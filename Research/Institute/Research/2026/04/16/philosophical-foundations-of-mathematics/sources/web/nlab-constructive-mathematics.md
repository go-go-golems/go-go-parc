## nLab constructive mathematics

Constructive mathematics

## Constructive mathematics

## Idea

Broadly speaking, **constructive mathematics** is [mathematics](https://ncatlab.org/nlab/show/mathematics) done without the [principle of excluded middle](https://ncatlab.org/nlab/show/principle+of+excluded+middle), or other principles, such as the full [axiom of choice](https://ncatlab.org/nlab/show/axiom+of+choice), that imply it, hence without “non-constructive” methods of [formal proof](https://ncatlab.org/nlab/show/formal+proof), such as [proof by contradiction](https://ncatlab.org/nlab/show/proof+by+contradiction). This is in contrast to *[classical mathematics](https://ncatlab.org/nlab/show/classical+mathematics)*, where such principles are taken to hold.

There are variations of what exactly is regarded as constructive mathematics, for instance [intuitionism](https://ncatlab.org/nlab/show/intuitionistic+mathematics) or [predicativism](https://ncatlab.org/nlab/show/predicative+mathematics), see the list of schools [below](https://ncatlab.org/nlab/show/constructive+mathematics#OriginsAndSchools). But beware the ambiguity in terminology: In [Brouwer](https://ncatlab.org/nlab/show/Brouwer) -style [intuitionistic mathematics](https://ncatlab.org/nlab/show/intuitionistic+mathematics) one includes [axioms](https://ncatlab.org/nlab/show/axioms) that *[contradict](https://ncatlab.org/nlab/show/contradiction)* [classical logic](https://ncatlab.org/nlab/show/classical+logic), while other authors use “intuitionistic” to mean what elsewhere is called “constructive”, and referring only to rejection of [excluded middle](https://ncatlab.org/nlab/show/excluded+middle) and [choice](https://ncatlab.org/nlab/show/axiom+of+choice). Some authors (particularly [material set theorists](https://ncatlab.org/nlab/show/material+set+theory)) use “constructive” to mean *[predicative](https://ncatlab.org/nlab/show/predicative)* constructive and “intuitionistic” to mean impredicative constructive. Other authors emphasize the necessity that constructive theories be [proof relevant](https://ncatlab.org/nlab/show/proof+relevance), with denial of the excluded middle’s universality subordinate to this requirement; see ([Harper 2013](https://ncatlab.org/nlab/show/constructive+mathematics#Harper13)).

**Constructivism** is the philosophy that such mathematics is useful, or (more strongly) that non-constructive mathematics is wrong. Historically, constructive mathematics was first pursued explicitly by mathematicians who believed the latter. However, many modern mathematicians who do constructive mathematics do it not because of any philosophical belief about the wrongness of non-constructive mathematics, but because constructive mathematics is interesting in its own right. In the ‘ [pluralist](http://citeseerx.ist.psu.edu/viewdoc/summary?doi=10.1.1.93.9892) ’ approach to the [foundations](https://ncatlab.org/nlab/show/foundations) of mathematics, a constructive proof (when it exists) is better because it is valid in more versions of mathematics, but a classical proof remains valid for [classical mathematics](https://ncatlab.org/nlab/show/classical+mathematics).

Another motivation for modern mathematicians —especially category theorists like those on the nLab— is that the study of constructive mathematics has potential applications to non-constructive mathematics. For example, even if one believes the principle of excluded middle to be true, the “ [internal](https://ncatlab.org/nlab/show/internal+logic) ” version of excluded middle in many interesting [categories](https://ncatlab.org/nlab/show/category) is still false; thus constructive mathematics can be useful in the study of such categories, even if mathematics is “globally” non-constructive. This is the neutral motivation for constructive mathematics from the [nPOV](https://ncatlab.org/nlab/show/nPOV#Logic).

Here we write mostly about the mathematics, trying to be mostly neutral philosophically.

## Origins and schools

During the “ [foundational](https://ncatlab.org/nlab/show/foundations) crisis” in mathematics around the beginning of the 20th century, a number of mathematicians espoused philosophies that are generally grouped together and labeled **constructivist**. The common feature of these philosophies was a rejection of axioms and principles of logic that lead to nonconstructive proofs. There was much talk at the time about potential vs absolute infinity, but from an axiomatic perspective, it turns out that (if one stops short of finitism) the two main culprits are

- the [axiom of choice](https://ncatlab.org/nlab/show/axiom+of+choice) and
- the principle of [excluded middle](https://ncatlab.org/nlab/show/excluded+middle).

Thus, constructivists (including many still active today) reject proofs that make use of either of these. (In fact, it was realized in 1975 by Diaconescu that the axiom of choice implies the principle of excluded middle. Excluded middle is precisely the “finitely indexed” axiom of choice; see [excluded middle](https://ncatlab.org/nlab/show/excluded+middle) for a proof.)

There are, however, differences among constructivists as well, even discounting the pluralists.

- Some, like [Fred Richman](https://ncatlab.org/nlab/show/Fred+Richman) (see (Richman 2000)), simply remove choice and excluded middle from [classical mathematics](https://ncatlab.org/nlab/show/classical+mathematics) with nothing to replace them. This is called [neutral constructive mathematics](https://ncatlab.org/nlab/show/neutral+constructive+mathematics). However, this makes it difficult to define a satisfactory notion of [continuous function](https://ncatlab.org/nlab/show/continuous+function), even from the [real line](https://ncatlab.org/nlab/show/real+line) to itself, without using [locales](https://ncatlab.org/nlab/show/locales); see (Waaldijk 2003).
- Others accept weaker versions of choice, such as [countable choice](https://ncatlab.org/nlab/show/countable+choice) or even [dependent choice](https://ncatlab.org/nlab/show/dependent+choice). [Toby Bartels](https://ncatlab.org/nlab/show/Toby+Bartels) argues that the intuition behind accepting these justifies the (yet stronger) [presentation axiom](https://ncatlab.org/nlab/show/presentation+axiom) (that [the category of sets](https://ncatlab.org/nlab/show/the+category+of+sets) has [enough projectives](https://ncatlab.org/nlab/show/enough+projectives)).
- Others add “non-classical” axioms which contradict choice or excluded middle, but which are consistent in their absence, such as “all total functions $[0,1] \to \mathbb{R}$ are continuous” (the [continuity axiom](https://ncatlab.org/nlab/show/continuity+axiom) of the “ [intuitionistic](https://ncatlab.org/nlab/show/intuitionism) ” school of [L. E. J. Brouwer](https://ncatlab.org/nlab/show/L.+E.+J.+Brouwer)) or “all partial functions $\mathbb{N} \to \mathbb{N}$ are computable” (the computability axiom[?](https://ncatlab.org/nlab/new/computability+axiom) of the “ [Russian](https://ncatlab.org/nlab/show/Russian+constructivism) ” school of [A. A. Markov](https://ncatlab.org/nlab/show/Andrey+Markov+Jr), which is also called “constructive recursive analysis”).
- [Errett Bishop](https://ncatlab.org/nlab/show/Errett+Bishop) had his own branch of constructive mathematics, known as [Bishop's constructive mathematics](https://ncatlab.org/nlab/show/Bishop%27s+constructive+mathematics) or [BISH](https://ncatlab.org/nlab/show/BISH), where [equality](https://ncatlab.org/nlab/show/equality) and [sets](https://ncatlab.org/nlab/show/sets) are defined notion rather than a primitive on [sets](https://ncatlab.org/nlab/show/sets).
- Still others, following [Hermann Weyl](https://ncatlab.org/nlab/show/Hermann+Weyl), go even further and refuse to allow “impredicative” constructions; see [predicative mathematics](https://ncatlab.org/nlab/show/predicative+mathematics). Most of the work done by the schools of Brouwer, Bishop, and Markov (but not Richman) is also predicative, even though those founders were not adamant about it; as a result, predicativism often appears in the [foundations](https://ncatlab.org/nlab/show/foundations) of constructive mathematics (in particular, in those of [Aczel](https://ncatlab.org/nlab/show/Peter+Aczel) and [Martin-Löf](https://ncatlab.org/nlab/show/Per+Martin-L%C3%B6f), but not those of [Friedman](https://ncatlab.org/nlab/show/Harvey+Friedman) or [Coquand](https://ncatlab.org/nlab/show/Thierry+Coquand)).
- An extreme form of constructive [predicative mathematics](https://ncatlab.org/nlab/show/predicative+mathematics) is to reject the use of [implication](https://ncatlab.org/nlab/show/implication) and the [universal quantifier](https://ncatlab.org/nlab/show/universal+quantifier) completely and work in [coherent logic](https://ncatlab.org/nlab/show/coherent+logic), resulting in [coherent mathematics](https://ncatlab.org/nlab/show/coherent+mathematics). Excluded middle and double negation cannot be formed, since negation can only be formed as a [sequent](https://ncatlab.org/nlab/show/sequent) rather than a [formula](https://ncatlab.org/nlab/show/formula) in the [coherent logic](https://ncatlab.org/nlab/show/coherent+logic). Examples of [coherent mathematics](https://ncatlab.org/nlab/show/coherent+mathematics) include [dependent type theory](https://ncatlab.org/nlab/show/dependent+type+theory) which does not make use of [function types](https://ncatlab.org/nlab/show/function+types) and [dependent function types](https://ncatlab.org/nlab/show/dependent+function+types), as well as mathematics done inside an [arithmetic pretopos](https://ncatlab.org/nlab/show/arithmetic+pretopos).
- One also has [geometric mathematics](https://ncatlab.org/nlab/show/geometric+mathematics), which is coherent mathematics with all [colimits](https://ncatlab.org/nlab/show/colimits) but no [function sets](https://ncatlab.org/nlab/show/function+sets).
- Very extreme constructivists, like [Doron Zeilberger](https://ncatlab.org/nlab/show/Doron+Zeilberger), reject the existence of infinite sets; see [finitism](https://ncatlab.org/nlab/show/finitism). (Kronecker, the ‘father of constructivism’, is often considered a finitist, but as he came before the foundational crisis, it is difficult to classify him accurately.) Ironically, this means that excluded middle and choice, in their naïve forms, may become acceptable, or even true. (Even constructivists believe that they are true [in](https://ncatlab.org/nlab/show/internal+logic) the category [FinSet](https://ncatlab.org/nlab/show/FinSet) of [finite sets](https://ncatlab.org/nlab/show/finite+sets).)
- The most extreme position of all is to deny even the existence of very large finite sets. This is called [ultrafinitism](https://ncatlab.org/nlab/show/ultrafinitism). This has been studied largely by Alexander Yesenin-Volpin[?](https://ncatlab.org/nlab/new/Alexander+Yesenin-Volpin) and (more recently) [Edward Nelson](https://ncatlab.org/nlab/show/Edward+Nelson); foundational systems such as [soft linear logic](https://ncatlab.org/nlab/show/soft+linear+logic) can also be argued to have an ultrafinitist flavor. Zeilberger also claims sympathy with ultrafinitist philosophy, although his actual work fits well into a (merely) finitist framework.

Many constructivists (like many classical mathematicians) believe in an absolute mathematical sense of “truth,” and that in this sense choice and excluded middle are simply *wrong*. (Some constructivists, using classically false axioms, can even refute them; others merely claim that no possible correct reasoning could ever prove them. See [Truth versus assertability](https://ncatlab.org/nlab/show/constructive+mathematics#truevassert) below.) To most mathematicians, this makes them seem quite strange. Other constructivists adopt a wait-and-see attitude, or even a relative notion of truth (which can seem strange in another way).

The following is a partial list of schools and subtheories of constructive mathematics:

- [neutral constructive mathematics](https://ncatlab.org/nlab/show/neutral+constructive+mathematics)
- Brouwer’s [intuitionistic mathematics](https://ncatlab.org/nlab/show/intuitionistic+mathematics)
- [Russian constructivism](https://ncatlab.org/nlab/show/Russian+constructivism)
- [Bishop's constructive mathematics](https://ncatlab.org/nlab/show/Bishop%27s+constructive+mathematics)
- [constructive reverse mathematics](https://ncatlab.org/nlab/show/constructive+reverse+mathematics)
- (at least related) [explicit mathematics](https://ncatlab.org/nlab/show/explicit+mathematics)

## Topos theory

With the invention of [topos theory](https://ncatlab.org/nlab/show/topos) in the second half of the 20th century, a new sort of constructivism arose. It was observed (by [Lawvere](https://ncatlab.org/nlab/show/Bill+Lawvere) and others) that any topos with a [natural numbers object](https://ncatlab.org/nlab/show/natural+numbers+object) has an [internal logic](https://ncatlab.org/nlab/show/internal+logic) which is powerful enough to interpret most of mathematics, but that this logic in general fails to satisfy choice and excluded middle. This meant that even for a mathematican who likes to use choice and excluded middle (and *a fortiori* for one who believes them to be “true”), there is a reason to care about what can be proven without them, because only if a proof is constructive can it be interpreted in an arbitrary topos with NNO.

Even starting from a “completely classical” world of mathematics, many interesting toposes arise naturally (such as the category of [sheaves](https://ncatlab.org/nlab/show/sheaf) on any [topological space](https://ncatlab.org/nlab/show/topological+space), or more generally any [site](https://ncatlab.org/nlab/show/site)) whose internal logic is not [classical logic](https://ncatlab.org/nlab/show/classical+logic). Then by internal reasoning in such a topos (which is constructive reasoning), one can prove various useful facts, which can then be reinterpreted as external statements about the behavior of the topos itself. For example, the constructive theorem that every [one-sided real number](https://ncatlab.org/nlab/show/one-sided+real+number) that is both a lower real and an upper real must be located (which, classically, is an utter triviality) becomes the theorem that any [semicontinuous function](https://ncatlab.org/nlab/show/semicontinuous+function) (from any [topological space](https://ncatlab.org/nlab/show/topological+space) to the [real line](https://ncatlab.org/nlab/show/real+line)) that is both upper and lower semicontinuous must be [continuous](https://ncatlab.org/nlab/show/continuous+map) (which is at least somewhat nontrivial).

By now it is known that many of the non-classical axioms used by the early constructivists have natural models in particular toposes. For instance, in the topos of sheaves on the real numbers $R$, the [continuity axiom](https://ncatlab.org/nlab/show/continuity+axiom) that “all total functions $R \to R$ are continuous” holds. And in the [effective topos](https://ncatlab.org/nlab/show/effective+topos), the computability axiom[?](https://ncatlab.org/nlab/new/computability+axiom) that “all partial functions $N\to N$ are computable” holds.

However, there are no non-classical (or classical) axioms beyond “pure constructivism” that are true in *all* toposes with NNO. In particular, there is a [free topos](https://ncatlab.org/nlab/show/free+topos) with NNO such that a statement is true in the free topos precisely when it is provable in pure (Richman-school) constructive mathematics. This means that for an argument to apply in all toposes, even mild assumptions such as countable or dependent choice are unacceptable (but impredicativity is fine). However, topos theory has also provided ideas that solve many of the problems with pure constructivism. For example, a well-behaved notion of “continuous function” can be recovered by using [locales](https://ncatlab.org/nlab/show/locale) instead of topological spaces, which was first discovered in the context of toposes and is closely related to them in any case.

## Some features of constructive mathematics

### Rephrasing of classical ideas

Sometimes, all that is necessary to make a piece of mathematics constructive is careful use of language. It is common in [classical mathematics](https://ncatlab.org/nlab/show/classical+mathematics) to define things with an unnecessary amount of [negation](https://ncatlab.org/nlab/show/negation). This doesn’t work so well constructively, since a statement can be not false without being true, but we can sometimes do perfectly well by just removing unnecessary [double negations](https://ncatlab.org/nlab/show/double+negations).

For example, classically one often speaks about “nonempty” sets, meaning a set which “does *not* have *no* elements.” Constructively it is much better to say that a set “ *does* have at least one element”; constructivists often call such a set *[inhabited](https://ncatlab.org/nlab/show/inhabited+set)* to remind themselves that it is a “positive” notion to replace the negative one of “nonempty”. Others continue to use the word “non-empty” but understand it as a term of art that really means “inhabited”.

### Bifurcation of notions

On the other hand, differences in axiomatization or definition that make no difference classically can result in actual differences in behavior constructively. Therefore, classically equivalent notions often “bifurcate” (or “trifurcate” or worse) into multiple inequivalent constructive ones. This tends to happen whenever a concept involves *[negation](https://ncatlab.org/nlab/show/negation)* and, to a lesser degree, *[disjunction](https://ncatlab.org/nlab/show/disjunction)* and *[existential quantification](https://ncatlab.org/nlab/show/existential+quantification)*. In some cases there is a “correct” constructive version of the definition, although it may take some thought to uncover it, but in many cases more than one of the resulting concepts is important and useful. For example:

- There are multiple inequivalent notions of a [set](https://ncatlab.org/nlab/show/set), because [denial inequality](https://ncatlab.org/nlab/show/denial+inequality) does not have the same properties in constructive mathematics that it does in [classical mathematics](https://ncatlab.org/nlab/show/classical+mathematics). These include objects such as sets with [stable equality](https://ncatlab.org/nlab/show/stable+equality), sets with [decidable equality](https://ncatlab.org/nlab/show/decidable+equality), sets with [tight apartness relations](https://ncatlab.org/nlab/show/tight+apartness+relations), and finally [classical sets](https://ncatlab.org/nlab/show/classical+sets), the last of which are precisely the sets in constructive mathematics whose denial inequality has all the same properties as it does in classical mathematics.
- There are multiple inequivalent constructive definitions of a [field](https://ncatlab.org/nlab/show/field), because of the axioms “every *nonzero* element has an inverse” and $0 \neq 1$.
- More generally, the [antithesis interpretation](https://ncatlab.org/nlab/show/antithesis+interpretation) of constructive mathematics leads to a generalised notion of [negation](https://ncatlab.org/nlab/show/negation) as two [mutually exclusive propositions](https://ncatlab.org/nlab/show/mutually+exclusive+propositions). This results in the bifurcation of basic mathematical objects, such as [set](https://ncatlab.org/nlab/show/set) ( [$\mathcal{A}$ \-set](https://ncatlab.org/nlab/show/A-set)), [monoid](https://ncatlab.org/nlab/show/monoid) ( [$\mathcal{A}$ \-monoid](https://ncatlab.org/nlab/show/A-monoid)), [group](https://ncatlab.org/nlab/show/group) ( [$\mathcal{A}$ \-group](https://ncatlab.org/nlab/show/A-group)), [ring](https://ncatlab.org/nlab/show/ring) ( [$\mathcal{A}$ \-ring](https://ncatlab.org/nlab/show/A-ring)), and [partial order](https://ncatlab.org/nlab/show/partial+order) ( [$\mathcal{A}$ \-partial order](https://ncatlab.org/nlab/show/antithesis+partial+order)) into at least five concepts each, depending on the relation between the pointwise mutually exclusive relations and their intuitionistic [denial negation](https://ncatlab.org/nlab/show/denial+negation).
- There are multiple inequivalent definitions of [real numbers](https://ncatlab.org/nlab/show/real+numbers).
	- the [Dedekind real numbers](https://ncatlab.org/nlab/show/Dedekind+real+numbers) and the [Cauchy real numbers](https://ncatlab.org/nlab/show/Cauchy+real+numbers) need no longer coincide. The Cauchy reals sit inside the Dedekind reals, but in general not every Dedekind real need be approximable by a *[sequence](https://ncatlab.org/nlab/show/sequence)* of rationals. From a topos-theoretic viewpoint, the Dedekind reals are usually the “correct” notion to study (if not the [locale of real numbers](https://ncatlab.org/nlab/show/locale+of+real+numbers) as a whole). However, the weak [limited principle of omniscience](https://ncatlab.org/nlab/show/limited+principle+of+omniscience) suffices to ensure that every Dedekind real is a Cauchy real, and hence that the two notions coincide; see ([Univalent Foundations Project](https://ncatlab.org/nlab/show/Univalent+Foundations+Project) 2013) and (Booij 2020). Weak countable choice implies the weak limited principle of omniscience, which in turn is implied by excluded middle and the axiom of choice; see (Bridges et al. 1993).
		- Similarly, the [Cauchy real numbers](https://ncatlab.org/nlab/show/Cauchy+real+numbers) are not sequentially [Cauchy complete](https://ncatlab.org/nlab/show/Cauchy+complete). There is an intermediate set of [real numbers](https://ncatlab.org/nlab/show/real+numbers) between the Cauchy reals and the Dedekind reals that are sequentially Cauchy complete called the [HoTT book real numbers](https://ncatlab.org/nlab/show/HoTT+book+real+numbers), such that there are embeddings from the Cauchy reals to the HoTT reals, and from the HoTT reals to the Dedekind reals, but there are no embeddings in the reverse direction.
		- The lower, upper, and two-sided [Dedekind real numbers](https://ncatlab.org/nlab/show/Dedekind+real+numbers) do not coincide with each other. That they do coincide is equivalent to [excluded middle](https://ncatlab.org/nlab/show/excluded+middle), as shown [here](https://categorytheory.zulipchat.com/#narrow/stream/229136-theory.3A-category-theory/topic/One.20universe.20as.20a.20foundation.20.26.20friends/near/465219817) by [James Hanson](https://ncatlab.org/nlab/show/James+Hanson).
		- A real number with a [locator](https://ncatlab.org/nlab/show/locator) is equivalent to a real number represented by a [Cauchy sequence](https://ncatlab.org/nlab/show/Cauchy+sequence) with [modulus of convergence](https://ncatlab.org/nlab/show/modulus+of+convergence), which implies that it is [sequentially complete](https://ncatlab.org/nlab/show/sequentially+complete). That every [modulated Cauchy real number](https://ncatlab.org/nlab/show/modulated+Cauchy+real+number) has a [locator](https://ncatlab.org/nlab/show/locator) or is a [Cauchy sequence](https://ncatlab.org/nlab/show/Cauchy+sequence) with [modulus of convergence](https://ncatlab.org/nlab/show/modulus+of+convergence) implies that the Cauchy real numbers coincide with the HoTT real numbers.
		- That every real number with a locator in the [unit interval](https://ncatlab.org/nlab/show/unit+interval) can be represented by a [sequence](https://ncatlab.org/nlab/show/sequence) of (positive) digits (i.e. [radix notation](https://ncatlab.org/nlab/show/radix+notation)) is equivalent to the lesser [limited principle of omniscience](https://ncatlab.org/nlab/show/limited+principle+of+omniscience), so it is no longer true that every such real number has an infinite decimal representation.
- There are at least three different constructive notions of [ordinal number](https://ncatlab.org/nlab/show/ordinal+number); see (Taylor 1996) and (Joyal–Moerdijk 1995).
- Without the axiom of choice, [functors](https://ncatlab.org/nlab/show/functor) and [anafunctors](https://ncatlab.org/nlab/show/anafunctor) become distinct, and often the latter is more appropriate; see (Makkai, 1996).
- Perhaps most disturbingly of all to the classical mathematician, one must distinguish between *finite sets*, *subfinite sets*, *finitely-indexed sets*, and even *subfinitely indexed sets*; see [finite set](https://ncatlab.org/nlab/show/finite+set) for definitions. However, in practice it is usually either finite or finitely-indexed sets that are important, and with practice a little bit of thought suffices to show which is the relevant concept.

### Negative translation

This allows one to translate classically valid theorems into intuitionistically valid theorems. See [double negation translation](https://ncatlab.org/nlab/show/double+negation+translation).

### Truth versus assertability

Already in [classical mathematics](https://ncatlab.org/nlab/show/classical+mathematics), there is a difference between saying that something is true and saying that something is [provable](https://ncatlab.org/nlab/show/proof). If you adopt [ZFC](https://ncatlab.org/nlab/show/ZFC) because you believe it correct, then presumably you believe that ZFC is consistent even though (assuming that you're aware of certain theorems) you also know that you cannot prove it so. In that case, you also believe that the [continuum hypothesis](https://ncatlab.org/nlab/show/continuum+hypothesis) (for example) is either true or false; you may or may not have an opinion on which it is, but in any case again you know that you cannot prove it either way.

A constructive mathematician can be even subtler. If you belong to the Bishop school, then you accept no classically false axioms, and anything that you can prove is valid also in classical mathematics. Even so, you can believe that the principle of excluded middle is false (even though, of course, you know that you cannot prove it false). So you can really confuse the classical mathematicians by saying, on the one hand, that they can safely accept all of your theorems as valid, and then saying, on the other hand, that you know excluded middle to be false. The resolution, of course, is that you never claimed that this was a *theorem*.

This way of talking has even been formalised in (Bishop, 1967) with a convention adopted by many (but not all) of his followers. In this convention, the word ‘not’, used normally in a vernacular sentence whose mathematical content would otherwise be the proposition $p$, changes to the content to $\neg p$, or $p \to \bot$, as usual. (This follows all of the rules of [intuitionistic logic](https://ncatlab.org/nlab/show/intuitionistic+logic); in particular, any statement that is ‘not’ true is false (just as in [classical logic](https://ncatlab.org/nlab/show/classical+logic)).) However, the word ‘ *not* ’, in italics as shown here, changes the content to $p \to x$, where $x$ is some statement that is known (although not proved!), according to Bishop, to be false. Now a statement that is ‘ *not* ’ true may be false, but this may be unknown, and it is even possible that it is also ‘ *not* ’ false (so $\neg p \to x$, possibly for a different $x$).

Bishop gives in his introduction several statements, suitable for use as $x$ above, including:

- excluded middle itself, which Bishop call the ‘principle of omniscience’;
- the ‘ [limited principle of omniscience](https://ncatlab.org/nlab/show/limited+principle+of+omniscience) ’: any infinite sequence in $\{0,1\}^N$ is either all $0$ or has at least one $1$;
- the ‘ [lesser limited principle of omniscience](https://ncatlab.org/nlab/show/lesser+limited+principle+of+omniscience) ’: for any two infinite sequence in $\{0,1\}^N$ that do not both have at least one $1$, at least one of these sequences does not have at least one $1$;
- others.

At one point in his book, while discussing the possibility of a pointwise-continuous function $[0,1] \to R$ that is not uniformly continuous (a Specker function[?](https://ncatlab.org/nlab/new/Specker+function), whose existence Markov's school claims as a theorem), Bishop seems to assert that this theorem is both *not* true and *not* false; he does not put it this way, so this may not be exactly what he meant, but there is no contradiction if it is. (But it *is* a contradiction, even in intuitionistic logic, if a statment is both not true and not false; indeed, a definition of ‘false’ may be taken to be ‘not true’.)

This practice can be understood through a careful distinction between [object language](https://ncatlab.org/nlab/show/object+language) and [metalanguage](https://ncatlab.org/nlab/show/metalanguage). A mathematical statement $p$ (such as the continuum hypothesis, or that a Specker function exists) belongs to the object language, as does $\neg p$ or $p \to x$ for any specific mathematical statement $x$. But the statement that $p$ is provable in some formal system belongs to the metalanguage (although it can also phrased internal to any object language suitable for mathematics), and as such may be written $\vdash p$. The metalanguage has its own logic (the metalogic, which for the sake of argument we may even assume to be classical), but notice that $\neg \vdash p$ and $\vdash \neg p$ are different; the first claims that $p$ cannot be proved, while the second claims that $p$ can be refuted, which (in any consistent[?](https://ncatlab.org/nlab/new/consistent+logic) formal system, even a classical one) is strictly stronger. Although Bishop did not commit to any formal system, if we assume for the sake of argument that he settled on one, then we may write $\vdash \neg p$ as our interpretation of his meaning when he asserts ‘not $p$ ’ but $\neg \vdash p$ as his meaning when he asserts ‘ *not* $p$ ’.

Even without the notational convention of the Bishop school, it is important when reading constructive mathematics to remember the difference between what can be refuted (proved false) and what merely cannot be proved true. Although Brouwer's and Markov's schools will sometimes claim to prove statements that are (classically) outright false (such as that every function $[0,1] \to R$ is pointwise-continuous), it is more common (and can happen in any school) that a constructive mathematician makes a claim that merely *sounds* false, when what they really mean is only that they don't accept what you say as true. Often modal phrases like ‘not necessarily’ will be used where Bishop would use ‘ *not* ’, as a clue that we're shifting to a metalanguage, or at least merely remaining agnostic rather than outright disagreeing.

The distinction between object language and metalanguage exists even in [classical mathematics](https://ncatlab.org/nlab/show/classical+mathematics), but it seems that most classical mathematicians are not used to remembering it, although it is not entirely clear why this should be so. One possibly relevant observation is that even if $P$ is a statement which is neither provable nor disprovable (like the continuum hypothesis), in classical mathematics it is still provable that “ $P$ is either true or false.” Moreover, classical [model theory](https://ncatlab.org/nlab/show/model+theory) often restricts itself to two-valued models[?](https://ncatlab.org/nlab/new/two-valued+model) in which the only truth values are “true” and “false,” although classical logic still holds in [Boolean-valued](https://ncatlab.org/nlab/show/Boolean+algebra) models, and in such a case the truth value of $P$ may be neither “true” nor “false,” although the truth value of “ $P$ or not $P$ ” is still “true.” Certainly when talking about classical truths which fail constructively, such as excluded middle, it is important to remember that “fails to be provable” is different from “is provably false.”

## Prehistory

In

- [Georg Hegel](https://ncatlab.org/nlab/show/Georg+Hegel), *[Phenomenology of Spirit](https://ncatlab.org/nlab/show/Phenomenology+of+Spirit)* (1807)

the following comment about mathematical proof (in section *[12 Historical and mathematical proof](https://www.marxists.org/reference/archive/hegel/works/ph/phprefac.htm#12)* of the Preface) might be read as being a complaint about the traditional non-constructive concept of proof and about the traditional lack of [proof relevance](https://ncatlab.org/nlab/show/proof+relevance):

> All the same, while proof is essential in the case of mathematical knowledge, it still does not have the significance and nature of being a moment in the result itself; the proof is over when we get the result, and has disappeared. The process of mathematical proof does not belong to the object; it is a function that takes place outside the matter in hand.
> 
> [footnote 42](https://www.marxists.org/reference/archive/hegel/help/finpref.htm#m042): Mathematical truths are not thought to be known unless proved true. Their demonstrations are not, however, kept as parts of what they prove, but are only our subjective means towards knowing the latter. In philosophy, however, consequences always form part of the essence made manifest in them, which returns to itself in such expressions.

See also earlier conceptions of proofs expressing the ‘cause’ of a theorem, where *reductio* proofs in particular were taken generally to fail. Such an idea goes back to Aristotle for whom a proper answer to the question “Why is the angle in a semicircle a right-angle?” gives its cause.

- Paolo Mancosu, *Philosophy of Mathematics and Mathematical Practice in the Seventeenth Century*, OUP, 1996.

See also

- [intuitionistic mathematics](https://ncatlab.org/nlab/show/intuitionistic+mathematics)
- [realizability](https://ncatlab.org/nlab/show/realizability)
- [computability](https://ncatlab.org/nlab/show/computability)
- [constructive set theory](https://ncatlab.org/nlab/show/constructive+set+theory)
- [constructive analysis](https://ncatlab.org/nlab/show/constructive+analysis)
- [constructive algebraic topology](https://ncatlab.org/nlab/show/constructive+algebraic+topology)
- [taboo](https://ncatlab.org/nlab/show/taboo)

Concepts that usually arise in constructive mathematics, often because they are classically trivial:

- [proof relevance](https://ncatlab.org/nlab/show/proof+relevance)
- [anafunctor](https://ncatlab.org/nlab/show/anafunctor) (classically equivalent to a [functor](https://ncatlab.org/nlab/show/functor))
- [apartness relation](https://ncatlab.org/nlab/show/apartness+relation) (classically complementary to an [equivalence relation](https://ncatlab.org/nlab/show/equivalence+relation))
- [comparison](https://ncatlab.org/nlab/show/comparison) (classically complementary to a [transitive relation](https://ncatlab.org/nlab/show/transitive+relation))
- [decidable equality](https://ncatlab.org/nlab/show/decidable+equality) (classically trivial)
- [decidable subset](https://ncatlab.org/nlab/show/decidable+subset) (classically trivial)
- [inhabited set](https://ncatlab.org/nlab/show/inhabited+set) (classically equivalent to a non- [empty set](https://ncatlab.org/nlab/show/empty+set))
- [pseudo-order](https://ncatlab.org/nlab/show/pseudo-order) (classically complementary to a [total order](https://ncatlab.org/nlab/show/total+order))
- [locale](https://ncatlab.org/nlab/show/locale) (classically similar to but not equivalent to a [topological space](https://ncatlab.org/nlab/show/topological+space))
- [connected irreflexive comparison](https://ncatlab.org/nlab/show/connected+irreflexive+comparison) (classically complementary to a [partial order](https://ncatlab.org/nlab/show/partial+order))
- [subsingleton](https://ncatlab.org/nlab/show/subsingleton) (classically equivalent to the empty set or a [singleton](https://ncatlab.org/nlab/show/singleton))
- [Heyting field](https://ncatlab.org/nlab/show/Heyting+field), [weak Heyting field](https://ncatlab.org/nlab/show/weak+Heyting+field), [discrete field](https://ncatlab.org/nlab/show/discrete+field) (classically all equivalent to a [field](https://ncatlab.org/nlab/show/field))
- [weak local ring](https://ncatlab.org/nlab/show/weak+local+ring), [local ring](https://ncatlab.org/nlab/show/local+ring), [residually discrete local ring](https://ncatlab.org/nlab/show/residually+discrete+local+ring) (classically equivalent to a [local ring](https://ncatlab.org/nlab/show/local+ring))
- [Cantor real numbers](https://ncatlab.org/nlab/show/Cantor+real+numbers), [HoTT book real numbers](https://ncatlab.org/nlab/show/HoTT+book+real+numbers), [Dedekind real numbers](https://ncatlab.org/nlab/show/Dedekind+real+numbers) (classically all equivalent as the [real numbers](https://ncatlab.org/nlab/show/real+numbers))

Some of these are also useful internally or even classically.

Topics relevant to the foundations of constructive mathematics:

- [axiom of choice](https://ncatlab.org/nlab/show/axiom+of+choice)
- [Bishop set](https://ncatlab.org/nlab/show/Bishop+set)
- [centipede mathematics](https://ncatlab.org/nlab/show/centipede+mathematics)
- [choice object](https://ncatlab.org/nlab/show/choice+object)
- [COSHEP](https://ncatlab.org/nlab/show/COSHEP)
- [excluded middle](https://ncatlab.org/nlab/show/excluded+middle)
- [finite mathematics](https://ncatlab.org/nlab/show/finite+mathematics)
- [internalization](https://ncatlab.org/nlab/show/internalization)
- [internal logic](https://ncatlab.org/nlab/show/internal+logic)
- [intuitionistic logic](https://ncatlab.org/nlab/show/intuitionistic+logic)
- [Markov's principle](https://ncatlab.org/nlab/show/Markov%27s+principle)
- [power set](https://ncatlab.org/nlab/show/power+set)
- [predicative mathematics](https://ncatlab.org/nlab/show/predicative+mathematics)
- [pretopos](https://ncatlab.org/nlab/show/pretopos)
- [set theory](https://ncatlab.org/nlab/show/set+theory)
- [topos](https://ncatlab.org/nlab/show/topos)
- [truth value](https://ncatlab.org/nlab/show/truth+value)
- [type theory](https://ncatlab.org/nlab/show/type+theory)
	- [intuitionistic type theory](https://ncatlab.org/nlab/show/intuitionistic+type+theory)
		- [homotopy type theory](https://ncatlab.org/nlab/show/homotopy+type+theory)

Other articles with content relating to constructive mathematics (rather incomplete):

- [axiom of foundation](https://ncatlab.org/nlab/show/axiom+of+foundation)
- [biproduct](https://ncatlab.org/nlab/show/biproduct)
- [Cantor's theorem](https://ncatlab.org/nlab/show/Cantor%27s+theorem)
- [cardinal number](https://ncatlab.org/nlab/show/cardinal+number)
- [complement](https://ncatlab.org/nlab/show/complement)
- [complete lattice](https://ncatlab.org/nlab/show/complete+lattice)
- [countable set](https://ncatlab.org/nlab/show/countable+set)
- [cyclic order](https://ncatlab.org/nlab/show/cyclic+order)
- [direct sum](https://ncatlab.org/nlab/show/direct+sum)
- [extended natural number system](https://ncatlab.org/nlab/show/extended+natural+number+system)
- [field](https://ncatlab.org/nlab/show/field)
- [filter](https://ncatlab.org/nlab/show/filter)
- [finite set](https://ncatlab.org/nlab/show/finite+set)
- [Grothendieck topos](https://ncatlab.org/nlab/show/Grothendieck+topos)
- [Hausdorff space](https://ncatlab.org/nlab/show/Hausdorff+space)
- [hereditarily finite set](https://ncatlab.org/nlab/show/hereditarily+finite+set)
- [infinite set](https://ncatlab.org/nlab/show/infinite+set)
- [injection](https://ncatlab.org/nlab/show/injection)
- [local ring](https://ncatlab.org/nlab/show/local+ring)
- [metric space](https://ncatlab.org/nlab/show/metric+space)
- [partial function](https://ncatlab.org/nlab/show/partial+function)
- [pure set](https://ncatlab.org/nlab/show/pure+set)
- [real number](https://ncatlab.org/nlab/show/real+number)
- [sequence](https://ncatlab.org/nlab/show/sequence)
- [Set](https://ncatlab.org/nlab/show/Set)
- [Sierpinski space](https://ncatlab.org/nlab/show/Sierpinski+space)
- [simple object](https://ncatlab.org/nlab/show/simple+object)
- [sober space](https://ncatlab.org/nlab/show/sober+space)
- [topological space](https://ncatlab.org/nlab/show/topological+space)
- [Tychonoff theorem](https://ncatlab.org/nlab/show/Tychonoff+theorem)
- [uniform space](https://ncatlab.org/nlab/show/uniform+space)
- [well-founded relation](https://ncatlab.org/nlab/show/well-founded+relation)
- [well-order](https://ncatlab.org/nlab/show/well-order)
- [well-ordering theorem](https://ncatlab.org/nlab/show/well-ordering+theorem)
- [well-pointed topos](https://ncatlab.org/nlab/show/well-pointed+topos)
- [Zorn's lemma](https://ncatlab.org/nlab/show/Zorn%27s+lemma)

In principle, every article could explain how it applies to constructive mathematics, but that will probably never happen.

There is also

- constructivism and idealism[?](https://ncatlab.org/nlab/new/constructivism+and+idealism)

## References

See also the references at *[intuitionistic mathematics](https://ncatlab.org/nlab/show/intuitionistic+mathematics)* for more.

Original texts:

- [Errett Bishop](https://ncatlab.org/nlab/show/Errett+Bishop), *[Foundations of Constructive Analysis](https://ncatlab.org/nlab/show/Foundations+of+Constructive+Analysis)*, McGraw-Hill (1967)

rewritten as:

- [Errett Bishop](https://ncatlab.org/nlab/show/Errett+Bishop), [Douglas Bridges](https://ncatlab.org/nlab/show/Douglas+Bridges) *[Constructive Analysis](https://ncatlab.org/nlab/show/Constructive+Analysis)*, Grundlehren der mathematischen Wissenschaften **279**, Springer (1985) \[[doi:10.1007/978-3-642-61667-9](https://doi.org/10.1007/978-3-642-61667-9)\]

Early monographs:

- [Anne Sjerp Troelstra](https://ncatlab.org/nlab/show/Anne+Sjerp+Troelstra), [Dirk van Dalen](https://ncatlab.org/nlab/show/Dirk+van+Dalen): *Constructivism in Mathematics – An introduction*, Volume I, Studies in Logic and the Foundations of Mathematics **121**, North Holland (1988) \[[ISBN:9780444702661](https://www.elsevier.com/books/constructivism-in-mathematics-vol-1/troelstra/978-0-444-70266-1)\]
- [Anne Sjerp Troelstra](https://ncatlab.org/nlab/show/Anne+Sjerp+Troelstra), [Dirk van Dalen](https://ncatlab.org/nlab/show/Dirk+van+Dalen), *Constructivism in Mathematics – An introduction*, Volume II, Studies in Logic and the Foundations of Mathematics **123**: North Holland (1988) \[[ISBN:9780444703583](https://shop.elsevier.com/books/constructivism-in-mathematics-vol-2/troelstra/978-0-444-70358-3)\]

Gentle introductions:

- [Douglas Bridges](https://ncatlab.org/nlab/show/Douglas+Bridges): *Introducing constructive mathematics*, talk notes (~2015) \[[pdf](https://ncatlab.org/nlab/files/Bridges-IntroducingConstructiveMath.pdf "pdf")\]
- [Andrej Bauer](https://ncatlab.org/nlab/show/Andrej+Bauer): *Five Stages of Accepting Constructive Mathematics*, Bull. Amer. Math. Soc. **54** (2017) 481-498 \[[doi:10.1090/bull/1556](http://dx.doi.org/10.1090/bull/1556), [pdf](https://www.ams.org/journals/bull/2017-54-03/S0273-0979-2016-01556-4/S0273-0979-2016-01556-4.pdf)\]
	based on a talk at IAS (March 18, 2013) \[[video](http://video.ias.edu/members/1213/0318-AndrejBauer)\]
- [Fred Richman](https://ncatlab.org/nlab/show/Fred+Richman), *[Interview with a constructive mathematician](https://projecteuclid.org/journals/modern-logic/volume-6/issue-3/Interview-with-a-constructive-mathematician/rml/1204835729.full)*, Modern Logic **6** 3 (1996) 247-271 \[[MathSciNet](http://www.ams.org/mathscinet-getitem?mr=1400617)\]
- [Ingo Blechschmidt](https://ncatlab.org/nlab/show/Ingo+Blechschmidt), *Double-negation translation and CPS transforms*, 2015 ([pdf](http://rawgit.com/iblech/talk-constructive-mathematics/master/negneg-translation-notes.pdf))
- Stanford Encyclopedia of Philosophy, *[Constructive mathematics](http://plato.stanford.edu/entries/mathematics-constructive/)*

An more technical introduction to constructive reasoning in mathematics is (with an eye towards [homotopy type theory](https://ncatlab.org/nlab/show/homotopy+type+theory)) in the introduction of:

- [Univalent Foundations Project](https://ncatlab.org/nlab/show/Univalent+Foundations+Project), *[Homotopy Type Theory – Univalent Foundations of Mathematics](https://ncatlab.org/nlab/show/Homotopy+Type+Theory+--+Univalent+Foundations+of+Mathematics)*

Other accounts:

- [Michael J. Beeson](https://ncatlab.org/nlab/show/Michael+J.+Beeson), *Foundations of Constructive Mathematics*, Ergebnisse der Mathematik und ihrer Grenzgebiete **3** 6, Springer 1985 ([doi:10.1007/978-3-642-68952-9](https://link.springer.com/book/10.1007/978-3-642-68952-9), [pdf](https://link.springer.com/content/pdf/10.1007%2F978-3-642-68952-9.pdf))
- [Douglas Bridges](https://ncatlab.org/nlab/show/Douglas+Bridges) and [Fred Richman](https://ncatlab.org/nlab/show/Fred+Richman), *Varieties of constructive mathematics* (1987)
- [Fred Richman](https://ncatlab.org/nlab/show/Fred+Richman), [Douglas Bridges](https://ncatlab.org/nlab/show/Douglas+Bridges), Peter Schuster, *A weak countable choice principle*. Proceedings of the American Mathematical Society 128(9):2749-2752, March 2000. \[[doi:10.1090/S0002-9939-00-05327-2](http://dx.doi.org/10.1090/S0002-9939-00-05327-2)\]
- [Michael Makkai](https://ncatlab.org/nlab/show/Michael+Makkai) (1996). [Avoiding the axiom of choice in general category theory](http://www.math.mcgill.ca/makkai/anafun/).
- [Fred Richman](https://ncatlab.org/nlab/show/Fred+Richman), *Constructive Mathematics without Choice*,
	in: *Reuniting the Antipodes – Constructive and Nonstandard Views of the Continuum*, Synthese Library **306**, Springer (2001) 199-206 \[[doi:10.1007/978-94-015-9757-9\_17](https://doi.org/10.1007/978-94-015-9757-9_17)\]
- [Paul Taylor](https://ncatlab.org/nlab/show/Paul+Taylor) (1996). Intuitionistic Sets and Ordinals. Available (with several other references) at [Induction, recursion, replacement and the ordinals](http://www.paultaylor.eu/ordinals/index.php).
- [André Joyal](https://ncatlab.org/nlab/show/Andr%C3%A9+Joyal) and [Ieke Moerdijk](https://ncatlab.org/nlab/show/Ieke+Moerdijk) (1995). *Algebraic set theory*.
- [Franka Waaldijk](https://ncatlab.org/nlab/show/Franka+Waaldijk), *On the foundations of constructive mathematics - especially in relation to the theory of continuous functions*, Foundations of Science, Volume 10, pages 249–324, (2005). ([doi:10.1007/s10699-004-3065-z](https://doi.org/10.1007/s10699-004-3065-z), [pdf](https://www.fwaaldijk.nl/foundations%20of%20constructive%20mathematics.pdf)).
- [Auke B. Booij](https://ncatlab.org/nlab/show/Auke+B.+Booij), Analysis in univalent type theory ([pdf](https://etheses.bham.ac.uk/id/eprint/10411/7/Booij2020PhD.pdf))

On constructive mathematics applied to [physics](https://ncatlab.org/nlab/show/physics) (cf. *[computable physics](https://ncatlab.org/nlab/show/computable+physics)*):

- [Douglas S. Bridges](https://ncatlab.org/nlab/show/Douglas+S.+Bridges): *Can Constructive Mathematics Be Applied in Physics?*, Journal of Philosophical Logic **28** 5 (1999) 439-453 \[[jstor:30226680](https://www.jstor.org/stable/30226680), [doi:10.1023/A:1004420413391](https://doi.org/10.1023/A:1004420413391)\]
- [Andrej Bauer](https://ncatlab.org/nlab/show/Andrej+Bauer): *Intuitionistic Mathematics and Realizability in the Physical World*, in *A Computable Universe* (2012) 143-157 \[[doi:10.1142/9789814374309\_0008](https://doi.org/10.1142/9789814374309_0008), [pdf](https://math.andrej.com/wp-content/uploads/2014/03/real-world-realizability.pdf), [webpage](https://math.andrej.com/2014/03/04/intuitionistic-mathematics-and-realizability-in-the-physical-world/)\]

In view of [reverse mathematics](https://ncatlab.org/nlab/show/reverse+mathematics):

- [Hajime Ishihara](https://ncatlab.org/nlab/show/Hajime+Ishihara), *Reverse Mathematics in Bishop’s Constructive Mathematics*, Philosophia Scientiæ, CS 6 (2006) ([doi:10.4000/philosophiascientiae.406](https://doi.org/10.4000/philosophiascientiae.406), [pdf](https://philosophiascientiae.revues.org/pdf/406))
- [Hannes Diener](https://ncatlab.org/nlab/show/Hannes+Diener), *Constructive Reverse Mathematics*, 2018 ([arXiv:1804.05495](https://arxiv.org/abs/1804.05495), [dspace:ubsi/1306](https://dspace.ub.uni-siegen.de/handle/ubsi/1306))

General comments on intuitionistic mathematics/logic as the natural language for [physics](https://ncatlab.org/nlab/show/physics) are in

- [Andrej Bauer](https://ncatlab.org/nlab/show/Andrej+Bauer), *[Intuitionistic mathematics for physics](http://math.andrej.com/2008/08/13/intuitionistic-mathematics-for-physics/)*, August 2008

For more on [physics](https://ncatlab.org/nlab/show/physics) formalized in intuitionistic mathematics (notably in [topos theory](https://ncatlab.org/nlab/show/topos+theory)) see at *[geometry of physics](https://ncatlab.org/nlab/show/geometry+of+physics)*.

For an emphasis on [proof relevance](https://ncatlab.org/nlab/show/proof+relevance), see:

- [Robert Harper](https://ncatlab.org/nlab/show/Robert+Harper), *[Constructive Mathematics is not Metamathematics](https://existentialtype.wordpress.com/2013/07/10/constructive-mathematics-is-not-meta-mathematics/)* (2013)

Most books on [topos theory](https://ncatlab.org/nlab/show/topos+theory) include some discussion of toposes' [internal](https://ncatlab.org/nlab/show/internal+logic) constructive logic. One good reference is:

- [Peter Johnstone](https://ncatlab.org/nlab/show/Peter+Johnstone) (2003). *[Sketches of an elephant](https://ncatlab.org/nlab/show/Elephant)*. Part D (in volume 2).

A historical account is in

- [Anne Sjerp Troelstra](https://ncatlab.org/nlab/show/Anne+Sjerp+Troelstra), *History of Constructivism in the Twentieth Century* (1991) \[[pdf](https://www.illc.uva.nl/Research/Publications/Reports/ML-1991-05.text.pdf), [pdf](https://ncatlab.org/nlab/files/Troelstra-HistoryOfConstructivism.pdf "pdf")\]

The relation to [realizability](https://ncatlab.org/nlab/show/realizability) and [computability](https://ncatlab.org/nlab/show/computability) is discussed in

- [Andrej Bauer](https://ncatlab.org/nlab/show/Andrej+Bauer), *Realizability as connection between constructive and computable mathematics*, in T. Grubba, P. Hertling, H. Tsuiki, and [Klaus Weihrauch](https://ncatlab.org/nlab/show/Klaus+Weihrauch), (eds.) *CCA 2005 - Second International Conference on Computability and Complexity in Analysis*, August 25-29,2005, Kyoto, Japan, ser. Informatik Berichte, vol. 326-7/2005. FernUniversität Hagen, Germany, 2005, pp. 378–379. ([pdf](http://math.andrej.com/data/c2c.pdf))

On [commutative algebra](https://ncatlab.org/nlab/show/commutative+algebra) with constructive methods:

- [Henri Lombardi](https://ncatlab.org/nlab/show/Henri+Lombardi), [Claude Quitté](https://ncatlab.org/nlab/show/Claude+Quitt%C3%A9) (2010): *Commutative algebra: Constructive methods (Finite projective modules)* Translated by Tania K. Roblo, Springer (2015) ([doi:10.1007/978-94-017-9944-7](https://link.springer.com/book/10.1007/978-94-017-9944-7), [pdf](http://hlombardi.free.fr/CACM.pdf))

On the [antithesis interpretation](https://ncatlab.org/nlab/show/antithesis+interpretation) of [constructive mathematics](https://ncatlab.org/nlab/show/constructive+mathematics):

- [Michael Shulman](https://ncatlab.org/nlab/show/Michael+Shulman), *Affine logic for constructive mathematics*. Bulletin of Symbolic Logic, Volume 28, Issue 3, September 2022. pp. 327 - 386 ([doi:10.1017/bsl.2022.28](https://doi.org/10.1017/bsl.2022.28), [arXiv:1805.07518](https://arxiv.org/abs/1805.07518))

Last revised on August 23, 2025 at 13:46:53. See the [history](https://ncatlab.org/nlab/history/constructive+mathematics) of this page for a list of all contributions to it.