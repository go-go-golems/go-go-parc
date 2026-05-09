## nLab computability

Contents

## Contents

## Idea

*Computability theory* studies [mathematical](https://ncatlab.org/nlab/show/mathematics) entities that may be obtained by actual [computation](https://ncatlab.org/nlab/show/computation) (instead of by less concrete proofs of existence). As such computability theory is similar to *[constructive mathematics](https://ncatlab.org/nlab/show/constructive+mathematics)* and to *[realizability](https://ncatlab.org/nlab/show/realizability)*; indeed (emphasized e.g. in ([Bauer 05](https://ncatlab.org/nlab/show/computability#Bauer05))):

Computable mathematics is the [realizability](https://ncatlab.org/nlab/show/realizability) [interpretation](https://ncatlab.org/nlab/show/interpretation) of [constructive mathematics](https://ncatlab.org/nlab/show/constructive+mathematics).

Computability theory deals only with computability in principle and disregards the complexity of computation, that is instead the topic of *[complexity theory](https://ncatlab.org/nlab/show/complexity+theory)*.

The key concept in computability theory is that of a *[computable function](https://ncatlab.org/nlab/show/computable+function)*, hence of a [function](https://ncatlab.org/nlab/show/function) whose output may be determined from its input by an actual [computation](https://ncatlab.org/nlab/show/computation). There are two main types of computability, depending on whether one takes the domain and codomain of computable functions to be *finite string* from a finite alphabet, hence equivalently [natural numbers](https://ncatlab.org/nlab/show/natural+numbers), or *infinite strings* from a finite interval, hence sequence of natural numbers.

In the first case – “type I computability” – computable functions are [partial recursive functions](https://ncatlab.org/nlab/show/partial+recursive+functions). In the second – “type II computability” – they are [continuous functions](https://ncatlab.org/nlab/show/continuous+functions) on (quotients of) [Baire space](https://ncatlab.org/nlab/show/Baire+space+%28computability%29) (see at *[computable function (analysis)](https://ncatlab.org/nlab/show/computable+function+%28analysis%29)*).

**[computability](https://ncatlab.org/nlab/show/computability)**

|  | type I computability | type II computability |
| --- | --- | --- |
| typical domain | [natural numbers](https://ncatlab.org/nlab/show/natural+numbers) $\mathbb{N}$ | [Baire space](https://ncatlab.org/nlab/show/Baire+space+%28computability%29) of infinite sequences $\mathbb{B} = \mathbb{N}^{\mathbb{N}}$ |
| [computable functions](https://ncatlab.org/nlab/show/computable+functions) | [partial recursive function](https://ncatlab.org/nlab/show/partial+recursive+function) | [computable function (analysis)](https://ncatlab.org/nlab/show/computable+function+%28analysis%29) |
| type of [computable mathematics](https://ncatlab.org/nlab/show/computable+mathematics) | [recursive mathematics](https://ncatlab.org/nlab/show/recursive+mathematics) | [computable analysis](https://ncatlab.org/nlab/show/computable+analysis), [Type Two Theory of Effectivity](https://ncatlab.org/nlab/show/Type+Two+Theory+of+Effectivity) |
| type of [realizability](https://ncatlab.org/nlab/show/realizability) | [number realizability](https://ncatlab.org/nlab/show/number+realizability) | [function realizability](https://ncatlab.org/nlab/show/function+realizability) |
| [partial combinatory algebra](https://ncatlab.org/nlab/show/partial+combinatory+algebra) | [Kleene's first partial combinatory algebra](https://ncatlab.org/nlab/show/Kleene%27s+first+partial+combinatory+algebra) | [Kleene's second partial combinatory algebra](https://ncatlab.org/nlab/show/Kleene%27s+second+partial+combinatory+algebra) |

## Properties

### Relation to intuitionistic mathematics

Computable mathematics is an instance of [intuitionistic mathematics](https://ncatlab.org/nlab/show/intuitionistic+mathematics) (see e.g. ([Bauer 05, section 4.3.1](https://ncatlab.org/nlab/show/computability#Bauer05))).

- [synthetic computability theory](https://ncatlab.org/nlab/show/synthetic+computability+theory)
- [computation](https://ncatlab.org/nlab/show/computation), [hypercomputation](https://ncatlab.org/nlab/show/hypercomputation)
- [computable real number](https://ncatlab.org/nlab/show/computable+real+number)
- [computable set](https://ncatlab.org/nlab/show/computable+set)
- [equilogical space](https://ncatlab.org/nlab/show/equilogical+space)
- [halting theorem](https://ncatlab.org/nlab/show/halting+theorem)
- [persistent homology](https://ncatlab.org/nlab/show/persistent+homology)
- [computable physics](https://ncatlab.org/nlab/show/computable+physics)
- [descriptive set theory](https://ncatlab.org/nlab/show/descriptive+set+theory)

## References

Textbook containing the basic notions:

- [Michael Sipser](https://ncatlab.org/nlab/show/Michael+Sipser), *Introduction to the Theory of Computation*, Third edition (2012), Course Technology Inc.

The relation to [constructive mathematics](https://ncatlab.org/nlab/show/constructive+mathematics) and [realizability](https://ncatlab.org/nlab/show/realizability) is discussed in

- [Andrej Bauer](https://ncatlab.org/nlab/show/Andrej+Bauer), *Realizability as connection between constructive and computable mathematics*, in T. Grubba, P. Hertling, H. Tsuiki, and [Klaus Weihrauch](https://ncatlab.org/nlab/show/Klaus+Weihrauch), (eds.) *CCA 2005 - Second International Conference on Computability and Complexity in Analysis*, August 25-29,2005, Kyoto, Japan, ser. Informatik Berichte,, vol. 326-7/2005. FernUniversität Hagen, Germany, 2005, pp. 378–379. ([pdf](http://math.andrej.com/data/c2c.pdf))

based on

- [Andrej Bauer](https://ncatlab.org/nlab/show/Andrej+Bauer), *The Realizability Approach to*
	Computable Analysis and Topology\_, PhD thesis CMU (2000) ([pdf](http://math.andrej.com/wp-content/uploads/2006/04/thesis.pdf))
- Peter Lietz, *From Constructive Mathematics to Computable Analysis via the Realizability Interpretation* ([pdf](https://www2.mathematik.tu-darmstadt.de/~streicher/THESES/lietz.pdf))

For [computable analysis](https://ncatlab.org/nlab/show/computable+analysis) see

- [Klaus Weihrauch](https://ncatlab.org/nlab/show/Klaus+Weihrauch), *Computable Analysis* Berlin: Springer, 2000

Last revised on February 13, 2026 at 13:03:56. See the [history](https://ncatlab.org/nlab/history/computability) of this page for a list of all contributions to it.