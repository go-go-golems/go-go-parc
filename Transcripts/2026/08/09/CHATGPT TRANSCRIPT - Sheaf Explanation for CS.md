# Sheaf Explanation for CS

- URL: https://chatgpt.com/c/6a780455-4490-83ea-b914-f16434dbb515
- Created: 2026-08-09T04:39:05.323Z

---

> [image: sediment://file_000000009a1c820c8e957bd5f51e5318]
> What’s a sheaf explain for computer scientist

For a computer scientist, a **sheaf** is best thought of as:

> **A data structure for storing information locally on regions, with rules saying when compatible local pieces can be assembled into one global piece.**

Suppose your “space” is time, \(\mathbb R\), as in the slide. For every time interval \(U=(a,b)\), define

\[
B(U) = \{\text{all possible system behaviors during }U\}.
\]

A behavior might be a sensor trace, program execution, state trajectory, network signal, etc.

### 1. You can restrict data

If you know a behavior on \(0<t<10\), you automatically know its behavior on \(3<t<5\):

\[
B((0,10)) \longrightarrow B((3,5)).
\]

In programming terms, this is like taking a slice:

```text
trace[0:10]  ->  trace[3:5]
```

These are called **restriction maps**.

### 2. Compatible pieces can be glued

Suppose two machines give you:

```text
behavior A:  t = 0 ... 6
behavior B:  t = 4 ... 10
```

They overlap on \(t=4...6\).

If A and B give **exactly the same behavior on that overlap**, then a sheaf says you can combine them into a behavior on \(0...10\):

```text
A:  ----------------
B:            ----------------
             ^^^^^^
             agree here

=>   ----------------------------
          one combined behavior
```

And importantly, that combined behavior is **unique**.

That is essentially the sheaf condition:

\[
\text{compatible local data}
\quad\Longleftrightarrow\quad
\text{one global piece of data}.
\]

### Why computer scientists might care

This pattern appears all over CS. Think of **distributed systems**: nodes each know part of the state and must agree where their knowledge overlaps. Or **databases**: several consistent views should correspond to one underlying dataset. Or **program analysis**: you understand execution on pieces of the state space and want to compose the results. Or, as in the lecture, **systems theory**: describe possible behaviors on short time intervals, then compose them into longer behaviors.

The distinction between a **presheaf** and a **sheaf** is useful here:

- A **presheaf** gives you local data plus the ability to restrict it.
- A **sheaf** additionally guarantees that mutually compatible local pieces glue uniquely.

So the slide’s notation \(B(a,b)\) is essentially saying:

> “For each time window \((a,b)\), store the set of possible behaviors the system can exhibit during that window.”

If those behavior sets satisfy the gluing rule, \(B\) is a sheaf.

A very CS-flavored slogan is:

\[
\boxed{\text{Sheaf} = \text{local state} + \text{restriction} + \text{consistent composition}}
\]

And the interesting move in Spivak’s talk is that instead of describing a system primarily by a state machine or differential equation, you can describe it by **which behaviors are possible on every region**, together with how those behaviors fit together.


---

> Examples of sheaves in a bit more abstract cs or even maths

<details><summary>💭 Thinking</summary>

**Exploring sheaf examples**

I’m organizing examples from familiar mathematical objects to abstract computer-science settings: continuous functions, vector-bundle sections, differential-equation solutions, and compatible local assignments in networks or constraint systems.

**Explored sheaf examples**

</details>

A useful way to move one level more abstract is to forget that the “regions” have to be time intervals.

A sheaf is roughly a contravariant assignment

\[
U \mapsto F(U)
\]

where \(U\) is some **context/region**, \(F(U)\) is the information available on that context, and inclusions \(V\subseteq U\) give restriction maps

\[
F(U)\to F(V).
\]

The extra sheaf condition says that compatible information on a cover \(U=\bigcup_i U_i\) corresponds to exactly one piece of information on \(U\).

For set-valued sheaves, the formal condition is that

\[
F(U)\longrightarrow \prod_i F(U_i)
\rightrightarrows
\prod_{i,j} F(U_i\cap U_j)
\]

is an equalizer: a global object is exactly a family of local objects that agree pairwise on overlaps.

Here are some examples.

### 1. Continuous functions

This is the canonical mathematical example.

For a topological space \(X\), define

\[
F(U)=\{f:U\to \mathbb R\mid f\text{ continuous}\}.
\]

Restriction is literally function restriction.

If you have continuous functions

\[
f_i:U_i\to\mathbb R
\]

and

\[
f_i|_{U_i\cap U_j}=f_j|_{U_i\cap U_j},
\]

then they uniquely glue into

\[
f:\bigcup_i U_i\to\mathbb R.
\]

So continuous functions form a sheaf.

The same works for smooth functions, holomorphic functions, etc.

---

### 2. Vector fields / sections of a bundle

Suppose \(M\) is a manifold. Let

\[
F(U)=\{\text{vector fields on }U\}.
\]

A vector field defined on a large region can be restricted to a smaller one.

And if

\[
v_1\in F(U_1), \qquad v_2\in F(U_2)
\]

agree on \(U_1\cap U_2\), they give one vector field on \(U_1\cup U_2\).

More generally, if you have a bundle

\[
E\to X,
\]

the assignment

\[
U\mapsto \Gamma(U,E)
\]

of **sections of the bundle over \(U\)** is a sheaf.

This is one reason “section” appears constantly in sheaf theory: a sheaf is abstracting the behavior of sections of geometric objects.

---

### 3. Solutions to differential equations

Suppose

\[
y''+y=0.
\]

Let

\[
F(U)=\{\text{solutions of }y''+y=0\text{ on }U\}.
\]

Again, solutions restrict.

If you have a solution on \(U_1\) and another on \(U_2\), and they literally agree on the overlap, they glue to a solution on the union.

So you can think of the differential equation as determining a sheaf of its **locally possible behaviors**.

This is quite close to the systems-theoretic interpretation in the lecture you were watching.

Instead of saying

\[
\text{"the system is }y''+y=0",
\]

you can characterize it by

\[
U\mapsto
\{\text{behaviors allowed on }U\}.
\]

---

### 4. Constraint satisfaction as a sheaf-like object

This is a nice CS interpretation.

Suppose variables are

\[
x_1,x_2,x_3,x_4.
\]

For each subset \(U\) of variables, define

\[
F(U)=\{\text{assignments of values to variables in }U\}.
\]

For example,

\[
F(\{x_1,x_2\})
\]

could contain assignments

\[
(x_1=3,x_2=7).
\]

Restriction means forgetting variables:

\[
(x_1=3,x_2=7,x_3=4)
\mapsto
(x_1=3,x_3=4).
\]

Now imagine two local assignments:

\[
\begin{aligned}
s_1 &: x_1=3,\ x_2=7,\ x_3=4\\
s_2 &: x_3=4,\ x_4=9.
\end{aligned}
\]

They agree on their shared variable \(x_3\), so they glue:

\[
x_1=3,\quad x_2=7,\quad x_3=4,\quad x_4=9.
\]

This viewpoint becomes powerful when local contexts carry constraints. Then a major question is:

\[
\boxed{
\text{Do locally consistent solutions come from a global solution?}
}
\]

That is extremely close to the language of sheaves and **descent**.

It appears in CSPs, contextuality, distributed consistency, database theory, and related areas.

---

### 5. A sheaf on a network

You don't even need an ordinary geometric space.

Take a graph

\[
A \longleftrightarrow B \longleftrightarrow C.
\]

Put a vector space of possible states on each node:

\[
V_A,\quad V_B,\quad V_C,
\]

and spaces describing shared/interface information on edges.

For instance,

\[
V_A \xrightarrow{r_{AB}} V_{AB}
\]

and

\[
V_B \xrightarrow{r_{BA}} V_{AB}.
\]

A globally consistent state requires

\[
r_{AB}(a)=r_{BA}(b).
\]

Similarly,

\[
r_{BC}(b)=r_{CB}(c).
\]

So a global section is a tuple

\[
(a,b,c)
\]

satisfying all interface-consistency equations.

This leads to **cellular sheaves**, which are used to model things such as distributed sensing, consensus, network coding, synchronization, and data fusion.

From a CS point of view, this is a particularly useful picture:

\[
\boxed{
\text{objects have local state; interfaces specify what must agree}
}
\]

and global sections are globally consistent system states.

---

### 6. Database views

There is also a database interpretation.

Suppose one table/view contains attributes

\[
\{A,B,C\}
\]

and another contains

\[
\{B,C,D\}.
\]

Their common interface is

\[
\{B,C\}.
\]

Projection onto columns behaves like restriction:

\[
\pi_{BC}:R_{ABC}\to R_{BC}.
\]

If two pieces of data agree on their shared attributes, one can ask whether they can be joined into a consistent larger relation.

So the sheaf viewpoint turns familiar operations

\[
\text{projection},\quad \text{join},\quad \text{consistency}
\]

into instances of

\[
\text{restriction},\quad \text{gluing},\quad \text{descent}.
\]

There are some subtleties here—arbitrary database schemas do not automatically give a sheaf—but the analogy becomes mathematically precise in appropriate categorical models.

---

### The really abstract version

Topology is not actually essential.

You can replace “open subsets of a space” by an arbitrary category of **contexts**

\[
\mathcal C.
\]

Then a presheaf is a functor

\[
F:\mathcal C^{op}\to\mathbf{Set}.
\]

The objects of \(\mathcal C\) might mean:

- regions of space,
- time intervals,
- sets of variables,
- subsystems,
- database schemas,
- experimental contexts,
- interfaces,
- computational resources.

You then specify what counts as a family of contexts that **covers** another context. This structure is called a **Grothendieck topology**.

A sheaf is then a presheaf satisfying the appropriate gluing condition with respect to those covers.

So at the most abstract level:

\[
\boxed{
\text{sheaf theory is a theory of consistent local-to-global information}
}
\]

That is why it jumps surprisingly naturally from algebraic geometry to differential equations, distributed systems, databases, logic, and theoretical CS.


---

> From compiler / semantics / typing?

<details><summary>💭 Thinking</summary>

**Connecting semantics and typing**

I’m distinguishing common presheaf uses from genuine sheaf conditions. In type theory, contexts and substitutions naturally form presheaves; sheaves arise when local typing data can be glued consistently. Compiler analyses can similarly model control-flow facts as sections over program regions.

**Connected semantics and typing**

</details>

Yes. In PL/compilers, **presheaves are often the immediate structure**, and a sheaf appears once you also specify what counts as a cover and require compatible local pieces to glue.

A useful translation is:

\[
\text{open region} \rightsquigarrow \text{typing context / program point / world / interface}.
\]

### Typing: contexts behave like regions

Take a typing context

\[
\Gamma = x:A,\; y:B,\; z:C.
\]

Let

\[
\mathrm{Tm}(\Gamma)
\]

mean “terms meaningful in context \(\Gamma\).”

If you substitute, rename, or forget variables, you get a map of contexts

\[
\sigma:\Delta\to\Gamma.
\]

A term in \(\Gamma\) can then be reinterpreted in \(\Delta\):

\[
t\in\mathrm{Tm}(\Gamma)
\quad\mapsto\quad
t[\sigma]\in\mathrm{Tm}(\Delta).
\]

So you get something like

\[
\mathrm{Tm}:\mathbf{Ctx}^{op}\to\mathbf{Set}.
\]

That is exactly a **presheaf**.

This is not just an analogy: presheaf categories are standard semantic universes for type theory.

For dependent types you get structures resembling

\[
\Gamma\mapsto \mathrm{Ty}(\Gamma)
\]

and

\[
(\Gamma,A)\mapsto \mathrm{Tm}(\Gamma,A),
\]

with substitution acting by reindexing:

\[
A\mapsto A[\sigma],
\qquad
t\mapsto t[\sigma].
\]

So one way to read “presheaf” as a PL person is:

> Something whose meaning varies with context, and substitution transports meaning contravariantly.

---

### Where the **sheaf** part enters

Suppose a context or semantic world can be covered by smaller contexts

\[
U = U_1\cup U_2.
\]

You know an object locally:

\[
t_1\in F(U_1),\qquad t_2\in F(U_2).
\]

If their interpretations agree wherever both contexts can observe them,

\[
t_1|_{U_1\cap U_2}
=
t_2|_{U_1\cap U_2},
\]

a sheaf says there is one unique

\[
t\in F(U)
\]

having both as restrictions.

In semantics, that reads like:

> If every local observer/context sees mutually compatible pieces of a semantic object, those pieces describe one global semantic object.

This comes up especially naturally in semantics involving locality, resources, state, concurrency, or partial observations.

---

## Kripke semantics / possible worlds

This is perhaps the cleanest PL example.

Suppose worlds describe available resources:

\[
w_0\leq w_1\leq w_2.
\]

A semantic type \(A\) assigns to every world \(w\) the values valid there:

\[
\llbracket A\rrbracket(w).
\]

Moving between worlds gives transport maps. This is fundamentally presheaf/Kripke structure.

For example, in semantics of mutable state, a world might describe which heap locations exist:

\[
w=\{\ell_1:\text{int},\ell_2:\text{bool}\}.
\]

Then a semantic object may have information defined relative to that heap fragment.

If worlds can be assembled from compatible pieces, sheaf conditions can express:

\[
\text{compatible semantics on heap fragments}
\Rightarrow
\text{semantics on the combined heap}.
\]

That is very close in spirit to separation logic:

\[
h=h_1 * h_2.
\]

Sheaf theory gives one mathematical vocabulary for saying that meaning is **local in resources and compositional under compatible combination**.

---

## Compiler analysis: CFG as a local-to-global problem

Take a CFG:

```text
       B1
      /  \
     B2  B3
      \  /
       B4
```

Each basic block has some analysis information:

\[
F(B_i).
\]

For example:

- live variables,
- reaching definitions,
- available expressions,
- constant information,
- taint information.

Edges describe compatibility/transport between facts.

You can think of

\[
F(B_i)\to F(e)
\]

as saying “what does the fact at this block imply at this interface?”

A **global section** would be a choice

\[
(x_1,x_2,x_3,x_4)
\]

of information for every block such that every edge constraint is satisfied.

Schematically:

\[
r_{B_2,e}(x_2)=r_{B_4,e}(x_4).
\]

This is strongly sheaf-like.

Traditional compiler terminology would instead say:

> Find a globally consistent solution to the dataflow equations.

Sheaf terminology says:

> Find a global section compatible with all local restrictions.

Those are extremely similar mathematical shapes.

Ordinary monotone dataflow frameworks aren't automatically sheaves, because joins and fixed points introduce extra order-theoretic structure, but a CFG can absolutely be equipped with a cellular sheaf whose sections encode consistent program information.

---

## SSA gives a surprisingly intuitive picture

Consider

```c
if (c) {
    x1 = 10;
} else {
    x2 = 20;
}

x3 = phi(x1, x2);
```

The branches have locally meaningful definitions:

```text
then region: x = x1
else region: x = x2
```

At the join point, they cannot simply be claimed to be the same value.

The \(\phi\)-node supplies the rule for producing the value appropriate to the combined control-flow context.

So although SSA itself is not “a sheaf”, there's a useful sheaf interpretation:

\[
\text{branch-local information}
\longrightarrow
\text{information valid after gluing control-flow paths}.
\]

A failure to reconcile branch information is exactly the kind of **local-to-global obstruction** sheaf language is designed to expose.

---

## Logical relations

Here's another very PL-native one.

Suppose you are proving contextual equivalence. For each typing context/world \(\Gamma\), define

\[
R(\Gamma)
\]

to be pairs of terms related at \(\Gamma\).

Substitution should preserve the relation:

\[
(t_1,t_2)\in R(\Gamma)
\implies
(t_1[\sigma],t_2[\sigma])\in R(\Delta).
\]

Again:

\[
R:\mathbf{Ctx}^{op}\to\mathbf{Set}
\]

is naturally presheaf-shaped.

Step-indexed logical relations make this even clearer: the “world” can include an index,

\[
(n,w),
\]

and semantic validity changes as you move through these worlds.

A lot of sophisticated PL semantics can therefore be summarized as:

\[
\boxed{\text{meaning is indexed by context/world, and reindexes functorially}}
\]

which is precisely presheaf territory.

---

## A compiler/programming-language dictionary

The correspondence I would keep in mind is:

| Sheaf language | PL/compiler language |
|---|---|
| region \(U\) | context, world, program fragment |
| \(F(U)\) | terms / values / facts valid there |
| restriction | substitution, projection, forgetting, observation |
| overlap | shared variables/resources/interface |
| compatibility | same observable information on interface |
| gluing | compose local meanings |
| global section | globally consistent program/analysis/state |
| obstruction to gluing | incompatibility / inconsistency |

And the key distinction is:

\[
\boxed{
\text{Presheaf} \approx \text{semantics under changing context}
}
\]

while

\[
\boxed{
\text{Sheaf} \approx
\text{semantics under changing context}
+
\text{a local-to-global principle}.
}
\]

If you're coming from type theory specifically, **“types and terms varying over contexts, with substitution as restriction”** is probably the fastest route into why category theorists see presheaves/sheaves everywhere in semantics.


---

> Explain what a semantic world is

A **semantic world** is an abstract description of the circumstances under which you interpret a program, value, proposition, or type.

Think of it as an extra parameter to semantics:

\[
\llbracket A \rrbracket_w
\]

meaning:

> “What does type \(A\) mean, assuming world \(w\)?”

The word **world** is deliberately vague. Depending on the semantics, \(w\) might describe the current heap layout, which resources exist, what invariants are assumed, how many computation steps remain, what other modules promise, which variables are observable, or some combination of these.

### A concrete mutable-memory example

Suppose a language has references. A world might be a description of allocated locations and their types:

\[
w =
\{
\ell_1 : \mathrm{Int},
\ell_2 : \mathrm{Bool}
\}.
\]

Then the semantic judgment

\[
w \models v : A
\]

means roughly:

> “Under a heap having the structure described by \(w\), \(v\) behaves like an \(A\).”

For instance,

\[
\ell_1 \in \llbracket \mathrm{Ref\ Int}\rrbracket_w
\]

because world \(w\) says that \(\ell_1\) points to an integer.

Now the program allocates another reference:

```text
r = new String("hello")
```

The semantic world grows to

\[
w' =
\{
\ell_1 : \mathrm{Int},
\ell_2 : \mathrm{Bool},
\ell_3 : \mathrm{String}
\}.
\]

We write something like

\[
w \leq w'
\]

meaning “\(w'\) is a possible extension of \(w\).”

This ordering between worlds is central to **Kripke semantics**.

---

A semantic type can therefore be thought of not simply as a set of values,

\[
\llbracket A\rrbracket \subseteq \mathrm{Values},
\]

but as something varying with worlds:

\[
w \mapsto \llbracket A\rrbracket_w.
\]

For example:

```text
World w0:
  locations = {a}

World w1:
  locations = {a,b}

World w2:
  locations = {a,b,c}
```

with

\[
w_0 \leq w_1 \leq w_2.
\]

If a value is valid at \(w_0\), we'd often require it to remain valid as the world grows:

\[
v\in\llbracket A\rrbracket_{w_0}
\Rightarrow
v\in\llbracket A\rrbracket_{w_1}.
\]

This property is sometimes called **monotonicity**, **persistence**, or **Kripke monotonicity**, depending on the setting.

### Why introduce worlds at all?

Because plain sets often aren't enough to describe program meaning.

Consider a function that closes over a reference:

```text
x = ref 0

f = () => {
    x := !x + 1
}
```

The meaning of `f` depends on an external fact:

> There exists some location \(x\), and it continues to satisfy a particular invariant.

That fact isn't really part of `f`'s syntax or ordinary lexical environment. A semantic world can record it.

This becomes particularly important when proving things about:

- mutable state,
- dynamically allocated memory,
- abstract data types,
- modules,
- concurrency,
- recursive types,
- separation logic,
- logical relations.

### World vs environment

These are related but usually different.

An **environment** says what program variables denote:

\[
\rho =
\{
x\mapsto 42,\;
f\mapsto \text{some closure}
\}.
\]

A **world** describes ambient semantic assumptions:

\[
w =
\{
\ell_1:\mathrm{Int},
\ell_2:\mathrm{Bool}
\}.
\]

So you might interpret a term as

\[
\llbracket e\rrbracket_{\rho,w}.
\]

Very roughly:

\[
\boxed{
\rho = \text{what the names mean}
}
\]

whereas

\[
\boxed{
w = \text{what is assumed about the surrounding universe}
}
\]

### Worlds don't have to describe memory

For step-indexed semantics, a world might contain a natural number:

\[
w=n.
\]

Then

\[
v\in\llbracket A\rrbracket_n
\]

means something like:

> \(v\) behaves like an \(A\) for at least the next \(n\) computational steps.

World accessibility goes downward:

\[
n+1 \to n.
\]

This gives a way to define otherwise circular semantic objects, especially recursive types.

In concurrent separation logic, a world may instead encode ownership and invariants:

\[
w =
\{
\text{resource }R_1\text{ satisfies }I_1,\;
R_2\text{ satisfies }I_2
\}.
\]

In modal semantics, a world might represent one possible state of knowledge, and

\[
wRv'
\]

means that \(v'\) is a possible world reachable from \(w\).

---

And this connects directly back to your sheaf question.

Instead of having one fixed interpretation

\[
F,
\]

we have information indexed by worlds:

\[
w\mapsto F(w).
\]

Moving between worlds induces maps between the corresponding semantic information. So a category of worlds

\[
\mathcal W
\]

can give rise to a presheaf such as

\[
F:\mathcal W^{op}\to\mathbf{Set}.
\]

That's why **Kripke semantics, possible-world semantics, presheaf semantics, and sheaf semantics** often appear near one another.

The key mental model is:

\[
\boxed{
\text{A semantic world is a formalized “under these assumptions…” parameter.}
}
\]

It makes the context that semantic truth depends on explicit.


---

> How would you apply sheaf / presheaf in a JS API / DSL for CNC CAM ? That language is compiled to IR before compiled to gcode, with operational semantics of mill behavior and dejotational semantics as geometry

<details><summary>💭 Thinking</summary>

**Modeling local semantics**

I’d model geometry with a spatial presheaf over stock regions: local meanings restrict and glue when boundary data agree. For machine behavior, I’d use interval-indexed traces or state-transition morphisms, composing segments through explicit pre/post conditions rather than naïve gluing.

**Modeled local semantics**

**Designing the semantics**

I’d keep the JavaScript API ordinary—operations, tools, regions, fixtures—while internally assigning each IR node spatial support, local geometry, machine traces, constraints, and boundary contracts. Spatial sheaves help localize geometry; temporal presheaves handle stateful execution.

</details>

Yes. Your architecture is unusually well suited to a sheaf/presheaf viewpoint because you already have two different notions of composition:

\[
\text{geometry composes spatially}
\]

while

\[
\text{machine behavior composes temporally}.
\]

I would **not make “sheaf” a user-facing JS abstraction**. I would use it to structure the semantics, IR contracts, locality, and compiler correctness.

## 1. Spatial sheaf for the denotational geometry

Let \(X\) be the machine/workpiece workspace.

For a region \(U\subseteq X\), define something like

\[
G(U)
=
\{\text{geometric facts/effects observable inside }U\}.
\]

For your CAM system that could include:

- stock geometry in \(U\)
- intended final geometry in \(U\)
- material to remove in \(U\)
- tolerance field
- keep-out geometry
- cutter swept volume in \(U\)

Restriction is obvious:

\[
G(U)\to G(V),\qquad V\subseteq U
\]

by clipping/intersecting with \(V\).

For example:

\[
R_U = \text{material removed in }U
\]

restricts as

\[
R_U|_V = R_U\cap V.
\]

If two geometric results on \(U_1\) and \(U_2\) agree on

\[
U_1\cap U_2,
\]

they can be glued into a geometric result on

\[
U_1\cup U_2.
\]

That's an extremely natural sheaf.

So your denotational semantics could conceptually be

\[
\llbracket p\rrbracket_G \in G(X).
\]

But importantly, you can ask for it locally:

\[
\llbracket p\rrbracket_G|_U.
\]

That locality can become operationally useful in the compiler.

---

# 2. Temporal presheaf/sheaf for mill behavior

Now use time rather than space.

For a time interval \(I\), define

\[
B(I)
=
\{\text{possible mill behaviors during }I\}.
\]

A behavior could contain

\[
b(t)=
(
q(t),
v(t),
\text{tool}(t),
\text{spindle}(t),
\text{feed}(t),
\text{coolant}(t),
\text{modalState}(t),
\text{stock}(t)
).
\]

Here \(q(t)\) could be the complete machine configuration, not merely XYZ.

A trace on

\[
I=[0,20]
\]

can clearly be restricted to

\[
J=[7,12].
\]

So

\[
B(I)\to B(J).
\]

If two complete traces overlap and agree on their overlap, they glue uniquely.

So **actual execution traces are very sheaf-like**.

But there's an important distinction for CAM:

> A set of *candidate toolpath fragments* is usually only a presheaf, not necessarily a sheaf.

Suppose one operation ends here:

```text
A ----> endpoint
```

and another starts here:

```text
                 start ----> B
```

There may be 100 valid retract/rapid/plunge paths connecting them.

The local pieces don't uniquely determine their glue.

That's not a bug. It means:

\[
\text{planning} = \text{finding a global section}
\]

rather than merely invoking the sheaf gluing theorem.

That's a quite good conceptual description of CAM.

---

# 3. Your denotational/operational split becomes very clean

Suppose your DSL program is

```js
const p = sequence(
  pocket(face, { tool: endmill6 }),
  contour(profile, { tool: endmill3 })
);
```

You already have approximately:

\[
p
\overset{\text{denotation}}{\longmapsto}
\text{geometry}
\]

and

\[
p
\overset{\text{compiler}}{\longmapsto}
IR
\longmapsto
GCode
\overset{\text{machine semantics}}{\longmapsto}
\text{behavior}.
\]

So make the bridge explicit.

Let

\[
D(p)
\]

be the intended geometric effect.

Let

\[
\operatorname{exec}(\operatorname{compile}(p))
\]

be the operational trace.

Then define

\[
\operatorname{effect} : B \to G
\]

where `effect` computes the physical geometric consequence of a trace.

Conceptually:

\[
\operatorname{effect}(b)
=
\bigcup_t \operatorname{CutterVolume}(q(t)).
\]

If \(S_0\) is the initial stock,

\[
S_{\text{final}}
=
S_0
\setminus
\operatorname{sweptVolume}(b)
\]

in an idealized milling model.

Then your central compiler correctness property becomes something like

\[
\boxed{
\operatorname{effect}
(
\operatorname{exec}(\operatorname{compile}(p))
)
\approx
D(p)
}
\]

where \(\approx\) incorporates your machining tolerance/model.

That's a very strong architecture.

---

# 4. Sheaves let that correctness theorem become local

This is where I think it becomes genuinely useful rather than category-theory decoration.

Suppose the workspace is covered by regions

\[
X=U_1\cup U_2\cup\cdots\cup U_n.
\]

Instead of proving

\[
\operatorname{effect}(\operatorname{exec}(C(p)))
=
D(p)
\]

over the entire giant BRep/mesh/voxel volume at once, verify

\[
\operatorname{effect}(\operatorname{exec}(C(p)))|_{U_i}
\approx
D(p)|_{U_i}
\]

for every \(U_i\).

If your geometric semantics is genuinely sheaf-like, agreement on the local pieces gives you the global result.

That naturally enables:

- tiled verification
- parallel geometry evaluation
- incremental recompilation
- localized collision checks
- local caching
- precise error localization

For example:

```text
Region 17:
  intended removal: 4.21 cm³
  operational removal: 4.21 cm³
  OK

Region 18:
  intended surface z: 12.000 ± .010
  operational surface z: 11.973
  FAIL
```

Now the semantic framework is telling you exactly *where* compilation stopped preserving meaning.

---

# 5. This could be especially useful for incremental CAM

Suppose the user modifies one pocket:

```js
pocket(foo, { depth: 12 })
```

to

```js
pocket(foo, { depth: 12.5 })
```

If you know its spatial support is approximately

\[
U\subset X,
\]

then the denotation hasn't changed outside \(U\):

\[
D(p_{\text{old}})|_{X-U}
=
D(p_{\text{new}})|_{X-U}.
\]

That gives you a principled basis for not recomputing the whole program.

Your IR nodes could carry support information:

```ts
interface IRNode {
  support: SpatialRegion;
  sweptEnvelope: SpatialRegion;

  pre: MachineContract;
  post: MachineContract;

  geometricEffect: GeometryEffect;
}
```

Notice I would distinguish:

```text
support
```

from

```text
sweptEnvelope
```

because an operation might remove material in a tiny region but retract through a much larger one.

That distinction matters for collision checking and recompilation dependencies.

---

# 6. The operational side needs boundary contracts

The really interesting gluing problem in G-code isn't just XYZ.

Suppose you compile two IR chunks:

```text
IR₁ ; IR₂
```

For them to compose, you need the outgoing semantic state of `IR₁` to match what `IR₂` assumes.

That state may contain:

```ts
type MachineWorld = {
  pose: Pose;
  velocity: Vec3;

  tool: ToolId;
  spindle: SpindleState;
  coolant: CoolantState;

  wcs: WorkCoordinateSystem;

  units: "mm" | "inch";
  distanceMode: "absolute" | "incremental";
  feedMode: FeedMode;

  cutterComp: CutterCompState;
  toolLengthComp: ToolLengthState;

  stock: Solid;
};
```

This is a very concrete example of the **semantic world** we were talking about.

A G-code fragment does not have an isolated meaning.

```gcode
X10 Y20
```

means radically different things depending on whether the world contains:

```text
G90
```

or

```text
G91
```

and similarly for active WCS, units, feed mode, cutter comp, etc.

So an IR fragment is better understood as something like

\[
IR : W_{\mathrm{in}}\to W_{\mathrm{out}}.
\]

In other words, your IR is really carrying an **effect system**.

---

# 7. The world-indexed semantics gives you another presheaf

Your world could be

\[
w =
(
\text{machine},
\text{tool table},
\text{fixture},
\text{stock},
\text{controller state},
\text{WCS},
\text{tolerance},
\ldots
).
\]

Then semantics varies with that context:

\[
w\mapsto \llbracket p\rrbracket_w.
\]

You can also have forgetful maps between contexts.

For example, an abstract compiler phase may know only

```text
machine = 3-axis
tool diameter = 6 mm
```

while a later phase knows

```text
machine = Haas VF2
controller = NGC
tool = slot 7
gauge length = 58.31 mm
fixture = ...
```

So semantics gets progressively instantiated/refined.

This is exactly the kind of situation where a context-indexed presheaf viewpoint becomes useful:

\[
F:\mathcal W^{op}\to\mathbf{Sem}.
\]

You don't necessarily need `Set` as the codomain. It might be:

- sets of feasible traces
- constraint lattices
- relations
- geometry domains
- abstract interpretation domains

---

# 8. Compiler passes as natural transformations

This is another place category theory buys something substantial.

Imagine:

```text
DSL
 ↓
Feature IR
 ↓
Toolpath IR
 ↓
Machine IR
 ↓
G-code
```

Each level has local semantics.

Then you'd like a compiler pass \(C\) to commute with restriction.

Informally:

\[
C(p)|_U
\approx
C(p|_U).
\]

In words:

> compiling and then looking locally should agree with looking locally and then compiling.

That is essentially a **naturality condition**.

If it holds, you get strong locality properties.

For instance:

```text
whole part
┌─────────────────────────────┐
│                             │
│      modified pocket U      │
│          ┌───────┐          │
│          │       │          │
│          └───────┘          │
│                             │
└─────────────────────────────┘
```

You can reason that changes confined to \(U\) should not mysteriously alter compiled behavior 300 mm away, except through explicitly modeled global dependencies such as:

- tool ordering
- tool changes
- thermal state
- total machining schedule
- fixture changes
- global optimization

Those dependencies become visible instead of implicit.

---

# 9. I'd separate two composition operators in the DSL/IR

This might be the most practical API consequence.

Your system has **spatial composition**:

```js
combineGeometry(a, b)
```

which is approximately symmetric/local.

And **temporal composition**:

```js
sequence(a, b)
```

which is emphatically ordered:

\[
a;b \neq b;a.
\]

Those shouldn't be conflated.

For example:

```js
const part = combine(
  pocket(regionA),
  pocket(regionB)
);
```

might state a geometric objective without committing to execution order.

Then

```js
plan(part, machine)
```

chooses

```js
sequence(
  toolChange(T1),
  machine(regionA),
  retract(),
  rapid(...),
  machine(regionB)
);
```

The first layer is very sheaf-like:

\[
\text{compatible local geometry}
\to
\text{global geometry}.
\]

The second is categorical/operational:

\[
f:A\to B,\quad g:B\to C
\]

compose as

\[
g\circ f:A\to C.
\]

I would preserve that distinction architecturally.

---

# 10. A possible internal model

Schematic TypeScript, rather than literal compilable dependent types:

```ts
type Region = SpatialRegion;
type Interval = TimeInterval;

interface LocalGeometry {
  restrict(region: Region): LocalGeometry;
}

interface MachineTrace {
  restrict(interval: Interval): MachineTrace;
}

interface Operation {
  // Denotational
  geometry(world: World): LocalGeometry;

  // Compilation
  lower(world: World): IR;
}

interface IR {
  pre: MachineContract;
  post: MachineContract;

  support: Region;
  sweptEnvelope: Region;

  simulate(world: World): MachineTrace;
}
```

Then:

```ts
function effect(
  trace: MachineTrace,
  stock: Solid
): LocalGeometry
```

and your semantic validator checks roughly:

```ts
equivalentWithinTolerance(
  effect(op.lower(w).simulate(w), w.stock),
  op.geometry(w)
)
```

You could make the spatially local version first-class:

```ts
validate(op, {
  cover: partition(workspace, { cellSize: 10 })
})
```

and generate diagnostics by region.

---

# 11. A stronger model: spacetime

If you wanted to push the idea farther, I'd actually consider a presheaf over **space × time**.

Let

\[
U\subseteq X,\qquad I\subseteq T.
\]

Define

\[
B(U,I)
\]

to contain observations of machine behavior occurring in spatial region \(U\) during time \(I\).

For example, you could interpret execution as an occupancy field

\[
\operatorname{occ}(x,t)
\]

saying whether location \(x\) at time \(t\) contains:

```text
cutter
holder
stock
fixture
machine
empty
```

Now collision is just a bad local spacetime configuration.

And final removed material is obtained by forgetting/projecting the time dimension:

\[
R(x)
=
\exists t:
\operatorname{cutter}(x,t).
\]

That gives a surprisingly elegant relationship between your operational and geometric semantics:

```text
operational semantics
        ↓
  spacetime behavior
        ↓ forget time
 geometric effect
```

For simulation/verification, this could be a useful conceptual core.

---

# 12. Where I would *not* insist on sheaves

A lot of CAM is globally coupled.

For example:

- minimizing total tool changes
- choosing operation ordering
- acceleration/look-ahead planning
- global feed optimization
- shortest rapid path
- avoiding clamps via alternate routes
- machine warmup/thermal effects

Local pieces generally **do not determine a unique global answer**.

So don't try to prove everything is a sheaf.

A good division would be:

\[
\boxed{
\text{presheaf} =
\text{we can observe/restrict semantics locally}
}
\]

and

\[
\boxed{
\text{sheaf} =
\text{local observations completely determine compatible global semantics}
}
\]

When the latter fails, that failure tells you where the planner/optimizer has genuine global work to do.

---

The architecture I would probably aim for is:

```text
                 JS DSL
                   │
                   │ denotation
                   ▼
          Spatial geometric semantics
             (sheaf-like)
                   │
                   │ planning
                   ▼
                 IR
          pre/post world contracts
                   │
                   │ operational semantics
                   ▼
            Machine behavior
         (time-indexed presheaf)
                   │
                   │ swept-volume/effect
                   ▼
          Spatial realized geometry
                   │
                   │ compare
                   ▼
            intended geometry
```

The particularly attractive theorem is then:

\[
\boxed{
\text{realized geometry of compiled operational behavior}
\approx
\text{denotational geometry of the source program}
}
\]

and sheaf-style locality gives you a route to make that theorem **incremental, spatially decomposable, and diagnosable**, rather than one giant whole-program claim.


---

> How can the locality be useful in the compiler?

<details><summary>💭 Thinking</summary>

**Framing the compiler value**

I’m treating locality as a dependency contract: each syntax node declares the regions, machines, tools, and context it can affect. That lets the compiler reason about scope instead of assuming every change is global.

**Compiling local patches**

A region can compile independently when its boundary interface is stable. The compiler produces geometry, motion, constraints, and required context for that patch, then glues compatible results. This supports parallel compilation and incremental recompilation.

**Invalidating precisely**

If a toolpath changes in one pocket, the compiler can invalidate that pocket, nearby linking moves, and any explicitly dependent operations—not the entire setup. Presheaf restriction gives the mechanism for viewing a larger program through smaller regions.

**Checking optimization safety**

Locality also acts as an optimization proof obligation. A transformation is safe when it preserves each region’s behavior and does not alter declared boundary effects. Truly global operations—stock evolution, collision envelopes, shared feeds, or machine scheduling—remain explicit joins rather than hidden leaks.

**Framed the compiler value**

**Applying locality concretely**

I’m sharpening the idea: each compiler pass records its spatial support, boundary contract, reads, and writes. A pocket edit then invalidates only overlapping toolpaths and dependent scheduling, while global effects remain explicit.

**Handling boundaries**

I’m allowing halos around regions because cutters, lead-ins, stock, collision checks, and machine motion cross geometric boundaries. Local compilation is valid when the halo’s interface state remains unchanged.

**Preserving correctness**

I’m using overlap agreement as a verification condition: independently compiled regions must match on shared boundaries. If they do, the compiler can safely assemble them, while global passes handle setup planning, stock evolution, and scheduling.

</details>

The most useful compiler interpretation of locality is:

> **To compile what happens in region \(U\), I should only need the source and semantic context near \(U\), plus a small explicit boundary interface.**

That gives you something much stronger than “the compiler happens to be modular.” It gives you a rule for **dependency tracking, invalidation, separate compilation, optimization, and verification**.

### A compiler pass can have a support law

Suppose \(C\) is a compiler pass and \(p\) is a CAM program. Ideally you get something like

\[
C(p)|_U
=
C(p|_U).
\]

Meaning: compiling the whole program and then inspecting region \(U\) gives the same answer as first restricting the problem to \(U\) and compiling just that.

For CAM, exact locality is usually too strong. A cutter has radius, lead-ins cross boundaries, smoothing looks ahead, etc. So a more realistic property is

\[
C(p)|_U
\quad\text{depends only on}\quad
p|_{\operatorname{halo}(U)}
\]

where

\[
\operatorname{halo}(U) \supseteq U
\]

is an influence region.

For a 6 mm end mill, for example, geometry inside \(U\) might depend on target geometry within at least a 3 mm expansion of \(U\). Corner smoothing might increase that further.

This is immediately useful for **incremental compilation**.

Imagine a plate with 100 pockets. The user changes:

```js
pocket(p17, { depth: 5 })
```

to

```js
pocket(p17, { depth: 5.5 })
```

You compute the changed spatial support \(D\). Then you only invalidate compiler artifacts whose dependency/support regions intersect its influence region:

\[
\operatorname{support}(node)\cap
\operatorname{influence}(D)
\neq\varnothing.
\]

The other 99 pockets don't need their geometry, offset calculations, collision queries, simulation, or semantic verification recomputed.

That is much more principled than an ad-hoc dependency graph because spatial support itself becomes part of the semantics.

---

### Make locality explicit in the IR

I would probably make every sufficiently high-level IR node carry something approximately like:

```ts
interface IRNode {
  // Where this operation changes the workpiece.
  semanticSupport: Region;

  // Everywhere the physical machine/tool may occupy.
  motionEnvelope: Region;

  // Context this node actually depends upon.
  reads: WorldProjection;

  // Context it modifies.
  writes: WorldProjection;

  pre: BoundaryContract;
  post: BoundaryContract;
}
```

The distinction between `semanticSupport` and `motionEnvelope` matters a lot.

A pocket might remove material only here:

```text
        semanticSupport
             ┌─────┐
             │     │
             └─────┘
```

while its machine movement is:

```text
       retract
          │
          │
   ───────┼──────── rapid
          │
       ┌─────┐
       │ cut │
       └─────┘
```

So changing that pocket may only invalidate geometric semantics locally, but collision analysis may need invalidation over the much larger swept envelope.

Different compiler analyses therefore have different notions of support.

That's a useful design principle in itself:

\[
\operatorname{support}_{geometry}(p)
\neq
\operatorname{support}_{collision}(p)
\neq
\operatorname{support}_{schedule}(p).
\]

---

### Local compilation becomes similar to separate compilation

Suppose the workpiece is covered by regions

\[
X=U_1\cup U_2\cup U_3.
\]

Rather than compiling one giant object, you can compile fragments

\[
C_1,\ C_2,\ C_3
\]

with explicit interfaces.

For a CNC fragment, the interface isn't just geometry. It could say:

```ts
type BoundaryContract = {
  allowedEntryPoses: PoseSet;
  allowedExitPoses: PoseSet;

  requiredTool: ToolId;

  incomingModalState: ModalConstraint;
  outgoingModalState: ModalConstraint;

  stockBoundary: LocalStockState;

  clearance: Region;
};
```

Then compilation becomes:

```text
 local planning                   linking / global planning

 U1 ──> fragment 1 ─┐
                    │
 U2 ──> fragment 2 ─┼──> compatible global machine program
                    │
 U3 ──> fragment 3 ─┘
```

This is where the sheaf language becomes interesting.

Each region doesn't necessarily produce **one** toolpath. It might produce a set of possible implementations:

\[
F(U)=
\{\text{valid machine behaviors implementing }U\}.
\]

The global planner is then looking for elements

\[
b_i\in F(U_i)
\]

whose boundary conditions agree.

So:

\[
\boxed{
\text{planning can be viewed as finding a compatible global section.}
}
\]

That is more interesting than merely saying “toolpaths form a sheaf.”

---

### Locality makes caching much better

Say your compiler currently has:

```text
DSL
 ↓
feature geometry
 ↓
offset geometry
 ↓
toolpath
 ↓
machine motion
 ↓
simulation
 ↓
G-code
```

With locality, your cache keys can become something like

```text
(
  IR fragment,
  relevant world projection,
  spatial support,
  compiler version
)
```

instead of

```text
(entire program, entire machine config)
```

Suppose a region only needs:

```ts
{
  toolDiameter,
  fluteLength,
  stockMaterial,
  localStock,
  tolerance
}
```

Then changing the coolant setting shouldn't invalidate its geometric offset calculation.

This is analogous to a compiler realizing that a function doesn't depend on every symbol in an entire program.

The presheaf/world viewpoint pushes you toward making that dependency precise:

\[
\llbracket p\rrbracket_w
\]

should ideally depend on only some projection

\[
\pi_p(w)
\]

of the world.

Thus if

\[
\pi_p(w_1)=\pi_p(w_2),
\]

you can reuse the result even though

\[
w_1\neq w_2.
\]

That's a potentially large cache win.

---

### It gives you a very good optimization criterion

Suppose you have some optimization

```text
toolpath
   ↓
optimized toolpath
```

such as simplifying collinear moves or replacing many short segments with an arc.

If the rewrite occurs entirely inside \(U\), you can establish:

\[
D(\text{before})|_U
\approx
D(\text{after})|_U
\]

and verify that the boundary behavior is preserved:

\[
\operatorname{boundary}(\text{before})
=
\operatorname{boundary}(\text{after}).
\]

Then the rest of the program does not need to participate in the proof.

This gives a **frame-like compiler rule**:

\[
\frac{
p \approx q\text{ on }U
\qquad
\partial p = \partial q
}{
p;r \approx q;r
}
\]

provided \(r\) is outside the affected support and no declared global dependency connects them.

Conceptually that's very similar to separation logic:

> If I know exactly which part of the world an optimization touches, I can reason about it while framing out everything else.

For a optimizing CAM compiler, this could be extremely useful.

---

### Verification gets dramatically more actionable

You described having

\[
D(p)
\]

as denotational geometry and an operational machine semantics

\[
\operatorname{Exec}(C(p)).
\]

Then suppose

\[
E(\operatorname{Exec}(C(p)))
\]

turns the machine trace into realized geometry.

Your correctness condition is something like

\[
E(\operatorname{Exec}(C(p)))
\approx D(p).
\]

Without locality, failure gives:

```text
compiled program does not match intended geometry
```

Not particularly useful.

With locality, cover the part:

```text
┌────┬────┬────┬────┐
│ U1 │ U2 │ U3 │ U4 │
├────┼────┼────┼────┤
│ U5 │ U6 │ U7 │ U8 │
└────┴────┴────┴────┘
```

and check

\[
E(\operatorname{Exec}(C(p)))|_{U_i}
\approx
D(p)|_{U_i}.
\]

Now you can report:

```text
U1 ✓
U2 ✓
U3 ✓

U4 ✗
expected floor: z = -5.000 ± 0.010
simulated floor: z = -4.972

U5 ✓
...
```

And then recursively subdivide \(U_4\).

That's essentially **semantic delta-debugging in space**.

It also makes verification parallelizable.

---

### Overlaps matter

You don't want to tile the world with totally disjoint boxes and ignore their boundaries.

Instead use overlapping regions or halos:

```text
       U1
 ┌───────────────┐
 │               │
 │        ┌──────┼────────┐
 │        │//////│        │
 └────────┼──────┘        │
          │       U2      │
          └───────────────┘
```

The overlap is where you test compatibility.

For geometry this could mean:

\[
G_1|_{U_1\cap U_2}
\approx
G_2|_{U_1\cap U_2}.
\]

For machine fragments it could mean compatible machine state, stock state, clearance conditions, etc.

This is the compiler version of the sheaf gluing condition:

\[
\text{local correctness}
+
\text{overlap compatibility}
\Rightarrow
\text{global correctness}.
\]

In actual numeric CAM you'd likely have an **approximate** compatibility relation due to tolerances rather than literal mathematical equality.

---

### Some passes should deliberately be nonlocal

Locality shouldn't become a religion.

For example, these are inherently global:

\[
\text{minimize tool changes}
\]

\[
\text{schedule all operations}
\]

\[
\text{find globally shortest traversal}
\]

\[
\text{choose a fixture/setup strategy}
\]

A tiny change in one pocket could legitimately change operation order over the whole job.

I would therefore make nonlocality **explicit in the compiler architecture**.

You might have something conceptually like:

```text
local feature lowering
        ↓
local geometric planning
        ↓
GLOBAL scheduling
        ↓
local motion realization
        ↓
GLOBAL machine look-ahead
        ↓
local simulation / verification
```

Then a source edit might cause:

```text
geometry invalidation:      local
collision invalidation:     local + envelope
operation scheduling:       potentially global
postprocessor formatting:   mostly local
```

The compiler knows exactly why recompilation expands outward.

That is much more useful than pretending all dependencies are equal.

---

So if I were turning the sheaf idea into a practical compiler abstraction, I wouldn't start with a `Sheaf<T>` class. I'd start with this invariant:

\[
\boxed{
\text{Every compiler artifact should say what region/world facts it depends on,
what region it affects, and what boundary contract it exposes.}
}
\]

Restriction then gives you **incrementality**, supports give you **precise invalidation**, boundary contracts give you **separate compilation**, gluing gives you **composition**, and local semantic equivalence gives you **modular verification and optimization**.

For a CAM compiler, that's probably where the abstract sheaf idea cashes out most directly.

