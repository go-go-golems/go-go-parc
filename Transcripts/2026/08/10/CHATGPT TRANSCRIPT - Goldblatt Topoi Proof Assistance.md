# Goldblatt Topoi Proof Assistance

- URL: https://chatgpt.com/c/6a79b139-ef64-83ea-aeb6-7a36b3a26de3
- Created: 2026-08-10T11:09:04.634Z

---

> [image: sediment://file_000000003b84822f9c93be535d4f6ecf]
> I’m trying to prove the thing in red, goldblatt topoi. Help me by commenting on what I wrote, and potentially helping me along

<details><summary>💭 Thinking</summary>

**Clarifying the proof**

I’m reading the red statement as “every equalizer is monic.” The key step is to take arrows $d_1,d_2:D\to E$ with $i d_1=i d_2$; the equalizer’s uniqueness then forces $d_1=d_2$.

**Clarified the proof**

**Refining the viewpoint**

I’m separating two ideas: equalizers are unique up to isomorphism, but that isn’t needed here. In Set, $E$ is a useful subset intuition; categorically, the universal property defines the equalizer arrow.

**Refined the viewpoint**

</details>

Yes. Your setup is essentially correct; the main thing missing is to use the **uniqueness clause in the equalizer universal property**. That is exactly what gives monicity.

For the equalizer
$$
E\xrightarrow{i}A \overset{f}{\underset{g}{\rightrightarrows}} B,
\qquad fi=gi,
$$
you want to prove that $i$ is monic. So start exactly as you did:
$$
D\overset{d_1}{\underset{d_2}{\rightrightarrows}}E
$$
and suppose
$$
id_1=id_2.
$$

Now define—not really construct, just **name**—
$$
h:=id_1=id_2:D\to A.
$$

Because $i$ equalizes $f$ and $g$,
$$
fh
= f i d_1
= g i d_1
= gh.
$$

So $h:D\to A$ is one of the arrows to which the universal property of the equalizer applies.

The universal property says:

> There is a **unique** $k:D\to E$ such that $ik=h$.

But both $d_1$ and $d_2$ have that property:
$$
id_1=h,\qquad id_2=h.
$$

Therefore, by uniqueness,
$$
\boxed{d_1=d_2}.
$$

And that's precisely the definition that $i$ is monic.

### On what you've written on the board

Your equation at the bottom,
$$
f i d_1=f i d_2=g i d_2,
$$
is fine, but it doesn't quite finish the argument. It establishes that the relevant composite equalizes $f$ and $g$. The decisive next move is: **invoke uniqueness of the factorization through $E$**.

Your instinct in blue that you "probably don't need this construction" is also right. You do **not** need to introduce another object $C$ or another equalizer. The $D$ from the definition of monic can simply play the role of the generic $C$ in the equalizer universal property:

$$
\text{in the UP, take } C=D,\qquad h=id_1=id_2.
$$

So the proof diagram can be pared down to:

$$
\require{AMScd}
\begin{CD}
D @>{d_1,d_2}>> E @>{i}>> A @>{f,g}>> B
\end{CD}
$$

with $id_1=id_2=h$.

### Your comment about $E$ being a subset

This is an important distinction.

In **Set**, the familiar equalizer can indeed be constructed as
$$
E=\{a\in A\mid f(a)=g(a)\},
$$
with $i:E\hookrightarrow A$ the inclusion.

But categorically, that is **not the definition of an equalizer**. The universal property is the definition. The subset description is what the universal property looks like when you're in **Set**.

So your blue comment—

> "$E$ as a subset is more a consequence ... and not the thing that defines it?"

—is basically right. More precisely: in Set, the universal property determines the equalizer up to unique isomorphism, and the literal subset above is a canonical concrete realization of it.

Equalizers also exist well outside Set. Many categories have them; a category need not have every equalizer, but whenever
$$
E\to A
$$
**is** an equalizer, the argument above shows its arrow is monic. In particular, a topos has finite limits, hence equalizers.

### And the "every" / uniqueness-up-to-isomorphism question

You don't need uniqueness of equalizers up to isomorphism for this proof.

"Every equalizer is monic" means:

> Take **any** pair $f,g:A\rightrightarrows B$, and take **any** $i:E\to A$ satisfying the equalizer universal property. Then $i$ is monic.

So just fix an arbitrary equalizer $i$ and prove it. Since nothing special about $i$ was assumed beyond "it is an equalizer," the result applies to every one.

The conceptual punchline is:

$$
\boxed{\text{equalizer uniqueness of factorization }\Longrightarrow\text{ left-cancellation for }i}
$$

The two notions are almost visibly the same once you choose $h=id_1=id_2$.

