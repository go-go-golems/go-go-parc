package compiler

import (
	"crypto/sha256"
	"encoding/hex"
	"errors"
	"fmt"
)

type Stage struct{ Name, Status, Detail string }
type SlotView struct {
	ID         int
	Name, Type string
	Owned      bool
	Span       Span
}
type FactView struct {
	Slot   int
	States []string
	Origin *Span
}
type BlockView struct {
	ID      int
	Ops     []operation
	End     terminator
	In, Out []FactView
}
type FunctionView struct {
	Name   string
	Slots  []SlotView
	Blocks []BlockView
}
type Inspection struct {
	Accepted          bool
	SourceSHA256      string
	Stages            []Stage
	Diagnostics       []*Diagnostic
	AST               *Module `json:",omitempty"`
	Functions         []FunctionView
	Output            *Output `json:",omitempty"`
	PlanAccepted      *bool   `json:",omitempty"`
	InspectionLimited bool
}

func facts(s ledger) []FactView {
	if s == nil {
		return nil
	}
	result := make([]FactView, len(s))
	for id, v := range s {
		item := FactView{Slot: id, Origin: v.Origin}
		for _, p := range []struct {
			bit  states
			name string
		}{{uninitialized, "U"}, {live, "L"}, {consumed, "D"}} {
			if v.State&p.bit != 0 {
				item.States = append(item.States, p.name)
			}
		}
		result[id] = item
	}
	return result
}

// Inspect uses the same parser, lowering and solver as Check, with a read-only
// observation callback. Invalid source can expose analysis facts, never native output.
func Inspect(sourceFile, source string, plan []byte) (*Inspection, error) {
	hash := sha256.Sum256([]byte(source))
	r := &Inspection{SourceSHA256: hex.EncodeToString(hash[:]), Stages: []Stage{{"Parse", "pending", "syntax.go: Parse"}, {"Resolve / types / CFG", "pending", "lower.go: lower"}, {"Ownership", "pending", "check.go: inspectOwnership"}, {"C++ emission", "pending", "cpp.go: EmitCPP"}}}
	reject := func(stage int, err error) (*Inspection, error) {
		var d *Diagnostic
		if !errors.As(err, &d) {
			return nil, err
		}
		r.Stages[stage].Status = "rejected"
		r.Diagnostics = append(r.Diagnostics, d)
		return r, nil
	}
	m, err := Parse(source)
	if err != nil {
		return reject(0, err)
	}
	r.AST = m
	r.Stages[0].Status = "passed"
	u, err := lower(m)
	if err != nil {
		return reject(1, err)
	}
	r.Stages[1].Status = "passed"
	indices := map[string]int{}
	for i, f := range u.Functions {
		indices[f.Name] = i
		view := FunctionView{Name: f.Name}
		for id, s := range f.Slots {
			view.Slots = append(view.Slots, SlotView{id, s.Name, s.Type, typeTable[s.Type].Owned, s.Span})
		}
		for id, b := range f.Blocks {
			view.Blocks = append(view.Blocks, BlockView{ID: id, Ops: b.Ops, End: b.End})
		}
		r.Functions = append(r.Functions, view)
	}
	cells := 0
	err = inspectOwnership(u, func(f *functionIR, in []ledger) {
		view := &r.Functions[indices[f.Name]]
		for id, s := range in {
			// Bound inspection amplification without skipping any compiler checks.
			if cells+2*len(s) > 100000 {
				r.InspectionLimited = true
				continue
			}
			cells += 2 * len(s)
			view.Blocks[id].In = facts(s)
			if s != nil {
				view.Blocks[id].Out = facts(transfer(f, f.Blocks[id], s, u.Signatures, false))
			}
		}
	})
	if err != nil {
		return reject(2, err)
	}
	r.Stages[2].Status = "passed"
	p := &CheckedProgram{ir: u, sourceHash: hash}
	if len(plan) > 0 {
		r.Stages = append(r.Stages, Stage{"Startup plan", "pending", "plan.go: CheckPlan"})
		cp, err := CheckPlan(p, plan)
		ok := err == nil
		r.PlanAccepted = &ok
		if err != nil {
			return reject(4, err)
		}
		r.Stages[4].Status = "passed"
		r.Output, err = EmitApplication(cp, sourceFile, source)
		if err != nil {
			return nil, err
		}
	} else {
		r.Output, err = EmitCPP(p, sourceFile, source)
		if err != nil {
			return nil, err
		}
	}
	r.Stages[3].Status = "passed"
	r.Accepted = true
	return r, nil
}

// ImplementationFiles exposes only the compiler sources embedded in this binary,
// never arbitrary paths from the request or host filesystem.
func ImplementationFiles() (map[string]string, error) {
	entries, err := implementation.ReadDir(".")
	if err != nil {
		return nil, err
	}
	files := map[string]string{}
	for _, e := range entries {
		data, err := implementation.ReadFile(e.Name())
		if err != nil {
			return nil, fmt.Errorf("embedded implementation: %w", err)
		}
		files[e.Name()] = string(data)
	}
	return files, nil
}
