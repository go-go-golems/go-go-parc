# Lattice Theory Abstraction

- URL: https://chatgpt.com/c/6a8059ed-737c-83ea-bab1-f0869ce27b77
- Created: 2026-08-15T12:22:50.129Z

---

> [image: sediment://file_0000000027f081fbad19c05c94f2447f]
> It talks about the basic idea for abstracting set theory into lattice theory. What does that mean and which section of the lattice book at the top should I read

<details><summary>💭 Thinking</summary>

**Explaining the abstraction**

I’m interpreting the statement as replacing membership with inclusion: represent each element $x$ by $\{x\}$, so $x\in S$ exactly when $\{x\}\subseteq S$. Read “Ordered sets,” then “Lattices as ordered sets” and “Complete lattices.”

**Explained the abstraction**

</details>

The sentence at the bottom is referring to this observation:

$$
x\in S \quad\Longleftrightarrow\quad \{x\}\subseteq S.
$$

That looks trivial, but it suggests a useful abstraction: **replace reasoning about membership $\in$ with reasoning about the ordering relation $\subseteq$.**

For example, fix some universe $X$ and consider its power set

$$
\mathcal P(X)=\{S:S\subseteq X\}.
$$

Instead of thinking about the internal contents of each set, treat every subset of $X$ as an abstract object and put an order on these objects:

$$
A\le B \quad\text{means}\quad A\subseteq B.
$$

Now familiar set operations become order-theoretic constructions:

$$
A\wedge B=A\cap B,\qquad
A\vee B=A\cup B,
$$

with

$$
\bot=\varnothing,\qquad \top=X.
$$

So the picture is essentially

$$
\boxed{\text{sets + inclusion}}
\quad\longrightarrow\quad
\boxed{\text{partially ordered set}}
\quad\longrightarrow\quad
\boxed{\text{lattice}}.
$$

The important abstraction is that once we notice the structural properties of $(\mathcal P(X),\subseteq)$, we can forget that the objects were sets at all. A lattice might instead consist of propositions ordered by implication, subspaces ordered by inclusion, information states ordered by information content, divisors ordered by divisibility, etc. The same lattice theorems can then apply to all of them.

That is what your lower book means when it says order/lattice theory has an analogue of $\subseteq$, but not necessarily an analogue of $x\in S$. It studies **relationships between whole objects**, rather than looking inside the objects.

### What to read in the lattice book

From the contents page you photographed, I would read these sections in this order:

1. **1. Ordered sets**
   - **Ordered sets** — p. 1
   - **Examples from mathematics, computer science and social science** — p. 3  
     This is particularly relevant because you want to see examples such as sets ordered by inclusion.
   - **Diagrams** — p. 7  
     Useful for learning Hasse diagrams and visually thinking about $\subseteq$.

2. Then go directly to **2. Lattices and complete lattices**
   - **Lattices as ordered sets** — p. 27 ← **the central section for your question**
   - **Complete lattices** — p. 33 ← **very important for semantics/static analysis**

You can initially skip the more specialized material in Chapter 1 such as duality, maximal elements, and constructing new ordered sets.

The key thing to understand on pp. 27–33 is why the power set forms a lattice:

$$
\begin{array}{ccc}
 & A\cup B &\\
 /&&\backslash\\
 A&&B\\
 \backslash&&/\\
 &A\cap B&
\end{array}
$$

and, more generally,

$$
\bigvee_i A_i=\bigcup_i A_i,
\qquad
\bigwedge_i A_i=\bigcap_i A_i.
$$

Because **arbitrary** unions and intersections exist in $\mathcal P(X)$, the power-set lattice is actually a **complete lattice**. That fact is one of the main bridges from ordinary set semantics into the order-theoretic machinery used in program analysis.

One subtle point: lattice theory is not literally a replacement for all of set theory. The trick $x\in S\iff\{x\}\subseteq S$ motivates the abstraction, but lattice theory deliberately throws away much of the internal structure of sets and retains the ordering structure that matters for the analysis.


---

> [image: sediment://file_00000000a7b4822fa3d5a0326ff7d932]
> [image: sediment://file_00000000d73c820cba84def969c86d6a]
> Explain concretizatjon without breaking my brain

<details><summary>💭 Thinking</summary>

**Explaining concretization**

I’m reading γ as a translation from abstract sign information to concrete possibilities. For example, γ(>0) means all positive integers, γ(⊤) means any integer, and γ(⊥) means none.

**Explained concretization**

</details>

Think of **concretization** as:

> “Given an abstract label, what actual values could this label represent?”

That is essentially all $\gamma$ is doing.

For this book, the abstract labels are things like

$$
>0,\quad =0,\quad <0,\quad \ge 0,\quad \top,\quad \bot
$$

instead of actual integers.

So the concretization function $\gamma$ translates **back from the abstract world into sets of concrete possibilities**:

$$
\gamma(>0)=\{1,2,3,\ldots\}
$$

$$
\gamma(=0)=\{0\}
$$

$$
\gamma(\le0)=\{\ldots,-2,-1,0\}
$$

$$
\gamma(\top)=\mathbb Z
$$

$$
\gamma(\bot)=\varnothing.
$$

So when you see

$$
\gamma(s)
$$

mentally read:

> **“all the actual integers represented by abstract sign $s$.”**

### Why do we need this?

Suppose the real program value is

$$
x=57.
$$

The abstract interpreter doesn't care that it's exactly $57$. It records

$$
x : >0.
$$

We've deliberately thrown information away.

The relationship looks like

$$
57
\quad\longrightarrow\quad
>0
$$

where the first side is **concrete** and the second is **abstract**.

Concretization goes conceptually in the other direction:

$$
>0
\quad\xrightarrow{\gamma}\quad
\{1,2,3,4,\ldots\}.
$$

Notice it **doesn't recover 57**. That's impossible because we intentionally forgot which positive integer we had.

Instead it says:

> “If all I know is $>0$, these are all the concrete values that are possible.”

That's concretization.

---

## What happens on the second part of your page?

They now apply exactly the same idea to **environments**.

A concrete environment might be

$$
\rho =
\begin{cases}
x\mapsto 7\\
y\mapsto -12
\end{cases}
$$

while an abstract environment is

$$
\hat\rho =
\begin{cases}
x\mapsto >0\\
y\mapsto <0.
\end{cases}
$$

What does that abstract environment represent?

Lots of concrete environments:

$$
(x=1,y=-1)
$$

$$
(x=500,y=-7)
$$

$$
(x=2,y=-999)
$$

and so on.

Therefore

$$
\gamma(\hat\rho)
$$

means:

> **the set of every concrete environment compatible with the signs in $\hat\rho$.**

That's what their scary-looking equation (3.26) says:

$$
\gamma(\hat\rho)
=
\{
\rho
\mid
\forall x,\;
\rho(x)\in\gamma(\hat\rho(x))
\}.
$$

Read it in English:

> Take every actual variable assignment $\rho$ such that each variable's actual integer belongs to the set described by its abstract sign.

For instance, if

$$
\hat\rho(x)=>0,
$$

then the condition is simply

$$
\rho(x)\in\gamma(>0),
$$

i.e.

$$
\rho(x)\in\{1,2,3,\ldots\}.
$$

That's it.

---

## And why does $\bot$ give the empty set?

Suppose

$$
\hat\rho(x)=\bot.
$$

But

$$
\gamma(\bot)=\varnothing.
$$

So we'd require

$$
\rho(x)\in\varnothing,
$$

which no actual value can satisfy.

Therefore there are **zero concrete environments** corresponding to that abstract environment:

$$
\gamma(\hat\rho)=\varnothing.
$$

This is why $\bot$ often means something like **impossible / no possible concrete state**.

---

## The third definition, equation (3.27)

This is the same idea **one level higher**, and I'd avoid staring at the notation initially.

You've now seen:

$$
\text{abstract sign}
\xrightarrow{\gamma}
\text{set of integers}
$$

then:

$$
\text{abstract environment}
\xrightarrow{\gamma}
\text{set of concrete environments}.
$$

Equation (3.27) just keeps lifting that same idea:

$$
\text{abstract description of program behavior}
\xrightarrow{\gamma}
\text{concrete program behaviors compatible with it}.
$$

So there aren't really three unrelated concepts on this page. It's **one concept repeated at three levels**.

### The sentence to keep in your head

Whenever you encounter

$$
\boxed{\gamma(X)}
$$

say:

$$
\boxed{\text{“What actual/concrete things could }X\text{ represent?”}}
$$

That's concretization.

And this makes the soundness statement at the top of your second photo much less mysterious:

$$
S^c[A]\subseteq\gamma(S^\pm[A]).
$$

It basically says:

> **Every result the real program can produce must be among the possibilities predicted by the abstract analysis.**

The abstract analysis is allowed to say **too much**—for example “could be any integer”—but for soundness it must never accidentally leave out a real possibility.


---

> [image: sediment://file_0000000081548230bf76ec6e8dffac97]
> Now abstraction function

<details><summary>💭 Thinking</summary>

**Explaining sign abstraction**

I’m interpreting the equation as mapping an integer set to its most precise sign category. For example, positive values become `>0`, mixed nonzero values become `≠0`, and sets spanning all signs become `⊤`.

**Explained sign abstraction**

</details>

Exactly the opposite direction from concretization.

Think of the two functions as:

$$
\boxed{\gamma = \text{“expand into concrete possibilities”}}
$$

$$
\boxed{\alpha = \text{“compress concrete possibilities into one abstract description”}}
$$

So if concretization was

$$
>0 \xrightarrow{\gamma} \{1,2,3,\ldots\},
$$

abstraction goes the other way:

$$
\{1,2,3,\ldots\}\xrightarrow{\alpha} >0.
$$

But the important wrinkle is that the abstract language is deliberately coarse. It only has labels like

$$
\bot,\;<0,\;=0,\;>0,\;\le0,\;\neq0,\;\ge0,\;\top.
$$

So $\alpha$ asks:

> **“What is the most precise sign description I have that safely describes every value in this concrete set?”**

For example,

$$
\alpha(\{3,8,100\})=>0
$$

because every number is positive.

$$
\alpha(\{-5,0,-100\})=\le0.
$$

$$
\alpha(\{-5,7\})=\neq0.
$$

And

$$
\alpha(\{-5,0,7\})=\top
$$

because your sign language has no more precise category that contains negative, zero, and positive numbers.

This is what equation (3.32) on your page is doing. It's basically a decision procedure saying:

> Is $P$ entirely negative? Use $<0$.  
> Is it exactly/entirely zero? Use $=0$.  
> Is it entirely positive? Use $>0$.  
> Is it entirely nonpositive? Use $\le0$.  
> Is it entirely nonzero? Use $\neq0$.  
> Is it entirely nonnegative? Use $\ge0$.  
> If nothing better works, use $\top$.

And

$$
\alpha(\varnothing)=\bot.
$$

### Why is it called the “best overapproximation”?

Take

$$
P=\{2,5\}.
$$

Your abstract domain can't say exactly “2 or 5.”

It could say

$$
>0,
$$

whose concretization is

$$
\gamma(>0)=\{1,2,3,4,5,\ldots\}.
$$

Clearly,

$$
\{2,5\}\subseteq\gamma(>0).
$$

So we've added fake possibilities such as $1,3,4,6,\ldots$. That's the **overapproximation**.

But $>0$ is still better than saying

$$
\top,
$$

because

$$
\gamma(\top)=\mathbb Z.
$$

Hence $>0$ is the **best** available overapproximation.

A very useful formula to keep in your head is therefore

$$
\boxed{P\subseteq\gamma(\alpha(P))}
$$

meaning:

> If I abstract $P$, then concretize the result, I may get extra possibilities, but I must not lose any original ones.

That's the whole soundness philosophy of abstract interpretation.

---

The next section, **3.17.2 Abstraction of Environment Properties**, looks worse but it's just the same operation applied variable-by-variable.

Suppose your possible concrete environments are

$$
\rho_1:
\begin{cases}
x=4\\
y=-3
\end{cases}
\qquad
\rho_2:
\begin{cases}
x=10\\
y=0.
\end{cases}
$$

For $x$, look at all values it can have:

$$
\{4,10\}.
$$

Abstract them:

$$
\alpha(\{4,10\})=>0.
$$

For $y$:

$$
\{-3,0\},
$$

so

$$
\alpha(\{-3,0\})=\le0.
$$

Thus the whole set of concrete environments gets summarized as

$$
\hat\rho:
\begin{cases}
x\mapsto >0\\
y\mapsto \le0.
\end{cases}
$$

That's equation (3.35). Despite the notation, it literally means:

$$
\boxed{
\text{for each variable, collect its possible values and summarize their signs}
}
$$

Then section 3.17.3 does the same trick **one level higher again**, now to program behaviors.

So there's a pattern:

$$
\text{integers}
\xrightarrow{\alpha}
\text{signs}
$$

$$
\text{concrete environments}
\xrightarrow{\alpha}
\text{sign environments}
$$

$$
\text{concrete semantic behaviors}
\xrightarrow{\alpha}
\text{abstract semantic behaviors}.
$$

And $\gamma$ runs conceptually in the opposite direction.

The equation at the bottom of your page,

$$
\alpha(P)\sqsubseteq \bar P
\iff
P\subseteq\gamma(\bar P),
$$

is then saying something remarkably simple:

> **$\alpha(P)$ is the best possible abstract summary of $P$.**

Any other abstract description $\bar P$ that safely represents all of $P$ must be at least as vague as the one chosen by $\alpha$.

That equation is the bridge into the Galois-connection/lattice material.


---

> Explain all the symbols that appear on the pages there are so many similar yet different ones

<details><summary>💭 Thinking</summary>

**Explaining notation**

I’m identifying the page’s main symbols: set membership, subsets, quantifiers, indexed or signed variants, bottom/top values, logical connectives, and conditional cases. I’ll distinguish notation that changes meaning from notation that merely labels related objects.

**Explained notation**

</details>

The notation is difficult mainly because the book uses **small visual decorations to tell you which “level” you are on**. Once those are separated, most of the symbols repeat the same idea.

Here is the useful master picture:

$$
\boxed{
\text{concrete world}
\;\underset{\gamma}{\overset{\alpha}{\rightleftarrows}}\;
\text{abstract world}
}
$$

- $\alpha$ = **abstraction**: concrete $\to$ abstract.
- $\gamma$ = **concretization**: abstract $\to$ concrete.
- Decorations such as dots/bars/hats distinguish whether we're talking about **values, environments, or semantic functions**.

## 1. The basic sets

### $\mathbb Z$

The integers:

$$
\mathbb Z=\{\ldots,-2,-1,0,1,2,\ldots\}.
$$

This is the **concrete value domain**.

---

### $\wp(X)$

This means the **power set** of $X$: the set of all subsets of $X$.

So

$$
P\in\wp(\mathbb Z)
$$

means:

> $P$ is a set of integers.

For example,

$$
P=\{-2,0,7\}.
$$

Be careful: the fancy $\wp$ is not an ordinary $P$. It means **powerset**.

---

### $\mathbb P^\pm$

This is the book's **abstract sign domain**.

Its elements are things like

$$
\bot^\pm,\quad <0,\quad =0,\quad >0,\quad
\le0,\quad \neq0,\quad \ge0,\quad \top^\pm.
$$

So:

$$
s\in\mathbb P^\pm
$$

means:

> $s$ is one abstract sign.

The superscript $\pm$ is just the author's notation for “the sign abstraction.” It is not arithmetic $+$ or $-$ being performed.

---

## 2. Concrete versus abstract objects

This distinction is probably causing most of the visual confusion.

### Concrete integer

$$
z\in\mathbb Z.
$$

For example,

$$
z=17.
$$

### Abstract sign

Something like

$$
s=>0.
$$

It represents many integers.

---

### Concrete environment

The book uses something like

$$
\rho:V\to\mathbb Z.
$$

Here $V$ is the set of program variables.

So $\rho$ assigns an actual integer to every variable:

$$
\rho(x)=17,\qquad
\rho(y)=-3.
$$

Think:

$$
\boxed{\rho=\text{actual program state}}
$$

---

### Abstract environment

The decorated version of $\rho$, which I'll write as $\hat\rho$, has type

$$
\hat\rho:V\to\mathbb P^\pm.
$$

Instead of assigning actual values,

$$
x\mapsto17,
$$

it assigns abstract signs:

$$
x\mapsto>0.
$$

For example,

$$
\hat\rho(x)=>0,\qquad
\hat\rho(y)=\le0.
$$

So:

$$
\boxed{
\rho(x)=17
\qquad\text{versus}\qquad
\hat\rho(x)=>0
}
$$

The decoration means **abstract version**.

---

## 3. $\alpha$ versus $\gamma$

This is the most important pair.

### $\alpha$: abstraction

$$
\alpha:\text{concrete}\to\text{abstract}.
$$

Example:

$$
\alpha(\{2,5,93\})=>0.
$$

Read:

> “Summarize these concrete possibilities using the best available abstract sign.”

---

### $\gamma$: concretization

$$
\gamma:\text{abstract}\to\text{concrete}.
$$

Example:

$$
\gamma(>0)=\{1,2,3,\ldots\}.
$$

Read:

> “What concrete possibilities does this abstract sign represent?”

So visually:

$$
\{2,5,93\}
\xrightarrow{\alpha}
>0
\xrightarrow{\gamma}
\{1,2,3,\ldots\}.
$$

The last set is bigger because abstraction lost information.

---

# 4. Why the book has several $\alpha$'s and $\gamma$'s

This is where the typography gets unpleasant.

There are essentially **three levels**.

### Level 1 — values

$$
\alpha_\pm,\qquad \gamma_\pm
$$

convert between

$$
\wp(\mathbb Z)
\quad\text{and}\quad
\mathbb P^\pm.
$$

That is:

$$
\boxed{\text{sets of integers}\leftrightarrow\text{signs}}
$$

---

### Level 2 — environments

The book adds a decoration to $\alpha_\pm,\gamma_\pm$.

These convert between

$$
\wp(V\to\mathbb Z)
$$

and

$$
V\to\mathbb P^\pm.
$$

That is:

$$
\boxed{
\text{sets of concrete program states}
\leftrightarrow
\text{abstract program states}
}
$$

It's the **same alpha/gamma idea lifted one level upward**.

---

### Level 3 — semantic properties

The book uses yet another decoration on $\alpha,\gamma$.

Now it is abstracting entire functions/semantic behaviors.

Again:

$$
\boxed{
\text{concrete behaviors}
\leftrightarrow
\text{abstract behaviors}
}
$$

So don't try to memorize three fundamentally different operations.

Think:

$$
\alpha
=
\text{summarize}
$$

$$
\gamma
=
\text{expand into possibilities}
$$

at increasingly larger scales.

---

# 5. $P$, $\bar P$, and similar symbols

On your page you have things like

$$
P\in\wp(\mathbb Z)
$$

and

$$
\bar P\in\mathbb P^\pm.
$$

These are intentionally related.

### $P$

A **concrete property**.

Usually it's literally a set.

For example:

$$
P=\{1,2,5\}.
$$

### $\bar P$

An **abstract property**.

For example:

$$
\bar P=>0.
$$

So you might have:

$$
P=\{1,2,5\}
$$

and

$$
\bar P=>0.
$$

The bar is basically screaming:

> “I am on the abstract side.”

Don't interpret the bar as subtraction, complement, or average here.

---

# 6. $S$

On these pages $S$ generally represents a **semantic function**.

Something like

$$
S:(V\to\mathbb Z)\to\mathbb Z.
$$

That complicated type simply says:

1. Give $S$ an environment $\rho$.
2. $S$ returns an integer.

So

$$
S(\rho)
$$

means:

> run/evaluate this semantic behavior in environment $\rho$.

For an expression such as

$$
x-y,
$$

an $S$ might act like

$$
S(\rho)=\rho(x)-\rho(y).
$$

---

# 7. $V$

$$
V
$$

is the set of program variables.

For example:

$$
V=\{x,y,z,\ldots\}.
$$

So

$$
x\in V
$$

means:

> $x$ is a program variable.

---

# 8. The arrow $\to$

This symbol gets used constantly for function types.

$$
A\to B
$$

means:

> functions taking elements of $A$ and producing elements of $B$.

So:

$$
V\to\mathbb Z
$$

means:

> functions from variables to integers.

That's why an environment has this type:

$$
\rho\in V\to\mathbb Z.
$$

It assigns each variable an integer.

Similarly,

$$
V\to\mathbb P^\pm
$$

means:

> functions assigning each variable an abstract sign.

---

# 9. The arrow $\mapsto$

This is slightly different from $\to$.

$$
x\mapsto f(x)
$$

describes what a function **does**.

For example:

$$
x\mapsto x^2.
$$

Compare:

$$
f:\mathbb Z\to\mathbb Z
$$

which tells you the **type**, with

$$
x\mapsto x^2
$$

which tells you the **rule**.

So on your page, something like

$$
x\in V\mapsto
\alpha_\pm(\{\rho(x)\mid\rho\in P\})
$$

means:

> define an abstract environment which, for each variable $x$, assigns the abstraction of all values $x$ can take in the environments belonging to $P$.

---

# 10. $\in$

$$
x\in X
$$

means:

> $x$ is an element of $X$.

Examples:

$$
3\in\mathbb Z
$$

and

$$
\rho\in P.
$$

---

# 11. $\subseteq$

$$
A\subseteq B
$$

means:

> every element of $A$ is also an element of $B$.

This is the ordering on the **concrete sets**.

For example:

$$
\{1,2\}\subseteq\{1,2,3\}.
$$

This is important because sound abstraction means:

$$
P\subseteq\gamma(\bar P).
$$

Read:

> every concrete possibility in $P$ is covered by the abstract description $\bar P$.

---

# 12. $\sqsubseteq$

Now we get the very similar-looking symbol:

$$
\sqsubseteq
$$

rather than

$$
\subseteq.
$$

They mean related but different things.

### Concrete side:

$$
P\subseteq Q
$$

is ordinary **set inclusion**.

### Abstract side:

$$
s_1\sqsubseteq s_2
$$

is the **abstract precision/order relation**.

For signs, for example,

$$
>0\sqsubseteq\neq0
$$

because $>0$ is more precise.

And

$$
\neq0\sqsubseteq\top.
$$

So:

$$
>0
\sqsubseteq
\neq0
\sqsubseteq
\top.
$$

Read

$$
a\sqsubseteq b
$$

roughly as:

> “$a$ contains at least as much information as $b$,”  
> or  
> “$a$ is more precise than $b$.”

This parallels subset inclusion after concretization:

$$
a\sqsubseteq b
\quad\Longrightarrow\quad
\gamma(a)\subseteq\gamma(b).
$$

That's exactly the lattice connection you were asking about earlier.

---

# 13. The little $\pm$ on $\sqsubseteq_\pm$

Your page has something like

$$
\sqsubseteq_\pm.
$$

That just says:

> the ordering specifically belonging to the **sign domain**.

It distinguishes this ordering from other abstract domains the book may introduce.

So:

$$
<0\sqsubseteq_\pm\le0
$$

means $<0$ is more precise than $\le0$ in the sign lattice.

---

# 14. $\bot$ and $\top$

These come directly from lattice theory.

### Bottom

$$
\bot
$$

means:

> no possibilities / impossible.

For signs:

$$
\gamma(\bot)=\varnothing.
$$

---

### Top

$$
\top
$$

means:

> no useful information / every possibility.

For signs:

$$
\gamma(\top)=\mathbb Z.
$$

So the information spectrum is:

$$
\boxed{
\bot
\quad\longrightarrow\quad
\text{precise information}
\quad\longrightarrow\quad
\top
}
$$

For example:

$$
\bot
\sqsubseteq
>0
\sqsubseteq
\ge0
\sqsubseteq
\top.
$$

---

# 15. $\varnothing$

$$
\varnothing
$$

is the **empty set**.

It has no elements:

$$
\varnothing=\{\}.
$$

Don't confuse:

$$
\boxed{\varnothing}
$$

with

$$
\boxed{\bot}.
$$

They live in different worlds.

- $\varnothing$ is a **concrete set**.
- $\bot$ is an **abstract element**.

They correspond through concretization:

$$
\gamma(\bot)=\varnothing.
$$

That distinction is extremely important.

---

# 16. $\top$ is not $\mathbb Z$

Similarly:

$$
\top\neq\mathbb Z.
$$

Rather,

$$
\gamma(\top)=\mathbb Z.
$$

$\top$ is the **abstract description** “could be any integer.”

$\mathbb Z$ is the actual concrete set of all integers.

---

# 17. Curly braces $\{\cdots\}$

These make sets.

Simple example:

$$
\{1,2,3\}.
$$

But the book frequently uses **set-builder notation**:

$$
\{z\in\mathbb Z\mid z>0\}.
$$

Read:

> the set of integers $z$ such that $z>0$.

It means

$$
\{1,2,3,\ldots\}.
$$

---

# 18. The vertical bar $\mid$

Inside a set,

$$
\{x\mid\text{condition}\},
$$

the vertical bar means:

> **such that**.

Example:

$$
\{z\in\mathbb Z\mid z<0\}
$$

means:

> all integers $z$ such that $z<0$.

Your page also has something like

$$
\{\rho(x)\mid\rho\in P\}.
$$

Read:

> all values of $x$ obtained from environments $\rho$ in $P$.

---

# 19. $\forall$

$$
\forall
$$

means **for all**.

For example:

$$
\forall x\in V.
$$

means:

> for every variable $x$.

---

# 20. $\exists$

$$
\exists
$$

means **there exists**.

For example:

$$
\exists x\in V.
$$

means:

> there is at least one variable $x$.

---

# 21. $\wedge$

$$
A\wedge B
$$

means logical **and**.

For example:

$$
S\in P\wedge\rho\in\gamma(\hat\rho)
$$

means both:

- $S\in P$, and
- $\rho\in\gamma(\hat\rho)$.

---

# 22. $\Longleftrightarrow$ or $\iff$

This means:

> **if and only if**.

On your page, the central result is essentially

$$
\boxed{
\alpha_\pm(P)\sqsubseteq_\pm\bar P
\iff
P\subseteq\gamma_\pm(\bar P)
}
$$

This is worth decoding slowly.

Left:

$$
\alpha_\pm(P)\sqsubseteq_\pm\bar P
$$

means:

> the best abstraction of $P$ is at least as precise as $\bar P$.

Right:

$$
P\subseteq\gamma_\pm(\bar P)
$$

means:

> $\bar P$ safely covers every concrete element of $P$.

And the theorem says those two statements are equivalent.

That is the characteristic **Galois connection** relationship.

---

# 23. $\triangleq$ / $\overset{\mathrm{def}}{=}$

Your book uses a special equals sign such as

$$
\triangleq
$$

or similar.

It means:

> **is defined to be**.

So

$$
\gamma_\pm(>0)\triangleq
\{z\in\mathbb Z\mid z>0\}
$$

is not proving an equality. It is **defining** $\gamma_\pm(>0)$.

Ordinary

$$
=
$$

means equality.

---

# 24. The question marks in equation (3.32)

The strange construction on the top of your current page is basically the book's conditional/case notation.

Conceptually it says:

$$
\alpha_\pm(P)=
\begin{cases}
\bot & P=\varnothing\\
<0 & P\subseteq\{z\mid z<0\}\\
=0 & P\subseteq\{0\}\\
>0 & P\subseteq\{z\mid z>0\}\\
\le0 & P\subseteq\{z\mid z\le0\}\\
\neq0 & P\subseteq\{z\mid z\neq0\}\\
\ge0 & P\subseteq\{z\mid z\ge0\}\\
\top & \text{otherwise.}
\end{cases}
$$

So don't attach deep mathematical significance to the `?`. It's being used to write a sequence of conditional choices.

---

# 25. The most useful “translation dictionary”

When reading these pages, mentally substitute:

$$
\alpha(X)
\quad\rightsquigarrow\quad
\text{“best abstract summary of $X$”}
$$

$$
\gamma(X)
\quad\rightsquigarrow\quad
\text{“all concrete things $X$ represents”}
$$

$$
\rho
\quad\rightsquigarrow\quad
\text{“actual variable assignment”}
$$

$$
\hat\rho
\quad\rightsquigarrow\quad
\text{“sign assignment”}
$$

$$
P
\quad\rightsquigarrow\quad
\text{“set of concrete possibilities”}
$$

$$
\bar P
\quad\rightsquigarrow\quad
\text{“abstract description”}
$$

$$
\subseteq
\quad\rightsquigarrow\quad
\text{“included as concrete sets”}
$$

$$
\sqsubseteq
\quad\rightsquigarrow\quad
\text{“more precise than, abstractly”}
$$

$$
\bot
\quad\rightsquigarrow\quad
\text{“impossible”}
$$

$$
\top
\quad\rightsquigarrow\quad
\text{“anything”}.
$$

The big conceptual trick is that **$\varnothing$ and $\bot$ say nearly the same thing at different levels, just as $\mathbb Z$ and $\top$ say nearly the same thing at different levels**:

$$
\boxed{
\varnothing
\;\xleftrightarrow[\alpha]{\gamma}\;
\bot
}
$$

and

$$
\boxed{
\mathbb Z
\;\xleftrightarrow[\alpha]{\gamma}\;
\top.
}
$$

Once you keep “concrete notation” and “abstract notation” in separate mental boxes, these pages become much more readable.


---

> [image: sediment://file_000000002ed0822fb05172243fa615de]
> [image: sediment://file_0000000096c081fb84ffcf85816dc820]
> Do the same for whatever new symbols are on here

```unknown
from PIL import Image
img=Image.open('/mnt/data/IMG_8962D262-58F9-4F6B-A76C-C4DC5DEE0BFB.jpeg')
img.size

```

<details><summary>💭 Thinking</summary>

**Identified mathematical symbols and explained typed function Boolean notation**

**Interpreting the notation**

I’m clarifying the decorated symbols as abstract sign environments, then unpacking the semantic brackets, function type, abstract bottom, and conditional notation. I’ll distinguish notation choices from their mathematical meaning.

**Interpreted the notation**

</details>

```unknown
crop=img2.crop((285,710,975,1030))
plt.figure(figsize=(15,7)); plt.imshow(crop); plt.axis('off');

```

<details><summary>💭 Thinking</summary>

**Explained abstract sign semantics and inspected conditional syntax**

</details>

Yes. These two pages introduce another batch of notation, and several symbols are overloaded. I’ll focus on the genuinely new ones and the places where an old symbol is being used differently.

The most important distinction on these pages is:

$$
\boxed{\mathcal S^c = \text{concrete/collecting semantics}}
\qquad\text{vs}\qquad
\boxed{\mathcal S^\pm = \text{sign/abstract semantics}}
$$

## 1. The double brackets $\llbracket A\rrbracket$

You keep seeing things like

$$
\mathcal S^c\llbracket A\rrbracket
$$

and

$$
\mathcal S^\pm\llbracket A\rrbracket.
$$

The double brackets mean roughly:

> **“the meaning/semantics of the syntactic expression $A$”**

They are deliberately different from ordinary parentheses.

For example,

$$
\mathcal S^\pm\llbracket x-y\rrbracket
$$

means:

> the abstract sign semantics of the syntax `x - y`.

Mentally you can read

$$
\mathcal S^\pm\llbracket A\rrbracket
$$

as

> **“analyze expression $A$ using signs.”**

---

# 2. Superscript $c$ versus superscript $\pm$

On page 24:

$$
\mathcal S^c
$$

The $c$ means the **concrete/collecting semantics** being developed there.

On page 25:

$$
\mathcal S^\pm
$$

means the **sign abstract semantics**.

The $\pm$ is a label telling you:

> “we're working in the sign abstraction.”

So compare:

$$
\mathcal S^c\llbracket A\rrbracket
$$

concrete information,

versus

$$
\mathcal S^\pm\llbracket A\rrbracket
$$

sign information.

---

# 3. The strange decorated $\rho$

The book writes a tiny sign decoration over $\rho$. I'll render it more legibly as

$$
\rho^\pm.
$$

Ordinary

$$
\rho
$$

is a **concrete environment**:

$$
\rho:V\to\mathbb Z.
$$

For example,

$$
\rho(x)=17,\qquad \rho(y)=-4.
$$

But

$$
\rho^\pm
$$

is a **sign environment**:

$$
\rho^\pm:V\to\mathbb P^\pm.
$$

For example,

$$
\rho^\pm(x)=>0,\qquad
\rho^\pm(y)=<0.
$$

So whenever you see the decorated $\rho$, think:

$$
\boxed{\rho^\pm=\text{abstract/sign version of a program state}}
$$

---

# 4. Function application: $\rho(x)$, $f(\rho)$

Very basic, but it occurs everywhere here.

If

$$
\rho:V\to\mathbb Z,
$$

then

$$
\rho(x)
$$

means:

> apply the environment function $\rho$ to variable $x$.

So if $x$ currently contains 12,

$$
\rho(x)=12.
$$

Similarly,

$$
f(\rho)
$$

means:

> run semantic function $f$ on environment $\rho$.

---

# 5. This weird construction

At the top you have something like

$$
\{\rho\in(V\to\mathbb Z)\mapsto 1\}.
$$

The important new symbol is

$$
\mapsto.
$$

It means **“maps to.”**

So

$$
\rho\mapsto1
$$

describes the function:

> whatever environment $\rho$ you give me, return $1$.

Likewise

$$
\rho\mapsto\rho(x)
$$

means:

> take an environment $\rho$, and return whatever value $x$ has in that environment.

Thus

$$
\mathcal S^c\llbracket x\rrbracket
=
\{\rho\mapsto\rho(x)\}
$$

is saying that the semantics of variable $x$ is the function that looks up $x$'s value.

---

# 6. $f_1$ and $f_2$

In the subtraction equation you see

$$
f_1,\quad f_2.
$$

These are just semantic functions chosen from the meanings of the two subexpressions.

For

$$
A_1-A_2,
$$

you get one semantic function for $A_1$,

$$
f_1,
$$

and one for $A_2$,

$$
f_2.
$$

Then construct

$$
\rho\mapsto f_1(\rho)-f_2(\rho).
$$

In English:

> evaluate the first child, evaluate the second child, then subtract the results.

This is just the mathematical version of recursively evaluating an AST.

---

# 7. $A_1,A_2$ versus $B_1,B_2$

These letters indicate different kinds of syntax.

Typically:

$$
A_1,A_2
$$

are **arithmetic expressions**, while

$$
B_1,B_2
$$

are **Boolean expressions**.

So:

$$
A_1-A_2
$$

is arithmetic.

But

$$
B_1\ \text{nand}\ B_2
$$

is Boolean.

The subscripts $1,2$ just distinguish the left and right children.

---

# 8. $\uparrow$ in the NAND equation

On page 24 there is an up-arrow operation:

$$
f_1(\rho)\uparrow f_2(\rho).
$$

Here

$$
\uparrow
$$

is **Boolean NAND**.

That is,

$$
a\uparrow b
=
\neg(a\land b).
$$

Truth table:

$$
\begin{array}{c|c|c}
a&b&a\uparrow b\\
\hline
\mathrm{tt}&\mathrm{tt}&\mathrm{ff}\\
\mathrm{tt}&\mathrm{ff}&\mathrm{tt}\\
\mathrm{ff}&\mathrm{tt}&\mathrm{tt}\\
\mathrm{ff}&\mathrm{ff}&\mathrm{tt}
\end{array}
$$

So don't interpret this $\uparrow$ as an order-theory symbol here. It's simply the Boolean NAND operation.

---

# 9. $\mathrm{tt}$ and $\mathrm{ff}$

The book writes

$$
\mathrm{tt}
$$

for **true**, and

$$
\mathrm{ff}
$$

for **false**.

So:

$$
b=\mathrm{tt}
$$

means $b$ is true.

This notation is common in programming-language semantics because they want to distinguish Boolean *values* from English words.

---

# 10. $\mathbb P^\pm\times\mathbb P^\pm\to\mathbb P^\pm$

This line is important:

$$
-_\pm\in
\mathbb P^\pm\times\mathbb P^\pm\to\mathbb P^\pm.
$$

Break it into pieces.

You've already seen

$$
\mathbb P^\pm
$$

as the set of sign properties.

The new symbol is

$$
\times.
$$

Here it means **Cartesian product**, not numerical multiplication.

So

$$
\mathbb P^\pm\times\mathbb P^\pm
$$

means:

> pairs of signs.

Examples:

$$
(>0,<0),\qquad
(\ge0,=0).
$$

Thus

$$
\mathbb P^\pm\times\mathbb P^\pm
\to
\mathbb P^\pm
$$

means:

> take **two signs** as input and return **one sign**.

Schematically:

$$
(s_1,s_2)\longmapsto s_3.
$$

That's exactly what abstract subtraction needs.

---

# 11. $-_\pm$

This is **not ordinary integer subtraction**.

The tiny $\pm$ says:

> abstract subtraction in the sign domain.

So

$$
s_1-_\pm s_2
$$

means:

> if the first operand has abstract sign $s_1$ and the second has abstract sign $s_2$, what sign can their difference have?

For example:

$$
>0-_\pm <0 =>0.
$$

Why? Positive minus negative is always positive.

But

$$
>0-_\pm >0=\top_\pm
$$

because, for example,

$$
5-2>0,
$$

$$
5-5=0,
$$

and

$$
2-5<0.
$$

So just knowing “positive minus positive” doesn't determine the sign.

---

# 12. How to read the subtraction table

The table has

$$
s_1
$$

on the left and

$$
s_2
$$

along the top.

Find the row for $s_1$, then the column for $s_2$.

The cell contains

$$
s_1-_\pm s_2.
$$

For example, row

$$
>0
$$

and column

$$
<0
$$

gives

$$
>0.
$$

It is literally a multiplication table, except the operation is **abstract sign subtraction**.

---

# 13. Standalone $>0$ is not a comparison here

This is a subtle source of confusion.

Normally

$$
x>0
$$

is a proposition asking whether $x$ is positive.

But when the book writes simply

$$
>0
$$

inside $\mathbb P^\pm$, it is being used as the **name of an abstract value**.

Think of it as though they had named it

$$
\texttt{POS}.
$$

Similarly,

$$
<0\approx\texttt{NEG}
$$

$$
=0\approx\texttt{ZERO}
$$

$$
\ge0\approx\texttt{NONNEG}
$$

etc.

That's why something like

$$
\rho^\pm(x)=>0
$$

is sensible. It means:

> the abstract sign stored for $x$ is `POS`.

---

# 14. $D_\pm$

On page 24 the book calls

$$
D_\pm
$$

the **sign abstract domain**.

Essentially this is the abstract mathematical structure containing the sign values and their relationships/operations.

For your current purposes, read:

$$
\boxed{D_\pm=\text{the whole sign-analysis domain}}
$$

while

$$
\mathbb P^\pm
$$

is the collection of its sign properties/elements.

---

# 15. The big type of $\mathcal S^\pm$

Page 25 says roughly

$$
\mathcal S^\pm\llbracket A\rrbracket
\in
(V\to\mathbb P^\pm)\to\mathbb P^\pm.
$$

This looks terrible but is actually very useful.

Start inside:

$$
V\to\mathbb P^\pm.
$$

That's a sign environment:

$$
x\mapsto >0,\qquad y\mapsto\le0,\ldots
$$

Then:

$$
(V\to\mathbb P^\pm)\to\mathbb P^\pm
$$

means:

> take one of those sign environments and produce one sign.

So the entire type says:

$$
\boxed{
\text{sign environment}
\longrightarrow
\text{sign of expression}
}
$$

For example,

$$
\begin{cases}
x\mapsto>0\\
y\mapsto\le0
\end{cases}
\quad
\xrightarrow{\mathcal S^\pm\llbracket x-y\rrbracket}
\quad
>0.
$$

That is literally what static sign analysis is doing.

---

# 16. The subscript environment on the semantics

You see something like

$$
\mathcal S^\pm\llbracket A\rrbracket_{\rho^\pm}
$$

or the environment immediately after the brackets.

Read it as:

> evaluate the abstract semantics of $A$ **under sign environment $\rho^\pm$**.

So:

$$
\mathcal S^\pm\llbracket x\rrbracket_{\rho^\pm}
=
\rho^\pm(x).
$$

That says:

> the sign of variable $x$ is whatever sign the environment records for $x$.

Very straightforward beneath the typography.

---

# 17. The newly defined $\downarrow^\pm$

This is probably the weirdest new symbol:

$$
\downarrow^\pm[\rho^\pm]s.
$$

The book has simply **invented a function and named it with a down-arrow**.

It is enforcing their rule that $\bot_\pm$ is **strict**.

Conceptually:

$$
\downarrow^\pm[\rho^\pm]s
=
\begin{cases}
\bot_\pm,
&
\text{if some variable has sign }\bot_\pm,\\[4pt]
s,
&
\text{otherwise}.
\end{cases}
$$

So if

$$
\rho^\pm(x)=>0,\qquad \rho^\pm(y)=<0,
$$

then

$$
\downarrow^\pm[\rho^\pm](>0)=>0.
$$

But if

$$
\rho^\pm(y)=\bot_\pm,
$$

then

$$
\downarrow^\pm[\rho^\pm](>0)=\bot_\pm.
$$

Don't give the down-arrow any deeper lattice interpretation **in this particular equation**. It's the author's chosen name for this “strictness check.”

---

# 18. $\exists y\in V$

Inside that definition:

$$
\exists y\in V.
$$

means:

> there exists at least one variable $y$ in $V$.

So

$$
\exists y\in V.\;\rho^\pm(y)=\bot_\pm
$$

means:

> at least one variable has abstract value bottom.

The dot after the quantified variable,

$$
\exists y\in V.\;P(y),
$$

just separates the variables being quantified from the condition.

Read it as:

> “there exists a $y\in V$ **such that** $P(y)$.”

---

# 19. The weird `?` conditional notation

The book explains this immediately underneath equation (3.23).

In simplified form,

$$
(b\ ?\ x\ \text{§}\ z)
$$

means approximately:

$$
\text{if }b\text{ then }x\text{ else }z.
$$

So the definition of $\downarrow^\pm$ is saying:

$$
\left(
\exists y\in V.\rho^\pm(y)=\bot_\pm
\quad ?\quad
\bot_\pm
\quad\text{else}\quad
s
\right).
$$

You don't need to memorize their peculiar punctuation. Translate it immediately to ordinary pseudocode:

```text
if any variable has value bottom:
    return bottom
else:
    return s
```

They also allow several alternatives:

$$
(b_1?x\mid b_2?y\ \text{else }z).
$$

Meaning:

```text
if b1:
    x
else if b2:
    y
else:
    z
```

Here the vertical bar $\mid$ separates alternatives.

This is important because **the same vertical bar means “such that” in set-builder notation**. Context determines which meaning it has.

---

# 20. Why equation (3.23) now has $\downarrow^\pm$

Originally they had:

$$
\mathcal S^\pm\llbracket1\rrbracket_{\rho^\pm}
=>0.
$$

But now they refine it to:

$$
\mathcal S^\pm\llbracket1\rrbracket_{\rho^\pm}
=
\downarrow^\pm[\rho^\pm](>0).
$$

Why?

Normally the literal $1$ has sign $>0$.

But their semantics says that if the environment contains some $\bot_\pm$, the expression is never evaluated at all. So the result must be

$$
\bot_\pm.
$$

The $\downarrow^\pm$ wrapper enforces this convention.

---

## The entire page translated into programmer notation

The abstract environment is essentially:

```text
SignEnv = Variable -> Sign
```

where

```text
Sign = {
    BOTTOM,
    NEG,
    ZERO,
    POS,
    NONPOS,
    NONZERO,
    NONNEG,
    TOP
}
```

Abstract subtraction is:

```text
abstract_subtract : Sign × Sign -> Sign
```

and the semantic evaluator has type:

```text
analyze : Expression × SignEnv -> Sign
```

with rules approximately:

```text
analyze(1, env) =
    strict(env, POS)

analyze(x, env) =
    strict(env, env[x])

analyze(A1 - A2, env) =
    abstract_subtract(
        analyze(A1, env),
        analyze(A2, env)
    )
```

So underneath all the mathematical decorations, **page 25 is basically defining a recursive abstract interpreter over an expression AST**. That is the main idea to keep fixed while reading the symbols.


---

> What about alpha dot and chi dot and alpha dot dot and chi dot dot

```unknown
bash -lc ls -l /mnt/data | sed -n '1,40p'
```

<details><summary>💭 Thinking</summary>

**Listed mounted data files**

</details>

```unknown
from PIL import Image
img=Image.open('/mnt/data/IMG_6484FC3C-900C-415B-BE84-FABE85130EFC.jpeg')
img.size

```

<details><summary>💭 Thinking</summary>

**Inspected and saved a cropped image region**

**Reading the notation**

I’m identifying the symbol as gamma, not chi. The dots appear to mark abstraction levels rather than derivatives: no dot, one dot, and two dots correspond to progressively higher-order domains and codomains.

**Read the notation**

</details>

Those dots are **not calculus derivatives**. They are just the author's way of saying “same abstraction/concretization idea, but lifted to a higher kind of object.”

Also, the symbol you're calling “chi” is **gamma**, $\gamma$.

Think of three floors:

$$
\boxed{\text{integers}}
\quad\to\quad
\boxed{\text{environments}}
\quad\to\quad
\boxed{\text{semantic functions}}
$$

At each floor there is an $\alpha$ going concrete $\to$ abstract and a $\gamma$ going abstract $\to$ concrete.

### No dot: values

$$
\alpha_\pm : \wp(\mathbb Z)\to \mathbb P^\pm
$$

takes a **set of concrete integers** and summarizes it by a sign.

Example:

$$
\alpha_\pm(\{2,5,100\})=>0.
$$

The reverse direction is

$$
\gamma_\pm:\mathbb P^\pm\to\wp(\mathbb Z).
$$

Example:

$$
\gamma_\pm(>0)=\{1,2,3,\ldots\}.
$$

So:

$$
\boxed{\alpha_\pm,\gamma_\pm
\text{ deal with integer values}}
$$

---

### One dot: environments

Now instead of describing one integer, we describe an entire assignment of variables.

A concrete environment looks like

$$
\rho:
\begin{cases}
x\mapsto 7\\
y\mapsto-4
\end{cases}
$$

and an abstract sign environment looks like

$$
\dot\rho:
\begin{cases}
x\mapsto>0\\
y\mapsto<0.
\end{cases}
$$

The book uses **one dot** on alpha/gamma for this level:

$$
\dot\alpha_\pm
$$

and

$$
\dot\gamma_\pm.
$$

So

$$
\boxed{\dot\alpha_\pm
=\text{abstract a set of concrete environments}}
$$

and

$$
\boxed{\dot\gamma_\pm
=\text{concretize a sign environment}}
$$

For example, suppose the concrete possibilities are

$$
(x=2,y=-3)
$$

and

$$
(x=10,y=-8).
$$

Then roughly

$$
\dot\alpha_\pm(\{\rho_1,\rho_2\})
=
\begin{cases}
x\mapsto>0\\
y\mapsto<0.
\end{cases}
$$

Going back,

$$
\dot\gamma_\pm
\left(
\begin{cases}
x\mapsto>0\\
y\mapsto<0
\end{cases}
\right)
$$

is the enormous set

$$
\{
(x=1,y=-1),
(x=2,y=-100),
(x=500,y=-3),
\ldots
\}.
$$

So:

$$
\boxed{
\dot\alpha_\pm,\dot\gamma_\pm
\text{ deal with environments}
}
$$

---

### Two dots: semantic functions / program behaviors

Then the book goes up **another level**.

Instead of describing individual states, it describes whole functions that take states and produce values:

$$
S:(V\to\mathbb Z)\to\mathbb Z.
$$

An $S$ might mean, for example,

$$
S(\rho)=\rho(x)-\rho(y).
$$

Now the book uses

$$
\ddot\alpha_\pm
$$

and

$$
\ddot\gamma_\pm.
$$

So:

$$
\boxed{
\ddot\alpha_\pm
=
\text{abstract concrete program behaviors}
}
$$

and

$$
\boxed{
\ddot\gamma_\pm
=
\text{turn an abstract program behavior into all concrete behaviors it allows}
}
$$

The two-dot level is why you see the soundness equation

$$
\mathcal S^c\llbracket A\rrbracket
\subseteq
\ddot\gamma_\pm
\bigl(
\mathcal S^\pm\llbracket A\rrbracket
\bigr).
$$

Read that as:

> The actual concrete behavior of $A$ must be included among the behaviors allowed by its abstract sign semantics.

## The whole notation in one picture

$$
\begin{array}{c|c|c}
\text{level} & \text{abstraction} & \text{concretization}\\
\hline
\text{integer values}
&
\alpha_\pm
&
\gamma_\pm
\\[3pt]
\text{environments}
&
\dot\alpha_\pm
&
\dot\gamma_\pm
\\[3pt]
\text{semantic/program behaviors}
&
\ddot\alpha_\pm
&
\ddot\gamma_\pm
\end{array}
$$

So don't think of these as six different ideas. There are only **two ideas**:

$$
\boxed{\alpha=\text{compress concrete information}}
$$

$$
\boxed{\gamma=\text{expand an abstract description into its concrete possibilities}}
$$

and the author uses dots to say **what level you're applying those ideas to**:

$$
\text{no dot}=\text{values},
\qquad
\text{one dot}=\text{states},
\qquad
\text{two dots}=\text{behaviors}.
$$

That convention is specific notation chosen by this book; the dots themselves do not have a universal abstract-interpretation meaning.


---

> Give type signatures of the 3 functions (mathematical notation)

For the three abstraction/concretization levels:

$$
\boxed{
\alpha_{\pm}:\wp(\mathbb Z)\to\mathbb P^{\pm}
}
\qquad
\boxed{
\gamma_{\pm}:\mathbb P^{\pm}\to\wp(\mathbb Z)
}
$$

$$
\boxed{
\dot{\alpha}_{\pm}:\wp(V\to\mathbb Z)\to(V\to\mathbb P^{\pm})
}
\qquad
\boxed{
\dot{\gamma}_{\pm}:(V\to\mathbb P^{\pm})\to\wp(V\to\mathbb Z)
}
$$

$$
\boxed{
\ddot{\alpha}_{\pm}:
\wp\big((V\to\mathbb Z)\to\mathbb Z\big)
\to
\big((V\to\mathbb P^{\pm})\to\mathbb P^{\pm}\big)
}
$$

$$
\boxed{
\ddot{\gamma}_{\pm}:
\big((V\to\mathbb P^{\pm})\to\mathbb P^{\pm}\big)
\to
\wp\big((V\to\mathbb Z)\to\mathbb Z\big)
}
$$

In compact form:

$$
\begin{array}{c|c|c}
&\alpha&\gamma\\ \hline
\text{values}
&\wp(\mathbb Z)\to\mathbb P^\pm
&\mathbb P^\pm\to\wp(\mathbb Z)\\[2mm]
\text{environments}
&\wp(V\to\mathbb Z)\to(V\to\mathbb P^\pm)
&(V\to\mathbb P^\pm)\to\wp(V\to\mathbb Z)\\[2mm]
\text{semantics}
&\wp((V\to\mathbb Z)\to\mathbb Z)\to((V\to\mathbb P^\pm)\to\mathbb P^\pm)
&((V\to\mathbb P^\pm)\to\mathbb P^\pm)\to\wp((V\to\mathbb Z)\to\mathbb Z)
\end{array}
$$

The pattern is: **0 dots = values, 1 dot = environments, 2 dots = functions from environments to values.**


---

> Abadi lamport refinement mappings

```json
{"system1_search_query":[{"q":"Abadi Lamport refinement mappings paper pdf refinement mappings specification mappings","domains":["lamport.azurewebsites.net"]},{"q":"Abadi Lamport existence of refinement mappings theorem refinement mappings pdf","domains":["microsoft.com"]}],"response_length":"medium"}
```

<details><summary>💭 Thinking</summary>

**Searched 16 websites**

</details>

Abadi–Lamport **refinement mappings** fit very naturally with the abstraction ideas you’ve just been reading.

Suppose you have two specifications:

$$
S_L=\text{lower-level / implementation specification}
$$

and

$$
S_H=\text{higher-level / abstract specification}.
$$

A **refinement mapping** is essentially a state-abstraction function

$$
\boxed{
f:\mathrm{State}_L\to\mathrm{State}_H
}
$$

that tells you:

> “Given this detailed implementation state, which abstract specification state does it represent?”

Abadi and Lamport define refinement mappings precisely as mappings from the lower-level specification's state space to the higher-level specification's state space, intended to map implementation steps and behaviors to permitted specification steps and behaviors. citeturn802532view0

For a simple example, imagine the abstract specification of a queue stores

$$
q=[a,b,c].
$$

The implementation might instead use

$$
\text{array},\quad \text{head},\quad \text{tail},\quad \text{size}.
$$

A refinement mapping could be

$$
f(\text{array},\text{head},\text{tail},\text{size})
=
\text{logical sequence represented by that array}.
$$

Thus:

$$
\underbrace{
(\text{array}=[c,\_,a,b],\,
\text{head}=2,\,
\text{size}=3)
}_{\text{low-level state}}
\quad\xrightarrow{f}\quad
\underbrace{[a,b,c]}_{\text{high-level state}}.
$$

This queue-style example is essentially the one Abadi and Lamport use to motivate the idea. citeturn802532view0

### What does the mapping prove?

Suppose the implementation makes a step

$$
l\longrightarrow l'.
$$

Apply the refinement mapping:

$$
\begin{array}{ccc}
l&\longrightarrow&l'\\
\downarrow f&&\downarrow f\\
h&\longrightarrow&h'
\end{array}
$$

where

$$
h=f(l),\qquad h'=f(l').
$$

You want the bottom transition to be a legal transition of the abstract specification (allowing the appropriate notion of stuttering). Then an entire implementation execution

$$
l_0\to l_1\to l_2\to\cdots
$$

gets transformed pointwise into

$$
f(l_0)\to f(l_1)\to f(l_2)\to\cdots,
$$

which should be a behavior permitted by the high-level specification. This changes a difficult proof about arbitrary executions into a much more local proof about states and transitions. citeturn802532view0

So the intended conclusion is

$$
\boxed{\text{every behavior of }S_L
\text{ corresponds to an allowed behavior of }S_H.}
$$

That is what it means for the lower-level specification to implement the higher-level one in their framework. citeturn802532view0

### Connection to the $\alpha$ you've just learned

Conceptually, they are extremely similar:

$$
\alpha:
\text{concrete information}
\to
\text{abstract information}
$$

versus

$$
f:
\text{implementation state}
\to
\text{specification state}.
$$

You can think:

$$
\boxed{
\text{refinement mapping}
\approx
\text{abstraction function for system states}
}
$$

but they aren't technically identical notions. Abstract interpretation uses $\alpha,\gamma$ to relate **domains of properties/information**, usually with an order or Galois connection. A refinement mapping directly relates the **states of two transition-system specifications** and must respect their behavior.

There is also an important direction issue:

$$
\boxed{\text{detailed}\xrightarrow{f}\text{abstract}}
$$

even though we say the detailed system **refines** the abstract one.

### Why Abadi–Lamport is particularly famous

Sometimes the implementation simply **doesn't contain enough state information** to construct such an $f$.

For example, the abstract specification might remember something about the past that the implementation has forgotten. Then no function

$$
f(\text{current implementation state})
$$

can reconstruct that abstract state.

Their key technique is to add **auxiliary variables** without changing the externally observable behavior. In particular:

$$
\text{history variable}
$$

stores relevant information from the past, whereas

$$
\text{prophecy variable}
$$

can represent information about a nondeterministic choice that will be resolved in the future. Abadi and Lamport show, under their stated conditions, that adding suitable auxiliary variables can guarantee the existence of a refinement mapping. citeturn802532view0

So you can picture their whole method as

$$
\text{implementation state}
$$

$$
\downarrow
$$

$$
\text{implementation state + auxiliary information}
$$

$$
\downarrow f
$$

$$
\text{abstract specification state}.
$$

The especially nice connection to what you're reading now is:

$$
\boxed{
\begin{array}{c}
\text{Abstract interpretation}\\
\text{concrete values/states}\xrightarrow{\alpha}\text{abstract values/states}
\end{array}}
$$

and

$$
\boxed{
\begin{array}{c}
\text{Refinement mappings}\\
\text{implementation states}\xrightarrow{f}\text{specification states}.
\end{array}}
$$

So if $\alpha$ already makes sense to you, a refinement mapping is not a completely foreign concept: it is another way of saying **“forget implementation detail while preserving everything that matters at the higher level.”** citeturn802532view0turn802532view1

