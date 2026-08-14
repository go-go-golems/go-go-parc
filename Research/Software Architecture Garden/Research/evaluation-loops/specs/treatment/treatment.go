// Package treatment is a research prototype for generic treatment-exercise
// witnessing: deciding, from an observed execution trace, whether a declared
// mechanism mutation was causally live in one arm of a paired experiment.
//
// It generalizes the product-specific implementation in CoinVault
// (cmd/coinvault/cmds/knowledge_ragopt_treatment.go and
// evaluateGECRagoptDefaultResultsTreatment in knowledge_ragopt.go) into three
// pure, product-neutral obligations:
//
//  1. Contract admission: a treatment contract names one registered mechanism,
//     declares exactly two arms whose mechanism-relevant parameters differ,
//     and lists the mechanism's canonical check set exactly — no check can be
//     silently dropped or smuggled in.
//  2. Exercise evaluation: a pure function maps (contract, arm, case, trace)
//     to a report of per-check evidence; Exercised is the conjunction of all
//     checks and nothing else.
//  3. Report validation: a report is internally coherent (Exercised equals
//     the conjunction; non-applicable reports carry no evidence) and matches
//     its contract's exact check set.
//
// The package deliberately has no I/O, no clock, and no dependencies: it is
// the deterministic kernel a harness such as Ragopt could adopt. What remains
// product-owned is the trace vocabulary (which observation fields exist and
// what they mean) and the mechanism definitions themselves.
package treatment

import (
	"errors"
	"fmt"
	"sort"
	"strings"
)

// ReportAPIVersion identifies the report schema of this prototype.
const ReportAPIVersion = "treatment-exercise-research/v1"

// Case is the minimal case metadata applicability predicates may consult.
// Labels generalize CoinVault's required-tool / evidence-group / eligible-ID
// eligibility sources without importing product semantics.
type Case struct {
	ID     string
	Labels map[string][]string
}

// Observation is one observed application point of a mechanism during a cell
// (in CoinVault: one knowledge_search call with its resolved limit provenance
// and semantic identities). Values are product-projected observed facts.
type Observation struct {
	Point  string
	Values map[string]string
}

// Trace is the observed evidence for one cell: cell-scoped facts (for example
// the digest of the actually-installed prompt suffix) plus the ordered word of
// per-point observations.
type Trace struct {
	Cell         map[string]string
	Observations []Observation
}

// ArmDeclaration carries the declared mechanism parameters for one arm.
type ArmDeclaration struct {
	Name       string
	Parameters map[string]string
}

// Contract is the declarative treatment contract for one candidate.
type Contract struct {
	Mechanism  string
	Arms       map[string]ArmDeclaration
	Invariants map[string]string
	Checks     []string
}

// Evidence is one check's expected/observed/passed record. Expected and
// Observed are human-auditable strings, never bare booleans, following the
// CoinVault convention that a failed check must explain itself.
type Evidence struct {
	Name     string
	Expected string
	Observed string
	Passed   bool
}

// Report is the generic treatment-exercise report proposed for inclusion in a
// Ragopt-style cell contract.
type Report struct {
	APIVersion string
	Mechanism  string
	Arm        string
	Applicable bool
	Exercised  bool
	Checks     []Evidence
}

// CheckSpec is one named pure predicate over declared arm parameters,
// contract invariants, and the observed trace.
type CheckSpec struct {
	Name string
	Eval func(arm ArmDeclaration, invariants map[string]string, trace Trace) Evidence
}

// MechanismSpec defines one mechanism: its canonical exact check set, its
// applicability predicate, and its arms-must-differ rule.
type MechanismSpec struct {
	Name         string
	Checks       []CheckSpec
	Applicable   func(c Case) bool
	ValidateArms func(incumbent, challenger ArmDeclaration) error
}

// Registry maps mechanism names to specifications. Products own their
// registry contents; the kernel owns only the admission and evaluation rules.
type Registry map[string]MechanismSpec

// Arm role names, mirroring Ragopt's fixed two-arm design.
const (
	ArmIncumbent  = "incumbent"
	ArmChallenger = "challenger"
)

func canonicalSet(names []string) string {
	sorted := append([]string(nil), names...)
	sort.Strings(sorted)
	return strings.Join(sorted, "\x00")
}

// AdmitContract enforces the contract admission obligations. It returns the
// resolved mechanism on success so evaluation cannot race a registry change.
func AdmitContract(contract Contract, registry Registry) (MechanismSpec, error) {
	spec, ok := registry[contract.Mechanism]
	if !ok {
		return MechanismSpec{}, fmt.Errorf("unknown treatment mechanism %q", contract.Mechanism)
	}
	if len(contract.Arms) != 2 {
		return MechanismSpec{}, errors.New("treatment contract requires exactly incumbent and challenger arms")
	}
	incumbent, ok := contract.Arms[ArmIncumbent]
	if !ok {
		return MechanismSpec{}, errors.New("treatment contract incumbent arm is missing")
	}
	challenger, ok := contract.Arms[ArmChallenger]
	if !ok {
		return MechanismSpec{}, errors.New("treatment contract challenger arm is missing")
	}
	if spec.ValidateArms != nil {
		if err := spec.ValidateArms(incumbent, challenger); err != nil {
			return MechanismSpec{}, fmt.Errorf("treatment contract arms invalid: %w", err)
		}
	}
	wanted := make([]string, 0, len(spec.Checks))
	seen := map[string]struct{}{}
	for _, check := range spec.Checks {
		if _, dup := seen[check.Name]; dup {
			return MechanismSpec{}, fmt.Errorf("mechanism %q declares duplicate check %q", spec.Name, check.Name)
		}
		seen[check.Name] = struct{}{}
		wanted = append(wanted, check.Name)
	}
	if canonicalSet(contract.Checks) != canonicalSet(wanted) {
		sort.Strings(wanted)
		return MechanismSpec{}, fmt.Errorf("treatment contract checks must be exactly %v", wanted)
	}
	return spec, nil
}

// Evaluate is the pure exercise decision. It never consults anything outside
// its arguments. A non-applicable case yields Applicable=false, no checks,
// and Exercised=false; an applicable case yields one Evidence per canonical
// check with Exercised as the conjunction.
func Evaluate(contract Contract, registry Registry, armName string, c Case, trace Trace) (Report, error) {
	spec, err := AdmitContract(contract, registry)
	if err != nil {
		return Report{}, err
	}
	arm, ok := contract.Arms[armName]
	if !ok {
		return Report{}, fmt.Errorf("treatment evaluation arm %q is absent from contract", armName)
	}
	report := Report{
		APIVersion: ReportAPIVersion,
		Mechanism:  contract.Mechanism,
		Arm:        armName,
		Checks:     []Evidence{},
	}
	if spec.Applicable != nil && !spec.Applicable(c) {
		return report, nil
	}
	report.Applicable = true
	report.Exercised = true
	for _, check := range spec.Checks {
		evidence := check.Eval(arm, contract.Invariants, trace)
		evidence.Name = check.Name
		report.Checks = append(report.Checks, evidence)
		if !evidence.Passed {
			report.Exercised = false
		}
	}
	return report, nil
}

// ValidateReport checks a report's internal coherence and its agreement with
// the contract. It exists so a serialized report crossing a process or
// storage boundary can be re-admitted rather than trusted; a forged
// Exercised flag or a dropped check is rejected here even if the producing
// process was compromised or buggy.
func ValidateReport(report Report, contract Contract, registry Registry) error {
	if report.APIVersion != ReportAPIVersion {
		return fmt.Errorf("unsupported treatment report API version %q", report.APIVersion)
	}
	if report.Mechanism != contract.Mechanism {
		return fmt.Errorf("treatment report mechanism %q differs from contract %q", report.Mechanism, contract.Mechanism)
	}
	if _, err := AdmitContract(contract, registry); err != nil {
		return err
	}
	if _, ok := contract.Arms[report.Arm]; !ok {
		return fmt.Errorf("treatment report arm %q is absent from contract", report.Arm)
	}
	if !report.Applicable {
		if report.Exercised || len(report.Checks) != 0 {
			return errors.New("non-applicable treatment report must not claim exercise evidence")
		}
		return nil
	}
	if len(report.Checks) == 0 {
		return errors.New("applicable treatment report requires at least one exercise check")
	}
	names := make([]string, 0, len(report.Checks))
	seen := map[string]struct{}{}
	conjunction := true
	for _, check := range report.Checks {
		name := strings.TrimSpace(check.Name)
		if name == "" || strings.TrimSpace(check.Expected) == "" || strings.TrimSpace(check.Observed) == "" {
			return errors.New("treatment report checks require name, expected, and observed values")
		}
		if _, dup := seen[name]; dup {
			return fmt.Errorf("duplicate treatment report check %q", name)
		}
		seen[name] = struct{}{}
		names = append(names, name)
		conjunction = conjunction && check.Passed
	}
	if canonicalSet(names) != canonicalSet(contract.Checks) {
		return fmt.Errorf("treatment report checks %v differ from contract %v", names, contract.Checks)
	}
	if report.Exercised != conjunction {
		return fmt.Errorf("treatment exercised=%t disagrees with check conjunction=%t", report.Exercised, conjunction)
	}
	return nil
}

// Applicability helpers covering CoinVault's three eligibility shapes.

// ApplicableAlways applies the mechanism to every case (prompt treatments).
func ApplicableAlways(Case) bool { return true }

// ApplicableWhenLabelContains applies when the case carries value under key
// (generalizing "case requires tool knowledge_search").
func ApplicableWhenLabelContains(key, value string) func(Case) bool {
	return func(c Case) bool {
		for _, entry := range c.Labels[key] {
			if entry == value {
				return true
			}
		}
		return false
	}
}

// ApplicableToCaseIDs applies only to an explicit eligible-ID list
// (comparison treatments).
func ApplicableToCaseIDs(ids ...string) func(Case) bool {
	eligible := map[string]struct{}{}
	for _, id := range ids {
		eligible[id] = struct{}{}
	}
	return func(c Case) bool {
		_, ok := eligible[c.ID]
		return ok
	}
}
