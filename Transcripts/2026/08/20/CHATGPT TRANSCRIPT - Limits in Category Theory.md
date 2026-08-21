# Limits in Category Theory

- URL: https://chatgpt.com/c/6a7f0e7c-8b0c-83ea-a0e6-b190fd0c8b07
- Created: 2026-08-14T12:48:25.940Z

---

> Are cones and limits defined on diagrams always , so that means there are no limits “for a category” per se?

Yes. In ordinary category theory, a **limit is always the limit of a diagram**.

Given a diagram
$$
F:J\to C,
$$
a cone to $F$ consists of an object $L\in C$ together with compatible maps
$$
L\to F(j)
$$
for all $j\in J$. A **limit of $F$** is a terminal cone to that diagram.

So there is not normally an object called **“the limit of the category $C$”** just from knowing $C$. You need a diagram in $C$.

What people do say is:

- “$C$ **has all limits**” = every small diagram $F:J\to C$ has a limit.
- “$C$ **has finite limits**” = every diagram whose indexing category $J$ is finite has a limit.
- “Take the limit over $J$” = shorthand for
  $$
  \lim_{j\in J}F(j),
  $$
  where the diagram $F:J\to C$ is understood.

So it helps to keep the three roles distinct:
$$
\boxed{J \xrightarrow{F} C}
$$

Here $J$ tells you the **shape** of the diagram, $C$ is the category **where the diagram lives**, and
$$
\lim F
$$
is an object **of $C$**.

For example, a product $X\times Y$ isn't “a limit of $C$.” It is the limit of the discrete diagram
$$
\{1,2\}\to C,\qquad 1\mapsto X,\;2\mapsto Y.
$$

Similarly, a terminal object is the limit of the **empty diagram**
$$
\varnothing\to C.
$$

There is one subtlety: a category can itself be an **object in the category $\mathbf{Cat}$**. So you can have a *diagram of categories*
$$
F:J\to \mathbf{Cat}
$$
and take its limit in $\mathbf{Cat}$. But again, that is still the limit of a **diagram**, not an intrinsic “limit of a category.”

So your intuition is right:

$$
\boxed{\text{limits belong to diagrams; categories are said to possess/allow certain limits.}}
$$


---

> Define diagram

A **diagram in a category $C$** is simply a **functor**
$$
F:J\to C,
$$
where $J$ is called the **indexing category** or **shape** of the diagram.

The idea is that $J$ specifies the pattern of objects and arrows, and $F$ realizes that pattern inside $C$.

For every object $j\in J$, the functor gives an object
$$
F(j)\in C,
$$
and for every morphism
$$
\alpha:j\to k
$$
in $J$, it gives a morphism
$$
F(\alpha):F(j)\to F(k)
$$
in $C$, preserving identities and composition.

For example, if $J$ has the shape
$$
1\longrightarrow 2,
$$
then a diagram $F:J\to C$ is just a morphism in $C$:
$$
X\longrightarrow Y.
$$

If $J$ has the shape
$$
1\longrightarrow 3\longleftarrow 2,
$$
then a diagram in $C$ has the form
$$
X\longrightarrow Z\longleftarrow Y.
$$

So a diagram is not fundamentally a picture. **The picture is a visualization of a functor.**

In short:
$$
\boxed{\text{diagram in }C=\text{functor }F:J\to C.}
$$

And this is why a limit is written
$$
\lim F:
$$
it is the limit of the particular diagram $F$, whose shape is $J$.


---

> [image: sediment://file_00000000ca4881fba4997eb823e181b5]
> So the goldblatt is kind of imprecise, right? What are different definition diagram, can it be “a subset of C that is self consistent?” Or is it always defined in terms of a functor?

<details><summary>💭 Thinking</summary>

**Clarifying diagram definitions**

I’m distinguishing several notions: a diagram may be a graph labeled in $C$, a functor from a shape category, or a presented commutative diagram. It needn’t be a subcategory; functoriality imposes coherent compositions and identities.

**Clarified diagram definitions**

**Refining the distinction**

I’m treating Goldblatt’s wording as informal rather than incorrect. A collection of labeled objects and arrows describes a graph-shaped picture; a functor formalizes it, preserving identities and composites while allowing repeated object occurrences and explicit commuting relations.

**Refined the distinction**

</details>

Goldblatt’s wording is **informal rather than fundamentally wrong**, but the functor definition is the cleaner modern definition.

What he writes—

> a collection of objects $d_i$ together with some arrows $g:d_i\to d_j$

—is basically describing the **picture/data you draw**. But if taken literally as “just a subset of the objects and arrows of $C$,” it loses information.

The standard definition is

$$
\boxed{\text{a diagram in }C\text{ is a functor }D:J\to C.}
$$

Here $J$ carries the **shape** of the diagram.

### Why not just “a self-consistent subset of $C$”?

Because a diagram need not be a subcategory, and a subset doesn't remember enough.

For example, suppose $X\in C$. Consider these two diagrams.

One-object diagram:

$$
\bullet \mapsto X.
$$

Two-object discrete diagram:

$$
\bullet\qquad\bullet
$$

with **both** objects mapped to $X$:

$$
D(1)=X,\qquad D(2)=X.
$$

As a naive “subset of $C$,” both diagrams just contain

$$
\{X\}.
$$

But they are very different diagrams. In $\mathbf{Set}$, for instance, their limits are

$$
X
$$

and

$$
X\times X
$$

respectively.

So the indexing category $J$ is doing important work: it remembers that there are **two occurrences** of $X$, not just which objects happen to occur in the image.

---

There are, however, a few closely related ways authors use the word “diagram.”

One common older/informal definition is essentially Goldblatt's: a directed graph of objects and arrows inside $C$,

$$
A\xrightarrow f B\xrightarrow g C.
$$

Formally, you can regard the shape as a **directed graph** $G$, and assign its vertices to objects of $C$ and its edges to morphisms of $C$.

This is almost the functor definition. From the graph $G$, form the **free category** $F(G)$. Then the assignment determines a functor

$$
F(G)\to C.
$$

For example, if your displayed graph is

$$
1\xrightarrow a2\xrightarrow b3,
$$

the free category also contains the composite

$$
1\xrightarrow{ba}3
$$

and the identity arrows. A functor into $C$ necessarily sends that composite to

$$
D(b)\circ D(a).
$$

So the picture doesn't normally draw identities and composites because they are **implicit**.

There's another variation when you want a **commutative diagram**. Suppose you draw

$$
\begin{array}{ccc}
A & \xrightarrow{f} & B\\
\downarrow g && \downarrow h\\
C & \xrightarrow{k} & D.
\end{array}
$$

You want the relation

$$
h\circ f=k\circ g.
$$

You can encode the shape as a category $J$ in which those two paths are declared equal. Then any functor

$$
D:J\to C
$$

automatically satisfies

$$
D(h)D(f)=D(k)D(g).
$$

So you can think of the progression as

$$
\boxed{
\text{graph}
\longrightarrow
\text{category of the shape}
\longrightarrow
C
}
$$

with the last arrow being the diagram functor.

### A subcategory is a special case

If $J$ actually is a subcategory of $C$, then the inclusion

$$
J\hookrightarrow C
$$

is indeed a diagram. But requiring diagrams to be subcategories would be much too restrictive.

A subcategory has to contain identities and be closed under composition (depending on the precise convention for subcategory), whereas when we draw

$$
A\xrightarrow f B\xrightarrow g C
$$

we don't necessarily explicitly include $g\circ f$. More importantly, a subcategory can't naturally represent the “same object appearing twice” phenomenon above.

So I would organize the definitions this way:

$$
\boxed{\textbf{Most precise/general:}\quad D:J\to C}
$$

$$
\boxed{\textbf{Equivalent for graph-shaped diagrams:}\quad
\text{a graph mapped into the underlying graph of }C}
$$

$$
\boxed{\textbf{Informal picture language:}\quad
\text{some objects of }C\text{ and arrows between them}}
$$

And I would **not** define it as “a self-consistent subset of $C$.” The central missing idea there is that a diagram has its own **abstract shape**, independently of the objects/arrows of $C$ that realize that shape.

That distinction—**shape $J$** versus **realization $D:J\to C$**—is really the conceptual reason the functor definition is superior.


---

> [image: sediment://file_00000000c4b4820c9cae5f02c90cbff6]
> How would one define imperative vs declarative here and why does milewski refer to “revolutionizing our understanding of the universe”

<details><summary>💭 Thinking</summary>

**Explaining the contrast**

I’m interpreting “revolutionizing the universe” as rhetorical: declarative descriptions express relationships, while imperative ones prescribe steps. The deeper idea is whether laws, mathematics, and programs can share one executable language—though undecidability limits universal conversion.

</details>

In this passage, Milewski is using **imperative** and **declarative** in a fairly conceptual sense rather than as a rigid classification of programming languages.

A declarative description says **what relation/result should hold** without making the temporal sequence of computation part of the description. For example,

$$
h = g\circ f
$$

says that $h$ is the composite of $f$ and $g$. Mathematically, this is just an equation between morphisms:

$$
X\xrightarrow{f}Y\xrightarrow{g}Z,
\qquad
h=g\circ f:X\to Z.
$$

There is no intrinsic statement here like “first execute $f$, wait until it finishes, store its output, then execute $g$.” It specifies the **relationship** between $h,f,g$.

An imperative description instead gives an **operational procedure**—roughly, what steps are to occur:

$$
\begin{aligned}
y &:= f(x),\\
\text{return }g(y).
\end{aligned}
$$

Conceptually:

$$
\text{do }f
\quad\longrightarrow\quad
\text{obtain }y
\quad\longrightarrow\quad
\text{do }g.
$$

So a useful distinction for this passage is

$$
\boxed{\text{declarative: what is true / what result is wanted}}
$$

versus

$$
\boxed{\text{imperative: how to produce it / what operations to perform}}.
$$

That distinction isn't perfectly sharp. Milewski himself immediately notes this: the compiler might implement the “declarative” expression using the same machine operations as the “imperative” one, and lazy evaluation might execute an apparently sequential expression in an unexpected order. He's distinguishing **levels of description**, not necessarily different physical execution.

### Why “revolutionize our understanding of the universe”?

He's pushing the distinction much further than ordinary programming.

The question at the bottom of the page is essentially:

> Given a description of **what a solution must satisfy**, can we always turn that description into a procedure for actually finding the solution?

Schematically,

$$
\boxed{\text{specification}}
\quad\xrightarrow{?}\quad
\boxed{\text{algorithm}}.
$$

That's a profound question because mathematics is full of declarative statements such as

$$
\text{find }x\text{ such that }P(x)
$$

while computation requires something like

$$
x_0\to x_1\to x_2\to\cdots\to\text{answer}.
$$

Those are not automatically equivalent.

For instance, saying

$$
\exists n\;P(n)
$$

is declarative. It says an $n$ satisfying $P$ exists. But that does **not**, in general, give you an algorithm that finds such an $n$.

This connects to some of the deepest results in logic and computation: undecidability, the halting problem, constructive versus nonconstructive existence proofs, and the limits of what algorithms can extract from mathematical specifications. We already know that there cannot be a completely general procedure turning arbitrary mathematical specifications into successful algorithms.

So I wouldn't read his sentence as claiming that this is literally an unsolved yes/no question in the simplest formulation. In unrestricted form, computability theory already gives strong negative results. I think he's gesturing toward the **broader philosophical problem**:

$$
\boxed{\text{What is the relationship between description and process?}}
$$

And that has an obvious connection to physics as well. Physics often gives us something resembling a declarative description:

$$
\text{the state of the universe satisfies certain laws/equations},
$$

while the universe appears to undergo a process:

$$
\text{state at }t
\longrightarrow
\text{state at }t+\Delta t.
$$

One can then ask whether every lawful/global description of a physical system has an equivalent local computational/evolutionary description. Questions of that sort touch computation, logic, mathematics, and fundamental physics, hence the deliberately grand phrase about “our understanding of the universe.”

There's also a category-theoretic theme hiding here. Category theory strongly favors **declarative/universal characterizations**. For example, a product isn't primarily defined as “run this construction algorithm”; it is characterized by a universal property:

$$
P\cong A\times B
$$

iff $P$ has the appropriate projections and unique factorization property. That tells you **what the product is characterized by**, not necessarily **how to compute one**.

So one recurring theme in Milewski is:

$$
\text{universal property/specification}
\quad\text{vs.}\quad
\text{construction/computation}.
$$

That is probably the conceptual bridge he's building on this page.


---

> [image: sediment://file_00000000dc04822f872475a954464ab0]
> What is a naturality condition

A **naturality condition** is the compatibility equation that the components of a natural transformation must satisfy with respect to every morphism in the source category.

Suppose you have two functors

$$
F,G:I\to C
$$

and a natural transformation

$$
\alpha:F\Rightarrow G.
$$

For every object $i\in I$, $\alpha$ gives a morphism

$$
\alpha_i:F(i)\to G(i).
$$

But an arbitrary collection of such arrows is **not** automatically a natural transformation. For every morphism

$$
f:i\to j
$$

in $I$, we require

$$
\boxed{G(f)\circ \alpha_i=\alpha_j\circ F(f).}
$$

Equivalently, this square must commute:

$$
\begin{array}{ccc}
F(i) & \xrightarrow{F(f)} & F(j)\\
\downarrow{\alpha_i} && \downarrow{\alpha_j}\\
G(i) & \xrightarrow{G(f)} & G(j).
\end{array}
$$

That equation is **the naturality condition for $f$**. A natural transformation satisfies it for every $f$.

### In the cone on your page

Milewski has

$$
\Delta_c:I\to C
$$

and

$$
D:I\to C,
$$

with a cone being a natural transformation

$$
\lambda:\Delta_c\Rightarrow D.
$$

The constant functor $\Delta_c$ sends every object of $I$ to $c$, and every morphism $f:i\to j$ to

$$
\Delta_c(f)=\operatorname{id}_c.
$$

The general naturality square therefore becomes

$$
\begin{array}{ccc}
c & \xrightarrow{\operatorname{id}_c} & c\\
\downarrow{\lambda_i} && \downarrow{\lambda_j}\\
D(i) & \xrightarrow{D(f)} & D(j).
\end{array}
$$

So the naturality equation is

$$
D(f)\circ\lambda_i
=
\lambda_j\circ\operatorname{id}_c,
$$

hence simply

$$
\boxed{D(f)\circ\lambda_i=\lambda_j.}
$$

Graphically:

$$
\require{AMScd}
\begin{array}{ccccc}
&&c&&\\
&\swarrow_{\lambda_i}&&\searrow^{\lambda_j}&\\
D(i)&\xrightarrow{\quad D(f)\quad}&D(j).
\end{array}
$$

The triangle must commute.

So if you can get from the apex $c$ to $D(j)$ in two ways,

$$
c\xrightarrow{\lambda_j}D(j)
$$

or

$$
c\xrightarrow{\lambda_i}D(i)\xrightarrow{D(f)}D(j),
$$

the two resulting morphisms must be identical.

That's what Milewski means when he says the morphisms in the indexing category “impose naturality conditions” on the cone: **each arrow in $I$ produces an equation that the cone's legs must satisfy.**

A useful way to think about it is:

$$
\boxed{\text{naturality}=\text{the component maps respect the structure of the diagram}.}
$$

Without the naturality condition, you'd merely have a bunch of unrelated arrows from $c$ to the objects of the diagram. The condition is precisely what makes those arrows into a coherent **cone**.

