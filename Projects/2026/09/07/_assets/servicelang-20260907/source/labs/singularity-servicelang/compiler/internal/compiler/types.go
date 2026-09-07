package compiler

type typeInfo struct {
	Owned           bool
	CPP, Capability string
	Fields          map[string]string
	Variants        []string
}
type signature struct {
	Args               []string
	Read               map[int]bool
	Result, Capability string
	Constructor, User  bool
}

var typeTable = map[string]typeInfo{
	"Unit": {CPP: "svc_rt::Unit"}, "Bool": {CPP: "bool"}, "I32": {CPP: "std::int32_t"}, "Time": {CPP: "svc_rt::Time"},
	"Sample": {CPP: "svc_rt::Sample", Capability: "sensor", Fields: map[string]string{"value": "I32"}},
	"Buffer": {Owned: true, CPP: "svc_rt::Buffer", Capability: "memory"},
	"Ready":  {Owned: true, CPP: "svc_rt::Ready", Capability: "sensor"}, "Pending": {Owned: true, CPP: "svc_rt::Pending", Capability: "sensor"},
	"Allocation":   {Owned: true, CPP: "svc_rt::Allocation", Capability: "memory", Variants: []string{"Allocated", "AllocFailed"}},
	"StartResult":  {Owned: true, CPP: "svc_rt::StartResult", Capability: "sensor", Variants: []string{"Started", "Rejected", "Unavailable"}},
	"Continuation": {Owned: true, CPP: "svc_rt::Continuation", Capability: "sensor", Variants: []string{"Reusable", "Lost"}},
	"PollResult":   {Owned: true, CPP: "svc_rt::PollResult", Capability: "sensor", Variants: []string{"Waiting", "Complete"}},
	"Step":         {Owned: true, CPP: "svc_rt::Step", Capability: "sensor", Variants: []string{"Again", "Finished"}},
	"CallResult":   {CPP: "svc_rt::CallResult", Capability: "sensor", Variants: []string{"Ok", "RemoteError", "NotSent", "Unknown", "RuntimeFault"}},
	"Arithmetic":   {CPP: "svc_rt::Arithmetic", Variants: []string{"Number", "Overflow"}},
}

func signatures() map[string]signature {
	m := map[string]signature{
		"rpc_start": {Args: []string{"Ready", "Time", "I32"}, Result: "StartResult", Capability: "sensor"},
		"rpc_poll":  {Args: []string{"Pending", "Time"}, Result: "PollResult", Capability: "sensor"},
		"close":     {Args: []string{"Ready"}, Result: "Unit", Capability: "sensor"},
		"allocate":  {Args: []string{"I32"}, Result: "Allocation", Capability: "memory"},
		"release":   {Args: []string{"Buffer"}, Result: "Unit", Capability: "memory"},
		"length":    {Args: []string{"Buffer"}, Read: map[int]bool{0: true}, Result: "I32", Capability: "memory"},
		"observe":   {Args: []string{"I32", "I32"}, Result: "Unit", Capability: "output"},
		"add":       {Args: []string{"I32", "I32"}, Result: "Arithmetic"},
	}
	add := func(result, name string, args ...string) {
		m[name] = signature{Args: args, Result: result, Capability: typeTable[result].Capability, Constructor: true}
	}
	add("Allocation", "Allocated", "Buffer")
	add("Allocation", "AllocFailed", "I32")
	add("StartResult", "Started", "Pending")
	add("StartResult", "Rejected", "Ready", "I32")
	add("StartResult", "Unavailable", "I32")
	add("Continuation", "Reusable", "Ready")
	add("Continuation", "Lost", "I32")
	add("PollResult", "Waiting", "Pending")
	add("PollResult", "Complete", "CallResult", "Continuation")
	add("Step", "Again", "Pending")
	add("Step", "Finished", "Continuation")
	add("CallResult", "Ok", "Sample")
	add("CallResult", "RemoteError", "I32")
	add("CallResult", "NotSent")
	add("CallResult", "Unknown")
	add("CallResult", "RuntimeFault", "I32")
	add("Arithmetic", "Number", "I32")
	add("Arithmetic", "Overflow")
	return m
}

type slot struct {
	Name, Type           string
	Span                 Span
	Parameter, Temporary bool
}
type operation struct {
	Kind, Name string
	Dest       int
	Args       []int
	Span       Span
}
type edge struct {
	Target   int
	Variant  string
	Bindings []int
}
type terminator struct {
	Kind  string
	Value int
	Edges []edge
	Span  Span
}
type block struct {
	Ops []operation
	End terminator
}
type functionIR struct {
	Name, Result string
	Slots        []slot
	Blocks       []block
	Params       []int
	Calls        []string
	Span         Span
}
type unchecked struct {
	Functions  []*functionIR
	Signatures map[string]signature
}
