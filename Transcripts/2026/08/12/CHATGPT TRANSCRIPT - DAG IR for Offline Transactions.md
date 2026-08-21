# DAG IR for Offline Transactions

- URL: https://chatgpt.com/c/6a7cdab0-c1f0-83ea-bb60-f271d8b27dfe
- Created: 2026-08-12T20:42:28.010Z

---

> Create an Elegant JS API (fluent builder pattern customizing with lambdas to create DAG IR)
>
> for distributed system, when you're offline, we have to be able to take a return for an order that is not available locally because we are offline and can't lookup the order, we have to validate the transaction as much as possible, then store and forward later. Store local copuies like loyalty points and merging it with the state of the system when it comes back.
>
> ---
>
> Lookup mathematical / CS theoretical foundations first and map the problem to composable fundamentals.
>
>
> Concise elegant DSL, not overengineered.

<details><summary>💭 Thinking</summary>

**Researching foundations**

I’m grounding the design in join-semilattice CRDTs, monotonic logic, invariant confluence, escrowed rights, and append-only event logs. The DSL will therefore separate facts, derivations, reservations, deferred checks, and compensation.

**Shaping the model**

I’m treating offline processing as a DAG of monotone facts and explicitly bounded authority. Local nodes may accept returns tentatively, while globally conflicting decisions—such as loyalty redemption—remain deferred or consume escrowed credits.

**Designing the DSL**

I’m building a fluent JavaScript API whose lambdas describe typed IR nodes. The compiler can topologically order dependencies, serialize policies, and execute locally without embedding hidden network assumptions.

**Researched foundations**

</details>

I’ll ground this in semilattices/CRDTs, monotonicity, invariant-confluence/escrow, and disconnected-operation reconciliation, then collapse it into a small DAG vocabulary and fluent JS DSL.

```json
{"system2_search_query":[{"q":"site:arxiv.org Shapiro conflict-free replicated data types semilattice CRDT paper"},{"q":"site:arxiv.org CALM theorem monotonicity coordination distributed systems paper"},{"q":"site:arxiv.org invariant confluence coordination avoidance distributed databases Bailis paper"},{"q":"Bayou disconnected operations tentative committed reconciliation paper PDF"}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Searched 14 websites**

</details>

The key split is already clear: **mergeable state** should be algebraic; **business invariants that are unsafe under merge** should become explicit deferred obligations, not hidden “eventual consistency” magic. Loyalty balance limits are the classic place where escrow/rights can preserve a bound offline.

```json
{"open":[{"ref_id":"turn731577search3"}],"response_length":"short"}
```

<details><summary>💭 Thinking</summary>

**Refining the architecture**

I’m distinguishing offline-safe facts from globally contested decisions: local validation can create tentative evidence, while authoritative reconciliation resolves inventory, duplicate returns, refund limits, and loyalty spending.

**Structuring reconciliation**

I’m modeling store-and-forward records as idempotent operations with unique identifiers. Positive credits can merge additively; debits need escrowed rights or deferred approval, while rejection produces explicit compensation rather than silent mutation.

**Refined the architecture**

**Searched 1 website**

</details>

The clean abstraction is **not “offline mode vs online mode.”** Model the workflow as a DAG of **evidence → validation → durable intent → mergeable local effects → authoritative reconciliation**.

The theoretical boundary matters because some parts can be made mathematically convergent, while others fundamentally cannot.

### Foundations → domain primitives

| Foundation | What it gives you | Return-system mapping |
|---|---|---|
| **Join-semilattices / CRDTs** | A merge `⊔` that is associative, commutative, idempotent, so replicas converge regardless of delivery order/duplicates. citeturn758855view1 | Immutable return intents, loyalty ledger entries, acknowledgements |
| **CALM / monotonicity** | Monotone conclusions can be computed consistently without coordination; conclusions invalidated by future facts require coordination. citeturn758855view0 | “Receipt proves SKU X was purchased” can be monotone. “Nobody has already returned SKU X” is not. |
| **Invariant confluence** | Characterizes when independently valid replica operations remain valid after merge. If they do not, coordination or another mechanism is required. citeturn758855view2 | `totalReturned <= purchasedQty` is not safely enforceable at arbitrary offline stores: two replicas can independently return the last unit. |
| **Escrow / bounded counters** | Pre-distribute finite rights so replicas can change a bounded quantity offline without violating its invariant. citeturn981576view0 | Offline refund-risk budget, point-spending allowance, inventory allocation |
| **Bayou-style tentative writes** | Carry application-specific dependency checks with tentative updates and perform deterministic resolution when better state becomes available. citeturn519724view0turn519724view1 | Almost exactly your “accept now, validate as much as possible, reconcile later” requirement |

The important consequence is that **“this order has not already been returned” cannot generally be proven offline from absence in a cache**. Two disconnected stores can both see the same old state and both accept the final returnable unit. By the invariant-confluence criterion, that invariant needs coordination, preallocated rights, or tentative acceptance. citeturn758855view2

So make incomplete knowledge explicit instead of pretending the local database is authoritative.

## Small validation algebra

Use three outcomes rather than Boolean validation:

```js
V.pass(evidence)
V.fail(reason)
V.defer(obligation)
```

Composition is simple:

```text
Fail   dominates
Defer  accumulates obligations
Pass   contributes evidence
```

`defer()` is the interesting value. It means:

> This operation is locally admissible, but this proposition must be established before final settlement.

That gives you things like:

```text
Pass  qty > 0
Pass  item barcode valid
Pass  signed receipt structurally valid

Defer authoritative order exists
Defer remaining return quantity >= requested quantity
Defer refund has not already occurred elsewhere
```

The transaction can still become a durable **tentative intent**.

## DSL surface

I would keep the vocabulary to roughly:

`input → read → check → emit → merge → reconcile`

```js
const intrinsic = op("returns.intrinsic@1", r => {
  if (r.qty <= 0) return V.fail("invalid-qty");
  if (r.amount < 0) return V.fail("invalid-amount");

  return V.pass();
});

const cachedOrderCheck = op("returns.cached-order@1", (order, r) => {
  if (!order)
    return V.defer("authoritative-order");

  // Only prove things the cached observation actually proves.
  if (canProveReturnable(order, r)) {
    return V.pass({
      orderVersion: order.version,
      observedAt: order.observedAt
    });
  }

  // Stale/incomplete data normally means "don't know",
  // not "definitely false".
  return V.defer("authoritative-return-policy");
});

const authoritativeCheck =
  op("returns.authoritative@3", (order, r) => {
    if (!order)
      return V.fail("order-not-found");

    const line = findLine(order, r.sku);

    if (!line)
      return V.fail("item-not-purchased");

    if (line.purchasedQty - line.returnedQty < r.qty)
      return V.fail("already-returned");

    return V.pass();
  });

const pointDebit = op("loyalty.return-debit@1", r => ({
  id: `points:return:${r.txnId}`,
  customerId: r.customerId,
  delta: -r.pointsEarned,
  cause: r.txnId
}));

const compensatePoints = op("loyalty.compensate@1", e => ({
  id: `points:compensate:${e.id}`,
  customerId: e.customerId,
  delta: -e.delta,
  compensationFor: e.id
}));
```

Then the workflow itself stays small:

```js
const offlineReturn = dag("offline-return")

  .input("r")

  .read(
    "cachedOrder",
    local("orders"),
    $ => $.r.orderId
  )

  .check(
    "intrinsic",
    $ => intrinsic($.r)
  )

  .check(
    "cachedPolicy",
    $ => cachedOrderCheck($.cachedOrder, $.r)
  )

  .emit(
    "intent",
    outbox("returns"),
    $ => ({
      id: $.r.txnId,
      type: "ReturnRequested",

      request: $.r,

      evidence: $.cachedPolicy.evidence,
      obligations: $.cachedPolicy.obligations
    }),
    {
      key: $ => $.r.txnId
    }
  )

  // Optimistic local projection.
  // Immutable entries merge by set-union.
  .merge(
    "loyalty",
    local("loyalty.entries"),
    crdt.gset(),
    $ => pointDebit($.r)
  )

  // Same DAG, but this region requires authoritative placement.
  .reconcile(r => r

    .read(
      "order",
      authority("orders"),
      $ => $.r.orderId
    )

    .check(
      "final",
      $ => authoritativeCheck($.order, $.r)
    )

    .emit(
      "decision",
      stream("return-decisions"),
      $ => ({
        intentId: $.intent.id,
        verdict: $.final
      })
    )

    .when(
      $ => $.final.failed,
      x => x.emit(
        "pointsCompensation",
        stream("loyalty.entries"),
        $ => compensatePoints(pointDebit($.r))
      )
    )
  )

  .build();
```

This says surprisingly little, which is desirable.

## Lambdas should build IR, not become IR

One important JS detail: **do not serialize function source or closures**.

The lambdas execute once during construction against symbolic references:

```js
$ => authoritativeCheck($.order, $.r)
```

Here `$.order` and `$.r` are symbolic `Ref`s. `authoritativeCheck` is a registered/versioned operator. Therefore the builder records something like:

```js
{
  name: "offline-return",

  nodes: [
    {
      id: "r",
      kind: "input"
    },

    {
      id: "cachedOrder",
      kind: "read",
      place: "edge",
      source: "orders",
      key: { ref: "r.orderId" }
    },

    {
      id: "intrinsic",
      kind: "check",
      fn: "returns.intrinsic@1",
      deps: ["r"]
    },

    {
      id: "cachedPolicy",
      kind: "check",
      fn: "returns.cached-order@1",
      deps: ["cachedOrder", "r"]
    },

    {
      id: "intent",
      kind: "emit",
      place: "edge",
      sink: "returns",
      deps: ["r", "cachedPolicy"]
    },

    {
      id: "loyalty",
      kind: "merge",
      algebra: "gset",
      deps: ["r"]
    },

    {
      id: "order",
      kind: "read",
      place: "authority",
      source: "orders",
      deps: ["r.orderId"]
    },

    {
      id: "final",
      kind: "check",
      fn: "returns.authoritative@3",
      deps: ["order", "r"]
    }
  ]
}
```

So the fluent API is syntactic sugar for a **serializable dependency graph**. Versioned `op("name@version", implementation)` functions give you deployment compatibility without serializing arbitrary JavaScript.

## Loyalty: merge events, not balances

I would not synchronize:

```js
{ points: 4720 }
```

with some ad-hoc “latest wins” policy.

Synchronize immutable entries:

```js
{
  id: "points:return:R123",
  customerId: "C7",
  delta: -250,
  cause: "R123"
}
```

Replica state becomes:

```text
entries = localEntries ∪ remoteEntries
balance = Σ entry.delta
```

Union is naturally idempotent, associative, and commutative, which is exactly the CRDT convergence structure. citeturn758855view1 A rejected return gets another immutable `+250` compensation entry rather than deleting history.

If loyalty points **may temporarily go negative**, that is enough.

If `points >= 0` is a hard invariant even during partitions, ordinary additive merging is insufficient. Give each store/device a finite spending allowance using escrow/bounded-counter rights; when local rights are exhausted, spending must wait for connectivity. That is precisely the problem bounded-counter CRDTs address. citeturn981576view0

The same trick is useful for an **offline refund exposure budget**:

```js
.claim(
  "offlineRefundAuthority",
  escrow("refund-usd"),
  $ => $.r.amount
)
```

You still cannot prove the order hasn't been returned elsewhere, but you can mathematically bound how much money an isolated store can expose the business to.

## The resulting architecture

The core model is:

```text
immutable evidence
      ↓
Pass | Fail | Defer
      ↓
tentative intent
      ↓
append-only mergeable local effects
      ↓
store & forward
      ↓
authoritative dependency checks
      ↓
accept | reject | adjust
      ↓
append compensating facts if necessary
```

Bayou's old `dependency check + tentative update + merge procedure` model is very close conceptually; the refinement here is to make **unknown knowledge, monotonic state, escrow rights, and placement boundaries explicit in the IR**. citeturn519724view0turn519724view1

The main design rule I would enforce in the API is:

> **CRDT the facts; reconcile the business decision.**

Don't attempt to turn the entire return transaction into a CRDT. The return **intent**, evidence, loyalty deltas, acknowledgements, and compensation records compose cleanly. Whether the customer was actually entitled to the refund is an invariant-bearing decision and should remain visibly tentative until the authoritative DAG portion resolves it.

