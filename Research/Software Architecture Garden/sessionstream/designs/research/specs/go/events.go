package dispatchlab

import "sync"

const ModelEventSchemaVersion = 1

// ModelEvent is the stable, serializable projection of an internal
// linearization-point event. It is intentionally smaller than a diagnostic
// log: a trace validator consumes action plus abstract-state evidence.
type ModelEvent[T any] struct {
	SchemaVersion int    `json:"schema_version"`
	RunID         string `json:"run_id"`
	DispatcherID  string `json:"dispatcher_id"`
	Sequence      uint64 `json:"sequence"`
	OperationID   string `json:"operation_id"`
	Operation     string `json:"operation"`
	Action        string `json:"action"`
	Value         T      `json:"value,omitempty"`
	HasValue      bool   `json:"has_value"`
	QueueLen      int    `json:"queue_len"`
	Dropped       uint64 `json:"dropped"`
}

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
	kind        eventKind
	operationID string
	operation   string
	value       T
	hasValue    bool
	queueLen    int
	dropped     uint64
}

// eventLog is an append-only event recorder. All appends happen under d.mu
// (lock order d.mu -> log.mu, never the reverse), so the slice order equals
// the linearization order. log.mu only protects readers (trace()).
// OperationIntervalEvent records invocation, linearization, and return in one
// per-dispatcher sequence. Events sharing OperationID define one operation
// interval; ModelEvent.OperationID links the abstract transition to it.
type OperationIntervalEvent struct {
	SchemaVersion int    `json:"schema_version"`
	RunID         string `json:"run_id"`
	DispatcherID  string `json:"dispatcher_id"`
	Sequence      uint64 `json:"sequence"`
	OperationID   string `json:"operation_id"`
	Operation     string `json:"operation"`
	Phase         string `json:"phase"`
	Action        string `json:"action,omitempty"`
}

type eventLog[T any] struct {
	mu               sync.Mutex
	runID            string
	dispatcherID     string
	events           []event[T]
	intervalEvents   []OperationIntervalEvent
	intervalSequence uint64
}

func (l *eventLog[T]) emit(e event[T]) {
	if l == nil {
		return
	}
	l.mu.Lock()
	l.events = append(l.events, e)
	l.emitIntervalLocked(e.operationID, e.operation, "linearize", string(e.kind))
	l.mu.Unlock()
}

func (l *eventLog[T]) emitInterval(operationID, operation, phase, action string) {
	if l == nil {
		return
	}
	l.mu.Lock()
	l.emitIntervalLocked(operationID, operation, phase, action)
	l.mu.Unlock()
}

func (l *eventLog[T]) emitIntervalLocked(operationID, operation, phase, action string) {
	l.intervalSequence++
	l.intervalEvents = append(l.intervalEvents, OperationIntervalEvent{
		SchemaVersion: ModelEventSchemaVersion,
		RunID:         l.runID,
		DispatcherID:  l.dispatcherID,
		Sequence:      l.intervalSequence,
		OperationID:   operationID,
		Operation:     operation,
		Phase:         phase,
		Action:        action,
	})
}

func (l *eventLog[T]) modelEvents() []ModelEvent[T] {
	if l == nil {
		return nil
	}
	l.mu.Lock()
	defer l.mu.Unlock()
	out := make([]ModelEvent[T], len(l.events))
	for i, ev := range l.events {
		out[i] = ModelEvent[T]{
			SchemaVersion: ModelEventSchemaVersion,
			RunID:         l.runID,
			DispatcherID:  l.dispatcherID,
			Sequence:      uint64(i + 1),
			OperationID:   ev.operationID,
			Operation:     ev.operation,
			Action:        string(ev.kind),
			Value:         ev.value,
			HasValue:      ev.hasValue,
			QueueLen:      ev.queueLen,
			Dropped:       ev.dropped,
		}
	}
	return out
}

func (l *eventLog[T]) operationIntervals() []OperationIntervalEvent {
	if l == nil {
		return nil
	}
	l.mu.Lock()
	defer l.mu.Unlock()
	out := make([]OperationIntervalEvent, len(l.intervalEvents))
	copy(out, l.intervalEvents)
	return out
}
