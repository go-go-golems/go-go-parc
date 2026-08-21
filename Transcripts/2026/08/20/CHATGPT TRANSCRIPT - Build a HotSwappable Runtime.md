# Build a HotSwappable Runtime

- URL: https://chatgpt.com/c/6a877639-802c-83ea-97f7-c88965c1dd60
- Created: 2026-08-20T21:48:43.417Z

---

> how could I build a toy version of this so it can help me understand the maths and theory in this paper, while also having some usefulness.

<details><summary>💭 Thinking</summary>

**Designing a toy runtime**

I’m proposing a small Python plugin system: components declare services, activation returns cleanup functions, and the runtime supports composition, removal, and dependency checks. I’ll connect each feature to monoids, inverses, coeffects, and lifecycle laws.

**Designed a toy runtime**

</details>

The best toy is not a miniature clone of Cordis. It should expose the paper’s invariants directly: “apply effect → record inverse → undo later,” plus “declare dependency → activate/deactivate when availability changes.” Those are the two dimensions the paper calls temporal and spatial composability.

<details><summary>💭 Thinking</summary>

**Building the toy runtime**

I’m shaping this into a small Python plugin system for a CLI: components provide services, require dependencies, register commands, and return undo actions. I’ll use it to demonstrate composition, inverses, coeffects, and safe unloading.

**Built the toy runtime**

</details>

A good project would be a **tiny hot-swappable plugin/tool runtime**. It would be small enough that you can trace every state transition by hand, but useful enough to run real commands or agent tools.

The paper’s central move is to turn two abstract ideas into runtime mechanisms:

- **Effects → reversible changes:** an effect changes the context and supplies an inverse. Formally the paper models this as roughly `Γ → Γ × (Γ → Γ)`. fileciteturn0file0L295-L303
- **Coeffects → reactive requirements:** a component declares which keys it needs, and changes in the context can make that requirement become satisfied or unsatisfied, triggering activation/deactivation. fileciteturn0file0L1082-L1102

So I would build this.

## The toy system: `HotBox`

Imagine a little command-line application with dynamically installable plugins.

For example:

```text
clock plugin
    provides: "clock"

notes plugin
    provides: "notes"

daily-summary plugin
    requires: "clock", "notes"
    provides command: "summary"
```

While `clock` and `notes` exist, `daily-summary` is active.

Remove `notes`:

```text
notes unloads
↓
daily-summary notices its requirement disappeared
↓
daily-summary cleans itself up
↓
notes finishes unloading
```

Install `notes` again:

```text
notes activates
↓
"notes" becomes available
↓
daily-summary requirements are satisfied again
↓
daily-summary activates
```

That is already a genuinely useful plugin architecture, while being almost exactly the mathematical picture in the paper.

---

## 1. Start with the mathematics, not plugins

First make `Γ` embarrassingly small.

```python
@dataclass
class State:
    values: dict[str, object]
```

An effect can initially look like:

```python
Effect = Callable[[State], tuple[State, Callable[[State], State]]]
```

For example:

```python
def set_value(key, value):
    def effect(state):
        old = state.values.get(key, MISSING)

        new = State(state.values | {key: value})

        def inverse(current):
            values = dict(current.values)

            if old is MISSING:
                del values[key]
            else:
                values[key] = old

            return State(values)

        return new, inverse

    return effect
```

Now experimentally verify:

```python
s0 = State({})

s1, undo = set_value("x", 42)(s0)

assert undo(s1) == s0
```

That assertion is the concrete version of the paper's witnessed inverse condition: the inverse only needs to undo the effect **at the state where that effect was applied**. fileciteturn0file0L487-L506

This is probably the most useful first implementation because suddenly

$$
g(f(\gamma))=\gamma
$$

isn't abstract notation. It's a unit test.

---

## 2. Then implement the paper's monoid

Suppose you do:

```text
set x = 10
set y = 20
set z = 30
```

You get inverses:

```text
undo_x
undo_y
undo_z
```

The combined inverse has to run:

```text
undo_z
undo_y
undo_x
```

This is the twisted composition in the paper:

$$
(f_1,g_1)\circ(f_2,g_2)
=
(f_1\circ f_2,\;g_2\circ g_1)
$$

The forward transformations compose one way and the inverse transformations accumulate in the opposite direction. fileciteturn0file0L315-L330

In your toy implementation that becomes almost laughably simple:

```python
class Scope:
    def __init__(self):
        self.undo = []

    def effect(self, state, effect):
        new_state, inverse = effect(state)
        self.undo.append(inverse)
        return new_state

    def dispose(self, state):
        for inverse in reversed(self.undo):
            state = inverse(state)

        self.undo.clear()
        return state
```

Now the rather intimidating algebra in §3.1 becomes:

> a stack of cleanup functions.

But crucially, you understand *why* a cleanup stack has the algebraic structure it does.

---

## 3. Turn `State` into the coeffect context

Next introduce services:

```python
class Context:
    def __init__(self):
        self.services = {}
```

Now:

```python
ctx.services["clock"] = Clock()
ctx.services["notes"] = Notes()
```

This is your simplified version of the paper's coeffect context

$$
\Sigma = (k:K) \rightharpoonup V_k
$$

—a finite partial mapping from dependency keys to appropriately typed values. fileciteturn0file0L994-L1017

A component then becomes:

```python
@dataclass
class Component:
    name: str
    requires: set[str]
    provides: set[str]
    activate: Callable
```

This corresponds very closely to the paper's component triple:

$$
(d,p,e)
$$

where `d` is what it requires, `p` is what it provides, and `e` is its reversible effect. fileciteturn0file0L1622-L1637

At this point the notation has acquired a direct programming interpretation:

```text
d = {"clock", "notes"}

p = {"summary"}

e = activate_daily_summary
```

---

## 4. Implement satisfaction literally

The paper defines dependency satisfaction essentially as:

$$
\sigma \models d
\iff
\forall k\in d,\; k\in\mathrm{dom}(\sigma)
$$

fileciteturn0file0L1083-L1093

Your implementation is:

```python
def satisfied(component, ctx):
    return component.requires <= ctx.services.keys()
```

That's it.

Then implement:

```python
def refresh(component):
    should_run = satisfied(component, ctx)

    if should_run and not component.active:
        activate(component)

    elif not should_run and component.active:
        deactivate(component)
```

You have now implemented the paper's activating/deactivating/neutral notification idea. fileciteturn0file0L1101-L1119

This is one of the useful lessons of building the toy: some of the paper's notation describes very ordinary machinery once the right abstraction has been identified.

---

## 5. Give every running component its own undo stack

Don't give the entire application one global undo stack.

Make a `Fiber`:

```python
@dataclass
class Fiber:
    component: Component
    active: bool = False
    undo: list = field(default_factory=list)
    committed: dict = field(default_factory=dict)
```

Then activation becomes conceptually:

```python
fiber.committed = resolve(fiber.component.requires)
fiber.undo = run_component(fiber.component)
fiber.active = True
```

and unloading:

```python
for undo in reversed(fiber.undo):
    undo()

fiber.undo.clear()
fiber.active = False
```

This is the important architectural jump.

Now:

```text
plugin A effects → A's inverse stack
plugin B effects → B's inverse stack
plugin C effects → C's inverse stack
```

So you can remove B while A and C stay alive.

That's **temporal composability** in miniature.

---

## 6. Build one genuinely useful effect

Rather than only manipulating dictionaries, let plugins register CLI commands:

```python
def register_command(ctx, name, handler):
    ctx.commands[name] = handler

    def undo():
        del ctx.commands[name]

    return undo
```

A plugin can now do:

```python
def activate(ctx):
    return [
        register_command(
            ctx,
            "hello",
            lambda: print("hello")
        )
    ]
```

Unloading that plugin automatically removes `hello`.

Then add other reversible primitives:

```text
register_command()
subscribe_event()
provide_service()
schedule_timer()
register_route()
```

Every one follows the same shape:

```text
do something
return how to undo it
```

This closely matches Cordis's actual implementation strategy: context mutation runs through one effect primitive, whose callback yields inverses that are accumulated for recovery. fileciteturn0file0L3458-L3483

This is where your toy stops being merely educational and becomes a little plugin framework.

---

## 7. Make provider replacement visible

There's a subtle idea in the paper worth implementing.

Don't define a component's resolved dependencies merely as:

```python
{"clock": Clock()}
```

Record **who provided them**:

```python
{"clock": "clock-plugin-17"}
```

Suppose:

```text
ClockPluginV1 -> provides "clock"
```

gets replaced by:

```text
ClockPluginV2 -> provides "clock"
```

Even if both objects happen to compare equal, the consumer should reload because its provider changed.

The paper calls this the component's **committed view** and compares it against the current target view to drive lifecycle transitions. fileciteturn0file0L1759-L1765

Implementing this will make the lifecycle calculus in §4 much easier to understand.

---

## 8. Add one piece of the hard theory: independence

This is where the project becomes particularly useful for learning the maths.

Make two effects:

```text
A: set key "a"
B: set key "b"
```

Test:

```python
A(B(s)) == B(A(s))
```

They commute because they touch separate parts of the context.

Then remove A while B remains.

It works.

Now try:

```text
A: append middleware A
B: append middleware B
```

These give:

```text
[A, B]
```

versus:

```text
[B, A]
```

They do **not** commute.

This is a concrete demonstration of the paper's independence condition. It specifically notes that operations on distinct keys commute automatically, while an ordered chain such as middleware generally does not. fileciteturn0file0L1466-L1498

I'd make this a test suite:

```python
def commute(e1, e2, state):
    return apply(e1, apply(e2, state)) == \
           apply(e2, apply(e1, state))
```

Now §3.1.3 stops looking like arbitrary formal machinery. You're discovering the conditions under which one plugin can be removed without perturbing another.

---

## 9. Implement dependency-safe unloading

This is probably the most interesting practical extension.

Suppose:

```text
database
   ↑
repository
   ↑
web-api
```

If `database` disappears, don't immediately destroy it.

Do:

```text
1. mark database as leaving
2. stop advertising "database"
3. repository sees dependency disappear
4. unload web-api
5. unload repository
6. finally undo database
```

Why wait?

Because `repository` might need the database **while cleaning itself up**.

That is exactly the motivation for the paper's `relied` guard: the provider's actual recovery waits until dependents have deactivated. fileciteturn0file0L1918-L1948

For the toy, you don't need their complete operational calculus. A recursive implementation is enough:

```python
async def deactivate(fiber):
    dependents = active_dependents_of(fiber)

    for dependent in dependents:
        await deactivate(dependent)

    await fiber.dispose()
```

That gives you most of the intuition behind the more elaborate state machine.

---

## 10. Add observational equivalence last

This is one of the nicest theoretical experiments.

Initially test:

```python
final_state == initial_state
```

Then introduce something such as generated IDs:

```text
load plugin -> gets resource id 47
unload plugin
load again -> gets resource id 48
```

You can no longer literally recover the identical machine state.

But perhaps nothing observable can distinguish them.

So define:

```python
def observe(ctx):
    return {
        "available_services": sorted(ctx.services),
        "commands": sorted(ctx.commands),
    }
```

Then test:

```python
observe(recovered_state) == observe(initial_state)
```

That gets directly at §3.3.2: the paper explicitly argues that literal physical-state equality is too strong, and instead reads recovery through observational equivalence. fileciteturn0file0L1307-L1319

This is probably the point where the category/type-theoretic material will start feeling much less mystical.

---

## A sensible build sequence

I'd keep the entire project under perhaps **500–800 lines** initially:

| Stage | Build | Theory you learn |
|---|---|---|
| 1 | Immutable `State` + reversible functions | `Γ`, inverses |
| 2 | Compose effects + undo stack | monoid, twisted composition |
| 3 | Service registry | `Σ`, coeffect context |
| 4 | `requires` / `provides` | satisfaction predicate |
| 5 | Component activation/deactivation | reactive coeffects |
| 6 | Per-component undo stacks | temporal composability |
| 7 | Provider identity | committed/target views |
| 8 | Dependency-safe teardown | spatial ordering |
| 9 | Commutation tests | independence |
| 10 | `observe(state)` | observational equivalence |

I would **not** initially implement isolation, interception, async iterators, configuration reconciliation, HMR, failure semantics, or the full four-state lifecycle. The paper deliberately layers these on after establishing the basic model. fileciteturn0file0L1605-L1617

The minimal conceptual core is only:

```text
Context
    services
    commands

Component
    requires
    provides
    activate()

Fiber
    active
    committed_dependencies
    undo_stack

Runtime
    add(component)
    remove(component)
    refresh()
```

If you can implement that and write the six or seven algebraic tests above, you'll have a surprisingly strong intuitive handle on most of Sections 3 and 4, while also ending up with a legitimate hot-swappable plugin/tool framework rather than a throwaway mathematical exercise.


---

> if you were to create a lab for students to work through the paper through implementing this system, how would you structure it and what exercises / milestones would you get them, and which resources would you give them to read for the theory part (both the theory / CS / maths, but also some more applied resources of the CT to programming)

I’d structure it as a sequence of implementation labs where each new feature corresponds to one definition/theorem in the paper, and each lab ends with a small empirical “theorem check” in code. I’ll anchor the milestones to the paper, then pair each with a short theory reading and a more applied category-theory/programming resource.

```unknown
fast|Types and Programming Languages Pierce official MIT Press
fast|Moggi Notions of computation and monads PDF
fast|Petricek Orchard Mycroft Coeffects unified static analysis PDF
fast|Heunen Kaarsgaard Karvonen Reversible Effects as Inverse Arrows PDF
fast|Mazurkiewicz Trace Theory PDF
fast|Category Theory for Programmers Bartosz Milewski book
fast|Seven Sketches in Compositionality Fong Spivak official
fast|Acar Blelloch Harper Adaptive functional programming PDF
length|medium

```

```unknown
fast|site:homepages.inf.ed.ac.uk wadler monads for functional programming pdf
fast|Eugenio Moggi Notions of computation and monads PDF Edinburgh
fast|Category Theory for Programmers Bartosz Milewski official PDF github
fast|site:math.mit.edu spivak seven sketches compositionality pdf
fast|Applied Category Theory course Fong Spivak programming compositionality
fast|Programming with effects handlers tutorial Pretnar pdf
length|medium

```

```unknown
fast|Seven Sketches in Compositionality PDF Spivak Fong arxiv
fast|David Spivak category theory for the sciences compositionality official PDF
fast|Category Theory Illustrated order theory monoids programming resource
fast|Learn You a Haskell monads tutorial official
fast|Haskell wikibook category theory monads
length|medium

```

<details><summary>💭 Thinking</summary>

**Organizing course topics**

I’m organizing the cited sections into a nine-lab progression, beginning with mathematical warmups and executable algebra, then covering effects, coeffects, equivalence, components, iteration, concurrency, metatheory, and implementation.

**Organized course topics**

**Searched 9 websites**

</details>

One design choice I would make explicit to students: **this is not really a “learn category theory first, then read the paper” course**. The paper uses categorical vocabulary to motivate effects/coeffects, but most of the machinery students must actually manipulate is monoids, functions/inverses, partial maps, equivalence relations, operational semantics, dependency graphs, and commutation. The paper itself says its preliminaries assume basic type theory/category theory mainly to fix notation before turning those ideas into runtime mechanisms. 

So I’d teach the mathematics just-in-time, with code as the running model.

```unknown
fast|Software Foundations Programming Language Foundations smallstep types official
fast|Practical Foundations for Programming Languages Harper official PDF
fast|Mathematics for Computer Science Lehman Leighton Meyer MIT free PDF monoids relations partial orders
fast|Matija Pretnar Introduction to Algebraic Effects and Handlers 2015 pdf
fast|QuickCheck original paper property based testing Claessen Hughes PDF
fast|Hypothesis stateful testing RuleBasedStateMachine docs
length|medium

```

<details><summary>💭 Thinking</summary>

**Gathering learning resources**

I’m looking for authoritative materials on operational semantics, programming-language metatheory, property-based testing, and applied category theory. I’ll balance rigorous textbooks with freely available resources, then connect them to the proposed course structure.

**Gathered learning resources**

</details>

```unknown
fast|site:softwarefoundations.cis.upenn.edu plf Smallstep Types Programming Language Foundations
fast|site:softwarefoundations.cis.upenn.edu Programming Language Foundations Smallstep
fast|site:softwarefoundations.cis.upenn.edu Programming Language Foundations Types
length|short

```

<details><summary>💭 Thinking</summary>

**Selecting foundational resources**

I’m assembling references for discrete mathematics, category theory, algebraic effects, coeffects, reversibility, concurrency, semantics, and property-based testing. I’m prioritizing accessible texts and official documentation, while marking advanced trace theory as optional.

**Designing the lab sequence**

I’m shaping the material into a practical progression: foundations, stateful and reversible effects, coeffects, components, equivalence, iteration, asynchronous failure, metatheory, and implementation. Each lab will pair paper sections with exercises, proof checkpoints, tests, and a cumulative project.

**Selected foundational resources and designed the lab sequence**

</details>

```unknown
open|https://softwarefoundations.cis.upenn.edu/plf-current/index.html
length|short

```

<details><summary>💭 Thinking</summary>

**Curating core references**

I’m narrowing the bibliography to accessible foundations: discrete mathematics, type systems, operational semantics, category theory, algebraic effects, and property-based testing. I’ll use freely available materials where possible and connect each resource to specific labs.

**Curating core references**

I’m narrowing the bibliography to accessible foundations: discrete mathematics, type systems, operational semantics, category theory, algebraic effects, and property-based testing. I’ll connect each resource to specific labs.

**Curated core references**

**Searched 14 websites**

</details>

I would make this an **8-lab “paper companion” course**, where students gradually construct a small but real plugin/runtime system. The important pedagogical device would be that every mathematical claim gets three representations:

$$
\text{paper notation}
\quad\longleftrightarrow\quad
\text{small executable model}
\quad\longleftrightarrow\quad
\text{property/test}
$$

So, for example,

$$
g(f(\gamma)) \simeq \gamma
$$

becomes both an equation they reason about and a property test that generates states, applies an effect, invokes its inverse, and checks recovery.

I would probably use **TypeScript**, because the paper's actual implementation is TypeScript and constructs such as closures, generators, promises, `Map`, `Symbol`, and proxies map unusually cleanly onto the theory. The paper explicitly gives a theory-to-runtime correspondence for `Γ∞`, effect callbacks, coeffect stores, fibers, target views and accumulators. fileciteturn0file0L3404-L3455 Python + Hypothesis would be my second choice if the primary objective were mathematical accessibility rather than correspondence with Cordis.

# The shape of the course

I'd have each lab contain five parts:

1. **Conceptual warm-up** — a tiny mathematical example students can calculate manually.
2. **Paper reading** — normally 4–8 pages rather than “read the next 20 pages.”
3. **Implementation** — add one mechanism to Mini-Cordis.
4. **Executable theorem** — turn one definition/theorem into tests.
5. **Counterexample exercise** — deliberately remove an assumption and make the theorem fail.

That fifth part is important. Students understand a theorem much better when they can say *why each hypothesis is there*.

The system at the end would look approximately like this:

```text
Runtime
 ├── Context
 │    ├── services
 │    ├── commands
 │    └── event handlers
 │
 ├── Components
 │    ├── requires
 │    ├── provides
 │    └── activate(ctx)
 │
 └── Fibers
      ├── target
      ├── committed dependencies
      ├── lifecycle state
      └── accumulated inverses
```

The capstone could genuinely host dynamically loadable CLI commands or agent tools.

---

# Lab 0 — The mathematical language of the paper

### Goal

Students should be able to read things like

$$
\Gamma\to\Gamma,\qquad
(f,g),\qquad
g\circ f=id,\qquad
\Sigma=(k:K)\rightharpoonup V_k
$$

without being slowed down by notation.

I would **not teach category theory broadly here**. Instead:

| Mathematical idea | Programming interpretation |
|---|---|
| Set/type | possible program values/states |
| Function | deterministic computation |
| Composition | sequential execution |
| Identity | do nothing |
| Monoid | composable operations + identity |
| Partial function | lookup that may fail |
| Relation | predicate relating two states |
| Equivalence relation | states considered indistinguishable |
| Directed graph | dependency relation |
| DAG/topological order | legal dependency ordering |

### Exercises

Students implement ordinary function composition and test associativity:

```ts
compose(f, compose(g, h))
===
compose(compose(f, g), h)
```

Then give them several structures and ask which form monoids:

```text
integers under +
strings under concatenation
arrays under concatenation
state transformations under composition
integers under subtraction
```

Have them produce one counterexample for every failed law.

Finally, implement a tiny transition system:

```ts
type State = ...
type Transition = (s: State) => State
```

and draw its state graph.

### Reading

For students whose discrete mathematics is weak, MIT's **Mathematics for Computer Science** is ideal: proof methods, relations, partial orders, directed graphs and state machines are precisely the background this paper needs. citeturn172110search0turn172110search6

For PL notation, selected material from Pierce's **Types and Programming Languages** is better than assigning a category-theory textbook. TAPL explicitly combines mathematical foundations with running implementations and exercises. citeturn396097search0

---

# Lab 1 — Effects are transformations, and transformations form a monoid

This begins §3.1.

The paper starts with context transformations

$$
\Gamma\to\Gamma
$$

and observes that they form a monoid under composition. Reversible effects pair a transformation with something that undoes it. fileciteturn0file0L295-L330

### Build

Start with an immutable context:

```ts
type Context = {
  values: Map<string, unknown>
}
```

Implement:

```ts
set(key, value)
delete(key)
increment(key)
append(key, value)
```

but initially as plain state transformations.

Then introduce:

```ts
type Inverse<S> = (state: S) => S

type Reversible<S> =
  (state: S) => [S, Inverse<S>]
```

### Exercises

**1. State-dependent inverses.**

Make this work:

```ts
const [s1, undo] = set("x", 42)(s0)

expect(undo(s1)).toEqual(s0)
```

The inverse should capture the previous value.

This exposes an important point from the paper: the inverse need only be correct at the state where the effect was performed; it need not be a globally defined two-sided inverse. fileciteturn0file0L487-L506

**2. Twisted composition.**

Implement the equivalent of

$$
(f_1,g_1)\circ(f_2,g_2)
=
(f_1\circ f_2,g_2\circ g_1).
$$

Students should explain why the second component reverses its order.

**3. Prove the monoid laws twice.**

First by hand for arbitrary `f`, `g`, `h`.

Then with property-based tests.

**4. Find a non-revertible effect.**

For example:

```text
print to terminal
send network packet
email somebody
```

Ask precisely where that effect sits relative to the system boundary.

That anticipates the paper's later distinction between reversible acquisition and irreversible emission. fileciteturn0file0L4053-L4069

### Theory reading

Paper §§3.1.1–3.1.2.

Then Wadler's **Monads for Functional Programming**, but with a very constrained question:

> How is sequencing being made explicit, and which part resembles our composition of context transformations?

Wadler develops monads specifically as a way of structuring effects such as state and exceptions. citeturn694875search36turn694875search2

I would **not** ask students to conclude that the paper's `Reversible` type “is a monad.” That isn't what the paper claims.

---

# Lab 2 — The accumulator: deriving teardown from setup

Now implement the thing that gives the paper much of its practical appeal.

The effect context contains current state plus accumulated recovery:

$$
\partial\Gamma=\Gamma\times(\Gamma\to\Gamma).
$$

The accumulator composes inverses so that recovery returns the context to its starting point. fileciteturn0file0L334-L345

### Build

```ts
class Scope<S> {
  private dispose: (s: S) => S = identity

  effect(effect: Reversible<S>): void
  recover(): void
}
```

Then use it for real operations:

```text
registerCommand()
subscribeEvent()
registerRoute()
startTimer()
provideService()
```

Each should perform an action and return its cleanup.

### Milestone 1

At this point students should have a small library where:

```ts
scope.registerCommand(...)
scope.subscribe(...)
scope.provide(...)
```

can all be torn down without an explicit plugin-level `deactivate()` implementation.

### Exercises

Give them a plugin:

```text
register A
register B
register C
```

and ask them to predict teardown order before running it.

Then make one inverse incorrect and have students identify which invariant breaks.

Then ask:

> Why does LIFO work even if A and B don't commute?

That leads directly toward the distinction between **ordinary reversal** and **selective removal**.

---

# Lab 3 — Coeffects: computations can require context too

This is where I'd introduce the effects/coeffects duality.

The paper's concise distinction is excellent:

> effects describe how computation modifies the environment; coeffects describe how it depends on the environment. fileciteturn0file0L265-L280

Before reading formal coeffects, I would have students compare:

```ts
State<S, A>  ≈ S -> [S, A]
Reader<R, A> ≈ R -> A
```

One says:

> my computation transforms an environment.

The other says:

> my computation requires an environment.

Then explain that the paper takes this broad duality and turns dependencies into runtime objects.

### Build

Implement:

```ts
type Key<T> = ...

class ServiceContext {
  get<T>(key: Key<T>): T
  set<T>(key: Key<T>, value: T): Dispose
}
```

The simplified coeffect context is the paper's finite dependent partial map:

$$
\Sigma=(k:K)\rightharpoonup V_k.
$$

fileciteturn0file0L994-L1017

Then define:

```ts
type Component = {
  requires: Set<Key<any>>
  provides: Set<Key<any>>
  activate(ctx: Context): ...
}
```

and literally implement satisfaction:

$$
\sigma\models d
\iff
\forall k\in d,\; k\in\operatorname{dom}(\sigma).
$$

fileciteturn0file0L1083-L1096

### Exercises

Build:

```text
Database
   provides db

Repository
   requires db
   provides repository

WebAPI
   requires repository
```

Students should observe:

```text
insert WebAPI
→ nothing

insert Repository
→ nothing

insert Database
→ Database
→ Repository
→ WebAPI
```

Then remove `Database`.

Everything should deactivate transitively.

Next:

```text
A requires b, provides a
B requires a, provides b
```

Ask students to explain why neither activates.

The paper later observes that dependency cycles simply leave components inactive and can be detected from declarations alone. fileciteturn0file0L4188-L4203

### Theory reading

Paper §§2.2, 3.2.1–3.2.2.

Then Petricek, Orchard & Mycroft's original **Coeffects** paper—not necessarily all of it. Its opening motivation is enough to establish coeffects as analysis of how computations rely on their environment. citeturn396097search6turn396097search7

For stronger students, read Milewski's comonad material after first understanding `Reader`; otherwise comonads can become an unnecessary conceptual detour.

---

# Lab 4 — Components, fibers, and operational semantics

This is the point where the course changes from “algebra library” into “small runtime.”

The paper's component is:

$$
(d,p,e)
$$

for dependencies, provisions and effect function. fileciteturn0file0L1622-L1642

A running instance becomes a **fiber**, which carries its own lifecycle state, accumulator and committed dependency resolution. fileciteturn0file0L1654-L1686

### Build

```ts
class Fiber {
  component
  state
  target
  committed
  dispose
}
```

Initially use only:

```text
INACTIVE
ACTIVE
```

Implement the paper's conceptual orchestration operations:

```text
insert
retire
remove
```

and lifecycle operations:

```text
reload
unload
```

### The important exercise: provider identity

Suppose:

```text
DatabaseV1 provides db
```

is replaced with:

```text
DatabaseV2 provides db
```

and both yield objects that happen to compare equal.

Consumers should still reload.

Students therefore need to record:

```ts
committed = {
  db: providerFiberId
}
```

rather than merely:

```ts
dbIsAvailable = true
```

That reproduces the reason the paper's target view records providers rather than values. fileciteturn0file0L1759-L1765

### Theory exercise

Give students one transition rule from the paper and ask them to translate it both directions:

```text
formal rule → TypeScript guard + mutation
```

and

```text
TypeScript implementation → inference rule
```

This is probably more valuable than having them merely memorize operational-semantics notation.

### Reading

Paper §§4.1–4.2.

For the general PL theory, either:

- Pierce, **TAPL**, especially the operational-semantics/type-system style, citeturn396097search0
- or Harper, **Practical Foundations for Programming Languages**, which is explicitly organized around formulating and analysing PL constructs precisely. citeturn172110search2

---

# Lab 5 — Independence, commutation and observational equivalence

I think this would be the intellectual centre of the lab.

First give two operations:

```text
A: add command "a"
B: add command "b"
```

They commute.

Then:

```text
A: prepend middleware A
B: prepend middleware B
```

They don't.

Have students build:

```ts
commutes(effectA, effectB, initialState)
```

and then a property-based version.

The paper's independence condition is stronger than simply testing that the two forward functions commute; inverses and their dependence on state matter too. fileciteturn0file0L710-L729 fileciteturn0file0L770-L815

### Key experiments

**Experiment A: independent effects.**

```text
load A
load B
remove A
```

must leave exactly B's contribution.

Then:

```text
load A
load B
remove B
remove A
```

and:

```text
load A
load B
remove A
remove B
```

should reach equivalent states.

**Experiment B: order-sensitive effects.**

Repeat with middleware.

Have students produce the smallest counterexample.

### Observational equivalence

Now introduce generated resource handles.

Suppose:

```text
initial allocator counter = 100

load plugin → receives handle 100
unload plugin

allocator counter = 101
```

Literal state equality has failed.

But perhaps none of the runtime's exposed operations can distinguish the recovered system from its original state.

Define:

```ts
observe(ctx): ObservableState
```

and switch from:

```ts
actual === initial
```

to:

```ts
observe(actual) === observe(initial)
```

The paper explicitly says physical state often cannot literally be restored and therefore reads recovery up to observational equivalence. fileciteturn0file0L1307-L1319

### Milestone 2

Students submit a **commutation matrix** for all primitives in their runtime:

| operation A | operation B | commute? | reason |
|---|---|---:|---|
| command registration | distinct command | yes | disjoint keys |
| command registration | same command | no | competing binding |
| event subscription | subscription | usually yes | set-like |
| middleware insertion | insertion | no | order observable |
| timer creation | command registration | yes | disjoint observations |

The paper proves that operations on distinct keys are independent and gives registration versus ordered middleware as representative examples. fileciteturn0file0L1466-L1498

This table forces students to think about **interfaces algebraically**.

---

# Lab 6 — Real lifecycles: iteration, asynchrony, failure and guarded withdrawal

Only now would I introduce the four-state lifecycle:

```text
INACTIVE
LOADING
ACTIVE
UNLOADING
```

The paper adds these because actual transitions are not necessarily atomic, immediate or infallible. fileciteturn0file0L1869-L1888

### Part A: effect iterators

Change:

```ts
activate(): Dispose
```

into approximately:

```ts
async *activate(): AsyncGenerator<Dispose>
```

A plugin can now:

```ts
yield registerCommand(...)
yield subscribeEvent(...)
yield await openResource(...)
```

Every yield becomes a rollback boundary.

This maps closely onto the paper's effect iterator, where each iteration yields state, inverse and optional continuation. fileciteturn0file0L1967-L2009

### Exercise: interrupt loading

Start loading:

```text
step 1 ✓
step 2 ✓
dependency disappears
step 3 should not begin
```

The component should roll back steps 1 and 2.

Then make step 3 already in flight. It must land before rollback.

Students now understand the otherwise rather abstract “inertia” discussion of §4.3.3. fileciteturn0file0L2095-L2114

### Part B: failure

Make:

```text
register route
open database
bind port ← fails
```

The first two effects must be recovered.

The final fiber state should be failed/inactive rather than partially installed.

That directly exercises the paper's failure semantics. fileciteturn0file0L2119-L2157

### Part C: safe provider withdrawal

This is the subtle exercise.

Suppose:

```text
Database
   ↑
Repository
```

The repository's teardown itself does:

```ts
await ctx.db.flush()
```

If Database destroys `db` before Repository's teardown, the runtime is wrong.

Students must therefore implement:

```text
1 provider becomes unavailable to *new* resolution
2 dependent begins teardown
3 dependent can still use committed old provider
4 wait until dependent finishes
5 provider finally performs its own recovery
```

That is precisely why the paper separates leaving from unloading and introduces its `relied` guard. fileciteturn0file0L1918-L1948

This lab usually produces the “oh, that's what all those lifecycle states are buying us” moment.

---

# Lab 7 — Turn the metatheory into a model checker

I would not ask most students to reproduce all the proofs in §4.4.

Instead, make them **operationalise the statements**.

Take a very small universe:

```text
≤ 4 fibers
≤ 4 dependency keys
≤ 3 operations per component
```

Enumerate or randomly generate scheduling choices.

Students implement invariant checks after every transition.

### Preservation

Check things like:

```text
every committed provider exists
every installed consumer's committed provider remains installed
providers are unique
```

This corresponds to the paper's registry well-formedness conditions and preservation theorem. fileciteturn0file0L2482-L2499

### Temporal composability

Pick a fiber episode, interleave operations from other fibers, unload it and test:

```text
final observable state
==
state produced by other fibers alone
```

That's the executable interpretation of recovery exactness. fileciteturn0file0L2640-L2658

### Spatial composability

Check:

```text
consumer begins only if dependencies exist

provider finishes unloading
only after every committed dependent finishes
```

Compare failures against Theorem 63. fileciteturn0file0L2782-L2817

### Progress

Generate acyclic dependency graphs and check that whenever the system isn't quiescent, *some legal lifecycle move exists*.

Then permit a dependency cycle and find a counterexample.

The paper's progress result depends explicitly on acyclicity and finite/bounded execution. fileciteturn0file0L2942-L2955

### Best assignment in the whole course

Give students switches:

```ts
CHECK_INDEPENDENCE = false
GUARD_PROVIDER_UNLOAD = false
USE_PROVIDER_IDENTITY = false
ROLLBACK_ON_FAILURE = false
```

Ask the model checker to automatically find the smallest counterexample to each theorem.

That turns assumptions from prose into observable necessity.

For a Python version, Hypothesis's stateful testing is particularly suited to this: it generates sequences of operations and supports invariants checked after every rule. citeturn172110search38turn172110search39

---

# Lab 8 — Confluence, reconciliation and hot replacement

The final theoretical idea is that dynamic history should eventually disappear.

The paper's confluence statement says, roughly, that after the system settles, its state should be the same as if its eventual active components had simply been assembled from scratch in dependency order. fileciteturn0file0L3088-L3098

### Exercise

Begin with the same desired final configuration and perform wildly different histories:

```text
History A
load db
load web
replace db
unload web
reload web
```

versus:

```text
History B
load replacement db
load web
```

Once quiescent:

```ts
observe(A) === observe(B)
```

should hold under the relevant assumptions.

Then deliberately add a non-independent effect and see the histories diverge.

### Build a tiny reconciler

Give the runtime:

```ts
reconcile([
  Database,
  Repository,
  WebAPI
])
```

Then change the declaration to:

```ts
reconcile([
  NewDatabase,
  Repository,
  WebAPI,
  Metrics
])
```

The runtime decides what to retire and insert.

This mirrors the paper's observation that the loader can reconcile incrementally because the final quiescent state depends on the final configuration rather than the exact route taken to get there. fileciteturn0file0L3771-L3789

### Final capstone

Each team makes the framework useful in one small domain:

```text
CLI plugin host
agent tool registry
HTTP route framework
chatbot plugin host
editor-command system
data-processing pipeline
```

Required features:

```text
dynamic insertion/removal
requires/provides dependencies
automatic cleanup
provider replacement
async loading
failure rollback
trace visualisation
```

And one 3–5 page report explaining three theorems in terms of their implementation.

---

# The theory reading ladder I would use

I would separate resources into **required**, **bridge**, and **deepening** rather than dumping a huge reading list on students.

## Mathematical / CS foundations

**MIT Mathematics for Computer Science** — selected chapters on proofs, relations/partial orders, directed graphs and state machines. This is enough discrete mathematics for almost everything in the calculus. citeturn172110search0turn172110search6

**Pierce, Types and Programming Languages** — use as the primary source for “what is a typing judgment / operational semantics / preservation / progress?” rather than assigning the whole book. Its emphasis is deliberately both theoretical and implementation-driven. citeturn396097search0

**Harper, Practical Foundations for Programming Languages** — optional alternative/deepening reference once the students reach §4 and the operational calculus. citeturn172110search2

I would probably explain preservation/progress once in a conventional typed lambda calculus *before* asking students to understand why the Cordis paper reuses those names for properties of its lifecycle system.

---

# Effects

Start applied:

**Wadler — “Monads for Functional Programming.”** It gives a programming-centred route from ordinary code to structured effects; no massive CT prerequisite is required. urlMonads for Functional Programminghttps://homepages.inf.ed.ac.uk/wadler/papers/marktoberdorf/baastad.pdf citeturn694875search36

Then:

**Pretnar — “An Introduction to Algebraic Effects and Handlers.”** This is useful for understanding the paper's discussion of algebraic effects and the distinction between effect operations and their interpretation. urlAlgebraic Effects and Handlers tutorialhttps://www.eff-lang.org/handlers-tutorial.pdf citeturn172110search37

For mathematically ambitious students:

**Moggi — “Notions of Computation and Monads.”** I would make this optional. The original paper is foundational but is much harder to learn from than Wadler. Moggi's publication page provides the original article. citeturn694875search4

**Plotkin & Power — “Notions of Computation Determine Monads.”** Particularly useful if you want students to see the algebraic-operation perspective the Cordis paper mentions. citeturn694875search40

---

# Coeffects

The obvious required companion is:

**Petricek, Orchard & Mycroft — “Coeffects: Unified Static Analysis of Context-Dependence.”** urlCoeffects paper and slideshttps://tomasp.net/academic/papers/coeffects/ citeturn396097search6

But I'd tell students explicitly:

> You do not need to master the full graded/comonadic theory to understand Mini-Cordis.

The Cordis paper reviews comonadic and graded coeffects but then reifies the dependency context at runtime. fileciteturn0file0L241-L264

A useful exercise is simply:

```text
Effect:
"What does my computation change?"

Coeffect:
"What must already be available for my computation to run?"
```

and have students classify examples.

---

# Category theory → programming

Here I would use **three resources in order**.

### 1. Category Theory Illustrated

For the first two labs, this is good for students intimidated by abstract notation. Its monoid section is highly concrete and exercise-oriented. citeturn886171search0

### 2. Bartosz Milewski — Category Theory for Programmers

This would be my main CT/programming bridge.

Assign only selected chapters:

```text
Category: The Essence of Composition
Types and Functions
Categories Great and Small
Kleisli Categories
Functors
Natural Transformations
Monads
Comonads
```

The freely available version is based on Milewski's original material and is licensed CC BY-SA. urlCategory Theory for Programmers source/PDFhttps://github.com/hmemcpy/milewski-ctfp-pdf citeturn694875search0

There is also a Python-oriented adaptation if the cohort isn't comfortable with Haskell. citeturn886171search10

### 3. Fong & Spivak — Seven Sketches in Compositionality

This isn't specifically a programming book. I'd use it because it teaches **why category theorists care about composition in the first place**.

The opening chapters deliberately build categorical ideas out of applied compositional examples, and the text assumes no prior category theory. citeturn886171academia35turn886171search36

MIT's Applied Category Theory course pairs the chapters with lecture material as well. citeturn886171search1

I would particularly use it to prevent a common failure mode where students think CT means “functors and monads are strange programming patterns.” The more important idea for this paper is:

> Find the notion of composition; identify the identity; identify which maps preserve the composition; then reason structurally rather than case-by-case.

---

# A category-theory map specifically for this paper

I might actually give students this on one sheet:

| Paper construct | Maths lens | Programming lens |
|---|---|---|
| `Γ → Γ` effects | endomorphisms | state mutations |
| composition of effects | monoid | sequential execution |
| reversed inverse composition | opposite monoid | cleanup stack |
| `track` preserving composition | monoid homomorphism | instrumentation doesn't change sequencing semantics |
| `EΓ` | state-dependent reversible arrows | operation returns cleanup closure |
| `Σ` | dependent partial map | typed service registry |
| coeffects | contextual requirements | dependency injection |
| `≃` | equivalence / quotient | ignore unobservable representation |
| independent effects | commuting morphisms | can safely reorder/unload independently |
| dependency relation | partial-order-like structure | provider graph |
| trace equivalence | commuting independent actions | scheduler interleavings |
| `Γ∞ = μΓ...` | recursive/fixed-point type | nested contexts |
| confluence | unique normal form | same final system despite different update history |

This is, in my view, the correct amount of CT for this particular paper.

---

# Two deeper readings I'd make optional

For students who want to understand **why independence and reversal are mathematically interesting**, the paper's own related-work choices are very good.

**Heunen, Kaarsgaard & Karvonen — “Reversible Effects as Inverse Arrows.”** This is substantially more categorical than the Cordis construction: it studies reversible side effects through dagger/inverse arrows and global reversibility. That contrast is useful because Cordis deliberately asks for much less—local one-sided inverses supplied at runtime. citeturn396097academia38turn396097search37

For scheduling/interleavings, introduce **Mazurkiewicz trace theory** conceptually: histories differing only by swapping independent adjacent actions should be considered equivalent. The Cordis paper explicitly connects its independence condition to trace theory in exactly this sense. fileciteturn0file0L2627-L2636

You don't need students reading an entire trace-theory monograph. I'd teach the basic idea with strings:

$$
abc \sim bac
$$

whenever `a` and `b` are independent.

That single idea provides a very good conceptual route into the temporal composability and confluence proofs.

---

# What I would assess

I wouldn't grade this primarily by “does their plugin framework work?”

I'd split marks roughly:

| Component | Weight |
|---|---:|
| Runtime implementation | 35% |
| Property/model-based tests | 25% |
| Mathematical explanations | 20% |
| Counterexamples when assumptions are removed | 15% |
| Final system/demo | 5% |

The counterexamples deserve substantial weight.

For example, a good submission for the independence lab shouldn't merely say:

> “These two effects aren't independent.”

It should produce:

```text
γ0
↓ A
γ1
↓ B
γ2
↓ undo(A)
γ3
```

and another execution showing concretely that

$$
\gamma_3\not\simeq B(\gamma_0).
$$

That's the bridge between a programmer who has *used* rollback and someone who understands what the theorem is saying.

---

# The milestone structure

I would collapse the eight labs into four major checkpoints:

**Milestone A — Reversible computation.** Students have state transformers, state-dependent inverses, composition and automatic LIFO recovery.

**Milestone B — Dynamic composition.** Students have a typed service context, `requires`/`provides`, fibers, target views and automatic reactive activation/deactivation.

**Milestone C — Safe interleaving.** They have observational equivalence, independence tests, async transitions, failure rollback and dependency-safe withdrawal.

**Milestone D — Metatheoretic runtime.** They have a state-machine/model-testing harness that checks preservation, recovery, ordering, progress and confluence on small generated systems, followed by the useful plugin-host capstone.

The last milestone is the part I'd be most reluctant to omit. It changes the exercise from **“we reimplemented a framework described in a paper”** into **“we used a running system to understand why the definitions and hypotheses in the paper have the shapes they do.”**

If this were a 10–12 week university module, I'd actually spend **about 60% of the contact time on Labs 1–6 and 40% on Labs 7–8**. The early code is straightforward; the real learning happens when students start asking why an accumulator is insufficient for arbitrary interleaving, why committed views must survive teardown, why equality is too strong, why commutation matters, and why acyclicity enters the progress theorem. Those are exactly the places where the paper moves from an interesting plugin design to a piece of programming-languages theory.


---

> Write the lab textbook as markdown + pdf. Use the material you gathered, but rewrite and restructure it so it actually turns into a real pedagogical lab handbook/ textbook.  structured and pedagogical: after writing the first draft, go back and make sure each definition and term worth defining or introducing is properly motivated and defined and then applied in a few examples. Pretend you are a student reading the text and trying to make sense of it, and then rewrite it.  Make sure to introduce concepts by motivation, definition, then concrete worked examples, then exercises, and potentially counterexample. Use full prose paragraphs and lists and pseudocode and maths and api signatures and diagrams. Use callouts for expanding on fundamentals or side topics.

<details><summary>💭 Thinking</summary>

**Planning textbook deliverables**

I’m preparing a beginner-friendly, notebook-style lab textbook about neighbor search and approximate nearest neighbors. I’ll use the uploaded paper and draft, verify useful resources, then create both Markdown and PDF files with exercises, code, diagrams, and references.

**Planned textbook deliverables**

</details>

I’ll turn the outline into a self-contained student handbook, audit its pedagogy and definitions, then produce and inspect both Markdown and typeset PDF versions.

```unknown
bash -lc cat /home/oai/skills/pdfs/SKILL.md && printf '\n---MARKDOWN INPUT HEAD---\n' && sed -n '1,120p' '/mnt/data/Pasted markdown(20260820-220349).md'
```

```unknown
bash -lc sed -n '1,260p' /home/oai/skills/pdfs/tasks/create.md && printf '\n---CONVERT---\n' && sed -n '1,260p' /home/oai/skills/pdfs/tasks/convert.md
```

<details><summary>💭 Thinking</summary>

**Building the textbook**

I’m shaping the material into a coherent first draft with chapters, notebooks, visual explanations, exercises, projects, and references. I’ll keep the mathematics accessible while connecting theory to practical neighbor-search systems and reproducible experiments.

**Built the textbook**

**Designing lab sequence**

I’m organizing eight core labs plus onboarding, covering executable semantics, dependencies, fibers, parallel composition, resilience, model checking, confluence, and hot replacement. Each lab will include theory, implementation, tests, exercises, counterexamples, deliverables, and readings.

**Rendering the materials**

I’m keeping diagrams in portable Markdown-friendly form and using math notation that survives PDF conversion. I’ll package the source with a consistent visual style, then inspect the rendered PDF for layout problems and revise as needed.

**Rendered the materials**

</details>

```unknown
bash -lc command -v pandoc; command -v xelatex; command -v latexmk; command -v dot; fc-list | head -20
```

<details><summary>💭 Thinking</summary>

**Read PDF, Markdown, creation, and conversion guidelines**

</details>

```unknown
bash -lc mkdir -p /mnt/data/work/paper_renders && python /home/oai/skills/pdfs/scripts/render_pdf.py /mnt/data/deepseek-category-theory.pdf --out_dir /mnt/data/work/paper_renders --dpi 110 >/tmp/render_paper.log 2>&1 && tail -20 /tmp/render_paper.log && ls /mnt/data/work/paper_renders | head
```

```unknown
bash -lc python - <<'PY'
from PIL import Image, ImageOps, ImageDraw
from pathlib import Path
pages=[9,10,11,12,13,14,15,16,17,18,19,20,22,23,24,25,28,29,30,31,33,34,35,36,37,38,43,45,46,47,49,52,54,55,56,57,58,59,60,61]
imgs=[]
for p in pages:
    im=Image.open(f'/mnt/data/work/paper_renders/page-{p:02d}.png').convert('RGB')
    im.thumbnail((260,360))
    canvas=Image.new('RGB',(280,390),'white')
    x=(280-im.width)//2; y=20
    canvas.paste(im,(x,y))
    d=ImageDraw.Draw(canvas)
    d.text((10,3),f'p. {p}',fill='black')
    imgs.append(canvas)
cols=5; rows=(len(imgs)+cols-1)//cols
sheet=Image.new('RGB',(cols*280,rows*390),(220,220,220))
for i,im in enumerate(imgs): sheet.paste(im,((i%cols)*280,(i//cols)*390))
sheet.save('/mnt/data/work/paper_contact.png')
PY
```

<details><summary>💭 Thinking</summary>

**Rendered and analyzed relevant PDF pages via contact sheet**

</details>

```json
{"search_query":[{"q":"site:ocw.mit.edu Mathematics for Computer Science readings official"},{"q":"site:mitpress.mit.edu Types and Programming Languages Pierce official"},{"q":"site:cs.cmu.edu Practical Foundations for Programming Languages Robert Harper official"},{"q":"site:homepages.inf.ed.ac.uk Wadler Monads for Functional Programming PDF"}],"response_length":"long"}
```

```json
{"search_query":[{"q":"site:homepages.inf.ed.ac.uk Pretnar introduction algebraic effects handlers pdf"},{"q":"site:tomasp.net coeffects unified static analysis context dependence"},{"q":"site:arxiv.org Seven Sketches in Compositionality Fong Spivak"},{"q":"site:github.com hmemcpy milewski ctfp pdf"}],"response_length":"long"}
```

```json
{"search_query":[{"q":"\"An Introduction to Algebraic Effects and Handlers\" Pretnar official PDF"},{"q":"site:arxiv.org/abs/1803.05316 Seven Sketches Compositionality"},{"q":"Category Theory Illustrated monoids official"},{"q":"fast-check official documentation property based testing TypeScript"}],"response_length":"long"}
```

```json
{"search_query":[{"q":"site:typescriptlang.org/docs handbook generics official TypeScript"},{"q":"site:typescriptlang.org/docs async generators TypeScript official"},{"q":"site:vitest.dev guide official testing TypeScript"},{"q":"site:hypothesis.readthedocs.io stateful testing official"}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Authoring textbook content**

I’m now expanding the outline into a substantial first draft, balancing readable explanations with runnable TypeScript examples, formal reasoning, testing strategies, exercises, and a curated resource list.

**Drafting full content**

I’m targeting a substantial first draft rather than a brief outline: about 25,000–30,000 words, with runnable code, careful proofs, visual explanations, labs, and appendices that make the material usable as a semester-style handbook.

**Authored and drafted full textbook content**

</details>

Each concept will follow motivation, definition, worked trace, executable law, implementation, and counterexample; I’ll explicitly distinguish state-local inverses from globally invertible functions.

<details><summary>💭 Thinking</summary>

**Searched 4 websites**

</details>

```unknown
bash -lc fc-match 'Libertinus Serif'; fc-match 'Inter'; fc-match 'DejaVu Sans Mono'
```

```unknown
bash -lc sed -n '1,240p' /home/oai/skills/pdfs/scripts/md_to_pdf.py
```

```unknown
bash -lc rm -rf /mnt/data/work/handbook && mkdir -p /mnt/data/work/handbook/chapters /mnt/data/work/handbook/build
```

```unknown
bash -lc cat > /mnt/data/work/handbook/chapters/00-front.md <<'EOF'
---
title: "Mini-Cordis"
subtitle: "A Laboratory Handbook for Revertible Effects, Reactive Coeffects, and Dynamic Composition"
author: "A paper companion to *A Programming Paradigm for Spatiotemporal Composability*"
date: "First edition, August 2026"
lang: en-GB
documentclass: book
classoption:
  - oneside
  - openany
toc: true
toc-depth: 3
numbersections: true
geometry:
  - margin=25mm
fontsize: 10pt
mainfont: "Noto Serif"
sansfont: "Inter"
monofont: "DejaVu Sans Mono"
colorlinks: true
linkcolor: NavyBlue
urlcolor: MidnightBlue
header-includes:
  - |
    \usepackage[most]{tcolorbox}
    \usepackage{booktabs}
    \usepackage{longtable}
    \usepackage{array}
    \usepackage{microtype}
    \usepackage{enumitem}
    \usepackage{xcolor}
    \usepackage{fancyhdr}
    \usepackage{listings}
    \usepackage{amsmath,amssymb,mathtools}
    \usepackage{tikz}
    \usetikzlibrary{arrows.meta,positioning,shapes.multipart,fit}
    \definecolor{HandbookBlue}{HTML}{1F4E79}
    \definecolor{HandbookLight}{HTML}{EEF5FB}
    \definecolor{HandbookRule}{HTML}{7A9BB8}
    \definecolor{CodeBack}{HTML}{F7F7F7}
    \definecolor{CodeRule}{HTML}{D0D0D0}
    \setlist{nosep,leftmargin=*}
    \setlength{\parskip}{0.55em}
    \setlength{\parindent}{0pt}
    \pagestyle{fancy}
    \fancyhf{}
    \fancyhead[LE,RO]{\small\sffamily Mini-Cordis Laboratory Handbook}
    \fancyhead[RE,LO]{\small\sffamily\nouppercase{\leftmark}}
    \fancyfoot[C]{\thepage}
    \renewcommand{\headrulewidth}{0.3pt}
    \renewenvironment{quote}
      {\begin{tcolorbox}[enhanced,breakable,colback=HandbookLight,colframe=HandbookRule,boxrule=0.6pt,arc=1mm,left=2mm,right=2mm,top=1.5mm,bottom=1.5mm]}
      {\end{tcolorbox}}
    \lstset{
      basicstyle=\ttfamily\small,
      backgroundcolor=\color{CodeBack},
      frame=single,
      rulecolor=\color{CodeRule},
      breaklines=true,
      breakatwhitespace=false,
      columns=fullflexible,
      keepspaces=true,
      showstringspaces=false,
      tabsize=2,
      xleftmargin=0.5em,
      xrightmargin=0.5em,
      aboveskip=0.8em,
      belowskip=0.8em
    }
    \renewcommand{\arraystretch}{1.18}
---

# Preface {-}

Modern software increasingly changes while it is running. Extensions are installed and removed, providers are replaced, configuration is reconciled, agent tools appear and disappear, and long-lived services must keep working while their internal composition changes. The engineering challenge is not merely to *load* code. It is to make the change behave as though the component had always been present - or had never been present - without leaving leaked resources, stale dependencies, or schedule-dependent state behind.

The course paper, *A Programming Paradigm for Spatiotemporal Composability*, gives this problem two dimensions:

- **Temporal composability:** when a component is removed, the changes attributable to it can be withdrawn without also erasing the contributions of components that remain.
- **Spatial composability:** components declare what they require and provide, and the runtime reacts when those dependency relationships change.

The paper develops a formal account using **revertible effects**, **reactive coeffects**, a unified context, and an operational calculus of component lifecycles. This handbook turns that account into a sequence of laboratories. You will build a small runtime called **Mini-Cordis**, use it for a real plugin or tool system, and repeatedly translate between three views of the same idea:

$$
\text{formal statement}
\quad\longleftrightarrow\quad
\text{executable model}
\quad\longleftrightarrow\quad
\text{property or counterexample}.
$$

For example, the recovery condition

$$
g(f(\gamma)) \simeq \gamma
$$

will not remain a line of notation. You will implement `f`, capture `g`, generate many states $\gamma$, and test whether recovery holds. Later, you will deliberately weaken the assumptions and ask a model checker to find the smallest execution that breaks the property.

This is not a reimplementation guide for the production Cordis framework. Mini-Cordis is intentionally smaller. It exists to make the paper's mathematical structures visible, manipulable, and falsifiable.

> **How to read this handbook.** Each important concept is introduced in the same order: a practical problem motivates it; a definition fixes its meaning; a worked example traces the definition; an implementation gives it operational form; exercises extend it; and a counterexample shows what fails when a condition is removed. Do not skip the counterexamples. They explain why the definitions have the shapes they do.

## Intended audience {-}

The handbook is suitable for advanced undergraduates, master's students, or experienced programmers studying programming-languages theory. You should be comfortable with:

- TypeScript or another typed general-purpose language;
- unit testing and asynchronous programming;
- elementary sets, functions, and graphs;
- reading short mathematical proofs, or being willing to learn how.

No prior category theory is assumed. The category-theoretic material is introduced only where it clarifies a programming construction. The course does not require students to derive monads or comonads from first principles.

## Learning outcomes {-}

By the end of the sequence, you should be able to:

1. Model stateful operations as context transformations and explain why they form a monoid under composition.
2. Distinguish a global inverse from a state-dependent, witnessed inverse.
3. Derive composite teardown behaviour from atomic inverse operations.
4. Model dependencies as coeffects and implement reactive activation and deactivation.
5. Explain the roles of components, fibers, registries, target views, and committed views.
6. Determine when two effects are independent, and construct a counterexample when they are not.
7. Replace literal state equality with a justified observational equivalence.
8. Implement asynchronous loading, failure rollback, and dependency-safe withdrawal.
9. State preservation, temporal composability, spatial composability, progress, and confluence as executable properties.
10. Build a small useful system whose composition can change at runtime without a process restart.

## Course architecture {-}

The handbook contains an orientation chapter, a mathematical onboarding lab, and eight implementation labs. Four milestones divide the work.

| Milestone | Labs | Result |
|---|---:|---|
| A. Reversible computation | 0-2 | State transformations, witnessed inverses, composition, and automatic LIFO recovery |
| B. Dynamic composition | 3-4 | Typed dependencies, reactive activation, components, fibers, and provider-aware target views |
| C. Safe interleaving | 5-6 | Independence, observational equivalence, asynchronous transitions, failure rollback, and guarded withdrawal |
| D. Executable metatheory | 7-8 | Model checking, progress, confluence, reconciliation, hot replacement, and a capstone runtime |

A typical twelve-week schedule is:

| Week | Topic | Main submission |
|---:|---|---|
| 1 | Orientation and Lab 0 | Notation exercises and transition-system warm-up |
| 2 | Lab 1 | Pure reversible transformations |
| 3 | Lab 2 | Effect scope and resource primitives |
| 4 | Lab 3 | Reactive service context |
| 5 | Lab 4 | Component and fiber lifecycle |
| 6-7 | Lab 5 | Independence report and commutation matrix |
| 8-9 | Lab 6 | Asynchronous lifecycle and safe withdrawal |
| 10 | Lab 7 | Model checker and minimized counterexamples |
| 11 | Lab 8 | Reconciler and hot replacement |
| 12 | Capstone | Demonstration and theory report |

## The system you will build {-}

At the end of the core labs, Mini-Cordis has the following shape:

```text
+-------------------------------------------------------------+
| Runtime                                                     |
|                                                             |
|  +---------------- Context -------------------------------+  |
|  | services | commands | event handlers | other resources |  |
|  +---------------------------------------------------------+  |
|                                                             |
|  +--------------- Component definitions ------------------+  |
|  | requires | provides | activate(context)                 |  |
|  +---------------------------------------------------------+  |
|                                                             |
|  +---------------- Running fibers -------------------------+  |
|  | lifecycle state                                         |  |
|  | target provider view                                    |  |
|  | committed provider view                                 |  |
|  | accumulated inverse / disposer                          |  |
|  +---------------------------------------------------------+  |
+-------------------------------------------------------------+
```

A component may register commands, subscribe to events, provide services, create child components, and acquire other runtime resources. Every context-mediated mutation yields an inverse. The fiber stores those inverses. Dependencies determine whether a fiber should be active and against which providers it should run.

## Two implementation models {-}

The paper gives a mathematical model in which an effect maps a context state to a new state and an inverse function. Production runtimes often mutate objects in place and return cleanup closures. This handbook deliberately uses both models.

**Pure model:** useful for equations, proofs, property tests, and model checking.

```ts
type Endo<S> = (state: S) => S;
type Reversible<S> = (state: S) => readonly [S, Endo<S>];
```

**Imperative model:** useful for actual commands, timers, sockets, and event listeners.

```ts
type Awaitable<T> = T | Promise<T>;
type Dispose = () => Awaitable<void>;
type EffectStep = () => Awaitable<Dispose>;
```

The two are not identical implementations. They represent the same design discipline: each context-changing operation makes its recovery behaviour local and explicit.

> **Fundamentals: denotation versus realisation.** A *denotation* says what an operation means: a successor state paired with a way to undo it. A *realisation* says how a host runtime carries that meaning out: immutable copies, in-place mutation, handles, closures, or derived child contexts. Keeping these separate prevents accidental arguments from JavaScript object identity from being mistaken for mathematical laws.

## Repository convention {-}

The examples assume a TypeScript project with this layout:

```text
mini-cordis/
  package.json
  tsconfig.json
  src/
    core/
      algebra.ts
      context.ts
      effects.ts
      coeffects.ts
      component.ts
      runtime.ts
      model.ts
    examples/
    index.ts
  test/
    unit/
    properties/
    model/
  lab-notes/
```

A minimal toolchain is:

```json
{
  "scripts": {
    "test": "vitest run",
    "test:watch": "vitest",
    "typecheck": "tsc --noEmit"
  },
  "devDependencies": {
    "fast-check": "latest",
    "typescript": "latest",
    "vitest": "latest"
  }
}
```

Your institution may pin versions. The textbook does not depend on a specific minor release.

## Conventions used in the text {-}

- $\Gamma$ denotes the type or set of complete context states.
- $\gamma,\delta,\varepsilon \in \Gamma$ denote individual states.
- Function composition is written in mathematical order: $(f\circ g)(x)=f(g(x))$. The right-hand function runs first.
- $\Sigma$ denotes the dependency or coeffect context.
- $K$ is the set of dependency keys, and $V_k$ is the value type associated with key $k$.
- $\simeq$ denotes an observational equivalence chosen for the system.
- `Dispose` denotes an imperative cleanup operation.
- `FiberId` identifies a running component instance, not merely a component definition.
- **Core exercise** means required work. **Extension** means a deeper or more applied variant. **Counterexample clinic** means the runtime is expected to fail in a controlled, explanatory way.

## Assessment model {-}

A balanced marking scheme is:

| Evidence | Weight |
|---|---:|
| Runtime implementation | 35% |
| Property-based and model-based tests | 25% |
| Mathematical explanations | 20% |
| Counterexamples and failure analysis | 15% |
| Final demonstration | 5% |

A correct-looking runtime with no properties is incomplete. A proof sketch with no executable connection is also incomplete. The course is about moving between the two.

## Primary source and scope {-}

The definitions and theorem names in this handbook follow the supplied paper closely, especially Sections 3-5. The examples, API designs, exercises, simplified proofs, and Mini-Cordis implementation are pedagogical adaptations. Where the handbook simplifies a condition, it says so explicitly.

The paper assumes familiarity with basic type theory and category theory. This handbook instead introduces only the needed material immediately before use. A structured reading pathway appears in Appendix D.

EOF
```

```unknown
bash -lc cat > /mnt/data/work/handbook/chapters/01-orientation-lab0.md <<'EOF'
# Orientation: Why Dynamic Composition Is Hard

Before introducing effects, coeffects, or category theory, begin with a mundane plugin host.

Suppose an application can load a `metrics` plugin. During activation it:

1. registers a command named `metrics`;
2. subscribes to request events;
3. starts a periodic timer;
4. obtains a database service;
5. creates an HTTP route;
6. installs a child plugin for exporting traces.

Loading is easy because every API already knows how to create something. Removal is harder. The host must know every action the plugin took, apply the corresponding cleanup, respect dependencies, handle operations that are still in flight, and avoid damaging unrelated plugins.

A conventional plugin interface often separates construction and destruction:

```ts
interface ConventionalPlugin {
  activate(host: Host): Promise<void>;
  deactivate(host: Host): Promise<void>;
}
```

This interface permits correct implementations, but it does not make correctness structural. `activate` can register six resources while `deactivate` remembers five. The omission may remain invisible until a reload or test suite runs repeatedly.

A dependency problem appears at the same time. Imagine:

```text
Database  --->  Repository  --->  Web API
 provider      consumer/provider   consumer
```

If the database provider leaves, the repository must stop. The web API must stop before the repository. During repository teardown, the repository may still need the database to flush pending work. Removing the database binding too early breaks cleanup; waiting without a dependency discipline may deadlock.

The paper calls these two problems **temporal** and **spatial** composability.

## Temporal composability

**Motivation.** A component contributes changes over time. Removal should withdraw exactly those changes.

**Definition.** A runtime has *temporal composability* at a chosen component boundary when the effects attributable to a component can be recovered on removal while the contributions of components that remain continue to hold, up to the system's chosen observational equivalence.

The phrase “up to observational equivalence” matters. Closing a file descriptor need not restore the kernel's internal allocation counter. It must restore the behaviour that the system promises observers.

**Example.** Plugin A registers command `a`; plugin B registers command `b`. After loading A and B, removing A should leave command `b` available and command `a` absent.

```text
initial:          {}
load A:           {a}
load B:           {a, b}
unload A:         {b}
```

**Counterexample.** If the host takes a snapshot before loading A and restores the whole snapshot when A leaves, B's later contribution disappears too.

```text
initial snapshot: {}
load A:           {a}
load B:           {a, b}
restore snapshot: {}        <-- B was erased
```

This is rollback, but not compositional rollback.

## Spatial composability

**Motivation.** Components occupy positions in a dependency structure. A consumer should run only while its declared requirements are satisfied, and a provider change should be propagated to the relevant consumers.

**Definition.** A runtime has *spatial composability* when components declare their environmental requirements and provisions, the runtime resolves those declarations, and lifecycle transitions react to changes in the resulting dependency topology.

**Example.** `WebAPI` declares `Repository`; `Repository` declares `Database`. Inserting the components in any order should eventually activate them in dependency order once all requirements exist.

```text
insert WebAPI       inactive: Repository missing
insert Repository   inactive: Database missing
insert Database     Database -> Repository -> WebAPI activate
```

**Counterexample.** If `WebAPI` simply calls a global service locator at arbitrary points, its dependency is implicit. Replacing the provider does not necessarily reinitialise the consumer, and accessing an absent provider becomes an ad hoc runtime error.

## Why the two dimensions interact

Temporal and spatial composability are orthogonal, but a real runtime needs both.

- Perfect cleanup without dependency management can tear down a provider before its consumers.
- Perfect dependency tracking without cleanup can deactivate consumers while leaving their commands, routes, or listeners installed.

Mini-Cordis therefore treats every component as a combination of:

1. a set of keys it **requires**;
2. a set of keys it may **provide**;
3. an effect program that installs its contribution and yields the means to withdraw it.

That shape will later become the paper's component triple $(d,p,e)$.

> **Side topic: processes already provide a coarse version.** An operating system can reclaim memory and file descriptors when a whole process exits, and a service orchestrator can restart or replace whole services. The paper's question is what happens when the desired composition boundary is smaller than a process: a plugin, tool, route package, agent capability, or in-process service.

## A running scenario

Most worked examples use a small command-and-service host.

```text
Clock component
  provides: clock

Notes component
  provides: notes
  effects: registers command "note:add"

DailySummary component
  requires: clock, notes
  effects: registers command "summary"
```

When `clock` and `notes` are available, `DailySummary` activates. If `notes` is removed, `DailySummary` deactivates before `notes` finishes withdrawing its service. Reinstalling a new notes provider reactivates it against the new provider identity.

This system is useful enough to demonstrate dynamic tools, but small enough to represent the complete state in a test.

# Lab 0: The Mathematical Language of the Runtime

## Purpose

The paper uses ordinary mathematical structures densely. Lab 0 makes the notation executable before any category-theoretic terminology is introduced.

By the end of the lab, you should be able to read:

$$
\Gamma\to\Gamma,
\qquad
(f,g),
\qquad
g\circ f=\mathrm{id}_{\Gamma},
\qquad
\Sigma=(k:K)\rightharpoonup V_k
$$

and translate each expression into a programming statement.

## Learning outcomes

After this lab you can:

- distinguish a type of states from an individual state;
- compose functions in the paper's order;
- state and test the laws of a monoid;
- work with partial functions and finite maps;
- define relations and equivalence relations;
- read a small-step transition rule;
- model a dependency graph and identify a cycle.

## 0.1 Types, values, and contexts

### Motivation

A runtime touches many pieces of state: services, commands, listeners, lifecycle fields, and counters. Reasoning about one mutation at a time requires a name for the *whole state space* and names for individual states within it.

### Definition: type or set of states

A **type** describes the values a program can manipulate. In a set-theoretic reading, a type can be treated as a set of possible values.

We write $\Gamma$ for the type of complete context states. An individual state is written $\gamma\in\Gamma$.

A first model might be:

```ts
export type ContextState = Readonly<{
  values: ReadonlyMap<string, unknown>;
}>;
```

Here `ContextState` plays the role of $\Gamma$. A particular object such as

```ts
const gamma0: ContextState = {
  values: new Map([["count", 0]])
};
```

plays the role of $\gamma_0$.

> **Common mistake: $\Gamma$ is not a global variable.** It names the *kind of thing* a context state is, not one current mutable object. The current object is a value such as $\gamma$.

### Worked example

Let $\Gamma$ be the set of integer-valued maps over keys `x` and `y`.

```text
gamma_0 = {x: 2, y: 5}
gamma_1 = {x: 3, y: 5}
```

Both states belong to $\Gamma$. The operation “increment x” is a function from $\Gamma$ back to $\Gamma$.

## 0.2 Functions and composition

### Motivation

To say that one operation runs after another, the mathematics needs a sequencing operation that does not depend on the specific contents of the functions.

### Definition: function

A function $f:X\to Y$ maps every input in $X$ to exactly one output in $Y$.

A **state transformation** is a function $f:\Gamma\to\Gamma$.

```ts
type Endo<S> = (state: S) => S;
```

The name `Endo` abbreviates **endomorphism**, a function from an object to itself.

### Definition: composition

Given $g:X\to Y$ and $f:Y\to Z$, their composition is

$$
f\circ g:X\to Z,
\qquad
(f\circ g)(x)=f(g(x)).
$$

The right-hand function runs first.

```ts
export function compose<A, B, C>(
  f: (value: B) => C,
  g: (value: A) => B
): (value: A) => C {
  return (value) => f(g(value));
}
```

> **Fundamentals: reading order.** In ordinary prose we may say “do `g`, then `f`.” Mathematics writes the combined function as $f\circ g$. When tracing a composite, start at the argument on the right and move left.

### Worked example

Let:

```ts
const incrementX: Endo<State> = (s) => ({ ...s, x: s.x + 1 });
const doubleX: Endo<State> = (s) => ({ ...s, x: 2 * s.x });
```

At `{x: 3}`:

```text
(doubleX o incrementX)({x: 3})
= doubleX({x: 4})
= {x: 8}
```

but:

```text
(incrementX o doubleX)({x: 3})
= incrementX({x: 6})
= {x: 7}
```

The functions do not commute. Composition is associative, but not generally commutative.

## 0.3 Identity and monoids

### Motivation

A cleanup accumulator begins empty. Sequential effects can be grouped in different ways. We therefore need a structure with a no-op and associative combination.

### Definition: identity function

The identity function on $X$ returns its argument unchanged:

$$
\mathrm{id}_X(x)=x.
$$

```ts
export const identity = <T>(value: T): T => value;
```

### Definition: monoid

A **monoid** consists of:

1. a set $M$;
2. a binary operation $\star:M\times M\to M$;
3. an identity element $e\in M$;

such that for all $a,b,c\in M$:

$$
(a\star b)\star c=a\star(b\star c)
$$

and

$$
e\star a=a=a\star e.
$$

The first law is **associativity**. The second pair are the **unit laws**.

### Worked examples

| Carrier | Operation | Identity | Monoid? |
|---|---|---|---|
| integers | addition | $0$ | yes |
| strings | concatenation | empty string | yes |
| arrays | concatenation | empty array | yes |
| $\Gamma\to\Gamma$ | composition | $\mathrm{id}_\Gamma$ | yes |
| integers | subtraction | $0$ | no: subtraction is not associative |

State transformations form a monoid because composing two transformations gives another transformation, function composition is associative, and the identity function changes nothing.

### Counterexample: subtraction

Take $a=10$, $b=3$, $c=2$.

$$
(10-3)-2=5,
\qquad
10-(3-2)=9.
$$

The grouping changes the result, so subtraction cannot be the monoid operation.

> **Category theory connection.** The paper needs very little category theory at first. A category generalises typed composition and identities. The transformations $\Gamma\to\Gamma$ are the endomorphisms of one object $\Gamma$, and those endomorphisms form a monoid. This is the exact algebraic fact used by the effect construction.

## 0.4 Partial functions and finite maps

### Motivation

A service lookup can fail because a key is absent. Modelling it as an ordinary total function that silently returns nonsense would hide the precondition.

### Definition: partial function

A **partial function** $f:X\rightharpoonup Y$ maps some, but not necessarily all, elements of $X$ to values in $Y$.

A finite `Map` is a common implementation:

```ts
const services = new Map<symbol, unknown>();
const result = services.get(key); // value or undefined
```

An equivalent total encoding uses an option type:

```ts
type Option<T> =
  | { readonly tag: "some"; readonly value: T }
  | { readonly tag: "none" };
```

Then a partial function $X\rightharpoonup Y$ is represented as a total function $X\to\mathrm{Option}(Y)$.

### Definition: dependent partial map

The paper's coeffect context is written

$$
\Sigma=(k:K)\rightharpoonup V_k.
$$

This means that every key $k$ has an associated value type $V_k$. A database key maps to a database value; a clock key maps to a clock value. TypeScript can approximate this relation with generic keys:

```ts
declare const keyType: unique symbol;

export type Key<T> = Readonly<{
  id: symbol;
  name: string;
  [keyType]?: T;
}>;

export function key<T>(name: string): Key<T> {
  return { id: Symbol(name), name };
}
```

The runtime stores `unknown` internally but exposes a typed API:

```ts
class Store {
  private readonly values = new Map<symbol, unknown>();

  get<T>(key: Key<T>): T | undefined {
    return this.values.get(key.id) as T | undefined;
  }
}
```

The cast is concentrated at the abstraction boundary rather than repeated by consumers.

## 0.5 Relations and equivalence

### Motivation

Two physical states may differ internally while every allowed observation gives the same answer. Recovery should often be judged by behaviour, not byte-for-byte representation.

### Definition: relation

A binary **relation** $R$ on $X$ is a predicate on pairs of values. We write $xRy$ when the predicate holds.

```ts
type Relation<T> = (left: T, right: T) => boolean;
```

### Definition: equivalence relation

An **equivalence relation** $\simeq$ is:

- reflexive: $x\simeq x$;
- symmetric: if $x\simeq y$, then $y\simeq x$;
- transitive: if $x\simeq y$ and $y\simeq z$, then $x\simeq z$.

It partitions values into equivalence classes: groups treated as the same for the purpose at hand.

### Worked example: allocator states

Suppose two states contain the same live handles but different next-ID counters:

```text
state A: live = {}, next = 17
state B: live = {}, next = 23
```

If clients can inspect `next`, the states are distinguishable. If the only operations are allocate, release, and use a live handle, a relation that permits a consistent renaming of future handles may identify them.

The observer determines the equivalence. There is no universal observational equivalence independent of the interface.

## 0.6 Graphs, dependencies, and topological order

### Motivation

Requirements and provisions form a directed graph. Activation and deactivation order depend on that graph.

### Definition: directed graph

A directed graph is a pair $(V,E)$ where $V$ is a set of vertices and $E\subseteq V\times V$ is a set of directed edges.

For components, use an edge

$$
A\longrightarrow B
$$

when A may provide a key required by B. The arrow points from provider to consumer.

### Definition: path and cycle

A **path** follows one or more edges. A **cycle** is a non-empty path that returns to its starting vertex.

```text
A ---> B ---> C
^           |
|-----------|
```

A graph with no directed cycles is a **directed acyclic graph**, or DAG.

### Definition: topological order

A topological order lists the vertices so that every provider appears before each consumer it precedes.

For:

```text
Database ---> Repository ---> WebAPI
       \--------------------> Metrics
```

one valid order is:

```text
Database, Repository, WebAPI, Metrics
```

Another may place `Metrics` before `Repository` if it depends only on `Database`.

## 0.7 Transition systems and inference rules

### Motivation

A runtime is not merely a function from initial state to final state. Many legal schedules may interleave lifecycle steps. We need to describe which single steps are permitted.

### Definition: transition relation

A **transition system** consists of states and a relation $\longrightarrow$ between states. The judgment

$$
\gamma\longrightarrow\delta
$$

means that the runtime may move from state $\gamma$ to state $\delta$ in one step.

The reflexive-transitive closure $\longrightarrow^*$ means zero or more steps.

### Definition: inference rule

An inference rule has premises above a line and a conclusion below it:

$$
\frac{\text{premise}_1\qquad\text{premise}_2}{\text{conclusion}}
\;\textsc{Name}
$$

Read it as: if all premises hold, the conclusion is a legal transition.

### Worked example

A simplified activation rule is:

$$
\frac{
  \mathrm{state}(n)=\mathrm{Inactive}
  \qquad
  \mathrm{satisfied}(n,\gamma)
}{
  \gamma\longrightarrow
  \gamma[\mathrm{state}(n)\mapsto\mathrm{Active}]
}
\;\textsc{Activate}
$$

Equivalent pseudocode:

```ts
if (fiber.state === "inactive" && satisfied(fiber, runtime)) {
  fiber.state = "active";
}
```

The formal rule is not decorative. It fixes exactly which observations the transition may depend on and exactly which state field it changes.

> **Common mistake: rules do not prescribe a scheduler.** If two rules are applicable, the transition relation usually permits either. A later confluence result asks whether different legal choices eventually agree.

## 0.8 Lab implementation

Create `src/core/algebra.ts` containing:

```ts
export type Endo<S> = (state: S) => S;

export const identity = <T>(value: T): T => value;

export function compose<A, B, C>(
  f: (value: B) => C,
  g: (value: A) => B
): (value: A) => C {
  return (value) => f(g(value));
}

export function composeEndos<S>(...steps: readonly Endo<S>[]): Endo<S> {
  return (initial) => steps.reduce((state, step) => step(state), initial);
}
```

Create `src/core/graph.ts` with:

```ts
export type Graph<N> = ReadonlyMap<N, ReadonlySet<N>>;

export function hasCycle<N>(graph: Graph<N>): boolean;
export function topologicalSort<N>(graph: Graph<N>): readonly N[];
```

A cycle may cause `topologicalSort` to throw a typed error.

## 0.9 Worked property tests

Associativity is a property of composition, not a collection of three favourite examples. Start with ordinary unit tests, then express the law generically.

```ts
import { describe, expect, test } from "vitest";
import { compose, identity } from "../../src/core/algebra";

describe("composition", () => {
  test("identity is a left and right unit", () => {
    const f = (x: number) => 3 * x + 1;
    expect(compose(identity, f)(7)).toBe(f(7));
    expect(compose(f, identity)(7)).toBe(f(7));
  });

  test("composition is associative", () => {
    const f = (x: number) => x + 1;
    const g = (x: number) => 2 * x;
    const h = (x: number) => x - 4;

    expect(compose(f, compose(g, h))(10))
      .toBe(compose(compose(f, g), h)(10));
  });
});
```

In later labs, `fast-check` will generate functions from a restricted family of transformations and hundreds of states.

## 0.10 Exercises

### Core exercise 0.1 - Translate the notation

For each item, give:

1. a sentence in ordinary language;
2. a TypeScript signature;
3. a concrete example.

Items:

1. $f:X\to Y$
2. $f:\Gamma\to\Gamma$
3. $f\circ g$
4. $\mathrm{id}_\Gamma$
5. $\sigma:K\rightharpoonup V$
6. $\gamma\simeq\delta$
7. $\gamma\longrightarrow\delta$
8. $\gamma\longrightarrow^*\delta$

### Core exercise 0.2 - Monoid or not?

For each proposed structure, state whether it is a monoid. If it is, identify the identity and justify associativity. If it is not, give the smallest counterexample you can.

- natural numbers under addition;
- natural numbers under multiplication;
- non-empty strings under concatenation;
- booleans under exclusive-or;
- integers under exponentiation;
- arrays under “take the longer array”;
- state transformations under composition.

### Core exercise 0.3 - State graph

Model a two-plugin runtime with states `(A inactive/active, B inactive/active)` where B requires A. Draw all states and all legal activation/deactivation transitions. Mark unreachable states.

### Core exercise 0.4 - Topological activation

Implement `topologicalSort`, then test the dependency graphs:

```text
Database -> Repository -> WebAPI
Clock -> Summary
Notes -> Summary
A -> B -> C -> A
```

Explain why a topological order is useful but insufficient for a fully dynamic runtime whose graph can change during execution.

### Extension 0.5 - Option versus exceptions

Implement a partial service lookup twice:

- returning `Option<T>`;
- throwing `MissingService`.

Compare how each representation affects composition, testing, and API ergonomics.

### Theory exercise 0.6 - Parenthesisation

Show by calculation that

$$
(f\circ g)\circ h=f\circ(g\circ h)
$$

for arbitrary functions of compatible types. Your proof should expand both sides at an arbitrary input $x$.

## 0.11 Counterexample clinic

Introduce this incorrect composition helper:

```ts
function wrongCompose<A>(f: (x: A) => A, g: (x: A) => A) {
  return (x: A) => g(f(x));
}
```

The implementation is a valid function, but its name and documentation claim mathematical composition. Write the smallest test that exposes the direction error. Then explain why an inverse accumulator implemented with the same mistaken convention would recover effects in the wrong order.

## 0.12 Deliverable checklist

- [ ] `algebra.ts` contains typed identity and composition helpers.
- [ ] Unit tests demonstrate associativity and both unit laws.
- [ ] `graph.ts` detects cycles and returns a topological order for DAGs.
- [ ] The lab note defines every symbol used in its equations.
- [ ] At least two failed structures include explicit counterexamples.
- [ ] The state graph for the two-plugin example distinguishes legal, illegal, and unreachable states.

## 0.13 Reading

**Primary paper:** Introduction; Sections 2.1-2.3; skim Section 4.2 to see where transition rules are headed.

**Foundations:** selected material on definitions, functions, relations, graphs, state machines, and invariants from *Mathematics for Computer Science*.

**Programming-languages notation:** the early operational-semantics chapters of Pierce's *Types and Programming Languages* or Harper's *Practical Foundations for Programming Languages*.

**Category theory bridge:** the opening chapters of *Category Theory for Programmers*, stopping after composition and categories. At this stage, the goal is fluent composition, not monads.

EOF
```

```unknown
bash -lc cat > /mnt/data/work/handbook/chapters/02-lab1.md <<'EOF'
# Lab 1: Effects as Revertible Context Transformations

## Purpose

An effect changes the world in which a computation runs. In this lab, “the world” is deliberately small: an immutable context state. The objective is to understand exactly what must be returned alongside a state change so that the change can later be withdrawn.

This is the first place where the paper departs from ordinary effect tracking. A static effect system may describe that a computation reads state, writes state, throws, or performs I/O. Mini-Cordis needs a runtime object that can be stored and invoked when the component leaves. The effect must therefore provide not only a successor state but also evidence of how to return from that successor.

## Learning outcomes

After this lab you can:

- model an atomic effect as a function $\Gamma\to\Gamma\times(\Gamma\to\Gamma)$;
- distinguish left inverses, right inverses, and two-sided inverses;
- explain why Mini-Cordis requires only a state-local witness;
- implement reversible `set`, `delete`, `increment`, and registration operations;
- compose two reversible effects in the correct order;
- state recovery as both an equation and a property-based test;
- identify operations that lie outside the chosen recovery boundary.

## 1.1 From an impure operation to an explicit state transformation

### Motivation

Consider an ordinary mutable update:

```ts
state.values.set("count", 4);
```

The returned value does not describe the effect. The change is visible only by inspecting mutable state before and after the statement. This makes composition convenient but reasoning indirect.

We first make the state explicit:

```ts
type CounterState = Readonly<{ count: number }>;

const setCount = (value: number) =>
  (state: CounterState): CounterState => ({ count: value });
```

Now the operation is a transformation $f:\Gamma\to\Gamma$. Its input and output expose the change.

### Definition: effect as a context transformation

For a context type $\Gamma$, an **effect transformation** is an endomorphism

$$
f:\Gamma\to\Gamma.
$$

Sequential effects use ordinary function composition. If $f$ runs after $h$, the combined effect is $f\circ h$.

### Worked example: two state effects

Let:

$$
h(x)=x+1,
\qquad
f(x)=2x.
$$

From $x=3$:

$$
(f\circ h)(3)=f(4)=8.
$$

The composed operation is still a transformation on the same state space. This closure, together with associativity and identity, is why the paper starts from the transformation monoid.

## 1.2 Why a cleanup callback is not yet a mathematical inverse

### Motivation

A plugin API commonly asks an operation to return a disposer:

```ts
const dispose = registerCommand("hello", handler);
```

This is already a strong design. Creation and cleanup are local. But the word “inverse” should be used carefully. A disposer may only be meaningful after its matching registration and at a state containing that registration.

### Definition: left inverse

Given $f:\Gamma\to\Gamma$ and $g:\Gamma\to\Gamma$, $g$ is a **left inverse** of $f$ when

$$
g\circ f=\mathrm{id}_{\Gamma}.
$$

The direction means: perform $f$, then perform $g$, and recover the starting state.

### Definition: right inverse

$g$ is a **right inverse** of $f$ when

$$
f\circ g=\mathrm{id}_{\Gamma}.
$$

A two-sided inverse satisfies both conditions.

### Why the paper needs only one side

Unloading follows loading. The runtime asks whether applying the returned inverse to the state produced by the effect recovers the input. It does not require that applying the “inverse” first and then reapplying the effect be neutral.

For resource acquisition:

```text
acquire resource -> release resource
```

is meaningful. The reverse sequence

```text
release arbitrary resource -> acquire some resource
```

usually is not.

> **Fundamentals: one-sided does not mean careless.** The inverse is still held to a precise equation in the relevant direction. The weaker condition matches lifecycle semantics: installation precedes withdrawal.

## 1.3 State-dependent inverses

### Motivation

Suppose `set("x", 42)` is applied to either of these states:

```text
{x: 7}    or    {x absent}
```

The correct cleanup differs. In the first case it must restore `7`; in the second it must remove `x`. No single inverse chosen before seeing the state can handle both unless it records additional information.

### Definition: reversible effect function

A **reversible effect function** is

$$
e:\Gamma\to\Gamma\times(\Gamma\to\Gamma).
$$

At input $\gamma$, it returns:

- a successor state $\delta$;
- an inverse $g:\Gamma\to\Gamma$ chosen using information available at $\gamma$.

In TypeScript:

```ts
export type Endo<S> = (state: S) => S;

export type Reversible<S> =
  (state: S) => readonly [next: S, undo: Endo<S>];
```

### Definition: witnessed reversible effect

The pair returned at $\gamma$ is **witnessed** when

$$
e(\gamma)=(\delta,g)
\quad\Longrightarrow\quad
g(\delta)=\gamma.
$$

When the book later uses observational equivalence, the equality becomes $g(\delta)\simeq\gamma$.

The important point is locality: $g$ must recover this application. It is not necessarily constrained at every unrelated state.

### Worked example: reversible set

```ts
const MISSING = Symbol("missing");

type ValueState = Readonly<{
  values: ReadonlyMap<string, number>;
}>;

export function setValue(
  key: string,
  value: number
): Reversible<ValueState> {
  return (state) => {
    const previous = state.values.has(key)
      ? state.values.get(key)!
      : MISSING;

    const nextValues = new Map(state.values);
    nextValues.set(key, value);
    const next = { values: nextValues };

    const undo: Endo<ValueState> = (current) => {
      const restored = new Map(current.values);
      if (previous === MISSING) {
        restored.delete(key);
      } else {
        restored.set(key, previous);
      }
      return { values: restored };
    };

    return [next, undo] as const;
  };
}
```

Trace the effect from:

```text
gamma = {x: 7, y: 2}
```

The operation captures `previous = 7`, returns:

```text
delta = {x: 42, y: 2}
```

and an inverse that restores `x` to `7` while leaving other keys as they currently stand.

### A deliberately bad inverse

```ts
const badUndo = (current: ValueState): ValueState => {
  const values = new Map(current.values);
  values.delete("x");
  return { values };
};
```

This recovers a state where `x` was absent, but not a state where `x` previously held a value. Cleanup that always deletes is not the inverse of replacement.

## 1.4 Uniform versus state-local inverses

A **uniform inverse** is one function $g$ that works for all states:

$$
\forall\gamma\in\Gamma.\;g(f(\gamma))=\gamma.
$$

Examples include adding and subtracting a fixed integer on an unbounded integer state:

$$
f(x)=x+3,
\qquad
g(x)=x-3.
$$

A state-local inverse is selected per application. Replacing a map entry is the representative example because the old value must be captured.

### Worked comparison

```ts
export function add(amount: number): Reversible<number> {
  return (state) => [state + amount, (next) => next - amount] as const;
}
```

Here every invocation returns extensionally the same inverse.

```ts
export function overwrite(
  value: number
): Reversible<number> {
  return (state) => [value, () => state] as const;
}
```

Here the inverse is a closure over the particular starting state.

Both satisfy the witnessed condition. Only the first has a uniform inverse determined independently of the input.

> **Common misconception: closures are not a proof.** Capturing the old state makes a correct inverse possible, but the closure may still restore the wrong field or forget a related invariant. The witness remains an obligation checked by reasoning or tests.

## 1.5 Composition of reversible effects

### Motivation

A component rarely performs one atomic effect. We need a combined reversible operation whose inverse is derived from the pieces.

Suppose $e_1$ is to run after $e_2$:

$$
\gamma
\xrightarrow{e_2}
\delta
\xrightarrow{e_1}
\varepsilon.
$$

Let $e_2(\gamma)=(\delta,s)$ and $e_1(\delta)=(\varepsilon,t)$. Recovery must first use $t$ to return to $\delta$, then $s$ to return to $\gamma$. The combined inverse is $s\circ t$.

### Definition: effect composition

Define $e_1\diamond e_2$ by:

$$
(e_1\diamond e_2)(\gamma)
=
\begin{aligned}[t]
&\text{let }(\delta,s)=e_2(\gamma)\text{ in}\\
&\text{let }(\varepsilon,t)=e_1(\delta)\text{ in}\\
&(\varepsilon,s\circ t).
\end{aligned}
$$

The right-hand effect runs first, matching function composition notation.

```ts
export function composeReversible<S>(
  after: Reversible<S>,
  before: Reversible<S>
): Reversible<S> {
  return (initial) => {
    const [middle, undoBefore] = before(initial);
    const [final, undoAfter] = after(middle);
    return [
      final,
      (state) => undoBefore(undoAfter(state))
    ] as const;
  };
}
```

### Worked example

Start with:

```text
{x: 1, y: 10}
```

Run:

1. `setValue("x", 5)`;
2. `setValue("y", 20)`.

Forward trace:

```text
{x: 1, y: 10}
  -- set x --> {x: 5, y: 10}
  -- set y --> {x: 5, y: 20}
```

Inverse trace:

```text
{x: 5, y: 20}
  -- undo y --> {x: 5, y: 10}
  -- undo x --> {x: 1, y: 10}
```

The composite inverse reverses the execution order.

### Definition: unit reversible effect

The unit performs no change and returns identity recovery:

$$
\eta_\Gamma(\gamma)=(\gamma,\mathrm{id}_\Gamma).
$$

```ts
export const reversibleIdentity = <S>(): Reversible<S> =>
  (state) => [state, (current) => current] as const;
```

Under $\diamond$, reversible effects form a monoid when restricted to witnessed effects. Associativity follows from associativity of ordinary function composition.

## 1.6 Twisted composition of explicit pairs

The paper first presents a simpler uniform case: pairs $(f,g)$ of forward and reverse transformations. Their composition is “twisted”:

$$
(f_1,g_1)\circledast(f_2,g_2)
=
(f_1\circ f_2,\;g_2\circ g_1).
$$

Why is the inverse order reversed? The forward side runs $f_2$ then $f_1$. Recovery must run $g_1$ then $g_2$. Written as a composite, that is $g_2\circ g_1$.

```text
forward:  gamma --f2--> delta --f1--> epsilon
reverse:  epsilon --g1--> delta --g2--> gamma
```

The “twist” is not an exotic additional rule. It is the ordinary order forced by undoing a sequence.

> **Category theory connection: the opposite monoid.** Reverses accumulate using the opposite multiplication: the same transformations, but with composition order turned around. The product of the forward transformation monoid and its opposite packages installation and teardown together.

## 1.7 Recovery boundary: what counts as state?

### Motivation

Not every real-world action can be undone. Sending a network packet cannot generally pull the bytes back from another machine. Printing a line cannot make every observer forget it. A payment may only be compensated, not literally reversed.

The equation $g(f(\gamma))\simeq\gamma$ depends on what $\Gamma$ includes.

### Definition: system boundary

The **system boundary** separates locations the runtime can exclusively control and recover from locations whose state may escape or be changed by others.

Inside the boundary, an operation is represented as a meaningful transformation of $\Gamma$ with an inverse. Outside the boundary, the model cannot claim literal recovery.

### Acquisition versus emission

Many operations have two stages:

```text
acquisition: obtain and record a capability
emission:    use it to affect the external world
```

Examples:

| Operation | Acquisition inside boundary | Emission outside boundary |
|---|---|---|
| file | open descriptor | write bytes visible elsewhere |
| network | open socket | send packet |
| process | start child and record handle | child communicates externally |
| payment | reserve transaction object | settle charge |

Closing a descriptor can reverse the acquisition. It does not erase bytes already written.

### Worked classification

Classify these effects for a command host:

- registering a command in a private map: inside;
- subscribing to a private event bus: inside;
- starting a timer and storing its handle: inside, if cancellation is reliable;
- logging to a shared terminal: outside as an emission;
- creating a temporary file in a private directory: potentially inside if the runtime owns the path and deletion is the agreed equivalence;
- sending an email: outside; a later apology is compensation, not inversion.

## 1.8 Implementation task

Create `src/core/reversible.ts`:

```ts
export type Endo<S> = (state: S) => S;
export type Reversible<S> =
  (state: S) => readonly [next: S, undo: Endo<S>];

export function composeReversible<S>(
  after: Reversible<S>,
  before: Reversible<S>
): Reversible<S>;

export function sequenceReversible<S>(
  effects: readonly Reversible<S>[]
): Reversible<S>;

export function reversibleIdentity<S>(): Reversible<S>;
```

Implement the following pure context operations:

```ts
setValue(key: string, value: number): Reversible<ValueState>
deleteValue(key: string): Reversible<ValueState>
incrementValue(key: string, amount: number): Reversible<ValueState>
appendUnique(key: string, value: string): Reversible<ListState>
registerCommand(name: string): Reversible<CommandState>
```

Choose explicit preconditions. For example, `registerCommand` may reject duplicate names rather than overwrite them.

## 1.9 Property-based tests

### Definition: property-based testing

A unit test checks a chosen example. A **property-based test** states a property over a generated domain and lets a test framework search many inputs, usually shrinking a failure to a simpler counterexample.

The witness condition becomes:

```ts
fc.assert(fc.property(stateArbitrary, (initial) => {
  const [next, undo] = effect(initial);
  expect(undo(next)).toEqual(initial);
}));
```

A generator for finite maps can be built from arrays of key-value tuples:

```ts
import fc from "fast-check";

const stateArbitrary = fc
  .array(fc.tuple(fc.string({ minLength: 1, maxLength: 5 }), fc.integer()), {
    maxLength: 8
  })
  .map((entries) => ({ values: new Map(entries) }));
```

Map equality may need a normalised representation:

```ts
function entriesOf(state: ValueState) {
  return [...state.values.entries()].sort(([a], [b]) => a.localeCompare(b));
}
```

Then compare `entriesOf(undo(next))` with `entriesOf(initial)`.

### Properties to test

1. **Witness:** `undo(next) ~= initial`.
2. **Unit:** composing an effect with identity does not change its successor or recovery.
3. **Associativity:** grouping a sequence of reversible effects does not change successor or inverse behaviour.
4. **Locality:** `setValue("x", v)` leaves keys other than `x` unchanged.
5. **Precondition:** duplicate command registration is rejected without changing the state.

> **Testing warning: function equality is extensional.** JavaScript cannot generally compare two closures for mathematical equality. Test that they produce equivalent outputs over generated states, not that the function objects are `===`.

## 1.10 Worked proof: composition preserves the witness

Let:

$$
e_2(\gamma)=(\delta,s),
\qquad
s(\delta)=\gamma,
$$

and:

$$
e_1(\delta)=(\varepsilon,t),
\qquad
t(\varepsilon)=\delta.
$$

By definition:

$$
(e_1\diamond e_2)(\gamma)=(\varepsilon,s\circ t).
$$

Apply the combined inverse:

$$
(s\circ t)(\varepsilon)
=s(t(\varepsilon))
=s(\delta)
=\gamma.
$$

Therefore the composite is witnessed.

This short proof should be mirrored by a property test over generated sequences. The proof explains *why* the implementation works; the test guards against implementing a different order.

## 1.11 Exercises

### Core exercise 1.1 - Correct replacement

Implement `setValue` so that it recovers both an absent key and an overwritten key. Write one example test for each case and one property test covering both.

### Core exercise 1.2 - Reversible deletion

Implement `deleteValue`. Decide what happens if the key is absent:

- reject the operation;
- treat it as an identity effect;
- encode partiality in the result type.

State the choice as a precondition or type, then test that failed operations produce no state transition.

### Core exercise 1.3 - Composition laws

For three generated reversible operations from a restricted family, test:

$$
(e_1\diamond e_2)\diamond e_3
\simeq
 e_1\diamond(e_2\diamond e_3).
$$

Test both the forward result and the behaviour of the returned inverse.

### Core exercise 1.4 - Uniform or state-dependent?

Classify each operation and justify the answer:

- increment an integer by 1;
- set a map key to `v`;
- append to a list;
- rotate a fixed-size array;
- allocate the next numeric ID;
- register a callback under a fresh token.

For each state-dependent case, identify what the inverse closure must capture.

### Core exercise 1.5 - Boundary audit

Choose an applied domain - HTTP routes, editor commands, agent tools, or chatbot plugins. List at least ten operations and classify each as:

- invertible inside the proposed boundary;
- only compensatable;
- irreversible emission;
- unclear until the interface is refined.

For two unclear cases, redesign the API so that acquisition becomes separately trackable.

### Extension 1.6 - Typed failure

Replace exception-based precondition failures with:

```ts
type Result<T, E> =
  | { readonly ok: true; readonly value: T }
  | { readonly ok: false; readonly error: E };
```

Define a reversible effect that may fail without producing a transition. Explain how composition changes.

### Theory exercise 1.7 - Left but not right

Give a concrete function with a left inverse but no right inverse, or a right inverse but no left inverse. Explain which direction corresponds to loading followed by unloading.

Hint: use an injection or projection between finite or countable sets.

## 1.12 Counterexample clinic

### Counterexample A: inverse order

Implement the composite inverse incorrectly as `undoAfter(undoBefore(state))`. Find the smallest pair of effects for which witness recovery fails. Avoid using two effects on disjoint keys, because they may commute and hide the bug.

A good candidate is:

```text
1. set x to 5
2. increment x by 2
```

### Counterexample B: stale snapshot

Implement `setValue` so that its inverse returns the entire captured starting state rather than restoring only its own key. Then run:

```text
load A: set x
load B: set y
unload A
```

Show that the snapshot inverse erases B's later change. This is the first indication that local witness recovery alone is not sufficient for arbitrary interleaving; Lab 5 will formalise the missing independence condition.

### Counterexample C: external emission

Model `sendEmail` as an identity state transformation with a no-op inverse. The equation holds trivially in the internal state, yet the recipient has observed an email. Explain why the model is not false, but its system boundary is too narrow to justify the claim a user probably cares about.

## 1.13 Deliverable checklist

- [ ] All atomic effects return a successor and a state-local inverse.
- [ ] Replacement restores the previous binding rather than blindly deleting.
- [ ] Composite recovery executes in reverse application order.
- [ ] Property tests cover witness, unit, associativity, and locality.
- [ ] Failed preconditions leave the state unchanged.
- [ ] The lab note distinguishes uniform, state-dependent, left, right, and two-sided inverses.
- [ ] The boundary audit includes acquisitions, emissions, and compensations.

## 1.14 Reading

**Primary paper:** Sections 3.1.1 and 3.1.2; revisit the system-boundary discussion in Section 6.1 after completing the boundary audit.

**Effects bridge:** Wadler, *Monads for Functional Programming*, focusing on explicit sequencing of stateful computations. The purpose is comparison, not the claim that Mini-Cordis's reversible effects are exactly Wadler's monad.

**Optional algebraic effects:** Pretnar, *An Introduction to Algebraic Effects and Handlers*, especially the motivation that effectful behaviour can be exposed as operations and interpreted separately.

**Category theory bridge:** read about monoids and the endomorphism monoid. Stop before more advanced categorical machinery unless it helps your own understanding.

EOF
```

```unknown
bash -lc cat > /mnt/data/work/handbook/chapters/03-lab2.md <<'EOF'
# Lab 2: Effect Contexts, Accumulators, and Derived Teardown

## Purpose

Lab 1 returned one inverse from one effect. A component activation performs many effects, often through helper functions that know nothing about the component's eventual teardown. Lab 2 introduces an **effect context** that accumulates the inverses as effects occur.

This turns teardown from a second, manually synchronised program into a value *derived from setup*. It also reveals the limits of a single accumulator: it provides reliable LIFO recovery for one sequence, but by itself does not justify removing one component from the middle of an interleaved system.

## Learning outcomes

After this lab you can:

- define the effect context $\partial\Gamma$;
- explain the accumulator and its soundness invariant;
- implement `track` and `recover`;
- derive a component disposer from atomic effect registration;
- distinguish LIFO reversal from arbitrary selective withdrawal;
- implement useful context-mediated primitives;
- test idempotent disposal and nested scopes;
- identify aliasing and double-disposal errors.

## 2.1 The problem with returning inverses to every caller

Suppose activation looks like this:

```ts
async function activate(ctx: HostContext): Promise<Dispose> {
  const undoCommand = ctx.registerCommand("summary", summary);
  const undoListener = ctx.on("note-added", refreshSummary);
  const undoTimer = ctx.every(60_000, refreshSummary);

  return async () => {
    await undoTimer();
    await undoListener();
    await undoCommand();
  };
}
```

This is better than a separate `deactivate` method, but the component author still has to:

- retain each disposer;
- compose them in reverse order;
- include every effect;
- prevent repeated disposal;
- propagate partial failure.

The runtime can do this bookkeeping once.

## 2.2 The effect context

### Motivation

After a sequence of effects, the runtime needs both the current state and a composite recovery operation.

### Definition: effect context

For a context type $\Gamma$, define:

$$
\partial\Gamma
=\Gamma\times(\Gamma\to\Gamma).
$$

An element $(\gamma,\varphi)$ contains:

- $\gamma$: the current context state;
- $\varphi$: the accumulated recovery function.

The initial effect context is:

$$
(\gamma_0,\mathrm{id}_\Gamma).
$$

The identity means no effect has yet been recorded.

### Definition: accumulator

The function $\varphi$ is the **accumulator**. If the sequence has been tracked correctly, applying $\varphi$ to the current state recovers the state at which accumulation began.

### Definition: soundness invariant

For a scope that began at $\gamma_0$, the **soundness invariant** is:

$$
\varphi(\gamma)\simeq\gamma_0.
$$

At this stage, use literal equality. Lab 5 replaces it with observational equivalence.

## 2.3 Tracking a uniform pair

The paper first defines tracking for a pair $(f,g)$ of transformations.

### Definition: track

$$
\operatorname{track}_\Gamma(f,g)(\gamma,\varphi)
=
(f(\gamma),\varphi\circ g).
$$

The forward transformation changes the current state. The inverse is appended on the right of the accumulator so that it runs before the older inverses when the accumulator is eventually applied.

### Worked trace

Start with:

$$
(\gamma_0,\mathrm{id}).
$$

Track $(f_1,g_1)$:

$$
(f_1(\gamma_0),g_1).
$$

Track $(f_2,g_2)$:

$$
(f_2(f_1(\gamma_0)),g_1\circ g_2).
$$

Recovery runs:

$$
(g_1\circ g_2)(f_2(f_1(\gamma_0)))
=g_1(f_1(\gamma_0))
=\gamma_0.
$$

The newest inverse $g_2$ runs first.

## 2.4 Recovery

### Definition: recover

$$
\operatorname{recover}_\Gamma(\gamma,\varphi)
=(\varphi(\gamma),\mathrm{id}_\Gamma).
$$

Recovery applies the accumulator and resets it. Resetting matters: a second recovery should not reapply inverses to states they were never promised to reverse.

### Worked example

```text
initial commands: {}
track register("a"): {a}, undo a
track register("b"): {a,b}, undo a o undo b
recover:             {}, identity
```

## 2.5 Imperative realisation: the effect scope

The pure pair $(\gamma,\varphi)$ is excellent for reasoning. An actual host often owns one mutable context and stores a closure that disposes effects.

```ts
export type Awaitable<T> = T | Promise<T>;
export type Dispose = () => Awaitable<void>;

const noop: Dispose = () => undefined;

function composeDispose(older: Dispose, newer: Dispose): Dispose {
  return async () => {
    await newer();
    await older();
  };
}
```

### Definition: imperative effect scope

An **effect scope** is a runtime object that:

1. admits effect operations;
2. accumulates their disposers in LIFO order;
3. exposes one idempotent disposer for the complete scope.

```ts
export class EffectScope {
  private armed = true;
  private disposeAll: Dispose = noop;

  add(dispose: Dispose): Dispose {
    if (!this.armed) {
      throw new Error("cannot add an effect to a disposed scope");
    }

    let localArmed = true;
    const once: Dispose = async () => {
      if (!localArmed) return;
      localArmed = false;
      await dispose();
    };

    this.disposeAll = composeDispose(this.disposeAll, once);
    return once;
  }

  dispose: Dispose = async () => {
    if (!this.armed) return;
    this.armed = false;
    const recover = this.disposeAll;
    this.disposeAll = noop;
    await recover();
  };
}
```

The local wrapper makes an individual disposer idempotent. The scope wrapper makes aggregate disposal idempotent.

> **Why idempotence is defensive, not algebraic.** The paper's inverse is promised at the state produced by one application. Applying it twice is generally meaningless. An `armed` flag prevents the invalid second application rather than claiming the inverse itself is idempotent.

## 2.6 Deriving teardown from setup

A context method performs a mutation and immediately registers its inverse with the current scope.

```ts
class CommandRegistry {
  private readonly commands = new Map<string, () => void>();

  constructor(private readonly scope: EffectScope) {}

  register(name: string, handler: () => void): Dispose {
    if (this.commands.has(name)) {
      throw new Error(`duplicate command: ${name}`);
    }

    this.commands.set(name, handler);

    return this.scope.add(() => {
      this.commands.delete(name);
    });
  }
}
```

A component no longer manually constructs a teardown program:

```ts
async function activate(ctx: ComponentContext): Promise<void> {
  ctx.commands.register("summary", () => ctx.summary.run());
  ctx.events.on("note-added", () => ctx.summary.refresh());
  ctx.timers.every(60_000, () => ctx.summary.refresh());
}
```

The fiber's scope already contains the composite disposer.

### Locality of concern

**Locality of concern** means the operation and its inverse are defined together. The component author chooses to register a command; the command API defines how command registration is withdrawn. The component does not repeat registry internals in a distant unload callback.

This does not eliminate all obligations. The primitive author must supply the correct inverse, and the component must route relevant effects through context-mediated primitives.

## 2.7 Useful primitives

Implement at least four resource types. Each should have:

- a state-changing action;
- a precondition;
- a disposer;
- a query used by tests;
- a clear system boundary.

### Command registration

```ts
interface CommandAPI {
  register(name: string, handler: () => Awaitable<void>): Dispose;
  has(name: string): boolean;
  invoke(name: string): Promise<void>;
}
```

Precondition: the name is not already registered in the current realm.

### Event subscription

```ts
interface EventAPI {
  on<T>(event: Key<T>, handler: (value: T) => Awaitable<void>): Dispose;
  emit<T>(event: Key<T>, value: T): Promise<void>;
  listenerCount<T>(event: Key<T>): number;
}
```

Registration is inside the boundary. The effects caused by handlers may not be.

### Timer acquisition

```ts
interface TimerAPI {
  every(milliseconds: number, task: () => Awaitable<void>): Dispose;
  pendingCount(): number;
}
```

The disposer cancels future ticks. A tick already running is an asynchronous operation that may require separate draining.

### Route registration

```ts
interface RouterAPI {
  route(method: HttpMethod, path: string, handler: Handler): Dispose;
  resolve(method: HttpMethod, path: string): Handler | undefined;
}
```

A route table treated as a finite map is a good example of operations at distinct keys commuting.

### Child component registration

Later, `ctx.use(component)` will itself be an effect. Its inverse retires the child fiber. This yields hierarchical composition.

## 2.8 Nested scopes

### Motivation

A component may call a helper that creates several effects. The helper should return one disposer without exposing its internal list.

### Definition: nested scope

A nested scope is an effect scope whose aggregate disposer is itself registered as one effect in its parent.

```ts
function childScope(parent: EffectScope): EffectScope {
  const child = new EffectScope();
  parent.add(child.dispose);
  return child;
}
```

### Worked example

```text
parent scope
  command A
  child scope
    listener B
    timer C
  route D
```

Parent recovery order:

```text
undo route D
  undo timer C
  undo listener B
undo command A
```

The parent does not know the child's internal structure. It only knows that the child has one disposer.

### Recursive context intuition

The paper eventually defines a recursive context type so that an inverse at one level is itself an effect at the parent level. Nested scopes provide the concrete programming intuition before the fixed-point type is introduced.

## 2.9 LIFO recovery and its limits

### The guarantee LIFO gives

For one sequence of witnessed effects:

```text
apply e1, e2, e3
undo  e3, e2, e1
```

Each inverse meets the state produced by its own effect after all later effects in that sequence have been removed. No commutativity assumption is needed.

### What LIFO does not give

Consider two components whose effects interleave:

```text
A1, B1, A2, B2
```

A single global stack can only undo a suffix:

```text
B2, A2, B1, A1
```

It cannot remove only A while leaving B:

```text
want: remove A2 and A1, preserve B1 and B2
```

Per-component stacks solve ownership bookkeeping but do not automatically make inverses valid in states moved by other components. Lab 5 introduces **independence**, the condition that justifies selective withdrawal.

> **Common mistake: “one stack per component” is necessary but not sufficient.** It identifies which inverses belong to A. It does not prove those inverses commute past B's effects.

## 2.10 Pure `track` and `recover` implementation

Create `src/core/effect-context.ts`:

```ts
import type { Endo } from "./algebra";

export type EffectContext<S> = Readonly<{
  state: S;
  recover: Endo<S>;
}>;

export function initialEffectContext<S>(state: S): EffectContext<S> {
  return { state, recover: (current) => current };
}

export function track<S>(
  context: EffectContext<S>,
  forward: Endo<S>,
  inverse: Endo<S>
): EffectContext<S> {
  return {
    state: forward(context.state),
    recover: (current) => context.recover(inverse(current))
  };
}

export function recover<S>(context: EffectContext<S>): EffectContext<S> {
  return {
    state: context.recover(context.state),
    recover: (current) => current
  };
}
```

Then add a lifting function for the state-dependent effects from Lab 1:

```ts
export function perform<S>(
  context: EffectContext<S>,
  effect: Reversible<S>
): EffectContext<S> {
  const [next, undo] = effect(context.state);
  return {
    state: next,
    recover: (current) => context.recover(undo(current))
  };
}
```

## 2.11 Worked invariant test

For a sequence of effects $e_1,\ldots,e_n$, define:

```ts
function run<S>(initial: S, effects: readonly Reversible<S>[]) {
  return effects.reduce(perform, initialEffectContext(initial));
}
```

Then:

```ts
const reached = run(initial, effects);
const recovered = recover(reached);
expect(normalise(recovered.state)).toEqual(normalise(initial));
```

A stronger property checks the invariant after every prefix:

```ts
let current = initialEffectContext(initial);
for (const effect of effects) {
  current = perform(current, effect);
  expect(normalise(current.recover(current.state)))
    .toEqual(normalise(initial));
}
```

This is an executable form of the paper's statement that every tracking step preserves the recovery target.

## 2.12 Handling disposer failure

Real cleanup can fail. A route may already have been removed, a network close may reject, or a user-supplied handler may throw.

Choose and document a policy:

1. **Fail-fast:** stop at the first error. Simple, but later resources leak.
2. **Best-effort:** run every disposer, collect errors, then throw an aggregate.
3. **Retry:** retry selected resource classes under a policy.
4. **Escalate:** mark the fiber failed and require process-level recovery.

For the lab, use best-effort:

```ts
export class DisposalError extends Error {
  constructor(readonly causes: readonly unknown[]) {
    super(`${causes.length} disposer(s) failed`);
  }
}

async function runAllLifo(disposers: readonly Dispose[]): Promise<void> {
  const errors: unknown[] = [];
  for (const dispose of [...disposers].reverse()) {
    try {
      await dispose();
    } catch (error) {
      errors.push(error);
    }
  }
  if (errors.length > 0) throw new DisposalError(errors);
}
```

This engineering policy is not part of the pure witness theorem. It is how the host tries to realise recovery when external operations may fail.

## 2.13 Exercises

### Core exercise 2.1 - `track` homomorphism

Implement `track` for uniform pairs and test:

$$
\operatorname{track}(\mathrm{id},\mathrm{id})
=\mathrm{id}
$$

and:

$$
\operatorname{track}((f_1,g_1)\circledast(f_2,g_2))
=
\operatorname{track}(f_1,g_1)\circ
\operatorname{track}(f_2,g_2).
$$

Explain in prose what it means for instrumentation to preserve composition.

### Core exercise 2.2 - Prefix invariant

Generate a list of reversible map operations. After every prefix, assert that the current accumulator recovers the original state.

### Core exercise 2.3 - Applied primitives

Implement command registration, event subscription, and one additional resource. Each method must register its inverse automatically with a scope.

Write a plugin that uses all three and demonstrate that `scope.dispose()` removes all visible resources.

### Core exercise 2.4 - Idempotent disposal

Test:

```ts
await scope.dispose();
await scope.dispose();
```

The second call should do nothing. Explain why the implementation prevents a semantically invalid repeated inverse application.

### Core exercise 2.5 - Nested scope

Create a child scope containing two effects and register it in a parent between two other effects. Record the disposal trace and verify exact LIFO order.

### Core exercise 2.6 - Best-effort failure

Make the middle of three disposers throw. Verify that the oldest disposer still runs and that the aggregate error reports the failure.

### Extension 2.7 - Structured concurrency

A timer callback begins an asynchronous task. Design an acquisition whose disposer:

1. prevents new tasks;
2. waits for in-flight tasks;
3. then releases the resource.

Compare this with simply calling `clearInterval`.

### Theory exercise 2.8 - Recovery preservation

Prove by induction on a sequence of witnessed effects that the accumulator recovers the initial state when the inverses are applied in LIFO order.

Use the one-step witness as the induction step.

## 2.14 Counterexample clinic

### Counterexample A: FIFO disposal

Change the scope to run disposers in insertion order. Use two operations on the same key to show recovery failure.

### Counterexample B: global snapshot

Replace local inverses with one snapshot of the whole context at scope creation. Interleave two scopes and show that disposing the earlier scope erases the later scope's contribution.

### Counterexample C: aliasing

Return a mutable map as both the initial and successor state in the pure model. Mutate it after capturing the “initial” state. Show that the witness test can become meaningless because the supposed historical value has changed by aliasing.

Explain why immutable state or defensive copying is useful for the mathematical model even if the production realisation mutates in place.

### Counterexample D: forgotten mediation

Have a component call the raw command map directly rather than `ctx.commands.register`. Scope disposal leaves the command installed. The effect system is complete only relative to the boundary of operations that pass through it.

## 2.15 Milestone A submission

Milestone A is complete when the repository contains:

- a pure reversible-effect algebra;
- an effect context with `perform` and `recover`;
- property tests for witness, composition, and the prefix invariant;
- an imperative `EffectScope` with idempotent, best-effort LIFO disposal;
- at least three useful context-mediated resource primitives;
- a demonstration plugin that installs and withdraws all its resources;
- a short report distinguishing local LIFO recovery from selective removal under interleaving.

## 2.16 Reading

**Primary paper:** complete Section 3.1, including the independence subsection even though Lab 5 develops it in detail; read Section 5.1.1 for the implementation correspondence.

**Applied comparison:** React's effect cleanup pattern is a useful familiar comparison, but note its different constraints and lifecycle semantics.

**Optional systems reading:** the paper's related-work discussion of interposed reclamation and recovery domains provides examples where a platform records acquisitions at an interface it controls.

EOF
```

```unknown
bash -lc cat > /mnt/data/work/handbook/chapters/04-lab3.md <<'EOF'
# Lab 3: Reactive Coeffects and Typed Dependency Contexts

## Purpose

Effects answer: **what does this computation change?** Coeffects answer: **what does this computation require from its environment?**

In a static type system, a coeffect annotation may record resource use, permissions, contextual data, or variable usage. The course paper takes the broad idea of environmental requirements and makes it operational at runtime. A component declares dependency keys; the runtime stores provided values; and every relevant context change is classified as activating, deactivating, or neutral for each component.

This lab builds that mechanism. At the end, components inserted in any order remain inactive until their requirements are satisfied and deactivate automatically when a provider disappears.

## Learning outcomes

After this lab you can:

- distinguish effects from coeffects without treating them as exact mirror-image APIs;
- implement a typed finite dependency context;
- define and evaluate a coeffect specification;
- implement satisfaction and notification;
- explain why `set` is itself a revertible effect;
- propagate provider changes to affected components;
- detect simple dependency cycles;
- state the local spatial-composability guarantee.

## 3.1 Why dependencies are more than parameters

A function parameter makes a requirement explicit within a call:

```ts
function makeSummary(clock: Clock, notes: Notes): Summary
```

This is excellent static composition. The caller chooses `clock` and `notes` before the function runs. Dynamic composition adds time:

- `notes` may not exist yet;
- a provider may be replaced while the process remains alive;
- a component may need to stop while a requirement is absent;
- different component contexts may resolve the same logical key differently.

A runtime registry is therefore not merely a bag of globals. It participates in lifecycle decisions.

## 3.2 Effects and coeffects

### Definition: effect

An **effect** describes or realises how a computation modifies its environment.

Examples:

- register a command;
- add a service binding;
- mutate shared state;
- create a child component.

### Definition: coeffect

A **coeffect** describes what a computation requires or assumes from its environment.

Examples:

- a database service must be available;
- a file capability must permit writes to a path;
- an execution context must provide a clock;
- a variable may be used at most once;
- a computation requires data from a particular region or time.

For Mini-Cordis, the principal coeffects are typed service dependencies.

### Worked classification

| Statement | Effect, coeffect, or both? | Reason |
|---|---|---|
| “Registers route `/health`” | effect | changes the router |
| “Requires a logger” | coeffect | depends on environmental service |
| “Provides a database service” | both | adding the binding is an effect; consumers treat it as a coeffect |
| “May emit network traffic” | effect description | describes environmental impact |
| “Requires permission `read:/tmp`” | coeffect | environmental authority is required |

The same service binding connects the two directions: providing it changes the context; consuming it expresses a requirement.

> **Side topic: Reader and State intuition.** A stateful computation is often represented as $S\to(S\times A)$: it transforms an environment. A reader computation is $R\to A$: it obtains a result from an environment it requires. This is useful intuition, but the paper's runtime coeffects are not simply an implementation of the Reader monad or a comonad.

## 3.3 The coeffect context

### Motivation

The runtime needs one place where providers install typed values and consumers resolve them.

### Definition: key space and value family

Let $K$ be a set of dependency keys. Each key $k\in K$ has an associated value type $V_k$.

Examples:

```text
ClockKey      -> Clock
NotesKey      -> Notes
DatabaseKey   -> Database
LoggerKey     -> Logger
```

### Definition: coeffect context

The **coeffect context** is a finite dependent partial function:

$$
\Sigma=(k:K)\rightharpoonup V_k.
$$

For a state $\sigma\in\Sigma$:

- $\operatorname{dom}(\sigma)$ is the set of keys currently bound;
- $\sigma(k)$ is the value at $k$, when present;
- $\sigma[k\mapsto v]$ extends the map;
- $\sigma\setminus k$ removes a binding.

### TypeScript representation

```ts
declare const keyType: unique symbol;

export interface Key<T> {
  readonly id: symbol;
  readonly name: string;
  readonly [keyType]?: T;
}

export function defineKey<T>(name: string): Key<T> {
  return { id: Symbol(name), name };
}

export class ServiceStore {
  private readonly values = new Map<symbol, unknown>();

  has<T>(key: Key<T>): boolean {
    return this.values.has(key.id);
  }

  get<T>(key: Key<T>): T | undefined {
    return this.values.get(key.id) as T | undefined;
  }
}
```

The generic `Key<T>` carries the static association between a key and its value type. Internally, the heterogeneous map stores `unknown`; the API restores type information at its boundary.

## 3.4 `get` and `set`

### Definition: lookup

For key $k$:

$$
\operatorname{get}(k):\Sigma\rightharpoonup V_k.
$$

Lookup requires $k\in\operatorname{dom}(\sigma)$.

### Definition: provision

For key $k$ and value $v\in V_k$:

$$
\operatorname{set}(k,v):
\Sigma\rightharpoonup
\Sigma\times(\Sigma\rightharpoonup\Sigma).
$$

Provision requires the key to be absent. It returns the extended context and an inverse that removes the same binding.

The key observation is that **coeffect provision is a revertible effect**.

```ts
set<T>(scope: EffectScope, key: Key<T>, value: T): Dispose {
  if (this.values.has(key.id)) {
    throw new Error(`already provided: ${key.name}`);
  }

  this.values.set(key.id, value);
  this.notify([key.id]);

  return scope.add(() => {
    this.values.delete(key.id);
    this.notify([key.id]);
  });
}
```

The binding appears during activation and disappears through the component's accumulated inverse.

### Counterexample: silent overwrite

If `set` silently replaces an existing provider, the old provider's inverse may later delete the new provider's binding. Single-source provision avoids that ambiguity in the core calculus. Multiplexing or scoped realms can be added later with explicit semantics.

## 3.5 Coeffect specifications

### Motivation

A component should not optimistically call `get` and fail halfway through activation. The runtime can check all declared dependencies before activation begins.

### Definition: coeffect specification

A **coeffect specification** is a finite set of keys:

$$
d\subseteq K.
$$

It records the dependencies a component declares.

```ts
export type Requirement = ReadonlySet<symbol>;
```

A typed component API can retain the actual key objects:

```ts
export interface ComponentDefinition {
  readonly name: string;
  readonly requires: readonly Key<unknown>[];
  readonly provides: readonly Key<unknown>[];
  activate(ctx: ComponentContext): Promise<void>;
}
```

The use of `Key<unknown>` means the list is heterogeneous; individual lookups remain typed through the original key value.

## 3.6 Satisfaction

### Definition: satisfaction predicate

A coeffect context $\sigma$ **satisfies** specification $d$ when every required key is present:

$$
\sigma\models d
\quad\Longleftrightarrow\quad
\forall k\in d.\;k\in\operatorname{dom}(\sigma).
$$

```ts
export function satisfied(
  store: ServiceStore,
  required: readonly Key<unknown>[]
): boolean {
  return required.every((key) => store.has(key));
}
```

### Worked example

Let:

```text
d_summary = {clock, notes}
```

Classify contexts:

| Context domain | Satisfies? | Missing |
|---|---:|---|
| `{}` | no | clock, notes |
| `{clock}` | no | notes |
| `{notes}` | no | clock |
| `{clock, notes}` | yes | none |
| `{clock, notes, logger}` | yes | none |

Extra keys do not invalidate satisfaction.

## 3.7 Notification as transition classification

### Motivation

After every provision or withdrawal, the runtime must determine whether a component crossed the boundary between satisfied and unsatisfied.

### Definition: notification

For a specification $d$ and old/new contexts $\sigma,\sigma'$:

$$
\operatorname{notify}_d(\sigma,\sigma')=
\begin{cases}
\mathrm{activating}
& \sigma\not\models d\land\sigma'\models d,\\
\mathrm{deactivating}
& \sigma\models d\land\sigma'\not\models d,\\
\mathrm{neutral}
& \text{otherwise.}
\end{cases}
$$

```ts
export type Notification =
  | "activating"
  | "deactivating"
  | "neutral";

export function classify(
  before: boolean,
  after: boolean
): Notification {
  if (!before && after) return "activating";
  if (before && !after) return "deactivating";
  return "neutral";
}
```

### Worked transition table

| Before | After | Classification |
|---:|---:|---|
| false | false | neutral |
| false | true | activating |
| true | false | deactivating |
| true | true | neutral |

A provider's value may change without changing the Boolean satisfaction result. Lab 4 replaces this Boolean with a provider identity view so that replacement is detected.

## 3.8 Reactive refresh

A simple runtime scans components affected by changed keys:

```ts
function notify(changed: ReadonlySet<symbol>): void {
  for (const fiber of runtime.fibers()) {
    const relevant = fiber.component.requires
      .some((key) => changed.has(key.id));

    if (relevant) refresh(fiber);
  }
}
```

`refresh` computes whether the fiber should be active:

```ts
function refresh(fiber: Fiber): void {
  const shouldRun = !fiber.retired &&
    satisfied(runtime.services, fiber.component.requires);

  if (shouldRun && fiber.state === "inactive") {
    activate(fiber);
  } else if (!shouldRun && fiber.state === "active") {
    deactivate(fiber);
  }
}
```

This two-state version is intentionally incomplete. It establishes local reactivity before asynchronous lifecycle states are added.

### Definition: local spatial composability

For one component considered against the context:

1. it begins activation only when its specification is satisfied;
2. every relevant context change is classified, so loss of satisfaction is detected and drives deactivation.

This is **local** because it does not yet guarantee that a provider waits for all dependent teardown before withdrawing the value. Lab 6 supplies the global ordering mechanism.

## 3.9 A complete worked scenario

Define keys:

```ts
interface Clock { now(): Date }
interface Notes { list(): readonly string[] }

const ClockKey = defineKey<Clock>("clock");
const NotesKey = defineKey<Notes>("notes");
```

Components:

```text
ClockProvider
  requires: {}
  provides: {clock}

NotesProvider
  requires: {}
  provides: {notes}

DailySummary
  requires: {clock, notes}
  provides: {}
  effect: register command "summary"
```

Trace:

```text
0. insert DailySummary
   store = {}
   summary satisfied? no
   summary state = inactive

1. insert ClockProvider and activate it
   store = {clock}
   notification for summary: neutral (still unsatisfied)

2. insert NotesProvider and activate it
   store = {clock, notes}
   notification for summary: activating
   summary registers command "summary"

3. retire NotesProvider
   notes binding is withdrawn in the simple model
   notification for summary: deactivating
   summary removes command "summary"
```

The ordering in step 3 is not yet safe if summary teardown needs `notes`; this limitation is intentional and will become an exercise.

## 3.10 Dependency cycles

### Motivation

A specification can prevent activation forever.

```text
A requires b, provides a
B requires a, provides b
```

Neither component can activate first because each requires a key only the other can provide after activation.

### Definition: precedence relation

For component instances $A$ and $B$, write:

$$
A\prec B
$$

when A may provide a key required by B.

A cycle in $\prec$ is a static warning that the involved components cannot bootstrap under the core activation rule.

### Worked graph

```text
A --provides a--> B requires a
^                         |
|                         |
+-- requires b <- provides b
```

The runtime can report:

```text
cycle: A -(a)-> B -(b)-> A
```

A cycle is not a scheduler deadlock in this simple model. No transition begins; the specifications are jointly unsatisfiable from the empty context.

### Decomposition strategy

An apparent mutual dependency can often be split into cores and integration components:

```text
ServerCore             AccessControlCore
     \                     /
      \                   /
       RequestMediation
       PolicyManagement
```

Neither core requires the other. Integration components require both.

## 3.11 Implementation task

Create:

```text
src/core/key.ts
src/core/service-store.ts
src/core/specification.ts
src/core/reactive.ts
```

Required API:

```ts
export interface Key<T> {
  readonly id: symbol;
  readonly name: string;
}

export class ServiceStore {
  has<T>(key: Key<T>): boolean;
  get<T>(key: Key<T>): T | undefined;
  provide<T>(scope: EffectScope, key: Key<T>, value: T): Dispose;
  snapshotDomain(): ReadonlySet<symbol>;
}

export function satisfied(
  domain: ReadonlySet<symbol>,
  requires: readonly Key<unknown>[]
): boolean;

export function classify(
  beforeSatisfied: boolean,
  afterSatisfied: boolean
): Notification;
```

Add a minimal `ReactiveRuntime` with component records and a synchronous two-state refresh loop. Avoid asynchronous code until Lab 6.

## 3.12 Properties

### Satisfaction monotonicity under unrelated extension

If $\sigma\models d$ and $k\notin d$, then extending the context at $k$ preserves satisfaction.

```ts
fc.assert(fc.property(specArb, domainArb, keyArb, (d, domain, k) => {
  fc.pre(satisfies(domain, d));
  fc.pre(!d.has(k));
  const extended = new Set(domain).add(k);
  expect(satisfies(extended, d)).toBe(true);
}));
```

### Exact effect of provision

Providing a fresh key adds exactly that key to the domain; disposing removes exactly that contribution.

### Notification consistency

`classify(before, after)` must agree with the truth table for all booleans.

### No missing access at activation

Instrument `get` so that activation records every key accessed. Assert that every accessed key occurs in the component's declared requirement set and is present in the committed environment.

## 3.13 Exercises

### Core exercise 3.1 - Typed keys

Implement `Key<T>` and `ServiceStore`. Demonstrate that:

```ts
const ClockKey = defineKey<Clock>("clock");
const clock: Clock | undefined = store.get(ClockKey);
```

is typed correctly, while assigning the result to `Database` is rejected by TypeScript.

### Core exercise 3.2 - Revertible provision

Implement `provide`. Test fresh-key provision, duplicate rejection, notification on installation, and notification on disposal.

### Core exercise 3.3 - Satisfaction and classification

Implement the formal definitions literally. Write table-driven unit tests covering all four truth-table rows and property tests over generated domains/specifications.

### Core exercise 3.4 - Dependency chain

Implement `Database`, `Repository`, and `WebAPI` components. Insert them in reverse dependency order and demonstrate eventual activation in provider order.

Then retire `Database` and record the deactivation trace.

### Core exercise 3.5 - Cycle report

Build the precedence graph from component declarations and report strongly connected components containing a cycle. Include the keys responsible for the edges.

### Core exercise 3.6 - Declared access

Reject a component that reads a service it did not declare. Compare these policies:

- throw at access time;
- reject component registration by static analysis of an explicit dependency list;
- permit raw `get` as an unsafe escape hatch.

State which policy Mini-Cordis uses.

### Extension 3.7 - Optional dependencies

Design a specification with required and optional keys. A change to an optional provider should notify the component without necessarily deactivating it. Define the new classification and give a transition table.

### Extension 3.8 - Capability metadata

A filesystem key provides an API, but each consumer should be restricted to particular paths. Sketch metadata attached to a requirement and an interception layer that enforces it without changing whether the dependency is satisfied.

### Theory exercise 3.9 - Local guarantee

State and justify the two parts of local spatial composability. Then explain why the guarantee does not yet ensure that a consumer can use a provider during its own teardown.

## 3.14 Counterexample clinic

### Counterexample A: optimistic access

Remove the satisfaction precondition and activate every component immediately. Construct a trace where `Repository` partially registers effects and then throws when `Database` is absent. Explain why effect rollback helps but does not make implicit dependencies desirable.

### Counterexample B: no notification on inverse

Notify on service installation but not on disposal. A dependent remains active with a missing provider. Write a test that catches the stale state.

### Counterexample C: duplicate providers

Allow two providers to write the same key in one flat store. Load A, load B, unload A. Depending on the inverse, A may delete B's value or restore a stale A value. Explain why multiplexing requires provider identities or realms rather than silent overwrite.

### Counterexample D: cycle mistaken for transient absence

Insert a cyclic pair and have the runtime wait indefinitely without diagnostics. Add cycle detection and explain the difference between a dependency declaration cycle and a schedule-dependent deadlock.

## 3.15 Deliverable checklist

- [ ] Keys retain a static association with their value types.
- [ ] The service store is a finite partial map with explicit preconditions.
- [ ] Provision is tracked as a revertible effect.
- [ ] Satisfaction is checked before activation.
- [ ] Install and withdrawal both trigger notification.
- [ ] The dependency chain activates and deactivates reactively.
- [ ] Undeclared access is rejected or clearly marked unsafe.
- [ ] Cycles are reported with component and key information.

## 3.16 Reading

**Primary paper:** Sections 2.2, 2.3, 3.2.1, and 3.2.2. Skim 3.2.3 to see how isolation and interception generalise the flat table.

**Coeffects:** Petricek, Orchard, and Mycroft, *Coeffects: Unified Static Analysis of Context-Dependence*. Focus on motivation and examples of environmental requirements; the complete graded calculus is optional.

**Optional deeper route:** Petricek's *Context-Aware Programming Languages* thesis begins with a broader introduction before the categorical and graded details.

EOF
```

The structure now includes nine implementation labs, executable-theorem checkpoints, counterexample clinics, a glossary, API reference, and staged theory-reading pathway; I’m now writing the chapters and examples.

```unknown
bash -lc cat > /mnt/data/work/handbook/chapters/05-lab4.md <<'EOF'
# Lab 4: Components, Fibers, Target Views, and Operational Semantics

## Purpose

Lab 3 stored component definitions and toggled a Boolean `active` flag. That is insufficient for a real dynamic runtime. One component definition may be instantiated more than once; each instance needs its own lifecycle state and accumulated inverse. A component may remain satisfiable while the *identity* of one provider changes. The runtime must distinguish “the same keys exist” from “the same providers remain committed.”

This lab introduces the paper's central operational objects:

- **component:** a reusable definition;
- **fiber:** one running instance of a component;
- **registry:** the collection of fibers in a runtime state;
- **target view:** the provider resolution a fiber should currently use;
- **committed view:** the provider resolution against which it actually activated;
- **quiescence:** every fiber agrees with its current target.

You will also learn to read and write small-step operational rules.

## Learning outcomes

After this lab you can:

- represent a component as requirements, provisions, and an effect program;
- distinguish a component definition from a fiber instance;
- implement insertion, retirement, and removal separately;
- compute target views using provider identities;
- explain why value equality and Boolean satisfaction are insufficient;
- translate between inference rules and runtime code;
- define quiescence for the two-state lifecycle;
- state and test basic registry well-formedness.

## 4.1 Component definitions

### Motivation

A component is more than an `activate` function. The runtime needs declarations before activation so that it can reason about dependencies and provider conflicts.

### Definition: component

Over context $\Gamma$, a component is modelled as a triple:

$$
(d,p,e)
$$

where:

- $d$ is the coeffect specification: keys required from the environment;
- $p$ is the provision: keys the component may provide;
- $e$ is a witnessed effect program run when the component is active.

A student-facing API is:

```ts
export interface Component {
  readonly name: string;
  readonly requires: readonly Key<unknown>[];
  readonly provides: readonly Key<unknown>[];
  activate(ctx: ComponentContext): Promise<void>;
}
```

The component definition is reusable. It has no per-instance `state`, `dispose`, or provider resolution.

### Provision as an interface contract

`provides` declares what the component *may* install. The runtime can use it to reject conflicting providers before running arbitrary activation code. For the core labs, distinct fibers must have disjoint provisions.

Later, totality will ask whether an active component actually installs every key it declares.

## 4.2 Fibers

### Motivation

The same component can be used in different contexts or with different configuration. Each use needs separate identity, lifecycle state, committed providers, and effects.

### Definition: fiber

A **fiber** is one instantiated component carrying runtime fields of its own.

```ts
export type FiberId = string & { readonly __fiberId: unique symbol };

export interface Fiber {
  readonly id: FiberId;
  readonly component: Component;
  readonly parent: FiberId | "root";
  readonly scope: EffectScope;

  retired: boolean;
  state: FiberState;
  target: ProviderView | null;
  committed: ProviderView | null;
}
```

In this lab:

```ts
export type FiberState = "inactive" | "active";
```

Lab 6 expands the state machine.

### Component versus fiber

| Component | Fiber |
|---|---|
| reusable definition | one runtime instance |
| declares `requires` and `provides` | stores actual provider identities |
| owns activation code | owns one effect scope/disposer |
| no lifecycle state | inactive/active/etc. |
| may be instantiated many times | has fresh stable identity |

### Worked example

One `LoggerConsumer` component can be instantiated twice:

```text
fiber F1: LoggerConsumer in tenant A context
fiber F2: LoggerConsumer in tenant B context
```

Even if the definitions are identical, they may resolve `logger` to different providers and must unload independently.

## 4.3 The registry

### Definition: registry

A **registry** is a finite mapping from fiber identity to fiber state:

$$
F_\gamma:\mathbb{N}\rightharpoonup\mathcal{F}_\Gamma.
$$

Mini-Cordis uses:

```ts
class Runtime {
  private readonly registry = new Map<FiberId, Fiber>();
}
```

Provider lookup is derived from active fibers in the registry rather than from an unrelated global map.

### Definition: provider

A fiber $m$ is the provider of key $k$ in state $\gamma$ when:

1. $m$ is active;
2. $k$ occurs in its installed service table;
3. no other active fiber provides $k$ in the same realm.

In the flat single-source model, `providerOf(key)` returns zero or one `FiberId`.

## 4.4 Orchestration versus lifecycle

### Motivation

An external orchestrator may ask for a component to exist or stop existing. It should not directly force a component into `active`; dependency satisfaction and effect execution determine that.

### Definition: orchestration operation

An **orchestration operation** is an external input such as:

- insert a new fiber;
- retire an existing fiber;
- remove a retired inactive fiber.

### Definition: lifecycle transition

A **lifecycle transition** is a runtime-driven step that moves a fiber toward its target, such as activation or unloading.

Separating them prevents a caller from bypassing cleanup.

## 4.5 Insert, retire, remove

### Insert

**Motivation.** Insertion creates a fiber record but should not assume dependencies already exist.

Simplified rule:

$$
\frac{
 n\notin\operatorname{dom}(F_\gamma)
 \qquad
 p_n\cap p_m=\varnothing\text{ for every existing }m
}{
 \gamma\Rightarrow
 \gamma[n\mapsto\langle d,p,e,\mathrm{inactive}\rangle]
}
\;\textsc{Insert}
$$

Code:

```ts
insert(component: Component, parent: FiberId | "root" = "root"): Fiber {
  assertProvisionDisjoint(component.provides);

  const fiber: Fiber = {
    id: freshFiberId(),
    component,
    parent,
    scope: new EffectScope(),
    retired: false,
    state: "inactive",
    target: null,
    committed: null
  };

  this.registry.set(fiber.id, fiber);
  this.refreshAll();
  return fiber;
}
```

### Retire

**Motivation.** A request to remove an active fiber must first drive deactivation. Deleting the record immediately would lose its accumulated inverse.

```ts
retire(id: FiberId): void {
  const fiber = this.requireFiber(id);
  fiber.retired = true;
  this.refreshAll();
}
```

Retirement is a monotone request: once true, it does not return to false for that fiber identity.

### Remove

**Motivation.** Physical removal from the registry is safe only after the fiber is inactive and has no live child entries that require it as parent.

```ts
remove(id: FiberId): void {
  const fiber = this.requireFiber(id);
  if (!fiber.retired || fiber.state !== "inactive") {
    throw new Error("fiber is not removable");
  }
  if (this.hasChildren(id)) {
    throw new Error("remove children first");
  }
  this.registry.delete(id);
}
```

> **Common mistake: retirement is not deactivation.** Retirement changes what the target should be. A lifecycle rule performs the actual recovery.

## 4.6 From satisfaction to a target view

### Motivation

A Boolean says whether every key exists. It does not say *which provider* satisfied each key.

Suppose `DatabaseV1` is replaced by `DatabaseV2`, both exposing equal-looking objects. A consumer should usually reload because the provider's lifecycle, state, and identity have changed.

### Definition: provider view

For a specification $d$, a **provider view** maps every required key to the identity of its current provider:

$$
\omega:d\to\mathbb{N}.
$$

```ts
export type ProviderView = ReadonlyMap<symbol, FiberId>;
```

### Definition: target view

The **target view** of fiber $n$ in state $\gamma$ is:

$$
\operatorname{target}_n(\gamma)=
\begin{cases}
\bot,
& n\text{ is retired or a requirement is unsatisfied},\\
(k\mapsto\operatorname{provider}_k(\gamma)),
& \text{otherwise.}
\end{cases}
$$

Use `null` for $\bot$:

```ts
function targetOf(fiber: Fiber): ProviderView | null {
  if (fiber.retired) return null;

  const entries: Array<readonly [symbol, FiberId]> = [];
  for (const key of fiber.component.requires) {
    const provider = this.providerOf(key);
    if (provider === undefined) return null;
    entries.push([key.id, provider.id]);
  }
  return new Map(entries);
}
```

### Definition: committed view

The **committed view** is the provider view recorded when activation begins or commits. It answers:

> Against which provider identity did this fiber install its effects?

```ts
fiber.committed = copyView(target);
```

The target may later move. The committed view remains fixed until deactivation completes.

### View equality

Map object identity is not view equality. Compare key-provider pairs:

```ts
function sameView(a: ProviderView | null, b: ProviderView | null): boolean {
  if (a === null || b === null) return a === b;
  if (a.size !== b.size) return false;
  for (const [key, provider] of a) {
    if (b.get(key) !== provider) return false;
  }
  return true;
}
```

## 4.7 Why provider identity matters

### Worked replacement trace

Initial state:

```text
DatabaseV1 fiber D1 active, provides db
Consumer fiber C active, committed {db -> D1}
```

Replacement:

```text
D1 leaves
D2 becomes active, provides an equal Database facade
current target of C = {db -> D2}
committed view of C = {db -> D1}
```

Although satisfaction remains true, the views differ. C must unload and reload.

### Counterexample: value-based target

If target equality compares service values and both providers expose `{query: sameFunction}`, the consumer may remain active with captured references, transactions, or teardown assumptions tied to D1. Provider identity gives a stable lifecycle-level distinction.

### Freshness

A removed fiber ID should not be reused, or stale committed views could accidentally point at a new fiber. Use monotonically increasing IDs, UUIDs, or unforgeable symbols.

## 4.8 The base lifecycle rules

### Activation rule

A simplified reload rule is:

$$
\frac{
 \theta_n=\mathrm{Inactive}
 \qquad
 \omega=\operatorname{target}_n(\gamma)\neq\bot
 \qquad
 e_n(\gamma)=(\delta,g)
}{
 \gamma\longrightarrow
 \delta[\theta_n\mapsto\mathrm{Active}(g,\omega)]
}
\;\textsc{Reload}
$$

Read it in order:

1. fiber $n$ is inactive;
2. its target is a concrete provider view $\omega$;
3. its effect program returns successor $\delta$ and inverse $g$;
4. the result stores $g$ and $\omega$ in the active lifecycle state.

Imperative form:

```ts
async function activate(fiber: Fiber, target: ProviderView): Promise<void> {
  fiber.committed = copyView(target);
  await fiber.component.activate(this.contextFor(fiber));
  fiber.state = "active";
}
```

The fiber's `EffectScope` is the imperative accumulator.

### Unload rule

$$
\frac{
 \theta_n=\mathrm{Active}(g,\omega)
 \qquad
 \operatorname{target}_n(\gamma)\neq\omega
 \qquad
 g(\gamma)=\delta
}{
 \gamma\longrightarrow
 \delta[\theta_n\mapsto\mathrm{Inactive}]
}
\;\textsc{Unload}
$$

Imperative form:

```ts
async function deactivate(fiber: Fiber): Promise<void> {
  await fiber.scope.dispose();
  fiber.committed = null;
  fiber.state = "inactive";
}
```

The two-state model treats the whole transition as atomic, immediate, and infallible. Lab 6 removes those idealisations.

## 4.9 Quiescence

### Motivation

A dynamic runtime may temporarily contain fibers whose state does not match current dependencies. We need a definition of “settled.”

### Definition: quiescent state

A state is **quiescent** when every fiber agrees with its target:

- an inactive fiber has target $\bot$;
- an active fiber's committed view equals its target view.

```ts
function isQuiescent(): boolean {
  for (const fiber of this.registry.values()) {
    const target = this.targetOf(fiber);
    if (fiber.state === "inactive") {
      if (target !== null) return false;
    } else {
      if (!sameView(target, fiber.committed)) return false;
    }
  }
  return true;
}
```

Quiescence is not “nothing can ever change.” It means no lifecycle transition is currently demanded by the state and orchestration inputs already received.

## 4.10 Refresh to a fixed point

In the synchronous base model, repeatedly apply any enabled lifecycle step until quiescent:

```ts
async function settle(): Promise<void> {
  while (!this.isQuiescent()) {
    const enabled = this.enabledLifecycleSteps();
    if (enabled.length === 0) {
      throw new Error("non-quiescent state with no enabled step");
    }
    await enabled[0]();
  }
}
```

Choosing `enabled[0]` is one scheduler. A random scheduler is useful for testing. The calculus permits any legal choice.

### Definition: nondeterministic semantics

A transition system is **nondeterministic** when a state may have more than one legal successor. This does not mean the implementation uses randomness. It means the semantics does not commit to one schedule.

Confluence will later ask whether different legal schedules reach equivalent normal forms.

## 4.11 Registry well-formedness

Even the base runtime should maintain invariants.

### Definition: well-formed registry, simplified

A registry is well formed when:

1. every non-root parent ID refers to an existing fiber;
2. distinct fibers have disjoint declared provisions in the flat realm;
3. every active fiber has a committed view total on its requirements;
4. every provider named by an active fiber's committed view exists and is active.

```ts
function assertWellFormed(runtime: Runtime): void {
  // Check parent references, provision disjointness,
  // view totality, and provider activity.
}
```

These conditions are not arbitrary data validation. Later proofs rely on them to show that provider lookup is unambiguous and stale committed names cannot survive removal.

## 4.12 Child components

### Motivation

A component may instantiate another component during activation. The child's lifetime should be bounded by the parent.

Treat `ctx.use(child)` as an effect:

```ts
use(component: Component): Fiber {
  const child = runtime.insert(component, this.fiber.id);

  this.fiber.scope.add(async () => {
    runtime.retire(child.id);
    await runtime.settle();
    runtime.remove(child.id);
  });

  return child;
}
```

The inverse retires rather than blindly deletes because the child may still be active and own effects.

This operation gives the runtime a tree of component instances while dependency edges may cross the tree.

## 4.13 Implementation task

Create:

```text
src/core/component.ts
src/core/fiber.ts
src/core/runtime.ts
src/core/view.ts
```

Required public API:

```ts
export class Runtime {
  insert(component: Component, parent?: FiberId | "root"): Fiber;
  retire(id: FiberId): void;
  remove(id: FiberId): void;
  settle(options?: { scheduler?: Scheduler }): Promise<void>;
  targetOf(id: FiberId): ProviderView | null;
  assertWellFormed(): void;
  isQuiescent(): boolean;
}
```

Keep the base lifecycle synchronous from the semantic perspective: each activation or deactivation is one awaited step with no concurrent interleaving inside it.

## 4.14 Worked schedule comparison

Components:

```text
Clock      provides clock
Notes      provides notes
Summary    requires clock, notes
Metrics    requires clock
```

After all fibers are inserted, both schedules are legal:

```text
Schedule A:
  activate Clock
  activate Notes
  activate Summary
  activate Metrics

Schedule B:
  activate Notes
  activate Clock
  activate Metrics
  activate Summary
```

If effects are independent, both quiescent states should be observationally equivalent. The base runtime does not prove this yet; it gives a concrete set of schedules for Lab 5.

## 4.15 Exercises

### Core exercise 4.1 - Component/fiber separation

Refactor the Lab 3 records so that component definitions contain no runtime lifecycle fields. Demonstrate two fibers of one consumer component unloading independently.

### Core exercise 4.2 - Insert, retire, remove

Implement the three operations with distinct preconditions. Write tests showing that:

- inserting does not force activation when requirements are absent;
- retiring an active fiber preserves its record until unload completes;
- removing an active or non-retired fiber is rejected;
- removing a parent with children is rejected.

### Core exercise 4.3 - Provider target view

Implement `targetOf` and `sameView`. Replace a provider with an equal-looking value under a fresh fiber ID and verify that the consumer reloads.

### Core exercise 4.4 - Operational rule translation

Choose one orchestration rule and one lifecycle rule. For each:

1. write the inference rule;
2. implement the guard and transition;
3. list every state field read;
4. list every state field written.

### Core exercise 4.5 - Quiescence

Implement `isQuiescent` and `settle`. Run at least fifty random legal schedulers on a small acyclic system and assert well-formedness after every step.

Do not yet assert equal endpoints; record whether they agree and bring the result to Lab 5.

### Core exercise 4.6 - Child registration

Implement `ctx.use`. Unloading a parent must retire and eventually remove the child, but the parent inverse must not discard a live child's accumulator.

### Extension 4.7 - Scoped providers

Allow two fibers to provide the same logical key in different realms. Add a realm mapping to the target calculation and explain how provision disjointness changes from global to per-realm.

### Theory exercise 4.8 - Why store providers, not values?

Give three distinct examples where two providers expose extensionally equal or structurally equal values but a consumer must still reload on replacement.

## 4.16 Counterexample clinic

### Counterexample A: Boolean target

Store only `satisfied: boolean`. Replace a provider without an unsatisfied interval. Show that the consumer remains active against a stale committed reference.

### Counterexample B: remove before unload

Delete a fiber record immediately on retirement. Its scope and inverse become unreachable; installed effects leak. Add a test that detects the leaked command or service.

### Counterexample C: reused identity

Reuse a numeric fiber ID after removal. Construct a stale view that accidentally appears valid for the new fiber. Fix the problem with non-reused IDs and an invariant that no committed view names a removed fiber.

### Counterexample D: component object as identity

Use the component definition object as provider identity. Two fibers of the same provider definition then collapse into one identity. Demonstrate incorrect view equality.

## 4.17 Milestone B submission

Milestone B is complete when Mini-Cordis has:

- typed dependency keys and revertible provision;
- separate component definitions and fibers;
- per-fiber effect scopes;
- insertion, retirement, and removal;
- provider-aware target and committed views;
- reactive settling to quiescence;
- child component registration;
- well-formedness checks after each step;
- a trace viewer showing state, target, committed view, and lifecycle rule.

## 4.18 Reading

**Primary paper:** Sections 4.1 and 4.2, plus the theory-to-implementation table in Section 5.1.

**Operational semantics:** selected small-step semantics material from Pierce or Harper. Focus on judgments, premises, state updates, preservation, and progress.

**Applied comparison:** dependency injection frameworks and service registries are useful contrasts. Ask what happens to existing consumers when a provider disappears or changes identity at runtime.

EOF
```

```unknown
bash -lc cat > /mnt/data/work/handbook/chapters/06-lab5.md <<'EOF'
# Lab 5: Independence, Commutation, and Observational Equivalence

## Purpose

Per-fiber accumulators tell the runtime *which* effects belong to each fiber. They do not by themselves prove that an inverse captured earlier remains correct after other fibers have changed the state.

This is the central interleaving problem:

```text
A applies effect a
B applies effect b
runtime removes A while B remains
```

A's inverse no longer meets the immediate state produced by `a`; it meets a state subsequently moved by `b`. Selective withdrawal is sound only when A's transformations and B's transformations interact in a controlled way.

The paper calls the required condition **independence**. It combines commutation of state transformations with stability of the inverses and continuations an effect chooses. The paper also weakens literal equality to **observational equivalence**, because physical state is often not restored byte for byte.

## Learning outcomes

After this lab you can:

- define commutation and explain its role in selective withdrawal;
- distinguish effect-function commutation from full independence;
- construct the transformation monoid generated by an effect;
- identify operations that commute because they touch distinct keys;
- define an observer and the resulting observational equivalence;
- explain why equivalence must be respected by operations and inverses;
- build a commutation matrix for a runtime API;
- generate minimized counterexamples when independence fails.

## 5.1 Why per-component stacks are not enough

### A safe interleaving

Let A register command `a` and B register command `b` in a map. Both registrations are present:

```text
{a -> handlerA, b -> handlerB}
```

A's inverse deletes `a`. Running it while `b` remains gives:

```text
{b -> handlerB}
```

This is the desired state: exactly B's contribution remains.

### An unsafe interleaving

Let A prepend middleware `A`; B prepend middleware `B`.

```text
initial: []
A:       [A]
B:       [B, A]
```

If A's inverse was “remove the first element,” applying it now removes B:

```text
[B, A] --undo A--> [A]
```

Even a more specific “remove A wherever it occurs” may alter ordering guarantees if middleware captures neighbours or receives position-dependent tokens.

The issue is not ownership alone. It is whether the operations can be moved past one another without changing observable behaviour.

## 5.2 Commutation

### Definition: commuting transformations

Two transformations $f,g:\Gamma\to\Gamma$ **commute** when:

$$
f\circ g\simeq g\circ f.
$$

With literal equality:

$$
\forall\gamma.\;f(g(\gamma))=g(f(\gamma)).
$$

Commutation says the two execution orders produce equivalent results.

### Worked example: distinct map keys

Let $f$ set key `a`; let $g$ set key `b`, with `a != b`.

```text
f(g({})) = {b, a}
g(f({})) = {a, b}
```

Map insertion order might differ internally, but lookup observations agree. Under map extensional equality, the operations commute.

### Counterexample: same key

Let $f$ set `x = 1` and $g$ set `x = 2`:

```text
f(g({})) = {x: 1}
g(f({})) = {x: 2}
```

They do not commute.

### Counterexample: ordered chain

Let $f$ prepend A and $g$ prepend B:

```text
f(g([])) = [A, B]
g(f([])) = [B, A]
```

If middleware order is observable, the operations do not commute.

## 5.3 The transformation monoid of an effect

### Motivation

A reversible effect function contains more than its forward state map. At different input states it may return different inverse functions. Independence must account for all transformations the effect can perform, forward and reverse.

### Definition: transformation generators

For effect $e:\Gamma\to\Gamma\times(\Gamma\to\Gamma)$, its generators include:

1. the forward map $\operatorname{pr}_1\circ e$;
2. every inverse $\operatorname{pr}_2(e(\gamma))$ that can be yielded at any input $\gamma$.

### Definition: transformation monoid

The **transformation monoid** $\mathcal{M}(e)$ is the smallest submonoid of $\Gamma\to\Gamma$ containing those generators. It therefore contains:

- identity;
- every generator;
- every finite composition of generators.

You rarely enumerate this monoid in code. The definition states the closure needed by proofs. For testing, use a finite family of representative generators and short compositions.

### Worked example

For `setValue("x", 5)`, the forward map always writes `5`, while the inverse may:

- delete `x` if it was absent;
- restore any integer previously stored at `x`.

The transformation family is richer than the one forward map.

## 5.4 Full independence

### Motivation

Forward commutation is not enough. An effect may choose a different inverse depending on a state changed by another effect.

### Definition: independence, simplified statement

Effects $e_1$ and $e_2$ are **independent** when:

1. every transformation generated by $e_1$ commutes, up to $\simeq$, with every transformation generated by $e_2$;
2. applying transformations of one effect does not change the inverse that the other effect yields, up to the appropriate equivalence;
3. for operations that return outcomes or continuations, one effect does not change the other's outcome or continuation choice.

The paper states this precisely using $\mathcal{M}(e)$ and equality/equivalence of yielded inverses.

### Why clause 2 is necessary

Consider an effect whose inverse depends on an unrelated-looking global mode:

```ts
const fragileEffect: Reversible<State> = (state) => {
  const next = { ...state, x: state.x + 1 };
  const undo = state.mode === "normal"
    ? (s: State) => ({ ...s, x: s.x - 1 })
    : (s: State) => ({ ...s, x: 0 });
  return [next, undo];
};
```

Another effect changes `mode`. The forward changes to `x` and `mode` may commute, yet evaluating `fragileEffect` before versus after the mode change yields different inverses. Reordering whole effect applications is not justified merely by forward commutation.

### Independence versus commutativity of composite effect functions

The equation:

$$
e_1\diamond e_2=e_2\diamond e_1
$$

compares complete forward results and the composite inverse each order happens to yield. Full independence is stronger: it relates every forward and reverse transformation across the two effects and requires stability of yielded data.

## 5.5 Selective withdrawal theorem, executable form

For pairwise independent witnessed effects $e_1,\ldots,e_n$, apply them in any order. The paper shows that their recorded inverses may be applied in any permutation and still recover the initial state, up to equivalence.

The component-level interpretation is:

> If A's effects are independent of B's effects, then applying A's accumulated inverse after B has moved the state removes A's contribution and preserves B's.

### Worked trace

Let:

```text
A: register command a
B: register command b
```

```text
gamma0 = {}
gamma1 = A(gamma0) = {a}
gamma2 = B(gamma1) = {a,b}
undoA(gamma2) = {b}
undoB({b}) = {}
```

Reverse order also works:

```text
undoB({a,b}) = {a}
undoA({a}) = {}
```

### Property schema

```ts
fc.assert(fc.property(independentProgramArb, (program) => {
  const initial = program.initial;
  const applied = applyAll(program.effects, initial);

  for (const permutation of selectedPermutations(program.effects.length)) {
    const recovered = applyInverses(applied, permutation);
    expect(observe(recovered)).toEqual(observe(initial));
  }
}));
```

For large lists, sample permutations rather than enumerate all factorially many.

## 5.6 Independence by separation of keys

### Definition: key-local operation

An operation is **local to key $k$** when its forward and inverse transformations read and write only the binding at $k$, leaving every other key unchanged.

### Distinct-key principle

Two key-local operations at distinct keys commute because each leaves the other's input untouched.

```text
operation at k:  reads/writes k, leaves k' unchanged
operation at k': reads/writes k', leaves k unchanged
```

This is one of the paper's major design payoffs. Reifying shared locations as separately keyed coeffects creates a structural route to independence.

### Worked example: route registrations

Model each route `(method,path)` as its own key. Registering `/a` and `/b` is independent.

If instead the router exposes one ordered middleware list key, insertions may not commute. The algebraic property belongs to the *interface*, not merely the underlying implementation.

> **Design lesson: commutativity is an API property.** A provider can often redesign an interface from one order-sensitive global structure into independent keyed registrations. This changes what the metatheory can guarantee.

## 5.7 Observational equivalence

### Motivation

Literal physical recovery is often impossible or irrelevant.

- an allocator's next ID advances;
- a hash map changes bucket layout;
- a fresh symbol is never reused;
- a cancelled timer leaves a historical record in debugging telemetry;
- garbage collection does not restore heap addresses.

A useful theorem should compare what clients can observe.

### Definition: observer

An **observer** is a permitted test or operation that can distinguish states by its definedness and result.

A simple Mini-Cordis observer is:

```ts
export type Observation = Readonly<{
  commands: readonly string[];
  serviceNames: readonly string[];
  activeFibers: readonly string[];
}>;

export function observe(runtime: Runtime): Observation {
  return {
    commands: runtime.commandNames().sort(),
    serviceNames: runtime.serviceNames().sort(),
    activeFibers: runtime.activeFiberNames().sort()
  };
}
```

### Definition: observational equivalence

States $\gamma$ and $\delta$ are **observationally equivalent**, written $\gamma\simeq\delta$, when no permitted observer can distinguish them.

For one finite observation function:

$$
\gamma\simeq\delta
\quad\Longleftrightarrow\quad
\operatorname{observe}(\gamma)=\operatorname{observe}(\delta).
$$

For a richer interface, equivalence considers all finite tests built from allowed operations and their outcomes.

### Worked example: fresh handles

```text
State A: liveHandles = {}, nextId = 10
State B: liveHandles = {}, nextId = 15
```

If `nextId` is hidden and allocated handles are only compared through a renaming-invariant API, A and B may be equivalent. If handles are returned as numbers and clients compare them by numeric equality, the difference becomes observable.

The interface determines the relation.

## 5.8 Operations must respect equivalence

### Motivation

It is unsafe to identify two states if a permitted operation later separates them.

### Definition: respecting an equivalence

A function $f:\Gamma\to\Gamma$ **respects** $\simeq$ when:

$$
\gamma\simeq\delta
\Longrightarrow
f(\gamma)\simeq f(\delta).
$$

This means $f$ is well defined on equivalence classes.

A reversible effect must respect equivalence both in the successor it computes and in the inverse it yields. The inverse itself must also respect equivalence.

### Counterexample

Suppose equivalence ignores an internal `secretMode`, but an operation branches on `secretMode` and returns visibly different commands. Then the operation does not respect the proposed equivalence. The relation was too coarse for the interface.

### Quotient intuition

A **quotient** $\Gamma/\simeq$ treats each equivalence class as one abstract state. A function that respects $\simeq$ descends to a well-defined function on the quotient.

You do not need to implement quotient objects. The idea explains why all relevant operations must preserve the relation.

## 5.9 Defining observations from coeffect interfaces

The paper assembles context equivalence from per-key equivalences. Each coeffect key exposes a value type and operations. Two values at a key are equivalent when the key's permitted operations cannot distinguish them.

Mini-Cordis can approximate this explicitly:

```ts
export interface ObservableKey<T, O> extends Key<T> {
  observe(value: T): O;
  equivalent(left: T, right: T): boolean;
}
```

Examples:

- a set-valued listener registry may compare listeners as an unordered set;
- a middleware chain compares order;
- an allocator may compare live capability structure up to renaming;
- a cache may ignore replacement policy metadata if no public operation reveals it.

### Strong versus weak observers

A stronger observer distinguishes more states and yields a finer equivalence. A weaker observer identifies more states and yields a coarser equivalence.

Coarsening helps prove recovery, but can become dishonest if it hides behaviour clients rely on.

## 5.10 Commutation matrix

Every team should maintain a **commutation matrix** for the runtime primitives.

| Operation A | Operation B | Independent? | Equivalence used | Reason or counterexample |
|---|---|---:|---|---|
| register command `a` | register command `b` | yes if names differ | command-map extensional equality | distinct keys |
| register command `a` | register command `a` | no / conflict | same | precondition conflict |
| subscribe listener L1 | subscribe listener L2 | often yes | unordered listener set | set-like registrations |
| prepend middleware A | prepend middleware B | no | ordered behaviour | request order differs |
| provide `clock` | provide `notes` | yes | per-key equivalence | distinct keys |
| allocate visible numeric ID | allocate visible numeric ID | generally no | numeric equality | order changes outcomes |
| allocate opaque capability | allocate opaque capability | possibly yes | renaming equivalence | handles not directly compared |

Do not fill the table by intuition alone. For each “yes,” write a property. For each “no,” record a concrete counterexample trace.

## 5.11 A practical independence checker

Full independence over all states and generated transformations is generally not decidable for arbitrary TypeScript functions. The lab checker is evidence, not a proof.

```ts
export interface EffectSample<S> {
  readonly name: string;
  readonly apply: Reversible<S>;
}

export function checkPair<S>(
  left: EffectSample<S>,
  right: EffectSample<S>,
  samples: readonly S[],
  equivalent: Relation<S>
): readonly IndependenceFailure<S>[];
```

For each sample state:

1. apply left then right and right then left;
2. compare forward endpoints;
3. compare each inverse moved past the foreign forward map;
4. compare inverses yielded at foreign-moved states over additional samples;
5. record the smallest trace that fails.

The checker should clearly state that passing finite samples does not establish the universal theorem.

## 5.12 Worked counterexample: forward commutation is insufficient

State:

```ts
interface State {
  readonly x: number;
  readonly mode: "normal" | "reset";
}
```

Effect A increments `x` but chooses its inverse from `mode` at application time. Effect B toggles `mode`.

Forward maps touch different fields and commute:

```text
increment x; toggle mode == toggle mode; increment x
```

But A applied after B may yield a different inverse from A applied before B. The second independence clause fails.

Ask the checker to report:

```text
initial = {x: 3, mode: normal}
A inverse before B = decrement
A inverse after B  = reset x to 0
```

## 5.13 Trace equivalence

### Motivation

Two schedules may differ only by swapping adjacent independent actions.

```text
A B C
B A C
```

If A and B are independent, the traces should be considered equivalent.

### Definition: adjacent-swap trace equivalence

Generate an equivalence on action sequences by the rule:

$$
xaby\sim xbay
$$

whenever actions $a$ and $b$ are independent.

This is the core intuition of Mazurkiewicz trace theory. It will support the confluence argument in Lab 8.

### Worked example

If `register a` and `register b` are independent:

```text
register a; register b; start timer
~
register b; register a; start timer
```

If `prepend auth` and `prepend logging` are not independent, their order cannot be swapped in the trace equivalence.

## 5.14 Implementation task

Add:

```text
src/core/observation.ts
src/core/independence.ts
test/properties/independence.test.ts
lab-notes/commutation-matrix.md
```

Required APIs:

```ts
export type Relation<T> = (left: T, right: T) => boolean;

export function commutes<S>(
  f: Endo<S>,
  g: Endo<S>,
  states: readonly S[],
  equivalent: Relation<S>
): boolean;

export function checkIndependence<S>(
  left: Reversible<S>,
  right: Reversible<S>,
  states: readonly S[],
  equivalent: Relation<S>
): readonly IndependenceFailure<S>[];
```

Extend runtime traces so every state-changing step records:

- acting fiber;
- operation name;
- key or resource touched;
- before/after observation;
- inverse identity or description.

## 5.15 Exercises

### Core exercise 5.1 - Command independence

Prove and property-test that registrations at distinct command names are independent under extensional map equality. Include forward maps and both yielded inverses.

### Core exercise 5.2 - Ordered middleware counterexample

Implement two middleware insertion operations. Find the smallest request observation that distinguishes the two orders. Document why the interface is non-commutative.

### Core exercise 5.3 - State-dependent inverse stability

Construct two effects whose forward maps commute but whose yielded inverses are not stable. Make `checkIndependence` catch the failure.

### Core exercise 5.4 - Observer design

Define an observation function for your applied domain. For every field omitted from the observation, answer:

1. can a component access it directly?
2. can an allowed operation branch on it?
3. can it alter an allowed operation's outcome?

If any answer is yes, justify why equivalence may still ignore it or refine the observer.

### Core exercise 5.5 - Renaming equivalence

Model an allocator returning opaque handles. Define equivalence up to a bijection between live handles. Demonstrate two allocation orders that are unequal literally but equivalent under renaming.

Then make handle numbers directly comparable and show the equivalence is no longer admissible.

### Core exercise 5.6 - Arbitrary unload order

Generate a family of pairwise independent command registrations. Apply them in one order and dispose them in several permutations. Assert recovery to the empty command observation.

### Core exercise 5.7 - Commutation matrix

Complete the matrix for every context primitive implemented so far. Every row must link to either:

- a property test; or
- a minimized counterexample test.

### Extension 5.8 - Static effect footprints

Annotate primitives with read/write key sets. Implement a conservative rule:

```text
disjoint write/read footprints => candidate independence
```

Explain why footprints can establish some independence cases but cannot replace semantic checks for outcome or inverse stability.

### Theory exercise 5.9 - Selective withdrawal

For two independent witnessed effects A and B, derive algebraically why:

```text
apply A, apply B, undo A
```

reaches the state produced by B alone. State exactly where commutation is used.

## 5.16 Counterexample clinic

### Counterexample A: equality too strong

Use an allocator whose next-ID counter changes after allocate/release. Literal recovery fails. Define a justified observer under which it succeeds.

### Counterexample B: equivalence too weak

Define an observer that only counts commands, ignoring names. States `{a}` and `{b}` become equivalent, yet invoking `a` distinguishes them. Refine the observer.

### Counterexample C: distinct underlying fields, shared outcome

Two effects mutate distinct internal counters but both change the public `status()` result. A naive disjoint-write analysis calls them independent; the observer disproves it.

### Counterexample D: pairwise test blind spot

Test commutation only at the empty state. Two registrations appear independent there but conflict after a third operation creates an alias between keys. Add generated reachable states and explain why the theorem quantifies over all relevant states.

## 5.17 Deliverable checklist

- [ ] The runtime has an explicit observation function or family of per-key equivalences.
- [ ] Operations and inverses are tested for respect of equivalence.
- [ ] The independence checker covers forward commutation and yielded inverse stability.
- [ ] The commutation matrix covers every primitive.
- [ ] Each non-independent pair includes a minimized counterexample.
- [ ] Independent effects can be withdrawn in sampled arbitrary orders.
- [ ] The lab report distinguishes finite testing evidence from universal proof.

## 5.18 Reading

**Primary paper:** Section 3.1.3 and Section 3.3.2; read Theorems 40 and 42 for the distinct-key and coeffect-mediated independence arguments. Then read Section 4.4.2 for the component-level recovery theorem.

**Category theory bridge:** monoids, opposite monoids, equivalence relations, and quotient intuition. Advanced categorical machinery is not required.

**Concurrency bridge:** a short introduction to Mazurkiewicz traces or partial-order reduction. Focus on swapping adjacent independent actions.

**Optional deeper paper:** Heunen, Kaarsgaard, and Karvonen, *Reversible Effects as Inverse Arrows*. Compare its stronger global reversibility with the paper's runtime-supplied one-sided inverses.

EOF
```

```unknown
bash -lc cat > /mnt/data/work/handbook/chapters/07-lab6.md <<'EOF'
# Lab 6: Transitions in Progress - Iteration, Asynchrony, Failure, and Safe Withdrawal

## Purpose

The base lifecycle treats activation and deactivation as atomic, immediate, and infallible. Real transitions are none of these.

- Activation may consist of many effects separated by useful interruption points.
- An effect may await I/O while the dependency graph changes.
- An operation may fail after earlier effects have succeeded.
- A provider may need to remain usable while its consumers perform asynchronous teardown.

This lab introduces explicit transition states and an **effect iterator**. It then implements the most subtle spatial guarantee in the paper: a provider stops being available for new resolution before it withdraws its binding, allowing committed consumers to deactivate first and continue using that provider during teardown.

## Learning outcomes

After this lab you can:

- explain why a transition requires intermediate lifecycle states;
- represent activation as an iterator that yields inverses;
- distinguish interruption at a step boundary from cancellation of an operation already in flight;
- implement rollback after partial activation and failure;
- define transition inertia;
- separate leaving from unloading;
- implement committed dependency access during teardown;
- implement and justify the `relied` guard;
- state the global spatial ordering guarantee.

## 6.1 The four-state lifecycle

### Motivation

If loading takes time, `inactive` and `active` do not describe the period between them. If unloading waits for dependents or asynchronous cleanup, the same problem occurs in reverse.

### Definition: lifecycle state

Mini-Cordis now uses:

```ts
export type FiberState =
  | { readonly tag: "inactive"; readonly error?: unknown }
  | {
      readonly tag: "loading";
      readonly committed: ProviderView;
      readonly accumulator: Dispose;
    }
  | {
      readonly tag: "active";
      readonly committed: ProviderView;
      readonly accumulator: Dispose;
    }
  | {
      readonly tag: "unloading";
      readonly committed: ProviderView;
      readonly accumulator: Dispose;
      readonly outcome?: unknown;
    };
```

The exact fields may be stored separately in your implementation. The semantic point is that loading and unloading are states the runtime can observe and reason about.

```text
                 finish
  INACTIVE -----------------> ACTIVE
      |                         |
      | begin                   | leave
      v                         v
   LOADING ----------------> UNLOADING
      ^       divert/fail        |
      |                          | unload complete
      +--------------------------+
```

### Definition: installed fiber

A fiber is **installed** while it carries an accumulator and committed view: loading, active, or unloading. Inactive fibers carry no live contribution.

### Why loading fibers do not provide

A loading fiber may have installed only some of its declared services. Dependents should not activate against a provider that has not committed. Provider lookup therefore considers only `active` fibers.

## 6.2 Effect iteration

### Motivation

An activation program performs a sequence:

```text
register command
subscribe listener
open resource
start worker
provide service
```

If the target changes after the second step, the runtime should stop before launching the third and recover the first two. A single `Promise<Dispose>` exposes no boundary inside the transition.

### Definition: effect iterator

An **effect iterator** yields one inverse per completed effect and optionally continues with another step.

A convenient TypeScript realisation is an async generator:

```ts
export type EffectProgram = AsyncGenerator<Dispose, void, void>;

export interface Component {
  readonly name: string;
  readonly requires: readonly Key<unknown>[];
  readonly provides: readonly Key<unknown>[];
  activate(ctx: ComponentContext): EffectProgram;
}
```

Example:

```ts
async function* activateSummary(ctx: ComponentContext): EffectProgram {
  yield ctx.commands.register("summary", () => ctx.summary.run());
  yield ctx.events.on(NoteAdded, () => ctx.summary.refresh());
  yield await ctx.workers.start("summary-indexer");
}
```

Each successful yield is a rollback boundary.

### Pure recursive shape

The paper expresses an iterator recursively as a function that returns:

- a successor state;
- an inverse for this iteration;
- either no continuation or the next iterator.

The async generator is a host-language realisation of the same control structure.

## 6.3 Executing an iterator

```ts
async function execute(
  program: EffectProgram,
  guard: () => boolean
): Promise<Dispose> {
  const disposers: Dispose[] = [];

  while (guard()) {
    const result = await program.next();
    if (result.done) break;
    disposers.push(once(result.value));
  }

  return async () => {
    const errors: unknown[] = [];
    for (const dispose of [...disposers].reverse()) {
      try {
        await dispose();
      } catch (error) {
        errors.push(error);
      }
    }
    if (errors.length > 0) throw new DisposalError(errors);
  };
}
```

The guard is checked *between* iterations. It cannot undo an operation that has already been launched and not yet resolved.

### Definition: iteration boundary

An **iteration boundary** is a point after one effect has completed and yielded its inverse, but before the next effect begins.

The granularity of interruption is therefore chosen by the component author. A long step gives fewer interruption points; a fine-grained program gives more responsive rollback but more bookkeeping.

## 6.4 Begin, iterate, finish, and divert

### Begin

When an inactive fiber has a non-bottom target, it records that provider view and enters loading.

```ts
function begin(fiber: Fiber, target: ProviderView): void {
  fiber.state = {
    tag: "loading",
    committed: copyView(target),
    accumulator: noop
  };
}
```

### Iterate

If the current target still equals the committed target, one iteration may land. Its disposer is prepended to the accumulator.

### Finish

When the iterator is done and the target still matches, the fiber becomes active.

### Divert

If the target changes while loading, the transition does not commit. At a boundary, it enters unloading with the accumulator constructed so far.

```text
loading against {db -> D1}
new target becomes bottom or {db -> D2}
=> stop launching new iterations
=> recover completed iterations
=> return inactive
=> perhaps begin again against the new target
```

### Worked trace

```text
1. begin loading Summary against {clock -> C1, notes -> N1}
2. register command; yield undoCommand
3. subscribe listener; yield undoListener
4. Notes N1 starts leaving; target changes
5. divert before starting worker
6. undo listener
7. undo command
8. become inactive
```

The transition installed either all of its effects or a recoverable prefix.

## 6.5 Asynchrony and inertia

### Motivation

Suppose step 3 has already called `await workers.start()`. The target changes while the promise is pending. The runtime cannot pretend the operation never happened.

### Definition: inertia

**Transition inertia** means that once an asynchronous iteration is launched, it is allowed to land. The runtime responds to target changes after the landing by diverting into unloading.

```text
launch openResource against D1
D1 leaves while await is pending
openResource resolves and yields inverse
fiber immediately enters unloading
inverse closes the resource
```

The effect may briefly exist, but the fiber never advertises itself as active against a stale target.

### Cancellation is not assumed

Some operations support cancellation tokens. Cancellation remains an effect-specific protocol and may fail or race with completion. The semantic model is sound without assuming universal cancellation: launched work lands, yields an inverse if successful, and is recovered.

> **Common mistake: cancellation is not rollback.** Stopping future computation does not necessarily undo state already changed by the operation. A cancellation-aware operation still needs a recovery contract for completed work.

## 6.6 Failure during loading

### Motivation

A transition may fail after installing earlier effects:

```text
register route       succeeds
open database        succeeds
bind network port    fails
```

The fiber must not remain partially installed.

### Definition: failing effect step

A step either raises an error or yields a successor/inverse. A raise contributes no new inverse, but the accumulator for earlier successful steps remains available.

### Failure transition

On failure:

1. record the error as the intended inactive outcome;
2. enter unloading with the accumulator built so far;
3. run recovery;
4. arrive inactive/failed with no installed contribution.

```ts
async function reload(fiber: Fiber): Promise<void> {
  const target0 = requireTarget(fiber);
  fiber.committed = copyView(target0);

  try {
    fiber.dispose = await execute(
      fiber.component.activate(this.contextFor(fiber)),
      () => sameView(this.targetOf(fiber), target0)
    );

    if (sameView(this.targetOf(fiber), target0)) {
      fiber.state = "active";
      this.notifyProvided(fiber);
    } else {
      fiber.state = "unloading";
      await this.unload(fiber);
    }
  } catch (error) {
    fiber.failure = error;
    fiber.target = null;
    fiber.state = "unloading";
    await this.unload(fiber);
  }
}
```

In a careful implementation, `execute` itself should expose the accumulated disposer when an iteration throws. One design is a custom `ActivationFailure` carrying `recover`.

### Error policy

A failed fiber does not automatically retry in an unchanged environment. Retrying may loop forever. A later orchestration action or explicit reset may clear the error.

## 6.7 The provider withdrawal problem

### Motivation

Consider:

```text
Database D
    |
    v
Repository R
```

Repository teardown performs:

```ts
async function closeRepository(ctx: ComponentContext) {
  await ctx.get(DatabaseKey).flushConnections();
}
```

If D deletes the database binding before R finishes deactivating, R's cleanup fails. But if D remains visible as an active provider, new consumers may activate against a provider already trying to leave.

We need two different notions:

1. availability for **new target resolution**;
2. readability through an **already committed view**.

## 6.8 Leave versus unload

### Definition: leave

A provider **leaves** by changing from active to unloading. From that moment it is excluded from provider lookup for new target views.

Its service table and committed view remain physically present.

```ts
function leave(fiber: Fiber): void {
  if (fiber.state !== "active") throw new Error("not active");
  fiber.state = "unloading";
  this.notifyProvided(fiber);
}
```

The notification makes dependents' target views change, so they begin their own deactivation.

### Definition: unload

A provider **unloads** when it actually applies its accumulator and removes the services and other effects it installed.

Unload must wait until no installed dependent's committed view still resolves a key to that provider.

## 6.9 Committed dependency access

### Motivation

During teardown, target resolution says the dependency is gone, but the fiber's committed view says which provider it is still entitled to use until its own accumulator finishes.

### Definition: committed lookup

A component context resolves a declared key through the fiber's committed view, not through the current global provider lookup.

```ts
class ComponentContext {
  constructor(
    private readonly runtime: Runtime,
    private readonly fiber: Fiber
  ) {}

  get<T>(key: Key<T>): T {
    const committed = this.fiber.committed;
    if (committed === null) {
      throw new Error("inactive dependency access");
    }

    const providerId = committed.get(key.id);
    if (providerId === undefined) {
      throw new Error(`undeclared dependency: ${key.name}`);
    }

    return this.runtime.valueFromProvider(providerId, key);
  }
}
```

This keeps the same binding readable throughout one installed episode, including unloading.

### Access rule

A key access is legal only if:

1. the key appears in the component's declared specification;
2. the fiber has a committed provider for the key;
3. that provider remains installed.

## 6.10 The relied-on guard

### Definition: relied upon

Provider fiber $n$ is **relied upon** in state $\gamma$ when some other installed fiber $m$ has a committed key mapped to $n$.

$$
\operatorname{relied}_n(\gamma)
\Longleftrightarrow
\exists m\neq n,\;k\in d_m.
\operatorname{installed}_m(\gamma)
\land
\omega_m(k)=n.
$$

```ts
function reliedUpon(provider: Fiber): boolean {
  for (const consumer of this.registry.values()) {
    if (consumer.id === provider.id) continue;
    if (!isInstalled(consumer)) continue;

    for (const providerId of consumer.committed?.values() ?? []) {
      if (providerId === provider.id) return true;
    }
  }
  return false;
}
```

### Guarded unload

```ts
async function unload(fiber: Fiber): Promise<void> {
  await this.awaitUntil(() => !this.reliedUpon(fiber));
  await fiber.dispose();
  fiber.dispose = noop;
  fiber.committed = null;
  fiber.state = "inactive";
}
```

A practical event-driven implementation awaits the exact dependent transition tasks returned by notification rather than polling.

## 6.11 Why the guard does not necessarily deadlock

A wait-for graph can deadlock if nothing causes consumers to leave. The crucial sequence is:

1. provider enters `unloading`;
2. only `active` providers participate in new target calculation;
3. each committed consumer now has a target different from its committed view;
4. consumers enter unloading;
5. their committed views are discarded after their teardown;
6. the provider's guard eventually clears.

For an acyclic provider-consumer precedence graph and finite transitions, there is always a maximal consumer that can unload first.

### Worked chain

```text
Database D -> Repository R -> WebAPI W
```

Retire D:

```text
D leaves; no longer a target provider
R target changes; R leaves
W target changes; W leaves
W has no dependents; W unloads
R no longer relied upon by W; R unloads
D no longer relied upon by R; D unloads
```

This is reverse dependency order.

## 6.12 Global spatial ordering guarantee

The paper's ordering theorem can be read as three practical properties for a consumer episode:

1. a consumer begins only where all dependencies are provided;
2. the provider episode begins before the consumer episode and, if it ends, ends after the consumer episode;
3. the consumer reads the same provider binding throughout its installed episode, including teardown.

This is stronger than “notifications eventually happen.” It provides a temporal interval in which cleanup can safely use committed dependencies.

## 6.13 Resolution coherence during loading

A multi-step activation should not silently combine effects computed against two different provider resolutions.

Rules:

- each iteration may proceed only while `target == committed`;
- if the target changes at a boundary, divert;
- if a launched asynchronous iteration lands after the change, retain its inverse and immediately divert;
- after recovery, a new activation may begin against the new target.

Thus a completed activation is coherent with one provider view. A stale in-flight step can land only on a path that is subsequently recovered.

## 6.14 Implementation task

Refactor the runtime around transition tasks:

```ts
interface Fiber {
  // ... declarations and identity ...
  state: "inactive" | "loading" | "active" | "unloading" | "failed";
  target: ProviderView | null;
  committed: ProviderView | null;
  dispose: Dispose;
  inertia: Promise<void> | null;
  failure: unknown | null;
}
```

Required operations:

```ts
refresh(fiber: Fiber): void;
reload(fiber: Fiber): Promise<void>;
unload(fiber: Fiber): Promise<void>;
awaitFiber(fiber: Fiber): Promise<void>;
reliedUpon(provider: Fiber): boolean;
```

`refresh` must be idempotent. If a transition is already in flight, it updates the target but does not start a competing transition.

### Suggested algorithm

```text
refresh(fiber):
  newTarget <- compute target
  if newTarget equals fiber.target: return
  fiber.target <- newTarget
  if fiber.inertia exists: return
  if newTarget is bottom:
      mark UNLOADING before scheduling
      fiber.inertia <- spawn unload
  else:
      mark LOADING
      fiber.inertia <- spawn reload

reload(fiber):
  target0 <- fiber.target
  committed <- target0
  recover <- execute iterator, checking target == target0 at boundaries
  append recover to fiber disposer
  if target still equals target0:
      mark ACTIVE; notify provided keys; clear inertia
  else:
      mark UNLOADING; chain unload

unload(fiber):
  notify provided keys and await affected dependents
  run disposer
  clear committed and accumulator
  if target is bottom:
      mark INACTIVE; clear inertia
  else:
      mark LOADING; chain reload
```

Marking the provider unloading *before* scheduling recovery is essential: dependents must see the provider disappear from target resolution before any binding is physically withdrawn.

## 6.15 Testing asynchronous traces

Use deterministic gates instead of timeouts:

```ts
class Gate<T = void> {
  readonly promise: Promise<T>;
  private releaseFn!: (value: T) => void;

  constructor() {
    this.promise = new Promise<T>((resolve) => {
      this.releaseFn = resolve;
    });
  }

  release(value: T): void {
    this.releaseFn(value);
  }
}
```

A component step can await a gate. The test changes the target while the step is in flight, then releases the gate and inspects the trace.

### Required trace events

```ts
type TraceEvent =
  | { tag: "begin"; fiber: FiberId; target: ProviderView }
  | { tag: "iteration-landed"; fiber: FiberId; label: string }
  | { tag: "finish"; fiber: FiberId }
  | { tag: "divert"; fiber: FiberId }
  | { tag: "raise"; fiber: FiberId; error: unknown }
  | { tag: "leave"; fiber: FiberId }
  | { tag: "unload"; fiber: FiberId };
```

Tests should assert order relations rather than fragile wall-clock timing.

## 6.16 Exercises

### Core exercise 6.1 - Effect generator

Convert one multi-effect component to an async generator yielding one disposer per effect. Demonstrate interruption after each boundary and exact recovery of completed steps.

### Core exercise 6.2 - In-flight landing

Create a step blocked on a gate. Change the fiber's target while the step is pending. Verify that:

1. the step lands;
2. its inverse is retained;
3. the fiber never becomes active;
4. unloading runs the inverse.

### Core exercise 6.3 - Failure rollback

Make the third of four iterations throw. Verify that the first two effects are withdrawn, the fourth never begins, and the fiber records a failure with no installed contribution.

### Core exercise 6.4 - Provider-safe teardown

Implement Database and Repository. Repository teardown must call the committed Database provider after Database has left target resolution. Verify the call succeeds and Database recovery occurs afterward.

### Core exercise 6.5 - Reverse dependency chain

Use Database -> Repository -> WebAPI. Retire Database and assert unload completion order:

```text
WebAPI before Repository before Database
```

The components may enter `unloading` in a different immediate order; distinguish leave order from recovery completion order.

### Core exercise 6.6 - Provider replacement during load

Begin loading a consumer against D1. Replace D1 with D2 during an awaited step. Verify that the first episode is recovered and a new episode eventually activates with committed `{db -> D2}`.

### Core exercise 6.7 - Access enforcement

Test that:

- an inactive fiber cannot read a dependency;
- an undeclared key is rejected;
- an unloading fiber can read its committed provider;
- a target provider that was never committed cannot be read.

### Extension 6.8 - Cancellation-aware step

Add an `AbortSignal` to an effect step. Test both races:

- cancellation wins before any effect occurs;
- effect completes before cancellation and yields an inverse.

State how the iterator protocol distinguishes the two.

### Extension 6.9 - Provider multiplexing

Replace single-source `Database` with a broker key that remains stable while backing providers register and deregister. Explain why consumers of the broker need not reload on every backend change.

### Theory exercise 6.10 - Ordering argument

For an acyclic chain of providers and consumers, argue why some unloading fiber's `relied` guard is always clear. Use a maximal element of the installed dependency relation.

## 6.17 Counterexample clinic

### Counterexample A: delete binding before leave notification

Have Database's first disposer remove its service binding, then notify Repository. Repository teardown can no longer read its dependency. Record the failing trace.

### Counterexample B: current lookup during teardown

Make `ctx.get` resolve through the current target instead of the committed view. As soon as a provider leaves, consumer teardown loses access. Fix the lookup path.

### Counterexample C: competing transitions

Allow `refresh` to launch a new reload while unload is still running. Construct overlapping effects and show duplicate registration or inverse application at an invalid state.

### Counterexample D: no accumulator on failure

Throw away the partial accumulator when an iteration raises. Earlier effects leak. Add a command-count invariant to expose the leak.

### Counterexample E: cyclic precedence

Create A requires/provides B and B requires/provides A through an artificially forced active starting state. Both enter unloading while each committed view relies on the other. The guards do not clear. Relate this to the acyclicity assumption in progress.

## 6.18 Milestone C submission

Milestone C is complete when the runtime has:

- explicit loading and unloading states;
- async-generator effect programs;
- boundary interruption and inertial landing;
- rollback after target changes and failures;
- committed provider access;
- leave-before-recovery semantics;
- guarded provider unload;
- deterministic async trace tests;
- an updated independence/equivalence report covering the new primitives.

## 6.19 Reading

**Primary paper:** Sections 4.3.1-4.3.4 and 4.4.3-4.4.4; then Section 5.1.3 for the implementation algorithm.

**TypeScript:** official documentation for async generators, `for await`, `Promise`, and typed generics.

**Applied comparison:** structured concurrency, graceful shutdown, and service draining. Compare “stop accepting new work” with “finish or cancel work already admitted.”

EOF
```

```unknown
bash -lc cat > /mnt/data/work/handbook/chapters/08-lab7.md <<'EOF'
# Lab 7: Executable Metatheory and Small-State Model Checking

## Purpose

The paper proves properties of all legal executions under stated assumptions. A student runtime cannot replace those proofs with a few integration tests. It can, however, make the proof statements concrete by exploring every transition in a deliberately small model, checking invariants after each step, and shrinking failures to short traces.

This lab turns metatheory into an executable laboratory. You will construct a **reference model** distinct from the production runtime, enumerate or generate lifecycle actions, and test preservation, temporal composability, spatial composability, progress, and selected schedule-equivalence claims.

The model checker is not a theorem prover. Its role is pedagogical and diagnostic:

- it reveals the operational content of each theorem;
- it checks that code matches the intended rules on bounded instances;
- it finds counterexamples when assumptions or guards are removed;
- it helps distinguish a theorem's conclusion from its hypotheses.

## Learning outcomes

After this lab you can:

- distinguish an implementation, a reference model, and a property;
- define reachable states and enabled transitions;
- express registry well-formedness as an invariant;
- state preservation as closure of invariants under steps;
- state recovery exactness as deletion of one fiber's contribution;
- state ordering and resolution coherence as trace properties;
- state progress and identify its finiteness/acyclicity assumptions;
- perform breadth-first search for a shortest counterexample;
- use stateful property testing to generate action sequences;
- explain what bounded verification can and cannot establish.

## 7.1 What “metatheory” means here

A formal calculus defines objects and transition rules. Its **metatheory** proves properties *about* those definitions and rules.

For Mini-Cordis, the important families are:

- **preservation:** well-formed states remain well formed after a legal step;
- **temporal composability:** a fiber's recovery removes its contribution despite interleaving;
- **spatial composability:** dependencies are available and ordered across consumer episodes;
- **progress:** a non-quiescent, well-formed state has a legal lifecycle step, and under bounds the lifecycle terminates;
- **confluence:** different legal lifecycle schedules reach equivalent normal forms under assumptions.

A theorem has the logical shape:

$$
\text{assumptions}
\Longrightarrow
\text{conclusion}.
$$

A useful lab report never writes only the conclusion. It records which assumptions the model enforces.

## 7.2 Implementation, reference model, and oracle

### Motivation

Testing an implementation against itself can reproduce the same mistake on both sides of an assertion.

### Definition: system under test

The **system under test** is the asynchronous object-oriented Mini-Cordis runtime from Labs 1-6.

### Definition: reference model

A **reference model** is a smaller, more explicit representation of the intended semantics. It should favour clarity over performance and avoid sharing implementation helpers with the system under test.

```ts
export interface ModelState {
  readonly fibers: ReadonlyMap<ModelFiberId, ModelFiber>;
  readonly commands: ReadonlyMap<string, ModelFiberId>;
  readonly services: ReadonlyMap<string, ModelFiberId>;
  readonly ambient: Readonly<Record<string, number>>;
}
```

### Definition: oracle

An **oracle** determines whether observed behaviour is acceptable. Examples:

- `wellFormed(state)`;
- `observe(model) == observe(runtime)`;
- `enabled(state).length > 0` when non-quiescent;
- two endpoints are observationally equivalent.

The model does not need real handlers, sockets, or promises. It represents their abstract contributions with tokens.

## 7.3 Bounded universe

Use small finite bounds so exhaustive search is possible:

```text
fiber identities:      0..3
service keys:          db, repo, clock, notes
command keys:          a, b, c
component steps:       at most 3 per activation
lifecycle transitions: at most 12 per search path
```

A bounded universe does not weaken the definitions. It limits the states the checker instantiates.

### Canonical state encoding

Hashable states are needed to avoid revisiting the same node.

```ts
function canonical(state: ModelState): string {
  return JSON.stringify({
    fibers: [...state.fibers.entries()]
      .sort(([a], [b]) => a - b)
      .map(([id, f]) => [id, canonicalFiber(f)]),
    commands: [...state.commands.entries()].sort(),
    services: [...state.services.entries()].sort(),
    ambient: Object.entries(state.ambient).sort()
  });
}
```

If fresh names are semantically irrelevant, canonicalise them up to renaming. Otherwise the search may treat alpha-equivalent states as distinct.

## 7.4 Enabled transitions

### Definition: enabled step

A transition rule is **enabled** at state $\gamma$ when all its premises hold.

```ts
export type ModelStep =
  | { tag: "insert"; component: ComponentId }
  | { tag: "retire"; fiber: ModelFiberId }
  | { tag: "remove"; fiber: ModelFiberId }
  | { tag: "begin"; fiber: ModelFiberId }
  | { tag: "iterate"; fiber: ModelFiberId }
  | { tag: "finish"; fiber: ModelFiberId }
  | { tag: "divert"; fiber: ModelFiberId }
  | { tag: "raise"; fiber: ModelFiberId }
  | { tag: "leave"; fiber: ModelFiberId }
  | { tag: "unload"; fiber: ModelFiberId };

export function enabled(state: ModelState): readonly ModelStep[];
export function apply(state: ModelState, step: ModelStep): ModelState;
```

`apply` must reject a step not returned by `enabled`.

### Why rules should be explicit

A monolithic `settle()` function hides which premise enabled which change. Model checking works better when every calculus rule is one named transition.

## 7.5 Invariants and preservation

### Definition: invariant

An **invariant** is a predicate that holds in the initial state and is preserved by every legal transition.

### Simplified well-formedness invariant

Check:

1. every parent name is root or an existing fiber;
2. provisions are disjoint within a realm;
3. every installed fiber has a committed provider for each required key;
4. every committed provider exists and remains installed;
5. only active fibers contribute to current provider lookup;
6. a command/service contribution is owned by the fiber whose abstract effect installed it;
7. inactive fibers own no installed effects;
8. a retired flag never returns to false.

```ts
export function wellFormed(state: ModelState): readonly Violation[];
```

### Definition: preservation

A transition relation **preserves** an invariant $I$ when:

$$
I(\gamma)
\land
\gamma\longrightarrow\delta
\Longrightarrow
I(\delta).
$$

### Executable preservation check

```ts
for (const step of enabled(state)) {
  const next = apply(state, step);
  expect(wellFormed(next)).toEqual([]);
}
```

For exhaustive search, run this at every reached state.

### Worked failure

Disable the unload guard. A provider may become inactive while a consumer's committed view still names it. Invariant 4 fails immediately. The shortest trace is more instructive than an eventual null dereference.

## 7.6 Temporal composability as recovery exactness

### Motivation

The paper's theorem compares a real interleaved episode with a hypothetical execution in which one fiber's steps are deleted.

### Definition: episode

An **episode** of fiber $n$ is a maximal interval during which the fiber is installed: from begin through final unload.

### Definition: foreign projection of a trace

Given a trace $T$ and fiber $n$, the **foreign projection** removes steps acting on $n$ and, when necessary, steps of children that only exist because $n$ registered them.

### Recovery exactness property

Let an episode of $n$ begin in state $\gamma_b$ and close in $\gamma_{u+1}$. Under pairwise independence:

```text
actual endpoint after n unloads
~=
endpoint obtained by applying only foreign state transformations
from the episode's starting state
```

The comparison ignores lifecycle bookkeeping owned by the removed episode and uses the chosen observational equivalence for shared state.

### Model implementation

Tag every abstract effect token with its owner fiber:

```ts
interface Contribution {
  readonly owner: ModelFiberId;
  readonly key: string;
  readonly value: string;
}
```

Then a simple temporal property is:

```ts
function withoutOwner(
  state: ModelState,
  owner: ModelFiberId
): Observation {
  return observeRemovingOwnedContributions(state, owner);
}
```

A stronger check replays the foreign steps from the episode start and compares endpoints.

### Counterexample under non-independence

Use an ordered middleware list. Deleting A's episode from a trace changes the position at which B inserted its middleware. Recovery exactness fails even if A's inverse removes its own token.

## 7.7 Spatial composability as trace properties

### Activation precondition

Whenever a `begin(n)` step occurs:

$$
\gamma\models d_n.
$$

In code:

```ts
if (step.tag === "begin") {
  expect(satisfied(stateBefore, step.fiber)).toBe(true);
}
```

### Provider interval ordering

If consumer $m$ commits key $k$ to provider $n$, then:

- $n$'s installed episode began earlier;
- $m$'s episode ends earlier than $n$'s if $n$ ends;
- the binding at $k$ remains readable and equivalent throughout $m$'s episode.

Track episode intervals and committed views in the trace analyser.

### Resolution coherence

During one loading interval, each landed iteration either:

- ran while the target equalled the committed view; or
- was already in flight, landed after a target change, and was followed by diversion and complete recovery.

No successful active episode combines committed providers from two target views.

## 7.8 Progress

### Motivation

The unload guard deliberately delays providers. A safety mechanism is useful only if the system can still move.

### Definition: progress, local form

A non-quiescent well-formed state has at least one enabled lifecycle step:

$$
\neg\operatorname{quiet}(\gamma)
\Longrightarrow
\exists\delta.\;\gamma\longrightarrow\delta.
$$

### Executable check

```ts
if (wellFormed(state).length === 0 && !quiet(state)) {
  expect(enabledLifecycle(state).length).toBeGreaterThan(0);
}
```

### Assumptions

The paper's stronger termination result assumes, in simplified language:

- the provider-consumer precedence relation is acyclic;
- each activation has bounded finite length;
- only finitely many fiber names appear;
- the trace consists of lifecycle steps after orchestration inputs stop.

Without these, a runtime may be safe but run forever.

### Worked progress argument

If an unloading provider is blocked, some installed consumer relies on it. If that consumer is also unloading and blocked, follow the reliance edge. In a finite acyclic graph, the chain ends at a consumer with no installed dependent, whose unload step is enabled.

### Counterexamples

- a cyclic reliance graph can leave every unload guard blocked;
- a component that registers another copy of itself forever violates finiteness;
- an infinite effect iterator violates bounded transition length;
- an external orchestrator that changes targets forever prevents quiescence.

## 7.9 Breadth-first search for shortest failures

### Definition: counterexample trace

A **counterexample trace** is a sequence of legal steps from the initial state to a state violating a property.

Breadth-first search finds a shortest trace in number of steps:

```ts
interface SearchNode {
  readonly state: ModelState;
  readonly trace: readonly ModelStep[];
}

export function findCounterexample(
  initial: ModelState,
  property: (state: ModelState, trace: readonly ModelStep[]) => boolean,
  maxDepth: number
): SearchNode | null {
  const queue: SearchNode[] = [{ state: initial, trace: [] }];
  const seen = new Set<string>([canonical(initial)]);

  while (queue.length > 0) {
    const node = queue.shift()!;
    if (!property(node.state, node.trace)) return node;
    if (node.trace.length >= maxDepth) continue;

    for (const step of enabled(node.state)) {
      const next = apply(node.state, step);
      const key = canonical(next);
      if (seen.has(key)) continue;
      seen.add(key);
      queue.push({ state: next, trace: [...node.trace, step] });
    }
  }
  return null;
}
```

For trace properties, the property may need auxiliary history rather than only the endpoint.

### State explosion

If each state has branching factor $b$ and depth $d$, naive exploration can approach $b^d$ paths. Use:

- small bounds;
- state canonicalisation;
- partial-order reduction for independent adjacent steps;
- symmetry reduction for fresh names;
- property-specific pruning.

These are not merely performance tricks. They connect directly to independence and trace equivalence.

## 7.10 Stateful property testing

Property-based frameworks can generate actions as well as values.

```ts
fc.commands([
  insertCommandArb,
  retireCommandArb,
  lifecycleStepCommandArb
], { maxCommands: 30 });
```

Each command has:

- a precondition against the model;
- an update to the model;
- an action on the real runtime;
- postconditions comparing observations.

Conceptual interface:

```ts
interface Command<Model, Real> {
  check(model: Readonly<Model>): boolean;
  run(model: Model, real: Real): Promise<void>;
  toString(): string;
}
```

The framework shrinks a failing action sequence, often finding a much shorter trace than a hand-written stress test.

### Exhaustive versus generative exploration

| Technique | Strength | Limitation |
|---|---|---|
| exhaustive bounded BFS | complete within bounds; shortest trace | state explosion |
| random scheduler tests | easy; exercises real async code | may miss rare schedules |
| stateful property testing | generates and shrinks action sequences | not exhaustive |
| theorem proof | universal under assumptions | higher formal cost; separate from implementation |

Use more than one technique.

## 7.11 Assumption switches

Build the model with switches that deliberately remove a condition:

```ts
interface SemanticsOptions {
  readonly guardProviderUnload: boolean;
  readonly useProviderIdentity: boolean;
  readonly rollbackOnFailure: boolean;
  readonly enforceProvisionDisjointness: boolean;
  readonly assumeEffectsIndependent: boolean;
}
```

For each switch, ask the checker to find a shortest failure.

### Suggested mapping

| Disabled condition | Expected failed property |
|---|---|
| provider unload guard | preservation / spatial ordering |
| provider identity | resolution coherence under replacement |
| failure rollback | temporal composability / inactive owns no effects |
| provision disjointness | unique provider / inverse ownership |
| independence | recovery exactness / schedule equivalence |

This is the most important exercise in the lab. The failure trace explains why the condition appears in the formalism.

## 7.12 Worked counterexample report

A high-quality report has this form:

```text
Property:
  Every installed consumer names an installed provider.

Disabled assumption:
  Guard on provider unload.

Shortest trace:
  1 insert Database
  2 begin Database
  3 finish Database
  4 insert Repository
  5 begin Repository (commits db -> Database)
  6 finish Repository
  7 retire Database
  8 leave Database
  9 unload Database       <-- now permitted incorrectly

Violating state:
  Repository is installed and committed db -> Database,
  but Database is inactive and its binding is gone.

Why the assumption matters:
  Notification changes Repository's target, but without the guard
  Database may complete recovery before Repository completes teardown.
```

The report should distinguish the first state in which the invariant fails from later symptoms.

## 7.13 Implementation task

Create:

```text
src/model/state.ts
src/model/rules.ts
src/model/invariants.ts
src/model/search.ts
src/model/trace-properties.ts
test/model/metatheory.test.ts
```

The reference model should be pure: `apply` returns a new state and does not mutate its argument.

Provide a command-line trace printer:

```text
npm run model -- --property preservation --depth 12
npm run model -- --disable guardProviderUnload
```

Output should include:

- property name;
- assumptions enabled;
- number of states explored;
- shortest counterexample or “none within bound”;
- before/after snapshots for each step.

## 7.14 Exercises

### Core exercise 7.1 - Pure rule model

Implement all orchestration and lifecycle rules as pure transitions. Compare at least five hand-written traces against the production runtime's observations.

### Core exercise 7.2 - Preservation search

Explore every reachable state within a chosen bound. Assert well-formedness after every transition. Report state count and maximum branching factor.

### Core exercise 7.3 - Disable the guard

Find and explain the shortest preservation or ordering failure when provider unload is unguarded.

### Core exercise 7.4 - Recovery exactness

For independent key-local effects, compare a closed episode's endpoint with replay of foreign transformations from the episode start. Then replace one primitive with ordered middleware and find a failure.

### Core exercise 7.5 - Progress

Generate finite acyclic component graphs and check that non-quiescent states have an enabled lifecycle step. Then introduce a cycle or unbounded registration and document the first failed assumption.

### Core exercise 7.6 - Stateful differential test

Run generated orchestration/lifecycle sequences against both model and runtime. Compare observations after every action. Require the framework to shrink at least one deliberately injected bug.

### Core exercise 7.7 - Trace visualisation

Produce a diagram or table showing:

```text
step | rule | acting fiber | state | target | committed | visible services
```

The visualisation must make the theorem violation understandable without reading source code.

### Extension 7.8 - Partial-order reduction

When two enabled steps act on independent fibers and commute, explore only one ordering. Explain the soundness argument and measure the reduction in explored states.

### Extension 7.9 - Symmetry reduction

Canonicalise fresh fiber names by order of first appearance. Show that two traces differing only in generated IDs collapse to one state.

### Theory exercise 7.10 - Proof versus bounded search

For preservation, write:

1. what bounded model checking establishes;
2. what a rule-by-rule induction proof establishes;
3. how the two forms of evidence complement one another.

## 7.15 Counterexample clinic

The entire lab is a counterexample clinic. At minimum, preserve these deliberate faults as regression fixtures:

1. FIFO rather than LIFO recovery;
2. full-state snapshot inverse;
3. missing notification on service withdrawal;
4. Boolean rather than provider-aware target;
5. removal before deactivation;
6. no failure rollback;
7. current rather than committed lookup during teardown;
8. no provider unload guard;
9. duplicate flat providers;
10. one non-independent ordered effect.

Each fixture should include the shortest known trace and the property it violates.

## 7.16 Deliverable checklist

- [ ] The model is pure and independent of production implementation helpers.
- [ ] Every rule exposes explicit premises and writes.
- [ ] State canonicalisation prevents redundant exploration.
- [ ] Preservation, temporal, spatial, and progress checks are implemented.
- [ ] At least five assumptions can be disabled independently.
- [ ] Each disabled assumption has a minimized counterexample trace.
- [ ] Stateful differential tests compare model and runtime.
- [ ] The report states bounds and avoids claiming a universal proof from finite search.

## 7.17 Reading

**Primary paper:** Section 4.4 in full, with special attention to the statements of preservation, recovery exactness, ordering, resolution coherence, progress, and confluence. Read proofs selectively while mapping each lemma to a model invariant or trace analysis.

**Property testing:** official `fast-check` documentation on properties, arbitraries, shrinking, and model-based commands. Python cohorts may use Hypothesis stateful testing instead.

**Formal-methods bridge:** short material on labeled transition systems, invariants, breadth-first reachability, and partial-order reduction.

EOF
```

```unknown
bash -lc cat > /mnt/data/work/handbook/chapters/09-lab8.md <<'EOF'
# Lab 8: Confluence, Reconciliation, and Hot Replacement

## Purpose

A dynamic runtime has history. Components may load, fail, unload, reload, and change providers under many legal schedules. The strongest whole-system question is whether this history leaves an observable trace after the system settles.

The paper's confluence result says, under explicit assumptions, that a quiescent system agrees with a canonical from-scratch assembly of the components that end up supported. In engineering terms:

> The final settled state should depend on the final composition, not on the incidental order in which independent lifecycle work was scheduled.

This lab turns that idea into two applied mechanisms:

- **declarative reconciliation:** keep a running system aligned with a desired component tree;
- **hot replacement:** withdraw components affected by changed modules and install replacements without restarting the process.

## Learning outcomes

After this lab you can:

- define normal form, confluence, and canonical assembly;
- explain why termination and confluence are separate properties;
- compute a support set from declarations and retirement state;
- explain the role of total provision;
- compare different histories with the same orchestration inputs;
- implement a declarative reconciler;
- implement transactional hot replacement with rollback;
- identify external emissions and failures that lie outside the confluence theorem;
- complete a useful Mini-Cordis capstone.

## 8.1 Normal forms

### Motivation

After orchestration requests stop, lifecycle rules continue until every fiber matches its target. The resulting state is a candidate final result.

### Definition: normal form

A state is a **normal form** for a transition relation when no transition applies. For the lifecycle relation, a well-formed normal form is quiescent.

A failed inactive fiber may also have no enabled lifecycle step. Whether it is accepted as a normal form depends on the theorem being stated; the paper's strongest confluence statement excludes failures.

### Definition: termination

A relation **terminates** on a class of states when it admits no infinite sequence of steps from those states.

Termination answers:

> Does the system eventually stop taking lifecycle steps?

It does not answer whether different schedules stop in the same place.

## 8.2 Confluence

### Motivation

Suppose a state permits two independent fibers to step:

```text
        step A
   gamma -----> gamma_A
     |             |
step B|             |step B
     v             v
 gamma_B -----> gamma_AB
        step A
```

If the square closes, the local choices agree. Repeatedly commuting independent choices can lead to a unique normal form.

### Definition: confluence

A transition relation is **confluent** when, whenever:

$$
\gamma\longrightarrow^*\delta_1
\quad\text{and}\quad
\gamma\longrightarrow^*\delta_2,
$$

there exists a state $\varepsilon$ such that:

$$
\delta_1\longrightarrow^*\varepsilon
\quad\text{and}\quad
\delta_2\longrightarrow^*\varepsilon,
$$

with equality interpreted up to the relevant equivalence and fresh-name renaming.

If the relation also terminates, every state has at most one normal form up to equivalence.

### Definition: canonical form

A **canonical form** is a chosen representative construction for the normal form. Here it is a from-scratch sequence that activates the supported fibers once in dependency/parent order, without closed episodes that are later undone.

## 8.3 What confluence does and does not claim

The lifecycle relation is confluent under assumptions; orchestration operations are inputs. Two runs with different requested component sets need not agree.

The claim compares schedules with the same orchestration history or the same final declarative configuration, depending on the applied layer.

It also compares state, not all historical emissions. Two schedules may print log lines in different orders while ending with equivalent registered commands and services.

> **Boundary reminder.** Confluence over the internal context does not retract emails, network packets, or observations already made by external parties. The theorem concerns the state represented inside the recovery boundary.

## 8.4 Support

### Motivation

At quiescence, which fibers should be active? The answer should be determined from declarations and orchestration state rather than the schedule.

### Definition: support relation

A fiber is **supported** when:

1. it is not retired;
2. its parent is root or itself supported;
3. every key it requires can be provided by a supported fiber.

The relation combines dependency edges and parent-child edges.

### Definition: support set

The **support set** $A$ is the least/well-founded solution of:

$$
n\in A
\Longleftrightarrow
\neg\operatorname{retired}(n)
\land
(\operatorname{parent}(n)=\mathrm{root}\lor\operatorname{parent}(n)\in A)
\land
\forall k\in d_n.\;\exists m\in A.\;k\in p_m.
$$

For a finite acyclic graph, compute it by fixed point:

```ts
function supportSet(fibers: readonly FiberDeclaration[]): Set<FiberId> {
  const supported = new Set<FiberId>();
  let changed = true;

  while (changed) {
    changed = false;
    for (const fiber of fibers) {
      if (fiber.retired || supported.has(fiber.id)) continue;
      if (fiber.parent !== "root" && !supported.has(fiber.parent)) continue;

      const requirementsMet = fiber.requires.every((key) =>
        fibers.some((provider) =>
          supported.has(provider.id) && provider.provides.includes(key)
        )
      );

      if (requirementsMet) {
        supported.add(fiber.id);
        changed = true;
      }
    }
  }
  return supported;
}
```

A topological implementation is preferable when the relation is known acyclic.

## 8.5 Total provision

### Motivation

A declaration says a component may provide keys $p$. Target resolution sees only keys actually installed. If an active component sometimes omits a declared key based on schedule-dependent state, declarations alone do not determine support.

### Definition: total on provision

A component is **total on its provision** when every successful activation installs every key in its declared provision set.

At an active fiber:

$$
\operatorname{dom}(\sigma_n)=p_n.
$$

This does not require every component to provide a key. Components with empty provisions are trivially total.

### Worked example

Bad declaration:

```text
provides: {cache}
activation: provides cache only when current second is even
```

The final active set may depend on timing. Better designs:

- declare no `cache` and provide it through a separate conditionally instantiated component;
- make the condition part of declarative configuration;
- model optional provision explicitly in a richer calculus.

Total provision aligns the static interface with active runtime behaviour.

## 8.6 Schedule transposition

### Motivation

To reduce an arbitrary history to canonical order, exchange adjacent steps of distinct independent fibers.

### Definition: transposition

A **transposition** swaps two adjacent steps when:

1. both remain enabled in the opposite order;
2. their state transformations commute up to equivalence;
3. their control-field edits affect distinct fibers;
4. neither step creates the identity required by the other.

```text
... step(m); step(n); ...
~
... step(n); step(m); ...
```

Repeated transpositions move provider/parent episodes before their consumers and make each episode contiguous.

This is the operational role of the independence condition from Lab 5.

## 8.7 Deleting closed episodes

A closed episode installs effects and later recovers them. Under recovery exactness, the episode can be removed from the trace without changing the final observable state, apart from vestigial control records or child names that exist only because the episode registered them.

```text
arbitrary history
  - closed episode of A
  - open final episode of B
  - closed episode of C

trace reduction
  delete A episode
  delete C episode
  keep one open episode per finally supported fiber
```

After deleting closed episodes and transposing independent open episodes, the trace becomes a from-scratch assembly.

## 8.8 Canonical assembly

Given support set $A$, choose a linear order that respects:

- provider precedes consumer;
- parent precedes registered child.

Then activate each supported fiber once in that order.

```text
orchestration inputs
then
episode(n1)
episode(n2)
...
episode(nk)
```

Any two linear extensions differ by swaps of incomparable elements. Under independence, those swaps preserve the endpoint.

### Executable confluence property

For a small system:

```ts
const endpoints = await runAllSchedulers(initial, orchestrationInputs);
const normalForms = endpoints.filter((s) => isQuiescent(s));

for (const left of normalForms) {
  for (const right of normalForms) {
    expect(observe(left)).toEqual(observeUpToRenaming(right));
  }
}
```

Run the same comparison against `canonicalAssemble(finalConfiguration)`.

## 8.9 Worked history comparison

Final desired components:

```text
DatabaseV2
Repository
WebAPI
```

History A:

```text
load DatabaseV1
load Repository
load WebAPI
replace DatabaseV1 with DatabaseV2
WebAPI unloads/reloads
Repository unloads/reloads
```

History B:

```text
load DatabaseV2
load Repository
load WebAPI
```

Under the assumptions and after quiescence:

```text
observe(history A endpoint)
==
observe(history B endpoint)
```

The histories differ in intermediate availability and emissions. Their recovered internal composition agrees.

## 8.10 Declarative configuration

### Motivation

An orchestrator should state what should exist, not manually call a fragile sequence of insertions and retirements.

### Definition: configuration entry

A configuration entry records one desired fiber:

```ts
export interface Entry<Config = unknown> {
  readonly id: string;
  readonly component: Component;
  readonly config: Config;
  readonly disabled?: boolean;
  readonly children?: readonly Entry[];
}
```

A production system may also include module URLs, isolation realms, and interception metadata.

### Definition: reconciliation

**Reconciliation** compares the desired configuration with existing fibers and issues the minimal orchestration operations needed to align them.

Keyed diff:

```text
same id, same component, same material config -> retain
same id, changed config -> patch or reload
same id, changed component -> retire old, insert new
id removed -> retire
id added -> insert
```

Lifecycle ordering remains the runtime's responsibility. The reconciler does not need to sort inserts manually by dependency; unsatisfied fibers wait.

## 8.11 Reconciler algorithm

```ts
async function reconcile(
  runtime: Runtime,
  desired: readonly Entry[]
): Promise<void> {
  const desiredById = new Map(desired.map((e) => [e.id, e]));
  const currentById = runtime.entries();

  for (const [id, current] of currentById) {
    const next = desiredById.get(id);
    if (next === undefined || next.disabled) {
      runtime.retire(current.fiber.id);
      continue;
    }

    if (next.component !== current.component || materialChange(current, next)) {
      runtime.retire(current.fiber.id);
      runtime.insertEntry(next);
    } else {
      runtime.patchEntry(current, next);
    }
  }

  for (const entry of desired) {
    if (!entry.disabled && !currentById.has(entry.id)) {
      runtime.insertEntry(entry);
    }
  }

  await runtime.settle();
  runtime.removeRetiredInactiveEntries();
}
```

A robust reconciler handles the temporary coexistence or conflict of old and new providers deliberately. One strategy retires the old provider before admitting the replacement in the same realm; another uses a stable broker.

## 8.12 Reconciliation laws

Test:

### Idempotence

Applying the same configuration twice produces no additional lifecycle episodes:

$$
\operatorname{reconcile}(C);
\operatorname{reconcile}(C)
\simeq
\operatorname{reconcile}(C).
$$

### From-scratch consistency

Reconciling from an arbitrary settled configuration to $C$ reaches the same observation as starting empty and loading $C$.

### Locality

Changing an entry reloads only that fiber and dependents whose target view changes, not unrelated components.

### Removal exactness

Removing one entry withdraws its contribution and leaves independent retained entries unchanged.

## 8.13 Hot module replacement

### Motivation

When source changes during development, restarting the entire process discards unrelated state. Component boundaries already provide a unit of effect recovery and reapplication.

### Definition: stale entry

An entry is **stale** when its component module or an accepted transitive dependency changed.

### HMR phases

A useful simplified engine has three phases.

#### Phase 1: classify changed modules

Partition changed/importing modules into:

- **accepted:** safe to reload through component replacement;
- **declined:** requires full restart or lies beyond the managed boundary.

Cycles or opaque native modules may default to declined.

#### Phase 2: detect stale entries

For each entry module, traverse imports until a declined boundary. If the dependency tree intersects accepted changes, mark the entry stale.

#### Phase 3: transactional replacement

1. back up affected module records;
2. invalidate accepted caches;
3. import new component definitions;
4. retire old fibers and insert replacements;
5. if any import or activation setup fails, restore caches and rebuild old fibers.

### Simplified pseudocode

```ts
async function hotReplace(
  runtime: Runtime,
  stale: readonly ManagedEntry[],
  loader: ModuleLoader
): Promise<void> {
  const backup = loader.backup(stale.map((e) => e.url));

  try {
    loader.invalidate(backup.urls);
    const replacements = await Promise.all(
      stale.map(async (entry) => ({
        entry,
        component: await loader.importComponent(entry.url)
      }))
    );

    for (const { entry, component } of replacements) {
      runtime.replaceEntry(entry.id, component);
    }
    await runtime.settle();
  } catch (error) {
    loader.restore(backup);
    for (const entry of stale) {
      runtime.replaceEntry(entry.id, backup.componentFor(entry.url));
    }
    await runtime.settle();
    throw error;
  }
}
```

### Transaction boundary

The module cache and component fibers form two layers of state. The rollback must restore both, or the runtime can contain old fibers backed by new module identity, or vice versa.

## 8.14 Failures and confluence

The strongest confluence statement excludes transition failures because failure may depend on schedule-sensitive external state:

```text
Schedule A binds port before B -> A succeeds, B fails
Schedule B binds port before A -> B succeeds, A fails
```

Recovery ensures the failed fiber contributes nothing, but lifecycle outcomes differ.

Possible applied policies:

- include failure outcomes in the observable state and accept non-confluence;
- isolate conflicting resources behind a deterministic broker;
- serialise the relevant transitions;
- treat the resource as a declared non-commutative dependency;
- retry under an explicit policy.

Confluence is not obtained by ignoring genuine conflict.

## 8.15 Implementation task

Add:

```text
src/loader/configuration.ts
src/loader/reconcile.ts
src/loader/hmr.ts
test/model/confluence.test.ts
examples/capstone/
```

Required APIs:

```ts
export interface Reconciler {
  reconcile(entries: readonly Entry[]): Promise<void>;
}

export interface ModuleLoader {
  importComponent(url: string): Promise<Component>;
  invalidate(urls: readonly string[]): ModuleBackup;
  restore(backup: ModuleBackup): void;
}
```

Extend the model checker to:

- enumerate all lifecycle schedules after fixed orchestration inputs;
- compare quiescent endpoints up to observation and fresh-name renaming;
- compare endpoints with canonical assembly;
- disable independence or total provision and find divergence.

## 8.16 Exercises

### Core exercise 8.1 - Confluence diamond

Find a state with two enabled independent lifecycle steps. Execute both orders and show the same endpoint. Then replace one effect with ordered middleware and show the diamond fails.

### Core exercise 8.2 - Support set

Implement support calculation over parent and dependency edges. Compare it with the active fibers in every successful quiescent state generated by the model checker.

### Core exercise 8.3 - Total provision

Create a component that declares `{x,y}` but installs only `{x}`. Show how support prediction diverges from active target resolution. Refactor the component or the declaration to restore totality.

### Core exercise 8.4 - All schedules

For a bounded acyclic, independent system, enumerate all lifecycle schedules to quiescence. Assert pairwise equivalent endpoints and equality with canonical assembly.

### Core exercise 8.5 - Reconciler

Implement keyed reconciliation. Test add, remove, disable, re-enable, material configuration change, and no-op repetition.

### Core exercise 8.6 - Local reload

Change one provider entry. Record which consumers reload because their provider view changed and which unrelated fibers remain in the same episode.

### Core exercise 8.7 - Transactional HMR

Simulate a syntax/import failure after one stale entry has already been replaced. Verify that module records and fibers return to the previous observation.

### Core exercise 8.8 - History independence

Construct two very different histories with the same final desired configuration. After reconciliation and quiescence, compare observations and list any historical emissions that the theorem does not erase.

### Extension 8.9 - Rolling update through a broker

Keep a broker provider stable while old and new backend fibers coexist. Shift traffic, drain the old backend, and remove it without reloading broker consumers.

### Extension 8.10 - State migration

Allow an old component to export selected logical state to its replacement. Explain how forward migration differs from recovering effects and reapplying from a clean slate. State which new equivalence or correctness property would be needed.

### Theory exercise 8.11 - Canonicalisation argument

Outline the confluence proof as three transformations of a trace:

1. delete closed episodes;
2. move orchestration inputs to canonical positions;
3. transpose independent open episodes into a dependency-respecting order.

For each transformation, name the earlier property that justifies it.

## 8.17 Counterexample clinic

### Counterexample A: non-independent endpoint

Two active components prepend ordered middleware. Different schedules yield different final order. Record both normal forms.

### Counterexample B: non-total provision

A provider declares a key but conditionally omits it. Support-set prediction says the consumer is supported; runtime target remains bottom.

### Counterexample C: failure-sensitive schedule

Two components acquire the same exclusive port. Different schedules produce different failed fibers. Recovery holds, confluence does not.

### Counterexample D: half transaction

Invalidate module cache, replace one fiber, then throw without restoring either layer. The runtime is neither old nor new. Add transactional rollback.

### Counterexample E: emission history

Two confluent internal schedules send external notifications in different orders. Explain why endpoint equivalence does not imply trace equivalence for emissions.

## 8.18 Milestone D submission

Milestone D is complete when the project contains:

- bounded confluence tests over all small schedules;
- canonical assembly and support-set comparison;
- explicit total-provision checks;
- a declarative reconciler;
- transactional hot replacement with rollback;
- a useful capstone application;
- a final report connecting at least three theorem statements to implementation invariants and counterexamples.

## 8.19 Reading

**Primary paper:** Section 4.4.5, Sections 5.2.1-5.2.2, and the discussion of system boundaries, service brokers, mutual dependencies, and versioning in Section 6.

**Applied category theory:** selected opening material from Fong and Spivak's *Seven Sketches in Compositionality*. Focus on the general discipline of identifying composition, interfaces, and structure-preserving maps.

**Dynamic updating:** use the paper's related-work section as a map of dynamic software updating, cleanup callbacks, transactional rollback, and service-reactive component models.

EOF
```

```unknown
bash -lc cat > /mnt/data/work/handbook/chapters/10-capstone.md <<'EOF'
# Capstone: Building a Useful Dynamic Component Host

## Purpose

The capstone tests whether the formal machinery survives contact with an application. Each team builds one small host in which dynamic insertion, removal, replacement, and dependency change are genuinely useful rather than simulated only for tests.

The capstone is not judged by feature count. A narrow application with explicit boundaries, strong traces, and convincing properties is better than a large framework with opaque cleanup.

## 9.1 Project choices

Suitable domains include:

### CLI plugin host

Components register commands, aliases, completion providers, and background jobs. Services may include configuration, storage, and clocks.

### Agent tool registry

Components provide model-callable tools and depend on sandboxes, memory stores, credentials, or policy services. Tool replacement demonstrates provider identity and capability mediation.

### HTTP route framework

Components register routes, middleware, schemas, and service bindings. Ordered middleware provides a deliberate non-commutative case.

### Editor command system

Components register commands, keybindings, diagnostics, and language services. A language service provider can be replaced while unrelated editor state remains.

### Chatbot plugin host

Components provide adapters, databases, command registries, and feature plugins. This is close to the paper's applied setting.

### Data-processing pipeline

Components provide sources, transforms, and sinks. The pipeline must distinguish recoverable resource acquisition from output emissions.

## 9.2 Required capabilities

Every project must demonstrate:

1. dynamic component insertion and retirement;
2. at least four typed dependency keys;
3. automatic inverse accumulation for at least four resource classes;
4. provider-aware committed and target views;
5. asynchronous loading with one controlled in-flight transition;
6. rollback after one injected failure;
7. dependency-safe provider withdrawal;
8. replacement of one provider without process restart;
9. an explicit observation function;
10. a model or property suite covering at least three theorem families;
11. a trace visualiser;
12. one documented non-commutative primitive.

## 9.3 Boundary statement

The report begins with a one-page **boundary statement**:

```text
Inside Gamma:
  command registrations
  service bindings
  event subscriptions
  timer handles
  route registrations
  child fibers

Outside Gamma:
  terminal output already observed
  network responses already sent
  external database commits

Compensation policy:
  temporary files are deleted
  external writes are not claimed to be reversed
```

For every external effect, say whether the project:

- withholds it until commit;
- compensates later;
- accepts it as an irreversible emission;
- places it behind a transactional provider.

## 9.4 Theory demonstration

Choose three results from this list:

- one-step witness recovery;
- composition preserves recovery;
- local spatial composability;
- selective withdrawal under independence;
- provider interval ordering;
- resolution coherence;
- preservation;
- progress;
- confluence/from-scratch consistency.

For each, submit:

1. the formal or semi-formal statement;
2. the implementation fields and transitions it refers to;
3. one property or model check;
4. one counterexample obtained by disabling an assumption;
5. the practical failure prevented.

## 9.5 Trace demo script

The final demonstration should be scripted and reproducible. A strong ten-minute sequence is:

```text
1. Start host with unrelated long-lived state.
2. Insert a consumer before its provider; show it remains inactive.
3. Insert provider; show dependency-ordered activation.
4. Invoke useful functionality.
5. Replace provider while one consumer step is in flight.
6. Show inertial landing, rollback, and reactivation against new provider ID.
7. Inject activation failure; show partial effects recovered.
8. Retire provider; show dependents leave and complete teardown first.
9. Reconcile to a final configuration.
10. Compare settled observation with from-scratch assembly.
```

## 9.6 Report structure

A recommended report is 3,000-5,000 words:

1. **Application and boundary**
2. **Component and dependency architecture**
3. **Resource primitives and inverse contracts**
4. **Independence and observational equivalence**
5. **Lifecycle design and safe withdrawal**
6. **Executable metatheory**
7. **Counterexamples and limitations**
8. **Evaluation and future work**

## 9.7 Evaluation rubric

| Criterion | Excellent evidence |
|---|---|
| Correct boundary | Internal acquisitions and external emissions are clearly separated |
| Temporal behaviour | Each context-mediated effect is recovered locally; interleavings are tested |
| Spatial behaviour | Requirements/provisions are explicit; committed providers remain readable during teardown |
| Asynchrony | In-flight transitions land and are recovered without overlapping lifecycle tasks |
| Theory connection | Statements, code, tests, and counterexamples correspond precisely |
| Diagnostics | Traces expose rule names, targets, committed views, and ownership |
| Usefulness | The host performs a coherent task beyond the laboratory scaffolding |
| Limitations | Non-commutative operations, failures, and external effects are not hidden |

## 9.8 Self-review questions

Before submission, answer:

- Can every installed contribution be attributed to one fiber?
- Does every primitive define its inverse at the same abstraction boundary as its forward action?
- Which pairs of operations are not independent?
- What is the strongest observer a component can legitimately use?
- Can a provider complete recovery while a committed consumer remains installed?
- Can two lifecycle tasks overlap for one fiber?
- Can a failed activation leave a visible effect?
- Does target equality detect provider replacement?
- Under which exact assumptions do schedule endpoints agree?
- Which historical emissions remain even when internal state is confluent?

EOF
```

```unknown
bash -lc cat > /mnt/data/work/handbook/chapters/11-appendix-ts.md <<'EOF'
# Appendix A: TypeScript Patterns Used in Mini-Cordis

This appendix is a targeted language reference. It covers only features used repeatedly in the labs.

## A.1 Generic functions

A generic function abstracts over a type while preserving relationships between inputs and outputs.

```ts
function identity<T>(value: T): T {
  return value;
}
```

`T` is not “any type at runtime.” It is a type parameter chosen at each call. The result has the same type as the argument.

Use generics for algebraic helpers:

```ts
type Endo<S> = (state: S) => S;

function composeEndo<S>(f: Endo<S>, g: Endo<S>): Endo<S> {
  return (state) => f(g(state));
}
```

Avoid unnecessary generic parameters. Every parameter should express a real relationship.

## A.2 Typed heterogeneous keys

A service store contains values of different types. A generic key associates each key value with its service type.

```ts
declare const keyType: unique symbol;

interface Key<T> {
  readonly id: symbol;
  readonly name: string;
  readonly [keyType]?: T;
}
```

The optional phantom field is never read at runtime. It keeps `T` present in the structural type so `Key<Clock>` and `Key<Database>` do not collapse unintentionally.

```ts
function defineKey<T>(name: string): Key<T> {
  return { id: Symbol(name), name };
}
```

Internally:

```ts
class Store {
  private readonly values = new Map<symbol, unknown>();

  get<T>(key: Key<T>): T | undefined {
    return this.values.get(key.id) as T | undefined;
  }
}
```

The unchecked cast is confined to the implementation of the abstraction.

## A.3 `unknown` versus `any`

`any` disables most type checking. `unknown` requires a check or trusted abstraction before use.

Prefer:

```ts
const values = new Map<symbol, unknown>();
```

rather than:

```ts
const values = new Map<symbol, any>();
```

A heterogeneous list of keys may use `Key<unknown>[]`; individual key variables retain their specific generic type.

## A.4 Discriminated unions

Lifecycle states carry different data. A discriminated union makes illegal field combinations harder to represent.

```ts
type Lifecycle =
  | { tag: "inactive"; error?: unknown }
  | { tag: "loading"; committed: ProviderView; dispose: Dispose }
  | { tag: "active"; committed: ProviderView; dispose: Dispose }
  | { tag: "unloading"; committed: ProviderView; dispose: Dispose };
```

Narrow with `switch`:

```ts
switch (fiber.lifecycle.tag) {
  case "inactive":
    break;
  case "active":
    console.log(fiber.lifecycle.committed);
    break;
  case "loading":
  case "unloading":
    break;
  default:
    assertNever(fiber.lifecycle);
}
```

```ts
function assertNever(value: never): never {
  throw new Error(`unhandled variant: ${String(value)}`);
}
```

The `never` check makes the compiler report missing variants after the union is extended.

## A.5 Readonly data in the pure model

Use `readonly` to reduce accidental aliasing in model states:

```ts
interface ModelFiber {
  readonly component: ComponentId;
  readonly retired: boolean;
  readonly lifecycle: LifecycleModel;
}
```

`ReadonlyMap` prevents mutation through the interface but does not deep-freeze the underlying object. Construct fresh maps when applying pure transitions:

```ts
const nextFibers = new Map(state.fibers);
nextFibers.set(id, nextFiber);
return { ...state, fibers: nextFibers };
```

## A.6 Opaque identifiers

A plain string can be confused with unrelated strings. A branded type provides lightweight separation:

```ts
type FiberId = string & { readonly __fiberId: unique symbol };

type EntryId = string & { readonly __entryId: unique symbol };
```

Construct IDs through one function:

```ts
function asFiberId(value: string): FiberId {
  return value as FiberId;
}
```

Runtime freshness remains a semantic invariant; the brand only prevents accidental type mixing.

## A.7 Symbols

`Symbol()` produces a unique runtime identity even when descriptions match.

```ts
const keyA = Symbol("db");
const keyB = Symbol("db");
console.log(keyA === keyB); // false
```

Symbols are useful for dependency keys and isolation realms. Do not serialise them directly in model-state hashes; use stable model identifiers there.

## A.8 Closures as state-dependent inverses

A closure captures the old value at effect application time:

```ts
function overwrite(nextValue: number): Reversible<number> {
  return (previousValue) => [
    nextValue,
    () => previousValue
  ] as const;
}
```

The captured value must be immutable or copied if later mutation would alter the historical state.

## A.9 Async generators

An async generator can await work and yield a sequence of disposers.

```ts
async function* activate(ctx: Context): AsyncGenerator<Dispose, void, void> {
  yield ctx.commands.register("a", handlerA);
  yield await ctx.workers.start("worker-a");
}
```

Manual iteration exposes boundaries:

```ts
const iterator = activate(ctx);
const first = await iterator.next();
if (!first.done) {
  const dispose = first.value;
}
```

`for await` is convenient when no custom guard is needed:

```ts
for await (const dispose of activate(ctx)) {
  disposers.push(dispose);
}
```

Mini-Cordis uses manual `next()` calls so it can check target stability between iterations.

## A.10 Promise task handles

Calling an async function returns a `Promise`. Store that promise as the fiber's transition handle:

```ts
fiber.inertia = reload(fiber);
await fiber.inertia;
```

Clear it in exactly one completion path. Use `try/finally` or chained transition discipline to avoid leaving a rejected promise recorded forever.

Do not launch both reload and unload concurrently for one fiber.

## A.11 Result and error types

For pure partial functions, prefer an explicit result:

```ts
type Result<T, E> =
  | { ok: true; value: T }
  | { ok: false; error: E };
```

For asynchronous runtime operations, exceptions may be natural, but the lifecycle should convert them into explicit fiber outcomes and recovery transitions.

## A.12 Test organisation

Suggested division:

```text
test/unit/          examples and local API behaviour
test/properties/    algebraic laws over generated inputs
test/model/         transition-system exploration
test/integration/   asynchronous runtime traces
```

A test name should state the property, not the implementation method:

```ts
test("provider recovery waits for committed dependents", async () => { ... });
```

rather than:

```ts
test("unload method works", async () => { ... });
```

## A.13 Deterministic asynchronous tests

Avoid arbitrary sleeps:

```ts
await new Promise((resolve) => setTimeout(resolve, 50));
```

Use gates, fake timers, or explicit task hooks so the test controls the relevant interleaving.

## A.14 Recommended language reading

Use the official TypeScript Handbook for everyday types, functions, classes, generics, and narrowing. Use the official async-iteration release notes or JavaScript language documentation for async generators. The labs assume the language features, not a particular framework architecture.

EOF
```

```unknown
bash -lc cat > /mnt/data/work/handbook/chapters/12-appendix-api.md <<'EOF'
# Appendix B: Consolidated Mini-Cordis API Reference

This appendix presents one coherent endpoint for the APIs developed incrementally. It is a reference architecture, not a required byte-for-byte solution.

## B.1 Algebra

```ts
export type Endo<S> = (state: S) => S;
export type Relation<T> = (left: T, right: T) => boolean;

export function identity<T>(value: T): T;

export function compose<A, B, C>(
  after: (value: B) => C,
  before: (value: A) => B
): (value: A) => C;

export function composeEndos<S>(
  ...steps: readonly Endo<S>[]
): Endo<S>;
```

Laws:

```text
compose(identity, f) ~= f
compose(f, identity) ~= f
compose(f, compose(g, h)) ~= compose(compose(f, g), h)
```

## B.2 Pure reversible effects

```ts
export type Reversible<S> =
  (state: S) => readonly [next: S, undo: Endo<S>];

export function reversibleIdentity<S>(): Reversible<S>;

export function composeReversible<S>(
  after: Reversible<S>,
  before: Reversible<S>
): Reversible<S>;

export function sequenceReversible<S>(
  effects: readonly Reversible<S>[]
): Reversible<S>;
```

Witness obligation:

```text
const [next, undo] = effect(initial)
undo(next) ~= initial
```

## B.3 Pure effect context

```ts
export interface EffectContext<S> {
  readonly state: S;
  readonly recover: Endo<S>;
}

export function initialEffectContext<S>(state: S): EffectContext<S>;

export function track<S>(
  context: EffectContext<S>,
  forward: Endo<S>,
  inverse: Endo<S>
): EffectContext<S>;

export function perform<S>(
  context: EffectContext<S>,
  effect: Reversible<S>
): EffectContext<S>;

export function recover<S>(
  context: EffectContext<S>
): EffectContext<S>;
```

Invariant for a scope begun at `initial`:

```text
context.recover(context.state) ~= initial
```

## B.4 Imperative disposal

```ts
export type Awaitable<T> = T | Promise<T>;
export type Dispose = () => Awaitable<void>;

export class EffectScope {
  add(dispose: Dispose): Dispose;
  dispose(): Promise<void>;
  get isDisposed(): boolean;
}
```

Required behaviour:

- disposers run LIFO;
- aggregate and individual disposers are at-most-once;
- adding after disposal is rejected;
- all disposers are attempted under best-effort policy;
- failures are aggregated.

## B.5 Keys and services

```ts
declare const keyType: unique symbol;

export interface Key<T> {
  readonly id: symbol;
  readonly name: string;
  readonly [keyType]?: T;
}

export function defineKey<T>(name: string): Key<T>;

export class ServiceStore {
  has<T>(key: Key<T>): boolean;
  get<T>(key: Key<T>): T | undefined;

  provide<T>(
    owner: FiberId,
    scope: EffectScope,
    key: Key<T>,
    value: T
  ): Dispose;

  providerOf<T>(key: Key<T>): FiberId | undefined;
  valueFrom<T>(provider: FiberId, key: Key<T>): T;
  domain(): ReadonlySet<symbol>;
}
```

Core preconditions:

- a key has at most one active provider in one flat realm;
- a provider may install only declared keys;
- withdrawal notifies affected consumers;
- only active fibers participate in current provider resolution;
- committed lookup may reach an installed unloading provider.

## B.6 Components

```ts
export type EffectProgram = AsyncGenerator<Dispose, void, void>;

export interface Component<Config = unknown> {
  readonly name: string;
  readonly requires: readonly Key<unknown>[];
  readonly provides: readonly Key<unknown>[];

  activate(
    ctx: ComponentContext,
    config: Config
  ): EffectProgram;
}
```

A component definition contains declarations and code, but no instance lifecycle state.

## B.7 Provider views

```ts
export type ProviderView = ReadonlyMap<symbol, FiberId>;

export function sameView(
  left: ProviderView | null,
  right: ProviderView | null
): boolean;

export function copyView(view: ProviderView): ProviderView;
```

`null` represents the bottom target: retired or unsatisfied.

## B.8 Fibers

```ts
export type FiberId = string & {
  readonly __fiberId: unique symbol;
};

export type FiberLifecycle =
  | { readonly tag: "inactive"; readonly error?: unknown }
  | {
      readonly tag: "loading";
      readonly committed: ProviderView;
      readonly dispose: Dispose;
    }
  | {
      readonly tag: "active";
      readonly committed: ProviderView;
      readonly dispose: Dispose;
    }
  | {
      readonly tag: "unloading";
      readonly committed: ProviderView;
      readonly dispose: Dispose;
      readonly outcome?: unknown;
    };

export interface Fiber<Config = unknown> {
  readonly id: FiberId;
  readonly component: Component<Config>;
  readonly config: Config;
  readonly parent: FiberId | "root";
  readonly scope: EffectScope;

  retired: boolean;
  lifecycle: FiberLifecycle;
  target: ProviderView | null;
  inertia: Promise<void> | null;
}
```

## B.9 Component context

```ts
export class ComponentContext {
  readonly fiberId: FiberId;

  get<T>(key: Key<T>): T;
  provide<T>(key: Key<T>, value: T): Dispose;

  use<C>(component: Component<C>, config: C): Fiber<C>;

  readonly commands: CommandAPI;
  readonly events: EventAPI;
  readonly timers: TimerAPI;
  readonly routes: RouterAPI;
}
```

Access policy:

- `get` requires declaration and committed provider;
- context mutations automatically join the owning fiber's scope;
- `use` registers the child lifetime as a parent effect;
- raw stores are not exposed to ordinary component code.

## B.10 Runtime

```ts
export interface Scheduler {
  choose<T>(enabled: readonly T[]): T;
}

export class Runtime {
  insert<C>(
    component: Component<C>,
    config: C,
    parent?: FiberId | "root"
  ): Fiber<C>;

  retire(id: FiberId): void;
  remove(id: FiberId): void;
  replace<C>(id: FiberId, component: Component<C>, config: C): Fiber<C>;

  targetOf(id: FiberId): ProviderView | null;
  refresh(id: FiberId): void;
  settle(options?: { scheduler?: Scheduler }): Promise<void>;
  awaitFiber(id: FiberId): Promise<void>;

  reliedUpon(id: FiberId): boolean;
  isQuiescent(): boolean;
  assertWellFormed(): void;

  observe(): Observation;
  trace(): readonly TraceEvent[];
}
```

## B.11 Lifecycle pseudocode

```text
refresh(n):
  target' <- computeTarget(n)
  if target' = target(n): return
  target(n) <- target'

  if transition task exists: return

  if target' = bottom:
      if n is active:
          mark n unloading immediately
          notify keys n provided
          spawn unload(n)
  else:
      if n is inactive and not failed:
          mark n loading
          spawn reload(n)

reload(n):
  omega <- target(n)
  commit omega
  run effect iterator with guard target(n) = omega
  retain every yielded inverse

  if success and target(n) = omega:
      mark active
      notify keys n now provides
      finish task
  else:
      mark unloading
      chain unload(n)

unload(n):
  notify keys n provided
  wait for committed dependents to finish
  run accumulated inverse
  clear committed view and accumulator

  if target(n) = bottom:
      mark inactive
      finish task
  else:
      mark loading
      chain reload(n)
```

## B.12 Observation

```ts
export interface Observation {
  readonly activeFibers: readonly string[];
  readonly commands: readonly string[];
  readonly services: readonly Readonly<{
    key: string;
    provider: string;
  }>[];
  readonly domainState: unknown;
}
```

Do not include internal fields in the observation merely because they are easy to serialise. Include them only if they are part of the client-visible semantics being claimed.

## B.13 Trace events

```ts
export type TraceEvent = Readonly<{
  index: number;
  rule:
    | "insert"
    | "retire"
    | "remove"
    | "begin"
    | "iterate"
    | "finish"
    | "divert"
    | "raise"
    | "leave"
    | "unload";
  fiber: FiberId;
  target: ProviderView | null;
  committed: ProviderView | null;
  observation: Observation;
}>;
```

A richer trace may include operation labels, owned contributions, errors, and causal links.

## B.14 Model checker

```ts
export interface ModelState { /* pure finite representation */ }
export type ModelStep = /* one variant per rule */;

export function enabled(state: ModelState): readonly ModelStep[];
export function apply(state: ModelState, step: ModelStep): ModelState;
export function canonical(state: ModelState): string;
export function wellFormed(state: ModelState): readonly Violation[];
export function quiet(state: ModelState): boolean;

export function findCounterexample(
  initial: ModelState,
  property: TraceProperty,
  options: SearchOptions
): Counterexample | null;
```

## B.15 Loader and reconciler

```ts
export interface Entry<C = unknown> {
  readonly id: string;
  readonly component: Component<C>;
  readonly config: C;
  readonly disabled?: boolean;
  readonly children?: readonly Entry[];
}

export class Reconciler {
  reconcile(entries: readonly Entry[]): Promise<void>;
}

export interface ModuleLoader {
  importComponent(url: string): Promise<Component>;
  invalidate(urls: readonly string[]): ModuleBackup;
  restore(backup: ModuleBackup): void;
}
```

## B.16 Law checklist

A mature implementation should have executable evidence for:

```text
Algebra
  composition associativity
  identity laws

Atomic effects
  witness recovery
  precondition failure makes no transition
  locality/footprint

Effect context
  prefix recovery invariant
  LIFO ordering
  at-most-once disposal

Coeffects
  satisfaction definition
  installation and withdrawal notification
  declared access

Fibers
  target uses provider identity
  committed view fixed over an episode
  inactive fiber owns no effects

Independence
  distinct-key operations commute
  yielded inverses stable under foreign effects
  non-independent pairs have counterexamples

Lifecycle
  one transition task per fiber
  partial/failing activation is recovered
  provider leaves before recovery
  committed dependents finish before provider recovery

Metatheory
  preservation within bounds
  recovery exactness for independent effects
  activation only when satisfied
  progress under finite acyclic assumptions
  equivalent normal forms under confluence assumptions

Loader
  reconciliation idempotence
  from-scratch consistency
  transactional HMR rollback
```

EOF
```

```unknown
bash -lc cat > /mnt/data/work/handbook/chapters/13-appendix-glossary.md <<'EOF'
# Appendix C: Glossary of Mathematical and Runtime Terms

This glossary gives the meaning used in the handbook. Some words have broader meanings in programming-languages research.

## Accumulator

A composite inverse stored by an effect context or fiber. Applying it withdraws the effects accumulated since the scope began, normally in LIFO order.

## Acquisition

An operation that obtains a resource and records a capability inside the system boundary, such as opening a descriptor or registering a listener. Acquisition is often revertible even when later emissions through the resource are not.

## Activation

The lifecycle transition that runs a component's effect program against a committed provider view. Successful activation ends in the active state.

## Active

A lifecycle state in which a fiber's activation has committed, its declared installed services are available for target resolution, and it owns a live accumulator.

## Associativity

The law $(a\star b)\star c=a\star(b\star c)$. Function composition and reversible-effect composition are associative, so grouping does not change a sequence's meaning.

## Atomic effect

A smallest context operation for which the API directly supplies an inverse. Composite teardown is derived from atomic inverses.

## Bottom target ($\bot$)

The absence of a valid target provider view, caused by retirement or an unsatisfied dependency. Mini-Cordis often represents it with `null`.

## Canonical assembly

A from-scratch activation sequence containing one successful episode for each finally supported fiber, ordered so providers and parents precede consumers and children.

## Canonical form

A chosen representative of an equivalence class of normal forms. In the confluence lab, canonical assembly produces the reference endpoint.

## Coeffect

A description of what a computation requires from its environment. Mini-Cordis primarily uses typed service dependencies as runtime coeffects.

## Coeffect context ($\Sigma$)

A finite dependent partial map from keys to values of the types associated with those keys.

## Coeffect specification ($d$)

The finite set of dependency keys a component declares it requires.

## Committed view ($\omega$)

The mapping from each required key to the provider fiber identity against which a fiber began its current installed episode. It remains fixed until unload completes.

## Commutation

The property $f\circ g\simeq g\circ f$. Commuting transformations may be exchanged without changing observable state.

## Component

A reusable definition consisting of requirements, provisions, and an effect program. A component has no per-instance lifecycle state.

## Compensation

A later operation that repairs or counteracts an external effect without literally restoring the prior state. Refunds and compensating messages are examples.

## Confluence

The property that divergent legal transition sequences can be joined again, up to observational equivalence and name renaming. With termination, it yields unique normal forms.

## Context ($\Gamma$)

The type or set of complete runtime states considered by the model. An individual state is written $\gamma\in\Gamma$.

## Context transformation

A function $f:\Gamma\to\Gamma$ representing a state change.

## Counterexample trace

A legal sequence of transitions leading to a violation of a claimed property. Shortest or shrunk traces are especially useful for understanding hypotheses.

## Deactivation

The lifecycle process that stops a fiber from providing, waits for committed dependents, applies its accumulator, and returns the fiber to inactive.

## Dependent partial map

A partial mapping whose result type depends on the input key, written $(k:K)\rightharpoonup V_k$.

## Derived realisation

A context operation that leaves its input intact and returns a fresh child context carrying an adjustment. Discarding the child performs recovery.

## Disposer (`Dispose`)

An imperative at-most-once cleanup closure used as the runtime realisation of an inverse.

## Effect

A description or realisation of how a computation changes its environment.

## Effect context ($\partial\Gamma$)

The product $\Gamma\times(\Gamma\to\Gamma)$ of current state and accumulated recovery.

## Effect function

A state-dependent reversible operation $e:\Gamma\to\Gamma\times(\Gamma\to\Gamma)$.

## Effect iterator

A multi-step effect program that yields an inverse after each completed iteration and exposes boundaries at which loading may stop or divert.

## Emission

An operation that sends information or irreversible influence outside the system boundary, such as a network packet or displayed output.

## Enabled transition

A rule instance whose premises hold in the current state.

## Endomorphism

A function from an object/type to itself. Context transformations are endomorphisms on $\Gamma$.

## Episode

A maximal interval during which a fiber is installed, beginning when loading starts and ending when unloading completes.

## Equivalence relation

A reflexive, symmetric, and transitive relation. It formalises which physical states are treated as the same.

## Fiber

One runtime instance of a component, with stable identity, parent, lifecycle state, target, committed view, and accumulator.

## Foreign step

A transition performed by a fiber other than the episode currently being analysed.

## Guard

A premise that delays a transition until a safety condition holds. The central example is the unload guard requiring that a provider is no longer relied upon.

## Identity

The no-op transformation $\mathrm{id}(x)=x$, serving as the unit of function composition and the empty accumulator.

## Independence

A condition stronger than forward commutation: all generated forward/reverse transformations commute, and foreign transformations do not alter yielded inverses, outcomes, or continuations.

## Inertia

The rule that a launched asynchronous iteration is allowed to land. A target change causes recovery afterward rather than pretending the in-flight operation never occurred.

## Inference rule

A formal presentation of a transition with premises above a line and a conclusion below it.

## In-place realisation

A context operation that mutates the current host object and returns a nontrivial inverse that later undoes the mutation.

## Installed

A fiber state that carries a committed view and accumulator: loading, active, or unloading.

## Invariant

A predicate that holds initially and remains true after every legal transition.

## Key-local operation

An operation whose forward and inverse transformations read and write one coeffect key and leave others unchanged.

## Left inverse

A function $g$ satisfying $g\circ f=\mathrm{id}$. This is the direction used by load followed by unload.

## Lifecycle transition

A runtime-driven step moving a fiber toward its target, such as begin, iterate, finish, leave, divert, or unload.

## LIFO

Last-in, first-out. Effects are normally undone in the reverse order of application.

## Local spatial composability

For one component: activation begins only when its requirements are satisfied, and relevant context changes are detected and drive lifecycle response.

## Local temporal composability

For one sequence: the recorded accumulator recovers the state at which the sequence began when run in LIFO order.

## Monoid

A set with an associative binary operation and an identity element. Context transformations under composition form a monoid.

## Normal form

A state with no enabled transition in the relation under study. A successful lifecycle normal form is quiescent.

## Notification

The classification of a context change as activating, deactivating, or neutral for a given coeffect specification.

## Observational equivalence ($\simeq$)

A relation identifying states that no permitted observer/test can distinguish.

## Observer

A permitted operation or finite test whose definedness and outcome can distinguish states.

## Opposite monoid

A monoid with multiplication order reversed. Inverses accumulate in the opposite order from forward effects.

## Orchestration operation

An external input that inserts, retires, removes, replaces, or reconfigures fibers. It changes desired composition, not lifecycle state directly.

## Partial function

A function that may be undefined for some inputs, written $X\rightharpoonup Y$.

## Precedence relation ($\prec$)

A provider-consumer relation: $n\prec m$ when fiber $n$ may provide a key declared by fiber $m$.

## Preservation

A theorem that legal transitions maintain well-formedness or another invariant.

## Progress

A property that a non-quiescent well-formed state has an enabled lifecycle step. A stronger termination result requires acyclicity and finiteness assumptions.

## Provider

An active fiber whose installed service table contains a key. In the flat core model, each key has at most one provider.

## Provider view

A mapping from dependency keys to provider fiber identities.

## Provision ($p$)

The set of keys a component declares it may provide.

## Quiescent

A state in which every fiber agrees with its target: inactive with bottom target, or active with target equal to committed view.

## Reactive coeffect

A runtime coeffect discipline in which context changes are classified against specifications and cause activation/deactivation.

## Reconciliation

The process of comparing declarative desired configuration with running fibers and issuing orchestration operations to align them.

## Recover

Apply an accumulator to withdraw tracked effects and reset the accumulator to identity.

## Recovery exactness

A global temporal property: unloading one fiber yields the state that foreign steps alone would have produced, up to control bookkeeping and observational equivalence.

## Registry

The finite mapping from fiber identities to fiber records carried by a runtime state.

## Relation

A predicate on pairs of values. An equivalence relation is a relation satisfying additional laws.

## Relied upon

A provider is relied upon when an installed consumer's committed view maps a required key to that provider.

## Resolution coherence

The property that one successful activation runs against one committed provider view; stale in-flight iterations may land only on a path that is subsequently recovered.

## Retire

An orchestration request marking a fiber as no longer desired. Retirement changes its target to bottom but does not bypass deactivation.

## Right inverse

A function $g$ satisfying $f\circ g=\mathrm{id}$. This is not the direction Mini-Cordis needs for unloading.

## Satisfaction

The predicate $\sigma\models d$ meaning every key in specification $d$ occurs in the coeffect context domain.

## Scheduler

A policy choosing one enabled transition when several are legal. The formal semantics permits any legal schedule.

## Soundness invariant

For effect context $(\gamma,\varphi)$ begun at $\gamma_0$, the relation $\varphi(\gamma)\simeq\gamma_0$.

## Spatial composability

The ability to declare, resolve, and reactively maintain component dependencies, including safe provider-consumer lifecycle ordering.

## Support set

The fibers justified by retirement state, parent support, and available provisions from other supported fibers.

## System boundary

The division between state the runtime can control and recover and effects that escape to external observers or concurrent actors.

## Target view

The provider view a fiber should currently use, or bottom if retired/unsatisfied.

## Temporal composability

The ability to withdraw a component's attributable effects without withdrawing independent contributions that remain.

## Termination

The absence of infinite transition sequences under stated assumptions.

## Total provision

The property that every successful active instance installs every key declared in its provision set.

## Trace equivalence

An equivalence on action sequences generated by swapping adjacent independent actions.

## Transformation monoid

The monoid generated by an effect's forward map and every inverse it can yield.

## Transition relation

A relation $\gamma\longrightarrow\delta$ describing legal one-step state changes.

## Transposition

Swapping two adjacent independent steps while preserving applicability and endpoint.

## Twisted composition

Composition of forward/inverse pairs where forward maps compose normally and inverses compose in reverse order.

## Vestigial entry

A retired inactive empty fiber record left after recovery whose presence is invisible to the relevant state observations, except for control bookkeeping.

## Witness

Evidence that an inverse returned at one effect application recovers that application's input: $g(\delta)\simeq\gamma$.

## Well formed

Satisfying registry invariants such as valid parent references, unique providers, complete committed views, and installed named providers.

EOF
```

<details><summary>💭 Thinking</summary>

**Created Mini-Cordis handbook chapters, labs, API reference, appendices, glossary, and PDF workflow**

</details>

```json
{"search_query":[{"q":"site:bartoszmilewski.com \"Category: The Essence of Composition\""},{"q":"site:bartoszmilewski.com category theory for programmers monoids"},{"q":"site:arxiv.org/abs/1805.08605 reversible effects inverse arrows"},{"q":"site:doi.org Mazurkiewicz Trace Theory 1986"}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Checking resource links**

I’m reviewing the listed theory resources and will incorporate them into the bibliography and reading pathway, keeping the links useful for readers who want deeper study of types, semantics, programming languages, and verification.

**Refining reading pathway**

I’m adding resources on effect handlers, algebraic effects, monoids, and category-theoretic composition. I’ll prioritize stable author, publisher, university, or project pages, then place them in a progression from prerequisites to advanced study.

**Checked resource links and refined reading pathway**

**Searched 9 websites**

</details>

```unknown
bash -lc cat > /mnt/data/work/handbook/chapters/14-appendix-reading.md <<'EOF'
# Appendix D: Theory and Applied Reading Pathway

The paper touches type theory, category theory, effect systems, coeffects, operational semantics, reversible computation, dependency injection, concurrency, and dynamic software updating. Reading all background in advance would delay the laboratory indefinitely. This pathway assigns only the material needed at the point of use.

## D.1 How to use the readings

Use three levels:

- **Required:** enough to complete the lab and read the corresponding paper section.
- **Bridge:** a more pedagogical source connecting notation to programming.
- **Deepening:** original or more abstract research for students pursuing the theory further.

For every paper reading, answer four questions:

1. What problem is being formalised?
2. What are the objects and judgments?
3. What is the composition operation?
4. Which theorem or law makes composition useful?

## D.2 Primary course paper

**Yifan Shi, Wei Zhang, and Tianyi Cui, “A Programming Paradigm for Spatiotemporal Composability.”**

Use the supplied PDF. The lab-to-section map is:

| Handbook unit | Paper sections |
|---|---|
| Orientation and Lab 0 | 1; 2.1-2.3 |
| Lab 1 | 3.1.1-3.1.2; 6.1 |
| Lab 2 | 3.1; 5.1.1 |
| Lab 3 | 3.2.1-3.2.2 |
| Lab 4 | 4.1-4.2; Table 2 in 5.1 |
| Lab 5 | 3.1.3; 3.3.2; 4.4.2 |
| Lab 6 | 4.3; 4.4.3-4.4.4; 5.1.3 |
| Lab 7 | 4.4 |
| Lab 8 | 4.4.5; 5.2; selected Section 6 |

Read theorem statements before proofs. First translate each statement into a runtime property. Then return to the proof to identify where each hypothesis is used.

## D.3 Discrete mathematics and proof

### Required: Mathematics for Computer Science

Eric Lehman, F. Thomson Leighton, and Albert R. Meyer, *Mathematics for Computer Science*.

Official MIT OpenCourseWare reading page:

<https://ocw.mit.edu/courses/6-1200j-mathematics-for-computer-science-spring-2024/pages/readings/>

Recommended topics:

- predicates, sets, and functions;
- direct proof, contradiction, and induction;
- relations and equivalence relations;
- directed graphs, DAGs, and partial orders;
- state machines and invariants;
- basic counting for state-space growth.

Use this text when a proof step fails because a quantifier, induction hypothesis, or graph argument is unfamiliar.

## D.4 Programming-languages foundations

### Required/bridge: Types and Programming Languages

Benjamin C. Pierce, *Types and Programming Languages*.

Official publisher page:

<https://mitpress.mit.edu/9780262162098/types-and-programming-languages/>

Use selected early chapters for:

- abstract syntax and judgments;
- small-step operational semantics;
- evaluation relations;
- preservation and progress;
- running implementations corresponding to formal rules.

The book's operational style is particularly useful for Lab 4 and Lab 7.

### Deepening: Practical Foundations for Programming Languages

Robert Harper, *Practical Foundations for Programming Languages*, second edition.

Author's resource page:

<https://www.cs.cmu.edu/~rwh/pfpl.html>

Use it when you want a more systematic framework for defining language constructs and their statics/dynamics. It is denser than this handbook and works well as a reference after the first operational-semantics lab.

### Alternative: The Formal Semantics of Programming Languages

Glynn Winskel, *The Formal Semantics of Programming Languages*.

Publisher page:

<https://mitpress.mit.edu/9780262231695/the-formal-semantics-of-programming-languages/>

Useful for students who want more transition-system and semantic proof practice, including concurrency-oriented examples.

## D.5 Effects

### Required bridge: Monads for Functional Programming

Philip Wadler, “Monads for Functional Programming.”

Author-hosted PDF:

<https://homepages.inf.ed.ac.uk/wadler/papers/marktoberdorf/baastad.pdf>

Reading question:

> How does the text make sequencing and context threading explicit, and which parts resemble the composition of state transformations in Lab 1?

Do not infer that the paper's reversible-effect type is simply “the state monad.” The comparison is about structured sequencing and composition.

### Bridge/deepening: An Introduction to Algebraic Effects and Handlers

Matija Pretnar, “An Introduction to Algebraic Effects and Handlers.”

Author/project-hosted tutorial:

<https://www.eff-lang.org/handlers-tutorial.pdf>

Read the motivation, examples, operational interpretation, and distinction between effect operations and handlers. This helps situate the course paper's claim that it lifts effect concepts to runtime tracking rather than using handlers for modular interpretation.

### Deepening: Handling Algebraic Effects

Gordon Plotkin and Matija Pretnar, “Handling Algebraic Effects.”

Author-hosted PDF:

<https://homepages.inf.ed.ac.uk/gdp/publications/handling-algebraic-effects.pdf>

Use this for the algebraic and semantic foundations after the tutorial.

### Deepening: Notions of Computation and Monads

Eugenio Moggi, “Notions of Computation and Monads.”

This is foundational but mathematically demanding. Read after Wadler if you want the categorical semantics of computations rather than a programming-first introduction.

## D.6 Coeffects

### Required: Coeffects - Unified Static Analysis of Context-Dependence

Tomas Petricek, Dominic Orchard, and Alan Mycroft.

Author page with paper and slides:

<https://tomasp.net/academic/papers/coeffects/>

Reading question:

> Which program properties describe requirements from the context rather than changes to it?

Focus first on motivation and examples: liveness, implicit parameters, dataflow, resources, and contextual requirements. The graded/comonadic formalism is optional for the core labs.

### Deepening: Coeffects - A Calculus of Context-Dependent Computation

Tomas Petricek, Dominic Orchard, and Alan Mycroft.

Paper:

<https://tomasp.net/academic/papers/structural/coeffects-icfp.pdf>

Use this for the more complete structural calculus and categorical semantics.

### Deepening/bridge: Context-Aware Programming Languages

Tomas Petricek's thesis:

<https://tomasp.net/academic/theses/coeffects/thesis-final.pdf>

The thesis provides a readable broad introduction before detailed theory. It is a useful source when the term “coeffect” still feels too narrow or too abstract.

## D.7 Category theory for programming

Category theory is used selectively. The essential habits are:

1. identify the objects and arrows;
2. identify legal composition;
3. identify identities;
4. ask which maps preserve the composition;
5. reason from laws instead of implementation cases.

### Entry point: Category Theory Illustrated

Monoid chapter:

<https://abuseofnotation.github.io/category-theory-illustrated/03_monoid/>

Use it for a visual first encounter with monoids, operations, identity, and associativity.

### Main programming bridge: Category Theory for Programmers

Bartosz Milewski's original series and table of contents:

<https://bartoszmilewski.com/2014/10/28/category-theory-for-programmers-the-preface/>

Start with:

- “Category: The Essence of Composition”;
- “Types and Functions”;
- “Categories Great and Small”;
- “Kleisli Categories”;
- “Functors” and “Natural Transformations” only when ready;
- monads/comonads after the effects/coeffects labs.

The first chapter is:

<https://bartoszmilewski.com/2014/11/04/category-the-essence-of-composition/>

An unofficial PDF assembled with permission is available at:

<https://github.com/hmemcpy/milewski-ctfp-pdf>

Use the author's original posts as the primary source when in doubt.

### Applied category theory: Seven Sketches in Compositionality

Brendan Fong and David I. Spivak, *Seven Sketches in Compositionality: An Invitation to Applied Category Theory*.

Open manuscript:

<https://arxiv.org/abs/1803.05316>

The book assumes no prior category theory and develops categorical structures through applied examples such as databases, circuits, and dynamical systems. It is especially useful before Lab 8, where the point is not “monads in code” but the broader discipline of compositional interfaces.

## D.8 Reversibility and independence

### Deepening: Reversible Effects as Inverse Arrows

Chris Heunen, Robin Kaarsgaard, and Martti Karvonen.

<https://arxiv.org/abs/1805.08605>

Compare:

- global reversible semantics and inverse/dagger arrows;
- the course paper's runtime-supplied, one-sided, state-local inverses.

The contrast clarifies how little Mini-Cordis assumes about the complete computation.

### Trace theory

Antoni Mazurkiewicz, “Trace Theory,” in *Petri Nets: Applications and Relationships to Other Models of Concurrency*.

Publisher/DOI page:

<https://link.springer.com/chapter/10.1007/3-540-17906-2_30>

For this course, the essential idea is enough:

```text
x a b y  ~  x b a y
```

when actions `a` and `b` are independent. Use the full paper only for deeper study of partially commutative monoids and concurrent traces.

## D.9 Testing and model checking

### Required: fast-check

Official documentation:

<https://fast-check.dev/>

Introduction to property-based testing:

<https://fast-check.dev/docs/introduction/what-is-property-based-testing/>

Use it for generated states, algebraic properties, shrinking, and model-based commands.

### Unit test runner: Vitest

Official guide:

<https://vitest.dev/guide/>

TypeScript works directly in the test files. Other test runners are acceptable if the property and trace structure remains clear.

### Python alternative: Hypothesis

Official stateful-testing documentation:

<https://hypothesis.readthedocs.io/en/latest/stateful.html>

Use this alternative when the cohort implements the pure model in Python.

### Formal-methods extensions

For students who want to go beyond bounded TypeScript models, useful next steps include:

- TLA+ for state-machine specifications and temporal properties;
- Alloy for bounded relational model finding;
- Lean, Coq, or Agda for mechanised definitions and proofs;
- model checkers for labeled transition systems;
- partial-order reduction for concurrent state spaces.

These are optional because changing tools should not obscure the paper's core definitions.

## D.10 TypeScript resources

Official handbook:

<https://www.typescriptlang.org/docs/handbook/intro.html>

Generics:

<https://www.typescriptlang.org/docs/handbook/2/generics.html>

Async generators and async iteration:

<https://www.typescriptlang.org/docs/handbook/release-notes/typescript-2-3.html>

Use these for language mechanics, not as architectural authority.

## D.11 Reading plan by lab

| Lab | Required | Bridge | Deepening |
|---:|---|---|---|
| 0 | MCS functions/relations/graphs; paper §2 | TAPL operational notation; Milewski composition | PFPL |
| 1 | paper §3.1.1-3.1.2 | Wadler | Moggi; Pretnar |
| 2 | paper §3.1 and §5.1.1 | applied cleanup/resource patterns | recovery-domain work cited by paper |
| 3 | paper §3.2.1-3.2.2 | Petricek coeffects motivation | coeffect calculus/thesis |
| 4 | paper §4.1-4.2 | TAPL/PFPL dynamics | nominal techniques for fresh names |
| 5 | paper §3.1.3, §3.3.2, §4.4.2 | trace-equivalence introduction | inverse arrows; trace theory |
| 6 | paper §4.3, §4.4.3-4.4.4 | async generators; graceful shutdown | structured concurrency and service models |
| 7 | paper §4.4 | fast-check/Hypothesis stateful testing | formal verification tools |
| 8 | paper §4.4.5, §5.2 | Seven Sketches | dynamic software updating references |

## D.12 A note on terminology

The paper intentionally lifts classical terms into a runtime setting. When reading external sources, do not assume identical use:

- a static effect annotation is not a disposer;
- a comonadic coeffect semantics is not a service registry;
- reversible computing often demands more than state-local left inverses;
- dependency injection may resolve only at initialisation rather than reactively;
- confluence of internal state does not imply identical external event traces.

The comparison is productive when the differences are kept explicit.

EOF
```

```unknown
bash -lc cat > /mnt/data/work/handbook/chapters/15-appendix-prooflab.md <<'EOF'
# Appendix E: Paper-to-Code Maps and Proof Templates

## E.1 Concept map

| Paper notation or construct | Mathematical lens | Mini-Cordis realisation | Executable evidence |
|---|---|---|---|
| $\Gamma$ | state space | pure `ModelState`; abstract complete runtime state | generated states and canonical snapshots |
| $\gamma\in\Gamma$ | one state | one model/runtime snapshot | trace row |
| $\Gamma\to\Gamma$ | endomorphism | pure state transformation | unit and composition tests |
| $(f,g)$ | forward/reverse pair | operation plus disposer | witness test |
| twisted composition | product with opposite order | forward sequence + LIFO cleanup | inverse-order test |
| $\partial\Gamma$ | state plus accumulator | `EffectContext<S>` | prefix recovery invariant |
| $\mathcal{E}_\Gamma$ | state-dependent reversible functions | `Reversible<S>` | generated witness tests |
| $\Sigma$ | dependent partial map | typed service store | type tests and domain tests |
| $d$ | coeffect specification | `component.requires` | satisfaction tests |
| $p$ | provision | `component.provides` | disjointness/totality checks |
| `notify` | transition classification | `refresh` after changed keys | activation/deactivation trace |
| component $(d,p,e)$ | interface plus behaviour | `Component` | declaration and activation program |
| fiber | component instance | `Fiber` | fresh ID and per-instance scope |
| $\omega$ | committed view | key-to-provider-ID map | provider replacement test |
| target | desired provider view | `targetOf(fiber)` | quiescence test |
| $\simeq$ | observational equivalence | `observe`/per-key relation | endpoint comparison |
| $\mathcal{M}(e)$ | generated transformation monoid | representative forward/inverse transformations | independence checker |
| independence | partial commutativity plus stable yields | commutation matrix | arbitrary unload-order tests |
| transition rule | small-step semantics | one named model action | `enabled` + `apply` |
| preservation | invariant closed under steps | `wellFormed` after each action | exhaustive bounded search |
| recovery exactness | erase one episode's contribution | replay foreign steps | trace comparison |
| ordering | provider episode contains consumer episode | leave/guard/committed lookup | interval assertions |
| progress | non-quiet implies enabled step | `enabledLifecycle` | search over acyclic finite states |
| confluence | joinable schedules/unique normal form | all schedulers + canonical assembly | endpoint equivalence |

## E.2 Definition-writing template

When introducing a term in lab notes, use:

```text
Motivation:
  What failure or ambiguity makes the term necessary?

Definition:
  State the term precisely, including domains, codomains, and preconditions.

Example:
  Give one concrete state and trace the definition.

Non-example or counterexample:
  Give the smallest case that does not satisfy the definition.

Implementation:
  Identify the type, field, method, or invariant representing it.

Property:
  State how the definition is checked or used.
```

A term has not been explained merely because its name appears next to code.

## E.3 Theorem-reading template

For each theorem:

1. **Quantifiers:** Over which states, effects, fibers, or traces does it range?
2. **Assumptions:** Which are properties of the runtime, which of components, and which of the selected boundary/equivalence?
3. **Conclusion:** Is it equality, equivalence, existence of a step, termination, or uniqueness?
4. **Operational interpretation:** What would a user see if the theorem failed?
5. **Proof dependency:** Which earlier definition or lemma does each step use?
6. **Executable approximation:** Which bounded property can the lab check?
7. **Counterexample:** Which assumption can be disabled to make failure visible?

## E.4 Induction over effect sequences

Typical proposition:

> After applying a sequence of witnessed effects and accumulating inverses, recovery returns the initial state.

Proof skeleton:

**Base case:** empty sequence.

```text
state = gamma0
accumulator = identity
identity(gamma0) = gamma0
```

**Induction hypothesis:** after $n$ effects, accumulator $\varphi_n$ satisfies:

$$
\varphi_n(\gamma_n)\simeq\gamma_0.
$$

**Step:** the $(n+1)$-st effect maps $\gamma_n$ to $\gamma_{n+1}$ and yields $g_{n+1}$ with:

$$
g_{n+1}(\gamma_{n+1})\simeq\gamma_n.
$$

New accumulator:

$$
\varphi_{n+1}=\varphi_n\circ g_{n+1}.
$$

Then:

$$
\varphi_{n+1}(\gamma_{n+1})
=\varphi_n(g_{n+1}(\gamma_{n+1}))
\simeq\varphi_n(\gamma_n)
\simeq\gamma_0,
$$

provided $\varphi_n$ respects the equivalence.

## E.5 Preservation proof template

To prove a registry invariant is preserved:

1. Assume all invariant clauses hold before a step.
2. Case-split on the rule.
3. List fields the rule reads and writes.
4. For each invariant clause:
   - show the rule does not touch relevant fields; or
   - use a rule premise to establish the clause after the write.
5. Treat registrations or name creation separately if they extend the domain.

Executable analogue:

```ts
for (const state of reachableStates) {
  assert(wellFormed(state));
  for (const step of enabled(state)) {
    assert(wellFormed(apply(state, step)));
  }
}
```

## E.6 Commutation proof template

To show two key-local transformations commute:

1. Fix an arbitrary state $\sigma$.
2. Let one operation update key $k$, the other key $k'$, with $k\neq k'$.
3. Evaluate both compositions at $k$; both yield the first operation's result.
4. Evaluate both at $k'$; both yield the second operation's result.
5. Evaluate at any other key; both leave it unchanged.
6. Conclude map extensional equality.
7. Repeat the argument for forward/inverse generator pairs and outcome stability.

## E.7 Progress proof template

To show a non-quiescent state has a step:

1. Pick a fiber not matching the quiescence clauses.
2. Case-split on its lifecycle state.
3. For inactive/loading/active mismatches, identify the directly enabled rule.
4. If it is unloading but blocked, follow a committed reliance edge to a dependent.
5. Use finiteness and acyclicity to show the chain ends.
6. The final unloading fiber has no dependent and can unload.

The counterexample for cyclic precedence follows the same chain and returns to its start.

## E.8 Confluence proof roadmap

The full proof is long, but its architecture is memorable:

```text
arbitrary quiescent history
        |
        | delete closed episodes using recovery exactness
        v
only final open episodes remain
        |
        | move independent orchestration/lifecycle steps
        v
same orchestration inputs in canonical positions
        |
        | transpose incomparable independent episodes
        v
one episode per supported fiber in dependency order
        |
        v
canonical from-scratch assembly
```

Two histories with the same inputs reduce to canonical assemblies over the same support set, up to fresh-name renaming.

## E.9 Lab notebook page

For every implementation session, record:

```text
Date / commit:

Definition under implementation:

Formal signature:

Runtime representation:

Preconditions:

Invariant expected after the operation:

Worked example:

Property test:

Known non-example:

Assumption deliberately disabled:

Shortest failure trace:

Questions for paper rereading:
```

## E.10 Review checklist for pedagogical explanations

Before considering a lab note complete, ask:

- Is every symbol introduced before use?
- Is the domain/codomain of every function clear?
- Is composition direction stated?
- Are preconditions part of the definition rather than hidden in code?
- Does every abstract term have a concrete state trace?
- Does every law have at least one property test?
- Does every major hypothesis have a counterexample when removed?
- Is equality distinguished from observational equivalence?
- Are internal state and external emissions separated?
- Is the scope of the claim - local, global, bounded, or universal - explicit?

EOF
```

```unknown
bash -lc cat > /mnt/data/work/handbook/chapters/16-bibliography.md <<'EOF'
# References

The primary course paper is the supplied manuscript:

- Yifan Shi, Wei Zhang, and Tianyi Cui. “A Programming Paradigm for Spatiotemporal Composability.” Supplied course manuscript.

Selected background and companion readings:

- Eric Lehman, F. Thomson Leighton, and Albert R. Meyer. *Mathematics for Computer Science*. MIT OpenCourseWare.
- Benjamin C. Pierce. *Types and Programming Languages*. MIT Press, 2002.
- Robert Harper. *Practical Foundations for Programming Languages*, second edition. Cambridge University Press, 2016.
- Philip Wadler. “Monads for Functional Programming.” In *Program Design Calculi*, 1993.
- Eugenio Moggi. “Notions of Computation and Monads.” *Information and Computation* 93(1), 1991.
- Gordon Plotkin and John Power. “Notions of Computation Determine Monads.” FoSSaCS, 2002.
- Gordon Plotkin and Matija Pretnar. “Handlers of Algebraic Effects.” ESOP, 2009.
- Matija Pretnar. “An Introduction to Algebraic Effects and Handlers.” *Electronic Notes in Theoretical Computer Science* 319, 2015.
- Tomas Petricek, Dominic Orchard, and Alan Mycroft. “Coeffects: Unified Static Analysis of Context-Dependence.” ICALP, 2013.
- Tomas Petricek, Dominic Orchard, and Alan Mycroft. “Coeffects: A Calculus of Context-Dependent Computation.” ICFP, 2014.
- Brendan Fong and David I. Spivak. *Seven Sketches in Compositionality: An Invitation to Applied Category Theory*. 2018.
- Bartosz Milewski. *Category Theory for Programmers*. Online series, 2014-2017.
- Chris Heunen, Robin Kaarsgaard, and Martti Karvonen. “Reversible Effects as Inverse Arrows.” MFPS, 2018.
- Antoni Mazurkiewicz. “Trace Theory.” In *Petri Nets: Applications and Relationships to Other Models of Concurrency*, LNCS 255, 1987.
- Kramer and Magee. “The Evolving Philosophers Problem: Dynamic Change Management.” *IEEE Transactions on Software Engineering* 16(11), 1990.
- Y. Vandewoude et al. “Tranquility: A Low Disruptive Alternative to Quiescence for Ensuring Safe Dynamic Updates.” *IEEE Transactions on Software Engineering* 33(12), 2007.
- Héctor Garcia-Molina and Kenneth Salem. “Sagas.” SIGMOD, 1987.

Software documentation used in the laboratory pathway:

- TypeScript Handbook: <https://www.typescriptlang.org/docs/handbook/intro.html>
- Vitest documentation: <https://vitest.dev/guide/>
- fast-check documentation: <https://fast-check.dev/>
- Hypothesis stateful testing: <https://hypothesis.readthedocs.io/en/latest/stateful.html>

EOF

# concatenate in order
cat /mnt/data/work/handbook/chapters/00-front.md \
    /mnt/data/work/handbook/chapters/01-orientation-lab0.md \
    /mnt/data/work/handbook/chapters/02-lab1.md \
    /mnt/data/work/handbook/chapters/03-lab2.md \
    /mnt/data/work/handbook/chapters/04-lab3.md \
    /mnt/data/work/handbook/chapters/05-lab4.md \
    /mnt/data/work/handbook/chapters/06-lab5.md \
    /mnt/data/work/handbook/chapters/07-lab6.md \
    /mnt/data/work/handbook/chapters/08-lab7.md \
    /mnt/data/work/handbook/chapters/09-lab8.md \
    /mnt/data/work/handbook/chapters/10-capstone.md \
    /mnt/data/work/handbook/chapters/11-appendix-ts.md \
    /mnt/data/work/handbook/chapters/12-appendix-api.md \
    /mnt/data/work/handbook/chapters/13-appendix-glossary.md \
    /mnt/data/work/handbook/chapters/14-appendix-reading.md \
    /mnt/data/work/handbook/chapters/15-appendix-prooflab.md \
    /mnt/data/work/handbook/chapters/16-bibliography.md \
    > /mnt/data/work/handbook/mini-cordis-lab-handbook.md

wc -w -l /mnt/data/work/handbook/mini-cordis-lab-handbook.md
```

```unknown
bash -lc python /home/oai/skills/pdfs/scripts/md_to_pdf.py /mnt/data/work/handbook/mini-cordis-lab-handbook.md -o /mnt/data/work/handbook/build/mini-cordis-lab-handbook-draft.pdf --pdf_engine xelatex --extra=--listings --extra=--highlight-style=tango
```

```unknown
bash -lc ls -R /mnt/data/work/handbook | sed -n '1,240p' && echo '---' && ls -lh /mnt/data/work/handbook/build/mini-cordis-lab-handbook-draft.pdf /mnt/data/work/handbook/mini-cordis-lab-handbook.md
```

```unknown
bash -lc sed -n '1,260p' /mnt/data/work/handbook/mini-cordis-lab-handbook.md
```

```unknown
bash -lc grep -nE '^#{1,4} ' /mnt/data/work/handbook/mini-cordis-lab-handbook.md | sed -n '1,320p'
```

<details><summary>💭 Thinking</summary>

**Compiled handbook appendices, references, and draft PDF contents**

</details>

```unknown
bash -lc pdfinfo /mnt/data/work/handbook/build/mini-cordis-lab-handbook-draft.pdf | sed -n '1,80p'; echo '--- code fences'; python - <<'PY'
from pathlib import Path
p=Path('/mnt/data/work/handbook/mini-cordis-lab-handbook.md')
text=p.read_text()
print('fences', sum(1 for l in text.splitlines() if l.startswith('```')))
# naive stack check
stack=[]
for i,l in enumerate(text.splitlines(),1):
    if l.startswith('```'):
        if stack: stack.pop()
        else: stack.append(i)
print('unclosed',stack)
print('dollar-block markers',sum(1 for l in text.splitlines() if l.strip()=='$$'))
PY
```

```unknown
bash -lc rm -rf /mnt/data/work/handbook/rendered-draft && python /home/oai/skills/pdfs/scripts/render_pdf.py /mnt/data/work/handbook/build/mini-cordis-lab-handbook-draft.pdf --out_dir /mnt/data/work/handbook/rendered-draft --dpi 110
```

```unknown
bash -lc ls /mnt/data/work/handbook/rendered-draft | head && identify /mnt/data/work/handbook/rendered-draft/page-001.png | head
```

```unknown
bash -lc python - <<'PY'
from PIL import Image, ImageOps, ImageDraw
from pathlib import Path
src=Path('/mnt/data/work/handbook/rendered-draft')
out=Path('/mnt/data/work/handbook/contact-draft')
out.mkdir(exist_ok=True)
files=sorted(src.glob('page-*.png'))
cols,rows=5,5
thumb=(187,242)
margin=20
label_h=20
for batch_idx in range(0,len(files),cols*rows):
    batch=files[batch_idx:batch_idx+cols*rows]
    sheet=Image.new('RGB',(margin*2+cols*thumb[0],margin*2+rows*(thumb[1]+label_h)),'white')
    d=ImageDraw.Draw(sheet)
    for j,f in enumerate(batch):
        im=Image.open(f).convert('RGB')
        im.thumbnail(thumb)
        x=margin+(j%cols)*thumb[0]+(thumb[0]-im.width)//2
        y=margin+(j//cols)*(thumb[1]+label_h)+(thumb[1]-im.height)//2
        sheet.paste(im,(x,y))
        d.text((margin+(j%cols)*thumb[0]+4,margin+(j//cols)*(thumb[1]+label_h)+thumb[1]+2),f'{batch_idx+j+1}',fill='black')
    p=out/f'contact-{batch_idx+1:03d}-{batch_idx+len(batch):03d}.png'
    sheet.save(p,optimize=True)
    print(p)
PY
```

```unknown
bash -lc sed -n '1,520p' /mnt/data/work/handbook/chapters/13-appendix-glossary.md
```

```unknown
bash -lc sed -n '1,620p' /mnt/data/work/handbook/chapters/14-appendix-reading.md && echo '---BIB---' && sed -n '1,380p' /mnt/data/work/handbook/chapters/16-bibliography.md
```

```unknown
bash -lc for term in 'homomorphism' 'quotient' 'small-step' 'metatheory' 'dynamic composition' 'revertible effect' 'reactive coeffect' 'type family' 'partial order' 'DAG' 'normal form' 'denotation' 'realisation' 'scheduler' 'fixed point' 'support set' 'total provision' 'transposition' 'freshness' 'state space' 'model checker'; do echo "--- $term"; grep -ni "$term" /mnt/data/work/handbook/mini-cordis-lab-handbook.md | head -6; done
```

```unknown
bash -lc sed -n '283,410p' /mnt/data/work/handbook/mini-cordis-lab-handbook.md && sed -n '1645,1815p' /mnt/data/work/handbook/mini-cordis-lab-handbook.md
```

```unknown
bash -lc grep -n -B2 -A6 'endomorphism' /mnt/data/work/handbook/mini-cordis-lab-handbook.md | head -80; grep -n -B2 -A8 'fixed point' /mnt/data/work/handbook/mini-cordis-lab-handbook.md | head -100; grep -n -B2 -A8 'Freshness' /mnt/data/work/handbook/mini-cordis-lab-handbook.md | head -100
```

```unknown
bash -lc sed -n '4910,5065p' /mnt/data/work/handbook/mini-cordis-lab-handbook.md; sed -n '5530,5765p' /mnt/data/work/handbook/mini-cordis-lab-handbook.md
```

```unknown
bash -lc grep -n -B2 -A8 -E 'reachable|reachability|breadth-first|stateful property|shrinking|counterexample' /mnt/data/work/handbook/chapters/08-lab7.md | sed -n '1,280p'
```

```unknown
bash -lc grep -n -B3 -A12 'Definition: reachable\|reachable state\|reachability' /mnt/data/work/handbook/chapters/08-lab7.md
```

```unknown
bash -lc sed -n '5100,5495p' /mnt/data/work/handbook/mini-cordis-lab-handbook.md
```

```unknown
bash -lc sed -n '245,285p' /mnt/data/work/handbook/mini-cordis-lab-handbook.md
```

```unknown
bash -lc sed -n '1440,1505p' /mnt/data/work/handbook/mini-cordis-lab-handbook.md
```

```unknown
bash -lc sed -n '1248,1368p' /mnt/data/work/handbook/mini-cordis-lab-handbook.md
```

```unknown
bash -lc sed -n '1800,1915p' /mnt/data/work/handbook/mini-cordis-lab-handbook.md
```

```unknown
bash -lc python - <<'PY'
from pathlib import Path
p=Path('/mnt/data/work/handbook/chapters/00-front.md')
s=p.read_text()
s=s.replace('toc-depth: 3\nnumbersections: true\ngeometry:', 'toc-depth: 2\nnumbersections: false\npapersize: a4\ngeometry:')
s=s.replace('    \\fancyhead[LE,RO]{\\small\\sffamily Mini-Cordis Laboratory Handbook}\n    \\fancyhead[RE,LO]{\\small\\sffamily\\nouppercase{\\leftmark}}\n    \\fancyfoot[C]{\\thepage}', '    \\fancyhead[L]{\\small\\sffamily Mini-Cordis Laboratory Handbook}\n    \\fancyhead[R]{\\small\\sffamily Paper Companion}\n    \\fancyfoot[C]{\\thepage}')
p.write_text(s)

p=Path('/mnt/data/work/handbook/chapters/01-orientation-lab0.md')
s=p.read_text()
needle='''A conventional plugin interface often separates construction and destruction:\n\n```ts\ninterface ConventionalPlugin {\n  activate(host: Host): Promise<void>;\n  deactivate(host: Host): Promise<void>;\n}\n```\n\nThis interface permits correct implementations, but it does not make correctness structural. `activate` can register six resources while `deactivate` remembers five. The omission may remain invisible until a reload or test suite runs repeatedly.\n'''
replacement=needle+'''\n### Definition: dynamic composition\n\nA system performs **dynamic composition** when its set of running components or the relationships between them can change after execution has begun, without rebuilding the whole program from scratch. Typical changes include insertion, retirement, removal, replacement, and reconfiguration.\n\nDynamic composition is an event: something changes at runtime. **Dynamic composability** is a guarantee: the runtime preserves stated recovery and dependency properties while those changes occur. The distinction prevents a system that merely supports `load()` from being mistaken for one that supports safe unloading and rewiring.\n\n**Worked contrast.** A statically linked command table is composed before startup. A plugin host that installs a new command while retaining existing process state performs dynamic composition. If removing the plugin leaks its timer, the host is dynamic but not temporally composable.\n'''
if needle not in s: raise SystemExit('orientation insertion needle not found')
s=s.replace(needle,replacement)
needle2='''Mini-Cordis therefore treats every component as a combination of:\n\n1. a set of keys it **requires**;\n2. a set of keys it may **provide**;\n3. an effect program that installs its contribution and yields the means to withdraw it.\n\nThat shape will later become the paper's component triple $(d,p,e)$.\n'''
replacement2=needle2+'''\n> **Preview of the two runtime mechanisms.** A **revertible effect** is a context-changing operation that produces both its successor state and a state-local inverse that recovers the input at that application. A **reactive coeffect** is an environmental requirement represented at runtime and re-evaluated when the context changes, so satisfaction changes can drive activation and deactivation. Labs 1-3 develop these definitions precisely.\n'''
if needle2 not in s: raise SystemExit('preview insertion needle not found')
s=s.replace(needle2,replacement2)
p.write_text(s)
PY

grep -n -A8 -B5 'Definition: dynamic composition' /mnt/data/work/handbook/chapters/01-orientation-lab0.md
head -32 /mnt/data/work/handbook/chapters/00-front.md
```

```unknown
bash -lc grep -n -A70 -B5 '## 2.3 Tracking' /mnt/data/work/handbook/chapters/03-lab2.md
```

```unknown
bash -lc python - <<'PY'
from pathlib import Path
p=Path('/mnt/data/work/handbook/chapters/03-lab2.md')
s=p.read_text()
needle='''The newest inverse $g_2$ runs first.\n\n## 2.4 Recovery\n'''
insert='''The newest inverse $g_2$ runs first.\n\n### Definition: monoid homomorphism\n\nThe tracking operation should preserve composition rather than merely work one step at a time. A **monoid homomorphism** from monoid $(M,\star,e_M)$ to monoid $(N,\bullet,e_N)$ is a function $h:M\to N$ satisfying\n\n$$\nh(e_M)=e_N\n\qquad\text{and}\qquad\nh(a\star b)=h(a)\bullet h(b).\n$$\n\nIn programming terms, it is a translation that preserves both “do nothing” and sequencing. If two effect pairs are composed before tracking, the result must agree with tracking each pair and then composing the tracked transformations.\n\nFor the twisted pair monoid from Lab 1, `track` has exactly this property:\n\n$$\n\operatorname{track}(\mathrm{id},\mathrm{id})\n=\mathrm{id}_{\partial\Gamma},\n$$\n\n$$\n\operatorname{track}\big((f_1,g_1)\circledast(f_2,g_2)\big)\n=\operatorname{track}(f_1,g_1)\circ\operatorname{track}(f_2,g_2).\n$$\n\n**Worked interpretation.** Instrumenting a two-step program does not change the program's composition law. Whether the runtime builds one composite pair and tracks it once, or tracks both operations as they occur, it reaches the same effect context. This is why local tracking scales to sequences without a new recovery argument for every sequence length.\n\n> **Category theory bridge.** “Preserves composition and identity” is the recurring categorical pattern. Here it appears in its simplest one-object form: a homomorphism between monoids of transformations.\n\n## 2.4 Recovery\n'''
if needle not in s: raise SystemExit('needle not found')
s=s.replace(needle,insert)
p.write_text(s)
PY
```

```unknown
bash -lc sed -n '120,190p' /mnt/data/work/handbook/chapters/03-lab2.md | cat -v
```

```unknown
bash -lc python - <<'PY'
from pathlib import Path
p=Path('/mnt/data/work/handbook/chapters/03-lab2.md')
s=p.read_text(errors='replace')
start=s.index('### Definition: monoid homomorphism')
end=s.index('## 2.4 Recovery', start)
block=r'''### Definition: monoid homomorphism

The tracking operation should preserve composition rather than merely work one step at a time. A **monoid homomorphism** from monoid $(M,\star,e_M)$ to monoid $(N,\bullet,e_N)$ is a function $h:M\to N$ satisfying

$$
h(e_M)=e_N
\qquad\text{and}\qquad
h(a\star b)=h(a)\bullet h(b).
$$

In programming terms, it is a translation that preserves both “do nothing” and sequencing. If two effect pairs are composed before tracking, the result must agree with tracking each pair and then composing the tracked transformations.

For the twisted pair monoid from Lab 1, `track` has exactly this property:

$$
\operatorname{track}(\mathrm{id},\mathrm{id})
=\mathrm{id}_{\partial\Gamma},
$$

$$
\operatorname{track}\big((f_1,g_1)\circledast(f_2,g_2)\big)
=\operatorname{track}(f_1,g_1)\circ\operatorname{track}(f_2,g_2).
$$

**Worked interpretation.** Instrumenting a two-step program does not change the program's composition law. Whether the runtime builds one composite pair and tracks it once, or tracks both operations as they occur, it reaches the same effect context. This is why local tracking scales to sequences without a new recovery argument for every sequence length.

> **Category theory bridge.** “Preserves composition and identity” is the recurring categorical pattern. Here it appears in its simplest one-object form: a homomorphism between monoids of transformations.

'''
s=s[:start]+block+s[end:]
p.write_text(s)
PY
python - <<'PY'
from pathlib import Path
p=Path('/mnt/data/work/handbook/chapters/03-lab2.md')
b=p.read_bytes()
print('control bytes:', sorted(set(x for x in b if x<32 and x not in (9,10,13))))
PY
sed -n '132,180p' /mnt/data/work/handbook/chapters/03-lab2.md
```

```unknown
bash -lc python - <<'PY'
from pathlib import Path
p=Path('/mnt/data/work/handbook/chapters/05-lab4.md')
s=p.read_text()
old='''### Freshness\n\nA removed fiber ID should not be reused, or stale committed views could accidentally point at a new fiber. Use monotonically increasing IDs, UUIDs, or unforgeable symbols.\n'''
new='''### Definition: fresh fiber identity\n\nA fiber identity is **fresh** when it does not identify any currently registered fiber. Mini-Cordis uses the stronger engineering rule of **global freshness**: once issued, a fiber ID is never reused. Monotonically increasing IDs, UUIDs, or unforgeable symbols make this easy.\n\nThe stronger rule prevents a stale reference from accidentally acquiring a new meaning. The paper's calculus can permit reuse after removal because its preservation argument ensures that no installed committed view still names the removed fiber. Global freshness is a simpler implementation discipline, not a stronger mathematical theorem about effects.\n'''
if old not in s: raise SystemExit('freshness block not found')
s=s.replace(old,new)
old2='''## 4.10 Refresh to a fixed point\n\nIn the synchronous base model, repeatedly apply any enabled lifecycle step until quiescent:\n'''
new2='''## 4.10 Settling to quiescence\n\nA runtime often describes repeated refresh as a fixed-point computation. The phrase is useful, but it should be interpreted carefully.\n\n### Definition: fixed point and normal form\n\nFor a deterministic function $F:S\to S$, a state $s$ is a **fixed point** when $F(s)=s$. A lifecycle calculus is usually nondeterministic: several rules may be enabled, so there is no single function $F$ until a scheduler is chosen. The corresponding rule-based notion is a **normal form**, a state with no enabled lifecycle transition. In the base Mini-Cordis model, the successful normal forms of interest are quiescent states.\n\nWith a fixed scheduler, one loop iteration can be viewed as a deterministic function, and settling repeatedly applies that function until it no longer changes the lifecycle state. Lab 8 asks whether different legal schedulers reach equivalent normal forms.\n\nIn the synchronous base model, repeatedly apply any enabled lifecycle step until quiescent:\n'''
if old2 not in s: raise SystemExit('fixed point block not found')
s=s.replace(old2,new2)
p.write_text(s)
PY

grep -n -A14 -B3 'fresh fiber identity\|Settling to quiescence' /mnt/data/work/handbook/chapters/05-lab4.md
```

```unknown
bash -lc python - <<'PY'
from pathlib import Path
p=Path('/mnt/data/work/handbook/chapters/05-lab4.md')
s=p.read_text()
s=s.replace('$F:S\to S$', '$F:S\\to S$') if '$F:S\to S$' in s else s
# Replace literal tab form too
s=s.replace('$F:S\to S$'.encode('utf-8').decode('unicode_escape'), '$F:S\\to S$')
s=s.replace('$F:S\t o S$', '$F:S\\to S$')
s=s.replace('$F:S\t o S$', '$F:S\\to S$')
# direct actual tab sequence
s=s.replace('$F:S\to S$', '$F:S\\to S$')
s=s.replace('$F:S\t o S$', '$F:S\\to S$')
s=s.replace('$F:S\t'+'o S$', '$F:S\\to S$')
p.write_text(s)
print(repr([line for line in s.splitlines() if 'fixed point' in line or 'deterministic function' in line][1]))
PY
python - <<'PY'
from pathlib import Path
b=Path('/mnt/data/work/handbook/chapters/05-lab4.md').read_bytes()
print('controls', sorted(set(x for x in b if x<32 and x not in (9,10,13))))
PY
sed -n '458,465p' /mnt/data/work/handbook/chapters/05-lab4.md | cat -v
```

```unknown
bash -lc python - <<'PY'
from pathlib import Path
p=Path('/mnt/data/work/handbook/chapters/08-lab7.md')
s=p.read_text()
needle='''The model checker is not a theorem prover. Its role is pedagogical and diagnostic:\n\n- it reveals the operational content of each theorem;\n- it checks that code matches the intended rules on bounded instances;\n- it finds counterexamples when assumptions or guards are removed;\n- it helps distinguish a theorem's conclusion from its hypotheses.\n'''
replacement=needle+r'''\n### Definition: bounded model checker

A **bounded model checker** for this lab is a program that starts from an initial model state, enumerates every legal successor within a finite universe and depth bound, and checks a property at each reached state or trace. “Bounded” means that the conclusion is complete only for the chosen keys, fibers, component programs, and trace depth. It is stronger than sampling within those bounds, but it is not a universal proof about all systems.

**Worked contrast.** An integration test may run one scheduler and observe no failure. A bounded checker with three fibers and depth ten explores every legal scheduler represented by that model. A theorem proof goes further still: it establishes the property for all instances satisfying its assumptions, not only the finite instances enumerated by a tool.
'''
if needle not in s: raise SystemExit('model checker insertion needle not found')
s=s.replace(needle,replacement)
needle2='''## 7.3 Bounded universe\n\nUse small finite bounds so exhaustive search is possible:\n'''
replacement2=r'''## 7.3 Bounded universe

### Definition: reachable state

A state is **reachable** when it is the initial state or there is a finite sequence of enabled transitions from the initial state to that state:

$$
\gamma_0\longrightarrow^*\gamma.
$$

A checker need not examine arbitrary values that no legal execution can produce. Its search frontier is the set of reached but not yet expanded states.

Use small finite bounds so exhaustive search is possible:
'''
if needle2 not in s: raise SystemExit('reachable insertion needle not found')
s=s.replace(needle2,replacement2)
needle3='''## 7.10 Stateful property testing\n\nProperty-based frameworks can generate actions as well as values.\n'''
replacement3=r'''## 7.10 Stateful property testing

### Definition: stateful property testing

**Stateful property testing** generates sequences of commands whose availability depends on a changing reference model. Each generated command states a precondition, updates the model, acts on the real implementation, and checks postconditions. This differs from generating independent input values because later commands are interpreted against the state produced by earlier commands.

A framework performs **shrinking** when it simplifies a failing value or command sequence while preserving the failure. For lifecycle systems, shrinking often turns a long stress trace into the minimal sequence “insert provider; activate consumer; retire provider; unload too early.”

Property-based frameworks can generate actions as well as values.
'''
if needle3 not in s: raise SystemExit('stateful insertion needle not found')
s=s.replace(needle3,replacement3)
p.write_text(s)
PY
python - <<'PY'
from pathlib import Path
b=Path('/mnt/data/work/handbook/chapters/08-lab7.md').read_bytes()
print('controls', sorted(set(x for x in b if x<32 and x not in (9,10,13))))
PY
sed -n '1,90p' /mnt/data/work/handbook/chapters/08-lab7.md
sed -n '95,135p' /mnt/data/work/handbook/chapters/08-lab7.md
sed -n '390,445p' /mnt/data/work/handbook/chapters/08-lab7.md
```

```unknown
bash -lc grep -RFn '\n' /mnt/data/work/handbook/chapters | head -50
```

```unknown
bash -lc python - <<'PY'
from pathlib import Path
p=Path('/mnt/data/work/handbook/chapters/08-lab7.md')
s=p.read_text().replace('hypotheses.\\n### Definition: bounded model checker','hypotheses.\n\n### Definition: bounded model checker')
p.write_text(s)
PY
sed -n '5,24p' /mnt/data/work/handbook/chapters/08-lab7.md
```

```unknown
bash -lc python - <<'PY'
from pathlib import Path
p=Path('/mnt/data/work/handbook/chapters/08-lab7.md')
s=p.read_text().replace('\\n### Definition: bounded model checker','\n### Definition: bounded model checker')
p.write_text(s)
PY
sed -n '9,20p' /mnt/data/work/handbook/chapters/08-lab7.md | cat -v
```

```unknown
bash -lc grep -n -A20 -B2 '## 7.3' /mnt/data/work/handbook/chapters/08-lab7.md
```

```unknown
bash -lc python - <<'PY'
from pathlib import Path
p=Path('/mnt/data/work/handbook/chapters/13-appendix-glossary.md')
s=p.read_text()
repls={
'''## Disposer (`Dispose`)\n\nAn imperative at-most-once cleanup closure used as the runtime realisation of an inverse.\n''':'''## Disposer (`Dispose`)\n\nAn imperative at-most-once cleanup closure used as the runtime realisation of an inverse.\n\n## Dynamic composition\n\nRuntime insertion, retirement, removal, replacement, or reconfiguration of components or their relationships without reconstructing the complete process from scratch.\n\n## Dynamic composability\n\nThe property that dynamic composition preserves stated recovery, dependency, progress, or confluence guarantees. Supporting runtime loading alone does not establish dynamic composability.\n''',
'''## Fiber\n\nOne runtime instance of a component, with stable identity, parent, lifecycle state, target, committed view, and accumulator.\n''':'''## Fiber\n\nOne runtime instance of a component, with stable identity, parent, lifecycle state, target, committed view, and accumulator.\n\n## Fixed point\n\nFor a deterministic function $F:S\\to S$, a state $s$ with $F(s)=s$. For a nondeterministic transition relation, the closely related notion used in the handbook is a normal form with no enabled transition.\n\n## Fresh identity\n\nAn identity not currently assigned to a registered fiber. Mini-Cordis uses globally fresh, never-reused IDs as a simple implementation discipline.\n''',
'''## Guard\n\nA premise that delays a transition until a safety condition holds. The central example is the unload guard requiring that a provider is no longer relied upon.\n''':'''## Guard\n\nA premise that delays a transition until a safety condition holds. The central example is the unload guard requiring that a provider is no longer relied upon.\n\n## Homomorphism\n\nA map between algebraic structures that preserves the designated identity and composition operation. `track` is studied as a monoid homomorphism because tracking a composite agrees with composing tracked steps.\n''',
'''## Monoid\n\nA set with an associative binary operation and an identity element. Context transformations under composition form a monoid.\n''':'''## Model checker\n\nA program that explores the transition graph of a reference model and checks properties at reached states or traces. The handbook uses bounded model checking, which is exhaustive only within declared finite bounds.\n\n## Monoid\n\nA set with an associative binary operation and an identity element. Context transformations under composition form a monoid.\n''',
'''## Reactive coeffect\n\nA runtime coeffect discipline in which context changes are classified against specifications and cause activation/deactivation.\n''':'''## Reachable state\n\nThe initial state or any state obtained from it by a finite sequence of enabled transitions.\n\n## Reactive coeffect\n\nA runtime coeffect discipline in which context changes are classified against specifications and cause activation/deactivation.\n''',
'''## Soundness invariant\n\nFor effect context $(\\gamma,\\varphi)$ begun at $\\gamma_0$, the relation $\\varphi(\\gamma)\\simeq\\gamma_0$.\n''':'''## Shrinking\n\nThe property-testing process of simplifying a failing generated value or command sequence while preserving the failure, ideally exposing a minimal counterexample.\n\n## Small-step operational semantics\n\nA semantics that describes execution as individual transitions between states. Mini-Cordis uses named small steps so rule premises and interleavings remain visible.\n\n## Soundness invariant\n\nFor effect context $(\\gamma,\\varphi)$ begun at $\\gamma_0$, the relation $\\varphi(\\gamma)\\simeq\\gamma_0$.\n''',
'''## System boundary\n\nThe division between state the runtime can control and recover and effects that escape to external observers or concurrent actors.\n''':'''## Stateful property testing\n\nProperty-based generation of legal command sequences against a changing reference model, with preconditions, model updates, real actions, and postconditions checked after each command.\n\n## System boundary\n\nThe division between state the runtime can control and recover and effects that escape to external observers or concurrent actors.\n'''
}
for old,new in repls.items():
    if old not in s:
        raise SystemExit('missing glossary needle: '+old.splitlines()[0])
    s=s.replace(old,new)
p.write_text(s)
PY
python - <<'PY'
from pathlib import Path
b=Path('/mnt/data/work/handbook/chapters/13-appendix-glossary.md').read_bytes()
print('controls',sorted(set(x for x in b if x<32 and x not in (9,10,13))))
PY
grep -n -E '^## (Dynamic|Fixed|Fresh|Homomorphism|Model checker|Reachable|Shrinking|Small-step|Stateful)' /mnt/data/work/handbook/chapters/13-appendix-glossary.md
```

```unknown
bash -lc grep -n '^## Metatheory' /mnt/data/work/handbook/chapters/13-appendix-glossary.md || true
```

```unknown
bash -lc for h in 'Metatheory' 'Property-based testing' 'Reference model' 'Oracle' 'Quotient' 'Scheduler' 'System under test' 'Alpha-equivalence' 'Symmetry reduction' 'Partial-order reduction'; do grep -q "^## $h" /mnt/data/work/handbook/chapters/13-appendix-glossary.md && echo yes "$h" || echo no "$h"; done
```

```unknown
bash -lc python - <<'PY'
from pathlib import Path
p=Path('/mnt/data/work/handbook/chapters/13-appendix-glossary.md')
s=p.read_text()
# insert after Accumulator alpha-equivalence
s=s.replace('''## Accumulator\n\nA composite inverse stored by an effect context or fiber. Applying it withdraws the effects accumulated since the scope began, normally in LIFO order.\n''','''## Accumulator\n\nA composite inverse stored by an effect context or fiber. Applying it withdraws the effects accumulated since the scope began, normally in LIFO order.\n\n## Alpha-equivalence\n\nEquivalence up to consistent renaming of generated local identities. Two model states may be alpha-equivalent even when their concrete fiber IDs differ.\n''')
s=s.replace('''## Model checker\n\nA program that explores the transition graph of a reference model and checks properties at reached states or traces. The handbook uses bounded model checking, which is exhaustive only within declared finite bounds.\n''','''## Metatheory\n\nDefinitions and proofs about a formal system rather than programs inside that system. The handbook's metatheory concerns preservation, composability, progress, termination, and confluence of lifecycle rules.\n\n## Model checker\n\nA program that explores the transition graph of a reference model and checks properties at reached states or traces. The handbook uses bounded model checking, which is exhaustive only within declared finite bounds.\n''')
s=s.replace('''## Observational equivalence ($\\simeq$)\n\nA relation identifying states that no permitted observer/test can distinguish.\n''','''## Observational equivalence ($\\simeq$)\n\nA relation identifying states that no permitted observer/test can distinguish.\n\n## Oracle\n\nA predicate or comparison that decides whether a model or runtime observation is acceptable during testing.\n''')
s=s.replace('''## Partial function\n\nA function that may be undefined for some inputs, written $X\\rightharpoonup Y$.\n''','''## Partial function\n\nA function that may be undefined for some inputs, written $X\\rightharpoonup Y$.\n\n## Partial-order reduction\n\nA state-space reduction that avoids exploring both orders of adjacent independent transitions when the orders are known to have equivalent effects.\n''')
s=s.replace('''## Provision ($p$)\n\nThe set of keys a component declares it may provide.\n''','''## Property-based testing\n\nTesting by generating many inputs from a domain and checking a general property, normally with shrinking to simplify failures.\n\n## Provision ($p$)\n\nThe set of keys a component declares it may provide.\n''')
s=s.replace('''## Quiescent\n\nA state in which every fiber agrees with its target: inactive with bottom target, or active with target equal to committed view.\n''','''## Quiescent\n\nA state in which every fiber agrees with its target: inactive with bottom target, or active with target equal to committed view.\n\n## Quotient\n\nA mathematical construction that treats every equivalence class as one abstract value. The quotient $\\Gamma/\\simeq$ explains why operations must respect observational equivalence.\n''')
s=s.replace('''## Reactive coeffect\n\nA runtime coeffect discipline in which context changes are classified against specifications and cause activation/deactivation.\n''','''## Reactive coeffect\n\nA runtime coeffect discipline in which context changes are classified against specifications and cause activation/deactivation.\n\n## Reference model\n\nA small explicit implementation of intended semantics used as an independent comparison point for the production runtime.\n''')
s=s.replace('''## Support set\n\nThe fibers justified by retirement state, parent support, and available provisions from other supported fibers.\n''','''## Support set\n\nThe fibers justified by retirement state, parent support, and available provisions from other supported fibers.\n\n## Symmetry reduction\n\nA state-space reduction that identifies states differing only by an irrelevant symmetry, such as a consistent renaming of fresh fiber identities.\n\n## System under test\n\nThe concrete implementation whose behaviour is being checked against properties or a reference model.\n''')
p.write_text(s)
PY
python - <<'PY'
from pathlib import Path
b=Path('/mnt/data/work/handbook/chapters/13-appendix-glossary.md').read_bytes()
print('controls',sorted(set(x for x in b if x<32 and x not in (9,10,13))))
PY
grep -n -E '^## (Alpha|Metatheory|Oracle|Partial-order|Property-based|Quotient|Reference model|Symmetry|System under test)' /mnt/data/work/handbook/chapters/13-appendix-glossary.md
```

```unknown
bash -lc python - <<'PY'
from pathlib import Path
root=Path('/mnt/data/work/handbook/chapters')
for p in sorted(root.glob('*.md')):
    b=p.read_bytes()
    bad=[x for x in b if x<32 and x not in (9,10,13)]
    if bad:
        print('BAD CONTROL',p, sorted(set(bad)))
    text=b.decode('utf-8')
    # literal slash-n only when not LaTeX neg etc - exact backslash+n followed by heading
    if '\\n#' in text:
        print('LITERAL NEWLINE ESCAPE',p)
print('done')
PY
# Count common suspicious patterns
grep -RIn $'\t' /mnt/data/work/handbook/chapters | head -20 || true

```

<details><summary>💭 Thinking</summary>

**Audited, rendered, analyzed, and updated handbook structure, terminology, definitions, formatting, and glossary**

</details>

```unknown
bash -lc python - <<'PY'
from pathlib import Path
root=Path('/mnt/data/work/handbook/chapters')
profiles={
'01-orientation-lab0.md':'> **Lab profile.** Estimated effort: 4-6 hours. Prerequisites: elementary programming and willingness to read short equations. Main artifacts: `algebra.ts`, `graph.ts`, and a notation worksheet. Paper focus: Sections 1-2 and the notation used throughout the formal development.\n',
'02-lab1.md':'> **Lab profile.** Estimated effort: 6-8 hours. Prerequisite: Lab 0. Main artifact: a pure library of state-dependent reversible transformations with property tests. Paper focus: Sections 3.1.1-3.1.2 and the system-boundary discussion in Section 6.1.\n',
'03-lab2.md':'> **Lab profile.** Estimated effort: 6-8 hours. Prerequisite: Lab 1. Main artifact: an effect scope that derives one idempotent component disposer from atomic inverses. Paper focus: Section 3.1 and the effect-tracking implementation in Section 5.1.1.\n',
'04-lab3.md':'> **Lab profile.** Estimated effort: 6-8 hours. Prerequisite: Milestone A. Main artifact: a typed service context with revertible provision, satisfaction checking, and reactive notification. Paper focus: Sections 3.2.1-3.2.2.\n',
'05-lab4.md':'> **Lab profile.** Estimated effort: 8-10 hours. Prerequisite: Lab 3. Main artifact: a component registry with fibers, provider-aware targets, committed views, and a two-state lifecycle. Paper focus: Sections 4.1-4.2 and the theory-to-implementation map in Section 5.1.\n',
'06-lab5.md':'> **Lab profile.** Estimated effort: 8-12 hours. Prerequisite: Lab 4. Main artifacts: a commutation matrix, selective-withdrawal properties, and an observational equivalence for the host. Paper focus: Sections 3.1.3, 3.3.2, and 4.4.2.\n',
'07-lab6.md':'> **Lab profile.** Estimated effort: 10-14 hours. Prerequisite: Lab 5. Main artifact: a four-state asynchronous lifecycle with effect iterators, rollback on failure, committed lookup, and guarded provider withdrawal. Paper focus: Section 4.3, Sections 4.4.3-4.4.4, and Section 5.1.3.\n',
'08-lab7.md':'> **Lab profile.** Estimated effort: 10-14 hours. Prerequisite: Lab 6. Main artifact: a pure bounded reference model, invariant checker, trace analyser, and shortest-counterexample search. Paper focus: Section 4.4.\n',
'09-lab8.md':'> **Lab profile.** Estimated effort: 8-12 hours. Prerequisite: Lab 7. Main artifacts: a canonical-assembly oracle, declarative reconciler, and transactional hot-replacement experiment. Paper focus: Section 4.4.5, Section 5.2, and selected discussion sections.\n'
}
for name,profile in profiles.items():
    p=root/name
    s=p.read_text()
    needle='\n## Learning outcomes\n'
    if needle not in s:
        raise SystemExit(f'Learning outcomes marker missing in {name}')
    s=s.replace(needle,'\n'+profile+'\n## Learning outcomes\n',1)
    p.write_text(s)
PY
for f in /mnt/data/work/handbook/chapters/0{1,2,3,4,5,6,7,8,9}*.md; do echo "---$(basename "$f")"; grep -n -A2 'Lab profile' "$f" | head -4; done
```

```unknown
bash -lc python - <<'PY'
from pathlib import Path
root=Path('/mnt/data/work/handbook/chapters')
for p in [root/f'{i:02d}-'+name for i,name in []]: pass
files=['01-orientation-lab0.md','02-lab1.md','03-lab2.md','04-lab3.md','05-lab4.md','06-lab5.md','07-lab6.md','08-lab7.md','09-lab8.md']
for name in files:
    t=(root/name).read_text().lower()
    print(f'{name:28s} motivation={t.count("motivation"):2d} definition={t.count("definition"):2d} worked={t.count("worked"):2d} exercises={t.count("exercise"):2d} counterexample={t.count("counterexample"):2d} deliverable={t.count("deliverable"):2d}')
PY
```

```unknown
bash -lc cat /mnt/data/work/handbook/chapters/00-front.md \
    /mnt/data/work/handbook/chapters/01-orientation-lab0.md \
    /mnt/data/work/handbook/chapters/02-lab1.md \
    /mnt/data/work/handbook/chapters/03-lab2.md \
    /mnt/data/work/handbook/chapters/04-lab3.md \
    /mnt/data/work/handbook/chapters/05-lab4.md \
    /mnt/data/work/handbook/chapters/06-lab5.md \
    /mnt/data/work/handbook/chapters/07-lab6.md \
    /mnt/data/work/handbook/chapters/08-lab7.md \
    /mnt/data/work/handbook/chapters/09-lab8.md \
    /mnt/data/work/handbook/chapters/10-capstone.md \
    /mnt/data/work/handbook/chapters/11-appendix-ts.md \
    /mnt/data/work/handbook/chapters/12-appendix-api.md \
    /mnt/data/work/handbook/chapters/13-appendix-glossary.md \
    /mnt/data/work/handbook/chapters/14-appendix-reading.md \
    /mnt/data/work/handbook/chapters/15-appendix-prooflab.md \
    /mnt/data/work/handbook/chapters/16-bibliography.md \
    > /mnt/data/work/handbook/mini-cordis-lab-handbook.md
python - <<'PY'
from pathlib import Path
p=Path('/mnt/data/work/handbook/mini-cordis-lab-handbook.md')
text=p.read_text()
b=p.read_bytes()
print('lines',len(text.splitlines()),'words',len(text.split()),'bytes',len(b))
print('code fences',sum(1 for l in text.splitlines() if l.startswith('```')))
print('math blocks',sum(1 for l in text.splitlines() if l.strip()=='$$'))
print('control bytes',sorted(set(x for x in b if x<32 and x not in (9,10,13))))
print('literal \\n headings',text.count('\\n#'))
PY
head -20 /mnt/data/work/handbook/mini-cordis-lab-handbook.md
```

```unknown
bash -lc rm -f /mnt/data/work/handbook/build/mini-cordis-lab-handbook-revised.pdf && python /home/oai/skills/pdfs/scripts/md_to_pdf.py /mnt/data/work/handbook/mini-cordis-lab-handbook.md --output /mnt/data/work/handbook/build/mini-cordis-lab-handbook-revised.pdf --pdf_engine xelatex --extra=--listings --extra=--highlight-style=tango
```

```unknown
bash -lc pdfinfo /mnt/data/work/handbook/build/mini-cordis-lab-handbook-revised.pdf | sed -n '1,40p'; pdffonts /mnt/data/work/handbook/build/mini-cordis-lab-handbook-revised.pdf | sed -n '1,30p'
```

```unknown
bash -lc rm -rf /mnt/data/work/handbook/rendered-revised && python /home/oai/skills/pdfs/scripts/render_pdf.py /mnt/data/work/handbook/build/mini-cordis-lab-handbook-revised.pdf --out_dir /mnt/data/work/handbook/rendered-revised --dpi 110 && rm -rf /mnt/data/work/handbook/contact-revised && python - <<'PY'
from PIL import Image, ImageDraw
from pathlib import Path
src=Path('/mnt/data/work/handbook/rendered-revised'); out=Path('/mnt/data/work/handbook/contact-revised'); out.mkdir()
files=sorted(src.glob('page-*.png')); cols=5; rows=5; thumb=(182,257); margin=16; label_h=18
for start in range(0,len(files),cols*rows):
    batch=files[start:start+cols*rows]
    sheet=Image.new('RGB',(margin*2+cols*thumb[0],margin*2+rows*(thumb[1]+label_h)),'white'); d=ImageDraw.Draw(sheet)
    for j,f in enumerate(batch):
        im=Image.open(f).convert('RGB'); im.thumbnail(thumb)
        x=margin+(j%cols)*thumb[0]+(thumb[0]-im.width)//2; y=margin+(j//cols)*(thumb[1]+label_h)+(thumb[1]-im.height)//2
        sheet.paste(im,(x,y)); d.text((margin+(j%cols)*thumb[0]+3,margin+(j//cols)*(thumb[1]+label_h)+thumb[1]+1),str(start+j+1),fill='black')
    p=out/f'contact-{start+1:03d}-{start+len(batch):03d}.png'; sheet.save(p,optimize=True); print(p)
PY
```

```unknown
bash -lc ls -lh /mnt/data/work/handbook/contact-revised 2>/dev/null || true; ls /mnt/data/work/handbook/rendered-revised | tail
```

```unknown
bash -lc rm -rf /mnt/data/work/handbook/contact-revised && mkdir -p /mnt/data/work/handbook/contact-revised && python - <<'PY'
from PIL import Image, ImageDraw
from pathlib import Path
src=Path('/mnt/data/work/handbook/rendered-revised'); out=Path('/mnt/data/work/handbook/contact-revised')
files=sorted(src.glob('page-*.png')); cols=5; rows=5; thumb=(182,257); margin=16; label_h=18
for start in range(0,len(files),cols*rows):
    batch=files[start:start+cols*rows]
    sheet=Image.new('RGB',(margin*2+cols*thumb[0],margin*2+rows*(thumb[1]+label_h)),'white'); d=ImageDraw.Draw(sheet)
    for j,f in enumerate(batch):
        with Image.open(f) as base:
            im=base.convert('RGB')
            im.thumbnail(thumb)
        x=margin+(j%cols)*thumb[0]+(thumb[0]-im.width)//2; y=margin+(j//cols)*(thumb[1]+label_h)+(thumb[1]-im.height)//2
        sheet.paste(im,(x,y)); d.text((margin+(j%cols)*thumb[0]+3,margin+(j//cols)*(thumb[1]+label_h)+thumb[1]+1),str(start+j+1),fill='black')
    p=out/f'contact-{start+1:03d}-{start+len(batch):03d}.jpg'; sheet.save(p,quality=82,optimize=True); print(p)
PY
```

The full draft is now typeset at 175 pages; revision added worked isolation/interception extensions and fuller metatheory traces. I’m now visual-QAing equations, code, diagrams, and page flow.

```unknown
bash -lc pdftotext -layout /mnt/data/work/handbook/build/mini-cordis-lab-handbook-revised.pdf /mnt/data/work/handbook/revised.txt && python - <<'PY'
from pathlib import Path
pages=Path('/mnt/data/work/handbook/revised.txt').read_text(errors='replace').split('\f')
for needle in ['Suggested algorithm','Testing asynchronous traces','Definition: monoid homomorphism','Lab 7: Executable Metatheory','Definition: bounded model checker','References']:
    print('\n',needle)
    for i,p in enumerate(pages,1):
        if needle in p:
            print(i)
PY
```

```unknown
bash -lc python - <<'PY'
from pathlib import Path
p=Path('/mnt/data/work/handbook/chapters/00-front.md')
s=p.read_text().replace('toc-depth: 2','toc-depth: 1')
p.write_text(s)
PY
# rebuild combined
cat /mnt/data/work/handbook/chapters/00-front.md /mnt/data/work/handbook/chapters/01-orientation-lab0.md /mnt/data/work/handbook/chapters/02-lab1.md /mnt/data/work/handbook/chapters/03-lab2.md /mnt/data/work/handbook/chapters/04-lab3.md /mnt/data/work/handbook/chapters/05-lab4.md /mnt/data/work/handbook/chapters/06-lab5.md /mnt/data/work/handbook/chapters/07-lab6.md /mnt/data/work/handbook/chapters/08-lab7.md /mnt/data/work/handbook/chapters/09-lab8.md /mnt/data/work/handbook/chapters/10-capstone.md /mnt/data/work/handbook/chapters/11-appendix-ts.md /mnt/data/work/handbook/chapters/12-appendix-api.md /mnt/data/work/handbook/chapters/13-appendix-glossary.md /mnt/data/work/handbook/chapters/14-appendix-reading.md /mnt/data/work/handbook/chapters/15-appendix-prooflab.md /mnt/data/work/handbook/chapters/16-bibliography.md > /mnt/data/work/handbook/mini-cordis-lab-handbook.md
python /home/oai/skills/pdfs/scripts/md_to_pdf.py /mnt/data/work/handbook/mini-cordis-lab-handbook.md --output /mnt/data/work/handbook/build/mini-cordis-lab-handbook-finalcandidate.pdf --pdf_engine xelatex --extra=--listings --extra=--highlight-style=tango
pdfinfo /mnt/data/work/handbook/build/mini-cordis-lab-handbook-finalcandidate.pdf | grep -E 'Pages|Page size|File size'
```

```unknown
bash -lc rm -rf /mnt/data/work/handbook/rendered-finalcandidate && python /home/oai/skills/pdfs/scripts/render_pdf.py /mnt/data/work/handbook/build/mini-cordis-lab-handbook-finalcandidate.pdf --out_dir /mnt/data/work/handbook/rendered-finalcandidate --dpi 110
```

```unknown
bash -lc pdftotext -layout /mnt/data/work/handbook/build/mini-cordis-lab-handbook-finalcandidate.pdf /mnt/data/work/handbook/finalcandidate.txt && python - <<'PY'
from pathlib import Path
pages=Path('/mnt/data/work/handbook/finalcandidate.txt').read_text(errors='replace').split('\f')
for needle in ['Preface','Orientation: Why Dynamic Composition','Lab 0: The Mathematical','Lab 1: Effects','Lab 7: Executable','References']:
    print(needle,[i for i,p in enumerate(pages,1) if needle in p][:10])
PY
```

```unknown
bash -lc rm -rf /mnt/data/work/handbook/contact-finalcandidate && mkdir -p /mnt/data/work/handbook/contact-finalcandidate && python - <<'PY'
from PIL import Image, ImageDraw
from pathlib import Path
src=Path('/mnt/data/work/handbook/rendered-finalcandidate'); out=Path('/mnt/data/work/handbook/contact-finalcandidate')
files=sorted(src.glob('page-*.png')); cols=5; rows=5; thumb=(182,257); margin=16; label_h=18
for start in range(0,len(files),cols*rows):
    batch=files[start:start+cols*rows]
    sheet=Image.new('RGB',(margin*2+cols*thumb[0],margin*2+rows*(thumb[1]+label_h)),'white'); d=ImageDraw.Draw(sheet)
    for j,f in enumerate(batch):
        with Image.open(f) as base:
            im=base.convert('RGB'); im.thumbnail(thumb)
        x=margin+(j%cols)*thumb[0]+(thumb[0]-im.width)//2; y=margin+(j//cols)*(thumb[1]+label_h)+(thumb[1]-im.height)//2
        sheet.paste(im,(x,y)); d.text((margin+(j%cols)*thumb[0]+3,margin+(j//cols)*(thumb[1]+label_h)+thumb[1]+1),str(start+j+1),fill='black')
    p=out/f'contact-{start+1:03d}-{start+len(batch):03d}.jpg'; sheet.save(p,quality=80,optimize=True); print(p)
PY
```

```unknown
bash -lc python - <<'PY'
import re
from pathlib import Path
root=Path('/mnt/data/work/handbook/chapters')
for lab,name in enumerate(['01-orientation-lab0.md','02-lab1.md','03-lab2.md','04-lab3.md','05-lab4.md','06-lab5.md','07-lab6.md','08-lab7.md','09-lab8.md']):
    text=(root/name).read_text().splitlines()
    nums=[]
    for ln,line in enumerate(text,1):
        m=re.match(r'##\s+(\d+)\.(\d+)\b',line)
        if m:
            nums.append((int(m.group(1)),int(m.group(2)),ln,line))
    print(name, [(a,b) for a,b,_,_ in nums])
    # validate main lab prefix and contiguous range
    if nums:
        prefixes=set(a for a,b,_,_ in nums)
        print(' prefixes',prefixes,'gaps',[n for n in range(1,max(b for a,b,_,_ in nums)+1) if n not in [b for a,b,_,_ in nums]])
PY
```

```unknown
bash -lc python - <<'PY'
import re
from pathlib import Path
for p in sorted(Path('/mnt/data/work/handbook/chapters').glob('0[1-9]-*.md')):
    seen={}
    for i,line in enumerate(p.read_text().splitlines(),1):
        for m in re.finditer(r'(?:exercise|Extension|Counterexample)\s+(\d+\.\d+)',line,re.I):
            key=m.group(1)
            seen.setdefault(key,[]).append(i)
    dups={k:v for k,v in seen.items() if len(v)>1}
    if dups: print(p.name,'duplicates',dups)
PY
```

```unknown
bash -lc sed -n '1,260p' /home/oai/skills/pdfs/SKILL.md
```

```unknown
bash -lc python /home/oai/skills/pdfs/scripts/pdf_inspect.py /mnt/data/work/handbook/build/mini-cordis-lab-handbook-finalcandidate.pdf | sed -n '1,220p'; echo '---PREFLIGHT---'; python /home/oai/skills/pdfs/scripts/pdf_preflight.py /mnt/data/work/handbook/build/mini-cordis-lab-handbook-finalcandidate.pdf | sed -n '1,240p'
```

```unknown
bash -lc command -v aspell || command -v hunspell || true
```

```unknown
bash -lc command -v languagetool || command -v vale || command -v proselint || python - <<'PY'
mods=['language_tool_python','proselint','textblob','wordfreq','wordninja']
for m in mods:
 try:
  __import__(m); print(m,'yes')
 except: pass
PY
```

```unknown
bash -lc python - <<'PY'
try:
 import codespell_lib
 print('codespell yes')
except Exception as e: print('no codespell',e)
PY
```

```unknown
bash -lc sed -n '1,620p' /mnt/data/work/handbook/chapters/12-appendix-api.md
```

```unknown
bash -lc python - <<'PY'
from pathlib import Path
for f in ['/mnt/data/work/handbook/mini-cordis-lab-handbook.md','/mnt/data/work/handbook/finalcandidate.txt']:
    t=Path(f).read_text(errors='replace')
    print(f,'replacement chars',t.count('\ufffd'),'NUL',t.count('\x00'))
PY
```

```unknown
bash -lc sed -n '1,280p' /mnt/data/work/handbook/chapters/15-appendix-prooflab.md
```

```unknown
bash -lc grep -n 'Gamma.*infty\|Gamma_\\infty\|\\Gamma\\^\\infty\|Gamma∞' /mnt/data/work/handbook/mini-cordis-lab-handbook.md | head -20
```

```unknown
bash -lc grep -ni -E 'unified context|recursive context|self-similar|fixed-point type|mu.*Gamma|Γ∞|context paradigm' /mnt/data/work/handbook/mini-cordis-lab-handbook.md | head -80
```

```unknown
bash -lc sed -n '1990,2085p' /mnt/data/work/handbook/mini-cordis-lab-handbook.md
```

```unknown
bash -lc grep -ni -E 'isolation|interception|realm|intercept' /mnt/data/work/handbook/mini-cordis-lab-handbook.md | head -120
```

```unknown
bash -lc sed -n '2800,2945p' /mnt/data/work/handbook/mini-cordis-lab-handbook.md
```

```unknown
bash -lc grep -n -A150 -B5 '## 3.3 The coeffect context' /mnt/data/work/handbook/chapters/04-lab3.md
```

```unknown
bash -lc python - <<'PY'
from pathlib import Path
p=Path('/mnt/data/work/handbook/chapters/04-lab3.md')
s=p.read_text()
needle='''The generic `Key<T>` carries the static association between a key and its value type. Internally, the heterogeneous map stores `unknown`; the API restores type information at its boundary.\n\n## 3.4 `get` and `set`\n'''
insert=r'''The generic `Key<T>` carries the static association between a key and its value type. Internally, the heterogeneous map stores `unknown`; the API restores type information at its boundary.

### Definition: the unified recursive context

The effect scope and the coeffect store must not become unrelated global mechanisms. A service provision is itself an effect, and a component's dependency view must be associated with the same context that owns its recovery.

The paper expresses this unification as the recursive type

$$
\Gamma_\infty
=\mu\Gamma.\;\Gamma\times(\Gamma\to\Gamma)\times\Sigma.
$$

The binder $\mu\Gamma$ says that the first component is another context of the same overall kind. Each level therefore carries:

1. a parent or recursively contained context state;
2. an accumulator for effects owned at this level;
3. a coeffect context containing dependencies visible at this level.

Mini-Cordis does not allocate a literally infinite value. It realises the recursive equation as a finite tree of context nodes created while the program runs:

```ts
interface ContextNode {
  readonly parent: ContextNode | null;
  readonly scope: EffectScope;
  readonly services: ServiceStore;
}
```

**Worked example.** The root context owns process-wide logging. A plugin fiber receives a child context with its own effect scope and inherited service resolution. The plugin creates a second child for a test component. Disposing the test child withdraws only its effects; disposing the plugin child also retires the test child; neither action destroys the root logger.

```text
root context
  services: logger
  scope: process lifetime
  |
  +-- notes-plugin context
      services: notes
      scope: notes effects
      |
      +-- test context
          services: fake-clock
          scope: test effects
```

> **Why this is a programming paradigm rather than one data structure.** The important discipline is that every relevant environmental read and write is mediated by a context with attributable lifecycle ownership. A global service locator beside an unrelated cleanup stack may contain the same raw information, but it does not impose this attribution or recursive composition.

### Side extension: coeffect isolation

**Motivation.** Two components may use the same logical key but need different bindings. A test should resolve `DatabaseKey` to a fake database without replacing the production database for every component.

Let $R$ be a set of **realms**. An isolation-aware coeffect context contains:

$$
\rho:K\rightharpoonup R
\qquad\text{and}\qquad
\sigma:(r:R)\rightharpoonup V_r.
$$

Lookup first resolves the logical key to a realm and then reads the realm's binding:

$$
\operatorname{get}(k)(\rho,\sigma)=\sigma(\rho(k)).
$$

A key with no explicit mapping can use itself as its default realm. An `isolate(k,r)` operation derives a child context whose realm map sends $k$ to $r$ while leaving the parent unchanged.

```ts
interface IsolatingContext {
  isolate<T>(key: Key<T>, realm?: symbol): IsolatingContext;
  get<T>(key: Key<T>): T;
}
```

**Worked example.** The root resolves `DatabaseKey` through realm `production`. A test child maps the same key to realm `test-42` and provides an in-memory database there. Code in the test child still asks for `DatabaseKey`; only its context changes the resolution.

Isolation is a **derived realisation**: recovery discards the child context rather than mutating and then repairing the parent's realm table.

### Side extension: coeffect interception

**Motivation.** Sometimes the binding should stay the same while the policy governing its use changes. A filesystem dependency can remain available, yet one component may be limited to `/tmp/plugin-a` and another to read-only access under `/data`.

For each key $k$, let metadata values form a monoid $(M_k,\oplus,\epsilon)$. A provider can be represented as a function from merged metadata to the value or capability exposed to the consumer:

$$
\operatorname{provider}_k:M_k\to V_k.
$$

The component declares metadata, the enclosing context may add or override metadata, and lookup combines them before invoking the provider. The metadata changes *how* the coeffect is used, not whether the dependency key is present, so an interception change need not deactivate the component.

```ts
interface InterceptingContext {
  intercept<M>(
    key: Key<unknown>,
    metadata: M,
    merge: (inner: M, outer: M) => M
  ): InterceptingContext;
}
```

**Worked example.** `FileSystemKey` remains provided by one host service. A plugin's specification requests `{ read: ["/data"], write: [] }`. Its enclosing context adds `{ read: ["/data"], write: ["/tmp/plugin"] }` under the key's merge rule. The provider constructs a capability that checks every operation against the merged policy.

> **Scope of the core labs.** The required implementation keeps one flat realm and no interception metadata so that the lifecycle theory remains visible. Exercises 3.7-3.8 and the capstone may add these mechanisms. Their purpose here is to make Section 3.2.3 of the paper readable, not to obscure the minimal runtime with framework engineering.

## 3.4 `get` and `set`
'''
if needle not in s: raise SystemExit('needle missing')
s=s.replace(needle,insert)
p.write_text(s)
PY
python - <<'PY'
from pathlib import Path
b=Path('/mnt/data/work/handbook/chapters/04-lab3.md').read_bytes()
print('controls',sorted(set(x for x in b if x<32 and x not in (9,10,13))))
PY
sed -n '132,290p' /mnt/data/work/handbook/chapters/04-lab3.md
```

```unknown
bash -lc ls -l /mnt/data/work/handbook/chapters && tail -n 80 /mnt/data/work/handbook/chapters/04-lab3.md && tail -n 100 /mnt/data/work/handbook/chapters/13-appendix-glossary.md && tail -n 120 /mnt/data/work/handbook/chapters/14-appendix-reading.md
```

```unknown
bash -lc grep -n -A180 -B20 'unified recursive context\|isolation realm\|interception' /mnt/data/work/handbook/chapters/04-lab3.md | head -n 260 && head -n 120 /mnt/data/work/handbook/chapters/13-appendix-glossary.md && grep -n -A60 -B10 'category-theory map\|Paper construct\|Concept map\|Appendix E' /mnt/data/work/handbook/chapters/14-appendix-reading.md /mnt/data/work/handbook/chapters/15-appendix-prooflab.md /mnt/data/work/handbook/chapters/13-appendix-glossary.md
```

```unknown
bash -lc grep -n '^## ' /mnt/data/work/handbook/chapters/13-appendix-glossary.md | sed -n '1,220p' && grep -n -A30 -B10 '^## 3\.1\|^## 3\.2\|^## 3\.3' /mnt/data/work/handbook/chapters/04-lab3.md | head -n 180 && grep -n -A20 -B5 'Learning outcomes\|Lab profile' /mnt/data/work/handbook/chapters/04-lab3.md | head -n 100
```

```unknown
bash -lc head -n 180 /mnt/data/work/handbook/chapters/00-front.md && cat /mnt/data/work/handbook/chapters/16-bibliography.md
```

```unknown
bash -lc grep -n -A200 -B10 '^# Appendix B\|^## B\.' /mnt/data/work/handbook/chapters/12-appendix-api.md | head -n 320
```

```unknown
bash -lc python - <<'PY'
from pathlib import Path

root = Path('/mnt/data/work/handbook/chapters')

# Lab 3 updates
p = root/'04-lab3.md'
s = p.read_text()
s = s.replace(
"> **Lab profile.** Estimated effort: 6-8 hours. Prerequisite: Milestone A. Main artifact: a typed service context with revertible provision, satisfaction checking, and reactive notification. Paper focus: Sections 3.2.1-3.2.2.",
"> **Lab profile.** Estimated effort: 6-8 hours. Prerequisite: Milestone A. Main artifact: a typed service context with revertible provision, satisfaction checking, and reactive notification. Paper focus: Sections 3.2.1-3.2.3 and 3.3.1."
)
s = s.replace(
"- implement a typed finite dependency context;\n- define and evaluate a coeffect specification;",
"- implement a typed finite dependency context;\n- explain how effect ownership and dependency resolution meet in a unified recursive context;\n- distinguish a flat context from isolation and interception extensions;\n- define and evaluate a coeffect specification;"
)
s = s.replace(
"**Primary paper:** Sections 2.2, 2.3, 3.2.1, and 3.2.2. Skim 3.2.3 to see how isolation and interception generalise the flat table.",
"**Primary paper:** Sections 2.2, 2.3, 3.2.1-3.2.3, and 3.3.1. Read the flat coeffect context first, then use isolation, interception, and the unified context to identify which parts are core semantics and which are scoped extensions."
)
p.write_text(s)

# Glossary entries
p = root/'13-appendix-glossary.md'
s = p.read_text()
s = s.replace(
"## Coeffect context ($\\Sigma$)\n\nA finite dependent partial map from keys to values of the types associated with those keys.\n\n## Coeffect specification ($d$)",
"## Coeffect context ($\\Sigma$)\n\nA finite dependent partial map from keys to values of the types associated with those keys.\n\n## Coeffect interception\n\nA derived context adjustment that changes how a dependency is used without changing which logical key is satisfied. Component-declared and context-carried metadata are merged before the provider exposes a value or capability.\n\n## Coeffect isolation\n\nA derived context adjustment that redirects a logical dependency key through an isolation realm, allowing the same key to resolve to different bindings in different child contexts.\n\n## Coeffect specification ($d$)"
)
s = s.replace(
"## In-place realisation\n\n",
"## In-place realisation\n\n"
)
s = s.replace(
"## Installed\n\n",
"## Isolation realm\n\nAn identifier used as the storage-level target of a logical dependency key. A realm map $\\rho:K\\rightharpoonup R$ lets child contexts redirect one key without renaming the key in component code.\n\n## Installed\n\n"
)
s = s.replace(
"## Metatheory\n\n",
"## Metadata monoid\n\nFor an intercepted key, a set of policy or usage metadata equipped with an associative merge operation and identity. The merge determines how component-declared metadata combines with context-carried constraints.\n\n## Metatheory\n\n"
)
s = s.replace(
"## Reactive coeffect\n\nA runtime environmental requirement whose satisfaction is re-evaluated when the context changes, driving activation, deactivation, or a neutral response.\n\n## Reference model",
"## Reactive coeffect\n\nA runtime environmental requirement whose satisfaction is re-evaluated when the context changes, driving activation, deactivation, or a neutral response.\n\n## Realm map\n\nA partial map $\\rho:K\\rightharpoonup R$ from logical dependency keys to isolation realms. Lookup resolves a key through this map before consulting the realm-indexed value store.\n\n## Recursive context type\n\nA type defined in terms of itself, commonly written with a least fixed-point binder $\\mu$. In this handbook, $\\Gamma_\\infty=\\mu\\Gamma.\\;\\Gamma\\times(\\Gamma\\to\\Gamma)\\times\\Sigma$ is realised as a finite runtime tree of context nodes, each owning recovery and dependency resolution.\n\n## Reference model"
)
s = s.replace(
"## Twisted composition\n\nComposition of forward/inverse pairs where forward maps compose normally and inverses compose in reverse order.\n\n## Vestigial entry",
"## Twisted composition\n\nComposition of forward/inverse pairs where forward maps compose normally and inverses compose in reverse order.\n\n## Unified context\n\nA context that carries both effect ownership and coeffect information, rather than placing cleanup and dependency resolution in unrelated global mechanisms. Its recursive form supports nested component lifetimes.\n\n## Vestigial entry"
)
p.write_text(s)

# Reading plan mapping
p = root/'14-appendix-reading.md'
s = p.read_text().replace(
"| 3 | paper §3.2.1-3.2.2 | Petricek coeffects motivation | coeffect calculus/thesis |",
"| 3 | paper §3.2.1-3.2.3, §3.3.1 | Petricek coeffects motivation | coeffect calculus/thesis; scoped dependency systems |"
)
p.write_text(s)

# Concept map additions
p = root/'15-appendix-prooflab.md'
s = p.read_text()
s = s.replace(
"| $\\partial\\Gamma$ | state plus accumulator | `EffectContext<S>` | prefix recovery invariant |\n| $\\mathcal{E}_\\Gamma$",
"| $\\partial\\Gamma$ | state plus accumulator | `EffectContext<S>` | prefix recovery invariant |\n| `track` | monoid homomorphism | instrumentation that accumulates inverses | identity/composition preservation tests |\n| $\\mathcal{E}_\\Gamma$"
)
s = s.replace(
"| $\\Sigma$ | dependent partial map | typed service store | type tests and domain tests |\n| $d$",
"| $\\Sigma$ | dependent partial map | typed service store | type tests and domain tests |\n| $\\Gamma_\\infty$ | recursive/fixed-point context | finite tree of `ContextNode`s | nested ownership and inherited-resolution tests |\n| $\\rho:K\\rightharpoonup R$ | realm redirection | context-local isolation map | same key, different child binding test |\n| interception metadata | monoidal policy composition | context-derived capability wrapper | merged-policy access tests |\n| $d$"
)
s = s.replace(
"| $\\simeq$ | observational equivalence | `observe`/per-key relation | endpoint comparison |",
"| $\\simeq$ | observational equivalence | `observe`/per-key relation | endpoint comparison |\n| $\\Gamma/\\simeq$ | quotient by observation | canonical observable states | representation-insensitive equality tests |"
)
p.write_text(s)

# API reference optional extensions
p = root/'12-appendix-api.md'
s = p.read_text()
needle = "Core preconditions:\n\n- a key has at most one active provider in one flat realm;\n- a provider may install only declared keys;\n- withdrawal notifies affected consumers;\n- only active fibers participate in current provider resolution;\n- committed lookup may reach an installed unloading provider.\n\n"
addition = r'''Core preconditions:

- a key has at most one active provider in one flat realm;
- a provider may install only declared keys;
- withdrawal notifies affected consumers;
- only active fibers participate in current provider resolution;
- committed lookup may reach an installed unloading provider.

### Optional scoped-context extensions

The required runtime may keep one flat realm. A capstone that implements the paper's scoped extensions can use:

```ts
export interface ContextNode {
  readonly parent: ContextNode | null;
  readonly scope: EffectScope;
  readonly services: ServiceStore;

  isolate<T>(key: Key<T>, realm?: symbol): ContextNode;

  intercept<M>(
    key: Key<unknown>,
    metadata: M,
    merge: (inner: M, outer: M) => M
  ): ContextNode;
}
```

`isolate` derives a child whose logical key resolves through a different realm. `intercept` derives a child whose metadata changes the capability exposed at a key. Neither operation mutates the parent; discarding the child is its recovery.

'''
if needle not in s:
    raise SystemExit('API insertion needle not found')
s = s.replace(needle, addition)
p.write_text(s)

print('updated')
PY

# Sanity report
grep -n '^## Coeffect\|^## Isolation\|^## Metadata\|^## Realm\|^## Recursive\|^## Unified' /mnt/data/work/handbook/chapters/13-appendix-glossary.md
grep -n 'Lab profile\|unified recursive\|Primary paper' /mnt/data/work/handbook/chapters/04-lab3.md | head -n 20
grep -n '\\Gamma_\\infty\|track.*homomorphism\|interception metadata' /mnt/data/work/handbook/chapters/15-appendix-prooflab.md
```

```unknown
bash -lc sed -n '40,75p' /mnt/data/work/handbook/chapters/13-appendix-glossary.md; sed -n '185,255p' /mnt/data/work/handbook/chapters/13-appendix-glossary.md; sed -n '315,355p' /mnt/data/work/handbook/chapters/13-appendix-glossary.md; sed -n '440,468p' /mnt/data/work/handbook/chapters/13-appendix-glossary.md; sed -n '105,190p' /mnt/data/work/handbook/chapters/12-appendix-api.md
```

```unknown
bash -lc grep -n -A16 -B4 '^## Reactive coeffect' /mnt/data/work/handbook/chapters/13-appendix-glossary.md && grep -n -A8 -B4 '^## Provision' /mnt/data/work/handbook/chapters/13-appendix-glossary.md && grep -n 'Recursive context\|Realm map' /mnt/data/work/handbook/chapters/13-appendix-glossary.md
```

<details><summary>💭 Thinking</summary>

**Revised, audited, and preflighted handbook PDF and supporting sections**

</details>

```unknown
bash -lc python - <<'PY'
from pathlib import Path
root=Path('/mnt/data/work/handbook/chapters')

p=root/'13-appendix-glossary.md'
s=p.read_text()
needle="## Reactive coeffect\n\nA runtime coeffect discipline in which context changes are classified against specifications and cause activation/deactivation.\n\n## Reference model"
replacement=r'''## Reactive coeffect

A runtime coeffect discipline in which context changes are classified against specifications and cause activation/deactivation.

## Realm map

A partial map $\rho:K\rightharpoonup R$ from logical dependency keys to isolation realms. Lookup resolves a key through this map before consulting the realm-indexed value store.

## Reconciliation

The process of comparing declarative desired configuration with running fibers and issuing orchestration operations to align them.

## Recover

Apply an accumulator to withdraw tracked effects and reset the accumulator to identity.

## Recovery exactness

A global temporal property: unloading one fiber yields the state that foreign steps alone would have produced, up to control bookkeeping and observational equivalence.

## Recursive context type

A type defined in terms of itself, commonly written with a least fixed-point binder $\mu$. In this handbook, $\Gamma_\infty=\mu\Gamma.\;\Gamma\times(\Gamma\to\Gamma)\times\Sigma$ is realised as a finite runtime tree of context nodes, each owning recovery and dependency resolution.

## Reference model'''
if needle not in s:
    raise SystemExit('glossary needle missing')
s=s.replace(needle,replacement)
# Remove duplicated blocks now superseded later in source.
dups=[
"## Reconciliation\n\nThe process of comparing declarative desired configuration with running fibers and issuing orchestration operations to align them.\n\n",
"## Recover\n\nApply an accumulator to withdraw tracked effects and reset the accumulator to identity.\n\n",
"## Recovery exactness\n\nA global temporal property: unloading one fiber yields the state that foreign steps alone would have produced, up to control bookkeeping and observational equivalence.\n\n",
]
# retain first occurrence and remove subsequent occurrences
for block in dups:
    first=s.find(block)
    second=s.find(block, first+len(block)) if first>=0 else -1
    while second>=0:
        s=s[:second]+s[second+len(block):]
        second=s.find(block, first+len(block))
p.write_text(s)

p=root/'04-lab3.md'
s=p.read_text()
old=r'''### Extension 3.8 - Capability metadata

A filesystem key provides an API, but each consumer should be restricted to particular paths. Sketch metadata attached to a requirement and an interception layer that enforces it without changing whether the dependency is satisfied.

### Theory exercise 3.9 - Local guarantee
'''
new=r'''### Extension 3.8 - Isolation realms

Add a realm map and derive two child contexts from one parent. Both children request the same `DatabaseKey`, but one resolves to a production database and the other to an in-memory test database.

Your submission must show:

1. the parent context is unchanged;
2. identical component code resolves different values in the two children;
3. disposing one child does not withdraw the other child's binding;
4. the logical dependency declaration remains `DatabaseKey` in both components.

State whether isolation changes satisfaction, resolution, or both in your design.

### Extension 3.9 - Capability metadata

A filesystem key provides an API, but each consumer should be restricted to particular paths. Define a metadata monoid, attach metadata to a requirement, and sketch an interception layer that enforces the merged policy without changing whether the dependency is satisfied. Include two merge examples and one non-associative merge rule that must be rejected.

### Theory exercise 3.10 - Local guarantee
'''
if old not in s:
    raise SystemExit('exercise needle missing')
s=s.replace(old,new)
p.write_text(s)

print('patched')
PY

grep -n '^## Realm\|^## Reconciliation\|^## Recover$\|^## Recovery exactness\|^## Recursive' /mnt/data/work/handbook/chapters/13-appendix-glossary.md
grep -n -A36 'Extension 3.7' /mnt/data/work/handbook/chapters/04-lab3.md
```

```unknown
bash -lc python - <<'PY'
from pathlib import Path
root=Path('/mnt/data/work/handbook')
chap=root/'chapters'
order=[
'00-front.md','01-orientation-lab0.md','02-lab1.md','03-lab2.md','04-lab3.md','05-lab4.md','06-lab5.md','07-lab6.md','08-lab7.md','09-lab8.md','10-capstone.md','11-appendix-ts.md','12-appendix-api.md','13-appendix-glossary.md','14-appendix-reading.md','15-appendix-prooflab.md','16-bibliography.md'
]
out=root/'mini-cordis-lab-handbook.md'
parts=[]
for i,name in enumerate(order):
    text=(chap/name).read_text().rstrip()
    parts.append(text)
out.write_text('\n\n\\newpage\n\n'.join(parts)+'\n')
print(out)
print('chars',len(out.read_text()),'lines',len(out.read_text().splitlines()),'words',len(out.read_text().split()))
PY

python - <<'PY'
from pathlib import Path
p=Path('/mnt/data/work/handbook/mini-cordis-lab-handbook.md')
s=p.read_text()
# Basic audits
print('fences', s.count('```'), 'balanced', s.count('```')%2==0)
ctrl=[(i,ord(c)) for i,c in enumerate(s) if ord(c)<32 and c not in '\n\t\r']
print('control chars',len(ctrl),ctrl[:10])
print('h1',sum(1 for l in s.splitlines() if l.startswith('# ')))
print('h2',sum(1 for l in s.splitlines() if l.startswith('## ')))
print('latex newpages',s.count('\\newpage'))
for pat in ['TODO','TBD','FIXME','PLACEHOLDER','[insert','lorem ipsum']:
    print(pat,s.lower().count(pat.lower()))
PY

# Parse Markdown through Pandoc as a structural check
pandoc /mnt/data/work/handbook/mini-cordis-lab-handbook.md -f markdown -t native -o /tmp/mini-cordis.native
wc -c /tmp/mini-cordis.native

```

```unknown
bash -lc mkdir -p /mnt/data/work/handbook/build && python /home/oai/skills/pdfs/scripts/md_to_pdf.py /mnt/data/work/handbook/mini-cordis-lab-handbook.md --output /mnt/data/work/handbook/build/mini-cordis-lab-handbook.pdf --pdf_engine xelatex --extra=--listings --extra=--highlight-style=tango
```

```unknown
bash -lc pdfinfo /mnt/data/work/handbook/build/mini-cordis-lab-handbook.pdf | sed -n '1,30p'; pdffonts /mnt/data/work/handbook/build/mini-cordis-lab-handbook.pdf | sed -n '1,25p'; rm -rf /mnt/data/work/handbook/rendered-final && python /home/oai/skills/pdfs/scripts/render_pdf.py /mnt/data/work/handbook/build/mini-cordis-lab-handbook.pdf --out_dir /mnt/data/work/handbook/rendered-final --dpi 110
```

```unknown
bash -lc pdftotext -layout /mnt/data/work/handbook/build/mini-cordis-lab-handbook.pdf /tmp/handbook.txt && python - <<'PY'
from pathlib import Path
text=Path('/tmp/handbook.txt').read_text(errors='replace')
pages=text.split('\f')
for needle in ['unified recursive context','Side extension: coeffect isolation','Side extension: coeffect interception','Extension 3.8 - Isolation realms','Appendix C: Glossary','Recursive context type','Optional scoped-context extensions','Concept map']:
    hits=[]
    for i,p in enumerate(pages,1):
        if needle.lower() in p.lower(): hits.append(i)
    print(needle,hits)
print('pages',len(pages))
PY
ls /mnt/data/work/handbook/rendered-final | sed -n '1,12p'
```

<details><summary>💭 Thinking</summary>

**Updated glossary, validated handbook Markdown, compiled PDF, and identified relevant pages**

</details>

```unknown
bash -lc python - <<'PY'
from PIL import Image, ImageOps, ImageDraw
from pathlib import Path
pages=[1,6,51,54,55,63,137,143,152,163,168]
root=Path('/mnt/data/work/handbook/rendered-final')
thumbs=[]
for n in pages:
    im=Image.open(root/f'page-{n:03d}.png').convert('RGB')
    w=620
    h=round(im.height*w/im.width)
    im=im.resize((w,h))
    canvas=Image.new('RGB',(w,h+35),'white')
    canvas.paste(im,(0,35))
    d=ImageDraw.Draw(canvas)
    d.text((10,8),f'Page {n}',fill='black')
    thumbs.append(canvas)
cols=3
rows=(len(thumbs)+cols-1)//cols
cellw=max(t.width for t in thumbs)
cellh=max(t.height for t in thumbs)
sheet=Image.new('RGB',(cols*cellw,rows*cellh),(220,220,220))
for i,t in enumerate(thumbs):
    x=(i%cols)*cellw; y=(i//cols)*cellh
    sheet.paste(t,(x,y))
out='/mnt/data/work/handbook/final-review-contact.png'
sheet.save(out,quality=95)
print(out,sheet.size)
PY
```

```unknown
bash -lc grep -n '^## 3\.' /mnt/data/work/handbook/chapters/04-lab3.md
```

```unknown
bash -lc python /home/oai/skills/pdfs/scripts/pdf_inspect.py /mnt/data/work/handbook/build/mini-cordis-lab-handbook.pdf > /mnt/data/work/handbook/build/pdf-inspect.txt && cat /mnt/data/work/handbook/build/pdf-inspect.txt && echo '--- preflight ---' && python /home/oai/skills/pdfs/scripts/pdf_preflight.py /mnt/data/work/handbook/build/mini-cordis-lab-handbook.pdf > /mnt/data/work/handbook/build/pdf-preflight.txt && cat /mnt/data/work/handbook/build/pdf-preflight.txt && echo '--- extracted text anomalies ---' && python - <<'PY'
from pathlib import Path
s=Path('/tmp/handbook.txt').read_text(errors='replace')
for token in ['�','□',' ']:
    print(repr(token),s.count(token))
print('empty pages', [i+1 for i,p in enumerate(s.split('\f')) if not p.strip()][:20])
PY
```

```unknown
bash -lc ls -l /mnt/data/work/handbook/build/pdf-*.txt; printf '%s\n' '--- inspect ---'; cat /mnt/data/work/handbook/build/pdf-inspect.txt 2>&1; printf '%s\n' '--- preflight ---'; cat /mnt/data/work/handbook/build/pdf-preflight.txt 2>&1; printf '%s\n' '--- status ---'; python /home/oai/skills/pdfs/scripts/pdf_preflight.py /mnt/data/work/handbook/build/mini-cordis-lab-handbook.pdf; echo rc=$?
```

```unknown
bash -lc python /home/oai/skills/pdfs/scripts/pdf_inspect.py --help 2>&1 | head -n 80; echo '---'; python /home/oai/skills/pdfs/scripts/pdf_inspect.py /mnt/data/work/handbook/build/mini-cordis-lab-handbook.pdf 2>&1 | head -n 100; echo rc=${PIPESTATUS[0]}
```

```unknown
bash -lc python /home/oai/skills/pdfs/scripts/pdf_inspect.py /mnt/data/work/handbook/build/mini-cordis-lab-handbook.pdf > /mnt/data/work/handbook/build/pdf-inspect.txt 2>&1; python /home/oai/skills/pdfs/scripts/pdf_preflight.py /mnt/data/work/handbook/build/mini-cordis-lab-handbook.pdf > /mnt/data/work/handbook/build/pdf-preflight.txt 2>&1; pdftotext -layout /mnt/data/work/handbook/build/mini-cordis-lab-handbook.pdf /tmp/handbook-final.txt; python - <<'PY'
from pathlib import Path
s=Path('/tmp/handbook-final.txt').read_text(errors='replace')
print('replacement_char',s.count('\ufffd'))
print('nul',s.count('\x00'))
blank=[i+1 for i,p in enumerate(s.split('\f')) if not p.strip()]
print('blank_pages',blank)
print('formfeeds',s.count('\f'))
PY
cat /mnt/data/work/handbook/build/pdf-preflight.txt
```

```unknown
bash -lc cp /mnt/data/work/handbook/mini-cordis-lab-handbook.md /mnt/data/mini-cordis-lab-handbook.md
cp /mnt/data/work/handbook/build/mini-cordis-lab-handbook.pdf /mnt/data/mini-cordis-lab-handbook.pdf
ls -lh /mnt/data/mini-cordis-lab-handbook.md /mnt/data/mini-cordis-lab-handbook.pdf
sha256sum /mnt/data/mini-cordis-lab-handbook.md /mnt/data/mini-cordis-lab-handbook.pdf
pdfinfo /mnt/data/mini-cordis-lab-handbook.pdf | grep -E 'Pages|Page size|File size|Title'
```

<details><summary>💭 Thinking</summary>

**Created and validated handbook PDFs with visual and structural checks**

</details>

# Building Mini-Cordis

The handbook is complete. It preserves the paper’s distinction between temporal and spatial composability, then develops revertible effects, reactive coeffects, components, fibers, lifecycle semantics, and metatheory through an executable Mini-Cordis runtime. fileciteturn0file0L8-L20 Its recurring pedagogical structure is the proposed relationship between paper notation, a small executable model, and a property or invariant. fileciteturn1file0L1-L17

The finished textbook is **193 pages** and contains:

- Labs 0–8, plus an optional studio on isolation and interception
- Motivation, formal definitions, worked calculations, implementations, executable laws, counterexamples, exercises, deliverables, and reading guides
- TypeScript APIs, pseudocode, mathematical notation, lifecycle diagrams, dependency diagrams, and model-checking workflows
- A theory companion covering effects, coeffects, operational semantics, category theory, observational equivalence, reversibility, and trace theory
- A consolidated reference architecture
- Appendices containing a notation glossary, proof and property templates, submission checklists, assessment rubric, and annotated resource guide

The PDF was rendered and visually inspected across chapter openings, equations, code listings, tables, callout boxes, diagrams, appendices, and page transitions.

### Files

- [Download the PDF textbook](sandbox:/mnt/data/mini-cordis-lab-handbook.pdf)
- [Open the Markdown source](sandbox:/mnt/data/mini-cordis-lab-handbook-source/mini-cordis-lab-handbook.md)
- [Download the complete Markdown source bundle](sandbox:/mnt/data/mini-cordis-lab-handbook-source.zip) — includes all diagrams, the Markdown source, rendering instructions, and the LaTeX styling file.

