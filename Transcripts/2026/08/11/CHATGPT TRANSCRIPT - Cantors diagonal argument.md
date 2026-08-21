# Cantors diagonal argument

- URL: https://chatgpt.com/c/6a7b16af-af70-83ea-8af0-4b4af078241b
- Created: 2026-08-11T12:34:00.486Z

---

> cantor's diagonal argument

**Cantor’s diagonal argument** proves that some infinite sets are strictly larger than others. The classic result is that the real numbers are **uncountable**: you cannot list all of them as $r_1,r_2,r_3,\ldots$.

Suppose, for contradiction, that every real number in $(0,1)$ can be listed:

$$
\begin{aligned}
r_1 &= 0.\mathbf{1}23456\ldots\\
r_2 &= 0.5\mathbf{7}8910\ldots\\
r_3 &= 0.42\mathbf{6}135\ldots\\
r_4 &= 0.381\mathbf{9}24\ldots\\
&\vdots
\end{aligned}
$$

Look at the **diagonal digits**: the 1st digit of $r_1$, the 2nd digit of $r_2$, the 3rd digit of $r_3$, and so on.

Now construct a new number

$$
x=0.x_1x_2x_3\ldots
$$

by choosing $x_n$ to be different from the $n$-th digit of $r_n$. For example, choose

$$
x_n=
\begin{cases}
1 & \text{if the diagonal digit isn't }1,\\
2 & \text{if the diagonal digit is }1.
\end{cases}
$$

Then $x$ cannot equal **any** number on the list:

- $x\neq r_1$, because their first digits differ.
- $x\neq r_2$, because their second digits differ.
- $x\neq r_3$, because their third digits differ.
- In general, $x\neq r_n$, because their $n$-th digits differ.

So we have constructed a real number that **isn't on the supposedly complete list**. Contradiction.

Therefore,

$$
\boxed{\mathbb R\text{ is uncountable}}
$$

The deeper version is **Cantor's theorem**: for every set $A$,

$$
\boxed{|A|<|\mathcal P(A)|}
$$

where $\mathcal P(A)$ is the set of all subsets of $A$. The diagonal construction is essentially the same idea: given any proposed listing, construct something that differs from entry $n$ at position $n$.

The striking point is that both $\mathbb N$ and $\mathbb R$ are infinite, but

$$
|\mathbb N|<|\mathbb R|.
$$

So **not all infinities have the same size**.


---

> how is that related to ssquares on a plane and diagonal lines?

There are **two different “diagonal” ideas** that are easy to mix up.

### 1. Diagonals through a grid: counting pairs

Imagine points arranged in an infinite square grid:

$$
\begin{array}{cccc}
(1,1)&(1,2)&(1,3)&\cdots\\
(2,1)&(2,2)&(2,3)&\cdots\\
(3,1)&(3,2)&(3,3)&\cdots\\
\vdots&\vdots&\vdots
\end{array}
$$

You can sweep through this grid along diagonal lines:

$$
(1,1)
$$

then

$$
(1,2),(2,1)
$$

then

$$
(1,3),(2,2),(3,1)
$$

and so on.

That shows that all pairs of natural numbers can be put into a list:

$$
\mathbb N\times\mathbb N
$$

is still **countable**.

So even though the grid looks two-dimensional and has infinitely many rows and columns, you can trace diagonals through it and eventually visit every square.

---

### 2. Cantor's diagonal argument: proving a list is impossible

Cantor's argument does almost the **opposite**.

Suppose you try to make an infinite grid where each row is a real number:

$$
\begin{array}{c|ccccc}
 &1&2&3&4&\cdots\\
r_1&\boxed{3}&1&4&1&\cdots\\
r_2&5&\boxed{9}&2&6&\cdots\\
r_3&5&3&\boxed{5}&8&\cdots\\
r_4&9&7&9&\boxed{3}&\cdots\\
\vdots&&&&\ddots
\end{array}
$$

The boxes form a geometric-looking diagonal:

$$
(1,1),(2,2),(3,3),(4,4),\ldots
$$

Cantor takes those diagonal entries and **changes each one**.

If the diagonal gives

$$
3,9,5,3,\ldots
$$

you might construct

$$
4,1,6,4,\ldots
$$

The resulting real number differs from:

- row 1 in square $(1,1)$,
- row 2 in square $(2,2)$,
- row 3 in square $(3,3)$,
- row $n$ in square $(n,n)$.

So it cannot be anywhere in the list.

That's why it's called the **diagonal argument**: you're literally following the diagonal of an infinite table.

### The interesting contrast

The diagonal-grid method says:

$$
\boxed{\mathbb N\times\mathbb N\text{ can be listed}}
$$

Cantor's diagonal argument says:

$$
\boxed{\mathbb R\text{ cannot be listed}}
$$

So diagonals are used in two almost opposite ways: **one diagonal pattern helps construct a complete list; the other helps construct something missing from every possible list.**

If by “squares on a plane” you mean the **unit square with a diagonal line from $(0,0)$ to $(1,1)$**, there is another very interesting connection to Cantor's argument too.

