package dispatchlab

import (
	"testing"
	"time"
)

// TestSubmitCloseSerializeThroughMutex is a "scheduler-as-data" test: it
// uses the preDecision hook as a turnstile to force one specific
// interleaving deterministically, instead of hoping the scheduler produces
// it (cf. the heartbeat arbitration harness in SESSIONSTREAM-005).
//
// Forced schedule:
//
//	P1 enters TrySubmit critical section and blocks inside the hook
//	C  calls Close()                    -- must block on d.mu
//	(assert Close has not proceeded)
//	P1 is released; its admission linearizes BEFORE the close
//	C  completes; a later submit is rejected
//
// This is the Go-side counterpart of the TLA+ atomicity claim: the mutex
// makes the closing check + send one decision that cannot interleave with
// Close. The racy variant of this schedule is exactly the TLC counterexample
// in ../tla/results/unguarded.txt.
func TestSubmitCloseSerializeThroughMutex(t *testing.T) {
	invoked := &intSlice{}
	d, err := NewChecked[int](4, func(v int) { invoked.append(v) })
	if err != nil {
		t.Fatal(err)
	}

	inSection := make(chan struct{})
	release := make(chan struct{})
	var once bool
	d.setPreDecision(func() {
		if once {
			return
		}
		once = true
		close(inSection)
		<-release
	})

	producerDone := make(chan bool, 1)
	go func() {
		producerDone <- d.TrySubmit(1)
	}()

	<-inSection // producer now holds d.mu inside TrySubmit

	closeReturned := make(chan struct{})
	go func() {
		d.Close()
		close(closeReturned)
	}()

	// Close must not be able to linearize while the producer holds d.mu.
	select {
	case <-closeReturned:
		t.Fatal("Close proceeded while a producer held the admission mutex")
	case <-time.After(100 * time.Millisecond):
	}

	close(release)

	if !<-producerDone {
		t.Fatal("producer that held the mutex before Close must be accepted")
	}
	select {
	case <-closeReturned:
	case <-time.After(5 * time.Second):
		t.Fatal("Close did not return")
	}

	if d.TrySubmit(2) {
		t.Fatal("submit after completed Close must be rejected")
	}

	waitWithTimeout(t, d, 5*time.Second)
	if got := invoked.slice(); !equalInts(got, []int{1}) {
		t.Fatalf("delivered = %v, want [1]", got)
	}

	// The linearized log must show: accepted(1) -> close_effective -> rejected(2).
	m := replayTrace(t, d, 4)
	if !equalInts(m.admitted, []int{1}) {
		t.Fatalf("kernel: admitted = %v, want [1]", m.admitted)
	}
	kinds := make([]eventKind, 0, 3)
	for _, ev := range d.trace() {
		if ev.kind == evSubmitAccepted || ev.kind == evCloseEffective || ev.kind == evSubmitRejected {
			kinds = append(kinds, ev.kind)
		}
	}
	want := []eventKind{evSubmitAccepted, evCloseEffective, evSubmitRejected}
	if len(kinds) != len(want) {
		t.Fatalf("lifecycle events = %v, want %v", kinds, want)
	}
	for i := range want {
		if kinds[i] != want[i] {
			t.Fatalf("lifecycle events = %v, want %v", kinds, want)
		}
	}
}
