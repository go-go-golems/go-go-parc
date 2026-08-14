package suitegov

import (
	"errors"
	"fmt"
	"os"
	"path/filepath"
	"sort"
	"strings"
)

// CommitRequest names the base set, the reviewer, and which proposals apply.
type CommitRequest struct {
	// Base is the reviewed set being evolved. Commit never modifies it.
	Base *SuiteDocument
	// Dir receives the minted set. The file name embeds the semantic digest,
	// so a set can never be silently replaced under a stable name.
	Dir string
	// Reviewer approves the batch. Commit fails if the reviewer authored any
	// selected proposal: a draft cannot reach committed on one identity.
	Reviewer Identity
	// ProposalIDs selects a subset; empty applies every pending proposal.
	ProposalIDs []string
}

// CommitResult reports what a commit produced.
type CommitResult struct {
	Path               string         `json:"path"`
	SemanticDigest     SemanticDigest `json:"semantic_digest"`
	ByteDigest         ByteDigest     `json:"byte_digest"`
	BaseSemanticDigest SemanticDigest `json:"base_semantic_digest"`
	Applied            int            `json:"applied"`
	Reviewer           Identity       `json:"reviewer"`
}

// Commit folds selected pending proposals into a new digest-named immutable
// evaluation set. The base set is never touched: a governance transition is
// visible as a digest change or it did not happen.
func Commit(index *Index, request CommitRequest) (CommitResult, error) {
	if index == nil {
		return CommitResult{}, errors.New("proposal index is required")
	}
	if request.Base == nil {
		return CommitResult{}, errors.New("base suite document is required")
	}
	if strings.TrimSpace(request.Dir) == "" {
		return CommitResult{}, errors.New("commit directory is required")
	}
	if strings.TrimSpace(string(request.Reviewer)) == "" {
		return CommitResult{}, errors.New("reviewer identity is required")
	}
	if index.TruncatedTail {
		return CommitResult{}, errors.New("ledger has a torn final line; repair before committing")
	}

	selected, err := selectProposals(index, request.ProposalIDs)
	if err != nil {
		return CommitResult{}, err
	}
	if len(selected) == 0 {
		return CommitResult{}, errors.New("no proposals to commit")
	}
	for _, proposal := range selected {
		if strings.TrimSpace(string(proposal.Author)) == "" {
			return CommitResult{}, fmt.Errorf("proposal %s has no author identity", proposal.ID)
		}
		if proposal.Author == request.Reviewer {
			return CommitResult{}, fmt.Errorf(
				"reviewer %q authored proposal %s; a proposal cannot be approved by its own author",
				request.Reviewer, proposal.ID,
			)
		}
	}

	next, err := applyProposals(request.Base.Suite, selected)
	if err != nil {
		return CommitResult{}, err
	}
	// Validate the result, not the proposals: a batch can be individually
	// valid and collectively wrong (rag-ttc's commit records the same lesson).
	if err := normalizeSuite(&next); err != nil {
		return CommitResult{}, fmt.Errorf("committed suite would be invalid: %w", err)
	}
	semantic, err := IdentifySuite(next)
	if err != nil {
		return CommitResult{}, err
	}
	if semantic == request.Base.SemanticDigest {
		return CommitResult{}, errors.New("commit would not change the suite's semantic identity")
	}

	data, err := marshalSuite(next)
	if err != nil {
		return CommitResult{}, err
	}
	path := filepath.Join(request.Dir, mintedName(next.Name, semantic))
	if err := writeImmutable(path, data); err != nil {
		return CommitResult{}, err
	}
	return CommitResult{
		Path:               path,
		SemanticDigest:     semantic,
		ByteDigest:         digestBytes(data),
		BaseSemanticDigest: request.Base.SemanticDigest,
		Applied:            len(selected),
		Reviewer:           request.Reviewer,
	}, nil
}

func applyProposals(base Suite, proposals []Proposal) (Suite, error) {
	next := Suite{SchemaVersion: base.SchemaVersion, Name: base.Name}
	next.Cases = append(next.Cases, base.Cases...)
	position := make(map[string]int, len(next.Cases))
	for index, value := range next.Cases {
		position[value.ID] = index
	}
	for _, proposal := range proposals {
		index, exists := position[proposal.CaseID]
		switch proposal.Kind {
		case KindAddCase:
			if exists {
				return Suite{}, fmt.Errorf("proposal %s adds case %q, which already exists", proposal.ID, proposal.CaseID)
			}
			next.Cases = append(next.Cases, *proposal.Case)
			position[proposal.CaseID] = len(next.Cases) - 1
		case KindAmendCase:
			if !exists {
				return Suite{}, fmt.Errorf("proposal %s amends unknown case %q", proposal.ID, proposal.CaseID)
			}
			next.Cases[index] = *proposal.Case
		case KindRetireCase:
			if !exists {
				return Suite{}, fmt.Errorf("proposal %s retires unknown case %q", proposal.ID, proposal.CaseID)
			}
			next.Cases = append(next.Cases[:index], next.Cases[index+1:]...)
			position = make(map[string]int, len(next.Cases))
			for i, value := range next.Cases {
				position[value.ID] = i
			}
		default:
			return Suite{}, fmt.Errorf("proposal %s has unknown kind %q", proposal.ID, proposal.Kind)
		}
	}
	return next, nil
}

func selectProposals(index *Index, ids []string) ([]Proposal, error) {
	pending := index.Pending()
	if len(ids) == 0 {
		return pending, nil
	}
	wanted := make(map[string]struct{}, len(ids))
	for _, id := range ids {
		wanted[id] = struct{}{}
	}
	out := make([]Proposal, 0, len(ids))
	for _, proposal := range pending {
		if _, ok := wanted[proposal.ID]; ok {
			out = append(out, proposal)
			delete(wanted, proposal.ID)
		}
	}
	if len(wanted) > 0 {
		missing := make([]string, 0, len(wanted))
		for id := range wanted {
			missing = append(missing, id)
		}
		sort.Strings(missing)
		return nil, fmt.Errorf("no pending proposal with ID %s", strings.Join(missing, ", "))
	}
	return out, nil
}

func mintedName(name string, semantic SemanticDigest) string {
	hexPart := strings.TrimPrefix(string(semantic), "sha256:")
	if len(hexPart) > 12 {
		hexPart = hexPart[:12]
	}
	return name + "-" + hexPart + ".json"
}

func marshalSuite(suite Suite) ([]byte, error) {
	data, err := marshalIndent(suite)
	if err != nil {
		return nil, fmt.Errorf("encode suite: %w", err)
	}
	return data, nil
}

// writeImmutable creates the minted set exclusively and read-only. O_EXCL is
// the immutability mechanism: a digest-named file exists at most once, so a
// re-commit of identical content is an explicit error rather than a silent
// overwrite, and a colliding name can never replace reviewed bytes.
func writeImmutable(path string, data []byte) error {
	if err := os.MkdirAll(filepath.Dir(path), 0o755); err != nil {
		return fmt.Errorf("create commit directory: %w", err)
	}
	file, err := os.OpenFile(path, os.O_CREATE|os.O_EXCL|os.O_WRONLY, 0o444)
	if err != nil {
		return fmt.Errorf("create minted suite (already committed?): %w", err)
	}
	if _, err := file.Write(data); err != nil {
		_ = file.Close()
		return fmt.Errorf("write minted suite: %w", err)
	}
	if err := file.Sync(); err != nil {
		_ = file.Close()
		return fmt.Errorf("sync minted suite: %w", err)
	}
	if err := file.Close(); err != nil {
		return fmt.Errorf("close minted suite: %w", err)
	}
	return nil
}
