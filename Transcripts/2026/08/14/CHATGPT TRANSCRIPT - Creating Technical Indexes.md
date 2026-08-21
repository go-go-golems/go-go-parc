# Creating Technical Indexes

- URL: https://chatgpt.com/c/6a7fa426-ac8c-83ea-9867-97410dea896b
- Created: 2026-08-14T23:26:54.935Z

---

> how to write a good mathematical / computer science textbook index (or just in general, how does one create great indexes / glossaries for complex technical topics books)

A great technical index is not a list of words that occur in the book. It is a **map of the book’s conceptual structure**, written from the perspective of a reader who does not yet know where the answer is.

For mathematics and computer science especially, the central question is:

> **What might a reader think to look up, and where would I want them to land?**

That principle produces much better indexes than mechanically extracting terminology.

## 1. Index and glossary solve different problems

An **index** answers:

> “Where in this book can I learn about or find this thing?”

A **glossary** answers:

> “What does this thing mean?”

So, for example:

**Glossary**

> **topological ordering** — A linear ordering of the vertices of a directed acyclic graph such that every directed edge $u\to v$ places $u$ before $v$.

**Index**

> topological ordering, 184–190  
>   algorithm for, 186–188  
>   cycle detection and, 190  
>   DAGs and, 184–185  
>   uniqueness of, 189  
>   see also directed acyclic graphs

A glossary is miniature reference documentation. An index is navigation.

---

# 2. Think in concepts, not strings

Suppose your book contains:

> “Every finite-dimensional vector space admits a basis.”

A naïve automatic index might extract:

- finite-dimensional
- vector space
- basis

A human-quality index asks what somebody might actually search for:

- basis
  - existence of
- finite-dimensional vector spaces
  - bases of
- vector spaces
  - basis existence theorem

Possibly also:

- existence
  - of bases

The important distinction is that **the index entry need not literally occur on the page**.

You are indexing ideas.

This becomes especially important in CS. A section might explain:

```text
memoization avoids recomputing previously evaluated subproblems
```

Useful entries could include:

- memoization
- caching, memoization as
- dynamic programming
  - memoization
- repeated computation, avoiding

Even if “avoiding repeated computation” never appears as a formal term.

---

# 3. Index what a reader might plausibly want to retrieve

For a technical textbook, I would consider at least these categories.

### Concepts

- compactness
- recursion
- aliasing
- covariance
- eigenvalue
- synchronization

These are the core of the index.

### Named objects

- AVL tree
- Fourier transform
- Lebesgue measure
- Turing machine
- Bellman–Ford algorithm

### Operations and procedures

Readers often remember what they want to **do**, rather than the noun for it:

- matrices
  - diagonalizing
  - inverting
  - multiplying
- graphs
  - traversing
  - coloring
- functions
  - composing
  - differentiating
- trees
  - balancing
  - traversing

This is extremely useful.

### Properties

- convexity
- differentiability
- immutability
- stability
- termination

### Theorems, lemmas, laws, algorithms

Especially named ones:

- Banach fixed-point theorem
- Bayes’ theorem
- Chinese remainder theorem
- Dijkstra’s algorithm
- master theorem

But also important unnamed results.

### Examples and canonical problems

- dining philosophers problem
- eight queens problem
- halting problem
- traveling-salesperson problem

### Failure modes and pathological cases

These are often under-indexed, even though readers search for them constantly:

- deadlock
- division by zero
- floating-point error
- integer overflow
- race condition
- stack overflow
- undefined behavior

Likewise in mathematics:

- counterexamples
- degeneracy
- divergence
- failure of uniqueness
- singularities

### Applications

If the book says why something matters, index that connection:

- eigenvectors
  - principal-component analysis
- hashing
  - symbol tables
- Markov chains
  - PageRank

### People

Usually only when substantively discussed:

- Dijkstra, Edsger
- Gödel, Kurt
- Turing, Alan

Do not index every person merely cited in a bibliography.

### Notation

Technical books need special consideration here. Readers frequently think:

> “What did $\preceq$ mean again?”

A separate **Index of Symbols / Notation** is often much better than trying to mix symbols into the ordinary alphabetic index.

For example:

| Symbol | Meaning | Page |
|---|---|---:|
| $A^\top$ | matrix transpose | 42 |
| $\lVert x\rVert$ | norm | 73 |
| $O(f(n))$ | asymptotic upper bound | 211 |
| $\Sigma^*$ | set of finite strings | 318 |

---

# 4. The most important quality: multiple access paths

Readers rarely remember your terminology exactly.

Suppose you call something **lexicographic ordering**.

Readers may search:

- dictionary order
- lexicographic order
- string comparison

A good index accommodates that:

> dictionary order. *See* lexicographic ordering  
> lexicographic ordering, 91–94  
>   of strings, 92  
> string comparison  
>   lexicographic, 92–93

Similarly:

> breadth-first search, 243–249  
> BFS. *See* breadth-first search  
> graph traversal  
>   breadth-first, 243–249

Cross-references are one of the strongest signals that an index was actually designed rather than generated.

---

# 5. Prefer subentries over long clouds of page numbers

Bad:

> recursion, 19, 23, 37, 42, 48, 51, 64, 88, 91, 92, 93, 97, 112, 145

That tells the reader almost nothing.

Better:

> recursion, 37–52  
>   base case, 39–40  
>   binary trees and, 145–147  
>   call stack, 42–45  
>   definition, 37  
>   infinite, 48–49  
>   mutual, 50–51  
>   versus iteration, 46–47

An index should compress information intelligently.

A useful rule is:

> **If an entry has more than roughly 5–7 undifferentiated locators, consider subentries.**

Not an absolute law, but a very good warning sign.

---

# 6. Subentries should answer meaningful questions

Poor subentries often arise from grammatical decomposition:

> graph  
>   algorithm  
>   example  
>   property  
>   theorem

Those tell you little.

Better:

> graphs  
>   adjacency-list representation  
>   adjacency-matrix representation  
>   connected  
>   directed  
>   shortest paths in  
>   traversal of  
>   weighted

The index should capture conceptual relationships.

For math:

> integrals  
>   change of variables in  
>   improper  
>   line  
>   numerical approximation of  
>   Riemann  
>   surface

rather than:

> integrals  
>   examples of  
>   formula for  
>   important  
>   theorem about

---

# 7. Index relationships, not only entities

Technical understanding consists largely of relationships.

Consider:

> dynamic programming and shortest paths

You probably want indexing under both:

> dynamic programming  
>   shortest paths, 271–278

and:

> shortest paths  
>   dynamic programming approach, 271–278

Likewise:

> compactness  
>   continuity and, 183–186

and perhaps:

> continuous functions  
>   on compact sets, 183–186

This is one of the things automatic keyword indexing does very poorly.

---

# 8. Distinguish a passing mention from substantive treatment

This is crucial.

If page 127 merely says:

> “Unlike merge sort, quicksort can…”

you probably don't want page 127 indexed under **merge sort** unless that comparison is genuinely useful.

Index a page when the reader who follows the reference will feel:

> “Yes, this page actually tells me something about what I searched for.”

An excellent test is:

### The disappointed-reader test

Imagine someone deliberately looked up `monads → error handling` and turned to the listed page.

Would they find enough discussion there to justify your sending them?

If not, remove the locator.

This single rule dramatically improves indexes.

---

# 9. Give special treatment to definitions

In textbooks, readers often specifically want the canonical definition.

You can use typographic locator conventions if your publishing system supports them—for example, bold page numbers for definitions—but don't make the convention too clever.

Alternatively:

> monoid  
>   definition, 117  
>   examples, 118–120  
>   homomorphisms of, 126–128

This is often clearer.

For mathematical books, also consider distinguishing:

- definition
- theorem
- proof
- example
- counterexample

but only when genuinely useful.

---

# 10. Glossaries should be aggressively canonical

A technical glossary should not try to reproduce the textbook.

A strong glossary entry usually contains:

1. **canonical term**
2. concise definition
3. notation, when relevant
4. aliases
5. one important qualification or distinction
6. cross-reference

For example:

> **stable sorting algorithm.** A sorting algorithm that preserves the relative order of elements having equal keys. Merge sort can be implemented stably; ordinary heapsort generally is not stable. *See also* sorting algorithm.

For mathematics:

> **injective function (injection, one-to-one function).** A function $f:A\to B$ such that $f(x)=f(y)$ implies $x=y$. Equivalently, distinct inputs have distinct outputs. *See also* bijection; surjection.

Notice that the glossary captures synonyms immediately.

---

# 11. Do not let the glossary become recursive nonsense

Bad:

> **Functor:** An object satisfying the functor laws.

Then:

> **Functor laws:** Laws that functors satisfy.

Technical glossaries are especially vulnerable to circular definitions.

Instead, definitions should eventually bottom out in terminology that the intended reader already knows.

A useful mental model is a dependency graph:

```text
semigroup
    ↓
monoid
    ↓
group
    ↓
abelian group
```

Later concepts can depend on earlier concepts.

If A's definition requires B and B's definition requires A, something probably needs rewriting.

---

# 12. Decide your vocabulary policy early

Technical subjects have lots of aliases.

For example:

- one-to-one / injective
- onto / surjective
- hash map / hash table / dictionary
- vertex / node
- arc / edge
- mutex / mutual-exclusion lock
- priority queue / heap — related but **not identical**

Establish a canonical term.

Then index alternatives:

> one-to-one function. *See* injective function

and glossary aliases:

> **injective function** *(also one-to-one function)* …

But be careful with things that are merely related rather than synonymous.

Bad:

> heap. *See* priority queue

A heap is one possible implementation of a priority queue; they aren't identical.

Better:

> heaps  
>   priority queues implemented with, 156–164  
>
> priority queues, 151–165  
>   binary heaps, 156–164

Precision matters.

---

# 13. Index at the level of abstraction readers use

One reason technical indexes fail is that their granularity is inconsistent.

Consider a chapter about databases.

Too broad:

> database, 1–340

Too narrow:

> B-tree internal node split after insertion, 184

unless that particular procedure is something readers are likely to search for.

Usually the useful middle level is:

> B-trees  
>   deletion from  
>   insertion into  
>   node splitting  
>   searching  
>   time complexity

Think of the index as exposing the book's **API**.

You don't expose every implementation detail. You expose useful handles.

---

# 14. Mathematics needs some special indexing habits

Math readers frequently search for:

### Objects

- fields
- groups
- manifolds
- matrices

### Properties

- compact
- connected
- continuous
- invertible
- measurable
- symmetric

### Operations

- completion
- differentiation
- factorization
- integration

### Named results

- Cayley–Hamilton theorem
- fundamental theorem of calculus

### Hypotheses and boundary conditions

These are unusually important.

Suppose you prove:

> continuous functions on compact sets attain their maximum.

Useful indexing includes:

> extreme-value theorem  
> compactness  
>   extrema of continuous functions and  
> continuous functions  
>   extrema on compact sets

because readers may remember the **conclusion**, not the theorem's official name.

### Counterexamples

Extremely valuable:

> continuity  
>   failure of uniform continuity, counterexample  
>
> differentiability  
>   does not imply continuous derivative

Math books should index memorable counterexamples almost as carefully as theorems.

---

# 15. Computer science needs some different habits

CS readers frequently search according to:

### Task

- searching
- sorting
- parsing
- scheduling
- serialization

### Data structure

- arrays
- hash tables
- linked lists
- tries

### Complexity

- amortized analysis
- exponential time
- $O(n \log n)$

### Implementation issue

- memory allocation
- recursion depth
- concurrency
- overflow

### Failure mode

- deadlock
- data race
- dangling pointer
- starvation

### Design tradeoff

These make excellent index entries:

> arrays  
>   versus linked lists  
>
> adjacency matrices  
>   versus adjacency lists  
>
> recursion  
>   versus iteration

Readers often return to textbooks specifically to recover these comparisons.

---

# 16. Treat examples as first-class intellectual objects

Suppose your algorithms book explains dynamic programming using:

- Fibonacci numbers
- edit distance
- knapsack
- longest common subsequence

Index all of those.

But also reverse-index them:

> dynamic programming  
>   edit distance  
>   knapsack problem  
>   longest common subsequence

and:

> edit distance  
>   dynamic programming solution

Examples are often how readers remember the concept.

---

# 17. A useful hierarchy is usually only 2 levels deep

You generally want:

```text
trees
    binary
    balanced
    traversing
```

Occasionally:

```text
trees
    binary
        traversal of
```

But indexes like this become unpleasant:

```text
algorithms
    graph
        traversal
            depth-first
                recursive implementation of
```

A back-of-book index is not an ontology browser.

Flatten aggressively:

> depth-first search  
>   recursive implementation  
>
> graph traversal  
>   depth-first

Two levels handles most cases elegantly.

---

# 18. `See` and `see also` have different meanings

Use:

### `See`

when the entry contains no useful locators because another term is preferred.

> DFS. *See* depth-first search

### `See also`

when both terms have useful entries and the second offers related material.

> depth-first search, 122–129  
>   …  
>   *see also* graph traversal; topological sorting

Overusing cross-references creates clutter, but well-chosen ones reveal the conceptual network of the book.

---

# 19. Don't over-index

A huge index is not automatically good.

Indexing every technical noun produces something resembling a search-engine concordance:

> Boolean, 2, 5, 7, 12, 13, 17, 19, 22, 23, 24, 31...

That is almost useless.

A smaller curated index can be far more powerful.

The objective is approximately:

$$
\text{index quality}
\neq
\text{number of entries}
$$

More like:

$$
\text{index quality}
\approx
\frac{\text{useful retrieval paths}}
{\text{reader effort}}
$$

---

# 20. But don't under-index terminology introduced locally

Authors have the opposite blind spot: because they know their book perfectly, they think:

> “Obviously that is in Chapter 7.”

The reader doesn't.

Every important coined term, technical phrase, named abstraction, algorithm, theorem, or repeated distinction deserves consideration.

A particularly good technique is to ask after every section:

> **What are the 3–10 questions for which this section is an answer?**

Those questions often tell you exactly what belongs in the index.

For a section explaining AVL rotations:

- AVL trees
- balancing
- binary search trees, balancing
- rotations
- left rotation
- right rotation

That's much better than merely extracting every italicized vocabulary term.

---

# 21. Build the index while writing—but finalize it after pagination

The best workflow is two-stage.

During writing, attach semantic markers to important passages:

```text
INDEX: dynamic programming
INDEX: memoization
INDEX: recursion--avoiding repeated computation
INDEX: Fibonacci numbers--dynamic programming
```

Don't worry yet about page numbers.

After the manuscript is essentially final:

1. generate the provisional index,
2. inspect every entry,
3. merge synonyms,
4. create subentries,
5. remove trivial mentions,
6. add missing alternative access points,
7. add cross-references,
8. check page ranges,
9. reread the index by itself.

That last step is surprisingly powerful.

The index should almost look like a **compressed conceptual outline of the book**.

---

# 22. Use the index itself as a diagnostic tool

If your index says:

> closures, 91  
> continuations, 92  
> environments, 93  
> lexical scope, 94

you may realize the chapter actually treats these concepts extensively and deserves richer indexing.

Or you may discover inconsistent vocabulary:

> mutex  
> mutual exclusion  
> mutual-exclusion lock  
> lock

That may reveal inconsistency in the manuscript itself.

A great index frequently exposes flaws in:

- terminology
- chapter organization
- definitions
- cross-references
- notation

So indexing isn't merely publishing cleanup. It can improve the book.

---

# 23. A concrete example

Imagine a section:

## 8.3 Dijkstra's Algorithm

It introduces the shortest-path problem, explains nonnegative edge weights, uses a priority queue, gives pseudocode, proves correctness, analyzes $O((V+E)\log V)$, and shows why negative edges break the algorithm.

A weak index:

> Dijkstra's algorithm, 184–191  
> graph, 184  
> priority queue, 186  
> shortest path, 184

A strong one might be:

> **Dijkstra's algorithm**, 184–191  
>   correctness, 188–189  
>   negative edge weights and, 190–191  
>   priority queue in, 186–187  
>   pseudocode, 187  
>   running time, 189–190  
>
> **negative edge weights**  
>   Dijkstra's algorithm and, 190–191  
>
> **priority queues**  
>   in Dijkstra's algorithm, 186–187  
>
> **shortest-path problem**, 181–198  
>   Dijkstra's algorithm, 184–191  
>   negative edge weights, 190–194  
>   single-source, 184  
>
> **single-source shortest paths**, 184–198  
>   *see also* Dijkstra's algorithm  
>
> **time complexity**  
>   of Dijkstra's algorithm, 189–190

Now someone can arrive at the material from **six different memories of what they were looking for**.

That is what you want.

---

# 24. A good glossary benefits from a different structure

For a large technical book, I would often maintain structured glossary data internally along roughly these lines:

```text
canonical term
aliases
short definition
notation
prerequisite concepts
contrasts
see also
introduced at
```

For example:

```text
canonical: directed acyclic graph
aliases:
    - DAG

definition:
    A directed graph containing no directed cycles.

contrasts:
    - cyclic directed graph

see also:
    - topological ordering
    - directed graph

introduced:
    Chapter 6
```

This data can generate:

- the glossary
- index cross-references
- hover definitions in an ebook
- vocabulary lists
- metadata for a website

For a sophisticated technical project, maintaining a **concept database** behind the manuscript can be extremely worthwhile.

---

# 25. One useful distinction: glossary vs notation table vs index

For a serious math/CS textbook I often prefer **three separate mechanisms**:

**Glossary**
: canonical meanings of terminology

**Notation / symbol table**
: what symbols mean

**Index**
: where concepts are discussed

Trying to make one mechanism perform all three jobs usually makes it worse.

---

# 26. Common failure modes

The indexes I find least useful tend to suffer from some combination of:

- indexing words instead of ideas;
- indexing every occurrence;
- hundreds of bare page-number lists;
- missing synonyms;
- no inversion of relationships;
- no entries for reader tasks;
- no entries for failure cases;
- no entries for important examples;
- excessively deep hierarchy;
- confusing related concepts with synonyms;
- indexing definitions but not applications;
- indexing theorem names but not theorem conclusions;
- failing to index comparisons such as “X versus Y”;
- sending readers to pages containing only passing mentions;
- treating auto-generated keyword extraction as a finished index.

LLMs and NLP tools can help produce **candidate entries**, but I would not trust an automated system to decide the final conceptual access structure without human review.

---

# 27. A useful practical test

Once you have a draft index, invent 30–50 realistic reader situations.

For example:

> “I remember there was an algorithm that computes shortest paths, but it doesn't work with negative weights.”

Can they find it?

> “Where was the proof that continuous functions attain maxima?”

Can they find it without remembering “extreme-value theorem”?

> “What was the difference between a shallow copy and a deep copy?”

Can they find the comparison?

> “What does `*` mean on a language alphabet?”

Can they find the notation?

> “Where did the book explain why hash tables sometimes become slow?”

Can they reach collision handling / worst-case complexity?

This is essentially **usability testing for the index**.

A great index works with imperfect human memory.

---

## The principle I would optimize for

If I had to compress the whole craft into one rule:

> **Index the book according to how readers might remember its knowledge, not according to how the author happened to phrase it.**

And for a math/CS textbook, I'd make the index particularly rich in **concept ↔ concept relationships, operations, theorem conclusions, examples, counterexamples, implementations, comparisons, failure modes, and alternate terminology**.

A genuinely excellent technical index can almost be read independently as a terse conceptual map of the discipline.

