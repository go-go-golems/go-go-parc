package gatealgebra

import (
	"os"
	"path/filepath"
	"testing"
)

// evaluateRescueMutant is the seeded defect the golden suite must catch: it
// lets a passing tie-break phase rescue a failed verdict, i.e. it deletes the
// constraint-domination law. Lean's evalRescueMutant example is the abstract
// version of the same defect.
func evaluateRescueMutant(p Policy, r Report) Decision {
	d := evaluateStrict(p, r)
	rescued := true
	for _, c := range d.Checks {
		if c.Phase == PhaseTieBreak && !c.Passed {
			rescued = false
		}
	}
	if len(p.TieBreakers) > 0 && rescued {
		d.Status = StatusPass
	}
	return d
}

// evaluateReorderedMutant swaps the hard and target phases while keeping
// short-circuit semantics.
func evaluateReorderedMutant(p Policy, r Report) Decision {
	d := Decision{PolicyDigest: p.ByteDigest, Status: StatusPass}
	for _, phase := range [][]Check{
		identityPhase(p, r),
		targetPhase(p, r), // swapped
		hardPhase(p, r),   // swapped
		regressionPhase(p, r),
	} {
		if record(&d, phase) {
			return d
		}
	}
	record(&d, tieBreakPhase(p, r))
	return d
}

// TestRescueMutantIsCaughtByGoldens: on the hard-fail fixture the mutant
// reports pass where the correct gate reports fail, so the pinned golden
// rejects it. This is the acceptance-gate mutation for the project.
func TestRescueMutantIsCaughtByGoldens(t *testing.T) {
	policy, report := basePolicy(), baseReport()
	report.Pairs[1].Candidate.Completed = false
	report.Pairs[1].Candidate.Failed = true

	correct := Evaluate(policy, report)
	mutant := evaluateRescueMutant(policy, report)
	if correct.Status != StatusFail {
		t.Fatal("fixture must fail the correct gate")
	}
	if mutant.Status != StatusPass {
		t.Fatal("mutant construction error: rescue mutant should pass the hard-fail fixture")
	}
	golden, err := os.ReadFile(filepath.Join("testdata", "hard-fail.golden"))
	if err != nil {
		t.Fatal(err)
	}
	if decisionSummary(mutant) == string(golden) {
		t.Fatal("golden failed to distinguish the rescue mutant")
	}
}

// TestReorderedMutantStatusInvariantTranscriptCaught: per Lean theorem
// strict_phase_order_irrelevant the reordered mutant produces the SAME
// status, so a status-only assertion cannot catch it — but the transcript
// golden does. This test documents both halves.
func TestReorderedMutantStatusInvariantTranscriptCaught(t *testing.T) {
	policy, report := basePolicy(), baseReport()
	report.Pairs[1].Candidate.Completed = false
	report.Pairs[1].Candidate.Failed = true

	correct := Evaluate(policy, report)
	mutant := evaluateReorderedMutant(policy, report)
	if correct.Status != mutant.Status {
		t.Fatalf("phase order must not change the verdict: correct=%s mutant=%s", correct.Status, mutant.Status)
	}
	golden, err := os.ReadFile(filepath.Join("testdata", "hard-fail.golden"))
	if err != nil {
		t.Fatal(err)
	}
	if decisionSummary(mutant) == string(golden) {
		t.Fatal("transcript golden failed to distinguish the reordered mutant")
	}
}
