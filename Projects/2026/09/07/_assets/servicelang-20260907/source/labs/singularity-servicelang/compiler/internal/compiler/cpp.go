package compiler

import (
	"crypto/sha256"
	"embed"
	"encoding/hex"
	"encoding/json"
	"fmt"
	"os"
	"path/filepath"
	"strconv"
	"strings"
)

//go:embed *.go
var implementation embed.FS

type SourceMapping struct {
	Function            string
	Block, Operation    int
	Source              Span
	FirstLine, LastLine int
}
type Output struct {
	Header                       string
	Wiring                       string `json:",omitempty"`
	PlanSHA256                   string `json:",omitempty"`
	Mappings                     []SourceMapping
	Functions                    map[string]string
	SourceSHA256, CompilerSHA256 string
	RuntimeABI                   int
	SourceFile                   string
}
type emitter struct {
	lines    []string
	mappings []SourceMapping
	sigs     map[string]signature
}

func (e *emitter) line(format string, args ...any) {
	e.lines = append(e.lines, fmt.Sprintf(format, args...))
}
func cppFunction(name string) string { return "fn" + strings.ReplaceAll(name, "_", "_u") }
func cppType(name string) string     { return typeTable[name].CPP }
func v(id int) string                { return fmt.Sprintf("v%d", id) }
func (e *emitter) define(f *functionIR, id int, expr string) {
	if typeTable[f.Slots[id].Type].Owned {
		e.line("sl::require(!%s.has_value());", v(id))
	}
	e.line("%s.emplace(%s);", v(id), expr)
}
func (e *emitter) operation(f *functionIR, op operation) {
	switch op.Kind {
	case "unit":
		e.define(f, op.Dest, "svc_rt::Unit{}")
	case "constant":
		e.define(f, op.Dest, cppType(f.Slots[op.Dest].Type)+"("+op.Name+")")
	case "copy":
		e.define(f, op.Dest, "*"+v(op.Args[0]))
	case "move":
		e.define(f, op.Dest, "svc_rt::take("+v(op.Args[0])+")")
	case "assign":
		expr := "*" + v(op.Args[0])
		if typeTable[f.Slots[op.Dest].Type].Owned {
			expr = "svc_rt::take(" + v(op.Args[0]) + ")"
		}
		e.define(f, op.Dest, expr)
	case "field":
		e.define(f, op.Dest, v(op.Args[0])+"->"+op.Name)
	case "compare":
		e.define(f, op.Dest, "*"+v(op.Args[0])+" "+op.Name+" *"+v(op.Args[1]))
	case "read":
		e.line("sl::require(%s.has_value());", v(op.Args[0]))
	case "scope_exit":
		e.line("sl::require(!%s.has_value());", v(op.Args[0]))
	case "call":
		sig := e.sigs[op.Name]
		e.line("{")
		var args []string
		for i, id := range op.Args {
			name := fmt.Sprintf("a%d", i)
			if sig.Read[i] {
				e.line("auto& %s = *%s;", name, v(id))
				args = append(args, name)
			} else {
				expr := "*" + v(id)
				if typeTable[f.Slots[id].Type].Owned {
					expr = "svc_rt::take(" + v(id) + ")"
				}
				e.line("auto %s = %s;", name, expr)
				args = append(args, "std::move("+name+")")
			}
		}
		var expr string
		if sig.Constructor {
			expr = cppType(sig.Result) + "{svc_rt::" + op.Name + "{" + strings.Join(args, ", ") + "}}"
		} else {
			name := "svc_rt::" + op.Name
			if sig.User {
				name = cppFunction(op.Name)
			}
			expr = name + "(" + strings.Join(append([]string{"ctx"}, args...), ", ") + ")"
		}
		e.define(f, op.Dest, expr)
		e.line("}")
	default:
		panic("unknown emission operation")
	}
}
func signatureCPP(f *functionIR) string {
	args := []string{"svc_rt::Context& ctx"}
	for _, id := range f.Params {
		args = append(args, cppType(f.Slots[id].Type)+" p"+strconv.Itoa(id))
	}
	return "inline " + cppType(f.Result) + " " + cppFunction(f.Name) + "(" + strings.Join(args, ", ") + ") noexcept"
}
func (e *emitter) function(f *functionIR) {
	e.line("%s {", signatureCPP(f))
	e.line("(void)ctx;")
	for id, s := range f.Slots {
		e.line("std::optional<%s> %s;", cppType(s.Type), v(id))
	}
	for _, id := range f.Params {
		e.line("%s.emplace(std::move(p%d));", v(id), id)
	}
	e.line("goto b0;")
	for id, b := range f.Blocks {
		e.line("b%d: {", id)
		for i, op := range b.Ops {
			first := len(e.lines) + 1
			e.operation(f, op)
			e.mappings = append(e.mappings, SourceMapping{f.Name, id, i, op.Span, first, len(e.lines)})
		}
		first := len(e.lines) + 1
		switch b.End.Kind {
		case "return":
			if typeTable[f.Slots[b.End.Value].Type].Owned {
				e.line("return svc_rt::take(%s);", v(b.End.Value))
			} else {
				e.line("return *%s;", v(b.End.Value))
			}
		case "jump":
			e.line("goto b%d;", b.End.Edges[0].Target)
		case "branch":
			e.line("if (*%s) goto b%d; else goto b%d;", v(b.End.Value), b.End.Edges[0].Target, b.End.Edges[1].Target)
		case "match":
			for _, edge := range b.End.Edges {
				e.line("if (std::holds_alternative<svc_rt::%s>(*%s)) {", edge.Variant, v(b.End.Value))
				value := "*" + v(b.End.Value)
				if typeTable[f.Slots[b.End.Value].Type].Owned {
					value = "svc_rt::take(" + v(b.End.Value) + ")"
				}
				e.line("auto variant = %s;", value)
				e.line("auto payload = std::get<svc_rt::%s>(std::move(variant));", edge.Variant)
				e.line("(void)payload;")
				for i, slot := range edge.Bindings {
					e.define(f, slot, fmt.Sprintf("std::move(payload.a%d)", i))
				}
				e.line("goto b%d;", edge.Target)
				e.line("}")
			}
			e.line("svc_rt::unreachable();")
		default:
			panic("unknown emission terminator")
		}
		e.mappings = append(e.mappings, SourceMapping{f.Name, id, -1, b.End.Span, first, len(e.lines)})
		e.line("}")
	}
	e.line("}")
}

// EmitCPP accepts only a successfully checked program. It performs no native compilation.
func EmitCPP(p *CheckedProgram, sourceFile, source string) (*Output, error) {
	if p == nil || p.ir == nil {
		return nil, fmt.Errorf("emission requires a checked program")
	}
	// Source identity must match the checked input; callers cannot attach a different
	// program's hash or source map to an accepted CFG.
	if sha256.Sum256([]byte(source)) != p.sourceHash {
		return nil, fmt.Errorf("source differs from checked input")
	}
	e := emitter{sigs: p.ir.Signatures}
	e.line("#pragma once")
	e.line("// Source: %s", strconv.Quote(sourceFile))
	e.line("#include \"svc_runtime.hpp\"")
	e.line("static_assert(svc_rt::abi_version == 1, \"ServiceLang adapter ABI mismatch\");")
	e.line("namespace svc_generated {")
	names := map[string]string{}
	for _, f := range p.ir.Functions {
		e.line("%s;", signatureCPP(f))
		names[f.Name] = cppFunction(f.Name)
	}
	for _, f := range p.ir.Functions {
		e.function(f)
	}
	e.line("} // namespace svc_generated")
	h := sha256.New()
	files, err := implementation.ReadDir(".")
	if err != nil {
		return nil, err
	}
	for _, f := range files {
		data, err := implementation.ReadFile(f.Name())
		if err != nil {
			return nil, err
		}
		h.Write([]byte(f.Name() + "\x00"))
		h.Write(data)
	}
	return &Output{Header: strings.Join(e.lines, "\n") + "\n", Mappings: e.mappings, Functions: names, SourceSHA256: hex.EncodeToString(p.sourceHash[:]), CompilerSHA256: hex.EncodeToString(h.Sum(nil)), RuntimeABI: 1, SourceFile: sourceFile}, nil
}

// Publish reserves a fresh destination, then atomically publishes the complete
// artifacts subdirectory. Existing destinations are never replaced, even if empty.
// Consumers use dest/artifacts, which is absent until every file has been written.
func (o *Output) Publish(dest string) (err error) {
	if o == nil {
		return fmt.Errorf("nil output")
	}
	data, err := json.MarshalIndent(o, "", "  ")
	if err != nil {
		return err
	}
	stage, err := os.MkdirTemp(filepath.Dir(dest), ".servicec-")
	if err != nil {
		return err
	}
	defer os.RemoveAll(stage)
	files := []struct {
		name string
		data []byte
	}{{"generated.hpp", []byte(o.Header)}, {"metadata.json", data}}
	if o.Wiring != "" {
		files = append(files, struct {
			name string
			data []byte
		}{"application.hpp", []byte(o.Wiring)})
	}
	for _, f := range files {
		if err = os.WriteFile(filepath.Join(stage, f.name), f.data, 0644); err != nil {
			return err
		}
	}
	if err = os.Mkdir(dest, 0755); err != nil {
		return err
	}
	if err = os.Rename(stage, filepath.Join(dest, "artifacts")); err != nil {
		// Remove only our still-empty reservation, never recursive user content.
		os.Remove(dest)
		return err
	}
	return nil
}
