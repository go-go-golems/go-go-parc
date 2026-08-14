package runcustody

import (
	"errors"
	"fmt"
	"sync"
)

// Stats is the durable spend record a resumed run seeds from prior
// artifacts (CoinVault loadGECRagoptResumeUsage).
type Stats struct {
	Calls  int `json:"calls"`
	Tokens int `json:"tokens"`
}

// Accountant is a pre-reserving budget accountant generalizing CoinVault's
// judge runtime (reserve-then-commit with rollback) and execution budget
// (ceilings, one-shot resume seeding, sticky conservative close).
//
// The reservation makes the ceiling guard and the admission one atomic
// step, which is what keeps concurrent callers within the call ceiling;
// the Budget.tla MutNoReserve counterexample shows the interleaving that
// overshoots when the guard and the spend are separate steps.
type Accountant struct {
	mu        sync.Mutex
	maxCalls  int
	maxTokens int
	spent     Stats
	reserved  int
	closed    string
	touched   bool
}

func NewAccountant(maxCalls, maxTokens int) (*Accountant, error) {
	if maxCalls <= 0 || maxTokens <= 0 {
		return nil, errors.New("budget ceilings must be positive")
	}
	return &Accountant{maxCalls: maxCalls, maxTokens: maxTokens}, nil
}

// Seed installs prior durable spend exactly once, before any reservation
// or commit, and rejects seeds that already exceed a ceiling.
func (a *Accountant) Seed(stats Stats) error {
	if a == nil {
		return errors.New("accountant is nil")
	}
	if stats.Calls < 0 || stats.Tokens < 0 {
		return errors.New("seed values must be nonnegative")
	}
	a.mu.Lock()
	defer a.mu.Unlock()
	if a.touched || a.spent != (Stats{}) || a.reserved != 0 {
		return errors.New("budget was already initialized")
	}
	if stats.Calls > a.maxCalls || stats.Tokens > a.maxTokens {
		return fmt.Errorf("prior usage exceeds budget: calls=%d/%d tokens=%d/%d",
			stats.Calls, a.maxCalls, stats.Tokens, a.maxTokens)
	}
	a.spent = stats
	a.touched = true
	return nil
}

// Reservation is one admitted-but-uncompleted call. Exactly one of Commit
// or Rollback must be invoked; both are idempotent afterward.
type Reservation struct {
	accountant *Accountant
	settled    bool
}

// Reserve atomically checks the sticky close and the call ceiling and
// admits one call. spent+reserved never exceeds maxCalls, so completed
// spend cannot overshoot regardless of caller concurrency.
func (a *Accountant) Reserve() (*Reservation, error) {
	if a == nil {
		return nil, errors.New("accountant is nil")
	}
	a.mu.Lock()
	defer a.mu.Unlock()
	a.touched = true
	if a.closed != "" {
		return nil, fmt.Errorf("budget is closed: %s", a.closed)
	}
	if a.spent.Calls+a.reserved >= a.maxCalls {
		return nil, fmt.Errorf("call budget exhausted: spent=%d reserved=%d max=%d",
			a.spent.Calls, a.reserved, a.maxCalls)
	}
	if a.spent.Tokens >= a.maxTokens {
		return nil, fmt.Errorf("token budget exhausted: %d/%d", a.spent.Tokens, a.maxTokens)
	}
	a.reserved++
	return &Reservation{accountant: a}, nil
}

// Commit converts the reservation into completed spend. Token cost is only
// known after the call, so the token ceiling is enforced post hoc: an
// overshooting commit is recorded (the spend happened) and returns an
// error so the caller stops before further work.
func (r *Reservation) Commit(tokens int) error {
	if r == nil || r.accountant == nil {
		return errors.New("reservation is nil")
	}
	if tokens < 0 {
		return errors.New("token cost must be nonnegative")
	}
	a := r.accountant
	a.mu.Lock()
	defer a.mu.Unlock()
	if r.settled {
		return errors.New("reservation was already settled")
	}
	r.settled = true
	a.reserved--
	a.spent.Calls++
	a.spent.Tokens += tokens
	if a.spent.Tokens > a.maxTokens {
		return fmt.Errorf("token budget exceeded: %d/%d", a.spent.Tokens, a.maxTokens)
	}
	return nil
}

// Rollback releases an unused reservation (the ceiling-breach error path
// of CoinVault's reserveProviderCall).
func (r *Reservation) Rollback() {
	if r == nil || r.accountant == nil {
		return
	}
	a := r.accountant
	a.mu.Lock()
	defer a.mu.Unlock()
	if r.settled {
		return
	}
	r.settled = true
	a.reserved--
}

// CloseForUncertainSpend latches the first reason and permanently refuses
// new reservations. It never reopens: once spend cannot be proved, the
// only conservative answer is to stop starting work.
func (a *Accountant) CloseForUncertainSpend(reason string) {
	if a == nil || reason == "" {
		return
	}
	a.mu.Lock()
	defer a.mu.Unlock()
	if a.closed == "" {
		a.closed = reason
	}
}

// Snapshot returns current spend and reservation state.
func (a *Accountant) Snapshot() (Stats, int, string) {
	if a == nil {
		return Stats{}, 0, ""
	}
	a.mu.Lock()
	defer a.mu.Unlock()
	return a.spent, a.reserved, a.closed
}
