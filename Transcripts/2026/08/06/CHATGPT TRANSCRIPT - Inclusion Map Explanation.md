# Inclusion Map Explanation

- URL: https://chatgpt.com/c/6a7472ae-61cc-83ea-a21a-0c8f17ef3712
- Created: 2026-08-06T11:41:38.616Z

---

> [image: sediment://file_00000000cc5c81fba30e0db4ecf5ed26]
> I don’t understand the jump from i(k(c)) = h(c) to k(c) = h(c) and why I is called inclusion

<details><summary>💭 Thinking</summary>

**Explaining inclusion**

I’m interpreting \(i:E\to A\) as the inclusion map: it sends each element of \(E\) to that identical element viewed inside \(A\). Thus \(i(k(c))=h(c)\) means \(k(c)=h(c)\), with both regarded as elements of \(A\).

**Explained inclusion**

</details>

Here \(E\) is literally a subset of \(A\):

\[
E=\{x\in A:f(x)=g(x)\}.
\]

The map

\[
i:E\hookrightarrow A
\]

is called the **inclusion map** because it simply regards an element of \(E\) as an element of the larger set \(A\):

\[
i(x)=x.
\]

It does not alter the element; it only changes which set we are viewing it as belonging to.

Now suppose

\[
i\circ k=h.
\]

Evaluating at \(c\in C\),

\[
i(k(c))=h(c).
\]

But \(i\) is inclusion, so

\[
i(k(c))=k(c)
\]

when \(k(c)\) is viewed as an element of \(A\). Therefore

\[
k(c)=h(c).
\]

There is a slight type distinction:

- \(k(c)\) is being regarded as an element of \(E\);
- \(h(c)\) is initially regarded as an element of \(A\).

But because \(E\subseteq A\), they can be the same underlying element.

The remaining condition

\[
f\circ h=g\circ h
\]

ensures that \(h(c)\) actually lies in \(E\), since

\[
f(h(c))=g(h(c)).
\]

Thus the only possible definition is

\[
k(c)=h(c),
\]

with \(h(c)\) now regarded as an element of \(E\). This explains both existence and uniqueness of \(k\).

For example, if \(A=\mathbb Z\) and \(E\) is the set of even integers, then \(i:E\hookrightarrow\mathbb Z\) sends \(4\mapsto4\). The number is unchanged; it is merely viewed as belonging to the larger set.


---

> So I just projects E into A, up to isomorphism? Or literally it’s only definition is i(a) = a?

In **Set**, it is literally the inclusion function

\[
i:E\to A,\qquad i(e)=e.
\]

It does not project or transform anything. It simply regards the same element \(e\), originally considered as an element of \(E\), as an element of \(A\).

For example, if

\[
E=\{2,4,6\}\subseteq A=\{1,2,3,4,5,6\},
\]

then

\[
i(2)=2,\quad i(4)=4,\quad i(6)=6.
\]

Calling it a **projection** would be misleading. A projection usually discards information, as in

\[
\pi_1:A\times B\to A,\qquad \pi_1(a,b)=a.
\]

An inclusion instead embeds a smaller set into a larger one.

The “up to isomorphism” point applies at a different level: the particular equalizer object is not uniquely determined as a literal set, but it is unique **up to a unique isomorphism**. For instance, you could use a renamed copy

\[
E'=\{x_2,x_4,x_6\}
\]

with a map \(j:E'\to A\) given by \(j(x_2)=2\), etc. Then \(j\) is not literally an inclusion, but \((E',j)\) is isomorphic to the standard equalizer \((E,i)\).

So:

- For the construction in the book: \(i(e)=e\), literally.
- For equalizers abstractly: any other equalizer is uniquely isomorphic to this one.


---

> Category theory

<details><summary>💭 Thinking</summary>

**Clarifying equalizers abstractly**

In category theory, an equalizer is an arrow \(i:E\to A\), not necessarily a literal subset inclusion. In **Set**, it can be chosen as the subset where \(f=g\), making \(i\) inclusion. Generally, \(i\) is monic, and equalizers are unique only up to a unique isomorphism.

**Explained equalizers abstractly**

</details>

In **abstract category theory**, \(i\) is **not necessarily a literal inclusion** and the notation \(i(a)=a\) may not even make sense, since objects need not have elements.

An equalizer of

\[
f,g:A\to B
\]

is an arrow

\[
i:E\to A
\]

such that

\[
f\circ i=g\circ i,
\]

with the universal property that every \(h:C\to A\) satisfying \(f\circ h=g\circ h\) factors uniquely as

\[
h=i\circ k
\]

for some \(k:C\to E\).

The arrow \(i\) is a **monomorphism**, the categorical analogue of an injective map. It should not be called a projection.

### In \(\mathbf{Set}\)

We can choose

\[
E=\{a\in A:f(a)=g(a)\}
\]

and then \(i\) is literally

\[
i(e)=e.
\]

That is why the book concludes

\[
i(k(c))=h(c)\quad\Longrightarrow\quad k(c)=h(c).
\]

This step relies specifically on the chosen inclusion map in \(\mathbf{Set}\).

### In a general category

There is no corresponding elementwise step. Instead, uniqueness is expressed through arrows:

\[
i\circ k_1=i\circ k_2
\quad\Longrightarrow\quad
k_1=k_2,
\]

because every equalizer arrow \(i\) is monic.

Equalizers are unique **up to unique isomorphism**: if

\[
i:E\to A
\qquad\text{and}\qquad
i':E'\to A
\]

are both equalizers, there is a unique isomorphism

\[
u:E\overset{\sim}{\longrightarrow}E'
\]

such that

\[
i'\circ u=i.
\]

So the distinction is:

- \(i(e)=e\): true for the standard equalizer construction in \(\mathbf{Set}\).
- “Unique up to isomorphism”: true for equalizers in any category.
- “Projection”: not the appropriate term; \(i\) is an equalizer arrow and therefore a monomorphism.

