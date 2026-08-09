# Voice Leading and Trees

- URL: https://chatgpt.com/c/6a6d0569-07e4-83ea-868b-f5b7b5f17cd6
- Created: 2026-07-31T20:28:26.700Z

---

> how is doing voice leading in choral composition similar to converting sorted lists to binary trees, category theory

<details><summary>💭 Thinking</summary>

**Comparing structural mappings**

I’m relating both processes to structure-preserving transformations: an ordered list becomes a tree while retaining traversal order, while voice leading maps chord progressions to realizations preserving harmony under motion constraints. Category theory frames these as functors or constrained lifts.

**Compared structural mappings**

</details>

Both tasks take a **simple ordered structure** and realize it as a richer structure while preserving an invariant.

## Core analogy

A sorted list

\[
[1,2,3,4,5,6,7]
\]

contains a total order. Converting it to a balanced binary search tree adds hierarchy:

```text
        4
      /   \
     2     6
    / \   / \
   1   3 5   7
```

The result is different structurally, but an inorder traversal recovers the original list.

Choral voice leading works similarly. A harmonic progression may specify only an abstract sequence of chords:

\[
C \rightarrow F \rightarrow G \rightarrow C
\]

A composer then realizes that sequence as four simultaneous melodic lines:

```text
Soprano: E  F  G  G
Alto:    C  C  D  E
Tenor:   G  A  B  C
Bass:    C  F  G  C
```

The realization adds structure—register, melodic motion, spacing, doubling, and contrary motion—while preserving the underlying harmonic progression.

So:

| Abstract input | Structured realization | Preserved invariant |
|---|---|---|
| Sorted list | Binary search tree | Element order |
| Chord progression | Interacting vocal lines | Harmonic identity and sequence |

## Local choices produce a global structure

When constructing a balanced tree, choosing the middle element as the root constrains everything beneath it. Each recursive choice affects the shape of the whole tree.

In voice leading, choosing one note for the soprano constrains the alto, tenor, and bass. Each choice affects:

- spacing,
- tendency-tone resolution,
- voice crossing,
- parallel fifths and octaves,
- melodic smoothness,
- chord completeness.

Neither problem is merely “place each item independently.” It is a **constraint-satisfaction problem whose local decisions must remain compatible globally**.

## The category-theoretic picture

Let \(\mathcal L\) be a category of sorted lists and order-preserving maps. Let \(\mathcal T\) be a category of binary search trees and maps that preserve their ordering structure.

There is an inorder traversal functor

\[
U:\mathcal T\rightarrow\mathcal L
\]

that forgets the tree’s hierarchy and returns its sorted sequence.

A particular tree-building algorithm gives a construction

\[
F:\mathcal L\rightarrow\mathcal T.
\]

Ideally,

\[
U\circ F \cong \mathrm{Id}_{\mathcal L},
\]

meaning that building the tree and then traversing it recovers the original list, up to the appropriate notion of equivalence.

For choral writing, let:

- \(\mathcal H\) be a category whose objects are abstract chords and whose morphisms are harmonic transitions;
- \(\mathcal V\) be a category whose objects are concrete voicings and whose morphisms are admissible voice-leading motions.

There is a forgetful map

\[
P:\mathcal V\rightarrow\mathcal H
\]

that discards register and voice identity and retains only the abstract harmony.

Writing a choral realization means **lifting** a harmonic path

\[
H_0\rightarrow H_1\rightarrow H_2
\]

to a path of concrete voicings

\[
V_0\rightarrow V_1\rightarrow V_2
\]

such that

\[
P(V_i)=H_i.
\]

Diagrammatically:

\[
\begin{array}{ccccc}
V_0 & \longrightarrow & V_1 & \longrightarrow & V_2\\
\downarrow P && \downarrow P && \downarrow P\\
H_0 & \longrightarrow & H_1 & \longrightarrow & H_2
\end{array}
\]

The composer’s job is to make the upper row exist and behave well.

## The main difference

Sorted-list-to-tree conversion can be made canonical by fixing an algorithm, such as “always choose the median.”

Choral realization is usually not canonical. One harmonic progression admits many valid voicings. Thus voice leading is less like a single function and more like selecting a point from a **space of possible lifts**.

That makes the strongest analogy:

> Balanced-tree construction chooses a hierarchical realization of linear order; voice leading chooses a contrapuntal realization of harmonic order. In both cases, the richer object must project back to the simpler one while satisfying additional structural constraints.


---

> what construction shows the similarity

<details><summary>💭 Thinking</summary>

**Identifying the construction**

I’m seeing the Grothendieck construction as the best match: it forms a category of realizations over abstract objects. Chord voicings and binary trees become fibers, while projection forgets realization details; categorically, this resembles a fibration.

**Identified the construction**

</details>

The categorical construction is the **Grothendieck construction**, viewed as a **fibration of concrete realizations over abstract structures**.

Let \(\mathcal B\) be a category of abstract objects. Define a functor

\[
R:\mathcal B^{op}\to \mathbf{Cat}
\]

where \(R(b)\) is the category of all concrete realizations of \(b\).

The Grothendieck construction forms

\[
\int_{\mathcal B} R
\]

whose objects are pairs

\[
(b,r),\qquad r\in R(b),
\]

with a projection

\[
\pi:\int_{\mathcal B}R\to\mathcal B,\qquad (b,r)\mapsto b.
\]

### Sorted lists and trees

Take \(\mathcal B=\mathcal L\), the category of sorted lists, and define

\[
R_{\mathrm{tree}}(L)
=
\{\text{binary-search trees whose inorder traversal is }L\}.
\]

Then

\[
\pi_{\mathrm{tree}}:
\int R_{\mathrm{tree}}\to\mathcal L
\]

forgets the tree shape and retains the sorted list.

A tree-building algorithm, such as repeatedly choosing the median, is a **section**

\[
s:\mathcal L\to\int R_{\mathrm{tree}}
\]

satisfying

\[
\pi_{\mathrm{tree}}\circ s=\mathrm{Id}_{\mathcal L}.
\]

It selects one tree from each fiber.

### Harmony and voice leading

Take \(\mathcal B=\mathcal H\), the category of abstract harmonies or chord progressions, and define

\[
R_{\mathrm{voice}}(H)
=
\{\text{choral voicings realizing }H\}.
\]

Then

\[
\pi_{\mathrm{voice}}:
\int R_{\mathrm{voice}}\to\mathcal H
\]

forgets voice assignment, register, spacing, and melodic motion, retaining only the abstract harmony.

Voice leading is the problem of **lifting** a harmonic transition

\[
H_0\longrightarrow H_1
\]

to a transition between objects in the corresponding fibers:

\[
\begin{array}{ccc}
(H_0,V_0)&\longrightarrow &(H_1,V_1)\\
\downarrow &&\downarrow\\
H_0&\longrightarrow&H_1.
\end{array}
\]

The upper arrow must satisfy contrapuntal constraints.

### The precise similarity

Both situations have:

\[
\text{space of realizations}
\longrightarrow
\text{space of abstract objects}.
\]

- The fiber above a sorted list consists of compatible tree shapes.
- The fiber above a chord consists of compatible voicings.
- Tree construction selects objects in the fibers.
- Voice leading selects objects and compatible arrows between successive fibers.

Thus the shared construction is:

\[
\boxed{\text{Grothendieck construction }+\text{ section/path lifting of a fibration}.}
\]

Balanced-tree conversion is usually a canonical or algorithmically specified section. Choral voice leading is generally a noncanonical, constraint-dependent lifting problem.


---

> how is it related to natural transformation?

<details><summary>💭 Thinking</summary>

**Explaining natural transformations**

I’m framing a natural transformation as a coherent comparison between two structure-preserving constructions. For lists-to-trees, it relates tree representations while preserving order; for voicings, it relates choices consistently across harmonic changes.

**Explained natural transformations**

</details>

A **natural transformation** appears when you compare two different, systematic choices of realization.

Suppose

\[
P:\mathcal V\to\mathcal H
\]

forgets the concrete voicing and retains only the abstract harmony. Let

\[
s,t:\mathcal H\to\mathcal V
\]

be two sections of \(P\):

\[
P\circ s=P\circ t=\mathrm{Id}_{\mathcal H}.
\]

Here:

- \(s(H)\) might choose a close-position voicing of each chord;
- \(t(H)\) might choose an open-position voicing.

A natural transformation

\[
\eta:s\Rightarrow t
\]

assigns to every harmony \(H\) a morphism

\[
\eta_H:s(H)\to t(H).
\]

Because both objects realize the same harmony, one normally requires

\[
P(\eta_H)=\mathrm{id}_H.
\]

Thus each component \(\eta_H\) changes the concrete realization without changing the underlying chord.

## Naturality condition

For every harmonic transition

\[
f:H\to K,
\]

naturality requires

\[
t(f)\circ \eta_H
=
\eta_K\circ s(f).
\]

This gives the commuting square

\[
\begin{array}{ccc}
s(H)&\xrightarrow{s(f)}&s(K)\\
\downarrow{\eta_H}&&\downarrow{\eta_K}\\
t(H)&\xrightarrow{t(f)}&t(K).
\end{array}
\]

Musically, there are two procedures:

1. change from voicing system \(s\) to voicing system \(t\), then move to the next chord;
2. move to the next chord using system \(s\), then change to system \(t\).

Naturality says these procedures are compatible.

So an individual voice-leading motion is usually a **morphism or lift**. A natural transformation is a coherent comparison between **entire systems of voice leading**.

## For sorted lists and binary trees

Let

\[
U:\mathcal T\to\mathcal L
\]

send a binary search tree to its inorder list. Suppose

\[
F,G:\mathcal L\to\mathcal T
\]

are two tree-construction algorithms:

- \(F\) builds a balanced tree;
- \(G\) builds some other canonical tree.

Both preserve the original list:

\[
U\circ F=U\circ G=\mathrm{Id}_{\mathcal L}.
\]

A natural transformation

\[
\alpha:F\Rightarrow G
\]

assigns to each sorted list \(L\) a tree transformation

\[
\alpha_L:F(L)\to G(L),
\]

perhaps implemented through order-preserving tree rotations.

For every order-preserving list map

\[
f:L\to M,
\]

naturality requires

\[
G(f)\circ\alpha_L
=
\alpha_M\circ F(f).
\]

That means converting between the two tree representations is compatible with transforming the underlying sorted data.

## A progression-indexed formulation

Let a chord progression be a functor

\[
C:[n]\to\mathcal H,
\]

where \([n]\) is the category

\[
0\to1\to\cdots\to n.
\]

Two choral realizations are lifts

\[
V,W:[n]\to\mathcal V
\]

such that

\[
P\circ V=P\circ W=C.
\]

A natural transformation

\[
\eta:V\Rightarrow W
\]

consists of maps

\[
\eta_i:V_i\to W_i
\]

at every moment in the progression, satisfying

\[
W_{i\to i+1}\circ\eta_i
=
\eta_{i+1}\circ V_{i\to i+1}.
\]

This is the closest musical interpretation:

> A natural transformation is a coherent way of translating one complete voice-leading realization into another, consistently across every chord transition.

The correspondence is therefore:

\[
\begin{array}{c|c}
\text{Binary trees} & \text{Choral writing}\\
\hline
\text{sorted list} & \text{abstract harmony}\\
\text{tree realization} & \text{choral voicing}\\
\text{tree construction functor} & \text{voicing strategy}\\
\text{tree rotation} & \text{change of voice disposition}\\
\text{natural transformation} &
\text{coherent comparison of voicing strategies}
\end{array}
\]

The essential idea is not merely that two objects can be converted. It is that the conversions behave consistently with every relevant map in the underlying category.

