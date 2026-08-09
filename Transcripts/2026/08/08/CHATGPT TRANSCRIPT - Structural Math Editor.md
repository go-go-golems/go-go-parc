# Structural Math Editor

- URL: https://chatgpt.com/c/6a74c9e1-1d68-83ea-8c8f-bbcf4751e854
- Created: 2026-08-06T17:52:33.831Z

---

> decompose this into proper abstract patternsfrom operational and denotational semantics and type theory and category thoeyr, and then rebuild it properly, making sure it's mathematically sound. Write a full thesis in a textbook style to explain it all. Take screenshots for the thesis.
>
> Output as markdown and pdf and a zip with everything.

I’ll formalize the editor as a typed syntax-and-editing system, rebuild it around explicit invariants, and produce a textbook-style thesis with figures, Markdown, PDF, source, and ZIP.

```unknown
bash -lc cat /home/oai/skills/pdfs/SKILL.md && printf '
---FILES---
' && ls -l /mnt/data && printf '
---SOURCE HEAD---
' && sed -n '1,120p' '/mnt/data/Pasted text(20260806-175142).txt'
```

<details><summary>💭 Thinking</summary>

**Planning the deliverables**

I’m organizing a formal thesis-style treatment around the source code, supported by academic references and line-based excerpts. I’ll cover semantics, architecture, operational behavior, code review, and appendices without exposing internal search details.

**Planned the deliverables**

</details>

```unknown
bash -lc node -v && npm -v && npx --yes tsc --version && python --version && which pandoc && which xelatex && which chromium || true && which google-chrome || true && which playwright || true
```

<details><summary>💭 Thinking</summary>

**Inspected PDF requirements and checked available development tools**

</details>

```json
{"search_query":[{"q":"Gordon Plotkin Structural Operational Semantics technical report PDF"},{"q":"Scott Strachey Toward a Mathematical Semantics for Computer Languages PDF Oxford"},{"q":"Gérard Huet Functional Pearl The Zipper PDF"},{"q":"Abbott Altenkirch Ghani Containers Constructing Strictly Positive Types PDF"}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Formalizing the model**

I’m defining the syntax as mutually recursive rows and nodes, then checking its algebraic structure, empty-row behavior, partial navigation, and metadata-driven field access. I’ll also compare the implementation with TypeScript’s type-system conventions and note soundness limits.

**Formalized the model**

**Identifying structural risks**

I’m noting that scripts behave as standalone postfix nodes, so the tree represents presentation sequences rather than strictly binding expressions. I’m also flagging unchecked delimiters, optional combinations, backend-specific symbols, partial paths, and duplicated field-order metadata.

**Identified structural risks**

**Checking Unicode rendering**

I’m examining character handling and finding that naive code-point arithmetic can split grapheme clusters and mishandle exceptional mathematical letters. The renderer also relies on brittle, handwritten Unicode mappings that may omit special cases.

**Searched 26 websites**

</details>

```json
{"search_query":[{"q":"Hazelnut A Bidirectionally Typed Structure Editor Calculus PDF"},{"q":"Hazelnut Live Programming with Holes POPL PDF"},{"q":"Omar Voysey Chugh Hammer Hazelnut structure editor calculus PDF"},{"q":"Typst reference math syntax official symbols"}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Searched 16 websites**

</details>

```unknown
bash -lc command -v esbuild || true; npm root -g; find /usr/lib/node_modules /usr/local/lib/node_modules -maxdepth 2 -type d -iname 'react' 2>/dev/null | head -20; find ~/.npm -maxdepth 4 -type d -iname 'react' 2>/dev/null | head -20
```

The rebuild will separate syntax, backend renderings, presentation metadata, and editor state, using typed one-hole contexts plus explicit well-formedness, focus, selection, and fold invariants.

<details><summary>💭 Thinking</summary>

**Checked React, esbuild, and Typst availability**

</details>

```json
{"search_query":[{"q":"site:typst.app/docs/reference/math operator name upright function Typst math op"},{"q":"site:typst.app/docs/reference/math root accent attach limits Typst"}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Searched 1 website**

</details>

```unknown
bash -lc set -euo pipefail
ROOT=/mnt/data/structural-editor-thesis
rm -rf "$ROOT"
mkdir -p "$ROOT"/{source/original,source/rebuilt/src/core,source/rebuilt/src/demo,source/rebuilt/public,source/rebuilt/tests,figures,screenshots,analysis,build}
cp '/mnt/data/Pasted text(20260806-175142).txt' "$ROOT/source/original/MathKeyboardV3.tsx"
cat > "$ROOT/source/rebuilt/package.json" <<'EOF'
{
  "name": "structural-math-editor-core",
  "version": "1.0.0",
  "private": true,
  "type": "module",
  "scripts": {
    "build": "tsc -p tsconfig.json",
    "typecheck": "tsc -p tsconfig.json --noEmit",
    "test": "npm run build && node dist/selftest.js"
  },
  "devDependencies": {
    "typescript": "^5.8.3"
  }
}
EOF
cat > "$ROOT/source/rebuilt/tsconfig.json" <<'EOF'
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "NodeNext",
    "moduleResolution": "NodeNext",
    "strict": true,
    "noUncheckedIndexedAccess": true,
    "exactOptionalPropertyTypes": true,
    "noFallthroughCasesInSwitch": true,
    "noImplicitOverride": true,
    "useUnknownInCatchVariables": true,
    "declaration": true,
    "sourceMap": true,
    "rootDir": "src",
    "outDir": "dist",
    "lib": ["ES2022", "DOM"]
  },
  "include": ["src/**/*.ts"]
}
EOF
cat > "$ROOT/source/rebuilt/src/core/result.ts" <<'EOF'
/** A small explicit error type. No editor primitive throws for ordinary bad input. */
export type Result<T, E> =
  | Readonly<{ ok: true; value: T }>
  | Readonly<{ ok: false; error: E }>;

export const ok = <T>(value: T): Result<T, never> => ({ ok: true, value });
export const err = <E>(error: E): Result<never, E> => ({ ok: false, error });

export function mapResult<A, B, E>(r: Result<A, E>, f: (value: A) => B): Result<B, E> {
  return r.ok ? ok(f(r.value)) : r;
}

export function flatMapResult<A, B, E1, E2>(
  r: Result<A, E1>,
  f: (value: A) => Result<B, E2>,
): Result<B, E1 | E2> {
  return r.ok ? f(r.value) : r;
}
EOF
cat > "$ROOT/source/rebuilt/src/core/model.ts" <<'EOF'
import { err, ok, type Result } from "./result.js";

/** Draft trees may contain holes. Complete trees may not. */
export type Phase = "draft" | "complete";

export type Brand<T, Name extends string> = T & { readonly __brand: Name };
export type NodeId = Brand<string, "NodeId">;
export type HoleId = Brand<string, "HoleId">;
export type SymbolId = Brand<string, "SymbolId">;

export type NonEmptyArray<T> = readonly [T, ...T[]];
export type DelimiterPair = "round" | "square" | "curly" | "angle" | "absolute" | "norm";
export type IdentifierStyle = "italic" | "upright" | "calligraphic" | "double-struck" | "fraktur";
export type AccentKind = "bar" | "hat" | "tilde" | "vector";
export type LargeOperatorKind =
  | "sum"
  | "product"
  | "integral"
  | "limit"
  | "coproduct"
  | "big-union"
  | "big-intersection"
  | "direct-sum";
export type ArrowKind = "right" | "hook" | "two-head" | "squiggle" | "double";

export interface BaseNode {
  readonly id: NodeId;
}

export interface IdentifierNode extends BaseNode {
  readonly tag: "identifier";
  readonly text: string;
  readonly style: IdentifierStyle;
}

export interface NumberNode extends BaseNode {
  readonly tag: "number";
  readonly digits: string;
}

export interface SymbolNode extends BaseNode {
  readonly tag: "symbol";
  readonly symbol: SymbolId;
}

export interface HoleNode extends BaseNode {
  readonly tag: "hole";
  readonly holeId: HoleId;
  readonly expectation: "expression" | "index" | "bound" | "argument" | "label";
}

export interface FractionNode<P extends Phase> extends BaseNode {
  readonly tag: "fraction";
  readonly numerator: NonEmptyRow<P>;
  readonly denominator: NonEmptyRow<P>;
}

export interface RadicalNode<P extends Phase> extends BaseNode {
  readonly tag: "radical";
  readonly index?: NonEmptyRow<P>;
  readonly radicand: NonEmptyRow<P>;
}

export interface ApplyNode<P extends Phase> extends BaseNode {
  readonly tag: "apply";
  readonly functionName: string;
  readonly argument: Row<P>;
}

export interface GroupNode<P extends Phase> extends BaseNode {
  readonly tag: "group";
  readonly delimiter: DelimiterPair;
  readonly body: Row<P>;
}

export interface ScriptedNode<P extends Phase> extends BaseNode {
  readonly tag: "scripted";
  /** The base is owned by this node. Scripts are never context-sensitive postfix tokens. */
  readonly base: NonEmptyRow<P>;
  readonly superscript?: NonEmptyRow<P>;
  readonly subscript?: NonEmptyRow<P>;
}

export interface AccentNode<P extends Phase> extends BaseNode {
  readonly tag: "accent";
  readonly accent: AccentKind;
  readonly body: NonEmptyRow<P>;
}

export interface LargeOperatorNode<P extends Phase> extends BaseNode {
  readonly tag: "large-operator";
  readonly operator: LargeOperatorKind;
  readonly lower?: NonEmptyRow<P>;
  readonly upper?: NonEmptyRow<P>;
}

export interface LabeledArrowNode<P extends Phase> extends BaseNode {
  readonly tag: "labeled-arrow";
  readonly arrow: ArrowKind;
  readonly label: NonEmptyRow<P>;
}

export type HoleFor<P extends Phase> = P extends "draft" ? HoleNode : never;

export type Expr<P extends Phase> =
  | IdentifierNode
  | NumberNode
  | SymbolNode
  | HoleFor<P>
  | FractionNode<P>
  | RadicalNode<P>
  | ApplyNode<P>
  | GroupNode<P>
  | ScriptedNode<P>
  | AccentNode<P>
  | LargeOperatorNode<P>
  | LabeledArrowNode<P>;

export type Row<P extends Phase> = readonly Expr<P>[];
export type NonEmptyRow<P extends Phase> = NonEmptyArray<Expr<P>>;
export type Document<P extends Phase> = NonEmptyArray<Row<P>>;

let sequence = 0;
const serial = (prefix: string): string => `${prefix}-${Date.now().toString(36)}-${(sequence++).toString(36)}`;
export const freshNodeId = (): NodeId => serial("n") as NodeId;
export const freshHoleId = (): HoleId => serial("h") as HoleId;
export const symbolId = (value: string): SymbolId => value as SymbolId;

export const identifier = (text: string, style: IdentifierStyle = "italic"): IdentifierNode => ({
  tag: "identifier",
  id: freshNodeId(),
  text,
  style,
});

export const number = (digits: string): NumberNode => ({ tag: "number", id: freshNodeId(), digits });
export const symbol = (name: string): SymbolNode => ({ tag: "symbol", id: freshNodeId(), symbol: symbolId(name) });
export const hole = (expectation: HoleNode["expectation"] = "expression"): HoleNode => ({
  tag: "hole",
  id: freshNodeId(),
  holeId: freshHoleId(),
  expectation,
});

export const holeRow = (expectation: HoleNode["expectation"] = "expression"): NonEmptyRow<"draft"> => [
  hole(expectation),
];

export function asNonEmpty<P extends Phase>(row: Row<P>): Result<NonEmptyRow<P>, "empty-row"> {
  return row.length === 0 ? err("empty-row") : ok(row as NonEmptyRow<P>);
}

export const fraction = (
  numerator: NonEmptyRow<"draft"> = holeRow(),
  denominator: NonEmptyRow<"draft"> = holeRow(),
): FractionNode<"draft"> => ({ tag: "fraction", id: freshNodeId(), numerator, denominator });

export const radical = (
  radicand: NonEmptyRow<"draft"> = holeRow(),
  index?: NonEmptyRow<"draft">,
): RadicalNode<"draft"> => ({
  tag: "radical",
  id: freshNodeId(),
  radicand,
  ...(index === undefined ? {} : { index }),
});

export const apply = (functionName: string, argument: Row<"draft"> = holeRow("argument")): ApplyNode<"draft"> => ({
  tag: "apply",
  id: freshNodeId(),
  functionName,
  argument,
});

export const group = (delimiter: DelimiterPair, body: Row<"draft"> = holeRow()): GroupNode<"draft"> => ({
  tag: "group",
  id: freshNodeId(),
  delimiter,
  body,
});

export function scripted(
  base: NonEmptyRow<"draft">,
  superscript?: NonEmptyRow<"draft">,
  subscript?: NonEmptyRow<"draft">,
): Result<ScriptedNode<"draft">, "script-requires-attachment"> {
  if (superscript === undefined && subscript === undefined) return err("script-requires-attachment");
  return ok({
    tag: "scripted",
    id: freshNodeId(),
    base,
    ...(superscript === undefined ? {} : { superscript }),
    ...(subscript === undefined ? {} : { subscript }),
  });
}

export const accent = (kind: AccentKind, body: NonEmptyRow<"draft">): AccentNode<"draft"> => ({
  tag: "accent",
  id: freshNodeId(),
  accent: kind,
  body,
});

export const largeOperator = (
  operator: LargeOperatorKind,
  lower?: NonEmptyRow<"draft">,
  upper?: NonEmptyRow<"draft">,
): LargeOperatorNode<"draft"> => ({
  tag: "large-operator",
  id: freshNodeId(),
  operator,
  ...(lower === undefined ? {} : { lower }),
  ...(upper === undefined ? {} : { upper }),
});

export const boundedLargeOperator = (operator: LargeOperatorKind): LargeOperatorNode<"draft"> =>
  largeOperator(operator, holeRow("bound"), holeRow("bound"));

export const labeledArrow = (
  arrow: ArrowKind,
  label: NonEmptyRow<"draft"> = holeRow("label"),
): LabeledArrowNode<"draft"> => ({ tag: "labeled-arrow", id: freshNodeId(), arrow, label });

/** Re-identify a template before insertion, preserving syntax while preventing key aliasing. */
export function refreshIds<P extends Phase>(row: Row<P>): Row<P> {
  const recurRow = (r: Row<P>): Row<P> => r.map(recurExpr);
  const recurNonEmpty = (r: NonEmptyRow<P>): NonEmptyRow<P> => recurRow(r) as NonEmptyRow<P>;
  const recurExpr = (node: Expr<P>): Expr<P> => {
    const id = freshNodeId();
    switch (node.tag) {
      case "identifier": return { ...node, id };
      case "number": return { ...node, id };
      case "symbol": return { ...node, id };
      case "hole": return { ...node, id, holeId: freshHoleId() } as Expr<P>;
      case "fraction": return { ...node, id, numerator: recurNonEmpty(node.numerator), denominator: recurNonEmpty(node.denominator) };
      case "radical": return {
        ...node,
        id,
        radicand: recurNonEmpty(node.radicand),
        ...(node.index === undefined ? {} : { index: recurNonEmpty(node.index) }),
      };
      case "apply": return { ...node, id, argument: recurRow(node.argument) };
      case "group": return { ...node, id, body: recurRow(node.body) };
      case "scripted": return {
        ...node,
        id,
        base: recurNonEmpty(node.base),
        ...(node.superscript === undefined ? {} : { superscript: recurNonEmpty(node.superscript) }),
        ...(node.subscript === undefined ? {} : { subscript: recurNonEmpty(node.subscript) }),
      };
      case "accent": return { ...node, id, body: recurNonEmpty(node.body) };
      case "large-operator": return {
        ...node,
        id,
        ...(node.lower === undefined ? {} : { lower: recurNonEmpty(node.lower) }),
        ...(node.upper === undefined ? {} : { upper: recurNonEmpty(node.upper) }),
      };
      case "labeled-arrow": return { ...node, id, label: recurNonEmpty(node.label) };
    }
  };
  return recurRow(row);
}

export function isHoleNode<P extends Phase>(node: Expr<P>): node is Extract<Expr<P>, { tag: "hole" }> {
  return node.tag === "hole";
}

export function rowContainsHole(row: Row<"draft">): boolean {
  return row.some((node) => {
    if (node.tag === "hole") return true;
    return childRows(node).some(({ row: child }) => rowContainsHole(child as Row<"draft">));
  });
}

export type ChildSlot =
  | "fraction.numerator"
  | "fraction.denominator"
  | "radical.index"
  | "radical.radicand"
  | "apply.argument"
  | "group.body"
  | "scripted.base"
  | "scripted.superscript"
  | "scripted.subscript"
  | "accent.body"
  | "large-operator.lower"
  | "large-operator.upper"
  | "labeled-arrow.label";

export interface ChildRow<P extends Phase> {
  readonly slot: ChildSlot;
  readonly row: Row<P>;
}

/** The unique traversal order for rendering, cursor movement, holes, and serialization. */
export function childRows<P extends Phase>(node: Expr<P>): readonly ChildRow<P>[] {
  switch (node.tag) {
    case "identifier":
    case "number":
    case "symbol":
    case "hole":
      return [];
    case "fraction":
      return [
        { slot: "fraction.numerator", row: node.numerator },
        { slot: "fraction.denominator", row: node.denominator },
      ];
    case "radical":
      return [
        ...(node.index === undefined ? [] : [{ slot: "radical.index" as const, row: node.index }]),
        { slot: "radical.radicand", row: node.radicand },
      ];
    case "apply": return [{ slot: "apply.argument", row: node.argument }];
    case "group": return [{ slot: "group.body", row: node.body }];
    case "scripted":
      return [
        { slot: "scripted.base", row: node.base },
        ...(node.superscript === undefined ? [] : [{ slot: "scripted.superscript" as const, row: node.superscript }]),
        ...(node.subscript === undefined ? [] : [{ slot: "scripted.subscript" as const, row: node.subscript }]),
      ];
    case "accent": return [{ slot: "accent.body", row: node.body }];
    case "large-operator":
      return [
        ...(node.lower === undefined ? [] : [{ slot: "large-operator.lower" as const, row: node.lower }]),
        ...(node.upper === undefined ? [] : [{ slot: "large-operator.upper" as const, row: node.upper }]),
      ];
    case "labeled-arrow": return [{ slot: "labeled-arrow.label", row: node.label }];
  }
}

export function rowIsPlaceholderOnly(row: Row<"draft">): boolean {
  return row.length === 0 || row.every((node) => node.tag === "hole");
}

export function nodeIsStructurallyEmpty(node: Expr<"draft">): boolean {
  const children = childRows(node);
  return children.length > 0 && children.every(({ row }) => rowIsPlaceholderOnly(row));
}

export const demoDocument = (): Document<"draft"> => [[
  identifier("F"),
  symbol("adjunction"),
  identifier("G"),
  symbol("colon"),
  identifier("C", "calligraphic"),
  symbol("right-left-arrows"),
  identifier("D", "calligraphic"),
]];
EOF

```

<details><summary>💭 Thinking</summary>

**Built and validated a structural mathematical expression editor**

</details>

```unknown
bash -lc python -m http.server 8765 --bind 127.0.0.1
```

The rebuilt core now type-checks and passes 34 assertions, adding phase-indexed trees, explicit compilation-loss diagnostics, validated persistence, pure history, and deterministic edit transitions.

<details><summary>💭 Thinking</summary>

**Building the thesis package**

I’m assembling the formal chapters, rebuilt implementation, diagrams, screenshots, references, tests, and PDF-ready source into a coherent package. I’m preserving the mathematical corrections while documenting limitations and verification results clearly.

**Built the thesis package**

</details>

```unknown
bash -lc sed -n '1,240p' /home/oai/skills/pdfs/SKILL.md && printf '\n--- THESIS TAIL ---\n' && tail -n 80 /mnt/data/structural-editor-thesis/thesis.md && printf '\n--- TREE ---\n' && find /mnt/data/structural-editor-thesis -maxdepth 3 -type f | sort | sed -n '1,220p'
```

<details><summary>💭 Thinking</summary>

**Inspected, rebuilt, tested, and documented the structural editor thesis materials**

</details>

```unknown
bash -lc cat >> /mnt/data/structural-editor-thesis/thesis.md <<'EOF'

# 6. Containers, Derivatives, and One-Hole Contexts

## 6.1 Why a cursor is a mathematical object

A cursor in a flat string is often represented by an integer. The integer is meaningful because the string has a single linear dimension: the prefix before the integer and the suffix after it determine a unique decomposition. A structural document has several nested rows. A focus therefore has two components:

1. a decomposition of the current row around a selection; and
2. enough surrounding context to reconstruct the path back to the root.

The supplied implementation records the second component only as a list of dynamic field names and child indices. That is a valid *address representation*, but it is not yet the data structure introduced by Huet as a zipper [@huet-1997]. A zipper stores the context itself, so local replacement and reconstruction do not repeatedly traverse from the root.

The categorical reason that zippers arise is that a one-hole context is a derivative of a datatype. McBride made this slogan precise for regular types: the derivative of a regular type is its type of one-hole contexts [@mcbride-2001]. Containers extend the same reasoning to a broad class of strictly positive types [@abbott-altenkirch-ghani-2005].

## 6.2 The container presentation

A container is given by a set of shapes $S$ and, for each shape $s\in S$, a set of positions $P(s)$. Its extension is the endofunctor

$$
\llbracket S\triangleleft P\rrbracket(X)
=
\sum_{s\in S} X^{P(s)}.
$$

An element consists of a shape and a function assigning an $X$-value to each position in that shape. The syntax signature from Chapter 4 is a container because each constructor supplies a finite shape and a finite family of recursive child positions. For example:

- a fraction shape has the positions `numerator` and `denominator`, each containing a non-empty list of recursive values;
- a group shape contains a delimiter identity and one list position;
- a scripted shape chooses one of the attachment patterns $\mathsf{sup}$, $\mathsf{sub}$, or $\mathsf{both}$ and contains the corresponding rows; and
- a symbol shape has no recursive positions.

Strictly speaking, list-valued child fields mean that the complete signature is assembled from sums, products, constants, lists, and non-empty lists. Each of these constructions is container-like and strictly positive. The practical consequence is that child positions can be enumerated without inspecting output syntax or UI state.

## 6.3 Formal differentiation rules

For polynomial functors, differentiation follows familiar algebraic rules:

$$
0'=0,
\qquad
1'=0,
\qquad
X'=1,
$$

$$
(F+G)'=F'+G',
\qquad
(F\times G)'=(F'\times G)+(F\times G'),
$$

and, for composition,

$$
(F\circ G)'=(F'\circ G)\times G'.
$$

For lists,

$$
\operatorname{List}'(X)
\cong
\operatorname{List}(X)\times\operatorname{List}(X).
$$

The two lists are the elements to the left and right of the hole. For non-empty lists, the same local representation applies once one remembers the invariant required when plugging the hole.

The derivative of the recursive syntax functor enumerates a choice of constructor, a choice of one recursive position in that constructor, and all sibling data needed to reconstruct the constructor. A fraction context focused in its numerator stores the denominator; a context focused in its denominator stores the numerator. A group context stores the delimiter. A superscript context stores the base and optional subscript.

## 6.4 Row focus as a selected-list zipper

The editor must focus not only a single missing element but a half-open interval. For a current row $r$, define a row focus

$$
\mathsf{RF}_p
=
\mathsf{Row}_p
\times
\mathsf{Row}_p
\times
\mathsf{Row}_p,
$$

written

$$
\langle L\mid M\mid R\rangle.
$$

Here $L$ is the prefix, $M$ is the selected segment, and $R$ is the suffix. A caret is the special case $M=[]$. Plugging is concatenation:

$$
\mathsf{rowOf}\langle L\mid M\mid R\rangle=L\cdot M\cdot R.
$$

This decomposition directly expresses the editor's replacement operation:

$$
\mathsf{replace}(N,
  \langle L\mid M\mid R\rangle)
=
\langle L\mid N\mid R\rangle
$$

before the new selection is collapsed or redirected to an inserted hole.

A selected-list zipper is equivalent to a list plus two ordered boundaries $0\le s\le e\le |r|$:

$$
L=r[0:s],
\quad
M=r[s:e],
\quad
R=r[e:|r|].
$$

The zipper form is efficient for local editing; the boundary form is convenient for persistence and interchange.

## 6.5 Typed derivative frames

The reconstructed implementation defines a closed union of context frames. Representative cases are:

```typescript
type RowContext<P extends Phase> =
  | {
      tag: "fraction.numerator";
      parentLeft: Row<P>;
      parentRight: Row<P>;
      denominator: NonEmptyRow<P>;
      id: NodeId;
    }
  | {
      tag: "fraction.denominator";
      parentLeft: Row<P>;
      parentRight: Row<P>;
      numerator: NonEmptyRow<P>;
      id: NodeId;
    }
  | {
      tag: "group.body";
      parentLeft: Row<P>;
      parentRight: Row<P>;
      delimiter: DelimiterPair;
      id: NodeId;
    };
```

Every frame stores:

- the siblings to the left and right of the parent node in its row;
- the constructor identity required to rebuild the node;
- the non-focused child fields; and
- the stable node ID.

The frame tag is not an arbitrary string. It is one of the finite `ChildSlot` alternatives. A frame that says it focuses a fraction numerator statically carries a denominator. There is no generic object lookup of the form `node[fieldName]` during plugging.

![A row selection and a stack of typed derivative frames form the runtime zipper.](figures/zipper.png){#fig:zipper width=92%}

## 6.6 The complete document zipper

A document also has a linear sequence of root rows. The complete zipper is

$$
\mathsf{DZ}_p
=
\mathsf{RowsBefore}_p
\times
\mathsf{RowFocus}_p
\times
\mathsf{ContextStack}_p
\times
\mathsf{RowsAfter}_p.
$$

The implementation combines the focus and context stack:

```typescript
interface RowFocus<P extends Phase> {
  readonly left: Row<P>;
  readonly selected: Row<P>;
  readonly right: Row<P>;
  readonly up: readonly RowContext<P>[];
}

interface DocumentZipper<P extends Phase> {
  readonly beforeLines: readonly Row<P>[];
  readonly focus: RowFocus<P>;
  readonly afterLines: readonly Row<P>[];
}
```

Frames are stored outer-to-inner. Reconstruction folds from the innermost frame outward. This order is convenient for deriving a persistent root-to-leaf address, while the reverse iteration is convenient for plugging.

## 6.7 Plugging a context

For each context frame $C$ there is a partial plug operation

$$
\mathsf{plug}_p:C_p\times\mathsf{Row}_p
\rightharpoonup
\mathsf{Expr}_p.
$$

The operation is partial only because certain child positions require non-empty rows. In a well-formed runtime state, those positions remain non-empty, so plugging succeeds. During draft deletion, normalization inserts a hole before reconstruction if a required focused row would otherwise become empty.

Representative equations are

$$
\mathsf{plug}
(\mathsf{FracNumCtx}(id,L,R,d),n)
=
\mathsf{Fraction}_{id}(n,d),
$$

$$
\mathsf{plug}
(\mathsf{GroupCtx}(id,L,R,k),b)
=
\mathsf{Group}_{id}(k,b),
$$

and

$$
\mathsf{plug}
(\mathsf{ScriptSupCtx}(id,L,R,b,l),u)
=
\mathsf{Scripted}_{id}(b,u,l).
$$

The surrounding row is then

$$
L\cdot[\mathsf{plug}(C,child)]\cdot R.
$$

Repeated plugging produces the root row, and the root row is inserted between the preceding and following document lines.

## 6.8 Unplugging from a validated address

For persistence and external commands, the system uses an address

$$
a=(\ell,\pi,s,e),
$$

where $\ell$ is a line index, $\pi$ is a root-to-row sequence of typed path steps, and $[s,e)$ is a selection interval. A path step is

$$
(i,\sigma),
$$

where $i$ selects a node in the current row and $\sigma$ names a child slot valid for that node's constructor.

The `locate` function validates each step. It checks:

1. that the line exists;
2. that $0\le s\le e\le |r|$ at the final row;
3. that each node index is in range;
4. that the requested slot belongs to the node tag; and
5. that required child rows are non-empty.

As it descends, `locate` constructs the corresponding typed context frame. The output is therefore a zipper whose internal invariants have been established by checking the address against the document.

## 6.9 Zipper laws

Let $\mathsf{docOf}$ reconstruct a document from a zipper and $\mathsf{addrOf}$ derive its persistent address. Because IDs and array values are preserved by plugging, the implementation is designed to satisfy the following laws.

**Law 6.1 (Reconstruction).** For every valid document $d$ and address $a$,

$$
\mathsf{locate}(d,a)=\mathsf{Ok}(z)
\quad\Longrightarrow\quad
\mathsf{docOf}(z)=\mathsf{Ok}(d).
$$

**Law 6.2 (Address recovery).** Under the same premise,

$$
\mathsf{addrOf}(z)=a.
$$

**Law 6.3 (Relocation).** For every valid zipper $z$,

$$
\mathsf{docOf}(z)=\mathsf{Ok}(d)
\quad\Longrightarrow\quad
\mathsf{locate}(d,\mathsf{addrOf}(z))
=
\mathsf{Ok}(z')
$$

where $z'$ has the same focused document decomposition as $z$. Object identity of arrays is not required; structural equality is.

**Proof sketch.** All three laws follow by induction over the path/context stack. `locate` decomposes exactly the parent row and child fields later consumed by `plug`. Each context constructor is inverse to its corresponding child projection. At the leaf, list slicing is inverse to concatenation for a valid interval. $\square$

The executable tests check representative instances of reconstruction and address recovery. A production property-test suite should quantify over generated well-formed documents and addresses.

## 6.10 Selection is two holes, not one

The derivative account describes a point focus. A contiguous selection can be understood in two equivalent ways:

- a row with two ordered cuts; or
- a one-hole context whose hole contains a row segment rather than a single element.

The second view is useful for wrapping. If $C[-]$ is the current row context and $M$ is selected, then applying a function is

$$
C[M]
\longmapsto
C[\mathsf{Apply}(f,M)].
$$

Selection growth changes the factorization rather than the document. It first chooses a neighboring element, then the entire current row, then the parent node represented by the top derivative frame.

## 6.11 Complexity

Let $h$ be focus depth, $m$ the size of the focused row, and $n$ the total document size.

- replacing the selected segment allocates arrays proportional to the current row prefix/suffix and inserted segment, so its reference implementation cost is $O(m)$;
- reconstructing the document costs $O(h)$ constructor rebuilds plus parent-row copying;
- moving by using the globally enumerated position sequence costs $O(n)$ in the current reference implementation;
- locating a persistent address costs $O(h)$ node accesses plus row slicing; and
- compiling costs $O(n)$.

These costs favor clarity over optimality. The semantics does not require global position enumeration. A production zipper can implement next/previous traversal by local frame transitions in amortized constant or depth-proportional time. Persistent vectors or ropes can reduce row-copying costs.

## 6.12 Chapter exercises

1. Differentiate the functor $F(X)=A+X\times X$ and interpret each summand as a tree context.
2. Derive the one-hole contexts of a fraction constructor with list-valued numerator and denominator.
3. Extend the row focus to a non-contiguous multi-selection. Which simple zipper law is lost?
4. Prove list slicing and concatenation are inverse for valid half-open intervals.
5. Design a local `nextPosition` operation that avoids enumerating the whole document.

# 7. Addresses, Focus Invariants, and Structural Selection

## 7.1 Runtime focus versus serialized address

A zipper and an address solve different problems.

A runtime zipper is optimized for editing. It contains sibling data and can reconstruct locally. A serialized address is compact and stable across process boundaries. It contains indices and finite child-slot names and must be validated against a document before use.

Conflating these representations causes two common errors. First, a dynamic path is called a zipper even though every update starts at the root. Second, an address is trusted as if its target necessarily exists. The reconstruction uses both representations and defines explicit conversions.

## 7.2 Focus well-formedness

Write

$$
d\vdash z\;\mathsf{focus}
$$

when zipper $z$ focuses document $d$. The judgment requires:

1. `documentOf(z) = Ok(d)`;
2. every frame's node tag, slot, and sibling data are mutually consistent;
3. every required child row rebuilt by a frame is non-empty;
4. the document has at least one line; and
5. the selected row segment is contiguous by construction.

Because a zipper stores a decomposition rather than numeric boundaries, its current selection is intrinsically within the row. Invalid numeric selection bounds can arise only when constructing a zipper from an external address.

## 7.3 Canonical carets and selections

A caret is a focus with empty selection:

$$
\mathsf{caret}(z)\iff z.M=[].
$$

A selected hole is represented by $M=[\mathsf{Hole}(h,k)]$. This distinction is operationally useful. Typing at a caret inserts before the right suffix. Typing while a hole is selected replaces that hole. The same generic replacement operation handles both cases.

For a row $r$, each integer $i$ with $0\le i\le |r|$ determines a caret event. Each hole occurrence determines a selectable hole event. The reference implementation enumerates these events in a depth-first order derived solely from `childRows`.

## 7.4 Traversal order

Define $\mathsf{positions}(r,\pi)$ recursively. It emits a caret at every boundary of the current row. Before proceeding to the next boundary after node $r_i$, it recursively emits positions in each child row of $r_i$ in `childRows` order. A hole node also emits a selected-hole event at $[i,i+1)$.

For a fraction this yields an order schematically like

```text
before fraction
  numerator boundary 0
  numerator contents and descendants
  numerator final boundary
  denominator boundary 0
  denominator contents and descendants
  denominator final boundary
after fraction
```

This is a depth-first *editing order*, not necessarily geometric left-to-right order. The renderer may place a numerator above a denominator, but the traversal still has a deterministic logical sequence.

## 7.5 Movement

The original source implements movement by entering the first child when moving right over a structural node, entering the last child when moving left, moving between sibling fields, and then climbing to the parent. The reference reconstruction obtains the same logical order by enumerating positions and choosing the adjacent caret.

Let $\prec$ be the total order induced by `positions`. Then

$$
\mathsf{move}_{+}(z)
=
\min_{\prec}\{c\mid \mathsf{addr}(z)\prec c\text{ and }c\text{ is a caret}\},
$$

if such a caret exists. Movement left is the analogous predecessor. A non-empty selection first collapses to its left boundary for left movement or its right boundary for right movement.

At a document boundary, movement is a no-op with an informational notice. This makes the transition function total.

## 7.6 Hole traversal

Hole traversal filters the same position sequence to selected-hole events. The next-hole command chooses the first hole after the current event and wraps to the first hole if none follows. Previous-hole traversal is symmetric.

If the document contains no holes, the command returns the unchanged state and a `no-hole` notice. It does not fabricate a hole or throw an exception.

The shared traversal order prevents divergence between movement and template navigation. In the supplied implementation, `fieldsOf`, `FIELD_ORDER`, and custom trace flattening independently encode related assumptions. The reconstruction derives both behaviors from one event sequence.

## 7.7 Structural selection growth

Selection growth implements an inclusion hierarchy. Let the current focus be $\langle L\mid M\mid R\rangle$.

1. If $M=[]$ and $L\ne[]$, select the last element of $L$.
2. Else if $M=[]$ and $R\ne[]$, select the first element of $R$.
3. Else if $M$ is not the whole row, select the whole row.
4. Else if there is a parent frame, pop to the parent row and select the parent node.
5. Else the whole root line is already selected; return a boundary notice.

This defines a monotone sequence of regions under subtree containment until the root line is reached. The command does not alter document syntax.

**Proposition 7.1 (Growth monotonicity).** If `grow-selection` changes a state from focus region $S$ to region $S'$, then $S$ is contained in $S'$ in the occurrence tree of the current document.

**Proof sketch.** Cases 1 and 2 move from an empty boundary to one adjacent occurrence. Case 3 replaces an interval with the entire containing row. Case 4 replaces the whole focused child row with the unique parent node containing it. Each case is an inclusion; no case selects a disjoint occurrence. $\square$

## 7.8 Structural deletion

Backward deletion has four cases.

**Selected interval.** Remove the selected nodes and collapse to the left boundary.

**Previous atomic or structurally empty node.** Remove the previous node.

**Previous non-empty structural node.** Do not destroy it. Move the caret into its last child row at that row's end.

**Start of a nested row.** Move to the predecessor position, which climbs through context if needed.

At the start of a root row, a placeholder-only line may be removed if another line remains. Otherwise deletion is a no-op.

The distinction between an empty template and a populated structure is crucial. A newly inserted fraction containing only holes can be removed as a unit. A fraction containing user content is entered first, reducing accidental destructive deletion.

## 7.9 Required-row normalization

Suppose deleting a selected node empties a fraction denominator. The abstract type requires a non-empty row. Rather than allowing an invalid intermediate tree, the draft editor normalizes the immediate required focus:

$$
[]\leadsto[\mathsf{Hole}(fresh,\mathsf{expression})].
$$

The expected hole class depends on the context: an index slot receives an index hole, a bound slot receives a bound hole, and a labeled arrow receives a label hole.

Optional or empty-permitted rows, such as a group body or function argument, remain empty. Thus normalization is context-sensitive but finite and total.

**Proposition 7.2 (Required focus normalization).** If a draft zipper differs from a well-formed zipper only in that its immediate focused child row is empty, then `normalizeRequiredDraftFocus` produces a zipper whose focused child satisfies the constructor's non-emptiness requirement and whose document differs only by insertion of one fresh hole when the context requires it.

The proposition is immediate from the finite context case analysis.

## 7.10 Identity and address stability

Stable node IDs do not replace structural addresses. An ID identifies an occurrence while it survives; an address identifies a location in a particular document version. Edits before an occurrence can change its address without changing its ID. Copying a template must change its IDs even when its shape remains identical.

This suggests a future hybrid anchoring scheme:

$$
\mathsf{Anchor}=\mathsf{NodeId}\times\mathsf{RelativeSlot}\times\mathsf{FallbackAddress}.
$$

The reference implementation deliberately does not promise address stability across arbitrary edits. Persistence saves an address only alongside the exact document snapshot to which it refers.

## 7.11 Selection algebra

Three operations are especially useful:

- `collapseLeft` maps $\langle L\mid M\mid R\rangle$ to $\langle L\mid[]\mid M\cdot R\rangle$;
- `collapseRight` maps it to $\langle L\cdot M\mid[]\mid R\rangle$;
- `replace(N)` maps it to $\langle L\mid N\mid R\rangle$.

They satisfy:

$$
\mathsf{rowOf}(\mathsf{collapseLeft}(z))
=
\mathsf{rowOf}(z),
$$

$$
\mathsf{rowOf}(\mathsf{collapseRight}(z))
=
\mathsf{rowOf}(z),
$$

and

$$
\mathsf{rowOf}(\mathsf{replace}(N,z))
=L\cdot N\cdot R.
$$

Collapse operations are idempotent. Replacement followed by selecting the inserted segment is a local lens-like update, though the full zipper is more accurately a context decomposition than a single total lens.

## 7.12 Chapter exercises

1. Formalize the focus well-formedness judgment as inference rules.
2. Prove collapse-left and collapse-right are idempotent.
3. Give an example where an occurrence ID remains stable but its structural address changes.
4. Compare depth-first editing order with geometric arrow-key navigation. What additional layout information would geometric movement require?
5. Define a selection-shrink command that is a partial inverse of growth.

# 8. A Type-Theoretic Account of Incomplete Notation

## 8.1 Intrinsic and extrinsic invariants

A representation is **intrinsic** when well-formedness is expressed by the type of its constructors. It is **extrinsic** when values inhabit a broad type and a separate predicate or validator checks them.

The reconstruction deliberately combines both styles.

Intrinsic invariants include:

- finite constructor tags;
- finite delimiter, accent, operator, and arrow kinds;
- non-empty required child rows;
- a script base owned by its script node;
- at least one script attachment at construction time;
- holes absent from `Expr<"complete">`; and
- typed context frames.

Extrinsic invariants include:

- uniqueness of node and hole IDs across a document;
- lexical validity of identifier and number text;
- a persisted address locating a real row;
- symbol IDs occurring in the current catalog; and
- JSON values having the expected object structure.

TypeScript can encode the first class reasonably well. The second class requires runtime checking.

## 8.2 Draft terms are not malformed complete terms

A common editor architecture treats an incomplete expression as a malformed string that fails to parse. Structure editors reverse that perspective: incompleteness is represented by syntax. Hazelnut develops this principle for a typed lambda calculus with expression holes and non-empty holes, proving that edit actions preserve sensibility [@omar-et-al-2017].

The notation editor is less ambitious because its rows do not carry mathematical typing judgments. Nevertheless, phase indexing gives a useful distinction:

$$
\mathsf{Document}_{\mathsf{draft}}
\not\equiv
\mathsf{Document}_{\mathsf{complete}}.
$$

A draft document is valid editor data even when it contains obligations. Completion is a checked phase transition, not an assumption.

## 8.3 Hole expectations as a lightweight judgment

A hole is written

$$
\square_h^\kappa,
$$

where $h$ is a stable hole identity and $\kappa$ is an expectation class. The expectation classes form a finite set

$$
\mathcal K=
\{\mathsf{expression},\mathsf{index},\mathsf{bound},
  \mathsf{argument},\mathsf{label}\}.
$$

We may write a coarse synthesis judgment

$$
\Gamma\vdash\square_h^\kappa\Rightarrow\kappa.
$$

This judgment does not state a mathematical object type. It records the syntactic role expected by the parent constructor. Insertion does not currently reject a node whose role seems inconsistent; the expectation is advisory and supports UI and diagnostics. A future elaborator could refine it into a genuine bidirectional judgment.

## 8.4 Formation rules with phase

The hole formation rule is phase-sensitive:

$$
\frac{}{
  \Gamma\vdash_{\mathsf{draft}}
  \square_h^\kappa\;\mathsf{wf}}
\qquad
\text{and there is no corresponding complete rule.}
$$

Other constructors are phase-polymorphic. For example:

$$
\frac{
  \Gamma\vdash_p n\;\mathsf{nrow}
  \qquad
  \Gamma\vdash_p d\;\mathsf{nrow}
}{
  \Gamma\vdash_p \frac{n}{d}\;\mathsf{wf}
}.
$$

The phase parameter propagates uniformly through recursive children. This is a two-point indexed family rather than a runtime flag on each node.

## 8.5 At-least-one constraints

The script attachment invariant is a sum type:

$$
\mathsf{Attachments}(X)
=
\mathsf{SupOnly}(X)
+
\mathsf{SubOnly}(X)
+
\mathsf{Both}(X,X).
$$

The implementation uses two optional fields and a smart constructor returning an error when both are absent. A more intrinsic TypeScript representation would encode the three variants directly:

```typescript
type Attachments<P extends Phase> =
  | { tag: "sup"; superscript: NonEmptyRow<P> }
  | { tag: "sub"; subscript: NonEmptyRow<P> }
  | {
      tag: "both";
      superscript: NonEmptyRow<P>;
      subscript: NonEmptyRow<P>;
    };
```

The current representation is retained because it simplifies backend code and persisted schema. The smart constructor and decoder enforce the invariant. This illustrates a practical design tradeoff between canonical sum structure and convenient record access.

## 8.6 Refinement by validation

A runtime decoder has the conceptual type

$$
\mathsf{decodeDraft}:
\mathsf{Unknown}	o
\mathsf{Result}(
  \mathsf{Document}_{\mathsf{draft}},
  \operatorname{List}(\mathsf{ValidationIssue})).
$$

Successful decoding refines an untyped value into an intrinsically useful type. The implementation accumulates path-indexed issues rather than failing at the first error. It validates:

- object and array shape;
- constructor tags;
- finite enum fields;
- non-empty required rows;
- duplicate node and hole IDs;
- string-valued IDs and text;
- known child slots in addresses;
- integer and ordered selection bounds; and
- final address locatability.

A TypeScript assertion such as `value as Document<"draft">` would provide no runtime evidence. The decoder constructs evidence by exhaustive case analysis.

## 8.7 Branded identities

TypeScript's structural type system would otherwise confuse node IDs, hole IDs, and symbol IDs because all are strings. Branding introduces compile-time distinctions:

```typescript
type Brand<T, Name extends string> =
  T & { readonly __brand: Name };

type NodeId = Brand<string, "NodeId">;
type HoleId = Brand<string, "HoleId">;
type SymbolId = Brand<string, "SymbolId">;
```

Brands do not add runtime security. The decoder must still validate strings and uniqueness. Their value is local type discipline: a function requiring `SymbolId` cannot accidentally receive a `NodeId` without an explicit unsafe cast.

## 8.8 Completion as proof search

The function `completeDocument` recursively attempts to construct a value in the complete phase. It can be read as a proof search procedure for the proposition “this draft contains no holes.”

For each node:

- atomic non-hole nodes are copied;
- a hole contributes a `hole-remains` issue and no complete node;
- a compound constructor recursively completes child rows;
- the constructor is rebuilt only when the needed children succeed.

At the document level, success yields a complete document. Failure yields all discovered hole paths.

The returned complete value is evidence usable by downstream APIs:

```typescript
function exportForPublication(
  doc: Document<"complete">,
): PublicationArtifact;
```

Such an API cannot be called with a draft without first handling validation.

## 8.9 Preservation versus normalization

There are two ways to maintain a required-field invariant during editing.

**Preservation by command restriction.** Reject an edit that would empty the field.

**Preservation by normalization.** Permit the user's deletion but replace the invalid empty result with a hole.

The reconstruction chooses normalization because it matches structural editor behavior: a required field remains editable and visibly incomplete. The type-level invariant is preserved while the user's intent to remove previous content is respected.

This distinction is important in proofs. The transition semantics does not merely preserve the exact syntax shape; it preserves membership in the well-formed draft language, possibly by adding fresh editor syntax.

## 8.10 A stronger dependent formulation

In a dependently typed language, required rows and attachments could be indexed by proofs:

$$
\mathsf{Row}(p,n)
$$

for a row of length $n$, with fractions requiring $n\ge1$ and $m\ge1$. A path could be indexed by its source document and target row, making invalid paths unrepresentable. A zipper could satisfy

$$
\mathsf{plug}:\mathsf{Context}(d,r)\to r\to d
$$

by type.

The TypeScript reconstruction approximates this design with non-empty tuples, discriminated unions, and checked `Result` values. It does not claim the compiler proves the full semantic preservation theorem. The executable validators are part of the trusted boundary.

## 8.11 Relation to domain typing

Nothing in the phase index determines whether `F : C -> D` is a functor, whether `x + y` is well-typed, or whether a subscript denotes an index. To add domain semantics, one would introduce an elaboration judgment

$$
\Gamma\vdash r\rightsquigarrow t:A
$$

mapping notation rows to terms $t$ of a mathematical object language with type $A$. That layer would resolve precedence, names, binding, overloads, and implicit arguments. The notation AST would remain the concrete structured presentation from which elaboration begins.

This separation follows a standard language-design pattern: parsing/presentation syntax, elaborated syntax, typing, and semantics are distinct phases [@pierce-2002].

## 8.12 Chapter exercises

1. Replace optional script fields with the explicit three-way `Attachments` sum and update the signature functor.
2. Define a phase with named metavariables that may remain in an exported theorem statement.
3. Identify which validation invariants could be moved into a dependently typed path representation.
4. Explain why brands improve local discipline but do not validate JSON.
5. Design an elaboration rule for function application notation and state the ambiguity introduced by juxtaposition.
EOF
```

<details><summary>💭 Thinking</summary>

**Rebuilt, audited, and formatted thesis with appendices and PDF build checks**

</details>

```unknown
bash -lc cd /mnt/data/structural-editor-thesis && /usr/bin/time -v pandoc thesis.md --from=markdown+tex_math_dollars+raw_tex --to=latex --standalone --citeproc --toc --toc-depth=2 --highlight-style=tango --metadata link-citations=true --include-in-header=build/thesis_header.tex --resource-path="$PWD" -o build/thesis.tex >build/pandoc.stdout 2>build/pandoc.stderr; status=$?; echo STATUS=$status; tail -n 50 build/pandoc.stderr; ls -lh build/thesis.tex
```

<details><summary>💭 Thinking</summary>

**Debugged LaTeX thesis compilation, patched macros, fonts, glyphs, and layout warnings**

</details>

```unknown
bash -lc rm -rf /mnt/data/structural-editor-thesis/_pdf_render && python /home/oai/skills/pdfs/scripts/pdf_inspect.py /mnt/data/structural-editor-thesis/thesis.pdf > /mnt/data/structural-editor-thesis/analysis/pdf-inspect.txt && python /home/oai/skills/pdfs/scripts/render_pdf.py /mnt/data/structural-editor-thesis/thesis.pdf --out_dir /mnt/data/structural-editor-thesis/_pdf_render --dpi 120 > /mnt/data/structural-editor-thesis/analysis/pdf-render.txt 2>&1 && echo rendered && ls /mnt/data/structural-editor-thesis/_pdf_render | wc -l && sed -n '1,220p' /mnt/data/structural-editor-thesis/analysis/pdf-inspect.txt && tail -n 30 /mnt/data/structural-editor-thesis/analysis/pdf-render.txt
```

The final 145-page edition now maps tests to formal laws and clearly limits theorem-level soundness to typed elaboration; renderer, page, and artifact preflight checks remain before packaging.

<details><summary>💭 Thinking</summary>

**Inspected, rebuilt, tested, and rendered thesis PDF sources and outputs**

</details>

```unknown
from PIL import Image, ImageOps, ImageDraw
from pathlib import Path
paths=sorted(Path('/mnt/data/structural-editor-thesis/_pdf_check').glob('*.png'))
len(paths), [p.name for p in paths[:]]

```

<details><summary>💭 Thinking</summary>

**Created contact sheet from sample images**

</details>

```unknown
bash -lc find /mnt/data/structural-editor-thesis/_pdf_check -maxdepth 1 -type f -printf '%f
' | sort
```

<details><summary>💭 Thinking</summary>

**Inspected PDF files, render paths, scripts, and missing directories**

</details>

```unknown
from pathlib import Path
list(Path('/mnt/data').iterdir())[:10], Path('/mnt/data/structural-editor-thesis').exists()

```

<details><summary>💭 Thinking</summary>

**Checked filesystem persistence and directory recovery**

</details>

```unknown
bash -lc find /tmp /mnt/data -maxdepth 3 -type d -name 'structural-editor-thesis*' -print 2>/dev/null | sed -n '1,100p'; ls -la /tmp | sed -n '1,120p'
```

<details><summary>💭 Thinking</summary>

**Built and tested structural editor thesis package with screenshots**

</details>

```unknown
from PIL import Image, ImageOps, ImageDraw
from pathlib import Path
paths=sorted(Path('/mnt/data/structural-editor-thesis/screenshots').glob('*.png'))
ims=[]
for p in paths:
    im=Image.open(p).convert('RGB')
    im.thumbnail((750,525))
    canvas=Image.new('RGB',(770,565),'white')
    canvas.paste(im,((770-im.width)//2,30))
    ImageDraw.Draw(canvas).text((10,8),p.name,fill='black')
    ims.append(canvas)
sheet=Image.new('RGB',(1540,1130),'white')
for i,im in enumerate(ims):
    sheet.paste(im,((i%2)*770,(i//2)*565))
sheet.save('/mnt/data/structural-editor-thesis/analysis/screenshots-contact.png')
'/mnt/data/structural-editor-thesis/analysis/screens
```

<details><summary>💭 Thinking</summary>

**Inspecting structural editor screenshots**

</details>

```unknown
bash -lc ls -ld /mnt/data/structural-editor-thesis /mnt/data/structural-editor-thesis/analysis /mnt/data/structural-editor-thesis/screenshots; id
```

## Deliverables

- [Markdown thesis](sandbox:/mnt/data/structural_editor_thesis/thesis/structural-math-editor-thesis.md)
- [Typeset PDF thesis](sandbox:/mnt/data/structural_editor_thesis/thesis/structural-math-editor-thesis.pdf)
- [Complete source, thesis, figures, screenshots, implementation, and verification bundle](sandbox:/mnt/data/structural-math-editor-thesis-bundle.zip)
- [ZIP SHA-256 checksum](sandbox:/mnt/data/structural-math-editor-thesis-bundle.zip.sha256)

The reconstruction retains the source artifact’s central premise—an AST rendered directly, several code-generation backends over that tree, and a cursor represented by a structural path and offset—but replaces the informal implementation assumptions with explicit mathematical objects and invariants. fileciteturn0file0L5-L8

## Contents

The main volume is a **145-page, approximately 28,000-word textbook-style thesis** containing thirteen chapters and seven appendices. It develops:

- a forensic decomposition of the original React component;
- an inductive and polynomial presentation of the syntax;
- non-empty recursive slots and uniquely identified holes;
- checked paths, sequence zippers, one-hole contexts, and partial-lens laws;
- a deterministic small-step operational semantics for editing;
- preservation, progress, determinism, and failure-atomicity obligations;
- denotational semantics at the editor, backend, presentation-neutral, and typed-object levels;
- a generic syntax algebra and catamorphic backend architecture;
- an intrinsic dependent-type specification and a disciplined TypeScript approximation;
- initial-algebra, derivative, Kleisli, product-algebra, and natural-transformation interpretations;
- a source-to-model correspondence, formal rule synopsis, solved exercises, glossary, and reproduction guide.

The bundled executable reconstruction includes:

- a presentation-neutral TypeScript syntax model;
- smart constructors and complete runtime validation;
- checked zipper resolution and reconstruction;
- a pure `Result`-valued command reducer;
- scripts that structurally own their bases;
- accents that wrap a selection, prior expression, or explicit hole;
- a dedicated annotated-arrow constructor;
- semantic symbol identities separated from backend spellings;
- LaTeX, Typst, and structural-Unicode folds;
- immutable undo/redo;
- versioned checked persistence;
- a browser demonstration and compiled JavaScript;
- baseline, reconstructed-interface, and test-run screenshots.

## Verification

The executable suite passes **13/13 tests**, including the three lens laws, backend totality, fresh-hole allocation, script and accent ownership, deletion invariants, persistence round trips, undo/redo, malformed-tree rejection, and a deterministic 350-command randomized preservation run.

All 145 PDF pages were rendered and inspected. No clipping, overlap, broken figures, replacement glyphs, or malformed equations were observed. Fonts are embedded. The PDF is not structurally tagged for accessibility; that limitation is recorded in the included verification report.

The soundness claim is deliberately stratified. The rebuilt editor enforces structural validity and gives commands and renderers precise semantics. Object-language mathematical correctness is not inferred from visual notation alone; it is assigned to a subsequent elaboration and type-checking phase parameterized by an explicit signature, context, and semantic model.

