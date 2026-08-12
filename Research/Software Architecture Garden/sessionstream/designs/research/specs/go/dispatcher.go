// Package dispatchlab is the verification scaffold for the Bounded
// Asynchronous Observer Dispatcher garden design
// ("01 - Bounded Asynchronous Observer Dispatcher").
//
// It is NOT the proposed production package. It exists so the formal models
// in ../tla, ../alloy, ../coq and ../lean can be exercised against a real Go
// binary using:
//
//   - linearization-point instrumentation (events.go),
//   - an executable oracle transliterated from the proved transition kernel
//     (model.go),
//   - deterministic, stress, and linearization tests (*_test.go),
//   - a state-aware native Go fuzzer (fuzz_test.go),
//   - mutation experiments demonstrating harness sensitivity (mutate.sh).
//
// The dispatcher itself is the reference implementation from the design doc,
// extended with two clearly marked test-only seams:
//
//   - log: every linearization point emits an event under d.mu, so an
//     execution trace is by construction a serialization the abstract
//     kernel can replay (see model.go for the legality argument);
//   - preDecision: an optional hook invoked inside the TrySubmit critical
//     section, used by the turnstile linearization test.
//
// Mutation markers (MUTATION-POINT: ...) anchor the sed-based mutation
// experiments in mutate.sh.
package dispatchlab

import (
	"fmt"
	"sync"
	"sync/atomic"
)

// Dispatcher is a bounded, single-worker, best-effort asynchronous callback
// dispatcher. Contract (design doc D1-D10):
//
//	D1  queue length never exceeds Capacity
//	D2  TrySubmit never waits for queue space or callback completion
//	D3  accepted values are offered in admission order
//	D4  capacity rejection increments a monotone drop counter
//	D5  one callback panic does not terminate later delivery
//	D6  Close is idempotent and serializes against TrySubmit
//	D7  TrySubmit after Close returns false without panic
//	D8  every accepted value is offered before worker exit
//	D9  Wait returns only after the worker exits
//	D10 exactly one callback worker
//
// TraceIdentity partitions model events from independent runs and dispatcher
// instances. Callers that persist or merge traces should provide stable IDs.
type TraceIdentity struct {
	RunID        string
	DispatcherID string
}

var checkedDispatcherSequence atomic.Uint64

type Dispatcher[T any] struct {
	deliver func(T)
	queue   chan T

	mu      sync.Mutex
	closing bool
	dropped uint64

	wg sync.WaitGroup

	// nonempty is the worker wakeup signal (buffered, signals coalesce).
	// It exists because the instrumented worker pops items under d.mu (see
	// run): when the queue is empty the worker sleeps on this signal
	// WITHOUT holding d.mu. Senders: every accepted TrySubmit, and Close.
	nonempty chan struct{}

	// Test-only seams (nil / nil in production use).
	log           *eventLog[T]
	nextOperation atomic.Uint64
	preDecision   func()
}

// New returns a dispatcher without instrumentation.
func New[T any](capacity int, deliver func(T)) (*Dispatcher[T], error) {
	return newDispatcher[T](capacity, deliver, false, TraceIdentity{})
}

// NewChecked returns a dispatcher with the linearization-point event log
// enabled. The trace can be retrieved with d.trace() and replayed against
// the abstract kernel with replayIntLog (for T = int).
func NewChecked[T any](capacity int, deliver func(T)) (*Dispatcher[T], error) {
	identity := TraceIdentity{
		RunID:        "local-process",
		DispatcherID: fmt.Sprintf("dispatcher-%d", checkedDispatcherSequence.Add(1)),
	}
	return newDispatcher[T](capacity, deliver, true, identity)
}

// NewCheckedWithIdentity enables model events using caller-supplied stable
// partition keys. Empty keys are rejected to prevent ambiguous merged traces.
func NewCheckedWithIdentity[T any](capacity int, deliver func(T), identity TraceIdentity) (*Dispatcher[T], error) {
	if identity.RunID == "" {
		return nil, fmt.Errorf("trace run ID is empty")
	}
	if identity.DispatcherID == "" {
		return nil, fmt.Errorf("trace dispatcher ID is empty")
	}
	return newDispatcher[T](capacity, deliver, true, identity)
}

func newDispatcher[T any](capacity int, deliver func(T), checked bool, identity TraceIdentity) (*Dispatcher[T], error) {
	if capacity <= 0 {
		return nil, fmt.Errorf("dispatcher capacity must be positive")
	}
	if deliver == nil {
		return nil, fmt.Errorf("dispatcher delivery function is nil")
	}

	d := &Dispatcher[T]{
		deliver:  deliver,
		queue:    make(chan T, capacity),
		nonempty: make(chan struct{}, 1),
	}
	if checked {
		d.log = &eventLog[T]{runID: identity.RunID, dispatcherID: identity.DispatcherID}
	}
	d.wg.Add(1)
	go d.run()
	return d, nil
}

// TrySubmit attempts to admit item without blocking.
//
// The closing check and the nonblocking send form one decision under d.mu;
// that mutex is what makes this decision atomic with respect to Close (the
// TLA+ SubmitBody action). emitLocked runs at the linearization point.
func (d *Dispatcher[T]) TrySubmit(item T) bool {
	if d == nil {
		return false
	}

	operationID := d.beginOperation("try_submit")
	defer d.endOperation(operationID, "try_submit")
	d.mu.Lock()
	defer d.mu.Unlock()

	if d.preDecision != nil {
		d.preDecision()
	}

	// MUTATION-POINT: closing-guard
	if d.closing {
		d.emitLocked(evSubmitRejected, operationID, "try_submit", item, true)
		return false
	}

	select {
	case d.queue <- item:
		d.emitLocked(evSubmitAccepted, operationID, "try_submit", item, true)
		select {
		case d.nonempty <- struct{}{}:
		default:
		}
		return true
	default:
		d.dropped++ // MUTATION-POINT: drop-accounting
		d.emitLocked(evSubmitDropped, operationID, "try_submit", item, true)
		return false
	}
}

// Close terminates admission and lets the worker drain accepted items.
// The state change and the channel close form one decision under d.mu (the
// TLA+ CloseBody action).
func (d *Dispatcher[T]) Close() {
	if d == nil {
		return
	}

	operationID := d.beginOperation("close")
	defer d.endOperation(operationID, "close")
	d.mu.Lock()
	defer d.mu.Unlock()

	// MUTATION-POINT: close-idempotence
	if d.closing {
		d.emitLocked(evCloseNoop, operationID, "close", *new(T), false)
		return
	}
	d.closing = true
	close(d.queue)
	d.emitLocked(evCloseEffective, operationID, "close", *new(T), false)
	select {
	case d.nonempty <- struct{}{}:
	default:
	}
}

// Wait joins the delivery worker.
func (d *Dispatcher[T]) Wait() {
	if d == nil {
		return
	}
	operationID := d.beginOperation("wait")
	defer d.endOperation(operationID, "wait")
	d.wg.Wait()
	d.emitMu(evWaitReturned, operationID, "wait", *new(T), false)
}

// Dropped reports how many submissions were rejected because the bounded
// queue was full. Post-close rejections are lifecycle rejections and are
// not counted here (design doc: drop accounting).
func (d *Dispatcher[T]) Dropped() uint64 {
	if d == nil {
		return 0
	}
	d.mu.Lock()
	defer d.mu.Unlock()
	return d.dropped
}

// run is the single delivery worker (D10).
//
// Instrumentation note: the design's reference implementation uses
// `for item := range d.queue`. That loop pops items WITHOUT holding d.mu,
// so a pop can interpose between a producer's send and its (mutex-held)
// event emission; the recorded log would then order submit_accepted before
// the receive that freed its slot, which the abstract kernel cannot replay
// (receive is a legal step only before the submit decision that depends on
// it). The two-phase loop below is behaviorally equivalent but pops items
// UNDER d.mu, so receive linearizes atomically with the pop:
//
//	queue nonempty  -> pop + emit under d.mu, then deliver outside d.mu
//	queue empty     -> sleep on d.nonempty WITHOUT holding d.mu
//	closed + drained-> emit exit under d.mu and return
func (d *Dispatcher[T]) run() {
	defer d.wg.Done()
	for {
		d.mu.Lock()
		select {
		case item, ok := <-d.queue:
			if !ok {
				// Closed and drained (D8).
				operationID := d.beginOperation("worker_exit")
				d.emitLocked(evWorkerExit, operationID, "worker_exit", *new(T), false)
				d.endOperation(operationID, "worker_exit")
				d.mu.Unlock()
				return
			}
			operationID := d.beginOperation("delivery")
			d.emitLocked(evReceive, operationID, "delivery", item, true)
			d.mu.Unlock()
			d.deliverSafe(operationID, item)
		default:
			d.mu.Unlock()
			<-d.nonempty
		}
	}
}

// deliverSafe invokes the callback with per-call panic isolation (D5).
func (d *Dispatcher[T]) deliverSafe(operationID string, item T) {
	defer d.endOperation(operationID, "delivery")
	defer func() {
		// MUTATION-POINT: panic-recovery
		if r := recover(); r != nil {
			d.emitMu(evPanic, operationID, "delivery", item, true)
		}
	}()
	d.deliver(item) // MUTATION-POINT: delivery
	d.emitMu(evOffered, operationID, "delivery", item, true)
}

// emitLocked records an event. The caller must hold d.mu, which makes the
// recorded order a true linearization of the execution (see model.go).
func (d *Dispatcher[T]) emitLocked(kind eventKind, operationID, operation string, value T, hasValue bool) {
	if d.log == nil {
		return
	}
	d.log.emit(event[T]{
		kind:        kind,
		operationID: operationID,
		operation:   operation,
		value:       value,
		hasValue:    hasValue,
		queueLen:    len(d.queue),
		dropped:     d.dropped,
	})
}

// emitMu records an event, acquiring d.mu first (worker-side events).
func (d *Dispatcher[T]) emitMu(kind eventKind, operationID, operation string, value T, hasValue bool) {
	d.mu.Lock()
	d.emitLocked(kind, operationID, operation, value, hasValue)
	d.mu.Unlock()
}

// trace returns a copy of the recorded linearization-point events.
func (d *Dispatcher[T]) trace() []event[T] {
	if d.log == nil {
		return nil
	}
	d.log.mu.Lock()
	defer d.log.mu.Unlock()
	out := make([]event[T], len(d.log.events))
	copy(out, d.log.events)
	return out
}

// ModelTrace returns a versioned, serializable copy of the model-event stream.
// NewChecked enables this stream; an uninstrumented dispatcher returns nil.
func (d *Dispatcher[T]) ModelTrace() []ModelEvent[T] {
	if d == nil || d.log == nil {
		return nil
	}
	return d.log.modelEvents()
}

// OperationIntervals returns invocation/linearization/return events. The
// sequence is independent of ModelTrace.Sequence; OperationID links streams.
func (d *Dispatcher[T]) OperationIntervals() []OperationIntervalEvent {
	if d == nil || d.log == nil {
		return nil
	}
	return d.log.operationIntervals()
}

func (d *Dispatcher[T]) beginOperation(operation string) string {
	if d.log == nil {
		return ""
	}
	operationID := fmt.Sprintf("op-%d", d.nextOperation.Add(1))
	d.log.emitInterval(operationID, operation, "invoke", "")
	return operationID
}

func (d *Dispatcher[T]) endOperation(operationID, operation string) {
	if d.log == nil {
		return
	}
	d.log.emitInterval(operationID, operation, "return", "")
}

// setPreDecision installs the critical-section hook used by the turnstile
// linearization test. Test-only seam.
func (d *Dispatcher[T]) setPreDecision(f func()) {
	d.preDecision = f
}
