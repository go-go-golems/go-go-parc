package dispatchlab

import "fmt"

// stepModel is the abstract transition kernel of the dispatcher, executed as
// an oracle. It is a direct transliteration of:
//
//   - the Coq development  ../coq/Dispatcher.v   (inductive Step relation)
//   - the Lean development ../lean/Dispatcher.lean
//   - the TLA+ model       ../tla/Dispatcher.tla (including the in-flight
//     "current" item: admitted = offered ++ current ++ queue)
//
// apply(ev) rejects any event that is not a legal step from the current
// model state, cross-checks the event's recorded queue length and drop
// counter against the model state, and re-validates the invariant bundle
// after every step. A violation therefore means: the implementation
// produced an execution the proved kernel cannot produce.
//
// Why the recorded log can be replayed strictly: every event is emitted
// under d.mu at its linearization point (submit/close decisions inside the
// critical section; worker receive/offer/panic/exit via emitMu). Mutex
// acquisition order therefore orders the events exactly the way the steps
// linearized, and no event can appear before the step it records.
type stepModel struct {
	capacity int
	queue    []int
	admitted []int
	offered  []int
	current  []int // 0 or 1 element: the item being offered right now
	dropped  uint64
	closing  bool
	closeCnt int
	exited   bool
	waited   bool
}

func (m *stepModel) apply(ev event[int]) error {
	var err error
	switch ev.kind {
	case evSubmitAccepted:
		switch {
		case m.closing:
			err = fmt.Errorf("D7: submit accepted while closing")
		case len(m.queue) >= m.capacity:
			err = fmt.Errorf("D1: submit accepted while queue full (%d >= %d)", len(m.queue), m.capacity)
		default:
			m.queue = append(m.queue, ev.value)
			m.admitted = append(m.admitted, ev.value)
		}
	case evSubmitDropped:
		switch {
		case m.closing:
			err = fmt.Errorf("D4/D7: overflow drop while closing (drops are admission decisions, they precede close)")
		case len(m.queue) < m.capacity:
			err = fmt.Errorf("D4: drop counted while queue not full (%d < %d)", len(m.queue), m.capacity)
		default:
			m.dropped++
		}
	case evSubmitRejected:
		if !m.closing {
			err = fmt.Errorf("D7: submit rejected while admission open")
		}
	case evCloseEffective:
		if m.closing {
			err = fmt.Errorf("D6: queue closed more than once")
		} else {
			m.closing = true
			m.closeCnt++
		}
	case evCloseNoop:
		if !m.closing {
			err = fmt.Errorf("D6: close no-op while admission open")
		}
	case evReceive:
		switch {
		case len(m.queue) == 0:
			err = fmt.Errorf("I6: worker received from an empty queue")
		case len(m.current) != 0:
			err = fmt.Errorf("D10: worker received while another item is in flight")
		default:
			m.current = append(m.current[:0], m.queue[0])
			m.queue = m.queue[1:]
		}
	case evOffered, evPanic:
		if len(m.current) == 0 {
			err = fmt.Errorf("I6: %s with no in-flight item", ev.kind)
		} else {
			m.offered = append(m.offered, m.current[0])
			m.current = m.current[:0]
		}
	case evWorkerExit:
		switch {
		case !m.closing:
			err = fmt.Errorf("I7: worker exit before close")
		case len(m.queue) != 0:
			err = fmt.Errorf("D8: worker exit with %d undrained items", len(m.queue))
		case len(m.current) != 0:
			err = fmt.Errorf("D8: worker exit with an item still in flight")
		default:
			m.exited = true
		}
	case evWaitReturned:
		if !m.exited {
			err = fmt.Errorf("D9: Wait returned before worker exit")
		} else {
			m.waited = true
		}
	default:
		err = fmt.Errorf("unknown event kind %q", ev.kind)
	}
	if err != nil {
		return err
	}
	// Cross-check the state evidence recorded at the linearization point.
	if ev.queueLen != len(m.queue) {
		return fmt.Errorf("queue length evidence: event recorded %d, model has %d", ev.queueLen, len(m.queue))
	}
	if ev.dropped != m.dropped {
		return fmt.Errorf("drop counter evidence: event recorded %d, model has %d", ev.dropped, m.dropped)
	}
	return m.checkInv()
}

// checkInv re-validates the invariant bundle (Coq record inv / Lean
// structure Inv / TLA+ invariants) after every step.
func (m *stepModel) checkInv() error {
	if len(m.queue) > m.capacity {
		return fmt.Errorf("D1: queue bound violated: %d > %d", len(m.queue), m.capacity)
	}
	if m.closeCnt > 1 {
		return fmt.Errorf("I4: queue closed %d times", m.closeCnt)
	}
	// Shape (D3, D8, I6): admitted = offered ++ current ++ queue.
	shape := make([]int, 0, len(m.offered)+len(m.current)+len(m.queue))
	shape = append(shape, m.offered...)
	shape = append(shape, m.current...)
	shape = append(shape, m.queue...)
	if !equalInts(shape, m.admitted) {
		return fmt.Errorf("D3/D8: shape violated: offered %v ++ current %v ++ queue %v != admitted %v",
			m.offered, m.current, m.queue, m.admitted)
	}
	if m.exited && !(m.closing && len(m.queue) == 0 && len(m.current) == 0) {
		return fmt.Errorf("I7: exited but not closed-and-drained")
	}
	if m.waited && !m.exited {
		return fmt.Errorf("D9: waited but worker not exited")
	}
	return nil
}

// replayIntLog replays a recorded trace through the abstract kernel and
// returns the final model state. Any error pinpoints the first event that
// is not a legal step of the proved kernel.
func replayIntLog(events []event[int], capacity int) (*stepModel, error) {
	m := &stepModel{capacity: capacity}
	for i, ev := range events {
		if err := m.apply(ev); err != nil {
			return m, fmt.Errorf("trace event %d (%s value=%v): %w", i, ev.kind, ev.value, err)
		}
	}
	return m, nil
}

func equalInts(a, b []int) bool {
	if len(a) != len(b) {
		return false
	}
	for i := range a {
		if a[i] != b[i] {
			return false
		}
	}
	return true
}
