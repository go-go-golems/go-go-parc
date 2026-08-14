// Package gatealgebra is a research prototype of a reusable
// constraint-domination gate, extracted from the shape shared by
// ragopt pkg/gate (v0.0.1), CoinVault's retrievalSummaryWins mini-gate, and
// the gate policies both products author.
//
// The algebra it implements is the one proved in ../lean/GateAlgebra.lean:
//
//   - a phase evaluates all of its checks (intra-phase totality);
//   - a failed phase terminates evaluation before later phases
//     (inter-phase short-circuit), and by theorem sc_status_eq_strict the
//     short-circuit is semantically inert for the verdict;
//   - tie-break checks are informational and can never change the status
//     (theorem tiebreak_inert);
//   - the unconditional complete-pairing identity check is load-bearing:
//     without it, both the failure-rate check and the presence-guarded mean
//     checks can flip fail→pass when pairs go missing (counterexamples C1 and
//     C2), and with it a report that lost any pair always fails
//     (theorems dropped_report_fails and dropped_target_fails).
//
// The package is pure: Evaluate performs no I/O, reads no clocks, and is a
// function of exactly (Policy, Report).
package gatealgebra

import (
	"fmt"
	"math"
	"sort"
	"strings"
)

// PolicyDigest is a nominal digest type. Two digests compare equal only as
// PolicyDigest values; a raw string does not satisfy an API that demands one,
// which prevents the byte-digest/semantic-digest confusion recorded as
// architecture debt in the Ragopt Garden study.
type PolicyDigest string

// NewPolicyDigest validates the canonical "sha256:<hex>" rendering.
func NewPolicyDigest(raw string) (PolicyDigest, error) {
	if !strings.HasPrefix(raw, "sha256:") || len(raw) != len("sha256:")+64 {
		return "", fmt.Errorf("policy digest must be sha256:<64 hex chars>, got %q", raw)
	}
	return PolicyDigest(raw), nil
}

// Phase names the lexicographic constraint phases. The order of the constants
// is the evaluation order; tie_break is preference and never decides.
type Phase string

const (
	PhaseIdentity   Phase = "identity"
	PhaseHard       Phase = "hard"
	PhaseTarget     Phase = "target"
	PhaseRegression Phase = "regression"
	PhaseTieBreak   Phase = "tie_break"
)

// Status is the gate verdict.
type Status string

const (
	StatusPass Status = "pass"
	StatusFail Status = "fail"
)

// Check is one named, phase-tagged verdict component.
type Check struct {
	Phase   Phase
	Name    string
	Passed  bool
	Message string
}

// Outcome is the per-arm slice of a comparison cell the gate needs.
type Outcome struct {
	Completed     bool
	ContractValid bool
	Failed        bool
	Metrics       map[string]float64
}

// Pair joins incumbent and candidate outcomes at one (case, repeat)
// coordinate. Deltas are computed, never stored, so a pair cannot carry a
// delta for a metric one side is missing.
type Pair struct {
	CaseID    string
	Repeat    int
	Groups    []string
	Incumbent Outcome
	Candidate Outcome
}

// MissingPair records a coordinate that produced no joinable pair. It carries
// its groups so per-group denominators stay honest.
type MissingPair struct {
	CaseID string
	Repeat int
	Groups []string
}

// Report is the denominator-preserving comparison input. ExpectedPairs is the
// schedule; Pairs plus MissingPairs must account for it.
type Report struct {
	PolicyByteDigest PolicyDigest
	RunComplete      bool
	ExpectedPairs    int
	Pairs            []Pair
	Missing          []MissingPair
}

// Policy is the product-authored constraint policy, mirroring
// ragopt-gate-policy/v1's decision-relevant fields.
type Policy struct {
	ByteDigest           PolicyDigest
	RequireAllCells      bool
	RequireCompleted     bool
	RequireContractValid bool
	MaxFailureRate       float64
	MetricFloors         map[string]float64
	TargetMetric         string
	TargetGroups         []string
	MinimumMeanDelta     float64
	MaxCaseDelta         map[string]float64
	MaxMeanDelta         map[string]map[string]float64
	TieBreakers          []string
}

// Decision is gate authority: a verdict with its transcript. It is
// deliberately NOT application authority; see authority.go.
type Decision struct {
	PolicyDigest PolicyDigest
	Status       Status
	Checks       []Check
	Reasons      []string
}

// Evaluate applies identity, hard, target, and regression constraint phases
// in lexicographic order with intra-phase totality and inter-phase
// short-circuit, then appends informational tie-break observations. It is
// total for well-formed inputs and pure.
func Evaluate(p Policy, r Report) Decision {
	return evaluatePhases(p, r, true)
}

// evaluateStrict evaluates every phase with no short-circuit. Theorem
// sc_status_eq_strict says its status always equals Evaluate's; the property
// test TestShortCircuitStatusEqualsStrict re-checks that on this
// implementation.
func evaluateStrict(p Policy, r Report) Decision {
	return evaluatePhases(p, r, false)
}

func evaluatePhases(p Policy, r Report, shortCircuit bool) Decision {
	d := Decision{PolicyDigest: p.ByteDigest, Status: StatusPass}
	for _, phase := range [][]Check{
		identityPhase(p, r),
		hardPhase(p, r),
		targetPhase(p, r),
		regressionPhase(p, r),
	} {
		failed := record(&d, phase)
		if failed && shortCircuit {
			return d
		}
	}
	if d.Status == StatusPass || !shortCircuit {
		record(&d, tieBreakPhase(p, r))
	}
	return d
}

// record implements ragopt's stopAfter: append every check in the phase,
// collect failure reasons, and report whether the phase failed.
func record(d *Decision, checks []Check) bool {
	d.Checks = append(d.Checks, checks...)
	failed := false
	for _, c := range checks {
		if !c.Passed {
			failed = true
			d.Reasons = append(d.Reasons, c.Message)
		}
	}
	if failed {
		d.Status = StatusFail
	}
	return failed
}

func identityPhase(p Policy, r Report) []Check {
	return []Check{
		mk(PhaseIdentity, "policy_bytes", r.PolicyByteDigest == p.ByteDigest,
			"run policy bytes match the loaded gate policy"),
		mk(PhaseIdentity, "run_complete", r.RunComplete, "evaluated run is complete"),
		mk(PhaseIdentity, "complete_pairing",
			len(r.Pairs) == r.ExpectedPairs && len(r.Missing) == 0,
			fmt.Sprintf("complete pairs %d of %d", len(r.Pairs), r.ExpectedPairs)),
	}
}

func hardPhase(p Policy, r Report) []Check {
	checks := make([]Check, 0, 4+len(p.MetricFloors))
	if p.RequireAllCells {
		checks = append(checks, mk(PhaseHard, "require_all_cells",
			len(r.Pairs) == r.ExpectedPairs,
			fmt.Sprintf("complete pairs %d of %d", len(r.Pairs), r.ExpectedPairs)))
	}
	completed, contractValid, failures := 0, 0, 0
	for _, pair := range r.Pairs {
		if pair.Candidate.Completed {
			completed++
		}
		if pair.Candidate.ContractValid {
			contractValid++
		}
		if pair.Candidate.Failed {
			failures++
		}
	}
	if p.RequireCompleted {
		checks = append(checks, mk(PhaseHard, "require_completed",
			completed == r.ExpectedPairs,
			fmt.Sprintf("candidate completed %d of %d", completed, r.ExpectedPairs)))
	}
	if p.RequireContractValid {
		checks = append(checks, mk(PhaseHard, "require_contract_valid",
			contractValid == r.ExpectedPairs,
			fmt.Sprintf("candidate contract-valid %d of %d", contractValid, r.ExpectedPairs)))
	}
	// Denominator is the SCHEDULE, not the surviving pairs. In isolation this
	// statistic is not missing-monotone (Lean counterexample C1); the
	// unconditional complete_pairing identity check is what makes the whole
	// gate monotone (Lean theorem dropped_report_fails).
	failureRate := 1.0
	if r.ExpectedPairs > 0 {
		failureRate = float64(failures) / float64(r.ExpectedPairs)
	}
	checks = append(checks, mk(PhaseHard, "max_failure_rate",
		failureRate <= p.MaxFailureRate,
		fmt.Sprintf("candidate failure rate %.6f <= %.6f", failureRate, p.MaxFailureRate)))
	for _, metric := range sortedKeys(p.MetricFloors) {
		floor := p.MetricFloors[metric]
		present, minimum, ok := 0, math.Inf(1), true
		for _, pair := range r.Pairs {
			value, has := pair.Candidate.Metrics[metric]
			if !has {
				ok = false
				continue
			}
			present++
			minimum = math.Min(minimum, value)
			if value < floor {
				ok = false
			}
		}
		ok = ok && present == len(r.Pairs) && len(r.Pairs) > 0
		checks = append(checks, mk(PhaseHard, "metric_floor:"+metric, ok,
			fmt.Sprintf("candidate %s minimum %.6f across %d pairs; floor %.6f", metric, minimum, present, floor)))
	}
	return checks
}

func targetPhase(p Policy, r Report) []Check {
	selected, missingMetric := 0, 0
	sum := 0.0
	deltas := 0
	for _, pair := range r.Pairs {
		if !inGroups(pair.Groups, p.TargetGroups) {
			continue
		}
		selected++
		delta, ok := pairDelta(pair, p.TargetMetric)
		if !ok {
			missingMetric++
			continue
		}
		sum += delta
		deltas++
	}
	mean := 0.0
	if deltas > 0 {
		mean = sum / float64(deltas)
	}
	presence := selected > 0 && missingMetric == 0 && deltas == selected
	return []Check{
		mk(PhaseTarget, "metric_presence:"+p.TargetMetric, presence,
			fmt.Sprintf("target metric present in %d of %d selected pairs", deltas, selected)),
		mk(PhaseTarget, "minimum_mean_delta:"+p.TargetMetric,
			presence && mean >= p.MinimumMeanDelta,
			fmt.Sprintf("target mean delta %.6f >= %.6f", mean, p.MinimumMeanDelta)),
	}
}

func regressionPhase(p Policy, r Report) []Check {
	checks := make([]Check, 0)
	for _, metric := range sortedKeys(p.MaxCaseDelta) {
		floor := p.MaxCaseDelta[metric]
		present, worst, ok := 0, math.Inf(1), true
		for _, pair := range r.Pairs {
			delta, has := pairDelta(pair, metric)
			if !has {
				ok = false
				continue
			}
			present++
			worst = math.Min(worst, delta)
			if delta < floor {
				ok = false
			}
		}
		ok = ok && present == r.ExpectedPairs
		checks = append(checks, mk(PhaseRegression, "maximum_case_delta:"+metric, ok,
			fmt.Sprintf("worst case delta %.6f >= %.6f with metric in %d of %d pairs", worst, floor, present, r.ExpectedPairs)))
	}
	groups := make([]string, 0, len(p.MaxMeanDelta))
	for group := range p.MaxMeanDelta {
		groups = append(groups, group)
	}
	sort.Strings(groups)
	for _, group := range groups {
		for _, metric := range sortedKeys(p.MaxMeanDelta[group]) {
			floor := p.MaxMeanDelta[group][metric]
			expected := expectedInGroup(r, group)
			present, sum := 0, 0.0
			for _, pair := range r.Pairs {
				if group != "all" && !inGroups(pair.Groups, []string{group}) {
					continue
				}
				delta, has := pairDelta(pair, metric)
				if !has {
					continue
				}
				present++
				sum += delta
			}
			mean := 0.0
			if present > 0 {
				mean = sum / float64(present)
			}
			ok := present == expected && expected > 0 && mean >= floor
			checks = append(checks, mk(PhaseRegression, "maximum_mean_delta:"+group+":"+metric, ok,
				fmt.Sprintf("%s mean delta %.6f >= %.6f with metric in %d of %d pairs", group, mean, floor, present, expected)))
		}
	}
	return checks
}

// tieBreakPhase mirrors ragopt exactly: every tie-break check is constructed
// with Passed = true. Preference is reported, never decided. Theorem
// tiebreak_inert proves the phase cannot change the status.
func tieBreakPhase(p Policy, r Report) []Check {
	checks := make([]Check, 0, len(p.TieBreakers))
	for _, name := range p.TieBreakers {
		checks = append(checks, mk(PhaseTieBreak, name, true,
			"lower is preferred only after quality gates"))
	}
	return checks
}

func expectedInGroup(r Report, group string) int {
	if group == "all" {
		return r.ExpectedPairs
	}
	count := 0
	for _, pair := range r.Pairs {
		if inGroups(pair.Groups, []string{group}) {
			count++
		}
	}
	for _, missing := range r.Missing {
		if inGroups(missing.Groups, []string{group}) {
			count++
		}
	}
	return count
}

func inGroups(groups, selected []string) bool {
	if len(selected) == 0 {
		return true
	}
	for _, want := range selected {
		if want == "all" {
			return true
		}
		for _, have := range groups {
			if have == want {
				return true
			}
		}
	}
	return false
}

func pairDelta(pair Pair, metric string) (float64, bool) {
	incumbent, okI := pair.Incumbent.Metrics[metric]
	candidate, okC := pair.Candidate.Metrics[metric]
	if !okI || !okC {
		return 0, false
	}
	return candidate - incumbent, true
}

func sortedKeys(values map[string]float64) []string {
	keys := make([]string, 0, len(values))
	for key := range values {
		keys = append(keys, key)
	}
	sort.Strings(keys)
	return keys
}

func mk(phase Phase, name string, passed bool, message string) Check {
	return Check{Phase: phase, Name: name, Passed: passed, Message: message}
}
