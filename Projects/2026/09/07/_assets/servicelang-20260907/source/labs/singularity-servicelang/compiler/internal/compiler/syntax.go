// Package compiler implements the bounded ServiceLang host compiler.
package compiler

import (
	"fmt"
	"strconv"
	"strings"
	"unicode/utf8"
)

type Span struct{ Start, End int }
type Diagnostic struct {
	Code, Message string
	Span          Span
	Related       *Span
}

func (d *Diagnostic) Error() string {
	return fmt.Sprintf("%s at byte %d: %s", d.Code, d.Span.Start, d.Message)
}
func fail(code, message string, span Span) {
	panic(&Diagnostic{Code: code, Message: message, Span: span})
}
func diagnostic(err *error) {
	if p := recover(); p != nil {
		if d, ok := p.(*Diagnostic); ok {
			*err = d
		} else {
			panic(p)
		}
	}
}

type token struct {
	text string
	span Span
}
type Expr struct {
	Kind, Text string
	Span       Span
	Args       []*Expr
}
type Param struct {
	Name, Type string
	Own        bool
	Span       Span
}
type Arm struct {
	Name  string
	Names []token
	Body  []Stmt
	Span  Span
}
type Stmt struct {
	Kind, Name string
	Span       Span
	Expr       *Expr
	Body, Else []Stmt
	Arms       []Arm
}
type Function struct {
	Name, Result string
	Params       []Param
	Body         []Stmt
	Span         Span
}
type Module struct {
	Imports   map[string]bool
	Functions []Function
}
type parser struct {
	tokens     []token
	pos, depth int
}

func identStart(c byte) bool { return c == '_' || c >= 'A' && c <= 'Z' || c >= 'a' && c <= 'z' }
func digit(c byte) bool      { return c >= '0' && c <= '9' }
func lex(src string) []token {
	if len(src) > 65536 {
		fail("E_LIMIT", "source exceeds 64 KiB", Span{})
	}
	if !utf8.ValidString(src) {
		fail("E_UTF8", "invalid UTF-8", Span{})
	}
	var out []token
	for i := 0; i < len(src); {
		start := i
		c := src[i]
		if strings.ContainsRune(" \t\r\n", rune(c)) {
			i++
			continue
		}
		if c == '/' && i+1 < len(src) && src[i+1] == '/' {
			for i < len(src) && src[i] != '\n' {
				i++
			}
			continue
		}
		if identStart(c) {
			i++
			for i < len(src) && (identStart(src[i]) || digit(src[i])) {
				i++
			}
		} else if digit(c) {
			i++
			for i < len(src) && digit(src[i]) {
				i++
			}
		} else {
			if i+1 < len(src) && strings.Contains(" -> => == != <= >= ", " "+src[i:i+2]+" ") {
				i += 2
			} else if strings.ContainsRune("(){};,:.=<>-", rune(c)) {
				i++
			} else {
				fail("E_UNSUPPORTED", "unsupported source character", Span{i, i + 1})
			}
		}
		out = append(out, token{src[start:i], Span{start, i}})
	}
	return append(out, token{"<eof>", Span{len(src), len(src)}})
}
func (p *parser) peek() token { return p.tokens[p.pos] }
func (p *parser) pop() token {
	t := p.peek()
	if t.text != "<eof>" {
		p.pos++
	}
	return t
}
func (p *parser) accept(s string) bool {
	if p.peek().text == s {
		p.pop()
		return true
	}
	return false
}
func (p *parser) want(s string) token {
	t := p.pop()
	if t.text != s {
		fail("E_SYNTAX", "expected "+s+", got "+t.text, t.span)
	}
	return t
}
func (p *parser) name() token {
	t := p.pop()
	if len(t.text) == 0 || !identStart(t.text[0]) || strings.Contains(" fn use own move let if else match return true false ", " "+t.text+" ") {
		fail("E_SYNTAX", "expected identifier", t.span)
	}
	return t
}
func (p *parser) enter() {
	p.depth++
	if p.depth > 64 {
		fail("E_LIMIT", "nesting exceeds 64", p.peek().span)
	}
}
func (p *parser) block() []Stmt {
	p.enter()
	defer func() { p.depth-- }()
	p.want("{")
	var stmts []Stmt
	for !p.accept("}") {
		if p.peek().text == "<eof>" {
			fail("E_SYNTAX", "unclosed block", p.peek().span)
		}
		stmts = append(stmts, p.statement())
	}
	return stmts
}
func (p *parser) statement() Stmt {
	t := p.peek()
	s := Stmt{Kind: t.text, Span: t.span}
	switch t.text {
	case "let":
		p.pop()
		s.Name = p.name().text
		p.want("=")
		s.Expr = p.expr()
		p.want(";")
	case "return":
		p.pop()
		if p.peek().text != ";" {
			s.Expr = p.expr()
		}
		p.want(";")
	case "if":
		p.pop()
		s.Expr = p.expr()
		s.Body = p.block()
		if p.accept("else") {
			s.Else = p.block()
		}
	case "match":
		p.pop()
		s.Expr = p.expr()
		p.want("{")
		for !p.accept("}") {
			a := p.name()
			arm := Arm{Name: a.text, Span: a.span}
			if p.accept("(") {
				if !p.accept(")") {
					for {
						arm.Names = append(arm.Names, p.name())
						if p.accept(")") {
							break
						}
						p.want(",")
					}
				}
			}
			p.want("=>")
			arm.Body = p.block()
			s.Arms = append(s.Arms, arm)
		}
	default:
		if p.pos+1 < len(p.tokens) && p.tokens[p.pos+1].text == "=" {
			s.Kind = "assign"
			s.Name = p.name().text
			p.want("=")
		} else {
			s.Kind = "expr"
		}
		s.Expr = p.expr()
		p.want(";")
	}
	return s
}
func (p *parser) expr() *Expr {
	p.enter()
	defer func() { p.depth-- }()
	left := p.atom()
	for strings.Contains(" == != < <= > >= ", " "+p.peek().text+" ") {
		op := p.pop()
		right := p.atom()
		left = &Expr{Kind: "compare", Text: op.text, Span: Span{left.Span.Start, right.Span.End}, Args: []*Expr{left, right}}
	}
	return left
}
func (p *parser) atom() *Expr {
	t := p.pop()
	e := &Expr{Span: t.span, Text: t.text}
	switch {
	case t.text == "(":
		e = p.expr()
		p.want(")")
	case t.text == "move":
		n := p.name()
		e.Kind = "move"
		e.Text = n.text
		e.Span.End = n.span.End
	case t.text == "true" || t.text == "false":
		e.Kind = "bool"
	case t.text == "-" || digit(t.text[0]):
		if t.text == "-" {
			n := p.pop()
			if !digit(n.text[0]) {
				fail("E_SYNTAX", "minus requires integer literal", n.span)
			}
			e.Text = "-" + n.text
			e.Span.End = n.span.End
		}
		value, err := strconv.ParseInt(e.Text, 10, 32)
		if err != nil {
			fail("E_INTEGER", "literal outside I32", e.Span)
		}
		// Preserve decimal semantics when lowering to C++ (08 is not C++ decimal).
		e.Text = strconv.FormatInt(value, 10)
		e.Kind = "integer"
	case identStart(t.text[0]):
		p.pos--
		n := p.name()
		e.Text = n.text
		e.Kind = "var"
		if p.accept("(") {
			e.Kind = "call"
			if !p.accept(")") {
				for {
					e.Args = append(e.Args, p.expr())
					if p.accept(")") {
						break
					}
					p.want(",")
				}
			}
			e.Span.End = p.tokens[p.pos-1].span.End
		}
	default:
		fail("E_SYNTAX", "expected expression", t.span)
	}
	for p.accept(".") {
		f := p.name()
		e = &Expr{Kind: "field", Text: f.text, Span: Span{e.Span.Start, f.span.End}, Args: []*Expr{e}}
	}
	return e
}

// Parse performs syntax checks only; it is not an ownership acceptance API.
func Parse(src string) (m *Module, err error) {
	defer diagnostic(&err)
	p := parser{tokens: lex(src)}
	m = &Module{Imports: map[string]bool{}}
	for p.peek().text != "<eof>" {
		if p.accept("use") {
			cap := p.name()
			if cap.text != "sensor" && cap.text != "memory" && cap.text != "output" {
				fail("E_CAPABILITY", "unknown capability", cap.span)
			}
			if m.Imports[cap.text] {
				fail("E_DUPLICATE", "duplicate import", cap.span)
			}
			m.Imports[cap.text] = true
			p.want(";")
			continue
		}
		start := p.peek()
		if start.text != "fn" {
			fail("E_UNSUPPORTED", "only use and fn declarations are supported", start.span)
		}
		p.pop()
		n := p.name()
		f := Function{Name: n.text, Span: Span{start.span.Start, n.span.End}}
		p.want("(")
		if !p.accept(")") {
			for {
				own := p.accept("own")
				a := p.name()
				p.want(":")
				typ := p.name()
				f.Params = append(f.Params, Param{a.text, typ.text, own, a.span})
				if p.accept(")") {
					break
				}
				p.want(",")
			}
		}
		p.want("->")
		f.Result = p.name().text
		f.Body = p.block()
		m.Functions = append(m.Functions, f)
		if len(m.Functions) > 256 {
			fail("E_LIMIT", "more than 256 functions", f.Span)
		}
	}
	if len(m.Functions) == 0 {
		fail("E_MODULE", "module requires a function", Span{})
	}
	return m, nil
}
