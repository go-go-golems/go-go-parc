//go:build forge_attempt_does_not_compile

// This file is a compile-error witness for the authority ladder. Remove the
// build tag and place this function in ANY OTHER package, and the build
// fails; verified 2026-08-14 against go1.26.5 with exactly:
//
//	cannot refer to unexported field approvedBy in struct literal of type
//	gatealgebra.Application
//
// (Inside this package it would compile, which is exactly the point: the
// package boundary is the authority boundary. The tag keeps the witness out
// of every build; the external-package variant is reproduced verbatim in the
// research document.)
package gatealgebra

func forgeApplication(d Decision) Application {
	// External code attempting the same literal cannot name approvedBy:
	return Application{approvedBy: "forged", decision: d}
}
