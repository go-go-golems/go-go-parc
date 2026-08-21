# Explain Pullback Definition

- URL: https://chatgpt.com/c/6a84407e-0e30-83ea-9c85-3915590bdfab
- Created: 2026-08-18T11:23:49.280Z

---

> [image: sediment://file_000000005e5481fba52246e41970d5e3]
> [image: sediment://file_00000000a1b081f98e4e46bec43836c7]
> [image: sediment://file_00000000dff8822fa49e4474e40467f4]
> I don’t understand the definition of the pullback in set in the book, in the case of my first drawing, wouldn’t we end up with many more elements in L than necessary? To me every singleton set would be a pullback?

<details><summary>💭 Thinking</summary>

**Clarifying pullbacks**

I’m distinguishing a commuting square from a genuine pullback. In **Set**, the pullback here is $A\times B$, since both maps land in the singleton and always agree, giving six ordered pairs—not an arbitrary singleton.

**Clarified pullbacks**

</details>

Yes — the key distinction is:

**a pullback is not merely a set $L$ that makes the square commute.**  
It must make the square commute **and satisfy the universal property**.

That second condition is exactly what rules out your singleton idea.

In your first example you have essentially

$$
A=\{1,2,3\},\qquad B=\{2,3\},\qquad C=\{3\},
$$

with

$$
f:A\to C,\qquad g:B\to C.
$$

Since $C$ has only one element, both functions are forced to be constant:

$$
f(1)=f(2)=f(3)=3,\qquad g(2)=g(3)=3.
$$

The book defines the pullback as

$$
L=\{(a,b)\in A\times B:f(a)=g(b)\}.
$$

But here **every pair satisfies that equality**, because both sides are always $3$. So

$$
\boxed{
L=A\times B
=
\{(1,2),(1,3),(2,2),(2,3),(3,2),(3,3)\}.
}
$$

So yes: there are six elements.

### Why can't I use a singleton instead?

Suppose you take

$$
L=\{*\}
$$

and define, for example,

$$
p_A(*)=2,\qquad p_B(*)=3.
$$

Then certainly the square commutes:

$$
f(p_A(*))=f(2)=3=g(3)=g(p_B(*)).
$$

So you've constructed **a cone** over $f$ and $g$.

But it is not the **universal** cone.

Consider another singleton $E=\{e\}$, with maps

$$
h(e)=1,\qquad j(e)=2.
$$

This is also a perfectly valid cone because

$$
f(h(e))=f(1)=3=g(2)=g(j(e)).
$$

The universal property of the pullback says there must be a unique

$$
k:E\to L
$$

such that

$$
p_A\circ k=h,\qquad p_B\circ k=j.
$$

There's only one possible function $k$, namely $k(e)=*$. But then

$$
p_A(k(e))=2\neq1=h(e),
$$

so it doesn't work.

Thus your singleton $L$ fails the universal property.

---

There's a particularly useful way to see **why the book's set of ordered pairs is forced upon us**.

Take any compatible pair

$$
(a,b)
$$

such that

$$
f(a)=g(b).
$$

Now use a singleton $1=\{*\}$ and define

$$
h(*)=a,\qquad j(*)=b.
$$

That's a cone:

$$
\begin{array}{ccc}
&1&\\
&\swarrow h\quad\searrow j&\\
A&&B\\
&\searrow f\quad\swarrow g&\\
&C&
\end{array}
$$

because $f(a)=g(b)$.

If $L$ is really the pullback, universality says there must be a **unique**

$$
k:1\to L
$$

that reproduces $a$ and $b$ under the two projections.

But a function $1\to L$ is just the choice of **one element of $L$**.

So:

> For every compatible pair $(a,b)$, $L$ must contain exactly one element lying over that pair.

That's why in **Set**

$$
\boxed{L\cong\{(a,b)\mid f(a)=g(b)\}.}
$$

Not fewer, because then some compatible pair wouldn't factor through $L$.

Not more (in an essential sense), because if two different elements of $L$ represented the same pair, uniqueness would fail.

So in your example the six elements are not "more than necessary." **All six are required by universality.**

This also gives a useful interpretation of pullbacks:

$$
\boxed{\text{pullback}=\text{set of all compatible pairs}}
$$

where "compatible" means that the two elements give the same result in $C$.

And this explains when a singleton actually *would* be a pullback: exactly when there is only **one** compatible pair $(a,b)$.


---

> Shouldn’t theoretically the notation A x_C B be actually also including f and g, since the selection of the subset of pairs depends not just on C, but on f and g?

Yes. Strictly speaking, **the pullback depends on the entire cospan**

$$
A\xrightarrow{f}C\xleftarrow{g}B,
$$

not merely on the three objects $A,B,C$.

So the notation

$$
A\times_C B
$$

is an abbreviation that assumes $f$ and $g$ are already understood from context. A more explicit notation could be something like

$$
A\times_{(f,C,g)}B
$$

although that is not standard.

You can see why the maps matter immediately in **Set**:

$$
A\times_C B
=
\{(a,b)\in A\times B\mid f(a)=g(b)\}.
$$

Take

$$
A=B=C=\{0,1\}.
$$

If

$$
f=g=\operatorname{id},
$$

then

$$
A\times_C B
=
\{(0,0),(1,1)\}.
$$

But with the **same sets** $A,B,C$, if both $f$ and $g$ are the constant-zero function, then

$$
A\times_C B=A\times B
=
\{(0,0),(0,1),(1,0),(1,1)\}.
$$

And if

$$
f=\operatorname{id},\qquad g(b)=0,
$$

then

$$
A\times_C B
=
\{(0,0),(0,1)\}.
$$

So the symbol $A\times_C B$ by itself does **not** contain enough information to reconstruct the pullback unless the maps to $C$ have already been specified.

There is also a categorical reason the notation is considered reasonable. When people say "$A$ and $B$ are objects **over $C$**," they often mean

$$
(A\xrightarrow{f}C)
\qquad\text{and}\qquad
(B\xrightarrow{g}C).
$$

In other words, the maps $f$ and $g$ are implicitly regarded as part of the data of $A$ and $B$. Formally these are objects of the **slice category** $\mathcal C/C$.

So

$$
A\times_C B
$$

really means something closer to

$$
(A\xrightarrow f C)\times (B\xrightarrow g C)
$$

inside the category of objects over $C$.

Your objection is therefore exactly right: **if all you know are the bare sets $A,B,C$, $A\times_C B$ is ambiguous.** The notation relies on the structure maps $f$ and $g$ being understood.


---

> [image: sediment://file_00000000ef2081f783b33a6813898527]
> [image: sediment://file_00000000471481fbb9c5b4b0635526d1]
> I want to explore pullbacks, and it seems a way to do this is to try out different “special” choices for A and B and f, g, p1, p2 (for example p1 = p2, etc…) and also considering them in different categories. 
>
> Make a list of such special constellation, and then see what conditions can be found when using them in the Type category of types in programming languages .

<details><summary>💭 Thinking</summary>

**Exploring pullbacks**

I’m connecting special cases across categories: products, fibers, equalizers, kernels, and joins. In posets, pullbacks become meets; in algebraic categories, they inherit componentwise structure; in programming, they model equijoins.

**Explored pullbacks**

**Formulating type-level pullbacks**

I’m expressing the pullback as dependent pairs of `a : A` and `b : B` equipped with evidence that `f(a) = g(b)`. I’m also organizing the requested special cases into a clear list.

**Formulated type-level pullbacks**

</details>

Yes. This is a useful way to study pullbacks: start from the generic square, then deliberately make some of the objects/arrows degenerate, identical, injective, constant, terminal, etc., and see what the universal property turns into.

For the programming-language case, I’ll use an idealized **Type** category: objects are types, arrows are pure total functions, and equality behaves set-like. I’ll note below what changes in dependent type theory or languages with partiality.

:::writing{variant="document" id="48317"}
# Pullback Experiments in the Category `Type`

Start with

$$
\begin{array}{ccc}
P &\xrightarrow{p_2}& B\\
{\scriptstyle p_1}\downarrow &&\downarrow{\scriptstyle g}\\
A&\xrightarrow{f}&C
\end{array}
$$

where

$$
P=A\times_C B.
$$

In a set-like category of types,

$$
\boxed{
P=\{(a,b):A\times B\mid f(a)=g(b)\}.
}
$$

In a dependently typed formulation this is more literally

$$
\boxed{
P=\sum_{a:A}\sum_{b:B}(f(a)=g(b)).
}
$$

So an inhabitant contains an $a$, a $b$, and evidence that their outputs agree.

A particularly useful observation is

$$
\operatorname{fib}_{p_2}(b)
\cong
\operatorname{fib}_f(g(b)),
$$

and symmetrically

$$
\operatorname{fib}_{p_1}(a)
\cong
\operatorname{fib}_g(f(a)).
$$

In words: **the possible elements of the pullback lying above $b$ are exactly the $a$'s whose $f$-value matches $g(b)$.**

That one fact explains many of the special cases below.

1. **$C=1$, the terminal/unit type.**

   There is only one function

   $$
   A\to 1,\qquad B\to1.
   $$

   Therefore the compatibility condition is automatic:

   $$
   f(a)=g(b)=*.
   $$

   Hence

   $$
   \boxed{A\times_1B\cong A\times B.}
   $$

   So an ordinary product is a special pullback.

   In programming:

   $$
   \texttt{Pullback<A,B,Unit>} \cong (A,B).
   $$

   This is the book's Example 6.

2. **$A=1$, so $f:1\to C$ chooses a particular value $c:C$.**

   Write

   $$
   f(*)=c.
   $$

   Then

   $$
   1\times_C B
   =
   \{(*,b)\mid c=g(b)\}.
   $$

   Thus

   $$
   \boxed{
   1\times_C B\cong\{b:B\mid g(b)=c\}
   =\operatorname{fib}_g(c).
   }
   $$

   So **fibers are pullbacks**.

   Programming interpretation: take a function

   $$
   g:B\to C
   $$

   and select only values of $B$ whose output is a particular $c$.

   In `Grp`, `Mon`, or `Vec`, choosing the distinguished identity/zero in the codomain gives the ordinary algebraic kernel. This is essentially what the book's Example 4 is doing.

3. **$A=0$ or $B=0$, the empty type.**

   There cannot be any pair $(a,b)$, so

   $$
   \boxed{0\times_CB\cong0}
   $$

   and similarly

   $$
   A\times_C0\cong0.
   $$

4. **One of $f,g$ is the identity.**

   Suppose $A=C$ and

   $$
   f=\operatorname{id}_C.
   $$

   Then

   $$
   P
   =
   \{(c,b)\mid c=g(b)\}.
   $$

   Once $b$ is known, $c$ is forced to be $g(b)$. Therefore

   $$
   \boxed{C\times_C B\cong B.}
   $$

   Explicitly,

   $$
   b\longmapsto(g(b),b).
   $$

   So pulling something back along an identity does nothing, up to isomorphism.

5. **$A=B$ and $f=g$.**

   Now

   $$
   P
   =
   \{(x,y):A\times A\mid f(x)=f(y)\}.
   $$

   This is the **kernel pair** of $f$, exactly the book's Example 3.

   It tells you which inputs are indistinguishable by $f$.

   Two extreme cases are informative.

   If $f$ is injective,

   $$
   f(x)=f(y)\Rightarrow x=y,
   $$

   so

   $$
   P=\{(x,x)\mid x:A\}\cong A.
   $$

   The pullback becomes the diagonal.

   If $f$ is constant, then

   $$
   f(x)=f(y)
   $$

   for every $x,y$, so

   $$
   \boxed{P=A\times A.}
   $$

   Thus the kernel pair measures, in a precise sense, **how much information $f$ forgets**.

6. **Demand $p_1=p_2$.**

   First, this is only type-correct when

   $$
   A=B,
   $$

   because otherwise $p_1$ and $p_2$ have different codomains.

   For

   $$
   f,g:A\to C,
   $$

   the ordinary pullback consists of

   $$
   (x,y)\quad\text{such that}\quad f(x)=g(y).
   $$

   Requiring

   $$
   p_1=p_2
   $$

   says that every compatible pair must actually have

   $$
   x=y.
   $$

   Thus the condition is

   $$
   \boxed{
   f(x)=g(y)\Longrightarrow x=y.
   }
   $$

   Under this condition the pullback reduces to

   $$
   P\cong
   \{x:A\mid f(x)=g(x)\},
   $$

   i.e. an **equalizer-type** object.

   This explains the book's Example 7: if the same arrow $i$ serves as both pullback projections, then $i$ is an equalizer.

   Notice that the converse is not generally true. Knowing only that

   $$
   f(x)=g(x)
   $$

   for the elements of the equalizer does not rule out some off-diagonal pair

   $$
   x\neq y,\qquad f(x)=g(y).
   $$

   A particularly nice subcase is

   $$
   f=g.
   $$

   Then $p_1=p_2$ precisely requires

   $$
   f(x)=f(y)\Rightarrow x=y,
   $$

   so in set-like `Type`:

   $$
   \boxed{
   A=B,\quad f=g,\quad p_1=p_2
   \quad\Longleftrightarrow\quad
   f\text{ is injective}.
   }
   $$

7. **One of the maps is injective.**

   Suppose

   $$
   f:A\to C
   $$

   is injective.

   For each $b:B$, there can be **at most one** $a:A$ satisfying

   $$
   f(a)=g(b).
   $$

   Therefore

   $$
   p_2:P\to B
   $$

   is injective.

   More conceptually,

   $$
   P
   \cong
   \{b:B\mid g(b)\in\operatorname{im}(f)\},
   $$

   together with the uniquely determined corresponding $a$.

   If $f$ is literally an inclusion

   $$
   A\hookrightarrow C,
   $$

   then

   $$
   A\times_C B
   $$

   is just the **inverse image of the subtype $A$** under $g$.

   This is one of the most useful programming interpretations: pulling back a subtype gives a refinement of another type.

8. **One of the maps is surjective.**

   Suppose $f:A\to C$ is surjective.

   Given any $b:B$, $g(b)$ has some preimage $a:A$. Therefore

   $$
   p_2:P\to B
   $$

   is surjective.

   But the sharper condition is worth noticing:

   $$
   p_2\text{ is surjective}
   \iff
   \forall b:B,\ \exists a:A,\ f(a)=g(b).
   $$

   Equivalently,

   $$
   \boxed{
   g(B)\subseteq f(A).
   }
   $$

   So $f$ does not actually have to be surjective onto all of $C$; it only has to cover the part of $C$ reached by $g$.

   Likewise,

   $$
   p_2\text{ injective}
   \iff
   \text{every fiber }f^{-1}(g(b))\text{ has at most one element}.
   $$

   And

   $$
   p_2\text{ bijective}
   \iff
   \text{every fiber }f^{-1}(g(b))\text{ has exactly one element}.
   $$

   These are useful conditions to experiment with.

9. **One map is a bijection/equivalence.**

   If

   $$
   f:A\overset{\sim}{\longrightarrow}C,
   $$

   then for every $b:B$ there is exactly one possible

   $$
   a=f^{-1}(g(b)).
   $$

   Thus

   $$
   \boxed{A\times_CB\cong B.}
   $$

   More categorically: pulling back an isomorphism gives an isomorphism.

10. **One or both maps are constant.**

   Suppose

   $$
   f(a)=c
   $$

   for every $a:A$. Then

   $$
   P
   =
   \{(a,b)\mid c=g(b)\},
   $$

   so

   $$
   \boxed{
   P\cong A\times\operatorname{fib}_g(c).
   }
   $$

   If both are constant,

   $$
   f(a)=c,\qquad g(b)=d,
   $$

   then there are two extremes.

   If $c=d$,

   $$
   \boxed{P\cong A\times B.}
   $$

   If $c\neq d$,

   $$
   \boxed{P\cong0.}
   $$

   This is exactly what happened in your earlier singleton-$C$ example: both functions were necessarily the same constant function, so **every pair became compatible**.

11. **$f$ and $g$ extract a common field from records.**

   This is one of the most concrete programming interpretations.

   Suppose

   $$
   A=X\times C,\qquad B=Y\times C
   $$

   and both maps simply extract the $C$-field:

   $$
   f(x,c)=c,\qquad g(y,c)=c.
   $$

   Then the pullback contains

   $$
   ((x,c),(y,c)).
   $$

   Hence

   $$
   \boxed{
   (X\times C)\times_C(Y\times C)
   \cong X\times Y\times C.
   }
   $$

   More generally, imagine

   ```text
   User  = { id : UserId, name : String }
   Score = { userId : UserId, score : Float }

   f : User  -> UserId
   g : Score -> UserId
   ```

   Then

   $$
   User\times_{UserId}Score
   $$

   is the type of pairs

   ```text
   (user, score)
   ```

   satisfying

   ```text
   user.id == score.userId
   ```

   In database language this is essentially an **equijoin**.

   And categorical conditions become familiar database constraints:

   - uniqueness of `User.id` means $f$ is injective;
   - every `Score.userId` referring to an existing user means $g(B)\subseteq f(A)$;
   - together they imply every score has exactly one matching user, so $p_2$ is a bijection onto `Score`.

12. **$C$ is a tag or enum type.**

   Let

   $$
   f:A\to C,\qquad g:B\to C
   $$

   assign a tag to every value.

   Then the pullback consists of pairs having the **same tag**.

   In fact,

   $$
   \boxed{
   A\times_CB
   \cong
   \sum_{c:C}
   f^{-1}(c)\times g^{-1}(c).
   }
   $$

   This formula is useful in general: a pullback can be viewed as taking each common output $c$, forming the product of the two fibers over $c$, and joining all those products together.

   If

   $$
   C=\texttt{Bool},
   $$

   then schematically

   $$
   A\times_C B
   \cong
   (A_{\mathrm{false}}\times B_{\mathrm{false}})
   +
   (A_{\mathrm{true}}\times B_{\mathrm{true}}).
   $$

   Programming interpretation: pair values only when their variants/states/discriminators agree.

13. **Use the diagonal to produce an equalizer.**

   Given

   $$
   f,g:A\to C,
   $$

   combine them into

   $$
   (f,g):A\to C\times C.
   $$

   There is also the diagonal

   $$
   \Delta:C\to C\times C,\qquad
   c\mapsto(c,c).
   $$

   Take their pullback:

   $$
   \begin{array}{ccc}
   E&\longrightarrow&C\\
   \downarrow&&\downarrow\Delta\\
   A&\xrightarrow{(f,g)}&C\times C.
   \end{array}
   $$

   The condition for $a:A$ to lie in the pullback is

   $$
   (f(a),g(a))=(c,c)
   $$

   for some $c$, which is exactly

   $$
   f(a)=g(a).
   $$

   Therefore

   $$
   \boxed{
   E\cong\{a:A\mid f(a)=g(a)\}.
   }
   $$

   So equalizers themselves can be constructed from pullbacks and products.

## The most useful general rule in `Type`

For studying $p_1,p_2$, look at their fibers:

$$
\boxed{
\operatorname{fib}_{p_2}(b)
\cong
\operatorname{fib}_f(g(b)).
}
$$

Consequently, $p_2$ is injective when every relevant $f$-fiber contains at most one value; $p_2$ is surjective when every relevant $f$-fiber contains at least one value; and $p_2$ is bijective when every relevant $f$-fiber contains exactly one value.

Symmetrically,

$$
\boxed{
\operatorname{fib}_{p_1}(a)
\cong
\operatorname{fib}_g(f(a)).
}
$$

This gives a systematic way to generate further experiments instead of treating the special cases as unrelated tricks.

## What changes in other categories?

In **Set**, the pullback is literally the set of matching pairs.

In a set-like **Type** category, it is the corresponding constrained pair type.

In dependent type theory, the more precise expression is

$$
\sum_{a:A}\sum_{b:B}(f(a)=g(b)),
$$

so an equality witness can itself be part of the data. If equality proofs are proof-irrelevant, this reduces essentially to the set-like picture. In homotopy type theory, where equality can carry nontrivial structure, the distinction matters.

In **Mon**, **Grp**, and **Vec**, the underlying elements are still matching pairs

$$
(a,b)\quad\text{with}\quad f(a)=g(b),
$$

but the pullback also inherits the algebraic structure componentwise. This is why ordinary kernels arise naturally as pullbacks.

In a **poset** regarded as a category, there is at most one arrow between two objects, and the pullback becomes a greatest lower bound/meet. This is the book's Example 5.

In **Top**, the underlying set is again the matching-pair set, but it carries the appropriate subspace topology inherited from $A\times B$.

So the same diagram is detecting quite different familiar constructions depending on the category.

## Programming-language caveat

There isn't a single canonical category called `Type` for every programming language.

The clean model above assumes **total, pure functions**. This corresponds closely to the mathematical view used in total dependent languages and type theories.

For a language in which functions can diverge, throw exceptions, mutate state, perform IO, etc., ordinary functions no longer behave exactly like morphisms in this simple set-like category. One then often changes the category—using partial maps, domains, Kleisli categories for effects, and so on.

For experimentation, the cleanest mental model is therefore:

$$
\boxed{
\text{Type}=\text{types of total values + pure total functions}.
}
$$

Under that interpretation, a pullback is very concretely a **type of synchronized pairs**:

$$
\boxed{
(a,b)\text{ may be paired precisely when }f(a)=g(b).
}
$$

That viewpoint connects products, fibers, inverse images, equalizers, kernel relations, joins, refinements, and algebraic kernels as instances of the same construction.
:::

The cases involving **$f=g$**, **$p_1=p_2$**, and **injectivity/surjectivity of the projections** are especially worth experimenting with, because they expose the universal property rather than merely giving different-looking formulas.

