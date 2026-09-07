package compiler

import (
	"errors"
	"testing"
)

func TestProtocolRejection(t *testing.T) {
	cases := []struct{ src, code string }{
		{`use sensor; fn f(own pending: Pending, now: Time) -> StartResult { return rpc_start(move pending, now, 10); }`, "E_TYPE"},
		{`use sensor; fn f(own p: PollResult) -> Step { match move p { Complete(r, c) => { return Finished(move c); } } }`, "E_EXHAUSTIVE"},
		{`use sensor; fn f(r: CallResult) -> Unit { match r { Ok(s) => { return; } RemoteError(e) => { return; } NotSent => { return; } RuntimeFault(fault) => { return; } } }`, "E_EXHAUSTIVE"},
		{`use sensor; fn f(own c: Continuation) -> Unit { match move c { Reusable(r) => { close(move r); return; } } }`, "E_EXHAUSTIVE"},
	}
	for _, tc := range cases {
		p, err := Check(tc.src)
		var d *Diagnostic
		if p != nil || !errors.As(err, &d) || d.Code != tc.code {
			t.Fatalf("want %s: %v", tc.code, err)
		}
	}
}
