package suitegov

import (
	"bufio"
	"encoding/json"
	"errors"
	"fmt"
	"os"
	"path/filepath"
	"sort"
	"strings"
	"sync"
	"time"
)

// ProposalSchemaVersion identifies the ledger record contract.
const ProposalSchemaVersion = "suitegov-proposal/v1"

// Op is what a ledger record does to a proposal.
type Op string

const (
	OpPropose  Op = "propose"
	OpWithdraw Op = "withdraw"
)

// Kind is the change a proposal requests against the base suite.
type Kind string

const (
	KindAddCase    Kind = "add-case"
	KindAmendCase  Kind = "amend-case"
	KindRetireCase Kind = "retire-case"
)

// Proposal is one hash-chained ledger record.
//
// Unlike rag-ttc's judgment ledger, which tolerates undecodable lines by
// counting them as dropped, this ledger is chain-verified: every record
// carries the digest of its predecessor and its own digest, so interior
// tampering or deletion is an error, not a statistic. Governance evidence and
// best-effort telemetry have different corruption budgets.
type Proposal struct {
	SchemaVersion string    `json:"schema_version"`
	ID            string    `json:"id"`
	At            time.Time `json:"at"`
	Op            Op        `json:"op"`
	Author        Identity  `json:"author,omitempty"`
	Kind          Kind      `json:"kind,omitempty"`
	CaseID        string    `json:"case_id,omitempty"`
	Case          *Case     `json:"case,omitempty"`
	Rationale     string    `json:"rationale,omitempty"`
	PrevDigest    string    `json:"prev_digest"`
	Digest        string    `json:"digest"`
}

func proposalDigest(proposal Proposal) (string, error) {
	proposal.Digest = ""
	data, err := json.Marshal(proposal)
	if err != nil {
		return "", fmt.Errorf("marshal proposal for digest: %w", err)
	}
	return string(digestBytes(data)), nil
}

// Ledger appends proposals to one hash-chained JSONL file.
type Ledger struct {
	mu   sync.Mutex
	path string
	now  func() time.Time
}

// OpenLedger prepares a ledger under root. It creates no file.
func OpenLedger(root string) (*Ledger, error) {
	if strings.TrimSpace(root) == "" {
		return nil, errors.New("ledger root is required")
	}
	return &Ledger{
		path: filepath.Join(root, "suite-proposals.jsonl"),
		now:  func() time.Time { return time.Now().UTC() },
	}, nil
}

// Path returns the ledger file location.
func (l *Ledger) Path() string { return l.path }

// ProposeRequest is one requested suite change.
type ProposeRequest struct {
	Author    Identity
	Kind      Kind
	CaseID    string
	Case      *Case // required for add/amend, forbidden for retire
	Rationale string
}

// Propose validates and appends one proposal.
func (l *Ledger) Propose(request ProposeRequest) (Proposal, error) {
	if l == nil {
		return Proposal{}, errors.New("ledger is nil")
	}
	if strings.TrimSpace(string(request.Author)) == "" {
		return Proposal{}, errors.New("proposal author identity is required")
	}
	if strings.TrimSpace(request.Rationale) == "" {
		return Proposal{}, errors.New("proposal rationale is required")
	}
	if !identifierPattern.MatchString(request.CaseID) {
		return Proposal{}, fmt.Errorf("invalid proposal case ID %q", request.CaseID)
	}
	switch request.Kind {
	case KindAddCase, KindAmendCase:
		if request.Case == nil {
			return Proposal{}, fmt.Errorf("%s proposal requires a case body", request.Kind)
		}
		if request.Case.ID != request.CaseID {
			return Proposal{}, fmt.Errorf("proposal case ID %q does not match case body ID %q", request.CaseID, request.Case.ID)
		}
		body := *request.Case
		if err := normalizeCase(&body); err != nil {
			return Proposal{}, err
		}
		request.Case = &body
	case KindRetireCase:
		if request.Case != nil {
			return Proposal{}, errors.New("retire-case proposal must not carry a case body")
		}
	default:
		return Proposal{}, fmt.Errorf("unknown proposal kind %q", request.Kind)
	}

	l.mu.Lock()
	defer l.mu.Unlock()
	chain, err := readChain(l.path)
	if err != nil {
		return Proposal{}, err
	}
	if chain.TruncatedTail {
		return Proposal{}, errors.New("ledger has a torn final line; repair explicitly before appending")
	}

	at := l.now()
	proposal := Proposal{
		SchemaVersion: ProposalSchemaVersion,
		At:            at,
		Op:            OpPropose,
		Author:        request.Author,
		Kind:          request.Kind,
		CaseID:        request.CaseID,
		Case:          request.Case,
		Rationale:     request.Rationale,
		PrevDigest:    chain.Head,
	}
	proposal.ID = fmt.Sprintf("proposal-%s", mustShortDigest(proposal))
	digest, err := proposalDigest(proposal)
	if err != nil {
		return Proposal{}, err
	}
	proposal.Digest = digest
	if err := appendRecord(l.path, proposal); err != nil {
		return Proposal{}, err
	}
	return proposal, nil
}

// Withdraw takes back a pending proposal by ID. The record stays in the log;
// withdrawal is itself an appended, chained record.
func (l *Ledger) Withdraw(id string, author Identity) error {
	if l == nil {
		return errors.New("ledger is nil")
	}
	if strings.TrimSpace(id) == "" {
		return errors.New("proposal ID is required")
	}
	l.mu.Lock()
	defer l.mu.Unlock()
	chain, err := readChain(l.path)
	if err != nil {
		return err
	}
	if chain.TruncatedTail {
		return errors.New("ledger has a torn final line; repair explicitly before appending")
	}
	record := Proposal{
		SchemaVersion: ProposalSchemaVersion,
		ID:            id,
		At:            l.now(),
		Op:            OpWithdraw,
		Author:        author,
		PrevDigest:    chain.Head,
	}
	digest, err := proposalDigest(record)
	if err != nil {
		return err
	}
	record.Digest = digest
	return appendRecord(l.path, record)
}

func mustShortDigest(proposal Proposal) string {
	digest, err := proposalDigest(proposal)
	if err != nil {
		return "invalid"
	}
	hexPart := strings.TrimPrefix(digest, "sha256:")
	if len(hexPart) > 12 {
		hexPart = hexPart[:12]
	}
	return hexPart
}

func appendRecord(path string, record Proposal) error {
	data, err := json.Marshal(record)
	if err != nil {
		return fmt.Errorf("marshal ledger record: %w", err)
	}
	if err := os.MkdirAll(filepath.Dir(path), 0o700); err != nil {
		return fmt.Errorf("create ledger directory: %w", err)
	}
	file, err := os.OpenFile(path, os.O_CREATE|os.O_APPEND|os.O_WRONLY, 0o600)
	if err != nil {
		return fmt.Errorf("open ledger: %w", err)
	}
	// One write of one complete line, then sync: a torn line is the only
	// recoverable corruption this format tolerates, and only at the tail.
	if _, err := file.Write(append(data, '\n')); err != nil {
		_ = file.Close()
		return fmt.Errorf("append ledger record: %w", err)
	}
	if err := file.Sync(); err != nil {
		_ = file.Close()
		return fmt.Errorf("sync ledger: %w", err)
	}
	if err := file.Close(); err != nil {
		return fmt.Errorf("close ledger: %w", err)
	}
	return nil
}

type chainState struct {
	Records       []Proposal
	Head          string
	TruncatedTail bool
}

// readChain loads and verifies the full hash chain. A record whose own digest
// does not verify, or whose predecessor link does not match, is an error. Only
// an undecodable final line is tolerated, reported as a torn tail.
func readChain(path string) (chainState, error) {
	state := chainState{}
	file, err := os.Open(path)
	if errors.Is(err, os.ErrNotExist) {
		return state, nil
	}
	if err != nil {
		return state, fmt.Errorf("open ledger: %w", err)
	}
	defer func() { _ = file.Close() }()

	scanner := bufio.NewScanner(file)
	scanner.Buffer(make([]byte, 0, 64*1024), 4*1024*1024)
	lineNumber := 0
	var pendingTornLine bool
	for scanner.Scan() {
		lineNumber++
		line := strings.TrimSpace(scanner.Text())
		if line == "" {
			continue
		}
		if pendingTornLine {
			// A decode failure followed by more content is interior
			// corruption, not a torn tail.
			return state, fmt.Errorf("ledger line %d: undecodable interior record", lineNumber-1)
		}
		var record Proposal
		if err := json.Unmarshal([]byte(line), &record); err != nil {
			pendingTornLine = true
			continue
		}
		if record.SchemaVersion != ProposalSchemaVersion {
			return state, fmt.Errorf("ledger line %d: unsupported schema %q", lineNumber, record.SchemaVersion)
		}
		computed, err := proposalDigest(record)
		if err != nil {
			return state, err
		}
		if computed != record.Digest {
			return state, fmt.Errorf("ledger line %d: record digest mismatch (tampered or rewritten)", lineNumber)
		}
		if record.PrevDigest != state.Head {
			return state, fmt.Errorf("ledger line %d: chain break (previous digest %q, expected %q)", lineNumber, record.PrevDigest, state.Head)
		}
		state.Records = append(state.Records, record)
		state.Head = record.Digest
	}
	if err := scanner.Err(); err != nil {
		return state, fmt.Errorf("scan ledger: %w", err)
	}
	state.TruncatedTail = pendingTornLine
	return state, nil
}

// Index is the folded set of pending proposals.
type Index struct {
	byID map[string]Proposal
	// TruncatedTail reports that the final ledger line was torn and ignored.
	TruncatedTail bool
}

// Load verifies the chain and folds it into pending state. A later proposal
// for the same case supersedes an earlier pending one; a withdrawal removes a
// pending proposal by ID.
func (l *Ledger) Load() (*Index, error) {
	index := &Index{byID: map[string]Proposal{}}
	if l == nil {
		return index, nil
	}
	l.mu.Lock()
	defer l.mu.Unlock()
	chain, err := readChain(l.path)
	if err != nil {
		return nil, err
	}
	index.TruncatedTail = chain.TruncatedTail
	for _, record := range chain.Records {
		switch record.Op {
		case OpPropose:
			for id, existing := range index.byID {
				if existing.CaseID == record.CaseID {
					delete(index.byID, id)
				}
			}
			index.byID[record.ID] = record
		case OpWithdraw:
			delete(index.byID, record.ID)
		}
	}
	return index, nil
}

// Pending returns proposals awaiting commit, oldest first.
func (i *Index) Pending() []Proposal {
	if i == nil {
		return nil
	}
	out := make([]Proposal, 0, len(i.byID))
	for _, proposal := range i.byID {
		out = append(out, proposal)
	}
	sort.Slice(out, func(a, b int) bool {
		if !out[a].At.Equal(out[b].At) {
			return out[a].At.Before(out[b].At)
		}
		return out[a].ID < out[b].ID
	})
	return out
}
