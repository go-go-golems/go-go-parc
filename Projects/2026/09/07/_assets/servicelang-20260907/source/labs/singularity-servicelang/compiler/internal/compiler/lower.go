package compiler

import "fmt"

type lowerer struct {
	f       *functionIR
	sigs    map[string]signature
	imports map[string]bool
	used    map[string]bool
	current int
}
type environment map[string]int

func child(e environment) environment {
	n := environment{}
	for k, v := range e {
		n[k] = v
	}
	return n
}
func requireType(name string, imports map[string]bool, span Span) {
	t, ok := typeTable[name]
	if !ok {
		fail("E_TYPE", "unknown type "+name, span)
	}
	if t.Capability != "" && !imports[t.Capability] {
		fail("E_CAPABILITY", "type requires use "+t.Capability, span)
	}
}
func sameType(want, got string, span Span) {
	if want != got {
		fail("E_TYPE", fmt.Sprintf("expected %s, got %s", want, got), span)
	}
}
func (l *lowerer) newSlot(name, typ string, span Span, temp bool) int {
	if len(l.f.Slots) >= 256 {
		fail("E_LIMIT", "function exceeds 256 storage slots", span)
	}
	if !temp {
		if l.used[name] {
			fail("E_SHADOW", "duplicate or shadowed local "+name, span)
		}
		if _, exists := l.sigs[name]; exists {
			fail("E_SHADOW", "local shadows callable "+name, span)
		}
		l.used[name] = true
	}
	id := len(l.f.Slots)
	l.f.Slots = append(l.f.Slots, slot{Name: name, Type: typ, Span: span, Temporary: temp})
	return id
}
func (l *lowerer) temp(typ string, span Span) int { return l.newSlot("", typ, span, true) }
func (l *lowerer) op(kind, name string, dest int, args []int, span Span) {
	l.f.Blocks[l.current].Ops = append(l.f.Blocks[l.current].Ops, operation{kind, name, dest, args, span})
}
func (l *lowerer) lookup(name string, e environment, span Span) int {
	id, ok := e[name]
	if !ok {
		fail("E_NAME", "unknown local "+name, span)
	}
	return id
}
func (l *lowerer) expr(e *Expr, env environment) int {
	if e == nil {
		id := l.temp("Unit", Span{})
		l.op("unit", "", id, nil, Span{})
		return id
	}
	switch e.Kind {
	case "integer", "bool":
		typ := "I32"
		if e.Kind == "bool" {
			typ = "Bool"
		}
		id := l.temp(typ, e.Span)
		l.op("constant", e.Text, id, nil, e.Span)
		return id
	case "var", "move":
		src := l.lookup(e.Text, env, e.Span)
		typ := l.f.Slots[src].Type
		owned := typeTable[typ].Owned
		if owned && e.Kind != "move" {
			fail("E_MOVE", "owner requires explicit move", e.Span)
		}
		if !owned && e.Kind == "move" {
			fail("E_MOVE_VALUE", "move requires a resource", e.Span)
		}
		id := l.temp(typ, e.Span)
		kind := "copy"
		if owned {
			kind = "move"
		}
		l.op(kind, "", id, []int{src}, e.Span)
		return id
	case "field":
		src := l.expr(e.Args[0], env)
		typ, ok := typeTable[l.f.Slots[src].Type].Fields[e.Text]
		if !ok {
			fail("E_FIELD", "unknown copyable record field", e.Span)
		}
		id := l.temp(typ, e.Span)
		l.op("field", e.Text, id, []int{src}, e.Span)
		return id
	case "compare":
		a := l.expr(e.Args[0], env)
		b := l.expr(e.Args[1], env)
		typ := l.f.Slots[a].Type
		sameType(typ, l.f.Slots[b].Type, e.Span)
		if typ != "I32" && typ != "Time" && !(typ == "Bool" && (e.Text == "==" || e.Text == "!=")) {
			fail("E_OPERATOR", "comparison requires matching scalar types", e.Span)
		}
		id := l.temp("Bool", e.Span)
		l.op("compare", e.Text, id, []int{a, b}, e.Span)
		return id
	case "call":
		sig, ok := l.sigs[e.Text]
		if !ok {
			fail("E_NAME", "unknown function or constructor "+e.Text, e.Span)
		}
		if sig.Capability != "" && !l.imports[sig.Capability] {
			fail("E_CAPABILITY", "call requires use "+sig.Capability, e.Span)
		}
		if len(e.Args) != len(sig.Args) {
			fail("E_ARITY", "wrong argument count", e.Span)
		}
		var args []int
		for i, a := range e.Args {
			var id int
			if sig.Read[i] {
				if a.Kind != "var" {
					fail("E_READ", "restricted read requires an owned local", a.Span)
				}
				id = l.lookup(a.Text, env, a.Span)
				l.op("read", "", -1, []int{id}, a.Span)
			} else {
				id = l.expr(a, env)
			}
			sameType(sig.Args[i], l.f.Slots[id].Type, a.Span)
			args = append(args, id)
		}
		id := l.temp(sig.Result, e.Span)
		l.op("call", e.Text, id, args, e.Span)
		if sig.User {
			l.f.Calls = append(l.f.Calls, e.Text)
		}
		return id
	}
	panic("unknown expression kind")
}
func (l *lowerer) newBlock() int {
	id := len(l.f.Blocks)
	l.f.Blocks = append(l.f.Blocks, block{})
	return id
}
func (l *lowerer) jump(from, to int, span Span) {
	l.f.Blocks[from].End = terminator{Kind: "jump", Edges: []edge{{Target: to}}, Span: span}
}
func (l *lowerer) body(stmts []Stmt, env environment, start int, bindings []int) int {
	l.current = start
	locals := append([]int(nil), bindings...)
	for _, s := range stmts {
		if l.current < 0 {
			fail("E_UNREACHABLE", "statement after terminal control flow", s.Span)
		}
		switch s.Kind {
		case "let":
			value := l.expr(s.Expr, env)
			id := l.newSlot(s.Name, l.f.Slots[value].Type, s.Span, false)
			env[s.Name] = id
			locals = append(locals, id)
			l.op("assign", "", id, []int{value}, s.Span)
		case "assign":
			id := l.lookup(s.Name, env, s.Span)
			value := l.expr(s.Expr, env)
			sameType(l.f.Slots[id].Type, l.f.Slots[value].Type, s.Span)
			l.op("assign", "", id, []int{value}, s.Span)
		case "expr":
			id := l.expr(s.Expr, env)
			if typeTable[l.f.Slots[id].Type].Owned {
				fail("E_DISCARD", "resource result must be consumed", s.Span)
			}
		case "return":
			id := l.expr(s.Expr, env)
			sameType(l.f.Result, l.f.Slots[id].Type, s.Span)
			l.f.Blocks[l.current].End = terminator{Kind: "return", Value: id, Span: s.Span}
			l.current = -1
		case "if":
			value := l.expr(s.Expr, env)
			sameType("Bool", l.f.Slots[value].Type, s.Span)
			from := l.current
			a := l.newBlock()
			b := l.newBlock()
			l.f.Blocks[from].End = terminator{Kind: "branch", Value: value, Edges: []edge{{Target: a}, {Target: b}}, Span: s.Span}
			ae := l.body(s.Body, child(env), a, nil)
			be := l.body(s.Else, child(env), b, nil)
			l.current = -1
			if ae >= 0 || be >= 0 {
				join := l.newBlock()
				if ae >= 0 {
					l.jump(ae, join, s.Span)
				}
				if be >= 0 {
					l.jump(be, join, s.Span)
				}
				l.current = join
			}
		case "match":
			value := l.expr(s.Expr, env)
			typ := l.f.Slots[value].Type
			variants := typeTable[typ].Variants
			if len(variants) == 0 {
				fail("E_MATCH", "match requires a variant type", s.Span)
			}
			from := l.current
			term := terminator{Kind: "match", Value: value, Span: s.Span}
			seen := map[string]bool{}
			var ends []int
			for _, arm := range s.Arms {
				sig, ok := l.sigs[arm.Name]
				if !ok || !sig.Constructor || sig.Result != typ {
					fail("E_VARIANT", "variant does not belong to "+typ, arm.Span)
				}
				if seen[arm.Name] {
					fail("E_DUPLICATE", "duplicate match arm", arm.Span)
				}
				seen[arm.Name] = true
				if len(arm.Names) != len(sig.Args) {
					fail("E_ARITY", "match must bind every payload field", arm.Span)
				}
				armEnv := child(env)
				var ids []int
				for i, n := range arm.Names {
					id := l.newSlot(n.text, sig.Args[i], n.span, false)
					armEnv[n.text] = id
					ids = append(ids, id)
				}
				target := l.newBlock()
				term.Edges = append(term.Edges, edge{target, arm.Name, ids})
				end := l.body(arm.Body, armEnv, target, ids)
				if end >= 0 {
					ends = append(ends, end)
				}
			}
			for _, v := range variants {
				if !seen[v] {
					fail("E_EXHAUSTIVE", "missing match arm "+v, s.Span)
				}
			}
			l.f.Blocks[from].End = term
			l.current = -1
			if len(ends) > 0 {
				join := l.newBlock()
				for _, end := range ends {
					l.jump(end, join, s.Span)
				}
				l.current = join
			}
		default:
			panic("unknown statement kind")
		}
	}
	if l.current >= 0 {
		for _, id := range locals {
			if typeTable[l.f.Slots[id].Type].Owned {
				l.op("scope_exit", "", -1, []int{id}, l.f.Slots[id].Span)
			}
		}
	}
	return l.current
}

// lower resolves symbols, checks value/contract types and builds an unchecked CFG.
// Ownership acceptance is a separate gate; this result must never reach emission.
func lower(m *Module) (u *unchecked, err error) {
	defer diagnostic(&err)
	u = &unchecked{Signatures: signatures()}
	for _, f := range m.Functions {
		if _, ok := u.Signatures[f.Name]; ok {
			fail("E_DUPLICATE", "duplicate callable "+f.Name, f.Span)
		}
		requireType(f.Result, m.Imports, f.Span)
		sig := signature{Result: f.Result, User: true}
		for _, p := range f.Params {
			requireType(p.Type, m.Imports, p.Span)
			if p.Own != typeTable[p.Type].Owned {
				fail("E_PARAMETER", "own qualifier must match resource type", p.Span)
			}
			sig.Args = append(sig.Args, p.Type)
		}
		u.Signatures[f.Name] = sig
	}
	for _, f := range m.Functions {
		ir := &functionIR{Name: f.Name, Result: f.Result, Span: f.Span}
		l := lowerer{f: ir, sigs: u.Signatures, imports: m.Imports, used: map[string]bool{}}
		env := environment{}
		for _, p := range f.Params {
			id := l.newSlot(p.Name, p.Type, p.Span, false)
			ir.Slots[id].Parameter = true
			ir.Params = append(ir.Params, id)
			env[p.Name] = id
		}
		if l.body(f.Body, env, l.newBlock(), nil) >= 0 {
			fail("E_RETURN", "every function path must return", f.Span)
		}
		u.Functions = append(u.Functions, ir)
	}
	byName := map[string]*functionIR{}
	for _, f := range u.Functions {
		byName[f.Name] = f
	}
	visiting, done := map[string]bool{}, map[string]bool{}
	var visit func(string)
	visit = func(name string) {
		if visiting[name] {
			fail("E_RECURSION", "recursive call cycle", byName[name].Span)
		}
		if done[name] {
			return
		}
		visiting[name] = true
		for _, n := range byName[name].Calls {
			visit(n)
		}
		visiting[name] = false
		done[name] = true
	}
	for _, f := range u.Functions {
		visit(f.Name)
	}
	return u, nil
}
