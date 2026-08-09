# Blue Diagram and Pullbacks

- URL: https://chatgpt.com/c/6a6a0348-3c5c-83ea-92a4-78934a6d1b70
- Created: 2026-07-29T13:44:00.628Z

---

> [image: sediment://file_000000004b0881f5b5fd9369ddee3a36]
> [image: sediment://file_00000000a92081f592ee2a81f82f263c]
> Is the blue diagram at the bottom modeling the black one (which is a C-instance)? This is from the spivak fong seven sketches book.
>
> Does it motivate pullbacks down the line? Chapter 3

Yes. I think your blue diagram is trying to model exactly what a **\(\mathcal C\)-instance** is, though it is mixing two levels of description, which is why it feels a bit awkward.

Let's separate the levels.

### The black diagram (the schema)

The schema is the category

\[
a \xrightarrow{f} b
\overset{g}{\underset{h}{\rightrightarrows}}
c
\]

with the relation

\[
f;g = f;h.
\]

This is purely **syntax**. It says:

- there are three object-types \(a,b,c\),
- arrows \(f,g,h\),
- and a path equation.

No sets or functions yet.

---

### A \(\mathcal C\)-instance

An instance is a functor

\[
I:\mathcal C\to\mathbf{Set}.
\]

So it assigns

- a set \(I(a)\),
- a set \(I(b)\),
- a set \(I(c)\),

and functions

\[
I(f),\ I(g),\ I(h)
\]

such that

\[
I(g)\circ I(f)=I(h)\circ I(f).
\]

That equality is forced because functors preserve composition.

---

### Your blue diagram

Your sketch appears to replace the objects by sets:

- top-left = \(I(a)\),
- top-right = \(I(b)\),
- bottom-left = \(I(c)\) (or another copy),
- bottom-right = another copy of \(I(c)\),

with \(g\) going to one copy of \(c\), \(h\) to another, and an identity between the copies.

The idea seems to be:

\[
\require{AMScd}
\begin{CD}
I(b) @>{I(g)}>> I(c)\\
@V{I(h)}VV @VV{\mathrm{id}}V\\
I(c) @>{\mathrm{id}}>> I(c).
\end{CD}
\]

or something morally similar.

That is **not** literally the definition of an instance, because an instance only has **one** copy of \(I(c)\). The duplicate copy is just a drawing convenience.

So conceptually you're expressing

> "Both \(g\) and \(h\) land in the same set."

which is correct.

---

## Does this motivate pullbacks?

I think you're seeing something that Spivak is deliberately building toward.

The relation

\[
g\circ f = h\circ f
\]

means exactly that the image of \(I(f)\) lies inside the **equalizer** of \(I(g)\) and \(I(h)\):

\[
I(a)\longrightarrow
\operatorname{Eq}(I(g),I(h))
\hookrightarrow I(b).
\]

So every element coming from \(a\) is a point of \(b\) where \(g\) and \(h\) agree.

This is already a universal-property viewpoint.

---

### Later in the book

Later, when Spivak introduces pullbacks, you'll encounter diagrams like

\[
\begin{CD}
P @>>> X\\
@VVV @VVfV\\
Y @>>g> Z.
\end{CD}
\]

A pullback describes

> "pairs whose images agree."

An equalizer is actually a special case of a pullback:

\[
\operatorname{Eq}(g,h)
=
B\times_{(g,h),\,C\times C,\,\Delta} C,
\]

where \(\Delta:C\to C\times C\) is the diagonal map.

So the schema constraint

\[
f;g=f;h
\]

is already expressing a compatibility condition that, in **Set**, factors through an equalizer, and equalizers themselves are special pullbacks.

---

### Why this appears in Chapter 3

Chapter 3 is about viewing database schemas as categories and database instances as functors. The path equations in the schema become equations of functions automatically.

Later chapters introduce limits (products, pullbacks, equalizers) as ways of constructing new tables from existing ones. For example:

- products correspond to independent combinations,
- pullbacks correspond to joins,
- equalizers correspond to selecting rows satisfying an equality constraint.

So I would say **yes**: your sketch is pointing in the right direction. It's not literally a pullback diagram yet, but it's expressing the same kind of "agreement of two maps" that eventually becomes the pullback/equalizer machinery. In hindsight, this exercise is an early motivation for those constructions.


---

> [image: sediment://file_000000004a54820c82773310905864f6]
> Here is a clearer view of my drawing what I think matches the first setup. Analyze (don’t make an image)

```unknown
from PIL import Image
img=Image.open('/mnt/data/IMG_9B55ACDE-2AC1-4B1C-800B-149EED7E2045.jpeg')
img.size

```

<details><summary>💭 Thinking</summary>

**Inspected and interpreted the handwritten diagram**

**Parsing the diagram**

I’m reading the square as forcing \(g=h\), because both routes from \(b\) to the final \(c\) use identity maps afterward. That is stronger than the intended condition \(g\circ f=h\circ f\), which only requires equality after precomposition with \(f\).

**Parsed the diagram**

**Correcting the square**

I’m distinguishing the intended relation from the drawn square. To express \(g\circ f=h\circ f\), I need two copies of \(b\): \(a\) at upper-left, \(b\) at upper-right and lower-left, and \(c\) at lower-right, with both \(a\to b\) arrows labeled \(f\).

**Corrected the square**

</details>

The clearer view shows that your current square does **not quite model the given relation**. My earlier reading was too generous.

The schema is

\[
a \xrightarrow{f} b
\overset{g}{\underset{h}{\rightrightarrows}} c,
\qquad
f;g=f;h,
\]

where Spivak’s notation means

\[
g\circ f=h\circ f.
\]

## What your square currently says

Your square appears to be

\[
\begin{array}{ccc}
b & \xrightarrow{g} & c\\
{\scriptstyle h}\downarrow && \downarrow{\scriptstyle \mathrm{id}_c}\\
c & \xrightarrow{\mathrm{id}_c} & c .
\end{array}
\]

Commutativity of this square says

\[
\mathrm{id}_c\circ g
=
\mathrm{id}_c\circ h,
\]

hence simply

\[
g=h.
\]

That is **stronger** than the book’s condition. The arrow \(f\) entering \(b\) does not participate in the square’s two composite paths, so it does not change what the square asserts.

The schema permits \(g\) and \(h\) to disagree on parts of \(b\) that are not reached by \(f\).

For example, take

\[
a=\{\ast\},\qquad b=\{0,1\},\qquad c=\{x,y\},
\]

with

\[
f(\ast)=0,
\]

and

\[
g(0)=h(0)=x,\qquad g(1)=x,\qquad h(1)=y.
\]

Then

\[
g\circ f=h\circ f,
\]

but \(g\neq h\).

## The corresponding commuting square

To express the stated equation as a square, duplicate \(b\), not \(c\):

\[
\begin{array}{ccc}
a & \xrightarrow{f} & b\\
{\scriptstyle f}\downarrow && \downarrow{\scriptstyle g}\\
b & \xrightarrow{h} & c .
\end{array}
\]

The two routes from the upper-left \(a\) to the lower-right \(c\) are

\[
a\xrightarrow{f}b\xrightarrow{g}c
\]

and

\[
a\xrightarrow{f}b\xrightarrow{h}c.
\]

Thus commutativity says exactly

\[
g\circ f=h\circ f.
\]

The two copies of \(b\) in the drawing represent the same object; they are duplicated only to display the path equation as a square.

## Schema versus instance

The black diagram is the **schema category** \(\mathcal C\), rather than a particular \(\mathcal C\)-instance.

An instance is a functor

\[
I:\mathcal C\to\mathbf{Set}.
\]

After applying \(I\), the corresponding square is

\[
\begin{array}{ccc}
I(a) & \xrightarrow{I(f)} & I(b)\\
{\scriptstyle I(f)}\downarrow && \downarrow{\scriptstyle I(g)}\\
I(b) & \xrightarrow{I(h)} & I(c),
\end{array}
\]

and it commutes because the functor must respect the equation imposed in \(\mathcal C\).

## Relation to pullbacks

This is a **commutative square**, but it is not asserted to be a pullback. A pullback requires an additional universal property that is absent here.

The construction most directly suggested by this equation is an **equalizer**:

\[
E=\operatorname{Eq}(g,h)\longrightarrow b.
\]

The equation \(g\circ f=h\circ f\) says that \(f\) lands in the part of \(b\) where \(g\) and \(h\) agree. Therefore \(f\) factors through the equalizer:

\[
a\longrightarrow \operatorname{Eq}(g,h)\longrightarrow b.
\]

It does **not** say that \(a\) is the equalizer; \(a\) might contain only some of the elements on which \(g\) and \(h\) agree.

Equalizers are closely related to pullbacks—they can be constructed as a pullback of \((g,h):b\to c\times c\) along the diagonal \(c\to c\times c\). So your intuition about later pullback ideas is sound, but the immediate concept here is:

\[
\boxed{\text{path equation} \;\longrightarrow\; \text{commutative diagram} \;\longrightarrow\; \text{equalizer compatibility}.}
\]

