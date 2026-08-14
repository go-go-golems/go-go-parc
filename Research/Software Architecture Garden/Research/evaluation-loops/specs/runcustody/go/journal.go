// Package runcustody is a research prototype extracting the run-custody
// algebra shared by ragopt (hash-chained cell journal, exact-coordinate
// resume) and CoinVault (pre-reserving budget accountant with sticky
// conservative close). It is deliberately dependency-free.
//
// The journal mirrors ragopt pkg/eval/cell_chain.go (seal/validate),
// pkg/runstore/run.go AppendJSONL (append+fsync commit boundary), and
// pkg/eval/resume.go loadCompletedCells (torn-tail truncation, strict
// decode, chain validation, schedule-membership and duplicate rejection).
package runcustody

import (
	"bytes"
	"crypto/sha256"
	"encoding/hex"
	"encoding/json"
	"errors"
	"fmt"
	"os"
	"path/filepath"
	"strings"
)

const RecordAPIVersion = "runcustody-record/v1"

// Coord is the exact identity of one unit of scheduled work. Two records
// with equal coordinates are the same work; committing both is a protocol
// violation.
type Coord struct {
	CaseID string `json:"case_id"`
	Repeat int    `json:"repeat"`
	Arm    string `json:"arm"`
}

// Key is the exact-coordinate join key (NUL-joined like ragopt's
// expectedCellKey, which additionally binds suite/policy/candidate digests;
// the prototype's schedule is assumed already identity-bound).
func (c Coord) Key() string {
	return strings.Join([]string{c.CaseID, fmt.Sprintf("%d", c.Repeat), c.Arm}, "\x00")
}

// Record is one committed cell: a payload at an exact coordinate, sealed
// into a hash chain.
type Record struct {
	APIVersion     string          `json:"api_version"`
	Coord          Coord           `json:"coord"`
	Payload        json.RawMessage `json:"payload,omitempty"`
	PreviousDigest string          `json:"previous_digest"`
	Digest         string          `json:"digest"`
}

func digestBytes(data []byte) string {
	sum := sha256.Sum256(data)
	return "sha256:" + hex.EncodeToString(sum[:])
}

// seal fixes the record's chain position: PreviousDigest links to the
// journal head and Digest covers every field with Digest itself blank.
func seal(record *Record, previous string) error {
	if record == nil {
		return errors.New("record is nil")
	}
	record.APIVersion = RecordAPIVersion
	record.PreviousDigest = previous
	record.Digest = ""
	data, err := json.Marshal(record)
	if err != nil {
		return fmt.Errorf("marshal record identity: %w", err)
	}
	record.Digest = digestBytes(data)
	return nil
}

// validateChain checks one record against the running head, exactly as
// ragopt validateCellChain: stored previous digest must equal the head, and
// the stored digest must recompute from the record with Digest blanked.
func validateChain(record Record, previous string) error {
	if record.APIVersion != RecordAPIVersion {
		return fmt.Errorf("unsupported record api version %q", record.APIVersion)
	}
	if record.PreviousDigest != previous {
		return fmt.Errorf("previous digest mismatch: record=%q expected=%q", record.PreviousDigest, previous)
	}
	claimed := record.Digest
	if !strings.HasPrefix(claimed, "sha256:") || len(claimed) != len("sha256:")+64 {
		return errors.New("record digest is invalid")
	}
	record.Digest = ""
	data, err := json.Marshal(record)
	if err != nil {
		return fmt.Errorf("marshal record identity: %w", err)
	}
	if actual := digestBytes(data); actual != claimed {
		return fmt.Errorf("record digest mismatch: stored=%s actual=%s", claimed, actual)
	}
	return nil
}

// Journal owns one append-only JSONL file for a single writer.
type Journal struct {
	path string
	head string
}

// Open validates the journal against the exact schedule and returns the
// committed records keyed by coordinate. Recovery truncates a torn tail
// (a final line without a newline) and fsyncs the truncation before any
// record is trusted. Every retained line must strict-decode, chain-link,
// belong to the schedule, and appear at most once.
func Open(path string, schedule []Coord) (*Journal, map[string]Record, error) {
	expected := make(map[string]struct{}, len(schedule))
	for _, coord := range schedule {
		if _, exists := expected[coord.Key()]; exists {
			return nil, nil, fmt.Errorf("schedule contains duplicate coordinate %q", coord.Key())
		}
		expected[coord.Key()] = struct{}{}
	}
	journal := &Journal{path: path}
	data, err := os.ReadFile(path)
	if err != nil {
		if os.IsNotExist(err) {
			return journal, map[string]Record{}, nil
		}
		return nil, nil, fmt.Errorf("read journal: %w", err)
	}
	if len(data) > 0 && data[len(data)-1] != '\n' {
		lastNewline := bytes.LastIndexByte(data, '\n')
		keep := 0
		if lastNewline >= 0 {
			keep = lastNewline + 1
		}
		if err := truncateAndSync(path, int64(keep)); err != nil {
			return nil, nil, fmt.Errorf("discard torn tail: %w", err)
		}
		data = data[:keep]
	}
	completed := make(map[string]Record)
	head := ""
	lines := bytes.Split(data, []byte{'\n'})
	for index, line := range lines {
		if len(line) == 0 {
			if index != len(lines)-1 {
				return nil, nil, fmt.Errorf("journal line %d is blank", index+1)
			}
			continue
		}
		var record Record
		decoder := json.NewDecoder(bytes.NewReader(line))
		decoder.DisallowUnknownFields()
		if err := decoder.Decode(&record); err != nil {
			return nil, nil, fmt.Errorf("decode journal line %d: %w", index+1, err)
		}
		if err := validateChain(record, head); err != nil {
			return nil, nil, fmt.Errorf("validate journal line %d: %w", index+1, err)
		}
		key := record.Coord.Key()
		if _, exists := expected[key]; !exists {
			return nil, nil, fmt.Errorf("journal line %d has an unexpected identity", index+1)
		}
		if _, exists := completed[key]; exists {
			return nil, nil, fmt.Errorf("duplicate journal coordinate on line %d", index+1)
		}
		completed[key] = record
		head = record.Digest
	}
	journal.head = head
	return journal, completed, nil
}

// Append seals the record against the current head and commits it with one
// write+fsync. Successful return is the durability boundary; the head
// advances only after fsync succeeds.
func (j *Journal) Append(record Record) error {
	if j == nil {
		return errors.New("journal is nil")
	}
	if err := seal(&record, j.head); err != nil {
		return err
	}
	data, err := json.Marshal(record)
	if err != nil {
		return fmt.Errorf("marshal sealed record: %w", err)
	}
	created := false
	if _, err := os.Lstat(j.path); os.IsNotExist(err) {
		created = true
	} else if err != nil {
		return fmt.Errorf("inspect journal: %w", err)
	}
	file, err := os.OpenFile(j.path, os.O_CREATE|os.O_APPEND|os.O_WRONLY, 0o600)
	if err != nil {
		return fmt.Errorf("open journal: %w", err)
	}
	if _, err := file.Write(append(data, '\n')); err != nil {
		_ = file.Close()
		return fmt.Errorf("append journal: %w", err)
	}
	if err := file.Sync(); err != nil {
		_ = file.Close()
		return fmt.Errorf("sync journal: %w", err)
	}
	if err := file.Close(); err != nil {
		return fmt.Errorf("close journal: %w", err)
	}
	if created {
		if err := syncDirectory(filepath.Dir(j.path)); err != nil {
			return err
		}
	}
	j.head = record.Digest
	return nil
}

// Head returns the digest of the last committed record ("" when empty).
func (j *Journal) Head() string {
	if j == nil {
		return ""
	}
	return j.head
}

func truncateAndSync(path string, size int64) error {
	file, err := os.OpenFile(path, os.O_WRONLY, 0)
	if err != nil {
		return fmt.Errorf("open journal for recovery: %w", err)
	}
	if err := file.Truncate(size); err != nil {
		_ = file.Close()
		return fmt.Errorf("truncate journal: %w", err)
	}
	if err := file.Sync(); err != nil {
		_ = file.Close()
		return fmt.Errorf("sync recovered journal: %w", err)
	}
	if err := file.Close(); err != nil {
		return fmt.Errorf("close recovered journal: %w", err)
	}
	return syncDirectory(filepath.Dir(path))
}

func syncDirectory(path string) error {
	directory, err := os.Open(path)
	if err != nil {
		return fmt.Errorf("open directory for sync: %w", err)
	}
	if err := directory.Sync(); err != nil {
		_ = directory.Close()
		return fmt.Errorf("sync directory: %w", err)
	}
	if err := directory.Close(); err != nil {
		return fmt.Errorf("close synced directory: %w", err)
	}
	return nil
}
