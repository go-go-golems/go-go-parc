package runcustody

import (
	"strings"
	"sync"
	"testing"
)

func TestAccountantCeilingUnderConcurrency(t *testing.T) {
	const maxCalls = 16
	accountant, err := NewAccountant(maxCalls, 1_000_000)
	if err != nil {
		t.Fatal(err)
	}
	var wg sync.WaitGroup
	for worker := 0; worker < 8; worker++ {
		wg.Add(1)
		go func() {
			defer wg.Done()
			for {
				reservation, err := accountant.Reserve()
				if err != nil {
					return // budget exhausted for this worker
				}
				if err := reservation.Commit(10); err != nil {
					t.Errorf("commit: %v", err)
					return
				}
			}
		}()
	}
	wg.Wait()
	spent, reserved, closed := accountant.Snapshot()
	if spent.Calls != maxCalls {
		t.Fatalf("spent calls %d, want exactly the ceiling %d", spent.Calls, maxCalls)
	}
	if reserved != 0 || closed != "" {
		t.Fatalf("leaked reservations=%d closed=%q", reserved, closed)
	}
	if _, err := accountant.Reserve(); err == nil {
		t.Fatal("reserve succeeded past the ceiling")
	}
}

func TestRollbackReleasesReservation(t *testing.T) {
	accountant, err := NewAccountant(1, 100)
	if err != nil {
		t.Fatal(err)
	}
	reservation, err := accountant.Reserve()
	if err != nil {
		t.Fatal(err)
	}
	if _, err := accountant.Reserve(); err == nil {
		t.Fatal("second reserve succeeded while first was outstanding at ceiling 1")
	}
	reservation.Rollback()
	if _, err := accountant.Reserve(); err != nil {
		t.Fatalf("reserve after rollback: %v", err)
	}
	reservation.Rollback() // idempotent settle: must not double-release
	spent, reserved, _ := accountant.Snapshot()
	if spent.Calls != 0 || reserved != 1 {
		t.Fatalf("bookkeeping after idempotent rollback: spent=%d reserved=%d", spent.Calls, reserved)
	}
}

func TestStickyCloseRefusesNewWorkAndKeepsFirstReason(t *testing.T) {
	accountant, err := NewAccountant(10, 100)
	if err != nil {
		t.Fatal(err)
	}
	accountant.CloseForUncertainSpend("cell timeout with outstanding provider calls")
	accountant.CloseForUncertainSpend("second reason must not overwrite")
	if _, err := accountant.Reserve(); err == nil || !strings.Contains(err.Error(), "cell timeout") {
		t.Fatalf("closed accountant admitted work or lost first reason: %v", err)
	}
}

func TestTokenCeilingIsPostHoc(t *testing.T) {
	accountant, err := NewAccountant(10, 50)
	if err != nil {
		t.Fatal(err)
	}
	reservation, err := accountant.Reserve()
	if err != nil {
		t.Fatal(err)
	}
	// Token cost is only known after the call: the overshooting commit is
	// recorded (the spend happened) and reported as an error.
	if err := reservation.Commit(80); err == nil {
		t.Fatal("overshooting commit did not report token ceiling breach")
	}
	spent, _, _ := accountant.Snapshot()
	if spent.Tokens != 80 || spent.Calls != 1 {
		t.Fatalf("overshoot not recorded faithfully: %+v", spent)
	}
	if _, err := accountant.Reserve(); err == nil {
		t.Fatal("reserve succeeded after token exhaustion")
	}
}

func TestSeedOnceBeforeSpendAndWithinCeilings(t *testing.T) {
	accountant, err := NewAccountant(10, 100)
	if err != nil {
		t.Fatal(err)
	}
	if err := accountant.Seed(Stats{Calls: 11, Tokens: 5}); err == nil {
		t.Fatal("seed above call ceiling accepted")
	}
	if err := accountant.Seed(Stats{Calls: 4, Tokens: 40}); err != nil {
		t.Fatalf("valid seed rejected: %v", err)
	}
	if err := accountant.Seed(Stats{Calls: 1, Tokens: 1}); err == nil {
		t.Fatal("second seed accepted")
	}
	reservation, err := accountant.Reserve()
	if err != nil {
		t.Fatal(err)
	}
	reservation.Rollback()
	fresh, _ := NewAccountant(10, 100)
	if _, err := fresh.Reserve(); err != nil {
		t.Fatal(err)
	}
	if err := fresh.Seed(Stats{Calls: 1}); err == nil {
		t.Fatal("seed after first reservation accepted")
	}
}

// TestNaiveCheckThenSpendOvershoots is the executable twin of the
// Budget.tla MutNoReserve counterexample: when the ceiling guard and the
// spend are separate steps with no reservation, two concurrent callers
// both pass the guard at spent==max-1 and the ceiling is exceeded. The
// test asserts the FAILURE occurs, documenting why Reserve exists.
func TestNaiveCheckThenSpendOvershoots(t *testing.T) {
	const maxCalls = 1
	var mu sync.Mutex
	spent := 0
	guard := func() bool { // AllowAnswerRun-style check without reservation
		mu.Lock()
		defer mu.Unlock()
		return spent < maxCalls
	}
	spend := func() {
		mu.Lock()
		defer mu.Unlock()
		spent++
	}

	admitted := make(chan struct{})
	proceed := make(chan struct{})
	var wg sync.WaitGroup
	for worker := 0; worker < 2; worker++ {
		wg.Add(1)
		go func() {
			defer wg.Done()
			if !guard() {
				t.Error("guard rejected before any spend")
				return
			}
			admitted <- struct{}{}
			<-proceed
			spend()
		}()
	}
	<-admitted
	<-admitted // both workers passed the guard before any spend landed
	close(proceed)
	wg.Wait()
	if spent != maxCalls+1 {
		t.Fatalf("expected the naive design to overshoot (spent=%d), got %d", maxCalls+1, spent)
	}
}
