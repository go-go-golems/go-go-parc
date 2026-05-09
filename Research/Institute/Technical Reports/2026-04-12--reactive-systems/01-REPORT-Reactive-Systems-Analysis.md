---
title: 'Reactive Systems: History, SICP Connections, and Implementation Patterns'
aliases: []
tags:
  - reactive-systems
  - signals
  - SICP
  - FRP
  - dependency-graph
  - loupedeck
  - implementation
  - technical-report
ticket: TECH-REPORT-2026-04-12
created: 2026-04-12
updated: 2026-04-12
---

# Reactive Systems: History, SICP Connections, and Implementation Patterns

## Executive Summary

This report examines the theoretical foundations and implementation patterns of reactive systems, with specific analysis of the loupedeck-test codebase's reactive JavaScript runtime. We trace the lineage from SICP's streams and assignment through Functional Reactive Programming (FRP) to modern signal-based architectures used by SolidJS, Angular, Preact, and Svelte. The loupedeck implementation represents a clean, minimal signal-based reactive system with explicit dependency tracking, batching, and effect scheduling—demonstrating core principles that underpin modern frontend frameworks.

---

## 1. Historical Foundations

### 1.1 SICP: Streams as Signals (Section 3.5)

The intellectual lineage of reactive programming traces directly to *Structure and Interpretation of Computer Programs* (SICP), Section 3.5: "Streams." Sussman and Abelson introduced streams as "computational analogs of the 'signals' in signal-processing systems." This was revolutionary because it provided an alternative to assignment and mutable state.

Key insights from SICP 3.5:

- **Streams decouple time from evaluation**: Unlike assignment where `set!` happens at a specific moment, streams represent values that unfold over time
- **Lazy evaluation enables infinite sequences**: Streams can model continuously varying signals without requiring infinite memory
- **Signal processing as functional composition**: Operations like `stream-map`, `stream-filter`, and `stream-add` correspond to signal processing blocks

The critical passage from SICP 3.5.3:

> "We can model electrical circuits using streams to represent the values of currents or voltages at a sequence of times. For instance, suppose we have an RC circuit consisting of a resistor of resistance R and a capacitor of capacitance C in series. The voltage response v of the circuit to an injected current i is determined by the formula..."

This establishes the fundamental insight: **time-varying values can be modeled as first-class data structures**, not as state mutations requiring complex synchronization.

### 1.2 Assignment vs. Propagation: The Core Tension

SICP Chapter 3 explores two approaches to modeling state:

1. **Assignment and Local State** (Section 3.1-3.4): Uses `set!` to mutate variables; requires careful handling of time, environment, and concurrency
2. **Streams** (Section 3.5): Models change through functional transformation of time-indexed values

The reactive systems we examine today are descendants of the stream approach—though they often reintroduce assignment in controlled ways (signals are mutable, but their propagation follows functional dependencies).

### 1.3 Constraint Propagation: The Predecessor to Dependency Graphs

SICP Section 3.3.5 on "Propagation of Constraints" introduces a system where values propagate through a network of constraints. This is conceptually similar to modern reactive dependency graphs:

- **Connectors** bind values (like reactive signals)
- **Constraints** enforce relationships (like computed values)
- **Propagation** updates dependent values automatically

```scheme
;; SICP constraint system (simplified)
(define (adder a b sum)
  (define (process-new-value)
    (cond ((and (has-value? a) (has-value? b))
           (set-value! sum (+ (get-value a) (get-value b))))
          ...))
  ...)
```

This pattern—where changes to input values automatically propagate through a dependency network—is the essence of reactive programming.

---

## 2. The Evolution of Functional Reactive Programming (FRP)

### 2.1 Fran (1997): FRP's Genesis

Conal Elliott's "Functional Reactive Animation" (ICFP 1997) introduced Fran, the first mature FRP system. Fran's key innovation was treating time-varying values as **behaviors**—functions from time to values:

```haskell
-- Fran-style (conceptual)
type Behavior a = Time -> a

-- A circle whose radius varies with time
growingCircle :: Behavior Shape
growingCircle = circle (sin time * 50)
```

Fran's contributions:
- **Continuous time model**: Behaviors are defined for all real-number times
- **Declarative animation**: Describe what should happen, not how to render it
- **Compositional reactivity**: Complex behaviors built from simple ones via function composition

### 2.2 Yampa (2002): Arrowized FRP

Yampa (Haskell) addressed FRP's "time leak" problem (where accumulating event history causes memory bloat). It used **arrows** to control the formation of recursive signal functions:

```haskell
-- Yampa: explicit signal function composition
counter :: SF () Int
counter = proc () -> do
  rec count <- integral -< 1
  returnA -< count
```

Yampa introduced:
- **Signal Functions (SF)**: Explicit transformer types between signals
- **Arrow notation**: Controlled feedback loops
- **Efficient sampling**: Discrete event handling without time leaks

### 2.3 Elm (2012): FRP for the Masses

Evan Czaplicki's Elm brought FRP to web developers. Elm's original architecture:

```elm
-- Elm 0.16 (FRP era)
type alias Model = { count : Int }

-- Signals of user inputs
clickSignal : Signal ()
clickSignal = Mouse.clicks

-- Fold signals into state
counterSignal : Signal Int
counterSignal = foldp (\_ count -> count + 1) 0 clickSignal
```

Elm's "A Farewell to FRP" (2016) acknowledged practical limitations:
> "When I started working on my thesis in 2011, I stumbled upon this academic subfield called Functional Reactive Programming (FRP). By stripping that approach down and putting a nicer syntax on it, Elm became a really pleasant way to create interactive apps. But as Elm got more popular, certain problems started coming up again and again."

Elm moved away from explicit signals toward The Elm Architecture (TEA)—simplifying for mainstream adoption while retaining reactive principles under the hood.

---

## 3. Modern Signal-Based Architectures

### 3.1 KnockoutJS (2010): The Pioneer

Released July 2010, KnockoutJS brought automatic dependency tracking to mainstream JavaScript:

```javascript
// KnockoutJS: Implicit dependency tracking
function ViewModel() {
    this.firstName = ko.observable('John');
    this.lastName = ko.observable('Doe');
    
    // Dependencies tracked automatically
    this.fullName = ko.computed(function() {
        return this.firstName() + ' ' + this.lastName();
    }, this);
}
```

Knockout's `ko.dependencyDetection` subsystem:
- Registers observables accessed during computed evaluation
- Establishes subscriber relationships
- Triggers re-evaluation when dependencies change

This established the pattern that persists today: **implicit dependency collection during execution**.

### 3.2 MobX (2015): Transparent FRP

Michel Weststrate's MobX introduced "transparent functional reactive programming":

```javascript
// MobX: Decorator-based observables
class Timer {
    @observable secondsPassed = 0;
    
    @computed get minutesPassed() {
        return this.secondsPassed / 60;
    }
    
    @action increment() {
        this.secondsPassed++;
    }
}
```

MobX's key insights:
1. **Proxy-based observation**: ES6 Proxies intercept property access
2. **Automatic dependency tracking**: No explicit subscription management
3. **Action/Transaction boundaries**: Batch changes for consistency
4. **Derivation graph**: Computed values form a lazy, cached computation graph

### 3.3 Vue 3 (2020): The Reactivity API

Vue 3 extracted its reactivity system into a standalone package (`@vue/reactivity`):

```javascript
// Vue 3 Reactivity API
import { ref, computed, effect } from '@vue/reactivity';

const count = ref(0);
const double = computed(() => count.value * 2);

effect(() => {
    console.log('Count changed:', count.value);
});
```

Vue's design:
- **Ref**: Container for reactive values (explicit `.value` access)
- **Computed**: Lazy, memoized derived values
- **Effect**: Side-effect execution with automatic dependency tracking
- **Proxy-based**: Deep reactivity through ES6 Proxies

### 3.4 SolidJS (2021): Fine-Grained Purity

Ryan Carniato's SolidJS eliminated the virtual DOM entirely through fine-grained reactivity:

```javascript
// SolidJS: Signals without VDOM overhead
import { createSignal, createEffect, createMemo } from 'solid-js';

const [count, setCount] = createSignal(0);
const double = createMemo(() => count() * 2);

createEffect(() => {
    console.log('Count:', count());
});
```

SolidJS innovations:
- **Fine-grained updates**: Only changed DOM nodes update
- **Compilation-time optimization**: Reactive graph built at compile time
- **Signal lifecycle**: Explicit disposal management
- **No VDOM overhead**: Direct binding to DOM operations

### 3.5 Preact Signals (2022): Framework-Agnostic Reactivity

Preact introduced signals as a framework-agnostic primitive:

```javascript
// Preact Signals: Framework-agnostic
import { signal, computed, effect } from '@preact/signals-core';

const count = signal(0);
const double = computed(() => count.value * 2);

effect(() => {
    console.log('Count:', count.value);
});
```

Key distinction: Preact Signals separate the **core reactivity engine** from framework binding, enabling use in React, Vue, or vanilla JS.

### 3.6 Angular Signals (2023): Mainstream Adoption

Angular 16+ introduced signals as first-class primitives:

```typescript
// Angular Signals
import { signal, computed, effect } from '@angular/core';

const count = signal(0);
const double = computed(() => count() * 2);

effect(() => {
    console.log('Count:', count());
});
```

Angular's implementation emphasizes:
- **Producer/consumer model**: Explicit distinction between sources and derived values
- **Equality checking**: Skip updates when values are semantically equal
- **Glitch-free propagation**: Ensure consistent intermediate states

### 3.7 Svelte 5 Runes (2024): Compile-Time Reactivity

Svelte 5 introduced "runes"—explicit reactive syntax:

```svelte
<!-- Svelte 5: Runes for explicit reactivity -->
<script>
  let count = $state(0);
  let double = $derived(count * 2);
  
  $effect(() => {
    console.log('Count:', count);
  });
</script>
```

Runes represent a hybrid approach:
- **Explicit opt-in**: Reactivity requires `$state`, `$derived`, or `$effect`
- **Compile-time transformation**: Runes become reactive graph nodes
- **Performance**: No runtime proxy overhead

---

## 4. Implementation Pattern Analysis

### 4.1 Core Primitives

Every modern reactive system implements four primitives:

| Primitive | Purpose | Access Pattern |
|-----------|---------|----------------|
| **Signal/Atom/Observable** | Mutable reactive state | `.get()` / `.set()` or `.value` |
| **Computed/Memo/Derivation** | Lazy derived values | Cached, auto-invalidated |
| **Effect/Reaction/Autorun** | Side-effect execution | Runs when dependencies change |
| **Batch/Transaction/Action** | Atomic updates | Defer propagation until end |

### 4.2 Dependency Graph Structure

The dependency graph has two fundamental node types:

1. **Sources (Producers)**: Signals that can change
2. **Targets (Consumers)**: Computeds and Effects that depend on sources

Graph properties:
- **Directed**: Dependencies flow from sources to targets
- **Acyclic**: Cycles must be detected and prevented
- **Dynamic**: Dependencies can change between evaluations
- **Lazy**: Computeds evaluate only when accessed

### 4.3 The Reactive Algorithm

All signal-based systems follow a similar execution model:

```
PHASE 1: Track
  When a computed/effect executes:
  - Clear previous dependencies
  - Set global "current collector"
  - Execute the function
  - Intercept all .get() calls
  - Register dependencies

PHASE 2: Notify
  When a signal changes:
  - Check equality (skip if equal)
  - Update internal value
  - Mark all dependents as "dirty"
  - Schedule effects for execution

PHASE 3: Flush
  On next tick or batch end:
  - Execute dirty effects
  - Evaluate dirty computeds (lazily or eagerly)
  - Repeat until quiescence
```

### 4.4 Batching and Consistency

Batching prevents intermediate states from triggering partial updates:

```javascript
// Without batching: two updates
state.a = 1;  // triggers effects
state.b = 2;  // triggers effects again

// With batching: single update
batch(() => {
    state.a = 1;
    state.b = 2;
});  // effects run once
```

Glitch-free propagation ensures that during a batch, effects see consistent states.

---

## 5. The Loupedeck Reactive System: Implementation Analysis

### 5.1 Architecture Overview

The loupedeck-test codebase implements a minimal, clean reactive system in Go with JavaScript bindings. Located in `runtime/reactive/`, it demonstrates core principles without framework-specific complexity.

### 5.2 Core Components

#### Signal (`signal.go`)

```go
type Signal[T any] struct {
    rt    *Runtime
    value T
    equal func(a, b T) bool
    src   sourceNode
}

func (s *Signal[T]) Get() T {
    s.rt.trackDependency(s)  // Register dependency
    return s.value
}

func (s *Signal[T]) Set(value T) {
    if s.equal != nil && s.equal(s.value, value) {
        return  // Skip if equal
    }
    s.value = value
    s.src.notifyDependents()  // Mark dependents dirty
    s.rt.maybeFlush()         // Schedule effects
}
```

**Design choices**:
- Generic `T any` for type safety
- Pluggable `equal` function for custom equality
- Automatic dependency registration on `Get()`

#### Computed (`computed.go`)

```go
type Computed[T any] struct {
    rt          *Runtime
    fn          func() T
    value       T
    initialized bool
    dirty       bool
    evaluating  bool
    deps        dependencySet
    src         sourceNode
}

func (c *Computed[T]) Get() T {
    c.rt.trackDependency(c)  // Register as dependency of parent
    if c.dirty || !c.initialized {
        c.evaluate()         // Lazy re-evaluation
    }
    return c.value
}

func (c *Computed[T]) evaluate() {
    if c.evaluating {
        panic("cyclic computed evaluation")
    }
    c.evaluating = true
    c.deps.clear(c)         // Clear old dependencies
    defer func() { c.evaluating = false }()

    c.rt.withCollector(c, func() {
        c.value = c.fn()    // Collect dependencies during execution
    })
    c.initialized = true
    c.dirty = false
}
```

**Design choices**:
- Lazy evaluation: only recompute when accessed while dirty
- Cycle detection via `evaluating` flag
- Dynamic dependencies: deps cleared and rebuilt each evaluation

#### Effect (`effect.go`)

```go
type Effect struct {
    rt         *Runtime
    fn         func()
    active     bool
    dirty      bool
    queued     bool
    evaluating bool
    deps       dependencySet
}

func (e *Effect) run() {
    if e.evaluating {
        panic("reentrant effect execution")
    }
    e.evaluating = true
    e.deps.clear(e)
    defer func() { e.evaluating = false }()

    e.rt.withCollector(e, func() {
        e.fn()  // Collect dependencies
    })
    e.dirty = false
}
```

**Design choices**:
- Eager execution: runs on next tick when marked dirty
- Reentrancy protection
- Explicit `Stop()` for cleanup

#### Dependency Tracking (`graph.go`)

```go
type sourceNode struct {
    dependents map[dependentNode]struct{}
}

func (s *sourceNode) notifyDependents() {
    dependents := make([]dependentNode, 0, len(s.dependents))
    for dependent := range s.dependents {
        dependents = append(dependents, dependent)
    }
    for _, dependent := range dependents {
        dependent.markDirty()
    }
}

type dependencySet struct {
    deps []dependencySource
    seen map[dependencySource]struct{}
}

func (d *dependencySet) track(owner dependentNode, source dependencySource) {
    if _, ok := d.seen[source]; ok {
        return  // Deduplicate
    }
    d.seen[source] = struct{}{}
    d.deps = append(d.deps, source)
    source.addDependent(owner)  // Bidirectional link
}
```

**Design choices**:
- Bidirectional links for O(1) registration/unregistration
- Snapshot iteration in `notifyDependents()` (safe against concurrent modification)
- Deduplication via `seen` map

#### Runtime (`runtime.go`)

```go
type Runtime struct {
    current        dependencyCollector  // Currently collecting effect/computed
    batchDepth     int                  // Nesting level for batching
    flushing       bool                 // Prevent reentrant flush
    pendingEffects map[*Effect]struct{} // Effects to run
}

func (r *Runtime) Batch(fn func()) {
    r.batchDepth++
    defer func() {
        r.batchDepth--
        if r.batchDepth == 0 {
            r.Flush()
        }
    }()
    fn()
}

func (r *Runtime) Flush() {
    if r.flushing {
        return
    }
    r.flushing = true
    defer func() { r.flushing = false }()

    for len(r.pendingEffects) > 0 {
        // Snapshot and clear
        effects := make([]*Effect, 0, len(r.pendingEffects))
        for effect := range r.pendingEffects {
            effects = append(effects, effect)
            delete(r.pendingEffects, effect)
            effect.queued = false
        }
        // Execute
        for _, effect := range effects {
            if effect.active && effect.dirty {
                effect.run()
            }
        }
    }
}
```

**Design choices**:
- Single-threaded (owner thread model)
- Batch nesting support
- Snapshot-and-execute pattern prevents issues from effect registration during flush

### 5.3 JavaScript Integration

The reactive system is exposed to JavaScript via `runtime/js/module_state/`:

```go
// Exposing signals to JavaScript
exports.Set("signal", func(call goja.FunctionCall) goja.Value {
    initial := exportValue(call.Argument(0))
    sig := reactive.NewSignal(env.Reactive, initial)
    return signalObject(bindings, ownerCtx, runtime, sig)
})

exports.Set("computed", func(call goja.FunctionCall) goja.Value {
    fn, ok := goja.AssertFunction(call.Argument(0))
    if !ok {
        panic(runtime.NewTypeError("state.computed requires a function"))
    }
    cmp := reactive.NewComputed(env.Reactive, func() any {
        // Execute in owner thread
        result, err := bindings.Owner.Call(ownerCtx, "state.computed", ...)
        return exportValue(result)
    })
    // Return object with .get()
})

exports.Set("watch", func(call goja.FunctionCall) goja.Value {
    fn, ok := goja.AssertFunction(call.Argument(0))
    sub := env.Reactive.Watch(func() {
        bindings.Owner.Call(ownerCtx, "state.watch", func() {
            fn(goja.Undefined())
        })
    })
    return stopHandleObject(runtime, sub)
})
```

**Integration patterns**:
- **Thread serialization**: All JS execution goes through `Owner.Call()` for thread safety
- **Value marshaling**: `exportValue()` converts between Goja (JS) and Go types
- **Subscription lifecycle**: Stop handles exposed as JS objects

### 5.4 Integration with Animation

The reactive system integrates with the animation runtime (`module_anim/`):

```go
// Animation can target signals
exports.Set("to", func(call goja.FunctionCall) goja.Value {
    get, set := numericTarget(bindings, ownerCtx, runtime, call.Argument(0))
    to := call.Argument(1).ToFloat()
    duration := time.Duration(call.Argument(2).ToInteger()) * time.Millisecond
    ease := easingFromArg(...)
    
    h := env.Anim.TweenFloat64(get, set, to, duration, ease)
    return handleObject(runtime, h)
})
```

This enables declarative animation:

```javascript
const state = require('loupedeck/state');
const anim = require('loupedeck/anim');

const level = state.signal(0);
anim.to(level, 100, 500, easing.linear);  // Animate signal from 0 to 100
```

### 5.5 Test Coverage Analysis

The test suite (`runtime_test.go`) validates critical properties:

1. **Equality optimization**: Setting equal values doesn't trigger watchers
2. **Invalidation chains**: Changes propagate through computed dependencies
3. **Diamond graphs**: `left` and `right` both depending on `base` doesn't cause `total` to recompute twice
4. **Batching**: Nested batches defer effects until outermost completes
5. **Cycle detection**: Cyclic computed evaluation panics
6. **Reentrancy protection**: Effect calling itself panics
7. **Cleanup**: Stopped watchers detach from dependencies

### 5.6 Design Strengths

1. **Minimal surface area**: Only 6 core files, ~400 lines of Go
2. **Type safety**: Generics for signal/computed values
3. **Explicit control**: Batch boundaries, effect stopping, equality functions
4. **Clean separation**: Reactive core is independent of JS runtime
5. **Testable**: Pure Go tests without JS dependency
6. **Thread model**: Clear owner thread semantics prevent races

### 5.7 Comparison to Other Implementations

| Feature | Loupedeck | SolidJS | Vue 3 | MobX |
|---------|-----------|---------|-------|------|
| Language | Go/JS | JS | JS | JS |
| Equality check | Configurable | `===` | `===` | Deep by default |
| Batching | Explicit | Automatic | Automatic | Automatic |
| Cleanup | Manual `Stop()` | Auto on dispose | Auto on unmount | Auto via GC |
| Lazy computed | Yes | Yes | Yes | Yes |
| Diamond handling | Yes | Yes | Yes | Yes |
| Thread safety | Owner thread | Single-threaded | Single-threaded | Single-threaded |

---

## 6. Theoretical Connections

### 6.1 From SICP Streams to Signals

The conceptual bridge:

| SICP Concept | Modern Equivalent |
|--------------|-------------------|
| `cons-stream` (lazy pair) | Signal with lazy evaluation |
| `stream-map` | Computed transformation |
| `stream-filter` | Conditional computed |
| `force` (evaluate thunk) | `.get()` on computed |
| `delay` (create thunk) | `.set()` without immediate effect flush |

SICP's key insight—that we can model time-varying values as data structures rather than state mutations—persists in modern signals. The difference is pragmatic: signals use assignment internally (for performance) but present a functional interface (for reasoning).

### 6.2 Category Theory Connections

Reactive systems relate to:
- **Functors**: `map` operation on signals
- **Applicatives**: Combining multiple signals
- **Monads**: Flattening nested signals
- **Comonads**: Accessing signal history (in some FRP variants)

Conal Elliott's FRP work explicitly used these abstractions; modern systems tend to hide them but preserve the structure.

### 6.3 The Spreadsheet Analogy

Spreadsheets are the most successful reactive system ever deployed:
- **Cells** = Signals
- **Formulas** = Computeds
- **Recalculation** = Effect flush
- **Circular reference error** = Cycle detection

Microsoft Excel's calculation engine handles millions of cells with similar dependency tracking to loupedeck's implementation—demonstrating the scalability of the approach.

---

## 7. Practical Applications and Future Directions

### 7.1 When to Use Signal-Based Reactivity

Appropriate for:
- UI state management
- Animation systems
- Real-time data visualization
- Game state
- Form handling

Less appropriate for:
- Simple one-off event handling
- Server-side request/response
- Stateless transformations

### 7.2 Implementation Checklist

When building a reactive system:

1. [ ] Define primitives (signal, computed, effect)
2. [ ] Implement dependency graph (bidirectional)
3. [ ] Add cycle detection
4. [ ] Implement batching/transaction support
5. [ ] Add equality checking for optimization
6. [ ] Handle diamond dependencies correctly
7. [ ] Implement cleanup/disposal
8. [ ] Add reentrancy protection
9. [ ] Test with concurrent modifications
10. [ ] Profile memory usage under load

### 7.3 Research Frontiers

Active research areas:
- **Distributed reactive systems**: Propagation across network boundaries
- **Glitch-free distributed consistency**: Ensuring all nodes see consistent states
- **Time-travel debugging**: Recording and replaying signal histories
- **Compile-time optimization**: Svelte-style pre-computation of reactive graphs
- **Hardware acceleration**: GPU-accelerated reactive computations

---

## 8. Conclusion

The loupedeck reactive system represents a clean, minimal implementation of principles that have evolved from SICP's streams through Fran's FRP to modern signal-based frameworks. Its Go/JS architecture demonstrates that these concepts transcend language boundaries.

Key takeaways:

1. **The SICP lineage is direct**: Streams as signals (3.5) and constraint propagation (3.3.5) are the theoretical ancestors of all modern reactive systems.

2. **Implementation patterns converge**: Despite different syntax (Solid's `createSignal`, Vue's `ref`, Angular's `signal`), all implementations share the same dependency graph structure and execution model.

3. **Primitives are stable**: Signal, computed, effect, and batch have become the standard vocabulary—evident in Preact, Vue, Angular, and Svelte's recent additions.

4. **Performance matters**: Modern systems prioritize fine-grained updates, lazy evaluation, and efficient dependency tracking—the loupedeck implementation demonstrates these concerns with its explicit batching and equality configuration.

5. **Integration requires care**: The JS/Go bridge in loupedeck shows that reactive systems need clear thread ownership models when crossing language boundaries.

The reactive paradigm has proven its value across three decades of evolution—from academic curiosity to the foundation of modern frontend development. Understanding these foundations, as this report has traced them, enables developers to build better reactive systems and make informed choices among existing implementations.

---

## References and Sources

### Primary Sources

1. Abelson, H., Sussman, G. J., & Sussman, J. (1996). *Structure and Interpretation of Computer Programs* (2nd ed.). MIT Press. Sections 3.3.5 (Constraint Propagation), 3.5 (Streams).

2. Elliott, C. (1997). "Functional Reactive Animation." *ICFP '97*. https://dl.acm.org/doi/10.1145/258949.258973

3. Elliott, C., & Hudak, P. (1997). "Functional Reactive Animation." *ACM SIGPLAN Notices*, 32(8), 263-273.

### Historical Implementations

4. Paterson, R. (2003). "Arrows and Computation." In *The Fun of Programming*. Palgrave Macmillan.

5. Courtney, A., & Elliott, C. (2001). "Genuinely Functional User Interfaces." *Haskell Workshop*.

6. Czaplicki, E. (2012). "Elm: Concurrent FRP for Functional GUIs." *PLDI '13*. https://people.seas.harvard.edu/~chong/pubs/pldi13-elm.pdf

7. Czaplicki, E. (2016). "A Farewell to FRP." *elm-lang.org*. https://elm-lang.org/news/farewell-to-frp

### Modern Frameworks

8. Carniato, R. (2021). "A Hands-on Introduction to Fine-Grained Reactivity." *DEV Community*. https://dev.to/ryansolid/a-hands-on-introduction-to-fine-grained-reactivity-3ndf

9. Weststrate, M. (2015-2023). *MobX Documentation*. https://mobx.js.org/

10. You, E. (2020). *Vue 3 Reactivity API*. https://vuejs.org/guide/extras/reactivity-in-depth.html

11. Preact Team. (2022). *Preact Signals Guide*. https://preactjs.com/guide/v10/signals/

12. Angular Team. (2023). *Angular Signals*. https://angular.dev/guide/signals

13. Harris, R. (2024). *Svelte 5 Runes*. https://svelte.dev/blog/runes

### Academic Surveys

14. Bainomugisha, E., et al. (2013). "A Survey on Reactive Programming." *ACM Computing Surveys*, 45(4). https://dl.acm.org/doi/10.1145/2501654.2501666

15. Myter, F., & De Meuter, W. (2019). "Distributed Reactive Programming for Reactive Distributed Systems." *Programming '19*. http://myter.be/wp-content/uploads/2021/03/Programming19.pdf

### Implementation Resources

16. KnockoutJS. (2010-2023). *Dependency Tracking Documentation*. https://knockoutjs.com/documentation/computed-dependency-tracking.html

17. Miller, J. (2023). "Angular Signals, Reactive Context, and Dynamic Dependency Tracking." *Medium*. https://medium.com/@eugeniyoz/angular-signals-reactive-context-and-dynamic-dependency-tracking-d2d6100568b0

### Codebase Reference

18. Loupedeck reactive runtime. `runtime/reactive/` in `/home/manuel/code/wesen/2026-04-11--loupedeck-test`.

---

## Appendix A: Reactive System Timeline

```
1984  SICP published (streams in Section 3.5)
1997  Fran (Functional Reactive Animation) - Conal Elliott
2002  Yampa (Arrowized FRP)
2010  KnockoutJS (implicit dependency tracking)
2012  Elm (FRP for web, later abandoned)
2015  MobX (transparent FRP)
2016  Vue 2 (Object.defineProperty reactivity)
2020  Vue 3 (Proxy-based reactivity, standalone API)
2021  SolidJS (fine-grained without VDOM)
2022  Preact Signals (framework-agnostic)
2023  Angular Signals (mainstream adoption)
2024  Svelte 5 Runes (compile-time reactivity)
2025  TC39 Signals proposal (stage 0)
```

---

## Appendix B: Code Examples Directory

The accompanying code workspace includes:

- `scripts/basic-signal.js`: Minimal signal/computed/effect example
- `scripts/diamond-dependency.js`: Diamond graph test case
- `scripts/batching-demo.js`: Batch operation demonstration
- `scripts/loupedeck-reactive-test.go`: Direct Go tests mirroring framework tests

See `ttmp/2026/04/12/TECH-REPORT-2026-04-12--reactive-systems-history-sicp-connections-and-implementation-patterns/scripts/` for runnable examples.

---

*End of Technical Report*
