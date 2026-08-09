---
title: "A Semantics-First Reconstruction of a Structural Mathematics Editor"
subtitle: "Operational Semantics, Denotational Semantics, Type Theory, and Category-Theoretic Design"
author: "Technical monograph prepared from the supplied source artifact"
date: "6 August 2026"
documentclass: book
classoption:
  - oneside
  - openany
papersize: letter
fontsize: 11pt
geometry:
  - top=1in
  - bottom=1in
  - left=1.05in
  - right=1.05in
linestretch: 1.12
toc: true
toc-depth: 3
numbersections: true
colorlinks: true
linkcolor: blue
urlcolor: blue
citecolor: blue
mainfont: "Noto Serif"
sansfont: "Inter"
monofont: "DejaVu Sans Mono"
mathfont: "STIX Math"
header-includes:
  - |
    \usepackage{microtype}
    \usepackage{booktabs}
    \usepackage{longtable}
    \usepackage{array}
    \usepackage{mathtools}
    \usepackage{amssymb}
    \usepackage{amscd}
    \usepackage{stmaryrd}
    \usepackage{fvextra}
    \usepackage{fancyhdr}
    \usepackage{enumitem}
    \usepackage{xcolor}
    \usepackage{caption}
    \usepackage{float}
    \usepackage{graphicx}
    \usepackage{xurl}
    \definecolor{MidnightBlue}{HTML}{17365D}
    \definecolor{CodeBg}{HTML}{F4F6F8}
    \setlist{nosep}
    \fvset{breaklines=true,breakanywhere=true,fontsize=\small}
    \pagestyle{fancy}
    \fancyhf{}
    \fancyhead[R]{\small\thepage}
    \fancyhead[L]{\small\nouppercase{\rightmark}}
    \setlength{\headheight}{14pt}
    \captionsetup{font=small,labelfont=bf}
    \newcommand{\Valid}{\mathsf{Valid}}
    \newcommand{\resolve}{\mathsf{resolve}}
    \newcommand{\plug}{\mathsf{plug}}
    \newcommand{\focus}{\mathsf{focus}}
    \newcommand{\cata}{\mathsf{cata}}
    \newcommand{\Result}{\mathsf{Result}}
    \newcommand{\Ok}{\mathsf{Ok}}
    \newcommand{\Err}{\mathsf{Err}}
---

# Abstract {.unnumbered}

The supplied program is a compact structural mathematics keyboard. Its central design claim is unusually good: the document is an abstract syntax tree, the editor renders that tree directly, textual formats are generated from the same tree, and the cursor is represented by a path into the structure plus an offset. Those choices are the correct starting point for a serious structure editor. The implementation, however, leaves most of their mathematical content implicit. Node shapes are unchecked runtime objects, paths are partial addresses, recursive slots may be empty, scripts are postfix siblings rather than owners of their bases, code-generation backends silently lose information, and editing transitions are interleaved with component state and mutable history.

This monograph first decomposes the program into its latent abstract patterns. The syntax is identified as an inductive, strictly positive datatype; code generators are recognized as algebras and their recursive traversals as catamorphisms; cursor contexts are related to Huet zippers and derivatives of datatypes; tree access is formulated as a partial lens; edit commands are given a deterministic operational semantics; persistence and undo are separated into checked codecs and timeline zippers; and object-level mathematical meaning is distinguished from presentation-level rendering.

The program is then rebuilt around four explicit invariants: well-formed syntax, a valid focused path, a bounded anchor/head selection, and globally unique hole identities. Recursive children are non-empty slots whose blank state is represented by an explicit hole. Scripts structurally own their bases and at least one attachment. Accents wrap an existing selection or prior expression. Annotated arrows receive a dedicated constructor. Symbols are stored by semantic identity rather than by LaTeX spelling. Every editor command is interpreted by a pure reducer

\[
  \mathsf{reduce}: S \times C \longrightarrow \Result(S,E),
\]

and every successful transition is required to preserve validity. Backend generation is expressed once through a generic syntax algebra. The reconstructed TypeScript implementation approximates dependent typing with discriminated unions, non-empty tuples, smart constructors, checked path resolution, and explicit `Result` values.

The resulting system is not presented as a complete proof assistant or as a parser for arbitrary mathematics. A visual formula alone does not determine a unique mathematical denotation. Accordingly, the thesis separates a presentation-neutral mathematical intermediate representation from a later, signature-dependent elaboration and typing phase. This distinction makes the claims precise: the editor guarantees structural well-formedness and coherent rendering; mathematical type correctness requires an external theory and context.

Executable checks accompany the mathematical development. They exercise the three lens laws, reducer preservation under deterministic randomized command sequences, backend totality, fresh-hole allocation, structural ownership of scripts and accents, non-empty slot preservation, undo/redo, and persistence round trips. The result is a complete design account, a runnable reconstruction, and a foundation suitable for later mechanization in Lean, Agda, Coq, or a dependently typed implementation language.

# Preface and scope {.unnumbered}

This work uses the supplied source artifact as its primary object of study. Descriptions of the original behavior are grounded in that artifact. The semantic theory, categorical analysis, and reconstructed implementation are additional work introduced here. Where the source does not support a claim, the text says so; in particular, it does not infer object-level mathematical meaning from glyphs that only encode notation.

The word *sound* is used in three separate senses, which must not be conflated:

1. **Structural soundness:** every stored editor tree satisfies its datatype invariants.
2. **Transition soundness:** every successful edit preserves those invariants.
3. **Mathematical soundness:** a typed mathematical term denotes an object in a model of a specified theory.

The reconstruction establishes the first by design and validator, argues the second by a preservation theorem and executable tests, and provides an interface for the third without pretending that an untyped notation editor can establish it by itself.

The executable code is intentionally dependency-free at runtime. TypeScript is used because it is close to the original implementation environment, not because its type system can express every desired invariant. The thesis therefore presents an idealized dependent formulation and then explains the disciplined approximation implemented in TypeScript.

# Reading guide {.unnumbered}

Chapters 1 and 2 state the problem and audit the source. Chapter 3 introduces the semantic tools. Chapters 4 through 8 give the mathematical reconstruction: inductive syntax, zippers and lenses, operational semantics, denotational semantics, type theory, and category theory. Chapters 9 and 10 present the software architecture and implementation. Chapter 11 reports executable verification. Chapter 12 works through representative editing scenarios. Chapter 13 states limitations and a route to full mechanization. The appendices collect formal rules, a source-to-model map, exercises, and reproduction instructions.

# Notation {.unnumbered}

| Notation | Meaning |
|---|---|
| $X^*$ | finite lists over $X$ |
| $X^+$ | non-empty finite lists over $X$ |
| $1+X$ | an optional $X$ |
| $\mu F$ | the carrier of an initial $F$-algebra |
| $C[-]$ | a one-hole context |
| $R[i:j)$ | the half-open slice of a sequence |
| $u\mathbin{+\!+}v$ | sequence concatenation |
| $\Result(X,E)$ | either $\Ok(x)$ or $\Err(e)$ |
| $\llbracket t\rrbracket_\rho$ | denotation of $t$ under interpretation $\rho$ |
| $\Gamma\vdash t:\tau$ | $t$ has type $\tau$ in context $\Gamma$ |

\newpage


# The problem: a structural editor whose laws are explicit

## The supplied idea

The source artifact opens with four architectural statements:

> The document is an AST. The editor renders the tree directly. LaTeX, Typst, and Unicode are code-generation backends over the same tree. The cursor is a path into the tree plus an offset.

These statements appear in source lines 5--8 and determine almost every important behavior of the program. They reject the usual model of a mathematics input widget as a decorated string. Fractions, roots, scripts, functions, groups, large operators, and accents are runtime structures. The WYSIWYG view recurses through those structures. Output formats recurse through the same structures. A selected hole is not a character in a source string but a node at a structural address.

That basis is stronger than many production editors. It makes balanced delimiters representable by construction, supports template holes, permits structural selection, and allows one document to have multiple textual projections. It also opens the door to precise semantics: the document can be treated as an inductive term, editing as a transition system, rendering as a fold, and cursor movement as navigation through one-hole contexts.

The difficulty is that the source expresses these ideas operationally rather than axiomatically. A JavaScript object with `k: "frac"` is intended to have two row-valued fields, but no type prevents one from being missing. A path step is intended to point to a valid child field, but `getRow` reduces through the path without a checked failure case. A script is intended to decorate a base, but it is stored as a sibling node that has only superscript and subscript children. An accent is documented as wrapping the selection or previous node, yet the no-selection branch inserts a fresh accent whose body is only a hole. The three output functions are intended to be interpretations of one syntax, but their unknown cases return empty strings or lossy fallbacks.

The right response is not to discard the program. It is to identify the algebra it already approximates, specify the invariants that algebra requires, and move all mutation-like behavior behind a pure, total interface.

## Research questions

This reconstruction is organized around six questions.

1. **What is the exact abstract syntax represented by the runtime objects?**
2. **What constitutes a valid cursor and selection for that syntax?**
3. **How should editing commands be specified so that successful edits preserve validity?**
4. **In what sense are LaTeX, Typst, Unicode, and WYSIWYG views denotational semantics?**
5. **Which invariants belong in types, which require runtime validation, and which require an external mathematical theory?**
6. **How do initial algebras, datatype derivatives, lenses, and Kleisli arrows organize the design?**

The answers produce both a mathematical model and executable code.

## Contributions

The work makes the following concrete contributions.

### A source-grounded decomposition

The single component is separated conceptually into ten subsystems: syntax constructors, child-field reflection, path access, hole traversal, backend generation, WYSIWYG rendering, editor state, primitive edits, navigation, and interface modes. This decomposition preserves the source terminology and intended interaction model.

### A corrected structural syntax

The reconstructed syntax is presentation-neutral. Recursive child positions are non-empty slots. Holes carry unique identities. Scripts own their bases and require at least one attachment. Accents own their bodies. Annotated arrows are not encoded as accents. Symbols refer to semantic catalog identifiers rather than storing LaTeX as canonical data.

### A checked zipper and lawful path lens

A cursor path is decoded into a sequence zipper containing prefix, parent node, selected field, and suffix crumbs. Rebuilding through the crumbs yields a checked `plug` operation. On valid paths, `focus` and `replace` satisfy the standard GetPut, PutGet, and PutPut lens laws.

### A deterministic editor calculus

Commands are values and the editor core is a pure reducer. Insertion, deletion, horizontal movement, hole jumps, structural selection growth, function wrapping, script attachment, accents, and new lines are defined without direct UI effects. Invalid persisted states and impossible paths produce explicit errors rather than uncaught property access.

### Algebraic output backends

The recursive scheme is factored into a single `SyntaxAlgebra<A>`. LaTeX, Typst, Unicode, size computation, and hole-order collection are instances. This makes constructor coverage auditable and gives a direct categorical interpretation as folds from an initial algebra.

### Executable verification and artifacts

The code checks path-lens laws, state invariants, history and codec round trips, backend totality, and randomized command preservation. The bundle includes the original source, the reconstructed code, the complete Markdown thesis, a typeset PDF, interface screenshots, diagrams, and test output.

## What this work does not claim

A structural notation tree is not automatically a typed mathematical term. The displayed sequence

\[
  F \dashv G : \mathcal C \rightleftarrows \mathcal D
\]

suggests categories, functors, and an adjunction, but the glyphs alone do not establish that $\mathcal C$ and $\mathcal D$ are categories, that $F$ and $G$ have compatible domains and codomains, or that unit and counit laws hold. Such facts require a signature, a context, an elaborator, and proof obligations. The editor may preserve the syntax of the display while the display remains ill-typed in any intended theory.

Accordingly, later chapters define two denotational layers. The first maps editor syntax to a presentation-neutral mathematical document tree and then to output formats. The second, optional layer elaborates that tree into a typed core language and interprets it in a model. Only the second layer can support object-level soundness.

## Baseline capture

The following capture reconstructs the visible baseline from the supplied component. It is not a screenshot of a separately deployed application; it is a faithful static rendering produced from the source's dimensions, labels, palette, formula, output bar, and keyboard layout.

![Baseline capture reconstructed from the supplied component.](../screenshots/baseline-editor.png){width=96%}

The baseline makes the design tension visible. The interface communicates a coherent structural editor, while the implementation underneath has no explicit notion of a valid state. The rest of the thesis closes that gap.

## Chapter summary

The source begins from the correct ontological choice: formulas are trees, not strings. The thesis preserves this choice and strengthens it with explicit laws. The target is not merely cleaner code. It is a system in which the datatype, cursor, transition relation, renderers, persistence boundary, and tests state the same mathematical contract.

## Exercises

1. Give two examples of editor behavior that are difficult to implement correctly over raw text but direct over a tree.
2. Explain why balanced delimiters are a structural invariant rather than merely a rendering feature.
3. Construct two visually similar formulas that require distinct syntax trees.
4. State why the display $F\dashv G$ does not by itself prove the existence of an adjunction.

# Forensic decomposition of the source artifact

## The runtime grammar

Source lines 12--21 define builder functions. The sequence constructor is `row`; expression constructors are `sym`, `hole`, `frac`, `sqrt`, `scr`, `func`, `grp`, `big`, and `acc`. Abstracting from JavaScript record syntax gives the following grammar:

\[
\begin{aligned}
R &::= [N_1,\ldots,N_k],\\
N &::= \mathsf{Sym}(t,d,o)
  \mid \mathsf{Hole}
  \mid \mathsf{Frac}(R,R)
  \mid \mathsf{Sqrt}(R,\mathsf{Opt}(R))\\
  &\quad\mid \mathsf{Scr}(\mathsf{Opt}(R),\mathsf{Opt}(R))
  \mid \mathsf{Func}(name,cmd,R)
  \mid \mathsf{Group}(l,r,R)\\
  &\quad\mid \mathsf{Big}(op,d,R,R)
  \mid \mathsf{Accent}(cmd,mark,R).
\end{aligned}
\]

The grammar as implemented is permissive. A `scr` may have neither attachment. Delimiters are arbitrary strings. Symbol records combine a LaTeX token, a display string, and optional layout flags. Recursive children are rows, and rows may be empty.

Source lines 23--33 define `fieldsOf`, a reflection function from runtime node tags to ordered recursive fields. This is the hidden signature of the datatype. Navigation, hole collection, emptiness, and rendering all depend on it. The table also establishes traversal order: numerator before denominator, index before radicand when present, superscript before subscript, and lower before upper.

### Observation: one component contains a language implementation

The component is not only a user interface. It contains the usual layers of a small language toolchain:

| Language concern | Source mechanism |
|---|---|
| concrete input vocabulary | keyboard layers, catalog, fuzzy aliases |
| abstract syntax | row and node builders |
| structural reflection | `fieldsOf` and `FIELD_ORDER` |
| interpreters | LaTeX, Typst, Unicode functions |
| evaluator-like state transition | insert, delete, navigation, wrapping |
| pretty printer | recursive React renderer |
| serialization | JSON persistence |
| interaction history | undo/redo snapshots |
| tutorial/specification | dynamic documentation overlay |

Treating the component as a language implementation rather than as a collection of button handlers immediately clarifies the right abstractions.

## Tree access as an unchecked lens

Source lines 39--45 define `getRow` and `setRow`. A path step has an expression index `i` and a field name `f`. `getRow` follows the steps by repeated indexing; `setRow` rebuilds each ancestor immutably.

For a valid path $p$, these functions approximate a lens

\[
  \mathsf{get}_p : R \to R,
  \qquad
  \mathsf{put}_p : R\times R \to R.
\]

But they are only partial JavaScript functions. An out-of-bounds index, a field that does not belong to the selected constructor, or malformed persisted data causes property access through `undefined`. The exception is not represented in the type or result.

The reconstruction retains the useful recursive update but changes the interface:

\[
  \resolve : R\times P \to \Result(Z,E),
  \qquad
  \plug : Z\times R \to \Result(R,E),
\]

where $Z$ is a zipper and $E$ explains the invalid index, invalid field, empty slot, or invalid replacement.

## Holes and traversal order

Source lines 47--70 flatten a path into a numeric trace and collect holes by depth-first traversal. The trace interleaves expression indices with field ranks. Hole jumping compares traces, enabling a next/previous operation that wraps at the ends.

This is a practical encoding of a total order on positions. Its weakness is duplication: field order appears both in `fieldsOf` and in `FIELD_ORDER`. Adding or reordering a constructor field requires changing both tables consistently. The reconstruction makes `childFields` the canonical source of recursive positions. Hole collection and navigation consume that function directly.

Holes in the source are anonymous. Two inserted templates containing holes cannot be distinguished except by current address. The reconstruction assigns every hole a unique identifier. Identity is not needed merely to draw a square, but it is useful for stable focus, collaborative edits, template cloning, diagnostics, and later elaboration into metavariables.

## Three recursive backends

Source lines 73--124 implement LaTeX, Typst, and Unicode as separate recursive switch statements. Their common recursion is clear:

```javascript
const genRow = (r, g) => r.c.map((n) => g(n)).join("");
```

Each backend supplies an interpretation of constructors. Fractions become `\frac`, slash syntax, or parenthesized numerator/denominator text. Roots become backend-specific root forms. Scripts become attachments. Functions, groups, large operators, and accents are similarly mapped.

This is already an algebraic pattern, but it is duplicated rather than named. In categorical terms, each switch is an $F$-algebra and each top-level recursive function is the unique catamorphism induced by that algebra. The reconstruction extracts the shared fold so that missing constructor cases are type errors rather than silent defaults.

### Loss and ambiguity in the original backends

Several cases are intentionally approximate or accidentally lossy.

- The Unicode root renderer ignores the optional index, so square roots and indexed roots can collapse to the same output.
- Unicode scripts use character maps only for a small alphabet and fall back to parenthesized syntax.
- The Typst mapping is marked draft and mixes lookup tables, command stripping, and direct heuristic conversion.
- Unknown node kinds return an empty string.
- A symbol node stores its LaTeX spelling as part of the syntax, making one backend privileged.
- An annotated arrow is encoded with the accent constructor, although its display behavior and semantic role differ from an accent.

A mathematically honest backend must be total and must report where a target format lacks a faithful native notation. The reconstructed renderer therefore returns both text and issues. It never silently erases a constructor.

## WYSIWYG rendering

Source lines 206--327 recursively render rows and nodes into React spans. Cursor state is threaded as contextual data. The rendering is not a plain fold because the appearance of a row depends on its path, line, selection, and click handlers. It can nevertheless be factored as a fold into a reader-like target: each algebra result is a function from rendering context to a UI fragment.

The source renderer demonstrates why the structural model is valuable. A fraction's numerator and denominator are separate rows. A root's radicand is beneath an overbar. A script displays attachments in a vertical stack. Clicking a hole selects exactly that node. These are direct consequences of constructor identity, not fragile inferences from source text.

## Editor state and history

Source lines 335--383 define state for lines, cursor, keyboard layer, style modifier, dynamic bar, query, output format, pins, recents, documentation, copied status, history, and long-press timers. The semantic state and interface state coexist in one component.

The history object is a mutable ref with `undo` and `redo` arrays. A snapshot serializes `lines` and `cur`. This works in the local component, but it obscures a simpler algebraic structure:

\[
  \mathsf{Timeline}(S) = S^* \times S \times S^*.
\]

The current state is the focus of a zipper over a sequence of committed states. Committing appends the current state to the past and clears the future. Undo moves one element from the end of the past to the present while pushing the old present onto the future. Redo performs the inverse move. The reconstruction represents exactly this immutable structure.

## Editing commands hidden inside callbacks

Source lines 389--563 implement insertion, postfix attachment, deletion, horizontal movement, hole jumps, structural selection growth, function wrapping, new lines, copying, and pins. The code contains the operational semantics of the editor, but commands are not represented as data. Instead, each button or gesture invokes a closure that reads component state and performs state updates.

The reconstruction introduces a command datatype:

```typescript
type Command =
  | { kind: "insert"; nodes: NonEmpty<Expr> }
  | { kind: "moveHorizontal"; direction: -1 | 1 }
  | { kind: "jumpHole"; direction: -1 | 1 }
  | { kind: "deleteBackward" }
  | { kind: "growSelection" }
  | { kind: "wrapFunction"; name: string }
  | { kind: "attachScript"; position: "superscript" | "subscript"; content?: Slot }
  | { kind: "applyAccent"; accent: AccentKind }
  | { kind: "newLine" };
```

Once commands are values, the transition function can be tested independently of React, replayed, logged, synchronized, or given a formal semantics.

## Concrete defects and design hazards

The following findings are source-derived. They are not allegations about every possible execution; they identify places where the code does not establish the stronger guarantee implied by the interface.

| Finding | Source behavior | Formal consequence |
|---|---|---|
| unchecked runtime grammar | fields selected by string tags | malformed values are representable |
| partial path access | reduction through indices and fields | invalid paths can throw |
| empty recursive rows | arrays may have length zero | focus target may be absent |
| script as postfix sibling | base is outside the script node | orphan scripts are representable |
| accent behavior mismatch | no-selection branch inserts an accent template | prior node is not wrapped despite documentation |
| overloaded accent/arrow node | `xrightarrow` uses `acc` | constructor meaning is not injective |
| anonymous holes | all holes are `{k:"hole"}` | cloned positions lack stable identity |
| duplicated traversal order | `fieldsOf` plus `FIELD_ORDER` | maintenance can break canonical order |
| silent backend defaults | default branch returns empty text | information can disappear |
| indexed-root Unicode loss | index is ignored | distinct trees can share output |
| unvalidated persistence | parsed JSON is accepted directly | invalid data crosses the boundary |
| swallowed storage errors | empty `catch` blocks | failure is unobservable |
| mutable history ref | snapshots managed imperatively | laws are not localized |
| selection lacks orientation | only sorted `s,e` are stored | anchor-sensitive extension is impossible |
| semantic and UI state mixed | one component owns all behavior | proof and testing boundaries are unclear |

### The accent mismatch in detail

The documentation says that bar, hat, and tilde act on a selection or the node before the cursor. In the implementation, the selection branch constructs a new accent whose child is the selected row. With no selection, however, `insertNodes([node])` inserts the default accent node containing a hole. The previous node remains outside it. This is not a philosophical objection; it is a direct mismatch between two branches of the source.

The reconstructed command follows one rule: choose the selected span if non-empty; otherwise choose the preceding expression if one exists; otherwise create a fresh hole. Replace that span with one accent node whose body is the chosen non-empty slot.

### A path is not by itself a materialized zipper

The source comment calls `path + offset` a zipper. Given the root and a valid path, this representation is extensionally sufficient to recover a zipper. But a path is an address; a materialized zipper stores the context required to rebuild the root locally. This distinction matters for complexity and laws. The reconstruction's persistent state keeps the serializable path, while `resolvePath` materializes crumbs before an edit. Thus the implementation obtains the convenience of addresses and the semantics of zippers without storing closures or redundant ancestors.

## Preserved strengths

A reconstruction should not erase the source's good decisions.

- Direct tree rendering is retained.
- Explicit holes and next-hole navigation are retained.
- Structural selection growth is retained.
- Multiple output formats over one document are retained.
- Immutable tree rebuilding is retained.
- Search aliases and templates remain compatible with semantic symbol IDs.
- Undo/redo, worksheets, and persistent templates remain natural extensions.

The new design is therefore a refinement, not a replacement of the interaction concept.

## Chapter summary

The source contains a compact language processor whose algebra is distributed across tables, switch statements, and callbacks. Its strongest idea is the shared structural document. Its main weakness is that validity is an intention rather than an explicit predicate. The next chapter develops the semantic tools needed to state that predicate and the operations over it.

## Exercises

1. Write the original runtime grammar as a TypeScript discriminated union without changing its shape.
2. Give an example path that is syntactically a list of steps but invalid for a fraction node.
3. Explain why the source's three recursive generators indicate an initial-algebra pattern.
4. Show how anonymous holes complicate collaborative editing or persistent diagnostics.
5. Find another source behavior whose documentation is stronger than its implementation.


# Semantic and categorical preliminaries

## Algebraic datatypes as sums and products

A variant datatype is modeled by a coproduct, and a record constructor by a product. For example, an untyped expression language

\[
  E ::= \mathsf{Num}(\mathbb N) \mid \mathsf{Add}(E,E)
\]

corresponds to a functor

\[
  F(X)=\mathbb N + X\times X.
\]

An $F$-algebra is a carrier $A$ with a structure map $\alpha:F(A)\to A$. Concretely, it supplies one operation for numerals and one binary operation for addition. If the expression datatype is the initial $F$-algebra $(\mu F,\mathsf{in})$, then for every algebra $(A,\alpha)$ there is a unique homomorphism

\[
  \cata(\alpha):\mu F\to A
\]

such that

\[
  \cata(\alpha)\circ\mathsf{in}
  =\alpha\circ F(\cata(\alpha)).
\]

This homomorphism is the familiar structural fold. It is unique because every expression is built from the constructors and the homomorphism equations determine its result constructor by constructor. Initial-algebra semantics was developed as a unifying account of syntax and interpretation [Goguen et al. 1977]; Lambek's fixed-point result explains why the structure map of an initial algebra is an isomorphism under standard conditions [Lambek 1968].

The editor syntax uses finite sequences in recursive positions. Finite list and non-empty list functors are containers:

\[
  X^*=\coprod_{n\in\mathbb N}X^n,
  \qquad
  X^+=\coprod_{n\ge 1}X^n.
\]

They are strictly positive and support maps, folds, and derivatives. The container perspective is useful because it separates a shape---the sequence length---from positions inside that shape [Abbott, Altenkirch, and Ghani 2005].

## Structural operational semantics

Operational semantics describes behavior by transitions between configurations. Plotkin's structural operational semantics presents rules whose premises describe transitions of components and whose conclusions describe transitions of compound terms [Plotkin 1981]. An editor command is simpler than a general programming language, but the same discipline applies.

Let $S$ be valid editor states and $C$ commands. A transition judgment may be written

\[
  \langle s,c\rangle \longrightarrow s'
\]

or, when failure is explicit,

\[
  \langle s,c\rangle \Downarrow \Ok(s')
  \qquad\text{or}\qquad
  \langle s,c\rangle \Downarrow \Err(e).
\]

The implementation uses the second, big-step style for one atomic command. Pointer gestures and key presses are translated to a command, then the command is evaluated in one pure reducer call. A small-step UI machine could add modes such as long-press and search, but those modes are intentionally kept outside the document semantics.

Three metatheoretic properties matter.

> **Determinism.** For a fixed valid state and command, there is at most one successful result.

> **Preservation.** If $\Valid(s)$ and $\langle s,c\rangle\Downarrow\Ok(s')$, then $\Valid(s')$.

> **Explicit failure.** If a persisted value or command cannot be interpreted, the reducer returns a typed error rather than leaving the domain of states by an exception or malformed object.

The first follows from functional definitions; the second is the central proof obligation; the third is an API totality property.

## Denotational semantics and compositionality

Scott and Strachey characterize mathematical semantics as a correspondence between program phrases and mathematical entities independent of implementation [Scott and Strachey 1971]. The key discipline is compositionality: the meaning of a compound is determined by the meanings of its immediate constituents.

For the editor there are two distinct denotational questions.

1. What presentation-neutral structure does a syntax node express?
2. What mathematical object does that structure denote in a chosen theory?

The first can be answered entirely within the editor. A symbol node with semantic ID `adjunction`, for example, denotes a relation token in a mathematical document tree independent of whether it will be rendered as `\dashv`, `tack.l`, or `⊣`. A fraction node denotes a presentation-neutral fraction of two structural rows.

The second cannot be answered without context. A row is a sequence of notation, not necessarily a parsed term. The glyph `-` may be unary negation, subtraction, a component of an arrow, or punctuation. Juxtaposition may mean multiplication, function application, tensoring, or mere visual adjacency. Thus a later elaboration relation is required:

\[
  \Gamma \vdash e \rightsquigarrow t : \tau,
\]

followed by an interpretation in a model $M$:

\[
  \llbracket \Gamma\vdash t:\tau\rrbracket_M
  \in \llbracket\tau\rrbracket_M.
\]

This separation prevents a common category error: confusing reliable code generation with proof of mathematical correctness.

## Type theory: intrinsic and extrinsic validity

A type can encode a structural invariant intrinsically, making invalid values unconstructible. For instance,

\[
  \mathsf{NonEmpty}(A)=\Sigma(n:\mathbb N).\,\mathsf{Vec}(A,n+1)
\]

ensures at least one element. A script can be represented by a sum with no empty-attachment case:

\[
\begin{aligned}
\mathsf{Attachments}(R)
  &= \mathsf{Sup}(R)
   + \mathsf{Sub}(R)
   + \mathsf{Both}(R,R),\\
\mathsf{Script}(R)
  &= R\times\mathsf{Attachments}(R).
\end{aligned}
\]

Paths are naturally dependent. A field name is valid only for certain constructors, and the type of the next focus depends on that field. An ideal formulation would use a family

\[
  \mathsf{Field}:\mathsf{Node}\to\mathsf{Type}
\]

and a path whose next step is indexed by the current node. TypeScript cannot express a path indexed by the runtime value of the whole document in an ergonomic serializable form. The reconstruction therefore combines intrinsic and extrinsic techniques:

- discriminated unions and non-empty tuples exclude many malformed values;
- smart constructors exclude scripts with no attachment;
- a runtime validator checks decoded data and unique hole IDs;
- path resolution returns `Result` and checks constructor-specific fields;
- reducer boundaries revalidate the resulting state.

This is not a failure of type theory. It is a disciplined approximation appropriate to the implementation language.

## Zippers and one-hole contexts

A one-hole context $C[-]$ is a value with one distinguished recursive position. Plugging $x$ into the hole yields $C[x]$. Huet's zipper represents a focused tree together with the path needed to reconstruct its ancestors [Huet 1997]. For a list, the context is a prefix and suffix:

\[
  \mathsf{ListCtx}(X)\cong X^*\times X^*.
\]

For polynomial datatypes, the derivative operation obeys familiar rules:

\[
  (K)'=0,
  \quad X'=1,
  \quad (F+G)'=F'+G',
  \quad (F\times G)'=F'\times G+F\times G'.
\]

McBride's observation is that the derivative of a regular type computes its type of one-hole contexts [McBride 2001]. For a recursive tree, a zipper contains the focused subtree plus a list of derivative-shaped crumbs, one for each ancestor.

The editor's focus is a sequence rather than a single expression. A crumb therefore stores:

- the parent sequence kind;
- expressions before the parent node;
- the parent node itself;
- expressions after the parent node;
- the child field through which focus descended.

This is exactly the data needed to plug an updated sequence back into its root.

## Lenses

A lens from a source $S$ to a view $V$ consists of

\[
  \mathsf{get}:S\to V,
  \qquad
  \mathsf{put}:S\times V\to S.
\]

For a fixed valid editor path, the source is a line and the view is its focused sequence. The standard well-behavedness laws are:

\[
\begin{aligned}
\text{GetPut: }&\mathsf{put}(s,\mathsf{get}(s))=s,\\
\text{PutGet: }&\mathsf{get}(\mathsf{put}(s,v))=v,\\
\text{PutPut: }&\mathsf{put}(\mathsf{put}(s,v_1),v_2)=\mathsf{put}(s,v_2).
\end{aligned}
\]

They hold only when the path remains valid and the replacement respects slot non-emptiness. The reconstructed API therefore has a partial, error-aware lens. In categorical terms it lives naturally in a category of partial maps or in the Kleisli category of the exception monad.

Lens laws are not ornamental. GetPut prevents a no-op edit from changing the document; PutGet ensures an accepted replacement is actually the new focus; PutPut ensures repeated local updates do not retain hidden effects from an earlier replacement. The executable tests check all three on representative nested syntax.

## Monads and explicit failure

For an error set $E$, define

\[
  T(X)=E+X.
\]

This is the exception monad. A partial edit is represented as a total function

\[
  f:S\to T(S).
\]

Commands therefore denote endomorphisms in the Kleisli category $\mathsf{Kl}(T)$. Sequential command execution uses monadic composition: an error short-circuits, while a successful state is passed to the next command. This formulation is more precise than saying an operation “might throw,” because errors are values and composition is specified.

The implementation's `Result<T,E>` is this sum type. It is used for path resolution, decoding, and reducer transitions. Smart constructors such as `nonEmpty` still throw when called incorrectly inside trusted TypeScript code; values crossing untrusted boundaries are decoded and validated through `Result`.

## Histories as zippers over time

A document zipper focuses space; a timeline zipper focuses time. Define

\[
  H(S)=S^*\times S\times S^*.
\]

An undo step is defined when the past is $p\mathbin{+\!+}[s_-]$:

\[
  (p\mathbin{+\!+}[s_-],s,f)
  \xrightarrow{undo}
  (p,s_-,[s]\mathbin{+\!+}f).
\]

Redo is the inverse move when the future begins with $s_+$:

\[
  (p,s,[s_+]\mathbin{+\!+}f)
  \xrightarrow{redo}
  (p\mathbin{+\!+}[s],s_+,f).
\]

Committing a new state appends the present to the past and discards the future. A finite history limit truncates the oldest past states. This design is pure and directly testable.

## Chapter summary

The required theory is not exotic. Algebraic datatypes provide the syntax, structural operational semantics provides the command calculus, denotational semantics separates structure from implementation, dependent types state validity, datatype derivatives explain cursors, lenses state local-update laws, the exception monad represents failure, and a second zipper explains history. The following chapters apply these tools to the editor in detail.

## Exercises

1. Derive the one-hole context type for $F(X)=A+X\times X$ using the differentiation rules.
2. Show that list contexts are isomorphic to a prefix and suffix.
3. Give a counterexample to PutGet if a path update silently truncates a replacement.
4. Explain why `Result` makes a partial function total without making every command successful.
5. Distinguish a fold that emits LaTeX from an object-level denotation in a model of category theory.


# A presentation-neutral syntax with explicit invariants

## Design criterion

The first reconstruction task is to decide what the editor stores. This decision must precede rendering, navigation, persistence, and interface design. A data model is satisfactory only when every inhabitant denotes a structurally admissible editor document and every intended blank position has an explicit representation.

The source model comes close to this criterion but does not meet it. Its child rows may be empty, its script node may contain no script, and its symbols combine semantic identity with one backend spelling. The replacement model therefore adopts four principles.

1. **Recursive child positions are non-empty.** A numerator, denominator, radicand, function argument, group body, accent body, arrow label, and script component always contains at least one expression.
2. **Blankness is data.** An editable blank is a uniquely identified hole, not an absent array entry and not an empty recursive sequence.
3. **Structural ownership is explicit.** A script owns its base; an accent owns its body; an annotated arrow owns its label.
4. **Backend spelling is derived.** A symbol node records an identifier in a catalog. LaTeX, Typst, Unicode, and visual renderers interpret that identifier separately.

These choices make illegal structural states less representable and make the remaining dynamic checks local.

## The polynomial signature

Let the following sets be given:

- $A$, atomic tokens, including identifiers, numbers, punctuation, and catalog symbols;
- $H$, hole identities with optional expectations;
- $N$, function names;
- $D$, delimiter-pair identifiers;
- $O$, large-operator identifiers;
- $K$, accent identifiers;
- $Q$, arrow identifiers.

For any set $X$, define

\[
  \mathsf{Line}(X)=X^*,
  \qquad
  \mathsf{Slot}(X)=X^+.
\]

A line may be empty because an empty worksheet line is a valid top-level state. A recursive slot may not be empty. Define the endofunctor $F:\mathbf{Set}\to\mathbf{Set}$ by

\[
\begin{aligned}
F(X)={}&A+H
  +\mathsf{Slot}(X)^2 \\
 &+\mathsf{Slot}(X)\times\bigl(1+\mathsf{Slot}(X)\bigr) \\
 &+\mathsf{Slot}(X)\times
   \bigl(\mathsf{Slot}(X)+\mathsf{Slot}(X)+\mathsf{Slot}(X)^2\bigr) \\
 &+N\times\mathsf{Slot}(X)
  +D\times\mathsf{Slot}(X) \\
 &+O\times\bigl(1+\mathsf{Slot}(X)\bigr)^2 \\
 &+K\times\mathsf{Slot}(X)
  +Q\times\mathsf{Slot}(X).
\end{aligned}
\]

The summands represent, in order:

- atoms and holes;
- fractions;
- roots, with an optional index;
- scripts, with a base and either a superscript, a subscript, or both;
- functions and groups;
- large operators with independently optional lower and upper limits;
- accents and annotated arrows.

The expression type is the least fixed point

\[
  \mathsf{Expr}=\mu F.
\]

A document is a non-empty finite list of lines:

\[
  \mathsf{Document}=\mathsf{Line}(\mathsf{Expr})^+.
\]

This is a regular, strictly positive recursive signature. Its recursive occurrences appear only under sums, products, and finite-list constructors. Consequently it supports structural recursion, induction, folds, container representations, and datatype differentiation.

## Concrete constructors

The mathematical signature is implemented by the following family of constructors:

\[
\begin{array}{rcl}
\mathsf{atom} &:& A\to\mathsf{Expr},\\
\mathsf{hole} &:& H\to\mathsf{Expr},\\
\mathsf{frac} &:& \mathsf{Slot}(\mathsf{Expr})^2\to\mathsf{Expr},\\
\mathsf{root} &:& \mathsf{Slot}(\mathsf{Expr})\times(1+\mathsf{Slot}(\mathsf{Expr}))\to\mathsf{Expr},\\
\mathsf{script} &:& \mathsf{Slot}(\mathsf{Expr})\times\mathsf{Attachments}\to\mathsf{Expr},\\
\mathsf{function} &:& N\times\mathsf{Slot}(\mathsf{Expr})\to\mathsf{Expr},\\
\mathsf{group} &:& D\times\mathsf{Slot}(\mathsf{Expr})\to\mathsf{Expr},\\
\mathsf{largeOp} &:& O\times(1+\mathsf{Slot}(\mathsf{Expr}))^2\to\mathsf{Expr},\\
\mathsf{accent} &:& K\times\mathsf{Slot}(\mathsf{Expr})\to\mathsf{Expr},\\
\mathsf{arrow} &:& Q\times\mathsf{Slot}(\mathsf{Expr})\to\mathsf{Expr}.
\end{array}
\]

Here

\[
  \mathsf{Attachments}
  =\mathsf{Slot}(\mathsf{Expr})
   +\mathsf{Slot}(\mathsf{Expr})
   +\mathsf{Slot}(\mathsf{Expr})^2
\]

is the disjoint union of superscript-only, subscript-only, and both. There is no constructor for a script with no attachment.

The corresponding TypeScript definition uses a discriminated union. `Slot` is a non-empty tuple type:

```ts
export type NonEmpty<T> = readonly [T, ...T[]];
export type Line = readonly Expr[];
export type Slot = NonEmpty<Expr>;

export type ScriptExpr = {
  readonly kind: "script";
  readonly base: Slot;
} & (
  | { readonly superscript: Slot; readonly subscript?: Slot }
  | { readonly superscript?: Slot; readonly subscript: Slot }
);
```

TypeScript cannot prevent every malformed value after JSON decoding or unsafe casts, but this representation makes normal construction precise and gives the decoder a clear target invariant.

## Holes as metavariables of the editor layer

A hole is not an empty string. It is a node

\[
  \mathsf{Hole}(h,\epsilon),
\]

where $h\in H$ is a globally unique identity and $\epsilon$ is an optional expectation such as `expression`, `identifier`, `number`, or `index`. The expectation is a user-interface hint, not yet an object-language type. A future elaborator may refine it into a typed metavariable.

Unique identities solve three practical problems.

First, a hole remains distinguishable when a template is copied. The insertion algorithm freshens every copied hole, so two copies of a fraction template do not share the same identity. Second, navigation and diagnostics can refer to a stable placeholder rather than only a transient array position. Third, persistence validation can detect accidental duplication.

Let $\mathsf{holes}(e)$ be the multiset of hole identities in an expression, extended pointwise to lines and documents. The uniqueness invariant is

\[
  \forall h.\;\mathsf{multiplicity}(h,\mathsf{holes}(D))\le 1.
\]

The editor stores a counter `nextHole`. For a valid state, every automatically allocated identity has the form $h_n$ and `nextHole` is strictly greater than every numeric suffix already in the document. External IDs that do not follow this convention remain legal provided they are unique.

## Child slots and total reflection

Navigation requires a uniform way to enumerate recursive fields. Define a finite set of child labels

\[
\begin{aligned}
\mathsf{Field}=
\{&\mathsf{numerator},\mathsf{denominator},\mathsf{radicand},\mathsf{index},
\mathsf{base},\mathsf{superscript},\mathsf{subscript},\\
&\mathsf{argument},\mathsf{body},\mathsf{lower},\mathsf{upper},\mathsf{label}\}.
\end{aligned}
\]

For each expression $e$, `childFields(e)` returns exactly the recursive fields present in $e$, in document traversal order. `getChild(e,f)` is partial because not every field belongs to every constructor. `setChild(e,f,s)` is likewise partial and additionally requires $s$ to be non-empty.

The essential coherence property is:

\[
  f\in\mathsf{childFields}(e)
  \quad\Longleftrightarrow\quad
  \mathsf{getChild}(e,f)\text{ is defined}.
\]

A second property connects getting and setting:

\[
  \mathsf{getChild}(\mathsf{setChild}(e,f,s),f)=s
\]

whenever the update is defined. These local laws are the building blocks for the path lens of the next chapter.

Traversal order is semantic editor data. It determines horizontal entry into structures and the order in which `next hole` visits placeholders. The reconstruction uses:

- numerator, then denominator;
- index, then radicand;
- base, superscript, subscript;
- lower, then upper;
- the sole child for functions, groups, accents, and annotated arrows.

The choice for scripts differs from the source because the reconstructed node owns its base. This means rightward movement enters the base first, then the attachments; hole traversal follows the same order.

## Valid expressions, documents, and states

Structural validity is defined inductively. Write $\Valid_S(s)$ for a valid slot and $\Valid_E(e)$ for a valid expression.

A slot is valid when it is non-empty and every member is valid:

\[
  \frac{n\ge1\qquad \Valid_E(e_1)\quad\cdots\quad\Valid_E(e_n)}
       {\Valid_S([e_1,\ldots,e_n])}.
\]

Atoms are valid when their payload satisfies elementary lexical checks. Holes are valid when their IDs are non-empty. Composite constructors are valid when their tags and parameters are recognized and all present child slots are valid. Representative rules are:

\[
\frac{\Valid_S(n)\qquad\Valid_S(d)}
     {\Valid_E(\mathsf{Frac}(n,d))}
\qquad
\frac{\Valid_S(b)\qquad\Valid_S(u)}
     {\Valid_E(\mathsf{ScriptSup}(b,u))}
\]

and

\[
\frac{\Valid_S(b)\qquad\Valid_S(u)\qquad\Valid_S(l)}
     {\Valid_E(\mathsf{ScriptBoth}(b,u,l))}.
\]

There is deliberately no rule for an attachment-free script.

A document is valid when it contains at least one line, every expression on every line is valid, and hole IDs are globally unique. A line itself may be empty. This asymmetry is important: deleting the last expression from a top-level line yields a valid blank line, while deleting the only expression in a numerator must replace it with a fresh hole rather than produce an empty slot.

An editor state additionally contains a cursor and a fresh-hole counter. Its full validity predicate is

\[
\begin{aligned}
\Valid(S)\iff{}&\Valid_D(S.\mathsf{document})\\
&\land 0\le S.\mathsf{cursor.line}<|S.\mathsf{document.lines}|\\
&\land \resolve(S.\mathsf{document},S.\mathsf{cursor})\text{ succeeds}\\
&\land 0\le\mathsf{anchor},\mathsf{head}\le|\mathsf{focusedSequence}|\\
&\land S.\mathsf{nextHole}\ge0\\
&\land S.\mathsf{nextHole}>\max\{n\mid h_n\text{ occurs in the document}\}.
\end{aligned}
\]

The executable validator reports a path and message for each violation. It is applied after decoding persisted data and after each reducer transition in the reference implementation. In a fully dependently typed implementation, much of the predicate would be carried by the state type itself.

## Why scripts must own their bases

In the supplied source, a script is a postfix sibling. The sequence for $x^2$ is morally

\[
  [\mathsf{Sym}(x),\mathsf{Scr}([2],\varnothing)].
\]

This mirrors the surface syntax of TeX but obscures the editor's own structure. The script can exist at the start of a row, where the source compensates by inserting a hole before it. Selection can separate the base from its script. A renderer must infer attachment from adjacency. Deleting or moving across the pair requires special cases.

The reconstructed representation is

\[
  [\mathsf{ScriptSup}([\mathsf{Sym}(x)],[2])].
\]

This representation has several advantages.

- The relation between base and attachment is an invariant rather than a convention.
- Moving or copying the expression preserves the decoration.
- Rendering does not depend on left context.
- A script can decorate a compound base without flattening it.
- Selection growth can climb from an attachment to the whole scripted expression.
- Object-level elaboration sees one application of a script-former rather than two adjacent tokens.

The change is semantic, not merely stylistic. It modifies the abstract syntax so that the tree records the relation the interface presents.

## Why annotated arrows are not accents

The source reuses its accent constructor to represent a labelled arrow, supplying `\xrightarrow` as the command and `→` as the mark. This works only because the renderer has enough ad hoc data to display something plausible. An accent and an annotated arrow have different geometry, backend syntax, navigation meaning, and prospective mathematical interpretation.

The reconstruction introduces

\[
  \mathsf{AnnotatedArrow}(q,\ell)
\]

with arrow kind $q$ and non-empty label slot $\ell$. This keeps constructor cases semantically homogeneous. A renderer may stretch the arrow and place the label above it; a future elaborator may interpret it as a morphism annotation. Neither behavior contaminates the laws for accents.

## Symbol identity and the catalog boundary

The source stores both a LaTeX token `t` and a display token `d` inside every symbol. The same symbol may also be reconstructed through aliases, keyboard keys, long-press variants, and styled alphabets. This duplicates semantic information and permits disagreement among instances.

The replacement stores a semantic catalog ID, for example:

```ts
{ kind: "atom", atom: { kind: "symbol", id: "relation.adjoint" } }
```

The catalog supplies backend projections:

\[
  \mathsf{catalog}:\mathsf{SymbolId}\to
  \mathsf{Display}\times\mathsf{LaTeX}\times\mathsf{Typst}\times\mathsf{Unicode}\times\mathsf{Metadata}.
\]

This is not a claim that every glyph has one universal mathematical meaning. It is a normalization boundary for editor-level symbol identity. Context-sensitive elaboration remains a later phase. The ID `relation.adjoint` says which catalog entry the user selected; whether the occurrence is a valid adjunction symbol in a theory depends on its context.

## Structural induction principle

Because $\mathsf{Expr}=\mu F$, proofs and functions over expressions follow structural induction. To prove a property $P(e)$ for all expressions, it is enough to establish:

- $P$ for atoms and holes;
- for each composite constructor, $P$ for the result under the assumption that $P$ holds for every expression in every child slot.

The use of non-empty slots does not change the principle; it strengthens the induction hypotheses by guaranteeing at least one child where a slot exists. Later preservation proofs use nested induction: case analysis on the editor command, followed when needed by structural induction on copied or replaced syntax.

## Chapter summary

The reconstructed syntax makes the editor's intended structure explicit. It is the least fixed point of a strictly positive functor. Recursive slots are non-empty, holes represent editable blankness, scripts own their bases, arrows receive their own constructor, and symbols are interpreted through a catalog. These decisions turn several source conventions into datatype invariants and establish the domain on which cursor and editor semantics can be defined.

## Exercises

1. Extend $F$ with a matrix constructor whose cells are non-empty slots. State the corresponding validity rule.
2. Explain why making every line non-empty would complicate the semantics of a blank worksheet line.
3. Give a malformed JSON value that TypeScript's static type cannot prevent at runtime. State how the checked codec must reject it.
4. Prove that a structurally valid script has at least one attachment.
5. Compare the representations $[x,\mathsf{Scr}(2)]$ and $[\mathsf{Script}(x,2)]$ under copying, selection, and rendering.


# Checked paths, sequence zippers, and lawful local update

## Address versus context

The source describes the cursor as “a path into the tree plus an offset,” and its state indeed stores a list of steps. Each step contains an array index and a recursive field name. This is a useful compact address, but it is not by itself a Huet zipper. A zipper contains the focused subtree together with enough context to rebuild the whole value. A path contains only instructions for recovering that context from a root.

The reconstruction makes the distinction explicit:

- a **path** is a serializable address;
- `resolvePath` interprets a path against a line;
- the result is a **sequence zipper** containing the focus and reconstruction crumbs;
- `plug` rebuilds the line from a replacement focus.

This separation provides checked failure, establishes local-update laws, and makes cursor movement derivable from context rather than from unchecked property access.

![A path is resolved into a zipper; plugging folds the crumbs in reverse.](../figures/zipper.png){width=42%}

## Paths

A path step is a pair

\[
  (i,f)\in\mathbb N\times\mathsf{Field},
\]

where $i$ selects an expression in the current sequence and $f$ selects a recursive slot of that expression. A path is a finite list of steps:

\[
  p=[(i_1,f_1),\ldots,(i_n,f_n)].
\]

The empty path focuses the root line. A non-empty path focuses a recursive slot. Paths are intentionally untrusted: indices may be out of range, fields may not exist on selected constructors, and persisted paths may refer to an older document.

Define the partial resolution judgment

\[
  R\vdash p\Downarrow Z,
\]

meaning that path $p$ resolves in line $R$ to zipper $Z$. The root rule is

\[
  \frac{}{R\vdash []\Downarrow\langle R,\mathsf{line},[]\rangle}.
\]

For a step $(i,f)$, suppose the current sequence decomposes as

\[
  R=L\mathbin{+\!+}[e]\mathbin{+\!+}U,
  \qquad |L|=i,
\]

and $\mathsf{getChild}(e,f)=S$. Then resolution descends into $S$ and records a crumb

\[
  \kappa=\langle k,L,e,U,f\rangle,
\]

where $k$ records whether the parent sequence was the top-level line or a recursive slot. The executable implementation performs the same process iteratively and returns a `Result<SequenceZipper, PathError>`.

## Zipper crumbs

A crumb records precisely one descent:

\[
  \mathsf{Crumb}
  =\mathsf{Kind}\times\mathsf{Line}\times\mathsf{Expr}
   \times\mathsf{Line}\times\mathsf{Field},
\]

where `Kind` distinguishes a line parent from a slot parent. Operationally a crumb contains:

- expressions before the selected parent;
- the selected parent expression;
- expressions after the selected parent;
- the field through which descent occurred;
- the non-emptiness obligation of the parent sequence.

A sequence zipper is

\[
  Z=\langle R,k,[\kappa_1,\ldots,\kappa_n]\rangle.
\]

The first component is the focused sequence; the crumbs run from outermost to innermost. Rebuilding consumes them in reverse.

The stored parent expression is useful even though it contains the old child. `plug` replaces exactly the recorded field with the current rebuilt child, then reconstructs the surrounding parent sequence from the saved prefix and suffix. At each step the type of the replacement is checked: a recursive slot cannot be replaced by an empty sequence.

## Plugging

Let $\plug(Z,R')$ denote replacement of the zipper focus by sequence $R'$. At the root it is simply $R'$. For one crumb

\[
  \kappa=\langle k,L,e,U,f\rangle,
\]

first construct

\[
  e'=\mathsf{setChild}(e,f,R').
\]

Then the rebuilt parent sequence is

\[
  R''=L\mathbin{+\!+}[e']\mathbin{+\!+}U.
\]

The process repeats with the next outer crumb. It succeeds only if every child update is defined and every slot replacement is non-empty. The final result is a line.

The implementation distinguishes the type of the current sequence while rebuilding. Below the root, `currentKind` must be `slot`; after the outermost crumb it becomes `line`. This dynamic tag is a TypeScript approximation to an indexed zipper whose type records the level.

## Resolution errors

A checked resolver distinguishes four error classes.

| Error | Condition | Consequence |
|---|---|---|
| `invalidIndex` | A step index lies outside the current sequence. | The address is stale or corrupt. |
| `invalidField` | The chosen constructor has no requested child field. | The path shape disagrees with the tree. |
| `emptySlot` | Untrusted data contains an empty recursive child. | The document violates syntax invariants. |
| `invalidReplacement` | A caller attempts to put an empty sequence into a slot. | The proposed update would violate validity. |

Errors include the failing depth and a diagnostic message. This is more informative than an exception from property access and supports persistence recovery, logging, tests, and interface feedback.

## The partial path lens

For a fixed line $R$ and valid path $p$, define

\[
  \focus_p(R)=Z.\mathsf{focus}
  \quad\text{where}\quad
  R\vdash p\Downarrow Z,
\]

and

\[
  \mathsf{replace}_p(R,V)=\plug(Z,V).
\]

Because resolution and plugging may fail, this is a partial lens. Restricting attention to the domain where the path is valid and the replacement satisfies the focus kind, the usual lens laws hold.

### GetPut

\[
  \mathsf{replace}_p(R,\focus_p(R))=R.
\]

**Proof.** Resolution records at each depth exactly the parent expression, selected field, prefix, and suffix from $R$. Plugging the unchanged focus replaces each field by its existing value. By the local child GetPut law, the parent expression is unchanged; by list reconstruction, its parent sequence is unchanged. Induction over the reverse crumb list yields $R$. $\square$

### PutGet

\[
  \focus_p(\mathsf{replace}_p(R,V))=V.
\]

This law requires that replacing the focus does not change constructors or sequence lengths above the focus. The path selects only ancestors, all of which are reconstructed with the same tag, field, prefix, and suffix. Resolving the same path therefore retraces the same crumbs and reaches $V$. The local child PutGet law supplies the inductive step. $\square$

### PutPut

\[
  \mathsf{replace}_p(\mathsf{replace}_p(R,V_1),V_2)
  =\mathsf{replace}_p(R,V_2).
\]

The first replacement changes only the focused sequence. The second reconstruction overwrites that same sequence and restores all saved context. Local child PutPut and induction over crumbs remove dependence on $V_1$. $\square$

These statements are not claims about arbitrary stale paths after arbitrary edits. An edit outside the lens operation can change an ancestor or shift an indexed sibling. The laws concern a fixed valid path and updates performed through its own replacement operation.

## Cursor selection as a directed interval

A cursor contains a line index, a path, and a directed selection

\[
  \sigma=\langle a,h\rangle,
\]

where $a$ is the anchor and $h$ is the head. Both are boundaries between expressions in the focused sequence. The selected half-open interval is

\[
  [\min(a,h),\max(a,h)).
\]

The source stores sorted endpoints `s` and `e`. Sorting is convenient for replacement but loses the active end of the selection. Anchor/head representation preserves direction, allowing shift-like extension and contraction without an additional flag. Rendering can still use the normalized span.

Cursor validity requires

\[
  0\le a,h\le |R|,
\]

where $R$ is the sequence at the resolved path. A caret is the special case $a=h$. A selected hole is represented by $h=a+1$ with $R[a]$ a hole.

## Horizontal movement from the zipper structure

Rightward movement is defined by cases.

1. If a non-empty selection exists, collapse to its right boundary.
2. If there is an expression at the caret and it has child fields, enter its first child at offset $0$.
3. If there is an atomic expression at the caret, advance one boundary.
4. If at the end of a recursive slot, inspect the innermost crumb. Move to the next sibling field if one exists; otherwise ascend after the parent expression.
5. If at the end of a top-level line, move to the start of the next line when present.

Leftward movement is dual:

1. collapse a selection to its left boundary;
2. enter the last child of the previous composite expression at its end;
3. move one boundary left over an atom;
4. at a slot start, move to the end of the previous sibling field or ascend before the parent;
5. at a line start, move to the end of the preceding line.

The source implements these rules by repeatedly consulting `fieldsOf` and slicing its path. The reconstruction preserves the behavior but checks every resolution. A more intrinsically typed implementation would operate directly on a zipper cursor and derive its serializable path only for persistence.

## Hole order as a trace order

The source assigns each hole a flattened trace consisting of alternating expression indices and field-order numbers. The reconstruction generalizes this idea. Let $\mathsf{rank}_e(f)$ be the ordinal of field $f$ in `childFields(e)`. For path

\[
  [(i_1,f_1),\ldots,(i_n,f_n)]
\]

define

\[
  \mathsf{trace}(p)=[i_1,\mathsf{rank}(f_1),\ldots,i_n,\mathsf{rank}(f_n)].
\]

A hole at index $j$ in the focused sequence has trace $\mathsf{trace}(p)\mathbin{+\!+}[j]$. Lexicographic order on traces is the editor's depth-first traversal order. `jumpHole(+1)` chooses the least hole trace greater than the current boundary trace and wraps to the first when none exists. `jumpHole(-1)` is dual.

This order is deterministic because `childFields` is deterministic. It is also stable under rendering: every backend fold visits children in the same declared order. The agreement is a useful design law:

\[
  \mathsf{navigationOrder}=\mathsf{foldOrder}=\mathsf{visualStructuralOrder},
\]

subject to a visual renderer's two-dimensional layout.

## Structural selection growth

Selection growth should produce successively larger well-formed substructures. The reconstructed operation follows a three-stage rule.

1. A caret selects the immediately preceding expression when possible, otherwise the following expression.
2. A proper subinterval expands to the entire focused sequence.
3. The entire focused slot ascends to select its containing parent expression.

Repeated growth therefore follows the chain

\[
  \text{token}
  \subseteq \text{focused sequence}
  \subseteq \text{parent expression}
  \subseteq \cdots
  \subseteq \text{whole line}.
\]

Every selected interval is a contiguous sequence, and every ascent selects one whole constructor. Wrapping, pinning, and deletion therefore operate on structurally coherent regions. The system does not claim that every contiguous sequence is an object-language term; it claims that it is a well-formed editor fragment.

## Datatype derivatives

The zipper construction is explained abstractly by differentiating the syntax functor. For polynomial functors, differentiation obeys familiar rules:

\[
  (F+G)'=F'+G',
  \qquad
  (F\times G)'=F'\times G+F\times G',
  \qquad
  X'=1.
\]

For lists,

\[
  (X^*)'\cong X^*\times X^*,
\]

corresponding to the prefix and suffix around a selected element. A one-hole expression context is an element of $F'(\mu F)$, and a path of nested contexts is a list-like composition of such derivatives. Huet's zipper is the concrete data structure that stores these contexts.

The editor focuses not a single expression but a sequence slot plus an offset or interval. Its zipper therefore combines two derivatives:

- the derivative of the recursive expression shape records ancestor constructor contexts;
- the derivative of the sequence records prefixes and suffixes at each level.

This account explains why the crumb contains both a parent constructor and list context. The implementation is not an arbitrary navigation trick; it is a concrete representation of one-hole contexts for a container-shaped datatype.

## Chapter summary

Paths are compact addresses, not complete zippers. Resolving a path constructs a checked sequence zipper; plugging folds its crumbs in reverse. The resulting partial lens satisfies GetPut, PutGet, and PutPut on its valid domain. Anchor/head selections preserve direction, traversal traces order holes, and structural selection climbs the zipper. Datatype derivatives explain why these contexts have their particular shape.

## Exercises

1. Write the resolution derivation for the denominator of a fraction nested in the radicand of a root.
2. Give a stale path that fails with `invalidField` rather than `invalidIndex`.
3. Prove GetPut for a path of length two by expanding both crumbs explicitly.
4. Explain why PutGet can fail if a replacement operation also reorders an ancestor's fields.
5. Derive the list derivative $\mathsf{List}'(X)\cong\mathsf{List}(X)\times\mathsf{List}(X)$ combinatorially.


# A structural operational semantics for editing

## Configurations and commands

The editor core is modeled as a deterministic transition system. A configuration is a valid editor state

\[
  S=\langle D,c,n\rangle,
\]

where $D$ is a document, $c$ a cursor, and $n$ the next automatic hole number. Commands are first-class values:

\[
\begin{aligned}
C::={}&\mathsf{Insert}(E^+)
\mid\mathsf{Move}(\leftarrow\mid\rightarrow)
\mid\mathsf{JumpHole}(\mathsf{prev}\mid\mathsf{next})\\
&\mid\mathsf{Backspace}
\mid\mathsf{Grow}
\mid\mathsf{WrapFn}(name)\\
&\mid\mathsf{AttachScript}(\mathsf{sup}\mid\mathsf{sub},\mathsf{Opt}(E^+))\\
&\mid\mathsf{Accent}(k)
\mid\mathsf{NewLine}
\mid\mathsf{SetCursor}(c').
\end{aligned}
\]

A successful small step is written

\[
  S\xrightarrow{C}S'.
\]

A rejected command is written

\[
  S\xrightarrow{C}\mathsf{error}(e).
\]

The executable interface combines these judgments as a total function

\[
  \mathsf{reduce}:S\times C\to\Result(S,E).
\]

Before dispatch, the reducer validates the input state. Every helper that commits a new state validates the result. This double boundary is redundant for states produced solely by the reducer, but it makes the reference implementation robust against unsafe external construction and turns preservation failures into explicit test failures.

## Evaluation contexts for the focused sequence

Suppose the cursor selects line $\ell$, path $p$, and directed interval $\langle a,h\rangle$. Let

\[
  \resolve(D_\ell,p)=\langle R,k,K\rangle
\]

where $R$ is the focused sequence, $k$ records whether it is a line or slot, and $K$ is the zipper context. Normalize the interval by

\[
  i=\min(a,h),\qquad j=\max(a,h).
\]

Then decompose

\[
  R=L\mathbin{+\!+}M\mathbin{+\!+}U,
  \qquad |L|=i,\quad |M|=j-i.
\]

Most edit rules replace $M$ with a sequence $V$ and rebuild the line:

\[
  D_\ell'=\plug(K,L\mathbin{+\!+}V\mathbin{+\!+}U).
\]

This is the structural analogue of a text editor's splice operation. Unlike a raw string splice, it is constrained by the focus kind: when the entire focused recursive slot is removed, a fresh hole must be inserted.

## Freshening

Templates may contain holes. Inserting the same template twice must not duplicate their identities. Define a state-threading freshening operation

\[
  \mathsf{freshen}:\mathsf{Expr}\times\mathbb N
  \to\mathsf{Expr}\times\mathbb N.
\]

It traverses structurally. At an atom it copies the atom and leaves the counter unchanged. At a hole it emits $h_n$ and returns $n+1$. At a composite node it freshens child slots from left to right, threading the counter through the traversal.

For a sequence $V=[e_1,\ldots,e_m]$, the lifted operation is

\[
  \mathsf{freshenSeq}(V,n)=(V',n').
\]

Two properties are required.

**Shape preservation.** Erasing hole IDs from $V$ and $V'$ yields the same syntax shape.

**Freshness.** If $S$ is valid, then every hole ID introduced in $V'$ is absent from $S$, and the introduced IDs are pairwise distinct.

The implementation obtains freshness from the `nextHole` invariant and deterministic preorder traversal.

## Insertion

Let

\[
  \mathsf{freshenSeq}(V,n)=(V',n').
\]

The insertion rule is

\[
\frac{
  \resolve(D_\ell,p)=\langle R,k,K\rangle
  \qquad R=L\mathbin{+\!+}M\mathbin{+\!+}U
  \qquad \mathsf{freshenSeq}(V,n)=(V',n')
}{
  \langle D,\langle\ell,p,a,h\rangle,n\rangle
  \xrightarrow{\mathsf{Insert}(V)}
  \langle D[\ell:=\plug(K,L\mathbin{+\!+}V'\mathbin{+\!+}U)],c',n'\rangle
}
\]

where $c'$ selects the first hole in $V'$ when one exists and otherwise places a caret immediately after $V'$. The path of a nested first hole is adjusted by the insertion offset $|L|$ only at its first path step.

Insertion subsumes replacement because $M$ is the current selection. Typing into a selected hole therefore removes that hole and inserts the new atom. Inserting into a caret uses $M=[]$.

### Insertion preservation

Assume $\Valid(S)$ and the command payload $V$ is structurally valid. Freshening preserves constructor validity and establishes unique IDs. Replacing a subinterval of a valid sequence by a non-empty valid sequence preserves validity. At a line focus, a valid sequence may be empty only if the payload were empty, which the command type forbids. At a slot focus the replacement remains non-empty because $V'$ is non-empty. Plugging preserves ancestor validity by induction over crumbs. The computed cursor points either to a freshly inserted hole or a boundary in the rebuilt focus. Thus $\Valid(S')$.

## Horizontal movement

Movement changes only the cursor. Its rules follow the cases stated in the zipper chapter. Representative rightward rules are:

### Collapse a selection

\[
\frac{a\ne h\qquad j=\max(a,h)}
 {\langle D,\langle\ell,p,a,h\rangle,n\rangle
  \xrightarrow{\mathsf{Move}(\rightarrow)}
  \langle D,\langle\ell,p,j,j\rangle,n\rangle}.
\]

### Enter the first child

If $a=h=i$, $R[i]=e$, and the first declared child of $e$ is $f$:

\[
\frac{\mathsf{childFields}(e)=f::F}
 {\langle D,\langle\ell,p,i,i\rangle,n\rangle
  \xrightarrow{\mathsf{Move}(\rightarrow)}
  \langle D,\langle\ell,p\mathbin{+\!+}[(i,f)],0,0\rangle,n\rangle}.
\]

### Cross an atom

\[
\frac{R[i]=e\qquad\mathsf{childFields}(e)=[]}
 {\langle D,\langle\ell,p,i,i\rangle,n\rangle
  \xrightarrow{\mathsf{Move}(\rightarrow)}
  \langle D,\langle\ell,p,i+1,i+1\rangle,n\rangle}.
\]

### Ascend after a parent

At the end of a slot whose path ends in $(q,f)$, when $f$ is the final child of the parent:

\[
\frac{i=|R|\qquad p=p_0\mathbin{+\!+}[(q,f)]
      \qquad f=\mathsf{last}(\mathsf{childFields}(e_q))}
 {\langle D,\langle\ell,p,i,i\rangle,n\rangle
  \xrightarrow{\mathsf{Move}(\rightarrow)}
  \langle D,\langle\ell,p_0,q+1,q+1\rangle,n\rangle}.
\]

Leftward rules are the order duals. At document boundaries movement is a no-op rather than an error. Because movement uses only valid boundaries and declared child fields, it preserves cursor validity.

## Hole jumps

Let $H(D_\ell)=[q_0,\ldots,q_{m-1}]$ be the holes of the active line ordered by structural traces. Let $t(c,d)$ be the boundary trace derived from cursor $c$ and direction $d$. A forward jump chooses

\[
  q=\min\{q_r\mid\mathsf{trace}(q_r)>t(c,+)\},
\]

or $q_0$ if the set is empty. A backward jump chooses the greatest trace below $t(c,-)$, excluding the currently selected hole where appropriate, and wraps to $q_{m-1}$. The resulting cursor selects exactly the chosen hole node.

When a line has no holes, the command is a no-op. Hole jumps do not cross lines in the reference implementation; a document-wide variant could order traces by prefixing the line number.

## Deletion

Backspace has four semantically distinct cases.

### Delete a non-empty selection

If $i<j$, remove $R[i:j)$. At a top-level line, the result may be empty. At a recursive slot, if removal would make the slot empty, replace the removed content with one fresh hole and select it.

Formally, define

\[
V=
\begin{cases}
[] & \text{if }k=\mathsf{line}\text{ or }L\mathbin{+\!+}U\ne[],\\
[\mathsf{Hole}(h_n)] & \text{if }k=\mathsf{slot}\text{ and }L\mathbin{+\!+}U=[].
\end{cases}
\]

The reconstructed focus is $L\mathbin{+\!+}V\mathbin{+\!+}U$.

### Enter a non-empty preceding structure

At a caret $i>0$, let $e=R[i-1]$. If $e$ has recursive fields and is not an “empty structure,” backspace is non-destructive: it moves to the end of $e$'s final child. An empty structure is one whose present children consist solely of holes. This rule prevents accidental destruction of a filled fraction or root at its outer boundary.

### Delete a preceding atom or empty structure

If the previous expression is atomic, a hole, or a composite whose children contain no entered content, remove it using the selection-deletion rule. Deleting the sole member of a slot therefore restores a fresh hole.

### Remove a blank line

At the start of an empty top-level line, if the document has another line, remove the active line and move to the end of the preceding line. A document always retains at least one line.

These rules embody a useful editor policy: destructive deletion acts locally only after navigation has exposed the interior of a filled structure. The policy is not forced by the datatype, but it is made precise by the transition system.

## Structural selection growth

The `Grow` command is deterministic.

- At a caret inside a non-empty sequence, select the expression immediately to the left when possible; at the start, select the first expression.
- If a proper selection does not cover the entire focused sequence, select the entire sequence.
- If the focused sequence is already fully selected and the path is non-empty, ascend and select the containing parent expression.
- At a fully selected root line, perform no change.

Anchor/head direction records whether the first selected token was reached leftward or rightward, but normalization makes subsequent structural wrapping independent of direction.

## Function wrapping

For a syntactically valid function name $f$, `WrapFn(f)` behaves as follows.

- With a non-empty selection $M$, replace $M$ by $\mathsf{Function}(f,M)$ and place the caret after the new node.
- With a caret, allocate a fresh hole, replace the empty interval by $\mathsf{Function}(f,[h_n])$, and select the hole in the argument slot.

The implementation accepts names matching

\[
  \texttt{[A-Za-z][A-Za-z0-9']*}.
\]

For typesetting clarity, this means an ASCII letter followed by zero or more ASCII letters, digits, or apostrophes. The check is editor-level lexical validation, not lookup in a mathematical signature.

## Script attachment

`AttachScript(pos,content)` first chooses a base.

- A non-empty selection is the base.
- At a caret with a preceding expression, the preceding expression is the base.
- At the start of a sequence, a fresh hole is the base.

The attachment is either a freshened supplied slot or a new hole with expected class `index`. If the base is a single existing script node, the command updates or adds the requested attachment while preserving the other one. Otherwise it creates a new script whose base is the selected sequence.

The key structural rule is that the base is moved *inside* the new script node. The source's sibling-postfix convention is not retained. This gives an idempotent update behavior for repeated use: attaching a subscript to a superscripted expression produces one script node with both fields rather than nested or adjacent script fragments.

The resulting cursor selects the first hole in the new attachment if present, otherwise moves after the scripted expression.

## Accent application

`Accent(k)` follows the same target selection policy as scripts but differs in composition.

- A non-empty selection becomes the body.
- Otherwise the preceding expression becomes the body.
- At a sequence start, a fresh hole becomes the body.

The result is one `Accent` node. This rule corrects the source-level inconsistency in which documentation says that an accent acts on the previous node, while the no-selection implementation merely inserts an empty accent template.

Accents may nest because composition order matters: $\widehat{\bar{x}}$ and $\bar{\widehat{x}}$ are distinct trees. The editor does not collapse them.

## New lines and direct cursor setting

`NewLine` inserts an empty line immediately after the active line and moves to its start. It does not split the current line. A separate `SplitLine` command could be defined by splicing the root line at the caret; it is not part of the reconstructed parity core.

`SetCursor(c')` is a checked administrative command. It leaves the document unchanged and succeeds only when the supplied line, path, anchor, and head are valid. The browser adapter uses it for mouse selection. Persisted cursors pass through the same validation boundary.

## Determinism

**Theorem 5.1 (determinism).** For every valid state $S$ and command $C$, there is at most one result $r$ such that $\mathsf{reduce}(S,C)=r$.

**Proof.** `reduce` is defined by exhaustive case analysis on the discriminant of $C$. Each branch invokes deterministic sequence operations, path resolution, structural traversal, and fresh allocation from the single counter in $S$. Every conditional has a unique Boolean outcome; every trace order is total on finite integer lists; and every error is returned at the first specified failing check. Hence the computed `Result` is unique. $\square$

This theorem concerns the pure core. Browser event ordering, long-press timers, clipboard effects, and persistence scheduling are outside the reducer and must be specified separately by the adapter.

## Preservation

**Theorem 5.2 (successful-transition preservation).** If $\Valid(S)$ and

\[
  \mathsf{reduce}(S,C)=\Ok(S'),
\]

then $\Valid(S')$.

**Proof sketch.** Proceed by cases on $C$.

- `SetCursor`, movement, jumps, and growth do not change the document. Their computed positions are checked by `commit`, so cursor validity holds.
- `Insert` freshens holes, substitutes a valid non-empty payload, and plugs through valid crumbs. Freshness and slot non-emptiness are preserved.
- `Backspace` either changes only the cursor, removes a top-level interval, or replaces an emptied slot with a fresh hole. It never removes the last document line.
- `WrapFn`, `AttachScript`, and `Accent` build constructors through smart constructors over non-empty slots. Their target extraction yields a non-empty body or creates a fresh hole.
- `NewLine` inserts a valid empty line into a non-empty line list.

In every mutating branch, `commit` runs the complete state validator. Thus the executable reducer additionally enforces the theorem dynamically. $\square$

The dynamic validator is not a substitute for the proof: it detects violations at runtime rather than showing they cannot arise. Conversely, the proof sketch is not a machine-checked theorem. The two forms of evidence are complementary.

## Progress and graceful failure

A conventional language progress theorem states that a well-typed term is a value or can step. An editor command may intentionally be a no-op at a boundary, and malformed command payloads may be rejected. The corresponding statement is:

**Theorem 5.3 (total command interpretation).** For every runtime state value $S$ and command value $C$, `reduce(S,C)` terminates with either `Ok(S')` or `Err(e)`; it does not require unchecked path access.

For valid $S$ and a structurally valid command payload, navigation commands always return `Ok`, possibly with $S'=S$. Mutating commands can still return `Err` for lexical constraints such as an invalid function name or for an impossible state introduced through unsafe host-language construction.

## Big-step command traces

For a finite command list $\vec C=[C_1,\ldots,C_m]$, define Kleisli sequencing:

\[
\begin{aligned}
\mathsf{run}(S,[])&=\Ok(S),\\
\mathsf{run}(S,C::\vec C)&=
  \begin{cases}
  \mathsf{run}(S',\vec C) & \mathsf{reduce}(S,C)=\Ok(S'),\\
  \Err(e) & \mathsf{reduce}(S,C)=\Err(e).
  \end{cases}
\end{aligned}
\]

Determinism and preservation lift immediately to successful traces by induction on the list. The randomized test in Chapter 11 generates such traces and validates every intermediate state.

## Separation from interface effects

The source combines edit semantics with React state setters, timers, clipboard code, storage, modal state, and keyboard layout. The reconstruction draws a strict boundary:

\[
  \text{UI event}
  \longrightarrow \text{Command}
  \longrightarrow \mathsf{reduce}
  \longrightarrow \Result(S,E)
  \longrightarrow \text{render/effects}.
\]

A long press is not an editor command; it is an interaction policy that chooses which command to issue. Copying output is not an editor transition; it is an effect over a rendered string. Persistence is not mutation of the syntax; it is encoding and storage of an accepted state. This separation is necessary for deterministic tests and for alternative front ends.

## Chapter summary

The editor is a deterministic transition system over valid configurations. Commands are values, focused edits are zipper-guided splices, templates are freshened, and every successful mutation preserves non-empty slots and unique holes. Deletion, scripts, accents, wrapping, navigation, and structural selection are stated as explicit cases rather than implicit UI behavior. The pure reducer is the central semantic object; interface effects are adapters around it.

## Exercises

1. Add a `SplitLine` command and give its operational rule at a root caret.
2. State the freshness lemma for inserting two copies of the same template consecutively.
3. Show why deletion of the only numerator expression must allocate a hole rather than return an empty array.
4. Prove preservation for `AttachScript` when the base is already a script with the opposite attachment.
5. Define a document-wide hole-jump order and state how wraparound changes.


# Denotational semantics at three distinct levels

## Why “semantics” must be stratified

A mathematics editor sits between three domains that are often conflated.

1. **Editor structure:** fractions, roots, identifiers, groups, scripts, holes, and other presentation constructs.
2. **Concrete output languages:** LaTeX, Typst, Unicode, HTML, MathML, or a visual box tree.
3. **Mathematical objects:** terms, types, morphisms, propositions, proofs, and their denotations in a model.

The source legitimately treats LaTeX, Typst, and Unicode as code-generation backends over one tree. This is a denotational view of the editor syntax in a broad programming-language sense: each backend assigns an output value to every constructor. It is not yet the object-level denotation of mathematics. A renderer can assign text to an ill-typed formula, and a visually identical string can receive different meanings under different signatures.

A mathematically sound architecture therefore uses three maps:

\[
\begin{CD}
\mathsf{EditorExpr} @>{\mathsf{render}_b}>> \mathsf{BackendText}_b\\
@V{\mathsf{elaborate}_{\Sigma,\Gamma}}VV @VV{\mathsf{parse}_b}V\\
\mathsf{CoreTerm}_{\Sigma,\Gamma} @>>{\mathsf{pretty}_b}> \mathsf{BackendAST}_b
\end{CD}
\]

and, for typed terms,

\[
  \llbracket-\rrbracket_{\mathcal M,\rho}:
  \mathsf{CoreTerm}_{\Sigma,\Gamma}(\tau)	o\llbracket\tau\rrbracket_{\mathcal M}.
\]

The first map is total over structurally valid editor trees. The second is partial and context-dependent. The third is defined only after typing. The present reconstruction implements the first and specifies the interface for the other two.

![The semantic pipeline separates editing, rendering, elaboration, typing, and model interpretation.](../figures/semantics-pipeline.png){width=96%}

## Syntax algebras

For carrier $B$, an $F$-algebra is a map

\[
  \alpha:F(B)\to B.
\]

Because $\mathsf{Expr}=\mu F$ is the initial $F$-algebra, every algebra $\alpha$ induces a unique homomorphism

\[
  \cata(\alpha):\mathsf{Expr}\to B
\]

satisfying

\[
  \cata(\alpha)\circ\mathsf{in}
  =\alpha\circ F(\cata(\alpha)).
\]

The TypeScript interface `SyntaxAlgebra<A>` is a direct programming representation of this idea. It supplies one operation for each constructor and separate sequence combiners for lines and slots:

```ts
export interface SyntaxAlgebra<A> {
  line(items: readonly A[]): A;
  slot(items: readonly A[]): A;
  atom(atom: Atom): A;
  hole(hole: HoleExpr): A;
  fraction(numerator: A, denominator: A): A;
  root(radicand: A, index: A | undefined): A;
  script(base: A, superscript: A | undefined, subscript: A | undefined): A;
  fn(name: string, argument: A): A;
  group(delimiters: DelimiterPair, body: A): A;
  largeOperator(operator: LargeOperatorKind, lower: A | undefined, upper: A | undefined): A;
  accent(accent: AccentKind, body: A): A;
  annotatedArrow(arrow: ArrowKind, label: A): A;
}
```

`foldExpr`, `foldSlot`, and `foldLine` implement the unique recursive homomorphism. The recursion scheme is written once. Backend definitions cannot accidentally recurse in a different way or omit traversal of a child while still satisfying the interface.

## Rendering as a writer-style algebra

A renderer returns more than text. It returns a pair

\[
  \mathsf{Piece}=\mathsf{Text}\times\mathsf{Issue}^*.
\]

Composition concatenates both text fragments and issue lists. This has the structure of a writer construction over the free monoid of diagnostics. Each backend algebra has carrier `Piece`; the final `RenderResult` adds a backend name and a fidelity classification.

The diagnostic channel is essential. A total renderer should not crash on a catalog miss, but silently emitting an empty string would conceal information loss. Instead the reconstruction returns a readable fallback and an issue such as:

- `unknown-symbol` when no catalog entry exists;
- `unicode-style-fallback` when a mathematical alphabet character lacks a reliable Unicode mapping;
- `backend-fallback` when direct Unicode is used inside another backend because no native spelling is registered.

Fidelity is classified as `exact-structure` when no issues occur and `readable-fallback` otherwise. “Exact structure” means that the backend output reflects every editor constructor according to the backend algebra. It does not mean typographic identity across engines or semantic equivalence after arbitrary external parsing.

## The LaTeX algebra

The LaTeX algebra maps each constructor to a compositional fragment. Representative equations are:

\[
\begin{aligned}
\mathsf{L}(\mathsf{Frac}(n,d))
  &=\mathsf{latexFrac}(\mathsf{L}(n),\mathsf{L}(d)),\\
\mathsf{L}(\mathsf{Root}(r,\varnothing))
  &=\mathsf{latexSqrt}(\mathsf{L}(r)),\\
\mathsf{L}(\mathsf{Root}(r,i))
  &=\mathsf{latexRoot}(\mathsf{L}(i),\mathsf{L}(r)),\\
\mathsf{L}(\mathsf{Script}(b,u,l))
  &=\mathsf{latexScript}(\mathsf{L}(b),\mathsf{L}(u),\mathsf{L}(l)).
\end{aligned}
\]

Braces around the base make script ownership explicit in the output. Function names from a standard set use native operators such as `\sin`; other valid names use `\operatorname`. Groups use `\left` and `\right` with catalogued delimiter pairs. Annotated arrows use dedicated arrow commands rather than the accent machinery.

The renderer escapes user-controlled function and identifier text where needed. This is a syntactic safety property: arbitrary names cannot inject unbalanced command arguments through the supported constructors. It is not a general sanitizer for concatenating renderer output into unrestricted TeX documents.

## The Typst algebra

The Typst backend is written independently rather than obtained by search-and-replace over LaTeX. Fractions, roots, scripts, functions, groups, accents, and arrows have different concrete conventions. Representative equations are:

\[
\begin{aligned}
\mathsf{T}(\mathsf{Frac}(n,d))&=(\mathsf{T}(n))/(\mathsf{T}(d)),\\
\mathsf{T}(\mathsf{Root}(r,i))&=\texttt{root(}\mathsf{T}(i)\texttt{, }\mathsf{T}(r)\texttt{)},\\
\mathsf{T}(\mathsf{Accent}(\mathsf{hat},b))&=\texttt{hat(}\mathsf{T}(b)\texttt{)},\\
\mathsf{T}(\mathsf{Arrow}(q,l))&=\texttt{stretch(arrow)}^{(\mathsf{T}(l))}.
\end{aligned}
\]

Spacing is introduced between folded sequence items and then normalized before punctuation. The catalog may supply a native Typst symbol spelling; otherwise the backend uses the display glyph and records a fallback issue.

Backend syntax changes over time, so a production implementation should regression-test emitted snippets against the supported Typst version. The thesis treats the included renderer as a coherent algebra and labels it a reconstruction, not a complete conformance implementation for every external engine.

## The Unicode algebra

Plain Unicode is not a full two-dimensional mathematics language. It lacks general stacked fractions, arbitrary scalable delimiters, uniform superscripts and subscripts, and portable accent layout. The Unicode backend is therefore a structural linearization with readable fallbacks:

\[
\begin{aligned}
\mathsf{U}(\mathsf{Frac}(n,d))&=(\mathsf{U}(n))/(\mathsf{U}(d)),\\
\mathsf{U}(\mathsf{Root}(r,i))&=\texttt{root[}\mathsf{U}(i)\texttt{](}\mathsf{U}(r)\texttt{)},\\
\mathsf{U}(\mathsf{Script}(b,u,l))&=(\mathsf{U}(b))^{(\mathsf{U}(u))}_{(\mathsf{U}(l))},\\
\mathsf{U}(\mathsf{Arrow}(q,l))&=\texttt{-}\mathsf{U}(l)\;\mathsf{glyph}(q).
\end{aligned}
\]

Mathematical alphabet characters use the Unicode Mathematical Alphanumeric Symbols block where available, with explicit exception tables for legacy code points such as $\mathbb R$ and $\mathcal H$. A character without a reliable mapping is retained in plain form and reported.

The indexed-root rule corrects an information loss in the source, whose Unicode generator renders every root as `√(radicand)` and drops the index. The rebuilt fallback is not beautiful, but it is structurally faithful.

## WYSIWYG as another algebra

The direct visual renderer can be understood as an algebra whose carrier is a layout tree rather than a string. Let `Box` contain horizontal sequences, vertical stacks, glyph boxes, scalable delimiters, rule boxes, script boxes, and focus annotations. Then

\[
  \alpha_{\mathsf{box}}:F(\mathsf{Box})\to\mathsf{Box}
\]

assigns layouts to constructors:

- a fraction stacks numerator and denominator around a horizontal rule;
- a root combines a radical glyph, overbar, radicand, and optional index;
- a script places attachments relative to a base box;
- a group stretches delimiter boxes around its body;
- an accent overlays a mark over its body;
- an annotated arrow stretches a shaft and positions a label.

Focus rendering is not purely a fold over syntax because it also depends on cursor paths and selection boundaries. It can nevertheless be factored as a fold producing address-annotated boxes followed by a decoration pass keyed by the cursor. The source's React `RowView` and `NodeView` combine these two concerns; a production reconstruction should separate them.

## Fold fusion and shared analyses

Once computations are expressed as folds, standard algebraic laws become useful. Suppose $h:B\to C$ is an algebra homomorphism from $\alpha$ to $\beta$:

\[
  h\circ\alpha=\beta\circ F(h).
\]

Then the fusion law gives

\[
  h\circ\cata(\alpha)=\cata(\beta).
\]

Operationally, a post-processing pass can be fused into a single syntax traversal when it commutes with constructors. For example, a renderer that produces strings and a later length computation can be replaced by an algebra that computes lengths directly, avoiding intermediate strings. The included `sizeAlgebra` and `holeOrderAlgebra` demonstrate non-rendering folds.

The size algebra has carrier $\mathbb N$ and counts expression constructors:

\[
\begin{aligned}
|\mathsf{Atom}|&=1,\qquad |\mathsf{Hole}|=1,\\
|\mathsf{Frac}(n,d)|&=1+|n|+|d|,\\
|\mathsf{Script}(b,u,l)|&=1+|b|+|u|+|l|,
\end{aligned}
\]

omitting absent attachments. The hole-order algebra has carrier $H^*$ and concatenates child results in canonical traversal order. The fact that the same fold interface supports text, metrics, and navigation metadata is evidence that it captures the datatype's recursion scheme rather than one renderer's implementation accident.

## Round trips and adequacy

It is tempting to require

\[
  \mathsf{parse}_b(\mathsf{render}_b(e))=e.
\]

This exact round-trip law is too strong for the current backends.

- The reconstruction does not include parsers.
- LaTeX and Typst have many equivalent spellings.
- Backend strings may omit editor-only data such as hole identities and expectation tags.
- Unicode fallbacks are intentionally lossy with respect to typography.
- External parsers may normalize associativity, spacing, or delimiters.

A realistic adequacy criterion introduces an erasure or normalization map $q$ from editor syntax to backend-representable structure and an equivalence relation $\simeq_b$:

\[
  \mathsf{parse}_b(\mathsf{render}_b(e))\simeq_b q(e).
\]

For holes, $q$ may erase unique IDs while retaining placeholder positions. For styled identifiers, it may preserve semantic style even when a Unicode engine falls back. A future parser test suite should state the exact quotient instead of using raw string equality.

## Presentation-neutral intermediate representation

The reconstructed editor tree is already substantially presentation-neutral: a fraction is not stored as `\frac`, a blackboard identifier is not stored as a Unicode code point, and a labelled arrow is not an accent command. Nevertheless, it remains a notation-level representation. It contains groups and accents that may be semantically transparent, and it represents juxtaposition as a sequence without deciding whether it means multiplication, application, composition, or concatenation.

An explicit `MathIR` layer can normalize editor-specific details while preserving ambiguity:

\[
\begin{aligned}
M::={}&\mathsf{Name}(x,s)
\mid\mathsf{Number}(n)
\mid\mathsf{Symbol}(id)
\mid\mathsf{Hole}(h,\epsilon)\\
&\mid\mathsf{Fraction}(M^+,M^+)
\mid\mathsf{Root}(M^+,\mathsf{Opt}(M^+))\\
&\mid\mathsf{Script}(M^+,\mathsf{Attachments})
\mid\mathsf{ApplyName}(n,M^+)\\
&\mid\mathsf{Delimited}(d,M^+)
\mid\mathsf{LargeOp}(o,\ldots)
\mid\mathsf{Accent}(k,M^+)\\
&\mid\mathsf{Arrow}(q,M^+)
\mid\mathsf{Sequence}(M^*).
\end{aligned}
\]

The current `Expr` type can be viewed as this `MathIR`; a visual adapter may add transient layout data without changing it. The important architectural law is that no backend string becomes canonical storage.

## Elaboration

Object-level meaning begins with a signature $\Sigma$ and context $\Gamma$. Elaboration is a partial, diagnostic-producing relation

\[
  \Sigma;\Gamma\vdash e\rightsquigarrow t:\tau\;\dashv\;\mathcal C,
\]

meaning that editor fragment $e$ elaborates to core term $t$ of type $\tau$ while generating constraints $\mathcal C$. Ambiguous sequences require precedence rules, notation declarations, or user disambiguation. Holes elaborate to metavariables with local contexts. A symbol catalog ID is resolved through $\Sigma$, not through its glyph alone.

For example, the editor sequence displaying

\[
  F\dashv G:\mathcal C\rightleftarrows\mathcal D
\]

might elaborate under a category-theory notation environment to a declaration asserting functors

\[
  F:\mathcal C\to\mathcal D,
  \qquad
  G:\mathcal D\to\mathcal C,
\]

plus an adjunction witness. Under a different environment it might be rejected or parsed differently. The presentation tree does not choose on its own.

## Typed denotation

After elaboration and constraint solving, denotational semantics is conventional. For each well-formed context $\Gamma$ and type $\tau$, an interpretation supplies sets, domains, objects, or types

\[
  \llbracket\Gamma\rrbracket_{\mathcal M},
  \qquad
  \llbracket\tau\rrbracket_{\mathcal M},
\]

and a term judgment induces

\[
  \llbracket\Gamma\vdash t:\tau\rrbracket_{\mathcal M}:
  \llbracket\Gamma\rrbracket_{\mathcal M}	o
  \llbracket\tau\rrbracket_{\mathcal M}.
\]

For simply typed lambda calculus, this may be a function between sets or domains. For dependent type theory, types may be interpreted in a category with families, contextual category, comprehension category, or another suitable model. For category-theoretic notation, the core term might elaborate into a formalization whose denotation lives in a selected category.

The editor's structural soundness theorem and the core language's type soundness theorem are separate. Their composition requires an elaboration theorem:

\[
  \mathsf{elaborate}(e)=\Ok(t:\tau)
  \quad\Longrightarrow\quad
  \Gamma\vdash t:\tau.
\]

Only then may the model interpretation be applied.

## Naturality across backends

A useful design objective is that backend renderers depend only on semantic syntax, not on interface history. If $\phi$ is a syntax-preserving renaming of hole IDs, then visible rendering should be invariant:

\[
  \mathsf{render}_b(\phi(e))=\mathsf{render}_b(e),
\]

because hole IDs are editor metadata and all holes render as the same placeholder. More generally, each renderer should be natural with respect to structure-preserving maps on atoms and catalog interpretations. This is a practical form of parametricity: the recursive scheme is fixed, while atom meanings vary by backend.

The source partially achieves this by using the same tree for three generators. The reconstruction strengthens it by centralizing traversal in `foldExpr` and moving all backend choices into algebras and the symbol catalog.

## Chapter summary

There are three semantic levels: editor structure, backend rendering, and typed mathematical meaning. Backend generators are catamorphisms into a writer-like carrier of text and diagnostics. WYSIWYG layout is another algebra. Total rendering does not imply losslessness, so fidelity issues are explicit. Object-level denotation requires signature-dependent elaboration, typing, and a model; the notation tree alone cannot supply it. This stratification is the key qualification behind any claim of mathematical soundness.

## Exercises

1. Define a MathML algebra for fractions, roots, scripts, and groups.
2. Give an example showing why exact string round trips are too strong even for LaTeX.
3. State an erasure map that removes hole IDs but preserves hole positions.
4. Show how the size algebra follows from the generic fold interface.
5. Give two different elaborations of the same juxtaposition sequence under different notation environments.


# Type-theoretic reconstruction

## Three layers of types

The phrase “type theory” applies to three different layers of this system.

1. **Host-language types** describe the implementation data and API.
2. **Editor invariants** refine host-language values with propositions such as non-empty slots and valid paths.
3. **Object-language types** classify the mathematics being entered.

The supplied JavaScript component uses the first layer only informally. The reconstruction implements a disciplined TypeScript approximation to the first two and specifies a path to the third. A dependently typed implementation could internalize more of the invariants, but no host type alone can infer the mathematical theory intended by arbitrary notation.

## Extrinsic and intrinsic syntax

An **extrinsic** representation defines raw syntax first and a separate predicate for well-formedness. The original runtime objects are extrinsic in a weak sense: any object with fields is admitted by JavaScript, and the intended conditions are conventions. The reconstruction's decoded JSON remains extrinsic:

\[
  \mathsf{RawValue}
  \quad\text{with predicate}\quad
  \Valid_D:\mathsf{RawValue}\to\mathsf{Prop}.
\]

An **intrinsic** representation makes structural conditions part of the datatype. Non-empty recursive slots and non-vacuous scripts are examples. In an ideal dependent language one may define:

\[
\begin{aligned}
\mathsf{Slot}&=\Sigma(n:\mathbb N).\;\mathsf{Expr}^{\mathsf{Fin}(n+1)},\\
\mathsf{Attachments}&=
  \mathsf{Sup}(\mathsf{Slot})
  +\mathsf{Sub}(\mathsf{Slot})
  +\mathsf{Both}(\mathsf{Slot},\mathsf{Slot}).
\end{aligned}
\]

Then an empty slot or attachment-free script has no constructor. The TypeScript tuple

```ts
type NonEmpty<T> = readonly [T, ...T[]];
```

approximates the same idea, although unsafe casts and unchecked JSON can still bypass it.

A balanced architecture uses intrinsic types for stable local structure and extrinsic validators for global or boundary conditions. Global uniqueness of hole IDs is awkward to encode directly in ordinary TypeScript and is therefore validated over a document. A proof assistant could represent a document together with a no-duplicates proof, but the operational cost and ergonomic tradeoffs should be considered.

## Indexed paths

The current path type is unindexed:

\[
  \mathsf{Path}=\mathsf{List}(\mathbb N\times\mathsf{Field}).
\]

Its validity depends on a particular root. A dependently typed formulation can index paths by their source and target sequence. Let `SeqKind` distinguish lines and slots. One possible family is

\[
  \mathsf{PathTo}:\prod_{R:\mathsf{Line}}\mathsf{SeqKind}\to\mathsf{Type}.
\]

The root constructor is

\[
  \mathsf{here}:\mathsf{PathTo}(R,\mathsf{line}),
\]

and descent carries evidence that an index is in bounds and a field exists:

\[
\frac{
  i:\mathsf{Fin}(|R|)
  \qquad f:\mathsf{ChildField}(R_i)
  \qquad p:\mathsf{PathTo}(\mathsf{child}(R_i,f),k)
}{
  \mathsf{down}(i,f,p):\mathsf{PathTo}(R,k)}.
\]

This direction encodes a path from the root to a target. An alternative stores a typed zipper directly:

\[
  \mathsf{CursorAt}(R)=\Sigma(S:\mathsf{Sequence}).\;\mathsf{Context}(S,R)\times\mathsf{Boundary}(S)^2.
\]

Here `Boundary(S)` is `Fin(|S|+1)`, so out-of-range selections are unrepresentable. Serialization erases the proofs to indices and field tags; decoding reconstructs them through a decision procedure.

## Refinement types for editor state

The ideal editor state is a refinement

\[
  \mathsf{State}=\{s:\mathsf{RawState}\mid\Valid(s)\}.
\]

A command is then

\[
  \mathsf{reduce}:\mathsf{State}\to\mathsf{Command}\to
  \Result(\mathsf{State},\mathsf{EditError}).
\]

The preservation theorem is reflected in the codomain: successful results already contain validity evidence. Some commands can be total on valid states and require no error branch. For example, bounded horizontal movement can return a state, treating document boundaries as no-ops. Commands with external payloads, such as setting an arbitrary cursor or decoding pasted templates, still require failure.

The executable TypeScript core uses a weaker but recognizable discipline:

- immutable readonly records;
- discriminated unions for constructors and commands;
- non-empty tuple aliases for slots;
- smart constructors for scripts and slots;
- checked `Result` values for path operations and decoding;
- a validation gate before and after reducer transitions.

This is “parse, do not validate” only in part: trusted constructors parse payloads into refined shapes, while the general validator remains necessary at untyped boundaries.

## Holes as metavariables

At the editor layer a hole is a structural placeholder. At an object-language layer it can elaborate to a metavariable. In dependent type theory, a metavariable is not merely a question mark; it has a local context and expected type:

\[
  ?m:[\Gamma]\vdash A.
\]

Its eventual solution must be a term $t$ such that

\[
  \Gamma\vdash t:A.
\]

The editor's hole ID supplies the stable identity $m$. Its lightweight expectation can guide initial elaboration, but only the elaborator can determine the full local type. For example, the denominator hole in a fraction may be expected to elaborate to a numeric expression in one notation environment and to a morphism or proof term in another.

A typed hole record might therefore be:

\[
  \mathsf{Meta}=
  \Sigma(\Gamma:\mathsf{Context}).
  \Sigma(A:\mathsf{Type}(\Gamma)).
  \mathsf{MetaId}.
\]

The editor tree should not store such semantic context directly unless it is committed to one object language. A clean architecture stores stable editor holes and lets the elaboration session maintain a map

\[
  \mathsf{MetaId}\rightharpoonup(\Gamma,A,\mathsf{constraints}).
\]

Edits invalidate or update this map incrementally.

## Bidirectional elaboration

Mathematical notation is highly ambiguous. Bidirectional typing provides a practical structure for elaboration by separating synthesis and checking judgments:

\[
  \Gamma\vdash e\Rightarrow A
  \qquad\text{and}\qquad
  \Gamma\vdash e\Leftarrow A.
\]

In synthesis mode, the elaborator infers a type. In checking mode, an expected type guides interpretation. Editor constructors can exploit this distinction.

- A numeric literal usually synthesizes a type through overloaded-literal resolution.
- A function application synthesizes after resolving the function name and checking its argument.
- A hole in checking mode becomes a metavariable of the expected type.
- A script may elaborate according to a notation declaration associated with its base type.
- A fraction may mean field division, a rational literal, a quotient, or a displayed inference rule; the expected type and notation scope determine which.

A generic elaboration interface is

\[
\begin{aligned}
\mathsf{synth}&:\Sigma\to\Gamma\to\mathsf{MathIR}	o
\Result(\Sigma(A:\mathsf{Type}).\mathsf{Term}(A)\times\mathsf{Constraints},E),\\
\mathsf{check}&:\Sigma\to\Gamma\to\mathsf{MathIR}\to A\to
\Result(\mathsf{Term}(A)\times\mathsf{Constraints},E).
\end{aligned}
\]

The editor core does not implement these functions. It is designed so that they can consume stable, backend-independent syntax.

## A minimal object language

To make the boundary concrete, consider a simply typed core language with base types $\iota$, function types, variables, constants, abstraction, and application:

\[
\begin{aligned}
A,B&::=\iota\mid A\to B,\\
t,u&::=x\mid c\mid\lambda x:A.t\mid t\;u.
\end{aligned}
\]

Typing rules include

\[
\frac{x:A\in\Gamma}{\Gamma\vdash x:A}
\qquad
\frac{\Gamma,x:A\vdash t:B}{\Gamma\vdash\lambda x:A.t:A\to B}
\qquad
\frac{\Gamma\vdash t:A\to B\qquad\Gamma\vdash u:A}{\Gamma\vdash t\;u:B}.
\]

An editor function node `f(argument)` might elaborate to application once $f$ resolves to a constant or variable. A sequence of adjacent expressions might elaborate using an application-precedence rule. A superscript could be desugared through a notation declaration for exponentiation. None of these interpretations follows from the structural datatype alone; each is a rule in the elaborator.

For category-theoretic notation, a more suitable core includes universes of objects and morphisms, source and target indices, composition, identities, functors, natural transformations, and adjunction data. Intrinsic typing can enforce composability:

\[
  \mathsf{Hom}:\mathsf{Obj}\to\mathsf{Obj}\to\mathsf{Type},
\]

\[
  (\circ):\mathsf{Hom}(B,C)\to\mathsf{Hom}(A,B)\to\mathsf{Hom}(A,C).
\]

The displayed composition $g\circ f$ is sound only after elaboration establishes matching middle object $B$.

## Substitution and editing

Object-language substitution and editor replacement are distinct operations.

Editor replacement substitutes a sequence into a structural focus:

\[
  \mathsf{replace}_p(R,V).
\]

It is capture-free because editor syntax does not yet bind variables. Object-language substitution

\[
  t[x:=u]
\]

must respect binders and alpha-equivalence. A future editor with explicit binders could represent scopes intrinsically using de Bruijn indices, locally nameless syntax, or higher-order abstract syntax. At that point, editor operations such as moving a subtree across a binder would require renaming or rejection.

The present reconstruction deliberately avoids claiming binder-aware semantics. Function nodes are notation forms with names and arguments, not lambda binders. This keeps structural editing independent from any one formal language.

## Type preservation versus editor preservation

Two preservation theorems must be distinguished.

**Editor preservation** states:

\[
  \Valid(S)\land S\xrightarrow{C}S'
  \Longrightarrow\Valid(S').
\]

It holds for the reconstructed reducer.

**Object-language type preservation** states, for an evaluation relation:

\[
  \Gamma\vdash t:A\land t\to t'
  \Longrightarrow\Gamma\vdash t':A.
\]

This is a theorem about executing or reducing mathematical/program terms, not about editing them. An edit may intentionally turn an elaborating expression into one with holes or errors. Interactive systems therefore maintain a weaker incremental property: after every structural edit, elaboration either returns a typed term with metavariables or a finite set of localized diagnostics; it must not corrupt the editor state.

A useful typed-edit theorem is:

\[
\frac{
  \Gamma\vdash e\rightsquigarrow t:A
  \qquad S(e)\xrightarrow{C}S(e')
}{
  \mathsf{elaborate}(e')=\Ok(t':A')\;\text{or}\;\Err(\Delta)
}
\]

where $\Delta$ contains source locations expressible through editor paths. This is robustness, not preservation of the original type.

## Proof-relevant diagnostics

A checked decoder currently returns textual issues. A stronger design returns evidence of where and why a judgment failed. For example:

\[
  \mathsf{PathError}
  =\mathsf{IndexOutOfBounds}(d,i,n)
   +\mathsf{FieldMismatch}(d,k,f)
   +\mathsf{EmptySlot}(d,f).
\]

Each constructor carries enough data to reproduce the failed premise of a resolution rule. Type errors can be represented similarly as failed derivation objects. This approach supports precise highlighting, repair suggestions, and tests that assert error classes rather than brittle message strings.

## Decidable validity

All editor structural invariants are decidable. Constructor tags and finite fields are enumerable; slot non-emptiness and selection bounds are finite checks; path resolution terminates by path length; hole uniqueness is decidable by finite-set insertion. Thus there is a decision procedure

\[
  \mathsf{decValid}:\prod_{s:\mathsf{RawState}}
  \mathsf{Dec}(\Valid(s)),
\]

where

\[
  \mathsf{Dec}(P)=P+\neg P.
\]

The TypeScript validator returns all found issues rather than a proof or refutation. A proof-assistant implementation could make the positive branch carry the evidence required to construct `State` and the negative branch carry a counterexample path.

## Versioned decoding as refinement introduction

Persistence stores untrusted bytes. Decoding has two stages:

\[
  \mathsf{bytes}\xrightarrow{\mathsf{JSON.parse}}\mathsf{RawValue}
  \xrightarrow{\mathsf{decodeV1}}\Result(\mathsf{State},\mathsf{DecodeError}).
\]

The second stage checks the schema version, constructor discriminants, primitive payloads, child slots, hole identities, cursor path, selection bounds, and counter. Successful decoding is the introduction rule for the refined state type at the persistence boundary.

Versioning is semantically necessary. Changing postfix scripts into base-owning script nodes changes the serialized abstract syntax. A version tag allows an explicit migration

\[
  \mathsf{migrate}_{0\to1}:\mathsf{State}_0\to\Result(\mathsf{State}_1,E)
\]

instead of silently interpreting old objects under new invariants. The included codec supports version 1 and rejects unknown versions; a production migration from the supplied component would need to decide how to associate each sibling script with a base and how to repair unattached scripts.

## Mechanization strategy

A complete formalization can be staged.

### Stage 1: syntax and zipper

Define `Expr`, non-empty slots, paths, and zippers in Lean, Agda, or Coq. Prove resolution/plug lens laws and decidability of validity.

### Stage 2: command semantics

Define the reducer as a function over refined states. Prove determinism and preservation. Extract or mirror test vectors for the TypeScript implementation.

### Stage 3: codecs and correspondence

Formalize a simplified JSON AST and prove that successful decoding yields a valid state. Establish a correspondence relation between TypeScript values and formal values.

### Stage 4: object-language elaboration

Select one formal theory, define MathIR elaboration, and prove elaboration soundness. This stage is theory-specific and should not be mixed into the general editor core.

### Stage 5: verified rendering subset

Define backend ASTs rather than raw strings, prove total translation, then rely on a small pretty-printer. Round-trip or adequacy theorems can be stated against formal parsers for selected subsets.

## Chapter summary

Type theory clarifies which guarantees belong where. The structural datatype can intrinsically exclude empty slots and vacuous scripts; paths and boundaries can be indexed by their roots; global uniqueness and untrusted decoding remain refinement checks; holes can later elaborate to contextual metavariables; and object-level typing requires a separate language and signature. Editor preservation is not object-language type preservation. The reconstruction is designed to support both without conflating them.

## Exercises

1. Define an indexed boundary type for a sequence of length $n$.
2. Explain how a proof-producing decoder differs from a Boolean validator.
3. Give an example in which an edit preserves editor validity but destroys object-language typability.
4. Formulate a typed metavariable for a hole under context $x:A,y:B(x)$.
5. Sketch a migration from a sibling postfix script representation to a base-owning script representation, including an ambiguous case.


# Category-theoretic organization of the editor

## Category theory as architecture, not decoration

The editor can be described without category theory, but categorical language reveals why several independently useful patterns fit together. The abstract syntax is an initial algebra. Renderers and analyses are catamorphisms. The signature is a container. Cursor contexts arise from a derivative. Checked paths behave as partial lenses. Commands compose as Kleisli arrows for an exception effect. History is a zipper over a sequence of states. These descriptions are valuable only insofar as they constrain interfaces, expose laws, and prevent accidental coupling.

![Categorical structures align the syntax, focus, transitions, effects, and backends.](../figures/architecture.png){width=96%}

## The syntax functor and its initial algebra

Let $F$ be the strictly positive endofunctor defined in Chapter 4. On a function $f:X\to Y$, $F(f)$ maps $f$ over every recursive child while preserving constructor parameters. For example,

\[
  F(f)(\mathsf{Frac}(n,d))
  =\mathsf{Frac}(\mathsf{map}^+(f,n),\mathsf{map}^+(f,d)).
\]

Identity and composition laws follow from the corresponding laws for finite-list mapping:

\[
  F(\mathsf{id})=\mathsf{id},
  \qquad
  F(g\circ f)=F(g)\circ F(f).
\]

The constructor map

\[
  \mathsf{in}:F(\mathsf{Expr})\to\mathsf{Expr}
\]

forms an $F$-algebra. Initiality says that for every algebra $\alpha:F(A)\to A$, there is a unique homomorphism $h:\mathsf{Expr}\to A$ such that

\[
  h\circ\mathsf{in}=\alpha\circ F(h).
\]

This unique $h$ is the catamorphism $\cata(\alpha)$. In software terms, once the constructor cases are supplied, the recursion is determined. The generic fold is therefore not only code reuse; it is the universal map out of the syntax algebra.

Lambek's lemma implies that the structure map of an initial algebra is an isomorphism:

\[
  F(\mathsf{Expr})\cong\mathsf{Expr}.
\]

Informally, every expression can be uniquely exposed as one layer of constructor shape containing recursive expressions, and every such layer can be folded back into an expression. The TypeScript discriminated union and its exhaustive switch implement this expose/fold intuition, though TypeScript does not prove the isomorphism.

## Containers

A container is specified by a set of shapes $S$ and a family of position sets $P:S\to\mathbf{Set}$. Its extension is

\[
  \llbracket S\triangleleft P\rrbracket(X)
  =\Sigma(s:S).\;P(s)\to X.
\]

Each editor constructor determines a shape: fraction, indexed root, unindexed root, superscript-only script, and so forth, together with non-recursive parameters such as delimiter or operator IDs. Positions identify child-expression locations. Because a slot contains a positive finite number of expressions, a shape also contains the arities of its child sequences, while positions identify a field and an index within that field.

For a fraction with numerator length $m+1$ and denominator length $n+1$, positions are

\[
  \mathsf{Fin}(m+1)+\mathsf{Fin}(n+1).
\]

For a root without index and radicand length $r+1$, positions are $\mathsf{Fin}(r+1)$. A script shape records which attachments are present and the lengths of base and attachments.

The container view provides three benefits.

1. **Strict positivity is manifest.** Recursive expressions occupy positions; they do not occur contravariantly.
2. **Generic mapping is canonical.** A function on child expressions acts by postcomposition in each position map.
3. **Positions support focus.** Selecting one recursive occurrence amounts to choosing a position in a shape.

The concrete `childFields` function is a coarser reflection than the full container position family because it lists fields but not indices within their sequences. Combining a field with a sequence index recovers a position.

## Derivatives and one-hole contexts

For a container, the derivative has shapes consisting of an original shape together with a distinguished position. The remaining positions form the context around a hole. Symbolically,

\[
  (S\triangleleft P)'=
  \left(\Sigma(s:S).P(s)\right)
  \triangleleft
  \left(\lambda(s,p).P(s)\setminus\{p\}\right).
\]

An element of the derivative filled with expressions is a one-hole context. Plugging an expression into the distinguished position reconstructs a full layer. Iterating such contexts yields a zipper for a recursive datatype.

The editor focuses a *sequence*, not merely one child expression. At each descent it first chooses a parent expression from a list context and then chooses a recursive field. The crumb consequently combines:

\[
  \mathsf{ListContext}(\mathsf{Expr})
  \times F'(\mathsf{Expr}).
\]

The list context is a prefix/suffix pair. The derivative context records the parent constructor with one child slot distinguished. Because the distinguished child is itself a sequence slot, the focus can hold an interval and a boundary.

This decomposition explains the shape of `Crumb`:

```ts
interface Crumb {
  parentKind: "line" | "slot";
  before: readonly Expr[];
  parent: Expr;
  after: readonly Expr[];
  field: ChildField;
}
```

The parent expression plus field is an implementation-friendly encoding of the constructor derivative; `before` and `after` are the list derivative.

## Lenses and partiality

A total lens from $S$ to $V$ consists of `get` and `put` maps satisfying GetPut, PutGet, and PutPut. A path focus is not total over all lines because the path may be invalid. There are several categorical ways to model this.

### Restriction to a domain

For a fixed path $p$, define the subobject

\[
  S_p=\{s:S\mid p\text{ resolves in }s\}.
\]

Then focus and replacement form an ordinary lens on $S_p$, provided replacement respects the focused sequence kind.

### Partial-map category

Treat `focus` and `put` as partial maps. The lens laws are equations where both sides are defined. This matches stale-path behavior directly.

### Kleisli lens for exceptions

Let $T(X)=E+X$. Then

\[
  \mathsf{get}:S\to T(V),
  \qquad
  \mathsf{put}:S\times V\to T(S).
\]

The laws can be stated using Kleisli equality with compatible error behavior. The executable `Result` API follows this model.

No single formulation is universally best. The thesis uses ordinary lens equations over the valid domain for proofs and `Result`-valued operations in code.

## Commands as Kleisli endomorphisms

For the exception monad $T(X)=E+X$, a command interpretation is a Kleisli arrow

\[
  \llbracket C\rrbracket:S\to T(S).
\]

Sequential execution uses Kleisli composition:

\[
  (g\mathbin{>=>}f)(s)=
  \begin{cases}
    \Err(e) & f(s)=\Err(e),\\
    g(s') & f(s)=\Ok(s').
  \end{cases}
\]

The identity is $\eta(s)=\Ok(s)$. Associativity follows from the exception monad laws. A command trace is therefore a morphism in $\mathsf{Kl}(T)$.

This formulation separates two issues:

- the command's structural state transformation;
- its possibility of explicit failure.

It also suggests reusable combinators. A transaction can compose several primitive commands and commit only on success. A `recover` combinator can map selected errors to alternative commands. Logging can be added by changing the effect to a transformer-like carrier such as

\[
  T(X)=E+(X\times W)
\]

for a diagnostic monoid $W$.

The browser UI should not embed arbitrary side effects inside these arrows. Clipboard, storage, timing, and DOM measurement belong to a larger effectful adapter. The core command category remains deterministic and referentially transparent.

## Rendering algebras and natural transformations

Each backend $b$ defines an algebra

\[
  \alpha_b:F(B_b)\to B_b.
\]

The induced renderer is

\[
  r_b=\cata(\alpha_b).
\]

A conversion $h:B_b\to B_c$ between backend carriers is structure-preserving when

\[
  h\circ\alpha_b=\alpha_c\circ F(h).
\]

Then initiality yields

\[
  h\circ r_b=r_c.
\]

In practice, direct conversion from LaTeX strings to Unicode strings is not such a homomorphism; concrete syntax has already collapsed structure and introduced backend-specific choices. This is precisely why all backends should originate from the shared editor algebra rather than from one another.

The symbol catalog can be modeled as a family of atom algebras. Fixing the composite constructor operations and varying only atom interpretation yields a natural family of folds. Hole-ID renaming is invisible because each hole algebra ignores the ID for visible text. This gives the invariance stated in the previous chapter.

## Product algebras and one-pass computation

Algebras compose by products. Given

\[
  \alpha:F(A)\to A,
  \qquad
  \beta:F(B)\to B,
\]

define

\[
  \langle\alpha,\beta\rangle:F(A\times B)\to A\times B
\]

by projecting recursive pairs, applying each algebra, and pairing the results. The induced fold computes both analyses in one traversal:

\[
  \cata(\langle\alpha,\beta\rangle)(e)
  =(\cata(\alpha)(e),\cata(\beta)(e)).
\]

A production renderer can use a product algebra to compute visual boxes, structural size, hole locations, and accessibility descriptions together. The implementation currently keeps size and hole-order folds separate for clarity.

## Histories as sequence zippers

Undo/redo history has the form

\[
  \mathsf{History}(S)=S^*\times S\times S^*.
\]

This is the zipper of a finite sequence with one focused present. Undo moves the nearest past state into focus and pushes the old focus onto the future. Redo is the inverse move when available. Committing a new state appends the old present to the past and clears the future.

It is tempting to label the history structure a comonad because zippers often support comonadic operations. The finite past/present/future implementation used here is not presented with a comonad instance, and the history limit truncates context. The mathematically justified claim is narrower: it is a sequence zipper with partial left and right movement and a reset-on-commit operation.

The key laws are:

\[
  \mathsf{redo}(\mathsf{undo}(H))=H
\]

when undo succeeds and no new commit occurs, and dually for redo. After committing from an undone state, the former future is discarded, so the inverse law no longer applies. Tests assert the valid inverse case.

## Persistence as an algebraic boundary

A codec consists of

\[
  \mathsf{encode}:S\to J,
  \qquad
  \mathsf{decode}:J\to T(S),
\]

where $J$ is a JSON value domain. The desired round-trip law is

\[
  \mathsf{decode}(\mathsf{encode}(s))=\Ok(s).
\]

The opposite composite cannot be identity on all JSON values because decoding rejects malformed values and encoding chooses a canonical representation. On accepted values one may define a normalization $q:J\rightharpoonup J$ and require

\[
  \mathsf{encode}(\mathsf{decode}(j))=q(j).
\]

Version migration is composition of partial codecs. If migrations are written as Kleisli arrows

\[
  m_{i,j}:S_i\to T(S_j),
\]

then multi-version migration is their Kleisli composition. Explicit version indices prevent a new decoder from pretending that old constructor shapes are already current.

## The proof-obligation graph

The system's guarantees compose in a dependency graph rather than one monolithic theorem.

![Dependencies among representation, focus, transition, codec, backend, and elaboration obligations.](../figures/proof-obligations.png){width=96%}

At the base are datatype and validator properties. Path lens laws depend on child-field coherence. Command preservation depends on syntax validity, freshening, and plug preservation. Codec soundness depends on the validator. Renderer totality depends on exhaustive folds and catalog fallbacks. Object-level soundness depends additionally on elaboration and the metatheory of the selected core language.

This graph prevents an invalid inference: passing renderer tests does not establish type soundness, and a preservation proof for editor states does not establish backend conformance. Each claim has a specific domain and prerequisites.

## Adjunctions in the architecture

One should be cautious about asserting adjunctions merely because the interface contains the glyph $\dashv$. Several genuine adjunction-like patterns may nevertheless arise in an extended design.

- Free syntax construction is left adjoint to an appropriate forgetful functor from algebras when the relevant categories and signatures are fixed.
- Parsing and pretty-printing are rarely strict adjoints on raw strings, but can form partial isomorphisms or lens-like structures on normalized subsets.
- Forgetting proofs from refined states to raw states may have a partial left inverse given by validation, not generally an adjunction without a carefully defined category.

The present thesis relies only on initiality, container derivatives, lenses, monadic composition, and zipper structure. It does not claim an unsupported categorical equivalence for the whole editor.

## Category-theoretic synthesis

The categorical picture can be summarized as follows.

\[
\begin{array}{lll}
\textbf{Object} & \textbf{Structure} & \textbf{Software consequence}\\
\hline
\mathsf{Expr} & \text{initial }F\text{-algebra} & \text{one exhaustive generic fold}\\
F & \text{container/polynomial functor} & \text{strictly positive, mappable children}\\
\mathsf{Context} & \text{datatype derivative} & \text{typed zipper crumbs}\\
\mathsf{PathFocus} & \text{partial lens} & \text{checked get/replace and laws}\\
\mathsf{Command} & \text{Kleisli endomorphism} & \text{pure reducer with explicit errors}\\
\mathsf{History} & \text{sequence zipper} & \text{lawful undo/redo movement}\\
\mathsf{Backend} & F\text{-algebra} & \text{independent folds from one syntax}\\
\mathsf{Codec} & \text{partial retraction} & \text{versioned checked persistence}.
\end{array}
\]

The value of this table is predictive. Adding a constructor requires extending $F$, every algebra, the container field reflection, validation, and derivative positions. Adding a backend requires only a new algebra and catalog projection. Adding a command requires a new Kleisli endomorphism and preservation case, not changes to rendering. Adding a UI requires a command adapter and box renderer, not a second syntax.

## Chapter summary

Category theory organizes the reconstruction into universal and law-governed components. The syntax is an initial algebra of a container functor; generic folds are its unique homomorphisms; derivatives explain cursor contexts; checked focus is a partial lens; commands compose in the exception Kleisli category; histories are sequence zippers; and codecs are partial retractions. These structures are used conservatively: the thesis states only laws supported by the data and implementation.

## Exercises

1. Describe the container shape and position set for a script with both attachments of lengths $b$, $u$, and $l$.
2. Construct the product of the size and hole-order algebras.
3. Explain why converting a LaTeX string to Unicode is not generally an algebra homomorphism from the editor syntax.
4. State the domain restriction needed to treat a fixed path as a total lens.
5. Give the Kleisli composite of two commands and show how the first error is propagated.


# Rebuilt software architecture

## From one component to semantic layers

The supplied artifact concentrates syntax, traversal, rendering, editing, history, persistence, catalog search, long-press behavior, documentation, and visual styles in one React component. Its compactness is useful for a prototype, but it obscures dependency direction. A change to a constructor can require synchronized edits in `fieldsOf`, three generators, the renderer, emptiness checks, navigation, template makers, and documentation examples.

The reconstruction replaces this horizontal coupling with a layered architecture:

\[
\begin{array}{c}
\text{browser events and visual components}\\
\downarrow\\
\text{commands and render requests}\\
\downarrow\\
\text{pure editor reducer}\quad\text{generic syntax folds}\\
\downarrow\\
\text{checked zipper}\quad\text{typed syntax}\quad\text{symbol catalog}\\
\downarrow\\
\text{versioned codec and immutable history}.
\end{array}
\]

Dependency arrows point downward. The core has no DOM, React, storage, timer, or clipboard dependency. The browser shell can be replaced without changing the syntax or transition semantics.

## Package map

The executable reconstruction is organized into the following modules.

| Module | Responsibility | Mathematical role |
|---|---|---|
| `model.ts` | Datatypes, smart constructors, child reflection, validation, cloning | Initial algebra carrier and validity predicate |
| `path.ts` | Path resolution, zipper crumbs, focus, replacement, traces | Datatype contexts and partial path lens |
| `editor.ts` | State, commands, pure reducer, fresh holes, navigation | Deterministic operational semantics |
| `fold.ts` | `SyntaxAlgebra<A>`, generic folds, analyses | Catamorphisms from the initial algebra |
| `catalog.ts` | Semantic symbol IDs and backend projections | Atom interpretation boundary |
| `backends.ts` | LaTeX, Typst, Unicode render algebras and diagnostics | Denotational interpretations |
| `history.ts` | Past/present/future timeline | Sequence zipper over states |
| `codec.ts` | Versioned encode/decode and schema checks | Partial retraction at the persistence boundary |
| `examples.ts` | Demonstration lines and templates | Well-formed test fixtures |
| `tests/run.ts` | Deterministic executable checks | Finite evidence for laws and invariants |
| `web/` | Browser shell and static capture pages | Effectful adapter and visual demonstration |

This organization is not arbitrary file splitting. Each module corresponds to a distinct semantic object with its own laws.

## Dependency discipline

The intended import graph is acyclic.

- `model.ts` depends on no editor module.
- `catalog.ts` depends only on catalog data types.
- `path.ts` depends on `model.ts` and `result.ts`.
- `fold.ts` depends only on `model.ts`.
- `backends.ts` depends on `fold.ts`, `model.ts`, and `catalog.ts`.
- `editor.ts` depends on `model.ts`, `path.ts`, and `result.ts`.
- `history.ts` is generic and does not know the syntax.
- `codec.ts` depends on the public state model and validation.
- the browser adapter depends on all public services but none depends on it.

A practical enforcement mechanism is to expose module-level public APIs and use a static dependency checker in continuous integration. The included reconstruction is small enough for manual inspection, but the rule should become automated as the project grows.

## Immutable data and referential transparency

All core records and arrays are readonly. Edits build new paths, sequences, expressions, lines, and documents through copying. The reducer does not mutate its input state. This establishes a host-language approximation to the mathematical view of a transition as a function.

Immutability has direct consequences.

- Undo history can store prior states without deep snapshots after every command, provided no value is mutated later.
- Renderer outputs can be memoized by structural identity.
- Tests can retain input states and compare them after commands.
- concurrent UI rendering cannot observe partially mutated trees.
- command replay is deterministic.

TypeScript's `readonly` is compile-time shallow discipline. The code avoids mutation by convention and cloning helpers; a production build may freeze values in development or use persistent collections for stronger runtime guarantees.

## Result values

The common result type is

```ts
export type Result<T, E> =
  | { readonly ok: true; readonly value: T }
  | { readonly ok: false; readonly error: E };
```

Path resolution, path replacement, editor commands, and decoding use this sum. Callers must discriminate on `ok` before accessing the branch payload. This produces explicit control flow and preserves error categories.

The reconstruction does not prohibit every exception. Smart constructors such as `nonEmpty` throw when trusted internal code violates a precondition. The distinction is:

- untrusted or expected failure is represented by `Result`;
- an impossible violation inside a trusted helper is treated as a programming defect.

A stricter implementation could make all smart constructors return `Result` or use branded refined values created only by decoders.

## Model module

The model exposes a discriminated union whose `kind` field determines payload shape. It also provides:

- atomic constructors for identifiers, numbers, symbols, and punctuation;
- smart constructors for fractions, roots, scripts, functions, groups, large operators, accents, and arrows;
- `childFields`, `getChild`, and `setChild`;
- `cloneExpr` for safe template copying;
- `validateExpr` and `validateDocument`;
- structural emptiness inspection.

`childFields` is the single source of truth for recursive traversal order. Any new constructor must update the discriminated union and this reflection interface; TypeScript's exhaustiveness checking makes missing switch cases visible during compilation.

The validator traverses all fields, checks non-empty slots even after unsafe construction, verifies lexical payloads, and accumulates hole IDs to report duplicates. Diagnostics contain structural paths in a readable notation. Validation is deliberately independent of the editor cursor so it can be used for templates and decoded documents.

## Path module

`resolvePath` iteratively traverses a line. It validates each index and field, records a crumb, and returns a sequence zipper. `plug` folds crumbs from the inside out. Convenience functions include:

- `focusAt(line,path)` for the focused sequence;
- `replaceAt(line,path,replacement)` for a checked local update;
- `pathOf(zipper)` for recovering a serializable address;
- `samePath` for cursor comparison;
- `pathTrace` and `compareTrace` for traversal order.

The API does not expose unchecked indexing helpers. An invalid path is a value-level error with a depth. This is the key boundary that prevents stale persistence from becoming a runtime property-access failure.

## Editor module

`editor.ts` contains no UI mode. Its public concepts are `Selection`, `Cursor`, `EditorState`, `Command`, `EditError`, `validateEditorState`, `makeState`, and `reduce`.

Every command branch follows the same template:

1. resolve and validate the focused sequence;
2. normalize the selection when needed;
3. construct a replacement using immutable sequences and smart constructors;
4. replace through the path lens;
5. compute a new cursor and fresh counter;
6. call `commit`, which validates the resulting state.

This uniform shape makes the preservation argument inspectable. Shared helpers implement freshening, hole collection, deletion of a span, and cursor updates. The UI can dispatch commands without receiving direct access to internal splice functions.

## Fold and backend modules

The fold module contains the recursion scheme and analyses. The backend module contains no recursive switch over `Expr`; it only supplies algebras. Adding MathML would require a `SyntaxAlgebra<Piece>` and a new backend selector case. It would not modify editor commands or model traversal.

Each renderer returns a `RenderResult`:

```ts
interface RenderResult {
  backend: "latex" | "typst" | "unicode";
  text: string;
  fidelity: "exact-structure" | "readable-fallback";
  issues: readonly RenderIssue[];
}
```

A UI can show the text while exposing warnings. Clipboard copying can choose to permit fallback output, require confirmation, or select a stricter backend mode. The core does not silently erase unsupported constructors.

## Symbol catalog

The catalog gives stable IDs to symbols. An entry contains:

- display glyph;
- LaTeX spelling;
- optional Typst spelling;
- mathematical spacing class;
- search aliases and categories where useful.

The source's catalog is rich and user-centered, with aliases such as “epi,” “tensor,” and “adjunction.” The reconstruction retains the idea while changing canonical storage. Keyboard keys and search hits create `symbol(id)` nodes; renderers ask the catalog for backend data.

A larger system should version the catalog independently. Renaming an ID is a persistence migration. Changing a backend spelling under the same ID is normally a renderer update. Splitting one overloaded ID into context-specific entries may require elaboration-aware migration.

## History module

The history API is generic:

```ts
interface Timeline<S> {
  readonly past: readonly S[];
  readonly present: S;
  readonly future: readonly S[];
}
```

`commitTimeline` appends the present to the past, installs the new state, clears the future, and enforces a history limit. `undo` and `redo` return unchanged timelines when unavailable or explicit options, depending on the helper. The included tests verify inverse movement in the defined domain.

History is outside `EditorState`. This avoids serializing transient undo stacks as part of the mathematical document and lets an application choose snapshot, command, or hybrid histories. The browser prototype uses snapshot states for clarity.

## Codec module

The codec emits a versioned JSON envelope. Decoding treats every property as untrusted. It validates constructor tags, arrays, strings, optional fields, script attachments, document non-emptiness, hole uniqueness, cursor bounds, and path resolution. An unknown version is rejected rather than guessed.

Persistence should store the semantic syntax and cursor, not generated backend strings or layout measurements. Generated outputs can be recomputed. Transient mode state such as an open search panel is likewise excluded unless product requirements explicitly demand restoration.

The source writes snapshots after a debounce and catches all storage errors silently. A production adapter should surface storage failure non-destructively and keep a last-known-good in-memory state. The core codec already supplies the distinction between invalid data and storage transport errors.

## Browser adapter

The included browser prototype demonstrates the core rather than recreating every original interaction. It presents:

- a worksheet with direct structural rendering;
- a visible cursor and selectable holes;
- LaTeX, Typst, and Unicode output;
- insertion templates and structural commands;
- invariant and renderer status;
- a design panel explaining the semantic layers.

![Executable rebuilt prototype with the typed core and invariant panel.](../screenshots/rebuilt-editor.png){width=98%}

The screenshot is taken from the included browser artifact. Unlike the baseline reconstruction, it is a capture of the rebuilt executable interface rendered in a browser environment. The interactive page lives in `rebuild/web/index.html` and can be served locally after compilation.

The adapter translates clicks and key actions into command values. After `reduce`, it either installs the returned state in history or displays the error. Rendering is derived from the current state; no backend string is edited directly. This enforces a one-way data flow:

\[
  \mathsf{State}\to\mathsf{View},
  \qquad
  \mathsf{Event}\to\mathsf{Command}\to\mathsf{State}.
\]

## Interaction policies outside the core

Some source behaviors remain adapter policies rather than semantic commands.

### Long press

A pointer timer decides whether a key dispatches its ordinary command or opens a variant menu. Timing thresholds and pointer cancellation belong to the UI, not the reducer.

### Search

Fuzzy search ranks catalog entries. Selecting a result dispatches an insertion command containing the entry's template. Search ranking does not modify the document.

### Pinning

A pinned fragment is serialized editor syntax. On insertion it passes through freshening so its holes receive new identities. Removal and ordering of pins are application state.

### Clipboard

Copy requests render the active line through a selected backend and pass the resulting text to a clipboard capability. Clipboard errors do not alter the editor document.

### Persistence debounce

A scheduler encodes accepted states after a delay. The codec is pure; timing and storage are effects. A state revision number can prevent older scheduled writes from overwriting newer ones.

## Accessibility and input methods

A structural editor must expose more than visual boxes. An accessibility algebra can produce a speech tree or linear description such as “fraction, numerator a plus b, denominator two.” Cursor movement should announce entry and exit from fields. Holes should expose identities or ordinal descriptions without reading internal IDs literally.

Keyboard and touch interactions should map to the same command set. Input method editors require composition events to produce atomic identifier text rather than one command per intermediate character. These concerns are not fully implemented in the prototype, but the command boundary makes them addable without altering syntax.

## Performance

The reference implementation favors clarity. Path replacement copies every sequence and ancestor along the path, giving time proportional to the focus depth plus copied sibling lengths. For document size $N$ and depth $d$, a local edit is generally $O(N)$ in the worst case under flat arrays, though it shares untouched expression objects.

Several optimizations preserve semantics:

- persistent vectors for large sequences;
- direct zipper state during an editing session, with paths only for serialization;
- memoized folds keyed by expression identity;
- incremental validation of the changed path plus a trusted-state invariant;
- product algebras computing multiple view artifacts in one traversal;
- line-level rendering and persistence granularity.

Optimization must preserve the same reducer relation and fold results. Differential tests can compare an optimized implementation with the reference semantics.

## Security boundary

The core eliminates several classes of accidental corruption but is not a complete security sandbox. Relevant controls include:

- escaping user-controlled text in backend emitters;
- rejecting unrecognized constructor tags and catalog IDs where strict mode is required;
- bounding document depth and size during decode to prevent resource exhaustion;
- avoiding `eval` and dynamic command construction;
- treating copied backend output as text;
- serving the browser adapter with a restrictive content security policy.

Because LaTeX output may be embedded in a larger toolchain, downstream compilation should use a restricted engine and trusted macro set. Structural validity of generated syntax does not make arbitrary TeX execution safe.

## Chapter summary

The reconstruction maps each mathematical abstraction to a module with a narrow dependency surface. Typed syntax, checked paths, a pure reducer, generic folds, backend algebras, a semantic symbol catalog, timeline history, a versioned codec, and an effectful browser adapter are separate. The result is not merely easier to read; it makes laws locally testable and gives every future extension an explicit integration point.

## Exercises

1. Draw the dependency graph after adding a MathML backend and verify that it does not introduce a dependency from `model.ts` to `backends.ts`.
2. Explain why pins must pass through hole freshening on insertion.
3. Design a revision-number rule for debounced persistence writes.
4. Compare storing a path cursor with storing a live zipper cursor in terms of update cost and serialization.
5. Specify an accessibility algebra for fractions and scripts.


# Verification: proofs, executable laws, and inspection

## Evidence classes

A mathematically responsible reconstruction distinguishes four classes of evidence.

1. **Representation arguments** show that constructors exclude specified malformed states.
2. **Paper proofs** establish laws under stated hypotheses.
3. **Executable tests** check finite instances and regression scenarios.
4. **Visual inspection** checks properties of rendered artifacts that are not captured by structural assertions.

None subsumes all the others. A discriminated union does not prove a renderer correct. A preservation proof does not verify CSS layout. A randomized test does not establish a universal theorem. A screenshot does not show that a cursor path is lawful. The bundle therefore includes all four forms and labels their scope.

## Static checks

The TypeScript compiler is run in strict mode through the project configuration. Compilation checks:

- exhaustiveness of constructor and command switches through unreachable fall-through;
- field compatibility of discriminated union branches;
- non-empty tuple use in smart-constructor APIs;
- readonly state and syntax interfaces;
- explicit optional-field handling;
- browser/core module compatibility with the selected ECMAScript target.

Static checking cannot validate JSON, prevent all unsafe casts, establish global hole uniqueness, or prove recursive functions total. Those obligations remain in codecs, validators, proofs, and tests.

## Test harness

The test runner is dependency-free. It defines named cases, structural JSON equality, assertions, and an `expectOk` helper. A failed case prints its name and stack; the process exits nonzero unless every test passes. `npm test` first recompiles the project and then executes the compiled runner.

The suite contains thirteen cases.

| Test | Obligation exercised |
|---|---|
| Example state validity | Document, cursor, path, bounds, and hole invariants |
| Three lens laws | GetPut, PutGet, PutPut on a nested fraction path |
| Backend totality | Shared syntax folds produce non-empty defined outputs |
| Template insertion | Hole freshening and first-hole focus |
| Accent target | Prior-expression wrapping semantics |
| Script ownership | Base and attachment form one node |
| Slot deletion | Empty recursive slots are repaired with a hole |
| Undo/redo | Inverse movement over committed timeline states |
| Codec round trip | Versioned checked persistence and schema rejection |
| Random command sequence | Transition preservation over 350 deterministic steps |
| Duplicate holes | Global uniqueness validator |
| Vacuous script rejection | Smart-constructor structural exclusion |
| Composite accent | Ordinary recursive validation of accent bodies |

![Verification run included with the reconstruction.](../screenshots/verification-tests.png){width=96%}

The captured run reports thirteen passing tests. Runtime in milliseconds is incidental and may differ by machine; pass/fail behavior and deterministic test data are the relevant artifacts.

## Lens-law test

The lens test constructs

\[
  R=[\mathsf{Frac}([a],[b])]
\]

and path

\[
  p=[(0,\mathsf{numerator})].
\]

It then checks:

\[
\begin{aligned}
\mathsf{focus}_p(\mathsf{replace}_p(R,[x,+,y]))&=[x,+,y],\\
\mathsf{replace}_p(R,\mathsf{focus}_p(R))&=R,\\
\mathsf{replace}_p(\mathsf{replace}_p(R,[x,+,y]),[2])
  &=\mathsf{replace}_p(R,[2]).
\end{aligned}
\]

This is a representative finite instance of the three universal laws proved by induction in Chapter 5. It additionally verifies that the path resolves to an actual zipper. Future property tests should generate arbitrary valid lines, paths, and non-empty replacements.

## Backend-totality test

The example line depicts an adjunction-like expression. Each backend fold must return non-empty text containing no JavaScript `undefined` leakage. The test also checks backend-specific representatives: LaTeX includes `\dashv`, and Unicode includes `⊣`.

This test establishes constructor coverage for the chosen fixture, not conformance for every symbol or external compiler. Exhaustive TypeScript switches and the generic algebra interface provide broader static pressure. A future suite should enumerate every catalog entry, compile emitted LaTeX and Typst in sandboxed toolchains, and parse supported subsets back to backend ASTs.

## Freshness test

The fraction template contains two placeholder holes. Inserting it after $x$ must:

- allocate two identities greater than or equal to the state's fresh counter;
- preserve global uniqueness;
- descend into the numerator;
- select the first new hole;
- leave the complete state valid.

The test does not depend on exact generated IDs beyond monotonicity. This avoids coupling to an implementation detail while still checking freshness.

## Structural correction tests

Two tests directly target source-level design defects.

### Accent targeting

Starting from the line $[x]$ with a caret after $x$, applying a hat must produce one accent node whose body contains the original atom. It must not produce $[x,\mathsf{Hat}([\square])]$.

### Script ownership

Starting from $[x]$, attaching superscript $2$ must produce a one-element line containing a script node. The script's base contains $x$, and LaTeX rendering contains `^{2}`. There is no orphan sibling script.

These tests are regression specifications for the reconstructed semantics, not claims that the original source behaved this way.

## Deletion and slot preservation

The deletion test focuses the entire numerator $[a]$ of a fraction and invokes backspace. The resulting focus must be a one-element slot containing a hole. The whole state is revalidated.

This is a boundary case with high defect risk: a generic splice naturally produces `[]`, but that value is illegal for a recursive slot. The test ensures that the context kind is consulted and a repair hole is allocated.

## History and codec laws

The timeline test creates two committed states, undoes one step, and redoes it. Structural equality with the original committed states checks the valid inverse law.

The codec test asserts

\[
  \mathsf{decode}(\mathsf{encode}(S))=\Ok(S)
\]

for the demonstration state and rejects an envelope with the wrong schema. It does not test every malformed JSON shape; decoder branch tests should be expanded for production.

## Deterministic randomized preservation

The most expansive executable check uses a linear congruential generator initialized with a fixed seed. At each of 350 steps it chooses among:

- atom and symbol insertion;
- fraction and summation templates;
- left/right movement;
- previous/next hole jumps;
- backspace;
- structural selection growth;
- function wrapping;
- superscript/subscript attachment;
- bar/hat accents.

The initial state contains one hole. Every command is required to return `Ok`; after every transition the full editor validator must return no issues. Because the seed and command set are fixed, a failure is reproducible.

The test checks a finite trace

\[
  S_0\xrightarrow{C_1}S_1\xrightarrow{C_2}\cdots\xrightarrow{C_{350}}S_{350}
\]

and validates each $S_i$. It gives useful broad regression coverage across nested interactions. It is not a proof of preservation for all states and command traces. The theorem argument in Chapter 6 supplies the universal claim, while this test detects implementation divergence from that argument.

## Negative tests

Positive examples alone can pass under permissive validators. The suite includes two important negative checks.

- A fraction whose numerator and denominator holes share the same ID must report a duplicate-hole issue.
- Calling the script smart constructor with neither attachment must throw as an internal programming error.

A mature suite should add invalid field paths, out-of-range selections, empty slots introduced through unsafe casts, unknown catalog entries under strict mode, invalid function names, malformed schema versions, excessive depth, and migration failures.

## Proof-obligation matrix

The following matrix states what is argued, tested, or left for future mechanization.

| Claim | Paper argument | Executable check | Machine proof |
|---|---:|---:|---:|
| Expression recursion is strictly positive | Yes | Compiler representation | No |
| Recursive slots are non-empty through constructors | By datatype | Yes | No |
| Hole IDs remain fresh under insertion | Inductive argument | Yes | No |
| Path lens laws | Inductive proof | Representative test | No |
| Reducer determinism | Case analysis | Deterministic runner | No |
| Successful transitions preserve validity | Case proof sketch | 350-step trace and cases | No |
| Backend folds are total on valid syntax | Algebra/exhaustiveness argument | Example fixture | No |
| Codec encode/decode round trip | Design law | Example state | No |
| LaTeX/Typst external conformance | Not established | Not compiled externally | No |
| Object-language elaboration soundness | Interface specified only | No | No |
| Object-language type soundness | Theory-dependent | No | No |

The final three rows are intentional limitations. The reconstruction makes them possible to address but does not manufacture evidence that is absent.

## Visual verification

The thesis includes three interface captures:

1. a source-grounded static reconstruction of the supplied component;
2. a browser capture of the rebuilt prototype;
3. a capture of the passing test run.

For the PDF itself, the production workflow renders every page to images and inspects representative pages for clipping, font failures, formula overflow, broken figure links, code-block truncation, and blank pages. Automated PDF metadata, font, and text checks supplement the visual pass. The inspection report is stored in `verification/`.

Visual verification is especially important for this thesis because the subject is a visual structure editor and the document contains long code identifiers, equations, tables, and screenshots. A syntactically valid PDF can still be unusable if those elements overlap or clip.

## Differential testing strategy

The pure reducer enables a stronger future method. Keep the present implementation as a reference semantics and develop an optimized implementation. Generate valid states and commands, then require:

\[
  \mathsf{normalize}(\mathsf{reduce}_{ref}(S,C))
  =\mathsf{normalize}(\mathsf{reduce}_{opt}(S,C)).
\]

Normalization may erase non-semantic allocation details when necessary, though fresh-hole IDs should normally remain deterministic. This technique is effective for replacing array copying with persistent vectors or live zipper state.

Similarly, backend algebras can be compared against backend AST emitters. A direct string algebra and an AST-plus-pretty-printer implementation should agree after whitespace normalization on a generated corpus.

## Model-based UI testing

The browser adapter can be tested against the core model. A test driver performs UI actions, extracts the displayed serialized state or output, and compares it with commands run directly through `reduce`. The model supplies the oracle. This can detect event-adapter defects such as dispatching the wrong command on a long press, applying a command twice, or placing the mouse cursor at the wrong boundary.

The included screenshot does not constitute such a test; it is a visual artifact. The architecture makes model-based testing feasible because the UI is not itself the only definition of behavior.

## Toward mechanized proofs

A proof assistant formalization should prioritize high-leverage theorems:

1. `resolve` followed by `plug` satisfies the path-lens laws.
2. freshening preserves shape and produces globally fresh IDs.
3. every command preserves `Valid` on success.
4. the decoder's success result carries `Valid` evidence.
5. each backend fold is total for the formal syntax.

A correspondence layer then relates formal syntax and states to JSON/TypeScript representations. Full proof of browser behavior is substantially harder and may rely on testing rather than end-to-end theorem proving.

## Chapter summary

The reconstruction is supported by representation constraints, paper proofs, deterministic tests, and visual inspection. Thirteen executable cases cover the principal laws and corrected behaviors, including a 350-command invariant-preservation trace. The evidence is deliberately scoped: it supports structural claims about the reference core, not external backend conformance or object-language soundness. Those stronger claims have explicit future proof obligations.

## Exercises

1. Extend the random command generator with `newLine` while guaranteeing that generated commands remain meaningful.
2. Design a generator for valid paths by traversing a generated expression rather than generating arbitrary indices.
3. State a property test for fresh-hole alpha-equivalence after inserting the same template twice.
4. Propose a backend conformance test that does not execute unrestricted TeX.
5. Explain why a screenshot cannot establish a lens law and why a unit test cannot establish absence of PDF clipping.


# Worked case studies

## How to read the traces

Each case begins with a structural state and applies commands through the reducer. A cursor is written

\[
  \langle\ell,p,a,h\rangle.
\]

At a root line the path is $[]$. A selected hole at index $i$ is shown as $[i,i+1)$. Generated hole identities are schematic; the executable implementation uses a monotone counter. Renderings are consequences of backend algebras, not canonical mathematical meanings.

## Case study 1: an adjunction display

The demonstration line is intended to display

\[
  F\dashv G:\mathcal C\rightleftarrows\mathcal D.
\]

In the reconstructed editor syntax, one possible line is

\[
\begin{aligned}
[&\mathsf{Id}(F,\mathsf{plain}),
  \mathsf{Sym}(\mathsf{relation.adjoint}),
  \mathsf{Id}(G,\mathsf{plain}),
  \mathsf{Punct}(:),\\
 &\mathsf{Id}(C,\mathsf{script}),
  \mathsf{Sym}(\mathsf{arrow.rightleft}),
  \mathsf{Id}(D,\mathsf{script})].
\end{aligned}
\]

The line has seven expressions. None is a special category-theory AST node. The structure records notation, style, and symbol identity. The LaTeX algebra yields a string of the form

```tex
F\dashv G:\mathcal{C}\rightleftarrows\mathcal{D}
```

while the Unicode backend yields the corresponding glyph sequence, visually equivalent to $F\dashv G:\mathcal Cightleftarrows\mathcal D$, with spacing determined by symbol classes.

### Structural guarantee

The editor can guarantee that the script letters remain styled atoms and that the relation and arrow are catalogued symbols. It cannot establish:

\[
  \mathcal C,\mathcal D:\mathsf{Category},
  \quad
  F:\mathcal C\to\mathcal D,
  \quad
  G:\mathcal D\to\mathcal C,
  \quad
  F\dashv G.
\]

An elaborator for category theory would need to resolve each identifier in a context and construct or check adjunction data. The notation tree is an input to that process.

### Cursor movement

Place a caret before $\mathcal C$ at root boundary $4$. Right movement over the styled identifier moves to boundary $5$. It does not enter any child because an identifier is atomic. If $\mathcal C$ were instead a script node, movement would enter its base first and then its attachment. This difference illustrates why mathematical font style and script attachment are distinct constructors.

## Case study 2: inserting and filling a fraction

Begin with a blank line and caret at root boundary $0$:

\[
  S_0=\langle[[]],\langle0,[],0,0\rangle,0\rangle.
\]

The fraction template is

\[
  V=[\mathsf{Frac}([\mathsf{Hole}(t_0)],[\mathsf{Hole}(t_1)])].
\]

The template IDs are not inserted directly. Freshening produces $h_0$ and $h_1$:

\[
  S_0\xrightarrow{\mathsf{Insert}(V)}S_1
\]

with line

\[
  [\mathsf{Frac}([h_0],[h_1])]
\]

and cursor

\[
  \langle0,[(0,\mathsf{numerator})],0,1\rangle.
\]

Typing $a$ dispatches `Insert([a])`. Because the hole is selected, the numerator becomes $[a]$ and the caret moves after it:

\[
  [\mathsf{Frac}([a],[h_1])].
\]

A next-hole command orders holes by traces. The denominator hole has the only remaining trace, so the cursor becomes

\[
  \langle0,[(0,\mathsf{denominator})],0,1\rangle.
\]

Typing $b$ yields

\[
  [\mathsf{Frac}([a],[b])].
\]

The LaTeX and Unicode renderings are, respectively,

```tex
\frac{a}{b}
```

and

```text
(a)/(b)
```

The Unicode output is linear but preserves the numerator/denominator boundary with parentheses.

### Deleting the numerator

Move into the numerator and select $a$. Backspace cannot leave the slot empty. It allocates a fresh hole, say $h_2$:

\[
  [\mathsf{Frac}([a],[b])]
  \xrightarrow{\mathsf{Backspace}}
  [\mathsf{Frac}([h_2],[b])].
\]

The cursor selects $h_2$. This is the operational manifestation of the non-empty-slot invariant.

### Deleting the whole fraction

At the root, select the fraction node and backspace. The root line may become empty:

\[
  [\mathsf{Frac}([h_2],[b])]
  \longrightarrow [].
\]

No hole is inserted because a line is allowed to be empty. The focus kind distinguishes the two cases.

## Case study 3: indexed root fidelity

Insert the indexed-root template:

\[
  \mathsf{Root}([h_r], [h_i]).
\]

Traversal order enters the index before the radicand. Fill $h_i$ with $3$ and $h_r$ with $x+1$ to obtain

\[
  \mathsf{Root}([x,+,1],[3]).
\]

The backends yield forms such as

```tex
\sqrt[3]{x+1}
```

```typst
root(3, x + 1)
```

```text
root[3](x + 1)
```

The source Unicode generator emits `√(x+1)` for both indexed and unindexed roots, identifying distinct trees. The rebuilt Unicode algebra chooses a less typographic but injectivity-preserving fallback for this constructor distinction.

This illustrates a general backend policy: when a target lacks a native visual construct, preserve structure textually and report fidelity where necessary rather than silently dropping data.

## Case study 4: script attachment

Begin with line

\[
  [x]
\]

and caret after $x$. Apply a superscript command with no supplied content. The target policy chooses the previous expression as the base and allocates an index hole:

\[
  [x]
  \longrightarrow
  [\mathsf{ScriptSup}([x],[h_0])].
\]

The cursor descends to the superscript and selects $h_0$. Inserting $2$ produces

\[
  [\mathsf{ScriptSup}([x],[2])].
\]

Now apply a subscript command at a caret after the scripted expression. The previous expression is already a script. Rather than wrapping it as the base of another script, the command merges attachments:

\[
  [\mathsf{ScriptSup}([x],[2])]
  \longrightarrow
  [\mathsf{ScriptBoth}([x],[2],[h_1])].
\]

After filling $h_1$ with $i$, the tree denotes the notation $x_i^2$. LaTeX rendering is compositionally derived:

```tex
{x}^{2}_{i}
```

### Selection as a compound base

Suppose the root line is $[x,+,y]$ and all three expressions are selected. Applying superscript constructs

\[
  [\mathsf{ScriptSup}([x,+,y],[h])].
\]

The base is a non-empty sequence, so the renderer can brace it. There is no need for the command to invent a group node; grouping for attachment is a property of the script constructor. An object-language elaborator may still require explicit parentheses depending on precedence.

### Starting a script at a sequence boundary

At the start of an empty or non-empty sequence with no previous expression and no selection, applying a script creates a fresh base hole and a fresh attachment hole:

\[
  [\mathsf{ScriptSup}([h_b],[h_s])].
\]

This state is structurally valid and visually communicates both missing components. In the source, a sibling script at position zero is repaired by inserting a hole before it. The rebuilt representation performs the repair inside the constructor.

## Case study 5: accent semantics

Start with $[x]$ and caret after $x$. Applying a hat gives

\[
  [\mathsf{Accent}(\mathsf{hat},[x])].
\]

The source documentation describes this target behavior, but its no-selection branch inserts an empty accent after $x$. The reconstructed rule aligns implementation and description.

With selection $[x,+,y]$, applying an overline yields

\[
  [\mathsf{Accent}(\mathsf{overline},[x,+,y])].
\]

At a sequence start with no selection, it yields

\[
  [\mathsf{Accent}(\mathsf{hat},[h])]
\]

and selects $h$.

Nested application preserves order:

\[
  \mathsf{Accent}(\mathsf{bar},
    [\mathsf{Accent}(\mathsf{hat},[x])])
\]

is not normalized to the reverse nesting. The LaTeX algebra emits nested commands according to the tree.

## Case study 6: annotated arrows

An annotated right arrow with label $f$ is

\[
  \mathsf{AnnotatedArrow}(\mathsf{right},[f]).
\]

Its LaTeX rendering is

```tex
\xrightarrow{f}
```

and its Unicode fallback is a linear annotation such as `-f→`. The visual algebra stretches the arrow and places $f$ above it.

Representing this as an accent would obscure three facts:

- the label is a navigable child field named `label`, not an accent body;
- the arrow kind determines direction and shaft geometry;
- output syntax uses an arrow command rather than an overlay accent.

The dedicated constructor makes future extension straightforward. A lower label can be added as a second optional slot, or a morphism elaborator can assign source and target objects.

## Case study 7: function wrapping

Take line

\[
  [x,+,y]
\]

and select all three expressions. `WrapFn("f")` produces

\[
  [\mathsf{Function}(f,[x,+,y])].
\]

The selection is structurally moved into the argument slot. LaTeX rendering uses `\operatorname{f}` for a nonstandard name and scalable parentheses. A standard name such as `sin` uses `\sin`.

With no selection, the same command creates

\[
  \mathsf{Function}(f,[h])
\]

and focuses the hole. Invalid names are rejected at the command boundary. This lexical check prevents backend command construction from arbitrary punctuation, but it does not assert that $f$ exists in a context.

### Hom as notation

The source includes a special `Hom` template with two holes and a subscript. In the reconstructed core, one may represent it compositionally as a function name `Hom` whose argument contains two holes separated by punctuation, then attach a subscript through the ordinary script constructor. An elaborator may instead normalize this surface form into a typed hom-set constructor. The editor need not hard-code that semantic choice.

## Case study 8: structural selection ascent

Consider the numerator of

\[
  \frac{a+b}{c}.
\]

Place a caret after $b$ inside the numerator. Repeated `Grow` commands produce:

1. selection of $b$;
2. selection of the whole numerator sequence $[a,+,b]$;
3. ascent to the root and selection of the whole fraction node;
4. no further change because the fraction is the entire line.

At each stage, wrapping in a function or accent produces a well-formed editor subtree. The second selection is a sequence rather than one expression; wrappers accept non-empty slots. The third selection is exactly one root expression.

This behavior is derived from the cursor context rather than pixel geometry. It remains stable across LaTeX, Typst, Unicode, and visual layout.

## Case study 9: undo, redo, and branching history

Let history begin as

\[
  H_0=\langle[],S_0,[]\rangle.
\]

Commit fraction insertion to obtain

\[
  H_1=\langle[S_0],S_1,[]\rangle.
\]

Fill the numerator and commit:

\[
  H_2=\langle[S_0,S_1],S_2,[]\rangle.
\]

Undo gives

\[
  H_3=\langle[S_0],S_1,[S_2]\rangle.
\]

Redo returns $H_2$. Instead, if a new root template is inserted from $H_3$, commit produces

\[
  H_4=\langle[S_0,S_1],S_3,[]\rangle.
\]

The old future $[S_2]$ is discarded. This is standard branching-history behavior for a linear undo stack. A persistent history DAG would retain both branches but is outside the current design.

## Case study 10: persistence repair boundary

Suppose stored JSON contains a fraction with an empty numerator array. JSON parsing succeeds, but versioned decoding fails because a recursive slot must be non-empty. It does not automatically insert a hole: repair policy should be explicit.

Three application strategies are possible.

1. Reject the snapshot and load a last-known-good state.
2. Run a version-specific migration that inserts fresh holes and reports repairs.
3. Open a recovery view that shows diagnostics and lets the user choose.

The core codec implements rejection. This is safer than silently changing data because malformed values may indicate a bug whose extent is unknown. A migration from the supplied unversioned state format would be a separate, auditable function.

## Case study 11: typed elaboration of composition

Enter the structural sequence

\[
  [g,\circ,f].
\]

The editor accepts it because it is a valid sequence of atoms and a symbol. In a category-theory signature, elaboration may resolve

\[
  f:\mathsf{Hom}(A,B),
  \qquad
  g:\mathsf{Hom}(B,C)
\]

and construct

\[
  g\circ f:\mathsf{Hom}(A,C).
\]

If instead $g:\mathsf{Hom}(D,C)$ with $D\ne B$, elaboration reports a source/target mismatch at the composition symbol or operands. The editor tree remains valid and editable. This exemplifies the separation between structural soundness and mathematical typing.

A typed mode could use the error path to highlight the relevant subinterval and insert coercion or hole suggestions, without changing the core syntax rules.

## Case study 12: one tree, three outputs

Take the structural expression

\[
  \mathsf{ScriptSup}
  ( [\mathsf{Root}([x,+,1],[3])], [2] ).
\]

The same tree may render as:

```tex
{\sqrt[3]{x+1}}^{2}
```

```typst
(root(3, x + 1))^(2)
```

```text
(root[3](x + 1))^(2)
```

The outputs differ syntactically and typographically but preserve the constructor nesting. Editing any backend string directly would require reparsing and could lose cursor identity. Editing the tree and regenerating all outputs maintains a single source of truth.

## Lessons from the cases

The cases exhibit the reconstruction's main patterns.

- Context kind distinguishes blank lines from non-empty recursive slots.
- Fresh holes are identities, not glyphs.
- Scripts and accents own the structures they visually decorate.
- Selection is a sequence interval embedded in a zipper context.
- Output is a family of folds, not canonical storage.
- Undo is movement in a timeline zipper.
- Persistence is a checked refinement boundary.
- Object-level meaning begins only after contextual elaboration.

These are reusable principles for any structured notation editor, not only the supplied keyboard.

## Exercises

1. Give the exact cursor path after inserting a fraction into the radicand of an indexed root and focusing its denominator.
2. Trace two successive script commands that replace an existing superscript value rather than add a second superscript.
3. Design a lower-and-upper-labelled arrow constructor and its navigation order.
4. Explain how the typed composition case should localize its diagnostic using editor paths.
5. Compare recovery strategies for a persisted empty recursive slot.


# Limitations, extensions, and conclusion

## Scope of the reconstruction

The rebuilt core is a reference architecture for structural mathematics editing. It establishes explicit syntax invariants, checked focus, deterministic command semantics, compositional backends, versioned persistence, and executable regression evidence. It is not a complete replacement for a mature mathematics editor, typesetting engine, computer algebra system, or proof assistant.

The limits are substantive and should shape further work.

## Presentation grammar remains intentionally small

The syntax covers atoms, holes, fractions, roots, scripts, named functions, groups, large operators, accents, and annotated arrows. Common mathematical constructs still absent include:

- matrices, aligned equations, cases, and multiline derivations;
- binders with explicit scope;
- underbraces, overbraces, cancellation marks, and extensible decorations;
- tensors with multiple prescripts and postscripts;
- commutative diagrams;
- inference rules and proof trees;
- text spans and mixed prose/math documents;
- semantic tables, records, and domain-specific notation.

Each extension must be added at the functor level. That entails a constructor, validity rules, child positions and traversal order, zipper support, every syntax algebra, command templates, persistence decoding, and tests. The architecture makes this obligation visible; it does not remove it.

## Visual layout is demonstrative

The browser prototype reproduces the structural interaction model but is not a full mathematical layout engine. High-quality layout requires font metrics, italic correction, math classes, cramped styles, delimiter stretching, radical assembly, line breaking, script placement, operator limits, bidirectional text, and accessibility semantics. Browser CSS approximations are insufficient for all formulas.

A production system should target a layout intermediate representation and use either:

- a proven mathematics layout library;
- MathML with a capable browser engine;
- a TeX-derived box algorithm implemented safely;
- a native platform math layout API.

The visual renderer remains an algebra, but its carrier becomes a measured box tree with constraints rather than ad hoc spans.

## Backends cover a disciplined subset

The LaTeX, Typst, and Unicode emitters are total over the reconstructed syntax and return diagnostics. They are not full external-language conformance layers.

LaTeX output assumes relevant packages and a math context. Typst syntax should be regression-tested against a pinned engine version. Unicode output is necessarily a readable linearization for two-dimensional constructs. None of the backends includes a parser, so round-trip adequacy is not established.

A stronger implementation should emit backend ASTs, not strings, and pretty-print them through small trusted modules. Sandboxed conformance tests should compile generated examples. Backend versions and required packages should be metadata in the renderer result.

## Paths may become stale across remote or concurrent edits

The current cursor path uses positional indices. It remains valid across edits performed through its own focus lens but can become stale when an independent edit inserts or removes earlier siblings or changes an ancestor constructor. In a single-user reducer, the cursor is updated with every command, so this is controlled. Collaborative editing introduces a new problem.

Possible approaches include:

- stable expression and sequence-node identities;
- operational transformation over structural paths;
- CRDT positions for sibling sequences;
- zipper rebasing against edit scripts;
- path invalidation with nearest-valid-focus recovery.

A collaborative semantics must specify how commands transform both documents and remote cursors. Positional path equality is inadequate by itself.

## Selection is structural but not geometrically complete

Anchor/head intervals select contiguous members of one focused sequence. Structural growth can select ancestors, but the model does not represent arbitrary discontiguous selections, rectangular matrix selections, or cross-line ranges. Such selections require a richer region algebra.

For many mathematical transformations, contiguous sequence or whole-subtree selection is desirable because it preserves well-formedness. A future design should add new region kinds only with explicit closure properties and command semantics, rather than generalizing to arbitrary pixel ranges.

## No parser or paste elaboration

The core inserts typed templates and programmatically constructed syntax. Pasting LaTeX, Typst, Unicode, or MathML would require parsing into a backend AST, translating into editor syntax, assigning fresh holes and IDs, and reporting unsupported constructs. Direct string insertion would violate the one-tree design.

A paste pipeline should be:

\[
  \mathsf{text}_b
  \xrightarrow{\mathsf{parse}_b}
  \mathsf{BackendAST}_b
  \xrightarrow{\mathsf{import}_b}
  \Result(\mathsf{Expr}^+,E)
  \xrightarrow{\mathsf{freshen}}
  \mathsf{Expr}^+.
\]

Import is not necessarily inverse to rendering; it should preserve as much structure as the common intermediate representation can express and retain unhandled fragments explicitly rather than dropping them.

## No theory-independent mathematical type checker exists

The most important limitation is principled: arbitrary mathematical notation cannot be made semantically sound without selecting a formal language, signature, and notation environment. The editor core cannot decide whether an expression is a valid group equation, category-theory judgment, lambda term, tensor equation, or overloaded informal notation merely from its glyph tree.

The proper extension is a plugin boundary:

\[
  \mathsf{TheoryPlugin}=
  \langle\Sigma,\mathsf{notations},\mathsf{elaborate},\mathsf{check},\mathsf{diagnose},\mathsf{pretty}\rangle.
\]

Each plugin consumes the same MathIR and returns typed core terms or localized diagnostics. Plugins may share infrastructure for metavariables and incremental constraints but must prove their own elaboration and type-soundness properties.

## Proofs are not mechanized

The thesis gives mathematical definitions, theorem statements, and proof sketches. The executable tests check representative laws and traces. There is no machine-checked proof connecting the TypeScript runtime to a formal model.

A full assurance argument requires:

1. mechanized syntax, zipper, validity, and reducer;
2. proofs of lens laws, freshness, determinism, and preservation;
3. verified decoding or a proved correspondence with a trusted decoder;
4. a refinement relation between TypeScript values and formal states;
5. differential or proof-producing extraction evidence.

The current artifact is designed to make that project tractable. It should not be described as formally verified.

## Performance and resource bounds

The validator traverses whole documents, and `commit` invokes it after each command. This is suitable for a reference implementation and modest worksheets but not for very large documents. Deeply nested untrusted input can also exhaust recursion or memory unless decoding imposes limits.

Production hardening should add:

- maximum decoded depth, node count, line count, and string length;
- incremental validity certificates for unchanged subtrees;
- persistent sequence structures;
- iterative folds where stack depth is a concern;
- worker-thread rendering and elaboration;
- cancellation and revision checks for stale asynchronous results.

These optimizations must be validated against the reference semantics.

## Accessibility requires first-class design

The structure is a strong foundation for accessibility, but the prototype does not provide a complete screen-reader interaction model. Requirements include:

- semantic speech for every constructor;
- navigable field roles such as “numerator” and “upper limit”;
- announcement of selection growth and structure entry/exit;
- keyboard-only access to all templates and variants;
- high-contrast, reduced-motion, and scalable-text modes;
- robust focus management across modal search and documentation;
- MathML or accessibility-tree export.

Accessibility should be expressed through algebras and command mappings rather than inferred from visual spans after the fact.

## Recommended extension sequence

A disciplined roadmap is:

### 1. Stabilize the structural core

Expand property tests, add depth/size limits, formalize exact path and renderer laws, and introduce a public package API. Preserve the current reducer as a reference model.

### 2. Replace the demonstration layout

Implement a measured box-tree algebra and accessible semantic tree. Keep cursor decoration separate from syntax folding.

### 3. Add backend ASTs and importers

Represent LaTeX, Typst, MathML, and Unicode output structurally. Compile and round-trip tested subsets in sandboxed environments.

### 4. Mechanize the editor metatheory

Prove zipper laws and reducer preservation in a proof assistant. Establish executable correspondence with the TypeScript core.

### 5. Add one typed theory plugin

Choose a constrained object language, such as simply typed lambda calculus or a small categorical combinator language. Implement bidirectional elaboration and prove soundness. Avoid attempting universal informal mathematics at the outset.

### 6. Add collaboration only after stable identities

Introduce node identities and a structural edit log before attempting remote cursor transformation or CRDT integration.

This order keeps each new claim supported by the layers beneath it.

## Design principles recovered from the source

The supplied component contains several strong ideas that should be retained.

- Treat the document as structure rather than source text.
- Render the structure directly for editing.
- Generate several textual formats from the same document.
- Navigate through template holes.
- Grow selections structurally.
- make mathematical symbols discoverable by semantic aliases.
- let reusable fragments remain syntax rather than flattened text.

The reconstruction does not replace these ideas; it gives them explicit mathematical form. Its corrections follow from the same original premise. If the document truly is an AST, scripts should own their bases, child slots should have a valid blank constructor, paths should be checked, backends should be folds, and editing should preserve a stated validity predicate.

## Final synthesis

The editor can now be summarized by four equations.

The syntax is an initial algebra:

\[
  \mathsf{Expr}=\mu F.
\]

A cursor address resolves to a context and focus:

\[
  \resolve(R,p)=C[R_f].
\]

Editing is an explicit, error-aware transition:

\[
  \mathsf{reduce}:S\times C\to\Result(S,E).
\]

Each backend is a fold:

\[
  \mathsf{render}_b=\cata(\alpha_b).
\]

Around these equations sit the invariants:

\[
  \text{non-empty slots},
  \quad\text{unique holes},
  \quad\text{valid focus},
  \quad\text{bounded selection},
  \quad\text{versioned decoding}.
\]

They are sufficient to make the structural editor coherent. They are not sufficient to prove arbitrary mathematics. For that, the editor tree must elaborate into a typed core under a specified theory, and that core must have its own metatheory and denotation.

## Conclusion

A mathematically sound reconstruction begins by refusing category errors. A path is not automatically a zipper; it is an address from which a zipper can be materialized. A renderer is a denotation of presentation syntax but not yet the meaning of a mathematical term. A TypeScript union excludes some malformed values but does not prove global invariants. Random tests provide evidence but not universal proof. A displayed adjunction symbol is notation, not adjunction data.

Once these distinctions are enforced, the design becomes simpler. The AST is a strictly positive inductive type. Recursive positions are non-empty and blankness is represented by holes. Cursor contexts are derivatives. Local update is a partial lens. Commands are deterministic Kleisli endomorphisms. Renderers are catamorphisms. Undo is a timeline zipper. Persistence is a versioned checked boundary. Typed mathematical meaning is a separate elaboration layer.

The supplied prototype therefore admits a principled evolution rather than a rewrite by taste. Its strongest intuition - one structural document, directly rendered, with several generated outputs - survives intact. The reconstructed system states the laws that intuition requires, implements them in a runnable core, documents the remaining obligations, and provides a foundation on which formal mathematics tooling can be built without confusing visual notation, editor structure, and mathematical truth.


\appendix

# Source-to-model correspondence

## Purpose

This appendix maps the supplied component to the reconstructed abstractions. Line numbers refer to the preserved source artifact in `original/MathKeyboardV3.jsx`. The map is descriptive: it records what the source implements and where the reconstruction intentionally changes semantics.

## Syntax and reflection

| Source lines | Source element | Abstract interpretation | Reconstructed location |
|---:|---|---|---|
| 12--21 | `row`, `sym`, `hole`, `frac`, `sqrtN`, `scr`, `func`, `grp`, `big`, `acc` | Runtime constructors for a recursive sum-of-products syntax | `rebuild/src/model.ts` |
| 23--33 | `FIELD_ORDER`, `fieldsOf` | Recursive-field signature and traversal order | `childFields`, `pathTrace` |
| 35--36 | `isEmptyRow`, `isEmptyNode` | Structural emptiness policy for deletion | `isEmptyStructure` plus explicit holes |
| 39--45 | `getRow`, `setRow` | Path-indexed focus and replacement | `resolvePath`, `focusAt`, `plug`, `replaceAt` |
| 48--70 | trace and hole collection helpers | Canonical depth-first placeholder order | `collectHoles`, `pathTrace`, hole-order fold |

The principal change is from permissive child rows to non-empty recursive slots. `fieldsOf` is retained in spirit as the authoritative child reflection, but the path API becomes checked and materializes zipper contexts.

## Backends

| Source lines | Source element | Abstract interpretation | Reconstructed location |
|---:|---|---|---|
| 74--88 | `latexOf` | An algebra-like recursive interpretation into LaTeX strings | `backends.ts` LaTeX algebra |
| 90--104 | `typstOf` | Draft Typst interpretation with inline mapping table | Typst algebra and symbol catalog |
| 106--124 | `uniOf`, `GEN` | Unicode structural linearization and backend dispatch | Unicode algebra and `renderLine` |
| 126--136 | styled alphabets | Presentation style mapping | identifier style plus backend functions |
| 139--177 | symbol catalog | Searchable semantic inventory mixed with makers | semantic catalog IDs and templates |

The source generators each contain their own recursive switch. The reconstruction moves recursion to `foldExpr` and makes each backend an instance of `SyntaxAlgebra<Piece>`. Unknown cases produce diagnostics rather than empty strings.

## Rendering

| Source lines | Source element | Abstract interpretation | Reconstructed treatment |
|---:|---|---|---|
| 206--235 | `RowView` | Sequence renderer plus caret/selection decoration | Browser box renderer over structural sequences |
| 237--303 | `NodeView` | Constructor-specific visual algebra | Demonstration visual renderer; future measured box algebra |
| 306--327 | `vs` | Constructor layout style table | CSS adapter, not core semantics |

The source renderer is already structurally recursive. The reconstruction interprets it as a layout algebra and separates cursor decoration conceptually from constructor layout.

## State and edits

| Source lines | Source element | Abstract interpretation | Reconstructed location |
|---:|---|---|---|
| 335--350 | React state variables | Document, cursor, UI mode, backend choice, pins, history, effects | Core state separated from adapter state |
| 352--372 | persistence effects | Unversioned delayed snapshot storage | `codec.ts` plus adapter scheduling |
| 374--383 | mutable undo/redo refs | Timeline zipper implemented through JSON snapshots | `history.ts` immutable timeline |
| 389--402 | insertion | Focused sequence splice and first-hole selection | `reduce` / `insert` |
| 410--430 | postfix attachment | Script or accent placement | base-owning scripts; body-owning accents |
| 433--458 | backspace | Selection deletion, structure entry, line removal | checked deletion rules |
| 460--503 | horizontal navigation | Depth-first movement over paths and fields | checked cursor movement |
| 506--513 | hole jump | Trace-ordered cyclic placeholder navigation | same policy over canonical child order |
| 516--527 | selection growth | Token-to-row-to-container ascent | anchor/head structural growth |
| 530--543 | function application | Wrap selection or create a holed function | `wrapFunction` command |
| 547--561 | line, clipboard, pin helpers | Mixed core and adapter operations | new line in reducer; clipboard/pins in adapter |

## Interface policies

| Source lines | Source element | Reconstructed interpretation |
|---:|---|---|
| 564--573 | pointer timer | Long-press adapter policy |
| 575--610 | key layers and navigation keys | Command-producing interface configuration |
| 612--623 | dynamic documentation | User-facing description, audited against semantics |
| 625--673 | naming, variants, search, pins | Adapter modes over syntax templates and catalog |
| 682--800 | component tree | Browser shell and one-way data flow |
| 804--846 | visual chrome | Product styling outside mathematical semantics |

## Corrected mismatches

### A path is not yet a zipper

The source comment calls the cursor representation a zipper, but stored state contains only a path and offsets. The reconstruction reserves *zipper* for the focus plus explicit crumbs created by resolution.

### Accent behavior

The documentation says accents act on a selection or preceding node. The source's no-selection implementation inserts an accent with its default holed child after the cursor. The reconstructed command follows the documented target rule.

### Script ownership

The source script node contains only superscript and subscript rows. Its base is inferred from adjacency. The reconstructed node contains a non-empty base and at least one attachment.

### Annotated arrow

The source long-arrow template reuses an accent constructor with `\xrightarrow`. The reconstruction introduces a dedicated annotated-arrow constructor.

### Indexed root Unicode

The source Unicode backend omits a root index. The reconstruction writes a structural fallback that retains it.

### Persistence

The source stores unversioned JSON and trusts its shape after parsing. The reconstruction uses a schema tag and checked decode.

# Formal definitions and rule summary

## Syntax

Let $\mathsf{Slot}(X)=X^+$ and $\mathsf{Line}(X)=X^*$. Expressions are generated by the functor

\[
\begin{aligned}
F(X)={}&A+H+\mathsf{Slot}(X)^2
+\mathsf{Slot}(X)\times(1+\mathsf{Slot}(X))\\
&+\mathsf{Slot}(X)\times
(\mathsf{Slot}(X)+\mathsf{Slot}(X)+\mathsf{Slot}(X)^2)\\
&+N\times\mathsf{Slot}(X)+D\times\mathsf{Slot}(X)\\
&+O\times(1+\mathsf{Slot}(X))^2
+K\times\mathsf{Slot}(X)+Q\times\mathsf{Slot}(X).
\end{aligned}
\]

Then $\mathsf{Expr}=\mu F$ and $\mathsf{Document}=\mathsf{Line}(\mathsf{Expr})^+$.

## Validity

The central state predicate is

\[
\begin{aligned}
\Valid(S)\iff{}&|D.\mathsf{lines}|\ge1
\land\mathsf{allExprsValid}(D)\\
&\land\mathsf{NoDuplicates}(\mathsf{holeIds}(D))\\
&\land0\le c.\mathsf{line}<|D.\mathsf{lines}|\\
&\land\resolve(D_{c.\mathsf{line}},c.\mathsf{path})=\Ok(Z)\\
&\land0\le c.\mathsf{anchor},c.\mathsf{head}\le|Z.\mathsf{focus}|\\
&\land n>\max\mathsf{AutoHoleSuffix}(D).
\end{aligned}
\]

Every present recursive child is a slot and therefore non-empty. Every script has a base and at least one attachment.

## Path resolution

The empty path resolves to a root zipper:

\[
  R\vdash[]\Downarrow\langle R,\mathsf{line},[]\rangle.
\]

A descent step is admissible when index $i$ selects parent $e$ and field $f$ is present with child slot $S$:

\[
\frac{
 R=L\mathbin{+\!+}[e]\mathbin{+\!+}U
 \quad |L|=i
 \quad \mathsf{getChild}(e,f)=S
 \quad S\vdash p\Downarrow\langle V,k,K\rangle
}{
 R\vdash(i,f)::p\Downarrow
 \langle V,k,\langle\mathsf{kind}(R),L,e,U,f\rangle::K\rangle}.
\]

The executable resolver reports invalid indices and fields rather than deriving a judgment.

## Plugging

At the root:

\[
  \plug(\langle R,\mathsf{line},[]\rangle,V)=V.
\]

For innermost crumb $\langle k,L,e,U,f\rangle$:

\[
\begin{aligned}
 e'&=\mathsf{setChild}(e,f,V),\\
 V'&=L\mathbin{+\!+}[e']\mathbin{+\!+}U,
\end{aligned}
\]

then continue with the outer crumbs. A slot focus rejects $V=[]$.

## Lens laws

For valid fixed path $p$ and admissible replacement $V$:

\[
\begin{aligned}
\mathsf{replace}_p(R,\mathsf{focus}_p(R))&=R,\\
\mathsf{focus}_p(\mathsf{replace}_p(R,V))&=V,\\
\mathsf{replace}_p(\mathsf{replace}_p(R,V_1),V_2)
  &=\mathsf{replace}_p(R,V_2).
\end{aligned}
\]

## Command reducer

\[
  \mathsf{reduce}:S\times C\to E+S.
\]

The reducer validates its input, dispatches on the command constructor, and validates every committed output. Successful transitions satisfy preservation.

## Insertion rule

With focused decomposition $R=L+\!+M+\!+U$ and freshened payload $(V',n')$:

\[
\frac{
 \resolve(D_\ell,p)=K[R]
 \quad \mathsf{freshen}(V,n)=(V',n')
}{
 \langle D,\langle\ell,p,a,h\rangle,n\rangle
 \xrightarrow{\mathsf{Insert}(V)}
 \langle D[\ell:=K[L+\!+V'+\!+U]],c',n'\rangle}.
\]

$c'$ selects the first inserted hole or the boundary after the payload.

## Deletion rule for an emptied slot

If deleting selected interval $M$ would leave a recursive slot empty:

\[
\frac{
 R=M
 \quad \mathsf{focusKind}=\mathsf{slot}
 \quad h_n\notin\mathsf{holes}(D)
}{
 \langle D,c,n\rangle
 \xrightarrow{\mathsf{Backspace}}
 \langle D[\mathsf{focus}:=[h_n]],c_{h_n},n+1\rangle}.
\]

## Rendering

For backend algebra $\alpha_b:F(B_b)\to B_b$:

\[
  \mathsf{render}_b=\cata(\alpha_b).
\]

The concrete carrier is text paired with a list of issues. The visible result ignores hole identities but preserves hole positions.

## Elaboration boundary

For signature $\Sigma$ and context $\Gamma$:

\[
  \Sigma;\Gamma\vdash e\rightsquigarrow t:A\dashv\mathcal C.
\]

Only after successful constraint solving is model interpretation defined:

\[
  \llbracket\Gamma\vdash t:A\rrbracket_{\mathcal M}:
  \llbracket\Gamma\rrbracket_{\mathcal M}\to\llbracket A\rrbracket_{\mathcal M}.
\]

# Public API synopsis

## Model construction

```ts
identifier(name, style?)
number(digits)
symbol(id)
punctuation(text)
hole(id, expected?)
slot(first, ...rest)
fraction(numerator, denominator)
root(radicand, index?)
script(base, superscript?, subscript?)
fn(name, argument)
group(delimiters, body)
largeOperator(operator, lower?, upper?)
accent(kind, body)
annotatedArrow(kind, label)
```

Every recursive argument is a `Slot`. `script` rejects the absence of both attachments.

## Validation and traversal

```ts
childFields(expr): readonly ChildField[]
getChild(expr, field): Slot | undefined
setChild(expr, field, slot): Expr | undefined
validateDocument(document): readonly ValidationIssue[]
```

## Checked focus

```ts
resolvePath(line, path): Result<SequenceZipper, PathError>
focusAt(line, path): Result<readonly Expr[], PathError>
plug(zipper, replacement): Result<Line, PathError>
replaceAt(line, path, replacement): Result<Line, PathError>
```

## Editing

```ts
makeState(lines, cursor?): EditorState
validateEditorState(state): readonly CursorIssue[]
reduce(state, command): Result<EditorState, EditError>
```

Commands are the discriminated union documented in Chapter 6.

## Folds and output

```ts
foldExpr(expr, algebra)
foldSlot(slot, algebra)
foldLine(line, algebra)
renderLine(line, "latex" | "typst" | "unicode")
```

## History and persistence

```ts
timeline(initial)
dispatch(history, command)
undo(history)
redo(history)
encodeState(state)
decodeState(json)
```

# Selected exercise solutions

## Solution 1: derivative of a binary-tree layer

For

\[
  F(X)=A+X\times X,
\]

we have

\[
  F'(X)=0+(1\times X+X\times1)\cong X+X.
\]

The two summands distinguish a hole in the left child with a stored right child and a hole in the right child with a stored left child. A recursive zipper stores a list of these left/right contexts.

## Solution 2: list contexts

A list with one distinguished element decomposes uniquely as

\[
  L\mathbin{+\!+}[x]\mathbin{+\!+}R.
\]

Erasing the distinguished $x$ leaves the pair $(L,R)\in X^*\times X^*$. Conversely, given $(L,R)$ and a filling $x$, concatenation reconstructs the list. Hence

\[
  (X^*)'\cong X^*\times X^*.
\]

## Solution 3: PutGet failure by truncation

Suppose `put` silently keeps only the first element of a requested replacement. Let $V=[x,y]$. Then

\[
  \mathsf{get}(\mathsf{put}(s,V))=[x]\ne[x,y]=V.
\]

Thus PutGet fails. The reconstructed replacement operation either installs the complete sequence or returns an error.

## Solution 4: empty numerator deletion

A fraction constructor requires numerator and denominator slots. If deleting the only numerator expression produced `[]`, the result would not inhabit the constructor's domain. Replacing it by a fresh hole yields a one-element valid slot and retains an edit target.

## Solution 5: path of a nested denominator

For a line whose first expression is a root and whose radicand's second expression is a fraction, the fraction denominator path is

\[
  [(0,\mathsf{radicand}),(1,\mathsf{denominator})].
\]

Resolution first selects the root at index $0$, then its radicand; inside that slot it selects the fraction at index $1$, then its denominator.

## Solution 6: preservation under script merging

Assume the base selection is a single valid script with base slot $b$ and superscript $u$, and the command attaches valid subscript $l$. The smart constructor produces `ScriptBoth(b,u,l)`. All three slots are non-empty and valid by assumption/freshening; the constructor has at least one attachment; replacing one valid selected expression by this valid expression preserves its containing sequence; plugging preserves all ancestors. Hole freshness follows from freshening $l$.

## Solution 7: editor validity versus object typing

The line $[g,\circ,f]$ is structurally valid whenever all three atoms are valid. It may be object-language ill-typed when $f:A\to B$ and $g:D\to C$ with $B\ne D$. An edit can therefore preserve editor validity while creating a composition error in the elaborator.

## Solution 8: product algebra

Given size result $n$ and hole-order result $hs$ for each child, define each constructor result as a pair. For a fraction:

\[
  \alpha_{\times}(\mathsf{Frac}((n_1,h_1),(n_2,h_2)))
  =(1+n_1+n_2,h_1\mathbin{+\!+}h_2).
\]

The induced fold computes size and hole order simultaneously.

## Solution 9: document-wide hole trace

Prefix each line-local hole trace with the line index:

\[
  \mathsf{docTrace}(\ell,p,i)=[\ell]\mathbin{+\!+}\mathsf{trace}(p)\mathbin{+\!+}[i].
\]

Lexicographic order then traverses lines in order and holes structurally within each line. Forward and backward jumps wrap at the document ends.

## Solution 10: checked cursor decode

A proof-producing decoder first decodes the line index and path, resolves the path in the decoded document, obtains focus length $n$, and decodes anchor/head as members of `Fin(n+1)`. Its success value contains bounded indices by construction. A Boolean validator would only state success without carrying those witnesses.

## Solution 11: MathML fraction algebra

For carrier XML nodes, define

\[
  \alpha(\mathsf{Frac}(n,d))=	exttt{<mfrac>}n\;d\texttt{</mfrac>}.
\]

Sequences become `<mrow>` nodes; roots become `<msqrt>` or `<mroot>`; scripts become `<msup>`, `<msub>`, or `<msubsup>`. The fold supplies all recursion.

## Solution 12: branching undo

After undo, history has a non-empty future. Committing a new state clears that future. Therefore redo cannot recover the abandoned branch. Retaining it would require a tree or DAG history rather than a linear zipper.

# Reproduction and package guide

## Bundle layout

```text
structural_editor_thesis/
├── README.md
├── AUDIT.md
├── original/
│   └── MathKeyboardV3.jsx
├── rebuild/
│   ├── src/
│   ├── tests/
│   ├── web/
│   ├── package.json
│   └── tsconfig.json
├── thesis/
│   ├── structural-math-editor-thesis.md
│   └── structural-math-editor-thesis.pdf
├── figures/
│   ├── *.dot
│   └── *.png
├── screenshots/
│   └── *.png
└── verification/
    ├── test-output.txt
    └── pdf-inspection.txt
```

Generated JavaScript under `rebuild/dist/` is included in the final archive after compilation.

## Build and test

From the `rebuild` directory:

```bash
npm run build
npm test
```

The project requires Node.js and the TypeScript compiler available to `npm`. It has no application runtime dependencies.

## Run the browser prototype

```bash
cd rebuild
npm run build
python -m http.server 8000
```

Then open:

```text
http://localhost:8000/web/index.html
```

Serving over HTTP avoids browser restrictions on module loading from `file:` URLs.

## Rebuild the thesis PDF

From the `thesis` directory, with Pandoc and XeLaTeX installed:

```bash
pandoc structural-math-editor-thesis.md \
  --from markdown+raw_tex \
  --pdf-engine=xelatex \
  --resource-path=..:../figures:../screenshots \
  --highlight-style=tango \
  -o structural-math-editor-thesis.pdf
```

The Markdown YAML selects Noto Serif, Inter, DejaVu Sans Mono, and STIX Math. Substitute installed fonts if necessary.

## Verify the PDF

Render every page to PNG images:

```bash
python /home/oai/skills/pdfs/scripts/render_pdf.py \
  structural-math-editor-thesis.pdf \
  --out_dir ../verification/pdf-renders \
  --dpi 150
```

Inspect the title, table of contents, equations, tables, screenshots, code blocks, appendix, and bibliography. Also run `pdfinfo`, `pdffonts`, and text extraction to detect missing fonts or malformed output. The final bundle contains an inspection summary rather than the full page-render directory.

## Screenshot provenance

- `baseline-editor.png` is a static reconstruction of the supplied component's visible interface, created from its dimensions, styles, labels, and demonstration formula.
- `rebuilt-editor.png` is captured from the included rebuilt browser artifact.
- `verification-tests.png` is captured from the included test-report page populated with the actual test output.

The static baseline is labeled as such in the thesis and is not represented as a capture from an independently deployed original application.

# Glossary

**Algebra.** A carrier together with one interpretation operation for each layer of a functor.

**Anchor/head selection.** A directed pair of sequence boundaries; its normalized span is the selected interval.

**Catamorphism.** The unique fold from an initial algebra to a chosen algebra.

**Codec.** A versioned encoder and checked decoder between editor states and persisted data.

**Container.** A representation of a strictly positive functor by shapes and positions.

**Cursor path.** A serializable list of index/field steps from a root line to a recursive sequence.

**Denotational semantics.** A compositional assignment of mathematical values to syntax; in this thesis, backend rendering and object-level mathematical interpretation are distinct denotational layers.

**Elaboration.** Context-dependent translation from notation-level syntax into a typed core term, often generating constraints and metavariables.

**Hole.** A uniquely identified editable placeholder; at the object-language layer it may correspond to a metavariable.

**Initial algebra.** An algebra with a unique homomorphism into every algebra for the same functor.

**Kleisli arrow.** A function whose result is wrapped in a monadic effect; editor commands use the exception effect.

**Lens.** A get/put interface satisfying local-update laws; path focus is partial because addresses may be invalid.

**MathIR.** The presentation-neutral structural representation shared by rendering and later elaboration.

**Operational semantics.** Rules or functions defining how commands transform editor configurations.

**Preservation.** The property that successful transitions from valid states return valid states.

**Slot.** A non-empty recursive sequence of expressions.

**Structural selection.** A selection that expands through sequence and ancestor boundaries determined by syntax, not pixels.

**Timeline zipper.** A past/present/future representation supporting undo and redo.

**Zipper.** A focused value paired with contexts sufficient to reconstruct its root.

# Bibliography

Abbott, Michael, Thorsten Altenkirch, and Neil Ghani. 2005. “Containers: Constructing Strictly Positive Types.” *Theoretical Computer Science* 342 (1): 3--27. https://doi.org/10.1016/j.tcs.2005.06.002.

Foster, J. Nathan, Michael B. Greenwald, Jonathan T. Moore, Benjamin C. Pierce, and Alan Schmitt. 2007. “Combinators for Bidirectional Tree Transformations: A Linguistic Approach to the View-Update Problem.” *ACM Transactions on Programming Languages and Systems* 29 (3), Article 17. https://doi.org/10.1145/1232420.1232424.

Goguen, Joseph A., James W. Thatcher, Eric G. Wagner, and Jesse B. Wright. 1977. “Initial Algebra Semantics and Continuous Algebras.” *Journal of the ACM* 24 (1): 68--95.

Harper, Robert. 2016. *Practical Foundations for Programming Languages*. 2nd ed. Cambridge: Cambridge University Press.

Huet, Gérard. 1997. “The Zipper.” *Journal of Functional Programming* 7 (5): 549--554.

Lambek, Joachim. 1968. “A Fixpoint Theorem for Complete Categories.” *Mathematische Zeitschrift* 103: 151--161. https://doi.org/10.1007/BF01110627.

McBride, Conor. 2001. “The Derivative of a Regular Type Is Its Type of One-Hole Contexts.” Extended abstract and manuscript.

Pierce, Benjamin C. 2002. *Types and Programming Languages*. Cambridge, MA: MIT Press.

Plotkin, Gordon D. 1981. *A Structural Approach to Operational Semantics*. DAIMI FN-19, Aarhus University. Revised version published in *Journal of Logic and Algebraic Programming* 60--61 (2004): 17--139.

Scott, Dana S., and Christopher Strachey. 1971. *Toward a Mathematical Semantics for Computer Languages*. Technical Monograph PRG-6, Oxford University Computing Laboratory.

Typst GmbH. 2026. “Typst Documentation: Math, Fractions, Roots, Attachments, Accents, Operators, Delimiters, and Symbols.” Official documentation, accessed 6 August 2026.


