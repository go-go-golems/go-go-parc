package judgekernel

import (
	"fmt"
	"sort"
	"strings"
)

// The request types make the information-hiding discipline a property of
// the type system rather than of prompt-writing care:
//
//   - StatementsRequest carries the question and the answer. It has no
//     field for evidence, so statement extraction cannot see what is
//     supported and cannot bias extraction toward it.
//   - VerdictsRequest carries the question, the numbered statements, and
//     the labeled evidence. It has no field for the answer, so the verdict
//     step can judge only the extracted statements — it cannot re-read the
//     answer and quietly judge claims that were never extracted.
//
// A caller who wants to leak must build prompts by hand, outside the kernel.

// StatementsRequest is the step-1 input: extraction sees the answer, never
// the evidence.
type StatementsRequest struct {
	Question string
	Answer   string
}

// Render builds the deterministic step-1 prompt body appended to the
// caller's instruction prompt.
func (r StatementsRequest) Render() string {
	return fmt.Sprintf("Question:\n%s\n\nAnswer:\n%s", r.Question, r.Answer)
}

// LabeledEvidence is one admitted evidence body under its label.
type LabeledEvidence struct {
	Label EvidenceLabel
	Body  string
}

// VerdictsRequest is the step-2 input: verdicts see statements and
// evidence, never the answer.
type VerdictsRequest struct {
	Question   string
	Statements []string
	Evidence   []LabeledEvidence
}

// Universe returns the label universe induced by the request's evidence.
// Admission against exactly this universe guarantees citations resolve to
// evidence the verdict step actually saw.
func (r VerdictsRequest) Universe() (LabelUniverse, error) {
	labels := make([]EvidenceLabel, 0, len(r.Evidence))
	for _, evidence := range r.Evidence {
		labels = append(labels, evidence.Label)
	}
	return NewLabelUniverse(labels...)
}

// Render builds the deterministic step-2 prompt body: numbered statements
// in order, evidence sorted by label for byte determinism.
func (r VerdictsRequest) Render() string {
	numbered := make([]string, len(r.Statements))
	for i, statement := range r.Statements {
		numbered[i] = fmt.Sprintf("%d. %s", i+1, statement)
	}
	evidence := append([]LabeledEvidence(nil), r.Evidence...)
	sort.Slice(evidence, func(i, j int) bool { return evidence[i].Label < evidence[j].Label })
	bodies := make([]string, 0, len(evidence))
	for _, item := range evidence {
		bodies = append(bodies, fmt.Sprintf("[%s] %s", item.Label, item.Body))
	}
	if len(bodies) == 0 {
		bodies = append(bodies, "(no evidence was retrieved)")
	}
	return fmt.Sprintf("Question:\n%s\n\nStatements:\n%s\n\nEvidence:\n%s", r.Question, strings.Join(numbered, "\n"), strings.Join(bodies, "\n\n"))
}
