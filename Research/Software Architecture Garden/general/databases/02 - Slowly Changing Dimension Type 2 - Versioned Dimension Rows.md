---
title: Slowly Changing Dimension Type 2 - Versioned Dimension Rows
aliases:
  - Slowly Changing Dimension Type 2
  - SCD Type 2
  - Type 2 dimension
  - Versioned dimension rows
status: established
type: architecture-garden-design
created: 2026-09-01
analyzed: 2026-09-01
repository: /home/manuel/code/wesen/go-go-golems/go-go-parc
repository_note_url: https://github.com/go-go-golems/go-go-parc/blob/main/Research/Software%20Architecture%20Garden/general/databases/02%20-%20Slowly%20Changing%20Dimension%20Type%202%20-%20Versioned%20Dimension%20Rows.md
tags:
  - architecture-garden
  - databases
  - dimensional-modeling
  - data-warehousing
  - temporal-data
  - slowly-changing-dimensions
  - scd-type-2
  - etl
  - dbt
related_notes:
  - "[[Research/Software Architecture Garden/README|Software Architecture Garden]]"
  - "[[Research/Software Architecture Garden/general/databases/01 - Bounded Correction Lookback for Incremental Materializations|Bounded Correction Lookback for Incremental Materializations]]"
---

# Slowly Changing Dimension Type 2: Versioned Dimension Rows

A dimension table gives facts their descriptive context. A sale may carry a customer key, but the customer dimension supplies the customer's name, market segment, account manager, and region. Those descriptions can change. If the warehouse overwrites a customer's old region with the new one, an old sale appears to have occurred under an assignment that did not exist when the sale happened.

Slowly Changing Dimension Type 2, usually abbreviated **SCD Type 2**, preserves that historical context. Instead of updating a dimension member in place, it expires the member's current row and inserts a new row with a new surrogate key. Facts continue to reference the version that was valid when those facts were admitted. The dimension therefore stores a sequence of versions for one durable business entity.

> [!summary]
> - Type 2 preserves descriptive history by inserting a new dimension row for each tracked change.
> - A durable business key identifies the entity; a surrogate key identifies one version of that entity.
> - Effective and expiration coordinates define when each version is valid, normally as a half-open interval `[valid_from, valid_to)`.
> - Fact rows reference version keys, not merely durable entity keys.
> - Correctness depends on non-overlapping intervals, one current version, deterministic change detection, and temporally correct fact lookup.
> - Type 2 is for changing descriptive context. It is not a substitute for an event log, a measurement history, or a general audit trail.

## 1. The problem: descriptions change after facts have been recorded

Consider a warehouse with an order fact table and a customer dimension. On January 1, customer `C-1042` belongs to the `Small Business` segment. On April 1, the account is reclassified as `Enterprise`.

A dimension that overwrites the row produces this state:

| customer_id | customer_name | segment |
|---|---|---|
| C-1042 | Acme Nursery | Enterprise |

The January orders now join to `Enterprise`. A report grouped by segment rewrites the past even though no order changed.

For some attributes this is intentional. Correcting a misspelled customer name may be expected to update every report. For other attributes, historical truth depends on preserving the old value. Sales attribution, territory assignment, contractual tier, regulatory classification, and product hierarchy are common examples.

Type 2 answers this question:

> Which descriptive version of this entity was in effect when a fact occurred?

It does so by representing identity at two levels:

1. **Durable entity identity** — the source or natural key shared by every version, such as `customer_id = C-1042`.
2. **Version identity** — a warehouse surrogate key that names exactly one historical row, such as `customer_key = 70118`.

Conflating those identities destroys the pattern. The durable key says “this is the same customer.” The surrogate key says “this is the March 2026 version of that customer.”

## 2. Pattern statement

> **When a historically significant dimension attribute changes, expire the current row and insert a successor row with a new surrogate key. Keep the durable business key on every version, represent each version's validity interval explicitly, and resolve each fact to the version valid at the fact's chosen business time.**

The Kimball Group describes Type 2 as “add a new row” and recommends, at minimum, a row effective timestamp, a row expiration timestamp, and a current-row indicator in addition to the new surrogate key.[^kimball-type2]

The pattern is simple to state but has a demanding correctness boundary. It requires the warehouse to define:

- which attributes create a new version;
- which timestamp determines validity;
- whether interval bounds are inclusive or exclusive;
- how facts find a version;
- how late and corrected source records alter history;
- how duplicate loads remain idempotent;
- what happens when source history is less precise than warehouse history.

## 3. The canonical table shape

A customer dimension might use this schema:

```sql
create table dim_customer (
    customer_key       bigint primary key,
    customer_id        varchar(64) not null,
    customer_name      varchar(255) not null,
    market_segment     varchar(64) not null,
    account_manager_id varchar(64),

    valid_from         timestamp not null,
    valid_to           timestamp null,
    is_current         boolean not null,

    version_number     integer not null,
    tracked_hash       char(64) not null,
    loaded_at          timestamp not null
);
```

The columns have different responsibilities:

| Column | Responsibility |
|---|---|
| `customer_key` | Surrogate key for one dimension version; fact tables store this value. |
| `customer_id` | Durable source/business key shared by all versions of the customer. |
| Descriptive columns | Values that reports use to group, filter, label, or classify facts. |
| `valid_from` | First instant at which this version is considered valid. |
| `valid_to` | First instant at which this version is no longer valid, or `NULL` for the current version. |
| `is_current` | Convenient current-row selector; redundant with `valid_to`, so it must agree with it. |
| `version_number` | Optional sequence useful for diagnostics; it is not a time coordinate. |
| `tracked_hash` | Optional digest of Type 2 attributes used for deterministic change detection. |
| `loaded_at` | Warehouse observation time, distinct from business validity time. |

A valid history for `C-1042` is:

| customer_key | customer_id | segment | valid_from | valid_to | is_current |
|---:|---|---|---|---|---:|
| 70118 | C-1042 | Small Business | 2026-01-01 00:00 | 2026-04-01 00:00 | false |
| 84920 | C-1042 | Enterprise | 2026-04-01 00:00 | `NULL` | true |

The source key repeats. The surrogate key does not.

## 4. Temporal semantics: use one interval convention

The clearest validity convention is a **half-open interval**:

$$
[valid\_from, valid\_to)
$$

The lower bound is included; the upper bound is excluded. A version matches business timestamp $t$ when:

$$
valid\_from \le t < valid\_to
$$

For a current row whose `valid_to` is `NULL`, the second comparison is treated as unbounded:

```sql
fact.occurred_at >= dimension.valid_from
and (
    fact.occurred_at < dimension.valid_to
    or dimension.valid_to is null
)
```

Half-open intervals make adjacent versions meet without overlapping:

```text
version 1: [2026-01-01 00:00, 2026-04-01 00:00)
version 2: [2026-04-01 00:00, infinity)
```

At exactly `2026-04-01 00:00`, only version 2 matches. By contrast, two inclusive intervals ending and beginning at the same timestamp match the boundary twice. Systems sometimes avoid that by subtracting a second or a day from the old interval, but that introduces precision assumptions and gaps. Half-open intervals work at any supported timestamp precision.

> [!warning]
> A sentinel such as `9999-12-31` can replace `NULL`, but the choice must be uniform. Mixing sentinel and `NULL` conventions causes current-row predicates, uniqueness checks, and joins to disagree.

### 4.1 Valid time and observation time are different

Type 2 histories usually need at least two temporal coordinates:

- **Valid time** says when the description applies in the business domain.
- **Observation or system time** says when the warehouse learned or recorded it.

Suppose a source correction arrives on May 10 but says that a territory change took effect on April 1. Then:

```text
valid_from = 2026-04-01
loaded_at  = 2026-05-10
```

The first coordinate answers an analytical question. The second supports lineage, replay, and audit. A basic Type 2 table is not automatically a full bitemporal database, but keeping both coordinates prevents “when true” from being confused with “when known.”

## 5. The core invariants

A Type 2 design is correct only if its rows obey explicit laws.

Let $V(k)$ be all versions with durable key $k$. Each version $v$ has interval $I(v) = [from(v), to(v))$, with an absent upper bound interpreted as infinity.

### Invariant 1: surrogate version identity is unique

$$
v_1 \ne v_2 \Rightarrow surrogate(v_1) \ne surrogate(v_2)
$$

A surrogate key never identifies two versions, and a version's key is not reused after deletion or reload.

### Invariant 2: intervals for one entity do not overlap

$$
\forall v_1,v_2 \in V(k),\; v_1 \ne v_2 \Rightarrow I(v_1) \cap I(v_2) = \varnothing
$$

If intervals overlap, an as-of lookup can return multiple dimension rows for one fact.

### Invariant 3: at most one current row exists

$$
\left|\{v \in V(k) \mid current(v)\}\right| \le 1
$$

For an active source entity, the stronger rule is exactly one current row. Deleted or retired entities may deliberately have none.

### Invariant 4: current-state representations agree

If both `is_current` and `valid_to` exist:

$$
is\_current(v) \iff valid\_to(v)\;is\;NULL
$$

Redundant columns improve usability but create a consistency obligation.

### Invariant 5: adjacent versions are ordered

For versions sorted by `valid_from`, a successor cannot begin before its predecessor. When history is known continuously, the predecessor's `valid_to` equals the successor's `valid_from`.

Gaps may be legitimate when the entity did not exist or source coverage is unknown. They must be deliberate because a fact in a gap has no matching dimension version.

### Invariant 6: an unchanged source state creates no new version

Reprocessing the same source state is idempotent. Version count must not depend on how many times the load ran.

### Invariant 7: every fact has the intended dimensional version

For a fact timestamp $t$, the chosen version is the unique $v$ such that $t \in I(v)$. If no version exists, the pipeline follows a declared unknown-member or retry policy; it does not silently select the current version.

## 6. Loading the dimension

### 6.1 Classify attributes before writing SQL

Not every source column should trigger a Type 2 version. Classify each attribute according to business semantics:

| Attribute policy | Change handling | Example |
|---|---|---|
| Type 0 / fixed | Preserve original value | Original signup channel |
| Type 1 / overwrite | Update all historical versions or the current representation | Corrected capitalization |
| Type 2 / historical | Expire current row and insert successor | Sales territory |
| Ignored / operational | Do not copy or compare | Source extraction timestamp |

A digest used for change detection must include only normalized Type 2 attributes. Including `updated_at`, ingestion metadata, or volatile formatting produces a false new version on every load.

```text
tracked_hash = SHA256(
    normalize(market_segment),
    normalize(account_manager_id)
)
```

Normalization itself is policy. `NULL`, empty string, trailing spaces, case differences, decimal scale, and timezone conversion must not drift between runs.

### 6.2 Initial load

For an entity not yet represented in the dimension:

```text
insert one row:
    surrogate key = newly allocated value
    durable key   = source durable key
    attributes    = normalized source values
    valid_from    = source effective time or declared warehouse baseline
    valid_to      = null
    is_current    = true
    version       = 1
```

If the source supplies no trustworthy effective time, the warehouse can use extraction time, but must document that the table describes **when the warehouse observed a state**, not necessarily when the state became true.

### 6.3 No-change load

When the current dimension row and source row have the same tracked values, do nothing except optional load telemetry. Do not extend, close, or duplicate the version.

### 6.4 Changed load

When tracked values differ, perform expiration and insertion in one transaction:

```sql
begin;

update dim_customer
set valid_to = :effective_at,
    is_current = false
where customer_id = :customer_id
  and is_current = true;

insert into dim_customer (
    customer_key,
    customer_id,
    customer_name,
    market_segment,
    account_manager_id,
    valid_from,
    valid_to,
    is_current,
    version_number,
    tracked_hash,
    loaded_at
)
values (
    :new_customer_key,
    :customer_id,
    :customer_name,
    :market_segment,
    :account_manager_id,
    :effective_at,
    null,
    true,
    :previous_version + 1,
    :tracked_hash,
    :loaded_at
);

commit;
```

The two writes are one logical transition. If expiration commits without insertion, the entity has no current row. If insertion commits without expiration, it has two.

### 6.5 Transaction and concurrency boundary

Two workers processing the same durable key can both read the same current row and both insert successors. Avoid this through one of:

- serialize dimension updates by durable key;
- lock the current row with `SELECT ... FOR UPDATE`;
- stage changes and execute a set-based transaction with uniqueness enforcement;
- use an engine-specific `MERGE` only after proving its concurrent semantics.

A uniqueness constraint for the current version is valuable where the database supports a filtered or partial index:

```sql
create unique index one_current_customer
on dim_customer (customer_id)
where is_current = true;
```

On engines without partial indexes, use an equivalent generated-column or transactional enforcement strategy. The database constraint is a backstop, not a replacement for correct load ordering.

## 7. Resolving facts to dimension versions

### 7.1 Early-arriving dimension, ordinary fact

If the dimension version exists before the fact load, resolve the surrogate key by durable key and fact business time:

```sql
select customer_key
from dim_customer
where customer_id = :customer_id
  and valid_from <= :fact_time
  and (valid_to > :fact_time or valid_to is null);
```

The result must contain exactly one row.

The fact stores that surrogate key:

```text
fact_order.customer_key = 70118
```

Later Type 2 changes do not rewrite the key. January orders remain attached to the January customer version.

### 7.2 Why joining facts by durable key is wrong

This query duplicates facts across every historical version:

```sql
-- Incorrect for a Type 2 dimension
select *
from fact_order f
join dim_customer d
  on f.customer_id = d.customer_id;
```

Adding `where d.is_current = true` avoids duplication but answers a different question: “show all facts under today's customer description.” That can be a useful report, but it is not historical attribution.

A well-designed warehouse can support both perspectives:

- **as was** — join the fact's stored version surrogate key;
- **as is** — join a durable entity key to a current-state projection.

The query must name which perspective it requests.

### 7.3 Late-arriving dimension member

A fact may arrive before its dimension row. Common policies are:

1. **Hold the fact** until the dimension member appears.
2. **Use an unknown member** and later restate the foreign key.
3. **Create an inferred member** containing the durable key and placeholders, then complete or version it later.

Each policy has operational consequences. An unknown member keeps the fact load moving but requires a repair process. An inferred member preserves entity-level attribution but needs careful rules so filling missing attributes does not create a false historical transition.

### 7.4 Late-arriving fact

A late fact with an old business timestamp should resolve against the historical interval containing that timestamp, not the current dimension row. This is one reason expired rows must remain queryable and indexed by durable key plus validity interval.

## 8. Corrections and out-of-order changes

Appending a successor is easy when changes arrive in effective-time order. Backdated corrections require interval surgery.

Suppose the warehouse contains:

```text
A: [Jan 1, Apr 1) Small Business
B: [Apr 1, infinity) Enterprise
```

On May 10 it learns that the customer was actually `Mid-Market` from March 1 through April 1. The corrected history is:

```text
A: [Jan 1, Mar 1) Small Business
C: [Mar 1, Apr 1) Mid-Market
B: [Apr 1, infinity) Enterprise
```

The loader must split an existing interval, not merely expire the current row. It must then decide whether facts from March should be restated from A's surrogate key to C's key.

This yields two distinct policies:

- **Prospective Type 2 processing** preserves changes from the time the warehouse observes them.
- **Effective-dated Type 2 processing** reconstructs the source's claimed business history and may rewrite interval boundaries and fact foreign keys.

Neither is universally correct. Regulatory reports may require the warehouse to preserve what was known at report time. Operational analysis may require corrected effective history. If both questions matter, a single valid-time dimension may be insufficient; retain load/audit history or adopt a bitemporal model.

> [!important]
> Type 2 preserves prior descriptive versions. It does not by itself preserve every prior warehouse belief after a backdated correction mutates those versions.

## 9. A complete loading algorithm

The following pseudocode states policy before choosing database syntax:

```text
for each normalized source member s:
    begin transaction

    versions = lock all dimension versions for s.durable_key
    current  = the unique current version, if any

    if no versions exist:
        insert initial version(s) from available source history
        commit
        continue

    if source supplies only current state:
        if tracked_attributes(s) == tracked_attributes(current):
            commit                         // idempotent no-op
        else:
            assert s.effective_at >= current.valid_from
            expire current at s.effective_at
            insert successor beginning at s.effective_at
            commit
        continue

    if source supplies effective-dated history:
        desired_timeline = normalize and validate source intervals
        existing_timeline = read existing intervals
        replacement = reconcile(existing_timeline, desired_timeline)

        assert replacement has no overlaps
        atomically apply inserts, expirations, and interval splits
        repair affected fact foreign keys according to policy
        commit
```

The branch between current-state and historical sources matters. A mutable source table that exposes only the latest row cannot reconstruct changes that occur between warehouse observations. Running the snapshot more often narrows the blind interval; it does not eliminate it.

## 10. Query patterns

### 10.1 Current member lookup

```sql
select *
from dim_customer
where customer_id = 'C-1042'
  and is_current = true;
```

### 10.2 Member as of a timestamp

```sql
select *
from dim_customer
where customer_id = 'C-1042'
  and valid_from <= timestamp '2026-03-15 12:00:00'
  and (
      valid_to > timestamp '2026-03-15 12:00:00'
      or valid_to is null
  );
```

### 10.3 Facts under historical context

```sql
select
    d.market_segment,
    sum(f.net_amount) as net_sales
from fact_order f
join dim_customer d
  on f.customer_key = d.customer_key
group by d.market_segment;
```

### 10.4 Facts restated under current context

This requires the fact or version row to retain the durable entity identity:

```sql
select
    current_d.market_segment,
    sum(f.net_amount) as net_sales
from fact_order f
join dim_customer fact_d
  on f.customer_key = fact_d.customer_key
join dim_customer current_d
  on current_d.customer_id = fact_d.customer_id
 and current_d.is_current = true
group by current_d.market_segment;
```

The second query deliberately restates history. It should be labeled accordingly in semantic models and dashboards.

## 11. Testing the pattern

Type 2 needs structural tests and behavioral transition tests.

### 11.1 Structural tests

**No duplicate surrogate keys**

```sql
select customer_key
from dim_customer
group by customer_key
having count(*) > 1;
```

**No multiple current rows**

```sql
select customer_id
from dim_customer
where is_current = true
group by customer_id
having count(*) > 1;
```

**Current flag agrees with open-ended interval**

```sql
select *
from dim_customer
where is_current <> (valid_to is null);
```

**No invalid interval**

```sql
select *
from dim_customer
where valid_to is not null
  and valid_from >= valid_to;
```

**No overlaps**

```sql
select a.customer_id, a.customer_key, b.customer_key
from dim_customer a
join dim_customer b
  on a.customer_id = b.customer_id
 and a.customer_key < b.customer_key
 and a.valid_from < coalesce(b.valid_to, timestamp '9999-12-31 00:00:00')
 and b.valid_from < coalesce(a.valid_to, timestamp '9999-12-31 00:00:00');
```

### 11.2 Behavioral test matrix

A loader should prove at least these transitions:

| Scenario | Expected result |
|---|---|
| First observation | One current version inserted. |
| Identical rerun | No additional version. |
| Type 1-only change | Historical policy applied without false Type 2 version. |
| One Type 2 change | Old row expires; one successor is current. |
| Multiple ordered changes | Contiguous, ordered versions. |
| Two changes at same effective time | Deterministic collapse or explicit rejection. |
| Backdated change | Interval split or declared rejection/manual repair. |
| Concurrent duplicate load | One successor, not two. |
| Transaction failure after expiration | Whole transition rolls back. |
| Late-arriving fact | Historical surrogate key selected. |
| Timestamp at boundary | Exactly one successor version selected. |
| Deleted source member | Current row expired according to deletion policy. |

Property-based tests are especially useful. Generate timelines and assert that every sampled instant matches at most one version, version intervals remain ordered, and replaying the same source sequence does not change the result.

## 12. Indexing and physical design

The workload usually needs three access paths:

1. surrogate-key lookup from facts;
2. current-row lookup by durable key;
3. as-of lookup by durable key and validity time.

A starting point is:

```sql
create unique index dim_customer_pk
    on dim_customer (customer_key);

create index dim_customer_current
    on dim_customer (customer_id, is_current);

create index dim_customer_asof
    on dim_customer (customer_id, valid_from, valid_to);
```

The optimal as-of index depends on the engine and data distribution. Interval predicates are more demanding than point equality, so inspect query plans with realistic version counts.

Type 2 can multiply dimension rows substantially when tracked values are volatile. That is not merely a storage concern: it enlarges indexes, makes current-state queries easier to write incorrectly, and increases fact-resolution work. Track only attributes whose historical value changes analytical meaning.

## 13. dbt snapshots as a Type 2 implementation

The dbt documentation explicitly describes snapshots as implementing Type 2 Slowly Changing Dimensions over mutable source tables.[^dbt-snapshots] A snapshot records changing rows and provides metadata such as validity coordinates. dbt supports timestamp- and check-based strategies; its documentation recommends the timestamp strategy when a reliable `updated_at` column exists because schema evolution is easier to handle.[^dbt-strategy]

A representative modern snapshot configuration is conceptually:

```yaml
snapshots:
  - name: customer_snapshot
    relation: source('crm', 'customers')
    config:
      schema: snapshots
      unique_key: customer_id
      strategy: timestamp
      updated_at: updated_at
```

The tool can implement row versioning, but it cannot choose business semantics on the team's behalf. The designer must still answer:

- Is `unique_key` truly durable and unique?
- Does `updated_at` advance for every tracked change?
- Is source update time the desired validity coordinate?
- Which columns should be Type 1 versus Type 2?
- How are deletes represented?
- How are facts resolved to snapshot versions?
- Can changes occur and disappear between snapshot runs?

A snapshot command without a consumer is not architecture. A complete mechanism has a declared cadence, ownership, tests, downstream joins, retention policy, and repair procedure.

## 14. What Type 2 is not

### 14.1 It is not an event log

An event log records domain occurrences such as `CustomerMovedRegion`, including order, payload, and event identity. A Type 2 table records versioned descriptive states. Several events may produce one state; one correction may rewrite state intervals; transitions may not explain why they occurred.

Use event sourcing or an append-only change log when replay, causal explanation, command audit, or every intermediate transition is required.

### 14.2 It is not a fact or measurement history

Inventory quantity, temperature, account balance observations, and request latency are measurements. Their changing values are usually facts at a declared grain, not descriptive versions of a dimension member.

Recording an inventory quantity every hour as Type 2 customer-like versions adds surrogate-key and interval machinery without clarifying the analytical model. A periodic snapshot fact table or event fact table is normally more appropriate.

### 14.3 It is not change data capture

CDC transports inserts, updates, and deletes from a source. Type 2 defines how a warehouse represents selected descriptive changes. CDC may feed a Type 2 loader, but one does not replace the other.

### 14.4 It is not automatically an audit trail

A loader can correct, merge, or delete Type 2 rows. Unless warehouse changes themselves are append-only and actor/reason metadata is retained, the table does not prove who changed what or what the warehouse believed before a correction.

### 14.5 It is not full bitemporal modeling

Type 2 normally models one validity timeline plus load metadata. Bitemporal modeling independently represents valid time and transaction/system time, allowing questions such as “what did we believe on May 1 about what was valid on April 1?” Type 2 alone often cannot answer that after correction.

## 15. Common failure modes

### Overwriting the current row

**Symptom:** old facts acquire current labels.

**Cause:** the load uses `UPDATE` for a historically significant attribute.

**Repair:** classify attributes and version Type 2 changes.

### Using the durable key as the dimension primary key

**Symptom:** inserting a successor violates uniqueness, so developers overwrite instead.

**Cause:** entity identity and version identity share one column.

**Repair:** introduce a surrogate version key and retain the durable key as a non-unique lookup key.

### Joining facts to the current row

**Symptom:** reports silently restate history.

**Cause:** fact rows lack or ignore version surrogate keys.

**Repair:** resolve the version during fact admission and label any current-state restatement query explicitly.

### Overlapping intervals

**Symptom:** one fact joins to multiple versions and aggregates double.

**Cause:** inconsistent boundary semantics, concurrent loads, or incorrect backdated repair.

**Repair:** use half-open intervals, serialize transitions, test overlap, and treat backdated changes as interval reconciliation.

### A new version on every run

**Symptom:** row count grows despite no business changes.

**Cause:** unstable hashes, volatile fields, timestamp precision changes, or inconsistent normalization.

**Repair:** canonicalize and compare only declared Type 2 attributes; prove identical-rerun idempotence.

### Snapshotting too slowly

**Symptom:** short-lived source states never appear.

**Cause:** a mutable source changes twice between observations.

**Repair:** consume CDC/source history or accept and document the sampling limit. A Type 2 loader cannot recover a state it never observed.

### Treating all attributes as Type 2

**Symptom:** excessive versions and difficult queries with no historical value.

**Cause:** change capture was substituted for dimensional design.

**Repair:** classify each attribute from reporting requirements.

### Ignoring deletion semantics

**Symptom:** a removed entity remains current forever.

**Cause:** the source extract omits rows but the loader cannot distinguish deletion from partial extraction.

**Repair:** use explicit delete signals, source tombstones, or a carefully defined full-snapshot comparison before expiring current rows.

## 16. When to use the pattern

Use Type 2 when all of the following are true:

- the table represents a dimension: a descriptive entity used to contextualize facts;
- selected attributes change over time;
- reports need the attribute values that were valid for historical facts;
- the source exposes enough identity and timing to create meaningful versions;
- consumers can manage surrogate version keys and temporal lookup;
- the additional rows and operational repair paths are justified.

Typical candidates include:

- customer segment or risk classification;
- employee department or manager assignment;
- product category hierarchy;
- supplier status;
- store territory;
- contract or service tier.

Do not default to Type 2 when:

- only current state matters;
- a correction should intentionally restate all history;
- the value is a frequent measurement rather than a description;
- every transition and cause must be replayable;
- source identity is unstable;
- no downstream consumer performs historical attribution.

## 17. Design checklist

Before implementing Type 2, write down the answers:

### Identity

- What is the durable business key?
- Is it stable, unique, non-null, and never recycled?
- How is the surrogate version key allocated?

### Attribute policy

- Which fields are fixed, overwritten, versioned, or ignored?
- How are values normalized before comparison?
- Is the change hash deterministic across environments?

### Time

- What does `valid_from` mean?
- Is the source time trustworthy and timezone-normalized?
- Are intervals half-open?
- Is the current upper bound `NULL` or a sentinel?
- Is warehouse observation time retained separately?

### Loading

- Is expiration plus insertion atomic?
- How are concurrent updates for one durable key serialized?
- What happens on identical replay?
- How are deletes, backdated changes, and same-time changes handled?

### Fact integration

- Which fact timestamp chooses the dimension version?
- What happens when no version matches?
- How are inferred or unknown members repaired?
- Are “as was” and “as is” queries separately named?

### Operations

- What is the load cadence?
- Which tests enforce interval and current-row invariants?
- How are missed source states detected?
- What is the retention and correction policy?
- Who owns historical restatement decisions?

If these answers are absent, the design is not complete even if a framework can generate snapshot rows.

## 18. Relationship to bounded correction lookback

[[Research/Software Architecture Garden/general/databases/01 - Bounded Correction Lookback for Incremental Materializations|Bounded Correction Lookback for Incremental Materializations]] and Type 2 solve different problems.

- Type 2 defines how descriptive entity versions are represented.
- Bounded lookback defines how a derived materialization reprocesses a recent event-time interval to absorb late corrections.

A Type 2 loader can use a lookback when source changes arrive late, but doing so introduces interval reconciliation and possibly fact restatement. Conversely, a daily inventory aggregate may benefit from a bounded lookback while having no Type 2 dimension at all.

Do not infer the data model from the incremental processing strategy.

## 19. Candidate Architecture Garden guidance

The following rules are stable enough to reuse across projects:

1. **Separate durable entity identity from version identity.** A natural key identifies the member; a surrogate key identifies one historical representation.
2. **State interval semantics as a law.** Prefer half-open intervals and test non-overlap.
3. **Make historical perspective explicit.** “As was” and “as is” are different joins, not interchangeable report options.
4. **Classify attributes before implementing capture.** Type 2 is a business-history decision, not a blanket response to mutable tables.
5. **Treat expiration and successor insertion as one transition.** The transaction and concurrency boundary belong to the pattern.
6. **Preserve valid time separately from observation time.** They answer different questions.
7. **Prove replay idempotence and boundary uniqueness.** These are first-class acceptance tests.
8. **Do not use Type 2 for frequent measurements merely because values change.** Model measurements as facts at an explicit grain.
9. **A snapshot facility needs a caller and consumer.** Cadence, ownership, downstream resolution, retention, and repair make it an operational mechanism.
10. **Name the correction contract.** Prospective observation, effective-dated reconstruction, and bitemporal audit are distinct promises.

## 20. Further reading

### Foundational sources

- Kimball Group, [Type 2: Add New Row](https://www.kimballgroup.com/data-warehouse-business-intelligence-resources/kimball-techniques/dimensional-modeling-techniques/type-2/). The compact canonical statement of the pattern: allocate a new surrogate key and add effective, expiration, and current-row fields.
- Ralph Kimball, [Slowly Changing Dimensions, Part 2](https://www.kimballgroup.com/2008/09/slowly-changing-dimensions-part-2/). Explains Type 2 in the larger Type 1/2/3 family and its role in preserving history.
- Margy Ross, [Slowly Changing Dimensions Are Not Always as Easy as 1, 2, 3](https://www.kimballgroup.com/2005/03/slowly-changing-dimensions-are-not-always-as-easy-as-1-2-3/). Covers mixed requirements and the need to locate the version effective at a requested time.
- Ralph Kimball and Margy Ross, *The Data Warehouse Toolkit*, 3rd ed., Wiley, 2013. The broader dimensional-modeling context for surrogate keys, facts, dimensions, and SCD techniques.

### Implementation guidance

- dbt Labs, [Snapshots](https://docs.getdbt.com/docs/build/snapshots). Documents dbt snapshots as a Type 2 mechanism over mutable source tables and describes validity metadata and operational behavior.
- dbt Labs, [Snapshot strategy](https://docs.getdbt.com/reference/resource-configs/strategy). Compares timestamp and check strategies and documents their configuration contracts.
- Microsoft Learn, [Slowly changing dimension type 2](https://learn.microsoft.com/en-us/fabric/data-factory/slowly-changing-dimension-type-two). A concrete Fabric/Dataflow implementation walkthrough.
- Microsoft Learn, [Dimension tables in a dimensional model](https://learn.microsoft.com/en-us/fabric/data-warehouse/dimensional-modeling-dimension-tables). Places Type 2 within dimension design, surrogate key generation, and historical querying.

### Adjacent concepts

- Martin Fowler, [Temporal Patterns](https://martinfowler.com/eaaDev/timeNarrative.html). A useful entry point to valid-time and temporal modeling vocabulary beyond dimensional warehouses.
- Richard T. Snodgrass, *Developing Time-Oriented Database Applications in SQL*, Morgan Kaufmann, 1999. A rigorous treatment of temporal intervals, valid time, transaction time, and SQL implementation concerns; the author provides the book online through the University of Arizona.

## Notes on terminology

“Slowly changing” is historical terminology from dimensional modeling. It does not impose a numerical rate limit. A Type 2 attribute may change twice in a day and still use the pattern, although high change frequency may indicate that the attribute belongs in a fact or event model instead.

“Dimension” is equally important. Type 2 is not the generic rule “insert a row whenever anything changes.” It is a representation for preserving historically meaningful descriptions used to interpret facts.

[^kimball-type2]: Kimball Group, “Type 2: Add New Row,” [Dimensional Modeling Techniques](https://www.kimballgroup.com/data-warehouse-business-intelligence-resources/kimball-techniques/dimensional-modeling-techniques/type-2/).
[^dbt-snapshots]: dbt Labs, [Snapshots](https://docs.getdbt.com/docs/build/snapshots).
[^dbt-strategy]: dbt Labs, [Snapshot strategy](https://docs.getdbt.com/reference/resource-configs/strategy).
