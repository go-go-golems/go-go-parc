In [programming language theory](https://en.wikipedia.org/wiki/Programming_language_theory "Programming language theory") and [proof theory](https://en.wikipedia.org/wiki/Proof_theory "Proof theory"), the **Curry–Howard correspondence** is a direct relationship between [computer programs](https://en.wikipedia.org/wiki/Computer_program "Computer program") and [mathematical proofs](https://en.wikipedia.org/wiki/Mathematical_proof "Mathematical proof"). It is also known as the **Curry–Howard isomorphism** or **equivalence**, or the **proofs-as-programs** and **propositions-** or **formulae-as-types interpretation**.

It is a generalization of a syntactic [analogy](https://en.wikipedia.org/wiki/Analogy "Analogy") between systems of formal logic and computational calculi that was first discovered by the American [mathematician](https://en.wikipedia.org/wiki/Mathematician "Mathematician") [Haskell Curry](https://en.wikipedia.org/wiki/Haskell_Curry "Haskell Curry") and the [logician](https://en.wikipedia.org/wiki/Logician "Logician") [William Alvin Howard](https://en.wikipedia.org/wiki/William_Alvin_Howard "William Alvin Howard").[^1] It is the link between logic and computation that is usually attributed to Curry and Howard, although the idea is related to the operational interpretation of [intuitionistic logic](https://en.wikipedia.org/wiki/Intuitionistic_logic "Intuitionistic logic") given in various formulations by [L. E. J. Brouwer](https://en.wikipedia.org/wiki/L._E._J._Brouwer "L. E. J. Brouwer"), [Arend Heyting](https://en.wikipedia.org/wiki/Arend_Heyting "Arend Heyting") and [Andrey Kolmogorov](https://en.wikipedia.org/wiki/Andrey_Kolmogorov "Andrey Kolmogorov") (see [Brouwer–Heyting–Kolmogorov interpretation](https://en.wikipedia.org/wiki/Brouwer%E2%80%93Heyting%E2%80%93Kolmogorov_interpretation "Brouwer–Heyting–Kolmogorov interpretation")) [^2] and [Stephen Kleene](https://en.wikipedia.org/wiki/Stephen_Kleene "Stephen Kleene") (see [Realizability](https://en.wikipedia.org/wiki/Realizability "Realizability")). The relationship has been extended to include [category theory](https://en.wikipedia.org/wiki/Category_theory "Category theory") as the three-way **Curry–Howard–Lambek correspondence**.[^3] [^4] [^5]

## Origin, scope, and consequences

The beginnings of the Curry–Howard correspondence lie in several observations:

1. In 1934, [Curry](https://en.wikipedia.org/wiki/Haskell_Curry "Haskell Curry") observes that the [types](https://en.wikipedia.org/wiki/Typed_lambda_calculus "Typed lambda calculus") of the combinators could be seen as [axiom-schemes](https://en.wikipedia.org/wiki/Axiom-scheme "Axiom-scheme") for [intuitionistic](https://en.wikipedia.org/wiki/Intuitionism "Intuitionism") implicational logic.[^6]
2. In 1958, he observes that a certain kind of [proof system](https://en.wikipedia.org/wiki/Proof_calculus "Proof calculus"), referred to as [Hilbert-style deduction systems](https://en.wikipedia.org/wiki/Hilbert-style_deduction_system "Hilbert-style deduction system"), coincides on some fragment with the typed fragment of a standard [model of computation](https://en.wikipedia.org/wiki/Model_of_computation "Model of computation") known as [combinatory logic](https://en.wikipedia.org/wiki/Combinatory_logic "Combinatory logic").[^7]
3. In 1969 [Howard](https://en.wikipedia.org/wiki/William_Alvin_Howard "William Alvin Howard") observes that another, more "high-level" [proof system](https://en.wikipedia.org/wiki/Proof_calculus "Proof calculus"), referred to as [natural deduction](https://en.wikipedia.org/wiki/Natural_deduction "Natural deduction"), can be directly interpreted in its [intuitionistic](https://en.wikipedia.org/wiki/Intuitionistic "Intuitionistic") version as a typed variant of the [model of computation](https://en.wikipedia.org/wiki/Model_of_computation "Model of computation") known as [lambda calculus](https://en.wikipedia.org/wiki/Lambda_calculus "Lambda calculus").[^8]

Actually, Howard's first formulation of the isomorphism was referred to (a variant of) Gentzen's [sequent calculus](https://en.wikipedia.org/wiki/Sequent_calculus "Sequent calculus"). The observation that the isomorphism is best understood with [natural deduction](https://en.wikipedia.org/wiki/Natural_deduction "Natural deduction"), as well as the current formulation of the isomorphism itself, are due to [Per Martin-Löf](https://en.wikipedia.org/wiki/Martin-L%C3%B6f "Martin-Löf").[^9] The Curry–Howard correspondence is the observation that there is an isomorphism between the proof systems, and the models of computation. It is the statement that these two families of formalisms can be considered as identical.

If one abstracts on the peculiarities of either formalism, the following generalization arises: *a proof is a program, and the formula it proves is the type for the program*. More informally, this can be seen as an [analogy](https://en.wikipedia.org/wiki/Analogy "Analogy") that states that the [return type](https://en.wikipedia.org/wiki/Return_type "Return type") of a function (i.e., the type of values returned by a function) is analogous to a logical theorem, subject to hypotheses corresponding to the types of the argument values passed to the function; and that the program to compute that function is analogous to a proof of that theorem. This sets a form of [logic programming](https://en.wikipedia.org/wiki/Logic_programming "Logic programming") on a rigorous foundation: *proofs can be represented as programs, and especially as lambda terms*, or *proofs can be **run***.

The correspondence has been the starting point of a large range of new research after its discovery, leading to a new class of [formal systems](https://en.wikipedia.org/wiki/Formal_system "Formal system") designed to act both as a [proof system](https://en.wikipedia.org/wiki/Proof_calculus "Proof calculus") and as a typed [programming language](https://en.wikipedia.org/wiki/Programming_language "Programming language") based on [functional programming](https://en.wikipedia.org/wiki/Functional_programming "Functional programming"). This includes [Martin-Löf](https://en.wikipedia.org/wiki/Martin-L%C3%B6f "Martin-Löf") 's [intuitionistic type theory](https://en.wikipedia.org/wiki/Intuitionistic_type_theory "Intuitionistic type theory") and [Coquand's](https://en.wikipedia.org/wiki/Thierry_Coquand "Thierry Coquand") [calculus of constructions](https://en.wikipedia.org/wiki/Calculus_of_constructions "Calculus of constructions") (CoC), two calculi in which proofs are regular objects of the discourse and in which one can state properties of proofs the same way as of any program. This field of research is usually referred to as modern [type theory](https://en.wikipedia.org/wiki/Type_theory "Type theory").

Such [typed lambda calculi](https://en.wikipedia.org/wiki/Typed_lambda_calculus "Typed lambda calculus") derived from the Curry–Howard paradigm led to software like Rocq in which proofs seen as programs can be formalized, checked, and run.

A converse direction is to *use a program to extract a proof*, given its [correctness](https://en.wikipedia.org/wiki/Program_correctness "Program correctness"), an area of research closely related to [proof-carrying code](https://en.wikipedia.org/wiki/Proof-carrying_code "Proof-carrying code"). This is only feasible if the [programming language](https://en.wikipedia.org/wiki/Programming_language "Programming language") the program is written for is very richly typed: the development of such type systems has been partly motivated by the wish to make the Curry–Howard correspondence practically relevant.

The Curry–Howard correspondence also raised new questions regarding the computational content of proof concepts that were not covered by the original works of Curry and Howard. In particular, [classical logic](https://en.wikipedia.org/wiki/Classical_logic "Classical logic") has been shown to correspond to the ability to manipulate the [continuation](https://en.wikipedia.org/wiki/Continuation "Continuation") of programs and the symmetry of [sequent calculus](https://en.wikipedia.org/wiki/Sequent_calculus "Sequent calculus") to express the duality between the two [evaluation strategies](https://en.wikipedia.org/wiki/Evaluation_strategy "Evaluation strategy") known as call-by-name and call-by-value.

Because of the possibility of writing non-terminating programs, [Turing-complete](https://en.wikipedia.org/wiki/Turing_completeness "Turing completeness") models of computation (such as languages with arbitrary [recursive functions](https://en.wikipedia.org/wiki/Recursion_\(computer_science\) "Recursion (computer science)")) must be interpreted with care, as naive application of the correspondence leads to an inconsistent logic. The best way of dealing with arbitrary computation from a logical point of view is still an actively debated research question, but one popular approach is based on using [monads](https://en.wikipedia.org/wiki/Monad_\(functional_programming\) "Monad (functional programming)") to segregate provably terminating from potentially non-terminating code (an approach that also generalizes to much richer models of computation,[^10] and is itself related to modal logic by a natural extension of the Curry–Howard isomorphism [^11]). A more radical approach, advocated by [total functional programming](https://en.wikipedia.org/wiki/Total_functional_programming "Total functional programming"), is to eliminate unrestricted recursion (and forgo [Turing completeness](https://en.wikipedia.org/wiki/Turing_completeness "Turing completeness"), although still retaining high computational complexity), using more controlled [corecursion](https://en.wikipedia.org/wiki/Corecursion "Corecursion") wherever non-terminating behavior is actually desired.

## General formulation

In its more general formulation, the Curry–Howard correspondence is a correspondence between formal [proof calculi](https://en.wikipedia.org/wiki/Proof_calculus "Proof calculus") and [type systems](https://en.wikipedia.org/wiki/Type_systems "Type systems") for [models of computation](https://en.wikipedia.org/wiki/Model_of_computation "Model of computation"). In particular, it splits into two correspondences. One at the level of [formulas](https://en.wikipedia.org/wiki/Formula_\(mathematical_logic\) "Formula (mathematical logic)") and [types](https://en.wikipedia.org/wiki/Data_type "Data type") that is independent of which particular proof system or model of computation is considered, and one at the level of [proofs](https://en.wikipedia.org/wiki/Mathematical_proof "Mathematical proof") and [programs](https://en.wikipedia.org/wiki/Computer_program "Computer program") which, this time, is specific to the particular choice of proof system and model of computation considered.

At the level of formulas and types, the correspondence says that implication behaves the same as a function type, conjunction as a "product" type (this may be called a tuple, a struct, a list, or some other term depending on the language), disjunction as a sum type (this type may be called a union), the false formula as the empty type and the true formula as a unit type (whose sole member is the null object). Quantifiers correspond to [dependent](https://en.wikipedia.org/wiki/Dependent_type "Dependent type") function space or products (as appropriate). This is summarized in the following table:

| Logic side | Programming side |
| --- | --- |
| formula | type |
| proof | term |
| formula is true | type has an element |
| formula is false | type does not have an element |
| logical constant ⊤ (truth) | [unit type](https://en.wikipedia.org/wiki/Unit_type "Unit type") |
| logical constant ⊥ (falsehood) | [empty type](https://en.wikipedia.org/wiki/Empty_type "Empty type") |
| [implication](https://en.wikipedia.org/wiki/Logical_implication "Logical implication") | [function type](https://en.wikipedia.org/wiki/Function_type "Function type") |
| [conjunction](https://en.wikipedia.org/wiki/Logical_conjunction "Logical conjunction") | [product type](https://en.wikipedia.org/wiki/Product_type "Product type") |
| [disjunction](https://en.wikipedia.org/wiki/Logical_disjunction "Logical disjunction") | [sum type](https://en.wikipedia.org/wiki/Sum_type "Sum type") |
| [universal quantification](https://en.wikipedia.org/wiki/Universal_quantification "Universal quantification") | [dependent product type](https://en.wikipedia.org/wiki/Dependent_type#%CE%A0_type "Dependent type") |
| [existential quantification](https://en.wikipedia.org/wiki/Existential_quantification "Existential quantification") | [dependent sum type](https://en.wikipedia.org/wiki/Dependent_type#%CE%A3_type "Dependent type") |

At the level of proof systems and models of computations, the correspondence mainly shows the identity of structure, first, between some particular formulations of systems known as [Hilbert-style deduction system](https://en.wikipedia.org/wiki/Hilbert-style_deduction_system "Hilbert-style deduction system") and [combinatory logic](https://en.wikipedia.org/wiki/Combinatory_logic "Combinatory logic"), and, secondly, between some particular formulations of systems known as [natural deduction](https://en.wikipedia.org/wiki/Natural_deduction "Natural deduction") and [lambda calculus](https://en.wikipedia.org/wiki/Lambda_calculus "Lambda calculus").

| Logic side | Programming side |
| --- | --- |
| [Hilbert-style deduction system](https://en.wikipedia.org/wiki/Hilbert-style_deduction_system "Hilbert-style deduction system") | type system for [combinatory logic](https://en.wikipedia.org/wiki/Combinatory_logic "Combinatory logic") |
| [natural deduction](https://en.wikipedia.org/wiki/Natural_deduction "Natural deduction") | type system for [lambda calculus](https://en.wikipedia.org/wiki/Lambda_calculus "Lambda calculus") |

Between the natural deduction system and the lambda calculus there are the following correspondences:

| Logic side | Programming side |
| --- | --- |
| [hypotheses](https://en.wikipedia.org/wiki/Hypotheses "Hypotheses") | [free variables](https://en.wikipedia.org/wiki/Free_variables_and_bound_variables "Free variables and bound variables") |
| [implication elimination](https://en.wikipedia.org/wiki/Implication_elimination "Implication elimination") (*modus ponens*) | [application](https://en.wikipedia.org/wiki/Apply "Apply") |
| [implication introduction](https://en.wikipedia.org/wiki/Implication_introduction "Implication introduction") | abstraction |

## Corresponding systems

### Intuitionistic Hilbert-style deduction systems and typed combinatory logic

It was at the beginning a simple remark in Curry and Feys's 1958 book on combinatory logic: the simplest types for the basic combinators K and S of [combinatory logic](https://en.wikipedia.org/wiki/Combinatory_logic "Combinatory logic") surprisingly corresponded to the respective [axiom schemes](https://en.wikipedia.org/wiki/Axiom_scheme "Axiom scheme") *α* → (*β* → *α*) and (*α* → (*β* → *γ*)) → ((*α* → *β*) → (*α* → *γ*)) used in [Hilbert-style deduction systems](https://en.wikipedia.org/wiki/Hilbert-style_deduction_system "Hilbert-style deduction system"). For this reason, these schemes are now often called axioms K and S. Examples of programs seen as proofs in a Hilbert-style logic are given [below](https://en.wikipedia.org/wiki/Curry%E2%80%93Howard_correspondence#Examples).

If one restricts to the implicational intuitionistic fragment, a simple way to formalize logic in Hilbert's style is as follows. Let Γ be a finite collection of formulas, considered as hypotheses. Then δ is *derivable* from Γ, denoted Γ ⊢ δ, in the following cases:

- δ is an hypothesis, i.e. it is a formula of Γ,
- δ is an instance of an axiom scheme; i.e., under the most common axiom system:
	- δ has the form *α* → (*β* → *α*), or
		- δ has the form (*α* → (*β* → *γ*)) → ((*α* → *β*) → (*α* → *γ*)),
- δ follows by deduction, i.e., for some *α*, both *α* → *δ* and *α* are already derivable from Γ (this is the rule of [modus ponens](https://en.wikipedia.org/wiki/Modus_ponens "Modus ponens"))

This can be formalized using [inference rules](https://en.wikipedia.org/wiki/Inference_rules "Inference rules"), as in the left column of the following table.

Typed combinatory logic can be formulated using a similar syntax: let Γ be a finite collection of variables, annotated with their types. A term T (also annotated with its type) will depend on these variables \[Γ ⊢ T:*δ*\] when:

- T is one of the variables in Γ,
- T is a basic combinator; i.e., under the most common combinator basis:
	- T is K:*α* → (*β* → *α*) \[where *α* and *β* denote the types of its arguments\], or
		- T is S:(*α* → (*β* → *γ*)) → ((*α* → *β*) → (*α* → *γ*)),
- T is the composition of two subterms which depend on the variables in Γ.

The generation rules defined here are given in the right-column below. Curry's remark simply states that both columns are in one-to-one correspondence. The restriction of the correspondence to [intuitionistic logic](https://en.wikipedia.org/wiki/Intuitionistic_logic "Intuitionistic logic") means that some [classical](https://en.wikipedia.org/wiki/Classical_logic "Classical logic") [tautologies](https://en.wikipedia.org/wiki/Tautology_\(logic\) "Tautology (logic)"), such as [Peirce's law](https://en.wikipedia.org/wiki/Peirce%27s_law "Peirce's law") ((*α* → *β*) → *α*) → *α*, are excluded from the correspondence.

| Hilbert-style intuitionistic implicational logic | Typed combinatory logic |
| --- | --- |
| ${\displaystyle {\frac {\alpha \in \Gamma }{\Gamma \vdash \alpha }}\qquad \qquad {\text{Assum}}}$ | ${\displaystyle {\frac {x:\alpha \in \Gamma }{\Gamma \vdash x:\alpha }}}$ |
| ${\displaystyle {\frac {}{\Gamma \vdash \alpha \rightarrow (\beta \rightarrow \alpha )}}\qquad {\text{Ax}}_{K}}$ | ${\displaystyle {\frac {}{\Gamma \vdash K:\alpha \rightarrow (\beta \rightarrow \alpha )}}}$ |
| ${\displaystyle {\frac {}{\Gamma \vdash (\alpha \!\rightarrow \!(\beta \!\rightarrow \!\gamma ))\!\rightarrow \!((\alpha \!\rightarrow \!\beta )\!\rightarrow \!(\alpha \!\rightarrow \!\gamma ))}}\;{\text{Ax}}_{S}}$ | ${\displaystyle {\frac {}{\Gamma \vdash S:(\alpha \!\rightarrow \!(\beta \!\rightarrow \!\gamma ))\!\rightarrow \!((\alpha \!\rightarrow \!\beta )\!\rightarrow \!(\alpha \!\rightarrow \!\gamma ))}}}$ |
| ${\displaystyle {\frac {\Gamma \vdash \alpha \rightarrow \beta \qquad \Gamma \vdash \alpha }{\Gamma \vdash \beta }}\quad {\text{Modus Ponens}}}$ | ${\displaystyle {\frac {\Gamma \vdash E_{1}:\alpha \rightarrow \beta \qquad \Gamma \vdash E_{2}:\alpha }{\Gamma \vdash E_{1}\;E_{2}:\beta }}}$ |

Seen at a more abstract level, the correspondence can be restated as shown in the following table. Especially, the [deduction theorem](https://en.wikipedia.org/wiki/Deduction_theorem "Deduction theorem") specific to Hilbert-style logic matches the process of [abstraction elimination](https://en.wikipedia.org/wiki/Combinatory_logic#Conversion_of_a_lambda_term_to_an_equivalent_combinatorial_term "Combinatory logic") of combinatory logic.

| Logic side | Programming side |
| --- | --- |
| assumption | variable |
| axiom schemes | combinators |
| modus ponens | application |
| [deduction theorem](https://en.wikipedia.org/wiki/Deduction_theorem "Deduction theorem") | [abstraction elimination](https://en.wikipedia.org/wiki/Combinatory_logic#Conversion_of_a_lambda_term_to_an_equivalent_combinatorial_term "Combinatory logic") |

Thanks to the correspondence, results from combinatory logic can be transferred to Hilbert-style logic and vice versa. For instance, the notion of [reduction](https://en.wikipedia.org/wiki/Combinatory_logic#Reduction_in_combinatory_logic "Combinatory logic") of terms in combinatory logic can be transferred to Hilbert-style logic and it provides a way to canonically transform proofs into other proofs of the same statement. One can also transfer the notion of normal terms to a notion of normal proofs, expressing that the hypotheses of the axioms never need to be all detached (since otherwise a simplification can happen).

Conversely, the non provability in intuitionistic logic of [Peirce's law](https://en.wikipedia.org/wiki/Peirce%27s_law "Peirce's law") can be transferred back to combinatory logic: there is no typed term of combinatory logic that is typable with type

((*α* → *β*) → *α*) → *α*.

Results on the completeness of some sets of combinators or axioms can also be transferred. For instance, the fact that the combinator **X** constitutes a [one-point basis](https://en.wikipedia.org/wiki/Combinatory_logic#One-point_basis "Combinatory logic") of (extensional) combinatory logic implies that the single axiom scheme

(((*α* → (*β* → *γ*)) → ((*α* → *β*) → (*α* → *γ*))) → ((*δ* → (*ε* → *δ*)) → *ζ*)) → *ζ*,

which is the [principal type](https://en.wikipedia.org/wiki/Principal_type "Principal type") of **X**, is an adequate replacement to the combination of the axiom schemes

*α* → (*β* → *α*) and

(*α* → (*β* → *γ*)) → ((*α* → *β*) → (*α* → *γ*)).

### Intuitionistic natural deduction and typed lambda calculus

After [Curry](https://en.wikipedia.org/wiki/Haskell_Curry "Haskell Curry") emphasized the syntactic correspondence between intuitionistic [Hilbert-style deduction](https://en.wikipedia.org/wiki/Hilbert-style_deduction_system "Hilbert-style deduction system") and typed [combinatory logic](https://en.wikipedia.org/wiki/Combinatory_logic "Combinatory logic"), [Howard](https://en.wikipedia.org/wiki/William_Alvin_Howard "William Alvin Howard") made explicit in 1969 a syntactic analogy between the programs of [simply typed lambda calculus](https://en.wikipedia.org/wiki/Simply_typed_lambda_calculus "Simply typed lambda calculus") and the proofs of [natural deduction](https://en.wikipedia.org/wiki/Natural_deduction "Natural deduction"). Below, the left-hand side formalizes intuitionistic implicational natural deduction as a calculus of [sequents](https://en.wikipedia.org/wiki/Sequent "Sequent") (the use of sequents is standard in discussions of the Curry–Howard isomorphism as it allows the deduction rules to be stated more cleanly) with implicit weakening and the right-hand side shows the typing rules of [lambda calculus](https://en.wikipedia.org/wiki/Lambda_calculus "Lambda calculus"). In the left-hand side, Γ, Γ <sub>1</sub> and Γ <sub>2</sub> denote ordered sequences of formulas while in the right-hand side, they denote sequences of named (i.e., typed) formulas with all names different.

| Intuitionistic implicational natural deduction | Lambda calculus type assignment rules |
| --- | --- |
| ${\displaystyle {\frac {}{\Gamma _{1},\alpha ,\Gamma _{2}\vdash \alpha }}{\text{Ax}}}$ | ${\displaystyle {\frac {}{\Gamma _{1},x:\alpha ,\Gamma _{2}\vdash x:\alpha }}}$ |
| ${\displaystyle {\frac {\Gamma ,\alpha \vdash \beta }{\Gamma \vdash \alpha \rightarrow \beta }}\rightarrow I}$ | ${\displaystyle {\frac {\Gamma ,x:\alpha \vdash t:\beta }{\Gamma \vdash (\lambda x\!:\!\alpha .~t):\alpha \rightarrow \beta }}}$ |
| ${\displaystyle {\frac {\Gamma \vdash \alpha \rightarrow \beta \qquad \Gamma \vdash \alpha }{\Gamma \vdash \beta }}\rightarrow E}$ | ${\displaystyle {\frac {\Gamma \vdash t:\alpha \rightarrow \beta \qquad \Gamma \vdash u:\alpha }{\Gamma \vdash t\;u:\beta }}}$ |

To paraphrase the correspondence, proving Γ ⊢ *α* means having a program that, given values with the types listed in Γ, manufactures an object of type *α*. An axiom/hypothesis corresponds to the introduction of a new variable with a new, unconstrained type, the → *I* rule corresponds to function abstraction and the → *E* rule corresponds to [function application](https://en.wikipedia.org/wiki/Function_application "Function application"). Observe that the correspondence is not exact if the context Γ is taken to be a set of formulas as, e.g., the λ-terms λ *x*.λ *y*.*x* and λ *x*.λ *y*.*y* of type *α* → *α* → *α* would not be distinguished in the correspondence. Examples are given [below](https://en.wikipedia.org/wiki/Curry%E2%80%93Howard_correspondence#Examples).

Howard showed that the correspondence extends to other connectives of the logic and other constructions of simply typed lambda calculus. Seen at an abstract level, the correspondence can then be summarized as shown in the following table. Especially, it also shows that the notion of normal forms in [lambda calculus](https://en.wikipedia.org/wiki/Lambda_calculus "Lambda calculus") matches [Prawitz](https://en.wikipedia.org/wiki/Dag_Prawitz "Dag Prawitz") 's notion of normal deduction in [natural deduction](https://en.wikipedia.org/wiki/Natural_deduction "Natural deduction"), from which it follows that the algorithms for the [type inhabitation problem](https://en.wikipedia.org/wiki/Type_inhabitation_problem "Type inhabitation problem") can be turned into algorithms for deciding [intuitionistic](https://en.wikipedia.org/wiki/Intuitionistic "Intuitionistic") provability.

| Logic side | Programming side |
| --- | --- |
| axiom/hypothesis | variable |
| introduction rule | constructor |
| elimination rule | destructor |
| normal deduction | normal form |
| normalisation of deductions | [weak normalisation](https://en.wikipedia.org/wiki/Normalization_property_\(lambda-calculus\) "Normalization property (lambda-calculus)") |
| provability | [type inhabitation problem](https://en.wikipedia.org/wiki/Type_inhabitation_problem "Type inhabitation problem") |
| intuitionistic tautology | universally inhabited type |

Howard's correspondence naturally extends to other extensions of [natural deduction](https://en.wikipedia.org/wiki/Natural_deduction "Natural deduction") and [simply typed lambda calculus](https://en.wikipedia.org/wiki/Simply_typed_lambda_calculus "Simply typed lambda calculus"). Here is a non-exhaustive list:

- Girard-Reynolds [System F](https://en.wikipedia.org/wiki/System_F "System F") as a common language for both second-order propositional logic and polymorphic lambda calculus,
- [higher-order logic](https://en.wikipedia.org/wiki/Higher-order_logic "Higher-order logic") and Girard's [System F <sub>ω</sub>](https://en.wikipedia.org/wiki/System_F "System F")
- inductive types as [algebraic data type](https://en.wikipedia.org/wiki/Algebraic_data_type "Algebraic data type")
- necessity ${\displaystyle \Box }$ in [modal logic](https://en.wikipedia.org/wiki/Modal_logic "Modal logic") and staged computation [^12]
- possibility ${\displaystyle \Diamond }$ in [modal logic](https://en.wikipedia.org/wiki/Modal_logic "Modal logic") and monadic types for effects [^11]
- The λ <sub>I</sub> calculus (where abstraction is restricted to *λx*.*E* where *x* has at least one free occurrence in *E)* and **CL** <sub>I</sub> calculus correspond to [relevant logic](https://en.wikipedia.org/wiki/Relevant_logic "Relevant logic").[^13]
- The local truth (∇) modality in [Grothendieck topology](https://en.wikipedia.org/wiki/Grothendieck_topology "Grothendieck topology") or the equivalent "lax" modality (◯) of Benton, Bierman, and de Paiva (1998) correspond to CL-logic describing "computation types".[^14]

### Classical logic and control operators

At the time of Curry, and also at the time of Howard, the proofs-as-programs correspondence concerned only [intuitionistic logic](https://en.wikipedia.org/wiki/Intuitionistic_logic "Intuitionistic logic"), i.e. a logic in which, in particular, [Peirce's law](https://en.wikipedia.org/wiki/Peirce%27s_law "Peirce's law") was *not* deducible. The extension of the correspondence to Peirce's law and hence to [classical logic](https://en.wikipedia.org/wiki/Classical_logic "Classical logic") became clear from the work of Griffin on typing operators that capture the evaluation context of a given program execution so that this evaluation context can be later on reinstalled. The basic Curry–Howard-style correspondence for classical logic is given below. Note the correspondence between the [double-negation translation](https://en.wikipedia.org/wiki/Double-negation_translation "Double-negation translation") used to map classical proofs to intuitionistic logic and the [continuation-passing-style](https://en.wikipedia.org/wiki/Continuation-passing_style "Continuation-passing style") translation used to map lambda terms involving control to pure lambda terms. More particularly, call-by-name continuation-passing-style translations relates to [Kolmogorov](https://en.wikipedia.org/wiki/Kolmogorov "Kolmogorov") 's double negation translation and call-by-value continuation-passing-style translations relates to a kind of double-negation translation due to Kuroda.

| Logic side | Programming side |
| --- | --- |
| [Peirce's law](https://en.wikipedia.org/wiki/Peirce%27s_law "Peirce's law"): ((*α* → *β*) → *α*) → *α* | [call-with-current-continuation](https://en.wikipedia.org/wiki/Call-with-current-continuation "Call-with-current-continuation") |
| [double-negation translation](https://en.wikipedia.org/wiki/Double-negation_translation "Double-negation translation") | [continuation-passing-style translation](https://en.wikipedia.org/wiki/Continuation-passing_style "Continuation-passing style") |

A finer Curry–Howard correspondence exists for classical logic if one defines classical logic not by adding an axiom such as [Peirce's law](https://en.wikipedia.org/wiki/Peirce%27s_law "Peirce's law"), but by allowing several conclusions in sequents. In the case of classical natural deduction, there exists a proofs-as-programs correspondence with the typed programs of Parigot's [λμ-calculus](https://en.wikipedia.org/wiki/Lambda-mu_calculus "Lambda-mu calculus").

### Sequent calculus

A proofs-as-programs correspondence can be settled for the formalism known as [Gentzen](https://en.wikipedia.org/wiki/Gentzen "Gentzen") 's [sequent calculus](https://en.wikipedia.org/wiki/Sequent_calculus "Sequent calculus") but it is not a correspondence with a well-defined pre-existing model of computation as it was for Hilbert-style and natural deductions.

Sequent calculus is characterized by the presence of left introduction rules, right introduction rule and a cut rule that can be eliminated. The structure of sequent calculus relates to a calculus whose structure is close to the one of some [abstract machines](https://en.wikipedia.org/wiki/Abstract_machine "Abstract machine"). The informal correspondence is as follows:

| Logic side | Programming side |
| --- | --- |
| cut elimination | reduction in a form of abstract machine |
| right introduction rules | constructors of code |
| left introduction rules | constructors of evaluation stacks |
| priority to right-hand side in cut-elimination | [call-by-name](https://en.wikipedia.org/wiki/Call-by-name "Call-by-name") reduction |
| priority to left-hand side in cut-elimination | [call-by-value](https://en.wikipedia.org/wiki/Call-by-value "Call-by-value") reduction |

### Prawitz's 1968 homomorphism

In a paper published in 1970, but drawn from a talk given at the First Scandinavian Logic Symposium, held in Åbo/Turku in 1968, [Dag Prawitz](https://en.wikipedia.org/wiki/Dag_Prawitz "Dag Prawitz") defined a homomorphism between [natural deduction](https://en.wikipedia.org/wiki/Natural_deduction "Natural deduction") derivations for minimal and intuitionistic first-order logic and construction terms from a language very similar to typed lambda calculus (the correspondence stems from a proof of soundness of those logics over the language of constructions terms).[^15] Although Prawitz's homomorphism is less powerful than the Curry-Howard isomorphism, with a stronger type-language it becomes an isomorphism too, though still missing dependent types. Prawitz was presumably unaware of Howard's work, especially in view of the fact that the talk from which his 1970 paper is drawn was delivered one year before Howard's manuscript started circulating.

### The role of de Bruijn

[N. G. de Bruijn](https://en.wikipedia.org/wiki/Nicolaas_Govert_de_Bruijn "Nicolaas Govert de Bruijn") used the lambda notation for representing proofs of the theorem checker [Automath](https://en.wikipedia.org/wiki/Automath "Automath"), and represented propositions as "categories" of their proofs. It was in the late 1960s at the same period of time Howard wrote his manuscript; de Bruijn was likely unaware of Howard's work, and stated the correspondence independently.[^16] Some researchers tend to use the term Curry–Howard–de Bruijn correspondence in place of Curry–Howard correspondence.

### BHK interpretation

The [BHK interpretation](https://en.wikipedia.org/wiki/BHK_interpretation "BHK interpretation") interprets intuitionistic proofs as functions but it does not specify the class of functions relevant for the interpretation. If one takes lambda calculus for this class of function, then the [BHK interpretation](https://en.wikipedia.org/wiki/BHK_interpretation "BHK interpretation") tells the same as Howard's correspondence between natural deduction and lambda calculus.

### Realizability

[Kleene](https://en.wikipedia.org/wiki/Stephen_Cole_Kleene "Stephen Cole Kleene") 's recursive [realizability](https://en.wikipedia.org/wiki/Realizability "Realizability") splits proofs of intuitionistic arithmetic into the pair of a recursive function and of a proof of a formula expressing that the recursive function "realizes", i.e. correctly instantiates the disjunctions and existential quantifiers of the initial formula so that the formula gets true.

[Kreisel](https://en.wikipedia.org/wiki/Georg_Kreisel "Georg Kreisel") 's modified realizability applies to intuitionistic higher-order predicate logic and shows that the [simply typed lambda term](https://en.wikipedia.org/wiki/Simply_typed_lambda_calculus "Simply typed lambda calculus") inductively extracted from the proof realizes the initial formula. In the case of propositional logic, it coincides with Howard's statement: the extracted lambda term is the proof itself (seen as an untyped lambda term) and the realizability statement is a paraphrase of the fact that the extracted lambda term has the type that the formula means (seen as a type).

[Gödel](https://en.wikipedia.org/wiki/Kurt_G%C3%B6del "Kurt Gödel") 's [dialectica interpretation](https://en.wikipedia.org/wiki/Dialectica_interpretation "Dialectica interpretation") realizes (an extension of) intuitionistic arithmetic with computable functions. The connection with lambda calculus is unclear, even in the case of natural deduction.

### Curry–Howard–Lambek correspondence

[Joachim Lambek](https://en.wikipedia.org/wiki/Joachim_Lambek "Joachim Lambek") showed in the early 1970s that the proofs of intuitionistic propositional logic and the combinators of typed [combinatory logic](https://en.wikipedia.org/wiki/Combinatory_logic "Combinatory logic") share a common equational theory, the theory of [cartesian closed categories](https://en.wikipedia.org/wiki/Cartesian_closed_categories "Cartesian closed categories"). The expression Curry–Howard–Lambek correspondence is now used by some people to refer to the relationships between intuitionistic logic, typed lambda calculus and cartesian closed categories. Under this correspondence, objects of a cartesian-closed category can be interpreted as propositions (types), and morphisms as deductions mapping a set of assumptions ([typing context](https://en.wikipedia.org/wiki/Typing_context "Typing context")) to a valid consequent (well-typed term).[^17]

Lambek's correspondence is a correspondence of equational theories, abstracting away from dynamics of computation such as beta reduction and term normalization, and is not the expression of a syntactic identity of structures as it is the case for each of Curry's and Howard's correspondences: i.e. the structure of a well-defined morphism in a cartesian-closed category is not comparable to the structure of a proof of the corresponding judgment in either Hilbert-style logic or natural deduction. For example, it is not possible to state or prove that a morphism is normalizing, establish a Church-Rosser type theorem, or speak of a "strongly normalizing" cartesian closed category. To clarify this distinction, the underlying syntactic structure of cartesian closed categories is rephrased below.

Objects (propositions/types) include

- ${\displaystyle \top }$ as an object
- given ${\displaystyle \alpha }$ and ${\displaystyle \beta }$ as objects, then ${\displaystyle \alpha \times \beta }$ and ${\displaystyle \alpha \rightarrow \beta }$ as objects.

Morphisms (deductions/terms) include

- identities: ${\displaystyle {\text{id}}_{\alpha }:\alpha \to \alpha }$
- composition: if ${\displaystyle t:\alpha \to \beta }$ and ${\displaystyle u:\beta \to \gamma }$ are morphisms ${\displaystyle u\circ t:\alpha \to \gamma }$ is a morphism
- [terminal morphisms](https://en.wikipedia.org/wiki/Terminal_object "Terminal object"): ${\displaystyle \star _{\alpha }:\alpha \to \top }$
- products: if ${\displaystyle t:\alpha \to \beta }$ and ${\displaystyle u:\alpha \to \gamma }$ are morphisms, ${\displaystyle (t,u):\alpha \to \beta \times \gamma }$ is a morphism
- projections: ${\displaystyle \pi _{\alpha ,\beta ,1}:\alpha \times \beta \to \alpha }$ and ${\displaystyle \pi _{\alpha ,\beta ,2}:\alpha \times \beta \to \beta }$
- evaluation: ${\displaystyle {\text{eval}}_{\alpha ,\beta }:(\alpha \to \beta )\times \alpha \to \beta }$
- currying: if ${\displaystyle t:\alpha \times \beta \to \gamma }$ is a morphism, ${\displaystyle \lambda t:\alpha \to \beta \to \gamma }$ is a morphism.

Equivalently to the annotations above, well-defined morphisms (typed terms) in any cartesian-closed category can be constructed according to the following [typing rules](https://en.wikipedia.org/wiki/Typing_rule "Typing rule"). The usual categorical morphism notation ${\displaystyle f:\alpha \to \beta }$ is replaced with [typing context](https://en.wikipedia.org/wiki/Typing_context "Typing context") notation ${\displaystyle \alpha \vdash f:\beta }$.

Identity:

${\displaystyle {\frac {}{\alpha \vdash {\text{id}}:\alpha }}}$

Composition:

${\displaystyle {\frac {\alpha \vdash t:\beta \qquad \beta \vdash u:\gamma }{\alpha \vdash u\circ t:\gamma }}}$

[Unit type](https://en.wikipedia.org/wiki/Unit_type "Unit type") ([terminal object](https://en.wikipedia.org/wiki/Terminal_object "Terminal object")):

${\displaystyle {\frac {}{\alpha \vdash \star :\top }}}$

Cartesian product:

${\displaystyle {\frac {\alpha \vdash t:\beta \qquad \alpha \vdash u:\gamma }{\alpha \vdash (t,u):\beta \times \gamma }}}$

Left and right projection:

${\displaystyle {\frac {}{\alpha \times \beta ~\vdash ~\pi _{1}:\alpha }}\qquad {\frac {}{\alpha \times \beta ~\vdash ~\pi _{2}:\beta }}}$

[Currying](https://en.wikipedia.org/wiki/Currying "Currying"):

${\displaystyle {\frac {\alpha \times \beta ~\vdash ~t:\gamma }{\alpha \vdash \lambda t:\beta \to \gamma }}}$

[Application](https://en.wikipedia.org/wiki/Apply "Apply"):

${\displaystyle {\frac {}{(\alpha \rightarrow \beta )\times \alpha \vdash {\text{eval}}:\beta }}}$

Finally, the equations of the category are

- ${\displaystyle {\text{id}}\circ t=t}$
- ${\displaystyle t\circ {\text{id}}=t}$
- ${\displaystyle (v\circ u)\circ t=v\circ (u\circ t)}$
- ${\displaystyle \star ={\text{id}}}$ (if well-typed)
- ${\displaystyle \star \circ u=\star }$
- ${\displaystyle \pi _{1}\circ (t,u)=t}$
- ${\displaystyle \pi _{2}\circ (t,u)=u}$
- ${\displaystyle (\pi _{1},\pi _{2})=id}$
- ${\displaystyle (t_{1},t_{2})\circ u=(t_{1}\circ u,t_{2}\circ u)}$
- ${\displaystyle {\text{eval}}\circ (\lambda t\circ \pi _{1},\pi _{2})=t}$
- ${\displaystyle \lambda {\text{eval}}={\text{id}}}$
- ${\displaystyle \lambda t\circ u=\lambda (t\circ (u\circ \pi _{1},\pi _{2}))}$

These equations imply the following ${\displaystyle \eta }$ -laws:

- ${\displaystyle (\pi _{1}\circ t,\pi _{2}\circ t)=t}$
- ${\displaystyle \lambda ({\text{eval}}\circ (t\circ \pi _{1},\pi _{2}))=t}$

Now, there exists t such that ${\displaystyle \alpha _{1}\times \ldots \times \alpha _{n}\vdash t:\beta }$ iff ${\displaystyle \alpha _{1},\ldots ,\alpha _{n}\vdash \beta }$ is provable in implicational intuitionistic logic.

## Examples

Thanks to the Curry–Howard correspondence, a typed expression whose type corresponds to a logical formula is analogous to a proof of that formula. Here are examples.

### The identity combinator seen as a proof of α → α in Hilbert-style logic

As an example, consider a proof of the theorem *α* → *α*. In [lambda calculus](https://en.wikipedia.org/wiki/Lambda_calculus "Lambda calculus"), this is the type of the identity function **I** = *λx*.*x* and in combinatory logic, the identity function is obtained by applying **S** = *λfgx*.*fx* (*gx*) twice to **K** = *λxy*.*x*. That is, **I** = ((**S** **K**) **K**). As a description of a proof, this says that the following steps can be used to prove *α* → *α*:

- instantiate the second axiom scheme with the formulas α, *β* → *α* and α to obtain a proof of (*α* → ((*β* → *α*) → *α*)) → ((*α* → (*β* → *α*)) → (*α* → *α*)),
- instantiate the first axiom scheme once with α and *β* → *α* to obtain a proof of *α* → ((*β* → *α*) → *α*),
- instantiate the first axiom scheme a second time with α and β to obtain a proof of *α* → (*β* → *α*),
- apply modus ponens twice to obtain a proof of *α* → *α*

In general, the procedure is that whenever the program contains an application of the form (*P* *Q*), these steps should be followed:

1. First prove theorems corresponding to the types of *P* and *Q*.
2. Since *P* is being applied to *Q*, the type of *P* must have the form *α* → *β* and the type of *Q* must have the form α for some α and β. Therefore, it is possible to detach the conclusion, β, via the modus ponens rule.

### The composition combinator seen as a proof of (β → α) → (γ → β) → γ → α in Hilbert-style logic

As a more complicated example, let's look at the theorem that corresponds to the **B** function. The type of **B** is (*β* → *α*) → (*γ* → *β*) → *γ* → *α*. **B** is equivalent to (**S** (**K** **S**) **K**). This is our roadmap for the proof of the theorem (*β* → *α*) → (*γ* → *β*) → *γ* → *α*.

The first step is to construct (**K** **S**). To make the antecedent of the **K** axiom look like the **S** axiom, set α equal to (*α* → *β* → *γ*) → (*α* → *β*) → *α* → *γ*, and β equal to δ (to avoid variable collisions):

**K**: *α* → *β* → *α*

**K** \[*α* = (*α* → *β* → *γ*) → (*α* → *β*) → *α* → *γ*, *β* = δ\]: ((*α* → *β* → *γ*) → (*α* → *β*) → *α* → *γ*) → *δ* → (*α* → *β* → *γ*) → (*α* → *β*) → *α* → *γ*

Since the antecedent here is just **S**, the consequent can be detached using Modus Ponens:

**K S**: *δ* → (*α* → *β* → *γ*) → (*α* → *β*) → *α* → *γ*

This is the theorem that corresponds to the type of (**K** **S**). Now apply **S** to this expression. Taking **S** as follows

**S**: (*α* → *β* → *γ*) → (*α* → *β*) → *α* → *γ*,

put *α* = *δ*, *β* = *α* → *β* → *γ*, and *γ* = (*α* → *β*) → *α* → *γ*, yielding

**S** \[*α* = *δ*, *β* = *α* → *β* → *γ*, *γ* = (*α* → *β*) → *α* → *γ*\]: (*δ* → (*α* → *β* → *γ*) → (*α* → *β*) → *α* → *γ*) → (*δ* → (*α* → *β* → *γ*)) → δ → (*α* → *β*) → *α* → *γ*

and then detach the consequent:

**S (K S)**: (*δ* → *α* → *β* → *γ*) → δ → (*α* → *β*) → *α* → *γ*

This is the formula for the type of (**S** (**K** **S**)). A special case of this theorem has *δ* = (*β* → *γ*):

**S (K S)** \[*δ* = *β* → *γ*\]: ((*β* → *γ*) → *α* → *β* → *γ*) → (*β* → *γ*) → (*α* → *β*) → *α* → *γ*

This last formula must be applied to **K**. Specialize **K** again, this time by replacing α with (*β* → *γ*) and β with α:

**K**: *α* → *β* → *α*

**K** \[*α* = *β* → *γ*, *β* = *α*\]: (*β* → *γ*) → *α* → (*β* → *γ*)

This is the same as the antecedent of the prior formula so, detaching the consequent:

**S (K S) K**: (*β* → *γ*) → (*α* → *β*) → *α* → *γ*

Switching the names of the variables α and γ gives us

(*β* → *α*) → (*γ* → *β*) → *γ* → *α*

which was what remained to prove.

### The normal proof of (β → α) → (γ → β) → γ → α in natural deduction seen as a λ-term

The diagram below gives proof of (*β* → *α*) → (*γ* → *β*) → *γ* → *α* in natural deduction and shows how it can be interpreted as the λ-expression λ *a*.λ *b*.λ *g*.(*a* (*b* *g*)) of type (*β* → *α*) → (*γ* → *β*) → *γ* → *α*.

```
a:β → α, b:γ → β, g:γ ⊢ b : γ → β    a:β → α, b:γ → β, g:γ ⊢ g : γ
———————————————————————————————————  ————————————————————————————————————————————————————————————————————
a:β → α, b:γ → β, g:γ ⊢ a : β → α      a:β → α, b:γ → β, g:γ ⊢ b g : β
————————————————————————————————————————————————————————————————————————
               a:β → α, b:γ → β, g:γ ⊢ a (b g) : α
               ————————————————————————————————————
               a:β → α, b:γ → β ⊢ λ g. a (b g) : γ → α
               ————————————————————————————————————————
                        a:β → α ⊢ λ b. λ g. a (b g) : (γ → β) → γ → α
                        ————————————————————————————————————
                                ⊢ λ a. λ b. λ g. a (b g) : (β → α) → (γ → β) → γ → α
```

## Other applications

Recently, the isomorphism has been proposed as a way to define search space partition in [genetic programming](https://en.wikipedia.org/wiki/Genetic_programming "Genetic programming").[^18] The method indexes sets of genotypes (the program trees evolved by the GP system) by their Curry–Howard isomorphic proof (referred to as a species).

As noted by [INRIA](https://en.wikipedia.org/wiki/INRIA "INRIA") research director Bernard Lang,[^19] the Curry-Howard correspondence constitutes an argument against the patentability of software: since algorithms are mathematical proofs, patentability of the former would imply patentability of the latter. A theorem could be private property; a mathematician would have to pay for using it, and to trust the company that sells it but keeps its proof secret and rejects responsibility for any errors.

## Generalizations

The correspondences listed here go much farther and deeper. For example, cartesian closed categories are generalized by [closed monoidal categories](https://en.wikipedia.org/wiki/Closed_monoidal_category "Closed monoidal category"). The [internal language](https://en.wikipedia.org/wiki/Internal_language "Internal language") of these categories is the [linear type system](https://en.wikipedia.org/wiki/Linear_type_system "Linear type system") (corresponding to [linear logic](https://en.wikipedia.org/wiki/Linear_logic "Linear logic")), which generalizes simply-typed lambda calculus as the internal language of cartesian closed categories. Moreover, these can be shown to correspond to [cobordisms](https://en.wikipedia.org/wiki/Cobordism "Cobordism"),[^20] which play a vital role in [string theory](https://en.wikipedia.org/wiki/String_theory "String theory").

An extended set of equivalences is also explored in [homotopy type theory](https://en.wikipedia.org/wiki/Homotopy_type_theory "Homotopy type theory"). Here, [type theory](https://en.wikipedia.org/wiki/Type_theory "Type theory") is extended by the [univalence axiom](https://en.wikipedia.org/wiki/Univalence_axiom "Univalence axiom") ("equivalence is equivalent to equality") which permits homotopy type theory to be used as a foundation for all of mathematics (including [set theory](https://en.wikipedia.org/wiki/Set_theory "Set theory") and classical logic, providing new ways to discuss the [axiom of choice](https://en.wikipedia.org/wiki/Axiom_of_choice "Axiom of choice") and many other things). That is, the Curry–Howard correspondence that proofs are elements of inhabited types is generalized to the notion of [homotopic equivalence](https://en.wikipedia.org/wiki/Homotopy "Homotopy") of proofs (as paths in space, the [identity type](https://en.wikipedia.org/wiki/Identity_type "Identity type") or [equality type](https://en.wikipedia.org/wiki/Intuitionistic_type_theory#Connectives_of_type_theory "Intuitionistic type theory") of type theory being interpreted as a path).[^21]

## References

### Seminal references

- Curry, H B (1934-09-20). ["Functionality in Combinatory Logic"](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC1076489). *Proceedings of the National Academy of Sciences of the United States of America*. **20** (11): 584–90. [Bibcode](https://en.wikipedia.org/wiki/Bibcode_\(identifier\) "Bibcode (identifier)"):[1934PNAS...20..584C](https://ui.adsabs.harvard.edu/abs/1934PNAS...20..584C). [doi](https://en.wikipedia.org/wiki/Doi_\(identifier\) "Doi (identifier)"):[10.1073/pnas.20.11.584](https://doi.org/10.1073%2Fpnas.20.11.584). [ISSN](https://en.wikipedia.org/wiki/ISSN_\(identifier\) "ISSN (identifier)") [0027-8424](https://search.worldcat.org/issn/0027-8424). [PMC](https://en.wikipedia.org/wiki/PMC_\(identifier\) "PMC (identifier)") [1076489](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC1076489). [PMID](https://en.wikipedia.org/wiki/PMID_\(identifier\) "PMID (identifier)") [16577644](https://pubmed.ncbi.nlm.nih.gov/16577644).
- Curry, Haskell B; Feys, Robert (1958). Craig, William (ed.). *Combinatory Logic*. Studies in Logic and the Foundations of Mathematics. Vol. 1. North-Holland Publishing Company. [LCCN](https://en.wikipedia.org/wiki/LCCN_\(identifier\) "LCCN (identifier)") [a59001593](https://lccn.loc.gov/a59001593); with two sections by Craig, William; see paragraph 9E `{{[cite book](https://en.wikipedia.org/wiki/Template:Cite_book "Template:Cite book")}}`: CS1 maint: postscript ([link](https://en.wikipedia.org/wiki/Category:CS1_maint:_postscript "Category:CS1 maint: postscript"))
- De Bruijn, Nicolaas (1968), *Automath, a language for mathematics*, Department of Mathematics, [Eindhoven University of Technology](https://en.wikipedia.org/wiki/Eindhoven_University_of_Technology "Eindhoven University of Technology"), TH-report 68-WSK-05. Reprinted in revised form, with two pages commentary, in: *Automation and Reasoning, vol 2, Classical papers on computational logic 1967–1970*, Springer Verlag, 1983, pp. 159–200.
- Howard, William A. (September 1980) \[original paper manuscript from 1969\], ["The formulae-as-types notion of construction"](https://www.cs.cmu.edu/~crary/819-f09/Howard80.pdf) (PDF), in [Seldin, Jonathan P.](https://en.wikipedia.org/w/index.php?title=Jonathan_P._Seldin&action=edit&redlink=1 "Jonathan P. Seldin (page does not exist)"); [Hindley, J. Roger](https://en.wikipedia.org/wiki/J._Roger_Hindley "J. Roger Hindley") (eds.), *To H.B. Curry: Essays on Combinatory Logic, Lambda Calculus and Formalism*, [Academic Press](https://en.wikipedia.org/wiki/Academic_Press "Academic Press"), pp. 479–490, [ISBN](https://en.wikipedia.org/wiki/ISBN_\(identifier\) "ISBN (identifier)") [978-0-12-349050-6](https://en.wikipedia.org/wiki/Special:BookSources/978-0-12-349050-6 "Special:BookSources/978-0-12-349050-6")
- Martin-Löf, Per (1975), "About models of intuitionistic type theories and the notion of definitional equality", in Kanger, Stig (ed.), *Proceedings of the Third Scandinavian Logic Symposium*, Elsevier, pp. 81–109
- Prawitz, Dag (1970), "Constructive semantics", *Proceedings of the First Scandinavian Logic Symposium*, pp. 96–114

### Extensions of the correspondence

- Moggi, Eugenio (1991), ["Notions of Computation and Monads"](http://www.disi.unige.it/person/MoggiE/ftp/ic91.pdf) (PDF), *Information and Computation*, **93** (1): 55–92, [doi](https://en.wikipedia.org/wiki/Doi_\(identifier\) "Doi (identifier)"):[10.1016/0890-5401(91)90052-4](https://doi.org/10.1016%2F0890-5401%2891%2990052-4)
- Davies, Rowan; Pfenning, Frank (2001), ["A Modal Analysis of Staged Computation"](https://www.cs.cmu.edu/~fp/papers/jacm00.pdf) (PDF), *Journal of the ACM*, **48** (3): 555–604, [CiteSeerX](https://en.wikipedia.org/wiki/CiteSeerX_\(identifier\) "CiteSeerX (identifier)") [10.1.1.3.5442](https://citeseerx.ist.psu.edu/viewdoc/summary?doi=10.1.1.3.5442), [doi](https://en.wikipedia.org/wiki/Doi_\(identifier\) "Doi (identifier)"):[10.1145/382780.382785](https://doi.org/10.1145%2F382780.382785), [S2CID](https://en.wikipedia.org/wiki/S2CID_\(identifier\) "S2CID (identifier)") [52148006](https://api.semanticscholar.org/CorpusID:52148006)
- Pfenning, Frank; Davies, Rowan (2001), ["A Judgmental Reconstruction of Modal Logic"](https://www.cs.cmu.edu/~fp/papers/mscs00.pdf) (PDF), *Mathematical Structures in Computer Science*, **11** (4): 511–540, [CiteSeerX](https://en.wikipedia.org/wiki/CiteSeerX_\(identifier\) "CiteSeerX (identifier)") [10.1.1.43.1611](https://citeseerx.ist.psu.edu/viewdoc/summary?doi=10.1.1.43.1611), [doi](https://en.wikipedia.org/wiki/Doi_\(identifier\) "Doi (identifier)"):[10.1017/S0960129501003322](https://doi.org/10.1017%2FS0960129501003322), [S2CID](https://en.wikipedia.org/wiki/S2CID_\(identifier\) "S2CID (identifier)") [16467268](https://api.semanticscholar.org/CorpusID:16467268)
- Benton; Bierman; de Paiva (1998), "Computational types from a logical perspective", *Journal of Functional Programming*, **8** (2): 177–193, [CiteSeerX](https://en.wikipedia.org/wiki/CiteSeerX_\(identifier\) "CiteSeerX (identifier)") [10.1.1.258.6004](https://citeseerx.ist.psu.edu/viewdoc/summary?doi=10.1.1.258.6004), [doi](https://en.wikipedia.org/wiki/Doi_\(identifier\) "Doi (identifier)"):[10.1017/s0956796898002998](https://doi.org/10.1017%2Fs0956796898002998), [S2CID](https://en.wikipedia.org/wiki/S2CID_\(identifier\) "S2CID (identifier)") [6149614](https://api.semanticscholar.org/CorpusID:6149614)
- Griffin, Timothy G. (1990), "The Formulae-as-Types Notion of Control", *Conf. Record 17th Annual ACM Symp. on Principles of Programming Languages, POPL '90, San Francisco, CA, USA, 17–19 Jan 1990*, pp. 47–57, [doi](https://en.wikipedia.org/wiki/Doi_\(identifier\) "Doi (identifier)"):[10.1145/96709.96714](https://doi.org/10.1145%2F96709.96714), [ISBN](https://en.wikipedia.org/wiki/ISBN_\(identifier\) "ISBN (identifier)") [978-0-89791-343-0](https://en.wikipedia.org/wiki/Special:BookSources/978-0-89791-343-0 "Special:BookSources/978-0-89791-343-0"), [S2CID](https://en.wikipedia.org/wiki/S2CID_\(identifier\) "S2CID (identifier)") [3005134](https://api.semanticscholar.org/CorpusID:3005134)
- Parigot, Michel (1992), "Lambda-mu-calculus: An algorithmic interpretation of classical natural deduction", [*International Conference on Logic Programming and Automated Reasoning: LPAR '92 Proceedings, St. Petersburg, Russia*](https://en.wikipedia.org/wiki/International_Conference_on_Logic_Programming_and_Automated_Reasoning "International Conference on Logic Programming and Automated Reasoning"), Lecture Notes in Computer Science, vol. 624, [Springer-Verlag](https://en.wikipedia.org/wiki/Springer-Verlag "Springer-Verlag"), pp. 190–201, [ISBN](https://en.wikipedia.org/wiki/ISBN_\(identifier\) "ISBN (identifier)") [978-3-540-55727-2](https://en.wikipedia.org/wiki/Special:BookSources/978-3-540-55727-2 "Special:BookSources/978-3-540-55727-2")
- Herbelin, Hugo (1995), "A Lambda-Calculus Structure Isomorphic to Gentzen-Style Sequent Calculus Structure", in Pacholski, Leszek; Tiuryn, Jerzy (eds.), *Computer Science Logic, 8th International Workshop, CSL '94, Kazimierz, Poland, September 25–30, 1994, Selected Papers*, Lecture Notes in Computer Science, vol. 933, [Springer-Verlag](https://en.wikipedia.org/wiki/Springer-Verlag "Springer-Verlag"), pp. 61–75, [ISBN](https://en.wikipedia.org/wiki/ISBN_\(identifier\) "ISBN (identifier)") [978-3-540-60017-6](https://en.wikipedia.org/wiki/Special:BookSources/978-3-540-60017-6 "Special:BookSources/978-3-540-60017-6")
- Gabbay, Dov; [de Queiroz, Ruy](https://en.wikipedia.org/wiki/Ruy_de_Queiroz "Ruy de Queiroz") (1992). "Extending the Curry–Howard interpretation to linear, relevant and other resource logics". *Journal of Symbolic Logic*. Vol. 57. Association for Symbolic Logic. pp. 1319–1365. [doi](https://en.wikipedia.org/wiki/Doi_\(identifier\) "Doi (identifier)"):[10.2307/2275370](https://doi.org/10.2307%2F2275370). [JSTOR](https://en.wikipedia.org/wiki/JSTOR_\(identifier\) "JSTOR (identifier)") [2275370](https://www.jstor.org/stable/2275370). [S2CID](https://en.wikipedia.org/wiki/S2CID_\(identifier\) "S2CID (identifier)") [7159005](https://api.semanticscholar.org/CorpusID:7159005). (Full version of the paper presented at *Logic Colloquium '90*, Helsinki. Abstract in *JSL* 56(3):1139–1140, 1991.)
- de Queiroz, Ruy; Gabbay, Dov (1994), "Equality in Labelled Deductive Systems and the Functional Interpretation of Propositional Equality", in Dekker, Paul; Stokhof, Martin (eds.), *Proceedings of the Ninth Amsterdam Colloquium*, ILLC/Department of Philosophy, University of Amsterdam, pp. 547–565, [ISBN](https://en.wikipedia.org/wiki/ISBN_\(identifier\) "ISBN (identifier)") [978-90-74795-07-4](https://en.wikipedia.org/wiki/Special:BookSources/978-90-74795-07-4 "Special:BookSources/978-90-74795-07-4")
- de Queiroz, Ruy; Gabbay, Dov (1995), ["The Functional Interpretation of the Existential Quantifier"](https://academic.oup.com/jigpal/article-abstract/3/2-3/243/2897783), *Bulletin of the Interest Group in Pure and Applied Logics*, vol. 3, pp. 243–290 (Full version of a paper presented at *Logic Colloquium '91*, Uppsala. Abstract in *JSL* 58(2):753–754, 1993.)
- de Queiroz, Ruy; Gabbay, Dov (1997), "The Functional Interpretation of Modal Necessity", in de Rijke, Maarten (ed.), *Advances in Intensional Logic*, Applied Logic Series, vol. 7, [Springer-Verlag](https://en.wikipedia.org/wiki/Springer-Verlag "Springer-Verlag"), pp. 61–91, [ISBN](https://en.wikipedia.org/wiki/ISBN_\(identifier\) "ISBN (identifier)") [978-0-7923-4711-8](https://en.wikipedia.org/wiki/Special:BookSources/978-0-7923-4711-8 "Special:BookSources/978-0-7923-4711-8")
- de Queiroz, Ruy; Gabbay, Dov (1999), ["Labelled Natural Deduction"](https://www.springer.com/philosophy/logic/book/978-0-7923-5687-5), in Ohlbach, Hans-Juergen; Reyle, Uwe (eds.), *Logic, Language and Reasoning. Essays in Honor of Dov Gabbay*, Trends in Logic, vol. 7, Kluwer, pp. 173–250, [ISBN](https://en.wikipedia.org/wiki/ISBN_\(identifier\) "ISBN (identifier)") [978-0-7923-5687-5](https://en.wikipedia.org/wiki/Special:BookSources/978-0-7923-5687-5 "Special:BookSources/978-0-7923-5687-5")
- de Oliveira, Anjolina; de Queiroz, Ruy (1999), "A Normalization Procedure for the Equational Fragment of Labelled Natural Deduction", *Logic Journal of the Interest Group in Pure and Applied Logics*, vol. 7, [Oxford University Press](https://en.wikipedia.org/wiki/Oxford_University_Press "Oxford University Press"), pp. 173–215 (Full version of a paper presented at *2nd WoLLIC'95*, Recife. Abstract in *Journal of the Interest Group in Pure and Applied Logics* 4(2):330–332, 1996.)
- Poernomo, Iman; Crossley, John; Wirsing; Martin (2005), *Adapting Proofs-as-Programs: The Curry–Howard Protocol*, Monographs in Computer Science, [Springer](https://en.wikipedia.org/wiki/Springer_Science%2BBusiness_Media "Springer Science+Business Media"), [ISBN](https://en.wikipedia.org/wiki/ISBN_\(identifier\) "ISBN (identifier)") [978-0-387-23759-6](https://en.wikipedia.org/wiki/Special:BookSources/978-0-387-23759-6 "Special:BookSources/978-0-387-23759-6"), concerns the adaptation of proofs-as-programs program synthesis to coarse-grain and imperative program development problems, via a method the authors call the Curry–Howard protocol. Includes a discussion of the Curry–Howard correspondence from a Computer Science perspective.
- de Queiroz, Ruy J.G.B.; de Oliveira, Anjolina (2011), "The Functional Interpretation of Direct Computations", *Electronic Notes in Theoretical Computer Science*, **269**, [Elsevier](https://en.wikipedia.org/wiki/Elsevier "Elsevier"): 19–40, [doi](https://en.wikipedia.org/wiki/Doi_\(identifier\) "Doi (identifier)"):[10.1016/j.entcs.2011.03.003](https://doi.org/10.1016%2Fj.entcs.2011.03.003) (Full version of a paper presented at *LSFA 2010*, Natal, Brazil.)

### Philosophical interpretations

- de Queiroz, Ruy J.G.B. (1994), "Normalisation and language-games", *Dialectica*, **48** (2): 83–123, [doi](https://en.wikipedia.org/wiki/Doi_\(identifier\) "Doi (identifier)"):[10.1111/j.1746-8361.1994.tb00107.x](https://doi.org/10.1111%2Fj.1746-8361.1994.tb00107.x), [JSTOR](https://en.wikipedia.org/wiki/JSTOR_\(identifier\) "JSTOR (identifier)") [42968904](https://www.jstor.org/stable/42968904) (Early version presented at *Logic Colloquium '88*, Padova. Abstract in *JSL* 55:425, 1990.)
- de Queiroz, Ruy J.G.B. (2001), ["Meaning, function, purpose, usefulness, consequences – interconnected concepts"](http://jigpal.oxfordjournals.org/cgi/content/abstract/9/5/693), *Logic Journal of the Interest Group in Pure and Applied Logics*, vol. 9, pp. 693–734 (Early version presented at *Fourteenth International Wittgenstein Symposium (Centenary Celebration)* held in Kirchberg/Wechsel, August 13–20, 1989.)
- de Queiroz, Ruy J.G.B. (2008), "On Reduction Rules, Meaning-as-use, and Proof-theoretic Semantics", *Studia Logica*, **90** (2): 211–247, [doi](https://en.wikipedia.org/wiki/Doi_\(identifier\) "Doi (identifier)"):[10.1007/s11225-008-9150-5](https://doi.org/10.1007%2Fs11225-008-9150-5), [S2CID](https://en.wikipedia.org/wiki/S2CID_\(identifier\) "S2CID (identifier)") [11321602](https://api.semanticscholar.org/CorpusID:11321602)
- Wadler, Philip (2015), *Propositions as types*, Communications of the ACM, 58(12), pp. 75–84.

### Synthetic papers

- De Bruijn, Nicolaas Govert (1995), ["On the roles of types in mathematics"](http://alexandria.tue.nl/repository/freearticles/597627.pdf) (PDF), in Groote, Philippe de (ed.), *[De Groote 1995](https://en.wikipedia.org/wiki/Curry%E2%80%93Howard_correspondence#CITEREFDe_Groote1995), pp. 27–54*, the contribution of de Bruijn by himself.
- Geuvers, Herman (1995), "The Calculus of Constructions and Higher Order Logic", *[De Groote 1995](https://en.wikipedia.org/wiki/Curry%E2%80%93Howard_correspondence#CITEREFDe_Groote1995), pp. 139–191*, contains a synthetic introduction to the Curry–Howard correspondence.
- [Gallier, Jean H.](https://en.wikipedia.org/wiki/Jean_Gallier "Jean Gallier") (1995), ["On the Correspondence between Proofs and Lambda-Terms"](https://web.archive.org/web/20170705163849/ftp://ftp.cis.upenn.edu/pub/papers/gallier/cahiers.pdf) (PDF), *[De Groote 1995](https://en.wikipedia.org/wiki/Curry%E2%80%93Howard_correspondence#CITEREFDe_Groote1995), pp. 55–138*, archived from [the original](ftp://ftp.cis.upenn.edu/pub/papers/gallier/cahiers.pdf) (PDF) on 2017-07-05, contains a synthetic introduction to the Curry–Howard correspondence.
- Goldblatt, Robert (2006). ["Grothendieck Topology as Intuitionistic Modality"](https://homepages.ecs.vuw.ac.nz/~rob/papers/modalhist.pdf) (PDF). In Gabbay, Dov M.; Woods, John (eds.). *Handbook of the History of Logic, vol. 7:* Logic and the Modalities in the Twentieth Century. Amsterdam: Elsevier. pp. 76–81. [ISBN](https://en.wikipedia.org/wiki/ISBN_\(identifier\) "ISBN (identifier)") [978-0-444-51622-0](https://en.wikipedia.org/wiki/Special:BookSources/978-0-444-51622-0 "Special:BookSources/978-0-444-51622-0").
- [Wadler, Philip](https://en.wikipedia.org/wiki/Philip_Wadler "Philip Wadler") (2014), ["Propositions as Types"](http://homepages.inf.ed.ac.uk/wadler/papers/propositions-as-types/propositions-as-types.pdf) (PDF), *Communications of the ACM*, **58** (12): 75–84, [doi](https://en.wikipedia.org/wiki/Doi_\(identifier\) "Doi (identifier)"):[10.1145/2699407](https://doi.org/10.1145%2F2699407), [S2CID](https://en.wikipedia.org/wiki/S2CID_\(identifier\) "S2CID (identifier)") [11957500](https://api.semanticscholar.org/CorpusID:11957500)

### Books

- Coecke, Bob; Kissinger, Aleks (2017). [*Picturing Quantum Processes*](https://books.google.com/books?id=I9gcDgAAQBAJ&pg=PA82). Cambridge University Press. [ISBN](https://en.wikipedia.org/wiki/ISBN_\(identifier\) "ISBN (identifier)") [978-1-107-10422-8](https://en.wikipedia.org/wiki/Special:BookSources/978-1-107-10422-8 "Special:BookSources/978-1-107-10422-8").
- Kennedy, Juliette; Kossak, Roman, eds. (2011). *Set Theory, Arithmetic, and Foundations of Mathematics: Theorems, Philosophies*. Cambridge University Press. [ISBN](https://en.wikipedia.org/wiki/ISBN_\(identifier\) "ISBN (identifier)") [978-1-107-00804-5](https://en.wikipedia.org/wiki/Special:BookSources/978-1-107-00804-5 "Special:BookSources/978-1-107-00804-5").
- Baez, John C.; Stay, Mike (2011). ["Physics, Topology, Logic and Computation: A Rosetta Stone"](http://math.ucr.edu/home/baez/rosetta/rose3.pdf) (PDF). In Coecke, Bob (ed.). *New Structures for Physics*. Lecture Notes in Physics. Vol. 813. Berlin: Springer. pp. 95–174. [arXiv](https://en.wikipedia.org/wiki/ArXiv_\(identifier\) "ArXiv (identifier)"):[0903.0340](https://arxiv.org/abs/0903.0340).
- Casadio, Claudia; Scott, Philip J. (2021). [*Joachim Lambek: The Interplay of Mathematics, Logic, and Linguistics*](https://books.google.com/books?id=rP8kEAAAQBAJ&pg=PA184). Springer. [ISBN](https://en.wikipedia.org/wiki/ISBN_\(identifier\) "ISBN (identifier)") [978-3-030-66545-6](https://en.wikipedia.org/wiki/Special:BookSources/978-3-030-66545-6 "Special:BookSources/978-3-030-66545-6").
- Lambek, Joachim; Scott, P. J. (1989). *Introduction to higher order categorical logic*. Cambridge New York Port Chester \[etc.\]: Cambridge university press. [ISBN](https://en.wikipedia.org/wiki/ISBN_\(identifier\) "ISBN (identifier)") [0521356539](https://en.wikipedia.org/wiki/Special:BookSources/0521356539 "Special:BookSources/0521356539").
- De Groote, Philippe, ed. (1995), *The Curry–Howard Isomorphism*, Cahiers du Centre de Logique (Université catholique de Louvain), vol. 8, Academia-Bruylant, [ISBN](https://en.wikipedia.org/wiki/ISBN_\(identifier\) "ISBN (identifier)") [978-2-87209-363-2](https://en.wikipedia.org/wiki/Special:BookSources/978-2-87209-363-2 "Special:BookSources/978-2-87209-363-2"), reproduces the seminal papers of Curry-Feys and Howard, a paper by de Bruijn and a few other papers.
- Sørensen, Morten Heine; Urzyczyn, Paweł (2006) \[1998\], *Lectures on the Curry–Howard isomorphism*, Studies in Logic and the Foundations of Mathematics, vol. 149, [Elsevier Science](https://en.wikipedia.org/wiki/Elsevier_Science "Elsevier Science"), [CiteSeerX](https://en.wikipedia.org/wiki/CiteSeerX_\(identifier\) "CiteSeerX (identifier)") [10.1.1.17.7385](https://citeseerx.ist.psu.edu/viewdoc/summary?doi=10.1.1.17.7385), [ISBN](https://en.wikipedia.org/wiki/ISBN_\(identifier\) "ISBN (identifier)") [978-0-444-52077-7](https://en.wikipedia.org/wiki/Special:BookSources/978-0-444-52077-7 "Special:BookSources/978-0-444-52077-7"), notes on proof theory and type theory, that includes a presentation of the Curry–Howard correspondence, with a focus on the formulae-as-types correspondence
- Girard, Jean-Yves (1987–1990), [*Proof and Types*](https://web.archive.org/web/20080418044121/http://www.monad.me.uk/stable/Proofs+Types.html), Cambridge Tracts in Theoretical Computer Science, vol. 7, Translated by and with appendices by Lafont, Yves and Taylor, Paul, Cambridge University Press, [ISBN](https://en.wikipedia.org/wiki/ISBN_\(identifier\) "ISBN (identifier)") [0-521-37181-3](https://en.wikipedia.org/wiki/Special:BookSources/0-521-37181-3 "Special:BookSources/0-521-37181-3"), archived from [the original](http://www.monad.me.uk/stable/Proofs+Types.html) on 2008-04-18, notes on proof theory with a presentation of the Curry–Howard correspondence.
- Thompson, Simon (1991), [*Type Theory and Functional Programming*](http://www.cs.kent.ac.uk/people/staff/sjt/TTFP/), Addison–Wesley, [ISBN](https://en.wikipedia.org/wiki/ISBN_\(identifier\) "ISBN (identifier)") [0-201-41667-0](https://en.wikipedia.org/wiki/Special:BookSources/0-201-41667-0 "Special:BookSources/0-201-41667-0")
- Poernomo, Iman; Crossley, John; Wirsing; Martin (2005), *Adapting Proofs-as-Programs: The Curry–Howard Protocol*, Monographs in Computer Science, [Springer](https://en.wikipedia.org/wiki/Springer_Science%2BBusiness_Media "Springer Science+Business Media"), [ISBN](https://en.wikipedia.org/wiki/ISBN_\(identifier\) "ISBN (identifier)") [978-0-387-23759-6](https://en.wikipedia.org/wiki/Special:BookSources/978-0-387-23759-6 "Special:BookSources/978-0-387-23759-6"), concerns the adaptation of proofs-as-programs program synthesis to coarse-grain and imperative program development problems, via a method the authors call the Curry–Howard protocol. Includes a discussion of the Curry–Howard correspondence from a Computer Science perspective.
- Binard, F.; Felty, A. (2008), ["Genetic programming with polymorphic types and higher-order functions"](http://www.site.uottawa.ca/~afelty/dist/gecco08.pdf) (PDF), *Proceedings of the 10th annual conference on Genetic and evolutionary computation*, Association for Computing Machinery, pp. 1187–94, [doi](https://en.wikipedia.org/wiki/Doi_\(identifier\) "Doi (identifier)"):[10.1145/1389095.1389330](https://doi.org/10.1145%2F1389095.1389330), [ISBN](https://en.wikipedia.org/wiki/ISBN_\(identifier\) "ISBN (identifier)") [9781605581309](https://en.wikipedia.org/wiki/Special:BookSources/9781605581309 "Special:BookSources/9781605581309"), [S2CID](https://en.wikipedia.org/wiki/S2CID_\(identifier\) "S2CID (identifier)") [3669630](https://api.semanticscholar.org/CorpusID:3669630)
- de Queiroz, Ruy J.G.B.; de Oliveira, Anjolina G.; Gabbay, Dov M. (2011), [*The Functional Interpretation of Logical Deduction*](https://books.google.com/books?id=aFO6CgAAQBAJ), Advances in Logic, vol. 5, Imperial College Press/World Scientific, [ISBN](https://en.wikipedia.org/wiki/ISBN_\(identifier\) "ISBN (identifier)") [978-981-4360-95-1](https://en.wikipedia.org/wiki/Special:BookSources/978-981-4360-95-1 "Special:BookSources/978-981-4360-95-1")

## Further reading

- [Johnstone, P.T.](https://en.wikipedia.org/wiki/P.T._Johnstone "P.T. Johnstone") (2002), "D4.2 λ-Calculus and cartesian closed categories", [*Sketches of an Elephant*](https://books.google.com/books?id=TLHfQPHNs0QC), A Topos Theory Compendium, vol. 2, Clarendon Press, pp. 951–962, [ISBN](https://en.wikipedia.org/wiki/ISBN_\(identifier\) "ISBN (identifier)") [978-0-19-851598-2](https://en.wikipedia.org/wiki/Special:BookSources/978-0-19-851598-2 "Special:BookSources/978-0-19-851598-2") – gives a [categorical](https://en.wikipedia.org/wiki/Categorical_logic "Categorical logic") view of "what happens" in the Curry–Howard correspondence.

## External links

- [Howard on Curry-Howard](http://wadler.blogspot.com/2014/08/howard-on-curry-howard.html)
- [The Curry–Howard Correspondence in Haskell](https://web.archive.org/web/20080819185521/http://www.thenewsh.com/~newsham/formal/curryhoward/)
- [The Monad Reader 6: Adventures in Classical-Land](http://www.haskell.org/wikiupload/1/14/TMR-Issue6.pdf): Curry–Howard in Haskell, Pierce's law.

[^1]: The correspondence was first made explicit in [Howard 1980](https://en.wikipedia.org/wiki/Curry%E2%80%93Howard_correspondence#CITEREFHoward1980). See, for example section 4.6, p.53 [Gert Smolka and Jan Schwinghammer (2007-8), Lecture Notes in Semantics](http://www.ps.uni-saarland.de/courses/sem-ws07/notes/0.pdf)

[^2]: The Brouwer–Heyting–Kolmogorov interpretation is also called the 'proof interpretation': [Kennedy & Kossak 2011](https://en.wikipedia.org/wiki/Curry%E2%80%93Howard_correspondence#CITEREFKennedyKossak2011), p. 161

[^3]: [Casadio & Scott 2021](https://en.wikipedia.org/wiki/Curry%E2%80%93Howard_correspondence#CITEREFCasadioScott2021), p. 184.

[^4]: [Coecke & Kissinger 2017](https://en.wikipedia.org/wiki/Curry%E2%80%93Howard_correspondence#CITEREFCoeckeKissinger2017), p. 82.

[^5]: ["Computational trilogy"](https://ncatlab.org/nlab/show/computational+trilogy). *nLab*. Retrieved October 29, 2023.

[^6]: [Curry 1934](https://en.wikipedia.org/wiki/Curry%E2%80%93Howard_correspondence#CITEREFCurry1934).

[^7]: [Curry & Feys 1958](https://en.wikipedia.org/wiki/Curry%E2%80%93Howard_correspondence#CITEREFCurryFeys1958).

[^8]: [Howard 1980](https://en.wikipedia.org/wiki/Curry%E2%80%93Howard_correspondence#CITEREFHoward1980).

[^9]: [Martin-Löf 1975](https://en.wikipedia.org/wiki/Curry%E2%80%93Howard_correspondence#CITEREFMartin-L%C3%B6f1975).

[^10]: [Moggi 1991](https://en.wikipedia.org/wiki/Curry%E2%80%93Howard_correspondence#CITEREFMoggi1991).

[^11]: [Pfenning & Davies 2001](https://en.wikipedia.org/wiki/Curry%E2%80%93Howard_correspondence#CITEREFPfenningDavies2001).

[^12]: [Davies & Pfenning 2001](https://en.wikipedia.org/wiki/Curry%E2%80%93Howard_correspondence#CITEREFDaviesPfenning2001).

[^13]: [Sørensen & Urzyczyn 2006](https://en.wikipedia.org/wiki/Curry%E2%80%93Howard_correspondence#CITEREFS%C3%B8rensenUrzyczyn2006).

[^14]: [Goldblatt 2006](https://en.wikipedia.org/wiki/Curry%E2%80%93Howard_correspondence#CITEREFGoldblatt2006). The "lax" modality referred to is from [Benton, Bierman & de Paiva 1998](https://en.wikipedia.org/wiki/Curry%E2%80%93Howard_correspondence#CITEREFBentonBiermande_Paiva1998)

[^15]: [Prawitz 1970](https://en.wikipedia.org/wiki/Curry%E2%80%93Howard_correspondence#CITEREFPrawitz1970).

[^16]: [Sørensen & Urzyczyn 2006](https://en.wikipedia.org/wiki/Curry%E2%80%93Howard_correspondence#CITEREFS%C3%B8rensenUrzyczyn2006), pp. 98–99.

[^17]: [Lambek & Scott 1989](https://en.wikipedia.org/wiki/Curry%E2%80%93Howard_correspondence#CITEREFLambekScott1989).

[^18]: [Binard & Felty 2008](https://en.wikipedia.org/wiki/Curry%E2%80%93Howard_correspondence#CITEREFBinardFelty2008).

[^19]: ["Article"](https://web.archive.org/web/20131117184907/http://bat8.inria.fr/~lang/ecrits/larecherche/03280721.html). *bat8.inria.fr*. Archived from [the original](http://bat8.inria.fr/~lang/ecrits/larecherche/03280721.html) on 2013-11-17. Retrieved 2020-01-31.

[^20]: [Baez & Stay 2011](https://en.wikipedia.org/wiki/Curry%E2%80%93Howard_correspondence#CITEREFBaezStay2011).

[^21]: [*Homotopy Type Theory: Univalent Foundations of Mathematics*](http://homotopytypetheory.org/book/). (2013) The Univalent Foundations Program. [Institute for Advanced Study](https://en.wikipedia.org/wiki/Institute_for_Advanced_Study "Institute for Advanced Study").