package compiler

import (
	"encoding/json"
	"errors"
	"os"
	"strings"
	"testing"
)

func TestStartupPlan(t *testing.T) {
	source, err := os.ReadFile("../../../examples/sensor.svc")
	if err != nil {
		t.Fatal(err)
	}
	data, err := os.ReadFile("../../../examples/sensor.plan.json")
	if err != nil {
		t.Fatal(err)
	}
	p, err := Check(string(source))
	if err != nil {
		t.Fatal(err)
	}
	cp, err := CheckPlan(p, data)
	if err != nil {
		t.Fatal(err)
	}
	out, err := EmitApplication(cp, "sensor.svc", string(source))
	if err != nil || !strings.Contains(out.Wiring, "fnbegin, fntick, 1") || len(out.PlanSHA256) != 64 {
		t.Fatal("missing checked host mapping", err)
	}
	cases := []struct {
		name, code string
		edit       func(*startupPlan)
	}{
		{"undeclared endpoint", "E_PLAN_ENDPOINT", func(p *startupPlan) { p.Components[0].Endpoint = "missing" }},
		{"duplicate owner", "E_PLAN_ENDPOINT", func(p *startupPlan) { p.Components[0].Endpoint = p.Components[1].Endpoint }},
		{"missing authority", "E_PLAN_AUTHORITY", func(p *startupPlan) { p.Components[0].Authorities = []string{"sensor"} }},
		{"wrong entry signature", "E_PLAN_SIGNATURE", func(p *startupPlan) { p.Components[0].Begin = "tick" }},
		{"wrong role", "E_PLAN_PROTOCOL", func(p *startupPlan) { p.Instances[0].Role = "server" }},
		{"pool overflow", "E_PLAN_RESOURCE", func(p *startupPlan) { p.Components[0].GeneralSlots = 7; p.Components[1].GeneralSlots = 6 }},
	}
	for _, tc := range cases {
		t.Run(tc.name, func(t *testing.T) {
			var plan startupPlan
			if err := json.Unmarshal(data, &plan); err != nil {
				t.Fatal(err)
			}
			tc.edit(&plan)
			raw, _ := json.Marshal(plan)
			checked, err := CheckPlan(p, raw)
			var d *Diagnostic
			if checked != nil || !errors.As(err, &d) || d.Code != tc.code {
				t.Fatalf("want %s got %v", tc.code, err)
			}
		})
	}
	if _, err = CheckPlan(p, []byte(`{"abi":1,"abi":2}`)); err == nil {
		t.Fatal("duplicate key accepted")
	}
	if _, err = EmitApplication(&CheckedPlan{}, "x", string(source)); err == nil {
		t.Fatal("zero plan emitted")
	}

	// A callee allocation must count even if the entry function has no direct allocate.
	withMemory := "use memory;\n" + strings.Replace(string(source), "return rpc_start(move ready, now, 8000);", "memory_helper(); return rpc_start(move ready, now, 8000);", 1) + `fn memory_helper() -> Unit { match allocate(1) { Allocated(b) => { release(move b); return; } AllocFailed(e) => { return; } } }`
	mp, err := Check(withMemory)
	if err != nil {
		t.Fatal(err)
	}
	var plan startupPlan
	json.Unmarshal(data, &plan)
	for i := range plan.Components {
		plan.Components[i].Authorities = append(plan.Components[i].Authorities, "memory")
	}
	raw, _ := json.Marshal(plan)
	_, err = CheckPlan(mp, raw)
	var d *Diagnostic
	if !errors.As(err, &d) || d.Code != "E_PLAN_RESOURCE" {
		t.Fatal("transitive allocation not counted", err)
	}
	for i := range plan.Components {
		plan.Components[i].GeneralSlots = 1
	}
	raw, _ = json.Marshal(plan)
	if _, err = CheckPlan(mp, raw); err != nil {
		t.Fatal(err)
	}
}
