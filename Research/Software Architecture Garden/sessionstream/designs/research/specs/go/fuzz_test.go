package dispatchlab

import (
	"sync/atomic"
	"testing"
	"time"
)

// FuzzDispatcherOps is a state-aware native Go fuzzer for the dispatcher,
// following the SESSIONSTREAM-005 pattern: bytes encode an operation
// sequence, and an independent oracle — the abstract kernel transliterated
// in model.go — decides whether the execution was legal.
//
// Input encoding: pairs of bytes (op, arg), op = b % 6:
//
//	0: TrySubmit(int(arg))
//	1: Close()
//	2: Wait checkpoint — first occurrence spawns the Wait goroutine
//	3: toggle "panic on odd values" in the callback (armed iff arg even)
//	4: block callbacks (gate closes)
//	5: release callbacks (gate opens)
//
// The final phase always releases the gate, closes, and waits (with a
// watchdog), so every execution terminates in a fully drained dispatcher
// whose entire trace must replay through the proved kernel.
//
// Checked at the end of every execution:
//
//   - every event is a legal step of the abstract kernel (D1-D9 legality)
//   - invoked == admitted  (D3 order + D8 drain completeness + D5:
//     panicking items are still invoked, in order)
//   - d.Dropped() == kernel dropped (D4)
//   - the Wait goroutine returned (D9; the watchdog catches worker death)
func FuzzDispatcherOps(f *testing.F) {
	// Seed corpus: readable scenario traces (regression anchors, cf. the
	// checked-in seeds of the heartbeat arbitration fuzzer).
	f.Add([]byte{0, 1, 0, 2, 0, 3, 1, 0})                                  // submit 1,2,3; close
	f.Add([]byte{4, 0, 0, 1, 0, 2, 0, 3, 0, 4, 5, 0, 1, 0})                // block; fill; release; close
	f.Add([]byte{3, 0, 0, 1, 0, 3, 0, 5, 0, 2, 1, 0})                      // panic parity; odd+even submits
	f.Add([]byte{1, 0, 0, 1, 2, 0, 1, 0, 0, 2})                            // close; submit; wait; close; submit
	f.Add([]byte{0, 9, 0, 9, 0, 9, 0, 9, 0, 9, 1, 0})                      // overflow drops then close
	f.Add([]byte{4, 0, 0, 1, 0, 2, 0, 3, 0, 4, 0, 5, 1, 0, 5, 0, 2, 0})    // block; overfill; close; release; wait
	f.Add([]byte{0, 1, 1, 0, 0, 2, 3, 0, 0, 3, 4, 0, 5, 0, 0, 4, 2, 0})    // mixed lifecycle with gate + panic

	f.Fuzz(func(t *testing.T, data []byte) {
		if len(data) > 256 {
			data = data[:256]
		}
		const capacity = 4

		invoked := &intSlice{}
		g := newGate()
		var panicOnOdd atomic.Bool

		d, err := NewChecked[int](capacity, func(v int) {
			invoked.append(v)
			g.wait()
			if panicOnOdd.Load() && v%2 == 1 {
				panic("fuzz panic")
			}
		})
		if err != nil {
			t.Fatal(err)
		}

		var waitKicked atomic.Bool
		waitReturned := make(chan struct{}, 1)

		for i := 0; i+1 < len(data); i += 2 {
			op, arg := data[i]%6, data[i+1]
			switch op {
			case 0:
				d.TrySubmit(int(arg))
			case 1:
				d.Close()
			case 2:
				if waitKicked.CompareAndSwap(false, true) {
					go func() {
						d.Wait()
						waitReturned <- struct{}{}
					}()
				}
			case 3:
				panicOnOdd.Store(arg%2 == 0)
			case 4:
				g.block()
			case 5:
				g.release()
			}
		}

		// Final phase: always drain and close.
		g.release()
		d.Close()
		waitWithTimeout(t, d, 10*time.Second)

		// Oracle 1: the whole trace must be a legal execution of the kernel.
		m := replayTrace(t, d, capacity)

		// Oracle 2: callback invocations equal admissions, in order.
		if got := invoked.slice(); !equalInts(got, m.admitted) {
			t.Fatalf("D3/D5/D8 violated: invoked = %v, admitted = %v", got, m.admitted)
		}

		// Oracle 3: drop accounting agrees with the kernel.
		if got := d.Dropped(); got != m.dropped {
			t.Fatalf("D4 violated: Dropped() = %d, kernel dropped = %d", got, m.dropped)
		}

		// Oracle 4: a kicked Wait must return now that the worker has exited
		// (scheduling delay of the goroutine itself is not a violation).
		if waitKicked.Load() {
			select {
			case <-waitReturned:
			case <-time.After(5 * time.Second):
				t.Fatal("D9 violated: Wait goroutine did not return after worker exit")
			}
		}
	})
}
