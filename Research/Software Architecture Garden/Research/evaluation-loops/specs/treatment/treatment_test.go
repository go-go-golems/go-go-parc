package treatment

import (
	"strings"
	"testing"
)

// The test fixtures replay the shapes recorded in the CoinVault Garden study
// and GEC-RAG-OPT-002's textbook §8 ("Configuration Is Not Behavior"). The
// incumbent declares default 5, the challenger 8, mirroring the historical
// default-results candidates.

func fallbackRegistry() Registry {
	spec := FallbackDefaultMechanism(
		ApplicableWhenLabelContains("required_tools", "knowledge_search"),
		"retrieval_policy_id", "evidence_ledger_id",
	)
	return Registry{spec.Name: spec}
}

func fallbackContract() Contract {
	return Contract{
		Mechanism: "fallback_default",
		Arms: map[string]ArmDeclaration{
			ArmIncumbent:  {Name: ArmIncumbent, Parameters: map[string]string{ParamConfiguredDefault: "5"}},
			ArmChallenger: {Name: ArmChallenger, Parameters: map[string]string{ParamConfiguredDefault: "8"}},
		},
		Invariants: map[string]string{
			"retrieval_policy_id": "gec-retrieval/v1",
			"evidence_ledger_id":  "gec-evidence-ledger/v1",
		},
		Checks: []string{"call_observed", "configured_matches_arm", "fallback_applied", "results_observed", "identities_match"},
	}
}

func knowledgeCase() Case {
	return Case{ID: "feedback-knowledge-proof-coins", Labels: map[string][]string{"required_tools": {"knowledge_search"}}}
}

func observation(configured, effective, source string) Observation {
	return Observation{
		Point: "knowledge_search",
		Values: map[string]string{
			ObsConfiguredDefault:  configured,
			ObsEffectiveLimit:     effective,
			ObsLimitSource:        source,
			ObsResultObserved:     "true",
			"retrieval_policy_id": "gec-retrieval/v1",
			"evidence_ledger_id":  "gec-evidence-ledger/v1",
		},
	}
}

func TestExercisedFallbackDefault(t *testing.T) {
	trace := Trace{Observations: []Observation{observation("8", "8", LimitSourceDefault)}}
	report, err := Evaluate(fallbackContract(), fallbackRegistry(), ArmChallenger, knowledgeCase(), trace)
	if err != nil {
		t.Fatalf("evaluate: %v", err)
	}
	if !report.Applicable || !report.Exercised {
		t.Fatalf("expected applicable and exercised, got %+v", report)
	}
	if err := ValidateReport(report, fallbackContract(), fallbackRegistry()); err != nil {
		t.Fatalf("validate: %v", err)
	}
}

// TestNeutralizedTreatmentIsNotExercised replays the historical v1–v6 failure:
// the challenger declares default 8, the configuration is installed, but the
// model supplies an explicit limit of 5 on every call, so the fallback never
// determines behavior. The checker must return not-exercised, and the failed
// check must be fallback_applied specifically.
func TestNeutralizedTreatmentIsNotExercised(t *testing.T) {
	trace := Trace{Observations: []Observation{
		observation("8", "5", "explicit"),
		observation("8", "5", "explicit"),
	}}
	report, err := Evaluate(fallbackContract(), fallbackRegistry(), ArmChallenger, knowledgeCase(), trace)
	if err != nil {
		t.Fatalf("evaluate: %v", err)
	}
	if !report.Applicable {
		t.Fatalf("expected applicable")
	}
	if report.Exercised {
		t.Fatalf("neutralized treatment must not be exercised: %+v", report)
	}
	failed := map[string]bool{}
	for _, check := range report.Checks {
		if !check.Passed {
			failed[check.Name] = true
		}
	}
	if !failed["fallback_applied"] || len(failed) != 1 {
		t.Fatalf("expected exactly fallback_applied to fail, got %v", failed)
	}
	if err := ValidateReport(report, fallbackContract(), fallbackRegistry()); err != nil {
		t.Fatalf("a truthful not-exercised report must validate: %v", err)
	}
}

func TestIdentityMismatchFailsExercise(t *testing.T) {
	obs := observation("8", "8", LimitSourceDefault)
	obs.Values["retrieval_policy_id"] = "gec-retrieval/v2-drifted"
	report, err := Evaluate(fallbackContract(), fallbackRegistry(), ArmChallenger, knowledgeCase(), Trace{Observations: []Observation{obs}})
	if err != nil {
		t.Fatalf("evaluate: %v", err)
	}
	if report.Exercised {
		t.Fatalf("identity drift must fail exercise")
	}
}

func TestNotApplicableCaseCarriesNoEvidence(t *testing.T) {
	sqlOnly := Case{ID: "feedback-schema-orders", Labels: map[string][]string{"required_tools": {"sql_query"}}}
	report, err := Evaluate(fallbackContract(), fallbackRegistry(), ArmIncumbent, sqlOnly, Trace{})
	if err != nil {
		t.Fatalf("evaluate: %v", err)
	}
	if report.Applicable || report.Exercised || len(report.Checks) != 0 {
		t.Fatalf("non-applicable report must be empty: %+v", report)
	}
	if err := ValidateReport(report, fallbackContract(), fallbackRegistry()); err != nil {
		t.Fatalf("validate: %v", err)
	}
}

func TestDroppedCheckIsRejected(t *testing.T) {
	contract := fallbackContract()
	kept := []string{}
	for _, name := range contract.Checks {
		if name != "fallback_applied" {
			kept = append(kept, name)
		}
	}
	contract.Checks = kept
	if _, err := AdmitContract(contract, fallbackRegistry()); err == nil {
		t.Fatalf("dropping fallback_applied must be rejected")
	} else if !strings.Contains(err.Error(), "must be exactly") {
		t.Fatalf("unexpected error: %v", err)
	}
}

func TestExtraCheckIsRejected(t *testing.T) {
	contract := fallbackContract()
	contract.Checks = append(contract.Checks, "vanity_check")
	if _, err := AdmitContract(contract, fallbackRegistry()); err == nil {
		t.Fatalf("adding an undeclared check must be rejected")
	}
}

func TestEqualArmsAreRejected(t *testing.T) {
	contract := fallbackContract()
	contract.Arms[ArmChallenger] = ArmDeclaration{Name: ArmChallenger, Parameters: map[string]string{ParamConfiguredDefault: "5"}}
	if _, err := AdmitContract(contract, fallbackRegistry()); err == nil {
		t.Fatalf("arms with equal defaults must be rejected")
	}
}

func TestForgedExercisedFlagIsRejected(t *testing.T) {
	trace := Trace{Observations: []Observation{observation("8", "5", "explicit")}}
	report, err := Evaluate(fallbackContract(), fallbackRegistry(), ArmChallenger, knowledgeCase(), trace)
	if err != nil {
		t.Fatalf("evaluate: %v", err)
	}
	report.Exercised = true // forge
	if err := ValidateReport(report, fallbackContract(), fallbackRegistry()); err == nil {
		t.Fatalf("forged exercised flag must be rejected")
	}
}

func TestNonApplicableReportClaimingEvidenceIsRejected(t *testing.T) {
	report := Report{
		APIVersion: ReportAPIVersion,
		Mechanism:  "fallback_default",
		Arm:        ArmIncumbent,
		Applicable: false,
		Exercised:  true,
	}
	if err := ValidateReport(report, fallbackContract(), fallbackRegistry()); err == nil {
		t.Fatalf("non-applicable report claiming exercise must be rejected")
	}
}

func TestCellDigestMechanism(t *testing.T) {
	spec := CellDigestMechanism()
	registry := Registry{spec.Name: spec}
	contract := Contract{
		Mechanism: "cell_digest",
		Arms: map[string]ArmDeclaration{
			ArmIncumbent:  {Name: ArmIncumbent, Parameters: map[string]string{ParamDigest: ""}},
			ArmChallenger: {Name: ArmChallenger, Parameters: map[string]string{ParamDigest: "sha256:abc"}},
		},
		Checks: []string{"digest_matches_arm", "applied"},
	}
	anyCase := Case{ID: "any"}

	// Challenger with the declared suffix installed: exercised.
	report, err := Evaluate(contract, registry, ArmChallenger, anyCase, Trace{Cell: map[string]string{CellDigest: "sha256:abc"}})
	if err != nil || !report.Exercised {
		t.Fatalf("installed digest must be exercised: %+v err=%v", report, err)
	}
	// Challenger whose suffix silently failed to install: not exercised.
	report, err = Evaluate(contract, registry, ArmChallenger, anyCase, Trace{Cell: map[string]string{}})
	if err != nil || report.Exercised {
		t.Fatalf("missing installed digest must not be exercised: %+v err=%v", report, err)
	}
	// Incumbent must prove absence too: a leaked suffix fails the incumbent.
	report, err = Evaluate(contract, registry, ArmIncumbent, anyCase, Trace{Cell: map[string]string{CellDigest: "sha256:abc"}})
	if err != nil || report.Exercised {
		t.Fatalf("leaked suffix into incumbent must not be exercised: %+v err=%v", report, err)
	}
}

func TestUnknownMechanismRejected(t *testing.T) {
	contract := fallbackContract()
	contract.Mechanism = "unregistered"
	if _, err := Evaluate(contract, fallbackRegistry(), ArmIncumbent, knowledgeCase(), Trace{}); err == nil {
		t.Fatalf("unknown mechanism must be rejected")
	}
}
