package compiler

import (
	"errors"
	"os"
	"strings"
	"testing"
)

func TestOwnership(t *testing.T) {
	tests := []struct{ name, src, code, at string }{
		{"close once", `use sensor; fn f(own r: Ready) -> Unit { close(move r); return; }`, "", ""},
		{"close twice", `use sensor; fn f(own r: Ready) -> Unit { close(move r); close(move r); return; }`, "E_USE", "move r); return"},
		{"implicit copy", `use sensor; fn f(own r: Ready) -> Ready { return r; }`, "E_MOVE", "r; }"},
		{"owner return", `use sensor; fn f(own r: Ready) -> Ready { return move r; }`, "", ""},
		{"owner leak", `use sensor; fn f(own r: Ready) -> Unit { return; }`, "E_LEAK", "return"},
		{"both branches consume", `use sensor; fn f(own r: Ready, flag: Bool) -> Unit { if flag { close(move r); } else { close(move r); } return; }`, "", ""},
		{"one branch consumes", `use sensor; fn f(own r: Ready, flag: Bool) -> Unit { if flag { close(move r); } return; }`, "E_JOIN", "return"},
		{"returned branch does not join", `use sensor; fn f(own r: Ready, flag: Bool) -> Ready { if flag { return move r; } return move r; }`, "", ""},
		{"replace consumed destination", `use sensor; fn f(own a: Ready, own b: Ready) -> Ready { close(move a); a = move b; return move a; }`, "", ""},
		{"overwrite live destination", `use sensor; fn f(own a: Ready, own b: Ready) -> Ready { a = move b; return move a; }`, "E_OVERWRITE", "a ="},
		{"read before release", `use memory; fn f(own b: Buffer) -> I32 { let n = length(b); release(move b); return n; }`, "", ""},
		{"read after release", `use memory; fn f(own b: Buffer) -> I32 { release(move b); let n = length(b); return n; }`, "E_USE", "b); return"},
		{"argument order", `use memory; fn sink(own data: Buffer, n: I32) -> I32 { release(move data); return n; } fn f(own b: Buffer) -> I32 { let n = length(b); return sink(move b, n); }`, "", ""},
		{"later argument reads moved owner", `use memory; fn sink(own data: Buffer, n: I32) -> I32 { release(move data); return n; } fn f(own b: Buffer) -> I32 { return sink(move b, length(b)); }`, "E_USE", "b));"},
		{"consume active payload", `use memory; fn f(own result: Allocation) -> Unit { match move result { Allocated(b) => { release(move b); return; } AllocFailed(error) => { return; } } }`, "", ""},
		{"drop active payload", `use memory; fn f(own result: Allocation) -> Unit { match move result { Allocated(b) => { return; } AllocFailed(error) => { return; } } }`, "E_LEAK", "return;"},
		{"discard result", `use memory; fn f() -> Unit { allocate(8); return; }`, "E_DISCARD", "allocate"},
		{"ignore owned field", `use memory; fn f(own result: Allocation) -> Unit { match move result { Allocated => { return; } AllocFailed(error) => { return; } } }`, "E_ARITY", "Allocated"},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			p, err := Check(tt.src)
			if tt.code == "" {
				if err != nil {
					t.Fatal(err)
				}
				if _, err = p.DumpIR(); err != nil {
					t.Fatal(err)
				}
				return
			}
			var d *Diagnostic
			if !errors.As(err, &d) || d.Code != tt.code {
				t.Fatalf("want %s, got %v", tt.code, err)
			}
			if p != nil {
				t.Fatal("rejected source returned checked program")
			}
			if want := strings.Index(tt.src, tt.at); d.Span.Start != want {
				t.Fatalf("span %d, want %d (%s)", d.Span.Start, want, tt.at)
			}
			if tt.name == "close twice" && (d.Related == nil || d.Related.Start != strings.Index(tt.src, "move r")) {
				t.Fatalf("missing first move provenance: %+v", d)
			}
		})
	}
	src, err := os.ReadFile("../../../examples/sensor.svc")
	if err != nil {
		t.Fatal(err)
	}
	if _, err = Check(string(src)); err != nil {
		t.Fatal(err)
	}
	if _, err = (*CheckedProgram)(nil).DumpIR(); err == nil {
		t.Fatal("nil accepted")
	}
	if _, err = (&CheckedProgram{}).DumpIR(); err == nil {
		t.Fatal("zero value accepted")
	}
}
