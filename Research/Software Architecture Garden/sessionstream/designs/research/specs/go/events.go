package dispatchlab

import "sync"

// eventKind enumerates the dispatcher's linearization points. Every event is
// emitted under d.mu, so the recorded log is a serialization of the
// execution that the abstract kernel (model.go) can replay step by step.
type eventKind string

const (
	evSubmitAccepted eventKind = "submit_accepted" // admitted to the queue
	evSubmitDropped  eventKind = "submit_dropped"  // overflow rejection (counted)
	evSubmitRejected eventKind = "submit_rejected" // post-close rejection
	evCloseEffective eventKind = "close_effective" // closing flipped, queue closed
	evCloseNoop      eventKind = "close_noop"      // idempotent repeated close
	evReceive        eventKind = "receive"         // worker dequeued an item
	evOffered        eventKind = "offered"         // callback returned
	evPanic          eventKind = "panic_recovered" // callback panicked, recovered
	evWorkerExit     eventKind = "worker_exit"     // range over closed queue ended
	evWaitReturned   eventKind = "wait_returned"   // wg.Wait() returned
)

// event is one linearization-point record. queueLen and dropped are the
// dispatcher's state at the linearization point (read under d.mu); the model
// replay cross-checks them against its own state, so a divergence between
// the implementation and the kernel shows up as a replay error.
type event[T any] struct {
	kind     eventKind
	value    T
	hasValue bool
	queueLen int
	dropped  uint64
}

// eventLog is an append-only event recorder. All appends happen under d.mu
// (lock order d.mu -> log.mu, never the reverse), so the slice order equals
// the linearization order. log.mu only protects readers (trace()).
type eventLog[T any] struct {
	mu     sync.Mutex
	events []event[T]
}

func (l *eventLog[T]) emit(e event[T]) {
	if l == nil {
		return
	}
	l.mu.Lock()
	l.events = append(l.events, e)
	l.mu.Unlock()
}
