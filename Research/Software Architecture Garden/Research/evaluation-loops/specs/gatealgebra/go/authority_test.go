// Black-box test: this file compiles OUTSIDE the gatealgebra package, so it
// can construct only what any consumer can construct.
package gatealgebra_test

import (
	"reflect"
	"testing"

	gatealgebra "github.com/go-go-golems/garden-research/evaluation-loops/gatealgebra"
)

// TestApplicationIsUnforgeableOutsidePackage: the only Application value a
// consumer can construct is the zero value, and it is unauthorized. The
// forbidden literal Application{approvedBy: ...} is a compile error here; it
// is preserved as a build-tagged witness in forge_attempt.go.
func TestApplicationIsUnforgeableOutsidePackage(t *testing.T) {
	var app gatealgebra.Application
	if app.Authorized() {
		t.Fatal("zero-value Application must be unauthorized")
	}
	// gatealgebra.Application{} is legal (no unexported field referenced) but
	// still unauthorized:
	if (gatealgebra.Application{}).Authorized() {
		t.Fatal("literal zero Application must be unauthorized")
	}
}

// TestNoExportedConstructorReturnsApplication walks the package's exported
// method set reachable from its exported types and asserts none of them
// produces an Application. This is a structural guard in the go-go-datadrop
// genre: it fails the moment someone adds an apply path to the library.
func TestNoExportedConstructorReturnsApplication(t *testing.T) {
	appType := reflect.TypeOf(gatealgebra.Application{})
	types := []reflect.Type{
		reflect.TypeOf(gatealgebra.Decision{}),
		reflect.TypeOf(gatealgebra.Policy{}),
		reflect.TypeOf(gatealgebra.Report{}),
		appType,
	}
	for _, typ := range types {
		for i := 0; i < typ.NumMethod(); i++ {
			method := typ.Method(i)
			for out := 0; out < method.Type.NumOut(); out++ {
				if method.Type.Out(out) == appType {
					t.Fatalf("%s.%s returns Application: the library must not mint application authority", typ.Name(), method.Name)
				}
			}
		}
	}
}
