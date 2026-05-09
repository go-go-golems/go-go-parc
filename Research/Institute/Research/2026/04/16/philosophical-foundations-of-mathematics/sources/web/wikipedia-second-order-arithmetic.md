In [mathematical logic](https://en.wikipedia.org/wiki/Mathematical_logic "Mathematical logic"), **second-order arithmetic** is a collection of [axiomatic](https://en.wikipedia.org/wiki/Axiom "Axiom") systems that formalize the [natural numbers](https://en.wikipedia.org/wiki/Natural_number "Natural number") and their [subsets](https://en.wikipedia.org/wiki/Subset "Subset"). It is an alternative to [axiomatic set theory](https://en.wikipedia.org/wiki/Axiomatic_set_theory "Axiomatic set theory") as a [foundation](https://en.wikipedia.org/wiki/Foundation_of_mathematics "Foundation of mathematics") for much, but not all, of mathematics.

A precursor to second-order arithmetic that involves third-order parameters was introduced by [David Hilbert](https://en.wikipedia.org/wiki/David_Hilbert "David Hilbert") and [Paul Bernays](https://en.wikipedia.org/wiki/Paul_Bernays "Paul Bernays") in their book *[Grundlagen der Mathematik](https://en.wikipedia.org/wiki/Grundlagen_der_Mathematik "Grundlagen der Mathematik")*.[^1] The standard axiomatization of second-order arithmetic is denoted by **Z <sub>2</sub>**.

Second-order arithmetic includes, but is significantly stronger than, its [first-order](https://en.wikipedia.org/wiki/First-order_logic "First-order logic") counterpart [Peano arithmetic](https://en.wikipedia.org/wiki/Peano_axioms#Peano_arithmetic_as_first-order_theory "Peano axioms"). Unlike Peano arithmetic, second-order arithmetic allows [quantification](https://en.wikipedia.org/wiki/Quantification_\(logic\) "Quantification (logic)") over sets of natural numbers as well as numbers themselves. Because [real numbers](https://en.wikipedia.org/wiki/Real_number "Real number") can be represented as ([infinite](https://en.wikipedia.org/wiki/Infinite_set "Infinite set")) sets of natural numbers in well-known ways, and because second-order arithmetic allows quantification over such sets, it is possible to formalize the [real numbers](https://en.wikipedia.org/wiki/Real_number "Real number") in second-order arithmetic. For this reason, second-order arithmetic is sometimes called " [analysis](https://en.wikipedia.org/wiki/Mathematical_analysis "Mathematical analysis") ".[^2]

Second-order arithmetic can also be seen as a weak version of [set theory](https://en.wikipedia.org/wiki/Set_theory "Set theory") in which every element is either a natural number or a set of natural numbers. Although it is much weaker than [Zermelo–Fraenkel set theory](https://en.wikipedia.org/wiki/Zermelo%E2%80%93Fraenkel_set_theory "Zermelo–Fraenkel set theory"), second-order arithmetic can prove essentially all of the results of classical mathematics expressible in its language.

A **subsystem of second-order arithmetic** is a [theory](https://en.wikipedia.org/wiki/Theory_\(logic\) "Theory (logic)") in the language of second-order arithmetic each axiom of which is a theorem of full second-order arithmetic (Z <sub>2</sub>). Such subsystems are essential to [reverse mathematics](https://en.wikipedia.org/wiki/Reverse_mathematics "Reverse mathematics"), a research program investigating how much of classical mathematics can be derived in certain weak subsystems of varying strength. Much of core mathematics can be formalized in these weak subsystems, some of which are defined below. Reverse mathematics also clarifies the extent and manner in which classical mathematics is [nonconstructive](https://en.wikipedia.org/wiki/Nonconstructive "Nonconstructive").

## Definition

### Syntax

The language of second-order arithmetic is [two-sorted](https://en.wikipedia.org/wiki/Many-sorted_logic "Many-sorted logic"). The first sort of [terms](https://en.wikipedia.org/wiki/Term_\(logic\) "Term (logic)") and in particular [variables](https://en.wikipedia.org/wiki/Variable_\(mathematics\) "Variable (mathematics)"), usually denoted by lower case letters, consists of [individuals](https://en.wikipedia.org/wiki/Individual "Individual"), whose intended interpretation is as natural numbers. The other sort of variables, variously called "set variables", "class variables", or even "predicates" are usually denoted by upper-case letters. They refer to classes/predicates/properties of individuals, and so can be thought of as sets of natural numbers. Both individuals and set variables can be quantified [universally](https://en.wikipedia.org/wiki/Universal_quantification "Universal quantification") or [existentially](https://en.wikipedia.org/wiki/Existential_quantification "Existential quantification"). A formula with no [bound](https://en.wikipedia.org/wiki/Bound_variable "Bound variable") set variables (that is, no quantifiers over set variables) is called **arithmetical**. An arithmetical formula may have free set variables and bound individual variables.

Individual terms are formed from the constant 0, the unary function *S* (the *[successor function](https://en.wikipedia.org/wiki/Successor_function "Successor function")*), and the binary operations + and ${\displaystyle \cdot }$ (addition and multiplication). The successor function adds 1 to its input. The relations = (equality) and < (comparison of natural numbers) relate two individuals, whereas the relation ∈ (membership) relates an individual and a set (or class). Thus in notation the language of second-order arithmetic is given by the signature ${\displaystyle {\mathcal {L}}=\{0,S,+,\cdot ,=,<,\in \}}$.

For example, ${\displaystyle \forall n(n\in X\rightarrow Sn\in X)}$, is a [well-formed formula](https://en.wikipedia.org/wiki/Well-formed_formula "Well-formed formula") of second-order arithmetic that is arithmetical, has one free set variable *X* and one bound individual variable *n* (but no bound set variables, as is required of an arithmetical formula)—whereas ${\displaystyle \exists X\forall n(n\in X\leftrightarrow n<SSSSSS0\cdot SSSSSSS0)}$ is a well-formed formula that is not arithmetical, having one bound set variable *X* and one bound individual variable *n*.

### Semantics

Several different interpretations of the quantifiers are possible. If second-order arithmetic is studied using the full semantics of [second-order logic](https://en.wikipedia.org/wiki/Second-order_logic "Second-order logic") then the set quantifiers range over all subsets of the range of the individual variables. If second-order arithmetic is formalized using the semantics of [first-order logic](https://en.wikipedia.org/wiki/First-order_logic "First-order logic") ([Henkin semantics](https://en.wikipedia.org/wiki/Henkin_semantics "Henkin semantics")) then any model includes a domain for the set variables to range over, and this domain may be a proper subset of the full [powerset](https://en.wikipedia.org/wiki/Powerset "Powerset") of the domain of individual variables.[^3]

### Axioms

#### Basic

The following axioms are known as the *basic axioms*, or sometimes the *Robinson axioms.* The resulting [first-order theory](https://en.wikipedia.org/wiki/First-order_theory "First-order theory"), known as [Robinson arithmetic](https://en.wikipedia.org/wiki/Robinson_arithmetic "Robinson arithmetic"), is essentially [Peano arithmetic](https://en.wikipedia.org/wiki/Peano_axioms#Peano_arithmetic_as_first-order_theory "Peano axioms") without induction. The [domain of discourse](https://en.wikipedia.org/wiki/Domain_of_discourse "Domain of discourse") for the [quantified variables](https://en.wikipedia.org/wiki/Quantification_\(logic\) "Quantification (logic)") is the [natural numbers](https://en.wikipedia.org/wiki/Natural_number "Natural number"), collectively denoted by **N**, and including the distinguished member ${\displaystyle 0}$, called " [zero](https://en.wikipedia.org/wiki/Zero "Zero")."

The primitive functions are the unary [successor function](https://en.wikipedia.org/wiki/Successor_function "Successor function"), denoted by [prefix](https://en.wikipedia.org/wiki/Prefix "Prefix") ${\displaystyle S}$, and two [binary operations](https://en.wikipedia.org/wiki/Binary_operation "Binary operation"), [addition](https://en.wikipedia.org/wiki/Addition "Addition") and [multiplication](https://en.wikipedia.org/wiki/Multiplication "Multiplication"), denoted by the [infix operator](https://en.wikipedia.org/wiki/Infix_operator "Infix operator") "+" and " ${\displaystyle \cdot }$ ", respectively. There is also a primitive [binary relation](https://en.wikipedia.org/wiki/Binary_relation "Binary relation") called [order](https://en.wikipedia.org/wiki/Order_relation "Order relation"), denoted by the infix operator "<".

Axioms governing the [successor function](https://en.wikipedia.org/wiki/Successor_function "Successor function") and [zero](https://en.wikipedia.org/wiki/Zero "Zero"):

1. ${\displaystyle \forall m[Sm=0\rightarrow \bot ].}$ ("the successor of a natural number is never zero")
2. ${\displaystyle \forall m\forall n[Sm=Sn\rightarrow m=n].}$ ("the successor function is [injective](https://en.wikipedia.org/wiki/Injective_function "Injective function") ")
3. ${\displaystyle \forall n[0=n\lor \exists m[Sm=n]].}$ ("every natural number is zero or a successor")

[Addition](https://en.wikipedia.org/wiki/Addition "Addition") defined [recursively](https://en.wikipedia.org/wiki/Recursion "Recursion"):

1. ${\displaystyle \forall m[m+0=m].}$
2. ${\displaystyle \forall m\forall n[m+Sn=S(m+n)].}$

[Multiplication](https://en.wikipedia.org/wiki/Multiplication "Multiplication") defined recursively:

1. ${\displaystyle \forall m[m\cdot 0=0].}$
2. ${\displaystyle \forall m\forall n[m\cdot Sn=(m\cdot n)+m].}$

Axioms governing the [order relation](https://en.wikipedia.org/wiki/Order_relation "Order relation") "<":

1. ${\displaystyle \forall m[m<0\rightarrow \bot ].}$ ("no natural number is smaller than zero")
2. ${\displaystyle \forall n\forall m[m<Sn\leftrightarrow (m<n\lor m=n)].}$
3. ${\displaystyle \forall n[0=n\lor 0<n].}$ ("every natural number is zero or bigger than zero")
4. ${\displaystyle \forall m\forall n[(Sm<n\lor Sm=n)\leftrightarrow m<n].}$

These axioms are all [first-order statements](https://en.wikipedia.org/wiki/First-order_logic "First-order logic"). That is, all variables range over the [natural numbers](https://en.wikipedia.org/wiki/Natural_number "Natural number") and not [sets](https://en.wikipedia.org/wiki/Set_theory "Set theory") thereof, a fact even stronger than their being arithmetical. Moreover, there is but one [existential quantifier](https://en.wikipedia.org/wiki/Existential_quantifier "Existential quantifier"), in Axiom 3. Axioms 1 and 2, together with an [axiom schema of induction](https://en.wikipedia.org/wiki/Peano_axioms "Peano axioms") make up the usual [Peano–Dedekind](https://en.wikipedia.org/wiki/Peano_axioms "Peano axioms") definition of **N**. Adding to these axioms any sort of [axiom schema of induction](https://en.wikipedia.org/wiki/Peano_axioms "Peano axioms") makes redundant the axioms 3, 10, and 11.

#### Induction and comprehension schema

If *φ* (*n*) is a formula of second-order arithmetic with a free individual variable *n* and possibly other free individual or set variables (written *m* <sub>1</sub>,...,*m* <sub><i>k</i></sub> and *X* <sub>1</sub>,...,*X* <sub><i>l</i></sub>), the **induction axiom** for *φ* is the axiom:

${\displaystyle \forall m_{1}\dots m_{k}\forall X_{1}\dots X_{l}((\varphi (0)\land \forall n(\varphi (n)\rightarrow \varphi (Sn)))\rightarrow \forall n\varphi (n))}$

The (**full**) **second-order induction scheme** consists of all instances of this axiom, over all second-order formulas.

One particularly important instance of the induction scheme is when *φ* is the formula " ${\displaystyle n\in X}$ " expressing the fact that *n* is a member of *X* (*X* being a free set variable): in this case, the induction axiom for *φ* is

${\displaystyle \forall X((0\in X\land \forall n(n\in X\rightarrow Sn\in X))\rightarrow \forall n(n\in X))}$

This sentence is called the **second-order induction axiom**.

If *φ* (*n*) is a formula with a free variable *n* and possibly other free variables, but not the variable *Z*, the **[comprehension axiom](https://en.wikipedia.org/wiki/Comprehension_axiom "Comprehension axiom")** for *φ* is the formula

${\displaystyle \exists Z\forall n(n\in Z\leftrightarrow \varphi (n))}$

This axiom makes it possible to form the set ${\displaystyle Z=\{n|\varphi (n)\}}$ of natural numbers satisfying *φ* (*n*). There is a technical restriction that the formula *φ* may not contain the variable *Z*, for otherwise the formula ${\displaystyle n\not \in Z}$ would lead to the comprehension axiom

${\displaystyle \exists Z\forall n(n\in Z\leftrightarrow n\not \in Z)}$,

which is inconsistent. This convention is assumed in the remainder of this article.

### The full system

The formal theory of **second-order arithmetic** (in the language of second-order arithmetic) consists of the basic axioms, the comprehension axiom for every formula *φ* (arithmetic or otherwise), and the second-order induction axiom. This theory is sometimes called *full second-order arithmetic* to distinguish it from its subsystems, defined below. Because full second-order semantics imply that every possible set exists, the comprehension axioms may be taken to be part of the deductive system when full second-order semantics is employed.[^3]

## Models

This section describes second-order arithmetic with first-order semantics. Thus a **model** ${\displaystyle {\mathcal {M}}}$ of the language of second-order arithmetic consists of a set *M* (which forms the range of individual variables) together with a constant 0 (an element of *M*), a function *S* from *M* to *M*, two binary operations + and · on *M*, a binary relation < on *M*, and a collection *D* of subsets of *M*, which is the range of the set variables. Omitting *D* produces a model of the language of first-order arithmetic.

When *D* is the full powerset of *M*, the model ${\displaystyle {\mathcal {M}}}$ is called a **full model**. The use of full second-order semantics is equivalent to limiting the models of second-order arithmetic to the full models. In fact, the axioms of second-order arithmetic have only one full model. This follows from the fact that the [Peano axioms](https://en.wikipedia.org/wiki/Peano_axioms "Peano axioms") with the second-order induction axiom have only one model under second-order semantics.

### Definable functions

The first-order functions that are provably [total](https://en.wikipedia.org/wiki/Total_function "Total function") in second-order arithmetic are precisely the same as those representable in [system F](https://en.wikipedia.org/wiki/System_F "System F").[^4] Almost equivalently, system F is the theory of functionals corresponding to second-order arithmetic in a manner parallel to how Gödel's [system T](https://en.wikipedia.org/wiki/Dialectica_interpretation "Dialectica interpretation") corresponds to first-order arithmetic in the [Dialectica interpretation](https://en.wikipedia.org/wiki/Dialectica_interpretation "Dialectica interpretation").

### More types of models

When a model of the language of second-order arithmetic has certain properties, it can also be called these other names:

- When *M* is the usual set of natural numbers with its usual operations, ${\displaystyle {\mathcal {M}}}$ is called an **ω-model**. In this case, the model may be identified with *D*, its collection of sets of naturals, because this set is enough to completely determine an ω-model. The unique full ${\displaystyle \omega }$ -model, which is the usual set of natural numbers with its usual structure and all its subsets, is called the **intended** or **standard** model of second-order arithmetic.[^5]
- A model ${\displaystyle {\mathcal {M}}}$ of the language of second-order arithmetic is called a **β-model** if ${\displaystyle {\mathcal {M}}\prec _{1}^{1}{\mathcal {P}}(\omega )}$, i.e. the [Σ <sup>1</sup> <sub>1</sub>](https://en.wikipedia.org/wiki/Analytical_hierarchy "Analytical hierarchy") -statements with parameters from ${\displaystyle {\mathcal {M}}}$ that are satisfied by ${\displaystyle {\mathcal {M}}}$ are the same as those satisfied by the full model.[^6] Some notions that are absolute with respect to β-models include " ${\displaystyle A\subseteq \omega \times \omega }$ encodes a [well-order](https://en.wikipedia.org/wiki/Well-order "Well-order") " [^7] and " ${\displaystyle A\subseteq \omega \times \omega }$ is a [tree](https://en.wikipedia.org/wiki/Tree_\(set_theory\) "Tree (set theory)") ".[^6]
- The above result has been extended to the concept of a **β <sub><i>n</i></sub> -model** for ${\displaystyle n\in \mathbb {N} }$, which has the same definition as the above except ${\displaystyle \prec _{1}^{1}}$ is replaced by ${\displaystyle \prec _{n}^{1}}$, i.e. ${\displaystyle \Sigma _{1}^{1}}$ is replaced by ${\displaystyle \Sigma _{n}^{1}}$.[^6] Using this definition β <sub>0</sub> -models are the same as ω-models.[^8]

## Subsystems

There are many named subsystems of second-order arithmetic.

A subscript 0 in the name of a subsystem indicates that it includes only a restricted portion of the full second-order induction scheme.[^9] Such a restriction lowers the [proof-theoretic strength](https://en.wikipedia.org/wiki/Proof-theoretic_strength "Proof-theoretic strength") of the system significantly. For example, the system ACA <sub>0</sub> described below is [equiconsistent](https://en.wikipedia.org/wiki/Equiconsistency "Equiconsistency") with [Peano arithmetic](https://en.wikipedia.org/wiki/Peano_arithmetic "Peano arithmetic"). The corresponding theory ACA, consisting of ACA <sub>0</sub> plus the full second-order induction scheme, is stronger than Peano arithmetic.

### Arithmetical comprehension

Many of the well-studied subsystems are related to closure properties of models. For example, it can be shown that every ω-model of full second-order arithmetic is closed under [Turing jump](https://en.wikipedia.org/wiki/Turing_jump "Turing jump"), but not every ω-model closed under Turing jump is a model of full second-order arithmetic. The subsystem ACA <sub>0</sub> includes just enough axioms to capture the notion of closure under Turing jump.

ACA <sub>0</sub> is defined as the theory consisting of the basic axioms, the **arithmetical comprehension axiom** scheme (in other words the comprehension axiom for every *arithmetical* formula *φ*) and the ordinary second-order induction axiom. It would be equivalent to also include the entire arithmetical induction axiom scheme, in other words to include the induction axiom for every arithmetical formula *φ*.

It can be shown that a collection *S* of subsets of ω determines an ω-model of ACA <sub>0</sub> if and only if *S* is closed under Turing jump, [Turing reducibility](https://en.wikipedia.org/wiki/Turing_reducibility "Turing reducibility"), and Turing join.[^10]

The subscript 0 in ACA <sub>0</sub> indicates that not every instance of the induction axiom scheme is included this subsystem. This makes no difference for ω-models, which automatically satisfy every instance of the induction axiom. It is of importance, however, in the study of non-ω-models. The system consisting of ACA <sub>0</sub> plus induction for all formulas is sometimes called ACA with no subscript.

The system ACA <sub>0</sub> is a [conservative extension](https://en.wikipedia.org/wiki/Conservative_extension "Conservative extension") of **first-order arithmetic** (or first-order Peano axioms), defined as the basic axioms, plus the first-order induction axiom scheme (for all formulas *φ* involving no class variables at all, bound or otherwise), in the language of first-order arithmetic (which does not permit class variables at all). In particular it has the same [proof-theoretic ordinal](https://en.wikipedia.org/wiki/Ordinal_analysis "Ordinal analysis") [ε <sub>0</sub>](https://en.wikipedia.org/wiki/Epsilon_number "Epsilon number") as first-order arithmetic, owing to the limited induction schema.

### The arithmetical hierarchy for formulas

A formula is called *bounded arithmetical*, or Δ <sup>0</sup> <sub>0</sub>, when all its quantifiers are of the form ∀ *n* < *t* or ∃ *n* < *t* (where *n* is the individual variable being quantified and *t* is an individual term), where

${\displaystyle \forall n<t(\cdots )}$

stands for

${\displaystyle \forall n(n<t\rightarrow \cdots )}$

and

${\displaystyle \exists n<t(\cdots )}$

stands for

${\displaystyle \exists n(n<t\land \cdots )}$.

A formula is called Σ <sup>0</sup> <sub>1</sub> (or sometimes Σ <sub>1</sub>), respectively Π <sup>0</sup> <sub>1</sub> (or sometimes Π <sub>1</sub>) when it is of the form ∃ *mφ*, respectively ∀ *mφ* where *φ* is a bounded arithmetical formula and *m* is an individual variable (that is free in *φ*). More generally, a formula is called Σ <sup>0</sup> <sub><i>n</i></sub>, respectively Π <sup>0</sup> <sub><i>n</i></sub> when it is obtained by adding existential, respectively universal, individual quantifiers to a Π <sup>0</sup> <sub><i>n</i> −1</sub>, respectively Σ <sup>0</sup> <sub><i>n</i> −1</sub> formula (and Σ <sup>0</sup> <sub>0</sub> and Π <sup>0</sup> <sub>0</sub> are both equal to Δ <sup>0</sup> <sub>0</sub>). By construction, all these formulas are arithmetical (no class variables are ever bound) and, in fact, by putting the formula in [Skolem prenex form](https://en.wikipedia.org/wiki/Skolem_prenex_form "Skolem prenex form") one can see that every arithmetical formula is logically equivalent to a Σ <sup>0</sup> <sub><i>n</i></sub> or Π <sup>0</sup> <sub><i>n</i></sub> formula for all large enough *n*.

### Recursive comprehension

The subsystem RCA <sub>0</sub> is a weaker system than ACA <sub>0</sub> and is often used as the base system in [reverse mathematics](https://en.wikipedia.org/wiki/Reverse_mathematics "Reverse mathematics"). It consists of: the basic axioms, the Σ <sup>0</sup> <sub>1</sub> induction scheme, and the Δ <sup>0</sup> <sub>1</sub> comprehension scheme. The former term is clear: the Σ <sup>0</sup> <sub>1</sub> induction scheme is the induction axiom for every Σ <sup>0</sup> <sub>1</sub> formula *φ*. The term "Δ <sup>0</sup> <sub>1</sub> comprehension" is more complex, because there is no such thing as a Δ <sup>0</sup> <sub>1</sub> formula. The Δ <sup>0</sup> <sub>1</sub> comprehension scheme instead asserts the comprehension axiom for every Σ <sup>0</sup> <sub>1</sub> formula that is logically equivalent to a Π <sup>0</sup> <sub>1</sub> formula. This scheme includes, for every Σ <sup>0</sup> <sub>1</sub> formula *φ* and every Π <sup>0</sup> <sub>1</sub> formula *ψ*, the axiom:

${\displaystyle \forall m\forall X((\forall n(\varphi (n)\leftrightarrow \psi (n)))\rightarrow \exists Z\forall n(n\in Z\leftrightarrow \varphi (n)))}$

The set of first-order consequences of RCA <sub>0</sub> is the same as those of the subsystem IΣ <sub>1</sub> of Peano arithmetic in which induction is restricted to Σ <sup>0</sup> <sub>1</sub> formulas. In turn, IΣ <sub>1</sub> is conservative over [primitive recursive arithmetic](https://en.wikipedia.org/wiki/Primitive_recursive_arithmetic "Primitive recursive arithmetic") (PRA) for ${\displaystyle \Pi _{2}^{0}}$ sentences. Moreover, the proof-theoretic ordinal of ${\displaystyle \mathrm {RCA} _{0}}$ is ω <sup>ω</sup>, the same as that of PRA.

It can be seen that a collection *S* of subsets of ω determines an ω-model of RCA <sub>0</sub> if and only if *S* is closed under Turing reducibility and Turing join. In particular, the collection of all [computable subsets](https://en.wikipedia.org/wiki/Computable_set "Computable set") of ω gives an ω-model of RCA <sub>0</sub>. This is the motivation behind the name of this system—if a set can be proved to exist using RCA <sub>0</sub>, then the set is recursive (i.e. computable).

### Weaker systems

Sometimes an even weaker system than RCA <sub>0</sub> is desired. One such system is defined as follows: one must first augment the language of arithmetic with an [exponential function](https://en.wikipedia.org/wiki/Exponential_function "Exponential function") symbol (in stronger systems the exponential can be defined in terms of addition and multiplication by the usual trick, but when the system becomes too weak this is no longer possible) and the basic axioms by the obvious axioms defining exponentiation inductively from multiplication; then the system consists of the (enriched) basic axioms, plus Δ <sup>0</sup> <sub>1</sub> comprehension, plus Δ <sup>0</sup> <sub>0</sub> induction.

### Stronger systems

Over ACA <sub>0</sub>, each formula of second-order arithmetic is equivalent to a Σ <sup>1</sup> <sub><i>n</i></sub> or Π <sup>1</sup> <sub><i>n</i></sub> formula for all large enough *n*. The system **Π <sup>1</sup> <sub>1</sub> -comprehension** is the system consisting of the basic axioms, plus the ordinary second-order induction axiom and the comprehension axiom for every ([boldface](https://en.wikipedia.org/wiki/Boldface_\(mathematics\) "Boldface (mathematics)") [^11]) Π <sup>1</sup> <sub>1</sub> formula *φ*. This is equivalent to Σ <sup>1</sup> <sub>1</sub> -comprehension (on the other hand, Δ <sup>1</sup> <sub>1</sub> -comprehension, defined analogously to Δ <sup>0</sup> <sub>1</sub> -comprehension, is weaker).

## Projective determinacy

[Projective determinacy](https://en.wikipedia.org/wiki/Projective_determinacy "Projective determinacy") is the assertion that every two-player [perfect information](https://en.wikipedia.org/wiki/Perfect_information "Perfect information") game with moves being natural numbers, game length ω and [projective](https://en.wikipedia.org/wiki/Projective_set "Projective set") payoff set is determined, that is, one of the players has a winning strategy. (The first player wins the game if the play belongs to the payoff set; otherwise, the second player wins.) A set is projective if and only if (as a predicate) it is expressible by a formula in the language of second-order arithmetic, allowing real numbers as parameters, so projective determinacy is expressible as a schema in the language of Z <sub>2</sub>.

Many natural propositions expressible in the language of second-order arithmetic are independent of Z <sub>2</sub> and even [ZFC](https://en.wikipedia.org/wiki/ZFC "ZFC") but are provable from projective determinacy. Examples include coanalytic [perfect subset property](https://en.wikipedia.org/wiki/Perfect_set_property "Perfect set property"), measurability and the [property of Baire](https://en.wikipedia.org/wiki/Property_of_Baire "Property of Baire") for ${\displaystyle \Sigma _{2}^{1}}$ sets, ${\displaystyle \Pi _{3}^{1}}$ [uniformization](https://en.wikipedia.org/wiki/Uniformization_\(set_theory\) "Uniformization (set theory)"), etc. Over a weak base theory (such as RCA <sub>0</sub>), projective determinacy implies comprehension and provides an essentially complete theory of second-order arithmetic — natural statements in the language of Z <sub>2</sub> that are independent of Z <sub>2</sub> with projective determinacy are hard to find.[^12]

ZFC + {there are *n* [Woodin cardinals](https://en.wikipedia.org/wiki/Woodin_cardinal "Woodin cardinal"): *n* is a natural number} is conservative over Z <sub>2</sub> with projective determinacy, that is a statement in the language of second-order arithmetic is provable in Z <sub>2</sub> with projective determinacy if and only if its translation into the language of set theory is provable in ZFC + {there are *n* Woodin cardinals: *n* ∈N}.

## Coding mathematics

Second-order arithmetic directly formalizes natural numbers and sets of natural numbers. However, it is able to formalize other mathematical objects indirectly via coding techniques, a fact that was first noticed by [Weyl](https://en.wikipedia.org/wiki/Hermann_Weyl "Hermann Weyl").[^13] The [integers](https://en.wikipedia.org/wiki/Integer "Integer"), [rational numbers](https://en.wikipedia.org/wiki/Rational_number "Rational number"), and [real numbers](https://en.wikipedia.org/wiki/Real_number "Real number") can all be formalized in the subsystem RCA <sub>0</sub>, along with [complete](https://en.wikipedia.org/wiki/Complete_metric_space "Complete metric space") [separable](https://en.wikipedia.org/wiki/Separable_space "Separable space") [metric spaces](https://en.wikipedia.org/wiki/Metric_space "Metric space") and continuous functions between them.[^14]

The research program of [reverse mathematics](https://en.wikipedia.org/wiki/Reverse_mathematics "Reverse mathematics") uses these formalizations of mathematics in second-order arithmetic to study the set-existence axioms required to prove mathematical theorems.[^15] For example, the [intermediate value theorem](https://en.wikipedia.org/wiki/Intermediate_value_theorem "Intermediate value theorem") for functions from the reals to the reals is provable in RCA <sub>0</sub>,[^16] while the [Bolzano **–** Weierstrass theorem](https://en.wikipedia.org/wiki/Bolzano%E2%80%93Weierstrass_theorem "Bolzano–Weierstrass theorem") is equivalent to ACA <sub>0</sub> over RCA <sub>0</sub>.[^17]

The aforementioned coding works well for continuous and total functions, assuming a higher-order base theory plus [weak Kőnig's lemma](https://en.wikipedia.org/wiki/K%C5%91nig%27s_lemma "Kőnig's lemma").[^18] As perhaps expected, in the case of [topology](https://en.wikipedia.org/wiki/Topology "Topology"), coding is not without problems.[^19]

## See also

- [Paris–Harrington theorem](https://en.wikipedia.org/wiki/Paris%E2%80%93Harrington_theorem "Paris–Harrington theorem")
- [Presburger arithmetic](https://en.wikipedia.org/wiki/Presburger_arithmetic "Presburger arithmetic")
- [True arithmetic](https://en.wikipedia.org/wiki/True_arithmetic "True arithmetic")

## References

## Further reading

- [Burgess, J. P.](https://en.wikipedia.org/wiki/John_P._Burgess "John P. Burgess") (2005). *Fixing Frege*. Princeton University Press.
- [Buss, S. R.](https://en.wikipedia.org/wiki/Samuel_Buss "Samuel Buss") (1998). *Handbook of Proof Theory*. Elsevier. [ISBN](https://en.wikipedia.org/wiki/ISBN_\(identifier\) "ISBN (identifier)") [0-444-89840-9](https://en.wikipedia.org/wiki/Special:BookSources/0-444-89840-9 "Special:BookSources/0-444-89840-9").
- [Takeuti, G.](https://en.wikipedia.org/wiki/Gaisi_Takeuti "Gaisi Takeuti") (1975). *Proof Theory*. [ISBN](https://en.wikipedia.org/wiki/ISBN_\(identifier\) "ISBN (identifier)") [0-444-10492-5](https://en.wikipedia.org/wiki/Special:BookSources/0-444-10492-5 "Special:BookSources/0-444-10492-5").

[^1]: [Hilbert, D.](https://en.wikipedia.org/wiki/David_Hilbert "David Hilbert"); [Bernays, P.](https://en.wikipedia.org/wiki/Paul_Bernays "Paul Bernays") (1934). *Grundlagen der Mathematik*. Springer-Verlag. [MR](https://en.wikipedia.org/wiki/MR_\(identifier\) "MR (identifier)") [0237246](https://mathscinet.ams.org/mathscinet-getitem?mr=0237246).

[^2]: [Sieg, W.](https://en.wikipedia.org/w/index.php?title=Wilfried_Sieg&action=edit&redlink=1 "Wilfried Sieg (page does not exist)") (2013). [*Hilbert's Programs and Beyond*](https://books.google.com/books?id=TdnQCwAAQBAJ). Oxford University Press. p. 291. [ISBN](https://en.wikipedia.org/wiki/ISBN_\(identifier\) "ISBN (identifier)") [978-0-19-970715-7](https://en.wikipedia.org/wiki/Special:BookSources/978-0-19-970715-7 "Special:BookSources/978-0-19-970715-7").

[^3]: [Shapiro, Stewart](https://en.wikipedia.org/wiki/Stewart_Shapiro "Stewart Shapiro") (1991). *Foundations Without Foundationalism: A Case for Second-Order Logic*. Oxford Logic Guides. Vol. 17. The Clarendon Press, Oxford University Press, New York. pp. 66, 74–75. [ISBN](https://en.wikipedia.org/wiki/ISBN_\(identifier\) "ISBN (identifier)") [0-19-853391-8](https://en.wikipedia.org/wiki/Special:BookSources/0-19-853391-8 "Special:BookSources/0-19-853391-8"). [MR](https://en.wikipedia.org/wiki/MR_\(identifier\) "MR (identifier)") [1143781](https://mathscinet.ams.org/mathscinet-getitem?mr=1143781).

[^4]: [Girard, Jean-Yves](https://en.wikipedia.org/wiki/Jean-Yves_Girard "Jean-Yves Girard") (1987). [*Proofs and Types*](https://www.paultaylor.eu/stable/Proofs+Types.html). Translated by Taylor, Paul. Cambridge University Press. pp. 122–123. [ISBN](https://en.wikipedia.org/wiki/ISBN_\(identifier\) "ISBN (identifier)") [0-521-37181-3](https://en.wikipedia.org/wiki/Special:BookSources/0-521-37181-3 "Special:BookSources/0-521-37181-3").

[^5]: [Simpson, S. G.](https://en.wikipedia.org/wiki/Steve_Simpson_\(mathematician\) "Steve Simpson (mathematician)") (2009). *Subsystems of Second Order Arithmetic*. Perspectives in Logic (2nd ed.). Cambridge University Press. pp. 3–4. [ISBN](https://en.wikipedia.org/wiki/ISBN_\(identifier\) "ISBN (identifier)") [978-0-521-88439-6](https://en.wikipedia.org/wiki/Special:BookSources/978-0-521-88439-6 "Special:BookSources/978-0-521-88439-6"). [MR](https://en.wikipedia.org/wiki/MR_\(identifier\) "MR (identifier)") [2517689](https://mathscinet.ams.org/mathscinet-getitem?mr=2517689).

[^6]: [Marek, W.](https://en.wikipedia.org/wiki/Victor_W._Marek "Victor W. Marek") (1974–1975). ["Stable sets, a characterization of *β* <sub>2</sub> -models of full second order arithmetic and some related facts"](https://doi.org/10.4064%2Ffm-82-2-175-189). *[Fundamenta Mathematicae](https://en.wikipedia.org/wiki/Fundamenta_Mathematicae "Fundamenta Mathematicae")*. **82**: 175–189. [doi](https://en.wikipedia.org/wiki/Doi_\(identifier\) "Doi (identifier)"):[10.4064/fm-82-2-175-189](https://doi.org/10.4064%2Ffm-82-2-175-189). [MR](https://en.wikipedia.org/wiki/MR_\(identifier\) "MR (identifier)") [0373897](https://mathscinet.ams.org/mathscinet-getitem?mr=0373897).

[^7]: [Marek, W.](https://en.wikipedia.org/wiki/Victor_W._Marek "Victor W. Marek") (1978). [" *ω* -models of second order arithmetic and admissible sets"](https://doi.org/10.4064%2Ffm-98-2-103-120). *Fundamenta Mathematicae*. **98** (2): 103–120. [doi](https://en.wikipedia.org/wiki/Doi_\(identifier\) "Doi (identifier)"):[10.4064/fm-98-2-103-120](https://doi.org/10.4064%2Ffm-98-2-103-120). [MR](https://en.wikipedia.org/wiki/MR_\(identifier\) "MR (identifier)") [0476490](https://mathscinet.ams.org/mathscinet-getitem?mr=0476490).

[^8]: [Marek, W.](https://en.wikipedia.org/wiki/Victor_W._Marek "Victor W. Marek") (1973). "Observations concerning elementary extensions of *ω* -models. II". *The Journal of Symbolic Logic*. **38**: 227–231. [doi](https://en.wikipedia.org/wiki/Doi_\(identifier\) "Doi (identifier)"):[10.2307/2272059](https://doi.org/10.2307%2F2272059). [JSTOR](https://en.wikipedia.org/wiki/JSTOR_\(identifier\) "JSTOR (identifier)") [2272059](https://www.jstor.org/stable/2272059). [MR](https://en.wikipedia.org/wiki/MR_\(identifier\) "MR (identifier)") [0337612](https://mathscinet.ams.org/mathscinet-getitem?mr=0337612).

[^9]: [Friedman, H.](https://en.wikipedia.org/wiki/Harvey_Friedman_\(mathematician\) "Harvey Friedman (mathematician)") (1976). "Systems of second order arithmetic with restricted induction, I, II". Meeting of the Association for Symbolic Logic. *[Journal of Symbolic Logic](https://en.wikipedia.org/wiki/Journal_of_Symbolic_Logic "Journal of Symbolic Logic")* (Abstracts). **41**: 557–559. [JSTOR](https://en.wikipedia.org/wiki/JSTOR_\(identifier\) "JSTOR (identifier)") [2272259](https://www.jstor.org/stable/2272259).

[^10]: [Simpson 2009](https://en.wikipedia.org/wiki/Second-order_arithmetic#CITEREFSimpson2009), pp. 311–313.

[^11]: [Welch, P. D.](https://en.wikipedia.org/wiki/Philip_Welch "Philip Welch") (2011). ["Weak systems of determinacy and arithmetical quasi-inductive definitions"](https://people.maths.bris.ac.uk/~mapdw/det17.pdf) (PDF). *The Journal of Symbolic Logic*. **76** (2): 418–436. [doi](https://en.wikipedia.org/wiki/Doi_\(identifier\) "Doi (identifier)"):[10.2178/jsl/1305810756](https://doi.org/10.2178%2Fjsl%2F1305810756). [MR](https://en.wikipedia.org/wiki/MR_\(identifier\) "MR (identifier)") [2830409](https://mathscinet.ams.org/mathscinet-getitem?mr=2830409).

[^12]: [Woodin, W. H.](https://en.wikipedia.org/wiki/W._Hugh_Woodin "W. Hugh Woodin") (2001). "The Continuum Hypothesis, Part I". *[Notices of the American Mathematical Society](https://en.wikipedia.org/wiki/Notices_of_the_American_Mathematical_Society "Notices of the American Mathematical Society")*. **48** (6).

[^13]: [Simpson 2009](https://en.wikipedia.org/wiki/Second-order_arithmetic#CITEREFSimpson2009), p. 16.

[^14]: [Simpson 2009](https://en.wikipedia.org/wiki/Second-order_arithmetic#CITEREFSimpson2009), Chapter II.

[^15]: [Simpson 2009](https://en.wikipedia.org/wiki/Second-order_arithmetic#CITEREFSimpson2009), p. 32.

[^16]: [Simpson 2009](https://en.wikipedia.org/wiki/Second-order_arithmetic#CITEREFSimpson2009), p. 87.

[^17]: [Simpson 2009](https://en.wikipedia.org/wiki/Second-order_arithmetic#CITEREFSimpson2009), p. 34.

[^18]: [Kohlenbach, Ulrich](https://en.wikipedia.org/wiki/Ulrich_Kohlenbach "Ulrich Kohlenbach") (2002). "Foundational and mathematical uses of higher types". *Reflections on the Foundations of Mathematics: Essays in honor of Solomon Feferman, Papers from the symposium held at Stanford University, Stanford, CA, December 11–13, 1998*. Lecture Notes in Logic. Vol. 15. Urbana, Illinois: Association for Symbolic Logic. pp. 92–116. [ISBN](https://en.wikipedia.org/wiki/ISBN_\(identifier\) "ISBN (identifier)") [1-56881-169-1](https://en.wikipedia.org/wiki/Special:BookSources/1-56881-169-1 "Special:BookSources/1-56881-169-1"). [MR](https://en.wikipedia.org/wiki/MR_\(identifier\) "MR (identifier)") [1943304](https://mathscinet.ams.org/mathscinet-getitem?mr=1943304).

[^19]: Hunter, James (2008). [*Higher order Reverse Topology*](https://hilbert.math.wisc.edu/logic/theses/hunter.pdf) (PDF) (Doctoral dissertation). University of Madison-Wisconsin.