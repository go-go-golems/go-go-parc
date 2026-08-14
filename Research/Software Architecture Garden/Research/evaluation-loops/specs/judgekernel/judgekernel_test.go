package judgekernel

import (
	"context"
	"encoding/json"
	"fmt"
	"math"
	"strings"
	"testing"
)

func mustUniverse(t *testing.T, labels ...EvidenceLabel) LabelUniverse {
	t.Helper()
	universe, err := NewLabelUniverse(labels...)
	if err != nil {
		t.Fatalf("NewLabelUniverse: %v", err)
	}
	return universe
}

// revalidate is an independent re-implementation of every admission rule.
// It shares no code with Admit; the property tests use it to check that
// whatever Admit accepts satisfies the rules.
func revalidate(statements []string, universe LabelUniverse, admitted Admitted) []string {
	var violations []string
	verdicts := admitted.Verdicts()
	if len(verdicts) != len(statements) {
		violations = append(violations, fmt.Sprintf("count: %d verdicts for %d statements", len(verdicts), len(statements)))
	}
	if math.IsNaN(admitted.Relevance()) || math.IsInf(admitted.Relevance(), 0) || admitted.Relevance() < 0 || admitted.Relevance() > 1 {
		violations = append(violations, fmt.Sprintf("relevance out of range: %g", admitted.Relevance()))
	}
	for i, verdict := range verdicts {
		if i < len(statements) && verdict.Statement != statements[i] {
			violations = append(violations, fmt.Sprintf("verdict %d bound to wrong statement", i+1))
		}
		if strings.TrimSpace(verdict.Reason) == "" {
			violations = append(violations, fmt.Sprintf("verdict %d blank reason", i+1))
		}
		seen := map[EvidenceLabel]bool{}
		for _, label := range verdict.Evidence {
			if !universe.Contains(label) {
				violations = append(violations, fmt.Sprintf("verdict %d unknown label %q", i+1, label))
			}
			if seen[label] {
				violations = append(violations, fmt.Sprintf("verdict %d duplicate label %q", i+1, label))
			}
			seen[label] = true
		}
		if verdict.Supported && len(verdict.Evidence) == 0 {
			violations = append(violations, fmt.Sprintf("verdict %d supported without evidence", i+1))
		}
	}
	return violations
}

func TestAdmitAcceptsValidPayload(t *testing.T) {
	universe := mustUniverse(t, "E1", "SQL1")
	statements := []string{"Proof coins are struck twice.", "Bars carry lower premiums."}
	raw := "```json\n" + `{"verdicts":[
		{"statement":1,"supported":true,"evidence_ids":["E1"],"reason":"entailed by E1"},
		{"statement":2,"supported":false,"evidence_ids":[],"reason":"not in evidence"}],
		"addresses_question":0.8,"abstained":false}` + "\n```"
	admitted, err := Admit(statements, universe, raw)
	if err != nil {
		t.Fatalf("Admit: %v", err)
	}
	if !admitted.Valid() {
		t.Fatal("admitted value not marked valid")
	}
	if violations := revalidate(statements, universe, admitted); len(violations) != 0 {
		t.Fatalf("violations: %v", violations)
	}
	score := ScoreCell(admitted)
	if score.Faithfulness != (Fraction{Numerator: 1, Denominator: 2}) {
		t.Fatalf("faithfulness = %+v", score.Faithfulness)
	}
	if value, defined := score.Faithfulness.Value(); !defined || value != 0.5 {
		t.Fatalf("faithfulness value = %v %v", value, defined)
	}
	if score.Status != StatusJudged || score.Relevance != 0.8 || score.Abstained {
		t.Fatalf("score = %+v", score)
	}
	if score.Verdicts[0].Statement != statements[0] {
		t.Fatalf("statement binding lost: %+v", score.Verdicts[0])
	}
}

func TestAdmitRejectsEveryStructuralRule(t *testing.T) {
	universe := mustUniverse(t, "E1")
	statements := []string{"a", "b"}
	valid := func(mutate func(payload map[string]any)) string {
		payload := map[string]any{
			"verdicts": []map[string]any{
				{"statement": 1, "supported": true, "evidence_ids": []string{"E1"}, "reason": "yes"},
				{"statement": 2, "supported": false, "evidence_ids": []string{}, "reason": "no"},
			},
			"addresses_question": 0.9,
			"abstained":          false,
		}
		if mutate != nil {
			mutate(payload)
		}
		encoded, err := json.Marshal(payload)
		if err != nil {
			t.Fatal(err)
		}
		return string(encoded)
	}
	verdict := func(payload map[string]any, index int) map[string]any {
		return payload["verdicts"].([]map[string]any)[index]
	}
	cases := map[AdmissionReason]string{
		ReasonNoJSONObject:         "no braces here",
		ReasonMalformedJSON:        `{"verdicts": [}`,
		ReasonVerdictCountMismatch: valid(func(p map[string]any) { p["verdicts"] = p["verdicts"].([]map[string]any)[:1] }),
		ReasonRelevanceMissing:     valid(func(p map[string]any) { delete(p, "addresses_question") }),
		ReasonRelevanceOutOfRange:  valid(func(p map[string]any) { p["addresses_question"] = 1.1 }),
		ReasonAbstainedMissing:     valid(func(p map[string]any) { delete(p, "abstained") }),
		ReasonStatementOutOfOrder:  valid(func(p map[string]any) { verdict(p, 1)["statement"] = 3 }),
		ReasonSupportedMissing:     valid(func(p map[string]any) { delete(verdict(p, 0), "supported") }),
		ReasonReasonMissing:        valid(func(p map[string]any) { verdict(p, 1)["reason"] = "  " }),
		ReasonUnknownEvidence:      valid(func(p map[string]any) { verdict(p, 0)["evidence_ids"] = []string{"E999"} }),
		ReasonDuplicateEvidence:    valid(func(p map[string]any) { verdict(p, 0)["evidence_ids"] = []string{"E1", "E1"} }),
		ReasonSupportedWithoutEvidence: valid(func(p map[string]any) {
			verdict(p, 0)["evidence_ids"] = []string{}
		}),
	}
	for reason, raw := range cases {
		t.Run(string(reason), func(t *testing.T) {
			_, err := Admit(statements, universe, raw)
			var admissionErr *AdmissionError
			if !asError(err, &admissionErr) {
				t.Fatalf("expected AdmissionError, got %v", err)
			}
			if admissionErr.Reason != reason {
				t.Fatalf("reason = %s, want %s (err: %v)", admissionErr.Reason, reason, err)
			}
		})
	}
}

func TestAdmitRelevanceNaNRejected(t *testing.T) {
	// NaN cannot travel through encoding/json literally; the raw payload
	// carries it as a string the decoder rejects, which is malformed JSON —
	// the non-finite guard is exercised through large exponent floats too.
	universe := mustUniverse(t, "E1")
	raw := `{"verdicts":[],"addresses_question":1e400,"abstained":false}`
	_, err := Admit(nil, universe, raw)
	if err == nil {
		t.Fatal("expected rejection for non-finite relevance")
	}
}

func TestAdmitZeroStatementsRequiresEmptyVerdicts(t *testing.T) {
	universe := mustUniverse(t, "E1")
	admitted, err := Admit(nil, universe, `{"verdicts":[],"addresses_question":0.9,"abstained":true}`)
	if err != nil {
		t.Fatalf("Admit: %v", err)
	}
	score := ScoreCell(admitted)
	if score.Status != StatusVacuousAbstention {
		t.Fatalf("status = %s", score.Status)
	}
	if _, defined := score.Faithfulness.Value(); defined {
		t.Fatal("vacuous faithfulness must be undefined, not 1.0")
	}
	if _, err := Admit(nil, universe, `{"verdicts":[{"statement":1,"supported":false,"reason":"x"}],"addresses_question":0.9,"abstained":true}`); err == nil {
		t.Fatal("expected count mismatch for phantom verdict")
	}
}

func TestAdmitStatementsTrimsDropsAndDedupes(t *testing.T) {
	statements, err := AdmitStatements("prose first\n```json\n{\"statements\": [\" a \", \"\", \"b\", \"a\"]}\n```")
	if err != nil {
		t.Fatalf("AdmitStatements: %v", err)
	}
	if len(statements) != 2 || statements[0] != "a" || statements[1] != "b" {
		t.Fatalf("statements = %v", statements)
	}
	if _, err := AdmitStatements(`{}`); err == nil {
		t.Fatal("expected statements_missing")
	}
	empty, err := AdmitStatements(`{"statements": []}`)
	if err != nil || len(empty) != 0 {
		t.Fatalf("empty list must be legal abstention signal: %v %v", empty, err)
	}
}

func TestSummarizeDenominatorDiscipline(t *testing.T) {
	scores := []Score{
		{Status: StatusJudged, Faithfulness: Fraction{1, 2}, Relevance: 0.8},
		{Status: StatusJudged, Faithfulness: Fraction{2, 2}, Relevance: 0.6, Abstained: true},
		{Status: StatusVacuousAbstention, Faithfulness: Fraction{0, 0}, Relevance: 0.9, Abstained: true},
	}
	summary := Summarize(scores)
	if summary.Cells != 3 || summary.Judged != 2 || summary.VacuousAbstentions != 1 || summary.JudgeAbstentions != 2 {
		t.Fatalf("summary = %+v", summary)
	}
	// Only the first cell may contribute to faithfulness: the second is
	// judge-abstained, the third vacuous.
	if !summary.Faithfulness.Defined || summary.Faithfulness.Denominator != 1 || summary.Faithfulness.Mean != 0.5 {
		t.Fatalf("faithfulness = %+v", summary.Faithfulness)
	}
	if summary.Relevance.Denominator != 3 {
		t.Fatalf("relevance = %+v", summary.Relevance)
	}
	empty := Summarize(nil)
	if empty.Faithfulness.Defined || empty.Relevance.Defined {
		t.Fatalf("empty population must be undefined, got %+v", empty)
	}
}

func TestRunWithRepairExactlyOnce(t *testing.T) {
	universe := mustUniverse(t, "E1")
	statements := []string{"a"}
	step := func(ctx context.Context, generate Generator) (Admitted, error) {
		raw, err := generate(ctx, "verdicts prompt")
		if err != nil {
			return Admitted{}, err
		}
		return Admit(statements, universe, raw)
	}
	t.Run("repairs one structural failure", func(t *testing.T) {
		calls := 0
		generate := func(_ context.Context, prompt string) (string, error) {
			calls++
			if !strings.Contains(prompt, "structurally invalid") {
				return `{"verdicts":[{"statement":1,"supported":true,"evidence_ids":["E999"],"reason":"x"}],"addresses_question":1,"abstained":false}`, nil
			}
			return `{"verdicts":[{"statement":1,"supported":true,"evidence_ids":["E1"],"reason":"x"}],"addresses_question":1,"abstained":false}`, nil
		}
		budget := &RepairBudget{}
		admitted, err := RunWithRepair(context.Background(), budget, generate, step)
		if err != nil || calls != 2 || !budget.Used() {
			t.Fatalf("calls=%d used=%v err=%v", calls, budget.Used(), err)
		}
		if violations := revalidate(statements, universe, admitted); len(violations) != 0 {
			t.Fatalf("violations after repair: %v", violations)
		}
	})
	t.Run("second structural failure is final", func(t *testing.T) {
		calls := 0
		generate := func(context.Context, string) (string, error) {
			calls++
			return `{"verdicts":[],"addresses_question":1,"abstained":false}`, nil
		}
		budget := &RepairBudget{}
		_, err := RunWithRepair(context.Background(), budget, generate, step)
		if err == nil || calls != 2 {
			t.Fatalf("calls=%d err=%v", calls, err)
		}
	})
	t.Run("provider failure never repairs", func(t *testing.T) {
		calls := 0
		generate := func(context.Context, string) (string, error) {
			calls++
			return "", fmt.Errorf("provider unavailable")
		}
		budget := &RepairBudget{}
		_, err := RunWithRepair(context.Background(), budget, generate, step)
		if err == nil || calls != 1 || budget.Used() {
			t.Fatalf("calls=%d used=%v err=%v", calls, budget.Used(), err)
		}
	})
	t.Run("budget shared across steps", func(t *testing.T) {
		budget := &RepairBudget{}
		if !budget.TryUse() || budget.TryUse() {
			t.Fatal("budget must be consumable exactly once")
		}
		calls := 0
		generate := func(context.Context, string) (string, error) {
			calls++
			return `not json`, nil
		}
		_, err := RunWithRepair(context.Background(), budget, generate, step)
		if err == nil || calls != 1 {
			t.Fatalf("exhausted budget must not repair: calls=%d err=%v", calls, err)
		}
	})
}

func TestPopulationKeySeparatesPopulations(t *testing.T) {
	base := PopulationKey{Step: "judge", PromptVersion: "v2", Model: "m"}
	prompt := "same prompt"
	keys := map[string]string{
		"base":       base.CacheKey(prompt),
		"prompt":     base.CacheKey(prompt + "!"),
		"version":    PopulationKey{Step: "judge", PromptVersion: "v3", Model: "m"}.CacheKey(prompt),
		"model":      PopulationKey{Step: "judge", PromptVersion: "v2", Model: "m2"}.CacheKey(prompt),
		"step":       PopulationKey{Step: "judge2", PromptVersion: "v2", Model: "m"}.CacheKey(prompt),
		"base-again": base.CacheKey(prompt),
	}
	if keys["base"] != keys["base-again"] {
		t.Fatal("cache key must be deterministic")
	}
	seen := map[string]string{}
	for name, key := range keys {
		if name == "base-again" {
			continue
		}
		if prior, duplicate := seen[key]; duplicate {
			t.Fatalf("key collision between %s and %s", prior, name)
		}
		seen[key] = name
	}
}

func TestRequestsEncodeInformationHiding(t *testing.T) {
	statementsBody := StatementsRequest{Question: "q", Answer: "the answer"}.Render()
	if strings.Contains(statementsBody, "Evidence") {
		t.Fatal("statements request must not carry evidence")
	}
	request := VerdictsRequest{
		Question:   "q",
		Statements: []string{"claim"},
		Evidence:   []LabeledEvidence{{Label: "E1", Body: "body"}},
	}
	verdictsBody := request.Render()
	if strings.Contains(verdictsBody, "the answer") {
		t.Fatal("verdicts request must not carry the answer")
	}
	universe, err := request.Universe()
	if err != nil || !universe.Contains("E1") || universe.Size() != 1 {
		t.Fatalf("universe = %+v err=%v", universe, err)
	}
	empty := VerdictsRequest{Question: "q"}.Render()
	if !strings.Contains(empty, "(no evidence was retrieved)") {
		t.Fatalf("empty evidence must be explicit: %s", empty)
	}
}
