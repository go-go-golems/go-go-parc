# List and Monoid Defs

- URL: https://chatgpt.com/c/6a773d1b-2e74-83ea-95d1-adfb53cd7551
- Created: 2026-08-08T14:29:13.199Z

---

> [image: sediment://file_000000000944823099a3218ce6fa1564]
> Concise definition of list and monoid, this is a bit too written out imo

A much shorter version:

- **List in a set \(X\):** a finite ordered sequence of elements of \(X\), e.g. \([x_1,\dots,x_n]\). The empty list is \([]\).
- **Monoid:** a set \(M\) with a binary operation \(\ast\) that is **associative** and has an **identity element** \(e\):
  \[
  (a\ast b)\ast c=a\ast(b\ast c),\qquad e\ast a=a\ast e=a.
  \]

For the page specifically:

> **Free monoid on \(X\):** all finite lists of elements of \(X\), with **concatenation** as the operation and \([]\) as the identity.

So you can basically read \(F_X\) as
\[
F_X=(\text{finite strings/lists made from }X,\ \text{concatenation},\ []).
\]


---

> Like you would find in A math textbook

**Definition.** Let \(X\) be a set. A **list in \(X\)** is a finite ordered sequence
\[
[x_1,\ldots,x_n], \qquad x_i\in X.
\]
The unique list of length \(0\) is called the **empty list** and is denoted \([]\).

**Definition.** A **monoid** is a set \(M\) equipped with an associative binary operation
\[
\ast:M\times M\to M
\]
and an identity element \(e\in M\) such that
\[
e\ast x=x\ast e=x
\]
for every \(x\in M\).

**Definition.** The **free monoid on \(X\)** is the set of all finite lists in \(X\), with list concatenation as its operation and the empty list \([]\) as its identity.


---

> Search for a bunch of definitions of free monoid online and in textbooks and list them and compare them and what their pros and cons are if they vary

<details><summary>💭 Thinking</summary>

**Planning the comparison**

I’m collecting authoritative online textbook and reference treatments of free monoids, then I’ll compare their equivalent definitions, notation, and explanatory strengths rather than relying on a single presentation.

**Planned the comparison**

</details>

```json
{"system1_search_query":[{"q":"site:math.mit.edu free monoid definition words concatenation pdf"},{"q":"site:math.ucr.edu free monoid universal property monoid pdf"},{"q":"Leinster Basic Category Theory free monoid pdf definition"},{"q":"free monoid definition textbook words concatenation universal property"}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Searched 23 websites**

**Comparing definitions**

I’m now comparing several standard formulations: finite strings, formal words, finite-list coproducts, universal properties, and “generators with no relations.” I’ll note where each is clearest, strongest, or more abstract, with representative sources.

**Compared definitions**

</details>

```json
{"open":[{"ref_id":"turn994999search32"},{"ref_id":"turn739924view1","lineno":7382},{"ref_id":"turn739924view2","lineno":36629},{"ref_id":"turn739924view3","lineno":3469},{"ref_id":"turn975303search1"},{"ref_id":"turn975303search0"},{"ref_id":"turn549383search28"},{"ref_id":"turn549383search4"}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Searched 6 websites**

</details>

I checked a mix of algebra, combinatorics, category-theory, and discrete-math sources. There are really **four styles of definition**, rather than fundamentally different definitions. The main choice is whether the author wants to tell you **what the free monoid consists of** or **what makes it free**.

1. **David Spivak, *Category Theory for the Sciences*** — the book in your photo. Spivak defines the free monoid on \(X\) concretely as
   \[
   F_X=(\operatorname{List}(X),[],++)
   \]
   where the elements are finite lists, the operation is concatenation, and the empty list is the identity. citeturn258731view3 Later he proves the characteristic property
   \[
   \operatorname{Hom}_{\mathbf{Mon}}(F(G),M)
   \cong
   \operatorname{Hom}_{\mathbf{Set}}(G,M),
   \]
   i.e. a map from the generators uniquely determines a monoid homomorphism. citeturn739924view3 **Pro:** extremely concrete and works naturally with his earlier definition of lists. **Con:** as a standalone definition it doesn't tell you why the adjective *free* is being used. Also, the preceding fully set-theoretic definition of a list as a pair \((n,f)\) makes it look much heavier than the actual idea.

2. **Richard Stanley, *Enumerative Combinatorics*, Vol. 1.** Stanley takes a set \(A\), calls it an alphabet, defines a word to be a finite sequence of elements of \(A\), includes the empty word \(1\), and defines multiplication by juxtaposition. The resulting \(A^*\) is the free monoid on \(A\). citeturn258731view2 In compressed form, his approach is essentially
   \[
   A^*=\{\text{finite words over }A\},
   \qquad
   uv=\text{juxtaposition of }u,v.
   \]
   **Pro:** probably the cleanest traditional algebra/combinatorics presentation. Very little machinery. **Con:** calling the empty word \(1\) can initially make it look like a numerical element, and the definition again doesn't itself explain “free.”

3. **James Milne, *Group Theory*.** Milne first gives the word construction: finite words in symbols from \(X\), multiplication by juxtaposition, and the empty word as identity. He then immediately states the universal property: every set map \(X\to S\) into a monoid \(S\) extends uniquely to a homomorphism from the free monoid. citeturn258731view4 **Pro:** pedagogically the most complete version I found, because you get both the concrete object and the meaning of *free*. **Con:** too long if you only want a one-line reference definition.

4. **Emily Riehl, *Category Theory in Context*.** Riehl writes the underlying set very compactly as
   \[
   \coprod_{n\ge0}X^n,
   \]
   the set of all finite lists of elements of \(X\), including the empty list. She presents this as the free construction left adjoint to the forgetful functor \(\mathbf{Monoid}\to\mathbf{Set}\). citeturn258731view1 **Pro:** mathematically compact and very clean once you know coproducts/adjoints. It also makes the structure of the set completely explicit: words of length \(0\), words of length \(1\), words of length \(2\), etc. **Con:** \(\coprod\) and “left adjoint” are much more machinery than is warranted if you're merely defining free monoids for the first time.

5. **Steve Awodey, category-theory treatment.** Awodey's notes construct
   \[
   FX=\{x_1\cdots x_n\mid n\ge0,\ x_i\in X\}
   \]
   with concatenation and the empty sequence, and then say precisely what “free” means: for every monoid \(M\) and function \(f:X\to U(M)\), there exists a unique monoid homomorphism \(FX\to M\) extending \(f\). citeturn258731view0 The universal-property formulation is also used as the definition in references citing Awodey's *Category Theory*. citeturn142499view2 **Pro:** this is the conceptually strongest definition. It characterizes the free monoid without depending on lists, strings, or a particular construction. **Con:** it's a poor first sentence if the reader doesn't already understand universal properties.

6. **Doerr–Levasseur, *Applied Discrete Structures* / formal-language convention.** Here \(A\) is an alphabet, a word/string is a finite sequence of letters, the empty string is \(\lambda\), and
   \[
   A^*=A^0\cup A^1\cup A^2\cup\cdots,
   \qquad A^0=\{\lambda\}.
   \]
   Concatenation makes \(A^*\) a monoid. citeturn142499view0 **Pro:** excellent if you're doing automata, languages, or computer science; \(A^*\) is the standard notation you will constantly encounter. **Con:** it can make “free monoid” sound like a special fact about strings rather than a general algebraic free-object construction.

7. **General online references such as Wikipedia and ProofWiki.** Wikipedia gives the very direct “finite sequences/strings + concatenation + empty string” definition and uses \(A^*\); it also points out that this object satisfies the universal property of a free object. citeturn142499view1 ProofWiki goes the opposite way and defines a free monoid directly by the universal mapping property. citeturn142499view2 **Pro:** seeing the two side by side makes the distinction especially clear. **Con:** the UMP-only version is elegant but not useful for actually picturing an element until someone tells you that the canonical model is finite words.

### What actually varies

There isn't a substantive disagreement. The **concrete definition**
\[
X^*=\{\text{finite words in elements of }X\}
\]
with concatenation and empty word gives an object satisfying the **abstract definition**
\[
\forall\, f:X\to U(M),\qquad
\exists!\,\bar f:X^*\to M
\]
with \(\bar f\) a monoid homomorphism extending \(f\). Milne and Awodey explicitly put both descriptions together, and Spivak proves the same relationship shortly after his concrete definition. citeturn258731view4turn258731view0turn739924view3

There is also a third algebraic slogan:

\[
\boxed{\text{free monoid on }X
      =\text{monoid generated by }X\text{ with no relations}}
\]

Spivak himself notes immediately afterward that a free monoid is a presented monoid with the set of relations empty. citeturn739924view3 This is an excellent explanation of the word *free*, but a bad literal definition unless presentations have already been introduced.

### The definition I'd actually put in a textbook

For the level/style of the book you're reading, I think the cleanest version is:

> **Definition.** Let \(X\) be a set. The **free monoid on \(X\)** is the monoid \(X^*\) of finite words in elements of \(X\), with multiplication given by concatenation and identity given by the empty word \(\varepsilon\).

Or, if you want it slightly more formal without becoming verbose:

\[
\boxed{
X^*:=\coprod_{n\ge0}X^n,
\qquad
\text{with concatenation and empty word }\varepsilon.
}
\]

Then **after** that definition I would add one sentence:

> Equivalently, \(X^*\) is characterized by the property that every function \(X\to M\) into a monoid \(M\) extends uniquely to a monoid homomorphism \(X^*\to M\).

That gives you Stanley's concision plus Milne/Awodey's explanation of what “free” actually means. citeturn258731view2turn258731view4turn258731view0

So yes: compared with a lot of other textbooks, **the page you photographed is unusually written out because Spivak is formally constructing “list” from sets and functions first**. The free-monoid definition itself does not need most of that apparatus once you are comfortable treating finite lists/words as familiar objects. citeturn258731view3


---

> Define homomorphism on set

For **sets alone**, the corresponding notion is simply a **function** (or map), not usually called a homomorphism.

> **Definition.** Let \(X\) and \(Y\) be sets. A **function**
> \[
> f:X\to Y
> \]
> assigns to each \(x\in X\) a unique element \(f(x)\in Y\).

A **homomorphism** is a function that additionally **preserves algebraic structure**.

For example, if \(M,N\) are monoids, a **monoid homomorphism** is a function
\[
f:M\to N
\]
such that
\[
f(xy)=f(x)f(y),\qquad f(e_M)=e_N.
\]

So in the category \(\mathbf{Set}\), the morphisms are just functions.


---

> [image: sediment://file_00000000a66081f7be54f7b9519fcb90]
> [image: sediment://file_000000007d0881f7ad406eb8235d4172]
> Do the same for the monad definition from spivak: math textbook format, then look for definitions across textbooks and resources and compare

<details><summary>💭 Thinking</summary>

**Planning the comparison**

I’m going to use the provided definition as a starting point, then compare it with textbook and authoritative mathematical formulations. I’ll focus on the shared structure, notation differences, and any genuinely substantive distinctions.

**Planned the comparison**

</details>

```json
{"system1_search_query":[{"q":"site:emilyriehl.github.io Category Theory in Context monad pdf definition monad"},{"q":"site:arxiv.org Leinster Basic Category Theory monad definition pdf"},{"q":"site:andrew.cmu.edu awodey category theory monad definition pdf"},{"q":"site:mit.edu Spivak Category Theory for the Sciences monad definition pdf"}],"response_length":"medium"}
```

<details><summary>💭 Thinking</summary>

**Searched 21 websites**

**Comparing definitions**

I’m distinguishing notation from substance: every source presents an endofunctor \(T\), a unit \(\eta\), multiplication \(\mu\), and two laws. The conceptual explanation varies, especially between algebraic, categorical, and computational presentations.

</details>

The cleanest version of Spivak's definition is substantially shorter than the presentation in the book.

### Textbook definition

**Definition.** Let \(\mathcal C\) be a category. A **monad** on \(\mathcal C\) is a triple
\[
(T,\eta,\mu)
\]
consisting of an endofunctor
\[
T:\mathcal C\to\mathcal C
\]
and natural transformations
\[
\eta:1_{\mathcal C}\Rightarrow T,
\qquad
\mu:T^2\Rightarrow T,
\]
such that
\[
\boxed{\mu\circ T\eta=1_T=\mu\circ\eta T}
\]
and
\[
\boxed{\mu\circ T\mu=\mu\circ\mu T.}
\]
These are called the **unit laws** and **associativity law**, respectively.

Here \(T^2=T\circ T\). Equivalently, for every object \(X\),
\[
\mu_X\circ T(\eta_X)
=
1_{TX}
=
\mu_X\circ\eta_{TX},
\]
and
\[
\mu_X\circ T(\mu_X)
=
\mu_X\circ\mu_{TX}.
\]

For **Spivak's definition**, simply take
\[
\mathcal C=\mathbf{Set}.
\]

That is exactly what the two pages you photographed are saying, with the laws expressed as diagrams rather than equations.

For the list monad, for example,
\[
T(X)=\operatorname{List}(X),\qquad
\eta_X(x)=[x],
\]
while
\[
\mu_X:\operatorname{List}(\operatorname{List}(X))
\longrightarrow \operatorname{List}(X)
\]
**flattens a list of lists**:
\[
[[a,b],[c],[],[d,e]]
\longmapsto
[a,b,c,d,e].
\]

### How other sources define it

I checked several mathematical texts and programming-oriented sources. The important result is that there is very little disagreement about the mathematical definition; what varies is **which equivalent presentation is taken as fundamental**.

1. **Spivak, *Category Theory for the Sciences*.** Spivak specializes immediately to \(\mathbf{Set}\):
   \[
   T:\mathbf{Set}\to\mathbf{Set},\qquad
   \eta:\operatorname{id}_{\mathbf{Set}}\Rightarrow T,\qquad
   \mu:T\circ T\Rightarrow T,
   \]
   followed by the unit and associativity diagrams. This is the definition visible in your photographs.

   **Pro:** concrete. Since his examples are lists, observations, probability-like constructions, etc., working in \(\mathbf{Set}\) keeps the reader grounded.

   **Con:** the restriction to \(\mathbf{Set}\) is unnecessary mathematically and can obscure the fact that monads are inherently categorical objects. Replacing `Set` by an arbitrary \(\mathcal C\) gives the standard general definition with essentially no extra complexity.

2. **Emily Riehl, *Category Theory in Context*.** Riehl gives almost exactly the compact definition above: an endofunctor \(T:\mathcal C\to\mathcal C\), a unit \(\eta:\mathrm{id}_{\mathcal C}\Rightarrow T\), and multiplication \(\mu:T^2\Rightarrow T\), satisfying the unit and associativity diagrams. citeturn211015view0

   She then gives the conceptual reformulation:
   \[
   \boxed{\text{a monad on }\mathcal C
   \text{ is a monoid in the category of endofunctors of }\mathcal C.}
   \]
   Here endofunctors are multiplied by composition, the identity functor plays the role of \(1\), \(\mu\) is multiplication, and \(\eta\) is the unit. citeturn211015view1

   **Pro:** probably the best conventional mathematical definition. It is general, concise, and immediately reveals why the axioms look exactly like monoid axioms.

   **Con:** the "monoid in the category of endofunctors" formulation is beautifully concise only after you already understand monoidal categories. For a first encounter, it can explain almost nothing.

3. **Barr & Wells, *Toposes, Triples and Theories*.** This older textbook uses the term **triple**:
   \[
   \mathbb T=(T,\eta,\mu),
   \]
   where \(T\) is an endofunctor and \(\eta,\mu\) satisfy exactly the same unit and associativity diagrams. The authors explicitly note that *monad*, *triad*, *standard construction*, and *fundamental construction* have also been used for the same object. citeturn748529search0

   **Pro:** useful historically, and it makes clear that \((T,\eta,\mu)\) really is the entire structure—there is nothing mysterious hiding behind the term "monad."

   **Con:** "triple" is now dated terminology. It also says much less about the nature of the structure than "monoid among endofunctors."

4. **Ahrens & Wullaert, *Category Theory for Programming*.** They first give the ordinary definition
   \[
   (T,\eta,\mu),
   \qquad
   T:\mathcal C\to\mathcal C,\quad
   \eta:\mathrm{Id}\Rightarrow T,\quad
   \mu:T^2\Rightarrow T,
   \]
   with the same laws. citeturn796384view0 But they also present an equivalent **Kleisli triple** formulation. Instead of giving \(\mu\), one gives
   \[
   \eta_X:X\to TX
   \]
   and, for every
   \[
   f:X\to TY,
   \]
   an extension
   \[
   f^*:TX\to TY,
   \]
   satisfying suitable identity and associativity laws. citeturn796384view1 They explicitly have the reader construct each formulation from the other. citeturn796384view0

   **Pro:** much closer to how monads are *used*. A map
   \[
   X\to TY
   \]
   can be extended to
   \[
   TX\to TY,
   \]
   which directly describes chaining monadic operations.

   **Con:** it conceals the extraordinarily clean algebraic structure
   \[
   T^2\xrightarrow{\mu}T.
   \]
   For pure category theory, \((T,\eta,\mu)\) is generally more transparent.

5. **Eugenio Moggi, *Notions of Computation and Monads*.** Moggi likewise gives both formulations. His categorical definition is the standard
   \[
   (T,\eta,\mu)
   \]
   definition, and immediately afterward he proves a one-to-one correspondence between monads and Kleisli triples. citeturn417871view0 This is important in computer science because a Kleisli arrow
   \[
   X\to TY
   \]
   can be interpreted as a computation taking an \(X\) and producing a \(Y\) with some computational effect.

   Moggi later introduces **strong monads**, which have additional structure needed for certain treatments of products and programming contexts. That is an *extra structure on a monad*, not a competing definition of an ordinary monad. citeturn417871view2

   **Pro:** gives perhaps the clearest bridge between the abstract categorical object and its computational interpretation.

   **Con:** if you encounter "strong monad" too early, it is easy to mistakenly think the additional strength map belongs to the definition of every monad.

6. **The Haskell formulation.** The Haskell 2010 report presents a monad operationally through
   \[
   \operatorname{return}:A\to MA
   \]
   and
   \[
   (\mathbin{>>=}):MA\to(A\to MB)\to MB,
   \]
   together with left-unit, right-unit, and associativity laws. citeturn462672search0turn462672search32

   This is essentially the **Kleisli formulation** in programming notation:
   \[
   \eta_X:X\to TX
   \]
   corresponds to `return`, while
   \[
   TX\times(X\to TY)\to TY
   \]
   corresponds to `>>=`.

   **Pro:** excellent for actually programming with monads. Composition of effectful operations is front and center.

   **Con:** poor as the primary mathematical definition. The endofunctor and natural transformations are largely implicit, and the formulation is tied to the ambient type system rather than making sense immediately in an arbitrary category.

### What is actually varying?

There are essentially **three equivalent definitions worth remembering**.

The standard categorical one is

\[
\boxed{
T:\mathcal C\to\mathcal C,\qquad
\eta:1_{\mathcal C}\Rightarrow T,\qquad
\mu:T^2\Rightarrow T
}
\]

with
\[
\mu\,T\eta=\mu\,\eta T=1_T,
\qquad
\mu\,T\mu=\mu\,\mu T.
\]

The abstract algebraic one is

\[
\boxed{\text{A monad is a monoid in }(\operatorname{End}(\mathcal C),\circ,1_{\mathcal C}).}
\]

Riehl explicitly identifies the two. citeturn211015view1

And the Kleisli/programming one is

\[
\boxed{
X\xrightarrow{\eta_X}TX,
\qquad
\frac{f:X\to TY}{f^*:TX\to TY},
}
\]

with identity and associativity laws. Ahrens–Wullaert and Moggi explicitly establish its equivalence with the \(T,\eta,\mu\) presentation. citeturn796384view2turn417871view0

For a **math textbook/your notes**, I would use exactly this:

> **Definition.** A **monad** on a category \(\mathcal C\) is an endofunctor \(T:\mathcal C\to\mathcal C\) equipped with natural transformations
> \[
> \eta:1_{\mathcal C}\Rightarrow T,
> \qquad
> \mu:T^2\Rightarrow T,
> \]
> satisfying
> \[
> \mu\circ T\eta=\mu\circ\eta T=1_T,
> \qquad
> \mu\circ T\mu=\mu\circ\mu T.
> \]

And immediately underneath it I'd put the mnemonic

\[
\boxed{\text{monad}=\text{monoid of endofunctors}}
\]

and, specifically for the list example,

\[
\boxed{\eta=\text{singleton},\qquad \mu=\text{flatten}.}
\]

That captures almost everything spread across those two Spivak pages in a few lines.


---

> [image: sediment://file_000000000c6481f78c212e15f50cde2f]
> Are these diagrams for u and n correct in set?

Yes — the **two functor-level diagrams are correct** for the list monad on \(\mathbf{Set}\).

For the unit,
\[
\eta:\operatorname{id}_{\mathbf{Set}}\Rightarrow \operatorname{List},
\]
so your diagram

\[
\begin{array}{c}
\mathbf{Set}\xrightarrow{\operatorname{id}_{\mathbf{Set}}}\mathbf{Set}\\
\Downarrow\eta\\
\mathbf{Set}\xrightarrow{\operatorname{List}}\mathbf{Set}
\end{array}
\]

is right.

And for multiplication,
\[
\mu:\operatorname{List}\circ\operatorname{List}\Rightarrow\operatorname{List},
\]
so your second diagram is also right:
\[
\begin{array}{c}
\mathbf{Set}\xrightarrow{\operatorname{List}\circ\operatorname{List}}\mathbf{Set}\\
\Downarrow\mu\\
\mathbf{Set}\xrightarrow{\operatorname{List}}\mathbf{Set}.
\end{array}
\]

### One correction to your note underneath

You wrote something like

\[
\eta_X=\operatorname{id}_{\mathbf{Set}}\text{ applied to }X?
\]

Not quite. Applying the two **functors** to \(X\) gives
\[
\operatorname{id}_{\mathbf{Set}}(X)=X,
\qquad
\operatorname{List}(X)=\operatorname{List}(X).
\]

Then \(\eta_X\) is the **component of the natural transformation** connecting those two objects:

\[
\boxed{\eta_X:X\to\operatorname{List}(X)}
\]

and specifically
\[
\boxed{x\mapsto[x].}
\]

Likewise,
\[
\boxed{
\mu_X:
\operatorname{List}(\operatorname{List}(X))
\to
\operatorname{List}(X)
}
\]
is flattening:
\[
[[a,b],[c,d],[e]]
\mapsto
[a,b,c,d,e].
\]

So the distinction to keep straight is

\[
\begin{aligned}
\eta &: \operatorname{id}_{\mathbf{Set}}\Rightarrow \operatorname{List}
&&\text{natural transformation},\\
\eta_X &: X\to\operatorname{List}(X)
&&\text{ordinary function at a particular set }X,
\end{aligned}
\]

and similarly for \(\mu\).

Your diagrams themselves are good; I'd just replace the line under \(\eta\) with
\[
\boxed{\eta_X:X\to\operatorname{List}(X),\quad x\mapsto[x].}
\]


---

> Explain Kleisli more and who he was and what he contributed

```json
{"system1_search_query":[{"q":"Heinrich Kleisli mathematician biography"},{"q":"Heinrich Kleisli Every standard construction is induced by a pair of adjoint functors 1965 PDF"},{"q":"Kleisli category original paper monad standard construction adjoint functors"},{"q":"Heinrich Kleisli University of Ottawa obituary"}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Searched 28 websites**

**Explaining Kleisli composition**

I’m defining the Kleisli category for a monad, then connecting its composition rule to bind. For the list monad, composition becomes mapping followed by flattening—essentially `flatMap`.

**Explained Kleisli composition**

</details>

```json
{"open":[{"ref_id":"turn342181search12"}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Searched 1 website**

</details>

Yes. The **Kleisli viewpoint** is especially useful for understanding what \(\eta\) and \(\mu\) are actually doing, rather than treating the monad laws as formal diagrams.

### Heinrich Kleisli

**Heinrich Kleisli (1930–2011)** was a Swiss mathematician and category theorist. He spent most of his career at the University of Fribourg, where he became a professor in 1966–67 and remained until 2000; he also served as dean and later vice-rector. citeturn953095view2turn600745search0

The work for which his name is now most familiar is his 1965 paper

*Every standard construction is induced by a pair of adjoint functors.*

In the terminology of the time, "standard construction" was what we now discuss in terms of monads/comonads. Kleisli proved a converse to an earlier observation of Peter Huber: not only does an adjunction produce this monadic structure, but **every such structure can itself be obtained from an adjunction**. citeturn953095view0

That theorem leads to what is now called the **Kleisli category**.

---

## The main idea of a Kleisli category

Suppose you have a monad

\[
(T,\eta,\mu)
\]

on a category \(\mathcal C\).

Normally, a morphism from \(X\) to \(Y\) is

\[
f:X\to Y.
\]

But suppose instead you repeatedly encounter maps of the form

\[
\boxed{f:X\to TY.}
\]

These do **not** compose in the ordinary way. If

\[
f:X\to TY,
\qquad
g:Y\to TZ,
\]

then you cannot write \(g\circ f\), because

\[
X\xrightarrow{f}TY
\]

ends at \(TY\), whereas \(g\) expects an input in \(Y\).

The monad gives you exactly enough machinery to fix this.

Apply \(T\) to \(g\):

\[
Tg:TY\to T(TZ)=T^2Z.
\]

Now you can compose:

\[
X
\xrightarrow{f}
TY
\xrightarrow{Tg}
T^2Z.
\]

But you've acquired an unwanted extra \(T\). This is **precisely what \(\mu\) removes**:

\[
T^2Z\xrightarrow{\mu_Z}TZ.
\]

Hence

\[
\boxed{
g\star f
=
\mu_Z\circ T(g)\circ f
:
X\to TZ.
}
\]

That operation \(\star\) is **Kleisli composition**.

So instead of thinking of \(\mu\) vaguely as "monad multiplication", you can think:

\[
\boxed{\mu:T^2\Rightarrow T
\quad\text{is what makes maps }X\to TY\text{ composable}.}
\]

This construction is the modern form of the category arising from Kleisli's 1965 argument. citeturn953095view0

---

# Definition in textbook form

**Definition.** Let \((T,\eta,\mu)\) be a monad on a category \(\mathcal C\). The **Kleisli category** \(\mathcal C_T\) is defined by

\[
\operatorname{Ob}(\mathcal C_T)
=
\operatorname{Ob}(\mathcal C),
\]

and

\[
\boxed{
\operatorname{Hom}_{\mathcal C_T}(X,Y)
=
\operatorname{Hom}_{\mathcal C}(X,TY).
}
\]

The identity on \(X\) is

\[
\boxed{\eta_X:X\to TX,}
\]

and the composite of

\[
f:X\to TY,
\qquad
g:Y\to TZ
\]

is

\[
\boxed{
g\star f
=
\mu_Z\circ T(g)\circ f.
}
\]

Now something quite nice happens:

\[
\boxed{
\text{the monad laws are exactly what make this into a category.}
}
\]

The two unit laws

\[
\mu\circ T\eta=1_T,
\qquad
\mu\circ\eta T=1_T
\]

ensure that \(\eta_X\) acts as the identity morphism, while

\[
\mu\circ T\mu=\mu\circ\mu T
\]

ensures that Kleisli composition is associative.

So there is a direct correspondence:

\[
\begin{array}{c|c}
\text{Monad structure} & \text{Kleisli category structure}\\
\hline
\eta & \text{identities}\\
\mu & \text{composition}\\
\text{unit laws} & \text{identity laws}\\
\text{associativity of }\mu & \text{associativity of composition}
\end{array}
\]

That is one of the best ways to understand why those particular monad axioms occur.

---

# Your List monad makes this extremely concrete

Take

\[
T=\operatorname{List}.
\]

You've already written

\[
\eta_X:X\to\operatorname{List}(X),
\qquad
x\mapsto[x],
\]

and

\[
\mu_X:
\operatorname{List}(\operatorname{List}(X))
\to
\operatorname{List}(X),
\]

where \(\mu\) concatenates/flatten lists.

Now consider two Kleisli arrows:

\[
f:X\to\operatorname{List}(Y),
\]

\[
g:Y\to\operatorname{List}(Z).
\]

For example suppose

\[
f(x)=[y_1,y_2],
\]

and

\[
g(y_1)=[z_1,z_2],
\qquad
g(y_2)=[z_3,z_4].
\]

Start with \(x\):

\[
x
\overset{f}{\longmapsto}
[y_1,y_2].
\]

Apply \(g\) entrywise, i.e. apply \(\operatorname{List}(g)\):

\[
[y_1,y_2]
\longmapsto
[[z_1,z_2],[z_3,z_4]].
\]

That's

\[
Tg:
TY\to T^2Z.
\]

Then \(\mu_Z\) flattens:

\[
[[z_1,z_2],[z_3,z_4]]
\overset{\mu_Z}{\longmapsto}
[z_1,z_2,z_3,z_4].
\]

Thus

\[
\boxed{
(g\star f)(x)
=
[z_1,z_2,z_3,z_4].
}
\]

In one line:

\[
X
\xrightarrow{f}
\operatorname{List}(Y)
\xrightarrow{\operatorname{List}(g)}
\operatorname{List}(\operatorname{List}(Z))
\xrightarrow{\mu_Z}
\operatorname{List}(Z).
\]

This gives a much more operational interpretation of your diagrams:

\[
\eta=\text{put one value into the context},
\]

\[
\mu=\text{collapse two layers of context into one}.
\]

For `List`:

\[
\boxed{\eta(x)=[x],\qquad \mu=\operatorname{flatten}.}
\]

---

## Why is \(\eta\) the identity in the Kleisli category?

This is initially strange because in \(\mathbf{Set}\),

\[
\eta_X:X\to TX
\]

certainly isn't the ordinary identity function

\[
1_X:X\to X.
\]

But remember what a morphism

\[
X\longrightarrow X
\]

**means inside the Kleisli category**.

By definition,

\[
\operatorname{Hom}_{\mathcal C_T}(X,X)
=
\operatorname{Hom}_{\mathcal C}(X,TX).
\]

So an identity morphism in the Kleisli category has to be an ordinary morphism

\[
X\to TX.
\]

And the canonical choice is exactly

\[
\boxed{\eta_X:X\to TX.}
\]

For List,

\[
x\mapsto[x].
\]

It says, roughly:

> Return \(x\) without introducing any additional list branching.

That's why `[x]`, rather than \(x\), is the "do nothing" operation in the world of list-valued computations.

---

# Kleisli triples

This also explains the term **Kleisli triple**.

Instead of defining a monad using

\[
T,\eta,\mu,
\]

you can equivalently describe it by giving \(\eta\) and a way of extending every map

\[
f:X\to TY
\]

to a map

\[
\boxed{f^*:TX\to TY.}
\]

The extension is defined from the ordinary monad structure by

\[
\boxed{
f^*
=
\mu_Y\circ T(f).
}
\]

Graphically,

\[
TX
\xrightarrow{T(f)}
T^2Y
\xrightarrow{\mu_Y}
TY.
\]

For the List monad:

\[
f:X\to\operatorname{List}(Y)
\]

becomes

\[
f^*:
\operatorname{List}(X)
\to
\operatorname{List}(Y).
\]

What does \(f^*\) do?

Take

\[
[x_1,x_2,x_3].
\]

First apply \(f\) to each entry:

\[
[f(x_1),f(x_2),f(x_3)],
\]

which is a **list of lists**, and then flatten it.

Thus

\[
\boxed{
f^*([x_1,\ldots,x_n])
=
f(x_1)++\cdots++f(x_n).
}
\]

And now Kleisli composition becomes simply

\[
\boxed{
g\star f=g^*\circ f.
}
\]

This is essentially the operation that later appears in functional programming as **bind** or `flatMap`. Monads became important in functional programming much later, particularly for structuring computations involving effects such as state, exceptions, I/O, and nondeterminism. Wadler's work is one of the major early presentations of that programming viewpoint. citeturn549656search0

---

# Kleisli's actual contribution to monad theory

There is a historical subtlety worth knowing. **Kleisli did not simply "invent monads."** The structure had appeared earlier under names such as *standard construction*, particularly in work of Roger Godement and Peter Huber. Huber had shown that an adjoint pair produces such a construction. Kleisli's 1965 paper proves the converse: starting from the structure, he explicitly constructs a category and an adjoint pair producing it. citeturn953095view0turn835503search1

In modern monad notation, the result can be summarized beautifully:

\[
\boxed{
\text{Every monad comes from an adjunction.}
}
\]

Starting from

\[
(T,\eta,\mu)
\quad\text{on }\mathcal C,
\]

Kleisli constructs

\[
\mathcal C
\underset{U_T}{\overset{F_T}{\rightleftarrows}}
\mathcal C_T
\]

with

\[
F_T\dashv U_T
\]

such that

\[
\boxed{U_TF_T=T.}
\]

So the monad you started with is recovered from the adjunction.

Samuel Eilenberg and John Moore developed another canonical category associated to a monad during the same period—the **Eilenberg–Moore category**, whose objects are \(T\)-algebras rather than merely the objects of \(\mathcal C\). citeturn835503search0

The contrast is useful:

\[
\boxed{
\begin{aligned}
\text{Kleisli:}&\quad
\text{same objects, change the morphisms;}\\[2mm]
\text{Eilenberg--Moore:}&\quad
\text{change the objects by adding }T\text{-algebra structure.}
\end{aligned}}
\]

Both reveal how a monad arises from an adjunction, but from opposite perspectives.

### The version I would put in your notes

Given what you're currently working through, I'd write:

> **Kleisli category.** For a monad \((T,\eta,\mu)\) on \(\mathcal C\), the Kleisli category \(\mathcal C_T\) has the same objects as \(\mathcal C\), with
> \[
> \operatorname{Hom}_{\mathcal C_T}(X,Y)
> :=
> \operatorname{Hom}_{\mathcal C}(X,TY).
> \]
> Its identities are \(\eta_X\), and composition is
> \[
> g\star f:=\mu_Z\circ T(g)\circ f.
> \]

Then underneath:

\[
\boxed{
X\xrightarrow{f}TY
\xrightarrow{Tg}T^2Z
\xrightarrow{\mu}TZ
}
\]

and the mnemonic

\[
\boxed{
\eta=\text{identity for effectful arrows},
\qquad
\mu=\text{what makes effectful arrows compose}.
}
\]

For the **List monad**, this is particularly strong: Kleisli arrows are literally **set functions returning zero or more possible outputs**, and Kleisli composition means "apply the next multivalued operation to every result, then flatten." That's probably the most concrete route from the Spivak diagrams you're currently looking at to why monads are structured the way they are.

