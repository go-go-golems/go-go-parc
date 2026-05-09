# Source: Kagi Assistant (Kimi K2.5) — JS Persistent REPL Scoping Deep-Dive

**Date:** 2026-04-03  
**Tool:** Kagi Assistant (Kimi K2.5 model, web search enabled)  
**URL:** https://kagi.com/assistant/9b10a7a4-7129-4ec3-8365-2d3e687dbedb  
**Prompt:** See IIFE-01 research plan for full prompt text.

Kagi searched 5 queries:
1. ECMA-262 LexicalEnvironment DeclarativeEnvironmentRecord eval let const var persistence
2. JavaScript REPL IIFE capture replay pattern let const persistence edge cases
3. JavaScript REPL with scopeProxy pattern let const persistence deprecated semantic problems
4. Node.js REPL let const persistence source rewriting implementation details
5. ECMA-262 LexicalEnvironment (focused on ecma-international.org)

---

## 1. Why let/const Don't Survive Across eval() Calls

### The Core Mechanism: LexicalEnvironment vs. VariableEnvironment

**ECMA-262 §9.4** defines how execution contexts are created. Every execution context has two environment components:

- **LexicalEnvironment**: Used to resolve identifier references (tracks `let`, `const`, `class`, `import`)
- **VariableEnvironment**: Used for `var` declarations and function declarations

The critical distinction lies in **§18.2.1.1 PerformEval** (the `eval()` specification). When `eval()` is called directly:

1. A **new DeclarativeEnvironmentRecord** is created for the eval code
2. This environment is **chained to the caller's LexicalEnvironment**
3. `let`/`const` bindings are created in this **temporary** DeclarativeEnvironmentRecord
4. When `eval()` completes, this environment is **discarded** unless explicitly preserved

### The var Difference: VariableEnvironment Persistence

**ECMA-262 §9.4** and **§13.1.5** explain why `var` behaves differently:

```javascript
// Cell 1
eval("var a = 1; let b = 2; const c = 3;");
// a exists on global object → persists
// b, c exist in temporary DeclarativeEnvironmentRecord → destroyed

// Cell 2
eval("console.log(a);"); // 1 ✓
eval("console.log(b);"); // ReferenceError: b is not defined ✗
```

**Why `var` persists**: In sloppy mode, `var` declarations in global code create properties on the global object. The **VariableEnvironment** for global code *is* the global object's EnvironmentRecord (an ObjectEnvironmentRecord per **§9.1.1.2**). Since the global object persists, `var` bindings persist.

**Why `let`/`const` don't**: Per **§6.2.6**, `let`/`const` create bindings in a **DeclarativeEnvironmentRecord**, which is a spec-level abstraction separate from object properties. Each `eval()` call creates its own DeclarativeEnvironmentRecord that becomes unreachable after the eval context pops.

### The Execution Context Stack Visualization

```
Cell 1: eval("let x = 1")
┌─────────────────────────────────────────┐
│ Eval Execution Context                  │
│  ├─ LexicalEnvironment → New DeclarativeEnvRecord {x: 1}
│  └─ VariableEnvironment → (same as caller's)
└─────────────────────────────────────────┘
↓ eval completes, context popped
↓ DeclarativeEnvRecord with 'x' becomes unreachable

Cell 2: eval("console.log(x)")
┌─────────────────────────────────────────┐
│ Eval Execution Context                  │
│  ├─ LexicalEnvironment → NEW empty DeclarativeEnvRecord
│  └─ VariableEnvironment → (same)
└─────────────────────────────────────────┘
↓ 'x' lookup fails—no binding found
```

---

## 2. The IIFE Capture-and-Replay Pattern

This is the most robust workaround. The core idea: wrap each cell in a function, capture declared bindings from the return value, and replay them onto a persistent scope object.

### Basic Implementation

```javascript
class PersistentREPL {
  constructor(vm) {
    this.vm = vm;
    this.scope = {}; // Persistent scope object
  }

  async evaluateCell(code) {
    // 1. Inject current scope as parameters
    const scopeKeys = Object.keys(this.scope);
    const scopeValues = Object.values(this.scope);

    // 2. Wrap in async IIFE to support await at top level
    const wrapped = `
      (async function(${scopeKeys.join(', ')}) {
        ${code}
        // Capture all declared bindings
        return { ${this.extractDeclarations(code)} };
      })(${scopeValues.map(v => JSON.stringify(v)).join(', ')})
    `;

    // 3. Execute in VM
    const result = await this.vm.runInContext(wrapped, this.context);

    // 4. Replay captured bindings to persistent scope
    Object.assign(this.scope, result);
    return result;
  }

  extractDeclarations(code) {
    // Parse and extract let/const/class identifiers
    // (simplified—real implementation needs AST parsing)
    const declared = [];
    const letConstRegex = /(?:let|const|class)\s+([a-zA-Z_$][\w$]*)/g;
    let match;
    while ((match = letConstRegex.exec(code)) !== null) {
      declared.push(`${match[1]}: ${match[1]}`);
    }
    return declared.join(', ');
  }
}
```

### Edge Cases

#### Generators
Generators suspend execution and maintain internal state. Capturing the generator *function* works; capturing an active generator *iterator* fails across serialization boundaries.

```javascript
// PROBLEM: Generator iterator state is lost
await repl.evaluateCell(`
  function* gen() { yield 1; yield 2; }
  let g = gen(); // Iterator state is internal/suspended
  g.next(); // { value: 1, done: false }
  return { g }; // g's [[GeneratorState]] is internal slot
`);
// SOLUTION: Capture generator functions, not iterators
```

#### Destructuring Declarations
Destructuring creates multiple bindings that must all be captured.

```javascript
await repl.evaluateCell(`
  let [a, b, c] = [1, 2, 3];
  const { x, y: renamedY } = { x: 10, y: 20 };
  // Must capture: a, b, c, x, renamedY
`);
// extractDeclarations must parse: a, b, c, x, renamedY
// NOT y (the source property), NOT the patterns themselves
```

#### Class Expressions vs. Declarations
Class declarations create lexical bindings; class expressions don't.

```javascript
// Declaration—binding 'MyClass' is created
await repl.evaluateCell(`class MyClass {}`);
// Must capture: MyClass

// Expression—no binding created unless assigned
await repl.evaluateCell(`const C = class {};`);
// Must capture: C (the variable), not the anonymous class
```

#### Temporal Dead Zone (TDZ)
The TDZ per **§13.3.1** means `let`/`const` bindings exist but are uninitialized until their declaration statement executes. The IIFE pattern handles this correctly because each cell is a fresh function with its own TDZ semantics.

```javascript
// Within a single cell, TDZ is preserved:
await repl.evaluateCell(`
  // console.log(x); // Would throw ReferenceError (TDZ)
  let x = 1;
  console.log(x); // 1
  return { x };
`);
```

#### Nested Scopes and Closures
Bindings captured from inner scopes must be hoisted to the cell's return.

```javascript
await repl.evaluateCell(`
  let outer = 1;
  if (true) {
    let inner = 2; // 'inner' is block-scoped—must be explicitly returned
  }
  // inner is NOT accessible here
  return { outer }; // inner is lost unless captured inside block
`);
```

---

## 3. The with(scopeProxy) Pattern

### How It Works

The `with` statement (**§13.11**) adds an object to the front of the scope chain. Property lookups that fail in the `with` block's LexicalEnvironment fall through to the `with` object's properties.

```javascript
const scopeProxy = new Proxy({}, {
  get(target, prop, receiver) {
    if (prop in target) return target[prop];
    throw new ReferenceError(`${String(prop)} is not defined`);
  },
  set(target, prop, value) {
    target[prop] = value;
    return true;
  },
  has(target, prop) {
    return true; // Claim we have all properties (suppress strict errors)
  }
});

// Each cell executes inside with(scopeProxy)
with (scopeProxy) {
  let x = 1; // Actually creates on scopeProxy, not a true lexical binding
  const y = 2;
}
```

### Why It Was Deprecated

**ECMA-262 §B.3.5** (Annex B) marks `with` as forbidden in strict mode. The semantic problems are severe:

1. **Unpredictable scope chain**: Any property access might resolve to the `with` object or an outer scope—static analysis becomes impossible

2. **Performance deoptimization**: Engines cannot optimize variable lookup because `with` object's properties are dynamic

3. **Security hazard**: The `with` object can intercept *all* identifier lookups, including unexpected ones:

```javascript
const maliciousScope = new Proxy({}, {
  get(target, prop) {
    if (prop === 'fetch') return () => stealCredentials();
    return target[prop];
  }
});

with (maliciousScope) {
  fetch('/api/data'); // Intercepted! Calls malicious function
}
```

4. **TDZ and `let`/`const` incompatibility**: `with` creates an ObjectEnvironmentRecord, not a DeclarativeEnvironmentRecord. It cannot represent TDZ states or `const` immutability:

```javascript
with (scopeProxy) {
  const x = 1;
  x = 2; // Should throw TypeError, but Proxy set() may allow it
}
```

### Historical Implementation

```javascript
function createScopeProxy(scope) {
  return new Proxy(scope, {
    get(target, name) {
      if (name in target) return target[name];
      if (name in globalThis) return globalThis[name];
      throw new ReferenceError(`${name} is not defined`);
    },
    set(target, name, value) { target[name] = value; return true; },
    has() { return true; }, // Critical: prevents strict mode errors
    ownKeys(target) { return Reflect.ownKeys(target); }
  });
}

function evalWithScope(code, scopeProxy) {
  return eval(`with(scopeProxy) { ${code} }`);
}
```

**Why this fails for modern JS**: `let`/`const` inside `with` still create bindings in the `with` block's LexicalEnvironment, not on the proxy object. The proxy only catches *unresolved* identifiers. True lexical scoping cannot be emulated with `with`.

---

## 4. How Node.js Built-in REPL Handles This

Node.js uses **source-to-source transformation**—it rewrites your input before execution.

### Key Insight

Node doesn't try to preserve lexical environments. Instead, it **converts `let`/`const` to property assignments on a persistent context object** while preserving the *illusion* of lexical scoping.

Located in `lib/repl.js`, the Node REPL uses the internal `vm` module with a custom `eval` function that preprocesses input through `REPLServer.prototype.eval`.

### Conceptual Implementation

```javascript
// From Node.js lib/repl.js (conceptual)
function processCell(src, context) {
  // 1. Parse with acorn/espree to find declarations
  const ast = parse(src, { ecmaVersion: 'latest' });

  // 2. Rewrite let/const to var + context assignment
  let rewritten = src;
  const declared = [];
  walk(ast, {
    VariableDeclaration(node) {
      if (node.kind === 'let' || node.kind === 'const') {
        for (const decl of node.declarations) {
          const name = decl.id.name;
          declared.push(name);
          // Transform: let x = 1 → var x = (context.x = 1)
        }
      }
    }
  });

  // 3. Execute and update context
  const result = vm.runInContext(rewritten, context);
  Object.assign(context, result);
}
```

### Node's Actual Behavior

```javascript
// In actual Node REPL:
> let x = 1
undefined
> let x = 2  // Would be SyntaxError in script, works in REPL!
undefined
> x
2
// What Node actually executed (conceptually):
// Cell 1: context.x = 1
// Cell 2: context.x = 2 (transformed from "let x = 2")
```

Node's implementation is more sophisticated:
- It uses `vm.Script` with a persistent `context` object that serves as the global object for the REPL session
- **It intercepts declaration errors**: When you redeclare `let x` in a new cell, Node catches the syntax error and rewrites to an assignment instead
- **It handles the "redeclaration" problem**: In true JS, `let x; let x;` is a SyntaxError. Node REPL transforms the second to `x = ...` (assignment) if `x` already exists in the context.

---

## ECMA-262 Spec References (Summary)

| Section | Topic |
|---------|-------|
| §9.4 | Execution Context — LexicalEnvironment and VariableEnvironment |
| §9.1.1.2 | ObjectEnvironmentRecord (global object as environment) |
| §6.2.6 | DeclarativeEnvironmentRecord |
| §13.1.5 | var statement semantics |
| §13.3.1 | let/const Temporal Dead Zone |
| §13.11 | with statement semantics |
| §18.2.1.1 | PerformEval — how eval() creates its own environment |
| §B.3.5 (Annex B) | with statement forbidden in strict mode |
