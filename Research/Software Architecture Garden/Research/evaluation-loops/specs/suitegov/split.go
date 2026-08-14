package suitegov

import (
	"encoding/json"
	"errors"
	"fmt"
	"os"
	"path/filepath"
	"strings"
)

// ClosedSentinelSchemaVersion identifies the closed-split sentinel contract.
const ClosedSentinelSchemaVersion = "suitegov-split-closed/v1"

// ClosedSentinel stands in place of held-out suite data. The mechanism copies
// CoinVault's `gec-validation-closed/v1` sentinel: the held-out bytes are not
// present behind a flag — they are not present at all, so leakage requires
// obtaining bytes elsewhere, not ignoring a boolean.
type ClosedSentinel struct {
	SchemaVersion string `json:"schema_version"`
	Split         string `json:"split"`
	Reason        string `json:"reason"`
	// OpenCriteria states, for humans, what evidence permits Open.
	OpenCriteria string `json:"open_criteria"`
}

// SplitClosedError is the typed refusal a closed split produces. Callers that
// want to branch must match this type; there is no suite value to misuse.
type SplitClosedError struct {
	Split  string
	Reason string
}

func (e *SplitClosedError) Error() string {
	return fmt.Sprintf("split %q is closed: %s", e.Split, e.Reason)
}

// PromotionEvidence is what an Open transition must carry. The package checks
// presence and approver identity shape; whether the evidence is sufficient is
// a human decision recorded by the referenced record.
type PromotionEvidence struct {
	FeedbackRunID      string   `json:"feedback_run_id"`
	GateDecisionDigest string   `json:"gate_decision_digest"`
	Approver           Identity `json:"approver"`
	Record             string   `json:"record"`
}

// LoadSplit loads a split file. A sentinel yields *SplitClosedError; anything
// else must strict-load as a suite. There is no code path that returns suite
// data from a closed split.
func LoadSplit(path string) (*SuiteDocument, error) {
	data, err := os.ReadFile(path)
	if err != nil {
		return nil, fmt.Errorf("read split: %w", err)
	}
	if sentinel, closed := decodeSentinel(data); closed {
		return nil, &SplitClosedError{Split: sentinel.Split, Reason: sentinel.Reason}
	}
	document, err := LoadSuiteBytes(data)
	if err != nil {
		return nil, err
	}
	absolute, err := filepath.Abs(path)
	if err == nil {
		document.SourcePath = absolute
	}
	return document, nil
}

func decodeSentinel(data []byte) (ClosedSentinel, bool) {
	probe := struct {
		SchemaVersion string `json:"schema_version"`
	}{}
	if err := json.Unmarshal(data, &probe); err != nil {
		return ClosedSentinel{}, false
	}
	if probe.SchemaVersion != ClosedSentinelSchemaVersion {
		return ClosedSentinel{}, false
	}
	var sentinel ClosedSentinel
	if err := json.Unmarshal(data, &sentinel); err != nil {
		return ClosedSentinel{}, false
	}
	return sentinel, true
}

// WriteClosedSentinel installs a sentinel at path. It refuses to replace an
// existing file: closing is a creation-time decision, not a data-destroying
// operation this package performs.
func WriteClosedSentinel(path string, sentinel ClosedSentinel) error {
	sentinel.SchemaVersion = ClosedSentinelSchemaVersion
	if strings.TrimSpace(sentinel.Split) == "" || strings.TrimSpace(sentinel.Reason) == "" || strings.TrimSpace(sentinel.OpenCriteria) == "" {
		return errors.New("closed sentinel requires split, reason, and open criteria")
	}
	data, err := marshalIndent(sentinel)
	if err != nil {
		return fmt.Errorf("encode sentinel: %w", err)
	}
	return writeImmutable(path, data)
}

// OpenSplit replaces a sentinel with real suite bytes, atomically, under
// promotion evidence. The transition fails when the path is not currently a
// sentinel (a split cannot be opened twice) or when any evidence field is
// absent. An opened split file also gets a sibling
// `<name>.opened.json` record binding the evidence to the transition.
func OpenSplit(path string, evidence PromotionEvidence, suiteBytes []byte) (*SuiteDocument, error) {
	current, err := os.ReadFile(path)
	if err != nil {
		return nil, fmt.Errorf("read split: %w", err)
	}
	sentinel, closed := decodeSentinel(current)
	if !closed {
		return nil, fmt.Errorf("split at %q is not closed; refusing to replace open data", path)
	}
	if strings.TrimSpace(evidence.FeedbackRunID) == "" ||
		strings.TrimSpace(evidence.GateDecisionDigest) == "" ||
		strings.TrimSpace(string(evidence.Approver)) == "" ||
		strings.TrimSpace(evidence.Record) == "" {
		return nil, errors.New("open transition requires feedback run, gate decision digest, approver, and record")
	}
	document, err := LoadSuiteBytes(suiteBytes)
	if err != nil {
		return nil, fmt.Errorf("held-out suite bytes are invalid: %w", err)
	}

	openRecord := struct {
		SchemaVersion string            `json:"schema_version"`
		Split         string            `json:"split"`
		Evidence      PromotionEvidence `json:"evidence"`
		SuiteDigest   SemanticDigest    `json:"suite_semantic_digest"`
	}{
		SchemaVersion: "suitegov-split-opened/v1",
		Split:         sentinel.Split,
		Evidence:      evidence,
		SuiteDigest:   document.SemanticDigest,
	}
	recordData, err := marshalIndent(openRecord)
	if err != nil {
		return nil, fmt.Errorf("encode open record: %w", err)
	}
	recordPath := strings.TrimSuffix(path, filepath.Ext(path)) + ".opened.json"
	if err := writeImmutable(recordPath, recordData); err != nil {
		return nil, err
	}

	temporary := path + ".opening"
	if err := os.WriteFile(temporary, suiteBytes, 0o444); err != nil {
		return nil, fmt.Errorf("stage opened suite: %w", err)
	}
	// The sentinel was written read-only; make the target replaceable.
	if err := os.Chmod(path, 0o644); err != nil {
		return nil, fmt.Errorf("unlock sentinel for replacement: %w", err)
	}
	if err := os.Rename(temporary, path); err != nil {
		return nil, fmt.Errorf("install opened suite: %w", err)
	}
	document.SourcePath = path
	return document, nil
}

func marshalIndent(value any) ([]byte, error) {
	data, err := json.MarshalIndent(value, "", "  ")
	if err != nil {
		return nil, err
	}
	return append(data, '\n'), nil
}
