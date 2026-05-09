**Reverse mathematics** is a program in [mathematical logic](https://en.wikipedia.org/wiki/Mathematical_logic "Mathematical logic") that seeks to determine which axioms are required to prove theorems of mathematics. Its defining method can briefly be described as "going backwards from the [theorems](https://en.wikipedia.org/wiki/Theorem "Theorem") to the [axioms](https://en.wikipedia.org/wiki/Axiom "Axiom") ", in contrast to the ordinary mathematical practice of deriving theorems from axioms. It can be conceptualized as sculpting out [necessary](https://en.wikipedia.org/wiki/Necessity_and_sufficiency "Necessity and sufficiency") conditions from [sufficient](https://en.wikipedia.org/wiki/Necessity_and_sufficiency "Necessity and sufficiency") ones.

The reverse mathematics program was foreshadowed by results in [set theory](https://en.wikipedia.org/wiki/Set_theory "Set theory") such as the classical theorem that the [axiom of choice](https://en.wikipedia.org/wiki/Axiom_of_choice "Axiom of choice") and [Zorn's lemma](https://en.wikipedia.org/wiki/Zorn%27s_lemma "Zorn's lemma") are equivalent over [ZF set theory](https://en.wikipedia.org/wiki/ZF_set_theory "ZF set theory"). The goal of reverse mathematics, however, is to study possible axioms of ordinary theorems of mathematics rather than possible axioms for set theory. Reverse mathematics is usually carried out using subsystems of [second-order arithmetic](https://en.wikipedia.org/wiki/Second-order_arithmetic "Second-order arithmetic"),[^1] where many of its definitions and methods are inspired by previous work in [constructive analysis](https://en.wikipedia.org/wiki/Constructive_analysis "Constructive analysis") and [proof theory](https://en.wikipedia.org/wiki/Proof_theory "Proof theory"). The use of second-order arithmetic also allows many techniques from [recursion theory](https://en.wikipedia.org/wiki/Recursion_theory "Recursion theory") to be employed; many results in reverse mathematics have corresponding results in [computable analysis](https://en.wikipedia.org/wiki/Computable_analysis "Computable analysis"). In *higher-order* reverse mathematics, the focus is on subsystems of [higher-order arithmetic](https://en.wikipedia.org/wiki/Higher-order_arithmetic "Higher-order arithmetic"), and the associated richer language.

The program was founded by [Harvey Friedman](https://en.wikipedia.org/wiki/Harvey_Friedman_\(mathematician\) "Harvey Friedman (mathematician)") [^2] [^3] and brought forward by [Steve Simpson](https://en.wikipedia.org/wiki/Steve_Simpson_\(mathematician\) "Steve Simpson (mathematician)").[^1]

**Constructive reverse mathematics** is related program which is applied to [constructive mathematics](https://en.wikipedia.org/wiki/Constructive_mathematics "Constructive mathematics").

## General principles

In reverse mathematics, one starts with a framework language and a base [theory](https://en.wikipedia.org/wiki/Theory_\(logic\) "Theory (logic)") —a core axiom system—that is too weak to prove most of the theorems one might be interested in, but still powerful enough to develop the definitions necessary to state these theorems. For example, to study the theorem "Every bounded [sequence](https://en.wikipedia.org/wiki/Sequence_\(mathematics\) "Sequence (mathematics)") of [real numbers](https://en.wikipedia.org/wiki/Real_number "Real number") has a [supremum](https://en.wikipedia.org/wiki/Supremum "Supremum") " it is necessary to use a base system that can speak of real numbers and sequences of real numbers.

For each theorem that can be stated in the base system but is not provable in the base system, the goal is to determine the particular axiom system (stronger than the base system) that is necessary to prove that theorem. To show that a system *S* is required to prove a theorem *T*, two proofs are required. The first proof shows *T* is provable from *S*; this is an ordinary mathematical proof along with a justification that it can be carried out in the system *S*. The second proof, known as a **reversal**, shows that *T* itself implies *S*; this proof is carried out in the base system.[^1] The reversal establishes that no axiom system *S* ′ that extends the base system can be weaker than *S* while still proving *T*.

### Use of second-order arithmetic

Most reverse mathematics research focuses on subsystems of [second-order arithmetic](https://en.wikipedia.org/wiki/Second-order_arithmetic "Second-order arithmetic"). The body of research in reverse mathematics has established that weak subsystems of second-order arithmetic suffice to formalize almost all undergraduate-level mathematics. In second-order arithmetic, all objects can be represented as either [natural numbers](https://en.wikipedia.org/wiki/Natural_number "Natural number") or sets of natural numbers. For example, in order to prove theorems about real numbers, the real numbers can be represented as [Cauchy sequences](https://en.wikipedia.org/wiki/Cauchy_sequence "Cauchy sequence") of [rational numbers](https://en.wikipedia.org/wiki/Rational_number "Rational number"), each of which sequence can be represented as a set of natural numbers.

The axiom systems most often considered in reverse mathematics are defined using [axiom schemes](https://en.wikipedia.org/wiki/Axiom_scheme "Axiom scheme") called **comprehension schemes**. Such a scheme states that any set of natural numbers definable by a formula of a given complexity exists. In this context, the complexity of formulas is measured using the [arithmetical hierarchy](https://en.wikipedia.org/wiki/Arithmetical_hierarchy "Arithmetical hierarchy") and [analytical hierarchy](https://en.wikipedia.org/wiki/Analytical_hierarchy "Analytical hierarchy").

The reason that reverse mathematics is not carried out using set theory as a base system is that the language of set theory is too expressive. Extremely complex sets of natural numbers can be defined by simple formulas in the language of set theory (which can quantify over arbitrary sets). In the context of second-order arithmetic, results such as [Post's theorem](https://en.wikipedia.org/wiki/Post%27s_theorem "Post's theorem") establish a close link between the complexity of a formula and the (non)computability of the set it defines.

Another effect of using second-order arithmetic is the need to restrict general mathematical theorems to forms that can be expressed within arithmetic. For example, second-order arithmetic can express the principle "Every countable [vector space](https://en.wikipedia.org/wiki/Vector_space "Vector space") has a basis" but it cannot express the principle "Every vector space has a basis". In practical terms, this means that theorems of [algebra](https://en.wikipedia.org/wiki/Abstract_algebra "Abstract algebra") and [combinatorics](https://en.wikipedia.org/wiki/Combinatorics "Combinatorics") are restricted to countable structures, while theorems of [analysis](https://en.wikipedia.org/wiki/Analysis_\(mathematics\) "Analysis (mathematics)") and [topology](https://en.wikipedia.org/wiki/Topology "Topology") are restricted to [separable spaces](https://en.wikipedia.org/wiki/Separable_space "Separable space"). Many principles that imply the [axiom of choice](https://en.wikipedia.org/wiki/Axiom_of_choice "Axiom of choice") in their general form (such as "Every vector space has a basis") become provable in weak subsystems of second-order arithmetic when they are restricted. For example, "every field has an algebraic closure" is not provable in ZF set theory, but the restricted form "every countable field has an algebraic closure" is provable in RCA <sub>0</sub>, the weakest system typically employed in reverse mathematics.

### Use of higher-order arithmetic

A recent strand of *higher-order* reverse mathematics research, initiated by [Ulrich Kohlenbach](https://en.wikipedia.org/wiki/Ulrich_Kohlenbach "Ulrich Kohlenbach") in 2005, focuses on subsystems of [higher-order arithmetic](https://en.wikipedia.org/wiki/Higher-order_arithmetic "Higher-order arithmetic").[^4] Due to the richer language of higher-order arithmetic, the use of representations (also known as 'codes') common in second-order arithmetic, is greatly reduced. For example, a continuous function on the [Cantor space](https://en.wikipedia.org/wiki/Cantor_space "Cantor space") is just a function that maps binary sequences to binary sequences, and that also satisfies the usual 'epsilon–delta'-definition of continuity.

Higher-order reverse mathematics includes higher-order versions of (second-order) comprehension schemes. Such a higher-order axiom states the existence of a functional that decides the truth or falsity of formulas of a given complexity. In this context, the complexity of formulas is also measured using the [arithmetical hierarchy](https://en.wikipedia.org/wiki/Arithmetical_hierarchy "Arithmetical hierarchy") and [analytical hierarchy](https://en.wikipedia.org/wiki/Analytical_hierarchy "Analytical hierarchy"). The higher-order counterparts of the major subsystems of second-order arithmetic generally prove the same second-order sentences (or a large subset) as the original second-order systems.[^5] For instance, the base theory of higher-order reverse mathematics, called RCA <sup><i>ω</i></sup>  
<sub>0</sub>, proves the same sentences as RCA <sub>0</sub>, up to language.

As noted in the previous paragraph, second-order comprehension axioms easily generalize to the higher-order framework. However, theorems expressing the *[compactness](https://en.wikipedia.org/wiki/Compactness "Compactness")* of basic spaces behave quite differently in second- and higher-order arithmetic: on one hand, when restricted to countable covers/the language of second-order arithmetic, the compactness of the unit interval is provable in WKL <sub>0</sub> from the next section. On the other hand, given uncountable covers/the language of higher-order arithmetic, the compactness of the unit interval is only provable from (full) second-order arithmetic.[^6] Other covering lemmas (e.g. due to [Lindelöf](https://en.wikipedia.org/wiki/Lindel%C3%B6f "Lindelöf"), [Vitali](https://en.wikipedia.org/wiki/Giuseppe_Vitali "Giuseppe Vitali"), [Besicovitch](https://en.wikipedia.org/wiki/Besicovitch "Besicovitch"), etc.) exhibit the same behavior, and many basic properties of the [gauge integral](https://en.wikipedia.org/wiki/Gauge_integral "Gauge integral") are equivalent to the compactness of the underlying space.

## The big five subsystems of second-order arithmetic

[Second-order arithmetic](https://en.wikipedia.org/wiki/Second-order_arithmetic "Second-order arithmetic") is a formal theory of the natural numbers and sets of natural numbers. Many mathematical objects, such as [countable](https://en.wikipedia.org/wiki/Countable_set "Countable set") [rings](https://en.wikipedia.org/wiki/Ring_\(mathematics\) "Ring (mathematics)"), [groups](https://en.wikipedia.org/wiki/Group_\(mathematics\) "Group (mathematics)"), and [fields](https://en.wikipedia.org/wiki/Field_\(mathematics\) "Field (mathematics)"), as well as points in [effective Polish spaces](https://en.wikipedia.org/wiki/Effective_Polish_space "Effective Polish space"), can be represented as sets of natural numbers, and modulo this representation can be studied in second-order arithmetic.

Reverse mathematics makes use of several subsystems of second-order arithmetic. A typical reverse mathematics theorem shows that a particular mathematical theorem *T* is equivalent to a particular subsystem *S* of second-order arithmetic over a weaker subsystem *B*. This weaker system *B* is known as the **base system** for the result; in order for the reverse mathematics result to have meaning, this system must not itself be able to prove the mathematical theorem *T*.

Steve Simpson describes five particular subsystems of second-order arithmetic, which he calls the **Big Five**, that occur frequently in reverse mathematics.[^7] [^8] In order of increasing strength, these systems are named by the initialisms RCA <sub>0</sub>, WKL <sub>0</sub>, ACA <sub>0</sub>, ATR <sub>0</sub>, and Π <sup>1</sup>  
<sub>1</sub> -CA <sub>0</sub>.

The following table summarizes the "big five" systems [^9] and lists the counterpart systems in higher-order arithmetic.[^5] The latter generally prove the same second-order sentences (or a large subset) as the original second-order systems.[^5]

| Subsystem | Stands for | [Ordinal](https://en.wikipedia.org/wiki/Ordinal_analysis "Ordinal analysis") | Corresponds roughly to | Comments | Higher-order counterpart |
| --- | --- | --- | --- | --- | --- |
| RCA <sub>0</sub> | Recursive comprehension axiom | ω <sup>ω</sup> | Constructive mathematics ([Bishop](https://en.wikipedia.org/wiki/Errett_Bishop "Errett Bishop")) | The base theory | RCA <sup>ω</sup>   <sub>0</sub>; proves the same second-order sentences as RCA <sub>0</sub> |
| WKL <sub>0</sub> | Weak Kőnig's lemma | ω <sup>ω</sup> | Finitistic reductionism ([Hilbert](https://en.wikipedia.org/wiki/David_Hilbert "David Hilbert")) | Conservative over [PRA](https://en.wikipedia.org/wiki/Primitive_recursive_arithmetic "Primitive recursive arithmetic") (resp. RCA <sub>0</sub>) for Π <sup>0</sup>   <sub>2</sub> (resp. Π <sup>1</sup>   <sub>1</sub>) sentences | Fan functional; computes modulus of uniform continuity on ${\displaystyle 2^{\mathbb {N} }}$ for continuous functions |
| ACA <sub>0</sub> | Arithmetical comprehension axiom | [ε <sub>0</sub>](https://en.wikipedia.org/wiki/Epsilon_numbers_\(mathematics\) "Epsilon numbers (mathematics)") | Predicativism ([Weyl](https://en.wikipedia.org/wiki/Hermann_Weyl "Hermann Weyl"), [Feferman](https://en.wikipedia.org/wiki/Solomon_Feferman "Solomon Feferman")) | Conservative over Peano arithmetic for arithmetical sentences | The 'Turing jump' functional ∃ <sup>2</sup> expresses the existence of a discontinuous function on ℝ |
| ATR <sub>0</sub> | Arithmetical transfinite recursion | [Γ <sub>0</sub>](https://en.wikipedia.org/wiki/Feferman%E2%80%93Sch%C3%BCtte_ordinal "Feferman–Schütte ordinal") | Predicative reductionism (Friedman, Simpson) | Conservative over Feferman's system IR for Π <sup>1</sup>   <sub>1</sub> sentences | The 'transfinite recursion' functional outputs the set claimed to exist by ATR <sub>0</sub>. |
| Π <sup>1</sup>   <sub>1</sub> -CA <sub>0</sub> | Π <sup>1</sup>   <sub>1</sub> comprehension axiom | [Ψ <sub>0</sub> (Ω <sub>ω</sub>)](https://en.wikipedia.org/wiki/Buchholz%27s_ordinal "Buchholz's ordinal") | Impredicativism |  | The Suslin functional *S* <sup>2</sup> decides Π <sup>1</sup>   <sub>1</sub> -formulas (restricted to second-order parameters). |

The subscript <sub>0</sub> in these names means that the induction scheme has been restricted from the full second-order induction scheme.[^10] For example, ACA <sub>0</sub> includes the induction axiom (0 ∈ *X* ${\displaystyle \wedge }$ ∀ *n* (*n* ∈ *X* → *n* + 1 ∈ *X*)) → ∀ *n* *n* ∈ X. This together with the full comprehension axiom of second-order arithmetic implies the full second-order induction scheme given by the universal closure of (*φ* (0) ${\displaystyle \wedge }$ ∀ *n* (*φ* (*n*) → *φ* (*n* +1))) → ∀ *n* *φ* (*n*) for any second-order formula *φ*. However ACA <sub>0</sub> does not have the full comprehension axiom, and the subscript <sub>0</sub> is a reminder that it does not have the full second-order induction scheme either. This restriction is important: systems with restricted induction have significantly lower [proof-theoretical ordinals](https://en.wikipedia.org/wiki/Ordinal_analysis "Ordinal analysis") than systems with the full second-order induction scheme.

### Base system RCA0

RCA <sub>0</sub> is the fragment of second-order arithmetic whose axioms are the axioms of [Robinson arithmetic](https://en.wikipedia.org/wiki/Robinson_arithmetic "Robinson arithmetic"), [induction for Σ <sup>0</sup>  
<sub>1</sub> formulas](https://en.wikipedia.org/wiki/Induction,_bounding_and_least_number_principles "Induction, bounding and least number principles"), and comprehension for Δ <sup>0</sup>  
<sub>1</sub> formulas.

The subsystem RCA <sub>0</sub> is the one most commonly used as a base system for reverse mathematics. The initials "RCA" stand for "recursive comprehension axiom", where "recursive" means "computable", as in [computable function](https://en.wikipedia.org/wiki/Computable_function "Computable function"). This name is used because RCA <sub>0</sub> corresponds informally to "computable mathematics". In particular, any set of natural numbers that can be proven to exist in RCA <sub>0</sub> is computable, and thus any theorem that implies that noncomputable sets exist is not provable in RCA <sub>0</sub>. To this extent, RCA <sub>0</sub> is a constructive system, although it does not meet the requirements of the program of [constructivism](https://en.wikipedia.org/wiki/Constructivism_\(mathematics\) "Constructivism (mathematics)") because it is a theory in classical logic including the [law of excluded middle](https://en.wikipedia.org/wiki/Law_of_excluded_middle "Law of excluded middle").

Despite its seeming weakness (of not proving any non-computable sets exist), RCA <sub>0</sub> is sufficient to prove a number of classical theorems which, therefore, require only minimal logical strength. These theorems are, in a sense, below the reach of the reverse mathematics enterprise because they are already provable in the base system. The classical theorems provable in RCA <sub>0</sub> include:

- Basic properties of the natural numbers, integers, and rational numbers (for example, that the latter form an [ordered field](https://en.wikipedia.org/wiki/Ordered_field "Ordered field")).
- Basic properties of the real numbers (the real numbers are an [Archimedean](https://en.wikipedia.org/wiki/Archimedean_property "Archimedean property") ordered field; any [nested sequence of closed intervals](https://en.wikipedia.org/wiki/Nested_sequence_of_closed_intervals "Nested sequence of closed intervals") whose lengths tend to zero has a single point in its intersection; the real numbers are not countable).[^1] <sup>Section II.4</sup>
- The [Baire category theorem](https://en.wikipedia.org/wiki/Baire_category_theorem "Baire category theorem") for a [complete](https://en.wikipedia.org/wiki/Complete_metric_space "Complete metric space") [separable](https://en.wikipedia.org/wiki/Separable_space "Separable space") [metric space](https://en.wikipedia.org/wiki/Metric_space "Metric space") (the separability condition is necessary to even state the theorem in the language of second-order arithmetic).[^1] <sup>theorem II.5.8</sup>
- The [intermediate value theorem](https://en.wikipedia.org/wiki/Intermediate_value_theorem "Intermediate value theorem") on continuous real functions.[^1] <sup>theorem II.6.6</sup>
- The [Banach–Steinhaus theorem](https://en.wikipedia.org/wiki/Banach%E2%80%93Steinhaus_theorem "Banach–Steinhaus theorem") for a sequence of continuous linear operators on separable Banach spaces.[^1] <sup>theorem II.10.8</sup>
- A weak version of [Gödel's completeness theorem](https://en.wikipedia.org/wiki/G%C3%B6del%27s_completeness_theorem "Gödel's completeness theorem") (for a set of sentences, in a countable language, that is already closed under consequence).
- The existence of an [algebraic closure](https://en.wikipedia.org/wiki/Algebraic_closure "Algebraic closure") for a countable field (but not its uniqueness).[^1] <sup>II.9.4–II.9.8</sup>
- The existence and uniqueness of the [real closure](https://en.wikipedia.org/wiki/Real_closed_field "Real closed field") of a countable ordered field.[^1] <sup>II.9.5, II.9.7</sup>

The first-order part of RCA <sub>0</sub> (the theorems of the system that do not involve any set variables) is the set of theorems of first-order Peano arithmetic with [induction](https://en.wikipedia.org/wiki/Induction,_bounding_and_least_number_principles "Induction, bounding and least number principles") limited to Σ <sup>0</sup>  
<sub>1</sub> formulas.[^1] <sup>Corollary IX.1.11</sup> It is provably consistent, as is RCA <sub>0</sub>, in full first-order Peano arithmetic.

### Weak Kőnig's lemma WKL0

The subsystem WKL <sub>0</sub> consists of RCA <sub>0</sub> plus a weak form of [Kőnig's lemma](https://en.wikipedia.org/wiki/K%C5%91nig%27s_lemma "Kőnig's lemma"), namely the statement that every infinite subtree of the full binary tree (the tree of all finite sequences of 0s and 1s) has an infinite path. This proposition, which is known as *weak Kőnig's lemma*, is easy to state in the language of second-order arithmetic. WKL <sub>0</sub> can also be defined as the principle of Σ <sup>0</sup>  
<sub>1</sub> separation (given two Σ <sup>0</sup>  
<sub>1</sub> formulas of a free variable *n* that are exclusive, there is a set containing all *n* satisfying the one and no *n* satisfying the other). When this axiom is added to RCA <sub>0</sub>, the resulting subsystem is called WKL <sub>0</sub>. A similar distinction between particular axioms on the one hand, and subsystems including the basic axioms and induction on the other hand, is made for the stronger subsystems described below.

In a sense, weak Kőnig's lemma is a form of the [axiom of choice](https://en.wikipedia.org/wiki/Axiom_of_choice "Axiom of choice") (although, as stated, it can be proven in classical Zermelo–Fraenkel set theory without the axiom of choice). It is not constructively valid in some senses of the word "constructive".

To show that WKL <sub>0</sub> is actually stronger than (not provable in) RCA <sub>0</sub>, it is sufficient to exhibit a theorem of WKL <sub>0</sub> that implies that noncomputable sets exist. This is not difficult; WKL <sub>0</sub> implies the existence of separating sets for effectively inseparable recursively enumerable sets.

It turns out that RCA <sub>0</sub> and WKL <sub>0</sub> have the same first-order part, meaning that they prove the same first-order sentences. WKL <sub>0</sub> can prove a good number of classical mathematical results that do not follow from RCA <sub>0</sub>, however. These results are not expressible as first-order statements but can be expressed as second-order statements.

The following results are equivalent to weak Kőnig's lemma and thus to WKL <sub>0</sub> over RCA <sub>0</sub>:

- The [Heine–Borel theorem](https://en.wikipedia.org/wiki/Heine%E2%80%93Borel_theorem "Heine–Borel theorem") for the closed unit real interval, in the following sense: every covering by a sequence of open intervals has a finite subcovering.
- The Heine–Borel theorem for complete totally bounded separable metric spaces (where covering is by a sequence of open balls).
- A continuous real function on the closed unit interval (or on any compact separable metric space, as above) is bounded (or: bounded and reaches its bounds).
- A continuous real function on the closed unit interval can be uniformly approximated by polynomials (with rational coefficients).
- A continuous real function on the closed unit interval is uniformly continuous.
- A continuous real function on the closed unit interval is [Riemann](https://en.wikipedia.org/wiki/Riemann_integral "Riemann integral") integrable.
- The [Brouwer fixed point theorem](https://en.wikipedia.org/wiki/Brouwer_fixed_point_theorem "Brouwer fixed point theorem") (for continuous functions on an *n* -simplex).[^1] <sup>Theorem IV.7.7</sup>
- The separable [Hahn–Banach theorem](https://en.wikipedia.org/wiki/Hahn%E2%80%93Banach_theorem "Hahn–Banach theorem") in the form: a bounded linear form on a subspace of a separable Banach space extends to a bounded linear form on the whole space.
- The [Jordan curve theorem](https://en.wikipedia.org/wiki/Jordan_curve_theorem "Jordan curve theorem").
- Gödel's completeness theorem (for a countable language).
- Determinacy for open (or even clopen) games on {0, 1} of length ω.
- Every countable [commutative ring](https://en.wikipedia.org/wiki/Commutative_ring "Commutative ring") has a [prime ideal](https://en.wikipedia.org/wiki/Prime_ideal "Prime ideal").
- Every countable formally real field is orderable.
- Uniqueness of algebraic closure (for a countable field).
- The [De Bruijn–Erdős theorem](https://en.wikipedia.org/wiki/De_Bruijn%E2%80%93Erd%C5%91s_theorem_\(graph_theory\) "De Bruijn–Erdős theorem (graph theory)") for countable graphs: every countable graph whose finite subgraphs are *k* -colorable is *k* -colorable.[^11]

### Arithmetical comprehension ACA0

ACA <sub>0</sub> is RCA <sub>0</sub> plus the comprehension scheme for arithmetical formulas (which is sometimes called the "arithmetical comprehension axiom"). That is, ACA <sub>0</sub> allows us to form the set of natural numbers satisfying an arbitrary arithmetical formula (one with no bound set variables, although possibly containing set parameters).[^1] <sup>pp. 6–7</sup> It suffices to add to RCA <sub>0</sub> the comprehension scheme for Σ <sub>1</sub> formulas (also including second-order free variables) in order to obtain full arithmetical comprehension.[^1] <sup>Lemma III.1.3</sup>

The first-order part of ACA <sub>0</sub> is exactly first-order Peano arithmetic; ACA <sub>0</sub> is a *conservative* extension of first-order Peano arithmetic.[^1] <sup>Corollary IX.1.6</sup> The two systems are provably (in a weak system) equiconsistent. ACA <sub>0</sub> can be thought of as a framework of [predicative](https://en.wikipedia.org/wiki/Impredicativity "Impredicativity") mathematics, although there are predicatively provable theorems that are not provable in ACA <sub>0</sub>. Most of the fundamental results about the natural numbers, and many other mathematical theorems, can be proven in this system.

One way of seeing that ACA <sub>0</sub> is stronger than WKL <sub>0</sub> is to exhibit a model of WKL <sub>0</sub> that does not contain all arithmetical sets. In fact, it is possible to build a model of WKL <sub>0</sub> consisting entirely of [low sets](https://en.wikipedia.org/wiki/Low_\(computability\) "Low (computability)") using the [low basis theorem](https://en.wikipedia.org/wiki/Low_basis_theorem "Low basis theorem"), since low sets relative to low sets are low.

The following assertions are equivalent to ACA <sub>0</sub> over RCA <sub>0</sub>:

- The sequential completeness of the real numbers (every bounded increasing sequence of real numbers has a limit).[^1] <sup>theorem III.2.2</sup>
- The [Bolzano–Weierstrass theorem](https://en.wikipedia.org/wiki/Bolzano%E2%80%93Weierstrass_theorem "Bolzano–Weierstrass theorem").[^1] <sup>theorem III.2.2</sup>
- [Ascoli's theorem](https://en.wikipedia.org/wiki/Ascoli%27s_theorem "Ascoli's theorem"): every bounded equicontinuous sequence of real functions on the unit interval has a uniformly convergent subsequence.
- Every countable field embeds isomorphically into its algebraic closure.[^1] <sup>theorem III.3.2</sup>
- Every countable commutative ring has a [maximal ideal](https://en.wikipedia.org/wiki/Maximal_ideal "Maximal ideal").[^1] <sup>theorem III.5.5</sup>
- Every countable vector space over the rationals (or over any countable field) has a basis.[^1] <sup>theorem III.4.3</sup>
- For any countable fields *K* ⊆ *L*, there is a [transcendence basis](https://en.wikipedia.org/wiki/Transcendence_basis "Transcendence basis") for *L* over *K*.[^1] <sup>theorem III.4.6</sup>
- Kőnig's lemma (for arbitrary finitely branching trees, as opposed to the weak version described above).[^1] <sup>theorem III.7.2</sup>
- For any countable group *G* and any subgroups *H*, *I* of *G*, the subgroup generated by *H* ∪ *I* exists.[^12] <sup>p.40</sup>
- Any partial function can be extended to a total function.[^13]
- [Higman's lemma](https://en.wikipedia.org/wiki/Higman%27s_lemma "Higman's lemma").[^1] <sup>Theorem X.3.22</sup>
- Various theorems in combinatorics, such as certain forms of [Ramsey's theorem](https://en.wikipedia.org/wiki/Ramsey%27s_theorem "Ramsey's theorem").[^14] [^1] <sup>Theorem III.7.2</sup>

### Arithmetical transfinite recursion ATR0

The system ATR <sub>0</sub> adds to ACA <sub>0</sub> an axiom that states, informally, that any arithmetical functional (meaning any arithmetical formula with a free number variable *n* and a free set variable *X*, seen as the operator taking *X* to the set of *n* satisfying the formula) can be iterated transfinitely along any countable [well ordering](https://en.wikipedia.org/wiki/Well_ordering "Well ordering") starting with any set. ATR <sub>0</sub> is equivalent over ACA <sub>0</sub> to the principle of Σ <sup>1</sup>  
<sub>1</sub> separation. ATR <sub>0</sub> is impredicative, and has the [proof-theoretic ordinal](https://en.wikipedia.org/wiki/Ordinal_analysis "Ordinal analysis") Γ <sub>0</sub>, the supremum of that of predicative systems.

ATR <sub>0</sub> proves the consistency of ACA <sub>0</sub>, and thus by [Gödel's theorem](https://en.wikipedia.org/wiki/G%C3%B6del%27s_incompleteness_theorems "Gödel's incompleteness theorems") it is strictly stronger.

The following assertions are equivalent to ATR <sub>0</sub> over RCA <sub>0</sub>:

- Any two countable well orderings are comparable. That is, they are isomorphic or one is isomorphic to a proper initial segment of the other.[^1] <sup>theorem V.6.8</sup>
- [Ulm's theorem](https://en.wikipedia.org/wiki/Ulm%27s_theorem "Ulm's theorem") for countable reduced Abelian groups.
- The [perfect set theorem](https://en.wikipedia.org/wiki/Perfect_set_property "Perfect set property"), which states that every uncountable closed subset of a complete separable metric space contains a perfect closed set.
- [Lusin's separation theorem](https://en.wikipedia.org/wiki/Lusin%27s_separation_theorem "Lusin's separation theorem") (essentially Σ <sup>1</sup>  
	<sub>1</sub> separation).[^1] <sup>Theorem V.5.1</sup>
- [Determinacy](https://en.wikipedia.org/wiki/Determinacy "Determinacy") for [open sets](https://en.wikipedia.org/wiki/Open_set "Open set") in the [Baire space](https://en.wikipedia.org/wiki/Baire_space "Baire space").

### Π11 comprehension Π11-CA0

Π <sup>1</sup>  
<sub>1</sub> -CA <sub>0</sub> is stronger than arithmetical transfinite recursion and is fully impredicative. It consists of RCA <sub>0</sub> plus the comprehension scheme for Π <sup>1</sup>  
<sub>1</sub> formulas.

In a sense, Π <sup>1</sup>  
<sub>1</sub> -CA <sub>0</sub> comprehension is to arithmetical transfinite recursion (Σ <sup>1</sup>  
<sub>1</sub> separation) as ACA <sub>0</sub> is to weak Kőnig's lemma (Σ <sup>0</sup>  
<sub>1</sub> separation). It is equivalent to several statements of descriptive set theory whose proofs make use of strongly impredicative arguments; this equivalence shows that these impredicative arguments cannot be removed.

The following theorems are equivalent to Π <sup>1</sup>  
<sub>1</sub> -CA <sub>0</sub> over RCA <sub>0</sub>:

- The [Cantor–Bendixson theorem](https://en.wikipedia.org/wiki/Cantor%E2%80%93Bendixson_theorem "Cantor–Bendixson theorem") (every closed set of reals is the union of a perfect set and a countable set).[^1] <sup>Exercise VI.1.7</sup>
- [Silver's dichotomy](https://en.wikipedia.org/wiki/Silver%27s_dichotomy "Silver's dichotomy") (every coanalytic equivalence relation has either countably many equivalence classes or a perfect set of incomparables) [^1] <sup>Theorem VI.3.6</sup>
- Every countable abelian group is the direct sum of a divisible group and a reduced group.[^1] <sup>Theorem VI.4.1</sup>
- Determinacy for Σ <sup>0</sup>  
	<sub>1</sub> ${\displaystyle \wedge }$ Π <sup>0</sup>  
	<sub>1</sub> games.[^1] <sup>Theorem VI.5.4</sup>

## Additional systems

- Weaker systems than recursive comprehension can be defined. The weak system RCA <sup>*</sup>  
	<sub>0</sub> consists of [elementary function arithmetic](https://en.wikipedia.org/wiki/Elementary_function_arithmetic "Elementary function arithmetic") EFA (the basic axioms plus Δ <sup>0</sup>  
	<sub>0</sub> induction in the enriched language with an exponential operation) plus Δ <sup>0</sup>  
	<sub>1</sub> comprehension. Over RCA <sup>*</sup>  
	<sub>0</sub>, recursive comprehension as defined earlier (that is, with Σ <sup>0</sup>  
	<sub>1</sub> induction) is equivalent to the statement that a polynomial (over a countable field) has only finitely many roots and to the classification theorem for finitely generated Abelian groups. The system RCA <sup>*</sup>  
	<sub>0</sub> has the same [proof theoretic ordinal](https://en.wikipedia.org/wiki/Ordinal_analysis "Ordinal analysis") ω <sup>3</sup> as EFA and is conservative over EFA for Π <sup>0</sup>  
	<sub>2</sub> sentences.
- Weak Weak Kőnig's Lemma is the statement that a subtree of the infinite binary tree having no infinite paths has an asymptotically vanishing proportion of the leaves at length *n* (with a uniform estimate as to how many leaves of length *n* exist). An equivalent formulation is that any subset of Cantor space that has positive measure is nonempty (this is not provable in RCA <sub>0</sub>). WWKL <sub>0</sub> is obtained by adjoining this axiom to RCA <sub>0</sub>. It is equivalent to the statement that if the unit real interval is covered by a sequence of intervals then the sum of their lengths is at least one. The model theory of WWKL <sub>0</sub> is closely connected to the theory of [algorithmically random sequences](https://en.wikipedia.org/wiki/Algorithmically_random_sequence "Algorithmically random sequence"). In particular, an ω-model of RCA <sub>0</sub> satisfies weak weak Kőnig's lemma if and only if for every set *X* there is a set *Y* that is 1-random relative to *X*.
- DNR (short for "diagonally non-recursive") adds to RCA <sub>0</sub> an axiom asserting the existence of a [diagonally non-recursive](https://en.wikipedia.org/wiki/Kleene%27s_recursion_theorem#Fixed-point-free_functions "Kleene's recursion theorem") function relative to every set. That is, DNR states that, for any set *A*, there exists a total function *f* such that for all *e* the *e* th partial recursive function with oracle *A* is not equal to *f*. DNR is strictly weaker than WWKL (Lempp *et al.*, 2004).
- Δ <sup>1</sup>  
	<sub>1</sub> -comprehension is in certain ways analogous to arithmetical transfinite recursion as recursive comprehension is to weak Kőnig's lemma. It has the hyperarithmetical sets as minimal ω-model. Arithmetical transfinite recursion proves Δ <sup>1</sup>  
	<sub>1</sub> -comprehension but not the other way around.
- Σ <sup>1</sup>  
	<sub>1</sub> -choice is the statement that if *η* (*n*, *X*) is a Σ <sup>1</sup>  
	<sub>1</sub> formula such that for each *n* there exists an *X* satisfying *η* then there is a sequence of sets *X <sub>n</sub>* such that *η* (*n*, *X <sub>n</sub>*) holds for each *n*. Σ <sup>1</sup>  
	<sub>1</sub> -choice also has the hyperarithmetical sets as minimal ω-model. Arithmetical transfinite recursion proves Σ <sup>1</sup>  
	<sub>1</sub> -choice but not the other way around.
- HBU (short for "uncountable Heine-Borel") expresses the (open-cover) [compactness](https://en.wikipedia.org/wiki/Compactness "Compactness") of the unit interval, involving *uncountable covers*. The latter aspect of HBU makes it only expressible in the language of *third-order* arithmetic. [Cousin's theorem](https://en.wikipedia.org/wiki/Cousin%27s_theorem "Cousin's theorem") (1895) implies HBU, and these theorems use the same notion of cover due to [Cousin](https://en.wikipedia.org/wiki/Cousin "Cousin") and [Lindelöf](https://en.wikipedia.org/wiki/Lindel%C3%B6f "Lindelöf"). HBU is *hard* to prove: in terms of the usual hierarchy of comprehension axioms, a proof of HBU requires full second-order arithmetic.[^6]
- [Ramsey's theorem](https://en.wikipedia.org/wiki/Ramsey%27s_theorem "Ramsey's theorem") for infinite graphs does not fall into one of the big five subsystems, and there are many other weaker variants with varying proof strengths.[^14]

### Stronger systems

Over RCA <sub>0</sub>, **Π <sup>1</sup>  
<sub>1</sub>** transfinite recursion, **∆ <sup>0</sup>  
<sub>2</sub>** determinacy, and the **∆ <sup>1</sup>  
<sub>1</sub>** Ramsey theorem are all equivalent to each other.

Over RCA <sub>0</sub>, **Σ <sup>1</sup>  
<sub>1</sub>** monotonic induction, **Σ <sup>0</sup>  
<sub>2</sub>** determinacy, and the **Σ <sup>1</sup>  
<sub>1</sub>** Ramsey theorem are all equivalent to each other.

The following are equivalent:[^15] [^16]

- (schema) Π <sup>1</sup>  
	<sub>3</sub> consequences of Π <sup>1</sup>  
	<sub>2</sub> -CA <sub>0</sub>
- RCA <sub>0</sub> + (schema over finite *n*) determinacy in the *n* th level of the difference hierarchy of **Σ <sup>0</sup>  
	<sub>2</sub>** sets
- RCA <sub>0</sub> + { *τ*: *τ* is a true [S2S](https://en.wikipedia.org/wiki/S2S_\(mathematics\) "S2S (mathematics)") sentence}

The set of Π <sup>1</sup>  
<sub>3</sub> consequences of second-order arithmetic Z <sub>2</sub> has the same theory as RCA <sub>0</sub> + (schema over finite *n*) determinacy in the *n* th level of the difference hierarchy of **Σ <sup>0</sup>  
<sub>3</sub>** sets.[^17]

For a [poset](https://en.wikipedia.org/wiki/Poset "Poset") *P*, let MF(*P*) denote the topological space consisting of the filters on *P* whose open sets are the sets of the form { *F* ∈ MF(*P*) | *p* ∈ *F* } for some *p* ∈ *P*. The following statement is equivalent to ${\displaystyle \Pi _{2}^{1}{\mathsf {-CA}}_{0}}$ over ${\displaystyle \Pi _{1}^{1}{\mathsf {-CA}}_{0}}$: for any countable poset *P*, the topological space MF(*P*) is [completely metrizable](https://en.wikipedia.org/wiki/Completely_metrizable_space "Completely metrizable space") iff it is [regular](https://en.wikipedia.org/wiki/Regular_topological_space "Regular topological space").[^18]

## ω-models and β-models

The ω in ω-model stands for the set of non-negative integers (or finite ordinals). An ω-model is a model for a fragment of second-order arithmetic whose first-order part is the standard model of Peano arithmetic,[^1] but whose second-order part may be non-standard. More precisely, an ω-model is given by a choice ${\displaystyle S\subseteq {\mathcal {P}}(\omega )}$ of subsets of ω. The first-order variables are interpreted in the usual way as elements of ω, and +, × have their usual meanings, while second-order variables are interpreted as elements of *S*. There is a standard ω-model where one just takes *S* to consist of all subsets of the integers. However, there are also other ω-models; for example, RCA <sub>0</sub> has a minimal ω-model where *S* consists of the computable subsets of ω.

A β-model is an ω model that agrees with the standard ω-model on truth of Π <sup>1</sup>  
<sub>1</sub> and Σ <sup>1</sup>  
<sub>1</sub> sentences (with parameters).

Non-ω models are also useful, especially in the proofs of conservation theorems.

## Constructive reverse mathematics

Constructive reverse mathematics is a program which is applied to [constructive mathematics](https://en.wikipedia.org/wiki/Constructivism_\(philosophy_of_mathematics\) "Constructivism (philosophy of mathematics)").[^19] It involves classifying theorems into 4 main systems: BISH (Bishop-style constructive mathematics), CLASS, INT, and RUSS.[^20]

## See also

- [Closed-form expression § Conversion from numerical forms](https://en.wikipedia.org/wiki/Closed-form_expression#Conversion_from_numerical_forms "Closed-form expression")
- [Induction, bounding and least number principles](https://en.wikipedia.org/wiki/Induction,_bounding_and_least_number_principles "Induction, bounding and least number principles")
- [Ordinal analysis](https://en.wikipedia.org/wiki/Ordinal_analysis "Ordinal analysis")

## References

## References/Further Reading

- Ambos-Spies, K.; Kjos-Hanssen, B.; Lempp, S.; Slaman, T.A. (2004), "Comparing DNR and WWKL", *[Journal of Symbolic Logic](https://en.wikipedia.org/wiki/Journal_of_Symbolic_Logic "Journal of Symbolic Logic")*, **69** (4): 1089, [arXiv](https://en.wikipedia.org/wiki/ArXiv_\(identifier\) "ArXiv (identifier)"):[1408.2281](https://arxiv.org/abs/1408.2281), [doi](https://en.wikipedia.org/wiki/Doi_\(identifier\) "Doi (identifier)"):[10.2178/jsl/1102022212](https://doi.org/10.2178%2Fjsl%2F1102022212), [S2CID](https://en.wikipedia.org/wiki/S2CID_\(identifier\) "S2CID (identifier)") [17582399](https://api.semanticscholar.org/CorpusID:17582399).
- Friedman, Harvey (1975), "Some systems of second-order arithmetic and their use", *Proceedings of the International Congress of Mathematicians (Vancouver, B. C., 1974), Vol. 1*, Montreal: Canad. Math. Congress, pp. 235–242, [MR](https://en.wikipedia.org/wiki/MR_\(identifier\) "MR (identifier)") [0429508](https://mathscinet.ams.org/mathscinet-getitem?mr=0429508)
- Friedman, Harvey (1976), Baldwin, John; [Martin, D. A.](https://en.wikipedia.org/wiki/Donald_A._Martin "Donald A. Martin"); [Soare, R. I.](https://en.wikipedia.org/wiki/Robert_I._Soare "Robert I. Soare"); [Tait, W. W.](https://en.wikipedia.org/wiki/William_W._Tait "William W. Tait") (eds.), "Systems of second-order arithmetic with restricted induction, I, II", Meeting of the Association for Symbolic Logic, *The Journal of Symbolic Logic*, **41** (2): 557–559, [doi](https://en.wikipedia.org/wiki/Doi_\(identifier\) "Doi (identifier)"):[10.2307/2272259](https://doi.org/10.2307%2F2272259), [JSTOR](https://en.wikipedia.org/wiki/JSTOR_\(identifier\) "JSTOR (identifier)") [2272259](https://www.jstor.org/stable/2272259)
- Hirschfeldt, Denis R. (2014), [*Slicing the Truth*](https://en.wikipedia.org/wiki/Slicing_the_Truth "Slicing the Truth"), Lecture Notes Series of the Institute for Mathematical Sciences, National University of Singapore, vol. 28, World Scientific
- Hunter, James (2008), [*Reverse Topology*](https://www.math.wisc.edu/~lempp/theses/hunter.pdf) (PDF) (PhD thesis), [University of Wisconsin–Madison](https://en.wikipedia.org/wiki/University_of_Wisconsin%E2%80%93Madison "University of Wisconsin–Madison")
- Kohlenbach, Ulrich (2005), ["Higher order reverse mathematics"](https://www2.mathematik.tu-darmstadt.de/~kohlenbach/), in Simpson, Stephen G (ed.), [*Higher Order Reverse Mathematics, Reverse Mathematics 2001*](https://www.brics.dk//RS/00/49/BRICS-RS-00-49.pdf) (PDF), Lecture notes in Logic, [Cambridge University Press](https://en.wikipedia.org/wiki/Cambridge_University_Press "Cambridge University Press"), pp. 281–295, [CiteSeerX](https://en.wikipedia.org/wiki/CiteSeerX_\(identifier\) "CiteSeerX (identifier)") [10.1.1.643.551](https://citeseerx.ist.psu.edu/viewdoc/summary?doi=10.1.1.643.551), [doi](https://en.wikipedia.org/wiki/Doi_\(identifier\) "Doi (identifier)"):[10.1017/9781316755846.018](https://doi.org/10.1017%2F9781316755846.018), [ISBN](https://en.wikipedia.org/wiki/ISBN_\(identifier\) "ISBN (identifier)") [9781316755846](https://en.wikipedia.org/wiki/Special:BookSources/9781316755846 "Special:BookSources/9781316755846")
- Normann, Dag; Sanders, Sam (2018), "On the mathematical and foundational significance of the uncountable", *[Journal of Mathematical Logic](https://en.wikipedia.org/wiki/Journal_of_Mathematical_Logic "Journal of Mathematical Logic")*, **19**: 1950001, [arXiv](https://en.wikipedia.org/wiki/ArXiv_\(identifier\) "ArXiv (identifier)"):[1711.08939](https://arxiv.org/abs/1711.08939), [doi](https://en.wikipedia.org/wiki/Doi_\(identifier\) "Doi (identifier)"):[10.1142/S0219061319500016](https://doi.org/10.1142%2FS0219061319500016), [S2CID](https://en.wikipedia.org/wiki/S2CID_\(identifier\) "S2CID (identifier)") [119120366](https://api.semanticscholar.org/CorpusID:119120366)
- Simpson, Stephen G. (2009), [*Subsystems of second-order arithmetic*](http://www.math.psu.edu/simpson/sosoa/), Perspectives in Logic (2nd ed.), [Cambridge University Press](https://en.wikipedia.org/wiki/Cambridge_University_Press "Cambridge University Press"), [doi](https://en.wikipedia.org/wiki/Doi_\(identifier\) "Doi (identifier)"):[10.1017/CBO9780511581007](https://doi.org/10.1017%2FCBO9780511581007), [ISBN](https://en.wikipedia.org/wiki/ISBN_\(identifier\) "ISBN (identifier)") [978-0-521-88439-6](https://en.wikipedia.org/wiki/Special:BookSources/978-0-521-88439-6 "Special:BookSources/978-0-521-88439-6"), [MR](https://en.wikipedia.org/wiki/MR_\(identifier\) "MR (identifier)") [2517689](https://mathscinet.ams.org/mathscinet-getitem?mr=2517689)
- [Stillwell, John](https://en.wikipedia.org/wiki/John_Stillwell "John Stillwell") (2018), [*Reverse Mathematics, proofs from the inside out*](https://en.wikipedia.org/wiki/Reverse_Mathematics:_Proofs_from_the_Inside_Out "Reverse Mathematics: Proofs from the Inside Out"), [Princeton University Press](https://en.wikipedia.org/wiki/Princeton_University_Press "Princeton University Press"), [ISBN](https://en.wikipedia.org/wiki/ISBN_\(identifier\) "ISBN (identifier)") [978-0-691-17717-5](https://en.wikipedia.org/wiki/Special:BookSources/978-0-691-17717-5 "Special:BookSources/978-0-691-17717-5")
- Solomon, Reed (1999), "Ordered groups: a case study in reverse mathematics", *[The Bulletin of Symbolic Logic](https://en.wikipedia.org/wiki/The_Bulletin_of_Symbolic_Logic "The Bulletin of Symbolic Logic")*, **5** (1): 45–58, [CiteSeerX](https://en.wikipedia.org/wiki/CiteSeerX_\(identifier\) "CiteSeerX (identifier)") [10.1.1.364.9553](https://citeseerx.ist.psu.edu/viewdoc/summary?doi=10.1.1.364.9553), [doi](https://en.wikipedia.org/wiki/Doi_\(identifier\) "Doi (identifier)"):[10.2307/421140](https://doi.org/10.2307%2F421140), [ISSN](https://en.wikipedia.org/wiki/ISSN_\(identifier\) "ISSN (identifier)") [1079-8986](https://search.worldcat.org/issn/1079-8986), [JSTOR](https://en.wikipedia.org/wiki/JSTOR_\(identifier\) "JSTOR (identifier)") [421140](https://www.jstor.org/stable/421140), [MR](https://en.wikipedia.org/wiki/MR_\(identifier\) "MR (identifier)") [1681895](https://mathscinet.ams.org/mathscinet-getitem?mr=1681895), [S2CID](https://en.wikipedia.org/wiki/S2CID_\(identifier\) "S2CID (identifier)") [508431](https://api.semanticscholar.org/CorpusID:508431)
- Dzhafarov, Damir D.; Mummert, Carl (2022), *Reverse Mathematics: Problems, Reductions, and Proofs*, Theory and Applications of Computability (1st ed.), Springer Cham, pp. XIX, 488, [doi](https://en.wikipedia.org/wiki/Doi_\(identifier\) "Doi (identifier)"):[10.1007/978-3-031-11367-3](https://doi.org/10.1007%2F978-3-031-11367-3), [ISBN](https://en.wikipedia.org/wiki/ISBN_\(identifier\) "ISBN (identifier)") [978-3-031-11367-3](https://en.wikipedia.org/wiki/Special:BookSources/978-3-031-11367-3 "Special:BookSources/978-3-031-11367-3")

## External links

- [Stephen G. Simpson's home page](https://sgslogic.net/)
- [Reverse Mathematics Zoo](https://rmzoo.math.uconn.edu/)

[^1]: Simpson, Stephen G. (2009), Subsystems of second-order arithmetic, Perspectives in Logic (2nd ed.), Cambridge University Press, doi:10.1017/CBO9780511581007, ISBN 978-0-521-88439-6, MR 2517689

[^2]: [Harvey Friedman](https://en.wikipedia.org/wiki/Harvey_Friedman_\(mathematician\) "Harvey Friedman (mathematician)") ([1975](https://en.wikipedia.org/wiki/Reverse_mathematics#CITEREFFriedman1975), [1976](https://en.wikipedia.org/wiki/Reverse_mathematics#CITEREFFriedman1976))

[^3]: H. Friedman, Some systems of second-order arithmetic and their use (1974), *Proceedings of the International Congress of Mathematicians*

[^4]: [Kohlenbach (2005)](https://en.wikipedia.org/wiki/Reverse_mathematics#CITEREFKohlenbach2005).

[^5]: See [Kohlenbach (2005)](https://en.wikipedia.org/wiki/Reverse_mathematics#CITEREFKohlenbach2005) and [Hunter (2008)](https://en.wikipedia.org/wiki/Reverse_mathematics#CITEREFHunter2008).

[^6]: [Normann & Sanders (2018)](https://en.wikipedia.org/wiki/Reverse_mathematics#CITEREFNormannSanders2018).

[^7]: [Simpson (2009)](https://en.wikipedia.org/wiki/Reverse_mathematics#CITEREFSimpson2009).

[^8]: Simpson claims to have *not* invented the term. \[Simpson, S.; Eastaugh, B.; Dean, W. (June 17, 2022). ["Panel Discussion"](https://www.youtube.com/watch?v=asPCn9-qcfg&t=540s). *YouTube*. Paris, France: University of Chicago, Reverse Mathematics and its Philosophy.\]

[^9]: [Simpson (2009)](https://en.wikipedia.org/wiki/Reverse_mathematics#CITEREFSimpson2009), p.42.

[^10]: [Simpson (2009)](https://en.wikipedia.org/wiki/Reverse_mathematics#CITEREFSimpson2009), p. 6.

[^11]: Schmerl, James H. (2000). "Graph coloring and reverse mathematics". *Mathematical Logic Quarterly*. **46** (4): 543–548. [doi](https://en.wikipedia.org/wiki/Doi_\(identifier\) "Doi (identifier)"):[10.1002/1521-3870(200010)46:4<543::AID-MALQ543>3.0.CO;2-E](https://doi.org/10.1002%2F1521-3870%28200010%2946%3A4%3C543%3A%3AAID-MALQ543%3E3.0.CO%3B2-E). [MR](https://en.wikipedia.org/wiki/MR_\(identifier\) "MR (identifier)") [1791549](https://mathscinet.ams.org/mathscinet-getitem?mr=1791549).

[^12]: S. Takashi, " [Reverse Mathematics and Countable Algebraic Systems](https://core.ac.uk/download/pdf/236077134.pdf) ". Ph.D. thesis, Tohoku University, 2016.

[^13]: M. Fujiwara, T. Sato, " [Note on total and partial functions in second-order arithmetic](https://repository.kulib.kyoto-u.ac.jp/dspace/handle/2433/223934) ". In *1950 Proof Theory, Computation Theory and Related Topics*, June 2015.

[^14]: [Hirschfeldt (2014)](https://en.wikipedia.org/wiki/Reverse_mathematics#CITEREFHirschfeldt2014).

[^15]: Kołodziejczyk, Leszek; Michalewski, Henryk (2016). *How unprovable is Rabin's decidability theorem?*. LICS '16: 31st Annual ACM/IEEE Symposium on Logic in Computer Science. [arXiv](https://en.wikipedia.org/wiki/ArXiv_\(identifier\) "ArXiv (identifier)"):[1508.06780](https://arxiv.org/abs/1508.06780).

[^16]: Kołodziejczyk, Leszek (October 19, 2015). ["Question on Decidability of S2S"](https://cs.nyu.edu/pipermail/fom/2015-October/019257.html). FOM.

[^17]: Montalban, Antonio; Shore, Richard (2014). "The limits of determinacy in second order arithmetic: consistency and complexity strength". *[Israel Journal of Mathematics](https://en.wikipedia.org/wiki/Israel_Journal_of_Mathematics "Israel Journal of Mathematics")*. **204**: 477–508. [doi](https://en.wikipedia.org/wiki/Doi_\(identifier\) "Doi (identifier)"):[10.1007/s11856-014-1117-9](https://doi.org/10.1007%2Fs11856-014-1117-9). [S2CID](https://en.wikipedia.org/wiki/S2CID_\(identifier\) "S2CID (identifier)") [287519](https://api.semanticscholar.org/CorpusID:287519).

[^18]: C. Mummert, S. G. Simpson. "Reverse mathematics and ${\displaystyle \Pi _{2}^{1}}$ comprehension". In *Bulletin of Symbolic Logic* vol. 11 (2005), pp. 526–533.

[^19]: Bridges, Douglas; Ishihara, Hajime; Schwichtenberg, Helmut; Rathjen, Michael, eds. (2023), ["An Introduction to Constructive Reverse Mathematics"](https://www.cambridge.org/core/books/handbook-of-constructive-mathematics/an-introduction-to-constructive-reverse-mathematics/FE95F70D10D4BB0DF76BD3C5111BB5DE), *Handbook of Constructive Mathematics*, Encyclopedia of Mathematics and its Applications, Cambridge: Cambridge University Press, pp. 636–660, [ISBN](https://en.wikipedia.org/wiki/ISBN_\(identifier\) "ISBN (identifier)") [978-1-316-51086-5](https://en.wikipedia.org/wiki/Special:BookSources/978-1-316-51086-5 "Special:BookSources/978-1-316-51086-5"), retrieved 2026-04-15 `{{[citation](https://en.wikipedia.org/wiki/Template:Citation "Template:Citation")}}`: CS1 maint: work parameter with ISBN ([link](https://en.wikipedia.org/wiki/Category:CS1_maint:_work_parameter_with_ISBN "Category:CS1 maint: work parameter with ISBN"))

[^20]: Diener, Hannes (2020-04-04), [*Constructive Reverse Mathematics*](http://arxiv.org/abs/1804.05495), arXiv, [doi](https://en.wikipedia.org/wiki/Doi_\(identifier\) "Doi (identifier)"):[10.48550/arXiv.1804.05495](https://doi.org/10.48550%2FarXiv.1804.05495), arXiv:1804.05495, retrieved 2026-04-15