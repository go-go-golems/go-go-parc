package judgekernel

import (
	"fmt"
	"reflect"
	"testing"
)

// FuzzAdmit checks the two core structural properties over arbitrary raw
// payloads: (1) Admit is deterministic; (2) whatever Admit accepts passes an
// independent re-implementation of every rule. statementCount and labelCount
// vary the statement list and universe alongside the payload.
func FuzzAdmit(f *testing.F) {
	f.Add(`{"verdicts":[{"statement":1,"supported":true,"evidence_ids":["E1"],"reason":"r"}],"addresses_question":1,"abstained":false}`, 1, 2)
	f.Add(`{"verdicts":[],"addresses_question":0.5,"abstained":true}`, 0, 1)
	f.Add(`{"verdicts":[{"statement":1,"supported":false,"evidence_ids":[],"reason":"no"}],"addresses_question":0,"abstained":false}`, 1, 0)
	f.Add("garbage", 2, 3)
	f.Add(`{"verdicts":[{"statement":1,"supported":true,"evidence_ids":["E1","SQL1"],"reason":"r"},{"statement":2,"supported":false,"evidence_ids":[],"reason":"n"}],"addresses_question":0.7,"abstained":false}`, 2, 1)
	f.Fuzz(func(t *testing.T, raw string, statementCount int, labelCount int) {
		if statementCount < 0 || statementCount > 8 || labelCount < 0 || labelCount > 8 {
			t.Skip()
		}
		statements := make([]string, statementCount)
		for i := range statements {
			statements[i] = fmt.Sprintf("statement %d", i+1)
		}
		labels := append(KnowledgeLabels(labelCount), SQLLabels(1)...)
		universe, err := NewLabelUniverse(labels...)
		if err != nil {
			t.Fatalf("universe: %v", err)
		}
		first, firstErr := Admit(statements, universe, raw)
		second, secondErr := Admit(statements, universe, raw)
		if (firstErr == nil) != (secondErr == nil) {
			t.Fatalf("nondeterministic admission: %v vs %v", firstErr, secondErr)
		}
		if firstErr != nil {
			if firstErr.Error() != secondErr.Error() {
				t.Fatalf("nondeterministic rejection: %v vs %v", firstErr, secondErr)
			}
			var admissionErr *AdmissionError
			if !asError(firstErr, &admissionErr) {
				t.Fatalf("rejection is not an AdmissionError: %v", firstErr)
			}
			return
		}
		if !reflect.DeepEqual(first.Verdicts(), second.Verdicts()) || first.Relevance() != second.Relevance() || first.Abstained() != second.Abstained() {
			t.Fatal("nondeterministic admitted value")
		}
		if !first.Valid() {
			t.Fatal("admitted value not marked valid")
		}
		if violations := revalidate(statements, universe, first); len(violations) != 0 {
			t.Fatalf("admitted payload violates rules: %v\nraw: %q", violations, raw)
		}
		score := ScoreCell(first)
		if value, defined := score.Faithfulness.Value(); defined && (value < 0 || value > 1) {
			t.Fatalf("faithfulness out of bounds: %v", value)
		}
		if score.Faithfulness.Denominator != statementCount {
			t.Fatalf("denominator %d != statement count %d", score.Faithfulness.Denominator, statementCount)
		}
	})
}

// FuzzAdmitStatements checks that statement admission is deterministic and
// that admitted statements are trimmed, non-empty, and duplicate-free.
func FuzzAdmitStatements(f *testing.F) {
	f.Add(`{"statements":[" a ","b","a",""]}`)
	f.Add(`{"statements":[]}`)
	f.Add(`no json`)
	f.Fuzz(func(t *testing.T, raw string) {
		first, firstErr := AdmitStatements(raw)
		second, secondErr := AdmitStatements(raw)
		if (firstErr == nil) != (secondErr == nil) || !reflect.DeepEqual(first, second) {
			t.Fatalf("nondeterministic: %v/%v vs %v/%v", first, firstErr, second, secondErr)
		}
		if firstErr != nil {
			return
		}
		seen := map[string]bool{}
		for _, statement := range first {
			if statement == "" || statement != trimmed(statement) {
				t.Fatalf("statement not trimmed/non-empty: %q", statement)
			}
			if seen[statement] {
				t.Fatalf("duplicate statement admitted: %q", statement)
			}
			seen[statement] = true
		}
	})
}

func trimmed(s string) string {
	for len(s) > 0 && (s[0] == ' ' || s[0] == '\t' || s[0] == '\n' || s[0] == '\r') {
		s = s[1:]
	}
	for len(s) > 0 && (s[len(s)-1] == ' ' || s[len(s)-1] == '\t' || s[len(s)-1] == '\n' || s[len(s)-1] == '\r') {
		s = s[:len(s)-1]
	}
	return s
}
