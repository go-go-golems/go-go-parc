export interface Span {
  Start: number;
  End: number;
}
export interface Diagnostic {
  Code: string;
  Message: string;
  Span: Span;
  Related: Span | null;
}
export interface Op {
  Kind: string;
  Name: string;
  Dest: number;
  Args: number[] | null;
  Span: Span;
}
export interface Edge {
  Target: number;
  Variant: string;
  Bindings: number[] | null;
}
export interface Fact {
  Slot: number;
  States: string[];
  Origin: Span | null;
}
export interface Block {
  ID: number;
  Ops: Op[] | null;
  End: { Kind: string; Value: number; Edges: Edge[] | null; Span: Span };
  In: Fact[] | null;
  Out: Fact[] | null;
}
export interface FunctionView {
  Name: string;
  Slots: {
    ID: number;
    Name: string;
    Type: string;
    Owned: boolean;
    Span: Span;
  }[];
  Blocks: Block[];
}
export interface Output {
  Header: string;
  Wiring?: string;
  SourceSHA256: string;
  CompilerSHA256: string;
  PlanSHA256?: string;
  RuntimeABI: number;
  Functions: Record<string, string>;
  Mappings: {
    Function: string;
    Block: number;
    Operation: number;
    Source: Span;
    FirstLine: number;
    LastLine: number;
  }[];
}
export interface Report {
  Accepted: boolean;
  SourceSHA256: string;
  Stages: { Name: string; Status: string; Detail: string }[];
  Diagnostics: Diagnostic[] | null;
  AST?: unknown;
  Functions: FunctionView[] | null;
  Output?: Output;
  PlanAccepted?: boolean;
  InspectionLimited: boolean;
}
export interface Input {
  Source: string;
  Filename: string;
  Plan: string;
}
export interface Preset extends Input {
  ID: string;
  Title: string;
  Description: string;
  Expected: boolean;
}
