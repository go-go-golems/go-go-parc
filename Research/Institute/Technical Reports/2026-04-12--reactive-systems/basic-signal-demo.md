---
title: 'Basic Signal Demo - Reactive Primitives'
tags: [reactive-systems, signals, demo, loupedeck]
created: 2026-04-12
type: script-example
---

# Basic Signal Demo

This demonstrates the three fundamental reactive primitives: signals, computed values, and effects.

## JavaScript Example (Loupedeck Runtime)

```javascript
const state = require('loupedeck/state');

// 1. SIGNAL: Mutable reactive state
const count = state.signal(0);

// 2. COMPUTED: Derived value (lazy, cached)
const double = state.computed(() => count.get() * 2);

// 3. EFFECT: Side-effect execution
const stopWatcher = state.watch(() => {
    console.log(`Count: ${count.get()}, Double: ${double.get()}`);
});

// Initial effect run
// Output: "Count: 0, Double: 0"

// Update signal
count.set(5);
// Output: "Count: 5, Double: 10"

// Cleanup
stopWatcher.stop();
```

## Conceptual Model

```
┌─────────┐     depends on     ┌───────────┐
│  count  │────────────────────▶│  double   │
│ (signal)│                     │(computed) │
└────┬────┘                     └─────┬─────┘
     │                                │
     │         triggers               │
     └────────────────────────────────┘
                    │
                    ▼
            ┌──────────────┐
            │   effect     │
            │ (console.log)│
            └──────────────┘
```

## Key Behaviors

1. **Lazy evaluation**: `double` only recomputes when accessed while dirty
2. **Automatic dependency tracking**: No explicit subscription management
3. **Equality optimization**: Setting same value doesn't trigger effects
4. **Cleanup**: `stop()` detaches all dependencies

## Comparison to Other Frameworks

| Framework | Signal | Computed | Effect |
|-----------|--------|----------|--------|
| Loupedeck | `state.signal()` | `state.computed()` | `state.watch()` |
| SolidJS | `createSignal()` | `createMemo()` | `createEffect()` |
| Vue 3 | `ref()` | `computed()` | `watchEffect()` |
| Preact | `signal()` | `computed()` | `effect()` |
| Angular | `signal()` | `computed()` | `effect()` |
| Svelte 5 | `$state()` | `$derived()` | `$effect()` |

## Testing the Behavior

```javascript
// Test equality optimization
const s = state.signal(1);
let runs = 0;
state.watch(() => {
    runs++;
    s.get();
});
// runs = 1 (initial)

s.set(1); // Same value - no effect run
// runs = 1 (unchanged!)

s.set(2); // Different value
// runs = 2
```

## SICP Connection

This is the modern realization of SICP Section 3.5's streams:

```scheme
;; SICP: Streams as signals
(define ones (cons-stream 1 ones))
(define integers (cons-stream 1 (add-streams ones integers)))

;; Modern: Signals with operators
const ones = state.signal(1);
const integers = state.computed(() => ones.get() + previous);
```

The difference is pragmatic: signals use assignment internally for performance, while presenting a functional interface for reasoning.
