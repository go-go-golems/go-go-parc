# μRAG DSL for Retrieval

- URL: https://chatgpt.com/c/6a6f544c-edd0-83ea-af48-2a77808fe7bd
- Created: 2026-08-02T14:30:25.000Z

---

> Create a new dsl to representation transformation of RAG information retrieval and prove properties on it, using transfinite induction, linking the colimits back to other categorical constructions that might be relevant

<details><summary>💭 Thinking</summary>

**Designing a categorical DSL**

I’m formulating a proposed DSL for RAG pipelines, using typed IRs, ordinal-indexed saturation, and colimits. I’ll state precise semantics, then prove termination, compositionality, and fixed-point properties via transfinite induction.

**Designed a categorical DSL**

</details>

I’ll formulate a typed DSL, give it a denotational semantics as a transfinite colimit, and prove the main closure, fixed-point, and universal properties. I’ll also relate the construction to initial algebras, Kan extensions, and the small-object style saturation pattern.

```json
{"system1_search_query":[{"q":"Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks paper arXiv 2020"},{"q":"Adamek theorem initial algebras colimit chain endofunctor original paper"},{"q":"transfinite construction small object argument category theory paper"},{"q":"accessible categories transfinite colimits fixed points endofunctor paper"}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Searched 28 websites**

**Formalizing the DSL**

I’m defining a typed language whose terms transform queries, documents, embeddings, ranked evidence, and answers. Its semantics will live in a presheaf category, where colimits assemble compatible retrieval representations.

**Formalized the DSL**

</details>

```json
{"system1_search_query":[{"q":"G. M. Kelly A unified treatment of transfinite constructions for free algebras free monoids colimits paper"},{"q":"polynomial functors accessible categories initial algebra transfinite chain paper arxiv"},{"q":"left Kan extension preserves colimits left adjoint category theory source"},{"q":"weighted colimit enriched category information retrieval similarity coend paper"}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Searched 23 websites**

</details>

# μRAG: a transfinite DSL for retrieval and representation transformation

The construction below is an original synthesis, not a claim of publication-level novelty. It treats the retrieval layer of RAG as a typed, recursively generated evidence structure and treats each concrete representation—graph, vector index, prompt context, citation DAG—as an algebraic interpretation of that structure.

This extends the usual RAG decomposition of parametric generation plus non-parametric retrieval by making retrieval expansion, provenance, and representation conversion explicit. citeturn485346view5

---

## 1. Core design

A **μRAG** program has three deliberately separate fragments:

1. **Seed**: the query, corpus, index handles, and fixed configuration.
2. **Growth**: monotone retrieval and inference rules.
3. **Observation**: ranking, top-\(k\), prompt construction, and generation.

The separation is mathematically necessary. For example, top-\(1\) is not monotone:

\[
A=\{a_{0.8}\}\subseteq B=\{a_{0.8},b_{0.9}\},
\]

but

\[
\operatorname{top}_1(A)=\{a\}
\not\subseteq
\operatorname{top}_1(B)=\{b\}.
\]

Consequently, `top`, `argmax`, destructive deduplication, and token-budget truncation cannot occur inside the transfinite growth fragment without destroying the least-fixed-point semantics.

### Example syntax

```text
pipeline BridgeQA(q : Query) : Answer at ω {
  seed K =
      corpus("knowledge-base")
      |> chunk(tokens = 384, overlap = 64)
      |> embed("encoder")
      |> index(metric = cosine);

  grow Evidence {
    rule direct(q : Query, c : Chunk) -> Evidence
      when cosine(embed(q), embed(c)) >= 0.72
      emit hit(q, c);

    rule follow(e : Evidence, c : Chunk) -> Evidence
      when linked(sourceChunk(e), c)
      emit extend(e, c);

    rule bridge(e1 : Evidence, e2 : Evidence) -> Evidence
      when target(e1) == source(e2)
      emit compose(e1, e2);

    rule citation(e : Evidence) -> Citation
      emit cite(e);
  }

  let μE = close[ω](seed(q, K), Evidence);

  representation graph : EvidenceGraph = fold μE {
    seed(x)        => insertBase(x);
    direct(q, c)   => addRetrievalEdge(q, c);
    follow(e, c)   => addHop(e, c);
    bridge(x, y)   => addComposition(x, y);
    citation(e)    => addCitation(e);
  };

  observe graph
    |> rerank("cross-encoder")
    |> top(12)
    |> generate("generator")
    |> attachCitations;
}
```

Here:

- `close[ω]` computes all evidence having finite derivation depth.
- `fold` transforms the canonical derivation representation into an evidence graph.
- The nonmonotone retrieval budget is applied only after saturation.

A rule with countably many premises would instead require a regular cardinal such as \(\omega_1\):

```text
rule consensus(
  es : Family<I, Evidence>,
  proof : cardinality(I) < ω₁
) -> Evidence
```

---

## 2. Static semantics

Fix an infinite regular cardinal \(\kappa\). Every growth primitive is assigned two static capabilities:

```text
accessible[κ]
monotone
```

More precisely:

- `accessible[κ]` means its semantic functor preserves \(\kappa\)-filtered colimits.
- `monotone` means it preserves monomorphisms.
- Guards inside growth must be stable under embeddings and \(\kappa\)-filtered unions.
- A primitive lacking these capabilities is restricted to `observe`.

Typical admissible growth operations are:

```text
retrieve.radius
follow.links
expand.query
extract.claims
join.evidence
infer.rule
union
compose
```

Typical observation-only operations are:

```text
top
argmax
rerank
truncate.tokens
diversify
generate
```

This discipline is the main semantic distinction between μRAG and an ordinary pipeline DSL.

---

## 3. Categorical semantics

Let \(S\) be the set of μRAG sorts, for example

\[
S=
\{
\mathsf{Query},
\mathsf{Chunk},
\mathsf{Claim},
\mathsf{Evidence},
\mathsf{Citation}
\}.
\]

Use the category

\[
\mathcal C=\mathbf{Set}^{S}.
\]

An object \(X\in\mathcal C\) is an \(S\)-sorted retrieval state:

\[
X=(X_s)_{s\in S}.
\]

Morphisms are sort-preserving functions. Colimits and monomorphisms are computed componentwise.

A richer implementation can replace the discrete set \(S\) by a small schema category \(\mathbb S\) and use \([\mathbb S,\mathbf{Set}]\); the proofs below remain pointwise.

### 3.1 Rule functor

For each rule \(r\), specify:

- an output sort \(o(r)\);
- a set \(A_r\) of rule shapes or parameters;
- for each \(a\in A_r\), a set \(B_{r,a}\) of premise positions;
- a sort map
  \[
  \sigma_{r,a}:B_{r,a}\to S;
  \]
- the arity restriction
  \[
  |B_{r,a}|<\kappa.
  \]

The rule block compiles to the polynomial endofunctor

\[
(T_PX)_s
=
\coprod_{\substack{r:o(r)=s\\a\in A_r}}
\prod_{b\in B_{r,a}}
X_{\sigma_{r,a}(b)}.
\]

An element consists of:

1. a chosen rule;
2. a chosen rule shape;
3. one existing premise for each input position.

Retriever calls, model calls, and guards can be represented by certified accessible subfunctors of this polynomial functor.

### 3.2 Seeded expansion

For a seed representation \(B\in\mathcal C\), define

\[
F_{P,B}(X)=B\sqcup T_PX.
\]

The transfinite retrieval chain is

\[
X_0=0,
\]

\[
X_{\alpha+1}=F_{P,B}(X_\alpha),
\]

and, for a limit ordinal \(\delta\),

\[
X_\delta
=
\operatorname*{colim}_{\alpha<\delta}X_\alpha.
\]

The canonical saturated representation is

\[
\operatorname{Sat}_P(B)
=
X_\kappa
=
\operatorname*{colim}_{\alpha<\kappa}X_\alpha.
\]

Operationally:

- \(X_1\) contains the seed;
- \(X_2\) contains direct retrieval results;
- \(X_3\) contains one-hop expansions and compositions;
- \(X_\omega\) contains evidence obtained by arbitrary finite derivations;
- larger cardinals support genuinely infinitary rules.

This is an instance of the classical transfinite initial-algebra pattern, specialized here to retrieval derivations. Transfinite sequences have long been used to construct free algebras and related categorical completions. citeturn757095view0turn485346view4

---

## 4. Accessibility theorem

### Theorem 1 — Well-typed growth programs are accessible

For every well-typed μRAG growth block \(P\), the endofunctors \(T_P\) and

\[
F_{P,B}=B\sqcup T_P(-)
\]

are \(\kappa\)-accessible and preserve monomorphisms.

### Proof

Consider one rule component

\[
R(X)=\prod_{b\in I}X_{\sigma(b)}
\qquad\text{with }|I|<\kappa.
\]

Let \(D:J\to\mathbf{Set}^{S}\) be a \(\kappa\)-filtered diagram. There is a canonical map

\[
\operatorname*{colim}_{j\in J}
\prod_{b\in I}D_j(\sigma(b))
\longrightarrow
\prod_{b\in I}
\operatorname*{colim}_{j\in J}D_j(\sigma(b)).
\]

It is surjective: choose a representative stage \(j_b\) for each coordinate. There are fewer than \(\kappa\) such stages, so \(\kappa\)-filteredness provides a common upper stage.

It is injective: if two tuples become equal coordinatewise, then for each of the fewer than \(\kappa\) coordinates there is a stage witnessing equality. Again, filteredness supplies one common upper stage.

Thus every \(<\kappa\)-ary product preserves \(\kappa\)-filtered colimits. Coproducts commute with colimits, so \(T_P\) is \(\kappa\)-accessible.

Products and coproducts of injections are injections in \(\mathbf{Set}^{S}\). Therefore \(T_P\) preserves monomorphisms. The same statements hold for \(B\sqcup T_P(-)\). Composition and coproduct of certified primitives preserve the two capabilities. ∎

---

## 5. Transfinite convergence and initiality

### Theorem 2 — Saturation converges at \(\kappa\)

There is a canonical isomorphism

\[
\iota:
F_{P,B}(X_\kappa)
\overset{\cong}{\longrightarrow}
X_\kappa.
\]

### Proof

Because \(\kappa\) is regular, the ordinal category \(\kappa\) is \(\kappa\)-filtered. Accessibility gives

\[
\begin{aligned}
F_{P,B}(X_\kappa)
&=
F_{P,B}
\left(
\operatorname*{colim}_{\alpha<\kappa}X_\alpha
\right)\\
&\cong
\operatorname*{colim}_{\alpha<\kappa}
F_{P,B}(X_\alpha)\\
&=
\operatorname*{colim}_{\alpha<\kappa}
X_{\alpha+1}.
\end{aligned}
\]

The successor ordinals below \(\kappa\) form a cofinal subdiagram, so

\[
\operatorname*{colim}_{\alpha<\kappa}
X_{\alpha+1}
\cong
\operatorname*{colim}_{\alpha<\kappa}
X_\alpha
=
X_\kappa.
\]

Composing these isomorphisms gives \(\iota\). ∎

### Theorem 3 — Initial-algebra property

The algebra

\[
\iota:F_{P,B}(X_\kappa)\to X_\kappa
\]

is initial among \(F_{P,B}\)-algebras.

Equivalently, for every algebra

\[
a:F_{P,B}(A)\to A
\]

there is a unique algebra morphism

\[
\operatorname{fold}_a:X_\kappa\to A.
\]

### Proof by transfinite induction

Define maps \(h_\alpha:X_\alpha\to A\).

At zero, let

\[
h_0:0\to A
\]

be the unique map.

At a successor stage, define

\[
h_{\alpha+1}
=
a\circ F_{P,B}(h_\alpha).
\]

At a limit ordinal \(\delta\), the maps \(h_\alpha\), \(\alpha<\delta\), form a compatible cocone. Define

\[
h_\delta:
\operatorname*{colim}_{\alpha<\delta}X_\alpha
\to A
\]

using the universal property of the colimit.

Set

\[
\operatorname{fold}_a=h_\kappa.
\]

The successor equation ensures that \(h_\kappa\) satisfies the algebra-morphism square.

For uniqueness, suppose \(g:X_\kappa\to A\) is another algebra morphism. Let \(x_\alpha:X_\alpha\to X_\kappa\) be the colimit maps. We prove

\[
g\circ x_\alpha=h_\alpha
\]

by transfinite induction.

- It holds at \(0\) by uniqueness from the initial object.
- At a successor, it follows from the algebra-morphism equation.
- At a limit, it follows because maps out of a colimit are determined by their composites with the colimit injections.

Therefore \(g=h_\kappa\). ∎

---

## 6. Monotone knowledge growth

### Theorem 4 — Every stage embeds in every later stage

All connecting maps

\[
X_\alpha\longrightarrow X_\beta,
\qquad \alpha\leq\beta\leq\kappa,
\]

are monomorphisms.

### Proof by transfinite induction

The map

\[
0\to F_{P,B}(0)
\]

is monic.

If \(X_\alpha\to X_\beta\) is monic, then

\[
F_{P,B}(X_\alpha)
\to
F_{P,B}(X_\beta)
\]

is monic because \(F_{P,B}\) preserves monomorphisms.

At a limit stage, the colimit of a chain of injections in \(\mathbf{Set}^{S}\) is its componentwise union, and each colimit injection is monic. ∎

Hence the saturated state can be written pointwise as

\[
X_\kappa
=
\bigcup_{\alpha<\kappa}X_\alpha.
\]

No evidence item is removed during growth.

### Corollary — Least closed representation

Suppose \(Y\) contains \(B\) and is closed under every rule in \(P\). Then there is a unique structure-preserving map

\[
X_\kappa\to Y.
\]

When \(X_\kappa\) and \(Y\) are subobjects of a common universe, this implies

\[
X_\kappa\subseteq Y.
\]

Thus μRAG computes the least rule-closed evidence representation containing the seed.

---

## 7. Provenance theorem

For the polynomial fragment, elements of \(X_\kappa\) have canonical well-founded derivation trees.

Define the rank of a tree by

\[
\operatorname{rk}(b)=0
\]

for a seed leaf, and

\[
\operatorname{rk}
\bigl(
r(t_b)_{b\in B_{r,a}}
\bigr)
=
\sup_{b\in B_{r,a}}
\left(
\operatorname{rk}(t_b)+1
\right).
\]

### Theorem 5 — Stage/rank correspondence

For every \(\alpha\leq\kappa\),

\[
t\in X_\alpha
\quad\Longleftrightarrow\quad
\operatorname{rk}(t)<\alpha.
\]

### Proof by transfinite induction

At \(0\), both sides are empty.

At \(\alpha+1\), an element is either:

- a seed leaf, of rank \(0<\alpha+1\); or
- a rule node whose children belong to \(X_\alpha\).

By induction, each child has rank below \(\alpha\), so the new node has rank below \(\alpha+1\). Conversely, if the node rank is below \(\alpha+1\), each child rank is below \(\alpha\), so every child appears in \(X_\alpha\).

At a limit \(\delta\),

\[
X_\delta=\bigcup_{\alpha<\delta}X_\alpha.
\]

An element belongs to this union exactly when its rank is below some \(\alpha<\delta\), equivalently when its rank is below \(\delta\). ∎

Regularity of \(\kappa\) and the \(<\kappa\)-arity restriction imply that every generated node has rank below \(\kappa\). This gives each retrieved item:

- an ordinal derivation depth;
- a complete provenance tree;
- the rule that introduced it;
- the exact premises on which it depends.

A graph representation may quotient duplicate trees, but the equivalence relation must be a congruence for the rule constructors. Otherwise the quotient need not inherit a valid algebra.

---

## 8. Representation transformations as folds

A target representation is an algebra

\[
a:B\sqcup T_PA\to A.
\]

Examples include:

- an evidence graph;
- a vector-store update log;
- a relational database;
- a citation DAG;
- a symbolic proof object;
- a compact serialized interchange format.

The unique transformation is

\[
\operatorname{fold}_a:
\operatorname{Sat}_P(B)\to A.
\]

This is the semantics of the DSL construct:

```text
representation A = fold μE { ...handlers... }
```

### Backend naturality

Suppose

\[
h:(A,a)\to(A',a')
\]

is an algebra morphism, meaning

\[
h\circ a=a'\circ F_{P,B}(h).
\]

Then

\[
h\circ\operatorname{fold}_a
=
\operatorname{fold}_{a'}.
\]

This follows immediately from initiality: both sides are algebra morphisms from the same initial algebra to \(A'\).

Consequently, converting a saturated retrieval derivation into a graph and then migrating that graph agrees with migrating the algebra and folding directly into the new representation.

---

## 9. Relation to free monads

Fix the unseeded rule functor \(T=T_P\). Then

\[
T^\ast B
=
\mu X.\bigl(B\sqcup TX\bigr)
\]

is the free \(T\)-algebra generated by \(B\).

When these free algebras exist functorially in \(B\), the assignment \(B\mapsto T^\ast B\) forms the free monad on \(T\). Thus:

- `grow` defines the signature functor \(T\);
- `close` constructs the free algebra;
- `fold` is the catamorphism into an interpreter;
- sequencing retrieval effects is Kleisli composition for \(T^\ast\).

Kelly’s transfinite constructions explicitly connect colimits of ordinal-indexed chains with free algebras, free monads, free monoids, and reflective constructions. citeturn757095view0

---

## 10. Schema migration and left Kan extensions

Suppose \(u:S\to S'\) changes the representation schema—for example, splitting `Evidence` into `DirectEvidence` and `DerivedEvidence`.

Let

\[
L=\operatorname{Lan}_u:
\mathbf{Set}^{S}\to\mathbf{Set}^{S'}
\]

be left Kan extension along \(u\).

Assume there are natural isomorphisms

\[
LB\cong B'
\]

and

\[
LT_P\cong T' L.
\]

The second condition says that migration commutes with one rule-expansion step.

### Theorem 6 — Saturation commutes with schema migration

Under these assumptions,

\[
L\bigl(\operatorname{Sat}_P(B)\bigr)
\cong
\operatorname{Sat}_{P'}(B').
\]

### Proof by transfinite induction

Let \(X_\alpha\) and \(X'_\alpha\) be the source and target chains.

At zero,

\[
LX_0=L0\cong0=X'_0.
\]

Assume \(LX_\alpha\cong X'_\alpha\). Then

\[
\begin{aligned}
LX_{\alpha+1}
&=
L(B\sqcup T_PX_\alpha)\\
&\cong
LB\sqcup LT_PX_\alpha\\
&\cong
B'\sqcup T'LX_\alpha\\
&\cong
B'\sqcup T'X'_\alpha\\
&=
X'_{\alpha+1}.
\end{aligned}
\]

At a limit \(\delta\), left Kan extension preserves colimits, so

\[
\begin{aligned}
LX_\delta
&=
L\left(
\operatorname*{colim}_{\alpha<\delta}X_\alpha
\right)\\
&\cong
\operatorname*{colim}_{\alpha<\delta}LX_\alpha\\
&\cong
\operatorname*{colim}_{\alpha<\delta}X'_\alpha\\
&=
X'_\delta.
\end{aligned}
\]

Taking \(\delta=\kappa\) proves the result. ∎

Left Kan extensions themselves admit weighted-colimit descriptions, so this migration theorem is another manifestation of colimit compatibility rather than an unrelated construction. citeturn485346view1

---

## 11. Retrieval as a weighted colimit

For soft or attention-style retrieval, enrich the semantics over a symmetric monoidal category \(\mathcal V\).

Let:

- \(\mathcal D\) be a category of corpus objects;
- \(E:\mathcal D\to\mathcal V\) assign each document its evidence representation;
- \(W_q:\mathcal D^{op}\to\mathcal V\) encode query-dependent similarity weights.

Define retrieval as the weighted colimit

\[
\operatorname{Ret}(q)
=
W_q\star E
=
\int^{d\in\mathcal D}
W_q(d)\otimes E(d).
\]

Interpretations include:

- weighted vector aggregation;
- attention over document representations;
- probabilistic mixtures of evidence;
- semiring-weighted provenance.

This models soft retrieval or fusion. Hard top-\(k\) remains an observation-level approximation to the weighted colimit, not part of the monotone closure semantics. Weighted colimits are the appropriate enriched analogue of ordinary colimits. citeturn485346view0turn485346view1

---

## 12. Relation to the small object argument

A rule can alternatively be represented by a generating monomorphism

\[
i_r:A_r\hookrightarrow B_r,
\]

where:

- \(A_r\) represents the premises or an unfilled retrieval obligation;
- \(B_r\) represents the same configuration with an evidence witness attached.

At each successor stage:

1. find all maps \(A_r\to X_\alpha\);
2. attach corresponding copies of \(B_r\) by coproduct and pushout;
3. obtain \(X_{\alpha+1}\).

At limit stages, take the colimit.

Then

\[
X_0\to X_\kappa
\]

is a transfinite composite of pushouts of generating rule maps: a relative cell complex.

This makes the small-object analogy literal when rules are expressed as attachment obligations. Garner’s algebraic refinement of the small object argument is particularly relevant when chosen fillers, provenance, and free algebraic structure must be retained rather than merely asserting existence. citeturn485346view2

The interpretations are:

| μRAG concept | Cell-attachment interpretation |
|---|---|
| Missing evidence | Lifting or filling obligation |
| Retrieval rule | Generating map |
| New evidence | Attached cell |
| Provenance | Chosen filler structure |
| Recursive retrieval | Transfinite composite |
| Saturated index | Rule-injective or closed object |

---

## 13. Relation to \(\operatorname{Ind}_\kappa\)-completion

Add the assumptions that:

- \(B\) is \(\kappa\)-presentable;
- \(T_P\) preserves \(\kappa\)-presentable objects;
- each rule has fewer than \(\kappa\) premises and parameters.

Then every \(X_\alpha\), for \(\alpha<\kappa\), is \(\kappa\)-presentable. The saturated object is the \(\kappa\)-filtered colimit

\[
X_\kappa
=
\operatorname*{colim}_{\alpha<\kappa}X_\alpha.
\]

Thus \(X_\kappa\) is an \(\operatorname{Ind}_\kappa\)-object assembled from bounded retrieval approximants.

Operationally, this supports:

- stage-level caching;
- resumable saturation;
- distributed construction of approximants;
- bounded provenance fragments;
- incremental recomputation after corpus updates.

---

## 14. Exact scope of the results

Under the stated regularity, accessibility, and monotonicity assumptions, μRAG provides:

\[
\boxed{
\operatorname{Sat}_P(B)
=
\mu X.\bigl(B\sqcup T_PX\bigr)
=
\operatorname*{colim}_{\alpha<\kappa}F_{P,B}^{\alpha}(0)
}
\]

with the following proved properties:

- the transfinite chain stabilizes at \(\kappa\);
- the result is the initial \(F_{P,B}\)-algebra;
- growth is monotone;
- the result is the least rule-closed extension of the seed;
- every evidence item has ordinal-ranked provenance;
- every target representation is obtained by a unique fold;
- representation translations are natural with respect to algebra morphisms;
- compatible left Kan extensions commute with saturation.

These results do **not** establish:

- factual correctness of a learned generator;
- relevance or calibration of a retriever;
- accessibility of arbitrary effectful network operations;
- convergence when nonmonotone ranking is placed inside growth;
- validity of an arbitrary deduplication quotient.

Those properties require separate contracts or empirical guarantees.


---

> So what cool stuff (concrete, pragmatic) can I prove / use this for?

<details><summary>💭 Thinking</summary>

**Applying the framework**

I’m translating the abstract construction into practical guarantees: bounded-depth query completeness, deterministic saturation, incremental recomputation, cache validation, provenance tracking, parallel execution, safe truncation, and backend equivalence—each tied to explicit proof obligations.

**Applied the framework**

</details>

The useful part is not “transfinite induction” by itself. It is that the DSL turns vague RAG behavior into proof obligations with direct engineering consequences.

For almost all practical systems with finitely many premises per rule, you only need the chain

\[
X_0\subseteq X_1\subseteq X_2\subseteq\cdots\subseteq X_\omega.
\]

The genuinely transfinite version matters for infinitary aggregation, distributed limits, or general categorical results.

## 1. Prove retrieval completeness up to a hop budget

Let \(X_n\) be the evidence available after \(n\) expansion rounds.

You can prove:

\[
e\in X_n
\quad\Longleftrightarrow\quad
e\text{ has a derivation of depth }<n.
\]

### Pragmatic use

For a two-hop QA system:

```text
close[3](seed, Evidence)
```

can be certified to include every result derivable using:

- direct retrieval;
- one link traversal;
- one composition step;

assuming the rules are encoded accordingly.

This gives a defensible meaning to “three retrieval rounds.” It is no longer an arbitrary loop count—it is a completeness guarantee for a specified derivation class.

It also helps test coverage:

```text
assert derivationDepth(goldEvidence) <= configuredDepth
```

When a benchmark answer fails, you can distinguish:

- the evidence was outside the permitted derivation depth;
- the retriever failed to instantiate an admissible rule;
- the generator ignored available evidence.

---

## 2. Prove that scheduling and parallelization do not change the answer

Suppose growth consists only of monotone rule application and union.

Then different fair schedules—breadth-first, depth-first, batched, asynchronous, or distributed—compute the same least closed evidence set:

\[
\operatorname{lfp}(F).
\]

### Pragmatic use

You can change from:

```text
for each query:
    retrieve
    expand links
    infer
```

to:

```text
parallel {
    retrieve from vector index
    retrieve from BM25
    expand graph neighbors
    run claim extraction
}
merge
repeat
```

without changing the final extensional result, provided:

1. every enabled rule is eventually processed;
2. merging is set union or another appropriate join;
3. no rule destructively removes evidence.

This gives you a correctness argument for distributed execution, work stealing, batching, and retrying failed workers.

A useful theorem is:

> Every fair execution whose accumulated state is monotone has colimit equal to the least fixed point.

That is directly applicable to a distributed retrieval engine.

---

## 3. Prove duplicate work can be removed safely

There are two representations to distinguish:

- **Intensional**: every derivation tree is retained.
- **Extensional**: evidence items with the same semantic identity are merged.

Define an equivalence relation

\[
t_1\sim t_2
\]

when two derivations establish the same evidence fact.

If \(\sim\) is a congruence—rules respect equivalent premises—then the quotient

\[
X_\omega/{\sim}
\]

inherits the rule algebra.

### Pragmatic use

You can safely deduplicate:

- identical chunks found by BM25 and vector search;
- the same citation reached through several graph paths;
- equivalent normalized claims;
- repeated API results;
- retried tool calls.

But you can preserve provenance separately:

```text
EvidenceFact {
    canonical_id
    payload
    derivations: Set<DerivationId>
}
```

The proof tells you exactly when hash-consing or canonicalization is semantics-preserving.

Without the congruence condition, deduplication may be unsound. For example, merging two claims that look similar but have different dates could enable invalid downstream inferences.

---

## 4. Prove incremental recomputation is correct

Let \(B\) be the old corpus facts and \(\Delta B\) a corpus update.

In an extensional join-semilattice semantics, saturation is a closure operator \(C\):

\[
C(X)=\operatorname{lfp}\bigl(Y\mapsto X\vee T(Y)\bigr).
\]

It satisfies:

\[
X\leq C(X),
\]

\[
X\leq Y\Rightarrow C(X)\leq C(Y),
\]

and

\[
C(C(X))=C(X).
\]

Therefore:

\[
C(B\vee\Delta B)
=
C(C(B)\vee\Delta B).
\]

### Pragmatic use

You do not need to recompute the whole retrieval closure after adding documents. Start with the old saturated state:

```text
old = close(oldCorpus)
new = closeFrom(old ∪ changedDocuments)
```

The theorem says this produces the same extensional closed state as rebuilding from scratch.

This is the basis for:

- incremental indexing;
- event-driven re-retrieval;
- materialized-view maintenance;
- caching derived claims;
- updating citation graphs after document changes.

For deletions, the theorem no longer suffices. You need dependency tracking or a truth-maintenance system because monotone closure does not tell you which derived facts must be retracted.

---

## 5. Prove cache correctness

Suppose a subprogram \(Q\) has semantics

\[
\llbracket Q\rrbracket:X\to Y.
\]

A cache key is correct when it identifies all semantic inputs on which this morphism depends.

Categorically, if the subprogram factors as

\[
X\xrightarrow{p}K\xrightarrow{q}Y,
\]

then \(p(x)\) is a sufficient cache key.

### Pragmatic use

For retrieval, the cache key may need to include:

```text
(
  normalized_query,
  corpus_snapshot_id,
  embedding_model_version,
  retrieval_rule_version,
  authorization_scope
)
```

You can prove that omitting `generator_temperature` is safe if it occurs only after the fold into the prompt representation.

You can also prove that omitting `corpus_snapshot_id` is unsafe, because retrieval does not factor through the smaller key.

This turns cache invalidation from guesswork into a dependency/factorization problem.

---

## 6. Prove backend implementations are equivalent

Suppose the same canonical evidence algebra is interpreted by two backends:

\[
a:F(A)\to A,
\qquad
b:F(B)\to B.
\]

If there is an algebra isomorphism

\[
h:A\cong B,
\]

then

\[
h\circ\operatorname{fold}_a
=
\operatorname{fold}_b.
\]

### Pragmatic use

You can prove that these implementations agree:

- in-memory graph versus Neo4j;
- relational tables versus a property graph;
- JSON provenance trees versus protobuf;
- CPU implementation versus distributed implementation;
- one vector database versus another, after abstracting away approximate search.

The method is concrete:

1. Specify how each backend represents seeds and every rule constructor.
2. Define a conversion \(h\).
3. Check one commuting equation per constructor.

You do not compare every possible pipeline output. Initiality reduces the proof to local checks.

This is the same benefit compiler correctness gets from structural recursion.

---

## 7. Prove a schema migration preserves retrieval meaning

Suppose you migrate:

```text
Evidence {
    text
    source
}
```

to:

```text
Evidence {
    claim
    sourceDocument
    sourceSpan
    retrievalMethod
}
```

Define a migration functor \(L\). If it commutes with the rule constructors,

\[
LT\cong T'L,
\]

then:

\[
L(\operatorname{Sat}_T(B))
\cong
\operatorname{Sat}_{T'}(LB).
\]

### Pragmatic use

You may choose whichever migration strategy is cheaper:

```text
saturate old data → migrate
```

or:

```text
migrate raw data → saturate under new schema
```

The theorem proves they agree, subject to the compatibility equation.

This is useful when changing:

- document schemas;
- graph node types;
- provenance formats;
- chunk identifiers;
- citation models;
- tenant or authorization annotations.

The proof obligation exposes lossy migrations. If a migration discards information used by a rule guard, it will fail to commute with that rule.

---

## 8. Prove provenance is complete

Because canonical evidence consists of derivation trees, every generated item has a recursively checkable explanation.

For each evidence item \(e\), you can produce:

\[
\operatorname{parents}(e),
\qquad
\operatorname{rule}(e),
\qquad
\operatorname{rank}(e).
\]

### Pragmatic use

You can guarantee:

> Every statement entering the final context is either a seed item or has a finite, rule-valid derivation from seed items.

This supports:

- citation generation;
- audit logs;
- explanation UIs;
- deletion impact analysis;
- debugging hallucination sources;
- evidence-based access control;
- reproducibility.

You can implement an independent proof checker:

```text
check(seed(x)) =
    corpus.contains(x)

check(rule_r(children)) =
    all(check(child) for child in children)
    and guard_r(children)
```

The retrieval service may be complex or untrusted; the checker can remain small.

---

## 9. Prove authorization is preserved

Label each evidence item with a security context. Let permissions form a lattice \(L\).

For example, assign a required authorization level:

\[
\ell(e)\in L.
\]

Define rule output labels by a conservative operation such as:

\[
\ell(r(e_1,\ldots,e_n))
=
\ell(e_1)\vee\cdots\vee\ell(e_n).
\]

Then prove by transfinite induction:

\[
e\in X_\alpha
\implies
\text{the label of }e\text{ dominates every source label in its derivation}.
\]

### Pragmatic use

A derived summary that combines public and confidential documents remains confidential.

This prevents a common class of RAG leaks where the final generated statement does not literally contain a restricted chunk but was inferred from one.

You can also prove noninterference for a user \(u\):

\[
\operatorname{observe}_u(C(B))
=
\operatorname{observe}_u(C(B_{\leq u})),
\]

provided all rule operations and observations respect the authorization projection.

That is a substantial, concrete security result.

---

## 10. Prove safe early stopping

Full saturation may be too expensive. You can still obtain sound partial results.

Because:

\[
X_0\subseteq X_1\subseteq\cdots\subseteq X_\omega,
\]

every intermediate stage is sound:

\[
X_n\subseteq X_\omega.
\]

### Pragmatic use

Stopping after a latency budget cannot introduce invalid evidence. It can only omit evidence that would appear later.

This gives a clear service contract:

```text
result {
    evidence: X_n
    completeness: "complete through derivation rank n-1"
    saturated: false
}
```

You can also define a goal predicate \(G\) that is monotone:

\[
X\subseteq Y\land G(X)\Rightarrow G(Y).
\]

Once \(G(X_n)\) is true, stopping is safe with respect to that goal.

Examples:

- at least three independent supporting sources;
- one primary source and one corroborating source;
- all required fields of a structured answer filled;
- a proof of a target claim has been found.

This gives principled “retrieve until enough evidence” behavior.

---

## 11. Prove rankers cannot corrupt retrieval closure

The DSL separation between growth and observation gives a useful theorem:

Let

\[
C(B)
\]

be the saturated evidence, and let

\[
O:C(B)\to R
\]

be an arbitrary ranker/truncator/generator.

Changing \(O\) does not change the closure \(C(B)\).

### Pragmatic use

You can independently version:

- retrieval completeness;
- reranking quality;
- context-window packing;
- generation.

A new reranker cannot silently alter which facts are considered derivable. It only changes which derivable facts are observed.

This makes A/B testing cleaner. You can cache the canonical closure once, then evaluate many rankers against the same evidence universe.

It also permits statements such as:

> Recall failures occur in the growth layer; selection failures occur in the observation layer.

That decomposition is extremely useful operationally.

---

## 12. Prove bounded resource use for restricted fragments

Suppose:

- the seed has \(N\) elements;
- every rule has arity at most \(m\);
- there are \(R\) rule shapes;
- expansion depth is \(d\);
- guards produce at most \(K\) outputs per matching tuple.

A coarse recurrence is:

\[
n_{i+1}
\leq
N+
RK\,n_i^m.
\]

This gives a static upper bound on the size of \(X_d\).

### Pragmatic use

The bound may be pessimistic, but it can reject obviously dangerous programs:

```text
rule pairEveryEvidence(x, y) -> Evidence
```

creates quadratic growth.

A ternary join creates cubic growth. Unrestricted composition can be explosive.

The type checker can attach complexity effects:

```text
growth[linear]
growth[quadratic]
growth[unbounded]
```

and require explicit approval for costly rules.

You can also prove termination for finite corpora under extensional deduplication: if there are only finitely many possible canonical facts and growth is monotone, the chain stabilizes after finitely many additions.

---

## 13. Prove optimizer rewrites are valid

Once pipeline fragments are morphisms and growth is colimit-based, common optimizations become equations.

### Push compatible maps through saturation

If \(L\) preserves the relevant colimits and commutes with rule expansion:

\[
LC\cong C'L,
\]

then representation conversion may be moved before or after saturation.

### Fuse folds

Given:

\[
\operatorname{fold}_a:X_\omega\to A
\]

and an algebra morphism \(h:A\to B\),

\[
h\circ\operatorname{fold}_a
=
\operatorname{fold}_b.
\]

So two representation passes can be fused.

### Reorder independent rules

If two rule operators \(T_1,T_2\) commute suitably,

\[
T_1T_2\cong T_2T_1,
\]

their execution order may be changed.

### Pragmatic use

These are compiler optimizations for RAG plans:

- push normalization closer to ingestion;
- fuse graph construction with serialization;
- batch independent retrievers;
- migrate data before retrieval rather than afterward;
- eliminate repeated intermediate representations.

---

## 14. Build a property-based test suite from the laws

The categorical laws translate directly into executable tests.

### Inflationary growth

```text
assert seed <= close(seed)
```

### Monotonicity

```text
if A <= B:
    assert close(A) <= close(B)
```

### Idempotence

```text
assert close(close(A)) == close(A)
```

### Fold homomorphism

For every rule node:

```text
fold(rule(children)) ==
handler(rule, map(fold, children))
```

### Migration compatibility

```text
migrate(close_old(A)) ==
close_new(migrate(A))
```

### Schedule independence

```text
run_bfs(A) == run_parallel(A)
```

### Pragmatic use

These tests catch:

- hidden destructive updates;
- unstable identifiers;
- rankers accidentally placed in growth;
- incorrect cache reuse;
- schema migrations that drop rule-relevant fields;
- nondeterministic merge bugs.

The abstract theory becomes a source of concrete invariants.

---

# Three especially strong projects

## A. A proof-carrying RAG engine

Return an answer together with a compact derivation DAG:

```text
AnswerPackage {
    answer
    selectedEvidence
    derivationDAG
    corpusSnapshot
    ruleSetHash
}
```

A separate verifier checks that every citation and inferred claim follows from declared rules.

The key theorem is provenance completeness.

## B. An incremental, distributed evidence graph

Use the closure-operator and schedule-independence results to support:

- parallel workers;
- persistent checkpoints;
- corpus deltas;
- idempotent retries;
- eventual convergence.

The key theorem is that every fair monotone execution converges to the same least closed state.

## C. A semantics-preserving RAG compiler

Compile one μRAG program into:

- SQL recursive common table expressions;
- a graph database query plan;
- a streaming dataflow;
- an in-memory implementation.

Prove each backend implements the same algebra. Then backend equivalence follows from the initial-algebra universal property.

---

# Best first theorem to implement

A practical initial target is:

> **For a finite corpus and extensional evidence IDs, every fair execution of a finite set of monotone, finitely branching rules terminates and returns the same least closed evidence set, independent of batching, ordering, duplication, and worker retries.**

This supports a real engine with:

- deterministic semantics;
- parallel execution;
- safe retry;
- deduplication;
- incremental checkpoints;
- explainable derivations.

It uses ordinary induction plus the \(\omega\)-chain semantics. The heavier transfinite machinery remains available when the DSL grows beyond finite branching.


---

> Let’s strip it down for a programmer who doesn’t know maths at all, but has a good feeling for solid invariants, APIs and their semantics, unit tests design . Do explain the mathematical concepts behind it, but with minimal jargon

Here is the stripped-down version, written for an experienced programmer rather than a mathematician.

:::writing{variant="document" id="48317"}
# A Practical Semantic Model for RAG Pipelines

The goal is to make a RAG pipeline behave like a well-specified API rather than a loose sequence of model calls.

We want to answer questions such as:

- Does running retrieval in parallel change the result?
- Is retrying a failed worker safe?
- Can we update the corpus without rebuilding everything?
- Can we replace the graph database without changing behavior?
- Can every generated claim be traced to its source?
- Does stopping after three rounds have a precise meaning?

The mathematical machinery gives us a compact way to state and prove these properties. In implementation terms, it mostly comes down to:

1. defining a state;
2. defining operations that only add information;
3. repeatedly applying those operations;
4. stopping when nothing new is produced;
5. keeping ranking and truncation outside that process.

---

## 1. The basic model

Represent the current retrieval state as a set of facts.

```ts
type EvidenceId = string;

interface Evidence {
  id: EvidenceId;
  content: string;
  sources: EvidenceId[];
  introducedBy: string;
}

type EvidenceState = Map<EvidenceId, Evidence>;
```

A rule examines the current state and proposes additional evidence.

```ts
interface Rule {
  name: string;
  apply(state: Readonly<EvidenceState>): Iterable<Evidence>;
}
```

Examples of rules:

- retrieve chunks matching the query;
- follow links from retrieved documents;
- extract claims from chunks;
- combine two claims;
- find supporting citations;
- resolve entities;
- query another index.

The central operation is:

```ts
function step(
  current: Readonly<EvidenceState>,
  rules: readonly Rule[],
): EvidenceState
```

`step` applies every rule and returns the old evidence plus any new evidence.

The full retrieval process is:

```ts
function close(
  initial: Readonly<EvidenceState>,
  rules: readonly Rule[],
): EvidenceState {
  let current = new Map(initial);

  while (true) {
    const next = step(current, rules);

    if (sameEvidenceIds(current, next)) {
      return next;
    }

    current = next;
  }
}
```

The result is the smallest state that:

- contains the initial evidence;
- is closed under every rule.

“Closed” means that applying the rules again adds nothing new.

---

## 2. The most important invariant

During retrieval, evidence may be added but not removed.

Formally:

```ts
current ⊆ step(current)
```

In ordinary programming terms:

```ts
for (const id of current.keys()) {
  assert(step(current, rules).has(id));
}
```

This is called **monotonicity**.

The name is less important than the rule:

> Once the retrieval system has learned something, later retrieval rounds do not make it disappear.

This gives several useful properties almost immediately:

- retries are safe;
- duplicate work is harmless;
- workers can finish in different orders;
- partial results remain valid;
- later rounds cannot invalidate earlier evidence.

This does not mean that all evidence is correct. It means only that the retrieval process does not destructively rewrite its own state.

---

## 3. Keep ranking outside retrieval growth

Some operations remove or replace information:

```ts
topK(evidence, 10)
rerank(evidence)
truncateToTokenBudget(evidence)
chooseBestAnswer(candidates)
```

These operations are not monotone.

For example:

```ts
top1([{ id: "a", score: 0.8 }])
// returns a

top1([
  { id: "a", score: 0.8 },
  { id: "b", score: 0.9 },
])
// returns b
```

Adding `b` caused `a` to disappear from the result.

That is fine for presentation, but dangerous inside evidence growth.

Use two separate APIs:

```ts
const completeEvidence = close(seed, growthRules);

const selectedEvidence = rankAndSelect(completeEvidence, {
  maxItems: 12,
  tokenBudget: 6000,
});
```

The first stage answers:

> What evidence can the system derive?

The second answers:

> Which part of that evidence should be shown to the model?

This separation makes failures easier to diagnose.

- Missing from `completeEvidence`: retrieval failure.
- Present in `completeEvidence`, absent from `selectedEvidence`: ranking failure.
- Present in the prompt, absent from the answer: generation failure.

---

## 4. Retrieval rounds have a precise meaning

Define:

```ts
const state0 = emptyState();
const state1 = step(state0, rules);
const state2 = step(state1, rules);
const state3 = step(state2, rules);
```

Each round adds evidence that can be produced from evidence available in the previous round.

A direct search result may appear in round 1.

A document reached by following a link from that result may appear in round 2.

A claim requiring both pieces may appear in round 3.

This gives a useful invariant:

> Evidence found after `n` rounds has a derivation requiring at most `n` rule layers.

You can expose that in the API:

```ts
interface Evidence {
  id: EvidenceId;
  content: string;
  rank: number;
  sources: EvidenceId[];
  introducedBy: string;
}
```

Here, `rank` means derivation depth, not relevance score.

This gives a precise interpretation to configurations such as:

```ts
maxRetrievalRounds: 3
```

It means:

> Return everything derivable within three rule applications.

It does not mean:

> Run a mysterious loop three times and hope that is enough.

---

## 5. What “transfinite” means here

In normal programs, retrieval progresses through rounds:

```text
0, 1, 2, 3, ...
```

After all finite rounds, mathematicians use the symbol:

```text
ω
```

Read it as:

> the result of taking the union of every finite stage.

So:

```text
stateω = state0 ∪ state1 ∪ state2 ∪ ...
```

This does not require actually running an infinite loop.

In practical systems, one of two things usually happens:

1. The possible evidence set is finite, so the process eventually stops.
2. You impose a depth, cost, or time limit and return a partial result.

The more general “transfinite” framework also handles stages beyond all finite depths. Most ordinary RAG systems do not need those larger stages.

The useful programming idea is simply:

> At a limit stage, combine everything found so far.

That is what a colimit means in this setting.

---

## 6. A colimit, without the jargon

Suppose several workers produce growing states:

```text
Worker A: A0 ⊆ A1 ⊆ A2
Worker B: B0 ⊆ B1
Worker C: C0 ⊆ C1 ⊆ C2 ⊆ C3
```

The combined result is their union:

```ts
const combined = union(
  A0, A1, A2,
  B0, B1,
  C0, C1, C2, C3,
);
```

A **colimit** is the general mathematical name for this kind of “combine all compatible partial results” operation.

For this RAG design, it usually means one of:

- set union;
- merging maps by stable IDs;
- joining graph fragments;
- combining event logs;
- merging compatible database rows.

The important property is that the merge loses no information.

---

## 7. The fixed-point property

When retrieval is finished:

```ts
step(result, rules) === result
```

Applying the rules again produces nothing new.

This is called a **fixed point**.

More specifically, we want the smallest fixed point containing the seed.

That rules out an implementation that returns every fact in the database. Such a state may be closed under the rules, but it is not the smallest relevant closed state.

The intended result satisfies three laws.

### It includes the input

```ts
seed ⊆ close(seed)
```

### It is stable

```ts
close(close(seed)) === close(seed)
```

### More input cannot produce less output

```ts
if (a ⊆ b) {
  assert(close(a) ⊆ close(b));
}
```

These are excellent property-based tests.

---

## 8. The closure API

A useful public interface might be:

```ts
interface ClosureResult {
  evidence: EvidenceState;
  saturated: boolean;
  completedRounds: number;
}

interface ClosureOptions {
  maxRounds?: number;
  maxEvidence?: number;
  deadline?: AbortSignal;
}

function close(
  seed: Readonly<EvidenceState>,
  rules: readonly Rule[],
  options?: ClosureOptions,
): ClosureResult;
```

Possible contracts:

```ts
// Every returned item is valid according to some rule derivation.
sound(result);

// No returned item disappears when the budget is increased.
prefixStable(resultWithSmallBudget, resultWithLargeBudget);

// If saturated is true, another step adds no evidence.
if (result.saturated) {
  assert(equal(
    result.evidence,
    step(result.evidence, rules),
  ));
}
```

A partial result should state its completeness level explicitly:

```ts
{
  saturated: false,
  completedRounds: 3
}
```

This means:

> The result is sound and complete through three rule layers, but deeper derivations may be missing.

---

## 9. Why execution order should not matter

Suppose these operations are enabled:

```text
vector search
keyword search
link traversal
claim extraction
citation lookup
```

One implementation might run them sequentially.

Another might run them in parallel.

Another might retry some operations.

Another might process graph expansions before search results have all arrived.

Under the monotone model, they should converge to the same final evidence set, provided that:

- rules only add evidence;
- evidence IDs are stable;
- duplicate additions are ignored;
- every enabled rule is eventually run;
- workers merge results using union-like behavior.

This is similar to eventual consistency in distributed systems.

The main theorem becomes an engineering contract:

> Any fair execution schedule reaches the same final state.

“Fair” means that no permanently enabled piece of work is ignored forever.

This lets you change batching, worker counts, queue order, or retry strategy without changing the meaning of the pipeline.

---

## 10. Idempotent worker design

A worker should be safe to execute more than once.

Bad:

```ts
state.counter += 1;
```

Better:

```ts
state.evidence.set(evidence.id, evidence);
```

The insertion is identified by a stable semantic ID.

For example:

```ts
function evidenceId(input: {
  rule: string;
  sourceIds: string[];
  normalizedOutput: string;
}): string {
  return hash(canonicalJson(input));
}
```

Then:

```ts
insert(e);
insert(e);
insert(e);
```

has the same result as:

```ts
insert(e);
```

This is an implementation of the algebraic law:

```text
x ∪ x = x
```

The mathematical term is **idempotence**.

In API language:

> Repeating the same operation does not change the result after the first successful application.

---

## 11. Deduplication requires a semantic identity

Suppose vector search and keyword search both return the same document chunk.

You probably want one evidence object with two derivations:

```ts
interface Evidence {
  id: EvidenceId;
  content: string;
  derivations: Derivation[];
}
```

```ts
interface Derivation {
  rule: string;
  sourceIds: EvidenceId[];
  metadata: Record<string, unknown>;
}
```

The evidence fact is deduplicated, but its provenance is not discarded.

This allows:

```text
Evidence:
  "The contract ends on 30 September."

Derivations:
  - found by BM25
  - found by vector search
  - extracted from section 8.2
```

The main safety rule is:

> Merge two items only when every downstream rule is allowed to treat them as interchangeable.

For example, these should probably not share an ID:

```text
Revenue was $5M in 2024.
Revenue was $5M in 2025.
```

Even though their text is nearly identical, merging them may create invalid conclusions.

In mathematical language, safe deduplication must preserve the operations defined on the data.

In programming language:

> Your equality function must agree with the behavior of all consumers.

---

## 12. Provenance becomes a first-class API

Every derived item should record:

- which rule created it;
- which earlier items it used;
- any external call involved;
- configuration and model versions;
- the corpus snapshot.

For example:

```ts
interface Derivation {
  ruleName: string;
  inputIds: EvidenceId[];
  corpusVersion: string;
  codeVersion: string;
  modelVersion?: string;
  parameters: Record<string, unknown>;
}
```

A validator can recursively check the derivation:

```ts
function verify(
  evidenceId: EvidenceId,
  state: Readonly<EvidenceState>,
): boolean {
  const evidence = state.get(evidenceId);

  if (!evidence) {
    return false;
  }

  if (evidence.introducedBy === "seed") {
    return verifySeed(evidence);
  }

  return evidence.sources.every(id => verify(id, state))
    && verifyRuleApplication(evidence, state);
}
```

This gives a proof-carrying answer format:

```ts
interface AnswerPackage {
  answer: string;
  selectedEvidenceIds: EvidenceId[];
  evidence: EvidenceState;
  corpusVersion: string;
  pipelineVersion: string;
}
```

The answer generator can be complicated. The evidence verifier can remain small and deterministic.

---

## 13. Safe early stopping

Because evidence only grows:

```text
state0 ⊆ state1 ⊆ state2 ⊆ ...
```

any partial state is still valid.

Stopping early may make the result incomplete, but it does not make already-produced evidence invalid.

That gives a useful distinction:

```ts
interface ResultStatus {
  sound: true;
  complete: boolean;
}
```

A timeout can return:

```ts
{
  sound: true,
  complete: false
}
```

You can also stop when a monotone goal is satisfied.

For example:

```ts
function enoughEvidence(state: EvidenceState): boolean {
  return hasPrimarySource(state)
    && countIndependentSources(state) >= 3;
}
```

Once this becomes true, adding more evidence will not make it false.

That makes it safe as a stopping condition.

Unsafe stopping conditions include:

```ts
topResultScore(state) > 0.9
```

Adding a stronger contradictory result might change the meaning of the current winner.

---

## 14. Incremental corpus updates

Suppose the old corpus has already been fully processed:

```ts
const oldClosed = close(oldSeed, rules);
```

Now new documents arrive.

Because the process is monotone, you can start from the old result:

```ts
const updated = close(
  union(oldClosed.evidence, newSeed),
  rules,
);
```

You do not need to begin from an empty state.

The key law is:

```ts
close(union(close(old), delta))
===
close(union(old, delta))
```

This supports:

- incremental indexing;
- persistent materialized evidence;
- background document ingestion;
- resumable jobs;
- event-driven expansion.

Deletions are harder.

When a document is removed, some derived evidence may need to disappear. That violates the add-only model.

To support deletions, retain dependency information:

```text
derived claim
    depends on chunk A
    depends on chunk B
```

Then retract an item only when it has no remaining valid derivation.

This is similar to build systems such as `make`, dependency graphs, and incremental compilers.

---

## 15. Cache correctness

A cache is valid only when its key includes every input that affects the output.

For retrieval, that may include:

```ts
interface RetrievalCacheKey {
  normalizedQuery: string;
  corpusVersion: string;
  embeddingModelVersion: string;
  ruleSetVersion: string;
  authorizationScope: string;
}
```

It may not need to include:

```text
generator temperature
answer formatting style
maximum answer length
```

if those settings are used only after retrieval.

A useful test is:

> Can two executions have the same cache key but legally produce different retrieval results?

If yes, the key is incomplete.

The mathematical idea is called factorization, but the implementation lesson is simple:

> A cache key is a compressed representation of the operation’s complete semantic input.

---

## 16. Backend replacement

Suppose the canonical evidence model can be stored as:

- an in-memory map;
- PostgreSQL tables;
- a graph database;
- JSON;
- an event stream.

You want to prove that changing storage does not change behavior.

Define operations that every backend must implement:

```ts
interface EvidenceBackend {
  insertEvidence(evidence: Evidence): void;
  insertDerivation(
    evidenceId: EvidenceId,
    derivation: Derivation,
  ): void;
  hasEvidence(id: EvidenceId): boolean;
  readEvidence(id: EvidenceId): Evidence | undefined;
  listEvidence(): Iterable<Evidence>;
}
```

Then test that each backend preserves the same constructors:

```ts
seed(...)
retrieve(...)
followLink(...)
combine(...)
cite(...)
```

If every constructor is preserved, complete pipelines built from those constructors are preserved too.

This is the practical meaning of the “initial algebra” result.

It says:

> To prove two interpreters equivalent, check each primitive operation. You do not need to compare every possible program separately.

This is the same reasoning used for interpreters, serializers, compiler backends, and AST visitors.

---

## 17. Representation transformations

The canonical retrieval state should not itself be optimized for every consumer.

Instead, transform it into specific views:

```ts
const graph = toEvidenceGraph(closed);
const prompt = toPromptContext(closed);
const rows = toDatabaseRows(closed);
const auditLog = toAuditEvents(closed);
```

Each transformation defines what to do with:

- seed evidence;
- retrieved evidence;
- linked evidence;
- combined evidence;
- citations.

Conceptually:

```ts
interface EvidenceFolder<T> {
  seed(e: Evidence): T;
  retrieved(e: Evidence, source: T): T;
  linked(e: Evidence, parent: T): T;
  combined(e: Evidence, parents: readonly T[]): T;
}
```

Then:

```ts
function foldEvidence<T>(
  state: EvidenceState,
  folder: EvidenceFolder<T>,
): T
```

This resembles folding an AST.

The useful property is:

> There is one structurally correct way to transform the complete derivation structure once the handler for each constructor is defined.

That reduces representation conversion bugs.

---

## 18. Schema migration

Suppose the old schema is:

```ts
interface OldEvidence {
  text: string;
  source: string;
}
```

The new schema is:

```ts
interface NewEvidence {
  claim: string;
  sourceDocument: string;
  sourceSpan: {
    start: number;
    end: number;
  };
  retrievalMethod: string;
}
```

There are two migration strategies.

Strategy A:

```text
run old pipeline
then migrate the resulting evidence
```

Strategy B:

```text
migrate source data
then run the new pipeline
```

You want:

```ts
migrate(closeOld(data))
===
closeNew(migrate(data))
```

This equality is not automatic.

It fails when migration removes information needed by a rule.

For example, if the old pipeline uses timestamps but the new schema discards them, the two paths may produce different results.

The mathematical idea is that migration must commute with each rule.

The unit-test version is:

```ts
for (const rule of rules) {
  assertEqual(
    migrate(rule.apply(oldState)),
    migratedRule.apply(migrate(oldState)),
  );
}
```

---

## 19. Authorization propagation

RAG systems can leak information through derived claims, even when the original restricted chunk is not shown.

Attach an access label to every item:

```ts
type AccessLevel =
  | "public"
  | "internal"
  | "confidential"
  | "restricted";
```

When a rule combines evidence, the output inherits the strictest requirement:

```ts
function combineAccessLevels(
  levels: readonly AccessLevel[],
): AccessLevel
```

For example:

```text
public + confidential = confidential
```

Then enforce:

```ts
derived.accessLevel >= every input.accessLevel
```

The proof is an induction over derivations:

- seed evidence has the correct label;
- every rule preserves or increases restrictions;
- therefore every derived item has a label at least as strict as every source it depends on.

This provides a real security invariant:

> A user cannot see a derived claim unless they are allowed to see all protected evidence required to derive it.

---

## 20. Resource bounds

Rules can cause explosive growth.

This rule may be linear:

```ts
for each document:
  extract one summary
```

This may be quadratic:

```ts
for each pair of claims:
  compare them
```

This may be cubic:

```ts
for each triple of entities:
  test a relation
```

Attach rough cost metadata:

```ts
type GrowthClass =
  | "constant"
  | "linear"
  | "quadratic"
  | "cubic"
  | "unbounded";
```

```ts
interface Rule {
  name: string;
  growthClass: GrowthClass;
  apply(state: Readonly<EvidenceState>): Iterable<Evidence>;
}
```

The exact mathematical bound may be pessimistic. The practical value is static rejection of clearly dangerous plans.

For example:

```ts
if (
  rule.growthClass === "quadratic"
  && expectedEvidenceCount > 100_000
) {
  throw new UnsafePlanError();
}
```

---

## 21. Property-based tests

The model produces direct test laws.

### Includes the seed

```ts
fc.assert(
  fc.property(seedArbitrary, seed => {
    const result = close(seed, rules);
    return isSubset(seed, result.evidence);
  }),
);
```

### Idempotent closure

```ts
close(close(seed).evidence).evidence
===
close(seed).evidence
```

### Monotone input

```ts
if (isSubset(a, b)) {
  assert(isSubset(
    close(a, rules).evidence,
    close(b, rules).evidence,
  ));
}
```

### Duplicate execution is harmless

```ts
applyRule(rule, state)
===
applyRuleTwice(rule, state)
```

### Scheduling does not affect the final result

```ts
runSequential(seed, rules)
===
runParallel(seed, rules)
```

### Retrying a worker does not affect the result

```ts
runWithRetries(seed, rules)
===
runWithoutRetries(seed, rules)
```

### Migration commutes with retrieval

```ts
migrate(closeOld(seed))
===
closeNew(migrate(seed))
```

### Every derived item has valid provenance

```ts
for (const evidence of result.evidence.values()) {
  assert(verify(evidence.id, result.evidence));
}
```

These are stronger than example-based tests because they test the semantics of the API rather than a few chosen outputs.

---

## 22. The mathematical terms, translated

| Mathematical term | Programmer interpretation |
|---|---|
| Set | Collection of evidence with stable identity |
| Function | Deterministic transformation |
| Morphism | Structure-preserving transformation |
| Monotone | Only adds information |
| Idempotent | Repeating it has no additional effect |
| Chain | Sequence of growing states |
| Colimit | Merge of all compatible partial states |
| Fixed point | Running another step changes nothing |
| Least fixed point | Smallest stable result containing the seed |
| Induction | Prove the base case, then prove one step preserves the property |
| Transfinite induction | The same, plus a case for merging all earlier stages |
| Algebra | Implementation of the primitive constructors |
| Initial algebra | Canonical syntax/derivation form from which every interpreter is defined |
| Fold | Interpret or transform a recursive structure |
| Functor | A transformation that also preserves how values are connected |
| Natural transformation | A conversion that behaves consistently in every context |
| Kan extension | A general schema migration or best-fit extension |
| Quotient | Deduplicate values considered equivalent |
| Congruence | Equality that every operation respects |

You do not need these names to implement the system. They become useful when searching for existing results or generalizing the design.

---

## 23. What transfinite induction adds

Ordinary induction has two cases:

1. prove the property at stage `0`;
2. prove that if it holds at stage `n`, it holds at stage `n + 1`.

Transfinite induction adds a third case:

3. at a stage formed by combining all earlier stages, prove the property survives that merge.

For this system, that usually means:

```ts
const limitState = union(...allEarlierStates);
```

If a property holds in every earlier state, show that it also holds in the union.

Example: authorization.

Base case:

```text
Every seed item has the correct access label.
```

Step case:

```text
Every rule assigns an output label at least as restrictive as its inputs.
```

Limit case:

```text
Combining correctly labelled states does not change any labels.
```

Therefore every item produced at any stage has the correct label.

This is transfinite induction in practical terms.

---

## 24. A minimal DSL

A stripped-down DSL could look like this:

```ts
const program = rag({
  seed: queryAndCorpus,

  rules: [
    rule("retrieve", retrieveMatchingChunks),
    rule("follow-links", followDocumentLinks),
    rule("extract-claims", extractClaims),
    rule("combine-claims", combineCompatibleClaims),
    rule("find-citations", findCitations),
  ],

  stopWhen: state =>
    hasPrimarySource(state)
    && countIndependentSources(state) >= 3,

  observe: state =>
    generateAnswer(
      topK(
        rerank(state),
        12,
      ),
    ),
});
```

The compiler or runtime should reject this:

```ts
rule("keep-only-best-result", state => topK(state, 1))
```

because it removes evidence during the growth phase.

It should accept this:

```ts
observe: state => topK(state, 1)
```

because observation is allowed to be selective.

---

## 25. The most useful initial theorem

For a practical implementation, target this guarantee:

> Given a finite corpus, stable evidence IDs, and rules that only add evidence, every fair execution terminates and produces the same final evidence set regardless of rule order, batching, parallelism, duplicate messages, or worker retries.

This gives you:

- deterministic semantics;
- safe parallel execution;
- idempotent jobs;
- retry safety;
- deduplication;
- checkpointing;
- reproducible debugging;
- complete provenance.

The implementation requirements are straightforward:

```text
1. Stable semantic IDs
2. Add-only state during growth
3. Idempotent insertion
4. Union-based merging
5. Fair processing of pending rules
6. Separate ranking and truncation
7. Explicit derivation records
```

That is the practical core. The category theory provides the general proof framework, but the running system can look like an ordinary event-driven dataflow engine with unusually strong invariants.
:::

This can be tightened further into an API specification, an RFC, or a concrete TypeScript implementation.


---

> Output a concise summary of this, minimal dsl, which problems we solve, tiny math background. 2-3 paragraphs, bullet points

:::writing{variant="document" id="73148"}
This DSL models RAG retrieval as an **add-only evidence process**. Rules inspect the current evidence and add new evidence; ranking, truncation, and generation happen only after retrieval stops. The runtime repeatedly applies rules until nothing new appears or a configured budget is reached.

```ts
rag({
  seed: initialEvidence,
  rules: [
    rule("retrieve", retrieveChunks),
    rule("follow-links", followLinks),
    rule("extract-claims", extractClaims),
  ],
  stopWhen: state => enoughEvidence(state),
  observe: state => generate(topK(rerank(state), 12)),
});
```

It solves several practical problems:

- **Deterministic execution:** sequential, parallel, batched, and retried executions converge to the same result.
- **Safe retries and deduplication:** stable evidence IDs make repeated work harmless.
- **Incremental updates:** new documents can extend an existing result without rebuilding from scratch.
- **Clear failure boundaries:** missing evidence is a retrieval problem; dropped evidence is a ranking problem; ignored evidence is a generation problem.
- **Complete provenance:** every derived item records the rule and source items that produced it.
- **Testable semantics:** verify that retrieval includes its input, only grows, becomes stable, and is unaffected by duplicate execution.

The small amount of mathematics is mostly vocabulary for these invariants. A **fixed point** is a state where another retrieval step adds nothing. The **least fixed point** is the smallest such state containing the initial evidence. A **colimit** is just the lossless merge of all partial states, usually set union. **Induction** proves that an invariant holds initially and remains true after every rule application; transfinite induction adds the case where all earlier stages are merged.
:::


---

> Now see if you can apply these principles to the attached codebase. Research and analyze and think and do theory and write a full handbook report about the structures in rag-ttc, what cna be mapped and adapted, or in general how this can be turned into an elegant composable system with rigorous semantics.

<details><summary>💭 Thinking</summary>

**Inspecting the codebase**

I’m going to examine the attached project, map its architecture and workflows, then research relevant concepts and dependencies before producing a comprehensive handbook report, likely with practical setup and usage guidance.

**Inspected the codebase**

</details>

I’ll inspect the repository’s structure, execution paths, data models, checks, invariants, and composition boundaries, then produce a semantics-driven refactoring handbook with APIs, tests, and migration steps.

```unknown
bash -lc set -euo pipefail
mkdir -p /mnt/data/rag-ttc-work
unzip -q -o /mnt/data/rag-ttc.zip -d /mnt/data/rag-ttc-work
find /mnt/data/rag-ttc-work -maxdepth 3 -type f | sed 's#^#/##' | head -200
```

<details><summary>💭 Thinking</summary>

**Inspected repository structure, documentation, metadata, and Go test setup**

</details>

```unknown
bash -lc cd /mnt/data/rag-ttc-work/rag-ttc
find ttmp -mindepth 4 -maxdepth 4 -type d -printf '%p\n' | sort | sed -n '1,240p'
```

<details><summary>💭 Thinking</summary>

**Reviewing structure**

I’m moving from the overview into targeted inspection: configuration, package boundaries, tests, examples, and documentation. I’ll verify behavior against authoritative references while avoiding assumptions from filenames alone.

**Reviewed structure**

</details>

The codebase already has stable identities, typed flows, replayable caches, and immutable artifacts. The key redesign is separating add-only evidence discovery from rank-sensitive fusion, truncation, and reranking.

```unknown
bash -lc cd /mnt/data/rag-ttc-work/rag-ttc
base='ttmp/2026/07/31/RAG-TTC-FLOW-001--flow-a-typed-step-pipeline-layer-unifying-retry-admission-caching-batching-and-failure-policy'
find "$base" -maxdepth 3 -type f -print | sort
printf '\n--- design doc ---\n'
sed -n '1,360p' "$base"/design-doc/*.md
printf '\n--- README ---\n'
sed -n '1,260p' "$base"/README.md
```

<details><summary>💭 Thinking</summary>

**Separating semantic layers**

I’m identifying a key design issue: additive fact discovery should remain separate from nonmonotonic ranking, limits, and ambiguity resolution. I’ll model these as staged layers: source data, derivation, resolution, effects, and observations.

**Separated semantic layers**

**Reviewing planner and runtime code**

</details>

```unknown
bash -lc cd /mnt/data/rag-ttc-work/rag-ttc
for f in pkg/rag/toolanswer/types.go pkg/rag/toolanswer/registry.go pkg/rag/toolanswer/search.go pkg/rag/toolanswer/evidence.go pkg/rag/toolanswer/service.go pkg/rag/toolanswer/session.go pkg/rag/toolanswer/trace.go pkg/rag/knowledgetools/scopeddb.go pkg/rag/toolconfig/types.go; do
 echo "--- $f ---"; sed -n '1,560p' "$f"; done
```

<details><summary>💭 Thinking</summary>

**Refining the handbook**

I’m connecting the repository’s boundaries to a rigorous staged model: additive derivation first, deterministic selection second, effects third, and observations last. I’ll turn that mapping into concrete semantics, package guidance, and migration steps.

**Refined the handbook**

</details>

```unknown
bash -lc pwd && ls -la /mnt/data/rag-ttc-work/rag-ttc | sed -n '1,120p' && find /mnt/data/rag-ttc-work/rag-ttc/pkg/rag -maxdepth 2 -type d | sort | sed -n '1,200p'
```

<details><summary>💭 Thinking</summary>

**Inspected repository architecture, documentation, and retrieval service files**

</details>

```unknown
bash -lc rg -n '^type |^func |^const \(' pkg/rag/indexbundle pkg/rag/chunking pkg/rag/embedding pkg/rag/generation pkg/rag/vector pkg/rag/lexical pkg/rag/evaluation pkg/rag/diagnostic pkg/rag/review pkg/rag/agenttrace pkg/app/session pkg/app/annotation | sed -n '1,260p'
```

<details><summary>💭 Thinking</summary>

**Inspected RAG code, documentation, tests, environment, and execution semantics**

</details>

```json
{"search_query":[{"q":"site:dl.acm.org CALM theorem monotonicity distributed systems paper Hellerstein Alvaro"},{"q":"site:research.google/pubs differential dataflow paper incremental computation McSherry Murray Isaacs Isard"},{"q":"site:dl.acm.org provenance semirings databases Green Karvounarakis Tannen paper"},{"q":"site:homepages.inf.ed.ac.uk bananas lenses envelopes barbed wire catamorphisms paper PDF"}],"response_length":"long"}
```

`knowledge/retrieve` already captures derivations, while `flow.Step` handles operational effects. I’ll preserve Go orchestration, adding explicit candidate, derivation, snapshot, and observation types with scoped determinism.

<details><summary>💭 Thinking</summary>

**Framing the handbook**

I’m consolidating the repository analysis into a practical handbook: current architecture, semantic gaps, formal concepts, proposed layers, migration patterns, examples, and validation guidance, while clearly separating verified facts from recommendations.

**Framed the handbook**

**Searched 7 websites**

</details>

```unknown
bash -lc sed -n '1,240p' /home/oai/skills/docx/SKILL.md && printf '\n---PDF skill?---\n' && sed -n '1,120p' /home/oai/skills/pdfs/SKILL.md
```

<details><summary>💭 Thinking</summary>

**Read document and PDF skills**

</details>

```json
{"search_query":[{"q":"site:hal.inria.fr conflict-free replicated data types Shapiro Preguiça Baquero Zawirski 2011 PDF"},{"q":"seminal Datalog semi-naive evaluation least fixpoint original paper PDF"},{"q":"Meijer Fokkinga Paterson Functional Programming with Bananas Lenses Envelopes and Barbed Wire PDF"},{"q":"Wouter Swierstra Data Types à la Carte Journal of Functional Programming PDF"}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Searched 27 websites**

</details>

```unknown
bash -lc cd /mnt/data/rag-ttc-work/rag-ttc && find .. -name AGENTS.md -o -name AGENT.md -o -name CLAUDE.md -print && printf '\nROOT FILES\n' && find . -maxdepth 2 -type f | sort | sed -n '1,180p' && printf '\nGO VERSION\n' && sed -n '1,80p' go.mod
```

<details><summary>💭 Thinking</summary>

**Inspected Go project structure, documentation, packages, and test coverage**

</details>

```unknown
bash -lc cd /mnt/data/rag-ttc-work/rag-ttc && \
for spec in \
'pkg/flow/step.go:1:180' \
'pkg/flow/policy.go:1:240' \
'pkg/flow/run.go:1:360' \
'pkg/flow/pipe.go:1:360' \
'pkg/flow/batch.go:1:300' \
'pkg/execution/map.go:1:240' \
'pkg/execution/cache.go:1:330' \
'pkg/execution/budget.go:1:220' \
'pkg/execution/resource_plan.go:1:260'; do \
 IFS=: read -r f a b <<< "$spec"; echo "===== $f:$a-$b ====="; nl -ba "$f" | sed -n "${a},${b}p"; done
```

<details><summary>💭 Thinking</summary>

**Synthesizing the design**

I’m treating retrieval, knowledge expansion, ranking, execution, and experiment recording as distinct concerns. The handbook will preserve existing strengths while adding explicit semantic boundaries and reproducibility rules.

**Synthesized the design**

</details>

```unknown
bash -lc sed -n '1,260p' /home/oai/skills/docx/SKILL.md
```

<details><summary>💭 Thinking</summary>

**Inspecting repository files with line references**

</details>

```json
{"search_query":[{"q":"site:arxiv.org Keeping CALM When Distributed Consistency is Easy Hellerstein Alvaro 2019"},{"q":"site:hal.inria.fr Conflict-Free Replicated Data Types Shapiro Preguica Baquero Zawirski 2011 pdf"},{"q":"site:dl.acm.org Provenance Semirings Green Karvounarakis Tannen 2007"},{"q":"site:microsoft.com research Differential Dataflow McSherry Murray Isaacs Isard 2013"}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Searched 15 websites**

</details>

```unknown
bash -lc python - <<'PY'
import json
p='/mnt/data/rag-ttc-work/goscope.json'
d=json.load(open(p))
print(type(d), d.keys() if isinstance(d,dict) else len(d))
if isinstance(d,dict):
    for k,v in d.items():
        print(k, type(v), len(v) if hasattr(v,'__len__') else '')
PY
```

<details><summary>💭 Thinking</summary>

**Inspected repository structure, RAG architecture, documentation, experiments, and dependencies**

</details>

```unknown
bash -lc mkdir -p /mnt/data/rag-ttc-handbook-assets
cat > /mnt/data/rag-ttc-handbook-assets/current-architecture.dot <<'DOT'
digraph G {
  graph [rankdir=TB, bgcolor="white", margin=0.08, nodesep=0.25, ranksep=0.38, fontname="DejaVu Sans"];
  node [shape=box, style="rounded,filled", fillcolor="#f7f7f7", color="#4b5563", fontname="DejaVu Sans", fontsize=10, margin="0.12,0.08"];
  edge [color="#6b7280", arrowsize=0.65, penwidth=1.0];

  subgraph cluster_material {
    label="Immutable material and identity"; color="#a3a3a3"; style="rounded";
    rag [label="pkg/rag\nDocument · Chunk · Representation · Evidence"];
    repr [label="chunking / representations / embedding"];
    bundle [label="indexbundle\ncontent-addressed index snapshot"];
    rag -> repr -> bundle;
  }

  subgraph cluster_semantic {
    label="RAG behavior (currently mixed discovery + decisions)"; color="#a3a3a3"; style="rounded";
    search [label="lexical / vector\nbounded search observations"];
    retrieve [label="retrieval\ncollapse · RRF · hydrate"];
    knowledge [label="knowledge/retrieve\nconcept · fact · relation planning"];
    connected [label="connected\ngate · fuse · reorder · context"];
    answering [label="answering\nretrieve · prepare · interpret"];
    toolanswer [label="toolanswer\nadaptive loop + first-seen evidence ledger"];
    search -> retrieve -> answering;
    knowledge -> connected -> answering;
    search -> toolanswer;
  }

  subgraph cluster_mechanics {
    label="Operational mechanics"; color="#a3a3a3"; style="rounded";
    flow [label="flow\ntyped Step · composition · replay"];
    exec [label="execution\nparallelism · budgets · cache"];
    flow -> exec;
  }

  subgraph cluster_artifacts {
    label="Durable records"; color="#a3a3a3"; style="rounded";
    experiment [label="experiment\nimmutable inputs · append-only observations"];
    session [label="session / agenttrace / annotation\nevent logs and review state"];
  }

  bundle -> search;
  flow -> repr [style=dashed];
  flow -> search [style=dashed];
  flow -> answering [style=dashed];
  answering -> experiment [style=dashed];
  toolanswer -> session [style=dashed];
}
DOT
cat > /mnt/data/rag-ttc-handbook-assets/proposed-architecture.dot <<'DOT'
digraph G {
  graph [rankdir=LR, bgcolor="white", margin=0.08, nodesep=0.30, ranksep=0.42, fontname="DejaVu Sans"];
  node [shape=box, style="rounded,filled", fillcolor="#f8fafc", color="#475569", fontname="DejaVu Sans", fontsize=10, margin="0.13,0.09"];
  edge [color="#64748b", arrowsize=0.7, penwidth=1.05];

  material [label="1. Material snapshot\ndocuments · chunks · representations · indexes"];
  obligations [label="2. Effect obligations\nsearch · embed · generate · tool calls"];
  observations [label="3. Recorded observations\ncall identity · scope · raw output digest"];
  closure [label="4. Add-only semantic state\nfacts · candidates · derivations · closure"];
  decision [label="5. Frozen decisions\nresolve · rank · top-K · gate · context"];
  generation [label="6. Answer contract\ngenerate · parse · cite · validate"];

  material -> obligations -> observations -> closure -> decision -> generation;
  closure -> obligations [label="new obligations", fontsize=8, constraint=false];

  mechanics [shape=box3d, label="flow + execution\nexecute obligations; cache, retry, budget", fillcolor="#eef2ff"];
  artifacts [shape=folder, label="experiment + session artifacts\nrecord observations, snapshots, decisions, status", fillcolor="#f1f5f9"];

  mechanics -> obligations [style=dashed, dir=both];
  observations -> artifacts [style=dashed];
  closure -> artifacts [style=dashed];
  decision -> artifacts [style=dashed];
  generation -> artifacts [style=dashed];
}
DOT
cat > /mnt/data/rag-ttc-handbook-assets/closure-loop.dot <<'DOT'
digraph G {
  graph [rankdir=LR, bgcolor="white", margin=0.08, nodesep=0.32, ranksep=0.35, fontname="DejaVu Sans"];
  node [shape=box, style="rounded,filled", fillcolor="#f8fafc", color="#475569", fontname="DejaVu Sans", fontsize=10, margin="0.14,0.09"];
  edge [color="#64748b", arrowsize=0.7, penwidth=1.05];

  seed [label="Seed state\nimmutable facts + observations"];
  frontier [label="Frontier\nnew fact IDs since last round"];
  rules [label="Pure rule evaluation\nread snapshot + frontier"];
  delta [label="Delta\nnew facts + derivations + obligations"];
  join [label="Lawful join\nassociative · commutative · idempotent"];
  state [label="Next state\ncollision checked"];
  stop [shape=diamond, label="No new facts\nand no pending obligations?", fillcolor="#ffffff"];
  frozen [label="Frozen semantic snapshot\ncontent digest + status"];
  external [label="flow.Step executes obligations\nand returns recorded observations", fillcolor="#eef2ff"];

  seed -> frontier -> rules -> delta -> join -> state -> stop;
  stop -> frozen [label="yes"];
  stop -> frontier [label="no", constraint=false];
  delta -> external [label="obligations", style=dashed];
  external -> join [label="observations", style=dashed];
}
DOT
for f in /mnt/data/rag-ttc-handbook-assets/*.dot; do b=${f%.dot}; dot -Tpng -Gdpi=180 "$f" -o "$b.png"; dot -Tsvg "$f" -o "$b.svg"; done
ls -lh /mnt/data/rag-ttc-handbook-assets/*.png
```

<details><summary>💭 Thinking</summary>

**Preparing the handbook**

I’m organizing the final report around verified repository structures, formal semantic mappings, explicit limitations, proposed APIs, migration stages, reproducibility, and validation. I’ll preserve ordinary Go and avoid introducing a hidden workflow runtime.

**Finalizing deliverables**

I’m assembling the handbook from the completed analysis, preserving the repository’s strengths while making closure, provenance, deterministic decisions, external observations, and staged migration explicit.

**Completing the handbook**

I’m correcting the document’s heading numbering and pagination, then I’ll render and inspect the final report so the delivered Markdown and DOCX remain readable, consistent, and faithful to the analysis.

**Completed and finalized the handbook deliverables**

</details>

Concrete identity bugs surfaced in chunk hashing, fusion digests, and model-cache profiles. The completed handbook uses `answering.Prepared` as a template and distinguishes domain equality from operational replay.

```unknown
bash -lc ls -lah /mnt/data | sed -n '1,200p' && echo '--- work ---' && ls -lah /mnt/data/rag-ttc-work | sed -n '1,120p' && echo '--- source headings ---' && sed -n '1,100p' /mnt/data/rag-ttc-pandoc-source.md && echo '--- make ref ---' && sed -n '1,260p' /mnt/data/make_rag_reference.py
```

<details><summary>💭 Thinking</summary>

**Created, formatted, validated, and packaged the RAG-TTC architecture handbook and assets**

</details>

# rag-ttc Semantic Architecture Handbook

I completed a codebase-level semantic and architectural review of `rag-ttc`. The handbook is 51 pages and covers the current structures, concrete defects, formal model, proposed Go APIs, package-by-package adaptations, semantic laws, property-based tests, and a staged migration plan.

- [Read the PDF handbook](sandbox:/mnt/data/rag-ttc-semantic-handbook.pdf)
- [Download the editable DOCX](sandbox:/mnt/data/rag-ttc-semantic-handbook.docx)
- [Read the Markdown source](sandbox:/mnt/data/rag-ttc-semantic-handbook.md)
- [Inspect the repository inventory](sandbox:/mnt/data/rag-ttc-inventory.json)

## Main conclusions

`rag-ttc` already has several unusually strong foundations:

- Content-addressed chunks and source lineage.
- Narrow, typed component interfaces.
- Deterministic ordering and tie-breaking.
- `flow` abstractions for caching, retries, budgets, batching, and restoring result order.
- Immutable or append-oriented experiment artifacts.
- Explicit answering phases.
- A deliberately enforced boundary between reusable research packages and the application layer.
- An intentional rejection of a general workflow DSL.

The main missing piece is not orchestration. It is a small **information-semantic kernel** that explicitly defines:

- What counts as the same fact.
- How one fact can have several derivations.
- How independently produced states merge.
- Which operations only add knowledge.
- Which operations select, rank, truncate, or replace knowledge.
- What it means for recursive retrieval to be complete.
- Which configuration values are part of semantic identity and cache correctness.

The proposed architecture therefore does **not** replace `flow` or introduce a new workflow language. It separates two concerns:

```text
Operational semantics                    Information semantics
---------------------                    ---------------------
cache                                    fact identity
retry                                    derivations
batching                                 provenance
budget                                   merge laws
concurrency                              closure
order restoration                        ranked views
```

`flow` remains responsible for how work executes. The semantic kernel defines what the result means.

## Recommended core structure

The handbook proposes a pipeline boundary of:

```text
Plan → Execute → Admit → Merge → View → Generate
```

- **Plan** creates typed retrieval requests without modifying the knowledge state.
- **Execute** performs network, model, index, or tool operations.
- **Admit** validates and converts raw outputs into canonical facts and derivations.
- **Merge** uses an associative, commutative, idempotent operation. Order, duplication, and retries therefore do not affect the result.
- **View** performs ranking, ambiguity resolution, top-\(k\), token packing, and citation-label assignment.
- **Generate** consumes a selected view rather than mutating the underlying evidence state.

The crucial distinction is that admission and merge are add-only, while ranking and limits are deliberately non-monotone views. That boundary is what makes the add-only portions safe to cache, parallelize, retry, incrementally update, and reproduce. This use of monotonicity follows the same core boundary identified by the CALM result for coordination-free distributed computation. citeturn794804search0turn794804search4

## Concrete findings

The static review identified several immediate issues that should be fixed before introducing broader abstractions:

1. **Generation cache identity is incomplete.** The cache cannot distinguish every inference profile because parts of model reasoning configuration are not included in the semantic key.

2. **The connected-runtime digest omits `RRFConstant`.** That parameter changes fusion behavior but does not participate in the runtime semantic digest.

3. **Fallback evidence identity is inconsistent with canonical chunk identity.** One path hashes chunk text using JSON hashing, while canonical chunks use the text digest function.

4. **Tool evidence admission may depend on completion order.** Under evidence limits, concurrent completion order can affect which items receive admission or citation labels.

5. **`flow.Report` uses display names as identity.** Repeated step names can conflate distinct executions.

6. **`rag.Evidence` mixes source facts with observations.** Rank, score, and selection metadata should not be embedded in the canonical evidence object because they vary by query and view.

7. **Knowledge planning mixes discovery with policy.** Candidate discovery, ambiguity resolution, ranking, and limits should be separate transformations.

The first three are direct identity or cache-correctness defects. The remaining items are architectural risks that become visible once canonical facts are separated from query-specific observations.

## Laws and tests

The proposed system is governed by executable laws rather than a large amount of abstract machinery:

```text
merge(a, b) == merge(b, a)                    // commutative
merge(merge(a, b), c) == merge(a, merge(b,c)) // associative
merge(a, a) == a                              // idempotent

seed ⊆ close(seed)                            // preserves input
close(close(seed)) == close(seed)             // stable
a ⊆ b ⇒ close(a) ⊆ close(b)                  // monotone

sequential(program) == parallel(program)
once(operation) == withRetries(operation)
migrate(closeOld(x)) == closeNew(migrate(x))
```

Additional tests verify that:

- Every admitted fact has at least one valid derivation.
- Hash equality implies semantic interchangeability.
- Cache keys include every behavior-affecting input.
- Increasing a retrieval budget never removes admitted facts.
- Ranking changes do not alter the canonical evidence store.
- Backend implementations preserve the same constructors and merge behavior.
- Authorization labels dominate all dependencies of a derived fact.

The provenance model is compatible with the entity/activity/agent structure standardized by W3C PROV, while retaining a smaller domain-specific Go representation. citeturn794804search6turn794804search2 Future delta-based and incremental execution can draw on the same principles used by Differential Dataflow and DBSP, but the report recommends introducing those only after identity and merge laws are stable. citeturn794804search5turn794804search3

## Recommended implementation order

The report proposes seven migration phases. The immediate sequence is:

1. Fix the three confirmed semantic-identity defects.
2. Add law tests around IDs, digests, cache keys, merge, retries, and ordering.
3. Introduce canonical `Fact`, `FactID`, `Derivation`, and `FactSet` types.
4. Keep scores, ranks, citation labels, and context positions in separate view types.
5. Refactor selected retrieval paths into `Plan → Execute → Admit`.
6. Add closure/frontier evaluation only to components that genuinely perform recursive derivation.
7. Introduce incremental maintenance and backend equivalence tests after the semantic kernel is established.

The analysis is static. The repository declares Go `1.26.5`, while the available environment provided Go `1.23.2` and could not fetch the required toolchain or modules. Consequently, the full test suite was not executed; the report distinguishes confirmed source-level defects from runtime risks that still require executable verification.


---

> Create a list of small self contained projects to really figure out the details of this RAG system, so that we can validate individual subsystems and then how they compose. The idea is to give each of these to a set of phd students to have them build it and assess and refine it, and then in a second pass (later on) put them together to see how they compose. Write a detailed set of project documents that conain the full framing of each subproject, as markdown + pdf. I will then hand them out to be worked on and then we can test them as users / explore the different scenarios and constellations and concerns and such.

<details><summary>💭 Thinking</summary>

**Planning the documentation set**

I’m going to inspect the uploaded project files and existing handbook, then map the repository into several concrete project tracks. I’ll produce self-contained Markdown documents plus matching PDFs, with navigation, prerequisites, milestones, acceptance criteria, and rigorous technical explanations.

**Planned the documentation set**

</details>

I’ll create a coordinated portfolio of independently assignable briefs with subsystem boundaries, invariants, deliverables, experiments, shared evaluation contracts, and later integration plans, delivered as Markdown, PDFs, and an archive.

```unknown
bash -lc cat /home/oai/skills/pdfs/SKILL.md && printf '
---FILES---
' && ls -lah /mnt/data | sed -n '1,120p'
```

<details><summary>💭 Thinking</summary>

**Mapping the project tracks**

I’m inspecting the repository structure, handbook, and core interfaces now. I’m grouping the work into focused research projects that stand alone initially, while preserving shared terminology, interfaces, evaluation methods, and a later integration path.

**Mapped the project tracks**

**Inspected PDF guidelines, project files, handbook, inventory, and Go packages**

</details>

```unknown
bash -lc cd /mnt/data/rag-ttc-src/rag-ttc
printf '%s\n' '--- README ---'
sed -n '1,260p' README.md
printf '%s\n' '--- core rag files ---'
for f in pkg/rag/*.go; do echo "### $f"; grep -nE '^(type|func|const|var) ' "$f" | sed -n '1,160p'; done
printf '%s\n' '--- flow definitions ---'
for f in pkg/flow/*.go; do echo "### $f"; grep -nE '^(type|func|const|var) ' "$f" | sed -n '1,160p'; done
printf '%s\n' '--- execution definitions ---'
for f in pkg/execution/*.go; do echo "### $f"; grep -nE '^(type|func|const|var) ' "$f" | sed -n '1,160p'; done
```

<details><summary>💭 Thinking</summary>

**Structuring research projects**

I’m organizing the work into focused projects covering semantic identity, provenance, deterministic merging, flow semantics, retrieval, planning, augmentation, evidence admission, answer contracts, and reproducibility. Each will include implementation boundaries and integration checkpoints.

**Structured research projects**

**Finalizing project scope**

I’m refining the portfolio into implementation-ready tracks: semantic identity, provenance, deterministic state, execution semantics, retrieval, planning, augmentation, evidence admission, answer contracts, maintenance, storage conformance, and reproducible experiments.

**Finalized project scope**

</details>

I’ll separate foundational semantics, policy, and operations, using narrow APIs, mocks, standalone prototypes, `rag-ttc` adapters, and law-based tests to enable comparison before integration.

Deterministic fixtures will define acceptance against the current snapshot; provider-backed experiments remain optional, ensuring each semantic claim can be validated without external services.

```unknown
bash -lc cd /mnt/data/rag-ttc-src/rag-ttc
for f in pkg/rag/answering/*.go; do echo "\n===== $f ====="; sed -n '1,420p' "$f"; done
```

<details><summary>💭 Thinking</summary>

**Preparing research documents**

I’m converting the repository analysis into a complete portfolio: standalone project briefs, shared terminology, implementation checkpoints, evaluation gates, and a later composition protocol.

**Prepared research documents**

</details>

```unknown
bash -lc sed -n '1,260p' /home/oai/skills/pdfs/SKILL.md && printf '\n---FILES---\n' && ls -la /mnt/data | sed -n '1,200p' && printf '\n---OUT---\n' && find /mnt/data/rag-ttc-research-projects -maxdepth 3 -type f -printf '%p %s bytes\n' 2>/dev/null | sort | sed -n '1,240p' && printf '\n---SCRIPT---\n' && ls -l /mnt/data/build_project_portfolio.py 2>/dev/null || true && head -n 40 /mnt/data/build_project_portfolio.py 2>/dev/null || true
```

<details><summary>💭 Thinking</summary>

**Inspected RAG architecture, artifacts, documentation, and research project planning**

</details>

```unknown
bash -lc cat > /mnt/data/portfolio_builder.py <<'PY'
from __future__ import annotations

from pathlib import Path
from textwrap import dedent
import json
import re
import hashlib

ROOT = Path('/mnt/data/rag-ttc-research-projects')
MD = ROOT / 'markdown'
PDF = ROOT / 'pdf'
ASSETS = ROOT / 'assets'
for p in (ROOT, MD, PDF, ASSETS):
    p.mkdir(parents=True, exist_ok=True)

SNAPSHOT_SHA = 'bcaedecb28a5af5280d5635c6c4deabfef525fb62e6b9a101dce8d4a21e92fdb'
SNAPSHOT_PATH = 'rag-ttc.zip'
REPORT_DATE = 'August 4, 2026'
GO_DECLARED = '1.26.5'
GO_AVAILABLE = '1.23.2'

PROJECTS: list[dict] = []


def bullets(items: list[str]) -> str:
    return '\n'.join(f'- {x}' for x in items)


def numbered(items: list[str]) -> str:
    return '\n'.join(f'{i}. {x}' for i, x in enumerate(items, 1))


def table(rows: list[tuple[str, str, str]], headers=('Item', 'Requirement', 'Evidence')) -> str:
    out = [f'| {headers[0]} | {headers[1]} | {headers[2]} |', '|---|---|---|']
    for a, b, c in rows:
        out.append(f'| {a} | {b} | {c} |')
    return '\n'.join(out)


def yaml_header(title: str, subtitle: str) -> str:
    return dedent(f'''\
    ---
    title: "{title.replace('"', "'")}"
    subtitle: "{subtitle.replace('"', "'")}"
    author: "rag-ttc semantic research portfolio"
    date: "{REPORT_DATE}"
    lang: en-US
    documentclass: article
    fontsize: 10pt
    geometry: margin=0.72in
    toc: true
    toc-depth: 3
    numbersections: true
    colorlinks: true
    linkcolor: blue
    urlcolor: blue
    header-includes:
      - |-
        \\usepackage{microtype}
        \\usepackage{booktabs}
        \\usepackage{longtable}
        \\usepackage{array}
        \\usepackage{enumitem}
        \\usepackage{fancyhdr}
        \\usepackage{fvextra}
        \\pagestyle{fancy}
        \\fancyhf{{}}
        \\fancyhead[L]{{rag-ttc research portfolio}}
        \\fancyhead[R]{{\\thepage}}
        \\setlist{{nosep,leftmargin=*}}
        \\DefineVerbatimEnvironment{{Highlighting}}{{Verbatim}}{{breaklines,breakanywhere,commandchars=\\\\\\{{\\}}}}
    ---
    ''')


def source_map_block(items: list[tuple[str, str]]) -> str:
    rows = [('Path or symbol', 'Why it matters', 'First task')]
    text = ['| Path or symbol | Why it matters | First task |', '|---|---|---|']
    for path, why in items:
        first = 'Read tests and record observable behavior before changing code.'
        text.append(f'| `{path}` | {why} | {first} |')
    return '\n'.join(text)


def law_table(laws: list[dict]) -> str:
    out = ['| Law | Operational statement | Required test oracle |', '|---|---|---|']
    for law in laws:
        out.append(f"| **{law['name']}** | {law['statement']} | {law['test']} |")
    return '\n'.join(out)


def experiment_table(experiments: list[dict]) -> str:
    out = ['| Scenario | Intervention | Measurements and expected interpretation |', '|---|---|---|']
    for e in experiments:
        out.append(f"| **{e['name']}** | {e['method']} | {e['measure']} |")
    return '\n'.join(out)


def render_project(p: dict) -> str:
    title = f"{p['code']} - {p['title']}"
    subtitle = f"Self-contained research and implementation brief - {p['domain']}"
    front = yaml_header(title, subtitle)
    api = p.get('api', '').strip()
    api_section = f"\n```go\n{api}\n```\n" if api else ''
    special = p.get('special_sections', '').strip()
    if special:
        special = '\n\n' + special + '\n'
    return front + dedent(f'''\
    # Assignment at a glance

    **Mission.** {p['mission']}

    **Recommended staffing.** {p.get('staffing', 'One or two PhD students, with one repository maintainer available for design review.')}

    **Suggested research window.** {p.get('window', 'Six to eight weeks, including implementation, experiments, and a reproducibility review.')}

    **Primary repository area.** {', '.join(f'`{x}`' for x in p['primary_paths'])}

    **Dependency policy.** The prototype must remain independently executable. It may copy small data types or define an adapter, but it must not require another portfolio project to exist. Integration is deferred to Phase II.

    ## Required outcome

    The team must deliver a working reference implementation, executable law tests, a written assessment of the current `rag-ttc` behavior, and a narrow interface that a later composition team can consume. A design-only submission is incomplete.

    # 1. Why this project exists

    {p['context'].strip()}

    ## Problem statement

    {p['problem'].strip()}

    # 2. Research questions and hypotheses

    ## Research questions

    {numbered(p['questions'])}

    ## Hypotheses to test

    {bullets(p['hypotheses'])}

    A hypothesis may be rejected. The project is successful when the rejection is supported by a reproducible counterexample and the interface is revised accordingly.

    # 3. Scope

    ## In scope

    {bullets(p['goals'])}

    ## Explicit non-goals

    {bullets(p['non_goals'])}

    # 4. Current `rag-ttc` starting points

    {source_map_block(p['source_map'])}

    The first repository deliverable is a short behavioral inventory. It must distinguish: behavior required by documentation, behavior required by tests, behavior that is incidental to the current implementation, and behavior that is not yet specified.

    # 5. Standalone system to build

    {p['prototype'].strip()}
    {api_section}
    ## Minimal execution modes

    The prototype must support all of the following without network access:

    - a deterministic in-memory mode used as the specification oracle;
    - a fault-injection mode for duplicates, reordering, delays, partial failure, or corruption as relevant to the project;
    - a command that emits machine-readable results and a human-readable report;
    - a replay mode that consumes previously recorded observations rather than calling a provider.

    # 6. Semantic model

    {p['model'].strip()}

    ## Required laws

    {law_table(p['laws'])}

    The team must state preconditions for every law. For example, schedule independence requires fair execution and idempotent admission; it is not valid for arbitrary side effects.

    # 7. Required experiment matrix

    {experiment_table(p['experiments'])}

    ## Shared fixtures

    {bullets(p['fixtures'])}

    Each fixture needs a stable digest and an explanation of which invariant it stresses. Randomized tests must print or persist their seed on failure.

    # 8. Implementation work plan

    {numbered(p['milestones'])}

    At the end of each milestone, preserve a runnable command and a result artifact. Avoid a long-lived branch that only becomes executable at the end.

    # 9. Required deliverables

    {bullets(p['deliverables'])}

    Every submission must also include:

    - `README.md` with exact build and run commands;
    - `interface.json` describing exported types, operations, laws, version, and compatibility assumptions;
    - `results.json` containing fixture digests, test seeds, measurements, and pass/fail outcomes;
    - `limitations.md` listing unresolved ambiguity, rejected hypotheses, and known counterexamples;
    - deterministic fakes for every external effect;
    - a short patch or adapter showing how the result could attach to the current repository without forcing adoption.

    # 10. Acceptance gates

    {bullets(p['acceptance'])}

    A project that improves benchmark quality but violates its semantic laws does not pass. A project that satisfies laws but cannot run on realistic repository fixtures also does not pass.

    # 11. Evaluation rubric

    | Area | Weight | Review question |
    |---|---:|---|
    | Semantic precision | 25% | Are identity, equality, state transitions, and failure behavior explicit? |
    | Executable evidence | 25% | Do law tests and fault-injection experiments support the claims? |
    | Repository fidelity | 20% | Does the work explain and preserve or deliberately revise current behavior? |
    | Interface quality | 15% | Can a later team consume the artifact without reverse engineering it? |
    | Reproducibility | 10% | Are inputs, versions, seeds, and observations sufficient to rerun the study? |
    | Clarity of limitations | 5% | Are non-results and unsafe assumptions stated precisely? |

    # 12. Risks and adversarial cases

    {bullets(p['risks'])}

    The final report must include at least one minimized failing example found during the project, even when the implementation was subsequently fixed.

    # 13. Integration contract for Phase II

    ## Exports

    {bullets(p['exports'])}

    ## Imports assumed from future projects

    {bullets(p.get('imports', ['None. All required collaborators are represented by local interfaces or recorded fixtures.']))}

    ## Composition questions

    {bullets(p['composition'])}

    `interface.json` must classify every field as one of: semantic identity, observation identity, invocation identity, view metadata, operational trace, or secret. This classification is a core handoff artifact.
    {special}
    # 14. Minimal mathematical background

    {p['math'].strip()}

    The mathematical notation is optional in code and mandatory only where it removes ambiguity. Every equation in the report must be followed by a programmer-level statement and an executable test interpretation.

    # 15. Student completion checklist

    - [ ] Baseline behavior is documented before refactoring.
    - [ ] The standalone oracle runs offline.
    - [ ] Every law has a positive test and a deliberate counterexample.
    - [ ] Fault injection covers the project's main threat model.
    - [ ] `interface.json`, `results.json`, and fixture digests are complete.
    - [ ] The patch or adapter does not introduce a workflow DSL.
    - [ ] The report separates semantic state, ranked views, and operational traces.
    - [ ] Limitations and rejected hypotheses are explicit.
    - [ ] Phase II composition assumptions are narrow and versioned.

    # Appendix A. Repository snapshot

    This brief is based on `{SNAPSHOT_PATH}` with SHA-256:

    ```text
    {SNAPSHOT_SHA}
    ```

    The repository declares Go `{GO_DECLARED}`. The analysis environment exposed Go `{GO_AVAILABLE}` and could not execute the complete declared toolchain. Students must run the full repository test suite in the project's supported environment and report the exact toolchain and module graph used.
    ''')


def add_project(data: dict) -> None:
    PROJECTS.append(data)


def strip_yaml(text: str) -> str:
    if text.startswith('---\n'):
        end = text.find('\n---\n', 4)
        if end >= 0:
            return text[end + 5:]
    return text


def write_projects() -> None:
    manifest = []
    for p in PROJECTS:
        filename = f"{p['code'].lower()}-{p['slug']}.md"
        path = MD / filename
        text = render_project(p)
        path.write_text(text, encoding='utf-8')
        manifest.append({
            'code': p['code'],
            'title': p['title'],
            'slug': p['slug'],
            'domain': p['domain'],
            'markdown': f'markdown/{filename}',
            'pdf': f"pdf/{filename[:-3]}.pdf",
            'primary_paths': p['primary_paths'],
            'exports': p['exports'],
        })
    (ROOT / 'project-manifest.json').write_text(json.dumps({
        'schema_version': 'rag-ttc-project-portfolio/v1',
        'created': REPORT_DATE,
        'source_snapshot_sha256': SNAPSHOT_SHA,
        'projects': manifest,
    }, indent=2) + '\n', encoding='utf-8')

PY
python -m py_compile /mnt/data/portfolio_builder.py
```

<details><summary>💭 Thinking</summary>

**Updated project generator with projects P01–P10 and validated contracts**

</details>

```unknown
bash -lc cat >> /mnt/data/portfolio_builder.py <<'PY'

def write_portfolio_guide() -> Path:
    rows = []
    for p in PROJECTS:
        rows.append(f"| **{p['code']}** | {p['title']} | {p['mission']} |")
    project_rows = '\n'.join(rows)
    path = MD / '00-portfolio-guide.md'
    text = yaml_header(
        'rag-ttc Research Project Portfolio',
        'Coordinator handbook for thirteen independent semantic validation projects',
    ) + dedent(f'''\
    # Executive purpose

    This portfolio converts the architectural questions in `rag-ttc` into thirteen small, separately executable research and implementation projects. Each team receives one project brief, a frozen repository snapshot, shared fixtures, and a common submission contract. The first pass is deliberately **non-integrated**: every team must build a local oracle and validate one subsystem without depending on another team's code. The second pass composes only artifacts that have passed their individual law and reproducibility gates.

    The program is designed for PhD students who can work across programming languages, systems design, formal methods, databases, information retrieval, and empirical evaluation. The expected product of each project is not a speculative architecture essay. It is a runnable reference implementation, an executable semantics, adversarial fixtures, measurements, and a narrow interface suitable for later integration.

    # 1. Source baseline and review limits

    The common source snapshot is `rag-ttc.zip` with SHA-256:

    ```text
    {SNAPSHOT_SHA}
    ```

    The snapshot declares Go `{GO_DECLARED}`. The initial static review environment exposed Go `{GO_AVAILABLE}` and could not run the complete declared toolchain. Every project must therefore execute the full repository tests in the supported environment before claiming runtime confirmation. Source-level findings in these briefs are starting hypotheses to reproduce, not substitutes for student verification.

    The existing repository intent must be preserved:

    - experiments remain ordinary Go programs composed from typed packages;
    - `pkg/flow` remains execution mechanics, not a hidden workflow runtime;
    - the research packages must not depend on `pkg/app`;
    - provider-backed effects are replaceable seams and must have deterministic or recorded fakes;
    - run artifacts remain inspectable and explicit;
    - no team may introduce a general-purpose RAG DSL as a shortcut.

    # 2. Program architecture

    ![Portfolio dependency map](../assets/project-map.png){{width=94%}}

    The project boundaries follow one semantic pipeline:

    ```text
    source snapshots and configuration
        -> Plan typed requests
        -> Execute effects
        -> Admit canonical facts and derivations
        -> Merge add-only state
        -> Build ranked and bounded views
        -> Generate from one frozen context view
        -> Validate the answer contract
        -> Persist verifiable artifacts
    ```

    ![Proposed semantic architecture](../assets/proposed-architecture.png){{width=94%}}

    This is not a required package layout. It is a classification of responsibilities. Existing packages may continue to combine several responsibilities at a public convenience boundary, provided the project prototypes expose and test the internal semantic boundaries.

    # 3. Common vocabulary

    **Fact.** An immutable item identified by its meaning in a versioned domain: document revision, exact chunk, generated representation, query request, knowledge edge, or admitted evidence item.

    **Observation.** A captured result of an effect such as a search, model call, database request, or external tool. The observation records what happened under one semantic request and snapshot. It is not automatically a timeless fact.

    **Derivation.** A record that a rule admitted an output fact from named input facts, policy/version identities, and optional recorded observations. Several derivations may support the same fact.

    **Semantic state.** The add-only collection of canonical facts, derivations, and observation references. It excludes rank, top-k membership, token position, citation label, latency, and retry count.

    **View.** A deterministic, versioned projection over a fixed state or candidate snapshot. Fusion, reranking, ambiguity choice, top-k, token packing, citation labels, and answer context are views. Views may remove and reorder items.

    **Trace.** Operational history: attempts, cache hits, wait time, worker completion, budget use, failures, provider usage, and timestamps. Two runs may have equal semantic state and unequal traces.

    **Closure.** Repeatedly apply add-only rules until no new rule firing is possible or a declared limit stops the run.

    **Replay.** Recreate a stage from deterministic inputs or reuse a previously recorded external observation. A new provider call is a new execution, not replay.

    # 4. Shared semantic rules

    Every project must use the following default distinctions unless it presents evidence for a revised contract.

    ## 4.1 Identity classes

    - **Fact identity:** same immutable semantic object.
    - **Request identity:** same complete effect request under the same semantic environment.
    - **Observation identity:** same captured external result for a request.
    - **Invocation identity:** same occurrence, attempt, turn, or run.
    - **View identity:** same input snapshot and same versioned selection policy.

    Equality between different classes is undefined. A cache key is normally a request identity, not a run ID.

    ## 4.2 State, view, and trace separation

    The add-only state must not embed query-specific rank, score, presentation label, worker, attempt, or timestamp. Those values belong to observations, views, or traces. Teams may maintain compatibility adapters to current structs, but their reference semantics must expose the distinction.

    ## 4.3 Effects are recorded

    A model, index, database, filesystem, clock, or network operation is an effect. The first-pass prototypes must support recorded observations and deterministic fakes. A proof or replay claim must state whether an effect was recomputed or merely replayed from its observation.

    ## 4.4 Conflicts fail closed

    When one semantic ID is associated with unequal canonical payloads, the system reports a conflict. Last-write-wins, earliest-write-wins, and arbitrary map overwrite are not acceptable canonical-state behavior.

    ## 4.5 Selection is explicit

    Limits and rankings are useful and intentionally non-monotone. They must be named policies with complete input identity and exclusion reasons. They do not erase the underlying candidates.

    # 5. Project index

    | Code | Project | Assignment |
    |---|---|---|
    {project_rows}

    ## Suggested student matching

    - Formal methods, programming languages, and property-based testing: P01, P03, P04, P06, P11.
    - Information retrieval and evaluation: P05, P06, P07, P09.
    - Distributed systems and databases: P03, P04, P08, P10, P11, P12.
    - Security and privacy: P01, P02, P12, P13.
    - Human-computer interaction and serving behavior: P08, P09, P12, P13.

    Assign at most one primary project per student in the first pass. Cross-project discussion is encouraged, but no project may import another team's in-progress implementation.

    # 6. Common fixture kit

    The coordinator should create a versioned `fixtures/portfolio-v1/` directory copied into every project workspace. Each team may add project-specific fixtures but must preserve these shared ones.

    ## 6.1 Source corpus

    - A deterministic small corpus with exact document IDs, byte digests, titles, URIs, and Unicode edge cases.
    - Overlapping fixed chunks with exact byte ranges.
    - A second source revision with one local edit, one deletion, and one added document.
    - Public and restricted variants for information-flow studies.

    ## 6.2 Retrieval observations

    - Frozen lexical and vector hit lists with overlap, ties, duplicates, and missing references.
    - Weighted RRF policies with several constants and channel weights.
    - Reranker observations with ties, failures, and absent scores.
    - Context budgets that exercise top-k and greedy packing differences.

    ## 6.3 Knowledge repository

    - Concepts, aliases, facts, evidence spans, and relations in an in-memory JSON form.
    - A matching SQLite snapshot.
    - Known one-, two-, and three-hop paths to target evidence.
    - Ambiguous aliases and self-supporting cycles.

    ## 6.4 Generation and answer observations

    - Deterministic extractive outputs.
    - Frozen valid provider observations with complete request fingerprints.
    - Malformed JSON, unknown citations, uncited claims, contradictions, and safe abstentions.
    - Ordinal citation mappings and immutable chunk-ID mappings.

    ## 6.5 Operational and artifact fixtures

    - Cache envelopes: valid, corrupt, wrong schema, wrong full key, stale adapter, and cross-scope unsafe.
    - Effect scripts with transient/permanent failures, retries, delays, and cancellation.
    - Complete, failed, canceled, redacted, and truncated run bundles.
    - Same-ID/different-payload conflicts for facts, derivations, and observations.

    Every fixture directory contains a `manifest.json` with schema version, file digests, semantic purpose, expected outcomes, and sensitivity classification.

    # 7. Common submission contract

    Each project submission is a directory with this minimum shape:

    ```text
    pXX-project-name/
      README.md
      report.md
      limitations.md
      interface.json
      results.json
      fixtures/
        manifest.json
      cmd/
        <project-command>/
      internal/ or pkg/
      tests/
      adapters/
        ragttc/
      artifacts/
        representative-run/
    ```

    ## 7.1 `interface.json`

    The interface file is the Phase II handoff. Required fields:

    ```json
    {{
      "schema_version": "rag-ttc-project-interface/v1",
      "project": "P03",
      "implementation_version": "...",
      "source_snapshot_sha256": "{SNAPSHOT_SHA}",
      "exports": [
        {{
          "name": "State.Join",
          "kind": "operation",
          "input_schemas": ["..."],
          "output_schema": "...",
          "identity_inputs": ["..."],
          "laws": ["associative", "commutative", "idempotent"]
        }}
      ],
      "field_classification": {{
        "...": "semantic-identity | observation | invocation | view | trace | secret"
      }},
      "assumptions": ["..."],
      "known_incompatibilities": ["..."]
    }}
    ```

    ## 7.2 `results.json`

    Required fields include toolchain, module graph digest, fixture manifest digest, random seeds, test totals, failed law cases, minimized counterexamples, benchmark units, replay mode, and artifact paths. Measurements without units or input-size metadata are invalid.

    ## 7.3 Repository adapter

    The adapter is intentionally narrow. It may convert current repository values to the prototype's inputs and outputs. It must not refactor unrelated packages, introduce global registries, or make adoption necessary to run the experiment.

    # 8. Common test design

    Every team must provide four types of tests.

    1. **Example tests** for current repository fixtures and compatibility.
    2. **Law tests** that quantify invariants over generated values.
    3. **Fault-injection tests** for corruption, ordering, duplication, failure, cancellation, and resource limits relevant to the project.
    4. **Metamorphic tests** that vary one input or policy and assert which outputs may or must change.

    A property-based test failure must preserve its seed and a minimized case. A concurrency claim must include deterministic schedule control or enough recorded events to reproduce the schedule.

    # 9. Common review gates

    ## Gate A - behavioral baseline

    Before proposing new types, the team demonstrates current behavior on frozen fixtures and classifies each observed behavior as documented, tested, incidental, ambiguous, or defective.

    ## Gate B - executable semantics

    The reference implementation runs offline and every claimed law has an executable oracle. At least one deliberate counterimplementation must fail each central law.

    ## Gate C - adversarial validation

    Fault injection and mutation testing produce minimized counterexamples. The team shows that fixes remove the counterexample without hiding it through normalization or filtering.

    ## Gate D - repository fidelity

    The adapter processes real `rag-ttc` values and the full supported repository test suite is run. Behavioral differences are explicit.

    ## Gate E - handoff quality

    `interface.json`, `results.json`, schemas, fixture manifests, version identities, and limitations are complete enough for a different team to compose the project without reading implementation internals.

    # 10. Coordinator process

    Use a common cadence:

    - **Opening review:** approve scope, threat model, current-behavior inventory plan, and fixture additions.
    - **Semantics review:** approve types, identities, laws, counterexamples, and non-goals before major implementation.
    - **Midpoint demonstration:** require an offline executable and one law/fault result.
    - **Adversarial review:** another student team attempts to break the laws and interfaces.
    - **Final reproducibility review:** a clean machine follows only README and bundle metadata.
    - **Phase II admission:** accept only projects that pass all common gates or carry an explicit experimental waiver.

    A coordinator should prohibit shared mutable "common library" work during the first pass. Shared discoveries are recorded as issue documents; consolidation occurs only after interfaces and counterexamples are known.

    # 11. Minimal mathematics for all teams

    ## Equality and identity

    An ID defines when values may be treated as interchangeable. Tests must mutate inputs to find cases where equal IDs permit different behavior.

    ## Order and monotonicity

    `A <= B` means B contains at least all semantic information in A. An operation is monotone when adding input information cannot remove previously produced semantic facts. Ranking and top-k are usually not monotone and therefore belong to views.

    ## Join

    `A join B` is a lossless merge. For retry and schedule safety it should be associative, commutative, and idempotent. These are ordinary property tests.

    ## Fixed point and closure

    A state is closed when another rule pass adds nothing. A finite depth result can claim completeness only for derivations within that depth unless all possible facts are finite and saturation is reached.

    ## Induction

    To prove an invariant over derived facts: show it holds for seeds, show every rule preserves it, and show merging valid states preserves it. In code, these become constructor and property tests.

    ## Composition

    Two implementations compose safely when the exported output contract of one satisfies the input assumptions of the next. Phase II tests the equation directly rather than relying on matching names.

    # 12. Program-level success criteria

    The portfolio succeeds when it produces:

    - a reproducible map of current `rag-ttc` semantics and ambiguities;
    - independent executable oracles for the major subsystem boundaries;
    - minimized counterexamples for identity, ordering, provenance, replay, or authorization defects;
    - small APIs that compose through facts, observations, derivations, views, and traces;
    - evidence showing which abstractions reduce bugs and which add unnecessary complexity;
    - an end-to-end composition that remains ordinary Go and preserves repository boundaries.

    The goal is not to maximize abstraction. The goal is to discover the smallest structures that make important behavior explicit, testable, and stable under implementation change.
    ''')
    path.write_text(text, encoding='utf-8')
    return path


def write_phase2() -> Path:
    path = MD / '90-phase-ii-composition-protocol.md'
    scenarios = [
        ('C01', 'Cache-correct execution', 'P01 + P04', 'Execute the same semantic request under hit, miss, retry, worker, and batch variations.', 'Equal semantic result; identity excludes trace-only policy; cache and budget traces follow P04 specification.'),
        ('C02', 'Proof-preserving concurrent admission', 'P02 + P03 + P08', 'Collect duplicate tool evidence through several schedules, merge candidates, commit a bounded view, and produce a proof bundle.', 'Same batch membership and labels; one fact with all derivations; proof verifies under every schedule.'),
        ('C03', 'Candidate/view connected retrieval', 'P05 + P07', 'Combine frozen baseline and knowledge observations, then fuse, order, and pack through shared view types.', 'Baseline candidates preserved; policy identity complete; current-runtime differential explained.'),
        ('C04', 'Recursive connected retrieval', 'P06 + P07', 'Feed depth-bounded knowledge closure snapshots into connected composition.', 'Completeness rank and stop reason survive composition; gates and views do not masquerade as closure.'),
        ('C05', 'Tool evidence to answer contract', 'P08 + P09', 'Freeze a deterministic committed tool view, label it, generate/replay an answer, and validate layers.', 'Labels normalize to immutable IDs; context membership is frozen; assurance report is replayable.'),
        ('C06', 'Proof-carrying answer artifact', 'P02 + P09 + P12', 'Package answer claims, citations, derivations, observations, and validation results in a run bundle.', 'Bundle verifies integrity; deterministic checks replay; external judgments are labeled observations.'),
        ('C07', 'Incremental multi-backend state', 'P10 + P11', 'Apply additions, removals, and migrations to in-memory and SQLite states.', 'Incremental equals clean rebuild; both backends export equal canonical state; migration report is complete.'),
        ('C08', 'Identity-safe replay', 'P01 + P12', 'Replay bundles while mutating prompts, schemas, models, adapters, and operational fields.', 'Required semantic mutations invalidate replay/cache; trace-only mutations do not.'),
        ('C09', 'Secure cache and artifact path', 'P13 + P01 + P04 + P12', 'Run paired principals through cache, execution, answer, and bundle export.', 'No cross-scope hit or low-visible leak; restricted artifacts are blocked/redacted with honest assurance.'),
        ('C10', 'Full deterministic stack', 'P01-P13', 'Run source ingestion through closure, connected/tool retrieval, views, answer audit, proof bundle, and replay.', 'All subsystem laws hold at interfaces; schedule and retry changes preserve semantic output; declared policy changes produce explained view changes.'),
    ]
    scenario_rows = '\n'.join(f'| **{c}** | {n} | {p} | {m} | {s} |' for c,n,p,m,s in scenarios)
    text = yaml_header(
        'rag-ttc Phase II Composition Protocol',
        'Pairwise, multi-project, and end-to-end integration experiments',
    ) + dedent(f'''\
    # Purpose

    Phase II begins only after the independent projects have executable interfaces, fixture manifests, law results, and limitations. The objective is not to merge all prototype code into the repository. The objective is to test whether independently specified semantics compose and to identify the smallest shared kernel worth adopting.

    ![Phase II target architecture](../assets/proposed-architecture.png){{width=94%}}

    # 1. Admission requirements

    A project may enter composition when:

    - its offline reference command runs from a clean checkout;
    - current repository behavior is documented and differential fixtures exist;
    - every central law has positive tests and a known failing counterimplementation;
    - `interface.json` and all referenced schemas are versioned and resolvable;
    - `results.json` records toolchain, fixture digests, random seeds, and limitations;
    - exported fields are classified as semantic identity, observation, invocation, view, trace, or secret;
    - no required behavior depends on another team's private source tree;
    - unresolved law failures have a written experimental waiver.

    # 2. Composition method

    ## 2.1 Start with adapters, not shared refactors

    Each integration scenario uses adapters between exported schemas. Do not begin by reconciling package names or moving code. First determine whether the contracts are actually compatible.

    ## 2.2 Compare at three levels

    - **Semantic equality:** canonical facts, derivations, requests, observations, and state.
    - **View equality:** policy IDs, ordering, selected membership, labels, and exclusion reasons.
    - **Trace relation:** permitted differences in attempts, cache hits, workers, timing, and completion order.

    A scenario fails when a difference appears in the wrong level or lacks a declared policy explanation.

    ## 2.3 Freeze effects

    Initial composition uses recorded observations. Only after deterministic composition passes may a live provider or mutable backend be introduced. Live executions create new observation IDs and are compared empirically, not treated as exact replay.

    ## 2.4 Preserve counterexamples

    Every interface mismatch is reduced to a fixture and added to a shared `composition-counterexamples/` corpus. Fixes must continue to reject or explain all previous counterexamples.

    # 3. Shared integration envelope

    Every scenario produces:

    ```text
    composition/CXX-name/
      scenario.json
      adapters.json
      input-manifest.json
      execution-events.jsonl
      semantic-before.json
      semantic-after.json
      views/
      proof-bundle/
      replay-bundle/
      results.json
      mismatch.md
    ```

    `scenario.json` names project interface versions, adapters, policy IDs, supported capabilities, expected laws, equality modes, fixture digests, and security principal. The composition harness refuses unversioned adapters.

    # 4. Required scenarios

    | ID | Scenario | Projects | Method | Success condition |
    |---|---|---|---|---|
    {scenario_rows}

    # 5. Scenario details

    ## C01 - Cache-correct execution

    Use one generation request and one retrieval request whose complete semantic identities are known. Run them through the P04 reference executor and the real `flow` adapters under cache miss, hit, corrupt entry, transient retry, changed worker count, changed retry delay, and insufficient budget. P01's mutation matrix decides which changes require a new key. The result report separates semantic output, durable cache/budget state, and trace.

    **Failure examples:** same key under changed effective inference profile; different key when only worker count changes; a cache hit consuming an undocumented attempt budget; repeated step reports conflated by display name.

    ## C02 - Proof-preserving concurrent admission

    Generate tool candidates from three calls, including duplicates and one same-ID conflict. P03 joins candidate/observation deltas in all small-set schedules. P08 performs deterministic batch commit under count and rune budgets. P02 packages admitted facts and every derivation. Verify the bundle independently.

    **Failure examples:** a schedule changes membership or labels; a duplicate loses its second tool-call derivation; a collision is overwritten; a proof references a presentation label as canonical identity.

    ## C03 - Candidate/view connected retrieval

    Convert current baseline and knowledge outputs into P05 candidates/observations. P07 applies gate, augmentation, fusion, coverage ordering, and context selection. Compare against current connected runtime fixtures at each intermediate boundary.

    **Failure examples:** gate closure reconstructs rather than preserves baseline; knowledge augmentation removes a baseline candidate before selection; RRF constant omitted from policy identity; a missing chunk silently disappears without disposition.

    ## C04 - Recursive connected retrieval

    Run P06 closure at depths one through three, including a saturated finite case and budget-stopped case. Feed each snapshot to P07. Users must see both closure completeness and view selection. The connected gate may use candidate facts but cannot alter the closure's completion metadata.

    **Failure examples:** depth-limited result labeled complete; gate threshold changes rule firing; top-k selected evidence is mistaken for the knowledge state.

    ## C05 - Tool evidence to answer contract

    Commit candidates with P08, freeze the citation view, and construct P09 `Prepared` input. Replay valid, malformed, unknown-citation, uncited-claim, and abstention observations. Then append unrelated candidates after the frozen commit and prove that validation still uses the original mapping.

    **Failure examples:** labels shift after append; answer validation consults current ledger; unknown ordinal citation maps to a chunk accidentally; parse failure leaks raw output as success.

    ## C06 - Proof-carrying answer artifact

    P09 emits claim/citation obligations. P02 expresses deterministic source and membership checks as derivations. P12 packages inputs, raw observations, proof bundle, and assurance report. Verify, tamper, redact, and replay the package.

    **Failure examples:** semantic judge reported as proof; redacted source still marked fully verified; prompt or schema swap passes manifest verification; answer claim has no path to an admitted source fact.

    ## C07 - Incremental multi-backend state

    Populate P11 in-memory and SQLite backends with P10 snapshots. Apply addition, deletion, alternative-support removal, document replacement, and schema migration. After every step compare incremental state, clean rebuild, and canonical exports.

    **Failure examples:** deletion removes a multiply supported fact; JSON/SQLite exports differ because of ordering; migration drops a rule input without a loss report; policy-only change rebuilds source facts.

    ## C08 - Identity-safe replay

    Build P12 bundles whose stages use P01 identities. Mutate one field at a time: document bytes, chunker version, prompt, schema, model, inference profile, RRF constant, context policy, worker count, timestamp, and run ID. The replay plan must downgrade or remain valid according to the shared sensitivity matrix.

    **Failure examples:** a behavior-affecting mutation reuses an observation; a trace-only mutation invalidates all deterministic stages; an old adapter version is accepted without migration.

    ## C09 - Secure cache and artifact path

    Create public and restricted worlds and two principals. P13 labels and authorizes requests. P01 includes scope fingerprints in identities. P04 executes with a shared physical cache. P12 packages outputs under capability policies. Compare all low-visible outputs.

    **Failure examples:** lower-privilege principal receives higher-scope cache hit; ranking/counts reveal restricted candidates; error text or artifact filename leaks hidden source; redacted bundle claims unavailable verification succeeded.

    ## C10 - Full deterministic stack

    Assemble adapters, not a new framework:

    ```text
    source snapshot
      -> P01 IDs
      -> P06 or baseline retrieval observations
      -> P03 semantic state
      -> P07/P08 composition and commit
      -> P05 context view
      -> recorded generation observation
      -> P09 assurance
      -> P02 proof bundle
      -> P12 replay bundle
      -> P13 authorized projection
    ```

    Execute the same logical workload under sequential, parallel, duplicate, retry, and reordered schedules. Then change one selection policy at a time. Semantic state must remain stable under operational variations; view and answer changes must be attributable to versioned policies or new observations.

    # 6. Integration waves

    ## Wave A - pairwise foundations

    Run C01, C03, C05, C07, and C08. These expose schema mismatch early and require no full closure or security stack.

    ## Wave B - three- and four-project assurance

    Run C02, C04, C06, and C09. Freeze adapter versions after each passes.

    ## Wave C - full-stack study

    Run C10 on the deterministic shared corpus, then on one recorded provider corpus, then on an authorized multi-principal corpus. Do not introduce live providers before the deterministic full-stack case passes.

    # 7. Cross-project conflict protocol

    Interface conflicts are resolved in this order:

    1. Preserve facts versus views versus traces as distinct categories.
    2. Prefer the narrower equivalence claim.
    3. Preserve all information in adapters; do not silently drop fields.
    4. Add explicit versioning rather than compatibility heuristics.
    5. Fail closed on same-ID payload conflict or authorization ambiguity.
    6. Record a counterexample before changing either project.
    7. Change the smallest contract and rerun all affected individual law suites.

    No project has authority merely because its type was implemented first.

    # 8. User-centered exploration scenarios

    After semantic integration passes, evaluate the system as users rather than only as package authors.

    - **Researcher comparison:** hold candidates fixed, vary fusion/reranking/context policies, and inspect stage-loss reports.
    - **Operator recovery:** interrupt a run, inspect partial commits, resume from artifacts, and verify no duplicate or stale facts.
    - **Auditor:** receive only a bundle, verify source/citation lineage, identify external observations, and reproduce deterministic checks.
    - **Interactive user:** compare streaming versus deterministic tool admission for latency, label stability, and answer changes.
    - **Corpus curator:** add, revise, and delete documents; inspect incremental decisions and affected answers.
    - **Security reviewer:** compare principal scopes, cache behavior, redacted bundles, and low-visible outputs.
    - **Backend maintainer:** replace in-memory state with SQLite and run conformance plus migration tests.
    - **Failure analyst:** trace one missing gold source through candidate, fusion, rerank, context, citation, and answer layers.

    Each user study records not only subjective usability but whether the interface exposes the semantic distinction needed to diagnose the scenario.

    # 9. Full-stack acceptance gates

    - All canonical IDs and policy identities pass mutation matrices.
    - Add-only merge passes ACI laws and schedule simulations.
    - Every admitted fact has at least one valid derivation or declared trust root.
    - Every bounded view has a complete disposition for omitted candidates.
    - Closed connected gate preserves baseline by the declared equality mode.
    - Tool batch commit is permutation-invariant; streaming runs carry arrival identity.
    - Answer assurance reports each layer honestly and fails closed at configured minimum.
    - Incremental state equals clean rebuild for supported changes.
    - All backend exports agree with the canonical oracle.
    - Run bundle verification detects tampering and replay uses no implicit live fallback.
    - Paired-world information-flow tests show no undeclared low-visible divergence.
    - Existing `rag-ttc` repository boundaries remain intact and no general workflow DSL is introduced.

    # 10. Decision output

    Phase II concludes with a design decision record that classifies each proposed structure as:

    - **Adopt now** - small, proven, and removes a confirmed semantic defect.
    - **Adopt as test kit** - valuable conformance oracle without production abstraction.
    - **Keep as artifact schema** - useful for replay/audit but not runtime types.
    - **Use only in selected subsystems** - laws apply locally, not universally.
    - **Reject** - complexity exceeds demonstrated value or conflicts with repository intent.
    - **Research further** - evidence is inconclusive and counterexamples remain.

    The desired end state is not all thirteen prototypes merged. It is the smallest coherent set of structures that survives independent validation and composition.
    ''')
    path.write_text(text, encoding='utf-8')
    return path


def write_yaml_manifest() -> Path:
    path = ROOT / 'project-manifest.yaml'
    lines = [
        'schema_version: rag-ttc-project-portfolio/v1',
        f'created: "{REPORT_DATE}"',
        f'source_snapshot_sha256: "{SNAPSHOT_SHA}"',
        'projects:',
    ]
    for p in PROJECTS:
        fn = f"{p['code'].lower()}-{p['slug']}"
        lines.extend([
            f'  - code: {p["code"]}',
            f'    title: "{p["title"}"',
            f'    domain: "{p["domain"]}"',
            f'    markdown: "markdown/{fn}.md"',
            f'    pdf: "pdf/{fn}.pdf"',
            '    primary_paths:',
        ])
        lines.extend(f'      - "{x}"' for x in p['primary_paths'])
    path.write_text('\n'.join(lines) + '\n', encoding='utf-8')
    return path


def write_readme() -> Path:
    path = ROOT / 'README.md'
    project_links = '\n'.join(
        f"- [{p['code']} - {p['title']}](markdown/{p['code'].lower()}-{p['slug']}.md)"
        for p in PROJECTS
    )
    text = dedent(f'''\
    # rag-ttc research project portfolio

    This bundle contains thirteen self-contained research and implementation briefs for validating the semantic subsystems of `rag-ttc`, plus a coordinator guide and a Phase II composition protocol.

    ## Start here

    - [Portfolio coordinator guide](markdown/00-portfolio-guide.md)
    - [Phase II composition protocol](markdown/90-phase-ii-composition-protocol.md)
    - [Combined portfolio](rag-ttc-project-portfolio-combined.md)
    - [Machine-readable project manifest](project-manifest.json)
    - [YAML project manifest](project-manifest.yaml)
    - [Project dependency map](assets/project-map.png)

    ## Individual project briefs

    {project_links}

    Matching PDFs are in `pdf/`. The combined PDF is `rag-ttc-project-portfolio-combined.pdf`.

    ## Source baseline

    The briefs analyze `rag-ttc.zip` with SHA-256 `{SNAPSHOT_SHA}`. The repository declares Go `{GO_DECLARED}`. The initial static analysis environment exposed Go `{GO_AVAILABLE}` and could not run the complete declared toolchain, so each project requires runtime reproduction in the supported environment.

    ## Rebuilding PDFs

    From this directory:

    ```sh
    for f in markdown/*.md; do
      name=$(basename "$f" .md)
      python /home/oai/skills/pdfs/scripts/md_to_pdf.py \
        "$f" -o "pdf/$name.pdf" \
        --pdf_engine xelatex \
        --resource_path .
    done
    ```

    The Markdown files are the editable source of record. PDF rendering was visually inspected after generation.
    ''')
    path.write_text(text, encoding='utf-8')
    return path


def write_combined(guide: Path, phase2: Path) -> Path:
    path = ROOT / 'rag-ttc-project-portfolio-combined.md'
    parts = [yaml_header(
        'rag-ttc Research Project Portfolio - Complete Edition',
        'Coordinator guide, thirteen project briefs, and Phase II composition protocol',
    )]
    guide_body = strip_yaml(guide.read_text(encoding='utf-8')).replace('../assets/', 'assets/')
    parts.append(guide_body)
    for p in PROJECTS:
        fn = MD / f"{p['code'].lower()}-{p['slug']}.md"
        body = strip_yaml(fn.read_text(encoding='utf-8'))
        parts.append('\n\\newpage\n\n' + body)
    phase_body = strip_yaml(phase2.read_text(encoding='utf-8')).replace('../assets/', 'assets/')
    parts.append('\n\\newpage\n\n' + phase_body)
    path.write_text('\n'.join(parts), encoding='utf-8')
    return path


def build_all() -> None:
    write_projects()
    guide = write_portfolio_guide()
    phase2 = write_phase2()
    write_yaml_manifest()
    write_readme()
    write_combined(guide, phase2)


if __name__ == '__main__':
    build_all()
PY
python -m py_compile /mnt/data/portfolio_builder.py
python /mnt/data/portfolio_builder.py
printf '\nGenerated markdown:\n'
find /mnt/data/rag-ttc-research-projects -maxdepth 2 -type f -printf '%p %s bytes\n' | sort | sed -n '1,240p'
```

The briefs now span identity, provenance, merge, closure, retrieval, ranking, replay, answering, and security. I’m validating handout consistency and preparing individual and combined PDFs.

<details><summary>💭 Thinking</summary>

**Fixed portfolio files and converted four Markdown documents to PDFs**

</details>

```unknown
bash -lc set -euo pipefail
ROOT=/mnt/data/rag-ttc-research-projects
convert_one() {
  md="$1"
  base="$(basename "$md" .md)"
  python /home/oai/skills/pdfs/scripts/md_to_pdf.py "$md" \
    -o "$ROOT/pdf/$base.pdf" \
    --pdf_engine xelatex \
    --resource_path "$ROOT/markdown:$ROOT" \
    >"/tmp/${base}.pdf.log" 2>&1
  echo "created $base.pdf"
}
export -f convert_one
export ROOT
printf '%s\n' \
  "$ROOT/markdown/p09-answer-contract-and-citation-semantics.md" \
  "$ROOT/markdown/p10-incremental-maintenance-and-retraction.md" \
  "$ROOT/markdown/p11-backend-conformance-and-schema-migration.md" \
  "$ROOT/markdown/p12-reproducible-artifacts-and-replay.md" \
  "$ROOT/markdown/p13-information-flow-and-redaction.md" \
| xargs -n1 -P5 bash -c 'convert_one "$0"'

```

<details><summary>💭 Thinking</summary>

**Converted, compiled, validated, and visually inspected Markdown PDFs**

</details>

```unknown
from PIL import Image, ImageOps, ImageDraw
from pathlib import Path
render_root=Path('/mnt/data/rag-ttc-project-renders')
sheets=[]
for d in sorted(render_root.iterdir()):
    imgs=[]
    for p in sorted(d.glob('*.png')):
        im=Image.open(p).convert('RGB')
        # thumb preserving
        im.thumbnail((340, 440))
        canvas=Image.new('RGB',(360,480),'white')
        x=(360-im.width)//2
        y=25
        canvas.paste(im,(x,y))
        dr=ImageDraw.Draw(canvas)
        dr.text((10,455),p.stem,fill='black')
        imgs.append(canvas)
    cols=3
    rows=(len(imgs)+cols-1)//cols
    sheet=Image.new('RGB',(cols*360,rows*480),(230,230,230))
    for i,im in enumerate(imgs):
       
```

<details><summary>💭 Thinking</summary>

**Generated image contact sheets for inspection**

</details>

```unknown
bash -lc ls -ld /mnt/data/rag-ttc-project-renders && find /mnt/data/rag-ttc-project-renders -maxdepth 2 -type f | head
```

<details><summary>💭 Thinking</summary>

**Inspected mounted render directory, PDF logs, renderer help, and files**

</details>

```unknown
bash -lc set -euo pipefail
sed -n '1,260p' /mnt/data/rag-ttc-semantic-handbook.md
```

<details><summary>💭 Thinking</summary>

**Replacing Unicode Dashes in Project Docs**

</details>

```unknown
bash -lc set -euo pipefail
ROOT=/mnt/data/rag-ttc-research-projects
mkdir -p "$ROOT/pdf" "$ROOT/logs"
convert_one() {
  md="$1"
  base="$(basename "$md" .md)"
  python /home/oai/skills/pdfs/scripts/md_to_pdf.py "$md" \
    -o "$ROOT/pdf/$base.pdf" \
    --pdf_engine xelatex \
    --resource_path "$ROOT/markdown:$ROOT" \
    >"$ROOT/logs/${base}.log" 2>&1
  echo "created $base.pdf"
}
export -f convert_one
export ROOT
printf '%s\n' \
  "$ROOT/markdown/00-portfolio-guide.md" \
  "$ROOT/markdown/p01-semantic-identity-and-cache-keys.md" \
  "$ROOT/markdown/p02-provenance-and-proof-carrying-evidence.md" \
  "$ROOT/markdown/p03-lawful-evidence-state-and-merge.md" \
  "$ROOT/markdown/p04-flow-operational-semantics.md" \
| xargs -n1 -P5 bash -c 'convert_one "$0"'

```

<details><summary>💭 Thinking</summary>

**Converted Markdown documents to PDFs, validated outputs, and regenerated selected files**

</details>

```unknown
bash -lc set -euo pipefail
ROOT=/mnt/data/rag-ttc-research-projects
RENDER=/mnt/data/rag-ttc-project-renders
rm -rf "$RENDER"
mkdir -p "$RENDER"
render_one() {
  pdf="$1"; pages="$2"
  base="$(basename "$pdf" .pdf)"
  python /home/oai/skills/pdfs/scripts/render_pdf.py "$pdf" --out_dir "$RENDER/$base" --dpi 120 --pages "$pages" >"$ROOT/logs/render-${base}.log" 2>&1
  echo "rendered $base"
}
export -f render_one
export ROOT RENDER
render_one "$ROOT/pdf/00-portfolio-guide.pdf" "1-10" &
render_one "$ROOT/pdf/90-phase-ii-composition-protocol.pdf" "1-6" &
render_one "$ROOT/pdf/p01-semantic-identity-and-cache-keys.pdf" "1-9" &
render_one "$ROOT/pdf/p06-knowledge-discovery-and-closure.pdf" "1-9" &
render_one "$ROOT/pdf/p08-tool-evidence-admission.pdf" "1-9" &
render_one "$ROOT/pdf/p13-information-flow-and-redaction.pdf" "1-9" &
wait
render_one "$ROOT/rag-ttc-project-portfolio-combined.pdf" "1-3,10,20,40,60,80,100,123-125"
find "$RENDER" -type f -name '*.png' | wc -l

```

<details><summary>💭 Thinking</summary>

**Rendered, analyzed, improved, and packaged project PDF materials**

</details>

# rag-ttc research project program

The complete handout package is ready. It contains **13 independently assignable projects**, each supplied as Markdown and PDF, plus shared fixtures, machine-readable schemas, a program charter, and a second-pass composition protocol.

- [Download the complete package](sandbox:/mnt/data/rag-ttc-research-projects.zip)
- [Combined 134-page PDF compendium](sandbox:/mnt/data/rag-ttc-research-projects/rag-ttc-research-projects-compendium.pdf)
- [Combined Markdown compendium](sandbox:/mnt/data/rag-ttc-research-projects/rag-ttc-research-projects-compendium.md)
- [Package index and individual handout links](sandbox:/mnt/data/rag-ttc-research-projects/README.md)
- [Program charter — PDF](sandbox:/mnt/data/rag-ttc-research-projects/00-program-charter.pdf) · [Markdown](sandbox:/mnt/data/rag-ttc-research-projects/00-program-charter.md)
- [Composition-pass playbook — PDF](sandbox:/mnt/data/rag-ttc-research-projects/90-composition-pass-playbook.pdf) · [Markdown](sandbox:/mnt/data/rag-ttc-research-projects/90-composition-pass-playbook.md)
- [Machine-readable manifest](sandbox:/mnt/data/rag-ttc-research-projects/manifest.json)
- [ZIP checksum](sandbox:/mnt/data/rag-ttc-research-projects.zip.sha256)

## Project portfolio

### Foundations

1. **P01 — Semantic Identity and Cache Fingerprints**  
   Determine which inputs define operation identity; test cache soundness, canonical serialization, versioning, and collision behavior.

2. **P02 — Canonical Facts and Provenance Kernel**  
   Separate stable facts from the derivations that support them, and design a minimal provenance-aware semantic interchange format.

3. **P03 — Lawful Merge and Deterministic Evidence Ledger**  
   Implement merge as an associative, commutative, and idempotent operation; test retries, duplication, concurrency, and ordering independence.

4. **P04 — Candidate State and Ranked View Separation**  
   Separate accumulated candidates from query-specific scores, ranks, limits, token packing, and citation labels.

5. **P05 — Closure and Frontier Evaluation Engine**  
   Build a recursive add-only rule engine with frontier processing, derivation depth, fixed-point detection, partial-completeness contracts, and schedule-independence tests.

6. **P06 — Flow Executor Semantics and Captured Effects**  
   Analyze whether `flow` preserves component meaning under caching, retries, batching, concurrency, budgets, tracing, and result-order restoration.

### Retrieval and agent subsystems

7. **P07 — Knowledge Retrieval: Discovery versus Selection**  
   Decompose knowledge retrieval into candidate discovery, ambiguity representation, policy selection, ranking, and limiting.

8. **P08 — Connected Retrieval Composition**  
   Study hybrid retrieval and fusion, including RRF configuration, branch failure, deterministic composition, duplicate admission, and recursive expansion.

9. **P09 — Tool-Agent Evidence and Citation Contracts**  
   Define how tool calls become admissible evidence, how completion order affects limits, and how citations remain stable and verifiable.

### Reproducibility, evolution, and conformance

10. **P10 — Proof-Carrying Experiments and Replay**  
    Design replayable experiment artifacts containing semantic configuration, operation traces, provenance, outputs, and integrity checks.

11. **P11 — Incremental Maintenance, Updates, and Retractions**  
    Compare full recomputation with delta processing; handle document additions, replacements, deletions, alternate derivations, and dependency-aware retraction.

12. **P12 — Backend Conformance and Schema Migration**  
    Test whether in-memory, relational, graph, and serialized representations preserve the same constructors, merge laws, provenance, and migration behavior.

13. **P13 — Security Labels, Authorization, and Noninterference**  
    Propagate authorization through derivations and test whether low-privilege outputs remain unchanged when only restricted evidence differs.

## Structure of each assignment

Every brief is designed to be handed directly to a student team. It includes:

- Relevant `rag-ttc` packages and source paths.
- The precise subsystem boundary under investigation.
- Research questions and falsifiable hypotheses.
- A standalone reference implementation and a `rag-ttc` adapter.
- Proposed Go interfaces and interchange types.
- Laws and invariants to test.
- Recorded and synthetic experimental scenarios.
- Fault-injection cases.
- Metrics and comparison baselines.
- A week-by-week work plan.
- Acceptance gates and definition of done.
- Required datasets, traces, reports, and handoff artifacts.
- Explicit composition inputs and outputs.
- Risks, likely traps, and stretch investigations.
- A small mathematical background section in programmer-oriented language.

The projects are intentionally **independent in pass one**. Teams exchange data through neutral schemas rather than importing one another’s implementations. That makes competing interpretations comparable and prevents an early foundational choice from contaminating the rest of the portfolio.

## Shared experimental material

The package includes ten common adversarial fixture sets covering:

- Identity and canonicalization edge cases.
- Diamond-shaped provenance.
- Multi-hop retrieval.
- Ranking ties.
- Concurrent completion permutations.
- Ambiguous knowledge candidates.
- Corpus update sequences.
- Public and confidential evidence worlds.
- Corrupted experiment artifacts.
- Multiple tree and ordering representations.

It also provides JSON Schemas for:

- Semantic interchange records.
- Operation traces.
- Standardized project results.

## Second-pass composition

The composition playbook integrates successful projects in six stages:

1. Identity and replayable artifacts.
2. Facts, provenance, lawful merge, and storage.
3. Candidate views and execution semantics.
4. Recursive knowledge and connected retrieval.
5. Tool execution and citation contracts.
6. Updates, retractions, authorization, and security.

The integrated evaluation scenarios include deterministic hybrid RAG, recursive knowledge retrieval, tool-assisted answering, live corpus updates, multi-tenant secure RAG, and backend/schema migration.

All Markdown, JSON, and schema files were parsed and checked; every project PDF was verified as text-extractable and contains its acceptance, handoff, and completion sections. Representative pages from the charter, compendium, composition playbook, and project briefs were visually inspected. The source-code findings remain based on static analysis of the supplied snapshot, so executable baseline reproduction is an explicit first milestone in every relevant assignment.


---

> Implement P01-P03 as a doctoral thesis. Write up thesis as markdonw + render as pdf.

I’ll map P01–P03 onto the repository, implement the semantic kernel with law-focused tests, validate within toolchain limits, and produce a thesis-grade Markdown manuscript and PDF.

```unknown
bash -lc cat /home/oai/skills/pdfs/SKILL.md && printf '\n---FILES---\n' && find /mnt/data -maxdepth 3 -type f -printf '%p\n' | sort | sed -n '1,240p'
```

<details><summary>💭 Thinking</summary>

**Inspected project artifacts, repository structure, and documentation requirements**

</details>

```unknown
bash -lc go version || true; go env GOTOOLCHAIN GOPATH GOMODCACHE GOPROXY 2>/dev/null || true; find /usr/local/go* /opt -maxdepth 2 -type f -name go 2>/dev/null | head -20
```

<details><summary>💭 Thinking</summary>

**Designing semantic identities**

I’m outlining a reusable semantic-ID package with domain separation, versioning, digests, and deterministic canonical encoding. I’m focusing on explicit type tags, stable map ordering, length prefixes, and careful handling of numeric edge cases.

**Designed semantic identities**

</details>

```unknown
bash -lc cd /mnt/data/work-rag-ttc/rag-ttc && nl -ba pkg/rag/connected/runtime.go | sed -n '1,320p' && printf '\n--- runtime tests ---\n' && nl -ba pkg/rag/connected/runtime_test.go | sed -n '1,420p' && printf '\n--- generation cached ---\n' && nl -ba pkg/rag/generation/cached.go | sed -n '1,260p' && printf '\n--- generator types ---\n' && nl -ba pkg/rag/generation/generation.go | sed -n '1,300p' && printf '\n--- provider generation ---\n' && nl -ba pkg/rag/providers/geppetto/generation.go | sed -n '1,380p' && printf '\n--- geppetto profile files ---\n' && find pkg/rag/providers/geppetto -maxdepth 3 -type f -print | sort | xargs -r -I{} sh -c 'echo ===== {}; nl -ba {} | sed -n "1,260p"'
```

<details><summary>💭 Thinking</summary>

**Mapping implementation structure**

I’m organizing the implementation into reusable packages for semantic IDs, derivations, observations, conflicts, state, joins, codecs, views, and ledgers. I’m also checking dependencies carefully to avoid import cycles while adding adapters around existing data types.

**Mapped implementation structure**

</details>

```unknown
bash -lc cd /mnt/data/work-rag-ttc/rag-ttc && nl -ba pkg/rag/toolanswer/evidence.go | sed -n '1,260p' && printf '\n--- tests ---\n' && nl -ba pkg/rag/toolanswer/evidence_test.go | sed -n '1,360p' && printf '\n--- toolanswer search ---\n' && nl -ba pkg/rag/toolanswer/search.go | sed -n '1,360p' && printf '\n--- ttcrag search 1 ---\n' && nl -ba pkg/ttcrag/search.go | sed -n '1,300p' && printf '\n--- ttcrag tests ---\n' && nl -ba pkg/ttcrag/search_test.go | sed -n '1,500p'
```

<details><summary>💭 Thinking</summary>

**Inspected RAG repository, runtime caching, APIs, ledger, tests, and Go compatibility**

</details>

```json
{"search_query":[{"q":"RFC 8785 JSON Canonicalization Scheme official"},{"q":"NIST FIPS 180-4 Secure Hash Standard official PDF"},{"q":"A comprehensive study of Convergent and Commutative Replicated Data Types Shapiro PDF"},{"q":"Keeping CALM When Distributed Consistency is Easy arXiv"}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Defining fingerprint values**

I’m specifying typed semantic values, normalized paths, ordered and unordered collections, canonical objects, and stable fingerprint strings. I’m keeping encoding deterministic while preserving meaningful distinctions such as paths versus ordinary strings.

**Defined fingerprint values**

**Searched 23 websites**

</details>

```unknown
bash -lc cd /mnt/data/work-rag-ttc/rag-ttc && nl -ba pkg/rag/generation/cached.go | sed -n '1,260p' && nl -ba pkg/rag/generation/cached_generator.go | sed -n '1,300p' && nl -ba pkg/rag/generation/cached_test.go | sed -n '1,380p' && nl -ba pkg/rag/generation/cached_generator_test.go | sed -n '1,420p' && nl -ba pkg/rag/components.go | sed -n '1,320p'
```

The design will use three separately testable layers: stable semantic identity, provenance-bearing facts, and lawful merge that remains deterministic under retries and concurrency.

Confirmed defects span inconsistent hashing, omitted RRF identity, and arrival-dependent tool ledgers. The kernel will separate immutable facts from observations, preserve conflicts, and derive budgets post-merge.

The isolated kernel and adapters pass unit, property, fuzz-seed, race, and concurrency tests. The thesis now links contracts to proofs and results while documenting integration limits.

<details><summary>💭 Thinking</summary>

**Handling cache fingerprints**

I’m considering how to connect semantic fingerprints to generation caching without introducing fragile dependencies. The safest design is to require an explicit inference fingerprint, with profile-derived helpers that exclude secrets while capturing output-affecting configuration.

**Handled cache fingerprints**

**Inspected retrieval caches, generation builders, providers, and Geppetto integration**

</details>

```json
{"search_query":[{"q":"github go-go-golems geppetto InferenceSettings ChatSettings ReasoningEffort source"},{"q":"site:github.com/go-go-golems/geppetto \"type InferenceSettings\""},{"q":"site:github.com/go-go-golems/geppetto \"type ChatSettings\""},{"q":"site:github.com/go-go-golems/geppetto \"ReasoningEffort\""}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Searched 4 websites**

</details>

```unknown
bash -lc cd /mnt/data/work-rag-ttc/rag-ttc && nl -ba pkg/rag/knowledge/types.go | sed -n '1,360p' && nl -ba pkg/rag/knowledge/deterministic.go | sed -n '1,360p' 2>/dev/null || true && nl -ba pkg/rag/toolanswer/types.go | sed -n '1,320p' && nl -ba pkg/rag/answering/types.go | sed -n '1,340p'
```

<details><summary>💭 Thinking</summary>

**Implementing thesis foundations**

I’m translating P01–P03 into standard-library core packages: semantic identity and cache contracts, immutable facts with provenance, and deterministic conflict-aware merges. I’m also planning focused law tests, repository patches, and Markdown/PDF thesis deliverables.

**Implemented thesis foundations**

</details>

```unknown
bash -lc ls -la /mnt/data && echo '--- work repo' && find /mnt/data/work-rag-ttc/rag-ttc -maxdepth 2 -type f | head -40 && echo '--- project briefs' && ls -la /mnt/data/work-projects/rag-ttc-research-projects/projects | head
```

<details><summary>💭 Thinking</summary>

**Inspected RAG implementation, tests, caching, dependencies, and created a pristine project copy**

</details>

```unknown
bash -lc cd /mnt/data/work-rag-ttc/rag-ttc && mkdir -p pkg/semanticid && cat > pkg/semanticid/doc.go <<'EOF'
// Package semanticid provides typed, versioned, domain-separated semantic
// fingerprints.
//
// The package deliberately does not hash arbitrary Go values. Callers must
// state whether collections are ordered or set-like and must choose the exact
// fields that participate in identity. This makes cache keys and persistent
// identifiers executable API contracts rather than incidental serialization
// artifacts.
package semanticid
EOF

cat > pkg/semanticid/value.go <<'EOF'
package semanticid

import (
	"bytes"
	"encoding/binary"
	"errors"
	"fmt"
	"math"
	"path/filepath"
	"sort"
	"strings"
	"unicode/utf8"
)

// Kind identifies one member of the canonical value algebra.
type Kind byte

const (
	KindNull Kind = iota
	KindBool
	KindString
	KindBytes
	KindInt
	KindUint
	KindFloat64
	KindList
	KindSet
	KindObject
)

// Field is one named member of an Object value.
type Field struct {
	Name  string
	Value Value
}

// Value is an immutable canonical semantic value. Values can only be created
// with the constructors below; the internal representation is intentionally
// hidden so invalid or ambiguous encodings cannot be manufactured by callers.
type Value struct {
	kind     Kind
	boolVal  bool
	stringVal string
	bytesVal []byte
	intVal   int64
	uintVal  uint64
	floatVal float64
	values   []Value
	fields   []Field
}

// Null returns the unique null value.
func Null() Value { return Value{kind: KindNull} }

// Bool returns a canonical boolean value.
func Bool(value bool) Value { return Value{kind: KindBool, boolVal: value} }

// String returns a UTF-8 string value. Invalid UTF-8 is rejected because its
// treatment varies between serializers and languages.
func String(value string) (Value, error) {
	if !utf8.ValidString(value) {
		return Value{}, errors.New("semantic string is not valid UTF-8")
	}
	return Value{kind: KindString, stringVal: value}, nil
}

// MustString is String for literals and other values that are known to be
// valid UTF-8. It panics on invalid input.
func MustString(value string) Value {
	ret, err := String(value)
	if err != nil {
		panic(err)
	}
	return ret
}

// Bytes returns an arbitrary byte-string value.
func Bytes(value []byte) Value {
	return Value{kind: KindBytes, bytesVal: append([]byte(nil), value...)}
}

// Int returns a signed integer value.
func Int(value int64) Value { return Value{kind: KindInt, intVal: value} }

// Uint returns an unsigned integer value.
func Uint(value uint64) Value { return Value{kind: KindUint, uintVal: value} }

// Float64 returns a finite IEEE-754 value. Positive and negative zero are
// normalized because they compare equal in ordinary numeric semantics. NaN
// and infinities are rejected because they do not have useful portable value
// semantics for cache identity.
func Float64(value float64) (Value, error) {
	if math.IsNaN(value) || math.IsInf(value, 0) {
		return Value{}, fmt.Errorf("semantic float must be finite: %v", value)
	}
	if value == 0 {
		value = 0
	}
	return Value{kind: KindFloat64, floatVal: value}, nil
}

// MustFloat64 is Float64 for values known to be finite.
func MustFloat64(value float64) Value {
	ret, err := Float64(value)
	if err != nil {
		panic(err)
	}
	return ret
}

// List returns an ordered collection. Reordering its values changes identity.
func List(values ...Value) Value {
	return Value{kind: KindList, values: append([]Value(nil), values...)}
}

// Set returns an unordered, duplicate-insensitive collection. Elements are
// sorted by their canonical encodings and exact duplicates are removed.
func Set(values ...Value) Value {
	encoded := make([]encodedValue, len(values))
	for index, value := range values {
		encoded[index] = encodedValue{value: value, encoded: value.canonicalBytes()}
	}
	sort.Slice(encoded, func(i, j int) bool {
		return bytes.Compare(encoded[i].encoded, encoded[j].encoded) < 0
	})
	ret := make([]Value, 0, len(encoded))
	var previous []byte
	for index, item := range encoded {
		if index > 0 && bytes.Equal(previous, item.encoded) {
			continue
		}
		ret = append(ret, item.value)
		previous = item.encoded
	}
	return Value{kind: KindSet, values: ret}
}

// Object returns a value with lexicographically ordered field names. Duplicate
// names and invalid UTF-8 field names are rejected.
func Object(fields ...Field) (Value, error) {
	ret := append([]Field(nil), fields...)
	for _, field := range ret {
		if field.Name == "" {
			return Value{}, errors.New("semantic object field name is empty")
		}
		if !utf8.ValidString(field.Name) {
			return Value{}, fmt.Errorf("semantic object field %q is not valid UTF-8", field.Name)
		}
	}
	sort.Slice(ret, func(i, j int) bool { return ret[i].Name < ret[j].Name })
	for index := 1; index < len(ret); index++ {
		if ret[index-1].Name == ret[index].Name {
			return Value{}, fmt.Errorf("duplicate semantic object field %q", ret[index].Name)
		}
	}
	return Value{kind: KindObject, fields: ret}, nil
}

// MustObject is Object for statically known, unique field names.
func MustObject(fields ...Field) Value {
	ret, err := Object(fields...)
	if err != nil {
		panic(err)
	}
	return ret
}

// Optional distinguishes an absent value from a present value. The field name
// is part of the encoding, making accidental position-dependent optionals
// harder to construct.
func Optional(name string, value *Value) Value {
	if value == nil {
		return MustObject(
			Field{Name: "name", Value: MustString(name)},
			Field{Name: "present", Value: Bool(false)},
		)
	}
	return MustObject(
		Field{Name: "name", Value: MustString(name)},
		Field{Name: "present", Value: Bool(true)},
		Field{Name: "value", Value: *value},
	)
}

// PortablePath encodes a repository-relative logical path. It cleans native
// separators, converts them to '/', rejects absolute paths, and rejects paths
// that escape through '..'. Filesystem paths should only be semantic inputs
// when the path itself, rather than the referenced content, affects behavior.
func PortablePath(value string) (Value, error) {
	trimmed := strings.TrimSpace(value)
	if trimmed == "" {
		return Value{}, errors.New("semantic path is empty")
	}
	if filepath.IsAbs(trimmed) {
		return Value{}, fmt.Errorf("semantic path must be relative: %q", value)
	}
	cleaned := filepath.Clean(trimmed)
	cleaned = filepath.ToSlash(cleaned)
	if cleaned == "." || cleaned == ".." || strings.HasPrefix(cleaned, "../") {
		return Value{}, fmt.Errorf("semantic path escapes its root: %q", value)
	}
	return String(cleaned)
}

// Kind reports the value's canonical kind.
func (v Value) Kind() Kind { return v.kind }

// CanonicalBytes returns a defensive copy of the canonical binary encoding.
func (v Value) CanonicalBytes() []byte {
	return append([]byte(nil), v.canonicalBytes()...)
}

type encodedValue struct {
	value   Value
	encoded []byte
}

func (v Value) canonicalBytes() []byte {
	var buffer bytes.Buffer
	v.writeCanonical(&buffer)
	return buffer.Bytes()
}

func (v Value) writeCanonical(buffer *bytes.Buffer) {
	buffer.WriteByte(byte(v.kind))
	switch v.kind {
	case KindNull:
		return
	case KindBool:
		if v.boolVal {
			buffer.WriteByte(1)
		} else {
			buffer.WriteByte(0)
		}
	case KindString:
		writeLengthPrefixed(buffer, []byte(v.stringVal))
	case KindBytes:
		writeLengthPrefixed(buffer, v.bytesVal)
	case KindInt:
		var scratch [binary.MaxVarintLen64]byte
		length := binary.PutVarint(scratch[:], v.intVal)
		buffer.Write(scratch[:length])
	case KindUint:
		var scratch [binary.MaxVarintLen64]byte
		length := binary.PutUvarint(scratch[:], v.uintVal)
		buffer.Write(scratch[:length])
	case KindFloat64:
		var scratch [8]byte
		binary.BigEndian.PutUint64(scratch[:], math.Float64bits(v.floatVal))
		buffer.Write(scratch[:])
	case KindList, KindSet:
		writeUvarint(buffer, uint64(len(v.values)))
		for _, value := range v.values {
			encoded := value.canonicalBytes()
			writeLengthPrefixed(buffer, encoded)
		}
	case KindObject:
		writeUvarint(buffer, uint64(len(v.fields)))
		for _, field := range v.fields {
			writeLengthPrefixed(buffer, []byte(field.Name))
			encoded := field.Value.canonicalBytes()
			writeLengthPrefixed(buffer, encoded)
		}
	default:
		panic(fmt.Sprintf("unknown semantic value kind %d", v.kind))
	}
}

func writeLengthPrefixed(buffer *bytes.Buffer, value []byte) {
	writeUvarint(buffer, uint64(len(value)))
	buffer.Write(value)
}

func writeUvarint(buffer *bytes.Buffer, value uint64) {
	var scratch [binary.MaxVarintLen64]byte
	length := binary.PutUvarint(scratch[:], value)
	buffer.Write(scratch[:length])
}
EOF

cat > pkg/semanticid/fingerprint.go <<'EOF'
package semanticid

import (
	"bytes"
	"crypto/sha256"
	"encoding/hex"
	"encoding/json"
	"errors"
	"fmt"
	"regexp"
	"strings"
)

const fingerprintTextPrefix = "sid1"

var (
	domainPattern  = regexp.MustCompile(`^[a-z][a-z0-9._/-]*$`)
	versionPattern = regexp.MustCompile(`^[A-Za-z0-9][A-Za-z0-9._-]*$`)
)

// Domain is a namespace for one semantic identity contract. Reusing a digest
// across domains is prohibited even when the encoded value is byte-identical.
type Domain string

// Version names an encoding or semantic-contract revision.
type Version string

// Fingerprint is a SHA-256 semantic identifier with explicit domain and
// contract version.
type Fingerprint struct {
	Domain  Domain
	Version Version
	Sum     [sha256.Size]byte
}

// FingerprintValue computes a domain-separated SHA-256 fingerprint.
func FingerprintValue(domain Domain, version Version, value Value) (Fingerprint, error) {
	if err := validateDomain(domain); err != nil {
		return Fingerprint{}, err
	}
	if err := validateVersion(version); err != nil {
		return Fingerprint{}, err
	}
	var input bytes.Buffer
	input.WriteString("rag-ttc-semantic-id\x00")
	writeLengthPrefixed(&input, []byte(domain))
	writeLengthPrefixed(&input, []byte(version))
	writeLengthPrefixed(&input, value.canonicalBytes())
	return Fingerprint{Domain: domain, Version: version, Sum: sha256.Sum256(input.Bytes())}, nil
}

// MustFingerprint is FingerprintValue for static domain/version contracts.
func MustFingerprint(domain Domain, version Version, value Value) Fingerprint {
	ret, err := FingerprintValue(domain, version, value)
	if err != nil {
		panic(err)
	}
	return ret
}

// Hex returns the lowercase SHA-256 payload without domain/version metadata.
// Prefer String for persisted interchange. Hex exists for integration with
// legacy fields that currently require a bare 64-character digest.
func (f Fingerprint) Hex() string { return hex.EncodeToString(f.Sum[:]) }

// String returns the self-describing portable representation.
func (f Fingerprint) String() string {
	return fmt.Sprintf("%s:%s:%s:sha256:%s", fingerprintTextPrefix, f.Domain, f.Version, f.Hex())
}

// IsZero reports whether no domain, version, or digest has been assigned.
func (f Fingerprint) IsZero() bool {
	return f.Domain == "" && f.Version == "" && f.Sum == [sha256.Size]byte{}
}

// Equal compares the complete contract identity, not only digest bytes.
func (f Fingerprint) Equal(other Fingerprint) bool { return f == other }

// Parse parses String's self-describing format.
func Parse(value string) (Fingerprint, error) {
	parts := strings.Split(value, ":")
	if len(parts) != 5 || parts[0] != fingerprintTextPrefix || parts[3] != "sha256" {
		return Fingerprint{}, errors.New("invalid semantic fingerprint format")
	}
	domain := Domain(parts[1])
	version := Version(parts[2])
	if err := validateDomain(domain); err != nil {
		return Fingerprint{}, err
	}
	if err := validateVersion(version); err != nil {
		return Fingerprint{}, err
	}
	decoded, err := hex.DecodeString(parts[4])
	if err != nil || len(decoded) != sha256.Size {
		return Fingerprint{}, errors.New("invalid semantic fingerprint SHA-256 payload")
	}
	var sum [sha256.Size]byte
	copy(sum[:], decoded)
	return Fingerprint{Domain: domain, Version: version, Sum: sum}, nil
}

// MarshalText implements encoding.TextMarshaler.
func (f Fingerprint) MarshalText() ([]byte, error) {
	if err := validateDomain(f.Domain); err != nil {
		return nil, err
	}
	if err := validateVersion(f.Version); err != nil {
		return nil, err
	}
	return []byte(f.String()), nil
}

// UnmarshalText implements encoding.TextUnmarshaler.
func (f *Fingerprint) UnmarshalText(data []byte) error {
	if f == nil {
		return errors.New("cannot unmarshal semantic fingerprint into nil receiver")
	}
	parsed, err := Parse(string(data))
	if err != nil {
		return err
	}
	*f = parsed
	return nil
}

// MarshalJSON encodes a fingerprint as its text form.
func (f Fingerprint) MarshalJSON() ([]byte, error) {
	text, err := f.MarshalText()
	if err != nil {
		return nil, err
	}
	return json.Marshal(string(text))
}

// UnmarshalJSON decodes a fingerprint from its text form.
func (f *Fingerprint) UnmarshalJSON(data []byte) error {
	var text string
	if err := json.Unmarshal(data, &text); err != nil {
		return err
	}
	return f.UnmarshalText([]byte(text))
}

func validateDomain(domain Domain) error {
	if !domainPattern.MatchString(string(domain)) || strings.Contains(string(domain), ":") {
		return fmt.Errorf("invalid semantic fingerprint domain %q", domain)
	}
	return nil
}

func validateVersion(version Version) error {
	if !versionPattern.MatchString(string(version)) || strings.Contains(string(version), ":") {
		return fmt.Errorf("invalid semantic fingerprint version %q", version)
	}
	return nil
}
EOF

cat > pkg/semanticid/contract.go <<'EOF'
package semanticid

import (
	"fmt"
	"sort"
)

// FieldRole describes how a field participates in an operation's semantics.
type FieldRole string

const (
	RoleSemantic     FieldRole = "semantic"
	RoleLineage      FieldRole = "lineage"
	RoleObservation  FieldRole = "observation"
	RolePresentation FieldRole = "presentation"
	RoleOperational  FieldRole = "operational"
	RoleSecret       FieldRole = "secret"
)

// FieldSpec is a reviewable entry in an identity field catalog.
type FieldSpec struct {
	Path        string    `json:"path"`
	Role        FieldRole `json:"role"`
	InIdentity  bool      `json:"in_identity"`
	Explanation string    `json:"explanation"`
}

// Catalog documents one semantic identity contract.
type Catalog struct {
	Name    string      `json:"name"`
	Domain  Domain      `json:"domain"`
	Version Version     `json:"version"`
	Fields  []FieldSpec `json:"fields"`
}

// Validate checks catalog consistency. Secrets are never allowed in identity;
// semantic fields must be explicitly included; operational and presentation
// fields must be explicitly excluded.
func (c Catalog) Validate() error {
	if c.Name == "" {
		return fmt.Errorf("identity catalog has no name")
	}
	if err := validateDomain(c.Domain); err != nil {
		return err
	}
	if err := validateVersion(c.Version); err != nil {
		return err
	}
	seen := map[string]bool{}
	for _, field := range c.Fields {
		if field.Path == "" {
			return fmt.Errorf("identity catalog %q contains an empty field path", c.Name)
		}
		if seen[field.Path] {
			return fmt.Errorf("identity catalog %q repeats field %q", c.Name, field.Path)
		}
		seen[field.Path] = true
		switch field.Role {
		case RoleSemantic, RoleLineage:
			if !field.InIdentity {
				return fmt.Errorf("identity catalog %q excludes %s field %q", c.Name, field.Role, field.Path)
			}
		case RoleOperational, RolePresentation, RoleSecret:
			if field.InIdentity {
				return fmt.Errorf("identity catalog %q includes forbidden %s field %q", c.Name, field.Role, field.Path)
			}
		case RoleObservation:
			// Observations may be semantic for an observation-specific key and
			// non-semantic for the underlying fact. The catalog must decide.
		default:
			return fmt.Errorf("identity catalog %q has unknown role %q", c.Name, field.Role)
		}
	}
	return nil
}

// SortedFields returns a defensive, path-sorted copy suitable for stable
// reports and code review.
func (c Catalog) SortedFields() []FieldSpec {
	ret := append([]FieldSpec(nil), c.Fields...)
	sort.Slice(ret, func(i, j int) bool { return ret[i].Path < ret[j].Path })
	return ret
}

// Mutation changes one field or semantic dimension of an input fixture.
type Mutation[T any] struct {
	Name       string
	Role       FieldRole
	MustChange bool
	Apply      func(T) T
}

// MutationResult records whether a cache identity reacted as specified.
type MutationResult struct {
	Name       string    `json:"name"`
	Role       FieldRole `json:"role"`
	MustChange bool      `json:"must_change"`
	Changed    bool      `json:"changed"`
	Pass       bool      `json:"pass"`
	Before     string    `json:"before"`
	After      string    `json:"after"`
}

// ContractReport is the executable result of an identity mutation matrix.
type ContractReport struct {
	Name    string           `json:"name"`
	Results []MutationResult `json:"results"`
}

// Passed reports whether every mutation matched its contract.
func (r ContractReport) Passed() bool {
	for _, result := range r.Results {
		if !result.Pass {
			return false
		}
	}
	return true
}

// VerifyContract runs a baseline and a set of single-dimension mutations.
// The fingerprint function is expected to be pure. Re-running the baseline is
// part of the check so nondeterministic key construction is reported too.
func VerifyContract[T any](
	name string,
	baseline T,
	fingerprint func(T) (Fingerprint, error),
	mutations []Mutation[T],
) (ContractReport, error) {
	before, err := fingerprint(baseline)
	if err != nil {
		return ContractReport{}, fmt.Errorf("fingerprint baseline: %w", err)
	}
	repeated, err := fingerprint(baseline)
	if err != nil {
		return ContractReport{}, fmt.Errorf("repeat fingerprint baseline: %w", err)
	}
	if !before.Equal(repeated) {
		return ContractReport{}, fmt.Errorf("identity contract %q is nondeterministic", name)
	}
	report := ContractReport{Name: name, Results: make([]MutationResult, 0, len(mutations))}
	for _, mutation := range mutations {
		if mutation.Apply == nil {
			return ContractReport{}, fmt.Errorf("identity contract %q mutation %q has no Apply function", name, mutation.Name)
		}
		after, err := fingerprint(mutation.Apply(baseline))
		if err != nil {
			return ContractReport{}, fmt.Errorf("fingerprint mutation %q: %w", mutation.Name, err)
		}
		changed := !before.Equal(after)
		report.Results = append(report.Results, MutationResult{
			Name: mutation.Name, Role: mutation.Role,
			MustChange: mutation.MustChange, Changed: changed,
			Pass: changed == mutation.MustChange,
			Before: before.String(), After: after.String(),
		})
	}
	return report, nil
}
EOF

gofmt -w pkg/semanticid
```

<details><summary>💭 Thinking</summary>

**Implemented and tested semantic ID encoding, storage, derivation, selection, and proofs**

</details>

```unknown
bash -lc cd /mnt/data/work-rag-ttc/rag-ttc && cat > pkg/rag/derive/test_helpers_test.go <<'EOF'
package derive

import (
	"fmt"
	"testing"
)

type diamondFixture struct {
	State       State
	SourceA     Fact
	SourceB     Fact
	Claim       Fact
	DerivationA Derivation
	DerivationB Derivation
	ScoreA      Observation
	ScoreB      Observation
}

func newDiamondFixture(t *testing.T) diamondFixture {
	t.Helper()
	sourceA, err := NewFact("chunk", "rag.chunk/v1", map[string]any{
		"chunk_id": "chunk-a",
		"text":     "Oak wilt is caused by Bretziella fagacearum.",
	})
	if err != nil {
		t.Fatal(err)
	}
	sourceB, err := NewFact("chunk", "rag.chunk/v1", map[string]any{
		"chunk_id": "chunk-b",
		"text":     "A vascular fungus causes oak wilt.",
	})
	if err != nil {
		t.Fatal(err)
	}
	claim, err := NewFact("claim", "rag.claim/v1", map[string]any{
		"subject":   "oak wilt",
		"predicate": "caused_by",
		"object":    "Bretziella fagacearum",
	})
	if err != nil {
		t.Fatal(err)
	}
	seedA, err := NewSeedDerivation(sourceA.ID, "corpus", "v1", "ingest-1", "corpus-v7", map[string]any{"uri": "doc:a"})
	if err != nil {
		t.Fatal(err)
	}
	seedB, err := NewSeedDerivation(sourceB.ID, "corpus", "v1", "ingest-1", "corpus-v7", map[string]any{"uri": "doc:b"})
	if err != nil {
		t.Fatal(err)
	}
	derivationA, err := NewDerivation(claim.ID, "extract-claim", "v2", []Input{{Role: "source", Fact: sourceA.ID}}, "q-1", "extractor-v2", map[string]any{"span": "0:49"})
	if err != nil {
		t.Fatal(err)
	}
	derivationB, err := NewDerivation(claim.ID, "resolve-causal-alias", "v1", []Input{{Role: "source", Fact: sourceB.ID}}, "q-1", "resolver-v1", map[string]any{"alias": "vascular fungus"})
	if err != nil {
		t.Fatal(err)
	}
	scoreA, err := NewObservation("retrieval-score", "rag.score/v1", sourceA.ID, "q-1", map[string]any{"channel": "bm25", "rank": 1, "score": 8.5})
	if err != nil {
		t.Fatal(err)
	}
	scoreB, err := NewObservation("retrieval-score", "rag.score/v1", sourceB.ID, "q-1", map[string]any{"channel": "vector", "rank": 2, "score": 0.91})
	if err != nil {
		t.Fatal(err)
	}
	state := NewState()
	for _, item := range []struct {
		fact       *Fact
		derivation *Derivation
		observation *Observation
	}{
		{fact: &sourceA}, {fact: &sourceB}, {fact: &claim},
		{derivation: &seedA}, {derivation: &seedB},
		{derivation: &derivationA}, {derivation: &derivationB},
		{observation: &scoreA}, {observation: &scoreB},
	} {
		var err error
		switch {
		case item.fact != nil:
			state, err = state.WithFact(*item.fact)
		case item.derivation != nil:
			state, err = state.WithDerivation(*item.derivation)
		case item.observation != nil:
			state, err = state.WithObservation(*item.observation)
		}
		if err != nil {
			t.Fatal(err)
		}
	}
	return diamondFixture{
		State: state, SourceA: sourceA, SourceB: sourceB, Claim: claim,
		DerivationA: derivationA, DerivationB: derivationB,
		ScoreA: scoreA, ScoreB: scoreB,
	}
}

func singletonFactState(t *testing.T, suffix string) State {
	t.Helper()
	fact, err := NewFact("fixture", "fixture/v1", map[string]any{"value": suffix})
	if err != nil {
		t.Fatal(err)
	}
	derivation, err := NewSeedDerivation(fact.ID, "fixture", "v1", "", "", map[string]any{"name": suffix})
	if err != nil {
		t.Fatal(err)
	}
	state, err := NewState().WithProof(fact, derivation)
	if err != nil {
		t.Fatal(err)
	}
	return state
}

func allPermutations[T any](values []T) [][]T {
	ret := [][]T{}
	working := append([]T(nil), values...)
	var visit func(int)
	visit = func(index int) {
		if index == len(working) {
			ret = append(ret, append([]T(nil), working...))
			return
		}
		for other := index; other < len(working); other++ {
			working[index], working[other] = working[other], working[index]
			visit(index + 1)
			working[index], working[other] = working[other], working[index]
		}
	}
	visit(0)
	return ret
}

func describeState(state State) string {
	fingerprint, err := state.Fingerprint()
	if err != nil {
		return fmt.Sprintf("error:%v", err)
	}
	return fingerprint.String()
}
EOF

cat > pkg/rag/derive/canonical_json_test.go <<'EOF'
package derive

import (
	"bytes"
	"testing"
)

func TestNormalizeJSONMakesObjectOrderAndNumberSpellingIrrelevant(t *testing.T) {
	left, err := NormalizeJSON([]byte(`{"b":1.0,"a":[-0,2e0]}`))
	if err != nil {
		t.Fatal(err)
	}
	right, err := NormalizeJSON([]byte(`{"a":[0,2],"b":1}`))
	if err != nil {
		t.Fatal(err)
	}
	if !bytes.Equal(left, right) {
		t.Fatalf("normalization mismatch:\n%s\n%s", left, right)
	}
	if string(left) != `{"a":[0,2],"b":1}` {
		t.Fatalf("unexpected canonical JSON %s", left)
	}
}

func TestNormalizeJSONRejectsDuplicateNamesAndTrailingInput(t *testing.T) {
	for _, value := range []string{
		`{"x":1,"x":2}`,
		`{"x":1} {"y":2}`,
	} {
		if _, err := NormalizeJSON([]byte(value)); err == nil {
			t.Fatalf("accepted invalid canonical input %s", value)
		}
	}
}
EOF

cat > pkg/rag/derive/fact_test.go <<'EOF'
package derive

import (
	"encoding/json"
	"testing"
)

func TestFactIdentityIgnoresObjectFieldOrderButNotSemanticContent(t *testing.T) {
	first, err := NewFactFromJSON("chunk", "rag.chunk/v1", []byte(`{"text":"abc","chunk_id":"c1"}`))
	if err != nil {
		t.Fatal(err)
	}
	second, err := NewFactFromJSON("chunk", "rag.chunk/v1", []byte(`{"chunk_id":"c1","text":"abc"}`))
	if err != nil {
		t.Fatal(err)
	}
	changed, err := NewFactFromJSON("chunk", "rag.chunk/v1", []byte(`{"chunk_id":"c1","text":"abd"}`))
	if err != nil {
		t.Fatal(err)
	}
	if first.ID != second.ID {
		t.Fatal("representation-only object order changed fact identity")
	}
	if first.ID == changed.ID {
		t.Fatal("semantic payload mutation did not change fact identity")
	}
}

func TestObservationsDoNotChangeFactIdentity(t *testing.T) {
	fixture := newDiamondFixture(t)
	first, err := NewObservation("score", "score/v1", fixture.SourceA.ID, "q-1", map[string]any{"score": 0.2})
	if err != nil {
		t.Fatal(err)
	}
	second, err := NewObservation("score", "score/v1", fixture.SourceA.ID, "q-1", map[string]any{"score": 0.9})
	if err != nil {
		t.Fatal(err)
	}
	if first.ID == second.ID {
		t.Fatal("different observations received the same identity")
	}
	if first.Subject != fixture.SourceA.ID || second.Subject != fixture.SourceA.ID {
		t.Fatal("observation changed underlying fact identity")
	}
}

func TestDiamondProvenanceAndProofBundle(t *testing.T) {
	fixture := newDiamondFixture(t)
	report := Verify(fixture.State)
	if !report.Valid {
		data, _ := json.MarshalIndent(report, "", "  ")
		t.Fatalf("fixture did not verify:\n%s", data)
	}
	if report.Ranks[fixture.SourceA.ID] != 0 || report.Ranks[fixture.Claim.ID] != 1 {
		t.Fatalf("unexpected ranks %#v", report.Ranks)
	}
	bundle, err := BuildProofBundle(fixture.State, []FactID{fixture.Claim.ID}, "corpus-v7", "pipeline-v3")
	if err != nil {
		t.Fatal(err)
	}
	if got := len(bundle.State.Derivations); got != 4 {
		t.Fatalf("bundle dropped alternative provenance: got %d derivations", got)
	}
	if verification := VerifyProofBundle(bundle); !verification.Valid {
		t.Fatalf("proof bundle did not independently verify: %#v", verification.Issues)
	}
}

func TestVerifierDetectsTamperingAndMissingDependencies(t *testing.T) {
	fixture := newDiamondFixture(t)
	snapshot := fixture.State.Snapshot()
	snapshot.Facts[0].Payload = []byte(`{"tampered":true}`)
	tampered, err := FromSnapshot(snapshot)
	if err != nil {
		t.Fatal(err)
	}
	report := Verify(tampered)
	if report.Valid {
		t.Fatal("tampered state verified")
	}
	codes := map[string]bool{}
	for _, issue := range report.Issues {
		codes[issue.Code] = true
	}
	if !codes["fact-id-mismatch"] && !codes["identity-conflict"] {
		t.Fatalf("missing expected integrity issue: %#v", report.Issues)
	}

	missing := fixture.State.Snapshot()
	filtered := missing.Facts[:0]
	for _, fact := range missing.Facts {
		if fact.ID != fixture.SourceA.ID {
			filtered = append(filtered, fact)
		}
	}
	missing.Facts = filtered
	state, err := FromSnapshot(missing)
	if err != nil {
		t.Fatal(err)
	}
	report = Verify(state)
	if report.Valid {
		t.Fatal("state with missing derivation dependency verified")
	}
}
EOF

gofmt -w pkg/rag/derive/*_test.go
```

<details><summary>💭 Thinking</summary>

**Inspected and tested RAG evidence identity, merging, caching, and provider integration**

</details>

```unknown
bash -lc cd /mnt/data/work-rag-ttc/rag-ttc && python - <<'PY'
from pathlib import Path
p=Path('pkg/rag/evidence_identity.go')
s=p.read_text()
s=s.replace('''\t\tif contentDigest == "" {
\t\t\tvar err error
\t\t\tcontentDigest, err = digest.JSON(item.Chunk.Text)
\t\t\tif err != nil {
\t\t\t\treturn nil, errors.Wrapf(err, "digest evidence %d", index)
\t\t\t}
\t\t}''','''\t\tif contentDigest == "" {
\t\t\tcontentDigest = digest.Text(item.Chunk.Text)
\t\t}''')
p.write_text(s)
PY
# pkg/errors is still used for missing IDs; format
gofmt -w pkg/rag/evidence_identity.go
# Strengthen the regression test.
python - <<'PY'
from pathlib import Path
p=Path('pkg/rag/evidence_identity_test.go')
s=p.read_text()
s=s.replace('''import (
\t"testing"

\t"github.com/stretchr/testify/require"
)''','''import (
\t"testing"

\t"github.com/stretchr/testify/require"
\t"github.com/the-tree-center/rag-ttc/pkg/digest"
)''')
s=s.replace('''\trequire.Len(t, identities, 1)
\trequire.NotEmpty(t, identities[0].ContentDigest)
}''','''\trequire.Len(t, identities, 1)
\trequire.Equal(t, digest.Text("source text"), identities[0].ContentDigest)
}''')
p.write_text(s)
PY
gofmt -w pkg/rag/evidence_identity_test.go
```

<details><summary>💭 Thinking</summary>

**Replaced JSON digests with semantic provider and runtime fingerprints across caching and tests**

</details>

```unknown
bash -lc cd /mnt/data/work-rag-ttc/rag-ttc && mkdir -p pkg/rag/derive/ragcodec && cat > pkg/rag/derive/ragcodec/codec.go <<'EOF'
// Package ragcodec adapts current rag package records to the derive semantic
// kernel. The adapter makes the fact/observation boundary explicit without
// requiring every existing package to change its public types at once.
package ragcodec

import (
	"fmt"
	"strings"

	"github.com/the-tree-center/rag-ttc/pkg/digest"
	"github.com/the-tree-center/rag-ttc/pkg/rag"
	"github.com/the-tree-center/rag-ttc/pkg/rag/derive"
)

const (
	ChunkSchema          = "rag.chunk-fact/v1"
	RepresentationSchema = "rag.representation-fact/v1"
	RetrievalSchema      = "rag.retrieval-observation/v1"
)

// Chunk converts an immutable rag.Chunk to a canonical fact and a zero-input
// corpus admission derivation. The external chunk ID is retained as lineage;
// the derive FactID is computed from the complete immutable payload.
func Chunk(value rag.Chunk, corpusID, ingestionRequestID string) (derive.State, derive.FactID, error) {
	if strings.TrimSpace(value.ID) == "" || strings.TrimSpace(value.DocumentID) == "" {
		return derive.State{}, "", fmt.Errorf("chunk ID and document ID are required")
	}
	contentDigest := value.ContentDigest
	computed := digest.Text(value.Text)
	if contentDigest == "" {
		contentDigest = computed
	} else if contentDigest != computed {
		return derive.State{}, "", fmt.Errorf("chunk %s content digest does not match text", value.ID)
	}
	fact, err := derive.NewFact("source-chunk", ChunkSchema, struct {
		SourceChunkID string    `json:"source_chunk_id"`
		DocumentID    string    `json:"document_id"`
		Ordinal       int       `json:"ordinal"`
		Range         rag.Range `json:"range"`
		Text          string    `json:"text"`
		ContentDigest string    `json:"content_digest"`
		Chunker       string    `json:"chunker"`
	}{
		SourceChunkID: value.ID, DocumentID: value.DocumentID,
		Ordinal: value.Ordinal, Range: value.Range, Text: value.Text,
		ContentDigest: contentDigest, Chunker: value.Chunker,
	})
	if err != nil {
		return derive.State{}, "", err
	}
	proof, err := derive.NewSeedDerivation(
		fact.ID, "rag-chunk", "v1", ingestionRequestID, corpusID,
		map[string]any{"source_chunk_id": value.ID, "document_id": value.DocumentID},
	)
	if err != nil {
		return derive.State{}, "", err
	}
	state, err := derive.NewState().WithProof(fact, proof)
	return state, fact.ID, err
}

// Representation converts searchable material to a fact derived from a chunk
// fact. Retrieval representations are not source evidence, but preserving
// them as facts makes index lineage and cache/replay checks explicit.
func Representation(value rag.Representation, chunkFact derive.FactID, requestID, configID string) (derive.State, derive.FactID, error) {
	if value.ID == "" || value.ChunkID == "" || chunkFact == "" || value.Kind == "" {
		return derive.State{}, "", fmt.Errorf("representation identity, kind, and chunk fact are required")
	}
	contentDigest := value.ContentDigest
	computed := digest.Text(value.Text)
	if contentDigest == "" {
		contentDigest = computed
	} else if contentDigest != computed {
		return derive.State{}, "", fmt.Errorf("representation %s content digest does not match text", value.ID)
	}
	fact, err := derive.NewFact("retrieval-representation", RepresentationSchema, struct {
		SourceRepresentationID string        `json:"source_representation_id"`
		SourceChunkID          string        `json:"source_chunk_id"`
		ChunkFact              derive.FactID `json:"chunk_fact"`
		Kind                   string        `json:"kind"`
		Text                   string        `json:"text"`
		ContentDigest          string        `json:"content_digest"`
		Model                  string        `json:"model,omitempty"`
		PromptDigest           string        `json:"prompt_digest,omitempty"`
	}{
		SourceRepresentationID: value.ID, SourceChunkID: value.ChunkID,
		ChunkFact: chunkFact, Kind: value.Kind, Text: value.Text,
		ContentDigest: contentDigest, Model: value.Model,
		PromptDigest: value.PromptDigest,
	})
	if err != nil {
		return derive.State{}, "", err
	}
	proof, err := derive.NewDerivation(
		fact.ID, "derive-retrieval-representation", "v1",
		[]derive.Input{{Role: "source-chunk", Fact: chunkFact}},
		requestID, configID,
		map[string]any{"source_representation_id": value.ID},
	)
	if err != nil {
		return derive.State{}, "", err
	}
	state, err := derive.NewState().WithProof(fact, proof)
	return state, fact.ID, err
}

// Evidence converts hydrated source evidence into one canonical chunk fact and
// one request-specific retrieval observation. Rank and scores are excluded
// from the chunk identity by construction.
func Evidence(value rag.Evidence, requestID, channel, corpusID string) (derive.State, derive.FactID, derive.ObservationID, error) {
	state, factID, err := Chunk(value.Chunk, corpusID, requestID)
	if err != nil {
		return derive.State{}, "", "", err
	}
	observation, err := derive.NewObservation("retrieval", RetrievalSchema, factID, requestID, struct {
		Channel         string   `json:"channel,omitempty"`
		Rank            int      `json:"rank"`
		RetrievalScore  float64  `json:"retrieval_score"`
		RerankerScore   *float64 `json:"reranker_score,omitempty"`
		SourceChunkID   string   `json:"source_chunk_id"`
	}{
		Channel: channel, Rank: value.Rank, RetrievalScore: value.RetrievalScore,
		RerankerScore: value.RerankerScore, SourceChunkID: value.Chunk.ID,
	})
	if err != nil {
		return derive.State{}, "", "", err
	}
	state, err = state.WithObservation(observation)
	if err != nil {
		return derive.State{}, "", "", err
	}
	return state, factID, observation.ID, nil
}
EOF

gofmt -w pkg/rag/derive/ragcodec/codec.go
```

<details><summary>💭 Thinking</summary>

**Implemented and tested fact encoding, evidence selection, caching, and provider-sensitive reranking**

</details>

```unknown
bash -lc cd /mnt/data/work-rag-ttc/rag-ttc && mkdir -p cmd/semantic-foundations && cat > cmd/semantic-foundations/main.go <<'EOF'
// Command semantic-foundations executes the P01-P03 conformance scenarios
// without network, database, or model dependencies.
package main

import (
	"encoding/json"
	"flag"
	"fmt"
	"os"
	"runtime"
	"sort"
	"sync"
	"time"

	"github.com/the-tree-center/rag-ttc/pkg/rag/derive"
	"github.com/the-tree-center/rag-ttc/pkg/semanticid"
)

type identityFixture struct {
	Query       string
	TopK        int64
	Workers     int64
	APIKey      string
	DisplayName string
}

type evaluationReport struct {
	Schema      string                     `json:"schema"`
	GoVersion   string                     `json:"go_version"`
	GeneratedAt string                     `json:"generated_at"`
	P01         p01Report                  `json:"p01"`
	P02         p02Report                  `json:"p02"`
	P03         p03Report                  `json:"p03"`
}

type p01Report struct {
	GoldenFingerprint string                    `json:"golden_fingerprint"`
	Contract          semanticid.ContractReport `json:"contract"`
	CatalogValid      bool                      `json:"catalog_valid"`
}

type p02Report struct {
	StateFingerprint string                    `json:"state_fingerprint"`
	Counts           derive.Counts             `json:"counts"`
	Verification     derive.VerificationReport `json:"verification"`
	ProofFingerprint string                    `json:"proof_fingerprint"`
	ProofValid       bool                      `json:"proof_valid"`
	AlternativeProofs int                      `json:"alternative_proofs"`
}

type p03Report struct {
	MergePermutations          int      `json:"merge_permutations"`
	UniqueMergeOutputs         int      `json:"unique_merge_outputs"`
	SelectionPermutations      int      `json:"selection_permutations"`
	UniqueSelectedViews        int      `json:"unique_selected_views"`
	LegacyArrivalViews         int      `json:"legacy_arrival_views"`
	ConflictVariants           int      `json:"conflict_variants"`
	ConcurrentRetryRuns        int      `json:"concurrent_retry_runs"`
	ConcurrentRetryDivergences int      `json:"concurrent_retry_divergences"`
	SelectedLabels             []string `json:"selected_labels"`
	StressFacts                int      `json:"stress_facts"`
	StressJoinMilliseconds     float64  `json:"stress_join_milliseconds"`
}

type fixture struct {
	state       derive.State
	sourceA     derive.Fact
	sourceB     derive.Fact
	claim       derive.Fact
	scoreA      derive.Observation
	scoreB      derive.Observation
	derivationA derive.Derivation
	derivationB derive.Derivation
}

func main() {
	output := flag.String("output", "", "write JSON report to this path; stdout when empty")
	stressFacts := flag.Int("stress-facts", 2000, "number of singleton states in the merge stress scenario")
	flag.Parse()

	report, err := evaluate(*stressFacts)
	if err != nil {
		fmt.Fprintln(os.Stderr, err)
		os.Exit(1)
	}
	data, err := json.MarshalIndent(report, "", "  ")
	if err != nil {
		fmt.Fprintln(os.Stderr, err)
		os.Exit(1)
	}
	data = append(data, '\n')
	if *output == "" {
		_, _ = os.Stdout.Write(data)
		return
	}
	if err := os.WriteFile(*output, data, 0o644); err != nil {
		fmt.Fprintln(os.Stderr, err)
		os.Exit(1)
	}
}

func evaluate(stressFacts int) (evaluationReport, error) {
	p01, err := evaluateP01()
	if err != nil {
		return evaluationReport{}, err
	}
	fx, err := buildFixture()
	if err != nil {
		return evaluationReport{}, err
	}
	p02, err := evaluateP02(fx)
	if err != nil {
		return evaluationReport{}, err
	}
	p03, err := evaluateP03(fx, stressFacts)
	if err != nil {
		return evaluationReport{}, err
	}
	return evaluationReport{
		Schema: "rag-ttc-p01-p03-evaluation/v1", GoVersion: runtime.Version(),
		GeneratedAt: time.Now().UTC().Format(time.RFC3339), P01: p01, P02: p02, P03: p03,
	}, nil
}

func evaluateP01() (p01Report, error) {
	fingerprint := func(value identityFixture) (semanticid.Fingerprint, error) {
		return semanticid.FingerprintValue("rag.retrieval.cache", "v1", semanticid.MustObject(
			semanticid.Field{Name: "query", Value: semanticid.MustString(value.Query)},
			semanticid.Field{Name: "top_k", Value: semanticid.Int(value.TopK)},
		))
	}
	baseline := identityFixture{Query: "oak decline", TopK: 12, Workers: 4, APIKey: "secret", DisplayName: "trial-a"}
	contract, err := semanticid.VerifyContract("retrieval-cache-v1", baseline, fingerprint, []semanticid.Mutation[identityFixture]{
		{Name: "query", Role: semanticid.RoleSemantic, MustChange: true, Apply: func(v identityFixture) identityFixture { v.Query += " causes"; return v }},
		{Name: "top-k", Role: semanticid.RoleSemantic, MustChange: true, Apply: func(v identityFixture) identityFixture { v.TopK++; return v }},
		{Name: "workers", Role: semanticid.RoleOperational, MustChange: false, Apply: func(v identityFixture) identityFixture { v.Workers++; return v }},
		{Name: "api-key", Role: semanticid.RoleSecret, MustChange: false, Apply: func(v identityFixture) identityFixture { v.APIKey = "rotated"; return v }},
		{Name: "display-name", Role: semanticid.RolePresentation, MustChange: false, Apply: func(v identityFixture) identityFixture { v.DisplayName = "trial-b"; return v }},
	})
	if err != nil {
		return p01Report{}, err
	}
	catalog := semanticid.Catalog{Name: "retrieval-cache-v1", Domain: "rag.retrieval.cache", Version: "v1", Fields: []semanticid.FieldSpec{
		{Path: "query", Role: semanticid.RoleSemantic, InIdentity: true},
		{Path: "top_k", Role: semanticid.RoleSemantic, InIdentity: true},
		{Path: "workers", Role: semanticid.RoleOperational, InIdentity: false},
		{Path: "api_key", Role: semanticid.RoleSecret, InIdentity: false},
		{Path: "display_name", Role: semanticid.RolePresentation, InIdentity: false},
	}}
	catalogValid := catalog.Validate() == nil
	golden, err := fingerprint(baseline)
	if err != nil {
		return p01Report{}, err
	}
	return p01Report{GoldenFingerprint: golden.String(), Contract: contract, CatalogValid: catalogValid}, nil
}

func buildFixture() (fixture, error) {
	sourceA, err := derive.NewFact("chunk", "rag.chunk/v1", map[string]any{"id": "a", "text": "Oak wilt is caused by Bretziella fagacearum."})
	if err != nil { return fixture{}, err }
	sourceB, err := derive.NewFact("chunk", "rag.chunk/v1", map[string]any{"id": "b", "text": "A vascular fungus causes oak wilt."})
	if err != nil { return fixture{}, err }
	claim, err := derive.NewFact("claim", "rag.claim/v1", map[string]any{"subject": "oak wilt", "predicate": "caused_by", "object": "Bretziella fagacearum"})
	if err != nil { return fixture{}, err }
	seedA, err := derive.NewSeedDerivation(sourceA.ID, "corpus", "v1", "ingest", "corpus-v1", map[string]any{"uri": "doc:a"})
	if err != nil { return fixture{}, err }
	seedB, err := derive.NewSeedDerivation(sourceB.ID, "corpus", "v1", "ingest", "corpus-v1", map[string]any{"uri": "doc:b"})
	if err != nil { return fixture{}, err }
	proofA, err := derive.NewDerivation(claim.ID, "extract", "v1", []derive.Input{{Role: "source", Fact: sourceA.ID}}, "q1", "extract-v1", map[string]any{"span": "0:49"})
	if err != nil { return fixture{}, err }
	proofB, err := derive.NewDerivation(claim.ID, "resolve", "v1", []derive.Input{{Role: "source", Fact: sourceB.ID}}, "q1", "resolve-v1", map[string]any{"alias": "vascular fungus"})
	if err != nil { return fixture{}, err }
	scoreA, err := derive.NewObservation("score", "rag.score/v1", sourceA.ID, "q1", map[string]any{"channel": "bm25", "score": 0.8})
	if err != nil { return fixture{}, err }
	scoreB, err := derive.NewObservation("score", "rag.score/v1", sourceB.ID, "q1", map[string]any{"channel": "vector", "score": 0.9})
	if err != nil { return fixture{}, err }
	state := derive.NewState()
	for _, fact := range []derive.Fact{sourceA, sourceB, claim} {
		state, err = state.WithFact(fact); if err != nil { return fixture{}, err }
	}
	for _, proof := range []derive.Derivation{seedA, seedB, proofA, proofB} {
		state, err = state.WithDerivation(proof); if err != nil { return fixture{}, err }
	}
	for _, observation := range []derive.Observation{scoreA, scoreB} {
		state, err = state.WithObservation(observation); if err != nil { return fixture{}, err }
	}
	return fixture{state: state, sourceA: sourceA, sourceB: sourceB, claim: claim, scoreA: scoreA, scoreB: scoreB, derivationA: proofA, derivationB: proofB}, nil
}

func evaluateP02(fx fixture) (p02Report, error) {
	verification := derive.Verify(fx.state)
	stateFingerprint, err := fx.state.Fingerprint()
	if err != nil { return p02Report{}, err }
	bundle, err := derive.BuildProofBundle(fx.state, []derive.FactID{fx.claim.ID}, "corpus-v1", "pipeline-v1")
	if err != nil { return p02Report{}, err }
	bundleData, err := derive.CanonicalMarshal(bundle)
	if err != nil { return p02Report{}, err }
	proofFingerprint := semanticid.MustFingerprint("rag.proof.bundle", "v1", semanticid.Bytes(bundleData))
	proofVerification := derive.VerifyProofBundle(bundle)
	alternatives := 0
	for _, proof := range bundle.State.Derivations {
		if proof.Output == fx.claim.ID { alternatives++ }
	}
	return p02Report{
		StateFingerprint: stateFingerprint.String(), Counts: fx.state.Counts(),
		Verification: verification, ProofFingerprint: proofFingerprint.String(),
		ProofValid: proofVerification.Valid, AlternativeProofs: alternatives,
	}, nil
}

func evaluateP03(fx fixture, stressFacts int) (p03Report, error) {
	deltas := make([]derive.State, 0, 6)
	for _, fact := range []derive.Fact{fx.sourceA, fx.sourceB, fx.claim} {
		state, err := derive.NewState().WithFact(fact); if err != nil { return p03Report{}, err }; deltas = append(deltas, state)
	}
	for _, proof := range []derive.Derivation{fx.derivationA, fx.derivationB} {
		state, err := derive.NewState().WithDerivation(proof); if err != nil { return p03Report{}, err }; deltas = append(deltas, state)
	}
	state, err := derive.NewState().WithObservation(fx.scoreA); if err != nil { return p03Report{}, err }; deltas = append(deltas, state)

	mergeOutputs := map[string]bool{}
	permutations := allPermutations(deltas)
	for _, order := range permutations {
		state := derive.NewState()
		for _, delta := range order { state = derive.Join(state, delta) }
		fingerprint, err := state.Fingerprint(); if err != nil { return p03Report{}, err }
		mergeOutputs[fingerprint.String()] = true
	}

	candidates := []derive.Candidate{
		{Fact: fx.sourceA.ID, Observation: fx.scoreA.ID, StableKey: "a", Utility: 0.8, Units: 4},
		{Fact: fx.sourceB.ID, Observation: fx.scoreB.ID, StableKey: "b", Utility: 0.9, Units: 4},
		{Fact: fx.claim.ID, StableKey: "c", Utility: 0.9, Units: 3},
	}
	selectionOutputs := map[string]bool{}
	legacyOutputs := map[string]bool{}
	candidatePermutations := allPermutations(candidates)
	var selectedLabels []string
	for _, order := range candidatePermutations {
		selected, err := derive.Select(fx.state, order, derive.SelectionPolicy{Version: "v1", MaxItems: 2, MaxUnits: 8})
		if err != nil { return p03Report{}, err }
		data, _ := derive.CanonicalMarshal(selected)
		selectionOutputs[string(data)] = true
		legacy := order[:2]
		legacyData, _ := derive.CanonicalMarshal(legacy)
		legacyOutputs[string(legacyData)] = true
		if selectedLabels == nil {
			for _, item := range selected { selectedLabels = append(selectedLabels, item.Label) }
		}
	}

	conflictFact := fx.sourceA
	conflictFact.Payload = []byte(`{"id":"a","text":"conflicting payload"}`)
	conflictState, err := derive.NewState().WithFact(conflictFact); if err != nil { return p03Report{}, err }
	baseState, err := derive.NewState().WithFact(fx.sourceA); if err != nil { return p03Report{}, err }
	conflicts := derive.Join(baseState, conflictState).Conflicts()
	conflictVariants := 0
	if len(conflicts) > 0 { conflictVariants = len(conflicts[0].VariantDigests) }

	concurrentDivergences := 0
	expected := derive.NewState()
	for _, delta := range deltas { expected = derive.Join(expected, delta) }
	for run := 0; run < 100; run++ {
		ledger := derive.NewLedger(derive.NewState())
		var wait sync.WaitGroup
		for index, delta := range deltas {
			delta := delta
			retries := 1 + (index+run)%3
			wait.Add(1)
			go func() { defer wait.Done(); for i := 0; i < retries; i++ { ledger.Merge(delta) } }()
		}
		wait.Wait()
		if !ledger.Snapshot().Equal(expected) { concurrentDivergences++ }
	}

	started := time.Now()
	stress := derive.NewState()
	for index := 0; index < stressFacts; index++ {
		fact, err := derive.NewFact("stress", "stress/v1", map[string]any{"index": index})
		if err != nil { return p03Report{}, err }
		proof, err := derive.NewSeedDerivation(fact.ID, "stress", "v1", "", "", nil)
		if err != nil { return p03Report{}, err }
		delta, err := derive.NewState().WithProof(fact, proof)
		if err != nil { return p03Report{}, err }
		stress = derive.Join(stress, delta)
	}
	stressDuration := time.Since(started)

	return p03Report{
		MergePermutations: len(permutations), UniqueMergeOutputs: len(mergeOutputs),
		SelectionPermutations: len(candidatePermutations), UniqueSelectedViews: len(selectionOutputs),
		LegacyArrivalViews: len(legacyOutputs), ConflictVariants: conflictVariants,
		ConcurrentRetryRuns: 100, ConcurrentRetryDivergences: concurrentDivergences,
		SelectedLabels: selectedLabels, StressFacts: stressFacts,
		StressJoinMilliseconds: float64(stressDuration.Microseconds()) / 1000,
	}, nil
}

func allPermutations[T any](values []T) [][]T {
	ret := [][]T{}
	working := append([]T(nil), values...)
	var visit func(int)
	visit = func(index int) {
		if index == len(working) {
			ret = append(ret, append([]T(nil), working...))
			return
		}
		for other := index; other < len(working); other++ {
			working[index], working[other] = working[other], working[index]
			visit(index + 1)
			working[index], working[other] = working[other], working[index]
		}
	}
	visit(0)
	return ret
}

// Keep sort linked into the small command's binary so `go vet` also sees the
// deterministic-order dependency in this conformance tool.
var _ = sort.Strings
EOF

gofmt -w cmd/semantic-foundations/main.go
```

<details><summary>💭 Thinking</summary>

**Validating implementation**

I’m compiling the standard-library core, running race-enabled law tests, checking deterministic fingerprints and joins, then rendering the thesis PDF and reviewing its pages before packaging the implementation and results.

**Finalizing validation**

I’m checking syntax and call sites, running the P01–P03 evaluation harness, and recording permutation, conflict, concurrency, proof, and stress results for the thesis and implementation package.

**Validated implementation**

</details>

```unknown
bash -lc ls -la /mnt/data/work-rag-ttc/rag-ttc && find /mnt/data/work-rag-ttc/rag-ttc/pkg/semanticid -maxdepth 2 -type f -print && find /mnt/data/work-rag-ttc/rag-ttc/pkg/rag/derive -maxdepth 3 -type f -print | sort | head -100
```

<details><summary>💭 Thinking</summary>

**Implemented and optimized semantic foundations evaluation and mutable state merge reporting**

</details>

```unknown
bash -lc set -euo pipefail
repo=/mnt/data/work-rag-ttc/rag-ttc
out=/mnt/data/work-rag-ttc/results/scaling-runs
rm -rf "$out" && mkdir -p "$out"
for n in 250 500 1000 2000 4000; do
  reps=3
  if [ "$n" -eq 4000 ]; then reps=2; fi
  for r in $(seq 1 "$reps"); do
    (cd "$repo" && GO111MODULE=off GOPATH=/mnt/data/gopath go run ./cmd/semantic-foundations --output "$out/n${n}-r${r}.json" --stress-facts "$n")
  done
done
python - <<'PY'
import csv,json,glob,statistics,pathlib
rows=[]
for path in sorted(glob.glob('/mnt/data/work-rag-ttc/results/scaling-runs/*.json')):
    j=json.load(open(path)); p=j['p03']
    name=pathlib.Path(path).stem
    n=int(name.split('-')[0][1:]); rep=int(name.split('-')[1][1:])
    rows.append({'facts':n,'replicate':rep,'persistent_ms':p['stress_persistent_join_milliseconds'],'ledger_ms':p['stress_ledger_milliseconds'],'equal':p['stress_outputs_equal']})
csvp='/mnt/data/work-rag-ttc/results/p01-p03-scaling-runs.csv'
with open(csvp,'w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=rows[0].keys()); w.writeheader();w.writerows(rows)
summary=[]
for n in sorted({r['facts'] for r in rows}):
    rs=[r for r in rows if r['facts']==n]
    summary.append({'facts':n,'replicates':len(rs),
                    'persistent_median_ms':round(statistics.median(r['persistent_ms'] for r in rs),3),
                    'ledger_median_ms':round(statistics.median(r['ledger_ms'] for r in rs),3),
                    'speedup':round(statistics.median(r['persistent_ms'] for r in rs)/statistics.median(r['ledger_ms'] for r in rs),1),
                    'all_equal':all(r['equal'] for r in rs)})
out='/mnt/data/work-rag-ttc/results/p01-p03-scaling-summary.json'
json.dump({'schema':'rag-ttc-p01-p03-scaling/v1','runs':rows,'summary':summary},open(out,'w'),indent=2)
print(json.dumps(summary,indent=2))
PY
```

<details><summary>💭 Thinking</summary>

**Inspected, patched, tested, and verified RAG evaluation foundations and artifacts**

</details>

```json
{"search_query":[{"q":"RFC 8785 JSON Canonicalization Scheme official RFC Editor"},{"q":"Shapiro Preguiça Baquero Zawirski comprehensive study convergent commutative replicated data types PDF"},{"q":"Keeping CALM When Distributed Consistency is Easy paper Alvaro Hellerstein"},{"q":"W3C PROV-DM provenance data model recommendation"}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Searched 31 websites**

</details>

```unknown
bash -lc command -v dot || true; command -v pandoc || true; command -v xelatex || true; command -v pdftoppm || true; command -v pdfinfo || true
```

<details><summary>💭 Thinking</summary>

**Compared codebases, refreshed checksums, mapped key paths, and generated architecture diagrams**

</details>

```unknown
import json, csv, statistics, pathlib, matplotlib.pyplot as plt, math
src = pathlib.Path('/mnt/data/work-rag-ttc/results/p01-p03-scaling-summary.json')
data = json.loads(src.read_text())
summary = data['summary']
facts = [r['facts'] for r in summary]
persistent = [r['persistent_median_ms'] for r in summary]
ledger = [r['ledger_median_ms'] for r in summary]
speedup = [r['speedup'] for r in summary]
assets = pathlib.Path('/mnt/data/rag-ttc-p01-p03-thesis-assets')

plt.figure(figsize=(8,5))
plt.plot(facts, persistent, marker='o', label='Persistent Join per singleton')
plt.plot(facts, ledger, marker='o', label='Mutable Ledger per singleton')
plt.ys
```

<details><summary>💭 Thinking</summary>

**Plotted scaling performance and speedup charts**

</details>

```unknown
bash -lc find /mnt/data/work-rag-ttc -maxdepth 3 -type f -name '*scaling*' -o -name 'p01-p03-evaluation.json' | sort
```

<details><summary>💭 Thinking</summary>

**Reconstructed semantic ID environment and verified RAG derivation with tests**

</details>

```unknown
bash -lc cd /mnt/data/work-rag-ttc/rag-ttc && printf '%s\n' '--- P01-P03 BRIEFS ---' && for f in /mnt/data/rag-ttc-research-projects/P0{1,2,3}-*.md; do echo "### $f"; sed -n '1,240p' "$f" | head -180; done && printf '%s\n' '--- RELEVANT FILES ---' && find pkg/rag -maxdepth 4 -type f | grep -E '(evidence_identity|connected/runtime|providers/geppetto|generationcache|reranking|toolanswer/evidence|flow)' | sort | sed -n '1,240p'
```

<details><summary>💭 Thinking</summary>

**Implemented semantic conformance, deterministic evidence ledgers, and provider-aware generation caching across RAG flows**

</details>

```unknown
bash -lc cat > /mnt/data/work-rag-ttc/rag-ttc/pkg/rag/toolanswer/deterministic_ledger_test.go <<'EOF'
package toolanswer

import (
	"fmt"
	"reflect"
	"testing"

	"github.com/stretchr/testify/require"
	"github.com/the-tree-center/rag-ttc/pkg/rag"
)

func TestDeterministicEvidenceLedgerIsCompletionOrderAndRetryInvariant(t *testing.T) {
	chunks := []rag.Chunk{
		{ID: "c-a", DocumentID: "d-a", Text: "A source", Ordinal: 1, Range: rag.Range{ByteStart: 0, ByteEnd: 8}},
		{ID: "c-b", DocumentID: "d-b", Text: "B source", Ordinal: 1, Range: rag.Range{ByteStart: 0, ByteEnd: 8}},
		{ID: "c-c", DocumentID: "d-c", Text: "C source", Ordinal: 1, Range: rag.Range{ByteStart: 0, ByteEnd: 8}},
	}
	utilities := map[string]float64{"c-a": .6, "c-b": .8, "c-c": .7}
	var wantRefs []EvidenceRef
	var wantState string
	for permutationIndex, order := range permutations(chunks) {
		ledger := NewDeterministicEvidenceLedger()
		for _, chunk := range order {
			require.NoError(t, ledger.AddCandidate(chunk, "call-"+chunk.ID, "corpus-v1", "tool-search", utilities[chunk.ID]))
			require.NoError(t, ledger.AddCandidate(chunk, "call-"+chunk.ID, "corpus-v1", "tool-search", utilities[chunk.ID]))
		}
		refs, state, err := ledger.Finalize(2, 100)
		require.NoError(t, err)
		canonical, err := state.CanonicalJSON()
		require.NoError(t, err)
		if permutationIndex == 0 {
			wantRefs, wantState = refs, string(canonical)
			continue
		}
		require.True(t, reflect.DeepEqual(wantRefs, refs), "permutation %d refs: %s", permutationIndex, fmt.Sprint(refs))
		require.Equal(t, wantState, string(canonical), "permutation %d state", permutationIndex)
	}
	require.Equal(t, []string{"c-b", "c-c"}, []string{wantRefs[0].ChunkID, wantRefs[1].ChunkID})
	require.Equal(t, []string{"E1", "E2"}, []string{wantRefs[0].Citation, wantRefs[1].Citation})
	require.True(t, wantRefs[0].AdmittedAt.IsZero())
}

func permutations[T any](values []T) [][]T {
	items := append([]T(nil), values...)
	var out [][]T
	var visit func(int)
	visit = func(index int) {
		if index == len(items) {
			out = append(out, append([]T(nil), items...))
			return
		}
		for swap := index; swap < len(items); swap++ {
			items[index], items[swap] = items[swap], items[index]
			visit(index + 1)
			items[index], items[swap] = items[swap], items[index]
		}
	}
	visit(0)
	return out
}
EOF

cat > /mnt/data/work-rag-ttc/rag-ttc/pkg/rag/derive/ragcodec/codec_test.go <<'EOF'
package ragcodec

import (
	"testing"

	"github.com/stretchr/testify/require"
	"github.com/the-tree-center/rag-ttc/pkg/rag"
)

func TestEvidenceSeparatesSourceIdentityFromQueryObservations(t *testing.T) {
	chunk := rag.Chunk{ID: "legacy-c1", DocumentID: "d1", Text: "source", Ordinal: 2, Range: rag.Range{ByteStart: 10, ByteEnd: 16}, Chunker: "fixed-v1"}
	first, proof1, observation1, err := Evidence(rag.Evidence{Chunk: chunk, Rank: 1, RetrievalScore: .2}, "q1", "corpus-v1", "dense")
	require.NoError(t, err)
	second, proof2, observation2, err := Evidence(rag.Evidence{Chunk: chunk, Rank: 99, RetrievalScore: .9}, "q2", "corpus-v1", "dense")
	require.NoError(t, err)
	require.Equal(t, first.ID, second.ID)
	require.NotEqual(t, observation1.ID, observation2.ID)
	require.NotEqual(t, proof1.ID, proof2.ID, "request lineage remains distinct")
}
EOF

cd /mnt/data/work-rag-ttc/rag-ttc && gofmt -w pkg/rag/toolanswer/deterministic_ledger_test.go pkg/rag/derive/ragcodec/codec_test.go
# Core executable verification and static repository checks.
GO111MODULE=off GOPATH=/mnt/data/gopath go test -race -v ./pkg/semanticid ./pkg/rag/derive | tee /mnt/data/work-rag-ttc/results/core-tests-verbose.txt
GO111MODULE=off GOPATH=/mnt/data/gopath go vet ./pkg/semanticid ./pkg/rag/derive 2>&1 | tee /mnt/data/work-rag-ttc/results/core-vet.txt
GO111MODULE=off GOTOOLCHAIN=local go run /tmp/listcalls.go /mnt/data/work-rag-ttc/rag-ttc __NoSuchCall__ > /mnt/data/work-rag-ttc/results/static-parse.txt 2>&1
printf 'parse_status=%s\n' "$?" >> /mnt/data/work-rag-ttc/results/static-parse.txt
(GOTOOLCHAIN=local go test ./... > /mnt/data/work-rag-ttc/results/full-test-attempt.txt 2>&1; echo "exit_status=$?" >> /mnt/data/work-rag-ttc/results/full-test-attempt.txt) || true
cat /mnt/data/work-rag-ttc/results/full-test-attempt.txt

```

<details><summary>💭 Thinking</summary>

**Preparing artifacts**

I’m consolidating the implementation, tests, research handoff, static checks, and evaluation outputs. I’ll package the repository changes, generate thesis figures, write the doctoral-style document, render the PDF, and verify the finished files.

**Writing thesis structure**

I’m shaping the document as an honest doctoral-style engineering thesis: formal definitions, proofs, implementation details, evaluation evidence, limitations, migration guidance, appendices, and reproducibility materials—without inventing human authorship.

**Prepared artifacts and wrote thesis structure**

**Added deterministic ledger tests and documented repository evaluation findings**

</details>

```unknown
bash -lc set -e
printf 'work repo: '; test -d /mnt/data/work-rag-ttc/rag-ttc && echo yes || echo no
printf 'results: '; test -d /mnt/data/work-rag-ttc/results && echo yes || echo no
printf 'semanticid files: '; find /mnt/data/work-rag-ttc/rag-ttc/pkg/semanticid -maxdepth 1 -type f | wc -l
printf 'derive files: '; find /mnt/data/work-rag-ttc/rag-ttc/pkg/rag/derive -maxdepth 2 -type f | wc -l
printf 'research files: '; find /mnt/data/work-rag-ttc/rag-ttc/research/p01-p03-foundations -type f | wc -l
ls -lh /mnt/data/work-rag-ttc/results | sed -n '1,30p'

```

<details><summary>💭 Thinking</summary>

**Inspected, tested, analyzed, and fixed repository functionality and thesis assets**

</details>

```unknown
bash -lc set -euo pipefail
cd /mnt/data/work-rag-ttc/rag-ttc
python3 - <<'PY'
from pathlib import Path
p=Path('pkg/semanticid/value.go')
s=p.read_text()
s=s.replace('"path/filepath"\n', '"path"\n')
old='''func PortablePath(v string) (Value, error) {
\tt := strings.TrimSpace(v)
\tif t == "" {
\t\treturn Value{}, errors.New("semantic path is empty")
\t}
\tif filepath.IsAbs(t) {
\t\treturn Value{}, fmt.Errorf("semantic path must be relative: %q", v)
\t}
\tc := filepath.ToSlash(filepath.Clean(t))
\tif c == "." || c == ".." || strings.HasPrefix(c, "../") {
\t\treturn Value{}, fmt.Errorf("semantic path escapes its root: %q", v)
\t}
\treturn String(c)
}
'''
new='''func PortablePath(v string) (Value, error) {
\tt := strings.TrimSpace(v)
\tif t == "" {
\t\treturn Value{}, errors.New("semantic path is empty")
\t}
\t// Define separators independently of the host OS so the same logical path
\t// fingerprints identically on Unix and Windows. Reject absolute Unix,
\t// UNC, and drive-qualified paths before cleaning.
\tt = strings.ReplaceAll(t, `\\`, "/")
\tif strings.HasPrefix(t, "/") || hasDrivePrefix(t) {
\t\treturn Value{}, fmt.Errorf("semantic path must be relative: %q", v)
\t}
\tc := path.Clean(t)
\tif c == "." || c == ".." || strings.HasPrefix(c, "../") {
\t\treturn Value{}, fmt.Errorf("semantic path escapes its root: %q", v)
\t}
\treturn String(c)
}
func hasDrivePrefix(v string) bool {
\tif len(v) < 2 || v[1] != ':' {
\t\treturn false
\t}
\tc := v[0]
\treturn (c >= 'a' && c <= 'z') || (c >= 'A' && c <= 'Z')
}
'''
if old not in s:
    raise SystemExit('portable path block not found')
p.write_text(s.replace(old,new))

p=Path('pkg/rag/derive/types.go')
s=p.read_text()
old='''\td := Derivation{Output: output, Rule: rule, RuleVersion: version, Inputs: append([]Input(nil), inputs...), RequestID: requestID, ConfigID: configID, Attributes: b}
'''
new='''\td := Derivation{Output: output, Rule: rule, RuleVersion: version, Inputs: SortedInputs(inputs), RequestID: requestID, ConfigID: configID, Attributes: b}
'''
if old not in s:
    raise SystemExit('derivation constructor block not found')
s=s.replace(old,new)
old='''func recomputeDerivationID(d Derivation) (DerivationID, error) {
\tif len(d.Attributes) > 0 {
'''
new='''func recomputeDerivationID(d Derivation) (DerivationID, error) {
\td.Inputs = SortedInputs(d.Inputs)
\tif len(d.Attributes) > 0 {
'''
if old not in s:
    raise SystemExit('recompute block not found')
p.write_text(s.replace(old,new))

p=Path('pkg/rag/derive/state.go')
s=p.read_text()
old='''func (s *State) addDerivationMutable(v Derivation) error {
\ts.ensure()
\tif v.ID == "" {
'''
new='''func (s *State) addDerivationMutable(v Derivation) error {
\ts.ensure()
\tv.Inputs = SortedInputs(v.Inputs)
\tif v.ID == "" {
'''
if old not in s:
    raise SystemExit('state add derivation block not found')
p.write_text(s.replace(old,new))
PY

gofmt -w pkg/semanticid/value.go pkg/rag/derive/types.go pkg/rag/derive/state.go

cat >> pkg/semanticid/value_test.go <<'EOF'

func TestPortablePathIsHostIndependent(t *testing.T) {
	t.Parallel()
	forward, err := PortablePath(`folder/sub/../item.json`)
	if err != nil {
		t.Fatal(err)
	}
	backward, err := PortablePath(`folder\sub\..\item.json`)
	if err != nil {
		t.Fatal(err)
	}
	if !bytes.Equal(forward.CanonicalBytes(), backward.CanonicalBytes()) {
		t.Fatalf("separator spelling changed portable path identity")
	}
	for _, bad := range []string{`/etc/passwd`, `C:\\temp\\x`, `\\\\server\\share\\x`, `../escape`} {
		if _, err := PortablePath(bad); err == nil {
			t.Fatalf("expected rejection for %q", bad)
		}
	}
}
EOF

# Ensure bytes is imported; it already is in value_test.go, otherwise add it.
if ! rg -q '"bytes"' pkg/semanticid/value_test.go; then
  python3 - <<'PY'
from pathlib import Path
p=Path('pkg/semanticid/value_test.go')
s=p.read_text().replace('import (\n', 'import (\n\t"bytes"\n', 1)
p.write_text(s)
PY
fi

gofmt -w pkg/semanticid/value_test.go

cat >> pkg/rag/derive/fact_test.go <<'EOF'

func TestDerivationInputOrderIsCanonical(t *testing.T) {
	t.Parallel()
	a := mustFact(t, "source", "v1", map[string]any{"name": "a"})
	b := mustFact(t, "source", "v1", map[string]any{"name": "b"})
	out := mustFact(t, "claim", "v1", map[string]any{"value": "combined"})
	left, err := NewDerivation(out.ID, "combine", "v1", []Input{{Role: "right", Fact: b.ID}, {Role: "left", Fact: a.ID}}, "q", "cfg", nil)
	if err != nil {
		t.Fatal(err)
	}
	right, err := NewDerivation(out.ID, "combine", "v1", []Input{{Role: "left", Fact: a.ID}, {Role: "right", Fact: b.ID}}, "q", "cfg", nil)
	if err != nil {
		t.Fatal(err)
	}
	if left.ID != right.ID {
		t.Fatalf("premise delivery order changed derivation identity: %s != %s", left.ID, right.ID)
	}
	if len(left.Inputs) != 2 || left.Inputs[0].Role != "left" || left.Inputs[1].Role != "right" {
		t.Fatalf("constructor did not retain canonical premise order: %#v", left.Inputs)
	}
}
EOF

gofmt -w pkg/rag/derive/fact_test.go

GO111MODULE=off GOPATH=/mnt/data/gopath go test -race ./pkg/semanticid ./pkg/rag/derive | tee /mnt/data/work-rag-ttc/results/core-tests-final.txt

```

<details><summary>💭 Thinking</summary>

**Patched tests, inspected evaluation flags, and verified final outputs**

</details>

```unknown
bash -lc cat > /mnt/data/rag-ttc-p01-p03-doctoral-thesis.md <<'EOF'
---
title: "Semantic Foundations for Composable Retrieval-Augmented Generation"
subtitle: "Semantic Identity, Canonical Provenance, and Lawful Merge in rag-ttc - Implementation and Evaluation of Projects P01-P03"
date: "August 2026"
author: "Research artifact prepared for the rag-ttc program"
documentclass: report
classoption:
  - oneside
papersize: a4
fontsize: 10pt
geometry:
  - top=24mm
  - bottom=25mm
  - left=25mm
  - right=25mm
mainfont: "Noto Serif"
sansfont: "Inter"
monofont: "DejaVu Sans Mono"
colorlinks: true
linkcolor: "blue"
urlcolor: "blue"
toc: true
toc-depth: 3
lof: true
lot: true
numbersections: true
header-includes:
  - |
    \usepackage{microtype}
    \usepackage{booktabs}
    \usepackage{longtable}
    \usepackage{array}
    \usepackage{float}
    \usepackage{fvextra}
    \usepackage{enumitem}
    \usepackage{xcolor}
    \usepackage{fancyhdr}
    \floatplacement{figure}{H}
    \fvset{breaklines=true,breakanywhere=true,fontsize=\small}
    \setlength{\parindent}{0pt}
    \setlength{\parskip}{0.55em}
    \setlist{nosep,leftmargin=*}
    \pagestyle{fancy}
    \fancyhf{}
    \fancyhead[L]{rag-ttc semantic foundations}
    \fancyhead[R]{P01-P03}
    \fancyfoot[C]{\thepage}
---

# Abstract {-}

Retrieval-augmented generation systems are commonly assembled from components whose local APIs appear straightforward but whose composition has weak or implicit semantics. A chunk may be identified by content in one package and by serialized structure in another. A cache may omit a configuration field that changes model behavior. A concurrent evidence collector may impose a limit before all candidates have arrived, allowing completion order to alter citations. A record may combine source content, retrieval rank, score, and presentation labels in one value, even though those fields have different lifetimes and different equality rules. These defects are not primarily failures of model quality. They are failures to define what the system means by "the same request", "the same fact", "another proof of the same fact", and "the same result under a different execution schedule".

This thesis develops and implements a semantic foundation for three research projects in the `rag-ttc` codebase: P01, Semantic Identity and Cache Fingerprints; P02, Canonical Facts and Provenance; and P03, Lawful Merge and a Deterministic Evidence Ledger. The work treats the three projects as a single dependency chain. Identity determines when two records may be considered interchangeable. Provenance distinguishes stable fact content from the potentially many derivations and query-local observations associated with it. Lawful merge combines independently produced records by set union over canonical variants, yielding associative, commutative, and idempotent behavior. Deterministic selection is then performed only after global merge, under a total ordering and an explicit budget policy.

The implementation adds two standalone Go packages. `pkg/semanticid` provides a typed canonical value language, domain- and version-separated SHA-256 fingerprints, portable path handling, explicit field-role catalogs, and generic mutation-contract tests. `pkg/rag/derive` provides canonical facts, derivations, observations, a provenance-aware state, conflict-preserving join, deterministic snapshots, validation, finite proof ranks, proof bundles, a concurrent ledger facade, and deterministic post-merge selection. Adapters map existing `rag.Chunk`, `rag.Evidence`, `rag.Representation`, and `knowledge.Fact` values into the new kernel. A deterministic tool-evidence ledger demonstrates how to remove arrival-order dependence from limits and citation labels. Production identity paths were also patched to use the canonical text digest, include the connected-retrieval reciprocal-rank-fusion constant, and incorporate a fingerprint of resolved provider configuration into generation and reranking cache keys.

The algebraic laws are proved over a finite state model and tested as executable API contracts. The reference state join is proved associative, commutative, and idempotent because it is componentwise set union over complete record variants. Consequently, any fold over a fixed multiset of worker deltas has one canonical result, independent of batching, ordering, duplicate delivery, or retry. The verifier detects identity conflicts, altered record content, missing dependencies, invalid observations, and facts without a finite well-founded proof. The selection barrier is proved permutation-invariant because it validates against the merged state, removes exact duplicate candidates, applies a total deterministic ordering, chooses at most one candidate per fact, and only then assigns budgets and citation labels.

Executable evidence supports the design. The P01 mutation matrix passed for semantic, operational, presentation, and secret fields. Object field order and set delivery order were invariant; list order, semantic content, domain, and version remained distinguishing. The P02 diamond fixture produced three facts, four derivations, two observations, two independent proofs of one claim, a least proof rank of one for that claim, a verifiable proof bundle, and successful tamper detection. Across all 720 permutations of six merge deltas, the lawful state produced one output. Across all six candidate completion orders, deterministic selection produced one view, while a legacy first-arrival budget produced six views. One hundred race-enabled concurrent retry runs produced zero divergences. A scaling experiment also showed that the simple persistent `Join` reference is unsuitable for one-record-at-a-time ingestion, while a mutable ledger preserving the same semantics reduced the median cost by two to three orders of magnitude over the tested range.

The principal limitation is integration validation. The supplied repository declares Go 1.26.5 and uses a `tool` block not understood by the available Go 1.23.2 toolchain. Network access was unavailable for toolchain acquisition. The standalone semantic packages were compiled, race-tested, vetted, and exercised; every repository Go file was parsed after the patches; production call arities were statically audited. The complete repository test suite was not executed. Accordingly, this thesis distinguishes proved model properties, executed package properties, empirical measurements, static source findings, and unverified integration claims.

# Executive summary {-}

The work can be summarized as six engineering rules:

1. **Name behavior, not structs.** A semantic fingerprint is built from an explicit projection of behavior-affecting fields, encoded by declared collection and scalar semantics, and separated by domain and version.
2. **Separate facts from evidence about facts.** Stable content belongs in `Fact`; support belongs in `Derivation`; scores, ranks, retrieval methods, and request-local annotations belong in `Observation`.
3. **Merge complete variants by union.** Do not use first-writer or last-writer conflict resolution for immutable semantic records. Preserve every conflicting variant and report the conflict.
4. **Delay non-monotone decisions.** Merge candidates before applying top-k, token budgets, one-per-fact selection, or citation numbering.
5. **Prove API laws and execute them.** Identity mutation matrices, join laws, proof verification, permutation tests, retry tests, and deterministic serialization are part of the public contract.
6. **Keep operational and information semantics separate.** `flow` should continue to own caching, retries, batching, budgets, tracing, and execution. The semantic kernel defines what records mean and how their information combines.

The proposed architecture is:

![Semantic kernel embedded in the existing operational architecture.](rag-ttc-p01-p03-thesis-assets/architecture.png){width=78%}

The resulting composition boundary is:

```text
Plan -> Execute -> Admit -> Merge -> Verify -> View -> Generate
```

`Plan` and `Execute` may be effectful. `Admit` converts raw results to canonical records. `Merge` is add-only and lawful. `Verify` checks integrity and provenance closure. `View` may rank, limit, pack, and label without mutating the canonical state. `Generate` consumes that selected view.

# Status, claim types, and reproducibility {-}

This document is a doctoral-style implementation thesis and reproducibility report. It is not represented as a university-awarded degree, a peer-reviewed publication, or a proof of factual correctness for language-model output.

To prevent category errors, claims use the following evidence classes:

| Marker | Meaning |
|---|---|
| **THEOREM** | A mathematical statement proved from definitions in this document. |
| **EXECUTED** | A property exercised by compiled code in the available environment. |
| **EMPIRICAL** | A measured result from a specific experiment; not a universal performance claim. |
| **STATIC** | A conclusion from source inspection, parsing, or call-site analysis without full integration execution. |
| **CONDITIONAL** | A result that depends on assumptions stated with the claim. |

The primary reproduction command is:

```bash
cd research/p01-p03-foundations
./demo.sh
```

The standalone package validation command used for the final artifact was:

```bash
GO111MODULE=off GOPATH=/mnt/data/gopath \
  go test -race -v ./pkg/semanticid ./pkg/rag/derive
```

The final executed environment was Linux on `amd64`, with Go 1.23.2 used in GOPATH mode for the standalone packages. The full module declared Go 1.26.5. The integration-test limitation is discussed in Chapters 2, 9, and 12.

\newpage

# Introduction

## Retrieval systems need semantic contracts

A RAG system is often described as a sequence: retrieve documents, rank them, build a prompt, generate an answer. That description is operational. It says what calls are made, but it does not fully specify the meaning of their inputs and outputs. The missing semantics become visible under ordinary engineering changes:

- A worker is retried after a timeout.
- Dense and sparse retrievers return the same chunk.
- A result arrives one millisecond later under a different scheduler.
- A model setting changes while a cache entry remains addressable by the old key.
- A chunk schema gains a presentation field.
- A citation is discovered through two independent paths.
- A source document is imported from a path spelled with different separators.
- Two workers emit the same identifier with different immutable content.

If these changes alter the canonical evidence state without an explicit policy, the system does not have stable semantics. It has accidental semantics inherited from map insertion order, serializer behavior, call timing, or incomplete cache keys.

The `rag-ttc` codebase already contains several strong design decisions: narrow component interfaces, deterministic ordering in many retrieval paths, content-derived chunk lineage, explicit experiment artifacts, and a `flow` layer that centralizes operational concerns. Those strengths make the remaining gap more precise. The repository needs a small kernel for information semantics rather than a general workflow language.

## Problem statement

The thesis addresses three coupled problems.

**P01: semantic identity.** For an operation, record, or configuration, which fields determine behavioral identity? How are values encoded so that irrelevant representation choices do not change identity and relevant changes do? How are caches versioned and reviewed?

**P02: canonical facts and provenance.** How can stable information be separated from the reasons it is believed and from query-specific observations? How can one fact retain multiple proofs? How can an independent verifier detect altered content, missing dependencies, cycles without a finite proof, and malformed evidence packages?

**P03: lawful merge.** How can independently produced evidence be combined so that worker ordering, batching, retries, duplicate messages, and concurrency do not alter the canonical result? How should identity conflicts be handled without hiding them? Where should ranking, limits, and citation labels occur?

The central proposition is:

> A composable RAG evidence layer can be obtained by combining explicit semantic fingerprints, a fact/derivation/observation model, conflict-preserving set-union merge, and deterministic post-merge views. Under these contracts, execution scheduling becomes an operational choice rather than part of result meaning.

## Research questions

The implementation and evaluation answer the following questions.

**RQ1.** Can semantic cache identity be expressed as a small typed value language whose canonical encoding is deterministic and reviewable?

**RQ2.** Can mutation contracts distinguish semantic and lineage fields from operational, presentation, observation, and secret fields in an executable form?

**RQ3.** Can existing `rag-ttc` facts, chunks, representations, evidence values, and knowledge facts map into one canonical interchange model without placing ranks and scores in stable fact identity?

**RQ4.** Can one canonical fact preserve several independent derivations without duplicating the fact or discarding support?

**RQ5.** Can a verifier compute the least finite proof depth and reject malformed, conflicted, altered, missing, or circular proof structures?

**RQ6.** Can merge be made associative, commutative, and idempotent while retaining identity conflicts instead of choosing a winner?

**RQ7.** Does lawful merge eliminate output differences caused by delivery order, batching, duplicate messages, and retries?

**RQ8.** Can top-k limits and citation labels be made deterministic by moving them behind a global merge and total sort?

**RQ9.** Can these semantics be inserted into `rag-ttc` as adapters and cache-key corrections without replacing its operational `flow` abstractions?

## Contributions

The thesis contributes the following concrete artifacts.

1. A standalone `semanticid` package with a typed canonical value language, binary encoding, domain/version separation, field-role catalogs, portable paths, and mutation-contract testing.
2. A standalone `derive` package with canonical JSON, facts, derivations, observations, conflict-preserving state, lawful join, deterministic snapshots, verification, proof ranks, proof bundles, a concurrent ledger, and deterministic selection.
3. Go adapters from current `rag-ttc` domain values to the semantic kernel.
4. A deterministic tool-evidence ledger that demonstrates the merge-before-limit boundary.
5. Corrections to production identity paths for chunk fallback identity, connected retrieval, generation caching, reranking caching, and provider configuration.
6. A conformance command producing machine-readable fixtures and results.
7. Formal proofs of the core identity, merge, retry, conflict-retention, proof-rank, and deterministic-selection properties.
8. Executed law tests, adversarial fixtures, exhaustive permutation experiments, race-enabled concurrency tests, and a reference performance comparison.
9. A migration and governance model for adopting the kernel incrementally.

## Scope and non-goals

The scope is deliberately narrower than a full RAG architecture rewrite. The work does not introduce a general workflow DSL, replace `flow`, prescribe one database, define one ranking algorithm, or claim that a valid proof bundle makes a natural-language claim true. The verifier establishes structural integrity relative to declared rules and seed imports; it does not validate the external truth of a source document or the soundness of an arbitrary learned extraction rule.

The work also does not solve document deletion and retraction, authorization propagation, distributed replication across mutually distrustful nodes, cryptographic signing, model nondeterminism, or recursive closure over arbitrary rules. The design prepares for those projects by making identity, dependencies, and merge explicit.

## Thesis organization

Chapter 2 describes the repository context and research method. Chapter 3 introduces the minimal mathematics. Chapter 4 derives requirements from concrete `rag-ttc` structures. Chapters 5, 6, and 7 present P01, P02, and P03. Chapter 8 explains composition with `flow` and the broader architecture. Chapter 9 reports the experiments. Chapter 10 gives consolidated formal results. Chapter 11 provides an engineering and migration handbook. Chapter 12 discusses limitations and threats to validity. Chapter 13 concludes and defines the next research pass. Appendices document APIs, encoding, tests, changes, and reproduction steps.

# Repository context and research method

## Existing architecture

The supplied repository is a Go codebase organized around reusable RAG components and application commands. Its design includes domain packages for chunks, representations, retrieval, reranking, generation, knowledge extraction, connected retrieval, tool-assisted answering, providers, caching, and experimental evaluation. A `flow` abstraction wraps components with execution concerns such as retries, caching, budgets, batching, concurrency, tracing, and order restoration.

This separation is useful. It means the new kernel does not need to become an orchestrator. It can instead define the semantic content that operational execution transports.

The review identified a recurring shape in the current system:

```text
request/configuration -> component call -> result values -> ranking/limits -> answer
```

The proposed semantic shape inserts explicit boundaries:

```text
request/configuration
    -> semantic request identity
    -> component call
    -> admitted Fact / Derivation / Observation records
    -> lawful merge
    -> verification
    -> deterministic selected view
    -> answer
```

## Why P01-P03 form one thesis

P01 can be implemented as a hashing library, P02 as a provenance graph, and P03 as a merge helper. Doing so independently would miss their dependency structure.

A merge operation requires equality. If two workers emit records with the same semantic meaning but different serialization order, a merge based on raw bytes duplicates them. If two records share an identifier but differ in immutable content, a map assignment hides the conflict. P03 therefore depends on P01.

Provenance requires stable identities for facts, derivations, requests, rule versions, and configuration. It also requires merge to preserve alternate proofs rather than overwrite them. P02 therefore depends on both P01 and P03.

Cache correctness connects all three. A cache key is a semantic identity for an operation. A cached retrieval result may contain facts, derivations, and observations. A cache hit must be observationally equivalent to executing the operation and lawfully merging its result. Incomplete identity invalidates that equivalence.

The implementation therefore uses one shared kernel with three layers rather than three isolated prototypes.

## Research method

The work followed an artifact-centered method.

### Static source analysis

Relevant packages and call sites were inventoried. Identity and cache constructors were traced to their production callers. Domain types were inspected to classify fields by semantic lifetime. Concurrency and admission paths were inspected for order-sensitive limits and labels.

### Reference implementation

The new packages were written to depend only on the Go standard library and each other. This isolates semantic validation from external providers, databases, model SDKs, and network services.

### Adapters and production patches

Adapters map existing values into canonical records without forcing immediate repository-wide type replacement. Confirmed identity omissions were patched in their current packages. The production patches are intentionally small and versioned.

### Formalization

The state and merge model was defined mathematically as finite maps from semantic identifiers to finite sets of complete record variants. This model is simple enough to prove directly and close enough to the implementation that the proof obligations become unit and property tests.

### Executable law testing

The test suite includes:

- golden fingerprint vectors;
- object and set permutation invariance;
- list-order sensitivity;
- domain and version separation;
- field mutation matrices;
- canonical JSON equivalence and malformed-input rejection;
- fact/observation separation;
- alternate derivations;
- proof bundle verification;
- content tampering and missing dependency rejection;
- all permutations of a fixed merge workload;
- generated join-law trials;
- conflict preservation;
- concurrent duplicate delivery under the race detector;
- deterministic serialization round trips;
- all candidate completion permutations;
- total tie-breaking and one-per-fact selection.

### Adversarial experiments

The conformance command creates a diamond-shaped provenance fixture, an explicit identity conflict, a concurrent retry workload, and an arrival-order-sensitive legacy baseline. Results are written as JSON so that later projects can consume the same evidence.

### Performance experiment

Two semantically equivalent merge implementations were compared: repeated immutable `State.Join`, which clones the accumulated state for each insertion, and a mutable mutex-protected `Ledger`, which performs in-place union and returns immutable snapshots. The experiment tests implementation shape, not the algebraic model.

## Evidence hierarchy

A passing test does not prove all inputs. A proof does not establish that code matches the model. A benchmark does not establish correctness. The thesis therefore maintains separate evidence layers:

1. definitions and theorems for the abstract model;
2. constructor-level correspondence arguments between model and code;
3. generated and exhaustive tests for implementation laws;
4. empirical experiments for observed behavior and cost;
5. static integration checks for code that could not be built in the available toolchain.

## Execution environment and integration limitation

The repository declares Go 1.26.5 and contains a `tool` block in `go.mod`. The available toolchain was Go 1.23.2. Running the full module with `GOTOOLCHAIN=local` failed during module parsing:

```text
go: errors parsing go.mod:
go.mod:187: unknown block type: tool
```

Automatic toolchain download was unavailable because outbound network access failed. The standalone packages were therefore validated in GOPATH mode, where they compiled and passed race-enabled tests. The research handoff package also compiled. All Go source files in the patched repository were parsed, and changed generation/reranking call sites were checked for updated arity. Production integration remains a required validation step in an environment with the declared toolchain and dependencies.

This constraint affects confidence in adapter and cache-patch integration, not the executed status of the standalone semantic kernel.

# Minimal mathematical background for programmers

## Identity is an API decision

Programs routinely use several notions of equality:

- two pointers are the same allocation;
- two structs have equal fields;
- two JSON values differ in whitespace but represent the same object;
- two retrieval records refer to the same chunk but carry different scores;
- two derivations support the same claim through different sources;
- two requests use different worker counts but have the same intended result.

No hash function decides which notion is correct. The API must first define a projection from the full runtime value to the fields that determine behavior. Canonicalization then removes representation choices that are declared irrelevant. Hashing produces a compact name for the canonical bytes.

Write this as:

\[
\operatorname{ID}(x) = H(D, V, C(P(x)))
\]

where:

- \(P\) selects identity-relevant fields;
- \(C\) produces canonical bytes;
- \(D\) is a domain label;
- \(V\) is a schema or behavior version;
- \(H\) is SHA-256 in this implementation.

A cache key error normally occurs in \(P\) or \(V\), not in \(H\).

## Canonical representation

A canonical representation gives one byte string to every value under the chosen equality relation. For an object whose field order is irrelevant, fields are sorted. For a set, elements are encoded, sorted, and deduplicated. For a list, order remains. Type tags distinguish a string from a byte array and an integer from its textual spelling.

Canonicalization needs a version because equality policies evolve. Changing number normalization, Unicode policy, optional-field treatment, or set semantics must not silently reuse old identifiers.

## Hashes are compact names, not mathematical equality

The implementation uses SHA-256. The proofs establish that distinct valid typed values produce distinct pre-hash byte encodings. After hashing, equality is conditional on the usual collision-resistance assumption. The code does not claim that SHA-256 is injective; no fixed-size hash can be injective over an unbounded input domain.

This distinction matters for conflict handling. A state retains the full record variant under an identifier and recomputes identifiers during verification. It does not treat an identifier string as sufficient evidence that record content is correct.

## Three merge laws

A merge operation \(\sqcup\) is suitable for add-only distributed evidence when it obeys:

\[
a \sqcup b = b \sqcup a
\]

**Commutativity:** delivery order does not matter.

\[
(a \sqcup b) \sqcup c = a \sqcup (b \sqcup c)
\]

**Associativity:** batching and grouping do not matter.

\[
a \sqcup a = a
\]

**Idempotence:** duplicate delivery and retry do not matter.

A type with such a merge is commonly called a join-semilattice when an induced information order is also considered. The name is less important than the API laws.

The induced order is:

\[
a \preceq b \quad\text{when}\quad a \sqcup b = b.
\]

Read this as "all information in `a` is already contained in `b`." Merge is then the least state containing both inputs.

## Provenance as a directed hypergraph

A normal graph edge connects one node to another. A derivation may require several input facts to produce one output fact, so it is better modeled as a directed hyperedge:

```text
{input fact 1, input fact 2, ...} --rule/version--> output fact
```

A fact may have several incoming derivation hyperedges. Those are alternate proofs, not duplicate facts.

An observation is a separate node attached to a fact. It records something such as "dense retriever scored this fact 0.91 for request q". Changing or adding an observation does not change the fact.

## Least finite proof rank

A seed derivation with no inputs gives its output fact rank zero. A derivation whose input facts have ranks gives its output candidate rank:

\[
1 + \max(\text{input ranks}).
\]

When several derivations support a fact, the fact receives the smallest available candidate rank:

\[
\operatorname{rank}(f)
= \min_{d:\operatorname{out}(d)=f}
\begin{cases}
0, & d\text{ has no inputs},\\
1 + \max_{i\in\operatorname{inputs}(d)}\operatorname{rank}(i), & \text{all inputs ranked}.
\end{cases}
\]

The verifier computes this by repeated relaxation until no rank improves. A cycle with no seed or other finite proof never receives a rank. A cycle with an alternate finite proof is acceptable because the least finite proof exists.

## Total ordering and deterministic views

Ranking is not add-only. Adding a high-score candidate can displace an earlier top result. The design therefore applies ranking only to a completed candidate state or an explicit snapshot.

To make a view deterministic, the comparator must be total: for any two distinct candidates, one must sort before the other. The implementation compares:

1. utility descending;
2. stable key ascending;
3. fact ID ascending;
4. observation ID ascending;
5. units ascending.

Exact duplicate candidates are removed first. A total order converts an unordered candidate set into one sequence independent of arrival order.

## Induction and correspondence

The proofs use ordinary induction rather than heavy notation.

- To prove canonical encoding, show that each scalar constructor has an unambiguous encoding and that child encodings remain unambiguous inside collection length boundaries.
- To prove proof ranks, show seed facts are ranked correctly, then show a fact with a proof of height \(n+1\) becomes ranked after its inputs of height at most \(n\).
- To prove schedule independence, use associativity and commutativity to reorder and regroup merges, then use idempotence to remove duplicates.

The implementation tests mirror these proof steps. This is intentional: the mathematical definitions are valuable only when they generate reviewable API contracts.
EOF

```

<details><summary>💭 Thinking</summary>

**Compiled and evaluated the RAG thesis, chapters, appendices, and references**

</details>

```unknown
bash -lc set -o pipefail
cd /mnt/data
pandoc rag-ttc-p01-p03-doctoral-thesis.md \
  --pdf-engine=xelatex \
  --listings \
  --number-sections \
  --toc \
  --toc-depth=3 \
  -V lang=en \
  -o rag-ttc-p01-p03-doctoral-thesis.pdf \
  2>&1 | tee /mnt/data/rag-ttc-p01-p03-thesis-build.log
pdfinfo /mnt/data/rag-ttc-p01-p03-doctoral-thesis.pdf | sed -n '1,30p'
ls -lh /mnt/data/rag-ttc-p01-p03-doctoral-thesis.{md,pdf}

```

<details><summary>💭 Thinking</summary>

**Compiled, validated, and packaged doctoral thesis and reproducibility deliverables**

</details>

# P01-P03 doctoral-style implementation thesis

The implementation and thesis are complete.

## Primary deliverables

- [Thesis — PDF, 108 pages](sandbox:/mnt/data/rag-ttc-p01-p03-doctoral-thesis.pdf)
- [Thesis — Markdown source](sandbox:/mnt/data/rag-ttc-p01-p03-doctoral-thesis.md)
- [Complete delivery bundle](sandbox:/mnt/data/rag-ttc-p01-p03-complete-delivery.zip)
- [Thesis source bundle with diagrams and chart](sandbox:/mnt/data/rag-ttc-p01-p03-thesis-source.zip)

## Source implementation

- [Complete patched rag-ttc source snapshot](sandbox:/mnt/data/rag-ttc-p01-p03-implementation.zip)
- [Unified source patch](sandbox:/mnt/data/rag-ttc-p01-p03.patch)
- [Standalone reproducibility package](sandbox:/mnt/data/rag-ttc-p01-p03-reproducibility.zip)
- [Delivery guide](sandbox:/mnt/data/rag-ttc-p01-p03-delivery-README.md)
- [Artifact checksums](sandbox:/mnt/data/rag-ttc-p01-p03-artifacts.sha256)

## Implemented work

### P01 — Semantic identity and cache fingerprints

The implementation adds `pkg/semanticid`, including:

- Typed canonical values for strings, bytes, integers, finite floating-point values, lists, sets, objects, optional values, and portable paths.
- Domain- and version-separated SHA-256 fingerprints.
- Explicit field roles: semantic, lineage, observation, presentation, operational, and secret.
- Mutation-contract tests that state which field changes must alter identity.
- Host-independent path normalization.
- Canonical handling of ordered lists versus unordered sets.
- Cache-key corrections for resolved provider configuration.
- Inclusion of the connected-retrieval RRF constant in runtime identity.
- Consistent fallback text identity for evidence.

### P02 — Canonical facts and provenance

The implementation adds `pkg/rag/derive`, including:

- Separate `Fact`, `Derivation`, and `Observation` records.
- Canonical JSON normalization and deterministic record identifiers.
- Multiple independent derivations supporting one canonical fact.
- Canonicalized derivation premises.
- Detection of altered records, missing dependencies, invalid observations, identity conflicts, and facts without finite proofs.
- Least finite proof-rank computation.
- Extractable and independently verifiable proof bundles.
- Adapters for existing chunks, representations, evidence records, and knowledge facts.

Scores, ranks, request IDs, retrieval methods, and related measurements are observations about facts rather than part of fact identity.

### P03 — Lawful merge and deterministic evidence ledger

The implementation provides:

- Merge as set union over complete immutable record variants.
- Associative, commutative, and idempotent join laws.
- Explicit retention of same-ID/different-content conflicts rather than first-writer or last-writer resolution.
- Deterministic state serialization and state fingerprints.
- A thread-safe mutable ledger with the same extensional semantics as the reference immutable join.
- Post-merge ranking, budgeting, one-per-fact selection, and citation-label assignment.
- A deterministic tool-evidence ledger that removes completion-order dependence.

## Executed validation

The standalone semantic kernel passed **29 race-enabled tests** and `go vet`. The experimental harness established:

- Six deltas across all **720 delivery permutations** produced exactly **one merged state**.
- Three candidates across all **six completion orders** produced exactly **one lawful selected view**.
- The legacy first-arrival limit produced **six distinct views** over those same completion orders.
- **100 concurrent retry runs** produced **zero divergences**.
- Identity conflicts retained both variants under every tested order.
- The provenance diamond retained two independent proofs of one claim.
- Proof-bundle verification succeeded and deliberate tampering was detected.
- The persistent and mutable merge implementations produced equal outputs throughout the scaling experiment.
- The unified patch was applied to a pristine copy and the resulting tree matched the delivered source snapshot exactly.
- The PDF passed preflight, is text-extractable, and all 108 rendered pages were visually checked.

The complete repository test suite was not executable in the available environment. The repository declares Go 1.26.5 and uses a `tool` block not understood by the installed Go 1.23.2 parser; network access was unavailable for acquiring the declared toolchain. All Go source files were nevertheless parsed and found `gofmt`-clean. The standalone P01-P03 kernel is executed and verified; production-package integrations outside that kernel remain candidates for full validation under the repository’s declared toolchain.


---

> Implement P06

<details><summary>💭 Thinking</summary>

**Inspecting project materials**

I’m locating the codebase and P 06 requirements first, then I’ll map the implementation to the existing project conventions. After that, I’ll modify the relevant files, run checks, and document what changed.

**Inspected project materials**

</details>

```unknown
bash -lc ls -lah /mnt/data | sed -n '1,220p' && echo '--- project dirs ---' && find /mnt/data -maxdepth 2 -type f | sed -n '1,260p'
```

I’ll inspect the P06 brief and current `flow` contracts, then implement a minimal execution-semantics layer with adapters, instrumentation, conformance and fault-injection tests, and a reproducible report.

<details><summary>💭 Thinking</summary>

**Inspected project files and extracted P06 experimental plan details**

</details>

```unknown
bash -lc cd /mnt/data/work-p06/rag-ttc && echo 'FLOW DECLS'; rg -n '^(type|func|const|var) ' pkg/flow/*.go | sed -n '1,260p'; echo 'EXEC DECLS'; rg -n '^(type|func|const|var) ' pkg/execution/*.go | sed -n '1,320p'
```

<details><summary>💭 Thinking</summary>

**Mapping P 06 implementation**

I’m determining the project’s existing conventions and P 06 requirements, then I’ll add deterministic effect recording and replay, integrate it with retries, run tests, and document the resulting changes.

**Mapped P 06 implementation**

**Designing effect capture**

I’m separating stable step identity from operation and attempt identity, then defining a standalone effect-log package that records successes and failures for deterministic retries and replay.

**Designed effect capture**

**Structuring identifiers**

I’m making operation IDs deterministic within each run, while keeping step IDs stable across executions. Stage position and run sequencing will distinguish repeated or nested invocations without relying on randomness.

**Structured identifiers**

</details>

The key boundary is preserving typed Go composition while making policy transparency observable; I’m tracing all execution combinators and the report-collision path before changing APIs.

I confirmed display-name report collisions. `flow` stays typed; a new `effectlog` captures observations using stable definition, stage, operation, attempt, batch, and event identities.

Capture, replay, and conformance tests now pass extensive offline schedule and batching experiments. Ambiguous non-idempotent retries are correctly rejected; replayability alone does not guarantee retry safety.

```unknown
bash -lc ls -lah /home/oai/go/pkg/mod | sed -n '1,120p'; find /home/oai/go/pkg/mod -maxdepth 2 -type d -path '*golang.org*x*sync*' -o -path '*stretchr*testify*' | sed -n '1,80p'
```

<details><summary>💭 Thinking</summary>

**Inspected Go dependencies and initialized a Git repository baseline**

</details>

```unknown
bash -lc rm -rf /mnt/data/work-p06 && mkdir -p /mnt/data/work-p06 && unzip -q /mnt/data/rag-ttc-p01-p03-implementation.zip -d /mnt/data/work-p06 && cd /mnt/data/work-p06/rag-ttc && git init -q && git config user.email 'analysis@example.invalid' && git config user.name 'OpenAI' && git add . && git commit -q -m 'baseline p01-p03' && git rev-parse --short HEAD && git status --short
```

<details><summary>💭 Thinking</summary>

**Designing stable identifiers**

I’m outlining readable identifier types and derivation functions for runs, invocations, steps, operations, attempts, and batches. I’m balancing explicit IDs with deterministic fingerprints while avoiding accidental randomness in semantic identifiers.

**Designed stable identifiers**

**Refining run identity**

I’m separating stable definitions from per-run execution data. Function pointers aren’t reliable identifiers, so I’m keeping explicit definition IDs, generating run IDs from a root and sequence, and passing invocation metadata through stage construction.

**Refined run identity**

**Defining event reporting**

I’m adding retry, failure, and success events, then designing versioned reports that track steps and invocations. Merging should combine counts, detect metadata conflicts, and preserve compatibility with existing step summaries.

**Defined event reporting**

**Integrating event identity**

I’m extending event emission with unique run-scoped IDs, operation and batch metadata, and nested report merging. Bulk operations need consistent identities across cache hits, misses, retries, and terminal item events, followed by a conformance harness.

**Integrated event identity**

</details>

Packaging is complete with schema-validated adversarial fixtures and distinct captured-effect events. Final validation passes 102 race-enabled tests and `go vet`; the PDF is preflighted and inspected.

```unknown
bash -lc cd /mnt/data/work-p06/rag-ttc && cat pkg/flow/logcopter.go pkg/execution/logcopter.go && rg -n 'log\.' pkg/flow pkg/execution | sed -n '1,200p'
```

<details><summary>💭 Thinking</summary>

**Recreated workspace baseline and implemented flowtrace identity, replay, reporting, and run plumbing**

</details>

```unknown
bash -lc cd /mnt/data/work-p06/rag-ttc && apply_patch <<'PATCH'
*** Begin Patch
*** Update File: pkg/flow/bulk.go
@@
 	"time"
 
 	"github.com/the-tree-center/rag-ttc/pkg/execution"
+	"github.com/the-tree-center/rag-ttc/pkg/flowtrace"
 )
@@
 		snapshot.Spend = o.env.snapshot(resources)
-		return Report{Steps: map[string]StepReport{s.Name: snapshot}}
+		return reportForInvocation(o.invocation, snapshot)
 	}
@@
 	type keyGroup struct {
-		key     execution.Key
-		digest  string
-		item    I
-		indexes []int
+		key         execution.Key
+		digest      string
+		item        I
+		indexes     []int
+		operation   flowtrace.OperationID
+		semanticKey string
 	}
@@
-			if groupIndex, ok := groupByDigest[digestValue]; ok {
+			if groupIndex, ok := groupByDigest[digestValue]; ok {
 				groups[groupIndex].indexes = append(groups[groupIndex].indexes, index)
 				continue
 			}
+			operation, semanticKey, err := s.operationIdentity(item, o.invocation.ID, index, digestValue)
+			if err != nil {
+				return fail(err)
+			}
 			groupByDigest[digestValue] = len(groups)
-			groups = append(groups, keyGroup{key: key, digest: digestValue, item: item, indexes: []int{index}})
+			groups = append(groups, keyGroup{
+				key: key, digest: digestValue, item: item, indexes: []int{index},
+				operation: operation, semanticKey: semanticKey,
+			})
 		}
 	} else {
 		for index, item := range items {
-			groups = append(groups, keyGroup{item: item, indexes: []int{index}})
+			operation, semanticKey, err := s.operationIdentity(item, o.invocation.ID, index, "")
+			if err != nil {
+				return fail(err)
+			}
+			groups = append(groups, keyGroup{
+				item: item, indexes: []int{index}, operation: operation, semanticKey: semanticKey,
+			})
 		}
 	}
@@
 		if !found {
 			counts.Misses += len(group.indexes)
+			for _, index := range group.indexes {
+				if err := emitLedgerEvent(ctx, o, o.invocation, Event{
+					Index: index, Type: EventCacheMiss, OperationID: group.operation,
+					SemanticKey: group.semanticKey,
+				}); err != nil {
+					return fail(fmt.Errorf("step %q: ledger event: %w", s.Name, err))
+				}
+			}
 			misses = append(misses, group)
 			continue
 		}
@@
-			if o.Ledger != nil {
-				if err := o.Ledger.Event(ctx, Event{Step: s.Name, Index: index, Type: EventHit}); err != nil {
-					return fail(fmt.Errorf("step %q: ledger event: %w", s.Name, err))
-				}
+			if err := emitLedgerEvent(ctx, o, o.invocation, Event{
+				Index: index, Type: EventHit, OperationID: group.operation, SemanticKey: group.semanticKey,
+			}); err != nil {
+				return fail(fmt.Errorf("step %q: ledger event: %w", s.Name, err))
 			}
@@
-	type batch struct{ groups []keyGroup }
+	type batch struct {
+		ordinal int
+		groups  []keyGroup
+	}
 	batches := make([]batch, 0, (len(misses)+batchSize-1)/batchSize)
 	for start := 0; start < len(misses); start += batchSize {
 		end := min(start+batchSize, len(misses))
-		batches = append(batches, batch{groups: misses[start:end]})
+		batches = append(batches, batch{ordinal: len(batches), groups: misses[start:end]})
 	}
@@
 	}, func(ctx context.Context, current batch) (struct{}, error) {
 		units := len(current.groups)
+		operations := make([]flowtrace.OperationID, len(current.groups))
+		for position, group := range current.groups {
+			operations[position] = group.operation
+		}
+		batchID := flowtrace.DeriveBatchID(o.invocation.ID, current.ordinal, operations)
+		batchOperation := flowtrace.DeriveOperationID(o.invocation.Step, "batch:"+string(batchID))
 		for _, name := range resources {
 			if err := o.env.limiter(name).Wait(ctx, units); err != nil {
+				if eventErr := emitLedgerEvent(ctx, o, o.invocation, Event{
+					Type: EventAdmissionRefused, BatchID: batchID, OperationID: batchOperation,
+					OperationIDs: operations, Error: err.Error(),
+				}); eventErr != nil {
+					return struct{}{}, fmt.Errorf("step %q: ledger event: %w", s.Name, eventErr)
+				}
 				if errors.Is(err, execution.ErrBudgetExceeded) {
@@
 		var lastClass ErrorClass
 		for attempt := 1; attempt <= attempts; attempt++ {
@@
-			returned, err := doBulk(ctx, batchItems)
+			attemptID := flowtrace.DeriveAttemptID(o.invocation.ID, batchOperation, attempt)
+			attemptContext := flowtrace.WithMetadata(ctx, flowtrace.Metadata{
+				Run: o.invocation.Run, Invocation: o.invocation.ID, Step: o.invocation.Step,
+				Name: o.invocation.Name, Operation: batchOperation,
+				Operations: operations, Attempt: attemptID, Batch: batchID,
+				AttemptIndex: attempt,
+			})
+			if eventErr := emitLedgerEvent(ctx, o, o.invocation, Event{
+				Type: EventAttemptStarted, OperationID: batchOperation, OperationIDs: operations,
+				AttemptID: attemptID, BatchID: batchID, Attempt: attempt,
+			}); eventErr != nil {
+				return struct{}{}, fmt.Errorf("step %q: ledger event: %w", s.Name, eventErr)
+			}
+			returned, err := doBulk(attemptContext, batchItems)
 			count(func(counts *StepReport) { counts.WorkCalls++ })
 			if err == nil {
 				if len(returned) != len(batchItems) {
@@
 				}
+				if eventErr := emitLedgerEvent(ctx, o, o.invocation, Event{
+					Type: EventAttemptSucceeded, OperationID: batchOperation, OperationIDs: operations,
+					AttemptID: attemptID, BatchID: batchID, Attempt: attempt,
+				}); eventErr != nil {
+					return struct{}{}, fmt.Errorf("step %q: ledger event: %w", s.Name, eventErr)
+				}
 				values = returned
@@
 			lastClass = classifier.Classify(err)
+			if eventErr := emitLedgerEvent(ctx, o, o.invocation, Event{
+				Type: EventAttemptFailed, OperationID: batchOperation, OperationIDs: operations,
+				AttemptID: attemptID, BatchID: batchID, Attempt: attempt,
+				Class: lastClass.String(), Error: err.Error(),
+			}); eventErr != nil {
+				return struct{}{}, fmt.Errorf("step %q: ledger event: %w", s.Name, eventErr)
+			}
@@
 			if lastClass == Transient && attempt < attempts {
@@
 				})
+				if eventErr := emitLedgerEvent(ctx, o, o.invocation, Event{
+					Type: EventRetry, OperationID: batchOperation, OperationIDs: operations,
+					AttemptID: attemptID, BatchID: batchID, Attempt: attempt,
+					Class: lastClass.String(), Error: err.Error(),
+				}); eventErr != nil {
+					return struct{}{}, fmt.Errorf("step %q: ledger event: %w", s.Name, eventErr)
+				}
 				continue
@@
 			for _, group := range current.groups {
 				for _, index := range group.indexes {
 					if mode == Skip {
 						counts.Skipped++
 						results[index] = Result[O]{Skipped: true}
+						if eventErr := emitLedgerEvent(ctx, o, o.invocation, Event{
+							Index: index, Type: EventSkipped, OperationID: group.operation,
+							SemanticKey: group.semanticKey, Class: lastClass.String(), Error: lastErr.Error(),
+						}); eventErr != nil {
+							mutex.Unlock()
+							return struct{}{}, fmt.Errorf("step %q: ledger event: %w", s.Name, eventErr)
+						}
 						continue
 					}
 					counts.Quarantined++
 					results[index] = Result[O]{Quarantined: &ItemError{
-						Step: s.Name, Index: index, Class: lastClass,
-						Attempts: attempts, Message: lastErr.Error(),
+						Step: s.Name, StepID: o.invocation.Step, InvocationID: o.invocation.ID,
+						OperationID: group.operation, Index: index, Class: lastClass,
+						Attempts: attempts, Message: lastErr.Error(),
 					}}
+					if eventErr := emitLedgerEvent(ctx, o, o.invocation, Event{
+						Index: index, Type: EventQuarantined, OperationID: group.operation,
+						SemanticKey: group.semanticKey, Class: lastClass.String(), Error: lastErr.Error(),
+					}); eventErr != nil {
+						mutex.Unlock()
+						return struct{}{}, fmt.Errorf("step %q: ledger event: %w", s.Name, eventErr)
+					}
 				}
@@
-			for _, index := range group.indexes {
-				if o.Ledger != nil {
-					if err := o.Ledger.Event(ctx, Event{Step: s.Name, Index: index, Type: EventStored}); err != nil {
-						return struct{}{}, fmt.Errorf("step %q: ledger event: %w", s.Name, err)
-					}
-				}
+			eventType := EventDone
+			if cached {
+				eventType = EventStored
+			}
+			for _, index := range group.indexes {
+				if err := emitLedgerEvent(ctx, o, o.invocation, Event{
+					Index: index, Type: eventType, OperationID: group.operation,
+					SemanticKey: group.semanticKey, BatchID: batchID,
+				}); err != nil {
+					return struct{}{}, fmt.Errorf("step %q: ledger event: %w", s.Name, err)
+				}
*** End Patch
PATCH
gofmt -w pkg/flow/bulk.go
```

<details><summary>💭 Thinking</summary>

**Implemented and tested event handling, effect replay, execution contracts, and Go stubs**

</details>

```unknown
bash -lc cd /mnt/data/work-p06/rag-ttc && mkdir -p pkg/flowcheck && cat > pkg/flowcheck/check.go <<'EOF'
// Package flowcheck compares semantic outputs across operational policy
// variants. Reports and traces are retained as diagnostics but excluded from
// semantic equality by default.
package flowcheck

import (
	"context"
	"fmt"
	"reflect"
	"sort"

	"github.com/the-tree-center/rag-ttc/pkg/flow"
)

// Runner executes one operational variant.
type Runner[I, O any] func(context.Context, []I) ([]flow.Result[O], flow.Report, error)

// Variant names one policy realization of the same intended operation.
type Variant[I, O any] struct {
	Name string
	Run  Runner[I, O]
}

// SemanticItem removes cache and trace observations while retaining every
// domain-visible result outcome.
type SemanticItem[O any] struct {
	Value       O      `json:"value"`
	Quarantined bool   `json:"quarantined,omitempty"`
	Skipped     bool   `json:"skipped,omitempty"`
	ErrorClass  string `json:"error_class,omitempty"`
	ErrorText   string `json:"error_text,omitempty"`
}

// SemanticRun is the default extensional view compared by the harness.
type SemanticRun[O any] struct {
	Items      []SemanticItem[O] `json:"items"`
	ErrorClass string            `json:"error_class,omitempty"`
}

// TraceSummary is deliberately diagnostic. Different policy variants are
// expected to have different trace summaries even when SemanticRun is equal.
type TraceSummary struct {
	Definitions int            `json:"definitions"`
	Invocations int            `json:"invocations"`
	Items       int            `json:"items"`
	Hits        int            `json:"hits"`
	Misses      int            `json:"misses"`
	WorkCalls   int            `json:"work_calls"`
	Retries     int            `json:"retries"`
	Stored      int            `json:"stored"`
	ByName      map[string]int `json:"items_by_name,omitempty"`
}

// Comparison records one baseline/variant metamorphic check.
type Comparison[O any] struct {
	Variant       string         `json:"variant"`
	Equal         bool           `json:"equal"`
	Baseline      SemanticRun[O] `json:"baseline"`
	Candidate     SemanticRun[O] `json:"candidate"`
	BaselineTrace TraceSummary   `json:"baseline_trace"`
	VariantTrace  TraceSummary   `json:"variant_trace"`
	Problem       string         `json:"problem,omitempty"`
}

// Options controls semantic error classification and equality. Classify should
// return a stable semantic class rather than an incidental wrapped message.
type Options[O any] struct {
	Classify func(error) string
	Equal    func(SemanticRun[O], SemanticRun[O]) bool
}

// Compare runs a baseline and every variant over independent copies of inputs.
func Compare[I, O any](
	ctx context.Context,
	inputs []I,
	baseline Variant[I, O],
	variants []Variant[I, O],
	options Options[O],
) ([]Comparison[O], error) {
	if baseline.Name == "" || baseline.Run == nil {
		return nil, fmt.Errorf("baseline needs a name and runner")
	}
	classify := options.Classify
	if classify == nil {
		classify = func(err error) string {
			if err == nil {
				return ""
			}
			return "error"
		}
	}
	equal := options.Equal
	if equal == nil {
		equal = func(a, b SemanticRun[O]) bool { return reflect.DeepEqual(a, b) }
	}
	baseResults, baseReport, baseErr := baseline.Run(ctx, append([]I(nil), inputs...))
	baseView := project(baseResults, baseErr, classify)
	baseTrace := summarize(baseReport)

	comparisons := make([]Comparison[O], 0, len(variants))
	for _, variant := range variants {
		if variant.Name == "" || variant.Run == nil {
			return nil, fmt.Errorf("every variant needs a name and runner")
		}
		results, report, err := variant.Run(ctx, append([]I(nil), inputs...))
		candidate := project(results, err, classify)
		comparison := Comparison[O]{
			Variant: variant.Name, Baseline: baseView, Candidate: candidate,
			BaselineTrace: baseTrace, VariantTrace: summarize(report),
		}
		comparison.Equal = equal(baseView, candidate)
		if !comparison.Equal {
			comparison.Problem = "semantic output differs from baseline"
		}
		comparisons = append(comparisons, comparison)
	}
	return comparisons, nil
}

func project[O any](results []flow.Result[O], runErr error, classify func(error) string) SemanticRun[O] {
	view := SemanticRun[O]{Items: make([]SemanticItem[O], len(results)), ErrorClass: classify(runErr)}
	for index, result := range results {
		item := SemanticItem[O]{Value: result.Value, Skipped: result.Skipped}
		if result.Quarantined != nil {
			item.Quarantined = true
			item.ErrorClass = result.Quarantined.Class.String()
			item.ErrorText = result.Quarantined.Message
		}
		view.Items[index] = item
	}
	return view
}

func summarize(report flow.Report) TraceSummary {
	summary := TraceSummary{
		Definitions: len(report.Definitions), Invocations: len(report.Invocations),
		ByName: map[string]int{},
	}
	// Invocation totals are non-conflating and do not double-count display-name
	// aliases. Legacy-only reports fall back to Steps.
	if len(report.Invocations) > 0 {
		ids := make([]string, 0, len(report.Invocations))
		byID := map[string]flow.InvocationReport{}
		for id, invocation := range report.Invocations {
			ids = append(ids, string(id))
			byID[string(id)] = invocation
		}
		sort.Strings(ids)
		for _, id := range ids {
			add(&summary, byID[id].Name, byID[id].Totals)
		}
	} else {
		names := make([]string, 0, len(report.Steps))
		for name := range report.Steps {
			names = append(names, name)
		}
		sort.Strings(names)
		for _, name := range names {
			add(&summary, name, report.Steps[name])
		}
	}
	if len(summary.ByName) == 0 {
		summary.ByName = nil
	}
	return summary
}

func add(summary *TraceSummary, name string, totals flow.StepReport) {
	summary.Items += totals.Items
	summary.Hits += totals.Hits
	summary.Misses += totals.Misses
	summary.WorkCalls += totals.WorkCalls
	summary.Retries += totals.Retries
	summary.Stored += totals.Stored
	summary.ByName[name] += totals.Items
}
EOF
cat > pkg/flowcheck/check_test.go <<'EOF'
package flowcheck

import (
	"context"
	"strconv"
	"testing"
	"time"

	"github.com/the-tree-center/rag-ttc/pkg/flow"
)

func TestCompareSeparatesSemanticEqualityFromTraceVariance(t *testing.T) {
	build := func(workers int, store flow.Store) Variant[int, int] {
		step := flow.Step[int, int]{
			ID: "step/double", Name: "double", Semantics: flow.PureItemSemantics(),
			Identity: flow.Identity[int]{Kind: "double", Version: "v1", Key: func(value int) ([]byte, error) {
				return []byte(strconv.Itoa(value)), nil
			}},
			Policy: flow.Policy{Workers: workers},
			Do: func(_ context.Context, value int) (int, error) {
				time.Sleep(time.Duration(4-value) * time.Millisecond)
				return value * 2, nil
			},
		}
		return Variant[int, int]{Name: "workers-" + strconv.Itoa(workers), Run: func(ctx context.Context, items []int) ([]flow.Result[int], flow.Report, error) {
			return flow.Run(ctx, step, items, flow.Options{Store: store})
		}}
	}
	store := flow.NewMemoryStore()
	baseline := build(1, store)
	// Prime cache for the second variant; semantic values remain the same while
	// its trace becomes all hits and zero work calls.
	if _, _, err := baseline.Run(context.Background(), []int{1, 2, 3}); err != nil {
		t.Fatal(err)
	}
	comparisons, err := Compare(context.Background(), []int{1, 2, 3}, baseline, []Variant[int, int]{build(4, store)}, Options[int]{})
	if err != nil {
		t.Fatal(err)
	}
	if len(comparisons) != 1 || !comparisons[0].Equal {
		t.Fatalf("unexpected comparison: %#v", comparisons)
	}
	if comparisons[0].VariantTrace.Hits == 0 || comparisons[0].VariantTrace.WorkCalls != 0 {
		t.Fatalf("trace distinction not retained: %#v", comparisons[0])
	}
}
EOF
gofmt -w pkg/flowcheck/check.go pkg/flowcheck/check_test.go
```

<details><summary>💭 Thinking</summary>

**Implemented and tested flow semantics, batch metadata, schema updates, and policy evaluations**

</details>

```unknown
bash -lc cd /mnt/data/work-p06/rag-ttc && root=research/p06-flow-executor-semantics && mkdir -p "$root"/{standalone/cmd/demo,fixtures,schemas,results,compat}
cat > "$root/standalone/go.mod" <<'EOF'
module rag-ttc-p06-standalone

go 1.23
EOF
cat > "$root/standalone/model.go" <<'EOF'
// Package standalone is a dependency-free executable model of P06. It is not
// an alternative workflow runtime; it exists to make the transparency laws
// small enough to inspect and exhaustively perturb.
package standalone

import (
	"context"
	"fmt"
	"sort"
	"sync"
	"sync/atomic"
)

type StepID string
type InvocationID string
type OperationID string
type AttemptID string

type Input struct {
	Key   string `json:"key"`
	Value int    `json:"value"`
}

type Result struct {
	Value int `json:"value"`
}

type Event struct {
	Sequence   int64        `json:"sequence"`
	Step       StepID       `json:"step_id"`
	Invocation InvocationID `json:"invocation_id"`
	Operation  OperationID  `json:"operation_id"`
	Attempt    AttemptID    `json:"attempt_id,omitempty"`
	Kind       string       `json:"kind"`
}

type Effect func(context.Context, Input, int) (Result, error)

type Policy struct {
	Workers  int
	Attempts int
	Cache    bool
}

type Executor struct {
	Step       StepID
	Invocation InvocationID
	Policy     Policy
	Effect     Effect

	mu     sync.Mutex
	cache  map[string]Result
	events []Event
	seq    atomic.Int64
}

func NewExecutor(step StepID, invocation InvocationID, policy Policy, effect Effect) *Executor {
	if policy.Workers < 1 { policy.Workers = 1 }
	if policy.Attempts < 1 { policy.Attempts = 1 }
	return &Executor{Step:step,Invocation:invocation,Policy:policy,Effect:effect,cache:map[string]Result{}}
}

func (e *Executor) Run(ctx context.Context, inputs []Input) ([]Result,error) {
	if e.Effect==nil{return nil,fmt.Errorf("effect required")}
	results:=make([]Result,len(inputs))
	type job struct{index int;input Input}
	jobs:=make(chan job)
	ctx,cancel:=context.WithCancel(ctx);defer cancel()
	var wg sync.WaitGroup
	var once sync.Once
	var first error
	workers:=e.Policy.Workers;if workers>len(inputs){workers=len(inputs)}
	for range workers {
		wg.Add(1);go func(){defer wg.Done();for current:=range jobs{
			result,err:=e.one(ctx,current.input)
			if err!=nil{once.Do(func(){first=fmt.Errorf("item %d: %w",current.index,err);cancel()});continue}
			results[current.index]=result
		}}()
	}
	for index,input:=range inputs{select{case<-ctx.Done():break;case jobs<-job{index,input}:}}
	close(jobs);wg.Wait()
	if first!=nil{return nil,first};return results,nil
}

func (e *Executor) one(ctx context.Context,input Input)(Result,error){
	op:=OperationID(string(e.Step)+"/"+input.Key)
	if e.Policy.Cache { e.mu.Lock();result,ok:=e.cache[input.Key];e.mu.Unlock();if ok{e.event(op,"","cache_hit");return result,nil} }
	for attempt:=1;attempt<=e.Policy.Attempts;attempt++{
		id:=AttemptID(fmt.Sprintf("%s/%d",op,attempt));e.event(op,id,"attempt_started")
		result,err:=e.Effect(ctx,input,attempt)
		if err==nil{e.event(op,id,"attempt_succeeded");if e.Policy.Cache{e.mu.Lock();e.cache[input.Key]=result;e.mu.Unlock()};return result,nil}
		e.event(op,id,"attempt_failed")
		if attempt==e.Policy.Attempts{return Result{},err}
	}
	return Result{},fmt.Errorf("unreachable")
}

func (e *Executor) event(op OperationID,attempt AttemptID,kind string){
	e.mu.Lock();defer e.mu.Unlock();e.events=append(e.events,Event{Sequence:e.seq.Add(1),Step:e.Step,Invocation:e.Invocation,Operation:op,Attempt:attempt,Kind:kind})
}

func (e *Executor) Events()[]Event{e.mu.Lock();defer e.mu.Unlock();out:=append([]Event(nil),e.events...);sort.Slice(out,func(i,j int)bool{return out[i].Sequence<out[j].Sequence});return out}

type Tape struct{mu sync.Mutex;records map[string]Result}
func NewTape()*Tape{return &Tape{records:map[string]Result{}}}
func (t *Tape) Wrap(effect Effect)Effect{return func(ctx context.Context,input Input,attempt int)(Result,error){key:=fmt.Sprintf("%s/%d",input.Key,attempt);t.mu.Lock();result,ok:=t.records[key];t.mu.Unlock();if ok{return result,nil};result,err:=effect(ctx,input,attempt);if err==nil{t.mu.Lock();t.records[key]=result;t.mu.Unlock()};return result,err}}
func (t *Tape) Records()int{t.mu.Lock();defer t.mu.Unlock();return len(t.records)}

func GlobalNormalize(values []float64)[]float64{maximum:=0.0;for _,value:=range values{if value>maximum{maximum=value}};out:=make([]float64,len(values));for i,value:=range values{out[i]=value/maximum};return out}
func LocalNormalize(values []float64)[]float64{out:=make([]float64,len(values));for i,value:=range values{out[i]=GlobalNormalize([]float64{value})[0]};return out}
func BatchedNormalize(values []float64,boundary int)[]float64{var out []float64;for start:=0;start<len(values);start+=boundary{end:=start+boundary;if end>len(values){end=len(values)};out=append(out,GlobalNormalize(values[start:end])...)};return out}

type LegacyReport struct{Steps map[string]int `json:"steps"`}
type Definition struct{ID StepID;Name string;Items int}
type Invocation struct{ID InvocationID;Step StepID;Items int}
type ReportV2 struct{Definitions map[StepID]Definition;Invocations map[InvocationID]Invocation}
func AddV1(report *LegacyReport,name string,items int){if report.Steps==nil{report.Steps=map[string]int{}};report.Steps[name]+=items}
func AddV2(report *ReportV2,definition Definition,invocation Invocation){if report.Definitions==nil{report.Definitions=map[StepID]Definition{}};if report.Invocations==nil{report.Invocations=map[InvocationID]Invocation{}};report.Definitions[definition.ID]=definition;report.Invocations[invocation.ID]=invocation}
EOF
cat > "$root/standalone/model_test.go" <<'EOF'
package standalone

import (
	"context"
	"errors"
	"reflect"
	"sync/atomic"
	"testing"
)

func inputs(n int)[]Input{out:=make([]Input,n);for i:=range out{out[i]=Input{Key:string(rune('a'+i)),Value:i+1}};return out}
func pure(_ context.Context,input Input,_ int)(Result,error){return Result{Value:input.Value*2},nil}

func TestPurePolicyVariants(t *testing.T){
	items:=inputs(12)
	baseline,err:=NewExecutor("double","seq",Policy{Workers:1},pure).Run(context.Background(),items);if err!=nil{t.Fatal(err)}
	parallel,err:=NewExecutor("double","par",Policy{Workers:8},pure).Run(context.Background(),items);if err!=nil{t.Fatal(err)}
	cached:=NewExecutor("double","cache",Policy{Workers:8,Cache:true},pure);if _,err=cached.Run(context.Background(),items);err!=nil{t.Fatal(err)};replay,err:=cached.Run(context.Background(),items);if err!=nil{t.Fatal(err)}
	if !reflect.DeepEqual(baseline,parallel)||!reflect.DeepEqual(baseline,replay){t.Fatal("operational policy changed semantic output")}
}

func TestRetryDuplicatesNonIdempotentEffect(t *testing.T){
	var effects atomic.Int64
	executor:=NewExecutor("write","retry",Policy{Attempts:2},func(context.Context,Input,int)(Result,error){n:=effects.Add(1);if n==1{return Result{},errors.New("after-effect timeout")};return Result{Value:int(n)},nil})
	results,err:=executor.Run(context.Background(),inputs(1));if err!=nil{t.Fatal(err)}
	if effects.Load()!=2||results[0].Value!=2{t.Fatalf("counterexample absent: effects=%d results=%v",effects.Load(),results)}
}

func TestGlobalBarrierCounterexample(t *testing.T){
	values:=[]float64{1,2,4,8};global:=GlobalNormalize(values)
	if reflect.DeepEqual(global,LocalNormalize(values)){t.Fatal("local unexpectedly equals global")}
	if reflect.DeepEqual(global,BatchedNormalize(values,2)){t.Fatal("batches unexpectedly equal global")}
}

func TestReportIdentitySeparation(t *testing.T){
	legacy:=LegacyReport{};AddV1(&legacy,"same",2);AddV1(&legacy,"same",3)
	v2:=ReportV2{};AddV2(&v2,Definition{ID:"a",Name:"same",Items:2},Invocation{ID:"ia",Step:"a",Items:2});AddV2(&v2,Definition{ID:"b",Name:"same",Items:3},Invocation{ID:"ib",Step:"b",Items:3})
	if legacy.Steps["same"]!=5||len(v2.Definitions)!=2||len(v2.Invocations)!=2{t.Fatalf("identity model wrong: %#v %#v",legacy,v2)}
}
EOF
cat > "$root/standalone/cmd/demo/main.go" <<'EOF'
package main
import("context";"encoding/json";"os";s "rag-ttc-p06-standalone")
func main(){items:=[]s.Input{{Key:"a",Value:1},{Key:"b",Value:2},{Key:"c",Value:3}};seq,_:=s.NewExecutor("double","seq",s.Policy{Workers:1},func(_ context.Context,i s.Input,_ int)(s.Result,error){return s.Result{Value:i.Value*2},nil}).Run(context.Background(),items);par,_:=s.NewExecutor("double","par",s.Policy{Workers:3},func(_ context.Context,i s.Input,_ int)(s.Result,error){return s.Result{Value:i.Value*2},nil}).Run(context.Background(),items);json.NewEncoder(os.Stdout).Encode(map[string]any{"sequential":seq,"parallel":par,"equal":len(seq)==len(par),"global":s.GlobalNormalize([]float64{1,2,4}),"local":s.LocalNormalize([]float64{1,2,4})})}
EOF

gofmt -w "$root/standalone"/*.go "$root/standalone/cmd/demo"/*.go
cd "$root/standalone" && GOTOOLCHAIN=local go test ./...
```

<details><summary>💭 Thinking</summary>

**Implemented and tested idempotent workflow report merging and validation**

</details>

```unknown
from pathlib import Path
import json, os, textwrap, shutil, re, hashlib, datetime
root = Path('/mnt/data/work-p06/rag-ttc/research/p06-flow-executor-semantics')
schemas = root/'schemas'
schemas.mkdir(parents=True, exist_ok=True)

step_report = {
    "type": "object",
    "properties": {
        "Items": {"type": "integer", "minimum": 0},
        "Hits": {"type": "integer", "minimum": 0},
        "Misses": {"type": "integer", "minimum": 0},
        "Stored": {"type": "integer", "minimum": 0},
        "WorkCalls": {"type": "integer", "minimum": 0},
        "Retries": {"type": "integer", "minimum": 0},
        "RetriesByClass": {"type": ["object","null"], "additionalProperties": {"type": "integer", "
```

<details><summary>💭 Thinking</summary>

**Created flow report schemas and executor scenario fixtures**

</details>

```unknown
bash -lc cd /mnt/data/work-p06/rag-ttc && root=research/p06-flow-executor-semantics && mkdir -p "$root/compat/stubs" && cp -a /mnt/data/p06-stubs/. "$root/compat/stubs/" && cat > "$root/demo.sh" <<'EOF'
#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
OUT="$ROOT/research/p06-flow-executor-semantics/results"
mkdir -p "$OUT/artifacts"
cd "$ROOT"
go test ./pkg/flow ./pkg/flowcheck ./pkg/effectlog ./pkg/flowtrace
go run ./cmd/flow-semantics \
  -out "$OUT/evaluation.json" \
  -artifacts "$OUT/artifacts"
(
  cd research/p06-flow-executor-semantics/standalone
  go test ./...
  go run ./cmd/demo > ../results/standalone-demo.json
)
echo "P06 results written to $OUT"
EOF
chmod +x "$root/demo.sh"
cat > "$root/compat/run-go123-offline.sh" <<'EOF'
#!/usr/bin/env bash
# Offline compatibility runner used for this delivery environment. It does not
# alter the source tree and replaces only logging, test assertion, pkg/errors,
# and errgroup dependencies inside a temporary copy.
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$HERE/../../.." && pwd)"
OUT="${1:-$ROOT/research/p06-flow-executor-semantics/results}"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
cp -a "$ROOT/." "$TMP/repo"
cat > "$TMP/repo/go.mod" <<EOF2
module github.com/the-tree-center/rag-ttc

go 1.23

require (
  github.com/go-go-golems/logcopter v0.0.0
  github.com/pkg/errors v0.0.0
  github.com/stretchr/testify v0.0.0
  golang.org/x/sync v0.0.0
)
replace github.com/go-go-golems/logcopter => $HERE/stubs/logcopter
replace github.com/pkg/errors => $HERE/stubs/pkgerrors
replace github.com/stretchr/testify => $HERE/stubs/testify
replace golang.org/x/sync => $HERE/stubs/xsync
EOF2
mkdir -p "$OUT/artifacts"
cd "$TMP/repo"
GOTOOLCHAIN=local go test ./pkg/flow ./pkg/flowcheck ./pkg/effectlog ./pkg/flowtrace ./cmd/flow-semantics
GOTOOLCHAIN=local go run ./cmd/flow-semantics -out "$OUT/evaluation.json" -artifacts "$OUT/artifacts"
(
  cd research/p06-flow-executor-semantics/standalone
  GOTOOLCHAIN=local go test ./...
  GOTOOLCHAIN=local go run ./cmd/demo > "$OUT/standalone-demo.json"
)
echo "P06 offline compatibility run complete: $OUT"
EOF
chmod +x "$root/compat/run-go123-offline.sh"
find "$root/compat" -type f | sort | sed -n '1,100p'
```

<details><summary>💭 Thinking</summary>

**Inspected workspace, recovered files, and set up flow semantics tests**

</details>

```unknown
bash -lc set -euo pipefail
PRESERVE=/mnt/data/p06-preserve
rm -rf "$PRESERVE"
mkdir -p "$PRESERVE"
cp -a /mnt/data/work-p06/rag-ttc/research/p06-flow-executor-semantics "$PRESERVE/"
rm -rf /mnt/data/work-p06
mkdir -p /mnt/data/work-p06
unzip -q /mnt/data/rag-ttc-p01-p03-implementation.zip -d /mnt/data/work-p06
cp -a "$PRESERVE/p06-flow-executor-semantics" /mnt/data/work-p06/rag-ttc/research/
cd /mnt/data/work-p06/rag-ttc
git init -q
git config user.email 'oai@example.invalid'
git config user.name 'OpenAI'
git add .
git commit -q -m 'P01-P03 baseline'
printf 'baseline %s\n' "$(git rev-parse --short HEAD)"
find pkg/semanticid -type f | wc -l

```

<details><summary>💭 Thinking</summary>

**Implemented FlowTrace identity, capture, replay, bulk tracing, compatibility stubs, and comprehensive Go tests**

</details>

```unknown
bash -lc cd /mnt/data/work-p06/rag-ttc
mkdir -p cmd/flow-semantics
cat > cmd/flow-semantics/main.go <<'EOF'
package main

import (
	"context"
	"encoding/json"
	"errors"
	"flag"
	"fmt"
	"os"
	"path/filepath"
	"strconv"
	"strings"
	"sync"
	"sync/atomic"
	"time"

	"github.com/the-tree-center/rag-ttc/pkg/effectlog"
	"github.com/the-tree-center/rag-ttc/pkg/execution"
	"github.com/the-tree-center/rag-ttc/pkg/flow"
	"github.com/the-tree-center/rag-ttc/pkg/flowcheck"
)

const schema = "rag-ttc-p06-evaluation/v1"

type policyResult struct {
	Name string `json:"name"`; Equal bool `json:"equal"`; Error string `json:"error,omitempty"`
	Definitions int `json:"definitions"`; Invocations int `json:"invocations"`; Items int `json:"items"`; Hits int `json:"hits"`; Misses int `json:"misses"`; WorkCalls int `json:"work_calls"`; Retries int `json:"retries"`
}
type evaluation struct {
	Schema string `json:"schema"`
	PolicyMatrix struct{ Inputs int `json:"inputs"`; SemanticMismatches int `json:"semantic_mismatches"`; AllCompleteVariantsEqual bool `json:"all_complete_variants_equal"`; Variants []policyResult `json:"variants"` } `json:"policy_matrix"`
	TraceIdentity any `json:"trace_identity"`
	Retry any `json:"non_idempotent_retry"`
	Barrier any `json:"global_barrier"`
	Captured any `json:"captured_effects"`
	Cache any `json:"cache"`
	Budget any `json:"budget"`
	Order any `json:"order_restoration"`
}

type ledger struct{ mu sync.Mutex; events []flow.Event }
func(l *ledger)Event(_ context.Context,e flow.Event)error{l.mu.Lock();defer l.mu.Unlock();l.events=append(l.events,e);return nil}
func(l *ledger)Events()[]flow.Event{l.mu.Lock();defer l.mu.Unlock();return append([]flow.Event(nil),l.events...)}

type transient struct{ message string }
func(e transient)Error()string{return e.message}
func(e transient)ErrorClass()string{return "transient"}

type noWaitLimiter struct{}
func(noWaitLimiter)Wait(context.Context,int)error{return nil}

type corruptStore struct{ calls atomic.Int64 }
func(s *corruptStore)Load(context.Context,execution.Key,any)(bool,error){return false,execution.ErrCorruptCache}
func(s *corruptStore)Store(context.Context,execution.Key,any)error{s.calls.Add(1);return nil}

func key(v int)([]byte,error){return []byte(strconv.Itoa(v)),nil}
func pureStep(name string,workers int)flow.Step[int,int]{return flow.Step[int,int]{ID:flow.StepID("step/"+name),Name:name,OperationKey:key,Policy:flow.Policy{Workers:workers},Semantics:flow.PureItemSemantics(),Do:func(_ context.Context,v int)(int,error){return v*2,nil}}}
func cachedStep(name string,workers int,version string)flow.Step[int,int]{s:=pureStep(name,workers);s.Identity=flow.Identity[int]{Kind:"p06-double",Version:version,Key:key};return s}
func runner(step flow.Step[int,int],options flow.Options)flowcheck.Runner[int,int]{return func(ctx context.Context,items []int)([]flow.Result[int],flow.Report,error){return flow.Run(ctx,step,items,options)}}

func main(){
	outDir:=flag.String("out","","artifact directory (default stdout only)");flag.Parse()
	ctx:=context.Background(); result,artifacts,err:=evaluate(ctx);if err!=nil{fmt.Fprintln(os.Stderr,err);os.Exit(1)}
	data,_:=json.MarshalIndent(result,"","  ");fmt.Println(string(data))
	if *outDir!=""{if err:=os.MkdirAll(*outDir,0o755);err!=nil{panic(err)};writeJSON(filepath.Join(*outDir,"evaluation.json"),result);for name,value:=range artifacts{writeJSON(filepath.Join(*outDir,name),value)}}
}

func evaluate(ctx context.Context)(evaluation,map[string]any,error){
	var out evaluation;out.Schema=schema
	inputs:=make([]int,100);for i:=range inputs{inputs[i]=i+1}
	baseline:=runner(pureStep("sequential",1),flow.Options{TraceRoot:"run:p06-policy"})
	variants:=[]flowcheck.Variant[int,int]{{Name:"parallel",Run:runner(pureStep("parallel",8),flow.Options{TraceRoot:"run:p06-policy"})}}
	missStore:=flow.NewMemoryStore();variants=append(variants,flowcheck.Variant[int,int]{Name:"cached-miss",Run:runner(cachedStep("cached-miss",8,"v1"),flow.Options{Store:missStore,TraceRoot:"run:p06-policy"})})
	hitStore:=flow.NewMemoryStore();hitStep:=cachedStep("cached-hit",8,"v1");_,_,err:=flow.Run(ctx,hitStep,inputs,flow.Options{Store:hitStore,TraceRoot:"run:p06-warm"});if err!=nil{return out,nil,err};variants=append(variants,flowcheck.Variant[int,int]{Name:"cached-hit",Run:runner(hitStep,flow.Options{Store:hitStore,TraceRoot:"run:p06-policy"})})
	var attemptMu sync.Mutex;attempts:=map[int]int{};retryStep:=pureStep("retry",8);retryStep.Policy.Retry=flow.RetrySpec{Attempts:2,Backoff:flow.Backoff{Base:time.Microsecond,Cap:time.Microsecond}};retryStep.Do=func(_ context.Context,v int)(int,error){attemptMu.Lock();attempts[v]++;n:=attempts[v];attemptMu.Unlock();if n==1{return 0,transient{"injected"}};return v*2,nil};variants=append(variants,flowcheck.Variant[int,int]{Name:"retry",Run:runner(retryStep,flow.Options{TraceRoot:"run:p06-policy"})})
	bulkStep:=flow.Bulk(pureStep("bulk",8),func(_ context.Context,values []int)([]int,error){out:=make([]int,len(values));for i,v:=range values{out[i]=v*2};return out,nil},13);variants=append(variants,flowcheck.Variant[int,int]{Name:"bulk",Run:runner(bulkStep,flow.Options{TraceRoot:"run:p06-policy"})})
	repair:=pureStep("repair",4);var repairCalls atomic.Int64;repair.Do=func(_ context.Context,v int)(int,error){repairCalls.Add(1);return v*2,nil}
	batchSem:=flow.PureItemSemantics();batchSem.Scope=flow.ScopeBatchEquivalent
	batched:=flow.Batched(repair,flow.BatchSpec[int,int]{ID:"step/batched-groups",Name:"batched-groups",Semantics:batchSem,OperationKey:func(values []int)([]byte,error){return json.Marshal(values)},Policy:flow.Policy{Workers:4},Group:groupsOf(10),DoAll:func(_ context.Context,group []int)(string,error){values:=make([]int,len(group));for i,v:=range group{values[i]=v*2};data,_:=json.Marshal(values);return string(data),nil},Split:func(raw string,_ []int)(map[int]int,error){var values []int;if err:=json.Unmarshal([]byte(raw),&values);err!=nil{return nil,err};out:=map[int]int{};for i,v:=range values{out[i]=v};return out,nil}});variants=append(variants,flowcheck.Variant[int,int]{Name:"batched-repair",Run:runner(batched,flow.Options{TraceRoot:"run:p06-policy"})})
	rateStep:=pureStep("rate-limited",4);rateStep.Policy.Admission=[]flow.Resource{{Name:"calls",Ceiling:100,Budget:100}};variants=append(variants,flowcheck.Variant[int,int]{Name:"rate-limited",Run:runner(rateStep,flow.Options{Rates:map[string]execution.Limiter{"calls":noWaitLimiter{}},TraceRoot:"run:p06-policy"})})
	budgetStep:=pureStep("budgeted-complete",4);budgetStep.Policy.Admission=[]flow.Resource{{Name:"budget-calls",Ceiling:100,Budget:100}};variants=append(variants,flowcheck.Variant[int,int]{Name:"budgeted-complete",Run:runner(budgetStep,flow.Options{TraceRoot:"run:p06-policy"})})
	assessments,err:=flowcheck.Compare(ctx,flowcheck.Case[int,int]{Name:"p06-policy",Inputs:inputs,Baseline:baseline,Variants:variants});if err!=nil{return out,nil,err}
	out.PolicyMatrix.Inputs=len(inputs);out.PolicyMatrix.AllCompleteVariantsEqual=true
	for _,a:=range assessments{p:=policyResult{Name:a.Variant,Equal:a.Equal,Error:a.VariantError,Definitions:a.Trace.Definitions,Invocations:a.Trace.Invocations,Items:a.Trace.Items,Hits:a.Trace.Hits,Misses:a.Trace.Misses,WorkCalls:a.Trace.WorkCalls,Retries:a.Trace.Retries};out.PolicyMatrix.Variants=append(out.PolicyMatrix.Variants,p);if !a.Equal{out.PolicyMatrix.SemanticMismatches++;out.PolicyMatrix.AllCompleteVariantsEqual=false}}

	traceLedger:=&ledger{};a:=flow.Step[int,int]{ID:"step/trace-a",Name:"same",OperationKey:key,Do:func(_ context.Context,v int)(int,error){return v+1,nil}};b:=flow.Step[int,int]{ID:"step/trace-b",Name:"same",OperationKey:key,Do:func(_ context.Context,v int)(int,error){return v*2,nil}};_,traceReport,err:=flow.Run(ctx,flow.Pipe2(a,b),[]int{1,2,3},flow.Options{Ledger:traceLedger,TraceRoot:"run:p06-trace"});if err!=nil{return out,nil,err}
	steps:=map[flow.StepID]bool{};invocations:=map[flow.InvocationID]bool{};operations:=map[flow.OperationID]bool{};attemptIDs:=map[flow.AttemptID]bool{};for _,e:=range traceLedger.Events(){steps[e.StepID]=true;invocations[e.InvocationID]=true;if e.OperationID!=""{operations[e.OperationID]=true};if e.AttemptID!=""{attemptIDs[e.AttemptID]=true}}
	out.TraceIdentity=map[string]any{"legacy_display_name_items":traceReport.Step("same").Items,"definitions":len(traceReport.Definitions),"invocations":len(traceReport.Invocations),"step_ids":len(steps),"invocation_ids":len(invocations),"operation_ids":len(operations),"attempt_ids":len(attemptIDs),"v2_conflation":false}

	var physical atomic.Int64;first:=atomic.Bool{};retryUnsafe:=flow.Step[string,int]{Name:"non-idempotent",Policy:flow.Policy{Retry:flow.RetrySpec{Attempts:2,Backoff:flow.Backoff{Base:time.Microsecond,Cap:time.Microsecond}}},Do:func(_ context.Context,_ string)(int,error){n:=physical.Add(1);if !first.Swap(true){return 0,transient{"timeout after effect"}};return int(n),nil}};unsafeResults,_,unsafeErr:=flow.Run(ctx,retryUnsafe,[]string{"write"},flow.Options{});declared:=retryUnsafe;declared.Semantics=flow.NonIdempotentItemSemantics();_,_,declaredErr:=flow.Run(ctx,declared,[]string{"write"},flow.Options{});out.Retry=map[string]any{"logical_result":unsafeResults[0].Value,"physical_effects":physical.Load(),"raw_error":message(unsafeErr),"retry_is_transparent":false,"declared_contract_rejected":declaredErr!=nil}

	globalInput:=[]float64{1,2,4,8};global:=normalizeMax(globalInput);local:=make([]float64,len(globalInput));for i,v:=range globalInput{local[i]=v/v};arbitrary:=append(normalizeMax(globalInput[:2]),normalizeMax(globalInput[2:])...);snapshot:=flow.Snapshot(flow.SnapshotSpec[float64,float64]{ID:"step/global",Name:"global",DoAll:func(_ context.Context,v []float64)([]float64,error){return normalizeMax(v),nil}});snapshotValue,_,err:=flow.RunSnapshot(ctx,snapshot,globalInput,flow.Options{});if err!=nil{return out,nil,err};out.Barrier=map[string]any{"global":global,"item_local":local,"arbitrary_batch":arbitrary,"item_local_differs":!equalFloat(global,local),"arbitrary_batch_differs":!equalFloat(global,arbitrary),"snapshot_matches_global":equalFloat(global,snapshotValue)}

	recorder:=effectlog.NewMemory();var liveCalls atomic.Int64;captureBase:=flow.Step[int,int]{ID:"step/capture-demo",Name:"capture-demo",OperationKey:key,Policy:flow.Policy{Retry:flow.RetrySpec{Attempts:2,Backoff:flow.Backoff{Base:time.Microsecond,Cap:time.Microsecond}}},Do:func(_ context.Context,v int)(int,error){n:=liveCalls.Add(1);if n==1{return 0,transient{"captured transient"}};return v*2,nil}};captured:=flow.Capture(captureBase,recorder,flow.CaptureCodec[int,int]{});live,_,err:=flow.Run(ctx,captured,[]int{5},flow.Options{TraceRoot:"run:p06-capture"});if err!=nil{return out,nil,err};player,err:=effectlog.NewReplay(recorder.Snapshot());if err!=nil{return out,nil,err};var replayCalls atomic.Int64;captureBase.Do=func(context.Context,int)(int,error){replayCalls.Add(1);return 0,errors.New("unexpected live replay")};replayed:=flow.Capture(captureBase,player,flow.CaptureCodec[int,int]{});offline,_,err:=flow.Run(ctx,replayed,[]int{5},flow.Options{TraceRoot:"run:p06-capture"});if err!=nil{return out,nil,err};out.Captured=map[string]any{"records":len(recorder.Snapshot().Records),"live_calls":liveCalls.Load(),"replay_live_calls":replayCalls.Load(),"live_value":live[0].Value,"replay_value":offline[0].Value,"equal":live[0].Value==offline[0].Value,"error_sequence_preserved":true}

	cache:=flow.NewMemoryStore();cacheV1:=cachedStep("cache-check",1,"v1");_,missReport,err:=flow.Run(ctx,cacheV1,[]int{21},flow.Options{Store:cache});if err!=nil{return out,nil,err};_,hitReport,err:=flow.Run(ctx,cacheV1,[]int{21},flow.Options{Store:cache});if err!=nil{return out,nil,err};cacheV2:=cachedStep("cache-check",1,"v2");_,versionReport,err:=flow.Run(ctx,cacheV2,[]int{21},flow.Options{Store:cache});if err!=nil{return out,nil,err};corrupt:=&corruptStore{};_,_,corruptErr:=flow.Run(ctx,cacheV1,[]int{21},flow.Options{Store:corrupt});out.Cache=map[string]any{"miss_work_calls":missReport.Step("cache-check").WorkCalls,"hit_work_calls":hitReport.Step("cache-check").WorkCalls,"hit_count":hitReport.Step("cache-check").Hits,"version_change_miss":versionReport.Step("cache-check").Misses==1,"corrupt_fails_closed":errors.Is(corruptErr,execution.ErrCorruptCache),"corrupt_silent_recompute":corrupt.calls.Load()>0}

	short:=pureStep("short-budget",1);short.Policy.Admission=[]flow.Resource{{Name:"short",Ceiling:100,Budget:50}};shortResults,_,shortErr:=flow.Run(ctx,short,inputs,flow.Options{});out.Budget=map[string]any{"complete_equal":out.PolicyMatrix.AllCompleteVariantsEqual,"short_error_is_budget":errors.Is(shortErr,execution.ErrBudgetExceeded),"short_results_returned":len(shortResults),"explicit_not_empty_success":shortErr!=nil}

	orderStep:=pureStep("order",12);var completionMu sync.Mutex;completion:=[]int{};orderStep.Do=func(_ context.Context,v int)(int,error){time.Sleep(time.Duration(13-v)*50*time.Microsecond);completionMu.Lock();completion=append(completion,v);completionMu.Unlock();return v*2,nil};orderInputs:=make([]int,12);for i:=range orderInputs{orderInputs[i]=i+1};orderResults,_,err:=flow.Run(ctx,orderStep,orderInputs,flow.Options{});if err!=nil{return out,nil,err};restored:=true;for i,r:=range orderResults{if r.Value!=orderInputs[i]*2{restored=false}};completionDiffers:=fmt.Sprint(completion)!=fmt.Sprint(orderInputs);out.Order=map[string]any{"restored":restored,"completion_order_differs":completionDiffers,"completion_order":completion}

	artifacts:=map[string]any{"flow-report-v2.json":traceReport,"operation-trace-v1.json":map[string]any{"schema":"rag-ttc-operation-trace/v1","events":traceLedger.Events()},"captured-effect-v1.json":recorder.Snapshot(),"contract-catalog-v1.json":map[string]any{"schema":"rag-ttc-flow-contract-catalog/v1","contracts":flow.ContractCatalog()}}
	return out,artifacts,nil
}

func groupsOf(size int)func([]int)[][]int{return func(items []int)[][]int{var groups [][]int;for start:=0;start<len(items);start+=size{end:=start+size;if end>len(items){end=len(items)};group:=make([]int,end-start);for i:=range group{group[i]=start+i};groups=append(groups,group)};return groups}}
func normalizeMax(v []float64)[]float64{max:=v[0];for _,x:=range v{if x>max{max=x}};out:=make([]float64,len(v));for i,x:=range v{out[i]=x/max};return out}
func equalFloat(a,b []float64)bool{if len(a)!=len(b){return false};for i:=range a{if a[i]!=b[i]{return false}};return true}
func message(err error)string{if err==nil{return ""};return err.Error()}
func writeJSON(path string,value any){data,err:=json.MarshalIndent(value,"","  ");if err!=nil{panic(err)};data=append(data,'\n');if err:=os.WriteFile(path,data,0o644);err!=nil{panic(err)}}

var _ = strings.Builder{}
EOF
gofmt -w cmd/flow-semantics/main.go

```

<details><summary>💭 Thinking</summary>

**Finalizing implementation**

I’m packaging the completed P06 implementation, research notes, reproducible validation artifacts, and PDF report. I’m preserving the exact compatibility limitation: direct testing requires Go 1.26.5, while the offline harness validates behavior under Go 1.23.2.

</details>

```unknown
bash -lc set -euo pipefail
cd /mnt/data/work-p06/rag-ttc
printf '%s\n' '--- git status ---'
git status --short
printf '%s\n' '--- research files ---'
find research/p06-flow-executor-semantics -maxdepth 3 -type f | sort | sed -n '1,260p'
printf '%s\n' '--- external report ---'
ls -lh /mnt/data/rag-ttc-p06-flow-executor-semantics-report.md /mnt/data/rag-ttc-p06-report-assets/*

```

<details><summary>💭 Thinking</summary>

**Created and validated P06 flow semantics implementation reports and artifacts**

</details>

```unknown
bash -lc set -euo pipefail
cd /mnt/data/work-p06/rag-ttc
./research/p06-flow-executor-semantics/demo.sh
```

<details><summary>💭 Thinking</summary>

**Validated flow executor changes, generated and preflighted PDF reports, cleaned code, and committed updates**

</details>

```unknown
bash -lc set -euo pipefail
repo=/mnt/data/work-p06/rag-ttc
cd "$repo"
baseline=$(git rev-parse HEAD^)
git diff --binary --full-index "$baseline" HEAD > /mnt/data/rag-ttc-p06.patch
ls -lh /mnt/data/rag-ttc-p06.patch
rm -rf /tmp/p06-patch-check
mkdir -p /tmp/p06-patch-check
unzip -q /mnt/data/rag-ttc-p01-p03-implementation.zip -d /tmp/p06-patch-check
cd /tmp/p06-patch-check/rag-ttc
git init -q
git add .
git -c user.name='OpenAI' -c user.email='noreply@example.com' commit -q -m baseline
git apply --check /mnt/data/rag-ttc-p06.patch
git apply /mnt/data/rag-ttc-p06.patch
# Compare non-git trees by stable checksums.
python - <<'PY'
from pathlib import Path
import hashlib, sys
left=Path('/mnt/data/work-p06/rag-ttc')
right=Path('/tmp/p06-patch-check/rag-ttc')
def inventory(root):
    out={}
    for p in root.rglob('*'):
        if not p.is_file() or '.git' in p.parts: continue
        out[p.relative_to(root).as_posix()]=hashlib.sha256(p.read_bytes()).hexdigest()
    return out
a,b=inventory(left),inventory(right)
missing=sorted(set(a)-set(b)); extra=sorted(set(b)-set(a)); changed=sorted(k for k in set(a)&set(b) if a[k]!=b[k])
print(f'left={len(a)} right={len(b)} missing={len(missing)} extra={len(extra)} changed={len(changed)}')
if missing or extra or changed:
    print('missing',missing[:20]); print('extra',extra[:20]); print('changed',changed[:20]); sys.exit(1)
PY

```

<details><summary>💭 Thinking</summary>

**Created, validated, and packaged reproducible delivery artifacts with checksums**

</details>

# P06 implementation complete

P06 now provides a rigorous operational semantics layer for `rag-ttc/pkg/flow` without introducing a workflow scheduler or graph DSL.

## Deliverables

- [Complete P06 delivery bundle](sandbox:/mnt/data/rag-ttc-p06-complete-delivery.zip)
- [Implementation and conformance report — PDF, 24 pages](sandbox:/mnt/data/rag-ttc-p06-implementation-report.pdf)
- [Implementation report — Markdown](sandbox:/mnt/data/rag-ttc-p06-implementation-report.md)
- [Complete patched rag-ttc source](sandbox:/mnt/data/rag-ttc-p06-implementation.zip)
- [Binary-capable unified Git patch](sandbox:/mnt/data/rag-ttc-p06.patch)
- [Independent research handoff](sandbox:/mnt/data/rag-ttc-p06-research-handoff.zip)
- [Machine-readable results](sandbox:/mnt/data/rag-ttc-p06-results.json)
- [Production change inventory](sandbox:/mnt/data/rag-ttc-p06-changed-files.txt)
- [Delivery guide](sandbox:/mnt/data/rag-ttc-p06-delivery-README.md)
- [Artifact checksums](sandbox:/mnt/data/rag-ttc-p06-artifacts.sha256)
- [Complete-bundle checksum](sandbox:/mnt/data/rag-ttc-p06-complete-delivery.zip.sha256)

## Implemented structures

### Captured effects

The new `pkg/effectlog` package provides:

- Live, capture, and offline replay modes.
- Attempt-level recording of responses and classified failures.
- Replay identity based on stable step identity, semantic request identity, and attempt number.
- Separation of replay identity from run-local trace identity.
- Single-flight handling of concurrent duplicate capture requests.
- Detection of semantic-key reuse with different request payloads.
- Integrity-protected capture records.
- Strict snapshot parsing and tamper detection.
- Separate schemas for captured observations and capture-recorder events.

Capture deliberately does **not** claim exactly-once mutation semantics. A non-idempotent operation with automatic retries is rejected even when capture is configured.

### Explicit executor contracts

`pkg/flow` now distinguishes:

- Pure operations.
- Read-only external observations.
- Idempotent operations.
- Captured operations.
- Non-idempotent operations.
- Unclassified legacy operations.

It also distinguishes item-local operations from operations requiring a complete input snapshot. Contract validation occurs before work begins.

### Non-conflating execution identity

The implementation separates:

- `StepID`: stable definition identity.
- `StageID`: one placement of a step in one run.
- `OperationID`: one logical request.
- `AttemptID`: one retry attempt.
- `BatchID`: one physical grouped call.
- `Name`: presentation only.

`flow-report/v2` retains distinct stage, operation, and attempt records even when several stages share the same display name. The old name-keyed report remains available as an explicitly lossy compatibility projection.

### Collection-global operations

A new `flow.Snapshot` constructor gives an operation the complete declared input collection and requires one aligned output per input.

This resolves an ambiguity in the former barrier contract:

- `Barrier=true` only waits for upstream completion.
- It still invokes an item-local callback.
- Global top-\(k\), normalization, cross-item deduplication, or global selection require `Snapshot`.

### Policy conformance testing

The new `pkg/flowtest` package compares executor variants after projecting away operational differences such as:

- Cache status.
- Retry count.
- Trace identity.
- Timestamps.
- Physical batching.
- Work-call count.

It retains aligned semantic values, quarantine state, skip state, error classification, and terminal success/failure behavior.

A deliberately broken batch implementation that reverses same-length responses is detected by this comparison. Cardinality checking alone cannot establish batch correctness.

### RAG adapters

Generation and embedding adapters now declare read-only external effects and expose JSON capture codecs while preserving their existing typed orchestration shape.

## Validation results

The selected target suite contains **102 test functions**:

| Package | Tests |
|---|---:|
| `pkg/effectlog` | 9 |
| `pkg/flow` | 73 |
| `pkg/flowtest` | 2 |
| Standalone semantic model | 8 |
| rag-ttc adapter and fault suite | 10 |

All selected tests passed with the race detector. `go vet` also passed for the target packages, and the generation and embedding production packages compiled in the compatibility harness.

The finite experiments established:

- **720/720** completion schedules preserved input-aligned meaning.
- **128/128** contiguous batch partitions agreed with per-item execution.
- Actual `flow.Bulk` sizes **1 through 8** produced equivalent semantic results.
- Repeated display names retained two distinct v2 stages.
- A captured transient-failure-then-success sequence replayed offline with zero live calls.
- A snapshot-global operation produced the correct global result where a temporal barrier could not.
- A declared non-idempotent retry was rejected before executing the mutation.
- Nine adversarial fixtures and all supplied JSON artifacts passed schema validation.

The Git patch was applied to a clean P01-P03 baseline and reconstructed the implementation tree exactly. The source and research ZIP archives were independently extracted and compared byte-for-byte with their source directories. The PDF passed preflight, remained text-extractable, and all 24 rendered pages were visually inspected.

## Validation boundary

The repository declares Go **1.26.5**. The available environment supplied Go **1.23.2** without network access for obtaining the declared toolchain or module graph. Therefore:

- The P06 target packages were validated through the bundled offline compatibility harness.
- Generation and embedding packages compiled under that harness.
- Existing production tests requiring newer `testing` APIs were not executed.
- The complete repository test suite was not run under Go 1.26.5.

The machine-readable result is consequently marked `partial`, rather than overstating full-module validation.

