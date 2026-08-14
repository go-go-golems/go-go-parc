package runcustody

import (
	"encoding/json"
	"os"
	"path/filepath"
	"reflect"
	"testing"
)

// executeRun simulates a writer: for each planned coordinate it performs
// the "external effect" (counted) and then commits. When interruptAfter
// effects have run, the writer stops between effect and commit — the
// crash window the RunCustodyAtMostOnce TLC counterexample exhibits.
func executeRun(t *testing.T, path string, schedule []Coord, effects map[string]int, interruptAfterEffects int) (interrupted bool) {
	t.Helper()
	journal, completed, err := Open(path, schedule)
	if err != nil {
		t.Fatalf("open: %v", err)
	}
	plan, err := Plan(schedule, completed)
	if err != nil {
		t.Fatalf("plan: %v", err)
	}
	performed := 0
	for _, coord := range plan {
		effects[coord.Key()]++ // the external effect happens first
		performed++
		if interruptAfterEffects > 0 && performed == interruptAfterEffects {
			// Crash between effect and commit, leaving a torn tail.
			file, err := os.OpenFile(path, os.O_CREATE|os.O_APPEND|os.O_WRONLY, 0o600)
			if err != nil {
				t.Fatal(err)
			}
			if _, err := file.Write([]byte(`{"api_version":"runcust`)); err != nil {
				t.Fatal(err)
			}
			_ = file.Close()
			return true
		}
		payload, _ := json.Marshal(map[string]string{"result": coord.Key()})
		if err := journal.Append(Record{Coord: coord, Payload: payload}); err != nil {
			t.Fatalf("append: %v", err)
		}
	}
	return false
}

func committedSequence(t *testing.T, path string, schedule []Coord) []string {
	t.Helper()
	_, completed, err := Open(path, schedule)
	if err != nil {
		t.Fatalf("load committed: %v", err)
	}
	var sequence []string
	for _, coord := range schedule {
		if _, exists := completed[coord.Key()]; exists {
			sequence = append(sequence, coord.Key())
		}
	}
	if len(sequence) != len(completed) {
		t.Fatalf("committed records outside schedule order: %d vs %d", len(sequence), len(completed))
	}
	return sequence
}

// TestResumeEquivalenceAtEveryInterruptionPoint is the Go analogue of the
// TLC-checked DurableIsSchedulePrefix + CompletionExact invariants plus
// the AtMostOnceEffects refutation: for every interruption point, the
// resumed run commits exactly the uninterrupted coordinate sequence, and
// the interrupted coordinate's effect ran twice (at-least-once, exposed).
func TestResumeEquivalenceAtEveryInterruptionPoint(t *testing.T) {
	schedule := testSchedule()

	baselinePath := filepath.Join(t.TempDir(), "baseline.jsonl")
	baselineEffects := map[string]int{}
	if interrupted := executeRun(t, baselinePath, schedule, baselineEffects, 0); interrupted {
		t.Fatal("baseline must not interrupt")
	}
	baseline := committedSequence(t, baselinePath, schedule)

	for interruptAfter := 1; interruptAfter <= len(schedule); interruptAfter++ {
		path := filepath.Join(t.TempDir(), "interrupted.jsonl")
		effects := map[string]int{}
		if !executeRun(t, path, schedule, effects, interruptAfter) {
			t.Fatalf("interruption point %d did not interrupt", interruptAfter)
		}
		if executeRun(t, path, schedule, effects, 0) {
			t.Fatalf("resume at point %d interrupted again", interruptAfter)
		}
		resumed := committedSequence(t, path, schedule)
		if !reflect.DeepEqual(resumed, baseline) {
			t.Fatalf("interruption point %d: resumed %v != baseline %v", interruptAfter, resumed, baseline)
		}
		interruptedCoord := schedule[interruptAfter-1].Key()
		for _, coord := range schedule {
			want := 1
			if coord.Key() == interruptedCoord {
				want = 2 // crash between effect and commit re-executes: at-least-once
			}
			if got := effects[coord.Key()]; got != want {
				t.Fatalf("interruption point %d: effects[%s]=%d want %d", interruptAfter, coord.Key(), got, want)
			}
		}
	}
}

func TestPlanRejectsForeignCompletedKeys(t *testing.T) {
	schedule := testSchedule()
	completed := map[string]Record{"foreign\x000\x00arm": {}}
	if _, err := Plan(schedule, completed); err == nil {
		t.Fatal("plan accepted a completed key outside the schedule")
	}
}
