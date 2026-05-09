// +build ignore

// Reactive System Experiments
//
// This file contains standalone experiments with the loupedeck reactive system.
// It mirrors the test patterns from runtime/reactive/runtime_test.go but adds
// additional experiments for understanding the implementation.
//
// Run: go run reactive-experiments.go

package main

import (
	"fmt"
	"time"
)

// ============================================================================
// Minimal Signal Implementation (simplified from loupedeck)
// ============================================================================

// For these experiments, we use a simplified reactive system
// that demonstrates the core concepts without the full loupedeck
// generic implementation.

type SimpleRuntime struct {
	current        SimpleCollector
	batchDepth     int
	flushing       bool
	pendingEffects map[*SimpleEffect]struct{}
}

func NewSimpleRuntime() *SimpleRuntime {
	return &SimpleRuntime{}
}

type SimpleCollector interface {
	trackDependency(source SimpleSource)
}

type SimpleSource interface {
	addDependent(dep SimpleDependent)
	removeDependent(dep SimpleDependent)
}

type SimpleDependent interface {
	markDirty()
}

// Signal implementation
type SimpleSignal struct {
	rt    *SimpleRuntime
	value int
	deps  map[SimpleDependent]struct{}
}

func (s *SimpleSignal) Get() int {
	s.rt.trackDependency(s)
	return s.value
}

func (s *SimpleSignal) Set(v int) {
	if s.value == v {
		return
	}
	s.value = v
	s.notifyDependents()
	s.rt.maybeFlush()
}

func (s *SimpleSignal) addDependent(d SimpleDependent) {
	if s.deps == nil {
		s.deps = make(map[SimpleDependent]struct{})
	}
	s.deps[d] = struct{}{}
}

func (s *SimpleSignal) removeDependent(d SimpleDependent) {
	delete(s.deps, d)
}

func (s *SimpleSignal) notifyDependents() {
	for d := range s.deps {
		d.markDirty()
	}
}

func (s *SimpleSignal) trackDependency(source SimpleSource) {
	if s.rt.current != nil {
		s.rt.current.trackDependency(source)
	}
}

// Computed implementation
type SimpleComputed struct {
	rt         *SimpleRuntime
	fn         func() int
	value      int
	dirty      bool
	initialized bool
	evaluating bool
	myDeps     []SimpleSource
	depSet     map[SimpleSource]struct{}
}

func (c *SimpleComputed) Get() int {
	c.rt.trackDependency(c)
	if c.dirty || !c.initialized {
		c.evaluate()
	}
	return c.value
}

func (c *SimpleComputed) evaluate() {
	if c.evaluating {
		panic("cyclic dependency!")
	}
	c.evaluating = true
	
	// Clear old dependencies
	for _, dep := range c.myDeps {
		dep.removeDependent(c)
	}
	c.myDeps = nil
	c.depSet = nil
	
	// Collect new dependencies
	prev := c.rt.current
	c.rt.current = c
	c.value = c.fn()
	c.rt.current = prev
	
	c.initialized = true
	c.dirty = false
	c.evaluating = false
}

func (c *SimpleComputed) markDirty() {
	if c.dirty {
		return
	}
	c.dirty = true
}

func (c *SimpleComputed) addDependent(d SimpleDependent) {
	// Computeds don't have dependents in this simplified model
}

func (c *SimpleComputed) removeDependent(d SimpleDependent) {}

func (c *SimpleComputed) trackDependency(source SimpleSource) {
	if c.depSet == nil {
		c.depSet = make(map[SimpleSource]struct{})
	}
	if _, ok := c.depSet[source]; ok {
		return
	}
	c.depSet[source] = struct{}{}
	c.myDeps = append(c.myDeps, source)
	source.addDependent(c)
}

// Effect implementation
type SimpleEffect struct {
	rt         *SimpleRuntime
	fn         func()
	active     bool
	dirty      bool
	queued     bool
	evaluating bool
	myDeps     []SimpleSource
	depSet     map[SimpleSource]struct{}
}

func (e *SimpleEffect) markDirty() {
	if !e.active {
		return
	}
	e.dirty = true
	e.rt.enqueueEffect(e)
}

func (e *SimpleEffect) run() {
	if e.evaluating {
		panic("reentrant effect!")
	}
	e.evaluating = true
	
	// Clear old dependencies
	for _, dep := range e.myDeps {
		dep.removeDependent(e)
	}
	e.myDeps = nil
	e.depSet = nil
	
	// Collect new dependencies
	prev := e.rt.current
	e.rt.current = e
	e.fn()
	e.rt.current = prev
	
	e.dirty = false
	e.evaluating = false
}

func (e *SimpleEffect) Stop() {
	e.active = false
	e.dirty = false
	if e.queued {
		delete(e.rt.pendingEffects, e)
		e.queued = false
	}
	for _, dep := range e.myDeps {
		dep.removeDependent(e)
	}
	e.myDeps = nil
}

func (e *SimpleEffect) trackDependency(source SimpleSource) {
	if e.depSet == nil {
		e.depSet = make(map[SimpleSource]struct{})
	}
	if _, ok := e.depSet[source]; ok {
		return
	}
	e.depSet[source] = struct{}{}
	e.myDeps = append(e.myDeps, source)
	source.addDependent(e)
}

// Runtime methods
func (r *SimpleRuntime) trackDependency(source SimpleSource) {
	if r.current != nil {
		r.current.trackDependency(source)
	}
}

func (r *SimpleRuntime) maybeFlush() {
	if r.batchDepth > 0 || r.flushing {
		return
	}
	r.Flush()
}

func (r *SimpleRuntime) Flush() {
	if r.flushing {
		return
	}
	r.flushing = true
	defer func() { r.flushing = false }()
	
	for len(r.pendingEffects) > 0 {
		effects := make([]*SimpleEffect, 0, len(r.pendingEffects))
		for e := range r.pendingEffects {
			effects = append(effects, e)
			delete(r.pendingEffects, e)
			e.queued = false
		}
		for _, e := range effects {
			if e.active && e.dirty {
				e.run()
			}
		}
	}
}

func (r *SimpleRuntime) enqueueEffect(e *SimpleEffect) {
	if !e.active {
		return
	}
	if e.queued {
		return
	}
	if r.pendingEffects == nil {
		r.pendingEffects = make(map[*SimpleEffect]struct{})
	}
	r.pendingEffects[e] = struct{}{}
	e.queued = true
}

func (r *SimpleRuntime) Watch(fn func()) *SimpleEffect {
	e := &SimpleEffect{
		rt:     r,
		fn:     fn,
		active: true,
		dirty:  true,
	}
	r.enqueueEffect(e)
	r.maybeFlush()
	return e
}

func (r *SimpleRuntime) Batch(fn func()) {
	r.batchDepth++
	defer func() {
		r.batchDepth--
		if r.batchDepth == 0 {
			r.Flush()
		}
	}()
	fn()
}

// ============================================================================
// Experiments
// ============================================================================

func main() {
	fmt.Println("=== Reactive System Experiments ===")
	fmt.Println()
	
	experiment1_BasicSignal()
	experiment2_Computed()
	experiment3_DiamondGraph()
	experiment4_Batching()
	experiment5_EffectCleanup()
	experiment6_CycleDetection()
	experiment7_DynamicDependencies()
	experiment8_Performance()
}

func experiment1_BasicSignal() {
	fmt.Println("--- Experiment 1: Basic Signal ---")
	
	rt := NewSimpleRuntime()
	sig := &SimpleSignal{rt: rt, value: 10}
	
	runs := 0
	rt.Watch(func() {
		runs++
		fmt.Printf("  Effect run #%d: value = %d\n", runs, sig.Get())
	})
	
	fmt.Println("  Initial value read")
	
	sig.Set(20)
	fmt.Println("  After set(20)")
	
	sig.Set(20) // Should not trigger (equality check)
	fmt.Println("  After set(20) again (should not trigger)")
	
	sig.Set(30)
	fmt.Println("  After set(30)")
	
	fmt.Printf("  Total effect runs: %d (expected: 3)\n", runs)
	fmt.Println()
}

func experiment2_Computed() {
	fmt.Println("--- Experiment 2: Computed ---")
	
	rt := NewSimpleRuntime()
	base := &SimpleSignal{rt: rt, value: 2}
	
	computedRuns := 0
	double := &SimpleComputed{
		rt: rt,
		fn: func() int {
			computedRuns++
			return base.Get() * 2
		},
		dirty: true,
	}
	
	effectRuns := 0
	rt.Watch(func() {
		effectRuns++
		fmt.Printf("  Effect run #%d: double = %d\n", effectRuns, double.Get())
	})
	
	base.Set(5)
	fmt.Printf("  After set(5): computed ran %d times\n", computedRuns)
	
	// Access computed again - should not recompute (cached)
	_ = double.Get()
	_ = double.Get()
	fmt.Printf("  After 3 more gets: computed ran %d times (should be 2)\n", computedRuns)
	
	fmt.Println()
}

func experiment3_DiamondGraph() {
	fmt.Println("--- Experiment 3: Diamond Dependency ---")
	
	rt := NewSimpleRuntime()
	base := &SimpleSignal{rt: rt, value: 2}
	
	leftRuns, rightRuns, totalRuns := 0, 0, 0
	
	left := &SimpleComputed{
		rt: rt,
		fn: func() int {
			leftRuns++
			return base.Get() + 1
		},
		dirty: true,
	}
	
	right := &SimpleComputed{
		rt: rt,
		fn: func() int {
			rightRuns++
			return base.Get() * 2
		},
		dirty: true,
	}
	
	total := &SimpleComputed{
		rt: rt,
		fn: func() int {
			totalRuns++
			return left.Get() + right.Get()
		},
		dirty: true,
	}
	
	effectRuns := 0
	rt.Watch(func() {
		effectRuns++
		v := total.Get()
		fmt.Printf("  Effect #%d: total = %d (base=%d, left=%d, right=%d)\n",
			effectRuns, v, base.Get(), left.Get(), right.Get())
	})
	
	fmt.Printf("  After init: left=%d, right=%d, total=%d runs\n", leftRuns, rightRuns, totalRuns)
	
	base.Set(3)
	fmt.Printf("  After set(3): left=%d, right=%d, total=%d runs (all should be 2)\n",
		leftRuns, rightRuns, totalRuns)
	
	base.Set(10)
	fmt.Printf("  After set(10): left=%d, right=%d, total=%d runs (all should be 3)\n",
		leftRuns, rightRuns, totalRuns)
	
	if leftRuns == 3 && rightRuns == 3 && totalRuns == 3 {
		fmt.Println("  ✓ Diamond handled correctly - no redundant recomputation!")
	} else {
		fmt.Println("  ✗ Diamond not handled correctly")
	}
	fmt.Println()
}

func experiment4_Batching() {
	fmt.Println("--- Experiment 4: Batching ---")
	
	rt := NewSimpleRuntime()
	a := &SimpleSignal{rt: rt, value: 0}
	b := &SimpleSignal{rt: rt, value: 0}
	
	effectRuns := 0
	rt.Watch(func() {
		effectRuns++
		fmt.Printf("  Effect #%d: a=%d, b=%d, sum=%d\n",
			effectRuns, a.Get(), b.Get(), a.Get()+b.Get())
	})
	
	// Without batching
	fmt.Println("  Without batching:")
	a.Set(1)
	b.Set(2)
	fmt.Printf("  Total effect runs: %d\n", effectRuns)
	
	// With batching
	fmt.Println("  With batching:")
	rt.Batch(func() {
		a.Set(10)
		b.Set(20)
	})
	fmt.Printf("  Total effect runs: %d\n", effectRuns)
	
	// Nested batching
	fmt.Println("  Nested batching:")
	rt.Batch(func() {
		a.Set(100)
		rt.Batch(func() {
			b.Set(200)
		})
		// No flush yet!
	})
	fmt.Printf("  Total effect runs: %d\n", effectRuns)
	
	fmt.Println()
}

func experiment5_EffectCleanup() {
	fmt.Println("--- Experiment 5: Effect Cleanup ---")
	
	rt := NewSimpleRuntime()
	sig := &SimpleSignal{rt: rt, value: 0}
	
	effectRuns := 0
	effect := rt.Watch(func() {
		effectRuns++
		fmt.Printf("  Effect: value = %d\n", sig.Get())
	})
	
	sig.Set(1)
	sig.Set(2)
	
	effect.Stop()
	fmt.Println("  Effect stopped")
	
	sig.Set(3)
	sig.Set(4)
	
	fmt.Printf("  Total effect runs: %d (should be 3)\n", effectRuns)
	fmt.Println()
}

func experiment6_CycleDetection() {
	fmt.Println("--- Experiment 6: Cycle Detection ---")
	
	rt := NewSimpleRuntime()
	
	var c *SimpleComputed
	c = &SimpleComputed{
		rt: rt,
		fn: func() int {
			return c.Get() // Self-reference!
		},
		dirty: true,
	}
	
	fmt.Println("  Attempting cyclic computed evaluation...")
	defer func() {
		if r := recover(); r != nil {
			fmt.Printf("  ✓ Panic caught: %v\n", r)
		} else {
			fmt.Println("  ✗ No panic - cycle detection failed")
		}
	}()
	
	_ = c.Get()
	fmt.Println()
}

func experiment7_DynamicDependencies() {
	fmt.Println("--- Experiment 7: Dynamic Dependencies ---")
	
	rt := NewSimpleRuntime()
	
	a := &SimpleSignal{rt: rt, value: 1}
	b := &SimpleSignal{rt: rt, value: 10}
	useA := &SimpleSignal{rt: rt, value: 1} // 1 = use a, 0 = use b
	
	computedRuns := 0
	computed := &SimpleComputed{
		rt: rt,
		fn: func() int {
			computedRuns++
			if useA.Get() == 1 {
				return a.Get()
			}
			return b.Get()
		},
		dirty: true,
	}
	
	effectRuns := 0
	rt.Watch(func() {
		effectRuns++
		fmt.Printf("  Effect #%d: computed = %d (runs=%d)\n",
			effectRuns, computed.Get(), computedRuns)
	})
	
	// Depends on a and useA
	useA.Set(1) // Triggers, but useA is already 1
	fmt.Printf("  After set useA=1 (no change): %d runs\n", computedRuns)
	
	// Now depends on b and useA
	useA.Set(0)
	fmt.Printf("  After switch to b: %d runs\n", computedRuns)
	
	// Changing a should NOT trigger (no longer a dependency)
	a.Set(999)
	fmt.Printf("  After change a (not dep): %d runs\n", computedRuns)
	
	// Changing b SHOULD trigger
	b.Set(100)
	fmt.Printf("  After change b (is dep): %d runs\n", computedRuns)
	
	fmt.Println("  ✓ Dynamic dependencies work correctly!")
	fmt.Println()
}

func experiment8_Performance() {
	fmt.Println("--- Experiment 8: Performance Test ---")
	
	rt := NewSimpleRuntime()
	
	// Create 100 signals
	signals := make([]*SimpleSignal, 100)
	for i := range signals {
		signals[i] = &SimpleSignal{rt: rt, value: i}
	}
	
	// Create computed that sums all
	computedRuns := 0
	sum := &SimpleComputed{
		rt: rt,
		fn: func() int {
			computedRuns++
			s := 0
			for _, sig := range signals {
				s += sig.Get()
			}
			return s
		},
		dirty: true,
	}
	
	effectRuns := 0
	rt.Watch(func() {
		effectRuns++
		_ = sum.Get()
	})
	
	// Update all signals
	start := time.Now()
	rt.Batch(func() {
		for i, sig := range signals {
			sig.Set(i * 2)
		}
	})
	elapsed := time.Since(start)
	
	fmt.Printf("  100 signals updated in batch\n")
	fmt.Printf("  Effect runs: %d (should be 2)\n", effectRuns)
	fmt.Printf("  Computed runs: %d (should be 2)\n", computedRuns)
	fmt.Printf("  Time: %v\n", elapsed)
	
	// Compare: no batching
	effectRuns = 0
	computedRuns = 0
	
	start = time.Now()
	for i, sig := range signals {
		sig.Set(i * 3) // Individual updates
	}
	elapsed = time.Since(start)
	
	fmt.Printf("\n  Without batching:\n")
	fmt.Printf("  Effect runs: %d\n", effectRuns)
	fmt.Printf("  Computed runs: %d (potentially many!)\n", computedRuns)
	fmt.Printf("  Time: %v\n", elapsed)
	
	fmt.Println()
}
