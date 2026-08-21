# Branch · Cohomology explanation

- URL: https://chatgpt.com/c/6a80de83-c22c-83ea-8f28-9aa6a1c256c7
- Created: 2026-08-15T21:47:48.461Z

---

> What’s cohomology

**Cohomology** is a mathematical tool for detecting and describing the “holes” and global structure of a space.

A rough intuition:

- A **0-dimensional hole** relates to disconnected pieces.
- A **1-dimensional hole** is like the hole in a circle.
- A **2-dimensional hole** is like the enclosed cavity inside a hollow sphere.

For example, a circle has one important 1-dimensional hole, while a solid disk doesn’t.

More formally, cohomology assigns groups (or vector spaces) to a space:

$$
H^0(X),\ H^1(X),\ H^2(X),\ldots
$$

These groups encode information about the space that survives stretching and bending, as long as you don’t tear or glue it.

Cohomology is closely related to **homology**, but it has extra algebraic structure: cohomology classes can be multiplied using the **cup product**. That extra structure often lets cohomology distinguish spaces that homology alone cannot.

If you want, I can explain cohomology **visually/intuitively**, starting from circles, spheres, and tori, without assuming abstract algebra.


---

> Cohomilogy of REST APIs or like, if certain parameters are enough to cover some kind of information or ensure some transactional invariant

There isn’t a standard “cohomology of REST APIs” in ordinary software engineering, but there is a mathematically precise way to use cohomological ideas for exactly the kind of question you’re describing: whether locally supplied data can be glued into a globally consistent state, and whether an invariant can be satisfied across overlapping pieces.

```json
{"system1_search_query":[{"q":"site:arxiv.org sheaf cohomology distributed systems consistency data integration"},{"q":"site:arxiv.org sheaf data consistency databases cohomology"},{"q":"site:ncatlab.org cohomology obstruction gluing local global sheaf"},{"q":"site:arxiv.org cohomology obstruction consistency distributed database"}],"response_length":"medium"}
```

<details><summary>💭 Thinking</summary>

**Searched 3 websites**

**Modeling API consistency**

I’m distinguishing two ideas: global sections can represent globally consistent parameter assignments, while higher cohomology may capture obstruction patterns. For parameter sufficiency itself, functional dependencies, schema constraints, refinement types, or formal verification are usually more direct.

**Modeled API consistency**

</details>

Yes. What you’re describing has a real mathematical analogue, but **sheaf theory / sheaf cohomology** is the more relevant formulation than ordinary topological cohomology.

A useful translation is:

> **API parameters give local information; can those local pieces be combined into a global state satisfying all system invariants?**

That is almost exactly the local-to-global problem sheaves were designed to formalize. Recent work explicitly uses sheaves this way for distributed computation and constraint-satisfaction problems. citeturn210946search1turn210946academia73

### REST API example

Suppose an order system has:

```text
POST /reserve
  orderId, sku, quantity

POST /charge
  orderId, amount, currency

POST /ship
  orderId, address
```

and globally you require

$$
\text{chargedAmount} = \text{orderTotal}
$$

$$
\text{reservedQuantity} \geq \text{orderedQuantity}
$$

$$
\text{shipped} \Rightarrow \text{paid}
$$

Each endpoint sees only part of the total state:

$$
U_R = \{\text{order},\text{inventory}\}
$$

$$
U_C = \{\text{order},\text{payment}\}
$$

$$
U_S = \{\text{order},\text{shipping}\}
$$

Think of each endpoint as producing a **local section**:

$$
s_R\in F(U_R),\quad
s_C\in F(U_C),\quad
s_S\in F(U_S).
$$

Where endpoints overlap—for example both `/reserve` and `/charge` know `orderId`, `orderVersion`, and perhaps `orderTotal`—you have restriction maps:

$$
F(U_R)\rightarrow F(U_R\cap U_C)
$$

and

$$
F(U_C)\rightarrow F(U_R\cap U_C).
$$

You ask whether they agree:

$$
s_R|_{U_R\cap U_C}
=
s_C|_{U_R\cap U_C}.
$$

Do this for all the overlaps.

The key question then becomes:

$$
\boxed{\text{Do these locally valid API states correspond to one globally valid system state?}}
$$

A **global section**

$$
s\in F(X)
$$

is precisely such a globally consistent assignment. This local-to-global interpretation is standard sheaf language. citeturn210946search11turn210946search12

And this is where cohomology becomes interesting. In suitable formulations, nontrivial cohomological classes can represent **obstructions** to obtaining a global solution from locally consistent information. This has been developed explicitly for distributed systems and constraint satisfaction. citeturn210946search10turn210946academia73

So you could imagine an API architecture having something analogous to

$$
H^0 \quad\text{= globally consistent configurations}
$$

while higher cohomological information detects certain global obstructions or degrees of inconsistency. The exact interpretation depends on how you construct the sheaf/presheaf; one shouldn't simply say “$H^1$ = API bugs” in general. In specific computational sheaf constructions, however, $H^1$ can encode independent global-consistency obstructions. citeturn210946search16

### But for “are these parameters enough?”, there is a simpler tool

If your question is specifically:

> Given parameters $P=\{p_1,\ldots,p_n\}$, are they sufficient to determine/verify invariant $I$?

then **functional dependencies, constraint satisfaction, information flow, or logic** are usually more direct than cohomology.

For example, suppose:

```text
/charge(orderId, amount)
```

must guarantee

$$
amount = price \times quantity.
$$

If you know

$$
orderId\rightarrow(price,quantity)
$$

because `orderId` uniquely determines the immutable order state, then

$$
\{orderId,amount\}
$$

contains enough information to verify the invariant.

But if prices are versioned,

$$
orderId\nrightarrow price,
$$

while

$$
(orderId,version)\rightarrow(price,quantity),
$$

then your parameter set is insufficient. You need something like

```text
orderId
orderVersion
amount
```

to establish the invariant without ambiguity.

That problem can be phrased as computing the **closure** of the supplied information:

$$
P^+
$$

under all known dependencies and asking

$$
\operatorname{Vars}(I)\subseteq P^+.
$$

That is probably the cleanest formal notion of **parameter sufficiency**.

Then sheaf/cohomological machinery becomes valuable when the problem gets distributed:

$$
\boxed{
\text{parameter sufficiency locally}
\quad+\quad
\text{compatibility across endpoints}
\quad+\quad
\text{existence of a global invariant-satisfying state}
}
$$

In other words, I think your intuition is pointing toward a potentially useful abstraction:

$$
\textbf{API surface}
\rightarrow
\textbf{cover of system state}
\rightarrow
\textbf{local constraints}
\rightarrow
\textbf{global sections / obstructions}.
$$

There is even research showing that database JOIN/data-merging problems can have genuine topological obstruction formulations, so this isn't merely a metaphor. citeturn210946academia71

If you're thinking about this as an **API design/static-analysis technique**, I can formalize a small “cohomology of an API” model—endpoints as a cover, parameters as observable coordinates, invariants as constraints, and a computable test for whether the API surface is sufficient to enforce them.


---

> Motivate and apply presheaf / sheaf to the following software I’ve been building so I can start to understand what they are and what cohomology is and bridge software engineering with some “multidimensional topological-esque shapes” intuitions I see in my head but I’m a software developer just getting into abstract maths but I know there is something there to look at more closely. Feel free to clone the repo and look more closely, you can also download the markdown of any page on parc.yolo by appending .md
>
> https://parc.yolo.scapegoat.dev/note/research/software-architecture-garden/sessionstream/readme

I’ll ground this in your actual architecture rather than give you a generic category-theory lecture. I’m going to inspect the SessionStream notes and the linked repo, then map concrete software objects in it to presheaves, sheaves, Čech-style overlap data, and eventually cohomological “obstructions.”

```json
{"open":[{"ref_id":"https://parc.yolo.scapegoat.dev/note/research/software-architecture-garden/sessionstream/readme.md"},{"ref_id":"https://parc.yolo.scapegoat.dev/note/research/software-architecture-garden/sessionstream/readme"}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Searched 1 website**

</details>

```unknown
git clone --depth 1 https://github.com/go-go-golems/sessionstream.git /mnt/data/sessionstream
```

```json
{"paths":["GitHub"],"query":"repository"}
```

<details><summary>💭 Thinking</summary>

**Cloned the sessionstream repository**

</details>

The output of this plugin was redacted.

<details><summary>💭 Thinking</summary>

**Inspected Sessionstream repository structure, projections, hydration, hub, and WebSocket schema**

</details>

One useful thing already jumps out: your notes are naturally written in “local-to-global” language even though they don’t call it that. `SessionId` partitions state into scopes, projections expose partial views, snapshots represent prefix cuts, and reconnect correctness asks whether separately obtained observations fit one coherent history. That is exactly the terrain where sheaf language becomes more than decoration.

The output of this plugin was redacted.

<details><summary>💭 Thinking</summary>

**Inspected SessionStream Hub implementation and hydration SQLite interfaces**

</details>

```json
{"system1_search_query":[{"q":"site:stacks.math.columbia.edu sheaf presheaf definition restriction maps sections open subsets"},{"q":"site:stacks.math.columbia.edu Cech cohomology sheaf cover definition"},{"q":"site:arxiv.org sheaf distributed systems consistency local global obstruction cohomology"},{"q":"site:arxiv.org cellular sheaves data fusion distributed systems consistency"}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Searched 2 websites**

</details>

The output of this plugin was redacted.

<details><summary>💭 Thinking</summary>

**Fetched WebSocket subscription handling and SQLite snapshot store implementation**

**Building the analogy**

I’m framing SessionStream as a space of observation contexts: vertices represent views, edges overlaps, and higher simplices multi-way consistency. A presheaf assigns data to each context; restriction maps compare views, while cohomology detects global gluing obstructions.

**Built the analogy**

**Expanding the model**

I’m noting that time alone forms a simple chain, so richer structure comes from combining time with projections, replicas, clients, and storage views. Their overlaps create squares, triangles, and higher-dimensional simplices where consistency can be studied.

</details>

```json
{"click":[{"ref_id":"turn861691view1","id":1}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Searching the web**

</details>

The most useful distinction for your codebase is this: **a presheaf is “all the ways I can look at or forget part of a system”; a sheaf adds a law saying compatible partial views can be assembled into one coherent whole.** Your snapshot/hydration path already contains an operational version of that gluing law, while your open atomicity/cut obligations are examples of places where the gluing law is not yet guaranteed.

The output of this plugin was redacted.

<details><summary>💭 Thinking</summary>

**Inspected local schema typing**

</details>

```json
{"open":[{"ref_id":"turn233951academia24"},{"ref_id":"turn233951academia26"},{"ref_id":"turn233951academia27"}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Searched 1 website**

</details>

Yes. There is a fairly precise mathematical object hiding behind the intuition you’re describing.

I inspected the Architecture Garden entry and the current `sessionstream` source through GitHub. Your system is an unusually good teaching example because it already revolves around **partial views of one underlying execution**: canonical events, projection state, materialized entities, snapshot cuts, projection cursors, live UI batches, and client-visible state. The Garden entry also explicitly identifies the hard parts as consistent cuts, atomic projection progress, deterministic replay, retry identity, and snapshot-plus-suffix completeness. citeturn861691view1

The bridge I would use is:

$$
\boxed{
\text{software contexts}
\longrightarrow
\text{presheaf}
\longrightarrow
\text{compatible local views}
\longrightarrow
\text{sheaf}
\longrightarrow
\text{global sections}
\longrightarrow
\text{cohomological obstructions}
}
$$

The important point is that **the “space” need not be physical space**.

---

## Start with the software meaning of a presheaf

Forget topology for a minute.

Suppose there is some complete system state $X$, but no component sees all of it.

One component sees:

$$
U=\{\text{SessionId},\text{event log},\text{event cursor}\}
$$

another sees:

$$
V=\{\text{SessionId},\text{timeline entities},\text{projection cursor}\}
$$

and another sees:

$$
W=\{\text{SessionId},\text{snapshot ordinal},\text{snapshot entities}\}.
$$

For every such context $U$, define

$$
\mathcal F(U)
=
\{\text{all locally valid states observable in context }U\}.
$$

Now suppose $V$ contains more information than some smaller context $A$. There is an obvious operation

$$
\rho^V_A:\mathcal F(V)\to\mathcal F(A)
$$

which means:

> **forget everything except what $A$ can see.**

That is a **restriction map**.

Mathematically, that is essentially the definition of a presheaf: assign some object $\mathcal F(U)$ to every context, and whenever $V\subseteq U$, provide a compatible restriction map $\mathcal F(U)\to\mathcal F(V)$. Equivalently, a presheaf is a contravariant functor from your category of contexts. citeturn233951search0turn233951search2

In software terms:

| Mathematics | Software intuition |
|---|---|
| base space / site / poset | your collection of information contexts |
| region $U$ | what some subsystem/request/transaction can observe |
| $\mathcal F(U)$ | valid states/values/traces over that context |
| section $s\in\mathcal F(U)$ | one concrete locally valid observation |
| restriction $s|_V$ | forget fields, project a view, truncate history |
| cover $U_1,\ldots,U_n$ | components/endpoints that collectively see the system |
| overlap $U_i\cap U_j$ | information both components know |
| global section | one coherent end-to-end system state/execution |
| sheaf condition | compatible partial states uniquely assemble |
| cohomology | algebraic information about failures/ambiguities of local-to-global assembly |

That table is probably the most useful Rosetta stone for you.

---

# What changes when a presheaf becomes a sheaf?

A presheaf merely says:

> I have partial views and know how to forget information.

A **sheaf** adds a very strong integration law.

Suppose

$$
U=U_1\cup U_2\cup\cdots\cup U_k
$$

and you have locally valid states

$$
s_i\in\mathcal F(U_i).
$$

Whenever two pieces overlap, require that they agree:

$$
s_i|_{U_i\cap U_j}
=
s_j|_{U_i\cap U_j}.
$$

The sheaf condition says that if all those local pieces agree on their overlaps, then there exists a **unique**

$$
s\in\mathcal F(U)
$$

whose restrictions are exactly those pieces.

That's the formal gluing axiom. citeturn233951search9

As a software developer, I would initially read:

$$
\boxed{\text{sheaf} \approx \text{lossless, unambiguous composition of compatible partial information}}
$$

This is close to a lossless JOIN intuition.

If API A tells you about `(orderId, amount)`, API B tells you about `(orderId, currency)`, and API C tells you about `(orderId, account)`, restriction means projecting down to the fields they share.

The sheaf question is:

> If all three agree wherever their data overlaps, is there exactly one globally coherent transaction they describe?

Sometimes yes.

Sometimes there are several possible global states.

Sometimes there are none.

Those distinctions are mathematically meaningful.

---

# This gives a precise formulation of your original “are these API parameters enough?” question

Let $X$ denote all semantic information that matters to an operation, and let $P\subseteq X$ denote the parameters an API call actually supplies.

There is a restriction:

$$
r_P:\mathcal F(X)\to\mathcal F(P).
$$

If the request contains payload $p\in\mathcal F(P)$, look at its **fiber**

$$
r_P^{-1}(p)
=
\{s\in\mathcal F(X)\mid s|_P=p\}.
$$

This is a very useful API-design object.

If

$$
r_P^{-1}(p)=\varnothing,
$$

the request is inconsistent: there is no possible global state corresponding to it.

If

$$
|r_P^{-1}(p)|=1,
$$

the supplied parameters uniquely determine the relevant global state.

If it contains many possibilities, the API has left something underdetermined.

And if you're interested only in invariant $I$, rather than the entire global state, then you need something slightly weaker:

$$
I(s_1)=I(s_2)
\qquad
\forall s_1,s_2\in r_P^{-1}(p).
$$

In words:

> **The parameters are sufficient to decide invariant $I$ exactly when every possible global completion of those parameters gives the same answer for $I$.**

That's already an interesting formal method for API design, before we touch cohomology.

---

# Now apply this directly to `sessionstream`

Your core types make the partial-view structure unusually visible.

An `Event` currently contains `Name`, `Payload`, `SessionId`, and `Ordinal`; a `Session` contains its identity and metadata. fileciteturn2file0L2

Meanwhile a timeline projection sees

$$
(\text{event},\text{session},\text{TimelineView})
$$

and emits `TimelineEntity` values; a UI projection sees the same sort of pre-event context and emits `UIEvent`s. fileciteturn3file0L2

And hydration introduces another family of views:

$$
\text{Snapshot}
=
(\text{SessionId},\text{SnapshotOrdinal},\text{Entities}).
$$

The store separately exposes event cursors, projection cursors, snapshots, event replay, and materialized state. fileciteturn7file0L2

So don't imagine one state object.

Imagine a family of overlapping coordinate charts on an execution.

---

## A useful “space” for SessionStream

I would define an observation context roughly as

$$
C=(s,n,K),
$$

where

- $s$ is a session,
- $n$ is an event-prefix/cut coordinate,
- $K$ says which kinds of information are visible.

For example $K$ might contain some subset of

$$
\{
E,T,S,U,C
\}
$$

where

$$
E=\text{canonical event history},
$$

$$
T=\text{timeline/materialization},
$$

$$
S=\text{snapshot},
$$

$$
U=\text{live UI stream},
$$

$$
C=\text{client-observed state}.
$$

Then there are two very natural kinds of restriction maps.

You can **forget an observation dimension**:

$$
(s,n,\{E,T,S\})
\rightarrow
(s,n,\{T,S\}),
$$

or you can **move backward in time**:

$$
(s,n,K)\rightarrow(s,m,K),
\qquad m\le n.
$$

That gives you something richer than a line.

You have approximately

$$
\text{session}
\times
\text{event time}
\times
\text{observer/context}.
$$

This is where the “multidimensional shape” intuition starts becoming legitimate.

---

# The topological-looking shape is the pattern of overlaps

Here's a toy architecture complex, not a claim that this is the uniquely correct model:

```text
             Timeline
             T
            / \
           /   \
          E     S
   Event  |     |  Snapshot
          |     |
          U-----C
       Live UI  Client
```

Think of the vertices as information contexts.

An edge means:

> These two contexts have some common semantic information whose agreement matters.

For example:

$$
E\leftrightarrow T
$$

shares session/prefix/projection-progress information.

$$
T\leftrightarrow S
$$

shares materialized entities and their cut.

$$
S\leftrightarrow C
$$

shares the snapshot delivered to the client.

$$
E\leftrightarrow U
$$

shares the canonical event ordinal associated with projected UI output.

$$
U\leftrightarrow C
$$

shares live observations.

Now the shape has a loop.

That loop is already a 1-dimensional topological feature.

If three contexts can be jointly observed/validated, you add a filled triangle. Four-way joint contexts produce tetrahedron-like simplices, and so forth.

So:

> **Dimension here means order of simultaneous compatibility, not physical dimension.**

A vertex represents one local context.

An edge represents pairwise compatibility.

A triangle represents a genuine three-way compatibility witness.

A tetrahedron represents four-way compatibility.

That is probably close to the multidimensional object you've been intuiting.

There is contemporary distributed-systems work doing essentially this: representing local knowledge/indistinguishability with cellular structures, attaching sheaf data to them, and characterizing valid distributed solutions as global sections. citeturn701652view0

---

# You already implemented something very close to sheaf gluing

The strongest example is your **snapshot-before-live** protocol.

Your Garden note describes a snapshot at ordinal $n$ as a representation of the prefix

$$
e_1e_2\cdots e_n
$$

with live delivery supplying the suffix strictly after the cut. Reconnect correctness therefore has the form

$$
\operatorname{fold}
(S_n,e_{n+1}\cdots e_m)
=
S_m.
$$

citeturn861691view1

Your current WebSocket implementation registers the subscription as hydrating *before* loading the snapshot, buffers concurrent UI batches, sends the snapshot, drains the buffered data relative to its `SnapshotOrdinal`, then transitions to live delivery. fileciteturn9file0L2

Conceptually you have two local sections:

$$
s_{\mathrm{past}}
\in
\mathcal F(U_{\mathrm{snapshot}})
$$

and

$$
s_{\mathrm{future}}
\in
\mathcal F(U_{\mathrm{live}}).
$$

Their common boundary information is the cut $n$.

The gluing conditions include:

$$
\text{same SessionId},
$$

$$
\operatorname{ordinal}(\text{live batch})>n,
$$

correct suffix ordering, and no event being silently neither represented by the snapshot nor delivered in the suffix.

If those conditions hold, you form

$$
s_{\mathrm{client}}
=
s_{\mathrm{past}}
\cup
s_{\mathrm{future}}.
$$

That is almost the sheaf axiom written as a network protocol.

The hydration buffer is acting as your **gluing mechanism**.

Its overflow/error path is also conceptually revealing: instead of pretending there is a valid global section, you explicitly fail the attempted construction.

---

# And some of your open correctness obligations are failures to guarantee gluing

This is where the abstraction starts paying rent.

## Atomic projection progress

Current `projectAndApply` does roughly:

```text
AppendEvent
    ↓
read View
    ↓
UIProjection
TimelineProjection
    ↓
Apply entities
    ↓
AdvanceProjectionCursor
    ↓
fanout UI
```

Those operations are separate persistence/effect boundaries in the current implementation. fileciteturn6file0L2

Your Garden note already calls out the desired invariant: a projection checkpoint at $n$ should mean that every event through $n$ has the promised materialization, and no later state is being claimed as part of that prefix. citeturn861691view1

The sheaf reading is:

$$
\mathcal F(E)
=
\text{event-store facts},
$$

$$
\mathcal F(T)
=
\text{materialization facts},
$$

$$
\mathcal F(P)
=
\text{projection-progress facts}.
$$

Each might contain a perfectly valid local observation.

But consider:

```text
event log:          n
materialization:    n
projection cursor:  n-1
```

Perhaps `Apply` committed and `AdvanceProjectionCursor` failed.

Locally, none of those values is malformed.

But they don't form the **global committed section** your stronger transactional semantics wants.

That is exactly a local-to-global consistency problem.

A SQL transaction spanning `Apply + cursor advance`, or a recovery protocol representing the intermediate state explicitly, changes the topology of what the software can jointly witness: you create a stronger context in which those facts are observed/committed together.

---

# The consistent-snapshot problem is an even cleaner example

Your SQLite `Snapshot` currently obtains the snapshot cursor and then queries the entity rows separately. fileciteturn10file0L2

The Garden entry therefore states the desired law

$$
\operatorname{LastEventOrdinal}(x)
\le
\operatorname{SnapshotOrdinal}
$$

for every returned entity, and notes that a read transaction should bind the cut and entity set into one coherent database snapshot if concurrent mutation is allowed. citeturn861691view1

Think about the two local sections:

$$
s_C=\text{“snapshot cut is }n\text{”}
$$

and

$$
s_E=\text{“these are the entity rows”}.
$$

Suppose a concurrent update occurs between the two reads and you get:

$$
\text{SnapshotOrdinal}=42
$$

while one entity says

$$
\text{LastEventOrdinal}=43.
$$

Both reads were locally legitimate.

There is simply **no global section representing “the state at cut 42”** that restricts to both observations.

That's almost the cleanest possible software-engineering example of what “doesn't glue” means.

---

# Retry identity exposes a different presheaf problem: missing coordinates

Your `Event` currently contains:

$$
(\text{Name},\text{Payload},\text{SessionId},\text{Ordinal})
$$

but no independent stable logical event identifier. fileciteturn2file0L2

The Garden analysis consequently identifies stable redelivery identity as incomplete: reuse of the same `(SessionId, Ordinal)` is idempotent in the event store, but a redelivery that acquires a fresh ordinal can look like a new event. citeturn861691view1

The sheaf interpretation is subtle and useful:

> This isn't primarily “nontrivial cohomology.” Your coordinate system is under-specified.

Two contexts:

```text
first delivery
retry delivery
```

may correspond to the same semantic event, but nothing in the common restriction forces them to be identified.

You probably need another coordinate such as

$$
\text{EventId}
$$

or

$$
(\text{producer},\text{stable message id})
$$

if logical redelivery identity is part of the invariant.

This is an important lesson:

> **Not every local-to-global problem is a cohomology problem. Sometimes your presheaf simply forgot a coordinate.**

---

# Deterministic replay has the same flavor

Your projection interface gets an event, session and `TimelineView`. fileciteturn3file0L2

But ordinary Go code implementing that interface could additionally consult clocks, randomness, network state, mutable globals, or other implicit inputs.

Your Garden entry explicitly identifies this: deterministic replay requires every relevant input to be represented—initial view, metadata, schema version, event prefix, and any otherwise hidden dependencies. citeturn861691view1

Suppose you believed the global section was indexed by

$$
(\text{events},\text{initial state}).
$$

But the projector secretly uses `time.Now()`.

You haven't discovered a mysterious topological hole.

You've discovered that the actual base has another coordinate:

$$
\text{wall-clock observation}.
$$

Either include it,

or, much better for event sourcing, turn the relevant observation into canonical event data.

This is a nice way to use presheaf thinking during architecture reviews:

> **If two supposedly identical local sections restrict differently downstream, ask what hidden coordinate you forgot.**

---

# Now we can finally talk about cohomology

For ordinary sheaf cohomology you normally want algebraic values—abelian groups, vector spaces, modules, etc.—rather than arbitrary Go objects.

Given a cover

$$
\mathcal U=\{U_i\},
$$

Čech cohomology constructs objects in dimensions:

$$
C^0
=
\prod_i\mathcal F(U_i),
$$

$$
C^1
=
\prod_{i,j}\mathcal F(U_i\cap U_j),
$$

$$
C^2
=
\prod_{i,j,k}
\mathcal F(U_i\cap U_j\cap U_k),
$$

and so on. citeturn121511search1turn121511search3

For a 0-cochain

$$
s=(s_i),
$$

the coboundary tells you the disagreements on overlaps:

$$
(\delta s)_{ij}
=
s_j|_{U_i\cap U_j}
-
s_i|_{U_i\cap U_j}.
$$

If

$$
\delta s=0,
$$

all local pieces agree.

So $H^0$ is the first familiar thing:

$$
H^0
\approx
\text{compatible global sections}.
$$

Indeed, ordinary sheaf notation identifies $H^0(U,\mathcal F)$ with global sections over $U$. citeturn233951search0

Then the magical-looking expression is

$$
H^1
=
\frac{\ker\delta_1}{\operatorname{im}\delta_0}.
$$

Read it as:

> **patterns of overlap discrepancy which satisfy all local higher-order consistency conditions, modulo discrepancies that can be explained away just by changing the local descriptions.**

That's where the “holes” intuition comes from.

---

# A software engineer's $H^1$ example

Take our toy SessionStream loop:

```text
EventStore → Timeline → Snapshot → Client → LiveUI → EventStore
```

Suppose every component has its own revision coordinate $x_i\in\mathbb Z$.

On every edge, record the claimed offset:

$$
r_{ij}=x_j-x_i.
$$

The collection of local coordinates $x_i$ is a **0-cochain**.

The edge offsets $r_{ij}$ are a **1-cochain**.

If those offsets actually come from globally meaningful local coordinates, then going around a loop must give

$$
r_{ET}
+r_{TS}
+r_{SC}
+r_{CU}
+r_{UE}
=
0.
$$

Because everything telescopes:

$$
(x_T-x_E)
+(x_S-x_T)
+(x_C-x_S)
+(x_U-x_C)
+(x_E-x_U)
=0.
$$

Now imagine your contracts instead imply

$$
r_{ET}
+r_{TS}
+r_{SC}
+r_{CU}
+r_{UE}
=1.
$$

Every individual edge contract might appear reasonable.

But globally you've accumulated an unremovable off-by-one around the loop.

There is no assignment of local coordinates $x_i$ that realizes all those edge relations simultaneously.

That persistent circulation is the kind of object $H^1$ captures.

For a simple cycle graph with constant coefficients, there's one independent 1-dimensional hole, corresponding precisely to one independent circulation around that loop.

---

## This is surprisingly relevant to your ordinal vocabulary

Your Garden entry repeatedly warns that these are not automatically identical notions:

```text
event-store cursor
projection checkpoint
snapshot cut
live suffix coordinate
entity last-event ordinal
```

citeturn861691view1

Suppose one adapter interprets its cursor as:

> last included event

and another interprets its cursor as:

> next event to consume.

They're shifted by one.

Locally every implementation may look correct.

After composing enough adapters, you may return to the original semantic coordinate shifted by $+1$.

That's an almost literal “holonomy around an architecture loop” intuition.

The fix might be a bug fix.

But sometimes the math tells you something deeper:

> You tried to pretend five different coordinate systems were the same coordinate.

Then the right solution is to type them separately and make the transformations explicit.

Which is remarkably close to the vocabulary discipline already present in your notes.

---

# Here is the topological intuition I think you're reaching for

Imagine that components only know pairwise overlaps:

```text
A ----- B
|       |
|       |
D ----- C
```

The boundary forms a loop.

There is no context anywhere in the system that sees all four things jointly.

So locally you can walk around checking:

```text
A agrees with B
B agrees with C
C agrees with D
D agrees with A
```

while still lacking one globally coherent witness.

The inside of the square is missing.

Now add a transaction/coordinator/context that jointly observes enough facts to validate the entire combination.

Mathematically, you've done something like **filling the hole with a higher-dimensional cell**.

That is why transactional boundaries and higher-order invariants fit your geometric intuition surprisingly well:

$$
\boxed{
\text{pairwise contracts form edges;}
\quad
\text{joint atomic contracts create faces.}
}
$$

This should not be interpreted too literally as “database transactions are 2-cells.” But as a modeling discipline, it is powerful.

A “hole” becomes:

> **a boundary of local compatibility for which your architecture provides no higher-order global witness.**

---

# The important caveat about cohomology

Your actual constraints include things like

$$
\text{LastEventOrdinal}\le\text{SnapshotOrdinal},
$$

idempotence, tombstones, ordering, uniqueness, cancellation, schema validity, and temporal behavior.

Those aren't naturally all linear equations in abelian groups.

So I would **not** begin by trying to calculate $H^1(\text{SessionStream})$.

Begin with a **set-valued presheaf of valid configurations**.

This is essentially a constraint-satisfaction perspective:

$$
\mathcal F(U)
=
\{\text{assignments on }U\text{ satisfying all constraints visible in }U\}.
$$

Global correctness becomes existence of a global section.

There is research making exactly this connection: CSPs can be represented as global-section problems for presheaves, with Čech-cohomological methods used to detect certain global obstructions that ordinary propagation of local consistency misses. citeturn818658view1

Then linearize particular diagnostics when useful.

For example:

$$
\text{cursor offsets},
\quad
\text{parities},
\quad
\text{counts},
\quad
\text{conservation laws},
\quad
\text{version deltas}
$$

can naturally live in $\mathbb Z$, $\mathbb F_2$, or vector spaces.

That's where actual matrix-computable cohomology becomes attractive.

And one should keep the logical direction straight: in many sheaf-theoretic obstruction constructions, a nonzero cohomology class witnesses impossibility, but vanishing need not prove that everything is globally consistent. Abramsky et al.'s contextuality construction explicitly has that sufficient-but-not-necessary character. citeturn818658view2

---

# What I would build inside `sessionstream` as a first experiment

Not production machinery. A research instrument alongside your existing formal/spec work.

1. **Define an architecture complex.** Start with cells corresponding to `EventStore`, `TimelineProjection`, `Snapshot`, `UIFanout`, and `Client`. Define explicitly what information each cell can observe and which overlaps exist. Then introduce session and ordinal/cut as coordinates.

2. **Define a set-valued presheaf first.** A section might contain facts such as `EventCursor`, `ProjectionCursor`, `SnapshotOrdinal`, maximum entity `LastEventOrdinal`, event-prefix digest, materialization digest, live batch ordinals, and a client reconstruction digest. Restriction just discards facts not visible to the smaller context.

3. **Feed real traces into it and test gluing.** Your observer/refinement work already thinks in terms of recorded traces and executable laws. Turn a recorded session into local sections and ask whether the sections agree on every overlap and whether a global execution witness exists. This would make “doesn't glue” an actual diagnostic rather than just category-theory language. Your Garden entry already treats transition traces and refinement evidence as first-class verification artifacts. citeturn861691view1

4. **Only then add a small cellular/Čech cohomology experiment.** Start with something intentionally linear, such as revision-offset consistency. Construct the incidence/coboundary matrices for your architecture complex and calculate $H^0$ and $H^1$. If a cycle carries an irreducible cursor offset, emit both the offending cohomology class and the architectural loop supporting it.

The particularly interesting combination with SessionStream is:

$$
\text{runtime trace}
\rightarrow
\text{local sections}
\rightarrow
\text{restriction checks}
\rightarrow
\text{global-section search}
\rightarrow
\text{cohomological diagnostic}.
$$

That could genuinely become a useful research tool rather than mathematics painted onto software.

---

## The deepest conceptual shift

You initially encounter topology as:

> circle has a hole, sphere has a cavity, torus has loops.

Sheaf theory changes what the “points” can mean.

Your points can be **information contexts**.

Your edges can mean **these contexts overlap**.

Your triangles can mean **three observations can be jointly reconciled**.

Your sections are **possible values living over those contexts**.

Then topology stops being about whether your software “looks like a doughnut.”

It becomes about the **shape of who knows what together**.

And cohomology starts asking whether information can circulate through that shape and return with a discrepancy that no local correction can eliminate.

For `sessionstream`, I would summarize the picture as:

$$
\boxed{
\begin{array}{c}
\text{event history is your temporal coordinate}\\
\text{projections/transports/stores are overlapping observers}\\
\text{restriction means forgetting/truncating information}\\
\text{snapshot + suffix is a gluing problem}\\
\text{transactional correctness is global-section correctness}\\
\text{missing parameters are missing coordinates}\\
\text{higher-order incompatibilities can sometimes become cohomological obstructions}
\end{array}
}
$$

The most important thing is that **sheaves are already useful before cohomology**. I would spend some time getting comfortable with “context → sections → restrictions → compatible family → global section.” Once that feels natural in SessionStream, the definition

$$
H^1=\ker\delta_1/\operatorname{im}\delta_0
$$

stops looking like arbitrary algebra and starts looking like a way of measuring the architectural loops that local reasoning can't eliminate.


---

> Use the attached book which I’m currently working through (I’m at the limits part of chapter 3) as a source of pedagogy, definitions, exercises, and write my “custom version” that is grounded in sessionstream in particular, software engineering at large, to make a custom textbook for me to work through all this theory and be able to study my mental intuitions. 
>
> Anchor it strongly in the sessionstream study. We don’t need to cover the material of goldblatt, just the relevant parts that will make this a strong book to work through to strengthen sheaf / presheaf / topos approach to software engineering 
>
> As markdown and pdf

I’ll build a self-contained SessionStream-centered study text, adapting Goldblatt’s pedagogy and terminology, with broader software-engineering connections, exercises and solutions, exported as Markdown and PDF.

<details><summary>💭 Thinking</summary>

**Assessing the project**

I’m preparing a transformative textbook grounded in the supplied EPUB and repository materials. I’ll inspect the available files, follow document-to-PDF requirements, and avoid reproducing the source verbatim.

**Assessed the project**

</details>

```unknown
bash -lc cat /home/oai/skills/pdfs/SKILL.md && printf '\n---FILES---\n' && ls -lh /mnt/data && printf '\n---REPO---\n' && find /mnt/data/sessionstream -maxdepth 2 -type f | head -100
```

<details><summary>💭 Thinking</summary>

**Inspected PDF requirements and EPUB structure, contents, and pedagogy**

</details>

```json
{"open":[{"ref_id":"https://parc.yolo.scapegoat.dev/note/research/software-architecture-garden/sessionstream/readme.md"}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Searching github.com**

**Searched GitHub and installed repositories for SessionStream**

</details>

```unknown
bash -lc git clone --depth 1 https://github.com/go-go-golems/sessionstream.git /mnt/data/sessionstream && cd /mnt/data/sessionstream && git rev-parse HEAD && find . -maxdepth 3 -type f | sort | sed -n '1,240p'
```

<details><summary>💭 Thinking</summary>

**Cloned the Sessionstream repository**

**Fetched and inspected SessionStream repository files and archive**

</details>

```json
{"open":[{"ref_id":"https://github.com/go-go-golems/sessionstream/archive/refs/heads/main.zip"}],"response_length":"short"}
```

<details><summary>💭 Thinking</summary>

**Searching the web**

**Gathering source material**

I’m locating the requested book and repository content, then I’ll map the ideas into an original, student-friendly textbook structure with exercises, examples, and a clean PDF-ready layout.

**Gathered source material**

</details>

```json
{"search_query":[{"q":"site:parc.yolo.scapegoat.dev/note/research/software-architecture-garden/sessionstream/readme \"SessionStream\""},{"q":"\"Architecture Garden\" \"SessionStream\""},{"q":"\"SnapshotOrdinal\" \"sessionstream\""},{"q":"\"projection cursor\" \"sessionstream\""}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Searched 1 website**

**Shaping the textbook**

I’m organizing the material around arrows, universal properties, functors, natural transformations, presheaves, sheaves, cohomology, and software-engineering applications, with exercises and project work throughout.

**Shaped the textbook**

**Structuring the study path**

I’m starting from limits and building toward presheaves, sheaves, topoi, adjunctions, and internal logic. I’ll keep SessionStream central, using software examples, exercises, intuitions, and projects to reinforce each idea.

**Building the study sequence**

I’m grounding the book in limits and universal properties, then connecting SessionStream’s projections, ordinals, snapshots, hydration, and live fanout to presheaves, sheaves, topoi, and cohomological diagnostics.

**Structured and built the study sequence**

</details>

I’ll use one recurring execution trace throughout, connecting limits to sheaf gluing through snapshot cuts, projection checkpoints, and overlapping observer views.

<details><summary>💭 Thinking</summary>

**Reviewed SessionStream architecture, hydration, ordinal, hub, and projection implementations**

**Reviewed SQLite sessions, WebSocket server, and subscription implementations**

</details>

```unknown
bash -lc ls -lah /mnt/data | sed -n '1,120p'; echo '---'; find /mnt/data/_topoi_epub/OEBPS/Text -maxdepth 1 -type f | sort | sed -n '1,60p'; echo '--- tools'; command -v pandoc || true; command -v xelatex || true; command -v lualatex || true; command -v pdftoppm || true; command -v pdfinfo || true; command -v dot || true; command -v weasyprint || true
```

<details><summary>💭 Thinking</summary>

**Inspected EPUB sources, chapter structure, metadata, and PDF tooling requirements**

</details>

```unknown
bash -lc mkdir -p /mnt/data/sessionstream_sheaves_textbook && cat > /mnt/data/sessionstream_sheaves_textbook/00-frontmatter.md <<'EOF'
---
title: "Sections Over Streams"
subtitle: "A SessionStream-First Introduction to Presheaves, Sheaves, Topos Thinking, and Cohomology for Software Engineers"
author: "Custom study edition"
date: "2026-08-15"
lang: en-US
documentclass: book
classoption:
  - openany
papersize: letter
fontsize: 10.5pt
geometry:
  - margin=0.9in
mainfont: "TeX Gyre Pagella"
sansfont: "Noto Sans"
monofont: "DejaVu Sans Mono"
monofontoptions:
  - Scale=0.86
colorlinks: true
linkcolor: "MidnightBlue"
urlcolor: "MidnightBlue"
toccolor: "black"
header-includes:
  - |
    ```{=latex}
    \usepackage{microtype}
    \usepackage{booktabs}
    \usepackage{longtable}
    \usepackage{array}
    \usepackage{enumitem}
    \usepackage{xcolor}
    \usepackage{mathtools}
    \usepackage{amssymb}
    \usepackage{fancyhdr}
    \usepackage[most]{tcolorbox}
    \definecolor{SSBlue}{HTML}{214761}
    \definecolor{SSGold}{HTML}{A97816}
    \definecolor{SSLight}{HTML}{F3F6F8}
    \definecolor{SSWarn}{HTML}{FFF5DE}
    \newtcolorbox{mentalmodel}{breakable,colback=SSLight,colframe=SSBlue,title=Mental model,fonttitle=\bfseries}
    \newtcolorbox{sessionstudy}{breakable,colback=SSWarn,colframe=SSGold,title=SessionStream study,fonttitle=\bfseries}
    \newtcolorbox{definitionbox}{breakable,colback=white,colframe=SSBlue,title=Definition,fonttitle=\bfseries}
    \newtcolorbox{cautionbox}{breakable,colback=white,colframe=black!55,title=Modeling caution,fonttitle=\bfseries}
    \pagestyle{fancy}
    \fancyhf{}
    \fancyhead[LE,RO]{\small\thepage}
    \fancyhead[LO]{\small\nouppercase{\rightmark}}
    \fancyhead[RE]{\small\nouppercase{\leftmark}}
    \setlength{\headheight}{14pt}
    \setlist{nosep}
    \setcounter{tocdepth}{2}
    \setcounter{secnumdepth}{3}
    ```
---

\frontmatter

# Preface {-}

This book is written for one reader: a software developer who is already building SessionStream, is working through Robert Goldblatt's *Topoi: The Categorial Analysis of Logic*, has reached the discussion of limits in Chapter 3, and suspects that software architectures have a genuine local-to-global geometry.

That suspicion is worth developing carefully. It can lead to useful mathematics, but only if several ideas that are often blended together are kept distinct:

1. A **category** records objects, transformations, and composition.
2. A **limit** is a universal coherent assembly of a diagram.
3. A **presheaf** assigns data to observation contexts and supplies restriction maps.
4. A **sheaf** says compatible local data can be glued uniquely.
5. A **topos** is a category in which context-indexed sets and predicates support a rich internal logic.
6. **Cohomology** extracts algebraic invariants from a local-to-global system; it is not a synonym for inconsistency.

The standing case study is SessionStream: a Go framework in which commands produce canonical backend events, projections derive live UI events and durable timeline entities, stores maintain event and projection cursors, and reconnecting clients receive a snapshot before future live events. The framework naturally exposes many partial views of one execution. That makes it a better teaching object than the usual disconnected examples involving weather measurements or functions on open intervals.

## Pedagogical source and method {-}

Goldblatt's book supplies the pedagogical model, not text to be reproduced. Its most important lesson for this project is methodological: begin with concrete constructions, translate their internal descriptions into arrow-based external characterizations, and only then state the abstract definition. This book follows that progression.

Definitions here are standard but paraphrased. Exercises are original and designed around SessionStream and software architecture. The selected route through Goldblatt is:

- Chapter 3: universal properties, products, equalizers, pullbacks, and limits;
- Chapter 4: subobjects, classifiers, bundles, sheaves, and topoi;
- Chapter 9: functors, natural transformations, and functor categories;
- Chapter 14: sites, sheaves, and local truth;
- Chapter 15: adjunctions;
- Chapter 16: geometric morphisms.

Goldblatt does not provide the applied cohomology course developed here. Those chapters use standard Cech and cellular intuitions, specialized to architecture diagrams and trace data.

## Source snapshot {-}

The software discussion is anchored to the `go-go-golems/sessionstream` repository as inspected on August 15, 2026, with the repository search reporting commit `d62dca9f5efa2e3094d6c62e5ead5ed0c88fd35c` on `main`. The book refers especially to:

- `pkg/sessionstream/types.go`;
- `pkg/sessionstream/projection.go`;
- `pkg/sessionstream/hydration.go`;
- `pkg/sessionstream/hub.go`;
- `pkg/sessionstream/ordinals.go`;
- `pkg/sessionstream/hydration/sqlite/store.go`;
- `pkg/sessionstream/transport/ws/server.go`;
- `proto/sessionstream/v1/transport.proto`;
- the SessionStream Architecture Garden study at `parc.yolo.scapegoat.dev`.

The implementation will evolve. Treat concrete code references as a dated laboratory specimen and the mathematical models as hypotheses to test, not permanent descriptions of the project.

## How to use this book {-}

Do not read it as continuous prose alone. Keep three artifacts beside it:

1. a **diagram notebook**, in which every definition is redrawn using SessionStream objects;
2. a **model ledger**, in which you record exactly what each object, arrow, context, cover, section, and coefficient group means;
3. a **counterexample file**, containing cases where an attractive analogy fails.

Each chapter has four exercise modes:

- **Translate**: restate mathematics in software terms and back again.
- **Prove**: establish a small mathematical fact.
- **Model**: make explicit choices for SessionStream.
- **Build**: write code or executable tests.

Attempt the exercises before consulting Appendix B. A correct model with explicit assumptions is more valuable than a sophisticated model whose objects and arrows are ambiguous.

## A standing discipline {-}

Throughout the book, ask six questions whenever a new construction appears:

1. What are the objects?
2. What are the arrows?
3. What does equality of arrows mean?
4. What information does a restriction forget?
5. Which families count as covers?
6. What concrete fact would a global section certify?

Most category-theoretic confusion in software comes from answering only the first question.

## Copyright and transformation note {-}

This is a new, transformative study text. It uses the attached Goldblatt volume as a guide to sequencing, terminology, and pedagogical style. It does not reproduce the book's chapters or exercise sets. Short code excerpts and type signatures from SessionStream are used for analysis under the repository's licensing terms; paths are provided so the evolving source remains authoritative.

\newpage

# Roadmap {-}

The book is organized as a sequence of enlarging viewpoints.

| Part | Central question | SessionStream anchor |
|---|---|---|
| I. Limits and architecture | What is a coherent assembly? | event, view, entity, cursor, snapshot |
| II. Presheaves and sheaves | How do partial observations restrict and glue? | snapshot-before-live, replay, context covers |
| III. Topos thinking | What logic lives inside contextual data? | local invariants, schema predicates, failure evidence |
| IV. Cohomology | What loop-shaped obstruction survives local re-description? | ordinal offsets and architecture cycles |
| V. Applied method | How can the theory become a verification instrument? | trace-to-section harness and capstone model |

A reasonable sixteen-week route is:

| Weeks | Chapters | Output |
|---|---|---|
| 1-3 | 1-4 | precise limit/pullback model of one SessionStream invariant |
| 4-6 | 5-9 | a presheaf and sheaf specification |
| 7-9 | 10-13 | a site, nerve, and presheaf-topos interpretation |
| 10-12 | 14-17 | local logic and change-of-context model |
| 13-14 | 18-21 | computable cohomology laboratory |
| 15-16 | 22-24 | verification prototype and research memo |

\mainmatter
EOF

cat > /mnt/data/sessionstream_sheaves_textbook/01-part-i.md <<'EOF'
# Limits and the Shape of an Execution

## One Execution, Many Views

### 1.1 The system you are actually studying

SessionStream is not merely an event bus with WebSockets. It is a machine for maintaining several related descriptions of one session-scoped computation.

A simplified execution is:

```text
Client command
      |
      v
     Hub ---> Command handler
                  |
                  v
          canonical backend event
             /             \
            v               v
     UI projection    Timeline projection
            |               |
            v               v
      live UI batch    durable entities
            |               |
            v               v
        subscribers    hydration store
             \             /
              \           /
               reconnecting client
```

The canonical event is one description. The timeline entity state is another. The live UI stream is another. A snapshot is another. A projection cursor is a claim about how far one derived description has incorporated the canonical history.

A developer often asks whether all these representations are *consistent*. That word hides several different questions:

- Do they carry the same `SessionId`?
- Do their ordinal conventions agree?
- Does the snapshot represent exactly the prefix it claims?
- Does the live suffix start strictly after that prefix?
- Could the same canonical event produce a different timeline after replay?
- Can two separately valid records coexist in one global execution?

The last question is the gateway to sheaf theory.

### 1.2 Local does not mean geographically local

In this book, a **local view** is a view available under a restricted context. The restriction may come from:

- a service boundary;
- an API parameter list;
- a database transaction boundary;
- a time prefix;
- a projection type;
- a replica;
- a schema version;
- a user authorization scope;
- an observer that records only selected fields.

A context is local because it sees less than the whole semantic situation, not because it runs on another machine.

For example, the current core types include:

```go
type Event struct {
    Name      string
    Payload   proto.Message
    SessionId SessionId
    Ordinal   uint64
}

type TimelineEntity struct {
    Kind             string
    Id               string
    CreatedOrdinal   uint64
    LastEventOrdinal uint64
    Payload          proto.Message
    Tombstone        bool
}

type Snapshot struct {
    SessionId       SessionId
    SnapshotOrdinal uint64
    Entities        []TimelineEntity
}
```

These types overlap semantically but are not copies of one another. `Event` and `Snapshot` share a session and an ordering interpretation. `TimelineEntity` and `Snapshot` share the claim that an entity's represented history lies at or before a cut. The live UI frame and a backend event share the event ordinal that produced the frame.

### 1.3 The first geometric intuition

Draw each observation context as a patch. Draw an overlap when two contexts can speak about a common fact.

```text
             Timeline state
               /       \
              /         \
       Event log ------- Snapshot
          |                 |
          |                 |
       Live UI ---------- Client state
```

This picture is not yet a topological space. It is a declaration of **joint observability**. An edge means that two views have a comparison map or common boundary. A filled triangle would mean that a three-way comparison is available as a single coherent witness, not merely as three pairwise checks.

That distinction matters. Pairwise agreement does not automatically supply a jointly atomic observation. A database transaction, an integration test, or a trace record containing several facts can act like a higher-dimensional witness that fills a boundary.

\begin{mentalmodel}
The topological-looking shape belongs to the pattern of information overlap. Vertices are contexts. Edges are pairwise overlaps. Higher-dimensional simplices represent genuine multiway overlap or joint validation. A hole is a boundary of comparisons for which no higher-order witness has been supplied.
\end{mentalmodel}

### 1.4 State space versus observation space

There are two spaces to keep separate.

The **state space** contains possible complete executions or system states. It may be enormous and highly structured.

The **observation space** contains contexts from which those executions are partially observed. Sheaf theory is commonly organized over the observation space. A sheaf assigns possible observations to each context and explains how to restrict richer observations to poorer ones.

This distinction immediately clarifies API parameter sufficiency. Suppose a complete semantic state is in a set `Global`, and an endpoint exposes parameters in `Params`. The endpoint gives a map

\[
r : \mathrm{Global} \longrightarrow \mathrm{Params}.
\]

For a supplied request \(p\), the possible completions are the fiber

\[
r^{-1}(p)=\{x\in\mathrm{Global}\mid r(x)=p\}.
\]

The parameters determine the complete state exactly when this fiber has one element. They determine an invariant \(I\) when \(I\) has the same value on every element of the fiber. Sheaf language generalizes this from one endpoint to many overlapping contexts.

### 1.5 Four standing SessionStream problems

The book will repeatedly revisit four cases.

**Projection atomicity.** In `Hub.projectAndApply`, event append, projection, entity application, projection-cursor advancement, and fanout occur as distinct steps. A failure between steps can leave locally meaningful records whose joint meaning is disputed.

**Snapshot consistency.** A snapshot cut and its entity rows must describe one common read. The invariant

\[
\mathrm{LastEventOrdinal}(e)\leq \mathrm{SnapshotOrdinal}
\]

is necessary, but the stronger question is whether the whole entity set is the state at that cut.

**Snapshot-plus-live gluing.** A reconnecting client must receive a prefix representation and then every relevant live event after the cut, with no gap or duplicate under the chosen semantics.

**Identity under retry.** `(SessionId, Ordinal)` can identify a persisted position, but a redelivered logical event may acquire a new ordinal. If logical identity matters, a missing `EventId` is a missing coordinate, not a cohomological mystery.

### Exercises

**1.1 Translate.** List five distinct meanings of “local” in software. For each, state what a restriction map would forget.

**1.2 Model.** Draw an overlap graph containing `EventStore`, `TimelineProjection`, `HydrationStore`, `WebSocketServer`, and `BrowserClient`. Label every edge with the exact fields or facts both endpoints can compare.

**1.3 Counterexample.** Construct two snapshots that both satisfy every entity-wise ordinal inequality but cannot both be outputs of one deterministic replay semantics.

**1.4 Build.** Add a trace type to a toy event system that records event ordinal, projection cursor, snapshot ordinal, and entity maximum ordinal at one instant. Explain which existing boundaries prevent the trace from being truly atomic.

**1.5 Reflection.** In your model ledger, write one paragraph distinguishing the global state space from the observation-context space.

\newpage

## Arrows Before Fields

### 2.1 Externalizing a software property

Goldblatt's Chapter 3 begins by replacing element-based definitions with arrow-based ones. That move is valuable in software because an implementation's internal fields are often inaccessible, unstable, or irrelevant. A contract should be characterized by how the component composes with other components.

A category \(\mathcal C\) consists of:

- objects \(A,B,C,\ldots\);
- arrows \(f:A\to B\);
- an identity arrow \(1_A:A\to A\) for each object;
- composition \(g\circ f:A\to C\) when \(f:A\to B\) and \(g:B\to C\);
- associativity and identity laws.

For software, possible categories include:

- Go types and total pure functions;
- schemas and migrations;
- event prefixes and truncation maps;
- system states and deterministic transitions;
- contexts and information-forgetting maps;
- services and protocol-preserving adapters.

Not every collection of components forms a useful category. Partial functions, exceptions, concurrency, effects, and versioning must be modeled rather than silently ignored.

### 2.2 Commutativity is implementation independence

A diagram commutes when every directed path with the same start and end denotes the same arrow.

Suppose `Encode` turns a typed event into wire data, `Decode` reverses that representation, and `Project` derives a timeline entity. A desired square might be

\[
\begin{array}{ccc}
\mathrm{TypedEvent} & \xrightarrow{\mathrm{Encode}} & \mathrm{WireEvent}\\
\downarrow{\mathrm{Project}} & & \downarrow{\mathrm{DecodeProject}}\\
\mathrm{Entity} & \xrightarrow{\mathrm{EncodeEntity}} & \mathrm{WireEntity}.
\end{array}
\]

Commutativity says that projecting before serialization and projecting after decoding have equivalent observable outcomes. This is stronger than “both paths usually work.” It states an equation between composed behaviors.

A commutative diagram is therefore a compact test specification. Property-based tests often approximate a diagram by generating inputs and checking that two paths agree.

### 2.3 Monomorphisms, epimorphisms, and isomorphisms

An arrow \(m:A\to B\) is **monic** when it is left-cancellable:

\[
m\circ g=m\circ h \implies g=h.
\]

In `Set`, this is equivalent to injectivity. In software, a monic encoding does not erase distinctions relevant to the modeled category. A typed protobuf encoding may be monic relative to semantic messages if decoding recovers them uniquely. A logging formatter usually is not.

An arrow \(e:A\to B\) is **epic** when it is right-cancellable:

\[
g\circ e=h\circ e \implies g=h.
\]

In `Set`, this is surjectivity. In other categories, the element-level intuition can fail. This is a warning against identifying categorical words with implementation-level set functions without proving the correspondence.

An arrow \(f:A\to B\) is an **isomorphism** when there is an inverse \(f^{-1}:B\to A\) satisfying

\[
f^{-1}f=1_A,\qquad ff^{-1}=1_B.
\]

Two representations can be isomorphic without being equal. JSON and protobuf messages may be isomorphic under a restricted schema and canonical encoding policy, while their bytes and operational costs differ.

### 2.4 A category of prefixes

Fix one session whose canonical event history is

\[
H_n=(e_1,\ldots,e_n).
\]

Construct a category \(\mathbf{Prefix}_s\):

- objects are prefixes \(H_n\);
- there is one arrow \(H_m\to H_n\) when \(n\le m\), interpreted as truncation;
- composition is repeated truncation.

This is a poset category: there is at most one arrow between objects. Every arrow in a poset category is both monic and epic, but generally not an isomorphism. That fact is a useful antidote to over-reading mono/epi as data injectivity/surjectivity in arbitrary categories.

The direction of arrows is a modeling choice. We point from richer history to poorer history because later presheaf restriction maps will literally truncate.

### 2.5 A category of observations

Now construct a category whose objects are observation interfaces:

```text
FullExecution
EventHistory
TimelineView
Snapshot
LiveUITrace
ClientReconstruction
```

An arrow means “deterministically forget or derive the target observation from the source.” For example:

\[
\mathrm{FullExecution}\to\mathrm{EventHistory}
\]

forgets derived views, while

\[
\mathrm{FullExecution}\to\mathrm{ClientReconstruction}
\]

models the observable client result.

Be cautious: a projection from event history to timeline state is only an arrow if it is actually a function in your category. Hidden clocks, randomness, external calls, mutable configuration, or nondeterministic map iteration can make the apparent arrow ill-defined.

\begin{cautionbox}
Category theory does not make an operation deterministic. It forces you to decide whether determinism is part of the equality notion for arrows. If the same input can yield observably different outputs, either enrich the input object with the missing coordinates or work in a category designed for effects or relations.
\end{cautionbox}

### Exercises

**2.1 Prove.** Show that every isomorphism is both monic and epic.

**2.2 Prove.** Show that every arrow in a poset category is monic and epic.

**2.3 Model.** Define equality of arrows for two SessionStream timeline projections. Is equality byte-for-byte protobuf equality, semantic entity equality, equality after sorting, or equality only after client rendering?

**2.4 Translate.** Give one SessionStream example of an arrow that appears injective at the Go-value level but is not monic under your chosen observational equivalence.

**2.5 Build.** Write a property test for one commutative square involving event encoding, decoding, and projection.

\newpage

## Universal Properties and Limits

### 3.1 Why limits arrive before sheaves

A sheaf's global section is a coherent assembly of local pieces. Limits are the categorical language of coherent assemblies. Understanding limits first prevents the sheaf axiom from looking like unrelated topology.

Goldblatt's route is particularly effective: study products and equalizers, notice their shared pattern, and then abstract the notion of a limiting cone.

### 3.2 Products: one thing with two projections

A product of objects \(A\) and \(B\) is an object \(A\times B\) with projections

\[
\pi_A:A\times B\to A,
\qquad
\pi_B:A\times B\to B,
\]

such that for every pair of arrows \(f:X\to A\), \(g:X\to B\), there is exactly one arrow

\[
\langle f,g\rangle:X\to A\times B
\]

with

\[
\pi_A\langle f,g\rangle=f,
\qquad
\pi_B\langle f,g\rangle=g.
\]

The product is not defined as a struct with two fields. It is defined by what every pair of observations can do through it.

In a category of record schemas and total field projections, a Go struct may realize a product. In a category with validation dependencies, effects, privacy constraints, or independently versioned fields, the naive struct may not have the universal property.

### 3.3 Equalizers: the universal agreement object

Given parallel arrows

\[
f,g:A\rightrightarrows B,
\]

an equalizer is an arrow \(e:E\to A\) satisfying \(fe=ge\), universal among arrows with that property. In `Set`,

\[
E=\{a\in A\mid f(a)=g(a)\}.
\]

A software equalizer can represent:

- inputs on which two implementations agree;
- traces for which a replayed state equals the persisted state;
- schemas accepted by two validators;
- requests whose calculated and supplied totals agree.

The equalizer does not merely report equality. It forms the largest subobject on which equality holds.

### 3.4 Cones and limits

A diagram \(D:J\to\mathcal C\) is a category-shaped arrangement of objects and arrows. A cone from \(X\) to \(D\) is a family of arrows from \(X\) to every object in the diagram, compatible with every diagram arrow.

A **limit** of \(D\) is a universal cone: every other cone factors through it uniquely.

\[
\begin{array}{ccccc}
& X & & \\
& \downarrow{\exists!} & \searrow & \\
& L & \longrightarrow & D(j) & \\
& \downarrow & & \downarrow & \\
& D(k) & \longrightarrow & D(\ell). &
\end{array}
\]

In `Set`, the limit can be understood as the set of all tuples of local values satisfying every compatibility equation imposed by the diagram.

That sentence is one of the main bridges in this book:

\begin{mentalmodel}
A limit is the space of globally compatible assignments to a diagram of partial views. A global section of a presheaf or sheaf will later be another instance of this idea.
\end{mentalmodel}

### 3.5 A SessionStream compatibility diagram

Consider the following objects for a fixed session:

- \(E\): persisted event history;
- \(P\): projection-progress record;
- \(T\): durable timeline state;
- \(S\): snapshot payload.

Each has a map to an ordinal interpretation \(O\):

\[
\mathrm{eventCursor}:E\to O,
\quad
\mathrm{projectionCursor}:P\to O,
\quad
\mathrm{timelineCut}:T\to O,
\quad
\mathrm{snapshotCut}:S\to O.
\]

A raw product \(E\times P\times T\times S\) contains every tuple, including incoherent ones. The desired object is closer to a limit that retains only tuples satisfying the diagram's equations and inequalities.

For example, a strict model may require

\[
\mathrm{projectionCursor}(p)=\mathrm{timelineCut}(t)
\]

and

\[
\mathrm{snapshotCut}(s)=\mathrm{timelineCut}(t).
\]

If the model permits projection lag, replace equality with an explicit lag relation object rather than silently weakening the diagram.

### 3.6 Limits as contract synthesis

Suppose three subsystems publish contracts:

1. the event store guarantees a unique event at each `(SessionId, Ordinal)`;
2. the timeline store guarantees every entity version records `LastEventOrdinal`;
3. the WebSocket layer guarantees live frames are labeled by producing event ordinal.

The limit question asks:

> What is the universal object whose values are complete observations satisfying all three contracts and all comparison arrows between them?

This viewpoint can expose a missing contract. If there is no arrow relating `SnapshotOrdinal` to the maximum represented entity version, the diagram has not encoded snapshot consistency. The resulting limit may contain states you intended to exclude.

### 3.7 Uniqueness up to isomorphism

A limit is unique up to unique isomorphism, not necessarily literal identity. This matters in software architecture. An in-memory aggregate and a normalized SQLite representation can both realize the same universal contract while differing internally.

Instead of asking whether two implementations use identical structures, ask whether they are isomorphic in the category whose arrows preserve the required behavior. This shifts the discussion from representation preference to observable law.

### Exercises

**3.1 Translate.** Describe a product, equalizer, terminal object, and general limit using API-contract language without mentioning sets or elements.

**3.2 Prove.** Show that the equalizer arrow is monic.

**3.3 Model.** Define a diagram whose limit consists of SessionStream snapshots satisfying `LastEventOrdinal <= SnapshotOrdinal`. Make inequalities into explicit relation objects or predicates; do not write them only in prose.

**3.4 Counterexample.** Give a category of software components in which a pair-like struct fails to be a categorical product.

**3.5 Build.** Write a function that enumerates the finite limit of a small diagram represented as finite sets and functions. Test it on event records, entity records, and shared ordinals.

**3.6 Reflection.** Explain why “the database is the source of truth” does not by itself define a terminal object, limit, or global section.

\newpage

## Pullbacks and Consistent Cuts

### 4.1 The central finite limit

A pullback begins with arrows sharing a codomain:

\[
f:A\to C,
\qquad
g:B\to C.
\]

Their pullback is an object \(P\) with arrows to \(A\) and \(B\):

\[
\begin{array}{ccc}
P & \xrightarrow{p_B} & B\\
\downarrow{p_A} & & \downarrow{g}\\
A & \xrightarrow{f} & C,
\end{array}
\]

such that the square commutes and is universal among commuting squares.

In `Set`,

\[
P=\{(a,b)\in A\times B\mid f(a)=g(b)\}.
\]

This is a join constrained by agreement over a shared key or interpretation.

### 4.2 Pullbacks are typed joins

A database join can resemble a pullback, but the categorical statement includes a universal property. The pullback is not just any query result satisfying a predicate. Every other compatible pair must map uniquely into it.

For software design, this suggests a three-step discipline:

1. identify the shared semantic object \(C\);
2. define both interpretation maps into \(C\);
3. form or validate the object of pairs that agree there.

For SessionStream, \(C\) may be:

- session identity;
- canonical event ordinal;
- schema version;
- projection semantics version;
- snapshot cut;
- logical event identity.

A common error is joining over a field whose name is shared but whose semantics are not. `event cursor`, `projection cursor`, `snapshot ordinal`, and `next expected ordinal` should not all be mapped to one undifferentiated `uint64` object without explicit conversion arrows.

### 4.3 Snapshot entities over a cut

Let \(E\) be all entity versions and \(O\) the ordinal set. Each version has a `LastEventOrdinal` map

\[
\ell:E\to O.
\]

Let \(C\) be candidate snapshot cuts with identity map \(c:C\to O\). Exact-cut versions form a pullback of \(\ell\) and \(c\). Versions at or before a cut require an order relation

\[
R_{\leq}\subseteq O\times O.
\]

The valid pairs are then a pullback against the relation:

\[
V=\{(e,n)\mid \ell(e)\le n\}.
\]

This is already more precise than a boolean check because it identifies the valid *object of pairs* and the projections back to entities and cuts.

### 4.4 A transaction can supply a missing face

The SQLite store's `Apply` method updates entity versions, current entities, and the session snapshot ordinal within one database transaction. This gives a joint witness for those writes.

The `Snapshot` path, by contrast, first obtains the cursor and then queries entity rows. Whether this denotes one coherent read depends on database connection and transaction semantics. A read transaction can make the pair

\[
(\text{cut},\text{entity set})
\]

a jointly observed value rather than two observations made at different instants.

Geometrically, imagine separate edges certifying pairwise facts:

```text
cut -------- session
 |              |
 |              |
entities ----- store state
```

A transaction does not literally create a topological 2-cell. It does create a stronger observation context that can witness the whole square under one database snapshot. That is the precise software content behind the “fill the face” intuition.

### 4.5 Projection progress as a pullback obligation

The current Hub sequence includes:

```text
AppendEvent
Get current View
UIProjection.Project
TimelineProjection.Project
HydrationStore.Apply
AdvanceProjectionCursor
PublishUI
```

Suppose materialization and projection progress are separate durable writes. Define:

\[
m:T\to O
\]

as the maximum timeline ordinal represented by durable state, and

\[
p:P\to O
\]

as the stored projection cursor. The strict committed-state object is the pullback

\[
T\times_O P.
\]

If `Apply` commits and cursor advancement fails, the system may inhabit the product \(T\times P\) but not this pullback. The state is locally representable in each store table but does not satisfy the intended global equation.

There are several legitimate responses:

- make both updates one transaction;
- treat the intermediate state as explicit protocol state;
- define the cursor as lower bound rather than exact equality;
- make replay idempotent and repairable;
- record a richer progress lattice.

Category theory does not choose the semantics. It forces the semantics into arrows and universal objects.

### 4.6 Pullback stability

Pullbacks let properties be transported along maps. In set language, inverse image is a pullback. In software, a predicate or authorization scope can be pulled back along an adapter.

If `AuthorizedSession` is a subobject of session identifiers and a command has a map to its session, the accepted command object is the inverse image of authorized sessions along that map. This is a categorical way to say “validate the command by the session it refers to.”

Pullback stability will later matter twice:

- a Grothendieck coverage must remain valid after changing context;
- the inverse-image part of a geometric morphism must preserve finite limits.

### Exercises

**4.1 Prove.** Show that a pullback in `Set` has the universal property stated above.

**4.2 Translate.** Express an SQL inner join over a shared session ID as a pullback. State the additional assumptions needed for it to be a categorical pullback in your chosen category.

**4.3 Model.** Draw separate objects for `LastIncludedOrdinal` and `NextExpectedOrdinal`, with conversion arrows. Rebuild the snapshot/live diagram without conflating them.

**4.4 Model.** Specify the pullback object representing a timeline state and projection cursor that agree under your intended semantics. Include lag or failure states if they are valid.

**4.5 Build.** Write a concurrency test that tries to observe a snapshot cut and entities from different moments. Then change the read path to use an explicit transaction and state what property the test approximates.

**4.6 Counterexample.** Show why matching on `SessionId` alone is insufficient to glue a snapshot and a live suffix.

\newpage

## Functors, Naturality, and Replay

### 5.1 Structure-preserving translation

A functor \(F:\mathcal C\to\mathcal D\) maps objects to objects and arrows to arrows while preserving identities and composition:

\[
F(1_A)=1_{F(A)},
\qquad
F(g\circ f)=F(g)\circ F(f).
\]

A functor is not merely a function between type names. It translates an entire compositional world.

The most important SessionStream candidates are:

- replay from event prefixes to timeline states;
- projection from backend-event contexts to UI-event contexts;
- serialization from typed messages to wire representations;
- reindexing from one architecture's context category to another;
- forgetting details from rich traces to public observer records.

### 5.2 Replay as a functor

Let \(\mathbf{Prefix}_s\) have event prefixes as objects and truncations as arrows. Let \(\mathbf{Timeline}_s\) have timeline states indexed by cuts, with restriction arrows that recover the state at an earlier cut.

A replay semantics is a functor

\[
R:\mathbf{Prefix}_s\to\mathbf{Timeline}_s
\]

when:

1. each event prefix has a determined timeline state;
2. replaying the unchanged prefix changes nothing;
3. replay respects truncation and composition.

The third requirement can be pictured as

\[
\begin{array}{ccc}
H_m & \xrightarrow{\mathrm{truncate}_{m,n}} & H_n\\
\downarrow{R_m} & & \downarrow{R_n}\\
T_m & \xrightarrow{\mathrm{restrict}_{m,n}} & T_n.
\end{array}
\]

If a projection reads `time.Now()`, random values, mutable process state, or unrecorded network data, then \(R(H_n)\) is not determined by \(H_n\). The apparent functor is missing input coordinates.

A repair is to enrich the source object:

\[
H_n'=(H_n,\text{schema version},\text{configuration},\text{external observations}).
\]

Event sourcing's standard advice—record the facts needed for deterministic replay—can be read as “make the proposed arrow well-defined.”

### 5.3 Natural transformations compare whole implementations

Given functors \(F,G:\mathcal C\to\mathcal D\), a natural transformation

\[
\eta:F\Rightarrow G
\]

provides an arrow \(\eta_A:F(A)\to G(A)\) for every object \(A\), such that for every \(f:A\to B\),

\[
G(f)\circ\eta_A=\eta_B\circ F(f).
\]

Naturality means the comparison commutes with every supported change of context.

Suppose \(F\) is an in-memory projection implementation and \(G\) is a SQLite-backed one. A family of one-off converters between their states is not enough. A natural comparison must also respect prefix truncation, session selection, schema migration, or whichever arrows exist in the source category.

This is a stronger refactoring criterion:

> The migration agrees at each context and remains coherent as contexts are restricted.

### 5.4 Projections as natural operations

The current projection interface accepts an event, session, and current `TimelineView`:

```go
type TimelineProjection interface {
    Project(
        ctx context.Context,
        ev Event,
        sess *Session,
        view TimelineView,
    ) ([]TimelineEntity, error)
}
```

To model this categorically, decide whether `Project` is:

- an ordinary function on a product object;
- a natural transformation between presheaves of event-plus-view contexts and entity-update contexts;
- a Kleisli arrow carrying errors or effects;
- a relation if multiple outputs are permitted.

The second formulation becomes useful when the same projection must behave coherently under restriction to earlier cuts, narrower authorization scopes, or reduced schemas.

### 5.5 A naturality test pattern

For a restriction \(r:U\to V\), a natural operation \(\eta:F\Rightarrow G\) must satisfy

\[
G(r)(\eta_U(x))=\eta_V(F(r)(x)).
\]

Read the two paths:

1. process the rich input, then restrict the output;
2. restrict the input, then process the poor input.

A property-based test can generate \(x\in F(U)\) and compare the results. Failures often reveal hidden dependencies, noncanonical ordering, or a restriction map that discards information the operation actually needs.

### 5.6 Functor categories foreshadow topoi

For a small category \(\mathcal C\), the category

\[
\mathbf{Set}^{\mathcal C^{op}}
\]

has presheaves as objects and natural transformations as arrows. This is not only a collection of presheaves. It is itself a category with products, limits, exponentials, and a subobject classifier: a presheaf topos.

That statement will later let us treat context-indexed software data as living in its own mathematical universe.

### Exercises

**5.1 Prove.** Verify that prefix truncation defines a category and that a deterministic fold defines a functor under explicit assumptions.

**5.2 Model.** List every hidden input that could make a SessionStream timeline projection nondeterministic. Decide which should become event data, configuration-version data, or prohibited effects.

**5.3 Translate.** Describe a natural transformation between two serializers or two hydration stores. State the source category whose arrows naturality must respect.

**5.4 Build.** Implement a naturality property test for replay under prefix restriction.

**5.5 Counterexample.** Give component-wise conversions between two implementations that fail to be natural.

**5.6 Reflection.** Why is “same output on current production examples” weaker than natural equivalence?
EOF
```

I’m drafting from limits forward: products, equalizers, and pullbacks become compatibility machinery, leading naturally to presheaves, sheaf gluing, internal logic, and finally cohomology.

<details><summary>💭 Thinking</summary>

**Created SessionStream textbook frontmatter and companion chapters 6–12**

</details>

```unknown
bash -lc cat > /mnt/data/sessionstream_sheaves_textbook/03-part-iii.md <<'EOF'
# Topos Thinking for Contextual Software

## The Presheaf Topos as a Software Universe

### 13.1 From one presheaf to a category of presheaves

Fix a small context category \(\mathcal C\). Presheaves on \(\mathcal C\) form a category

\[
\widehat{\mathcal C}=\mathbf{Set}^{\mathcal C^{op}}.
\]

Its objects are presheaves. Its arrows are natural transformations. Composition and identities are defined context by context.

This category is a **topos**. Informally, it behaves enough like `Set` to support:

- finite limits;
- exponentials, or internal function objects;
- a subobject classifier \(\Omega\);
- an internal higher-order intuitionistic logic.

The remarkable point is that the “sets” in this universe vary by context.

### 13.2 Context-indexed types

A conventional type has one collection of values. A presheaf type \(F\) has a collection \(F(U)\) at every context \(U\), plus restriction maps.

Examples:

- `Events(U)`: event histories observable under \(U\);
- `Timeline(U)`: timeline states meaningful under \(U\);
- `Snapshot(U)`: snapshots valid under \(U\);
- `Evidence(U)`: evidence records available under \(U\);
- `Command(U)`: commands authorized and schema-valid under \(U\).

A natural transformation is a context-polymorphic program. It runs at every context and commutes with restriction.

This is close to a type system in which values carry scope, version, cut, or capability indices, but the indices form a category rather than merely a set.

### 13.3 Limits are computed pointwise

Products and other limits in a presheaf category are computed context by context. For presheaves \(F\) and \(G\),

\[
(F\times G)(U)=F(U)\times G(U).
\]

Restrictions act componentwise.

Equalizers are also pointwise:

\[
\mathrm{Eq}(\alpha,\beta)(U)
=
\{x\in F(U)\mid \alpha_U(x)=\beta_U(x)\}.
\]

This makes invariant types easy to express. The presheaf of states on which replayed and persisted timeline views agree is an equalizer subpresheaf, provided agreement is stable under restriction.

### 13.4 Exponentials are contextual programs

In `Set`, \(B^A\) is the set of functions \(A\to B\). In a presheaf topos, the exponential \(G^F\) is more subtle. A section of \(G^F\) over \(U\) describes an operation from \(F\) to \(G\) that works naturally under every refinement into \(U\).

One useful formula is

\[
(G^F)(U)
\cong
\mathrm{Nat}(yU\times F,G).
\]

So a contextual function at \(U\) is a natural transformation that accepts both a probe into \(U\) and an \(F\)-value.

Software reading:

> A function available under context \(U\) must continue to behave coherently after any permitted restriction of \(U\).

This is stronger than storing a Go closure in each context independently.

### 13.5 Why this is a topos rather than a library pattern

A library can implement context-indexed data. A topos supplies laws connecting data types, predicates, quantifiers, and function spaces.

For example, within \(\widehat{\mathcal C}\):

- an invariant is a subobject \(P\hookrightarrow X\);
- its truth value is a map \(X\to\Omega\);
- conjunction is a finite-limit construction;
- implication is an internal exponential-like operation on subobjects;
- existential quantification can arise as an adjoint to substitution under suitable structure.

This gives a unified language for data and logic. The value for software engineering is not that production code should be “implemented in a topos.” The value is that context-sensitive contracts can be modeled in a universe where restriction and local truth are first-class.

### 13.6 SessionStream objects in a presheaf topos

Choose a base \(\mathcal C_{SS}\) with session, cut, observer, schema, and authorization contexts. Candidate presheaves include:

\[
\mathsf{Ev},\mathsf{Tl},\mathsf{Snap},\mathsf{UI},\mathsf{Trace},\mathsf{Err}.
\]

Candidate natural transformations include:

\[
\mathsf{Replay}:\mathsf{Ev}\to\mathsf{Tl},
\]

\[
\mathsf{Hydrate}:\mathsf{Tl}\to\mathsf{Snap},
\]

\[
\mathsf{UIProject}:\mathsf{Ev}\times\mathsf{Tl}\to\mathsf{UI},
\]

and restriction-preserving schema encoders.

The global-section object \(\Gamma(F)=F(1)\), when the base has an appropriate terminal context, retrieves values visible at the global context. More generally, global sections are natural transformations from the terminal presheaf to \(F\).

### 13.7 Global sections as programs with no unresolved context

The terminal presheaf \(1\) assigns a singleton to every context. A global section of \(F\) is a natural transformation

\[
1\to F.
\]

It chooses a section \(s_U\in F(U)\) at every context, all compatible with restriction.

This is stronger than choosing one state at a “largest” object when the base has no such object. It is a coherent family across all contexts.

In a SessionStream trace model, a global section may assign:

- an event prefix to every cut;
- a timeline state to every corresponding view;
- a snapshot to every snapshot context;
- compatible client reconstructions to every subscription context.

That is an entire coherent execution, not one database row.

### 13.8 The topos is relative to the base

Change \(\mathcal C\), and the presheaf topos changes. A base containing only time prefixes has different truth values and global sections from a base containing time, replicas, and authorization scopes.

Therefore “the SessionStream topos” is not a canonical object waiting to be discovered. There are candidate topoi, each expressing a particular observational theory.

### Exercises

**13.1 Translate.** Describe an object and arrow in \(\widehat{\mathcal C}_{SS}\) in Go-interface language.

**13.2 Prove.** Verify that pointwise products satisfy the categorical product universal property in a presheaf category.

**13.3 Model.** Define the terminal presheaf on a finite SessionStream context category. Describe a global section of your event-history presheaf.

**13.4 Build.** Implement pointwise products and equalizers in your finite-presheaf checker.

**13.5 Reflection.** State one reason a context-indexed Go generic type is weaker than a presheaf object with natural transformations.

\newpage

## Subobjects, Classifiers, and Invariant Predicates

### 14.1 Invariants as subobjects

A subobject of \(X\) is represented by a monomorphism

\[
m:P\hookrightarrow X.
\]

In `Set`, this is essentially a subset. In a presheaf category, it is a **subpresheaf**: for every context \(U\), a subset

\[
P(U)\subseteq X(U)
\]

that is closed under restriction.

Thus an invariant is not merely a predicate on global states. It is a family of context-wise predicates stable under forgetting information.

Example:

\[
\mathsf{OrdinalSafe}(U)
=
\{x\in\mathsf{Trace}(U)
\mid
\text{every visible entity ordinal is at most the visible snapshot cut}\}.
\]

If this property can become false after restriction, it does not define a subpresheaf under the chosen restriction semantics. That failure reveals a mismatch between predicate and context orientation.

### 14.2 The subobject classifier in `Set`

In `Set`, the two-element set

\[
\Omega=\{\bot,\top\}
\]

classifies subsets. Every inclusion \(P\hookrightarrow X\) has a characteristic function

\[
\chi_P:X\to\Omega
\]

with \(\chi_P(x)=\top\) exactly when \(x\in P\).

The inclusion \(\{\top\}\hookrightarrow\Omega\) is universal: every subobject is its pullback along a unique characteristic map.

This turns predicates into arrows.

### 14.3 The presheaf truth-value object

In a presheaf topos, \(\Omega(U)\) is generally not two-valued. Its elements are **sieves on \(U\)**.

A sieve records the refinements or probes under which a proposition is verified, and it is closed under further precomposition. Therefore a predicate's truth value can say:

> This claim is supported under exactly these stable refinements of the current context.

This is richer than `true`, `false`, or `unknown`. It records the shape of supporting evidence.

### 14.4 A snapshot-safety truth value

Let \(x\in\mathsf{SnapshotCandidate}(U)\). Its characteristic value

\[
\chi_{\mathsf{Safe}}(x)\in\Omega(U)
\]

is the sieve of arrows \(r:V\to U\) for which the restricted candidate \(x|_V\) is known to lie in the safety subpresheaf.

Possible refinements might include:

- a context that observes the cut and entities in one read transaction;
- a context that compares against deterministic replay;
- a context that includes all entity version ordinals;
- a context that merely sees `SessionId`, which may be insufficient.

The truth value therefore exposes *how* safety is established.

### 14.5 Validity must be restriction-stable

Suppose the rich context shows that a snapshot is unsafe because one entity has ordinal 43 while the snapshot cut is 42. If restriction forgets entity ordinals, should the resulting poor section belong to `Safe`?

There are two different predicates:

- **actually safe**, a property of the underlying complete state;
- **verified safe from this context**, an epistemic property of available evidence.

For a presheaf of observations, the second is often better modeled by a sieve-valued truth judgment. Simply declaring the poor observation safe because no violation is visible confuses absence of evidence with evidence of absence.

### 14.6 Schema validation as a subobject

Let \(X(U)\) be wire payloads observable under schema context \(U\). Let \(P(U)\) be those that decode to the registered concrete protobuf descriptor and satisfy local validation.

The inclusion

\[
P\hookrightarrow X
\]

models schema-valid payloads. The SessionStream policy rejecting top-level `google.protobuf.Struct` can be modeled as an additional subobject constraint: accepted registrations lie in the subpresheaf of named concrete message schemas.

This makes policy composition visible. “Decodes,” “matches event name,” “uses concrete schema,” and “passes semantic validation” can be separate subobjects combined by pullback/intersection.

### 14.7 Safety and liveness

Subobjects naturally model safety properties: states or traces that avoid forbidden configurations.

Liveness properties such as “every accepted command eventually emits a terminal event” concern infinite or temporal behavior. They may require:

- presheaves over intervals or traces;
- modalities;
- coalgebraic structure;
- temporal logic internal to a suitable topos;
- coverage that treats future extensions as refinements.

Do not force every liveness property into a subset of instantaneous states.

### 14.8 Classifying an invariant is a design achievement

To turn a prose invariant into a characteristic arrow, you must specify:

- its state object \(X\);
- its valid subobject \(P\);
- restriction stability;
- the truth-value interpretation;
- the contexts under which it is decidable.

That process is already useful even if no categorical theorem is applied.

### Exercises

**14.1 Prove.** Show that the intersection of two subpresheaves is a subpresheaf and is their pullback over the ambient presheaf.

**14.2 Model.** Define a subpresheaf of projection states in which materialization and projection cursor agree. State what happens in an error-recovery context.

**14.3 Model.** Distinguish “safe” from “verified safe” for snapshots. Give each a mathematical home.

**14.4 Build.** Extend your finite-presheaf tool with subpresheaves and characteristic sieve computation.

**14.5 Reflection.** Identify a SessionStream liveness property that cannot be represented faithfully as a predicate on one instantaneous snapshot.

\newpage

## Local Truth and Internal Logic

### 15.1 Truth at a context

In sheaf and presheaf semantics, propositions are evaluated relative to contexts. Write

\[
U\Vdash\varphi
\]

for “\(\varphi\) is forced at context \(U\).”

The exact clauses depend on the site and internal language, but the guiding principle is locality and stability under restriction.

For a simple atomic predicate \(P(x)\),

\[
U\Vdash P(x)
\]

means the section \(x\) lies in the corresponding subobject at \(U\).

### 15.2 Conjunction and implication

Conjunction behaves as expected:

\[
U\Vdash\varphi\wedge\psi
\]

when both propositions hold at \(U\).

Implication is contextual. Roughly,

\[
U\Vdash\varphi\Rightarrow\psi
\]

when for every refinement \(V\to U\), if \(V\Vdash\varphi\) then \(V\Vdash\psi\).

An API contract “if a client is authorized, then a snapshot is redacted correctly” must survive every permitted restriction or refinement of the current context, not only the present sample.

### 15.3 Negation is durable refutation

Negation is implication into falsity:

\[
\neg\varphi=(\varphi\Rightarrow\bot).
\]

Thus \(U\Vdash\neg\varphi\) means no refinement of \(U\) can establish \(\varphi\).

This is much stronger than “\(\varphi\) is not currently known.” Consequently, excluded middle

\[
\varphi\vee\neg\varphi
\]

need not hold at every context.

For distributed software, this distinction is natural. Lack of a matching pong does not imply that a peer has crashed. A later or richer context may reveal scheduler delay, queue delay, or a delayed pong.

### 15.4 Disjunction and local witnesses

In sheaf semantics, disjunction may be local. Roughly, \(U\Vdash\varphi\vee\psi\) when \(U\) can be covered by contexts on each of which one disjunct holds.

Likewise, existential truth may have local witnesses that differ across a cover:

\[
U\Vdash\exists x\,\varphi(x)
\]

when a cover of \(U\) supplies local witnesses satisfying \(\varphi\), compatible as required by the semantics.

This is unfamiliar if truth is assumed to be a single global boolean. It is useful when different shards, tenants, schema regions, or time windows have different witnesses.

### 15.5 Heartbeat failure suspicion

SessionStream's WebSocket heartbeat has an application-level challenge, a nonce, a write-completion time, a timeout policy, and matching-pong observations. The implementation documentation correctly treats timeout as **suspicion under a timing assumption**, not proof of remote crash.

Define a context

\[
U=(\text{connection},\text{challenge},\text{write time},\text{deadline policy},\text{observed messages}).
\]

At \(U\), the proposition

\[
\mathsf{Suspect}(c)
\]

may be true. The proposition

\[
\mathsf{Crashed}(c)
\]

is not justified by the same evidence. These are different subobjects.

Refining the context with a delayed matching pong can invalidate a naive monotone knowledge model. Therefore choose the context order carefully: an observation interval that has *closed* under a deadline may support suspicion, while later real-world evidence belongs to a different temporal context rather than a simple restriction.

This example demonstrates that local truth requires serious temporal modeling; it is not a decorative label for `unknown`.

### 15.6 Snapshot truth at a cut

Consider

\[
\varphi(S_n):
\text{“snapshot }S_n\text{ represents exactly the timeline through }n.”
\]

At a context containing only the snapshot payload, \(\varphi\) may not be decidable. At a context including event log, deterministic projector, projection version, and atomic store read, it may be provable by comparison.

The proposition's characteristic sieve records the refinements under which the proof exists.

This supports a practical evidence API:

```go
type Judgment struct {
    Proposition string
    Context     ContextID
    Evidence    []EvidenceRef
    Status      Status // established, refuted, unresolved under this context
}
```

Such an API is not itself a topos, but it mirrors the discipline of context-relative judgments.

### 15.7 Internal language

A topos can be reasoned about as if its objects were types and its arrows were terms. Subobjects behave like predicates, products like conjunctions of data, exponentials like function types, and quantifiers arise through adjunctions.

The internal logic is generally intuitionistic. This is not a philosophical tax. It reflects that context-indexed evidence may not decide every proposition globally.

A useful practice is to write invariants twice:

1. externally, as diagrams and natural transformations;
2. internally, as typed logical formulas.

Example external equation:

\[
\mathrm{lastOrd}\le\mathrm{snapshotOrd}.
\]

Internal formula:

\[
\forall e:\mathsf{Entity}(S),\;
\mathsf{LastOrdinal}(e)\le\mathsf{Cut}(S).
\]

The external view clarifies maps and contexts. The internal view supports compositional reasoning.

### 15.8 Do not conflate local truth with eventual consistency

Eventual consistency is an operational convergence property. Local truth is semantic evaluation relative to contexts and covers. One can model eventual consistency sheaf-theoretically, but the terms are not interchangeable.

Likewise, intuitionistic logic is not simply “three-valued logic.” A sieve-valued truth can encode many stable modes of evidence.

### Exercises

**15.1 Translate.** Explain why “not observed” is weaker than logical negation in local semantics.

**15.2 Model.** Define contexts and propositions for `Suspect(connection)` and `Crashed(connection)`. State which observations justify each.

**15.3 Model.** Give a cover under which an existential SessionStream statement has different local witnesses on different pieces.

**15.4 Build.** Implement a small context-relative judgment engine. Ensure evidence is monotone only along arrows where the semantics justify monotonicity.

**15.5 Reflection.** Identify one production dashboard boolean that should instead expose context and evidence.

\newpage

## Adjunctions and Change of Context

### 16.1 A universal relationship between transformations

Functors

\[
F:\mathcal C\to\mathcal D,
\qquad
G:\mathcal D\to\mathcal C
\]

form an adjunction \(F\dashv G\) when there is a natural bijection

\[
\mathrm{Hom}_{\mathcal D}(F A,B)
\cong
\mathrm{Hom}_{\mathcal C}(A,G B).
\]

The bijection says that maps out of a freely or minimally transformed object correspond exactly to maps into a forgotten or interpreted object.

Goldblatt emphasizes the unit and counit universal properties. For software, this is preferable to memorizing the hom-set formula: an adjunction packages a best possible approximation subject to a constraint.

### 16.2 Free and forgetful constructions

A familiar example is

\[
\mathrm{FreeMonoid}\dashv\mathrm{UnderlyingSet}.
\]

A function from values into the underlying set of a monoid uniquely extends to a monoid homomorphism from the free monoid.

Software analogies include parsers, schema builders, query planners, and policy completions, but analogies must be proved. A serializer is not automatically left adjoint to a deserializer. Loss, validation failure, and noncanonical encodings can break the universal bijection.

### 16.3 Reindexing presheaves

A functor between context categories

\[
f:\mathcal C\to\mathcal D
\]

induces a reindexing functor on presheaves by precomposition:

\[
f^*:\widehat{\mathcal D}\to\widehat{\mathcal C},
\qquad
f^*(F)=F\circ f^{op}.
\]

This takes a data model defined over \(\mathcal D\) and views it over \(\mathcal C\).

Example: \(\mathcal C\) may be the detailed SessionStream context category and \(\mathcal D\) a simpler public API context category. A functor \(f\) says how every detailed context appears publicly. Reindexing pulls a public presheaf back to the detailed architecture.

### 16.4 Kan extensions: minimal and maximal transport

Under suitable size conditions, reindexing has both adjoints:

\[
\mathrm{Lan}_f\dashv f^*\dashv\mathrm{Ran}_f.
\]

The left Kan extension transports data along \(f\) using colimits: it combines source information in the freest or most generated way compatible with the target.

The right Kan extension uses limits: it completes target data by collecting all compatible source observations.

Software intuition:

- **left Kan extension** resembles aggregation, generated migration, or least committed completion;
- **right Kan extension** resembles compatible reconstruction, query-by-all-refinements, or greatest constrained completion.

These are intuitions only. The actual comma-category formulas determine the result.

### 16.5 Schema and architecture migration

Suppose version 1 contexts map into version 2 contexts:

\[
f:\mathcal C_{v1}\to\mathcal C_{v2}.
\]

Questions become:

- Can a v2 presheaf be reindexed to v1 consumers?
- What is the minimal v2 extension of v1 data?
- What compatible v1 information can be reconstructed from v2?
- Does migration preserve the finite-limit invariants used by snapshots and projection commits?

This is more precise than saying “the migration is backward compatible.” Compatibility is relative to chosen presheaves and preserved diagrams.

### 16.6 Pullback functors and dependent data

For a map of base objects \(f:A\to B\), pulling back bundles or dependent data along \(f\) reindexes fibers over \(B\) to fibers over \(A\). In software:

- attach session-scoped data to a connection by its subscribed session;
- pull an authorization policy back along a command's session map;
- reindex schema-specific data along a schema-version map.

The pullback functor often has adjoints corresponding to dependent sum and dependent product. Internally, these become existential and universal quantification.

### 16.7 Sheafification as an adjunction

For a site \((\mathcal C,J)\), inclusion

\[
i:\mathbf{Sh}(\mathcal C,J)\hookrightarrow\widehat{\mathcal C}
\]

has a left adjoint

\[
a:\widehat{\mathcal C}\to\mathbf{Sh}(\mathcal C,J),
\qquad
a\dashv i.
\]

Sheafification \(aF\) is universal among maps from \(F\) into sheaves.

Software interpretation: once a coverage policy has been fixed, sheafification is the canonical way to move from raw local assignments toward a semantics satisfying locality and gluing. It may identify observational duplicates and add locally determined sections.

Again, this is not automatic bug repair. The result is canonical relative to the site, not necessarily relative to product intent.

### 16.8 Unit and counit as round-trip laws

An adjunction has a unit

\[
\eta:1_{\mathcal C}\Rightarrow GF
\]

and counit

\[
\varepsilon:FG\Rightarrow1_{\mathcal D}
\]

satisfying triangle identities.

These resemble encode/decode or migrate/forget round trips, but the laws are not generally isomorphisms. The unit embeds an object into its free-then-forgotten approximation; the counit evaluates a free construction in a target.

This gives a more nuanced language than insisting every transformation be reversible.

### Exercises

**16.1 Translate.** Give a software explanation of an adjunction that does not use the phrase “two functors going opposite ways.”

**16.2 Prove.** Derive the unit's universal property from the hom-set bijection.

**16.3 Model.** Define a context functor from detailed SessionStream contexts to public WebSocket contexts. Describe reindexing of a public frame presheaf.

**16.4 Build.** For finite categories and finite sets, compute a small left or right Kan extension by enumerating the relevant comma-category diagram.

**16.5 Counterexample.** Show why protobuf encode/decode need not form an adjoint equivalence when unknown fields, defaults, or noncanonical JSON are included.

\newpage

## Geometric Morphisms and Architecture Change

### 17.1 The topos-level map

A geometric morphism from a topos \(\mathcal E\) to a topos \(\mathcal F\) consists of an adjoint pair

\[
f^*:\mathcal F\rightleftarrows\mathcal E:f_*
\]

with

\[
f^*\dashv f_*
\]

and \(f^*\) preserving finite limits. The functor \(f^*\) is called the inverse-image part; \(f_*\) is the direct-image part.

The direction is named after the underlying geometric intuition: a continuous map of spaces pulls sheaves back and pushes them forward.

### 17.2 Why left exactness matters

Finite limits express:

- terminal structure;
- products of observations;
- equalizers of implementations;
- pullbacks over shared identities or cuts.

If \(f^*\) preserves finite limits, then changing context through the inverse-image functor preserves these finite-limit invariants.

For software architecture, this suggests a strong migration criterion:

> A change of observational universe should preserve the coherent finite-limit structures on which contracts depend.

This is far stronger than field-level compatibility.

### 17.3 A candidate SessionStream migration

Suppose \(\mathcal E\) models the internal architecture with canonical events, timeline entities, cursors, and transport states. Suppose \(\mathcal F\) models a public client API with snapshots and live frames.

A context map may induce an inverse-image functor that interprets public contextual data internally. To claim a geometric morphism, one would need:

1. a well-defined functor between the topoi;
2. a right adjoint;
3. proof that the inverse image preserves finite limits.

This book does not assert that the current API realizes such a morphism. It proposes the criterion as a research target.

### 17.4 Examples of preservation obligations

If a public snapshot predicate is defined by a pullback of `SessionId` and `SnapshotOrdinal`, inverse image should carry it to the corresponding internal pullback.

If two public frame transformations have an equalizer expressing “same client-visible behavior,” inverse image should preserve that equalizer.

If the public model combines snapshot and live sections by a product constrained over a cut, inverse image should preserve the constrained product.

Failure can reveal that the public API merges distinctions required for internal correctness.

### 17.5 Direct image as aggregation of local data

The right adjoint \(f_*\) often collects or pushes contextual data forward. In software terms it may resemble exposing an internal presheaf through a public context system.

Right adjoints preserve limits. Therefore compatible internal families remain compatible after direct image. This can be useful for aggregating observations, though it may retain more constraint structure than a simple serializer.

### 17.6 Geometric logic

Geometric morphisms preserve the interpretation of **geometric logic**, built from finite conjunctions, arbitrary disjunctions, and existential quantification. This fragment is stable under inverse-image functors.

For architecture specifications, geometric formulas are attractive because they can be transported across models. However, negation, universal quantification, and implication are more delicate and need not be preserved in the same way.

A possible research direction is to express portable SessionStream contracts in a geometric fragment:

- “there exists a matching entity version”;
- “one of these error classifications holds”;
- “these finitely many identity/cut equations hold.”

### 17.7 A practical migration checklist

When adapting SessionStream across storage backends, transports, or schema generations, ask:

1. What are the context categories on both sides?
2. Which presheaves represent events, views, snapshots, and evidence?
3. What is the reindexing or inverse-image operation?
4. Does it preserve terminal objects, products, equalizers, and pullbacks used by invariants?
5. Is there a right adjoint that interprets or aggregates data back?
6. Which logical formulas remain valid after transport?

Even without proving a geometric morphism, this checklist exposes semantic loss.

### 17.8 The second major caution

Terms such as “topos,” “geometric morphism,” and “sheafification” should not be used as metaphors alone. Each requires explicit categories, functors, natural transformations, and laws.

The reward for this strictness is that architectural intuition becomes testable mathematics.

### Exercises

**17.1 Translate.** Explain finite-limit preservation using products, equality constraints, and typed joins.

**17.2 Model.** Choose one SessionStream adapter and list the finite-limit diagrams it should preserve.

**17.3 Counterexample.** Construct a schema projection that preserves products of fields but not an equalizer expressing a cross-field invariant.

**17.4 Build.** Extend the finite-category laboratory to test whether a functor preserves selected finite limits.

**17.5 Research note.** Draft a one-page argument for or against modeling a public/internal SessionStream boundary as a geometric morphism.
EOF
```

<details><summary>💭 Thinking</summary>

**Drafted accessible Part III and cohomology obstruction calculus chapters**

</details>

```unknown
bash -lc cat > /mnt/data/sessionstream_sheaves_textbook/05-part-v.md <<'EOF'
# From Theory to a SessionStream Verification Instrument

## A Trace-to-Section Verification Harness

### 23.1 The goal

The applied goal is not to annotate the codebase with category-theory vocabulary. It is to build a tool that takes a declared local-to-global model and runtime or test traces, then answers:

1. Are all local sections well-typed and locally valid?
2. Do restrictions satisfy the presheaf laws?
3. Do supplied sections agree on overlaps?
4. Does a global section exist under the model?
5. Is it unique?
6. If linear transition data are supplied, do they carry a nontrivial cohomology class?
7. Which concrete contexts, restrictions, and loops support the diagnostic?

Call the prototype **SessionStream Atlas**.

### 23.2 Separate specification from evidence

Maintain two inputs.

The **model specification** declares:

- context category;
- section schemas at each context;
- restriction maps;
- covering families;
- local validity constraints;
- global invariants;
- optional coefficient groups and coboundary matrices.

The **evidence trace** supplies:

- concrete local sections;
- timestamps and cut labels;
- provenance for every observation;
- transaction or observer identity;
- schema and projection versions;
- failure records.

Do not infer the model from traces alone. Do not assume the specification is realized merely because it parses.

### 23.3 A minimal Go model

```go
package atlas

import (
    "context"
    "encoding/json"
)

type ContextID string
type ArrowID string
type CoverID string

type Context struct {
    ID          ContextID
    Description string
}

type Arrow struct {
    ID          ArrowID
    Source      ContextID
    Target      ContextID
    Description string
}

type Section struct {
    Context    ContextID
    Schema     string
    Value      json.RawMessage
    Provenance []string
}

type Restriction func(
    ctx context.Context,
    section Section,
) (Section, error)

type PresheafSpec struct {
    Contexts     map[ContextID]Context
    Arrows       map[ArrowID]Arrow
    Identities   map[ContextID]ArrowID
    Composition  map[[2]ArrowID]ArrowID
    Restrictions map[ArrowID]Restriction
}

type Cover struct {
    ID      CoverID
    Whole   ContextID
    Pieces  []ContextID
    // Overlaps should be explicit objects/pullbacks, not inferred by names.
    Overlaps map[[2]ContextID]ContextID
}
```

Production code will need typed values rather than generic JSON. The generic form is useful for a first finite laboratory and serialized model files.

### 23.4 Presheaf-law checking

For every sampled or finite section \(s\in F(U)\), check identity:

```text
restrict(identity_U, s) == s
```

For composable arrows \(U -> V -> W\), check composition:

```text
restrict(U->W, s)
==
restrict(V->W, restrict(U->V, s))
```

Failures should report:

- section provenance;
- direct and composed paths;
- normalized values;
- equality semantics;
- missing hidden inputs suspected by the comparison.

A naturality checker uses the same shape with an operation inserted into both paths.

### 23.5 Compatibility and gluing reports

```go
type OverlapMismatch struct {
    LeftContext   ContextID
    RightContext  ContextID
    Overlap       ContextID
    LeftValue     json.RawMessage
    RightValue    json.RawMessage
    LeftPath      []ArrowID
    RightPath     []ArrowID
}

type GluingReport struct {
    Cover          CoverID
    Compatible     bool
    Mismatches     []OverlapMismatch
    Amalgamations  []Section
    Unique         bool
    Assumptions    []string
}
```

For a finite model, enumerate candidate global sections. For realistic models, encode constraints into:

- SQL queries;
- a SAT solver;
- an SMT solver such as Z3;
- Datalog;
- property-based generators;
- a custom replay oracle.

The sheaf checker is then a wrapper around a global-solution search plus restriction comparison.

### 23.6 SessionStream trace facts

A useful event-processing trace record might include:

```go
type ProjectionStepTrace struct {
    SessionID                string
    EventName                string
    EventOrdinal             uint64
    EventAppendCommitted     bool
    TimelineApplyCommitted   bool
    ProjectionCursorBefore   uint64
    ProjectionCursorAfter    uint64
    SnapshotOrdinalObserved  uint64
    MaxEntityOrdinalObserved uint64
    FanoutAttempted          bool
    FanoutCompleted          bool
    ProjectionVersion        string
    SchemaVersion            string
    TransactionID            string
}
```

One record should not pretend to be atomic unless all fields derive from the same atomic or causally justified observation. Provenance and transaction IDs are part of the section, not debugging metadata.

For hydration:

```go
type HydrationTrace struct {
    SessionID          string
    ConnectionID       string
    SubscribeAccepted  bool
    HydratingAt        int64
    SnapshotOrdinal    uint64
    SnapshotWriteAt    int64
    BufferedOrdinals   []uint64
    DrainedOrdinals    []uint64
    LiveOrdinals       []uint64
    BufferOverflowed   bool
    EnteredLiveAt      int64
    ProjectionVersion string
}
```

Use monotonic logical sequence numbers or causal markers where wall-clock timestamps are insufficient.

### 23.7 A five-stage analysis pipeline

**Stage 1: normalize.** Decode concrete protobuf messages, use explicit ordinal types, canonicalize entity ordering, and attach versions.

**Stage 2: local validation.** Check each section against its context-local schema and constraints.

**Stage 3: restriction validation.** Compute every declared overlap value and report direct mismatch.

**Stage 4: global-section search.** Ask whether local sections extend to a complete valid execution. Report zero, one, or multiple completions.

**Stage 5: cohomological analysis.** For selected additive transition fields, construct cochains, verify cocycle conditions, reduce modulo coboundaries, and map representatives back to architecture loops.

Do not run Stage 5 when Stage 2 or Stage 3 already shows ordinary invalidity unless the goal is exploratory diagnosis.

### 23.8 Model the error space

Projection errors, buffer overflows, unknown schemas, and connection closures need sections in an error-aware model.

One option is a sum:

\[
F_{\mathrm{outcome}}(U)
=F_{\mathrm{success}}(U)+F_{\mathrm{failure}}(U).
\]

Restrictions must explain how failure evidence is retained or redacted. A public context may forget internal stack traces while preserving error class and session.

A global section can then represent a coherent failed execution rather than requiring every execution to be successful.

### 23.9 Testing coverage realization

For every declared cover, record its implementation witness:

| Cover | Witness | Verification |
|---|---|---|
| entity rows + snapshot cut | read transaction | isolation/concurrency test |
| snapshot + post-cut batches | hydrating subscription buffer | interleaving test |
| event + materialization + cursor | transaction or repair protocol | fault-injection test |
| heartbeat timeout evidence | state-machine trace | model-based test |

Atlas should reject or warn about a cover with no witness reference.

### 23.10 Runtime cost and placement

The tool need not run on critical paths. Possible modes:

- deterministic unit-test laboratory;
- property-based integration tests;
- offline trace analysis;
- sampled production observer;
- replay audit in CI;
- schema-version migration check.

The model should distinguish evidence gathered synchronously from evidence reconstructed later.

### 23.11 Output format

A useful report has four layers:

1. **plain statement:** “snapshot cut and entity set do not agree”;
2. **local evidence:** exact restrictions and values;
3. **global consequence:** no amalgamation under cover `hydrate-v1`;
4. **topological/algebraic context:** supported on loop or face `E-T-S-C-U`, class representative if applicable.

The mathematics should improve diagnostics, not obscure them.

### Exercises

**23.1 Build.** Implement the Go data structures above and a presheaf identity/composition checker.

**23.2 Build.** Add a finite gluing checker with exact mismatch reports.

**23.3 Model.** Write a machine-readable specification for the snapshot-plus-suffix cover.

**23.4 Build.** Convert a SessionStream integration-test trace into local sections and overlap values.

**23.5 Design.** Define a report schema that distinguishes local invalidity, overlap mismatch, no global completion, nonunique completion, and nontrivial cohomology.

**23.6 Reflection.** Identify the smallest useful Atlas prototype that could find a real class of bug within two weeks.

\newpage

## Capstone: A SessionStream Sheaf and Cohomology Study

### 24.1 The capstone question

Build and defend one precise answer to:

> Under what observation contexts and coverage policies do SessionStream's event, projection, hydration, and transport views form a sheaf of valid execution fragments, and what additive transition data can carry a nontrivial cohomological obstruction?

A good capstone is narrow enough to compute and broad enough to expose a real architectural boundary.

### 24.2 Recommended scope

Use one session and one command handler from `examples/chatdemo`. Bound histories to at most five canonical events. Model:

- event prefix;
- timeline entities;
- projection cursor;
- snapshot cut;
- hydrating WebSocket buffer;
- client reconstruction.

Ignore multi-session fanout, authorization, and heartbeat in the first model. Add one dimension only after the first sheaf condition is executable.

### 24.3 Phase 1: semantic inventory

Produce a table:

| Name | Go representation | Semantic meaning | Equality | Version |
|---|---|---|---|---|
| event ordinal | `Event.Ordinal` | producing event position | numeric under one session | assignment policy |
| snapshot ordinal | `Snapshot.SnapshotOrdinal` | last timeline ordinal represented | exact cut | store version |
| entity last ordinal | `TimelineEntity.LastEventOrdinal` | latest event reflected by entity | numeric | projection version |
| client next expected | client state | next acceptable live ordinal | numeric after conversion | protocol version |

This prevents machine-type equality from replacing semantic equality.

### 24.4 Phase 2: finite context category

Define 8-15 contexts. Include at least:

```text
EventPrefix(n)
TimelineState(n)
ProjectionProgress(n)
Snapshot(n)
HydratingBuffer(n,m)
LiveSuffix(n,m)
ClientState(m)
AtomicStoreRead(n)
```

List every arrow and composition. Implement a category-law checker.

Deliverable: `contexts.yaml` plus a generated diagram.

### 24.5 Phase 3: presheaves and restrictions

Define at least three presheaves:

- `ExecutionFragments`;
- `Evidence`;
- `OrdinalCoordinates`.

For each, document section schemas and restrictions. Test the presheaf laws with finite data.

Deliverable: model ledger and executable law tests.

### 24.6 Phase 4: coverage and sheaf tests

Declare two covers:

1. snapshot plus buffered/live suffix covers client reconstruction;
2. event prefix plus projection semantics covers timeline state.

For every cover, enumerate compatible local families and global amalgamations in the bounded model.

Classify failures:

- restriction bug;
- incompatible local sections;
- missing global section;
- multiple global sections;
- false cover caused by missing version or identity coordinate.

Deliverable: a sheaf-condition report with at least one deliberately injected counterexample.

### 24.7 Phase 5: architecture nerve

Build the nerve of your covers and mark each simplex with its implementation witness.

Generate two versions:

- the intended protocol complex;
- the actually observed/testable complex.

Differences between them are architectural hypotheses requiring verification.

Deliverable: diagrams and witness table.

### 24.8 Phase 6: cohomology laboratory

Choose one additive coefficient system, preferably typed ordinal offsets. Construct \(D_0\) and \(D_1\). Compute:

\[
H^0,
\qquad
H^1.
\]

Inject an off-by-one adapter around a loop. Show:

- the transition data satisfy or fail face cocycle conditions;
- the loop circulation;
- whether the cocycle is a coboundary;
- the concrete adapter contracts involved.

Deliverable: exact matrix computation and human-readable diagnostic.

### 24.9 Phase 7: local logic

Define three propositions:

- `SnapshotSafe(S)`;
- `ProjectionCommitted(e)`;
- `ConnectionSuspected(c)`.

For each, provide:

- the subpresheaf or predicate object;
- contexts where it is decidable;
- its sieve-valued evidence interpretation;
- one invalid use of classical negation.

Deliverable: a local-truth memo.

### 24.10 Phase 8: architecture proposal

Use the model to recommend exactly one change, such as:

- distinct ordinal types and explicit conversions;
- a read transaction for snapshot cut and entity rows;
- atomic projection apply-plus-cursor advancement;
- stable logical event identity;
- version coordinates in snapshot/live overlap;
- a richer observer trace.

Your proposal must state which context, cover, restriction, or global-section law it repairs.

### 24.11 Evaluation rubric

| Criterion | Weak | Strong |
|---|---|---|
| Objects/arrows | component names only | exact semantic types and total maps |
| Restrictions | informal “forgetting” | executable, law-checked functions |
| Covers | “these services together” | stable, witnessed coverage policy |
| Sheaf claim | analogy | enumerated or proved gluing theorem |
| Cohomology | hole metaphor | coefficient system, matrices, representatives |
| Engineering value | vocabulary | actionable diagnostic or design change |
| Honesty | omitted assumptions | explicit limits and counterexamples |

### 24.12 Research directions after the capstone

Possible extensions:

- multi-replica event streams and descent data;
- authorization as a base dimension;
- schema migrations as nonabelian transition functions;
- heartbeat evidence in interval or temporal sheaves;
- cosheaves for event aggregation;
- sheaf Laplacians for approximate clock or latency reconciliation;
- geometric logic for portable architecture invariants;
- Kan extensions for versioned context migration;
- model extraction from OpenTelemetry traces;
- a Go analyzer that finds untyped ordinal conversions.

### Final exercise

Write a ten-page research report with these headings:

1. Claim;
2. Base category;
3. Presheaf definitions;
4. Coverage;
5. Sheaf theorem or counterexample;
6. Nerve and witnesses;
7. Coefficient system;
8. Cohomology calculation;
9. Engineering consequence;
10. Modeling limits.
EOF

cat > /mnt/data/sessionstream_sheaves_textbook/06-appendices.md <<'EOF'
\appendix

# Notation and Conventions

## Categories and arrows

| Symbol | Meaning |
|---|---|
| \(\mathcal C,\mathcal D\) | categories |
| \(A,B,C,U,V\) | objects or contexts |
| \(f:A\to B\) | arrow from \(A\) to \(B\) |
| \(1_A\) | identity arrow on \(A\) |
| \(g\circ f\) | first \(f\), then \(g\) |
| \(A\cong B\) | isomorphic objects |
| \(\mathrm{Hom}(A,B)\) | set of arrows \(A\to B\) |

## Limits

| Symbol | Meaning |
|---|---|
| \(A\times B\) | product |
| \(\mathrm{Eq}(f,g)\) | equalizer |
| \(A\times_C B\) | pullback over \(C\) |
| \(\lim D\) | limit of diagram \(D\) |
| \(1\) | terminal object when unambiguous |

## Presheaves and sheaves

| Symbol | Meaning |
|---|---|
| \(\widehat{\mathcal C}\) | \(\mathbf{Set}^{\mathcal C^{op}}\), presheaf category |
| \(F(U)\) | sections of \(F\) over context \(U\) |
| \(s|_V\) | restriction of section \(s\) to \(V\) |
| \(yU\) | representable presheaf \(\mathrm{Hom}(-,U)\) |
| \(\Gamma(F)\) | global sections of \(F\) |
| \(\mathbf{Sh}(\mathcal C,J)\) | sheaves on site \((\mathcal C,J)\) |
| \(\Omega\) | subobject classifier / truth-value object |
| \(U\Vdash\varphi\) | proposition \(\varphi\) is forced at \(U\) |

## Cohomology

| Symbol | Meaning |
|---|---|
| \(C^q\) | \(q\)-cochains |
| \(d^q:C^q\to C^{q+1}\) | coboundary |
| \(Z^q=\ker d^q\) | cocycles |
| \(B^q=\mathrm{im}\,d^{q-1}\) | coboundaries |
| \(H^q=Z^q/B^q\) | cohomology |
| \([c]\) | cohomology class of cocycle \(c\) |

## SessionStream ordinal conventions

Do not use one symbol for all ordinal-like quantities. Suggested notation:

| Symbol | Meaning |
|---|---|
| \(o_E\) | last persisted event ordinal |
| \(o_T\) | last materialized timeline ordinal |
| \(o_P\) | projection cursor |
| \(o_S\) | last ordinal represented by snapshot |
| \(o_U\) | producing event ordinal of a UI batch |
| \(o_C^+\) | client's next expected ordinal |

An explicit conversion is

\[
o_C=o_C^+-1
\]

when \(o_C^+>0\) and the protocol uses the stated conventions.

\newpage

# Selected Solutions and Hints

These are intentionally selective. A model-specific exercise may have several valid answers. The solution is acceptable only when its objects, arrows, equality, and assumptions are explicit.

## Chapter 1

### Solution 1.3

Let snapshots contain only current entities and a cut. Consider two event histories:

```text
H: Create A at 1; Delete A at 2
K: no event concerning A
```

At cut 2 both current snapshots may have no entity `A`, and all entity-wise ordinal inequalities hold vacuously. Yet the histories differ in audit meaning, replay side effects, and perhaps emitted UI events. Therefore current-entity snapshots do not uniquely determine canonical history.

The example demonstrates failure of uniqueness, not necessarily failure of snapshot correctness. The intended global object must say whether history or only current durable state is being reconstructed.

## Chapter 2

### Solution 2.1

Let \(f:A\to B\) have inverse \(f^{-1}\). If \(fg=fh\), compose on the left with \(f^{-1}\):

\[
f^{-1}fg=f^{-1}fh.
\]

Using associativity and \(f^{-1}f=1_A\), obtain \(g=h\); hence \(f\) is monic. The epic proof is dual: from \(gf=hf\), compose on the right with \(f^{-1}\).

### Solution 2.2

In a poset category there is at most one arrow between any two objects. Given parallel arrows \(g,h:C\to A\), they are already equal, so every arrow is monic. The epic argument is dual.

## Chapter 3

### Solution 3.2

Let \(e:E\to A\) equalize \(f,g:A\rightrightarrows B\). Suppose \(eu=ev\) for \(u,v:X\to E\). The common composite \(eu=ev:X\to A\) equalizes \(f\) and \(g\). By the equalizer's universal property there is a unique arrow from \(X\) to \(E\) factoring this composite. Both \(u\) and \(v\) do so, hence \(u=v\). Thus \(e\) is monic.

### Hint 3.3

Use an object of candidate pairs `(Snapshot, Entity)` and a map to `Ordinal x Ordinal`. Pull back the subobject \(\leq\hookrightarrow O\times O\). For whole-snapshot consistency, replace individual entities by an entity-set object with a `maxLastOrdinal` map and add identity/version constraints.

## Chapter 4

### Solution 4.6

Matching `SessionId` permits a snapshot at cut 42 to be paired with a live suffix beginning at 57. It also permits a snapshot from projection version v1 to be paired with v2 UI events. The shared session key establishes routing identity but not temporal continuity or semantic compatibility. The overlap needs at least cut convention and relevant version coordinates.

## Chapter 5

### Hint 5.1

Objects are prefixes; arrows are unique truncations. Identity truncates a prefix to itself. Composition of truncation functions is associative. A deterministic fold gives objects in the target. To obtain a functor, define target restriction so that folding then restricting equals truncating then folding.

### Solution 5.5

Suppose implementation \(F\) stores entities sorted by creation ordinal, while \(G\) stores them in arbitrary map order. At each cut one can sort \(G\)'s state to compare with \(F\), giving component-wise maps. If restriction to an earlier cut occurs before sorting and selects “first k entries” in current order, while restriction after comparison selects by ordinal, the naturality square fails. The comparison family is not natural under that restriction.

## Chapter 6

### Hint 6.1

Choose arrows from later prefixes to earlier prefixes. Then there is exactly one arrow \(H_m\to H_n\) when \(n\le m\). Composition is determined by the order, so associativity is automatic.

### Solution 6.5

A common false face is “event append, timeline application, and cursor advancement are atomic” when they are separate calls. A real omitted face may be the transaction inside SQLite `Apply`, which jointly updates entity versions, current entities, and the session snapshot ordinal.

## Chapter 7

### Solution 7.3

A store containing only a map from entity ID to current payload, with deletions physically removing entries and no version history, cannot generally map state at cut \(m\) to state at earlier cut \(n\). The same current map may result from many histories. No deterministic restriction function exists without additional history.

### Hint 7.4

Represent every section by an integer ID and every restriction by a lookup table. Check each section at each object against the identity table. For every composable pair of arrows, compare direct and two-step lookup results.

## Chapter 8

### Solution 8.2

If \(I=\bar I r\), then \(r(x)=r(y)\) implies \(I(x)=\bar I(r(x))=\bar I(r(y))=I(y)\).

Conversely, assume \(r\) is surjective and \(I\) is constant on fibers. Define \(\bar I(p)=I(x)\) for any \(x\) with \(r(x)=p\). Surjectivity supplies such \(x\), and fiber constancy makes the definition independent of choice. Then \(I=\bar I r\).

### Hint 8.3

Ask whether retries preserve ordinals, whether imports can reuse ordinals, and whether event name/payload differences at one position are rejected. Separate persisted-position identity from producer-assigned logical identity.

## Chapter 9

### Solution 9.3

Let the base be a circle covered by proper arcs, and let a presheaf assign bounded real-valued functions to each region. Restrictions preserve boundedness, and uniqueness holds because functions equal on a cover are equal. Locally bounded functions may glue to a globally unbounded function when the cover is infinite, so existence in the bounded presheaf can fail. For a finite toy site, construct the same phenomenon algebraically by declaring a compatible local family whose candidate global value is excluded from the global section set.

### Hint 9.5

For every cover and tuple of local sections, compare restrictions on explicit overlap objects. If compatible, enumerate sections at the whole context whose restrictions equal the tuple. Count amalgamations.

## Chapter 10

### Solution 10.2

Base case: an empty suffix gives \(\mathrm{FoldFrom}(S_n,[]) = S_n = \mathrm{Fold}(E_n)\).

Inductive step: assume applying \(e_{n+1},\ldots,e_k\) yields \(\mathrm{Fold}(E_k)\). Applying \(e_{k+1}\) gives the next fold state by determinism and the fold definition, hence \(\mathrm{Fold}(E_{k+1})\). Ordered complete delivery supplies every step exactly once.

### Solution 10.3

Pause after snapshot read at cut 10. Publish event 11 before registration. Register, send snapshot 10, and forward only future events beginning at 12. Event 11 is in neither local piece, so the family does not cover the complete history.

## Chapter 11

### Hint 11.2

Pull the hydration cover back along an authorization restriction. If the snapshot is redacted but live events are not redacted by the same policy, the induced pieces do not form a stable cover of authorized client state.

### Solution 11.4

A cursor is read at time \(t_1\), entity rows at \(t_2\), and live subscription state at \(t_3\). Even if the three observations collectively mention every required field, they do not cover a single coherent state unless the model includes temporal relationships or an atomic snapshot.

## Chapter 12

### Solution 12.2

For a connected graph, the incidence matrix has rank \(v-1\). With no faces, \(\dim H^1=e-(v-1)=e-v+1\). Each extra independent edge beyond a spanning tree creates one cycle direction.

### Hint 12.4

Use identity restrictions for one coefficient system, then change one edge restriction to the zero map or a shifted affine condition. The overlap graph is unchanged, but the global-section equations differ.

## Chapter 13

### Solution 13.2

At each context \(U\), define projections from \((F\times G)(U)=F(U)\times G(U)\). Given a presheaf \(H\) with natural transformations \(a:H\to F\) and \(b:H\to G\), define \(\langle a,b\rangle_U(h)=(a_U(h),b_U(h))\). Naturality follows componentwise, and uniqueness follows from uniqueness of ordered pairs at each context.

### Hint 13.3

The terminal presheaf assigns `{*}` everywhere. A global event-history section chooses a compatible history at every cut and observer context; all truncations and projections must agree.

## Chapter 14

### Solution 14.1

Define \((P\cap Q)(U)=P(U)\cap Q(U)\). Because both subpresheaves are closed under restriction, the intersection is also closed. Its inclusion into \(X\) is the pullback of the two inclusions in the presheaf category, computed pointwise.

### Hint 14.3

“Safe” belongs to a subobject of complete semantic states. “Verified safe” is a judgment or characteristic sieve describing contexts with adequate evidence. They coincide only under a completeness theorem for the evidence context.

## Chapter 15

### Solution 15.1

At context \(U\), failure to force \(\varphi\) means current evidence does not establish it. Forcing \(\neg\varphi\) requires that every refinement of \(U\) fails to establish \(\varphi\). A delayed pong or later store read may establish a proposition that was previously unresolved, so non-observation is not negation.

### Hint 15.2

Make `Suspect` depend on a completed challenge interval and policy assumptions. `Crashed` requires an oracle or stronger failure model. Do not define later wall-clock time automatically as a refinement if it can overturn a closed-interval judgment; use interval contexts and explicit extension maps.

## Chapter 16

### Hint 16.2

Set \(B=F(A)\) and map the identity under the hom-set bijection to obtain \(\eta_A:A\to GF(A)\). Naturality and the bijection show every \(g:A\to G(B)\) factors uniquely as \(G(f)\eta_A\).

### Solution 16.5

Protobuf JSON may omit default values, accept multiple textual encodings, preserve or discard unknown fields differently, and fail decoding. Thus encode/decode may be partial and round trips may not be identities under byte equality. An adjoint equivalence would require carefully chosen categories and semantic equality.

## Chapter 17

### Hint 17.2

For a transport adapter, list the terminal empty/no-op context, products of independent frame observations, equalizers expressing equivalent encodings, and pullbacks over session/cut identity. Test each diagram rather than asserting general left exactness.

### Solution 17.3

Project a record `(amount, quantity, unitPrice)` to `(amount, quantity)`. This projection preserves the product of the first two field sets but does not preserve the equalizer subobject `amount = quantity * unitPrice`, because `unitPrice` is forgotten and invalid/valid records may become indistinguishable.

## Chapter 18

### Solution 18.1

For a triple \(i<j<k\),

\[
(d^1d^0s)_{ijk}
=(s_k-s_j)-(s_k-s_i)+(s_j-s_i)=0
\]

with all sections restricted to the triple overlap. Every term cancels.

### Hint 18.4

Exact no-gap/no-duplicate delivery involves order, multiplicity, identity, and a finite sequence language. A single additive count can have the right total while containing duplicates and omissions.

## Chapter 19

### Solution 19.1

A 0-cocycle is constant on each connected component. Each component chooses one independent scalar, so \(H^0\cong\mathbb R^3\).

### Hint 19.4

A client value 43 meaning “next expected” agrees with a snapshot value 42 meaning “last included.” Their raw integers differ; conversion into a common overlap coordinate makes them equal.

## Chapter 20

### Solution 20.1

For a potential \(x\), every edge value is \(x_v-x_u\). Summing around an oriented cycle cancels every vertex once positively and once negatively, giving zero.

### Solution 20.2

The loop sum is 1, while every coboundary has loop sum zero. Therefore the assignment is not a coboundary. On the unfilled five-cycle it represents a nonzero \(H^1\) class.

### Solution 20.5

Choose vertex origins \(a=(0,1,1,1,1)\) on a cycle. The edge pattern \(d^0a=(1,0,0,0,-1)\) is nonzero on two edges but is a coboundary. It reflects local origin choices and has zero total circulation.

## Chapter 21

### Hint 21.4

Give each vertex one or more coordinates and each edge a canonical comparison space. Replace scalar incidence entries with conversion matrices. Check dimensions before assembling blocks.

## Chapter 22

### Solution 22.2

Let three boolean variables satisfy pairwise equality, so every additive parity discrepancy is zero, but add a nonlinear global constraint that exactly one variable is true. Pairwise equality forces either all false or all true, neither of which satisfies exactly-one. Additive \(H^1\) can vanish while the set-valued global-section problem has no solution.

### Hint 22.3

Use schema migrations as permutations or automorphisms of a structured payload. Compose them in order around a loop; a nonidentity round trip is holonomy.

## Chapter 23

### Hint 23.6

A high-value minimal prototype is a hydration interleaving laboratory that emits snapshot and buffer sections, checks cut restrictions, reconstructs client state, and compares against authoritative replay. Add cohomology only after the gluing checker is reliable.

\newpage

# Companion Laboratory Code

## A complete finite graph/cohomology script

```python
#!/usr/bin/env python3
"""Small architecture cohomology laboratory over rational numbers.

This is deliberately small. It computes incidence matrices, cycle-space
information, and least-squares/coboundary diagnostics. For exact integer
cohomology with torsion, add Smith normal form.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from typing import Iterable, Sequence


Vector = list[Fraction]
Matrix = list[list[Fraction]]


@dataclass(frozen=True)
class Edge:
    source: str
    target: str
    name: str


def transpose(a: Matrix) -> Matrix:
    return [list(column) for column in zip(*a)] if a else []


def rref(matrix: Matrix) -> tuple[Matrix, list[int]]:
    a = [row[:] for row in matrix]
    if not a:
        return a, []

    rows = len(a)
    cols = len(a[0])
    pivots: list[int] = []
    pivot_row = 0

    for col in range(cols):
        pivot = next(
            (r for r in range(pivot_row, rows) if a[r][col] != 0),
            None,
        )
        if pivot is None:
            continue

        a[pivot_row], a[pivot] = a[pivot], a[pivot_row]
        scale = a[pivot_row][col]
        a[pivot_row] = [value / scale for value in a[pivot_row]]

        for r in range(rows):
            if r == pivot_row:
                continue
            factor = a[r][col]
            if factor != 0:
                a[r] = [
                    x - factor * y
                    for x, y in zip(a[r], a[pivot_row])
                ]

        pivots.append(col)
        pivot_row += 1
        if pivot_row == rows:
            break

    return a, pivots


def rank(matrix: Matrix) -> int:
    return len(rref(matrix)[1])


def nullspace(matrix: Matrix) -> list[Vector]:
    if not matrix:
        return []
    reduced, pivots = rref(matrix)
    cols = len(matrix[0])
    free = [c for c in range(cols) if c not in pivots]
    basis: list[Vector] = []

    for free_col in free:
        vector = [Fraction(0) for _ in range(cols)]
        vector[free_col] = Fraction(1)
        for row, pivot_col in enumerate(pivots):
            vector[pivot_col] = -reduced[row][free_col]
        basis.append(vector)
    return basis


def incidence(vertices: Sequence[str], edges: Sequence[Edge]) -> Matrix:
    index = {name: i for i, name in enumerate(vertices)}
    d0: Matrix = []
    for edge in edges:
        row = [Fraction(0) for _ in vertices]
        row[index[edge.source]] = Fraction(-1)
        row[index[edge.target]] = Fraction(1)
        d0.append(row)
    return d0


def matvec(a: Matrix, x: Vector) -> Vector:
    return [sum(value * coord for value, coord in zip(row, x)) for row in a]


def solve(a: Matrix, b: Vector) -> Vector | None:
    augmented = [row[:] + [value] for row, value in zip(a, b)]
    reduced, pivots = rref(augmented)
    cols = len(a[0]) if a else 0

    for row in reduced:
        if all(value == 0 for value in row[:cols]) and row[cols] != 0:
            return None

    x = [Fraction(0) for _ in range(cols)]
    for row_index, pivot_col in enumerate(pivots):
        if pivot_col < cols:
            x[pivot_col] = reduced[row_index][cols]
    return x


def cycle_circulation(offsets: Sequence[int]) -> int:
    return sum(offsets)


def main() -> None:
    vertices = ["Event", "Timeline", "Snapshot", "Client", "LiveUI"]
    edges = [
        Edge("Event", "Timeline", "event_to_timeline"),
        Edge("Timeline", "Snapshot", "timeline_to_snapshot"),
        Edge("Snapshot", "Client", "snapshot_to_client"),
        Edge("Client", "LiveUI", "client_to_live"),
        Edge("LiveUI", "Event", "live_to_event"),
    ]

    d0 = incidence(vertices, edges)
    offsets = [Fraction(v) for v in [0, 0, 1, 0, 0]]
    potentials = solve(d0, offsets)

    print("rank D0:", rank(d0))
    print("H0 dimension:", len(vertices) - rank(d0))
    print("graph H1 dimension:", len(edges) - rank(d0))
    print("offset circulation:", cycle_circulation([0, 0, 1, 0, 0]))
    print("global potentials:", potentials)

    if potentials is None:
        print("The edge offsets are not a coboundary.")
    else:
        print("D0 x =", matvec(d0, potentials))


if __name__ == "__main__":
    main()
```

## Go skeleton for context-relative laws

```go
package atlas

import (
    "context"
    "fmt"
    "reflect"
)

type Value any

type FiniteRestriction struct {
    Arrow Arrow
    Apply func(context.Context, Value) (Value, error)
}

func CheckIdentity(
    ctx context.Context,
    identity FiniteRestriction,
    values []Value,
) error {
    for i, value := range values {
        restricted, err := identity.Apply(ctx, value)
        if err != nil {
            return fmt.Errorf("identity value %d: %w", i, err)
        }
        if !reflect.DeepEqual(restricted, value) {
            return fmt.Errorf(
                "identity law failed at %s for value %d: got %#v want %#v",
                identity.Arrow.Source,
                i,
                restricted,
                value,
            )
        }
    }
    return nil
}

func CheckComposition(
    ctx context.Context,
    direct FiniteRestriction,
    first FiniteRestriction,
    second FiniteRestriction,
    values []Value,
) error {
    for i, value := range values {
        directValue, err := direct.Apply(ctx, value)
        if err != nil {
            return fmt.Errorf("direct restriction value %d: %w", i, err)
        }
        intermediate, err := first.Apply(ctx, value)
        if err != nil {
            return fmt.Errorf("first restriction value %d: %w", i, err)
        }
        compositeValue, err := second.Apply(ctx, intermediate)
        if err != nil {
            return fmt.Errorf("second restriction value %d: %w", i, err)
        }
        if !reflect.DeepEqual(directValue, compositeValue) {
            return fmt.Errorf(
                "composition law failed for value %d: direct=%#v composite=%#v",
                i,
                directValue,
                compositeValue,
            )
        }
    }
    return nil
}
```

\newpage

# Model Ledger Templates

## Context specification

```text
Context ID:
Human meaning:
Concrete implementation witness:
Allowed sections:
Equality of sections:
Local constraints:
Incoming arrows:
Outgoing arrows:
Time semantics:
Version coordinates:
Authorization coordinates:
Failure sections:
```

## Restriction specification

```text
Arrow ID:
Source context:
Target context:
Operational action (truncate/project/redact/etc.):
Totality assumptions:
Information forgotten:
Fields converted:
Equality preservation:
Identity/composition laws:
Implementation function:
Tests:
Known counterexamples:
```

## Cover specification

```text
Cover ID:
Whole context:
Pieces:
Explicit overlap objects:
Compatibility equations:
Existence theorem or protocol:
Uniqueness theorem:
Pullback-stability argument:
Transitivity argument:
Implementation witness:
Failure behavior:
Executable tests:
```

## Cohomology specification

```text
Complex / nerve:
Vertices, edges, faces:
Coefficient group or vector space:
Meaning of zero:
Meaning of addition:
Restriction / transition maps:
D0 matrix:
D1 matrix:
Proof that D1*D0 = 0:
Meaning of H0:
Meaning of H1:
Representative diagnostics:
Claims allowed:
Claims forbidden:
```

\newpage

# Glossary

**Adjunction.** A universal correspondence between maps involving two functors, written \(F\dashv G\). Often expresses a best free construction paired with forgetting, or reindexing paired with aggregation/completion.

**Amalgamation.** A global section whose restrictions are a given compatible local family.

**Base category.** The category of contexts over which a presheaf varies.

**Cech cohomology.** A cohomology construction formed from a cover and its finite intersections.

**Cochain.** Data assigned to cells or intersections of one fixed dimension.

**Coboundary.** The image under the cochain differential; often a discrepancy generated by lower-dimensional local choices.

**Cocycle.** A cochain whose next coboundary vanishes; locally coherent transition data.

**Cone.** A compatible family of arrows from one object to every object in a diagram.

**Context.** A declared scope of observation, capability, time, schema, replica, or authorization.

**Contravariant.** Reversing arrows; presheaf restrictions run opposite to base arrows.

**Cover.** A family of contexts declared sufficient to determine a larger context.

**Equalizer.** Universal subobject on which two parallel arrows agree.

**Geometric morphism.** An adjoint pair between topoi whose inverse-image functor preserves finite limits.

**Global section.** A value coherent over the whole context, or a natural transformation from the terminal presheaf.

**Grothendieck topology.** A coherent declaration of covering families or sieves on a category.

**Holonomy.** Net transformation obtained by transporting data around a loop.

**Internal logic.** The typed logical language interpreted inside a category such as a topos.

**Kan extension.** Universal extension of a functor along another functor; left Kan extensions use colimit-like aggregation, right Kan extensions use limit-like compatible completion.

**Limit.** A universal coherent cone over a diagram.

**Local section.** One value of a presheaf over one context.

**Monomorphism.** Left-cancellable arrow; represents subobjects in a category.

**Natural transformation.** A context-wise family of arrows commuting with every source-category arrow.

**Nerve.** A simplicial record of which cover pieces have common intersections.

**Presheaf.** A contravariant functor from a context category to sets or another value category.

**Pullback.** Universal compatible pair over a shared codomain; a typed join or inverse-image construction.

**Representable.** Presheaf \(\mathrm{Hom}(-,U)\) of all probes into an object \(U\).

**Restriction map.** Operation that moves a section to a smaller, poorer, or differently scoped context.

**Separated presheaf.** A presheaf with uniqueness of gluing for the chosen covers.

**Sheaf.** A presheaf in which every compatible covering family glues uniquely.

**Sheafification.** Universal map from a presheaf to a sheaf for a chosen topology.

**Sieve.** A precomposition-closed family of arrows into one object; truth values in a presheaf topos.

**Site.** A category equipped with a Grothendieck topology.

**Stalk.** Classical local fiber of a sheaf at a point; in software analogy, a value space at a maximally localized observation, when such points are part of the model.

**Subobject classifier.** Object \(\Omega\) that turns subobjects into characteristic arrows and supplies internal truth values.

**Topos.** A category with finite limits, exponentials, and a subobject classifier, or a category of sheaves under standard hypotheses.

**Universal property.** A property defined by unique factorization among all competing constructions.

**Yoneda lemma.** The theorem that a presheaf's sections at \(U\) correspond naturally to transformations from the representable \(yU\).

\newpage

# Reading Map Back to Goldblatt

This book intentionally changes the examples and route. Use the following map to cross-read the attached volume.

| This book | Goldblatt sections | Purpose of cross-reading |
|---|---|---|
| Chapters 2-4 | 3.1-3.15 | arrow-only characterizations, products, equalizers, pullbacks, limits |
| Chapter 13-14 | 4.1-4.4, 4.7-4.8 | subobjects, classifiers, topos structure, power objects |
| Chapters 6-12 | 4.5 and 14.1-14.4 | bundles, sheaves, sites, Grothendieck topoi |
| Chapters 5 and 13 | 9.1-9.3 | functors, natural transformations, functor categories |
| Chapter 15 | 14.5-14.8 | local truth and Kripke-Joyal semantics |
| Chapter 16 | 15.1-15.4 | adjunctions and quantifiers |
| Chapter 17 | 16.1-16.4 | preservation, geometric morphisms, internal/geometric logic |
| Chapters 18-22 | not a direct Goldblatt route | Cech/cellular cohomology and applied obstruction models |

A recommended loop is:

1. read the relevant Goldblatt section;
2. restate its definition in your diagram notebook;
3. read the corresponding SessionStream chapter here;
4. complete one proof and one build exercise;
5. record where the analogy fails.

\newpage

# Bibliography and Further Study

## Primary pedagogical source

Goldblatt, Robert. *Topoi: The Categorial Analysis of Logic*. Revised edition. The attached Dover reprint is a corrected republication of the 1984 second edition with new material from 2006.

## Category theory and topoi

- Mac Lane, Saunders, and Ieke Moerdijk. *Sheaves in Geometry and Logic: A First Introduction to Topos Theory*.
- Leinster, Tom. *Basic Category Theory*.
- Riehl, Emily. *Category Theory in Context*.
- Fong, Brendan, and David I. Spivak. *An Invitation to Applied Category Theory: Seven Sketches in Compositionality*.
- Spivak, David I. *Category Theory for the Sciences*.
- The Stacks Project, especially the chapters on presheaves, sheaves, sites, and cohomology.

## Sheaves and applied topology

- Rosiak, Daniel. *Sheaf Theory through Examples*.
- Curry, Justin. *Sheaves, Cosheaves and Applications*.
- Ghrist, Robert. *Elementary Applied Topology*.
- Robinson, Michael. *Topological Signal Processing*.

## Contextuality and obstruction methods

- Abramsky, Samson, and Adam Brandenburger. “The Sheaf-Theoretic Structure of Non-Locality and Contextuality.”
- Abramsky and collaborators on cohomological obstructions and constraint satisfaction.

## Software-facing directions

Study these topics after completing the capstone:

- categorical databases and functorial data migration;
- temporal and interval sheaves;
- cellular sheaf Laplacians;
- sheaves on graphs for distributed estimation;
- nonabelian descent and schema transition functions;
- geometric logic and classifying topoi for portable specifications;
- formal refinement, model checking, and event-sourced system verification.

\backmatter

# Closing Perspective {-}

The productive idea is not that software systems secretly *are* topological spaces. It is that software engineers routinely work with partial, overlapping, context-indexed information and then make global claims from it.

Category theory asks whether the transformations compose.

Limits ask which tuples are jointly coherent.

Presheaves organize what can be known at each context and how it is forgotten.

Sheaves state when compatible local knowledge determines a unique whole.

Topos theory supplies a universe in which those contextual values have predicates, functions, and an internal logic.

Cohomology identifies selected transition patterns that remain globally twisted after all local coordinate changes.

For SessionStream, this turns an intuition into a research program:

\[
\text{runtime traces}
\longrightarrow
\text{local sections}
\longrightarrow
\text{restriction laws}
\longrightarrow
\text{covers and gluing}
\longrightarrow
\text{global executions}
\longrightarrow
\text{obstruction diagnostics}.
\]

The next step is not a larger metaphor. It is one small, explicit site and one executable sheaf condition.
EOF
```

<details><summary>💭 Thinking</summary>

**Compiled and visually inspected the textbook PDF, fixing layout and equations**

**Validating the manuscript**

I’ve finished the manuscript and am checking the revised PDF’s table of contents, final page, and page rendering so I can catch layout problems before sharing both files.

**Validated the manuscript**

</details>

```unknown
bash -lc set -euo pipefail
BOOK=/mnt/data/sessionstream_sheaves_textbook/sections-over-streams.pdf
MD=/mnt/data/sessionstream_sheaves_textbook/sections-over-streams.md
ls -lh "$BOOK" "$MD"
pdfinfo "$BOOK" | sed -n '1,25p'
rm -rf /mnt/data/sessionstream_sheaves_textbook/_renders_final
python /home/oai/skills/pdfs/scripts/render_pdf.py "$BOOK" --out_dir /mnt/data/sessionstream_sheaves_textbook/_renders_final --dpi 120
find /mnt/data/sessionstream_sheaves_textbook/_renders_final -maxdepth 1 -type f | sort | sed -n '1,5p'
find /mnt/data/sessionstream_sheaves_textbook/_renders_final -maxdepth 1 -type f | wc -l
```

<details><summary>💭 Thinking</summary>

**Validated, preflighted, and copied final textbook PDF files**

</details>

The manuscript is now complete through a repository-applied capstone, with extensive exercises and selected solutions. The PDF builds cleanly; I’m visually checking diagrams, tables, code, and math.

```json
{"paths":["GitHub"],"query":"fetch"}
```

## Deliverables

- [Download the Markdown textbook](sandbox:/mnt/data/local-truth-in-sessionstream.md)
- [Download the typeset PDF](sandbox:/mnt/data/local-truth-in-sessionstream.pdf)

## **Local Truth in SessionStream**

The finished book is a **31,800-word, 134-page custom study text** containing:

- **20 chapters**
- **6 appendices**
- **159 exercises**
- **40 selected solution sketches**
- A twelve-week study route
- A Goldblatt cross-reference map
- A frozen SessionStream source map
- A categorical and sheaf-theoretic cheat sheet
- A glossary and completion checklist
- A capstone specification for an executable `ss-sheafcheck` research tool

It begins at your current position in Goldblatt—**limits in Chapter 3**—and develops the material through one recurring SessionStream study:

$$
\text{limits}
\rightarrow
\text{pullbacks and equalizers}
\rightarrow
\text{functors}
\rightarrow
\text{presheaves}
\rightarrow
\text{sheaf gluing}
\rightarrow
\text{sites}
\rightarrow
\text{topos logic}
\rightarrow
\text{nerves and cohomology}.
$$

The recurring engineering examples include canonical event histories, projections, timeline views, snapshot cuts, event and projection cursors, deterministic replay, schema migrations, WebSocket hydration buffering, observer traces, retry identity, parameter sufficiency, and transactional witnesses.

The cohomology portion is explicitly separated as an **applied extension beyond Goldblatt’s principal route**. It first establishes the presheaf and sheaf model, then introduces nerves, cochains, $H^0$, and $H^1$ only where an additive coefficient system—such as cursor offsets or version-calibration defects—makes the construction mathematically justified.

The SessionStream analysis is anchored to repository commit `d62dca9f5efa2e3094d6c62e5ead5ed0c88fd35c`, dated 13 August 2026, and to the supplied Architecture Garden study. The PDF is searchable, bookmarked, preflighted, and uses embedded fonts.


---

> Let’s try again, more structured and pedagogical: 4 big chapters, and after writing the first draft, go back and make sure each definition and term worth defining or introducing is properly motivated and defined and then applied in a few examples, like in the goldblatt book. Pretend you are a student reading the text and trying to make sense of it, and then rewrite it.

```unknown
bash -lc cat /home/oai/skills/pdfs/SKILL.md && printf '\n---DOCX SKILL---\n' && cat /home/oai/skills/docx/SKILL.md
```

I’ll rebuild the textbook as four large chapters, then do a student-minded second pass strengthening motivation, definitions, examples, exercises, and sequencing before producing Markdown and PDF.

<details><summary>💭 Thinking</summary>

**Inspected book sources and existing outputs**

</details>

```unknown
bash -lc echo '--- heading outline ---'; grep -nE '^#{1,4} ' /mnt/data/local-truth-in-sessionstream.md | head -260; echo '--- installed converters ---'; command -v pandoc || true; command -v ebook-convert || true; command -v calibre-debug || true; command -v wkhtmltopdf || true; command -v weasyprint || true; command -v libreoffice || true
```

<details><summary>💭 Thinking</summary>

**Reviewed Markdown structure and listed document headings**

**Revising the textbook**

I’m planning a clearer second edition organized into four larger chapters, with stronger pedagogy, motivated terminology, definitions, examples, and exercises. I’ll keep the mathematical structure coherent while using the source as guidance rather than reproducing it.

**Revised the textbook**

</details>

```unknown
bash -lc rm -rf /mnt/data/goldblatt_epub && mkdir -p /mnt/data/goldblatt_epub && unzip -q '/mnt/data/Topoi The Categorial Analysis of Logic (Robert Goldblatt) (z-library.sk, 1lib.sk, z-lib.sk).epub' -d /mnt/data/goldblatt_epub && find /mnt/data/goldblatt_epub/OEBPS -maxdepth 2 -type f | sed -n '1,120p'; echo '--- nav files ---'; find /mnt/data/goldblatt_epub/OEBPS -maxdepth 1 -type f | grep -Ei 'toc|nav|ncx|html|xhtml' | head -100
```

<details><summary>💭 Thinking</summary>

**Rewrote topoi material into four chapters using XHTML and Goldblatt analysis**

**Organizing the rewrite**

I’m shaping the material into four coherent chapters: categorical foundations, indexed computation, sheaves and local-to-global correctness, then topos logic and cohomological ideas. I’ll follow a motivation-first progression from concrete software structures to abstract mathematics.

**Organized the rewrite**

</details>

```unknown
bash -lc ls -ld /mnt/data/sessionstream 2>/dev/null || true; git -C /mnt/data/sessionstream rev-parse HEAD 2>/dev/null || true; git -C /mnt/data/sessionstream status --short 2>/dev/null || true; git -C /mnt/data/sessionstream log -1 --format='%H %ad %s' --date=iso 2>/dev/null || true
```

<details><summary>💭 Thinking</summary>

**Inspected sessionstream status and researched Goldblatt chapters and sheaf terminology**

**Building the textbook**

I’m designing each section around a concrete problem, a motivated definition, worked examples, a common misconception, and exercises. I’ll then audit terminology and applications for consistency across all four chapters.

**Built the textbook**

</details>

```unknown
bash -lc rm -rf /mnt/data/sessionstream-src && git clone --depth 1 https://github.com/go-go-golems/sessionstream.git /mnt/data/sessionstream-src && git -C /mnt/data/sessionstream-src log -1 --format='%H%n%ad%n%s' --date=iso
```

<details><summary>💭 Thinking</summary>

**Cloned SessionStream details and checked PDF and diagram rendering tools**

**Designing supporting visuals**

I’m adding visual schematics for pipelines, pullbacks, context grids, sheaf gluing, and cohomological cycles. These diagrams will reinforce the geometric intuition without replacing the formal definitions or worked examples.

**Designed supporting visuals**

</details>

```unknown
bash -lc sed -n '1,760p' /mnt/data/local-truth-in-sessionstream.md > /mnt/data/old_part1.txt; sed -n '1690,2380p' /mnt/data/local-truth-in-sessionstream.md > /mnt/data/old_part2.txt; sed -n '2770,3950p' /mnt/data/local-truth-in-sessionstream.md > /mnt/data/old_part3.txt; sed -n '3950,4705p' /mnt/data/local-truth-in-sessionstream.md > /mnt/data/old_part4.txt; wc -w /mnt/data/old_part*.txt; sed -n '1,220p' /mnt/data/old_part2.txt
```

The four chapters will follow coherent state, contextual knowledge, local-to-global gluing, and residual shape, progressing through limits, presheaves, sheaves/topoi, and cohomology.

<details><summary>💭 Thinking</summary>

**Drafted and validated a local-to-global mathematics textbook manuscript**

</details>

```unknown
bash -lc cat >> /mnt/data/sessionstream_sheaves_textbook_v2/local-truth-global-behavior.md <<'EOF'

# Chapter 2: Functors, Presheaves, and Context-Indexed Data

## 2.1 Functors: transform a whole category without breaking composition

A single arrow transforms one object into another. Software architecture usually needs something larger: transform an entire family of objects and every admissible transformation between them.

A serializer maps each typed payload to a wire representation and each typed transformation to a corresponding wire transformation. A replay interpreter maps event prefixes to states and prefix extensions to state transitions. A schema migration maps every value and every operation from one versioned world into another.

The pressure is not merely to translate objects. The translation must preserve identities and composition. Otherwise a pipeline that is coherent before translation can become incoherent afterward.

### Definition 2.1: functor

> A **functor** $F:\mathcal C\to\mathcal D$ assigns:
>
> - to each object $A$ of $\mathcal C$, an object $F(A)$ of $\mathcal D$;
> - to each arrow $f:A\to B$, an arrow $F(f):F(A)\to F(B)$;
>
> such that
> $$
> F(1_A)=1_{F(A)}
> $$
> and
> $$
> F(g\circ f)=F(g)\circ F(f).
> $$

A functor preserves domains, codomains, identities, and composites. It may forget structure or identify distinctions, but it must do so coherently.

### Example 2.1: monotone maps as functors

If posets are viewed as categories, a functor $F:P\to Q$ is exactly a monotone function:

$$
p\leq p'\implies F(p)\leq F(p').
$$

This is the first bridge from ordinary context refinement to functoriality. A map from event cuts to projection cuts is functorial only if extending the event prefix never moves the claimed projection backward.

### Example 2.2: a replay functor

Let $\mathbf{Prefix}_s$ be the category of prefixes for one session. Let $\mathbf{State}$ be a category whose objects are timeline states and whose arrows are valid state transitions. A deterministic reducer suggests a functor

$$
R:\mathbf{Prefix}_s\to\mathbf{State}.
$$

For each prefix $E_n$, $R(E_n)=T_n$. For an inclusion $E_m\to E_n$, the functor assigns the transition from $T_m$ to $T_n$ obtained by folding the suffix.

The identity law says that folding an empty suffix changes nothing. The composition law says that folding from $m$ to $k$ and then $k$ to $n$ agrees with folding from $m$ directly to $n$:

$$
R(m\to n)=R(k\to n)\circ R(m\to k).
$$

This equation is a precise deterministic-replay law. A reducer that consults undeclared randomness may fail to define a functor because the same prefix inclusion can yield different transitions.

### Example 2.3: encoding as a functor

Suppose $\mathcal T$ is a category of typed messages and typed transformations, and $\mathcal W$ a category of wire schemas and wire transformations. An encoder is functorial when:

- identity transformations encode as identity transformations;
- encoding a composite transformation agrees with composing the encoded transformations.

Ordinary serialization functions are only the object part of this idea. To claim a functor, you must also say how relevant arrows are mapped.

### Definition 2.2: faithful, full, and essentially surjective

These terms are useful for comparing software representations, but they are not prerequisites for presheaves.

> A functor is **faithful** if it is injective on each hom-set: distinct arrows remain distinct.
>
> It is **full** if every arrow between image objects comes from an arrow in the source.
>
> It is **essentially surjective** if every target object is isomorphic to some image object.

A full, faithful, essentially surjective functor is an equivalence of categories, up to standard coherence details.

A wire representation may be faithful on semantic transformations without being full: the wire layer may admit malformed transformations that no typed source operation produces. A projection functor is usually not faithful because different event histories may yield the same view.

### SessionStream application: projection is not automatically a functor

It is tempting to write

$$
P:\mathbf{Events}\to\mathbf{UI}
$$

and call a projection a functor. But the repository interface

```go
Project(ctx, event, session, view) -> []UIEvent
```

shows that output depends on more than the event. The honest source object may need to include event, pre-event timeline view, session metadata, projector version, and declared environment. The arrows must represent compatible transitions of all those coordinates.

This is a recurring lesson: functoriality begins by choosing a truthful domain category.

### Definition 2.3: functor category

Given categories $\mathcal C$ and $\mathcal D$, the **functor category** $[\mathcal C,\mathcal D]$ has functors $\mathcal C\to\mathcal D$ as objects and natural transformations as arrows. Natural transformations are defined next.

Functor categories matter because a presheaf category is a functor category:

$$
[\mathcal C^{op},\mathbf{Set}].
$$

### Caution: mapping values is not enough

A JSON adapter, reducer, or API gateway is not a functor merely because it maps inputs to outputs. The identity and composition equations must be meaningful and valid. If there is no category of source arrows, the word "functor" has not yet earned its use.

### Exercises 2.1

1. Define a prefix category and a state-transition category for a counter. Prove that summing event deltas defines a functor.
2. Give a reducer that fails the identity law.
3. Give a reducer that preserves identities but fails composition because it reads current wall-clock time.
4. Is a hash function from events to digests likely to be faithful? Full? Explain relative to a chosen source and target category.
5. Identify the object part and arrow part of a schema migration functor.

## 2.2 Natural transformations: change an interpretation coherently everywhere

Suppose two functors interpret the same source category in two different ways. One projection produces version-1 timeline entities; another produces version-2 entities. One reducer is the production implementation; another is a reference model. One encoder uses an old wire schema; another uses a new schema.

A collection of per-object converters is not enough. The converters must commute with every source arrow. That coherence is a natural transformation.

### Definition 2.4: natural transformation

Let $F,G:\mathcal C\to\mathcal D$ be functors.

> A **natural transformation** $\eta:F\Rightarrow G$ assigns to every object $A$ of $\mathcal C$ an arrow
> $$
> \eta_A:F(A)\to G(A)
> $$
> called the **component** at $A$, such that for every arrow $f:A\to B$ in $\mathcal C$, the naturality square commutes:
> $$
> G(f)\circ\eta_A=\eta_B\circ F(f).
> $$

The square is:

```text
F(A) ----F(f)----> F(B)
 |                   |
eta_A               eta_B
 |                   |
 v                   v
G(A) ----G(f)----> G(B)
```

Read it as:

> convert, then evolve = evolve, then convert.

### Example 2.4: schema migration

Let $F$ interpret each event prefix as a version-1 timeline state and $G$ interpret it as a version-2 state. A family of migrations

$$
\eta_n:F(E_n)\to G(E_n)
$$

is natural when extending history and then migrating gives the same result as migrating the earlier state and applying the version-2 extension.

If a migration works only for final snapshots but not for incremental updates, the components exist but naturality fails.

### Example 2.5: reference reducer versus optimized reducer

Let $R$ be a simple fold from event prefixes to states and $O$ an optimized incremental implementation. A natural isomorphism $\eta:R\Rightarrow O$ would show that every prefix state corresponds reversibly and that prefix extension commutes with the correspondence.

This is stronger and more useful than comparing only one final state. It asserts coherence at every cut.

### Example 2.6: canonicalization

Suppose $F$ records raw wire values and $G$ records canonicalized values. Components $\eta_U$ canonicalize data in every context $U$. Naturality requires canonicalization to commute with restriction or evolution. If canonicalizing before truncating differs from truncating before canonicalizing, the operation is not natural with respect to that context structure.

### Definition 2.5: natural isomorphism

A natural transformation is a **natural isomorphism** when every component $\eta_A$ is an isomorphism. The functors then represent the same structure up to coherent representation change.

### SessionStream application: migration review template

For a proposed migration between projection versions, identify:

1. the source category of prefixes or contexts;
2. the old and new interpretation functors;
3. one migration component per context;
4. the naturality square for a one-event extension;
5. the equality notion on the two resulting states.

Testing one-event squares often suffices for a free prefix category because longer extensions are composites. This is the software value of the functor laws.

### Caution: ad hoc conversions can hide temporal inconsistency

A converter that fixes only current rows may appear correct while historical replay under the new schema disagrees. Naturality asks whether the conversion works coherently along all relevant arrows, not only at one object.

### Exercises 2.2

1. Draw a naturality square for migrating a timeline entity before or after applying one event.
2. Give a family of per-prefix conversions that is not natural.
3. Show that identity components form an identity natural transformation.
4. Explain how natural transformations compose vertically.
5. Suppose two serializers are naturally isomorphic on typed values but one drops unknown fields. Which category or equality assumption must be reconsidered?

## 2.3 Contravariance and the category of contexts

A projection or reducer follows the direction of history: more events lead to a later state. A presheaf behaves differently. When a context becomes smaller, the available data is restricted from the larger context to the smaller one. The direction of data flow is opposite to context inclusion.

This reversal is called contravariance.

### Definition 2.6: contravariant functor

A **contravariant functor** from $\mathcal C$ to $\mathcal D$ is a covariant functor

$$
F:\mathcal C^{op}\to\mathcal D.
$$

Thus an arrow $f:V\to U$ in $\mathcal C$ induces an arrow

$$
F(f):F(U)\to F(V)
$$

in $\mathcal D$.

For contexts, $V\to U$ usually means that $V$ is contained in or less informative than $U$. Contravariance gives the expected restriction from rich data over $U$ to poorer data over $V$.

### Definition 2.7: context

A **context** in this book is an object representing a scope within which observations or claims are meaningful. Context may include:

- a session;
- a temporal region or cut;
- a set of visible aspects;
- schema and projector versions;
- a connection or replica;
- an authorization principal;
- a trace region;
- a parameter set.

This is a modeling term, not a standard categorical primitive. The mathematical primitive is the object of a chosen base category.

### Example 2.7: aspect contexts

Let

$$
\mathsf{Aspect}=
\{E,T,S,U,C\}
$$

stand for event log, timeline, snapshot, live UI, and client view. Let objects be subsets $K\subseteq\mathsf{Aspect}$ and arrows be inclusions $J\to K$ when $J\subseteq K$.

A section over $K$ can mention all aspects in $K$. Restriction to $J$ forgets the others.

### Example 2.8: interval contexts

Let objects be finite ordinal intervals $[a,b]$, with an arrow

$$
[a,b]\to[c,d]
$$

when $[a,b]\subseteq[c,d]$. A trace over a large interval restricts by selecting records in the smaller interval.

Intervals are often better than cuts for gluing because two intervals can overlap on a nontrivial region.

### Definition 2.8: product category

Given categories $\mathcal C$ and $\mathcal D$, their **product category** $\mathcal C\times\mathcal D$ has pairs $(C,D)$ as objects and pairs of arrows $(f,g)$ as arrows. Identities and composition are componentwise.

A SessionStream context category can combine time and aspects:

$$
\mathcal B
=
\mathbf{Interval}_s\times\mathbf{Aspect}.
$$

An object $([a,b],K)$ says "observe aspects $K$ over interval $[a,b]$."

One can add version or principal coordinates by further products, but every coordinate increases model complexity. Add a coordinate only when it changes sections, restrictions, or coverage.

### SessionStream model 2.1: the base category

For the central examples, fix a session $s$ and define $\mathcal B_s$ as follows.

An object is

$$
U=([a,b],K,v),
$$

where $[a,b]$ is an ordinal interval, $K$ is a finite aspect set, and $v$ records schema/projector version information.

There is an arrow

$$
V=([a',b'],J,v')\longrightarrow U=([a,b],K,v)
$$

when:

- $[a',b']\subseteq[a,b]$;
- $J\subseteq K$;
- $v'$ is the declared restriction or compatible view of $v$.

Because this is a poset-like category, identities and composition follow from inclusion and version compatibility.

### Caution: the base category is designed, not discovered

There is no canonical "topology of SessionStream." A base category is an explicit hypothesis about which contexts exist and how information can be restricted. If a current-only database cannot reconstruct historical state, then an arrow from a current context to an earlier context may not support a meaningful restriction. You must either:

- retain historical versions;
- remove that arrow from the base;
- define a weaker section type;
- or use a setting with partial restriction maps.

A failed restriction law often means the context category is dishonest.

### Exercises 2.3

1. Build a product context category from event cuts and authorization scopes.
2. Explain why a trace over $[0,10]$ naturally restricts to $[3,7]$.
3. Explain why a current materialized row may not restrict to its state at ordinal 3.
4. Add a deployment-version coordinate to the base category. Which arrows should exist between versions?
5. Compare an interval base with a cut base for expressing overlap.
EOF
```

The first two chapters are drafted; I’m now slowing down contravariance into presheaves and compatible families into sheaf gluing, using explicit SessionStream restriction laws and counterexamples.

<details><summary>💭 Thinking</summary>

**Extended Chapters 2 and 3 on presheaves, sheaves, and local-to-global correctness**

</details>

```unknown
bash -lc cat >> /mnt/data/sessionstream_sheaves_textbook_v2/local-truth-global-behavior.md <<'EOF'

# Chapter 4: Topos Logic, Nerves, and Cohomological Diagnostics

## 4.1 From one sheaf to a universe of variable sets

So far, a presheaf has been one context-indexed data type. Category theory now asks us to consider the category of all such data types and their natural transformations.

For a small category $\mathcal C$, the presheaf category

$$
\widehat{\mathcal C}
=
[\mathcal C^{op},\mathbf{Set}]
$$

has:

- presheaves as objects;
- natural transformations as arrows.

This category behaves in many ways like $\mathbf{Set}$, but its "elements" vary by context. It has products, exponentials, subobjects, and a classifier of subobjects. It is an example of a topos.

The pressure for the topos concept is the same pressure Goldblatt emphasizes: can we describe a universe that supports set-like constructions using arrows alone, even when truth and elements vary with context?

### Definition 4.1: elementary topos

> An **elementary topos** is a category with finite limits, exponentials, and a subobject classifier.

Equivalently, it is a cartesian closed category with finite limits and a subobject classifier. Different texts package the finite-limit assumptions slightly differently; this is the formulation used here.

The three ingredients have distinct roles:

- **finite limits** support products, equality constraints, pullbacks, and coherent finite tuples;
- **exponentials** support internal function spaces and higher-order behavior;
- **the subobject classifier** supports predicates and truth values.

A topos is not a topological space. Historically, categories of sheaves motivated the name. Conceptually, a topos is a mathematical "place" or universe in which set-like reasoning can be carried out, often with nonclassical logic.

### Example 4.1: $\mathbf{Set}$

The category of sets is an elementary topos:

- it has finite limits;
- $B^A$ is the set of functions $A\to B$;
- the two-element set $\Omega=\{0,1\}$ classifies subsets.

This is the familiar universe whose logic is classical.

### Example 4.2: a presheaf topos

For any small category $\mathcal C$, the category

$$
[\mathcal C^{op},\mathbf{Set}]
$$

is a topos. Limits and much of the structure are computed context by context. The subobject classifier is not generally the constant two-element presheaf; at a context $U$, its elements are sieves on $U$.

This is the central software-facing example. A universe of context-indexed types has context-indexed truth values.

### Example 4.3: a sheaf topos

For a site $(\mathcal C,J)$, the category $\mathbf{Sh}(\mathcal C,J)$ of sheaves is a Grothendieck topos and therefore an elementary topos. The proof is beyond this book. The important idea is that after imposing the chosen local-to-global law, the resulting variable sets still support products, functions, predicates, and internal logic.

### SessionStream interpretation

Choose a context category $\mathcal B_s$ and consider all presheaves on it:

- trace presheaves;
- snapshot presheaves;
- evidence presheaves;
- schema presheaves;
- law presheaves;
- client-state presheaves.

Natural transformations connect them. Inside the presheaf topos, one can discuss products of observations, context-dependent functions, subobjects of valid states, and truth values that record where a claim can be established.

This does **not** mean the Go repository is itself a topos. The topos is the mathematical category of all presheaves on a chosen base model.

### Definition 4.2: Grothendieck topos

> A **Grothendieck topos** is a category equivalent to $\mathbf{Sh}(\mathcal C,J)$ for some site $(\mathcal C,J)$.

Every presheaf category is a Grothendieck topos using the trivial topology in which only maximal covers are required. Sheaf topoi arise from stronger coverage.

### Why this matters for software

A single global struct assumes all fields coexist at once. A presheaf topos begins with many possible context-indexed data types and permits reasoning about them without pretending every local value is globally available.

It gives a disciplined setting for statements such as:

- "this invariant holds in every refinement of the current context";
- "there exists a local witness on a cover";
- "this transformation is defined uniformly across versions";
- "this subobject of valid states is classified by a contextual truth value."

### Caution: a topos does not supply domain invariants automatically

Finite limits and a subobject classifier do not prove that a snapshot is sound, that a reducer is deterministic, or that a cover is appropriate. Those are modeled as objects, subobjects, and axioms inside the topos. The topos supplies a language and structural environment, not product correctness for free.

### Exercises 4.1

1. List the three structural ingredients in the definition of an elementary topos and connect each to one software capability.
2. Explain why a presheaf category contains more than one presheaf.
3. Why is "SessionStream is a topos" usually the wrong statement? Give a more precise statement.
4. Give a presheaf product and describe it contextwise.
5. State the difference between an elementary topos and a Grothendieck topos at the level needed in this book.

## 4.2 Subobjects and classifiers: predicates as arrows

In $\mathbf{Set}$, a predicate on a set $A$ selects a subset $S\subseteq A$. The subset can be represented by its inclusion $S\hookrightarrow A$ or by a characteristic function

$$
\chi_S:A\to\{0,1\}.
$$

Goldblatt uses this correspondence to motivate the subobject classifier and the definition of a topos. The categorical version lets predicates live in contexts where truth has more than two possible values.

### Definition 4.3: subobject

A **subobject** of $A$ is an equivalence class of monic arrows

$$
m:S\hookrightarrow A.
$$

Two monics $m:S\to A$ and $n:T\to A$ represent the same subobject when there is an isomorphism $i:S\to T$ with

$$
n\circ i=m.
$$

In $\mathbf{Set}$, subobjects correspond to subsets. In a presheaf category, a subobject of $F$ is a subpresheaf $S\subseteq F$: for every context $U$, $S(U)\subseteq F(U)$, and restriction preserves membership.

### Example 4.4: valid snapshots as a subpresheaf

Let $\mathsf{SnapshotCandidate}$ assign all well-typed candidate snapshots to each context. Define $\mathsf{ConsistentSnapshot}$ by selecting those satisfying:

$$
\forall e\in S.\operatorname{Entities},
\qquad
\operatorname{LastEventOrdinal}(e)\leq S.\operatorname{SnapshotOrdinal},
$$

plus session and schema compatibility.

For this to be a subpresheaf, restriction of a valid snapshot must remain valid. That requirement can reveal a bad restriction operation. If truncation only relabels the cut, validity may not be preserved.

### Definition 4.4: subobject classifier

A **subobject classifier** in a category $\mathcal E$ is an object $\Omega$ together with a monic arrow

$$
\operatorname{true}:1\hookrightarrow\Omega
$$

such that for every subobject $m:S\hookrightarrow A$, there is a unique arrow

$$
\chi_m:A\to\Omega
$$

making the square

```text
S ---------> 1
|            |
m            true
|            |
v            v
A --chi_m--> Omega
```

into a pullback.

The arrow $\chi_m$ is the **characteristic map** or **classifying map** of the subobject.

### Example 4.5: classifier in $\mathbf{Set}$

Take

$$
\Omega=\{0,1\}
$$

and `true` to select $1$. For a subset $S\subseteq A$,

$$
\chi_S(a)=
\begin{cases}
1,&a\in S,\\
0,&a\notin S.
\end{cases}
$$

The pullback of `true` along $\chi_S$ recovers exactly $S$.

### Definition 4.5: truth value

A **truth value** in a topos is a global element

$$
1\to\Omega.
$$

In $\mathbf{Set}$ there are exactly two: false and true. In a presheaf topos there can be many, reflecting stages or refinements on which a proposition becomes true.

### SessionStream application: classifying snapshot consistency

The subpresheaf inclusion

$$
\mathsf{ConsistentSnapshot}
\hookrightarrow
\mathsf{SnapshotCandidate}
$$

has a characteristic map

$$
\chi:
\mathsf{SnapshotCandidate}
\to
\Omega.
$$

At a context $U$ and candidate snapshot $s$, $\chi_U(s)$ is not necessarily a Boolean. It is a sieve describing the refinements of $U$ on which $s$ is seen to satisfy the predicate.

For example, a coarse observer may lack entity ordinals and be unable to establish consistency. A richer refinement that includes those ordinals may prove or refute it. The truth value records the contexts in which the claim holds persistently.

### Definition 4.6: power object, briefly

A **power object** $P(A)$ in a topos plays the role of the power set. Subobjects of $X\times A$ correspond naturally to arrows $X\to P(A)$. In an elementary topos, power objects can be constructed using exponentials and the subobject classifier, commonly as $\Omega^A$.

For software, the useful idea is that context-dependent collections and predicates can themselves be represented as objects. We will not develop the full theory.

### Caution: subobject is not subclass

A subobject is defined by a monic arrow and an equivalence relation on such arrows. It is not object-oriented inheritance. A Go subtype relation may or may not model a categorical subobject, depending on the category of types and arrows.

### Exercises 4.2

1. Prove that the pullback of `true` along a characteristic function in $\mathbf{Set}$ recovers the subset.
2. Define a subpresheaf of locally ordered trace records.
3. Show why validity must be preserved by restriction for a predicate to define a subpresheaf.
4. Give a candidate snapshot predicate that is not local under your restriction maps.
5. Explain why a truth value in a presheaf topos can contain more information than true/false.

## 4.3 Local truth: what can be established at a context

A proposition about a distributed system is often not simply true or false from every point of view.

- A client knows that it received a snapshot.
- The server knows that it enqueued a frame.
- An observer may know that the write loop reported success.
- No one local context may know that the remote application reduced the frame.

Topos logic treats truth as context-dependent while requiring it to persist under refinement in the appropriate direction.

### Definition 4.7: stage or context of truth

A **stage** is an object $U$ of the base category at which a proposition is evaluated. We write

$$
U\Vdash\varphi
$$

and read "the proposition $\varphi$ holds at stage $U$."

The symbol $\Vdash$ is forcing notation. Its exact Kripke-Joyal clauses depend on the topos. Here it is used to organize the central idea: truth may be established locally and must behave coherently under restriction.

### Truth values as sieves

In the presheaf topos $[\mathcal C^{op},\mathbf{Set}]$, the subobject classifier $\Omega$ assigns to each object $U$ the set of sieves on $U$.

For a predicate $S\hookrightarrow F$ and element $x\in F(U)$, its characteristic truth value is the sieve

$$
\chi_U(x)
=
\{f:V\to U\mid F(f)(x)\in S(V)\}.
$$

This is the collection of refinements on which the restricted element satisfies the predicate.

It is a sieve because if $f:V\to U$ establishes the predicate and $g:W\to V$ is a further refinement, then restriction stability of the subpresheaf ensures $f\circ g$ also establishes it.

### Example 4.6: contextual authorization

Let $F(U)$ contain requests visible at context $U$, and let $S(U)$ contain requests authorized using credentials and policy visible there.

For request $r\in F(U)$, $\chi_U(r)$ consists of refinements that reveal enough principal, tenant, and ACL information to establish authorization. If every refinement belongs to the sieve, the truth value is maximal: authorization already holds robustly at $U$. If no refinement can establish it, the sieve is empty.

### Example 4.7: observed delivery

Let $\varphi$ be "UI batch 42 was delivered to the client application."

Possible stages include:

- fanout call accepted;
- frame queued;
- frame written to socket;
- TCP acknowledged;
- browser message event fired;
- client reducer applied batch.

Each stage supports a different predicate. It is an error to treat evidence at an earlier stage as a proof at a later one unless the arrows and assumptions justify the implication.

### Definition 4.8: intuitionistic logic

**Intuitionistic logic** is a logic in which a proposition is asserted only with constructive or local evidence, and the law of excluded middle

$$
\varphi\vee\neg\varphi
$$

is not assumed universally.

Topos logic is generally intuitionistic. This does not mean every topos is motivated by philosophical constructivism. Goldblatt emphasizes that intuitionistic logic emerges from the categorical generalization of set-theoretic logic.

### Why excluded middle can fail operationally

At a stage lacking sufficient evidence, neither $\varphi$ nor $\neg\varphi$ may be established. For example, after a network timeout:

- you may not know that the remote side applied the command;
- you may not know that it did not apply it.

This is not a third classical truth value. It is absence of proof for either side at the current stage.

### Basic forcing readings

The full Kripke-Joyal semantics is beyond this book, but several clauses have direct engineering interpretations.

**Conjunction.** $U\Vdash\varphi\wedge\psi$ when both claims hold at $U$.

**Implication.** $U\Vdash\varphi\Rightarrow\psi$ when at every refinement $V\to U$, evidence for $\varphi$ at $V$ yields evidence for $\psi$ at $V$.

**Existence.** In a sheaf topos, $U\Vdash\exists x\,\varphi(x)$ may mean that $U$ has a cover on whose pieces local witnesses exist. A single global witness need not already be available at $U$.

**Disjunction.** $U\Vdash\varphi\vee\psi$ may mean there is a cover of $U$ such that on each piece one of the alternatives holds, possibly with different alternatives on different pieces.

These local clauses explain why sheaf logic and local-to-global reasoning are connected.

### Example 4.8: local existence of retry witnesses

Suppose different producer partitions each know a stable retry ID for events they originated, but there is no globally centralized ID registry. The statement "every delivery has a logical identity" may hold locally on a cover by producer contexts. Gluing those identities globally requires agreement on overlaps and may fail if events cross partitions without shared identity metadata.

### Definition 4.9: internal and external reasoning

**External reasoning** is ordinary mathematics about the topos as a category: its objects, arrows, and global properties.

**Internal reasoning** treats the topos as a universe of variable sets and reasons in its internal language, where objects act like types, arrows like functions, and subobjects like predicates.

The distinction matters. Externally, we may know that a presheaf has no global section. Internally, it may still be locally inhabited on a cover.

### Definition 4.10: geometric formula, briefly

A **geometric formula** is built using finite conjunctions, arbitrary disjunctions, and existential quantification, but not unrestricted negation or implication. Geometric logic is stable under inverse-image parts of geometric morphisms, making it well suited to reasoning that should survive change of context or base topos.

For software specifications, monotone evidence claims often have a geometric flavor:

- there exists a local witness;
- one of these observable cases holds;
- these finite compatibility conditions hold.

Claims involving absence, global uniqueness, or nontermination require more care.

### SessionStream local-truth worksheet

For any proposition, write:

1. **Formula:** what is being claimed?
2. **Stage:** which context evaluates it?
3. **Evidence:** what section or arrow witnesses it?
4. **Refinement:** does truth persist under smaller/more informative contexts?
5. **Coverage:** can local witnesses on a cover establish it?
6. **Operational gap:** what stronger proposition is being accidentally inferred?

Example:

```text
Formula: snapshot S is consistent at cut n
Stage: snapshot header + entity ordinal context
Evidence: all entity last-event ordinals <= n
Refinement: selecting fewer entities preserves the inequality
Coverage: entity partitions cover the full entity family only with a complete index
Gap: observer saw snapshot serialized != client applied snapshot
```

### Caution: unknown is not false

A missing trace record, timeout, or absent local witness may mean the current stage cannot decide. Treating absence of evidence as evidence of absence is equivalent to adding an unjustified classical principle to the operational model.

### Exercises 4.3

1. For a subpresheaf $S\subseteq F$, prove that $\chi_U(x)$ is a sieve.
2. Define stages for enqueue, write, receive, and reduce in the WebSocket path. State which implications need environmental assumptions.
3. Give a proposition for which neither it nor its negation is established after a timeout.
4. Explain the local-cover reading of existential quantification.
5. Distinguish internally inhabited from externally having a global section.
6. Apply the local-truth worksheet to "projection cursor 42 is trustworthy."
EOF
```

<details><summary>💭 Thinking</summary>

**Drafted and audited Topos Logic chapters, appendices, terminology, and source materials**

</details>

```unknown
from pathlib import Path
import re, pandas as pd, textwrap, json, os, math
path=Path('/mnt/data/sessionstream_sheaves_textbook_v2/local-truth-global-behavior.md')
lines=path.read_text().splitlines()
terms = {
'category':158,'object':158,'arrow':158,'domain':158,'codomain':158,'hom-set':158,'composition':158,'identity':158,
'commutative diagram':240,'isomorphism':301,'monic':317,'epic':317,'opposite category':339,'initial object':384,'terminal object':384,
'product':394,'coproduct':428,'equalizer':434,'coequalizer':434,'cone':487,'limit':509,'universal property':365,'pullback':574,'pushout':723,
'finite limit':544,'complete':544,'exponential
```

<details><summary>💭 Thinking</summary>

**Audited textbook terminology and pedagogical gaps**

</details>

```unknown
bash -lc python - <<'PY'
from pathlib import Path
import re, pandas as pd
path=Path('/mnt/data/sessionstream_sheaves_textbook_v2/local-truth-global-behavior.md')
lines=path.read_text().splitlines()
terms = {
'category':158,'object':158,'arrow':158,'domain':158,'codomain':158,'hom-set':158,'composition':158,'identity':158,
'commutative diagram':240,'isomorphism':301,'monic':317,'epic':317,'opposite category':339,'initial object':384,'terminal object':384,
'product':394,'coproduct':428,'equalizer':434,'coequalizer':434,'cone':487,'limit':509,'universal property':365,'pullback':574,'pushout':723,
'finite limit':544,'complete':544,'exponential':764,'evaluation':764,'cartesian closed':794,'subobject':661,
'functor':991,'faithful':1046,'full':1046,'natural transformation':1106,'component':1106,'naturality square':1106,
'contravariant':1190,'poset category':184,'product category':1248,'context':1208,'presheaf':1325,'section':1358,'restriction map':1325,
'global section':1358,'fiber':1491,'factorization':365,'representable':1594,'generalized element':1614,'Yoneda':1620,'stalk':1733,'germ':1715,
'cover':1910,'matching family':1995,'amalgamation':2018,'separated':2032,'sheaf':2046,'pretopology':2274,'site':2274,'sieve':2336,
'Grothendieck topology':2344,'sheafification':2617,'local equivalence':2640,'descent data':2205,'adjunction':2607,
'elementary topos':2847,'subobject classifier':2971,'truth arrow':2971,'characteristic map':2971,'truth value':3020,'power object':3053,
'internal language':3170,'stage':3082,'forcing':3152,'intuitionistic':3131,'excluded middle':3143,'geometric formula':3178,
'simplex':3247,'simplicial complex':3261,'nerve':3272,'Cech nerve':3285,'coefficient system':3465,'cochain':3471,'coboundary operator':3489,
'cocycle':3520,'coboundary':3520,'cohomology group':3538,'cellular sheaf':3663,
}
for term,dline in terms.items():
    pat=re.compile(re.escape(term),re.I)
    f=None
    for i,l in enumerate(lines,1):
        if pat.search(l):
            f=(i,l.strip());break
    if f and f[0]<dline:
        print(f'{term:26} def={dline:4} first={f[0]:4} :: {f[1][:100]}')
PY
```

<details><summary>💭 Thinking</summary>

**Inspected and reorganized mathematical manuscript sources and terminology coverage**

</details>

```unknown
bash -lc cat > /mnt/data/work_v2/pedagogy_pass.py <<'PY'
from pathlib import Path
import re

p=Path('/mnt/data/work_v2/first-draft.md')
text=p.read_text()

def insert_before(marker, block):
    global text
    if marker not in text:
        raise SystemExit(f'marker not found: {marker}')
    text=text.replace(marker, block.rstrip()+"\n\n"+marker,1)

def insert_after(marker, block):
    global text
    if marker not in text:
        raise SystemExit(f'marker not found: {marker}')
    text=text.replace(marker, marker+"\n\n"+block.rstrip(),1)

# ---------------- Chapter 1 ----------------
insert_before('### Commutative diagrams as route independence', r'''### Definition bridge: diagrams, paths, and commutativity

The category axioms let us compose arrows. They do not yet tell us which composites should agree. Software correctness frequently takes the form “these two routes have the same observable result,” so we need language for a network of arrows and for equality of routes through it.

> **Definition AUTO (Diagram).** A **diagram** in a category is a collection of objects and arrows arranged according to a fixed shape. Formally, the shape may itself be a category $J$, and a diagram of that shape is a functor $D:J\to\mathcal C$.

A **path** in a diagram is a composable sequence of arrows. Two arrows are **parallel** when they have the same domain and codomain.

> **Definition AUTO (Commutative diagram).** A diagram **commutes** when any two directed paths with the same starting object and ending object have equal composites.

Minimal example: a triangle

```text
A ----f----> B
 \           |
  \h         |g
   \         v
    -------> C
```

commutes exactly when $h=g\circ f$.

SessionStream example: let $A$ be typed backend events, $B$ wire frames, and $C$ client updates. If `encode` followed by `decode/project` is meant to preserve direct projection, the triangle commutes only after the equality on client updates has been fixed - byte equality, protobuf semantic equality, or equality after canonicalization.

Wider software example: a database cache square commutes when reading through the cache and reading through the source of truth produce the same value under the declared consistency boundary.

Near miss: two routes that eventually converge do not form a commuting diagram at the time being modeled. Eventual consistency is a temporal property, not equality of two arrows at one stage.''')

insert_before('### Duality', r'''> **Definition AUTO (Opposite category and duality).** The **opposite category** $\mathcal C^{op}$ has the same objects as $\mathcal C$. For every arrow $f:A\to B$ in $\mathcal C$, it has an arrow $f^{op}:B\to A$, and composition is reversed. A statement obtained by reversing every arrow in a categorical statement is its **dual**.

Minimal example: terminal objects in $\mathcal C$ are initial objects in $\mathcal C^{op}$. Products in $\mathcal C$ are coproducts in $\mathcal C^{op}$.

SessionStream use: event extension and information restriction naturally point in opposite directions. Keeping the base category and its opposite explicit prevents the common mistake of defining a restriction map with the same variance as context inclusion.''')

insert_before('### Diagrams and cones', r'''### Universal properties before limits

A beginner can memorize that a product is a pair, an equalizer is a subset, and a pullback is a join. That knowledge does not transfer well. Goldblatt's decisive move is to define each construction by how every competing construction maps to it.

> **Definition AUTO (Factorization and mediating arrow).** Given arrows $x:X\to B$ and $m:A\to B$, a **factorization** of $x$ through $m$ is an arrow $u:X\to A$ such that $m\circ u=x$. The arrow $u$ is the **mediating arrow**.

> **Definition AUTO (Universal property).** A construction has a **universal property** when every object carrying the required comparison data admits a unique mediating arrow to or from the proposed universal object. The direction is part of the definition.

The two words to audit are **exists** and **unique**. Existence says the universal object can represent every admissible competitor. Uniqueness says there is one canonical representation, not merely an implementation that happens to work.

> **Definition AUTO (Terminal and initial objects).** A **terminal object** $1$ receives exactly one arrow $A\to1$ from every object $A$. An **initial object** $0$ has exactly one arrow $0\to A$ to every object $A$.

In $\mathbf{Set}$, any singleton is terminal and the empty set is initial. In a category of protocol states ordered by reachability, a terminal state would be one uniquely reachable from every state - a strong condition that many protocols do not satisfy.

> **Definition AUTO (Product).** A **product** of $A$ and $B$ is an object $A\times B$ with projections $\pi_A:A\times B\to A$ and $\pi_B:A\times B\to B$ such that, for every $f:X\to A$ and $g:X\to B$, there is a unique $\langle f,g\rangle:X\to A\times B$ satisfying $\pi_A\langle f,g\rangle=f$ and $\pi_B\langle f,g\rangle=g$.

A Go struct with fields `A` and `B` is only a product after the relevant arrows and uniqueness law have been identified. If construction performs validation, normalization, I/O, or nondeterministic defaults, the ordinary struct intuition may fail.

> **Definition AUTO (Equalizer).** For parallel arrows $f,g:A\rightrightarrows B$, an **equalizer** is an arrow $e:E\to A$ with $f\circ e=g\circ e$, universal among arrows into $A$ on which $f$ and $g$ agree.

SessionStream example: let `storedCursor` and `derivedCursor` map traces to ordinals. Their equalizer contains exactly the traces on which the stored claim agrees with the claim derived from evidence. This detects agreement of two interpretations; it does not by itself prove either interpretation matches the product requirement.''')

insert_before('### Definition\n\nGiven arrows $f:A\to C$', r'''### The pressure: compatible pairs are not arbitrary pairs

A product combines any $a\in A$ with any $b\in B$. Many integration problems permit only pairs that make the same claim about a shared boundary. A snapshot and a buffered live batch must refer to the same session and compatible cut semantics. An authorization decision and a snapshot must refer to the same principal/session relation. The pullback is the universal object of such compatible pairs.

''')

insert_after('commutes and is universal among commuting squares over the cospan.', r'''> **Definition AUTO (Subobject).** A **subobject** of $A$ is an equivalence class of monic arrows $m:S\hookrightarrow A$, where two monics represent the same subobject when they are isomorphic over $A$. In $\mathbf{Set}$, subobjects correspond to subsets.

A predicate can therefore be represented by the inclusion of the states satisfying it. Pulling that monic back along $f:X\to A$ gives the states of $X$ whose image satisfies the predicate.

SessionStream example: valid snapshots form a subobject of all well-typed snapshot payloads. Pulling this subobject back along `loadSnapshot : Trace -> SnapshotPayload` selects traces whose loaded snapshot satisfies the consistency predicate.

> **Caution.** A subobject is not an object-oriented subclass. It is a way of sitting inside another object through a monic arrow.''')

insert_after('> **Definition 1.5.2 (Colimit).** A colimit is a cocone $(L,\iota_j)$ through which every other cocone factors by one unique arrow $L\to N$.', r'''> **Definition AUTO (Coproduct).** A **coproduct** $A+B$ has injections $\iota_A:A\to A+B$ and $\iota_B:B\to A+B$ such that every pair of arrows $f:A\to X$ and $g:B\to X$ induces a unique case-analysis arrow $[f,g]:A+B\to X$.

In typed software, a tagged sum type is the standard example. An untagged `any` is not a coproduct in the useful sense because case identity and exhaustive elimination are not preserved by its interface.

> **Definition AUTO (Coequalizer).** For parallel arrows $f,g:A\rightrightarrows B$, a **coequalizer** is an arrow $q:B\to Q$ with $q\circ f=q\circ g$, universal among arrows out of $B$ that identify every pair identified by $f$ and $g$.

This is the categorical form of quotienting by generated identifications. Stable retry identity can be modeled by asking which deliveries should become equal in a quotient of delivery attempts.

> **Definition AUTO (Pushout).** Given $f:C\to A$ and $g:C\to B$, a **pushout** is a universal cocone $A\to P\leftarrow B$ that amalgamates $A$ and $B$ while identifying the two images of $C$.

Software example: merge two schema extensions over a shared base schema. The pushout says what the least common amalgamation would be; it does not guarantee that such an amalgamation is valid in the chosen category of deployable schemas.''')

insert_after('> **Definition 1.6.1 (Exponential).** An exponential $B^A$ is an object equipped with an evaluation arrow', r'''$$
\operatorname{ev}:B^A\times A\to B
$$

such that every $f:X\times A\to B$ has a unique **transpose** or **curried form** $\lambda f:X\to B^A$ satisfying

$$
\operatorname{ev}\circ(\lambda f\times1_A)=f.
$$

> **Definition AUTO (Cartesian closed category).** A category is **cartesian closed** when it has finite products and an exponential $B^A$ for every pair of objects $A,B$.

Minimal example: in $\mathbf{Set}$, $B^A$ is the set of all functions $A\to B$. A point $1\to B^A$ corresponds to one function $A\to B$.

SessionStream example: a projector can be modeled as a point of a behavior object only when all inputs on which its behavior depends are included in $A$. A callback that reads wall-clock time or a mutable global flag is not a point of the declared $B^A$; the domain has omitted coordinates.

The definition also explains why dependency injection matters mathematically: it moves implicit environmental information into the function's explicit domain.''')
# Remove duplicated original formula immediately following exponential opening.
text=text.replace(r'''$$
\operatorname{ev}:B^A\times A\to B
$$

such that every arrow

$$
f:X\times A\to B
$$

has a unique transpose

$$
\lambda f:X\to B^A
$$

with

$$
\operatorname{ev}\circ(\lambda f\times1_A)=f.
$$
''','',1)

# ---------------- Chapter 2 ----------------
insert_before('### Faithful, full, and essentially surjective', r'''> **Definition AUTO (Faithful, full, and essentially surjective functors).** A functor $F:\mathcal C\to\mathcal D$ is **faithful** when each map
> $$
> \mathcal C(A,B)\to\mathcal D(F(A),F(B))
> $$
> is injective; **full** when each such map is surjective; and **essentially surjective** when every object of $\mathcal D$ is isomorphic to some $F(A)$.

Faithful means distinct source arrows remain distinct after interpretation. Full means every target arrow between interpreted objects comes from a source arrow. Essential surjectivity ignores harmless representation changes up to isomorphism.

SessionStream example: event-to-UI projection is intentionally non-faithful when several backend events have the same client-visible result. A serializer intended for replay should be faithful on the chosen event semantics. Neither property should be demanded without first choosing the source and target categories.''')

insert_before('### Vertical and horizontal composition', r'''> **Definition AUTO (Natural isomorphism).** A natural transformation $\eta:F\Rightarrow G$ is a **natural isomorphism** when every component $\eta_A:F(A)\to G(A)$ is an isomorphism.

A natural isomorphism is stronger than pointwise convertibility: the conversions must also commute with every modeled transition. In-memory and SQLite reducers could be naturally isomorphic after both are mapped to observable snapshot state, even if their internal audit data differs.''')

insert_before('### Functor categories', r'''> **Definition AUTO (Functor category).** When $\mathcal C$ is suitably small, the **functor category** $[\mathcal C,\mathcal D]$ has functors $\mathcal C\to\mathcal D$ as objects and natural transformations as arrows. Identities and composition are defined componentwise.

This is not merely notation. It turns whole interpretations into objects that can be compared, transformed, multiplied, and studied categorically.''')

insert_before('### Definition\n\n> **Definition 2.3.1 (Presheaf).**', r'''### Contexts and contravariance

Before defining a presheaf, we must say what is being indexed.

> **Definition AUTO (Context).** A **context** is an object of a chosen base category whose coordinates specify what information, time range, principal, version, or subsystem is available for one local observation.

Contexts are model choices. The repository does not contain a unique canonical context category.

> **Definition AUTO (Contravariant functor).** A **contravariant functor** from $\mathcal C$ to $\mathcal D$ is an ordinary functor $\mathcal C^{op}\to\mathcal D$. It reverses the direction of arrows.

If $V\to U$ means “$V$ is a smaller context contained in $U$,” contravariance produces $F(U)\to F(V)$: richer information can be forgotten.

> **Definition AUTO (Product category).** The **product category** $\mathcal C\times\mathcal D$ has pairs $(C,D)$ as objects and pairs of arrows $(f,g)$ as arrows, with identities and composition componentwise.

SessionStream contexts often combine independent coordinates such as session, cut, aspect set, version, and principal. A product category is the first model; dependencies between coordinates may require a smaller subcategory.''')

insert_after('A presheaf does **not** yet promise that compatible local data glues globally.', r'''> **Definition AUTO (Section and restriction map).** An element $s\in F(U)$ is a **section over $U$**. For $i:V\to U$, the function $F(i):F(U)\to F(V)$ is the **restriction map**. The equations $s|_U=s$ and $(s|_V)|_W=s|_W$ are the **restriction laws**.

> **Definition AUTO (Global section).** A **global section** is a section over a designated whole context $X$. Categorically, it is also a natural transformation from the terminal presheaf to $F$.

> **Definition AUTO (Morphism of presheaves).** A **presheaf morphism** $\eta:F\Rightarrow G$ is a natural transformation. It converts sections at every context and commutes with every restriction map.

Example: canonicalize a snapshot and then truncate it, or truncate first and canonicalize. A genuine presheaf morphism gives the same local snapshot both ways.''')

insert_before('### Parameter sufficiency via fibers', r'''> **Definition AUTO (Fiber).** For a function $r:X\to P$ and $p\in P$, the **fiber over $p$** is
> $$
> r^{-1}(p)=\{x\in X\mid r(x)=p\}.
> $$

A fiber collects all global completions compatible with one local observation. Empty, singleton, and many-point fibers correspond respectively to inconsistency, full determination, and underdetermination.''')

insert_after('Equivalently, when this holds for every $p$, $I$ factors through $r_P$.', r'''> **Definition AUTO (Sufficiency for an invariant).** A parameter map $r:X\to P$ is **sufficient for an invariant** $I:X\to V$ when there exists $\bar I:P\to V$ with $I=\bar I\circ r$. Equivalently, $I$ is constant on every fiber of $r$.

This is weaker and more useful than requiring parameters to reconstruct all of $X$. An authorization endpoint needs enough information to decide authorization, not enough to reproduce every session row.''')

insert_before('### Missing coordinates', r'''> **Definition AUTO (Hidden or missing coordinate).** A **hidden coordinate** is an input on which behavior depends but which is absent from the declared context or function domain. A model has a **missing coordinate** when two executions represented by the same modeled point can produce observably different results because of that omitted input.

The first repair is to enrich the base or remove the dependency, not to search for a topological obstruction.''')

# Add a new, pedagogical Section 2.4 before checkpoint.
marker='## Chapter 2 student checkpoint'
newsec=r'''## 2.4 Bundles, Germs, Stalks, Representables, and Yoneda

Presheaves are often introduced through open sets, but Goldblatt also presents the complementary bundle picture. This section supplies that bridge and then introduces representable presheaves and the Yoneda viewpoint. The common theme is that an object can be understood through the observations available over or into it.

### Bundles and sections

The pressure is simple: a context may have a different set of possible values at each point. A global product $X\times A$ assumes the same value set everywhere. A bundle allows the fibers to vary.

> **Definition AUTO (Bundle and fiber).** A **bundle of sets over $X$** is a function $p:E\to X$. For $x\in X$, the **fiber** over $x$ is $E_x=p^{-1}(x)$. A **section** over $U\subseteq X$ is a function $s:U\to E$ satisfying $p\circ s=1_U$.

Minimal example: take $E=X\times A$ and $p(x,a)=x$. Every fiber is a copy of $A$, and sections are ordinary functions $U\to A$.

SessionStream example: let the base points be session cuts. The fiber over cut $n$ may contain all timeline states admissible at $n$. A section chooses one state at each cut while respecting whatever continuity or transition law the bundle model imposes.

Caution: the total space $E$ is not automatically the runtime heap. It is a mathematical collection of possible local values.

### Germs and stalks

Two sections may differ globally but agree near one point. Sheaf theory records this local agreement without requiring a globally fixed neighborhood.

> **Definition AUTO (Germ).** Let $F$ be a presheaf on open sets of a topological space and let $x\in X$. Two pairs $(U,s)$ and $(V,t)$ with $x\in U,V$ define the same **germ at $x$** when there is a neighborhood $W\subseteq U\cap V$ of $x$ such that $s|_W=t|_W$.

> **Definition AUTO (Stalk).** The **stalk** $F_x$ is the set of germs at $x$. It is the colimit of the sets $F(U)$ over neighborhoods $U$ of $x$ ordered by reverse inclusion.

Minimal example: two real-valued functions have the same germ at $x$ if they agree on some neighborhood of $x$, even if they differ elsewhere.

Software analogy: two long traces can have the same local behavior around an event boundary. A stalk-like construction forgets how that behavior was extended far away. Use the analogy carefully: logs do not carry a topology until neighborhoods and restrictions have been explicitly chosen.

### Representables and generalized elements

A presheaf can also arise from probes into a context.

> **Definition AUTO (Representable presheaf).** For an object $U$ of $\mathcal C$, the **representable presheaf** $yU$ is
> $$
> yU(V)=\mathcal C(V,U),
> $$
> with restriction by precomposition. The assignment $U\mapsto yU$ is the Yoneda embedding.

> **Definition AUTO (Generalized element).** A **generalized element of $U$ at stage $V$** is an arrow $V\to U$, equivalently an element of $yU(V)$.

In $\mathbf{Set}$, ordinary elements of $U$ are arrows $1\to U$ from a singleton. Generalized elements allow the “element” to vary over a stage.

SessionStream example: a probe $V\to U$ can mean that a smaller test context embeds into a richer observation context. The family of all such probes reveals how $U$ behaves under restriction, authorization, versioning, and time truncation.

### Yoneda, stated for use

> **Theorem (Yoneda lemma, working form).** For a presheaf $F:\mathcal C^{op}\to\mathbf{Set}$ and an object $U$, there is a natural bijection
> $$
> \operatorname{Nat}(yU,F)\cong F(U).
> $$
> A section over $U$ is exactly the same information as a natural rule that assigns compatible $F$-data to every probe into $U$.

This is not a slogan that “everything is its API.” The probes must be all arrows of the chosen category, and compatibility with precomposition is essential.

Worked SessionStream example: a snapshot section $s\in\mathsf{State}(U)$ determines, for every probe $v:V\to U$, the restricted snapshot $s|_V$. Conversely, a natural family of probe responses determines the section at the identity probe $1_U:U\to U$. Naturality forces every other response to be its restriction.

Engineering use: design an interface by asking which probes distinguish the states that matter. If two candidate states give the same response to every available probe, the interface cannot distinguish them. Add a probe or accept the quotient.

### Exercises

**Exercise 2.4.1. Bundle section.** Model timeline states over cut ordinals as a bundle. What condition would make a chosen family of states a lawful section rather than an arbitrary selection?

**Exercise 2.4.2. Germ equivalence.** Give three traces $a,b,c$ and neighborhoods of a cut such that $a$ and $b$ have the same germ, $b$ and $c$ have the same germ, and verify transitivity.

**Exercise 2.4.3. Representable restrictions.** For $yU(V)=\mathcal C(V,U)$, prove the two presheaf restriction laws using associativity and identities.

**Exercise 2.4.4. Yoneda reconstruction.** Starting from $\alpha:yU\Rightarrow F$, show that the corresponding section is $\alpha_U(1_U)$ and derive every component from it.

**Exercise 2.4.5. Probe insufficiency.** Design two SessionStream states that all current client-facing probes identify. Name a new probe that would distinguish them.

**Exercise 2.4.6. Analogy boundary.** Explain why “the state near ordinal $n$” does not define a germ until a neighborhood system and restriction maps have been specified.
'''
insert_before(marker,newsec)

# ---------------- Chapter 3 ----------------
start=text.index('### Covers', text.index('## 3.1 Sheaves'))
end=text.index('### The limit/equalizer form', start)
replacement=r'''### Covers, overlaps, and matching data

A local-to-global theorem needs a declaration of which local contexts collectively count as the whole.

> **Definition AUTO (Cover).** A **cover** of $U$ is a family of arrows $\{u_i:U_i\to U\}$ declared to be jointly sufficient according to a chosen coverage. For open sets this means $U=\bigcup_iU_i$. On a general category it is extra structure, developed as a site in Section 3.3.

> **Definition AUTO (Overlap).** The **overlap** of $U_i\to U$ and $U_j\to U$ is their pullback $U_i\times_UU_j$, when it exists. It is the context in which the information supplied by both pieces can be compared.

A database join key is not by itself an overlap. The overlap object must carry exactly the common semantic information and satisfy the pullback universal property in the chosen category.

> **Definition AUTO (Matching family).** For a presheaf $F$ and a cover $\{U_i\to U\}$, a family $s_i\in F(U_i)$ is **matching** or **compatible** when the two restrictions of $s_i$ and $s_j$ to every overlap $U_i\times_UU_j$ agree.

> **Definition AUTO (Amalgamation or gluing).** An **amalgamation** of a matching family is a section $s\in F(U)$ whose restriction to every $U_i$ is $s_i$.

The three possible outcomes are now distinct:

1. the local pieces disagree on an overlap, so the family is not matching;
2. the family matches but has no amalgamation;
3. the family has one or several amalgamations.

> **Definition AUTO (Separated presheaf).** A presheaf is **separated** for the coverage when a matching family has at most one amalgamation.

> **Definition AUTO (Sheaf and COM).** A presheaf is a **sheaf** when every matching family over every declared cover has exactly one amalgamation. Goldblatt calls this compatibility-and-amalgamation requirement **COM**.

The sheaf condition therefore contains two claims:

- **existence:** compatible local data comes from some global section;
- **uniqueness:** compatible local data determines at most one global section.

Minimal example: ordinary functions on open sets form a sheaf. Functions agreeing on overlaps define one function on the union.

SessionStream example: a sound snapshot at cut $n$ and a complete live suffix after $n$ form local sections on two temporal pieces. They match when session, version, reducer semantics, and boundary ordinals agree. They glue when they reconstruct one client state through cut $m$.

Non-example: a digest-only presheaf may be separated or may fail uniqueness depending on whether distinct global states can share all local digests. Hash agreement is not automatically semantic agreement.

'''
text=text[:start]+replacement+text[end:]

insert_before('### A SessionStream matching family', r'''> **Definition AUTO (Descent data).** **Descent data** consists of local objects or sections together with specified identifications on overlaps satisfying compatibility on higher overlaps. A descent problem asks whether this data comes from one object over the whole context.

For set-valued sheaves, descent data reduces to matching sections. For schemas, modules, databases, or richer categorical objects, the overlap comparison may be an isomorphism rather than literal equality.

SessionStream use: versioned projection states may need migration isomorphisms on overlaps and a coherence condition on triple overlaps. That is richer than comparing JSON values.''')

insert_before('### Canonical prefixes and reducers', r'''> **Definition AUTO (Reducer).** A **reducer** is a deterministic transition function
> $$
> R:T\times E\to T
> $$
> together with an initial state $t_0$. Its fold over an event sequence is written $\operatorname{fold}_R(t_0,-)$.

The environment and version on which reduction depends must be included in $T$, $E$, or an explicit parameter. Otherwise the word deterministic hides a missing coordinate.''')

insert_before('### Snapshot soundness', r'''> **Definition AUTO (Snapshot soundness).** A snapshot $S_n$ is **sound at cut $n$** for reducer $R$ when decoding it yields exactly the state obtained by reducing the canonical prefix through $n$:
> $$
> \operatorname{decode}(S_n)=\operatorname{fold}_R(t_0,E_n).
> $$

Local well-typedness is weaker. An entity with `LastEventOrdinal > SnapshotOrdinal` can be well typed and still violate soundness.''')

insert_before('### The temporal cover', r'''> **Definition AUTO (Suffix completeness).** A delivered suffix $L_{(n,m]}$ is **complete after cut $n$ through $m$** when it contains every canonical event effect required to advance the client from $n$ to $m$, in order, with no required event omitted.

> **Definition AUTO (Boundary compatibility).** A snapshot and suffix are **boundary-compatible** when they refer to the same session and semantic version, the snapshot includes effects through exactly its cut, and the suffix begins strictly after that cut under one explicit ordinal convention.

These definitions separate three bugs that are often conflated: an unsound snapshot, an incomplete suffix, and a duplicate or ambiguous boundary event.''')

# Enrich sites before existing pretopology definition.
insert_before('### Pretopology axioms', r'''A topology on a physical space already tells us which open families cover an open set. On an arbitrary category, “enough local contexts” is not intrinsic. It must be declared and constrained.

> **Definition AUTO (Pretopology).** A **pretopology** assigns to every object $U$ certain families $\{U_i\to U\}$ called covers, satisfying identity coverage, transitivity of coverage, and stability under pullback.

> **Definition AUTO (Site).** A **site** is a category equipped with a pretopology or, more generally, a Grothendieck topology.

The category says which contexts and refinements exist. The coverage says which families are entitled to support local-to-global reasoning. Conflating these two choices hides assumptions.''')
# Existing pretopology definition is duplicate; keep as formal elaboration but rename heading.
text=text.replace('### Pretopology axioms\n\n> **Definition 3.3.1 (Coverage basis / pretopology).**','### The three coverage axioms\n\n> **Definition AUTO (Coverage basis / pretopology, expanded).**',1)

insert_before('### Grothendieck topologies and sieves', r'''> **Definition AUTO (Sieve).** A **sieve** $S$ on $U$ is a collection of arrows into $U$ closed under precomposition: if $f:V\to U$ lies in $S$ and $g:W\to V$ is any arrow, then $f\circ g$ lies in $S$.

A sieve records all refinements through which a body of evidence remains available.

> **Definition AUTO (Grothendieck topology).** A **Grothendieck topology** assigns to each object $U$ a collection of covering sieves satisfying maximality, pullback stability, and local character. A category equipped with one is a site.

A covering family generates a sieve by closing its arrows under precomposition. Sieve language is especially useful in Chapter 4 because truth values in a presheaf topos are sieves.''')

# Reorder 3.4 and 3.5: Adjunctions before repair.
ch3_start=text.index('## 3.4 Repairing Local-to-Global Failure')
repair_start=ch3_start
adj_start=text.index('## 3.5 Adjunctions and Change of Context',repair_start)
checkpoint=text.index('## Chapter 3 student checkpoint',adj_start)
repair=text[repair_start:adj_start]
adj=text[adj_start:checkpoint]
# relabel internal references/labels carefully
repair=repair.replace('## 3.4 ','## 3.5 ',1)
repair=re.sub(r'\b(Definition|Exercise|Section) 3\.4\.',r'\1 3.5.',repair)
adj=adj.replace('## 3.5 ','## 3.4 ',1)
adj=re.sub(r'\b(Definition|Exercise|Section) 3\.5\.',r'\1 3.4.',adj)
text=text[:repair_start]+adj+'\n\n'+repair+text[checkpoint:]
# references in the rest
text=text.replace('in Section 3.5.', 'in Section 3.4.')

# Add local equivalence definition in repair.
insert_before('### Local equivalence and observability', r'''> **Definition AUTO (Local equivalence).** A map of presheaves is a **local equivalence** when it becomes an isomorphism after passage to the chosen local/sheaf semantics; informally, it may change presentation while preserving all information detectable on an adequate cover.

For software this is a demanding phrase. It requires an explicit site and observation notion. Two implementations are not locally equivalent merely because current tests do not distinguish them.''')

# ---------------- Chapter 4 ----------------
insert_before('### Elementary topos', r'''The pressure now changes. We no longer study one presheaf in isolation. We study a whole category of context-dependent sets and coherent transformations. The claim that this category has a logic comes from its universal constructions, not from a metaphor about “truth in distributed systems.”

> **Definition AUTO (Small category).** A category is **small** when its objects and arrows form sets rather than proper classes. This size condition ensures the ordinary presheaf category $[\mathcal C^{op},\mathbf{Set}]$ can be formed without additional foundational machinery.''')

insert_before('### Subobjects as predicates', r'''> **Definition AUTO (Grothendieck topos).** A **Grothendieck topos** is a category equivalent to the category of sheaves of sets on some site. Every presheaf category on a small category is a Grothendieck topos, using the coverage in which only maximal/identity-generated covers are required.

Elementary topos is an axiomatic internal characterization. Grothendieck topos emphasizes presentation as sheaves on a site. The two notions overlap but are not identical in scope.''')

insert_before('### Subobjects as predicates', r'''> **Definition AUTO (Subobject, revisited).** A **subobject** of $A$ is represented by a monic $m:S\hookrightarrow A$, modulo isomorphism over $A$. It plays the role of a predicate on generalized elements of $A$: those that factor through $m$ satisfy the predicate.''')

insert_after('> **Definition 4.1.2 (Subobject classifier).** A subobject classifier is an object $\Omega$ with an arrow', r'''$$
\mathsf{true}:1\to\Omega
$$

such that every monic $m:S\hookrightarrow A$ is, up to isomorphism, the pullback of $\mathsf{true}$ along a unique arrow $\chi_m:A\to\Omega$.

The arrow $\mathsf{true}$ is the **truth arrow**. The unique $\chi_m$ is the **characteristic** or **classifying map** of the predicate.

A **global element** of an object $A$ is an arrow $1\to A$. Thus a global truth value is a global element $1\to\Omega$.

Minimal example: in $\mathbf{Set}$, $\Omega=\{0,1\}$ and $\chi_S(a)=1$ exactly when $a\in S$.

SessionStream example: let $A$ be the presheaf of typed snapshot observations and $S$ the subpresheaf of sound snapshots. Its classifier records, at each context, the refinements on which the observation can be established to lie in $S$. This is generally richer than a Boolean.''')
# Remove duplicate original classifier formula block if present.
text=text.replace(r'''$$
\mathsf{true}:1\to\Omega
$$

such that every monic

$$
m:S\hookrightarrow A
$$

is a pullback of $\mathsf{true}$ along a unique characteristic arrow

$$
\chi_m:A\to\Omega.
$$
''','',1)

insert_before('### Power objects', r'''> **Definition AUTO (Truth value).** A **truth value** at stage $U$ is an element of the classifier $\Omega(U)$. In a presheaf topos this is a sieve on $U$, not merely `true` or `false`.

The sieve contains exactly the refinements $V\to U$ at which the proposition becomes established. The empty sieve is nowhere established; the maximal sieve is established at the current stage and all refinements.''')

insert_before('### Presheaf topos versus sheaf topos', r'''> **Definition AUTO (Power object).** A **power object** $PA$ represents subobjects of $A$ in the same way that a power set represents subsets in $\mathbf{Set}$. It is characterized by a membership subobject $\in_A\hookrightarrow A\times PA$ universal among predicates on $A$ parameterized by another object.

Software reading: a power object is a space of context-dependent predicates, not a runtime list of every subset. The universal property matters more than enumeration.''')

# Remove duplicate Yoneda block from Ch4 because now in Ch2.
ys=text.find('### Yoneda interlude: know an object by its probes')
ye=text.find('### Internal objects are not global structs',ys)
if ys!=-1 and ye!=-1:
    text=text[:ys]+text[ye:]

insert_before('### Stages and generalized elements', r'''> **Definition AUTO (Stage and generalized element).** A **stage** is a context object $U$ at which a statement is evaluated. A **generalized element of $A$ at stage $U$** is an arrow $U\to A$.

This replaces the assumption that every value is globally available as a point $1\to A$. A snapshot observation may exist at a session/cut/principal stage without extending to one global snapshot for all stages.''')

insert_before('### Forcing notation', r'''> **Definition AUTO (Forcing or local truth).** The notation
> $$
> U\Vdash\varphi
> $$
> reads “$\varphi$ is true at stage $U$.” Its clauses are defined recursively from the topos semantics. In presheaf and sheaf models, truth must be stable under refinement: if $U\Vdash\varphi$ and $V\to U$, then $V\Vdash\varphi$.

Operational evidence is therefore monotone in the chosen refinement order. If adding detail can invalidate a claim, the order or proposition has been modeled incorrectly.''')

insert_before('### Why excluded middle can fail', r'''> **Definition AUTO (Intuitionistic logic).** **Intuitionistic logic** does not infer $\varphi\vee\neg\varphi$ without evidence for one side. A proof of a disjunction identifies a supported disjunct; a proof of existence supplies a witness locally according to the semantics.

For a distributed trace, “the client received event $e$ or did not receive $e$” may be classically true externally while neither disjunct is established at the current observation stage. Unknown is not false.''')

insert_before('### Geometric reasoning', r'''> **Definition AUTO (Internal and external reasoning).** **External reasoning** is mathematics carried out about the topos from the surrounding metatheory. **Internal reasoning** uses the topos's own language, treating its objects as variable sets and its arrows as functions.

A formula proved internally is automatically stable under the relevant substitution and context semantics. An external database query may use implementation facts not represented internally.''')

insert_before('### Internal language as specification notation', r'''> **Definition AUTO (Geometric formula).** A **geometric formula** is built from atomic formulas using finite conjunction, arbitrary disjunction, and existential quantification. Geometric formulas are preserved by inverse-image parts of geometric morphisms, which makes them robust under many changes of context.

This does not mean every safety property is geometric. Negation, unrestricted implication, and universal quantification require separate care.''')

# Nerve definitions.
insert_before('### Simplicial complexes', r'''> **Definition AUTO (Simplex).** An **$n$-simplex** is the abstract combinatorial analogue of a point ($n=0$), edge ($n=1$), filled triangle ($n=2$), tetrahedron ($n=3$), and their higher-dimensional continuations. Its faces are obtained by deleting vertices.

> **Definition AUTO (Simplicial complex).** A **simplicial complex** is a set of finite vertex sets closed under taking subsets. If a simplex is present, all its faces are present.

The dimension records the order of joint compatibility: vertices are individual contexts, edges are pairwise overlaps, triangles are triple overlaps with one joint witness, and higher simplices represent higher-order joint contexts.''')

insert_before('### The Čech nerve', r'''> **Definition AUTO (Cech nerve).** Given a cover $\{U_i\to U\}$ with iterated pullbacks, the **Cech nerve** has degree-$n$ objects formed from $(n+1)$-fold overlaps
> $$
> U_{i_0}\times_U\cdots\times_UU_{i_n},
> $$
> with face maps that forget one factor and degeneracy maps that repeat one.

The ordinary nerve records which overlaps exist. The Cech nerve retains the overlap objects and maps themselves, which is the structure needed for descent and cohomology.''')

insert_before('### Two ways a hole can disappear', r'''> **Definition AUTO (Combinatorial hole).** Informally, a **hole** is a cycle of lower-dimensional simplices that is not the boundary of higher-dimensional simplices already present. The precise invariant depends on homology or cohomology and the chosen coefficients.

A square of pairwise contracts may look like a loop because no component witnesses all four facts jointly. Adding a transaction can add a higher-dimensional witness; changing the base contexts can instead identify vertices or edges. These are mathematically different repairs.''')

# Cohomology formal bridge.
insert_before('### Cochains', r'''### Algebra needed for the quotient

Cohomology is not defined for arbitrary payloads by writing subtraction signs next to them.

> **Definition AUTO (Group and abelian group).** A **group** is a set with an associative binary operation, an identity, and inverses. It is **abelian** when the operation is commutative.

> **Definition AUTO (Homomorphism, kernel, and image).** A **group homomorphism** preserves the group operation. Its **kernel** is the subgroup mapped to zero; its **image** is the subgroup of attained outputs.

> **Definition AUTO (Quotient group).** For an abelian group $A$ and subgroup $B$, the **quotient** $A/B$ identifies elements of $A$ that differ by an element of $B$.

Cursor offsets form an abelian group under addition. Arbitrary protobuf messages do not.

> **Definition AUTO (Coefficient system).** A **coefficient system** assigns an abelian group or vector space to the cells of the chosen shape, together with compatible restriction maps. Constant coefficients assign the same group to every cell with identity restrictions.''')

insert_before('### The coboundary', r'''> **Definition AUTO (Cochain).** An **$n$-cochain** assigns a coefficient value to every oriented $n$-simplex or, for a cellular sheaf, chooses an element of the stalk on every $n$-cell. The group of such assignments is $C^n$.

A $0$-cochain is a set of local calibrations. A $1$-cochain is a set of edge discrepancies. Neither is automatically consistent.''')

insert_before('### Cocycles, coboundaries, and cohomology', r'''> **Definition AUTO (Coboundary operator).** The **coboundary operator** $\delta^n:C^n\to C^{n+1}$ computes the signed incompatibility of an $n$-cochain around each $(n+1)$-cell, using restriction maps where coefficients vary. It satisfies $\delta^{n+1}\delta^n=0$.

For a vertex assignment $x$, $(\delta^0x)_{i\to j}=x_j-x_i$. For an edge assignment on a filled triangle, $\delta^1$ computes circulation around the face.''')

insert_before('### Cursor calibration example', r'''> **Definition AUTO (Cocycle, coboundary, and cohomology).** An $n$-cochain $c$ is a **cocycle** when $\delta^nc=0$. It is a **coboundary** when $c=\delta^{n-1}b$ for some $(n-1)$-cochain $b$. The **$n$-th cohomology group** is
> $$
> H^n=\ker\delta^n/\operatorname{im}\delta^{n-1}.
> $$

Closed means no higher-cell inconsistency is detected. Exact means the cochain is fully explained by changing lower-dimensional local coordinates. Cohomology classes are closed patterns modulo such coordinate changes.

For an additive sheaf, $H^0=\ker\delta^0$ is the group of globally compatible local assignments. $H^1$ records closed edge-discrepancy patterns not arising from vertex calibrations. These interpretations depend on the chosen coefficient system.''')

insert_before('### A small calculation', r'''> **Definition AUTO (Cellular sheaf, brief).** A **cellular sheaf** on a cell complex assigns a vector space or abelian group to every cell and a restriction map from each face to each containing cell, satisfying identity and composition laws. Its cochain complex uses these stalks and restrictions instead of constant coefficients.

Architecture use: a vertex stalk may store a component's cursor coordinate, an edge stalk the shared boundary coordinate, and restriction maps the translation each endpoint uses. Global sections are vertex assignments whose translated values agree on every edge.''')

# Clean outdated cross-references inherited from old chapter numbering.
old_to_new={17:'4.3',18:'4.4',19:'4.5',20:'4.6',14:'4.1',15:'4.2',16:'3.4',13:'3.5',12:'3.3',11:'3.2',10:'3.1',9:'2.3',8:'2.2',7:'2.1',6:'1.6',5:'1.5',4:'1.4',3:'1.3',2:'1.2',1:'1.1'}
for old,new in old_to_new.items():
    text=re.sub(rf'\bSection {old}\.(\d+)\b',f'Section {new}',text)
# Specific prose cleanup.
text=text.replace('Section 18.10','the cursor-calibration example in Section 4.4')
text=text.replace('Section 17.3','Section 4.3')

# Fix solution appendix over-numbering produced in first pass.
text=re.sub(r'Exercise (\d+\.\d+)\.\d+\.(\d+)',r'Exercise \1.\2',text)
text=re.sub(r'^### Section 1\.1\.1', '### Section 1.1', text, flags=re.M)

# Standardize all definition numbering section-by-section.
lines=text.splitlines()
current=None
counts={}
out=[]
pat=re.compile(r'^> \*\*Definition(?:\s+(?:AUTO|[0-9.]+))?(?:\s+\((.*?)\))?\.\*\*(.*)$')
for line in lines:
    msec=re.match(r'^## (\d+\.\d+)\s',line)
    if msec:
        current=msec.group(1)
    m=pat.match(line)
    if m and current:
        counts[current]=counts.get(current,0)+1
        title=m.group(1)
        rest=m.group(2)
        label=f'> **Definition {current}.{counts[current]}'
        if title:
            label+=f' ({title})'
        label+='.'+'**'+rest
        line=label
    out.append(line)
text='\n'.join(out)+'\n'

# Normalize headings of sections after reorder in roadmap/reference prose.
text=text.replace('## 3.4 Adjunctions and Change of Context','## 3.4 Adjunctions and Change of Context')
text=text.replace('## 3.5 Repairing Local-to-Global Failure','## 3.5 Repairing Local-to-Global Failure')

Path('/mnt/data/work_v2/second-draft.md').write_text(text)
print('second draft',len(text.split()),'words',len(text.splitlines()),'lines')
print('definitions',sum(counts.values()),counts)
PY
python /mnt/data/work_v2/pedagogy_pass.py
wc -l -w -c /mnt/data/work_v2/second-draft.md
grep -n '^# ' /mnt/data/work_v2/second-draft.md
grep -nE '^> \*\*Definition' /mnt/data/work_v2/second-draft.md | tail -20
```

The student audit is complete, with prerequisites defined before use and cohomological obstructions separated from simpler failures. I’m fixing final PDF navigation and boundary artifacts before preflight.

<details><summary>💭 Thinking</summary>

**Audited and cleaned manuscript formatting, definitions, references, and appendices**

</details>

```unknown
bash -lc cd /mnt/data/work_v2 && pandoc final-manuscript.md -o local-truth-global-behavior.pdf --pdf-engine=xelatex --toc --number-sections --metadata linkcolor=linkblue --metadata urlcolor=linkblue 2>pandoc.log; status=$?; echo STATUS=$status; tail -80 pandoc.log; ls -lh local-truth-global-behavior.pdf
```

<details><summary>💭 Thinking</summary>

**Compiled manuscript PDF and inspected YAML indentation**

**Preparing final files**

I’m fixing the manuscript’s formatting metadata, then I’ll compile the polished four-chapter text into Markdown and PDF and perform a final readability check.

**Prepared final files**

</details>

```unknown
bash -lc cat /home/oai/skills/pdfs/SKILL.md && printf '\n---FILES---\n' && ls -l /mnt/data/work_v2 /mnt/data | sed -n '1,160p'
```

<details><summary>💭 Thinking</summary>

**Inspected, fixed, compiled, and audited the final manuscript PDF deliverables**

</details>

# Revised textbook

- [Download the Markdown source](sandbox:/mnt/data/local-truth-global-execution-sessionstream.md)
- [Download the typeset PDF](sandbox:/mnt/data/local-truth-global-execution-sessionstream.pdf)

## **Local Truth, Global Execution**

The new edition is organized as four sustained chapters:

1. **What Counts as One Coherent State?**  
   Categories, arrows, commutative diagrams, universal properties, products, equalizers, limits, pullbacks, transactional witnesses, parameter sufficiency, and exponentials.

2. **What Can Be Known from Each Context?**  
   Functors, natural transformations, opposite categories, context categories, presheaves, restriction maps, sections, fibers, missing coordinates, representables, and Yoneda.

3. **When Do Compatible Local Views Determine a Whole?**  
   Covers, pretopologies, sites, matching families, amalgamations, the sheaf condition, SessionStream hydration as gluing, sheafification, topoi, subobject classifiers, sieves, and contextual truth.

4. **What Shape Remains When Local Data Does Not Glue?**  
   Nerves, simplicial complexes, coefficient systems, cochains, coboundaries, $H^0$, $H^1$, cursor holonomy, cellular sheaves, obstruction diagnostics, and the proposed `ss-sheafcheck` tool.

The second-pass rewrite treats definitions in a consistent sequence:

$$
\text{engineering need}
\rightarrow
\text{ordinary set example}
\rightarrow
\text{formal definition}
\rightarrow
\text{multiple applications}
\rightarrow
\text{counterexample or failure mode}
\rightarrow
\text{exercises}.
$$

It contains approximately **22,000 words**, **96 pages**, **54 numbered definitions**, **95 exercises**, selected hints and solutions, a definition-dependency map, a failure-to-concept index, and a twelve-week parallel study route. The PDF is searchable, bookmarked, uses embedded fonts, and was rendered and visually inspected across all pages.

