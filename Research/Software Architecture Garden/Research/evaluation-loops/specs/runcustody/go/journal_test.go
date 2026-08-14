package runcustody

import (
	"bytes"
	"encoding/json"
	"os"
	"path/filepath"
	"strings"
	"testing"
)

func testSchedule() []Coord {
	return []Coord{
		{CaseID: "c1", Repeat: 0, Arm: "incumbent"},
		{CaseID: "c1", Repeat: 0, Arm: "challenger"},
		{CaseID: "c2", Repeat: 0, Arm: "incumbent"},
		{CaseID: "c2", Repeat: 0, Arm: "challenger"},
	}
}

func journalPath(t *testing.T) string {
	t.Helper()
	return filepath.Join(t.TempDir(), "cells.jsonl")
}

func mustAppend(t *testing.T, journal *Journal, coord Coord) {
	t.Helper()
	payload, _ := json.Marshal(map[string]string{"result": "ok-" + coord.Key()})
	if err := journal.Append(Record{Coord: coord, Payload: payload}); err != nil {
		t.Fatalf("append %v: %v", coord, err)
	}
}

func TestJournalRoundTrip(t *testing.T) {
	schedule := testSchedule()
	path := journalPath(t)
	journal, completed, err := Open(path, schedule)
	if err != nil || len(completed) != 0 {
		t.Fatalf("open empty: %v completed=%d", err, len(completed))
	}
	for _, coord := range schedule {
		mustAppend(t, journal, coord)
	}
	_, reloaded, err := Open(path, schedule)
	if err != nil {
		t.Fatalf("reopen: %v", err)
	}
	if len(reloaded) != len(schedule) {
		t.Fatalf("reloaded %d records, want %d", len(reloaded), len(schedule))
	}
	for _, coord := range schedule {
		if _, exists := reloaded[coord.Key()]; !exists {
			t.Fatalf("missing coordinate %q after reload", coord.Key())
		}
	}
}

func TestTornTailTruncatedAndJournalContinues(t *testing.T) {
	schedule := testSchedule()
	path := journalPath(t)
	journal, _, err := Open(path, schedule)
	if err != nil {
		t.Fatal(err)
	}
	mustAppend(t, journal, schedule[0])
	mustAppend(t, journal, schedule[1])
	// Crash mid-append: a partial record without a trailing newline.
	file, err := os.OpenFile(path, os.O_APPEND|os.O_WRONLY, 0)
	if err != nil {
		t.Fatal(err)
	}
	if _, err := file.Write([]byte(`{"api_version":"runcustody-record/v1","coord":{"ca`)); err != nil {
		t.Fatal(err)
	}
	_ = file.Close()

	recovered, completed, err := Open(path, schedule)
	if err != nil {
		t.Fatalf("recovery open: %v", err)
	}
	if len(completed) != 2 {
		t.Fatalf("recovered %d records, want 2", len(completed))
	}
	data, _ := os.ReadFile(path)
	if len(data) == 0 || data[len(data)-1] != '\n' {
		t.Fatalf("torn tail was not truncated: %q", string(data))
	}
	// The recovered journal must keep accepting appends on the surviving head.
	mustAppend(t, recovered, schedule[2])
	_, completed, err = Open(path, schedule)
	if err != nil || len(completed) != 3 {
		t.Fatalf("post-recovery append: %v completed=%d", err, len(completed))
	}
}

func TestInPlaceEditDetected(t *testing.T) {
	schedule := testSchedule()
	path := journalPath(t)
	journal, _, err := Open(path, schedule)
	if err != nil {
		t.Fatal(err)
	}
	mustAppend(t, journal, schedule[0])
	mustAppend(t, journal, schedule[1])
	data, _ := os.ReadFile(path)
	edited := bytes.Replace(data, []byte("ok-"), []byte("KO-"), 1)
	if bytes.Equal(edited, data) {
		t.Fatal("edit fixture did not change the journal")
	}
	if err := os.WriteFile(path, edited, 0o600); err != nil {
		t.Fatal(err)
	}
	if _, _, err := Open(path, schedule); err == nil || !strings.Contains(err.Error(), "digest mismatch") {
		t.Fatalf("edited record not detected: %v", err)
	}
}

func TestReorderDetected(t *testing.T) {
	schedule := testSchedule()
	path := journalPath(t)
	journal, _, err := Open(path, schedule)
	if err != nil {
		t.Fatal(err)
	}
	mustAppend(t, journal, schedule[0])
	mustAppend(t, journal, schedule[1])
	data, _ := os.ReadFile(path)
	lines := bytes.Split(bytes.TrimSuffix(data, []byte("\n")), []byte("\n"))
	if len(lines) != 2 {
		t.Fatalf("fixture lines: %d", len(lines))
	}
	swapped := append(append(append([]byte{}, lines[1]...), '\n'), append(lines[0], '\n')...)
	if err := os.WriteFile(path, swapped, 0o600); err != nil {
		t.Fatal(err)
	}
	if _, _, err := Open(path, schedule); err == nil || !strings.Contains(err.Error(), "previous digest mismatch") {
		t.Fatalf("reordered journal not detected: %v", err)
	}
}

func TestDeletionDetected(t *testing.T) {
	schedule := testSchedule()
	path := journalPath(t)
	journal, _, err := Open(path, schedule)
	if err != nil {
		t.Fatal(err)
	}
	mustAppend(t, journal, schedule[0])
	mustAppend(t, journal, schedule[1])
	data, _ := os.ReadFile(path)
	lines := bytes.SplitAfter(data, []byte("\n"))
	// Drop the first committed record but keep the second.
	if err := os.WriteFile(path, lines[1], 0o600); err != nil {
		t.Fatal(err)
	}
	if _, _, err := Open(path, schedule); err == nil || !strings.Contains(err.Error(), "previous digest mismatch") {
		t.Fatalf("deleted prefix not detected: %v", err)
	}
}

func TestDuplicateCoordinateDetected(t *testing.T) {
	schedule := testSchedule()
	path := journalPath(t)
	journal, _, err := Open(path, schedule)
	if err != nil {
		t.Fatal(err)
	}
	mustAppend(t, journal, schedule[0])
	// A correctly sealed record at an already-committed coordinate: the
	// chain is valid, so only the duplicate check can reject it.
	mustAppend(t, journal, schedule[0])
	if _, _, err := Open(path, schedule); err == nil || !strings.Contains(err.Error(), "duplicate journal coordinate") {
		t.Fatalf("duplicate coordinate not detected: %v", err)
	}
}

func TestUnexpectedIdentityDetected(t *testing.T) {
	schedule := testSchedule()
	path := journalPath(t)
	journal, _, err := Open(path, schedule)
	if err != nil {
		t.Fatal(err)
	}
	mustAppend(t, journal, Coord{CaseID: "not-in-schedule", Repeat: 9, Arm: "rogue"})
	if _, _, err := Open(path, schedule); err == nil || !strings.Contains(err.Error(), "unexpected identity") {
		t.Fatalf("foreign coordinate not detected: %v", err)
	}
}
