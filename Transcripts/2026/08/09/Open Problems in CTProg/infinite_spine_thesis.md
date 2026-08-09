---
title: "Orthogonality, Infinite Spines, and Synthetic Predomains"
subtitle: "A Partial Resolution and Exact Reduction of Xue's Conjecture 6.20"
author: "Research manuscript prepared by GPT-5.6 Pro (OpenAI)"
date: "9 August 2026"
documentclass: book
classoption:
  - 11pt
  - oneside
papersize: letter
geometry:
  - inner=1.15in
  - outer=1.05in
  - top=1.05in
  - bottom=1.05in
mainfont: "DejaVu Serif"
sansfont: "DejaVu Sans"
monofont: "DejaVu Sans Mono"
mathfont: "DejaVu Math TeX Gyre"
toc: true
toc-depth: 3
numbersections: true
secnumdepth: 3
colorlinks: true
linkcolor: ThesisNavy
urlcolor: ThesisNavy
header-includes:
  - \input{/mnt/data/infinite_spine_thesis/header.tex}
---

\frontmatter

# Status, scope, and integrity statement {-}

\statusbox{\textbf{Research status.} This is a thesis-style research manuscript, not a degree submission, not a peer-reviewed paper, and not a machine-checked formalization. It does \emph{not} claim a complete proof of Xue's Conjecture 6.20. It gives paper-level proofs of substantial consequences of the conjecture's hypothesis, reduces the unresolved part to one precise orthogonality question, proves several conditional versions, and records failed approaches and a concrete formalization programme. All claims labelled ``proved in this manuscript'' remain subject to expert review and mechanization.}

The problem addressed here was proposed by Runze Xue in *Topology in Synthetic Domain Theory and its Formalisation in Agda* (2026). In Xue's notation, the conjecture says that a type right-orthogonal to the inclusion of the infinite spine into the final lifting coalgebra is a synthetic predomain. The source itself cautions that the conjecture may be false and expects, more conservatively, that the hypothesis should at least imply Segal completeness and chain completeness.

This manuscript takes that caution literally. Its conclusions are divided into four levels.

| Level | Meaning in this manuscript |
|---|---|
| **Established source result** | A theorem or definition explicitly present in the cited literature. |
| **Paper-level deduction** | A proof supplied here from stated assumptions; not peer reviewed or machine checked. |
| **Conditional theorem** | A proof whose additional hypothesis is made explicit. |
| **Open or failed** | No valid proof or counterexample was obtained. |

The main honesty constraint is therefore simple: the unrestricted conjecture remains unresolved here. The exact point of failure is identified in Chapters 9--12.

# Abstract {-}

Let

\[
  j : \Lambda_\omega \longrightarrow \Delta^\infty \simeq \overline\omega
\]

be the canonical inclusion of the infinite directed spine into the infinite simplex/final lifting coalgebra in the synthetic-domain-theoretic setting developed by Xue. Conjecture 6.20 asserts that every type \(A\) for which precomposition

\[
  j^* : A^{\Delta^\infty} \longrightarrow A^{\Lambda_\omega}
\]

is an equivalence is a synthetic predomain: Segal complete, Rezk complete, \(\mathbb I\)-separated, and \(\omega\)-chain complete.

This manuscript proves the following at paper level, under explicit assumptions about the canonical finite-spine colimit presentations and their coherence.

First, every finite spine inclusion

\[
  j_n : \Lambda_n \hookrightarrow \Delta^n
\]

is a retract of \(j\) in the arrow category. Hence \(j\)-locality implies locality for every finite spine, and in particular Segal completeness.

Second, writing

\[
  \Lambda_\omega \xrightarrow{k} \Delta^\omega
  \xrightarrow{c} \Delta^\infty,
  \qquad j=c\circ k,
\]

mapping out of the sequential colimit presentations shows that \(j\)-locality implies \(k\)-locality. Two-out-of-three then implies \(c\)-locality, which is precisely \(\omega\)-chain completeness. More strongly,

\[
  A\perp j
  \quad\Longleftrightarrow\quad
  \bigl(A\perp c\bigr)
  \ \text{and}\ 
  \bigl(\forall n,\ A\perp j_n\bigr).
\]

Thus the infinite-spine condition is exactly the conjunction of finite categorical composition and chain convergence; it is not merely suggestive of those properties.

Third, assuming \(\mathbb I\)-separation, a cofinal even/odd subsequence argument turns chain convergence into antisymmetry. In Xue's h-set setting this supplies the Rezk component for the resulting thin Segal type. Consequently, the full conjecture reduces to one question:

\[
  \boxed{
  A\perp j \ \Longrightarrow\
  A\perp (\mathbb I_{\parallel}\to\mathbb I)
  }
\]

or, equivalently, whether the walking-parallel-pair comparison is a \(j\)-local equivalence.

Fourth, a conditional full theorem is obtained. If the evaluation map

\[
  \eta_A:A\longrightarrow \mathbb I^{\mathbb I^A},
  \qquad
  \eta_A(a)(\varphi)=\varphi(a),
\]

is an embedding---that is, open observations separate points---then \(A\) embeds in an observational algebra, hence is \(\mathbb I\)-separated. Combined with the preceding results, every observationally separated \(j\)-local type is a synthetic predomain.

No proof is found that arbitrary \(j\)-local types are observationally separated, and no valid counterexample is constructed. The most direct counterexample candidate is the \(j\)-local reflection of the walking parallel pair. The manuscript ends with a formalization blueprint for Cubical Agda or Rzk and a model-theoretic search programme in classifying topoi and realizability models.

# Contributions at a glance {-}

\resultbox{\textbf{Headline result.} Subject to the shape and colimit assumptions stated in Chapter 4, the hypothesis of Xue's Conjecture 6.20 already implies all finite Segal conditions and \(\omega\)-chain completeness. After a cofinality argument, the only genuinely unresolved property is \(\mathbb I\)-separation.}

| Question | Status reached here |
|---|---|
| Does \(A\perp j\) imply Segal completeness? | **Yes**, paper-level proof by arrow retracts. |
| Does \(A\perp j\) imply all finite spine conditions? | **Yes**, same proof. |
| Does \(A\perp j\) imply chain completeness? | **Yes**, paper-level proof by colimits and two-out-of-three. |
| Is \(j\)-locality equivalent to finite-spine locality plus chain completeness? | **Yes**, under the stated shape identifications. |
| Does \(A\perp j\) imply Rezk completeness? | **Yes after \(\mathbb I\)-separation**; not independently proved. |
| Does \(A\perp j\) imply \(\mathbb I\)-separation? | **Open here.** This is the exact remaining core. |
| Is the full conjecture proved? | **No.** |
| Is the conjecture disproved? | **No.** No validated countermodel was found. |
| Is the argument formalized? | **No.** Agda/Rzk pseudocode and proof obligations are supplied. |

# Acknowledgements and provenance {-}

The conjecture, definitions of the directed shapes, and the associated Cubical Agda development are due to Runze Xue. The broader orthogonality/repleteness viewpoint comes from synthetic domain theory, particularly work of Reus and Streicher, van Oosten and Simpson, and Sterling and Ye. The synthetic-category-theoretic reading of Segal and Rezk conditions follows Riehl--Shulman and related work. Any new argument in this manuscript should be read as a proposed proof for checking, not as an established result attributable to those authors.

\mainmatter

# Introduction

## The conjecture in one diagram

The relevant map factors through the initial lifting algebra:

\[
\begin{tikzcd}[column sep=large]
\Lambda_\omega \arrow[r,"k",hook]
  & \Delta^\omega \simeq \omega
    \arrow[r,"c",hook]
  & \Delta^\infty \simeq \overline\omega .
\end{tikzcd}
\]

The first map freely supplies all finite composites to an infinite string of composable directed edges. The second adjoins the limit point of an \(\omega\)-chain. Their composite is

\[
  j=c\circ k:\Lambda_\omega\hookrightarrow\Delta^\infty.
\]

For any type \(A\), precomposition produces

\[
  j^*:A^{\Delta^\infty}\longrightarrow A^{\Lambda_\omega}.
\]

The statement \(A\perp j\) means that every infinite spine-shaped diagram in \(A\) has a unique extension across the infinite simplex. Informally, one extension must perform two jobs simultaneously:

1. fill all finite higher simplices, thereby composing paths coherently; and
2. assign a limit to the underlying countable chain.

Xue's conjecture asks whether those jobs force not only composition and limits but also univalence/Rezk completeness and proof-irrelevance of parallel directed paths.

The first two implications are plausible because they are visibly encoded by the factorization. The last two are structurally different. They are quotient-like or separation conditions: they demand that certain distinctions disappear. The main result of this manuscript makes that distinction exact.

## Why the question matters for programming languages

Synthetic domain theory reorganizes classical domain theory so that continuity is built into the ambient logic. Instead of selecting continuous functions from all set-theoretic functions, one works in a universe where every definable map between suitable objects is already continuous. This is useful for denotational semantics because recursion, approximation, partiality, and fixed points can then be handled internally.

The interval or dominance \(\mathbb I\) plays several roles at once. Its points act like semidecidable truth values or opens; maps \(A\to\mathbb I\) act like observations on programs; and maps \(\mathbb I\to A\) generate the intrinsic information order. If a compact orthogonality condition such as \(A\perp j\) characterized predomains, it would give a single reusable interface for semantic domains:

\[
  \text{coherent composition}
  +\text{countable approximation}
  +\text{extensional order}.
\]

For formalized semantics this matters operationally. A single locality structure is easier to transport through dependent products, function spaces, and model constructions than a collection of separately managed laws. It could also make the boundary between categorical semantics and executable type theory more uniform.

The risk is equally important. If the locality condition only constructs an \(\omega\)-complete synthetic category and does not force thinness, then calling every local object a predomain would silently erase proof-relevant computational structure. Nondeterministic choices, witnesses, traces, or multiple refinement proofs could survive as parallel directed paths. Determining whether that can happen is therefore not terminological; it determines what semantic information the proposed axiom forgets.

## The result in conceptual form

Let \(\Local(f)\) denote the class of types right-orthogonal to a map \(f\). Under the canonical colimit identifications, this manuscript proves

\[
  \Local(j)
  =
  \Local(c)\cap\bigcap_{n\ge 0}\Local(j_n).
\]

The right side says exactly:

- every finite composable string has a unique coherent simplex filler; and
- every \(\omega\)-chain has a unique continuous limit extension.

Hence \(j\)-locality is a strong notion of complete Segal object. What is not present in this formula is any explicit generator that identifies parallel arrows. The walking-parallel-pair map

\[
  \rho:\mathbb I_{\parallel}\longrightarrow\mathbb I
\]

is therefore the decisive comparison. The conjecture is equivalent, after the other deductions, to the assertion that every \(j\)-local object is \(\rho\)-local. In localization language:

\[
  \rho\text{ is a }j\text{-local equivalence}.
\]

This reformulation provides both a proof strategy and a disproof strategy. A proof should derive \(\rho\)-locality from \(j\)-locality, perhaps through observational duality or a model-independent density theorem. A disproof should find a \(j\)-local object with two distinct parallel paths, or equivalently show that the \(j\)-local reflection of \(\rho\) is not invertible.

## Claims deliberately not made

This manuscript does not claim that the shape maps and colimit comparison maps have been checked against the exact names and definitional equalities in Xue's Cubical Agda repository. The associated code record is cited by Xue, but it was not available for inspection in the present environment. The proofs are therefore formulated at the invariant categorical/type-theoretic level.

It also does not infer openness merely from a failed proof. In particular, the inability to prove \(\mathbb I\)-separation is not evidence that the conjecture is false. Conversely, the absence of a counterexample is not evidence that it is true. The correct status is a reduction with conditional results.

## Organization

Chapters 2--4 reconstruct the ambient theory, shapes, and assumptions. Chapters 5--8 contain the main paper-level deductions. Chapter 9 reduces the full conjecture to \(\mathbb I\)-separation. Chapter 10 proves the observationally separated case. Chapters 11--13 document failed approaches, model tests, and counterexample searches. Chapters 14--15 give formalization plans and a research roadmap. Appendices contain expanded proofs, shape formulas, and pseudocode.

# Background: synthetic domains as local objects

## Orthogonality

Let \(f:X\to Y\) be a map in a cartesian closed type-theoretic universe. A type \(A\) is **right-orthogonal** or **local** with respect to \(f\) when precomposition is an equivalence:

\[
  f^*:A^Y\xrightarrow{\simeq}A^X,
  \qquad
  f^*(g)=g\circ f.
\]

We write \(A\perp f\), or occasionally \(f\perp A\), depending on convention. This is the special case of map orthogonality in which the right-hand map is \(A\to 1\). Internally, it says that every map \(X\to A\) extends uniquely across \(f\).

Three elementary closure principles drive most of the manuscript.

\begin{lemma}[Closure under equivalence]
If \(A\simeq B\) and \(A\perp f\), then \(B\perp f\).
\end{lemma}

\begin{lemma}[Closure under products]
If \(A_i\perp f\) for every \(i:I\), then \(\prod_{i:I}A_i\perp f\). In particular, if \(A\perp f\), then every power \(A^Z\perp f\).
\end{lemma}

\begin{proof}
Precomposition into a dependent product is computed pointwise:
\[
  \left(\prod_i A_i\right)^Y
  \simeq
  \prod_i A_i^Y
  \xrightarrow{\prod_i f^*}
  \prod_i A_i^X
  \simeq
  \left(\prod_i A_i\right)^X.
\]
A product of equivalences is an equivalence.
\end{proof}

\begin{lemma}[Arrow-retract closure]
If \(f\) is a retract of \(g\) in the arrow category and \(A\perp g\), then \(A\perp f\).
\end{lemma}

\begin{proof}
Contravariant exponentiation sends an arrow retract to a retract of restriction maps. A retract of an equivalence is an equivalence.
\end{proof}

The last lemma will turn the single infinite map \(j\) into every finite spine map \(j_n\).

## Directed paths

Fix a directed interval \(\mathbb I\) with endpoints \(0,1:\mathbb I\). For points \(x,y:A\), the directed path type is

\[
  \operatorname{hom}_A(x,y)
  :=
  \{p:\mathbb I\to A\mid p(0)=x,\ p(1)=y\}.
\]

Constant maps supply identities. Every function \(A\to B\) acts functorially on directed paths by postcomposition. The resulting relation is therefore reflexive and preserved by all definable maps.

The ambient equality type and the directed path type are distinct. Xue works, for simplicity, in an h-set fragment, so ordinary identity types are propositions. Directed hom-types need not be propositions; two different functions \(\mathbb I\to A\) can have the same endpoints. This distinction is exactly why \(\mathbb I\)-separation is a nontrivial axiom.

## Segal, Rezk, separated, and chain-complete types

Let \(\Lambda_2\hookrightarrow\Delta^2\) be the two-edge spine inclusion. A type \(A\) is **Segal** when

\[
  A^{\Delta^2}\xrightarrow{\simeq}A^{\Lambda_2}.
\]

Thus two composable paths have a unique triangular filler, whose diagonal supplies their composite. Higher finite spine conditions similarly encode coherent composites of longer strings. In the ordinary Segal argument, the binary condition generates the higher ones.

Let \(\mathbb E\) be the walking isomorphism shape. A Segal type is **Rezk complete** when it is right-orthogonal to \(\mathbb E\to 1\). This identifies categorical isomorphism with equality of objects in the directed type.

Let \(\mathbb I_{\parallel}\) be the pushout of two copies of \(\mathbb I\) along their endpoints. A map \(\mathbb I_{\parallel}\to A\) is a pair of parallel directed paths. The codiagonal

\[
  \rho:\mathbb I_{\parallel}\longrightarrow\mathbb I
\]

identifies the two copies. A type is **\(\mathbb I\)-separated** when \(A\perp\rho\). Equivalently, the endpoint map

\[
  A^{\mathbb I}\longrightarrow A\times A
\]

is an embedding. In the h-set setting, each directed hom-type is then a proposition.

A Segal, Rezk-complete, \(\mathbb I\)-separated type is a **synthetic poset**. Finally, let

\[
  c:\omega\simeq\Delta^\omega
  \hookrightarrow
  \overline\omega\simeq\Delta^\infty
\]

be the initial-to-final lifting (co)algebra inclusion. A type is **chain complete** when it is right-orthogonal to \(c\). A chain-complete synthetic poset is a **synthetic predomain**.

In symbols,

\[
\Predom(A)
:=
\Seg(A)\wedge\Rezk(A)\wedge\Sep(A)\wedge\CC(A).
\]

## Observational algebras and repleteness

For any type \(X\), its observational algebra is

\[
  \mathcal O(X):=\mathbb I^X.
\]

The product closure of right orthogonality implies that every locality property of \(\mathbb I\) is inherited by every observational algebra. This is the elementary source of many well-behaved semantic domains.

A type is **replete** when it is local with respect to every map with respect to which \(\mathbb I\) is local. Replete objects therefore lie in the smallest exponential ideal/localization class generated by \(\mathbb I\). Sterling and Ye show that spectra and spatial \(\mathbb I\)-algebras are replete in their classifying-topos framework, and consequently inherit the synthetic-poset conditions satisfied by \(\mathbb I\).

The conjecture studied here is stronger in a different direction. It asks whether locality with respect to one particular countable map \(j\) already implies enough repleteness to force all predomain conditions. The source itself warns that this may fail outside observational algebras.

# Directed simplices and spines

## Finite simplices

For \(n\ge 0\), write

\[
  \Delta^n
  =
  \{(i_1,\ldots,i_n):\mathbb I^n
    \mid i_1\ge i_2\ge\cdots\ge i_n\}.
\]

Its vertices are

\[
  v_k=(\underbrace{1,\ldots,1}_{k},
       \underbrace{0,\ldots,0}_{n-k}),
  \qquad 0\le k\le n.
\]

The finite spine \(\Lambda_n\) is the colimit of \(n\) copies of \(\mathbb I\) glued end to end. It has the same vertices but only the adjacent edges

\[
  v_0\to v_1\to\cdots\to v_n.
\]

There is a canonical inclusion

\[
  j_n:\Lambda_n\hookrightarrow\Delta^n.
\]

A map \(\Lambda_n\to A\) is an \(n\)-tuple of composable directed paths. A map \(\Delta^n\to A\) contains those paths together with all composites and higher coherence data encoded by the simplex. Right-orthogonality to \(j_n\) says this coherent extension is unique.

## The initial infinite simplex

The face-padding maps

\[
  s_n:\Delta^n\longrightarrow\Delta^{n+1},
  \qquad
  s_n(i_1,\ldots,i_n)=(i_1,\ldots,i_n,0)
\]

form a sequential diagram. Its colimit is the finite-support infinite simplex

\[
  \Delta^\omega
  \simeq
  \colim_n\Delta^n.
\]

Concretely, it consists of descending sequences in \(\mathbb I\) that become \(0\) after finitely many coordinates. Xue identifies this object with the initial algebra \(\omega\) of the lifting endofunctor.

The finite spine inclusions are compatible with the padding maps. Their colimit is

\[
  k:\Lambda_\omega\longrightarrow\Delta^\omega.
\]

The domain \(\Lambda_\omega\) may be presented as a higher inductive type with vertices \(\operatorname{step}(n)\) and an interval edge from \(\operatorname{step}(n)\) to \(\operatorname{step}(n+1)\). Equivalently, it is the colimit of the finite spines:

\[
  \Lambda_\omega\simeq\colim_n\Lambda_n.
\]

## The final infinite simplex

The full infinite simplex is

\[
  \Delta^\infty
  =
  \{s:\mathbb N\to\mathbb I
    \mid s_n\ge s_{n+1}\}.
\]

It contains \(\Delta^\omega\) by zero padding but also the non-finite points, including the all-ones limit vertex

\[
  v_\infty=(1,1,1,\ldots).
\]

Xue identifies \(\Delta^\infty\) with the final lifting coalgebra \(\overline\omega\). The inclusion

\[
  c:\Delta^\omega\hookrightarrow\Delta^\infty
\]

is the chain-completeness comparison map.

The infinite spine includes by mapping its \(n\)-th vertex to

\[
  v_n=(1^n0^\infty)
\]

and its \(n\)-th edge to the adjacent edge \(v_n\to v_{n+1}\). This gives

\[
  j:\Lambda_\omega\hookrightarrow\Delta^\infty,
  \qquad j=c\circ k.
\]

## What maps from the shapes mean

The three mapping types have different semantic content:

\[
\begin{aligned}
  A^{\Lambda_\omega}
  &\simeq \{\text{infinite composable strings in }A\},\\
  A^{\Delta^\omega}
  &\simeq \{\text{such strings with all finite composites/coherences}\},\\
  A^{\Delta^\infty}
  &\simeq \{\text{coherent strings with a continuous limit point}\}.
\end{aligned}
\]

These descriptions are schematic rather than definitions, but they explain the factorization of restriction maps:

\[
  A^{\Delta^\infty}
  \xrightarrow{c^*}
  A^{\Delta^\omega}
  \xrightarrow{k^*}
  A^{\Lambda_\omega}.
\]

The conjectural leap is from this composition-and-limit structure to path proof-irrelevance.

# Ambient assumptions and proof discipline

## Why assumptions must be explicit

The central diagrams are elementary when drawn externally, but a formal proof lives inside a specific directed type theory. Several points that are harmless on paper become proof obligations in Cubical Agda:

- the finite and infinite shapes may be higher inductive types rather than literal subsets;
- the identification of \(\Lambda_\omega\) with a sequential colimit must respect edge constructors;
- the colimit map \(k\) must agree with the canonical inclusion into \(\Delta^\omega\);
- arrow-retract equations may be propositional rather than definitional;
- the mapping-out universal property must be available at the universe level in use.

The paper-level results will therefore be stated relative to a small package of shape assumptions. These assumptions are intended to isolate the formalization burden, not to conceal it.

## Shape package

\begin{assumption}[Cartesian closed ambient theory]\label{ass:ccc}
The ambient theory has function types, finite limits, the finite shape colimits used to form spines and walking isomorphisms, and the sequential colimits used below. Mapping out of a colimit satisfies its universal property:
\[
  \Map(\colim_i X_i,A)\simeq\liminv_i\Map(X_i,A).
\]
All types under discussion are h-sets, following Xue's simplifying convention.
\end{assumption}

\begin{assumption}[Finite shapes]\label{ass:finite}
For each \(n\), there are shapes \(\Lambda_n,\Delta^n\) and a canonical inclusion \(j_n:\Lambda_n\to\Delta^n\). The vertices and edges satisfy the standard simplicial identities described in Chapter 3.
\end{assumption}

\begin{assumption}[Sequential presentations]\label{ass:colimits}
There are equivalences
\[
  \Lambda_\omega\simeq\colim_n\Lambda_n,
  \qquad
  \Delta^\omega\simeq\colim_n\Delta^n,
\]
and, under these equivalences, \(k:\Lambda_\omega\to\Delta^\omega\) is the colimit of the natural transformation \((j_n)_n\).
\end{assumption}

\begin{assumption}[Final simplex and factorization]\label{ass:factor}
There is an inclusion \(c:\Delta^\omega\to\Delta^\infty\), and the canonical infinite-spine map factors as \(j=c\circ k\).
\end{assumption}

\begin{assumption}[Clamping and truncation maps]\label{ass:clamp}
For each \(n\), the evident maps exist:
\[
\begin{aligned}
  u_n &: \Lambda_n\to\Lambda_\omega,
  &q_n &: \Lambda_\omega\to\Lambda_n,\\
  e_n &: \Delta^n\to\Delta^\infty,
  &p_n &: \Delta^\infty\to\Delta^n,
\end{aligned}
\]
where \(u_n\) includes the first \(n\) edges, \(q_n\) clamps every vertex after \(n\) to \(v_n\), \(e_n\) pads with zeros, and \(p_n\) truncates to the first \(n\) coordinates. They satisfy the equations listed in Theorem 5.1.
\end{assumption}

Assumptions \ref{ass:finite}--\ref{ass:factor} are direct expressions of Xue's constructions. Assumption \ref{ass:clamp} is not quoted as a theorem from the source; it is a proposed elementary construction. In a higher-inductive presentation, \(q_n\) sends each tail edge to the constant path at \(v_n\), so its recursor data are available. The remaining equalities should follow by constructor computation and function extensionality. They have not been machine checked here.

## Logical strength of the arguments

The finite-retract proof uses only function extensionality, the shape maps, and closure of equivalences under retracts. The chain-completeness proof additionally uses sequential colimit universal properties and closure of equivalences under limits. It does **not** require a choice principle for \(\mathbb I\).

This distinction deserves emphasis because Sterling and Ye identify a choice issue in proving that certain localization classes are closed under arbitrary sequential colimits. The present argument is contravariant: it maps *out of* a known colimit into a fixed target. That universal property is part of the definition of the colimit. It does not assert that exponentiation in its covariant argument preserves a colimit.

## A reusable localization lemma

\begin{lemma}[Composite locality]\label{lem:composite}
Let \(X\xrightarrow{k}Y\xrightarrow{c}Z\) and \(j=c\circ k\). For every \(A\),
\[
  j^*=k^*\circ c^*.
\]
Consequently:

1. if \(A\perp k\) and \(A\perp c\), then \(A\perp j\);
2. if \(A\perp j\) and \(A\perp k\), then \(A\perp c\);
3. if \(A\perp j\) and \(A\perp c\), then \(A\perp k\).
\end{lemma}

\begin{proof}
The factorization of restriction maps is associativity of composition. Each implication is two-out-of-three for equivalences.
\end{proof}

Without additional information, locality for a composite does not imply locality for either factor. The finite-retract and colimit arguments provide precisely the missing information for this particular composite.

## Proof ledger

To prevent later deductions from being mistaken for source results, the following ledger will be maintained.

| Label | Claim | Dependence | Status |
|---|---|---|---|
| FR | Every \(j_n\) is an arrow retract of \(j\). | Shape package | Proved here, paper level. |
| FS | \(A\perp j\Rightarrow A\perp j_n\) for all \(n\). | FR | Proved here. |
| SC | \(A\perp j\Rightarrow A\perp k\). | FS + colimits | Proved here. |
| CC | \(A\perp j\Rightarrow A\perp c\). | SC + two-out-of-three | Proved here. |
| DEC | \(A\perp j\iff(A\perp c\land\forall n\,A\perp j_n)\). | Above | Proved here. |
| AS | \(A\perp j\land\Sep(A)\Rightarrow\) antisymmetry/Rezk. | Cofinal maps | Proved here, formal details pending. |
| OBS | \(A\perp j\land\eta_A\text{ embedding}\Rightarrow\Predom(A)\). | AS + observational algebra | Proved conditionally. |
| SEP | \(A\perp j\Rightarrow\Sep(A)\). | None known | Open here. |

# Finite spine conditions are retracts of the infinite one

## Construction of the retract

Fix \(n\ge 0\). Define the maps on vertices by

\[
  u_n(v_m)=v_m\quad(0\le m\le n),
\]

and

\[
  q_n(v_m)=v_{\min(m,n)}\quad(m\in\mathbb N).
\]

On edges, \(u_n\) is the evident inclusion. The clamping map \(q_n\) sends the edge \(v_m\to v_{m+1}\) to

\[
  \begin{cases}
    v_m\to v_{m+1}, & m<n,\\
    \id_{v_n}, & m\ge n.
  \end{cases}
\]

Thus

\[
  q_n\circ u_n=\id_{\Lambda_n}.
\]

For simplices, define zero padding and truncation:

\[
  e_n(i_1,\ldots,i_n)
  =(i_1,\ldots,i_n,0,0,\ldots),
\]

\[
  p_n(s_1,s_2,\ldots)=(s_1,\ldots,s_n).
\]

Descendingness is preserved, and

\[
  p_n\circ e_n=\id_{\Delta^n}.
\]

The key point is compatibility with the spine inclusions. On the first \(n\) edges, inclusion followed by zero padding is the same path in \(\Delta^\infty\):

\[
  j\circ u_n=e_n\circ j_n.
\]

Conversely, truncating the image of an edge in the infinite spine either retains that edge, when it lies among the first \(n\), or turns it into the constant path at the final finite vertex. This is exactly what clamping does:

\[
  j_n\circ q_n=p_n\circ j.
\]

These equations form two arrow morphisms

\[
  (u_n,e_n):j_n\longrightarrow j,
  \qquad
  (q_n,p_n):j\longrightarrow j_n,
\]

whose composite is the identity of \(j_n\).

\begin{theorem}[Finite-spine arrow retract]\label{thm:finite-retract}
Under Assumptions \ref{ass:finite} and \ref{ass:clamp}, every finite spine inclusion \(j_n:\Lambda_n\to\Delta^n\) is a retract of \(j:\Lambda_\omega\to\Delta^\infty\) in the arrow category.
\end{theorem}

\begin{proof}
The required diagram is
\[
\begin{tikzcd}[column sep=huge,row sep=large]
\Lambda_n \arrow[r,"u_n"] \arrow[d,"j_n"']
  & \Lambda_\omega \arrow[r,"q_n"] \arrow[d,"j"]
  & \Lambda_n \arrow[d,"j_n"] \\
\Delta^n \arrow[r,"e_n"']
  & \Delta^\infty \arrow[r,"p_n"']
  & \Delta^n .
\end{tikzcd}
\]
The left and right squares commute by the compatibility equations above. The horizontal composites are identities by clamping after inclusion and truncation after zero padding. Therefore the left-hand arrow is an arrow retract of the middle arrow.
\end{proof}

## Consequence for local types

\begin{corollary}[All finite spine fillers]\label{cor:all-finite}
If \(A\perp j\), then \(A\perp j_n\) for every \(n\ge0\).
\end{corollary}

\begin{proof}
Apply arrow-retract closure to Theorem \ref{thm:finite-retract}.
\end{proof}

\begin{corollary}[Segal completeness]\label{cor:segal}
If \(A\perp j\), then \(A\) is Segal complete.
\end{corollary}

\begin{proof}
Take \(n=2\) in Corollary \ref{cor:all-finite}.
\end{proof}

This proves one of the implications explicitly anticipated but not established in Xue's discussion of Conjecture 6.20.

## Why the retract proof is stronger than a factorization argument

The factorization \(j=c\circ k\) alone cannot imply that \(A\perp j\) gives \(A\perp k\). The finite retracts bypass that problem. Every finite piece of \(k\) is visible as a literal retract of the larger map \(j\), so locality descends before any limiting argument is used.

This has two useful consequences.

First, no global statement about preservation of colimits is needed to obtain binary composition. The Segal result is finite and elementary.

Second, the argument yields all finite spines at once. A \(j\)-local type is not merely binary Segal; it comes equipped with unique fillers for every finite composable chain. Associativity and unit coherence can therefore be read directly from higher simplex restrictions rather than reconstructed only from \(n=2\).

## Sanity checks at small dimensions

For \(n=0\), both \(\Lambda_0\) and \(\Delta^0\) are terminal, and the statement is trivial.

For \(n=1\), \(j_1\) is an equivalence, since the one-edge spine is the interval/simplex itself. The retract construction reduces to inclusion of the first edge and truncation to the first coordinate.

For \(n=2\), the clamping map collapses every edge after the second to the final vertex. Truncation of the infinite simplex retains the first two coordinates. A tail edge lies entirely where those coordinates are \((1,1)\), so it becomes the constant path at \(v_2\). This is the nontrivial compatibility needed for the Segal case.

## Formalization obligations for the retract theorem

A Cubical Agda proof should separate four tasks:

1. define the finite-spine recursor and the prefix inclusion \(u_n\);
2. define \(q_n\) by the infinite-spine HIT recursor, with tail edge data constant at \(v_n\);
3. define \(e_n\) and \(p_n\) on descending sequence records;
4. prove the two square equations and two retraction equations by HIT elimination and function extensionality.

The most likely friction is not mathematical but definitional: the finite spine used in the existing code may be presented as a finite colimit rather than an inductive family with named vertices. In that case, the clamping map should be defined through the colimit eliminator. No use of excluded middle or choice is expected.

# From finite fillers to the initial infinite simplex

## Mapping out of sequential colimits

Assumption \ref{ass:colimits} gives

\[
  \Delta^\omega\simeq\colim_n\Delta^n,
  \qquad
  \Lambda_\omega\simeq\colim_n\Lambda_n.
\]

For any \(A\), the mapping types are therefore limits:

\[
  A^{\Delta^\omega}
  \simeq
  \liminv_n A^{\Delta^n},
  \qquad
  A^{\Lambda_\omega}
  \simeq
  \liminv_n A^{\Lambda_n}.
\]

Naturality identifies the restriction map \(k^*\) with the limit of the finite restriction maps:

\[
\begin{tikzcd}[column sep=huge]
A^{\Delta^\omega} \arrow[r,"k^*"] \arrow[d,"\simeq"']
  & A^{\Lambda_\omega} \arrow[d,"\simeq"]\\
\liminv_n A^{\Delta^n}
  \arrow[r,"\liminv_n j_n^*"']
  & \liminv_n A^{\Lambda_n}.
\end{tikzcd}
\]

A limit of a natural family of equivalences is an equivalence. This can be proved internally by taking the limit of the inverse natural transformation, or externally by the closure of equivalences under limits.

\begin{theorem}[Initial-simplex locality]\label{thm:k-local}
Under Assumptions \ref{ass:ccc}--\ref{ass:colimits}, if \(A\perp j\), then \(A\perp k\).
\end{theorem}

\begin{proof}
By Corollary \ref{cor:all-finite}, each
\[
  j_n^*:A^{\Delta^n}\to A^{\Lambda_n}
\]
is an equivalence. Their limit is therefore an equivalence. Under the colimit mapping equivalences, that limit is \(k^*\).
\end{proof}

## No hidden countable choice

The theorem uses the equivalence

\[
  \Map(\colim_nX_n,A)\simeq\liminv_n\Map(X_n,A),
\]

which is the representable functor's universal property. It does not use

\[
  \left(\colim_n X_n\right)^I
  \stackrel{?}{\simeq}
  \colim_n(X_n^I),
\]

which is a preservation statement and may require boundedness or choice. Conflating these two directions would invalidate the proof analysis. The present argument stays entirely in the safe, contravariant direction.

## An explicit inverse, conceptually

Given an infinite spine map \(a:\Lambda_\omega\to A\), restrict it to every finite prefix \(a_n:\Lambda_n\to A\). Since \(A\perp j_n\), there is a unique extension

\[
  \bar a_n:\Delta^n\to A.
\]

Uniqueness forces the \(\bar a_n\) to be compatible with zero padding: both possible restrictions to \(\Delta^n\) extend the same \(a_n\). The colimit recursor therefore glues them to

\[
  \bar a:\Delta^\omega\to A.
\]

This is the inverse of \(k^*\). The limit proof packages exactly this construction and its coherence.

# Chain completeness follows by two-out-of-three

## The factorization revisited

Recall

\[
  j=c\circ k:
  \Lambda_\omega\xrightarrow{k}\Delta^\omega
  \xrightarrow{c}\Delta^\infty.
\]

Contravariance gives

\[
  j^*=k^*\circ c^*:
  A^{\Delta^\infty}
  \xrightarrow{c^*}A^{\Delta^\omega}
  \xrightarrow{k^*}A^{\Lambda_\omega}.
\]

If \(A\perp j\), then \(j^*\) is an equivalence. Theorem \ref{thm:k-local} says \(k^*\) is also an equivalence. Hence \(c^*\) is an equivalence.

\begin{theorem}[Chain completeness from infinite-spine locality]\label{thm:chain-complete}
Under the shape package, if \(A\perp j\), then \(A\perp c\). Thus every \(j\)-local type is \(\omega\)-chain complete.
\end{theorem}

\begin{proof}
By Theorem \ref{thm:k-local}, \(k^*\) is an equivalence. By hypothesis, \(j^*=k^*\circ c^*\) is an equivalence. Two-out-of-three implies that \(c^*\) is an equivalence.
\end{proof}

This establishes the second implication anticipated in Xue's discussion.

## Interpretation of the extension

Let \(a:\Delta^\omega\to A\) be a coherent finite chain. Restricting along \(k\) gives its underlying infinite spine. Since \(A\perp j\), that spine has a unique extension

\[
  \widehat a:\Delta^\infty\to A.
\]

The restriction \(\widehat a|_{\Delta^\omega}\) and the original \(a\) are both extensions of the same spine across \(k\). Since \(A\perp k\), they are equal. Therefore \(\widehat a\) is the unique extension of \(a\) across \(c\). This elementwise proof is the semantic content of two-out-of-three.

## Exact decomposition theorem

The preceding arguments can be assembled into an equivalence rather than a one-way consequence.

\begin{theorem}[Decomposition of infinite-spine locality]\label{thm:decomposition}
Under the shape package, for every type \(A\), the following are equivalent:

1. \(A\perp j\);
2. \(A\perp c\) and \(A\perp k\);
3. \(A\perp c\) and \(A\perp j_n\) for every \(n\ge0\).

Equivalently,
\[
  \Local(j)
  =
  \Local(c)\cap\Local(k)
  =
  \Local(c)\cap\bigcap_{n\ge0}\Local(j_n).
\]
\end{theorem}

\begin{proof}

\(1\Rightarrow3\): Corollary \ref{cor:all-finite} gives all finite spine localities, and Theorem \ref{thm:chain-complete} gives \(c\)-locality.

\(3\Rightarrow2\): the colimit argument of Theorem \ref{thm:k-local} turns all \(j_n\)-localities into \(k\)-locality.

\(2\Rightarrow1\): restriction along the composite is the composite of two equivalences.

The equivalence between \(2\) and \(3\) follows from the same colimit argument and the fact that each \(j_n\) is an arrow retract of \(k\) as well as of \(j\), using the analogous prefix/retraction diagram with \(\Delta^\omega\) in place of \(\Delta^\infty\).
\end{proof}

\resultbox{\textbf{Interpretation.} The map \(j\) does not hide a mysterious third completion operation. Its local objects are exactly the objects with all finite Segal fillers and with continuous \(\omega\)-chain extension. Any proof of path thinness must therefore show that, in the intended ambient theory, these two forms of completeness jointly imply separation.}

## Relation to the ordinary Segal condition

Theorem \ref{thm:decomposition} uses all finite spine maps. In most Segal settings, locality for \(j_2\) implies locality for every \(j_n\): an \(n\)-simplex can be built by successively gluing triangles, and uniqueness supplies coherence. Let this standard finite Segal induction be available.

\begin{corollary}[Binary formulation]\label{cor:binary-decomp}
Under finite Segal induction,
\[
  A\perp j
  \quad\Longleftrightarrow\quad
  \Seg(A)\wedge\CC(A).
\]
\end{corollary}

This equation should be read with care. \(\Seg(A)\) means the full coherent Segal structure generated by the binary condition, not merely the existence of a chosen binary composition without associativity.

## The easy converse for predomains

A synthetic predomain is Segal and chain complete by definition. Hence, under finite Segal induction, it is local for \(k\) and \(c\), and therefore local for \(j\).

\begin{proposition}[Necessity of infinite-spine locality]\label{prop:predom-local}
Every synthetic predomain is \(j\)-local.
\end{proposition}

\begin{proof}
Segal completeness gives all finite spine fillers and hence \(A\perp k\). Chain completeness gives \(A\perp c\). Therefore \(A\perp c\circ k=j\).
\end{proof}

Thus Xue's conjecture is a proposed characterization, not merely an isolated sufficient condition:

\[
  \Predom(A)
  \quad\stackrel{?}{\Longleftrightarrow}\quad
  A\perp j.
\]

The reverse implication is the only nontrivial direction.

## What has and has not been resolved

At this stage, a \(j\)-local type is known to satisfy

\[
  \Seg(A)\wedge\CC(A).
\]

A synthetic predomain additionally requires

\[
  \Rezk(A)\wedge\Sep(A).
\]

Neither additional property follows by an arrow retract visible in the shape diagram. The maps

\[
  \mathbb E\to1,
  \qquad
  \mathbb I_{\parallel}\to\mathbb I
\]

are quotient/separation comparisons rather than inclusions of finite linear subshapes. The next chapters investigate how much of the Rezk condition can be recovered from chain convergence and whether the separation condition can be reduced further.

# Cofinal subsequences and antisymmetry

## Even and odd endomorphisms of the final simplex

The infinite simplex admits canonical cofinal endomorphisms that select even and odd vertices. In sequence coordinates define

\[
  \epsilon(s_0,s_1,s_2,\ldots)
  =(s_0,s_0,s_1,s_1,s_2,s_2,\ldots)
\]

and

\[
  \omicron(s_0,s_1,s_2,\ldots)
  =(1,s_0,s_0,s_1,s_1,s_2,s_2,\ldots).
\]

These preserve descendingness. On vertices,

\[
  \epsilon(v_n)=v_{2n},
  \qquad
  \omicron(v_n)=v_{2n+1},
\]

and both fix the limit vertex:

\[
  \epsilon(v_\infty)=v_\infty
  =\omicron(v_\infty).
\]

They represent the even and odd cofinal embeddings of \(\omega+1\) into itself.

## Alternating chains

Let \(A\) be Segal and \(\mathbb I\)-separated. Suppose there are directed paths

\[
  p:x\rightsquigarrow y,
  \qquad
  q:y\rightsquigarrow x.
\]

Because \(A\) is \(\mathbb I\)-separated, every two parallel paths are equal. The composites therefore satisfy

\[
  q\circ p=\id_x,
  \qquad
  p\circ q=\id_y,
\]

since each side has the same endpoints as the corresponding identity.

Construct the alternating spine map

\[
  a:\Lambda_\omega\to A
\]

with vertices

\[
  x,y,x,y,\ldots
\]

and edges

\[
  p,q,p,q,\ldots.
\]

If \(A\perp j\), let

\[
  \bar a:\Delta^\infty\to A
\]

be its unique extension, and write

\[
  z:=\bar a(v_\infty)
\]

for the limit point.

Precomposition with \(\epsilon\) selects the even two-step composites. Its restriction to the infinite spine is the constant chain at \(x\), because every two-step composite is \(q\circ p=\id_x\). The constant map \(\Delta^\infty\to A\) at \(x\) is an extension of that constant spine. By uniqueness,

\[
  \bar a\circ\epsilon=\operatorname{const}_x.
\]

Evaluating at \(v_\infty\), which \(\epsilon\) fixes, gives \(z=x\). The odd map similarly gives

\[
  \bar a\circ\omicron=\operatorname{const}_y,
  \qquad z=y.
\]

Therefore \(x=y\).

\begin{theorem}[Cofinal antisymmetry]\label{thm:cofinal-antisym}
Assume the even and odd endomorphisms above are available with the stated compatibility. If \(A\perp j\) and \(A\) is \(\mathbb I\)-separated, then its directed path relation is antisymmetric:
\[
  (x\rightsquigarrow y)\times(y\rightsquigarrow x)
  \longrightarrow (x=y).
\]
\end{theorem}

\begin{proof}
The alternating-chain argument above supplies the equality \(x=z=y\).
\end{proof}

## From antisymmetry to Rezk completeness

In a thin Segal type, an isomorphism consists of paths in both directions; the inverse equations are automatic because the relevant hom-types are propositions. Theorem \ref{thm:cofinal-antisym} identifies the endpoints. Since ordinary equality types are propositions in Xue's h-set setting, this is exactly the object-level content needed for Rezk completeness, and thinness removes nontrivial automorphism ambiguity.

\begin{corollary}[Separated local types are Rezk]\label{cor:sep-rezk}
In Xue's h-set setting, if \(A\perp j\) and \(A\) is \(\mathbb I\)-separated, then \(A\) is Rezk complete.
\end{corollary}

\begin{proof}
Corollary \ref{cor:segal} makes \(A\) Segal. Separation makes each hom-type a proposition. An isomorphism gives paths in both directions, so Theorem \ref{thm:cofinal-antisym} gives equality of endpoints. Thinness implies the isomorphism is the identity transported along that equality. This identifies the map \(A\to A^{\mathbb E}\) as an equivalence.
\end{proof}

\begin{warning}
Without \(\mathbb I\)-separation, the alternating argument does not prove full Rezk completeness. For an isomorphism \(p,q\), even and odd subsequences can identify the endpoints, but nontrivial automorphisms may remain as distinct directed loops. Any claim that the argument proves Rezk independently would be too strong.
\end{warning}

## The full conjecture reduces to separation

Combining the previous chapters yields the central reduction.

\begin{theorem}[Exact remaining core]\label{thm:reduction}
Under the shape package and the h-set convention, Xue's Conjecture 6.20 is equivalent to the statement
\[
  A\perp j
  \quad\Longrightarrow\quad
  A\perp\rho,
  \qquad
  \rho:\mathbb I_{\parallel}\to\mathbb I.
\]
In words: every infinite-spine-local type is \(\mathbb I\)-separated.
\end{theorem}

\begin{proof}
If the displayed implication holds, a \(j\)-local \(A\) is Segal by Corollary \ref{cor:segal}, chain complete by Theorem \ref{thm:chain-complete}, separated by hypothesis, and Rezk by Corollary \ref{cor:sep-rezk}. Hence it is a synthetic predomain.

Conversely, if Conjecture 6.20 holds, every \(j\)-local type is a synthetic predomain and therefore \(\mathbb I\)-separated by definition.
\end{proof}

\resultbox{\textbf{Reduced conjecture.} The unresolved mathematical question is not whether the infinite spine encodes finite composition or countable convergence; it does. The question is whether those two completion properties force the endpoint map \(A^{\mathbb I}\to A\times A\) to be an embedding for every local type.}

# Localization-theoretic formulation

## The walking parallel pair as a local equivalence

Given a map \(j\), call a map \(f:X\to Y\) a **\(j\)-local equivalence** when every \(j\)-local object sees it as an equivalence:

\[
  \forall A\in\Local(j),
  \quad
  f^*:A^Y\xrightarrow{\simeq}A^X.
\]

Theorem \ref{thm:reduction} can then be restated in one line.

\begin{corollary}[Localization form of the conjecture]\label{cor:local-equivalence}
Conjecture 6.20 holds if and only if
\[
  \rho:\mathbb I_{\parallel}\to\mathbb I
\]
is a \(j\)-local equivalence.
\end{corollary}

If a reflective \(j\)-localization \(L_j\) exists, this is further equivalent to

\[
  L_j(\rho):L_j(\mathbb I_{\parallel})
  \xrightarrow{\simeq}
  L_j(\mathbb I).
\]

This is the most concrete target for a formal proof or counterexample. It asks for the result of applying one localization construction to one small map.

## Orthogonality-class inclusion

Let \(\rho\) be the parallel-pair comparison. The conjecture is the class inclusion

\[
  \Local(j)\subseteq\Local(\rho).
\]

The opposite inclusion is neither expected nor needed. A separated type need not have chain limits or Segal composition. The problem is therefore an implication between two localities, not equality of localization classes.

A standard way to prove such an implication is to show that \(\rho\) belongs to the strongly saturated class generated by \(j\), with whatever closure operations are sound in the ambient localization theory. A standard way to disprove it is to produce a \(j\)-local object that detects \(\rho\), namely a type \(A\) for which

\[
  A^{\mathbb I}\longrightarrow A^{\mathbb I_{\parallel}}
\]

fails to be an equivalence.

## A structural warning about linear generators

The map \(j\) is built from a linear chain. The map \(\rho\) identifies two parallel edges. There is no obvious retraction diagram from \(\rho\) to \(j\): clamping and truncation can extract finite linear prefixes, but cannot manufacture a pair of distinct arrows with common endpoints.

This does not prove non-generation. Saturated closure can create maps with very different geometric appearances. It does explain why the successful finite-retract method stops exactly at separation.

## A universal counterexample candidate

Suppose a \(j\)-local reflection exists. The object

\[
  L_j(\mathbb I_{\parallel})
\]

is the free \(j\)-local type generated by two parallel paths. The conjecture says those paths become equal after localization. Therefore:

- if their images remain distinct, this object is a counterexample;
- if they become equal, the unit square may provide the key lemma needed for a general proof.

This candidate is superior to guessing ad hoc models because it is universal. It concentrates the problem into computing a single free completion.

# Observational separation gives a conditional full theorem

## The double-dual evaluation map

For any type \(A\), define its observational double dual

\[
  D(A):=\mathbb I^{\mathbb I^A}.
\]

There is a canonical evaluation map

\[
  \eta_A:A\longrightarrow D(A),
  \qquad
  \eta_A(a)(\varphi)=\varphi(a).
\]

Two points \(a,b:A\) have equal images precisely when every open observation gives the same result:

\[
  \eta_A(a)=\eta_A(b)
  \quad\Longleftrightarrow\quad
  \forall\varphi:A\to\mathbb I,\ \varphi(a)=\varphi(b).
\]

Call \(A\) **observationally separated** when \(\eta_A\) is an embedding. In an h-set universe this means that open observations jointly distinguish points.

Xue's concluding discussion asks whether applying the observation functor twice can provide a useful duality between ordinary types and observational algebras. The source also notes that naive fixed-point sobriety is too restrictive: even the simplices need not be fixed by double dualization. The present argument requires only that \(\eta_A\) be an embedding, not an equivalence.

## The double dual is a predomain

Assume the interval \(\mathbb I\) is a synthetic predomain, as established in Xue's setting under the transfinite Phoa/sobriomorphism hypotheses and in the classifying-topos setting under the relevant quasi-coherence axioms.

Since right orthogonality is closed under products, every power \(\mathbb I^X\) inherits every predomain locality of \(\mathbb I\). Hence

\[
  D(A)=\mathbb I^{\mathbb I^A}
\]

is a synthetic predomain.

\begin{proposition}[Observational double dual is a predomain]\label{prop:double-dual-predom}
If \(\mathbb I\) is a synthetic predomain, then \(D(A)\) is a synthetic predomain for every \(A\).
\end{proposition}

\begin{proof}
Each defining orthogonality condition is inherited by products. The power \(\mathbb I^{\mathbb I^A}\) is an internally indexed product of copies of \(\mathbb I\).
\end{proof}

## Separation inherited from an embedding

Right orthogonality is not generally inherited by arbitrary subobjects. The walking-parallel-pair condition is special enough that a direct argument works.

\begin{lemma}[Embedded subtypes of separated types]\label{lem:embed-sep}
Let \(m:A\to B\) be an embedding of h-set types. If \(B\) is \(\mathbb I\)-separated, then \(A\) is \(\mathbb I\)-separated.
\end{lemma}

\begin{proof}
Let \(p,q:\mathbb I\to A\) have the same endpoints. Then \(m\circ p\) and \(m\circ q\) are parallel paths in \(B\). Since \(B\) is separated,
\[
  m\circ p=m\circ q.
\]
Function extensionality gives \(m(p(i))=m(q(i))\) for every \(i:\mathbb I\). Because \(m\) is an embedding, \(p(i)=q(i)\) pointwise; function extensionality gives \(p=q\). Thus each endpoint fiber of \(A^{\mathbb I}\to A\times A\) is a proposition.
\end{proof}

No extension-in-the-subobject argument is needed: \(\rho\)-locality is exactly uniqueness of parallel paths, so pointwise reflection of equality suffices.

## Conditional resolution

\begin{theorem}[Observationally separated case]\label{thm:observational-case}
Assume the shape package and assume \(\mathbb I\) is a synthetic predomain. Let \(A\) be a type such that

1. \(A\perp j\); and
2. \(\eta_A:A\to\mathbb I^{\mathbb I^A}\) is an embedding.

Then \(A\) is a synthetic predomain.
\end{theorem}

\begin{proof}
By Proposition \ref{prop:double-dual-predom}, \(D(A)\) is a synthetic predomain and hence \(\mathbb I\)-separated. By Lemma \ref{lem:embed-sep}, the embedding \(\eta_A\) makes \(A\) \(\mathbb I\)-separated.

The \(j\)-locality of \(A\) gives Segal completeness by Corollary \ref{cor:segal} and chain completeness by Theorem \ref{thm:chain-complete}. Separation plus \(j\)-locality gives Rezk completeness by Corollary \ref{cor:sep-rezk}. Therefore \(A\) satisfies all four predomain conditions.
\end{proof}

\resultbox{\textbf{Conditional full result.} Xue's conjecture is valid for every \(j\)-local type whose points are separated by maps into the interval. This includes any case where the evaluation map into the observational double dual is known to be monic.}

## Relation to spatiality and repleteness

Sterling and Ye define spatial \(\mathbb I\)-algebras and sober spectra through an observation--spectrum adjunction. They prove that spectra and spatial algebras are replete, and that under their finite quasi-coherence assumptions these objects are synthetic posets. Under countable quasi-coherence they also obtain chain completeness of the interval and hence of replete objects.

For such objects, Theorem \ref{thm:observational-case} is not needed to establish predomain structure; repleteness already transfers every locality of \(\mathbb I\). Its significance is instead diagnostic. It shows exactly which part of spatial/replete reasoning repairs the unrestricted conjecture: observations separate enough structure to rule out parallel-path ambiguity.

The conditional theorem also applies in intermediate situations where full repleteness is unavailable. An embedding into a single observational algebra is much weaker than being local for every map seen as invertible by \(\mathbb I\).

## A stronger but easier corollary

\begin{corollary}[Embedding into any synthetic poset]\label{cor:embed-poset}
Let \(A\perp j\). If there is an embedding \(m:A\to P\) into a synthetic poset \(P\), then \(A\) is a synthetic predomain.
\end{corollary}

\begin{proof}
Lemma \ref{lem:embed-sep} makes \(A\) separated. Apply Theorem \ref{thm:reduction} and the already proved Segal/chain-complete consequences.
\end{proof}

This form may be easier to use in semantics: one can embed denotations into a function space or logical-relation object known to be a synthetic poset.

## The missing observational theorem

The unrestricted conjecture would follow immediately from

\[
  A\perp j
  \quad\Longrightarrow\quad
  \eta_A\text{ is an embedding}.
\]

Call this the **observational separation principle for local types**. It is a clean intermediate conjecture, but it is not proved here.

The principle is stronger than the reduced target in one sense and more structured in another. It implies \(\mathbb I\)-separation by embedding into \(D(A)\), but \(\mathbb I\)-separation alone need not make all points observationally distinguishable. Its advantage is that it connects directly to the duality programme proposed by Xue and to spatiality/repleteness in classifying topoi.

A proof would likely need one of the following:

- a density theorem saying that the infinite spine detects distinct points of a local type through interval-valued maps;
- a Stone-style representation theorem for \(j\)-local objects;
- a construction of enough open observations from the local extension operator;
- a model-specific theorem that all \(j\)-local objects in the relevant universe are spatial or replete.

None of these is currently available in the generality required.

# Where the proof stops

## The exact unsolved lifting problem

Take a pair of parallel paths

\[
  p,q:x\rightsquigarrow y
\]

in a \(j\)-local type \(A\). To prove separation one must show \(p=q\). The \(j\)-locality hypothesis only provides unique extension for maps

\[
  \Lambda_\omega\to A.
\]

A single infinite linear chain can compose arrows and take a limit, but the data \(p,q\) are not composable with one another: both start at \(x\) and end at \(y\). Without a return path \(y\to x\), they cannot be alternated along a spine. This elementary typing obstruction is the practical reason the successful cofinal argument needs separation before it can prove antisymmetry.

The reduced problem can be written as the lifting statement

\[
\begin{tikzcd}[column sep=large,row sep=large]
\mathbb I_{\parallel} \arrow[r,"{(p,q)}"] \arrow[d,"\rho"']
  & A\\
\mathbb I \arrow[ur,dashed,"p=q"'] &
\end{tikzcd}
\]

for every \(j\)-local \(A\). There is no direct map of this square into the defining \(j\)-lifting square known here.

## Why constant chains do not solve it

A tempting argument is to take the constant finite chain at \(x\) and construct two extensions to \(\Delta^\infty\) whose limit transition is \(p\) or \(q\). Uniqueness would then identify them.

This construction requires a map

\[
  \ell:\Delta^\infty\to\mathbb I
\]

that is \(0\) on every finite vertex \(v_n\) but \(1\) at \(v_\infty\). Then \(p\circ\ell\) and \(q\circ\ell\) would be the desired extensions. But \(\ell\) is a discontinuous ``jump at infinity.'' Chain completeness of \(\mathbb I\) is precisely the assertion that a map out of \(\Delta^\omega\) has only its continuous extension; the constant-zero chain must extend constantly. Therefore the needed \(\ell\) is unavailable in the intended models.

The failure is instructive. The most direct uniqueness proof for parallel paths would rely on a noncontinuous test that synthetic domain theory is designed to exclude.

## Why a finite retract is unavailable

For finite spine inclusions, clamping and truncation produced an arrow retract. An analogous retraction would require maps

\[
  \mathbb I_{\parallel}\rightleftarrows\Lambda_\omega,
  \qquad
  \mathbb I\rightleftarrows\Delta^\infty
\]

that preserve the two parallel branches through the inclusion. A linear spine has no place to store two noncomposable edges with the same endpoints. Any map into the spine must either identify the branches or place them at different positions, which changes their endpoints. The arrow-retract method therefore cannot transfer locality to \(\rho\) in the same elementary way.

This is not a proof that no more elaborate arrow retract exists in the ambient homotopy theory. It is a proof that the straightforward vertex-and-edge construction used for \(j_n\) cannot work.

## Why a codiagonal construction stalls

Another standard localization technique is to obtain a quotient map as the codiagonal of a pushout of a generating cofibration. Doubling a simplex along its spine creates two top-dimensional fillers sharing the same boundary. One might hope to retract the resulting codiagonal onto \(\rho\).

At dimension two, however, the two candidate triangle retractions must agree on the shared spine. To send their diagonals to distinct parallel copies of \(\mathbb I\), they would need incompatible behavior on that common boundary. No coherent retraction was found. Higher dimensions reproduce the same mismatch: the generator controls alternative *fillers* for one composable boundary, while \(\rho\) controls alternative *one-dimensional arrows* with common endpoints.

This failed construction should be formalized before being treated as definitive. A sophisticated anodyne or join construction could circumvent the naive retraction.

## Why higher groupoids are not immediate counterexamples

A nontrivial groupoid would be an obvious object with Segal composition and nontrivial isomorphisms. But Xue explicitly restricts to h-set types for simplicity. Ordinary equality therefore has no higher loops, and a proposed counterexample must use multiple directed maps \(\mathbb I\to A\), not homotopical identity paths of \(A\).

Moreover, \(j\)-locality includes chain continuity, which fails in the ordinary simplicial nerve model with the naive infinite ordinal: a constant chain can jump to a new object at the limit. Thus the nerve of an arbitrary category cannot be imported as a counterexample without first verifying all SDT interval and continuity axioms.

## What would count as a complete solution

A complete positive solution must provide a valid derivation of \(\rho\)-locality for arbitrary \(j\)-local types, with all universe and shape assumptions stated and preferably formalized.

A complete negative solution must provide:

1. a model of the relevant ambient axioms, including the interval principles used by Xue;
2. a type \(A\) in that model with \(A\perp j\); and
3. two distinct parallel directed paths in \(A\), or another explicit failure of predomain structure.

An object that is merely Segal and chain-complete in an unrelated category is not enough. The ambient model is part of the claim.

# Failed proof attempts in detail

## Attempt 1: derive both factors from the composite directly

**Idea.** Since \(j=c\circ k\), try to use two-out-of-three to infer both \(k\)- and \(c\)-locality from \(j\)-locality.

**Failure.** Two-out-of-three requires one factor in addition to the composite. A composite equivalence does not make either factor an equivalence in general.

**Repair.** The finite-arrow-retract theorem proves each finite component of \(k\) local; the colimit theorem then proves \(k\)-locality. Only after that does two-out-of-three give \(c\)-locality. This repaired attempt becomes Chapters 5--7.

## Attempt 2: use a jump at infinity

**Idea.** Encode a parallel path as an alternative limit extension of a constant chain.

**Failure.** It requires a discontinuous characteristic map that distinguishes the limit point from all finite approximants. Such a map contradicts chain completeness of the interval.

**Lesson.** Limit uniqueness cannot identify arbitrary finite-dimensional path data unless that data can be approximated continuously along the chain.

## Attempt 3: alternate the parallel paths

**Idea.** Put \(p,q,p,q,\ldots\) on successive edges and compare even and odd cofinal subsequences.

**Failure.** Parallel paths \(p,q:x\to y\) are not composable. The target of \(p\) is not the source of \(q\).

**Repair in a special case.** If a return path \(r:y\to x\) is available and separation identifies composites appropriately, alternating paths prove antisymmetry. This becomes Theorem \ref{thm:cofinal-antisym}. It does not prove separation itself.

## Attempt 4: prove Rezk before separation

**Idea.** Apply the alternating-chain argument to an isomorphism \(p:x\to y\), \(q:y\to x\), where composites are identities by definition.

**Partial success.** Even and odd cofinal subsequences force equality of the endpoint objects, provided the shape calculations are accepted.

**Failure.** Full Rezk completeness also rules out nontrivial automorphism data over an equality. Without thin hom-types, endpoint equality alone does not identify the isomorphism with the identity. The argument therefore proves only a skeletal/antisymmetry component, not the complete Rezk lifting property.

**Repair.** Once \(\mathbb I\)-separation is assumed, automorphism ambiguity disappears and the argument proves Rezk completeness.

## Attempt 5: inherit all locality through a subobject

**Idea.** Embed \(A\) into \(D(A)\), a predomain, and claim every predomain property is inherited by subobjects.

**Failure.** Right lifting properties are generally not inherited by subobjects because fillers constructed in the ambient object may leave the subobject.

**Repair.** Use only the special fact that \(\mathbb I\)-separation is uniqueness of parallel paths. An embedding reflects pointwise equality, so this one property is inherited. Segal and chain completeness come independently from \(j\)-locality. Rezk follows from separation plus the cofinal argument.

## Attempt 6: use ordinary category nerves as counterexamples

**Idea.** The nerve of a category is local for finite spine inclusions and can have parallel arrows.

**Failure.** The map \(j\) includes a limit point. In the ordinary nerve of \(\omega+1\), a constant chain can admit many noncontinuous cocone extensions. Hence ordinary nerves are generally not \(j\)-local. The naive simplicial model also fails the intended chain-completeness axiom for the interval.

**Lesson.** Any counterexample must live in a model where all definable maps obey the intended continuity, not merely in a Segal model.

# Model diagnostics

## Purpose of model tests

A model test is not a proof of the conjecture unless it covers every intended model, and it is not a counterexample unless it satisfies all ambient assumptions. Its purpose is narrower: to expose which part of an argument uses continuity, thinness, spatiality, or higher categorical structure.

Four diagnostic environments are useful.

## Ordinary sets with a two-point interval

Take \(\mathbb I=\{0<1\}\) in ordinary Set and define directed paths as arbitrary functions \(\mathbb I\to A\). Then a path is simply an ordered pair of points, and every two points are connected by exactly one function with those endpoints. This makes every type path-thin, but it fails the intended interval theory: not every endomap \(\mathbb I\to\mathbb I\) is monotone, and the Phoa interpolation principle fails because the endpoint values \((1,0)\) occur.

This environment is therefore too classical and too discontinuous. It should not be used to validate the conjecture. It does show why the interval axioms matter: they remove functions that reverse information order.

## Ordinary simplicial nerves

Let \(\mathbb I=\Delta^1\) in simplicial sets. Finite spine locality characterizes nerves of categories, so parallel arrows and nontrivial isomorphisms are abundant. This appears at first to refute the conjecture.

The infinite map changes the conclusion. If \(\Delta^\infty\) is the nerve of \(\omega+1\), a map from it into a category nerve is an arbitrary functor \(\omega+1\to C\). Restricting to \(\omega\) forgets the endpoint and its cocone. Even the constant chain at \(x\) can be extended using any arrow \(x\to y\). Hence a nerve local for this infinite inclusion would have no nonidentity outgoing arrows. More importantly, the interval itself admits a jump from finite \(0\)'s to \(1\) at infinity, so it is not chain complete in the SDT sense.

Thus the ordinary simplicial model separates the two ingredients sharply:

- finite spine locality alone permits arbitrary categories;
- chain continuity rules out discontinuous endpoint choices.

It does not decide whether chain continuity also kills parallel arrows in a genuine SDT model.

## Posetal domain models

In a conventional category of dcpos with the Sierpinski dcpo as interval, a Scott-continuous map \(\mathbb I\to A\) is determined by an ordered pair \(x\le y\). Parallel paths are automatically equal. In such a setting \(\mathbb I\)-separation is built in, so the reduced conjecture holds trivially.

This is a valuable soundness check for the positive direction, but it cannot detect the difficult case. Xue's type-theoretic setting deliberately allows general types whose directed path spaces need not be propositions.

## Spatial and replete classifying-topos models

Sterling and Ye construct broad classes of higher sheaf models from distributive-lattice classifiers. In their framework, spectra and spatial \(\mathbb I\)-algebras are replete. Under finite quasi-coherence assumptions they are synthetic posets; under the countable assumptions the interval is chain complete, so these objects are predomain-like as well.

For this spatial/replete region, the conjecture is safe: any \(j\)-locality needed is only one among many inherited locality properties. The unresolved region consists of arbitrary objects that are \(j\)-local but not known to be spatial, sober, or replete.

This suggests a model-theoretic attack:

1. work in a classifying topos satisfying the interval and countable quasi-coherence axioms;
2. construct the internal \(j\)-localization;
3. determine whether every local object is replete or at least \(\mathbb I\)-separated;
4. if not, extract a concrete nonspatial local object.

The source theorem that spectra and spatial algebras are synthetic posets cannot simply be extended to all objects without an additional argument. Doing so would assume the missing conclusion.

## Realizability and independence warnings

Classical SDT literature contains several notions---complete, well-complete, regular complete, replete---that coincide under some axioms and diverge in others. Van Oosten and Simpson construct models where familiar closure principles fail; for example, complete objects need not be closed under lifting in a modified realizability model, and natural numbers may fail well-completeness in a Grothendieck-topos model even when a two-point object has it.

These results do not directly settle Xue's directed-path conjecture, whose shapes and interval axioms are newer. They warn against assuming that one countable completeness condition automatically generates every desired locality. A negative result may be model-dependent, and the exact ambient axioms must be recorded.

## A comparison table

| Environment | Finite Segal structure | Chain continuity | Parallel paths | Diagnostic value |
|---|---:|---:|---:|---|
| Ordinary Set, two-point interval | Degenerate | No intended SDT continuity | Usually thin for endpoint-fixed functions | Rejects missing interval axioms. |
| Simplicial nerves | Yes | Fails at the limit point | Abundant | Shows finite Segal is insufficient. |
| DCPOS/Sierpinski | Yes in posetal form | Yes | Automatically thin | Positive but cannot test separation. |
| Spatial/replete classifying-topos objects | Yes | Yes under countable axioms | Thin by repleteness | Confirms conditional theorem. |
| Arbitrary local objects in SDT topoi | By this manuscript | By this manuscript | Unknown | Exact frontier. |

# Candidate counterexamples

## The walking parallel pair itself

The smallest visibly non-separated type is \(\mathbb I_{\parallel}\), obtained by gluing two intervals along their endpoints. Its two canonical paths are distinct unless the pushout degenerates. It has no intended nontrivial composable chain beyond one transition, so one might hope that every countable chain is eventually stationary and therefore convergent.

This intuition is insufficient for three reasons.

First, internal chains need not come with a decidable stage at which they become stationary. A transition may be governed by a semidecidable proposition.

Second, choosing which parallel branch occurs at the transition can require data that must be transported to the limit.

Third, the raw pushout need not be Segal: even compositions with identities require unique simplex fillers, and these fillers are not automatically present merely because the underlying directed graph has no long paths.

Consequently, no claim is made here that \(\mathbb I_{\parallel}\perp j\). It is a test object, not a counterexample.

## The free Segal and chain completion

A better candidate is obtained in stages. Start with the walking parallel pair, freely impose finite Segal fillers, then freely impose \(c\)-locality. By Theorem \ref{thm:decomposition}, the result should be the \(j\)-local reflection when these localizations exist and commute appropriately.

Denote the result schematically by

\[
  A_{\parallel}:=L_cL_{\mathrm{Seg}}(\mathbb I_{\parallel}).
\]

There are two possibilities:

- the localization identifies the parallel generators, supporting the conjecture;
- the generators survive, yielding a universal counterexample.

The construction resembles the free \(\omega\)-complete category on a parallel pair, but ordinary categorical intuition is unreliable because the synthetic continuity of the interval constrains the completion.

## A finite acyclic category intuition

Consider the ordinary category with two objects \(x,y\), two arrows \(p,q:x\to y\), and no other nonidentity arrows. Every infinite composable chain is eventually stationary. If continuous extension only records eventual behavior, it would seem that the nerve should be chain complete while retaining \(p\ne q\).

The obstruction is the constant chain at \(x\). In an ordinary \(\omega+1\) nerve it can jump to \(y\) through either \(p\) or \(q\), so uniqueness fails. A genuine SDT model should exclude such jumps. Whether it still admits an internal realization of the finite category with the desired path object is unclear.

This intuition suggests where a countermodel might live: a topology should enforce continuity of object-valued chains while retaining proof-relevant one-step transition data. Presheaves or sheaves enriched over a domain-like base are natural places to search.

## Nonspatial local objects

The conditional theorem shows that any counterexample must fail observational separation. Therefore its distinct parallel paths cannot be detected strongly enough by maps into \(\mathbb I\). In particular, a counterexample must lie outside the well-behaved spatial/replete fragment unless observational separation and spatiality diverge in the model.

This gives a practical filter:

\[
  \text{counterexample}
  \Rightarrow
  \text{\(j\)-local, non-\(\mathbb I\)-separated, non-observationally-separated}.
\]

Searching among powers of \(\mathbb I\), spectra, or spatial algebras cannot succeed because those objects are already synthetic posets.

## Quotients invisible to observations

A generic way to destroy observational separation is to construct distinct points or paths that all maps to \(\mathbb I\) identify. In topos language these may arise from dense quotients, non-sober spaces, or objects outside the reflective hull generated by \(\mathbb I\).

One candidate pattern is:

1. take a replete predomain \(P\);
2. form an internal relation that duplicates one directed path without changing any interval-valued observation;
3. quotient or glue so that the duplicate paths remain distinct internally;
4. test whether \(j\)-locality survives.

The final step is difficult because local objects are closed under limits, not arbitrary colimits or quotients. The quotient is likely to leave the local class, which is why the free local reflection is the correct follow-up.

## Model-theoretic counterexample criterion

A model \(\mathcal E\) refutes the conjecture precisely when the internal map \(\rho\) is not a \(j\)-local equivalence. Externally, this means there exists a \(j\)-local object \(A\in\mathcal E\) for which

\[
  \mathcal E(\mathbb I,A)
  \longrightarrow
  \mathcal E(\mathbb I_{\parallel},A)
\]

is not an isomorphism, with the internal statement interpreted in all contexts. An external global pair of paths is sufficient but not necessary; failure may appear only after pulling back to a context.

This contextual point matters for proof assistants. Testing only closed terms may miss an internal failure of embedding.

# Literature map

## Xue's transfinite Phoa programme

Xue develops finite dual simplices and spines, establishes higher Phoa principles, constructs the initial and final lifting (co)algebras as \(\Delta^\omega\) and \(\Delta^\infty\), and defines the infinite spine \(\Lambda_\omega\). Evaluation on vertices identifies maps from \(\Delta^\omega\) and from \(\Lambda_\omega\) into the interval with appropriate infinite simplices. These results motivate the sobriomorphism

\[
  \Lambda_\omega\trianglelefteq\Delta^\omega
\]

and the completeness conjecture.

The source proves that if the infinite spine spans the final simplex observationally, then the interval is a synthetic domain. It then proposes Conjecture 6.20 for arbitrary types and explicitly notes two limitations: the conjecture may be false, and the route from Phoa to transfinite Phoa relies strongly on the lattice structure of the interval. The source expects Segal and chain completeness under suitable conditions, which Chapters 5--7 establish from the shape package.

## Reus--Streicher orthogonality and repletion

Reus and Streicher formulate general synthetic domain theory in constructive type theory, emphasizing logical/orthogonality characterizations rather than external order theory. Their notion of replete object captures closure under all maps inverted by the chosen Sierpinski object. This is conceptually stronger than completeness with respect to one chain inclusion.

The distinction between local for one generator and replete for the entire interval-generated class is central here. The conditional observational theorem can be read as a partial bridge from one-generator locality to an interval-controlled embedding.

## Van Oosten--Simpson countermodels

Van Oosten and Simpson compare axiom systems and construct realizability and Grothendieck-topos models separating completeness principles. Their results demonstrate that SDT closure properties can be independent and that the exact definition of the initial lifting algebra matters. This manuscript uses those results as methodological caution, not as a direct counterexample.

A productive next step is to translate \(j\), \(\rho\), and Xue's interval axioms into their model frameworks and ask whether known complete-but-not-replete objects are \(j\)-local and non-separated.

## Sterling--Ye classifying topoi

Sterling and Ye derive SDT axioms from synthetic quasi-coherence in classifying topoi. Their work supplies:

- a duality between spatial algebras and sober spaces;
- repleteness of spectra and spatial algebras;
- finite locality properties making the interval a synthetic poset;
- countable locality making the interval chain complete;
- a broad family of higher sheaf models.

Their Theorem 9.13, that spectra and spatial algebras are synthetic posets under finite quasi-coherence, directly supports the observationally separated region of this manuscript. Their discussion of choice and sequential colimits also clarifies why the mapping-out argument in Chapter 6 should be kept distinct from closure of local classes under covariant colimits.

## Riehl--Shulman synthetic categories

Riehl and Shulman develop a directed type theory in which Segal and Rezk conditions express synthetic \(\infty\)-categorical structure. The finite spine maps used here belong to that general synthetic-category-theoretic vocabulary. The conjecture can therefore be understood as asking whether a specific countable completeness generator collapses a synthetic category to a synthetic poset.

The reduction to \(\rho\)-locality makes the categorical content transparent: the missing step is not composition but local thinness.

## Proof assistants

Xue's main constructions are formalized in Cubical Agda. Cubical Agda supplies higher inductive types, path types, and computational univalence, but directed paths are encoded using a separate synthetic interval inside the theory. Rzk, by contrast, is designed for synthetic \(\infty\)-category theory and may express simplices and directed extension types more natively. A split formalization is plausible:

- Cubical Agda to reuse the existing interval, lattice, and transfinite Phoa development;
- Rzk to verify the abstract shape/retract/cofinality lemmas;
- a comparison layer to ensure the assumptions match.

No such formalization is completed here.

# Formalization blueprint

## Target architecture

The proposed formal development should have five layers.

1. **Abstract orthogonality.** Definitions and closure lemmas for local types, arrow retracts, composites, products, and diagram limits.
2. **Finite and infinite shapes.** Prefix, clamp, padding, truncation, and colimit comparison maps.
3. **Main decomposition.** Formal proofs of finite locality, \(k\)-locality, and \(c\)-locality.
4. **Cofinal subsequences.** Even/odd maps of \(\Delta^\infty\) and the antisymmetry theorem under separation.
5. **Reduced conjecture interface.** The walking-parallel-pair map and equivalent formulations of the remaining problem.

The first and third layers are largely ordinary homotopy type theory. The second and fourth depend on the exact directed-shape implementation. The fifth should remain abstract so that different model constructions can instantiate it.

## Core definitions

The following is schematic Cubical Agda-style pseudocode. Names and universe levels must be adapted to the source repository.

```agda
isLocal : {X Y : Type} -> (f : X -> Y) -> Type -> Type
isLocal {X} {Y} f A = isEquiv (precomp f A)

precomp : {X Y A : Type} -> (X -> Y) -> (Y -> A) -> (X -> A)
precomp f g = g . f

record ArrowMap {X Y X' Y' : Type}
                (f : X -> Y) (g : X' -> Y') : Type where
  field
    left   : X -> X'
    right  : Y -> Y'
    square : g . left == right . f

record ArrowRetract {X Y X' Y' : Type}
                    (f : X -> Y) (g : X' -> Y') : Type where
  field
    into : ArrowMap f g
    back : ArrowMap g f
    left-retract  : ArrowMap.left back .
                    ArrowMap.left into == id
    right-retract : ArrowMap.right back .
                    ArrowMap.right into == id
```

The first reusable theorem is:

```agda
local-of-arrow-retract :
  ArrowRetract f g -> isLocal g A -> isLocal f A
```

A robust proof should avoid unfolding `isEquiv` repeatedly. Instead, build a general lemma that a retract of an equivalence is an equivalence and let contravariant precomposition construct the retract.

## Finite prefix and clamp

Assume finite spines have vertices and edges indexed by `Fin (suc n)` and `Fin n`. The maps should behave as follows.

```agda
prefix : (n : Nat) -> Lambda n -> Lambda omega
prefix n (vertex k) = vertex (toNat k)
prefix n (edge k i) = edge (toNat k) i

clamp : (n : Nat) -> Lambda omega -> Lambda n
clamp n (vertex m) = vertex (minFin m n)
clamp n (edge m i) with m <? n
... | yes m<n = edge (bounded m m<n) i
... | no  n<=m = vertex (last n)
```

For a HIT spine, the last line is the constant interval path at the final vertex. Endpoint computation obligations verify that it matches the images of both edge endpoints.

The simplex maps are pointwise.

```agda
padZero : (n : Nat) -> Delta n -> DeltaInf
padZero n x k with k <? n
... | yes k<n = x (bounded k k<n)
... | no  n<=k = zero

truncate : (n : Nat) -> DeltaInf -> Delta n
truncate n x k = x (toNat k)
```

Descendingness proofs use the corresponding proof carried by `x`; the boundary case for zero padding uses `zero` as the least element.

## Arrow square equations

The essential statements are:

```agda
prefix-square :
  jInf . prefix n == padZero n . jFinite n

clamp-square :
  jFinite n . clamp n == truncate n . jInf

clamp-prefix : clamp n . prefix n == id
truncate-pad : truncate n . padZero n == id
```

The finite-spine retract then becomes a record value.

```agda
finite-retract : (n : Nat) ->
  ArrowRetract (jFinite n) jInf
```

This theorem should be proved before importing any domain-theoretic axioms. It is a combinatorial fact about the shapes.

## Sequential colimit comparison

The next layer requires explicit equivalences

```agda
LambdaOmega-colim :
  SequentialColim finiteLambdaDiagram ~= LambdaOmega

DeltaOmega-colim :
  SequentialColim finiteDeltaDiagram ~= DeltaOmega
```

and a naturality theorem that the colimit of finite `j` maps is the canonical `k`.

```agda
k-is-colim-j :
  colimMap finiteJNaturalTransformation
  == transportMap LambdaOmega-colim DeltaOmega-colim k
```

The general mapping-out theorem should yield:

```agda
mapOutSeqColim :
  (SequentialColim D -> A) ~= Limit (fun n -> D n -> A)
```

From this, define:

```agda
local-k-of-local-j :
  isLocal jInf A -> isLocal k A
```

The proof flow is:

```agda
local-jInf
  -> ((n : Nat) -> isLocal (jFinite n) A)
  -> isEquiv (limitMap (fun n -> precomp (jFinite n) A))
  -> isLocal k A
```

The middle implication uses finite retracts. The final implication uses the mapping-out equivalences and `k-is-colim-j`.

## Chain completeness

The factorization should be represented as a path of functions:

```agda
j-factor : jInf == c . k
```

Then:

```agda
local-c-of-local-j :
  isLocal jInf A -> isLocal c A
local-c-of-local-j h =
  equiv-2outof3-right
    (local-k-of-local-j h)
    (transport isLocal j-factor h)
```

The exact two-out-of-three lemma depends on the library representation of equivalence. It may be simpler to write an explicit inverse for `precomp c` by composing the inverse of `precomp j` with `precomp k`.

## Decomposition theorem

```agda
local-j-iff :
  isLocal jInf A
  ~= (isLocal c A * ((n : Nat) -> isLocal (jFinite n) A))
```

The forward direction is Chapters 5--7. The backward direction obtains `isLocal k A` from the finite family and composes with `isLocal c A`.

Formalizing this equivalence is more useful than merely proving two implications. Downstream developments can pattern-match on a single `j`-locality proof to obtain both operations and can construct a `j`-locality proof from separately implemented Segal and limit structures.

## Even and odd maps

On descending sequences:

```agda
even : DeltaInf -> DeltaInf
even s (2 * n)       = s n
even s (2 * n + 1)   = s n

odd : DeltaInf -> DeltaInf
odd s zero            = one
odd s (2 * n + 1)     = s n
odd s (2 * n + 2)     = s n
```

A library implementation should avoid arithmetic pattern overlap by defining a helper from `Nat` parity. Required equations include:

```agda
even-vertex : even (vertex n) == vertex (2 * n)
odd-vertex  : odd  (vertex n) == vertex (2 * n + 1)

even-infty : even infinityVertex == infinityVertex
odd-infty  : odd  infinityVertex == infinityVertex
```

The difficult statement is not the vertex formula but the restriction of an extended alternating chain along the infinite spine. It must compute two-edge composites. A proof will likely use the uniqueness part of finite Segal locality to identify the induced long edge with the composite.

## Antisymmetry theorem

A useful interface for separation is:

```agda
isISeparated : Type -> Type
isISeparated A = isEmbedding (endpoints {A = A})
```

Then:

```agda
local-separated-antisymmetric :
  isLocal jInf A ->
  isISeparated A ->
  (x y : A) ->
  hom x y -> hom y x -> x == y
```

The proof constructs the alternating spine by HIT recursion, obtains its extension using the inverse of `precomp jInf`, and proves its even and odd restrictions equal constant extensions.

A separate theorem should convert thin Segal antisymmetry into the exact Rezk orthogonality definition used by the repository:

```agda
thin-segal-antisym-to-rezk :
  isSet A ->
  isSegal A ->
  isISeparated A ->
  isAntisymmetric A ->
  isRezk A
```

This conversion should not be left implicit; it is one of the places where differing definitions of Rezk completeness can hide a gap.

## Observational theorem

```agda
DoubleDual : Type -> Type
DoubleDual A = (A -> I) -> I

eta : A -> DoubleDual A
eta a phi = phi a

observational-case :
  isPredomain I ->
  isLocal jInf A ->
  isEmbedding (eta {A = A}) ->
  isPredomain A
```

The key local lemma is:

```agda
embedding-reflects-I-separated :
  isEmbedding m ->
  isISeparated B ->
  isISeparated A
```

No claim should be made that an embedding reflects arbitrary right-orthogonality.

## Reduced conjecture as a module signature

The remaining open statement can be isolated so that all consequences compile conditionally.

```agda
module ReducedConjecture
  (local-j-to-separated :
    {A : Type} -> isLocal jInf A -> isISeparated A)
  where

  xue620 : {A : Type} -> isLocal jInf A -> isPredomain A
  xue620 h = record
    { segal    = local-j-to-segal h
    ; rezk     = local-separated-to-rezk h
                     (local-j-to-separated h)
    ; separated = local-j-to-separated h
    ; complete = local-j-to-complete h
    }
```

This organization makes the mathematical status visible in the codebase. All proved components remain usable even while the final parameter is open.

## Rzk variant

In Rzk, extension types can state locality directly. The finite-spine retract and even/odd maps may be shorter because simplices, horns, and directed homs are native. A possible workflow is:

1. define \(\Lambda_\omega\), \(\Delta^\omega\), and \(\Delta^\infty\) as external higher inductive shapes or imported axioms;
2. prove the arrow-retract theorem using extension-type equivalences;
3. prove the decomposition abstractly;
4. export the result as a theorem schema applicable to Xue's Cubical Agda model.

The limitation is that Rzk's treatment of the final lifting coalgebra and countable HITs may require additional library work. As of August 2026, this should be checked against the current implementation rather than assumed.

## Test suite

A formal development should include negative tests preventing accidental strengthening:

- verify that the proof of chain completeness does not import choice;
- ensure that `embedding-reflects-I-separated` is not generalized to arbitrary locality;
- keep the Rezk theorem parameterized by separation until the exact conversion is proved;
- construct an ordinary Segal example showing that finite spine locality alone does not imply separation;
- mark the reduced-conjecture parameter as a postulate only in a separate experimental module.

# Research programme

## Phase I: verify the partial theorems

The first phase is finite and should be attempted before searching for a countermodel.

### Task 1: formalize the finite arrow retracts

This is the lowest-risk contribution. It should settle whether any overlooked orientation or constructor issue invalidates Theorem \ref{thm:finite-retract}. Expected output:

\[
  \forall n,\quad j_n\text{ is an arrow retract of }j.
\]

Even if the full conjecture fails, this theorem remains useful.

### Task 2: formalize the colimit comparison

Prove that the HIT \(\Lambda_\omega\) is the sequential colimit of finite spines in the exact source development, and that \(k\) is the induced colimit map. Expected output:

\[
  A\perp j\Rightarrow A\perp k.
\]

This is the most important unverified coherence point in the manuscript.

### Task 3: formalize two-out-of-three chain completeness

Once Task 2 compiles, the chain-completeness result should be short. The final theorem should expose the exact factorization path used.

### Task 4: formalize cofinal antisymmetry

Define even and odd sequence maps, prove they fix the limit vertex, and check the alternating-chain restriction. This task may reveal whether the sequence formulas correspond to maps of the directed shapes in the precise implementation.

## Phase II: attack separation constructively

### Route A: observational separation

Try to prove

\[
  A\perp j\Rightarrow\eta_A\text{ is an embedding}.
\]

A possible strategy is contraposition. Given \(a\ne b\), construct an observation \(A\to\mathbb I\) distinguishing them by using the local extension operator to close a finite separating predicate under composition and chain limits. The obstacle is that the ambient theory may not provide any initial finite separating predicate.

A weaker target is enough:

\[
  A\perp j\Rightarrow A\hookrightarrow P
\]

for some synthetic poset \(P\), not necessarily the full double dual.

### Route B: compute the local reflection of the parallel pair

Construct \(L_j(\mathbb I_{\parallel})\) by a small-object or higher-inductive localization and inspect whether the two generators become equal. The localization can be staged using Theorem \ref{thm:decomposition}:

1. free finite Segal completion;
2. free \(\omega\)-chain completion.

If neither stage identifies the generators and the composite remains non-separated, the result is a canonical counterexample.

### Route C: saturation proof

Show that \(\rho\) lies in the \(j\)-local-equivalence class. Candidate operations include pushouts, retracts, transfinite composition, joins, diagonals, and pullback-stable closure. The naive codiagonal attempt failed, but a join theorem might turn linear convergence into path uniqueness.

A successful proof must specify which localization theorem is used and verify its hypotheses in the nonclassical type theory.

### Route D: encode parallel paths as limits in a path object

Because powers preserve \(j\)-locality, \(A^{\mathbb I}\) is \(j\)-local whenever \(A\) is. Parallel paths \(p,q\) are points in one endpoint fiber

\[
  F_{x,y}:=\{r:A^{\mathbb I}\mid r(0)=x,r(1)=y\}.
\]

If this fiber were closed under the relevant local structure and if \(p,q\) could be connected by an alternating or approximation chain inside it, chain uniqueness might imply equality. The missing ingredient is a canonical directed path between arbitrary parallel paths. A construction based on whiskering, connections, or a cubical interpolation operation should be investigated.

## Phase III: search for models

### Route E: classifying-topos computation

In a distributive-lattice classifying topos satisfying countable quasi-coherence, determine the internal local operator generated by \(j\). Ask whether its sheaves are all \(\mathbb I\)-separated. Because both \(j\) and \(\rho\) are built from countably/finitely presented shapes, the question may translate to an algebraic statement about a limit diagram of presented \(\mathbb I\)-algebras.

This is likely the most promising model-independent route because Sterling--Ye already translate many orthogonality conditions into algebraic limits.

### Route F: realizability countermodels

Translate the directed interval and shape maps into modified realizability and effective-topos models. Search among known complete-but-not-replete objects. A candidate must be checked against:

- Phoa/interpolation axioms;
- existence and identification of \(\omega,\overline\omega\);
- chain completeness of \(\mathbb I\);
- the h-set convention;
- failure of \(\mathbb I\)-separation.

A model satisfying only older SDT axioms but not Xue's transfinite shape assumptions would not settle the conjecture as stated.

### Route G: sheaves of proof-relevant orders

Construct a topos of sheaves over a domain-like site in which objects can carry multiple directed arrows between the same endpoints, while the interval remains chain complete. Try the sheafified nerve of the finite parallel-pair category. Continuity should rule out jumps at infinity; sheaf proof relevance may preserve the two arrows.

This route targets the intuitive gap directly but requires substantial model building.

## Phase IV: communicate status correctly

Any future paper should distinguish the following possible outcomes.

1. **Full positive theorem:** \(j\)-locality implies separation under exactly Xue's axioms.
2. **Conditional theorem:** the implication requires spatiality, repleteness, choice, or an additional interval axiom.
3. **Independence:** models of the base axioms exist on both sides.
4. **Counterexample:** a specific model and local non-separated object refute the unrestricted statement.

The current manuscript establishes a conditional theorem and a reduction, not outcome 1.

# Conclusion

Xue's Conjecture 6.20 asks whether one countable orthogonality condition characterizes synthetic predomains. The answer obtained here is partial but structurally sharp.

The infinite spine inclusion factors into finite categorical completion and chain convergence. That factorization can be upgraded from intuition to an exact theorem. Finite spine inclusions are arrow retracts of the infinite inclusion, so every local type has coherent finite composition. Sequential colimit universal properties then produce locality for the initial infinite simplex, and two-out-of-three produces chain completeness. Under the stated shape assumptions,

\[
  A\perp j
  \quad\Longleftrightarrow\quad
  \left(\forall n,\ A\perp j_n\right)
  \wedge
  A\perp(\Delta^\omega\hookrightarrow\Delta^\infty).
\]

This resolves the part Xue explicitly expected might be reachable.

The remaining properties are not equally mysterious. Once parallel paths are unique, an even/odd cofinal-subsequence argument forces antisymmetry and, in the h-set setting, Rezk completeness. Therefore the full conjecture is equivalent to one separation implication:

\[
  A\perp(\Lambda_\omega\hookrightarrow\Delta^\infty)
  \quad\Longrightarrow\quad
  A\perp(\mathbb I_{\parallel}\to\mathbb I).
\]

The conjecture holds for observationally separated local types, because they embed into a double-dual observational algebra that is already a synthetic predomain. This includes the broad spatial/replete region of existing classifying-topos models.

The unrestricted separation implication is where this manuscript stops. The linear generator does not directly encode two parallel noncomposable paths; constant-chain and codiagonal arguments fail for identifiable reasons; and ordinary category nerves do not satisfy the required chain continuity. No counterexample meeting all ambient axioms was found.

The most informative next calculations are now concrete: formalize the finite retracts and colimit comparison, then compute the \(j\)-local reflection of the walking parallel pair or prove that open observations separate every \(j\)-local type. Either result would materially advance the conjecture.

\statusbox{\textbf{Final status.} The full conjecture is neither proved nor disproved. The manuscript supplies a proposed paper-level proof of the Segal and chain-complete consequences, reduces the remaining theorem to \(\mathbb I\)-separation, proves the observationally separated case, and identifies precise formal and model-theoretic next steps.}

\appendix

# Expanded categorical proofs

## Retracts of local equivalences

Let \(f:X\to Y\) and \(g:X'\to Y'\). Suppose there are commutative squares

\[
\begin{tikzcd}[column sep=large]
X \arrow[r,"u"] \arrow[d,"f"'] & X' \arrow[d,"g"]
& X' \arrow[r,"q"] \arrow[d,"g"'] & X \arrow[d,"f"]\\
Y \arrow[r,"e"'] & Y'
& Y' \arrow[r,"p"'] & Y
\end{tikzcd}
\]

with \(q\circ u=\id_X\) and \(p\circ e=\id_Y\). For a target \(A\), precomposition reverses the diagram. Define

\[
\begin{aligned}
  U_X &: A^X\to A^{X'}, & U_X(h)&=h\circ q,\\
  Q_X &: A^{X'}\to A^X, & Q_X(h')&=h'\circ u,\\
  U_Y &: A^Y\to A^{Y'}, & U_Y(k)&=k\circ p,\\
  Q_Y &: A^{Y'}\to A^Y, & Q_Y(k')&=k'\circ e.
\end{aligned}
\]

Then \(Q_XU_X=\id\) and \(Q_YU_Y=\id\), and the restriction square commutes. Thus \(f^*\) is a retract of \(g^*\) in the arrow category. If \(g^*\) has inverse \(r\), an inverse for \(f^*\) can be written explicitly as

\[
  A^X\xrightarrow{U_X}A^{X'}
  \xrightarrow{r}A^{Y'}
  \xrightarrow{Q_Y}A^Y.
\]

The two inverse laws follow from the square equations and retract equations. This explicit formula may be easier to formalize than invoking a general categorical lemma.

## Limit of a natural family of equivalences

Let \(F,G:\mathbb N^{op}\to\mathcal U\) be diagrams and \(\alpha:F\Rightarrow G\) a natural transformation whose components are equivalences. Choose componentwise inverses \(\beta_n\). Naturality of \(\alpha\) implies naturality of \(\beta\): for each transition map, cancel \(\alpha\) on both sides. Therefore \(\beta\) induces a map on limits inverse to the map induced by \(\alpha\).

In type theory, a limit element is a compatible family \((x_n)_n\). The induced map sends it to \((\alpha_nx_n)_n\), and the inverse sends \((y_n)_n\) to \((\beta_ny_n)_n\). Compatibility follows from naturality. The inverse equations are pointwise.

Applied to

\[
  F_n=A^{\Delta^n},
  \qquad
  G_n=A^{\Lambda_n},
  \qquad
  \alpha_n=j_n^*,
\]

this supplies the inverse of \(k^*\).

## Decomposition without chosen inverses

Theorem \ref{thm:decomposition} can be proved propositionally without choosing extension operators. The type `isEquiv(f)` is a proposition, so all constructions are insensitive to inverse choices. This matters in Cubical Agda, where one should avoid making the resulting Segal or chain-complete structure depend on arbitrary equivalence witnesses when a mere property is intended.

If operational extension functions are wanted, they can be extracted canonically from the equivalence structure. Uniqueness then proves independence.

## Predomains imply infinite-spine locality

Assume \(A\) is Segal. Standard Segal induction decomposes \(\Delta^n\) into a sequence of \(2\)-simplices glued along edges, or equivalently decomposes the spine inclusion \(j_n\) into pushouts and composites of \(j_2\). Locality is stable under those operations, so \(A\perp j_n\) for every \(n\). The colimit argument gives \(A\perp k\). If \(A\) is chain complete, \(A\perp c\), and composite locality gives \(A\perp j\).

This proof uses only the Segal and chain-complete components; Rezk completeness and separation are irrelevant to the necessary direction.

# Expanded cofinality argument

## Shape calculations

Write a point of \(\Delta^\infty\) as a descending sequence \(s=(s_0,s_1,\ldots)\). Define

\[
  \epsilon(s)_{2n}=s_n,
  \qquad
  \epsilon(s)_{2n+1}=s_n,
\]

and

\[
  \omicron(s)_0=1,
  \quad
  \omicron(s)_{2n+1}=s_n,
  \quad
  \omicron(s)_{2n+2}=s_n.
\]

For \(\epsilon\), descendingness follows from

\[
  s_n\ge s_n\ge s_{n+1}.
\]

For \(\omicron\), it follows from

\[
  1\ge s_0\ge s_0\ge s_1\ge s_1\ge\cdots.
\]

The finite vertex \(v_m\) has coordinates \(1\) for indices below \(m\) and \(0\) thereafter. Duplicating each coordinate gives exactly \(2m\) initial ones; prefixing a one and duplicating gives \(2m+1\). The all-ones sequence is fixed.

## Restriction to the spine

Let \(\bar a:\Delta^\infty\to A\) extend an alternating chain. The composite \(\bar a\circ\epsilon\circ j\) traverses, on its \(n\)-th edge, the image under \(\bar a\) of the long edge from \(v_{2n}\) to \(v_{2n+2}\) selected by \(\epsilon\). In a Segal type this long edge is the composite of the adjacent edges. Because the adjacent edges are \(p\) and \(q\), it is \(q\circ p\).

There is a formal subtlety: the map \(\epsilon\) sends a one-dimensional edge of the spine into a path in the infinite simplex whose coordinate formula may not be definitionally the canonical diagonal of the corresponding \(2\)-simplex. The required equality follows from locality for \(j_2\): both paths are fillers of the same two-edge spine and therefore agree in \(A\) after applying \(\bar a\). This should be an explicit lemma in a formalization.

The same reasoning applies to \(\omicron\), yielding \(p\circ q\).

## Uniqueness at the limit

If the even restriction is the constant identity chain at \(x\), both

\[
  \bar a\circ\epsilon
  \quad\text{and}\quad
  \operatorname{const}_x
\]

are maps \(\Delta^\infty\to A\) with the same restriction to \(\Lambda_\omega\). Since \(j^*\) is an embedding---indeed an equivalence---they are equal. Evaluating at \(v_\infty\) gives

\[
  \bar a(v_\infty)
  =\bar a(\epsilon(v_\infty))
  =x.
\]

The odd equation gives the same limit equal to \(y\).

## Dependence on separation

For arbitrary paths \(p:x\to y\) and \(q:y\to x\), the even subsequence has transition \(q\circ p\), not necessarily identity. Separation makes all endomorphisms of a point equal to the identity because the hom-type \(x\rightsquigarrow x\) is a proposition and contains \(\id_x\). This is the only use of separation in the antisymmetry proof.

# A decision tree for the remaining conjecture

The following decision tree can guide further work.

1. **Can the shape package be formalized?**
   - No: repair the statement or identify a mismatch in Xue's constructions.
   - Yes: the Segal/chain-complete theorem is established.
2. **Does \(L_j(\rho)\) exist in the chosen model?**
   - No: use an orthogonality-class argument without reflection.
   - Yes: compute whether it is an equivalence.
3. **If it is an equivalence in spatial/classifying models, is the proof model-independent?**
   - Yes: full positive theorem.
   - No: identify the extra axiom, yielding a conditional theorem.
4. **If it is not an equivalence, can a local detector be extracted?**
   - Yes: explicit counterexample.
   - No: prove non-equivalence internally or after a context extension.
5. **Do different models disagree?**
   - Yes: independence result and exact axiom separation.

# Bibliographic notes

## On notation

Xue uses two omega-like symbols for the initial lifting algebra and final lifting coalgebra. To avoid font ambiguity, this manuscript writes \(\omega\simeq\Delta^\omega\) and \(\overline\omega\simeq\Delta^\infty\). The infinite-spine conjecture is therefore written

\[
  \Lambda_\omega\hookrightarrow\overline\omega.
\]

Some source text extractions render both objects as \(\omega\); readers should consult the typeset source.

## On the date and version of the conjecture

The cited arXiv version of Xue's manuscript was submitted on 19 July 2026 and was the current public version located during preparation of this manuscript on 9 August 2026. No later proof or counterexample to Conjecture 6.20 was found in the targeted search. Because the conjecture is very recent, absence from search results is weak evidence; author communication and inspection of the associated code record are recommended before publication.

## On the source formalization

Xue's arXiv record links associated source code through Zenodo DOI `10.5281/zenodo.21442391`. The code record could not be retrieved in the present environment. Consequently, no claim is made that the pseudocode names or module boundaries match the repository. The mathematical source reports that the principal interval and Phoa results are formalized in Cubical Agda.

# References

1. **Adámek, Jiří.** “Free Algebras and Automata Realizations in the Language of Categories.” *Commentationes Mathematicae Universitatis Carolinae* 15 (1974): 589--602. Relevant for initial-algebra constructions by colimits.

2. **Buchholtz, Ulrik, and Jonathan Weinberger.** Work on synthetic categories and Rezk completeness, as cited by Sterling and Ye. The walking-equivalence shape used here follows this synthetic-category-theoretic tradition.

3. **Escardó, Martín H., and Cory M. Knapp.** “Partial Elements and Recursion via Dominances in Univalent Type Theory.” In *CSL 2017*, LIPIcs 82, Article 21. DOI: `10.4230/LIPIcs.CSL.2017.21`.

4. **Hyland, J. M. E.** “First Steps in Synthetic Domain Theory.” In *Category Theory*, Como 1990, Lecture Notes in Mathematics 1488, Springer, 1991, 131--156. A foundational source for replete objects.

5. **Longley, John, and Alex Simpson.** “A Uniform Approach to Domain Theory in Realizability Models.” *Mathematical Structures in Computer Science* 7, no. 5 (1997): 469--505.

6. **Mörtberg, Anders, Andrea Vezzosi, and Andreas Abel.** “Cubical Agda: A Dependently Typed Programming Language with Univalence and Higher Inductive Types.” *Journal of Functional Programming* 31 (2021), e8; earlier conference/system descriptions appeared in 2019. DOI: `10.1017/S0956796821000034`.

7. **Pugh, Matt, and Jonathan Sterling.** “When Is the Partial Map Classifier a Sierpiński Cone?” arXiv:`2504.06789`, 2025; accepted at LICS 2025. Develops interval/dominance conditions closely related to modern SDT models.

8. **Reus, Bernhard, and Thomas Streicher.** “General Synthetic Domain Theory---A Logical Approach.” *Mathematical Structures in Computer Science* 9, no. 2 (1999): 177--223. DOI: `10.1017/S096012959900273X`.

9. **Riehl, Emily, and Michael Shulman.** “A Type Theory for Synthetic ∞-Categories.” *Higher Structures* 1, no. 1 (2017): 147--224. arXiv:`1705.07442`.

10. **Sterling, Jonathan, and Lingyuan Ye.** “Domains and Classifying Topoi.” arXiv:`2505.13096`, 2025. Establishes spatiality, repleteness, synthetic-poset locality, and countable chain-completeness principles in classifying topoi.

11. **The Univalent Foundations Program.** *Homotopy Type Theory: Univalent Foundations of Mathematics.* Institute for Advanced Study, 2013.

12. **van Oosten, Jaap, and Alex Simpson.** “Axioms and (Counter)Examples in Synthetic Domain Theory.” *Annals of Pure and Applied Logic* 104, nos. 1--3 (2000): 233--278. DOI: `10.1016/S0168-0072(00)00014-2`.

13. **Xue, Runze.** “Topology in Synthetic Domain Theory and its Formalisation in Agda.” arXiv:`2607.17292`, submitted 19 July 2026. Associated source code: DOI `10.5281/zenodo.21442391`. Conjecture 6.20 is the problem studied in this manuscript.

14. **Kudasov, Nikolai, Jonathan Sim, and Benedikt Ahrens.** “Rzk: A Proof Assistant for Synthetic ∞-Categories.” arXiv:`2607.12207`, 2026. Consult the current version for available support for countable directed shapes.

