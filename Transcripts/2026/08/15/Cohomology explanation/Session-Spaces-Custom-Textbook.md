---
title: "Session Spaces"
subtitle: "Category Theory, Topoi, Sheaves, and Cohomology through SessionStream"
author: "A custom study companion prepared for a software engineer"
date: "15 August 2026"
lang: en-US
documentclass: book
classoption:
  - 11pt
  - oneside
geometry:
  - margin=1in
fontsize: 11pt
linestretch: 1.08
toc: true
toc-depth: 2
numbersections: true
colorlinks: true
linkcolor: blue
urlcolor: blue
citecolor: blue
header-includes:
  - |
    \usepackage{microtype}
    \usepackage{booktabs}
    \usepackage{longtable}
    \usepackage{array}
    \usepackage{amssymb}
    \usepackage{stmaryrd}
    \usepackage{xcolor}
    \usepackage{enumitem}
    \usepackage{fancyhdr}
    \usepackage{titlesec}
    \usepackage{caption}
    \usepackage{float}
    \definecolor{MidnightBlue}{RGB}{20,55,100}
    \definecolor{SoftGray}{RGB}{245,246,248}
    \pagestyle{fancy}
    \fancyhf{}
    \fancyhead[L]{\footnotesize Session Spaces}
    \fancyhead[R]{\footnotesize\nouppercase{\leftmark}}
    \fancyfoot[C]{\thepage}
    \setlength{\headheight}{16pt}
    \setlist[itemize]{topsep=3pt,itemsep=2pt,parsep=1pt}
    \setlist[enumerate]{topsep=3pt,itemsep=2pt,parsep=1pt}
    \captionsetup{font=small,labelfont=bf}
    \titleformat{\chapter}[display]{\normalfont\huge\bfseries}{\chaptertitlename\ \thechapter}{14pt}{\Huge}
---

\frontmatter

# Preface {-}

This is an original, software-grounded companion to Robert Goldblatt's *Topoi: The Categorial Analysis of Logic*. It follows the dependency order and much of the conceptual itinerary of that book, but it does not reproduce its exposition or exercises. Definitions are restated in new language, examples are rebuilt around event-driven software, and the exercises are newly written.

The central running system is [`sessionstream`](https://github.com/go-go-golems/sessionstream), read at repository commit `d62dca9f5efa` from 13 August 2026 (the full commit is recorded in Appendix E). The principal source paths are the `Hub`, event and projection types, hydration interfaces and SQLite store, ordinal assignment, WebSocket snapshot-before-live protocol, and the chat demonstration. The Architecture Garden analysis at `parc.yolo.scapegoat.dev` supplies additional explicit laws: per-session serializability, consistent-cut snapshots, stable retry identity, atomic projection progress, deterministic replay, and snapshot-plus-suffix completeness.

Goldblatt's book is about categorical logic rather than category theory in isolation. This companion keeps that emphasis. Category theory is introduced as a method for replacing hidden element-level implementation details with observable relationships, universal properties, and transformations that remain meaningful across representations. Topos theory then turns those constructions into a setting where predicates, truth values, quantifiers, and local reasoning can be treated structurally.

Cohomology is not developed in Goldblatt's book. Chapters 17-20 therefore form a clearly marked supplement. They build on the preceding treatment of limits, presheaves, sheaves, and local-to-global reasoning, then introduce nerves, cochains, coboundaries, and low-dimensional cohomology as tools for studying the shape of compatibility data.

## The mental picture

A SessionStream execution is never seen from one omniscient place. A handler sees a command and a publisher. A projector sees an event and a timeline view. A store sees rows and cursors. A WebSocket subscriber sees a snapshot followed by live batches. An operator sees traces. A browser sees decoded transport frames. These views overlap, but no view is identical to the complete execution.

The main mathematical question of this book is therefore:

\[
\textit{When do locally meaningful observations assemble into one coherent global execution?}
\]

Category theory gives the language of the observations and their relationships. Limits describe compatible assemblies. Presheaves describe how information restricts from larger contexts to smaller ones. Sheaves say when compatible local information glues uniquely. Cohomology can sometimes detect persistent obstruction patterns around loops of overlap.

![The running architecture. A command produces a canonical event; independent projections derive live and durable views; reconnects combine a snapshot with a future suffix.](figures/01-sessionstream-architecture.png){width=95%}

## You are here

You reported being at the limits section of Goldblatt Chapter 3, which is §3.11 in the supplied edition. That is the correct point to slow down. Products, equalizers, terminal objects, and limits are not a miscellaneous collection of constructions. They are the first appearance of the general pattern that later becomes:

- pullbacks and subobjects;
- finite completeness in a topos;
- the sheaf gluing condition as a limit;
- reindexing and quantifiers through adjunctions;
- compatible observations and obstruction theory.

A practical route is:

1. Read Chapters 1-3 here quickly, doing only the starred exercises.
2. Work through Chapter 4 slowly. Re-draw every universal-property diagram from memory.
3. Continue through Chapters 5-12 with one SessionStream notebook example per section.
4. Spend substantial time on Chapters 13-15. These contain the presheaf/sheaf bridge you were originally looking for.
5. Treat Chapters 17-20 as a second pass, not as prerequisites for understanding sheaves.

## How each chapter works

Each chapter contains five recurring components.

**Source alignment** identifies the corresponding part of Goldblatt. This tells you what is source-derived in organization and conceptual emphasis.

**Core mathematics** gives definitions and small proofs. Definitions are intended to be usable, not merely suggestive.

**SessionStream translation** constructs a model from actual concepts in the repository. The translation is sometimes exact and sometimes analogical; the text labels that distinction.

**Shape intuition** gives the geometric or multidimensional picture. These pictures are aids, not replacements for definitions.

**Exercises** move through four levels:

- *recognition*: identify a categorical structure;
- *calculation*: construct an arrow, limit, or restriction;
- *proof*: verify a universal property or law;
- *design*: apply the concept to SessionStream or another system.

Selected hints and solutions appear in Appendix B. A problem marked **[proof]** is worth writing in complete mathematical prose. A problem marked **[lab]** is intended for code or trace data. A problem marked **[research]** may not have one canonical answer.

## Conventions

Composition is written in the mathematical order:

\[
g\circ f:A\to C
\]

means first run \(f:A\to B\), then \(g:B\to C\). In code this often appears in the opposite visual order:

```go
c := g(f(a))
```

`Set` denotes the category of sets and total functions. `1` denotes a terminal object; in `Set`, any singleton is terminal. `0` denotes an initial object; in `Set`, the empty set is initial.

For a category \(\mathcal C\), the set of arrows from \(A\) to \(B\) is written

\[
\mathcal C(A,B)\quad\text{or}\quad \operatorname{Hom}_{\mathcal C}(A,B).
\]

For a fixed session \(s\), \(E_s^*\) denotes the set of finite event histories for that session. Concatenation is written by juxtaposition, and \(\epsilon\) is the empty history.

A prefix relation is written

\[
x\preceq y \quad\Longleftrightarrow\quad \exists z\;xz=y.
\]

The phrase *global section* is used in its sheaf-theoretic sense: a section over the largest context under discussion. It does not mean a global variable.

## A warning about software metaphors

There is no single canonical "category of software". A category is a model chosen for a purpose. You must specify:

1. what the objects are;
2. what the arrows are;
3. when arrows compose;
4. what equality of arrows means;
5. why identity and associativity hold.

Side effects, exceptions, concurrency, nondeterminism, resource limits, and observational equivalence can all force a different choice of category. When this book says "model a projection as an arrow," it means that we have abstracted enough operational detail to obtain a deterministic mathematical map. It does not claim that arbitrary Go functions form a simple category under all runtime observations.

## Source map

The Goldblatt alignment is:

| This companion | Goldblatt |
|---|---|
| Chapters 1-2 | Chapters 1-2 |
| Chapters 3-4 | Chapter 3 |
| Chapters 5-6 | Chapters 4-5 |
| Chapters 7-8 | Chapters 6-8 |
| Chapters 9-12 | Chapters 9-13 |
| Chapters 13-14 | Chapter 14 |
| Chapter 15 | Chapter 15 |
| Chapter 16 | Chapter 16 |
| Chapters 17-20 | Supplemental material beyond Goldblatt |

The most important SessionStream files for this edition are:

```text
pkg/sessionstream/types.go
pkg/sessionstream/hub.go
pkg/sessionstream/projection.go
pkg/sessionstream/hydration.go
pkg/sessionstream/ordinals.go
pkg/sessionstream/consumer.go
pkg/sessionstream/schema.go
pkg/sessionstream/hydration/sqlite/store.go
pkg/sessionstream/transport/ws/server.go
examples/chatdemo/chat.go
proto/sessionstream/v1/transport.proto
```

\mainmatter

# Mathematical Universes and Engineering Boundaries

**Source alignment:** Goldblatt, Chapter 1, especially the contrast between set-membership descriptions and structural descriptions.

## Why foundations matter to a software engineer

A software system is usually introduced by listing its data structures. SessionStream appears to begin with `Command`, `Event`, `UIEvent`, `TimelineEntity`, and `Snapshot`. That is analogous to beginning mathematics with sets and their members.

But a list of structures does not yet explain the architecture. The architecture lies in relationships:

- a command is routed to a handler;
- a handler publishes events;
- an event is interpreted by projections;
- a timeline entity is applied to a store;
- a snapshot represents a cut of materialized history;
- a live batch is delivered only to matching subscriptions.

Goldblatt's opening move is to question whether membership must be the primitive language of mathematics. Category theory proposes that arrows and composition can be primary instead. The engineering analogue is to resist explaining a component solely by its fields and internal algorithm. Explain it by the arrows it admits, the diagrams it must make commute, and the universal properties it satisfies.

This is not anti-data. Objects still exist. It is a change in what counts as a stable explanation.

Consider these two descriptions of a snapshot.

**Representation-level description**

```go
type Snapshot struct {
    SessionId       SessionId
    SnapshotOrdinal uint64
    Entities        []TimelineEntity
}
```

**Structural description**

A snapshot at cut \(n\) is an observation of a session state that is compatible with the event prefix through \(n\), and that can be combined with every accepted live suffix strictly after \(n\) to reconstruct later client state.

The first is necessary for implementation. The second survives a change from SQLite to another store, a change in serialization, and many changes in entity layout. Category theory is largely a discipline for finding the second kind of description.

## Objects are relative to a discourse

Goldblatt treats a category as a universe of mathematical discourse. The objects and arrows depend on what is being discussed.

In software, the same runtime entity can appear as a different object in different categories.

- A protobuf message can be an object in a category of schemas and schema-preserving transformations.
- The same message value can be an object in a category of runtime values and pure functions.
- Its encoded bytes can be an object in a category of wire representations and codecs.
- The event carrying it can be an object in a category of session histories and prefix extensions.

No contradiction is involved. A model selects some distinctions and suppresses others.

A useful criterion is:

> A categorical model is good when its arrow equality matches the observations relevant to the law being studied.

For a codec law, byte-for-byte equality may matter. For a client rendering law, two protobuf encodings may be considered equal when they decode to the same semantic value. For a concurrency proof, timing and order may matter even when final values agree.

## Internal and external descriptions

An *internal* description talks about constituents:

\[
A\times B=\{(a,b):a\in A, b\in B\}.
\]

An *external* description talks about arrows into and out of the object. A product is characterized by two projections and a unique mediating arrow. Chapter 4 develops that example fully.

The same distinction appears in API design.

An internal description of a valid event says:

```text
name is a nonempty string
payload is a protobuf message
session id is nonempty
payload descriptor happens to match the registered descriptor
```

An external description can identify a valid event as a pullback of two maps into a common descriptor space. The validity condition is no longer an ad hoc conjunction; it is the universal object of matching names and payload types. We construct this in Chapter 4.

External descriptions are especially valuable when:

- representations change;
- several implementations must satisfy one contract;
- a property must be transported through a functor;
- the system has many partial observers;
- local facts must be assembled into a global fact.

## Equality is a design decision

Mathematics often treats functions extensionally:

\[
f=g \quad\Longleftrightarrow\quad \forall x,\; f(x)=g(x).
\]

Go function values do not support general equality, and two implementations with the same outputs may differ in latency, allocation, logging, I/O, or failure behavior. Therefore a category of software functions must state which effects are abstracted away.

For example, a projection can be modeled as a pure arrow

\[
p:S\times E\to S\times U^*
\]

only under an abstraction in which:

- the prior view \(S\) and event \(E\) contain every relevant input;
- clocks, randomness, mutable globals, and network calls are absent or represented explicitly;
- the output state and UI word are the observations that define equality.

This explains the SessionStream deterministic replay obligation. If live projection and replay use the same explicit coordinates but still differ, either the implementation violates the modeled arrow or the model omitted a coordinate.

## A first running model: histories as words

For a fixed session \(s\), let \(E_s\) be the set of admitted event values. A finite history is a word

\[
h=e_1e_2\cdots e_n\in E_s^*.
\]

The empty word is \(\epsilon\). Concatenation is associative:

\[
(xy)z=x(yz).
\]

This is already a one-object category: the sole object represents the state space, and every history is an endomorphism-shaped program fragment. Composition is concatenation. The identity arrow is \(\epsilon\).

A stateful fold gives an action of this history monoid on states:

\[
\operatorname{fold}(S_0,xy)
=
\operatorname{fold}(\operatorname{fold}(S_0,x),y).
\]

That equation is not merely a convenient implementation property. It is the compatibility between monoid composition and interpretation.

SessionStream does not imply that events commute. Usually

\[
e_1e_2\ne e_2e_1
\]

as words, and their folds can differ. The category remembers order through composition.

## What this perspective buys you

The categorical perspective can separate four questions that are often mixed together.

1. **Well-formedness:** Is a value admitted by the schema and type contract?
2. **Composability:** Can two transformations legally be composed?
3. **Equivalence:** Are two representations or implementations the same for the observations under study?
4. **Universality:** Is an object the canonical solution to a whole family of compatible problems?

The fourth question is the distinctive one. A product is not merely a pair type. A pullback is not merely a database join. A limit is not merely an aggregate. Each is characterized by the unique factorization of every competing solution.

## Exercises

**1.1 [recognition].** Give three different choices of objects and arrows for modeling SessionStream. For each, state what equality of arrows should mean.

**1.2 [proof].** Prove associativity of concatenation for finite event words. Then explain why this proof does not prove that concurrent publication is serializable.

**1.3 [design].** A projector reads `time.Now()` and inserts the timestamp into a timeline entity. List two ways to obtain a mathematically deterministic arrow. Which way better supports replay?

**1.4 [recognition].** Classify each statement as primarily internal or external.

1. A `TimelineEntity` has fields `Kind`, `Id`, and `Payload`.
2. Every update of an existing entity factors through its stable `(Kind, Id)` identity.
3. A snapshot contains a list of entities.
4. A snapshot glues with every later suffix satisfying the ordinal boundary.

**1.5 [research].** Choose one architectural promise in your own software. Write a representation-level definition and a structural definition. Identify which changes would preserve the structural definition.

# Categories of Software Processes

**Source alignment:** Goldblatt, Chapter 2: functions, composition, categories, abstraction, and basic examples.

## The definition

> **Definition.** A category \(\mathcal C\) consists of objects, arrows, domain and codomain assignments, a partially defined composition operation, and an identity arrow \(1_A:A\to A\) for each object \(A\), satisfying associativity and identity laws.

If

\[
A\xrightarrow{f}B\xrightarrow{g}C,
\]

then the composite is

\[
g\circ f:A\to C.
\]

![Composition.](figures/02-category-composition.png){width=60%}

The laws are

\[
h\circ(g\circ f)=(h\circ g)\circ f
\]

whenever the composites make sense, and

\[
1_B\circ f=f=f\circ 1_A.
\]

These laws say that a long pipeline has a stable meaning independent of parenthesization, and that doing nothing before or after a transformation changes nothing.

The laws are equations of arrows, so arrow equality must already have been chosen.

## The category `Set`

`Set` has sets as objects and total functions as arrows. It is the primary motivating example for Goldblatt and for elementary topos theory.

Many software examples initially live in `Set` after abstraction:

- the set of valid commands;
- the set of events;
- the set of timeline states;
- a deterministic decoder as a function from valid bytes to messages;
- a projection as a function between mathematical state sets.

Partial functions require adjustment. You can represent a partial function \(A\rightharpoonup B\) as a total function

\[
A\to B+\{\mathsf{error}\},
\]

or work in a category designed for partial maps. Exceptions and cancellation should not be silently ignored.

## Posets as categories

A preorder \((P,\leq)\) becomes a category by declaring that there is one arrow

\[
p\to q
\]

exactly when \(p\leq q\). Reflexivity supplies identities; transitivity supplies composition. Because there is at most one arrow between two objects, all parallel arrows are equal.

This example is crucial because many information structures are ordered.

### Event cuts

For one session, let the objects be natural-number cuts

\[
0,1,2,\ldots
\]

and let there be an arrow \(m\to n\) when \(m\leq n\). The arrow means that cut \(n\) contains at least as much event-prefix information as cut \(m\).

### Event histories

Let objects be histories, with an arrow

\[
x\to y
\]

when \(x\preceq y\). This category distinguishes histories with the same length but different events. An arrow records extension by some suffix.

### Invariant strength

Let objects be predicates and put an arrow \(P\to Q\) when \(P\) implies \(Q\). Then products will become conjunctions and exponentials will relate to implication. This is the order-theoretic doorway into Heyting algebras.

## Monoids as one-object categories

A monoid \((M,\cdot,e)\) is a category with one object \(*\). Every element \(m\in M\) is an arrow \(*\to *\); composition is multiplication; \(e\) is the identity.

For SessionStream, \(E_s^*\) is the free monoid of histories. A projection fold is then a monoid action or, equivalently, a functor from this one-object category into a category of state transformations.

This viewpoint turns a long history from a passive list into a composed arrow.

## A category of typed transformations

Let objects be selected semantic types:

```text
Command
Event
TimelineState
Snapshot
ClientState
WireFrame
```

Let arrows be pure total transformations between them. Potential arrows include:

\[
\operatorname{validate}:\text{RawCommand}\to\text{Command}+\text{Error},
\]

\[
\operatorname{project}:\text{TimelineState}\times\text{Event}\to\text{TimelineState},
\]

\[
\operatorname{encode}:\text{Snapshot}\to\text{WireFrame}.
\]

This forms a category only after error values and effects are treated consistently. A Go function that panics is not a total arrow under ordinary value semantics. A function that mutates hidden state may not compose extensionally as expected.

A safer approach is to define arrows as explicit effectful computations in a category appropriate to those effects. Later category theory describes this using constructions such as Kleisli categories, although that topic is outside Goldblatt's route and outside the core of this book.

## A transition category

An alternative model keeps operational steps visible.

- Objects are runtime states.
- An arrow \(x\to y\) is an allowed finite trace taking state \(x\) to state \(y\).
- Composition concatenates traces.
- The empty trace is an identity.

This is a category when traces compose associatively and trace equality is chosen coherently. If two different traces between the same states remain distinct, the category can contain many parallel arrows. That is useful for observer and refinement work: final-state equality does not erase evidence about how the state was reached.

A heartbeat implementation, for example, can have arrows labeled by timer firing, ping enqueue, successful write acknowledgement, pong reception, and timeout. The state-transition category retains the distinction between "ping intended" and "ping actually written."

## SessionStream is a diagram, not one object

It is tempting to say "SessionStream is a category." That is too vague. A more useful statement is:

> SessionStream supplies several categories and functors between them, arranged in an architecture diagram.

Examples include:

- a category of command/event schemas;
- a category of session histories;
- a category of timeline states and transitions;
- a category of transport frames;
- a category of observation contexts;
- a preorder of cuts or checkpoints.

The architecture itself can be studied as a diagram whose nodes are these domains and whose arrows are validation, projection, storage, encoding, and restriction operations.

## Commutative diagrams as executable laws

A diagram commutes when every directed path with the same start and finish gives the same arrow.

For deterministic replay, one desired square is:

\[
\begin{array}{ccc}
(H_0,e_1\cdots e_n) & \xrightarrow{\text{live application}} & S_n\\
\downarrow \text{persist/reload} & & \downarrow \text{identity}\\
(H_0,e_1\cdots e_n) & \xrightarrow{\text{rebuild}} & S_n.
\end{array}
\]

The square says that live materialization and replay are equal under the chosen state observation.

A test can sample this law. A proof can establish it for a model. A refinement argument can connect the model to the Go implementation.

## Exercises

**2.1 [proof].** Verify that the prefix relation on finite histories is reflexive, transitive, and antisymmetric. Conclude that it defines a poset category.

**2.2 [design].** Define a category whose objects are SessionStream schemas and whose arrows are backward-compatible migrations. State a composition law. Identify at least one reason the proposed arrows may fail to be closed under composition.

**2.3 [recognition].** Model a bounded queue as a transition category. Give two distinct parallel arrows between the same start and end states that should not be identified if drop accounting matters.

**2.4 [proof].** In a preorder category, show that every diagram with the same source and target commutes.

**2.5 [lab].** Extract a trace from a SessionStream test or log. Represent each runtime state as a node and each observed transition as an edge. Determine whether concatenating adjacent edges always yields another valid trace in your model.

**2.6 [research].** Write one commutative square for each of the following: codec round-trip, snapshot reconstruction, schema validation, and projection replay. State exactly what equality means in each square.

# Cancellation, Isomorphism, and Distinguished Objects

**Source alignment:** Goldblatt §§3.1-3.7: monic, epic, and iso arrows; isomorphic objects; initial and terminal objects; duality.

## Monic arrows

> **Definition.** An arrow \(m:A\to B\) is **monic** if it is left-cancellable: for all \(g,h:X\to A\),
>
> \[
> m\circ g=m\circ h\quad\Longrightarrow\quad g=h.
> \]

In `Set`, monic arrows are exactly injective functions. But the definition is arrow-theoretic and can behave differently in other categories.

A software interpretation in a concrete function category is *information preservation*. If `encode : Event -> Bytes` is monic, then two event-producing computations cannot become indistinguishable after encoding. This requires an injective encoding over the modeled event set.

A hash is generally not monic: collisions identify distinct inputs. A projection from a full event to a UI event is usually not monic: several backend events may intentionally have the same UI observation.

Monicity is relative to the category. If the domain category already identifies events by a coarse observational equivalence, a lossy representation may still be monic with respect to that quotient.

## Epic arrows

> **Definition.** An arrow \(e:A\to B\) is **epic** if it is right-cancellable: for all \(g,h:B\to X\),
>
> \[
> g\circ e=h\circ e\quad\Longrightarrow\quad g=h.
> \]

In `Set`, epic arrows are exactly surjective functions. Epics say that downstream behavior is determined by behavior on the image of \(e\).

A parser from valid wire frames onto all semantic frame variants may be epic when every semantic value has some accepted encoding. Canonical encoders are often not surjective onto all byte strings, but the associated decoder may be surjective onto semantic values.

Do not equate epic with surjective outside concrete set-like categories. Goldblatt emphasizes this early because arrow definitions are meant to survive changes of universe.

## Isomorphisms

> **Definition.** An arrow \(f:A\to B\) is an **isomorphism** if there is an arrow \(f^{-1}:B\to A\) such that
>
> \[
> f^{-1}\circ f=1_A,
> \qquad
> f\circ f^{-1}=1_B.
> \]

An isomorphism is a reversible change of representation in the category. It is stronger than having a one-way migration and stronger than being both monic and epic in an arbitrary category.

A codec pair is an isomorphism only if both round trips are identities under the chosen equality:

\[
\operatorname{decode}(\operatorname{encode}(x))=x,
\]

\[
\operatorname{encode}(\operatorname{decode}(b))=b.
\]

The second law fails for many practical codecs because decoding then re-encoding canonicalizes the bytes. In that case semantic values may be isomorphic to *canonical encodings*, not to all accepted encodings.

This distinction is productive. It tells you which object should appear in the model.

## Isomorphic objects and representation independence

Objects \(A\) and \(B\) are isomorphic when there is an isomorphism between them. Category theory normally treats isomorphic objects as structurally interchangeable, while keeping them technically distinct.

Examples:

- a timeline entity map and a sorted list with unique keys can be isomorphic if each representation determines the other;
- a snapshot protobuf and a domain snapshot can be isomorphic under a lossless codec;
- an event history and a compressed history are not isomorphic if compression discards information needed for replay;
- a live UI stream and a final snapshot are not isomorphic because the live stream contains temporal observations not generally recoverable from final state.

"Same data" should therefore be replaced by a specific isomorphism claim with explicit round-trip laws.

## Initial objects

> **Definition.** An object \(0\) is **initial** if for every object \(A\) there is exactly one arrow
>
> \[
> 0\to A.
> \]

In `Set`, the empty set is initial. In a category of types and total functions, an uninhabited type plays this role: from an impossible value one can produce a value of any type, because there is no input case to handle.

In a transition category, an initial object can represent a unique origin state from which every modeled execution has one canonical initialization arrow. That is a stronger property than merely having a startup state; uniqueness matters.

## Terminal objects

> **Definition.** An object \(1\) is **terminal** if for every object \(A\) there is exactly one arrow
>
> \[
> A\to 1.
> \]

In `Set`, any singleton is terminal. The unique function forgets all information.

In software, the unit type is terminal in a category of pure total functions. Every computation can discard its result:

```go
func discard[A any](A) struct{} { return struct{}{} }
```

Terminal objects encode a universal form of forgetting. They also allow generalized elements: an element of \(A\) is represented by an arrow \(1\to A\). This becomes important for categorical logic, where "elements" are replaced by arrows from arbitrary contexts, not only from \(1\).

## Duality

Every category \(\mathcal C\) has an opposite category \(\mathcal C^{op}\) with the same objects and all arrows reversed. A theorem has a dual obtained by reversing arrows and composition order.

Pairs of dual notions include:

| Notion | Dual |
|---|---|
| monic | epic |
| initial | terminal |
| product | coproduct |
| equalizer | coequalizer |
| pullback | pushout |
| limit | colimit |

Duality is not a vague symmetry. It is a method for generating definitions and proofs.

For information systems, reversal often exchanges "assemble" and "decompose," or "consume" and "produce." The analogy can help, but the formal dual is always defined by reversing arrows in a specified category.

## Session identity is not ordinal identity

A useful application of these distinctions concerns `SessionId` and `Ordinal`.

An ordinal is intended as a per-session sequence coordinate. It is not necessarily a globally monic identifier of events: two sessions can have the same ordinal, and bus redelivery may assign a new ordinal to the same logical event. The pair

\[
(\text{SessionId},\text{Ordinal})
\]

is a stronger coordinate, but it still identifies delivery position rather than semantic event identity unless the architecture guarantees otherwise.

A stable `EventId` would define a different arrow into an identity space. Asking whether that arrow is monic forces a precise question: can two distinct logical events share the same ID?

## Exercises

**3.1 [proof].** Show that every identity arrow is monic, epic, and iso.

**3.2 [proof].** Show that the composite of two monic arrows is monic. State and prove the dual result.

**3.3 [calculation].** Let `encode` map semantic snapshots to canonical JSON bytes, while `decode` accepts canonical and noncanonical whitespace variants. Determine which round-trip equations hold. Identify the objects between which an isomorphism exists.

**3.4 [design].** Propose an event identity type for SessionStream. Separate semantic identity, delivery identity, and order coordinate. State which maps should be monic.

**3.5 [recognition].** Identify initial and terminal objects in each category:

1. sets and total functions;
2. event cuts ordered by \(\leq\);
3. predicates ordered by implication;
4. one-object category of event histories.

**3.6 [proof].** Initial objects are unique up to a unique isomorphism. Write the standard proof using the two unique arrows.

**3.7 [research].** Find an engineering claim phrased as "these representations are equivalent." Rewrite it as an explicit isomorphism, equivalence weaker than isomorphism, or one-way refinement. Justify the choice.

# Universal Constructions in SessionStream

**Source alignment:** Goldblatt §§3.8-3.16. This chapter is the custom counterpart to the point you have currently reached, especially §3.11 on limits and colimits.

## The universal-property pattern

A universal construction is not characterized primarily by what it contains. It is characterized by how every competing construction maps to or from it.

A typical limiting universal property has this form:

1. specify a pattern of arrows, called a diagram;
2. define cones over that diagram;
3. select a cone through which every other cone factors;
4. require the factorization arrow to be unique.

The unique factorization is the source of canonicity. If two objects satisfy the same universal property, they are uniquely isomorphic in the relevant sense.

This is the right mental model for the phrase "canonical solution." It does not mean a favorite implementation. It means an object determined up to unique isomorphism by its relation to every admissible candidate.

## Products

> **Definition.** A product of \(A\) and \(B\) is an object \(A\times B\) with projections
>
> \[
> \pi_A:A\times B\to A,
> \qquad
> \pi_B:A\times B\to B,
> \]
>
> such that for every pair \(f:X\to A\), \(g:X\to B\), there is exactly one arrow
>
> \[
> \langle f,g\rangle:X\to A\times B
> \]
>
> with \(\pi_A\circ\langle f,g\rangle=f\) and \(\pi_B\circ\langle f,g\rangle=g\).

![The universal property of a product.](figures/03-product.png){width=72%}

In `Set`, this is the ordinary Cartesian product. The universal property says that giving one function into a pair is exactly the same as giving its two component functions:

\[
\operatorname{Set}(X,A\times B)
\cong
\operatorname{Set}(X,A)\times\operatorname{Set}(X,B).
\]

### Product projections in SessionStream

Suppose one canonical event is interpreted by independent UI and timeline projections:

\[
p_U:S\times E\to U^*,
\]

\[
p_T:S\times E\to T.
\]

Their product interpretation is

\[
\langle p_U,p_T\rangle:S\times E\to U^*\times T.
\]

The product does not imply that the two projections are operationally independent. If either performs hidden effects or reads mutable shared state, the mathematical product model is inaccurate. But under pure semantics, it says one input can be observed through both interpreters without identifying their output types.

### Session decomposition

The intended global state often has a product shape

\[
S=\prod_{s\in\mathrm{Sessions}}S_s.
\]

An event for session \(a\) should change the \(a\)-component and leave every \(b\ne a\) component unchanged. This is a noninterference law. For an infinite family, this is a possibly infinite product, not merely a binary product.

## Coproducts

The dual construction is the coproduct.

> **Definition.** A coproduct of \(A\) and \(B\) is an object \(A+B\) with injections
>
> \[
> \iota_A:A\to A+B,
> \qquad
> \iota_B:B\to A+B,
> \]
>
> such that for every \(f:A\to X\), \(g:B\to X\), there is exactly one arrow
>
> \[
> [f,g]:A+B\to X
> \]
>
> whose composites with the injections are \(f\) and \(g\).

In typed programming, tagged unions are coproduct-like. SessionStream's logical payload families have this shape:

\[
\mathrm{EventPayload}
=
E_1+E_2+\cdots+E_k.
\]

A consumer of the coproduct is defined by handling every variant. Protobuf `oneof` is a concrete encoding of a finite sum. The current `Event` structure uses a string name plus a dynamic `proto.Message`; the schema registry provides runtime evidence for the intended tagged-sum discipline.

An untagged `google.protobuf.Struct` weakens this structure because the alternatives and their eliminators are no longer explicit.

## Equalizers

> **Definition.** Given parallel arrows \(f,g:A\to B\), an equalizer is an arrow
>
> \[
> e:E\to A
> \]
>
> such that \(f\circ e=g\circ e\), and for every \(h:X\to A\) satisfying \(f\circ h=g\circ h\), there is exactly one \(u:X\to E\) with \(e\circ u=h\).

In `Set`,

\[
E=\{a\in A:f(a)=g(a)\}.
\]

![An equalizer can select histories on which live and replay semantics agree.](figures/04-equalizer.png){width=72%}

### Replay agreement as an equalizer

Let \(H\) be a set of histories and let

\[
L,R:H\to V
\]

be live materialization and rebuild materialization into an observable view space \(V\). The equalizer

\[
\operatorname{Eq}(L,R)\hookrightarrow H
\]

is the subspace of histories for which replay agrees with live behavior.

This is more precise than the sentence "replay should be deterministic." It separates:

- the domain of histories under consideration;
- the observation used for equality;
- the two competing interpretations;
- the maximal subobject on which they agree.

A failing test supplies a history outside the equalizer.

## Coequalizers

The dual of an equalizer identifies outputs that should be treated as equivalent.

In `Set`, the coequalizer of \(f,g:A\to B\) is the quotient of \(B\) by the smallest equivalence relation forcing

\[
f(a)\sim g(a)
\]

for every \(a\in A\).

Software quotienting appears when several representations are normalized to one semantic value. For example, if different accepted JSON encodings are declared equivalent, the semantic decode space can be seen as a quotient. A coequalizer describes the universal quotient that performs the required identifications and no more.

Quotients are dangerous when operational evidence matters. If two traces end in the same state but differ in drops, timeouts, or authorization decisions, coequalizing them may erase the property you intended to verify.

## Diagrams and cones

A diagram \(D\) in \(\mathcal C\) is a collection of objects and arrows with a specified shape. Formally, a diagram is a functor

\[
D:J\to\mathcal C
\]

from an indexing category \(J\), although Goldblatt first introduces it less formally.

A cone from an object \(X\) to \(D\) assigns an arrow

\[
\lambda_j:X\to D(j)
\]

for every object \(j\) of the diagram, compatible with every arrow of the diagram. If \(u:i\to j\) is in \(J\), then

\[
D(u)\circ\lambda_i=\lambda_j.
\]

The cone is one candidate global observation whose projections agree with the diagram's internal relationships.

## Limits

> **Definition.** A limit of \(D:J\to\mathcal C\) is a cone \((L,\lambda_j)\) such that for every cone \((X,x_j)\), there is exactly one arrow \(u:X\to L\) satisfying
>
> \[
> \lambda_j\circ u=x_j
> \]
>
> for every \(j\).

![A limit as the universal compatible execution.](figures/06-limit-cone.png){width=75%}

A limit is the universal compatible assembly of the diagram's pieces.

This single definition includes:

- terminal objects: limits of empty diagrams;
- products: limits of discrete two-object diagrams;
- equalizers: limits of parallel-arrow diagrams;
- pullbacks: limits of cospans.

This is why §3.11 is a conceptual hinge. Products and equalizers are not isolated tricks. They are instances of one construction.

### Limits as compatible databases of facts

Suppose a diagram contains:

- event facts \(E\);
- timeline facts \(T\);
- snapshot facts \(S\);
- live UI facts \(U\);

with arrows expressing the projection and cut contracts. A point of the limit is a tuple

\[
(e,t,s,u)
\]

whose components satisfy every compatibility equation.

In `Set`, limits can often be constructed as subsets of products:

\[
L\subseteq E\times T\times S\times U
\]

containing exactly the compatible tuples.

This is the categorical version of a constrained join. The universal property says any other system supplying compatible component facts factors uniquely through this one.

## Colimits

A cocone reverses the cone arrows, and a colimit is universal among cocones. Colimits assemble by identification rather than by compatibility constraints.

Examples include:

- initial objects: colimits of empty diagrams;
- coproducts: colimits of discrete diagrams;
- coequalizers: colimits of parallel arrows;
- pushouts: colimits of spans.

A rough engineering mnemonic is:

- limits select tuples that agree;
- colimits merge pieces while imposing identifications.

The mnemonic is reliable in `Set`, but the universal property is the definition.

## Pullbacks

> **Definition.** Given arrows \(f:A\to C\) and \(g:B\to C\), a pullback is an object \(P\) with arrows \(p_A:P\to A\) and \(p_B:P\to B\) such that
>
> \[
> f\circ p_A=g\circ p_B,
> \]
>
> and universal among all such commuting pairs.

In `Set`,

\[
P=A\times_C B
=
\{(a,b):f(a)=g(b)\}.
\]

### Schema validation as a pullback

Let:

- \(N\) be logical event names;
- \(P\) be protobuf payload values;
- \(D\) be protobuf descriptors;
- \(r:N\to D\) be registry lookup;
- \(t:P\to D\) be runtime reflection.

Then validated named payloads form the pullback

\[
V=N\times_D P
=
\{(n,p):r(n)=t(p)\}.
\]

![Schema validation as a pullback.](figures/05-schema-pullback.png){width=72%}

The concrete `SchemaRegistry` and `Hub.validatePayloadType` implement this matching idea: the name selects a prototype descriptor, the payload supplies its actual descriptor, and validation requires equality.

The pullback is stronger than saying "check the two descriptors." It is the canonical object of all matching pairs. Any other typed event representation carrying a name and payload that agree over descriptors factors uniquely through it.

### Reindexing by pullback

Suppose \(f:A\to B\) maps detailed scopes to coarser scopes. A bundle of data over \(B\) can be pulled back along \(f\) to a bundle over \(A\). In database language this resembles reindexing or joining data with the scope map. In topos theory, pullback becomes the central reindexing operation, and its adjoints become quantifiers.

## Pushouts

A pushout is the dual of a pullback. Given \(C\to A\) and \(C\to B\), it merges \(A\) and \(B\) while identifying the two images of \(C\).

A protocol migration can sometimes be modeled this way. An old schema and a new schema may share a stable common core. Their pushout is a universal merged representation in which the two copies of the core are identified.

This is an abstract construction, not an automatic recommendation. Real migrations must preserve semantics, compatibility, and operational constraints that may not be represented by the chosen category.

## Finite completeness

A category is finitely complete when every finite diagram has a limit. It is enough to have a terminal object and pullbacks. From those, finite products and equalizers can be constructed.

For software reasoning, finite completeness means the modeling universe can express finite systems of compatible observations. You can:

- add contextual variables through products;
- impose equations through equalizers;
- reindex dependent data through pullbacks;
- combine these operations coherently.

An elementary topos will be finitely complete. This supplies the structural substrate for predicates and substitution.

## Exponentials

> **Definition.** An exponential \(B^A\) is an object with an evaluation arrow
>
> \[
> \operatorname{ev}:B^A\times A\to B
> \]
>
> such that for every \(f:X\times A\to B\), there is exactly one arrow
>
> \[
> \widehat f:X\to B^A
> \]
>
> satisfying
>
> \[
> \operatorname{ev}\circ(\widehat f\times 1_A)=f.
> \]

In `Set`, \(B^A\) is the set of all functions from \(A\) to \(B\). The universal property is currying:

\[
\operatorname{Set}(X\times A,B)
\cong
\operatorname{Set}(X,B^A).
\]

A category with finite products and exponentials is Cartesian closed.

### Handler and projection spaces

Mathematically, the set of pure event interpreters \(S\times E\to S\) can be represented as an exponential

\[
S^{S\times E}.
\]

A configuration-dependent projection

\[
C\times(S\times E)\to S
\]

can be curried to

\[
C\to S^{S\times E}.
\]

This says a configuration selects a projector. It gives a clean model for dependency injection when dependencies are explicit values.

Actual Go functions are not automatically elements of a set with usable equality, but the mathematical semantics can still be Cartesian closed.

## A complete worked limit: coherent hydration

Fix a session \(s\) and a target cut \(m\). Consider these local facts:

1. a snapshot \(S_n\) at cut \(n\le m\);
2. a suffix \(q=e_{n+1}\cdots e_m\);
3. a reconstructed client state \(C_m\);
4. a timeline fold result \(T_m\).

Compatibility equations are:

\[
\operatorname{fold}(S_n,q)=C_m,
\]

\[
\operatorname{materialize}(e_1\cdots e_m)=T_m,
\]

\[
\operatorname{clientView}(T_m)=C_m,
\]

and the suffix ordinals are strictly greater than \(n\) and ordered.

The set of coherent hydration witnesses is the limit of this constraint diagram. A witness is not just a client state. It is the entire tuple with all compatibility evidence.

This distinction is useful in testing. A test that checks only final client state projects the limit witness onto one component. A stronger test records the cut, suffix, timeline state, and delivery trace, then verifies all equations.

## When limits fail to exist in the model

A category may lack a desired limit, or a specific family of observations may have no compatible tuple.

These are different failures.

- **Missing construction:** the category does not support the required universal object.
- **Empty instance:** the limit object exists, but this particular constraint fiber has no element.
- **Non-unique assembly:** compatible local data have several global completions; the presheaf will later fail the uniqueness part of sheaf gluing.
- **Model mismatch:** the implementation uses hidden coordinates not present in the diagram.

For example, cursor and entity observations can each be locally valid while no consistent-cut snapshot contains both. That is an empty compatibility fiber for the claimed cut.

## Exercises

**4.1 [proof].** Prove that products are unique up to unique isomorphism.

**4.2 [calculation].** In the prefix poset of histories, compute the product and coproduct of two histories when they exist. Interpret the result as greatest common prefix and least common extension.

**4.3 [proof].** Show that an equalizer arrow is monic.

**4.4 [design].** Define two arrows from event histories to an observable client model: one for the live path and one for rebuild. State a practical method for sampling their equalizer.

**4.5 [calculation].** For registry map \(r:N\to D\) and payload-type map \(t:P\to D\), list the elements of the pullback for a toy registry with two names and three payloads.

**4.6 [proof].** Show that a pullback in `Set` satisfies the universal property, not only the matching-pair equation.

**4.7 [design].** Model authorization as a pullback or explain why a pullback is insufficient. Distinguish type admission from authority.

**4.8 [proof].** Show that a terminal object is the limit of the empty diagram and a product is the limit of a discrete two-object diagram.

**4.9 [calculation].** Construct the limit in `Set` of a diagram \(A\xrightarrow{f}C\xleftarrow{g}B\). Then add a fourth set \(D\) with maps into \(A\) and \(B\) that commute over \(C\). Write the unique mediating function.

**4.10 [lab].** Build a small property test for snapshot-plus-suffix reconstruction. Generate an event history, choose a cut, materialize the prefix, replay the suffix, and compare with the full fold. Record enough data to diagnose which compatibility equation failed.

**4.11 [research].** Draw a finite diagram for atomic projection progress containing event append, timeline apply, projection cursor, and fanout. Which subdiagram should be committed atomically? Which effect should remain outside the durable transaction?

**4.12 [proof].** Derive the currying bijection in `Set` and verify both inverse equations.

**4.13 [design].** Give one useful pushout-shaped schema migration and one case where a pushout would collapse distinctions that must remain separate.

**4.14 [checkpoint].** Without notes, define cone, limit, pullback, and exponential. For each, state the universal quantification over competing candidates and the uniqueness clause.

# Subobjects, Classifiers, and the Topos Idea

**Source alignment:** Goldblatt, Chapter 4: subobjects, classifying arrows, the definition of an elementary topos, first examples, bundles and sheaves, monoid actions, power objects, and comprehension.

## Subobjects are embeddings up to representation

A subset \(A\subseteq B\) can be represented by its inclusion function

\[
i:A\hookrightarrow B.
\]

The categorical generalization is a monic arrow into \(B\).

Two monics

\[
m:A\hookrightarrow B,
\qquad
n:C\hookrightarrow B
\]

represent the same subobject when there is an isomorphism \(u:A\cong C\) with

\[
n\circ u=m.
\]

The domain's labels do not matter; the way it sits inside \(B\) does.

> **Definition.** A subobject of \(B\) is an equivalence class of monic arrows with codomain \(B\), under isomorphism over \(B\).

In `Set`, subobjects correspond exactly to subsets. In a general category they encode predicates, embedded structures, or admissible states without referring to literal membership.

### Software invariants as subobjects

Let \(X\) be the set of all representable SessionStream runtime records of some type. An invariant \(P\) selects valid records

\[
X_P=\{x\in X:P(x)\}.
\]

The inclusion

\[
X_P\hookrightarrow X
\]

is the subobject corresponding to the invariant.

Examples include:

\[
\text{SessionId}\ne "",
\]

\[
\operatorname{LastEventOrdinal}(x)
\le
\operatorname{SnapshotOrdinal},
\]

\[
\operatorname{payloadDescriptor}(p)
=
\operatorname{registeredDescriptor}(n).
\]

The subobject is not merely a Boolean check. It is the type of states carrying evidence that the check holds.

## Generalized elements

In `Set`, an element \(x\in X\) corresponds to a function

\[
\bar x:1\to X
\]

from a singleton. In a general category, arrows \(1\to X\) are called global elements.

But global elements may be too few to reveal an object. Category theory therefore uses generalized elements:

\[
x:U\to X.
\]

Here \(U\) is a context. You can read \(x\) as an \(X\)-valued quantity depending on variables in \(U\).

This is a major bridge to software. A value is rarely observed without context. An event depends on a session and cut; a snapshot depends on a database state; a UI event depends on a subscription. The arrow \(U\to X\) makes the context explicit rather than pretending every value is globally available.

## Characteristic functions in `Set`

For a subset \(A\subseteq X\), define the characteristic function

\[
\chi_A:X\to\{0,1\}
\]

by \(\chi_A(x)=1\) exactly when \(x\in A\).

Let

\[
\mathsf{true}:1\to\{0,1\}
\]

select \(1\). Then the inclusion \(A\hookrightarrow X\) is the pullback of `true` along \(\chi_A\).

This pullback square says that \(A\) consists exactly of those elements of \(X\) classified as true.

## Subobject classifiers

> **Definition.** A subobject classifier in a category \(\mathcal C\) is an object \(\Omega\) together with an arrow
>
> \[
> \mathsf{true}:1\to\Omega
> \]
>
> such that every monic \(m:A\hookrightarrow X\) is, up to the standard equivalence, the pullback of `true` along a unique characteristic arrow
>
> \[
> \chi_m:X\to\Omega.
> \]

The object \(\Omega\) internalizes truth values. A predicate on \(X\) is represented by an arrow \(X\to\Omega\).

In `Set`, \(\Omega=\{0,1\}\). In a presheaf or sheaf topos, \(\Omega\) is richer: a proposition can have stage-dependent or local truth rather than one global Boolean value.

### A classifier for typed admission

At a simple set level, let \(X\) be all pairs `(name, payload)`. Let \(A\subseteq X\) be pairs whose payload descriptor matches the registry. The characteristic map

\[
\chi_A:X\to\{0,1\}
\]

is the validation predicate.

The pullback of `true` is the set of admitted pairs. In code, returning a refined type such as `ValidatedEvent` rather than a bare Boolean corresponds more closely to using the pullback object.

## The definition of an elementary topos

Goldblatt first states the original Lawvere-Tierney definition and then notes the redundancy of finite cocompleteness.

> **Definition.** An elementary topos is a Cartesian closed category with a subobject classifier.

Equivalently, in the expanded form used pedagogically:

- it has finite limits;
- it has exponentials;
- it has a subobject classifier.

Finite colimits follow from these conditions, although proving that is nontrivial.

A topos has enough Set-like structure to support:

- finite contexts and equations;
- function objects;
- predicates as arrows into \(\Omega\);
- an internal intuitionistic logic;
- power objects and comprehension.

A topos is not simply "a category with topology." The word has historical roots in Grothendieck's sheaf theory, but elementary topoi include `Set`, finite sets, presheaf categories, and many other universes.

## Power objects

In `Set`, the power set \(\mathcal P(A)\) classifies subsets of \(A\). Categorically, a power object \(PA\) classifies subobjects of \(A\times X\) naturally in \(X\).

In a Cartesian closed category with subobject classifier,

\[
PA=\Omega^A.
\]

An element of \(\Omega^A\) is a predicate on \(A\). The evaluation map

\[
\Omega^A\times A\to\Omega
\]

is membership.

For software, \(\Omega^A\) is the space of predicates or policies on \(A\), at the mathematical level. A concrete policy engine usually represents only a computable or syntactically describable subset of all predicates.

## Topos thinking for API contracts

A useful sequence is:

1. choose an object \(X\) of candidate requests or states;
2. represent each invariant as a subobject \(A\hookrightarrow X\);
3. obtain its characteristic arrow \(\chi_A:X\to\Omega\);
4. combine predicates using the internal algebra of \(\Omega\);
5. pull predicates back along API or projection maps;
6. quantify along context maps using adjoints, when available.

This reframes "validation" as structural predicate manipulation. It also reveals why parameter sufficiency is a pullback/reindexing question: a predicate on full states can be pulled back to supplied parameters only if it is constant across the omitted fibers, or if the API supplies enough evidence to decide it.

## First encounter with sheaves

Goldblatt introduces sheaves of germs in Chapter 4 before returning to presheaves and sheaves of sections in Chapter 14. This companion follows the same spiral.

At this stage, retain only the picture:

- a base space supplies locations or contexts;
- over each location there is a stalk of possible local values;
- a section chooses values continuously or compatibly across a region;
- the category of sheaves behaves like a universe of variable sets.

For SessionStream, an eventual analogue will take contexts to be observation regions rather than physical opens. Sections will be compatible assignments of events, cuts, projections, and client states.

## Exercises

**5.1 [proof].** Verify that equivalence of monics over \(X\) is an equivalence relation.

**5.2 [design].** Define the subobject of `Snapshot` values satisfying consistent-cut safety. What evidence would a refined `ConsistentSnapshot` type carry?

**5.3 [calculation].** For \(X=\{0,1,2,3\}\) and \(A=\{1,3\}\), write the characteristic map and the pullback square classifying \(A\).

**5.4 [proof].** Show that predicates \(X\to\{0,1\}\) correspond bijectively to subsets of \(X\).

**5.5 [design].** Give a reason to return a validated value rather than only `bool` or `error`. Relate the answer to the pullback of `true`.

**5.6 [research].** List the parts of a real SessionStream implementation that prevent it from literally being an elementary topos. Then identify a mathematical semantics that plausibly is one.

# Images, Reachability, and Extensionality

**Source alignment:** Goldblatt, Chapter 5: monics as equalizers, images, fundamental structural facts, extensionality, bivalence, and characterizations by elements.

## Monics as equalizers

In a topos, every monic arrow can be exhibited as an equalizer. Intuitively, every subobject is the locus where two characteristic behaviors agree.

For a monic \(m:A\hookrightarrow X\) with characteristic arrow \(\chi_m:X\to\Omega\), the inclusion is the equalizer of \(\chi_m\) and the constant-true predicate:

\[
A\hookrightarrow X
\rightrightarrows
\Omega.
\]

This connects predicates and equations. To satisfy a predicate is to equalize its truth value with `true`.

In software terms, a refined type can be described either by an admission predicate or by an equalizer of two observations.

## Images

For a function \(f:A\to B\), its image is the subset of outputs actually reached. Categorically, an image factorization has the form

\[
A\twoheadrightarrow \operatorname{Im}(f)
\hookrightarrow B.
\]

The first arrow is epic and the second monic. In a topos, such factorizations behave well.

### Reachable materialized states

Let

\[
\operatorname{fold}:E_s^*\to S_s
\]

map histories to timeline states. The image

\[
\operatorname{Reach}_s\hookrightarrow S_s
\]

is the subobject of reachable states.

A state can satisfy all local field validations and still lie outside this image. Reachability is a global historical invariant, not a record-level schema invariant.

This distinction matters in repair tooling. Directly editing rows may create an entity configuration that cannot arise from any valid event history.

## Image as the smallest containing subobject

The image of \(f:A\to B\) is the smallest subobject of \(B\) through which \(f\) factors. This universal property is more useful than "the set of outputs" because it generalizes beyond `Set`.

For an event handler's published-event map, the image tells you which canonical events are reachable from admitted commands under the modeled handler semantics. If a schema registers events outside this image, they may still be produced by other handlers or recovery processes; the image is always relative to the chosen arrow.

## Extensionality

Extensionality says that arrows are determined by their behavior on arguments. In `Set`, if

\[
f\circ x=g\circ x
\]

for every element \(x:1\to A\), then \(f=g\).

In an arbitrary category, global elements may not be enough to distinguish arrows. Generalized elements often are: the Yoneda perspective says an arrow is determined by all its composites from all contexts.

For software, this warns against testing only global or default contexts. Two projections can agree on every current fixture and differ on a context not represented in the test suite.

A robust extensional test scheme quantifies over:

- session metadata;
- prior timeline views;
- schema versions;
- event prefixes;
- cancellation states;
- transport timing states.

## Bivalence and its limits

In `Set`, global truth values are the two elements of \(\{0,1\}\). Every global proposition is either true or false.

In a general topos, \(\Omega\) can have more global or local structure, and excluded middle may fail internally. This does not mean the external metatheory has abandoned ordinary truth. It means the internal language of the modeled universe tracks evidence or locality differently.

For a partially observed run, the proposition "this run finishes successfully" may not yet have a proof, nor may its negation have a proof. The runtime's eventual outcome is classically determined in a fixed complete execution, but the stage-indexed information model is intuitionistic.

## Observable equivalence

Let two implementations \(p,q:I\to O\) be compared through an observation map \(o:O\to V\). They are observationally equal when

\[
o\circ p=o\circ q.
\]

This is weaker than \(p=q\). It may intentionally forget logs, allocation, timing, or internal entity order.

The equalizer of \(o\circ p\) and \(o\circ q\) identifies inputs on which the implementations are observationally equivalent. Changing \(o\) changes the theorem.

The Architecture Garden's law

\[
\operatorname{observe}(\operatorname{concurrentApply}(H_s))
=
\operatorname{observe}(\operatorname{fold}(H_s))
\]

is explicitly an observational equation. The choice of `observe` is part of the contract.

## Exercises

**6.1 [proof].** Show in `Set` that the inclusion of a subset \(A\subseteq X\) equalizes its characteristic function and the constant-true function, and satisfies the universal property.

**6.2 [design].** Define three different observation maps for comparing live and replayed SessionStream state: storage-level, client-level, and audit-level. Give a pair of implementations equal under one and unequal under another.

**6.3 [calculation].** For a toy event fold, enumerate its reachable states and construct the image inclusion.

**6.4 [research].** Identify a direct database edit that preserves row schemas but leaves the image of valid event-history materialization.

**6.5 [proof].** Explain why testing arrows only on global elements can fail in a category with too few global elements. Use generalized elements to state a stronger criterion.

# Logic as Algebra of Invariants

**Source alignment:** Goldblatt, Chapters 6-7: classical propositional logic, Boolean algebra, truth functions as arrows, and the lattice of subobjects.

## Propositions as subobjects

A proposition in a topos can be represented as a subobject of the terminal object:

\[
P\hookrightarrow 1.
\]

In `Set`, there are only two such subobjects up to equivalence: the empty subset and the singleton itself. Hence global propositions have two truth values.

A predicate with a free variable of type \(X\) is a subobject

\[
P\hookrightarrow X
\]

or equivalently a characteristic arrow

\[
\chi_P:X\to\Omega.
\]

This is the categorical form of a typed invariant.

## Conjunction and intersection

Given subobjects \(P,Q\hookrightarrow X\), their conjunction is their intersection, constructed as a pullback:

\[
P\wedge Q=P\times_X Q.
\]

A state satisfies the conjunction exactly when it factors through both subobjects.

For a snapshot, consider:

\[
P(x): \text{all entity ordinals are at most the snapshot cut},
\]

\[
Q(x): \text{entity keys are unique}.
\]

The valid-snapshot object for both conditions is the pullback intersection.

## Disjunction and union

In `Set`, disjunction corresponds to union. In a topos, unions of subobjects can be constructed using images of coproduct maps:

\[
P+Q\to X.
\]

The coproduct remembers which proof branch supplied membership; taking the image forgets the tag and retains the union subobject.

This proof-sensitive distinction is familiar in typed programming. A value of `Either[P,Q]` carries evidence of which branch holds. A Boolean `P || Q` may erase that evidence.

## Negation

Classically, \(\neg P\) is the complement of \(P\). In intuitionistic logic, negation means

\[
P\Rightarrow\bot.
\]

It says that a proof of \(P\) would lead to contradiction. It does not automatically produce a decidable complement.

For runtime information, "not observed to have finished" is not the same as "observed to be unfinished forever." Confusing these is a common temporal-logic bug.

## Implication

In a Heyting algebra of subobjects, implication \(P\Rightarrow Q\) is the largest predicate \(R\) such that

\[
R\wedge P\le Q.
\]

This is an adjoint property:

\[
R\wedge P\le Q
\quad\Longleftrightarrow\quad
R\le(P\Rightarrow Q).
\]

The meaning is operationally useful. \(P\Rightarrow Q\) is the weakest additional condition under which \(P\) guarantees \(Q\).

For example:

- \(P\): a subscription has been registered;
- \(Q\): every post-registration batch is represented or delivered;
- \(R\): buffering remains below capacity and snapshot transition completes.

Then \(R\) can be studied as a sufficient condition for the desired implication.

## The subobject lattice

For each object \(X\), its subobjects form an ordered structure

\[
\operatorname{Sub}(X),
\]

where \(P\le Q\) means \(P\) factors through \(Q\), corresponding to logical implication.

In a topos, \(\operatorname{Sub}(X)\) is a Heyting algebra. It supports finite meets, joins, implication, top, and bottom. It need not be Boolean.

This makes invariant composition algebraic. One can ask:

- Which invariant is stronger?
- What is their conjunction?
- What is the least invariant implied by either?
- What additional assumption makes one imply another?

## Pulling invariants backward

Given \(f:X\to Y\) and a predicate \(Q\hookrightarrow Y\), its pullback

\[
f^{-1}(Q)\hookrightarrow X
\]

is the predicate "\(f(x)\) satisfies \(Q\)."

This is substitution. If \(f\) is an API-to-domain map, pulling a domain invariant backward gives the request-level condition that guarantees it.

For parameter sufficiency, let \(r:X\to P\) forget the omitted domain coordinates and retain supplied parameters. A full-state invariant \(I\hookrightarrow X\) descends to a predicate on \(P\) only when it is constant in the relevant way over fibers of \(r\). Otherwise no request-only Boolean can decide the invariant without additional lookup or evidence.

## Classical logic as a special case

A topos is Boolean when every subobject has a complement, or equivalently when its internal logic validates excluded middle. `Set` is Boolean. General sheaf and presheaf topoi are often not.

Classical logic remains available externally while we reason about a non-Boolean internal universe. This two-level discipline matters:

- externally, we can prove a theorem about all stages;
- internally, a stage may lack evidence for \(P\vee\neg P\).

## Exercises

**7.1 [calculation].** Construct the intersection of two subsets as a pullback and verify the universal property.

**7.2 [design].** Express the SessionStream snapshot safety contract as a conjunction of at least four subobjects.

**7.3 [proof].** In a Boolean algebra, show that \(P\Rightarrow Q=\neg P\vee Q\). Explain why this identity is not the definition in a Heyting algebra.

**7.4 [design].** Given a request parameter map \(r:X\to P\), formulate a test for whether an invariant \(I:X\to\{0,1\}\) is determined by parameters alone.

**7.5 [research].** Compare a proof-carrying coproduct `Either[P,Q]` with a Boolean disjunction. Which information is lost by taking the image/union?

# Intuitionistic Logic as Growing Information

**Source alignment:** Goldblatt, Chapter 8: constructivist motivation, Heyting calculus and algebras, Kripke semantics, and Beth-style local semantics.

## Truth at a stage

Let \(P\) be the prefix poset of a session's histories. Interpret

\[
h\Vdash\varphi
\]

as "the information available at history \(h\) supports \(\varphi\)."

Information grows along prefix extension. Therefore forcing should be monotone:

\[
h\preceq k\text{ and }h\Vdash\varphi
\quad\Longrightarrow\quad
k\Vdash\varphi.
\]

Once a durable fact is established, later history should not invalidate the fact. This applies only to propositions modeled as persistent. "The current text is empty" is not persistent; "an inference-start event occurred" is.

## Kripke semantics

For a preorder of stages, intuitionistic connectives can be interpreted as follows.

\[
h\Vdash\varphi\wedge\psi
\]

when both are forced at \(h\).

\[
h\Vdash\varphi\vee\psi
\]

when one branch is forced at \(h\) with evidence of which.

\[
h\Vdash\varphi\Rightarrow\psi
\]

when for every extension \(k\succeq h\), if \(k\Vdash\varphi\), then \(k\Vdash\psi\).

\[
h\Vdash\neg\varphi
\]

when no extension \(k\succeq h\) forces \(\varphi\).

The implication clause explains why implication is future-looking. To know \(\varphi\Rightarrow\psi\) now, the guarantee must survive every refinement of information.

## Why excluded middle can fail

Let \(F\) mean "the current inference eventually finishes normally." At a prefix before a terminal event, neither \(F\) nor \(\neg F\) may be forced.

- There is not yet evidence of normal finish.
- There may be an extension with normal finish, so negation is not supported.

Thus

\[
F\vee\neg F
\]

need not be forced at that stage.

Externally, each complete execution may have a definite outcome. The internal stage semantics is about available evidence, not metaphysical indeterminacy.

## Heyting algebras of information

Open sets of a topological space form a Heyting algebra. So do upward-closed sets of stages in a Kripke frame.

A proposition corresponds to the set of stages where it is forced. Persistence makes this set upward closed.

Conjunction is intersection. Disjunction is union. Implication is

\[
U\Rightarrow V
=
\{p:\forall q\succeq p,\;q\in U\Rightarrow q\in V\}.
\]

Negation is \(U\Rightarrow\varnothing\).

This gives a geometric picture: a proposition is a region of information space. Implication collects the points from which every future entrance into \(U\) also lies in \(V\).

## Safety and liveness

Intuitionistic stage semantics naturally distinguishes safety evidence from eventuality.

A safety property such as

\[
\text{no delivered live ordinal is at most the snapshot cut}
\]

can often be refuted by a finite bad prefix. Its negation may become forced once the bad delivery occurs.

A liveness property such as

\[
\text{every accepted observation is eventually delivered or explicitly dropped}
\]

cannot generally be established from a finite prefix without additional fairness or termination evidence.

This is not itself temporal logic, but the evidence-sensitive reading prevents classical shortcuts that confuse "not yet" with "never."

## Local proof objects

Constructive logic treats a proof of disjunction as a choice of branch and a proof of existential quantification as a witness. Software frequently needs exactly that information.

Instead of returning

```go
bool
```

for "the batch is covered," return a sum type:

```text
CoveredBySnapshot(snapshotOrdinal)
| DeliveredInSuffix(eventOrdinal, deliveryId)
| ExplicitOverflow(reason)
```

This is a constructive proof object for the snapshot-plus-suffix completeness law. It is more useful for debugging and recovery than a Boolean summary.

## Refinement of knowledge versus mutation of truth

A subtle but essential distinction:

- **knowledge refinement:** later contexts reveal more about one fixed execution;
- **world mutation:** later events change the system state.

Kripke semantics models monotone information, not arbitrary mutable predicates. To use event prefixes as stages, propositions must be chosen so that evidence persists along extension, or their time index must be included explicitly.

For example, "entity `x` has payload `p` at the current cut" is not persistent. The proposition

\[
\text{entity `x` had payload `p` at cut }n
\]

is persistent once cut \(n\) is included in history.

Adding coordinates turns mutable claims into stable historical claims.

## Exercises

**8.1 [calculation].** Build a four-stage prefix poset for a run that starts, emits a delta, and either finishes or stops. Compute the upward-closed set for "start occurred" and for "normal finish occurred."

**8.2 [proof].** Verify the monotonicity of the Kripke implication clause.

**8.3 [calculation].** Give a stage at which neither \(F\) nor \(\neg F\) is forced. Explain why this refutes stagewise excluded middle.

**8.4 [design].** Rewrite a Boolean SessionStream status check as a constructive sum of evidence variants.

**8.5 [research].** Choose five runtime propositions and classify them as persistent, nonpersistent, or persistent after adding an explicit cut/time coordinate.

**8.6 [proof].** In the Heyting algebra of upward-closed subsets, derive the formula for implication and prove its adjunction with intersection.

# Functors, Natural Transformations, and Multiple Interpreters

**Source alignment:** Goldblatt, Chapter 9: functors, contravariant functors, natural transformations, equivalence, and functor categories.

## Functors preserve categorical structure

> **Definition.** A functor \(F:\mathcal C\to\mathcal D\) assigns an object \(F(A)\) to each object \(A\), and an arrow \(F(f):F(A)\to F(B)\) to each arrow \(f:A\to B\), such that
>
> \[
> F(1_A)=1_{F(A)}
> \]
>
> and
>
> \[
> F(g\circ f)=F(g)\circ F(f).
> \]

A functor is an interpretation that respects doing nothing and doing things in sequence.

This is the formal core of "one architecture, several views." If canonical histories form a category and each view interprets histories compositionally, then each view is functorial.

## Histories acting on states

Treat \(E_s^*\) as a one-object category. Let `End(S)` be the one-object category whose arrows are state endomorphisms \(S\to S\), with composition.

A deterministic event semantics assigns to each event \(e\) a state transformer

\[
\delta_e:S\to S.
\]

Extending by

\[
F(e_1\cdots e_n)
=
\delta_{e_n}\circ\cdots\circ\delta_{e_1}
\]

and \(F(\epsilon)=1_S\) gives a functor

\[
F:E_s^*\to\operatorname{End}(S).
\]

Functoriality is exactly the fold law. Concatenated histories are interpreted as composed state transformations.

The same event signature can have several functors:

\[
F_T:E_s^*\to\operatorname{End}(T)
\]

for timeline state,

\[
F_A:E_s^*\to\operatorname{End}(A)
\]

for audit state, and a writer-style interpretation for emitted UI words. This is the mathematically disciplined form of multiple interpreters.

## Covariant and contravariant behavior

A contravariant functor \(F:\mathcal C^{op}\to\mathcal D\) reverses arrows. If \(U\subseteq V\), a presheaf supplies a restriction map

\[
F(V)\to F(U).
\]

More context has a map to less context because restriction forgets information.

Software contains both directions:

- execution extends forward from a shorter history to a longer one;
- observations restrict backward from a larger cut or context to a smaller one.

Confusing these directions is a common source of diagram errors. The base category arrow says which context is included in which; the presheaf arrow goes the opposite way.

## Natural transformations

> **Definition.** Given functors \(F,G:\mathcal C\to\mathcal D\), a natural transformation \(\eta:F\Rightarrow G\) assigns to each object \(A\) an arrow
>
> \[
> \eta_A:F(A)\to G(A)
> \]
>
> such that for every \(f:A\to B\),
>
> \[
> G(f)\circ\eta_A
> =
> \eta_B\circ F(f).
> \]

![Naturality: translate then evolve equals evolve then translate.](figures/07-natural-transformation.png){width=63%}

The square says translation is uniform across structure.

### Projection-version migration

Suppose \(F\) and \(G\) are old and new timeline semantics over the same history category, and \(\eta_h:F(h)\to G(h)\) migrates the state at each history. Naturality says:

\[
\text{migrate after processing an extension}
=
\text{process the extension after migrating}.
\]

That is stronger than having a migration for each snapshot. It says migration commutes with every history arrow.

### Encoding transformations

A family of codecs indexed by schema type is natural only if every schema-preserving transformation commutes with encoding. This is why code generation can be more principled than a collection of unrelated serializers: it can enforce a uniform translation.

## Natural isomorphism and equivalence

A natural transformation is a natural isomorphism when each component is an isomorphism. Two functors connected by one are the same interpretation up to coherent representation change.

Categories \(\mathcal C\) and \(\mathcal D\) are equivalent when there are functors between them whose composites are naturally isomorphic to the respective identity functors.

Equivalence is often the correct notion for software representations. Requiring literal equality of type names or object identities is too strict; requiring only pairwise bijections is too weak because the bijections may not respect transformations.

## Functor categories

For categories \(\mathcal C\) and \(\mathcal D\), the functor category \(\mathcal D^{\mathcal C}\) has:

- functors \(\mathcal C\to\mathcal D\) as objects;
- natural transformations as arrows.

Presheaves on \(\mathcal C\) form the functor category

\[
\operatorname{Set}^{\mathcal C^{op}}.
\]

This is itself a topos when \(\mathcal C\) is small. Thus a whole universe of context-dependent sets and restriction-preserving transformations arises from an ordinary category of contexts.

## A caution about projections

A SessionStream `UIProjection` takes one event, session metadata, and a timeline view, and returns zero or more UI events. It is not automatically a functor as implemented. To obtain a functorial model, specify:

- a category of histories or transitions;
- an explicit state object containing all relevant prior information;
- composition by sequential event interpretation;
- equality of outputs, including whether UI word order matters.

The interface suggests an algebra, but the laws require proof or tests.

## Exercises

**9.1 [proof].** Extend an assignment of event generators to state endomorphisms into a unique functor from the free event-history category.

**9.2 [design].** Give a naturality square for migrating timeline entity version 1 to version 2. State one likely failure of naturality.

**9.3 [calculation].** For a two-object prefix category \(0\to1\), list the data of a presheaf and the data of a natural transformation between two such presheaves.

**9.4 [research].** Determine whether the current UI and timeline projections can be treated as two components of a product functor. List the purity and state assumptions required.

**9.5 [proof].** Show that natural isomorphism is an equivalence relation on functors with fixed domain and codomain.

# Presheaf Topoi and Stage-Indexed Validity

**Source alignment:** Goldblatt, Chapter 10, where functor categories on preorders are used to analyze set concepts, the subobject classifier, truth arrows, and validity.

## Variable sets

A presheaf is a set that varies over context. For a category \(\mathcal C\), a presheaf

\[
F:\mathcal C^{op}\to\operatorname{Set}
\]

assigns:

- a set \(F(U)\) of values available over each context \(U\);
- a restriction function \(F(U)\to F(V)\) for each arrow \(V\to U\);
- identity and composition laws for restriction.

A value is not simply "in \(F\)." It is a section \(s\in F(U)\) over some context \(U\).

For event cuts, \(F(n)\) might be the set of valid snapshots at cut \(n\). Restriction from \(n\) to \(m\le n\) requires historical information; the current-only SQLite state does not by itself define this presheaf, while the entity-version table can support it.

## Stage-indexed truth

In a presheaf topos over a preorder, the truth value of a proposition at a stage can be represented by the set of future refinements where it holds. Such sets are upward closed or, depending on arrow orientation, sieves.

The subobject classifier is therefore richer than \(\{0,1\}\). At context \(U\), \(\Omega(U)\) contains compatible collections of refinements of \(U\).

This is a formal version of statements such as:

- true now and under every future extension;
- not established now, but established after particular refinements;
- locally true under a cover;
- impossible under every extension.

## Subpresheaves

A subobject \(A\hookrightarrow F\) in a presheaf category consists of subsets

\[
A(U)\subseteq F(U)
\]

closed under restriction. If a section satisfies the property over \(U\), every restriction must satisfy the restricted property over smaller contexts.

This closure condition tests whether a proposed invariant is genuinely contextual.

For example, "this snapshot has no entity newer than its cut" is stable under a correct historical restriction. "This is the latest snapshot" is not stable under arbitrary restriction and needs a different index or formulation.

## The Yoneda viewpoint

Every object \(C\) determines a representable presheaf

\[
yC=\mathcal C(-,C).
\]

At context \(U\), \(yC(U)\) is the set of arrows \(U\to C\). The Yoneda lemma says

\[
\operatorname{Nat}(yC,F)\cong F(C).
\]

A section at \(C\) is the same as a natural way of converting every generalized element of \(C\) into an \(F\)-section.

For software intuition, an object is completely characterized by how every context can map into it. This is the ultimate external-description principle.

Goldblatt does not center the early exposition on Yoneda, so this section is supplemental, but it clarifies why generalized elements are sufficient.

## Parameter sufficiency as factorization

Let \(X\) be full semantic states and \(r:X\to P\) retain API parameters. Let \(I:X\to\Omega\) be an invariant predicate.

The parameters decide the invariant exactly when there exists a predicate

\[
J:P\to\Omega
\]

such that

\[
I=J\circ r.
\]

This is a factorization problem. In `Set` with Boolean truth, it means \(I\) is constant on every fiber

\[
r^{-1}(p).
\]

If two full states share the supplied parameters but give different invariant values, no parameter-only function can decide it.

The fiber formulation is:

\[
\forall x_1,x_2,
\quad
r(x_1)=r(x_2)
\Longrightarrow
I(x_1)=I(x_2).
\]

For a richer presheaf of contexts, sufficiency must also be natural under restriction. A decision procedure that works only at one stage but not compatibly across refinements is not a presheaf morphism.

## Context design is part of the theorem

Suppose `orderId` does not determine price because prices are versioned. The context object was too small. Replace it with `(orderId, priceVersion)`.

Mathematically, you refine the observation map

\[
r:X\to P
\]

to

\[
r':X\to P'.
\]

The invariant may factor through \(r'\) even though it did not factor through \(r\).

This provides a precise vocabulary for "missing parameter": the current context identifies states that the invariant needs to distinguish.

## Exercises

**10.1 [design].** Define a cut-indexed presheaf of SessionStream event prefixes. Define every restriction map and verify the laws.

**10.2 [design].** Define a presheaf of snapshots using historical `asOf` lookup. What happens at a cut for which no snapshot representation exists?

**10.3 [proof].** Prove the fiber criterion for factorization of a Boolean invariant through a surjective parameter map.

**10.4 [calculation].** Give a parameter map with fibers of sizes 1, 2, and 3. Define one invariant that factors through it and one that does not.

**10.5 [research].** Choose a current REST or WebSocket request in your software. List all full-state coordinates relevant to authorization and invariants. Determine which are present, derivable, or missing.

# Internal Languages and Schemas

**Source alignment:** Goldblatt, Chapter 11: first-order language, semantics, models in a topos, substitution, soundness, Kripke models, completeness, partial elements, and higher-order logic.

## Signatures before implementations

A first-order signature specifies:

- sorts;
- function symbols with input and output sorts;
- relation symbols with argument sorts.

A model interprets sorts as objects, function symbols as arrows, and relation symbols as subobjects.

A SessionStream schema registry resembles a fragment of a signature:

- command names and payload types;
- event names and payload types;
- UI event names and payload types;
- timeline entity kinds and payload types.

But a registry alone is not a logical theory. It does not state equations, invariants, quantifiers, or semantic truth conditions. It is admission metadata for typed alternatives.

## A small SessionStream language

Consider sorts:

```text
Session
Event
Ordinal
Entity
Snapshot
```

Function symbols might include:

\[
\operatorname{session}:Event\to Session,
\]

\[
\operatorname{ordinal}:Event\to Ordinal,
\]

\[
\operatorname{cut}:Snapshot\to Ordinal,
\]

\[
\operatorname{last}:Entity\to Ordinal.
\]

Relations might include:

\[
\operatorname{ContainedIn}(Entity,Snapshot),
\]

\[
\operatorname{ProjectsTo}(Event,Entity),
\]

\[
\operatorname{DeliveredTo}(Event,Connection).
\]

A consistent-cut axiom can then be written informally as

\[
\forall x\forall s,
\quad
\operatorname{ContainedIn}(x,s)
\Rightarrow
\operatorname{last}(x)\le\operatorname{cut}(s).
\]

A concrete model interprets these symbols in sets, database relations, traces, or internal objects of a topos.

## Terms as arrows

A term with variables in context \(\Gamma\) and result sort \(A\) is interpreted as an arrow

\[
\llbracket t\rrbracket:\llbracket\Gamma\rrbracket\to\llbracket A\rrbracket.
\]

A context of variables is interpreted by a product. Substitution is composition.

If \(t(x)\) is an ordinal-valued term and \(u(y)\) supplies an event for \(x\), then substituting \(u\) into \(t\) is

\[
\llbracket t[u/x]\rrbracket
=
\llbracket t\rrbracket\circ\llbracket u\rrbracket.
\]

This is why finite products and composition are prerequisites for logic.

## Formulas as subobjects

A formula \(\varphi\) in context \(\Gamma\) is interpreted as a subobject

\[
\llbracket\varphi\rrbracket
\hookrightarrow
\llbracket\Gamma\rrbracket.
\]

Conjunction, disjunction, and implication use the Heyting algebra of subobjects. Substitution pulls the subobject back along the term arrow.

Logical soundness becomes a statement that derivable sequents correspond to subobject inclusions in every model.

## Partial elements

Real software computations can fail to return a value. Goldblatt studies objects of partial elements later in Chapter 11. Categorically, a partial map can be represented by a domain subobject together with an arrow from that domain.

A partial decoder has:

\[
D\hookrightarrow Bytes
\]

as the subobject of decodable inputs and an arrow

\[
D\to Message.
\]

Returning `error` is one total encoding of this partiality. The domain-subobject model makes the admission predicate explicit.

For streaming handlers, termination is also partial at a finite stage. A terminal result exists only on the subobject of runs that have reached a terminal event.

## Internal versus external claims

An internal statement is expressed in the language interpreted inside the category. An external statement is made in the surrounding mathematics about the category or model.

Example:

- internal: "every entity in this snapshot has `last <= cut`";
- external: "the category of snapshots has a subobject interpreting that formula";
- implementation: a SQL query and Go scan construct a value claimed to satisfy it.

Do not slide between these levels. A schema validator can establish a syntactic internal predicate without proving a business event's external truth. A protobuf type proves shape, not authority or historical accuracy.

## Completeness is relative to a logic and model class

Goldblatt develops completeness results for logical systems and classes of models. In software, the analogous phrase "the checks are complete" is often used loosely.

A precise completeness claim must specify:

- the language of properties;
- the model class;
- the proof or checking system;
- whether every semantically valid property in that language is derivable or detected.

A linter that rejects top-level `Struct` is complete only for a narrowly specified syntactic policy, not for all schema quality.

## Exercises

**11.1 [design].** Write a many-sorted signature for SessionStream hydration. Include at least six sorts, eight functions, and six relations.

**11.2 [proof].** Show how substitution of terms becomes composition of arrows.

**11.3 [design].** Express snapshot-plus-suffix completeness as a family of first-order or temporal statements. Identify which parts exceed ordinary first-order logic.

**11.4 [recognition].** Separate schema-level, internal logical, external semantic, and implementation claims for a validated `Event`.

**11.5 [research].** State a narrow soundness and completeness theorem that `sessionstream-lint` could plausibly satisfy.

# Choice, Natural Numbers, and Recursive Folds

**Source alignment:** Goldblatt, Chapters 12-13: choice, natural numbers objects, categorical set theory, primitive recursion, and Peano-style structure.

## The categorical axiom of choice

One categorical form of choice says every epic arrow splits: for every epic \(e:A\to B\), there is \(s:B\to A\) with

\[
e\circ s=1_B.
\]

The section \(s\) chooses one preimage for each \(b\in B\).

In `Set`, this is related to the ordinary axiom of choice. In a general topos it is a strong condition and can force classical logical behavior.

Software systems often make local choices through canonicalization, ordering, or IDs. Such mechanisms are explicit selection functions, not appeals to a global axiom. A deterministic retry selector, for example, needs an actual section with stability laws.

## Natural numbers objects

> **Definition.** A natural numbers object consists of an object \(N\), a zero arrow
>
> \[
> 0:1\to N,
> \]
>
> and successor
>
> \[
> s:N\to N,
> \]
>
> satisfying a universal recursion property: for every object \(A\), point \(a:1\to A\), and endomorphism \(f:A\to A\), there is a unique \(h:N\to A\) with
>
> \[
> h\circ0=a,
> \qquad
> h\circ s=f\circ h.
> \]

The object is characterized by recursion, not by membership in a set-theoretic construction.

## Ordinals are not automatically an NNO

SessionStream uses `uint64` ordinals. That implementation type is not itself a categorical natural numbers object in the runtime category. It is bounded, can overflow, and is interpreted through storage and transport conventions.

A mathematical model may use \(\mathbb N\) as an NNO while proving that implementation ordinals refine a bounded prefix of it under an overflow precondition.

This separation is necessary for long-lived systems. A proof about \(\mathbb N\) does not silently discharge `uint64` overflow.

## Primitive recursion and folds

The NNO recursion property handles iteration indexed by natural numbers. Event replay is more naturally recursion over a free monoid or list object:

\[
\operatorname{fold}(S,\epsilon)=S,
\]

\[
\operatorname{fold}(S,he)
=
\delta(\operatorname{fold}(S,h),e).
\]

The same universal theme appears: a recursive interpreter is the unique arrow satisfying base and step equations.

If events are indexed by ordinals, the history length and event ordinal may correspond, but they are conceptually distinct:

- length counts positions in a particular word;
- ordinal is an architecture-assigned coordinate;
- event identity names a logical occurrence;
- bus stream ID is a transport coordinate.

## Induction as proof over construction

Induction proves a property for every value generated by zero and successor. For histories, structural induction proves:

1. the property holds for \(\epsilon\);
2. if it holds for \(h\), it holds for \(he\).

Many SessionStream laws should be stated this way.

Example: if every event transition preserves entity-key uniqueness, and the empty state has unique keys, then every folded history has unique keys.

Concurrency can invalidate the sequential induction model. Then the theorem applies to the abstract serial fold, while a separate refinement theorem must show that concurrent execution is observationally equivalent to some legal serial order.

## Recursion and snapshots

A snapshot can be viewed as a memoized fold result at cut \(n\). The reconstruction law

\[
\operatorname{fold}(S_n,e_{n+1}\cdots e_m)=S_m
\]

is a fusion or decomposition law for recursion.

A checkpoint is trustworthy when it is extensionally equal to folding the represented prefix. Otherwise suffix replay begins from a state outside the fold image and can compound the error.

## Exercises

**12.1 [proof].** Use structural induction on histories to prove the fold concatenation law.

**12.2 [design].** State an invariant preserved by every timeline event transition. Write the base and induction steps.

**12.3 [research].** List the proof obligations required to refine mathematical natural numbers to `uint64` ordinals.

**12.4 [calculation].** For a toy state machine, compute folds by both left recursion and prefix checkpoint plus suffix. Verify equality.

**12.5 [design].** Distinguish event length, event ordinal, stable event ID, and transport stream ID in types and laws.

# Presheaves as Contextual APIs

**Source alignment:** This chapter prepares Goldblatt Chapter 14 using the definitions of functor and limit already established. Goldblatt calls a presheaf over a topological space a "stack" in the older terminology used by the book.

## The base category of contexts

A presheaf begins with a category of contexts \(\mathcal C\). The choice of \(\mathcal C\) determines what locality means.

For SessionStream, useful context coordinates include:

- session \(s\);
- event cut \(n\);
- observer or subsystem \(K\);
- schema version \(v\);
- connection or subscription scope \(c\).

A context might therefore be a tuple

\[
U=(s,n,K,v,c).
\]

An arrow \(V\to U\) should mean that \(V\) is a smaller, more local, or less informative context contained in \(U\). Possible generators include:

- move from cut \(n\) to an earlier cut \(m\le n\);
- forget timeline facts while retaining event facts;
- forget connection-specific information;
- project a full schema to an older compatible interface;
- restrict a set of sessions to one session.

The direction must be chosen consistently. A presheaf will reverse these arrows.

## Definition of a presheaf

> **Definition.** A presheaf on \(\mathcal C\) is a functor
>
> \[
> F:\mathcal C^{op}\to\operatorname{Set}.
> \]

For each context \(U\), \(F(U)\) is the set of sections over \(U\). For each arrow \(i:V\to U\), there is a restriction map

\[
F(i):F(U)\to F(V),
\qquad
s\mapsto s|_V.
\]

Restrictions satisfy

\[
s|_U=s,
\]

and

\[
(s|_V)|_W=s|_W
\]

whenever \(W\to V\to U\).

![Information grows in the base direction while observations restrict contravariantly.](figures/08-presheaf-restriction.png){width=92%}

The word *section* should be read broadly: a local configuration, local observation, admissible assignment, or piece of data valid over the context.

## A cut presheaf of histories

Fix a session \(s\). Let the base category have natural cuts with an arrow \(m\to n\) when \(m\le n\).

Define

\[
H(n)=\{e_1\cdots e_n\},
\]

the singleton containing the actual prefix of one fixed execution. Restriction truncates a longer prefix to a shorter prefix.

This is a very simple presheaf: one section at each stage.

A more general presheaf has

\[
\mathcal H(n)=\{\text{all admissible histories of length }n\},
\]

with truncation. Now a global compatible family across all finite cuts is an infinite behavior whose every finite prefix is admissible. This begins to resemble safety-property semantics.

## A snapshot presheaf

Let \(S(n)\) be the set of coherent snapshots as of cut \(n\). A restriction

\[
S(n)\to S(m),\qquad m\le n,
\]

must reconstruct the historical state at \(m\).

The current SQLite design stores entity versions, so an `asOf` query can support this mathematically. A store retaining only current rows cannot generally define the restriction map. It may have values at each current cut, but no lawful way to restrict later state to earlier state.

This is a useful diagnostic:

> Having stage-indexed values does not make a presheaf. You must provide compositional restriction maps.

## A presheaf of observations

Let observer kinds be subsets of

\[
\{E,T,S,U,C\}
\]

for event, timeline, snapshot, live UI, and client observations. Order contexts by inclusion of visible dimensions.

Define \(F(K)\) as the set of locally valid assignments to all coordinates visible in \(K\). Restriction forgets coordinates.

For example,

\[
F(\{E,T,S\})\to F(\{T,S\})
\]

forgets event details but retains timeline and snapshot facts.

This presheaf formalizes the architecture as overlapping partial views. It does not yet assert that locally valid views come from a global execution. That is the sheaf question.

## Sections and fibers

Given a restriction \(r:F(U)\to F(V)\) and a local section \(v\in F(V)\), the fiber

\[
r^{-1}(v)
\]

contains all extensions of \(v\) to \(U\).

For API parameters, \(V\) is the supplied parameter context and \(U\) is the full semantic context.

- Empty fiber: the request cannot be completed consistently.
- Singleton fiber: the parameters determine a unique full state.
- Multiple-element fiber: the request is underdetermined.
- Invariant-constant fiber: the full state is underdetermined, but the invariant has one value across all completions.

This is the cleanest elementary answer to "are these parameters enough?"

## Presheaves of constraints

Let variables be distributed across contexts. Define

\[
F(U)=\{\text{assignments to variables in }U\text{ satisfying constraints visible in }U\}.
\]

Restriction forgets variables. This is a presheaf when restricting a valid assignment remains valid for the smaller set of visible constraints.

A global section is a full assignment satisfying every constraint.

This connects presheaves to constraint-satisfaction problems. It also supplies a practical software model before any additive algebra or cohomology is introduced.

## When restriction is not mere field deletion

Restriction may require computation.

- Restricting a snapshot to an earlier cut requires historical lookup or replay.
- Restricting a transport trace to a subsystem requires projecting and possibly coalescing events.
- Restricting a schema to an older version may apply a migration.
- Restricting a materialized entity set to a tenant may enforce authorization.

The only requirements are functoriality:

\[
\operatorname{restrict}_{U\to U}=1,
\]

\[
\operatorname{restrict}_{U\to W}
=
\operatorname{restrict}_{V\to W}
\circ
\operatorname{restrict}_{U\to V}.
\]

A migration chain that gives a different result from direct migration violates presheaf functoriality.

## Presheaf morphisms

A natural transformation \(\eta:F\Rightarrow G\) between presheaves is a context-compatible translation. For every restriction \(V\to U\),

\[
\eta_V(s|_V)
=
\eta_U(s)|_V.
\]

Examples:

- translating internal timeline entities to client models at every cut;
- redacting observations while preserving restriction;
- migrating schema versions consistently across contexts;
- deriving metrics from traces so that metrics of a restricted trace equal restricted metrics.

A transformation that inspects unavailable global state is not natural with respect to the chosen contexts.

## Exercises

**13.1 [design].** Define a context category with coordinates `(session, cut, observer-kind)`. Specify objects, generating arrows, and composition.

**13.2 [proof].** Verify that prefix truncation defines a presheaf of admissible histories.

**13.3 [design].** Determine whether current, historical, and replayable hydration stores define snapshot presheaves. Give the required restriction maps.

**13.4 [calculation].** Construct fibers for a toy API parameter map and classify them as impossible, unique, underdetermined, or invariant-sufficient.

**13.5 [proof].** Show that a family of schema migrations forms a presheaf restriction system exactly when identity and path-independence laws hold.

**13.6 [research].** Define a presheaf of authorization evidence. What must restriction do when moving to a smaller scope?

# Sheaves, Covers, and Snapshot-Plus-Live Gluing

**Source alignment:** Goldblatt Chapter 14, especially §14.1 on presheaves and the compatibility condition `COM`, §§14.2-14.5 on classifying sheaves and sites, and §14.6 on Kripke-Joyal semantics.

## Covers

A presheaf tells us how to restrict. A sheaf tells us when local pieces can be reconstructed globally.

On a topological space, a family of open subsets \(\{U_i\}\) covers \(U\) when

\[
U=\bigcup_i U_i.
\]

In a general site, covering families are specified abstractly and must satisfy stability and transitivity laws. This lets "cover" mean collectively sufficient observation rather than literal spatial union.

For software contexts, possible covers include:

- snapshot prefix plus post-cut suffix;
- event log plus deterministic projector;
- several service responses whose fields jointly cover an invariant;
- replicas or shards that collectively cover a dataset;
- component traces that jointly cover an execution.

A cover is part of the modeling structure. Declaring a family to cover means you assert that its local information should suffice, subject to compatibility, to determine the global object.

## Matching families

Let \(F\) be a presheaf and \(\{U_i\to U\}\) a cover. Choose local sections

\[
s_i\in F(U_i).
\]

They form a matching family when they agree on every overlap:

\[
s_i|_{U_i\cap U_j}
=
 s_j|_{U_i\cap U_j}.
\]

For a general site, overlaps are represented by pullbacks

\[
U_i\times_U U_j.
\]

The matching condition is pairwise equality after restriction to those pullbacks.

Pairwise compatibility is local evidence. It is necessary for gluing but, for a general presheaf, not sufficient.

## The sheaf condition

> **Definition.** A presheaf \(F\) is a sheaf for the chosen covers if every matching family \(\{s_i\}\) has a unique amalgamation
>
> \[
> s\in F(U)
> \]
>
> such that \(s|_{U_i}=s_i\) for every \(i\).

Existence says compatible local data can be assembled. Uniqueness says the local data determine the global section.

Goldblatt's `COM` condition is precisely this compatibility-and-unique-pasting law.

The sheaf condition can also be expressed as a limit. For a cover, \(F(U)\) is the equalizer of

\[
\prod_iF(U_i)
\rightrightarrows
\prod_{i,j}F(U_i\cap U_j),
\]

where the parallel arrows restrict each local section to the two sides of each overlap.

This equation directly links Chapter 4 limits to sheaves.

## Snapshot plus live suffix as a cover

The WebSocket hydration protocol has two information regions:

\[
U_{\mathrm{past}}=\text{history represented through cut }n,
\]

\[
U_{\mathrm{future}}=\text{accepted live observations after registration}.
\]

The local sections are:

\[
s_{\mathrm{past}}=S_n,
\]

\[
s_{\mathrm{future}}=q_{>n}.
\]

Their overlap or boundary data includes at least:

- the same `SessionId`;
- the cut \(n\);
- an agreement that future batches have ordinals strictly greater than \(n\);
- ordering and duplicate semantics.

The desired amalgamation is the reconstructed client state

\[
S_m=\operatorname{fold}(S_n,q_{>n}).
\]

![Snapshot and suffix as compatible local sections that glue into client state.](figures/09-sheaf-gluing.png){width=92%}

The current WebSocket implementation registers a subscription as hydrating before loading the snapshot, buffers concurrent UI batches, filters relative to `SnapshotOrdinal`, flushes later batches, and only then marks the subscription live. This is a concrete gluing algorithm.

## Existence, uniqueness, and explicit failure

The sheaf condition has two independent parts.

### Failure of existence

A snapshot says cut \(42\), but contains an entity with `LastEventOrdinal = 43`. No global "state at cut 42" restricts to both observations.

A hydration buffer overflows. The accepted local data cannot all be represented by the available snapshot-plus-buffer mechanism. Correct behavior is an explicit reconnect or overflow outcome, not silent gluing.

Two projections require incompatible values for one shared entity field. The matching family is not compatible.

### Failure of uniqueness

Parameters omit the price version. Several full orders restrict to the same request but have different totals.

Two schema interpretations agree on every exposed field but differ on hidden semantics.

A partial trace omits the linearization point, allowing several global orderings.

Uniqueness failures correspond to underdetermination. Add coordinates, strengthen overlaps, or accept a quotient notion of global state.

## The separatedness condition

A presheaf is *separated* when compatible local restrictions determine at most one global section. It satisfies uniqueness but not necessarily existence.

Software systems frequently achieve separatedness before full sheaf behavior:

- if a valid global execution exists, complete traces identify it uniquely;
- but some locally compatible traces may have no realizable global execution because of resource or timing constraints.

This distinction can sharpen architecture reviews. Ask separately:

1. Could two global states look identical through the cover?
2. Does every matching family correspond to a realizable state?

## Sites and Grothendieck topologies

A site is a category equipped with a notion of covering. One common formulation uses covering sieves.

A **sieve** on \(U\) is a collection of arrows into \(U\) closed under precomposition. If \(V\to U\) belongs to the sieve, then every composite \(W\to V\to U\) also belongs.

A Grothendieck topology designates certain sieves as covering, subject to:

1. the maximal sieve covers;
2. covers are stable under pullback;
3. local covers compose to covers.

For software, these laws mean:

- complete observation is sufficient;
- sufficient observation remains sufficient after reindexing to a smaller context;
- if a family covers a context and each member is itself covered, the combined finer family covers the original.

This formalism lets you choose application-specific locality.

## Example sites for SessionStream

### Cut site

Objects are cuts. A family covers \(n\) when its represented prefixes and suffix intervals jointly cover all ordinals through \(n\) without gaps and with compatible boundaries.

### Observer site

Objects are sets of observable dimensions. A family covers the global execution context when their union includes every coordinate required by the target invariant.

### Transaction site

Objects are persistence facts. A family is covering only when the facts are read or committed under one transaction or a recovery protocol that supplies equivalent atomic evidence.

This last choice is important. Pairwise access to event append, entity state, and cursor does not automatically cover the atomic commit fact. The topology should not declare an invalid family sufficient.

## Sheafification

Given a presheaf that fails gluing, one can often construct an associated sheaf by formally adding local equivalences and amalgamations. This is sheafification.

In engineering terms, sheafification resembles repairing an interface so that local data can be combined consistently. Possible operations include:

- add missing version coordinates;
- quotient representations by a justified local equivalence;
- insert a transaction boundary;
- retain enough history to define restrictions;
- add stable event IDs;
- replace implicit failure with an explicit outcome variant.

The analogy is useful, but mathematical sheafification is a specific universal construction: a left adjoint from presheaves to sheaves. Not every system repair is literally that construction.

## Local truth and Kripke-Joyal semantics

Sheaf semantics interprets truth over a context \(U\). A statement may hold locally on a cover without one global witness available on all of \(U\).

The characteristic clauses include:

- conjunction holds when both conjuncts hold on \(U\);
- implication holds when it is preserved after every restriction;
- disjunction holds when a cover exists on whose pieces one branch or the other holds;
- existence holds when a cover exists with local witnesses;
- universal quantification holds after every restriction for every local element.

The disjunction and existential clauses are local. To establish

\[
U\Vdash\exists x\,\varphi(x),
\]

one may have witnesses \(x_i\) on covering regions \(U_i\), without one global witness on \(U\).

### Software reading

A service federation may establish "there exists an owner for every shard" through local owners that do not glue to one global owner value. A UI may show one of two local rendering variants depending on feature context, even though no global branch is selected.

For SessionStream, "every accepted batch is covered" can be locally witnessed by either snapshot inclusion or suffix delivery. A constructive proof is a cover by these cases plus explicit overflow handling.

## A detailed hydration matching condition

Let a hydration trace contain:

- registration time \(r\);
- loaded snapshot cut \(n\);
- set \(A\) of batches accepted after \(r\);
- set \(P\) represented by the snapshot;
- ordered delivered suffix \(D\);
- explicit failures \(F\).

A completeness matching condition can be written

\[
A=P\sqcup D\sqcup F
\]

under a suitable identity relation, with

\[
\forall d\in D,\quad \operatorname{ord}(d)>n,
\]

and delivery order respecting ordinal order.

The disjoint-union symbol emphasizes that every accepted batch has exactly one custody outcome. If duplicates are allowed, replace set equality with a multiset or trace relation.

A global section is a complete trace assigning every accepted batch to one lawful outcome while agreeing with snapshot and delivery facts on overlaps.

## Why pairwise agreement may not be enough

Suppose three services expose pairwise compatible data:

- event store and timeline agree on cut;
- timeline and snapshot agree on entity rows;
- snapshot and client agree on rendered state.

There may still be no single event-to-client execution realizing all three if the pairwise agreements use different hidden versions. Pairwise overlaps omit a triple intersection coordinate.

This motivates higher-dimensional cells. An edge records pairwise compatibility. A filled triangle records a joint three-way witness. The nerve construction in Chapter 17 turns this overlap pattern into a shape.

## Exercises

**14.1 [proof].** Derive the equalizer formulation of the sheaf condition for a finite cover.

**14.2 [design].** Specify the overlap object between a snapshot and a live suffix. Include identity, cut, ordering, duplicate, and failure data.

**14.3 [lab].** Build a trace checker that partitions accepted hydration batches into snapshot-covered, suffix-delivered, and explicit-failure outcomes. Detect missing and duplicate custody.

**14.4 [design].** Give one SessionStream presheaf that is separated but not a sheaf.

**14.5 [proof].** Verify the Grothendieck-topology pullback-stability law for a simple cut-interval site.

**14.6 [research].** Choose which families should cover the atomic projection-progress fact. Explain why separate nontransactional reads may fail to be a cover.

**14.7 [calculation].** Construct a three-context example with pairwise compatible sections but no global section. Identify the missing triple-overlap information.

**14.8 [research].** Describe a sheafification-like repair for stable retry identity. Which new coordinate is introduced, and how do restriction maps treat it?

# Adjunctions, Reindexing, and Quantifiers

**Source alignment:** Goldblatt, Chapter 15: adjunctions, universal arrows, products and exponentials as adjoint situations, the fundamental theorem of topoi, and quantifiers.

## The hom-set correspondence

> **Definition.** A functor \(F:\mathcal C\to\mathcal D\) is left adjoint to \(G:\mathcal D\to\mathcal C\), written
>
> \[
> F\dashv G,
> \]
>
> when there is a bijection
>
> \[
> \mathcal D(F(A),B)
> \cong
> \mathcal C(A,G(B))
> \]
>
> natural in \(A\) and \(B\).

![An adjunction is a natural correspondence between two kinds of arrows.](figures/12-adjunction.png){width=72%}

An adjunction says that two differently shaped design problems are equivalent in a coherent way.

## Free and forgetful constructions

A classic pattern is:

\[
\text{free structure}\dashv\text{forgetful functor}.
\]

A free monoid on an event alphabet \(E\) is the history set \(E^*\). Any function from generators \(E\) to the underlying set of a monoid \(M\) extends uniquely to a monoid homomorphism

\[
E^*\to M.
\]

This is exactly why assigning semantics to event generators determines semantics for all histories.

In software, code generation often has a free/forgetful flavor: a schema declaration generates structured code, while forgetting returns the underlying signature. A literal adjunction requires carefully chosen categories and laws, so this should be treated as a modeling program rather than assumed.

## Product and exponential adjunction

In a Cartesian closed category, product with \(A\) is left adjoint to exponentiation by \(A\):

\[
(-)\times A\dashv(-)^A.
\]

The hom-set bijection is currying:

\[
\mathcal C(X\times A,B)
\cong
\mathcal C(X,B^A).
\]

For dependency-injected projectors, an arrow

\[
C\times(S\times E)\to T
\]

is equivalent to

\[
C\to T^{S\times E}.
\]

One view supplies configuration at each invocation; the other selects a configured projector once.

## Reindexing predicates

Given \(f:A\to B\), pullback sends a subobject of \(B\) to one of \(A\):

\[
f^*:\operatorname{Sub}(B)\to\operatorname{Sub}(A).
\]

This is substitution or inverse image. A predicate on \(B\) becomes a predicate on \(A\) by applying \(f\).

In `Set`, for \(Q\subseteq B\),

\[
f^*(Q)=f^{-1}(Q).
\]

## Existential quantification as a left adjoint

The left adjoint to inverse image is direct image:

\[
\exists_f\dashv f^*.
\]

For \(P\subseteq A\),

\[
\exists_f(P)
=
\{b\in B:\exists a\in P,\ f(a)=b\}.
\]

The adjunction law is

\[
\exists_f(P)\subseteq Q
\quad\Longleftrightarrow\quad
P\subseteq f^{-1}(Q).
\]

### Software example

Let \(f:Event\to Session\). For an event predicate \(P\), \(\exists_f(P)\) is the set of sessions having at least one event satisfying \(P\).

For example:

\[
\exists_f(\text{terminal-event})
\]

is the predicate "this session has some terminal event."

## Universal quantification as a right adjoint

In a topos, inverse image also has a right adjoint:

\[
f^*\dashv\forall_f.
\]

In `Set`,

\[
\forall_f(P)
=
\{b\in B:\forall a,
\ f(a)=b\Rightarrow a\in P\}.
\]

For \(f:Event\to Session\), \(\forall_f(P)\) is the set of sessions all of whose events satisfy \(P\).

The adjunction law is

\[
f^{-1}(Q)\subseteq P
\quad\Longleftrightarrow\quad
Q\subseteq\forall_f(P).
\]

Quantifiers therefore arise from changing context along a projection. If \(\pi:X\times Y\to X\), then

\[
\exists_\pi
\]

and

\[
\forall_\pi
\]

interpret quantification over \(Y\).

## Parameter sufficiency revisited

Let \(r:X\to P\) forget hidden state. Pullback

\[
r^*:\operatorname{Sub}(P)\to\operatorname{Sub}(X)
\]

turns parameter predicates into full-state predicates.

A full invariant \(I\hookrightarrow X\) is exactly expressible from parameters when it lies in the image of \(r^*\):

\[
I=r^*(J)
\]

for some \(J\hookrightarrow P\).

The approximations

\[
\exists_r(I)
\]

and

\[
\forall_r(I)
\]

have distinct meanings:

- \(\exists_r(I)\): parameters admit at least one completion satisfying \(I\);
- \(\forall_r(I)\): every completion satisfying those parameters obeys \(I\).

For transaction safety, \(\forall_r(I)\) is the relevant guarantee. Existential satisfiability is insufficient.

## Pullback functors between slice categories

For \(f:A\to B\), pulling back bundles over \(B\) yields bundles over \(A\):

\[
f^*:\mathcal C/B\to\mathcal C/A.
\]

In a topos this functor has both adjoints:

\[
\Sigma_f\dashv f^*\dashv\Pi_f.
\]

This is the fundamental theorem emphasized by Goldblatt.

- \(\Sigma_f\) aggregates or composes dependent data along \(f\);
- \(f^*\) reindexes it;
- \(\Pi_f\) forms dependent products or families of local sections.

Dependent types are close to this picture: a bundle \(p:E\to B\) is a family of fibers \(E_b\), and reindexing substitutes base values.

## Unit and counit as round-trip maps

Every adjunction has a unit

\[
\eta:1_{\mathcal C}\Rightarrow G F
\]

and counit

\[
\varepsilon:F G\Rightarrow1_{\mathcal D}
\]

satisfying triangle identities.

These are not generally isomorphisms. Adjunction is weaker than equivalence.

In software, a parse/pretty-print pair often forms an approximation pattern rather than an isomorphism:

- parse after print may recover the semantic object exactly;
- print after parse may canonicalize the source.

This resembles a reflection, a special adjunction where one side embeds a subcategory of canonical objects.

## Exercises

**15.1 [proof].** Derive the free-monoid adjunction between sets and monoids.

**15.2 [calculation].** For a finite map \(f:A\to B\) and subset \(P\subseteq A\), compute \(\exists_f(P)\) and \(\forall_f(P)\).

**15.3 [design].** Let `Event -> Session` be the scope map. Define event predicates whose existential and universal pushforwards answer useful operational questions.

**15.4 [proof].** Verify both adjunction laws for inverse image, existential image, and universal image in `Set`.

**15.5 [design].** For a REST parameter map, interpret \(\exists_r(I)\), \(\forall_r(I)\), and exact descent \(I=r^*(J)\).

**15.6 [research].** Identify a canonicalization pipeline in your software. Model it as a reflection if possible, stating the unit, fixed objects, and universal property.

# Geometric Morphisms and Architectural Translation

**Source alignment:** Goldblatt, Chapter 16: preservation and reflection, geometric morphisms, internal and geometric logic, and theories as sites.

## Preservation and reflection

A functor preserves a construction when applying the functor to a construction in the source yields the corresponding construction in the target. It reflects a property when the property of the image implies the property in the source.

Examples:

- a left-exact functor preserves finite limits;
- a faithful functor can reflect equality of arrows;
- an equivalence preserves and reflects all categorical properties expressible up to isomorphism.

For software translations, preservation questions are concrete:

- Does encoding preserve products of independent fields?
- Does replay preserve event order?
- Does a redaction functor preserve pullback-defined authorization predicates?
- Does a client projection preserve the equalizer of live and replay semantics?

A translation can be useful while failing to preserve important constructions. The failed preservation identifies information loss.

## Geometric morphisms

> **Definition.** A geometric morphism from a topos \(\mathcal E\) to a topos \(\mathcal F\) consists of an adjunction
>
> \[
> f^*:\mathcal F\rightleftarrows\mathcal E:f_*
> \]
>
> where \(f^*\) is left adjoint to \(f_*\) and preserves finite limits.

The functor \(f^*\) is called inverse image and \(f_*\) direct image. The direction of the named geometric morphism is opposite to the inverse-image functor.

Finite-limit preservation means inverse image preserves finite contexts and equations. This is why geometric logic is stable under geometric morphisms.

## Software analogy: changing worlds of observation

Suppose \(\mathcal F\) models backend semantic contexts and \(\mathcal E\) models browser-visible contexts. A translation may pull backend predicates and objects into the browser world while a right adjoint aggregates browser observations back into backend descriptions.

This is only a geometric morphism if the selected categories are topoi, the functors form an adjunction, and inverse image preserves finite limits. Ordinary serialization adapters should not be called geometric morphisms without this structure.

The analogy nevertheless suggests good questions:

- Which finite-limit invariants survive transport?
- Does the browser representation preserve matching of name and descriptor?
- Are conjunctions and equalities preserved?
- Which existential facts can be transported?
- Which information is visible only after direct image aggregation?

## Geometric logic

Geometric formulas are built using:

- finite conjunctions;
- arbitrary disjunctions, subject to size conditions;
- existential quantification;
- equality;
- truth and falsehood.

They avoid unrestricted implication, negation, and universal quantification. Geometric formulas are preserved by inverse-image functors of geometric morphisms.

For distributed software, geometric logic matches a class of positive, locally witnessable claims:

- some event with a property exists;
- one of a family of explicit outcomes occurred;
- several equalities and predicates hold together.

Claims involving absence, global universal guarantees, or negation require more care under change of context.

## Theories as sites

A logical theory can generate a category of syntactic contexts and arrows, then a topology describing which families of formulas cover another. Sheaves on this site form a classifying topos for the theory.

The deep idea is:

> A theory has a geometric space of models, even when no ordinary point-set space is given.

For software, one can imagine a specification theory whose:

- objects are finite interface contexts;
- arrows are substitutions or refinements;
- covers are collectively sufficient case splits or observations;
- sheaves are implementations that assign compatible data and glue it.

This is a research direction, not a claim that SessionStream currently has a classifying topos.

## Refinement as a functor with laws

The SessionStream verification work distinguishes pure transition kernels from Go runtime shells and asks for trace inclusion or abstraction mappings. A categorical formulation begins with a functor-like interpretation

\[
\alpha:\text{ConcreteTraces}\to\text{AbstractTraces}
\]

that preserves identity and concatenation.

Safety refinement then asks that every concrete trace map to an allowed abstract trace. Stronger claims ask preservation of limits, observations, or accepted-work custody.

Naturality appears when abstraction commutes with subsystem projection:

\[
\alpha(\text{concrete trace restricted to component})
=
\text{abstract trace restricted to component}.
\]

This connects formal verification to the presheaf language: refinement should be a morphism of observation presheaves, not merely a final-state map.

## Exercises

**16.1 [design].** Choose a SessionStream translation such as protobuf encoding, WebSocket framing, or client projection. List finite-limit constructions it preserves and fails to preserve.

**16.2 [proof].** Show that a functor preserving terminal objects and pullbacks preserves all finite limits.

**16.3 [recognition].** Classify five system properties as geometric or non-geometric in form.

**16.4 [research].** Sketch a site for a small event-driven protocol theory. Define contexts, arrows, and covers.

**16.5 [design].** Define an abstraction map from concrete WebSocket traces to an abstract hydration state machine. State identity, composition, and restriction-naturality laws.

# From Covers to Multidimensional Shapes

**Supplemental material:** Goldblatt develops presheaves, sheaves, sites, and local truth but does not introduce cohomology. This chapter begins the additional route requested for connecting those ideas to topological shapes.

## The nerve of a cover

Let \(\{U_i\}_{i\in I}\) be a cover. Its **nerve** is a simplicial complex built from overlap data.

- A vertex \(i\) represents one context \(U_i\).
- An edge \((i,j)\) exists when \(U_i\cap U_j\) is relevant or nonempty.
- A triangle \((i,j,k)\) exists when the three contexts have a joint overlap.
- A tetrahedron exists when four contexts have a joint overlap.
- Higher simplices continue the pattern.

The dimension records the order of joint compatibility, not physical dimension.

For an architecture cover:

- vertices can be EventStore, Timeline, Snapshot, Live UI, and Client;
- edges record shared facts or comparison contracts;
- triangles record contexts where three components can be jointly witnessed;
- missing faces record absent higher-order witnesses.

![A possible nerve of SessionStream observation contexts. Edges record overlaps; a missing face can leave a cycle.](figures/10-architecture-nerve.png){width=62%}

## Why triangles matter

Three pairwise comparisons do not necessarily imply one three-way compatible state.

Suppose:

- EventStore and Timeline agree under schema version \(v_1\);
- Timeline and Snapshot agree under version \(v_2\);
- Snapshot and EventStore agree after a migration.

Every edge can pass its own check while no single versioned triple realizes all three. An actual three-way observation context supplies the triangle that records joint compatibility.

A triangle is therefore not decorative. It says the boundary loop is filled by a higher-order witness.

## Cycles and holes

A graph cycle is a closed path of pairwise overlaps. If the cycle is not the boundary of included higher-dimensional faces, it can support circulation data that cannot be reduced to local vertex assignments.

![An unfilled cycle can support a first cohomology class; filling it supplies a higher-order compatibility condition.](figures/11-cycle-vs-filled.png){width=90%}

The intuitive word *hole* means that a compatible-looking boundary lacks an interior witness in the chosen complex.

This statement is model-relative. Adding a transaction or joint observer can add a simplex and fill a hole. Forgetting joint evidence can remove a simplex and create one.

## Architecture as a simplicial complex

A disciplined construction is:

1. Choose a target invariant.
2. List the minimal contexts that observe parts of it.
3. Add an edge when two contexts share data with a comparison map.
4. Add a higher simplex only when there is a real joint observation or compatibility witness.
5. Attach local values to every simplex through a presheaf or cellular sheaf.

Do not add a triangle merely because all three edges exist. That would assume the theorem you want to test.

## Example: snapshot consistency complex

Choose vertices:

\[
\begin{aligned}
E &= \text{event-store cut},\\
P &= \text{projection checkpoint},\\
S &= \text{snapshot cut},\\
L &= \text{maximum entity last-event coordinate}.
\end{aligned}
\]

Edges represent comparison contracts:

- \(E-P\): projector progress relative to durable events;
- \(P-S\): materialization progress relative to snapshot cut;
- \(S-L\): entities represented by the snapshot;
- \(L-E\): entity provenance relative to event history.

A transaction that atomically reads or commits \(E,P,S,L\) can justify a filled higher-dimensional cell. Without it, the graph may be only a cycle of pairwise observations taken at different instants.

The shape itself warns you that pairwise tests may miss a global race.

## The nerve is not the data

The nerve records where overlaps exist. A sheaf or coefficient system records what values live over vertices, edges, and faces and how they restrict.

Two systems can have the same nerve but different local data and different cohomology. Conversely, the same values attached to a different complex can behave differently because cycles have been filled or opened.

Topology studies the shape of compatibility. Sheaf theory studies values varying over that shape.

## Refining the cover

You may split one context into smaller contexts or add more observers. This refines the cover.

A good invariant should not depend arbitrarily on the granularity of observation. Čech cohomology often studies behavior under refinements and, in suitable settings, stabilizes to sheaf cohomology.

For software, compare:

- one coarse "WebSocket" context;
- separate reader, writer, heartbeat, request-worker, and observer-dispatch contexts.

The refined cover can reveal cycles and missing joint witnesses hidden by the coarse box.

## Exercises

**17.1 [design].** Build a nerve for the core SessionStream pipeline. Add an edge only when you can name the shared data and restriction maps.

**17.2 [design].** Identify three contexts that are pairwise comparable but lack one joint atomic witness. Draw the unfilled triangle.

**17.3 [research].** Explain how adding a database transaction changes the complex rather than merely changing a value on an existing vertex.

**17.4 [calculation].** For a cover of four contexts, list all possible vertices, edges, triangles, and tetrahedra. Mark which exist in your architecture.

**17.5 [lab].** Generate a simplicial complex from a trace schema: add a simplex whenever one trace record jointly contains the corresponding context IDs.

# Cochains, Coboundaries, and Cohomology

## Why algebra enters

A set-valued sheaf can express gluing, but subtraction of discrepancies is unavailable. Cohomology requires coefficients with algebraic structure, usually abelian groups, modules, or vector spaces.

We therefore choose a sheaf \(\mathcal F\) of abelian groups. Examples of additive diagnostics include:

- ordinal offsets;
- signed count differences;
- parity bits;
- conservation-law residuals;
- log-probability or cost differences in linearized models;
- vector-clock deltas after embedding into a module.

Business states themselves are rarely abelian groups. Cohomology usually applies to a diagnostic abstraction of them.

## Čech cochains

For a cover \(\mathcal U=\{U_i\}\), define

\[
C^0(\mathcal U,\mathcal F)
=
\prod_i\mathcal F(U_i),
\]

\[
C^1(\mathcal U,\mathcal F)
=
\prod_{i<j}\mathcal F(U_i\cap U_j),
\]

\[
C^2(\mathcal U,\mathcal F)
=
\prod_{i<j<k}\mathcal F(U_i\cap U_j\cap U_k),
\]

and so forth.

A 0-cochain assigns a local value to each context. A 1-cochain assigns a value to each overlap. A 2-cochain assigns a value to each triple overlap.

## The first coboundary

For a 0-cochain \(x=(x_i)\), define the edge discrepancy

\[
(\delta^0x)_{ij}
=
 x_j|_{U_i\cap U_j}
-
 x_i|_{U_i\cap U_j}.
\]

If \(\delta^0x=0\), the local values form a matching family.

Thus

\[
H^0=\ker\delta^0
\]

is the group of compatible local sections, and for a sheaf it corresponds to global sections over the covered region.

## The second coboundary

For a 1-cochain \(r=(r_{ij})\), on an oriented triple \(i<j<k\),

\[
(\delta^1r)_{ijk}
=
 r_{jk}-r_{ik}+r_{ij},
\]

with all terms restricted to the triple overlap.

This is the circulation around the triangle boundary. A 1-cochain is a cocycle when

\[
\delta^1r=0.
\]

Every discrepancy produced from vertex values is automatically a cocycle:

\[
\delta^1\delta^0=0.
\]

The cancellation is algebraic: every vertex term appears twice with opposite signs.

## First cohomology

The first cohomology group is

\[
H^1
=
\frac{\ker\delta^1}{\operatorname{im}\delta^0}.
\]

- \(\ker\delta^1\) contains edge assignments satisfying all triangle consistency conditions.
- \(\operatorname{im}\delta^0\) contains edge assignments explained by choosing local vertex coordinates.
- A nonzero class is a locally consistent circulation that cannot be removed by changing local coordinates.

This is the precise version of "go around a loop and return shifted."

## A cycle graph

Take five contexts arranged in a cycle, with coefficients in \(\mathbb R\). Orient edges

\[
0\to1\to2\to3\to4\to0.
\]

A 0-cochain is a vector

\[
x=(x_0,x_1,x_2,x_3,x_4).
\]

Its coboundary is

\[
\delta^0x=
\begin{bmatrix}
-1&1&0&0&0\\
0&-1&1&0&0\\
0&0&-1&1&0\\
0&0&0&-1&1\\
1&0&0&0&-1
\end{bmatrix}x.
\]

There are no filled triangles, so \(C^2=0\) and every 1-cochain is a cocycle. The matrix has rank 4. Therefore

\[
\dim H^1=5-4=1.
\]

The invariant coordinate is total circulation:

\[
r_{01}+r_{12}+r_{23}+r_{34}+r_{40}.
\]

Every gradient \(\delta^0x\) has zero total circulation. A nonzero sum cannot be explained by local coordinates.

## A filled triangle

For vertices \(0,1,2\) with the triangle included, a 1-cochain \(r\) must satisfy

\[
r_{12}-r_{02}+r_{01}=0
\]

to be a cocycle.

The face enforces zero circulation. The boundary loop is filled, and for constant coefficients on one filled triangle,

\[
H^1=0.
\]

This is the algebraic meaning of adding a genuine joint compatibility witness.

## Higher cohomology

In general,

\[
H^n
=
\frac{\ker\delta^n}{\operatorname{im}\delta^{n-1}}.
\]

- \(H^0\): global compatible sections or degrees of freedom.
- \(H^1\): loop-like twisting and first-order gluing obstructions.
- \(H^2\): higher coherence obstructions over shells of triangles or 2-dimensional boundaries.

The interpretation depends on the sheaf. It is incorrect to assign a universal software meaning such as "\(H^1\) equals bugs." Cohomology reports structure in the chosen coefficient system.

## Sheaf cohomology versus ordinary topology

Ordinary simplicial cohomology uses constant coefficients attached uniformly to the space. Sheaf cohomology lets coefficient groups vary by context with nontrivial restriction maps.

For SessionStream, the EventStore-Timeline overlap may expose different diagnostic coordinates than the Snapshot-Client overlap. A cellular sheaf can attach different vector spaces to vertices and edges and linear restriction maps between them.

This is more expressive than a constant-value graph, and often the correct model for heterogeneous components.

## Obstruction logic and its limits

In some sheaf-theoretic formulations, a nonzero cohomology class certifies that a local family cannot be extended globally. But several cautions are essential.

1. The obstruction may be sufficient but not necessary.
2. Linearization can forget nonlinear conflicts.
3. Vanishing cohomology does not guarantee a global section for arbitrary set-valued constraints.
4. A bad choice of cover or coefficients can hide the relevant problem.
5. A nonzero class may reflect an intended feature, such as a legitimate phase or gauge freedom, not a defect.

The reliable workflow is:

\[
\text{set-valued gluing problem}
\to
\text{diagnostic linearization}
\to
\text{cohomology as one source of evidence}.
\]

## Exercises

**18.1 [calculation].** Compute \(H^0\) and \(H^1\) over \(\mathbb R\) for a path of four vertices.

**18.2 [calculation].** Compute them for a square cycle with no face.

**18.3 [calculation].** Add a diagonal and two filled triangles to the square. Recompute \(H^1\).

**18.4 [proof].** Verify directly that \(\delta^1\delta^0=0\) on a triangle.

**18.5 [design].** Choose an additive diagnostic for SessionStream and define coefficient groups on contexts and overlaps.

**18.6 [research].** Give a nonlinear global-section failure that is invisible after reducing all values modulo 2.

# Cohomological Case Studies for SessionStream

## Case study: ordinal convention holonomy

Suppose five adapters use local coordinates for the same logical cut:

- \(x_E\): EventStore cursor;
- \(x_P\): projection checkpoint;
- \(x_S\): snapshot cut;
- \(x_W\): WebSocket suffix boundary;
- \(x_C\): client last-seen coordinate.

On each overlap, an adapter declares an offset

\[
r_{ij}=x_j-x_i.
\]

If all offsets arise from actual local coordinates, the sum around every architecture loop must be zero.

Imagine these conventions:

```text
EventStore:       last included event
Projection:       last included event
Snapshot:         last included event
WebSocket:        next event expected
Client:           last included event
```

The Snapshot-to-WebSocket conversion introduces \(+1\), but a later adapter treats WebSocket's value as already "last included" and introduces no compensating \(-1\). Around the loop, total circulation is \(+1\).

Every pairwise adapter can pass local examples. Globally, the coordinate returns shifted. This is a nontrivial \(H^1\) class in the cycle model.

The engineering fix can take several forms:

- type `LastIncludedOrdinal` and `NextExpectedOrdinal` separately;
- make every edge conversion explicit;
- add a joint protocol witness that fills the loop and enforces zero circulation;
- remove an unjustified comparison edge.

## Case study: atomic projection progress

Facts include:

\[
E=\text{event appended through }n,
\]

\[
T=\text{timeline materialized through }n,
\]

\[
P=\text{projection cursor equals }n.
\]

A crash can produce

```text
event cursor       = n
timeline state     = n
projection cursor  = n-1
```

or another partial combination depending on commit order.

This is first a global-section problem: does one committed-state object restrict to these local observations under the declared transaction semantics?

A linear cohomology model can track coordinate differences, but it does not by itself capture atomicity, crash timing, or the distinction between durable and attempted effects. The correct base model should include transaction states or a recovery state machine. Cohomology may then diagnose loops of progress claims, but it does not replace the state-machine proof.

## Case study: consistent-cut snapshots

The safety condition is

\[
\forall x\in\operatorname{Entities}(S),
\quad
\operatorname{LastEventOrdinal}(x)
\le
\operatorname{SnapshotOrdinal}(S).
\]

This is an inequality constraint, not naturally an abelian equality. A set-valued or order-valued sheaf is the primary model.

One can derive additive residuals

\[
d_x=
\operatorname{LastEventOrdinal}(x)
-
\operatorname{SnapshotOrdinal}(S).
\]

Safety requires \(d_x\le0\). Cohomology of residual differences might help locate inconsistent cycles among readers, but positivity is order structure, not captured by group cohomology alone.

This case teaches when not to force cohomology onto a problem.

## Case study: stable retry identity

Consider contexts:

- producer logical event;
- bus message;
- consumed event;
- persisted event row;
- projected entity update.

Each overlap carries some subset of:

```text
EventId
MessageId
SessionId
StreamId
Ordinal
PayloadDigest
```

A global section is one coherent identity assignment across the delivery path.

If the current model has no `EventId`, two consumed deliveries with different ordinals can both extend the same producer event. This may be non-unique gluing rather than a cohomological obstruction: the local coordinates simply do not distinguish logical occurrence from delivery occurrence.

Add the missing coordinate first. Then study whether overlap transformations preserve it.

## Case study: schema registry as a pullback, not a hole

The condition

\[
\operatorname{registryDescriptor}(name)
=
\operatorname{payloadDescriptor}(payload)
\]

is a pullback constraint. There is no need for cohomology when one local equality check and its universal object solve the problem.

Cohomology becomes relevant when schema information is distributed around a cover with loops of migrations, aliases, or version translations. A cycle of type-name transformations can carry a nontrivial automorphism even when each edge is locally valid.

## Case study: observer traces

Suppose separate observers record:

- connection lifecycle;
- request decoding;
- hydration transitions;
- fanout;
- write completion;
- observer-queue admission and drops.

A presheaf assigns compatible partial traces to subsystem contexts. A global section is one execution trace whose projections equal every observer trace.

Potential failures include:

- missing events: no global trace projects to all logs;
- ambiguous ordering: several global traces fit the same partial orders;
- clock offsets: additive edge data have nonzero circulation;
- observer drops: explicit gaps mean the cover is not complete unless drop evidence is included.

Vector clocks, interval orders, and happens-before relations are often better primary coefficients than scalar timestamps. Linear embeddings can then support cohomological diagnostics.

## A worked four-cycle

Take contexts \(E,P,S,C\) and observed relative offsets:

\[
r_{EP}=0,
\quad
r_{PS}=0,
\quad
r_{SC}=1,
\quad
r_{CE}=0.
\]

The total circulation is

\[
0+0+1+0=1.
\]

No vertex coordinates \(x_E,x_P,x_S,x_C\) satisfy all equations

\[
x_P-x_E=0,
\]

\[
x_S-x_P=0,
\]

\[
x_C-x_S=1,
\]

\[
x_E-x_C=0.
\]

Adding the equations gives \(0=1\). The 1-cochain is non-exact.

A diagnostic should report both:

- the nonzero class or circulation value;
- one supporting cycle, here \(E\to P\to S\to C\to E\).

The cycle is more actionable than a bare matrix rank.

## What a useful tool should say

Bad diagnostic:

```text
H^1 dimension = 1
```

Useful diagnostic:

```text
No coherent ordinal coordinate exists.
Cycle: EventCursor -> ProjectionCursor -> SnapshotCut -> ClientCursor -> EventCursor
Accumulated offset: +1
Likely convention mismatch: SnapshotCut is "last included" while ClientCursor is treated as both "next expected" and "last included".
```

Mathematics should compress evidence without hiding the architecture.

## Exercises

**19.1 [calculation].** Solve the four-cycle equations above directly and derive the contradiction.

**19.2 [design].** Build an ordinal-convention graph for SessionStream. Label every edge with a conversion function and linearized offset.

**19.3 [research].** Determine which projection-progress failures are representable as additive cocycles and which require a transition-system model.

**19.4 [design].** Define a global-section identity model for retries, including producer, bus, store, and projector contexts.

**19.5 [lab].** From a recorded trace, construct edge timestamp offsets and search for cycles with nonzero circulation. Account for clock uncertainty intervals.

# Building a Local-to-Global Checker

## Two layers, not one

A practical checker should have two separate engines.

### Layer A: set-valued consistency

This layer handles arbitrary values and constraints.

- contexts and sections;
- restriction functions;
- covers and overlaps;
- matching-family checks;
- global-section search through SAT, SMT, CSP, database queries, or explicit enumeration.

### Layer B: additive diagnostics

This layer handles abelian-group or vector-space abstractions.

- incidence and restriction matrices;
- coboundary operators;
- cocycle checks;
- exactness solving;
- basis vectors and supporting cycles.

Layer B is an explanation and obstruction tool for selected diagnostics. It must not silently replace Layer A.

## A declarative model

A compact input format might be:

```yaml
contexts:
  - id: event
    fields: [session, event_cursor]
  - id: projection
    fields: [session, projection_cursor]
  - id: snapshot
    fields: [session, snapshot_cut]
  - id: client
    fields: [session, client_cursor]

overlaps:
  - [event, projection]
  - [projection, snapshot]
  - [snapshot, client]
  - [client, event]

faces: []

coefficients:
  type: integers
  edge_value: ordinal_offset
```

A richer version describes restriction code, schemas, allowed covers, and trace provenance.

## Verifying presheaf laws

Before gluing, test restriction itself.

For every section \(s\in F(U)\):

\[
\operatorname{res}_{U,U}(s)=s.
\]

For every chain \(W\to V\to U\):

\[
\operatorname{res}_{U,W}(s)
=
\operatorname{res}_{V,W}(
\operatorname{res}_{U,V}(s)).
\]

Property-based tests can generate contexts and sections. A failure means the object is not even a presheaf; sheaf checks are premature.

## Checking matching families

For every cover \(\{U_i\to U\}\) and local sections \(s_i\), compare restrictions on overlaps:

\[
\operatorname{res}_{U_i,U_i\times_UU_j}(s_i)
=
\operatorname{res}_{U_j,U_i\times_UU_j}(s_j).
\]

Report discrepancies with:

- context IDs;
- overlap fields;
- source trace or row identifiers;
- expected versus observed values;
- schema versions and cut coordinates.

## Searching for global sections

For finite domains, encode all local variables and constraints in an SMT solver. A satisfying assignment is a global section. No assignment means a genuine incompatibility relative to the model.

To test uniqueness, ask for a second distinct satisfying assignment after blocking the first.

Results are:

```text
UNSAT          no global section
SAT-UNIQUE     exactly one global section
SAT-MULTIPLE   underdetermined
UNKNOWN        resource or theory limitation
```

For API sufficiency, `SAT-MULTIPLE` can still be invariant-sufficient if the invariant has the same value in every model. Ask the solver for two completions with opposite invariant values.

## Building coboundary matrices

For a simplicial complex with constant scalar coefficients:

- enumerate vertices and oriented edges;
- construct \(D_0\), one row per edge, with \(-1\) at the tail and \(+1\) at the head;
- enumerate oriented triangles;
- construct \(D_1\), one row per triangle, with signed edge incidences;
- verify \(D_1D_0=0\).

Then:

- a 0-cochain \(x\) has discrepancy \(D_0x\);
- a 1-cochain \(r\) is a cocycle when \(D_1r=0\);
- it is exact when \(D_0x=r\) has a solution.

Over a field,

\[
\dim H^1
=
\dim\ker D_1-\operatorname{rank} D_0.
\]

Over integers, Smith normal form also detects torsion.

## A Go-oriented sketch

```go
type Complex struct {
    Vertices  []string
    Edges     []OrientedEdge
    Triangles []OrientedTriangle
}

type Diagnostic struct {
    EdgeValues map[OrientedEdge]int64
}

type CohomologyResult struct {
    IsCocycle      bool
    IsExact        bool
    TriangleErrors []TriangleResidual
    CycleWitnesses []CycleResidual
}
```

The checker pipeline is:

```text
validate complex
-> build D0 and D1
-> assert D1*D0 == 0
-> check D1*r == 0
-> solve D0*x == r
-> if unsolved, extract a cycle witness
```

For floating timestamps, use rational values, exact integer ticks, or tolerance-aware interval constraints. Naive floating-point rank can create false classes.

## Cellular sheaves for heterogeneous data

A more realistic checker attaches a vector space \(F(v)\) to each component and \(F(e)\) to each overlap, with linear restriction maps

\[
\rho_{v,e}:F(v)\to F(e).
\]

The degree-zero coboundary on edge \(e=(u,v)\) is

\[
(\delta x)_e
=
\rho_{v,e}(x_v)-\rho_{u,e}(x_u).
\]

This allows EventStore to expose `(eventCursor, streamId)` while Snapshot exposes `(snapshotCut, maxEntityOrdinal)`, and the overlap compares only a shared linear projection.

Constructing these maps is the main modeling work. Matrix computation is the easy part.

## Integration with traces

Each diagnostic should retain provenance:

```text
value
context
source record ID
wall-clock interval
logical cut
schema version
confidence or uncertainty
```

When a class is detected, map the algebraic support back to trace records. A cycle witness should be navigable to code paths and timestamps.

This aligns with SessionStream's observer and flight-recorder research: traces are evidence, and algebra is a projection of that evidence.

## A staged research program

1. **Manual model:** draw one context cover and define restrictions.
2. **Presheaf tests:** property-test identity and composition of restriction.
3. **Matching checker:** validate pairwise overlaps in traces.
4. **Global-section solver:** encode one finite invariant in SMT.
5. **Constant-coefficient cohomology:** detect ordinal-offset loops.
6. **Cellular sheaf:** use heterogeneous component coordinates.
7. **Runtime integration:** emit trace records with model version and context IDs.
8. **Refinement evidence:** connect concrete records to an abstract transition model.

Do not begin with a generic category-theory framework. Begin with one invariant and one trace family.

## Capstone project

Build `sessionstream-gluecheck` with two commands.

```text
sessionstream-gluecheck sections trace.json model.yaml
sessionstream-gluecheck cohomology trace.json complex.yaml
```

The first reports existence and uniqueness of global sections for snapshot-plus-suffix custody. The second reports ordinal-coordinate cocycles and supporting cycles.

A successful capstone report should contain:

- the exact model version;
- contexts and cover used;
- restriction-law test results;
- local mismatch table;
- global-section status;
- cohomology status;
- minimal or near-minimal witness trace;
- caveats about hidden coordinates and linearization.

## Exercises

**20.1 [design].** Write a YAML model for snapshot-plus-suffix completeness.

**20.2 [lab].** Implement restriction-law property tests for one presheaf.

**20.3 [lab].** Build \(D_0\) and \(D_1\) for a square with one diagonal and two faces. Verify \(D_1D_0=0\).

**20.4 [lab].** Solve exactness of an observed edge-offset vector. Return a vertex-coordinate assignment or a cycle witness.

**20.5 [research].** Compare SMT global-section search with cohomology for the same trace. Document one conflict detected by only one method.

**20.6 [capstone].** Implement the two-command checker above for a reduced SessionStream trace format.

\appendix

# Proof and Modeling Patterns

## Proving a category

To show proposed objects and arrows form a category:

1. Define domain and codomain.
2. Define which pairs compose.
3. Prove the composite is still an allowed arrow.
4. Define identities and prove they are allowed.
5. Prove left and right identity laws.
6. Prove associativity under the chosen arrow equality.

For side-effecting software, step 6 often exposes the real modeling problem. If observable traces differ by parenthesization because resource acquisition or failure handling differs, the arrows or equality are wrong for an ordinary category.

## Proving a universal property

To prove \((L,\lambda_i)\) is a limit:

1. **Cone:** verify all required triangles commute.
2. **Existence:** take an arbitrary cone \((X,x_i)\) and construct \(u:X\to L\).
3. **Factorization:** verify \(\lambda_i\circ u=x_i\) for every component.
4. **Uniqueness:** assume \(v:X\to L\) has the same factorization equations and prove \(v=u\).

Do not stop after constructing an object satisfying compatibility equations. Universality and uniqueness are the theorem.

## Uniqueness up to unique isomorphism

Suppose \((L,\lambda_i)\) and \((M,\mu_i)\) are both limits.

- Universality of \(L\) gives a unique \(f:M\to L\).
- Universality of \(M\) gives a unique \(g:L\to M\).
- Both \(f\circ g\) and \(1_L\) are arrows \(L\to L\) with the required cone factorization, so uniqueness gives \(f\circ g=1_L\).
- Similarly \(g\circ f=1_M\).

Thus \(L\cong M\), with the isomorphism uniquely compatible with the cones.

Use the same template dually for colimits.

## Proving functoriality

For a proposed functor \(F\):

1. verify source and target types of \(F(f)\);
2. verify \(F(1_A)=1_{F(A)}\);
3. verify \(F(g\circ f)=F(g)\circ F(f)\).

For restriction systems, the third law is path independence. Direct restriction and staged restriction must agree.

## Proving naturality

For \(\eta:F\Rightarrow G\), take an arbitrary arrow \(f:A\to B\) and prove

\[
G(f)\circ\eta_A
=
\eta_B\circ F(f).
\]

Read the two paths in software language. For migration:

```text
old state at A -> migrate -> new state at A -> evolve
```

must equal

```text
old state at A -> evolve -> old state at B -> migrate
```

A counterexample is usually one event or transformation that migration handles nonuniformly.

## Proving presheaf laws

For each context \(U\), define \(F(U)\). For each arrow \(V\to U\), define

\[
\rho_{U,V}:F(U)\to F(V).
\]

Then prove:

\[
\rho_{U,U}=1_{F(U)},
\]

\[
\rho_{U,W}
=
\rho_{V,W}\circ\rho_{U,V}.
\]

The second equation is the restriction equivalent of migration path independence.

## Proving the sheaf condition

For a cover \(\{U_i\to U\}\):

1. take a matching family \(s_i\in F(U_i)\);
2. construct a candidate amalgamation \(s\in F(U)\);
3. prove \(s|_{U_i}=s_i\);
4. assume \(t\) has the same restrictions;
5. prove \(t=s\).

To disprove sheafness, provide either:

- a matching family with no amalgamation;
- two distinct amalgamations with the same local restrictions.

## Computing low-dimensional cohomology

For a finite simplicial complex over a field:

1. choose orientations for edges and faces;
2. enumerate bases of \(C^0,C^1,C^2\);
3. construct matrices \(D_0,D_1\);
4. verify \(D_1D_0=0\);
5. compute \(\ker D_0\) for \(H^0\);
6. compute \(\ker D_1\) and \(\operatorname{im}D_0\);
7. obtain

\[
\dim H^1
=
\dim\ker D_1-\operatorname{rank} D_0.
\]

For one observed 1-cochain \(r\):

1. check \(D_1r=0\);
2. solve \(D_0x=r\);
3. if no solution exists, extract a dual or cycle witness.

## Model audit questions

Before trusting a categorical or cohomological result, ask:

- Which runtime distinctions were quotiented away?
- Is arrow equality observational, semantic, or byte-level?
- Are all relevant inputs explicit coordinates?
- Does the cover genuinely provide sufficient observation?
- Are higher-order joint contexts represented as faces?
- Is the coefficient system additive for a principled reason?
- Could a nonzero class be an intended degree of freedom?
- Does vanishing merely show the linear abstraction is consistent?

# Selected Exercise Hints and Solutions

## Solution to 1.2

Concatenation of words appends the symbols of one finite sequence after another. Both \((xy)z\) and \(x(yz)\) contain the symbols of \(x\), then \(y\), then \(z\), with the same indices, so they are equal.

This algebraic associativity does not prove concurrent serializability. Concurrent publication can assign or apply events in an order not represented by the chosen word, can interleave hidden effects, or can expose intermediate states. A refinement theorem must connect concrete execution to one legal word.

## Solution to 2.1

For histories:

- Reflexive: \(x\preceq x\) because \(x\epsilon=x\).
- Transitive: if \(xy=z\) and \(zw=t\), then \(x(yw)=t\), so \(x\preceq t\).
- Antisymmetric: if \(x\preceq y\) and \(y\preceq x\), their lengths satisfy \(|x|\le|y|\le|x|\), hence lengths are equal. The suffixes must be empty, so \(x=y\).

Thus prefix order is a partial order.

## Solution to 3.6

Let \(0\) and \(0'\) be initial. There is a unique \(f:0\to0'\) and unique \(g:0'\to0\). Both \(g\circ f\) and \(1_0\) are arrows \(0\to0\). Initiality says there is only one, so they are equal. Similarly \(f\circ g=1_{0'}\). Thus \(f\) and \(g\) are inverse isomorphisms.

## Solution to 4.2

In a poset category, a product is a greatest lower bound. For histories under prefix order, the product of \(x\) and \(y\) is their longest common prefix.

A coproduct is a least upper bound. It exists only when one history is a prefix of the other, because two divergent histories have no common extension as literal words. When it exists, it is the longer history.

This reveals branching: the prefix poset is generally not a lattice.

## Solution to 4.3

Let \(e:E\to A\) equalize \(f,g:A\to B\). Suppose \(e\circ u=e\circ v\) for \(u,v:X\to E\). The common arrow \(h=e\circ u=e\circ v\) equalizes \(f,g\). By the universal property, there is exactly one arrow \(X\to E\) factoring \(h\) through \(e\). Both \(u\) and \(v\) do so, hence \(u=v\). Therefore \(e\) is monic.

## Solution to 4.6

For \(P=\{(a,b):f(a)=g(b)\}\), let projections be \(p_A(a,b)=a\) and \(p_B(a,b)=b\). The square commutes by definition.

Given \(u:X\to A\) and \(v:X\to B\) with \(f\circ u=g\circ v\), define

\[
w(x)=(u(x),v(x)).
\]

The compatibility equation ensures \(w(x)\in P\). Its projections are \(u,v\). If \(w'\) has the same projections, then for every \(x\),

\[
w'(x)=(p_Aw'(x),p_Bw'(x))=(u(x),v(x))=w(x),
\]

so \(w'=w\).

## Solution to 5.4

Given a predicate \(\chi:X\to\{0,1\}\), define

\[
A_\chi=\{x:\chi(x)=1\}.
\]

Given a subset \(A\), define \(\chi_A\) in the usual way. These operations are inverse:

\[
A_{\chi_A}=A,
\qquad
\chi_{A_\chi}=\chi.
\]

## Hint for 6.2

Use observations of increasing strength.

- Client-level: normalized rendered entities only.
- Storage-level: exact entity rows, tombstones, and ordinals.
- Audit-level: event append, projector decisions, errors, and delivery attempts.

A replay can match client output while differing in audit trace because a transient projection error was retried.

## Solution to 7.4

Let \(I:X\to\{0,1\}\) and \(r:X\to P\). The invariant is parameter-determined exactly when

\[
r(x_1)=r(x_2)
\Rightarrow
I(x_1)=I(x_2).
\]

Then define \(J(p)=I(x)\) for any \(x\) with \(r(x)=p\). The condition makes this well-defined. If \(r\) is not surjective, define \(J\) arbitrarily outside its image. Then \(I=J\circ r\).

## Solution to 8.2

Assume \(h\Vdash\varphi\Rightarrow\psi\) and \(h\preceq k\). To prove \(k\Vdash\varphi\Rightarrow\psi\), take any \(l\succeq k\). Then \(l\succeq h\). If \(l\Vdash\varphi\), the implication forced at \(h\) gives \(l\Vdash\psi\). Hence the implication persists.

## Solution to 9.1

Let \(E^*\) be the free monoid and assign each generator \(e\in E\) an endomorphism \(\delta_e:S\to S\). Define

\[
F(\epsilon)=1_S,
\]

\[
F(e_1\cdots e_n)=\delta_{e_n}\circ\cdots\circ\delta_{e_1}.
\]

Then \(F(xy)=F(y)\circ F(x)\) with the chosen execution convention. Any functor extending the generator assignment must have these values because it preserves identities and composition, proving uniqueness.

## Solution to 10.3

Assume \(r:X\to P\) is surjective.

If \(I=J\circ r\), then equal parameter values imply equal invariant values immediately.

Conversely, assume the fiber criterion. For each \(p\in P\), choose any \(x_p\) with \(r(x_p)=p\) and define \(J(p)=I(x_p)\). If another representative is chosen, the fiber criterion gives the same result. Then \(J(r(x))=I(x)\).

For constructive mathematics, the choice of representatives requires care. One can instead define \(J\) by the unique common value on each inhabited fiber.

## Solution to 12.1

Prove

\[
\operatorname{fold}(S,xy)
=
\operatorname{fold}(\operatorname{fold}(S,x),y)
\]

by induction on \(y\).

Base \(y=\epsilon\): both sides are \(\operatorname{fold}(S,x)\).

Step \(y=ze\):

\[
\operatorname{fold}(S,xze)
=
\delta(\operatorname{fold}(S,xz),e)
\]

and by induction this equals

\[
\delta(\operatorname{fold}(\operatorname{fold}(S,x),z),e)
=
\operatorname{fold}(\operatorname{fold}(S,x),ze).
\]

## Solution to 14.1

A matching family is a tuple in

\[
\prod_iF(U_i)
\]

whose two restrictions to every pairwise overlap agree. Therefore it lies in the equalizer of the two maps

\[
\prod_iF(U_i)
\rightrightarrows
\prod_{i,j}F(U_i\cap U_j).
\]

The sheaf condition says restriction from \(F(U)\) gives a bijection onto this equalizer: every matching family has exactly one amalgamation.

## Solution to 15.2

Let

\[
A=\{a_1,a_2,a_3,a_4\},
\quad
B=\{b_1,b_2\},
\]

with \(f(a_1)=f(a_2)=b_1\), \(f(a_3)=f(a_4)=b_2\). Take \(P=\{a_1,a_3,a_4\}\).

Then

\[
\exists_f(P)=\{b_1,b_2\}
\]

because each fiber contains at least one member of \(P\).

But

\[
\forall_f(P)=\{b_2\}
\]

because the entire fiber over \(b_2\) lies in \(P\), while \(a_2\notin P\) blocks \(b_1\).

## Solution to 18.1

For a path with four vertices and three edges, \(D_0\) has rank 3. The complex is connected, so

\[
\dim H^0=1.
\]

There are no faces, so \(\ker D_1=C^1\) has dimension 3. Therefore

\[
\dim H^1=3-3=0.
\]

Every edge assignment is a gradient because a tree has no cycle obstruction.

## Solution to 18.2

A square cycle has four vertices and four edges, is connected, and has no faces. Thus

\[
\operatorname{rank} D_0=3,
\qquad
\dim C^1=4,
\]

so

\[
\dim H^1=4-3=1.
\]

The class is measured by total oriented circulation around the square.

## Solution to 18.3

Adding a diagonal and both triangular faces gives five edges and two independent face equations. The complex is a filled disk, so it is connected and has no first cohomology:

\[
\dim H^0=1,
\qquad
\dim H^1=0.
\]

Algebraically, \(\dim\ker D_1=3\) and \(\operatorname{rank} D_0=3\).

## Solution to 18.4

For vertex values \(x_0,x_1,x_2\), edge differences are

\[
r_{01}=x_1-x_0,
\quad
r_{02}=x_2-x_0,
\quad
r_{12}=x_2-x_1.
\]

Then

\[
r_{12}-r_{02}+r_{01}
=(x_2-x_1)-(x_2-x_0)+(x_1-x_0)=0.
\]

## Solution to 19.1

The equations are

\[
x_P=x_E,
\quad
x_S=x_P,
\quad
x_C=x_S+1,
\quad
x_E=x_C.
\]

The first two give \(x_S=x_E\). The third gives \(x_C=x_E+1\). The fourth gives \(x_E=x_E+1\), impossible. Equivalently, summing the four edge equations gives \(0=1\).

# Study Plan and Working Notebook

## A twenty-session route

| Session | Reading | Deliverable |
|---|---|---|
| 1 | Chapters 1-2 | Define two categories from your codebase. |
| 2 | Chapter 3 | Classify five arrows as monic, epic, iso, or neither. |
| 3 | Chapter 4 through equalizers | Prove one product and one equalizer universal property. |
| 4 | Rest of Chapter 4 | Draw the schema pullback and a hydration limit. |
| 5 | Chapter 5 | Represent four invariants as subobjects. |
| 6 | Chapters 6-7 | Build an invariant lattice for snapshots. |
| 7 | Chapter 8 | Build a prefix Kripke model for chat inference. |
| 8 | Chapter 9 | Model event interpretation as a functor. |
| 9 | Chapter 10 | Perform a parameter-sufficiency fiber analysis. |
| 10 | Chapter 11 | Write a many-sorted protocol signature. |
| 11 | Chapter 12 | Prove a fold invariant by induction. |
| 12 | Chapter 13 | Implement one restriction system and test its laws. |
| 13 | Chapter 14 through gluing | Specify snapshot/suffix matching conditions. |
| 14 | Rest of Chapter 14 | Design a site of sufficient observations. |
| 15 | Chapter 15 | Compute existential and universal pushforwards. |
| 16 | Chapter 16 | Audit what one adapter preserves. |
| 17 | Chapter 17 | Build an architecture nerve. |
| 18 | Chapter 18 | Compute \(H^0,H^1\) for three small complexes. |
| 19 | Chapter 19 | Model an ordinal-convention cycle. |
| 20 | Chapter 20 | Implement a reduced glue checker. |

## Notebook page template

For every new concept, fill one page with:

```text
Definition:

Diagram:

SessionStream object model:

Exact analogy, partial analogy, or non-analogy:

One law:

One counterexample:

One executable test:

One unanswered question:
```

The "non-analogy" line is important. It prevents mathematical vocabulary from becoming decorative architecture language.

## Diagram drills

Redraw from memory:

1. category composition and identities;
2. monic cancellation;
3. product universal property;
4. equalizer universal property;
5. pullback;
6. a general limit cone;
7. subobject classifier pullback;
8. naturality square;
9. presheaf restriction;
10. sheaf matching family and amalgamation;
11. adjunction hom-set correspondence;
12. an unfilled cycle and a filled triangle.

For each diagram, narrate the types of every arrow. A diagram whose arrows cannot be typed is not understood.

## Proof-writing standard

A complete proof should state:

- arbitrary objects and arrows introduced;
- why every composite is defined;
- which law or universal property is used;
- where existence is established;
- where uniqueness is established;
- what equality of arrows means.

Avoid "obvious" until you can supply the omitted equation.

# Glossary

**Adjunction.** A natural correspondence between arrows \(F(A)\to B\) and \(A\to G(B)\).

**Amalgamation.** A global section whose restrictions are a given matching family.

**Arrow.** A morphism with specified domain and codomain.

**Cartesian closed category.** A category with finite products and exponentials.

**Characteristic arrow.** The predicate \(X\to\Omega\) classifying a subobject of \(X\).

**Cocycle.** A cochain in the kernel of the next coboundary.

**Coboundary.** The alternating restriction map \(\delta^n:C^n\to C^{n+1}\).

**Cochain.** An assignment of coefficient data to simplices or overlaps of one degree.

**Cohomology.** The quotient of cocycles by coboundaries, \(H^n=\ker\delta^n/\operatorname{im}\delta^{n-1}\).

**Colimit.** A universal cocone from a diagram.

**Cone.** A compatible family of arrows from one apex object into a diagram.

**Context.** The base object over which a section is defined.

**Contravariant functor.** A functor reversing arrow direction, equivalently a functor from an opposite category.

**Coproduct.** A universal sum with injections.

**Cover.** A family declared collectively sufficient to determine data over a context.

**Epic.** Right-cancellable arrow.

**Equalizer.** Universal subobject on which two parallel arrows agree.

**Exact cochain.** A cochain in the image of the previous coboundary.

**Exponential.** Function-object \(B^A\) characterized by currying.

**Fiber.** The inverse image of one value under a map; possible global completions of local data.

**Functor.** A structure-preserving map between categories.

**Generalized element.** An arrow \(U\to X\) from an arbitrary context.

**Geometric morphism.** An adjunction between topoi whose inverse-image functor preserves finite limits.

**Global section.** A section over the largest context under consideration.

**Grothendieck topology.** A system of covering sieves satisfying maximality, pullback stability, and transitivity.

**Heyting algebra.** A bounded distributive lattice with implication right adjoint to meet.

**Image.** The smallest subobject through which an arrow factors.

**Initial object.** An object with a unique arrow to every object.

**Isomorphism.** An arrow with a two-sided inverse.

**Limit.** A universal cone into a diagram.

**Matching family.** Local sections agreeing after restriction to all overlaps.

**Monic.** Left-cancellable arrow.

**Natural transformation.** A componentwise translation between functors commuting with every source arrow.

**Nerve.** A simplicial complex encoding nonempty or relevant finite overlaps of a cover.

**Opposite category.** The category obtained by reversing every arrow.

**Power object.** An object classifying subobjects of products, usually \(\Omega^A\) in a topos.

**Presheaf.** A contravariant set-valued functor on a context category.

**Product.** A universal pairing object with projections.

**Pullback.** A limit of a cospan; the object of matching pairs over a common target.

**Pushout.** A colimit of a span; a universal merge with specified identifications.

**Restriction.** The presheaf map from sections over a larger context to a smaller one.

**Section.** A value or assignment defined over a context.

**Separated presheaf.** A presheaf in which a matching family has at most one amalgamation.

**Sheaf.** A presheaf in which every matching family has a unique amalgamation.

**Sheafification.** The universal passage from a presheaf to an associated sheaf.

**Sieve.** A precomposition-closed family of arrows into one object.

**Site.** A category equipped with a Grothendieck topology.

**Subobject.** An equivalence class of monic arrows into one object.

**Subobject classifier.** An object \(\Omega\) and `true` arrow classifying every subobject by pullback.

**Terminal object.** An object receiving a unique arrow from every object.

**Topos.** A Cartesian closed category with a subobject classifier.

**Universal property.** A characterization by unique factorization among all competing candidates.

# Source Notes and Further Reading

## Primary pedagogical source

Robert Goldblatt, *Topoi: The Categorial Analysis of Logic*, second edition with later Dover preface. The supplied EPUB was used for chapter order, definitions, conceptual progression, and exercise style. This companion cites section numbers rather than reproducing passages.

Especially important correspondences are:

- §2.3: category definition;
- §§3.1-3.16: arrow properties and universal constructions;
- §4.3: elementary topos definition;
- Chapter 8: intuitionistic logic and Kripke semantics;
- Chapter 9: functors and natural transformations;
- §14.1: presheaves, compatibility, and unique pasting;
- §§14.3-14.6: sites, geometric modality, and local truth;
- Chapter 15: adjunctions and quantifiers;
- Chapter 16: geometric morphisms and geometric logic.

## SessionStream source snapshot

Repository: `github.com/go-go-golems/sessionstream`

Commit: `d62dca9f5efa2e3094d6c62e5ead5ed0c88fd35c`

Key observations used in examples:

- `types.go`: `SessionId`, `Command`, `Event`, and `Session`;
- `projection.go`: UI and timeline projections over events and timeline views;
- `hydration.go`: snapshots, event replay, projection cursors, and error custody interfaces;
- `hub.go`: command dispatch, local publication, projection/application order, rebuild, and fanout;
- `schema.go`: named protobuf prototype registry and payload validation;
- `ordinals.go`: per-session ordinal assignment and stream-ID-derived coordinates;
- `consumer.go`: bus consumption, ordinal assignment, project/apply, and acknowledgement;
- `hydration/sqlite/store.go`: event and entity persistence, historical versions, cursors, and snapshot reads;
- `transport/ws/server.go`: hydrating/live subscription states, buffering, snapshot send, suffix flush, heartbeat, and observer dispatch;
- `examples/chatdemo/chat.go`: event generators and separate UI/timeline interpretations.

The Architecture Garden study supplied the explicit hardening laws used throughout: per-session serializability, consistent-cut snapshots, stable retry identity, atomic projection progress, deterministic replay, and snapshot-plus-suffix completeness.

## Additional mathematical references

These are optional extensions rather than sources for the chapter sequence.

- Saunders Mac Lane, *Categories for the Working Mathematician*.
- Saunders Mac Lane and Ieke Moerdijk, *Sheaves in Geometry and Logic*.
- F. William Lawvere and Stephen Schanuel, *Conceptual Mathematics*.
- David Spivak, *Category Theory for the Sciences*.
- Brendan Fong and David Spivak, *An Invitation to Applied Category Theory*.
- Justin Curry, *Sheaves, Cosheaves and Applications*.
- Robert Ghrist, *Elementary Applied Topology*.
- Samson Abramsky and Adam Brandenburger, work on sheaf-theoretic contextuality.

## Copyright and scope note

This book is a newly written study aid. It is not an edition, abridgment, or substitute for Goldblatt's text. The source book remains necessary for its historical argument, detailed logical development, and original exercise sequence. The cohomology chapters are supplemental and should not be attributed to Goldblatt.

\backmatter

# Closing Perspective {-}

The progression of ideas can now be compressed into one line:

\[
\begin{gathered}
\text{arrows}
\to
\text{universal constructions}
\to
\text{predicates and logic}\\
\to
\text{context-dependent sets}
\to
\text{local gluing}\\
\to
\text{shape and obstruction}.
\end{gathered}
\]

For SessionStream, the corresponding engineering progression is:

\[
\begin{gathered}
\text{typed events}
\to
\text{projections and cuts}
\to
\text{invariants}\\
\to
\text{partial observers}
\to
\text{snapshot-plus-suffix assembly}\\
\to
\text{diagnostics of missing global coherence}.
\end{gathered}
\]

The most productive immediate practice is not to compute cohomology. It is to define one presheaf correctly: choose contexts, write restriction maps, and test identity and composition. Then choose one cover, state the matching condition, and determine whether amalgamations exist and are unique. Once those objects are concrete, the multidimensional shapes cease to be metaphors. They become the actual combinatorics of which parts of the system can be known together.
