package suitegov

import (
	"errors"
	"fmt"
	"os"
	"path/filepath"
	"strings"
)

// LockSchemaVersion identifies the reviewed-suite lock contract.
const LockSchemaVersion = "suitegov-lock/v1"

// LockEntry binds one split to its reviewed identity. A closed entry binds
// the sentinel bytes instead of suite content.
type LockEntry struct {
	Split          string         `json:"split"`
	Path           string         `json:"path"`
	Closed         bool           `json:"closed,omitempty"`
	CaseCount      int            `json:"case_count,omitempty"`
	SemanticDigest SemanticDigest `json:"semantic_digest,omitempty"`
	ByteDigest     ByteDigest     `json:"byte_digest"`
}

// Lock is the reviewed-suite lock: the durable statement that a named
// reviewer approved exactly these suite identities on a date, with a record.
// It generalizes CoinVault's `gec-chat-suite-lock/v1`.
type Lock struct {
	SchemaVersion string      `json:"schema_version"`
	ReviewStatus  string      `json:"review_status"`
	ReviewedOn    string      `json:"reviewed_on"`
	ReviewRecord  string      `json:"review_record"`
	Reviewer      Identity    `json:"reviewer"`
	Entries       []LockEntry `json:"entries"`
}

// LoadLock strictly loads a lock file.
func LoadLock(path string) (*Lock, error) {
	data, err := os.ReadFile(path)
	if err != nil {
		return nil, fmt.Errorf("read lock: %w", err)
	}
	var lock Lock
	if err := decodeStrictJSON(data, &lock); err != nil {
		return nil, fmt.Errorf("decode lock: %w", err)
	}
	if lock.SchemaVersion != LockSchemaVersion {
		return nil, fmt.Errorf("unsupported lock schema %q", lock.SchemaVersion)
	}
	return &lock, nil
}

// Verify checks the lock's review metadata and every entry against the files
// under root. It is designed for preflight embedding: run it before spend,
// alongside the rest of an experiment's environment validation.
func (l *Lock) Verify(root string) error {
	if l == nil {
		return errors.New("lock is nil")
	}
	if l.ReviewStatus != "approved" {
		return fmt.Errorf("lock review status is %q, not approved", l.ReviewStatus)
	}
	if strings.TrimSpace(l.ReviewedOn) == "" || strings.TrimSpace(l.ReviewRecord) == "" {
		return errors.New("lock requires reviewed_on and review_record")
	}
	if strings.TrimSpace(string(l.Reviewer)) == "" {
		return errors.New("lock requires a reviewer identity")
	}
	if len(l.Entries) == 0 {
		return errors.New("lock has no entries")
	}
	absoluteRoot, err := filepath.Abs(root)
	if err != nil {
		return err
	}
	seen := map[string]struct{}{}
	for _, entry := range l.Entries {
		if _, duplicate := seen[entry.Split]; duplicate {
			return fmt.Errorf("lock repeats split %q", entry.Split)
		}
		seen[entry.Split] = struct{}{}
		path := filepath.Join(absoluteRoot, filepath.FromSlash(entry.Path))
		relative, err := filepath.Rel(absoluteRoot, path)
		if err != nil || relative == ".." || strings.HasPrefix(relative, ".."+string(filepath.Separator)) {
			return fmt.Errorf("lock entry %q escapes root: %q", entry.Split, entry.Path)
		}
		data, err := os.ReadFile(path)
		if err != nil {
			return fmt.Errorf("read locked split %q: %w", entry.Split, err)
		}
		if digestBytes(data) != entry.ByteDigest {
			return fmt.Errorf("split %q byte digest drifted from reviewed lock", entry.Split)
		}
		if entry.Closed {
			if _, closed := decodeSentinel(data); !closed {
				return fmt.Errorf("split %q is locked closed but the file is not a sentinel", entry.Split)
			}
			if entry.SemanticDigest != "" || entry.CaseCount != 0 {
				return fmt.Errorf("closed split %q must not declare suite identity", entry.Split)
			}
			continue
		}
		document, err := LoadSuiteBytes(data)
		if err != nil {
			return fmt.Errorf("strict-load locked split %q: %w", entry.Split, err)
		}
		if document.SemanticDigest != entry.SemanticDigest {
			return fmt.Errorf("split %q semantic digest drifted from reviewed lock", entry.Split)
		}
		if len(document.Suite.Cases) != entry.CaseCount {
			return fmt.Errorf("split %q case count drifted: lock=%d actual=%d", entry.Split, entry.CaseCount, len(document.Suite.Cases))
		}
	}
	return nil
}

// BindRun is the preflight law CoinVault currently does not enforce: the
// suite a run is about to measure must be, provably, a reviewed suite. It
// fails when the split is unknown, locked closed, or when the observed
// semantic digest differs from the reviewed one.
func (l *Lock) BindRun(split string, observed SemanticDigest) error {
	if l == nil {
		return errors.New("lock is nil")
	}
	if l.ReviewStatus != "approved" {
		return fmt.Errorf("lock review status is %q, not approved", l.ReviewStatus)
	}
	for _, entry := range l.Entries {
		if entry.Split != split {
			continue
		}
		if entry.Closed {
			return &SplitClosedError{Split: split, Reason: "split is locked closed"}
		}
		if entry.SemanticDigest != observed {
			return fmt.Errorf(
				"run suite is not the reviewed suite for split %q: reviewed=%s observed=%s",
				split, entry.SemanticDigest, observed,
			)
		}
		return nil
	}
	return fmt.Errorf("lock has no entry for split %q", split)
}
