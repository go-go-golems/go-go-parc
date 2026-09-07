package main

import (
	"errors"
	"fmt"
	"io"
	"os"
	"strings"

	"servicelang/internal/compiler"
)

func readBounded(path string) ([]byte, error) {
	file, err := os.Open(path)
	if err != nil {
		return nil, err
	}
	data, err := io.ReadAll(io.LimitReader(file, 65537))
	closeErr := file.Close()
	if err == nil {
		err = closeErr
	}
	return data, err
}

func run(args []string, out, errOut io.Writer) int {
	if len(args) < 2 || (args[0] != "check" && args[0] != "dump-ir" && args[0] != "emit-cpp" && args[0] != "emit-app") {
		fmt.Fprintln(errOut, "usage: servicec {check|dump-ir} SOURCE | servicec emit-cpp SOURCE --out NEW_DIRECTORY | servicec emit-app SOURCE PLAN --out NEW_DIRECTORY")
		return 2
	}
	if args[0] == "emit-cpp" {
		if len(args) != 4 || args[2] != "--out" {
			fmt.Fprintln(errOut, "emit-cpp requires SOURCE --out NEW_DIRECTORY")
			return 2
		}
	} else if args[0] == "emit-app" {
		if len(args) != 5 || args[3] != "--out" {
			fmt.Fprintln(errOut, "emit-app requires SOURCE PLAN --out NEW_DIRECTORY")
			return 2
		}
	} else if len(args) != 2 {
		fmt.Fprintln(errOut, "unexpected arguments")
		return 2
	}
	data, err := readBounded(args[1])
	if err != nil {
		fmt.Fprintln(errOut, err)
		return 2
	}
	src := string(data)
	p, err := compiler.Check(src)
	if err != nil {
		var d *compiler.Diagnostic
		if errors.As(err, &d) {
			position := func(offset int) string {
				prefix := src[:offset]
				line := strings.Count(prefix, "\n") + 1
				column := len(prefix) - strings.LastIndex(prefix, "\n")
				return fmt.Sprintf("%s:%d:%d", args[1], line, column)
			}
			fmt.Fprintf(errOut, "%s: %s: %s\n", position(d.Span.Start), d.Code, d.Message)
			if d.Related != nil {
				fmt.Fprintf(errOut, "%s: related ownership location\n", position(d.Related.Start))
			}
			return 1
		}
		fmt.Fprintln(errOut, err)
		return 2
	}
	switch args[0] {
	case "check":
		fmt.Fprintln(out, "OK")
	case "dump-ir":
		var data []byte
		data, err = p.DumpIR()
		if err == nil {
			_, err = fmt.Fprintln(out, string(data))
		}
	case "emit-app":
		var data []byte
		data, err = readBounded(args[2])
		if err != nil {
			break
		}
		var plan *compiler.CheckedPlan
		plan, err = compiler.CheckPlan(p, data)
		if err != nil {
			var d *compiler.Diagnostic
			if errors.As(err, &d) {
				fmt.Fprintf(errOut, "%s: %s: %s\n", args[2], d.Code, d.Message)
				return 1
			}
			break
		}
		var result *compiler.Output
		result, err = compiler.EmitApplication(plan, args[1], src)
		if err == nil {
			err = result.Publish(args[4])
		}
	case "emit-cpp":
		var result *compiler.Output
		result, err = compiler.EmitCPP(p, args[1], src)
		if err == nil {
			err = result.Publish(args[3])
		}
	}
	if err != nil {
		fmt.Fprintln(errOut, err)
		return 2
	}
	return 0
}
func main() { os.Exit(run(os.Args[1:], os.Stdout, os.Stderr)) }
