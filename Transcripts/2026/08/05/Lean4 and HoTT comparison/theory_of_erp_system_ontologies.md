---
title: "Theory of ERP System Ontologies"
subtitle: "Categories, Dependent Types, and Homotopical Integration for Industrial Systems"
author: "Prepared with GPT-5.6 Pro"
date: "First working edition — August 2026"
lang: en-US
documentclass: book
classoption:
  - 11pt
  - oneside
  - openany
geometry:
  - margin=1in
mainfont: "Noto Serif"
sansfont: "Noto Sans"
monofont: "DejaVu Sans Mono"
fontsize: 11pt
colorlinks: true
linkcolor: "blue!40!black"
urlcolor: "blue!40!black"
toc: true
toc-depth: 2
secnumdepth: 0
header-includes:
  - |
    \usepackage{microtype}
  - |
    \usepackage{booktabs}
  - |
    \usepackage{longtable}
  - |
    \usepackage{array}
  - |
    \usepackage{xcolor}
  - |
    \usepackage{fancyhdr}
  - |
    \pagestyle{fancy}
  - |
    \fancyhf{}
  - |
    \fancyhead[LE,RO]{\small\nouppercase{\leftmark}}
  - |
    \fancyfoot[C]{\thepage}
  - |
    \setlength{\headheight}{14pt}
  - |
    \usepackage{enumitem}
  - |
    \setlist{nosep}
  - |
    \usepackage{fvextra}
  - |
    \RecustomVerbatimEnvironment{Highlighting}{Verbatim}{breaklines,breakanywhere,commandchars=\\\{\}}
  - |
    \usepackage{amsthm}
  - |
    \newtheorem{principle}{Principle}[chapter]
  - |
    \newtheorem{proposition}{Proposition}[chapter]
  - |
    \newtheorem{designrule}{Design Rule}[chapter]
  - |
    \newcommand{\ERP}{\textsc{erp}}
  - |
    \newcommand{\PLM}{\textsc{plm}}
  - |
    \newcommand{\MES}{\textsc{mes}}
  - |
    \newcommand{\EAM}{\textsc{eam}}
  - |
    \newcommand{\QMS}{\textsc{qms}}
---

# Preface

Industrial information systems are rarely short of data. They are short of agreement about what the data denotes. A part number may denote a design family in one system, an orderable item in another, a plant-specific planning object in a third, and a physical serialized unit in casual conversation. A machine name may denote a functional position, a logical production resource, a maintenance record, or the device currently bolted to the floor. Integration projects fail when these distinctions are postponed until implementation and rediscovered as nullable columns, brittle mapping tables, and exceptions in message handlers.

This book develops a mathematical theory for that problem. Its subject is not an ontology in the narrow sense of a taxonomy. An **ERP system ontology** is a controlled account of the entities, relations, identity criteria, transformations, evidence, time, and coherence laws that organize an industrial information landscape. The intended landscape includes product-lifecycle management, enterprise resource planning, manufacturing execution, quality management, maintenance and asset management, warehouse and logistics systems, industrial data platforms, and digital-twin representations.

The central thesis is:

> An industrial ontology should be designed first as a compositional mathematical theory, refined second as an executable dependent type theory, and merged finally as a homotopical structure in which identifications and their coherence are explicit data.

The three parts correspond to three levels of semantic control.

**Part I** uses category theory. A local ontology is presented as a category or categorical schema. Its objects are concepts; its arrows are typed aspects or relationships; its path equations are business laws. A database instance is a set-valued functor. Schema mappings are functors. Data migrations arise functorially. Shared semantic interfaces and pushouts make ontology merging an explicit construction rather than a name-matching exercise. Lean 4 is used as a small laboratory for definitions and proofs.

**Part II** moves from diagrams to dependent types. Industrial identifiers are indexed by their system and kind. Business relations carry evidence. Workflows become indexed state machines. Quantities are indexed by dimension. Configurations are indexed by revisions and effectivity conditions. Queries can return both an answer and a proof of why the answer is admissible. Lean 4 is used here not merely to draw the theory but to execute and verify fragments of it.

**Part III** changes the organizing notion of identity. In homotopy type theory, equality is a space of paths rather than a proof-irrelevant Boolean fact. An approved correspondence between two local concepts can be retained as a path; competing or composite correspondences can be compared by higher paths; a merge can be generated as a homotopy pushout; and set truncation can deliberately extract the flat identities needed by conventional databases without confusing that operational view with the richer design theory. This is the part in which HoTT is not decoration. It supplies the core architecture of coherent ontology integration.

The framework proposed here is a research program and an engineering method, not an existing industrial standard. Category-theoretic databases, ologs, dependent type theory, univalence, higher inductive types, and industrial standards are established subjects. Their synthesis into a theory of ERP system ontologies is the book's constructive proposal. Statements called *design propositions* should therefore be read as claims with explicit assumptions, suitable for formalization and empirical validation, rather than as universally accepted doctrine.

## Intended audience

The primary reader is a software architect, formal-methods engineer, data architect, systems engineer, or mathematically inclined domain expert working on industrial integration. The text assumes ordinary programming experience and comfort with types and functions. It introduces the required category theory and dependent type theory, but it proceeds quickly. Prior exposure to Lean, Agda, Coq, Idris, Haskell, Rust, or a proof assistant is useful but not required.

The book also supports three distinct uses:

1. a design text for a conventional ERP or digital-thread architecture;
2. a Lean 4 course in domain modeling and proof-oriented programming;
3. a specification for a future HoTT-native ontology and proof engine.

## How to read the notation

A local ontology is usually written as a capital letter such as $P$ for PLM, $E$ for ERP, $M$ for MES, $A$ for asset management, and $Q$ for quality. A shared interface is written $K$. A functor $F : C \to D$ maps one ontology or schema to another. The category of instances on schema $C$ is written $C\text{-Inst}$. A homotopy pushout is written $P \sqcup^{h}_{K} E$. The type of equivalences between $A$ and $B$ is written $A \simeq B$. Set truncation is written $\lVert X \rVert_0$.

Lean code is written against a small, self-contained vocabulary where practical. Some snippets are deliberately pedagogical rather than library-optimal. The mathematical content does not depend on Mathlib's exact module names. Lean 4 evolves; the current stable release at the time of this edition is in the 4.32 line, and readers should expect minor import or syntax adjustments in later releases [R1, R2].

## The running case: a pump train

The book follows one physical pump train through an industrial digital thread. The same industrial reality appears in several contexts:

| Context | Representative object | Primary denotation |
|---|---|---|
| PLM | `PUMP-2000 / Rev C` | an approved engineering revision |
| ERP | `Item 4711`, plant 1000 | a plant-planned commercial or manufactured item |
| MES | `MaterialDefinition M-82` | a production-execution material definition |
| Inventory | `Lot L-882` | a batch of material or units |
| Serialization | `Serial S-1044` | one physical unit |
| EAM | `Asset E-90017` | a maintainable asset record |
| Plant model | `FunctionalPosition CP-4` | a persistent functional position |
| QMS | `InspectionResult IR-603` | evidence about a characteristic of a unit or lot |

The entire theory begins by refusing to call all of these objects “the pump.” Their relationships are modeled instead.

# Part I. Categories and Local Industrial Ontologies

# Chapter 1. Ontology Before Integration

## 1.1 The semantic failure hidden by successful transport

An integration can be operationally successful and semantically false. A message leaves PLM, enters ERP, survives JSON validation, and creates a row. Every transport-level metric is green. The row may still denote the wrong kind of thing.

Suppose PLM emits:

```json
{
  "partNumber": "PUMP-2000",
  "revision": "C",
  "massKg": 84.2
}
```

ERP imports it into an `Item` table. Four interpretations are possible:

- the item *is identical to* revision C;
- the item *realizes* revision C in a particular plant;
- the item *is classified by* the part definition, with revision handled elsewhere;
- the item record merely *represents a local claim* about revision C.

Those interpretations support different lifecycle rules. If revision D is released, does the ERP identifier remain? Can stock built to revision C still be issued? Is supplier part `ACME-X9` the same item or an approved alternative? Does a serial number built under a deviation conform to revision C, to a derived configuration, or to neither? No serializer can answer these questions. They belong to the ontology.

An ontology therefore precedes a canonical data model. It states the commitments that make a canonical model meaningful.

## 1.2 Ontology as a mathematical theory

For this book, an ontology contains six components:

1. **sorts or entity kinds**, such as `ProductRevision`, `MaterialLot`, and `FunctionalPosition`;
2. **typed relations or aspects**, such as `revisionOf`, `conformsTo`, and `installedAt`;
3. **composition**, so a chain of relations has a determined meaning;
4. **equations**, stating when two chains mean the same thing;
5. **admissibility conditions**, including time, authority, quantity, state, and scope;
6. **identity rules**, specifying what counts as the same entity, an equivalent representation, or merely related evidence.

This is closer to an algebraic theory or a program interface than to a thesaurus. A vocabulary without laws cannot control integration. A class hierarchy without identity criteria cannot control record merging.

### Principle: contextual identity

An identifier has meaning only relative to a context and an entity kind.

In notation:

$$
\operatorname{Ref}(s,k)
$$

is the type of references belonging to system or bounded context $s$ and denoting kind $k$. The string `4711` by itself is not an industrial identity. It becomes one only as, for example,

$$
4711 : \operatorname{Ref}(\mathrm{ERP}_{1000},\mathrm{PlantItem}).
$$

### Principle: stratified identity

Industrial systems must distinguish at least the following strata when they occur:

| Stratum | Typical question |
|---|---|
| definition | What kind of product or material is this? |
| revision or version | Under which controlled design state? |
| commercial/planning object | What can be bought, planned, valued, or stocked? |
| lot or batch | Which jointly produced or received population? |
| serialized unit | Which individual physical unit? |
| functional role or position | What persistent job in the plant is being fulfilled? |
| information record | Which system representation asserts something about it? |

Identity does not automatically move between strata. A serial realizes a revision but is not that revision. An asset record represents a unit but need not be the unit. A functional position can persist while its installed unit changes.

## 1.3 Bounded contexts as local theories

ERP, PLM, MES, EAM, and QMS are not simply applications that happen to duplicate master data. Each is a local theory optimized for a different form of reasoning.

PLM asks what was designed and approved. ERP asks what can be planned, procured, valued, and accounted for. MES asks what resources and materials are required and what was actually consumed or produced. EAM asks what is installed, maintainable, inspected, or replaced. QMS asks what characteristic was required, measured, accepted, or found nonconforming.

Trying to erase those local theories into one universal `Asset` or `Product` entity removes distinctions that the enterprise later needs. The objective is therefore not a single vocabulary. It is a family of local theories with explicit, coherent bridges.

We write:

$$
P, E, M, A, Q
$$

for the local ontologies of PLM, ERP, MES, EAM, and QMS. A bridge between two theories is not initially an equality. It is a typed mapping whose strength must be declared.

## 1.4 Correspondence is not one relation

A practical ontology needs a vocabulary of cross-context relationships. The following are intentionally distinct:

```text
SameEntity
EquivalentRepresentation
Represents
Classifies
Instantiates
Realizes
ConformsTo
Commercializes
ManufacturedAccordingTo
InstalledAt
PlaysRole
DerivedFrom
Supersedes
ApprovedSubstituteFor
PotentialMatch
```

For the running case, plausible assertions include:

```text
Serial S-1044 conformsTo PartRevision PUMP-2000/C
AssetRecord E-90017 represents Serial S-1044
Serial S-1044 installedAt FunctionalPosition CP-4 during I₁
Serial S-2088 installedAt FunctionalPosition CP-4 during I₂
ERP PlantItem 4711 realizes PartRevision PUMP-2000/C under policy π
```

Only the second and fifth lines are even candidates for stronger equivalence-like treatment, and both require scope. A record may be an equivalent representation for a restricted API while differing in provenance, temporal history, or fields. A plant item may represent several approved revisions depending on effectivity.

### Design rule: do not quotient uncertainty

A probabilistic or pending match is not an identity constructor. Keep it as a claim with evidence, confidence, status, and reviewer. Quotienting uncertain matches prematurely destroys the information required to reverse a merge, investigate an error, or satisfy audit requirements.

## 1.5 Competency questions

A formal ontology should be justified by the questions it must answer. The running case uses these:

1. Which engineering revision governed serial `S-1044` at manufacture?
2. Which material lots were consumed to produce it?
3. Which deviations and substitutions were active for that production order?
4. Which physical unit occupied functional position `CP-4` when alarm `AL-77` occurred?
5. Does the as-maintained configuration still satisfy an approved configuration rule?
6. Why does ERP plant item `4711` map to MES material definition `M-82`?
7. Do the direct ERP-to-MES mapping and the route through PLM agree?
8. Which facts would become invalid if an alignment approval were revoked?

These questions determine the needed entity kinds, paths, time model, provenance model, and coherence laws. A `GET /assets/{id}` API is not a competency question; it presupposes the ontology that the project is meant to discover.

## 1.6 A first Lean vocabulary

Lean lets us make the contextual nature of references explicit before introducing any category theory.

```lean
inductive System
  | plm | erp | mes | eam | qms
  deriving Repr, DecidableEq

inductive Kind
  | productDefinition
  | productRevision
  | plantItem
  | materialDefinition
  | materialLot
  | serializedUnit
  | assetRecord
  | functionalPosition
  | inspectionResult
  deriving Repr, DecidableEq

structure Ref (system : System) (kind : Kind) where
  raw : String
  deriving Repr, DecidableEq

abbrev PartRevisionId := Ref .plm .productRevision
abbrev PlantItemId := Ref .erp .plantItem
abbrev SerialId := Ref .mes .serializedUnit
abbrev AssetRecordId := Ref .eam .assetRecord
abbrev PositionId := Ref .eam .functionalPosition
```

A function accepting a `PartRevisionId` cannot accidentally receive a `PlantItemId`, even when both wrap strings. This is a modest type-level result. It already blocks an entire family of semantic mistakes.

The deeper problem begins when we ask how these kinds and their relations compose. Category theory supplies the first answer.

## 1.7 Exercises

1. List five identifiers from an industrial system you know. Assign each a system and kind. Identify any string that is currently reused across kinds.
2. For one “asset” table, classify every column according to whether it describes a definition, revision, physical unit, role, position, record, or event.
3. Give an example in which `SameEntity` is too strong but `Represents` is too weak. State the missing relation and its scope.
4. Write three competency questions whose answers require both valid time and transaction time.

# Chapter 2. Categories from Industrial Diagrams

## 2.1 Objects, arrows, and composition

A category $C$ consists of:

- a collection of objects $\operatorname{Ob}(C)$;
- for every pair $X,Y$, a collection of arrows $C(X,Y)$;
- an identity arrow $\operatorname{id}_X : X \to X$;
- composition taking $f : X \to Y$ and $g : Y \to Z$ to $g \circ f : X \to Z$;
- identity and associativity laws.

In an industrial ontology, an object is an entity kind and an arrow is a total, single-valued aspect in a declared scope. For example:

$$
\mathrm{PartRevision}
\xrightarrow{\mathrm{revisionOf}}
\mathrm{PartDefinition}.
$$

If every assembly occurrence belongs to one parent revision and selects one child revision, we may also have:

$$
\mathrm{AssemblyOccurrence}
\xrightarrow{\mathrm{parent}}
\mathrm{PartRevision},
\qquad
\mathrm{AssemblyOccurrence}
\xrightarrow{\mathrm{child}}
\mathrm{PartRevision}.
$$

Composition gives longer meaningful aspects. If a material actual points to a lot and the lot points to a material definition, then:

$$
\mathrm{MaterialActual}
\xrightarrow{\mathrm{lot}}
\mathrm{MaterialLot}
\xrightarrow{\mathrm{definition}}
\mathrm{MaterialDefinition}
$$

composes to the material definition of the actual.

The categorical discipline matters because every composite receives a type. A path that attempts to compose `installedAt` with `revisionOf` is rejected unless the intermediate objects match.

## 2.2 Path equations as business laws

The schema becomes informative when two paths are required to agree. Suppose an `AssemblyOccurrence` points directly to a `ProductDefinition`, but it also points to a child revision, which in turn points to its definition:

```text
AssemblyOccurrence ──childRevision──▶ PartRevision
        │                                  │
        │ childDefinition                  │ revisionOf
        ▼                                  ▼
  PartDefinition ◀────────────────── PartDefinition
```

The law is:

$$
\mathrm{childDefinition}
=
\mathrm{revisionOf} \circ \mathrm{childRevision}.
$$

This is not a comment. It is a consistency condition on every valid data instance. A database can enforce it with a constraint, a reconciliation query, or a verified import function. The ontology states the invariant independently of the enforcement mechanism.

Other industrial path equations include:

- the plant of a production order equals the plant of its work center;
- the material definition reached through an actual lot equals the definition declared by the material actual;
- the unit of a measurement agrees with the unit required by its characteristic, after an approved conversion;
- the product definition reached from a serial's build revision agrees with the definition reached through its ERP item mapping.

## 2.3 Why arrows are not arbitrary relationships

A category's arrows behave like composable functions. Many business relationships are partial or many-to-many. They should not be forced into a functional arrow without changing the model.

There are several standard repairs:

1. **Reify the relationship as an entity.** `InstalledAt` becomes an installation assignment object with arrows to a unit, a position, and an interval.
2. **Use a relation-valued model.** This is appropriate for graph or allegorical treatments but changes the basic semantics.
3. **Use spans or profunctors.** A many-to-many bridge is represented by a witness object between its endpoints.
4. **Use dependent types.** The fiber over an entity contains its admissible related entities and evidence.

For ERP ontologies, reification is often the best first move because the relation usually has attributes: time, quantity, source document, confidence, approval, and reason.

Thus instead of a partial arrow

$$
\mathrm{SerializedUnit} \dashrightarrow \mathrm{FunctionalPosition},
$$

we introduce:

$$
\begin{aligned}
\mathrm{Installation} &\to \mathrm{SerializedUnit},\\
\mathrm{Installation} &\to \mathrm{FunctionalPosition},\\
\mathrm{Installation} &\to \mathrm{Interval}.
\end{aligned}
$$

## 2.4 A minimal category in Lean 4

The following definition is intentionally small. It makes no use of Mathlib.

```lean
universe u v

structure SmallCategory where
  Obj : Type u
  Hom : Obj → Obj → Type v
  id : {X : Obj} → Hom X X
  comp : {X Y Z : Obj} → Hom Y Z → Hom X Y → Hom X Z
  id_comp : ∀ {X Y} (f : Hom X Y), comp id f = f
  comp_id : ∀ {X Y} (f : Hom X Y), comp f id = f
  assoc : ∀ {W X Y Z}
    (h : Hom Y Z) (g : Hom X Y) (f : Hom W X),
    comp h (comp g f) = comp (comp h g) f
```

The order of `comp` is chosen so that `comp g f` means $g \circ f$. A functor preserves the structure.

```lean
structure Functor (C D : SmallCategory) where
  obj : C.Obj → D.Obj
  map : {X Y : C.Obj} → C.Hom X Y → D.Hom (obj X) (obj Y)
  map_id : ∀ {X : C.Obj}, map (@C.id X) = @D.id (obj X)
  map_comp : ∀ {X Y Z : C.Obj}
    (g : C.Hom Y Z) (f : C.Hom X Y),
    map (C.comp g f) = D.comp (map g) (map f)
```

The laws prevent a schema mapping from preserving names while changing composition. That distinction will become central: a cross-system mapping is valid only when it preserves the declared meaning of paths.

## 2.5 Free paths from a graph

Industrial schemas are usually presented by generators and equations. Begin with object kinds and primitive edges, then construct paths freely.

```lean
universe u v

inductive Path {Obj : Type u} (Edge : Obj → Obj → Type v) :
    Obj → Obj → Type (max u v)
  | nil : Path Edge X X
  | cons : Edge X Y → Path Edge Y Z → Path Edge X Z

namespace Path

variable {Obj : Type u} {Edge : Obj → Obj → Type v}

protected def append : Path Edge X Y → Path Edge Y Z → Path Edge X Z
  | .nil, q => q
  | .cons e p, q => .cons e (p.append q)

@[simp] theorem nil_append (p : Path Edge X Y) :
    (Path.nil : Path Edge X X).append p = p := rfl

@[simp] theorem append_nil (p : Path Edge X Y) :
    p.append Path.nil = p := by
  induction p with
  | nil => rfl
  | cons e p ih => simp [Path.append, ih]

@[simp] theorem append_assoc
    (p : Path Edge W X) (q : Path Edge X Y) (r : Path Edge Y Z) :
    (p.append q).append r = p.append (q.append r) := by
  induction p with
  | nil => rfl
  | cons e p ih => simp [Path.append, ih]

end Path
```

The free path category contains every well-typed chain of primitive edges. A presented schema then adds an equivalence relation on paths generated by business equations. This distinction is useful in practice:

- the graph says what can be composed;
- the equations say which composites must agree;
- the instance says which concrete data realizes the presentation.

## 2.6 Workflow categories

Categories also model transitions. Let objects be lifecycle states:

```text
Planned → Released → Executing → Completed → Closed
```

An arrow is an admissible transition sequence. Composition is sequencing. Identity is “do nothing.” The category makes illegal transitions absent rather than false.

A workflow category is not yet a full process model. It omits concurrency, compensation, resources, and temporal duration. Later chapters will refine it with dependent types. Still, it establishes a critical principle: admissibility belongs in the shape of the theory, not only in runtime `if` statements.

## 2.7 Thin categories and classifications

A preorder $(P,\leq)$ generates a thin category: there is at most one arrow from $x$ to $y$, existing exactly when $x \leq y$. Classification hierarchies, capability inclusion, and “is no more specific than” relations often fit this form.

For example:

```text
Metal
  ├── FerrousMetal
  │     └── StainlessSteel
  └── NonFerrousMetal
        └── AluminumAlloy
```

If a machine capability is monotone along the material classification, a capability for `Metal` implies a capability for `StainlessSteel`. The 2015 manufacturing example in functorial data migration used this kind of semantic enrichment in a distributed supply-chain scenario [R8].

The thinness assumption is substantial. If two distinct classification derivations carry different standards, jurisdictions, or evidence, they should not be collapsed into one arrow. HoTT will later give us a principled way to retain multiple paths.

## 2.8 Exercises

1. Present a category for purchase-to-pay states. Identify which “transitions” should instead be events with attributes.
2. Reify a many-to-many relationship between material definitions and approved substitutes.
3. State a commuting square involving an inspection result, characteristic, unit, and measurement procedure.
4. In Lean, add a `mapPath` function that maps paths along an edge mapping. Prove that it preserves `append`.

# Chapter 3. Ologs and Categorical Schemas

## 3.1 From diagrams to controlled prose

An olog, or ontology log, uses category-theoretic diagrams as a knowledge-representation language. Objects are types of things, arrows are functional aspects, and commuting diagrams state facts about composition. Ologs were proposed as a disciplined way to record local worldviews and connect them by functors [R5].

The important word is *local*. An olog need not pretend to be the final universal ontology. A maintenance engineer and a production planner may construct different valid diagrams because they ask different questions. Integration then becomes the formal task of comparing those diagrams.

A useful naming convention writes object labels as noun phrases beginning “a” or “an” and arrow labels as verb phrases that form grammatical sentences. For example:

```text
[a serialized pump]
       ── was manufactured according to ──▶
[an approved pump revision]
```

The linguistic discipline catches ambiguity early. “has type” is usually too vague: does it mean classification, programming type, engineering design, commercial item category, equipment class, or runtime variant?

## 3.2 A PLM fragment

Consider the following PLM schema:

```text
PartDefinition ←revisionOf— PartRevision
       ▲                         ▲
       │ parentDefinition        │ parentRevision
       │                         │
AssemblyOccurrence ─childRevision─▶ PartRevision
       │
       └──── childDefinition ────▶ PartDefinition
```

Two equations are expected:

$$
\mathrm{parentDefinition}
=
\mathrm{revisionOf}\circ\mathrm{parentRevision},
$$

$$
\mathrm{childDefinition}
=
\mathrm{revisionOf}\circ\mathrm{childRevision}.
$$

An assembly occurrence is an occurrence *within a controlled parent revision*. Treating it merely as a pair of part definitions loses effectivity, quantity, position, alternates, and occurrence identity. These can be added as arrows from the reified occurrence.

## 3.3 An ERP fragment

An ERP schema may contain:

```text
PlantItem ─itemOf────────▶ Item
PlantItem ─validAt───────▶ Plant
PlantItem ─baseUnit──────▶ UnitOfMeasure
MaterialLot ─lotOf───────▶ PlantItem
StockPosition ─lot───────▶ MaterialLot
StockPosition ─location──▶ StorageLocation
StockPosition ─quantity──▶ Quantity
```

ERP's `Item` does not necessarily correspond to PLM's `PartDefinition`. Some items are services, packaging, tools, indirect materials, configured products, or accounting objects. A schema mapping must state a restricted subdomain or introduce a more precise shared interface.

## 3.4 MES, EAM, and QMS fragments

MES often distinguishes a material definition, a material lot, a material requirement, and a material actual. It may distinguish logical equipment from a physical asset. ISA-95 and the corresponding OPC UA companion model explicitly separate classes, definitions, lots, equipment roles, and physical assets; this separation is a valuable source of ontology tests rather than a mandate to copy the standard wholesale [R12, R13].

EAM should distinguish:

```text
PhysicalUnit
AssetRecord
FunctionalPosition
InstallationAssignment
MaintenanceOrder
MaintenanceExecution
```

QMS should distinguish:

```text
CharacteristicDefinition
InspectionSpecification
InspectionExecution
Measurement
AcceptanceDecision
Nonconformance
```

The characteristic definition is not the measurement. The measurement is not the acceptance decision. The nonconformance is not simply `measurement > limit`; it may be a controlled business object with disposition, concession, and closure.

## 3.5 Records are representations

A decisive modeling move is to introduce an information stratum:

```text
SystemRecord ─representsDuring──▶ DomainEntity
SystemRecord ─storedIn──────────▶ System
SystemRecord ─assertedAt────────▶ TransactionTime
```

The relation `representsDuring` is usually reified because it may be partial, time-scoped, or disputed. The resulting distinction permits two EAM records to represent the same physical unit while retaining different record histories. It also permits one record to change what it represents after a correction without pretending that the physical object changed identity.

### Counterexample: the global master row

A common canonical model creates one row:

```text
GlobalAsset(id, plm_id, erp_id, mes_id, eam_id, ...)
```

This conflates three assertions:

1. all local records denote one underlying entity;
2. the entity has one stable cross-system identity;
3. each local identifier is functional and current.

Any of these may fail. A part revision may map to many plant items; a plant item may cover multiple revisions by effectivity; a physical unit may have several historical asset records; a functional position may host many units over time. The correct canonical object is often an *alignment claim* or *assignment*, not a wide master row.

## 3.6 A schema signature in Lean

We can represent a graph of object kinds and primitive edges.

```lean
structure Schema where
  Obj : Type
  Edge : Obj → Obj → Type

namespace PumpSchema

inductive Obj
  | partDefinition
  | partRevision
  | serial
  | assetRecord
  | position
  | installation
  deriving Repr, DecidableEq

inductive Edge : Obj → Obj → Type
  | revisionOf : Edge .partRevision .partDefinition
  | conformsTo : Edge .serial .partRevision
  | recordRepresents : Edge .assetRecord .serial
  | installUnit : Edge .installation .serial
  | installPosition : Edge .installation .position

abbrev S : Schema := ⟨Obj, Edge⟩

end PumpSchema
```

The type indices reject malformed edges. A path from `.serial` to `.partDefinition` can be constructed by composing `conformsTo` with `revisionOf`; a path from `.position` to `.partRevision` cannot be constructed from this signature.

```lean
open PumpSchema

example : Path Edge .serial .partDefinition :=
  .cons Edge.conformsTo (.cons Edge.revisionOf .nil)
```

This is syntax, not yet an ontology instance. We still need meanings for objects and edges, and equations between paths.

## 3.7 Presentations and path congruence

A finitely presented categorical schema consists of a finite graph plus a set of path equations. Formally, one takes the free category on the graph and quotients paths by the smallest congruence containing the equations. “Congruence” means equations are preserved when paths are composed on either side.

For production tooling, a presentation is often preferable to enumerating all arrows. It is close to a schema definition language:

```text
objects:
  PartDefinition PartRevision AssemblyOccurrence

arrows:
  revisionOf      : PartRevision -> PartDefinition
  parentRevision  : AssemblyOccurrence -> PartRevision
  childRevision   : AssemblyOccurrence -> PartRevision
  parentDefinition: AssemblyOccurrence -> PartDefinition
  childDefinition : AssemblyOccurrence -> PartDefinition

equations:
  parentDefinition = parentRevision ; revisionOf
  childDefinition  = childRevision  ; revisionOf
```

The semicolon here means “then.” A compiler can translate the same presentation into Lean declarations, SQL constraints, graph validations, documentation, and diagram renderings.

## 3.8 Partiality, optionality, and null

A total arrow is a strong assertion. `Serial -> BuildRevision` means every serial has exactly one build revision. If legacy data can lack that information, there are three conceptually different responses:

- weaken the instance by using `Option BuildRevision`;
- model an explicit `UnknownBuildRevision` value;
- preserve a total domain law while representing the legacy database as an incomplete observation of the domain.

These choices are not equivalent. `Option` changes the ontology to permit absence. An explicit unknown value turns ignorance into an object and may create false equalities. Treating the database as a partial observation preserves the target theory but requires an error or completion semantics.

The right choice depends on whether the absence is permitted in reality, permitted only in a workflow state, or merely a defect in data capture. Dependent types will let us make those conditions explicit.

## 3.9 Exercises

1. Write an olog fragment for a supplier part, manufacturer part, and approved source list. Avoid using the phrase “same part.”
2. Find three relationships in an ERP database currently implemented by nullable foreign keys. Decide whether each should be optional, state-indexed, or reified.
3. Add `InstallationInterval` and `EvidenceRecord` to the Lean schema. Which arrows become path equations?
4. Give an example where two local ontologies are both internally consistent but cannot be connected by a functor without restricting one of them.

# Chapter 4. Instances as Functors

## 4.1 A schema is not its data

A schema describes possible shapes and laws. An instance supplies concrete inhabitants. In the functorial data model, an instance on a schema category $C$ is a functor

$$
I : C \to \mathbf{Set}.
$$

For every object $X$ in the schema, $I(X)$ is a set of rows or entity occurrences. For every arrow $f : X \to Y$, $I(f)$ is a function $I(X) \to I(Y)$. Functoriality requires identities and composition to be preserved.

This recovers familiar database structure:

| Categorical element | Database interpretation |
|---|---|
| object $X$ | entity table or typed population |
| element $x \in I(X)$ | row identifier |
| arrow $f : X \to Y$ | total foreign key or typed attribute |
| function $I(f)$ | foreign-key lookup |
| path equation | integrity constraint |
| natural transformation | structure-preserving instance map |

If the schema asserts $h = g \circ f$, every instance must satisfy

$$
I(h)(x) = I(g)(I(f)(x))
$$

for every $x$. A commuting diagram is therefore an executable data-quality condition.

## 4.2 The running instance

Let the schema contain:

```text
Serial ─conformsTo─▶ PartRevision ─revisionOf─▶ PartDefinition
Serial ─productDefinition─────────────────────▶ PartDefinition
```

and the equation

$$
\mathrm{productDefinition}
=
\mathrm{revisionOf}\circ\mathrm{conformsTo}.
$$

An instance may contain:

```text
Serial = {S-1044, S-2088}
PartRevision = {PUMP-2000/C, PUMP-2000/D}
PartDefinition = {PUMP-2000}

conformsTo(S-1044) = PUMP-2000/C
conformsTo(S-2088) = PUMP-2000/D
revisionOf(PUMP-2000/C) = PUMP-2000
revisionOf(PUMP-2000/D) = PUMP-2000
productDefinition(S-1044) = PUMP-2000
productDefinition(S-2088) = PUMP-2000
```

The path equation prevents an import from asserting that `S-1044` directly belongs to `PUMP-3000` while its build revision belongs to `PUMP-2000`.

## 4.3 An interpretation in Lean

The graph-level schema from Chapter 3 can be interpreted in Lean types and functions.

```lean
universe u

structure Interpretation (S : Schema) where
  obj : S.Obj → Type u
  edge : {X Y : S.Obj} → S.Edge X Y → obj X → obj Y

namespace Interpretation

variable {S : Schema} (I : Interpretation S)

protected def evalPath : {X Y : S.Obj} →
    Path S.Edge X Y → I.obj X → I.obj Y
  | _, _, .nil => id
  | _, _, .cons e p => fun x => I.evalPath p (I.edge e x)

@[simp] theorem eval_nil {X : S.Obj} (x : I.obj X) :
    I.evalPath (Path.nil : Path S.Edge X X) x = x := rfl

@[simp] theorem eval_append
    (p : Path S.Edge X Y) (q : Path S.Edge Y Z) (x : I.obj X) :
    I.evalPath (p.append q) x = I.evalPath q (I.evalPath p x) := by
  induction p with
  | nil => rfl
  | cons e p ih => simp [Path.append, Interpretation.evalPath, ih]

end Interpretation
```

The `eval_append` theorem is functoriality for free paths. An interpretation automatically respects path composition because path evaluation is defined by function composition.

To model a presented schema, add laws for the declared equations. For a particular equation $p=q$:

```lean
structure EquationLaw (I : Interpretation S)
    (p q : Path S.Edge X Y) : Prop where
  sound : ∀ x, I.evalPath p x = I.evalPath q x
```

A valid instance packages an interpretation with proofs of all required equation laws. In a generated implementation, the schema compiler can produce one proof obligation per path equation.

## 4.4 Natural transformations as instance mappings

Given two instances $I,J : C \to \mathbf{Set}$, a natural transformation

$$
\eta : I \Rightarrow J
$$

assigns a function $\eta_X : I(X) \to J(X)$ to every object, subject to naturality. For each arrow $f : X \to Y$:

$$
J(f)\circ\eta_X = \eta_Y\circ I(f).
$$

In database language, mapping a row and then following a foreign key must give the same result as following the foreign key and then mapping the target row.

This is a strong notion of instance migration. It rules out a common defect: a header row is mapped to one target document while its line rows map to a different target header. Naturality makes referential coherence part of the mapping's type.

A Lean-level version for graph interpretations is:

```lean
structure InstanceMap {S : Schema}
    (I J : Interpretation S) where
  app : (X : S.Obj) → I.obj X → J.obj X
  natural : ∀ {X Y : S.Obj} (e : S.Edge X Y) (x : I.obj X),
    app Y (I.edge e x) = J.edge e (app X x)
```

The orientation of the equality is immaterial; its content is the commuting square.

## 4.5 Attributes and concrete values

The simplest functorial model treats strings, dates, decimals, and units as additional objects. For example:

```text
PartRevision ─revisionCode─▶ String
PartRevision ─releaseDate──▶ Date
MaterialLot ─quantity──────▶ Decimal
MaterialLot ─unit──────────▶ UnitOfMeasure
```

This is useful but incomplete. Concrete values have operations and equations: decimal addition, date ordering, unit conversion, string normalization, and dimensional analysis. Algebraic database models extend set-valued instances with multisorted algebraic theories so concrete data and operations are represented systematically [R9].

For industrial use, it is helpful to separate:

- **entity sorts**, whose elements carry identity;
- **value sorts**, whose elements are compared extensionally;
- **controlled vocabulary sorts**, whose terms are versioned and governed;
- **measurement sorts**, whose values include units, uncertainty, and procedure.

The difference determines how merging and equality should behave. Two temperature readings of `20 °C` can be equal as values while remaining distinct observations because they were made at different times or by different instruments.

## 4.6 Incomplete and inconsistent instances

Real databases rarely satisfy the ideal schema. We should distinguish three conditions.

An **incomplete instance** lacks a value required by the target theory. An **inconsistent instance** supplies values that violate an equation or constraint. An **open-world instance** intentionally leaves some facts undecided because additional facts may exist outside the system.

These conditions need different remediation:

| Condition | Typical response |
|---|---|
| incomplete | repair, infer with evidence, or represent partial observation |
| inconsistent | reject, quarantine, or retain competing claims explicitly |
| open-world | avoid closed-world negation; query under declared assumptions |

A category-valued model by itself does not solve uncertainty or partiality. It clarifies where the ideal laws are and therefore where defects occur. Later, evidence-bearing dependent types will represent the status of claims instead of forcing every row into a supposedly valid instance.

## 4.7 Database views as functorial observations

A bounded context often sees only a projection of a richer ontology. ERP may observe the product definition and approved plant items but not detailed geometric revisions. Maintenance may observe serialized components and functional positions but not procurement valuation.

A view can be modeled by a functor $V : C \to D$ or, depending on variance, by reindexing an instance along such a functor. The important point is that a view is not merely a selected column list. It declares how the observed paths relate to the source paths.

This gives a criterion for API stability: a versioned API is stable when the new view remains naturally equivalent to the old view on the contractually visible fragment, even if the internal schema changes.

## 4.8 Exercises

1. Encode a three-table schema as an `Interpretation`. State one `EquationLaw` that corresponds to a foreign-key consistency rule.
2. Give an instance mapping that fails naturality. Explain the corresponding industrial integration defect.
3. Classify five columns as entity-valued, value-valued, vocabulary-valued, or measurement-valued.
4. Design an explicit representation of an incomplete instance that does not silently add an `Unknown` entity to every sort.

# Chapter 5. Functorial Data Migration

## 5.1 A mapping of schemas induces mappings of data

Let

$$
F : C \to D
$$

be a functor between schemas. The functor maps each source concept to a target concept and each source path to a target path while preserving identities, composition, and equations.

From $F$, three canonical data-migration operations arise in the functorial data model [R4]:

$$
\Delta_F : D\text{-Inst} \to C\text{-Inst},
$$

$$
\Sigma_F : C\text{-Inst} \to D\text{-Inst},
$$

$$
\Pi_F : C\text{-Inst} \to D\text{-Inst}.
$$

The first, $\Delta_F$, is reindexing by precomposition. Given $J : D \to \mathbf{Set}$,

$$
\Delta_F(J) = J \circ F.
$$

It reads a target instance through the vocabulary of the source schema. The other two are left and right Kan extensions and are adjoint to $\Delta_F$:

$$
\Sigma_F \dashv \Delta_F \dashv \Pi_F.
$$

The notation is compact, but the three operations correspond to recognizably different integration behavior.

## 5.2 Delta: restriction and contract views

Suppose a canonical ontology $D$ contains `ProductDefinition`, `ProductRevision`, `SerializedUnit`, `PhysicalAsset`, and `FunctionalPosition`. A plant API schema $C$ contains only `SerializedUnit`, `FunctionalPosition`, and their current assignment. A functor $F:C\to D$ tells how the API concepts are interpreted in the canonical ontology.

Then $\Delta_F$ restricts a canonical instance to the API view. It neither invents nor aggregates data. It changes the vocabulary through which the instance is observed.

In implementation terms, $\Delta$ often resembles projection, view definition, or query re-expression. Its categorical definition guarantees that path laws visible in the view are inherited from the source.

## 5.3 Sigma: integration by freely adding structure

The left migration $\Sigma_F$ moves source data forward while making the least identifications and additions required by the target schema. It behaves like a colimit or union-oriented integration.

A manufacturing example is importing supplier capability data into an enterprise capability schema. Several supplier-local concepts may map to one canonical material class. The left migration combines corresponding source populations and generates target structure subject to the schema equations.

This operation can merge identifiers. It therefore requires explicit policy. A left Kan extension is mathematically canonical relative to $F$; the choice of $F$ is where business semantics enters.

## 5.4 Pi: integration by compatible tuples

The right migration $\Pi_F$ moves data forward by collecting compatible families. It behaves like a limit or join-oriented integration.

For example, a target concept `ReleasePackage` may require a compatible part revision, manufacturing plan, inspection plan, and approval. A right-style migration can construct target records only from source tuples satisfying the shared relationships.

The distinction between $\Sigma$ and $\Pi$ mirrors a practical choice:

- combine what maps to the same target and propagate it forward;
- construct only compatible collections that jointly satisfy a target shape.

Calling both operations “ETL” hides this semantic difference.

## 5.5 Information loss and round trips

A migration should be evaluated by its round-trip laws. Given source $I$, compare it with a round trip such as

$$
I \longrightarrow \Delta_F\Sigma_F(I)
$$

or

$$
\Delta_F\Pi_F(I) \longrightarrow I.
$$

The unit and counit of the adjunction provide canonical comparison maps, but they are not generally isomorphisms. This fact is not a mathematical nuisance; it measures information loss, completion, or duplication.

For an ERP project, ask:

- Which source distinctions disappear under the mapping?
- Which target entities are generated?
- Can generated identities be traced to source witnesses?
- Does a round trip preserve source keys, or only observable behavior?
- Which laws hold only under scope conditions such as “one active revision per date”?

An adapter that serializes and deserializes successfully may still fail these semantic round trips.

## 5.6 A concrete mapping: PLM revisions to ERP items

Let $P$ contain:

```text
PartRevision ─revisionOf─▶ PartDefinition
```

and let $E$ contain:

```text
PlantItem ─itemOf─▶ Item
PlantItem ─plant──▶ Plant
```

There is no obvious total functor from $P$ to $E$. A PLM revision may be valid in several plants, and an ERP plant item may intentionally cover several revisions. The correct response is not to guess a mapping. Introduce an interface category $K$ that captures the scope under which the mapping is functional:

```text
EffectiveRevisionAtPlant
  ─revision─▶ PartRevision
  ─plant────▶ Plant
  ─realizedBy▶ PlantItem
```

Now the bridge is represented by witness objects. The relation itself carries effectivity and approval. The local schemas remain honest.

This pattern recurs: when a desired schema functor does not exist, reify the correspondence or restrict the domain until it does.

## 5.7 Queries as compositional migrations

A categorical query can be expressed as a composite

$$
C \xleftarrow{F} A \xrightarrow{G} B \xrightarrow{H} D
$$

with a corresponding instance migration such as

$$
\Sigma_H\Pi_G\Delta_F.
$$

The exact normal form varies by formalism, but the architectural lesson is stable: complex data movement is assembled from a small number of semantics-preserving operations. This is more analyzable than a sequence of opaque scripts whose intermediate schemas are implicit.

For a digital-thread query, the stages might be:

1. restrict the enterprise graph to serials, build orders, material actuals, and lots;
2. join compatible paths that prove a lot was consumed for a serial-producing execution;
3. project the result into a traceability API schema.

## 5.8 Manufacturing precedent

Functorial data migration has been demonstrated on a manufacturing-service capability scenario involving a distributed supply chain and semantic enrichment, developed in relation to NIST work [R8]. This does not establish that categorical databases are a turnkey ERP platform. It establishes that the mathematical machinery is not confined to toy examples and that manufacturing integration naturally exhibits the schema, mapping, enrichment, and migration structures the theory describes.

## 5.9 Exercises

1. Identify a data migration in your environment that is best described as restriction, union-like integration, or compatible-tuple construction.
2. State a source-to-target mapping that cannot be a functor because it fails to preserve a path equation.
3. For a versioned API, describe the unit or counit map that would express a round-trip test.
4. Design a query for “all lots consumed in the ancestry of a serial” as a sequence of restrict, join, and project stages.

# Chapter 6. Merging Ontologies Through Shared Interfaces

## 6.1 Why union is the wrong primitive

A union of schemas combines names. An ontology merge must combine meanings. Suppose PLM and ERP both contain a node called `Item`. A name-based union either identifies them without proof or keeps them separate without explaining their relation. Neither is a semantic merge.

The right primitive is a span from a shared interface:

$$
P \xleftarrow{f} K \xrightarrow{g} E.
$$

The interface $K$ contains exactly the concepts and paths that the two local ontologies agree to compare. The functors $f$ and $g$ state how that shared vocabulary is realized locally.

The pushout

$$
P \sqcup_K E
$$

is the schema generated by $P$ and $E$ while identifying the images of $K$ and imposing the consequences of those identifications.

## 6.2 Designing the interface

A good interface is smaller than either local ontology. For a PLM-ERP bridge it may contain:

```text
ProductDefinition
ProductRevision
Plant
EffectiveRealization
```

with arrows:

```text
EffectiveRealization ─definition─▶ ProductDefinition
EffectiveRealization ─revision───▶ ProductRevision
EffectiveRealization ─plant──────▶ Plant
```

PLM maps the product concepts to part definitions and revisions. ERP may map `EffectiveRealization` to a reified item-revision-effectivity record rather than directly to `PlantItem`. The interface is allowed to expose that the supposed one-to-one mapping was actually conditional.

### Design rule: interfaces encode common commitments, not common words

A concept belongs in $K$ only when both sides can preserve its relevant laws. A vague superclass such as `BusinessObject` creates a formally valid but semantically useless interface.

## 6.3 The universal property

The pushout is characterized by a universal property. Given maps

$$
P \xrightarrow{i_P} X,
\qquad
E \xrightarrow{i_E} X
$$

that agree on $K$,

$$
i_P \circ f = i_E \circ g,
$$

there is a unique induced map

$$
P \sqcup_K E \to X.
$$

For architecture, this says that any downstream model consuming both ontologies coherently factors through the merge. The merge is not merely a bag of copied concepts; it is the least theory satisfying the declared agreement.

The word *unique* will become problematic in Part III. In higher settings, induced maps are unique up to coherent homotopy rather than by strict equality. That is one reason homotopy pushouts fit ontology integration better than set-level pushouts.

## 6.4 A three-system diagram

Add MES. We may merge in stages:

$$
(P \sqcup_{K_{PE}} E) \sqcup_{K_{EM}} M.
$$

Or choose another order:

$$
P \sqcup_{K_{PM}} (E \sqcup_{K_{EM}} M).
$$

Under appropriate categorical assumptions these constructions are related, but an engineering implementation must still supply compatible interfaces and equations. The practical risk is route disagreement.

Suppose:

```text
ERP PlantItem 4711 ─direct────────▶ MES MaterialDefinition M-82
ERP PlantItem 4711 ─via PLM Rev C─▶ MES MaterialDefinition M-91
```

Each mapping may have been approved independently. Together they create an incoherent triangle. A global ontology must either:

- prove `M-82 = M-91` under the relevant notion of identity;
- distinguish the scopes in which each path applies;
- reject one mapping;
- retain both as a controlled ambiguity.

A plain pushout often hides the history of how the identification arose. The homotopy pushout of Part III will retain that information as paths.

## 6.5 Conservative merges

A merge is **conservative over a local ontology** when it does not create new local equalities or consequences except those justified by the interface and declared laws. This is an essential safety objective. A PLM theory should not accidentally identify two revisions merely because ERP maps both to one planning item.

A simple warning pattern is:

$$
f(k_1) \neq f(k_2) \text{ in } P,
\qquad
g(k_1)=g(k_2) \text{ in } E.
$$

The pushout may force the two PLM images together. That may be intended aggregation, or it may be destructive collapse. Before merging, analyze the fibers of each interface functor: which local distinctions does the other side forget?

### Design proposition: fiber review

For every interface mapping $f:K\to P$, review nontrivial pairs $k_1,k_2$ for which $f(k_1)=f(k_2)$ or which become observationally indistinguishable. These fibers are the precise locations where the mapping loses semantic resolution.

## 6.6 Alignment objects instead of strict identifications

When a relation has scope or evidence, put an alignment object in $K$ rather than identifying endpoints directly.

```text
Alignment
  ─left──────▶ PLM.PartRevision
  ─right─────▶ ERP.PlantItem
  ─relation──▶ RelationKind
  ─validity──▶ Interval
  ─authority─▶ Authority
  ─status────▶ ApprovalStatus
```

The merged ontology then contains both endpoints and the structured bridge. A later operation may extract a stricter equivalence from approved alignments satisfying additional conditions. This separates data acquisition from identity formation.

## 6.7 Merge diagnostics

A mathematical merge phase should produce diagnostics before any canonical schema is generated:

- **kind mismatch:** the endpoints live at different identity strata;
- **cardinality mismatch:** one side assumes a function, the other a relation;
- **path mismatch:** a mapped equation does not commute;
- **scope mismatch:** mappings use different plants, dates, jurisdictions, or product families;
- **resolution loss:** distinct local entities collapse in the interface;
- **cycle ambiguity:** multiple alignment paths have no comparison proof;
- **provenance erasure:** an identity would discard the evidence that justifies it.

These diagnostics are more valuable than an automatically generated “unified” graph because they reveal the design decisions the enterprise must make.

## 6.8 Exercises

1. Design a shared interface between an EAM functional-location model and an MES equipment model. State where the mapping is not functional.
2. Construct a span for supplier parts and internal items using an approved-source-list witness.
3. Give an example of a nonconservative merge and repair it by weakening an identification to a relation.
4. Find a commuting triangle that should be checked across three systems in your environment.

# Chapter 7. Time, Provenance, Quantities, and Standards

## 7.1 Industrial truth is indexed

The statement

```text
S-1044 is installed at CP-4
```

is incomplete. At minimum it needs valid time. Often it also needs transaction time and an authority:

```text
according to EAM record E-90017,
recorded on 2026-01-18,
S-1044 occupied CP-4 during [2025-03-12, 2026-01-17).
```

We should think of many industrial predicates as indexed families:

$$
\mathrm{InstalledAt}(u,p,t,e),
$$

where $u$ is a unit, $p$ a position, $t$ a valid-time interval, and $e$ evidence or authority.

Flattening this to a timeless edge loses replacement history and makes event reconstruction impossible.

## 7.2 Valid time and transaction time

**Valid time** is when a claim holds in the modeled world. **Transaction time** is when the information system stored or accepted the claim. They differ when data is entered late, corrected retroactively, or imported from another system.

A bitemporal assertion can be modeled as:

$$
\mathrm{Claim}(A, I_v, I_t),
$$

where $A$ is the asserted proposition, $I_v$ is a valid-time interval, and $I_t$ is a transaction-time interval. Revisions to historical data close one transaction interval and open another without rewriting history.

For ontology alignment, this distinction supports questions such as:

- Which mapping did the system use when the production order executed?
- What mapping do we now believe was correct for that date?
- Which reports were generated under the superseded mapping?

## 7.3 Provenance as first-class structure

An alignment should answer “why?” A practical evidence record includes:

```text
source system and record
source document or standard
mapping rule version
author or approving authority
valid-time interval
transaction-time interval
confidence or certainty class
approval status
supersession relation
scope assumptions
```

Provenance is not a comment attached after identity resolution. It is part of the type of an admissible bridge.

One useful distinction is between:

- **evidence for a claim**, such as a certificate or mapping rule;
- **the authority to accept a claim**, such as an engineering approval;
- **the derivation of a claim**, such as composition through other alignments.

HoTT will later treat derivations as paths and comparisons between derivations as higher paths. The operational fields remain necessary because mathematical equality alone does not encode governance.

## 7.4 Quantities and dimensions

Industrial ontology failures are often numerical but semantic. A quantity is not a decimal plus an optional unit string. It has a physical dimension, a unit, a scale, and often uncertainty and measurement context.

A safe model separates dimension from unit:

$$
\mathrm{Quantity}(d),
$$

where $d$ may be mass, length, time, count, temperature, or a compound dimension. Addition requires the same dimension. Conversion requires a proof that two units realize the same dimension and a conversion function satisfying the appropriate laws.

Count deserves special attention. `3 EA` can mean three serialized units, three packages, or three meters sold under an “each” commercial unit. The counted kind must be explicit when it matters:

$$
\mathrm{Count}(\mathrm{SerializedPump})
\neq
\mathrm{Count}(\mathrm{ShippingContainer}).
$$

## 7.5 Standards as source ontologies

Industrial standards are valuable inputs, but none should be treated as the single enterprise ontology.

**ISA-95 / IEC 62264** provides concepts for enterprise-control integration, including personnel, equipment, physical assets, materials, process segments, operations definitions, schedules, and performance. The OPC UA companion specification supplies a common object model for expressing ISA-95 structures [R12, R13]. It is especially useful for testing distinctions among equipment classes, role-based equipment, and physical assets.

**ISO 10303 AP242** addresses managed model-based 3D engineering and product manufacturing information, including product structures, assemblies, tools, raw materials, and product-data-management concerns [R16]. It is a strong source for PLM identity, revision, occurrence, and configuration concepts.

**Asset Administration Shell (AAS)** provides a metamodel and standardized submodel approach for industrial digital twins. The official specification repository published metamodel version 3.1.2 in late 2025, and the OPC UA companion work provides a mapping into OPC UA [R14, R15]. AAS is best treated as a representation framework whose submodels must still be aligned to local domain identities.

**GS1 EPCIS** models visibility events for traceability, organized around what happened, when, where, and why, with event types for object, aggregation, transaction, transformation, and association contexts [R17]. It is useful for event and supply-chain semantics, not as a complete engineering or maintenance ontology.

**ISO 15926** targets lifecycle integration for process plants. Its parts address upper ontology, reference data, RDF-based implementation and configuration management, and evolving reference vocabularies [R18–R20]. It is relevant when plant functions, equipment, facilities, and lifecycle records must remain interpretable across long asset lifetimes.

A company ontology should import selected fragments under explicit version identifiers. Standards evolve; an alignment to “AP242” or “AAS” without edition and profile is not reproducible.

## 7.6 Standards alignment as a functor with obligations

Suppose $S$ is a standard fragment and $L$ is a local ontology. A mapping

$$
F : S \to L
$$

claims that local concepts realize the standard's structure. The mapping is valid only if it preserves the relevant paths and equations. This produces a concrete conformance method:

1. choose the standard fragment and version;
2. define the functor on objects and generators;
3. generate proof obligations for every imported equation;
4. record any local restriction, strengthening, or unsupported construct;
5. test representative data instances.

A spreadsheet mapping of class names performs only step 2 and usually performs it ambiguously.

## 7.7 Temporal schemas and events

Some facts are better represented as events than as changing attributes. EPCIS makes this explicit for traceability. In an ERP ontology, an event carries:

```text
Event
  ─subject────────▶ Entity or collection
  ─eventType──────▶ EventType
  ─occurredAt─────▶ Time
  ─recordedAt─────▶ Time
  ─location───────▶ Location
  ─businessStep───▶ ProcessStep
  ─evidence────────▶ Evidence
```

Current state is then a derived view over events and policies. This avoids overwriting the history needed to explain how an entity reached its current state.

Not every state should be event-sourced. The ontology should distinguish enduring identity, state observations, authoritative transitions, and derived snapshots. Category theory models the paths; dependent types will model transition admissibility; HoTT will model equality and coherence of multiple semantic routes.

## 7.8 Exercises

1. Take one current-state table and redesign it as enduring entities plus events and assignments.
2. State the difference between “recorded late” and “valid retroactively” using bitemporal intervals.
3. Select a five-concept fragment from an industrial standard and map it to a local model. List the preservation obligations.
4. Find a quantity field whose unit is known but whose counted or measured kind is ambiguous.

# Chapter 8. A Lean 4 Categorical Laboratory

## 8.1 The goal of the laboratory

The objective is not to reproduce a full category-theory library. It is to make ontology claims executable enough that the team can inspect assumptions, generate counterexamples, and prove small coherence laws. A minimal repository can be organized as:

```text
ErpOntology/
  Basic/Category.lean
  Basic/Path.lean
  Schema/Signature.lean
  Schema/Equation.lean
  Schema/Instance.lean
  Domain/Identifiers.lean
  Domain/PumpTrain.lean
  Alignment/Claims.lean
  Alignment/Coherence.lean
  Tests/PumpTrain.lean
```

The first milestone is a checked commuting triangle for the running case.

## 8.2 Local records

```lean
namespace PumpTrain

structure PartRevision where
  partNo : String
  revision : String
  deriving Repr, DecidableEq

structure PlantItem where
  itemNo : String
  plant : String
  deriving Repr, DecidableEq

structure MaterialDefinition where
  code : String
  deriving Repr, DecidableEq

structure Serial where
  value : String
  deriving Repr, DecidableEq

end PumpTrain
```

These structures are intentionally nominal. Two records with equal fields are equal in Lean's ordinary structural equality, which may or may not match business identity. In a production formalization, use opaque identifiers plus separately modeled attributes when field equality should not create identity.

## 8.3 Three mappings and a coherence law

```lean
namespace PumpTrain

abbrev ErpToPlm := PlantItem → PartRevision
abbrev PlmToMes := PartRevision → MaterialDefinition
abbrev ErpToMes := PlantItem → MaterialDefinition

def Commutes
    (erpToPlm : ErpToPlm)
    (plmToMes : PlmToMes)
    (erpToMes : ErpToMes) : Prop :=
  ∀ item, erpToMes item = plmToMes (erpToPlm item)

end PumpTrain
```

A concrete mapping table can be represented by functions with an error result when the mapping is partial.

```lean
inductive MappingError
  | notFound
  | ambiguous
  | outsideEffectivity
  | unapproved
  deriving Repr, DecidableEq

abbrev PartialMap (A B : Type) := A → Except MappingError B
```

Now strict function equality is too strong because errors, effectivity, and evidence must align. Define observational coherence on successful results under a scope predicate.

```lean
def CoherentOn
    (scope : A → Prop)
    (direct : A → Except ε C)
    (first : A → Except ε B)
    (second : B → Except ε C) : Prop :=
  ∀ a, scope a →
    direct a = (first a).bind second
```

This is already a useful CI theorem: for every item in the declared scope, the direct ERP-to-MES adapter must agree with the composite ERP-to-PLM-to-MES adapter, including failure behavior.

## 8.4 Evidence-aware mappings

The next step separates a mapped value from the evidence supporting it.

```lean
structure Evidence where
  source : String
  ruleVersion : String
  approvedBy : String
  note : String
  deriving Repr, DecidableEq

structure Supported (A : Type) where
  value : A
  evidence : List Evidence
  deriving Repr, DecidableEq

abbrev EvidentialMap (A B : Type) :=
  A → Except MappingError (Supported B)
```

For coherence, we may require equal values but permit different evidence lists, provided a comparison relation explains their compatibility.

```lean
def SameValue
    (x y : Except ε (Supported A)) : Prop :=
  match x, y with
  | .ok sx, .ok sy => sx.value = sy.value
  | .error ex, .error ey => ex = ey
  | _, _ => False
```

This exposes the limitation of ordinary proposition-valued coherence: `SameValue` says routes agree, but proofs of agreement are themselves proof-irrelevant in Lean's `Prop`. If distinct derivations matter, we must keep them in `Type` as data or move to a higher identity theory.

## 8.5 A schema equation as a validator

Suppose every serial has a direct product definition and a build revision. We can package data and validate the path law.

```lean
structure SerialFacts where
  serial : PumpTrain.Serial
  buildRevision : PumpTrain.PartRevision
  directDefinition : String


def revisionDefinition (r : PumpTrain.PartRevision) : String :=
  r.partNo


def validSerialFacts (f : SerialFacts) : Bool :=
  f.directDefinition == revisionDefinition f.buildRevision
```

A proof-producing version is stronger:

```lean
structure ValidSerialFacts extends SerialFacts where
  definition_coherent :
    directDefinition = revisionDefinition buildRevision
```

A parser can return `Except ValidationError ValidSerialFacts`. Downstream functions no longer repeat the check; the proof travels with the value.

## 8.6 From model to tests

The categorical model should generate at least four classes of tests:

1. **typing tests:** malformed paths and identifier mixes fail to elaborate;
2. **equation tests:** every declared commuting diagram is tested on fixtures or live extracts;
3. **round-trip tests:** schema adapters satisfy stated unit/counit or inverse laws within scope;
4. **conservativity tests:** merging does not collapse protected local distinctions.

Property-based generators can produce finite instances satisfying the local schemas, then search for counterexamples to proposed mappings. This makes the mathematical phase exploratory rather than merely confirmatory.

## 8.7 Part I synthesis

Category theory has given us a disciplined vocabulary:

```text
local ontology       category or presented schema
business concept     object
functional aspect    arrow
derived meaning      path
business invariant   path equation
concrete database    set-valued functor
record migration     natural transformation
schema mapping       functor
restriction          Δ
union-like extension Σ
compatible join      Π
shared semantics     interface category
merge                pushout
route consistency    commuting diagram
```

This is sufficient to discover many design errors. It is not yet sufficient to represent every industrial condition elegantly. Totality, state, evidence, time, and admissibility often depend on values. The next part replaces a flat schema with dependent families of types.

## 8.8 Part I project

Construct a categorical model for one controlled slice, preferably product definition through as-built serialization.

The deliverables are:

- five to twelve object kinds per local context;
- primitive arrows with explicit totality assumptions;
- at least five path equations;
- a shared interface between two contexts;
- one proposed pushout merge;
- a list of resolution losses and nonconservative identifications;
- one Lean validator for a commuting diagram;
- three competency questions expressed as paths or migrations.

# Part II. Dependent Types and Executable Domain Theories

# Chapter 9. From Diagrams to Judgments

## 9.1 Why category theory is not the end

A categorical schema gives every arrow a source and target. Many industrial rules depend on the value at the source.

Examples include:

- a production order may be released only when the referenced routing and bill of material are effective for its plant and date;
- a quantity may be added only to a quantity of the same physical dimension and compatible counted kind;
- a serialized component may be installed only in a position whose class permits its approved equipment class;
- an inspection result is admissible only when its procedure, instrument calibration, unit, and characteristic match;
- an alignment may be used only while approved and within its declared scope.

These are not merely arrows between fixed object kinds. They are families of types indexed by data. Dependent type theory is designed for such situations.

## 9.2 Judgments and propositions as types

A typing judgment

$$
\Gamma \vdash t : A
$$

says that term $t$ has type $A$ under assumptions $\Gamma$. Under the Curry-Howard interpretation, a proposition is represented by a type and a proof by a term inhabiting that type.

Instead of a Boolean function

```lean
isApproved : Alignment → Bool
```

we can define a proposition or evidence type

```lean
Approved : Alignment → Prop
```

and require a proof:

```lean
useAlignment : (a : Alignment) → Approved a → Result
```

The function cannot be called without supplying evidence that the alignment is approved. Lean checks that evidence against the proposition.

There is an operational distinction between putting evidence in `Prop` and in `Type`. Lean's `Prop` is proof-irrelevant: all proofs of the same proposition are treated as interchangeable, and proof content is erased from compiled programs. This supports efficient theorem proving but means `Prop` is the wrong place for evidence whose identity, source, or derivation must remain observable [R1–R3].

Use:

- `Prop` for an admissibility fact when the specific proof is irrelevant;
- `Type` for a certificate, provenance record, derivation, or alternative witness that must be retained.

## 9.3 Dependent functions: Pi types

A dependent function type

$$
\prod_{x:A} B(x)
$$

allows the result type to depend on the input value. Lean writes it as:

```lean
(x : A) → B x
```

or:

```lean
∀ x : A, B x
```

For example:

```lean
BuildRevision : SerialId → Type
```

can assign a type of admissible build-revision witnesses to each serial. A function

```lean
resolveBuildRevision : (s : SerialId) → BuildRevision s
```

must produce an appropriate witness for every serial in its domain.

More realistically, resolution can fail:

```lean
resolveBuildRevision :
  (s : SerialId) → Except ResolutionError (BuildRevision s)
```

The dependency remains: a successful result is tied to the serial that was queried.

## 9.4 Dependent pairs: Sigma types

A dependent pair

$$
\sum_{x:A} B(x)
$$

contains a value $x:A$ together with a value of the type $B(x)$. Lean's subtype and structures often provide ergonomic forms of this idea.

Suppose `ConformsTo s r` is a proposition that serial $s$ conforms to revision $r$:

```lean
structure BuildRevisionWitness (s : SerialId) where
  revision : PartRevisionId
  conforms : ConformsTo s revision
```

A result of type `BuildRevisionWitness s` contains both the revision and proof that it is valid for precisely `s`. The caller cannot detach the proof and reuse it for another serial.

Dependent pairs are the basic shape of proof-carrying query results:

```text
an answer
+
evidence that the answer satisfies the query contract
```

## 9.5 Inductive families

An ordinary inductive type enumerates constructors. An inductive family lets constructors determine indices.

A workflow example:

```lean
inductive WorkState
  | planned | released | executing | completed | closed

structure WorkOrder (state : WorkState) where
  id : String
  product : PlantItemId
  quantity : Nat
```

Transition evidence can be indexed by source and target states:

```lean
inductive CanTransition : WorkState → WorkState → Type
  | release : CanTransition .planned .released
  | start : CanTransition .released .executing
  | complete : CanTransition .executing .completed
  | close : CanTransition .completed .closed
```

There is no constructor for `.planned` to `.completed`. Illegal transitions are uninhabited, not merely disfavored.

## 9.6 Equality and substitution

If $p : x = y$ and $P$ is a family of types, equality permits transport:

$$
\operatorname{transport}^{P}(p) : P(x) \to P(y).
$$

This is the core mechanism by which facts indexed by one value can be moved to an equal value. In ordinary Lean, equality lives in `Prop`, and equality proofs are proof-irrelevant. Transport computes well for reflexivity and definitional equalities but may become cumbersome for complex representation changes.

The HoTT part of the book will reinterpret equality proofs as paths with potentially meaningful higher structure. For now, transport is useful for conventional dependent modeling.

## 9.7 Definitional and propositional equality

Two terms are **definitionally equal** when Lean can reduce them to the same term by computation. No explicit proof is needed. Two terms are **propositionally equal** when a term of `Eq` relates them.

This distinction is architectural. A canonical representation can make common equalities definitional and keep proof terms small. A poor representation can require transports and rewrites throughout the system.

For example, represent a plant-scoped item directly as:

```lean
structure PlantItem where
  plant : PlantId
  item : ItemId
```

rather than storing an opaque identifier and repeatedly proving that it belongs to a plant. Conversely, do not bake volatile facts such as “currently installed” into identity, because every replacement would force type-level rewrites across the application.

## 9.8 Total functions and the world outside Lean

Dependent types do not make an external database truthful. A proof may rely on a snapshot that becomes stale after it is constructed. The system must state the boundary between pure evidence and changing external state.

A sound architecture often uses:

1. an I/O phase that reads data under a transaction or snapshot token;
2. a validation phase that constructs typed evidence tied to that snapshot;
3. a pure decision phase operating on the validated value;
4. a commit phase that checks the token or relevant preconditions again.

The type system prevents internal misuse. Isolation, locking, version checks, and authorization still protect the interaction with the world.

## 9.9 Exercises

1. Decide whether calibration evidence should live in `Prop` or `Type`. State which observations of the evidence your system needs.
2. Define a dependent pair for an approved substitution of a material requirement.
3. Model a four-state deviation workflow as an indexed transition type.
4. Find a fact currently embedded in an identifier that should instead be a time-indexed relation.

# Chapter 10. Indexed Identity and Context

## 10.1 Typed references

The `Ref` type from Chapter 1 prevents accidental interchange of identifiers. We can strengthen it with explicit context parameters.

```lean
inductive Context
  | plmEngineering
  | erpPlant (plant : String)
  | mesSite (site : String)
  | eamTenant (tenant : String)
  | qmsLaboratory (lab : String)
  deriving Repr, DecidableEq

structure Ref (ctx : Context) (kind : Kind) where
  raw : String
  deriving Repr, DecidableEq
```

Now an ERP item in plant `1000` has a different type from an item in plant `2000`:

```lean
abbrev Plant1000Item := Ref (.erpPlant "1000") .plantItem
abbrev Plant2000Item := Ref (.erpPlant "2000") .plantItem
```

A transfer or cross-plant equivalence must be explicit.

## 10.2 Existential packaging at system boundaries

Dynamic APIs sometimes receive a reference before its kind is known. We can package the indices with the value.

```lean
structure SomeRef where
  ctx : Context
  kind : Kind
  ref : Ref ctx kind
```

Pattern matching recovers the indices. This is safer than reducing all references to a string because the dynamic uncertainty is localized. Once the reference has been validated, internal code can work with precise types.

A JSON representation might carry:

```json
{
  "context": { "system": "ERP", "plant": "1000" },
  "kind": "PlantItem",
  "id": "4711"
}
```

The decoder returns `SomeRef`; a kind-specific endpoint then refines it to the expected `Ref ctx kind` or rejects it.

## 10.3 Identity versus attributes

A common modeling mistake makes a record structure itself the identity:

```lean
structure PartRevision where
  partNo : String
  revision : String
  status : Status
  description : String
```

Lean's structural equality then says changing a description changes the value. Depending on usage, that may represent a new snapshot rather than a new revision identity.

A clearer split is:

```lean
structure PartRevisionId where
  partNo : String
  revision : String
  deriving Repr, DecidableEq

structure PartRevisionData where
  id : PartRevisionId
  status : Status
  description : String
  validDuring : Interval
```

The identifier and the temporally qualified record are different types. Equality of records is not automatically business identity of revisions.

## 10.4 Entity kinds as a universe of discourse

We can use the `Kind` index to define which relations are legal. A typed relation signature is an inductive family.

```lean
inductive Relation : Kind → Kind → Type
  | revisionOf : Relation .productRevision .productDefinition
  | conformsTo : Relation .serializedUnit .productRevision
  | lotOf : Relation .materialLot .materialDefinition
  | representsSerial : Relation .assetRecord .serializedUnit
  | installedUnit : Relation .serializedUnit .functionalPosition
  | inspectedBy : Relation .serializedUnit .inspectionResult
```

A generic relation claim can now quantify over contexts while preserving endpoint kinds.

```lean
structure RelationClaim
    {k₁ k₂ : Kind} (rel : Relation k₁ k₂) where
  leftContext : Context
  rightContext : Context
  left : Ref leftContext k₁
  right : Ref rightContext k₂
```

It is impossible to construct `Relation.conformsTo` between a lot and a position. The relation constructor itself carries the typing rule.

## 10.5 Same entity as an indexed relation

`SameEntity` should generally require compatible kinds and identity criteria. One conservative signature is:

```lean
structure SameEntity
    {c₁ c₂ : Context} {k : Kind}
    (x : Ref c₁ k) (y : Ref c₂ k) where
  criterion : String
  authority : String
```

This still permits a same-kind error: two `productRevision` references can denote different revisions. The structure is merely the type of a claim; its constructor should not be public in a production module. Instead, smart constructors validate declared criteria.

Some cross-kind pairs may support a stronger structured equivalence without literal sameness. An asset record and serialized unit have different kinds, but a restricted view of the record may be equivalent to the unit's identity representation. Represent this with a relation specific to the pair, not by weakening `SameEntity` until it means nothing.

## 10.6 Local keys, natural keys, and global identifiers

The theory separates three ideas:

- a **local key** identifies a record inside a context;
- a **domain key** follows a governed business identity criterion;
- a **global canonical identifier** is an operational handle assigned by an integration service.

A global identifier does not prove that its linked local records denote the same domain entity. It is a reference to an identity-resolution decision. The decision and its evidence remain first-class.

A typed model can express this:

```lean
structure CanonicalId (kind : Kind) where
  raw : String
  deriving Repr, DecidableEq

structure CanonicalMembership
    {ctx : Context} {kind : Kind}
    (local : Ref ctx kind) (canonical : CanonicalId kind) where
  resolutionCase : String
  approvedBy : String
  validDuring : Interval
```

The membership is temporal and governed. The canonical identifier itself is not treated as metaphysical truth.

## 10.7 Context morphisms

Sometimes contexts are related systematically: plant 1000 uses a subset of the corporate item model, or a site MES mirrors a corporate manufacturing definition. A context mapping should preserve entity kinds and relations within scope.

At the type level:

```lean
structure ContextMap (c₁ c₂ : Context) where
  mapRef : {k : Kind} → Ref c₁ k → Ref c₂ k
  -- Additional laws relate attributes and relation claims.
```

In practice, `mapRef` is often partial and evidence-producing. The point of the structure is to group the mapping with its laws rather than scatter conversion functions throughout services.

## 10.8 Exercises

1. Define precise kinds for an item master in a system you know. Split any overloaded kind.
2. Design a decoder from a generic JSON reference into `SomeRef` and a refinement into a required kind.
3. State an identity criterion for serialized units. List the authorities and failure modes.
4. Give a cross-kind equivalence-like relation that should not be called `SameEntity`.

# Chapter 11. Evidence-Bearing Relations

## 11.1 A fact is not just a pair

Traditional relation tables store endpoint keys and perhaps timestamps. A formal domain theory asks for the witness that makes the relation admissible.

For a conformance claim:

$$
\mathrm{ConformsTo}(u,r),
$$

possible evidence includes:

- an as-built record;
- a released manufacturing order;
- approved deviations;
- serialized component genealogy;
- inspection results;
- a signature or authority;
- a rule that interprets those records.

The evidence is not necessarily a proof in the mathematical sense. It is structured data from which an admissibility proof can be constructed under declared assumptions.

## 11.2 Evidence in `Type`

```lean
structure Evidence where
  sourceSystem : System
  sourceRecord : String
  ruleVersion : String
  assertedAt : Nat
  approvedBy : Option String
  note : String
  deriving Repr, DecidableEq

inductive Certainty
  | asserted
  | derived
  | reviewed
  | certified
  deriving Repr, DecidableEq

structure Evidenced (P : Prop) where
  proof : P
  evidence : List Evidence
  certainty : Certainty
```

`Evidenced P` lives in `Type` because the evidence list and certainty class are operationally observable. The proof field establishes the proposition; the surrounding record preserves why the system accepted it.

This split is useful when two derivations prove the same `P`. Lean treats their proof fields as irrelevant, but the evidence records remain distinct.

## 11.3 Alignment states

An ontology alignment is a governed lifecycle object.

```lean
inductive AlignmentState
  | proposed
  | reviewed
  | approved
  | rejected
  | superseded
  | revoked
  deriving Repr, DecidableEq

structure AlignmentId where
  raw : String
  deriving Repr, DecidableEq

structure AlignmentRecord where
  id : AlignmentId
  left : SomeRef
  right : SomeRef
  relationName : String
  state : AlignmentState
  validDuring : Interval
  evidence : List Evidence
```

A raw `AlignmentRecord` is not automatically usable. Define a refined type:

```lean
structure ApprovedAlignment where
  record : AlignmentRecord
  approved : record.state = .approved
  hasEvidence : record.evidence ≠ []
```

Only `ApprovedAlignment` is accepted by merge or query functions. The constructor can be private, with a validator responsible for producing the proofs.

## 11.4 Relation-specific evidence

A generic evidence list is useful for storage, but the formal core should define relation-specific witness types.

```lean
structure ConformanceEvidence
    (serial : SerialId) (revision : PartRevisionId) where
  manufacturingOrder : String
  asBuiltRecord : String
  approvedDeviations : List String
  authority : String

structure InstallationEvidence
    (serial : SerialId) (position : PositionId) where
  workOrder : String
  startedAt : Nat
  endedAt : Option Nat
  recordedBy : String
```

A relation then becomes a family of evidence types:

```lean
abbrev ConformsTo (s : SerialId) (r : PartRevisionId) :=
  ConformanceEvidence s r

abbrev InstalledAt (s : SerialId) (p : PositionId) :=
  InstallationEvidence s p
```

An inhabitant is a witness. Unlike a Boolean, it can explain itself.

## 11.5 Derivations as data

Derived claims should record their rule tree.

```lean
inductive Derivation (Claim : Type) : Type
  | asserted : Claim → Evidence → Derivation Claim
  | byRule :
      (rule : String) →
      (premises : List (Derivation Claim)) →
      Claim →
      Derivation Claim
```

This simplified definition assumes premises have the same claim type. A real engine uses an indexed syntax where each rule declares premise and conclusion types. The central point is that derivations live in `Type`, so two routes are distinct values even when they establish propositionally equal conclusions.

A derivation tree supports:

- explanation;
- impact analysis when an evidence source is revoked;
- rule-version migration;
- confidence propagation;
- comparison of direct and composite mappings.

## 11.6 Approval does not turn a claim into timeless truth

Approval is itself scoped. A mapping may be approved for plant 1000, product family PUMP, and dates after a rollout. The witness type should include the scope.

```lean
structure Scope where
  plant : Option String
  productPrefix : Option String
  validDuring : Interval
  deriving Repr, DecidableEq

structure UsableAlignment (a : AlignmentRecord) (scope : Scope) where
  approved : a.state = .approved
  scopeCovered : Covers a.validDuring scope.validDuring
  relationAllowed : RelationAdmissible a.left.kind a.right.kind a.relationName
```

`Covers` and `RelationAdmissible` are propositions supplied by the domain theory. A use site must provide a `UsableAlignment a scope`, not merely check a status string.

## 11.7 Negative evidence and absence

“Not found” is not evidence that a relation does not hold. To prove absence, the system needs a completeness assumption about the searched source and time.

A negative result should therefore distinguish:

```text
no matching record observed
source declared complete and no record exists
record exists but is rejected
relation is logically impossible by type or invariant
```

Dependent result types can encode these cases. This is critical for traceability and compliance queries, where an empty result may mean either “none” or “unknown.”

## 11.8 Exercises

1. Design a relation-specific evidence type for an approved material substitution.
2. Separate an alignment's lifecycle record from the refined type accepted by query execution.
3. Give two distinct derivations of the same mapping and state what operational information differs.
4. Model a negative traceability result that records the completeness assumptions under which it is valid.

# Chapter 12. Temporal Types and Workflow Correctness

## 12.1 Intervals as governed values

A minimal interval type is:

```lean
structure Interval where
  start : Nat
  finish : Option Nat
  valid : match finish with
    | none => True
    | some t => start < t
```

This uses natural numbers as abstract timestamps. A production model should use a time library, declare inclusivity, timezone handling, and clock source.

Define containment and overlap:

```lean
def Interval.contains (i : Interval) (t : Nat) : Prop :=
  i.start ≤ t ∧ match i.finish with
    | none => True
    | some e => t < e


def Interval.disjoint (a b : Interval) : Prop :=
  (match a.finish with | none => False | some e => e ≤ b.start) ∨
  (match b.finish with | none => False | some e => e ≤ a.start)
```

An installation history can require pairwise disjoint intervals for assignments to a position when the plant model permits at most one occupying unit.

## 12.2 State-indexed workflow objects

```lean
inductive WorkState
  | planned | released | executing | completed | closed
  deriving Repr, DecidableEq

structure WorkOrder (state : WorkState) where
  id : String
  item : PlantItemId
  requestedQty : Nat
  deriving Repr

structure ReleaseApproval where
  approver : String
  approvedAt : Nat
  bomEffective : Bool
  routingEffective : Bool
```

A transition consumes a value in one state and produces a value in another.

```lean
def release
    (w : WorkOrder .planned)
    (a : ReleaseApproval)
    (valid : a.bomEffective = true ∧ a.routingEffective = true) :
    WorkOrder .released :=
  { id := w.id, item := w.item, requestedQty := w.requestedQty }
```

There is no `complete : WorkOrder .planned → WorkOrder .completed`. To skip states, the domain must add an explicit exceptional transition and its evidence.

## 12.3 Events and state reconstruction

State-indexed values model admissible transitions in pure code. An event store records that transitions occurred.

```lean
inductive WorkEvent : WorkState → WorkState → Type
  | released : ReleaseApproval → WorkEvent .planned .released
  | started : String → WorkEvent .released .executing
  | completed : Nat → WorkEvent .executing .completed
  | closed : String → WorkEvent .completed .closed
```

An event path can be indexed by its endpoints:

```lean
inductive WorkflowPath : WorkState → WorkState → Type
  | nil : WorkflowPath s s
  | cons : WorkEvent a b → WorkflowPath b c → WorkflowPath a c
```

This is the dependent-type analogue of the workflow category from Part I. Every path is a typed transition history.

## 12.4 Effectivity as a dependent precondition

A production order references revisions, routings, substitutions, and resources that must be effective at a plant and time.

```lean
structure ProductionContext where
  plant : String
  atTime : Nat

class EffectiveAt (A : Type) where
  effective : A → ProductionContext → Prop

structure EffectiveValue (ctx : ProductionContext) (A : Type)
    [EffectiveAt A] where
  value : A
  proof : EffectiveAt.effective value ctx
```

A release function can require `EffectiveValue ctx BomRevision` and `EffectiveValue ctx RoutingRevision`. The proof binds the selected revisions to the same context, blocking accidental combination of independently valid but mutually mismatched revisions.

## 12.5 Snapshot-indexed evidence

External facts should be tied to the snapshot under which they were validated.

```lean
structure Snapshot where
  token : String
  capturedAt : Nat
  deriving Repr, DecidableEq

structure ObservedAt (snap : Snapshot) (A : Type) where
  value : A
  sourceVersion : String
```

A proof of current inventory should not be reusable after an unrelated database update unless the application has a policy for monotonicity. Indexing by `Snapshot` makes stale evidence visible in function signatures.

```lean
reserveInventory :
  (snap : Snapshot) →
  ObservedAt snap InventoryPosition →
  ReservationRequest →
  Except ReservationError (Reservation snap)
```

The commit phase can require the same snapshot token or perform a compare-and-swap against the source version.

## 12.6 Temporal identity and replacement

A functional position persists while its occupants change. Model occupancy as a dependent relation, not as equality:

$$
\mathrm{Occupancy}(p,t) : \mathrm{Option}(\mathrm{SerializedUnit}).
$$

The statement that `S-1044` and `S-2088` both occupied `CP-4` does not identify the serials. It connects each to the same role at different times.

Likewise, a superseding revision is not equal to its predecessor. `Supersedes r₂ r₁` is a directed lifecycle relation. Equivalence may hold for a restricted behavior or interface, but version history must not be erased.

## 12.7 Concurrency and compensation

State machines become more complex when operations are concurrent or reversible. A cancellation after partial material issue is not the inverse of release; it creates compensating events and accounting entries. The ontology should distinguish:

- mathematical inverse;
- business reversal;
- compensating transaction;
- supersession;
- correction of a false record.

These relations have different audit semantics. Modeling all of them as status changes to a previous value destroys the path history that explains the current state.

## 12.8 Exercises

1. Add a `cancelled` state and distinguish cancellation before and after execution starts.
2. Define a non-overlap invariant for installation assignments at one functional position.
3. Model the effectivity of a substitute material relative to plant, date, and customer program.
4. Explain why changing an erroneous installation record is not the same event as physically replacing equipment.

# Chapter 13. Quantities, Bills of Material, and Configurations

## 13.1 Dimension-indexed quantities

A quantity type should make impossible operations unrepresentable. A compact pedagogical model is:

```lean
inductive Dimension
  | mass
  | length
  | duration
  | temperature
  | count (kind : Kind)
  deriving Repr, DecidableEq

structure Quantity (d : Dimension) where
  magnitude : Int
  deriving Repr, DecidableEq
```

Now addition is homogeneous by construction:

```lean
def Quantity.add (x y : Quantity d) : Quantity d :=
  ⟨x.magnitude + y.magnitude⟩
```

The function cannot add a mass to a length, or a count of serialized units to a count of lots. Units require another index or a value whose type guarantees the same dimension.

```lean
structure UnitOf (d : Dimension) where
  symbol : String
  scaleNumerator : Int
  scaleDenominator : Nat
```

A production implementation should represent rational or decimal magnitudes exactly and prove conversion laws. The simple code illustrates the dependency: the unit is selected only from units of the quantity's dimension.

## 13.2 Compound dimensions

Engineering calculations require compound dimensions such as velocity, pressure, energy, and flow. Mathematically, represent a dimension by an exponent vector over base dimensions:

$$
d = (e_L,e_M,e_T,e_I,e_\Theta,e_N,e_J).
$$

Multiplication adds exponent vectors; division subtracts them. A quantity of pressure has dimension

$$
M L^{-1} T^{-2}.
$$

The type of multiplication can compute the result index:

$$
\mathrm{Quantity}(d_1) \to
\mathrm{Quantity}(d_2) \to
\mathrm{Quantity}(d_1+d_2).
$$

This is useful in manufacturing formulas, energy accounting, process limits, and unit-normalized integration. It also distinguishes a dimension error from a conversion error: converting psi to pascals is valid; converting psi to liters per minute is not.

## 13.3 Definitions, occurrences, and required quantities

A bill of material contains occurrences or requirements, not merely child part identifiers.

```lean
structure BomLine (parent : PartRevisionId) where
  lineId : String
  child : PartRevisionId
  quantity : Quantity (.count .serializedUnit)
  positionCode : String
  effectivity : Interval
```

For bulk material, the quantity index would be mass, volume, or another dimension. For nonserialized components, `count .serializedUnit` is wrong; a more complete kind universe distinguishes countable part instances, packages, and continuous materials.

The parent index ties each line to a controlled revision. A `BomLine revC` cannot silently be inserted into a `BomLine revD` collection without an explicit migration or reuse rule.

## 13.4 Acyclicity and rank witnesses

Many BOMs should be acyclic within a declared expansion policy. One proof technique assigns a rank and requires every component edge to decrease it.

```lean
structure RankedRevision where
  revision : PartRevisionId
  rank : Nat

structure RankedBomLine (parent child : RankedRevision) where
  quantity : Nat
  decreases : child.rank < parent.rank
```

A path of component lines must strictly decrease a natural number, so a cycle is impossible. This is stronger than checking a finite extract after the fact: every constructor of a valid line carries the local condition that supports the global theorem.

Actual product structures complicate this rule. Phantom assemblies, reference-only links, alternate structures, configurable loops, and process recirculation may require different graph semantics. The ontology must name the relation whose acyclicity is claimed rather than declaring the entire enterprise graph acyclic.

## 13.5 Approved substitutions

A substitution is not a symmetric identity. It is a contextual capability to satisfy a requirement.

```lean
structure SubstitutionContext where
  plant : String
  atTime : Nat
  customerProgram : Option String
  quantity : Nat

structure SatisfiesRequirement
    (required candidate : PartRevisionId)
    (ctx : SubstitutionContext) where
  approval : String
  validDuring : Interval
  quantityLimit : Option Nat
  characteristicEvidence : List Evidence
```

The type is directional. A candidate may satisfy a requirement while the reverse does not hold. Transitivity also need not hold: if B substitutes for A and C substitutes for B, C is not automatically approved for A.

This is a recurring lesson for ontology merging. Relations that look like equivalence in casual language may fail symmetry or transitivity once scope and governance are included.

## 13.6 Four configuration views

Industrial digital threads often need at least four configurations:

| View | Meaning |
|---|---|
| as-designed | approved engineering structure |
| as-planned | manufacturing or maintenance plan selected for context |
| as-built | actual components, lots, serials, and deviations used |
| as-maintained | components currently or historically installed after service |

Model the view as an index:

```lean
inductive ConfigView
  | asDesigned | asPlanned | asBuilt | asMaintained
  deriving Repr, DecidableEq

structure Configuration (view : ConfigView) where
  root : String
  capturedAt : Nat
  members : List SomeRef
  evidence : List Evidence
```

The simplified member list hides rich typed edges, but the index still prevents accidental use of an as-designed configuration where an as-built one is required.

A conformance function relates views:

```lean
Conforms :
  Configuration .asBuilt →
  Configuration .asDesigned →
  Prop
```

It should not assert equality. Deviations and approved substitutions can make an as-built configuration conform without being structurally identical to the design.

## 13.7 Configuration transformations

The digital thread can be organized as evidence-bearing transformations:

$$
\mathrm{AsDesigned}
\xrightarrow{\mathrm{planning}}
\mathrm{AsPlanned}
\xrightarrow{\mathrm{execution}}
\mathrm{AsBuilt}
\xrightarrow{\mathrm{maintenance}}
\mathrm{AsMaintained}.
$$

Each arrow has its own laws.

Planning should preserve required product intent while selecting plant-specific resources and substitutions. Execution should account for every actual consumption and production against requirements or approved exceptions. Maintenance should record removals and installations without rewriting as-built history.

The composite path answers the question “how did the currently installed configuration arise from the approved design?” A direct mapping from design to current configuration should agree with this composite under an explicit coherence rule. Part III will treat that comparison as a higher path.

## 13.8 Conservation laws

ERP and MES systems contain conservation principles:

$$
\mathrm{inventoryBefore}
+
\mathrm{receipts}
-
\mathrm{issues}
=
\mathrm{inventoryAfter},
$$

$$
\mathrm{inputMass}
=
\mathrm{outputMass}
+
\mathrm{scrapMass}
+
\mathrm{measuredLoss}
$$

within declared tolerances and boundaries.

Dependent quantities ensure dimensional validity. Proof obligations state the conservation law. Evidence records connect mathematical terms to transactions, measurements, and time windows.

Not every manufacturing process conserves the tracked quantity exactly. Chemical reactions, evaporation, yield uncertainty, rework, and measurement error require a domain-specific balance model. The ontology should expose the boundary and tolerance rather than install a universal conservation axiom.

## 13.9 Exercises

1. Refine `Dimension` to distinguish count of packages from count of pieces.
2. State an acyclicity policy for an engineering BOM that permits reference links but forbids component cycles.
3. Model a substitution that is valid only up to a quantity and only for one customer program.
4. State a conformance relation between as-built and as-designed configurations that admits approved deviations.

# Chapter 14. Traceability as a Constructed Proof

## 14.1 Traceability is a path problem

A traceability answer is not just a list of joined rows. It is a path through a typed evidence graph.

For the question

```text
Which lots contributed to serial S-1044?
```

one possible derivation is:

```text
S-1044
  was produced by WorkExecution WE-51
  which fulfilled JobOrder JO-40
  during which MaterialActual MA-18 was consumed
  and MA-18 referenced Lot L-882.
```

Each step has a type and evidence. The result should preserve the composite derivation.

## 14.2 An indexed trace syntax

For a compact Lean model, use a closed sum of domain references.

```lean
inductive EntityRef
  | serial (id : String)
  | workExecution (id : String)
  | jobOrder (id : String)
  | materialActual (id : String)
  | materialLot (id : String)
  | partRevision (id : String)
  | plantItem (id : String)
  deriving Repr, DecidableEq
```

Primitive trace steps are indexed by endpoints.

```lean
inductive TraceStep : EntityRef → EntityRef → Type
  | producedBy (evidence : Evidence) :
      TraceStep (.serial s) (.workExecution w)
  | fulfills (evidence : Evidence) :
      TraceStep (.workExecution w) (.jobOrder j)
  | consumedActual (evidence : Evidence) :
      TraceStep (.jobOrder j) (.materialActual a)
  | actualLot (evidence : Evidence) :
      TraceStep (.materialActual a) (.materialLot l)
  | builtTo (evidence : Evidence) :
      TraceStep (.serial s) (.partRevision r)
```

The variables `s`, `w`, `j`, and so on are implicit constructor parameters inferred from the endpoints.

The reflexive transitive closure composes steps.

```lean
inductive Trace : EntityRef → EntityRef → Type
  | refl : Trace x x
  | cons : TraceStep x y → Trace y z → Trace x z
```

A value of `Trace x y` is an explanation of reachability from $x$ to $y$.

## 14.3 Proof-carrying query results

A trace query can return:

```lean
structure TraceResult (source : EntityRef) where
  target : EntityRef
  derivation : Trace source target
```

A specialized query makes the target kind precise:

```lean
structure LotTraceResult (serial : String) where
  lot : String
  derivation :
    Trace (.serial serial) (.materialLot lot)
```

The consumer receives not only `L-882` but the path that justifies it. An explanation API can render the constructors and evidence records.

## 14.4 Soundness of trace execution

Suppose the production query engine traverses a graph database. We want a theorem:

> Every returned target has a derivation in the formal trace relation.

The implementation strategy is proof-producing traversal. Each graph edge decoder returns a typed `TraceStep` only after validating kind, relation, scope, and evidence. Path search concatenates these values. The result is sound by construction.

Completeness is separate:

> Every valid derivation represented in the authoritative sources is discoverable by the query.

Completeness requires assumptions about ingestion, source coverage, event ordering, and search bounds. It should never be implied by an empty result without stating those assumptions.

## 14.5 Route comparison

There may be several paths from a serial to a part revision:

```text
serial → work execution → job order → ERP item → PLM revision
serial → as-built record → PLM revision
```

In ordinary dependent type theory, these are distinct values of `Trace source target`. We can define an equivalence relation or a proposition saying they agree in conclusion and scope. But a quotient may erase the very derivational distinctions needed for audit.

This is the point at which traceability naturally becomes a higher-dimensional problem:

- objects are records or domain entities;
- paths are derivations or alignments;
- paths between paths are coherence proofs explaining why two derivations agree.

Part III will make that structure foundational rather than simulated.

## 14.6 Revocation and dependency analysis

Because evidence appears inside trace steps, we can calculate which results depend on a revoked source. Define a function that extracts evidence identifiers from a trace:

```lean
EvidenceIds : Trace x y → List String
```

When mapping rule `MR-17` is superseded, the system searches stored derivations for `MR-17`, invalidates or rechecks affected canonical memberships, and regenerates materialized views.

This is superior to recomputing the entire integration without explanation. The derivation graph is a dependency graph for semantic decisions.

## 14.7 Minimal and preferred explanations

Several valid traces may exist. A query policy can choose:

- shortest path;
- highest authority;
- newest approved evidence;
- path restricted to regulated sources;
- path avoiding deprecated mappings;
- all non-equivalent paths.

The selection criterion must not be confused with truth. It is a policy over derivations. The formal result can return the chosen path plus a proof that it satisfies the policy, while retaining alternatives for diagnostics.

## 14.8 Privacy and authorization

An explanation may contain sensitive supplier, personnel, or quality data. Authorization should apply both to the conclusion and to the derivation.

A user may be permitted to know that a serial conforms but not see the supplier certificate. One response is to return a truncated or redacted proof object whose verification token confirms the conclusion without exposing all evidence. Cryptographic proof systems are beyond this book, but the ontology must at least separate:

- permission to use a fact in a decision;
- permission to inspect its evidence;
- permission to disclose it externally.

## 14.9 Exercises

1. Add maintenance replacement steps to `TraceStep` and derive a path from a current position to an original build serial.
2. State soundness and completeness assumptions for a lot genealogy query.
3. Design two route-selection policies and identify a case in which they choose different valid traces.
4. Model a redacted explanation that exposes a conclusion while hiding selected evidence fields.

# Chapter 15. Reconciliation, Migrations, and API Extraction

## 15.1 Schema evolution as a typed transformation

Let `CustomerV1` and `CustomerV2` be two representations. A total lossless migration can be packaged as an equivalence:

```lean
structure SchemaEquiv (A B : Type) where
  forward : A → B
  backward : B → A
  forward_backward : ∀ b, forward (backward b) = b
  backward_forward : ∀ a, backward (forward a) = a
```

Lean already provides `Equiv`, written `A ≃ B`, for this pattern. Most ERP migrations are not equivalences. Splitting `fullName` into `givenName` and `familyName` may require a heuristic and can lose information. The type should say so.

```lean
structure PartialMigration (A B : Type) where
  forward : A → Except MigrationError B
  preservedId : ∀ a b, forward a = .ok b → sourceId a = targetId b
```

Additional fields record loss, defaults, warnings, and provenance.

## 15.2 Reconciliation as comparison of observations

Two systems may observe the same domain entity through different representations. A reconciliation job should not compare rows wholesale. It should compare declared observations.

Let:

$$
O_P : P \to V,
\qquad
O_E : E \to V
$$

map PLM and ERP records into a comparison view $V$. A reconciliation case contains local records, their mapped observations, a comparison result, and evidence.

The comparison view might include:

```text
product family
revision applicability
plant
base unit dimension
lifecycle status
valid-time interval
```

Fields outside the view remain local. This prevents an ERP purchasing description from being treated as a conflict with an engineering description when the ontology never claimed they were the same attribute.

## 15.3 From theorem to enforcement

Formal statements should be compiled into ordinary mechanisms.

| Formal construct | Conventional artifact |
|---|---|
| indexed identifier | branded or newtype ID |
| finite enum | database enum or check constraint |
| total relation | non-null foreign key |
| uniqueness proposition | unique constraint |
| interval non-overlap | exclusion constraint or validator |
| path equation | reconciliation query or trigger |
| state transition | domain-service command handler |
| quantity dimension | typed library plus unit validation |
| proof-carrying result | response plus explanation token |
| round-trip law | property-based test |
| mapping coherence | CI integration test |

The theorem prover does not need to run in every request. It can produce a verified core, generators, fixtures, and contracts consumed by conventional services.

## 15.4 A conventional API derived from the theory

The competency questions generate domain APIs:

```text
GET /serials/{serial}/as-built?at=...
GET /serials/{serial}/consumed-lots
GET /positions/{position}/occupancy?at=...
GET /alignments/explain?left=...&right=...
POST /work-orders/{id}/release
POST /substitutions/evaluate
```

The release endpoint does not accept a free-form status update. It accepts a command containing the evidence needed to construct the transition.

A response can separate conclusion from explanation:

```json
{
  "serial": "S-1044",
  "buildRevision": "PUMP-2000/C",
  "validAt": "2025-08-09T10:00:00Z",
  "explanationId": "EXP-9021",
  "assumptions": ["MES genealogy complete through snapshot 8f2a"]
}
```

`GET /explanations/EXP-9021` returns the authorized derivation graph.

## 15.5 TypeScript extraction

A generated client can preserve the identity strata.

```typescript
type Brand<T, B extends string> = T & { readonly __brand: B };

type PartRevisionId = Brand<string, "PartRevisionId">;
type PlantItemId = Brand<string, "PlantItemId">;
type SerialId = Brand<string, "SerialId">;
type MaterialLotId = Brand<string, "MaterialLotId">;
type FunctionalPositionId = Brand<string, "FunctionalPositionId">;

type Interval = {
  start: string;
  endExclusive?: string;
};

type AlignmentState =
  | "PROPOSED"
  | "REVIEWED"
  | "APPROVED"
  | "REJECTED"
  | "SUPERSEDED"
  | "REVOKED";
```

Generated types are weaker than the Lean theory. A branded string does not prove provenance or effectivity. It still prevents widespread accidental mixing and makes the remaining runtime obligations explicit.

## 15.6 SQL extraction

An alignment ledger might use:

```sql
create table alignment_claim (
  alignment_id       uuid primary key,
  left_context       text not null,
  left_kind          text not null,
  left_id            text not null,
  right_context      text not null,
  right_kind         text not null,
  right_id           text not null,
  relation_kind      text not null,
  valid_from         timestamptz not null,
  valid_to           timestamptz,
  state              text not null,
  rule_version       text not null,
  approved_by        text,
  recorded_at        timestamptz not null,
  check (valid_to is null or valid_from < valid_to)
);
```

This table stores claims, not canonical truth. A materialized canonical-membership view selects only alignments whose kind pair, relation, state, scope, and evidence satisfy the formal policy.

The database can enforce local constraints. Cross-system path coherence is typically checked by a reconciliation service because it spans sources and requires derivation data.

## 15.7 Generated property tests

For every declared equivalence or migration, generate laws:

```text
backward(forward(x)) = x
forward(backward(y)) = y
serialize(parse(x)) = x
parse(serialize(y)) = y
unit conversion round trips within tolerance
mapping direct route = mapping composite route
```

Scope conditions become generator constraints. A test failure should report the formal law, the generated witness, and the involved alignment versions.

Proofs remain preferable for the pure core. Property tests extend assurance across generated code, databases, serializers, and third-party platforms that are not inside Lean's kernel.

## 15.8 The verified core and the conventional shell

A realistic architecture has layers:

```text
formal ontology and proofs
        ↓
verified pure domain core
        ↓
generated contracts, validators, and tests
        ↓
conventional services and databases
        ↓
external ERP/PLM/MES/EAM systems
```

The most valuable verified functions are those with stable mathematical specifications:

- quantity and currency calculations;
- state-transition admissibility;
- configuration conformance;
- schema migration laws;
- alignment coherence;
- trace derivation checking;
- authorization decision logic.

HTTP retries, vendor connectors, observability, and user interfaces remain in the conventional shell.

## 15.9 Exercises

1. Classify a real migration as equivalence, injection, surjection, partial migration, or approximation.
2. Define the comparison view for reconciling PLM revisions with ERP plant items.
3. Translate one path equation into a SQL or batch reconciliation check.
4. Design an API command whose request contains enough evidence to construct a state transition.

# Chapter 16. The Limits of Ordinary Identity

## 16.1 What Lean 4 gives us

Lean 4 provides dependent functions, inductive families, equality, quotients, proof automation, metaprogramming, and a small trusted kernel. These are sufficient for the entire categorical and dependent-type development in Parts I and II. Lean's tactics construct proof terms that the kernel checks [R1–R3].

For conventional verified ERP cores, this may be enough. The limitation appears when distinct identifications and their relationships are themselves part of the domain.

## 16.2 Equality in `Prop`

Lean's standard equality has type:

```lean
Eq a b : Prop
```

and `Prop` is proof-irrelevant. If:

```lean
p q : a = b
```

then the distinction between `p` and `q` is not available as computationally meaningful higher structure. We can store two derivation records in `Type`, but their equality proofs remain external bookkeeping rather than the identity structure of the objects themselves.

For many theorem-proving tasks this is a feature. For ontology merging, it means the standard identity type cannot directly express:

- two approved ways of identifying local concepts;
- a proof that the two ways agree;
- a higher comparison between coherence proofs;
- nontrivial loops representing semantic automorphisms.

## 16.3 Equivalence is not equality

Suppose two schemas or record types are mutually invertible:

```lean
schemaEquiv : SchemaA ≃ SchemaB
```

In ordinary intensional type theory, this does not make `SchemaA` and `SchemaB` equal. Every dependent construction must be transported by an explicit theorem or adapter.

For example:

```lean
ValidationRules SchemaA
ValidationRules SchemaB
```

are different types. We can write a function mapping one to the other, but every construction needs its own invariance plumbing.

Univalence will say that an equivalence can be used as an identity of types. Then all dependent constructions respect the equivalence by ordinary substitution.

## 16.4 Setoids and quotients

A setoid packages a carrier with an equivalence relation. A quotient identifies related elements. This is useful for canonicalizing representations, case-insensitive codes, normalized units, or records modulo irrelevant fields.

The danger is information erasure. If we quotient local references by approved alignments, we obtain flat canonical entities, but lose:

- which alignment produced the identification;
- whether several alignments exist;
- how composite routes compare;
- which evidence supports a route;
- how revocation affects the quotient decision.

A separate audit table can retain that information, but the mathematical identity type no longer reflects it. HoTT offers a structure in which the quotient-like identifications and their paths coexist.

## 16.5 Strict commuting versus coherent commuting

Part I wrote a coherence law as strict equality:

$$
F_{EM} = F_{PM}\circ F_{EP}.
$$

In an industrial integration, the two routes may not be definitionally or structurally equal. They may be connected by a specified transformation, adapter, unit conversion, version correspondence, or proof of observational agreement.

The appropriate diagram commutes **up to a chosen identification**. With four or more routes, those chosen identifications must themselves satisfy coherence laws. Strict equality either rejects useful equivalences or forces premature canonicalization.

Higher category theory and HoTT are designed to speak about commuting up to higher cells or paths.

## 16.6 Identity proofs as explanations

In Part II, an explanation was a separate `Trace` value. The conclusion `x = y` remained proof-irrelevant. A HoTT-oriented theory can take the explanation path itself as the identity witness:

$$
p : x = y.
$$

A second route is another path:

$$
q : x = y.
$$

A coherence proof is:

$$
\alpha : p = q.
$$

This hierarchy continues. The ontology no longer stores “same entity” as a Boolean edge plus an unrelated derivation graph. Identity is generated by the approved paths, and coherence is generated by higher paths.

## 16.7 The bridge to Part III

The next part will use four HoTT mechanisms:

1. **path types** to represent identifications with potentially distinct witnesses;
2. **equivalences and univalence** to make structurally equivalent representations substitutable;
3. **higher inductive types** to generate merged ontologies from local points and alignment paths;
4. **truncation** to extract set-like operational identities deliberately.

Lean 4 remains useful as the implementation language for the surrounding tools and for an object-language kernel. Its standard kernel is not a native computational HoTT kernel because of its proof-irrelevant `Prop` equality. A genuinely computational implementation points toward cubical type theory, as implemented in systems such as Cubical Agda [R6, R10].

## 16.8 Part II project

Extend the Part I model with:

- context- and kind-indexed identifiers;
- one evidence-bearing alignment lifecycle;
- one state-indexed workflow;
- one dimension-indexed quantity calculation;
- one proof-carrying trace query;
- one schema migration with a round-trip or preservation theorem;
- generated TypeScript or SQL artifacts;
- a written account of which derivational distinctions ordinary `Eq` fails to retain.

# Part III. Homotopy Type Theory as the Organizing Structure

# Chapter 17. Identity as a Space of Paths

## 17.1 The change of foundation

Ordinary type theory asks whether two terms are equal and lets equality support substitution. Homotopy type theory asks us to take the identity type itself seriously.

For $x,y:A$, the type

$$
x =_A y
$$

is interpreted as a space of paths from $x$ to $y$. A proof

$$
p : x = y
$$

is a path. Two paths may themselves be connected by a path:

$$
\alpha : p = q.
$$

Paths between those paths continue at higher dimensions. Types behave like spaces or $\infty$-groupoids: terms are points, equalities are paths, equalities between equalities are homotopies, and so on [R6].

For ERP ontologies, this does not mean that every process step is reversible. Identity paths are invertible. A purchase order release, material consumption, or physical replacement is directed and should remain a directed morphism, event, or state transition. HoTT organizes **identity and equivalence**, not every business relation.

### Principle: directed relations are not paths

Use HoTT paths for claims of sameness, equivalence, representation change, and coherence. Use ordinary functions, relations, categories, or directed type theories for causation, workflow, supersession, consumption, and time.

This separation prevents a seductive error: interpreting “there is a path from planned to released” as if the two states were equal.

## 17.2 Path operations

Every point has a reflexivity path:

$$
\operatorname{refl}_x : x=x.
$$

Every path has an inverse:

$$
p^{-1} : y=x.
$$

Paths compose:

$$
p\cdot q : x=z
$$

when $p:x=y$ and $q:y=z$.

The groupoid laws hold, but in intensional type theory many of them hold propositionally rather than by definitional equality:

$$
(p\cdot q)\cdot r = p\cdot(q\cdot r),
$$

$$
\operatorname{refl}_x\cdot p=p,
\qquad
p\cdot p^{-1}=\operatorname{refl}_x.
$$

The proofs of these laws are higher paths. Their own coherence matters in sufficiently high-dimensional constructions.

In an ontology merge, path composition is the composition of identity justifications. If:

$$
p : e_{4711}=r_C
$$

identifies an ERP representation with a PLM revision under an approved alignment, and

$$
q : r_C=m_{82}
$$

identifies that revision with an MES definition, then:

$$
p\cdot q : e_{4711}=m_{82}
$$

is the composite integration route.

## 17.3 Path induction

The eliminator for identity is path induction, often called $J$. To prove a property about every path, it is enough to prove it for reflexivity in a suitable dependent family.

Operationally, path induction supplies the principle that every construction respects equality. Given a family $P:A\to\mathcal{U}$ and $p:x=y$, transport moves inhabitants:

$$
\operatorname{transport}^{P}(p) : P(x) \to P(y).
$$

Given a function $f:A\to B$, applying it to a path yields:

$$
\operatorname{ap}_f(p) : f(x)=f(y).
$$

For an ontology, if a canonical policy family

$$
\mathrm{ValidationRules} : \mathrm{Entity} \to \mathcal{U}
$$

is indexed by entities, an alignment path transports rules from one representation to another. The transport is not a hand-written adapter for each dependent construction; it follows from identity.

This is one concrete reason HoTT matters. It turns identity resolution into a universal substitution mechanism.

## 17.4 Identity versus evidence

A path can be generated from an alignment witness, but it should not be confused with a database row containing that witness. Suppose:

$$
\mathrm{Alignment}(x,y)
$$

is a type whose inhabitants contain authority, validity, rule version, and evidence. A higher inductive merge can include a constructor:

$$
\operatorname{glue} : \mathrm{Alignment}(x,y) \to (x=y).
$$

Different alignment witnesses generate potentially different paths. The path records their effect on identity. The witness remains available as the constructor parameter or in an associated evidence family.

This is stronger than a quotient relation $R(x,y)\to [x]=[y]$ followed immediately by proof irrelevance. The generated path space can retain distinctions and loops.

## 17.5 The type-as-groupoid view

At the one-dimensional approximation, a type behaves like a groupoid:

- points are objects;
- paths are invertible morphisms;
- path composition is morphism composition;
- higher paths identify morphisms.

This suggests an **identity groupoid** for industrial entities. Local references are points. Approved identity-forming alignments are generating arrows. Composite mappings are paths. Coherence proofs are 2-cells.

The phrase “identity groupoid” must be kept separate from the directed domain category of Chapter 2. An ERP ontology has both:

1. a directed categorical structure of aspects, events, and dependencies;
2. a higher groupoidal structure of identity, equivalence, and coherent representation.

A mature theory combines them, for example as dependent families or displayed structures over an identity type.

## 17.6 Homotopy levels

HoTT classifies types by the complexity of their identity types.

- A **contractible type** has exactly one point up to equality.
- A **mere proposition** has at most one point up to equality; any two proofs are equal.
- A **set** has proposition-valued identity types; between two points there is at most one path up to equality.
- A **1-type** has set-valued identity types; multiple paths may exist, but higher paths between paths are proposition-like.
- Higher $n$-types retain higher identity structure.

Using the common indexing convention, these are $(-2)$-, $(-1)$-, $0$-, and $1$-types.

This hierarchy is directly useful for architecture:

| Information | Useful level |
|---|---|
| “an approved mapping exists” | propositional truncation |
| canonical entity identifiers | set level |
| distinct alignment paths and their comparisons | 1-type or higher |
| unrestricted design theory | potentially higher type |

A central design decision is therefore not simply “identify or do not identify.” It is “at what truncation level should this layer observe identity?”

## 17.7 Loops and ambiguity

Two paths $p,q:x=y$ generate a loop at $x$:

$$
p\cdot q^{-1} : x=x.
$$

In an ontology, such a loop can mean several things:

- two equivalent proofs of the same correspondence;
- a nontrivial representation automorphism;
- a unit or code conversion round trip;
- an unresolved route ambiguity;
- a genuine defect in coherence.

The theory should not declare every loop erroneous. It should ask how dependent information transports around the loop. If every relevant family returns unchanged, the loop may be harmless. If transport changes a validation rule or attribute, integration is route-dependent.

Chapter 20 will call this phenomenon **semantic holonomy**.

## 17.8 Lean 4 and native HoTT

Lean 4's standard kernel is excellent for formalizing ordinary dependent type theory, categories, evidence records, and an object-language implementation. It is not a native HoTT kernel: its ordinary equality is proof-irrelevant because it lives in `Prop`. Earlier Lean work supported a HoTT library through a different kernel configuration and primitive higher inductive constructions, but that work belongs to earlier Lean generations rather than the standard Lean 4 foundation [R7].

There are three responsible ways to use Lean 4 in this book's project:

1. formalize the categorical and dependent layers directly in Lean 4;
2. axiomatize a restricted HoTT interface, understanding the loss of computation;
3. implement a separate cubical/HoTT object language and checker in Lean 4.

For computational univalence and higher inductive types, cubical type theory provides a more direct foundation [R10, R11].

## 17.9 Exercises

1. Classify five industrial relations as identity paths or directed relations. Defend every choice.
2. Give two distinct alignment paths between the same endpoints and form the resulting loop.
3. Define a dependent family whose transport around that loop should be trivial.
4. Choose the required homotopy level for proposed mappings, approved alignments, canonical IDs, and audit explanations.

# Chapter 18. Univalence and Representation Independence

## 18.1 From equality to equivalence

Every equality of types induces an equivalence:

$$
\operatorname{idtoequiv} : (A=B) \to (A\simeq B).
$$

The univalence principle states that this map is itself an equivalence. Informally:

$$
(A=B) \simeq (A\simeq B).
$$

Thus an equivalence of types can be used as a path in the universe:

$$
\operatorname{ua}(e) : A=B
$$

for $e:A\simeq B$.

Univalence formalizes the mathematical practice of treating equivalent structures as interchangeable while preserving the fact that the interchangeability is supplied by a particular equivalence [R6, R10].

## 18.2 What counts as an ERP equivalence

Two schemas are not equivalent because their tables have similar names or the same number of rows. An equivalence must include transformations in both directions and laws showing that the round trips are homotopic to identity.

For record types $A$ and $B$:

$$
e = (f,g,\eta,\epsilon)
$$

with:

$$
f:A\to B,
\qquad
g:B\to A,
$$

$$
\eta : g\circ f \sim \operatorname{id}_A,
\qquad
\epsilon : f\circ g \sim \operatorname{id}_B.
$$

The symbol $\sim$ denotes pointwise homotopy. The laws can be scoped to a subtype when only valid records are equivalent.

A PLM revision representation and an ERP planning representation may be equivalent only after restricting to:

- a plant;
- an effectivity interval;
- a product family;
- a normalization of units and codes;
- approved, nonconfigurable items;
- a selected observable interface.

The restricted subtype is the object of equivalence. The unrestricted tables are not.

## 18.3 An example: list and graph routings

Plant A stores a routing as an ordered list of operations. Plant B stores a directed graph. They are equivalent on the subtype of graphs that are finite, connected, acyclic, and have a unique linear successor order.

Let:

$$
\mathrm{LinearGraph}
=
\sum_{g:\mathrm{RoutingGraph}}
\mathrm{IsLinear}(g).
$$

Then one may construct:

$$
\mathrm{RoutingList} \simeq \mathrm{LinearGraph}.
$$

Univalence turns this equivalence into a path of types. A construction indexed by the representation, such as:

$$
\mathrm{ExecutionValidator} : \mathcal{U}\to\mathcal{U},
$$

can be transported along the path.

The scope proof `IsLinear` is not incidental. It is what prevents a branching process graph from being silently flattened into a list.

## 18.4 Structure Identity Principle

The Structure Identity Principle is the broad consequence of univalence that isomorphic structured objects can be identified when their structure is formulated appropriately. For ERP ontologies, this applies to structures such as:

- unit systems;
- code systems with bijective code translation;
- finite classifications;
- schema fragments;
- typed API contracts;
- product structures under an occurrence-preserving isomorphism.

It does not say that every relation called “equivalent” by a business user is equality. The relevant notion must be a genuine structure-preserving equivalence.

For example, two equipment class hierarchies may have a bijection on nodes but differ in capability inheritance. They are not equivalent as classified capability structures until the arrows and laws are preserved.

## 18.5 Transporting dependent constructions

Suppose:

$$
e : A\simeq B
$$

and:

$$
P : \mathcal{U}\to\mathcal{U}.
$$

Univalence gives:

$$
\operatorname{transport}^{P}(\operatorname{ua}(e)) : P(A)\to P(B).
$$

Set $P(X)$ to:

- validators for $X$;
- query plans over $X$;
- authorization policies indexed by $X$;
- provenance schemas for $X$;
- configuration predicates on $X$;
- API clients for $X$.

Every such construction respects the equivalence because it respects identity.

This reduces repetitive “mapping preserves feature $F$” lemmas. The cost is that the equivalence and the universe-level transport must have usable computational behavior.

## 18.6 Axiomatic versus computational univalence

If univalence is merely postulated as an axiom, transport along `ua e` may not reduce to the expected conversion function. The theorem is logically powerful but evaluation can get stuck on opaque transports.

Cubical type theory supplies computational rules for paths, transport, composition, and univalence. Cubical Agda exposes interval and path types, systems, transport, composition, Glue types, and higher inductive types so univalent programs can compute [R10, R11].

For an ontology engine, computational behavior matters when transported validators or serializers must execute. Axiomatic univalence is sufficient for high-level proofs; a cubical implementation is preferable for generated executable adapters.

## 18.7 Univalence and API versioning

Consider API versions $V_1$ and $V_2$. If they are equivalent on the supported contract:

$$
e : \mathrm{ValidPayload}_{V_1}\simeq\mathrm{ValidPayload}_{V_2},
$$

then clients expressed generically over the contract can be transported. This gives a precise definition of a nonbreaking version change: not textual compatibility, but equivalence of the valid observable structures together with preservation of specified behavior.

A deprecation can be modeled as a sequence of equivalences and embeddings:

```text
V1 valid subset ≃ V2 legacy view ↪ V2 full model
```

Lossy changes are not equivalences. They require an explicit migration with a residual or error type.

## 18.8 Univalence does not solve matching

Univalence consumes an equivalence; it does not discover one. Ontology matching remains a domain and governance task. Statistical or language-model systems can propose candidate correspondences, but a candidate becomes an equivalence only after the required functions, inverse laws, scopes, and coherence obligations are supplied.

This is a useful safety boundary:

```text
heuristic matching
    produces candidates
formal elaboration
    produces obligations
review and proof
    produce approved equivalences
univalence
    grants substitution
```

The most powerful operation is last, after evidence and laws.

## 18.9 Substitution is stronger than conversion

An explicit adapter converts values. Univalence additionally lets every dependent context treat the representations as the same type. This is valuable when the representation appears inside other types:

$$
\mathrm{Configuration}(A),
\quad
\mathrm{Permission}(A),
\quad
\mathrm{MigrationHistory}(A),
\quad
\mathrm{Query}(A).
$$

Without univalence, each of these needs a custom lifting of the adapter. With univalence, transport is generic.

This is the concrete promise for ERP ontology design: prove one scoped equivalence and obtain representation independence across all correctly typed dependent constructions.

## 18.10 Exercises

1. State the forward, backward, and round-trip laws for two representations of a routing.
2. Give an example of a mapping that is injective but not an equivalence. Explain what univalence must not do with it.
3. Select a dependent construction that should be transported across an API equivalence.
4. Identify the exact subtype on which two local industrial representations are genuinely equivalent.

# Chapter 19. Higher Inductive Merges and Homotopy Pushouts

## 19.1 Constructors for points and identifications

An ordinary inductive type is generated by point constructors. A higher inductive type may also have path constructors and higher-path constructors.

The homotopy pushout of a span

$$
P \xleftarrow{f} K \xrightarrow{g} E
$$

can be presented by the higher inductive type:

```text
data Pushout (f : K → P) (g : K → E) : Type where
  inP  : P → Pushout f g
  inE  : E → Pushout f g
  glue : (k : K) → inP (f k) = inE (g k)
```

The point constructors retain every local point. The path constructor adds one identification for every witness $k:K$.

This is the core merge structure of the book.

## 19.2 The interface as a type of alignment witnesses

In a simple categorical pushout, $K$ is a shared sub-schema. In a HoTT merge, $K$ can be a type of structured alignment witnesses.

For PLM and ERP entity spaces:

$$
P = \mathrm{PlmEntity},
\qquad
E = \mathrm{ErpEntity},
$$

let:

$$
K = \sum_{p:P}\sum_{e:E}\mathrm{ApprovedAlignment}(p,e).
$$

The projections are:

$$
f(p,e,a)=p,
\qquad
g(p,e,a)=e.
$$

Every approved alignment $a$ generates a path:

$$
\operatorname{glue}(p,e,a) : \operatorname{inP}(p)=\operatorname{inE}(e).
$$

Because $a$ is part of $k$, two distinct approved alignments between the same endpoints generate two potentially distinct paths.

## 19.3 Why the homotopy pushout is not a set quotient

A set quotient forces related points to be equal and then makes equality proof-irrelevant. A homotopy pushout freely generates paths while retaining higher structure.

Suppose $a_1,a_2 : \mathrm{ApprovedAlignment}(p,e)$. Then:

$$
\operatorname{glue}(a_1),
\operatorname{glue}(a_2)
:
\operatorname{inP}(p)=\operatorname{inE}(e).
$$

Their difference produces a loop:

$$
\operatorname{glue}(a_1)\cdot
\operatorname{glue}(a_2)^{-1}
:
\operatorname{inP}(p)=\operatorname{inP}(p).
$$

The loop records the existence of two identity routes. It can later be declared coherent by a 2-path, preserved as a meaningful alternative, or detected as a conflict. A set quotient would erase the distinction immediately.

## 19.4 The recursion principle

To define a nondependent function

$$
h : P\sqcup^h_K E \to X,
$$

it is enough to provide:

$$
h_P : P\to X,
\qquad
h_E : E\to X,
$$

and for every $k:K$ a path:

$$
h_P(f(k))=h_E(g(k)).
$$

This is the universal property internalized as an eliminator. A consumer of the merged ontology must explain how it handles local entities and prove that its outputs respect every approved alignment.

For example, to compute a canonical product-family code from the merge, define local functions from PLM and ERP and prove their outputs agree on each alignment. The resulting function is total on the merge.

The dependent eliminator is stronger. For a family

$$
X : P\sqcup^h_K E \to \mathcal{U},
$$

one supplies local dependent sections plus dependent paths over every glue constructor. This is the mechanism for transporting validators, permissions, and evidence families across the merge.

## 19.5 Merging schemas and merging populations

There are two levels that should not be conflated.

At the **population level**, $P$ and $E$ can be types of local entity references, and the pushout generates an identity space of integrated entities.

At the **schema level**, local ontologies contain many types, relations, and equations. A rigorous merge requires a higher-categorical or type-theoretic colimit of structured theories, not merely a pushout of two carrier types. One practical approach is to represent a schema as an indexed family of entity types and relation families, then form pushouts sort by sort together with constructors enforcing relation compatibility.

This book uses the population-level HIT to explain the identity core and a theory presentation to organize the schema-level obligations. A full formalization would use univalent categories, higher inductive-inductive definitions, or a cubical signature language.

## 19.6 The pump merge

Let:

```text
P points:
  plmRevC
  plmPumpDefinition

E points:
  erpPlantItem4711
  erpItemPump2000
```

Let $K$ contain an approved realization witness:

```text
kPE:
  left  = plmRevC
  right = erpPlantItem4711
  relation = equivalent representation within plant 1000 and interval I
  evidence = mapping rule MR-17 plus engineering approval
```

The pushout contains:

$$
\operatorname{inP}(\mathrm{plmRevC}),
\qquad
\operatorname{inE}(\mathrm{erpPlantItem4711}),
$$

and:

$$
p_{PE}
=
\operatorname{glue}(k_{PE}).
$$

The local points remain available. Their path permits substitution in the approved theory scope. No claim is made that the physical serial, asset record, or functional position is the same point; those are connected by directed relations or different identity-forming alignments with their own criteria.

## 19.7 Adding MES and multiple routes

Add MES entity type $M$ and alignment interfaces. We may form an iterated homotopy pushout. Suppose we have:

$$
p_{PE} : e_{4711}=r_C,
$$

$$
p_{PM} : r_C=m_{82},
$$

and a direct path:

$$
p_{EM} : e_{4711}=m_{82}.
$$

The merge now contains two routes:

$$
p_{EM}
$$

and:

$$
p_{PE}\cdot p_{PM}.
$$

It does not silently assume they are the same path. A coherence constructor must state that if this is intended:

$$
\alpha : p_{EM}=p_{PE}\cdot p_{PM}.
$$

This 2-path is the formal version of a commuting integration triangle.

## 19.8 Candidate, approved, and historical merges

A higher inductive merge should not be regenerated from every proposed match. Maintain distinct theories:

- a **candidate graph** containing heuristic or pending claims as ordinary data;
- an **approved alignment type** supplying path constructors;
- a **historical ledger** retaining revoked and superseded witnesses;
- a **versioned merged type** generated from approvals at a declared governance snapshot.

Revoking an alignment changes the presentation of the merged type. It does not retroactively prove that a path in an earlier theory never existed. Treat the new merge as a new version and define a migration or comparison between versions.

This is analogous to schema evolution: identity governance is theory evolution.

## 19.9 Computational HITs

In axiomatic HoTT, a pushout can be postulated with elimination rules, but computation on path constructors may be propositional. Cubical type theories provide computational higher inductive types, including pushouts and truncations, with judgmental computation behavior for higher constructors in established formulations [R21, R22].

For an ERP ontology engine, computational HITs enable an integrated function defined by the pushout eliminator to reduce on local points and alignment paths rather than remain opaque. This is important for executable validators and code generation.

## 19.10 Exercises

1. Define $K$ as a sigma type of approved alignment witnesses for two local entity spaces.
2. Show how two alignment witnesses between the same endpoints generate a loop.
3. Specify the data needed to define a function from the pushout to a canonical code type.
4. Distinguish a population-level pushout from a schema-level ontology merge in one concrete example.

# Chapter 20. Coherence, Higher Paths, and Semantic Holonomy

## 20.1 A commuting diagram becomes a path between paths

In an ordinary category, a triangle commutes when two composites are equal. In the HoTT merge, the routes are themselves identity paths. Coherence is therefore a higher path.

For:

$$
p : x=y,
\qquad
q : y=z,
\qquad
r : x=z,
$$

triangle coherence is:

$$
\alpha : r = p\cdot q.
$$

This is not merely a Boolean check. The term $\alpha$ can be used to transport dependent information between the two derivations. It is a controlled identification of integration routes.

For the pump case:

$$
\alpha_{EPM} :
\mathrm{erpToMes}
=
\mathrm{erpToPlm}\cdot\mathrm{plmToMes}.
$$

The endpoints, scopes, and path orientations are part of the type. An attempted comparison of routes with different endpoints does not type-check.

## 20.2 Squares, cubes, and higher governance

A four-system integration produces squares. Suppose a serial can be connected to an asset identity through MES or through a corporate master-data hub. The square requires a 2-path comparing its boundary composites.

With several overlapping squares, the 2-paths may themselves be comparable. A cube requires a 3-dimensional coherence condition. Monoidal and categorical structures lead to familiar pentagon and triangle coherence laws.

Industrial architecture should not add higher cells indiscriminately. The rule is:

> Add a coherence constructor whenever downstream behavior must be independent of a choice among explicitly supported routes.

At set level, all route proofs are collapsed. At a higher level, route independence must be earned by coherence.

## 20.3 Transport along a path

Let:

$$
F : X \to \mathcal{U}
$$

be a family over the merged identity space $X$. A path $p:x=y$ induces transport:

$$
\operatorname{tr}_F(p) : F(x)\to F(y).
$$

Because paths are invertible, transport is an equivalence. The family can encode:

- valid codes for an entity;
- permitted operations;
- configuration predicates;
- validators;
- units or dimensions associated with a representation;
- authorization scopes;
- serialization formats;
- evidence requirements.

An alignment path is operationally sound for $F$ only when the induced transport expresses the intended adapter.

## 20.4 Route independence from a 2-path

Given $p,q:x=y$ and:

$$
\alpha:p=q,
$$

applying the transport construction to $\alpha$ proves that transport along $p$ agrees with transport along $q$.

Informally:

$$
\operatorname{tr}_F(p)
=
\operatorname{tr}_F(q).
$$

Thus a 2-path is not abstract excess. It proves that every well-typed dependent construction sees the two integration routes consistently.

In conventional systems, teams prove route independence separately for every attribute, validator, and API. In the HoTT organization, one coherence path induces those equalities generically.

## 20.5 Semantic holonomy

A loop

$$
\ell:x=x
$$

induces an automorphism:

$$
\operatorname{tr}_F(\ell) : F(x)\simeq F(x).
$$

Borrowing terminology from geometry, call this automorphism the **semantic holonomy** of $F$ around $\ell$.

If two integration routes form a loop, transport a dependent value around it. Three outcomes are possible:

1. transport is the identity, so the loop is behaviorally harmless for $F$;
2. transport is a nontrivial intended automorphism, such as a reversible change of coordinates;
3. transport changes meaning unexpectedly, revealing route-dependent semantics.

### Design proposition: zero holonomy for canonical observations

For every observation family declared canonical and route-independent, transport around every approved alignment loop should be homotopic to the identity.

This is a higher form of reconciliation. Instead of comparing only endpoint IDs, it compares the action of the entire loop on dependent meaning.

## 20.6 A unit-conversion loop

Suppose one route expresses pressure in bar, another in pascals, and a third in psi. Each alignment carries a unit equivalence. A loop may be:

```text
bar → pascal → psi → bar
```

The quantity family over representations should transport a value around the loop to the original value, subject to the chosen exact or tolerance semantics.

For exact rational conversions, require a 2-path proving strict round-trip equivalence. For floating-point implementations, equality may be inappropriate; the production extraction uses a tolerance relation, while the formal core uses exact units and delays rounding.

The distinction between mathematical coherence and numerical approximation belongs in the ontology.

## 20.7 A code-system loop

Suppose three plants map equipment class codes:

```text
A: PUMP_CENTRIFUGAL
B: P-01
C: ROTODYNAMIC_7
```

Pairwise bijections may exist. Their composite around the loop could return `PUMP_ROTARY` instead of `PUMP_CENTRIFUGAL` because one mapping collapsed a distinction and another reconstructed it differently.

At the table level, all pairwise mappings may appear valid. Holonomy exposes the defect: the loop acts nontrivially on the classification family. The mappings cannot all be equivalences of the claimed structure.

## 20.8 Coherence cells as governed artifacts

A 2-path should have governance metadata just as a 1-path does. The formal identity proof can be generated from a record containing:

```text
coherence case ID
boundary paths
comparison rule
scope
proof or validation result
review authority
validity interval
theory version
```

At runtime, the record can be stored in a coherence ledger. In the formal theory, its approved inhabitant generates the higher path.

A direct mapping and a composite mapping may agree in output but differ in evidence. The 2-cell can state equality of semantic action while preserving the different provenance fibers.

## 20.9 Coherence completion

Given a graph of alignment generators, a tool can enumerate critical pairs: pairs of paths with common endpoints arising from overlapping mapping rules. For each critical pair, the project must:

- provide a coherence proof;
- declare that the paths intentionally differ;
- refine scopes so they are not comparable;
- reject one route;
- truncate the distinction only in a layer where it is irrelevant.

This resembles completion procedures in rewriting systems. Termination and confluence are not guaranteed for arbitrary ontology theories, but finite bounded path searches can still find high-value integration conflicts.

## 20.10 Higher coherence and scalability

Requiring all paths to be compared explicitly is infeasible. The theory needs generators and general laws. Examples include:

- all unit-conversion paths are coherent because they factor through a canonical dimension representation;
- all code translations are coherent because they are induced by one governed equivalence;
- all ERP-to-MES mappings factor through a shared product realization interface;
- all evidence composition is associative up to a canonical higher path.

A small set of structural theorems can discharge many route obligations. This is the same reason category theory uses functor laws rather than testing every composite individually.

## 20.11 Exercises

1. Draw an integration square and state its 2-path boundary precisely.
2. Choose a dependent family and calculate conceptually what transport around a mapping loop does.
3. Give an example of intended nontrivial holonomy and an example of a defect.
4. Design a coherence ledger record and state which fields remain data rather than identity proofs.

# Chapter 21. Truncation as an Architectural Control

## 21.1 Rich design, flat operation

Conventional databases and APIs generally expect set-like identities. For two canonical IDs, equality should have no observable multiplicity of proofs. The design theory, by contrast, needs multiple paths and higher coherence.

HoTT resolves this tension with truncation. The $n$-truncation

$$
\lVert X\rVert_n
$$

is the best approximation to $X$ whose homotopy level is at most $n$. It preserves information visible at that level and collapses higher distinctions.

The architecture can therefore retain a high-dimensional source theory while deliberately exposing lower-dimensional views.

## 21.2 Propositional truncation

The propositional truncation

$$
\lVert A\rVert_{-1}
$$

says merely that $A$ is inhabited. It hides which witness exists.

For an authorization check, a caller may need only:

$$
\left\lVert
\mathrm{ApprovedPath}(x,y)
\right\rVert_{-1}.
$$

This means “there exists an approved identity route” without revealing the route. It supports privacy and abstraction, but it is insufficient for audit or revocation analysis.

Elimination from propositional truncation is restricted to propositions. One cannot recover a witness-dependent value without additional choice or structure. This restriction is the formal expression of information hiding.

## 21.3 Set truncation

The set truncation

$$
\lVert X\rVert_0
$$

makes every identity type a mere proposition. Points connected by paths remain identified, but all higher distinctions between identity proofs are collapsed.

For an approved merge $M$, define:

$$
\mathrm{CanonicalEntity}
:=
\lVert M\rVert_0.
$$

This is the appropriate semantic target for canonical IDs. A local PLM point and ERP point connected by an approved glue path map to equal elements of `CanonicalEntity`. The operational layer no longer observes whether one or three alignment routes justify the equality.

The path ledger must remain elsewhere if those routes are needed for explanation.

## 21.4 One-truncation and the audit groupoid

The 1-truncation

$$
\lVert M\rVert_1
$$

retains multiple paths but makes higher comparisons set-like. It is a useful model for an audit identity groupoid:

- entities are objects;
- alignment derivations are morphisms;
- coherence proofs compare derivations;
- distinctions above dimension 2 are suppressed.

Many ERP integration programs probably need no more than this level. The unrestricted higher theory provides compositional semantics; the 1-truncated view provides a manageable operational proof graph.

## 21.5 A three-layer identity architecture

A concrete design is:

```text
Layer H — higher design theory
  local entities, alignment generators, 2-cells, higher laws

Layer G — audit groupoid = ‖H‖₁
  explicit identity paths and set-like coherence evidence

Layer C — canonical set = ‖H‖₀
  canonical entity membership for databases and APIs
```

The layers answer different questions.

`C` answers: “Are these references in the same approved canonical identity class?”

`G` answers: “By which approved routes, and how do the routes compare?”

`H` answers: “How are those routes generated compositionally, and what higher laws make the whole theory coherent?”

## 21.6 Explanations over the canonical set

Truncation erases path distinctions, so explanations must retain representatives from the higher layer. One conceptual explanation type for canonical elements $c,d:\lVert M\rVert_0$ is:

$$
\mathrm{Explanation}(c,d)
=
\sum_{x,y:M}
(|x|_0=c)
\times
(|y|_0=d)
\times
(x=y).
$$

An explanation chooses local representatives and a path between them. Several explanations can exist for the same canonical equality.

A production service can store:

```text
canonical entity ID
local membership references
approved path ID
path constructor sequence
coherence normalization record
```

The canonical table remains flat while the explanation store retains the higher witness.

## 21.7 Canonical identifiers require governance

The set truncation yields abstract canonical entities, not UUID strings. Assigning operational identifiers requires a registry:

$$
\mathrm{assign} : \lVert M\rVert_0 \to \mathrm{CanonicalId}.
$$

Desirable properties include stability, injectivity over active entities, versioning, and traceability back to local representatives. Constructing such a function can require choice or an explicit registration process.

The theory therefore separates:

- semantic canonical identity, given by the set truncation;
- operational canonical naming, given by a governed registry.

A UUID is a name for a truncation class, not the cause of that class.

## 21.8 Truncation boundaries

Every service should declare the highest identity level it can observe.

A pricing service may consume only canonical set-level product identities. A reconciliation service needs path-level explanations. A governance console needs candidate claims, rejected paths, and historical theory versions. A proof engine needs the untruncated generators and higher laws.

This is an abstraction boundary enforced by elimination rules. A set-level consumer cannot branch on which equality proof was used. That prevents accidental dependence on an integration route declared irrelevant at that layer.

## 21.9 Quotients versus truncations

A set quotient by a relation and a set truncation of a homotopy quotient can produce similar flat results, but their construction histories differ.

The homotopical workflow is:

```text
retain local points
generate paths from approved witnesses
add higher coherence
then truncate deliberately
```

The naive quotient workflow is:

```text
declare a relation
collapse immediately
reconstruct provenance out of band
```

The first supports design analysis before information loss. The second begins with information loss.

## 21.10 When not to truncate

Do not set-truncate when:

- multiple alignments carry different legal authority;
- route choice changes transported data;
- revocation impact must be calculated;
- mapping loops are under investigation;
- higher coherence is part of certification;
- an equivalence has nontrivial automorphisms relevant to users.

Truncate only after proving that the discarded distinctions are irrelevant for the target consumer.

## 21.11 Exercises

1. Assign the candidate graph, approved path graph, canonical registry, and public API to truncation levels.
2. Define an explanation object over two canonical IDs using higher-layer representatives.
3. Identify a service that currently depends accidentally on a mapping route that should have been truncated away.
4. State the proof obligation needed before exposing only propositional existence of a mapping.

# Chapter 22. Time, Evidence, and Change in a Higher Ontology

## 22.1 Identity theories are versioned

An approved alignment valid today may be revoked tomorrow. It is tempting to model this as a path that appears and disappears over time. A type theory is not a mutable graph. Once a path constructor belongs to a theory, it remains derivable in that theory.

The correct model versions the theory:

$$
M_s
$$

for governance snapshot $s$. A new approval or revocation produces $M_{s'}$ and a comparison map, migration, or partial correspondence between versions.

### Principle: governance change is theory change

Identity is stable relative to a declared ontology version. Changes in approval create a new theory rather than retroactively altering proofs in the old one.

This supports reproducibility: a report can state that it was evaluated in ontology snapshot `OS-204`.

## 22.2 Time-indexed alignment types

For valid time $t$, define:

$$
K(t)
=
\sum_{x:P}\sum_{y:E}
\mathrm{ApprovedAt}(x,y,t).
$$

The merge at $t$ is:

$$
M(t)=P\sqcup^h_{K(t)}E.
$$

This notation is conceptually useful but expensive if treated as an independently rebuilt type for every instant. In implementation, use intervals and governance snapshots, forming one theory per interval partition or release.

A path valid in $M(t_1)$ is not automatically a path in $M(t_2)$. A monotone map exists only when the later alignment set contains the earlier one and no incompatible changes are introduced. Revocation breaks monotonicity.

## 22.3 Time is directed

Time has an order and irreversible observations. It should usually be modeled by a category or preorder, not by identity paths. A time-indexed ontology is a functor or dependent family over time:

$$
\mathcal{M} : \mathrm{Time} \to \mathcal{U}
$$

with transition maps in the chosen direction when they exist.

Similarly, lifecycle evolution is not equality. Revision D superseding revision C is a directed relation:

$$
\mathrm{Supersedes}(D,C).
$$

The two revisions may induce equivalent observable interfaces for a customer or plant, yielding a path in a *view universe*, while remaining distinct revision entities in the lifecycle theory.

This distinction prevents HoTT from collapsing historical change into sameness.

## 22.4 Dependent paths across changing representations

Cubical type theory provides dependent path types, often written `PathP`. Given a family:

$$
A : I\to\mathcal{U}
$$

over an interval $I$, and endpoints $a_0:A(0)$ and $a_1:A(1)$, a dependent path is:

$$
\mathrm{PathP}(A,a_0,a_1).
$$

For schema evolution, let $A(i)$ interpolate between representation versions. A `PathP` can express that a record changes coherently with the representation rather than being transported inside a constant type.

Conceptually:

```text
schema at version 1  ───────── schema path ───────── schema at version 2
record v1            ───── dependent record path ─── record v2
```

This is a more faithful model of coupled schema-and-data migration than treating the schema as fixed and converting only values.

## 22.5 Provenance over paths

Let $M$ be a merged identity type. Define a provenance family:

$$
\mathrm{Prov} :
\prod_{x,y:M}(x=y)\to\mathcal{U}.
$$

For every identity path $p:x=y$, `Prov p` is the type of admissible provenance packages for that path.

On a generating glue path, provenance comes from the alignment witness. On reflexivity, it may be a canonical empty derivation. On composition, provenance combines:

$$
\mathrm{Prov}(p)
\to
\mathrm{Prov}(q)
\to
\mathrm{Prov}(p\cdot q).
$$

On inversion, provenance records reversal of an identity use without pretending the underlying evidence relation was symmetric. The path is invertible, but the explanation of the inverse can state that it derives from reversing an approved equivalence.

## 22.6 Evidence and 2-paths

If:

$$
\alpha:p=q,
$$

then provenance over $p$ can be transported to provenance over $q$:

$$
\operatorname{transport}^{\mathrm{Prov}}(\alpha)
:
\mathrm{Prov}(p)\to\mathrm{Prov}(q).
$$

This models coherence of explanations. A direct mapping and a composite mapping may have different raw evidence, yet a 2-path can provide a structured transformation between their explanation forms.

The target need not require literal equality of evidence lists. It can define an evidence abstraction family whose transport preserves authority, scope, and conclusion while allowing different source records.

## 22.7 Bitemporal proof objects

A proof object can carry both validity and recording intervals:

$$
\mathrm{Evidence}(p,I_v,I_t).
$$

The path $p$ belongs to ontology version $s$; the evidence says when the claim is valid and when the enterprise considered it active. Historical evaluation selects:

- ontology snapshot $s$;
- valid time $t_v$;
- transaction time $t_t$;
- source data snapshot.

A reproducible query result should record all four. “As of” is otherwise ambiguous.

## 22.8 Revocation and dependency

Revocation creates a new theory version without the corresponding constructor or with a blocking governance rule. Existing derived paths in the old theory remain historical facts about what was accepted then.

To calculate impact:

1. index every generated path by its constructor dependencies;
2. find paths depending on the revoked alignment;
3. attempt to reconstruct them in the new theory through alternate routes;
4. compare alternate routes with surviving coherence cells;
5. update canonical memberships and explanations.

This turns semantic governance into incremental proof maintenance.

## 22.9 Uncertainty is not homotopy

Multiple paths do not automatically represent probabilistic uncertainty. A path is an inhabitant of an identity type under the theory's rules. Confidence scores, likelihoods, and statistical entity matching require a separate quantitative structure.

A responsible pipeline is:

```text
probabilistic matcher
  → candidate claim with confidence
human/rule review
  → approved alignment witness
HIT constructor
  → identity path in a versioned theory
```

Do not generate identity paths directly from similarity scores unless the ontology explicitly defines and accepts that criterion.

## 22.10 Directed higher structure

Industrial processes combine higher identity with directed change. A complete foundation may need directed type theory, $(\infty,1)$-categories with noninvertible 1-morphisms and higher invertible cells, double categories, or displayed higher categories.

The pragmatic architecture in this book uses:

- categories and dependent relations for directed industrial processes;
- HoTT for entity identity, equivalence, and path coherence;
- families over time and governance snapshots for change;
- truncation for operational views.

This division is implementable now and identifies where further theory is needed.

## 22.11 Exercises

1. Model an alignment revocation as a change of theory version rather than deletion of a proof.
2. Give a directed relation between revisions and an equivalence between restricted revision views.
3. Define the fields needed for a bitemporal, snapshot-reproducible explanation.
4. State how provenance should compose and how a 2-path should transform it.

# Chapter 23. An ERP Ontology Calculus

## 23.1 Purpose

We now collect the preceding constructions into a calculus: a small language of declarations and proof obligations for industrial ontologies. The calculus is not intended to replace OWL, SQL, BPMN, OPC UA, or enterprise modeling tools. It supplies a semantic core from which those artifacts can be generated or checked.

An ontology package should answer:

- what local theories exist;
- what kinds of entities and directed relations they contain;
- what alignment witnesses generate identity paths;
- what higher coherence cells compare routes;
- what time and governance snapshot indexes the theory;
- what truncation level each consumer observes;
- what conventional artifacts are extracted.

## 23.2 The signature of a package

Write an ERP ontology package as:

$$
\mathcal{O}
=
(\mathcal{L},\mathcal{D},\mathcal{K},\mathcal{G},\mathcal{C},\mathcal{V},\mathcal{T}).
$$

The components are:

- $\mathcal{L} = \{L_i\}$: local dependent theories for PLM, ERP, MES, EAM, QMS, and other contexts;
- $\mathcal{D}$: directed domain relations, workflows, events, and data dependencies;
- $\mathcal{K} = \{K_{ij}\}$: types of approved alignment witnesses between local entity spaces;
- $\mathcal{G}$: generating path constructors induced by the alignments;
- $\mathcal{C}$: generating higher coherence cells;
- $\mathcal{V}$: version, valid-time, transaction-time, and source-snapshot parameters;
- $\mathcal{T}$: truncation and extraction policies.

The merged higher identity theory is generated from the local entity spaces and $\mathcal{G}$, subject to $\mathcal{C}$. Directed relations from $\mathcal{D}$ are transported or displayed over that identity theory but are not turned into invertible paths.

## 23.3 Ten principles

### Principle 1: contextual typing

Every local reference has a context and kind. No raw identifier crosses a boundary without refinement.

$$
\mathrm{Ref}(c,k).
$$

### Principle 2: identity stratification

Definitions, revisions, commercial items, lots, units, roles, positions, events, and records are distinct kinds unless an explicit theory says otherwise.

### Principle 3: directedness preservation

Workflow, causation, consumption, supersession, installation, and time remain directed relations. They do not become equality paths merely because they connect entities.

### Principle 4: evidence-generated identity

A cross-context identity path is generated only by an inhabitant of an approved alignment type.

$$
\mathrm{glue} : K_{ij}(x,y) \to (x=y).
$$

### Principle 5: temporal and governance indexing

Every approved merge is relative to an ontology version and declared temporal scope. Revocation creates a new theory version.

### Principle 6: functorial local translation

Schema and instance mappings preserve identities, composition, and declared equations. Partiality and scope must be explicit.

### Principle 7: coherence completion

Supported parallel routes are either compared by higher paths, separated by scope, or reported as unresolved. Silent route choice is forbidden.

### Principle 8: semantic holonomy control

Canonical dependent observations must have trivial transport around approved loops, unless a nontrivial automorphism is explicitly intended.

### Principle 9: truncation discipline

Higher identity information is discarded only at a named interface and only after proving it irrelevant to that consumer.

### Principle 10: operational traceability

Every extracted canonical identity, migration, and query answer retains a reference to a derivation in the higher or audit layer.

## 23.4 Declarations in a possible DSL

A surface language might look like this:

```text
ontology PumpThread version OS-204 {

  context PLM {
    kind ProductDefinition
    kind ProductRevision
    relation revisionOf : ProductRevision -> ProductDefinition
  }

  context ERP plant "1000" {
    kind Item
    kind PlantItem
    relation itemOf : PlantItem -> Item
  }

  alignment PE_17
    left  PLM.ProductRevision("PUMP-2000/C")
    right ERP[1000].PlantItem("4711")
    as EquivalentRepresentation
    valid [2025-01-01, 2026-12-31)
    by rule "MR-17"
    approvedBy "ENG-BOARD"

  cohere EPM_4 {
    direct ERP.toMES
    equals ERP.toPLM ; PLM.toMES
    on productFamily "PUMP-2000"
  }

  view CanonicalProducts : setTruncation ApprovedProductMerge
  view AuditProducts     : oneTruncation ApprovedProductMerge
}
```

The compiler elaborates names to typed references, checks relation admissibility, constructs path generators, and emits coherence obligations.

## 23.5 Static verification conditions

The calculus generates obligations in layers.

### Local theory obligations

- every relation has well-formed endpoint kinds;
- every path equation is well typed;
- every local instance satisfies required equations;
- workflow transitions preserve declared invariants;
- quantity expressions are dimensionally valid.

### Alignment obligations

- endpoints belong to the declared contexts and kinds;
- the relation kind is admissible for the endpoint kinds;
- scope and validity are nonempty and well formed;
- required evidence and authority are present;
- a claimed equivalence has forward, backward, and inverse laws.

### Merge obligations

- protected local distinctions are not collapsed unintentionally;
- parallel paths have a coherence policy;
- path constructors do not import candidate or revoked claims;
- dependent families define transport on every generator.

### Extraction obligations

- set-level consumers cannot observe path representatives;
- every canonical membership has at least one approved explanation;
- generated migrations preserve declared identifiers and invariants;
- version and snapshot identifiers are included in results.

## 23.6 Semantics of commands

The main commands have mathematical meanings.

`import` adds a local theory and a functor from a standard or source schema.

`align` adds a witness to an interface type $K_{ij}$; when approved, it generates a path constructor.

`cohere` adds a higher path between parallel generated paths.

`merge` forms a homotopy colimit or a controlled sequence of homotopy pushouts.

`view` applies truncation or a dependent observation.

`extract` generates conventional types, constraints, APIs, or migration code from a view.

`reconcile` compares current source instances against the path and equation laws.

`explain` returns a representative path and provenance package for a set-level conclusion.

## 23.7 Design propositions

The following propositions organize a formal development. Each requires precise assumptions.

### Proposition: endpoint soundness

Every generated identity path connects endpoints of an admissible identity-forming relation in the declared theory version.

The proof follows from restricting path constructors to approved inhabitants of typed interface families.

### Proposition: local equation preservation

If a local instance satisfies its schema equations and a mapping functor preserves the presentation, the reindexed instance satisfies the mapped equations.

This is ordinary functoriality.

### Proposition: coherence-induced route invariance

If $\alpha:p=q$, then every dependent family transports identically along $p$ and $q$ up to the path induced by $\alpha$.

This is the generic payoff of higher coherence.

### Proposition: truncation nonobservability

A function defined on $\lVert M\rVert_0$ cannot distinguish alignment paths beyond their induced set-level equality.

This follows from the elimination principle of set truncation.

### Proposition: explanation soundness

Every extracted canonical membership is backed by a path in the approved higher merge and by provenance satisfying the current extraction policy.

This is proved by making extraction proof-producing.

### Proposition: historical reproducibility

A result tagged with ontology version, valid time, transaction time, and source snapshot can be rechecked against the preserved theory and source evidence for those indices.

This depends on immutable versioned artifacts and retained evidence, not on type theory alone.

## 23.8 Conservativity as a release gate

Before a merge version is released, protected local entities should be checked for new identifications. For each context $L_i$, consider the injection:

$$
\iota_i : L_i \to M.
$$

A strong conservativity goal is that if:

$$
\iota_i(x)=\iota_i(y),
$$

then the local theory can derive the intended local equivalence between $x$ and $y$. This may be too strong when deliberate cross-system aggregation collapses local distinctions. The package should therefore declare protected kinds and permitted collapse policies.

For example:

- two PLM revisions are protected from collapse;
- several supplier codes may collapse to one commercial equivalence class;
- several historical EAM records may map to one physical unit while remaining distinct records.

Conservativity is kind- and view-sensitive.

## 23.9 Normal forms and path policies

An ontology engine may normalize paths to preferred explanations. A normal form is a policy, not the definition of equality. Possible policies include:

- prefer direct certified alignments;
- factor all product mappings through PLM;
- factor all physical identity through serialization;
- use a canonical unit system;
- exclude deprecated standards mappings.

A normalization theorem should state that every approved path is coherent with its normal form. Without such a theorem, normalization can silently change meaning.

## 23.10 Exercises

1. Instantiate the seven components of $\mathcal{O}$ for a two-system integration.
2. Write a DSL declaration for a time-scoped approved substitute and decide whether it generates an identity path.
3. Choose three protected kinds and state their conservativity policies.
4. Define a path-normalization policy and list the coherence theorems it requires.

# Chapter 24. End-to-End Case Study: Product to Plant

## 24.1 Scope

The case study follows a pump assembly from engineering definition through planning, execution, quality, and maintenance. It focuses on five questions:

1. What revision was approved?
2. What did the plant plan to build?
3. What materials and components were actually used?
4. What physical configuration is installed now?
5. Why do the records across systems refer to the entities claimed by the answer?

The systems are represented by local theories, not by vendor-specific schemas.

## 24.2 Local PLM theory

Entity kinds:

```text
ProductDefinition
ProductRevision
AssemblyOccurrence
CharacteristicDefinition
EngineeringChange
DocumentRevision
```

Directed relations:

```text
revisionOf          : ProductRevision -> ProductDefinition
parentRevision      : AssemblyOccurrence -> ProductRevision
childRevision       : AssemblyOccurrence -> ProductRevision
characteristicOf    : CharacteristicDefinition -> ProductRevision
releasedBy          : ProductRevision -> EngineeringChange
```

Equations ensure that direct definition links agree with routes through revisions. The running objects are:

```text
PD-PUMP-2000
PR-PUMP-2000-C
PR-MOTOR-550-C2
AO-MOTOR-01
CHAR-DISCHARGE-PRESSURE
```

## 24.3 Local ERP theory

Entity kinds:

```text
Item
PlantItem
BomRevision
BomLine
ProductionOrder
PurchaseInfoRecord
ApprovedSource
```

Directed relations:

```text
itemOf              : PlantItem -> Item
bomFor              : BomRevision -> PlantItem
lineParent          : BomLine -> BomRevision
lineComponent       : BomLine -> PlantItem
orderItem           : ProductionOrder -> PlantItem
selectedBom         : ProductionOrder -> BomRevision
```

The running objects include:

```text
ITEM-4711
PLANTITEM-1000-4711
MBOM-C-1000
PO-700041
```

ERP deliberately does not assert that `PLANTITEM-1000-4711` is the PLM revision. It records planning and valuation objects.

## 24.4 Local MES theory

Entity kinds:

```text
MaterialDefinition
MaterialLot
SerializedUnit
JobOrder
WorkExecution
MaterialRequirement
MaterialActual
EquipmentResource
```

Directed relations:

```text
jobMaterial         : JobOrder -> MaterialDefinition
executionOf         : WorkExecution -> JobOrder
producedSerial      : WorkExecution -> SerializedUnit
actualLot           : MaterialActual -> MaterialLot
consumedIn          : MaterialActual -> WorkExecution
lotDefinition       : MaterialLot -> MaterialDefinition
```

Running objects:

```text
MAT-M82
LOT-L882
SERIAL-S1044
JOB-JO40
EXEC-WE51
ACTUAL-MA18
```

## 24.5 Local EAM and QMS theories

EAM kinds:

```text
PhysicalUnit
AssetRecord
FunctionalPosition
InstallationAssignment
MaintenanceOrder
```

QMS kinds:

```text
InspectionSpecification
InspectionExecution
Measurement
AcceptanceDecision
Nonconformance
```

The physical unit represented by serial `S-1044` is recorded by asset record `E-90017` and occupied functional position `CP-4` during interval $I_1$. After replacement, serial `S-2088` occupies `CP-4` during $I_2$.

QMS measurement `MEAS-603` evaluates the discharge-pressure characteristic under specification `ISP-44`.

## 24.6 Interfaces and alignment witnesses

### PLM-ERP interface

An alignment witness $k_{PE}$ contains:

```text
PLM endpoint: PR-PUMP-2000-C
ERP endpoint: PLANTITEM-1000-4711
relation: EquivalentRepresentation
scope: plant 1000, product family PUMP-2000
validity: [2025-01-01, 2026-12-31)
evidence: rule MR-17, engineering approval EA-91
```

The strength `EquivalentRepresentation` is justified only for the planning interface selected by the project. It does not identify every PLM and ERP attribute.

### PLM-MES interface

Witness $k_{PM}$ connects `PR-PUMP-2000-C` to `MAT-M82` under manufacturing-definition rule `MM-12`.

### ERP-MES interface

Witness $k_{EM}$ directly connects `PLANTITEM-1000-4711` to `MAT-M82` under interface mapping `IF-ERP-MES-8`.

### MES-EAM interface

Witness $k_{MA}$ connects MES serial `S-1044` to the EAM physical-unit representation used by asset record `E-90017`. The asset record itself is related by `Represents`; it is not the same identity kind.

### PLM-QMS interface

An equivalence connects the PLM characteristic definition to the QMS inspection-specification view after unit and tolerance normalization.

## 24.7 The higher merge

Let $D$ be the diagram of local entity spaces and approved interface types. Define the integrated identity theory as the homotopy colimit:

$$
H := \operatorname{hocolim} D.
$$

An implementation can build $H$ as an iterated sequence of homotopy pushouts while generating associativity and comparison obligations.

The theory contains paths:

$$
p_{PE} : [\mathrm{ERP}	ext{-}4711]=[\mathrm{PLM}	ext{-}\mathrm{RevC}],
$$

$$
p_{PM} : [\mathrm{PLM}	ext{-}\mathrm{RevC}]=[\mathrm{MES}	ext{-}\mathrm{M82}],
$$

$$
p_{EM} : [\mathrm{ERP}	ext{-}4711]=[\mathrm{MES}	ext{-}\mathrm{M82}].
$$

Square brackets here denote the corresponding point constructor in $H$.

The integration board approves a coherence cell:

$$
\alpha_{EPM} : p_{EM}=p_{PE}\cdot p_{PM}.
$$

This proves route independence for every dependent family over $H$.

## 24.8 Transporting a validation family

Define:

$$
\mathrm{ProductValidation} : H\to\mathcal{U}.
$$

At the PLM point, the family contains engineering revision validations. At the ERP point, it contains plant-planning validations. At the MES point, it contains execution-material validations. The pushout eliminator requires equivalences across each generating alignment.

Transporting a PLM validation along $p_{PE}$ yields the corresponding ERP validation. Transporting further along $p_{PM}$ yields the MES validation. The 2-path $\alpha_{EPM}$ proves this agrees with direct transport along $p_{EM}$.

This replaces three separately maintained “mapping preserves validation” implementations with one family and one coherence cell.

## 24.9 The as-built trace

The directed trace remains separate from identity. We have:

```text
S-1044
  producedBy WE-51
  executionOf JO-40
  consumedActual MA-18
  actualLot L-882
  lotDefinition MAT-M82
```

The identity theory connects `MAT-M82` to the PLM/ERP product representation. Composition yields an explanation from consumed lot to approved product revision, combining directed trace steps with identity transports.

A result can be rendered as:

```json
{
  "serial": "S-1044",
  "consumedLot": "L-882",
  "productRevision": "PUMP-2000/C",
  "ontologyVersion": "OS-204",
  "validTime": "2025-08-09T10:00:00Z",
  "sourceSnapshot": "SNAP-8f2a",
  "tracePath": ["WE-51", "JO-40", "MA-18", "L-882"],
  "identityPath": ["k_PM"],
  "coherenceCases": []
}
```

The public API may omit the path arrays and return an explanation ID. The audit API retains them.

## 24.10 The installed unit at alarm time

Alarm `AL-77` occurred at time $t_a$. The query is:

$$
\sum_{u:\mathrm{PhysicalUnit}}
\mathrm{InstalledAt}(u,\mathrm{CP4},t_a)
\times
\mathrm{ObservedAlarmOn}(\mathrm{AL77},\mathrm{CP4},t_a).
$$

The result selects `S-1044` because $t_a\in I_1$. It does not select `S-2088`, whose interval begins later. The MES-EAM identity path lets the query transport from the EAM physical-unit representation to the MES serial representation and then follow the as-built trace.

The answer can therefore connect an operational alarm to the engineering revision and consumed lots of the unit occupying the position at that time.

## 24.11 Canonical extraction

Define:

$$
C:=\lVert H\rVert_0.
$$

A canonical registry assigns:

```text
CE-PRODUCT-0091
```

as the operational ID for the set-level class containing the PLM revision view, ERP plant-item view, and MES material-definition view under the approved scope.

The registry does **not** put serial `S-1044`, lot `L-882`, asset record `E-90017`, or position `CP-4` into the same class. They remain related entities of different kinds.

A canonical membership table stores:

```text
CE-PRODUCT-0091 ↔ PR-PUMP-2000-C
CE-PRODUCT-0091 ↔ PLANTITEM-1000-4711
CE-PRODUCT-0091 ↔ MAT-M82
```

Each membership references an explanation path in the audit layer.

## 24.12 Failure case: incoherent direct mapping

Assume the direct ERP-MES mapping changes to `MAT-M91`, while the PLM route still reaches `MAT-M82`.

Then the proposed 2-path has mismatched endpoints:

$$
p_{EM} : e_{4711}=m_{91},
$$

$$
p_{PE}\cdot p_{PM} : e_{4711}=m_{82}.
$$

The coherence term cannot even be stated until a path $m_{91}=m_{82}$ is supplied. The compiler reports an endpoint mismatch rather than a failed string comparison.

The integration release is blocked or the scopes are refined. This is a concrete advantage of higher typing: some incoherence becomes unformulable.

## 24.13 Failure case: overlapping installation

Suppose `S-1044` and `S-2088` both have installation assignments at `CP-4` over overlapping intervals. This is not a higher identity conflict. It violates a directed temporal invariant:

$$
\forall a,b,
\mathrm{position}(a)=\mathrm{position}(b)
\land a\neq b
\Rightarrow
\mathrm{disjoint}(\mathrm{interval}(a),\mathrm{interval}(b)).
$$

The dependent temporal layer rejects the EAM instance. HoTT does not replace ordinary domain invariants.

## 24.14 Failure case: revoked mapping

Mapping rule `MR-17` is revoked. Ontology version `OS-205` omits $k_{PE}$ or replaces it with a narrower witness. The system searches explanations depending on $p_{PE}$.

The direct path $p_{EM}$ may still connect ERP and MES. PLM-linked canonical membership may lose its proof unless another route survives. Historical reports under `OS-204` remain reproducible; current results under `OS-205` change explicitly.

## 24.15 What HoTT bought in this case

The categorical layer provided typed local schemas and compositional mappings. The dependent layer provided evidence, states, quantities, time, and proof-carrying traces. HoTT contributed four additional capabilities:

1. approved alignments generated identity paths without erasing local points;
2. scoped equivalences became universally substitutable through univalence;
3. direct and composite integration routes were compared by a 2-path with generic consequences;
4. canonical set-level identities were extracted by truncation while the path ledger remained available.

That is the practical core of a HoTT-organized ERP ontology.

## 24.16 Exercises

1. Add a supplier catalog and approved-source interface to the case study. Decide which relationships generate paths.
2. Define a coherence square connecting PLM, ERP, supplier, and MES representations.
3. Specify the dependent family transported across the square and its zero-holonomy requirement.
4. Design the theory-version change produced by replacing revision C with revision D.

# Chapter 25. Building a HoTT-Oriented Ontology Engine

## 25.1 Type engine, proof engine, ontology engine

A **type engine** checks that a term inhabits a type. A **proof engine** constructs terms intended to inhabit goal types. An **ontology engine** adds a domain-specific surface language, governed declarations, migrations, queries, and extraction.

The architecture should keep these layers separate:

```text
ERP ontology DSL
        ↓
parser and name resolver
        ↓
elaborator, unifier, and ontology-specific tactics
        ↓
explicit higher type-theory term
        ↓
small trusted kernel/type checker
        ↓
checked theory package and certificates
        ↓
SQL, APIs, validators, tests, explanation graph
```

Automation may be sophisticated and fallible. Soundness depends on the kernel rechecking the explicit term.

Lean follows the same broad trust pattern: elaboration and tactics construct proof terms, while a small kernel validates them [R1–R3]. Lean 4 is therefore a strong host language for the engine even when the object theory is not Lean's native theory.

## 25.2 Stage one: a conventional Lean 4 prototype

Before implementing cubical type theory, build the ontology language directly in Lean 4 using:

- indexed references and relations;
- the small category and path definitions from Part I;
- evidence-bearing dependent structures;
- explicit derivation types in `Type`;
- set-level canonicalization policies;
- theorem-generated validators and tests.

Simulate higher paths as explicit data structures:

```lean
inductive IdentityDerivation : EntityRef → EntityRef → Type
  | refl : IdentityDerivation x x
  | generator : ApprovedAlignment x y → IdentityDerivation x y
  | symm : IdentityDerivation x y → IdentityDerivation y x
  | trans :
      IdentityDerivation x y →
      IdentityDerivation y z →
      IdentityDerivation x z

structure Coherence {x y : EntityRef}
    (p q : IdentityDerivation x y) where
  caseId : String
  justification : String
```

This is not native HoTT: `Coherence p q` is ordinary data, not the identity type `p=q`. It is still useful for validating the DSL, governance workflow, and case studies before committing to a new kernel.

## 25.3 Stage two: an explicit higher object language

A small dependent core can be represented as syntax in Lean.

```lean
inductive HTerm where
  | var      : Nat → HTerm
  | sort     : Nat → HTerm
  | pi       : HTerm → HTerm → HTerm
  | sigma    : HTerm → HTerm → HTerm
  | lam      : HTerm → HTerm
  | app      : HTerm → HTerm → HTerm
  | pair     : HTerm → HTerm → HTerm
  | fst      : HTerm → HTerm
  | snd      : HTerm → HTerm

  | interval : HTerm
  | i0       : HTerm
  | i1       : HTerm
  | pathP    : HTerm → HTerm → HTerm → HTerm
  | pathLam  : HTerm → HTerm
  | pathApp  : HTerm → HTerm → HTerm

  | pushout  : HTerm → HTerm → HTerm → HTerm
  | inl      : HTerm → HTerm
  | inr      : HTerm → HTerm
  | glue     : HTerm → HTerm

  | trunc    : Int → HTerm → HTerm
```

This is a sketch, not a complete cubical syntax. A real core must encode binders, interval variables, face formulas, systems, composition operations, universes, and the parameters of each constructor precisely.

The key architectural point is that `HTerm.pathP` belongs to the object language. It is not Lean's `Eq`.

## 25.4 Core dependent type checking

Start with ordinary dependent type theory. Implement:

```text
eval  : Environment → Term → Value
quote : Level → Value → Term
conv  : Level → Value → Value → CheckM Unit
infer : Context → Term → CheckM Value
check : Context → Term → Value → CheckM Unit
```

Use normalization by evaluation or a related semantic evaluator. Values include closures and neutral terms. Bidirectional checking separates inferable terms from terms checked against an expected type.

Core rules include:

```text
infer variable
infer universe
infer application
check lambda against Pi
check pair against Sigma
conversion by normalized equality
```

Do not begin with implicit arguments, type classes, tactics, or ontology syntax. First establish a small explicit kernel with a test suite.

## 25.5 Cubical primitives

A computational HoTT kernel needs more than an intensional identity type. In a cubical design, the trusted theory includes concepts such as:

- an interval $I$ with endpoints $0,1$;
- interval expressions and face formulas;
- path abstraction and application;
- dependent path types `PathP`;
- partial elements and compatible systems;
- transport;
- homogeneous and dependent composition;
- Glue types or another computational account of univalence;
- higher inductive types with boundary computation.

Composition is central. It fills an open cube from compatible boundary data. Type formers define how composition computes. This supports Kan structure, path transport, and univalence [R10, R11].

Implementing conversion now requires normalization of interval substitutions and systems in addition to beta reduction. This is the major increase in kernel complexity.

## 25.6 Higher inductive declarations

The ontology language needs at least pushouts and truncations. There are two implementation strategies.

**Built-in primitives** add dedicated syntax and reduction rules for `Pushout` and `Trunc`. This is manageable for a research prototype but grows the trusted kernel.

**A general HIT schema** lets users declare point, path, and higher constructors with boundaries. It is more reusable but much harder to validate for positivity, substitution stability, and computation.

A practical first kernel should implement a fixed set:

```text
Pushout
propositional truncation
set truncation
possibly 1-truncation
```

These cover the ontology architecture without attempting every higher inductive type.

## 25.7 Elaboration of ontology declarations

The surface declaration:

```text
alignment PE_17 left p right e by evidence a
```

elaborates to:

1. endpoint terms $p:P$ and $e:E$;
2. a checked evidence term $a:K(p,e)$;
3. a path term `glue a : inP p = inE e`;
4. provenance metadata stored outside or in a dependent family over the path;
5. a stable declaration name for later coherence terms.

A coherence declaration elaborates its route expressions, normalizes endpoints, and creates a goal:

$$
p=q.
$$

An endpoint mismatch is reported before proof search.

## 25.8 Ontology-specific tactics

Useful tactics include:

```text
intro-context
exact-alignment PE_17
compose-route
invert-route
normalize-route
apply-coherence EPM_4
transport-family ProductValidation
prove-zero-holonomy
truncate-to-set
explain-path
```

These tactics construct explicit terms. For example, `normalize-route` applies approved 2-cells and associativity paths to transform a composite into the declared normal form. The kernel checks the resulting higher equality.

Proof search should remain bounded and explainable. A suggested route is a candidate; the checked path term is the certificate.

## 25.9 Metavariables and higher unification

The elaborator needs metavariables for omitted endpoints, implicit context parameters, universe levels, and path holes. Ordinary higher-order unification is already difficult. Cubical terms add interval dimensions and boundary constraints.

Restrict the first implementation:

- require most ontology endpoints explicitly;
- use pattern-style unification where possible;
- make scopes and theory versions explicit;
- require annotations at higher inductive boundaries;
- solve route goals by named generators and bounded composition, not unrestricted search.

Good error reporting is more valuable than maximal inference. An enterprise ontology must show which scope, endpoint, or coherence obligation failed.

## 25.10 Trusted and untrusted components

The trusted computing base should include only:

- parser-independent core syntax representation;
- evaluator and conversion checker;
- typing rules;
- universe and cubical composition machinery;
- fixed HIT rules;
- certificate reader.

The following remain untrusted:

- ontology matching;
- language-model suggestions;
- tactic search;
- SQL and API code generators;
- diagram visualization;
- external source ingestion;
- incremental caches.

Generated artifacts include a certificate or core term that can be rechecked independently.

## 25.11 Code extraction

The higher theory itself may not compile directly to ordinary application code. Extraction targets truncated views and pure functions.

For a set-truncated entity view, generate:

- canonical ID types;
- membership tables;
- endpoint validators;
- route-independent lookup functions;
- explanation references;
- schema-version tags.

For dependent state machines and quantities, extract executable Lean functions or translate their specifications into another verified or tested implementation.

The extraction theorem should state that generated results correspond to terms in the selected truncated view and that every membership references a checked higher path.

## 25.12 Verification of the verifier

Writing a checker in Lean does not automatically prove it sound. A longer-term goal is to formalize:

- the typing judgment;
- operational or denotational semantics;
- substitution;
- weakening;
- subject reduction;
- normalization or canonicity;
- decidability of conversion for the selected core;
- soundness of the executable checker against the judgment.

Projects such as Lean4Lean illustrate the value of an independently checkable type checker written in Lean for Lean's own theory [R23]. A HoTT ontology engine should similarly separate the abstract theory from the implementation and prove their relationship.

## 25.13 Testing strategy

The kernel and ontology compiler need several test classes.

**Positive golden tests** check known well-typed theories and their normal forms.

**Negative tests** ensure malformed paths, illegal kinds, bad boundaries, and incoherent routes are rejected.

**Metatheory tests** exercise substitution, weakening, and conversion.

**Model-based tests** compare small finite or groupoid models where semantics is computable.

**Fuzz tests** generate syntax and verify that evaluator and checker agree, subject to resource limits.

**Industrial regression tests** preserve every discovered mapping defect as a minimal theory package.

## 25.14 Performance architecture

Large ontology graphs require incremental behavior. Useful techniques include:

- hash-consed core terms;
- memoized normalization;
- content-addressed theory declarations;
- dependency-indexed invalidation;
- union-find only for the set-truncated operational layer, never as a replacement for the path theory;
- bounded route normalization;
- separate caches by ontology version and source snapshot;
- proof term sharing for repeated standard alignments.

The path layer can be large even when the canonical set is small. Store generators and normal forms rather than enumerating all composites.

## 25.15 An implementation roadmap

A disciplined sequence is:

1. typed local identifiers and relation signatures in Lean 4;
2. categorical schemas, instances, and equation validators;
3. alignment and provenance ledger;
4. dependent workflows, quantities, and trace derivations;
5. explicit groupoid-style identity derivations as ordinary Lean data;
6. ontology DSL, elaborator, and code generation for set-level views;
7. a small standalone dependent type checker implemented in Lean;
8. cubical interval, path, transport, and composition;
9. computational univalence;
10. pushout and truncation HITs;
11. higher ontology elaboration and coherence tactics;
12. independent certificate checker and industrial case-study validation.

At milestone 6, the project already provides practical value. Milestones 7–12 turn the HoTT organizing structure into a native computational foundation.

## 25.16 Alternative: target Cubical Agda first

A lower-risk path is to formalize the HoTT case study in Cubical Agda while building the conventional ontology tooling in Lean 4. Cubical Agda already provides computational univalence, path types, composition, and higher inductive support [R10]. The experiment can validate:

- the homotopy-pushout merge;
- 2-path coherence;
- transport of dependent validators;
- truncation-based extraction specifications.

Once the desired core is understood, implement only the required fragment in Lean. This avoids designing a cubical kernel before the ontology semantics is stable.

## 25.17 Exercises

1. Extend `HTerm` with explicit binders for `PathP` and state the typing rule.
2. Classify each component of the proposed engine as trusted or untrusted.
3. Design the core term generated by an `alignment` declaration.
4. Choose whether your first prototype should axiomatize HoTT, target Cubical Agda, or implement a cubical object language. State the tradeoff.

# Chapter 26. Research Program and Engineering Agenda

## 26.1 The open synthesis

The components of this book are individually mature enough to use: categorical schemas, functorial data migration, dependent types, proof assistants, univalence, higher inductive types, and industrial reference models. Their synthesis into a practical ERP ontology discipline remains open.

The research task is not to demonstrate that a pushout can merge two toy sets. It is to determine whether higher identity yields measurable improvements in industrial semantic integration while preserving governance, performance, and comprehensibility.

## 26.2 Formal foundation questions

A complete theory must make the schema level precise. Candidate foundations include:

- univalent categories of local schemas;
- homotopy colimits of typed signatures;
- higher inductive-inductive definitions of sorts and relations;
- displayed categories or fibrations over identity spaces;
- $(\infty,1)$-categorical models combining directed morphisms and higher equivalence;
- double or equipment-like structures for schemas, instances, mappings, and transformations.

The key formal question is:

> What is the smallest higher type theory in which local industrial theories, evidence-generated identity, directed relations, coherent merge, and executable truncation can all be represented with usable computation?

## 26.3 Conservativity and collapse analysis

Pushout-style merging can collapse distinctions. Research is needed on automated diagnostics for:

- protected local injectivity;
- fibers of interface mappings;
- loops generated by multiple alignments;
- path-space growth;
- conditions under which set truncation matches intended canonical classes;
- countermodels demonstrating an unintended identification.

A useful tool should produce human-readable collapse reports before approving a merge.

## 26.4 Directed processes and higher identity

ERP systems are dominated by directed behavior. A future theory should integrate:

- state transitions;
- event causality;
- temporal order;
- compensation;
- resource flow;
- higher equivalence of representations.

Directed homotopy type theory, higher categories, and categorical systems theory are plausible sources. The result should keep identity paths reversible while allowing noninvertible business morphisms and higher cells between process transformations.

## 26.5 Uncertainty and probabilistic alignment

Real entity resolution is uncertain. HoTT alone supplies structure for identity once accepted, not a probability calculus for candidates. A combined system could use:

- probabilistic models for candidate generation;
- evidence logics for source reliability;
- dependent types for admissibility;
- human governance for approval;
- HoTT for the approved identity and coherence layer.

Research questions include how confidence propagates through composite candidate paths and how to prevent high-confidence local matches from creating low-quality global loops.

## 26.6 Standards evolution

Industrial standards change over decades. A formal standards repository should provide:

- versioned categorical and dependent signatures;
- machine-checkable mappings between editions;
- declared profiles and optional fragments;
- proofs of backward-compatible views;
- explicit losses in migrations;
- reference data provenance.

An enterprise alignment would then target an exact versioned module rather than an informal standard name.

## 26.7 Scaling proof and reconciliation

A plant may contain millions of records and billions of events. The formal theory should avoid constructing a proof term for every obvious foreign-key traversal when a shared theorem and compact certificate suffice.

Promising strategies include:

- theorem schemas for classes of rows;
- proof by verified query plans;
- compressed path certificates;
- incremental recomputation by dependency;
- database-native evaluation with a small external checker;
- Merkleized evidence and ontology packages;
- stratified reasoning, keeping most data at set level and lifting only disputed identity regions.

Performance evaluation must include theory-checking time, incremental update cost, explanation latency, and storage overhead.

## 26.8 Human factors

An ontology is governed by engineers, planners, operators, quality professionals, and auditors. Most will not write path algebra. The tool must render formal obligations as domain questions:

```text
The direct ERP-to-MES mapping selects M-91.
The approved route through PLM selects M-82.
No approved equivalence between M-91 and M-82 exists.
Choose one:
  refine scope
  approve a comparison
  reject a mapping
  retain an ambiguity
```

Diagrams, counterexamples, competency questions, and provenance are the user interface to higher mathematics.

## 26.9 Security and adversarial semantics

Semantic integration can be attacked. A malicious or erroneous alignment can grant unauthorized substitution, redirect traceability, or hide a nonconforming component inside a canonical class.

A secure ontology engine should support:

- signed theory packages;
- separation of proposer and approver roles;
- least-privilege visibility of evidence;
- replayable historical versions;
- proof-carrying canonical memberships;
- impact analysis before activation;
- policy checks on which kinds may be identified;
- independent kernel rechecking.

The higher path structure is useful only when governance of its constructors is strong.

## 26.10 Empirical evaluation

A research deployment should measure:

- number of identity-stratum errors discovered before implementation;
- number of noncommuting mapping triangles detected;
- number of unintended collapses prevented;
- time to explain a canonical membership;
- time to update after mapping revocation;
- percentage of APIs generated from competency questions and formal views;
- defect rate in schema migrations and adapters;
- usability for domain reviewers;
- runtime and storage overhead.

Compare against a conventional canonical-model or knowledge-graph project on the same bounded scope.

## 26.11 A capstone sequence

A twelve-to-fourteen week project can proceed as follows:

1. select one product family and three systems;
2. elicit competency questions and identity strata;
3. present local categorical schemas;
4. load finite instances and validate path equations;
5. define shared interfaces and detect nonfunctorial mappings;
6. add dependent identifiers, time, evidence, and quantities;
7. implement one proof-carrying trace query;
8. construct candidate alignment paths;
9. form a homotopy pushout in a cubical system or explicit model;
10. add one nontrivial 2-path coherence proof;
11. define a dependent family and test loop holonomy;
12. extract a set-truncated canonical API;
13. simulate revocation and theory migration;
14. evaluate findings with domain experts.

The capstone is successful even if the final production system remains conventional. The formal phase should change the types, APIs, constraints, or governance model in demonstrably useful ways.

## 26.12 Final synthesis

A traditional ERP integration asks:

```text
Which fields map to which fields?
```

A categorical ontology asks:

```text
Which typed paths and equations does the mapping preserve?
```

A dependent ontology asks:

```text
Under which values, states, times, dimensions, and evidence is the mapping admissible?
```

A homotopical ontology asks:

```text
Which approved witnesses generate identity,
how do multiple identity routes cohere,
what dependent meaning is transported,
and at which boundary may higher distinctions be forgotten?
```

That last set of questions is what HoTT contributes. It does not make ordinary ERP data intrinsically topological. It supplies a disciplined theory of equivalence, identification, path dependence, and controlled information loss—precisely the issues that dominate difficult ontology merges.

The practical objective is not a production database filled with higher paths. It is an architecture in which the flat production database is recognized as a deliberate truncation of a richer, checked theory, and in which every collapse of meaning has a name, a scope, a proof obligation, and an explanation.

\newpage

# Appendix A. Lean 4 Working Guide

This appendix collects the small amount of Lean needed to use the book as a laboratory. It is not a substitute for the Lean reference manual or *Theorem Proving in Lean 4* [R1, R2]. Its purpose is to keep the ontology model, rather than proof-assistant mechanics, in the foreground.

## A.1 Project shape

A minimal project can be organized as follows:

```text
ErpOntology/
  lakefile.toml
  lean-toolchain
  ErpOntology.lean
  ErpOntology/
    Basic.lean
    Category.lean
    Instance.lean
    Migration.lean
    Domain.lean
    Evidence.lean
    Trace.lean
    Extraction.lean
    Tests.lean
```

The root module imports the others:

```lean
import ErpOntology.Basic
import ErpOntology.Category
import ErpOntology.Instance
import ErpOntology.Migration
import ErpOntology.Domain
import ErpOntology.Evidence
import ErpOntology.Trace
import ErpOntology.Extraction
```

For the self-contained fragments in this book, the standard library is enough. Mathlib becomes useful when the project needs mature category theory, algebra, finite sets, orders, or tactics. A serious categorical implementation should reuse a maintained library rather than reproduce the pedagogical definitions below.

The code in the book is written in Lean 4 style and designed to make the mathematical structure visible. It is not presented as one frozen, version-pinned library. Imports, namespace names, and some elaboration details may require minor adjustment against a particular Lean release.

## A.2 Terms, propositions, and proofs

Lean follows the propositions-as-types discipline:

```lean
variable (P Q : Prop)

-- P → Q is both a function type and an implication.
def modusPonens (hp : P) (h : P → Q) : Q := h hp
```

A theorem is a definition whose result type is a proposition:

```lean
theorem and_comm (P Q : Prop) : P ∧ Q → Q ∧ P := by
  intro h
  exact ⟨h.right, h.left⟩
```

The tactic block constructs a term. Lean's kernel checks that term. In this book, that division motivates the architecture of an ontology proof engine: elaboration and search may be sophisticated, but a small checker should validate the resulting witness.

## A.3 Structures and indexed families

A conventional record:

```lean
structure PartRevision where
  number : String
  revision : String
  released : Bool
  deriving Repr, DecidableEq
```

An indexed family carries a distinction in its type:

```lean
inductive System
  | plm | erp | mes | eam | qms
  deriving Repr, DecidableEq

inductive Kind
  | productDefinition
  | productRevision
  | commercialItem
  | materialDefinition
  | lot
  | serialUnit
  | physicalAsset
  | functionalPosition
  deriving Repr, DecidableEq

structure Ref (s : System) (k : Kind) where
  localId : String
  deriving Repr, DecidableEq
```

The following types are distinct:

```lean
abbrev PlmRevision := Ref .plm .productRevision
abbrev ErpItem := Ref .erp .commercialItem
abbrev MesMaterial := Ref .mes .materialDefinition
abbrev SerialUnit := Ref .mes .serialUnit
abbrev Asset := Ref .eam .physicalAsset
abbrev Position := Ref .eam .functionalPosition
```

Therefore, a function requiring a serialized unit cannot accidentally receive a part revision merely because both use strings internally.

## A.4 Propositions versus evidence-rich types

A proposition is appropriate when only logical validity matters:

```lean
def Released (r : PartRevision) : Prop := r.released = true
```

A type is preferable when witnesses must retain operational content:

```lean
structure Evidence where
  source : String
  authority : String
  recordedAt : Nat
  note : String
  deriving Repr

structure ConformsTo (u : SerialUnit) (r : PlmRevision) where
  evidence : Evidence
  certificate : String
  deriving Repr
```

Lean's `Prop` is proof-irrelevant. Two proofs of the same proposition are not intended to remain distinguishable computational data. A source document, timestamp, approver, or confidence score therefore belongs in `Type`, not only in a proposition that will be erased.

A common pattern separates payload from logical law:

```lean
structure ApprovedConformance (u : SerialUnit) (r : PlmRevision) where
  evidence : Evidence
  approved : evidence.authority ≠ ""
```

## A.5 Equality and rewriting

Lean's ordinary equality is written `x = y`:

```lean
theorem congrArgExample
    {α β : Type}
    (f : α → β)
    {x y : α}
    (p : x = y) :
    f x = f y := by
  cases p
  rfl
```

`cases p` reduces the problem to reflexivity. In Part II this is useful for ordinary indexed programming. In Part III the object theory treats paths as potentially structured data. The distinction is essential: Lean's built-in equality is the metalanguage equality used to implement the experiment; it does not by itself give a native univalent HoTT universe.

## A.6 Dependent pairs

A dependent pair packages a value with data indexed by that value:

```lean
structure SomeRef where
  system : System
  kind : Kind
  ref : Ref system kind
```

The type of `ref` depends on the preceding fields. A query can similarly return an answer and its witness:

```lean
structure SupportedAnswer (α : Type) where
  answer : α
  evidence : Evidence
```

A logical dependent pair can be expressed with `Subtype` or `Exists`:

```lean
def ReleasedRevision := {r : PartRevision // Released r}
```

Use a structure when the witness is domain data with names, serialization needs, or multiple fields. Use `Subtype` when a value plus a proposition is the intended interface.

## A.7 Sum types and state machines

An explicit state index prevents illegal transitions:

```lean
inductive OrderState
  | draft | released | executing | complete | cancelled

structure ProductionOrder (s : OrderState) where
  orderNo : String
  product : ErpItem
  quantity : Nat

structure ReleaseAuthorization where
  approvedBy : String
  approvalId : String


def release
    (o : ProductionOrder .draft)
    (a : ReleaseAuthorization) :
    ProductionOrder .released :=
  { orderNo := o.orderNo
    product := o.product
    quantity := o.quantity }
```

There is no function branch for releasing a completed order because the input type forbids it. Runtime state still needs checking at an I/O boundary; after successful decoding, the typed core can rely on the stronger invariant.

## A.8 Universes

Lean stratifies types into universes:

```lean
#check Type       -- Type 1
#check Type 1     -- Type 2
```

A polymorphic structure can quantify over a universe:

```lean
universe u

structure EquivLike (A B : Type u) where
  toFun : A → B
  invFun : B → A
  leftInv : ∀ a, invFun (toFun a) = a
  rightInv : ∀ b, toFun (invFun b) = b
```

Universe levels matter in a HoTT engine because univalence concerns identity in a universe of types. A first prototype may use one or two explicit universes; a reusable checker needs universe polymorphism and constraints.

## A.9 Totality and partial industrial functions

A mathematical arrow is total. Industrial data is often partial. Encode the precondition, uncertainty, or failure explicitly:

```lean
def findRevision (partNo rev : String) : List PartRevision → Option PartRevision
  | [] => none
  | x :: xs =>
      if x.number = partNo && x.revision = rev then some x
      else findRevision partNo rev xs
```

For explainable failure:

```lean
inductive ResolveError
  | notFound
  | ambiguous (candidates : List String)
  | outsideEffectivity
  | insufficientEvidence
  deriving Repr

abbrev ResolveM (α : Type) := Except ResolveError α
```

Do not conceal partiality by inventing a default object. Doing so turns a missing fact into a false fact.

## A.10 Small proof patterns

### Constructor and projection

```lean
theorem pairSwap {P Q : Prop} : P ∧ Q → Q ∧ P := by
  intro h
  constructor
  · exact h.2
  · exact h.1
```

### Case analysis

```lean
theorem stateCases (s : OrderState) :
    s = .draft ∨ s = .released ∨ s = .executing ∨
    s = .complete ∨ s = .cancelled := by
  cases s <;> simp
```

### Equality substitution

```lean
theorem transportProperty
    {α : Type}
    (P : α → Prop)
    {x y : α}
    (p : x = y)
    (hx : P x) : P y := by
  simpa [p] using hx
```

### Induction over traces

```lean
inductive Link : String → String → Type
  | step (a b : String) : Link a b

inductive Chain : String → String → Type
  | refl (a : String) : Chain a a
  | cons {a b c : String} : Link a b → Chain b c → Chain a c


def Chain.length {a b : String} : Chain a b → Nat
  | .refl _ => 0
  | .cons _ rest => Nat.succ rest.length
```

The endpoints are part of the type. A malformed chain whose adjacent endpoints do not match cannot be constructed.

## A.11 Testing formal and executable layers

Use at least four test classes:

1. **example proofs** for central invariants;
2. **negative compilation tests** for illegal states or mismatched kinds;
3. **property-based tests** for executable transformations and round trips;
4. **golden tests** for extracted schemas, APIs, and diagnostics.

A theorem proves a universal claim within the formal model. It does not prove that a parser, database connector, or human-entered alignment has faithfully instantiated that model. Boundary tests remain necessary.

## A.12 Recommended discipline

Keep three layers separate:

```text
Raw input
  -- strings, nullable fields, external records

Validated domain values
  -- indexed IDs, dimensions, intervals, approved evidence

Proved constructions
  -- traces, coherent mappings, admissible migrations
```

Most production defects arise when raw input is permitted to masquerade as a validated or proved value.

# Appendix B. Consolidated Ontology Model Skeleton

This appendix combines representative definitions from the book into one coherent skeleton. It is deliberately smaller than an industrial implementation. Its role is to show how the categorical, dependent, and extraction layers fit together in ordinary Lean 4.

## B.1 Systems, kinds, and references

```lean
namespace ErpOntology

inductive System
  | plm | erp | mes | eam | qms | warehouse | supplier
  deriving Repr, DecidableEq

inductive Kind
  | productDefinition
  | productRevision
  | commercialItem
  | materialDefinition
  | materialLot
  | serialUnit
  | assetRecord
  | physicalAsset
  | functionalPosition
  | processDefinition
  | productionOrder
  | workExecution
  | inspectionResult
  deriving Repr, DecidableEq

structure Ref (s : System) (k : Kind) where
  localId : String
  deriving Repr, DecidableEq

structure SomeRef where
  system : System
  kind : Kind
  ref : Ref system kind
  deriving Repr
```

The distinction between `assetRecord` and `physicalAsset` is intentional. A row in an EAM system is an information object; the maintained pump is a physical object. They may stand in a representation relation, but they are not definitionally the same.

## B.2 Time

Use a real timestamp library in production. Natural numbers suffice to expose the type structure:

```lean
abbrev Instant := Nat

structure Interval where
  start : Instant
  finish : Option Instant
  valid : match finish with
    | none => True
    | some t => start ≤ t


def Interval.contains (i : Interval) (t : Instant) : Prop :=
  i.start ≤ t ∧ match i.finish with
    | none => True
    | some f => t < f
```

Half-open intervals avoid double occupancy at an exact replacement time:

```text
old installation: [100, 200)
new installation: [200, ∞)
```

## B.3 Evidence and claim status

```lean
inductive ClaimStatus
  | proposed | approved | rejected | superseded | revoked
  deriving Repr, DecidableEq

structure Evidence where
  sourceSystem : System
  sourceId : String
  authority : String
  recordedAt : Instant
  method : String
  note : String
  deriving Repr

structure ClaimMeta where
  validDuring : Interval
  status : ClaimStatus
  evidence : List Evidence
  deriving Repr
```

A path-like alignment used for canonicalization should normally require approved status and nonempty evidence:

```lean
def ClaimMeta.Admissible (m : ClaimMeta) : Prop :=
  m.status = .approved ∧ m.evidence ≠ []
```

## B.4 Typed industrial relations

```lean
abbrev PlmRevision := Ref .plm .productRevision
abbrev ErpItem := Ref .erp .commercialItem
abbrev MesMaterial := Ref .mes .materialDefinition
abbrev Lot := Ref .mes .materialLot
abbrev Unit := Ref .mes .serialUnit
abbrev AssetRecord := Ref .eam .assetRecord
abbrev PhysicalAsset := Ref .eam .physicalAsset
abbrev Position := Ref .eam .functionalPosition
abbrev Work := Ref .mes .workExecution
abbrev Inspection := Ref .qms .inspectionResult

structure ItemRealizesRevision (i : ErpItem) (r : PlmRevision) where
  meta : ClaimMeta
  admissible : meta.Admissible

structure MaterialRealizesItem (m : MesMaterial) (i : ErpItem) where
  meta : ClaimMeta
  admissible : meta.Admissible

structure UnitConformsTo (u : Unit) (r : PlmRevision) where
  meta : ClaimMeta
  certificate : String
  admissible : meta.Admissible

structure RecordRepresentsAsset (rec : AssetRecord) (a : PhysicalAsset) where
  meta : ClaimMeta
  admissible : meta.Admissible

structure UnitIsAsset (u : Unit) (a : PhysicalAsset) where
  meta : ClaimMeta
  admissible : meta.Admissible

structure InstalledAt (a : PhysicalAsset) (p : Position) where
  interval : Interval
  meta : ClaimMeta
  admissible : meta.Admissible
```

The `UnitIsAsset` name should not be interpreted as a global metaphysical identity. It is a typed, governed assertion that a serialized production unit and a physical asset designation concern the same physical continuant under the organization's identity policy.

## B.5 Dimensions and quantities

```lean
inductive BaseDimension
  | mass | length | time | temperature | amount
  deriving Repr, DecidableEq

structure Dimension where
  mass : Int := 0
  length : Int := 0
  time : Int := 0
  temperature : Int := 0
  amount : Int := 0
  deriving Repr, DecidableEq

structure Quantity (d : Dimension) where
  magnitude : Rat
  unitSymbol : String
  deriving Repr


def Quantity.add {d : Dimension} (x y : Quantity d) : Quantity d :=
  { magnitude := x.magnitude + y.magnitude
    unitSymbol := x.unitSymbol }
```

A complete unit system also records scale and offset transformations, prevents addition before normalization, and treats affine temperatures separately. The invariant shown here is still valuable: unlike dimensions cannot be added accidentally.

## B.6 Trace steps and chains

```lean
inductive TraceNode
  | revision (x : PlmRevision)
  | item (x : ErpItem)
  | material (x : MesMaterial)
  | lot (x : Lot)
  | unit (x : Unit)
  | asset (x : PhysicalAsset)
  | position (x : Position)
  | inspection (x : Inspection)
  deriving Repr

inductive TraceStep : TraceNode → TraceNode → Type
  | revisionToItem {r i} : ItemRealizesRevision i r →
      TraceStep (.revision r) (.item i)
  | itemToMaterial {i m} : MaterialRealizesItem m i →
      TraceStep (.item i) (.material m)
  | unitToRevision {u r} : UnitConformsTo u r →
      TraceStep (.unit u) (.revision r)
  | unitToAsset {u a} : UnitIsAsset u a →
      TraceStep (.unit u) (.asset a)
  | assetToPosition {a p} : InstalledAt a p →
      TraceStep (.asset a) (.position p)

inductive Trace : TraceNode → TraceNode → Type
  | refl (x) : Trace x x
  | cons {x y z} : TraceStep x y → Trace y z → Trace x z
```

A query can return an existentially quantified start node and a trace to a requested endpoint:

```lean
structure SomeTraceTo (target : TraceNode) where
  source : TraceNode
  trace : Trace source target
```

The path itself is the explanation. Projecting only `source` or `target` gives a conventional result; retaining `trace` supports audit and diagnostics.

## B.7 A small categorical schema

```lean
universe u v

structure SmallCategory where
  Obj : Type u
  Hom : Obj → Obj → Type v
  id : {X : Obj} → Hom X X
  comp : {X Y Z : Obj} → Hom X Y → Hom Y Z → Hom X Z
  id_comp : ∀ {X Y} (f : Hom X Y), comp id f = f
  comp_id : ∀ {X Y} (f : Hom X Y), comp f id = f
  assoc : ∀ {W X Y Z}
    (f : Hom W X) (g : Hom X Y) (h : Hom Y Z),
    comp (comp f g) h = comp f (comp g h)
```

A schema-specific presentation is often easier than constructing a quotient of generated paths. For example:

```lean
inductive CoreObj
  | revision | item | material | unit | asset | position
  deriving Repr, DecidableEq

inductive CoreHom : CoreObj → CoreObj → Type
  | id (X) : CoreHom X X
  | itemRevision : CoreHom .item .revision
  | materialItem : CoreHom .material .item
  | unitRevision : CoreHom .unit .revision
  | unitAsset : CoreHom .unit .asset
  | assetPosition : CoreHom .asset .position
  | comp {X Y Z} : CoreHom X Y → CoreHom Y Z → CoreHom X Z
```

A rigorous free-category implementation quotients paths by associativity and identity equations or uses normalized paths. In a small engineering prototype, one can instead give a semantic interpretation and prove the required path equations there.

## B.8 Instances

An instance assigns a carrier type to each schema object and a function to each arrow:

```lean
structure Instance (C : SmallCategory) where
  obj : C.Obj → Type
  map : {X Y : C.Obj} → C.Hom X Y → obj X → obj Y
  map_id : ∀ {X} (x : obj X), map C.id x = x
  map_comp : ∀ {X Y Z} (f : C.Hom X Y) (g : C.Hom Y Z) (x : obj X),
    map (C.comp f g) x = map g (map f x)
```

The equations state that a stored or computed instance respects the ontology's compositional meaning. A table collection with foreign keys is not yet an instance if two paths declared equivalent produce different answers.

## B.9 Alignment witnesses

```lean
inductive RelationKind
  | sameEntity
  | equivalentRepresentation
  | realizes
  | conformsTo
  | represents
  | installedAt
  | supersedes
  | potentialMatch
  deriving Repr, DecidableEq

structure Alignment where
  left : SomeRef
  right : SomeRef
  relation : RelationKind
  meta : ClaimMeta
  deriving Repr
```

Only selected relation kinds should generate identity paths in a HoTT merge. `realizes`, `conformsTo`, and `installedAt` remain directed domain relations. `potentialMatch` generates no identity until promoted under an approved policy.

## B.10 Coherence certificates

Two integration routes can be represented as explicit transformations:

```lean
structure Mapping (A B : Type) where
  run : A → Except String B
  name : String

structure CoherentTriangle
    {A B C : Type}
    (ab : Mapping A B)
    (bc : Mapping B C)
    (ac : Mapping A C) where
  onSuccess : ∀ a b c,
    ab.run a = .ok b →
    bc.run b = .ok c →
    ac.run a = .ok c
```

For mappings that are partial or multivalued, the correct law may compare relations, finite sets of candidates, or evidence-bearing results rather than pure functions. The type of coherence must match the operational semantics.

## B.11 Extraction boundary

A flat API view intentionally discards higher proof detail but retains a certificate reference:

```lean
structure CanonicalEntity where
  canonicalId : String
  kind : Kind
  displayName : String
  deriving Repr

structure MembershipCertificate where
  local : SomeRef
  canonical : CanonicalEntity
  theoryVersion : String
  proofDigest : String
  validDuring : Interval
  deriving Repr
```

The extraction process should satisfy at least:

```text
soundness:
  every emitted membership has a valid proof in the source theory

stability:
  unchanged source theory and data produce the same canonical result

versioning:
  a result names the theory version under which it was derived

explainability:
  the proof digest resolves to a retained witness graph
```

## B.12 Namespace closure

```lean
end ErpOntology
```

This skeleton is sufficient for an ordinary Lean prototype. It does not implement univalence or higher inductive types internally. Those belong either in an explicit object theory, as discussed in Chapter 25, or in a cubical proof assistant.

# Appendix C. Ontology Design Workshop

Formalization succeeds only when it is attached to disciplined domain elicitation. This appendix gives a workshop method for turning industrial disagreement into an explicit theory.

## C.1 Scope one thread, not one enterprise

Choose a bounded trace with visible operational value. Good initial scopes include:

- engineering revision to plant item to MES material definition;
- production order to actual material consumption to serialized output;
- serialized output to installed asset to functional position;
- inspection plan to observation to release decision;
- approved substitute to effectivity rule to execution choice;
- supplier lot to internal lot to consumed unit.

Avoid “model the whole company.” Ontologies expand through composition after local identity rules are understood.

## C.2 Assemble contrasting authorities

A useful group includes at least:

- product engineering or PLM ownership;
- production planning or ERP ownership;
- manufacturing execution;
- quality;
- maintenance or asset management;
- integration or data architecture;
- one person responsible for audit, security, or regulated records.

The purpose is not consensus by terminology. It is to expose where different roles apply different identity criteria.

## C.3 Begin with competency questions

A competency question is a question the integrated theory must answer. It is more informative than a list of entities because it reveals required relations, time semantics, evidence, and failure behavior.

### Product and revision

```text
Which approved engineering revision governs this plant item at time t?
Which effectivity rule made the revision applicable?
Are two revision records equivalent representations or successive revisions?
Which downstream objects become suspect if the approval is revoked?
```

### Production and traceability

```text
Which material lots were actually consumed in this serialized unit?
Which planned requirement did each actual satisfy?
Which substitutions were used, and under whose approval?
Can every trace step name its source evidence?
```

### Asset and maintenance

```text
Which physical device occupied functional position P at time t?
Which asset record represented that device during the interval?
Did replacement preserve the functional position but change the serial unit?
Does the current as-maintained configuration conform to an approved baseline?
```

### Quality

```text
Which measurement supports the release decision?
What unit, method, calibration state, and specification limit applied?
Was the inspection about a lot, a unit, a process execution, or a position?
What changed if the specification revision changed?
```

### Integration governance

```text
Why are these two local records canonically merged?
Which route produced the merge?
Do all approved routes agree?
What dependent data changes after transport around a loop?
Which collapse is set-truncated for the production API?
```

## C.4 Identity-stratum interview

For every noun, ask the following questions separately:

1. Is it a **kind**, **definition**, **revision**, **plan**, **event**, **physical continuant**, **role**, **position**, **record**, or **observation**?
2. What makes two occurrences the same?
3. What can change while identity is preserved?
4. What change creates a new object?
5. Is identity global or scoped by plant, organization, supplier, or interval?
6. Which authority may assert or revoke it?
7. Is the relation symmetric and invertible?
8. Is it merely a directed transformation or realization?
9. Does the assertion carry provenance or confidence?
10. Can distinct valid assertions coexist?

Record the answer as an identity policy, not merely a note.

## C.5 Draw local categories first

Each system owner draws a local diagram without trying to adopt a global vocabulary. For example:

```text
PLM

AssemblyOccurrence ─childRevision→ PartRevision ─revisionOf→ PartDefinition
        │
        └─parentRevision→ PartRevision

ERP

PlantItem ─itemOf→ Item
   │
   ├─plannedBy→ MRPPolicy
   └─procuredAs→ SupplierItem

MES

MaterialActual ─lot→ MaterialLot ─definition→ MaterialDefinition
       │
       └─execution→ WorkExecution ─jobOrder→ JobOrder
```

Then state equations. If `MaterialActual → MaterialLot → MaterialDefinition` and `MaterialActual → Requirement → MaterialDefinition` are intended to agree, write that commuting condition explicitly.

## C.6 Mark partiality and multiplicity

Do not draw a single arrow when the operational relation is:

- optional;
- one-to-many;
- many-to-many;
- time-dependent;
- confidence-weighted;
- subject to approval;
- computed from a rule;
- only locally unique.

Choose a representation that preserves the semantics. A relation may be modeled as a span, a table object, a finite-set-valued mapping, or an evidence-indexed family rather than as a total function.

## C.7 Build the correspondence ledger

Use a ledger with at least these columns:

| Field | Meaning |
|---|---|
| left concept | source-system object or type |
| right concept | target-system object or type |
| correspondence kind | identity, equivalence, realization, classification, representation, and so on |
| scope | plant, organization, product family, time interval |
| cardinality | functional, injective, surjective, many-to-many |
| transformation | executable conversion, when any |
| inverse | executable or logical inverse, when any |
| evidence | documents, rules, approvals, measurements |
| coherence routes | other routes that must agree |
| collapse policy | whether it may generate canonical identity |
| owner | authority responsible for maintenance |
| status | proposed, approved, superseded, revoked |

This ledger is the precursor to both a formal alignment type and an operational governance table.

## C.8 Classify merge constructors

For every candidate cross-system link, choose one of four outcomes:

```text
A. identity-generating path
   The organization intentionally treats the endpoints as the same
   within a declared scope.

B. equivalence without object identity
   Representations are reversibly interchangeable for a stated family
   of observations, but remain distinct records or models.

C. directed semantic relation
   One object realizes, conforms to, represents, classifies, succeeds,
   or occupies another.

D. uncertain candidate
   A match is proposed but not yet admissible for canonicalization.
```

Most difficult failures arise from promoting C or D directly to A.

## C.9 Identify coherence diagrams

Search for triangles, squares, and loops:

```text
ERP Item ─────────────→ MES Material
   │                         ▲
   │                         │
   ▼                         │
PLM Revision ────────────────┘
```

Ask:

- Must the two routes give literally equal results?
- Must they give equivalent results?
- Is disagreement allowed but required to produce a reconciliation object?
- What time and theory version must be held fixed?
- What evidence approves the 2-cell witnessing agreement?

A coherence obligation should become a theorem, a validation query, or a controlled exception—not an informal expectation.

## C.10 Test loops with dependent families

Choose important data families over the merged ontology:

```text
ApprovedSpecification(x)
UnitConvention(x)
SerializationCodec(x)
AccessPolicy(x)
ApplicableWorkInstruction(x)
EffectivityContext(x)
```

Transport a representative value around each approved loop. A nontrivial result is semantic holonomy. It may reveal a hidden conversion, policy change, or loss of information.

The key question is not only whether a loop returns to the same canonical entity. It is whether all meaning that depends on the entity returns coherently.

## C.11 Decide truncation boundaries

For each consumer, choose the least destructive output level:

- **untruncated witness space** for theory maintenance and research;
- **set-level canonical memberships** for master-data APIs;
- **proposition-level existence** for authorization or validation checks;
- **mere count or Boolean** for dashboards and alerts.

Document each boundary. A consumer that needs provenance must not receive only a Boolean. A transaction processor may not need the entire higher path space.

## C.12 Extract implementation artifacts

The workshop should end with concrete outputs:

1. typed domain vocabulary;
2. local categorical schemas and equations;
3. correspondence ledger;
4. identity and truncation policies;
5. coherence obligations;
6. API competency questions;
7. database constraints and validation rules;
8. proof-carrying trace requirements;
9. versioning and revocation behavior;
10. a bounded formal prototype.

## C.13 Review gates

A useful gate sequence is:

```text
Gate 1 — denotation
Every central term has an identity criterion and stratum.

Gate 2 — local composition
Each local ontology has typed arrows and required equations.

Gate 3 — mapping
Every mapping states partiality, multiplicity, time, and evidence.

Gate 4 — coherence
Parallel routes have explicit agreement or conflict semantics.

Gate 5 — collapse
Every canonicalization names its path-constructor policy.

Gate 6 — extraction
Every production view identifies the information it forgets.

Gate 7 — change
Revocation and theory-version migration have an operational plan.
```

# Appendix D. Exercises and Selected Solutions

The exercises are grouped by part. Selected solutions emphasize modeling decisions rather than tactic syntax.

## D.1 Part I exercises

### Exercise 1: Separate the pump meanings

Given the following fields in a legacy table, classify each as a likely definition, revision, physical instance, role, position, record, event, or observation:

```text
part_no
revision
serial_no
asset_no
functional_location
work_center
installation_date
vibration_rms
inspection_id
```

Explain which pairs must not be identified without additional evidence.

**Selected solution.** `part_no` normally denotes a definition or family; `revision` refines it to a controlled version; `serial_no` denotes a physical unit under a serialization policy; `asset_no` denotes an asset-management record and perhaps, by policy, a physical asset; `functional_location` denotes a persistent position; `work_center` denotes a logical production resource or organizational capability; `installation_date` contributes to an installation event or interval; `vibration_rms` is an observation value; `inspection_id` denotes an information record or execution. `serial_no`, `asset_no`, and `functional_location` are related but not identical. `part_no` and `revision` are not physical units. `vibration_rms` is not the machine whose condition it reports.

### Exercise 2: Present a local schema

Model the following statements categorically:

- each material lot has a material definition;
- each material actual references a lot;
- each material actual satisfies a material requirement;
- each material requirement asks for a material definition;
- the definition reached through the lot must agree with the required definition unless a substitution is recorded.

**Selected solution.** Use objects `MaterialActual`, `MaterialLot`, `MaterialRequirement`, `MaterialDefinition`, and optionally `SubstitutionApproval`. Add arrows:

```text
actualLot : MaterialActual → MaterialLot
lotDefinition : MaterialLot → MaterialDefinition
actualRequirement : MaterialActual → MaterialRequirement
requiredDefinition : MaterialRequirement → MaterialDefinition
```

For the no-substitution subcategory, impose:

```text
lotDefinition ∘ actualLot
=
requiredDefinition ∘ actualRequirement
```

When substitutions are possible, do not keep the same unconditional equation. Introduce an accepted-definition relation or an approval object that mediates the two definitions. The equation may then say that both routes reach the same approved requirement-satisfaction witness, not that the raw definitions are identical.

### Exercise 3: Diagnose a nonfunctorial mapping

A source schema states that every serialized unit reaches its product definition through both its build revision and its catalog item. A target mapping sends build revision to a PLM revision but drops the catalog item relation. Explain why a purported schema functor may fail.

**Selected solution.** A functor must preserve arrows, composition, identities, and equations. If one source path has no well-typed target image or if two equal source paths map to unequal target paths, the mapping is not a functor. “Dropping” an arrow can be modeled only by mapping into a schema with an appropriate terminal or optional construction, by restricting the source, or by changing the mapping notion. Silently omitting it destroys the stated semantics.

### Exercise 4: Choose a merge interface

Construct a shared interface `K` for PLM and ERP containing no more than six objects. Explain why a small interface is preferable to a full universal model.

**Selected solution.** One choice is:

```text
ProductDefinition
ProductRevision
CommercialItem
Organization
TimeInterval
Quantity
```

with arrows such as `revisionOf`, `ownedBy`, and `effectiveDuring`. The interface should contain only concepts whose correspondences are understood and governed. A small interface localizes identification commitments, makes the pushout auditable, and avoids forcing unrelated local concepts into premature global equality.

### Exercise 5: Data migration direction

For a functor `F : C → D`, explain in operational language the difference between precomposition and its left and right adjoints.

**Selected solution.** Precomposition pulls a `D`-instance back to `C` by reading it through the mapping. The left adjoint performs a least or generative extension into `D`; it is associated with union-like construction and may create target facts needed by the mapping. The right adjoint performs a compatible or constraint-oriented extension, associated with joins and universal matching. Exact database behavior depends on the categorical data model and finiteness conditions [R4, R8, R9].

## D.2 Part II exercises

### Exercise 6: Index identifiers

Replace this API:

```typescript
function install(assetId: string, positionId: string): void
```

with a typed core signature that distinguishes systems, kinds, and time.

**Selected solution.** One possible core is:

```lean
def install
    (asset : Ref .eam .physicalAsset)
    (position : Ref .eam .functionalPosition)
    (during : Interval)
    (approval : InstallationApproval asset position during) :
    InstalledAt asset position
```

The external API still decodes strings. It must validate that they resolve to the required kinds, that the interval is valid, and that the approval applies before invoking the core.

### Exercise 7: Preserve evidence

Why is `SameEntity x y : Prop` insufficient for an auditable merge? Give a richer type.

**Selected solution.** The proposition can prove admissibility, but proof irrelevance discards distinctions among witnesses. Audit requires authority, source, validity interval, rule version, and status. A richer structure is:

```lean
structure SameEntityClaim (x y : SomeRef) where
  meta : ClaimMeta
  policy : String
  approved : meta.Admissible
```

The logical proposition “these may be canonically identified” can then be derived from an approved claim while the operational payload remains available.

### Exercise 8: Temporal non-overlap

State a property ensuring that one functional position has at most one installed physical asset at any instant.

**Selected solution.** For all assets `a₁`, `a₂`, position `p`, installations `i₁`, `i₂`, and instant `t`, if both intervals contain `t`, then `a₁ = a₂` under the physical-asset identity policy. In a database, this may become a temporal exclusion constraint. In a proof model, it is a theorem about the installation relation plus the interval algebra. The property may need an explicit exception for redundant or composite positions.

### Exercise 9: Dimension-safe quality result

Model a measurement that retains characteristic, value, unit dimension, method, and calibration evidence.

**Selected solution.** A simplified dependent structure is:

```lean
structure Characteristic where
  name : String
  dimension : Dimension

structure Measurement (c : Characteristic) where
  value : Quantity c.dimension
  method : String
  calibrationEvidence : Evidence
  measuredAt : Instant
```

A specification limit for `c` has the same indexed dimension, preventing comparison of pressure with temperature.

### Exercise 10: Proof-carrying trace

Design a return type for “Which revision governed this unit?” that can represent ambiguity.

**Selected solution.** Do not return one revision unconditionally. Use:

```lean
inductive Resolution (u : Unit)
  | none (reason : ResolveError)
  | unique (r : PlmRevision) (trace : Trace (.unit u) (.revision r))
  | ambiguous (candidates : List (Sigma fun r =>
      Trace (.unit u) (.revision r)))
```

A production API may serialize candidate revisions and evidence references. The type prevents ambiguity from being silently collapsed to the first row.

## D.3 Part III exercises

### Exercise 11: Classify path constructors

For each relation below, decide whether it should normally generate an identity path, an equivalence, a directed relation, or no approved relation:

```text
ERP item realizes PLM revision
asset record represents physical asset
two losslessly convertible unit encodings
serial unit occupies functional position
probabilistic duplicate-customer match
```

**Selected solution.** `realizes`, `represents`, and `occupies` are normally directed relations, not identity. Two losslessly convertible encodings may support an equivalence and, in a univalent universe of representations, a path between their types. A probabilistic match remains a candidate with evidence; it should generate no identity until a policy and authority promote it. A specific organization may adopt a scoped identity policy between a serialized unit and its physical-asset designation, but that is an explicit constructor, not a consequence of the `represents` relation alone.

### Exercise 12: Homotopy pushout presentation

Let `K` contain shared product definitions. Let `P` contain PLM revisions and `E` contain ERP items. Write the generators of a homotopy pushout merge.

**Selected solution.** The higher inductive presentation has point constructors:

```text
inP : P → Merge
inE : E → Merge
```

and, for each `k : K`, a path constructor:

```text
glue : inP (f k) = inE (g k)
```

where `f : K → P` and `g : K → E`. The elimination principle says that a dependent construction over `Merge` is determined by compatible constructions over `P` and `E` together with coherence over every `glue k`.

### Exercise 13: A coherence square

Suppose ERP-to-MES has a direct alignment, while ERP-to-PLM-to-MES gives a composite alignment. State the required 2-path.

**Selected solution.** For each applicable item `i`, let:

```text
p_direct : inERP i = inMES (em i)
p_via    : inERP i = inMES (pm (ep i))
```

After establishing that the two MES endpoints coincide or are appropriately identified, require:

```text
coh i : p_direct = p_via
```

The precise dependent endpoints matter. If the routes end at merely equivalent but not definitionally equal nodes, the statement must include the endpoint path and use path whiskering or a square rather than a homogeneous equality of paths.

### Exercise 14: Detect holonomy

Give an example of a family whose transport around an ontology loop may be nontrivial.

**Selected solution.** Let `UnitConvention(x)` assign the approved display and conversion convention at entity `x`. A loop from supplier representation to ERP item to MES material to canonical product and back may convert kilograms to pounds and then incorrectly return a rounded kilogram value. The base entity may return to itself while the dependent value does not. That nontrivial transport is semantic holonomy and indicates that the loop's coherence proof is missing, false, or intentionally carries transformation content.

### Exercise 15: Choose a truncation level

For each consumer, choose an output level: ontology maintainer, master-data lookup API, authorization check, trace audit report.

**Selected solution.** The ontology maintainer needs the untruncated witness structure. A master-data lookup API normally needs set-level canonical entities plus certificate references. An authorization check may need only a proposition or Boolean after proof checking, though the decision log should retain evidence. A trace audit report needs explicit paths and evidence rather than mere existence.

### Exercise 16: Revocation

An approved glue path is revoked after discovering an incorrect mapping. Explain why deleting a row from the canonical table is not a sufficient semantics.

**Selected solution.** The path may have induced canonical memberships, transported attributes, generated API views, discharged coherence obligations, and supported historical decisions. Revocation changes the theory. A correct operation versions the constructor set, recomputes affected colimits or equivalence classes, invalidates dependent derivations, preserves the old theory for historical replay, and emits migration or contradiction diagnostics. The canonical table is only one truncation of that process.

## D.4 Open-ended projects

1. Formalize a small ISA-95-inspired material model as a category and a Lean instance validator.
2. Define a dependent type for revision effectivity over plant, serial range, and time.
3. Build a proof-carrying genealogy query over a finite event set.
4. Model two routing representations and prove a scoped equivalence.
5. Implement a finite approximation to a homotopy pushout that retains all alignment witnesses as a graph before set truncation.
6. Detect nontrivial loop transport for units, access policies, or specifications.
7. Compare a conventional canonical model with a witness-preserving model on one real integration defect class.

# Appendix E. Mathematical and Industrial Glossary

**Alignment.** A governed assertion relating concepts or instances from different local ontologies. It may express identity, equivalence, realization, representation, classification, or another relation. Only selected alignments generate identity paths.

**As-built configuration.** The components, lots, serial units, software, and parameters actually used to produce a unit, together with their provenance.

**As-maintained configuration.** The configuration believed to be physically present after installation, replacement, repair, or upgrade activity.

**Canonical entity.** A set-level operational representative produced by a declared collapse policy. It is not assumed to be the fundamental ontology object.

**Category.** A collection of objects and typed arrows with identities and associative composition. In this book, categories present local ontologies and schemas.

**Coherence.** Evidence that multiple compositions or identification routes agree in the required sense. In HoTT, coherence is represented by higher paths.

**Colimit.** A universal construction that combines a diagram of objects. Pushouts are a basic colimit used to merge schemas along a shared interface.

**Commuting diagram.** A diagram in which parallel composed paths are equal. It records a semantic consistency law.

**Competency question.** A domain question that an ontology and its implementation must be able to answer. It drives scope and exposes required semantics.

**Configuration baseline.** An approved set of revisioned items and constraints against which an actual or maintained configuration is compared.

**Context.** In type theory, an ordered collection of typed assumptions. In industrial semantics, it also denotes plant, organization, time, or configuration scope; the two meanings should be distinguished by notation.

**Dependent family.** A type `P x` whose form depends on a value `x`. Examples include specifications by product revision and unit policies by material definition.

**Dependent pair.** A pair `(x, p)` in which the type of `p` depends on `x`. It packages an answer with indexed evidence.

**Effectivity.** Conditions under which a revision, substitute, configuration, or rule applies, commonly involving time, plant, lot, serial range, or order.

**Entity resolution.** The process of determining whether records concern the same underlying entity. In this book it produces evidence-bearing candidates and approved path constructors rather than an unexplained Boolean.

**Equivalence.** A reversible structure-preserving correspondence. In HoTT, univalence relates equivalence of types to identity of types.

**Evidence.** Operational data supporting a claim: authority, source, document, method, timestamp, confidence, rule version, or certificate.

**Fiber.** For a mapping `f : A → B`, the type or set of inputs mapping to a given `b : B`. Fibers expose multiplicity and ambiguity in cross-system mappings.

**Functor.** A mapping between categories that preserves objects, arrows, identities, composition, and equations. It is the basic notion of semantics-preserving schema mapping.

**Functional position.** A persistent role or location in a plant structure that may be occupied by different physical assets over time.

**Higher inductive type.** A type generated by point constructors and path or higher-path constructors. Homotopy pushouts and truncations can be presented this way.

**Holonomy.** Nontrivial transport of dependent data around a loop. In ontology integration it reveals that a closed identity route changes units, policies, specifications, or other dependent meaning.

**Homotopy pushout.** A pushout that retains the specified gluing witnesses as paths rather than immediately collapsing them to proof-irrelevant equality.

**Identity criterion.** The rule determining when two presentations count as the same object and which changes preserve identity.

**Identity path.** In HoTT, an inhabitant of an identity type. In this framework, an approved merge witness may generate such a path in the integrated ontology.

**Identity stratum.** A level such as definition, revision, plan, event, physical continuant, role, position, observation, or record. Confusing strata is a primary ontology defect.

**Instance.** A set-valued functor assigning actual data to a categorical schema while respecting its equations.

**Logical equipment.** A production resource or role used in planning and execution. It may remain stable while its physical realization changes.

**Mere proposition.** A type with at most one inhabitant up to equality. It records that a fact holds without retaining multiple distinguishable ways in which it holds.

**Natural transformation.** A coherent mapping between functors. It can represent a transformation between database instances or between ontology mappings.

**Ontology.** Here, a typed and governed theory of entities, relations, identity, composition, evidence, time, and coherence—not only a class hierarchy.

**Olog.** An ontology log: a category whose objects are types and whose arrows are meaningful aspects, expressed in controlled natural language [R5].

**Path induction.** The eliminator for identity types: to prove a property of all paths, it suffices to prove the reflexive case under the appropriate motive.

**Physical asset.** A physical continuant managed for maintenance, reliability, or lifecycle purposes. It must be distinguished from its asset record and functional position.

**Proof-carrying query.** A query returning an answer together with a typed witness explaining why the answer follows from approved facts and rules.

**Provenance.** Information about the origin, derivation, authority, and history of a fact or transformation.

**Pushout.** A colimit that glues two objects along a shared interface. Ordinary pushouts are useful for schema construction; homotopy pushouts retain path structure.

**Realization.** A directed relation in which one object implements, instantiates, or operationalizes another, such as a plant item realizing an engineering design. It is not ordinarily identity.

**Record.** An information-system representation. A record is not automatically identical to the physical or conceptual object it describes.

**Refinement type.** A type restricted by a property, such as an interval with ordered endpoints or a released revision.

**Representation independence.** The property that downstream constructions depend on the meaning of a representation, not accidental encoding choices. Univalence supplies a foundational account for equivalent types.

**Revision.** A controlled version of a definition. Revisions may share a definition while differing in effectivity, approval, or configuration content.

**Schema.** A formal organization of entity types, relationships, and equations. In categorical databases it is modeled as a category.

**Semantic holonomy.** See *holonomy*.

**Set truncation.** A construction that turns a type into a set-level type by identifying all parallel higher paths while retaining points and ordinary equality classes. It is a controlled boundary from a higher theory to conventional data identity.

**Span.** A diagram `A ← R → B` representing a relation through its witnesses. Spans are useful when a cross-system relation is not functional.

**Structured identity principle.** The idea that equality of structured objects corresponds to an appropriate notion of structure-preserving equivalence, under univalence.

**Theory version.** An immutable version of ontology declarations, alignment constructors, coherence proofs, and extraction policies used to derive operational views.

**Traceability.** The ability to reconstruct relevant material, process, equipment, quality, and transformation history through evidence-bearing paths.

**Transport.** Moving a value of a dependent family `P x` along a path `x = y` to obtain a value of `P y`.

**Truncation boundary.** An architectural point at which higher witness information is deliberately forgotten to meet an operational interface.

**Univalence.** The principle that equivalences between types correspond to identities between those types. In cubical type theory, univalence can have computational behavior [R6, R11].

**Witness graph.** The retained graph of local entities, alignment claims, provenance, and coherence evidence from which canonical views are derived.

# Appendix F. Bibliography, Standards, and Version Notes

## F.1 Foundational sources

**[R1]** Lean Project. *The Lean Language Reference*. Current online reference, consulted August 5, 2026. <https://lean-lang.org/doc/reference/latest/>

**[R2]** Jeremy Avigad, Leonardo de Moura, Soonho Kong, Sebastian Ullrich, and contributors. *Theorem Proving in Lean 4*. Current online edition, consulted August 5, 2026. <https://lean-lang.org/theorem_proving_in_lean4/>

**[R3]** Leonardo de Moura and Sebastian Ullrich. “The Lean 4 Theorem Prover and Programming Language.” In *Automated Deduction—CADE 28*, Lecture Notes in Computer Science 12699, 625–635. Springer, 2021. DOI: 10.1007/978-3-030-79876-5_37.

**[R4]** David I. Spivak. “Functorial Data Migration.” *Information and Computation* 217 (2012): 31–51. Preprint: arXiv:1009.1166. <https://arxiv.org/abs/1009.1166>

**[R5]** David I. Spivak and Robert E. Kent. “Ologs: A Categorical Framework for Knowledge Representation.” *PLOS ONE* 7, no. 1 (2012): e24274. DOI: 10.1371/journal.pone.0024274.

**[R6]** The Univalent Foundations Program. *Homotopy Type Theory: Univalent Foundations of Mathematics*. Institute for Advanced Study, 2013. <https://homotopytypetheory.org/book/>

**[R7]** Floris van Doorn, Jakob von Raumer, and Ulrik Buchholtz. “Homotopy Type Theory in Lean.” In *Interactive Theorem Proving 2017*, Lecture Notes in Computer Science 10499, 479–495. Springer, 2017. DOI: 10.1007/978-3-319-66107-0_30. Preprint: arXiv:1704.06781.

**[R8]** Ryan Wisnesky, David I. Spivak, Patrick Schultz, and Eswaran Subrahmanian. “Functorial Data Migration: From Theory to Practice.” 2015. arXiv:1502.05947. <https://arxiv.org/abs/1502.05947>

**[R9]** Patrick Schultz, David I. Spivak, Christina Vasilakopoulou, and Ryan Wisnesky. “Algebraic Databases.” *Theory and Applications of Categories* 32 (2017): 547–619. Preprint: arXiv:1602.03501.

**[R10]** Agda Team. *Cubical Agda Documentation*. Current online documentation, consulted August 5, 2026. <https://agda.readthedocs.io/en/latest/language/cubical.html>

**[R11]** Cyril Cohen, Thierry Coquand, Simon Huber, and Anders Mörtberg. “Cubical Type Theory: A Constructive Interpretation of the Univalence Axiom.” In *Types for Proofs and Programs (TYPES 2015)*, Leibniz International Proceedings in Informatics 69, article 5, 2017. arXiv:1611.02108.

**[R21]** Thierry Coquand, Simon Huber, and Anders Mörtberg. “On Higher Inductive Types in Cubical Type Theory.” In *Proceedings of LICS 2018*. arXiv:1802.01170.

**[R22]** Evan Cavallo and Robert Harper. “Computational Higher Type Theory IV: Inductive Types.” 2018. arXiv:1801.01568.

**[R23]** Mario Carneiro. “Lean4Lean: Verifying Lean 4's Type Theory in Lean.” 2024. arXiv:2403.14064.

## F.2 Applied category theory and higher-structure references

**[R24]** Brendan Fong and David I. Spivak. *An Invitation to Applied Category Theory: Seven Sketches in Compositionality*. Cambridge University Press, 2019. DOI: 10.1017/9781108668804.

**[R25]** Emily Riehl. *Category Theory in Context*. Dover Publications, 2017. Author's open edition: <https://emilyriehl.github.io/files/context.pdf>

**[R26]** Nicolai Kraus and Jakob von Raumer. “Path Spaces of Higher Inductive Types in Homotopy Type Theory.” 2019. arXiv:1901.06022.

**[R27]** Peter LeFanu Lumsdaine and Michael Shulman. “Semantics of Higher Inductive Types.” *Mathematical Proceedings of the Cambridge Philosophical Society* 169, no. 1 (2020): 159–208. Preprint: arXiv:1705.07088.

## F.3 Industrial standards and specifications

**[R12]** International Society of Automation. *ISA-95: Enterprise-Control System Integration* standards family. Official overview and catalog, consulted August 5, 2026. <https://www.isa.org/standards-and-publications/isa-standards/isa-95-standard>

**[R13]** OPC Foundation. *OPC UA for ISA-95 Common Object Model*. Current online reference, consulted August 5, 2026. <https://reference.opcfoundation.org/ISA-95/v100/docs/>

**[R14]** Industrial Digital Twin Association. *Asset Administration Shell Specification—Metamodel*. Versioned specification repository; version 3.1.2 was the current published line consulted for this edition. <https://github.com/admin-shell-io/aas-specs-metamodel>

**[R15]** OPC Foundation. *OPC UA Companion Specification for the Asset Administration Shell*. Current online reference, consulted August 5, 2026. <https://reference.opcfoundation.org/AAS/v100/docs/>

**[R16]** International Organization for Standardization. *ISO 10303-242, Industrial automation systems and integration—Product data representation and exchange—Application protocol: Managed model-based 3D engineering*. Consult the ISO catalog for the current edition and corrigenda. <https://www.iso.org/standard/84382.html>

**[R17]** GS1. *EPCIS and Core Business Vocabulary Standard*. Official standard resources, consulted August 5, 2026. <https://www.gs1.org/standards/epcis>

**[R18]** International Organization for Standardization. *ISO 15926-2:2003, Industrial automation systems and integration—Integration of life-cycle data for process plants including oil and gas production facilities—Part 2: Data model*. <https://www.iso.org/standard/29557.html>

**[R19]** International Organization for Standardization. *ISO/TS 15926-11:2023, Simplified industrial usage of reference data*. Consult the ISO catalog for status and amendments. <https://www.iso.org/standard/78570.html>

**[R20]** International Organization for Standardization. *ISO 15926-100:2026, Integration of life-cycle data for process plants including oil and gas production facilities—Part 100: Adaptation of the ISO 15926-2 data model for implementation in RDF*. Consult the ISO catalog for the current publication record. <https://www.iso.org/standard/93280.html>

## F.4 How the standards are used in this book

The standards are treated as **source ontologies and boundary vocabularies**, not as interchangeable universal models.

- ISA-95 and its OPC UA companion provide distinctions useful at the enterprise–manufacturing boundary, including material, equipment, personnel, operations, schedules, and actuals.
- AP242 provides product-definition, revision, configuration, and model-based engineering structures.
- AAS provides a digital-twin metamodel, identifiers, submodels, and interoperable representations.
- EPCIS contributes event-oriented supply-chain visibility and traceability vocabulary.
- ISO 15926 contributes lifecycle, process-plant, reference-data, and semantic-integration concepts.

A company theory should import only the fragments needed by its competency questions. The formal alignment must state what each imported concept means locally and which edition or profile was used.

## F.5 Version discipline

Software and standards evolve. A reproducible ontology package should therefore record:

```text
theory identifier and immutable version
Lean toolchain or cubical prover version
library commit hashes
industrial standard edition and profile
source-schema versions
alignment-rule versions
proof-certificate format
extraction-policy version
```

The semantic content of a proof depends on these declarations. A change to an alignment constructor, standard profile, or truncation policy is a theory migration even when no application table changes shape.

## F.6 Citation scope

References [R4], [R5], [R8], and [R9] support the categorical database and olog foundations. References [R6], [R7], [R10], [R11], [R21], [R22], [R26], and [R27] support the HoTT, cubical, and higher-inductive foundations. References [R12]–[R20] are industrial source specifications. The synthesis called a **theory of ERP system ontologies**, including the ontology calculus and homotopical integration architecture developed in Parts II and III, is the constructive proposal of this book rather than a claim that the industrial standards prescribe HoTT.

# Closing Note

The central engineering decision in an ontology project is not whether to use a graph database, an RDF vocabulary, a canonical JSON schema, or a proof assistant. It is which distinctions the organization is prepared to preserve and which identifications it is prepared to authorize.

Category theory makes composition and mapping laws explicit. Dependent type theory makes admissibility depend on context, evidence, time, quantity, and state. Homotopy type theory makes identification itself structured: paths are generated by approved witnesses, parallel paths require coherence, dependent meaning is transported, and truncation records where the architecture deliberately forgets distinctions.

A conventional ERP API can remain conventional. Its reliability improves when it is extracted from a theory that knows what was collapsed to produce it.
