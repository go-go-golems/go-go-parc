package treatment

import (
	"errors"
	"fmt"
	"strconv"
)

// This file defines two exemplar mechanisms mirroring CoinVault's two hardest
// treatment shapes. They are library exemplars, not a closed vocabulary:
// products register their own MechanismSpecs.
//
// Exemplar 1 — "fallback_default": a configuration default that only
// determines behavior when the caller does not override it. This is the
// mechanism whose neutralization produced the historical v1–v6 failure
// ("the model supplied an explicit limit on every call"). Its check set is a
// direct generalization of CoinVault's default-results checks.
//
// Exemplar 2 — "cell_digest": a cell-scoped installed text (prompt suffix)
// whose exercise is proven by the digest of what was actually installed.

// Observation value keys used by the fallback_default exemplar.
const (
	ObsConfiguredDefault = "configured_default"
	ObsEffectiveLimit    = "effective_limit"
	ObsLimitSource       = "limit_source"
	ObsResultObserved    = "result_observed"

	LimitSourceDefault = "default"
)

// Arm parameter keys.
const (
	ParamConfiguredDefault = "configured_default"
	ParamDigest            = "digest"
)

// Cell fact keys.
const CellDigest = "digest"

func armInt(arm ArmDeclaration, key string) (int, bool) {
	raw, ok := arm.Parameters[key]
	if !ok {
		return 0, false
	}
	value, err := strconv.Atoi(raw)
	if err != nil {
		return 0, false
	}
	return value, true
}

// FallbackDefaultMechanism proves that a mutated fallback default was causally
// live: at least one observation resolved its effective value from the
// fallback source at the arm's declared value, every observation was
// configured with the arm's value, every observation produced a result, and
// every observation carried the contract's invariant identities.
func FallbackDefaultMechanism(applicable func(Case) bool, identityKeys ...string) MechanismSpec {
	return MechanismSpec{
		Name:       "fallback_default",
		Applicable: applicable,
		ValidateArms: func(incumbent, challenger ArmDeclaration) error {
			left, okLeft := armInt(incumbent, ParamConfiguredDefault)
			right, okRight := armInt(challenger, ParamConfiguredDefault)
			if !okLeft || !okRight || left <= 0 || right <= 0 {
				return errors.New("both arms require a positive configured default")
			}
			if left == right {
				return errors.New("arms must declare different defaults")
			}
			return nil
		},
		Checks: []CheckSpec{
			{
				Name: "call_observed",
				Eval: func(_ ArmDeclaration, _ map[string]string, trace Trace) Evidence {
					return Evidence{
						Expected: "at least 1",
						Observed: fmt.Sprintf("%d", len(trace.Observations)),
						Passed:   len(trace.Observations) > 0,
					}
				},
			},
			{
				Name: "configured_matches_arm",
				Eval: func(arm ArmDeclaration, _ map[string]string, trace Trace) Evidence {
					expected, _ := armInt(arm, ParamConfiguredDefault)
					matches := len(trace.Observations) > 0
					for _, obs := range trace.Observations {
						if obs.Values[ObsConfiguredDefault] != strconv.Itoa(expected) {
							matches = false
						}
					}
					return Evidence{
						Expected: strconv.Itoa(expected),
						Observed: fmt.Sprintf("all %d observations", len(trace.Observations)),
						Passed:   matches,
					}
				},
			},
			{
				Name: "fallback_applied",
				Eval: func(arm ArmDeclaration, _ map[string]string, trace Trace) Evidence {
					expected, _ := armInt(arm, ParamConfiguredDefault)
					applied := 0
					for _, obs := range trace.Observations {
						if obs.Values[ObsLimitSource] == LimitSourceDefault && obs.Values[ObsEffectiveLimit] == strconv.Itoa(expected) {
							applied++
						}
					}
					return Evidence{
						Expected: "at least 1",
						Observed: fmt.Sprintf("%d", applied),
						Passed:   applied > 0,
					}
				},
			},
			{
				Name: "results_observed",
				Eval: func(_ ArmDeclaration, _ map[string]string, trace Trace) Evidence {
					all := len(trace.Observations) > 0
					for _, obs := range trace.Observations {
						if obs.Values[ObsResultObserved] != "true" {
							all = false
						}
					}
					return Evidence{
						Expected: "all observations",
						Observed: fmt.Sprintf("%t", all),
						Passed:   all,
					}
				},
			},
			{
				Name: "identities_match",
				Eval: func(_ ArmDeclaration, invariants map[string]string, trace Trace) Evidence {
					all := len(trace.Observations) > 0
					for _, obs := range trace.Observations {
						for _, key := range identityKeys {
							if obs.Values[key] != invariants[key] {
								all = false
							}
						}
					}
					return Evidence{
						Expected: "declared invariant identities on every observation",
						Observed: fmt.Sprintf("%t", all),
						Passed:   all,
					}
				},
			},
		},
	}
}

// CellDigestMechanism proves that a cell-scoped installed text matched the
// arm's declaration: the observed digest equals the declared digest, and
// enablement agrees with digest presence in both directions.
func CellDigestMechanism() MechanismSpec {
	return MechanismSpec{
		Name:       "cell_digest",
		Applicable: ApplicableAlways,
		ValidateArms: func(incumbent, challenger ArmDeclaration) error {
			if incumbent.Parameters[ParamDigest] == challenger.Parameters[ParamDigest] {
				return errors.New("arms must declare distinct digests")
			}
			return nil
		},
		Checks: []CheckSpec{
			{
				Name: "digest_matches_arm",
				Eval: func(arm ArmDeclaration, _ map[string]string, trace Trace) Evidence {
					expected := arm.Parameters[ParamDigest]
					observed := trace.Cell[CellDigest]
					return Evidence{
						Expected: display(expected),
						Observed: display(observed),
						Passed:   expected == observed,
					}
				},
			},
			{
				Name: "applied",
				Eval: func(arm ArmDeclaration, _ map[string]string, trace Trace) Evidence {
					enabled := arm.Parameters[ParamDigest] != ""
					observed := trace.Cell[CellDigest]
					return Evidence{
						Expected: fmt.Sprintf("enabled=%t", enabled),
						Observed: fmt.Sprintf("digest=%s", display(observed)),
						Passed:   (enabled && observed != "") || (!enabled && observed == ""),
					}
				},
			},
		},
	}
}

func display(value string) string {
	if value == "" {
		return "none"
	}
	return value
}
