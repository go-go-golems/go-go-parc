package suitegov

import (
	"encoding/json"
	"errors"
	"os"
	"path/filepath"
	"strings"
	"testing"
	"time"
)

func caseJSON(id, group, question string) Case {
	return Case{
		ID:     id,
		Groups: []string{group},
		Input:  json.RawMessage(`{"question": "` + question + `"}`),
	}
}

func baseSuiteBytes(t *testing.T) []byte {
	t.Helper()
	suite := Suite{
		SchemaVersion: SuiteSchemaVersion,
		Name:          "feedback",
		Cases: []Case{
			caseJSON("case-a", "knowledge", "what is a proof coin"),
			caseJSON("case-b", "sql", "how many orders shipped"),
		},
	}
	data, err := json.MarshalIndent(suite, "", "  ")
	if err != nil {
		t.Fatal(err)
	}
	return data
}

func writeBaseSuite(t *testing.T, dir string) *SuiteDocument {
	t.Helper()
	path := filepath.Join(dir, "feedback.json")
	if err := os.WriteFile(path, baseSuiteBytes(t), 0o644); err != nil {
		t.Fatal(err)
	}
	document, err := LoadSuite(path)
	if err != nil {
		t.Fatalf("load base suite: %v", err)
	}
	return document
}

// --- Identity projection ---

func TestSemanticDigestStableAcrossReserialization(t *testing.T) {
	compact := []byte(`{"schema_version":"suitegov-suite/v1","name":"feedback",` +
		`"cases":[{"id":"case-a","groups":["knowledge"],"input":{"question":"q1"}},` +
		`{"id":"case-b","groups":["sql"],"input":{"question":"q2"}}]}`)
	spaced := []byte(`{
  "schema_version": "suitegov-suite/v1",
  "name": "feedback",
  "cases": [
    { "id": "case-a", "input": { "question": "q1" }, "groups": [ "knowledge" ] },
    { "id": "case-b", "input": { "question": "q2" }, "groups": [ "sql" ] }
  ]
}`)
	first, err := LoadSuiteBytes(compact)
	if err != nil {
		t.Fatal(err)
	}
	second, err := LoadSuiteBytes(spaced)
	if err != nil {
		t.Fatal(err)
	}
	if first.SemanticDigest != second.SemanticDigest {
		t.Fatalf("semantic digests differ across reserialization: %s vs %s", first.SemanticDigest, second.SemanticDigest)
	}
	if first.ByteDigest == second.ByteDigest {
		t.Fatal("byte digests should differ for different bytes")
	}
}

func TestSemanticDigestSensitiveToCaseOrder(t *testing.T) {
	forward := []byte(`{"schema_version":"suitegov-suite/v1","name":"s",` +
		`"cases":[{"id":"a","input":{}},{"id":"b","input":{}}]}`)
	reversed := []byte(`{"schema_version":"suitegov-suite/v1","name":"s",` +
		`"cases":[{"id":"b","input":{}},{"id":"a","input":{}}]}`)
	first, err := LoadSuiteBytes(forward)
	if err != nil {
		t.Fatal(err)
	}
	second, err := LoadSuiteBytes(reversed)
	if err != nil {
		t.Fatal(err)
	}
	if first.SemanticDigest == second.SemanticDigest {
		t.Fatal("case order participates in execution and must participate in identity")
	}
}

func TestSemanticDigestInsensitiveToGroupOrder(t *testing.T) {
	forward := []byte(`{"schema_version":"suitegov-suite/v1","name":"s",` +
		`"cases":[{"id":"a","groups":["x","y"],"input":{}}]}`)
	reversed := []byte(`{"schema_version":"suitegov-suite/v1","name":"s",` +
		`"cases":[{"id":"a","groups":["y","x"],"input":{}}]}`)
	first, err := LoadSuiteBytes(forward)
	if err != nil {
		t.Fatal(err)
	}
	second, err := LoadSuiteBytes(reversed)
	if err != nil {
		t.Fatal(err)
	}
	if first.SemanticDigest != second.SemanticDigest {
		t.Fatal("group order carries no execution meaning and must not change identity")
	}
}

func TestLoadSuiteRejectsDuplicateAndUnknown(t *testing.T) {
	duplicate := []byte(`{"schema_version":"suitegov-suite/v1","name":"s",` +
		`"cases":[{"id":"a","input":{}},{"id":"a","input":{}}]}`)
	if _, err := LoadSuiteBytes(duplicate); err == nil {
		t.Fatal("duplicate case IDs must be rejected")
	}
	unknown := []byte(`{"schema_version":"suitegov-suite/v1","name":"s","surprise":true,` +
		`"cases":[{"id":"a","input":{}}]}`)
	if _, err := LoadSuiteBytes(unknown); err == nil {
		t.Fatal("unknown fields must be rejected")
	}
}

// --- Ledger ---

func newTestLedger(t *testing.T) *Ledger {
	t.Helper()
	ledger, err := OpenLedger(t.TempDir())
	if err != nil {
		t.Fatal(err)
	}
	tick := time.Date(2026, 8, 14, 12, 0, 0, 0, time.UTC)
	ledger.now = func() time.Time {
		tick = tick.Add(time.Second)
		return tick
	}
	return ledger
}

func propose(t *testing.T, ledger *Ledger, author Identity, kind Kind, id string, body *Case) Proposal {
	t.Helper()
	proposal, err := ledger.Propose(ProposeRequest{
		Author:    author,
		Kind:      kind,
		CaseID:    id,
		Case:      body,
		Rationale: "test rationale",
	})
	if err != nil {
		t.Fatalf("propose: %v", err)
	}
	return proposal
}

func TestLedgerFoldSupersedesAndWithdraws(t *testing.T) {
	ledger := newTestLedger(t)
	newCase := caseJSON("case-c", "knowledge", "v1")
	first := propose(t, ledger, "author-1", KindAddCase, "case-c", &newCase)
	updated := caseJSON("case-c", "knowledge", "v2")
	second := propose(t, ledger, "author-1", KindAddCase, "case-c", &updated)
	retire := propose(t, ledger, "author-2", KindRetireCase, "case-b", nil)

	index, err := ledger.Load()
	if err != nil {
		t.Fatal(err)
	}
	pending := index.Pending()
	if len(pending) != 2 {
		t.Fatalf("want 2 pending after supersede, got %d", len(pending))
	}
	if _, ok := index.byID[first.ID]; ok {
		t.Fatal("superseded proposal should not remain pending")
	}
	if err := ledger.Withdraw(second.ID, "author-1"); err != nil {
		t.Fatal(err)
	}
	index, err = ledger.Load()
	if err != nil {
		t.Fatal(err)
	}
	if len(index.Pending()) != 1 || index.Pending()[0].ID != retire.ID {
		t.Fatalf("want only the retire proposal pending, got %+v", index.Pending())
	}
}

func TestLedgerDetectsTamperedRecord(t *testing.T) {
	ledger := newTestLedger(t)
	body := caseJSON("case-c", "knowledge", "v1")
	propose(t, ledger, "author-1", KindAddCase, "case-c", &body)
	propose(t, ledger, "author-2", KindRetireCase, "case-b", nil)

	data, err := os.ReadFile(ledger.Path())
	if err != nil {
		t.Fatal(err)
	}
	tampered := strings.Replace(string(data), "test rationale", "rewritten rationale", 1)
	if tampered == string(data) {
		t.Fatal("test setup: nothing replaced")
	}
	if err := os.WriteFile(ledger.Path(), []byte(tampered), 0o600); err != nil {
		t.Fatal(err)
	}
	if _, err := ledger.Load(); err == nil {
		t.Fatal("tampered interior record must break the chain")
	}
}

func TestLedgerDetectsDeletedRecord(t *testing.T) {
	ledger := newTestLedger(t)
	bodyC := caseJSON("case-c", "knowledge", "v1")
	propose(t, ledger, "author-1", KindAddCase, "case-c", &bodyC)
	bodyD := caseJSON("case-d", "knowledge", "v1")
	propose(t, ledger, "author-1", KindAddCase, "case-d", &bodyD)
	propose(t, ledger, "author-2", KindRetireCase, "case-b", nil)

	data, err := os.ReadFile(ledger.Path())
	if err != nil {
		t.Fatal(err)
	}
	lines := strings.Split(strings.TrimSpace(string(data)), "\n")
	if len(lines) != 3 {
		t.Fatalf("want 3 ledger lines, got %d", len(lines))
	}
	rewritten := lines[0] + "\n" + lines[2] + "\n"
	if err := os.WriteFile(ledger.Path(), []byte(rewritten), 0o600); err != nil {
		t.Fatal(err)
	}
	if _, err := ledger.Load(); err == nil {
		t.Fatal("deleting an interior record must break the chain")
	}
}

func TestLedgerToleratesOnlyTornTail(t *testing.T) {
	ledger := newTestLedger(t)
	body := caseJSON("case-c", "knowledge", "v1")
	propose(t, ledger, "author-1", KindAddCase, "case-c", &body)

	file, err := os.OpenFile(ledger.Path(), os.O_APPEND|os.O_WRONLY, 0o600)
	if err != nil {
		t.Fatal(err)
	}
	if _, err := file.WriteString(`{"schema_version":"suitegov-proposal/v1","id":"torn`); err != nil {
		t.Fatal(err)
	}
	_ = file.Close()

	index, err := ledger.Load()
	if err != nil {
		t.Fatalf("torn tail should be reported, not fatal on load: %v", err)
	}
	if !index.TruncatedTail {
		t.Fatal("torn tail must be reported")
	}
	if len(index.Pending()) != 1 {
		t.Fatalf("intact prefix must survive, got %d pending", len(index.Pending()))
	}
	if _, err := ledger.Propose(ProposeRequest{
		Author: "author-1", Kind: KindRetireCase, CaseID: "case-b", Rationale: "r",
	}); err == nil {
		t.Fatal("append onto a torn tail must be refused")
	}
}

// --- Commit ---

func TestCommitRejectsSelfApproval(t *testing.T) {
	dir := t.TempDir()
	base := writeBaseSuite(t, dir)
	ledger := newTestLedger(t)
	body := caseJSON("case-c", "knowledge", "new question")
	propose(t, ledger, "author-1", KindAddCase, "case-c", &body)
	index, err := ledger.Load()
	if err != nil {
		t.Fatal(err)
	}
	_, err = Commit(index, CommitRequest{Base: base, Dir: dir, Reviewer: "author-1"})
	if err == nil || !strings.Contains(err.Error(), "own author") {
		t.Fatalf("self-approval must be rejected, got %v", err)
	}
	if _, err := Commit(index, CommitRequest{Base: base, Dir: dir, Reviewer: "reviewer-1"}); err != nil {
		t.Fatalf("distinct reviewer must succeed: %v", err)
	}
}

func TestCommitMintsDigestNamedImmutableSet(t *testing.T) {
	dir := t.TempDir()
	base := writeBaseSuite(t, dir)
	ledger := newTestLedger(t)
	body := caseJSON("case-c", "knowledge", "new question")
	propose(t, ledger, "author-1", KindAddCase, "case-c", &body)
	index, err := ledger.Load()
	if err != nil {
		t.Fatal(err)
	}
	result, err := Commit(index, CommitRequest{Base: base, Dir: dir, Reviewer: "reviewer-1"})
	if err != nil {
		t.Fatal(err)
	}
	if result.SemanticDigest == base.SemanticDigest {
		t.Fatal("commit must change semantic identity")
	}
	shortDigest := strings.TrimPrefix(string(result.SemanticDigest), "sha256:")[:12]
	if !strings.Contains(filepath.Base(result.Path), shortDigest) {
		t.Fatalf("minted file name %q must embed the semantic digest", result.Path)
	}
	minted, err := LoadSuite(result.Path)
	if err != nil {
		t.Fatal(err)
	}
	if minted.SemanticDigest != result.SemanticDigest || len(minted.Suite.Cases) != 3 {
		t.Fatal("minted set must round-trip to the committed identity")
	}
	// Re-committing the same content must fail: the digest-named file exists.
	if _, err := Commit(index, CommitRequest{Base: base, Dir: dir, Reviewer: "reviewer-1"}); err == nil {
		t.Fatal("re-commit of identical content must be an explicit error")
	}
}

func TestCommitValidatesResultNotProposals(t *testing.T) {
	dir := t.TempDir()
	base := writeBaseSuite(t, dir)
	ledger := newTestLedger(t)
	propose(t, ledger, "author-1", KindRetireCase, "case-a", nil)
	propose(t, ledger, "author-1", KindRetireCase, "case-b", nil)
	index, err := ledger.Load()
	if err != nil {
		t.Fatal(err)
	}
	_, err = Commit(index, CommitRequest{Base: base, Dir: dir, Reviewer: "reviewer-1"})
	if err == nil || !strings.Contains(err.Error(), "invalid") {
		t.Fatalf("retiring every case must fail result validation, got %v", err)
	}
}

// --- Splits ---

func TestClosedSplitIsUnloadable(t *testing.T) {
	dir := t.TempDir()
	path := filepath.Join(dir, "validation.json")
	err := WriteClosedSentinel(path, ClosedSentinel{
		Split:        "validation",
		Reason:       "feedback must pass and reproduce first",
		OpenCriteria: "gate pass on feedback plus fresh-root reproduction",
	})
	if err != nil {
		t.Fatal(err)
	}
	_, err = LoadSplit(path)
	var closed *SplitClosedError
	if !errors.As(err, &closed) {
		t.Fatalf("closed split must yield SplitClosedError, got %v", err)
	}
	if closed.Split != "validation" {
		t.Fatalf("sentinel split mismatch: %+v", closed)
	}
}

func TestOpenSplitRequiresEvidence(t *testing.T) {
	dir := t.TempDir()
	path := filepath.Join(dir, "validation.json")
	if err := WriteClosedSentinel(path, ClosedSentinel{
		Split: "validation", Reason: "closed", OpenCriteria: "criteria",
	}); err != nil {
		t.Fatal(err)
	}
	if _, err := OpenSplit(path, PromotionEvidence{}, baseSuiteBytes(t)); err == nil {
		t.Fatal("open without evidence must fail")
	}
	evidence := PromotionEvidence{
		FeedbackRunID:      "run-1",
		GateDecisionDigest: "sha256:abc",
		Approver:           "human-1",
		Record:             "reference/promotion-decision.md",
	}
	document, err := OpenSplit(path, evidence, baseSuiteBytes(t))
	if err != nil {
		t.Fatal(err)
	}
	if document.Suite.Name != "feedback" {
		t.Fatalf("opened suite mismatch: %+v", document.Suite.Name)
	}
	if _, err := LoadSplit(path); err != nil {
		t.Fatalf("opened split must load: %v", err)
	}
	if _, err := OpenSplit(path, evidence, baseSuiteBytes(t)); err == nil {
		t.Fatal("a split cannot be opened twice")
	}
	if _, err := os.Stat(strings.TrimSuffix(path, ".json") + ".opened.json"); err != nil {
		t.Fatalf("open transition must leave a durable evidence record: %v", err)
	}
}

// --- Lock ---

func writeLock(t *testing.T, dir string, lock Lock) string {
	t.Helper()
	data, err := json.MarshalIndent(lock, "", "  ")
	if err != nil {
		t.Fatal(err)
	}
	path := filepath.Join(dir, "suite-lock.json")
	if err := os.WriteFile(path, data, 0o644); err != nil {
		t.Fatal(err)
	}
	return path
}

func TestLockVerifyAndBindRun(t *testing.T) {
	dir := t.TempDir()
	base := writeBaseSuite(t, dir)
	raw, err := os.ReadFile(base.SourcePath)
	if err != nil {
		t.Fatal(err)
	}
	closedPath := filepath.Join(dir, "validation.json")
	if err := WriteClosedSentinel(closedPath, ClosedSentinel{
		Split: "validation", Reason: "closed", OpenCriteria: "criteria",
	}); err != nil {
		t.Fatal(err)
	}
	closedBytes, err := os.ReadFile(closedPath)
	if err != nil {
		t.Fatal(err)
	}

	lockPath := writeLock(t, dir, Lock{
		SchemaVersion: LockSchemaVersion,
		ReviewStatus:  "approved",
		ReviewedOn:    "2026-08-14",
		ReviewRecord:  "reference/review.md",
		Reviewer:      "reviewer-1",
		Entries: []LockEntry{
			{
				Split:          "feedback",
				Path:           "feedback.json",
				CaseCount:      2,
				SemanticDigest: base.SemanticDigest,
				ByteDigest:     digestBytes(raw),
			},
			{
				Split:      "validation",
				Path:       "validation.json",
				Closed:     true,
				ByteDigest: digestBytes(closedBytes),
			},
		},
	})
	lock, err := LoadLock(lockPath)
	if err != nil {
		t.Fatal(err)
	}
	if err := lock.Verify(dir); err != nil {
		t.Fatalf("verify: %v", err)
	}
	if err := lock.BindRun("feedback", base.SemanticDigest); err != nil {
		t.Fatalf("bind run: %v", err)
	}
	if err := lock.BindRun("feedback", SemanticDigest("sha256:other")); err == nil {
		t.Fatal("an unreviewed suite digest must not bind")
	}
	var closed *SplitClosedError
	if err := lock.BindRun("validation", base.SemanticDigest); !errors.As(err, &closed) {
		t.Fatalf("binding a closed split must yield SplitClosedError, got %v", err)
	}

	// Drift the suite on disk: verification must catch it.
	drifted := strings.Replace(string(raw), "what is a proof coin", "edited question", 1)
	if err := os.WriteFile(base.SourcePath, []byte(drifted), 0o644); err != nil {
		t.Fatal(err)
	}
	if err := lock.Verify(dir); err == nil {
		t.Fatal("drifted suite bytes must fail lock verification")
	}
}

func TestLockRejectsUnapprovedReview(t *testing.T) {
	dir := t.TempDir()
	base := writeBaseSuite(t, dir)
	raw, err := os.ReadFile(base.SourcePath)
	if err != nil {
		t.Fatal(err)
	}
	lockPath := writeLock(t, dir, Lock{
		SchemaVersion: LockSchemaVersion,
		ReviewStatus:  "pending",
		ReviewedOn:    "2026-08-14",
		ReviewRecord:  "reference/review.md",
		Reviewer:      "reviewer-1",
		Entries: []LockEntry{{
			Split: "feedback", Path: "feedback.json", CaseCount: 2,
			SemanticDigest: base.SemanticDigest, ByteDigest: digestBytes(raw),
		}},
	})
	lock, err := LoadLock(lockPath)
	if err != nil {
		t.Fatal(err)
	}
	if err := lock.Verify(dir); err == nil {
		t.Fatal("a lock that is not approved must not verify")
	}
	if err := lock.BindRun("feedback", base.SemanticDigest); err == nil {
		t.Fatal("a run must not bind to an unapproved lock")
	}
}
