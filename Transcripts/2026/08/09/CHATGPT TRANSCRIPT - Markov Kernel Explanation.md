# Markov Kernel Explanation

- URL: https://chatgpt.com/c/6a786aea-402c-83ea-a20c-0d6f6cd73f54
- Created: 2026-08-09T11:56:36.426Z

---

> whats markov kernel, what me through, use code snippets

A **Markov kernel** is a function that takes an input and returns a **probability distribution over outputs**.

The ordinary-function picture is

\[
f : X \to Y.
\]

Given \(x\), you get one definite \(y=f(x)\).

A Markov kernel replaces the definite output with uncertainty:

\[
K : X \rightsquigarrow Y
\]

where the squiggly arrow means:

> given \(x\in X\), \(K\) produces a probability distribution on \(Y\).

More formally,

\[
K(x, A) \in [0,1]
\]

is the probability that the output lies in the measurable subset \(A\subseteq Y\), given input \(x\).

So you can read

\[
K(x,A)
\]

as

\[
\Pr(Y\in A\mid X=x).
\]

---

## 1. Start with an ordinary function

Suppose we have:

```python
def classify_temperature(temp: float) -> str:
    if temp < 10:
        return "cold"
    elif temp < 25:
        return "mild"
    else:
        return "hot"
```

This is deterministic:

\[
f:\mathbb R\to
\{\text{cold},\text{mild},\text{hot}\}.
\]

Calling

```python
classify_temperature(20)
```

always produces:

```text
"mild"
```

A Markov kernel could instead say:

```python
def classify_temperature_kernel(temp: float) -> dict[str, float]:
    if temp < 10:
        return {
            "cold": 0.90,
            "mild": 0.09,
            "hot": 0.01,
        }
    elif temp < 25:
        return {
            "cold": 0.10,
            "mild": 0.80,
            "hot": 0.10,
        }
    else:
        return {
            "cold": 0.01,
            "mild": 0.09,
            "hot": 0.90,
        }
```

Now

```python
classify_temperature_kernel(20)
```

returns

```python
{
    "cold": 0.10,
    "mild": 0.80,
    "hot": 0.10,
}
```

Mathematically:

\[
K(20,\{\text{mild}\})=0.8.
\]

And

\[
K(20,\{\text{cold},\text{mild}\})=0.9.
\]

The second argument \(A\) is why the formal definition says

\[
K:X\times\Sigma_Y\to[0,1].
\]

For each fixed \(x\), \(K(x,-)\) has to be a probability measure.

---

# 2. Finite spaces make the idea especially clear

Suppose

\[
X=\{a,b\}
\]

and

\[
Y=\{1,2,3\}.
\]

A kernel can be represented as a stochastic matrix:

\[
K =
\begin{pmatrix}
0.1 & 0.6 & 0.3\\
0.7 & 0.2 & 0.1
\end{pmatrix}.
\]

Rows correspond to inputs.

So:

\[
K(a,-)=(0.1,0.6,0.3)
\]

and

\[
K(b,-)=(0.7,0.2,0.1).
\]

In Python:

```python
K = {
    "a": {1: 0.1, 2: 0.6, 3: 0.3},
    "b": {1: 0.7, 2: 0.2, 3: 0.1},
}
```

Then:

```python
K["a"][2]
```

means

\[
\Pr(Y=2\mid X=a)=0.6.
\]

---

# 3. Why not just call it a conditional probability?

You often can.

A conditional distribution

\[
P(Y\mid X=x)
\]

is essentially a Markov kernel

\[
K:X\rightsquigarrow Y.
\]

But **kernel** emphasizes that we are treating the entire conditional distribution as a composable mathematical object.

Instead of thinking:

> here's a joint probability distribution and I derived some conditional probabilities,

you can think:

> here's a stochastic computation from \(X\) to \(Y\).

That becomes powerful because kernels **compose**.

---

# 4. Composition is the important part

Suppose we have

\[
X\rightsquigarrow Y
\]

and then

\[
Y\rightsquigarrow Z.
\]

For example:

\[
\text{query}
\rightsquigarrow
\text{retrieved document}
\rightsquigarrow
\text{answer}.
\]

Let

\[
K:X\rightsquigarrow Y
\]

and

\[
L:Y\rightsquigarrow Z.
\]

Then their composition is another kernel:

\[
L\circ K:X\rightsquigarrow Z.
\]

The formula is

\[
(L\circ K)(x,C)
=
\int_Y L(y,C)\,K(x,dy).
\]

The integral looks intimidating, but its meaning is simple:

> average the second-stage probability over all possible intermediate outcomes produced by the first stage.

For a finite space, the integral becomes a sum:

\[
(L\circ K)(x,z)
=
\sum_y K(x,y)L(y,z).
\]

That's just matrix multiplication.

---

## Python example

First kernel:

```python
retrieval = {
    "query-a": {
        "doc-1": 0.7,
        "doc-2": 0.3,
    }
}
```

Second kernel:

```python
answer = {
    "doc-1": {
        "correct": 0.9,
        "incorrect": 0.1,
    },
    "doc-2": {
        "correct": 0.4,
        "incorrect": 0.6,
    },
}
```

What's the probability of a correct answer?

We marginalize over the document:

```python
p_correct = (
    retrieval["query-a"]["doc-1"] * answer["doc-1"]["correct"]
    +
    retrieval["query-a"]["doc-2"] * answer["doc-2"]["correct"]
)

print(p_correct)
```

Result:

```text
0.75
```

because

\[
0.7(0.9)+0.3(0.4)
=
0.63+0.12
=
0.75.
\]

Diagrammatically:

\[
\text{query-a}
\rightsquigarrow
\begin{cases}
\text{doc-1} & 0.7\\
\text{doc-2} & 0.3
\end{cases}
\rightsquigarrow
\text{answer}.
\]

Composition removes the intermediate variable:

\[
\text{query-a}
\rightsquigarrow
\begin{cases}
\text{correct} & 0.75\\
\text{incorrect} & 0.25
\end{cases}.
\]

This is the central operation.

---

# 5. A tiny reusable implementation

We can represent finite distributions as dictionaries.

```python
from collections import defaultdict
from typing import Callable, TypeVar

X = TypeVar("X")
Y = TypeVar("Y")
Z = TypeVar("Z")

Distribution = dict[Y, float]
Kernel = Callable[[X], Distribution[Y]]
```

A kernel is then literally:

```python
X -> Distribution[Y]
```

For example:

```python
def retrieval(query: str) -> dict[str, float]:
    if query == "cats":
        return {
            "cat-doc": 0.8,
            "dog-doc": 0.2,
        }

    return {
        "cat-doc": 0.2,
        "dog-doc": 0.8,
    }
```

Another kernel:

```python
def generation(doc: str) -> dict[str, float]:
    if doc == "cat-doc":
        return {
            "good-answer": 0.95,
            "bad-answer": 0.05,
        }

    return {
        "good-answer": 0.30,
        "bad-answer": 0.70,
    }
```

Now define kernel composition:

```python
def compose(
    k: Callable[[X], dict[Y, float]],
    l: Callable[[Y], dict[Z, float]],
) -> Callable[[X], dict[Z, float]]:

    def composed(x: X) -> dict[Z, float]:
        result = defaultdict(float)

        for y, p_y in k(x).items():
            for z, p_z_given_y in l(y).items():
                result[z] += p_y * p_z_given_y

        return dict(result)

    return composed
```

Then:

```python
rag = compose(retrieval, generation)

print(rag("cats"))
```

gives approximately:

```python
{
    "good-answer": 0.82,
    "bad-answer": 0.18,
}
```

because

\[
P(\text{good})
=
0.8(0.95)+0.2(0.30)
=
0.82.
\]

We've created

```text
Query
  ~> Document
  ~> Answer
```

and composed it into

```text
Query
  ~> Answer
```

---

# 6. This is why the squiggly arrow is useful

Earlier I wrote:

\[
X\rightsquigarrow Y.
\]

It's not some fundamentally special mathematical arrow with one universal definition. I'm using it as notation to distinguish a **stochastic map** from an ordinary deterministic function.

Compare:

\[
X\xrightarrow{f}Y
\]

meaning

```text
x -> exactly one y
```

versus

\[
X\rightsquigarrow^K Y
\]

meaning

```text
x -> probability distribution over y
```

You could equally write

\[
K:X\to\mathcal P(Y)
\]

where \(\mathcal P(Y)\) means probability distributions on \(Y\).

More precisely, in measure theory one often uses something like

\[
K:X\to\mathsf{Prob}(Y).
\]

---

# 7. Deterministic functions are special Markov kernels

This is an important observation.

Suppose:

\[
f:X\to Y.
\]

We can turn it into a Markov kernel:

\[
K_f(x,-)=\delta_{f(x)}.
\]

Here

\[
\delta_y
\]

is the **Dirac distribution** concentrated entirely at \(y\).

In code:

```python
def deterministic(f):
    def kernel(x):
        return {f(x): 1.0}

    return kernel
```

For example:

```python
def uppercase(s: str) -> str:
    return s.upper()

uppercase_kernel = deterministic(uppercase)

print(uppercase_kernel("hello"))
```

produces:

```python
{
    "HELLO": 1.0
}
```

So ordinary deterministic computation sits **inside** stochastic computation.

That's mathematically very useful.

You don't need two completely separate composition systems:

```text
deterministic stages
probabilistic stages
```

They can all be represented as kernels.

---

# 8. A sampling implementation

A probability distribution can also be interpreted operationally: sample from it.

```python
import random

def sample(dist):
    outcomes = list(dist)
    probabilities = list(dist.values())

    return random.choices(
        outcomes,
        weights=probabilities,
        k=1,
    )[0]
```

Now:

```python
doc = sample(retrieval("cats"))
answer = sample(generation(doc))

print(doc, answer)
```

One run might produce:

```text
cat-doc good-answer
```

Another:

```text
dog-doc bad-answer
```

This gives us two different views of the same kernel.

### Denotational view

```python
retrieval("cats")
```

means the mathematical distribution:

\[
\{
\text{cat-doc}:0.8,
\text{dog-doc}:0.2
\}.
\]

### Operational view

Actually execute it:

```python
sample(retrieval("cats"))
```

and obtain one realization.

That distinction is directly relevant to the denotational/operational semantics you've been considering for RAG.

---

# 9. Continuous Markov kernels

The output doesn't have to be finite.

Suppose:

\[
X=\mathbb R,\qquad
Y=\mathbb R.
\]

Define

\[
K(x,-)
=
\mathcal N(x,1).
\]

That means:

> given \(x\), output a normally distributed number centered at \(x\).

Operationally:

```python
import random

def kernel(x: float) -> float:
    return random.gauss(
        mu=x,
        sigma=1.0,
    )
```

But strictly speaking, this function only gives us a **sampler**.

The mathematical kernel is:

\[
K(x,A)
=
\int_A
\frac{1}{\sqrt{2\pi}}
e^{-(y-x)^2/2}
\,dy.
\]

For every fixed \(x\),

\[
K(x,-)
\]

is a probability measure over \(Y\).

---

# 10. Why the measure-theoretic definition has two arguments

You might wonder why we don't simply define:

\[
K(x,y)=P(y\mid x).
\]

For discrete \(Y\), that's fine.

But for continuous variables:

\[
P(Y=y)=0.
\]

So the fundamental object can't really be the probability of an individual point.

Instead:

\[
K(x,A)
\]

means

> probability that the output lies somewhere in region \(A\).

For example,

\[
K(5,[4,6])
\]

could mean:

> given input 5, what's the probability the noisy output lies between 4 and 6?

That's why the proper definition is over measurable sets.

---

# 11. Markov chains are repeated Markov kernels

A Markov chain is essentially repeated application of a kernel

\[
K:X\rightsquigarrow X.
\]

For example:

```python
weather = {
    "sunny": {
        "sunny": 0.8,
        "rainy": 0.2,
    },
    "rainy": {
        "sunny": 0.4,
        "rainy": 0.6,
    },
}
```

This is a kernel

\[
K:
\text{Weather}
\rightsquigarrow
\text{Weather}.
\]

One application gives tomorrow's distribution.

Two compositions:

\[
K\circ K
\]

give the distribution two days later.

Three:

\[
K\circ K\circ K
\]

give three days later.

So a **Markov chain is not what a Markov kernel is**.

Rather:

> a Markov kernel is the transition mechanism from which a Markov chain can be built.

---

# 12. Now the category-theoretic interpretation

This is where things become particularly relevant to your RAG architecture.

Ordinary functions form a category:

\[
X\xrightarrow fY\xrightarrow gZ
\]

with composition

\[
g\circ f.
\]

Probability distributions give rise to something like the **Giry monad**:

\[
\mathcal G(X)
=
\text{probability measures on }X.
\]

Then a Markov kernel can be represented as:

\[
K:X\to\mathcal G(Y).
\]

Another kernel:

\[
L:Y\to\mathcal G(Z).
\]

Notice ordinary function composition doesn't work:

\[
X\to\mathcal G(Y)
\]

followed by

\[
Y\to\mathcal G(Z).
\]

The types don't match:

```text
G(Y) != Y
```

Instead we use **Kleisli composition**.

Conceptually:

```python
X
 -> Distribution[Y]
 -> Distribution[Distribution[Z]]
 -> Distribution[Z]
```

That final flattening operation integrates over the intermediate distribution.

The code we wrote earlier:

```python
for y, p_y in k(x).items():
    for z, p_z_given_y in l(y).items():
        result[z] += p_y * p_z_given_y
```

is literally a finite implementation of Kleisli composition.

---

# 13. `bind` makes this even clearer

For distributions, define:

```python
def bind(dist, kernel):
    result = defaultdict(float)

    for x, p_x in dist.items():
        for y, p_y_given_x in kernel(x).items():
            result[y] += p_x * p_y_given_x

    return dict(result)
```

Now:

```python
docs = retrieval("cats")

answers = bind(
    docs,
    generation,
)

print(answers)
```

The structure is:

```text
Distribution[X]
    +
X -> Distribution[Y]
    ↓
Distribution[Y]
```

This is monadic `bind`:

\[
\mathcal G(X)
\times
(X\to\mathcal G(Y))
\to
\mathcal G(Y).
\]

Kernel composition can then be defined through `bind`:

```python
def compose(k, l):
    return lambda x: bind(k(x), l)
```

That's essentially the whole algebra.

---

# 14. Think of it as probabilistic `flatMap`

If you're familiar with things like Scala:

```scala
Option[A].flatMap(A => Option[B])
```

or promises:

```text
Promise[A].flatMap(A -> Promise[B])
```

then probability kernels have the same shape:

```text
Distribution[A].flatMap(
    A -> Distribution[B]
)
```

The special thing about distributions is how flattening works.

Suppose:

```text
70%:
    A -> { X: 90%, Y: 10% }

30%:
    B -> { X: 20%, Y: 80% }
```

Flattening produces:

\[
P(X)=.7(.9)+.3(.2)=.69
\]

and

\[
P(Y)=.7(.1)+.3(.8)=.31.
\]

---

# 15. Why this is a useful semantic backbone for RAG

Suppose your system has:

\[
Q\rightsquigarrow R
\rightsquigarrow C
\rightsquigarrow A
\rightsquigarrow S
\]

where

- \(Q\): query
- \(R\): retrieval candidates
- \(C\): selected context
- \(A\): generated answer
- \(S\): evaluation score/outcome

You might model:

\[
K_{\mathrm{retrieve}}
:
Q\rightsquigarrow R
\]

\[
K_{\mathrm{select}}
:
R\rightsquigarrow C
\]

\[
K_{\mathrm{generate}}
:
C\rightsquigarrow A
\]

\[
K_{\mathrm{evaluate}}
:
A\rightsquigarrow S.
\]

Then the complete system is

\[
K_{\mathrm{system}}
=
K_{\mathrm{evaluate}}
\odot
K_{\mathrm{generate}}
\odot
K_{\mathrm{select}}
\odot
K_{\mathrm{retrieve}}.
\]

I used \(\odot\) here to emphasize **kernel/Kleisli composition**, rather than ordinary function composition.

This allows the denotational semantics of the pipeline to be:

\[
\llbracket P\rrbracket
:
Q\rightsquigarrow S.
\]

No matter how many internal stages exist.

---

## And optimization parameters can be inputs too

Suppose retrieval has configuration

\[
\theta\in\Theta.
\]

Then:

\[
K_{\mathrm{retrieve}}
:
\Theta\times Q
\rightsquigarrow
R.
\]

Generation similarly:

\[
K_{\mathrm{gen}}
:
\Phi\times C
\rightsquigarrow
A.
\]

An entire RAG configuration

\[
c=(\theta,\phi,\ldots)
\]

induces a kernel

\[
K_c:
Q\rightsquigarrow S.
\]

Optimization can then be interpreted as searching over \(c\) for a desirable property of the resulting kernel:

\[
c^*
=
\arg\max_c
\mathbb E_{s\sim K_c(q)}
[U(s)].
\]

Now "configuration" has a mathematically clean meaning:

> it selects a stochastic program/kernel.

That's a much stronger abstraction than "configuration is a dictionary of hyperparameters."

---

# 16. The really compact mental model

I'd remember these four correspondences:

| deterministic world | stochastic world |
|---|---|
| \(f:X\to Y\) | \(K:X\rightsquigarrow Y\) |
| `Y f(X)` | `Distribution[Y] k(X)` |
| ordinary composition | integrate/marginalize |
| category of functions | category of Markov kernels |

And the key equation is simply:

\[
\boxed{
(L\odot K)(x,dz)
=
\int_Y
L(y,dz)\,K(x,dy)
}
\]

Read it as:

> Run \(K\), consider every intermediate \(y\), run \(L\) from that \(y\), and average according to how probable each \(y\) was.

For a finite implementation, that scary-looking integral is just:

```python
for y, p_y in K(x).items():
    for z, p_z_given_y in L(y).items():
        result[z] += p_y * p_z_given_y
```

That's a Markov kernel in a nutshell—and it's one of the reasons it makes such a good candidate for the semantic core of the compositional RAG/optimization machinery you're working toward. memcite


---

> Category theory

I’ll start with categories and composition, then derive Markov kernels via probability and Kleisli composition, before connecting the categorical structure back to RAG.

<details><summary>💭 Thinking</summary>

**Explaining category theory**

I’m interpreting the request as a category-theoretic view of Markov kernels. Objects are measurable spaces, morphisms are probability kernels, composition is integration, and deterministic functions appear as Dirac kernels.

</details>

# Category theory behind Markov kernels

Category theory is primarily the mathematics of **typed composition**.

It asks:

> What kinds of processes can be connected, what does their composition mean, and which equations must composition satisfy?

For Markov kernels, the answer is:

\[
X \rightsquigarrow Y
\]

means a stochastic process from \(X\) to \(Y\), and composition means integrating out the intermediate result.

---

## 1. An ordinary category

A category \(\mathcal C\) consists of:

1. **Objects** \(X,Y,Z,\ldots\)
2. **Morphisms** \(f:X\to Y\)
3. An identity morphism \(\mathrm{id}_X:X\to X\) for every object
4. A composition operation

\[
X\xrightarrow{f}Y\xrightarrow{g}Z
\quad\leadsto\quad
X\xrightarrow{g\circ f}Z.
\]

These must obey two laws.

### Identity

\[
\mathrm{id}_Y\circ f=f=f\circ\mathrm{id}_X.
\]

### Associativity

\[
h\circ(g\circ f)=(h\circ g)\circ f.
\]

Associativity is operationally important. It says that the grouping of a pipeline does not change its meaning:

```text
((f then g) then h)
```

and

```text
(f then (g then h))
```

denote the same computation.

---

## 2. Functions form a category

The standard example is \(\mathbf{Set}\):

- objects are sets;
- morphisms are functions;
- identities are identity functions;
- composition is ordinary function composition.

In Python:

```python
from typing import Callable, TypeVar

A = TypeVar("A")
B = TypeVar("B")
C = TypeVar("C")


def identity(x: A) -> A:
    return x


def then(
    f: Callable[[A], B],
    g: Callable[[B], C],
) -> Callable[[A], C]:
    return lambda x: g(f(x))
```

For example:

```python
def length(text: str) -> int:
    return len(text)


def is_even(n: int) -> bool:
    return n % 2 == 0


length_is_even = then(length, is_even)

assert length_is_even("cats") is True
assert length_is_even("cat") is False
```

The types line up:

\[
\mathrm{String}
\xrightarrow{\mathrm{length}}
\mathrm{Integer}
\xrightarrow{\mathrm{isEven}}
\mathrm{Boolean}.
\]

Category theory focuses on this externally visible structure, not on how either function is internally implemented.

---

# 3. A Markov kernel changes the notion of morphism

An ordinary function has the type

\[
f:X\to Y.
\]

A Markov kernel has the effective type

\[
K:X\to\mathsf{Prob}(Y).
\]

Given \(x\), it returns a probability distribution over possible \(Y\)-values.

We often write this as

\[
K:X\rightsquigarrow Y
\]

to visually distinguish it from a deterministic function.

For finite spaces:

```python
def retrieve(query: str) -> dict[str, float]:
    if query == "cats":
        return {
            "cat-document": 0.8,
            "dog-document": 0.2,
        }

    return {
        "cat-document": 0.3,
        "dog-document": 0.7,
    }
```

Its type is conceptually:

```text
Query -> ProbabilityDistribution[Document]
```

not:

```text
Query -> Document
```

---

# 4. Markov kernels form a category

Consider a category commonly called \(\mathbf{Stoch}\):

- objects are measurable spaces;
- morphisms are Markov kernels;
- identity morphisms are point-mass kernels;
- composition marginalizes over intermediate values.

Suppose

\[
K:X\rightsquigarrow Y
\]

and

\[
L:Y\rightsquigarrow Z.
\]

Their composition is

\[
L\odot K:X\rightsquigarrow Z
\]

defined by

\[
(L\odot K)(x,C)
=
\int_Y L(y,C)\,K(x,dy).
\]

For finite spaces:

\[
(L\odot K)(x,z)
=
\sum_{y\in Y}K(x,y)L(y,z).
\]

This means:

1. Run \(K\) conceptually to obtain every possible \(y\).
2. From every \(y\), run \(L\).
3. Weight the second-stage outcomes by the probability of reaching \(y\).
4. Sum over \(y\).

---

## Finite implementation

Here is a small probability-distribution type.

```python
from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from math import isclose
from typing import Callable, Generic, Hashable, Mapping, TypeVar

A = TypeVar("A", bound=Hashable)
B = TypeVar("B", bound=Hashable)
C = TypeVar("C", bound=Hashable)


@dataclass(frozen=True)
class Dist(Generic[A]):
    mass: Mapping[A, float]

    def __post_init__(self) -> None:
        cleaned = {
            value: float(probability)
            for value, probability in self.mass.items()
            if probability != 0.0
        }

        if any(probability < 0.0 for probability in cleaned.values()):
            raise ValueError("Probabilities cannot be negative")

        total = sum(cleaned.values())

        if not isclose(total, 1.0, abs_tol=1e-12):
            raise ValueError(
                f"Probabilities must sum to 1; received {total}"
            )

        object.__setattr__(self, "mass", cleaned)

    @staticmethod
    def pure(value: A) -> Dist[A]:
        """The point mass, or Dirac distribution, at value."""
        return Dist({value: 1.0})

    def bind(
        self,
        kernel: Callable[[A], Dist[B]],
    ) -> Dist[B]:
        result: defaultdict[B, float] = defaultdict(float)

        for value, outer_probability in self.mass.items():
            inner_distribution = kernel(value)

            for output, inner_probability in inner_distribution.mass.items():
                result[output] += (
                    outer_probability * inner_probability
                )

        return Dist(dict(result))

    def map(
        self,
        function: Callable[[A], B],
    ) -> Dist[B]:
        return self.bind(
            lambda value: Dist.pure(function(value))
        )
```

A kernel is now a function returning `Dist`.

```python
def retrieve(query: str) -> Dist[str]:
    if query == "cats":
        return Dist({
            "cat-document": 0.8,
            "dog-document": 0.2,
        })

    return Dist({
        "cat-document": 0.3,
        "dog-document": 0.7,
    })


def generate(document: str) -> Dist[str]:
    if document == "cat-document":
        return Dist({
            "correct-answer": 0.95,
            "incorrect-answer": 0.05,
        })

    return Dist({
        "correct-answer": 0.30,
        "incorrect-answer": 0.70,
    })
```

Kernel composition is `bind`:

```python
def kernel_then(
    first: Callable[[A], Dist[B]],
    second: Callable[[B], Dist[C]],
) -> Callable[[A], Dist[C]]:
    return lambda value: first(value).bind(second)
```

Compose retrieval and generation:

```python
rag = kernel_then(retrieve, generate)

print(rag("cats").mass)
```

The result is:

```python
{
    "correct-answer": 0.82,
    "incorrect-answer": 0.18,
}
```

because

\[
0.8(0.95)+0.2(0.30)=0.82.
\]

The intermediate document has disappeared from the external type:

\[
\mathrm{Query}
\rightsquigarrow
\mathrm{Document}
\rightsquigarrow
\mathrm{Answer}
\]

becomes

\[
\mathrm{Query}
\rightsquigarrow
\mathrm{Answer}.
\]

That is categorical composition.

---

# 5. What is the identity Markov kernel?

For ordinary functions:

\[
\mathrm{id}_X(x)=x.
\]

For Markov kernels, the identity must return the input with probability \(1\):

\[
\mathrm{id}_X(x)=\delta_x.
\]

Here \(\delta_x\) is the Dirac or point-mass distribution at \(x\).

```python
def kernel_identity(value: A) -> Dist[A]:
    return Dist.pure(value)
```

For example:

```python
kernel_identity("document")
```

returns:

```python
Dist({"document": 1.0})
```

This is why deterministic functions naturally embed into stochastic computation.

Given

\[
f:X\to Y,
\]

define

\[
\widehat f:X\rightsquigarrow Y
\]

by

\[
\widehat f(x)=\delta_{f(x)}.
\]

In code:

```python
def deterministic(
    function: Callable[[A], B],
) -> Callable[[A], Dist[B]]:
    return lambda value: Dist.pure(function(value))
```

Example:

```python
def normalize_query(query: str) -> str:
    return query.strip().lower()


normalize_kernel = deterministic(normalize_query)

print(normalize_kernel("  CATS  ").mass)
```

Result:

```python
{"cats": 1.0}
```

Thus deterministic and stochastic stages can use the same composition operator.

---

# 6. The category laws become probability laws

The identity laws say:

```python
kernel_then(kernel_identity, kernel)
```

and

```python
kernel_then(kernel, kernel_identity)
```

must have the same meaning as `kernel`.

The associativity law says:

```python
kernel_then(
    kernel_then(k, l),
    m,
)
```

must mean the same thing as:

```python
kernel_then(
    k,
    kernel_then(l, m),
)
```

This is not merely syntax. It says that marginalization can be regrouped without changing the final distribution.

For three finite kernels:

\[
\sum_y
\left(
    K(x,y)
    \sum_z L(y,z)M(z,w)
\right)
\]

equals

\[
\sum_z
\left(
    \sum_y K(x,y)L(y,z)
\right)
M(z,w).
\]

Both are equal to

\[
\sum_{y,z}
K(x,y)L(y,z)M(z,w).
\]

In code:

```python
def evaluate(answer: str) -> Dist[str]:
    if answer == "correct-answer":
        return Dist({
            "pass": 0.98,
            "fail": 0.02,
        })

    return Dist({
        "pass": 0.10,
        "fail": 0.90,
    })


left_grouped = kernel_then(
    kernel_then(retrieve, generate),
    evaluate,
)

right_grouped = kernel_then(
    retrieve,
    kernel_then(generate, evaluate),
)

print(left_grouped("cats").mass)
print(right_grouped("cats").mass)
```

Both return the same distribution, up to floating-point precision.

---

# 7. Where the monad appears

A kernel has the type

\[
X\to\mathsf{Prob}(Y).
\]

This is not an ordinary function from \(X\) to \(Y\). Therefore ordinary function composition does not directly work.

Given

\[
K:X\to\mathsf{Prob}(Y)
\]

and

\[
L:Y\to\mathsf{Prob}(Z),
\]

the codomain of \(K\) is \(\mathsf{Prob}(Y)\), but the domain of \(L\) is \(Y\).

The types do not line up:

```text
X -> Prob[Y]
          Y -> Prob[Z]
```

The probability-distribution **monad** supplies the missing composition machinery.

---

## The distribution functor

The first piece is a mapping

\[
\mathsf{Prob}
\]

that sends a space \(X\) to the space of probability distributions over \(X\).

A deterministic function

\[
f:X\to Y
\]

induces a pushforward function

\[
\mathsf{Prob}(f):
\mathsf{Prob}(X)
\to
\mathsf{Prob}(Y).
\]

For finite distributions:

\[
\mathsf{Prob}(f)(p)(y)
=
\sum_{\{x\mid f(x)=y\}}p(x).
\]

This is `Dist.map`:

```python
distribution = Dist({
    1: 0.2,
    2: 0.3,
    3: 0.5,
})

parity = distribution.map(
    lambda n: "even" if n % 2 == 0 else "odd"
)

print(parity.mass)
```

Result:

```python
{
    "odd": 0.7,
    "even": 0.3,
}
```

The probabilities of values mapped to the same output are added.

A functor must preserve identity and composition:

\[
\mathsf{Prob}(\mathrm{id}_X)
=
\mathrm{id}_{\mathsf{Prob}(X)}
\]

and

\[
\mathsf{Prob}(g\circ f)
=
\mathsf{Prob}(g)\circ\mathsf{Prob}(f).
\]

---

## `pure`: putting a value into the probability context

The monad unit is

\[
\eta_X:X\to\mathsf{Prob}(X)
\]

defined by

\[
\eta_X(x)=\delta_x.
\]

That is our `Dist.pure`.

```python
Dist.pure("document")
```

means:

```python
Dist({"document": 1.0})
```

---

## `join`: flattening nested uncertainty

Suppose we have a distribution over distributions:

\[
\mathsf{Prob}(\mathsf{Prob}(X)).
\]

For example:

- with probability \(0.7\), use one distribution;
- with probability \(0.3\), use another distribution.

The monad multiplication

\[
\mu_X:
\mathsf{Prob}(\mathsf{Prob}(X))
\to
\mathsf{Prob}(X)
\]

flattens this into one distribution by weighted averaging.

Conceptually:

```text
70% choose {a: 90%, b: 10%}
30% choose {a: 20%, b: 80%}
```

becomes

\[
P(a)=0.7(0.9)+0.3(0.2)=0.69
\]

and

\[
P(b)=0.7(0.1)+0.3(0.8)=0.31.
\]

`bind` combines `map` and `join`.

---

# 8. The Kleisli category

Given a monad \(\mathsf{Prob}\), we can construct its **Kleisli category**.

The objects remain the same spaces \(X,Y,Z\), but a Kleisli morphism

\[
X\to_{\mathrm{Kl}}Y
\]

is an ordinary function

\[
X\to\mathsf{Prob}(Y).
\]

That is exactly a Markov kernel.

Kleisli composition is

\[
L\star K
=
\mu_Z
\circ
\mathsf{Prob}(L)
\circ
K.
\]

Expanded:

\[
X
\xrightarrow{K}
\mathsf{Prob}(Y)
\xrightarrow{\mathsf{Prob}(L)}
\mathsf{Prob}(\mathsf{Prob}(Z))
\xrightarrow{\mu_Z}
\mathsf{Prob}(Z).
\]

In code:

```python
def kernel_then(k, l):
    return lambda x: k(x).bind(l)
```

So the important correspondence is:

| Probability concept | Category-theoretic concept |
|---|---|
| Distribution | Monad value |
| Point mass \(\delta_x\) | Monad unit |
| Marginalization | Monad multiplication |
| Conditional distribution | Kleisli morphism |
| Kernel composition | Kleisli composition |
| Markov kernels | Morphisms in the Kleisli category |

For finite distributions this is the **finite distribution monad** on sets.

For general measurable spaces, the corresponding construction is usually described using the **Giry monad**.

---

# 9. Monad laws produce category laws

The probability monad obeys three laws.

## Left identity

\[
\eta(x)\mathbin{\mathrm{bind}}K=K(x).
\]

```python
Dist.pure(x).bind(k) == k(x)
```

## Right identity

\[
p\mathbin{\mathrm{bind}}\eta=p.
\]

```python
distribution.bind(Dist.pure) == distribution
```

## Associativity

\[
(p\mathbin{\mathrm{bind}}K)
\mathbin{\mathrm{bind}}L
=
p\mathbin{\mathrm{bind}}
\left(
    x\mapsto K(x)\mathbin{\mathrm{bind}}L
\right).
\]

These are exactly what is needed for identities and associative composition in the Kleisli category.

This is one of the recurring category-theoretic patterns:

> Find a small algebraic structure whose laws guarantee that a larger system composes correctly.

---

# 10. Sequential and parallel composition

Ordinary category composition describes sequential execution:

\[
X\xrightarrow{K}Y\xrightarrow{L}Z.
\]

RAG systems also contain parallel execution:

```text
                dense retrieval
query  --------<
                lexical retrieval
```

Parallel composition is captured by a **monoidal category**.

Given kernels

\[
K:X\rightsquigarrow Y
\]

and

\[
L:U\rightsquigarrow V,
\]

their tensor product is

\[
K\otimes L:
X\times U
\rightsquigarrow
Y\times V.
\]

For finite distributions:

\[
(K\otimes L)((x,u),(y,v))
=
K(x,y)L(u,v).
\]

This product represents independent random choices, conditional on the inputs.

```python
D = TypeVar("D", bound=Hashable)


def tensor(
    left: Callable[[A], Dist[B]],
    right: Callable[[C], Dist[D]],
) -> Callable[[tuple[A, C]], Dist[tuple[B, D]]]:

    def combined(inputs: tuple[A, C]) -> Dist[tuple[B, D]]:
        left_input, right_input = inputs
        left_distribution = left(left_input)
        right_distribution = right(right_input)

        return Dist({
            (left_output, right_output):
                left_probability * right_probability
            for left_output, left_probability
                in left_distribution.mass.items()
            for right_output, right_probability
                in right_distribution.mass.items()
        })

    return combined
```

Example:

```python
def coin(_: None) -> Dist[str]:
    return Dist({
        "heads": 0.5,
        "tails": 0.5,
    })


two_independent_coins = tensor(coin, coin)

print(two_independent_coins((None, None)).mass)
```

Result:

```python
{
    ("heads", "heads"): 0.25,
    ("heads", "tails"): 0.25,
    ("tails", "heads"): 0.25,
    ("tails", "tails"): 0.25,
}
```

The monoidal structure provides:

- sequential composition: \(L\circ K\);
- parallel composition: \(K\otimes L\);
- a unit object \(I\), typically a one-element space;
- wire-swapping and regrouping operations.

---

# 11. Why stochastic categories are not ordinary cartesian categories

This distinction is central.

In an ordinary programming language, it seems harmless to duplicate a value:

```python
lambda x: (x, x)
```

For a stochastic computation, there are two different operations:

1. Run the random computation once, then copy its result.
2. Copy the input, then run the random computation twice.

They are not equivalent.

Let

\[
K:I\rightsquigarrow\{\mathrm H,\mathrm T\}
\]

be a fair coin.

## One sample, copied

\[
I\xrightarrow{K}Y\xrightarrow{\mathrm{copy}}Y\times Y.
\]

Distribution:

\[
P(H,H)=0.5,
\qquad
P(T,T)=0.5.
\]

There are no mixed pairs.

## Two independent samples

\[
I\xrightarrow{\mathrm{copy}}I\times I
\xrightarrow{K\otimes K}Y\times Y.
\]

Distribution:

\[
P(H,H)=P(H,T)=P(T,H)=P(T,T)=0.25.
\]

In code:

```python
copy_output = deterministic(
    lambda output: (output, output)
)

one_coin_copied = kernel_then(
    coin,
    copy_output,
)

copy_input = deterministic(
    lambda value: (value, value)
)

two_coin_runs = kernel_then(
    copy_input,
    tensor(coin, coin),
)

print("One run, copied:")
print(one_coin_copied(None).mass)

print("Two independent runs:")
print(two_coin_runs(None).mass)
```

Result:

```python
One run, copied:
{
    ("heads", "heads"): 0.5,
    ("tails", "tails"): 0.5,
}

Two independent runs:
{
    ("heads", "heads"): 0.25,
    ("heads", "tails"): 0.25,
    ("tails", "heads"): 0.25,
    ("tails", "tails"): 0.25,
}
```

This distinction matters directly for LLM systems:

```text
generate once and reuse the answer
```

is not the same as:

```text
call the model twice with the same prompt
```

Even though the input was duplicated.

---

# 12. Markov categories

A **Markov category** abstracts the categorical structure needed for probability.

Roughly, it is a symmetric monoidal category with specified operations for:

- copying values;
- discarding values;
- composing stochastic processes;
- running processes in parallel.

For every object \(X\), there is a copy map

\[
\mathrm{copy}_X:X\to X\otimes X
\]

and a discard map

\[
\mathrm{discard}_X:X\to I.
\]

The copy map is deterministic:

\[
x\mapsto(x,x).
\]

The discard map forgets the value:

\[
x\mapsto *.
\]

Crucially, an arbitrary stochastic morphism does not preserve copying:

\[
\mathrm{copy}_Y\circ K
\neq
(K\otimes K)\circ\mathrm{copy}_X.
\]

The left side samples once and copies the sample. The right side samples twice.

Deterministic morphisms do preserve copying. This gives a structural way to distinguish deterministic processes from genuinely stochastic ones.

---

## Discarding corresponds to normalization

For a normalized Markov kernel,

\[
K:X\rightsquigarrow Y,
\]

discarding the output always has total probability \(1\):

\[
\mathrm{discard}_Y\circ K
=
\mathrm{discard}_X.
\]

This expresses the fact that

\[
K(x,Y)=1.
\]

If instead probabilities sum to at most \(1\), we have a **sub-Markov kernel**. Missing probability mass can model:

- nontermination;
- filtering;
- cancellation;
- runtime failure;
- an observation that rejected the execution.

That can be useful for production systems, although it should be distinguished from ordinary normalized probabilistic behavior.

---

# 13. String diagrams

Category theory often represents morphisms as boxes and objects as wires.

A sequential RAG pipeline:

```text
 Query       Documents       Context        Answer
   │             │              │              │
   ▼             ▼              ▼              ▼
┌────────┐   ┌────────┐    ┌────────┐    ┌────────┐
│Retrieve│──▶│ Select │───▶│Generate│───▶│Evaluate│
└────────┘   └────────┘    └────────┘    └────────┘
```

The wires are semantic types. The boxes are morphisms.

Composition is connecting wires.

Parallel composition places boxes next to one another:

```text
                  ┌───────────────┐
 Query ──────────▶│ Dense retrieve│────▶ Dense result
                  └───────────────┘

                  ┌─────────────────┐
 Query ──────────▶│ Lexical retrieve│────▶ Lexical result
                  └─────────────────┘
```

The outputs can then be merged by another morphism.

String diagrams are not merely illustrations. Two diagrams represent the same morphism when they can be transformed using the category's equations.

---

# 14. Functors

A **functor** translates between categories while preserving their compositional structure.

Given categories \(\mathcal C\) and \(\mathcal D\), a functor

\[
F:\mathcal C\to\mathcal D
\]

maps:

- each object \(X\) to an object \(F(X)\);
- each morphism \(f:X\to Y\) to a morphism

\[
F(f):F(X)\to F(Y).
\]

It must preserve identities and composition:

\[
F(\mathrm{id}_X)=\mathrm{id}_{F(X)}
\]

and

\[
F(g\circ f)=F(g)\circ F(f).
\]

The probability-distribution construction is a functor:

\[
\mathsf{Prob}:\mathbf{Set}\to\mathbf{Set}
\]

in the finite case.

It sends:

\[
X\mapsto\mathsf{Prob}(X)
\]

and

\[
f:X\to Y
\]

to its pushforward:

\[
\mathsf{Prob}(f):
\mathsf{Prob}(X)\to\mathsf{Prob}(Y).
\]

In code, `Dist.map` is the action of this functor on morphisms.

---

# 15. Natural transformations

A natural transformation is a uniform transformation between functors.

If

\[
F,G:\mathcal C\to\mathcal D,
\]

then a natural transformation

\[
\alpha:F\Rightarrow G
\]

gives, for every object \(X\), a morphism

\[
\alpha_X:F(X)\to G(X)
\]

that behaves consistently with every morphism in the category.

For the probability monad, the point-mass operation is a natural transformation:

\[
\eta:\mathrm{Id}\Rightarrow\mathsf{Prob}.
\]

Each component is

\[
\eta_X:X\to\mathsf{Prob}(X),
\qquad
x\mapsto\delta_x.
\]

The flattening operation is another natural transformation:

\[
\mu:
\mathsf{Prob}\circ\mathsf{Prob}
\Rightarrow
\mathsf{Prob}.
\]

A monad is therefore not merely a container API. Categorically it consists of:

\[
(\mathsf{Prob},\eta,\mu)
\]

satisfying compatibility laws.

---

# 16. Markov kernels as RAG semantics

A RAG system can be described by semantic objects:

\[
Q=\text{queries}
\]

\[
D=\text{retrieved document collections}
\]

\[
C=\text{constructed contexts}
\]

\[
A=\text{answers}
\]

\[
S=\text{evaluation outcomes}.
\]

Stages become kernels:

\[
R:Q\rightsquigarrow D
\]

\[
M:D\rightsquigarrow C
\]

\[
G:C\rightsquigarrow A
\]

\[
E:A\rightsquigarrow S.
\]

Their composition is

\[
E\odot G\odot M\odot R:
Q\rightsquigarrow S.
\]

The internal objects \(D,C,A\) are hidden after composition. The complete system has a well-defined denotation:

\[
\llbracket\mathrm{pipeline}\rrbracket:
Q\rightsquigarrow S.
\]

A deterministic query normalizer can participate as a Dirac kernel:

\[
N:Q\to Q'
\quad\leadsto\quad
\widehat N:Q\rightsquigarrow Q'.
\]

Thus one semantic category can contain:

- deterministic transformations;
- randomized retrieval;
- approximate search;
- sampling-based generation;
- noisy evaluation;
- deterministic validation.

---

# 17. Configuration as an input object

Suppose retrieval depends on configuration parameters

\[
\theta\in\Theta.
\]

Instead of treating configuration as unstructured metadata, model the retriever as

\[
R:\Theta\otimes Q\rightsquigarrow D.
\]

A fixed configuration \(\theta\) is a deterministic state

\[
\delta_\theta:I\to\Theta.
\]

Plugging that configuration into the retriever gives:

\[
Q
\cong
I\otimes Q
\xrightarrow{\delta_\theta\otimes\mathrm{id}_Q}
\Theta\otimes Q
\xrightarrow{R}
D.
\]

The result is a configured kernel

\[
R_\theta:Q\rightsquigarrow D.
\]

This gives a precise meaning to configuration:

> A configuration is a state that partially evaluates a parameterized process.

For example:

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class RetrievalConfig:
    top_k: int
    dense_weight: float


def parameterized_retrieval(
    value: tuple[RetrievalConfig, str],
) -> Dist[str]:
    config, query = value

    # Illustrative probabilities only.
    if config.dense_weight >= 0.5:
        return Dist({
            "semantic-document": 0.8,
            "lexical-document": 0.2,
        })

    return Dist({
        "semantic-document": 0.3,
        "lexical-document": 0.7,
    })


def configure_retrieval(
    config: RetrievalConfig,
) -> Callable[[str], Dist[str]]:
    return lambda query: parameterized_retrieval(
        (config, query)
    )
```

Then:

```python
retriever = configure_retrieval(
    RetrievalConfig(
        top_k=10,
        dense_weight=0.7,
    )
)
```

denotes a particular morphism

\[
R_\theta:Q\rightsquigarrow D.
\]

Optimization searches over the family \(\{R_\theta\}_{\theta\in\Theta}\).

---

# 18. Category theory does not itself perform optimization

Category theory supplies the compositional language. It does not by itself choose the best parameter.

Given a configured pipeline

\[
K_\theta:Q\rightsquigarrow S
\]

and a utility function

\[
u:S\to\mathbb R,
\]

an objective could be

\[
J(\theta)
=
\mathbb E_{q\sim\mu}
\mathbb E_{s\sim K_\theta(q)}
[u(s)].
\]

Optimization then seeks

\[
\theta^*\in\arg\max_\theta J(\theta).
\]

The categorical contribution is that:

- \(K_\theta\) has precise semantics;
- stages compose uniformly;
- deterministic stages embed correctly;
- pipeline regrouping is meaning-preserving;
- parallel and sequential execution are distinguished;
- repeated sampling is distinguished from copying;
- parameter plugging has a compositional interpretation.

The optimizer can change without changing these semantics.

---

# 19. Plugin interfaces derived from the mathematics

A minimal semantic plugin interface is:

```python
from typing import Protocol


class KernelPlugin(Protocol[A, B]):
    def __call__(self, value: A) -> Dist[B]:
        ...
```

The core only needs:

```python
def compose(first, second):
    return lambda value: first(value).bind(second)
```

Everything else can be implemented outside the kernel:

- vector-store adapters;
- database clients;
- embedding models;
- rerankers;
- LLM providers;
- evaluators;
- caching;
- tracing;
- retry policies.

A deterministic adapter is lifted:

```python
normalize_plugin = deterministic(normalize_query)
```

A stochastic adapter directly implements:

```python
Query -> Dist[RetrievedSet]
```

A production system will often implement a sampler rather than enumerate the complete distribution:

```python
from random import Random
from typing import Protocol


class OperationalKernel(Protocol[A, B]):
    def sample(
        self,
        value: A,
        rng: Random,
    ) -> B:
        ...
```

The mathematical kernel is the **denotation**. The `sample` method is one possible **operational realization** of it.

These should not be conflated:

```text
Denotation:
    Query -> probability distribution over answers

Execution:
    Query × RNG state -> one answer × new RNG state
```

The denotational interface supports reasoning. The operational interface supports execution.

---

# 20. What the categorical laws buy the implementation

The laws become testable architecture properties.

### Identity test

Adding a pass-through stage does not change behavior:

```python
kernel_then(kernel_identity, plugin)
```

is equivalent to `plugin`.

### Associativity test

Regrouping a pipeline does not change its denotation:

```python
kernel_then(kernel_then(a, b), c)
```

is equivalent to:

```python
kernel_then(a, kernel_then(b, c))
```

### Normalization test

Every total kernel returns probability mass \(1\).

### Determinism test

A claimed deterministic plugin preserves copying:

\[
\mathrm{copy}\circ f
=
(f\otimes f)\circ\mathrm{copy}.
\]

### Independent parallelism test

Tensor composition uses independent random choices rather than accidentally reusing one sample.

These are stronger than ordinary interface tests. They test the algebra that makes components safely composable.

---

# 21. The hierarchy of concepts

The concepts build on one another:

## Category

Provides typed sequential composition:

\[
X\to Y\to Z.
\]

## Functor

Translates compositional structures:

\[
F(g\circ f)=F(g)\circ F(f).
\]

## Natural transformation

Transforms functors uniformly.

## Monad

Packages an effect such as probability:

\[
X\to\mathsf{Prob}(Y).
\]

## Kleisli category

Turns effectful functions into composable morphisms.

## Symmetric monoidal category

Adds parallel composition:

\[
f\otimes g.
\]

## Markov category

Adds the probability-specific behavior of copying, discarding, deterministic processes, and stochastic processes.

---

# Compact interpretation

The ordinary functional world is:

\[
X\xrightarrow{f}Y.
\]

The stochastic world is:

\[
X\xrightarrow{K}\mathsf{Prob}(Y).
\]

The probability monad converts these effectful functions into the morphisms of a category:

\[
X\rightsquigarrow Y.
\]

The identity is:

\[
x\mapsto\delta_x.
\]

Composition is:

\[
(L\odot K)(x,dz)
=
\int_Y L(y,dz)\,K(x,dy).
\]

Parallel composition is:

\[
K\otimes L.
\]

A Markov category then records the crucial fact that:

\[
\text{sample once and copy}
\neq
\text{copy the input and sample twice}.
\]

For a compositional RAG architecture, that gives a precise semantic backbone for pipeline stages, configuration, random execution, deterministic adapters, parallel retrieval, evaluation, and optimization.


---

> give proper motivation and build up to the actual definition of markov category. imam up to about products and equalizers and maybe limits in my knowledge, also functors and narural transformations.

<details><summary>💭 Thinking</summary>

**Defining Markov categories**

I’m framing Markov categories as symmetric monoidal settings for stochastic processes. I’ll emphasize copying, discarding, stochastic morphisms, deterministic maps, and how these structures support composition and conditional independence.

**Defined Markov categories**

</details>

The key conceptual jump is this: **probability forces us to weaken “product.”** Cartesian categories let every morphism duplicate data naturally; stochastic maps do not. Markov categories are built to retain exactly the parts of product structure that probability actually supports.

```json
{"system2_search_query":[{"q":"Tobias Fritz Markov categories definition commutative comonoid arXiv"},{"q":"Markov categories synthetic probability definition copy discard deterministic morphism arXiv"}],"response_length":"medium"}
```

<details><summary>💭 Thinking</summary>

**Searched 14 websites**

</details>

```json
{"open":[{"ref_id":"turn219960search23"}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Searched 1 website**

</details>

A useful way to organize the buildup is to start from something you already know: in a category with finite products, the product is doing **two jobs** at once—parallel composition and data management. Probability preserves the first job but breaks part of the second.

<details><summary>💭 Thinking</summary>

**Contrasting categorical products**

I’m highlighting the key distinction: stochastic maps usually lack unique pairings, so ordinary products fail. Tensor products retain joint systems, while copying is explicit and generally not natural for random maps.

**Contrasted categorical products**

</details>

```json
{"system1_search_query":[{"q":"site:arxiv.org/abs/1908.07021 Markov categories Fritz definition"},{"q":"site:arxiv.org Markov categories Fritz Gonda Perrone Rischel deterministic morphisms cartesian subcategory"}],"response_length":"medium"}
```

<details><summary>💭 Thinking</summary>

**Searched 2 websites**

</details>

Yes. Given where you are in category theory, I would **not** introduce Markov categories through monads or Kleisli categories first. Those are useful constructions later, but they obscure the motivation.

The clean path is

\[
\text{finite products}
\;\longrightarrow\;
\text{copy/delete structure}
\;\longrightarrow\;
\text{symmetric monoidal categories}
\;\longrightarrow\;
\text{what probability breaks}
\;\longrightarrow\;
\boxed{\text{Markov category}}.
\]

The central idea is:

> A cartesian category makes copying and discarding automatic and natural for every morphism. Probability still lets us copy and discard **values**, but copying is no longer natural with respect to stochastic morphisms.

That one failure essentially explains why Markov categories exist.

---

# 1. Start from products

Suppose \(\mathcal C\) has binary products.

For objects \(X,Y\), you have

\[
X\times Y
\]

with projections

\[
\pi_X:X\times Y\to X,
\qquad
\pi_Y:X\times Y\to Y.
\]

The universal property says that whenever

\[
f:Z\to X,
\qquad
g:Z\to Y,
\]

there exists a **unique**

\[
\langle f,g\rangle:Z\to X\times Y
\]

such that

\[
\pi_X\circ\langle f,g\rangle=f,
\qquad
\pi_Y\circ\langle f,g\rangle=g.
\]

Diagrammatically:

\[
\require{AMScd}
\begin{CD}
& Z &\\
@V f VV @VV \langle f,g\rangle V @VV g V\\
X @<\pi_X<< X\times Y @>\pi_Y>>Y
\end{CD}
\]

You presumably already know this.

What is less often emphasized is that **products secretly give you a little algebra of information flow**.

---

# 2. Products automatically let you copy things

Take

\[
X\times X.
\]

We have two maps

\[
\operatorname{id}_X:X\to X,
\qquad
\operatorname{id}_X:X\to X.
\]

By the product universal property, there is a unique map

\[
\Delta_X
=
\langle\operatorname{id}_X,\operatorname{id}_X\rangle
:
X\to X\times X.
\]

In \(\mathbf{Set}\),

\[
\Delta_X(x)=(x,x).
\]

This is the **diagonal map**.

It literally means:

> copy the information \(x\).

I'll write it pictorially as

```text
       X
       │
       │
      / \
     /   \
    X     X
```

or

\[
\Delta_X:X\to X\times X.
\]

---

# 3. A terminal object lets you delete things

If your category has a terminal object \(1\), then for every \(X\) there is a unique map

\[
!_X:X\to1.
\]

In \(\mathbf{Set}\), \(1=\{*\}\), so

\[
x\mapsto *.
\]

This simply forgets \(x\).

Graphically:

```text
X
│
▼
discard
```

So finite products give you two canonical operations:

\[
\boxed{
\Delta_X:X\to X\times X
}
\]

for copying, and

\[
\boxed{
!_X:X\to1
}
\]

for discarding.

---

# 4. These operations satisfy equations

Copying twice should not depend on which copy you copy first.

Starting from \(X\), compare

\[
X
\xrightarrow{\Delta}
X\times X
\xrightarrow{\Delta\times\operatorname{id}}
X\times X\times X
\]

with

\[
X
\xrightarrow{\Delta}
X\times X
\xrightarrow{\operatorname{id}\times\Delta}
X\times X\times X.
\]

Both send

\[
x\mapsto(x,x,x).
\]

So

\[
(\Delta_X\times\operatorname{id}_X)\circ\Delta_X
=
(\operatorname{id}_X\times\Delta_X)\circ\Delta_X.
\]

This is **coassociativity**.

Likewise copying and then throwing away either copy changes nothing:

\[
(!_X\times\operatorname{id}_X)\circ\Delta_X
=
\operatorname{id}_X
\]

and

\[
(\operatorname{id}_X\times !_X)\circ\Delta_X
=
\operatorname{id}_X,
\]

modulo the obvious identifications

\[
1\times X\cong X\cong X\times1.
\]

And it doesn't matter which copy you call the first one:

\[
\sigma_{X,X}\circ\Delta_X=\Delta_X,
\]

where

\[
\sigma_{X,X}:X\times X\to X\times X
\]

swaps the two factors.

These equations will become exactly the **commutative comonoid axioms**.

But don't worry about that terminology yet.

---

# 5. There is another important fact hiding in products

Suppose

\[
f:X\to Y.
\]

There are two ways of getting two copies of its output.

First apply \(f\), then copy:

\[
X
\xrightarrow{f}
Y
\xrightarrow{\Delta_Y}
Y\times Y.
\]

Or copy the input and apply \(f\) to both copies:

\[
X
\xrightarrow{\Delta_X}
X\times X
\xrightarrow{f\times f}
Y\times Y.
\]

In a cartesian category these are equal:

\[
\boxed{
\Delta_Y\circ f
=
(f\times f)\circ\Delta_X.
}
\]

For ordinary functions this is obvious:

\[
x
\mapsto f(x)
\mapsto(f(x),f(x))
\]

versus

\[
x
\mapsto(x,x)
\mapsto(f(x),f(x)).
\]

Same answer.

Similarly, deleting after \(f\) is the same as deleting immediately:

\[
\boxed{
!_Y\circ f=!_X.
}
\]

This means that **copying and deleting are natural with respect to every ordinary function**.

This seemingly innocent property is exactly what probability breaks.

---

# 6. Enter stochastic maps

Let's consider the simplest probabilistic category:

\[
\mathbf{FinStoch}.
\]

Its objects are finite sets.

A morphism

\[
K:X\to Y
\]

is a stochastic matrix

\[
K(y\mid x)\ge0
\]

such that

\[
\sum_{y\in Y}K(y\mid x)=1.
\]

Composition is

\[
(L\circ K)(z\mid x)
=
\sum_y L(z\mid y)K(y\mid x).
\]

So morphisms are finite Markov kernels / channels. \(\mathbf{FinStoch}\) is the canonical elementary example of a Markov category. citeturn282796view0

For example, let

\[
B=\{H,T\}.
\]

A fair coin is a morphism

\[
p:1\to B
\]

with

\[
p(H)=p(T)=\frac12.
\]

Think:

```python
def coin():
    return {
        "H": 0.5,
        "T": 0.5,
    }
```

---

# 7. Why isn't \(X\times Y\) a categorical product anymore?

This is probably the most important step in the buildup.

Suppose \(B\times B\) were the categorical product in \(\mathbf{FinStoch}\).

Take two morphisms

\[
p:1\to B,
\qquad
p:1\to B
\]

representing two fair-coin marginals.

The product universal property would require a **unique**

\[
r:1\to B\times B
\]

whose first and second marginals are both \(p\).

But there isn't a unique one.

One possibility is two independent fair coins:

\[
r_{\mathrm{ind}}(H,H)=\frac14
\]

\[
r_{\mathrm{ind}}(H,T)=\frac14
\]

\[
r_{\mathrm{ind}}(T,H)=\frac14
\]

\[
r_{\mathrm{ind}}(T,T)=\frac14.
\]

Another is a perfectly correlated pair:

\[
r_{\mathrm{corr}}(H,H)=\frac12,
\]

\[
r_{\mathrm{corr}}(T,T)=\frac12,
\]

and

\[
r_{\mathrm{corr}}(H,T)
=
r_{\mathrm{corr}}(T,H)
=
0.
\]

Both have the same marginals:

\[
P(\text{first}=H)
=
P(\text{second}=H)
=
\frac12.
\]

So

\[
\pi_1r_{\mathrm{ind}}
=
\pi_1r_{\mathrm{corr}}
=
p
\]

and similarly for \(\pi_2\).

Thus the universal property fails because **uniqueness fails**.

This is not an incidental technical problem. Joint distributions are not determined by their marginals. That's essentially what correlation is.

---

# 8. But we still want \(X\times Y\) to mean "two systems together"

Although \(X\times Y\) is no longer a categorical product, it remains extremely useful.

If I have

\[
K:X\to X'
\]

and

\[
L:Y\to Y',
\]

I can run them independently in parallel:

\[
K\otimes L:
X\times Y\to X'\times Y'
\]

where

\[
(K\otimes L)(x',y'\mid x,y)
=
K(x'\mid x)L(y'\mid y).
\]

Fritz explicitly describes this monoidal structure in \(\mathbf{FinStoch}\) as implementing independent parallel composition. citeturn282796view0

So we want an operation

\[
X\otimes Y
\]

that means roughly:

> the composite system consisting of an \(X\)-part and a \(Y\)-part.

But we **do not** want to require the product universal property.

That is exactly what a monoidal category gives us.

---

# 9. From cartesian product to monoidal tensor

A **monoidal category**

\[
(\mathcal C,\otimes,I)
\]

has a bifunctor

\[
\otimes:
\mathcal C\times\mathcal C\to\mathcal C.
\]

So we can combine objects:

\[
X,Y\mapsto X\otimes Y
\]

and morphisms:

\[
f:X\to X',
\qquad
g:Y\to Y'
\]

into

\[
f\otimes g:
X\otimes Y
\to
X'\otimes Y'.
\]

There is a unit object \(I\), along with coherent isomorphisms

\[
(X\otimes Y)\otimes Z
\cong
X\otimes(Y\otimes Z),
\]

\[
I\otimes X\cong X,
\qquad
X\otimes I\cong X.
\]

A **symmetric** monoidal category additionally has coherent swaps

\[
\sigma_{X,Y}:
X\otimes Y
\overset{\sim}{\longrightarrow}
Y\otimes X.
\]

The major difference from products is:

\[
\boxed{\text{There is no universal property required of }X\otimes Y.}
\]

It's just a way to combine systems.

So:

\[
\text{cartesian category}
\quad\text{is much stronger than}\quad
\text{symmetric monoidal category}.
\]

---

# 10. Cartesian categories are special symmetric monoidal categories

If \(\mathcal C\) has finite products, we can take

\[
X\otimes Y:=X\times Y
\]

and

\[
I:=1.
\]

This makes \(\mathcal C\) symmetric monoidal.

But it has extra structure: every object possesses canonical maps

\[
\Delta_X:X\to X\otimes X
\]

and

\[
\epsilon_X:X\to I.
\]

For a cartesian category these arise automatically from the universal property.

Once we throw away the universal property, however, these operations no longer come for free.

So suppose we add them explicitly.

This is the crucial move.

---

# 11. Abstract copying and discarding

Take a symmetric monoidal category

\[
(\mathcal C,\otimes,I).
\]

For every object \(X\), explicitly choose

\[
\Delta_X:X\to X\otimes X
\]

and

\[
\epsilon_X:X\to I.
\]

Interpret:

\[
\Delta_X=\text{copy},
\qquad
\epsilon_X=\text{discard}.
\]

We demand the same equations we observed for products.

Coassociativity:

\[
(\Delta_X\otimes\operatorname{id}_X)\circ\Delta_X
=
(\operatorname{id}_X\otimes\Delta_X)\circ\Delta_X.
\]

Counitality:

\[
(\epsilon_X\otimes\operatorname{id}_X)\circ\Delta_X
=
\operatorname{id}_X
\]

and

\[
(\operatorname{id}_X\otimes\epsilon_X)\circ\Delta_X
=
\operatorname{id}_X,
\]

with unitors suppressed.

Commutativity:

\[
\sigma_{X,X}\circ\Delta_X
=
\Delta_X.
\]

These precisely say that

\[
(X,\Delta_X,\epsilon_X)
\]

is a **commutative comonoid object** in \(\mathcal C\).

---

# 12. Why "comonoid"?

You may know an ordinary monoid:

\[
(M,\mu,e)
\]

with multiplication

\[
\mu:M\times M\to M
\]

and unit

\[
e:1\to M.
\]

A monoid object in a monoidal category has

\[
\mu:M\otimes M\to M
\]

and

\[
e:I\to M.
\]

A **comonoid** simply reverses the arrows:

\[
\Delta:X\to X\otimes X
\]

and

\[
\epsilon:X\to I.
\]

So:

\[
\text{monoid: combine two into one}
\]

whereas

\[
\text{comonoid: split one into two}.
\]

For information-flow purposes, the latter is interpreted as **copying**, not physically splitting a random sample into two independent random samples.

That distinction will matter shortly.

---

# 13. We also require copying to interact coherently with tensor

If \(X\) and \(Y\) both have copy operations, copying the composite system \(X\otimes Y\) should agree with copying its two components.

Ignoring associators, the equation is

\[
\Delta_{X\otimes Y}
=
(\operatorname{id}_X\otimes
\sigma_{X,Y}\otimes
\operatorname{id}_Y)
\circ
(\Delta_X\otimes\Delta_Y).
\]

Why the swap?

Starting with

\[
X\otimes Y,
\]

copying each separately gives

\[
X\otimes X\otimes Y\otimes Y.
\]

But copying the pair should produce

\[
(X\otimes Y)\otimes(X\otimes Y),
\]

so we rearrange the middle terms:

\[
X_1,X_2,Y_1,Y_2
\quad\mapsto\quad
X_1,Y_1,X_2,Y_2.
\]

Similarly,

\[
\epsilon_{X\otimes Y}
=
\epsilon_X\otimes\epsilon_Y
\]

modulo \(I\otimes I\cong I\).

There are analogous coherence requirements for \(I\).

At this stage you have essentially what is often called **copy-discard structure** or a **gs-monoidal/CD category**. Modern treatments describe this as a symmetric monoidal category with compatible chosen commutative comonoids on all objects. citeturn272650academia13

We still haven't imposed the specifically Markov condition.

---

# 14. Now ask: should copying be natural?

In a cartesian category, remember:

\[
\Delta_Y\circ f
=
(f\otimes f)\circ\Delta_X.
\tag{*}
\]

What happens for a stochastic map?

Take the fair coin

\[
p:I\to B.
\]

Compare the two sides.

### First sample, then copy

\[
I
\xrightarrow{p}
B
\xrightarrow{\Delta_B}
B\otimes B.
\]

This gives

\[
(H,H)\quad\text{with probability }\frac12
\]

and

\[
(T,T)\quad\text{with probability }\frac12.
\]

There are no mixed results.

---

### First copy the input, then sample twice

\[
I
\xrightarrow{\Delta_I}
I\otimes I
\xrightarrow{p\otimes p}
B\otimes B.
\]

This gives

\[
(H,H),(H,T),(T,H),(T,T)
\]

each with probability

\[
\frac14.
\]

They are manifestly different.

Therefore

\[
\boxed{
\Delta_B\circ p
\neq
(p\otimes p)\circ\Delta_I.
}
\]

So **copying cannot be natural with respect to arbitrary stochastic maps**.

This equation is arguably the conceptual heart of Markov categories.

---

# 15. Code makes the distinction obvious

```python
coin = {
    "H": 0.5,
    "T": 0.5,
}

# sample once, then copy the result
sample_once_then_copy = {
    ("H", "H"): 0.5,
    ("T", "T"): 0.5,
}

# two independent executions of the stochastic process
run_twice = {
    ("H", "H"): 0.25,
    ("H", "T"): 0.25,
    ("T", "H"): 0.25,
    ("T", "T"): 0.25,
}
```

These correspond to

\[
\Delta\circ p
\]

and

\[
(p\otimes p)\circ\Delta.
\]

This same distinction appears with LLM calls:

```text
call model once
then duplicate answer
```

is not

```text
duplicate prompt
then call model twice.
```

The latter creates two stochastic executions.

---

# 16. This explains exactly what we must weaken

For cartesian categories:

\[
\Delta_Y\circ f
=
(f\otimes f)\circ\Delta_X
\]

for **every** \(f\).

For stochastic categories, we cannot require that.

But what about discarding?

Consider

\[
X\xrightarrow{K}Y\xrightarrow{\epsilon_Y}I.
\]

A stochastic kernel outputs *something* with total probability \(1\). If we then forget what it was, nothing observable remains.

That's the same as immediately throwing away \(X\):

\[
\epsilon_Y\circ K
=
\epsilon_X.
\]

So deletion **is** natural:

\[
\boxed{
\epsilon_Y\circ f=\epsilon_X
}
\]

for every morphism \(f:X\to Y\).

For stochastic matrices this equation is exactly the normalization condition

\[
\sum_y f(y\mid x)=1.
\]

Fritz's basic \(\mathbf{FinStoch}\) example has precisely this normalization, and deletion is the unique stochastic morphism into the one-point space. citeturn282796view0

---

# 17. Naturality of deletion means \(I\) is terminal

This is a nice connection directly back to the category theory you know.

Suppose

\[
\epsilon_X:X\to I
\]

is natural for every morphism.

Take **any**

\[
f:X\to I.
\]

Naturality of \(\epsilon\) with \(f\) gives

\[
\epsilon_I\circ f=\epsilon_X.
\]

But

\[
\epsilon_I=\operatorname{id}_I
\]

from the comonoid/unit coherence.

Therefore

\[
f=\epsilon_X.
\]

So there is exactly one map

\[
X\to I.
\]

Thus \(I\) is terminal.

Conversely, if \(I\) is terminal, then every

\[
X\to I
\]

must be the unique discard map, so

\[
\epsilon_Y\circ f=\epsilon_X
\]

automatically.

Therefore:

\[
\boxed{
\text{natural deletion}
\iff
\text{monoidal unit }I\text{ is terminal}.
}
\]

This gives the cleanest modern definition.

---

# 18. The actual definition

We are now ready for it.

A **Markov category** is a symmetric monoidal category

\[
(\mathcal C,\otimes,I)
\]

such that every object \(X\) is equipped with a chosen **commutative comonoid**

\[
\Delta_X:X\to X\otimes X,
\qquad
\epsilon_X:X\to I,
\]

these comonoid structures are compatible with the monoidal structure, and the monoidal unit \(I\) is terminal.

Equivalently, instead of saying "\(I\) is terminal," say that discarding is natural:

\[
\boxed{
\epsilon_Y\circ f=\epsilon_X
\qquad
\forall f:X\to Y.
}
\]

This is essentially Fritz's definition: symmetric monoidal structure, compatible copy/delete commutative comonoids, together with the condition expressing normalization/causality. citeturn282796view0turn219960academia22

That is it.

No probability measures appear in the definition.

No Markov chains appear.

No conditional probability appears.

No monad appears.

It's an **abstract algebra of information flow** designed so that stochastic maps are a central example.

---

# 19. Compare cartesian and Markov categories

Now the difference becomes extremely precise.

In a cartesian category,

\[
\Delta_Y\circ f
=
(f\otimes f)\circ\Delta_X
\]

and

\[
\epsilon_Y\circ f
=
\epsilon_X
\]

for every morphism.

In a Markov category, only the second is required for every morphism:

\[
\epsilon_Y\circ f=\epsilon_X.
\]

The copying equation may fail.

That failure is where randomness lives.

---

# 20. Deterministic morphisms emerge from this

Once you're inside a Markov category, you can define:

\[
f:X\to Y
\]

to be **deterministic** exactly when it does preserve copying:

\[
\boxed{
\Delta_Y\circ f
=
(f\otimes f)\circ\Delta_X.
}
\]

Discarding is already preserved by every morphism.

So deterministic maps are exactly the maps that behave cartesianly with respect to copy.

Fritz uses precisely this definition, and the deterministic morphisms form a cartesian monoidal subcategory. citeturn282796view0turn272650search2

This is a very satisfying result:

\[
\boxed{
\text{inside the stochastic world lives an ordinary cartesian world.}
}
\]

For \(\mathbf{FinStoch}\), deterministic stochastic matrices correspond to ordinary functions

\[
f:X\to Y
\]

represented by

\[
K(y\mid x)
=
\begin{cases}
1 & y=f(x),\\
0 & \text{otherwise}.
\end{cases}
\]

---

# 21. So \(\mathbf{FinStoch}\) looks like this

Objects:

\[
X,Y,\ldots
\]

finite sets.

Morphisms:

\[
K:X\to Y
\]

stochastic matrices.

Sequential composition:

\[
(LK)(z\mid x)
=
\sum_yL(z\mid y)K(y\mid x).
\]

Tensor:

\[
X\otimes Y=X\times Y
\]

on underlying sets, with

\[
(K\otimes L)(y,v\mid x,u)
=
K(y\mid x)L(v\mid u).
\]

Copy:

\[
\Delta_X(x_1,x_2\mid x)
=
\begin{cases}
1 & x_1=x_2=x,\\
0 & \text{otherwise}.
\end{cases}
\]

Discard:

\[
\epsilon_X(*\mid x)=1.
\]

All the Markov-category axioms can be checked directly. Fritz presents \(\mathbf{FinStoch}\) as the paradigmatic example. citeturn282796view0

---

# 22. A subtle point: \(\otimes\) does not mean "independent variables"

This is worth getting exactly right.

If

\[
p:I\to X
\]

and

\[
q:I\to Y
\]

are states, then

\[
p\otimes q:I\to X\otimes Y
\]

is their independent joint distribution.

But an **arbitrary**

\[
r:I\to X\otimes Y
\]

may be correlated.

So:

\[
X\otimes Y
\]

means

> a system with an \(X\)-component and a \(Y\)-component,

not

> \(X\) and \(Y\) are independent.

Independence concerns how a particular morphism into \(X\otimes Y\) factors.

This is another reason categorical product would be wrong: product pairing would force the joint to be uniquely determined by its components.

---

# 23. Where your knowledge of limits fits

There is a useful conceptual boundary here.

You know that products are limits:

\[
X\times Y
=
\lim(X\leftarrow\varnothing\rightarrow Y)
\]

informally speaking, with the discrete two-object diagram.

Markov-category tensor products are **not generally limits**.

That is deliberate.

A limit has a universal property that says the maps into the combined object are uniquely determined by their components.

Probability specifically needs:

\[
\text{same marginals}
\not\Rightarrow
\text{same joint distribution}.
\]

So replacing categorical product by monoidal tensor is effectively saying:

> I still need "systems side by side," but I must stop asking for the universal property that destroys correlation.

That is probably the most direct bridge from your current category-theory knowledge to Markov categories.

---

# 24. The whole construction in one picture

Start with a cartesian category.

You have

\[
X\times Y
\]

plus automatically:

\[
\Delta_X:X\to X\times X,
\]

\[
!_X:X\to1.
\]

And both are natural:

\[
\Delta_Y f=(f\times f)\Delta_X,
\]

\[
!_Yf=!_X.
\]

Now weaken:

\[
\times
\rightsquigarrow
\otimes
\]

and explicitly retain copy and discard:

\[
\Delta_X:X\to X\otimes X,
\]

\[
\epsilon_X:X\to I.
\]

Keep their internal comonoid equations.

Keep discard natural:

\[
\epsilon_Yf=\epsilon_X.
\]

But **drop naturality of copying**:

\[
\Delta_Yf
\stackrel{\text{not necessarily}}{=}
(f\otimes f)\Delta_X.
\]

You have reached a Markov category.

So the compact conceptual equation is:

\[
\boxed{
\text{Markov category}
\approx
\text{cartesian structure
minus natural copying}.
}
\]

More precisely, it is a symmetric monoidal category with compatible copy/discard commutative-comonoid structure and terminal monoidal unit. citeturn219960academia22turn282796view0

---

# 25. Why this is a better starting point than the probability monad

Only **after** understanding the above would I introduce

\[
P(X)=\text{probability distributions on }X.
\]

Given a suitable commutative probability monad \(P\) on a category with finite products, its Kleisli arrows are

\[
X\to P(Y),
\]

i.e. stochastic maps

\[
X\rightsquigarrow Y.
\]

Under appropriate normalization/affineness assumptions, the resulting Kleisli category is a Markov category. Fritz states this construction explicitly: a commutative monad \(P\) with \(P(1)\cong1\) on a finite-product category gives a Markov Kleisli category. citeturn282796view0

But that's a **way to construct examples**.

It isn't the conceptual reason for the definition.

The conceptual reason is:

\[
\text{products force unique coupling}
\]

and

\[
\text{products force copy naturality},
\]

both of which are too strong for stochastic processes.

---

# 26. For the RAG architecture, this distinction is quite concrete

Suppose

\[
Q=\text{queries},
\qquad
A=\text{answers}.
\]

An LLM could be represented semantically by

\[
G:Q\to A
\]

as a morphism in some Markov category.

If \(G\) is stochastic, then:

\[
\Delta_A\circ G
\]

means

> generate once and copy the answer.

Whereas

\[
(G\otimes G)\circ\Delta_Q
\]

means

> copy the query and perform two generations.

Those need not agree:

\[
\Delta_A G
\neq
(G\otimes G)\Delta_Q.
\]

By contrast, if

\[
N:Q\to Q'
\]

is deterministic query normalization, you'd expect

\[
\Delta_{Q'}N
=
(N\otimes N)\Delta_Q.
\]

Thus the categorical definition gives you a structural distinction between

```text
pure/deterministic plugin
```

and

```text
stochastic/effectful plugin
```

without encoding that distinction as an arbitrary interface flag.

It is an equation that the morphism either satisfies or does not. citeturn272650search2

---

## The one diagram I'd keep in your head

\[
\begin{array}{ccc}
X & \xrightarrow{f} & Y\\[4pt]
\downarrow\Delta_X && \downarrow\Delta_Y\\[4pt]
X\otimes X & \xrightarrow{f\otimes f} & Y\otimes Y
\end{array}
\]

In a **cartesian category**, this commutes for every \(f\).

In a **Markov category**, it need not commute.

The morphisms for which it **does** commute are called deterministic.

Meanwhile,

\[
\begin{array}{ccc}
X & \xrightarrow{f} & Y\\
& \searrow_{\epsilon_X} & \downarrow\epsilon_Y\\
&& I
\end{array}
\]

**does commute for every \(f\)**.

That is normalization.

Those two diagrams contain most of the conceptual content of the definition.

If you're going deeper from here, I would next develop **symmetric monoidal categories and commutative comonoids properly from the universal property of cartesian products**, and prove the theorem that cartesian categories are precisely the appropriate symmetric monoidal categories in which the copy/delete structure is natural. That theorem makes Markov categories feel almost inevitable rather than like a collection of probability-specific axioms.


---

> now redo it as a mathematical textbook style with definitions and examples and exercises, use existing reaource as reference (and cite), try to chose examples and exercises from cs or cs/programming adjacent

I’ll recast it as a short textbook chapter: prerequisites → motivating failure of products in stochastic computation → monoidal/comonoid structure → formal Markov-category definition → deterministic maps → worked CS examples → exercises. I’ll anchor the presentation in the original Markov-category literature rather than secondary summaries.

```json
{"system2_search_query":[{"q":"site:arxiv.org Markov categories Fritz 2020 probability paper"},{"q":"site:arxiv.org Markov categories conditional independence Fritz"},{"q":"site:arxiv.org categorical probability Markov kernels Giry Kleisli stochastic matrices"}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Searched 1 website**

**Framing the compositional model**

I’m unable to provide private chain-of-thought or a word-for-word reconstruction of hidden reasoning. I can provide a concise, user-facing summary of the approach instead.

**Framed the compositional model**

</details>

```json
{"screenshot":[{"ref_id":"turn821434search10","pageno":9},{"ref_id":"turn821434search10","pageno":29}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Searching the web**

**Building a textbook treatment**

I’m not able to provide hidden chain-of-thought or reconstruct private internal reasoning. I can still give a concise, user-facing explanation of how I would structure the mathematical development, including definitions, examples, and exercises.

**Built a textbook treatment**

</details>

# From Products to Markov Categories
## A categorical introduction motivated by randomized computation

This chapter assumes familiarity with categories, functors, natural transformations, terminal objects, products, equalizers, and the basic idea of limits. It does **not** assume prior knowledge of monoidal categories, comonoids, probability monads, or string diagrams.

The development follows the viewpoint introduced systematically by Tobias Fritz: Markov categories axiomatize the compositional structure shared by categories of stochastic maps, while abstracting away the analytic details of particular probability spaces. Fritz's basic examples include finite stochastic matrices, measurable Markov kernels, and Gaussian channels. citeturn729673view0turn499123view2 The copy/discard formulation has antecedents in Cho and Jacobs' categorical treatment of probability and Bayesian inversion. citeturn729673view1

Our route will be:

\[
\boxed{
\text{products}
\to
\text{copying and discarding}
\to
\text{monoidal products}
\to
\text{stochastic maps}
\to
\text{failure of natural copying}
\to
\text{Markov categories}
}
\]

The crucial observation will be that **categorical products are too rigid for probabilistic computation**.

---

# 1. Products as an algebra of data flow

We begin with an ordinary category \(\mathcal C\) having finite products.

## Definition 1.1 — Binary product

A **product** of objects \(X,Y\) consists of an object

\[
X\times Y
\]

and morphisms

\[
\pi_1:X\times Y\to X,
\qquad
\pi_2:X\times Y\to Y
\]

such that for every pair

\[
f:Z\to X,
\qquad
g:Z\to Y,
\]

there exists a unique morphism

\[
\langle f,g\rangle:Z\to X\times Y
\]

for which

\[
\pi_1\circ\langle f,g\rangle=f,
\qquad
\pi_2\circ\langle f,g\rangle=g.
\]

You can read this computationally.

If

```text
f : Z -> X
g : Z -> Y
```

then the product gives a canonical program

```text
z |-> (f(z), g(z))
```

and says that this is the **unique** program into \(X\times Y\) with those two projections.

---

## Example 1.2 — Product types

In a typed functional language,

```python
def f(z: Z) -> X:
    ...

def g(z: Z) -> Y:
    ...

def pair(z: Z) -> tuple[X, Y]:
    return (f(z), g(z))
```

is the concrete realization of

\[
\langle f,g\rangle.
\]

Projection is ordinary tuple access:

```python
def pi1(pair):
    return pair[0]

def pi2(pair):
    return pair[1]
```

and indeed

```python
pi1(pair(z)) == f(z)
pi2(pair(z)) == g(z)
```

---

# 2. Products secretly give us copying

Set \(Y=X\), and take both maps to be the identity:

\[
\operatorname{id}_X:X\to X,
\qquad
\operatorname{id}_X:X\to X.
\]

By the universal property there is a unique morphism

\[
\Delta_X
:=
\langle\operatorname{id}_X,\operatorname{id}_X\rangle
:
X\to X\times X.
\]

## Definition 2.1 — Diagonal

The morphism

\[
\Delta_X:X\to X\times X
\]

is called the **diagonal**.

In \(\mathbf{Set}\),

\[
\Delta_X(x)=(x,x).
\]

Computationally:

```python
def copy(x):
    return (x, x)
```

Thus categorical products encode an operation that can be interpreted as **copying a value**.

---

# 3. The terminal object gives us discarding

Let \(1\) be terminal.

For every \(X\), there is a unique map

\[
!_X:X\to1.
\]

## Definition 3.1 — Discard

We interpret

\[
!_X:X\to1
\]

as **discarding** an \(X\)-value.

For example, if the one-element type is represented by `None`:

```python
def discard(x):
    return None
```

So finite products automatically supply two operations:

\[
\boxed{
\Delta_X:X\to X\times X
}
\]

and

\[
\boxed{
!_X:X\to1.
}
\]

These turn out to contain much of the structure we need for talking about information flow.

---

# 4. The equations obeyed by copy and discard

These maps are not arbitrary.

For example, there are two ways of turning one \(X\) into three copies:

\[
X
\xrightarrow{\Delta_X}
X\times X
\xrightarrow{\Delta_X\times\operatorname{id}_X}
X\times X\times X
\]

and

\[
X
\xrightarrow{\Delta_X}
X\times X
\xrightarrow{\operatorname{id}_X\times\Delta_X}
X\times X\times X.
\]

Both compute

\[
x\mapsto(x,x,x).
\]

Therefore, suppressing the canonical associativity isomorphisms,

\[
(\Delta_X\times\operatorname{id}_X)\circ\Delta_X
=
(\operatorname{id}_X\times\Delta_X)\circ\Delta_X.
\tag{4.1}
\]

This is called **coassociativity**.

Copying and then discarding one copy returns the original:

\[
(!_X\times\operatorname{id}_X)\circ\Delta_X
=
\operatorname{id}_X,
\tag{4.2}
\]

and

\[
(\operatorname{id}_X\times !_X)\circ\Delta_X
=
\operatorname{id}_X.
\tag{4.3}
\]

Finally, exchanging the copies does nothing:

\[
\sigma_{X,X}\circ\Delta_X=\Delta_X,
\tag{4.4}
\]

where

\[
\sigma_{X,X}:X\times X\to X\times X
\]

swaps the two factors.

The algebraic structure described by (4.1)–(4.4) is called a **commutative comonoid**. It will reappear in the definition of a Markov category. Fritz's definition explicitly equips every object with exactly this copy/discard comonoid structure. citeturn261064view0

---

# 5. The particularly strong property of cartesian copying

Now let

\[
f:X\to Y
\]

be an arbitrary morphism.

There are two ways to produce two \(Y\)'s.

First compute \(f\), then copy:

\[
X
\xrightarrow{f}
Y
\xrightarrow{\Delta_Y}
Y\times Y.
\]

Alternatively copy \(X\), then run \(f\) on each copy:

\[
X
\xrightarrow{\Delta_X}
X\times X
\xrightarrow{f\times f}
Y\times Y.
\]

In a category with products,

\[
\boxed{
\Delta_Y\circ f
=
(f\times f)\circ\Delta_X.
}
\tag{5.1}
\]

### Proposition 5.1

Equation (5.1) holds for every \(f\) in every category with finite products.

### Proof

Apply the first projection to both sides:

\[
\pi_1\circ\Delta_Y\circ f=f,
\]

while

\[
\pi_1\circ(f\times f)\circ\Delta_X=f.
\]

Likewise after \(\pi_2\), both sides equal \(f\).

By the **uniqueness** part of the product universal property, the two morphisms

\[
X\to Y\times Y
\]

must therefore be equal. \(\square\)

Likewise,

\[
!_Y\circ f=!_X
\tag{5.2}
\]

because both sides are maps \(X\to1\), and \(1\) is terminal.

---

## Remark 5.2 — Naturality

If you know natural transformations, (5.1) and (5.2) should look familiar.

The family

\[
\Delta_X:X\to X\times X
\]

behaves naturally in \(X\), and so does

\[
!_X:X\to1.
\]

This is not a superficial property.

It says that **every computation in a cartesian category commutes with copying**.

In deterministic programming that is perfectly reasonable:

```python
y = f(x)
result1 = (y, y)
```

and

```python
result2 = (f(x), f(x))
```

produce the same mathematical value, provided `f` is an ordinary pure function.

Probability changes this.

---

# 6. Randomized functions

Consider a randomized program

```python
def coin_flip() -> str:
    ...
```

whose result is

\[
H
\]

with probability \(1/2\) and

\[
T
\]

with probability \(1/2\).

Now compare:

```python
x = coin_flip()
result = (x, x)
```

with

```python
result = (
    coin_flip(),
    coin_flip(),
)
```

The first program produces only

\[
(H,H)
\quad\text{or}\quad
(T,T),
\]

each with probability \(1/2\).

The second produces

\[
(H,H),(H,T),(T,H),(T,T)
\]

each with probability \(1/4\).

Thus

\[
\boxed{
\text{run once and copy result}
\neq
\text{run twice}.
}
\]

This is precisely the equation that cartesian categories force to be equal.

We have found our first obstruction.

---

# 7. Finite stochastic maps

Before solving the problem abstractly, let us build a concrete category.

## Definition 7.1 — Finite stochastic map

For finite sets \(X,Y\), a stochastic map

\[
K:X\to Y
\]

assigns probabilities

\[
K(y\mid x)\in[0,1]
\]

such that

\[
\sum_{y\in Y}K(y\mid x)=1
\]

for each \(x\in X\).

Equivalently, it is a stochastic matrix.

The category whose objects are finite sets and whose morphisms are stochastic matrices is conventionally denoted

\[
\mathbf{FinStoch}.
\]

Fritz uses \(\mathbf{FinStoch}\) as the basic running example of a Markov category. citeturn503082view1turn499123view1

---

## Example 7.2 — Randomized load balancer

Let

\[
R=\{\texttt{request}\}
\]

and

\[
S=\{A,B\}.
\]

A randomized router might have

\[
K(A\mid\texttt{request})=0.7,
\]

\[
K(B\mid\texttt{request})=0.3.
\]

In code:

```python
router = {
    "request": {
        "server-A": 0.7,
        "server-B": 0.3,
    }
}
```

A stochastic map is therefore a categorical abstraction of a randomized program of type

```text
X -> randomized Y
```

or, informally,

```text
X -> Distribution[Y].
```

---

# 8. Composition of stochastic maps

Suppose

\[
K:X\to Y
\]

and

\[
L:Y\to Z.
\]

Then define

\[
(L\circ K)(z\mid x)
=
\sum_{y\in Y}
L(z\mid y)K(y\mid x).
\tag{8.1}
\]

This is ordinary matrix multiplication.

The interpretation is:

> sum over all possible intermediate values \(y\).

For example,

\[
X\xrightarrow{K}Y\xrightarrow{L}Z
\]

is itself one probabilistic computation

\[
X\xrightarrow{L\circ K}Z.
\]

---

## Example 8.1 — Router followed by machine failure

Suppose

\[
K(A)=0.7,\qquad K(B)=0.3.
\]

The probability that server \(A\) succeeds is \(0.9\), while \(B\) succeeds with probability \(0.8\).

Then

\[
P(\text{success})
=
0.7(0.9)+0.3(0.8)
=
0.87.
\]

The intermediate server identity has been marginalized away.

This is the same algebra that appears when Markov kernels are composed in more general probability spaces; Fritz's framework deliberately abstracts this compositional structure. citeturn729673view0

---

# 9. Why categorical products fail in \(\mathbf{FinStoch}\)

Now we reach the main motivation.

Let

\[
B=\{H,T\}
\]

and let

\[
p:1\to B
\]

denote a fair coin.

Suppose the ordinary set product

\[
B\times B
\]

were also the categorical product in \(\mathbf{FinStoch}\).

Given two copies of \(p\),

\[
p:1\to B,
\qquad
p:1\to B,
\]

the product universal property would require a **unique**

\[
r:1\to B\times B
\]

whose two marginals are \(p\).

But consider two candidates.

### Independent pair

\[
r_{\mathrm{ind}}(H,H)=\frac14,
\]

\[
r_{\mathrm{ind}}(H,T)=\frac14,
\]

\[
r_{\mathrm{ind}}(T,H)=\frac14,
\]

\[
r_{\mathrm{ind}}(T,T)=\frac14.
\]

### Perfectly correlated pair

\[
r_{\mathrm{same}}(H,H)=\frac12,
\]

\[
r_{\mathrm{same}}(T,T)=\frac12,
\]

with the other probabilities zero.

Both have first marginal

\[
p
\]

and second marginal

\[
p.
\]

Yet

\[
r_{\mathrm{ind}}\neq r_{\mathrm{same}}.
\]

Therefore uniqueness fails.

---

## Proposition 9.1

The ordinary set-level object \(X\times Y\), equipped with its deterministic projections, is in general **not** a categorical product in \(\mathbf{FinStoch}\).

### Interpretation

The pair of marginal distributions

\[
P_X,\qquad P_Y
\]

does not uniquely determine a joint distribution

\[
P_{X,Y}.
\]

There may be many different **couplings**, distinguished by correlation.

This tells us exactly what is wrong with categorical products for probability:

\[
\boxed{
\text{product universal property identifies a joint object too strongly with its components.}
}
\]

Probability needs room for correlation.

---

# 10. What we want to keep from products

We should not throw away \(X\times Y\) entirely.

We still want to say that

\[
X
\quad\text{and}\quad
Y
\]

can exist side-by-side.

For example, given

\[
K:X\to X'
\]

and

\[
L:Y\to Y',
\]

we want to run them independently in parallel.

For stochastic maps define

\[
K\otimes L:
X\times Y\to X'\times Y'
\]

by

\[
(K\otimes L)(x',y'\mid x,y)
=
K(x'\mid x)L(y'\mid y).
\tag{10.1}
\]

This operation **is useful**.

What failed was not "put two systems next to each other."

What failed was the **universal property of the categorical product**.

This motivates monoidal categories.

---

# 11. Monoidal categories: parallel composition without product universality

## Definition 11.1 — Monoidal category

A monoidal category consists of a category \(\mathcal C\), a bifunctor

\[
\otimes:
\mathcal C\times\mathcal C\to\mathcal C,
\]

an object \(I\), and natural isomorphisms

\[
\alpha_{X,Y,Z}:
(X\otimes Y)\otimes Z
\overset{\sim}{\longrightarrow}
X\otimes(Y\otimes Z),
\]

\[
\lambda_X:I\otimes X\overset{\sim}{\longrightarrow}X,
\]

\[
\rho_X:X\otimes I\overset{\sim}{\longrightarrow}X,
\]

satisfying the standard coherence conditions.

A **symmetric monoidal category** additionally has natural isomorphisms

\[
\sigma_{X,Y}:X\otimes Y\overset{\sim}{\longrightarrow}Y\otimes X
\]

which behave like swapping parallel components.

For readability we will suppress associators and unitors and write, for example,

\[
X\otimes Y\otimes Z
\]

without specifying parentheses.

---

## Computational interpretation

Think of

\[
\circ
\]

as sequential composition and

\[
\otimes
\]

as parallel composition.

If

```text
f : X -> Y
g : A -> B
```

then

```text
f ⊗ g : (X,A) -> (Y,B)
```

means:

```python
def parallel(x, a):
    return (f(x), g(a))
```

for deterministic functions.

For stochastic functions, it means **independent parallel execution**.

---

# 12. Cartesian monoidal versus merely monoidal

Every category with finite products becomes symmetric monoidal by taking

\[
X\otimes Y:=X\times Y,
\qquad
I:=1.
\]

But a general monoidal category does **not** require \(\otimes\) to satisfy a product universal property.

That is the key relaxation.

\[
\boxed{
\text{cartesian monoidal}
\Longrightarrow
\text{symmetric monoidal},
}
\]

but not conversely.

Thus a monoidal tensor gives us

> systems side by side

without claiming

> every map into the combined system is uniquely determined by its projections.

That is exactly what probability needs.

Fong's categorical treatment of Bayesian networks similarly uses symmetric monoidal structure to model parallel pieces of causal/probabilistic information flow. citeturn164149academia0

---

# 13. But we lost copying and discarding

There is a price.

For a categorical product, the maps

\[
\Delta_X:X\to X\times X
\]

and

\[
!_X:X\to1
\]

came automatically from universal properties.

For a generic tensor

\[
X\otimes X,
\]

there is no canonical morphism

\[
X\to X\otimes X.
\]

Similarly, a generic monoidal unit \(I\) need not be terminal, so there may not be a unique map

\[
X\to I.
\]

Probability, however, still has perfectly meaningful operations for:

1. copying an already-existing value;
2. throwing a value away.

So instead of deriving these maps from products, we add them explicitly.

---

# 14. Comonoids

## Definition 14.1 — Comonoid object

Let

\[
(\mathcal C,\otimes,I)
\]

be a monoidal category.

A **comonoid object** consists of an object \(X\) together with morphisms

\[
\Delta_X:X\to X\otimes X
\]

and

\[
\epsilon_X:X\to I
\]

satisfying

\[
(\Delta_X\otimes\operatorname{id}_X)\circ\Delta_X
=
(\operatorname{id}_X\otimes\Delta_X)\circ\Delta_X
\tag{14.1}
\]

and

\[
(\epsilon_X\otimes\operatorname{id}_X)\circ\Delta_X
=
\operatorname{id}_X,
\tag{14.2}
\]

\[
(\operatorname{id}_X\otimes\epsilon_X)\circ\Delta_X
=
\operatorname{id}_X.
\tag{14.3}
\]

A comonoid in a symmetric monoidal category is **commutative** when

\[
\sigma_{X,X}\circ\Delta_X
=
\Delta_X.
\tag{14.4}
\]

---

## Why "comonoid"?

A monoid object has multiplication

\[
\mu:M\otimes M\to M
\]

and unit

\[
\eta:I\to M.
\]

Reverse the arrows:

\[
\Delta:X\to X\otimes X,
\qquad
\epsilon:X\to I.
\]

You obtain a comonoid.

For data-flow purposes:

\[
\Delta=\text{copy},
\]

\[
\epsilon=\text{discard}.
\]

---

# 15. Copy/discard structure

We now equip **every** object with such a commutative comonoid.

Moreover, these structures should respect tensor products.

Schematically,

\[
\Delta_{X\otimes Y}
\]

must amount to:

1. copy \(X\);
2. copy \(Y\);
3. rearrange the wires into two copies of \(X\otimes Y\).

Suppressing associators,

\[
\Delta_{X\otimes Y}
=
(\operatorname{id}_X\otimes
\sigma_{X,Y}\otimes
\operatorname{id}_Y)
\circ
(\Delta_X\otimes\Delta_Y).
\tag{15.1}
\]

Likewise,

\[
\epsilon_{X\otimes Y}
=
\epsilon_X\otimes\epsilon_Y.
\tag{15.2}
\]

There are corresponding coherence equations at \(I\).

Closely related structures are called **copy-discard categories**, **CD categories**, or **gs-monoidal categories**, with terminology varying somewhat across the literature. Fritz and Liang study the gs-monoidal version explicitly and describe its string diagrams as term-graph-like combinatorial structures, which makes the connection with computer implementations particularly direct. citeturn729673view2turn164149academia1

But this is still not quite a Markov category.

---

# 16. What should happen when we discard stochastic output?

Take a stochastic computation

\[
K:X\to Y.
\]

There are two programs:

```text
run K;
discard result
```

and

```text
discard input immediately.
```

For a normalized probabilistic computation these should be observationally identical.

Categorically,

\[
\boxed{
\epsilon_Y\circ K=\epsilon_X.
}
\tag{16.1}
\]

In \(\mathbf{FinStoch}\), this says exactly

\[
\sum_y K(y\mid x)=1.
\]

So naturality of discard expresses **normalization**.

This is part of Fritz's definition of a Markov category; Fritz and Liang emphasize that related gs-monoidal/CD structures omit this normalization requirement. citeturn261064view0turn729673view2

---

# 17. Naturality of discard and terminality

There is a useful formulation entirely in terms of category theory you already know.

### Proposition 17.1

Assume

\[
\epsilon_I=\operatorname{id}_I.
\]

Then the condition

\[
\epsilon_Y\circ f=\epsilon_X
\]

for every

\[
f:X\to Y
\]

is equivalent to \(I\) being terminal.

### Proof

Suppose discard is natural.

Take any

\[
f:X\to I.
\]

Then

\[
\epsilon_I\circ f=\epsilon_X.
\]

Since

\[
\epsilon_I=\operatorname{id}_I,
\]

we obtain

\[
f=\epsilon_X.
\]

So there is exactly one map \(X\to I\), hence \(I\) is terminal.

Conversely, suppose \(I\) is terminal.

Both

\[
\epsilon_Y\circ f
\]

and

\[
\epsilon_X
\]

are morphisms

\[
X\to I.
\]

By terminality they must be equal. \(\square\)

Thus we may equivalently say:

\[
\boxed{
\text{the monoidal unit is terminal}.
}
\]

Such a symmetric monoidal category is often called **semicartesian**. Fritz explicitly notes this equivalent characterization. citeturn499123view3turn503082view1

---

# 18. Definition of a Markov category

We now have all the ingredients.

## Definition 18.1 — Markov category

A **Markov category** is a symmetric monoidal category

\[
(\mathcal C,\otimes,I)
\]

such that:

1. every object \(X\) is equipped with a specified commutative comonoid

\[
\Delta_X:X\to X\otimes X,
\qquad
\epsilon_X:X\to I;
\]

2. these comonoid structures are compatible with the symmetric monoidal structure;

3. discarding is natural:

\[
\epsilon_Y\circ f=\epsilon_X
\]

for every morphism

\[
f:X\to Y.
\]

Equivalently, condition 3 can be expressed by requiring \(I\) to be terminal.

This is essentially Fritz's Definition 2.1; the original presentation uses the names `copy` and `del` and states the equations diagrammatically. citeturn261064view0

---

# 19. What is strikingly absent from the definition

Notice what does **not** occur in Definition 18.1.

There is no mention of:

\[
[0,1].
\]

There are no measures.

There are no integrals.

There is no sigma-algebra.

There are no Markov chains.

There is not even an explicit concept of probability distribution.

Instead the definition says:

> Here is an abstract category of processes possessing sequential composition, parallel composition, copying, and discarding, subject to certain laws.

Concrete categories of probability satisfy these laws, but so can other categories. Fritz's motivation is precisely to provide a synthetic framework in which probabilistic/statistical concepts can be developed abstractly and then instantiated in discrete, measure-theoretic, Gaussian, and stochastic-process settings. citeturn729673view0turn499123view2

---

# 20. The one axiom we deliberately did **not** impose

Recall the cartesian identity

\[
\Delta_Y\circ f
=
(f\otimes f)\circ\Delta_X.
\tag{20.1}
\]

A Markov category does **not** require (20.1) for arbitrary \(f\).

This omission is crucial.

Take a fair coin

\[
p:I\to B.
\]

Then

\[
\Delta_B\circ p
\]

means:

> generate one random bit and copy it.

Its distribution is

\[
(H,H):\frac12,
\qquad
(T,T):\frac12.
\]

But

\[
(p\otimes p)\circ\Delta_I
\]

means:

> generate two independent random bits.

Its distribution is

\[
(H,H):\frac14,
\quad
(H,T):\frac14,
\quad
(T,H):\frac14,
\quad
(T,T):\frac14.
\]

Hence

\[
\Delta_Bp
\neq
(p\otimes p)\Delta_I.
\]

Fritz singles out precisely this failure: copy is intentionally **not** required to be natural for arbitrary Markov-category morphisms. citeturn261064view1turn499123view2

---

# 21. Deterministic morphisms

The failure of copy naturality gives us a categorical definition of determinism.

## Definition 21.1 — Deterministic morphism

A morphism

\[
f:X\to Y
\]

in a Markov category is **deterministic** if

\[
\boxed{
\Delta_Y\circ f
=
(f\otimes f)\circ\Delta_X.
}
\tag{21.1}
\]

Since every morphism already preserves discarding, this is the only additional equation needed.

This is Fritz's Definition 10.1. citeturn261064view1turn499123view2

---

## Computational reading

For deterministic \(f\),

```python
y = f(x)
(y, y)
```

and

```python
(f(x), f(x))
```

have the same semantics.

For stochastic \(f\), the two evaluations on the right may involve independent random choices.

So equation (21.1) means:

\[
\boxed{
\text{duplicating an invocation adds no new randomness}.
}
\]

That is an unusually elegant characterization of deterministic computation.

---

# 22. Deterministic maps recover cartesian structure

The deterministic morphisms of a Markov category form a subcategory conventionally denoted

\[
\mathcal C_{\mathrm{det}}.
\]

An important theorem is that this deterministic subcategory has cartesian monoidal structure; Fritz highlights this explicitly. citeturn499123view2turn261064view1

We can see why.

Define projections

\[
\pi_1:
X\otimes Y\to X
\]

by

\[
\pi_1
=
\operatorname{id}_X\otimes\epsilon_Y,
\]

and

\[
\pi_2
=
\epsilon_X\otimes\operatorname{id}_Y.
\]

For deterministic maps

\[
f:Z\to X,
\qquad
g:Z\to Y,
\]

define pairing

\[
\langle f,g\rangle
=
(f\otimes g)\circ\Delta_Z.
\tag{22.1}
\]

This is exactly the familiar operation

\[
z\mapsto(f(z),g(z)).
\]

The copy-preservation equation supplies the uniqueness needed for the product universal property.

So the relation is:

\[
\boxed{
\text{Markov category}
\supset
\text{cartesian category of deterministic maps}.
}
\]

You can think of a Markov category as a cartesian world of deterministic computation enriched with additional stochastic processes.

---

# 23. \(\mathbf{FinStoch}\) as the basic example

Let us now assemble everything concretely.

## Objects

Finite sets

\[
X,Y,\ldots
\]

## Morphisms

Stochastic matrices

\[
K(y\mid x).
\]

## Composition

\[
(L\circ K)(z\mid x)
=
\sum_yL(z\mid y)K(y\mid x).
\]

## Tensor product on objects

\[
X\otimes Y=X\times Y.
\]

Notice that the **underlying set** is an ordinary product, even though categorically it is not generally a product object in \(\mathbf{FinStoch}\).

## Tensor of morphisms

\[
(K\otimes L)(y,v\mid x,u)
=
K(y\mid x)L(v\mid u).
\]

## Monoidal unit

\[
I=\{*\}.
\]

## Copy

\[
\Delta_X(x_1,x_2\mid x)
=
\begin{cases}
1,&x_1=x_2=x,\\
0,&\text{otherwise}.
\end{cases}
\]

## Discard

\[
\epsilon_X(*\mid x)=1.
\]

These are exactly the structures described in Fritz's finite stochastic example. citeturn503082view1turn499123view0

---

# 24. States are distributions

There is a nice categorical interpretation of a probability distribution.

## Definition 24.1 — State

In any monoidal category, a morphism

\[
p:I\to X
\]

is called a **state** of \(X\).

In \(\mathbf{FinStoch}\), since \(I\) has one element, a stochastic matrix

\[
I\to X
\]

is exactly a collection

\[
p(x)\ge0
\]

satisfying

\[
\sum_xp(x)=1.
\]

Thus:

\[
\boxed{
\text{states in }\mathbf{FinStoch}
=
\text{finite probability distributions}.
}
\]

---

# 25. Tensor does not mean "uncorrelated"

This distinction is important.

Given states

\[
p:I\to X
\]

and

\[
q:I\to Y,
\]

their tensor

\[
p\otimes q:I\to X\otimes Y
\]

is the independent distribution

\[
(p\otimes q)(x,y)=p(x)q(y).
\]

But an arbitrary state

\[
r:I\to X\otimes Y
\]

does **not** need to factor this way.

It may be correlated.

Therefore

\[
X\otimes Y
\]

means:

> a joint system consisting of an \(X\)-component and a \(Y\)-component.

It does not assert independence.

Independence is a property of particular morphisms.

This is exactly why replacing the categorical product by a monoidal tensor was necessary.

---

# 26. A small executable model

Here is enough Python to model finite Markov-category calculations.

```python
from dataclasses import dataclass
from collections import defaultdict
from typing import Callable, Generic, TypeVar

A = TypeVar("A")
B = TypeVar("B")
C = TypeVar("C")


@dataclass(frozen=True)
class Dist(Generic[A]):
    mass: dict[A, float]

    @staticmethod
    def pure(x: A) -> "Dist[A]":
        return Dist({x: 1.0})

    def bind(
        self,
        kernel: Callable[[A], "Dist[B]"],
    ) -> "Dist[B]":
        out = defaultdict(float)

        for x, px in self.mass.items():
            for y, py_given_x in kernel(x).mass.items():
                out[y] += px * py_given_x

        return Dist(dict(out))
```

A finite Markov kernel is represented by:

```python
Kernel = Callable[[A], Dist[B]]
```

Sequential composition is:

```python
def compose(k, l):
    return lambda x: k(x).bind(l)
```

---

## Tensor

```python
def product_dist(
    p: Dist[A],
    q: Dist[B],
) -> Dist[tuple[A, B]]:
    return Dist({
        (x, y): px * py
        for x, px in p.mass.items()
        for y, py in q.mass.items()
    })


def tensor(k, l):
    def combined(inputs):
        x, y = inputs
        return product_dist(k(x), l(y))

    return combined
```

---

## Deterministic lifting

```python
def deterministic(f):
    return lambda x: Dist.pure(f(x))
```

Copy is therefore:

```python
copy = deterministic(
    lambda x: (x, x)
)
```

and discard:

```python
discard = deterministic(
    lambda x: None
)
```

This tiny library already contains the essential finite Markov-category operations.

---

# 27. Programming example: shared randomness versus repeated execution

Consider a randomized service router.

```python
def route(request: str) -> Dist[str]:
    return Dist({
        "server-A": 0.7,
        "server-B": 0.3,
    })
```

### Run once and share

```python
run_once_and_share = compose(
    route,
    deterministic(lambda server: (server, server)),
)
```

This returns

```python
{
    ("server-A", "server-A"): 0.7,
    ("server-B", "server-B"): 0.3,
}
```

### Copy request and route independently

```python
route_twice = compose(
    deterministic(lambda request: (request, request)),
    tensor(route, route),
)
```

This gives

\[
P(A,A)=0.49,
\]

\[
P(A,B)=0.21,
\]

\[
P(B,A)=0.21,
\]

\[
P(B,B)=0.09.
\]

These are exactly

\[
\Delta\circ\mathrm{route}
\]

and

\[
(\mathrm{route}\otimes\mathrm{route})\circ\Delta.
\]

Their inequality witnesses that `route` is stochastic.

---

# 28. A compiler/data-flow interpretation

This categorical distinction also clarifies **sharing**.

Suppose source code contains:

```python
x = random_bit()
return (x, x)
```

A compiler must not transform it into

```python
return (
    random_bit(),
    random_bit(),
)
```

Those programs have different probability distributions.

For deterministic expressions, common-subexpression duplication may be semantically harmless:

```python
x = hash(data)
return (x, x)
```

versus

```python
return (
    hash(data),
    hash(data),
)
```

assuming `hash` here denotes a pure deterministic function.

Categorically, the distinction is exactly whether

\[
\Delta f=(f\otimes f)\Delta.
\]

Fritz and Liang's work is particularly relevant here: their free gs-monoidal and Markov categories admit combinatorial descriptions using labeled hypergraphs and are explicitly related to **term graphs**, where sharing and copying are first-class structural phenomena. citeturn729673view2turn164149academia1

---

# 29. Connection to probabilistic programming

A probabilistic program can be viewed denotationally as something like

\[
X\to\text{probabilistic }Y.
\]

Operational execution samples one particular \(Y\).

The distinction between copying a sampled value and reevaluating a probabilistic expression is therefore fundamental to language semantics. Modern work on probabilistic programming likewise distinguishes operational execution from denotational probability semantics and studies program equations and compiler transformations in that setting. citeturn164149academia2

Markov categories isolate one especially small compositional fragment of this story:

\[
\text{sequential composition},
\]

\[
\text{parallel composition},
\]

\[
\text{copy},
\]

\[
\text{discard},
\]

plus equations saying how these interact.

---

# 30. Your knowledge of limits: exactly where it fits

There is a useful way to understand the entire development using limits.

A binary product

\[
X\times Y
\]

is a limit of the discrete diagram

\[
X\qquad Y.
\]

Its universal property says that maps

\[
Z\to X\times Y
\]

correspond uniquely to pairs

\[
(Z\to X,\;Z\to Y).
\]

Symbolically,

\[
\operatorname{Hom}(Z,X\times Y)
\cong
\operatorname{Hom}(Z,X)
\times
\operatorname{Hom}(Z,Y).
\tag{30.1}
\]

For probability this is exactly the property we do **not** want.

A joint probabilistic state

\[
Z\to X\otimes Y
\]

contains more information than its two marginals

\[
Z\to X,
\qquad
Z\to Y.
\]

The missing information is dependence/correlation.

So, from the perspective of limits, the key conceptual move is:

\[
\boxed{
\text{retain an object representing juxtaposition}
\quad
\text{but remove the limit universal property}.
}
\]

That object is the monoidal tensor.

This is perhaps the shortest explanation of why Markov categories are monoidal rather than cartesian.

---

# 31. Why equalizers do not enter the basic definition

Equalizers answer a question of the form:

> where do two morphisms \(f,g:X\to Y\) agree?

They may certainly exist in particular categories relevant to probability, but they are not necessary to express the primitive operations that Markov categories are designed to axiomatize.

The basic problem is instead about:

\[
\text{composition},
\qquad
\text{parallel composition},
\qquad
\text{copying},
\qquad
\text{discarding}.
\]

Thus the relevant weakening is primarily

\[
\text{cartesian monoidal}
\rightsquigarrow
\text{symmetric monoidal + explicit copy/discard}.
\]

Limits can be studied on top of this structure, but they are not the starting point.

---

# 32. Optional bridge: probability as a functor

Since you already know functors and natural transformations, there is another route worth knowing—but it should come **after** the structural motivation above.

For finite sets, define

\[
\mathcal D(X)
\]

to be the set of finitely supported probability distributions over \(X\).

Given a function

\[
f:X\to Y,
\]

we obtain

\[
\mathcal D(f):
\mathcal D(X)\to\mathcal D(Y)
\]

by pushing the distribution forward:

\[
\mathcal D(f)(p)(y)
=
\sum_{x:f(x)=y}p(x).
\]

Thus

\[
\mathcal D:\mathbf{Set}\to\mathbf{Set}
\]

is a functor.

---

# 33. The unit natural transformation

There is a natural transformation

\[
\eta:
\operatorname{Id}
\Rightarrow
\mathcal D
\]

whose component is

\[
\eta_X:X\to\mathcal D(X),
\]

\[
x\mapsto\delta_x.
\]

This embeds deterministic values as point distributions.

In code:

```python
def pure(x):
    return {x: 1.0}
```

---

# 34. Flattening probabilistic choice

There is also a transformation

\[
\mu_X:
\mathcal D(\mathcal D(X))
\to
\mathcal D(X)
\]

which averages a distribution of distributions.

For instance,

\[
0.7
\begin{cases}
A:0.9\\
B:0.1
\end{cases}
+
0.3
\begin{cases}
A:0.2\\
B:0.8
\end{cases}
\]

flattens to

\[
A:0.69,
\qquad
B:0.31.
\]

Together,

\[
(\mathcal D,\eta,\mu)
\]

form the finite-distribution monad.

Its Kleisli arrows have the form

\[
X\to\mathcal D(Y),
\]

which are precisely finite stochastic kernels.

More generally, Markov categories can arise from suitable probability monads; the relationship between probability monads, their Kleisli categories, and Markov categories is developed explicitly by Fritz and collaborators. citeturn729673view3turn499123view2

But conceptually:

\[
\boxed{
\text{the monad explains one construction of stochastic morphisms;}
}
\]

whereas

\[
\boxed{
\text{the Markov-category axioms explain their abstract compositional structure.}
}
\]

These are different viewpoints.

---

# 35. A useful hierarchy

You can now organize the ideas as follows.

\[
\textbf{category}
\]

gives sequential composition.

\[
X\xrightarrow fY\xrightarrow gZ.
\]

A

\[
\textbf{symmetric monoidal category}
\]

adds parallel composition.

\[
f\otimes g.
\]

A

\[
\textbf{copy/discard structure}
\]

adds explicit

\[
\Delta_X:X\to X\otimes X
\]

and

\[
\epsilon_X:X\to I.
\]

A

\[
\textbf{Markov category}
\]

requires the discard operation to be natural, equivalently requiring the monoidal unit to be terminal.

Finally, inside a Markov category,

\[
\textbf{deterministic morphisms}
\]

are precisely those satisfying

\[
\Delta_Yf=(f\otimes f)\Delta_X.
\]

These deterministic maps recover a cartesian monoidal subcategory. citeturn499123view2turn261064view1

---

# 36. The conceptual definition in one sentence

A Markov category is:

> a symmetric monoidal category in which values may be copied and discarded coherently, every process may be discarded without observable effect, but arbitrary processes need not commute with copying.

Or algebraically:

\[
\boxed{
\begin{aligned}
&\text{parallel composition} && \otimes\\
&\text{copy} && \Delta_X:X\to X\otimes X\\
&\text{discard} && \epsilon_X:X\to I\\
&\text{normalization} &&
\epsilon_Yf=\epsilon_X\\
&\text{but generally} &&
\Delta_Yf\neq(f\otimes f)\Delta_X.
\end{aligned}
}
\]

The last inequality is where genuine stochasticity becomes possible.

---

# Exercises

## Exercise 1 — Constructing the diagonal

Let \(\mathcal C\) have binary products.

Using only the universal property of \(X\times X\), construct

\[
\Delta_X:X\to X\times X
\]

and prove that

\[
\pi_1\Delta_X
=
\pi_2\Delta_X
=
\operatorname{id}_X.
\]

Then express the same construction as a program on product types.

---

## Exercise 2 — Naturality of copying

For an arbitrary morphism

\[
f:X\to Y
\]

in a category with finite products, prove

\[
\Delta_Yf
=
(f\times f)\Delta_X
\]

using only the uniqueness clause in the product universal property.

Do not reason elementwise.

---

## Exercise 3 — Copy/discard equations

Prove categorically that

\[
(!_X\times\operatorname{id}_X)\Delta_X
=
\operatorname{id}_X.
\]

Then prove coassociativity:

\[
(\Delta_X\times\operatorname{id}_X)\Delta_X
=
(\operatorname{id}_X\times\Delta_X)\Delta_X.
\]

Again, use product universal properties rather than elements.

---

## Exercise 4 — A stochastic matrix

Let

\[
X=\{a,b\},
\qquad
Y=\{0,1\}
\]

and define

\[
K(0\mid a)=0.8,
\qquad
K(1\mid a)=0.2,
\]

\[
K(0\mid b)=0.3,
\qquad
K(1\mid b)=0.7.
\]

Let

\[
L:Y\to\{u,v\}
\]

be

\[
L(u\mid0)=0.9,
\qquad
L(v\mid0)=0.1,
\]

\[
L(u\mid1)=0.4,
\qquad
L(v\mid1)=0.6.
\]

Compute the complete stochastic matrix

\[
L\circ K.
\]

Implement the computation in Python.

---

## Exercise 5 — Associativity in \(\mathbf{FinStoch}\)

Write three finite stochastic matrices \(K,L,M\).

Show directly that

\[
M\circ(L\circ K)
=
(M\circ L)\circ K.
\]

Explain why this is essentially associativity of finite summation/matrix multiplication.

---

## Exercise 6 — Products fail

Let

\[
B=\{0,1\}
\]

and let \(p:I\to B\) be Bernoulli\((1/2)\).

Construct two distinct states

\[
r,s:I\to B\times B
\]

having identical first and second marginals.

Use this to show that \(B\times B\), with the usual projections, cannot satisfy the categorical product universal property in \(\mathbf{FinStoch}\).

Identify exactly which part of the universal property fails.

---

## Exercise 7 — Tensor normalization

Let

\[
K:X\to Y,
\qquad
L:A\to B
\]

be stochastic matrices.

Define

\[
(K\otimes L)(y,b\mid x,a)
=
K(y\mid x)L(b\mid a).
\]

Prove that \(K\otimes L\) is again stochastic by showing

\[
\sum_{y,b}
(K\otimes L)(y,b\mid x,a)=1.
\]

---

## Exercise 8 — Copy once versus sample twice

Let

\[
p:I\to\{0,1\}
\]

be Bernoulli\((q)\).

Compute explicitly the two joint states

\[
\Delta p
\]

and

\[
p\otimes p.
\]

For which values of \(q\) are they equal?

Interpret your result computationally.

---

## Exercise 9 — Characterizing deterministic maps in \(\mathbf{FinStoch}\)

Let

\[
K:X\to Y
\]

be stochastic.

Assume

\[
\Delta_YK
=
(K\otimes K)\Delta_X.
\]

For fixed \(x\in X\), show that

\[
K(y\mid x)^2=K(y\mid x).
\]

Conclude that

\[
K(y\mid x)\in\{0,1\}.
\]

Since the row sums to \(1\), prove that each \(x\) has exactly one \(y\) with probability \(1\).

Conclude that deterministic morphisms in \(\mathbf{FinStoch}\) correspond exactly to ordinary functions.

---

## Exercise 10 — Randomized load balancing

A router chooses server \(A\) with probability \(0.7\) and \(B\) with probability \(0.3\).

Compare these two implementations:

```python
server = route(request)
return server, server
```

and

```python
return route(request), route(request)
```

Compute the joint distribution in each case.

What is the probability that both returned server names agree?

---

## Exercise 11 — Shared computation in a compiler

Consider a small expression language containing

```text
RandomBit
Pair(e1, e2)
Let(x, e1, e2)
```

Give probabilistic semantics to the programs

```text
let x = RandomBit in (x, x)
```

and

```text
(RandomBit, RandomBit).
```

Explain the distinction using

\[
\Delta\circ p
\]

and

\[
(p\otimes p)\circ\Delta.
\]

What optimization would incorrectly identify the two programs?

---

## Exercise 12 — Deriving projections in a Markov category

Given objects \(X,Y\), define

\[
\pi_X
:=
\operatorname{id}_X\otimes\epsilon_Y
:
X\otimes Y\to X
\]

and

\[
\pi_Y
:=
\epsilon_X\otimes\operatorname{id}_Y
:
X\otimes Y\to Y.
\]

For deterministic

\[
f:Z\to X,
\qquad
g:Z\to Y,
\]

define

\[
\langle f,g\rangle
=
(f\otimes g)\Delta_Z.
\]

Prove

\[
\pi_X\langle f,g\rangle=f
\]

and

\[
\pi_Y\langle f,g\rangle=g.
\]

This is the existence half of the product property inside \(\mathcal C_{\mathrm{det}}\).

---

## Exercise 13 — Product uniqueness and deterministic maps

Continue Exercise 12.

Suppose

\[
h:Z\to X\otimes Y
\]

is deterministic and satisfies

\[
\pi_Xh=f,
\qquad
\pi_Yh=g.
\]

Use copy preservation of \(h\) to prove

\[
h=(f\otimes g)\Delta_Z.
\]

You have thereby derived the full product universal property for deterministic morphisms.

---

## Exercise 14 — Failure and subprobabilities

Suppose instead of requiring

\[
\sum_yK(y\mid x)=1
\]

we allow

\[
\sum_yK(y\mid x)\le1.
\]

Interpret the missing probability as program failure or nontermination.

Show that generally

\[
\epsilon_YK\neq\epsilon_X.
\]

Which Markov-category axiom has failed?

This is a useful first hint toward categorical semantics for partial or failing probabilistic computations.

---

## Exercise 15 — A probabilistic data-flow graph

Consider three program components

\[
A:X\to Y,
\qquad
B:Y\to Z,
\qquad
C:Y\to W.
\]

You want to run \(A\) once and then feed the **same resulting \(Y\)** into \(B\) and \(C\).

Write the composite categorically.

Then write the different composite that first duplicates the input \(X\) and independently executes \(A\) twice.

Under what condition on \(A\) are the two equal?

---

## Exercise 16 — Retrieval systems

Let

\[
R:Q\to D
\]

denote a randomized retriever.

Compare

\[
Q
\xrightarrow{R}
D
\xrightarrow{\Delta_D}
D\otimes D
\]

with

\[
Q
\xrightarrow{\Delta_Q}
Q\otimes Q
\xrightarrow{R\otimes R}
D\otimes D.
\]

Interpret both operationally for a search system.

In the first system, what correlation exists between the two retrieved results?

In the second?

Under what categorical condition on \(R\) would the distinction disappear?

---

## Exercise 17 — Monad implementation

Implement:

```python
class Dist:
    ...

def pure(x):
    ...

def bind(dist, kernel):
    ...
```

Then define

```python
def compose(k, l):
    return lambda x: bind(k(x), l)
```

Test experimentally on finite distributions that

```python
compose(compose(f, g), h)
```

and

```python
compose(f, compose(g, h))
```

produce the same distributions.

Relate your implementation to stochastic-matrix multiplication.

---

## Exercise 18 — Correlation is the missing information

Let \(X=Y=\{0,1\}\).

Find all joint distributions

\[
p:X\times Y\to[0,1]
\]

whose two marginals are both uniform and which satisfy the symmetry condition

\[
p(0,1)=p(1,0).
\]

Show that there is an entire one-parameter family.

Explain how this illustrates, quantitatively, why

\[
X\otimes Y
\]

cannot generally be a categorical product in stochastic computation.

---

# Primary references

The central reference is Tobias Fritz, **“A Synthetic Approach to Markov Kernels, Conditional Independence and Theorems on Sufficient Statistics.”** Definition 2.1 gives the Markov-category axioms, Example 2.5 gives \(\mathbf{FinStoch}\), and Section 10 develops deterministic morphisms. citeturn729673view0turn261064view0turn261064view1

Cho and Jacobs, **“Disintegration and Bayesian Inversion via String Diagrams,”** is an important precursor using copy/discard categorical structure to formulate conditional probability and Bayesian inversion. citeturn729673view1turn821434search0

Fritz, Gonda, Perrone, and Rischel, **“Representable Markov Categories and Comparison of Statistical Experiments in Categorical Probability,”** develops the relationship between Markov categories and probability monads/Kleisli categories. citeturn729673view3

Fritz and Liang, **“Free gs-monoidal Categories and Free Markov Categories,”** is especially relevant from a CS perspective because it connects free copy/discard structures with labeled hypergraphs and term graphs as concrete combinatorial representations. citeturn729673view2

Fong, **“Causal Theories: A Categorical Perspective on Bayesian Networks,”** is useful for seeing monoidal categorical structure applied directly to Bayesian networks and information flow. citeturn164149academia0

Staton, Yang, Heunen, Kammar, and Wood, **“Semantics for Probabilistic Programming: Higher-Order Functions, Continuous Distributions, and Soft Constraints,”** provides broader context for why compositional denotational semantics and operational probabilistic execution matter in programming-language theory. citeturn164149academia2

