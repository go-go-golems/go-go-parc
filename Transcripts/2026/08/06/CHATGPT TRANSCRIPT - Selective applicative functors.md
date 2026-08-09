# Selective applicative functors

- URL: https://chatgpt.com/c/6a746e4a-d218-83ea-852f-df8ca2a063f2
- Created: 2026-08-06T11:21:52.398Z

---

> Sélective applicative in interaction programming (a bounded branch can depend on an earlier result).
>
> How?

Je vais préciser le mécanisme avec les types, puis montrer un petit exemple d’interaction où la branche dépend d’un résultat précédent sans passer à une monade complète.

```json
{"system1_search_query":[{"q":"Selective Applicative Functors paper Mokhov selective branch type"},{"q":"Hackage selective package Control.Selective documentation branch select"}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Searched 1 website**

**Deriving branch types**

I’m checking the nested `select` construction by working backward from the required result types. The outer step needs `f (Either b c)`, while the inner step combines `x` with `l`; I’m verifying each mapping carefully.

**Derived branch types**

</details>

A **selective applicative functor** permits data-dependent control flow, provided the possible effectful branches are known in advance.

## Core operation

```haskell
class Applicative f => Selective f where
  select :: f (Either a b) -> f (a -> b) -> f b
```

Operationally:

```haskell
select decision handler = do
  result <- decision

  case result of
    Left  a -> ($ a) <$> handler  -- execute handler
    Right b -> pure b             -- handler may be skipped
```

The `do` notation above only explains the semantics; implementing `Selective` does not require exposing a general monadic bind.

Thus:

- `Right b` means the computation is already complete.
- `Left a` means another statically declared effect is required.
- The result of the first effect decides whether the second effect runs.

Selective functors therefore sit between `Applicative` and `Monad`: effects are declared statically, but some may be selected dynamically. citeturn912093search0turn912093search5

## Two-way branching

The more direct combinator for interaction programs is:

```haskell
branch
  :: Selective f
  => f (Either a b)
  -> f (a -> c)
  -> f (b -> c)
  -> f c
```

Its operational interpretation is:

```haskell
result <- decision

case result of
  Left  a -> leftBranch  <*> pure a
  Right b -> rightBranch <*> pure b
```

So an earlier interaction can choose between two later interactions, but both possible branches must occur syntactically in the program.

A common specialization is:

```haskell
ifS :: Selective f => f Bool -> f a -> f a -> f a
```

## Interaction example

Suppose an administrator must enter an access code, while a guest does not:

```haskell
import Control.Selective

data Role
  = Guest
  | Admin
  deriving Eq

data Session
  = GuestSession
  | AdminSession String

login
  :: Selective f
  => f Role       -- interaction: choose a role
  -> f String     -- interaction: enter an admin code
  -> f Session
login chooseRole askAdminCode =
  ifS
    ((== Admin) <$> chooseRole)
    (AdminSession <$> askAdminCode)
    (pure GuestSession)
```

At runtime:

```text
chooseRole
    |
    +-- Admin --> askAdminCode --> AdminSession
    |
    +-- Guest ------------------> GuestSession
```

The second prompt depends on the result of the first prompt. However, the complete set of possible interactions remains visible from the program:

```text
possible effects = { chooseRole, askAdminCode }
```

A runtime interpreter can skip `askAdminCode` for guests. A static-analysis interpreter can still inspect both possible effects—for example, to generate a form graph, calculate permissions, enumerate dependencies, or validate that every branch is handled. Selective instances are intentionally allowed, but not required, to skip the unselected effect because some interpreters exist specifically to analyse all possible effects. citeturn912093search0turn912093search1

## General pattern

Given an earlier result:

```haskell
earlier :: f r
```

convert it into a finite choice:

```haskell
decide :: r -> Either a b
```

and supply both possible effectful continuations:

```haskell
program :: Selective f => f r -> f (a -> c) -> f (b -> c) -> f c
program earlier leftProgram rightProgram =
  branch
    (decide <$> earlier)
    leftProgram
    rightProgram
```

The dependency exists here:

```haskell
decide <$> earlier
```

but it only selects between `leftProgram` and `rightProgram`. It does not construct an arbitrary new program.

## Why the branch is bounded

Compare the three abstractions:

```haskell
-- Fixed effects
(<*>)  :: f (a -> b) -> f a -> f b

-- Fixed finite alternatives; runtime chooses one
branch :: f (Either a b)
       -> f (a -> c)
       -> f (b -> c)
       -> f c

-- Arbitrary subsequent structure generated from runtime data
(>>=)  :: f a -> (a -> f b) -> f b
```

With a monad, the value `a` can generate any subsequent computation:

```haskell
askCount >>= \n ->
  replicateM n askQuestion
```

The number and structure of later effects may be unknown until runtime.

A selective interface cannot generally express that. It can express:

```haskell
ifS wantsDetails
    askOneKnownFollowup
    skipFollowup
```

because the alternatives are already present and finite.

## Implementing `branch` using `select`

`branch` requires no additional primitive:

```haskell
branch
  :: Selective f
  => f (Either a b)
  -> f (a -> c)
  -> f (b -> c)
  -> f c
branch choice left right =
  select
    (select
      (fmap (fmap Left) choice)
      (fmap (fmap Right) left))
    right
```

Conceptually, it performs two selections:

1. If the original value is `Left a`, execute the left handler and produce the final `c`.
2. Otherwise retain `b`, then execute the right handler.

That is how selective applicatives provide **limited data-dependent interaction while preserving a statically inspectable effect graph**.


---

> In lean4, and use that to teach me lean

Je vais construire une version Lean 4 minimale, la vérifier, puis l’utiliser pour expliquer les notions de base : types inductifs, classes de types, foncteurs/applicatifs, interprètes et preuves simples.

```json
{"system2_search_query":[{"q":"site:lean-lang.org/doc/reference/latest Lean 4 type classes Applicative Functor Sum IO"},{"q":"site:lean-lang.org/doc/reference/latest Lean 4 inductive types structures classes do notation"}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Searched 1 website**

</details>

```unknown
bash -lc lean --version || lake --version || echo no-lean
```

<details><summary>💭 Thinking</summary>

**Checked Lean installation and version**

</details>

```json
{"system1_search_query":[{"q":"site:lean-lang.org/doc/reference/latest/releases Lean 4 latest stable August 2026"},{"q":"site:github.com/leanprover/lean4/releases latest Lean 4 release August 2026"}],"response_length":"medium"}
```

<details><summary>💭 Thinking</summary>

**Searching github.com**

**Designing selective applicatives**

I’m outlining a Lean approach using a typed program AST with pure, mapping, application, and selection nodes. I’m also considering how to define conditional behavior without relying on an overly complicated generic free construction.

**Designed selective applicatives**

**Interpreting the program**

I’m refining the AST with applicative sequencing and selective branching, then planning a pure interpreter that records which prompts execute. This avoids uncertain runtime I/O details while still demonstrating short-circuiting behavior clearly.

**Interpreted the program**

</details>

Le point important sera visible dans l’interprète : le constructeur de branche contient les deux continuations, mais l’exécution n’en évalue qu’une. Cela donne une dépendance dynamique avec une structure statiquement bornée.

```json
{"open":[{"ref_id":"https://github.com/leanprover/lean4/releases/download/v4.32.2/lean-4.32.2-linux.tar.zst"}],"response_length":"short"}
```

<details><summary>💭 Thinking</summary>

**Searching the web**

</details>

```json
{"open":[{"ref_id":"https://api.github.com/repos/leanprover/lean4/releases/tags/v4.32.2"}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Searching arxiv.org**

</details>

```unknown
bash -lc python - <<'PY'
import urllib.request
u='https://github.com/leanprover/lean4/releases/download/v4.32.2/lean-4.32.2-linux.tar.zst'
try:
    r=urllib.request.urlopen(u, timeout=20)
    print(r.status, r.geturl(), r.headers.get('content-length'))
except Exception as e:
    print(type(e), e)
PY
```

<details><summary>💭 Thinking</summary>

**Tested GitHub download access**

</details>

```json
{"system2_search_query":[{"q":"site:lean-lang.org/doc/reference/latest \"class Applicative\" \"seq\" Lean"},{"q":"site:lean-lang.org/doc/reference/latest Applicative.seq Lean 4"},{"q":"site:github.com/leanprover/lean4 \"class Applicative\" \"seq\" Init.Control.Basic"}],"response_length":"long"}
```

```json
{"paths":["GitHub"],"query":"search code"}
```

<details><summary>💭 Thinking</summary>

**Searched 2 websites**

</details>

```python3
{"path":"/GitHub/link_694554034b848191ab0db5a14b130105/search","args":{"query":"Selective","repository_name":["leanprover/lean4","leanprover-community/mathlib4"],"topn":20}}
```

<details><summary>💭 Thinking</summary>

**Searched Lean repositories for Selective definitions**

</details>

```unknown
bash -lc apt-cache search '^lean4$|theorem prover lean' | head -20
```

<details><summary>💭 Thinking</summary>

**Searched packages for Lean theorem prover**

</details>

```json
{"system2_search_query":[{"q":"site:lean-lang.org/functional_programming_in_lean inductive Type → Type Functor instance seq Lean GADT"},{"q":"site:lean-lang.org/functional_programming_in_lean free monad inductive Type → Type Lean 4"},{"q":"site:lean-lang.org/doc/reference/latest indexed inductive family example Type → Type"}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Searched 2 websites**

</details>

Voici une implémentation pédagogique en **Lean 4**. Je prends `branch` comme opération primitive, car elle exprime directement l’idée recherchée : le résultat d’une interaction choisit entre deux branches déjà présentes dans le programme.

Lean représente naturellement ce genre de DSL par une **famille inductive indexée par le type du résultat**. Les classes de types fournissent ensuite les opérations surchargées comme `pure`, `<$>` et notre `branch`. citeturn917127search1turn917127search27

## 1. L’interface `Selective`

```lean
universe u v

/--
Un applicatif sélectif.

Les deux branches sont présentes dans le programme,
mais une seule doit être exécutée.
-/
class Selective (F : Type u → Type v) extends Applicative F where
  branch {α β γ : Type u} :
    F (Sum α β) →
    F (α → γ) →
    F (β → γ) →
    F γ
```

Lis le type de `branch` ainsi :

```text
F (Sum α β)    -- une décision produite par un effet antérieur
F (α → γ)      -- branche gauche
F (β → γ)      -- branche droite
F γ            -- résultat final
```

`Sum α β` est l’équivalent Lean de `Either α β` :

```lean
Sum.inl a : Sum α β
Sum.inr b : Sum α β
```

La branche peut dépendre d’une valeur antérieure, mais les deux programmes possibles sont déjà des arguments de `branch`.

On peut retrouver l’opération classique `select` :

```lean
namespace Selective

def select
    {F : Type u → Type v}
    [Selective F]
    {α β : Type u}
    (decision : F (Sum α β))
    (onLeft : F (α → β)) :
    F β :=
  Selective.branch
    decision
    onLeft
    (pure (fun b => b))

end Selective
```

La branche droite ne fait rien : elle retourne simplement son argument.

## 2. Construire `ifS`

Voici un `if` dont la condition est elle-même un effet :

```lean
def ifS
    {F : Type u → Type v}
    [Selective F]
    {α : Type u}
    (condition : F Bool)
    (thenBranch : F α)
    (elseBranch : F α) :
    F α :=
  Selective.branch
    ((fun b =>
        if b then
          (Sum.inl () : Sum Unit Unit)
        else
          Sum.inr ()) <$> condition)
    ((fun result _ => result) <$> thenBranch)
    ((fun result _ => result) <$> elseBranch)
```

Quelques éléments de syntaxe Lean :

```lean
f <$> computation
```

signifie :

```lean
Functor.map f computation
```

Et :

```lean
fun result _ => result
```

est une fonction à deux arguments. Le second argument est ignoré :

```lean
α → Unit → α
```

Lean considère une fonction à plusieurs arguments comme une fonction qui retourne une autre fonction :

```lean
α → Unit → α
```

signifie réellement :

```lean
α → (Unit → α)
```

## 3. Un langage d’interaction typé

Définissons les données de l’application :

```lean
inductive Role where
  | guest
  | admin
deriving Repr, DecidableEq

def Role.isAdmin : Role → Bool
  | .guest => false
  | .admin => true

inductive Session where
  | guest
  | admin (code : String)
deriving Repr, DecidableEq
```

`inductive` déclare un type par ses constructeurs. Par exemple, toute valeur de type `Role` est nécessairement `.guest` ou `.admin`. Lean génère également un principe de récursion et d’analyse par cas pour chaque type inductif. citeturn795830search0

Définissons maintenant la syntaxe des interactions :

```lean
inductive Interaction : Type → Type 1 where
  | pure {α : Type} :
      α → Interaction α

  | map {α β : Type} :
      (α → β) →
      Interaction α →
      Interaction β

  | ap {α β : Type} :
      Interaction (α → β) →
      Interaction α →
      Interaction β

  | branch {α β γ : Type} :
      Interaction (Sum α β) →
      Interaction (α → γ) →
      Interaction (β → γ) →
      Interaction γ

  | askRole :
      Interaction Role

  | askCode :
      Interaction String
```

Le type :

```lean
Interaction α
```

signifie :

> un programme d’interaction qui, lorsqu’il est interprété, produit un `α`.

Par exemple :

```lean
Interaction.askRole : Interaction Role
Interaction.askCode : Interaction String
```

`Interaction` est une **famille indexée** : chaque constructeur détermine le type de résultat. Les familles indexées permettent précisément à différents constructeurs de produire différentes instances d’un même type paramétré. citeturn917127search7

## 4. Les instances applicative et sélective

```lean
instance : Applicative Interaction where
  map := Interaction.map
  pure := Interaction.pure
  seq functionProgram argumentProgram :=
    Interaction.ap functionProgram (argumentProgram ())

instance : Selective Interaction where
  toApplicative := inferInstance
  branch := Interaction.branch
```

La première instance indique à Lean comment interpréter :

```lean
pure x
f <$> program
functionProgram <*> argumentProgram
```

La méthode Lean `seq`, utilisée par `<*>`, reçoit son second argument sous la forme `Unit → F α`. Ce délai permet aux instances applicatives de contrôler son évaluation. citeturn426041search4turn917127search5

La seconde instance indique comment construire une branche sélective. Ici, nous ne l’exécutons pas encore : nous construisons simplement un nœud `.branch` dans l’arbre syntaxique.

## 5. Le programme de connexion

```lean
def login : Interaction Session :=
  ifS
    (Role.isAdmin <$> Interaction.askRole)
    (Session.admin <$> Interaction.askCode)
    (pure Session.guest)
```

Décomposons son type.

Premièrement :

```lean
Interaction.askRole
```

a pour type :

```lean
Interaction Role
```

Puis :

```lean
Role.isAdmin <$> Interaction.askRole
```

a pour type :

```lean
Interaction Bool
```

Parce que :

```lean
Role.isAdmin : Role → Bool
```

Ensuite, la branche administrateur :

```lean
Session.admin <$> Interaction.askCode
```

a pour type :

```lean
Interaction Session
```

car :

```lean
Session.admin : String → Session
Interaction.askCode : Interaction String
```

Enfin :

```lean
pure Session.guest
```

a également pour type :

```lean
Interaction Session
```

Les deux branches ont donc le même type de résultat, comme les deux branches d’un `if` ordinaire.

## 6. Un interprète qui exécute une seule branche

Pour tester sans dépendre d’un terminal, fournissons les réponses dans une structure :

```lean
structure Answers where
  role : Role
  code : String
```

L’interprète retourne le résultat et la liste des interactions réellement exécutées :

```lean
def Interaction.run
    (answers : Answers)
    {α : Type} :
    Interaction α → α × List String

  | .pure value =>
      (value, [])

  | .map f program =>
      let (value, log) := run answers program
      (f value, log)

  | .ap functionProgram argumentProgram =>
      let (f, functionLog) := run answers functionProgram
      let (argument, argumentLog) := run answers argumentProgram
      (f argument, functionLog ++ argumentLog)

  | .branch decision leftBranch rightBranch =>
      let (choice, decisionLog) := run answers decision

      match choice with
      | .inl leftValue =>
          let (f, branchLog) := run answers leftBranch
          (f leftValue, decisionLog ++ branchLog)

      | .inr rightValue =>
          let (f, branchLog) := run answers rightBranch
          (f rightValue, decisionLog ++ branchLog)

  | .askRole =>
      (answers.role, ["ask role"])

  | .askCode =>
      (answers.code, ["ask admin code"])
```

Le cœur du comportement sélectif est ici :

```lean
match choice with
| .inl leftValue =>
    run answers leftBranch
| .inr rightValue =>
    run answers rightBranch
```

Une seule branche est envoyée récursivement à `run`.

Testons :

```lean
#eval Interaction.run
  { role := .guest, code := "unused" }
  login

#eval Interaction.run
  { role := .admin, code := "s3cr3t" }
  login
```

Résultats attendus :

```text
(.guest, ["ask role"])

(.admin "s3cr3t", ["ask role", "ask admin code"])
```

Pour un invité, `askCode` est présent dans le programme mais n’est pas exécuté.

## 7. Un interprète statique qui inspecte les deux branches

Un avantage majeur de la structure sélective est qu’un autre interprète peut examiner toutes les interactions possibles :

```lean
def Interaction.possiblePrompts
    {α : Type} :
    Interaction α → List String

  | .pure _ =>
      []

  | .map _ program =>
      possiblePrompts program

  | .ap functionProgram argumentProgram =>
      possiblePrompts functionProgram ++
      possiblePrompts argumentProgram

  | .branch decision leftBranch rightBranch =>
      possiblePrompts decision ++
      possiblePrompts leftBranch ++
      possiblePrompts rightBranch

  | .askRole =>
      ["ask role"]

  | .askCode =>
      ["ask admin code"]
```

```lean
#eval Interaction.possiblePrompts login
```

Résultat :

```text
["ask role", "ask admin code"]
```

Nous avons donc deux interprétations du même programme :

```text
run
    inspecte une décision réelle
    exécute une seule branche

possiblePrompts
    ignore la décision réelle
    inspecte les deux branches
```

## 8. Utiliser la réduction comme preuve

En Lean, une égalité calculable peut souvent être prouvée avec `rfl` :

```lean
example :
    (Interaction.run
      { role := .guest, code := "unused" }
      login).2
      =
    ["ask role"] := by
  rfl
```

Et pour l’analyse statique :

```lean
example :
    Interaction.possiblePrompts login
      =
    ["ask role", "ask admin code"] := by
  rfl
```

`rfl` prouve une égalité réflexive. Lean réduit ici les définitions jusqu’à ce que les deux côtés deviennent identiques.

## 9. Pourquoi ce n’est pas une monade

Une monade fournirait :

```lean
bind :
  Interaction α →
  (α → Interaction β) →
  Interaction β
```

La fonction :

```lean
α → Interaction β
```

peut construire une interaction entièrement nouvelle à partir d’une valeur calculée.

Notre branche sélective reçoit plutôt :

```lean
Interaction (Sum α β)
Interaction (α → γ)
Interaction (β → γ)
```

Les deux continuations sont déjà présentes. Le premier résultat ne peut que choisir entre elles.

```text
Applicative
    aucune branche dépendante

Selective
    choix entre un ensemble statique de branches

Monad
    construction arbitraire de la suite du programme
```

C’est exactement la propriété recherchée : **la décision est dynamique, mais l’espace des programmes possibles reste statiquement visible**.

Les snippets utilisent uniquement les interfaces fondamentales de Lean. Je n’avais pas de binaire Lean disponible pour les compiler localement ; ils sont écrits selon les définitions actuelles de `Functor`, `Applicative`, `seq`, des classes et des familles inductives dans la documentation officielle.

