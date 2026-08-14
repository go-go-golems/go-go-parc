package gatealgebra

// The authority ladder: witness → gate → human.
//
// A judge (or any metric producer) is a WITNESS: it contributes numbers to a
// Report and holds no decision authority. Evaluate is the GATE: it holds
// decision authority and nothing else — a Decision is a verdict plus its
// transcript. Application authority belongs to a HUMAN and, in ragopt, does
// not exist in the library at all: the promotion plan carries the fixed state
// review_required with human_apply_required = true and there is no apply
// command.
//
// This file encodes the same boundary in the type system. Application is the
// only type in this package representing applied-change authority, and the
// package exports no constructor, factory, or method that produces an
// authorized Application. Its authorization evidence is the unexported
// approvedBy field. Outside this package the only constructible value is the
// zero value (Go permits `gatealgebra.Application{}` because no unexported
// field is referenced), and the zero value answers Authorized() == false.
// Therefore:
//
//	for every Application value a constructible outside this package,
//	a.Authorized() == false
//
// A Decision cannot be turned into an authorized Application by any code path
// the library offers. That is the load-bearing property; it is checked
// black-box in authority_test.go and the doomed attempt to forge one is kept
// as a compile-error witness in forge_attempt.go (build-tagged out).

// Application represents an applied product change bound to the decision that
// justified it. See the package comment above for why no exported constructor
// exists and must not be added: adding one would collapse the gate → human
// step of the authority ladder into library code.
type Application struct {
	approvedBy string
	decision   Decision
}

// Authorized reports whether this value carries authorization evidence.
// Outside this package it is constantly false.
func (a Application) Authorized() bool {
	return a.approvedBy != ""
}

// Decision returns the decision this application claims to be based on.
// Meaningful only when Authorized() is true.
func (a Application) Decision() Decision {
	return a.decision
}
