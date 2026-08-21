# Cobra Design Patterns

- URL: https://chatgpt.com/c/6a824dd7-5f94-83ea-924a-061fdca24451
- Created: 2026-08-16T23:55:06.029Z

---

> Read [https://parc.yolo.scapegoat.dev/note/research/playbooks/creating-an-index](https://parc.yolo.scapegoat.dev/note/research/playbooks/creating-an-index) and [https://parc.yolo.scapegoat.dev/note/research/playbooks/creating-github-issues-and-software-design-garden-entries](https://parc.yolo.scapegoat.dev/note/research/playbooks/creating-github-issues-and-software-design-garden-entries) and garden entries like [https://parc.yolo.scapegoat.dev/note/research/software-architecture-garden/sessionstream/readme](https://parc.yolo.scapegoat.dev/note/research/software-architecture-garden/sessionstream/readme) (you can add .md at the end to get the md). Then study https\://github.com/spf13/cobra and create a design software garden set of design patterns that can be learned and reused from cobra.

I’ll first extract the garden/index conventions from the three PARC notes, then inspect Cobra’s source and history through GitHub. I’ll use those conventions to build a reusable pattern set rather than a generic repository summary.

```json
{"open":[{"ref_id":"https://parc.yolo.scapegoat.dev/note/research/playbooks/creating-an-index.md"},{"ref_id":"https://parc.yolo.scapegoat.dev/note/research/playbooks/creating-github-issues-and-software-design-garden-entries.md"},{"ref_id":"https://parc.yolo.scapegoat.dev/note/research/software-architecture-garden/sessionstream/readme.md"}],"response_length":"long"}
```

```json
{"paths":["GitHub"],"query":"fetch"}
```

<details><summary>💭 Thinking</summary>

**Searching parc.yolo.scapegoat.dev**

</details>

```python3
{"path":"/GitHub/link_694554034b848191ab0db5a14b130105/fetch","args":{"url":"https://github.com/spf13/cobra"}}
```

<details><summary>💭 Thinking</summary>

**Analyzing Cobra’s architecture**

I’m examining Cobra’s source to identify recurring design patterns, especially command-tree composition, lifecycle hooks, inherited flags, completion protocols, templated help, validation, dependency injection, and extensibility mechanisms.

**Analyzed Cobra's architecture**

**Fetched Cobra repository metadata, commit SHA, and file trees**

</details>

```json
{"open":[{"ref_id":"turn696260view2","lineno":198},{"ref_id":"turn696260view1","lineno":333},{"ref_id":"turn696260view1","lineno":380},{"ref_id":"turn696260view1","lineno":500},{"ref_id":"turn696260view1","lineno":600},{"ref_id":"turn696260view1","lineno":900}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Searched 1 website**

</details>

The playbooks make the target stricter than “interesting Cobra tricks”: each entry needs an invariant, at least two concrete implementation facts, explicit non-guarantees, and honest maturity. I’m narrowing candidates now to patterns Cobra actually enforces in code/tests, then I’ll assemble the project study plus index/rationale around them.

```json
{"paths":["GitHub"],"query":"search"}
```

```python3
{"path":"/GitHub/link_694554034b848191ab0db5a14b130105/search","args":{"query":"findAndTraverse execute PersistentPreRunE PersistentPostRunE","repository_name":"spf13/cobra","topn":10}}
```

```json
{"uri":"/response/turn16","query":"PersistentPreRun"}
```

```json
{"uri":"/response/turn16","query":"InheritedFlags"}
```

<details><summary>💭 Thinking</summary>

**Mapping Cobra patterns**

I’m organizing the source and tests into reusable patterns, beginning with the command tree as a shared model and hierarchical inheritance for flags, output, templates, and configuration.

**Mapped Cobra patterns**

</details>

```python3
{"path":"/GitHub/link_694554034b848191ab0db5a14b130105/fetch","args":{"url":"https://api.github.com/repos/spf13/cobra/contents?ref=adbc8813901bba65827259daa8e22ff94ec1f30e"}}
```

```json
{"uri":"/response/turn19","query":"flag_groups"}
```

<details><summary>💭 Thinking</summary>

**Organizing the study**

I’m turning Cobra’s implementation evidence into reusable design-garden entries, emphasizing invariant-based pattern names, applicability, tradeoffs, tests, and links between durable notes and repository issues.

**Extracting Cobra patterns**

I’m grounding each candidate in Cobra’s command model, execution pipeline, routing, flag scoping, default initialization, tests, and shell completion. I’m also noting negative space, especially where hooks do not guarantee cleanup.

**Organized the study**

**Inspected Cobra architecture, lifecycle, flags, completion, tests, and documented patterns**

</details>

The strongest Cobra lesson is emerging as **one mutable command graph serving as the semantic authority for dispatch, help, completion, validation, and generated docs**. Several smaller patterns fall out of how Cobra preserves or deliberately relaxes that authority at boundaries.

```json
{"open":[{"ref_id":"https://parc.yolo.scapegoat.dev/note/research/playbooks/creating-an-index"},{"ref_id":"https://parc.yolo.scapegoat.dev/note/research/playbooks/creating-an-index.md"},{"ref_id":"https://parc.yolo.scapegoat.dev/note/research/software-architecture-garden/sessionstream/index-of-design-patterns.md"},{"ref_id":"https://parc.yolo.scapegoat.dev/note/research/software-architecture-garden/sessionstream/index-of-design-patterns-rationale.md"}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Searched 1 website**

</details>

```python3
{"path":"/GitHub/link_694554034b848191ab0db5a14b130105/fetch_file","args":{"repository_full_name":"spf13/cobra","path":"flag_groups.go","ref":"adbc8813901bba65827259daa8e22ff94ec1f30e","start_line":1,"end_line":360}}
```

<details><summary>💭 Thinking</summary>

**Fetched Cobra Flag Group and SessionStream documentation and design patterns**

</details>

```python3
{"path":"/GitHub/link_694554034b848191ab0db5a14b130105/fetch_file","args":{"repository_full_name":"spf13/cobra","path":"flag_groups_test.go","ref":"adbc8813901bba65827259daa8e22ff94ec1f30e","start_line":1,"end_line":330}}
```

```json
{"uri":"/response/turn26","query":"FlagGroups"}
```

```json
{"uri":"/response/turn26","query":"MutuallyExclusive"}
```

<details><summary>💭 Thinking</summary>

**Inspected Cobra completion tests and command architecture**

</details>

```python3
{"path":"/GitHub/link_694554034b848191ab0db5a14b130105/search_branches","args":{"owner":"go-go-golems","repo_name":"go-go-parc","query":"architecture-garden/cobra","page_size":20}}
```

```python3
{"path":"/GitHub/link_694554034b848191ab0db5a14b130105/create_branch","args":{"repository_full_name":"go-go-golems/go-go-parc","branch_name":"architecture-garden/cobra-design-patterns","sha":"d0a050247e79b6b54ff0b91e0346bb3c6380acca"}}
```

The source evidence is sufficient. I’ve pinned Cobra at commit `adbc8813901bba65827259daa8e22ff94ec1f30e`; the Garden work is now isolated on `architecture-garden/cobra-design-patterns`.

```python3
{"path":"/GitHub/link_694554034b848191ab0db5a14b130105/create_file","args":{"repository_full_name":"go-go-golems/go-go-parc","branch":"architecture-garden/cobra-design-patterns","path":"Research/Software Architecture Garden/cobra/README.md","message":"docs(garden): add Cobra architecture study","content":"---\ntitle: Architecture Garden — Cobra\naliases:\n  - Cobra architecture study\n  - Cobra reusable CLI design patterns\nstatus: active\ntype: architecture-garden-project\ncreated: 2026-08-16\nanalyzed: 2026-08-16\nanalysis_schema: architecture-garden-v1\nrepository: https://github.com/spf13/cobra\nrepository_remote: https://github.com/spf13/cobra.git\nrepository_commit: adbc8813901bba65827259daa8e22ff94ec1f30e\nrepository_branch: main\nrepository_commit_date: 2026-
```

<details><summary>💭 Thinking</summary>

**Reviewing project conventions**

I’m organizing the repository guidance around pattern-study structure, maturity vocabulary, evidence quality, and index design. I’m also noting that the second playbook’s exact source remains incomplete, so I’ll avoid overstating its contents.

**Planning repository updates**

I’m identifying the remaining work: inspect the second playbook, verify current branch files, create focused pattern studies plus indexes and rationale, then update the garden README while matching established conventions.

**Reviewed project conventions and planned repository updates**

</details>

```python3
{"path":"/GitHub/link_694554034b848191ab0db5a14b130105/fetch_file","args":{"repository_full_name":"go-go-golems/go-go-parc","path":"Research/playbooks/creating-github-issues-and-software-design-garden-entries.md","ref":"d0a050247e79b6b54ff0b91e0346bb3c6380acca","start_line":1,"end_line":500}}
```

```json
{"uri":"/response/turn31","query":"repository issue"}
```

```json
{"uri":"/response/turn31","query":"## 8."}
```

<details><summary>💭 Thinking</summary>

**Created Cobra architecture study files and designed a software architecture garden set**

</details>

The second playbook confirms the important distinction: Garden notes are durable evidence artifacts; repository issues are maintainer-facing proposals. Since this task is an observational study of upstream Cobra rather than a request to change Cobra, I’m not going to spam the upstream project with pattern issues; the Garden artifacts will preserve the evidence and reuse guidance.

```python3
{"path":"/GitHub/link_694554034b848191ab0db5a14b130105/create_file","args":{"repository_full_name":"go-go-golems/go-go-parc","branch":"architecture-garden/cobra-design-patterns","path":"Research/Software Architecture Garden/cobra/01 - Command Graph as Semantic Authority.md","message":"docs(garden): add Cobra command graph pattern","content":"---\ntitle: Command Graph as Semantic Authority\naliases:\n  - Cobra semantic command graph\n  - One command model, many interpreters\nstatus: established\ntype: architecture-garden-design\ncreated: 2026-08-16\nanalyzed: 2026-08-16\nrepository: https://github.com/spf13/cobra\nrepository_remote: https://github.com/spf13/cobra.git\nrepository_commit: adbc8813901bba65827259daa8e22ff94ec
```

<details><summary>💭 Thinking</summary>

**Created and documented Cobra architecture garden patterns**

</details>

The first three entries now cover the core structure: one semantic graph, nearest-scope inheritance, and the ordered execution lifecycle. The execution study also records the key non-guarantee that `PostRun*` is not a `finally` boundary.

```python3
{"path":"/GitHub/link_694554034b848191ab0db5a14b130105/create_file","args":{"repository_full_name":"go-go-golems/go-go-parc","branch":"architecture-garden/cobra-design-patterns","path":"Research/Software Architecture Garden/cobra/04 - Late Defaults with User Override.md","message":"docs(garden): add Cobra late defaults pattern","content":"---\ntitle: Late Defaults with User Override\naliases:\n  - Cobra synthesized defaults\n  - Late-bound framework convenience\nstatus: established\ntype: architecture-garden-design\ncreated: 2026-08-16\nanalyzed: 2026-08-16\nrepository: https://github.com/spf13/cobra\nrepository_remote: https://github.com/spf13/cobra.git\nrepository_commit: adbc8813901bba65827259daa8e22ff94ec1f30e\ntags:\n  - architecture-garden\n 
```

<details><summary>💭 Thinking</summary>

**Documented Cobra defaults, constraint metadata, and hidden protocol commands**

</details>

```python3
{"path":"/GitHub/link_694554034b848191ab0db5a14b130105/create_file","args":{"repository_full_name":"go-go-golems/go-go-parc","branch":"architecture-garden/cobra-design-patterns","path":"Research/Software Architecture Garden/cobra/07 - Injectable Process Boundaries for Deterministic Tests.md","message":"docs(garden): add Cobra injectable boundaries pattern","content":"---\ntitle: Injectable Process Boundaries for Deterministic Tests\naliases:\n  - Cobra in-process execution harness\n  - Injectable CLI process boundary\nstatus: established\ntype: architecture-garden-design\ncreated: 2026-08-16\nanalyzed: 2026-08-16\nrepository: https://github.com/spf13/cobra\nrepository_remote: https://github.com/spf13
```

<details><summary>💭 Thinking</summary>

**Created Cobra patterns documentation, index, rationale, and PR**

</details>

```python3
{"path":"/GitHub/link_694554034b848191ab0db5a14b130105/fetch_file","args":{"repository_full_name":"go-go-golems/go-go-parc","path":"Research/Software Architecture Garden/README.md","ref":"architecture-garden/cobra-design-patterns","start_line":1,"end_line":260}}
```

```json
{"uri":"/response/turn42","start_line":3,"num_lines":5}
```

```json
{"uri":"/response/turn43","start_line":3,"num_lines":10}
```

```json
{"uri":"/response/turn42","start_line":1,"num_lines":400}
```

<details><summary>💭 Thinking</summary>

**Fetched README data, verified Cobra patterns, and opened study PR**

</details>

Created the Cobra Software Architecture Garden study and opened **go-go-parc PR #2**. It contains **11 new files / 1,581 lines**: the project study, eight focused pattern entries, the back-of-book index, and its rationale. fileciteturn45file0L2-L2 fileciteturn46file0L2-L35

The set follows the PARC discipline: invariant-first naming, concrete implementation/test evidence, explicit failure modes and non-guarantees, honest maturity, and an index organized by reader-memory vocabulary rather than source-string concordance. fileciteturn31file0L2-L2 The index/rationale structure also follows the existing sessionstream model. fileciteturn23file0L2-L2 fileciteturn24file0L2-L2

The eight reusable patterns are:

1. **Command Graph as Semantic Authority** — one command tree drives routing, help, completion, validation scope, and generated documentation.
2. **Hierarchical Policy Inheritance with Local Shadowing** — ancestor policy flows downward while children retain explicit override/provenance.
3. **Staged Command Execution Pipeline** — routing → parsing → argument validation → hooks → flag validation → effect.
4. **Late Defaults with User Override** — framework help/version/completion conveniences are fallback implementations, installed only when necessary.
5. **Constraint Metadata Drives Validation and Completion** — required-together, one-required, and mutually-exclusive relationships are annotations interpreted both by runtime validation and completion. Cobra's implementation explicitly uses the same metadata for both paths. fileciteturn20file0L2-L2
6. **Hidden Protocol Commands for Interactive Tooling** — `__complete` turns the executable into a query endpoint over its live semantic model; Cobra's completion tests exercise routing, visibility, traversal, flags, arguments, and directives. fileciteturn26file0L2-L2
7. **Injectable Process Boundaries for Deterministic Tests** — argv, context, stdin/stdout/stderr can be caller-controlled so the production executor runs in-process under tests.
8. **Generate Documentation from the Runtime Model** — reference documentation is another interpreter over the executable command schema rather than a separately maintained catalog.

I also preserved the less flattering architecture lessons. In particular, `PostRun*` is **not** a guaranteed cleanup/finally boundary; Cobra has several process-global behavior/extension variables and registries; and the command model is deliberately mutable. The process-global surface is visible directly in Cobra's switches, template-function registry, and initializer/finalizer lists. fileciteturn27file0L2-L2

I did **not** create upstream `spf13/cobra` issues. The PARC issue playbook distinguishes the durable Garden artifact from a maintainer-facing proposal; this task discovered reusable architecture but did not propose a Cobra implementation change, so opening upstream issues would add noise rather than actionable work. fileciteturn31file1

**PR:** `go-go-golems/go-go-parc#2` — “Add Cobra Software Architecture Garden study.” fileciteturn46file0L2-L13


---

> ouput as markdown and pdfd, focus on CS and maths structures,

> Use the material you gathered, but rewrite and restructure it so it actually turns into a real pedagogical textbook.
>
> Let’s try again, more structured and pedagogical: 4 big chapters, and after writing the first draft, go back and make sure each definition and term worth defining or introducing is properly motivated and defined and then applied in a few examples. Pretend you are a student reading the text and trying to make sense of it, and then rewrite it.
>
> Make sure to introduce concepts by motivation, definition, then concrete worked examples, then exercises, and potentially counterexample. Use full prose paragraphs and lists and pseudocode and maths and api signatures and diagrams. Use callouts for expanding on fundamentals or side topics.
>
> ouput as markdown and pdfd, focus on CS and maths structures,

```unknown
bash -lc cat /home/oai/skills/pdfs/SKILL.md
```

I’ll rebuild the Cobra material as a four-chapter CS/mathematics textbook, then audit definitions, examples, counterexamples, exercises, and cross-chapter consistency before rendering Markdown and PDF.

<details><summary>💭 Thinking</summary>

**Structuring textbook content**

I’m outlining a four-chapter textbook on executable command languages, combining motivations, formal definitions, examples, counterexamples, pseudocode, mathematical structures, diagrams, APIs, and exercises with solutions or hints.

**Structured textbook content**

**Refining chapter four**

I’m developing the final chapter around lifecycle correctness, context propagation, reflection, constraints, completion, documentation, and testing. I’m keeping exactly four main chapters, with optional glossary and solution appendices.

**Refined chapter four**

</details>

```unknown
bash -lc command -v dot || true; command -v pandoc || true; command -v xelatex || true; command -v git || true
```

<details><summary>💭 Thinking</summary>

**Reviewed PDF guidelines, conversion tools, and Cobra design sources**

**Designing the PDF**

I’m planning a polished PDF workflow with local mathematical rendering, structured metadata, numbered chapters, equations, code, diagrams, typography, navigation, and reliable pagination, while avoiding fragile dependencies where possible.

**Designed the PDF**

**Fetched Cobra architecture files, research, validation sources, and runtime documentation designs**

</details>

```unknown
bash -lc set -e
OUT=/mnt/data/cobra_textbook
rm -rf "$OUT"
mkdir -p "$OUT/figures" "$OUT/_build" "$OUT/_renders"
cat > "$OUT/figures/ch1-command-tree.dot" <<'DOT'
digraph G {
  graph [rankdir=TB, bgcolor="transparent", pad=0.2, nodesep=0.45, ranksep=0.55];
  node [shape=box, style="rounded", fontname="DejaVu Sans", fontsize=12, margin="0.12,0.08"];
  edge [fontname="DejaVu Sans", fontsize=10];
  forge [label="forge\n(root)"];
  repo [label="repo"];
  issue [label="issue"];
  clone [label="clone"];
  list [label="list"];
  create [label="create"];
  close [label="close"];
  forge -> repo;
  forge -> issue;
  repo -> clone;
  repo -> list;
  issue -> create;
  issue -> close;
  argv [shape=note, label="argv:\nforge repo clone --depth 1 URL"];
  route [shape=ellipse, label="route_T"];
  target [shape=note, label="target = clone\nresidual = --depth 1 URL"];
  argv -> route;
  route -> target;
  route -> clone [style=dashed, label="selects"];
}
DOT
cat > "$OUT/figures/ch2-scope-resolution.dot" <<'DOT'
digraph G {
  graph [rankdir=LR, bgcolor="transparent", pad=0.2, nodesep=0.5, ranksep=0.5];
  node [shape=box, style="rounded", fontname="DejaVu Sans", fontsize=11, margin="0.12,0.08"];
  root [label="forge\nP(root) = {config, verbose}\nout = buffer"];
  repo [label="repo\nP(repo) = {host}\nL(repo) = {verbose}"];
  clone [label="clone\nL(clone) = {depth}"];
  root -> repo [label="parent"];
  repo -> clone [label="parent"];
  effective [shape=note, label="Effective at clone\nconfig (root)\nhost (repo)\nverbose (repo shadows root)\ndepth (clone)\nout (root fallback)"];
  clone -> effective [label="resolve nearest"];
}
DOT
cat > "$OUT/figures/ch3-execution-machine.dot" <<'DOT'
digraph G {
  graph [rankdir=LR, bgcolor="transparent", pad=0.15, nodesep=0.35, ranksep=0.4];
  node [shape=box, style="rounded", fontname="DejaVu Sans", fontsize=10.5, margin="0.10,0.07"];
  edge [fontname="DejaVu Sans", fontsize=9];
  s0 [label="Route"];
  s1 [label="Parse flags"];
  s2 [label="Validate args"];
  s3 [label="Persistent/local\npre-hooks"];
  s4 [label="Validate required\nand grouped flags"];
  s5 [label="Run / RunE\n(effect boundary)"];
  s6 [label="Local/persistent\npost-hooks"];
  ok [shape=doublecircle, label="success"];
  err [shape=octagon, label="error"];
  s0 -> s1 -> s2 -> s3 -> s4 -> s5 -> s6 -> ok;
  s0 -> err [label="not found", style=dashed];
  s1 -> err [label="parse", style=dashed];
  s2 -> err [label="args", style=dashed];
  s3 -> err [label="pre", style=dashed];
  s4 -> err [label="flags", style=dashed];
  s5 -> err [label="RunE", style=dashed];
  note [shape=note, label="PostRun* is not finally:\nan error at RunE skips s6"];
  err -> note [style=dotted];
}
DOT
cat > "$OUT/figures/ch4-multiple-interpreters.dot" <<'DOT'
digraph G {
  graph [rankdir=LR, bgcolor="transparent", pad=0.2, nodesep=0.4, ranksep=0.45];
  node [shape=box, style="rounded", fontname="DejaVu Sans", fontsize=11, margin="0.12,0.08"];
  model [shape=folder, label="Semantic command model\n(tree + flags + metadata + hooks)"];
  exec [label="Execution interpreter\nargv -> effects/results"];
  help [label="Help interpreter\nmodel -> prose"];
  comp [label="Completion interpreter\npartial argv -> candidates"];
  docs [label="Documentation interpreter\nmodel -> Markdown/man/reST"];
  test [label="Test harness\ninjected argv/context/I/O"];
  model -> exec;
  model -> help;
  model -> comp;
  model -> docs;
  test -> exec [label="same executor"];
  constraints [shape=note, label="constraint annotations"];
  constraints -> model;
  constraints -> comp [style=dashed, label="guide"];
  constraints -> exec [style=dashed, label="reject"];
}
DOT
for f in "$OUT"/figures/*.dot; do
  dot -Tpng -Gdpi=180 "$f" -o "${f%.dot}.png"
done
ls -lh "$OUT/figures"/*.png
```

<details><summary>💭 Thinking</summary>

**Planning the textbook**

I’m organizing the book around a running CLI example, formal models, motivations, definitions, worked examples, counterexamples, exercises, and solution sketches. I’m targeting a substantial but manageable manuscript delivered as Markdown and PDF.

**Planned the textbook**

</details>

The mathematical progression is fixed: command trees as schemas, scoped environments, execution transition systems, then multiple interpreters for annotations, completion protocols, tests, and generated documentation.

```unknown
bash -lc cat > /mnt/data/cobra_textbook/Executable_Command_Languages.md <<'EOF'
---
title: "Executable Command Languages"
subtitle: "Computer Science and Mathematical Structures in Cobra"
author: "An evidence-backed textbook derived from spf13/cobra"
date: "August 2026"
lang: en-US
documentclass: book
papersize: letter
fontsize: 10pt
geometry:
  - margin=0.9in
numbersections: true
toc: true
toc-depth: 3
linkcolor: blue
urlcolor: blue
colorlinks: true
header-includes:
  - |
    \usepackage{amsmath,amssymb,mathtools}
    \usepackage{booktabs,longtable,array}
    \usepackage{graphicx}
    \usepackage{xcolor}
    \usepackage{fancyhdr}
    \usepackage{microtype}
    \usepackage{enumitem}
    \usepackage{tcolorbox}
    \usepackage{titlesec}
    \definecolor{CalloutBack}{HTML}{F3F5F7}
    \definecolor{CalloutRule}{HTML}{6B7280}
    \renewenvironment{quote}{\begin{tcolorbox}[colback=CalloutBack,colframe=CalloutRule,boxrule=0.5pt,arc=1mm,left=2mm,right=2mm,top=1mm,bottom=1mm]}{\end{tcolorbox}}
    \pagestyle{fancy}
    \fancyhf{}
    \fancyhead[LE,RO]{\small Executable Command Languages}
    \fancyhead[RE,LO]{\small\leftmark}
    \fancyfoot[C]{\thepage}
    \setlength{\headheight}{14pt}
    \setlist{nosep}
    \setcounter{secnumdepth}{3}
---

\frontmatter

# Preface {-}

A mature command-line program is a small language implementation. It has syntax, names, scope, inheritance, static checks, dynamic effects, error behavior, documentation, and interactive tooling. The superficial view says that a CLI framework maps strings to callbacks. The more useful view says that it defines an executable language whose abstract syntax is a command tree and whose interpreters include execution, help, completion, validation, testing, and documentation.

This book develops that view through the architecture of [Cobra](https://github.com/spf13/cobra), a widely used Go library for hierarchical command-line interfaces. The analysis is pinned to Cobra commit `adbc8813901bba65827259daa8e22ff94ec1f30e`. The goal is not to teach every method in Cobra's public API. The goal is to extract reusable computer-science structures: rooted trees, partial functions, scoped environments, left-biased map composition, small-step operational semantics, Boolean constraint systems, multiple interpreters, protocol design, and recursive document generation.

The source material began as an Architecture Garden study. This edition has been rewritten as a textbook. Concepts are introduced in a deliberate order:

1. **motivation** - the engineering pressure that makes the idea necessary;
2. **definition** - a precise mathematical or computational object;
3. **worked examples** - concrete traces through a running CLI;
4. **counterexamples** - designs that look similar but violate the intended law;
5. **exercises** - problems that require reconstruction rather than recognition.

The recurring example is a fictional command-line tool named `forge`:

```text
forge
├── repo
│   ├── clone
│   └── list
└── issue
    ├── create
    └── close
```

It is small enough to trace by hand and large enough to exhibit hierarchy, inherited flags, aliases, validation, completion, documentation, and effectful execution.

> **Reader orientation.** You do not need prior knowledge of Cobra. Familiarity with basic Go syntax helps, but every framework-specific API used in an argument is introduced before it matters. Mathematical notation is used to compress reasoning, not to replace prose.

## Learning objectives {-}

By the end of the book, you should be able to:

- model a hierarchical CLI as a rooted labeled tree and define routing as a partial function over token sequences;
- distinguish command syntax, residual arguments, validation, and effects;
- derive effective configuration from local and inherited scopes using left-biased map composition;
- explain why local, inherited, and effective views are different and useful;
- model command execution as an ordered transition system with explicit admission and effect boundaries;
- reason about hook order, error short-circuiting, and the difference between a post-hook and guaranteed cleanup;
- encode cross-flag laws as Boolean constraints and interpret the same metadata for rejection and guidance;
- understand completion as analysis of a partial program rather than execution of a complete one;
- generate help and documentation as interpreters over one semantic model;
- design deterministic in-process tests by injecting arguments, context, and streams.

## The evidence base {-}

The principal source files are:

- [`command.go`](https://github.com/spf13/cobra/blob/adbc8813901bba65827259daa8e22ff94ec1f30e/command.go), which defines the command model, topology, routing, inheritance, lifecycle, and execution;
- [`args.go`](https://github.com/spf13/cobra/blob/adbc8813901bba65827259daa8e22ff94ec1f30e/args.go), which defines composable positional-argument validators;
- [`flag_groups.go`](https://github.com/spf13/cobra/blob/adbc8813901bba65827259daa8e22ff94ec1f30e/flag_groups.go), which defines cross-flag metadata and its validation/completion interpretations;
- [`completions.go`](https://github.com/spf13/cobra/blob/adbc8813901bba65827259daa8e22ff94ec1f30e/completions.go), which implements the hidden completion protocol and partial-input analysis;
- [`doc/md_docs.go`](https://github.com/spf13/cobra/blob/adbc8813901bba65827259daa8e22ff94ec1f30e/doc/md_docs.go), which recursively generates documentation from the runtime model;
- the corresponding test files, especially `command_test.go`, `flag_groups_test.go`, and `completions_test.go`.

The textbook also uses the evidence-backed Cobra Architecture Garden study in [go-go-parc PR #2](https://github.com/go-go-golems/go-go-parc/pull/2), but it reorganizes and substantially expands that material.

## Mathematical conventions {-}

A **sequence** or **word** is written as

$$
w = t_1t_2\cdots t_n \in \Sigma^*,
$$

where $\Sigma$ is a token alphabet and $\Sigma^*$ is the set of all finite token sequences. Concatenation is written by juxtaposition or $\cdot$. The empty word is $\epsilon$.

A **partial function** $f : A \rightharpoonup B$ may be undefined for some inputs. We write

$$
f(a) = \bot
$$

when no result exists. In implementation code, $\bot$ usually appears as an error, a `nil` result, or both.

A **finite map** $M : K \rightharpoonup V$ associates some keys with values. `dom(M)` denotes its set of defined keys. Chapter 2 defines a left-biased composition operator $\oplus$ for maps.

A **predicate** is a Boolean-valued function. For example,

$$
\operatorname{Runnable}(v) \in \{\mathsf{true},\mathsf{false}\}
$$

says whether a command node has an executable handler.

\mainmatter

# The Command Tree as an Executable Language

## Why a CLI needs a semantic model

Imagine implementing `forge` without a central model. The parser knows that `repo clone` exists. The help system has a manually maintained table of commands. The completion script has another table. The documentation generator has a third. The authorization layer has a fourth list, and a test fixture has a fifth. Each list is locally reasonable. Together they form a distributed consistency problem.

The failure mode is **schema drift**: two components disagree about the structure of the interface. A command is executable but absent from help. A deprecated command disappears from help but remains in completion. A flag exists at runtime but not in generated documentation. A renamed command leaves a stale alias in a shell script.

Cobra's central architectural choice is to represent the CLI as one mutable graph of `Command` objects and to make multiple features interpret that graph. The graph is not only routing data. It is the semantic authority for command identity, hierarchy, descriptions, flags, validators, lifecycle hooks, completion functions, and documentation traversal.

> **Fundamentals: syntax versus semantics.** Syntax answers, "Which token sequences are well formed?" Semantics answers, "What does a well-formed sequence mean?" A command tree contributes to both. Its paths define a grammar fragment, while its node data supplies validation and execution meaning.

## Rooted labeled trees

We begin with the structure that makes hierarchy precise.

**Definition 1.1 (rooted tree).** A rooted tree is a tuple

$$
T = (V,E,r)
$$

where $V$ is a finite set of nodes, $E \subseteq V \times V$ is a parent-to-child edge relation, and $r \in V$ is the root, such that every node except $r$ has exactly one parent and every node is reachable from $r$.

The unique-parent condition matters. If a node had two parents, then its inherited flags, help template, error prefix, and command path could depend on which parent was chosen. Cobra stores one `parent *Command` pointer, so its intended topology is a rooted tree rather than a general directed acyclic graph.

**Definition 1.2 (labeled command tree).** A labeled command tree extends $T$ with:

- a canonical command name $n : V \to \mathcal{N}$;
- an alias set $A : V \to \mathcal{P}(\mathcal{N})$;
- metadata $m : V \to \mathcal{M}$;
- an optional handler $h : V \rightharpoonup \mathcal{H}$.

We write

$$
\mathcal{T} = (V,E,r,n,A,m,h).
$$

For a Cobra command, the canonical name is derived from the first word of `Use`; aliases come from `Aliases`; metadata includes `Short`, `Long`, examples, flags, validators, groups, and annotations; and the handler is `Run` or `RunE`.

**Definition 1.3 (command path).** Let

$$
r=v_0,v_1,\ldots,v_k=v
$$

be the unique root-to-$v$ path. The command path of $v$ is

$$
\operatorname{path}(v)=n(v_0)\;n(v_1)\;\cdots\;n(v_k).
$$

For the `clone` node in the running example,

```text
path(clone) = forge repo clone
```

Cobra exposes this relation through methods such as:

```go
func (c *Command) Parent() *Command
func (c *Command) Root() *Command
func (c *Command) CommandPath() string
func (c *Command) VisitParents(fn func(*Command))
func (c *Command) AddCommand(cmds ...*Command)
```

`AddCommand` is a **grafting operation**: it attaches one or more rooted subtrees beneath a parent and updates each child's parent pointer.

![A rooted command tree and a routing query.](figures/ch1-command-tree.png){ width=92% }

## Token words and routing

The shell presents a CLI with a sequence of strings. After shell quoting and expansion, Cobra sees an argument word such as

$$
w = [\texttt{repo},\texttt{clone},\texttt{--depth},\texttt{1},\texttt{URL}].
$$

The program name `forge` is normally removed before the framework receives `os.Args[1:]`.

**Definition 1.4 (routing).** Routing is a partial function

$$
\operatorname{route}_{\mathcal{T}} : \Sigma^* \rightharpoonup V \times \Sigma^*
$$

that maps an argument word to a selected command node and a residual word. The residual word contains tokens not consumed as command names.

The function is partial because an input may name no available command or may be ambiguous under optional prefix rules.

For the running example,

$$
\operatorname{route}_{\mathcal{T}}([	exttt{repo},	exttt{clone},	exttt{--depth},	exttt{1},	exttt{URL}])
=
(	exttt{clone},[	exttt{--depth},	exttt{1},	exttt{URL}]).
$$

Notice what routing does **not** do. It does not yet establish that `--depth` is legal, that `1` parses as an integer, that `URL` satisfies an argument contract, or that cloning is authorized. Routing chooses a syntactic destination. Later interpreters establish additional meaning.

### Canonical names and aliases

A token $x$ matches a child $v$ when either

$$
x=n(v)
$$

or

$$
x\in A(v).
$$

If `clone` has alias `cp`, then both words route to the same node:

```text
forge repo clone URL
forge repo cp URL
```

The semantic node is the same, but Cobra records which spelling was used through `CalledAs()`. That distinction is useful for compatibility warnings, telemetry, and display behavior.

### Prefix matching

Cobra can optionally accept an unambiguous prefix. Suppose a node has children named `clone` and `list`. The token `cl` matches only `clone`, so prefix routing can select it. If children are named `commit` and `compare`, the token `co` matches both and must not silently select either.

Formally, define the prefix candidate set

$$
P_x(v)=\{u\in\operatorname{children}(v)\mid x\preceq n(u)\text{ or }x\preceq a\text{ for some }a\in A(u)\},
$$

where $x\preceq y$ means that $x$ is a string prefix of $y$. Prefix routing is valid only when $|P_x(v)|=1$.

> **Counterexample: "first prefix wins."** Selecting the first matching child makes behavior depend on registration order. Adding a new command can silently change the meaning of an old abbreviation. Unique-prefix matching avoids that non-local instability, although Cobra leaves it disabled by default because abbreviations still create compatibility risk.

## Worked example: tracing `forge repo clone`

Consider this Go-like construction:

```go
root := &cobra.Command{Use: "forge"}
repo := &cobra.Command{Use: "repo", Short: "Repository operations"}
clone := &cobra.Command{
    Use:   "clone URL",
    Short: "Clone a repository",
    Args:  cobra.ExactArgs(1),
    RunE:  runClone,
}
repo.AddCommand(clone)
root.AddCommand(repo)
```

Now trace the word

```text
repo clone --depth 1 https://example.test/x.git
```

1. Start at `root` with the full word.
2. The first non-flag command token is `repo`; choose the `repo` child.
3. Remove only that occurrence of `repo` from the residual word.
4. At `repo`, the next command token is `clone`; choose the `clone` child.
5. The remaining word is `--depth 1 https://example.test/x.git`.
6. Routing stops because `clone` has no matching child in the residual word.
7. Flag parsing and positional validation happen later.

A simplified routing procedure is:

```text
function ROUTE(node, tokens):
    commandTokens := REMOVE_FLAG_NAMES_AND_VALUES(tokens, node.effectiveFlags)
    if commandTokens is empty:
        return (node, tokens)

    next := first(commandTokens)
    child := EXACT_ALIAS_OR_UNIQUE_PREFIX(node.children, next)
    if child does not exist:
        return (node, tokens)  // later logic may report unknown command

    residual := REMOVE_FIRST_NONFLAG_OCCURRENCE(tokens, next)
    return ROUTE(child, residual)
```

The real implementation is more careful because a token following `--flag` may be a flag value rather than a command name, and `--` terminates flag parsing. The important abstraction is that routing consumes command-name tokens while preserving a residual word for the selected node.

### `Find` and `Traverse`

Cobra offers two related routing modes:

```go
func (c *Command) Find(args []string) (*Command, []string, error)
func (c *Command) Traverse(args []string) (*Command, []string, error)
```

`Find` primarily identifies the deepest matching command and leaves flag parsing to the selected command. `Traverse` parses parent flags while descending, which permits local flags on parent commands before a child name when `TraverseChildren` is enabled.

This difference is semantic, not cosmetic. It changes the accepted language.

Without traversal:

```text
forge repo clone --host example.test URL
```

may be the expected arrangement for a parent-local flag.

With traversal, a form such as

```text
forge --config forge.yaml repo --host example.test clone URL
```

can be interpreted incrementally along the path. Chapter 2 gives the scope model needed to reason about which flags are visible at each point.

## Semantic authority and multiple interpreters

A command tree becomes especially valuable when it is interpreted more than once.

**Definition 1.5 (semantic model).** A semantic model is a machine-readable structure that contains the facts several system behaviors must agree on.

**Definition 1.6 (interpreter).** An interpreter is a function that consumes a semantic model and produces behavior or another representation:

$$
I : \mathcal{M} \times \mathcal{X} \to \mathcal{Y}.
$$

Cobra supports several interpreters over the command model $M$:

- execution: $I_{\mathrm{exec}}(M,\text{argv}) \to \text{effects and result}$;
- help: $I_{\mathrm{help}}(M,v) \to \text{human-readable usage}$;
- completion: $I_{\mathrm{comp}}(M,\text{partial argv}) \to \text{candidates and directives}$;
- documentation: $I_{\mathrm{doc}}(M) \to \text{Markdown/man/reST files}$;
- tests: $I_{\mathrm{test}}(M,\text{synthetic process boundary}) \to \text{observations}$.

The phrase **semantic authority** means that facts shared by those interpreters are declared in $M$, not independently in each interpreter.

A useful consistency law is:

$$
\operatorname{Visible}_{\mathrm{help}}(v)
=
\operatorname{Visible}_{\mathrm{completion}}(v)
$$

whenever both features are supposed to expose the same class of available commands. Cobra's `Hidden`, `Deprecated`, and availability predicates help preserve this agreement.

### Example: adding a new command once

Suppose we add:

```go
repo.AddCommand(&cobra.Command{
    Use:   "status",
    Short: "Show repository status",
    RunE:  runStatus,
})
```

If all interpreters traverse the command model, the new node becomes:

- routable as `forge repo status`;
- visible in help when available;
- eligible for completion;
- included in generated documentation;
- inspectable by command-tree tests.

There is still authored metadata that can be wrong. `Short` may be misleading, and `RunE` may be buggy. The model prevents **structural drift**, not all semantic defects.

## Tree composition and locality

The command-tree design supports modular construction. A package can return a rooted subtree:

```go
func NewRepoCommand(deps RepoDeps) *cobra.Command
func NewIssueCommand(deps IssueDeps) *cobra.Command
```

The application root grafts them together:

```go
root.AddCommand(NewRepoCommand(repoDeps))
root.AddCommand(NewIssueCommand(issueDeps))
```

This is compositional because each subtree can be reasoned about relative to an eventual parent. Its path, inherited flags, and inherited I/O are resolved after grafting.

**Definition 1.7 (subtree locality).** A property is subtree-local when it can be defined using a node and its descendants without inspecting unrelated siblings.

Examples include:

- whether a subtree contains a command named `clone`;
- the generated documentation rooted at `repo`;
- whether all children of `repo` belong to declared help groups.

A global uniqueness property such as "no two command paths collide under a flattened filename encoding" is not subtree-local; it requires comparison across the whole model.

## Availability is a predicate, not mere existence

A node can exist in the tree without being presented as an ordinary command.

Cobra distinguishes concepts including:

- **runnable**: `Run` or `RunE` is defined;
- **has subcommands**: the node has children;
- **hidden**: intentionally omitted from ordinary discovery;
- **deprecated**: retained for compatibility but discouraged;
- **additional help topic**: documentation-only structure rather than an executable command.

We can summarize ordinary availability as a predicate

$$
\operatorname{Available}(v)
=
\neg\operatorname{Hidden}(v)
\land
\neg\operatorname{Deprecated}(v)
\land
\big(\operatorname{Runnable}(v)\lor\operatorname{HasAvailableChildren}(v)\big),
$$

with special treatment for the synthesized help command.

This is a key modeling lesson: **membership and visibility are different relations**. A hidden protocol command can belong to the model temporarily while remaining absent from ordinary help. Chapter 4 develops that idea through `__complete`.

## Counterexamples and limits

### Counterexample 1: duplicated catalogs

Suppose the parser tree and help list are separate:

```go
router.Add("repo clone", runClone)
help.Add("repo clone", "Clone a repository")
```

The design has no structural mechanism forcing both calls to occur. A code-review convention can reduce drift but does not eliminate the second authority.

### Counterexample 2: a general graph with two parents

Suppose the `export` node is attached beneath both `repo` and `issue`. Which persistent flag set does it inherit? What is its command path? Which parent help template wins? A general DAG may be valid in another system, but it requires explicit semantics for multiple ancestry. Cobra's nearest-parent model assumes a tree.

### Counterexample 3: treating routing as authorization

If a caller can spell `forge issue close 42`, routing proves only that the command exists. It does not prove that the caller owns issue 42 or may close it. A command model is not an authority grant.

### Limit: mutable topology

Cobra's model is intentionally mutable. Commands can be added and removed, defaults can be synthesized, and completion can temporarily install internal nodes. Therefore the equation

$$
M_{\mathrm{construction}} = M_{\mathrm{execution}}
$$

is not automatically true. A design that requires immutable or signed schemas should resolve defaults and plugins in a build phase and then freeze the model.

> **Student question: Is `Command` an abstract syntax tree node?** It is close, but richer. An AST normally represents syntax independently of execution state. Cobra's `Command` also stores context, I/O overrides, caches, lifecycle functions, and mutable flag state. The reusable idea is "one semantic authority with multiple interpreters," not necessarily "put every concern in one struct."

## Chapter exercises

1. **Tree validity.** State the three conditions that distinguish a rooted tree from a general directed graph. For each condition, describe one Cobra ambiguity that would arise if it were violated.

2. **Route trace.** Given children `repo`, `report`, and `remote`, determine the result of prefix routing for tokens `rep`, `repo`, `rem`, and `r`.

3. **Residual words.** Trace routing for:

   ```text
   forge --config c.yaml repo clone --depth 1 URL
   ```

   under (a) non-traversing lookup and (b) parent-flag traversal. Identify which tokens are command names, flag names, flag values, and positional arguments.

4. **Alias semantics.** Design a node with canonical name `remove` and aliases `rm` and `delete`. Explain which parts of the model should use canonical identity and which may care about the spelling used by the caller.

5. **Interpreter agreement.** Write three invariants that help and completion should share. Then write one property on which they may intentionally differ.

6. **Grafting.** Define a function that attaches a subtree $S$ beneath node $v$ of tree $T$. What preconditions are required to preserve tree structure?

7. **Availability.** Construct a truth table for `Hidden`, `Deprecated`, `Runnable`, and `HasAvailableChildren`. Propose a simplified availability predicate and compare it with the one in this chapter.

8. **Countermodel.** Design a CLI where a general DAG is preferable to a tree. Specify explicit semantics for command path, inheritance, and documentation so that the ambiguities are resolved rather than ignored.

## Solution sketches

**Exercise 1.** The root is unique; every non-root node has exactly one parent; every node is reachable from the root, which also excludes disconnected components and, together with unique ancestry, cycles. Violations make `Root`, `CommandPath`, and inherited-policy lookup ambiguous or non-terminating.

**Exercise 2.** `repo` is exact. `rem` uniquely selects `remote`. `rep` is ambiguous between `repo` and `report`. `r` is ambiguous among all three.

**Exercise 5.** Shared invariants might include command-name visibility, parent/child structure, and omission of hidden/deprecated nodes. A deliberate difference is that help emits complete prose for a selected command, while completion analyzes an incomplete token prefix and may omit candidates already used.

**Exercise 6.** Preconditions include disjoint node identities, no edge from the subtree back into $T$, and exactly one new edge $(v,r_S)$. Existing parent pointers in $S$ must remain internal except for the subtree root, whose parent becomes $v$.
EOF
wc -w /mnt/data/cobra_textbook/Executable_Command_Languages.md
```

<details><summary>💭 Thinking</summary>

**Created diagrams and wrote Cobra command-language textbook chapters**

</details>

```unknown
bash -lc cat >> /mnt/data/cobra_textbook/Executable_Command_Languages.md <<'EOF'

# Execution as an Operational Semantics

## Why a command is more than a callback

A naive command framework stores a function beside a name:

```text
"clone" -> runClone
```

That association is necessary but not sufficient. Before `runClone` should perform network and filesystem effects, the system must answer several questions:

- Which command did the token word select?
- Which flags are visible in that scope?
- Did every flag value parse?
- Are the positional arguments legal?
- Should inherited setup hooks run?
- Are all required flags present?
- Do cross-flag constraints hold?
- Which context and streams should the handler observe?
- What happens when any earlier stage fails?

These questions define an **operational semantics**: a precise account of how an invocation moves through states and either reaches an effect or terminates with a result or error.

> **Fundamentals: operational semantics.** Denotational semantics maps a program directly to a mathematical meaning. Operational semantics describes execution as transitions between machine configurations. A CLI pipeline is naturally operational because ordering and short-circuit behavior are part of its contract.

## Machine configurations and stages

Let a machine configuration be

$$
\gamma=\langle s,v,w,\phi,\kappa,o\rangle,
$$

where:

- $s$ is the current stage;
- $v$ is the selected command node, if known;
- $w$ is the residual token word;
- $\phi$ is parsed flag state;
- $\kappa$ is execution context and inherited policy;
- $o$ is accumulated observation state, such as output and error.

Let the stage set be

$$
S=\{\textsf{route},\textsf{parse},\textsf{args},\textsf{pre},\textsf{flags},\textsf{run},\textsf{post},\textsf{done},\textsf{error}\}.
$$

A transition relation

$$
\gamma\to\gamma'
$$

says that one legal execution step changes configuration $\gamma$ into $\gamma'$.

![The staged execution machine and its short-circuit exits.](figures/ch3-execution-machine.png){ width=100% }

The central path is:

```text
route
  -> parse flags
  -> validate positional arguments
  -> run inherited/local pre-hooks
  -> validate required and grouped flags
  -> run the effect handler
  -> run local/inherited post-hooks
  -> done
```

Every arrow may instead lead to `error`. That branching behavior is just as important as the success path.

## Stage functions and error composition

We can model each stage as a partial or error-returning function.

Let `Result(X)` mean either a value in $X$ or an error. Then:

$$
R : \Sigma^* \to \operatorname{Result}(V\times\Sigma^*)
$$

routes a token word;

$$
P_v : \Sigma^* \to \operatorname{Result}(\Phi_v)
$$

parses flags for command $v$;

$$
A_v : \Phi_v \to \operatorname{Result}(\Phi_v)
$$

validates positional arguments;

$$
H_v^{\mathrm{pre}} : \Phi_v \to \operatorname{Result}(\Phi_v)
$$

runs preparation hooks;

$$
G_v : \Phi_v \to \operatorname{Result}(\Phi_v)
$$

validates required flags and group constraints;

$$
X_v : \Phi_v \to \operatorname{Result}(Y)
$$

performs the command effect;

$$
H_v^{\mathrm{post}} : Y \to \operatorname{Result}(Y)
$$

runs success-path post-hooks.

The executor is an error-short-circuiting composition:

$$
\operatorname{Exec}
=
H^{\mathrm{post}}
\mathbin{>=>}
X
\mathbin{>=>}
G
\mathbin{>=>}
H^{\mathrm{pre}}
\mathbin{>=>}
A
\mathbin{>=>}
P
\mathbin{>=>}
R,
$$

read from right to left. The operator $>=>$ denotes composition that stops when the left stage returns an error.

> **Side topic: the `Either` or `Result` pattern.** In functional programming, this is often called Kleisli composition for an error monad. The practical idea is simple: each stage returns either a value for the next stage or an error that bypasses the remaining success stages.

## Cobra's execution entry points

The public API includes:

```go
func (c *Command) Execute() error
func (c *Command) ExecuteC() (*Command, error)
func (c *Command) ExecuteContext(ctx context.Context) error
func (c *Command) ExecuteContextC(ctx context.Context) (*Command, error)
```

`ExecuteC` normalizes execution to the root, establishes a background context if none exists, initializes default infrastructure, chooses `Find` or `Traverse`, propagates root context to the selected child when needed, and invokes the selected node's internal `execute` method.

The selected command's internal sequence is approximately:

```text
1. initialize default help and version flags
2. parse flags
3. handle help/version short-circuits
4. require a runnable command
5. enter framework initializer/finalizer scope
6. validate positional arguments
7. run persistent pre-hook(s)
8. run local PreRun or PreRunE
9. validate required flags
10. validate grouped flags
11. run Run or RunE
12. run local PostRun or PostRunE
13. run persistent post-hook(s)
```

This sequence establishes the points at which different classes of error can occur.

## Admission and the effect boundary

**Definition 3.1 (effect boundary).** The effect boundary is the first point at which domain-specific external effects are permitted to begin.

For an ordinary Cobra command, the `Run` or `RunE` handler is the intended effect boundary. Earlier framework stages may still perform computation and pre-hooks may perform arbitrary application code, but the architecture treats the main handler as the command's domain effect owner.

**Definition 3.2 (admission predicate).** An invocation is admitted to the main effect when

$$
\operatorname{Admit}(v,w,\phi)
=
\operatorname{Routed}(v)
\land
\operatorname{Parsed}(\phi)
\land
\operatorname{ArgsValid}(v,w)
\land
\operatorname{PreSucceeded}(v)
\land
\operatorname{RequiredFlagsPresent}(v,\phi)
\land
\operatorname{FlagGroupsValid}(v,\phi).
$$

The executor should call the handler only if `Admit` is true.

This predicate is valuable even if no implementation literally computes one Boolean. It names the law the pipeline enforces.

## Positional arguments as predicates

Cobra represents positional validation with a function type:

```go
type PositionalArgs func(cmd *Command, args []string) error
```

A validator is therefore a predicate with an explanatory error:

$$
Q_v : \Sigma^* \to \{\mathsf{accept}\}\cup\operatorname{Error}.
$$

Built-in validators include:

```go
cobra.NoArgs
cobra.ArbitraryArgs
cobra.MinimumNArgs(n)
cobra.MaximumNArgs(n)
cobra.ExactArgs(n)
cobra.RangeArgs(min, max)
cobra.OnlyValidArgs
cobra.NoDuplicateArgs
```

`MatchAll` composes validators:

```go
func MatchAll(pargs ...PositionalArgs) PositionalArgs
```

Mathematically, if validators correspond to predicates $q_1,\ldots,q_n$, then

$$
\operatorname{MatchAll}(q_1,\ldots,q_n)(w)
=
\bigwedge_{i=1}^n q_i(w),
$$

with implementation short-circuiting at the first error.

### Worked example: a strict clone argument

Suppose `forge repo clone` requires exactly one unique positional argument and accepts only `https` URLs:

```go
func HTTPSURL(cmd *cobra.Command, args []string) error {
    if len(args) == 0 || !strings.HasPrefix(args[0], "https://") {
        return fmt.Errorf("repository URL must use https")
    }
    return nil
}

clone.Args = cobra.MatchAll(
    cobra.ExactArgs(1),
    cobra.NoDuplicateArgs,
    HTTPSURL,
)
```

For input

```text
forge repo clone ssh://example.test/x.git
```

routing and flag parsing may succeed, but positional admission fails before `RunE` is entered.

## Worked execution trace

Consider:

```go
clone := &cobra.Command{
    Use:  "clone URL",
    Args: cobra.ExactArgs(1),
    PreRunE: func(cmd *cobra.Command, args []string) error {
        return loadRepositoryProfile(cmd.Context())
    },
    RunE: func(cmd *cobra.Command, args []string) error {
        return cloneRepository(cmd.Context(), args[0])
    },
}
clone.Flags().Int("depth", 0, "history depth")
_ = clone.MarkFlagRequired("token")
```

Assume the command also has a required `--token` flag.

Trace this invocation:

```text
forge repo clone --depth 1 https://example.test/x.git
```

1. `route` selects `clone`.
2. `parse` accepts `--depth 1`.
3. `args` accepts exactly one positional argument.
4. `pre` loads the repository profile.
5. `flags` discovers that `--token` is missing.
6. execution returns an error.
7. `cloneRepository` does not run.
8. local and persistent `PostRun*` hooks do not run.

This trace exposes a subtle ordering choice: `PreRunE` executed before required-flag validation. Therefore a pre-hook can run for an invocation that is later rejected.

**Design implication:** pre-hooks should be idempotent or reversible when later framework validation can still fail. Applications should avoid irreversible side effects in a pre-hook unless they intentionally accept this ordering.

## Hook inheritance and order

Cobra supports local hooks and persistent hooks:

```go
PersistentPreRun, PersistentPreRunE
PreRun, PreRunE
Run, RunE
PostRun, PostRunE
PersistentPostRun, PersistentPostRunE
```

A persistent hook is eligible to affect descendants.

When `EnableTraverseRunHooks` is true, the conceptual order for a root `r`, parent `p`, and leaf `v` is:

```text
r.PersistentPreRun
p.PersistentPreRun
v.PersistentPreRun
v.PreRun
v.Run
v.PostRun
v.PersistentPostRun
p.PersistentPostRun
r.PersistentPostRun
```

Pre-hooks flow outer-to-inner. Post-hooks flow inner-to-outer. This resembles stack discipline.

When traversal is disabled, only the first applicable persistent hook is selected according to Cobra's lookup behavior. That mode is compatible with older "nearest hook wins" semantics but gives a different execution algebra.

> **Definition 3.3 (hook trace).** A hook trace is the ordered word of lifecycle labels observed during one invocation. Tests can assert trace equality, not merely that every hook eventually ran.

For example,

$$
\tau=[r.\mathrm{pre},p.\mathrm{pre},v.\mathrm{pre},v.\mathrm{run},v.\mathrm{post},p.\mathrm{post},r.\mathrm{post}].
$$

Ordering is a semantic property because hooks may transform shared state or depend on earlier preparation.

## The crucial counterexample: post-hooks are not `finally`

A common student assumption is:

```text
PreRun is before
Run is during
PostRun is guaranteed after
```

The last line is false.

`PostRun`, `PostRunE`, `PersistentPostRun`, and `PersistentPostRunE` are ordinary later success-path stages. If `RunE` returns an error, Cobra returns before those stages.

The following design leaks a resource:

```go
var conn *sql.DB

cmd.PreRunE = func(cmd *cobra.Command, args []string) error {
    var err error
    conn, err = sql.Open("sqlite", "work.db")
    return err
}

cmd.RunE = func(cmd *cobra.Command, args []string) error {
    return performWork(conn) // may return an error
}

cmd.PostRun = func(cmd *cobra.Command, args []string) {
    _ = conn.Close() // skipped when RunE fails
}
```

The correct effect-owned scope uses Go's guaranteed cleanup mechanism:

```go
cmd.RunE = func(cmd *cobra.Command, args []string) error {
    conn, err := sql.Open("sqlite", "work.db")
    if err != nil {
        return err
    }
    defer conn.Close()

    return performWork(conn)
}
```

**Definition 3.4 (guaranteed cleanup).** A cleanup action is guaranteed for a scope when every exit path after acquisition executes it, including normal return, error return, and panic paths covered by the language mechanism.

Cobra lifecycle post-hooks do not satisfy this definition for errors returned before their stage.

### Framework finalizers are different

Cobra's package-level `OnFinalize` callbacks are invoked through a deferred internal `postRun()` after the executor enters its initializer/finalizer scope. They therefore have stronger exit-path behavior for that scope than command `PostRun*` hooks.

However, they are process-global registrations, not resource-local lexical cleanup. They should not replace `defer` around a resource whose ownership is local to one handler.

## Errors as a sum of failure classes

A useful error taxonomy is

$$
\mathcal{E}
=
\mathcal{E}_{\mathrm{route}}
+\mathcal{E}_{\mathrm{parse}}
+\mathcal{E}_{\mathrm{args}}
+\mathcal{E}_{\mathrm{pre}}
+\mathcal{E}_{\mathrm{flags}}
+\mathcal{E}_{\mathrm{domain}}
+\mathcal{E}_{\mathrm{post}},
$$

where $+$ denotes a tagged sum.

Why preserve tags?

- a route error may suggest similar commands;
- a parse error should explain flag syntax;
- an argument error should display usage;
- a validation error means no domain effect should have started;
- a domain error means the effect boundary was crossed and may require retry or compensation;
- a post-hook error means the main effect may already have succeeded.

Cobra returns ordinary Go `error` values, so applications that need this distinction can wrap or type errors deliberately.

> **Side topic: error values versus exit codes.** A library-level executor should return errors. The outer process adapter decides the exit code and whether to print. Deep calls to `os.Exit` destroy composability because callers cannot recover, test, or add cleanup around them.

## Help and version as control-flow signals

Help is not an ordinary domain error. When the help flag is present, Cobra uses a distinguished signal (`flag.ErrHelp`) so the outer executor can render help and return without treating the request as a failed domain operation.

This is an example of a **control effect** represented through the error channel. The representation is pragmatic but requires callers to distinguish help from failure.

Version behaves similarly: when a generated version flag is set, Cobra renders the version and returns before the domain handler.

## Context as execution-scoped state

Context propagation gives handlers and completion functions access to cancellation, deadlines, and request-scoped values.

```go
func (c *Command) ExecuteContext(ctx context.Context) error
func (c *Command) Context() context.Context
func (c *Command) SetContext(ctx context.Context)
```

If execution begins without a context, Cobra installs `context.Background()`. If the selected child has no context, the root context is propagated to it.

This establishes a channel but not a guarantee. A handler that calls a blocking API without passing `cmd.Context()` ignores cancellation.

**Definition 3.5 (cancellation-respecting effect).** An effect respects cancellation when it either completes or returns promptly after its context is canceled, subject to documented bounds of the underlying operation.

## The flag-parsing escape hatch

`DisableFlagParsing` lets a command receive raw arguments. This is valuable for wrappers, plugin launchers, and commands that embed another language.

Formally, the command changes the grammar boundary:

$$
P_v = \operatorname{id}
$$

for the framework parser, and the residual word is delegated to the command.

This flexibility transfers responsibility. Required-flag checks, normal grouped-flag validation, and some completion semantics may no longer apply automatically. Escape hatches should be treated as new interpreters, not as free exceptions.

## Deterministic in-process execution

Cobra lets callers inject the process boundary:

```go
func (c *Command) SetArgs(a []string)
func (c *Command) SetIn(r io.Reader)
func (c *Command) SetOut(w io.Writer)
func (c *Command) SetErr(w io.Writer)
```

A test helper can run the production executor:

```go
func execute(root *cobra.Command, args ...string) (string, error) {
    buf := new(bytes.Buffer)
    root.SetOut(buf)
    root.SetErr(buf)
    root.SetArgs(args)
    err := root.Execute()
    return buf.String(), err
}
```

This supports **observational testing**: supply a controlled input configuration and inspect selected command, output, and error without forking a subprocess.

Two executions are observationally equivalent for a test suite $\mathcal{O}$ when

$$
\forall o\in\mathcal{O},\quad o(\operatorname{Exec}_1)=o(\operatorname{Exec}_2).
$$

The observation set may include returned error type, output bytes, selected command path, hook trace, and mock-service calls.

## Chapter exercises

1. **Transition trace.** Draw the complete configuration trace for a successful `forge issue close 42` invocation with one root persistent pre-hook and one leaf post-hook.

2. **Short-circuit proof.** Using the `Result` composition model, prove that if positional validation returns an error, the domain effect function is not evaluated.

3. **Validator design.** Implement a `DistinctFrom(flagName string)` positional validator that rejects an argument equal to a named flag value. Discuss whether it belongs in static metadata or a dynamic callback.

4. **Hook ordering.** For a four-level command path, list the hook trace with traversal enabled. Then specify the expected trace when only the nearest persistent hook is used.

5. **Cleanup analysis.** Find every exit path in the leaking database example. Explain exactly which paths skip `PostRun`. Rewrite the example so acquisition happens in a pre-hook but cleanup is still guaranteed.

6. **Error algebra.** Design tagged Go error types for route, validation, and domain failures. Show how an outer `main` adapter could map them to exit codes without calling `os.Exit` inside handlers.

7. **Context.** Write a `RunE` handler that launches two cancellable requests and returns the first successful result while canceling the other. State the cleanup and goroutine-leak obligations.

8. **Escape hatch.** Design a command `forge exec -- <program> <args...>` using `DisableFlagParsing`. Define where Cobra parsing ends and child-process parsing begins.

9. **Property test.** Generate random invalid argument counts for an `ExactArgs(2)` command and assert that the handler-call counter remains zero.

## Solution sketches

**Exercise 2.** Error-short-circuit composition evaluates the next function only for a successful value. If $A_v(x)=\operatorname{Error}(e)$, then $(X_v>=>A_v)(x)=\operatorname{Error}(e)$ by definition; $X_v$ is not called.

**Exercise 5.** If acquisition remains in `PreRunE`, store a cleanup closure in command-local execution state and install a framework-level guaranteed `defer` around the remaining pipeline, or redesign the framework adapter so the resource scope encloses both pre-hook and run stages. In ordinary application code, moving acquisition into `RunE` is simpler and safer.

**Exercise 6.** One mapping is route/usage errors to exit code 2, domain failures to 1, and cancellation to 130. `main` calls the executor, inspects the tagged error, prints through the command's error stream, and returns the selected code to the only process-level `os.Exit` call.

**Exercise 8.** The command consumes `forge exec` as framework syntax. Because flag parsing is disabled, the residual word beginning after `exec` is passed unchanged to the handler. The conventional `--` can be handled by the wrapper to separate wrapper options from child argv.
EOF
wc -w /mnt/data/cobra_textbook/Executable_Command_Languages.md
```

The structural pass is complete around one running CLI. Revisions now distinguish policy from provenance, validity from diagnostic order, and post stages from guaranteed cleanup, with proof/trace/design exercises.

<details><summary>💭 Thinking</summary>

**Revised textbook chapters, audited terminology, patched code, and verified PDF rendering**

</details>

```unknown
bash -lc python - <<'PY'
from pathlib import Path
src=Path('/mnt/data/cobra_textbook/Executable_Command_Languages.md').read_text()
# Replace YAML front matter with portable Markdown metadata.
end=src.find('\n---\n', 4)
body=src[end+5:]
for raw in ['\\frontmatter\n\n','\\mainmatter\n\n','\\backmatter\n']:
    body=body.replace(raw,'')
mermaids={
'![A rooted command tree and a routing query.](figures/ch1-command-tree.png){ width=92% }': '''```mermaid
flowchart TB
    forge[forge root] --> repo
    forge --> issue
    repo --> clone
    repo --> list
    issue --> create
    issue --> close
    argv["argv: repo clone --depth 1 URL"] --> route((route_T))
    route -. selects .-> clone
    route --> result["target = clone; residual = --depth 1 URL"]
```

*Figure 1.1: A rooted command tree and a routing query.*''',
'![Nearest-scope resolution for flags and streams.](figures/ch2-scope-resolution.png){ width=94% }': '''```mermaid
flowchart LR
    root["forge: persistent config, verbose; output buffer"] --> repo["repo: persistent host"]
    repo --> clone["clone: local depth and verbose"]
    clone --> effective["effective at clone: config from root; host from repo; local verbose shadows root; depth local; output from root"]
```

*Figure 2.1: Nearest-scope resolution for flags and streams.*''',
'![The staged execution machine and its short-circuit exits.](figures/ch3-execution-machine.png){ width=100% }': '''```mermaid
flowchart LR
    route[Route] --> parse[Parse flags]
    parse --> args[Validate arguments]
    args --> pre[Persistent and local pre-hooks]
    pre --> flags[Validate required and grouped flags]
    flags --> run[Run or RunE: effect boundary]
    run --> post[Local and persistent post-hooks]
    post --> ok((success))
    route -. error .-> err((error))
    parse -. error .-> err
    args -. error .-> err
    pre -. error .-> err
    flags -. error .-> err
    run -. error .-> err
    err --> note["PostRun is not finally: RunE error skips post-hooks"]
```

*Figure 3.1: The staged execution machine and its short-circuit exits.*''',
'![One semantic model interpreted as execution, help, completion, documentation, and tests.](figures/ch4-multiple-interpreters.png){ width=100% }': '''```mermaid
flowchart LR
    constraints[Constraint annotations] --> model[Semantic command model]
    model --> exec[Execution interpreter]
    model --> help[Help interpreter]
    model --> completion[Completion interpreter]
    model --> docs[Documentation interpreter]
    harness[Test harness with injected argv, context, and I/O] --> exec
    constraints -. reject .-> exec
    constraints -. guide .-> completion
```

*Figure 4.1: One semantic model interpreted as execution, help, completion, documentation, and tests.*'''
}
for old,new in mermaids.items():
    if old not in body:
        raise SystemExit(f'Missing image marker: {old}')
    body=body.replace(old,new)
front='''---
title: "Executable Command Languages"
subtitle: "Computer Science and Mathematical Structures in Cobra"
author: "An evidence-backed textbook derived from spf13/cobra"
date: "August 2026"
lang: en-US
---

'''
out=front+body
Path('/mnt/data/Executable_Command_Languages.md').write_text(out)
Path('/mnt/data/Executable_Command_Languages.pdf').write_bytes(Path('/mnt/data/cobra_textbook/Executable_Command_Languages.pdf').read_bytes())
PY
python - <<'PY'
from pathlib import Path
import re
p=Path('/mnt/data/Executable_Command_Languages.md')
text=p.read_text()
print('markdown words',len(re.findall(r"\b[\w'-]+\b",text)))
print('mermaid blocks',text.count('```mermaid'))
print('latex control leftovers', [x for x in ['\\frontmatter','\\mainmatter','\\backmatter','header-includes'] if x in text])
print('top-level',re.findall(r'^# (.+)$',text,re.M))
print('pdf bytes',Path('/mnt/data/Executable_Command_Languages.pdf').stat().st_size)
PY
ls -lh /mnt/data/Executable_Command_Languages.*
```

<details><summary>💭 Thinking</summary>

**Transformed Markdown diagrams and metadata, then verified PDF integrity and text extraction**

</details>

```json
{"paths":["GitHub"],"query":"fetch_file"}
```

# Executable Command Languages

Completed as a **65-page pedagogical textbook** organized into four chapters:

1. **Command Graphs as Executable Schemas** — rooted trees, command languages, partial resolution, aliases, semantic authority, tree folds, and ambiguity.
2. **Scopes, Inheritance, Shadowing, and Late Binding** — partial maps, left-biased override, provenance, persistent policy, default-synthesis laws, and scope counterexamples.
3. **Operational Semantics of Command Execution** — small-step transitions, effect admission, validator algebra, hook ordering, cleanup guarantees, and error taxonomy.
4. **Multiple Interpreters over One Model** — Boolean constraint systems, partial assignments, completion protocols, injectable process boundaries, documentation folds, and artifact-name injectivity.

The revision includes 56 motivated definitions, a continuous `atlas` running example, 16 worked examples, pseudocode and Go API signatures, formal propositions, counterexamples, 10 diagrams, chapter exercises, selected solutions, a comprehensive glossary, and a source map. It is grounded in the pinned Cobra Architecture Garden study and its eight focused pattern analyses. fileciteturn47file0L2-L2

- [Download the Markdown textbook](sandbox:/mnt/data/cobra-executable-command-languages/executable-command-languages.md)
- [Download the PDF textbook](sandbox:/mnt/data/cobra-executable-command-languages/executable-command-languages.pdf)
- [Download the Markdown source bundle with diagram assets](sandbox:/mnt/data/cobra-executable-command-languages-source.zip)


---

> Now study github.com/go-go-golems/glazed . I want to remove the dependency on cobra and implement my own CLI flag parsing, and potentially rearchitect/extend/update the Command framework and its mappings to CLI flags, and also make the help system a bit more modern if applicable. 
>
> Study all this, experiment, and write a phd thesis in the same style as the textook, as markdown and pdf

<details><summary>💭 Thinking</summary>

**Inspecting the repository**

I’ll study the public codebase through connected sources, review its structure, commits, issues, and tests, then prototype parser changes in a local sandbox without modifying the remote project.

**Inspected the repository**

</details>

```unknown
bash -lc cat /home/oai/skills/pdfs/SKILL.md && printf '\n---DOCX?---\n' && if [ -f /home/oai/skills/docx/SKILL.md ]; then sed -n '1,120p' /home/oai/skills/docx/SKILL.md; fi
```

I’ll pin Glazed, reconstruct its command/parameter/help architecture and Cobra coupling, then prototype and test replacements before writing a four-part architecture-and-language-design thesis in Markdown and PDF.

<details><summary>💭 Thinking</summary>

**Reviewed PDF generation guidance and textbook style diagrams**

**Fetched Glazed repository and inspected latest main branch contents**

</details>

```unknown
bash -lc rm -rf /mnt/data/glazed-study && git clone --no-tags --depth 1 https://github.com/go-go-golems/glazed.git /mnt/data/glazed-study && cd /mnt/data/glazed-study && git rev-parse HEAD && git status --short --branch
```

<details><summary>💭 Thinking</summary>

**Cloned the Glazed repository locally**

</details>

```json
{"open":[{"ref_id":"https://codeload.github.com/go-go-golems/glazed/tar.gz/a2bff0ece5f46b90975d7687f7c0dca2ea516d22"}],"response_length":"short"}
```

<details><summary>💭 Thinking</summary>

**Searching the web**

**Fetched GitHub repository archive**

</details>

```json
{"search_query":[{"q":"site:github.com/go-go-golems/glazed archive a2bff0ece5f46b90975d7687f7c0dca2ea516d22 tar.gz"},{"q":"https://api.github.com/repos/go-go-golems/glazed/tarball/a2bff0ece5f46b90975d7687f7c0dca2ea516d22"}],"response_length":"short"}
```

<details><summary>💭 Thinking</summary>

**Searched 1 website**

**Inspected Glazed CLI architecture and researched Cobra removal alternatives**

</details>

```unknown
bash -lc go version || true; go env GOPATH GOMODCACHE; find $(go env GOPATH 2>/dev/null)/pkg/mod/github.com/spf13 -maxdepth 2 -type d 2>/dev/null | head -30
```

Glazed already has a typed schema and layered-value model; the key redesign is extracting Cobra hooks from it, making CLI syntax one interpreter alongside existing sources and help.

<details><summary>💭 Thinking</summary>

**Checked Go environment and dependencies**

**Framing the study**

I’m treating this as a full architecture thesis: I’ll reconstruct Glazed’s command, parameter, flag, and help models, prototype Cobra-free alternatives, test them, and produce matching Markdown and PDF deliverables.

**Synthesizing the thesis**

I’m consolidating the repository study, architectural findings, prototypes, and experimental conclusions into a thesis-style treatment. I’ll preserve the textbook’s formal definitions, examples, exercises, diagrams, and polished document workflow.

**Mapping the architecture**

I’m tracing how command descriptions become CLI flags, how middleware establishes precedence, and how execution modes, structured output, aliases, help, and validation interact.

**Refining the design thesis**

I’m separating core command semantics from Cobra-specific adapters, formalizing source precedence and required-value validation, and connecting minimal output, immutable catalogs, manifests, and modern help into one architecture.

**Framed and refined the study’s architectural design thesis**

**Reviewed Glazed Cobra parsing, middleware, field registration, and help implementations**

**Inspected Glazed issue details, schemas, values, settings, CLI, and help implementations**

</details>

```unknown
bash -lc sed -n '1,220p' /mnt/data/cobra-executable-command-languages/executable-command-languages.md | head -220
```

<details><summary>💭 Thinking</summary>

**Inspected textbook metadata, project assets, archives, and diagramming tools**

</details>

```unknown
bash -lc set -euo pipefail
OUT=/mnt/data/glazed-native-cli-thesis
EXP=$OUT/experiments/nativecli
mkdir -p "$EXP"
cat > "$EXP/go.mod" <<'EOF'
module thesis.local/nativecli

go 1.23
EOF
cat > "$EXP/model.go" <<'EOF'
package nativecli

import (
    "encoding/json"
    "fmt"
    "sort"
    "strconv"
    "strings"
)

type ValueKind string

const (
    StringKind     ValueKind = "string"
    BoolKind       ValueKind = "bool"
    IntKind        ValueKind = "int"
    FloatKind      ValueKind = "float"
    StringListKind ValueKind = "string-list"
    IntListKind    ValueKind = "int-list"
    ChoiceKind     ValueKind = "choice"
)

type Scope string

const (
    LocalScope      Scope = "local"
    PersistentScope Scope = "persistent"
)

type RequiredMode string

const (
    Optional         RequiredMode = "optional"
    RequiredResolved RequiredMode = "resolved"
    RequiredCLI      RequiredMode = "cli"
)

type MergePolicy string

const (
    Replace MergePolicy = "replace"
    Append  MergePolicy = "append"
)

type FieldSpec struct {
    Key         string
    Long        string
    Short       rune
    Section     string
    Kind        ValueKind
    Help        string
    Choices     []string
    Default     []string
    Argument    bool
    Variadic    bool
    Scope       Scope
    Required    RequiredMode
    Merge       MergePolicy
    Hidden      bool
    Environment string
}

type CommandSpec struct {
    Name        string
    Aliases     []string
    Summary     string
    Description string
    Examples    []string
    Runnable    bool
    Fields      []FieldSpec
    Children    []*CommandSpec
}

type ProgramSpec struct {
    Name    string
    Summary string
    Root    *CommandSpec
}

type Field struct {
    FieldSpec
    OwnerPath string
    Position  int
}

type Command struct {
    Name        string
    Aliases     []string
    Summary     string
    Description string
    Examples    []string
    Runnable    bool
    Path        []string
    Parent      *Command
    Children    []*Command
    ChildIndex  map[string]*Command
    Local       []*Field
    Persistent  []*Field
    Arguments   []*Field
    FlagIndex   map[string]*Field
    ShortIndex  map[rune]*Field
}

type Program struct {
    Name     string
    Summary  string
    Root     *Command
    ByPath   map[string]*Command
    Manifest []byte
}

type CompileError struct {
    Path string
    What string
}

func (e *CompileError) Error() string {
    if e.Path == "" {
        return e.What
    }
    return e.Path + ": " + e.What
}

func Compile(spec ProgramSpec) (*Program, error) {
    if spec.Root == nil {
        return nil, &CompileError{What: "root command is required"}
    }
    if spec.Name == "" {
        spec.Name = spec.Root.Name
    }
    p := &Program{Name: spec.Name, Summary: spec.Summary, ByPath: map[string]*Command{}}
    root, err := compileCommand(nil, nil, spec.Root, p)
    if err != nil {
        return nil, err
    }
    p.Root = root
    manifest, err := canonicalManifest(p)
    if err != nil {
        return nil, err
    }
    p.Manifest = manifest
    return p, nil
}

func compileCommand(parent *Command, path []string, spec *CommandSpec, p *Program) (*Command, error) {
    if spec.Name == "" {
        return nil, &CompileError{Path: strings.Join(path, " "), What: "empty command name"}
    }
    for _, part := range append([]string{spec.Name}, spec.Aliases...) {
        if strings.TrimSpace(part) != part || strings.ContainsAny(part, " \t\n") || strings.HasPrefix(part, "-") {
            return nil, &CompileError{Path: strings.Join(path, " "), What: fmt.Sprintf("invalid command spelling %q", part)}
        }
    }
    full := append(append([]string(nil), path...), spec.Name)
    pathKey := strings.Join(full, " ")
    if _, exists := p.ByPath[pathKey]; exists {
        return nil, &CompileError{Path: pathKey, What: "duplicate command path"}
    }
    c := &Command{
        Name: spec.Name, Aliases: append([]string(nil), spec.Aliases...), Summary: spec.Summary,
        Description: spec.Description, Examples: append([]string(nil), spec.Examples...), Runnable: spec.Runnable,
        Path: full, Parent: parent, ChildIndex: map[string]*Command{}, FlagIndex: map[string]*Field{}, ShortIndex: map[rune]*Field{},
    }
    p.ByPath[pathKey] = c

    // Inherit only persistent flags. Local flags remain local to the declaring command.
    if parent != nil {
        for _, f := range parent.FlagIndex {
            if f.Scope == PersistentScope {
                c.FlagIndex[f.Long] = f
                if f.Short != 0 {
                    c.ShortIndex[f.Short] = f
                }
            }
        }
    }

    hadOptional := false
    hadVariadic := false
    argPos := 0
    for i := range spec.Fields {
        fs := spec.Fields[i]
        if fs.Key == "" {
            fs.Key = fs.Long
        }
        if fs.Section == "" {
            fs.Section = "default"
        }
        if fs.Scope == "" {
            fs.Scope = LocalScope
        }
        if fs.Required == "" {
            fs.Required = Optional
        }
        if fs.Merge == "" {
            fs.Merge = Replace
        }
        if fs.Argument {
            if fs.Long != "" || fs.Short != 0 {
                return nil, &CompileError{Path: pathKey, What: fmt.Sprintf("argument %s cannot have flag spellings", fs.Key)}
            }
            if hadVariadic {
                return nil, &CompileError{Path: pathKey, What: fmt.Sprintf("argument %s follows a variadic argument", fs.Key)}
            }
            required := fs.Required != Optional
            if required && hadOptional {
                return nil, &CompileError{Path: pathKey, What: fmt.Sprintf("required argument %s follows an optional argument", fs.Key)}
            }
            if !required {
                hadOptional = true
            }
            if fs.Variadic {
                hadVariadic = true
            }
            f := &Field{FieldSpec: fs, OwnerPath: pathKey, Position: argPos}
            argPos++
            c.Arguments = append(c.Arguments, f)
            continue
        }
        if fs.Long == "" {
            fs.Long = normalizeName(fs.Key)
        }
        fs.Long = normalizeName(fs.Long)
        if strings.Contains(fs.Long, "=") || strings.HasPrefix(fs.Long, "-") || fs.Long == "" {
            return nil, &CompileError{Path: pathKey, What: fmt.Sprintf("invalid long flag %q", fs.Long)}
        }
        if old, exists := c.FlagIndex[fs.Long]; exists {
            return nil, &CompileError{Path: pathKey, What: fmt.Sprintf("flag --%s collides with %s.%s", fs.Long, old.OwnerPath, old.Key)}
        }
        if fs.Short != 0 {
            if fs.Short == '-' || fs.Short == '=' || fs.Short == ' ' {
                return nil, &CompileError{Path: pathKey, What: fmt.Sprintf("invalid short flag %q", string(fs.Short))}
            }
            if old, exists := c.ShortIndex[fs.Short]; exists {
                return nil, &CompileError{Path: pathKey, What: fmt.Sprintf("short flag -%c collides with %s.%s", fs.Short, old.OwnerPath, old.Key)}
            }
        }
        if err := validateDefault(fs); err != nil {
            return nil, &CompileError{Path: pathKey, What: err.Error()}
        }
        f := &Field{FieldSpec: fs, OwnerPath: pathKey}
        c.FlagIndex[fs.Long] = f
        if fs.Short != 0 {
            c.ShortIndex[fs.Short] = f
        }
        if fs.Scope == PersistentScope {
            c.Persistent = append(c.Persistent, f)
        } else {
            c.Local = append(c.Local, f)
        }
    }

    for _, childSpec := range spec.Children {
        child, err := compileCommand(c, full, childSpec, p)
        if err != nil {
            return nil, err
        }
        for _, spelling := range append([]string{child.Name}, child.Aliases...) {
            if old, exists := c.ChildIndex[spelling]; exists {
                return nil, &CompileError{Path: pathKey, What: fmt.Sprintf("child spelling %q is shared by %s and %s", spelling, old.Name, child.Name)}
            }
            c.ChildIndex[spelling] = child
        }
        c.Children = append(c.Children, child)
    }
    sort.Slice(c.Children, func(i, j int) bool { return c.Children[i].Name < c.Children[j].Name })
    return c, nil
}

func normalizeName(s string) string { return strings.ReplaceAll(s, "_", "-") }

func validateDefault(f FieldSpec) error {
    for _, raw := range f.Default {
        if _, err := decodeOne(f.Kind, raw, f.Choices); err != nil {
            return fmt.Errorf("invalid default for %s: %w", f.Key, err)
        }
    }
    return nil
}

func decodeOne(kind ValueKind, raw string, choices []string) (any, error) {
    switch kind {
    case StringKind, StringListKind:
        return raw, nil
    case BoolKind:
        v, err := strconv.ParseBool(raw)
        if err != nil { return nil, fmt.Errorf("expected boolean, got %q", raw) }
        return v, nil
    case IntKind, IntListKind:
        v, err := strconv.Atoi(raw)
        if err != nil { return nil, fmt.Errorf("expected integer, got %q", raw) }
        return v, nil
    case FloatKind:
        v, err := strconv.ParseFloat(raw, 64)
        if err != nil { return nil, fmt.Errorf("expected number, got %q", raw) }
        return v, nil
    case ChoiceKind:
        for _, c := range choices { if raw == c { return raw, nil } }
        return nil, fmt.Errorf("expected one of %s, got %q", strings.Join(choices, ", "), raw)
    default:
        return nil, fmt.Errorf("unsupported value kind %q", kind)
    }
}

type manifestProgram struct {
    APIVersion string            `json:"apiVersion"`
    Kind       string            `json:"kind"`
    Name       string            `json:"name"`
    Commands   []manifestCommand `json:"commands"`
}

type manifestCommand struct {
    Path      []string        `json:"path"`
    Summary   string          `json:"summary,omitempty"`
    Runnable  bool            `json:"runnable"`
    Aliases   []string        `json:"aliases,omitempty"`
    Fields    []manifestField `json:"fields,omitempty"`
    Arguments []manifestField `json:"arguments,omitempty"`
}

type manifestField struct {
    Key      string       `json:"key"`
    Long     string       `json:"long,omitempty"`
    Short    string       `json:"short,omitempty"`
    Section  string       `json:"section"`
    Kind     ValueKind    `json:"kind"`
    Scope    Scope        `json:"scope,omitempty"`
    Required RequiredMode `json:"required"`
    Variadic bool         `json:"variadic,omitempty"`
    Choices  []string     `json:"choices,omitempty"`
}

func canonicalManifest(p *Program) ([]byte, error) {
    keys := make([]string, 0, len(p.ByPath))
    for k := range p.ByPath { keys = append(keys, k) }
    sort.Strings(keys)
    m := manifestProgram{APIVersion: "glazed.dev/native-cli/v0alpha1", Kind: "CommandCatalog", Name: p.Name}
    for _, k := range keys {
        c := p.ByPath[k]
        mc := manifestCommand{Path: append([]string(nil), c.Path...), Summary: c.Summary, Runnable: c.Runnable, Aliases: append([]string(nil), c.Aliases...)}
        fields := make([]*Field, 0, len(c.Local)+len(c.Persistent))
        fields = append(fields, c.Local...)
        fields = append(fields, c.Persistent...)
        sort.Slice(fields, func(i, j int) bool { return fields[i].Long < fields[j].Long })
        for _, f := range fields {
            mf := manifestField{Key: f.Key, Long: f.Long, Section: f.Section, Kind: f.Kind, Scope: f.Scope, Required: f.Required, Choices: append([]string(nil), f.Choices...)}
            if f.Short != 0 { mf.Short = string(f.Short) }
            mc.Fields = append(mc.Fields, mf)
        }
        for _, f := range c.Arguments {
            mc.Arguments = append(mc.Arguments, manifestField{Key: f.Key, Section: f.Section, Kind: f.Kind, Required: f.Required, Variadic: f.Variadic, Choices: append([]string(nil), f.Choices...)})
        }
        m.Commands = append(m.Commands, mc)
    }
    return json.MarshalIndent(m, "", "  ")
}
EOF
cat > "$EXP/parse.go" <<'EOF'
package nativecli

import (
    "fmt"
    "sort"
    "strings"
)

type Source string

const (
    DefaultSource Source = "default"
    ConfigSource  Source = "config"
    EnvSource     Source = "env"
    ArgSource     Source = "argument"
    FlagSource    Source = "flag"
)

type RawAssignment struct {
    Key        string
    Raw        []string
    Source     Source
    TokenIndex int
    Spelling   string
}

type ParseResult struct {
    Command     *Command
    Assignments []RawAssignment
    Positionals []string
    Trace       []string
}

type Diagnostic struct {
    Code       string
    Message    string
    TokenIndex int
    Token      string
    Suggestions []string
}

func (d *Diagnostic) Error() string {
    if d.TokenIndex >= 0 {
        return fmt.Sprintf("token %d (%q): %s", d.TokenIndex, d.Token, d.Message)
    }
    return d.Message
}

func Parse(p *Program, argv []string) (*ParseResult, error) {
    if p == nil || p.Root == nil { return nil, &Diagnostic{Code: "E_PROGRAM", Message: "nil program", TokenIndex: -1} }
    r := &ParseResult{Command: p.Root}
    current := p.Root
    flagsEnabled := true
    positionalStarted := false

    for i := 0; i < len(argv); i++ {
        tok := argv[i]
        r.Trace = append(r.Trace, fmt.Sprintf("q=%s token[%d]=%q", strings.Join(current.Path, " "), i, tok))
        if flagsEnabled && tok == "--" {
            flagsEnabled = false
            r.Trace = append(r.Trace, "enter positional-only mode")
            continue
        }
        if flagsEnabled && strings.HasPrefix(tok, "--") && len(tok) > 2 {
            name, inline, hasInline := splitLong(tok[2:])
            f, ok := current.FlagIndex[name]
            if !ok {
                return nil, unknownFlag(current, i, tok, name)
            }
            raw, consumed, err := consumeValue(f, inline, hasInline, argv, i)
            if err != nil { return nil, err }
            i += consumed
            r.Assignments = append(r.Assignments, RawAssignment{Key: f.Key, Raw: raw, Source: FlagSource, TokenIndex: i-consumed, Spelling: "--"+name})
            continue
        }
        if flagsEnabled && strings.HasPrefix(tok, "-") && tok != "-" {
            assignments, consumed, err := parseShort(current, argv, i)
            if err != nil { return nil, err }
            r.Assignments = append(r.Assignments, assignments...)
            i += consumed
            continue
        }
        if !positionalStarted {
            if child, ok := current.ChildIndex[tok]; ok {
                current = child
                r.Command = child
                r.Trace = append(r.Trace, "descend to "+strings.Join(child.Path, " "))
                continue
            }
        }
        positionalStarted = true
        r.Positionals = append(r.Positionals, tok)
    }

    if !r.Command.Runnable && len(r.Command.Children) > 0 {
        names := make([]string, 0, len(r.Command.Children))
        for _, c := range r.Command.Children { names = append(names, c.Name) }
        return nil, &Diagnostic{Code: "E_COMMAND_REQUIRED", Message: "a subcommand is required; choose one of: "+strings.Join(names, ", "), TokenIndex: len(argv)}
    }
    posAssignments, err := bindPositionals(r.Command, r.Positionals)
    if err != nil { return nil, err }
    r.Assignments = append(r.Assignments, posAssignments...)
    return r, nil
}

func splitLong(s string) (name, value string, has bool) {
    if i := strings.IndexByte(s, '='); i >= 0 { return s[:i], s[i+1:], true }
    return s, "", false
}

func consumeValue(f *Field, inline string, hasInline bool, argv []string, i int) ([]string, int, error) {
    if f.Kind == BoolKind {
        if hasInline { return []string{inline}, 0, nil }
        return []string{"true"}, 0, nil
    }
    if hasInline { return []string{inline}, 0, nil }
    if i+1 >= len(argv) {
        return nil, 0, &Diagnostic{Code: "E_FLAG_VALUE", Message: fmt.Sprintf("flag --%s requires a value", f.Long), TokenIndex: i, Token: argv[i]}
    }
    return []string{argv[i+1]}, 1, nil
}

func parseShort(c *Command, argv []string, i int) ([]RawAssignment, int, error) {
    token := argv[i]
    runes := []rune(token[1:])
    if len(runes) == 0 { return nil, 0, nil }
    out := []RawAssignment{}
    for j, r := range runes {
        f, ok := c.ShortIndex[r]
        if !ok {
            return nil, 0, &Diagnostic{Code: "E_UNKNOWN_SHORT", Message: fmt.Sprintf("unknown short flag -%c", r), TokenIndex: i, Token: token}
        }
        spelling := "-"+string(r)
        if f.Kind == BoolKind {
            out = append(out, RawAssignment{Key: f.Key, Raw: []string{"true"}, Source: FlagSource, TokenIndex: i, Spelling: spelling})
            continue
        }
        tail := string(runes[j+1:])
        if tail != "" {
            out = append(out, RawAssignment{Key: f.Key, Raw: []string{tail}, Source: FlagSource, TokenIndex: i, Spelling: spelling})
            return out, 0, nil
        }
        if i+1 >= len(argv) {
            return nil, 0, &Diagnostic{Code: "E_FLAG_VALUE", Message: fmt.Sprintf("flag -%c requires a value", r), TokenIndex: i, Token: token}
        }
        out = append(out, RawAssignment{Key: f.Key, Raw: []string{argv[i+1]}, Source: FlagSource, TokenIndex: i, Spelling: spelling})
        return out, 1, nil
    }
    return out, 0, nil
}

func bindPositionals(c *Command, args []string) ([]RawAssignment, error) {
    out := []RawAssignment{}
    idx := 0
    for _, f := range c.Arguments {
        if f.Variadic {
            if idx < len(args) {
                out = append(out, RawAssignment{Key: f.Key, Raw: append([]string(nil), args[idx:]...), Source: ArgSource, TokenIndex: idx, Spelling: f.Key})
                idx = len(args)
            }
            break
        }
        if idx < len(args) {
            out = append(out, RawAssignment{Key: f.Key, Raw: []string{args[idx]}, Source: ArgSource, TokenIndex: idx, Spelling: f.Key})
            idx++
        }
    }
    if idx < len(args) {
        return nil, &Diagnostic{Code: "E_TOO_MANY_ARGS", Message: fmt.Sprintf("expected at most %d positional arguments, got %d", len(c.Arguments), len(args)), TokenIndex: idx, Token: args[idx]}
    }
    return out, nil
}

func unknownFlag(c *Command, i int, token, name string) error {
    candidates := make([]string, 0, len(c.FlagIndex))
    for n := range c.FlagIndex { candidates = append(candidates, n) }
    sort.Strings(candidates)
    scored := []string{}
    best := 99
    for _, candidate := range candidates {
        d := levenshtein(name, candidate)
        if d < best { best = d; scored = []string{candidate} } else if d == best { scored = append(scored, candidate) }
    }
    if best > 3 { scored = nil }
    return &Diagnostic{Code: "E_UNKNOWN_FLAG", Message: "unknown flag --"+name, TokenIndex: i, Token: token, Suggestions: scored}
}

func levenshtein(a,b string) int {
    ar, br := []rune(a), []rune(b)
    prev := make([]int, len(br)+1)
    for j := range prev { prev[j] = j }
    for i, x := range ar {
        cur := make([]int, len(br)+1); cur[0] = i+1
        for j, y := range br {
            cost := 1; if x==y { cost=0 }
            cur[j+1] = min3(cur[j]+1, prev[j+1]+1, prev[j]+cost)
        }
        prev = cur
    }
    return prev[len(br)]
}
func min3(a,b,c int) int { if b<a {a=b}; if c<a {a=c}; return a }
EOF
cat > "$EXP/resolve.go" <<'EOF'
package nativecli

import (
    "fmt"
    "sort"
    "strings"
)

type SourceValues struct {
    Source      Source
    Assignments []RawAssignment
}

type Step struct {
    Source Source `json:"source"`
    Raw    []string `json:"raw"`
    Value  any `json:"value"`
    Note   string `json:"note,omitempty"`
}

type ResolvedValue struct {
    Field *Field `json:"-"`
    Value any `json:"value"`
    Steps []Step `json:"steps"`
}

type Values struct {
    Command *Command
    Fields map[string]*ResolvedValue
}

func Defaults(c *Command) SourceValues {
    assignments := []RawAssignment{}
    // Deterministic traversal over effective flags and local arguments.
    names := make([]string,0,len(c.FlagIndex)); for n := range c.FlagIndex { names=append(names,n) }; sort.Strings(names)
    seen := map[string]bool{}
    for _, n := range names {
        f := c.FlagIndex[n]
        if seen[f.Key] { continue }; seen[f.Key]=true
        if len(f.Default)>0 { assignments=append(assignments,RawAssignment{Key:f.Key,Raw:append([]string(nil),f.Default...),Source:DefaultSource,TokenIndex:-1,Spelling:"default"}) }
    }
    for _, f := range c.Arguments {
        if len(f.Default)>0 { assignments=append(assignments,RawAssignment{Key:f.Key,Raw:append([]string(nil),f.Default...),Source:DefaultSource,TokenIndex:-1,Spelling:"default"}) }
    }
    return SourceValues{Source:DefaultSource,Assignments:assignments}
}

func Resolve(c *Command, sources ...SourceValues) (*Values, error) {
    fields := effectiveFields(c)
    result := &Values{Command:c,Fields:map[string]*ResolvedValue{}}
    for _, source := range sources {
        grouped := map[string][]RawAssignment{}
        order := []string{}
        for _, a := range source.Assignments {
            if _, ok := grouped[a.Key]; !ok { order=append(order,a.Key) }
            grouped[a.Key]=append(grouped[a.Key],a)
        }
        for _, key := range order {
            f, ok := fields[key]
            if !ok { return nil, fmt.Errorf("source %s assigned unknown field %s", source.Source,key) }
            as := grouped[key]
            raw := []string{}
            for _, a := range as { raw=append(raw,a.Raw...) }
            decoded, err := decodeMany(f,raw)
            if err != nil { return nil, fmt.Errorf("%s from %s: %w",key,source.Source,err) }
            rv, exists := result.Fields[key]
            if !exists { rv=&ResolvedValue{Field:f}; result.Fields[key]=rv }
            if f.Merge==Append && exists && isListKind(f.Kind) {
                decoded=appendAny(rv.Value,decoded)
            }
            rv.Value=decoded
            rv.Steps=append(rv.Steps,Step{Source:source.Source,Raw:append([]string(nil),raw...),Value:decoded})
        }
    }
    for key, f := range fields {
        rv, present := result.Fields[key]
        switch f.Required {
        case RequiredResolved:
            if !present || emptyValue(rv.Value) { return nil, fmt.Errorf("%s is required after all sources are resolved",key) }
        case RequiredCLI:
            if !present || !hasSource(rv.Steps,FlagSource) && !hasSource(rv.Steps,ArgSource) { return nil, fmt.Errorf("%s must be supplied on the command line",key) }
        }
    }
    return result,nil
}

func effectiveFields(c *Command) map[string]*Field {
    out:=map[string]*Field{}
    for _,f:=range c.FlagIndex {out[f.Key]=f}
    for _,f:=range c.Arguments {out[f.Key]=f}
    return out
}
func decodeMany(f *Field,raw []string)(any,error){
    if isListKind(f.Kind){
        vals:=make([]any,0,len(raw)); for _,r:=range raw{v,e:=decodeOne(f.KindBase(),r,f.Choices);if e!=nil{return nil,e};vals=append(vals,v)}; return vals,nil
    }
    if len(raw)==0{return nil,fmt.Errorf("missing value")}
    return decodeOne(f.Kind,raw[len(raw)-1],f.Choices)
}
func (f *Field) KindBase() ValueKind { if f.Kind==StringListKind{return StringKind}; if f.Kind==IntListKind{return IntKind}; return f.Kind }
func isListKind(k ValueKind)bool{return k==StringListKind||k==IntListKind}
func appendAny(a,b any)any{aa,_:=a.([]any);bb,_:=b.([]any);return append(append([]any(nil),aa...),bb...)}
func hasSource(steps []Step,s Source)bool{for _,x:=range steps{if x.Source==s{return true}};return false}
func emptyValue(v any)bool{if v==nil{return true};switch x:=v.(type){case string:return strings.TrimSpace(x)=="";case []any:return len(x)==0};return false}

func MapSource(source Source, values map[string][]string) SourceValues {
    keys:=make([]string,0,len(values));for k:=range values{keys=append(keys,k)};sort.Strings(keys)
    as:=make([]RawAssignment,0,len(keys));for _,k:=range keys{as=append(as,RawAssignment{Key:k,Raw:append([]string(nil),values[k]...),Source:source,TokenIndex:-1,Spelling:string(source)})}
    return SourceValues{Source:source,Assignments:as}
}
EOF
cat > "$EXP/help.go" <<'EOF'
package nativecli

import (
    "bytes"
    "encoding/json"
    "fmt"
    "sort"
    "strings"
    "text/tabwriter"
)

type HelpMode string
const(
    QuickHelp HelpMode="quick"
    FullHelp HelpMode="full"
    MachineHelp HelpMode="machine"
)

type HelpIR struct {
    Path []string `json:"path"`
    Summary string `json:"summary"`
    Description string `json:"description,omitempty"`
    Usage string `json:"usage"`
    Commands []HelpCommand `json:"commands,omitempty"`
    Groups []HelpGroup `json:"groups,omitempty"`
    Examples []string `json:"examples,omitempty"`
}
type HelpCommand struct{Name string `json:"name"`;Summary string `json:"summary"`}
type HelpGroup struct{Section string `json:"section"`;Fields []HelpField `json:"fields"`}
type HelpField struct{Syntax string `json:"syntax"`;Key string `json:"key"`;Kind ValueKind `json:"kind"`;Required RequiredMode `json:"required"`;Help string `json:"help"`;Default []string `json:"default,omitempty"`;Choices []string `json:"choices,omitempty"`;Inherited bool `json:"inherited,omitempty"`}

func BuildHelp(c *Command, mode HelpMode)*HelpIR{
    ir:=&HelpIR{Path:append([]string(nil),c.Path...),Summary:c.Summary,Description:c.Description,Usage:usage(c),Examples:append([]string(nil),c.Examples...)}
    for _,ch:=range c.Children{ir.Commands=append(ir.Commands,HelpCommand{Name:ch.Name,Summary:ch.Summary})}
    groups:=map[string][]HelpField{};sections:=[]string{};seen:=map[string]bool{}
    fields:=make([]*Field,0,len(c.FlagIndex));used:=map[*Field]bool{};for _,f:=range c.FlagIndex{if !used[f]{fields=append(fields,f);used[f]=true}}
    sort.Slice(fields,func(i,j int)bool{if fields[i].Section==fields[j].Section{return fields[i].Long<fields[j].Long};return fields[i].Section<fields[j].Section})
    for _,f:=range fields{if f.Hidden&&mode!=MachineHelp{continue};if mode==QuickHelp&&f.Section!="default"&&f.Section!="structured-output"{continue};if !seen[f.Section]{sections=append(sections,f.Section);seen[f.Section]=true};syntax:="--"+f.Long;if f.Short!=0{syntax="-"+string(f.Short)+", "+syntax};if f.Kind!=BoolKind{syntax+=" "+strings.ToUpper(string(f.Kind))};groups[f.Section]=append(groups[f.Section],HelpField{Syntax:syntax,Key:f.Key,Kind:f.Kind,Required:f.Required,Help:f.Help,Default:append([]string(nil),f.Default...),Choices:append([]string(nil),f.Choices...),Inherited:f.OwnerPath!=strings.Join(c.Path," ")})}
    for _,s:=range sections{ir.Groups=append(ir.Groups,HelpGroup{Section:s,Fields:groups[s]})}
    return ir
}
func usage(c *Command)string{parts:=append([]string(nil),c.Path...);if len(c.Children)>0{parts=append(parts,"<command>")};for _,a:=range c.Arguments{name:=strings.ToUpper(a.Key);if a.Variadic{name+="..."};if a.Required==Optional{name="["+name+"]"}else{name="<"+name+">"};parts=append(parts,name)};if len(c.FlagIndex)>0{parts=append(parts,"[flags]")};return strings.Join(parts," ")}
func RenderText(ir *HelpIR)string{var b bytes.Buffer;fmt.Fprintf(&b,"%s — %s\n\nUsage:\n  %s\n",strings.Join(ir.Path," "),ir.Summary,ir.Usage);if ir.Description!=""{fmt.Fprintf(&b,"\n%s\n",ir.Description)};if len(ir.Commands)>0{fmt.Fprintln(&b,"\nCommands:");w:=tabwriter.NewWriter(&b,2,4,2,' ',0);for _,c:=range ir.Commands{fmt.Fprintf(w,"  %s\t%s\n",c.Name,c.Summary)};w.Flush()};for _,g:=range ir.Groups{fmt.Fprintf(&b,"\n%s options:\n",title(g.Section));w:=tabwriter.NewWriter(&b,2,4,2,' ',0);for _,f:=range g.Fields{extra:="";if len(f.Choices)>0{extra+=" {"+strings.Join(f.Choices,"|")+"}"};if len(f.Default)>0{extra+=" (default "+strings.Join(f.Default,",")+")"};if f.Inherited{extra+=" [inherited]"};fmt.Fprintf(w,"  %s\t%s%s\n",f.Syntax,f.Help,extra)};w.Flush()};if len(ir.Examples)>0{fmt.Fprintln(&b,"\nExamples:");for _,e:=range ir.Examples{fmt.Fprintln(&b,"  "+e)}};return b.String()}
func RenderJSON(ir *HelpIR)([]byte,error){return json.MarshalIndent(ir,"","  ")}
func title(s string)string{if s==""{return "General"};return strings.ToUpper(s[:1])+s[1:]}

type Completion struct{Value string;Description string;Kind string}
func Complete(p *Program,argv []string)[]Completion{
    // Parse all complete tokens except a trailing partial token. On parse failure,
    // fall back to root candidates rather than executing anything.
    partial:="";base:=argv;if len(argv)>0{partial=argv[len(argv)-1];base=argv[:len(argv)-1]}
    r,err:=Parse(p,base);c:=p.Root;if err==nil{c=r.Command}
    out:=[]Completion{}
    if strings.HasPrefix(partial,"-"){
        seen:=map[*Field]bool{};for _,f:=range c.FlagIndex{if seen[f]||f.Hidden{continue};seen[f]=true;candidate:="--"+f.Long;if strings.HasPrefix(candidate,partial){out=append(out,Completion{Value:candidate,Description:f.Help,Kind:"flag"})}}
    }else{
        for _,ch:=range c.Children{if strings.HasPrefix(ch.Name,partial){out=append(out,Completion{Value:ch.Name,Description:ch.Summary,Kind:"command"})}}
        if len(c.Arguments)>0{a:=c.Arguments[min(len(rSafePositionals(r)),len(c.Arguments)-1)];for _,choice:=range a.Choices{if strings.HasPrefix(choice,partial){out=append(out,Completion{Value:choice,Description:a.Help,Kind:"argument"})}}}
    }
    sort.Slice(out,func(i,j int)bool{return out[i].Value<out[j].Value});return out
}
func rSafePositionals(r *ParseResult)[]string{if r==nil{return nil};return r.Positionals}
func min(a,b int)int{if a<b{return a};return b}
EOF
cat > "$EXP/example.go" <<'EOF'
package nativecli

func ExampleProgram() ProgramSpec {
    return ProgramSpec{
        Name:"atlas",Summary:"Inspect and manage indexed documents",
        Root:&CommandSpec{Name:"atlas",Summary:"Inspect and manage indexed documents",Fields:[]FieldSpec{
            {Key:"config",Long:"config",Short:'c',Kind:StringKind,Help:"Configuration file",Scope:PersistentScope,Environment:"ATLAS_CONFIG"},
            {Key:"verbose",Long:"verbose",Short:'v',Kind:BoolKind,Help:"Enable diagnostic output",Scope:PersistentScope,Default:[]string{"false"}},
        },Children:[]*CommandSpec{
            {Name:"search",Aliases:[]string{"find"},Summary:"Search the document index",Description:"Searches the index and emits structured result rows.",Runnable:true,Examples:[]string{"atlas search retry policy --limit 10 --format jsonl"},Fields:[]FieldSpec{
                {Key:"query",Argument:true,Kind:StringListKind,Variadic:true,Required:RequiredResolved,Help:"Search terms"},
                {Key:"limit",Long:"limit",Short:'n',Kind:IntKind,Default:[]string{"20"},Help:"Maximum source results"},
                {Key:"tag",Long:"tag",Short:'t',Kind:StringListKind,Merge:Append,Help:"Filter by tag; repeatable"},
                {Key:"format",Long:"format",Kind:ChoiceKind,Choices:[]string{"table","json","jsonl","csv","tsv"},Default:[]string{"table"},Section:"structured-output",Help:"Stdout framing"},
            }},
            {Name:"config",Summary:"Manage configuration",Children:[]*CommandSpec{
                {Name:"show",Summary:"Show the resolved configuration",Runnable:true,Fields:[]FieldSpec{
                    {Key:"profile",Long:"profile",Kind:StringKind,Required:RequiredResolved,Environment:"ATLAS_PROFILE",Help:"Profile name"},
                    {Key:"explain",Long:"explain",Kind:BoolKind,Help:"Show value provenance"},
                }},
            }},
        }},
    }
}
EOF
cat > "$EXP/nativecli_test.go" <<'EOF'
package nativecli

import (
    "bytes"
    "encoding/json"
    "errors"
    "fmt"
    "reflect"
    "strings"
    "testing"
    "testing/quick"
)

func mustProgram(t *testing.T)*Program{t.Helper();p,err:=Compile(ExampleProgram());if err!=nil{t.Fatal(err)};return p}

func TestCompileRejectsCollision(t *testing.T){
    spec:=ProgramSpec{Name:"x",Root:&CommandSpec{Name:"x",Runnable:true,Fields:[]FieldSpec{{Key:"a",Long:"same",Kind:StringKind},{Key:"b",Long:"same",Kind:StringKind}}}}
    _,err:=Compile(spec);if err==nil||!strings.Contains(err.Error(),"collides"){t.Fatalf("expected collision, got %v",err)}
}
func TestCompileRejectsInvalidPositionalGrammar(t *testing.T){
    spec:=ProgramSpec{Name:"x",Root:&CommandSpec{Name:"x",Runnable:true,Fields:[]FieldSpec{{Key:"optional",Argument:true,Kind:StringKind},{Key:"required",Argument:true,Kind:StringKind,Required:RequiredResolved}}}}
    _,err:=Compile(spec);if err==nil||!strings.Contains(err.Error(),"required argument"){t.Fatalf("expected positional grammar error, got %v",err)}
}
func TestParseWorkedInvocation(t *testing.T){
    p:=mustProgram(t);r,err:=Parse(p,[]string{"-vc","cfg.yml","search","retry","policy","--limit=-3","-t","go","--tag","cli","--format","jsonl"});if err!=nil{t.Fatal(err)}
    if got:=strings.Join(r.Command.Path," ");got!="atlas search"{t.Fatalf("path %q",got)}
    vals,err:=Resolve(r.Command,Defaults(r.Command),SourceValues{Source:FlagSource,Assignments:r.Assignments});if err!=nil{t.Fatal(err)}
    if vals.Fields["limit"].Value!= -3{t.Fatalf("limit=%#v",vals.Fields["limit"].Value)}
    tags:=vals.Fields["tag"].Value.([]any);if !reflect.DeepEqual(tags,[]any{"go","cli"}){t.Fatalf("tags %#v",tags)}
    q:=vals.Fields["query"].Value.([]any);if !reflect.DeepEqual(q,[]any{"retry","policy"}){t.Fatalf("query %#v",q)}
}
func TestDoubleDash(t *testing.T){p:=mustProgram(t);r,err:=Parse(p,[]string{"search","--","--literal"});if err!=nil{t.Fatal(err)};if got:=r.Positionals;!reflect.DeepEqual(got,[]string{"--literal"}){t.Fatalf("%#v",got)}}
func TestSourcePrecedenceAndProvenance(t *testing.T){
    p:=mustProgram(t);c:=p.ByPath["atlas config show"]
    vals,err:=Resolve(c,Defaults(c),MapSource(ConfigSource,map[string][]string{"profile":{"team"}}),MapSource(EnvSource,map[string][]string{"profile":{"staging"}}),MapSource(FlagSource,map[string][]string{"profile":{"prod"}}));if err!=nil{t.Fatal(err)}
    v:=vals.Fields["profile"];if v.Value!="prod"{t.Fatalf("%v",v.Value)}
    got:=[]Source{};for _,s:=range v.Steps{got=append(got,s.Source)};want:=[]Source{ConfigSource,EnvSource,FlagSource};if !reflect.DeepEqual(got,want){t.Fatalf("steps %v",got)}
}
func TestRequiredResolvedCanComeFromEnv(t *testing.T){p:=mustProgram(t);c:=p.ByPath["atlas config show"];_,err:=Resolve(c,Defaults(c),MapSource(EnvSource,map[string][]string{"profile":{"prod"}}));if err!=nil{t.Fatal(err)}}
func TestRequiredCLIRejectsEnvOnly(t *testing.T){
    spec:=ExampleProgram();spec.Root.Children[1].Children[0].Fields[0].Required=RequiredCLI;p,err:=Compile(spec);if err!=nil{t.Fatal(err)};c:=p.ByPath["atlas config show"];_,err=Resolve(c,MapSource(EnvSource,map[string][]string{"profile":{"prod"}}));if err==nil||!strings.Contains(err.Error(),"command line"){t.Fatalf("%v",err)}
}
func TestUnknownFlagSuggestion(t *testing.T){p:=mustProgram(t);_,err:=Parse(p,[]string{"search","--formt","json"});var d *Diagnostic;if !errors.As(err,&d){t.Fatalf("%v",err)};if !reflect.DeepEqual(d.Suggestions,[]string{"format"}){t.Fatalf("%v",d.Suggestions)}}
func TestManifestDeterministic(t *testing.T){p1:=mustProgram(t);p2:=mustProgram(t);if !bytes.Equal(p1.Manifest,p2.Manifest){t.Fatal("manifest differs")};var v any;if err:=json.Unmarshal(p1.Manifest,&v);err!=nil{t.Fatal(err)}}
func TestHelpAndCompletionUseCompiledModel(t *testing.T){p:=mustProgram(t);c:=p.ByPath["atlas search"];text:=RenderText(BuildHelp(c,FullHelp));for _,needle:=range []string{"--format","--limit","--verbose","Usage:"}{if !strings.Contains(text,needle){t.Fatalf("missing %q\n%s",needle,text)}};comps:=Complete(p,[]string{"search","--fo"});if len(comps)!=1||comps[0].Value!="--format"{t.Fatalf("%#v",comps)}}
func TestLongSplitRoundTripProperty(t *testing.T){
    f:=func(name,value string)bool{if strings.Contains(name,"="){return true};n,v,h:=splitLong(name+"="+value);return h&&n==name&&v==value};if err:=quick.Check(f,&quick.Config{MaxCount:1000});err!=nil{t.Fatal(err)}
}
func TestDecodeIntegersProperty(t *testing.T){f:=func(x int32)bool{raw:=fmt.Sprint(x);v,err:=decodeOne(IntKind,raw,nil);return err==nil&&v==int(x)};if err:=quick.Check(f,&quick.Config{MaxCount:1000});err!=nil{t.Fatal(err)}}
EOF
cat > "$EXP/benchmark_test.go" <<'EOF'
package nativecli

import (
    "fmt"
    "testing"
)

func benchmarkCommand(n int)*Command{
    c:=&Command{Name:"bench",Path:[]string{"bench"},Runnable:true,FlagIndex:map[string]*Field{},ShortIndex:map[rune]*Field{}}
    for i:=0;i<n;i++{name:=fmt.Sprintf("flag-%04d",i);f:=&Field{FieldSpec:FieldSpec{Key:name,Long:name,Kind:StringKind}};c.FlagIndex[name]=f;c.Local=append(c.Local,f)}
    return c
}
func linearLookup(c *Command,name string)*Field{for _,f:=range c.Local{if f.Long==name{return f}};return nil}
func BenchmarkFlagLookupMap16(b *testing.B){benchMap(b,16)}
func BenchmarkFlagLookupMap64(b *testing.B){benchMap(b,64)}
func BenchmarkFlagLookupMap256(b *testing.B){benchMap(b,256)}
func BenchmarkFlagLookupMap1024(b *testing.B){benchMap(b,1024)}
func BenchmarkFlagLookupLinear16(b *testing.B){benchLinear(b,16)}
func BenchmarkFlagLookupLinear64(b *testing.B){benchLinear(b,64)}
func BenchmarkFlagLookupLinear256(b *testing.B){benchLinear(b,256)}
func BenchmarkFlagLookupLinear1024(b *testing.B){benchLinear(b,1024)}
func benchMap(b *testing.B,n int){c:=benchmarkCommand(n);name:=fmt.Sprintf("flag-%04d",n-1);b.ResetTimer();for i:=0;i<b.N;i++{if c.FlagIndex[name]==nil{b.Fatal()}}}
func benchLinear(b *testing.B,n int){c:=benchmarkCommand(n);name:=fmt.Sprintf("flag-%04d",n-1);b.ResetTimer();for i:=0;i<b.N;i++{if linearLookup(c,name)==nil{b.Fatal()}}}
func BenchmarkParseRepresentative(b *testing.B){p,_:=Compile(ExampleProgram());argv:=[]string{"-vc","cfg.yml","search","retry","policy","--limit","20","-t","go","-t","cli","--format","jsonl"};b.ResetTimer();for i:=0;i<b.N;i++{if _,err:=Parse(p,argv);err!=nil{b.Fatal(err)}}}
func BenchmarkCompileRepresentative(b *testing.B){spec:=ExampleProgram();b.ResetTimer();for i:=0;i<b.N;i++{if _,err:=Compile(spec);err!=nil{b.Fatal(err)}}}
EOF

gofmt -w "$EXP"/*.go
cd "$EXP"
go test ./...

```

<details><summary>💭 Thinking</summary>

**Implemented native CLI experiment and validated performance with Go race coverage tests**

**Inspected Glazed command runners, repository commands, and help rendering**

**Mapped Glazed dependency clusters and fetched render implementation details**

</details>

```unknown
bash -lc set -euo pipefail
OUT=/mnt/data/glazed-native-cli-thesis
AS=$OUT/assets
mkdir -p "$AS"
cat > "$AS/01-current-architecture.dot" <<'EOF'
digraph G {
  graph [rankdir=LR, bgcolor="transparent", pad=0.2, nodesep=0.35, ranksep=0.6, fontname="DejaVu Sans"];
  node [shape=box, style="rounded", fontname="DejaVu Sans", fontsize=10, margin="0.12,0.08"];
  edge [fontname="DejaVu Sans", fontsize=9];
  desc [label="CommandDescription\nSchema + Sections + Fields"];
  cobra [label="Cobra adapter\ncommand tree + pflag registration"];
  source [label="FromCobra / FromArgs\nraw CLI source"];
  merge [label="Source middleware chain\ndefault < config < env < args < flags"];
  vals [label="Values\ntyped values + parse log"];
  run [label="Bare / Writer / Glaze\ncommand execution"];
  help [label="Cobra-shaped help projection\n+ Markdown help store"];
  desc -> cobra [label="mount"];
  cobra -> source [label="read"];
  source -> merge;
  merge -> vals;
  vals -> run;
  cobra -> help;
  desc -> help [style=dashed, label="metadata"];
}
EOF
cat > "$AS/02-compiled-runtime.dot" <<'EOF'
digraph G {
  graph [rankdir=LR, bgcolor="transparent", pad=0.2, nodesep=0.4, ranksep=0.65, fontname="DejaVu Sans"];
  node [shape=box, style="rounded", fontname="DejaVu Sans", fontsize=10, margin="0.12,0.08"];
  edge [fontname="DejaVu Sans", fontsize=9];
  author [label="Mutable authoring model\nGo / YAML / JavaScript"];
  compiler [label="CompileProgram\nnormalize + validate + index"];
  program [label="Immutable Program\ncommand graph + field tables + contracts"];
  parser [label="Native token parser"];
  help [label="Help IR renderer"];
  comp [label="Completion continuation"];
  manifest [label="Versioned manifest"];
  exec [label="Invocation executor"];
  author -> compiler -> program;
  program -> parser;
  program -> help;
  program -> comp;
  program -> manifest;
  program -> exec;
}
EOF
cat > "$AS/03-parser-machine.dot" <<'EOF'
digraph G {
  graph [rankdir=LR, bgcolor="transparent", pad=0.2, nodesep=0.35, ranksep=0.55, fontname="DejaVu Sans"];
  node [shape=ellipse, fontname="DejaVu Sans", fontsize=10];
  start [label="command scope\nflags enabled"];
  flag [label="expecting\nflag value"];
  pos [label="positional-only\nmode"];
  done [shape=doublecircle, label="parsed\ninvocation"];
  error [shape=octagon, label="typed\ndiagnostic"];
  start -> start [label="subcommand / bool flag / positional"];
  start -> flag [label="non-boolean flag"];
  flag -> start [label="consume next token\n(including -3)"];
  start -> pos [label="--"];
  pos -> pos [label="any token"];
  start -> done [label="end"];
  pos -> done [label="end"];
  start -> error [label="unknown / ambiguous"];
  flag -> error [label="missing value"];
}
EOF
cat > "$AS/04-source-resolution.dot" <<'EOF'
digraph G {
  graph [rankdir=LR, bgcolor="transparent", pad=0.2, nodesep=0.35, ranksep=0.6, fontname="DejaVu Sans"];
  node [shape=box, style="rounded", fontname="DejaVu Sans", fontsize=10];
  d [label="defaults"];
  c [label="configuration"];
  e [label="environment"];
  a [label="positional arguments"];
  f [label="flags"];
  v [label="resolved value\n+ provenance trace", shape=box3d];
  d -> c [label="overridden by"];
  c -> e [label="overridden by"];
  e -> a [label="overridden by"];
  a -> f [label="overridden by"];
  d -> v [style=dashed]; c -> v [style=dashed]; e -> v [style=dashed]; a -> v [style=dashed]; f -> v [style=dashed];
}
EOF
cat > "$AS/05-command-boundaries.dot" <<'EOF'
digraph G {
  graph [rankdir=TB, bgcolor="transparent", pad=0.2, nodesep=0.45, ranksep=0.55, fontname="DejaVu Sans"];
  node [shape=box, style="rounded", fontname="DejaVu Sans", fontsize=10];
  spec [label="CommandSpec\nidentity + fields + prose + static contract"];
  compiled [label="CompiledCommand\nvalidated path + lookup tables + argument automaton"];
  inv [label="Invocation\nselected command + syntax assignments + diagnostics"];
  vals [label="ResolvedValues\ntyped values + source provenance"];
  plan [label="ExecutionPlan\nmode + output + declared effects"];
  result [label="Result\nrows / text / no output + error"];
  spec -> compiled [label="compile"];
  compiled -> inv [label="parse argv"];
  inv -> vals [label="merge sources"];
  vals -> plan [label="admit"];
  plan -> result [label="execute"];
}
EOF
cat > "$AS/06-help-ir.dot" <<'EOF'
digraph G {
  graph [rankdir=LR, bgcolor="transparent", pad=0.2, nodesep=0.4, ranksep=0.65, fontname="DejaVu Sans"];
  node [shape=box, style="rounded", fontname="DejaVu Sans", fontsize=10];
  program [label="Compiled Program"];
  docs [label="Markdown help store\nexamples + tutorials + topics"];
  ir [label="Help IR\nusage + groups + provenance + related docs"];
  quick [label="quick terminal help"];
  full [label="full reference"];
  tui [label="searchable TUI"];
  json [label="JSON describe"];
  web [label="static/web docs"];
  program -> ir;
  docs -> ir;
  ir -> quick; ir -> full; ir -> tui; ir -> json; ir -> web;
}
EOF
cat > "$AS/07-completion-continuation.dot" <<'EOF'
digraph G {
  graph [rankdir=LR, bgcolor="transparent", pad=0.2, nodesep=0.4, ranksep=0.6, fontname="DejaVu Sans"];
  node [shape=box, style="rounded", fontname="DejaVu Sans", fontsize=10];
  prefix [label="partial token sequence"];
  parser [label="incremental parser"];
  state [label="parser state\ncommand + mode + expected value"];
  expected [label="Expected(state)\nlegal continuations"];
  filter [label="prefix filter + descriptions"];
  shell [label="shell / editor / TUI"];
  prefix -> parser -> state -> expected -> filter -> shell;
}
EOF
cat > "$AS/08-migration.dot" <<'EOF'
digraph G {
  graph [rankdir=LR, bgcolor="transparent", pad=0.2, nodesep=0.35, ranksep=0.6, fontname="DejaVu Sans"];
  node [shape=box, style="rounded", fontname="DejaVu Sans", fontsize=10];
  s0 [label="0 Characterize\ncurrent behavior"];
  s1 [label="1 Compile\nframework-neutral Program"];
  s2 [label="2 Native parser\nbehind adapter interface"];
  s3 [label="3 Help + completion\nfrom Help IR"];
  s4 [label="4 Dual-run\ndifferential testing"];
  s5 [label="5 Remove Cobra\nfrom core and go.mod"];
  s0 -> s1 -> s2 -> s3 -> s4 -> s5;
}
EOF
cat > "$AS/09-evidence-boundaries.dot" <<'EOF'
digraph G {
  graph [rankdir=TB, bgcolor="transparent", pad=0.2, nodesep=0.4, ranksep=0.55, fontname="DejaVu Sans"];
  node [shape=box, style="rounded", fontname="DejaVu Sans", fontsize=10];
  source [label="Observed Glazed at pinned commit\nsource code + tests + issues"];
  model [label="Architectural reconstruction\nformal definitions and laws"];
  proto [label="Independent prototype\nstandard-library Go"];
  data [label="Experimental observations\ntests + race + benchmarks"];
  proposal [label="Proposed native runtime\nnot yet integrated"];
  source -> model;
  model -> proto;
  proto -> data;
  model -> proposal;
  data -> proposal;
}
EOF
cat > "$AS/10-synthesis.dot" <<'EOF'
digraph G {
  graph [rankdir=LR, bgcolor="transparent", pad=0.2, nodesep=0.35, ranksep=0.65, fontname="DejaVu Sans"];
  node [shape=box, style="rounded", fontname="DejaVu Sans", fontsize=10];
  one [label="one compiled semantic model"];
  parse [label="deterministic syntax"];
  resolve [label="provenance-aware resolution"];
  help [label="contextual help"];
  discover [label="machine discovery"];
  execute [label="host-owned effects"];
  one -> parse; one -> resolve; one -> help; one -> discover; one -> execute;
}
EOF
for f in "$AS"/*.dot; do dot -Tpng -Gdpi=160 "$f" -o "${f%.dot}.png"; done
ls -lh "$AS"/*.png

```

A Cobra-free prototype now passes unit, property, race, and provenance tests, with compiled lookups and structured diagnostics. Its renderer-neutral help model preserves Glazed’s existing knowledge subsystem.

<details><summary>💭 Thinking</summary>

**Planned and documented Native CLI thesis architecture, benchmarks, appendices, and compilation requirements**

</details>

```unknown
bash -lc python - <<'PY'
from pathlib import Path
p=Path('/mnt/data/glazed-native-cli-thesis/compiling-command-interfaces.md')
s=p.read_text()
print('Definitions:', s.count('**Definition '))
print('Propositions:', s.count('**Proposition '))
print('Theorems:', s.count('**Theorem '))
print('Worked examples:', s.lower().count('worked example'))
print('Counterexamples:', s.lower().count('counterexample'))
print('Exercises headings:', s.count('## Exercises'))
print('Fences:', s.count('```'))
print('Images:', s.count('!['))
for ch in ['—','–','‑','−']:
    print(repr(ch), s.count(ch))
# Replace typography dashes outside LaTeX as a conservative PDF-preflight choice.
s=s.replace('—',' - ').replace('–','-').replace('‑','-')
p.write_text(s)
print('after bytes',len(s))
PY
# Check image references
python - <<'PY'
import re
from pathlib import Path
p=Path('/mnt/data/glazed-native-cli-thesis/compiling-command-interfaces.md')
base=p.parent
missing=[]
for ref in re.findall(r'!\[[^\]]*\]\(([^)]+)\)',p.read_text()):
    if not (base/ref).exists(): missing.append(ref)
print('missing images',missing)
PY
# Show definition list and chapter headers for audit
grep -n '^#\|^\*\*Definition' /mnt/data/glazed-native-cli-thesis/compiling-command-interfaces.md | sed -n '1,240p'

```

<details><summary>💭 Thinking</summary>

**Auditing the thesis**

I’m checking the remaining rendered pages, preflighting the PDF, and verifying that the Markdown, diagrams, experiments, and bibliography remain consistent before I finalize both deliverables.

**Audited the thesis**

</details>

```unknown
bash -lc sed -n '1,260p' /home/oai/skills/pdfs/SKILL.md
```

<details><summary>💭 Thinking</summary>

**Audited thesis PDFs, visuals, metadata, validation, source files, and archives**

</details>

The thesis draft is complete; final auditing now checks reproducibility and PDF layout. Crucially, requiredness remains post-resolution, while introspection modes preserve their intentional bypass semantics.

```json
{"paths":["GitHub"],"query":"fetch"}
```

```json
{"paths":["GitHub"],"query":"search"}
```

```json
{"uri":"/response/turn59","query":"\"path\":\"pkg/cmds"}
```

```json
{"uri":"/response/turn59","query":"pkg/cmds"}
```

```json
{"uri":"/response/turn98","start_line":40,"num_lines":10}
```

```json
{"uri":"/response/turn107","query":"required short"}
```

```json
{"uri":"/response/turn107","query":"required"}
```

# Compiling Command Interfaces

The doctoral-style thesis is complete in Markdown and PDF. It contains **83 pages**, approximately **20,000 source words**, four major chapters, 12 diagrams, formal definitions and laws, worked examples, counterexamples, exercises, selected solutions, a glossary, migration checklists, a compatibility questionnaire, a pinned source-evidence map, and a bibliography.

The central finding is that Cobra should not be replaced by another isolated flag loop. Glazed already owns most of a typed language runtime: frontend-neutral command descriptions and effect interfaces, typed field definitions and codecs, provenance-bearing values, multi-source resolution, and a runner that operates on resolved values. fileciteturn67file0L2-L2 fileciteturn114file0L2-L2 fileciteturn103file0L2-L2 The remaining Cobra dependency is concentrated in command mounting, token and pflag adaptation, completion integration, and portions of the help adapter. fileciteturn70file0L2-L2 fileciteturn72file0L2-L2

The proposed replacement is a whole-program compiler:

```text
mutable Glazed command definitions
    -> CompileCommandSet
    -> immutable CommandCatalog
         -> native parser
         -> source resolver
         -> completion
         -> help and documentation
         -> machine manifest
         -> transitional Cobra adapter
         -> existing command runner
```

The help proposal retains Glazed’s authored Markdown corpus and existing searchable Bubble Tea interface rather than replacing them. It adds stable semantic identities, catalog-derived reference facts, contextual diagnostics, and separate `help`, `describe`, `explain`, and `plan` operations. fileciteturn100file0L2-L2

## Deliverables

- [Download the Markdown thesis](sandbox:/mnt/data/glazed-native-thesis/compiling-command-interfaces.md)
- [Download the PDF thesis](sandbox:/mnt/data/glazed-native-thesis/compiling-command-interfaces.pdf)
- [Download the complete thesis source bundle](sandbox:/mnt/data/glazed-native-thesis/compiling-command-interfaces-source.zip)
- [Download the native CLI research prototype](sandbox:/mnt/data/glazed-native-thesis/glazed-native-prototype.zip)
- [Download SHA-256 checksums](sandbox:/mnt/data/glazed-native-thesis/SHA256SUMS.txt)

## Experimental result

The included standard-library-only Go prototype implements catalog compilation, collision detection, native long and clustered-short parsing, `--`, macro aliases, typed decoding, source precedence with provenance, post-merge required validation, residual-state completion, Markdown help, JSON manifests, and structured diagnostics.

It passes:

```text
go test ./... -race -cover -count=1
go vet ./...
```

The core package reports **73.6% statement coverage**. On the synthetic 100-command, 40-field workload:

| Operation | Median |
|---|---:|
| Compile catalog | 3.407 ms |
| Parse invocation | 1.567 microseconds |
| Complete partial invocation | 5.861 microseconds |

These measurements establish architectural feasibility only. The prototype is not presented as a production-ready or drop-in Glazed implementation.

