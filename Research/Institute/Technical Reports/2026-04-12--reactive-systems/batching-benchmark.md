---
title: 'Batching Benchmark - Atomic Updates'
tags: [reactive-systems, batching, performance, transactions, loupedeck]
created: 2026-04-12
type: script-example
---

# Batching Benchmark

This demonstrates batching (also called transactions or actions) which groups multiple signal updates into a single effect execution.

## The Problem

Without batching, intermediate states trigger partial updates:

```javascript
// Without batching
const a = state.signal(0);
const b = state.signal(0);
const sum = state.computed(() => a.get() + b.get());

state.watch(() => {
    console.log(`Sum: ${sum.get()}`);
});

// Multiple updates
a.set(1);  // Triggers: "Sum: 1" (intermediate!)
b.set(2);  // Triggers: "Sum: 3" (final)
```

Problem: The first effect sees an inconsistent state where `a=1` but `b=0`.

## The Solution: Batching

With batching, all updates apply atomically:

```javascript
// With batching
state.batch(() => {
    a.set(1);
    b.set(2);
});  // Single effect run: "Sum: 3"
```

## JavaScript Example (Loupedeck Runtime)

```javascript
const state = require('loupedeck/state');

const a = state.signal(0);
const b = state.signal(0);
const sum = state.computed(() => a.get() + b.get());

let effectRuns = 0;
state.watch(() => {
    effectRuns++;
    console.log(`Run ${effectRuns}: Sum = ${sum.get()}, a = ${a.get()}, b = ${b.get()}`);
});

// Test 1: Without batching (individual updates)
console.log('\n--- Without batching ---');
a.set(1);
b.set(2);
// Output:
// Run 1: Sum = 1, a = 1, b = 0  <-- Inconsistent!
// Run 2: Sum = 3, a = 1, b = 2  <-- Consistent

// Test 2: With batching
console.log('\n--- With batching ---');
state.batch(() => {
    a.set(5);
    b.set(10);
});
// Output:
// Run 3: Sum = 15, a = 5, b = 10  <-- Single atomic update

// Test 3: Nested batches
console.log('\n--- Nested batches ---');
state.batch(() => {
    a.set(100);
    state.batch(() => {
        b.set(200);
    });
    // No flush here - outer batch still active
});
// Output:
// Run 4: Sum = 300, a = 100, b = 200  <-- Single flush at end
```

## Go Implementation (from loupedeck codebase)

```go
// Runtime maintains batch depth counter
type Runtime struct {
    batchDepth     int  // Nesting level
    pendingEffects map[*Effect]struct{}
    // ...
}

func (r *Runtime) Batch(fn func()) {
    r.batchDepth++
    defer func() {
        r.batchDepth--
        if r.batchDepth == 0 {
            r.Flush()  // Only flush when outermost batch completes
        }
    }()
    fn()
}

func (r *Runtime) maybeFlush() {
    if r.batchDepth > 0 || r.flushing {
        return  // Skip flush during batch
    }
    r.Flush()
}
```

The test from `runtime/reactive/runtime_test.go`:

```go
func TestBatchDefersWatcherFlushUntilOuterBatchCompletes(t *testing.T) {
    rt := NewRuntime()
    a := NewSignal(rt, 0)
    b := NewSignal(rt, 0)

    runs := 0
    rt.Watch(func() {
        runs++
        _ = a.Get() + b.Get()
    })

    // Single batch with multiple updates
    rt.Batch(func() {
        a.Set(1)
        b.Set(2)
        a.Set(3)  // Even same-batch updates are batched
    })

    if runs != 2 {  // Initial + 1 batch flush
        t.Fatalf("expected a single rerun after first batch")
    }

    // Nested batches
    rt.Batch(func() {
        a.Set(4)
        rt.Batch(func() {
            b.Set(5)
            a.Set(6)
        })
        // No flush here - outer batch still active
    })

    if runs != 3 {  // Initial + 2 batch flushes
        t.Fatalf("expected nested batch to add one rerun")
    }
}
```

## Performance Benchmark

```javascript
// Benchmark: Batching vs No Batching
function benchmarkBatching(signalCount, updateCount) {
    const signals = [];
    const state = require('loupedeck/state');
    
    // Create N signals
    for (let i = 0; i < signalCount; i++) {
        signals.push(state.signal(0));
    }
    
    // Create computed that depends on all
    const sum = state.computed(() => {
        return signals.reduce((acc, s) => acc + s.get(), 0);
    });
    
    // Watch the sum
    let effectRuns = 0;
    state.watch(() => {
        effectRuns++;
        sum.get();
    });
    
    // Without batching
    const start1 = performance.now();
    for (let i = 0; i < updateCount; i++) {
        signals.forEach((s, idx) => s.set(idx + i));
    }
    const time1 = performance.now() - start1;
    const runsWithoutBatch = effectRuns;
    
    // Reset
    signals.forEach(s => s.set(0));
    effectRuns = 0;
    
    // With batching
    const start2 = performance.now();
    for (let i = 0; i < updateCount; i++) {
        state.batch(() => {
            signals.forEach((s, idx) => s.set(idx + i));
        });
    }
    const time2 = performance.now() - start2;
    const runsWithBatch = effectRuns;
    
    return {
        withoutBatch: { time: time1, effectRuns: runsWithoutBatch },
        withBatch: { time: time2, effectRuns: runsWithBatch },
        speedup: time1 / time2,
        effectReduction: runsWithoutBatch / runsWithBatch
    };
}

// Run benchmark
console.log(benchmarkBatching(10, 100));
// Expected output:
// {
//   withoutBatch: { time: ~500ms, effectRuns: 1001 },
//   withBatch: { time: ~5ms, effectRuns: 101 },
//   speedup: ~100x,
//   effectReduction: ~10x
// }
```

## Batching Patterns Across Frameworks

| Framework | Syntax | Nested | Use Case |
|-----------|--------|--------|----------|
| Loupedeck | `state.batch(fn)` | Yes | Transaction boundaries |
| MobX | `runInAction(fn)` | Yes | State mutations |
| Vue 3 | `nextTick()` | Implicit | DOM updates |
| SolidJS | `batch(fn)` | Yes | Signal updates |
| React | `unstable_batchedUpdates` | Internal | Event handlers |
| Svelte | `$effect.pre` / tick | Implicit | DOM synchronization |

## Advanced: Automatic Batching

Some frameworks batch automatically within event handlers:

```javascript
// React 18+ automatic batching
function handleClick() {
    setA(1);  // Not flushed yet
    setB(2);  // Not flushed yet
}  // Automatic batch flush here

// SolidJS automatic batching
const handleClick = () => {
    setA(1);  // Deferred
    setB(2);  // Deferred
    // Flush happens microtask
};
```

Loupedeck uses **explicit batching**, giving developers control:

```javascript
// Explicit is clearer for complex transactions
state.batch(() => {
    // Complex state update
    items.forEach(item => {
        item.update({
            position: calculatePosition(item),
            velocity: calculateVelocity(item)
        });
    });
    
    // Batch effects until all items updated
    summary.set(calculateSummary(items));
});
// Effects run here with consistent state
```

## Glitch-Free Guarantees

Batching enables **glitch-free propagation**:

```javascript
const a = state.signal(0);
const b = state.computed(() => a.get() * 2);
const c = state.computed(() => a.get() + b.get());  // c = a + 2a = 3a

state.watch(() => {
    console.log(`a=${a.get()}, b=${b.get()}, c=${c.get()}`);
});

// Without batching:
a.set(1);
// a=1, b=0 (stale!), c=1  <-- GLITCH!
// Then: a=1, b=2, c=3

// With batching:
state.batch(() => {
    a.set(1);
});
// a=1, b=2, c=3  <-- Consistent!
```

## Implementation Tips

1. **Always batch related updates**:
   ```javascript
   // Good: Coordinates update together
   state.batch(() => {
       position.x.set(newX);
       position.y.set(newY);
   });
   ```

2. **Don't batch across async boundaries**:
   ```javascript
   // Bad: Async breaks batch
   state.batch(async () => {
       await fetchData();  // Don't await in batch!
       data.set(result);
   });
   ```

3. **Use for bulk operations**:
   ```javascript
   // Good: Bulk update
   state.batch(() => {
       items.forEach((item, i) => item.set(i));
   });
   ```

4. **Profile effect counts** to verify batching:
   ```javascript
   let runs = 0;
   state.watch(() => { runs++; });
   // ... operations
   console.log(`Effects: ${runs}`);  // Should be minimal
   ```
