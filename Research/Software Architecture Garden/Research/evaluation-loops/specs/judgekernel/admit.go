package judgekernel

import (
	"encoding/json"
	"fmt"
	"math"
	"strings"
)

// AdmissionReason is the closed taxonomy of structural rejections. Each
// reason corresponds to exactly one rule in the admission relation; the
// taxonomy is the union of CoinVault's nine verdict-step rejections
// (internal/knowledge/judge.go:453-496) plus the parse-level rejections
// both implementations share.
type AdmissionReason string

const (
	ReasonNoJSONObject             AdmissionReason = "no_json_object"
	ReasonMalformedJSON            AdmissionReason = "malformed_json"
	ReasonStatementsMissing        AdmissionReason = "statements_missing"
	ReasonVerdictCountMismatch     AdmissionReason = "verdict_count_mismatch"
	ReasonRelevanceMissing         AdmissionReason = "relevance_missing"
	ReasonRelevanceOutOfRange      AdmissionReason = "relevance_out_of_range"
	ReasonAbstainedMissing         AdmissionReason = "abstained_missing"
	ReasonStatementOutOfOrder      AdmissionReason = "statement_out_of_order"
	ReasonSupportedMissing         AdmissionReason = "supported_missing"
	ReasonReasonMissing            AdmissionReason = "reason_missing"
	ReasonUnknownEvidence          AdmissionReason = "unknown_evidence"
	ReasonDuplicateEvidence        AdmissionReason = "duplicate_evidence"
	ReasonSupportedWithoutEvidence AdmissionReason = "supported_without_evidence"
)

// AdmissionError is a structural rejection of a judge payload. Only
// AdmissionError triggers the bounded repair; provider errors never do.
type AdmissionError struct {
	Reason AdmissionReason
	Detail string
}

func (e *AdmissionError) Error() string {
	return fmt.Sprintf("inadmissible judge payload (%s): %s", e.Reason, e.Detail)
}

func reject(reason AdmissionReason, format string, args ...any) error {
	return &AdmissionError{Reason: reason, Detail: fmt.Sprintf(format, args...)}
}

// IsAdmissionError reports whether err is a structural rejection.
func IsAdmissionError(err error) bool {
	var target *AdmissionError
	return asError(err, &target)
}

// asError is errors.As without importing errors twice across files.
func asError(err error, target **AdmissionError) bool {
	for err != nil {
		if e, ok := err.(*AdmissionError); ok {
			*target = e
			return true
		}
		unwrapper, ok := err.(interface{ Unwrap() error })
		if !ok {
			return false
		}
		err = unwrapper.Unwrap()
	}
	return false
}

// extractJSONObject is the fence-tolerant slice both implementations use:
// models wrap JSON in prose and code fences routinely.
func extractJSONObject(raw string) (string, error) {
	start := strings.Index(raw, "{")
	end := strings.LastIndex(raw, "}")
	if start < 0 || end <= start {
		return "", reject(ReasonNoJSONObject, "no JSON object in %.80q", raw)
	}
	return raw[start : end+1], nil
}

// AdmitStatements admits a raw step-1 payload. Statements are trimmed,
// empty entries are dropped, and duplicates are removed order-preserving —
// the rag-ttc discipline, adopted here because a duplicated statement
// double-counts in the faithfulness denominator. An empty admitted list is
// legal: it is the abstention signal, not an error.
func AdmitStatements(raw string) ([]string, error) {
	object, err := extractJSONObject(raw)
	if err != nil {
		return nil, err
	}
	var payload struct {
		Statements *[]string `json:"statements"`
	}
	if err := json.Unmarshal([]byte(object), &payload); err != nil {
		return nil, reject(ReasonMalformedJSON, "statements: %v", err)
	}
	if payload.Statements == nil {
		return nil, reject(ReasonStatementsMissing, "statements field is required")
	}
	seen := make(map[string]struct{}, len(*payload.Statements))
	statements := make([]string, 0, len(*payload.Statements))
	for _, statement := range *payload.Statements {
		statement = strings.TrimSpace(statement)
		if statement == "" {
			continue
		}
		if _, duplicate := seen[statement]; duplicate {
			continue
		}
		seen[statement] = struct{}{}
		statements = append(statements, statement)
	}
	return statements, nil
}

// Verdict is one admitted per-statement verdict. The statement text is bound
// in, so downstream consumers never index back into a parallel slice.
type Verdict struct {
	Statement string
	Supported bool
	Evidence  []EvidenceLabel
	Reason    string
}

// Admitted carries a validated verdict payload. It can be constructed only
// by Admit, so possession of an Admitted value is proof that every
// structural rule held. The zero value reports zero verdicts and relevance
// zero and is distinguishable by Valid().
type Admitted struct {
	valid     bool
	verdicts  []Verdict
	relevance float64
	abstained bool
}

// Valid reports whether this value was produced by Admit.
func (a Admitted) Valid() bool { return a.valid }

// Verdicts returns a copy of the admitted verdicts.
func (a Admitted) Verdicts() []Verdict {
	out := make([]Verdict, len(a.verdicts))
	copy(out, a.verdicts)
	return out
}

// Relevance is the judge's addresses-question rating, guaranteed finite and
// within [0,1] by admission.
func (a Admitted) Relevance() float64 { return a.relevance }

// Abstained is the judge's whole-answer abstention flag.
func (a Admitted) Abstained() bool { return a.abstained }

// rawVerdicts mirrors the wire schema. Every optional field is a pointer so
// absent and zero stay distinguishable — the CoinVault discipline.
type rawVerdicts struct {
	Verdicts []struct {
		Statement   int      `json:"statement"`
		Supported   *bool    `json:"supported"`
		EvidenceIDs []string `json:"evidence_ids"`
		Reason      string   `json:"reason"`
	} `json:"verdicts"`
	AddressesQuestion *float64 `json:"addresses_question"`
	Abstained         *bool    `json:"abstained"`
}

// Admit is the admission relation for step-2 payloads: it decides whether a
// raw judge response is admissible against the statement list and the
// evidence-label universe, and returns the validated value or a typed
// rejection. It is a pure function of its arguments.
//
// The rules, in check order:
//  1. the payload contains one JSON object (fence-tolerant);
//  2. the object parses against the wire schema;
//  3. verdict count equals statement count;
//  4. addresses_question is present, finite, and within [0,1];
//  5. abstained is present;
//  6. verdict i references statement i+1 (order and coverage);
//  7. every supported flag is present;
//  8. every reason is non-blank;
//  9. every cited label is in the universe;
//  10. no verdict cites a label twice;
//  11. supported verdicts cite at least one label.
func Admit(statements []string, universe LabelUniverse, raw string) (Admitted, error) {
	object, err := extractJSONObject(raw)
	if err != nil {
		return Admitted{}, err
	}
	var payload rawVerdicts
	if err := json.Unmarshal([]byte(object), &payload); err != nil {
		return Admitted{}, reject(ReasonMalformedJSON, "verdicts: %v", err)
	}
	if len(payload.Verdicts) != len(statements) {
		return Admitted{}, reject(ReasonVerdictCountMismatch, "got %d verdicts for %d statements", len(payload.Verdicts), len(statements))
	}
	if payload.AddressesQuestion == nil {
		return Admitted{}, reject(ReasonRelevanceMissing, "addresses_question is required")
	}
	relevance := *payload.AddressesQuestion
	if math.IsNaN(relevance) || math.IsInf(relevance, 0) || relevance < 0 || relevance > 1 {
		return Admitted{}, reject(ReasonRelevanceOutOfRange, "addresses_question must be within [0,1], got %g", relevance)
	}
	if payload.Abstained == nil {
		return Admitted{}, reject(ReasonAbstainedMissing, "abstained is required")
	}
	admitted := Admitted{valid: true, relevance: relevance, abstained: *payload.Abstained}
	for i, verdict := range payload.Verdicts {
		if verdict.Statement != i+1 {
			return Admitted{}, reject(ReasonStatementOutOfOrder, "verdict %d references statement %d, want %d", i+1, verdict.Statement, i+1)
		}
		if verdict.Supported == nil {
			return Admitted{}, reject(ReasonSupportedMissing, "verdict %d supported is required", i+1)
		}
		if strings.TrimSpace(verdict.Reason) == "" {
			return Admitted{}, reject(ReasonReasonMissing, "verdict %d reason is required", i+1)
		}
		seen := make(map[EvidenceLabel]struct{}, len(verdict.EvidenceIDs))
		labels := make([]EvidenceLabel, 0, len(verdict.EvidenceIDs))
		for _, id := range verdict.EvidenceIDs {
			label := EvidenceLabel(id)
			if !universe.Contains(label) {
				return Admitted{}, reject(ReasonUnknownEvidence, "verdict %d references unknown evidence %q", i+1, id)
			}
			if _, duplicate := seen[label]; duplicate {
				return Admitted{}, reject(ReasonDuplicateEvidence, "verdict %d repeats evidence %q", i+1, id)
			}
			seen[label] = struct{}{}
			labels = append(labels, label)
		}
		if *verdict.Supported && len(labels) == 0 {
			return Admitted{}, reject(ReasonSupportedWithoutEvidence, "supported verdict %d requires evidence_ids", i+1)
		}
		admitted.verdicts = append(admitted.verdicts, Verdict{
			Statement: statements[i],
			Supported: *verdict.Supported,
			Evidence:  labels,
			Reason:    strings.TrimSpace(verdict.Reason),
		})
	}
	return admitted, nil
}
