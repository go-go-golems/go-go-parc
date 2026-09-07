package compiler

import (
	"os"
	"os/exec"
	"path/filepath"
	"reflect"
	"strings"
	"testing"
)

func TestEmissionGate(t *testing.T) {
	src := `fn f() -> I32 { return 1; }`
	p, err := Check(src)
	if err != nil {
		t.Fatal(err)
	}
	a, err := EmitCPP(p, "quoted\"file.svc", src)
	if err != nil {
		t.Fatal(err)
	}
	b, err := EmitCPP(p, "quoted\"file.svc", src)
	if err != nil || !reflect.DeepEqual(a, b) {
		t.Fatal("nondeterministic emission", err)
	}
	if _, err = EmitCPP(p, "x", src+" "); err == nil {
		t.Fatal("mismatched source accepted")
	}
	if _, err = EmitCPP(&CheckedProgram{}, "x", src); err == nil {
		t.Fatal("unchecked zero value accepted")
	}
	if len(a.Mappings) == 0 || len(a.CompilerSHA256) != 64 {
		t.Fatal("missing provenance")
	}
	dir := filepath.Join(t.TempDir(), "out")
	if err = a.Publish(dir); err != nil {
		t.Fatal(err)
	}
	if err = a.Publish(dir); err == nil {
		t.Fatal("existing destination accepted")
	}
	if _, err = os.Stat(filepath.Join(dir, "artifacts", "generated.hpp")); err != nil {
		t.Fatal(err)
	}
}
func TestGeneratedOwnershipCPP(t *testing.T) {
	gpp, err := exec.LookPath("g++")
	if err != nil {
		t.Skip("native test requires g++")
	}
	data, err := os.ReadFile("../../../examples/ownership.svc")
	if err != nil {
		t.Fatal(err)
	}
	program := strings.ReplaceAll(string(data), "allocate(8)", "allocate(0008)") + `
fn decimal() -> I32 { return 0010; }
fn negative() -> I32 { return -0010; }
`
	p, err := Check(program)
	if err != nil {
		t.Fatal(err)
	}
	out, err := EmitCPP(p, "ownership.svc", program)
	if err != nil {
		t.Fatal(err)
	}
	temp := t.TempDir()
	if err = out.Publish(filepath.Join(temp, "gen")); err != nil {
		t.Fatal(err)
	}
	source := `#include "generated.hpp"
int main() {
 sl::Pool pool;
 svc_rt::Context ctx(pool);
 sl::require(svc_generated::BUFFER(ctx) == 8);
 sl::require(svc_generated::SUM(ctx, 2, 3) == 5);
 sl::require(svc_generated::SUM(ctx, INT32_MAX, 1) == -1);
 sl::require(svc_generated::SUM(ctx, INT32_MIN, -1) == -1);
 sl::require(svc_generated::fndecimal(ctx) == 10);
 sl::require(svc_generated::fnnegative(ctx) == -10);
 const auto stats = pool.stats();
 sl::require(stats.allocations == 1 && stats.releases == 1 && stats.live_general == 0);
}
`
	source = strings.ReplaceAll(source, "BUFFER", out.Functions["buffer_size"])
	source = strings.ReplaceAll(source, "SUM", out.Functions["checked_sum"])
	file := filepath.Join(temp, "main.cpp")
	if err = os.WriteFile(file, []byte(source), 0644); err != nil {
		t.Fatal(err)
	}
	binary := filepath.Join(temp, "run")
	cmd := exec.Command(gpp, "-std=c++17", "-Wall", "-Wextra", "-Wpedantic", "-Werror", "-fno-exceptions", "-fno-rtti", "-pthread", "-I", filepath.Join(temp, "gen", "artifacts"), "-I", "../../../runtime", "-I", "../../../../singularity-local/core/include", "-I", "../../../../singularity-rpc/core/include", file, "-o", binary)
	if output, err := cmd.CombinedOutput(); err != nil {
		t.Fatalf("native build: %v\n%s", err, output)
	}
	if output, err := exec.Command(binary).CombinedOutput(); err != nil {
		t.Fatalf("native run: %v\n%s", err, output)
	}
}
