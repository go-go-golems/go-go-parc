package dispatchlab

import (
	"sync"
	"testing"
	"time"
)

// intSlice is a mutex-guarded []int for recording callback invocations.
type intSlice struct {
	mu  sync.Mutex
	vals []int
}

func (s *intSlice) append(v int) {
	s.mu.Lock()
	s.vals = append(s.vals, v)
	s.mu.Unlock()
}

func (s *intSlice) slice() []int {
	s.mu.Lock()
	defer s.mu.Unlock()
	out := make([]int, len(s.vals))
	copy(out, s.vals)
	return out
}

// gate blocks callbacks while closed. Open gate: ch == nil (wait returns
// immediately). Closed gate: ch != nil (wait blocks until release closes it).
type gate struct {
	mu sync.Mutex
	ch chan struct{}
}

func newGate() *gate { return &gate{} }

func (g *gate) block() {
	g.mu.Lock()
	if g.ch == nil {
		g.ch = make(chan struct{})
	}
	g.mu.Unlock()
}

func (g *gate) release() {
	g.mu.Lock()
	if g.ch != nil {
		close(g.ch)
		g.ch = nil
	}
	g.mu.Unlock()
}

func (g *gate) wait() {
	g.mu.Lock()
	ch := g.ch
	g.mu.Unlock()
	if ch != nil {
		<-ch
	}
}

// waitWithTimeout fails the test if d.Wait() does not return within the
// timeout. This turns "worker died / never drains" defects (e.g. a removed
// panic recovery) into test failures instead of hung test processes.
func waitWithTimeout(t *testing.T, d *Dispatcher[int], timeout time.Duration) {
	t.Helper()
	done := make(chan struct{})
	go func() {
		d.Wait()
		close(done)
	}()
	select {
	case <-done:
	case <-time.After(timeout):
		t.Fatalf("Wait did not return within %s (worker stuck or dead)", timeout)
	}
}

// replayTrace replays the dispatcher's trace through the abstract kernel and
// fails the test on the first illegal step.
func replayTrace(t *testing.T, d *Dispatcher[int], capacity int) *stepModel {
	t.Helper()
	m, err := replayIntLog(d.trace(), capacity)
	if err != nil {
		t.Fatalf("trace replay against abstract kernel failed: %v", err)
	}
	return m
}
