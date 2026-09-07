package compiler

import (
	"errors"
	"os"
	"testing"
)

func front(src string) error {
	m, err := Parse(src)
	if err != nil {
		return err
	}
	_, err = lower(m)
	return err
}
func TestFrontend(t *testing.T) {
	src, err := os.ReadFile("../../../examples/sensor.svc")
	if err != nil {
		t.Fatal(err)
	}
	if err = front(string(src)); err != nil {
		t.Fatal(err)
	}
	tests := []struct{ name, src, code string }{
		{"values and branches", `fn pick(flag: Bool, x: I32) -> I32 { let y = x; if flag { y = -2147483648; } else { y = 42; } return y; }`, ""},
		{"unknown local", `fn f() -> I32 { return missing; }`, "E_NAME"},
		{"value type", `fn f() -> I32 { return true; }`, "E_TYPE"},
		{"integer bound", `fn f() -> I32 { return 2147483648; }`, "E_INTEGER"},
		{"shadowing", `fn f(x: I32) -> I32 { let x = 0; return x; }`, "E_SHADOW"},
		{"capability", `fn f() -> Unit { observe(1, 2); return; }`, "E_CAPABILITY"},
		{"recursion", `fn f() -> I32 { return g(); } fn g() -> I32 { return f(); }`, "E_RECURSION"},
		{"nonexhaustive", `fn f(x: Arithmetic) -> I32 { match x { Number(n) => { return n; } } }`, "E_EXHAUSTIVE"},
		{"unsupported", `protocol Other {}`, "E_UNSUPPORTED"},
		{"missing return", `fn f() -> Unit {}`, "E_RETURN"},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			err := front(tt.src)
			if tt.code == "" {
				if err != nil {
					t.Fatal(err)
				}
				return
			}
			var d *Diagnostic
			if !errors.As(err, &d) || d.Code != tt.code {
				t.Fatalf("want %s, got %v", tt.code, err)
			}
		})
	}
}
