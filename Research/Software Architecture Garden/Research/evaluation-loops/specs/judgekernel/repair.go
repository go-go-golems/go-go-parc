package judgekernel

import (
	"context"
	"fmt"
)

// Generator runs one prompt on the judge model and returns its raw text.
// It is the only model-facing type in the kernel.
type Generator func(ctx context.Context, prompt string) (string, error)

// RepairBudget bounds structural repairs. One budget is shared across both
// judge steps for one cell — the CoinVault discipline (retryUsed is threaded
// through extraction and verdicts) — so a cell costs at most one extra call
// regardless of which step misbehaved.
type RepairBudget struct {
	used bool
}

// TryUse consumes the budget if available.
func (b *RepairBudget) TryUse() bool {
	if b == nil || b.used {
		return false
	}
	b.used = true
	return true
}

// Used reports whether the repair was consumed.
func (b *RepairBudget) Used() bool { return b != nil && b.used }

// WithRepairFeedback wraps a generator so the retried prompt carries the
// validation error. Appending to the prompt also changes the population
// cache key, so a cached invalid response cannot be replayed as the repair.
func WithRepairFeedback(generate Generator, invalid error) Generator {
	return func(ctx context.Context, prompt string) (string, error) {
		return generate(ctx, fmt.Sprintf("%s\n\nYour previous response was structurally invalid: %s. Return one corrected JSON object that strictly follows the requested schema.", prompt, invalid))
	}
}

// RunWithRepair executes step with the generator; if the result is a
// structural AdmissionError and the shared budget is available, it reruns
// once with the error appended to the prompt. Provider errors and admitted
// results never trigger repair, and a second structural failure is final.
func RunWithRepair[T any](ctx context.Context, budget *RepairBudget, generate Generator, step func(ctx context.Context, generate Generator) (T, error)) (T, error) {
	out, err := step(ctx, generate)
	if err == nil || !IsAdmissionError(err) {
		return out, err
	}
	if !budget.TryUse() {
		return out, err
	}
	return step(ctx, WithRepairFeedback(generate, err))
}
