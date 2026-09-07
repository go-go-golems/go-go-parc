package compiler

import (
	"bytes"
	"crypto/sha256"
	"encoding/hex"
	"encoding/json"
	"fmt"
	"io"
	"sort"
	"strings"
)

type Instance struct {
	Name     string `json:"name"`
	Protocol string `json:"protocol"`
	Role     string `json:"role"`
}
type Component struct {
	Name         string   `json:"name"`
	Endpoint     string   `json:"endpoint"`
	Begin        string   `json:"begin"`
	Poll         string   `json:"poll"`
	Authorities  []string `json:"authorities"`
	GeneralSlots int      `json:"general_slots"`
}
type startupPlan struct {
	ABI        int         `json:"abi"`
	Instances  []Instance  `json:"instances"`
	Components []Component `json:"components"`
}
type CheckedPlan struct {
	program *CheckedProgram
	plan    startupPlan
	hash    [32]byte
}
type footprint struct {
	slots int
	caps  map[string]bool
}

func capAdd(a, b int) int {
	if a+b > 12 {
		return 13
	}
	return a + b
}
func planError(code, message string) { fail("E_PLAN_"+code, message, Span{}) }

// rejectJSONDuplicates gives authority manifests one unambiguous interpretation.
func rejectJSONDuplicates(data []byte) error {
	d := json.NewDecoder(bytes.NewReader(data))
	var value func(int) error
	value = func(depth int) error {
		if depth > 32 {
			return fmt.Errorf("JSON nesting exceeds 32")
		}
		tok, err := d.Token()
		if err != nil {
			return err
		}
		delim, ok := tok.(json.Delim)
		if !ok {
			return nil
		}
		switch delim {
		case '{':
			seen := map[string]bool{}
			for d.More() {
				key, err := d.Token()
				if err != nil {
					return err
				}
				name, ok := key.(string)
				if !ok {
					return fmt.Errorf("object key must be a string")
				}
				if seen[name] {
					return fmt.Errorf("duplicate key %q", name)
				}
				seen[name] = true
				if err = value(depth + 1); err != nil {
					return err
				}
			}
		case '[':
			for d.More() {
				if err = value(depth + 1); err != nil {
					return err
				}
			}
		default:
			return fmt.Errorf("unexpected JSON delimiter")
		}
		_, err = d.Token()
		return err
	}
	if err := value(0); err != nil {
		return err
	}
	if _, err := d.Token(); err != io.EOF {
		return fmt.Errorf("trailing JSON data")
	}
	return nil
}
func footprintOf(p *CheckedProgram) map[string]footprint {
	functions := map[string]*functionIR{}
	for _, f := range p.ir.Functions {
		functions[f.Name] = f
	}
	memo := map[string]footprint{}
	var visit func(string) footprint
	visit = func(name string) footprint {
		if result, ok := memo[name]; ok {
			return result
		}
		result := footprint{caps: map[string]bool{}}
		for _, b := range functions[name].Blocks {
			for _, op := range b.Ops {
				if op.Kind != "call" {
					continue
				}
				sig := p.ir.Signatures[op.Name]
				if sig.User {
					sub := visit(op.Name)
					result.slots = capAdd(result.slots, sub.slots)
					for c := range sub.caps {
						result.caps[c] = true
					}
				} else {
					if sig.Capability != "" {
						result.caps[sig.Capability] = true
					}
					if op.Name == "allocate" {
						result.slots = capAdd(result.slots, 1)
					}
				}
			}
		}
		memo[name] = result
		return result
	}
	for _, f := range p.ir.Functions {
		visit(f.Name)
	}
	return memo
}
func CheckPlan(p *CheckedProgram, data []byte) (checked *CheckedPlan, err error) {
	defer diagnostic(&err)
	if p == nil || p.ir == nil {
		return nil, fmt.Errorf("startup plan requires a checked program")
	}
	if len(data) > 65536 {
		planError("LIMIT", "plan exceeds 64 KiB")
	}
	if err = rejectJSONDuplicates(data); err != nil {
		planError("JSON", err.Error())
	}
	d := json.NewDecoder(bytes.NewReader(data))
	d.DisallowUnknownFields()
	var plan startupPlan
	if err = d.Decode(&plan); err != nil {
		planError("JSON", err.Error())
	}
	if plan.ABI != 1 {
		planError("ABI", "only ABI 1 is supported")
	}
	if len(plan.Components) < 1 || len(plan.Components) > 4 || len(plan.Instances) != len(plan.Components) {
		planError("COUNT", "require one to four components with one exclusive instance each")
	}
	instances := map[string]bool{}
	used := map[string]bool{}
	names := map[string]bool{}
	for _, in := range plan.Instances {
		if in.Name == "" || instances[in.Name] {
			planError("NAME", "empty or duplicate instance name")
		}
		instances[in.Name] = true
		if in.Protocol != "SensorRPC" || in.Role != "client" {
			planError("PROTOCOL", "only SensorRPC client instances are supported")
		}
	}
	footprints := footprintOf(p)
	total := 0
	signatureOK := func(name, result string, args ...string) bool {
		s, ok := p.ir.Signatures[name]
		if !ok || !s.User || s.Result != result || len(s.Args) != len(args) {
			return false
		}
		for i, a := range args {
			if s.Args[i] != a {
				return false
			}
		}
		return true
	}
	for _, c := range plan.Components {
		if c.Name == "" || names[c.Name] {
			planError("NAME", "empty or duplicate component name")
		}
		names[c.Name] = true
		if !instances[c.Endpoint] {
			planError("ENDPOINT", "undeclared endpoint "+c.Endpoint)
		}
		if used[c.Endpoint] {
			planError("ENDPOINT", "endpoint assigned to multiple components")
		}
		used[c.Endpoint] = true
		if !signatureOK(c.Begin, "StartResult", "Ready", "Time") || !signatureOK(c.Poll, "Step", "Pending", "Time") {
			planError("SIGNATURE", "begin/poll signatures must be Ready,Time -> StartResult and Pending,Time -> Step")
		}
		allowed := map[string]bool{}
		for _, a := range c.Authorities {
			if a != "sensor" && a != "memory" && a != "output" {
				planError("AUTHORITY", "unknown authority "+a)
			}
			if allowed[a] {
				planError("AUTHORITY", "duplicate authority "+a)
			}
			allowed[a] = true
		}
		required := map[string]bool{"sensor": true}
		for _, name := range []string{c.Begin, c.Poll} {
			for a := range footprints[name].caps {
				required[a] = true
			}
		}
		var ordered []string
		for a := range required {
			ordered = append(ordered, a)
		}
		sort.Strings(ordered)
		for _, a := range ordered {
			if !allowed[a] {
				planError("AUTHORITY", c.Name+" lacks "+a)
			}
		}
		demand := footprints[c.Begin].slots
		if footprints[c.Poll].slots > demand {
			demand = footprints[c.Poll].slots
		}
		if c.GeneralSlots < demand || c.GeneralSlots < 0 || c.GeneralSlots > 12 {
			planError("RESOURCE", c.Name+" has insufficient or invalid general_slots")
		}
		total = capAdd(total, c.GeneralSlots)
	}
	if total > 12 {
		planError("RESOURCE", "declared general slots exceed the fixed pool capacity of 12")
	}
	return &CheckedPlan{program: p, plan: plan, hash: sha256.Sum256(data)}, nil
}

func EmitApplication(p *CheckedPlan, sourceFile, source string) (*Output, error) {
	if p == nil || p.program == nil {
		return nil, fmt.Errorf("emission requires a checked startup plan")
	}
	out, err := EmitCPP(p.program, sourceFile, source)
	if err != nil {
		return nil, err
	}
	var b strings.Builder
	fmt.Fprintln(&b, "#pragma once\n#include \"generated.hpp\"\n#include \"svc_component.hpp\"\nnamespace svc_generated {")
	fmt.Fprintf(&b, "using Application = svc_rt::Application<%d>;\n", len(p.plan.Components))
	fmt.Fprintln(&b, "inline bool create_application(std::optional<Application>& output, sl::Pool& pool, const Application::Hosts& hosts) noexcept {")
	fmt.Fprintln(&b, "const std::array<svc_rt::ComponentFunctions, Application::count> functions{{")
	total := 0
	for _, c := range p.plan.Components {
		host := 0
		for i, in := range p.plan.Instances {
			if in.Name == c.Endpoint {
				host = i
				break
			}
		}
		fmt.Fprintf(&b, "{%s, %s, %d},\n", cppFunction(c.Begin), cppFunction(c.Poll), host)
		total += c.GeneralSlots
	}
	fmt.Fprintf(&b, "}};\nreturn Application::create(output, pool, hosts, functions, %d);\n}\n} // namespace svc_generated\n", total)
	out.Wiring = b.String()
	out.PlanSHA256 = hex.EncodeToString(p.hash[:])
	return out, nil
}
