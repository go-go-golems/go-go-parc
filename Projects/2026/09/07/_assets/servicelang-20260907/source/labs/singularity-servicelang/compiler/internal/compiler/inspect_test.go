package compiler

import (
	"os"
	"testing"
)

func TestInspectionUsesChecker(t *testing.T) {
	for _, file := range []string{"branch.svc", "double-move.invalid.svc"} {
		source, err := os.ReadFile("../../../examples/" + file)
		if err != nil {
			t.Fatal(err)
		}
		checked, checkErr := Check(string(source))
		report, err := Inspect(file, string(source), nil)
		if err != nil {
			t.Fatal(err)
		}
		if report.Accepted != (checkErr == nil) {
			t.Fatal("inspection/check disagreement")
		}
		if report.Accepted {
			out, err := EmitCPP(checked, file, string(source))
			if err != nil || report.Output.Header != out.Header {
				t.Fatal("inspection/emitter disagreement", err)
			}
		} else {
			if report.Output != nil || len(report.Diagnostics) == 0 {
				t.Fatal("rejected inspection emitted native output")
			}
		}
		if len(report.Functions) == 0 || report.Functions[0].Blocks[0].In == nil {
			t.Fatal("missing real ownership facts")
		}
	}
}
