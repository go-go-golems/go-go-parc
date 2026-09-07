package compiler

import (
	"crypto/sha256"
	"encoding/json"
	"fmt"
)

// CheckedProgram has no public unchecked-IR constructor. Its zero value is invalid.
// The compiler and native toolchain remain trusted; this is an API invariant.
type CheckedProgram struct {
	ir         *unchecked
	sourceHash [32]byte
}

func (p *CheckedProgram) DumpIR() ([]byte, error) {
	if p == nil || p.ir == nil {
		return nil, fmt.Errorf("invalid checked program")
	}
	return json.MarshalIndent(p.ir, "", "  ")
}
func Check(src string) (p *CheckedProgram, err error) {
	m, err := Parse(src)
	if err != nil {
		return nil, err
	}
	u, err := lower(m)
	if err != nil {
		return nil, err
	}
	if err = checkOwnership(u); err != nil {
		return nil, err
	}
	return &CheckedProgram{ir: u, sourceHash: sha256.Sum256([]byte(src))}, nil
}

type states uint8

const (
	uninitialized states = 1 << iota
	live
	consumed
)

type fact struct {
	State  states
	Origin *Span
}
type ledger []fact

func initial(f *functionIR) ledger {
	s := make(ledger, len(f.Slots))
	for i, v := range f.Slots {
		s[i].State = uninitialized
		if v.Parameter {
			s[i].State = live
		}
	}
	return s
}
func cloneLedger(s ledger) ledger { return append(ledger(nil), s...) }
func earlier(a, b *Span) *Span {
	if a == nil {
		return b
	}
	if b == nil {
		return a
	}
	if b.Start < a.Start || b.Start == a.Start && b.End < a.End {
		return b
	}
	return a
}
func mergeLedger(dst *ledger, src ledger) bool {
	if *dst == nil {
		*dst = cloneLedger(src)
		return true
	}
	changed := false
	for i, v := range src {
		old := (*dst)[i]
		next := fact{State: old.State | v.State, Origin: earlier(old.Origin, v.Origin)}
		originChanged := (old.Origin == nil) != (next.Origin == nil)
		if old.Origin != nil && next.Origin != nil {
			originChanged = *old.Origin != *next.Origin
		}
		if next.State != old.State || originChanged {
			(*dst)[i] = next
			changed = true
		}
	}
	return changed
}
func ownershipError(code, msg string, span Span, origin *Span) {
	panic(&Diagnostic{Code: code, Message: msg, Span: span, Related: origin})
}
func transfer(f *functionIR, b block, in ledger, sigs map[string]signature, report bool) ledger {
	s := cloneLedger(in)
	owned := func(id int) bool { return typeTable[f.Slots[id].Type].Owned }
	require := func(id int, span Span) {
		if report && s[id].State != live {
			ownershipError("E_USE", "local is not definitely live", span, s[id].Origin)
		}
	}
	consume := func(id int, span Span) { require(id, span); s[id] = fact{State: consumed, Origin: &span} }
	define := func(id int, span Span) {
		if report && owned(id) && s[id].State&live != 0 {
			ownershipError("E_OVERWRITE", "assignment overwrites a live owner", span, s[id].Origin)
		}
		s[id] = fact{State: live}
	}
	for _, op := range b.Ops {
		switch op.Kind {
		case "constant", "unit":
			define(op.Dest, op.Span)
		case "copy", "field", "compare":
			for _, id := range op.Args {
				require(id, op.Span)
			}
			define(op.Dest, op.Span)
		case "move":
			consume(op.Args[0], op.Span)
			define(op.Dest, op.Span)
		case "assign":
			if owned(op.Args[0]) {
				consume(op.Args[0], op.Span)
			} else {
				require(op.Args[0], op.Span)
			}
			define(op.Dest, op.Span)
		case "read":
			require(op.Args[0], op.Span)
		case "call":
			sig := sigs[op.Name]
			for i, id := range op.Args {
				if owned(id) && !sig.Read[i] {
					consume(id, op.Span)
				} else {
					require(id, op.Span)
				}
			}
			define(op.Dest, op.Span)
		case "scope_exit":
			id := op.Args[0]
			if report && s[id].State&live != 0 {
				ownershipError("E_LEAK", "owner leaves its scope without consumption", op.Span, s[id].Origin)
			}
		default:
			panic("unknown ownership operation")
		}
	}
	switch b.End.Kind {
	case "return":
		id := b.End.Value
		if owned(id) {
			consume(id, b.End.Span)
		} else {
			require(id, b.End.Span)
		}
		if report {
			for i, v := range f.Slots {
				if owned(i) && s[i].State&live != 0 {
					ownershipError("E_LEAK", "unconsumed owner "+v.Name+" at return", b.End.Span, &v.Span)
				}
			}
		}
	case "match":
		if owned(b.End.Value) {
			consume(b.End.Value, b.End.Span)
		} else {
			require(b.End.Value, b.End.Span)
		}
	case "branch":
		require(b.End.Value, b.End.Span)
	case "jump":
	default:
		panic("unterminated CFG block")
	}
	return s
}
func checkOwnership(u *unchecked) error { return inspectOwnership(u, nil) }

func inspectOwnership(u *unchecked, observe func(*functionIR, []ledger)) (err error) {
	defer diagnostic(&err)
	for _, f := range u.Functions {
		incoming := make([]ledger, len(f.Blocks))
		incoming[0] = initial(f)
		queue := []int{0}
		queued := make([]bool, len(f.Blocks))
		queued[0] = true
		// Finite powerset union plus monotone transfers. Diagnostics are emitted only
		// after convergence, never from transient worklist states.
		for len(queue) > 0 {
			id := queue[0]
			queue = queue[1:]
			queued[id] = false
			b := f.Blocks[id]
			out := transfer(f, b, incoming[id], u.Signatures, false)
			for _, e := range b.End.Edges {
				candidate := cloneLedger(out)
				for _, binding := range e.Bindings {
					candidate[binding] = fact{State: live}
				}
				if mergeLedger(&incoming[e.Target], candidate) && !queued[e.Target] {
					queue = append(queue, e.Target)
					queued[e.Target] = true
				}
			}
		}
		if observe != nil {
			observe(f, incoming)
		}
		for id, b := range f.Blocks {
			if incoming[id] == nil {
				continue
			}
			for i, v := range incoming[id] {
				if typeTable[f.Slots[i].Type].Owned && v.State&live != 0 && v.State != live {
					ownershipError("E_JOIN", "incoming paths disagree on owner "+f.Slots[i].Name, b.End.Span, v.Origin)
				}
			}
			transfer(f, b, incoming[id], u.Signatures, true)
		}
	}
	return nil
}
