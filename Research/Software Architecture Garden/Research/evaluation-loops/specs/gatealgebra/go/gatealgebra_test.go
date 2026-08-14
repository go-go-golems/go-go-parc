package gatealgebra

import (
	"flag"
	"fmt"
	"os"
	"path/filepath"
	"strings"
	"testing"
)

var update = flag.Bool("update", false, "rewrite golden files")

const testDigest = PolicyDigest("sha256:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa")

func basePolicy() Policy {
	return Policy{
		ByteDigest:           testDigest,
		RequireAllCells:      true,
		RequireCompleted:     true,
		RequireContractValid: true,
		MaxFailureRate:       0,
		MetricFloors:         map[string]float64{"safety": 0.8},
		TargetMetric:         "quality",
		TargetGroups:         []string{"feedback"},
		MinimumMeanDelta:     0.05,
		MaxCaseDelta:         map[string]float64{"safety": -0.2},
		MaxMeanDelta:         map[string]map[string]float64{"all": {"quality": -0.05}},
		TieBreakers:          []string{"provider_calls", "total_tokens"},
	}
}

func outcome(quality, safety float64) Outcome {
	return Outcome{
		Completed:     true,
		ContractValid: true,
		Metrics:       map[string]float64{"quality": quality, "safety": safety},
	}
}

// baseReport mirrors the shape of ragopt's gate fixture: two cases, one
// repeat, candidate ahead on quality, safety level.
func baseReport() Report {
	return Report{
		PolicyByteDigest: testDigest,
		RunComplete:      true,
		ExpectedPairs:    2,
		Pairs: []Pair{
			{CaseID: "case-a", Repeat: 0, Groups: []string{"feedback"},
				Incumbent: outcome(0.60, 0.90), Candidate: outcome(0.75, 0.90)},
			{CaseID: "case-b", Repeat: 0, Groups: []string{"feedback"},
				Incumbent: outcome(0.55, 0.85), Candidate: outcome(0.70, 0.85)},
		},
	}
}

func decisionSummary(d Decision) string {
	var b strings.Builder
	fmt.Fprintf(&b, "status=%s\n", d.Status)
	for _, c := range d.Checks {
		verdict := "pass"
		if !c.Passed {
			verdict = "fail"
		}
		fmt.Fprintf(&b, "%s/%s=%s\n", c.Phase, c.Name, verdict)
	}
	return b.String()
}

func TestGateDecisionGoldens(t *testing.T) {
	tests := []struct {
		name   string
		mutate func(*Policy, *Report)
	}{
		{name: "pass"},
		{name: "hard-fail", mutate: func(_ *Policy, r *Report) {
			// One candidate cell incomplete and failed: require_completed AND
			// max_failure_rate both fail, and both are recorded — intra-phase
			// totality, exactly as in ragopt's hard-fail golden.
			r.Pairs[1].Candidate.Completed = false
			r.Pairs[1].Candidate.Failed = true
		}},
		{name: "target-fail", mutate: func(_ *Policy, r *Report) {
			r.Pairs[0].Candidate.Metrics["quality"] = 0.58
			r.Pairs[1].Candidate.Metrics["quality"] = 0.56
		}},
		{name: "hard-floor-fail", mutate: func(_ *Policy, r *Report) {
			// A catastrophic safety drop is caught FIRST by the hard metric
			// floor (0.65 < 0.8); the case-delta regression check would also
			// reject it but is never reached. Phase coverage overlaps, and the
			// transcript names the earliest responsible phase.
			r.Pairs[0].Candidate.Metrics["safety"] = 0.65
			r.Pairs[0].Candidate.Metrics["quality"] = 0.75
		}},
		{name: "regression-fail", mutate: func(p *Policy, r *Report) {
			// The same safety drop with the hard floor lowered to 0.5: now the
			// per-case regression check (delta -0.25 < -0.2) is what rejects.
			p.MetricFloors["safety"] = 0.5
			r.Pairs[0].Candidate.Metrics["safety"] = 0.65
		}},
		{name: "tie-break", mutate: func(p *Policy, _ *Report) {
			p.MinimumMeanDelta = 0
		}},
		{name: "incomplete-pairing", mutate: func(_ *Policy, r *Report) {
			dropped := r.Pairs[1]
			r.Pairs = r.Pairs[:1]
			r.Missing = append(r.Missing, MissingPair{CaseID: dropped.CaseID, Repeat: dropped.Repeat, Groups: dropped.Groups})
		}},
	}
	for _, test := range tests {
		t.Run(test.name, func(t *testing.T) {
			policy, report := basePolicy(), baseReport()
			if test.mutate != nil {
				test.mutate(&policy, &report)
			}
			actual := decisionSummary(Evaluate(policy, report))
			golden := filepath.Join("testdata", test.name+".golden")
			if *update {
				if err := os.MkdirAll("testdata", 0o755); err != nil {
					t.Fatal(err)
				}
				if err := os.WriteFile(golden, []byte(actual), 0o644); err != nil {
					t.Fatal(err)
				}
			}
			expected, err := os.ReadFile(golden)
			if err != nil {
				t.Fatal(err)
			}
			if actual != string(expected) {
				t.Fatalf("decision mismatch\n--- actual ---\n%s--- expected ---\n%s", actual, expected)
			}
		})
	}
}

// enumerateReports builds a small deterministic report space for the
// property tests: every combination of two per-pair variants over two pairs,
// with and without a policy-digest mismatch.
func enumerateReports() []Report {
	variants := []Outcome{
		outcome(0.75, 0.90), // healthy improvement
		outcome(0.58, 0.90), // quality regression
		outcome(0.75, 0.65), // safety floor violation
		{Completed: false, Failed: true, // failed cell, metrics absent
			Metrics: map[string]float64{}},
	}
	reports := make([]Report, 0, len(variants)*len(variants)+1)
	for _, a := range variants {
		for _, b := range variants {
			r := baseReport()
			r.Pairs[0].Candidate = a
			r.Pairs[1].Candidate = b
			reports = append(reports, r)
		}
	}
	mismatch := baseReport()
	mismatch.PolicyByteDigest = PolicyDigest("sha256:bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb")
	reports = append(reports, mismatch)
	return reports
}

// TestShortCircuitStatusEqualsStrict re-checks Lean theorem
// sc_status_eq_strict on this implementation: stopAfter never changes the
// verdict, only the transcript length.
func TestShortCircuitStatusEqualsStrict(t *testing.T) {
	policy := basePolicy()
	for i, report := range enumerateReports() {
		sc := Evaluate(policy, report)
		strict := evaluateStrict(policy, report)
		if sc.Status != strict.Status {
			t.Fatalf("report %d: short-circuit %s != strict %s", i, sc.Status, strict.Status)
		}
		if len(sc.Checks) > len(strict.Checks) {
			t.Fatalf("report %d: short-circuit transcript longer than strict", i)
		}
	}
}

// TestDroppingPairsNeverFlipsToPass re-checks Lean theorem
// dropped_report_fails at gate level: from any fully-paired report, moving
// any pair to Missing yields a failing decision, whatever the rest of the
// report says.
func TestDroppingPairsNeverFlipsToPass(t *testing.T) {
	policy := basePolicy()
	for i, report := range enumerateReports() {
		for drop := range report.Pairs {
			mutated := report
			mutated.Pairs = make([]Pair, 0, len(report.Pairs)-1)
			for j, pair := range report.Pairs {
				if j == drop {
					mutated.Missing = append([]MissingPair(nil), MissingPair{
						CaseID: pair.CaseID, Repeat: pair.Repeat, Groups: pair.Groups,
					})
					continue
				}
				mutated.Pairs = append(mutated.Pairs, pair)
			}
			if got := Evaluate(policy, mutated); got.Status != StatusFail {
				t.Fatalf("report %d drop %d: expected fail after data loss, got %s", i, drop, got.Status)
			}
		}
	}
}

// TestFailureRateAloneIsNotMissingMonotone reproduces Lean counterexample C1
// against this implementation: the failure-rate statistic in isolation flips
// fail→pass when the failing pair goes missing, because its denominator is
// the schedule; the unconditional complete_pairing identity check is what
// restores gate-level monotonicity.
func TestFailureRateAloneIsNotMissingMonotone(t *testing.T) {
	policy := basePolicy()
	report := baseReport()
	report.Pairs[1].Candidate = Outcome{Completed: false, Failed: true, Metrics: map[string]float64{}}

	before := findCheck(t, evaluateStrict(policy, report), PhaseHard, "max_failure_rate")
	if before.Passed {
		t.Fatal("fixture must fail max_failure_rate before the drop")
	}

	dropped := report
	dropped.Pairs = report.Pairs[:1]
	dropped.Missing = []MissingPair{{CaseID: "case-b", Repeat: 0, Groups: []string{"feedback"}}}

	after := evaluateStrict(policy, dropped)
	if !findCheck(t, after, PhaseHard, "max_failure_rate").Passed {
		t.Fatal("expected max_failure_rate to flip to pass after dropping the failing pair (C1)")
	}
	if findCheck(t, after, PhaseIdentity, "complete_pairing").Passed {
		t.Fatal("complete_pairing must catch the dropped pair")
	}
	if Evaluate(policy, dropped).Status != StatusFail {
		t.Fatal("gate must still fail the dropped report")
	}
}

func findCheck(t *testing.T, d Decision, phase Phase, name string) Check {
	t.Helper()
	for _, c := range d.Checks {
		if c.Phase == phase && c.Name == name {
			return c
		}
	}
	t.Fatalf("check %s/%s not found in transcript", phase, name)
	return Check{}
}

func TestNominalPolicyDigest(t *testing.T) {
	if _, err := NewPolicyDigest("sha256:" + strings.Repeat("a", 64)); err != nil {
		t.Fatalf("valid digest rejected: %v", err)
	}
	for _, bad := range []string{"", "aaaa", "md5:" + strings.Repeat("a", 64), "sha256:short"} {
		if _, err := NewPolicyDigest(bad); err == nil {
			t.Fatalf("invalid digest %q accepted", bad)
		}
	}
}
