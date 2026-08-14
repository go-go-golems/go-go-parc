// Package judgekernel is the reusable structural half of the two-step
// decomposed LLM judge extracted from CoinVault internal/knowledge/judge.go
// and rag-ttc cmd/rag-ttc/cmds/experiments/answerquality/judge.go.
//
// The kernel owns exactly what is provable without a model: the admission
// relation over raw judge payloads, estimators with explicit denominators,
// the bounded repair combinator, and version-keyed population identity.
// It deliberately exports no accept/reject decision about the judged answer:
// the judge is a witness, not a gate, and that is an API property here —
// there is nothing in this package a gate could call.
package judgekernel

import (
	"fmt"
	"strings"
)

// EvidenceLabel is a nominal label for one piece of admitted evidence
// (for example "E1" from a knowledge ledger or "SQL2" from a tool result).
// Verdicts may cite evidence only through labels; the kernel never sees
// evidence bodies, which is part of the information-hiding discipline.
type EvidenceLabel string

// LabelUniverse is the closed set of labels a verdict may cite. Admission
// rejects any citation outside the universe, so a verdict cannot invent
// provenance — the same law CoinVault's projection layer enforces for
// user-facing source cards.
type LabelUniverse struct {
	labels map[EvidenceLabel]struct{}
}

// NewLabelUniverse builds a universe from distinct, non-empty labels.
func NewLabelUniverse(labels ...EvidenceLabel) (LabelUniverse, error) {
	set := make(map[EvidenceLabel]struct{}, len(labels))
	for _, label := range labels {
		if strings.TrimSpace(string(label)) == "" {
			return LabelUniverse{}, fmt.Errorf("empty evidence label")
		}
		if _, duplicate := set[label]; duplicate {
			return LabelUniverse{}, fmt.Errorf("duplicate evidence label %q", label)
		}
		set[label] = struct{}{}
	}
	return LabelUniverse{labels: set}, nil
}

// KnowledgeLabels returns E1..En, the ledger-label convention shared by both
// source implementations.
func KnowledgeLabels(n int) []EvidenceLabel {
	labels := make([]EvidenceLabel, 0, n)
	for i := 1; i <= n; i++ {
		labels = append(labels, EvidenceLabel(fmt.Sprintf("E%d", i)))
	}
	return labels
}

// SQLLabels returns SQL1..SQLn for non-knowledge tool-result evidence.
func SQLLabels(n int) []EvidenceLabel {
	labels := make([]EvidenceLabel, 0, n)
	for i := 1; i <= n; i++ {
		labels = append(labels, EvidenceLabel(fmt.Sprintf("SQL%d", i)))
	}
	return labels
}

// Contains reports membership.
func (u LabelUniverse) Contains(label EvidenceLabel) bool {
	_, ok := u.labels[label]
	return ok
}

// Size reports the number of labels in the universe.
func (u LabelUniverse) Size() int { return len(u.labels) }
