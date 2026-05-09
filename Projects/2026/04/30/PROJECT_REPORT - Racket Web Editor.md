# Building a Racket Server and an Interactive Compiler Course

*A technical project report in textbook style*

## 1. What We Built

This project began with a simple request: build a browser-based Racket editor and REPL, then use it as the foundation for an interactive Chapter 2 course for *Essentials of Compilation*. The final system has two faces. The first is a general-purpose local Racket workbench where a learner can edit a full `#lang racket` file or evaluate snippets in a persistent REPL. The second is a focused compiler-course environment where a learner implements the Chapter 2 compiler passes and watches trees change as their code runs.

The important point is that this is not a static tutorial. The browser does not merely check strings or compare fill-in-the-blank answers. When the learner presses **Run tests in Racket**, the page sends a generated Racket file to a local Racket backend. The backend writes that file to disk, invokes the installed `racket` executable, captures stdout and stderr, and returns the result to the browser. The course page therefore has the same basic shape as a programming lab: read, edit, run, inspect, revise.

The repository now contains these major parts:

```text
.
├── server.rkt                         # Racket HTTP API and evaluators
├── README.md                          # Run instructions and book-aligned data definitions
├── PROJECT_REPORT.md                  # This report
├── web/
│   ├── package.json                   # React, Vite, CodeMirror dependencies
│   ├── vite.config.js                 # Dev server and /api proxy
│   ├── index.html                     # Vite entry point
│   └── src/
│       ├── main.jsx                   # React app, labs, harness generation, REPL UI
│       └── styles.css                 # Dark responsive layout and lab styling
└── ttmp/2026/04/30/RACKET-WEB-REPL--racket-web-editor-and-repl/
    ├── design-doc/...
    ├── reference/...
    └── scripts/01-smoke-test-api.sh
```

There are two browser routes:

```text
http://localhost:5173/#/chapter2   Chapter 2 compiler-pass labs
http://localhost:5173/#/repl        General Racket editor + persistent REPL
```

The Racket backend runs separately:

```text
http://localhost:8090
```

Vite runs the frontend on port `5173` and proxies `/api/*` requests to the backend.

## 2. The Central Design Idea

The central design idea is to let the browser be a teaching surface while Racket remains the execution authority. That distinction matters. A compiler course teaches transformations over programs. If the page fakes those transformations in JavaScript, then the learner is not really practicing the implementation language used in the book. If the page only embeds static examples, then the learner can read about compiler passes but cannot observe their own code changing a tree.

The system therefore separates responsibilities like this:

| Layer | Responsibility | What it deliberately does not do |
|---|---|---|
| React UI | Presents lessons, editors, lab controls, outputs, and navigation. | It does not evaluate Racket code. |
| CodeMirror | Provides the editing experience: highlighting, line numbers, bracket matching, and keyboard behavior. | It does not understand compiler-pass semantics. |
| Racket API server | Runs file evaluations and REPL evaluations, captures results, and returns JSON. | It does not render lessons or manage React state. |
| Generated lab harnesses | Wrap student pass code in tests or transform drivers. | They do not replace the student's implementation. |

This division gives us a useful teaching loop:

```text
┌──────────────┐       ┌──────────────────┐       ┌─────────────────────┐
│ Student code │  -->  │ Generated Racket │  -->  │ Local racket process │
│ in browser   │       │ harness          │       │ or REPL namespace    │
└──────────────┘       └──────────────────┘       └──────────┬──────────┘
                                                              │
┌──────────────┐       ┌──────────────────┐       ┌──────────▼──────────┐
│ Rendered UI  │  <--  │ JSON API result  │  <--  │ stdout/stderr/value │
│ feedback     │       │                  │       │ capture             │
└──────────────┘       └──────────────────┘       └─────────────────────┘
```

The learner sees friendly controls, but the evidence comes from a real Racket run.

## 3. The Backend: A Small Racket Evaluation Server

The backend lives in `server.rkt`. It uses Racket's `web-server` libraries directly. There is no Node server, no Express middleware, and no database. This is intentional. The backend has one job: receive JSON requests, run Racket code in the requested mode, and return structured JSON.

The server exposes four endpoints:

```text
GET  /api/health
POST /api/file/eval
POST /api/repl/eval
POST /api/repl/reset
```

The health endpoint is there for operational clarity. It answers the question, "Is the Racket backend actually running?" This matters because Vite's development server proxies `/api` requests. If the frontend is running but the Racket backend is down, requests to `http://localhost:5173/api/file/eval` will fail through the proxy. The fix is not in React; the fix is to start `racket server.rkt`.

### 3.1 JSON Responses

The backend uses one helper to produce JSON responses:

```racket
(define (json-response data #:status [status 200])
  (response/full
   status
   #"OK"
   (current-seconds)
   #"application/json; charset=utf-8"
   (list (header #"Access-Control-Allow-Origin" #"*")
         (header #"Access-Control-Allow-Methods" #"GET, POST, OPTIONS")
         (header #"Access-Control-Allow-Headers" #"content-type"))
   (list (jsexpr->bytes data))))
```

Every evaluator result has the same broad shape:

```json
{
  "ok": true,
  "output": "text printed to stdout",
  "errorOutput": "text printed to stderr or exception text",
  "values": ["values returned by REPL expressions"],
  "exitCode": 0
}
```

That shape is deliberately simple. The frontend can render the same kind of panel for file runs, REPL runs, lab checks, and transform visualizations.

### 3.2 File Evaluation

File evaluation is used for complete programs and for lab checkers. It is implemented by writing the submitted source code to a temporary file and invoking the installed `racket` executable:

```racket
(define (eval-file-code code timeout-seconds)
  (define tmp (make-temporary-file "racket-web-editor-~a.rkt"))
  (call-with-output-file tmp #:exists 'truncate
    (lambda (out) (display code out)))
  (define racket-bin (or (find-executable-path "racket") "racket"))
  (define-values (sp stdout stdin stderr)
    (subprocess #f #f #f racket-bin (path->string tmp)))
  ...)
```

This choice solves an important semantic problem. A complete Racket file usually begins with:

```racket
#lang racket
```

The `#lang` line is not an ordinary expression that should be handed to `eval`. It is part of Racket's module system. Running a temporary file with the `racket` executable gives the same behavior that the learner would get from the terminal:

```bash
racket some-file.rkt
```

The file evaluator also provides a clean boundary for lab execution. Every lab run becomes a fresh process. If the student's definitions mutate module-level state, that state disappears when the process exits. The server still runs local code and is not a sandbox, but the subprocess boundary is a useful practical boundary for a local teaching tool.

### 3.3 REPL Evaluation

The REPL endpoint has a different goal. A REPL should remember definitions. If the learner evaluates:

```racket
(define xs '(1 2 3 4))
```

then the next evaluation should be able to use `xs`:

```racket
(map sqr xs)
```

The server implements this by maintaining a hash table from session ids to namespaces:

```racket
(define sessions (make-hash))

(define (make-repl-namespace)
  (define ns (make-base-namespace))
  (parameterize ([current-namespace ns])
    (namespace-require 'racket)
    (namespace-require 'racket/pretty))
  ns)

(define (session-namespace session-id)
  (hash-ref! sessions session-id make-repl-namespace))
```

A namespace is the environment in which Racket resolves variable names and stores top-level definitions. The browser generates a session id with `crypto.randomUUID()`, and every REPL request sends that session id. The backend lazily creates a namespace the first time it sees the id.

This creates a useful contrast between the two evaluation modes:

| Mode | Implementation | Good for | State behavior |
|---|---|---|---|
| File evaluation | Temporary file + `racket` subprocess | Complete `#lang racket` programs and generated lab checkers. | Fresh process each run. |
| REPL evaluation | In-process evaluation in a session namespace. | Interactive snippets and persistent definitions. | Definitions persist until reset or server restart. |

The distinction is not accidental. It follows from the different mental models of "run this file" and "continue this conversation with the evaluator."

### 3.4 Timeouts

Both evaluators accept `timeoutSeconds`. The file evaluator waits for the subprocess with `sync/timeout` and kills it if it takes too long. The REPL evaluator runs the thunk in a custodian-managed thread and shuts the custodian down on timeout.

Timeouts are not security. They are a guardrail for ordinary mistakes such as infinite loops:

```racket
(let loop () (loop))
```

A real multi-user sandbox would need process isolation, filesystem restrictions, memory limits, network restrictions, and careful cleanup. This project is a local teaching tool, so the timeout is there to keep experiments from hanging the session, not to make untrusted code safe.

## 4. The Frontend: React as a Teaching Surface

The frontend is a Vite app in `web/`. It uses React for application state and CodeMirror 6 for editing. The page is not a typical form-based exercise site. It is closer to a small IDE embedded in a lesson.

The route structure is intentionally small:

```javascript
function App() {
  const [hash, setHash] = useState(window.location.hash || '#/chapter2');
  ...
  return hash === '#/repl' ? <RacketReplPage /> : <Chapter2Page />;
}
```

This hash-based routing avoids adding a router dependency. It is enough for the two modes we need: course and REPL.

### 4.1 CodeMirror Integration

The editor integration uses CodeMirror directly rather than a React wrapper. The hook creates an editor once, listens for document changes, and synchronizes external value changes back into the editor:

```javascript
function useCodeMirror({ value, onChange, ariaLabel, minHeight = 360 }) {
  const hostRef = useRef(null);
  const viewRef = useRef(null);

  const extensions = useMemo(() => [
    lineNumbers(),
    highlightActiveLineGutter(),
    history(),
    bracketMatching(),
    indentOnInput(),
    StreamLanguage.define(scheme),
    syntaxHighlighting(defaultHighlightStyle, { fallback: true }),
    highlightActiveLine(),
    keymap.of([indentWithTab, ...defaultKeymap, ...historyKeymap]),
    oneDark,
    EditorView.lineWrapping,
    EditorView.updateListener.of((update) => {
      if (update.docChanged) onChange(update.state.doc.toString());
    })
  ], [onChange, ariaLabel, minHeight]);
  ...
}
```

The language mode is CodeMirror's legacy Scheme mode. It is not a full Racket parser, but it gives useful syntax highlighting for the S-expression-heavy code used throughout the course. The most important editor affordances for these labs are not advanced semantic features. They are the simple things that make Lisp-like code tolerable to edit: line numbers, bracket matching, indentation, history, and a monospace dark theme.

### 4.2 The REPL Page

The REPL page keeps the original project goal alive. It has two editors:

- a file editor for complete `#lang racket` programs;
- a REPL input editor for snippets evaluated in a persistent namespace.

The file editor sends code to `/api/file/eval`. The REPL editor sends code to `/api/repl/eval`. Both show stdout, values or status, and stderr/errors. The learner can therefore use the system outside the course labs as a general Racket scratchpad.

This matters pedagogically. Compiler courses often require small experiments: trying a `match` pattern, checking a quasiquote, printing a transformed tree, or evaluating a helper function. Keeping the REPL page available gives the learner a side channel for exploration.

## 5. The Course Page: From Static Exercises to Pass Labs

The Chapter 2 page began as a fill-in-the-blank exercise layer. That was useful for checking concepts like lexical scope and stack homes, but it missed the deeper goal. In a compiler course, the essential activity is not selecting the right answer from a bank. The essential activity is implementing a transformation and then seeing whether the transformed program has the intended structure and meaning.

The course page now has seven implementation labs:

1. `uniquify-exp`
2. `remove-complex-operands`
3. `explicate-control`
4. `select-instructions`
5. `assign-homes`
6. `patch-instructions`
7. `prelude-and-conclusion`

Each lab has four pieces:

| Piece | Purpose |
|---|---|
| Starter code | Gives the shape of the pass and leaves meaningful TODOs. |
| Reveal code | Shows one working implementation. |
| Checker harness | Runs tests against the learner's current implementation. |
| Transform visualizer | Runs the learner's pass on custom input and pretty-prints the output tree. |

This structure creates two kinds of feedback. The checker answers, "Does my pass satisfy these invariants?" The visualizer answers, "What did my pass actually do to this tree?" Both are necessary. A pass can fail because it produces the wrong value, the wrong shape, the wrong names, or the wrong instruction sequence. Seeing the tree often makes the mistake visible before the test message does.

## 6. Aligning with *Essentials of Compilation*

The project aligns with Chapter 2 by using the same S-expression style that appears in the book's Racket track, especially the Figure 2.10 skeleton for `uniquify-exp`:

```racket
(define (uniquify-exp symtab)
  (lambda (e)
    (match e
      [(? symbol?) ___]
      [(? integer?) e]
      [`(let ([,x ,e]) ,body) ___]
      [`(,op ,es ...)
       `(,op ,@(for/list ([e es])
                 ((uniquify-exp symtab) e)))])))
```

The labs use compact teaching representations rather than importing the entire support library. That choice keeps the exercise readable in a browser. The representations are still book-aligned: they preserve the core categories and pass responsibilities.

### 6.1 LVar / R1 Expressions

The source language shape is:

```racket
(program info expression)

expression ::= integer
             | symbol
             | (let ([symbol expression]) expression)
             | (op expression ...)
```

A typical input for `uniquify` is:

```racket
(program ()
  (let ([x 32])
    (+ (let ([x 10]) x)
       x)))
```

The important feature here is shadowing. The same printed symbol `x` names two different bindings. After `uniquify`, each binding should have a globally unique name, and every use should point to the correct binding.

A correct transformation looks like this, ignoring the exact numeric suffix chosen by `gensym`:

```racket
(program ()
  (let ([x1147 32])
    (+ (let ([x1148 10]) x1148)
       x1147)))
```

The shape teaches the central invariant:

- The inner use of `x` becomes the inner unique name.
- The final outer use of `x` becomes the outer unique name.
- The right-hand side of a `let` is transformed in the old environment.
- The body of a `let` is transformed in the extended environment.

### 6.2 `remove-complex-operands`

The RCO lab asks the learner to ensure that primitive operands are atomic. In this course page, atomic means an integer or a symbol:

```racket
(define (atom? e)
  (or (integer? e) (symbol? e)))
```

The expression:

```racket
(+ 42 (- 10))
```

has one atomic operand, `42`, and one complex operand, `(- 10)`. RCO introduces a temporary binding:

```racket
(let ([tmp1146 (- 10)])
  (+ 42 tmp1146))
```

This pass prepares later instruction selection. x86-like instructions are simpler when their operands are already in a restricted form.

### 6.3 `explicate-control`

The `explicate-control` lab turns nested expression structure into a CVar-style block. A nested expression such as:

```racket
(let ([x.1 20])
  (let ([x.2 22])
    (+ x.1 x.2)))
```

becomes:

```racket
(program ()
  (start
    (assign x.1 20)
    (assign x.2 22)
    (return (+ x.1 x.2))))
```

This is the moment when the compiler stops thinking primarily in expressions and starts thinking in statements and tails. The pass makes evaluation order explicit. First assign `x.1`, then assign `x.2`, then return the final expression.

### 6.4 `select-instructions`

The `select-instructions` lab lowers CVar-style statements into x86-like instructions. For example:

```racket
(program ()
  (start
    (assign x (+ 10 32))
    (assign y (read))
    (return (+ x y))))
```

becomes:

```racket
((movq (Imm 10) (Var x))
 (addq (Imm 32) (Var x))
 (callq read_int)
 (movq (Reg rax) (Var y))
 (movq (Var x) (Reg rax))
 (addq (Var y) (Reg rax))
 (jmp conclusion))
```

The representation uses book-like argument categories:

```racket
(Imm n)          ; immediate integer
(Reg rax)        ; register
(Var x)          ; abstract variable before assign-homes
(Deref rbp -8)   ; stack home after assign-homes
```

The output is not printed assembly yet. It is structured instruction data, which later passes can inspect and rewrite.

### 6.5 `assign-homes`

Before register allocation is introduced, Chapter 2 places variables on the stack. The lab represents stack homes explicitly:

```racket
(program ((homes ((a (Deref rbp -8))
                  (b (Deref rbp -16)))))
  ((movq (Imm 42) (Var a))
   (movq (Var a) (Var b))
   (movq (Var b) (Reg rax))))
```

The pass replaces variables with homes:

```racket
((movq (Imm 42) (Deref rbp -8))
 (movq (Deref rbp -8) (Deref rbp -16))
 (movq (Deref rbp -16) (Reg rax)))
```

This output intentionally contains an invalid x86 pattern: a memory-to-memory move. That is not a bug in `assign-homes`; it is the reason the next pass exists.

### 6.6 `patch-instructions`

x86 does not allow many instructions to use two memory operands. The instruction:

```racket
(movq (Deref rbp -8) (Deref rbp -16))
```

must be rewritten through a register:

```racket
(movq (Deref rbp -8) (Reg rax))
(movq (Reg rax) (Deref rbp -16))
```

The patching lab makes this constraint concrete. It is a good example of a compiler pass that exists because the target language is less permissive than the intermediate language.

### 6.7 `prelude-and-conclusion`

The last Chapter 2 lab wraps an instruction body with function-entry and function-exit code. A small body:

```racket
(program ((stack-space 16))
  ((movq (Imm 42) (Reg rax))
   (jmp conclusion)))
```

becomes a complete instruction sequence:

```racket
((global main)
 (label main)
 (pushq (Reg rbp))
 (movq (Reg rsp) (Reg rbp))
 (subq (Imm 16) (Reg rsp))
 (jmp start)
 (label start)
 (movq (Imm 42) (Reg rax))
 (jmp conclusion)
 (label conclusion)
 (addq (Imm 16) (Reg rsp))
 (popq (Reg rbp))
 (retq))
```

This pass is a reminder that compiler output is not just the translation of the source expression. A real program needs a calling-convention boundary: set up the frame, run the body, restore the frame, and return.

## 7. Generated Harnesses: Tests as Executable Explanations

Each lab's checker is generated by combining three things:

1. a `#lang racket` header and required libraries;
2. the learner's current implementation;
3. a pass-specific harness containing examples and invariants.

For example, the `uniquify-exp` checker verifies that:

- the original sample evaluates to `42`;
- the transformed sample also evaluates to `42`;
- every binder is globally unique;
- the inner use points to the inner binder;
- the final outer use points to the outer binder;
- the right-hand side of an inner `let` is transformed in the old environment.

The harnesses are not merely answer keys. They encode the contract of the pass. In a compiler, the output of a pass is both a program and a promise to the next pass. RCO promises atomic primitive operands. Assign-homes promises that variables have become concrete homes. Patch-instructions promises that no memory-to-memory instructions remain. These promises are exactly what the checkers test.

## 8. Transform Visualization: Seeing the Pass Work

The most recent addition is the transform panel. It exists because test results alone are too indirect for learning compiler passes. A test can say "expected all primitive operands to be atomic," but the learner still needs to see the malformed tree that their code produced.

The transform panel lets the learner enter a datum such as:

```racket
(+ (+ 1 2) (+ 3 4))
```

and run the current `remove-complex-operands` implementation. With the reveal solution, the output is a nested set of temporary bindings whose exact names come from `gensym`:

```racket
(let ((tmp... (+ 1 2)))
  (let ((tmp... (+ 3 4)))
    (+ tmp... tmp...)))
```

The mechanism is small. The frontend builds a temporary Racket program that reads the custom input with `read`, applies the current lab's transform expression, and prints the result with `pretty-write`:

```javascript
function buildTransformHarness(userCode, lab, inputText) {
  return `#lang racket
(require racket/match racket/dict racket/set racket/pretty)

${userCode}

(define input
  (with-input-from-string ${JSON.stringify(inputText)} read))

(define output
  ${lab.transformExpr.replaceAll('\\`', '`')})

(pretty-write output)
`;
}
```

This is a useful pattern: the UI does not need to understand each pass deeply. The lab definition supplies the transform expression, such as `(uniquify input)` or `(patch-instructions input)`. The server runs the generated file and returns the printed tree.

The result is a course page where a learner can ask not only "Did I pass?" but "What did my compiler just do?"

## 9. A Walk Through the System

Suppose the learner opens `/#/chapter2`, selects `patch-instructions`, clicks **Reveal**, and then clicks **Run transform**. The sequence is:

1. React reads the selected lab definition from `PASS_LABS`.
2. The current editor contents become `userCode`.
3. The custom input editor contents become `inputText`.
4. `buildTransformHarness` creates a complete Racket program.
5. `postJson` sends that program to `/api/file/eval`.
6. Vite proxies the request from port `5173` to `localhost:8090`.
7. `server.rkt` receives the JSON body.
8. `eval-file-code` writes the generated program to a temporary `.rkt` file.
9. The backend invokes `racket temporary-file.rkt`.
10. Racket prints the transformed instruction list.
11. The backend captures stdout, stderr, and the exit code.
12. React displays the pretty-printed tree in the output panel.

That path is worth understanding because it explains many common failures. If the frontend is up but the backend is down, the proxy fails. If the generated Racket code has a syntax error, the backend returns `ok: false` with stderr. If the pass produces the wrong tree, the checker raises a lab-specific error. Each failure happens at a different layer, and the UI is designed to show enough evidence to locate it.

## 10. Validation

The project was validated in three ways.

First, the Racket backend was compiled:

```bash
raco make server.rkt
```

Second, the frontend production build was run:

```bash
cd web
pnpm build
```

Third, browser-level tests were performed with Playwright. With both servers running, each lab was selected, the reveal implementation was loaded, the checker was run, and the transform visualizer was exercised. The expected success messages were observed:

```text
✓ All uniquify-exp tests passed in real Racket.
✓ remove-complex-operands tests passed in real Racket.
✓ explicate-control tests passed in real Racket.
✓ select-instructions tests passed in real Racket.
✓ assign-homes tests passed in real Racket.
✓ patch-instructions tests passed in real Racket.
✓ prelude-and-conclusion tests passed in real Racket.
```

The REPL route was also checked by running the factorial file example and evaluating:

```racket
(define xs '(1 2 3 4))
(map sqr xs)
```

which produced:

```racket
(1 4 9 16)
```

## 11. What This Project Teaches

The project teaches at two levels. At the surface level, it teaches Chapter 2 compiler passes. Underneath, it teaches how to build an interactive programming course without reducing programming to a multiple-choice exercise.

The key lessons are:

- A browser can be a good teaching surface without becoming the execution engine. Keeping Racket in charge of Racket code preserves the learner's mental model.
- Compiler passes become easier to understand when learners can see input and output trees side by side. The tree is the evidence.
- Tests and visualizations answer different questions. Tests state whether invariants hold; visualizations show what transformation occurred.
- A small backend can be enough if its responsibilities are sharp. This server receives code, runs it, captures results, and returns JSON.
- File execution and REPL execution are different tools. File execution respects `#lang` and gives fresh runs; REPL execution preserves definitions in a namespace.
- Book-aligned representations matter. The closer the data shape is to the text, the less translation the learner has to do before thinking about the compiler idea.

## 12. Limitations and Future Work

The current lab representations are book-aligned but simplified. They are designed for teaching in a browser, not for replacing the full support-code environment from the book. A future version could move closer to the book's complete data definitions and testing framework.

Good next steps include:

- Add a preset gallery for each pass so learners can try several examples without typing them.
- Add a full-pipeline mode that feeds the output of one pass into the next.
- Add structural diff views so changes between input and output are highlighted.
- Add per-test rendered explanations instead of only stdout/stderr.
- Add export/import for lab attempts.
- Add a production mode where Racket serves the built `web/dist` files directly.
- Add stronger process isolation if the tool ever needs to run code from untrusted users.

## 13. Closing

The finished system is small, but it has the shape of a real interactive textbook. It introduces an idea, gives the learner a working skeleton, runs their code in the language being taught, and shows the resulting program tree. That loop is the heart of compiler education. A compiler pass is not a definition to memorize; it is a transformation to perform, inspect, and refine.

The Racket server supplies the execution ground truth. The React interface supplies the learning surface. CodeMirror supplies the editing feel. The generated harnesses connect the lesson to real checks. Together they turn Chapter 2 from a sequence of descriptions into a set of experiments the learner can run.
