package dispatchlab

import "testing"

func TestModelTraceSchemaSequenceAndPartition(t *testing.T) {
	identity := TraceIdentity{RunID: "run-test", DispatcherID: "dispatcher-test"}
	d, err := NewCheckedWithIdentity[int](2, func(int) {}, identity)
	if err != nil {
		t.Fatal(err)
	}
	if !d.TrySubmit(7) {
		t.Fatal("sample submit was not admitted")
	}
	d.Close()
	d.Wait()

	trace := d.ModelTrace()
	if len(trace) == 0 {
		t.Fatal("checked dispatcher produced no model events")
	}
	for i, event := range trace {
		if event.RunID != identity.RunID || event.DispatcherID != identity.DispatcherID {
			t.Fatalf("event %d partition = %q/%q, want %q/%q", i, event.RunID, event.DispatcherID, identity.RunID, identity.DispatcherID)
		}
		if event.SchemaVersion != ModelEventSchemaVersion {
			t.Fatalf("event %d schema = %d, want %d", i, event.SchemaVersion, ModelEventSchemaVersion)
		}
		if want := uint64(i + 1); event.Sequence != want {
			t.Fatalf("event %d sequence = %d, want %d", i, event.Sequence, want)
		}
		if event.Action == "" {
			t.Fatalf("event %d has empty action", i)
		}
	}

	internal := d.trace()
	if len(trace) != len(internal) {
		t.Fatalf("model trace length = %d, internal trace length = %d", len(trace), len(internal))
	}

	intervals := d.OperationIntervals()
	if len(intervals) == 0 {
		t.Fatal("checked dispatcher produced no operation intervals")
	}
	type operationState struct {
		invoked, linearized, returned bool
	}
	states := map[string]operationState{}
	linearizedActions := map[string]map[string]bool{}
	for i, event := range intervals {
		if want := uint64(i + 1); event.Sequence != want {
			t.Fatalf("interval event %d sequence = %d, want %d", i, event.Sequence, want)
		}
		if event.RunID != identity.RunID || event.DispatcherID != identity.DispatcherID {
			t.Fatalf("interval event %d has wrong partition", i)
		}
		state := states[event.OperationID]
		switch event.Phase {
		case "invoke":
			if state.invoked || state.linearized || state.returned {
				t.Fatalf("operation %s has out-of-order invocation", event.OperationID)
			}
			state.invoked = true
		case "linearize":
			if !state.invoked || state.returned {
				t.Fatalf("operation %s linearized outside its interval", event.OperationID)
			}
			state.linearized = true
			if linearizedActions[event.OperationID] == nil {
				linearizedActions[event.OperationID] = map[string]bool{}
			}
			linearizedActions[event.OperationID][event.Action] = true
		case "return":
			if !state.invoked || !state.linearized || state.returned {
				t.Fatalf("operation %s returned without a complete interval", event.OperationID)
			}
			state.returned = true
		default:
			t.Fatalf("operation %s has unknown phase %q", event.OperationID, event.Phase)
		}
		states[event.OperationID] = state
	}
	for operationID, state := range states {
		if !state.invoked || !state.linearized || !state.returned {
			t.Fatalf("operation %s incomplete: %+v", operationID, state)
		}
	}
	for i, event := range trace {
		if event.OperationID == "" || event.Operation == "" {
			t.Fatalf("model event %d lacks operation identity", i)
		}
		if !linearizedActions[event.OperationID][event.Action] {
			t.Fatalf("model event %d has no matching interval linearization", i)
		}
	}
}

func TestCheckedIdentityRejectsEmptyPartitionKeys(t *testing.T) {
	if _, err := NewCheckedWithIdentity[int](1, func(int) {}, TraceIdentity{DispatcherID: "d"}); err == nil {
		t.Fatal("empty run ID was accepted")
	}
	if _, err := NewCheckedWithIdentity[int](1, func(int) {}, TraceIdentity{RunID: "r"}); err == nil {
		t.Fatal("empty dispatcher ID was accepted")
	}
}

func TestModelTraceDisabledForUninstrumentedDispatcher(t *testing.T) {
	d, err := New[int](1, func(int) {})
	if err != nil {
		t.Fatal(err)
	}
	d.Close()
	d.Wait()
	if trace := d.ModelTrace(); trace != nil {
		t.Fatalf("uninstrumented dispatcher trace = %v, want nil", trace)
	}
}
