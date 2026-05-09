---
title: 'Diamond Dependency Test - Graph Handling'
tags: [reactive-systems, dependency-graph, diamond-problem, loupedeck]
created: 2026-04-12
type: script-example
---

# Diamond Dependency Test

This demonstrates how a well-designed reactive system handles diamond-shaped dependency graphs without redundant recomputation.

## The Diamond Problem

```
        ┌─────────┐
        │  base   │
        │ (signal)│
        └────┬────┘
             │
        ┌────┴────┐
        │         │
        ▼         ▼
   ┌─────────┐ ┌─────────┐
   │  left   │ │  right  │
   │(computed)│ (computed)│
   └────┬────┘ └────┬────┘
        │           │
        └─────┬─────┘
              │
              ▼
        ┌───────────┐
        │   total   │
        │ (computed)│
        └───────────┘
```

**The problem**: When `base` changes, both `left` and `right` become dirty. When `total` is accessed, it reads both. A naive system would:
1. Read `left` → recompute (dirty)
2. `left` reads `base` during recomputation
3. Read `right` → recompute (dirty)
4. `right` reads `base` during recomputation
5. **Result**: `base` is read twice, potentially causing inconsistency

**The solution**: Proper reactive systems handle this via:
- Lazy evaluation (only compute when accessed)
- Consistent snapshot of source values
- Idempotent source reads

## JavaScript Example (Loupedeck Runtime)

```javascript
const state = require('loupedeck/state');

// Source signal
const base = state.signal(2);

// Both branches depend on base
let leftRuns = 0;
let rightRuns = 0;
let totalRuns = 0;

const left = state.computed(() => {
    leftRuns++;
    return base.get() + 1;  // left = base + 1
});

const right = state.computed(() => {
    rightRuns++;
    return base.get() * 2;  // right = base * 2
});

const total = state.computed(() => {
    totalRuns++;
    return left.get() + right.get();  // total = left + right
});

// Watch to trigger evaluation
state.watch(() => {
    console.log(`Total: ${total.get()}`);
});

// Initial state: base=2, left=3, right=4, total=7
// leftRuns=1, rightRuns=1, totalRuns=1

// Update base
base.set(3);
// Expected: base=3, left=4, right=6, total=10

// CRITICAL: With proper diamond handling:
// leftRuns=2 (not 3!)
// rightRuns=2 (not 3!)
// totalRuns=2
```

## Go Implementation (from loupedeck codebase)

The test from `runtime/reactive/runtime_test.go`:

```go
func TestDiamondDependencyGraphDoesNotDoubleEvaluateDownstreamComputed(t *testing.T) {
    rt := NewRuntime()
    base := NewSignal(rt, 2)

    leftRuns := 0
    left := NewComputed(rt, func() int {
        leftRuns++
        return base.Get() + 1
    })

    rightRuns := 0
    right := NewComputed(rt, func() int {
        rightRuns++
        return base.Get() * 2
    })

    totalRuns := 0
    total := NewComputed(rt, func() int {
        totalRuns++
        return left.Get() + right.Get()
    })

    watchRuns := 0
    rt.Watch(func() {
        watchRuns++
        _ = total.Get()
    })

    base.Set(3)

    // Assertions: Each computed should only run twice (initial + update)
    if leftRuns != 2 || rightRuns != 2 || totalRuns != 2 {
        t.Fatalf("expected one downstream reevaluation per computed")
    }
}
```

## Why This Matters

1. **Performance**: Prevents O(n²) recomputation in deep/wide graphs
2. **Consistency**: All computeds see the same source values during a propagation
3. **Predictability**: Developers can reason about evaluation counts

## Comparison Table

| Framework | Diamond Handling | Mechanism |
|-----------|-----------------|-----------|
| Loupedeck | Yes | Lazy evaluation + dirty flag |
| Vue 3 | Yes | Recursively track + skip unchanged |
| SolidJS | Yes | Topological ordering |
| MobX | Yes | Dependency tree + memoization |
| KnockoutJS | Yes (with plugin) | De-duplication via subscription keys |

## Testing Diamond Handling

```javascript
function testDiamond(system) {
    const base = system.signal(1);
    let branch1Runs = 0;
    let branch2Runs = 0;
    
    const branch1 = system.computed(() => {
        branch1Runs++;
        return base.get() * 2;
    });
    
    const branch2 = system.computed(() => {
        branch2Runs++;
        return base.get() * 3;
    });
    
    const total = system.computed(() => {
        return branch1.get() + branch2.get();
    });
    
    // Force initial evaluation
    system.watch(() => total.get());
    
    // Reset counters after initialization
    branch1Runs = 0;
    branch2Runs = 0;
    
    // Update base
    base.set(2);
    
    // Read total (triggers evaluation)
    total.get();
    
    // Assert: Each branch should only run once
    console.assert(branch1Runs === 1, 'branch1 should run once');
    console.assert(branch2Runs === 1, 'branch2 should run once');
}
```

## The Algorithm

A properly implemented reactive system handles diamonds through:

1. **Dirty marking**: When `base` changes, mark all dependents as dirty
2. **Lazy evaluation**: Don't recompute until accessed
3. **Consistent read**: During a single "read transaction", cache source values
4. **Cleanup on re-eval**: Clear and rebuild dependencies (dynamic dependency tracking)

From loupedeck's `computed.go`:

```go
func (c *Computed[T]) Get() T {
    c.rt.trackDependency(c)  // Register this computed as dependency of parent
    if c.dirty || !c.initialized {
        c.evaluate()
    }
    return c.value
}

func (c *Computed[T]) evaluate() {
    c.deps.clear(c)  // Clear old dependencies
    c.rt.withCollector(c, func() {
        c.value = c.fn()  // Rebuild dependency graph during execution
    })
    c.dirty = false
}
```

This ensures that even if both `left` and `right` read `base`, the dependency graph remains consistent and each computed only evaluates once per propagation.
