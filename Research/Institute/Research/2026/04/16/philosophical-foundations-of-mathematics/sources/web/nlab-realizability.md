## nLab realizability

Contents

## Contents

## Idea

The idea of *realizability* is a way of making the [Brouwer-Heyting-Kolmogorov interpretation](https://ncatlab.org/nlab/show/Brouwer-Heyting-Kolmogorov+interpretation) of [constructivism](https://ncatlab.org/nlab/show/constructivism) and [intuitionistic mathematics](https://ncatlab.org/nlab/show/intuitionistic+mathematics) precise. It is related to the [propositions as types](https://ncatlab.org/nlab/show/propositions+as+types) paradigm. For instance, constructively a [proof](https://ncatlab.org/nlab/show/proof) of an [existential quantification](https://ncatlab.org/nlab/show/existential+quantification) $\underset{x\in X}{\exists} \phi(x)$ consists of constructing a specific $x \in X$ and a proof of $\phi(x)$, which “realizes” the [truth](https://ncatlab.org/nlab/show/truth) of the statement, whence the name (see e.g. [Streicher 07, section 1](https://ncatlab.org/nlab/show/realizability#Streicher07), [Vermeeren 09, section 1](https://ncatlab.org/nlab/show/realizability#Vermeeren09) for introductions to the rough idea, or [Bauer 05, page 12 and def. 4.7](https://ncatlab.org/nlab/show/realizability#Bauer05) for an actual definition).

## Realizability of univalence in homotopy type theory

One possible way to find a computational interpretation for [univalence](https://ncatlab.org/nlab/show/univalence) in [homotopy type theory](https://ncatlab.org/nlab/show/homotopy+type+theory) is to interpret it in using realizability. Stekelburg provides a univalent universe of modest Kan complexes.

Simplicial homotopy theory can be developed in an [extensive](https://ncatlab.org/nlab/show/extensive) [locally cartesian closed](https://ncatlab.org/nlab/show/locally+cartesian+closed) category $A$. Such categories are also called Heyting bialgebras[?](https://ncatlab.org/nlab/new/Heyting+bialgebras). The category $A$ has a class of [small maps](https://ncatlab.org/nlab/show/small+maps) which has a bundle of small [assemblies](https://ncatlab.org/nlab/show/assemblies). This provides an internal Heyting bialgebra[?](https://ncatlab.org/nlab/new/Heyting+bialgebra) $S$ which we can use as a target for simplicial \`sets'. There is a (Kan-) model structure on these simplicial sets.

Within $S$ we can define a universe $M$ and show that it is fibrant. This universe is even univalent.

Now, the category of assemblies in number realizability provides such a Heyting bialgebra. The modest sets, a small internally complete full subcategory, provide the univalent universe. Note that modest sets are an [impredicative](https://ncatlab.org/nlab/show/impredicative) universe. It models the [calculus of constructions](https://ncatlab.org/nlab/show/calculus+of+constructions).

- [realizability topos](https://ncatlab.org/nlab/show/realizability+topos)
- [realizability model](https://ncatlab.org/nlab/show/realizability+model)
- [realizability interpretation](https://ncatlab.org/nlab/show/realizability+interpretation)
- [effective topos](https://ncatlab.org/nlab/show/effective+topos), [Kleene-Vesley topos](https://ncatlab.org/nlab/show/Kleene-Vesley+topos)
- [propositional axiom of choice](https://ncatlab.org/nlab/show/propositional+axiom+of+choice)
- [Lifschitz realizability](https://ncatlab.org/nlab/show/Lifschitz+realizability)

**[computability](https://ncatlab.org/nlab/show/computability)**

|  | type I computability | type II computability |
| --- | --- | --- |
| typical domain | [natural numbers](https://ncatlab.org/nlab/show/natural+numbers) $\mathbb{N}$ | [Baire space](https://ncatlab.org/nlab/show/Baire+space+%28computability%29) of infinite sequences $\mathbb{B} = \mathbb{N}^{\mathbb{N}}$ |
| [computable functions](https://ncatlab.org/nlab/show/computable+functions) | [partial recursive function](https://ncatlab.org/nlab/show/partial+recursive+function) | [computable function (analysis)](https://ncatlab.org/nlab/show/computable+function+%28analysis%29) |
| type of [computable mathematics](https://ncatlab.org/nlab/show/computable+mathematics) | [recursive mathematics](https://ncatlab.org/nlab/show/recursive+mathematics) | [computable analysis](https://ncatlab.org/nlab/show/computable+analysis), [Type Two Theory of Effectivity](https://ncatlab.org/nlab/show/Type+Two+Theory+of+Effectivity) |
| type of [realizability](https://ncatlab.org/nlab/show/realizability) | [number realizability](https://ncatlab.org/nlab/show/number+realizability) | [function realizability](https://ncatlab.org/nlab/show/function+realizability) |
| [partial combinatory algebra](https://ncatlab.org/nlab/show/partial+combinatory+algebra) | [Kleene's first partial combinatory algebra](https://ncatlab.org/nlab/show/Kleene%27s+first+partial+combinatory+algebra) | [Kleene's second partial combinatory algebra](https://ncatlab.org/nlab/show/Kleene%27s+second+partial+combinatory+algebra) |

## References

Realizability originates with the interpretation of [intuitionistic](https://ncatlab.org/nlab/show/intuitionistic+mathematics) [number theory](https://ncatlab.org/nlab/show/number+theory), later developed as *[Heyting arithmetic](https://ncatlab.org/nlab/show/Heyting+arithmetic)*, in

- [Stephen Kleene](https://ncatlab.org/nlab/show/Stephen+Kleene), *On the interpretation of intuitionistic number theory* Journal of Symbolic Logic, 10:109–124, 1945. [link](http://www.jstor.org/stable/2269016)

A historical survey of realizability (including [categorical realizability](https://ncatlab.org/nlab/show/realizability+topos)) is in

- [Jaap van Oosten](https://ncatlab.org/nlab/show/Jaap+van+Oosten), *Realizability: An Historical Essay*, 2000 ([link](http://www.staff.science.uu.nl/~ooste110/realizability/history.ps.gz), [pdf](https://pdfs.semanticscholar.org/0eb4/60525d1580fb9f184b43b974499bce2a2ea7.pdf))

A quick survey is in

- [Stijn Vermeeren](https://ncatlab.org/nlab/show/Stijn+Vermeeren), *Realizability Toposes*, 2009 ([pdf](http://stijnvermeeren.be/download/mathematics/essay.pdf))

being a summary of

- [Martin Hyland](https://ncatlab.org/nlab/show/Martin+Hyland), *The effective topos*, in The L.E.J. Brouwer Centenary
	Symposium (A. S. Toelstra and D. van Dalen, eds.), North-Holland Publishing Company, 1982, pp. 165–216

A modern textbook account is

- [Jaap van Oosten](https://ncatlab.org/nlab/show/Jaap+van+Oosten), *Realizability: an introduction to its categorical side*, Studies in Logic and the Foundations of Mathematics, vol. 152, Elsevier, 2008 ([preface pdf](http://www.staff.science.uu.nl/~ooste110/boekbegin.pdf))

Further discussion:

- [Andrej Bauer](https://ncatlab.org/nlab/show/Andrej+Bauer), *The Realizability Approach to*
	Computable Analysis and Topology\_, PhD thesis CMU (2000) ([pdf](http://andrej.com/thesis/thesis.pdf))
- Peter Lietz, *From Constructive Mathematics to Computable Analysis via the Realizability Interpretation*, PhD thesis (2004) \[[d-nb:974032735/34](https://d-nb.info/974032735/34)\]
- [Andrej Bauer](https://ncatlab.org/nlab/show/Andrej+Bauer), *Realizability as connection between constructive and computable mathematics* (based on [Bauer 2000](https://ncatlab.org/nlab/show/realizability#Bauer00)) in T. Grubba, P. Hertling, H. Tsuiki, and [Klaus Weihrauch](https://ncatlab.org/nlab/show/Klaus+Weihrauch), (eds.): *CCA 2005 - Second International Conference on Computability and Complexity in Analysis*, August 25-29,2005, Kyoto, Japan, ser. Informatik Berichte,, vol. 326-7/2005. FernUniversität Hagen, Germany, 2005, pp. 378&-379 \[[pdf](http://math.andrej.com/data/c2c.pdf)\]

Lecture notes:

- [Thomas Streicher](https://ncatlab.org/nlab/show/Thomas+Streicher), *Realizability* (2007/08) \[[pdf](http://www.mathematik.tu-darmstadt.de/~streicher/REAL/REAL.pdf)\]
- [Andrej Bauer](https://ncatlab.org/nlab/show/Andrej+Bauer): *Notes on Realizability*, Midlands Graduate School notes (2022, 2025) \[[pdf](https://github.com/andrejbauer/notes-on-realizability/releases/download/release/notes-on-realizability.pdf), [Github Repo](https://github.com/andrejbauer/notes-on-realizability)\]

On realizability of [univalent universes](https://ncatlab.org/nlab/show/univalent+universes):

- Wouter Stekelenburg, *Realizability of Univalence: Modest Kan complexes*, [arXiv](http://arxiv.org/abs/1406.6579)

See also:

- [Steven Awodey](https://ncatlab.org/nlab/show/Steven+Awodey), [Andrej Bauer](https://ncatlab.org/nlab/show/Andrej+Bauer), *Sheaf toposes for realizability* ([pdf](http://www.andrew.cmu.edu/user/awodey/preprints/stfr.pdf))
- Wouter Pieter Stekelenburg, *Realizability Categories*, PhD thesis, Utrecht 2013 ([arXiv:1301.2134](http://arxiv.org/abs/1301.2134))
- [Martin Hyland](https://ncatlab.org/nlab/show/Martin+Hyland), *Variations on realizability: realizing the propositional axiom of choice*, Mathematical Structures in Computer Science, Volume 12, Issue 3, June 2002, pp. 295 - 317 ([doi:10.1017/S0960129502003651](https://doi.org/10.1017/S0960129502003651), [pdf](https://www.dpmms.cam.ac.uk/~jmeh1/Research/Publications/2002/vor02.pdf))

Last revised on August 5, 2025 at 10:58:55. See the [history](https://ncatlab.org/nlab/history/realizability) of this page for a list of all contributions to it.