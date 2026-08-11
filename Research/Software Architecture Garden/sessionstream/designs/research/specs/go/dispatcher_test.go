package dispatchlab

import (
	"sync"
	"sync/atomic"
	"testing"
	"time"
)

// The deterministic tests below implement the design doc's "Testing
// obligations" section. Every test also replays the execution trace through
// the abstract kernel (model.go), so each test validates the same execution
// twice: once semantically (Go assertions) and once against the proved
// transition relation.

// D3: accepted values are delivered in admission order.
func TestDeliveredInAdmissionOrder(t *testing.T) {
	invoked := &intSlice{}
	const n = 100
	d, err := NewChecked[int](128, func(v int) { invoked.append(v) })
	if err != nil {
		t.Fatal(err)
	}
	for i := 0; i < n; i++ {
		if !d.TrySubmit(i) {
			t.Fatalf("submit %d unexpectedly rejected/dropped", i)
		}
	}
	d.Close()
	waitWithTimeout(t, d, 5*time.Second)

	got := invoked.slice()
	want := make([]int, n)
	for i := range want {
		want[i] = i
	}
	if !equalInts(got, want) {
		t.Fatalf("delivery order = %v, want %v", got, want)
	}
	m := replayTrace(t, d, 128)
	if !equalInts(m.offered, m.admitted) {
		t.Fatalf("kernel: offered %v != admitted %v", m.offered, m.admitted)
	}
}

// D1 + D4 + "N queued + 1 active": with a blocked callback, the queue fills
// to capacity, the next submit is rejected and counted, and the in-flight
// item plus the queued items are exactly capacity+1 retained items.
func TestFullQueueDropsAndCounts(t *testing.T) {
	const capacity = 4
	g := newGate()
	g.block()
	invoked := &intSlice{}
	d, err := NewChecked[int](capacity, func(v int) {
		invoked.append(v)
		g.wait()
	})
	if err != nil {
		t.Fatal(err)
	}

	// First item is picked up by the worker and blocks inside the callback.
	if !d.TrySubmit(0) {
		t.Fatal("first submit not accepted")
	}
	// Wait until the worker actually received it (queue is now empty again).
	waitForEvent(t, d, evReceive, 5*time.Second)

	// Fill the queue to capacity.
	for i := 1; i <= capacity; i++ {
		if !d.TrySubmit(i) {
			t.Fatalf("submit %d should have been accepted into the queue", i)
		}
	}
	// Queue full + one in flight: the next submit must be rejected+counted.
	if d.TrySubmit(99) {
		t.Fatal("submit beyond capacity should have been dropped")
	}
	if got := d.Dropped(); got != 1 {
		t.Fatalf("Dropped() = %d, want 1", got)
	}

	g.release()
	d.Close()
	waitWithTimeout(t, d, 5*time.Second)

	want := []int{0, 1, 2, 3, 4}
	if got := invoked.slice(); !equalInts(got, want) {
		t.Fatalf("delivered = %v, want %v", got, want)
	}
	m := replayTrace(t, d, capacity)
	if m.dropped != 1 {
		t.Fatalf("kernel: dropped = %d, want 1", m.dropped)
	}
}

// D8: closing drains every accepted value before the worker exits.
func TestCloseDrainsAccepted(t *testing.T) {
	invoked := &intSlice{}
	d, _ := NewChecked[int](64, func(v int) { invoked.append(v) })
	for i := 0; i < 50; i++ {
		d.TrySubmit(i)
	}
	d.Close()
	waitWithTimeout(t, d, 5*time.Second)
	if got := len(invoked.slice()); got != 50 {
		t.Fatalf("delivered %d items, want all 50 drained", got)
	}
	m := replayTrace(t, d, 64)
	if !m.exited {
		t.Fatal("kernel: worker did not exit")
	}
	if !equalInts(m.offered, m.admitted) {
		t.Fatal("kernel: worker exited before offering all admitted items")
	}
}

// D7: submit after close returns false (and is a lifecycle rejection, not a
// capacity drop).
func TestSubmitAfterCloseReturnsFalse(t *testing.T) {
	d, _ := NewChecked[int](4, func(v int) {})
	d.TrySubmit(1)
	d.Close()
	if d.TrySubmit(2) {
		t.Fatal("submit after close returned true")
	}
	if got := d.Dropped(); got != 0 {
		t.Fatalf("post-close rejection counted as capacity drop: %d", got)
	}
	waitWithTimeout(t, d, 5*time.Second)
	replayTrace(t, d, 4)
}

// D6: repeated close is harmless.
func TestRepeatedCloseHarmless(t *testing.T) {
	invoked := &intSlice{}
	d, _ := NewChecked[int](4, func(v int) { invoked.append(v) })
	d.TrySubmit(1)
	d.Close()
	d.Close()
	d.Close()
	waitWithTimeout(t, d, 5*time.Second)
	if got := invoked.slice(); !equalInts(got, []int{1}) {
		t.Fatalf("delivered = %v, want [1]", got)
}
	replayTrace(t, d, 4)
}

// D5: one panic does not terminate later delivery.
func TestPanicDoesNotStopDelivery(t *testing.T) {
	invoked := &intSlice{}
	d, _ := NewChecked[int](8, func(v int) {
		invoked.append(v)
		if v == 2 {
			panic("boom")
		}
	})
	for i := 0; i < 6; i++ {
		d.TrySubmit(i)
	}
	d.Close()
	waitWithTimeout(t, d, 5*time.Second)
	want := []int{0, 1, 2, 3, 4, 5}
	if got := invoked.slice(); !equalInts(got, want) {
		t.Fatalf("delivered = %v, want %v (panic must not stop delivery)", got, want)
	}
	replayTrace(t, d, 8)
}

// D9: Wait blocks while a callback is blocked; bounded queue does not imply
// bounded close latency.
func TestWaitBlocksWhileCallbackBlocked(t *testing.T) {
	g := newGate()
	g.block()
	d, _ := NewChecked[int](4, func(v int) { g.wait() })
	d.TrySubmit(1)

	waitReturned := make(chan struct{})
	go func() {
		d.Wait()
		close(waitReturned)
	}()
	d.Close()

	select {
	case <-waitReturned:
		t.Fatal("Wait returned while the callback was still blocked")
	case <-time.After(100 * time.Millisecond):
		// expected: Wait still blocked; one in-flight callback holds the worker
	}

	g.release()
	select {
	case <-waitReturned:
	case <-time.After(5 * time.Second):
		t.Fatal("Wait did not return after the callback was released")
	}
	replayTrace(t, d, 4)
}

// D9/D8: Wait returns after release and full drain.
func TestWaitReturnsAfterReleaseAndDrain(t *testing.T) {
	g := newGate()
	g.block()
	invoked := &intSlice{}
	d, _ := NewChecked[int](4, func(v int) {
		invoked.append(v)
		g.wait()
	})
	for i := 0; i < 3; i++ {
		d.TrySubmit(i)
	}
	waitForEvent(t, d, evReceive, 5*time.Second)
	d.Close()
	g.release()
	waitWithTimeout(t, d, 5*time.Second)
	want := []int{0, 1, 2}
	if got := invoked.slice(); !equalInts(got, want) {
		t.Fatalf("delivered = %v, want %v", got, want)
	}
	replayTrace(t, d, 4)
}

// D1/D8 boundary: the final queue slot is delivered (capacity-1 index).
func TestFinalQueueSlotDelivered(t *testing.T) {
	g := newGate()
	g.block()
	invoked := &intSlice{}
	const capacity = 3
	d, _ := NewChecked[int](capacity, func(v int) {
		invoked.append(v)
		g.wait()
	})
	// one in flight + exactly capacity queued, no drops
	d.TrySubmit(0)
	waitForEvent(t, d, evReceive, 5*time.Second)
	for i := 1; i <= capacity; i++ {
		if !d.TrySubmit(i) {
			t.Fatalf("submit %d should fit", i)
		}
	}
	if got := d.Dropped(); got != 0 {
		t.Fatalf("unexpected drop: %d", got)
	}
	g.release()
	d.Close()
	waitWithTimeout(t, d, 5*time.Second)
	want := []int{0, 1, 2, 3}
	if got := invoked.slice(); !equalInts(got, want) {
		t.Fatalf("delivered = %v, want %v", got, want)
	}
	replayTrace(t, d, capacity)
}

// Concurrency contract (design doc): many producers race with close under
// -race; afterwards accepted == delivered, and nothing is accepted after
// the close linearization point.
func TestConcurrentProducersAndClose(t *testing.T) {
	const capacity = 8
	invoked := &intSlice{}
	d, _ := NewChecked[int](capacity, func(v int) {
		invoked.append(v)
		if v%1017 == 0 && v != 0 {
			panic("occasional panic")
		}
	})

	var accepted atomic.Int64
	var producers sync.WaitGroup
	for p := 0; p < 8; p++ {
		producers.Add(1)
		go func(p int) {
			defer producers.Done()
			for i := 0; i < 400; i++ {
				if d.TrySubmit(p*1000 + i) {
					accepted.Add(1)
				}
			}
		}(p)
	}

	time.Sleep(2 * time.Millisecond) // let some submissions land before close
	d.Close()
	d.Close() // idempotence under concurrency
	producers.Wait()
	waitWithTimeout(t, d, 10*time.Second)

	m := replayTrace(t, d, capacity)

	if got := int(accepted.Load()); got != len(m.admitted) {
		t.Fatalf("accepted = %d, kernel admitted = %d", got, len(m.admitted))
	}
	if got := invoked.slice(); !equalInts(got, m.admitted) {
		t.Fatalf("delivered %d items != admitted %d items (D3/D8)", len(got), len(m.admitted))
	}

	// Post-close acceptance must be zero (D7): scan the linearized log.
	seenClose := false
	for _, ev := range d.trace() {
		if ev.kind == evCloseEffective {
			seenClose = true
		}
		if seenClose && ev.kind == evSubmitAccepted {
			t.Fatal("an item was accepted after the close linearization point")
		}
	}
}

// Oracle self-check: the trace checker must reject fabricated violations.
// This is the sensitivity evidence that model.go is not vacuous.
func TestModelRejectsFabricatedTraces(t *testing.T) {
	ok := []event[int]{
		{kind: evSubmitAccepted, value: 1, hasValue: true, queueLen: 1},
		{kind: evSubmitAccepted, value: 2, hasValue: true, queueLen: 2},
		{kind: evReceive, value: 1, hasValue: true, queueLen: 1},
		{kind: evOffered, value: 1, hasValue: true, queueLen: 1},
		{kind: evCloseEffective, queueLen: 1},
		{kind: evReceive, value: 2, hasValue: true, queueLen: 0},
		{kind: evPanic, value: 2, hasValue: true, queueLen: 0},
		{kind: evWorkerExit, queueLen: 0},
		{kind: evWaitReturned, queueLen: 0},
	}
	if _, err := replayIntLog(ok, 4); err != nil {
		t.Fatalf("valid trace rejected: %v", err)
	}

	bad := []struct {
		name   string
		events []event[int]
	}{
		{"accept while closing", []event[int]{
			{kind: evCloseEffective, queueLen: 0},
			{kind: evSubmitAccepted, value: 1, hasValue: true, queueLen: 1},
		}},
		{"accept over capacity", []event[int]{
			{kind: evSubmitAccepted, value: 1, hasValue: true, queueLen: 1},
			{kind: evSubmitAccepted, value: 2, hasValue: true, queueLen: 2},
			{kind: evSubmitAccepted, value: 3, hasValue: true, queueLen: 3},
		}},
		{"offer without receive", []event[int]{
			{kind: evOffered, value: 1, hasValue: true, queueLen: 0},
		}},
		{"exit with undrained items", []event[int]{
			{kind: evSubmitAccepted, value: 1, hasValue: true, queueLen: 1},
			{kind: evCloseEffective, queueLen: 1},
			{kind: evWorkerExit, queueLen: 1},
		}},
		{"wait before exit", []event[int]{
			{kind: evWaitReturned, queueLen: 0},
		}},
		{"drop while not full", []event[int]{
			{kind: evSubmitDropped, value: 1, hasValue: true, queueLen: 0, dropped: 1},
		}},
		{"double effective close", []event[int]{
			{kind: evCloseEffective, queueLen: 0},
			{kind: evCloseEffective, queueLen: 0},
		}},
		{"queue length evidence mismatch", []event[int]{
			{kind: evSubmitAccepted, value: 1, hasValue: true, queueLen: 2},
		}},
	}
	for _, tc := range bad {
		t.Run(tc.name, func(t *testing.T) {
			if _, err := replayIntLog(tc.events, 2); err == nil {
				t.Fatalf("fabricated trace %q was NOT rejected", tc.name)
			}
		})
	}
}

// waitForEvent polls the trace until an event kind appears (worker progress
// synchronization without sleeps).
func waitForEvent(t *testing.T, d *Dispatcher[int], kind eventKind, timeout time.Duration) {
	t.Helper()
	deadline := time.Now().Add(timeout)
	for time.Now().Before(deadline) {
		for _, ev := range d.trace() {
			if ev.kind == kind {
				return
			}
		}
		time.Sleep(time.Millisecond)
	}
	t.Fatalf("event %s not observed within %s", kind, timeout)
}
