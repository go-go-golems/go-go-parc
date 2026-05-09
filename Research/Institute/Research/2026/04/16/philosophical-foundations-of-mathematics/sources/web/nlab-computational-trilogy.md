## nLab computational trilogy

Contents

## Contents

## Idea

A profound cross-disciplinary insight has emerged – starting in the late 1970s, with core refinements in recent years – observing that three superficially different-looking fields of [mathematics](https://ncatlab.org/nlab/show/mathematics),

- [formal logic](https://ncatlab.org/nlab/show/formal+logic) / [type theory](https://ncatlab.org/nlab/show/type+theory)
- [∞-](https://ncatlab.org/nlab/show/%28%E2%88%9E%2C1%29-category) [category theory](https://ncatlab.org/nlab/show/category+theory) / [∞-](https://ncatlab.org/nlab/show/%28%E2%88%9E%2C1%29-topos) [topos theory](https://ncatlab.org/nlab/show/topos+theory) ([algebraic topology](https://ncatlab.org/nlab/show/algebraic+topology))

are but three different perspectives on a single underlying phenomenon at the [foundations of mathematics](https://ncatlab.org/nlab/show/foundations+of+mathematics):

### Classical

#### Plain

Under the identifications

1. [propositions as types](https://ncatlab.org/nlab/show/propositions+as+types),
2. [programs as proofs](https://ncatlab.org/nlab/show/programs+as+proofs),
3. [relation between type theory and category theory](https://ncatlab.org/nlab/show/relation+between+type+theory+and+category+theory)

the following notions are equivalent:

| In [intuitionistic](https://ncatlab.org/nlab/show/intuitionistic+mathematics) [logic](https://ncatlab.org/nlab/show/logic)   and [type theory](https://ncatlab.org/nlab/show/type+theory): | In [programming languages](https://ncatlab.org/nlab/show/programming+languages)   and [computation](https://ncatlab.org/nlab/show/computation): | In [category theory](https://ncatlab.org/nlab/show/category+theory)   and [topos theory](https://ncatlab.org/nlab/show/topos+theory): |
| --- | --- | --- |
| A [proof](https://ncatlab.org/nlab/show/proof) of a [proposition](https://ncatlab.org/nlab/show/proposition),   [or](https://ncatlab.org/nlab/show/propositions+as+types) a [term](https://ncatlab.org/nlab/show/term) of some [type](https://ncatlab.org/nlab/show/type). | A [program](https://ncatlab.org/nlab/show/program) / [λ-term](https://ncatlab.org/nlab/show/%CE%BB-term) with   output of some [data type](https://ncatlab.org/nlab/show/data+type). | A [generalized element](https://ncatlab.org/nlab/show/generalized+element)   of an [object](https://ncatlab.org/nlab/show/object). |

whence these three subjects are but three perspectives on a single underlying phenomenon.

This insight dates from the late 1970s; an early record is [Lambek & Scott 86](https://ncatlab.org/nlab/show/computational+trilogy#LambekScott86); it is explicitly highlighted as a *trilogy* ([Wikipedia](https://en.wikipedia.org/wiki/Trilogy): “three works of art that are connected and can be seen either as a single work or as three individual works”) in [Melliès 06, Sec. 1](https://ncatlab.org/nlab/show/computational+trilogy#Mellies06):

![[Attachments/f1235eadec80a989bef839f81ec31110_MD5.png]]

From Melliès 06

(Notice that [Melliès 06](https://ncatlab.org/nlab/show/computational+trilogy#Mellies06) on [p.2](https://hal.archives-ouvertes.fr/hal-00154243/document#page=3) does mean to regard [λ-calculus](https://ncatlab.org/nlab/show/%CE%BB-calculus) as [programming language](https://ncatlab.org/nlab/show/programming+language).)

In [Harper 11](https://ncatlab.org/nlab/show/computational+trilogy#Harper11) the profoundness of the trilogy inspires the following emphatic prose, alluding to the doctrinal position of ‘trinitarianism’:

> The central dogma of computational trinitarianism holds that Logic, Languages, and Categories are but three manifestations of one divine notion of computation. There is no preferred route to enlightenment: each aspect provides insights that comprise the experience of computation in our lives.
> 
> Computational trinitarianism entails that any concept arising in one aspect should have meaning from the perspective of the other two. If you arrive at an insight that has importance for logic, languages, and categories, then you may feel sure that you have elucidated an essential concept of computation–you have made an enduring scientific discovery.

For more detailed review see [Eades 12, Sec. 3](https://ncatlab.org/nlab/show/computational+trilogy#Eades12).

#### Parametrized

More is true: Since

1. computation happens in [contexts](https://ncatlab.org/nlab/show/contexts) and is [proof relevant](https://ncatlab.org/nlab/show/proof+relevance);
2. [categories](https://ncatlab.org/nlab/show/categories) give rise to their [systems of](https://ncatlab.org/nlab/show/codomain+fibration) [slice categories](https://ncatlab.org/nlab/show/slice+categories) and are in general [(∞,1)-categories](https://ncatlab.org/nlab/show/%28%E2%88%9E%2C1%29-categories);
3. [types](https://ncatlab.org/nlab/show/types) may [depend](https://ncatlab.org/nlab/show/dependent+type+theory) on other types and are in general [homotopy types](https://ncatlab.org/nlab/show/homotopy+type+theory)

the traditional computational trilogy [above](https://ncatlab.org/nlab/show/computational+trilogy#ClassicalPlain) enhances to read as follows:

| In [dependent](https://ncatlab.org/nlab/show/dependent+type+theory)   [homotopy type theory](https://ncatlab.org/nlab/show/homotopy+type+theory): | In [programming languages](https://ncatlab.org/nlab/show/programming+languages)   and [computation](https://ncatlab.org/nlab/show/computation): | In [locally cartesian closed](https://ncatlab.org/nlab/show/locally+cartesian+closed+%28%E2%88%9E%2C1%29-categories)   [(∞,1)-categories](https://ncatlab.org/nlab/show/%28%E2%88%9E%2C1%29-categories) / [(∞,1)-toposes](https://ncatlab.org/nlab/show/%28%E2%88%9E%2C1%29-toposes): |
| --- | --- | --- |
| A [term](https://ncatlab.org/nlab/show/term) of some [type](https://ncatlab.org/nlab/show/type)   in [context](https://ncatlab.org/nlab/show/context). | A [program](https://ncatlab.org/nlab/show/program) outputting some [data type](https://ncatlab.org/nlab/show/data+type)   in [context](https://ncatlab.org/nlab/show/context). | A [generalized element](https://ncatlab.org/nlab/show/generalized+element) of an [object](https://ncatlab.org/nlab/show/object)   in a [slice](https://ncatlab.org/nlab/show/slice+%28%E2%88%9E%2C1%29-category). |

See also [Shulman 18](https://ncatlab.org/nlab/show/computational+trilogy#Shulman18).

In this deeper form yet another equivalence – to [algebraic topology](https://ncatlab.org/nlab/show/algebraic+topology) ([Sati Schreiber 20](https://ncatlab.org/schreiber/show/Proper+Orbifold+Cohomology), [p. 5](https://ncatlab.org/schreiber/files/orbi210313.pdf#page=5)) – opens up, as [generalized elements](https://ncatlab.org/nlab/show/generalized+elements) in an [(∞,1)-topos](https://ncatlab.org/nlab/show/%28%E2%88%9E%2C1%29-topos) may equivalently be regarded as [cocycles](https://ncatlab.org/nlab/show/cocycles) in ([non-abelian](https://ncatlab.org/nlab/show/non-abelian+cohomology)) [cohomology](https://ncatlab.org/nlab/show/cohomology), and in [twisted cohomology](https://ncatlab.org/nlab/show/twisted+cohomology) if in a [slice (∞,1)-category](https://ncatlab.org/nlab/show/slice+%28%E2%88%9E%2C1%29-category) ([Sati Schreiber 20](https://ncatlab.org/schreiber/show/Proper+Orbifold+Cohomology) [p. 6](https://arxiv.org/pdf/2008.01101.pdf#page=6), [FSS 20](https://ncatlab.org/schreiber/show/The+Character+Map+in+Twisted+Non-Abelian+Cohomology)), whence we have a *computational tetralogy*:

| In [dependent](https://ncatlab.org/nlab/show/dependent+type+theory)   [homotopy type theory](https://ncatlab.org/nlab/show/homotopy+type+theory): | In [programming languages](https://ncatlab.org/nlab/show/programming+languages)   and [computation](https://ncatlab.org/nlab/show/computation): | In [locally cartesian closed](https://ncatlab.org/nlab/show/locally+cartesian+closed+%28%E2%88%9E%2C1%29-categories)   [∞-categories](https://ncatlab.org/nlab/show/%28%E2%88%9E%2C1%29-categories) / [∞-toposes](https://ncatlab.org/nlab/show/%28%E2%88%9E%2C1%29-toposes): | In [non-abelian](https://ncatlab.org/nlab/show/non-abelian+cohomology) [cohomology](https://ncatlab.org/nlab/show/cohomology)   [param. homotopy theory](https://ncatlab.org/nlab/show/parametrized+homotopy+theory): |
| --- | --- | --- | --- |
| A [term](https://ncatlab.org/nlab/show/term) of some [type](https://ncatlab.org/nlab/show/type)   in [context](https://ncatlab.org/nlab/show/context). | A [program](https://ncatlab.org/nlab/show/program) of some [data type](https://ncatlab.org/nlab/show/data+type)   in [context](https://ncatlab.org/nlab/show/context). | An [element](https://ncatlab.org/nlab/show/generalized+element) of an [object](https://ncatlab.org/nlab/show/object)   in a [slice](https://ncatlab.org/nlab/show/slice+%28%E2%88%9E%2C1%29-category). | A [cocycle](https://ncatlab.org/nlab/show/cocycle)   in [twisted cohomology](https://ncatlab.org/nlab/show/twisted+cohomology). |

> (graphics from *[SS22](https://ncatlab.org/schreiber/show/Topological+Quantum+Programming+in+TED-K)*)

### Quantum

#### Plain

An analogous trilogy is seen under passage:

1. from [logic](https://ncatlab.org/nlab/show/logic) / [type theory](https://ncatlab.org/nlab/show/type+theory) to [linear logic](https://ncatlab.org/nlab/show/linear+logic) / [linear type theory](https://ncatlab.org/nlab/show/linear+type+theory);
2. from [cartesian closed categories](https://ncatlab.org/nlab/show/cartesian+closed+categories) to [closed monoidal categories](https://ncatlab.org/nlab/show/closed+monoidal+categories)

This is the main point of [Melliès 06, Sec. 1](https://ncatlab.org/nlab/show/computational+trilogy#Mellies06), only that where Melliès shows “ [proof nets](https://ncatlab.org/nlab/show/proof+nets) ” ([p. 4](https://hal.archives-ouvertes.fr/hal-00154243/document#page=5)) we refer to them as “ [quantum computation](https://ncatlab.org/nlab/show/quantum+computation) ” for better emphasis, following [Abramsky-Coecke 04](https://ncatlab.org/nlab/show/quantum+programming+language#AbramskyCoecke04), [Abramsky & Duncan 05](https://ncatlab.org/nlab/show/quantum+programming+language#AbramskyDuncan05), [Duncan 06](https://ncatlab.org/nlab/show/quantum+programming+language#Duncan06); going back to [Pratt 92](https://ncatlab.org/nlab/show/quantum+programming+language#Pratt92):

![[Attachments/13a8555fa34b5c1565cab9fa81a763ea_MD5.png]]

From Melliès 06, p. 4

See also [Baez & Stay 09](https://ncatlab.org/nlab/show/computational+trilogy#BaezStay09).

#### Parametrized

Combining the [classical parametrized trilogy](https://ncatlab.org/nlab/show/computational+trilogy#ClassicalParametrized) with the [plain quantum trilogy](https://ncatlab.org/nlab/show/computational+trilogy#QuantumPlain), as one passes

- from classical [computation](https://ncatlab.org/nlab/show/computation) to **[classically controlled](https://ncatlab.org/nlab/show/quantum+computation#ClassicalControlQuantumData) [quantum computation](https://ncatlab.org/nlab/show/quantum+computation)** on [linear](https://ncatlab.org/nlab/show/linear+spaces) [spaces of quantum states](https://ncatlab.org/nlab/show/spaces+of+quantum+states) parametrized over classical [data types](https://ncatlab.org/nlab/show/data+types);
- from [dependent](https://ncatlab.org/nlab/show/dependent+type+theory) [intuitionistic](https://ncatlab.org/nlab/show/intuitionistic+type+theory) [homotopy type theory](https://ncatlab.org/nlab/show/homotopy+type+theory) to **[dependent](https://ncatlab.org/nlab/show/dependent+linear+type+theory) [linear type theory](https://ncatlab.org/nlab/show/linear+type+theory)** of dependent [stable homotopy types](https://ncatlab.org/nlab/show/stable+homotopy+types);
- from [locally cartesian closed categories](https://ncatlab.org/nlab/show/locally+cartesian+closed+categories) / [(∞,1)-categories](https://ncatlab.org/nlab/show/locally+cartesian+closed+%28%E2%88%9E%2C1%29-categories) to **[indexed monoidal categories](https://ncatlab.org/nlab/show/indexed+monoidal+categories) / [(∞,1)-categories](https://ncatlab.org/nlab/show/indexed+monoidal+%28%E2%88%9E%2C1%29-categories)** of [parametrized spectra](https://ncatlab.org/nlab/show/parametrized+spectra); which in the language of [algebraic topology](https://ncatlab.org/nlab/show/algebraic+topology) is the context of **[twisted](https://ncatlab.org/nlab/show/twisted+generalized+cohomology) [generalized cohomology theory](https://ncatlab.org/nlab/show/generalized+cohomology+theory)**.

there appears the “classically controlled quantum computational tetralogy”:

> (graphics from *[SS22](https://ncatlab.org/schreiber/show/Topological+Quantum+Programming+in+TED-K)*)

| In [dependent linear](https://ncatlab.org/nlab/show/dependent+linear+type+theory)   [homotopy type theory](https://ncatlab.org/nlab/show/homotopy+type+theory): | In [classically controlled](https://ncatlab.org/nlab/show/quantum+computation#ClassicalControlQuantumData)   [quantum programming languages](https://ncatlab.org/nlab/show/quantum+programming+languages): | In [indexed monoidal](https://ncatlab.org/nlab/show/indexed+monoidal+%28%E2%88%9E%2C1%29-categories)   [∞-cats of par. spectra](https://ncatlab.org/nlab/show/parameterized+stable+homotopy+theory): | In [Whitehead-generalized](https://ncatlab.org/nlab/show/Whitehead+generalized+cohomology+theory)   [twisted cohomology theory](https://ncatlab.org/nlab/show/twisted+cohomology+theory): |
| --- | --- | --- | --- |
| A [term](https://ncatlab.org/nlab/show/term) of some [type](https://ncatlab.org/nlab/show/type)   in [context](https://ncatlab.org/nlab/show/context). | A [quantum circuit](https://ncatlab.org/nlab/show/quantum+circuit)   controlled by [classical data](https://ncatlab.org/nlab/show/data+type). | An [element](https://ncatlab.org/nlab/show/generalized+element) of an [object](https://ncatlab.org/nlab/show/object)   in a [slice](https://ncatlab.org/nlab/show/slice+%28%E2%88%9E%2C1%29-category). | A [cocycle](https://ncatlab.org/nlab/show/cocycle)   in [twisted cohomology](https://ncatlab.org/nlab/show/twisted+cohomology). |

(along the lines of [Schreiber 14](https://ncatlab.org/schreiber/show/Quantization+via+Linear+homotopy+types), [Nuiten 13](https://ncatlab.org/schreiber/show/master+thesis+Nuiten),

- with parametrized stable homotopy theory understood as twisted cohomology theory as in [Ando, Blumberg & Gepner 10](https://ncatlab.org/nlab/show/twisted+cohomology#ABG10), [Ando, Blumberg, Gepner & Hopkins 14](https://ncatlab.org/nlab/show/computational+trilogy#twisted+cohomology#ABGHR14), [Fiorenza, Sati, Schreiber 20](https://ncatlab.org/schreiber/show/The+Character+Map+in+Twisted+Non-Abelian+Cohomology);
- with dependent linear homotopy type theory understood as, e.g., in [Riley, Finster & Licata 21](https://ncatlab.org/nlab/show/dependent+linear+type+theory#RileyFinsterLicata21) following [Schreiber 13](https://ncatlab.org/schreiber/show/differential+cohomology+in+a+cohesive+topos) [Prop. 4.1.9](https://arxiv.org/pdf/1310.7930v1.pdf#page=446);
- with classically controlled quantum computation seen as dependent linear type theory, as stated fully explicitly in [Fu, Kishida & Selinger 20](https://ncatlab.org/nlab/show/quantum+programming+language#FKS20), [Fu, Kishida, Ross & Selinger 20](https://ncatlab.org/nlab/show/quantum+programming+language#FKRS20) and more tentatively before in [Vakar 14](https://ncatlab.org/nlab/show/dependent+linear+type+theory#Vakar14), [Vakar 15](https://ncatlab.org/nlab/show/dependent+linear+type+theory#Vakar15), [Vakar 17](https://ncatlab.org/nlab/show/dependent+linear+type+theory#Vakar17), following [Schreiber 14](https://ncatlab.org/schreiber/show/Quantization+via+Linear+homotopy+types))

$\,$

![[Attachments/c8cd1b8f43bf56ab41a7e7c1a75d4bef_MD5.png]]

> (from [SS22](https://ncatlab.org/schreiber/show/Topological+Quantum+Programming+in+TED-K))

  

## Rosetta stone

The following shows a rosetta stone dictionary with more details:

> (NB. This table shows the computational aspect mostly under “type theory”…)

**[computational trinitarianism](https://ncatlab.org/nlab/show/computational+trinitarianism)** =  
**[propositions as types](https://ncatlab.org/nlab/show/propositions+as+types)** + **[programs as proofs](https://ncatlab.org/nlab/show/programs+as+proofs)** + **[relation type theory/category theory](https://ncatlab.org/nlab/show/relation+between+type+theory+and+category+theory)**

| [logic](https://ncatlab.org/nlab/show/logic) | [set theory](https://ncatlab.org/nlab/show/set+theory) ([internal logic](https://ncatlab.org/nlab/show/internal+logic+of+set+theory) of) | [category theory](https://ncatlab.org/nlab/show/category+theory) | [type theory](https://ncatlab.org/nlab/show/type+theory) |
| --- | --- | --- | --- |
| [proposition](https://ncatlab.org/nlab/show/proposition) | [set](https://ncatlab.org/nlab/show/set) | [object](https://ncatlab.org/nlab/show/object) | [type](https://ncatlab.org/nlab/show/type) |
| [predicate](https://ncatlab.org/nlab/show/predicate) | [family of sets](https://ncatlab.org/nlab/show/family+of+sets) | [display morphism](https://ncatlab.org/nlab/show/display+morphism) | [dependent type](https://ncatlab.org/nlab/show/dependent+type) |
| [proof](https://ncatlab.org/nlab/show/proof) | [element](https://ncatlab.org/nlab/show/element) | [generalized element](https://ncatlab.org/nlab/show/generalized+element) | [term](https://ncatlab.org/nlab/show/term) / [program](https://ncatlab.org/nlab/show/program) |
| [cut rule](https://ncatlab.org/nlab/show/cut+rule) |  | [composition](https://ncatlab.org/nlab/show/composition) of [classifying morphisms](https://ncatlab.org/nlab/show/classifying+morphisms) / [pullback](https://ncatlab.org/nlab/show/pullback) of [display maps](https://ncatlab.org/nlab/show/display+maps) | [substitution](https://ncatlab.org/nlab/show/substitution) |
| [introduction rule](https://ncatlab.org/nlab/show/introduction+rule) for [implication](https://ncatlab.org/nlab/show/implication) |  | [counit](https://ncatlab.org/nlab/show/counit) for hom-tensor adjunction | lambda |
| [elimination rule](https://ncatlab.org/nlab/show/elimination+rule) for [implication](https://ncatlab.org/nlab/show/implication) |  | [unit](https://ncatlab.org/nlab/show/unit) for hom-tensor adjunction | application |
| [cut elimination](https://ncatlab.org/nlab/show/cut+elimination) for [implication](https://ncatlab.org/nlab/show/implication) |  | one of the [zigzag identities](https://ncatlab.org/nlab/show/zigzag+identities) for hom-tensor adjunction | [beta reduction](https://ncatlab.org/nlab/show/beta+reduction) |
| identity elimination for [implication](https://ncatlab.org/nlab/show/implication) |  | the other [zigzag identity](https://ncatlab.org/nlab/show/zigzag+identity) for hom-tensor adjunction | [eta conversion](https://ncatlab.org/nlab/show/eta+conversion) |
| [true](https://ncatlab.org/nlab/show/true) | [singleton](https://ncatlab.org/nlab/show/singleton) | [terminal object](https://ncatlab.org/nlab/show/terminal+object) / [(-2)-truncated object](https://ncatlab.org/nlab/show/%28-2%29-truncated+object) | [h-level 0](https://ncatlab.org/nlab/show/h-level+0) - [type](https://ncatlab.org/nlab/show/type) / [unit type](https://ncatlab.org/nlab/show/unit+type) |
| [false](https://ncatlab.org/nlab/show/false) | [empty set](https://ncatlab.org/nlab/show/empty+set) | [initial object](https://ncatlab.org/nlab/show/initial+object) | [empty type](https://ncatlab.org/nlab/show/empty+type) |
| [proposition](https://ncatlab.org/nlab/show/proposition), [truth value](https://ncatlab.org/nlab/show/truth+value) | [subsingleton](https://ncatlab.org/nlab/show/subsingleton) | [subterminal object](https://ncatlab.org/nlab/show/subterminal+object) / [(-1)-truncated object](https://ncatlab.org/nlab/show/%28-1%29-truncated+object) | [h-proposition](https://ncatlab.org/nlab/show/h-proposition), [mere proposition](https://ncatlab.org/nlab/show/mere+proposition) |
| [logical conjunction](https://ncatlab.org/nlab/show/logical+conjunction) | [cartesian product](https://ncatlab.org/nlab/show/cartesian+product) | [product](https://ncatlab.org/nlab/show/product) | [product type](https://ncatlab.org/nlab/show/product+type) |
| [disjunction](https://ncatlab.org/nlab/show/disjunction) | [disjoint union](https://ncatlab.org/nlab/show/disjoint+union) ([support](https://ncatlab.org/nlab/show/support) of) | [coproduct](https://ncatlab.org/nlab/show/coproduct) ([(-1)-truncation](https://ncatlab.org/nlab/show/%28-1%29-truncation) of) | [sum type](https://ncatlab.org/nlab/show/sum+type) ([bracket type](https://ncatlab.org/nlab/show/bracket+type) of) |
| [implication](https://ncatlab.org/nlab/show/implication) | [function set](https://ncatlab.org/nlab/show/function+set) (into [subsingleton](https://ncatlab.org/nlab/show/subsingleton)) | [internal hom](https://ncatlab.org/nlab/show/internal+hom) (into [subterminal object](https://ncatlab.org/nlab/show/subterminal+object)) | [function type](https://ncatlab.org/nlab/show/function+type) (into [h-proposition](https://ncatlab.org/nlab/show/h-proposition)) |
| [negation](https://ncatlab.org/nlab/show/negation) | [function set](https://ncatlab.org/nlab/show/function+set) into [empty set](https://ncatlab.org/nlab/show/empty+set) | [internal hom](https://ncatlab.org/nlab/show/internal+hom) into [initial object](https://ncatlab.org/nlab/show/initial+object) | [function type](https://ncatlab.org/nlab/show/function+type) into [empty type](https://ncatlab.org/nlab/show/empty+type) |
| [universal quantification](https://ncatlab.org/nlab/show/universal+quantification) | indexed [cartesian product](https://ncatlab.org/nlab/show/cartesian+product) (of family of [subsingletons](https://ncatlab.org/nlab/show/subsingletons)) | [dependent product](https://ncatlab.org/nlab/show/dependent+product) (of family of [subterminal objects](https://ncatlab.org/nlab/show/subterminal+objects)) | [dependent product type](https://ncatlab.org/nlab/show/dependent+product+type) (of family of [h-propositions](https://ncatlab.org/nlab/show/h-propositions)) |
| [existential quantification](https://ncatlab.org/nlab/show/existential+quantification) | indexed [disjoint union](https://ncatlab.org/nlab/show/disjoint+union) ([support](https://ncatlab.org/nlab/show/support) of) | [dependent sum](https://ncatlab.org/nlab/show/dependent+sum) ([(-1)-truncation](https://ncatlab.org/nlab/show/%28-1%29-truncation) of) | [dependent sum type](https://ncatlab.org/nlab/show/dependent+sum+type) ([bracket type](https://ncatlab.org/nlab/show/bracket+type) of) |
| [logical equivalence](https://ncatlab.org/nlab/show/logical+equivalence) | [bijection set](https://ncatlab.org/nlab/show/bijection+set) | [object of isomorphisms](https://ncatlab.org/nlab/show/object+of+isomorphisms) | [equivalence type](https://ncatlab.org/nlab/show/equivalence+type) |
|  | [support set](https://ncatlab.org/nlab/show/support+set) | [support object](https://ncatlab.org/nlab/show/support+object) / [(-1)-truncation](https://ncatlab.org/nlab/show/%28-1%29-truncation) | [propositional truncation](https://ncatlab.org/nlab/show/propositional+truncation) / [bracket type](https://ncatlab.org/nlab/show/bracket+type) |
|  |  | [n-image](https://ncatlab.org/nlab/show/n-image) of [morphism](https://ncatlab.org/nlab/show/morphism) into [terminal object](https://ncatlab.org/nlab/show/terminal+object) / [n-truncation](https://ncatlab.org/nlab/show/n-truncation) | [n-truncation modality](https://ncatlab.org/nlab/show/n-truncation+modality) |
| [propositional equality](https://ncatlab.org/nlab/show/propositional+equality) | [diagonal function](https://ncatlab.org/nlab/show/diagonal+function) / [diagonal subset](https://ncatlab.org/nlab/show/diagonal+subset) / [diagonal relation](https://ncatlab.org/nlab/show/diagonal+relation) | [path space object](https://ncatlab.org/nlab/show/path+space+object) | [identity type](https://ncatlab.org/nlab/show/identity+type) / [path type](https://ncatlab.org/nlab/show/path+type) |
| [completely presented set](https://ncatlab.org/nlab/show/completely+presented+set) | [set](https://ncatlab.org/nlab/show/set) | [discrete object](https://ncatlab.org/nlab/show/discrete+object) / [0-truncated object](https://ncatlab.org/nlab/show/0-truncated+object) | [h-level 2](https://ncatlab.org/nlab/show/h-level+2) - [type](https://ncatlab.org/nlab/show/type) / [set](https://ncatlab.org/nlab/show/set) / [h-set](https://ncatlab.org/nlab/show/h-set) |
| [set](https://ncatlab.org/nlab/show/set) | [set](https://ncatlab.org/nlab/show/set) with [equivalence relation](https://ncatlab.org/nlab/show/equivalence+relation) | [internal 0-groupoid](https://ncatlab.org/nlab/show/groupoid+object+in+an+%28infinity%2C1%29-category) | [Bishop set](https://ncatlab.org/nlab/show/Bishop+set) / [setoid](https://ncatlab.org/nlab/show/setoid) with its [pseudo-equivalence relation](https://ncatlab.org/nlab/show/pseudo-equivalence+relation) an actual [equivalence relation](https://ncatlab.org/nlab/show/equivalence+relation) |
|  | [equivalence class](https://ncatlab.org/nlab/show/equivalence+class) / [quotient set](https://ncatlab.org/nlab/show/quotient+set) | [quotient](https://ncatlab.org/nlab/show/quotient) | [quotient type](https://ncatlab.org/nlab/show/quotient+type) |
| [induction](https://ncatlab.org/nlab/show/induction) |  | [colimit](https://ncatlab.org/nlab/show/colimit) | [inductive type](https://ncatlab.org/nlab/show/inductive+type), [W-type](https://ncatlab.org/nlab/show/W-type), [M-type](https://ncatlab.org/nlab/show/M-type) |
| higher [induction](https://ncatlab.org/nlab/show/induction) |  | [higher colimit](https://ncatlab.org/nlab/show/%28infinity%2C1%29-colimit) | [higher inductive type](https://ncatlab.org/nlab/show/higher+inductive+type) |
| \- |  | [0-truncated](https://ncatlab.org/nlab/show/0-truncated) [higher colimit](https://ncatlab.org/nlab/show/%28infinity%2C1%29-colimit) | [quotient inductive type](https://ncatlab.org/nlab/show/quotient+inductive+type) |
| [coinduction](https://ncatlab.org/nlab/show/coinduction) |  | [limit](https://ncatlab.org/nlab/show/limit) | [coinductive type](https://ncatlab.org/nlab/show/coinductive+type) |
|  | [preset](https://ncatlab.org/nlab/show/preset) |  | [type](https://ncatlab.org/nlab/show/type) without [identity types](https://ncatlab.org/nlab/show/identity+types) |
|  | [set](https://ncatlab.org/nlab/show/set) of [truth values](https://ncatlab.org/nlab/show/truth+values) | [subobject classifier](https://ncatlab.org/nlab/show/subobject+classifier) | [type of propositions](https://ncatlab.org/nlab/show/type+of+propositions) |
| [domain of discourse](https://ncatlab.org/nlab/show/domain+of+discourse) | [universe](https://ncatlab.org/nlab/show/universe) | [object classifier](https://ncatlab.org/nlab/show/object+classifier) | [type universe](https://ncatlab.org/nlab/show/type+universe) |
| [modality](https://ncatlab.org/nlab/show/modality) |  | [closure operator](https://ncatlab.org/nlab/show/closure+operator), ([idempotent](https://ncatlab.org/nlab/show/idempotent+monad)) [monad](https://ncatlab.org/nlab/show/monad) | [modal type theory](https://ncatlab.org/nlab/show/modal+type+theory), [monad (in computer science)](https://ncatlab.org/nlab/show/monad+%28in+computer+science%29) |
| [linear logic](https://ncatlab.org/nlab/show/linear+logic) |  | ([symmetric](https://ncatlab.org/nlab/show/symmetric+monoidal+category), [closed](https://ncatlab.org/nlab/show/closed+monoidal+category)) [monoidal category](https://ncatlab.org/nlab/show/monoidal+category) | [linear type theory](https://ncatlab.org/nlab/show/linear+type+theory) / [quantum computation](https://ncatlab.org/nlab/show/quantum+computation) |
| [proof net](https://ncatlab.org/nlab/show/proof+net) |  | [string diagram](https://ncatlab.org/nlab/show/string+diagram) | [quantum circuit](https://ncatlab.org/nlab/show/quantum+circuit) |
| (absence of) [contraction rule](https://ncatlab.org/nlab/show/contraction+rule) |  | (absence of) [diagonal](https://ncatlab.org/nlab/show/diagonal) | [no-cloning theorem](https://ncatlab.org/nlab/show/no-cloning+theorem) |
|  |  | [synthetic mathematics](https://ncatlab.org/nlab/show/synthetic+mathematics) | [domain specific embedded programming language](https://ncatlab.org/nlab/show/domain+specific+embedded+programming+language) |

- [syntax-semantics duality](https://ncatlab.org/nlab/show/syntax-semantics+duality)
- [relation between category theory and type theory](https://ncatlab.org/nlab/show/relation+between+category+theory+and+type+theory)
- [programs as proofs](https://ncatlab.org/nlab/show/programs+as+proofs), [propositions as types](https://ncatlab.org/nlab/show/propositions+as+types)
- [initiality conjecture](https://ncatlab.org/nlab/show/initiality+conjecture)

## References

In the introduction of

- [Paul-André Melliès](https://ncatlab.org/nlab/show/Paul-Andr%C3%A9+Melli%C3%A8s), *Functorial boxes in string diagrams*, Procceding of *Computer Science Logic 2006* in Szeged, Hungary. 2006 ([hal:00154243](https://dumas.ccsd.cnrs.fr/PPS/hal-00154243), [pdf](https://hal.archives-ouvertes.fr/hal-00154243/document), [pdf](https://ncatlab.org/nlab/files/MelliesFunctorialBoxesInStringDiagrams.pdf "pdf"))

the insight is recalled to have surfaced in the 1970s, with an early appearance in print being the monograph

- [Joachim Lambek](https://ncatlab.org/nlab/show/Joachim+Lambek), [Phil Scott](https://ncatlab.org/nlab/show/Phil+Scott), *Introduction to Higher Order Categorical Logic*, Cambridge Studies in Advanced Mathematics Vol. 7. Cambridge University Press, 1986 (ISBN:978-0-521-24665-1)

See also at *[History of categorical semantics of linear type theory](https://ncatlab.org/nlab/show/linear+type+theory#HistoryCategoricalSemantics)* for more on this.

A exposition of the relation between the three concepts is in

- [Robert Harper](https://ncatlab.org/nlab/show/Robert+Harper), *The Holy Trinity* (2011) ([web](http://existentialtype.wordpress.com/2011/03/27/the-holy-trinity/), [wayback machine snapshot](https://web.archive.org/web/20170921012554/http://existentialtype.wordpress.com/2011/03/27/the-holy-trinity/))
- [Harley Eades](https://ncatlab.org/nlab/show/Harley+Eades), Section 3 of: *Type Theory and Applications*, 2012 ([pdf](https://metatheorem.org/includes/pubs/comp.pdf), [pdf](https://ncatlab.org/nlab/files/EadesTypeTheoryAndApplications.pdf "pdf"))
- Dan Frumin, *Computational trinitarianism*, Feb 2014 ([prezi slides](http://prezi.com/fnz-4wzsygiq/computational-trinitarianism/))

An exposition with emphasis on [linear logic](https://ncatlab.org/nlab/show/linear+logic) / [quantum logic](https://ncatlab.org/nlab/show/quantum+logic) and the relation to [physics](https://ncatlab.org/nlab/show/physics) is in

- [John Baez](https://ncatlab.org/nlab/show/John+Baez), [Mike Stay](https://ncatlab.org/nlab/show/Mike+Stay): *Physics, Topology, Logic and Computation: A Rosetta Stone*, in *New Structures for Physics*, Lecture Notes in Physics **813** Springer (2011) 95-174 \[[arXiv:0903.0340](http://arxiv.org/abs/0903.0340), [doi:10.1007/978-3-642-12821-9\_2](https://doi.org/10.1007/978-3-642-12821-9_2)\]

Discussion in the context of [homotopy type theory](https://ncatlab.org/nlab/show/homotopy+type+theory):

- [Mike Shulman](https://ncatlab.org/nlab/show/Mike+Shulman), *Homotopical trinitarianism: A perspective on homotopy type theory*, 2018 ([pdf slides](http://home.sandiego.edu/~shulman/papers/trinity.pdf), [pdf](https://ncatlab.org/nlab/files/ShulmanHomotopicalTrinitarianism.pdf "pdf"))

For further references see at *[programs as proofs](https://ncatlab.org/nlab/show/programs+as+proofs)*, *[propositions as types](https://ncatlab.org/nlab/show/propositions+as+types)*, and *[relation between category theory and type theory](https://ncatlab.org/nlab/show/relation+between+category+theory+and+type+theory)*.

Textbooks on the [foundations of mathematics](https://ncatlab.org/nlab/show/foundations+of+mathematics) and foundations of [programming language](https://ncatlab.org/nlab/show/programming+language) which connect via the common theme of [type theory](https://ncatlab.org/nlab/show/type+theory) / [categorical logic](https://ncatlab.org/nlab/show/categorical+logic) include the following:

- [Paul Taylor](https://ncatlab.org/nlab/show/Paul+Taylor), *[Practical Foundations of Mathematics](https://ncatlab.org/nlab/show/Practical+Foundations+of+Mathematics)* ([web](http://www.paultaylor.eu/~pt/prafm/index.html))
- [William Lawvere](https://ncatlab.org/nlab/show/William+Lawvere), [Robert Rosebrugh](https://ncatlab.org/nlab/show/Robert+Rosebrugh), *[Sets for Mathematics](https://ncatlab.org/nlab/show/Sets+for+Mathematics)*, Cambridge UP 2003 ([book homepage](http://www.mta.ca/~rrosebru/setsformath/), [GoogleBooks](http://books.google.de/books?id=h3_7aZz9ZMoC&pg=PP1&dq=sets+for+mathematics), [pdf](http://patryshev.com/books/Sets%20for%20Mathematics.pdf))
- [Robert Harper](https://ncatlab.org/nlab/show/Robert+Harper), *[Practical Foundations for Programming Languages](https://ncatlab.org/nlab/show/Practical+Foundations+for+Programming+Languages)*, Cambridge University Press (2016) ([ISBN:9781107150300](http://www.cambridge.org/us/academic/subjects/computer-science/programming-languages-and-applied-logic/practical-foundations-programming-languages-2nd-edition?format=HB))

See also

- [Joseph A. Goguen](https://ncatlab.org/nlab/show/Joseph+A.+Goguen), *[A Categorical Manifesto](https://ncatlab.org/nlab/show/A+Categorical+Manifesto)*. In *Mathematical Structures in Computer Science* **1** 1 (1991) 49-67 ([doi:10.1017/S0960129500000050](https://doi.org/10.1017/S0960129500000050), [CiteSeerX](http://citeseerx.ist.psu.edu/viewdoc/summary?doi=10.1.1.13.362).

Last revised on February 26, 2025 at 09:30:36. See the [history](https://ncatlab.org/nlab/history/computational+trilogy) of this page for a list of all contributions to it.