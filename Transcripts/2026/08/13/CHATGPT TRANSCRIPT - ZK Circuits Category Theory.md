# ZK Circuits Category Theory

- URL: https://chatgpt.com/c/6a7dee9b-1878-83ea-ba62-f32b562611a0
- Created: 2026-08-13T16:19:47.282Z

---

> ZK circuits , category theory

There is a real connection: category theory can give a compositional language for building and reasoning about zero-knowledge circuits, especially when circuits are assembled from reusable gadgets. I’ll separate the mathematical correspondence from what is actually used in current ZK systems.

```json
{"system1_search_query":[{"q":"site:eprint.iacr.org category theory zero knowledge circuits categorical circuits"},{"q":"site:arxiv.org category theory zero knowledge proof circuits monoidal category"},{"q":"site:docs.circom.io circuits signals components constraints"},{"q":"site:zcash.github.io halo2 circuit chips gadgets regions constraints"}],"response_length":"medium"}
```

<details><summary>💭 Thinking</summary>

**Modeling ZK categorically**

I’m modeling each circuit as a relation between input and output wire spaces, with hidden witnesses existentially quantified. Composition connects wires, tensor places circuits side by side, and identities or swaps represent basic wiring.

**Modeled ZK categorically**

**Searched 8 websites**

</details>

Yes—**ZK circuits and category theory fit together naturally through compositionality**, although category theory is better viewed today as a semantic/design framework than as a standard layer in mainstream ZK tooling such as Circom or Halo2. Circom exposes circuits as components with input/output signals and generated constraints, while Halo2 explicitly builds larger circuits from reusable chips and gadgets. citeturn964242search10turn964242search12turn964242search13

A useful categorical model is:

$$
\boxed{\text{objects = wire interfaces},\qquad
\text{morphisms = constraint gadgets}}
$$

For a field $\mathbb F$, imagine an object

$$
A=\mathbb F^m
$$

representing $m$ wires. A ZK gadget with $m$ inputs and $n$ outputs becomes

$$
f:A\to B.
$$

But unlike an ordinary function, a constraint system is often more naturally a **relation**

$$
R_f\subseteq \mathbb F^m\times\mathbb F^n
$$

because there may be hidden witness variables satisfying the constraints.

For example,

$$
z=x y
$$

can be represented by

$$
R_{\mathrm{mul}}
=
\{(x,y,z)\mid z-xy=0\}.
$$

That matches the actual constraint-centric view of systems such as R1CS: Circom, for example, compiles constraints into quadratic equations of the form $A\cdot B+C=0$. citeturn964242search19

### The particularly nice part: composition

Suppose you have gadgets

$$
R_f:A\rightarrow B
$$

and

$$
R_g:B\rightarrow C.
$$

Connecting the output wires of $f$ to the input wires of $g$ gives

$$
R_g\circ R_f.
$$

Relationally,

$$
(a,c)\in R_g\circ R_f
\iff
\exists b\;.\;
R_f(a,b)\land R_g(b,c).
$$

That existential variable $b$ looks exactly like an **internal witness wire**.

So one of the cleanest correspondences is

$$
\boxed{\text{hiding internal wires}
\quad\leftrightarrow\quad
\text{existential quantification in categorical composition}.}
$$

This is one reason the category **Rel** or categories of algebraic relations can be more natural for ZK semantics than simply the category of functions.

You also get parallel circuit composition from a monoidal product:

$$
f:A\to B,\qquad
g:C\to D
$$

becomes

$$
f\otimes g:
A\otimes C\to B\otimes D.
$$

Diagrammatically:

```text
 x ──[ f ]── y
                 
 a ──[ g ]── b
```

is $f\otimes g$, while

```text
x ──[ f ]── y ──[ g ]── z
```

is $g\circ f$.

This is precisely the setting of **symmetric monoidal categories and string diagrams**. Circuit semantics have long been modeled this way: a gate set generates a free monoidal category, and an interpretation of those gates is a monoidal functor into a semantic category. citeturn964242academia63turn964242academia64

For ZK, I would therefore think about a stack like

$$
\text{Circuit syntax}
\overset{F}{\longrightarrow}
\text{Polynomial constraints}
\overset{G}{\longrightarrow}
\text{Proof-system representation}.
$$

The interesting research question is whether the compiler $F$ can be made into a structure-preserving functor:

$$
F(g\circ f)=F(g)\circ F(f)
$$

and

$$
F(f\otimes g)=F(f)\otimes F(g).
$$

If so, **correctness and optimization can potentially be reasoned about locally**. Prove properties for individual gadgets, then use compositional laws to obtain properties of the whole circuit.

There is another, separate categorical connection at the cryptographic-protocol level. Work on **categorical composable cryptography** formalizes cryptographic protocols and their security using symmetric monoidal categories, showing that secure protocols can themselves compose categorically. citeturn964242search6 This is conceptually one level above circuit semantics:

$$
\boxed{
\begin{array}{c}
\text{category of gates/gadgets}\\
\downarrow\\
\text{category of constraint systems}\\
\downarrow\\
\text{category of cryptographic protocols}
\end{array}}
$$

A potentially strong research direction is therefore **categorical semantics for ZK circuit DSLs**: model gadgets as morphisms, private intermediate values through relational/existential composition, parallelism through the tensor product, copying through explicit comonoid/Frobenius structure, and circuit compilation/optimization through monoidal functors.

That could connect category theory not just to abstract ZK theory, but directly to **Circom/Halo2-style gadget composition, equivalence checking, compiler correctness, and formally verified circuit optimization**. Current Circom and Halo2 documentation already exposes the compositional gadget structure, but the categorical interpretation here is an abstraction/inference rather than something those systems presently advertise as their architecture. citeturn964242search8turn964242search12turn964242search13


---

> A potentially strong research direction is therefore **categorical semantics for ZK circuit DSLs**: model gadgets as morphisms, private intermediate values through relational/existential composition, parallelism through the tensor product, copying through explicit comonoid/Frobenius structure, and circuit compilation/optimization through monoidal functors.
>
> tell me more about that

The most interesting version of this idea is not “use category theory to describe circuits,” but **make the categorical structure the semantic contract of the ZK compiler**. Then composition, hiding, rewrites, and proof-system lowering can all be stated as structure-preserving operations. I’ll make that concrete and distinguish established mathematics from genuinely open ZK work.

```json
{"system2_search_query":[{"q":"site:arxiv.org categorical semantics circuits symmetric monoidal category string diagrams relations hypergraph categories circuits"},{"q":"site:eprint.iacr.org zero knowledge circuit compiler Circ compiler infrastructure proof systems"},{"q":"site:docs.circom.io constraints quadratic R1CS official documentation"},{"q":"site:zcash.github.io/halo2 design chips gadgets official"}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Structuring categorical semantics**

I’m framing a circuit DSL using syntax and semantic categories. Types represent wire interfaces, morphisms denote polynomial relations with existentially hidden witnesses, composition models wiring, and tensor models parallel composition. Copying and equality require explicit structural maps.

**Structured categorical semantics**

**Refining the framework**

I’m modeling syntax as a free hypergraph category, constraints as open equation systems, and semantics as relations over field assignments. Compiler correctness means translation preserves meaning; zero-knowledge remains a protocol-level property.

**Refined the framework**

</details>

```json
{"system1_search_query":[{"q":"\"category theory\" \"zero-knowledge\" circuits"},{"q":"\"categorical\" \"zero-knowledge\" circuit semantics"},{"q":"\"string diagrams\" \"zero knowledge\" circuits constraints"},{"q":"\"monoidal\" \"zero knowledge\" circuits"}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Searched 4 websites**

</details>

Yes. The strongest version of this idea is a **semantic architecture for ZK compilers**, not merely a graphical notation.

There is also some direct prior art worth knowing: a 2019 paper by Genovese, Knispel, and Fitzgerald models Boolean circuits as a free symmetric monoidal category and then constructs bicategories of “knowledge proof circuits” and “zero knowledge proof circuits.” They even point out that richer 2-cells could represent circuit rewrites. Their work is focused on compiling finite-state-machine executions to zk-SNARK circuits, rather than giving categorical semantics to arithmetic constraint DSLs, so there is still substantial room for the direction we're discussing. citeturn245539view0turn867925view0turn867925view1

## 1. Start from the semantics of a ZK circuit

Fix a prime field

$$
\mathbb F=\mathbb F_p.
$$

A conventional programming-language view says a gadget is a function

$$
f:\mathbb F^n\to\mathbb F^m.
$$

But that's slightly wrong for ZK circuits.

A constraint gadget really describes a **relation**:

$$
R_f\subseteq \mathbb F^n\times\mathbb F^m.
$$

For example, multiplication is

$$
R_{\mathrm{mul}}
=
\{((x,y),z)\mid xy=z\}.
$$

A gadget containing private auxiliary variables $w$ is

$$
R(a,b)
\iff
\exists w.\ C(a,b,w)=0.
$$

That's the key move.

The semantics of a ZK circuit becomes:

$$
\boxed{
\text{circuit}
\quad\mapsto\quad
\text{relation between its exposed wires}
}
$$

rather than merely a function.

This isn't just philosophical. Diagrammatic treatments of satisfiability already exploit exactly this phenomenon: parallel composition corresponds to conjunction, while serial composition introduces existential quantification over the connected variable. citeturn726989view2turn163953view0

---

# 2. Composition becomes existential witness hiding

Suppose

$$
f:A\to B
$$

has constraints

$$
C_f(a,b,u)=0
$$

and

$$
g:B\to C
$$

has constraints

$$
C_g(b,c,v)=0.
$$

Their composition is

$$
g\circ f:A\to C.
$$

Semantically,

$$
(a,c)\in\llbracket g\circ f\rrbracket
$$

iff

$$
\exists b,u,v.\;
C_f(a,b,u)=0
\land
C_g(b,c,v)=0.
$$

Notice what happened to $b$.

It was externally visible in each component:

$$
A\to\boxed f\to B
$$

and

$$
B\to\boxed g\to C.
$$

After wiring them together, it becomes an **internal variable**:

$$
A\to\boxed f\to b\to\boxed g\to C.
$$

Categorically:

$$
\boxed{
\text{wire composition}
=
\text{conjunction + existential quantification}
}
$$

This is exceptionally close to what a constraint compiler actually does: create intermediate variables and impose constraints linking them.

---

# 3. Parallel composition is the tensor product

If

$$
f:A\to B
\qquad
g:C\to D,
$$

then

$$
f\otimes g:
A\otimes C\to B\otimes D.
$$

For ordinary field-wire interfaces,

$$
\mathbb F^n\otimes\mathbb F^m
$$

can simply be represented structurally as

$$
\mathbb F^{n+m}.
$$

And semantically,

$$
\llbracket f\otimes g\rrbracket
=
\llbracket f\rrbracket\times
\llbracket g\rrbracket.
$$

If $f$ contributes constraints $C_f$ and $g$ contributes constraints $C_g$, the combined circuit contributes

$$
C_f\land C_g.
$$

So we obtain:

$$
\begin{array}{c|c}
\text{categorical operation} & \text{constraint meaning}\\
\hline
g\circ f & \exists\text{ shared wires}.(C_f\land C_g)\\
f\otimes g & C_f\land C_g
\end{array}
$$

That is one reason symmetric monoidal categories are such an appealing semantic foundation.

---

# 4. Why copying becomes a Frobenius structure

This gets more interesting.

Suppose one signal $x$ feeds two gadgets:

```text
        ┌──→ gadget A
x ──────┤
        └──→ gadget B
```

Ordinary string diagrams don't allow one wire magically to become two.

You introduce an explicit copying operation

$$
\delta:
\mathbb F\to
\mathbb F\otimes\mathbb F
$$

with

$$
\delta(x)=(x,x).
$$

There is also deletion

$$
\epsilon:\mathbb F\to I.
$$

Relationally,

$$
\epsilon(x)=*
$$

for every $x$.

Then take the relational converse of copying:

$$
\mu:
\mathbb F\otimes\mathbb F\to\mathbb F,
$$

where

$$
\mu(x_1,x_2)=x
$$

only when

$$
x_1=x_2=x.
$$

**Important:** $\mu$ is not field addition. It represents **wire equality**.

Together,

$$
(\mu,\eta,\delta,\epsilon)
$$

form a special commutative Frobenius structure in the usual relational model.

The practical interpretation is:

$$
\boxed{\text{a Frobenius spider = “all these ports hold the same value.”}}
$$

Hypergraph categories formalize symmetric monoidal categories equipped with exactly this kind of Frobenius structure. citeturn726989view3

The spider theorem then says that a complicated connected network of copy/equality/delete nodes can collapse into a single node.

So

```text
           ┌── x
x ──●──────┼── x
    │      └── x
    └── ...
```

doesn't require reasoning about the precise shape of the copying tree.

All that matters is connectivity:

$$
x_1=x_2=x_3=\cdots.
$$

That's extremely attractive for a circuit IR because **variable wiring becomes algebra rather than compiler bookkeeping**.

---

# 5. A tiny example

Consider

$$
f(x)=x^2+5.
$$

Categorically, build it from:

$$
\delta:\mathbb F\to\mathbb F^2
$$

followed by multiplication

$$
m:\mathbb F^2\to\mathbb F
$$

followed by adding five

$$
a_5:\mathbb F\to\mathbb F.
$$

So

$$
f=a_5\circ m\circ\delta.
$$

Diagrammatically:

```text
       ┌──────┐
   ┌──→│      │
x──●   │ MUL  ├── t ──[ +5 ]── y
   └──→│      │
       └──────┘
```

Its relational semantics is

$$
\exists t.\;
t=x^2
\land
y=t+5.
$$

An R1CS-like backend could generate

$$
x\cdot x=t
$$

and

$$
y-t-5=0.
$$

But eliminate $t$, and you get

$$
x^2-y+5=0.
$$

Same external relation.

So categorically:

$$
\exists t.\;(t=x^2\land y=t+5)
\quad\equiv\quad
x^2-y+5=0.
$$

That equation can become a **certified compiler rewrite**.

This isn't hypothetical as an optimization pattern: Circom already performs constraint simplification, including substitutions involving linear constraints and Gaussian-elimination-style simplifications. citeturn580365search32

The categorical contribution would be to give those transformations a clean denotational proof:

$$
\boxed{
\llbracket C_{\text{before}}\rrbracket
=
\llbracket C_{\text{after}}\rrbracket
}
$$

rather than trusting an ad-hoc optimization implementation.

---

# 6. The compiler becomes a functor

Now introduce three categories.

Let

$$
\mathbf{ZKSyn}
$$

be your high-level gadget language.

Let

$$
\mathbf{R1CS}
$$

be an appropriate category of open R1CS constraint systems.

And let

$$
\mathbf{Rel}_{\mathbb F}
$$

be the semantic category of field-valued relations.

Then:

$$
\begin{array}{ccc}
\mathbf{ZKSyn}
&\xrightarrow{\mathrm{Compile}}&
\mathbf{R1CS}\\
\downarrow{\mathrm{Sem}}
&&
\downarrow{\mathrm{Sat}}\\
\mathbf{Rel}_{\mathbb F}
&=&
\mathbf{Rel}_{\mathbb F}
\end{array}
$$

The main compiler-correctness theorem becomes:

$$
\boxed{
\mathrm{Sat}\circ\mathrm{Compile}
=
\mathrm{Sem}.
}
$$

In words:

> compiling a circuit and then asking what assignments satisfy the generated constraints gives exactly the same relation as interpreting the source program directly.

That's a serious compiler-correctness statement.

---

# 7. Don't make the R1CS category just ordinary relations

There is an important subtlety here.

You could define a circuit only by its external relation

$$
R\subseteq A\times B.
$$

But that loses information needed by an actual ZK backend:

- auxiliary witness variables;
- number of constraints;
- R1CS decomposition;
- lookup tables;
- gate layout;
- witness-generation order;
- optimization opportunities.

A better intermediate category would have morphisms like

$$
C:A\to B
$$

represented by

$$
(W,E)
$$

where $W$ is a finite set of internal wires and $E$ is a collection of polynomial constraints.

For example:

$$
C(x,y)=
\left(
\{t\},
\{
t-x^2=0,\;
y-t-5=0
\}
\right).
$$

Composition doesn't actually eliminate $t$.

It merely joins the constraint presentations.

Then there is a **black-box semantics functor**

$$
B:\mathbf{ConstraintPresentations}_{\mathbb F}
\to
\mathbf{Rel}_{\mathbb F}
$$

defined by

$$
B(W,E)
=
\{(a,b)\mid
\exists w\in\mathbb F^W.\ E(a,b,w)
\}.
$$

This gives you two levels:

$$
\boxed{
\begin{array}{c}
\text{intensional constraint representation}\\
\downarrow\text{ existential black-boxing}\\
\text{extensional mathematical relation}
\end{array}}
$$

That distinction is crucial for optimization.

---

# 8. A particularly important ZK issue: two semantics

This might be the strongest part of the research program.

A ZK DSL usually has two things going on simultaneously:

1. **compute the witness**;
2. **constrain the witness**.

Those aren't necessarily identical.

Consider two semantic interpretations.

### Operational semantics

$$
\mathrm{Eval}(C):
X\to Y\times W
$$

says how the witness generator computes values.

### Constraint semantics

$$
\mathrm{Constr}(C)
\subseteq
X\times Y\times W
$$

says which assignments the verifier accepts.

Ideally,

$$
\operatorname{Graph}(\mathrm{Eval}(C))
=
\mathrm{Constr}(C)
$$

modulo any intentionally nondeterministic witness values.

But real bugs happen precisely when these diverge.

Circom makes the distinction visible at the language level: some forms of signal assignment add an R1CS constraint, whereas single-arrow assignments compute values without themselves imposing the corresponding constraint, which means the programmer must supply the necessary constraint separately. citeturn580365search29

Categorically, you could express this as

$$
\begin{array}{ccc}
&\mathbf{ZKSyn}&\\
\swarrow{\mathrm{Eval}}
&&
\searrow{\mathrm{Constr}}\\
\mathbf{PartialFunctions}
&&
\mathbf{Rel}
\\
&\searrow{\mathrm{Graph}}\quad\swarrow&
\end{array}
$$

and study when the triangle commutes.

That turns **under-constrained circuits into semantic disagreement**.

---

# 9. Under-constrained versus over-constrained becomes relation inclusion

This gives an elegant verification calculus.

Suppose the intended functionality is

$$
f:X\to Y.
$$

Its graph is

$$
G_f
=
\{(x,f(x))\}.
$$

Let the actual circuit, after existentially hiding auxiliary witnesses, accept relation

$$
R_C\subseteq X\times Y.
$$

Correctness is

$$
R_C=G_f.
$$

A pure under-constraining bug gives

$$
G_f\subsetneq R_C,
$$

meaning the circuit accepts additional invalid behavior.

A pure over-constraining bug gives

$$
R_C\subsetneq G_f,
$$

meaning some valid behavior is rejected.

Some bugs can of course make the two relations incomparable.

Now order morphisms by inclusion:

$$
R\le S
\iff
R\subseteq S.
$$

Composition of relations is monotone:

$$
R\subseteq R',
\quad
S\subseteq S'
$$

implies

$$
S\circ R
\subseteq
S'\circ R'.
$$

This is powerful because **refinement proofs become compositional**.

You could prove for one gadget

$$
R_{\mathrm{impl}}\subseteq R_{\mathrm{spec}}
$$

and obtain analogous guarantees when that gadget is embedded in a larger circuit.

There is already active work on compositional formal verification of ZK circuits. In particular, Coglio, McCarthy, and Smith model prime-field constraint systems and introduce PFCS, a hierarchical formalism specifically aimed at compositional and scalable circuit verification. citeturn726989view0

That work is very close in spirit to this proposal. The categorical layer would add a general algebra of interfaces, composition, refinement, and rewriting.

---

# 10. Then optimizations become 2-cells

Instead of a plain category, use a bicategory or 2-category.

- **objects:** wire interfaces;
- **1-morphisms:** circuits;
- **2-morphisms:** proofs that one circuit rewrites/refines another.

For an equivalence-preserving rewrite,

$$
\alpha:C\Rightarrow C'
$$

means

$$
\llbracket C\rrbracket
=
\llbracket C'\rrbracket.
$$

Examples might include:

$$
x+0\Rightarrow x,
$$

$$
x\cdot1\Rightarrow x,
$$

constant folding,

linear substitution,

dead-variable removal,

copy-spider normalization,

common gadget decompositions,

and backend-specific identities.

The fundamental benefit is **contextual replacement**.

If

$$
C=C'
$$

semantically, then automatically

$$
G\circ C\circ F
=
G\circ C'\circ F.
$$

And

$$
C\otimes H
=
C'\otimes H.
$$

You prove a rewrite once and can safely use it anywhere.

The 2019 categorical zk-SNARK paper already introduces a bicategorical structure and explicitly observes that its 2-cells could have been defined as circuit rewritings; that is almost exactly the hook this research direction could develop further. citeturn245539view0

---

# 11. Start with linear circuits

Trying to build a complete calculus for arbitrary polynomial constraint systems immediately is ambitious.

A very clean starting point is the **linear fragment**.

Generators:

$$
+,\quad
0,\quad
\text{scalar multiplication},\quad
\text{copy},\quad
\text{equality}.
$$

Its semantics consists of linear relations over $\mathbb F$.

There is already deep category-theoretic machinery here: interacting Hopf algebras give a diagrammatic presentation of linear relations and support sound and complete equational reasoning about linear systems. citeturn726989view4turn643390academia38

So a research progression could be

$$
\text{linear ZK constraints}
$$

first, where a complete graphical theory is realistic, and then add

$$
\boxed{\text{multiplication}}
$$

as the nonlinear generator.

Conceptually:

$$
\text{Interacting Hopf algebra}
+
\text{multiplication gate}
+
\text{constraint/assertion structure}.
$$

That might be the mathematical core of an arithmetic-circuit calculus.

---

# 12. Add types later

Real ZK DSLs aren't just

$$
\mathbb F,\mathbb F,\mathbb F,\ldots
$$

They have concepts such as

$$
\texttt{Bool},
\quad
\texttt{UInt32},
\quad
\texttt{Field},
\quad
\texttt{ECPoint}.
$$

Categorically these can become different objects.

For example

$$
\mathsf{Bool}
$$

has an invariant

$$
b(b-1)=0.
$$

An elliptic-curve point object has an invariant

$$
y^2=x^3+ax+b.
$$

Then a gadget

$$
\mathrm{ECAdd}:
\mathrm{ECPoint}\otimes
\mathrm{ECPoint}
\to
\mathrm{ECPoint}
$$

comes with a specification relation.

This starts moving toward **refinement types categorically**:

$$
\text{object}
=
\text{wire representation + invariant}.
$$

Halo2's own architecture illustrates why such abstraction matters: its gadget layer is designed to expose more stable, reusable interfaces while hiding lower-level chip/layout details. citeturn726989view6

---

# 13. Public versus private wires

There is another useful distinction:

$$
P=\text{public},
\qquad
S=\text{secret/witness}.
$$

You could use a **colored PROP** or typed monoidal category where

$$
P\not=S.
$$

A circuit might have type

$$
P^{\otimes n}
\otimes
S^{\otimes k}
\longrightarrow
P^{\otimes m}.
$$

At the statement boundary, secret inputs are hidden:

$$
R_{\mathrm{statement}}(x,y)
\iff
\exists w.\;R_{\mathrm{circuit}}(x,w,y).
$$

So the operation

$$
\exists_S
$$

would literally implement witness hiding.

However, one conceptual warning matters:

$$
\boxed{
\text{existentially hiding a wire is NOT the same as proving zero knowledge.}
}
$$

It captures **the mathematical NP relation**.

Actual zero-knowledge is a security property of the proof protocol: the verifier must learn nothing beyond the statement. A categorical circuit semantics could establish that the correct relation was compiled, but cryptographic ZK security still needs a separate proof-system layer.

That separation is important.

---

# 14. The full architecture could look like this

Something like:

$$
\begin{array}{ccccc}
&&\mathbf{TypedZKDSL}&&\\
&\swarrow&&\searrow&\\
\mathbf{Operational}
&&&&
\mathbf{ConstraintIR}\\
&&&&\downarrow\\
&&&&
\mathbf{R1CS/PLONKish}\\
&\searrow&&\swarrow&\\
&&\mathbf{Rel}_{\mathbb F}&&
\end{array}
$$

with several commuting-diagram theorems.

### Witness correctness

$$
\operatorname{Graph}(\mathrm{Eval}(C))
\subseteq
\llbracket C\rrbracket.
$$

### Constraint soundness

$$
\llbracket C\rrbracket
\subseteq
R_{\mathrm{spec}}.
$$

### Completeness

$$
R_{\mathrm{spec}}
\subseteq
\llbracket C\rrbracket.
$$

Therefore

$$
\llbracket C\rrbracket
=
R_{\mathrm{spec}}.
$$

### Compiler correctness

$$
\llbracket\mathrm{compile}(C)\rrbracket
=
\llbracket C\rrbracket.
$$

### Optimization correctness

$$
\llbracket\mathrm{opt}(C)\rrbracket
=
\llbracket C\rrbracket.
$$

Those are crisp, machine-checkable mathematical targets.

---

# 15. What I think the strongest paper would actually be

A manageable first project would **not** attempt to categorize all of zero knowledge.

It would be something like:

> **A Hypergraph Semantics for Arithmetic Constraint Circuits**

with four concrete contributions:

1. Define a typed/free hypergraph category of arithmetic circuit syntax over $\mathbb F_p$.
2. Define a category of open prime-field constraint systems whose composition preserves internal witness variables.
3. Give a relational semantics functor
   $$
   \llbracket-\rrbracket:
   \mathbf{Constraints}
   \to
   \mathbf{Rel}_{\mathbb F_p}
   $$
   and prove compilation compositionality.
4. Define and mechanically verify a collection of semantics-preserving circuit rewrites, then show they reduce R1CS constraint counts.

The next paper could add the **dual operational/constraint semantics** and characterize under-constrained gadgets via failure of the semantic diagram to commute.

That, to me, is considerably more interesting than simply saying “ZK circuits form a symmetric monoidal category.” It would make category theory responsible for an actual security/compiler invariant:

$$
\boxed{
\text{the constraint system accepted by the verifier
means exactly what the source programmer wrote.}
}
$$

That is a concrete problem in current ZK engineering, and existing formal-verification work confirms that compositional reasoning about prime-field circuit constraints is already useful. citeturn726989view0


---

> EVM in ZKVM what does it mean?

**EVM** means **Ethereum Virtual Machine**. It is the execution environment that runs Ethereum smart contracts.

So when someone says **“EVM in a zkVM”**, they usually mean:

> Execute EVM programs or Ethereum transactions inside a virtual machine whose execution can be proven with zero-knowledge proofs.

The key distinction is:

- **EVM:** executes Ethereum bytecode.
- **zkVM:** executes programs and produces a cryptographic proof that the execution was correct.
- **zkEVM:** a zkVM specifically designed to reproduce or prove EVM execution.

For example, suppose an Ethereum transaction executes:

$$
\text{state}_0
\xrightarrow{\text{EVM execution}}
\text{state}_1
$$

Normally, every Ethereum node re-executes the transaction to verify that `state₁` is correct.

With a zkEVM, a prover instead computes:

$$
(\text{execution trace},\ \text{proof})
$$

and produces something like

$$
\pi =
\operatorname{Prove}(
\text{state}_0,
\text{transactions},
\text{state}_1
)
$$

The verifier checks:

$$
\operatorname{Verify}(\pi)=\text{true}
$$

without re-running all the EVM instructions.

Conceptually:

```text
Ethereum transaction
        ↓
     EVM bytecode
        ↓
 ┌─────────────────┐
 │      zkEVM      │
 │                 │
 │ ADD             │
 │ SLOAD           │
 │ SSTORE          │
 │ CALL            │
 │ KECCAK256       │
 │ ...             │
 └─────────────────┘
        ↓
 new Ethereum state
        +
   ZK proof π
```

The difficult part is that the EVM has many semantics that must be encoded into constraints: stack operations, memory, storage, gas accounting, opcodes, contract calls, Keccak hashing, state transitions, and so on.

In terms of our previous **categorical circuit semantics** discussion, you can think of each EVM instruction as a state-transition gadget:

$$
\mathrm{ADD}:
\mathrm{VMState}
\rightarrow
\mathrm{VMState}
$$

and an entire program as composition:

$$
\mathrm{SSTORE}
\circ
\mathrm{ADD}
\circ
\mathrm{PUSH}
\circ
\mathrm{SLOAD}.
$$

The zkEVM compiler/prover then translates those transitions into polynomial constraints whose satisfaction proves that the EVM execution was valid.

One terminology trap: **not every zkVM is a zkEVM**. A zkVM might prove RISC-V, WASM, MIPS, or a custom instruction set. A zkEVM specifically targets Ethereum/EVM semantics.


---

> papers about all of this

I’ll group the literature into four layers: categorical circuit semantics, formal verification of ZK circuits, proof-system foundations, and zkVM/zkEVM execution. The useful goal is a reading path, not just a pile of titles.

```json
{"system1_search_query":[{"q":"site:arxiv.org category theory circuits hypergraph categories string diagrams arithmetic circuits relations paper"},{"q":"site:arxiv.org zero knowledge circuits category theory zkSNARK circuits categorical paper"},{"q":"site:arxiv.org PFCS prime field constraint systems compositional verification zero knowledge circuits"},{"q":"site:arxiv.org categorical composable cryptography paper symmetric monoidal categories"}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Searched 5 websites**

</details>

The closest paper to the exact intersection is **“Mapping finite state machines to zk-SNARKS Using Category Theory” (2019)**. But for a new research project, the more important combination is that paper + compositional circuit verification + hypergraph/string-diagram rewriting + modern zkVM work such as Jolt/HyperNova.

```json
{"system1_search_query":[{"q":"site:eprint.iacr.org Lasso lookup argument Setty Thaler Wahby 2023"},{"q":"site:eprint.iacr.org customizable constraint systems CCS Setty 2023 552"},{"q":"site:arxiv.org rewriting free hypergraph categories Bonchi Gadducci Kissinger Sobocinski Zanasi 2017"}],"response_length":"medium"}
```

<details><summary>💭 Thinking</summary>

**Selecting foundational papers**

I’m prioritizing peer-reviewed and influential work spanning circuit semantics, SNARKs, recursive proofs, zkVMs, EVM translation, and formal verification. I’ll distinguish foundational papers from newer preprints where that matters.

**Selected foundational papers**

</details>

```json
{"system1_search_query":[{"q":"site:eprint.iacr.org Cairo CPU Algebraic Intermediate Representation whitepaper StarkWare 2021"},{"q":"site:starkware.co Cairo whitepaper PDF CPU AIR 2021"}],"response_length":"medium"}
```

<details><summary>💭 Thinking</summary>

**Building the reading path**

I’m organizing this from categorical semantics and rewriting through proof systems, recursive arguments, zkVMs, and zkEVM verification. I’m separating foundational papers from newer system-oriented work and preprints.

**Built the reading path**

**Searched 3 websites**

</details>

Yes. If your target is the intersection

$$
\boxed{\text{Category Theory}
\rightarrow \text{ZK circuits}
\rightarrow \text{constraint systems}
\rightarrow \text{zkVM}
\rightarrow \text{zkEVM}}
$$

these are the papers I would use as the core bibliography.

1. **Genovese, Knispel, Fitzgerald — “Mapping finite state machines to zk-SNARKS Using Category Theory” (2019).** This is the most directly relevant paper to your original idea. It models Boolean circuits categorically, constructs categorical transformations from state machines into circuits suitable for zk-SNARKs, and proves pseudofunctoriality of the constructions. Start here because it shows that “category theory → ZK circuit compiler” is already a legitimate research direction, while leaving arithmetic-circuit semantics and modern zkVMs largely open. citeturn295389academia81

2. **Coglio, McCarthy, Smith — “Formal Verification of Zero-Knowledge Circuits” (2023).** Probably the most important paper for the project we were discussing. It formalizes prime-field circuit correctness, models R1CS, and introduces **PFCS (Prime Field Constraint Systems)**, a hierarchical constraint representation specifically intended to support compositional verification. This is very close to the problem a categorical semantics could attack. citeturn295389search9

3. **Fong, Spivak — “Hypergraph Categories” (2018).** This gives the categorical machinery for treating systems with wires that can copy, merge, discard, and connect. Hypergraph categories are symmetric monoidal categories equipped with special commutative Frobenius structures—the exact structure behind the “copying/equality spiders” we discussed. citeturn551176academia32

4. **Bonchi, Sobociński, Zanasi — “Interacting Hopf Algebras” (2014).** Extremely relevant mathematically. It gives an equational/string-diagram calculus whose semantics is the PROP of **linear relations**. Since the linear portion of R1CS/Plonkish constraints is essentially linear algebra over finite fields, this is a natural mathematical starting point for a categorical theory of ZK constraints. citeturn310262academia3

5. **Baez, Erbele — “Categories in Control” (2014).** Another useful bridge between string diagrams and relations. It shows how diagrams with addition, scalar multiplication, duplication, deletion, cups and caps can represent linear relations. Replace their field with $\mathbb F_p$, and much of the intuition becomes directly useful for circuit semantics. citeturn310262academia0

6. **Zanasi — “Rewriting in Free Hypergraph Categories” (2017)** and the later **Bonchi et al. “String Diagram Rewrite Theory I” (2020/2022).** These are what you want if your goal is not merely semantics but **verified circuit optimization**. They connect equations of string diagrams/Frobenius structures to concrete hypergraph rewriting, providing machinery for reasoning about semantics-preserving transformations. citeturn551176academia30turn551176academia33

7. **Broadbent, Karvonen — “Categorical Composable Cryptography” (2021/2022).** This moves category theory one layer upward—from circuits to cryptographic protocols and security definitions. They formulate simulation-based composable cryptography categorically and show that secure protocols form a symmetric monoidal category. This is useful for understanding where categorical **circuit correctness** ends and categorical **cryptographic security** begins. citeturn295389search6turn295389search19

8. **Ben-Sasson, Chiesa, Genkin, Tromer, Virza — “SNARKs for C: Verifying Program Executions Succinctly and in Zero Knowledge” (2013).** This is an important ancestor of today's zkVM idea. Instead of manually writing one circuit for one application, they compile program execution using the TinyRAM machine and prove correct execution of programs compiled from C. The conceptual shift is:
   $$
   \text{program}\rightarrow\text{machine execution}\rightarrow\text{constraints}\rightarrow\text{proof}.
   $$
   citeturn637565search15

9. **Ben-Sasson, Bentov, Horesh, Riabzev — “Scalable, Transparent, and Post-Quantum Secure Computational Integrity” (2018).** This is the foundational practical **STARK** paper. It matters for zkVMs because AIR-style execution traces are a major alternative to R1CS/Plonkish circuit representations, particularly when representing repeated VM state transitions. citeturn254038search0

10. **Setty et al. — “Customizable Constraint Systems for Succinct Arguments” (2023).** Very important for your categorical idea. **CCS** generalizes R1CS, Plonkish constraints, and AIR under one formal constraint-system abstraction. If you wanted one target semantic category rather than separately developing categories for R1CS, PLONK and AIR, CCS is something I would study carefully. citeturn551176search1

11. **Kothapalli, Setty — “HyperNova: Recursive Arguments for Customizable Constraint Systems” (2023–2026).** HyperNova combines CCS with recursive/folding proofs. Particularly relevant to your EVM question: the paper explicitly discusses proving stateful machines such as **EVM and RISC-V**, with proving cost dependent on the instruction actually executed rather than requiring one giant universal circuit. citeturn254038search3

12. **Arun et al. — “Jolt: SNARKs for Virtual Machines via Lookups” (2023)** together with **Setty, Thaler, Wahby — “Unlocking the Lookup Singularity with Lasso” (2023).** These are essential modern zkVM papers. Jolt's core idea is to encode much of an instruction set through gigantic but structured lookup tables rather than conventional gate-by-gate arithmetic circuits; Lasso supplies the lookup argument. This gives you a very different categorical question: perhaps VM instructions should be primitive morphisms with **lookup semantics**, rather than decomposed immediately into arithmetic gates. citeturn551176search9turn551176search0

13. **Arun et al. — “Nebula: Proving Machine Executions Using Folding Schemes” (2024).** Directly about zkVMs and long-running machine execution. It studies incremental/folding-based proof generation to address the memory costs of proving long executions. This is especially relevant if your categorical model eventually includes sequential machine-state transitions and recursion. citeturn440152search9

14. **Hassanzadeh-Nazarabadi, Taheri-Boshrooyeh — “Constraint-Level Design of zkEVMs: Architectures, Trade-offs, and Evolution” (2025/2026).** This recent survey is almost tailor-made for connecting the previous papers to the **EVM**. It examines how zkEVMs translate irregular EVM execution into R1CS, Plonkish, AIR and related constraint architectures, and identifies formal equivalence between EVM semantics and generated constraints as an open problem. citeturn440152academia41turn440152search23

15. **Huang et al. — “Towards Automated Formal Verification of zkEVMs Using LLM-Guided Constraint Synthesis” (2026).** Very recent preprint. It focuses specifically on checking that zkEVM opcode implementations correctly model EVM state transitions, using symbolic constraints/SMT reasoning. The motivating failure mode is exactly the one relevant to your proposed semantics: a proof system can be perfectly sound while proving the **wrong constraint encoding of the EVM**. citeturn440152academia40

For **your particular research direction**, I would read them in this order:

$$
\boxed{
1\rightarrow3\rightarrow4\rightarrow2\rightarrow6
\rightarrow10\rightarrow11\rightarrow12\rightarrow14
}
$$

That sequence takes you through:

$$
\begin{aligned}
&\text{categorical ZK circuits}\\
&\downarrow\\
&\text{hypergraph/Frobenius semantics}\\
&\downarrow\\
&\text{linear relations}\\
&\downarrow\\
&\text{formal ZK constraint verification}\\
&\downarrow\\
&\text{verified diagram rewriting}\\
&\downarrow\\
&\text{R1CS/Plonkish/AIR unification}\\
&\downarrow\\
&\text{recursive VM execution}\\
&\downarrow\\
&\text{modern zkVMs}\\
&\downarrow\\
&\text{zkEVM constraint semantics}.
\end{aligned}
$$

And there is a fairly clear **research gap** at the intersection. The literature has categorical circuit models, compositional formal verification of ZK constraints, mature categorical rewriting theory, unified constraint formalisms such as CCS, and increasingly sophisticated zkVM/zkEVM architectures—but these pieces have not, as far as I can determine from the literature above, been unified into a **categorical denotational semantics for modern arithmetic ZK DSL/VM compilation with machine-checked semantics-preserving rewrites**. citeturn295389academia81turn295389search9turn551176academia33turn551176search1turn440152academia41

A plausible thesis-shaped statement is:

$$
\boxed{
\textbf{Categorical Semantics and Verified Compilation for Zero-Knowledge Virtual Machines}
}
$$

where you construct something like

$$
\mathbf{EVM/VM}
\xrightarrow{F}
\mathbf{ZKCircuit}
\xrightarrow{G}
\mathbf{CCS}
\xrightarrow{H}
\mathbf{Rel}_{\mathbb F_p}
$$

and prove

$$
HGF(\text{program})
=
\llbracket\text{program}\rrbracket_{\mathrm{VM}}.
$$

That equation says: **the relation proved cryptographically by the generated constraints is exactly the operational semantics of the original VM program.**

That is the connection between category theory, ZK circuits, zkVMs and the EVM that I would investigate.


---

> modelling it as a VM  / which instruction set / how is the compiler built? how is the interpreter? current applications

A zkVM can be built in two very different ways: **prove a native VM instruction set directly**, or **run/compile another VM such as the EVM inside a zk-friendly VM**. That choice determines the ISA, compiler pipeline, interpreter/executor, and proof cost.

```json
{"system1_search_query":[{"q":"site:docs.succinct.xyz SP1 RISC-V zkVM compiler execution official docs"},{"q":"site:dev.risczero.com zkVM RV32IM instruction set compiler executor official docs"},{"q":"site:docs.zkm.io zkMIPS instruction set zkVM official docs"},{"q":"site:docs.polygon.technology zkEVM architecture EVM opcodes state machine official"}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Clarifying zkVM execution**

I’m framing the explanation around compilation, host–guest separation, instruction execution, trace recording, and proof constraints. I’ll also distinguish an EVM interpreter running inside a zkVM from the zkVM’s own execution engine.

**Clarified zkVM execution**

**Searched 20 websites**

</details>

A useful way to see the stack is that there may actually be **two virtual machines**:

```text
Solidity → EVM bytecode → EVM interpreter
                         ↓ compiled
                    RISC-V program
                         ↓
                     RISC-V zkVM
                         ↓
                execution trace + proof
```

So “EVM in a zkVM” often means proving the execution of an **EVM interpreter**, rather than making EVM opcodes the zkVM’s native ISA. Succinct’s RSP is a concrete example: Ethereum block execution code from Reth runs as the SP1 guest.

<details><summary>💭 Thinking</summary>

**Explaining zkVM layers**

I’ll organize this through four layers: source compilation, the instruction set, execution and trace generation, and arithmetization. I’ll also separate ordinary software interpretation from the proof system’s constraint representation.

**Explained zkVM layers**

</details>

Yes. The cleanest mental model is to separate **four layers**:

$$
\boxed{
\text{source program}
\rightarrow
\text{ISA}
\rightarrow
\text{VM execution trace}
\rightarrow
\text{ZK constraints/proof}
}
$$

For Ethereum, there may be an additional EVM layer:

$$
\boxed{
\text{Solidity}
\rightarrow
\text{EVM bytecode}
\rightarrow
\text{EVM interpreter}
\rightarrow
\text{RISC-V}
\rightarrow
\text{zkVM proof}
}
$$

That distinction explains most modern zkVM architectures.

## 1. What does it mean to model computation as a VM?

Forget ZK for a moment. A VM is essentially a state transition system.

Define machine state

$$
S_t =
(
pc_t,
registers_t,
memory_t,
input_t,
output_t,
\ldots
).
$$

An instruction defines a transition

$$
\operatorname{step}:
I\times S\rightarrow S.
$$

For example,

```text
ADD x3, x1, x2
```

means roughly

$$
x_3'=x_1+x_2,
\qquad
pc'=pc+4
$$

while everything else remains unchanged.

A program execution is therefore

$$
S_0
\xrightarrow{i_0}
S_1
\xrightarrow{i_1}
S_2
\rightarrow\cdots\rightarrow
S_n.
$$

The crucial zkVM move is:

> Don't merely execute this sequence. Produce a proof that every transition obeyed the ISA semantics.

So the prover constructs an **execution trace**

$$
T=
\begin{pmatrix}
S_0\\
S_1\\
S_2\\
\vdots\\
S_n
\end{pmatrix}
$$

and the proof system establishes something equivalent to

$$
\mathrm{Initial}(S_0)
\land
\bigwedge_{t=0}^{n-1}
\mathrm{ValidStep}(S_t,S_{t+1})
\land
\mathrm{ValidMemory}(T)
\land
\mathrm{Final}(S_n).
$$

Cairo describes this architecture particularly explicitly: its VM fetches, decodes and executes instructions while producing the execution trace used as input to its AIR proof system. citeturn174238search0turn174238search24

So a zkVM is essentially a **provable state machine**.

---

# 2. Which instruction set?

There isn't one universal zkVM ISA.

Today you see several approaches:

| System/style | ISA |
|---|---|
| SP1 | RISC-V RV32IM target |
| RISC Zero | RISC-V RV32IM |
| Jolt | RISC-V, current implementation RV64IMAC |
| Ethereum zkVM standardization | RV64IM + Zicclsm |
| Ziren | MIPS32r2 |
| Cairo | Custom ZK-optimized ISA |
| Native zkEVM | EVM instructions themselves |

SP1 currently compiles guest programs using the `riscv32im-succinct-zkvm-elf` target, while RISC Zero documents an RV32IM execution model. citeturn171291view0turn595538search1 Ziren instead deliberately targets MIPS32r2. citeturn174238search2turn174238search3

Cairo takes the opposite philosophy: rather than reuse a physical CPU ISA, it defines a custom ZK-oriented ISA and memory model explicitly optimized for proving. citeturn174238search0

### Why is RISC-V becoming important?

The important development in **2026** is the Ethereum Foundation's zkVM interoperability work.

In February 2026, it published zkVM Standards v0 specifying

$$
\boxed{\text{RV64IM + Zicclsm}}
$$

as the common target architecture for RISC-V zkVMs used in the Ethereum execution-proof effort. The same standard also specifies common C interfaces for zkVM precompiles and I/O. citeturn171291view1

That doesn't mean every zkVM has already migrated to RV64. SP1 and RISC Zero documentation still exposes RV32-based architectures. Rather, RV64IM is becoming a **common Ethereum-oriented interoperability target**. citeturn171291view0turn595538search1

---

# 3. Why use something like RISC-V at all?

Suppose your application is ordinary Rust:

```rust
fn verify_block(block: Block) -> StateRoot {
    ...
}
```

Without a zkVM you might need to manually turn it into

```text
arithmetic circuit
lookup tables
memory constraints
range checks
hash gadgets
...
```

That's painful.

Instead:

```text
Rust
 │
 │ rustc / LLVM
 ▼
RISC-V
 │
 ▼
zkVM
 │
 ▼
proof
```

The zkVM author only has to implement and prove the semantics of the instruction set once.

Then potentially millions of programs reuse it.

That is the big abstraction:

$$
\boxed{
\text{prove the CPU once}
\quad\Rightarrow\quad
\text{prove arbitrary programs running on that CPU}.
}
$$

Jolt describes a zkVM precisely in terms of a program expressed in the assembly language of a particular ISA, with a front end reducing valid VM execution to lower-level proof constraints. Jolt's distinctive design uses structured lookup arguments for much of the ISA semantics. citeturn980706view5

---

# 4. How is the compiler built?

For a RISC-V zkVM, surprisingly little of the **front half** of the compiler needs to be exotic.

For SP1, for example:

```text
Rust
 ↓
Rust compiler
 ↓
RISC-V target
 ↓
ELF executable
```

SP1's `cargo prove build` ultimately performs a Cargo build against its custom RISC-V zkVM target and produces an ELF executable that the zkVM can run. citeturn171291view0

Conceptually, the full compiler stack is closer to:

```text
            source
              │
       ┌──────▼──────┐
       │ Rust / C /  │
       │ C++ compiler│
       └──────┬──────┘
              │
              ▼
        compiler IR
              │
              ▼
        RISC-V backend
              │
              ▼
          RISC-V ELF
              │
       ┌──────▼──────┐
       │ zkVM loader │
       └──────┬──────┘
              │
              ▼
      program memory image
```

SP1 explicitly supports programs written in languages that can compile to RISC-V, including Rust, C and C++. citeturn980706view3

The unusual part is mainly what happens **after** compilation.

---

# 5. How does the interpreter/executor work?

Imagine implementing a tiny RISC-V interpreter:

```text
while !halted:
    instruction = memory[pc]
    decoded = decode(instruction)

    execute(decoded)

    pc = next_pc
```

Internally:

```text
FETCH
  ↓
DECODE
  ↓
read registers
  ↓
execute ALU / memory / branch
  ↓
write result
  ↓
next PC
```

But a zkVM executor also records enough information to later prove everything.

For every instruction it might produce something conceptually like

$$
(
pc,
opcode,
rs_1,
rs_2,
rd,
value_1,
value_2,
result,
memoryAddress,
memoryValue
).
$$

Then specialized proof machinery checks different parts.

```text
execution
    │
    ├── CPU constraints
    ├── ADD/SUB constraints
    ├── MUL constraints
    ├── branch constraints
    ├── memory consistency
    ├── range checks
    ├── lookup arguments
    └── public I/O
```

Ziren, for example, describes instructions producing CPU/ALU events that feed specialized proof “chips,” each with associated constraints. citeturn174238search16

RISC Zero similarly separates execution from proving: an ELF guest is executed and its session recorded, and then the prover proves that session, producing a cryptographic receipt. citeturn980706view2

This distinction is important:

$$
\boxed{
\text{executor generates witness}
\qquad
\text{prover proves witness consistency}.
}
$$

The executor itself does **not** have to be trusted.

If it creates an invalid trace, the proof should fail.

---

# 6. Now put the EVM inside it

Here's where it gets interesting.

Ethereum already has its own VM:

```text
Solidity
   ↓
 solc
   ↓
EVM bytecode
   ↓
EVM
```

An EVM program might contain instructions such as

```text
PUSH
ADD
MLOAD
SLOAD
CALL
SSTORE
KECCAK256
...
```

You have two fundamentally different options for proving this execution.

---

## Option A — build a native zkEVM

Directly create proof constraints for EVM semantics:

```text
EVM bytecode
      │
      ▼
┌──────────────┐
│ zkEVM        │
│ constraints  │
│              │
│ ADD          │
│ SLOAD        │
│ CALL         │
│ KECCAK       │
│ ...          │
└──────┬───────┘
       ▼
      proof
```

Here

$$
\mathrm{EVM\ opcode}
\rightarrow
\mathrm{ZK\ constraints}
$$

directly.

There is no RISC-V CPU between the EVM and proof system.

This is the traditional “specialized zkEVM” approach.

---

# 7. Option B — put an EVM interpreter inside a general zkVM

Instead, write the EVM implementation in ordinary software.

For example, `revm` is a Rust EVM interpreter, with separate implementations of EVM bytecode instructions, stack, memory, precompiles, execution context and state handling. citeturn444905search1turn444905search2

Then:

```text
Ethereum block
       │
       ▼
      Reth
       │
       ▼
 EVM interpreter
    written
    in Rust
       │
       │ compile
       ▼
 RISC-V binary
       │
       ▼
    SP1
       │
       ▼
   ZK proof
```

Now you aren't proving

$$
\mathrm{EVM}
$$

directly.

You're proving

$$
\boxed{
\text{a RISC-V machine correctly executed
software that implements the EVM}.
}
$$

That is a major architectural shift.

---

# 8. This is exactly what RSP demonstrates

Succinct's **Reth Succinct Processor (RSP)** combines Reth with SP1.

It has a host that prepares Ethereum execution data and a client program that executes inside SP1. Its purpose is to generate proofs of Ethereum and OP Stack block execution. citeturn980706view4

So conceptually:

```text
Ethereum block
     │
     ▼
Reth execution logic
     │
     ▼
EVM transactions
     │
     ▼
Rust execution program
     │
  compile
     ▼
   RISC-V
     │
     ▼
     SP1
     │
     ▼
proof that the Ethereum
block was executed correctly
```

This is probably the architecture you were getting at by **“EVM in a zkVM.”**

---

# 9. There are actually two interpreters

This is a subtle but useful observation.

In this design:

```text
               interpreter #1
EVM bytecode ────────────────→ EVM state
                  REVM

                      │
                compiled into
                      ▼

                 RISC-V code

                      │
               interpreter #2
                      ▼
                zkVM executor
```

So the zkVM is effectively proving execution of an interpreter running another ISA.

Formally:

$$
\operatorname{EVMstep}
$$

is implemented as a program

$$
P_{\mathrm{EVM}}
$$

over RISC-V.

And the zkVM proves

$$
\operatorname{RISCVExec}
(P_{\mathrm{EVM}},input,output).
$$

Compiler correctness plus interpreter correctness should imply

$$
\operatorname{RISCVExec}
(P_{\mathrm{EVM}},x,y)
\iff
\operatorname{EVMExec}(x,y).
$$

**That equation is an excellent formal-verification/category-theory research target.**

---

# 10. What about performance?

The obvious problem is interpretation overhead.

One EVM operation may become many RISC-V instructions:

$$
1\;\mathrm{EVM\ opcode}
\rightarrow
10,100,1000,\ldots\;\mathrm{RISC\ instructions}.
$$

Cryptographic operations are particularly problematic.

That's why zkVMs introduce **precompiles/accelerators**.

Instead of proving thousands of ordinary instructions for something like SHA-256 or elliptic-curve arithmetic, the VM can invoke a specialized proof gadget.

RISC Zero, for example, exposes specialized circuits/precompiles for operations including SHA-256, elliptic-curve operations and modular arithmetic; SP1 likewise provides optimized precompiles for expensive cryptographic operations. citeturn595538search3turn675580search15

So practically:

```text
ordinary computation
       ↓
RISC-V

expensive crypto
       ↓
special ZK chip/precompile
```

This looks remarkably similar to CPU hardware accelerators.

---

# 11. ZKsync OS is another interesting architecture

As of August 2026, ZKsync OS's Developer Preview provides a particularly clean version of the idea.

Its state-transition logic is written in Rust and compiled to **two targets**:

```text
                  ZKsync OS
                   Rust
                 /      \
                /        \
              x86       RISC-V
               │           │
          sequencer     Airbender
          execution      zkVM
               │           │
            result       proof
```

The same source program is used for normal execution and provable execution. Its execution environments are interpreters, and the current Developer Preview provides an EVM-equivalent environment. citeturn980706view1

That's important architecturally because it attacks the classic problem:

$$
\boxed{
\text{code that executes}
\neq
\text{code represented by the ZK circuit}.
}
$$

Instead they aim for

$$
\boxed{
\text{same source}
\rightarrow
\begin{cases}
\text{fast native execution}\\
\text{provable RISC-V execution}
\end{cases}}
$$

which reduces semantic duplication. citeturn980706view1

---

# 12. Current applications

As of **August 2026**, the major applications fall into several categories.

**Blockchain execution proofs** are probably the biggest one. Instead of every verifier re-executing a block, a prover can execute it and supply a succinct proof of the resulting state transition. Ethereum's own L1 zkEVM effort explicitly targets this model. The current workstream is pursuing optional execution proofs before eventually moving toward mandatory proof-based execution verification. citeturn980706view0turn468376search2

**ZK rollups** use the same basic idea to execute batches offchain and prove the resulting state transition back to Ethereum. citeturn468376search6

**Proving existing blockchain software** is becoming increasingly important: rather than reimplement an execution client as hand-written circuits, systems such as RSP aim to prove ordinary Ethereum execution software running inside a general zkVM. citeturn980706view4

**Coprocessors, light clients, bridges and oracles** use zkVMs to perform expensive computations offchain and submit only their outputs and proofs onchain. Succinct currently lists coprocessors, ZK light clients, oracles, OP Stack proving and Ethereum execution among SP1's practical use cases. citeturn468376search1

There are also **general verifiable-compute markets**. Boundless, built around RISC Zero technology, lets an application submit an offchain computation for proving and then verify the returned proof in a smart contract. citeturn499560search1

One nuance: despite the “ZK” name, many of these applications are primarily using zkVMs for **succinct computational integrity**, not secrecy. Zero-knowledge/privacy can be added by keeping inputs private, but proving an Ethereum block correctly executed is mainly a validity problem.

---

# 13. And this circles directly back to category theory

Here is where your earlier research direction gets considerably more concrete.

Treat the ISA instructions as **generators**:

$$
\mathrm{ADD},\mathrm{MUL},\mathrm{LOAD},
\mathrm{STORE},\mathrm{JUMP},\ldots
$$

Each is a morphism on machine state:

$$
\mathrm{ADD}:S\to S.
$$

A RISC-V program

```text
LOAD
LOAD
ADD
STORE
```

becomes

$$
P
=
\mathrm{STORE}
\circ
\mathrm{ADD}
\circ
\mathrm{LOAD}
\circ
\mathrm{LOAD}.
$$

Then you potentially have several semantic maps:

$$
\mathbf{Source}
\xrightarrow{\text{compiler}}
\mathbf{RISC\!-\!V}
\xrightarrow{\text{arithmetization}}
\mathbf{Constraints}
\xrightarrow{\text{semantics}}
\mathbf{Rel}_{\mathbb F}.
$$

For the EVM case, insert another layer:

$$
\mathbf{EVM}
\xrightarrow{\text{interpreter}}
\mathbf{RISC\!-\!V}
\xrightarrow{\text{zkVM}}
\mathbf{Constraints}.
$$

Now the desired theorem is a commuting diagram:

$$
\boxed{
\llbracket
ZKCompile(
EVMInterpreter(P)
)
\rrbracket
=
\llbracket P\rrbracket_{\mathrm{EVM}}
}
$$

In plain English:

> **The constraints proved by the zkVM describe exactly the same state transition as the Ethereum specification.**

That's much more interesting than simply proving that a circuit is satisfiable. It ties together **programming-language semantics, compiler verification, virtual-machine semantics, categorical composition, and ZK soundness**.

And the 2026 Ethereum direction makes this less hypothetical: the Ethereum Foundation is now explicitly standardizing a common RV64IM-based zkVM target and interfaces with the aim of using zkVMs for Ethereum block execution proofs. citeturn171291view1turn980706view0

If you're approaching this as a research topic, **the EVM → interpreter → RISC-V → constraint-system pipeline is probably the most fertile place to focus**. It gives you a concrete compiler/interpreter whose semantic preservation could be formulated categorically and then machine-checked.

