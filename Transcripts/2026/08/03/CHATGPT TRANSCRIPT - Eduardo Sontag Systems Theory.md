# Eduardo Sontag Systems Theory

- URL: https://chatgpt.com/c/6a405dc2-9a38-83ea-af70-49d4b0bb194c
- Created: 2026-06-27T23:33:44.249Z

---

> Mathematical systems theory Eduardo Sontag

I’ll treat this as a request for a concise orientation to Eduardo Sontag’s work in mathematical systems theory, including key texts and themes.

```json
{"system1_search_query":[{"q":"Eduardo D. Sontag mathematical systems theory key works Mathematical Control Theory"},{"q":"Eduardo Sontag Rutgers mathematical systems theory nonlinear control input-to-state stability"},{"q":"Eduardo Sontag Mathematical Control Theory Deterministic Finite Dimensional Systems PDF"}],"response_length":"medium"}
```

<details><summary>💭 Thinking</summary>

**Looking for a citation source**

I think I need to find a reliable source, like the official Sontag site, and include a citation in the answer. I’ll search for a trustworthy webpage to ensure the information is accurate. Let's see what's available.

</details>

```json
{"system1_search_query":[{"q":"site:sontaglab.org Eduardo D Sontag biography research interests systems control biology"},{"q":"Eduardo D. Sontag Northeastern University biography control systems biology"}],"response_length":"medium"}
```

Eduardo D. Sontag is a central figure in **mathematical systems and control theory**, especially nonlinear control, stability theory, and later systems biology.

The text you probably want is:

**Eduardo D. Sontag, _Mathematical Control Theory: Deterministic Finite Dimensional Systems_**  
Springer, 2nd ed., 1998, in the *Texts in Applied Mathematics* series. It is a theorem-proof style introduction to finite-dimensional control systems: state-space models, controllability, observability, stabilization, feedback, nonlinear systems, and Lie-algebraic methods. Springer lists it as a 1998 text by Sontag with DOI `10.1007/978-1-4612-0577-7`. citeturn620734search0

Sontag also hosts a PDF of the book on his own site; the description says it introduces “basic concepts and results of mathematical control and system theory” and is based on courses he taught over many years. citeturn620734search2

Core topics associated with Sontag’s systems-theory work:

| Topic | Role |
|---|---|
| **Control systems** | Systems of the form \(\dot{x}=f(x,u)\), where inputs \(u\) steer state \(x\). |
| **Controllability / reachability** | Whether one can drive the system from one state to another. |
| **Observability** | Whether internal state can be inferred from outputs. |
| **Feedback stabilization** | Designing \(u=k(x)\) so a desired equilibrium becomes stable. |
| **Control-Lyapunov functions** | Lyapunov methods for constructive nonlinear feedback. |
| **Input-to-state stability, ISS** | A major nonlinear stability framework introduced by Sontag; it formalizes how bounded or decaying inputs affect state behavior. citeturn620734search4turn620734search16 |
| **Systems biology** | Later work applies control/dynamical-systems tools to molecular biology, synthetic biology, cancer, and immunology. Northeastern lists his research focus as feedback control theory, systems biology, cancer, and biomedicine. citeturn811575search1 |

A compact way to frame his contribution: **Sontag helped put nonlinear control theory on a rigorous mathematical footing, especially by connecting state-space control, Lyapunov methods, feedback design, and robustness to inputs.** His later work extends the same systems viewpoint to biological networks. The National Academy of Sciences lists his interests across control and dynamical systems theory, theoretical computer science, machine learning, cancer, immunology, and molecular/synthetic/computational biology. citeturn811575search3


---

> Willems polderman

I’ll map this to the Willems–Polderman systems-theory text and how it differs from Sontag’s control-theoretic framing.

```json
{"system1_search_query":[{"q":"Willems Polderman Introduction to Mathematical Systems Theory behavioral approach"},{"q":"J.C. Willems J.W. Polderman mathematical systems theory behavioral approach PDF"}],"response_length":"short"}
```

You likely mean:

**Jan Willem Polderman & Jan C. Willems, _Introduction to Mathematical Systems Theory: A Behavioral Approach_**  
Springer, 1998, *Texts in Applied Mathematics*, Vol. 26. Springer lists the authors as **Jan Willem Polderman** and **Jan C. Willems**, with DOI `10.1007/978-1-4757-2953-5`. citeturn917704search0

This is the canonical text for the **behavioral approach** to mathematical systems theory. Instead of starting with the standard input/state/output form,

\[
\dot{x}=Ax+Bu,\qquad y=Cx+Du,
\]

Willems’ behavioral view treats a system as a **set of trajectories** satisfying laws or constraints. In this view, variables are not automatically divided into “inputs” and “outputs”; that distinction can be imposed later when useful. The University of Twente summary describes the book as covering modeling, analysis, and control of **linear time-invariant systems**, with systems viewed as dynamical relations between **manifest** and **latent** variables. citeturn917704search6

Core ideas:

| Concept | Meaning |
|---|---|
| **Behavior** \(\mathcal{B}\) | The set of all signal trajectories compatible with the system laws. |
| **Manifest variables** | Variables externally visible in the model. |
| **Latent variables** | Auxiliary/internal variables, such as states. |
| **Kernel representation** | A system described by differential equations such as \(R(d/dt)w=0\). |
| **Controllability** | Ability to concatenate or patch compatible trajectories. |
| **Autonomy** | Behavior determined by its own laws, without free external variables. |
| **Elimination** | Removing latent variables to obtain equations only in manifest variables. |

Compared with **Sontag**, the difference is roughly:

| Sontag | Willems–Polderman |
|---|---|
| Classical control-theory orientation | Behavioral systems-theory orientation |
| Usually starts from state-space systems | Starts from sets of trajectories |
| Strong emphasis on nonlinear control and feedback stabilization | Strong emphasis on linear systems, representations, and trajectory structure |
| Inputs and outputs are central | Input/output partition is secondary |
| Natural for control design | Natural for modeling and structural system theory |

A compact summary: **Sontag is closer to nonlinear control and stabilization; Willems–Polderman is closer to algebraic/behavioral systems theory, where a system is the totality of its possible trajectories.**


---

> Hopf algebra

<details><summary>💭 Thinking</summary>

**Explaining Hopf algebra in relation to systems theory**

It seems the user is asking about Hopf algebra in the context of systems theory, perhaps with a specific interest in how it relates to Sontag, Willems, and Polderman. I'll provide a concise explanation linking Hopf algebra to control theory, renormalization, and combinatorics, without needing citations. This should fit well into the ongoing discussion.

</details>

A **Hopf algebra** is an algebraic structure that combines:

\[
\text{multiplication} \quad+\quad \text{comultiplication} \quad+\quad \text{inverse-like operation}.
\]

Formally, over a field \(k\), a Hopf algebra \(H\) has:

\[
m:H\otimes H\to H
\]

multiplication,

\[
\eta:k\to H
\]

unit,

\[
\Delta:H\to H\otimes H
\]

comultiplication,

\[
\epsilon:H\to k
\]

counit,

and an **antipode**

\[
S:H\to H,
\]

which behaves like a generalized inverse.

The defining intuition is:

| Structure | Meaning |
|---|---|
| Algebra | You can multiply elements. |
| Coalgebra | You can split elements into tensor components. |
| Antipode | You have an abstract inverse operation. |
| Hopf algebra | Algebra + coalgebra + compatible inverse. |

In Sweedler notation, the coproduct is written

\[
\Delta(h)=\sum h_{(1)}\otimes h_{(2)}.
\]

The antipode satisfies

\[
\sum S(h_{(1)})h_{(2)}=\epsilon(h)1
\]

and

\[
\sum h_{(1)}S(h_{(2)})=\epsilon(h)1.
\]

### Basic examples

| Example | Hopf structure |
|---|---|
| Group algebra \(kG\) | \(\Delta(g)=g\otimes g\), \(S(g)=g^{-1}\) |
| Universal enveloping algebra \(U(\mathfrak g)\) | Encodes Lie algebra structure |
| Polynomial algebra \(k[x]\) | Often \(\Delta(x)=x\otimes 1+1\otimes x\) |
| Shuffle algebra | Important in iterated integrals and control |
| Connes–Kreimer algebra | Rooted trees, renormalization, numerical analysis |

### Relation to systems theory

Hopf algebras are **not central in the introductory Sontag or Willems–Polderman texts**, but they appear in more advanced algebraic approaches to dynamical systems and control.

Important links:

| Area | Hopf-algebra role |
|---|---|
| **Chen iterated integrals** | Shuffle Hopf algebra |
| **Fliess series** | Nonlinear input-output systems |
| **Control theory** | Algebraic representation of nonlinear systems |
| **Rough paths** | Tensor/shuffle Hopf algebras |
| **Numerical integration** | Butcher group, rooted-tree Hopf algebras |
| **Renormalization** | Connes–Kreimer Hopf algebra |

For nonlinear control, the relevant bridge is often:

\[
\text{inputs} \rightarrow \text{iterated integrals} \rightarrow \text{formal power series} \rightarrow \text{shuffle Hopf algebra}.
\]

This connects to **Chen–Fliess series**, which represent certain nonlinear input-output systems using noncommutative formal power series.

A compact summary:

**Sontag and Willems–Polderman give standard mathematical systems theory. Hopf algebras enter when systems theory is reformulated through formal series, iterated integrals, rooted trees, or algebraic/combinatorial structures.**


---

> Formal power systems

In this context the standard term is **formal power series**, especially **noncommutative formal power series**.

They are central in the algebraic approach to nonlinear systems, Chen–Fliess series, shuffle algebras, and Hopf-algebraic control theory.

A usual setup:

\[
X=\{x_0,x_1,\dots,x_m\}
\]

is an alphabet. The free monoid \(X^\ast\) consists of all finite words in those letters:

\[
\emptyset,\ x_0,\ x_1,\ x_0x_1,\ x_1x_0x_0,\dots
\]

A **formal power series** over \(X\) is

\[
c=\sum_{\eta\in X^\ast} (c,\eta)\eta,
\]

where each word \(\eta\) has a coefficient \((c,\eta)\).

The key point: the symbols do **not** have to commute. So usually

\[
x_0x_1 \neq x_1x_0.
\]

That matters because in nonlinear input-output systems, the order of inputs matters.

### Link to control systems

For a nonlinear control system

\[
\dot z = g_0(z)+\sum_{i=1}^m g_i(z)u_i,
\qquad y=h(z),
\]

the input-output map can often be represented as a **Chen–Fliess series**:

\[
y(t)=\sum_{\eta\in X^\ast} (c,\eta) E_\eta[u](t).
\]

Here:

| Object | Meaning |
|---|---|
| \(c\) | Noncommutative formal power series |
| \(\eta\) | Word over the alphabet \(X\) |
| \((c,\eta)\) | Coefficient encoding system dynamics |
| \(E_\eta[u]\) | Iterated integral of the input |
| \(y(t)\) | System output |

The iterated integrals are defined recursively:

\[
E_{\emptyset}[u](t)=1,
\]

\[
E_{x_i\eta}[u](t)=\int_0^t u_i(\tau)E_\eta[u](\tau)\,d\tau.
\]

Usually \(x_0\) corresponds to the drift term, with \(u_0=1\).

### Why Hopf algebras enter

Formal power series interact naturally with the **shuffle product**:

\[
E_\eta[u](t)E_\xi[u](t)
=
\sum_{\zeta\in \eta \shuffle \xi} E_\zeta[u](t).
\]

This creates a Hopf algebra structure.

So the chain is:

\[
\text{nonlinear system}
\rightarrow
\text{iterated integrals}
\rightarrow
\text{formal power series}
\rightarrow
\text{shuffle Hopf algebra}.
\]

### Minimal example

Take alphabet

\[
X=\{x_0,x_1\}.
\]

A formal series might be

\[
c = 3\emptyset + 2x_1 - 5x_0x_1 + 7x_1x_0x_1+\cdots.
\]

This is not a polynomial, because it can contain infinitely many words. It is “formal” because convergence is not always the first issue; algebraic manipulation comes first.

### In systems terms

A **formal power series representation** encodes a nonlinear input-output system by storing all its higher-order input-response coefficients.

It is analogous to a transfer function, but for nonlinear systems:

| Linear systems | Nonlinear formal-series systems |
|---|---|
| Transfer function | Chen–Fliess series |
| Rational function | Formal power series |
| Convolution kernel | Iterated integrals |
| Matrix algebra | Shuffle / Hopf algebra |
| Frequency-domain tools | Algebraic/combinatorial tools |

Compact summary:

**Formal power series are the algebraic language used to represent nonlinear systems through ordered input words and iterated integrals. Hopf algebras appear because these words multiply through shuffle-type rules.**


---

> Mathematica David bessis

I’ll interpret this as asking for the David Bessis connection to mathematics/Mathematica, not Wolfram Mathematica, unless the sources indicate otherwise.

```json
{"system1_search_query":[{"q":"David Bessis Mathematica book math intuition curiosity"},{"q":"David Bessis mathematician book Mathematica"}],"response_length":"short"}
```

```json
{"system1_search_query":[{"q":"David Bessis mathematician biography braid groups complex reflection arrangements"},{"q":"David Bessis Institut de Mathématiques de Jussieu biography"}],"response_length":"medium"}
```

David Bessis’s **_Mathematica: A Secret World of Intuition and Curiosity_** is a book about **how mathematical thinking works**, not about Wolfram Mathematica software.

It was originally written by the French mathematician **David Bessis** and translated into English by **Kevin Frey**. Yale University Press lists the English hardcover/eBook publication date as **May 28, 2024**, with a paperback edition on **May 20, 2025**. citeturn198814search3

Core thesis:

**Mathematics is not mainly symbol manipulation. It is trained intuition: forming mental images, testing them, correcting them, and gradually making them precise.**

This fits well after your previous chain:

\[
\text{systems theory}
\rightarrow
\text{formal power series}
\rightarrow
\text{Hopf algebra}
\rightarrow
\text{mathematical intuition}
\]

Bessis himself is not just a popularizer. His research background is in **group theory, braid groups, complex reflection groups, hyperplane arrangements, and noncrossing partitions**. His 2015 *Annals of Mathematics* paper **“Finite complex reflection arrangements are \(K(\pi,1)\)”** concerns braid groups, complex reflection groups, and hyperplane arrangements. citeturn189359search2 He also wrote **“The dual braid monoid”**, published in *Annales scientifiques de l’École Normale Supérieure* in 2003. citeturn189359search11

A compact reading of Bessis:

| Theme | Meaning |
|---|---|
| **Intuition** | Mathematical understanding begins with internal images and experiments. |
| **Formalism** | Symbols come later to stabilize and verify intuition. |
| **Errors** | Mistakes are not incidental; they are part of the learning mechanism. |
| **Practice** | Mathematical ability is trainable, not a fixed genetic gift. |
| **Research background** | Braid groups, reflection groups, topology, algebraic/combinatorial structures. |

In relation to your earlier topics:

| Earlier topic | Link to Bessis |
|---|---|
| **Hopf algebra** | Algebraic structures require mental compression and symbolic intuition. |
| **Formal power series** | Good example of formalism that becomes intelligible through images: words, trees, paths, shuffles. |
| **Willems / Sontag systems theory** | Bessis is less about systems theory itself, more about how to build the kind of mathematical intuition needed to understand it. |
| **Braid groups** | Directly connected to Bessis’s research mathematics. |

So the relevant takeaway is:

**Bessis’s _Mathematica_ is a meta-mathematical book: it explains how to learn and think mathematics from the inside. His own technical background is close to braid groups, reflection groups, and algebraic topology, not control theory.**


---

> Homotopy type theory and control theory ringer and raginsky collab

I’ll verify the names and the specific collaboration first, then place it in the broader HoTT/control-theory context.

```json
{"system1_search_query":[{"q":"Talia Ringer Maxim Raginsky homotopy type theory control theory collaboration"},{"q":"Ringer Raginsky control theory homotopy type theory"},{"q":"\"Raginsky\" \"Ringer\" \"homotopy type theory\""},{"q":"\"Homotopy Type Theory\" \"control theory\" Raginsky"}],"response_length":"medium"}
```

```json
{"open":[{"ref_id":"turn735687search0"},{"ref_id":"turn735687search4"}],"response_length":"medium"}
```

```json
{"open":[{"ref_id":"turn304872view1","lineno":54},{"ref_id":"turn304872view0","lineno":73}],"response_length":"medium"}
```

<details><summary>💭 Thinking</summary>

**Searching for Ringer's work on HoTT**

I need to clarify Ringer and Raginsky’s collaboration. It looks like it’s about structural recursion in Transformers, not HoTT or control theory. I’ll search for "Ringer homotopy type theory" and "Talia Ringer HoTT" to explore any potential connections or bridges between them, even if they’re not exactly collaborating.

</details>

```json
{"system1_search_query":[{"q":"Talia Ringer homotopy type theory"},{"q":"Talia Ringer dependent type theory proof repair homotopy type theory"},{"q":"\"Proof Repair across Type Equivalences\" Ringer type equivalences"},{"q":"\"Dylan Zhang\" \"Raginsky\" \"Ringer\" recursive"}],"response_length":"medium"}
```

<details><summary>💭 Thinking</summary>

**Exploring HoTT and control theory synthesis**

I need to clear up that Ringer and Raginsky's actual collaboration is on recursion/transformers, not HoTT and control theory. But there might be a possible synthesis between HoTT and control theory—formalizing control theory in HoTT or dependent type theory. I might even search "formalization control theory Coq" for more insights.

</details>

```json
{"system1_search_query":[{"q":"formalization control theory Coq proof assistant"},{"q":"control theory proof assistant Coq Lean formalization"},{"q":"\"control theory\" \"homotopy type theory\""},{"q":"\"systems theory\" \"dependent type theory\" control"}],"response_length":"medium"}
```

<details><summary>💭 Thinking</summary>

**Clarifying collaboration details and citations**

To clarify:
- The Ringer and Raginsky collaboration isn't specifically on HoTT + control theory.
- Talia Ringer focuses on proof assistants, dependent type theory, and proof repair; her work "Proof Repair across Type Equivalences" explores transport across equivalences, which is similar to HoTT ideas.
- Maxim Raginsky's research spans control, information, and learning, with recent works on neural ODEs, stochastic realization, and the Liouville theorem.
- Their paper "Can/Transformer-based models are not yet perfect..." explores transformer learning, structural recursion, CS logic, and dynamical systems.

**Exploring the bridge between HoTT and control theory**

To make connections between HoTT and control theory:
1. Proof assistants can formalize control proofs, like stability and reachability.
2. HoTT’s univalence and equivalences offer important representations for systems and proof repair.
3. Dependent types help encode specifications for systems and controllers, ensuring stability.
4. Recursion/transformers connect induction, type theory, and learning.

I haven’t found a direct Ringer–Raginsky paper on HoTT and control theory yet, but I’ll search and cite relevant papers.

</details>

```json
{"open":[{"ref_id":"turn642549search11"},{"ref_id":"turn642549search2"},{"ref_id":"turn642549academia41"},{"ref_id":"turn580646search0"}],"response_length":"medium"}
```

```json
{"open":[{"ref_id":"turn580646search26"}],"response_length":"medium"}
```

<details><summary>💭 Thinking</summary>

**Considering citation for search results**

It seems like it's acceptable to cite search results, especially for formalized concepts like the inverted pendulum. However, I’m not sure if I should use results from sources with restricted access or not. If the web tool provides useful details, it might be okay, but a direct citation might not work in this case. I’ll search for an alternative title.

</details>

```json
{"system1_search_query":[{"q":"\"A Formal Proof in Coq of a Control Function for the Inverted Pendulum\" abstract"},{"q":"\"A Formalized Theory for Verifying Stability and Convergence\" Coq control systems"},{"q":"\"Lyapunov\" \"Coq\" \"control\" formalization"},{"q":"\"inverted pendulum\" \"Coq\" control function formal proof"}],"response_length":"medium"}
```

<details><summary>💭 Thinking</summary>

**Finalizing citations for HoTT source**

I need a final answer with citations, since I’ve browsed sources. I could potentially cite the HoTT book (arxiv 1308.0729) or Rijke. Should I use the official nLab as well? Hmm, I’ll stick to the HoTT book citation from arxiv and include details from the search results where appropriate.

</details>

```json
{"open":[{"ref_id":"turn735687academia16"},{"ref_id":"turn735687search13"}],"response_length":"medium"}
```

I don’t find evidence of a **direct Ringer–Raginsky collaboration specifically on “homotopy type theory and control theory.”** The collaboration I find is adjacent: **Talia Ringer + Maxim Raginsky** coauthored work on whether transformers can learn **structural recursion**, relevant to formal verification and proof engineering, not classical control theory directly. The paper is **“Can Transformers Learn to Solve Problems Recursively?”**, with authors Shizhuo Dylan Zhang, Curt Tigges, Stella Biderman, Maxim Raginsky, and Talia Ringer. It studies transformer models on structurally recursive functions, with subjects listed as ML, AI, logic in CS, and programming languages. citeturn381695view0

The conceptual bridge looks like this:

\[
\text{HoTT / dependent type theory}
\rightarrow
\text{proof assistants}
\rightarrow
\text{formal verification}
\rightarrow
\text{certified control systems}
\]

Talia Ringer’s side is **proof engineering and dependent type theory**. Her page describes current work on proof assistants, proof repair, machine learning for proofs, and verified systems. citeturn199257view1 Her paper **“Proof Repair across Type Equivalences”** implements transport across type equivalences in Coq, which is very close in spirit to the HoTT/univalence idea that equivalent structures can be systematically transported across. citeturn381695view1 A later Ringer-related paper, **“Proof Repair across Quotient Type Equivalences,”** explicitly discusses quotient type equivalences, Coq setoids, and Cubical Agda, where quotient types and univalent ideas are more native. citeturn381695view2

Raginsky’s side is **control, dynamical systems, information theory, and learning**. His publication list includes recent work on neural ODEs, Chen–Fliess series, stochastic realization, Sussmann’s orbit theorem, nonlinear stochastic differential equations, input-to-state stability, control-theoretic RNA velocities, and Liouville-equation controllability. citeturn199257view0

So the synthesis is not:

\[
\text{Ringer + Raginsky} = \text{HoTT control theory paper}
\]

but more plausibly:

\[
\text{Ringer: formal proof / type equivalence}
+
\text{Raginsky: control / dynamics / learning}
\Rightarrow
\text{future-style certified dynamical systems}
\]

### Where HoTT helps control theory

HoTT’s key principle is that **equivalent structures can be treated as identical in a controlled formal sense**. The HoTT book says univalence implies that isomorphic structures can be identified, while higher inductive types give logical descriptions of spaces and homotopical constructions. citeturn339958view0 The IAS summary states the same more directly: univalence says identity is equivalent to equivalence, and constructions can be transported along such identifications. citeturn339958view1

That matters for control theory because control uses many equivalent representations:

| Control-theory object | HoTT / type-theoretic analogue |
|---|---|
| State-space realization | Structured type with dynamics |
| Change of coordinates | Equivalence of types/spaces |
| Minimal realization equivalence | Transport of properties across equivalent models |
| Behavioral equivalence | Equality up to observable trajectories |
| Quotient by indistinguishability | Quotient type / setoid |
| Controller correctness | Dependent type containing system + proof |

A certified controller might be represented as:

\[
\Sigma(K : \text{Controller}).\ \text{Stable}(G,K)
\]

meaning: “a controller \(K\), together with a proof that \(K\) stabilizes plant \(G\).”

### Existing formal-control precedent

This is not merely speculative. Control proofs have been formalized in proof assistants. For example, Rouhling formalized in Coq the soundness proof of a control function for the inverted pendulum, a benchmark nonlinear control problem. citeturn924154search2 INRIA’s MARELLE report also describes Coq formalizations of LaSalle’s invariance principle and the correctness of a controller for an inverted pendulum. citeturn924154search19

### Compact formulation

The clean research-program statement would be:

**Use dependent type theory / HoTT-style equivalence reasoning to make control-theoretic constructions representation-invariant and machine-checkable. Then use proof-engineering tools, possibly ML-assisted, to maintain those proofs as models, coordinates, abstractions, or controllers change.**

Ringer contributes the proof-engineering/type-equivalence side. Raginsky contributes the dynamical-systems/control/learning side. Their known collaboration is on **structural recursion in transformers**, not yet a direct HoTT-control-theory project.


---

> what books are good about homotopy type theory ?

I’ll separate true HoTT books from prerequisite books, since many “good HoTT books” are actually type theory or category/topology preparation.

```json
{"system1_search_query":[{"q":"homotopy type theory book Univalent Foundations Program official"},{"q":"Egbert Rijke Introduction to Homotopy Type Theory Cambridge University Press book"},{"q":"Homotopy Type Theory Univalent Foundations of Mathematics book official pdf"},{"q":"HoTT book resources homotopy type theory recommended books"}],"response_length":"medium"}
```

<details><summary>💭 Thinking</summary>

**Searched 17 websites**

</details>

Good core books/resources:

| Level | Book | Why read it |
|---|---|---|
| Best modern entry | **Egbert Rijke, _Introduction to Homotopy Type Theory_** | Probably the best first serious textbook now. It introduces Martin-Löf dependent type theory first, then univalence and higher inductive types. It is self-contained and includes 200+ exercises. citeturn723075academia32turn311975search2 |
| Canonical reference | **The Univalent Foundations Program, _Homotopy Type Theory: Univalent Foundations of Mathematics_** | The original “HoTT Book.” Free online, systematic, broad, and still the main reference for univalent foundations. It does not require prior formal logic or proof-assistant use. citeturn311975search0turn311975search12 |
| Gentle dependent-type preparation | **Daniel P. Friedman & David Thrane Christiansen, _The Little Typer_** | Not HoTT proper, but a good informal bridge into dependent types and proofs-as-programs. MIT Press describes it as an introduction to dependent types that builds a bridge between mathematics and programming. citeturn219035search0 |
| Formal type-theory preparation | **Rob Nederpelt & Herman Geuvers, _Type Theory and Formal Proof_** | Good if the syntax/rules of type theory feel opaque. It is a step-by-step introduction to type theory, lambda calculus, and formal proof. citeturn723075search0 |
| Programming-language angle | **Robert Harper, _Practical Foundations for Programming Languages_** | Not HoTT, but useful for understanding type systems, operational semantics, and the programming-language side of dependent type theory. citeturn723075search10 |
| Category-theory support | **Emily Riehl, _Category Theory in Context_** | Good background for the categorical/homotopical language around HoTT. It covers categories, functors, natural transformations, Yoneda, limits/colimits, adjunctions, monads, and Kan extensions. citeturn723075search8 |

My suggested order:

\[
\textit{The Little Typer}
\rightarrow
\textit{Type Theory and Formal Proof}
\rightarrow
\textit{Rijke}
\rightarrow
\textit{The HoTT Book}
\]

For a mathematically mature reader, skip straight to:

\[
\textit{Rijke}
\rightarrow
\textit{The HoTT Book}
\]

The **Rijke book** is the best starting point if you want to actually learn HoTT. The **HoTT Book** is the standard reference. The others are supporting material.

