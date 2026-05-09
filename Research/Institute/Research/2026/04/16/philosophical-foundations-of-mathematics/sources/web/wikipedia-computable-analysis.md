In [mathematics](https://en.wikipedia.org/wiki/Mathematics "Mathematics") and [computer science](https://en.wikipedia.org/wiki/Computer_science "Computer science"), **computable analysis** is the study of [mathematical analysis](https://en.wikipedia.org/wiki/Mathematical_analysis "Mathematical analysis") from the perspective of [computability theory](https://en.wikipedia.org/wiki/Computability_theory "Computability theory"). It is concerned with the parts of [real analysis](https://en.wikipedia.org/wiki/Real_analysis "Real analysis") and [functional analysis](https://en.wikipedia.org/wiki/Functional_analysis "Functional analysis") that can be carried out in a [computable](https://en.wikipedia.org/wiki/Computability_theory "Computability theory") manner. The field is closely related to [constructive analysis](https://en.wikipedia.org/wiki/Constructive_analysis "Constructive analysis") and [numerical analysis](https://en.wikipedia.org/wiki/Numerical_analysis "Numerical analysis").

A notable result is that [integration](https://en.wikipedia.org/wiki/Integral "Integral") (in the sense of the [Riemann integral](https://en.wikipedia.org/wiki/Riemann_integral "Riemann integral")) is computable.[^1] This might be considered surprising as an integral is (loosely speaking) an infinite sum. While this result could be explained by the fact that every [computable function](https://en.wikipedia.org/wiki/Computable_function "Computable function") from ${\displaystyle \mathbb {[} 0,1]}$ to ${\displaystyle \mathbb {R} }$ is [uniformly continuous](https://en.wikipedia.org/wiki/Uniformly_continuous "Uniformly continuous"), the notable thing is that the [modulus of continuity](https://en.wikipedia.org/wiki/Modulus_of_continuity "Modulus of continuity") can always be computed without being explicitly given. A similarly surprising fact is that [differentiation](https://en.wikipedia.org/wiki/Differential_calculus "Differential calculus") of [complex functions](https://en.wikipedia.org/wiki/Complex_functions "Complex functions") is also computable, while the same result is *false* for [real functions](https://en.wikipedia.org/wiki/Real_functions "Real functions"); see [§ Basic results](https://en.wikipedia.org/wiki/Computable_analysis#Basic_results).

The above motivating results have no counterpart in [Bishop](https://en.wikipedia.org/wiki/Errett_Bishop "Errett Bishop") 's [constructive analysis](https://en.wikipedia.org/wiki/Constructive_analysis "Constructive analysis"). Instead, it is the stronger form of constructive analysis developed by [Brouwer](https://en.wikipedia.org/wiki/L._E._J._Brouwer "L. E. J. Brouwer") that provides a counterpart in [constructive logic](https://en.wikipedia.org/wiki/Constructive_logic "Constructive logic").

## Basic constructions

A popular model for doing computable analysis is [Turing machines](https://en.wikipedia.org/wiki/Turing_machine "Turing machine"). The tape configuration and interpretation of mathematical structures are described as follows.

### Type 2 Turing machines

A Type 2 Turing machine is a Turing machine with three tapes: An input tape, which is read-only; a working tape, which can be written to and read from; and, notably, an output tape, which is "append-only".

### Real numbers

In this context, real numbers are represented as arbitrary infinite sequences of symbols. These sequences could for instance represent the digits of a real number. Such sequences **need not be computable** — this freedom is both an important one and philosophically unproblematic.[^2] Note that the programs that act on these sequences *do* need to be computable in a reasonable sense.

In the case of real numbers, the usual decimal or binary representations are not appropriate. Instead a signed digit representation first suggested by Brouwer often gets used: The number system is base 2, but the digits are ${\displaystyle {\overline {1}}}$ (representing ${\displaystyle -1}$), 0 and 1. In particular, this means ${\displaystyle 1/2}$ can be represented both as ${\displaystyle 0.1}$ and ${\displaystyle 1.{\overline {1}}}$.

To understand why decimal notation is inappropriate, consider the problem of computing ${\displaystyle z=x+y}$ where ${\displaystyle x=0.(3)}$ and ${\displaystyle y=0.(6)}$, and giving the result ${\displaystyle z}$ in decimal notation. The value of ${\displaystyle z}$ is either ${\displaystyle 0.(9)}$ or ${\displaystyle 1.(0)}$. If the latter result were given for instance, then a finite number ${\displaystyle n}$ of digits of ${\displaystyle x}$ would be read before choosing the digit ${\displaystyle 1}$ before the decimal point in ${\displaystyle z}$ — but then if the ${\displaystyle n+1}$ th digit of ${\displaystyle x}$ were decreased to 2, then the result for ${\displaystyle z}$ would be wrong. Similarly, the former choice ${\displaystyle 0.(9)}$ for ${\displaystyle z}$ would be wrong sometimes. This is essentially the [tablemaker's dilemma](https://en.wikipedia.org/wiki/Table-maker%27s_dilemma "Table-maker's dilemma").

As well as signed digits, there are analogues of [Cauchy sequences](https://en.wikipedia.org/wiki/Cauchy_sequence "Cauchy sequence") and [Dedekind cuts](https://en.wikipedia.org/wiki/Dedekind_cut "Dedekind cut") that could in principle be used instead.

### Computable functions

Computable functions are represented as programs on a Type 2 Turing machine. A program is considered *total* (in the sense of a [total function](https://en.wikipedia.org/wiki/Total_function "Total function") as opposed to [partial function](https://en.wikipedia.org/wiki/Partial_function "Partial function")) if it takes finite time to write any number of symbols on the output tape regardless of the input. A total program runs forever, generating increasingly more digits of the output.

### Names

Results about computability associated with infinite sets often involve namings, which are maps between those sets and recursive representations of subsets thereof. A naming on a set gives rise to a [topology over that set](https://en.wikipedia.org/wiki/Topological_space "Topological space"), as [elaborated upon below](https://en.wikipedia.org/wiki/Computable_analysis#Analogy_between_general_topology_and_computability_theory).

### The issue of Type 1 versus Type 2 computability

Type 1 computability is the naive form of computable analysis in which one restricts the inputs to a machine to be [computable numbers](https://en.wikipedia.org/wiki/Computable_numbers "Computable numbers") instead of arbitrary real numbers.

The difference between the two models lies in the fact that a program that is well-behaved over computable numbers (in the sense of being total) is not necessarily well-behaved over arbitrary real numbers. For instance, there are computable functions over the computable real numbers that map some bounded closed intervals to unbounded open intervals.[^3] These functions cannot be extended to arbitrary real numbers (without making them partial), as all computable functions ${\displaystyle \mathbb {R} \to \mathbb {R} }$ are continuous, and this would then violate the [extreme value theorem](https://en.wikipedia.org/wiki/Extreme_value_theorem "Extreme value theorem"). Since that sort of behaviour could be considered pathological, it is natural to insist that a function should only be considered total if it is total over *all* real numbers, not just the computable ones.

### Realisability

In the event that one is unhappy with using Turing machines (on the grounds that they are low level and somewhat arbitrary), there is a *realisability [topos](https://en.wikipedia.org/wiki/Topos "Topos")* called the [Kleene](https://en.wikipedia.org/wiki/Stephen_Cole_Kleene "Stephen Cole Kleene") –Vesley topos in which one can reduce *computable analysis* to *[constructive analysis](https://en.wikipedia.org/wiki/Constructive_analysis "Constructive analysis")*. This constructive analysis includes everything that is valid in the Brouwer school, and not just the [Bishop](https://en.wikipedia.org/wiki/Errett_Bishop "Errett Bishop") school.[^4] Additionally, a theorem in this school of constructive analysis is that *not all real numbers are computable*, which is constructively **non-equivalent** to *there exist uncomputable numbers*. This school of constructive analysis is therefore in direct contradiction to schools of constructive analysis — such as Markov's — which claim that all functions are computable. It ultimately shows that while [constructive existence](https://en.wikipedia.org/wiki/Existence_property "Existence property") implies computability, it is in fact unproblematic — even useful — to assert that not every function is computable.

## Basic results

- Every computable real function is [continuous](https://en.wikipedia.org/wiki/Continuous_function "Continuous function").[^5]
- The arithmetic operations on real numbers are computable.
- While the [equality](https://en.wikipedia.org/wiki/Equality_\(mathematics\) "Equality (mathematics)") relation is not [decidable](https://en.wikipedia.org/wiki/Decidability_\(logic\) "Decidability (logic)"), the greater-than predicate on unequal real numbers is decidable.
- The [uniform norm](https://en.wikipedia.org/wiki/Uniform_norm "Uniform norm") operator is also computable. This implies the computability of Riemann integration.
- The [Riemann integral](https://en.wikipedia.org/wiki/Riemann_integral "Riemann integral") is a computable operator: In other words, there is an algorithm that will numerically evaluate the integral of any [computable function](https://en.wikipedia.org/wiki/Computable_function "Computable function").
- The differentiation operator over real-valued functions is *not* computable, but over [complex functions](https://en.wikipedia.org/wiki/Complex_functions "Complex functions") *is* computable. The latter result follows from [Cauchy's integral formula](https://en.wikipedia.org/wiki/Cauchy%27s_integral_formula "Cauchy's integral formula") and the computability of integration. The former negative result follows from the fact that differentiation (over real-valued functions) is [discontinuous](https://en.wikipedia.org/wiki/Discontinuous_linear_map "Discontinuous linear map").[^6] This illustrates the gulf between [real analysis](https://en.wikipedia.org/wiki/Real_analysis "Real analysis") and [complex analysis](https://en.wikipedia.org/wiki/Complex_analysis "Complex analysis"), as well as the difficulty of [numerical differentiation](https://en.wikipedia.org/wiki/Numerical_differentiation "Numerical differentiation") over the real numbers, which is often bypassed by extending a function to the [complex numbers](https://en.wikipedia.org/wiki/Complex_number "Complex number") or by using symbolic methods.
- There is a subset of the real numbers called the [computable numbers](https://en.wikipedia.org/wiki/Computable_numbers "Computable numbers"), which by the results above is a [real closed field](https://en.wikipedia.org/wiki/Real_closed_field "Real closed field").

## Analogy between general topology and computability theory

One of the basic results of computable analysis is that every [computable function](https://en.wikipedia.org/wiki/Computable_function "Computable function") from ${\displaystyle \mathbb {R} }$ to ${\displaystyle \mathbb {R} }$ is [continuous](https://en.wikipedia.org/wiki/Continuous_function "Continuous function").[^5] Taking this further, this suggests that there is an analogy between basic notions in topology and basic notions in computability:

- Computable functions are analogous to continuous functions.
- [Semidecidable](https://en.wikipedia.org/wiki/Semidecidable "Semidecidable") sets are analogous to [open sets](https://en.wikipedia.org/wiki/Open_sets "Open sets").
- Co-semidecidable sets are analogous to [closed sets](https://en.wikipedia.org/wiki/Closed_sets "Closed sets").
- There is a computable analogue of topological [compactness](https://en.wikipedia.org/wiki/Compactness "Compactness"). Namely, a subset ${\displaystyle S}$ of ${\displaystyle \mathbb {R} }$ is *computably compact* if it there is a semi-decision procedure " ${\displaystyle \forall _{S}}$ " that, given a semidecidable predicate ${\displaystyle P}$ as input, semi-decides whether every point in the set ${\displaystyle S}$ satisfies the predicate ${\displaystyle P}$.
- The above notion of computable compactness satisfies an analogue of the [Heine–Borel theorem](https://en.wikipedia.org/wiki/Heine%E2%80%93Borel_theorem "Heine–Borel theorem"). In particular, the unit interval ${\displaystyle [0,1]}$ is computably compact.
- [Discrete spaces](https://en.wikipedia.org/wiki/Discrete_space "Discrete space") in topology are analogous to sets in computability where equality between elements is semi-decidable.
- [Hausdorff spaces](https://en.wikipedia.org/wiki/Hausdorff_space "Hausdorff space") in topology are analogous to sets in computability where inequality between elements is semi-decidable.
- There is a close analogy between the degrees of discontinuity of functions in the [Borel hierarchy](https://en.wikipedia.org/wiki/Borel_hierarchy "Borel hierarchy") and the degrees of incomputability provided by the Weihrauch hierarchy.

The analogy suggests that [general topology](https://en.wikipedia.org/wiki/General_topology "General topology") and [computability](https://en.wikipedia.org/wiki/Computability "Computability") are nearly mirror images of each other. The analogy has been made rigorous in the case of [locally compact spaces](https://en.wikipedia.org/wiki/Locally_compact_space "Locally compact space").[^7] This has resulted in the creation of sub-areas of general topology like [domain theory](https://en.wikipedia.org/wiki/Domain_theory "Domain theory") that study [topological spaces](https://en.wikipedia.org/wiki/Topological_space "Topological space") very unlike the [Hausdorff spaces](https://en.wikipedia.org/wiki/Hausdorff_space "Hausdorff space") studied by most people in [mathematical analysis](https://en.wikipedia.org/wiki/Mathematical_analysis "Mathematical analysis") — these spaces become natural under the analogy.

## See also

- [Specker sequence](https://en.wikipedia.org/wiki/Specker_sequence "Specker sequence")

## Notes

## References

- Oliver Aberth (1980), *Computable analysis*, [McGraw-Hill](https://en.wikipedia.org/wiki/McGraw-Hill "McGraw-Hill"), [ISBN](https://en.wikipedia.org/wiki/ISBN_\(identifier\) "ISBN (identifier)") [0-0700-0079-4](https://en.wikipedia.org/wiki/Special:BookSources/0-0700-0079-4 "Special:BookSources/0-0700-0079-4").
- [Marian Pour-El](https://en.wikipedia.org/wiki/Marian_Pour-El "Marian Pour-El") and Ian Richards (1989), *[Computability in Analysis and Physics](https://en.wikipedia.org/wiki/Computability_in_Analysis_and_Physics "Computability in Analysis and Physics")*, [Springer-Verlag](https://en.wikipedia.org/wiki/Springer-Verlag "Springer-Verlag").
- [Stephen G. Simpson](https://en.wikipedia.org/wiki/Steve_Simpson_\(mathematician\) "Steve Simpson (mathematician)") (1999), *Subsystems of second-order arithmetic*.
- Klaus Weihrauch (2000), *Computable analysis*, Springer, [ISBN](https://en.wikipedia.org/wiki/ISBN_\(identifier\) "ISBN (identifier)") [3-540-66817-9](https://en.wikipedia.org/wiki/Special:BookSources/3-540-66817-9 "Special:BookSources/3-540-66817-9").

## External links

- [Computability and Complexity in Analysis Network](http://cca-net.de/)

[^1]: See Simpson, Alex K. (1998), Brim, Luboš; Gruska, Jozef; Zlatuška, Jiří (eds.), ["Lazy functional algorithms for exact real functionals"](http://link.springer.com/10.1007/BFb0055795), *Mathematical Foundations of Computer Science 1998*, Lecture Notes in Computer Science, vol. 1450, Berlin, Heidelberg: Springer Berlin Heidelberg, pp. 456–464, [doi](https://en.wikipedia.org/wiki/Doi_\(identifier\) "Doi (identifier)"):[10.1007/bfb0055795](https://doi.org/10.1007%2Fbfb0055795), [ISBN](https://en.wikipedia.org/wiki/ISBN_\(identifier\) "ISBN (identifier)") [978-3-540-64827-7](https://en.wikipedia.org/wiki/Special:BookSources/978-3-540-64827-7 "Special:BookSources/978-3-540-64827-7") `{{[citation](https://en.wikipedia.org/wiki/Template:Citation "Template:Citation")}}`: CS1 maint: work parameter with ISBN ([link](https://en.wikipedia.org/wiki/Category:CS1_maint:_work_parameter_with_ISBN "Category:CS1 maint: work parameter with ISBN"))

[^2]: An uncomputable real number can be generated with near certainty by sampling each digit at random in an infinite unending process.

[^3]: Bauer, Andrej. ["Kőnig's Lemma and Kleene Tree"](https://math.andrej.com/wp-content/uploads/2006/05/kleene-tree.pdf) (PDF).

[^4]: Bauer, Andrej. ["The Realizability Approach to Computable Analysis"](https://math.andrej.com/wp-content/uploads/2006/04/thesis.pdf) (PDF). *math.andrej.com*. Retrieved 2025-01-06.

[^5]: Weihrauch 2000, p. 6.

[^6]: Myhill, J. (1971). ["A recursive function, defined on a compact interval and having a continuous derivative that is not recursive"](https://doi.org/10.1307%2Fmmj%2F1029000631). *[Michigan Mathematical Journal](https://en.wikipedia.org/wiki/Michigan_Mathematical_Journal "Michigan Mathematical Journal")*. **18** (2). [doi](https://en.wikipedia.org/wiki/Doi_\(identifier\) "Doi (identifier)"):[10.1307/mmj/1029000631](https://doi.org/10.1307%2Fmmj%2F1029000631). [ISSN](https://en.wikipedia.org/wiki/ISSN_\(identifier\) "ISSN (identifier)") [0026-2285](https://search.worldcat.org/issn/0026-2285).

[^7]: ["abstract Stone duality in nLab"](https://ncatlab.org/nlab/show/abstract+Stone+duality). *ncatlab.org*. Retrieved 2023-07-29.