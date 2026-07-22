# Monic Epic Arrows Intuition

- URL: https://chatgpt.com/c/6a5f5a7d-1e10-83ea-b2f0-3cad9746dc09
- Created: 2026-07-21T11:39:43.447Z

---

> Monic and epic arrows in categories, make a set of small exercises for me to develop intuition (and how isomorphisms don’t mean epic + monic) preferably with examples / domains from computer science / programming.

<details><summary>💭 Thinking</summary>

**Clarifying category theory concepts**

I'm thinking about isomorphisms in category theory and clarifying that they imply both epimorphisms and monomorphisms. I also want to create simple exercises, hopefully with programming and CS examples.

**Clarified category theory concepts**

</details>

I’ll build a progressive exercise set around types/functions, information order, and program transformations, with short hints and a compact answer key.

<details><summary>💭 Thinking</summary>

**Explaining category theory exercises**

I’m working on definitions of monomorphisms and epimorphisms with exercises. I’ll cover examples working with total functions and cancellations, especially focusing on mono and epi properties in sets and categories.

**Explained category theory exercises**

</details>

## First, the key correction

For any arrow \(f:A\to B\):

\[
f\text{ is an isomorphism} \quad\Longrightarrow\quad f\text{ is monic and epic}.
\]

What fails in some categories is the converse:

\[
f\text{ monic and epic} \quad\centernot\Longrightarrow\quad f\text{ is an isomorphism}.
\]

Categories where the converse does hold are called **balanced**. The category of sets and total functions is balanced; many categories carrying additional structure are not.

---

## Working intuition

Let \(f:A\to B\).

### Monic

\(f\) is **monic** when

\[
f\circ g=f\circ h\quad\Longrightarrow\quad g=h
\]

for every \(g,h:X\to A\).

Think:

> No distinction made before \(f\) is lost by passing through \(f\).

In `Set`, this is exactly injectivity.

```text
X ──g──▶ A ──f──▶ B
╰──h──▶
```

If the two complete pipelines are equal, monicity lets you cancel \(f\).

### Epic

\(f\) is **epic** when

\[
g\circ f=h\circ f\quad\Longrightarrow\quad g=h
\]

for every \(g,h:B\to Y\).

Think:

> Every downstream observer is determined by how it behaves after \(f\).

In `Set`, this is exactly surjectivity.

```text
A ──f──▶ B ──g──▶ Y
             ╰──h──▶
```

If two observers agree after \(f\), epicness lets you cancel \(f\).

### Isomorphism

\(f\) is an isomorphism when there is an arrow \(f^{-1}:B\to A\) satisfying both

\[
f^{-1}\circ f=\operatorname{id}_A,
\qquad
f\circ f^{-1}=\operatorname{id}_B.
\]

An isomorphism is not merely cancellable. It has an actual structure-preserving inverse.

---

# Exercise set

For the first exercises, work in the category of types and **total deterministic functions**. This behaves like `Set`; ignore nontermination and runtime exceptions.

## 1. Classify some functions

For each function, decide whether it is monic, epic, an isomorphism, or none.

1. `duplicate : Bool → Bool × Bool`

   \[
   b\mapsto (b,b)
   \]

2. `or : Bool × Bool → Bool`

3. `not : Bool → Bool`

4. `increment : Nat → Nat`

   \[
   n\mapsto n+1
   \]

5. `parity : Nat → Bool`

6. `forget : Bool → Unit`

Try to justify each answer without immediately saying “injective” or “surjective.” Instead, ask:

- Does it lose distinctions?
- Are there outputs that no input reaches?

---

## 2. Witness failure of monicity

Suppose \(f:A\to B\) is not injective. Thus there are \(a_1\neq a_2\) with

\[
f(a_1)=f(a_2).
\]

Construct two distinct functions

\[
g,h:\mathrm{Unit}\to A
\]

such that

\[
f\circ g=f\circ h.
\]

Why is `Unit` useful here?

Programming interpretation: a function `Unit → A` simply selects a value of type `A`.

---

## 3. Witness failure of epicness

Consider

\[
\operatorname{increment}:\mathbb N\to\mathbb N,
\qquad n\mapsto n+1.
\]

Construct two different functions

\[
g,h:\mathbb N\to\mathrm{Bool}
\]

that disagree at \(0\), but satisfy

\[
g\circ\operatorname{increment}
=
h\circ\operatorname{increment}.
\]

Explain why downstream code cannot use `increment` to test how \(g\) and \(h\) behave at \(0\).

---

## 4. Encoders and left inverses

Suppose a serialization library provides

```text
encode : Tree → Bytes
decode : Bytes → Tree
```

and guarantees

\[
\operatorname{decode}\circ\operatorname{encode}
=
\operatorname{id}_{Tree}.
\]

1. Prove that `encode` is monic.
2. Must `encode` be epic?
3. Must `decode` be monic?
4. What does the equation say operationally about serialization?

This situation is called a **split monomorphism**: `encode` has a left inverse.

---

## 5. Normalization and right inverses

Suppose

```text
normalize : RawSyntax → CanonicalSyntax
renderCanonical : CanonicalSyntax → RawSyntax
```

satisfy

\[
\operatorname{normalize}\circ\operatorname{renderCanonical}
=
\operatorname{id}_{CanonicalSyntax}.
\]

1. Prove that `normalize` is epic.
2. Must `normalize` be monic?
3. Give a programming reason why several raw syntax trees might normalize to the same canonical tree.

This is a **split epimorphism**: `normalize` has a right inverse.

---

## 6. Different one-sided inverses

Suppose \(f:A\to B\) has arrows \(l,r:B\to A\) satisfying

\[
l\circ f=\operatorname{id}_A,
\qquad
f\circ r=\operatorname{id}_B.
\]

Prove that

\[
l=r.
\]

Conclude that \(f\) is an isomorphism.

Hint: Insert \(f\circ r\) or \(l\circ f\) into the expression \(l\).

---

## 7. Monic and epic, but not an isomorphism: information order

Let \(D\) be the preorder with two elements \(0,1\), but no nontrivial comparison:

```text
0     1
```

Let \(C\) be the chain

```text
0 ≤ 1
```

Consider the identity-on-elements function

\[
i:D\to C,
\qquad i(0)=0,\quad i(1)=1.
\]

Morphisms are monotone functions.

Verify:

1. \(i\) is monotone.
2. \(i\) is monic because its underlying function is injective.
3. \(i\) is epic because its underlying function is surjective.
4. The inverse set function \(C\to D\) is not monotone.
5. Therefore \(i\) is monic and epic but not an isomorphism.

Interpretation: \(i\) preserves the order present in \(D\), but it does not **reflect** the extra order relation \(0\leq1\) introduced in \(C\).

This is analogous to converting a data structure into one with extra semantic relationships: no elements are lost or added, but the structure has changed.

---

## 8. Monic and epic, but not invertible: accumulated cost

Construct a one-object category from the monoid \((\mathbb N,+,0)\):

- There is one object, call it `Program`.
- Every natural number \(n\) is an arrow `Program → Program`.
- Composition is addition.
- The identity arrow is \(0\).

Interpret \(n\) as “add \(n\) units of cost” or “append \(n\) log entries.”

Show that every \(n\) is monic:

\[
n+g=n+h\quad\Longrightarrow\quad g=h.
\]

Show that every \(n\) is epic:

\[
g+n=h+n\quad\Longrightarrow\quad g=h.
\]

Which arrows are isomorphisms?

This is a particularly compact demonstration that left and right cancellation do not imply the existence of an inverse.

---

## 9. Find the error in the argument

Consider this attempted proof:

> Let \(f:A\to B\) be epic and monic. Because \(f\) is epic, there must be some \(g:B\to A\) such that \(f\circ g=\operatorname{id}_B\). Since \(f\) is also monic, this \(g\) is an inverse. Therefore every monic and epic arrow is an isomorphism.

Where is the unjustified step?

What stronger condition was silently substituted for “epic”?

---

## 10. A useful repair theorem

Suppose \(f:A\to B\) is monic and has a right inverse \(s:B\to A\):

\[
f\circ s=\operatorname{id}_B.
\]

Prove that \(f\) is an isomorphism.

Hint:

\[
f\circ(s\circ f)
=
(f\circ s)\circ f
=
f
=
f\circ\operatorname{id}_A.
\]

What can you cancel?

State and prove the dual result involving an epic arrow with a left inverse.

---

# Compact answer key

## 1. Classification

| Function | Monic? | Epic? | Iso? |
|---|---:|---:|---:|
| `duplicate : Bool → Bool×Bool` | Yes | No | No |
| `or : Bool×Bool → Bool` | No | Yes | No |
| `not : Bool → Bool` | Yes | Yes | Yes |
| `increment : Nat → Nat` | Yes | No | No |
| `parity : Nat → Bool` | No | Yes | No |
| `forget : Bool → Unit` | No | Yes | No |

In `Set`, being both monic and epic does imply being an isomorphism because injective plus surjective means bijective.

## 2. Failure of monicity

Define

\[
g(*)=a_1,\qquad h(*)=a_2.
\]

Then \(g\neq h\), but

\[
(f\circ g)(*)=f(a_1)=f(a_2)=(f\circ h)(*).
\]

`Unit` acts as a probe that selects one element.

## 3. Failure of epicness

For example, define

\[
g(n)=\text{false for every }n,
\]

and

\[
h(n)=
\begin{cases}
\text{true},&n=0,\\
\text{false},&n>0.
\end{cases}
\]

They differ, but `increment` never produces \(0\), so their composites with `increment` agree.

## 4. Encoding

If

\[
\operatorname{encode}\circ g
=
\operatorname{encode}\circ h,
\]

apply `decode`:

\[
\operatorname{decode}\circ\operatorname{encode}\circ g
=
\operatorname{decode}\circ\operatorname{encode}\circ h,
\]

so \(g=h\).

Thus `encode` is monic. It need not be epic: many byte strings may not be valid encodings.

## 5. Normalization

If

\[
g\circ\operatorname{normalize}
=
h\circ\operatorname{normalize},
\]

compose with `renderCanonical`:

\[
g\circ\operatorname{normalize}\circ\operatorname{renderCanonical}
=
h\circ\operatorname{normalize}\circ\operatorname{renderCanonical},
\]

hence \(g=h\).

Normalization need not be monic because whitespace, comments, or redundant parentheses may be discarded.

## 6. One-sided inverses coincide

\[
l
=
l\circ\operatorname{id}_B
=
l\circ(f\circ r)
=
(l\circ f)\circ r
=
\operatorname{id}_A\circ r
=
r.
\]

## 8. Cost category

Every natural number is both monic and epic because addition on \(\mathbb N\) is cancellative.

Only \(0\) is an isomorphism. An inverse for \(n\) would require an \(m\in\mathbb N\) with

\[
n+m=0,
\]

which is impossible unless \(n=0\).

## 9. False proof

Epicness is a **cancellation property**. It does not assert that a right inverse exists.

The argument silently replaced “epic” with “split epic.”

## 10. Repair theorem

From

\[
f\circ(s\circ f)=f\circ\operatorname{id}_A
\]

and monicity of \(f\), cancel \(f\):

\[
s\circ f=\operatorname{id}_A.
\]

Thus \(s\) is a two-sided inverse.

Dually: an epic arrow with a left inverse is an isomorphism.

---

## The central distinction

- **Monic:** you can cancel the arrow from equations involving incoming maps.
- **Epic:** you can cancel the arrow from equations involving outgoing maps.
- **Isomorphism:** you can actually run the transformation backward while preserving the category’s structure.

Cancellation tells you how an arrow behaves **inside equations**. Invertibility requires the category to contain a suitable reverse arrow.


---

> Make svg for the diagrams

<details><summary>💭 Thinking</summary>

**Creating SVG diagrams**

I’ll generate a set of SVG files for diagrams such as monic/epic arrow and poset diagrams. I’ll use code to generate these files rather than image-gen, since files need to be vector-based.

**Created SVG diagrams**

</details>

I’ll convert the category-theory sketches into clean standalone SVGs and also package them as one combined sheet.

```unknown
from pathlib import Path
import zipfile

out = Path("/mnt/data/category_arrow_svgs")
out.mkdir(parents=True, exist_ok=True)

common_defs = """
<defs>
  <marker id="arrow" markerWidth="10" markerHeight="10" refX="9" refY="3"
          orient="auto" markerUnits="strokeWidth">
    <path d="M0,0 L0,6 L9,3 z" fill="#222"/>
  </marker>
  <style>
    .label { font-family: Inter, Arial, sans-serif; font-size: 20px; fill: #111; }
    .small { font-family: Inter, Arial, sans-serif; font-size: 16px; fill: #222; }
    .title { font-family: Inter, Arial, sans-serif; font-size: 24px; font-weight: 700; fill: #111; }
    .node { fill: #fff; stroke: #222; stroke-width: 2; }
    .arrow { fill: none; stroke: #222; stroke-width: 2.2; marker-end: url(#arrow); }
    .dash { fill: none; stroke: #555; stroke-width: 1.8; stroke-dasharray: 6 5; marker-end: url(#arrow); }
  </style>
</defs>
"""

monic = f"""<svg xmlns="http://www.w3.org/2000/svg" width="760" height="260" viewBox="0 0 760 260">
{common_defs}
<rect width="100%" height="100%" fill="white"/>
<text x="380" y="36" text-anchor="middle" class="title">Monic arrow: left-cancellation</text>

<circle cx="120" cy="135" r="28" class="node"/>
<circle cx="380" cy="135" r="28" class="node"/>
<circle cx="640" cy="135" r="28" class="node"/>

<text x="120" y="142" text-anchor="middle" class="label">X</text>
<text x="380" y="142" text-anchor="middle" class="label">A</text>
<text x="640" y="142" text-anchor="middle" class="label">B</text>

<path d="M148 124 C220 80, 292 80, 352 124" class="arrow"/>
<path d="M148 146 C220 190, 292 190, 352 146" class="arrow"/>
<path d="M408 135 L610 135" class="arrow"/>

<text x="250" y="84" text-anchor="middle" class="label">g</text>
<text x="250" y="202" text-anchor="middle" class="label">h</text>
<text x="510" y="122" text-anchor="middle" class="label">f</text>

<text x="380" y="238" text-anchor="middle" class="small">
  f ∘ g = f ∘ h  ⇒  g = h
</text>
</svg>
"""
(out / "monic_left_cancellation.svg").write_text(monic, encoding="utf-8")

epic = f"""<svg xmlns="http://www.w3.org/2000/svg" width="760" height="260" viewBox="0 0 760 260">
{common_defs}
<rect width="100%" height="100%" fill="white"/>
<text x="380" y="36" text-anchor="middle" class="title">Epic arrow: right-cancellation</text>

<circle cx="120" cy="135" r="28" class="node"/>
<circle cx="380" cy="135" r="28" class="node"/>
<circle cx="640" cy="135" r="28" class="node"/>

<text x="120" y="142" text-anchor="middle" class="label">A</text>
<text x="380" y="142" text-anchor="middle" class="label">B</text>
<text x="640" y="142" text-anchor="middle" class="label">Y</text>

<path d="M148 135 L350 135" class="arrow"/>
<path d="M408 124 C480 80, 552 80, 612 124" class="arrow"/>
<path d="M408 146 C480 190, 552 190, 612 146" class="arrow"/>

<text x="250" y="122" text-anchor="middle" class="label">f</text>
<text x="510" y="84" text-anchor="middle" class="label">g</text>
<text x="510" y="202" text-anchor="middle" class="label">h</text>

<text x="380" y="238" text-anchor="middle" class="small">
  g ∘ f = h ∘ f  ⇒  g = h
</text>
</svg>
"""
(out / "epic_right_cancellation.svg").write_text(epic, encoding="utf-8")

preorder = f"""<svg xmlns="http://www.w3.org/2000/svg" width="900" height="360" viewBox="0 0 900 360">
{common_defs}
<rect width="100%" height="100%" fill="white"/>
<text x="450" y="36" text-anchor="middle" class="title">
  Monic and epic, but not an isomorphism
</text>

<text x="220" y="82" text-anchor="middle" class="label">D: discrete preorder</text>
<text x="680" y="82" text-anchor="middle" class="label">C: chain</text>

<circle cx="150" cy="190" r="26" class="node"/>
<circle cx="290" cy="190" r="26" class="node"/>
<text x="150" y="197" text-anchor="middle" class="label">0</text>
<text x="290" y="197" text-anchor="middle" class="label">1</text>

<circle cx="610" cy="240" r="26" class="node"/>
<circle cx="750" cy="140" r="26" class="node"/>
<text x="610" y="247" text-anchor="middle" class="label">0</text>
<text x="750" y="147" text-anchor="middle" class="label">1</text>
<path d="M632 224 L727 156" class="arrow"/>
<text x="682" y="181" text-anchor="middle" class="small">0 ≤ 1</text>

<path d="M330 190 C405 190, 495 190, 575 210" class="arrow"/>
<text x="450" y="174" text-anchor="middle" class="label">i</text>
<text x="450" y="206" text-anchor="middle" class="small">same elements</text>

<path d="M720 280 C610 330, 390 330, 250 260" class="dash"/>
<text x="475" y="318" text-anchor="middle" class="small">
  inverse set-function is not monotone
</text>

<text x="450" y="348" text-anchor="middle" class="small">
  i is injective and surjective on elements, but it does not reflect the added order relation.
</text>
</svg>
"""
(out / "monic_epic_not_iso_preorder.svg").write_text(preorder, encoding="utf-8")

cost = f"""<svg xmlns="http://www.w3.org/2000/svg" width="820" height="360" viewBox="0 0 820 360">
{common_defs}
<rect width="100%" height="100%" fill="white"/>
<text x="410" y="38" text-anchor="middle" class="title">
  One-object category from (ℕ, +, 0)
</text>

<circle cx="410" cy="205" r="58" class="node"/>
<text x="410" y="213" text-anchor="middle" class="label">Program</text>

<path d="M365 165 C250 55, 160 115, 285 220 C320 245, 350 225, 364 211" class="arrow"/>
<text x="215" y="112" text-anchor="middle" class="label">m</text>

<path d="M455 165 C570 55, 660 115, 535 220 C500 245, 470 225, 456 211" class="arrow"/>
<text x="605" y="112" text-anchor="middle" class="label">n</text>

<path d="M389 148 C380 105, 440 105, 431 148" class="arrow"/>
<text x="410" y="102" text-anchor="middle" class="small">0 = id</text>

<text x="410" y="292" text-anchor="middle" class="label">composition: m ∘ n = m + n</text>
<text x="410" y="326" text-anchor="middle" class="small">
  Every arrow is monic and epic by cancellation; only 0 is invertible in ℕ.
</text>
</svg>
"""
(out / "cancellative_monoid_category.svg").write_text(cost, encoding="utf-8")

combined = f"""<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="1280" viewBox="0 0 1200 1280">
{common_defs}
<rect width="100%" height="100%" fill="white"/>
<text x="600" y="42" text-anchor="middle" class="title">Monic, Epic, and Isomorphism — Diagram Sheet</text>

<!-- Monic panel -->
<rect x="50" y="75" width="1100" height="250" rx="18" fill="#fff" stroke="#bbb"/>
<text x="600" y="108" text-anchor="middle" class="title">Monic arrow: left-cancellation</text>
<circle cx="200" cy="200" r="26" class="node"/>
<circle cx="600" cy="200" r="26" class="node"/>
<circle cx="1000" cy="200" r="26" class="node"/>
<text x="200" y="207" text-anchor="middle" class="label">X</text>
<text x="600" y="207" text-anchor="middle" class="label">A</text>
<text x="1000" y="207" text-anchor="middle" class="label">B</text>
<path d="M226 190 C340 125, 480 125, 574 190" class="arrow"/>
<path d="M226 210 C340 275, 480 275, 574 210" class="arrow"/>
<path d="M626 200 L974 200" class="arrow"/>
<text x="410" y="138" text-anchor="middle" class="label">g</text>
<text x="410" y="278" text-anchor="middle" class="label">h</text>
<text x="800" y="185" text-anchor="middle" class="label">f</text>
<text x="600" y="306" text-anchor="middle" class="small">f ∘ g = f ∘ h  ⇒  g = h</text>

<!-- Epic panel -->
<rect x="50" y="350" width="1100" height="250" rx="18" fill="#fff" stroke="#bbb"/>
<text x="600" y="383" text-anchor="middle" class="title">Epic arrow: right-cancellation</text>
<circle cx="200" cy="475" r="26" class="node"/>
<circle cx="600" cy="475" r="26" class="node"/>
<circle cx="1000" cy="475" r="26" class="node"/>
<text x="200" y="482" text-anchor="middle" class="label">A</text>
<text x="600" y="482" text-anchor="middle" class="label">B</text>
<text x="1000" y="482" text-anchor="middle" class="label">Y</text>
<path d="M226 475 L574 475" class="arrow"/>
<path d="M626 465 C740 400, 880 400, 974 465" class="arrow"/>
<path d="M626 485 C740 550, 880 550, 974 485" class="arrow"/>
<text x="400" y="460" text-anchor="middle" class="label">f</text>
<text x="790" y="413" text-anchor="middle" class="label">g</text>
<text x="790" y="553" text-anchor="middle" class="label">h</text>
<text x="600" y="581" text-anchor="middle" class="small">g ∘ f = h ∘ f  ⇒  g = h</text>

<!-- Preorder counterexample -->
<rect x="50" y="625" width="1100" height="310" rx="18" fill="#fff" stroke="#bbb"/>
<text x="600" y="660" text-anchor="middle" class="title">Monic and epic, but not an isomorphism</text>
<text x="300" y="705" text-anchor="middle" class="label">D: discrete preorder</text>
<text x="900" y="705" text-anchor="middle" class="label">C: chain</text>
<circle cx="230" cy="795" r="25" class="node"/>
<circle cx="370" cy="795" r="25" class="node"/>
<text x="230" y="802" text-anchor="middle" class="label">0</text>
<text x="370" y="802" text-anchor="middle" class="label">1</text>
<circle cx="830" cy="840" r="25" class="node"/>
<circle cx="970" cy="745" r="25" class="node"/>
<text x="830" y="847" text-anchor="middle" class="label">0</text>
<text x="970" y="752" text-anchor="middle" class="label">1</text>
<path d="M852 824 L947 760" class="arrow"/>
<path d="M405 795 C520 795, 660 795, 800 820" class="arrow"/>
<text x="600" y="780" text-anchor="middle" class="label">i</text>
<text x="600" y="812" text-anchor="middle" class="small">identity on elements</text>
<path d="M940 875 C750 930, 500 930, 320 850" class="dash"/>
<text x="620" y="915" text-anchor="middle" class="small">inverse is not monotone</text>

<!-- Cost category -->
<rect x="50" y="960" width="1100" height="275" rx="18" fill="#fff" stroke="#bbb"/>
<text x="600" y="995" text-anchor="middle" class="title">One-object category from (ℕ, +, 0)</text>
<circle cx="600" cy="1105" r="48" class="node"/>
<text x="600" y="1112" text-anchor="middle" class="label">Program</text>
<path d="M565 1072 C445 975, 345 1040, 480 1130 C515 1155, 545 1135, 560 1120" class="arrow"/>
<text x="400" y="1030" text-anchor="middle" class="label">m</text>
<path d="M635 1072 C755 975, 855 1040, 720 1130 C685 1155, 655 1135, 640 1120" class="arrow"/>
<text x="800" y="1030" text-anchor="middle" class="label">n</text>
<path d="M583 1061 C575 1028, 625 1028, 617 1061" class="arrow"/>
<text x="600" y="1025" text-anchor="middle" class="small">0 = id</text>
<text x="600" y="1190" text-anchor="middle" class="small">
  composition is addition; every arrow cancels, but only 0 is invertible
</text>
</svg>
"""
(out / "all_category_diagrams.svg").write_text(combined, encoding="utf-8")

zip_path = Path("/mnt/data/category_arrow_svgs.zip")
with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
    for p in sorted(out.glob("*.svg")):
        z.write(p, arcname=p.name)

print("Created:")
for p in sorted(out.glob("*.svg")):
    print(p)
print(zip_path)

```

Created five SVG files:

- [Combined diagram sheet](sandbox:/mnt/data/category_arrow_svgs/all_category_diagrams.svg)
- [Monic — left cancellation](sandbox:/mnt/data/category_arrow_svgs/monic_left_cancellation.svg)
- [Epic — right cancellation](sandbox:/mnt/data/category_arrow_svgs/epic_right_cancellation.svg)
- [Monic and epic but not isomorphic — preorder example](sandbox:/mnt/data/category_arrow_svgs/monic_epic_not_iso_preorder.svg)
- [Cancellative monoid category](sandbox:/mnt/data/category_arrow_svgs/cancellative_monoid_category.svg)

[Download all SVGs as a ZIP](sandbox:/mnt/data/category_arrow_svgs.zip)


---

> What’s the total in “total deterministic functions” for

“Total” means the function produces an output for **every valid input** in its domain.

For a function

\[
f:A\to B,
\]

totality means:

\[
\forall a\in A,\quad f(a)\text{ is defined and belongs to }B.
\]

“Deterministic” means each input has **at most one** output. Together:

- deterministic: no input has multiple possible outputs;
- total: no input is missing an output;
- total deterministic: every input has exactly one output.

Example:

```text
isEven : Int → Bool
```

is total if it returns either `true` or `false` for every integer.

By contrast:

```text
head : List<A> → A
```

is not total as written, because `head([])` has no result. It becomes total if its type records failure:

```text
head : List<A> → Option<A>
```

Now the empty list maps to `None`.

Likewise, semantically, these can make a programming function non-total:

- throwing an exception;
- infinite looping;
- crashing;
- accessing an invalid array index;
- deliberately leaving a case unimplemented.

The phrase was there because the category `Set` models arrows as ordinary mathematical functions: every input has exactly one output. Real program functions often behave more like **partial functions** unless their types account for failure or nontermination.


---

> [image: sediment://file_00000000921481f5b27045c709dfd938]
> Help me be more precise / sure for showing that or is epic

<details><summary>💭 Thinking</summary>

**Explaining categorical proof**

I'm breaking down a categorical proof about the function "or." I'll show it involves considering surjectivity, section mappings, and cancellation with explicit definitions. I'll clean up some unnecessary steps in their reasoning.

**Explained categorical proof**

</details>

Your idea is correct. The cleanest proof is to exhibit a **right inverse** for `or`.

Let

\[
\lor:\mathrm{Bool}\times\mathrm{Bool}\to\mathrm{Bool}.
\]

Define

\[
s:\mathrm{Bool}\to\mathrm{Bool}\times\mathrm{Bool},
\qquad
s(b)=(b,\mathrm{false}).
\]

Then

\[
(\lor\circ s)(b)
=
b\lor\mathrm{false}
=
b,
\]

so

\[
\lor\circ s=\operatorname{id}_{\mathrm{Bool}}.
\]

Therefore `or` is a **split epimorphism**, hence epic.

The important correction to the margin note is:

\[
b\lor\mathrm{false}=b,
\]

not \(b\lor\mathrm{true}=b\). Using `true` would give the constant function `true`.

## Proof directly from the definition

To prove that `or` is epic, take an arbitrary type \(Z\) and arbitrary functions

\[
g,h:\mathrm{Bool}\to Z.
\]

Assume

\[
g\circ\lor=h\circ\lor.
\]

We must prove \(g=h\).

Take any \(b\in\mathrm{Bool}\). Since

\[
b=b\lor\mathrm{false},
\]

we have

\[
\begin{aligned}
g(b)
&=g(b\lor\mathrm{false})\\
&=(g\circ\lor)(b,\mathrm{false})\\
&=(h\circ\lor)(b,\mathrm{false})\\
&=h(b\lor\mathrm{false})\\
&=h(b).
\end{aligned}
\]

Thus \(g(b)=h(b)\) for every Boolean \(b\), so by function extensionality,

\[
g=h.
\]

Hence

\[
\lor:\mathrm{Bool}\times\mathrm{Bool}\to\mathrm{Bool}
\]

is epic.

## Diagrammatic cancellation proof

The right inverse \(s\) makes the cancellation especially short:

\[
g\circ\lor=h\circ\lor.
\]

Compose both sides with \(s\):

\[
(g\circ\lor)\circ s=(h\circ\lor)\circ s.
\]

By associativity,

\[
g\circ(\lor\circ s)=h\circ(\lor\circ s).
\]

Since \(\lor\circ s=\operatorname{id}_{\mathrm{Bool}}\),

\[
g=h.
\]

## About your \(g\neq h\) argument

You were trying to argue:

\[
g\neq h
\quad\Longrightarrow\quad
g(\mathrm{true})\neq h(\mathrm{true})
\text{ or }
g(\mathrm{false})\neq h(\mathrm{false}).
\]

That works in ordinary set theory, but it is more indirect than necessary. You would then choose

\[
(b,\mathrm{false})
\]

for whichever Boolean \(b\) distinguishes \(g\) and \(h\).

The direct proof avoids contradiction and avoids enumerating both Boolean cases.

## Your non-monic proof

Your witness for failure of monicity is valid. Let

\[
p,q:\mathrm{Unit}\to\mathrm{Bool}\times\mathrm{Bool}
\]

be defined by

\[
p(*)=(\mathrm{true},\mathrm{false}),
\qquad
q(*)=(\mathrm{false},\mathrm{true}).
\]

Then \(p\neq q\), but

\[
\lor\circ p=\lor\circ q,
\]

because both pairs map to `true`. Therefore `or` is not monic.

So the final classification is:

\[
\boxed{\lor\text{ is epic but not monic}.}
\]


---

> [image: sediment://file_000000002bcc820c86b71bf5f77e60ae]
> What about my def kf right inverse correct?

<details><summary>💭 Thinking</summary>

**Clarifying right inverses**

For f:A→B, a right inverse g:B→A satisfies f∘g = id_B. Uniqueness isn’t required. If f has a right inverse, g is a section, and f usually forms a retraction.

**Clarified right inverses**

</details>

Yes. Your definition is correct.

Given a category \(\mathcal C\) and an arrow

\[
f:A\to B,
\]

a **right inverse of \(f\)** is an arrow

\[
g:B\to A
\]

such that

\[
f\circ g=\operatorname{id}_B.
\]

The word “right” refers to where \(g\) appears in the composite \(f\circ g\): it is written to the right of \(f\).

Existence is enough. The right inverse does **not** need to be unique.

For your `or` example,

\[
\lor:\mathrm{Bool}\times\mathrm{Bool}\to\mathrm{Bool},
\]

both of these are right inverses:

\[
g_1(b)=(b,\mathrm{false}),
\]

because

\[
b\lor\mathrm{false}=b,
\]

and

\[
g_2(b)=(\mathrm{false},b),
\]

because

\[
\mathrm{false}\lor b=b.
\]

Thus

\[
\lor\circ g_1=\operatorname{id}_{\mathrm{Bool}}
\quad\text{and}\quad
\lor\circ g_2=\operatorname{id}_{\mathrm{Bool}},
\]

while \(g_1\neq g_2\). So this is also a concrete demonstration that right inverses need not be unique.

A useful notation for your notes is

\[
\operatorname{RInv}(f)
=
\left\{
g:B\to A\mid f\circ g=\operatorname{id}_B
\right\}.
\]

Then:

\[
f\text{ has a right inverse}
\iff
\operatorname{RInv}(f)\neq\varnothing.
\]

An arrow with a right inverse is called a **split epimorphism**.

One additional fact:

> If \(f\) is monic and has a right inverse, then that right inverse is unique and \(f\) is an isomorphism.

Indeed, if \(g,h\) are both right inverses, then

\[
f\circ g=\operatorname{id}_B=f\circ h.
\]

Since \(f\) is monic, cancel \(f\) to obtain

\[
g=h.
\]

So your note “\(g\) doesn’t need to be unique” is correct; uniqueness follows under an extra condition such as monicity of \(f\).


---

> Why does having a right inverse mean epic?

Let

\[
f:A\to B
\]

have a right inverse

\[
r:B\to A,
\qquad
f\circ r=\operatorname{id}_B.
\]

To prove that \(f\) is epic, take arbitrary arrows

\[
g,h:B\to C
\]

and assume

\[
g\circ f=h\circ f.
\]

Because the two sides are arrows \(A\to C\), compose both sides with \(r:B\to A\):

\[
(g\circ f)\circ r=(h\circ f)\circ r.
\]

Using associativity,

\[
g\circ(f\circ r)=h\circ(f\circ r).
\]

Since \(f\circ r=\operatorname{id}_B\),

\[
g\circ\operatorname{id}_B
=
h\circ\operatorname{id}_B,
\]

so

\[
g=h.
\]

That is exactly the definition of \(f\) being epic.

The key mechanism is:

\[
(g\circ f)\circ r
=
g\circ(f\circ r)
=
g.
\]

The right inverse lets you remove \(f\) from the right side of a composite.

Diagrammatically:

\[
A\xrightarrow{f}B\xrightarrow[g]{h}C,
\qquad
B\xrightarrow{r}A,
\]

with

\[
B\xrightarrow{r}A\xrightarrow{f}B
=
\operatorname{id}_B.
\]

So:

\[
\boxed{\text{having a right inverse }\Longrightarrow\text{ epic}.}
\]

The converse is generally false: an epic arrow need not have a right inverse. Having a right inverse is the stronger property, called being a **split epimorphism**.


---

> [image: sediment://file_00000000c8c881f5a490360077f2e6da]
> Here is my attempt, and I would also like some help if there is a diagram way of doing the proof

<details><summary>💭 Thinking</summary>

**Explaining the diagram for functions**

I'm focusing on their notation for the diagram. I’ll walk through the function properties and identity, then explain the commuting diagram of mappings and inverses step by step.

**Explained the diagram for functions**

</details>

Your attempt is essentially correct. The main improvement is to keep the object types visible and avoid calling the right inverse \(f^{-1}\), since it may not be a genuine inverse.

Let

\[
f:A\to B
\]

and suppose \(f\) has a right inverse

\[
s:B\to A
\]

such that

\[
f\circ s=\operatorname{id}_B.
\]

To prove that \(f\) is epic, take arbitrary arrows

\[
g,h:B\to Z
\]

and assume

\[
g\circ f=h\circ f.
\]

The types are:

\[
A\xrightarrow{f}B
\overset{g,h}{\rightrightarrows}Z.
\]

Now precompose both sides with \(s:B\to A\):

\[
(g\circ f)\circ s=(h\circ f)\circ s.
\]

Then

\[
\begin{aligned}
(g\circ f)\circ s
&=g\circ(f\circ s)\\
&=g\circ\operatorname{id}_B\\
&=g,
\end{aligned}
\]

and similarly,

\[
(h\circ f)\circ s=h.
\]

Therefore \(g=h\), which proves that \(f\) is epic.

\[
\boxed{\text{right inverse} \implies \text{epic}}
\]

## Diagrammatic proof

First, the right-inverse triangle:

```text
        s
    B ─────▶ A
     ╲       │
      ╲id_B  │ f
       ╲     ▼
        ───▶ B
```

The equation represented by this triangle is

\[
f\circ s=\operatorname{id}_B.
\]

Now begin with the epicness test:

```text
A ──f──▶ B ──g──▶ Z
          ╰─h──▶ Z
```

Assume the two paths from \(A\) to \(Z\) agree:

\[
g\circ f=h\circ f.
\]

Attach \(s\) to the beginning of both paths:

```text
B ──s──▶ A ──f──▶ B ──g──▶ Z
                       ╰─h──▶ Z
```

The middle detour

```text
B ──s──▶ A ──f──▶ B
```

is just \(\operatorname{id}_B\). Therefore the two long paths simplify to

```text
B ──g──▶ Z
B ──h──▶ Z
```

and hence \(g=h\).

Another way to display the entire calculation is:

```text
B ──s──▶ A ──f──▶ B ──g──▶ Z
│                    │
│ id_B               │
└───────────────────▶B ──g──▶ Z
```

and likewise for \(h\).

## One terminology detail

Although \(s\) is written on the right in

\[
f\circ s,
\]

when reading arrows from input to output, \(s\) runs **first**:

\[
B\xrightarrow{s}A\xrightarrow{f}B.
\]

This is why the statement “compose the equality on the right with \(s\)” means

\[
(g\circ f)\circ s=(h\circ f)\circ s.
\]

Your algebra in the image has the correct core idea:

\[
(h\circ f)\circ s
=
h\circ(f\circ s)
=
h\circ\operatorname{id}_B
=
h.
\]

You only need to perform the same simplification on the \(g\)-side and conclude \(h=g\).


---

> How to read equality in diagrams?

In a categorical diagram, **equality means equality of paths with the same starting object and ending object**.

A diagram is said to **commute** when every pair of directed paths with the same endpoints gives the same composite arrow.

## Basic rule

Suppose the diagram contains

\[
A\xrightarrow{f}B\xrightarrow{g}C
\]

and also

\[
A\xrightarrow{h}C.
\]

```text
A ──f──▶ B
│         │
h         g
│         │
▼         ▼
C ═══════ C
```

Commutativity means

\[
g\circ f=h.
\]

Read the long path from \(A\) to \(C\):

1. first \(f:A\to B\);
2. then \(g:B\to C\);

so the composite is \(g\circ f\).

The direct path is \(h:A\to C\). Equality of the two paths means

\[
g\circ f=h.
\]

## Composition order

The diagram is read in travel order:

\[
A\xrightarrow{f}B\xrightarrow{g}C,
\]

but the formula is written

\[
g\circ f.
\]

Thus:

> travel through \(f\) first, then \(g\); write \(g\circ f\).

This reversed-looking notation is a common source of confusion.

---

## A commuting triangle

For a right inverse \(s:B\to A\) of \(f:A\to B\):

```text
       s
   B ─────▶ A
   │         │
id_B         f
   │         │
   ▼         ▼
   B ═══════ B
```

There are two paths from the upper \(B\) to the lower \(B\):

- direct path: \(\operatorname{id}_B\);
- path through \(A\): first \(s\), then \(f\), giving \(f\circ s\).

The triangle commutes precisely when

\[
f\circ s=\operatorname{id}_B.
\]

So the diagram is a visual representation of that equation.

---

## A commuting square

```text
A ──f──▶ B
│         │
u         v
│         │
▼         ▼
C ──g──▶ D
```

There are two paths from \(A\) to \(D\):

- across then down:

\[
v\circ f;
\]

- down then across:

\[
g\circ u.
\]

The square commutes when

\[
v\circ f=g\circ u.
\]

A good reading method is:

> Pick a starting corner and an ending corner. Write the composite for every route between them. A commuting diagram says those composites are equal.

---

## Parallel arrows

For epicness, you have:

```text
A ──f──▶ B ──g──▶ Z
          ╰─h──▶ Z
```

The two paths from \(A\) to \(Z\) are

\[
g\circ f
\qquad\text{and}\qquad
h\circ f.
\]

The assumption

\[
g\circ f=h\circ f
\]

says those two paths are equal.

Notice that \(g\) and \(h\) are **parallel arrows**: they have the same source and target,

\[
g,h:B\to Z.
\]

Only parallel arrows can be equal. An arrow \(A\to B\) cannot equal an arrow \(B\to Z\), because their types differ.

---

## Reading your epic proof diagrammatically

Suppose

\[
f:A\to B,\qquad s:B\to A,\qquad f\circ s=\operatorname{id}_B,
\]

and assume

\[
g\circ f=h\circ f.
\]

Start with the equal paths:

```text
A ──f──▶ B ──g──▶ Z
A ──f──▶ B ──h──▶ Z
```

Now attach the same arrow \(s:B\to A\) to the beginning of both paths:

```text
B ──s──▶ A ──f──▶ B ──g──▶ Z
B ──s──▶ A ──f──▶ B ──h──▶ Z
```

These composites are

\[
g\circ f\circ s
\qquad\text{and}\qquad
h\circ f\circ s.
\]

Because the middle triangle commutes,

\[
f\circ s=\operatorname{id}_B.
\]

Therefore the upper path simplifies to

\[
g\circ f\circ s
=
g\circ\operatorname{id}_B
=
g,
\]

and the lower path simplifies to

\[
h\circ f\circ s
=
h\circ\operatorname{id}_B
=
h.
\]

Hence \(g=h\).

## Compact visual vocabulary

- **Arrow:** a morphism.
- **Path:** a composite of arrows.
- **Parallel paths:** paths with the same start and endpoint.
- **Commuting diagram:** all parallel paths have equal composites.
- **Triangle commutes:** two routes between its endpoints are equal.
- **Square commutes:** going around either side gives the same morphism.
- **Identity path:** staying at an object, represented by \(\operatorname{id}\).

The central principle is:

\[
\boxed{\text{A commuting diagram is a collection of equations between paths.}}
\]


---

> So in the A -f-> B - g/h -> Z 
>
> We actually have to prove that g/h commute

Not quite. We do **not** start by proving that \(g\) and \(h\) commute.

Given

\[
A\xrightarrow{f}B\overset{g}{\underset{h}{\rightrightarrows}}Z,
\]

to prove \(f\) is epic, we:

1. Choose arbitrary \(g,h:B\to Z\).
2. **Assume the two paths from \(A\) to \(Z\) are equal**:

\[
g\circ f=h\circ f.
\]

So the larger diagram commutes after passing through \(f\).

3. Prove that

\[
g=h.
\]

The phrase “\(g\) and \(h\) commute” is not usually used. Since \(g\) and \(h\) are parallel arrows, the conclusion is simply that they are equal.

Visually:

```text
          g
A ──f──▶ B ───▶ Z
          └───▶ Z
            h
```

The assumption is:

```text
path A ─f→ B ─g→ Z
=
path A ─f→ B ─h→ Z
```

That is,

\[
g\circ f=h\circ f.
\]

Epicness says that this forces the remaining arrows to be equal:

\[
g=h.
\]

So the pattern is:

\[
\boxed{
\text{the two long paths commute}
\quad\Longrightarrow\quad
\text{the two final arrows are equal}
}
\]

For your right-inverse proof, the right inverse lets you remove the shared initial segment \(f\).


---

> I mean that we have to prove that they are parallel, in order for the           g
> A ──f──▶ B ───▶ Z
>           └───▶ Z
>             h
>
> To be valid. 
>
> To start we only have the square with A -F-> B twice that then go to Z with two edges g and h. So while that diagram shows gf = hf now we have to show g parallel to h

<details><summary>💭 Thinking</summary>

**Clarifying diagram syntax**

The user wants to ensure proper conceptual understanding: objects and arrows in a diagram must be clarified, especially with parallelism. Commutativity applies only to composite equalities, not unrelated codomains.

**Clarified diagram syntax**

</details>

Exactly: \(g\) and \(h\) must be parallel. But this is **part of the setup**, not something proved from epicness.

The definition is:

\[
f:A\to B \text{ is epic}
\]

when, for every object \(Z\) and every pair of arrows

\[
g,h:B\to Z,
\]

we have

\[
g\circ f=h\circ f \implies g=h.
\]

Writing

\[
g,h:B\to Z
\]

already says that \(g\) and \(h\) are parallel: same domain \(B\), same codomain \(Z\).

## Why the equality already requires parallelism

Suppose

\[
f:A\to B.
\]

For \(g\circ f\) to exist, \(g\) must start at \(B\):

\[
g:B\to Z.
\]

For \(h\circ f\) to exist, \(h\) must also start at \(B\):

\[
h:B\to Z'.
\]

But now to write

\[
g\circ f=h\circ f,
\]

the two composite arrows must have the same source and target. Their source is already \(A\), so their targets must agree:

\[
Z=Z'.
\]

Thus the equality is only well-typed when

\[
g,h:B\to Z.
\]

So parallelism is encoded in the types.

## About drawing the objects twice

You might initially draw:

```text
A ──f──▶ B ──g──▶ Z
A ──f──▶ B ──h──▶ Z
```

The two occurrences of \(A\), \(B\), and \(Z\) are not intended to be different objects. They are repeated visually to show the two paths.

You can collapse the repeated objects into:

```text
          g
A ──f──▶ B ───▶ Z
          └───▶
            h
```

This is valid because both rows used:

\[
f:A\to B,\qquad g,h:B\to Z.
\]

If they were genuinely different objects, you would need different names:

```text
A₁ ──f₁──▶ B₁ ──g──▶ Z₁
A₂ ──f₂──▶ B₂ ──h──▶ Z₂
```

Then \(g\circ f_1=h\circ f_2\) would not even be a meaningful equality unless the sources and targets were identified appropriately.

## The logical structure

For epicness:

\[
\underbrace{g,h:B\to Z}_{\text{assume they are parallel}}
\]

\[
\underbrace{g\circ f=h\circ f}_{\text{assume the long paths are equal}}
\]

\[
\underbrace{g=h}_{\text{prove the parallel arrows are equal}}.
\]

So you are right that parallelism is required. The precise correction is that we do not derive it later; we specify it when choosing \(g\) and \(h\).


---

> [image: sediment://file_000000004a74822f88bbeb6ce37f254c]
> Regarding decode being monic, we can’t fully derive it from encode/decode being isomorphic, we need to know a bit more about the encoding function, no? Or we could derive from an information theoretic point of view, that encoding a tree reduces the amount of information, but on the other hand we could define a decoding that is valid on every input of bytes and projects to a different tree, while not being monic, for example just a long string of children with each children being a byte, although then that would not be isomorphic with encode. 
>
> I also wonder if we can describe the “quality” of a fingerprinting algorithm which can be used as a way to project f down to a faster more monic projection of bytes to trees (still not monic since there’s hash collisions) and also formalizing the “quality” of the fingerprint (maybe it’s an enriched category?)

<details><summary>💭 Thinking</summary>

**Untangling encoding concepts**

I’m focusing on properly explaining encoding and decoding trees. If encoding and decoding are isomorphic, then they are both injective and surjective functions, but I’ll clarify if this holds properly.

**Untangled encoding concepts**

</details>

<details><summary>💭 Thinking</summary>

**Exploring encoding and hashing**

I’m explaining how encoding and hashing affect trees and bytes. While hashes are surjective (same trees, same digest), they aren’t injective, so collisions can happen. The category approach helps frame "quality" in this context.

**Explored encoding and hashing**

</details>

Your reasoning is close. The key distinction is between **having one round-trip law** and actually being **isomorphic**.

Let

\[
e:\mathrm{Tree}\to\mathrm{Bytes},
\qquad
d:\mathrm{Bytes}\to\mathrm{Tree}
\]

with

\[
d\circ e=\operatorname{id}_{\mathrm{Tree}}.
\]

This tells us:

\[
e\text{ is monic},\qquad d\text{ is epic}.
\]

It does **not** tell us that \(d\) is monic.

If \(e\) and \(d\) really were isomorphisms, meaning we also had

\[
e\circ d=\operatorname{id}_{\mathrm{Bytes}},
\]

then \(d\) would automatically be monic.

## Why `decode` is usually not monic

In the category of sets/types and total functions, \(d\) is monic exactly when it is injective:

\[
d(x)=d(y)\implies x=y.
\]

That would mean no two byte strings decode to the same tree. Usually this fails because of:

- alternative encodings;
- ignored whitespace or metadata;
- invalid bytes mapped to a default tree;
- redundant representations;
- normalization.

For example:

\[
\begin{aligned}
e(\mathrm{false})&=00,\\
e(\mathrm{true})&=01,
\end{aligned}
\]

but define

\[
\begin{aligned}
d(00)&=\mathrm{false},&
d(10)&=\mathrm{false},\\
d(01)&=\mathrm{true},&
d(11)&=\mathrm{true}.
\end{aligned}
\]

Then

\[
d\circ e=\operatorname{id}_{\mathrm{Bool}},
\]

but \(d\) is not monic because

\[
d(00)=d(10)
\quad\text{while}\quad
00\neq10.
\]

In fact, under the round-trip law \(d\circ e=\operatorname{id}\), if \(d\) were also monic, then \(d\) and \(e\) would necessarily be isomorphisms.

Indeed,

\[
d\circ(e\circ d)
=
(d\circ e)\circ d
=
d
=
d\circ\operatorname{id}_{\mathrm{Bytes}}.
\]

If \(d\) is monic, cancel \(d\):

\[
e\circ d=\operatorname{id}_{\mathrm{Bytes}}.
\]

So requiring `decode` to be monic is extremely strong: it says every byte string is already a unique valid encoding.

## Canonicalization really is a projection

Your canonicalization idea has a clean categorical formulation. Define

\[
c=e\circ d:\mathrm{Bytes}\to\mathrm{Bytes}.
\]

Then

\[
\begin{aligned}
c\circ c
&=e\circ d\circ e\circ d\\
&=e\circ(d\circ e)\circ d\\
&=e\circ\operatorname{id}_{\mathrm{Tree}}\circ d\\
&=e\circ d\\
&=c.
\end{aligned}
\]

Thus \(c\) is **idempotent**:

\[
c^2=c.
\]

That is the precise sense in which it is a projection onto canonical byte strings.

Let

\[
C=\operatorname{im}(e)\subseteq\mathrm{Bytes}.
\]

After restricting to \(C\), the maps

\[
\mathrm{Tree}\xrightarrow{e}C
\qquad\text{and}\qquad
C\xrightarrow{d}\mathrm{Tree}
\]

are isomorphisms.

So the useful picture is:

\[
\mathrm{Bytes}
\xrightarrow{c}
C
\cong
\mathrm{Tree}.
\]

The full decoder may not be monic, but the decoder restricted to canonical encodings is.

## Information-theoretic interpretation

The law

\[
d\circ e=\operatorname{id}_{\mathrm{Tree}}
\]

already says that encoding loses no information **about the tree**. Every distinction between trees survives encoding.

It does not mean the byte representation is smaller. It may be much larger. “Amount of information” in the Shannon sense also requires a probability distribution, while the categorical statement is simply exact recoverability.

The information loss occurs in the other direction:

\[
d:\mathrm{Bytes}\to\mathrm{Tree}
\]

may discard distinctions between byte strings.

## Fingerprints

A fingerprint normally has the form

\[
\phi:\mathrm{Tree}\to\mathrm{Digest},
\qquad
\phi=h\circ e,
\]

or, for arbitrary byte strings,

\[
\psi=h\circ c:
\mathrm{Bytes}\to\mathrm{Digest}.
\]

A hash cannot make a map “more monic.” Composition downstream can only preserve or lose distinctions.

For example, if

\[
c(x)=c(y),
\]

then automatically

\[
h(c(x))=h(c(y)).
\]

And even if \(c(x)\neq c(y)\), the hash may introduce a new collision:

\[
h(c(x))=h(c(y)).
\]

So the fingerprint is less informative, but faster to compare.

The usual algorithm is:

1. Compare fingerprints.
2. If they differ, the trees differ.
3. If they agree, compare the full canonical representation to rule out collisions.

## Formalizing “how close to monic”

Monicity itself is binary: a map is monic or it is not. But a useful measure of its failure is its **kernel relation**:

\[
K_\phi
=
\{(x,y)\mid \phi(x)=\phi(y)\}.
\]

A map is monic exactly when

\[
K_\phi=\{(x,x)\mid x\in X\},
\]

the diagonal relation.

Given two fingerprints

\[
\phi_1:X\to D_1,
\qquad
\phi_2:X\to D_2,
\]

you can say that \(\phi_1\) is at least as discriminating as \(\phi_2\) when

\[
K_{\phi_1}\subseteq K_{\phi_2}.
\]

Equivalently, in many situations, \(\phi_2\) factors through \(\phi_1\):

\[
\phi_2=q\circ\phi_1.
\]

Then everything distinguished by \(\phi_2\) is also distinguished by \(\phi_1\), while \(\phi_1\) may distinguish more.

This gives a preorder of fingerprints by informational quality.

For quantitative quality, choose a distribution \(\mu\) over inputs and measure something such as

\[
\Pr_{x,y\sim\mu}
\bigl[
\phi(x)=\phi(y)\mid x\neq y
\bigr],
\]

or measure maximum bucket size:

\[
\max_d |\phi^{-1}(d)|.
\]

For cryptographic hashes, the relevant notion is often not absence of collisions—collisions must exist for a finite digest—but the computational difficulty of finding one.

An enriched category could track cost and collision risk, but it requires choosing how those quantities compose. The kernel-partition preorder is the more direct categorical model of “how much distinction a fingerprint preserves.”


---

> So here tree and bytes are sets and thus we have this iso -> epic and monic property which doesn’t hold for other categories?

<details><summary>💭 Thinking</summary>

**Clarifying category properties**

I’m explaining that the iso → monic + epic relationship doesn’t hold for all categories. In a Set, both monic and epic imply iso. But in other contexts, the mapping might not work the same way.

**Clarified category properties**

</details>

Not quite. The implication

\[
\boxed{\text{isomorphism} \implies \text{monic and epic}}
\]

holds in **every category**, not only in `Set`.

What is special about `Set` is the converse:

\[
\boxed{\text{monic and epic} \implies \text{isomorphism}}
\]

This converse does not hold in every category.

A category with that converse is called **balanced**.

## For `Tree` and `Bytes`

If we treat

- `Tree` and `Bytes` as sets/types, and
- arrows as total deterministic functions,

then we are working in `Set`, or something Set-like.

In this setting:

\[
\text{monic}\iff\text{injective},
\qquad
\text{epic}\iff\text{surjective},
\]

and therefore

\[
\text{monic and epic}
\iff
\text{bijective}
\iff
\text{isomorphism}.
\]

But be careful: the law

\[
\operatorname{decode}\circ\operatorname{encode}
=
\operatorname{id}_{Tree}
\]

alone does **not** say that `encode` and `decode` are isomorphisms.

It only gives:

\[
\operatorname{encode}\text{ is monic},
\qquad
\operatorname{decode}\text{ is epic}.
\]

For an isomorphism, you also need

\[
\operatorname{encode}\circ\operatorname{decode}
=
\operatorname{id}_{Bytes}.
\]

That second equation is usually false because arbitrary byte strings may be invalid or noncanonical.

## Why an isomorphism is always monic

Suppose \(f:A\to B\) has inverse \(f^{-1}:B\to A\). If

\[
f\circ g=f\circ h,
\]

compose with \(f^{-1}\):

\[
f^{-1}\circ f\circ g
=
f^{-1}\circ f\circ h,
\]

so

\[
g=h.
\]

Therefore \(f\) is monic.

Similarly, if

\[
g\circ f=h\circ f,
\]

compose on the right with \(f^{-1}\):

\[
g\circ f\circ f^{-1}
=
h\circ f\circ f^{-1},
\]

so

\[
g=h.
\]

Therefore \(f\) is epic.

Nothing in this proof depends on elements or sets.

## Where the converse fails

Consider the one-object category constructed from \((\mathbb N,+,0)\). Every natural number \(n\) is an arrow, and composition is addition.

Cancellation gives

\[
n+g=n+h\implies g=h
\]

and

\[
g+n=h+n\implies g=h.
\]

So every arrow is monic and epic. But only \(0\) is invertible, because for \(n>0\) there is no \(m\in\mathbb N\) satisfying

\[
n+m=0.
\]

Thus:

\[
\text{monic and epic}\centernot\implies\text{isomorphism}.
\]

The correct summary is:

\[
\boxed{
\begin{aligned}
&\text{In every category: iso }\implies\text{ monic and epic}.\\
&\text{In Set: monic and epic }\implies\text{ iso}.\\
&\text{In arbitrary categories: the converse may fail.}
\end{aligned}
}
\]


---

> How can we categorically study the amount of collisions of different hash functions ?

```json
{"system1_search_query":[{"q":"site:arxiv.org categorical probability Markov categories collision probability hash functions kernel pairs"},{"q":"site:arxiv.org kernel pairs category theory equivalence relations regular categories"},{"q":"site:stacks.math.columbia.edu kernel pair morphism category theory"},{"q":"site:arxiv.org information orders partitions category theory hash functions collisions"}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Searched multiple sources for information on hash collisions and Markov categories**

</details>

Categorically, the primary object is not a number but the **relation of which inputs collide**.

Let

\[
h:X\to D
\]

be a hash function.

## 1. The kernel pair records every collision

Form the pullback of \(h\) along itself:

\[
K_h:=X\times_D X.
\]

Diagrammatically,

```text
Kₕ ──π₂──▶ X
│          │
π₁         h
│          │
▼          ▼
X ───h───▶ D
```

In `Set`,

\[
K_h=\{(x,y)\in X\times X\mid h(x)=h(y)\}.
\]

Thus \(K_h\) literally consists of all colliding pairs, including the unavoidable pairs \((x,x)\). This construction is called the **kernel pair** of \(h\); it is a pullback, and pullbacks in `Set` are sets of matching pairs. citeturn471274view3

The diagonal

\[
\Delta_X=\{(x,x)\mid x\in X\}
\]

is always contained in \(K_h\). The hash is monic precisely when

\[
K_h=\Delta_X,
\]

meaning there are no collisions between distinct inputs.

So:

\[
\boxed{\text{failure of monicity is measured structurally by }K_h.}
\]

---

## 2. Comparing two hashes by refinement

Suppose

\[
h_1:X\to D_1,
\qquad
h_2:X\to D_2.
\]

Say \(h_1\) is **at least as discriminating as** \(h_2\) when

\[
K_{h_1}\subseteq K_{h_2}.
\]

This says:

> Whenever \(h_1\) collides, \(h_2\) also collides.

Equivalently, \(h_1\) has no more collisions than \(h_2\).

After restricting each codomain to the actual image of the hash, this is equivalent to the existence of a postprocessing map

\[
q:\operatorname{im}(h_1)\to\operatorname{im}(h_2)
\]

such that

\[
h_2=q\circ h_1.
\]

Diagrammatically,

```text
           h₁
      X ───────▶ im(h₁)
       ╲            │
        ╲ h₂        │ q
         ╲          ▼
          ─────▶ im(h₂)
```

Thus \(h_2\) can be obtained by taking the information produced by \(h_1\) and discarding some of it.

This produces a preorder—or, after identifying equivalent hashes, a poset—of hash functions ordered by informational discrimination. It is the deterministic analogue of comparing statistical experiments by postprocessing or “garbling,” which is treated categorically using Markov categories and the Blackwell order. citeturn396437search4turn554207view4

### Data processing cannot improve a hash

For any postprocessing function \(q\),

\[
K_h\subseteq K_{q\circ h}.
\]

Indeed,

\[
h(x)=h(y)
\implies
q(h(x))=q(h(y)).
\]

Postprocessing may introduce collisions, but cannot remove existing ones.

### Combining two hashes

The combined fingerprint

\[
\langle h_1,h_2\rangle:X\to D_1\times D_2
\]

satisfies

\[
K_{\langle h_1,h_2\rangle}
=
K_{h_1}\cap K_{h_2}.
\]

Two inputs collide under the combined fingerprint only when they collide under both components.

---

## 3. Turning collision structure into a number

Category theory supplies \(K_h\). To speak about the **amount** of collisions, add cardinality or probability.

Assume \(X\) is finite with

\[
|X|=N.
\]

For each digest \(d\), let

\[
n_d=|h^{-1}(d)|
\]

be the size of its collision bucket.

Then

\[
|K_h|=\sum_{d\in D} n_d^2.
\]

The number of ordered collisions between distinct inputs is

\[
|K_h|-N
=
\sum_d n_d(n_d-1).
\]

The number of unordered distinct collision pairs is

\[
\frac12\sum_d n_d(n_d-1).
\]

If two distinct inputs are chosen uniformly, the collision probability is

\[
\Pr[h(X_1)=h(X_2)\mid X_1\neq X_2]
=
\frac{|K_h|-N}{N(N-1)}.
\]

So cardinality applied to the categorical kernel pair gives an exact numerical collision count.

### Example

Take \(X=\{0,\dots ,7\}\).

For

\[
h_2(x)=x\bmod 2,
\]

the fibers have sizes \(4,4\). Therefore

\[
|K_{h_2}|=4^2+4^2=32,
\]

and the distinct-input collision probability is

\[
\frac{32-8}{8\cdot7}=\frac37.
\]

For

\[
h_4(x)=x\bmod 4,
\]

the fibers have sizes \(2,2,2,2\), so

\[
|K_{h_4}|=4\cdot2^2=16,
\]

and

\[
\Pr[\text{collision}\mid X_1\neq X_2]
=
\frac{16-8}{56}
=
\frac17.
\]

Moreover,

\[
h_2=q\circ h_4,
\qquad q(z)=z\bmod2.
\]

Thus the factorization agrees with the numerical conclusion: \(h_4\) is more discriminating than \(h_2\).

---

## 4. Workload-dependent collision probability

Uniform inputs are often unrealistic. Let

\[
\mu:X\to[0,1]
\]

be an input distribution, and let

\[
p_d=\sum_{x:h(x)=d}\mu(x)
\]

be the induced probability of digest \(d\).

For independent inputs \(X_1,X_2\sim\mu\),

\[
\Pr[h(X_1)=h(X_2)]
=
\sum_d p_d^2.
\]

This includes the case \(X_1=X_2\). Conditioning on distinct inputs gives

\[
\Pr[h(X_1)=h(X_2)\mid X_1\neq X_2]
=
\frac{
\sum_d p_d^2-\sum_x\mu(x)^2
}{
1-\sum_x\mu(x)^2
}.
\]

The quantity

\[
-\log\left(\sum_d p_d^2\right)
\]

is the order-2 Rényi entropy of the hash output. Larger order-2 entropy means lower collision probability for independent samples.

Markov categories provide a categorical setting for probability channels, and enriched Markov categories can incorporate quantitative notions such as Shannon and Rényi entropy, divergences, and data-processing inequalities. citeturn396437search0turn471274view0

In the finite stochastic category, collision probability can be pictured as

```text
1 ──μ⊗μ──▶ X×X ──h×h──▶ D×D ──equal?──▶ Bool
```

The probability assigned to `true` is the collision probability. It is important to use two independent samples \(\mu\otimes\mu\); copying one sample would trivially produce identical inputs.

---

## 5. Several different notions of “quality”

One scalar is rarely sufficient. Useful measures include:

\[
\text{total collision pairs}
=
\sum_d n_d(n_d-1),
\]

\[
\text{largest bucket}
=
\max_d n_d,
\]

\[
\text{number of occupied outputs}
=
|\operatorname{im}(h)|,
\]

\[
\text{average collision probability}
=
\sum_d p_d^2,
\]

and the full fiber-size profile

\[
(n_d)_{d\in D}.
\]

These capture different failure modes. A hash can have good average behavior while containing one very large bad bucket.

The kernel pair is stronger than all of these numbers because it remembers **exactly which inputs** collide, not merely how many.

---

## 6. Do you need an enriched category?

Not for the basic comparison.

The category of hashes from a fixed input \(X\) can be defined as follows:

- Objects are surjective hashes \(h:X\twoheadrightarrow Q\), representing their actual occupied buckets.
- An arrow from \(h_1\) to \(h_2\) is a function \(q:Q_1\to Q_2\) satisfying

\[
h_2=q\circ h_1.
\]

Because \(h_1\) is surjective, such a \(q\) is unique when it exists. Consequently this category is essentially a poset: the lattice of partitions of \(X\).

Enrichment becomes useful when attaching quantitative values such as:

- collision probability;
- entropy loss;
- execution time;
- digest size;
- memory cost.

One could enrich over an ordered cost structure, provided the chosen quantities behave coherently under composition. Divergence- or metric-enriched Markov categories are an established way of combining categorical information flow with entropy and statistical distance. citeturn471274view0

---

## 7. Cryptographic collision resistance is different

The kernel pair answers:

> How many collisions exist, and which inputs collide?

Cryptographic security asks:

> How difficult is it for an efficient adversary to find one?

Every function from a sufficiently large input set to a finite digest set has collisions. A cryptographic hash is useful because those collisions are intended to be computationally difficult to discover.

A possible quantitative profile is

\[
\operatorname{Adv}^{\mathrm{coll}}_h(t)
=
\sup_{\substack{A\\\operatorname{cost}(A)\le t}}
\Pr\left[
A\text{ outputs }x\neq y
\text{ with }h(x)=h(y)
\right].
\]

Two hashes may have identical fiber sizes and identical kernel-pair cardinalities while having very different adversarial search difficulty.

Therefore:

\[
\boxed{
\begin{array}{l}
\text{kernel pair}=\text{extensional collision structure},\\
\text{probability/entropy}=\text{average collision quality},\\
\text{resource-sensitive model}=\text{computational collision resistance}.
\end{array}
}
\]

For cache fingerprints or deduplication, the probabilistic/kernel-pair model is often the relevant one. For cryptographic hashing, a computational or resource-sensitive structure must be added.


---

> Fastest learning paths / building intuition around markov categories. Also, where does topos theory enter the picture?

```json
{"system1_search_query":[{"q":"site:arxiv.org Markov categories Fritz introduction paper"},{"q":"site:arxiv.org synthetic probability theory Markov categories copy delete"},{"q":"site:arxiv.org quasi-Borel spaces probability monad higher-order probabilistic programming"},{"q":"site:arxiv.org topos probability monad stochastic maps"}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Searched resources on Markov categories, topos theory, and related sites**

</details>

## Fastest route: learn `FinStoch`, not general measure theory

For your current interests—hashes, information loss, programming, channels—the highest-yield path is:

\[
\text{finite stochastic matrices}
\longrightarrow
\text{string diagrams}
\longrightarrow
\text{conditioning/independence}
\longrightarrow
\text{entropy and enrichment}.
\]

Do **not** begin with topos theory. It is a later branch, not a prerequisite.

---

# A roughly 10-hour path

## 1. Channels as probabilistic programs — 90 minutes

Work in the category \(\mathbf{FinStoch}\):

- objects: finite types or alphabets;
- morphisms \(f:X\to Y\): stochastic channels;
- concretely:

\[
f(y\mid x)\geq 0,
\qquad
\sum_y f(y\mid x)=1.
\]

Programming interpretation:

```text
Channel<X,Y> = X -> Distribution<Y>
```

Composition is probabilistic bind:

\[
(g\circ f)(z\mid x)
=
\sum_y g(z\mid y)f(y\mid x).
\]

That is simply “run \(f\), then feed its random output into \(g\).” Perrone’s introductory section develops Markov categories directly from finite alphabets, noisy channels, states, sequential composition, and parallel composition. citeturn323687view3turn310146view2

### Exercises

Implement or calculate:

1. A binary symmetric channel that flips a bit with probability \(p\).
2. Compose two such channels.
3. Calculate the effective flip probability.
4. Represent an ordinary function as a stochastic matrix containing only \(0\)s and \(1\)s.
5. Verify that ordinary function composition agrees with stochastic composition.

---

## 2. Copying is the central intuition — 90 minutes

Every object \(X\) has a copy operation

\[
\Delta_X:X\to X\otimes X,
\qquad
x\mapsto(x,x),
\]

and a discard operation

\[
!_X:X\to I.
\]

The key distinction is between these two processes.

### Sample once, then copy

\[
X\xrightarrow{f}Y\xrightarrow{\Delta_Y}Y\otimes Y.
\]

This produces

\[
(y,y):
\]

the two outputs are always identical.

### Copy the input, then sample twice

\[
X\xrightarrow{\Delta_X}X\otimes X
\xrightarrow{f\otimes f}Y\otimes Y.
\]

This performs two independent random runs of \(f\), conditional on the same input.

These are generally unequal:

\[
\Delta_Y\circ f
\neq
(f\otimes f)\circ\Delta_X.
\]

For ordinary deterministic functions they are equal. This yields the Markov-categorical definition:

\[
f\text{ deterministic}
\quad\Longleftrightarrow\quad
\Delta_Y\circ f
=
(f\otimes f)\circ\Delta_X.
\]

This “sample once versus sample twice” distinction is probably the single most important intuition to acquire. Recent introductions emphasize that stochastic processes cannot generally commute with copying, while deterministic processes can. citeturn461076view6

### Exercise

Take a fair coin source \(c:I\to\mathrm{Bool}\).

Calculate the two joint distributions:

\[
\Delta\circ c
\qquad\text{and}\qquad
c\otimes c.
\]

The first gives:

\[
P(00)=P(11)=\frac12.
\]

The second gives:

\[
P(00)=P(01)=P(10)=P(11)=\frac14.
\]

---

## 3. Learn four diagram operations — 2 hours

You only need four operations initially:

### Sequential composition

```text
X ──f──▶ Y ──g──▶ Z
```

### Parallel composition

```text
X ──f──▶ Y
A ──g──▶ B
```

represents

\[
f\otimes g:X\otimes A\to Y\otimes B.
\]

### Copy

A wire branches, meaning the **same obtained value** is used twice.

### Discard

A wire terminates, corresponding to marginalization.

For example, from a joint state

\[
p:I\to X\otimes Y,
\]

discarding \(Y\) gives the \(X\)-marginal:

\[
p_X
=
(\operatorname{id}_X\otimes !_Y)\circ p.
\]

At this stage, redraw elementary probability calculations as diagrams:

- joint distributions;
- marginals;
- independent products;
- Markov chains;
- noisy observations.

Markov-category string diagrams are intended to encode information flow and causal structure, with boxes representing channels and wires representing typed random data. citeturn461076view1turn310146view1

---

## 4. Conditioning and Bayesian inversion — 2 hours

A joint channel

\[
p:I\to X\otimes Y
\]

may factor as

\[
p(x,y)=p_X(x)\,p(y\mid x).
\]

Diagrammatically, one first samples \(X\), copies it, and uses one copy to produce \(Y\).

The resulting channel

\[
c:X\to Y
\]

is a **conditional** or **disintegration**.

Then study Bayesian inversion:

\[
c:X\to Y
\]

together with a prior

\[
p:I\to X
\]

produces a reverse channel

\[
c^\dagger_p:Y\to X.
\]

The subscript matters:

> Bayesian inversion is not usually an inverse of \(c\); it depends on the prior.

Cho and Jacobs’ paper is useful here because it develops disintegration and Bayesian inversion diagrammatically and applies them to a concrete naive Bayes classifier. citeturn461076view5

### Exercise

Use:

\[
P(D)=0.01,\qquad
P(+\mid D)=0.99,\qquad
P(+\mid\neg D)=0.05
\]

and derive \(P(D\mid +)\) both numerically and as a channel inversion relative to the prior.

---

## 5. Conditional independence and DAGs — 90 minutes

Learn to read a Bayesian network as a factorization.

For example,

```text
      Z
     / \
    X   Y
```

means a joint distribution factors as

\[
P(x,y,z)=P(z)P(x\mid z)P(y\mid z).
\]

It therefore expresses

\[
X\perp Y\mid Z.
\]

The categorical treatment generalizes DAGs to arbitrary string diagrams of channels, and categorical \(d\)-separation becomes a graphical connectivity criterion. citeturn310146view1

For a fast pass, read:

- Section 2 of *The d-separation criterion in categorical probability*;
- then examples from Section 5;
- leave the completeness theorem for later.

---

## 6. Return to hashes and information loss — 2 hours

Now study your original question about fingerprint quality.

For a deterministic hash

\[
h:X\to D,
\]

you can first examine its collision relation categorically through the kernel pair

\[
X\times_D X.
\]

Then add quantitative structure:

- entropy;
- divergence;
- collision probability;
- mutual information;
- data-processing inequalities.

Perrone’s *Markov Categories and Entropy* is particularly suited to this direction. It begins with a self-contained Markov-category introduction and then equips hom-sets with divergences or metrics, allowing one to quantify how far diagrams are from commuting and how far channels are from determinism or independence. citeturn461076view2turn323687view3

For you, the useful reading order is:

1. Section 1: background;
2. Section 2.1: data processing;
3. Section 3: mutual information;
4. Section 4: entropy as distance from determinism.

---

# Minimal reading sequence

### First

**Perrone, “Markov Categories and Entropy,” Section 1.**

It is compact, concrete, uses `FinStoch`, and assumes no prior category theory. citeturn461076view2

### Second

**Fritz, “A synthetic approach to Markov kernels…”**

Read only:

- Section 2: Markov categories;
- Section 3: probability monads/Kleisli examples;
- Section 10: deterministic morphisms;
- Section 12: conditional independence.

Skip the long measure-theoretic and statistical portions on the first pass. The paper’s full scope includes conditioning, almost-sure equality, sufficient statistics, and several classical statistical theorems. citeturn310146view0

### Third

Choose based on interest:

- causal models: Fritz–Klingler;
- Bayesian inversion: Cho–Jacobs;
- entropy/hashes: Perrone;
- probabilistic programming: quasi-Borel spaces.

---

# Where topos theory enters

## It does not enter at the basic level

A Markov category is generally **not a topos**, and usually is not even cartesian.

This is not accidental.

In any cartesian category, every arrow automatically preserves copying:

\[
\Delta_Y\circ f
=
(f\times f)\circ\Delta_X.
\]

Thus every arrow behaves deterministically with respect to the diagonal.

But in a stochastic category, this equality should fail for genuinely random channels:

\[
\text{sample once and copy}
\neq
\text{sample independently twice}.
\]

This is why stochastic channels are modeled in a symmetric monoidal category with designated copy/discard maps, rather than simply as all arrows of a cartesian category. citeturn461076view6

So the division is roughly:

\[
\boxed{
\begin{array}{c}
\text{topos/cartesian category}\\
\text{all arrows copy naturally}
\end{array}}
\qquad\text{versus}\qquad
\boxed{
\begin{array}{c}
\text{Markov category}\\
\text{only deterministic arrows preserve copying}
\end{array}}
\]

---

## Entry point 1: a deterministic base plus a probability monad

A common construction begins with a deterministic category \(\mathcal E\) and a probability monad \(P\).

The probabilistic category is its Kleisli category:

\[
\mathrm{Kl}(P)(X,Y)
=
\mathcal E(X,PY).
\]

Conceptually:

```text
deterministic function:
X ─────────▶ Y

probabilistic program:
X ─────────▶ P(Y)
```

The base category \(\mathcal E\) handles:

- deterministic functions;
- products;
- types;
- possibly higher-order functions and logical structure.

The Kleisli category handles:

- sampling;
- stochastic channels;
- probabilistic composition.

Under suitable conditions on the probability monad, this Kleisli category is a Markov category. The relationship between probability monads, Kleisli categories, and representable Markov categories is developed explicitly in work on representable Markov categories. citeturn209662academia31

A topos can potentially serve as such a deterministic universe, provided it carries an appropriate probability construction. But “being a topos” alone does not automatically supply a useful probability monad.

---

## Entry point 2: higher-order probabilistic programming

Ordinary measurable spaces are not cartesian closed, so they do not naturally support function types such as

\[
X\Rightarrow Y
\]

together with continuous probability.

Quasi-Borel spaces were introduced to provide a cartesian-closed deterministic category supporting higher-order functions and continuous probability distributions. citeturn323687view4turn310146view3

This is adjacent to the role normally played by a topos in programming-language semantics:

- a rich deterministic type universe;
- exponentials/function spaces;
- internal reasoning;
- a probability monad layered on top.

For computer science, quasi-Borel spaces are likely a more direct next step than general topos theory.

---

## Entry point 3: sheaves and varying sample spaces

A more explicitly topos-theoretic approach uses **probability sheaves**.

The idea is that random variables are not attached to one permanently fixed global sample space. Instead, they vary over a site of possible sample spaces or contexts, with restriction and gluing conditions.

This is useful when:

- sample spaces grow dynamically;
- fresh names or resources are generated;
- information is contextual;
- local probabilistic descriptions must glue consistently;
- one wants an internal logic of random variables.

Recent work explicitly connects the channel-centered Markov-category picture with the random-variable-centered probability-sheaf picture: suitable Markov categories generate categories of abstract sample spaces over which probability sheaves can be studied. citeturn310146view4

A useful slogan is:

\[
\begin{array}{ll}
\textbf{Markov category:}
&\text{channels and information flow are primary;}\\[2mm]
\textbf{probability sheaf/topos:}
&\text{random variables across contexts are primary.}
\end{array}
\]

---

# Practical decision rule

Study **Markov categories first** when your questions involve:

- channels;
- Bayesian networks;
- conditional independence;
- hashes and information loss;
- stochastic programs;
- causal diagrams;
- entropy and data processing.

Add **topos/sheaf theory later** when your questions involve:

- internal logical reasoning;
- context-dependent random variables;
- local-to-global compatibility;
- higher-order or dependent probabilistic types;
- dynamically varying sample spaces;
- constructive foundations.

For your present thread, the most efficient sequence is:

\[
\boxed{
\mathbf{FinStoch}
\to
\text{copy/discard diagrams}
\to
\text{conditioning}
\to
\text{entropy-enriched Markov categories}
\to
\text{probability monads/QBS}
\to
\text{probability sheaves/toposes}.
}
\]

