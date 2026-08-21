# Abstraction vs Elegance

- URL: https://chatgpt.com/c/6a7cdd77-17d0-83ea-bc4e-799296873211
- Created: 2026-08-12T20:54:24.112Z

---

> I don't like this for some reason, explain

I think the discomfort comes from a mismatch between how elegant the **idea** is and how heavy the **resulting abstraction** feels.

The opening principle is strong: local replicas accumulate facts/evidence under partial knowledge, while authoritative systems later resolve the non-monotone parts. fileciteturn0file0L1-L5 But the design then tries to encode almost every distributed-systems concept directly into the DSL. That makes it feel more like a distributed-systems taxonomy rendered as JavaScript than a natural programming model.

A few things are probably causing that feeling:

- **The abstraction level keeps shifting.** `input`, `read`, `derive`, `check`, `decide` are workflow/dataflow concepts. `reserve` is an invariant/escrow concept. `append` is a storage concept. `effect` is runtime execution. `reconcile` is lifecycle orchestration. fileciteturn0file0L181-L195 They don't feel like peers, yet the API presents them as peers.

- **The theory is leaking too directly into application code.** `whenAuthoritative`, `offlineAs("unknown")`, `using("bounded-counter")`, `merge("op-set")`, and explicit compensation expose implementation strategy everywhere. For example, the refund flow requires the application author to know that the exposure mechanism happens to be a bounded counter. fileciteturn0file0L250-L278 A developer probably wants to state the constraint—“I may issue at most $X of offline refund liability”—and let the runtime/compiler choose the mechanism.

- **There is too much ceremony around a simple business statement.** The core return rule is roughly: validate what you can; reject known failures; if required facts are unavailable, allow a bounded provisional return; reconcile later. But expressing that requires a large graph containing checks, reservations, dispositions, claims, ledger mutations, effects, forwarding, callbacks, and compensation. fileciteturn0file0L284-L378 The architecture is sophisticated, but the user-facing code doesn't compress that sophistication.

- **`Unknown` is good; `Disposition` feels artificial.** Making `unknown` distinct from `fail` is one of the strongest parts. fileciteturn0file0L202-L219 But then `reject | accept | provisional` gets elevated into a generic primitive. That's really return-domain policy. Another workflow could need `approve/review/escalate`, `commit/defer`, or something else entirely. The generic IR probably shouldn't know what a “business disposition” is.

- **The DSL mixes description with execution sequencing.** `.after(claim, exposure)`, `.when(...)`, `.handler(...)`, `.idempotencyKey(...)`, `.untilAcknowledged()`, `.onAccepted()`, and `.onRejected()` gradually turn the declarative DAG into a fluent workflow engine. The graph stops feeling like an IR builder and starts feeling like a custom Temporal/Step Functions-style orchestration language.

- **`forward`/`reconcile` is particularly awkward.** The conceptual primitive list says `reconcile`, while the example API actually uses `$.forward("reconcile", ...)`. fileciteturn0file0L181-L195 fileciteturn0file0L352-L378 That's a small naming inconsistency, but it points at a deeper uncertainty: is reconciliation an operation, a phase, a subgraph, or simply another execution of the same graph when new knowledge arrives?

- **The compiler is being asked to understand more than the IR visibly proves.** The proposed static error—“Non-monotone dependency crosses an irreversible effect”—is excellent as a product goal. fileciteturn0file0L583-L615 But terms like `requires: "authoritative"`, `provisional`, `compensatable`, and `bounded risk reservation` need a rigorous type/effect system underneath them. Right now the fluent syntax makes that rigor look somewhat declarative-by-convention.

The biggest issue, though, is that **the abstraction centers the mechanism rather than the guarantee**.

The really interesting thing you're building isn't:

> read → check → reserve → decide → append → effect → reconcile

It's closer to:

> **Here is a decision I want to make. Here are the facts it depends on. Here is what I'm allowed to conclude when some facts are unavailable. Here are the invariants that must remain true.**

Then the compiler should derive whether that decision can execute locally, needs a capability, must remain provisional, or requires coordination.

That inversion would make the DSL substantially cleaner. Instead of the programmer explicitly writing:

```js
.using("bounded-counter")
.otherwiseFail("OFFLINE_LIMIT_EXCEEDED")
```

they might declare something conceptually like:

```js
refund.amount <= offlineRefundAuthority
```

and the system determines that `offlineRefundAuthority` must be a partitionable/escrowed resource if offline execution is required.

Likewise, rather than manually constructing `accept / reject / provisional`, you could have the graph produce an ordinary domain result, while the compiler separately tracks the **certainty** of that result:

```text
value: AcceptReturn
certainty: provisional
missing: [currentReturnState]
```

That feels much closer to the genuinely powerful observation already buried near the end: a provisional offline operation is effectively a **proof-carrying deferred command**. fileciteturn0file0L623-L676

I suspect *that* is the abstraction you like, while the nine-primitive workflow DSL around it is what feels wrong.


---

> No, take a step back and reason through it as if you were peter norvig and leslie lamport combined

<details><summary>💭 Thinking</summary>

**Reframing the model**

I’m separating world state, local knowledge, and actions. A DAG may describe dependencies, but reconciliation creates temporal cycles, so event histories and state-transition rules seem more fundamental. “Unknown” represents incomplete knowledge, not necessarily a third truth value.

**Reframed the model**

</details>

The deeper issue is not the fluent syntax. It is that the design starts from **dataflow**, while the problem is fundamentally about **state-machine safety under incomplete histories**.

<details><summary>💭 Thinking</summary>

**Formalizing decisions**

I’m refining the idea around sets of possible worlds: a check passes only when an invariant holds in every state consistent with local knowledge. Otherwise, I’m deferring, narrowing authority, or marking the action provisional.

**Formalized decisions**

</details>

The sentence I would challenge first is **“That maps cleanly to a DAG IR.”**  A DAG can describe dependencies *inside one computation*. It is a poor primary model for a protocol that retries, receives later information, consumes authority, compensates, and continues indefinitely.

Yes. Taking the problem from first principles, I think the unease is more fundamental than the API shape.

The key wrong turn is here:

> local replica accumulates knowledge → therefore model the program as a DAG of knowledge-producing operations. fileciteturn0file0L1-L5

That is not quite the problem you have.

## The system is not fundamentally a DAG

A distributed retail system under partition is a collection of **state machines executing concurrently**.

A store doesn't merely compute a value from incomplete inputs. It changes the world:

- it gives someone money,
- consumes some authority,
- records a claim,
- another store may simultaneously do the same thing,
- messages later arrive,
- new transitions become enabled,
- some previous economic consequence may have to be counteracted.

Those are behaviors over time.

A DAG is useful for something much narrower: the dependency graph of expressions evaluated during one transition. It may be an excellent *compiled artifact*. It should not be the semantic foundation.

The semantic foundation should be closer to:

$$
S_0 \xrightarrow{a_1} S_1 \xrightarrow{a_2} S_2 \xrightarrow{} \cdots
$$

with many replicas independently taking transitions and exchanging messages.

That immediately changes how I would think about the whole design.

---

## There are actually two different problems being conflated

The document begins with an epistemic argument:

$$
K \subseteq K'
$$

and says that conclusions safe under increasing knowledge are particularly useful offline. fileciteturn0file0L9-L36

That's correct as far as it goes.

But there are **two axes**, not one:

$$
\text{knowledge changes}
$$

and

$$
\text{the world changes}.
$$

Those are profoundly different.

Suppose store A has authoritative knowledge at 12:00 that an item has not been returned.

At 12:01, store B returns it.

Store A's old statement wasn't merely based on *insufficient knowledge*. The relevant state of the world has changed.

So:

```text
unknown → known
```

is one phenomenon.

But:

```text
true → false because another process acted
```

is another.

The current design puts a tremendous amount of weight on `Knowledge<T>`, `unknown`, `whenKnown`, and `whenAuthoritative`. fileciteturn0file0L202-L219

But an authoritative read is not an authority to act.

That's an extremely important distinction.

Knowing:

```text
remainingRefundableQuantity = 1
```

does not give me the right to consume that 1 while disconnected.

What I need is something like:

```text
rightToRefund(item, quantity=1)
```

Those are completely different objects.

One is information.

The other is authority.

---

# I would therefore start with safety, not knowledge

Forget the DSL for a moment.

Suppose there is some global invariant:

$$
I(S)
$$

where $S$ is the conceptual global state.

Examples:

$$
\text{total offline refund exposure} \le \$10,000
$$

or

$$
\text{each unique refund token is consumed at most once}
$$

or

$$
\text{inventory} \ge 0.
$$

Now ask:

> **Which state transitions may a replica perform while isolated such that arbitrary permitted concurrent execution cannot violate $I$?**

That is the central question.

Not:

> Is this read known?

Not:

> Is this computation monotone?

Not even:

> Can this CRDT merge?

Those are tools for answering the question.

The real object you're designing is the set of **admissible uncoordinated transitions**.

And this is why the bounded-counter section feels more fundamental than most of the surrounding DSL. The document correctly observes that two replicas can converge perfectly while violating the business invariant, and that preallocated rights can make certain operations safe. fileciteturn0file0L88-L119

That's not an escape hatch.

I think that's the center of the model.

---

# Knowledge and authority should be different types of things

Imagine a replica possessing:

$$
(K, A)
$$

where:

- $K$ is what it knows;
- $A$ is what it is authorized to do without further coordination.

Then an offline transition has the form:

$$
(K,A,S_{local})
\xrightarrow{command}
(K',A',S'_{local},M)
$$

where $M$ is durable information/messages to eventually propagate.

A transition can require evidence from $K$.

But anything that protects a global invariant must generally come from $A$, unless the invariant happens to be coordination-free.

That gives you a much cleaner taxonomy.

A receipt signature is **evidence**.

A cached order is **knowledge**.

A `$500 offline refund allowance` is **authority**.

An exclusive token for processing return `R` is **authority**.

`ReturnClaimed` is a **fact produced by a transition**.

A request to the central service is a **message**.

These things should not all be sibling DAG operators.

---

# And this exposes another problem with `provisional`

The current formulation says the business disposition can be:

```text
reject
accept
provisional
```

and treats provisional acceptance as essentially an acceptance whose unresolved predicates will be checked later. fileciteturn0file0L623-L676

I would be much more literal about reality.

If I hand a customer $74.95 while offline, the act of handing them $74.95 is **not provisional**.

It happened.

What is provisional is some higher-level interpretation:

```text
this payment constitutes the final settlement of a valid return
```

Those should not be conflated.

This distinction matters because otherwise "compensation" starts looking suspiciously like magical rollback.

The document already correctly says that distributed effects should not be deleted and that compensation produces additional history. fileciteturn0file0L126-L149

Take that thought all the way.

There was an actual transition:

$$
\text{IssueCustomerCredit}(74.95)
$$

Later there may be:

$$
\text{RecoverCredit}(74.95)
$$

or:

$$
\text{ChargeLossToStoreRiskBudget}(74.95)
$$

or:

$$
\text{SendForManualReview}
$$

Those aren't undo operations. They're subsequent transitions.

So I wouldn't make `compensate` a fundamental semantic primitive either.

---

# The return problem becomes much simpler

The mistake is trying to perform an offline version of:

```text
AcceptReturn
```

when the system lacks enough authority to decide that proposition.

Don't do that.

Define a different operation whose semantics are actually valid offline:

```text
IssueOfflineReturnCredit
```

Its contract might be:

$$
\begin{aligned}
&\text{receipt signature valid} \\
\land\;&\text{local policy permits item} \\
\land\;&\text{associate authenticated} \\
\land\;&\text{offlineRefundAuthority} \ge amount
\end{aligned}
$$

Then the transition consumes:

$$
A_{\text{refund}}' =
A_{\text{refund}} - amount
$$

and durably produces something like:

```text
OfflineReturnClaim {
    request,
    evidence,
    authorityConsumed,
    creditIssued
}
```

Notice what's missing.

There is no local check for:

```text
item has not already been returned anywhere
```

because the replica cannot establish that.

It doesn't pretend to.

That predicate belongs to a later authoritative transition:

```text
ValidateReturnClaim
```

The central authority eventually evaluates the claim and transitions to one of several states.

The local action is safe not because it somehow made a tentative global truth judgment.

It is safe because **the economic consequence it was permitted to create was bounded in advance**.

That's a much stronger conceptual model.

---

# Then the "DSL primitives" almost disappear

Your document currently proposes roughly nine semantic operations:

`input`, `read`, `derive`, `check`, `join`, `reserve`, `decide`, `append`, `effect`, `reconcile`. fileciteturn0file0L181-L195

I think that's a clue that several abstraction layers have been collapsed together.

`read` and `derive` are computation.

`check` is logic.

`reserve` is distributed authority management.

`append` is persistence.

`effect` is interaction with the outside world.

`reconcile` is protocol behavior.

`untilAcknowledged()` is a liveness/transport property.

`idempotencyKey()` is execution machinery.

Those shouldn't necessarily inhabit the same language.

At the semantic level, I think you may need only three important ideas:

$$
\boxed{\text{evidence}}
\qquad
\boxed{\text{authority}}
\qquad
\boxed{\text{transition}}
$$

Everything else can be built underneath or above them.

A transition says approximately:

```text
given this evidence
and possessing this authority
I may cause these durable consequences
and consume/produce this authority
```

Messages are consequences.

External effects are consequences.

Facts are consequences.

Later reconciliation is just another transition.

There is no privileged `reconcile` phase.

---

# The compiler's job then becomes much more interesting

The static-analysis example in the document is one of the strongest ideas:

> `Non-monotone dependency crosses an irreversible effect.` fileciteturn0file0L583-L615

But I'd formulate the underlying check differently.

Suppose the programmer declares:

```text
transition OfflineRefund(req)
```

and says it must be executable while partitioned.

The compiler asks:

> Can this transition preserve every declared invariant under all allowed concurrent executions?

If yes, fine.

If not, it attempts to determine what authority would make it safe.

For a numeric bound:

```text
refund exposure <= 10,000
```

it might infer that authority can be partitioned as escrow rights.

For uniqueness:

```text
one processor per return
```

it might require an exclusive capability/token.

For something inherently centralized:

```text
approve refund iff current fraud model says yes
```

it might conclude:

```text
cannot be guaranteed offline
```

That's a compiler doing something substantial.

`bounded-counter` is then not something most application code says explicitly. It's one possible realization of a proof obligation.

---

# `Unknown` also becomes more principled

I would not begin with:

```ts
type Knowledge<T> =
  | { kind: "known", value: T }
  | { kind: "unknown" };
```

That's useful ergonomically, but it isn't the semantics.

Semantically, local knowledge describes a set of possible worlds:

$$
W(K)
$$

More observations shrink that set:

$$
K \preceq K'
\quad\Longrightarrow\quad
W(K') \subseteq W(K).
$$

For some proposition $P$:

$$
\forall w\in W(K): P(w)
$$

means the replica can prove $P$.

Likewise:

$$
\forall w\in W(K): \neg P(w)
$$

means it can prove the opposite.

Otherwise the answer is genuinely undecidable from its current information.

Then your `known / unknown` API can be an implementation of that model rather than the model itself.

This also explains exactly why an offline cache miss cannot mean `false`, which the original text correctly emphasizes. fileciteturn0file0L27-L36

---

# And causality falls naturally into place

The document says the IR DAG and event causal graph should remain distinct. fileciteturn0file0L155-L177

I would go further.

The event/state-machine graph is primary.

The computation DAG is derived.

A distributed system is fundamentally about which transitions can occur, what they depend on, and which executions are legal.

Within one transition, sure:

```text
receipt
   ↓
verify signature
   ↓
policy check
   ↓
construct claim
```

can compile into a DAG.

But that is analogous to an SSA graph inside a compiler function. You wouldn't define the semantics of an operating system in terms of its SSA graph.

Same issue here.

---

## So I would replace the opening thesis

Instead of:

> A local replica accumulates evidence, claims, rights, and effects under partial knowledge; later replicas exchange monotone information and authoritative services resolve the deliberately non-monotone parts.

I'd start from something closer to:

> **A distributed application is a protocol of state transitions. During a partition, a replica may execute exactly those transitions justified by its local evidence and delegated authority whose concurrent execution preserves the system's safety invariants. Replicas later exchange durable facts and obligations, enabling further transitions.**

Then:

**CRDTs** tell you how certain state converges.

**CALM/monotonicity** tells you which conclusions can safely arise from growing information.

**Escrow/capabilities** tell you how authority can be distributed.

**Invariant-confluence** tells you when independent transitions compose safely.

**Sagas** are one technique for dealing with consequences of already-executed transitions.

**DAGs** represent local computation.

None of those is the master abstraction.

The master abstraction is the **protocol and its allowed transitions**.

And I think that's probably why the original design feels subtly wrong despite containing many individually correct ideas: it has assembled the right distributed-systems concepts, but put the wrong one at the center.


---

> create a better, simpler, more eleant one

I’d reduce it to a protocol language with three semantic nouns: **facts, rights, transitions**. Invariants are declarations the compiler proves about transitions; DAGs become an implementation detail.

<details><summary>💭 Thinking</summary>

**Designing the protocol model**

I’m shaping a compact formal model around durable facts, linear rights, transitions, effects, and invariants. I’m checking whether this stays elegant while still expressing concurrency, retries, compensation, authorization, and auditability clearly.

**Designed the protocol model**

</details>

This version keeps the strongest ideas from the original—cache misses are not false, convergence does not preserve invariants, delegated rights can make offline actions safe, and later remediation adds history rather than erasing it—but removes the DAG/workflow machinery as the semantic center. fileciteturn0file0L27-L36 fileciteturn0file0L88-L119 fileciteturn0file0L126-L149

:::writing{variant="document" id="48317" title="A Minimal Protocol Model for Offline Distributed Applications"}
# A Minimal Protocol Model for Offline Distributed Applications

The primitive abstraction is not a DAG.

It is a **protocol**.

A protocol consists of replicas that observe facts, possess limited authority, and perform state transitions.

The entire semantic model needs only three runtime concepts:

```text
fact
right
transition
```

and one static concept:

```text
invariant
```

Everything else—reads, checks, decisions, reconciliation, retries, compensation, CRDT merges, bounded counters, DAGs—is derived machinery.

---

## 1. Facts

A fact is an immutable statement that a replica has evidence for.

```text
Fact<T>
```

Examples:

```text
ReceiptSignatureValid(receiptId)
ItemScanned(sku)
ReturnRequested(returnId, orderId, sku, amount)
OfflineCreditIssued(returnId, amount)
ReturnValidated(returnId)
ReturnRejected(returnId, reason)
```

Facts only accumulate:

$$
F' = F \cup \Delta F
$$

Replicas exchange facts by union.

Duplicate delivery is harmless because every fact has a stable identity.

There is no:

```text
orderDoesNotExist = false
```

merely because the local replica cannot find an order.

Absence of a fact means only:

```text
not proven
```

This eliminates the need to propagate `Unknown<T>` through the entire programming model.

The semantic rule is simpler:

> A transition may depend only on propositions it can prove from the facts available to it.

If it cannot prove something, that transition is simply not enabled.

---

## 2. Rights

Facts describe what a replica knows.

Rights describe what it may do.

```text
Right<T>
```

A right is a non-duplicable capability representing delegated authority.

Examples:

```text
RefundUSD(500)
SpendablePoints(400)
ProcessReturn(returnId)
ReserveInventory(sku, 3)
```

Unlike facts, rights do not grow by set union.

They are conserved, transferred, split, or consumed.

For a numeric right:

$$
R_{before} = R_{after} + R_{consumed}
$$

So a store that possesses:

```text
RefundUSD(500)
```

may safely issue $75 of offline credit and retain:

```text
RefundUSD(425)
```

It does not need to know the current global refund exposure.

Its authority to create $75 of exposure was established earlier.

This is the fundamental distinction:

```text
knowledge != authority
```

Knowing that an item was refundable five seconds ago is not the same thing as possessing the authority to refund it now.

---

## 3. Transitions

A transition is the only thing that changes the system.

Conceptually:

$$
T:
(F,R,input)
\rightarrow
(\Delta F,R',effects)
$$

A transition:

1. receives an input or fact,
2. proves predicates from available facts,
3. consumes or transforms rights,
4. emits new facts,
5. may cause external effects.

That is the whole execution model.

For example:

```js
transition("issue-offline-credit", t => {
  t.on(ReturnRequested);

  t.require(({ request }) =>
    receiptIsValid(request.receipt) &&
    localPolicyAllows(request.item)
  );

  t.consume(
    RefundUSD,
    ({ request }) => request.amount
  );

  t.emit(({ request, transition }) => [
    OfflineCreditIssued({
      returnId: request.id,
      amount: request.amount,
      operationId: transition.id
    }),

    ReturnClaimed({
      returnId: request.id,
      orderId: request.orderId,
      item: request.item,
      amount: request.amount,
      evidence: transition.evidence
    })
  ]);

  t.effect("pos.credit", ({ request, transition }) => ({
    idempotencyKey: transition.id,
    amount: request.amount
  }));
});
```

There is no `read`.

There is no `check`.

There is no `decide`.

There is no `reserve`.

There is no `append`.

There is no `reconcile`.

Those are implementation techniques.

Semantically, a transition was enabled, consumed authority, and produced consequences.

---

## 4. Invariants

An invariant describes what must remain true for every legal execution.

```js
invariant("offline-refund-exposure", s =>
  s.outstandingOfflineRefunds <= s.delegatedOfflineRefundAuthority
);
```

Or:

```js
invariant("inventory-nonnegative", s =>
  s.inventory.every(x => x.quantity >= 0)
);
```

Or:

```js
invariant("exclusive-return-token", s =>
  s.holders(ProcessReturn).countPerReturn <= 1
);
```

The programmer specifies the property.

The compiler determines whether the transitions preserve it.

That reverses an important responsibility.

Application code should not normally say:

```js
.using("bounded-counter")
```

It should say:

```text
this transition must be executable offline
and this invariant must remain true
```

A compiler/runtime may then determine that the required right can be implemented with:

- escrow,
- a bounded counter,
- an exclusive capability,
- leases,
- static partitioning,
- or no offline implementation at all.

Mechanism follows semantics.

---

# 5. Offline execution

Suppose a customer asks for a $74.95 return.

The store knows:

```text
ReceiptSignatureValid
ItemScanned
AssociateAuthenticated
LocalPolicyAllowsReturn
```

It does not know:

```text
CurrentOrderState
PriorReturnAtAnotherStore
RemainingRefundableQuantity
```

That is not an error.

The important question is not:

> Can the store determine that the return is globally valid?

It cannot.

The important question is:

> Is there a legal transition the store is authorized to perform with the information it possesses?

Suppose the store owns:

```text
RefundUSD(2000)
```

Then:

```text
IssueOfflineCredit(74.95)
```

can be a legal transition.

It consumes $74.95 of authority and emits:

```text
OfflineCreditIssued(...)
ReturnClaimed(...)
```

The store has made **no assertion** that the return is globally valid.

It has asserted only things that are actually true:

```text
we observed this evidence
we possessed this authority
we issued this credit
we created this claim
```

That distinction is the core of the model.

---

# 6. There is no `provisional` primitive

"Provisional" is not an operation.

It is a derived interpretation of history.

If we have:

```text
OfflineCreditIssued(R)
ReturnClaimed(R)
```

but neither:

```text
ReturnValidated(R)
```

nor:

```text
ReturnRejected(R)
```

then an application may display:

```text
status(R) = "pending validation"
```

That status is a projection:

```js
const returnStatus = query(r => {
  if (has(ReturnRejected(r))) return "rejected";
  if (has(ReturnValidated(r))) return "accepted";
  if (has(OfflineCreditIssued(r))) return "pending";
  return "unknown";
});
```

It is not durable state.

It is not a protocol primitive.

It is derived from facts.

This avoids inventing a special distributed meaning for the word `provisional`.

---

# 7. Reconnection is not special

When connectivity returns, nothing switches into a special "reconciliation mode."

New facts simply arrive.

For example, the authoritative service eventually sees:

```text
ReturnClaimed(R)
```

That enables another transition:

```js
transition("validate-return", t => {
  t.on(ReturnClaimed);

  t.require(({ claim, authority }) =>
    authority.orderExists(claim.orderId) &&
    authority.itemBelongsToOrder(claim.item) &&
    authority.remainingRefundableQuantity(claim.item) > 0
  );

  t.emit(({ claim }) =>
    ReturnValidated({
      returnId: claim.returnId
    })
  );
});
```

A conflicting claim may instead enable:

```js
transition("reject-return", t => {
  t.on(ReturnClaimed);

  t.require(({ claim, authority }) =>
    authority.invalidReturn(claim)
  );

  t.emit(({ claim, authority }) =>
    ReturnRejected({
      returnId: claim.returnId,
      reason: authority.reason
    })
  );
});
```

These are ordinary transitions.

There is no semantic distinction between:

```text
local processing
```

and:

```text
reconciliation
```

There are merely transitions enabled at different replicas by different facts and rights.

---

# 8. Compensation disappears as a primitive too

Suppose the credit was issued, but the claim is later rejected.

The credit already happened.

Nothing rolls it back.

`ReturnRejected` may enable another transition:

```js
transition("recover-rejected-credit", t => {
  t.on(ReturnRejected);

  t.require(({ rejection }) =>
    has(OfflineCreditIssued(rejection.returnId))
  );

  t.emit(({ rejection }) =>
    CreditRecoveryRequested({
      returnId: rejection.returnId
    })
  );

  t.effect("customer-account.recover-credit", ({ rejection, transition }) => ({
    idempotencyKey: transition.id,
    returnId: rejection.returnId
  }));
});
```

Perhaps company policy chooses instead:

```text
ChargeToFraudBudget
SendToManualReview
AbsorbLoss
RestrictCustomerAccount
```

Those are all domain transitions.

Calling them generically "compensation" hides important semantics.

The protocol should describe what actually happens.

---

# 9. External effects are facts about attempted reality

An external effect needs a durable identity.

```js
t.effect("pos.credit", {
  idempotencyKey: transition.id,
  ...
});
```

The runtime then implements the usual machinery:

```text
durable transition
      │
      ▼
effect intent
      │
      ▼
delivery
      │
      ▼
effect result fact
```

For example:

```text
CreditRequested(op42)
CreditSucceeded(op42)
```

or:

```text
CreditRequested(op42)
CreditFailed(op42, reason)
```

Retries are therefore runtime behavior around a durable effect identity.

They are not part of the application semantics.

---

# 10. The complete return protocol

The application-level program can now be very small.

```js
export default protocol("returns", p => {
  // Authority that may be delegated to disconnected stores.
  const RefundUSD = p.right("refund-usd", Money);

  // Global safety requirement.
  p.invariant("offline-exposure-bounded", s =>
    s.offlineCredits <= s.delegatedRefundAuthority
  );

  p.transition("issue-offline-credit", t => {
    t.on(ReturnRequested);

    t.require(({ request }) =>
      validReceipt(request.receipt) &&
      localPolicyAllows(request.item)
    );

    t.consume(RefundUSD, ({ request }) => request.amount);

    t.emit(({ request, transition }) => [
      ReturnClaimed({
        returnId: request.id,
        orderId: request.orderId,
        item: request.item,
        amount: request.amount,
        evidence: transition.evidence
      }),

      OfflineCreditIssued({
        returnId: request.id,
        amount: request.amount
      })
    ]);

    t.effect("pos.credit", ({ request, transition }) => ({
      idempotencyKey: transition.id,
      amount: request.amount
    }));
  });

  p.transition("validate-return", t => {
    t.on(ReturnClaimed);

    t.at("return-authority");

    t.require(({ claim, authority }) =>
      authority.returnIsValid(claim)
    );

    t.emit(({ claim }) =>
      ReturnValidated({ returnId: claim.returnId })
    );
  });

  p.transition("reject-return", t => {
    t.on(ReturnClaimed);

    t.at("return-authority");

    t.require(({ claim, authority }) =>
      authority.returnIsInvalid(claim)
    );

    t.emit(({ claim, authority }) =>
      ReturnRejected({
        returnId: claim.returnId,
        reason: authority.reason
      })
    );
  });

  p.transition("recover-credit", t => {
    t.on(ReturnRejected);

    t.require(({ rejection }) =>
      has(OfflineCreditIssued(rejection.returnId))
    );

    t.effect("returns.handle-rejected-credit",
      ({ rejection, transition }) => ({
        idempotencyKey: transition.id,
        returnId: rejection.returnId
      })
    );
  });
});
```

That is essentially the entire user-facing model.

---

# 11. The IR becomes correspondingly small

The compiler does not need a large workflow vocabulary.

```json
{
  "protocol": "returns",

  "rights": [
    {
      "id": "refund-usd",
      "type": "Money"
    }
  ],

  "invariants": [
    {
      "id": "offline-exposure-bounded",
      "predicate": "offlineCredits <= delegatedRefundAuthority"
    }
  ],

  "transitions": [
    {
      "id": "issue-offline-credit",
      "trigger": "ReturnRequested",
      "requires": [
        "validReceipt",
        "localPolicyAllows"
      ],
      "consumes": [
        "refund-usd(request.amount)"
      ],
      "emits": [
        "ReturnClaimed",
        "OfflineCreditIssued"
      ],
      "effects": [
        "pos.credit"
      ]
    },

    {
      "id": "validate-return",
      "trigger": "ReturnClaimed",
      "location": "return-authority",
      "requires": [
        "returnIsValid"
      ],
      "emits": [
        "ReturnValidated"
      ]
    },

    {
      "id": "reject-return",
      "trigger": "ReturnClaimed",
      "location": "return-authority",
      "requires": [
        "returnIsInvalid"
      ],
      "emits": [
        "ReturnRejected"
      ]
    }
  ]
}
```

A DAG may be generated *inside each transition* for evaluation and optimization.

It is not the application model.

---

# 12. What the compiler proves

This is where most of the sophistication belongs.

For every transition declared as offline-capable, the compiler asks:

$$
I(S)
\land Pre_t(S)
\implies
I(t(S))
$$

and, crucially, whether arbitrary concurrent executions also preserve the invariant.

If a transition cannot safely execute independently, compilation should explain why.

For example:

```text
E201 Offline transition cannot preserve invariant

transition:
  issue-refund

invariant:
  each item may be refunded at most once

reason:
  two disconnected replicas may independently
  satisfy the transition precondition

possible remedies:
  - require online coordination
  - introduce an exclusive right for this item
  - weaken the invariant
  - define a bounded-loss offline transition
```

For a numeric invariant, the compiler might determine that partitionable rights are sufficient:

```text
offline refund exposure <= $10,000

        ↓

RefundUSD is distributable authority
```

For uniqueness:

```text
one return per unique token

        ↓

ProcessReturn(token) must be exclusive
```

For an invariant that cannot be decentralized:

```text
refund allowed iff current fraud service approves

        ↓

transition requires authority
offline execution impossible
```

That is where CALM, invariant-confluence, escrow, CRDT theory, linear types, and formal verification become useful.

They are compiler theory.

They do not need to become application vocabulary.

---

# 13. The algebra underneath it

The runtime state of one replica is approximately:

$$
L = (F,R)
$$

where:

$$
F
$$

is accumulated factual knowledge, and:

$$
R
$$

is locally possessed authority.

Facts have a join:

$$
F_1 \sqcup F_2
$$

and therefore naturally replicate.

Rights have conservation laws rather than arbitrary joins.

A transition is:

$$
t : F \times R \times X
\rightarrow
F \times R \times E
$$

subject to:

$$
Pre_t(F,R,X)
$$

and every transition must preserve declared invariants.

This cleanly separates the two questions a disconnected replica must answer:

```text
Can I prove enough to perform this action?

Do I possess enough authority to perform this action?
```

Those are the two fundamental dimensions.

---

# 14. What disappears

The original nine-ish concepts collapse substantially.

```text
input        → transition input
read         → implementation detail
derive       → ordinary expression
check        → transition precondition
join         → fact replication
reserve      → consume/transform right
decide       → ordinary domain logic
append       → emit fact
effect       → transition consequence
reconcile    → another transition
compensate   → another transition
forward      → fact propagation
```

The result is not merely shorter syntax.

It has fewer semantic ideas.

---

# 15. The central rule

The model can ultimately be summarized in one sentence:

> **A replica may perform a transition when its local facts prove the transition's preconditions and its local rights authorize every globally constrained consequence.**

Everything else follows from that.

Facts answer:

```text
What can I establish?
```

Rights answer:

```text
What am I allowed to change?
```

Transitions answer:

```text
What happens?
```

Invariants answer:

```text
What must never become false?
```

That is the language.
:::

