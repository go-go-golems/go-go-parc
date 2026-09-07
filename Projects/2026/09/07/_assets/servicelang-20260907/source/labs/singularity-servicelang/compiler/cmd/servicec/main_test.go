package main

import (
	"bytes"
	"os"
	"path/filepath"
	"strings"
	"testing"
)

func TestCLIStartupPlan(t *testing.T) {
	source := "../../../examples/sensor.svc"
	raw, err := os.ReadFile("../../../examples/sensor.plan.json")
	if err != nil {
		t.Fatal(err)
	}
	dir := t.TempDir()
	plan := filepath.Join(dir, "plan.json")
	dest := filepath.Join(dir, "app")
	if err = os.WriteFile(plan, raw, 0644); err != nil {
		t.Fatal(err)
	}
	var out, errs bytes.Buffer
	if code := run([]string{"emit-app", source, plan, "--out", dest}, &out, &errs); code != 0 {
		t.Fatalf("emit-app %d: %s", code, &errs)
	}
	if _, err = os.Stat(filepath.Join(dest, "artifacts", "application.hpp")); err != nil {
		t.Fatal(err)
	}
	raw = []byte(strings.ReplaceAll(string(raw), `"endpoint": "radio-b"`, `"endpoint": "undeclared"`))
	if err = os.WriteFile(plan, raw, 0644); err != nil {
		t.Fatal(err)
	}
	rejected := filepath.Join(dir, "rejected")
	out.Reset()
	errs.Reset()
	if code := run([]string{"emit-app", source, plan, "--out", rejected}, &out, &errs); code != 1 || !strings.Contains(errs.String(), "E_PLAN_ENDPOINT") {
		t.Fatalf("plan rejection %d: %s", code, &errs)
	}
	if _, err = os.Stat(rejected); !os.IsNotExist(err) {
		t.Fatal("invalid plan published an application", err)
	}
}

func TestCLI(t *testing.T) {
	dir := t.TempDir()
	file := filepath.Join(dir, "source.svc")
	put := func(src string) {
		t.Helper()
		if err := os.WriteFile(file, []byte(src), 0644); err != nil {
			t.Fatal(err)
		}
	}
	var out, errs bytes.Buffer
	put(`fn f() -> I32 { return 1; }`)
	if code := run([]string{"check", file}, &out, &errs); code != 0 || out.String() != "OK\n" {
		t.Fatalf("check %d: %s", code, &errs)
	}
	out.Reset()
	errs.Reset()
	dest := filepath.Join(dir, "accepted")
	if code := run([]string{"emit-cpp", file, "--out", dest}, &out, &errs); code != 0 {
		t.Fatalf("emit %d: %s", code, &errs)
	}
	if code := run([]string{"emit-cpp", file, "--out", dest}, &out, &errs); code != 2 {
		t.Fatalf("overwrite returned %d", code)
	}
	put("use sensor;\nfn f(own r: Ready) -> Unit { close(move r); close(move r); return; }")
	out.Reset()
	errs.Reset()
	rejected := filepath.Join(dir, "rejected")
	if code := run([]string{"emit-cpp", file, "--out", rejected}, &out, &errs); code != 1 {
		t.Fatalf("rejection returned %d", code)
	}
	if out.Len() != 0 || !strings.Contains(errs.String(), ":2:") || !strings.Contains(errs.String(), "E_USE") || !strings.Contains(errs.String(), "related ownership location") {
		t.Fatalf("diagnostics: %s / %s", &out, &errs)
	}
	if _, err := os.Stat(rejected); !os.IsNotExist(err) {
		t.Fatal("rejected source published output", err)
	}
	if code := run(nil, &out, &errs); code != 2 {
		t.Fatal("usage exit", code)
	}
}
