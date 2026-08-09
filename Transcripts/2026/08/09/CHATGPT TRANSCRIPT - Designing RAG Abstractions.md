# Designing RAG Abstractions

- URL: https://chatgpt.com/c/6a75e142-f058-83ea-a9ad-8132656dbf12
- Created: 2026-08-07T13:44:35.710Z

---

> we are building a rag engine, both indexing / optimization / querying.
>
> We have started building two common packages: ragkit and ragopt, one for general rag functionality and querying, one for optimization loop management. We also have a GEC chat for admins, a rag-ttc optimization and querying pipelines (work in progress for a rag-ttc chat for admins), a TTC garden chat assistant (in ttc-design-system) and probably a fair bunch of overlapping functionality and unclear abstractions.
>
> Go over ragkit and ragopt in particular, looking at how they can be used or parallel functionality in the more pragmatic existing applied implementations of them, and design a shared set of abstractions and APIs and packages that are grounded in fundamentals (think category theoretical structures, provable correct kernels, etc...) and how the current system can be modified to use them or nhow they relate.
>
> This is about studying possible designs, so the write ups need to be clear, instructive, thought out.
>
> Write them up as a doctoral thesis / textbook from that thesis.

<details><summary>💭 Thinking</summary>

**Inspecting the archive**

I’m examining the uploaded repository, identifying its main packages, documentation, tests, and architecture. I’ll then structure the findings into a rigorous doctoral-style thesis and practical textbook narrative.

</details>

```unknown
bash -lc cat /home/oai/skills/docx/SKILL.md && printf '\n---PDF---\n' && cat /home/oai/skills/pdfs/SKILL.md
```

I’ll map the repository and concrete RAG/optimization flows, compare overlapping abstractions, then develop a formally grounded thesis with executable APIs and migration guidance.

<details><summary>💭 Thinking</summary>

**Inspected and safely extracted DOCX and PDF archive contents**

</details>

```unknown
bash -lc for d in ragkit ragopt rag-ttc gec ttc-design-system; do echo "===== $d ====="; find "/mnt/data/rag_study/$d" -maxdepth 1 -type f -printf '%f\n' | sort; echo; done
printf '\n--- READMES / module files ---\n'
for f in \
 /mnt/data/rag_study/ragkit/README.md \
 /mnt/data/rag_study/ragkit/go.mod \
 /mnt/data/rag_study/ragopt/README.md \
 /mnt/data/rag_study/ragopt/AGENT.md \
 /mnt/data/rag_study/ragopt/go.mod \
 /mnt/data/rag_study/rag-ttc/README.md \
 /mnt/data/rag_study/rag-ttc/AGENT.md \
 /mnt/data/rag_study/rag-ttc/go.mod \
 /mnt/data/rag_study/gec/README.md \
 /mnt/data/rag_study/gec/go.mod \
 /mnt/data/rag_study/ttc-design-system/AGENTS.md; do
  echo "===== $f ====="; sed -n '1,240p' "$f"; echo;
done
```

<details><summary>💭 Thinking</summary>

**Inspected repositories, dependencies, versions, and Go package architecture**

</details>

```unknown
bash -lc for f in \
 /mnt/data/rag_study/ragkit/rag/types.go \
 /mnt/data/rag_study/ragkit/rag/components.go \
 /mnt/data/rag_study/ragkit/rag/validate.go \
 /mnt/data/rag_study/ragkit/rag/ordering.go \
 /mnt/data/rag_study/ragkit/rag/evidence_identity.go \
 /mnt/data/rag_study/ragkit/rag/usage.go \
 /mnt/data/rag_study/ragkit/rag/target.go; do
 echo "===== ${f#/mnt/data/rag_study/} ====="; nl -ba "$f" | sed -n '1,280p'; echo; done
```

Five codebases form the empirical basis. A key fault line is duplicated RAG substrate in `ragkit` and `rag-ttc`, creating competing sources of truth before optimization enters.

<details><summary>💭 Thinking</summary>

**Mapping the repository**

I’m organizing the codebase into modules, dependency relationships, and conceptual layers. I’ll connect those findings to category theory, probabilistic kernels, algebraic effects, and typed software architecture in the finished thesis.

**Mapped the repository structure**

</details>

```unknown
bash -lc f=/mnt/data/rag_study/ragopt/ttmp/2026/08/06/RAGOPT-001--reusable-reproducible-self-optimization-harness/design-doc/01-ragopt-intern-guide-to-a-reusable-evidence-gated-optimization-harness.md
for r in '39,180' '205,388' '389,722' '724,1006' '1045,1187' '1378,1493'; do echo "--- $r ---"; sed -n "${r}p" "$f"; done
```

<details><summary>💭 Thinking</summary>

**Assessing implementation evidence**

I’m using the inventory to distinguish shared architecture from meaningful divergence. The analysis will emphasize typed RAG contracts, deterministic ordering, resumable execution, content-addressed artifacts, and the specific differences between related repositories.

**Synthesizing architecture**

I’m framing the thesis around experimental optimization, evidence custody, and runtime integrity. The central finding is architectural drift: related systems share abstractions, but semantics and operational responsibilities are not consistently unified.

**Assessed implementation evidence and synthesized architecture**

</details>

```unknown
bash -lc find /mnt/data/rag_study -maxdepth 2 -type f | head -50 && echo '---' && du -sh /mnt/data/rag_study/* && echo '---' && ls -l /mnt/data | sed -n '1,30p'
```

<details><summary>💭 Thinking</summary>

**Inspected and compared RAG architectures, implementations, documentation, dependencies, and test metrics**

</details>

```json
{"search_query":[{"q":"site:dl.acm.org Notions of Computation and Monads Moggi 1991 PDF"},{"q":"site:research.google/pubs The Design and Implementation of Glasgow Haskell Compiler arrows Hughes 2000 generalising monads"},{"q":"site:homepages.inf.ed.ac.uk plotkin algebraic operations and generic effects pdf"},{"q":"site:cambridge.org Categories for the Working Mathematician monoidal categories formal semantics"}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Searched 3 websites**

</details>

```unknown
bash -lc cd /mnt/data/rag_study
for f in ragkit/README.md ragkit/boundary_test.go ragkit/go.mod ragopt/README.md ragopt/go.mod ragopt/AGENT.md rag-ttc/go.mod gec/go.mod ttc-design-system/backend/go.mod; do echo "===== $f ====="; nl -ba "$f" | sed -n '1,240p'; done
```

<details><summary>💭 Thinking</summary>

**Analyzed RAG repositories, APIs, documentation, overlap, and cache correctness**

</details>

```json
{"search_query":[{"q":"site:rfc-editor.org RFC 8785 JSON Canonicalization Scheme"},{"q":"site:rfc-editor.org RFC 8949 deterministic encoding CBOR"},{"q":"site:go.dev encoding/json map keys sorted documentation"}],"response_length":"long"}
```

The deeper duplication concerns identity, publication, resumability, ordering, and evidence provenance; these belong in verified kernels. Product layers should own retrieval routing while parameterizing authorization and tool policy.

<details><summary>💭 Thinking</summary>

**Searched 3 websites**

</details>

```unknown
bash -lc ls -la /mnt/data/rag_study && find /mnt/data/rag_study -maxdepth 2 -type f | sed 's#^#/##' | head -100
```

<details><summary>💭 Thinking</summary>

**Inspected RAG study files before thesis writing**

</details>

```json
{"search_query":[{"q":"Green Karvounarakis Tannen Provenance Semirings PODS 2007 PDF"},{"q":"Paterson a new notation for arrows ICFP 2001 PDF"},{"q":"McBride Paterson Applicative Programming with Effects PDF"},{"q":"Abramsky Coecke categorical quantum mechanics symmetric monoidal category process theory PDF"}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Searched 30 websites**

</details>

```unknown
bash -lc cat /home/oai/skills/docx/SKILL.md && printf '\n---PDF SKILL---\n' && cat /home/oai/skills/pdfs/SKILL.md
```

<details><summary>💭 Thinking</summary>

**Inspected RAG documentation, code, metrics, and deliverable metadata**

</details>

```json
{"search_query":[{"q":"site:dl.acm.org \"A new notation for arrows\" DOI"},{"q":"site:sciencedirect.com \"Generalising monads to arrows\" DOI"},{"q":"site:dl.acm.org \"Provenance semirings\" DOI"},{"q":"site:dl.acm.org \"Reciprocal rank fusion\" DOI"}],"response_length":"medium"}
```

<details><summary>💭 Thinking</summary>

**Searched 2 websites**

</details>

```json
import pandas as pd, os, json, textwrap, math
ov = pd.read_csv('/mnt/data/rag_study/ragkit_ragttc_overlap.csv')
ov['status'].value_counts(), len(ov)

```

<details><summary>💭 Thinking</summary>

**Calculated overlap status counts**

</details>

```unknown
bash -lc awk -F, 'NR>1{c[$2]++} END{for(k in c) print k,c[k]}' /mnt/data/rag_study/ragkit_ragttc_overlap.csv && wc -l /mnt/data/rag_study/ragkit_ragttc_overlap.csv
```

<details><summary>💭 Thinking</summary>

**Counted CSV categories and listed files across containers**

</details>

```unknown
bash -lc set -euo pipefail
rm -rf /mnt/data/rag_study /mnt/data/rag_output /mnt/data/rag_work
mkdir -p /mnt/data/rag_study /mnt/data/rag_output /mnt/data/rag_work
python - <<'PY'
from pathlib import Path
from zipfile import ZipFile
src=Path('/mnt/data/rag-ttc(2).zip')
out=Path('/mnt/data/rag_study')
with ZipFile(src) as z:
    for info in z.infolist():
        name=info.filename
        p=Path(name)
        if p.is_absolute() or '..' in p.parts:
            raise SystemExit(f'unsafe path: {name}')
        target=out/p
        if info.is_dir():
            target.mkdir(parents=True, exist_ok=True)
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            with z.open(info) as r, open(target,'wb') as w:
                while True:
                    b=r.read(1024*1024)
                    if not b: break
                    w.write(b)
print('extracted')
PY
find /mnt/data/rag_study -maxdepth 2 -type d -print | sort | head -40

```

<details><summary>💭 Thinking</summary>

**Checking Document Creation Tools**

</details>

```unknown
bash -lc cat > /mnt/data/rag_work/make_diagrams.py <<'PY'
from pathlib import Path
import subprocess, textwrap, csv
import matplotlib.pyplot as plt
import numpy as np

OUT=Path('/mnt/data/rag_work/figures')
OUT.mkdir(parents=True, exist_ok=True)

NAVY='#17324d'; BLUE='#2d5f87'; TEAL='#2e7d77'; LIGHT='#edf3f6'; MID='#c7d6df'; ORANGE='#c06b2c'; RED='#9f3a38'; GREEN='#3f7d4a'; GRAY='#5f6b73'; WHITE='#ffffff'; DARK='#1f2933'

def dot(name, src):
    path=OUT/f'{name}.dot'
    path.write_text(src)
    subprocess.run(['dot','-Tpng','-Gdpi=220',str(path),'-o',str(OUT/f'{name}.png')],check=True)
    subprocess.run(['dot','-Tsvg',str(path),'-o',str(OUT/f'{name}.svg')],check=True)

base='''
digraph G {
  graph [fontname="Lato", bgcolor="transparent", pad="0.25", nodesep="0.45", ranksep="0.65", splines=ortho];
  node [fontname="Lato", fontsize=11, shape=box, style="rounded,filled", color="%s", fontcolor="%s", fillcolor="%s", penwidth=1.2, margin="0.12,0.08"];
  edge [fontname="Lato", fontsize=9.5, color="%s", fontcolor="%s", arrowsize=0.7, penwidth=1.2];
'''%(BLUE,DARK,LIGHT,GRAY,GRAY)

# 1 current topology
dot('01_current_topology', base+f'''
  rankdir=LR;
  subgraph cluster_common {{ label="Common packages"; color="{MID}"; style="rounded,dashed";
    ragkit [label="ragkit\nRAG types, indexes, retrieval, answering, flow", fillcolor="{LIGHT}"];
    ragopt [label="ragopt\ncandidates, paired evaluation, gates, run custody", fillcolor="#f0f6ef"];
  }}
  subgraph cluster_apps {{ label="Applied systems"; color="{MID}"; style="rounded,dashed";
    gec [label="GEC admin chat\nimports ragkit; owns eval/sweep/judge", fillcolor="#eef4fb"];
    ragttc [label="rag-ttc\ncontains older copied RAG core + TTC application code", fillcolor="#fff0e6", color="{ORANGE}", penwidth=2];
    garden [label="TTC Garden assistant\nimports rag-ttc through local replace; owns calibration/widgets", fillcolor="#fff8e8"];
  }}
  ragkit -> gec [label="runtime dependency"];
  ragopt -> ragttc [label="tool-eval adapter only"];
  ragttc -> garden [label="runtime dependency"];
  ragttc -> ragkit [label="historical extraction, not a live dependency", style=dashed, color="{RED}", fontcolor="{RED}", dir=both, arrowtail=none];
  gec -> ragopt [label="not yet integrated", style=dotted, color="{RED}"];
  garden -> ragopt [label="parallel calibration loop", style=dotted, color="{RED}"];
}}''')

# 2 scale chart
metrics=[]
with open('/mnt/data/rag_work/analysis_metrics.csv') as f:
    for row in csv.DictReader(f): metrics.append(row)
projects=[r['project'].replace('ttc-design-system/backend','TTC Garden backend') for r in metrics]
go_files=[int(r['go_files']) for r in metrics]
tests=[int(r['test_functions']) for r in metrics]
y=np.arange(len(projects))
fig,ax=plt.subplots(figsize=(10.5,5.0))
h=0.34
ax.barh(y-h/2,go_files,h,label='Go files',color=BLUE)
ax.barh(y+h/2,tests,h,label='Test functions',color=TEAL)
ax.set_yticks(y,projects)
ax.invert_yaxis()
ax.set_xlabel('Count')
ax.set_title('Repository scale in the supplied snapshot')
ax.grid(axis='x',alpha=.25)
ax.legend(frameon=False,loc='lower right')
for i,v in enumerate(go_files): ax.text(v+6,i-h/2,str(v),va='center',fontsize=9)
for i,v in enumerate(tests): ax.text(v+6,i+h/2,str(v),va='center',fontsize=9)
fig.tight_layout()
fig.savefig(OUT/'02_repository_scale.png',dpi=220,bbox_inches='tight')
fig.savefig(OUT/'02_repository_scale.svg',bbox_inches='tight')
plt.close(fig)

# 3 overlap heatmap
rows=['Semantic identity','Immutable artifacts','Execution/retry/cache','Retrieval & ranking','Answer contracts','Evaluation metrics','Paired comparison & gates','Session evidence','Admin/UI composition']
cols=['ragkit','ragopt','rag-ttc','GEC','Garden']
# 0 none,1 adapter/use,2 owns/implements,3 duplicate/parallel
M=np.array([
 [2,2,3,1,1],
 [2,2,3,2,2],
 [2,2,3,2,2],
 [2,0,3,2,2],
 [2,1,3,2,2],
 [2,1,3,3,3],
 [0,2,2,3,3],
 [0,0,2,2,2],
 [0,0,2,2,2],
])
from matplotlib.colors import ListedColormap
cmap=ListedColormap(['#f7f8f9','#dce8ef','#92b6c9','#e7a56d'])
fig,ax=plt.subplots(figsize=(10.5,6.0))
im=ax.imshow(M,cmap=cmap,vmin=0,vmax=3,aspect='auto')
ax.set_xticks(np.arange(len(cols)),cols)
ax.set_yticks(np.arange(len(rows)),rows)
ax.set_title('Semantic ownership and overlap')
labels={0:'-',1:'uses',2:'owns',3:'parallel'}
for i in range(M.shape[0]):
    for j in range(M.shape[1]):
        ax.text(j,i,labels[int(M[i,j])],ha='center',va='center',fontsize=8.5,color=DARK)
ax.set_xticks(np.arange(-.5,len(cols),1),minor=True); ax.set_yticks(np.arange(-.5,len(rows),1),minor=True)
ax.grid(which='minor',color='white',linewidth=1.5); ax.tick_params(which='minor',bottom=False,left=False)
fig.tight_layout()
fig.savefig(OUT/'03_overlap_matrix.png',dpi=220,bbox_inches='tight')
fig.savefig(OUT/'03_overlap_matrix.svg',bbox_inches='tight')
plt.close(fig)

# 4 compositional model
dot('04_compositional_model', base+f'''
  rankdir=TB;
  values [shape=record, label="Typed immutable values|Document -> Chunk -> Representation -> Hit -> Evidence -> Answer", fillcolor="#eef4fb"];
  plan [label="Free typed operation plan\nsequential composition ;  parallel tensor x  explicit choice", fillcolor="#eef6f5", color="{TEAL}", penwidth=2];
  spec [label="Static specification\nsemantic identity | effects | determinism | resources | schemas", fillcolor="#f4f7f9"];
  exec [label="Execution interpreter\ncache, retry, concurrency, budgets"];
  audit [label="Audit interpreter\nprovenance, artifacts, observations"];
  test [label="Law/test interpreter\ndeterministic fixtures, property checks"];
  graph [label="Planning interpreter\ngraph, cost preflight, capability check"];
  values -> plan [label="objects and morphisms"];
  plan -> spec [label="inspect without running"];
  spec -> exec; spec -> audit; spec -> test; spec -> graph;
  exec -> outcome [label="produces"];
  audit -> outcome;
  outcome [label="Outcome[T]\nvalue OR attributable failure\n+ artifact references + observations", fillcolor="#f0f6ef", color="{GREEN}"];
}}''')

# 5 proposed module topology
dot('05_proposed_topology', base+f'''
  rankdir=TB;
  kernel [label="evidencekit (provisional)\ncanon | identity | artifact | ordered | outcome | observe | op | ledger | lawtest", fillcolor="#e8f2f0", color="{TEAL}", penwidth=2.2];
  ragkit [label="ragkit\ncorpus | representation | index | retrieve | answer | eval\nbackend adapters in replaceable packages", fillcolor="#edf3f8", color="{BLUE}", penwidth=1.8];
  ragopt [label="ragopt\ncandidate | eval | compare | gate | report | runstore", fillcolor="#eef6eb", color="{GREEN}", penwidth=1.8];
  ragbuild [label="ragbuild (only after two adopters)\nbuild registry | lifecycle | activation | rollback", fillcolor="#f8f5ec"];
  ttc [label="TTC product packages\nttcrag | toolanswer | toolconfig | product facts | providers"];
  gec [label="GEC product adapter\nauthorization | synonyms | judge | admin chat"];
  garden [label="Garden application\nwidgets | session runtime | product release pair"];
  experiments [label="Product experiment commands\nArm adapters + native artifacts"];
  kernel -> ragkit; kernel -> ragopt; kernel -> ragbuild;
  ragkit -> ragbuild;
  ragkit -> ttc; ragkit -> gec;
  ttc -> garden;
  ragopt -> experiments;
  ttc -> experiments [style=dashed]; gec -> experiments [style=dashed]; garden -> experiments [style=dashed];
  ragbuild -> gec [label="optional coordinator", style=dashed]; ragbuild -> ttc [style=dashed];
}}''')

# 6 build lifecycle
dot('06_build_lifecycle', base+f'''
  rankdir=LR;
  requested [label="requested"];
  snapshot [label="snapshotting"];
  extract [label="extracting"];
  represent [label="representing"];
  embed [label="embedding"];
  assemble [label="assembling"];
  verify [label="verifying", fillcolor="#eef6f5", color="{TEAL}"];
  evaluate [label="evaluating"];
  await [label="awaiting activation"];
  active [label="active", fillcolor="#eef6eb", color="{GREEN}"];
  rejected [label="rejected", fillcolor="#fbeeee", color="{RED}"];
  failed [label="failed/cancelled", fillcolor="#fbeeee", color="{RED}"];
  rollback [label="rolled back"];
  requested->snapshot->extract->represent->embed->assemble->verify->evaluate->await->active;
  evaluate->rejected;
  active->rollback;
  requested->failed [style=dotted]; snapshot->failed [style=dotted]; extract->failed [style=dotted]; represent->failed [style=dotted]; embed->failed [style=dotted]; assemble->failed [style=dotted]; verify->failed [style=dotted]; evaluate->failed [style=dotted]; await->failed [style=dotted];
}}''')

# 7 query trust boundary
dot('07_query_trust_boundary', base+f'''
  rankdir=LR;
  subject [label="Subject + server-owned scopes", fillcolor="#eef4fb"];
  auth [label="Authorization / partition selection\nfail closed", fillcolor="#fbeeee", color="{RED}", penwidth=2];
  search [label="Local lexical/vector search"];
  fuse [label="Collapse + fuse + hydrate"];
  filter [label="Authorized candidate set\nverified source lineage", fillcolor="#eef6f5", color="{TEAL}"];
  remote [label="Remote reranker / model\nTRUST BOUNDARY", fillcolor="#fff0e6", color="{ORANGE}", penwidth=2];
  context [label="Context policy + citation labels"];
  gen [label="Generation"];
  contract [label="Grounding contract kernel", fillcolor="#eef6eb", color="{GREEN}"];
  trace [label="Typed query trace + artifact refs"];
  subject->auth->search->fuse->filter->remote->context->gen->contract->trace;
  auth->filter [label="policy identity", style=dashed];
}}''')

# 8 optimization loop
dot('08_optimization_loop', base+f'''
  rankdir=LR;
  diagnose [label="Diagnose\nproduct-owned"];
  propose [label="Propose one mutation\nhuman or product-owned"];
  validate [label="Validate candidate\nexactly one mutable asset", fillcolor="#eef6f5", color="{TEAL}"];
  evaluate [label="Paired evaluation\ncase x repeat x arm"];
  compare [label="Strict comparison\nno dropped failures"];
  gate [label="Lexicographic gates\nhard -> target -> regressions -> cost", fillcolor="#eef6eb", color="{GREEN}"];
  report [label="Promotion evidence\nplan cannot deploy"];
  human [label="Human review / Git promotion", fillcolor="#fff8e8", color="{ORANGE}"];
  deploy [label="Activation / rollback\noutside ragopt"];
  diagnose->propose->validate->evaluate->compare->gate->report->human->deploy;
  report->diagnose [label="next-cycle evidence", style=dashed];
}}''')

# 9 identity strata
dot('09_identity_strata', base+f'''
  rankdir=TB;
  semantic [label="Semantic plan identity\nwhat can affect meaning\nmodels, prompts, corpus, policies, schemas", fillcolor="#eef6f5", color="{TEAL}"];
  material [label="Material artifact identity\nexact canonical bytes and Merkle links", fillcolor="#edf3f8", color="{BLUE}"];
  execution [label="Execution identity\nrun ID, attempt, workers, host, timestamps", fillcolor="#f4f5f6"];
  release [label="Release identity\nselected artifacts + activation generation", fillcolor="#fff8e8", color="{ORANGE}"];
  semantic -> material [label="plan may produce one or more exact artifacts"];
  material -> release [label="human-reviewed selection"];
  execution -> material [label="records how produced", style=dashed];
  execution -> semantic [label="must not contaminate cache/plan ID", style=dotted, color="{RED}", fontcolor="{RED}", arrowhead=tee];
}}''')

# 10 migration roadmap
dot('10_migration_roadmap', base+f'''
  rankdir=LR;
  w0 [label="0. Baseline\nbehavioral fixtures\nimport graph"];
  w1 [label="1. Kernel\ncanonical identity\ntotal order\nartifact refs"];
  w2 [label="2. ragkit facade\noperation plans\nquery trace"];
  w3 [label="3. rag-ttc hard cut\nremove copied core"];
  w4 [label="4. GEC -> ragopt\neval/sweep adapter"];
  w5 [label="5. Garden cutover\nragkit + ragopt calibration"];
  w6 [label="6. Build/release\nshared coordinator after proof"];
  w7 [label="7. Cleanup\nremove shims\nmajor versions"];
  w0->w1->w2->w3->w4->w5->w6->w7;
}}''')

print('created', len(list(OUT.glob('*.png'))), 'PNG figures')
PY
python /mnt/data/rag_work/make_diagrams.py
ls -lh /mnt/data/rag_work/figures/*.png
```

<details><summary>💭 Thinking</summary>

**Structuring the thesis**

I’m consolidating the repository evidence into a formal architecture: a verified evidence kernel, `ragkit` as the RAG semantics layer, and `ragopt` as the domain-neutral experiment spine, with deployment kept separate.

</details>

```unknown
bash -lc ls -R /mnt/data/rag_work | sed -n '1,220p' && printf '\n--- thesis tail ---\n' && tail -n 120 /mnt/data/rag_work/thesis.md
```

<details><summary>💭 Thinking</summary>

**Inspected thesis sources and drafted RAG architecture documentation and diagrams**

</details>

```unknown
bash -lc cat >> /mnt/data/rag_work/thesis.md <<'EOF'

# Part IV. Applied mappings and migration

# 18. GEC: from a pragmatic knowledge service to a verified query application

## 18.1 What GEC already gets right

GEC is the most direct consumer of `ragkit` in the supplied snapshot. Its `internal/knowledge` package opens an immutable index bundle, reconstructs a query-side embedder from the vector manifest when necessary, loads verified source documents, and separates the shared immutable service from per-session evidence state. Its internal `SearchRequest` makes `AccessScopes`, `SourceRoles`, and channel selection server-owned values. This is a strong application boundary: the model can ask to search, but it does not manufacture its own authority.

GEC also contains several mechanisms that should inform, but not be moved wholesale into, the shared RAG layer:

- curated lexical synonym expansion applies only to the BM25 channel;
- hybrid retrieval fuses lexical and vector rankings before optional reranking;
- reranker failure degrades to the fused ranking rather than failing the serving request;
- reranker order is blended with the prior fused order by a second reciprocal-rank fusion;
- the reranker receives title or heading context in addition to raw chunk text;
- source-role and access-scope filters are explicit;
- a per-session evidence ledger records what the model has actually seen;
- product-specific tools and UI projections determine how evidence appears to administrators.

These are not signs that `ragkit` is too weak. They are examples of application policy assembled from shared mechanisms. The architecture should make this composition more explicit and more inspectable without absorbing GEC policy into a universal search service.

## 18.2 Current-to-target ownership map

| Current GEC mechanism | Current location | Target owner | Reason |
|---|---|---|---|
| Bundle open and verification | `internal/knowledge/service.go` plus `ragkit/indexbundle` | `ragkit/index` with thin GEC adapter | RAG artifact semantics are shared; configuration resolution is product-owned |
| Lexical, vector, collapse, RRF | `internal/knowledge/service.go` plus `ragkit/retrieval` | `ragkit/retrieve` | These are domain-level retrieval operations |
| Curated synonym groups | `internal/knowledge/synonyms.go` | GEC | Vocabulary is corpus and product policy |
| Access scopes and source roles | `internal/knowledge` | GEC policy compiled into a `ragkit` filter capability | Authorization semantics are application-owned |
| Reranker endpoint and document composition | `internal/knowledge/rerank*.go` | GEC adapter; composition declared in query-plan identity | Provider and presentation text are deployment policy |
| Reranker fallback | `internal/knowledge/service.go` | GEC query policy using shared explicit outcomes | Degradation is a serving decision, not a universal rule |
| Session evidence ledger | `internal/knowledge/evidence.go` and web runtime | GEC, implemented over `evidencekit/ledger` | Session meaning and retention are product-owned; reducer mechanics are shared |
| Eval cases, judge, and sweep | `internal/knowledge/eval.go`, `judge.go`, `sweep.go` | GEC evaluator plus `ragopt` custody | Native labels and judging remain GEC-specific; run pairing and gates are shared |
| Tool result schema | `internal/knowledge/tool.go` | GEC | It is an application protocol |
| Admin chat and projections | `internal/webchat`, projection packages | GEC | UI, authentication, and conversational state are not RAG-core concerns |

The target does not eliminate GEC's `internal/knowledge` package. It changes that package from a second retrieval orchestrator into a compiler and adapter around explicit `ragkit` plans.

## 18.3 A GEC query profile

A useful application-level configuration is a value that can be compiled into a subject-bound query plan:

```go
type QueryProfile struct {
    Release          identity.ID
    LexicalTopK      int
    VectorTopK       int
    RankConstant     ordered.Score
    VectorWeight     ordered.Score
    SynonymAsset     artifact.Ref
    Reranker         *RerankerProfile
    RerankPool       int
    ContextPolicy    ragkit.ContextPolicy
    Degradation      DegradationPolicy
}

type RerankerProfile struct {
    Adapter          identity.ID
    Model            identity.ID
    TextComposition  identity.ID
    CachePolicy      identity.ID
}
```

The profile is not itself authority. It is combined with a server-derived subject and authorization policy:

```go
type SubjectQuery struct {
    Subject      auth.Subject
    Query        ragkit.Query
    AccessScopes []Scope
    SourceRoles  []SourceRole
}

func Compile(
    profile QueryProfile,
    request SubjectQuery,
    opened ragkit.Release,
) (op.Plan[struct{}, GECAnswer], error)
```

Compilation checks that the release named by the profile is the release actually opened by the process, the synonym asset resolves to the exact recorded bytes, requested roles are subsets of server policy, and all source-disclosing stages occur after authorization. The compiled plan can then be rendered for an administrator and identified independently of execution concurrency or retry settings.

## 18.4 Move authorization before remote disclosure

The current fixed over-fetch strategy ranks a bounded global candidate set and filters it afterward. It prevents unauthorized chunks from being returned to the model so long as no remote component receives source text before filtering. It does not prove completeness for the authorized subset. A relevant authorized result can be absent because unauthorized candidates consumed the bounded prefix.

The migration should make the retrieval capability explicit:

```go
type SearchCapabilities struct {
    MetadataPrefilter bool
    Partitioned       bool
    ExhaustiveLocal   bool
}
```

GEC should prefer, in order:

1. backend metadata prefiltering by scope and source role;
2. physically or logically partitioned indexes selected by server authority;
3. exhaustive local retrieval followed by local authorization;
4. bounded over-fetch only as a documented degraded capability.

The query compiler rejects a plan that sends source text to a remote reranker before an `AuthorizationCertificate` has been produced for every candidate. This makes a security property structural rather than dependent on service-method ordering.

The certificate can remain local and compact:

```go
type AuthorizationCertificate struct {
    SubjectID    identity.ID
    PolicyID     identity.ID
    ReleaseID    identity.ID
    EvidenceIDs []identity.ID
    Epoch        uint64
    MAC          []byte
}
```

A remote-disclosure adapter verifies that the certificate binds exactly the evidence being serialized. It need not understand GEC scope strings; it verifies a typed decision made by the GEC policy engine.

## 18.5 Preserve the GEC reranking policy as policy

GEC's current reranker behavior embodies three distinct decisions:

1. prepare a richer reranker document from heading context and chunk body;
2. treat endpoint failure as a recoverable stage outcome;
3. blend reranker rank with fused retrieval rank rather than replacing it.

These should be represented separately. The shared RAG package can offer `PrepareRerankCandidates`, `Rerank`, and `FuseRankings`. GEC's profile selects the composition and fallback:

```go
reranked := op.Then(authorized,
    op.Recover(
        ragkit.Rerank(rerankerSpec),
        GECFallbackUseFused,
    ),
)
final := ragkit.Fuse(
    map[string]ragkit.Ranking{
        "retrieval": fused,
        "reranker":  reranked,
    },
    blendSpec,
)
```

`Recover` should not erase failure. The output is a success-with-warning or a typed degraded result whose observation contains the failed operation ID, failure class, attempted provider, and selected fallback. Evaluation can then gate degradation rate even when serving remains available.

The text-composition identity must be part of the reranker operation specification. Changing title-prefix behavior changes the semantic input to the model and therefore creates a new cache epoch. A source-code comment is not a sufficient identity mechanism.

## 18.6 GEC evidence ledgers

The per-session evidence ledger has a different purpose from an experiment ledger. It records what evidence labels are available to the model and may enforce bounded context or citation validity. It should remain GEC-owned, but its storage and reducer can use `evidencekit/ledger`.

A minimal event vocabulary is:

```go
type EvidenceEvent interface{ isEvidenceEvent() }

type SearchAdmitted struct {
    QueryID       identity.ID
    Evidence      []ragkit.SourceEvidenceRef
    Authorization identity.ID
}

type EvidenceDisclosed struct {
    TurnID     identity.ID
    EvidenceID identity.ID
    Label      string
}

type EvidenceCited struct {
    TurnID     identity.ID
    EvidenceID identity.ID
    Label      string
}
```

The pure reducer enforces label uniqueness within a session generation, prevents citation of undisclosed evidence, and computes a bounded view for the next model turn. Storage appends immutable events; retention and access control remain GEC concerns.

This design also clarifies admin inspection. An administrator can ask why a citation was accepted and receive the event chain linking search admission, authorization, disclosure, and citation. The UI need not infer this chain from model transcript text.

## 18.7 Migrate GEC evaluation custody to ragopt

GEC's retrieval evaluation, judge, and parameter sweep are mature product assets. Replacing their semantics with a generic score would discard useful information. The correct migration is to make one GEC evaluator implement `ragopt/eval.Arm` while retaining a native artifact.

A GEC case remains opaque to `ragopt`:

```json
{
  "query": "How should the restricted vault feed be reconciled?",
  "expected_document_ids": ["ops/vault-reconciliation"],
  "access_scopes": ["finance-admin"],
  "source_roles": ["procedure"],
  "required_claims": ["dual-control review"],
  "tags": ["authorization", "hybrid"]
}
```

The GEC arm performs the real search and optional answer/judge loop. It writes a native artifact containing, at minimum:

- exact release and query-profile identities;
- case and repeat coordinates;
- authorized and rejected candidate identities;
- channel rankings and fusion trace;
- reranker request identity and outcome;
- final context identity;
- answer contract result;
- native judge rubric, per-dimension result, and explanation;
- usage, latency, warnings, and degradation events.

It projects only comparable fields into `ragopt.Outcome`, for example recall at fixed cutoffs, reciprocal rank, nDCG, groundedness, answer-quality dimensions, contract validity, unauthorized-disclosure count, provider calls, tokens, and latency. The native artifact remains the source for diagnosis.

A gate should be phased:

1. **hard safety:** no unauthorized disclosure, no path or artifact violation, no invalid contract above the allowed ceiling;
2. **coverage:** every exact arm/case/repeat cell exists or carries an explicit failure outcome;
3. **target improvement:** the candidate improves the named primary metric under the configured paired statistic;
4. **regression limits:** no protected tag slice or secondary metric exceeds its tolerance;
5. **cost and operational tie-break:** use lower provider calls, token cost, or latency only after the earlier phases pass.

This directly replaces ad hoc sweep selection without replacing the GEC evaluator.

## 18.8 Release identity for GEC

GEC serving currently centers on an index bundle, but a reproducible knowledge behavior also depends on configuration that is not part of the bundle: synonyms, reranker adapter and model, query profile, grounded-answer contract, judge-independent safety policy, and possibly application profile data.

A GEC release manifest should therefore include:

```go
type ReleaseManifest struct {
    Schema          identity.Schema
    Index           artifact.Ref
    Synonyms        *artifact.Ref
    QueryProfile    artifact.Ref
    RerankerAdapter *artifact.Ref
    Contract        artifact.Ref
    AuthzPolicy     artifact.Ref
    ToolSchema      artifact.Ref
}
```

The active release ID is the content identity of this manifest. Query traces record the release ID, not merely the index bundle ID. Activation verifies every child artifact and publishes one atomic pointer to the release manifest. Rollback changes the pointer to a previously verified release; it does not reconstruct an old configuration from mutable files.

## 18.9 GEC migration sequence and acceptance criteria

The GEC migration can proceed without changing user-visible behavior:

1. serialize current query profiles and reranker text composition as immutable artifacts;
2. add a release manifest around the already used `ragkit` bundle;
3. emit a structured query trace alongside current logs;
4. replace internal ranking orchestration with a compiled `ragkit` plan while retaining golden output fixtures;
5. add prefilter-capable search or explicitly mark over-fetch as degraded;
6. implement the GEC `ragopt` arm and run it in shadow against existing sweeps;
7. switch experiment custody and reporting to `ragopt`; delete duplicate run/pairing/gate code only after equivalence fixtures pass;
8. move the session evidence ledger storage to the shared reducer infrastructure without changing its product event vocabulary.

Acceptance requires more than compilation. For a fixed local fixture, the new path must produce identical authorized hit identities and ranks, identical fallback behavior, equivalent tool output, and a trace that proves no unauthorized text crossed a remote boundary. Resume tests must demonstrate exact cell custody, and promotion reports must resolve every referenced native artifact.

# 19. RAG-TTC: eliminate the second RAG core and retain the product system

## 19.1 The repository currently contains two architectural layers

`rag-ttc` is not merely a consumer of reusable RAG code. It contains both a common substrate copied into `pkg/digest`, `pkg/execution`, `pkg/flow`, `pkg/rag`, `pkg/text`, and `pkg/vector`, and a large TTC-specific product and research layer. The latter includes connected retrieval, product catalogs, tool answer schemas, tool configuration, providers, diagnostics, review, evaluation, chat commands, datasets, and UI components.

The correct migration is not to replace `rag-ttc` with `ragkit`. It is to remove the common substrate from `rag-ttc` so that the repository becomes an honest product layer over `ragkit`.

## 19.2 Package cut line

The immediate package map is:

| RAG-TTC current package | Target | Action |
|---|---|---|
| `pkg/digest` | `evidencekit/identity` or temporary `ragkit/digest` | Replace imports, then delete |
| `pkg/execution` | `evidencekit/op` interpreters or retained `ragkit/execution` during transition | Replace imports; no fork |
| `pkg/flow` | `evidencekit/op` / compatibility layer | Replace imports, then delete |
| `pkg/text`, `pkg/vector` | `ragkit/text`, `ragkit/vector` or future focused packages | Replace imports, then delete |
| `pkg/rag` root domain types | `ragkit/rag` compatibility or new semantic packages | Hard cut, then delete copied files |
| `pkg/rag/chunking` | `ragkit/rag/chunking` | Replace |
| `pkg/rag/representations` | `ragkit/rag/representations` | Replace; supply TTC prompt set explicitly |
| `pkg/rag/embedding` | `ragkit/rag/embedding` | Replace |
| `pkg/rag/lexical` and backends | `ragkit` backends | Replace |
| `pkg/rag/vector` and backends | `ragkit` backends | Replace or retain only TTC-specific experimental backend adapters |
| `pkg/rag/indexbundle` | `ragkit/rag/indexbundle` | Replace; accept lexical-only and new identity behavior |
| `pkg/rag/retrieval`, `reranking`, `answering`, `evaluation`, `dataset`, `generation` | corresponding `ragkit` packages | Replace |
| `pkg/rag/connected`, `connectedconfig` | TTC product layer | Retain and refactor to depend on `ragkit` |
| `pkg/rag/productcatalog` | TTC product layer | Retain |
| `pkg/rag/toolanswer`, `toolconfig`, `knowledgetools` | TTC product layer | Retain |
| `pkg/rag/providers/geppetto` | TTC adapter layer | Retain outside shared core |
| `pkg/rag/diagnostic`, `review`, `tooleval`, `agenttrace` | TTC experiment and admin layer | Retain; integrate with `ragopt` where applicable |
| `pkg/ttcrag` | TTC application facade | Retain, but make its dependencies explicit |

The package name does not determine ownership. A package under `pkg/rag` can remain TTC-specific, but it should not pretend to be part of the common RAG kernel. Moving product packages under `pkg/ttcrag` or a top-level `ttcrag` tree would make the boundary legible, but import replacement and implementation deletion matter more than directory aesthetics.

## 19.3 Use behavioral fixtures before the hard cut

Because many copied files are identical or nearly identical, a gradual adapter mesh would create more risk than it removes. The recommended method is a fixture-driven hard cut:

1. identify every public symbol imported by TTC-specific packages;
2. create golden fixtures for chunk IDs, representation text, representation IDs, bundle manifests, hit ordering, fusion results, hydrated evidence, answer context, grounded contract validation, and usage aggregation;
3. record expected cache-key and bundle-ID changes where the new package intentionally creates an epoch;
4. add `ragkit` as a real module dependency;
5. change all common imports in one branch;
6. delete the copied common packages in the same change;
7. run repository-wide build, tests, fixture comparisons, and selected end-to-end commands;
8. add a boundary test that forbids reintroduction of the deleted package paths.

A compatibility re-export package is acceptable only when an external consumer cannot move in the same change. It must contain aliases, not copied implementation, and have a deletion issue. Internal TTC packages should not use it.

## 19.4 Resolve the known semantic drift explicitly

The overlap analysis found changes that must not be treated as accidental compile failures:

- `ragkit` includes document identity in the deterministic hit tie-break;
- generated representation prompts are injectable through a `PromptSet` while the default preserves upstream texts;
- lexical-only index bundles are valid;
- grounded-answer contract kind is configurable;
- bundle identity uses a different prefix;
- the extracted module enforces provider and UI dependency boundaries.

The cutover should codify intended behavior:

**Ordering.** TTC adopts the strengthened total tie-break and adds finite-score validation. Existing fixtures that depended on an unstable tie are defects, not compatibility requirements.

**Prompts.** TTC constructs an explicit `PromptSet` artifact. The initial bytes equal the old package constants so generated representation and cache behavior remain stable. Future prompt changes become candidates or release changes rather than source edits.

**Lexical-only bundles.** TTC accepts them in generic open and inspect commands. Product profiles may still require a vector channel and should validate that requirement at profile compilation.

**Contract kind.** TTC supplies the exact product contract identifier. The shared answer package should not default to a TTC name after the API transition.

**Identity prefix.** IDs are typed by schema rather than interpreted by string prefix. Where external scripts currently parse a prefix, migrate them to manifest fields. Treat the extraction as an explicit cache and artifact epoch.

**Dependency boundary.** Geppetto, Pinocchio, Glazed, Cobra, Bubble Tea, and product UI dependencies remain in TTC adapter or command packages, never in `ragkit` core.

## 19.5 The RAG-TTC query architecture after cutover

The product query path should compile TTC configuration into a `ragkit` plan and then add TTC operations:

```text
subject/query
  -> TTC intent and route selection
  -> ragkit authorized retrieval plan
  -> TTC connected or structured-data augmentation
  -> ragkit context assembly
  -> TTC tool loop and answer schema
  -> ragkit grounding validation
  -> TTC response and admin projections
```

Connected retrieval and product catalog facts are not representations of source chunks. They are distinct evidence providers with their own provenance. The context type should therefore be a sum of evidence kinds rather than coercing everything into a chunk:

```go
type TTCContextItem interface{ isTTCContextItem() }

type SourceChunk struct {
    Evidence ragkit.SourceEvidence
}

type StructuredFact struct {
    QuerySpecID   identity.ID
    DatabaseID    identity.ID
    EntityID      string
    Field         string
    Value         json.RawMessage
    Provenance    artifact.Ref
}

type ConnectedResult struct {
    ConnectorID   identity.ID
    RequestID     identity.ID
    Payload       artifact.Ref
    Disclosure    identity.ID
}
```

The answer contract can then state grounding rules per evidence kind. A citation to a source chunk proves verbatim lineage; a structured fact proves the query specification, database digest, entity key, and field. These are different proof obligations and should not be collapsed into one string label.

## 19.6 The existing ragopt adapter is the reference integration pattern

The supplied `cmd/rag-ttc/cmds/chat/tooleval/ragopt.go` already demonstrates the correct dependency direction. It loads a `ragopt` suite, exposes incumbent and challenger arms, materializes the candidate's assets into a product configuration, executes the actual TTC tool loop, invokes the product judge, writes a TTC-native artifact, and projects a narrow `ragopt.Outcome`.

The adapter should be generalized, not moved into `ragopt`. The following pieces remain TTC-owned:

- decoding the TTC case input;
- resolving tool configuration and product prompts;
- executing the TTC chat/tool loop;
- parsing the grounded answer;
- invoking the TTC answer-quality judge;
- deciding which native dimensions are meaningful;
- writing a native artifact that links the session transcript and product trace.

`ragopt` should own:

- copied and validated candidate inputs;
- exact case/repeat/arm coordinates;
- run creation and resume;
- append-only cell custody;
- strict paired comparison;
- ordered gate evaluation;
- machine and human reports.

The adapter currently writes a run-relative native artifact and projects contract validity, abstention, metrics, provider calls, tool calls, and tokens. That is already a strong model. The kernel migration should replace path-only artifact references with verified content references while preserving product details.

## 19.7 Candidate materialization should become a plan

The current adapter materializes files into a generated tool configuration. This is pragmatic but can be made auditable. Candidate application should be a pure transformation:

```go
type TTCSnapshot struct {
    OrchestrationPrompt artifact.Ref
    AnswerSchema       artifact.Ref
    SearchDescription  artifact.Ref
    ToolProfile        artifact.Ref
    JudgePolicy        artifact.Ref
    Release            identity.ID
}

func ApplyCandidate(
    base TTCSnapshot,
    candidate ragopt.Candidate,
) (TTCSnapshot, error)
```

The function validates exactly one mutable asset, verifies all locked assets, returns a new snapshot value, and does not write files. A separate materializer interprets the snapshot for the legacy runtime. Its output directory and generated config become a derived artifact linked to the snapshot ID. This removes string-built configuration from the semantic boundary and permits differential tests between direct and materialized runtimes.

## 19.8 Admin chat for RAG-TTC

The planned RAG-TTC admin chat should not introduce another query engine. It should consume the same plan descriptions and trace artifacts as production evaluation. Its capabilities can include:

- resolve a release, plan, build, run, candidate, or cell by typed ID;
- display a redacted stage graph and operation identities;
- compare channel rankings and show collapse/fusion provenance;
- inspect context inclusion and omission reasons;
- resolve native artifacts under administrator authorization;
- replay from exact provider-response artifacts where policy permits;
- create an optimization candidate bundle without mutating live configuration;
- launch an externally authorized experiment command;
- render gate decisions and linked evidence.

It must not own authentication, release activation, direct file mutation, or hidden evaluator changes. Administrative actions should invoke application services that validate typed requests and append auditable events.

## 19.9 RAG-TTC migration acceptance criteria

The common-core deletion is complete when:

- no TTC source file imports the deleted common package paths;
- `go list -deps` shows `ragkit` as the sole common RAG implementation;
- a boundary test rejects local packages named for the deleted substrate;
- canonical fixtures document all intentional identity epochs;
- end-to-end indexing and query tests run against a `ragkit` bundle;
- the existing `ragopt` proof cycle produces equivalent projected metrics and resolvable native artifacts;
- Garden integration tests pass through the refactored TTC product facade;
- no product provider, CLI, or UI dependency appears in `ragkit`.

Only after this cut should deeper API renaming occur. Removing duplicate authority is higher priority than achieving the ideal package vocabulary.

# 20. TTC Garden assistant: a product experience over shared evidence

## 20.1 The Garden assistant is a distinct application

The TTC Garden assistant combines a chat runtime, intent-aware search, product-catalog resolution, structured facts, evidence widgets, source cards, choice interactions, persistence, and calibration. It currently imports `rag-ttc` through a local module replacement and reaches both common RAG packages and TTC-specific packages.

Its architecture should not be reduced to a thin skin over a generic chat package. Garden owns customer experience and interaction semantics. The shared design should instead give it stable evidence and experiment boundaries.

## 20.2 Target dependency topology

The target dependency path is:

```text
TTC Garden backend
    -> TTC product facade (`ttcrag` packages)
        -> ragkit
        -> evidencekit
    -> ragopt only from calibration/experiment commands
```

Garden should no longer import common types from `github.com/the-tree-center/rag-ttc/pkg/rag`. Display metadata and tests that need `Document`, `Chunk`, or evidence types should import `ragkit` directly or, preferably, consume TTC facade types. Garden may continue importing TTC product-catalog and tool-configuration packages from the RAG-TTC module until a separate TTC product library is justified.

A later repository split can create a stable `ttcrag` module and leave research commands in `rag-ttc`, but it is not required for semantic cleanup. The immediate rule is that only the TTC facade may compose common RAG and product behavior.

## 20.3 Product facts require release-level identity

Garden's runtime can combine index evidence with a product-facts database. The backend already exposes a fact-database SHA-256 and records structured-fact provenance. An index bundle ID alone therefore cannot identify the behavior of a Garden release.

A Garden release manifest should bind:

```go
type GardenRelease struct {
    TTCQueryRelease   identity.ID
    ProductFacts      artifact.Ref
    ProductQuerySpec  artifact.Ref
    IntentPolicy      artifact.Ref
    RuntimeProfile    artifact.Ref
    SystemPrompt      artifact.Ref
    WidgetSchemas     []artifact.Ref
    SourceViewPolicy  artifact.Ref
}
```

The product-facts reference should include the exact database bytes or a verified snapshot manifest, not merely a path. `ProductQuerySpec` identifies the fixed queries and field interpretations used to turn the database into facts. A value is not sufficiently grounded by naming a database digest if the query semantics are mutable.

The runtime identity attached to chat turns should include the Garden release ID. Existing profile registry, profile version, fingerprint, and system-prompt fields can remain useful projections, but one root release ID simplifies reproducibility and rollback.

## 20.4 Keep evidence presentation separate from evidence admission

Garden's source-results tool validates that requested citation labels were admitted in the current conversation, resolves display metadata, optionally augments presentation with product facts, groups evidence, and publishes customer-facing widgets. This is a good separation from retrieval, but the architecture should distinguish three stages more sharply:

1. **evidence production:** source chunks and structured facts are produced with provenance;
2. **evidence admission:** application policy decides which items may enter the current conversation and assigns stable local labels;
3. **evidence presentation:** a widget projection groups and redacts admitted evidence for a customer.

Presentation-only enrichment must not silently become answer evidence. For example, facts fetched solely to decorate a source card should be marked `presentation` and excluded from the answer-grounding set unless separately admitted. A typed role avoids relying on comments:

```go
type EvidenceUse uint8

const (
    UseAnswer EvidenceUse = iota + 1
    UsePresentation
    UseDiagnostic
)
```

A widget payload should link each displayed fact either to admitted answer evidence or to an explicitly presentation-only provenance record. This preserves the useful Garden behavior while making the grounding boundary auditable.

## 20.5 Choice interactions are product-native evaluation state

Garden calibration cases may contain a user turn or a selection by choice identifier or index. The runner verifies that a selected choice was actually offered by the preceding snapshot, derives a deterministic idempotency key, polls until a terminal answer has settled, and records normalized snapshots. This is richer than a single request-response evaluation cell.

`ragopt` should not redefine a case as one prompt. The Garden arm can interpret one opaque case as a multi-turn scenario and produce one cell outcome after the scenario completes. The native artifact retains every `TurnRecord`:

- session and runtime identity;
- turn number and prompt or selected choice;
- idempotency key;
- start and duration;
- normalized terminal snapshot;
- expectation result;
- source kinds and answer/choice counts;
- any create, submit, polling, or expectation failure.

The projected `ragopt.Outcome` summarizes scenario-level metrics such as all-turn pass, intent match, expected source-kind coverage, invalid-choice count, terminal completion, answer-length compliance, provider calls, latency, and cost. It must not discard the first failing turn or convert an absent later turn into success.

## 20.6 Garden calibration on ragopt

A candidate bundle for Garden should isolate one mutable asset, for example:

- system prompt;
- intent-routing policy;
- search tool description;
- source-card instruction;
- answer schema;
- retrieval profile;
- product-resolution policy.

The suite, release, product database, model profile, widget schemas, expectation interpreter, and judge policy remain locked unless the campaign explicitly studies one of them.

A Garden `Arm` can be defined as:

```go
type GardenArm struct {
    RuntimeFactory RuntimeFactory
    BaseRelease    GardenRelease
    Candidate      ragopt.CandidateView
    ArtifactStore  artifact.Store
}

func (a *GardenArm) Run(
    ctx context.Context,
    req ragopt.Request,
) (ragopt.Outcome, error)
```

For each cell it creates an isolated session, executes the scenario with deterministic idempotency coordinates, stores the full normalized transcript and widget/evidence artifacts, evaluates native expectations, and returns the projection. Ordinary session or expectation failures become completed cell outcomes with explicit failure class. Loss of run custody, artifact-store corruption, or cancellation remains an interpreter error and stops safely.

Paired evaluation should use the same scenario order and repeat coordinate for incumbent and challenger. To reduce temporal provider drift, execution can alternate arms by deterministic cell schedule while preserving exact coordinates. The schedule is execution identity, not experiment semantic identity.

## 20.7 Garden-specific gates

Garden needs protected dimensions that a generic RAG metric suite would miss. A representative ordered gate is:

1. zero evidence-provenance violations;
2. zero invalid-choice continuation and zero cross-session citation reuse;
3. no increase in failed or nonterminal scenarios;
4. required source kinds present for every protected case;
5. no regression in product-fact accuracy or named-product resolution;
6. target improvement in intent routing, recommendation quality, or scenario pass rate;
7. answer-length and interaction-shape tolerances;
8. latency, provider calls, and token cost tie-breaks.

The gate policy names metrics and tag slices; the native evaluator defines them. A weighted average across all these dimensions would allow a serious interaction or provenance regression to be hidden by answer-style gains.

## 20.8 Garden admin and support inspection

Garden support tools should project the same release and evidence trace into a customer-support-appropriate view. Useful questions include:

- which release and profile generated this turn;
- which intent was selected and why;
- which source chunks and structured facts were admitted;
- which facts were presentation-only;
- what choice messages were offered;
- which widget publication corresponds to which admitted evidence set;
- whether a fallback or provider error occurred;
- whether the turn matches a calibration failure pattern.

Raw reasoning, sensitive provider payloads, and unrestricted corpus text should not be exposed merely because the interface is called administrative. Trace resolution is capability-controlled and redacted by default.

## 20.9 Garden migration sequence and acceptance criteria

1. introduce a Garden release manifest binding TTC query release and product facts;
2. record its ID in runtime identity and turn snapshots;
3. refactor Garden imports so common RAG types come from `ragkit` or the TTC facade;
4. make evidence use—answer, presentation, diagnostic—explicit;
5. wrap the existing calibration runner as a `ragopt` arm while preserving native `TurnRecord` artifacts;
6. shadow-run existing calibration output and compare every scenario and turn outcome;
7. move run custody, resume, pairing, comparison, and reports to `ragopt`;
8. delete only the duplicated experiment infrastructure, not the Garden expectation language or normalized snapshot model.

Acceptance requires deterministic choice validation, resolvable exact runtime and release identities, equivalent widget/evidence behavior, exact paired cell coverage, and a demonstrated rollback to a prior full release including product-fact data.

# 21. Migration program: dependency-ordered hardening

## 21.1 Principles

The migration should optimize for deletion of duplicate authority, not for the number of packages created. Five principles govern the sequence:

1. preserve working application behavior with golden and differential fixtures;
2. establish one owner for each semantic decision before generalizing APIs;
3. make intentional identity epochs explicit rather than pretending cache compatibility;
4. adopt shared custody around product-native artifacts, not instead of them;
5. avoid permanent dual writes, bidirectional adapters, and compatibility layers without deletion conditions.

![Dependency-ordered migration roadmap.](figures/10_migration_roadmap.png){width=98%}

## 21.2 Wave 0: freeze semantics and create evidence

Before moving packages, record the behavior that matters:

- source document, chunk, representation, and evidence identities;
- fixed chunk byte ranges and source-slice validation;
- lexical and vector rankings on deterministic fixtures;
- collapse, fusion, and reranker-blend results;
- index manifests and open verification;
- answer context and contract results;
- GEC authorization and fallback behavior;
- TTC tool-loop native outcomes;
- Garden multi-turn snapshots, choice resolution, evidence groups, and widgets;
- current experiment run, resume, and missing-cell behavior.

Fixtures should include invalid and adversarial cases: duplicate IDs, non-finite scores, corrupt cache entries, path escapes, missing cells, unauthorized high-ranked candidates, stale documents, provider failure, and partial terminal sessions.

This wave produces a compatibility matrix that states which outputs must remain byte-identical, semantically equivalent, or intentionally epoch-changing.

## 21.3 Wave 1: introduce the verified evidence kernel

Extract only mechanisms already duplicated or clearly required by both `ragkit` and `ragopt`:

- canonical codec with versioned golden vectors;
- typed identity and domain separation;
- finite ordered numeric values;
- immutable artifact references and verification;
- explicit outcomes and observations;
- append-only ledger primitives and pure reducers;
- law-test helpers.

Do not begin with the full typed plan DSL. Identity, artifacts, outcomes, and reducers provide immediate value and constrain later design. `ragkit` and `ragopt` adopt them behind existing APIs. Existing serialized schemas remain readable where necessary, but new writes use explicit new versions.

Exit criteria are cross-module identity golden tests, no dependency cycle, and a small dependency graph that passes boundary tests.

## 21.4 Wave 2: make ragkit the sole common RAG implementation

Perform the RAG-TTC hard cut described in Chapter 19. This is the highest-value architectural change because it removes a live fork. Garden should continue to pass through the TTC facade during the cut.

Exit criteria are deletion of copied packages, repository-wide build and tests, documented cache epochs, and import-boundary enforcement. No advanced optimization redesign should block this wave.

## 21.5 Wave 3: establish full release identities

Add immutable release manifests to GEC and Garden/TTC. A release binds all artifacts that can alter serving behavior, not just the index. Activation uses an atomic verified pointer. Query traces record the release root.

This wave should also classify all provider-facing caches by semantic key and schema. Unknown old entries either migrate through a verifier or become an explicit cache epoch. Do not infer release identity from a directory name or deployment timestamp.

Exit criteria include exact replay from retained artifacts where permitted, rollback tests, and a release diff that identifies every changed child artifact.

## 21.6 Wave 4: converge experiment custody on ragopt

Implement product-owned arms for:

- the existing RAG-TTC proof cycle;
- GEC retrieval and answer evaluation;
- Garden multi-turn calibration.

Run old and new custody paths in shadow on fixed local suites. Compare cell coordinates, failure classification, native artifacts, projected metrics, pairing, and gate results. Once equivalent, delete duplicate run, resume, pair, and report mechanisms while retaining native evaluators.

Exit criteria are exact resume after interruption, no silently missing cells, immutable terminal runs, and promotion reports whose references all verify.

## 21.7 Wave 5: introduce statically inspectable plans

With identity and artifact semantics stable, replace orchestration hidden in service methods with typed operation specifications and static composition. Start with one index path and one query path, not a universal engine.

Required interpreters are:

- local execution;
- semantic identity analysis;
- graph/description rendering;
- resource and remote-disclosure analysis;
- deterministic test interpretation.

Caching and concurrency can initially delegate to existing `ragkit/execution` and `flow` code. The plan model earns adoption only if it makes the current system easier to inspect and test.

Exit criteria include plan IDs independent of worker count, pre-execution rejection of an invalid disclosure order, and equivalence with the legacy execution path.

## 21.8 Wave 6: build registry and activation coordination

Implement the build state machine inside product code first. When both GEC and TTC demonstrate the same event vocabulary and operational needs, extract `ragbuild`. The outer scheduler remains external; a scheduler starts or resumes one coarse build job, while the inner plan interpreter handles stage-level concurrency and caching.

Exit criteria for extraction are two independent adopters, shared state-transition laws, and a clear deletion of product-local duplicated coordination. Without two adopters, keep the code product-local.

## 21.9 Wave 7: higher assurance

Add model checking for run and build reducers, cross-language canonicalization vectors, adversarial authorization tests, and selective formal proofs. These activities refine a small established kernel; they should not delay removal of the copied RAG core.

## 21.10 Compatibility policy

Every compatibility mechanism must state:

- old and new schema or import surface;
- which direction conversion is allowed;
- whether conversion preserves semantic or only informational equality;
- read deadline and write deadline;
- owner and deletion condition;
- behavior for unknown fields and invalid legacy values.

New systems should never write both old and new authoritative records. During migration, one is authoritative and the other is a derived projection. Dual authority recreates the original problem at the storage layer.

## 21.11 Risk register

| Risk | Likelihood | Impact | Mitigation |
|---|---:|---:|---|
| Hidden TTC dependency on copied implementation detail | High | High | symbol inventory, compile-time hard cut, golden behavior fixtures |
| Cache or bundle IDs change unexpectedly | High | Medium | explicit epoch matrix, typed schemas, no cross-epoch cache sharing |
| Generic kernel grows into a framework | Medium | High | dependency ceiling, package law, two-consumer rule, boundary tests |
| Product-native diagnostic detail is lost | Medium | High | native artifact remains authoritative; projection tests |
| Authorization filtering changes recall | High | Medium | protected authorized-subset fixtures, capability-labeled strategy |
| Provider nondeterminism makes equivalence noisy | High | Medium | artifact replay, deterministic local fakes, paired repeats |
| Old and new experiment stores diverge | Medium | High | shadow one-way projection, exact coordinate comparison, single authority |
| Build coordinator duplicates scheduler | Medium | Medium | one coarse external job; inner interpreter only |
| Formal work becomes detached from code | Medium | Medium | proofs target executable kernel specifications and golden vectors |
| More repositories increase release friction | Medium | Low | keep kernel small, automated compatibility matrix, independent versioning |

## 21.12 Decision checkpoints

Three decisions should be revisited with evidence rather than preference:

**Kernel module boundary.** If `evidencekit` cannot remain narrow after two adoption waves, merge it with a more appropriate domain-neutral infrastructure module. Do not put it into `ragkit` merely to reduce repository count.

**Plan DSL depth.** If static plans do not improve identity analysis, trust checks, or testing in two real paths, retain ordinary Go composition with explicit operation specifications. The category-theoretical model is a guide, not a requirement to construct syntax trees everywhere.

**Build module extraction.** Create `ragbuild` only after two product-local implementations converge. Premature extraction would confuse a state-machine pattern with an actual shared operational contract.
EOF
wc -l -w /mnt/data/rag_work/thesis.md
```

<details><summary>💭 Thinking</summary>

**Appended Parts IV and V with mappings, migration, and verification chapters**

</details>

```json
{"search_query":[{"q":"site:dl.acm.org Generalising Monads to Arrows John Hughes 2000 DOI"},{"q":"site:dl.acm.org provenance semirings Green Karvounarakis Tannen PODS 2007 DOI"},{"q":"site:arxiv.org retrieval augmented generation Lewis 2005.11401 dense passage retrieval 2004.04906"},{"q":"site:rfc-editor.org RFC 8785 JSON Canonicalization Scheme RFC 8949 deterministic encoding"}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Searched 3 websites**

</details>

```unknown
bash -lc echo '--- metrics'; cat /mnt/data/rag_work/analysis_metrics.csv; echo '--- overlap'; cat /mnt/data/rag_work/ragkit_ragttc_overlap.csv
```

Repository measurements confirm the fork: 141 of 165 matched files are at least 95% similar. The 99-page manuscript is now undergoing final render inspection.

<details><summary>💭 Thinking</summary>

**Finalizing artifacts**

I’m packaging the completed thesis with its repository analysis, formal architecture, migration plan, diagrams, and API proposals. I’m also preparing publication-ready document formats and checking that the presentation remains readable end to end.

</details>

```unknown
bash -lc ls -lah /mnt/data/rag_output /mnt/data/rag_work | sed -n '1,200p' && echo '---' && file /mnt/data/rag_output/Compositional_Retrieval_Systems_Thesis.docx && du -h /mnt/data/rag_output/Compositional_Retrieval_Systems_Thesis.docx
```

<details><summary>💭 Thinking</summary>

**Reviewed repository data and generated, formatted, and rendered a thesis DOCX and PDF**

</details>

```unknown
bash -lc identify /mnt/data/rag_work/rendered/page-1.png /mnt/data/rag_work/rendered/page-120.png | sed -n '1,5p'
```

<details><summary>💭 Thinking</summary>

**Inspected, patched, rebuilt, and validated thesis document layout**

</details>

```unknown
bash -lc python - <<'PY'
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
import re, shutil
src=Path('/mnt/data/rag_work/rendered_final')
out=Path('/mnt/data/rag_work/contact_sheets_final')
if out.exists(): shutil.rmtree(out)
out.mkdir()
pages=sorted(src.glob('page-*.png'),key=lambda p:int(re.search(r'(\d+)',p.stem).group(1)))
w,h=Image.open(pages[0]).size; g=24; label=44
font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',26)
for k in range(0,len(pages),4):
    group=pages[k:k+4]
    canvas=Image.new('RGB',(2*w+3*g,2*(h+label)+3*g),(220,220,220)); draw=ImageDraw.Draw(canvas)
    for j,p in enumerate(group):
        r=j//2;c=j%2;x=g+c*(w+g);y=g+r*(h+label+g);n=int(re.search(r'(\d+)',p.stem).group(1))
        draw.text((x+4,y+5),f'PAGE {n}',fill=(0,0,0),font=font)
        canvas.paste(Image.open(p).convert('RGB'),(x,y+label))
    canvas.save(out/f'pages_{k+1:03d}_{min(k+4,len(pages)):03d}.jpg',quality=92,subsampling=0)
print('pages',len(pages),'sheets',len(list(out.glob('*.jpg'))))
PY
```

<details><summary>💭 Thinking</summary>

**Generated and analyzed final page contact sheets and rendered files**

</details>

```unknown
bash -lc sed -n '1,240p' /mnt/data/rag_work/check_render.py
```

<details><summary>💭 Thinking</summary>

**Verifying Thesis Structure and Metadata**

</details>

# Compositional Retrieval Systems

The architecture study is complete. It is a **125-page thesis-style textbook**, comprising **25 chapters and six appendices**, based on direct analysis of the supplied `ragkit`, `ragopt`, `rag-ttc`, GEC, and TTC Garden codebases. The empirical review covered 1,003 Go files, 1,580 test functions, and approximately 137,500 nonblank lines of Go.

### Publications

- [Download the PDF](sandbox:/mnt/data/rag_output/Compositional_Retrieval_Systems_Thesis.pdf)
- [Download the editable DOCX](sandbox:/mnt/data/rag_output/Compositional_Retrieval_Systems_Thesis.docx)
- [Download the Markdown source](sandbox:/mnt/data/rag_output/Compositional_Retrieval_Systems_Thesis.md)
- [Download the complete source bundle](sandbox:/mnt/data/rag_output/Compositional_Retrieval_Systems_Source.zip)

The source bundle contains the Markdown, all ten figures in PNG and SVG forms, repository-scale measurements, and the file-level `ragkit`/RAG-TTC overlap analysis.

## Principal architectural result

The recommended system is not a universal RAG framework. It has three principal layers:

1. **`evidencekit`**, a deliberately small, domain-neutral correctness kernel for canonical encoding, typed identity, immutable artifacts, finite total ordering, explicit outcomes, observations, operation plans, append-only ledgers, reducers, and reusable law tests.
2. **`ragkit`**, the sole owner of shared RAG semantics: corpus lineage, chunks and representations, lexical/vector retrieval, fusion, reranking, context construction, grounded-answer contracts, and query plans.
3. **`ragopt`**, a domain-neutral optimization and experiment layer that operates over opaque product snapshots and native result artifacts. It owns exact pairing, durable run custody, comparison, ordered gates, and promotion reports—not RAG semantics or product evaluation meaning.

A conditional **`ragbuild`** package is proposed only after two applications demonstrate the same build-state and activation semantics. External scheduling, deployment, and provider control remain outside it.

The applied applications retain their native responsibilities:

- **GEC** retains authorization, scope policy, synonyms, reranker policy, judges, evidence-ledger presentation, and administrative behavior.
- **RAG-TTC** deletes its copied common RAG substrate after fixture-backed compatibility testing, while retaining product catalogs, connected retrieval, tool loops, providers, diagnostics, review, and tool evaluation.
- **Garden** consumes a stable TTC facade over `ragkit` while retaining multi-turn intent, choices, widgets, product facts, calibration expectations, and customer-facing session behavior.

The formal core is organized around nine small correctness obligations: canonical identity, source lineage, total ranking, atomic artifact publication, append-only ledger reduction, exact experimental pairing, lexicographic gating, grounding validation, and authorization before remote disclosure. The thesis distinguishes properties suitable for ordinary tests, property testing, fuzzing, state-machine model checking, differential fixtures, and optional formal proof.

It also supplies concrete Go API blueprints, dependency rules, identity strata, product mappings, gate models, trust-boundary designs, worked execution traces, acceptance criteria, architectural decision records, and a dependency-ordered migration program. No repository code was modified; the deliverables are the design, verification, and migration study.


---

> Now do the same for the actual functionality:
>
>
>
> - RAG retrieval optimization (optimizing the indexing + querying phases)
> - RAG in production (indexing as corpus changes, exposing RAG queries to the frontend).
>
>
>
> It feels the current work has been done on the base semantic kernel that is behind optimization, not really conceptualizing the field of "RAG".

I’ll treat this as a second thesis volume centered on operational RAG: end-to-end retrieval optimization, continuous corpus evolution, serving, frontend integration, observability, and safe rollout.

```unknown
bash -lc cat /home/oai/skills/pdfs/SKILL.md && printf '
---DOCX---
' && cat /home/oai/skills/docx/SKILL.md
```


---

> for example denotational/operational semantics

<details><summary>💭 Thinking</summary>

The user wants the thesis/textbook treatment of RAG functionality and system design to explicitly incorporate formal semantic frameworks such as denotational semantics and operational semantics.

**Reading PDF and DOCX skills**

**Planning the deliverable**

I’m treating this as a request for a second, implementation-focused artifact built from the supplied archive. I’ll inspect the materials, identify the semantic-kernel gap, and develop formal denotational and operational semantics around the actual functionality.

**Planned the deliverable**

</details>

```unknown
bash -lc cat /home/oai/skills/pdfs/SKILL.md && printf '\n---DOCX---\n' && cat /home/oai/skills/docx/SKILL.md
```

I’ll formalize denotational semantics over corpora, indexes, evidence, contexts, and answers, alongside operational semantics for ingestion, publication, execution, recovery, concurrency, caching, and failure.

<details><summary>💭 Thinking</summary>

**Inspected RAG artifacts, filesystem contents, and ZIP repositories**

</details>

```unknown
bash -lc rm -rf /mnt/data/rag_functionality_work && mkdir -p /mnt/data/rag_functionality_work/repos /mnt/data/rag_functionality_output && unzip -q '/mnt/data/rag-ttc(2).zip' -d /mnt/data/rag_functionality_work/repos && unzip -q /mnt/data/rag_output/Compositional_Retrieval_Systems_Source.zip -d /mnt/data/rag_functionality_work/prior_source && find /mnt/data/rag_functionality_work/repos -maxdepth 2 -type d | sort | sed -n '1,120p'
```

<details><summary>💭 Thinking</summary>

**Mapping repository semantics**

I’m examining the supplied codebase to connect its concrete indexing, querying, optimization, and serving behavior to formal denotational and operational semantics, with production lifecycle and evaluation treated as first-class concerns.

**Mapped repository semantics**

</details>


---

> and capturing / studying / formalizing the runtime / dyanmic behavior and nature of the domain

<details><summary>💭 Thinking</summary>

The user wants the design and thesis to explicitly capture, study, and formalize the runtime, dynamic behavior, and evolving nature of the RAG domain, including its operational dynamics, state changes, and behavior over time.

</details>

```unknown
bash -lc cd /mnt/data/rag_functionality_work/repos && echo '=== ragkit packages ===' && find ragkit -type f -name '*.go' | sed 's#/[^/]*$##' | sort -u && echo '\n=== rag-ttc pkg/internal packages ===' && find rag-ttc/{pkg,internal,cmd} -type f -name '*.go' 2>/dev/null | sed 's#/[^/]*$##' | sort -u | sed -n '1,260p' && echo '\n=== GEC packages ===' && find code/gec -type f -name '*.go' | sed 's#/[^/]*$##' | sort -u | sed -n '1,260p' && echo '\n=== Garden backend packages ===' && find 2026-05-27--ttc-design-system/backend -type f -name '*.go' | sed 's#/[^/]*$##' | sort -u | sed -n '1,220p'
```

I’ll distinguish semantic equivalence from quality and performance improvement, including when incremental rebuilds preserve meaning and when different runtime traces remain observably equivalent.

<details><summary>💭 Thinking</summary>

**Inspected repository structure, thesis coverage, documentation, and RAG codebase APIs**

</details>

```unknown
bash -lc cat /home/oai/skills/pdfs/SKILL.md && printf '\n---DOCX---\n' && cat /home/oai/skills/docx/SKILL.md
```

<details><summary>💭 Thinking</summary>

**Inspected guidelines, repositories, RAG sources, APIs, and Go modules**

</details>

```unknown
bash -lc ROOT=/mnt/data/rag_functionality_work/repos/code/gec/2026-03-16--gec-rag; echo 'TOP DIRS'; find "$ROOT" -mindepth 1 -maxdepth 3 -type d -not -path '*/.git*' -printf '%P\n' | sort | sed -n '1,260p'; echo 'GO FILES BY DIR'; python - <<'PY'
from pathlib import Path
from collections import Counter
root=Path('/mnt/data/rag_functionality_work/repos/code/gec/2026-03-16--gec-rag')
c=Counter()
for f in root.rglob('*.go'):
    if 'ttmp' in f.parts or '.git' in f.parts: continue
    rel=f.relative_to(root)
    c[str(rel.parent)] += 1
for k,v in sorted(c.items()): print(f'{v:3} {k}')
PY
```

I’ll make index maintenance and query execution primary stateful machines, with optimization candidates coupling materialization and serving policies against time-indexed corpora and workloads.

<details><summary>💭 Thinking</summary>

**Formalizing RAG behavior**

I’m modeling RAG as two interacting state machines: corpus/index maintenance and query serving. I’ll capture their denotations, runtime transitions, optimization objectives, production refreshes, rollbacks, and frontend-facing behavior.

**Refining the scope**

I’m grounding the treatment in the inspected interfaces and documented behavior, while clearly separating directly observed implementation from inferred build behavior and noting the unavailable runtime validation constraint.

**Connecting runtime layers**

I’m integrating cache, batching, retrieval, reranking, evaluation, immutable bundles, filtered serving, and parameter sweeps into one semantic account, distinguishing durable release state from request-time behavior and optimization limits.

**Building the formal model**

I’m extending the analysis into a living RAG service model: evolving corpus and releases, interactive query traces, frontend projection, and optimization interventions, with correctness, freshness, cost, and uncertainty evaluated together.

**Formalized RAG behavior**

**Inspected Go repository, ragkit architecture, RAG optimization, and GEC runtime integration**

</details>

```unknown
bash -lc cat /home/oai/skills/pdfs/SKILL.md && printf '\n---DOCX---\n' && cat /home/oai/skills/docx/SKILL.md
```

<details><summary>💭 Thinking</summary>

**Inspected repository structure, instructions, and RAG indexing files**

</details>

```unknown
bash -lc repo=/mnt/data/rag_functionality_work/repos/rag-ttc
for f in \
 cmd/rag-ttc/cmds/serve/serve.go \
 pkg/app/chatserver/server.go \
 pkg/app/chatserver/live_runtime.go \
 pkg/app/chatserver/submission.go \
 pkg/app/chatserver/turns.go \
 pkg/app/chatserver/http.go \
 pkg/app/chatserver/observability.go \
 pkg/app/chat/runtime.go \
 pkg/app/chat/tool_runtime.go \
 pkg/app/chat/controller.go; do
 echo "===== $f ($(wc -l < "$repo/$f") lines) ====="
 rg -n '^type |^func |^const \(|^var \(' "$repo/$f" | head -100
 done
```

<details><summary>💭 Thinking</summary>

**Inspected production chat, server, controller, and RAG codebases**

</details>

```unknown
bash -lc python - <<'PY'
from pathlib import Path
import hashlib, difflib, json
base=Path('/mnt/data/rag_functionality_work/repos')
a=base/'ragkit'
b=base/'rag-ttc/pkg'
# compare ragkit relative Go files to rag-ttc/pkg equivalents (ragkit/rag -> rag-ttc/pkg/rag, etc.)
rows=[]
for p in a.rglob('*.go'):
    rel=p.relative_to(a)
    q=b/rel
    if q.exists():
        x=p.read_text(errors='replace'); y=q.read_text(errors='replace')
        exact=x==y
        ratio=difflib.SequenceMatcher(None,x,y,autojunk=False).ratio()
        rows.append((str(rel), exact, ratio, len(x.splitlines()), len(y.splitlines())))
print('matching paths',len(rows),'exact',sum(r[1] for r in rows))
from collections import Counter
print('similar >=.95',sum(r[2]>=.95 for r in rows),' >=.8',sum(r[2]>=.8 for r in rows),' >=.5',sum(r[2]>=.5 for r in rows))
print('top nonexact similarities')
for r in sorted((r for r in rows if not r[1]),key=lambda r:r[2],reverse=True)[:30]: print(r)
print('lowest')
for r in sorted(rows,key=lambda r:r[2])[:20]: print(r)
out=Path('/mnt/data/rag_functionality_work/v2/data/ragkit_ragttc_overlap.json')
out.parent.mkdir(parents=True,exist_ok=True)
out.write_text(json.dumps([dict(path=r[0],exact=r[1],similarity=r[2],ragkit_lines=r[3],ragttc_lines=r[4]) for r in rows],indent=2))
PY
```

<details><summary>💭 Thinking</summary>

**Inspected RAG implementations, frontend wiring, datasets, snapshots, and thesis structure**

</details>

```json
{"search_query":[{"q":"site:arxiv.org Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks Lewis 2020 PDF"},{"q":"site:arxiv.org Dense Passage Retrieval for Open-Domain Question Answering Karpukhin 2020 PDF"},{"q":"site:arxiv.org BEIR heterogeneous benchmark information retrieval 2021 PDF"},{"q":"site:dl.acm.org reciprocal rank fusion outperforms condorcet and individual rank learning methods 2009"}],"response_length":"long"}
```

Production refresh and optimization separate cleanly: refresh advances corpus epochs under fixed policy, while optimization changes policy against frozen evidence. Queries bind immutable release leases, preventing mixed index generations.

<details><summary>💭 Thinking</summary>

**Searched 2 websites**

</details>

```unknown
bash -lc set -euo pipefail
printf 'Work dirs:\n'; find /mnt/data/rag_functionality_work -maxdepth 3 -type f | sed 's#^#/##' | head -200
printf '\nOutput dirs:\n'; find /mnt/data/rag_output -maxdepth 2 -type f -printf '%p %s bytes\n' | sort | head -50
printf '\nTool versions:\n'; pandoc --version | head -2; libreoffice --version | head -1; dot -V 2>&1 | head -1
```

<details><summary>💭 Thinking</summary>

**Inspected thesis directories, Markdown style, and RAG source files**

</details>

```unknown
bash -lc set -euo pipefail
R=/mnt/data/rag_functionality_work/repos
OUT=/mnt/data/rag_functionality_work/v2/notes/key_source_excerpts.txt
: > "$OUT"
files=(
"$R/ragkit/rag/answering/types.go"
"$R/ragkit/rag/answering/service.go"
"$R/ragkit/rag/answering/context.go"
"$R/ragkit/rag/indexbundle/types.go"
"$R/ragkit/rag/indexbundle/build.go"
"$R/ragkit/rag/indexbundle/open.go"
"$R/ragkit/rag/flow/flow.go"
"$R/rag-ttc/cmd/rag-ttc/cmds/indexes/build.go"
"$R/rag-ttc/cmd/rag-ttc/cmds/indexes/ann_bakeoff.go"
"$R/rag-ttc/cmd/rag-ttc/cmds/workspace/index.go"
"$R/rag-ttc/pkg/ttcrag/search.go"
"$R/code/gec/2026-03-16--gec-rag/internal/knowledge/service.go"
"$R/code/gec/2026-03-16--gec-rag/internal/knowledge/sweep.go"
"$R/code/gec/2026-03-16--gec-rag/internal/knowledge/tool.go"
"$R/code/gec/2026-03-16--gec-rag/web/src/ws/wsManager.ts"
"$R/code/gec/2026-03-16--gec-rag/web/src/store/timelineSlice.ts"
"$R/2026-05-27--ttc-design-system/backend/internal/ragsearch/ragsearch.go"
"$R/2026-05-27--ttc-design-system/backend/internal/calibration/runner.go"
"$R/2026-05-27--ttc-design-system/backend/internal/webchatcmd/run.go"
)
for f in "${files[@]}"; do
  echo "===== ${f#$R/} =====" >> "$OUT"
  if [[ -f "$f" ]]; then
    nl -ba "$f" | sed -n '1,320p' >> "$OUT"
  else
    echo 'MISSING' >> "$OUT"
  fi
  echo >> "$OUT"
done
wc -l "$OUT"; du -h "$OUT"
# Show selected signatures and stateful behaviors compactly
rg -n "type (Service|Request|Result|Manifest|Build|Runtime|Search|Release|Snapshot|Change|Outcome)|func \(.*\) (Search|Answer|Build|Run|Open|Activate)|fallback|rerank|scope|snapshot|ordinal|append|replace|bundle|register|Close" \
  "$R/ragkit/rag/answering" "$R/ragkit/rag/indexbundle" \
  "$R/code/gec/2026-03-16--gec-rag/internal/knowledge" \
  "$R/code/gec/2026-03-16--gec-rag/web/src/ws/wsManager.ts" \
  "$R/code/gec/2026-03-16--gec-rag/web/src/store/timelineSlice.ts" \
  "$R/2026-05-27--ttc-design-system/backend/internal/ragsearch" \
  "$R/rag-ttc/pkg/ttcrag/search.go" | head -240
```

<details><summary>💭 Thinking</summary>

**Inspected source files, calculated metrics, and designed corpus change figures**

</details>

```unknown
bash -lc set -euo pipefail
R=/mnt/data/rag_functionality_work/repos
find "$R/ragopt" "$R/code/gec/2026-03-16--gec-rag/ttmp" -type f -name '*.md' | rg 'production-index-build|ground-up-production-rag|deep-review|retrieval-optimization-analysis|implementation-guide-for-durable-chat' > /mnt/data/rag_functionality_work/v2/data/design_docs.txt
cat /mnt/data/rag_functionality_work/v2/data/design_docs.txt
printf '\nHEADINGS:\n'
while IFS= read -r f; do echo "===== ${f#$R/}"; rg -n '^#{1,4} ' "$f" | head -160; done < /mnt/data/rag_functionality_work/v2/data/design_docs.txt
```

<details><summary>💭 Thinking</summary>

**Designed and reviewed RAG architecture figures and thesis sources**

</details>

```unknown
bash -lc cat > /mnt/data/rag_functionality_work/v2/The_Semantics_and_Dynamics_of_RAG.md <<'EOF'
---
title: "The Semantics and Dynamics of Retrieval-Augmented Systems"
subtitle: "Optimization, Corpus Evolution, and Production Serving"
author: "Volume II of the architecture study of ragkit, ragopt, rag-ttc, GEC Chat, and the TTC Garden Assistant"
date: "August 2026"
lang: en-US
---

# Abstract {-}

A retrieval-augmented generation system is not adequately described by the static expression "retrieve, then generate." In production it is a long-lived, stateful, concurrent service whose source world changes while queries are executing; whose indexes are derived, verified, activated, drained, compacted, and occasionally rolled back; whose retrieval behavior depends on query-time policy and remote providers as well as index bytes; whose interaction may be direct search, retrieve-then-generate answering, or an agentic sequence of tool calls; and whose customer-visible state is reconstructed from snapshots and event streams. Optimization is therefore not tuning a few ranks against a frozen benchmark. It is controlled intervention in a dynamic system with multiple semantic layers and safety constraints.

This volume studies the actual RAG functionality present in `ragkit`, `ragopt`, `rag-ttc`, the GEC administrative chat, and the TTC Garden assistant. The reviewed snapshot contains 1,003 Go files and 1,580 Go test functions across the five scopes. `ragkit` provides deterministic chunking, representations, immutable lexical/vector bundles, retrieval, fusion, reranking contracts, context construction, grounded answer validation, and within-stage execution controls. RAG-TTC adds committed-Git source snapshots, complete-corpus builds, ANN bakeoffs, connected retrieval, model-invoked search, turn-scoped evidence ledgers, and a persistent chat runtime. GEC adds access scopes, source roles, lexical synonyms, an optional cross-encoder reranker, rank sweeps, administrative tool registration, and a snapshot-plus-WebSocket frontend. Garden adds intent-routed retrieval, structured product facts, evidence-bound widgets, and multi-turn calibration. `ragopt` supplies experiment custody, exact pairing, resumability, ordered gates, and promotion reports, but deliberately has no native model of RAG dynamics.

The central correction to the earlier kernel-centered architecture is to make the *evolving RAG service* the semantic object. The study gives both denotational and operational semantics. Denotationally, a release maps a subject, conversation state, and request to a distribution over outcomes and traces. Outcomes include answers, ranked evidence, abstentions, failures, cancellation, and presentation events. Traces retain intensional facts that final answer text erases: source and release lineage, authorization decisions, remote disclosure, fallback paths, latency, cost, freshness, and tool iterations. Operationally, the system is described by coupled labelled transition systems: an index-maintenance machine, a query/interaction machine, a release-activation machine, and a frontend projection machine. The optimization controller observes and intervenes in all four without owning their domain semantics.

The proposed production architecture introduces source revisions, changes, cursors, snapshot barriers, watermarks, impact plans, incremental derivation, backend capabilities, immutable RAG releases, compare-and-swap activation, reference-counted release leases, typed query interpreters, trace schemas, and replayable frontend events. Index maintenance is treated as incremental view maintenance. A clean full rebuild is the correctness oracle for an incremental build; a base-plus-delta overlay is the recommended first production design because it preserves immutable release semantics while enabling bounded freshness. Exactly-once execution is not assumed. Correctness is instead obtained from at-least-once source delivery, semantic idempotence, content-addressed derivation, checkpointed stages, and exactly-once *activation effect* through an idempotent compare-and-swap transition.

The optimization design covers the indexing and querying phases jointly. It defines a typed dependency graph over source admission, normalization, chunking, representations, embedding, lexical/vector indexes, query rewriting, routing, candidate depth, filtering, fusion, reranking, context admission, answer and agent policy, serving policy, and presentation. Interventions are classified as semantics-preserving operational changes, approximation changes, relevance changes, knowledge changes, policy/security changes, and user-outcome changes. Evaluation proceeds through multiple fidelities: static laws, retrieval tests, repeated answer tests, session and frontend calibration, shadow traffic, and canary release. Promotion is constraint-first and Pareto-aware across relevance, grounding, answer quality, freshness, reliability, latency, cost, capacity, security, and user outcomes; it is not a universal weighted score.

The most urgent implementation findings are concrete. GEC currently applies access filtering after retrieval and optional reranking, so unauthorized hydrated text can cross a remote reranker boundary even though it is not returned to the user. GEC opens one bundle at startup while synonyms and reranking remain outside bundle identity. GEC and Garden lack a native atomic hot-activation boundary. RAG-TTC and Garden serve agentic retrieval whose semantics cannot be reduced to one `Query -> Answer` function. The GEC frontend buffers and sorts events around hydration, but its entity reducer does not explicitly reject stale entity versions, and append patches are not duplicate-idempotent. These are not incidental implementation details; they are violations or omissions in the runtime semantics that the shared RAG packages should make explicit.

The volume concludes with Go API blueprints, state-transition rules, proof obligations, testing and model-checking targets, a package architecture, product-specific migrations, and a staged implementation plan. The intended result is not a universal chatbot framework. It is a precise operational model of RAG from source revision to frontend projection, with enough structure to optimize the whole system without losing lineage, reproducibility, or safety.

# Preface and reader's guide {-}

This is the second volume of the architecture study. The first volume concentrated on compositional kernels, typed identity, immutable artifacts, evidence custody, and optimization-loop structure. Those results remain prerequisites, but they are not the subject here. This volume treats RAG as a field of computation in its own right.

The word *RAG* is used in industry for several materially different programs. One program returns ranked evidence. A second program retrieves evidence once and generates an answer. A third exposes retrieval as a tool to an agent that may search zero, one, or many times before it produces a final projection. A fourth mixes unstructured retrieval with structured facts and typed UI widgets. All four appear in the supplied code. They share retrieval primitives, but they have different state spaces, traces, completion rules, failure modes, evaluation units, and frontend contracts. The architecture must preserve those distinctions.

Readers implementing corpus refresh should begin with Chapters 7, 12, and 16 through 20. Readers optimizing relevance should read Chapters 8 through 11 and 21 through 26. Readers responsible for query serving should focus on Chapters 13 through 15 and 27 through 30. Product owners should read Chapters 2 through 6 and 32 through 35. The appendices provide formal transition rules, API sketches, parameter catalogs, and test obligations suitable for direct conversion into tickets.

The mathematical presentation is intentionally operational. Category theory, denotational semantics, probability kernels, labelled transition systems, stream functions, and incremental view maintenance are used because each answers a concrete engineering question. They are not used to rename ordinary functions. Whenever a formal structure does not improve an API, an invariant, an optimization plan, or a test, it is omitted.

This study is based on a supplied development snapshot rather than a complete, buildable monorepo. In particular, the GEC source imports `internal/knowledgebuild`, but that directory is absent from the extracted snapshot. The design documents and call sites describe it in detail, but its implementation could not be inspected directly. The repositories require Go 1.26.x while the analysis environment provides Go 1.23.2 without network access for toolchain download. Consequently, the empirical claims in this volume are based on static source, tests, manifests, and design records; the current snapshot was not compiled or executed. These limitations are stated again in Appendix G.

# Principal claims {-}

1. The correct semantic object is a long-lived evolving RAG service, not an immutable index bundle and not an optimization run.
2. RAG behavior has at least three semantic layers: extensional outcomes, intensional traces, and operational transitions. Optimization must preserve or intentionally change each layer under explicit constraints.
3. Corpus maintenance and query serving are coupled machines. Release activation is the synchronization protocol between them.
4. Direct retrieval, retrieve-then-generate answering, and agentic retrieval are separate interpreters over a shared retrieval algebra.
5. A production RAG release must identify all behaviorally material inputs: corpus snapshot, derived indexes, retrieval policy, reranker, synonyms and rewrites, structured stores, prompts, contracts, provider identities, and presentation policy.
6. A query or turn must be pinned to one release. Evidence, context, citations, structured facts, answer validation, and frontend provenance must not mix release epochs.
7. Authorization must constrain candidate text before any remote reranker, generator, or connected-retrieval provider receives it.
8. Corpus refresh should begin with immutable base releases plus delta overlays and periodic compaction. Incremental output must be observationally equivalent to a clean full rebuild at the same source barrier, subject to declared approximate-backend tolerances.
9. Exactly-once execution is the wrong reliability target. Use at-least-once inputs, idempotent semantic stages, durable checkpoints, and compare-and-swap activation.
10. Retrieval optimization is a constrained intervention problem over a dependency graph, not a flat parameter sweep. Indexing and querying parameters interact and must be evaluated at the correct behavioral level.
11. Frontend projection is part of RAG semantics whenever evidence, citations, choices, or widgets affect the user outcome. Snapshot-plus-suffix replay requires versioning, deduplication, stale-update rejection, and explicit patch laws.
12. `ragkit` should own shared RAG-domain semantics and runtime contracts. `ragopt` should orchestrate controlled trials over those contracts without owning source, index, query, activation, or presentation meaning.

# Notation and semantic conventions {-}

Let $W_t$ denote the external source world at time $t$. A source capture at barrier $\tau$ produces a finite logical snapshot $S_\tau$. A build specification is $b$, a query specification is $q$, and a behavior-complete release is $R = (S_\tau, b, q, a)$ where $a$ denotes auxiliary material such as prompts, rerankers, structured fact stores, contracts, and presentation policy. A subject and authorization context is $u$; a conversation state is $c$; and a request is $x$.

The notation $X + Y$ denotes a disjoint sum. $\mathcal{D}(X)$ denotes a probability distribution over $X$; in an implementation it may be represented only by samples and retained provider transcripts. $\mathsf{Trace}$ is a finite sequence of typed events. A deterministic relation $z \xrightarrow{\ell} z'$ is one small operational step from configuration $z$ to $z'$ with label $\ell$. Its reflexive transitive closure is $\xrightarrow{*}$. The symbol $\Delta$ denotes a change or differential. A signed multiset is used when insertions and deletions must compose algebraically.

A *release* is not merely an index directory. It is the immutable root of everything required to interpret a query under one declared behavior. A *deployment* is a running process or replica set that can serve one or more releases. An *activation* changes which release new leases resolve to. A *lease* pins an in-flight query, turn, or session to a release and prevents premature retirement.

A *trace-equivalence* relation may be exact or observational. Exact trace equivalence requires the same typed events and material values. Observational equivalence projects away declared operational variation, such as worker scheduling, while retaining user outcomes and protected facts such as authorization, evidence lineage, and fallback class. Every optimization candidate must state which equivalence or improvement relation it claims.

![The RAG domain consists of coupled maintenance, serving, projection, and optimization machines.](figures/01_rag_domain_machines.png){width=88%}

# Part I. The implemented RAG domain

# 1. Research problem, scope, and method

## 1.1 Why the object of study must change

The earlier architectural work asked what small common kernel could support indexing, querying, and optimization. That question was useful but incomplete. It starts from reusable mechanisms and moves outward. The present question starts from the domain itself: what is a RAG system over time, what does it mean, how does it execute, what can change, and what counts as a correct optimization?

A static pipeline description hides the decisive facts. A source revision may arrive while a query is running. An index may be partially built but not eligible for activation. A reranker may fail after lexical and vector retrieval succeeded. A generator may emit tokens before its final citation set is known. A frontend may hydrate a snapshot while newer events are already buffered. An agent may call search twice, reuse one evidence item, query a structured database, and then present a typed product comparison. A canary release may improve nDCG but disclose unauthorized text to a remote provider or violate a freshness objective. These behaviors are the field.

The central research questions are therefore:

1. What denotation should be assigned to an evolving RAG release and service?
2. What operational machines explain build, activation, query, agent, and frontend behavior?
3. Which state and transition boundaries should become shared APIs?
4. How should corpus changes be represented and incrementally maintained?
5. How can indexing and querying be optimized jointly without invalid comparisons?
6. Which properties can be tested, model-checked, or proved over small kernels?
7. How should the current applied systems migrate while preserving useful product semantics?

## 1.2 Reviewed systems

The review covers five scopes. `ragkit` is the reusable RAG package. `ragopt` is the reusable experiment and optimization-loop package. `rag-ttc` is the largest applied and experimental RAG system and contains both a copied RAG substrate and product-specific runtime functionality. GEC is an administrative chat with RAG and structured-data tools. The TTC design-system repository contains the Garden assistant and its evidence-aware product presentation.

The reviewed snapshot contains 176 files in `ragkit`, 120 in `ragopt`, 1,302 in `rag-ttc`, 1,114 in GEC, and 940 in the TTC design-system scope. The corresponding nonblank Go line counts are approximately 17,743; 5,925; 76,705; 28,668; and 8,485. These measurements are useful only as scale indicators. The architectural conclusions come from the semantics expressed in types, state transitions, tests, and call graphs, not from line counts.

![Implementation scale of the reviewed systems.](figures/13_repository_scale.png){width=86%}

## 1.3 Method

The analysis followed the runtime path in both directions. On the indexing side it began at source capture and corpus loading, followed normalization, chunking, representation generation, embedding, index construction, manifest verification, and bundle opening, then inspected the build and experiment commands that compose those stages. On the query side it began with frontend and chat submission, followed runtime resolution, tool registration, retrieval, ranking, evidence admission, generation, validation, event emission, and frontend reduction.

Static API analysis was supplemented by test analysis and design-record analysis. Tests reveal intended laws that comments may not state: deterministic tie-breaking, context admission boundaries, evidence-ledger capacity, session cancellation, snapshot hydration, and ANN reproducibility. Design records reveal intended operational contracts not yet present in the checked-in source: nightly refresh, resumable builds, source watermarks, and activation workflows. The volume distinguishes implemented behavior from intended design.

The optimization review traced what each harness holds fixed, what it mutates, what unit it evaluates, what failures enter the denominator, and what decision rule it applies. This is necessary because two loops can both be called "optimization" while answering different causal questions. A fusion sweep over frozen channel rankings is not an index optimization. An ANN bakeoff against an exact oracle is not an answer-quality experiment. A multi-turn calibration is not a paired retrieval benchmark. A production canary is not a substitute for any of them.

## 1.4 Strength of claims

Claims about source-visible ordering and identity are strong. For example, GEC's `Search` calls `retrieve` and only then calls `filterHits`; `retrieve` may call `rerank`, which hydrates candidate chunks before invoking the reranker. The security consequence follows from the order of operations. Claims about missing behavior are also strong when no corresponding type, state, or code path exists in the supplied snapshot.

Claims about the absent GEC `internal/knowledgebuild` package are weaker. Its behavior is reconstructed from imports, command call sites, tests that reference its constants, and detailed ticket diaries. The missing source prevents direct confirmation of implementation details. Claims about runtime performance are not made because the code could not be built in the analysis environment and because supplied benchmark artifacts are workload-specific.

# 2. What “RAG” means in the current code

## 2.1 A family of interpreters, not one pipeline

The code contains at least four operational meanings of RAG.

The first is **direct ranked retrieval**. A request contains a query and perhaps a route, filters, and a limit. The result is an ordered list of hydrated chunks or structured facts. GEC's `knowledge.Service.Search`, RAG-TTC workspace search, and the TTC search tool's internal channel execution are examples. Completion occurs when the ranked evidence list is produced.

The second is **retrieve-then-generate answering**. `ragkit/rag/answering` performs channel retrieval, fusion, optional reranking, context construction, provider generation, and grounded-contract validation. Completion occurs when a valid answer or safe abstention is produced. The retrieval trace and the generation trace are one operation, but their failures are distinct.

The third is **agentic retrieval**. RAG-TTC's `ttcrag.SearchTool` is registered as a model-callable tool. A turn may make no search call, one call, or multiple calls under different routes. Evidence is accumulated in a turn-scoped ledger and exposed through stable labels. Completion is decided by the agent policy, not by the search function. The semantic input is conversation state; the semantic result is a trajectory and final projection.

The fourth is **retrieval plus typed product presentation**. Garden may satisfy a product-fact intent through structured data before unstructured retrieval, augment retrieved evidence with exact product facts, and expose only evidence-admitted material to grounded widget tools. The final user result is not only answer text. It includes choices, source cards, product comparisons, step widgets, and developer lineage. Presentation is an interpreter from evidence and product policy to UI events.

These modes should share data types for queries, candidates, contributions, evidence, release lineage, and traces. They should not share one overloaded service method whose optional fields attempt to encode every mode. Separate interpreters make terminal conditions and failure behavior explicit.

![Three query interpreters share a retrieval algebra but have different completion semantics.](figures/05_query_interpreters.png){width=88%}

## 2.2 The retrieval algebra already present

Across the systems, a common algebra is visible:

$$
\mathsf{retrieve} = \mathsf{admit} \circ \mathsf{hydrate} \circ \mathsf{rerank} \circ \mathsf{filter} \circ \mathsf{fuse} \circ \mathsf{collapse} \circ \mathsf{channels} \circ \mathsf{rewrite}.
$$

Not every route uses every operator. A lexical-only route omits vector search and fusion. A structured-fact route may return authoritative facts without chunk retrieval. A no-rerank route omits the cross-encoder. A representation-kind route wraps a searcher and filters searchable derivatives. A connected-retrieval route may augment or replace local candidates. Nevertheless, the operations and their ordering are stable enough to form a shared vocabulary.

Ordering is semantically important. Filtering before remote reranking is not equivalent to filtering after it, even when the returned top-$k$ list happens to match, because remote disclosure differs. Collapsing representations before fusion is not generally equivalent to fusing representations and then collapsing, because multiple representations from one chunk can occupy channel ranks. Applying synonyms only to lexical search, as GEC does, is not equivalent to rewriting the query globally. Hydrating before a budget check may cause unnecessary I/O or disclosure. The algebra must therefore retain stage order rather than exposing an unordered bag of plugins.

## 2.3 Evidence is stateful in the applied systems

In `ragkit/answering`, evidence is a bounded ordered context for one answer operation. In GEC, a per-run evidence ledger assigns labels such as `E1` and advertises its scope in tool output. In RAG-TTC, the search tool tracks already-seen chunks across multiple calls in one turn. In Garden, a per-conversation search session retains citations and structured facts so later widget tools can prove that their payload was grounded in admitted evidence.

These are not identical ledgers. Their lifetime differs: operation, run, turn, or conversation. Their element types differ: chunks, structured facts, or presentation groups. Their capacity rules differ. The shared abstraction should therefore be an explicit *evidence session* parameterized by scope and evidence kind, not a global singleton or one fixed ledger implementation.

A critical invariant is that an evidence session belongs to one release lease. Reusing a conversation-scoped ledger after activating a new release can silently mix source revisions unless the product explicitly creates a new evidence epoch. The current code does not yet make this release relationship a type-level contract because it does not have behavior-complete release leases.

## 2.4 Structured facts and connected retrieval

Garden and RAG-TTC show why RAG cannot be reduced to vector search over text. Some product questions are better answered from a structured fact database. Some routes invoke connected retrieval. Some final answers combine exact structured fields with explanatory source chunks. The common semantic category is not "text passage" but *typed evidence with provenance and disclosure policy*.

This does not justify collapsing SQL tools, search tools, and product databases into a universal evidence engine. Their authority and freshness differ. A structured store may be live and transactionally current while an index is a captured snapshot. A connected source may have weaker reproducibility and stronger disclosure risks. Shared types should express evidence kind, source epoch, query provenance, and policy. Product code should retain the meaning of fields and the rules for joining them.

# 3. Implemented indexing functionality

## 3.1 `ragkit`: a deterministic full-build substrate

`ragkit` defines documents, chunks, representations, embeddings, search interfaces, and immutable index bundles. A document has a stable ID, source URI, title, text, content digest, and metadata. A chunk refers to one document and an exact half-open byte range. Chunk identity includes the document, chunker, range, and text digest. A representation is searchable derived material linked to a source chunk; it is not evidence.

The chunking package supplies fixed-size, Markdown-aware, and Markdown-heading-aware policies. These transformations are deterministic and document-local. Document locality matters for future incremental maintenance: changing one document need not invalidate chunk identities for other documents. It may still invalidate many chunks inside the changed document, particularly when an insertion shifts byte ranges or heading structure.

The flow and embedding packages provide content-addressed cache keys, bounded parallel maps, retries, fail-fast or quarantine policies, rate limits, and budget admission. These mechanisms are substantial. They determine how expensive provider operations execute and resume at the *stage* level. They do not yet constitute a durable production build machine: there is no source cursor, build lease, stage checkpoint manifest, activation state, or cross-process resume protocol.

`ragkit/rag/indexbundle` builds an immutable artifact containing chunk and representation data, a Bleve lexical index, an exact SQLite vector index when configured, and a manifest. Publication uses a temporary location followed by synchronization and rename. Opening verifies schema, counts, backend manifests, corpus lineage, and query-embedding identity. Verified source documents are loaded only when the corpus path remains within the expected root and its digest matches the manifest.

This is a strong **sealed snapshot** abstraction. It answers: given a finite corpus and complete derived material, what exact searchable bundle was built, and can it be opened safely? It does not answer: what changed in the source world, which work is affected, how is a failed build resumed, which release is active, or how does an old release drain.

## 3.2 RAG-TTC complete-corpus builds

The RAG-TTC index build command is the most pragmatic composition of the shared substrate. It loads a full corpus JSON file, chooses a chunker, creates raw and optionally generated representations, embeds every representation through a cache, and invokes the immutable bundle builder. Generated representation kinds include summaries, contextual forms, questions, and entities. The dry-run path estimates counts and cost.

The provider caches mean that a logical full rebuild does not necessarily repeat all expensive work. Identical representation inputs can reuse generated text and embeddings. This is valuable and should be retained. However, cache reuse is not incremental *state maintenance*. The command still computes from a complete input corpus and produces a complete output bundle. It has no explicit document upsert/delete protocol, source watermark, or delta index.

RAG-TTC workspace indexing contributes a stronger source capture model. `gochunk.LoadCommitted` captures Git `HEAD`, reads tracked files from the committed tree rather than the mutable working directory, applies admission policy, and computes a deterministic snapshot digest from repository state, policy, and document digests. The workspace command persists snapshot, admissions, diagnostics, chunk records, representations, and a build record. This is close to a proper `Snapshotter` interface and should inform `ragkit/corpus`.

The limitation is again dynamic: each workspace build is a new full committed snapshot. There is no reconciliation from the prior snapshot, no delete propagation contract, and no activated release registry. The source semantics are stronger than the maintenance semantics.

## 3.3 Index backend experiments

The current vector bundle uses exact SQLite search. RAG-TTC also contains an in-memory HNSW candidate and an ANN bakeoff command. The bakeoff treats exact search as an oracle, sweeps `efSearch`, measures recall and p95 search latency, and requires ranking reproducibility across a rebuild before choosing a candidate. This is a good example of an approximation-changing intervention with an explicit gate.

Its scope is deliberately narrow. It evaluates a fixed query workload and does not include update throughput, deletion behavior, memory residency, compaction, build duration, crash recovery, multi-tenant isolation, or freshness under a delta overlay. These are not defects in the experiment; they are additional dimensions required before the backend can be declared production-equivalent.

An index backend contract should therefore expose capabilities rather than only `Search`. Relevant capabilities include full build, deterministic bulk load, point upsert, point delete, snapshot reads, atomic checkpoint, compaction, exact-score availability, filter pushdown, and memory/disk reporting. Optimization can then reject candidates that cannot implement required semantics before spending quality-evaluation budget.

## 3.4 What is absent from the shared indexing model

The shared code has no first-class source revision. `rag.Document` describes a current logical document, not a revision with observed and effective time. There is no tombstone type, source cursor, snapshot barrier, or watermark. A corpus digest identifies one finite serialization, but it does not describe the relationship between successive corpus states.

There is also no build intent or durable build status. A filesystem bundle is either successfully returned or the call errors. Flow-level caches can preserve completed expensive items, but an operator cannot ask a shared service which source barrier is being built, which stage is blocked, which items are quarantined, whether a build can resume under the same semantic identity, or which release supersedes it.

Finally, index bytes do not identify complete query behavior. Lexical field boosts are embedded in build behavior, but reranker, synonyms, route configuration, prompts, fact databases, and presentation policies live elsewhere. The production unit must be larger than an index bundle.

# 4. Implemented query functionality

## 4.1 `ragkit/answering`

The answering service exposes strategies for BM25, vector, reciprocal-rank fusion, reranked fusion, multi-query retrieval, and HyDE-style query generation. A request carries IDs, query text, retrieval query, and retrieval configuration. A result carries per-channel hits, fallback and error observations, fused rankings, admitted evidence, timing, and a trace.

The implementation executes lexical and vector retrieval sequentially. Multi-query and HyDE generation can degrade to the original query when their provider fails, recording the failure. A generic reranker error can fail the request, whereas GEC's product-specific reranker fails open to fused order. This difference is semantically material and should be a declared `FallbackPolicy`, not an accidental divergence between applications.

Context construction admits complete chunks in ranked order under evidence-count and rune limits; it does not truncate chunks. This gives a simple prefix property: increasing the budget cannot reorder already-admitted chunks, though it can admit additional chunks. The grounded answer contract validates that cited chunk IDs came from supplied evidence and converts unsupported output into a safe abstention.

The service already emits stage observations. Those observations should be promoted from diagnostics to the intensional denotation of the request. An answer that used the original query after HyDE failed is not trace-equivalent to an answer produced by the intended route, even when the final text matches.

## 4.2 GEC retrieval

GEC opens one verified bundle and source corpus into an immutable `knowledge.Service` at process startup. It reconstructs a query embedder from the bundle manifest when a vector channel exists. The service is shared across sessions; run-scoped evidence lives in the tool wrapper.

The query contract adds server-owned access scopes, source roles, and route controls. Lexical query expansion uses curated synonyms; the vector and reranker queries remain raw. Hybrid retrieval fuses lexical and vector rankings with weighted RRF. An optional reranker hydrates a candidate pool, prefixes titles, invokes the cross-encoder, and blends reranker rank with fused rank. Provider failure logs a warning and returns the fused order.

The code explicitly states that reranking and synonyms are serving configuration rather than bundle identity. This is operationally convenient but semantically incomplete. Two processes can advertise the same bundle ID and return different rankings because environment-loaded synonyms or reranker configuration differ. A query trace can partially explain the difference, but release identity cannot.

The more serious issue is stage order. `Search` calls `retrieve` with an overfetch depth and applies `filterHits` afterward. `retrieve` may rerank before filtering; reranking hydrates chunk text and may call a remote provider. Thus unauthorized chunks can be sent to a remote reranker even though they are removed before the result is returned. "Never returned" is not the same security property as "never disclosed." Authorization must be applied before hydration for any remote stage, ideally through backend filter pushdown or a local authorized candidate set.

Post-ranking filtering also creates relevance starvation. The implementation overfetches by a fixed factor of eight and notes that this is adequate for the current small scope set. The general semantic contract should be stronger: the returned list must be the top-$k$ ranking *within the authorized subcorpus*, not the filtered prefix of an unauthorized global ranking. Backend prefiltering or per-scope indexes can implement that contract.

## 4.3 RAG-TTC search as an agent tool

`ttcrag.SearchTool` contains lexical and vector searchers, source and chunk catalogs, route definitions, configuration, and a turn-scoped evidence ledger. A route can alter representation-kind or source-role searchers, channel enablement, candidate depths, RRF constant, and connected augmentation. Each call returns citations, ranks, contributions, and an `AlreadySeen` marker.

This is not merely a search API with additional metadata. The ledger changes the meaning of later calls. A repeated chunk can retain its citation label while being marked already seen. Capacity limits can prevent new evidence from entering the turn. A structured route can answer an authoritative product-fact query without source chunks. The transition system must include ledger state and route observations.

The direct service path and the model tool path should use the same retrieval plan types and ranking kernels. They should not be forced into the same method. The tool interpreter needs operation names, model-visible schemas, iteration limits, tool-result serialization, and conversation-state transitions that direct search does not.

## 4.4 Garden's product interpreter

Garden opens a fixed RAG index bundle, product fact database, tool configuration, and embedding provider at startup. It creates fresh session search state and tool registries per conversation. Intent classification selects routes that change representation filters, source roles, channel depths, RRF, and connected augmentation. Structured product facts can satisfy some intents before local retrieval; exact facts can also augment retrieved evidence.

Grounded widget tools are particularly important. They do not accept arbitrary model-provided product facts. They project from evidence admitted by the exact session search instance, group chunks by document, align structured fields, retain field-level provenance, and suppress conflicting extracted facts. Customer and developer modes expose different projections.

This makes frontend presentation part of the semantic result. A retrieval candidate can improve answer text yet degrade the widget by failing to supply aligned product fields. Conversely, a structured fact route can produce a better customer outcome without improving text-retrieval metrics. Optimization must include the presentation interpreter when the product uses it.

# 5. Implemented production runtime

## 5.1 Startup-bound resources

GEC and Garden both resolve RAG resources at process startup. GEC opens one bundle and then applies environment-configured synonyms and reranking. Garden opens the index, fact database, tool configuration, and provider, then creates per-conversation tool state. RAG-TTC's simple serve command similarly opens a fixed bundle. This is operationally straightforward and safe for immutable objects, but activation requires a process restart and there is no shared draining or rollback protocol.

A restart is not a semantic activation mechanism. It can mix old and new replicas behind a load balancer, interrupt in-flight sessions, and leave release identity implicit in deployment configuration. A production RAG runtime needs a release manager that can acquire immutable handles, atomically change the active head, preserve old handles for in-flight work, and expose exact release IDs in traces and frontend provenance.

## 5.2 Persistent chat and submission state

RAG-TTC and the GEC/Garden chat stacks are more mature than a simple HTTP question-answer endpoint. They maintain conversations, turns, timelines, submissions, idempotency keys, cancellation, authorization, and persistent observations. Runtime composition occurs per conversation or request. Tool calls and results are events in a durable interaction, not transient local function calls.

This state determines RAG behavior. An agent policy sees prior messages and tool results. A turn may be cancelled after retrieval but before generation. A duplicate submission should not create duplicate turns. A runtime failure to persist observations can be fatal even when the model returned text, because the transcript is part of the operational contract. Shared RAG APIs must fit into this stateful host rather than replacing it.

## 5.3 Frontend hydration and live events

GEC's WebSocket manager receives a hello frame, subscribes with a prior snapshot ordinal, optionally hydrates a snapshot, buffers live UI events that arrive before hydration completes, sorts the buffer, and then appends the suffix. Events and snapshots are mapped into a common timeline entity model. The Redux reducer upserts entities, merges sparse terminal data, and supports append and replace stream patches.

This is close to a formal snapshot-plus-suffix protocol, but the reducer laws are underspecified. `updatedOrdinal` is set to the maximum of old and incoming values, yet incoming fields are merged even when the incoming entity is stale. A stale update can therefore overwrite newer content while retaining the newer ordinal. Duplicate append patches append twice unless transport or upstream storage deduplicates them. The current transport may make these cases rare, but the reducer itself is neither stale-safe nor duplicate-idempotent.

A production event envelope should contain an event ID, stream ID, entity ID, entity version, global or stream ordinal, operation, patch mode, causation ID, and release/turn lineage. The reducer should reject lower entity versions, deduplicate event IDs, and define exactly-once semantics for append patches or replace them with versioned full values. These requirements become especially important when answer streaming is exposed through reconnecting mobile or browser clients.

## 5.4 Runtime identity

Garden records a broader runtime identity than GEC: profile registry, prompt source, RAG index path, fact database path and digest, augmentation behavior, and tool configuration path. This is useful but remains partly path-based and not one immutable release root. GEC's runtime fingerprint comes mainly from an inference profile and omits complete RAG behavior.

A behavior-complete release must be material rather than locational. A path may be overwritten; an environment variable may change; a provider alias may resolve to a new model. The release manifest should record content digests or immutable provider version identities and should itself be content-addressed. A deployment can then state exactly which release each turn used.

# 6. Implemented optimization and its boundary

## 6.1 `ragopt` is experiment custody

`ragopt` has a clear domain-neutral role. Candidates are immutable exact-one-mutation snapshots. Evaluation schedules incumbent and challenger cells at the same case and repeat coordinates. The run store copies inputs, appends durable cell results, supports resume, and records terminal status. Comparison requires exact pairs and represents missing metrics explicitly. Gates are ordered predicates. Reports make promotion evidence reviewable and do not directly apply production changes.

This is the right substrate for reproducible intervention. It intentionally does not know what a chunk, RRF constant, release lease, source watermark, citation, or frontend widget means. The current package therefore cannot by itself answer the RAG-specific questions in this volume. It needs a domain adapter built on shared RAG semantics.

The control boundary should remain: `ragopt` may request a build, execute a query interpreter, consume native metrics, and propose activation. It should not define source connectors, incremental index semantics, authorization, evidence admission, or release activation rules. Putting production refresh entirely inside `ragopt` would make the optimizer the owner of ordinary product operation, creating an opaque semantic boundary.

## 6.2 Current retrieval sweeps

GEC's RRF sweep evaluates combinations of rank constant and vector weight. It obtains channel rankings once and re-fuses them in memory for each cell. This is efficient and causally clean for the parameters under study. The sweep chooses by hit rate, then MRR, then deterministic parameter tie-breakers.

The sweep does not optimize indexing. Chunking, representations, embeddings, lexical analysis, and vector backend are frozen. It does not evaluate reranking or answer behavior. It uses one fixed evaluation set and lacks uncertainty estimates. This is a useful *fusion subproblem*, not a general retrieval optimizer.

RAG-TTC's ANN bakeoff is another well-formed subproblem. It compares approximate rankings with an exact oracle and gates recall and p95 latency. It says little about end-to-end answer quality, and it deliberately excludes embedding latency from vector search timing. Again, the correct response is not to criticize it for limited scope but to place it in a larger multi-fidelity field.

## 6.3 Answer and session evaluation

`ragkit` provides standard retrieval metrics such as precision, recall, hit rate, MRR, and nDCG and rejects mixed target granularity. GEC adds answer-quality judging and detailed strata. Garden's calibration runner drives multi-turn cases against the real chat server, waits for a stable terminal answer, and asserts answers, choices, word count, and source kinds. RAG-TTC contains tool-loop and answer-quality experiments with frozen arm contracts.

These evaluations occur at different semantic levels. Retrieval metrics are cheap and diagnostic but cannot prove answer faithfulness. Judge-based answer metrics can detect some failures but are stochastic and can share model biases. Session calibration exercises routing, tool loops, persistence, and presentation but is expensive and often weakly paired. Production telemetry measures latency and failure under real load but usually lacks counterfactual relevance labels.

The architecture should preserve all levels and specify how evidence moves between them. A candidate that fails a static authorization law should never enter answer evaluation. A candidate that cannot improve retrieval on a paired holdout should usually not consume session-calibration budget. A candidate that passes offline tests must still pass shadow and canary operational gates.

## 6.4 The missing RAG optimization field

A complete field needs four things the current packages do not jointly provide:

- a typed parameter and intervention model covering both build and query behavior;
- a dependency graph that determines which artifacts and evaluations are invalidated;
- a behavior-complete release that can be evaluated and activated as one unit;
- a multi-objective, multi-fidelity decision model that includes freshness, security, reliability, capacity, and user outcome.

This volume supplies those abstractions. `ragopt` remains the campaign and custody engine. `ragkit` supplies the RAG-domain model, build/query interpreters, release semantics, and native evaluation contracts.

EOF
wc -c /mnt/data/rag_functionality_work/v2/The_Semantics_and_Dynamics_of_RAG.md
wc -w /mnt/data/rag_functionality_work/v2/The_Semantics_and_Dynamics_of_RAG.md
```

<details><summary>💭 Thinking</summary>

**Wrote RAG semantics volume and appended Part II architecture**

</details>

```unknown
bash -lc cat >> /mnt/data/rag_functionality_work/v2/The_Semantics_and_Dynamics_of_RAG.md <<'EOF'

# Part III. Corpus evolution and index maintenance

# 16. Source revisions, changes, cursors, and barriers

## 16.1 The source contract

A shared RAG package should not assume that a corpus is one JSON file. It should accept source connectors that can provide a consistent snapshot, an ordered or partially ordered change stream, or both. The minimum interfaces are semantic rather than transport-specific:

```go
type SourceKey string
type RevisionID string
type Cursor string
type SnapshotToken string

type DocumentRevision struct {
    Key         SourceKey
    Revision    RevisionID
    ObservedAt  time.Time
    EffectiveAt *time.Time
    ContentSHA  digest.Digest
    Metadata    map[string]string
    Payload     artifact.Ref
}

type Tombstone struct {
    Key        SourceKey
    Revision   RevisionID
    ObservedAt time.Time
    Reason     string
}

type Change struct {
    Cursor    Cursor
    Upsert    *DocumentRevision
    Delete    *Tombstone
    Barrier   *Barrier
}

type Barrier struct {
    Token     SnapshotToken
    Watermark time.Time
}
```

A connector can expose `Snapshot` when the source supports a repeatable read and `Changes` when it supports a durable cursor. A filesystem connector may scan and produce a synthetic barrier. A Git connector can use commit/tree identity, as RAG-TTC already does. A database connector can use transaction snapshot or changelog position. A web connector may offer only best-effort observed revisions and a capture batch token.

The common contract should not pretend all connectors have the same consistency. Each connector declares:

- whether snapshot reads are repeatable;
- whether cursors are durable and monotone;
- delivery order and duplication guarantees;
- delete visibility;
- maximum lateness or reordering, if any;
- the meaning of its watermark;
- payload immutability and retention;
- subject and data-class policy.

The release manifest records these guarantees so freshness and reproducibility claims are honest.

## 16.2 Stable logical identity

Source key, source revision, document ID, and chunk ID answer different questions. A source key identifies the logical external item. A revision identifies one version of that item. Normalization may create one or many document IDs. Chunk IDs identify exact derived spans under one chunker and document revision.

Using content digest alone as source identity loses delete and rename semantics. Two different source items can contain identical text and still require separate lineage and policy. Conversely, a source key can remain stable while content changes. The model therefore carries both logical and content identity.

Renames are source-specific. Git can represent a delete and add unless similarity analysis is applied; a database row key remains stable. RAG semantics usually need only stable source lineage and correct current content, not a universal rename detector. Connectors can emit an optional predecessor relation when meaningful.

## 16.3 Admission and policy

Admission is not a preprocessing convenience. It determines the knowledge and disclosure boundary. RAG-TTC's Git snapshot excludes vendor/generated content and applies size and test-data policy. GEC documents carry access scopes and source roles. Garden distinguishes product pages, guides, and structured product facts.

An admission decision should be retained as:

```go
type Admission struct {
    Key         SourceKey
    Revision    RevisionID
    Decision    AdmissionDecision // admit, exclude, quarantine
    RuleID      string
    PolicyID    digest.Digest
    Explanation string
}
```

Excluded items do not silently disappear from operational reports. Counts and reasons support corpus coverage analysis. A policy change is a knowledge- and security-changing intervention even if source content is unchanged; it invalidates normalized corpus state and downstream artifacts for affected items.

No document lacking required access metadata should default to public. GEC's current `scopesAllow` behavior treats unscoped content as non-returnable, which is the safe default. Build verification should reject rather than merely hide such documents, because a different query path might omit the filter.

## 16.4 Normalization as a versioned function

Normalization converts source payload into canonical text and metadata. It handles HTML removal, whitespace, metadata names, redaction, product-field rendering, and prompt-injection hygiene. It must be versioned because a code change can alter every downstream digest even when source revisions are fixed.

A normalizer should be a pure function over an immutable payload artifact and a specification:

```go
type Normalizer interface {
    Spec() NormalizeSpec
    Normalize(context.Context, DocumentRevision) ([]NormalizedDocument, error)
}
```

`NormalizeSpec` includes semantic version, configuration, parser identity, and data policy. The output includes exact source lineage, warnings, and extracted fields. Any use of current time, locale, network fetch, or mutable database state must be explicit as an additional input; otherwise reproducibility is false.

## 16.5 Barriers and consistent snapshots

A barrier separates open-ended ingestion from one release intent. Suppose changes continue arriving after barrier $\tau$. They belong to a later release unless the current build is explicitly amended and receives a new source snapshot identity. This avoids moving-target builds.

For a full snapshot connector, the barrier token may be a Git commit, database snapshot ID, or corpus manifest digest. For a change stream, a barrier means all source changes through cursor $c$ have been materialized into the logical document map. The coordinator persists both cursor and normalized snapshot digest.

Cross-source releases require a vector of barriers, one per connector. There may be no global transaction across sources. The release records capture times and watermarks, and product policy defines acceptable skew. A knowledge index and structured fact database may intentionally have different epochs; the release makes the skew visible.

## 16.6 Late and corrected events

A connector can observe an older effective revision after a newer one. The source adapter must define conflict order. A common rule is highest source revision sequence, then effective time, then deterministic revision ID, never raw arrival order. Corrections can supersede prior revisions explicitly.

When a late event changes the logical state for a barrier already activated, it cannot mutate the release. It triggers a new corrective release. Audit links the correction to the affected prior release and measures stale exposure duration.

## 16.7 Deletion semantics

Deletion has three layers:

1. **Logical tombstone:** the source item is no longer part of current corpus state.
2. **Query invisibility:** new release views cannot return its documents, chunks, representations, or structured projections.
3. **Physical erasure:** stored artifacts are removed after retention, legal, and audit policy.

These layers must not be conflated. A delta overlay can make a document immediately invisible with a tombstone while old immutable base bytes remain until compaction. In-flight leases on an old release may still access it unless deletion policy requires emergency revocation. Security deletions may need a registry-level quarantine that prevents new and existing queries from using affected releases.

# 17. Incremental derivation algebra

## 17.1 From snapshots to differences

Let corpus state be represented as a multiset or finite map. The difference between states is a signed change $\Delta D$ such that:

$$
D_{t+1} = D_t \oplus \Delta D.
$$

For a deterministic transformation $F$, an incremental form $F^\Delta$ should satisfy:

$$
F(D_t \oplus \Delta D) = F(D_t) \oplus F^\Delta(D_t, \Delta D).
$$

This is the fundamental incremental correctness equation. It says maintained output after applying derived changes equals a fresh evaluation of the original transformation. The right side may reuse prior output; the left side is the oracle.

Not every stage has an efficient local differential, but every stage can be incrementally maintained by recomputing the affected partition and taking a set difference. The package should optimize only after specifying the equation.

## 17.2 Document-local chunking

Current chunkers operate independently per document. Let $C(d)$ be the chunk set for document $d$. Then corpus chunking is the disjoint union:

$$
C(D) = \biguplus_{d \in D} C(d).
$$

A document upsert affects only old and new chunks for that document:

$$
\Delta C = -C(d_{old}) \uplus C(d_{new}).
$$

Content-based chunk IDs cause unchanged chunks to survive when their byte range and text remain equal. An insertion near the beginning can shift ranges and invalidate later chunks even if text is unchanged. A future chunker can use structural anchors to increase identity stability, but this changes lineage semantics and requires evaluation.

Global chunkers, cross-document deduplication, or corpus-level clustering break document locality. Their specs must declare a larger invalidation scope. The impact planner derives affected closure from stage properties rather than assuming locality universally.

## 17.3 Representation differentials

Representations are derived per chunk and kind. For deterministic raw or breadcrumb representations, unchanged chunk identity and representation spec imply exact reuse. Generated summaries or questions additionally depend on prompt, provider/model version, decoding policy, and retained output.

A representation key can be:

$$
K_P = H(\mathsf{chunkDigest},\mathsf{kind},\mathsf{promptID},\mathsf{modelID},\mathsf{decoderID}).
$$

When the key is unchanged, cached output is valid. When a prompt changes, every representation of that kind is affected even if chunks are unchanged. This is why the optimization dependency graph matters: a prompt intervention invalidates representation and embedding artifacts but need not recompute normalization or chunking.

Generated output can be nondeterministic. Content-addressed cache turns one sampled output into retained material. A candidate that intentionally resamples must declare a new stochastic replicate rather than reuse the old key.

## 17.4 Embedding differentials

Embedding is pointwise over representation text under model and normalization identity:

$$
E(P) = \{(id(p), e_m(text(p))) : p \in P\}.
$$

Additions require embeddings; deletions remove vector entries; unchanged representation digests reuse vectors. A model, dimension, pooling, or normalization change invalidates the whole affected representation set.

Provider aliases are unsafe cache identities. The manifest should use an immutable model version or provider-reported deployment revision. If the provider cannot supply one, the release records the alias plus observation time and retained vector digests; reproducibility is then material rather than semantic.

## 17.5 Lexical-index differentials

A lexical index supports upsert and delete when the backend exposes stable document IDs and snapshot or commit semantics. The logical differential is straightforward. Physical scoring statistics such as document frequency change globally, but an incremental backend updates them internally. The correctness oracle compares search results to a clean build at the same state.

Field mapping and analyzer changes require rebuilding the affected index because existing terms were produced under different semantics. Title boosts and token filters are part of index spec. GEC synonym expansion currently occurs at query time; moving synonyms into analyzer configuration would change both invalidation scope and query semantics.

## 17.6 Vector-index differentials

Exact vector storage can upsert and delete rows directly. ANN structures are more complicated. Some support dynamic insertion but weak deletion, background repair, or nondeterministic topology. A backend contract should distinguish:

- logical update acceptance;
- visibility epoch;
- delete/tombstone semantics;
- query snapshot isolation;
- compaction requirement;
- recall degradation under updates;
- deterministic rebuild behavior.

An ANN candidate can pass static recall and still degrade after many updates. Optimization and acceptance tests need update-sequence workloads and periodic exact-oracle checks.

## 17.7 Algebra of tombstones

Represent current output as a signed multiset or as `(base, additions, tombstones)`. A query view is:

$$
V = (B \cup A) \setminus T.
$$

The tombstone set must dominate both base and older additions. A newer upsert after deletion carries a higher source revision and can reintroduce the logical key with a new derived identity. Comparing only chunk IDs is insufficient; tombstones should target logical document/revision lineage so every derived representation is excluded.

## 17.8 Incremental equivalence tests

For generated random document states and change sequences:

1. build $F(D_0)$ cleanly;
2. apply changes incrementally to obtain $M_n$;
3. build $F(D_n)$ cleanly;
4. compare canonical logical outputs;
5. compare exact-backend rankings over generated queries;
6. compare approximate backend metrics within declared tolerance;
7. verify deleted lineage is absent;
8. restart from checkpoints at arbitrary points and repeat.

This property test should be part of backend certification. It is more important than unit tests for individual update methods because it checks the composed invariant.

# 18. Backend update models and the base-plus-delta design

## 18.1 Four update models

There are four common production models.

**Full immutable rebuild.** Every release contains a complete new index. This has the simplest correctness and rollback semantics but the worst freshness and rebuild cost.

**In-place mutable index.** Changes update the active index. Freshness is good, but query snapshot consistency, rollback, and audit are hard. A failed update can corrupt the active state.

**Immutable base plus delta overlay.** A stable base is queried together with a smaller delta containing upserts and tombstones. New releases can publish deltas quickly; compaction periodically produces a new base.

**Partitioned immutable segments.** Changes create immutable segments and tombstone maps; queries search many segments and merge results. This generalizes the overlay but requires segment management and score comparability.

For the current systems, base plus delta is the recommended first dynamic model. It extends existing immutable bundles without forcing a mutable active index and keeps rollback as release selection.

![Incremental maintenance with immutable base, delta overlay, tombstones, and a clean-build oracle.](figures/07_incremental_index_overlay.png){width=62%}

## 18.2 Release view

A release can reference one base artifact and zero or more ordered deltas:

```go
type IndexView struct {
    Base       artifact.Ref
    Deltas     []artifact.Ref
    Tombstones artifact.Ref
    Watermark  corpus.Watermark
}
```

The query runtime opens the view under one lease. Lexical and vector searchers query base and deltas, apply tombstones and logical-key supersession, normalize scores if necessary, and fuse segment candidates deterministically. The view is immutable even if a delta was built recently.

A new small change produces a new delta and a new release manifest. It does not mutate the prior active release. Activation can therefore switch atomically and rollback instantly.

## 18.3 Score comparability

Lexical scores from separately built segments may not be directly comparable because collection statistics differ. Options include:

- search base and delta separately and fuse ranks rather than raw scores;
- use a backend that maintains global statistics;
- rescore candidate documents against a shared global corpus model;
- compact frequently enough that delta bias is bounded and evaluated.

Rank fusion is pragmatic and aligns with existing RRF infrastructure. It can, however, overweight small delta segments. The release query policy must identify segment-fusion behavior, and optimization should include freshness strata so new content is neither suppressed nor unfairly promoted.

Vector similarity is usually more comparable when all vectors use the same embedding model and normalization. Approximate backends can still have segment-specific recall. Query each segment with sufficient $k$, merge by exact similarity where vectors are available, and evaluate against a clean exact view.

## 18.4 Delta size and compaction policy

Compaction triggers can depend on:

- number or byte size of deltas;
- tombstone ratio;
- query fan-out and p95 latency;
- ANN recall degradation;
- base age and source watermark lag;
- operational maintenance window;
- cost of continuing overlay search versus rebuild.

Compaction builds a new complete base at a fixed source barrier. It is verified against the overlay view before activation. Once active and drained, old segments can be retired under retention policy.

Compaction policy is operational when it preserves view semantics. Under approximate indexes and deadlines it may change ranking and latency; then it is part of release behavior or at least protected operational configuration.

## 18.5 Backend capability interface

A shared capability model might be:

```go
type Capabilities struct {
    FullBuild          bool
    Upsert             bool
    Delete             bool
    SnapshotRead       bool
    FilterPushdown     bool
    DeterministicBuild bool
    ExactScores        bool
    Compact            bool
}

type Builder interface {
    Spec() IndexSpec
    Build(context.Context, BuildInput, EventSink) (artifact.Ref, error)
}

type DeltaBuilder interface {
    BuildDelta(context.Context, BaseDescriptor, []IndexChange, EventSink) (artifact.Ref, error)
}

type Opener interface {
    Open(context.Context, IndexView) (SnapshotSearcher, error)
}
```

`SnapshotSearcher` guarantees immutable view behavior for its lifetime. Product query code should not call point updates on it.

## 18.6 Full rebuild remains first-class

Incremental maintenance does not eliminate full builds. Full builds serve as:

- a correctness oracle;
- a compaction operation;
- recovery when lineage or cache integrity is uncertain;
- migration across incompatible schemas or backends;
- periodic defense against accumulated approximation drift.

The coordinator should support both from one `BuildSpec`. An incremental plan can fall back to full build when affected closure exceeds a threshold or backend capability is insufficient.

# 19. Durable build coordination and resumability

## 19.1 Coordinator responsibilities

The production coordinator owns:

- build intent registration and idempotency;
- source capture and barrier custody;
- impact-plan construction;
- stage scheduling and resource admission;
- immutable artifact and cache references;
- append-only build events and checkpoints;
- retry, quarantine, cancellation, and operator commands;
- verification, evaluation, and release registration;
- metrics and status projection.

It does not own product source meaning, retrieval quality metrics, or activation authority. Product adapters supply connectors, normalization policy, and evaluators. `ragkit` supplies the coordinator contracts and local implementation. An external scheduler can later drive the same state machine.

## 19.2 Build intent identity

A build intent identifies the desired semantic result:

```go
type BuildIntent struct {
    Product          string
    SourceRequest    corpus.CaptureRequest
    BaseRelease      release.ID
    BuildSpec        BuildSpec
    QuerySpec        query.Spec
    AuxiliaryAssets  []artifact.Ref
    EvaluationPolicy eval.PolicyID
}
```

The intent ID excludes worker count, retry backoff, and machine placement. It includes every input that can alter release material or eligibility. Re-registering the same intent returns the existing run or terminal result.

A refresh intent and an optimization intent can share the same type but differ in locks. A content refresh changes source barrier while freezing build/query policy. An optimization candidate freezes source barrier while changing one declared asset. The two loops must not be conflated because their causal interpretation differs.

## 19.3 Stage DAG and progress

The coordinator derives a DAG of stage instances from impact plan. Progress is measured by semantic work units, not only percent. For example:

```text
capture: barrier acquired
normalize: 8,402 / 8,402 source revisions
chunk: 8,397 / 8,397 admitted documents
represent.summary: 12,110 / 16,884 chunks, 9,332 cache hits
embed: 55,100 / 61,004 representations, 54,911 cache hits
lexical-index: sealed
vector-delta: building
verify: pending
```

Each count has a denominator fixed by the plan. Dynamic discovery creates a new plan version or explicit subplan, not a silently changing denominator.

Operator status should show blocked resources, retry storms, cost budget, source watermark, quarantines, and the last committed checkpoint. This information exists partially in current flow observations and design records but lacks a shared durable projection.

## 19.4 Scheduler model

The first implementation should be a fixed coordinator, not a general workflow language. RAG builds have known semantic stages and domain-specific verification. A local process with a durable SQLite event store and blob/artifact backend is sufficient for one active build. Cloud scheduling can invoke one coordinator job rather than creating a queue message for every chunk.

Within stages, `ragkit/flow` handles bounded concurrency and provider calls. This separation gives operational flexibility: the same coordinator can run locally, in a container job, or under a workflow service while preserving events and checkpoints.

## 19.5 Leases and fencing

A build lease prevents two coordinators from committing the same intent concurrently. It includes a fencing token. Artifact commits and checkpoint writes include the token; stale workers cannot publish after lease loss.

Long provider calls may finish after cancellation or lease expiry. Their content-addressed outputs can be stored in a neutral cache if they verify, but they cannot advance the cancelled build without a valid fence. This salvages expensive work without violating run custody.

## 19.6 Resume equivalence

Let event prefix $P$ reduce to coordinator state $s$. Resume reconstructs pending work from $(intent, plan, P)$ and continues with suffix $U$. The terminal release should be equivalent to uninterrupted execution with the same provider outputs:

$$
\mathsf{reduce}(P \cdot U) = \mathsf{runFromStart}(intent,\omega).
$$

Property tests can interrupt after every event boundary, reopen the store, and compare terminal manifests. Tests should also duplicate commands and provider completions to verify idempotence.

## 19.7 Publication and activation separation

The coordinator can register a release as verified and eligible. It can produce a promotion plan containing expected current release, candidate release, gate report, rollout cohort, and rollback recommendation. A distinct activation authority applies it.

This separation supports both scheduled content refresh and optimization. A routine content refresh may have an automated policy that activates after integrity, freshness, and regression gates. A relevance optimization may require human review. Both use the same activation API.

# 20. Freshness, time, and temporal correctness

## 20.1 Four clocks

RAG freshness is not one timestamp. At least four clocks exist:

1. **Source effective time:** when the information became true in the source domain.
2. **Connector observed time:** when the RAG system saw the revision.
3. **Release activation time:** when new queries began using it.
4. **Query time:** when the user asked.

A fifth clock, frontend presentation time, matters for live systems. Lag can be decomposed:

$$
\mathsf{staleness} =
(t_{observed}-t_{effective}) +
(t_{activated}-t_{observed}) +
(t_{query}-t_{activated\_content}).
$$

The last term is zero for content captured in the active release and positive for newer unseen revisions.

## 20.2 Freshness objectives

A product can define:

- maximum source-to-observation lag;
- maximum observation-to-activation lag;
- maximum active-release watermark age;
- percentile objectives by source class;
- emergency correction objectives for security-sensitive content;
- maximum cross-source skew inside a release.

A static documentation corpus may tolerate daily refresh. Product prices or inventory may require structured live tools instead of index refresh. The architecture should not force rapidly changing authoritative facts into a text index when a structured source has better temporal semantics.

## 20.3 Watermark propagation

Every derived artifact carries the source barrier vector. A release exposes watermarks to the query trace. Answers and source cards can optionally display "knowledge through" time when users need temporal context.

A query can impose freshness requirements. If the active release watermark is older than requested policy, the runtime can abstain, invoke a live structured/connected source, or route to a fresher release. It should not silently answer from stale material while claiming current authority.

## 20.4 Temporal evaluation

Random train/test splits over a static evaluation set do not measure corpus evolution. Evaluation should include temporal holdouts:

- queries whose relevant content was added after the optimization training window;
- updates that modify previously correct facts;
- deletions and retractions;
- late-arriving revisions;
- source-policy changes;
- queries issued during base-plus-delta periods and after compaction.

Metrics include time-to-retrievable, time-to-answerable, stale-answer rate, deleted-content exposure, and freshness-conditioned relevance. The candidate and incumbent should be evaluated at the same source barriers for relevance comparisons; refresh performance is evaluated as a separate time process.

## 20.5 Session consistency under refresh

A per-turn lease ensures one turn does not mix epochs. Across turns, the conversation can move to a newer release. Prior assistant messages and evidence remain historical facts from their original releases. Follow-up query rewriting may reference those messages. The trace should preserve release lineage so diagnosis can reconstruct why a newer turn differs.

A product can choose to notify the model that the knowledge release changed between turns or simply treat prior evidence as quoted conversation context. For regulated or administrative use, explicit epoch markers are preferable.

## 20.6 Emergency invalidation

Some deletions cannot wait for normal draining. A registry can mark a release `Revoked` for a policy scope. New acquisitions fail or resolve to a safe prior/new release. In-flight requests check revocation before remote disclosure and final emission. This is stronger than immutable draining and should be reserved for security or legal incidents because it can break ongoing turns.

Emergency invalidation must be auditable: affected source keys, releases, actors, reason, start/end time, and queries blocked or completed. Physical artifact erasure follows separate policy.

EOF
wc -c /mnt/data/rag_functionality_work/v2/The_Semantics_and_Dynamics_of_RAG.md
wc -w /mnt/data/rag_functionality_work/v2/The_Semantics_and_Dynamics_of_RAG.md
```

<details><summary>💭 Thinking</summary>

**Wrote Parts III and IV on RAG corpus evolution and retrieval optimization**

</details>

```unknown
bash -lc cat >> /mnt/data/rag_functionality_work/v2/The_Semantics_and_Dynamics_of_RAG.md <<'EOF'

# Part V. RAG in production

# 27. Serving APIs and frontend contracts

## 27.1 The service boundary

The shared production boundary should expose semantic operations rather than an HTTP framework. Product servers already have mature conversation, authentication, persistence, tool, and WebSocket stacks. `ragkit` should fit beneath them.

A minimal service surface is:

```go
type Service interface {
    Search(context.Context, SearchRequest) (SearchOutcome, error)
    Answer(context.Context, AnswerRequest, EventSink) (AnswerOutcome, error)
    StartAgentTurn(context.Context, AgentRequest, EventSink) (TurnOutcome, error)
}
```

The methods are separate because their terminal conditions differ. Each request contains product scope, subject context, conversation/turn IDs, query input, deadline, and optional release-selection constraints. The caller cannot pass arbitrary access scopes as model-controlled fields; product authorization constructs `SubjectContext`.

The service internally acquires a release lease or accepts a lease supplied by a conversation runtime. The outcome always includes release ID and trace summary. An ordinary Go error represents failure to perform the API contract itself; domain failures are typed outcomes so they remain observable and evaluable.

## 27.2 Search outcome

A direct search outcome should contain:

```go
type SearchOutcome struct {
    Status       SearchStatus // complete, degraded, failed, cancelled
    ReleaseID    release.ID
    QueryPlanID  query.PlanID
    Hits         []EvidenceHit
    Warnings     []Warning
    Trace         trace.Ref
    Timing        Timing
}
```

`EvidenceHit` carries stable chunk/source revision, rank, finite score, channel contributions, evidence kind, authorization certificate reference, and presentation metadata. It does not copy every source payload by default; hydration policy determines what is returned to the product.

A degraded status distinguishes fallback from intended behavior. This lets GEC preserve its fail-open reranker while making it measurable.

## 27.3 Answer outcome

An answer outcome contains admitted evidence and a validated projection:

```go
type AnswerOutcome struct {
    Status          AnswerStatus
    ReleaseID       release.ID
    EvidenceSession EvidenceSessionID
    Answer           ValidatedAnswer
    Evidence         []EvidenceRef
    Warnings         []Warning
    Trace             trace.Ref
    Usage             Usage
}
```

The answer can be text, a typed JSON contract, choices, or a product-specific envelope. Shared code owns generic grounding and citation relationships. Product code owns widget schemas and domain fields.

The `EventSink` receives lifecycle and presentation events. It should be idempotent by event ID and return an error when durable emission fails. The product decides whether a failure to record an observation is fatal; the shared plan can label the requirement.

## 27.4 Agent-turn boundary

An agent request includes conversation snapshot, allowed tool capabilities, release lease policy, model profile, and bounded budgets. Product code supplies tool implementations and server-owned authorization. The shared RAG runtime supplies search tools that are release- and evidence-session-aware.

The agent result retains the complete typed trajectory or a reference to it. Tool results carry causation and release IDs. A model-generated tool argument cannot override product scope, release, or provider data policy.

RAG-TTC's current `SearchTool` can implement this interface with little semantic loss. Its route table becomes a release query asset; its evidence ledger becomes a shared evidence session; connected augmentation remains a product/provider adapter.

## 27.5 Release resolution API

```go
type Resolver interface {
    Acquire(context.Context, AcquireRequest) (*Lease, error)
}

type AcquireRequest struct {
    ProductScope   string
    Subject        SubjectContext
    ConversationID string
    TurnID         string
    CohortKey      string
    Pinning        PinningPolicy
}

type Lease struct {
    ID() release.ID
    Manifest() release.Manifest
    Runtime() RuntimeResources
    Close() error
}
```

`RuntimeResources` exposes typed searchers, evidence stores, validators, structured snapshots, and policy only through immutable interfaces. It should not expose artifact paths for product code to reopen independently, which would permit mixed releases.

## 27.6 Transport adapters

HTTP, gRPC, CLI, model tools, and WebSockets are adapters. A direct REST endpoint can return `SearchOutcome`. A chat server can translate lifecycle events to its timeline. A model tool can serialize a bounded subset of evidence. A CLI can print trace details.

Adapters must preserve IDs and status. They should not convert degraded success into ordinary success or drop release lineage. Public/customer adapters may redact internal trace fields while preserving a safe trace reference.

## 27.7 Frontend event contract

A RAG-aware frontend event should include:

- conversation and turn identity;
- event and entity versions;
- release ID;
- semantic kind: retrieval started/completed, source admitted, answer delta, answer terminal, choices, widget, warning, cancellation;
- customer-safe payload;
- optional developer projection reference;
- causation and correlation IDs.

The server can expose sources before answer completion or only at terminal validation. That is a product policy and should be consistent. Source cards must reference the turn's release, not current active release.

## 27.8 Snapshot API

A snapshot response contains:

```go
type Snapshot struct {
    StreamID       string
    ThroughOrdinal uint64
    Entities       []EntitySnapshot
    SchemaVersion  string
}
```

The subscribe request supplies the last applied ordinal. The server either sends a suffix or a new snapshot plus suffix. The client discards duplicate event IDs and events at or below the snapshot boundary.

GEC's current manager already sends the last snapshot ordinal and buffers events around hydration. The new contract formalizes entity versions and deduplication rather than replacing the stack.

## 27.9 Product-specific projection boundary

Garden's evidence-bound widgets should remain product-owned because product fields, comparisons, and conflict rules are domain semantics. The shared package can provide:

- evidence and structured-fact references;
- projection session bound to a release/evidence session;
- validators that every payload field cites admitted provenance;
- generic source-card types;
- event envelope and replay laws.

GEC can project administrative sources and developer traces differently. RAG-TTC can expose tool-loop diagnostics. One universal widget schema would erase useful distinctions.

# 28. Reliability, deadlines, caching, and backpressure

## 28.1 Reliability is stage-specific

A RAG request has multiple failure domains: release resolution, local index, query embedding, connected retrieval, reranking, hydration, generation, validation, event persistence, and frontend transport. Treating all as one `500` loses the ability to degrade safely.

Each stage declares:

- whether it is required or optional;
- retry policy and idempotency;
- fallback policy;
- deadline allocation;
- whether partial output is valid;
- whether failure affects release health;
- what trace and metric it emits.

A local index corruption is not equivalent to a reranker timeout. The former should quarantine a release. The latter may degrade one request and trip a provider circuit breaker.

## 28.2 Deadline algebra

Let total deadline be $D$. A plan allocates stage budgets $d_i$ and reserve $r$:

$$
\sum_i d_i + r \le D.
$$

Parallel stages use maximum elapsed time rather than sum, but shared provider and queue budgets still matter. Static allocation is simple; adaptive allocation can transfer unused budget. The plan records allocation policy.

A stage starting without enough remaining budget should fail fast or choose a cheaper fallback. For example, skip remote reranking when only validation reserve remains. This changes outcomes and belongs to release query policy.

Timeout errors should identify queue, connection, provider, or response phase where possible. End-to-end latency metrics alone cannot diagnose budget misuse.

## 28.3 Retry semantics

Retries are safe only for idempotent operations or with idempotency keys. Local search and immutable hydration are safe. Provider generation may produce a new sample and incur cost; a retry is a new trace branch. Tool calls to structured systems may have side effects and require product-specific guarantees.

Retry policy includes maximum attempts, backoff, retryable error classes, and remaining-budget check. The final outcome records attempts. A successful retry is not trace-equivalent to first-attempt success and can be an early incident signal.

## 28.4 Circuit breakers and health

Provider health is tracked per endpoint/model/data class. A circuit breaker can prevent repeated slow failures and select a declared fallback. It must not silently route protected data to a different provider with a different policy.

Release health combines artifact health and dependency health. An index-open failure quarantines the release on that replica and should stop new leases if widespread. A reranker outage can mark a route degraded without invalidating the index release, but the release behavior remains the same because fallback policy is declared.

## 28.5 Cache layers

RAG systems have several caches with different semantics:

- source payload cache;
- normalized document and derivation cache;
- generated representation cache;
- embedding cache;
- opened release/artifact cache;
- query embedding cache;
- channel result cache;
- reranker result cache;
- final answer or session replay cache;
- frontend snapshot cache.

Every cache key includes all semantic inputs. A query-result cache must include release ID, subject-policy partition, query plan, route, filters, locale, and query text. Caching authorized results under only text and bundle ID is unsafe.

Final answer caching is particularly difficult because conversation context, subject, stochastic policy, and presentation change. Prefer caching deterministic intermediate results unless product semantics make final answers explicitly reusable.

## 28.6 Cache soundness laws

For cache $C_f$ of operation $f$:

1. equal keys imply inputs equivalent under $f$'s denotation;
2. a cached value verifies against the key and output schema;
3. cache hit and fresh execution are observationally equivalent under declared properties;
4. protected subject partitions cannot collide;
5. cache invalidation follows semantic identity rather than time alone;
6. provider outputs retained as material remain linked to original policy and model identity.

Property tests can mutate each input field and confirm whether key changes according to the operation spec.

## 28.7 Backpressure

Under load, the system should reject or queue work before it exhausts providers or memory. Separate pools for query embedding, reranking, generation, connected retrieval, and build work prevent a large refresh from starving interactive queries.

Admission considers deadline, estimated cost, tenant quota, and current queue. A request rejected before disclosure returns a typed overloaded outcome. An accepted request receives a budget reservation.

Build workloads use lower-priority or separately provisioned resources. Semantic caches can be shared, but resource queues should not.

## 28.8 Load shedding and quality degradation

A declared degradation ladder may be:

1. full hybrid plus reranker;
2. hybrid without reranker;
3. lexical plus vector with lower depth;
4. lexical-only local search;
5. safe abstention.

The ladder must respect product and query class. A vector-only corpus cannot use lexical fallback. A security-sensitive query may prefer abstention over connected search. Every step has its own plan ID and outcome warning.

Quality evaluation must include degraded plans because production traffic will use them under stress. Reliability is the weighted behavior over healthy and degraded states, not ideal-path quality alone.

## 28.9 Cancellation and resource reclamation

Context cancellation should stop queued work, propagate to providers, and prevent nonessential post-processing. Provider APIs may not cancel immediately; traces distinguish requested from confirmed cancellation. Results arriving after cancellation can populate safe semantic caches but not emit customer events.

Release leases close after terminal persistence, not merely after model completion, if frontend/source projection still needs release artifacts. Long-running streams must renew process-level lease heartbeats.

## 28.10 Graceful shutdown

A server shutdown stops acquiring new leases, marks the replica draining, waits for bounded in-flight work, persists terminal cancellation for forced exits, closes release handles, and flushes trace/event stores. Startup preloads active release and verifies dependencies before accepting traffic.

This lifecycle should be tested with active agent turns and snapshot streams. Current startup-bound services already close bundles; the shared release manager generalizes the behavior across hot activations.

# 29. Security, privacy, and trust boundaries

## 29.1 Trust zones

The system has at least five trust zones:

1. source systems and connector credentials;
2. local corpus and index artifact plane;
3. product server and authorization policy;
4. remote model, embedding, reranker, or connected-search providers;
5. customer and developer frontends.

Data can cross a boundary only through a typed operation with policy. Retrieval correctness is subordinate to authorization and provider disclosure rules.

## 29.2 Authorization before ranking effects

Authorization should be applied as early as possible. Source admission can exclude globally prohibited data. Index partitioning and metadata filters constrain channel search. Local authorization verifies candidates before text hydration or remote stages. Final presentation rechecks evidence references.

GEC's current post-rerank filter violates the remote non-disclosure property. The immediate fix is to prefilter candidate IDs using local chunk/document metadata before `rerank`. The complete fix is authorized top-$k$ retrieval through filter pushdown or scope-partitioned indexes, followed by an authorization certificate.

A regression test should use a reranker spy that fails the test if it receives unauthorized marker text. Returned-result tests alone will not catch the disclosure.

## 29.3 Noninterference goal

A strong ideal is that unauthorized documents do not influence observable results, including ranks and timing. Full noninterference is difficult because global index statistics or shared ANN topology can create indirect effects. The production requirement should at least guarantee no content disclosure and no unauthorized result; products can decide whether rank-position influence is acceptable.

For high-assurance administrative corpora, per-scope indexes or cryptographically separate partitions provide a clearer model. The route selects partitions authorized for the subject and fuses only those rankings.

## 29.4 Provider data policy

Each remote provider configuration declares allowed data classes, regions, retention, training use, and logging policy. A provider call includes a policy decision reference. Rerankers receive source text; embedding providers receive corpus or query text; generators receive evidence and conversation. These are distinct disclosure categories.

Fallback cannot change provider policy implicitly. If primary provider is unavailable and backup is not permitted for the data class, the correct outcome is local fallback or abstention.

## 29.5 Prompt injection in sources

Source normalization should mark or remove active content such as scripts and hidden instructions. Retrieval should treat source text as evidence, not system instructions. Context formatting clearly delimits source material and tells the model not to follow embedded commands.

Tests should include documents that ask the model to ignore policy, reveal secrets, call tools, or fabricate citations. Grounding and tool policy should prevent source text from granting capabilities.

Source content remains untrusted even when authorized. Structured facts from trusted databases have different authority and should be typed separately.

## 29.6 Tool argument authority

Model-visible tool schemas expose query terms, requested limits, or route hints only when safe. Access scopes, tenant, release, provider policy, and database permissions come from server context. GEC already follows this principle in its knowledge tool.

The tool runtime validates every argument and caps limits. Unknown routes fall back or fail according to release policy. Tool descriptions are versioned release assets because they influence model behavior but do not confer authority.

## 29.7 Evidence provenance

Every evidence item should support a chain:

```text
release -> source barrier -> source revision -> normalized document
        -> chunk span -> representation contribution -> ranked hit
        -> authorization certificate -> admitted evidence -> citation/widget field
```

Structured facts add database snapshot/query/item lineage. Connected retrieval adds provider request and response artifact identity with weaker reproducibility classification.

This chain enables audits, deletion impact analysis, stale-answer diagnosis, and source-card rendering. Missing links are verification failures, not optional metadata.

## 29.8 Logging and traces

Trace payload policy uses references and digests by default. Sensitive query/evidence text can be stored in an authorized encrypted artifact store with retention, not duplicated across logs. Customer frontend receives only safe projection. Developer mode still enforces subject authorization.

A trace redaction bug can be more serious than a retrieval bug because logs have broader access and retention. Static trace-schema review and payload scanners belong in release gates.

## 29.9 Multi-tenant isolation

Release scope, indexes, caches, and query keys include tenant where required. Shared public corpus can be referenced by several tenant releases, but private delta overlays and subject filters remain isolated. Provider rate and cost quotas are tenant-aware.

Cross-tenant cache reuse is permitted only for public immutable inputs and operations whose output is independent of tenant policy. The cache artifact records its sharing class.

## 29.10 Security under optimization

The candidate system cannot relax security constraints to improve relevance. Policy assets are immutable and reviewed. Proposers operate within a capability sandbox. Security test suites are hidden from unrestricted automated proposers when exposure would make gaming easy.

Online shadow execution uses the same authorization and provider policy as production. Candidate traces are subject to the same retention and redaction rules.

# 30. Observability, SLOs, and runtime diagnosis

## 30.1 Observability model

Observability should answer four questions:

1. What source and release state existed?
2. What plan and transitions executed?
3. What outcome and evidence reached the user?
4. Why did this differ from an expected or comparison run?

Metrics alone answer the second question poorly. Traces, release manifests, evidence lineage, build events, and frontend event logs must be linked.

## 30.2 Build telemetry

Build metrics include:

- source items captured, admitted, excluded, deleted, and late;
- source watermark and capture lag;
- affected versus reused documents/chunks/representations/vectors;
- cache hits and provider calls;
- stage throughput, queue, retries, and quarantines;
- cost and resource usage;
- delta size, tombstone ratio, and compaction trigger;
- verification and evaluation results;
- time from observation to verified and active release;
- activation conflicts and rollback.

Metrics carry build intent, source barrier, and release labels. Avoid unbounded document IDs as metric labels; detailed item data belongs in traces/artifacts.

## 30.3 Query telemetry

Query metrics include:

- requests by interpreter and route;
- release and cohort;
- channel success/timeout/failure;
- candidate and evidence counts;
- filter selectivity and authorized starvation indicators;
- reranker invocation/fallback;
- context tokens and source diversity;
- generation and validation outcome;
- tool calls and iterations;
- end-to-end and stage latency;
- cancellation and partial output;
- provider usage and cost;
- frontend terminal delivery.

A `complete` counter without `degraded` dimension hides provider incidents. A quality dashboard should stratify by path actually executed.

## 30.4 Freshness SLOs

Example objectives are:

- 99% of source revisions observed within 15 minutes for class A;
- 99% of admitted revisions active within 60 minutes of observation;
- active release watermark no older than 24 hours for documentation;
- security tombstones block new acquisitions within 5 minutes;
- cross-source release skew below a declared bound.

The exact numbers are product decisions. The architecture exposes the clocks required to measure them.

## 30.5 Query SLOs

Define SLOs by interpreter and route. Direct search can have a lower latency target than agent turns. A hybrid-rerank route has different budget from lexical fallback. Report p50/p95/p99 and success/degraded/abstain separately.

A terminal outcome is not enough if the frontend never applies it. End-to-end completion spans submission reservation, query runtime, durable event persistence, WebSocket delivery, and client reduction where measurable.

## 30.6 Quality monitoring

Production has sparse labels. Use a mix of:

- sampled human review;
- structural grounding validators;
- calibrated model judges;
- user corrections and follow-up signals;
- retrieval contribution and empty-evidence alerts;
- canary paired shadow judgments;
- regression cases mined from incidents.

Judge scores are not SLOs unless calibrated and audited. They are indicators. Safety invariants and operational objectives remain directly measurable.

## 30.7 Trace-based diagnosis

A retrieval miss investigation should reconstruct:

1. source revision and active release watermark;
2. whether the expected document was admitted and indexed;
3. chunk/representation identities and index membership;
4. query rewrite and route;
5. per-channel ranks and filters;
6. fusion and reranker movement;
7. evidence admission and context budget;
8. answer/tool behavior;
9. frontend projection.

The trace schema and artifact references should make this possible without rerunning live providers. A replay can test counterfactual policy changes against retained intermediate artifacts.

## 30.8 Release health and automatic action

The release manager aggregates hard health signals. Examples:

- index open/verification failures;
- query error rate above threshold;
- security invariant failure;
- deleted-content exposure;
- severe latency or provider-cost regression;
- frontend terminal-event failure.

A canary can auto-rollback on hard signals. An active stable release can be quarantined and rolled back under incident policy. Soft quality drift opens an investigation rather than immediate automation.

## 30.9 Service-level evidence

SLO evaluation itself should be reproducible. Retain the time window, metric query/version, release cohorts, exclusions, and decision result. Promotion reports link to this evidence. This applies `ragopt`-style custody to operational decisions without moving metric semantics into `ragopt`.

![A production topology separates control, artifact, serving, and projection planes.](figures/11_production_topology.png){width=72%}

EOF
wc -c /mnt/data/rag_functionality_work/v2/The_Semantics_and_Dynamics_of_RAG.md
wc -w /mnt/data/rag_functionality_work/v2/The_Semantics_and_Dynamics_of_RAG.md
```

<details><summary>💭 Thinking</summary>

**Expanded production RAG APIs and improved reliability**

</details>

```unknown
bash -lc cat >> /mnt/data/rag_functionality_work/v2/The_Semantics_and_Dynamics_of_RAG.md <<'EOF'

# Part VI. Shared architecture and migration

# 31. Proposed package architecture

## 31.1 Design rule

The shared package boundary follows semantic ownership. `ragkit` owns general RAG-domain meaning and runtime laws. Product repositories own source-specific normalization, authorization policy, structured-domain meaning, agent prompts, and presentation schemas. `ragopt` owns experiment custody and campaign mechanics. Transport frameworks and deployment schedulers remain separate.

The design does not require all packages to be extracted immediately. Types can begin under internal paths and move only after two applied systems use matching semantics. The release, source-change, query-interpreter, and frontend-law types are exceptions where one shared definition prevents high-risk divergence.

## 31.2 `ragkit/corpus`

Responsibilities:

- source keys, revisions, tombstones, cursors, barriers, and watermarks;
- connector capability descriptions;
- normalized document envelopes and admission records;
- snapshot and change-stream validation;
- source-lineage and temporal consistency laws;
- canonical snapshot manifests.

It does not know SQL schemas, product fields, Git admission rules, or web crawler details. Those are adapters.

Proposed surface:

```go
package corpus

type Connector interface {
    ID() ConnectorID
    Capabilities() Capabilities
}

type Snapshotter interface {
    Connector
    Snapshot(context.Context, SnapshotRequest, ChangeSink) (Barrier, error)
}

type ChangeSource interface {
    Connector
    Changes(context.Context, Cursor, ChangeSink) error
}

type Normalizer interface {
    Spec() NormalizeSpec
    Normalize(context.Context, DocumentRevision) ([]NormalizedDocument, Admission, error)
}
```

A `ChangeSink` is backpressured and idempotent by connector/cursor/revision identity. It does not require loading the whole corpus into memory.

## 31.3 `ragkit/derive`

Responsibilities:

- versioned stage specifications;
- semantic derivation keys;
- impact graph and invalidation closure;
- content-addressed cache contracts;
- deterministic and retained-stochastic derivations;
- lineage graph from documents to index entries;
- incremental equivalence helpers.

Existing chunking, representations, embedding, and flow packages remain domain implementations. `derive` connects them without becoming another workflow framework.

```go
type NodeSpec interface {
    Kind() NodeKind
    SemanticID() digest.Digest
    Dependencies() []NodeKind
    Incrementality() Incrementality
}

type Planner interface {
    Plan(context.Context, BaseLineage, corpus.Snapshot, Graph) (ImpactPlan, error)
}
```

## 31.4 `ragkit/index`

Responsibilities:

- backend capabilities and semantic contracts;
- full and delta build interfaces;
- immutable snapshot searchers;
- base/delta/tombstone views;
- compaction;
- exact-oracle and incremental-equivalence certification;
- common filters and result-completeness declarations.

Existing Bleve and SQLite implementations can adapt behind this package. `indexbundle` can become an implementation of one full immutable release artifact rather than the top-level production unit.

## 31.5 `ragkit/build`

Responsibilities:

- build intent and plan identity;
- durable event vocabulary and reducer;
- checkpoint manifest;
- local coordinator implementation;
- stage scheduling over `flow`;
- verification and release-registration handoff;
- status and progress projections.

This package is justified once both GEC and TTC use the same refresh lifecycle. Until then it can live in `ragkit/experimental/build` or one product with shared interfaces fixed in `corpus`, `derive`, and `release`.

It must remain a fixed RAG coordinator. Generic distributed workflow concerns belong to an external scheduler.

## 31.6 `ragkit/release`

Responsibilities:

- behavior-complete release manifest and canonical ID;
- lifecycle state and activation events;
- registry, compare-and-swap activation, cohort mapping;
- resolver and reference-counted/epoch leases;
- release verification hooks and retirement;
- rollback and emergency revocation.

This package is the synchronization boundary between maintenance and querying. It should be adopted early even while builds remain full and activation still requires process-local reload.

## 31.7 `ragkit/query`

Responsibilities:

- retrieval operation signature and typed plans;
- rewrite, channel, collapse, fusion, filtering, rerank, hydrate, and admit specifications;
- direct-search interpreter;
- common outcomes, warnings, and trace events;
- authorization-certificate and provider-disclosure contracts;
- deterministic reference interpreter and production concurrent interpreter.

Existing `rag/retrieval` kernels move under or are used by this package. Existing `rag/answering` becomes one interpreter rather than the only complete query abstraction.

## 31.8 `ragkit/answer` and `ragkit/agent`

`ragkit/answer` owns context construction, generation request formation, grounded contract validation, abstention, and answer outcomes. Product prompts and structured response schemas are inputs.

`ragkit/agent` should remain small. It defines a bounded RAG tool-transition host, idempotent call IDs, evidence-session integration, and terminal validation hooks. It does not replace Geppetto/Pinocchio or product chat frameworks. It adapts shared search semantics into them.

## 31.9 `ragkit/evidence`

Responsibilities:

- typed source, structured, generated, and connected evidence references;
- evidence-session scopes and release coherence;
- stable citation labels;
- admission certificates;
- generic source projections;
- laws for boundedness and stable reuse.

Product-specific ledgers can wrap it. The package must not assume every evidence kind can be cited as source authority.

## 31.10 `ragkit/stream`

Responsibilities:

- event envelope, entity version, ordinal, operation, and patch modes;
- snapshot type;
- pure reducer interfaces and conformance tests;
- deduplication and stale-event laws;
- generic RAG lifecycle events.

Product timeline schemas remain outside. GEC and Garden map their entities to this envelope.

## 31.11 `ragkit/eval`

Responsibilities:

- retrieval and evidence metric schemas;
- answer/grounding result envelopes;
- temporal and operational metric coordinates;
- per-case artifacts and stratification;
- paired-difference helpers;
- exact-oracle and release comparison contracts.

It does not implement a universal LLM judge or product utility. Those are arms that emit native artifacts and shared metric projections.

## 31.12 `ragopt/ragspace`

A thin adapter package can define RAG parameter references, intervention classes, dependency closures, and fidelity requirements. It imports `ragkit` types. Core `ragopt` remains domain-neutral.

```go
type Arm struct {
    Builder   ragbuild.Client
    Resolver  release.Resolver
    Executor  rageval.Executor
    Projector MetricProjector
}
```

The arm builds or resolves candidate releases and evaluates them at product-native levels. `ragopt` schedules paired cells and gates their projections.

## 31.13 Dependency rules

- `ragkit/corpus`, `derive`, `index`, `release`, `query`, `evidence`, `stream`, and `eval` do not import product code.
- `ragkit/query` depends on `release`, `index`, and `evidence`, not on HTTP or chat frameworks.
- `ragkit/build` depends on corpus/derive/index/release and uses flow as inner execution.
- `ragopt` core does not import `ragkit`.
- `ragopt/ragspace` may import both and is optional.
- GEC, RAG-TTC, and Garden depend on published `ragkit`, never copied source.
- Product presentation depends on shared evidence/stream types but retains domain schemas.

# 32. API blueprint and executable laws

## 32.1 Release specification

```go
type Spec struct {
    SchemaVersion string
    Product       string
    Corpus        corpus.SnapshotRef
    Build         build.SpecRef
    Indexes       []index.ViewSpec
    Query         query.Spec
    Answer        answer.Spec
    Agent         *agent.Spec
    Evidence      evidence.Policy
    Structured    []StructuredAsset
    Presentation  []artifact.Ref
    Validators    []artifact.Ref
    DataPolicy    policy.Ref
}

type Manifest struct {
    ID        ID
    Spec      Spec
    Artifacts []artifact.VerifiedRef
    BuiltAt   time.Time
    VerifiedAt time.Time
}
```

Canonical validation rejects paths without material digests where behavior depends on content, mutable provider aliases without retained identity classification, duplicate artifact roles, and missing dependency links.

## 32.2 Query plan

```go
type Spec struct {
    PlanID          PlanID
    Rewrite         RewriteSpec
    Channels        []ChannelSpec
    Collapse        CollapseSpec
    Authorization   AuthorizationSpec
    Fusion          FusionSpec
    Rerank          *RerankSpec
    Admission       AdmissionSpec
    Deadline        DeadlineSpec
    Fallbacks       []FallbackRule
    TracePolicy     trace.Policy
}
```

A plan validator checks:

- unique channel names and deterministic order;
- finite weights and positive depths;
- authorization domination of remote text operations;
- capability match with release indexes;
- bounded remote candidate and agent loops;
- fallback plan existence and policy compatibility;
- evidence admission after release-bound hydration;
- complete semantic identity.

## 32.3 Search interface

```go
type Interpreter interface {
    Execute(context.Context, *release.Lease, SubjectContext, Request) Outcome
}

type Outcome struct {
    Status    Status
    Release   release.ID
    Plan      PlanID
    Rankings  []ChannelRanking
    Fused     []Candidate
    Evidence  []evidence.Admitted
    Warnings  []Warning
    Trace     trace.Ref
}
```

The deterministic reference interpreter executes channels in canonical sequence with no deadlines and retained provider outputs. The production interpreter may execute concurrently but must refine protected semantics.

## 32.4 Build events

```go
type Event interface{ isBuildEvent() }

type Started struct{ Intent IntentID; Fence uint64 }
type BarrierCaptured struct{ Barrier corpus.BarrierVector }
type PlanCommitted struct{ Plan artifact.Ref }
type ItemCommitted struct{ Stage StageID; Key derive.Key; Artifact artifact.Ref }
type ItemQuarantined struct{ Stage StageID; Key derive.Key; Reason ErrorCode }
type StageSealed struct{ Stage StageID; Summary StageSummary }
type VerificationCompleted struct{ Report artifact.Ref; Passed bool }
type ReleaseRegistered struct{ Release release.ID }
type BuildFailed struct{ Stage StageID; Error ErrorCode }
type BuildCancelled struct{ Reason string }
```

A pure reducer rejects impossible transitions. The event store appends with expected position and fence token. The reducer is a small model-checking target.

## 32.5 Activation API

```go
type Activator interface {
    CompareAndSwap(context.Context, ActivationRequest) (Activation, error)
}

type ActivationRequest struct {
    Scope         string
    Expected      ID
    Desired       ID
    IdempotencyKey string
    Actor         string
    Reason        string
    GateReport    artifact.Ref
    Cohort        *CohortPolicy
}
```

The activator verifies desired release state, gate report policy, and expected head. It emits one immutable activation event. It does not rewrite a config file and hope all replicas reload consistently.

## 32.6 Stream reducer

```go
type Event struct {
    ID            string
    StreamID      string
    StreamOrdinal uint64
    EntityID      string
    EntityVersion uint64
    Operation     Operation
    PatchMode     PatchMode
    Payload       json.RawMessage
    ReleaseID     release.ID
    CausationID   string
}

type Reducer[S any] interface {
    Apply(S, Event) (S, error)
}
```

The conformance suite generates snapshots, suffixes, duplicates, stale events, and legal reorderings. Product reducers must pass before adopting the envelope.

## 32.7 Law suite

The shared law suite contains:

**Release laws.** Canonical manifest round trip; ID sensitivity to material behavior fields; insensitivity to explicitly operational deployment fields; artifact role uniqueness.

**Lease laws.** No new lease after draining; old lease remains valid; close idempotence; retirement only after zero leases; activation does not mutate existing lease.

**Query laws.** deterministic fusion and tie order; authorization before remote disclosure; all evidence from lease release; fallback warning preservation; context budget and stable prefix where applicable.

**Build laws.** event reducer transition validity; duplicate item commit idempotence; resume equivalence; incremental/full equivalence; no publication before verification; activation absent from build success.

**Evidence laws.** stable labels, boundedness, no mixed release, evidence-kind preservation, source projection lineage.

**Stream laws.** snapshot-suffix equivalence, duplicate idempotence, stale rejection, deterministic display, terminal immutability.

**Optimization laws.** dependency closure complete; candidate exactly one declared intervention; paired coordinates exact; missing outcomes retained; gates ordered and fail closed.

# 33. GEC migration

## 33.1 Current strengths to retain

GEC already has product-correct boundaries: server-owned scopes and roles, separate knowledge and structured tools, strict synonym loading, deterministic weighted RRF, explicit forced routes for evaluation, run-scoped evidence labels, persistent chat/timeline infrastructure, and customer/developer distinctions. These should not be generalized away.

Its immediate production issues are release identity, authorization order, startup-only activation, and fragmented optimization custody.

## 33.2 Phase G0: behavioral fixture

Before changing the query path, capture fixture cases containing:

- lexical, hybrid, no-rerank, and synonym-expanded rankings;
- reranker success and failure fallback;
- access scope and source role filtering;
- evidence labels and tool serialization;
- empty/invalid queries;
- representative admin conversations and frontend snapshots.

Use retained local search/reranker outputs where remote providers are unavailable. These fixtures define current intentional behavior and expose intentional changes such as secure prefiltering.

## 33.3 Phase G1: behavior-complete release

Wrap the existing startup resources in a `release.Manifest` without changing execution. Include:

- bundle and corpus identity;
- synonym file content digest and expansion spec;
- reranker provider/model, pool, document-text composer, blend, timeout, and fallback;
- query route/defaults and search-depth behavior;
- evidence policy and tool schema/description;
- answer prompt/contract and inference profile where used;
- structured SQL/tool policy references;
- frontend source projection schema.

Every query trace and tool output adds release ID. This immediately makes current behavior auditable.

## 33.4 Phase G2: authorization before reranking

Change retrieval to return metadata-bearing candidate IDs, prefilter them locally by access scope and source role, and hydrate only authorized candidates for reranking. Add the remote spy regression test.

Then replace heuristic postfilter completeness with index filter pushdown or scope-partitioned search. The query outcome reports whether authorized top-$k$ completeness is guaranteed. Remove comments that rely on current two-scope corpus size as a general safety argument.

## 33.5 Phase G3: release manager

Replace the single `*knowledge.Service` with a resolver-backed runtime. A release loader opens bundle, documents, synonyms, reranker adapter, prompts, and validators. The chat runtime acquires one lease per run/turn. The evidence ledger records the lease ID.

Begin with manual activation and one process. Add compare-and-swap registry, preload, and draining. Later add replica-wide registry watch. A configuration reload that fails leaves the old release active.

## 33.6 Phase G4: corpus connector and refresh

Because `internal/knowledgebuild` is absent from the supplied source, the migration must begin with a source-contract audit when that package is available. Based on design records, product/category/schema-doc connectors become `corpus` adapters. The existing committed manifest and normalization become versioned specs. The first shared coordinator can still perform a full nightly build with content-addressed representation/embedding reuse.

Add source snapshot identity and watermarks to the release. Only after full-refresh operation is stable should GEC add delta overlays. Product and category rows are suitable for logical-key upsert/delete; embedded schema docs may use package/library version barriers.

## 33.7 Phase G5: optimization integration

Map current RRF sweep into a `ragopt` campaign whose candidate intervention is fusion spec. Retain frozen channel rankings as native artifacts and add paired confidence/holdout. Map reranker and synonym experiments to separate intervention classes.

Answer-quality judges and evaluation sets remain GEC-owned arms. They emit common answer/grounding metric projections and retain failures. Promotion creates a new release spec and activation report rather than environment-variable instructions.

## 33.8 Phase G6: frontend event hardening

Add event IDs and entity versions to SessionStream/UI events. Update `wsManager` to discard events at or below snapshot ordinal and deduplicate IDs. Update `timelineSlice` to reject stale versions before merging. Append patches carry offsets or are converted to full replace values at reconnection boundaries.

Property tests generate snapshot/event schedules. Existing UI mapping and display sorting remain.

# 34. RAG-TTC migration

## 34.1 Current strengths to retain

RAG-TTC contains the richest experimental surface: multiple representations, caches and budgets, committed-Git snapshots, workspace artifacts, exact and ANN search, connected retrieval, search routes, agent tools, evidence ledgers, answer/tool evaluation, persistent chat server, and diagnostics. It should be the first proving ground for joint index-query optimization.

It also contains copied `ragkit` source. The copied substrate must be removed so runtime fixes and semantics have one owner.

## 34.2 Phase T0: hard cutover to `ragkit`

Use package-level differential fixtures to compare current copied code and `ragkit` for chunking, representations, bundle opening, retrieval, fusion, context, and evaluation. Resolve intentional differences. Change imports to `github.com/go-go-golems/ragkit` and delete copied packages rather than maintaining adapters indefinitely.

Product-specific packages such as `ttcrag`, product catalog, connected retrieval, knowledge database, tool answer, HNSW candidate, application chat, and experiment commands remain in RAG-TTC.

## 34.3 Phase T1: source connector

Adapt `gochunk.LoadCommitted` to `corpus.Snapshotter`. Git commit/tree becomes snapshot token. Admission records map directly. Snapshot digest and per-file document revisions enter release lineage.

A future Git change source can diff commits and emit upsert/delete changes. The clean committed-tree snapshot remains the oracle. Working-directory indexing, if needed for developer tools, is a separate weaker connector with explicit non-repeatable semantics.

## 34.4 Phase T2: build coordinator

Adapt the current indexes build and workspace index commands to one build intent and stage DAG. Existing representation and embedding caches become derivation caches. CLI progress subscribes to build events. Dry run prints impact plan and budgets.

The first implementation still produces full `indexbundle` artifacts. Later it adds delta views. Experiment builds and production refresh use the same build semantics but different source/parameter locks and registries.

## 34.5 Phase T3: query interpreters

Extract shared retrieval plan construction from workspace search, ask, and `ttcrag.SearchTool`. Direct CLI search uses direct interpreter. Ask uses answer interpreter. The model tool uses agent interpreter with the same channel/fusion kernels.

Route observation, connected augmentation, product filters, and structured routes remain RAG-TTC-owned extensions. Every tool call runs under the turn lease and evidence session.

## 34.6 Phase T4: ANN backend certification

Move HNSW candidate behind `ragkit/index` capability interface only after it passes:

- static exact-oracle recall/latency gate;
- incremental insertion/deletion sequence tests;
- base-plus-delta query view tests;
- filter behavior;
- build/reopen/reproducibility tests;
- memory, build time, and concurrency benchmarks;
- compaction and source-refresh scenarios.

The existing bakeoff becomes one fidelity in a broader backend campaign.

## 34.7 Phase T5: production serving

The simple serve command and canonical chat server resolve releases through shared manager rather than opening one bundle forever. Per-conversation runtime construction receives a turn or conversation lease. Submission idempotency, timeline persistence, and auth remain application-owned.

Expose release and evidence IDs in outcomes and SessionStream events. Add shadow arm support that executes a candidate release without emitting customer events.

## 34.8 Phase T6: optimization campaigns

Define typed RAG spaces for representation kind, chunking, embedding, ANN, route, channel depth, fusion, reranking, context, and agent/tool policy. Use dependency-aware shared artifacts. Current manual arm contracts become candidate specs. Tool-answer and session evaluations remain native arms.

RAG-TTC can then serve as the integration test for `ragopt/ragspace` without making `ragopt` own RAG behavior.

# 35. Garden migration and presentation semantics

## 35.1 Current strengths to retain

Garden's distinctive value is product interpretation: intent-specific routes, structured product facts, connected fallback, exact fact augmentation, evidence-admitted widgets, field alignment, conflict suppression, customer/developer projections, and real multi-turn calibration. These are not generic retrieval utilities.

The migration should replace infrastructure beneath them while preserving the product semantic layer.

## 35.2 Phase A: replace copied substrate transitively

Garden currently depends on RAG-TTC, which contains copied RAG core. After RAG-TTC cuts over, Garden receives shared `ragkit` behavior without direct large changes. Add fixture tests around current route outputs, citations, structured-first responses, and grounded widgets.

## 35.3 Phase B: Garden release manifest

Create one release spec containing:

- TTC index view and source corpus;
- embedding/query provider identities;
- fact database content digest and schema/query adapters;
- tool configuration content;
- intent route definitions and connected-retrieval policy;
- evidence-session limits;
- prompt/profile/tool schema assets;
- grounded widget projection schemas and conflict policy.

Paths are deployment locators only. The manifest uses content identities. The per-conversation session search is created from a release lease.

## 35.4 Phase C: evidence epochs

Garden currently creates fresh search state per conversation. Choose one of two explicit policies:

- pin the entire conversation to one release with a maximum conversation lease duration; or
- pin each turn, create evidence epoch per turn, and allow widgets only from the current epoch unless historical evidence is explicitly imported with original release lineage.

Per-turn pinning is preferable for freshness. Follow-up interactions can reference prior visible content, but new widget generation should not silently treat old evidence as current.

## 35.5 Phase D: typed projection integration

Keep `grounded_widgets.go` and `evidenceview` product-owned. Replace internal citation identity plumbing with `ragkit/evidence` references. Each widget field carries source chunk or structured fact lineage and release ID. The generic stream envelope transports the typed widget payload.

Conflicting fact suppression remains a Garden validator. It can emit structured diagnostics for calibration and optimization.

## 35.6 Phase E: calibration as a high-fidelity arm

Garden calibration becomes a `ragopt` arm at conversation level. Each case has stable idempotency keys and source/release constraints. The runner records every snapshot poll and terminal-settle decision as native artifacts. Metrics include:

- terminal completion and latency;
- answer and choice assertions;
- source/evidence kinds;
- widget grounding and field lineage;
- tool calls and route decisions;
- word/token budget;
- release consistency across turn;
- customer and developer projection correctness.

Run incumbent and candidate on paired conversation cases and repeat stochastic profiles. Preserve current real-server execution rather than replacing it with a unit-level simulator.

## 35.7 Phase F: frontend law conformance

Garden's shared chat provider and widget frontend should adopt event IDs, entity versions, release lineage, and snapshot-suffix conformance tests. Zod schemas continue validating product payloads. Customer mode must never render developer-only lineage even when it is present in the authoritative event artifact.

# 36. Migration program, verification, and conclusion

## 36.1 Dependency-ordered program

The migration is ordered to reduce semantic risk:

1. freeze behavioral fixtures and current runtime identities;
2. introduce behavior-complete release manifests without changing query output;
3. fix authorization before remote disclosure;
4. cut RAG-TTC copied core over to `ragkit`;
5. separate direct, answer, and agent interpreters;
6. add release manager, leases, compare-and-swap activation, and rollback;
7. introduce source revisions, barriers, and a full-snapshot reconciler;
8. add durable build events/checkpoints over existing full builds;
9. add base-plus-delta views, tombstones, and compaction with full-build oracle;
10. add typed RAG optimization spaces and multi-fidelity campaigns;
11. add shadow/canary resolution and operational gates;
12. harden frontend snapshot/event semantics.

![Dependency-ordered migration from current fixed bundles to dynamic production RAG.](figures/12_migration_roadmap.png){width=55%}

## 36.2 Why release identity comes first

Without complete release identity, every later comparison is ambiguous. Hot activation cannot say what it activated. A query trace cannot prove which synonyms, fact DB, prompt, or reranker it used. An optimization candidate cannot be reproduced. Therefore the first implementation change is a manifest and trace field, not incremental indexing.

This can be introduced around current startup-bound services and creates immediate value with low behavioral risk.

## 36.3 Why security precedes relevance work

GEC's remote rerank ordering is a concrete trust-boundary defect. Fixing it may change rankings because authorized prefiltering changes the candidate pool. That change should be accepted as a security correction and then rebaselined, not delayed to preserve benchmark continuity.

The new authorization certificate and plan law prevent recurrence across products.

## 36.4 Why full refresh precedes deltas

A durable full-refresh machine establishes source barriers, build intent, checkpoints, verification, release registration, activation, and observability. Incremental maintenance reuses all of these and changes the impact plan/index view. Implementing deltas first would mix source, build, and activation bugs.

Full rebuild remains the oracle, so this work is never discarded.

## 36.5 Acceptance criteria by milestone

**Release milestone.** Every turn records one complete release ID; changing any material query asset changes release ID; fixtures remain stable.

**Security milestone.** No unauthorized marker text reaches remote reranker/generator in adversarial tests; authorized top-$k$ semantics are declared and measured.

**Activation milestone.** New queries switch atomically; in-flight old queries complete; rollback is one CAS; no mixed-release evidence.

**Refresh milestone.** Source barrier and watermark are visible; duplicate connector events are idempotent; failed build resumes; publication never activates implicitly.

**Incremental milestone.** Random change sequences produce views equivalent to clean full builds; deletes disappear; compaction preserves query behavior within backend tolerance.

**Optimization milestone.** Candidates declare intervention/dependency/fidelity; paired runs retain failures; holdout and uncertainty gates are enforced; promotion references immutable release.

**Frontend milestone.** Duplicate and stale events cannot corrupt state; snapshot plus suffix equals full replay; terminal answer/source/widget provenance retains release ID.

## 36.6 Model checking targets

Small state machines merit exhaustive exploration:

- release activation with two concurrent activators and leases;
- build event reducer with retry, cancellation, lease loss, and resume;
- query cancellation across channel/generation/event stages;
- evidence session under repeated calls and release changes;
- frontend snapshot, duplicate, stale, and reordered events.

TLA+ or a small explicit-state model can find interleavings that ordinary tests miss. The production Go reducers remain the executable authority; model traces become test fixtures.

## 36.7 Formal-proof targets

Machine-checked proof is most valuable for stable pure kernels:

- total ordering and finite-score ranking;
- weighted RRF determinism;
- authorization domination in typed plans;
- incremental differential laws for finite maps and document-local stages;
- event-reducer invariants;
- snapshot-suffix reducer equivalence;
- release-ID canonical encoding.

Provider behavior and complete product correctness remain empirical. The architecture concentrates proof effort where it can establish lasting guarantees.

## 36.8 Operational adoption strategy

Run old and new paths in differential mode. For release manager, resolve the same current bundle through a lease and compare outputs. For query interpreters, execute both against retained searchers. For frontend changes, replay captured snapshots/events through both reducers. For incremental builds, compare every candidate delta view to full build before activation.

Compatibility adapters have deletion dates. The objective is one semantic path, not permanent double execution.

## 36.9 Final conclusion

The field of RAG begins before chunking and ends after the frontend has reconstructed a grounded user outcome. It includes source revision semantics, temporal capture, derived views, physical indexes, authorization, retrieval algebra, stochastic providers, agent trajectories, release activation, event streams, and optimization under uncertainty.

The supplied systems already contain most of the necessary local mechanisms. `ragkit` has deterministic retrieval and verified immutable artifacts. RAG-TTC has source snapshots, experimental builds, ANN comparison, agentic search, and persistent chat. GEC has administrative policy and practical reranking/evaluation. Garden has evidence-to-product presentation and multi-turn calibration. `ragopt` has disciplined experiment custody. The architectural task is to connect these mechanisms under a domain model that explains time and state rather than hiding them.

The proposed semantics makes three distinctions decisive. Denotational outcomes explain what a release means to a user. Intensional traces retain facts that outcomes erase. Operational transition systems explain how partial, concurrent, and failureful execution produces those traces. Together they give optimization a correct object: not a score over a static pipeline, but a constrained comparison of evolving RAG releases and their runtime behavior.

The resulting architecture remains pragmatic. It does not require theorem proving before shipping, an all-purpose workflow engine, or a universal product schema. It requires explicit source barriers, immutable behavior-complete releases, lease-pinned query interpreters, typed evidence and events, durable build transitions, and dependency-aware experiments. These are implementable from the current code and strong enough to support incremental indexing, hot activation, safe frontend serving, and joint retrieval optimization.

EOF
wc -c /mnt/data/rag_functionality_work/v2/The_Semantics_and_Dynamics_of_RAG.md
wc -w /mnt/data/rag_functionality_work/v2/The_Semantics_and_Dynamics_of_RAG.md
```

I’ll model corpus evolution as revision streams with tombstones, barriers, cursors, and watermarks, using full rebuild equivalence as the incremental-index oracle. Optimization follows causal dependency closures, not flat parameter sweeps.

<details><summary>💭 Thinking</summary>

**Completing the model**

I’m consolidating the deliverable around evolving corpus state, query execution, optimization, release semantics, and frontend convergence, while preserving empirical findings and clearly marking unavailable implementation evidence.

</details>

```unknown
bash -lc ls -lah /mnt/data/rag_functionality_work/v2 && echo '---' && wc -l -w -c /mnt/data/rag_functionality_work/v2/The_Semantics_and_Dynamics_of_RAG.md && echo '---tail---' && tail -n 80 /mnt/data/rag_functionality_work/v2/The_Semantics_and_Dynamics_of_RAG.md
```

<details><summary>💭 Thinking</summary>

**Appended architecture, semantics, and RAG documentation sections**

</details>

```unknown
bash -lc cat >> /mnt/data/rag_functionality_work/v2/The_Semantics_and_Dynamics_of_RAG.md <<'EOF'

# Appendix E. Optimization campaign catalog {-}

This appendix turns the optimization semantics of Part IV into executable study designs. It is deliberately more prescriptive than the main text. Each campaign identifies the intervention, the affected dependency closure, the required evaluation unit, the validity threats, and the promotion gates. The purpose is not to prescribe permanent threshold values. It is to prevent incomparable experiments from being presented as one undifferentiated tuning loop.

## E.1 A campaign is a typed intervention, not a parameter sweep

Let a production release specification be a value $R$ in a typed configuration space. A candidate is not merely a partial map from string names to numbers. It is an intervention

$$
I : R \rightsquigarrow R'
$$

with five declarations:

1. **target nodes** - the components directly changed;
2. **dependency closure** - the artifacts and evaluators invalidated by the change;
3. **semantic class** - operational, approximation, relevance, knowledge, policy, interaction, or presentation changing;
4. **claimed invariants** - properties asserted to remain equal or within a tolerance;
5. **required evidence** - the lowest fidelity at which the claim can be decided.

A campaign is then a finite or adaptive family of interventions evaluated under a common protocol:

$$
\mathcal{C} = (R_0, \mathcal{I}, W, M, G, A),
$$

where $R_0$ is the baseline release, $\mathcal{I}$ is the candidate generator, $W$ is the workload and sampling design, $M$ is the measurement plan, $G$ is an ordered gate program, and $A$ is the allocation policy. The allocation policy may be a grid, random search, Bayesian optimization, successive halving, racing, or a manually curated set. The semantics do not depend on the search algorithm. They depend on whether the candidates, cells, and gates retain their identities and causal scopes.

Every candidate should have a machine-readable declaration resembling:

```go
type Intervention struct {
    ID               InterventionID
    Baseline         release.ID
    Patch            release.SpecPatch
    Targets          []derive.NodeKind
    Closure          []derive.NodeKind
    SemanticClass    []SemanticClass
    ClaimedInvariants []InvariantClaim
    Workload         eval.WorkloadID
    Fidelity         eval.Fidelity
    Repeats          eval.RepeatPolicy
}
```

The closure must be computed from the release dependency graph, not entered by hand. A change to the embedding model invalidates vector representations, vector indexes, release manifests, retrieval evaluation, and all answer/session evaluations that depend on retrieval. It need not invalidate lexical-index bytes when lexical analysis is unchanged. A change to `efSearch` invalidates no corpus derivation, but it invalidates vector-search observations and every downstream outcome that may depend on the candidate set. A change to a frontend widget projection invalidates session and presentation evaluation while leaving retrieval metrics unchanged.

## E.2 Parameter families and minimum evaluation levels

The following catalog is a starting schema for `ragopt/ragspace`. “Minimum fidelity” means the first level at which a candidate can possibly be accepted. Lower levels can still reject it cheaply.

| Layer | Parameter family | Typical semantic class | Minimum fidelity |
|---|---|---|---|
| Source | connector and capture protocol | knowledge, reliability | refresh simulation |
| Source | inclusion, exclusion, access policy | policy, security, knowledge | policy suite plus retrieval |
| Normalization | canonical text and metadata | knowledge, relevance | retrieval plus lineage |
| Chunking | algorithm, size, overlap, boundaries | relevance, knowledge projection | retrieval and answer |
| Representation | raw, context, summary, questions, entities | relevance, knowledge projection | retrieval and answer |
| Representation generation | model, prompt, decoding, reuse | knowledge, stochastic | repeated answer/retrieval |
| Embedding | model, dimension, normalization | relevance | retrieval and answer |
| Lexical index | analyzer, fields, boosts | relevance | retrieval |
| Vector index | exact or ANN backend | approximation, operational | oracle plus load |
| Vector construction | graph, quantization, partitions | approximation, operational | oracle plus scale |
| Rewrite | synonyms, variants, HyDE, route | relevance, stochastic | retrieval and answer |
| Candidate generation | channel depth and overfetch | relevance, operational | retrieval plus policy |
| Filtering | subject, source, role, kind | policy, security, relevance | security plus retrieval |
| Fusion | rank constant, weights, tie rules | relevance | retrieval |
| Reranking | model, pool, blend, fallback | relevance, disclosure, reliability | retrieval, answer, failure |
| Context | token/rune budget, diversity, ordering | answer | answer |
| Answer | model, prompt, contract, repair | answer, stochastic | repeated answer |
| Agent | tools, routing, iteration and retry | interaction | session |
| Serving | deadlines, concurrency, cache | operational, sometimes outcome | load and failure |
| Release | rollout, pinning, epoch scope | operational, experimental | concurrency and canary |
| Presentation | event and widget policy | user outcome | frontend/session |

A useful rule is that a candidate must be evaluated at the highest fidelity required by any changed node in its dependency closure. This prevents a retriever-only metric from promoting a prompt change, and prevents an exact-oracle ANN test from promoting a new chunking scheme whose relevance semantics changed.

## E.3 Invalidation examples

The dependency graph should produce explicit invalidation records. Examples follow.

### E.3.1 Chunk-size intervention

Changing fixed chunks from 1,200 to 800 runes directly changes chunk derivation. The closure normally includes:

- chunk records and chunk identities;
- every representation attached to changed chunks;
- generated-representation cache keys when the source chunk is part of the prompt input;
- embeddings of changed representations;
- lexical and vector index partitions for changed representations;
- release manifest and aggregate digests;
- retrieval judgments whose evidence unit is a chunk ID;
- answer and session fixtures whose accepted citations name old chunks.

The source snapshot and normalized document IDs remain stable. A correct impact planner records this distinction so that source capture and document normalization can be reused.

### E.3.2 Fusion-weight intervention

Changing a vector-channel weight affects only query policy and downstream observations. No index needs rebuilding. The closure includes ranked retrieval, evidence admission, answer generation, agent behavior, and frontend outputs. Because the candidate can change which evidence is disclosed to a generator, cached generated answers from the baseline are not valid candidate observations.

### E.3.3 Reranker-provider intervention

Changing a reranker model or endpoint changes ranking, latency, cost, disclosure, failure behavior, and possibly jurisdiction. The intervention therefore cannot be classified as relevance-only. It requires provider identity in release material, a disclosure-policy check, repeated failure testing, and a fail-open/fail-closed declaration. The candidate is invalid if its remote stage receives text that the subject is not authorized to disclose.

### E.3.4 Deadline intervention

Increasing concurrency or reducing a stage timeout may be operational under an idealized no-timeout semantics, but it is outcome-changing in a real service whenever the timeout can trigger partial retrieval, reranker fallback, answer truncation, or cancellation. The intervention may claim answer-distribution equivalence only after a workload test shows the altered deadline is not reached in the declared operating envelope. Otherwise, timeout behavior is part of the denotation and requires answer/session evaluation.

## E.4 Campaign 1: GEC fusion, synonyms, and reranking

### E.4.1 Question

The practical question is not “what is the best RRF constant?” It is:

> For each authorized administrative query class, which combination of lexical rewriting, channel allocation, fusion, and reranking improves evidence and answer quality without increasing unauthorized disclosure, tail latency, cost, or failure severity?

The current GEC sweep varies a small RRF/vector-weight space against a fixed corpus. That is an appropriate first retrieval experiment, but it omits three coupled effects: synonyms alter only lexical query behavior; reranking can compensate for or amplify first-stage changes; and post-retrieval authorization changes effective candidate depth.

### E.4.2 Candidate factors

A first complete campaign should vary a bounded, reviewable set:

- synonym-set revision and whether expansion is disjunctive or weighted;
- lexical and vector channel depths;
- preauthorization overfetch strategy;
- RRF rank constant and channel weights;
- representation kinds admitted to each channel;
- rerank pool size;
- rerank/fused blending policy;
- reranker model and local versus remote execution;
- fail-open or fail-closed behavior by query class;
- context evidence count and diversity constraints.

Authorization policy is not a tunable quality factor. It is a hard constraint and release input. The campaign may compare *implementations* of the same policy, such as pushdown filters versus local pre-rerank filtering, but must prove policy equivalence.

### E.4.3 Workload design

The workload should be stratified by:

- subject role and source scope;
- query intent: exact policy lookup, broad procedure, troubleshooting, cross-document synthesis, and unsupported question;
- lexical characteristics: exact terminology, synonym-dependent wording, acronym, misspelling, and paraphrase;
- corpus density: one authoritative source, many near-duplicates, conflicting revisions, and no relevant source;
- reranker sensitivity: cases where lexical and vector channels disagree;
- temporal status: current, superseded, recently changed, and tombstoned material.

Every test case carries an authorized evidence set, a forbidden-disclosure set, graded relevance judgments, expected source authority, and answer/abstention expectations. Forbidden evidence is necessary: a system can improve conventional recall by retrieving material the subject must not see.

### E.4.4 Measurements

Retrieve-level measurements include graded nDCG, recall at evidence budget, reciprocal rank of first authoritative chunk, duplicate-source concentration, and authorized-candidate survival. Intensional measurements include candidate counts before and after policy, remote bytes disclosed, fallback path, rewrite expansion, reranker calls, and release lineage. Answer measurements include citation support, contradiction, authority selection, completeness, abstention appropriateness, latency, and cost.

### E.4.5 Ordered gates

1. **Security gate.** Zero forbidden chunks disclosed to any remote provider and zero returned to the caller.
2. **Integrity gate.** Every evidence and answer citation belongs to the pinned release and authorized candidate set.
3. **Reliability gate.** Declared fallback behavior holds under reranker timeout, provider error, malformed score, and partial cancellation.
4. **Retrieval gate.** Noninferior authoritative recall and nDCG on every protected stratum; aggregate improvement alone is insufficient.
5. **Answer gate.** Noninferior grounding and abstention; material completeness improvement on targeted classes.
6. **Operational gate.** Tail-latency, provider-call, and cost budgets.
7. **Canary gate.** No protected-stratum regression under production traffic and no unexplained trace-distribution shift.

A winning candidate may be Pareto-superior rather than scalar-best. For example, a local reranker may have slightly lower nDCG but eliminate remote disclosure and substantially reduce latency variance. The promotion report should show that trade rather than hiding it in one score.

## E.5 Campaign 2: exact-to-ANN certification for RAG-TTC

### E.5.1 Semantic claim

An ANN backend does not preserve the exact ranked-list semantics. Its claim is relative to an exact oracle over a declared workload and operating envelope:

$$
\Pr\left[\operatorname{Recall@k}(A(q), E(q)) \ge \rho\right] \ge 1-\alpha,
$$

where $A$ is the approximate backend, $E$ the exact backend, $\rho$ the required recall threshold, and $\alpha$ the tolerated violation probability. This claim must be conditioned on corpus size, vector distribution, filter selectivity, concurrency, update state, and hardware class.

### E.5.2 Factors

- backend implementation and version;
- distance metric and vector normalization;
- graph construction parameters such as $M$ and `efConstruction`;
- query parameter such as `efSearch`;
- quantization or compression mode;
- shard/partition count;
- filter pushdown strategy;
- base-plus-delta overlay sizes;
- deleted-vector fraction and compaction state;
- concurrency and memory residency.

### E.5.3 Workloads

Use at least four workload families:

1. **Natural queries** sampled from evaluated TTC tasks and production-like traces after privacy processing.
2. **Adversarial nearest-neighbor probes** around dense clusters, duplicate representations, ties, and near-boundary vectors.
3. **Filter-selective queries** for narrow source, representation, product, or policy filters.
4. **Dynamic-state queries** after controlled upserts, deletes, tombstones, and compaction.

Measure oracle recall at multiple $k$ values, score/rank distortion, deterministic tie behavior, p50/p95/p99 latency, throughput, memory, build duration, update cost, compaction cost, and failure recovery. Repeat the build under identical inputs and compare the declared reproducibility class. Bit-identical graph bytes may be unnecessary, but ranked results under fixed seeds and environment should satisfy a stated tolerance.

### E.5.4 Gates

- exact metric and normalization compatibility;
- no deleted or unauthorized item returned;
- recall lower confidence bound above the required threshold for every critical stratum;
- bounded tail latency at target concurrency;
- bounded memory and build time;
- successful checkpoint, reopen, and crash recovery;
- full-build and base-plus-delta query equivalence within the declared ANN tolerance;
- no degradation of downstream answer grounding beyond its own noninferiority margin.

The last gate is essential. A one-point recall loss can be irrelevant when lexical fusion recovers the evidence, or catastrophic when the lost neighbor is the only authoritative source. ANN promotion therefore requires both oracle-relative and task-relative evidence.

## E.6 Campaign 3: chunking and representation design

### E.6.1 Why this is a joint experiment

Chunking and representation generation determine the searchable knowledge projection. They cannot be optimized independently of channel depth, context admission, and answer policy. Smaller chunks may improve localization but fragment definitions. Larger chunks may preserve context but waste evidence budget. Generated questions may raise recall for paraphrases while adding cost, noise, and stale derived claims. Contextual representations may improve retrieval while never being suitable as direct evidence.

### E.6.2 Candidate families

A disciplined campaign should use a small factorial structure rather than an unconstrained Cartesian product:

- baseline Markdown-heading chunks;
- smaller heading-aware chunks with overlap;
- hierarchical parent/child chunks;
- raw only;
- raw plus breadcrumb/context representation;
- raw plus generated questions;
- raw plus context and questions;
- retrieval at chunk, representation, or parent-child level;
- evidence admission at source chunk or parent section level.

Each generated representation must retain its producing prompt, model, decoding parameters, source chunk, and generation transcript or retained deterministic output. It is searchable derived data, not authority. A final answer cites the source evidence from which the representation was derived.

### E.6.3 Evaluation units

Use three linked labels:

- **source-span relevance**, identifying authoritative byte or structural spans;
- **retrieval-unit relevance**, identifying which chunks/representations make those spans discoverable;
- **answer support**, identifying which admitted evidence actually supports claims.

This avoids freezing the benchmark to baseline chunk IDs. When chunk boundaries change, source-span labels can be projected onto the candidate’s chunk graph. The projection rule must be versioned, for example by overlap threshold, structural containment, or explicit assessor mapping.

### E.6.4 Cost model

Report storage, representation-generation calls, embedding calls, index build duration, index size, query channel operations, reranking tokens, context tokens, and refresh amplification. Refresh amplification is particularly important:

$$
A_{refresh} = \frac{\text{derived items recomputed}}{\text{source items materially changed}}.
$$

A chunking scheme that improves frozen-corpus nDCG but turns a one-line edit into thousands of regenerated representations may be unacceptable for a frequently changing corpus.

### E.6.5 Promotion rule

A candidate must improve a declared relevance or answer stratum, remain noninferior on protected strata, satisfy freshness and cost envelopes, and pass incremental/full-build equivalence. The campaign should not promote an opaque “best chunk size.” It should produce a release-specific design choice with a workload and change-rate envelope.

## E.7 Campaign 4: refresh, overlay, and compaction policy

Retrieval quality experiments usually freeze the corpus. A production maintenance campaign varies the *trajectory* of the corpus and system load.

### E.7.1 Input process

Generate or replay a timestamped revision stream containing:

- new documents;
- small edits within existing documents;
- large replacements;
- metadata-only policy changes;
- deletions and later recreations;
- source reordering and duplicate delivery;
- delayed and out-of-order changes;
- barriers and connector restarts;
- bursts followed by idle periods.

The simulation should preserve source-specific revision identities and event-time versus observation-time distinctions. A delete must name the object and revision relationship it supersedes; “file absent in one poll” is not always a deletion.

### E.7.2 Policy factors

- polling or subscription cadence;
- debounce/coalescing window;
- maximum change batch;
- impact-plan granularity;
- delta-overlay activation threshold;
- maximum overlay depth or tombstone ratio;
- compaction schedule;
- full-rebuild cadence;
- failure retry and quarantine policy;
- staleness budget by source class;
- activation gate strictness.

### E.7.3 Correctness oracle

At every barrier $b$, compare the activated maintained view with a clean rebuild from the source snapshot at $b$. Exact backends should be observationally equal for normalized documents, chunks, representations, filters, and ranked output under a deterministic query set. Approximate backends should compare through an exact logical oracle plus their declared approximation relation.

The simulation must also check absence. Deleted material must not be retrievable, disclosed, cited, or projected. Tombstone correctness is a first-class property, not the complement of recall.

### E.7.4 Operational measurements

- source-to-captured, captured-to-built, and built-to-active lag;
- percent of time inside freshness SLO;
- activation frequency and skipped/coalesced revisions;
- work amplification and cache hit rate;
- build queue depth and age;
- overlay size, tombstone ratio, and compaction pause;
- query latency under concurrent maintenance;
- recovery point after injected crashes;
- time and work to converge after connector outage;
- number of releases retained and storage pressure.

### E.7.5 Failure injections

Crash after every durable build event, duplicate every source change, reorder changes inside the connector’s allowed window, lose a worker lease, corrupt a staged artifact, fail one provider batch, activate concurrently from two coordinators, revoke the active release, and reconnect a frontend during activation. The expected behavior is expressed in machine invariants, not in log-message matching.

## E.8 Campaign 5: Garden agent and widget calibration

Garden demonstrates a user-level RAG system whose output includes choices, facts, citations, and widgets across multiple turns. Retrieval-only evaluation is insufficient.

### E.8.1 Experimental unit

The unit is a scripted or assessor-driven conversation with:

- an initial user goal;
- hidden constraints revealed over turns;
- expected intent transitions;
- authoritative structured facts;
- acceptable source evidence;
- expected clarifying questions or abstention;
- admissible widgets and fields;
- terminal user outcome.

Each conversation runs against one pinned release or against explicitly modeled evidence epochs. Repeats use controlled provider seeds when supported and always retain transcripts and traces.

### E.8.2 Factors

- intent classifier/router;
- structured-first versus retrieve-first ordering;
- connected-retrieval policy;
- search tool description and agent prompt;
- maximum tool iterations;
- evidence novelty threshold;
- structured-fact augmentation rules;
- grounded-widget admission and conflict suppression;
- answer model and decoding policy;
- conversation release scope.

### E.8.3 Session metrics

Measure task completion, number of turns, unnecessary tool calls, unsupported claims, fact conflicts, widget eligibility, field-level provenance, stale evidence reuse, clarification quality, abandonment proxy, total latency, and cost. Inspect the trajectory: two sessions may end with identical text while one leaked stale facts, retried a tool repeatedly, or crossed release epochs.

### E.8.4 Gates

- no widget field without admissible provenance;
- no conflict hidden by projection;
- no structured fact or chunk from a different release epoch unless the product explicitly marks it;
- noninferior task completion and grounding;
- bounded turn/tool count and latency;
- no increase in unsafe or misleading terminal outcomes;
- frontend snapshot-plus-suffix convergence for every calibrated session.

## E.9 Multi-fidelity allocation

Evaluation cost grows sharply from static laws to canary traffic. A candidate should advance only when the current fidelity can no longer decide its eligibility.

A practical ladder is:

1. **Schema and dependency validation.** Is the intervention well typed, and is its invalidation closure complete?
2. **Deterministic laws.** Can artifacts open, lineage reconcile, filters preserve policy, and reducers converge?
3. **Retrieval cells.** Does the candidate improve or preserve ranked evidence on a stratified suite?
4. **Repeated answer cells.** Does the distribution of answers, grounding, latency, and cost satisfy gates?
5. **Session calibration.** Do agent trajectories and frontend projections remain valid?
6. **Refresh and load simulation.** Does the candidate operate under corpus evolution and concurrency?
7. **Shadow.** What traces would production requests produce without affecting users?
8. **Canary.** Does a small eligible subject/request population satisfy online gates?
9. **Promotion.** Does CAS activation change the intended release pointer with rollback ready?

Successive halving is appropriate only within comparable candidates. It is unsafe to race a cheap retrieval-only candidate against an agent-policy candidate using one early scalar. The allocator should group candidates by minimum fidelity and semantic class.

## E.10 Statistical decision rules

Exact paired cells should remain the primitive `ragopt` unit. For each case $i$, repeat $r$, baseline $b$, and candidate $c$, retain the paired difference

$$
\Delta_{i,r,m} = m(c,i,r) - m(b,i,r)
$$

for every metric $m$. Pairing controls case difficulty and, where provider control permits, shared randomness. Aggregate reports should preserve strata and uncertainty rather than only pooled means.

Recommended rules include:

- exact or permutation tests for deterministic paired rankings;
- paired bootstrap intervals over cases for nDCG, recall, latency, and cost;
- cluster bootstrap at conversation or source level when observations are dependent;
- noninferiority margins for protected quality and safety metrics;
- lower confidence bounds for recall and success rates;
- upper confidence bounds for latency, cost, failure, and disclosure;
- sequential confidence methods for canaries when repeated peeking is expected;
- explicit multiplicity control or hierarchical gate ordering for large candidate families.

The gate program should evaluate hard constraints before preferences. A useful partial order is:

$$
\text{security} \prec \text{integrity} \prec \text{reliability} \prec \text{quality} \prec \text{latency/cost} \prec \text{preference}.
$$

A failure in an earlier class makes later aggregate gains irrelevant. Among surviving candidates, report the Pareto frontier. A human or product policy then chooses a release; `ragopt` should not conceal that policy inside an unexplained weighted sum.

## E.11 Temporal holdouts and corpus leakage

RAG evaluation is especially vulnerable to temporal leakage. A benchmark built from the same corpus snapshot used for candidate engineering may reward memorized source structure, stale aliases, or answers that are no longer authoritative. Maintain at least:

- a development workload tied to a known source snapshot;
- a hidden static holdout;
- a future-revision holdout consisting of changes captured after the candidate design began;
- a deletion/supersession suite;
- a production shadow sample with policy-safe retention.

Generated evaluation questions must retain their source revision and generation procedure. They should not be treated as independent evidence of quality when the same model/prompt family generated candidate representations. Correlated synthetic artifacts can make a representation scheme appear better than it is.

## E.12 Promotion report schema

A promotion report should be sufficient to reconstruct the decision without rerunning the campaign. It contains:

- baseline and candidate release specifications;
- intervention and dependency closure;
- source snapshot and workload identities;
- evaluator and judge identities;
- exact paired-cell coverage and missingness;
- metric distributions by protected stratum;
- every gate result with evidence references;
- failure and fallback distributions;
- refresh/load envelope;
- security/disclosure attestations;
- Pareto comparison;
- canary routing and rollback plan;
- decision authority and timestamp.

The report does not claim universal optimality. It states that a candidate is eligible, under a declared workload and operating envelope, to become the next active release.

# Appendix F. Verification, testing, and model checking {-}

The runtime semantics are useful only if they become executable obligations. This appendix maps each obligation to the cheapest verification technique that can detect its violation. Ordinary unit tests remain important, but concurrency, replay, corpus evolution, and stochastic providers require a layered strategy.

## F.1 Verification hierarchy

| Technique | Best target | Typical failure found |
|---|---|---|
| Example unit test | local branch or transformation | wrong field, score, or event |
| Golden/differential fixture | compatibility during migration | changed rank, citation, or trace |
| Property test | algebraic law over many inputs | non-idempotent reducer, unstable identity |
| Fuzz test | parser and state-machine boundary | malformed manifest, panic, invalid transition |
| State-machine model test | concurrent lifecycle | double activation, leaked lease, lost update |
| Fault-injection test | durable workflow | non-resumable build, duplicate side effect |
| Load/soak test | resource and deadline envelope | queue collapse, tail amplification |
| Statistical test | stochastic provider behavior | quality or latency regression |
| Formal model check | finite concurrency protocol | safety/liveness counterexample |
| Proof or proof assistant | small mathematical kernel | invalid law or incomplete precondition |

The architecture should expose pure reducers and transition validators so that most state behavior can be tested without starting servers or providers. Integration tests then verify that storage and transport adapters implement the same events.

## F.2 Source and snapshot test matrix

### F.2.1 Example cases

- first observation of a source object produces one upsert;
- identical repeated observation produces no semantic change;
- a newer content revision produces one replacement;
- metadata-only policy revision changes the policy projection without silently retaining an old authorization certificate;
- delete removes the object from the next complete snapshot;
- delete followed by recreate produces a distinct revision lineage according to source semantics;
- a barrier closes exactly the prefix promised by the connector;
- a restarted connector resumes from a committed cursor without dropping or inventing changes;
- an out-of-order stale revision cannot overwrite a newer accepted revision;
- two aliases for one source object normalize to the declared canonical identity.

### F.2.2 Properties

For a connector whose delivery contract permits duplicates:

$$
\operatorname{reduce}(S, e, e) = \operatorname{reduce}(S, e).
$$

For any permutation that preserves the connector’s causal order and barrier rules, reducing the event multiset yields the same captured snapshot. For a source snapshot digest $d$, repeated serialization and capture produce the same digest. A barrier identity binds the exact source frontier, admission-policy revision, and connector state used by the build.

### F.2.3 Generators

Generate small source worlds of documents with random content, metadata, roles, and revisions. Generate event traces containing duplicates, delayed events, deletes, recreations, and barriers. Shrinking should preserve the failing causal relation; otherwise the minimal counterexample may become an invalid trace. Store every discovered seed as a regression fixture.

## F.3 Derivation and incremental-maintenance tests

### F.3.1 Local deterministic laws

For normalization, chunking, representation projection, and embedding-cache keys:

- determinism under repeated execution;
- stable identity under irrelevant input ordering;
- sensitivity to every behaviorally material input;
- locality: an unchanged document does not change another document’s derived IDs;
- range validity and exact source-span reconstruction;
- representation-to-source lineage totality;
- no representation may be admitted as authoritative evidence without resolving to a source evidence object.

### F.3.2 Incremental/full equivalence

For randomly generated source state $D$ and valid change batch $\Delta D$:

$$
\operatorname{normalize}\left(F_{inc}(F(D), \Delta D)\right)
=
\operatorname{normalize}\left(F(D \oplus \Delta D)\right).
$$

Normalization removes irrelevant backend ordering and serial-format variation while retaining all observable content, identity, policy, and search semantics. Run the property after every barrier and after arbitrary compaction points. Include deletes, boundary-shifting edits, generated representations, failed/quarantined derivations, and cache hits.

### F.3.3 Crash-point enumeration

Instrument the build coordinator so that a test can terminate it immediately after every durable event:

- source cursor commit;
- impact-plan commit;
- work-item lease;
- provider response receipt;
- artifact write;
- artifact digest verification;
- item commit;
- stage seal;
- index checkpoint;
- evaluation cell;
- release registration;
- activation CAS.

Restart from the durable ledger and verify that the final registered release and visible activation effect equal an uninterrupted execution. Provider calls may be repeated; publication and activation must not produce duplicate semantic effects.

## F.4 Index-backend conformance suite

Every backend implements a capability-specific suite.

### F.4.1 Common exact semantics

- inserted items are searchable according to the metric;
- deleted/tombstoned items are never returned;
- filters are sound: every result satisfies the filter;
- a stable total order resolves equal scores;
- scores are finite and normalized as declared;
- opening a checkpoint reproduces the same observable index;
- concurrent snapshot readers see one committed view;
- compaction preserves logical contents;
- malformed or incompatible manifests fail closed.

### F.4.2 Exact backend oracle

For small generated indexes, compare against a pure in-memory implementation. Exhaustively enumerate queries from a finite vector/term domain where feasible. This oracle should be intentionally simple, not optimized.

### F.4.3 Approximate backend relation

An ANN backend is not tested for equality with the exact oracle. It is tested for:

- sound membership and filters;
- recall/rank-distance relation under declared parameters;
- deterministic or distributional reproducibility class;
- monotonicity expectations where valid, such as nondecreasing search effort not materially reducing recall;
- behavior under insert/delete/overlay/compaction;
- no catastrophic stratum with hidden zero recall.

Performance assertions are separated from logical conformance so a slow CI host cannot make correctness flaky.

## F.5 Query algebra property tests

Generate finite channel rankings with ties, duplicate chunks through multiple representations, policy labels, and finite scores. Then verify:

- collapse returns at most one candidate per collapse identity;
- fusion is deterministic under map/input iteration permutation;
- total-order comparator is antisymmetric, transitive, and total;
- every fused contribution refers to an input rank;
- policy filtering is monotone: tightening policy never introduces a candidate;
- authorization precedes every remote text-bearing event;
- evidence admission never exceeds declared count/token/rune budgets;
- admitted evidence is a subsequence of the policy-valid ranked candidates unless diversification explicitly documents a reorder;
- citations resolve only to admitted evidence;
- fallback paths are explicit in the trace and cannot masquerade as the intended stage.

RRF deserves a direct reference implementation with rational or high-precision arithmetic for small cases. Production floating-point output can then be compared after the declared rounding and tie policy.

## F.6 Remote-disclosure spy tests

Implement provider spies for rewrite, embedding, reranking, and generation. Each spy records the exact text, metadata, subject certificate, release, and purpose presented to it. The test corpus contains uniquely marked secrets by role and source scope. For every generated subject/query pair:

1. run the query or agent turn;
2. collect all remote disclosures;
3. assert that every disclosed item is authorized for that subject, provider, purpose, and jurisdiction;
4. assert that returned evidence is a subset of authorized, admitted material;
5. assert that trace redaction does not itself leak the marked secret.

This suite should run against GEC before any relevance migration. It converts a subtle ordering defect into a mechanically testable security property.

## F.7 Release and activation state-machine tests

Model commands such as register, verify, stage, activate, acquire, release, revoke, retire, and purge. Generate command sequences against both a pure model and the real registry implementation.

Key invariants:

- at most one active release per routing key;
- activation succeeds only from an eligible staged release;
- a failed compare-and-swap does not change the head;
- a lease returns exactly the release that was active at acquisition linearization;
- all evidence and events under a lease carry that release;
- no new lease is granted to draining, retired, revoked, or quarantined releases;
- retirement cannot purge resources while leases remain;
- rollback is another validated activation, not mutation of an old release;
- revocation behavior for in-flight leases follows the declared policy;
- registry replay reconstructs the same head and lease-independent state.

Run concurrent histories with randomized scheduling. Record invocation and response times and check linearizability for the active-head register and lease acquisition. A lightweight model checker can enumerate short histories; a stress harness can explore longer randomized histories.

## F.8 Query-machine transition tests

The query interpreter should expose a pure transition function or test seam over stage outcomes. Generate combinations of:

- rewrite success, timeout, malformed result, and fallback;
- lexical/vector/connected channel success, partial timeout, and empty result;
- reranker success, timeout, bad scores, and provider denial;
- evidence empty, over budget, duplicate, or stale;
- generator success, invalid contract, repair success/failure, and stream interruption;
- client cancellation at every transition;
- terminal event persistence success/failure.

Verify that every run reaches one terminal class within the model’s assumptions, closes its release lease exactly once, records every fallback, and never emits a final answer before validation. Deadline allocation must be monotone in elapsed time and never produce a negative child budget.

## F.9 Agent and tool-loop tests

Agentic RAG adds replay and nontermination hazards. Test:

- one logical tool call ID executes at most one semantic search effect despite transport replay;
- repeated tool calls can reuse the turn evidence ledger without relabeling existing evidence;
- a tool result belongs to the turn release;
- zero-search completion is represented distinctly from search failure;
- maximum-iteration exhaustion produces a terminal, inspectable result;
- cancellation interrupts model and tool work and persists a terminal event;
- malformed tool arguments do not mutate evidence state;
- connected retrieval failures follow route policy;
- final citations resolve to evidence actually accumulated during the turn;
- conversation-scoped reuse across a release change creates a declared new evidence epoch or is rejected.

A small-step reference interpreter can generate the expected trace from scripted model choices. Product adapters are differential-tested against it while retaining product-specific tools and projections.

## F.10 Frontend reducer tests

The frontend projection contract should be testable in Go/TypeScript against the same event schema.

### F.10.1 Core convergence law

For a snapshot $S_n$ at ordinal $n$ and suffix events $e_{n+1},\ldots,e_m$:

$$
\operatorname{reduce}(S_n, [e_{n+1},\ldots,e_m]) = S_m.
$$

The result must remain equal under duplicate delivery and any reordering permitted by the transport buffer rules.

### F.10.2 Required cases

- live events arrive before snapshot hydration;
- duplicate event ID before and after hydration;
- stale entity version with larger global ordinal;
- fresh entity version delivered out of order;
- append patch replayed twice;
- append patch with wrong offset;
- snapshot truncation followed by a suffix beyond retained history;
- reconnect during release activation;
- cancellation and error terminal events;
- widget retraction or tombstone;
- server replay from an event cursor;
- client with unsupported schema version.

Append patches should carry an expected offset or segment identity. The reducer either applies exactly once or requests resynchronization; it must not silently duplicate text.

### F.10.3 Cross-language fixture

Serialize event traces and expected terminal state into a language-neutral fixture. Run the authoritative reducer in Go and the browser reducer in TypeScript. The normalized states must be equal. This catches drift between backend semantics and frontend convenience code.

## F.11 Differential migration fixtures

Before deleting duplicate implementations, capture behavior from the current products. A fixture contains input corpus, bundle/release inputs, subject, query or conversation, provider stubs, expected ranked candidates, evidence labels, answer contract result, observations, and frontend events.

Run current and target implementations side by side. Classify differences:

- intended security correction;
- intended deterministic-order correction;
- intended release-lineage addition;
- acceptable trace enrichment;
- unacceptable behavior regression;
- nondeterministic provider variation requiring repeated comparison.

Do not require byte equality where the migration intentionally changes identities or event envelopes. Define a normalization that preserves the semantic layer being claimed. For example, GEC may intentionally filter before reranking; its remote-disclosure trace must differ, while its authorized result ranking should remain compatible or be reevaluated.

## F.12 Load, soak, and chaos verification

A production RAG system has coupled queues: source capture, derivation, embedding/reranking provider calls, build publication, query channels, generation streams, event persistence, and WebSocket delivery. Test the system under realistic joint load rather than isolated microbenchmarks.

Scenarios include:

- steady query load during a large corpus refresh;
- burst of source changes while a compaction runs;
- provider rate-limit reduction;
- slow frontend consumers;
- registry/storage latency;
- repeated failed candidate builds;
- release activation during long agent turns;
- old-release drain with new-release canary load;
- connector outage and catch-up;
- mass cancellation.

Measure queue age, admission rejections, deadline exhaustion by stage, release lease duration, memory, file descriptors, provider concurrency, event lag, and freshness. Soak tests should cover retention and compaction cycles; otherwise resource leaks and ever-growing ledgers remain invisible.

## F.13 TLA+ model outline

The release/build protocol is small enough for a bounded TLA+ model. Suggested variables:

```text
active            routing key -> release or None
releaseState      release -> Registered | Verified | Staged | Active |
                               Draining | Retired | Revoked | Quarantined
leases            query -> release or None
buildState        build -> lifecycle state
registeredByBuild build -> release or None
frontier          connector -> cursor/barrier
published         artifact digest set
```

Actions include `Register`, `Verify`, `Stage`, `ActivateCAS`, `Acquire`, `Release`, `Supersede`, `Retire`, `Revoke`, `BuildCommit`, `Resume`, and `Cancel`. Safety invariants:

```text
OneActive == each routing key has at most one active head
LeaseEligible == every lease references a release active at acquisition
NoPrematurePurge == leased releases are not purged
CASLinear == successful activation observes expected predecessor
OneReleasePerBuild == a build registers at most one semantic release
NoActiveQuarantine == active heads are never quarantined
```

Liveness assumptions should be modest and explicit: fair storage, eventual worker retry, and eventual lease closure for nonfaulty clients. Candidate liveness properties include eventual build terminality and eventual retirement of a superseded release after all leases close. Model cancellation and revocation separately because forced termination of in-flight queries is a product policy, not a universal law.

The frontend protocol can use a second small model with snapshot ordinal, delivered event set, dedupe set, entity versions, and append offsets. Its invariant is convergence with the authoritative event prefix or an explicit resync state.

## F.14 Proof targets

Formal proof effort should focus on kernels with high reuse and small state.

1. **Total ranking.** Prove the comparator yields a total order over all finite valid scores and stable IDs.
2. **Incremental algebra.** Prove local delta rules for deterministic document-local derivations; use full-build differential testing for provider-backed stages.
3. **Overlay semantics.** Prove lookup/search membership of base plus ordered deltas with tombstones equals the integrated logical multiset, before approximation.
4. **Authorization noninterference.** Prove that no remote-text action is enabled without a valid authorization certificate for the candidate set.
5. **Activation linearizability.** Prove or model-check the CAS head and lease-acquisition protocol.
6. **Reducer convergence.** Prove idempotence and stale-update rejection for replace/merge/tombstone events and exact-once offset behavior for append events.
7. **Gate monotonicity.** Prove that adding a failed earlier hard gate cannot make a candidate eligible through later scores.

Provider quality, natural-language correctness, and empirical latency are not suitable proof targets. They require measurement under retained uncertainty.

## F.15 CI and release verification tiers

A workable pipeline separates fast deterministic checks from expensive campaigns.

- **Per commit:** unit, property, fuzz corpus, manifest/schema, pure reducer, dependency-closure, and small differential fixtures.
- **Per merge:** backend conformance, cross-language reducer, state-machine randomized tests, provider-spy security tests, and representative retrieval cells.
- **Nightly:** larger fuzzing, build crash matrix, ANN oracle suite, refresh simulation, session calibration subset, and moderate load.
- **Candidate release:** complete paired evaluation, security attestation, full refresh/compaction simulation, load envelope, and reproducible promotion report.
- **Canary:** online SLO/gate monitor with automatic stop/rollback authority for hard constraints.
- **Periodic:** full rebuild audit against maintained state, disaster-recovery exercise, retention/purge audit, and model-check update when protocol changes.

A test result is itself an immutable artifact referenced by the release or promotion report. “Tests passed” without evaluator identity, input snapshot, seed, and artifact digest is not sufficient evidence.

# Appendix G. Empirical source map, limitations, and current-to-target mapping {-}

## G.1 Scope of the supplied snapshot

The review covers five development scopes. Counts are static measurements of the supplied archive and are included to characterize the evidence base, not to compare team productivity.

| Scope | Files | Go files | Nonblank Go lines | Go test functions |
|---|---:|---:|---:|---:|
| `ragkit` | 176 | 173 | 17,743 | 273 |
| `ragopt` | 120 | 45 | 5,925 | 42 |
| RAG-TTC | 1,302 | 515 | 76,705 | 905 |
| GEC RAG | 1,114 | 200 | 28,668 | 252 |
| TTC Garden | 940 | 70 | 8,485 | 108 |
| **Total** | **3,652** | **1,003** | **137,526** | **1,580** |

The RAG-TTC `pkg` tree substantially overlaps `ragkit`: 165 matching relative Go paths were found, with 50 byte-identical files and 114 pairs at token-set Jaccard similarity of at least 0.95. This supports a hard shared-package migration rather than continued synchronization of copied substrates. The overlap statistic does not imply all same-path files are semantically interchangeable; product-specific forks require fixture-backed review.

## G.2 `ragkit` source map

| Source area | Evidence used in this volume |
|---|---|
| `rag/answering/service.go` | channel execution, fusion/rerank flow, fallback and observation behavior |
| `rag/answering/context.go` | whole-chunk context admission, ordering, count/rune budgets |
| `rag/answering/contract.go` | grounded answer schema, citation and supplied-evidence validation |
| `rag/indexbundle/build.go` | immutable full-bundle construction and atomic publication |
| `rag/indexbundle/open.go` | manifest, backend, and query-embedder compatibility verification |
| `rag/indexbundle/verified_documents.go` | source-root confinement and corpus digest checks |
| `rag/flow` | stage-local caching, retries, resource admission, and budgets |
| document/chunk/representation packages | deterministic identity and derivation substrate |

`ragkit` is therefore already a substantial batch RAG library. The target architecture extends it into corpus, release, index-view, interpreter, trace, and stream semantics; it does not replace its current deterministic kernels.

## G.3 RAG-TTC source map

| Source area | Evidence used in this volume |
|---|---|
| `cmd/rag-ttc/cmds/indexes/build.go` | applied complete-corpus representation/embedding build |
| `cmd/rag-ttc/cmds/indexes/ann_bakeoff.go` | exact-oracle HNSW quality/latency gate and rebuild check |
| `cmd/rag-ttc/cmds/workspace/index.go` | committed source snapshot to workspace artifacts |
| `pkg/gochunk/snapshot.go` | Git-tree capture, tracked-file admission, snapshot digest |
| `pkg/ttcrag/search.go` | model-invoked retrieval routes and turn evidence ledger |
| `pkg/app/chat/controller.go` | active-turn custody, cancellation, observation collection |
| `pkg/app/chatserver` | persistent submissions, timelines, WebSocket streaming, runtime composition |

RAG-TTC provides the richest applied bridge between index construction and agentic serving. Its principal architectural liability is the copied common substrate and the absence of native corpus reconciliation and release activation.

## G.4 GEC source map

| Source area | Evidence used in this volume |
|---|---|
| `internal/knowledge/service.go` | startup bundle, query-time synonyms/reranker, post-ranking scope filtering |
| `internal/knowledge/sweep.go` | offline fusion/vector-weight grid sweep |
| `internal/knowledge/tool.go` | server-controlled scopes and run-scoped evidence labels |
| `web/src/ws/wsManager.ts` | snapshot hydration, pre-hydration buffering, ordering, truncation |
| `web/src/store/timelineSlice.ts` | entity upserts and append/replace stream patches |

The imported `internal/knowledgebuild` package is absent from the supplied snapshot. Design records and call sites describe its role, but its implementation was not directly inspected. Assertions about exact GEC build internals are therefore intentionally limited. The query and frontend findings are based on present source.

## G.5 Garden source map

| Source area | Evidence used in this volume |
|---|---|
| `backend/internal/ragsearch/ragsearch.go` | intent routes and per-conversation session resources |
| `backend/internal/ragsearch/searchtool.go` | structured-first facts, routed retrieval, and observations |
| `backend/internal/ragsearch/grounded_widgets.go` | evidence-bound typed frontend projections |
| `backend/internal/calibration/runner.go` | multi-turn calibration and stable terminal polling |

Garden is the clearest evidence that production RAG semantics extend beyond ranked text and answer strings. Structured facts, typed widgets, conversation state, and field-level provenance are user-visible semantics and belong in release/evaluation scope even though their domain meaning remains in the Garden application.

## G.6 `ragopt` source map

`ragopt` was reviewed as a whole because its responsibilities cut across packages: candidate construction, exact baseline/candidate pairing, resumable run custody, comparison, ordered gates, and reporting. No native corpus revision, index build, query trace, release activation, or frontend projection model was found. This is a deliberate boundary, not a deficiency. The proposed `ragopt/ragspace` adapter supplies RAG-specific intervention spaces and evaluators while preserving the generic experiment kernel.

## G.7 High-priority findings

### G.7.1 P0: authorization before remote disclosure

GEC’s observed ordering allows candidate hydration and optional remote reranking before final source-scope filtering. A candidate that will later be removed can therefore cross a provider boundary. The target order is policy-constrained candidate generation or a local authorization filter before any remote text-bearing stage, with an auditable certificate carried through the trace.

### G.7.2 P0: behavior-complete release identity

GEC’s reranker and synonyms are query-time configuration outside the opened bundle identity. Garden composes an index bundle, structured fact database, tool policy, prompts, and projections without one material release root. The target release manifest binds every input that can change observable behavior or disclosure.

### G.7.3 P0: atomic activation and pinning

The applied services primarily open fixed resources at startup. There is no shared hot-stage, compare-and-swap activation, draining, rollback, or lease protocol. The target registry gives each query/turn/session one release epoch and permits safe replacement without mixed evidence.

### G.7.4 P1: corpus-change semantics

The shared builder consumes complete corpus material and emits immutable bundles. RAG-TTC adds strong Git snapshot capture and caches, but not revision reconciliation. The target introduces source changes, barriers, cursors, impact plans, delta overlays, compaction, and full-rebuild equivalence.

### G.7.5 P1: query-mode separation

Direct search, retrieve-generate, and agentic search are implemented through related primitives but have different state and terminal semantics. The target exposes separate interpreters over one retrieval plan/algebra.

### G.7.6 P1: frontend replay laws

GEC has a practical hydration buffer, but stale entity versions and duplicate append patches are not rejected by a complete shared law. The target uses versioned event envelopes, event-ID deduplication, entity versions, exact append offsets, and resynchronization.

### G.7.7 P1: joint optimization

Current applied experiments are valuable but narrow: fusion-weight sweeps and ANN parameter bakeoffs. The target uses typed intervention spaces, dependency closure, temporal holdouts, paired statistics, multiple fidelities, and constraint-first Pareto gates.

### G.7.8 P2: durable build custody

`ragkit/flow` provides stage execution controls, but no durable cross-process production build state machine. The target adds append-only build events, resumable work items, leases, verification, quarantine, cancellation, and release registration.

## G.8 Current-to-target package mapping

| Current capability | Current owner | Target owner | Migration relation |
|---|---|---|---|
| documents, chunks, representations | `ragkit` and copy | `ragkit/corpus`, `ragkit/derive` | retain and generalize |
| full immutable bundle | `ragkit/indexbundle` | `ragkit/index` plus `ragkit/release` | wrap, then extend |
| stage cache/retry/budget | `ragkit/flow` | `ragkit/flow` used by build/query runtimes | retain; do not overpromote |
| full RAG-TTC index command | RAG-TTC | product connector + `ragkit/build` | refactor orchestration |
| Git committed snapshot | RAG-TTC `gochunk` | connector implementation of `ragkit/corpus` | extract interface, retain policy |
| exact/ANN bakeoff | RAG-TTC command | `ragkit/eval` + `ragopt/ragspace` | turn into reusable campaign |
| GEC query service | GEC | GEC facade over `ragkit/query` | preserve product policy |
| GEC scopes/roles | GEC | GEC policy adapter + shared authorization certificate | retain domain meaning |
| GEC synonyms/reranker | GEC config | behavior-complete release query policy | materialize and identify |
| turn evidence ledger | GEC/RAG-TTC | `ragkit/evidence` with scoped adapters | share laws, retain presentation |
| Garden structured facts | Garden | Garden evidence adapter | retain in product |
| grounded widgets | Garden | Garden projection over `ragkit/stream` | retain product semantics |
| chat timelines/WebSocket | applied apps | product server over shared event envelope/reducer law | share protocol, not UI domain |
| experiment run/gates | `ragopt` | `ragopt` | retain generic kernel |
| RAG candidate space | ad hoc commands | `ragopt/ragspace` | add thin domain adapter |

## G.9 Proposed repository/package shape

A practical target layout is:

```text
ragkit/
  corpus/          revision, change, connector, cursor, barrier, snapshot
  derive/          impact graph, deterministic stages, lineage, cache keys
  index/           logical view, exact/ANN capabilities, overlay, compaction
  release/         behavior-complete spec, registry, activation, leases
  query/           plans, stages, direct/answer/agent interpreters
  evidence/        typed evidence, admission, scoped sessions, provenance
  trace/           versioned intensional and operational observations
  stream/          event envelope, snapshot, reducer laws, replay cursors
  eval/            RAG workloads, metrics, refresh and session harnesses
  flow/            bounded local execution primitives

ragopt/
  ...              existing generic experiment kernel
  ragspace/         interventions, dependency closure, fidelities, gates

products/
  gec/              authorization, source roles, admin tools, judges, UI policy
  rag-ttc/          TTC sources, connected retrieval, agent tools, providers
  garden/           intent, structured facts, catalog semantics, widgets
```

`ragkit/build` may be introduced only when at least two products share the same durable build-state semantics. Until then, the transition types and event laws can live in `corpus`, `derive`, `index`, and `release`, while each product composes them with its existing workflow/runtime infrastructure. This avoids creating an orchestration framework before operational commonality is demonstrated.

## G.10 Product migration acceptance map

### G.10.1 GEC

- current authorized outputs captured as differential fixtures;
- authorization enforced before all remote text disclosure;
- synonyms, reranker, prompts, and policy bound into release identity;
- query/turn pinned to a release lease;
- full refresh and activation available before incremental refresh;
- frontend reducer satisfies duplicate/stale/append laws;
- fusion/rerank campaign uses protected role/scope strata.

### G.10.2 RAG-TTC

- copied common packages deleted after compatibility classification;
- committed Git capture implements shared source revision/snapshot interface;
- index command emits a behavior-complete staged release;
- direct search, answer, and agent tool use separate interpreters/traces;
- HNSW backend passes common capability and dynamic-state certification;
- chat server acquires/releases one release per turn;
- optimization commands become reproducible `ragopt/ragspace` campaigns.

### G.10.3 Garden

- all transitive copied retrieval substrate replaced by shared packages;
- structured fact snapshot and presentation policy included in Garden release material;
- conversation evidence reuse has explicit release-epoch rules;
- grounded widget fields carry evidence and release provenance;
- calibration runner records complete session traces and paired candidate cells;
- browser/server projection reducers share fixtures and convergence laws.

## G.11 Analysis limitations

1. **Static snapshot.** The archive is a development snapshot, not necessarily the deployed system or latest branch.
2. **Missing GEC build source.** `internal/knowledgebuild` is referenced but absent; detailed build claims rely only on call sites and design material.
3. **Toolchain mismatch.** The repositories require Go 1.26.x; the environment provides Go 1.23.2 and cannot download a newer toolchain. The snapshot was not compiled or executed.
4. **No production telemetry.** Latency, cost, failure, traffic, corpus-change rate, and user-outcome claims are design requirements, not measurements of a live deployment.
5. **No provider experiment.** Remote model behavior was not benchmarked. Stochastic semantics and gates are proposed from interfaces and runtime paths.
6. **No security penetration test.** The disclosure issue is a source-ordering finding, not a claim that a specific provider received unauthorized production content.
7. **Code-count limitations.** File/line/test counts are descriptive and depend on the extracted archive and simple static counting rules.
8. **Formalization boundary.** The operational rules abstract storage, scheduler, network, and model internals. Implementations must refine them and state any additional failure modes.

These limitations do not weaken the central architectural conclusion: the supplied implementations already exhibit corpus capture, immutable indexes, retrieval pipelines, agentic tool use, persistent streaming, and optimization experiments, but the shared packages do not yet model their coupled runtime semantics as one production RAG domain.

# Appendix H. Selected bibliography {-}

This bibliography emphasizes primary sources that motivate the formal and empirical structures used in the volume. It is not a survey of every RAG framework or vector database.

## H.1 Retrieval-augmented generation and retrieval

**Lewis, Patrick, Ethan Perez, Aleksandra Piktus, Fabio Petroni, Vladimir Karpukhin, Naman Goyal, Heinrich Kuttler, et al.** 2020. “Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks.” *Advances in Neural Information Processing Systems* 33.

**Karpukhin, Vladimir, Barlas Oguz, Sewon Min, Patrick Lewis, Ledell Wu, Sergey Edunov, Danqi Chen, and Wen-tau Yih.** 2020. “Dense Passage Retrieval for Open-Domain Question Answering.” In *Proceedings of EMNLP 2020*.

**Khattab, Omar, and Matei Zaharia.** 2020. “ColBERT: Efficient and Effective Passage Search via Contextualized Late Interaction over BERT.” In *Proceedings of SIGIR 2020*.

**Thakur, Nandan, Nils Reimers, Andreas Rucklé, Abhishek Srivastava, and Iryna Gurevych.** 2021. “BEIR: A Heterogeneous Benchmark for Zero-Shot Evaluation of Information Retrieval Models.” In *NeurIPS Datasets and Benchmarks*.

**Petroni, Fabio, Aleksandra Piktus, Angela Fan, Patrick Lewis, Majid Yazdani, Nicola De Cao, James Thorne, et al.** 2021. “KILT: A Benchmark for Knowledge Intensive Language Tasks.” In *Proceedings of NAACL-HLT 2021*.

**Robertson, Stephen, and Hugo Zaragoza.** 2009. “The Probabilistic Relevance Framework: BM25 and Beyond.” *Foundations and Trends in Information Retrieval* 3 (4): 333-389.

**Cormack, Gordon V., Charles L. A. Clarke, and Stefan Buettcher.** 2009. “Reciprocal Rank Fusion Outperforms Condorcet and Individual Rank Learning Methods.” In *Proceedings of SIGIR 2009*.

**Järvelin, Kalervo, and Jaana Kekäläinen.** 2002. “Cumulated Gain-Based Evaluation of IR Techniques.” *ACM Transactions on Information Systems* 20 (4): 422-446.

**Malkov, Yu. A., and D. A. Yashunin.** 2020. “Efficient and Robust Approximate Nearest Neighbor Search Using Hierarchical Navigable Small World Graphs.” *IEEE Transactions on Pattern Analysis and Machine Intelligence* 42 (4): 824-836.

## H.2 RAG evaluation

**Es, Shahul, Jithin James, Luis Espinosa-Anke, and Steven Schockaert.** 2024. “RAGAS: Automated Evaluation of Retrieval Augmented Generation.” In *Proceedings of the 18th Conference of the European Chapter of the Association for Computational Linguistics: System Demonstrations*.

**Saad-Falcon, Jon, Omar Khattab, Christopher Potts, and Matei Zaharia.** 2024. “ARES: An Automated Evaluation Framework for Retrieval-Augmented Generation Systems.” In *Proceedings of NAACL-HLT 2024*.

The evaluation design in this volume uses these works as evidence for decomposed RAG measurements, while adding release lineage, authorization, freshness, failure, agent trajectories, and frontend projection as first-class dimensions.

## H.3 Denotational, operational, and effectful semantics

**Scott, Dana, and Christopher Strachey.** 1971. “Toward a Mathematical Semantics for Computer Languages.” Programming Research Group Technical Monograph PRG-6, Oxford University Computing Laboratory.

**Kahn, Gilles.** 1974. “The Semantics of a Simple Language for Parallel Programming.” In *Information Processing 74: Proceedings of IFIP Congress 74*.

**Plotkin, Gordon D.** 1981. “A Structural Approach to Operational Semantics.” DAIMI FN-19, Aarhus University. Reprinted with revisions in *The Journal of Logic and Algebraic Programming* 60-61 (2004): 17-139.

**Moggi, Eugenio.** 1991. “Notions of Computation and Monads.” *Information and Computation* 93 (1): 55-92.

**Fritz, Tobias.** 2020. “A Synthetic Approach to Markov Kernels, Conditional Independence and theorems on Sufficient Statistics.” *Advances in Mathematics* 370: 107239.

These sources motivate the distinction between extensional denotations, small-step labelled transitions, stream/process meanings, and effectful or probabilistic composition. The APIs proposed here use ordinary Go types rather than exposing the mathematical machinery directly.

## H.4 Incremental computation, replicated state, and concurrency

**Budiu, Mihai, Tej Chajed, Frank McSherry, Leonid Ryzhyk, and Val Tannen.** 2023. “DBSP: Automatic Incremental View Maintenance for Rich Query Languages.” *Proceedings of the VLDB Endowment*.

**Shapiro, Marc, Nuno Preguiça, Carlos Baquero, and Marek Zawirski.** 2011. “Conflict-Free Replicated Data Types.” In *Stabilization, Safety, and Security of Distributed Systems (SSS 2011)*.

**Lamport, Leslie.** 1994. “The Temporal Logic of Actions.” *ACM Transactions on Programming Languages and Systems* 16 (3): 872-923.

**Lamport, Leslie.** 2002. *Specifying Systems: The TLA+ Language and Tools for Hardware and Software Engineers*. Addison-Wesley.

DBSP informs the full-versus-incremental equivalence law and signed-change perspective. CRDT work informs the analysis of duplicate/out-of-order frontend events, while also clarifying why unrestricted text append is not automatically a convergent replicated datatype. TLA/TLA+ motivates protocol-level safety and liveness models for activation, leasing, and replay.

## H.5 Property-based verification

**Claessen, Koen, and John Hughes.** 2000. “QuickCheck: A Lightweight Tool for Random Testing of Haskell Programs.” In *Proceedings of ICFP 2000*.

Property-based testing is used throughout this volume for identities, ranking orders, incremental/full equivalence, state-machine traces, and frontend convergence. The method complements, rather than replaces, product fixtures and stochastic evaluation.

## H.6 Empirical system under study

**Supplied repository snapshot.** 2026. `ragkit`, `ragopt`, RAG-TTC, GEC RAG Chat, TTC Garden Assistant, associated tests, design records, and frontend code, provided for this architecture study. All implementation-specific findings in the volume derive from that snapshot subject to the limitations in Appendix G.

# Appendix I. Glossary of operational RAG terms {-}

**Activated release.** The immutable behavior-complete release currently selected by a routing key for new leases.

**Activation.** A compare-and-swap transition that changes release resolution. It is distinct from building, publishing, staging, and warming.

**Agent interpreter.** A query interpreter whose execution includes model decisions and zero or more tool calls before a terminal projection.

**Authorization certificate.** An auditable value proving which subject, policy revision, release, candidate set, provider, and purpose authorize a disclosure or stage transition.

**Barrier.** A source event asserting that a finite prefix or snapshot frontier is complete enough to build and identify.

**Base-plus-delta index.** A logical searchable view composed from an immutable base index, one or more change layers, and tombstones, later compacted into a new base.

**Behavior-complete release.** An immutable manifest over all inputs capable of changing observable RAG behavior: corpus, derivations, indexes, query and answer policy, providers, structured stores, and presentation.

**Build intent.** A durable request to derive a candidate release from a source frontier and release specification.

**Candidate.** A proposed release or release patch evaluated against a baseline under an explicit intervention declaration.

**Change.** A typed source revision event such as upsert, delete, or barrier. Delivery may be duplicated; semantic reduction must be idempotent.

**Collapse.** Mapping multiple searchable representations or duplicate candidates to one logical evidence identity under a defined score/contribution rule.

**Compaction.** A semantics-preserving maintenance operation that integrates delta layers and tombstones into a new base representation.

**Conversation epoch.** A declared interval in which conversation-scoped evidence belongs to one release. A release change either starts a new epoch or is rejected under the product policy.

**Corpus snapshot.** A finite, identified source state at a barrier, including admission policy and source lineage.

**Denotational semantics.** The mathematical meaning of a RAG release/service as a mapping from subject, state, and request to outcomes and traces, abstracting from particular execution steps.

**Direct interpreter.** A query interpreter that terminates with ranked evidence and trace rather than generating an answer.

**Disclosure.** Transmission of source-derived content or metadata across a trust boundary, including to embedding, reranking, generation, logging, or telemetry systems.

**Evidence.** Authoritative or explicitly typed material admitted for use in an answer or presentation. A searchable representation is not automatically evidence.

**Evidence session.** Scoped mutable custody of admitted evidence and stable labels over an operation, turn, run, or conversation epoch.

**Extensional outcome.** The externally observable result class and content, such as ranked evidence, answer, abstention, failure, or presentation state.

**Fallback.** A declared alternate transition after stage failure or deadline, retained in the trace because it can change outcomes and reliability semantics.

**Freshness.** The relation between source event time/frontier and the release serving a query. It is not synonymous with build recency.

**Full-rebuild oracle.** A clean derivation from the complete source snapshot used to validate incremental maintenance.

**Gate.** A typed decision predicate over experiment evidence. Hard gates are evaluated before preference comparisons.

**Impact plan.** The dependency-closure computation that identifies which derived items and evaluations a source change or intervention invalidates.

**Incremental view maintenance.** Updating derived state from source changes while preserving equivalence to recomputation from the integrated source state.

**Intensional trace.** The lineage, decisions, disclosures, fallbacks, latency, cost, and iteration history by which an outcome was produced.

**Interpreter.** A runtime that executes a typed query plan under a release lease. Direct, answer, and agent interpreters have different terminal rules.

**Lease.** A reference to one release acquired for a query, turn, or session epoch; it prevents mixed-release execution and premature resource retirement.

**Logical index view.** The abstract searchable relation seen by query code, independent of whether its physical representation is exact, ANN, sharded, or base-plus-delta.

**Noninferiority.** A statistical decision that a candidate is not worse than a baseline by more than a declared margin on a protected metric or stratum.

**Observation.** A versioned, typed trace event emitted by build, query, activation, or projection machines.

**Operational semantics.** The labelled transition rules by which runtime states evolve through source changes, builds, searches, provider calls, streams, failures, and activation.

**Overlay.** A physical or logical delta layer queried together with a base index before compaction.

**Pinned query/turn.** An execution whose every stage, evidence item, structured fact, citation, and event belongs to one release lease.

**Presentation interpreter.** Product-owned logic that projects evidence and answer state into typed frontend entities and events.

**Projection reducer.** A deterministic state reducer that reconstructs frontend state from a snapshot and event suffix under deduplication and version rules.

**Query algebra.** The ordered composition of rewrite, channels, collapse, fusion, policy, rerank, hydrate, evidence admission, generation, validation, and projection operators.

**Release registry.** Durable custody of registered releases, eligibility state, active routing heads, activation history, and retirement state.

**Representation.** Searchable derived material linked to source evidence, such as contextual text, summary, question, or entity text. It aids retrieval but carries no independent authority by default.

**Retrieve-then-generate interpreter.** A query interpreter that performs a bounded retrieval plan once, constructs context, generates, validates, and emits a terminal answer.

**Revision.** A source-system identity for a particular state of an object or policy. Revision semantics are connector-specific but must support ordering or conflict rules.

**Routing key.** The tenant, product, environment, corpus, or cohort key whose active release is changed atomically.

**Semantic class.** The declared kind of change made by an intervention: operational, approximation, relevance, knowledge, policy/security, interaction, or presentation.

**Snapshot-plus-suffix law.** The requirement that hydrating a frontend snapshot and reducing all later valid events yields the same state as the authoritative event prefix, despite permitted duplicates and reordering.

**Source frontier.** The connector cursor, revisions, barriers, and policy state delimiting the source world captured by a build.

**Staged release.** A verified, loadable release prepared for activation but not yet selected for new queries.

**Subject.** The authenticated and authorized principal, including tenant, roles, scopes, purpose, and relevant policy context.

**Tombstone.** A durable negative change that suppresses a deleted logical item in overlays and future releases until correctly compacted or recreated.

**Trace equivalence.** Equality or an explicit relation over intensional behavior, stronger than final-answer equality and parameterized by what the comparison is intended to preserve.

**Watermark.** A measured source or build frontier used to quantify freshness and progress; it may represent event time, revision position, capture completion, or activation.
EOF
wc -l -w -c /mnt/data/rag_functionality_work/v2/The_Semantics_and_Dynamics_of_RAG.md
```

<details><summary>💭 Thinking</summary>

**Appended optimization campaign catalog**

</details>

```json
{"search_query":[{"q":"site:aclanthology.org 2024 RAGAS Automated Evaluation of Retrieval Augmented Generation EACL system demonstrations"},{"q":"site:aclanthology.org 2024 ARES Automated Evaluation Framework Retrieval-Augmented Generation Systems NAACL"},{"q":"site:vldb.org DBSP Automatic Incremental View Maintenance for Rich Query Languages 2023"},{"q":"site:ieeexplore.ieee.org Malkov Yashunin HNSW 42 4 824 836"}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Searched 10 websites**

</details>

```unknown
bash -lc python - <<'PY'
from pathlib import Path
p=Path('/mnt/data/rag_functionality_work/v2/The_Semantics_and_Dynamics_of_RAG.md')
s=p.read_text()
print('code fences', s.count('```'), 'even', s.count('```')%2==0)
print('display math $$ count', s.count('$$'), 'even', s.count('$$')%2==0)
print('fig refs', s.count('](figures/'))
for name in sorted(Path('/mnt/data/rag_functionality_work/v2/figures').glob('*.png')):
    if f'figures/{name.name}' not in s:
        print('unused figure', name.name)
# detect tabs and control chars
bad=[]
for i,ch in enumerate(s):
    if ord(ch)<32 and ch not in '\n\t\r': bad.append((i,ord(ch)))
print('bad controls',len(bad))
PY
pandoc /mnt/data/rag_functionality_work/v2/The_Semantics_and_Dynamics_of_RAG.md --from=markdown+tex_math_dollars --to=native >/mnt/data/rag_functionality_work/v2/qa/pandoc_native.txt
printf 'pandoc_exit=%s\n' "$?"
wc -c /mnt/data/rag_functionality_work/v2/qa/pandoc_native.txt
```

<details><summary>💭 Thinking</summary>

**Validated Markdown and Pandoc output, patched bibliography entries, and located RAG files**

</details>

```unknown
bash -lc mkdir -p /mnt/data/rag_output /mnt/data/rag_functionality_work/v2/qa/docx_render
cp /mnt/data/rag_functionality_work/v2/The_Semantics_and_Dynamics_of_RAG.md /mnt/data/rag_output/The_Semantics_and_Dynamics_of_RAG.md
cd /mnt/data/rag_functionality_work/v2
pandoc The_Semantics_and_Dynamics_of_RAG.md \
  --from=markdown+tex_math_dollars \
  --to=docx \
  --toc --toc-depth=3 \
  --reference-doc=/mnt/data/rag_output/Compositional_Retrieval_Systems_Thesis.docx \
  --resource-path=/mnt/data/rag_functionality_work/v2 \
  --output=/mnt/data/rag_output/The_Semantics_and_Dynamics_of_RAG.docx
ls -lh /mnt/data/rag_output/The_Semantics_and_Dynamics_of_RAG.*
```

<details><summary>💭 Thinking</summary>

**Created, patched, and rendered RAG study DOCX with metadata inspection**

</details>

```unknown
bash -lc cat /home/oai/skills/docx/tasks/toc_workflow.md | sed -n '1,260p'; echo '--- insert_toc help ---'; python /home/oai/skills/docx/scripts/insert_toc.py --help | sed -n '1,200p'
```

<details><summary>💭 Thinking</summary>

**Inspecting remaining pages**

I’m continuing visual QA through the remaining rendered pages, checking tables, equations, figures, code blocks, headers, footers, and page boundaries before finalizing the deliverable files.

**Inspected remaining pages**

</details>

```unknown
bash -lc ls -lah /mnt/data/rag_functionality_work/v2/qa/contact_sheets_full | tail -n 30 && echo '---' && ls -lah /mnt/data/rag_output | tail -n 20
```

<details><summary>💭 Thinking</summary>

**Inspected DOCX TOC automation, rendered pages, and analyzed layout images**

</details>

```unknown
bash -lc grep -n -B 5 -A 8 -E 'migration.*roadmap|Dependency-ordered migration|figure_12|migration_roadmap|frontend replay laws' /mnt/data/rag_functionality_work/v2/The_Semantics_and_Dynamics_of_RAG.md | head -n 80
```

<details><summary>💭 Thinking</summary>

**Located Figure 12 source and analyzed image dimensions and content**

</details>

```unknown
bash -lc sed -n '1,220p' /mnt/data/rag_functionality_work/v2/qa/update_fields_uno.py && echo '---' && ls -lah /mnt/data/rag_functionality_work/v2/qa
```

<details><summary>💭 Thinking</summary>

**Finalized and validated the RAG manuscript DOCX, PDF, and source bundle**

</details>

# Volume II: *The Semantics and Dynamics of Retrieval-Augmented Systems*

The second thesis-style volume is complete. It contains **172 pages, approximately 42,000 words, 36 chapters, and nine appendices**.

### Publications

- [Download the PDF](sandbox:/mnt/data/rag_output/The_Semantics_and_Dynamics_of_RAG.pdf)
- [Download the editable DOCX](sandbox:/mnt/data/rag_output/The_Semantics_and_Dynamics_of_RAG.docx)
- [Download the Markdown source](sandbox:/mnt/data/rag_output/The_Semantics_and_Dynamics_of_RAG.md)
- [Download the complete source bundle](sandbox:/mnt/data/rag_output/The_Semantics_and_Dynamics_of_RAG_Source.zip)

The source bundle contains the manuscript, all thirteen figures in source/SVG/PNG forms, repository measurements, overlap analysis, the RAG parameter taxonomy, reproducibility scripts, retained study notes, checksums, and QA reports.

## Central correction

The semantic object is now the **evolving RAG service**, not an immutable artifact, a retrieval function, or an optimization campaign.

The base kernel developed in the first volume remains useful, but it is repositioned as infrastructure beneath a domain with its own time, state, concurrency, observation, and intervention semantics.

The volume develops three complementary meanings of RAG behavior:

1. **Denotational semantics** describe what behavior a complete RAG release denotes: a mapping from subject, conversation state, and request to distributions over ranked evidence, answers, abstentions, failures, cancellations, tool trajectories, and presentation events.
2. **Intensional trace semantics** preserve facts erased by final-answer equality: source and release lineage, authorization decisions, remote disclosure, freshness, fallback paths, tool iterations, latency, cost, partial results, and frontend delivery.
3. **Operational semantics** describe execution as small-step transitions over runtime configurations, including ingestion, derivation, indexing, verification, activation, retrieval, generation, validation, streaming, cancellation, retry, and projection.

This distinction prevents a candidate from being called semantics-preserving merely because it produces the same answer text while changing disclosure, freshness, evidence lineage, fallback frequency, latency behavior, or frontend state.

## Runtime model

Production RAG is formalized as four coupled state machines:

- An **index-maintenance machine** consumes revision streams and constructs verified releases.
- A **release-activation machine** stages, activates, drains, rolls back, and retires immutable releases.
- A **query and interaction machine** interprets direct search, retrieve-then-generate, and agentic retrieval.
- A **frontend projection machine** reconstructs customer-visible state from snapshots and ordered event suffixes.

Activation and release leases form the synchronization protocol between corpus maintenance and live querying. Every query, turn, evidence item, citation, structured fact, validator, and frontend projection belongs to one release epoch.

This produces a sharper production abstraction:

\[
\text{source world}
\rightarrow
\text{maintained release}
\rightarrow
\text{release-pinned interpretation}
\rightarrow
\text{replayable user projection}.
\]

## RAG retrieval optimization

Optimization is modeled as a **typed causal intervention over a dependency graph**, rather than a flat hyperparameter sweep.

The graph includes:

- source capture and admission;
- normalization and document identity;
- chunking and representation generation;
- embedding and lexical/vector index construction;
- query rewriting and routing;
- candidate generation, filtering, fusion, and reranking;
- context admission and evidence selection;
- answer, agent, and tool policy;
- deadlines, caching, concurrency, and fallback;
- structured data and presentation policy.

Every candidate declares:

- which nodes it changes;
- the resulting invalidation and rebuild closure;
- the observations that must be repeated;
- its claimed semantic class;
- the fidelity at which that claim can be tested;
- the invariants it must preserve.

The semantic classes distinguish operational, approximation, relevance, knowledge, policy/security, interaction, and presentation changes. They have different correctness relations and cannot legitimately be collapsed into one scalar objective.

For example:

- An exact-to-ANN change is evaluated relative to an exact retrieval oracle.
- A chunking change is a knowledge and relevance intervention requiring rebuild and answer-level evaluation.
- A timeout change is operational only when deadline-triggered outcomes remain invariant; otherwise it changes query semantics.
- An agent-policy change requires trajectory and session evaluation.
- A widget-projection change requires frontend convergence and product-outcome evaluation.

The volume supplies five detailed campaign designs:

1. GEC fusion, synonym, and reranking optimization.
2. Exact-to-ANN certification for RAG-TTC.
3. Joint chunking and representation design.
4. Refresh, overlay, compaction, and activation policy.
5. Garden agent and widget calibration.

Promotion is constraint-first and Pareto-aware across relevance, grounding, answer quality, security, freshness, reliability, latency, cost, capacity, and user outcomes. Ordered hard gates precede preference comparisons.

## Corpus evolution and indexing

The corpus is modeled as a **revision stream**, not a directory periodically rebuilt in place.

The source protocol includes:

- stable source keys;
- source-specific revisions;
- upserts and tombstones;
- duplicate and reordered delivery;
- cursors and barriers;
- snapshot tokens;
- event-time and observation-time watermarks;
- admission-policy decisions;
- connector capability declarations.

Indexing is then incremental view maintenance. The proposed initial production structure is:

\[
V_t = B_\tau \oplus \Delta_{\tau,t},
\]

where \(B_\tau\) is an immutable base release and \(\Delta_{\tau,t}\) is an ordered collection of additions, replacements, and tombstones. Compaction produces a new base without changing declared query behavior.

A clean full rebuild at the same source barrier is the correctness oracle:

\[
\operatorname{maintain}(B,\Delta)
\;\simeq\;
\operatorname{rebuild}(S \oplus \Delta).
\]

The equivalence is exact for deterministic backends and tolerance-relative for approximate indexes.

The reliability model explicitly rejects exactly-once execution as a general assumption. Instead it relies on:

- at-least-once source delivery;
- semantic idempotence;
- canonical derivation keys;
- durable build events and checkpoints;
- retryable and quarantinable stages;
- immutable publication;
- exactly-once activation effect through compare-and-swap.

## Behavior-complete production releases

An index directory is insufficient as a release identity. A behavior-complete release binds every input capable of changing observable RAG behavior, including:

- source barrier and normalized corpus;
- chunk and representation specifications;
- lexical and vector indexes;
- query rewrite, routing, fusion, and filtering policy;
- synonyms and reranking assets;
- structured fact snapshots;
- prompts, tool descriptions, and answer contracts;
- provider identities and disclosure policy;
- validators and evidence policy;
- agent iteration policy;
- server-owned presentation policy.

Activation changes a routing key from one immutable release to another with compare-and-swap semantics. In-flight operations retain leases on the old release until their required terminal persistence and projection work completes.

This supplies native semantics for hot activation, canaries, rollback, draining, retirement, and mixed-release prevention.

## Query and frontend semantics

The shared design no longer collapses three materially different operations into “query”:

- **Direct interpreter:** terminates with ranked evidence and a trace.
- **Retrieve-then-generate interpreter:** executes one bounded retrieval plan, constructs context, generates, validates, and emits an answer.
- **Agent interpreter:** executes a bounded transition system with zero or more model-selected tool calls, an evidence session, and a final validated projection.

The frontend is part of the RAG semantic boundary whenever citations, evidence, choices, product facts, or widgets affect the user-visible result.

The proposed stream protocol uses:

- stable event IDs;
- stream ordinals;
- release IDs;
- entity identities and versions;
- replace, merge, append, and tombstone operations;
- exact append offsets;
- snapshot watermarks;
- deduplication and stale-update rejection;
- explicit resynchronization.

Its principal law is snapshot-plus-suffix equivalence:

\[
\operatorname{reduce}(S_n,e_{n+1},\ldots,e_m)
=
\operatorname{reduce}(e_1,\ldots,e_m).
\]

Duplicate append patches and lower-version entity updates are semantic violations rather than incidental UI bugs.

## Package architecture

The target package structure is grounded in the runtime domain:

- `ragkit/corpus` — revisions, changes, cursors, barriers, snapshots, and watermarks.
- `ragkit/derive` — dependency graphs, derivation keys, impact plans, and incremental-maintenance laws.
- `ragkit/index` — logical index views, backend capabilities, exact and approximate relations, overlays, and compaction.
- `ragkit/build` — RAG-specific durable build coordination, introduced only after shared lifecycle semantics are demonstrated.
- `ragkit/release` — behavior-complete manifests, registry, activation, leases, draining, rollback, and retirement.
- `ragkit/query` — typed retrieval plans and direct-search interpretation.
- `ragkit/answer` — context construction, generation, grounding validation, and answer outcomes.
- `ragkit/agent` — bounded agent execution and release-scoped tool integration.
- `ragkit/evidence` — evidence sessions, lineage, admission, citation labels, and disclosure certificates.
- `ragkit/stream` — versioned frontend events and replay laws.
- `ragkit/trace` — operational observations and trace equivalence.
- `ragkit/eval` — common RAG measurement schemas and paired artifacts.
- `ragopt/ragspace` — typed RAG intervention spaces, dependency closure, fidelities, and gates.

`ragopt` remains domain-neutral at its core. Its RAG adapter imports `ragkit` types rather than reimplementing RAG meaning.

## Applied migration findings

### GEC

The most urgent issue is the trust-boundary ordering. Current retrieval can hydrate candidates and send them to an optional remote reranker before final source-scope filtering. Material later removed from results may therefore cross the provider boundary.

The migration requires authorization before hydration or remote disclosure, behavior-complete release identity for synonyms and reranking, a release manager with leases, and stronger frontend event laws.

### RAG-TTC

RAG-TTC provides the strongest applied environment for complete-corpus builds, committed source snapshots, ANN certification, connected retrieval, model-invoked search, persistent turns, and evidence ledgers.

Its copied common retrieval substrate should be removed through fixture-backed differential cutover to `ragkit`. Product catalogs, route semantics, connected retrieval, provider behavior, agent composition, and evaluation remain product-owned.

### Garden

Garden demonstrates why RAG semantics extend beyond ranked text. Its result includes intent decisions, product facts, choices, evidence-bound widgets, conflicts, and multi-turn calibration.

The migration replaces copied infrastructure while retaining those domain semantics. Conversations use explicit release epochs, and grounded widget fields retain evidence and release provenance through frontend projection.

## Formal and verification material

The appendices contain:

- structural operational semantics for build, activation, query, agent, and frontend machines;
- semantic laws and proof obligations;
- an extended Go API blueprint;
- state and transition tables;
- a detailed optimization campaign catalog;
- property, fuzz, differential, fault-injection, load, and state-machine test plans;
- TLA+ model targets;
- machine-checkable proof candidates;
- empirical source maps and current-to-target package mappings;
- a bibliography and operational RAG glossary.

The final DOCX passed its accessibility audit with no high-, medium-, or low-severity findings. The DOCX and PDF were rendered to 172 page images and inspected; the PDF also passed structural preflight. No repository code was modified. The supplied snapshot could not be compiled end-to-end because it references an absent GEC build package and requires a newer Go toolchain than was available offline, so deployment and provider claims are explicitly separated from static source findings.


---

> let's take chapter 21 and focus on working on the underlying abstract mathematical (prob category theory) backbone that would allow creating a composable architecture for the optimization field. write a whole thesis + sandbox self-contained implementation about it.

I’ll reconstruct Chapter 21’s optimization assumptions as a compositional probabilistic categorical core, then build a self-contained executable kernel with laws, tests, examples, and rendered thesis artifacts.

```unknown
bash -lc ls -lah /mnt/data/rag_output && echo '---PDF SKILL---' && sed -n '1,240p' /home/oai/skills/pdfs/SKILL.md && echo '---DOCX SKILL---' && sed -n '1,260p' /home/oai/skills/docx/SKILL.md
```

<details><summary>💭 Thinking</summary>

**Planning mathematical backbone**

I’m inspecting the existing chapter and implementation context so I can avoid duplication. I’ll connect composable optimization to category-theoretic structure, then design a self-contained sandbox that makes the abstractions executable and testable.

**Planned the mathematical backbone**

**Structuring the framework**

I’m organizing the thesis around one coherent hierarchy: typed measurable spaces, stochastic kernels, composable runtime components, indexed specifications, refinement relations, and semantics-preserving interventions.

**Structured the framework**

**Choosing formal components**

I’m combining indexed categories for architecture changes, stochastic kernels for evaluation, ordered objective spaces for optimization, and polynomial representations for typed candidate spaces, while avoiding unnecessary categorical machinery.

**Chose formal components**

**Inspected Chapters 20–24 and located Chapter 21 headings**

</details>

```unknown
bash -lc command -v go || true; go version || true; command -v lean || true; command -v lake || true; command -v tlc || true; command -v java || true; command -v pandoc || true; command -v quarto || true; command -v typst || true; command -v pdflatex || true; command -v xelatex || true; command -v libreoffice || true; python --version
```

<details><summary>💭 Thinking</summary>

**Inspected repository, archives, build scripts, and RAGOpt implementation sources**

</details>

```json
{"search_query":[{"q":"site:arxiv.org Markov categories Fritz stochastic kernels category theory"},{"q":"site:arxiv.org Para construction parameterized morphisms category theory machine learning optics learners"},{"q":"site:arxiv.org change actions incremental computation category theory"},{"q":"site:arxiv.org compositional game theory open games optimization selection functions"}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Searched 1 website**

</details>

```unknown
bash -lc grep -n '^# Bibliography\|^# References\|^## Bibliography\|^# Appendix' /mnt/data/rag_output/The_Semantics_and_Dynamics_of_RAG.md | tail -30 && tail -380 /mnt/data/rag_output/The_Semantics_and_Dynamics_of_RAG.md
```

<details><summary>💭 Thinking</summary>

**Used container tool**

</details>

```json
{"open":[{"ref_id":"turn290238search0"},{"ref_id":"turn253512search1"},{"ref_id":"turn774236search0"},{"ref_id":"turn290238search10"},{"ref_id":"turn774236search31"},{"ref_id":"turn253512search16"},{"ref_id":"turn253512search3"},{"ref_id":"turn253512search13"}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Defining the thesis**

I’m shaping the work around a compositional mathematics of RAG optimization: parameterized stochastic systems, typed interventions, experiments, promotion decisions, and a fibred optimization field, with a finite sandbox implementation.

**Defined the thesis**

</details>

The formal backbone is sharpening around stochastic transducers, intervention optics, rebuild-change propagation, and ordered promotion algebras, with emphasis on making these structures executable rather than merely descriptive.

<details><summary>💭 Thinking</summary>

**Searched 1 website**

</details>

```unknown
bash -lc command -v dot || true; dot -V || true; command -v plantuml || true
```

<details><summary>💭 Thinking</summary>

**Implementing the sandbox**

I’m building a standard-library Go sandbox with finite distributions, lenses, change actions, dependency closure, experiments, metrics, gates, and campaign control. I’m preserving existing candidate, evaluation, and audit concepts while adding typed field semantics.

**Implemented the sandbox**

</details>

The kernel now uses exact finite rational probabilities, making categorical, lens, coupling, and closure laws equality-testable. Most packages compile; one generic law-test typing defect remains.

```unknown
bash -lc find /mnt/data/optfield_work/optfield-sandbox -maxdepth 3 -type f | sort | sed -n '1,240p'
```

<details><summary>💭 Thinking</summary>

**Implemented and tested optimization, RAG evaluation, and promotion tooling**

</details>

```unknown
bash -lc sed -i 's/got != "d"/got != "c"/' /mnt/data/optfield_work/optfield-sandbox/pkg/field/field_test.go
for f in /mnt/data/optfield_work/optfield-sandbox/pkg/ragtoy/*.go; do echo '###'$(basename "$f"); sed -n '1,320p' "$f"; done
```

<details><summary>💭 Thinking</summary>

**Inspected repository and implemented, formatted, and tested the RAG evaluation pipeline**

</details>

```unknown
bash -lc cd /mnt/data/optfield_work/optfield-sandbox && rm -rf demo-output && time go run ./cmd/optfield-demo -out demo-output > /tmp/optfield_demo_summary.txt && cat /tmp/optfield_demo_summary.txt && echo '--- pareto'; sed -n '1,30p' demo-output/pareto.csv && echo '--- finalists'; sed -n '1,25p' demo-output/finalists.csv
```

<details><summary>💭 Thinking</summary>

**Ran campaign reviews, inspected chapters and APIs, and implemented law checks**

</details>

```json
{"open":[{"ref_id":"turn573476view0"},{"ref_id":"turn573476view7"},{"ref_id":"turn573476view1"},{"ref_id":"turn573476view2"},{"ref_id":"turn573476view3"},{"ref_id":"turn573476view4"},{"ref_id":"turn573476view6"},{"ref_id":"turn573476view5"}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Searched 1 website**

</details>

```unknown
bash -lc for f in \
/mnt/data/optfield_work/repo/ragopt/pkg/candidate/*.go \
/mnt/data/optfield_work/repo/ragopt/pkg/eval/types.go \
/mnt/data/optfield_work/repo/ragopt/pkg/eval/runner.go \
/mnt/data/optfield_work/repo/ragopt/pkg/gate/*.go \
/mnt/data/optfield_work/repo/ragopt/pkg/compare/*.go \
/mnt/data/optfield_work/repo/ragopt/pkg/runstore/*.go; do echo '###' $f; grep -nE '^type |^func |one mutation|Pair|Gate|Candidate|Snapshot|Run' "$f" | head -80; done
```

<details><summary>💭 Thinking</summary>

**Inspected RAGOPT architecture, verified framework environment, and wrote README figures**

</details>

```unknown
bash -lc mkdir -p /mnt/data/optfield_work/thesis/figures /mnt/data/optfield_work/thesis/sources /mnt/data/optfield_work/thesis/qa
cat > /mnt/data/optfield_work/thesis/figures/01_backbone.dot <<'EOF'
digraph G {
  graph [rankdir=TB, bgcolor="white", pad=.25, nodesep=.30, ranksep=.42, fontname="DejaVu Sans", labelloc=t, label="Compositional backbone of an optimization field"];
  node [shape=box, style="rounded", fontname="DejaVu Sans", fontsize=10, margin="0.12,0.07"];
  edge [fontname="DejaVu Sans", fontsize=9];
  A [label="Open stochastic RAG systems\nMarkov kernels + state"];
  B [label="Parameterized composition\nPara(C) and wiring diagrams"];
  C [label="Local intervention\noptics / lenses"];
  D [label="Dynamic change\nchange actions + derivatives"];
  E [label="Optimization field\nindexed graded intervention categories"];
  F [label="Statistical experiment\npairing + fidelity order"];
  G [label="Decision doctrine\nconstraints + non-inferiority + Pareto"];
  H [label="Campaign dynamics\ncontroller + trusted event reducer"];
  A -> B -> C -> D -> E -> F -> G -> H;
}
EOF

cat > /mnt/data/optfield_work/thesis/figures/02_para_system.dot <<'EOF'
digraph G {
  graph [rankdir=LR, bgcolor="white", pad=.25, nodesep=.45, ranksep=.5, fontname="DejaVu Sans", labelloc=t, label="A parameterized stochastic transducer and its composition"];
  node [shape=box, style="rounded", fontname="DejaVu Sans", fontsize=10];
  edge [fontname="DejaVu Sans", fontsize=9];
  X [shape=oval,label="input X"];
  P [shape=oval,label="parameter P"];
  F [label="component f\nP ⊗ X → K(S ⊗ Y)"];
  Y [shape=oval,label="output Y"];
  S [shape=oval,label="next state S"];
  Q [shape=oval,label="parameter Q"];
  G2 [label="component g\nQ ⊗ Y → K(T ⊗ Z)"];
  Z [shape=oval,label="output Z"];
  T [shape=oval,label="next state T"];
  X -> F; P -> F; F -> Y; F -> S; Y -> G2; Q -> G2; G2 -> Z; G2 -> T;
  subgraph cluster_comp { label="composite parameter P ⊗ Q"; style=dashed; P; Q; }
}
EOF

cat > /mnt/data/optfield_work/thesis/figures/03_intervention.dot <<'EOF'
digraph G {
  graph [rankdir=LR, bgcolor="white", pad=.25, nodesep=.35, ranksep=.45, fontname="DejaVu Sans", labelloc=t, label="Local intervention, semantic effect, and incremental closure"];
  node [shape=box, style="rounded", fontname="DejaVu Sans", fontsize=10];
  edge [fontname="DejaVu Sans", fontsize=9];
  theta [label="baseline specification θ"];
  lens [label="lawful focus ℓ\nwhole ↔ local parameter"];
  delta [label="atomic change δ"];
  theta2 [label="candidate θ ⊕ ℓ(δ)"];
  grade [label="effect grade g(δ)"];
  closure [label="impact closure Dθ(δ)"];
  evidence [label="required evidence Req(g(δ))"];
  theta -> lens -> theta2;
  delta -> lens;
  delta -> grade -> evidence;
  delta -> closure;
}
EOF

cat > /mnt/data/optfield_work/thesis/figures/04_fibration.dot <<'EOF'
digraph G {
  graph [rankdir=TB, bgcolor="white", pad=.25, nodesep=.35, ranksep=.55, fontname="DejaVu Sans", labelloc=t, label="The optimization field as indexed intervention categories"];
  node [shape=box, style="rounded", fontname="DejaVu Sans", fontsize=10];
  edge [fontname="DejaVu Sans", fontsize=9];
  subgraph cluster_f1 { label="Fiber Opt(A): architecture A"; style=dashed; A0[label="θ₀"]; A1[label="θ₁"]; A2[label="θ₂"]; A0->A1[label="i"]; A1->A2[label="j"]; A0->A2[label="j∘i",style=dotted]; }
  subgraph cluster_f2 { label="Fiber Opt(B): architecture B"; style=dashed; B0[label="φ₀"]; B1[label="φ₁"]; B0->B1[label="k"]; }
  ArchA [shape=oval,label="A"];
  ArchB [shape=oval,label="B"];
  ArchA -> ArchB [label="architecture map u"];
  B0 -> A0 [label="reindex u*",style=dashed];
  B1 -> A1 [label="reindex u*",style=dashed];
  A0 -> ArchA [arrowhead=none,style=dotted]; A2 -> ArchA [arrowhead=none,style=dotted];
  B0 -> ArchB [arrowhead=none,style=dotted]; B1 -> ArchB [arrowhead=none,style=dotted];
}
EOF

cat > /mnt/data/optfield_work/thesis/figures/05_effects.dot <<'EOF'
digraph G {
  graph [rankdir=LR, bgcolor="white", pad=.25, nodesep=.25, ranksep=.45, fontname="DejaVu Sans", labelloc=t, label="Effect grading is conservative and evidence-monotone"];
  node [shape=box, style="rounded", fontname="DejaVu Sans", fontsize=9];
  edge [fontname="DejaVu Sans", fontsize=8];
  op[label="operational"];
  ap[label="approximation"];
  rel[label="relevance"];
  know[label="knowledge"];
  sec[label="policy / security"];
  int[label="interaction"];
  pres[label="presentation"];
  join[label="join under composition\ng(i;j)=g(i)∨g(j)"];
  req[label="monotone Req"];
  ev[label="law, build, oracle, retrieval,\nanswer, temporal, load, security,\nsession, frontend evidence"];
  {op ap rel know sec int pres} -> join -> req -> ev;
}
EOF

cat > /mnt/data/optfield_work/thesis/figures/06_experiment.dot <<'EOF'
digraph G {
  graph [rankdir=LR, bgcolor="white", pad=.25, nodesep=.35, ranksep=.5, fontname="DejaVu Sans", labelloc=t, label="Paired experiments and multi-fidelity evidence"];
  node [shape=box, style="rounded", fontname="DejaVu Sans", fontsize=10];
  edge [fontname="DejaVu Sans", fontsize=9];
  z [shape=oval,label="case × repeat × seed z"];
  copy [label="copy deterministic context Δ"];
  base [label="baseline channel Eθ₀"];
  cand [label="candidate channel Eθ₁"];
  pair [label="paired contrast\nobservation and delta"];
  high [label="high-fidelity experiment H"];
  garble [label="garbling / projection G"];
  low [label="low fidelity L = H ; G"];
  z -> copy; copy -> base; copy -> cand; base -> pair; cand -> pair;
  high -> garble -> low;
}
EOF

cat > /mnt/data/optfield_work/thesis/figures/07_campaign.dot <<'EOF'
digraph G {
  graph [rankdir=LR, bgcolor="white", pad=.25, nodesep=.28, ranksep=.45, fontname="DejaVu Sans", labelloc=t, label="Small-step operational semantics of a candidate campaign"];
  node [shape=ellipse, fontname="DejaVu Sans", fontsize=9];
  edge [fontname="DejaVu Sans", fontsize=8];
  absent -> proposed [label="propose"];
  proposed -> built [label="build, when required"];
  proposed -> evaluating [label="start, query-only"];
  built -> evaluating [label="start"];
  evaluating -> evaluated [label="complete(fidelity)"];
  evaluated -> evaluating [label="next fidelity"];
  evaluated -> decided [label="gate"];
  decided -> promoted [label="pass"];
  decided -> rejected [label="fail / stop"];
  proposed -> rejected [label="budget stop",style=dashed];
}
EOF

cat > /mnt/data/optfield_work/thesis/figures/08_packages.dot <<'EOF'
digraph G {
  graph [rankdir=TB, bgcolor="white", pad=.25, nodesep=.28, ranksep=.42, fontname="DejaVu Sans", labelloc=t, label="Target package architecture and dependency direction"];
  node [shape=box, style="rounded", fontname="DejaVu Sans", fontsize=9];
  edge [fontname="DejaVu Sans", fontsize=8];
  apps[label="GEC / RAG-TTC / Garden\nproduct objectives and native traces"];
  adapter[label="ragopt/ragspace\ntyped interventions, supports, fidelities"];
  ragkit[label="ragkit\nbehavior-complete RAG semantics"];
  ragopt[label="ragopt core\ncandidate custody, pairing, gates, campaign"];
  kernel[label="evidence / identity kernel\ncanonical data, reducers, laws"];
  infra[label="job runner / storage / providers\noperational adapters"];
  apps -> adapter; apps -> ragkit; adapter -> ragkit; adapter -> ragopt; ragkit -> kernel; ragopt -> kernel; ragkit -> infra; ragopt -> infra;
}
EOF

cat > /mnt/data/optfield_work/thesis/figures/10_reuse.dot <<'EOF'
digraph G {
  graph [rankdir=LR, bgcolor="white", pad=.25, nodesep=.35, ranksep=.45, fontname="DejaVu Sans", labelloc=t, label="Support-disjoint reuse is stronger than content-addressing alone"];
  node [shape=box, style="rounded", fontname="DejaVu Sans", fontsize=10];
  impact[label="impact closure I(δ)"];
  support[label="artifact/evaluator support S"];
  ids[label="barrier, suite, seed, policy, fidelity"];
  disjoint[label="I(δ) ∩ S = ∅"];
  same[label="external identities equal"];
  reuse[label="reuse certificate"];
  deny[label="recompute or reevaluate"];
  impact -> disjoint; support -> disjoint; ids -> same; disjoint -> reuse [label="true"]; same -> reuse [label="true"]; disjoint -> deny [label="false",style=dashed]; same -> deny [label="false",style=dashed];
}
EOF

cat > /mnt/data/optfield_work/thesis/figures/13_migration.dot <<'EOF'
digraph G {
  graph [rankdir=LR, bgcolor="white", pad=.25, nodesep=.3, ranksep=.45, fontname="DejaVu Sans", labelloc=t, label="Incremental migration from the current packages"];
  node [shape=box, style="rounded", fontname="DejaVu Sans", fontsize=9];
  edge [fontname="DejaVu Sans", fontsize=8];
  c1[label="ragopt candidate/v1\nstrict immutable one-mutation snapshot"];
  c2[label="atomic intervention descriptor\ntarget, grade, support, hypothesis"];
  c3[label="verified intervention path\nadjacent snapshots + path identity"];
  e1[label="exact paired eval and missing cells"];
  e2[label="fidelity + experiment identity\nsource barrier, seed design, support"];
  g1[label="ordered gates and report"];
  g2[label="interval non-inferiority\nfeasible Pareto report"];
  r1[label="ragkit RAG components"];
  r2[label="behavior-complete spec + dependency graph"];
  c1->c2->c3; e1->e2; g1->g2; r1->r2; r2->c2; r2->e2;
}
EOF

for f in /mnt/data/optfield_work/thesis/figures/*.dot; do base=${f%.dot}; dot -Tsvg "$f" -o "$base.svg"; dot -Tpng -Gdpi=180 "$f" -o "$base.png"; done
cp /mnt/data/optfield_work/optfield-sandbox/demo-output/dependencies.dot /mnt/data/optfield_work/thesis/figures/09_toy_rag_dependency.dot
cp /mnt/data/optfield_work/optfield-sandbox/demo-output/dependencies.svg /mnt/data/optfield_work/thesis/figures/09_toy_rag_dependency.svg
cp /mnt/data/optfield_work/optfield-sandbox/demo-output/dependencies.png /mnt/data/optfield_work/thesis/figures/09_toy_rag_dependency.png
ls -lh /mnt/data/optfield_work/thesis/figures | sed -n '1,160p'
```

<details><summary>💭 Thinking</summary>

**Created thesis optimization framework figures and computed repository metrics**

</details>

```unknown
bash -lc cat > /mnt/data/optfield_work/thesis/The_Algebra_of_Intervention_Fields.md <<'EOF'
---
title: "The Algebra of Intervention Fields"
subtitle: "Compositional Denotational, Operational, and Statistical Semantics for RAG Optimization"
author: "RAG-MATHS Architecture Study"
date: "August 2026"
lang: en-US
rights: "Architecture study and executable reference model"
abstract: |
  Retrieval-augmented generation optimization is usually represented as a flat search over configuration values. That representation is inadequate for a production RAG system. A candidate can alter source admission, chunk identity, derived representations, index bytes, approximate search error, query interpretation, remote disclosure, context construction, agent trajectories, latency behavior, and frontend state. Its cost and meaning depend on where it acts, which downstream artifacts it invalidates, which observations it is expected to preserve, and which evidence must be collected before promotion.

  This thesis develops an abstract mathematical backbone for a composable optimization architecture. The central construction is an **optimization field**: an indexed family of categories whose objects are behavior-complete system specifications and whose morphisms are typed interventions. The fibers are graded by semantic effect, equipped with local optics, change actions, dependency derivatives, statistical experiment functors, and constraint-first decision relations. Open RAG behavior is interpreted as a parameterized stateful morphism in a Markov category; runtime campaigns are given a small-step event semantics and a denotational fold. Multi-fidelity evaluation is analyzed through comparison of statistical experiments, and artifact reuse is justified by a support-disjointness theorem rather than content identity alone.

  A self-contained standard-library Go implementation accompanies the thesis. It provides finite Markov kernels, lawful lenses, change actions, dependency closure, typed intervention spaces, paired experiments, a finite Blackwell witness, mergeable statistics, interval-aware gates, Pareto fronts, an event-sourced campaign reducer, finite state-space exploration, a TLA+ model target, and a hybrid lexical/vector RAG optimizer. The executable campaign evaluates 575 candidate specifications at low fidelity, advances 56 and then 14, identifies six passing Pareto points, and promotes one candidate through an auditable reducer. The implementation is an executable model of the theory, not a claim that finite tests prove all production properties.
---

\newpage

# Preface

This volume expands the optimization-field proposal introduced in Chapter 21 of *The Semantics and Dynamics of Retrieval-Augmented Systems*. The earlier chapter made three practical claims: a RAG candidate is a controlled intervention rather than an arbitrary configuration; its dependency closure determines rebuild and reuse; and promotion is a constrained, multi-objective judgment rather than maximization of one score. Those claims were architecturally useful but mathematically underdeveloped. They did not yet explain what kind of object an intervention is, how interventions compose, how a local change acts on a whole release, what it means for behavior to be preserved, how runtime observations relate to denotation, or how a generic optimizer can remain ignorant of RAG internals while still validating RAG-specific work.

The present thesis supplies that backbone. It is deliberately positioned between pure category theory and production systems engineering. It uses category-theoretic structures because they expose interfaces and laws that ordinary configuration schemas hide. It uses operational semantics because an optimizer is a stateful runtime system with retries, partial evidence, cancellations, and promotion authority. It uses statistical decision theory because the behavior of a RAG release is stochastic and finite evidence cannot justify exact equality. It uses incremental computation because changes to indexing and querying induce structured rebuild and reevaluation work. None of these perspectives is sufficient alone.

The result is not a universal theorem that every possible RAG optimizer must instantiate exactly. It is a proposed semantic architecture with explicit assumptions. Definitions and propositions are separated from engineering conventions. Proof sketches state the conditions on which they depend. Executable checks validate finite instances of laws; they do not replace general proof. Product security, user impact, and provider behavior remain product-specific obligations.

# Principal contributions

The thesis makes nine connected contributions.

1. It defines a production RAG release as an **open, stateful, stochastic, parameterized system** rather than a static retrieval function.
2. It defines a candidate as a **morphism out of a baseline**. Candidate identity therefore includes causal path and declared intervention, not only endpoint bytes.
3. It uses **optics and lawful lenses** to represent local parameter focus and reconstruction of behavior-complete specifications.
4. It uses **change actions and derivatives** to give semantic meaning to invalidation, incremental rebuild, cache reuse, and experiment reuse.
5. It defines an **optimization field** as an indexed or fibred family of intervention categories over system architectures.
6. It grades interventions by a join-semilattice of semantic effects and derives evidence obligations through a monotone map.
7. It interprets evaluation as a **statistical experiment**, exact pairing as copying deterministic experimental context, and nested fidelity as a Blackwell garbling relation when such a witness exists.
8. It separates search allocation from promotion, using hard constraints, interval-valued non-inferiority, and Pareto order instead of a promotion scalar.
9. It supplies a self-contained implementation and migration path for the existing `ragkit` and `ragopt` packages.

![The mathematical backbone proceeds from open stochastic behavior to a validated campaign controller.](figures/01_backbone.png){width=76%}

# How to read this volume

Readers primarily concerned with architecture can begin with Chapters 1, 5, 15, 25, 28, and 31. Readers concerned with formal semantics should read Parts II and III in order. Readers implementing `ragopt` can begin with Chapters 22 through 30 and the API appendices. The sandbox is described in Part VI; its source tree is included beside the manuscript.

Notation is introduced locally and summarized in Appendix A. The base category of stochastic maps is written $\mathcal{K}$; an architecture is $A$; its specification space is $\Theta_A$; a baseline is $\theta_0$; and an intervention is $i : \theta_0 \to \theta_1$. Composition is written $j \circ i$, with $i$ performed first. The semantic effect grade of $i$ is $g(i)$. Its changed support is $\operatorname{supp}(i)$ and its downstream impact closure is $\operatorname{cl}_A(\operatorname{supp}(i))$.

# Part I. The optimization problem reconstructed

# 1. Why a flat search space is the wrong object

## 1.1 The conventional representation

A conventional optimizer begins with a product space:

$$
\Theta = \Theta_{\text{chunk}} \times \Theta_{\text{embed}} \times
\Theta_{\text{index}} \times \Theta_{\text{query}} \times
\Theta_{\text{rank}} \times \Theta_{\text{answer}}.
$$

A trial samples $\theta \in \Theta$, builds whatever is necessary, evaluates a scalar objective $J(\theta)$, and updates a search policy. This representation is useful for an isolated model whose parameters have uniform status. It is misleading for a production RAG service.

The coordinates do not have uniform semantics. Changing worker count may preserve all successful outcomes until a deadline is crossed. Changing HNSW search breadth changes an approximation relation to an exact oracle. Changing chunk boundaries changes evidence identity and may change what facts are representable. Changing authorization order changes disclosure even if final answer text is unchanged. Changing a widget projection changes user-visible state without changing retrieval. Treating all of these as values in one untyped product erases the reasons they require different evidence.

The coordinates also do not have uniform operational cost. A fusion weight can often reuse channel rankings. A reranker pool change can reuse a retained fused prefix. A chunker change invalidates chunks, derived representations, embeddings, index bytes, query traces, contexts, and answer observations. A provider timeout may invalidate only runtime measurements unless it changes fallback frequency. The optimizer must know the *support* of a change and the transitive dependency relation, not just the before and after JSON documents.

Finally, endpoint equality is insufficient. Suppose two paths reach the same final release:

$$
\theta_0 \xrightarrow{i} \theta_a \xrightarrow{j} \theta_1,
\qquad
\theta_0 \xrightarrow{k} \theta_b \xrightarrow{\ell} \theta_1.
$$

The endpoint bytes may agree while the causal hypotheses, intermediate evidence, reused artifacts, and audit records differ. A system intended to learn from interventions must retain the arrow, not only its codomain.

## 1.2 The field metaphor

The word *field* is used in a structural, not physical, sense. Over every system architecture lies a family of valid specifications, interventions, observations, and decisions. Moving to a different architecture changes which parameters exist and how evidence can be transported. Within one architecture, local changes compose. Across architectures, restriction or translation maps carry a specification and its support into another context.

This suggests an indexed construction:

$$
\operatorname{Opt} : \mathcal{A}^{op} \longrightarrow \mathbf{Cat},
$$

where $\mathcal{A}$ is a category of architectures and $\operatorname{Opt}(A)$ is the intervention category for architecture $A$. The associated Grothendieck construction collects all fibers into one total category while retaining the projection to architecture. The term *optimization field* refers to this indexed family together with its behavioral semantics, change calculus, experiment doctrine, and decision doctrine.

## 1.3 Requirements for the replacement

A replacement for a flat search space must support all of the following without making the generic optimizer a RAG framework:

- local, typed, law-governed changes;
- sequential composition and certified parallel composition;
- behavior-complete release identity;
- stochastic and stateful runtime interpretation;
- explicit observational equivalence and approximation budgets;
- dependency-aware rebuild and cache reuse;
- effect-sensitive evidence requirements;
- paired, resumable, multi-fidelity experiments;
- hard constraints and partial-order promotion;
- event-sourced operational custody;
- reindexing across architectures and product adapters.

The rest of the thesis constructs these capabilities from smaller mathematical structures.

# 2. The empirical anchor: current `ragopt` and `ragkit`

## 2.1 What already exists

The supplied snapshot contains two valuable but differently scoped packages. `ragkit` has 173 Go files, approximately 17,743 nonblank lines, and 273 test functions across retrieval, chunking, representations, embedding, lexical and exact vector search, reranking, context construction, generation, evaluation, index bundles, execution utilities, flows, and content identity. `ragopt` has 45 Go files, approximately 5,925 nonblank lines, and 42 test functions across candidates, evaluation, comparison, gates, reports, run storage, and command-line adapters. These are static source measurements of the supplied snapshot, not statements about deployment.

`ragopt` already implements several parts of the trusted core that this thesis requires:

- strict, content-identified snapshots;
- a candidate manifest that validates exactly one declared mutation;
- copied and verified assets;
- exact baseline/candidate pairing by case and repeat;
- explicit retention of missing pairs and missing metrics;
- ordered gates and promotion reports;
- durable run directories, append-only records, completion/failure state, and resume checks.

These are not incidental utilities. They are the beginnings of a semantic kernel: identity, custody, pairing, and authorization to promote.

`ragkit` already implements much of the behavioral vocabulary over which an optimization field must range. It has distinct chunking, representation, embedding, index, retrieval, reranking, answering, generation, and evaluation packages. It also contains deterministic ordering and evidence identity rules. The missing piece is not another generic candidate runner. It is a typed account of how changes to these RAG meanings become interventions with closure, preservation claims, and evidence obligations.

## 2.2 The boundary problem

The generic optimizer should not import every RAG concept. If `ragopt` owns chunk specifications, HNSW parameters, grounding contracts, tool trajectories, and frontend widgets, it becomes a second RAG framework and immediately diverges from `ragkit`. Conversely, a generic optimizer that sees only opaque configuration blobs cannot validate rebuild closure or reuse.

The proposed boundary is an adapter. `ragopt` owns generic intervention custody, statistical experiment execution, decision protocols, and campaign state. A `ragopt/ragspace` package imports stable RAG semantic types from `ragkit` and supplies:

- typed parameter references;
- effect grades;
- dependency graphs and supports;
- observation families;
- fidelity definitions;
- product-neutral RAG evidence obligations.

Applications supply native objectives, suites, traces, and product gates. This direction preserves dependency hygiene:

$$
\text{application} \to \text{ragspace} \to (\text{ragkit},\text{ragopt}),
$$

not `ragopt` $\to$ product code.

## 2.3 Exactly one mutation as a generator

The current `ragopt` one-mutation invariant is useful and should not be discarded. It should be reinterpreted. An atomic candidate is a generator in an intervention category. A compound candidate is a verified path of generators:

$$
i_n \circ \cdots \circ i_2 \circ i_1.
$$

Each adjacent snapshot identity must agree, and the path identity must be preserved even when two paths produce the same endpoint. This permits factorial or coordinated experiments without returning to opaque multi-change files. It also means the existing candidate format can remain stable while a versioned path manifest is added above it.

# 3. The semantic object: an evolving RAG service

## 3.1 Beyond retrieval as a pure function

A minimal retrieval function has type

$$
q : Q \longrightarrow \operatorname{List}(E).
$$

A production RAG service has source state, release state, caches, provider state, conversation state, time, deadlines, random choices, and streaming output. A more faithful one-step type is

$$
T_\theta : S \otimes X \longrightarrow \mathcal{D}(S \otimes Y \otimes \Tau),
$$

where $S$ is runtime state, $X$ is an input event, $Y$ is an external outcome, $\Tau$ is an intensional trace, and $\mathcal{D}$ is a probability construction. The parameter $\theta$ is behavior-complete: it binds the source barrier, derived artifacts, query policy, provider identities, validators, operational policy, and projection policy capable of changing observable behavior.

The trace is not debugging exhaust. It carries facts needed to distinguish releases that return the same answer text: evidence lineage, disclosure, fallback path, release lease, latency, cost, tool actions, partial delivery, and cancellation. Optimization can project this trace differently for different claims.

## 3.2 Time and state

Index optimization and query optimization meet at release activation. Source revisions are transformed into immutable releases; queries acquire a lease on one active release; experiments compare release-pinned interpretations. The semantic state therefore contains at least:

$$
S = S_{\text{source}} \times S_{\text{build}} \times S_{\text{release}}
\times S_{\text{query}} \times S_{\text{campaign}}.
$$

The optimizer is not outside this runtime. It observes traces, allocates experiments, creates builds, and proposes promotions. Its own state and transition laws must be modeled. A promotion decision made from incomplete pairing is a runtime safety error even if the comparison code is numerically correct.

## 3.3 Open-system interfaces

RAG components are open systems: a retriever receives a query and index interface; a reranker receives candidates and possibly calls a provider; a context builder receives an evidence budget; an evaluator receives a case, release, and randomization context. The architecture must preserve these interfaces so that components can be composed and replaced without flattening their semantics.

Wiring-diagram and operadic accounts of dynamical systems motivate this treatment: modular dynamical systems can be assembled by explicit interface wiring rather than by erasing structure into one global transition function [Libkind et al. 2022]. The implementation in this volume uses ordinary Go composition rather than a generic operad library, but the mathematical interpretation treats architecture as wiring data.

# 4. Three meanings that must agree

## 4.1 Denotational meaning

The denotation of a behavior-complete release is the stochastic behavior it induces. For a fixed architecture $A$ and specification $\theta \in \Theta_A$:

$$
\llbracket \theta \rrbracket_A : S \otimes X
\longrightarrow \mathcal{D}(S \otimes Y \otimes \Tau).
$$

For a finite event sequence, Kleisli iteration gives a distribution over final state and trace. Denotation abstracts away from process implementation while retaining explicitly selected intensional events.

## 4.2 Operational meaning

The operational semantics is a labeled transition relation

$$
\langle C, e \rangle \longrightarrow \langle C', o \rangle,
$$

where $C$ is a runtime configuration, $e$ is an input or internal event, and $o$ is an emitted observation. For the optimizer, labels include proposed, built, evaluation-started, evaluation-completed, decided, promoted, and rejected. Illegal transitions are rejected by the reducer.

The operational semantics answers questions denotation alone does not: Can evaluation start before a required build? Can a candidate be promoted without a passing decision? What survives a crash? Which event order is replayable? Which partial state is terminal?

## 4.3 Statistical meaning

A finite evaluation is neither the denotation nor the operational trace. It is a statistical experiment generated from them. For a suite case $c$, randomization context $z$, fidelity $f$, and release $\theta$:

$$
E_{\theta,f}(c,z) \in \mathcal{D}(O_f).
$$

A comparison observes paired samples and computes interval-valued evidence. Promotion is therefore a decision under uncertainty, conditional on suite scope and modeling assumptions.

## 4.4 Adequacy obligations

The architecture needs bridges among the three meanings.

1. **Interpreter adequacy:** the distribution of completed operational traces projects to the denotational channel.
2. **Replay adequacy:** folding the append-only event log yields the same campaign state as online reduction.
3. **Experiment fidelity:** an evaluation cell records the release, suite, case, repeat, seed design, policy, and fidelity whose channel it sampled.
4. **Decision adequacy:** the gate consumes only evidence certified for the intervention's effect grade.

These are obligations, not automatic consequences of using category-theoretic language.

# 5. Design criteria and non-goals

The mathematical core is judged by a practical standard: does it make invalid production actions unrepresentable or rejectable while allowing domain-specific extension?

A successful design should be **compositional**: the meaning and support of a compound intervention should be derivable from its parts. It should be **conservative**: composition must not silently lower effect grade or evidence requirements. It should be **intensional when necessary**: path, disclosure, and release lineage should survive when endpoint output is insufficient. It should be **extensional when justified**: unaffected artifacts and observations should be reusable under a checkable theorem. It should be **statistically honest**: missing pairs, uncertainty, and fidelity limitations should remain visible. It should be **operationally closed**: promotion authority must be implemented by a small reducer rather than convention.

The thesis does not attempt to solve all search algorithms, prove semantic properties of arbitrary external model providers, define a universal metric of answer quality, or certify production security from offline tests. It does not require that every component be differentiable in the ordinary real-valued sense. Its change calculus is finite and structural. It does not claim that every low-fidelity suite is a Blackwell garbling of a high-fidelity suite; instead it makes that relation an explicit claim requiring a witness or calibration.

\newpage

# Part II. Compositional behavioral semantics

# 6. The base category of stochastic behavior

## 6.1 Markov kernels

A RAG release contains deterministic code and stochastic components: approximate candidate selection, provider sampling, load-dependent scheduling, retries, timeouts, and external state. The natural base is therefore a category of stochastic maps rather than ordinary functions.

In the finite model, an object is a finite set and a morphism $k : X \to Y$ assigns a probability distribution $k(x)$ over $Y$ to every $x \in X$. Composition is Kleisli composition:

$$
(g \circ k)(x)(z) = \sum_{y \in Y} k(x)(y) g(y)(z).
$$

Identity is the Dirac distribution. Tensor product composes independent channels in parallel. Copy and discard maps on deterministic data give the structure of a Markov category. Markov categories provide an abstract setting for probability, conditional independence, and sufficient statistics across discrete and measure-theoretic models [Fritz 2020].

The sandbox implements this finite fragment in `pkg/kernel`. It checks identity, associativity, tensor interchange, copying, and total-variation equality on finite examples.

## 6.2 Why copying requires care

A paired experiment should expose both arms to the same case and randomization context. It should not copy a stochastic outcome after sampling it. The categorical distinction is:

$$
z \xrightarrow{\Delta} (z,z)
\xrightarrow{E_{\theta_0} \otimes E_{\theta_1}} (o_0,o_1),
$$

where $z$ is deterministic experimental context containing case, repeat, and seed. Each arm then interprets that shared context. This is the common-random-numbers design implemented by `experiment.SeedFor` and `RunPaired`.

Copying a provider response from one arm into the other would answer a different question. Copying only a nominal seed is also insufficient if provider model, batching, or sampling implementation differs. The experiment identity must say what is actually shared.

## 6.3 Observation-rich codomains

The semantic output should not be only the user answer. Let

$$
Y = O_{\text{answer}} + O_{\text{abstain}} + O_{\text{failure}} + O_{\text{cancel}},
$$

and let $\Tau$ contain ranked evidence, provider calls, authorization decisions, timing, cost, release, and projection events. Different observation maps select different claims:

$$
\pi_{\text{text}} : Y \otimes \Tau \to \text{AnswerText},
\qquad
\pi_{\text{disclosure}} : Y \otimes \Tau \to \text{DisclosureTrace}.
$$

Two releases may be equivalent under $\pi_{\text{text}}$ and inequivalent under $\pi_{\text{disclosure}}$. Optimization must name the protected observation family rather than asserting unqualified equivalence.

# 7. Stateful and open RAG transducers

## 7.1 Stateful Kleisli arrows

For one request, a release is interpreted as

$$
T_\theta : S \otimes X \to \mathcal{D}(S \otimes Y \otimes \Tau).
$$

This is a stochastic Mealy-style transducer. Repeated execution is obtained by feeding the next state forward. Conversation turns, cache updates, release leases, and streaming projections are therefore within the semantic object.

The state can be factored by ownership. Source and release state are server-owned. Conversation state may be application-owned. Provider state is external and observed only through an adapter. The factorization matters because an intervention may be local to one state component while preserving others.

## 7.2 Open composition

Suppose retrieval produces evidence $E$, context construction produces $C$, and answer generation produces $A$:

$$
R_\rho : S_R \otimes Q \to \mathcal{D}(S_R \otimes E \otimes \Tau_R),
$$

$$
K_\kappa : E \to C,
$$

$$
G_\gamma : S_G \otimes Q \otimes C
\to \mathcal{D}(S_G \otimes A \otimes \Tau_G).
$$

Their composite retains separate parameter and trace interfaces. A wiring diagram connects evidence output to context input and context to generation. Parallel structured-fact retrieval can be tensored with text retrieval and then fused. An agent is a feedback system whose next tool action depends on accumulated evidence and model state.

The point of open composition is not diagram aesthetics. It determines where an intervention can focus, which support it has, and which observations can be reused.

![A RAG component is a parameterized stochastic transducer; composition accumulates parameters and state.](figures/02_para_system.png){width=88%}

## 7.3 Coalgebraic view

A state machine can also be represented coalgebraically as a map

$$
c_\theta : S \to \left(\mathcal{D}(Y \otimes S)\right)^X.
$$

This view is useful for runtime equivalence and controller design. Bisimulation can express whether two implementations match step by step under selected observations. Trace equivalence is weaker and may suffice for an optimization claim. The thesis does not impose one universal equivalence; it supplies observation-indexed relations in Chapter 14.

# 8. Parameterized morphisms and the `Para` construction

## 8.1 Components with parameters

A component whose behavior depends on a parameter object $P$ is a morphism

$$
f : P \otimes X \to Y.
$$

The `Para` construction turns such maps into arrows from $X$ to $Y$ while retaining $P$ as part of the arrow. If $(P,f):X\to Y$ and $(Q,g):Y\to Z$, their composite has parameter $P\otimes Q$:

$$
(Q,g) \circ (P,f) =
\left(P\otimes Q,
P\otimes Q\otimes X \xrightarrow{\cong}
Q\otimes(P\otimes X) \xrightarrow{1\otimes f}
Q\otimes Y \xrightarrow{g} Z\right).
$$

This construction has been used to formalize parameterized learning systems and their composition [Cruttwell et al. 2022]. For RAG, the parameters are not limited to differentiable weights. They include source policies, chunkers, embedding identities, index settings, query plans, timeouts, prompts, and projection policies.

## 8.2 Behavior-complete parameter objects

Let the architecture contain components $c \in C_A$ with local parameter objects $P_c$. The global parameter object is a structured product or tensor

$$
P_A = \bigotimes_{c \in C_A} P_c.
$$

A release specification is a point $\theta : I \to P_A$, where $I$ is the tensor unit, plus content-addressed references to large assets. “Behavior-complete” means that every input capable of changing protected behavior is either inside $P_A$ or explicitly modeled as environmental state. Hidden process environment, mutable provider aliases, or unversioned prompts violate this condition.

This is an engineering discipline rather than a purely mathematical fact. The denotation can only be stable relative to the declared boundary.

## 8.3 Parameters versus campaign state

Search-policy state is not a release parameter. Momentum, surrogate models, trial budgets, and prior observations belong to campaign controller state. A candidate proposes a new release parameter. Keeping these separate prevents accidental promotion of optimizer internals and makes replay possible.

# 9. Optics and local intervention

## 9.1 Lenses as typed focus

A local change needs a way to focus a component parameter inside the whole specification. A cartesian lens from whole $S$ to part $A$ consists of:

$$
\operatorname{get}:S\to A,
\qquad
\operatorname{put}:S\times A\to S.
$$

The usual laws are:

$$
\operatorname{put}(s,\operatorname{get}(s)) = s,
$$

$$
\operatorname{get}(\operatorname{put}(s,a)) = a,
$$

$$
\operatorname{put}(\operatorname{put}(s,a_1),a_2)
=\operatorname{put}(s,a_2).
$$

These laws state that focusing and rebuilding the release does not create unrelated drift. Lenses and more general optics provide a uniform account of bidirectional accessors and lawfulness [Riley 2018].

The sandbox implements cartesian lenses in `pkg/optic`, composition of lenses, finite law checks, and commuting-update checks.

## 9.2 Intervention as focused action

Let $\ell_c : P_A \leftrightarrow P_c$ focus component $c$. Let $\delta_c \in \Delta P_c$ be a local change acting through $\oplus_c$. The induced global intervention is

$$
i_{c,\delta}(\theta)
= \operatorname{put}_{\ell_c}
\left(\theta,
\operatorname{get}_{\ell_c}(\theta) \oplus_c \delta_c\right).
$$

The intervention carries more than this state transformation. It carries a typed target, hypothesis, effect grade, atomic identity, and claimed preservation relation.

## 9.3 Sequential and parallel composition

Sequential composition is ordinary function or categorical composition. Its target support is the union of constituent supports, and its effect grade is their join.

Parallel composition is valid only for interventions on certified independent or commuting foci. Disjoint field names are not by themselves a proof: two fields can influence the same derived artifact or invariant. A parallel combinator therefore requires both disjoint target support and a domain certificate. The sandbox requires an explicit certificate function and rejects overlap.

![A local optic changes one focused parameter while effect grading and dependency differentiation propagate its consequences.](figures/03_intervention.png){width=90%}

# 10. From lenses to general optics

Cartesian lenses are sufficient for ordinary immutable Go structs, but the optimization architecture benefits from the broader optic pattern. An optic separates a forward map from the residual context needed for a backward update. In an optimizer, forward behavior produces observations; backward information carries objectives, counterfactuals, or update demands to the focused component.

Categorical cybernetics combines parametrization and optics to describe systems that interact with an environment and controller, with objectives flowing backward [Capucci et al. 2022]. This suggests a long-term formulation in which a RAG component is a parameterized optic and a search controller supplies update policies. The present implementation stops short of a generic optic coend because that machinery would obscure the trusted kernel in Go. It uses lenses for configuration focus, explicit evaluator outputs for feedback, and an event-sourced controller.

This distinction is important. The thesis uses optics as a semantic organizing principle, not as a requirement that application developers manipulate advanced categorical encodings. A package API should expose simple typed interfaces whose laws correspond to the optic interpretation.

# 11. Change actions and finite derivatives

## 11.1 Changes as first-class values

Ordinary differentiation models infinitesimal changes in smooth spaces. RAG optimization contains discrete changes: replace a prompt, add a source, switch an index backend, change a chunk boundary, or alter a timeout. Change actions generalize differentiation by equipping a value space $A$ with a monoid of changes $\Delta A$ acting on it:

$$
\oplus : A \times \Delta A \to A.
$$

A derivative of $f:A\to B$ is a function

$$
Df : A \times \Delta A \to \Delta B
$$

satisfying the fundamental update law

$$
f(a \oplus \delta a)
= f(a) \oplus Df(a,\delta a).
$$

Change actions connect incremental computation and discrete derivatives [Alvarez-Picallo 2020]. The sandbox implements the law directly and checks finite examples.

## 11.2 Derivatives of build functions

Let

$$
B : \Theta_A \to \mathcal{A}_A
$$

map a release specification to its derived artifact family. A derivative

$$
DB(\theta,\delta\theta)
$$

is an incremental artifact update whose application agrees with a clean rebuild. This is the formal version of the production oracle:

$$
B(\theta \oplus \delta\theta)
\simeq B(\theta) \oplus DB(\theta,\delta\theta).
$$

For deterministic exact artifacts, $\simeq$ can be byte or semantic equality. For approximate indexes, it is a declared tolerance-relative observation relation.

## 11.3 Support abstraction

A full derivative may be expensive or backend-specific. A dependency DAG is a conservative abstraction of its support. Each node represents a parameter, artifact, runtime stage, or evaluator. An edge $a\to b$ means that $b$ may semantically depend on $a$. For changed nodes $C$, the impact is the least downstream-closed set:

$$
\operatorname{cl}(C) = \mu X.\; C \cup \operatorname{succ}(X).
$$

This closure need not compute the delta itself. It determines what cannot be reused without a stronger semantic certificate.

# 12. Dependency closure as an abstract derivative

## 12.1 Soundness condition

Let every artifact or evaluator $v$ have a denotation $F_v$ whose explicit parent inputs are $\operatorname{pred}(v)$. A dependency graph is sound when, for any two worlds agreeing on all ancestors of $v$, $F_v$ agrees under its declared observation relation. If a changed node cannot reach $v$, the worlds agree on the support of $F_v$, so $v$ is reusable.

> **Proposition 12.1 — Support-disjoint reuse.**  Let $i$ be an intervention with impact closure $I$. Let an artifact or evaluator result $a$ factor through a projection onto support $S$. If $I\cap S=\varnothing$ and all external identities used by $a$ agree, then $a$ has the same denotation before and after $i$.
>
> **Proof sketch.** The intervention changes only coordinates in $I$. Disjointness implies the projection onto $S$ is unchanged. Since $a$ factors through that projection, extensionality gives equal output. External identities are separate coordinates and must also agree. $\square$

The external-identity clause includes source barrier, release epoch, case suite, randomization design, evaluator policy, provider identity, and fidelity. Content-addressing only the artifact bytes is therefore insufficient.

## 12.2 Closure algebra

Closure is extensive, monotone, and idempotent:

$$
C \subseteq \operatorname{cl}(C),
$$

$$
C \subseteq D \Rightarrow \operatorname{cl}(C) \subseteq \operatorname{cl}(D),
$$

$$
\operatorname{cl}(\operatorname{cl}(C)) = \operatorname{cl}(C).
$$

It also preserves finite unions in a directed reachability graph:

$$
\operatorname{cl}(C\cup D)
= \operatorname{cl}(C)\cup\operatorname{cl}(D).
$$

These laws make compound-intervention planning compositional. The sandbox checks closure behavior and renders the RAG dependency graph as Graphviz.

## 12.3 Precision ladder

Dependency analysis can be introduced in levels.

1. **Coarse DAG:** conservative reachability.
2. **Keyed nodes:** reuse when canonical input identities match.
3. **Change-sensitive derivative:** produce an exact affected-key set.
4. **Semantic delta:** incrementally update the artifact and verify against a rebuild oracle.
5. **Proof-carrying reuse:** attach a machine-checkable factorization or refinement witness.

A production migration should begin with conservative closure and make precision improvements only where their cost is justified.

# 13. Behavior identity and causal identity

A release identity answers, “What behavior-complete parameter point is this?” A candidate identity answers, “By what declared intervention did we move from the baseline to this point?” A build identity answers, “Which subset of parameters determines these artifact bytes?” An evaluation identity answers, “Which experiment was sampled?” These identities must not be collapsed.

Let

$$
\operatorname{id}_{\text{release}} = H(\theta),
$$

$$
\operatorname{id}_{\text{build}} = H(\pi_B(\theta)),
$$

$$
\operatorname{id}_{\text{candidate}} =
H(\operatorname{id}_{\text{parent}}, i, \operatorname{id}_{\text{child}}),
$$

$$
\operatorname{id}_{\text{experiment}} =
H(\operatorname{id}_{\text{candidate}}, \text{suite}, \text{policy},
\text{fidelity}, \text{barrier}, \text{randomization}).
$$

The sandbox demonstrates the distinction: fusion and reranking changes preserve the build key while changing full spec identity. A chunk-size change changes both.

Path identity also guards causal interpretation. If a search system proposes a compound endpoint, the optimizer can require an ordered sequence of atomic candidates. The final release may be deployable regardless of path, but the optimization record should not pretend that an interaction was an isolated one-factor result.

# 14. Observation-indexed equivalence and refinement

## 14.1 No unqualified semantic preservation

An intervention is not simply “semantics-preserving.” It preserves a selected observation family $\mathcal{O}$. For each observation map $O \in \mathcal{O}$, exact preservation requires

$$
O \circ \llbracket \theta_0 \rrbracket
= O \circ \llbracket \theta_1 \rrbracket.
$$

Examples include answer text, ranked evidence, authorization decisions, release lineage, frontend projection, and latency-excluded functional outcomes. An operational tuning may preserve successful answers but change deadline-triggered failures; then it is not equivalent under the outcome observation.

## 14.2 Approximate refinement

Approximate retrieval needs a metric or divergence. Let $d_O$ compare distributions under observation $O$. An error-budget claim is

$$
d_O\left(
O\circ\llbracket \theta_0 \rrbracket,
O\circ\llbracket \theta_1 \rrbracket
\right) \le \varepsilon_O.
$$

The relation should be compositional. If each component has an error budget and the chosen metric admits a composition bound, the whole pipeline can accumulate a conservative budget. In practice, ANN recall relative to exact retrieval is only one coordinate; downstream reranking and context admission may amplify or mask retrieval error.

## 14.3 Refinement rather than equality

Security and abstention claims are often preorders. A candidate may reveal no more information than the baseline, or abstain on at least the unsafe cases. Write

$$
\theta_1 \sqsubseteq_{\text{disclosure}} \theta_0
$$

for no-more-disclosing behavior. The direction of “better” depends on the observation. The decision doctrine therefore carries metric directions and predicates explicitly.

## 14.4 Trace congruence

For compositional reasoning, an observation relation should be a congruence under the wiring contexts in which replacement is allowed. If $f\sim g$ but composing either with a deadline wrapper yields observably different failure behavior, then $\sim$ was too weak for that context. The architecture should attach preservation claims to both an observation family and an admissible context class.

# 15. The optimization field

## 15.1 Fiber categories

Fix an architecture $A$. Define a category $\operatorname{Opt}(A)$:

- objects are valid behavior-complete specifications $\theta\in\Theta_A$;
- morphisms $i:\theta\to\theta'$ are validated intervention paths;
- identity is the empty intervention;
- composition concatenates paths and validates adjacent identities.

The slice category

$$
(\theta_0 \downarrow \operatorname{Opt}(A))
$$

is the candidate category for baseline $\theta_0$. An object is an intervention out of the baseline; a morphism between candidates is a further intervention making the triangle commute. This formalizes the statement that candidates are arrows, not points.

## 15.2 Architecture indexing

Let $\mathcal{A}$ contain architectures and valid architecture mappings. A mapping $u:A\to B$ can induce a reindexing functor

$$
u^* : \operatorname{Opt}(B) \to \operatorname{Opt}(A),
$$

for example by restricting a shared RAG specification to a product facade or translating a generic query plan into an application-supported subset. Reindexing must preserve identity and composition up to the coherence chosen by the implementation.

The sandbox's `field.Reindex` is only an executable shadow: it maps specifications and supports and checks identity/composition on finite examples. A production implementation can remain concrete while retaining the law as an API contract.

![Each architecture has its own intervention category; reindexing transports specifications and supports between fibers.](figures/04_fibration.png){width=82%}

## 15.3 Graded symmetric monoidal structure

Within a fiber, independent components can be composed in parallel. This gives a partial or certified monoidal structure. Interventions are graded by semantic effect in a join-semilattice $E$:

$$
g(1_\theta)=\bot,
$$

$$
g(j\circ i)=g(i)\vee g(j),
$$

$$
g(i\otimes j)=g(i)\vee g(j).
$$

The grade is a conservative summary, not a complete semantics. It exists to prevent composition from reducing required scrutiny.

## 15.4 The complete field structure

An optimization field consists of:

$$
\mathfrak{F} =
(\mathcal{A},\operatorname{Opt},\llbracket-\rrbracket,
\Delta,D,g,\operatorname{Req},\mathcal{E},\mathcal{D}),
$$

where:

- $\mathcal{A}$ is the architecture category;
- $\operatorname{Opt}$ is the indexed intervention category;
- $\llbracket-\rrbracket$ interprets specifications as open stochastic systems;
- $\Delta$ and $D$ are change actions and derivatives/support closures;
- $g$ is the effect grading;
- $\operatorname{Req}$ maps effects to evidence obligations;
- $\mathcal{E}$ supplies experiment semantics;
- $\mathcal{D}$ supplies decision and campaign semantics.

This tuple is the central abstraction of the thesis. Each later part develops one component and its laws.
EOF
wc -w /mnt/data/optfield_work/thesis/The_Algebra_of_Intervention_Fields.md
```

<details><summary>💭 Thinking</summary>

**Drafted and appended thesis chapters on RAG interventions, architecture, migration, and sandbox appendices**

</details>

```json
{"search_query":[{"q":"arXiv 2103.01931 Categorical Foundations of Gradient-Based Learning journal reference"},{"q":"arXiv 2105.06332 Towards Foundations of Categorical Cybernetics journal reference"},{"q":"change actions incremental computation discrete derivatives Mario Alvarez-Picallo publication"},{"q":"categories of optics Mitchell Riley publication"}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Verifying and packaging**

I’m expanding the manuscript with appendices, bibliography, migration guidance, verification matrices, and sandbox interpretation. I’m also checking reproducibility, documentation, rendered pages, and deliverables before final packaging.

**Verified and packaged**

**Searched 24 websites**

</details>

```unknown
bash -lc tail -n 120 /mnt/data/optfield_work/thesis/The_Algebra_of_Intervention_Fields.md && printf '\n--- counts ---\n' && wc -w -l /mnt/data/optfield_work/thesis/The_Algebra_of_Intervention_Fields.md && printf '\n--- skill excerpts ---\n' && sed -n '1,240p' /home/oai/skills/docx/SKILL.md && printf '\n--- PDF ---\n' && sed -n '1,260p' /home/oai/skills/pdfs/SKILL.md
```

<details><summary>💭 Thinking</summary>

**Inspected manuscript, code, documentation, and fixed reproducibility setup**

</details>

```json
{"search_query":[{"q":"site:link.springer.com \"Categorical Foundations of Gradient-Based Learning\" Cruttwell"},{"q":"site:arxiv.org \"Categories of Optics\" Riley 1809.00738"},{"q":"site:arxiv.org \"Change actions: models of generalised differentiation\" Alvarez-Picallo"},{"q":"site:arxiv.org \"Pareto Optimization in Categories\" Marcolli"}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Searched 3 websites**

</details>

```unknown
bash -lc cat > /mnt/data/optfield_work/thesis/appendices.md <<'EOF'
\newpage

# Appendices

# Appendix A. Formal notation and core definitions

This appendix collects the mathematical objects used throughout the thesis in one place. It is intentionally more explicit than the main text. The purpose is not to force the implementation to expose category-theory terminology. The purpose is to make the interface laws, variance, and proof obligations precise enough that independent implementations can be compared.

## A.1 Categories, monoidal structure, and enrichment

A **category** $\mathcal C$ consists of objects, hom-sets $\mathcal C(X,Y)$, identity arrows $1_X$, and associative composition. The convention in this volume is that $g\circ f$ performs $f$ first. An ordinary deterministic program $f:X\to Y$ is treated as an arrow in a category of value types and total functions. Partiality, failure, state, and probability require richer categories or explicit result objects.

A **symmetric monoidal category** $(\mathcal C,\otimes,I)$ permits parallel composition. The tensor $X\otimes Y$ represents independent interfaces placed side by side; it does not mean that values may always be duplicated. Associators, unitors, and braidings are omitted from formulas when coherence makes their placement unambiguous.

Several structures in the thesis can be understood as enrichment or decoration of ordinary arrows:

- a cost-enriched arrow carries an upper bound, estimate, or distribution of resource consumption;
- a metric-enriched arrow carries an approximation distance;
- a graded arrow carries a semantic effect;
- a labeled arrow carries a causal hypothesis and audit identity;
- an indexed arrow lives in the fiber belonging to one architecture.

The implementation keeps these structures separate because no single numeric enrichment faithfully represents all of them. For example, semantic security effect has no lawful conversion into milliseconds, and a confidence interval is not a monoidal cost.

## A.2 Finite Markov kernels

Let $\mathbf{FinStoch}$ denote the finite stochastic category. Its objects are finite sets. An arrow $k:X\rightsquigarrow Y$ is a row-stochastic matrix, equivalently a function

$$
k:X\longrightarrow \mathcal D(Y),
$$

where $\mathcal D(Y)$ is the set of finite probability distributions over $Y$. The identity is $\eta_X(x)=\delta_x$. Composition is

$$
(\ell\circ k)(x)(z)
=\sum_{y\in Y} k(x)(y)\,\ell(y)(z).
$$

The tensor is the independent product:

$$
(k\otimes \ell)(x,u)(y,v)=k(x)(y)\ell(u)(v).
$$

Deterministic functions embed by Dirac distributions. Every deterministic data object has copy and discard maps

$$
\Delta_X:x\mapsto(x,x),\qquad !_X:x\mapsto *,
$$

satisfying the commutative comonoid laws. A general stochastic arrow does not preserve copying. This distinction is central to paired evaluation. The case identifier, repeat, and seed design may be copied before the two candidate arms execute; one realized random output must not be copied and represented as two independent samples.

A production semantics may replace $\mathbf{FinStoch}$ with a suitable Markov category over measurable spaces. The finite implementation is a witness that the equations can be executed, not a restriction on the abstract architecture.

## A.3 Stateful stochastic transducers

For runtime state $S$, input $X$, output $Y$, and trace $\Tau$, a one-step system is

$$
t:S\otimes X\rightsquigarrow S\otimes Y\otimes\Tau.
$$

Sequential execution threads the state component. Given

$$
t:S\otimes X\rightsquigarrow S\otimes Y\otimes\Tau_t,
\qquad
u:S\otimes Y\rightsquigarrow S\otimes Z\otimes\Tau_u,
$$

their stateful composite first samples $t$, then feeds its new state and output to $u$, and combines traces with an associative trace operation. A trace may be a free monoid of events, a structured event tree, or an append-only artifact reference. The relevant law is associativity of trace combination and compatibility with identity.

A system is **open** when its interfaces remain visible under composition. An index builder, retriever, reranker, answer generator, and projector are not forced into one opaque arrow. Wiring data says which ports are connected. This permits architecture-indexed optimization: an intervention can target a port, component parameter, or wiring decision without pretending that all systems share one flat record.

## A.4 The parameterized category

Given a symmetric monoidal category $\mathcal C$, the parameterized category $\operatorname{Para}(\mathcal C)$ has the same interface objects as $\mathcal C$. A morphism $X\to Y$ is represented by a parameter object $P$ and an arrow

$$
f:P\otimes X\longrightarrow Y.
$$

Two presentations are identified up to the selected equivalence on parameter objects. Composition of $(P,f):X\to Y$ and $(Q,g):Y\to Z$ has parameter object $Q\otimes P$ and behavior

$$
Q\otimes P\otimes X
\xrightarrow{1_Q\otimes f}
Q\otimes Y
\xrightarrow{g}
Z.
$$

For RAG, $P$ includes far more than learned weights. It can contain a corpus barrier, source policy, chunker identity, embedding model, index algorithm, query policy, prompt, provider configuration, timeout, validator, and projection contract. A **behavior-complete** parameter object contains every input whose change can alter the selected observation family.

A configuration field that merely changes logging verbosity may be omitted from an answer-only behavior identity but cannot be omitted from an operations-trace identity. Behavior completeness is therefore indexed by observation scope.

## A.5 Lenses and optics

A cartesian lens from a whole $S$ to a focus $A$ is a pair

$$
\operatorname{get}:S\to A,
\qquad
\operatorname{put}:S\times A\to S,
$$

with the laws

$$
\begin{aligned}
\operatorname{put}(s,\operatorname{get}(s)) &= s,\\
\operatorname{get}(\operatorname{put}(s,a)) &= a,\\
\operatorname{put}(\operatorname{put}(s,a_1),a_2) &= \operatorname{put}(s,a_2).
\end{aligned}
$$

The laws guarantee that focusing and rebuilding a release does not introduce unrelated drift. A focused update $u:A\to A$ lifts to

$$
\widehat u(s)=\operatorname{put}(s,u(\operatorname{get}(s))).
$$

Lenses compose, so a package can expose a focus on `Query.Fusion.Alpha` without exposing the entire release representation. More general optics permit residual context, non-cartesian tensors, and bidirectional feedback. The executable kernel uses lenses because their laws are transparent and sufficient for immutable configuration updates. The abstract architecture leaves room for parameterized optics when evaluator feedback and controller updates are modeled in one compositional object.

## A.6 Change actions and derivatives

A **change action** on $A$ consists of a monoid $(\Delta A,+,0)$ and an action

$$
\oplus:A\times\Delta A\to A
$$

such that $a\oplus0=a$ and $(a\oplus\delta_1)\oplus\delta_2=a\oplus(\delta_1+\delta_2)$. A derivative of $f:A\to B$ is a map

$$
Df:A\times\Delta A\to\Delta B
$$

satisfying

$$
f(a\oplus\delta)=f(a)\oplus Df(a,\delta).
$$

The derivative need not be linear or real-valued. For a build program, $Df$ may be an artifact delta, a work plan, or a conservative set of invalidated nodes. The thesis uses three levels:

1. **semantic delta**, which exactly reconstructs the new output;
2. **artifact delta**, which identifies bytes or rows that must change;
3. **support derivative**, which returns a conservative downstream node set.

The dependency DAG implements the third. It is sound when every output node that can change after an input change appears in the returned closure. It may over-approximate, causing unnecessary work but not stale reuse.

## A.7 Dependency doctrine

For architecture $A$, let $N_A$ be a finite set of semantic nodes and $\leadsto_A$ a directed acyclic dependency relation. For $U\subseteq N_A$, define the downstream closure as the least set satisfying

$$
U\subseteq\operatorname{cl}_A(U),
\qquad
x\in\operatorname{cl}_A(U)\land x\leadsto_A y
\Rightarrow y\in\operatorname{cl}_A(U).
$$

The closure operator is extensive, monotone, and idempotent:

$$
U\subseteq\operatorname{cl}(U),\qquad
U\subseteq V\Rightarrow\operatorname{cl}(U)\subseteq\operatorname{cl}(V),\qquad
\operatorname{cl}(\operatorname{cl}(U))=\operatorname{cl}(U).
$$

For finite DAGs, it also preserves union:

$$
\operatorname{cl}(U\cup V)=\operatorname{cl}(U)\cup\operatorname{cl}(V).
$$

An artifact or evaluator has a declared support $\operatorname{supp}(a)\subseteq N_A$. Support is intensional: it names semantic dependencies, not merely files read during execution. A retriever metric may depend on query rewriting, ranking, and relevance labels but not on the answer generator. An answer-support metric depends on the selected context and therefore on every upstream retrieval stage.

## A.8 The intervention category

Fix architecture $A$. The objects of $\operatorname{Opt}(A)$ are valid behavior-complete specifications $\theta\in\Theta_A$. A morphism

$$
i:\theta\longrightarrow\theta'
$$

contains:

- a total, validated update from $\theta$ to $\theta'$;
- an ordered atomic path identity;
- a primitive target support $\operatorname{supp}(i)$;
- a semantic effect grade $g(i)$;
- a causal hypothesis;
- optional preservation claims;
- a schema and interpreter version.

Identity performs no update, has empty support, bottom grade, and empty path. Sequential composition concatenates paths, composes updates, unions target support, joins grades, and intersects preservation claims. The endpoint is validated after composition.

For a fixed baseline $\theta_0$, candidates form the coslice category

$$
(\theta_0\downarrow\operatorname{Opt}(A)).
$$

An object is an arrow $i:\theta_0\to\theta$. A morphism from $i$ to $j$ is an extension $k$ with $j=k\circ i$. This captures progressive campaigns: a candidate is not merely a configuration but a located intervention history from the baseline.

## A.9 Effect grading

Let $G$ be a finite join-semilattice generated by semantic concerns:

$$
\{\mathsf{op},\mathsf{approx},\mathsf{rel},\mathsf{know},
\mathsf{policy},\mathsf{interact},\mathsf{present}\}.
$$

The implementation represents a grade as a set of generators and join as union. The grading map

$$
g:\operatorname{Mor}(\operatorname{Opt}(A))\to G
$$

satisfies

$$
g(1_\theta)=\bot,
\qquad
g(j\circ i)=g(i)\vee g(j).
$$

This is a conservative grade. A compound path never becomes less consequential than either component. Product-specific grades may refine the shared generators, provided there is a monotone forgetful map into the common lattice.

## A.10 Evidence doctrine

Let $E$ be a join-semilattice of evidence obligations. The map

$$
\mathsf{Req}:G\to E
$$

is monotone and preferably join-preserving:

$$
\mathsf{Req}(g_1\vee g_2)
=
\mathsf{Req}(g_1)\vee\mathsf{Req}(g_2).
$$

An evidence certificate is not just a set bit. It should record the artifact identity, producer, suite, fidelity, source barrier, evaluator version, randomization design, timestamps, and verification outcome. The finite implementation uses a bitset to make the algebra visible; production code must attach native artifacts to each obligation witness.

The doctrine is indexed by architecture and product policy. A common approximation grade may require exact-oracle comparison everywhere, while a medical product may add a domain review and a customer-facing product may add session calibration. Reindexing an intervention must reindex or strengthen its obligations.

## A.11 Architecture indexing and the Grothendieck construction

Let $\mathcal A$ be a category whose objects are RAG architectures and whose arrows are architecture mappings. An arrow $r:B\to A$ can represent restriction to a subsystem, an embedding of a shared component, a migration, or a semantics-preserving translation. The optimization assignment is contravariant:

$$
\operatorname{Opt}:\mathcal A^{op}\to\mathbf{Cat}.
$$

Thus $r$ induces a reindexing functor

$$
r^*:\operatorname{Opt}(A)\to\operatorname{Opt}(B).
$$

Reindexing maps specifications, parameter references, supports, effects, and observation claims. It must preserve identities and composition. Strict preservation may be relaxed to coherent isomorphism in a pseudofunctorial implementation.

The Grothendieck construction $\int\operatorname{Opt}$ has objects $(A,\theta)$ and morphisms combining an architecture map with a vertical intervention in the target fiber. This total category is the mathematical version of a registry containing several RAG products without flattening their parameter spaces. `ragopt` can manage total-category custody while each `ragkit` or application adapter supplies a fiber.

## A.12 Observation families and equivalence

An observation family $O$ selects what is semantically visible. It may include final answers, ranked evidence, traces, latency, cost, disclosure, frontend events, or session outcomes. For release $\theta$, let

$$
\operatorname{Obs}_O(\theta):C_O\rightsquigarrow Y_O
$$

be the induced stochastic channel from controlled context to observations. Exact $O$-equivalence is equality of channels:

$$
\theta\equiv_O\theta'
\iff
\operatorname{Obs}_O(\theta)=\operatorname{Obs}_O(\theta').
$$

Approximate equivalence relative to a divergence $d_O$ and tolerance $\varepsilon$ is

$$
\theta\approx_{O,\varepsilon}\theta'
\iff
\sup_{c\in C_O}d_O(
\operatorname{Obs}_O(\theta)(c),
\operatorname{Obs}_O(\theta')(c))\le\varepsilon.
$$

Finite evaluation cannot usually establish this universal statement. It supplies evidence about a suite-indexed restriction. Preservation claims must therefore name the observation family, domain, tolerance, and evidence scope.

## A.13 Statistical experiments

A statistical experiment is a channel from a latent condition or controlled context to an observation. For release $\theta$, fidelity $f$, case $c$, and deterministic randomization context $z$:

$$
E_{\theta,f}(c,z)\in\mathcal D(O_f).
$$

A paired contrast uses the copying map on $(c,z)$:

$$
(c,z)\xmapsto{\Delta}((c,z),(c,z))
\xmapsto{E_{\theta_0,f}\otimes E_{\theta_1,f}}
(o_0,o_1).
$$

The pairing key is an identity relation, not a join heuristic. If either arm is missing, the cell remains incomplete unless the protocol explicitly defines censoring or imputation.

Experiment $H$ is at least as informative as $L$ in the Blackwell order when there exists a channel $G$ with

$$
L=G\circ H.
$$

The channel $G$ is a garbling witness. Case-count inclusion alone does not establish Blackwell order because different prompts, providers, label policies, or sampling processes can change the experiment in incomparable ways.

## A.14 Metrics and decision relations

A mergeable metric summary is a commutative monoid $(M,\oplus,0)$ together with an extractor from observations. Distributed evaluation is lawful when partitioning and merge order do not change the summary. Mean statistics use count, sum, and sum of squares; ranking statistics may use sufficient count vectors or retained per-case observations.

A metric estimate is interval-valued:

$$
\widehat m=(\mu,L,U,n,\mathit{method}).
$$

A promotion policy defines a feasible predicate over evidence, absolute constraints, protected non-inferiority relations, and a target improvement. The three-valued decision set is

$$
\mathbb V=\{\mathsf{pass},\mathsf{fail},\mathsf{need\text{-}more}\}.
$$

The third value is semantically important. An interval crossing a threshold is not a weak pass or weak fail; it is insufficient evidence under that policy.

After hard feasibility, candidates are compared by a product order with explicit metric directions. A candidate is Pareto dominated when another feasible candidate is no worse on every selected coordinate and strictly better on at least one. The frontier is a report, not an automatic release choice.

\newpage

# Appendix B. Laws, propositions, and proof obligations

This appendix states the principal correctness claims in theorem-like form. Most proofs are straightforward once assumptions are explicit. The engineering difficulty lies in ensuring that concrete identities, dependency supports, and interpreters satisfy those assumptions.

## B.1 Category laws for finite kernels

**Proposition B.1 (finite stochastic category).** Normalized finite distributions with Dirac identity and Kleisli composition form a category.

**Proof sketch.** Left and right identity follow from multiplication by the point mass. Associativity follows by rearranging a finite triple sum:

$$
\sum_y k(x)(y)\sum_z\ell(y)(z)m(z)(w)
=
\sum_z\left(\sum_y k(x)(y)\ell(y)(z)\right)m(z)(w).
$$

Nonnegativity is preserved and total mass remains one. The executable law check compares both association orders on finite kernels within a numerical tolerance.

**Production obligation.** Any optimized distribution representation must preserve normalization, reject NaN and negative masses, and state the tolerance used for approximate equality. Provider APIs that return truncated alternatives are subprobability observations until an explicit “other” outcome or renormalization policy is supplied.

## B.2 Tensor and deterministic copying

**Proposition B.2 (parallel composition).** Independent product of finite kernels is bifunctorial:

$$
(k_2\circ k_1)\otimes(\ell_2\circ\ell_1)
=
(k_2\otimes\ell_2)\circ(k_1\otimes\ell_1).
$$

**Proof sketch.** Both sides expand to the product of two independent finite sums. The result depends on the independence represented by tensor. Shared provider rate limits or correlated random generators belong in explicit shared state, not in a false independent tensor.

**Corollary B.2.1 (paired context).** Copying deterministic context before two stochastic arms is lawful. Copying one stochastic realization and treating the copies as independent is not.

This corollary is the semantic reason the evaluator copies case/repeat/seed identity and executes each arm separately.

## B.3 Lens lifting

**Proposition B.3 (focused update identity).** If $L:S\leftrightarrow A$ is a lawful lens and $u=1_A$, then the lifted update $\widehat u$ is $1_S$.

**Proof.** $\widehat u(s)=\operatorname{put}(s,\operatorname{get}(s))=s$ by get-put.

**Proposition B.4 (focused update composition).** For ordinary updates $u,v:A\to A$,

$$
\widehat{v\circ u}=\widehat v\circ\widehat u.
$$

**Proof sketch.** Expand both sides and use put-get and put-put. This law permits a path of atomic focus updates to be interpreted without serializing and reparsing the whole release at every step.

**Production obligation.** Generated lenses over versioned schemas must be tested across all representable values or derived from a construction that proves the laws. A lens that normalizes unrelated fields during `Put` is not lawful for causal optimization because it creates hidden targets.

## B.4 Intervention category

**Proposition B.5 (category of interventions).** Valid specifications and validated intervention paths form a category under the composition defined in Appendix A.

**Proof sketch.** The identity update is neutral under function composition, union with empty support, grade join with bottom, and path concatenation with the empty path. Associativity follows from associativity of function composition, set union, join, and list concatenation. Preservation claims use set intersection, which is associative and has the universal claim set as identity. Validation must be deterministic and depend only on the resulting specification and declared schema versions.

**Caveat.** If candidate identity is computed only from endpoint bytes, associativity of semantic identity still holds, but causal identity is quotiented away. The thesis intentionally keeps path identity.

## B.5 Grade conservation

**Proposition B.6 (strictest concern wins).** The effect map is a grading functor into the one-object category induced by join semilattice $G$:

$$
g(1)=\bot,
\qquad
g(j\circ i)=g(i)\vee g(j).
$$

Consequently $g(i)\le g(j\circ i)$ and $g(j)\le g(j\circ i)$.

**Engineering consequence.** A relevance-changing intervention followed by an operational intervention cannot be filed as “operational only.” Any path optimizer that permits grade override after composition violates the algebra.

## B.6 Monotone evidence

**Proposition B.7 (evidence monotonicity).** If $\mathsf{Req}:G\to E$ is monotone, then

$$
g(i)\le g(j)\Rightarrow\mathsf{Req}(g(i))\le\mathsf{Req}(g(j)).
$$

If it preserves joins, required evidence for a path is exactly the join of obligations for its generators.

**Proof.** Immediate from monotonicity or the homomorphism law.

**Production obligation.** The obligation schema and policy version are part of campaign identity. Updating policy after an evaluation may strengthen obligations; old evidence can be transported only if a verifier certifies it under the new schema.

## B.7 Closure algebra

**Proposition B.8 (least downstream closure).** For a finite DAG, reachability from $U$ is the least downstream-closed set containing $U$.

**Proof sketch.** Breadth-first or depth-first reachability is downstream closed and contains $U$. Any downstream-closed superset containing $U$ must contain every node reachable by induction on path length.

**Proposition B.9 (union preservation).**

$$
\operatorname{cl}(U\cup V)
=
\operatorname{cl}(U)\cup\operatorname{cl}(V).
$$

**Proof.** A node is reachable from $U\cup V$ exactly when it is reachable from either $U$ or $V$.

**Corollary B.9.1.** Impact closure of a composed intervention can be computed by joining the closures of its atomic target sets. Incremental computation may cache closure per generator.

**Caveat.** Dynamic dependencies, data-dependent routing, and provider fallbacks can make a static DAG incomplete. A sound production graph may require conditional edges labeled by guards; conservative union over feasible guards is safe but less precise.

## B.8 Build-key projection

Let $B_A\subseteq N_A$ be the support of build bytes. Define a build-key projection $\pi_B:\Theta_A\to K_B$ that includes exactly those parameter identities on which the build interpreter depends.

**Proposition B.10 (build reuse by projection).** If the build interpreter factors as

$$
\operatorname{Build}=\overline{\operatorname{Build}}\circ\pi_B
$$

and $\pi_B(\theta)=\pi_B(\theta')$, then build outputs are equal under the build’s declared deterministic equality.

**Proof.** Substitution through the factorization.

**Engineering consequence.** Full release identity and build identity must be distinct. Query-only candidates may share build bytes without pretending to be the same release.

## B.9 Support-disjoint reuse theorem

Let intervention $i:\theta\to\theta'$, impact $I=\operatorname{cl}(\operatorname{supp}(i))$, and artifact/evaluator $a$ with support $S_a$. Let $\xi$ denote external identities not represented in the architecture graph, such as corpus barrier, suite, seed design, provider version, and fidelity.

**Theorem B.11 (reuse soundness).** Suppose:

1. the support declaration is sound: the denotation of $a$ factors through the projection to $S_a$ and $\xi$;
2. the dependency closure is sound;
3. $I\cap S_a=\varnothing$;
4. external identities agree, $\xi=\xi'$.

Then the artifact or observation produced by $a$ is unchanged under $i$ and may be reused.

**Proof sketch.** Sound closure implies every node in $S_a$ is unchanged because none lies in the impact set. Support factorization then gives equal inputs to $a$. Equal external identities provide the remaining arguments. Determinism gives equal artifacts; for a stochastic evaluator, equal channels give equality in distribution under the same randomization design.

**Why content hashing alone is insufficient.** A cached file can have the same bytes while being semantically invalid under a changed suite, policy, or provider contract. Conversely, a different release identity may lawfully reuse the same upstream rankings. The theorem requires semantic support and external identity, not only byte equality.

## B.10 Independent interventions

Two interventions $i$ and $j$ are **structurally independent** when their primitive targets are disjoint. They are **operationally independent** when their impact closures do not contend for noncommutative resources or require incompatible build transactions. They are **behaviorally commuting** when

$$
\llbracket j\circ i\rrbracket_O
=
\llbracket i\circ j\rrbracket_O
$$

for the declared observation family $O$.

**Proposition B.12 (certified parallel composition).** If focused updates commute on specifications, effect and target combination are commutative, and the interpreters are behaviorally commuting on $O$, then either sequential order denotes the same $O$-behavior and may be represented by a parallel intervention $i\otimes j$.

**Caveat.** Disjoint fields do not imply behavioral independence. Candidate depth and reranker threshold may occupy different fields but interact through candidate availability. The sandbox therefore requires an explicit commutativity certificate rather than inferring parallelism from target inequality alone.

## B.11 Pairing integrity

Let a paired cell key be

$$
p=(\mathit{suite},\mathit{case},\mathit{repeat},\mathit{seedDesign},\mathit{fidelity},\mathit{policy}).
$$

**Proposition B.13 (contrast invariance under execution order).** If both arms are evaluated from the same deterministic $p$, evaluator state is either isolated or explicitly modeled, and the metric contrast is a function of the completed pair, then interleaving or execution order does not change the contrast distribution.

**Proof sketch.** The two-arm diagram factors through copied deterministic context and tensor product. Scheduling is observationally irrelevant under isolation. If there is shared mutable provider or cache state, that state must be added to the experiment; otherwise the assumption fails.

**Production obligation.** Randomization may intentionally randomize arm order to control temporal confounding. The selected order is then part of $p$ and the analysis design.

## B.12 Blackwell transport

**Proposition B.14 (decision transport under garbling).** If $L=G\circ H$, every decision rule $d_L$ based on low-fidelity observations has a high-fidelity counterpart $d_H=d_L\circ G$ with the same risk under corresponding states.

This is the operational value of a Blackwell witness: high-fidelity evidence can reproduce every low-fidelity decision. The reverse need not hold. The sandbox checks exact matrix factorization for a finite constructed example.

**Non-theorem.** A suite with more cases is not automatically more informative. If the large suite changes labels or uses a lower-quality provider, there may be no garbling relation in either direction.

## B.13 Monoidal reduction

**Proposition B.15 (partition-independent summary).** Let $(M,\oplus,0)$ be a commutative monoid and $e:O\to M$ an extractor. For any partition of observations $D=D_1\uplus\cdots\uplus D_k$,

$$
\bigoplus_{o\in D}e(o)
=
\bigoplus_{r=1}^k\left(\bigoplus_{o\in D_r}e(o)\right).
$$

Thus distributed workers may merge summaries without changing the result.

**Caveat.** Quantiles, bootstrap intervals, and ranking metrics may require richer summaries or retention of cell-level data. Calling a non-associative floating-point reducer “monoidal” without a declared numerical tolerance is an overstatement. The production artifact should record reduction order or use stable algorithms when exact reproducibility matters.

## B.14 Ordered gate soundness

Let the gate phases be obligation completeness, pair completeness, absolute safety, protected non-inferiority, and target improvement.

**Proposition B.16 (no target override).** If the gate reducer stops on `fail` or `need-more` before the target phase, no target improvement can convert an infeasible candidate into `pass`.

**Proof.** By control-flow construction of the ordered decision algebra.

**Proposition B.17 (conservatism under interval widening).** For one-sided gates defined by interval containment, widening a confidence interval cannot turn `fail` or `need-more` into `pass` unless the widened interval still lies entirely in the passing region. In the usual widening relation, a previous pass may become need-more, but uncertainty cannot manufacture evidence.

## B.15 Pareto invariance

**Proposition B.18 (positive monotone reparameterization).** Pareto dominance is invariant under coordinatewise strictly monotone transformations respecting each metric direction.

**Proof sketch.** Strictly monotone maps preserve all pairwise order relations on each coordinate.

This permits reporting latency in milliseconds or seconds without changing the frontier. It does not permit mixing hard constraints into a weighted scalar because scalarization can reverse incomparable tradeoffs.

## B.16 Campaign reducer safety

Let $R:S\times E\rightharpoonup S$ be the partial reducer.

**Theorem B.19 (inductive safety).** If the initial state satisfies invariants $I$, and every accepted transition from an $I$-state returns an $I$-state, then every finite accepted event trace reduces to an $I$-state.

**Proof.** Induction on trace length.

The implemented invariants include:

- a promoted candidate has a passing decision;
- a candidate is not both promoted and rejected;
- a build-required candidate is not evaluated before build completion;
- an evaluation is not completed before it starts;
- the active candidate is promoted;
- event sequence numbers are contiguous.

The bounded model checker explores every generated legal and illegal action up to depth nine for a finite candidate model and validates reducer behavior. This is not a proof for unbounded campaigns or all production event schemas.

## B.17 Replay adequacy

Let $e_1\cdots e_n$ be an append-only event trace and

$$
\operatorname{fold}_R(s_0,e_1\cdots e_n)
$$

its left fold through the partial reducer.

**Proposition B.20 (prefix replay).** If online command handling persists an accepted event before exposing the resulting state, then replaying the durable prefix after a crash yields the same authoritative state as the online reducer at that prefix.

**Proof sketch.** Determinism of $R$ and induction over the persisted event sequence. Atomic persistence is an external assumption.

**Production obligation.** Side effects such as build submission and provider calls require an outbox, inbox, or idempotency protocol. Reducer replay alone does not make external effects exactly once.

## B.18 Promotion authorization

**Theorem B.21 (promotion kernel).** Assume candidate identity, effect grade, required obligations, experiment identity, gate policy, and decision artifact are all verified by the trusted kernel. If the reducer accepts `Promoted(c)`, then candidate $c$ has a passing decision under the recorded policy and cannot already be rejected.

This theorem is intentionally narrow. It does not state that the suite represents future users, that an evaluator is valid, or that the product owner should choose the candidate. It states that the runtime cannot bypass the declared evidence and decision process.

## B.19 Adequacy triangle

For an interpreter $I$, operational transition system $\to$, and projection $\pi$ from completed traces to denotational observations, the desired adequacy relation is

$$
\llbracket I(\theta)\rrbracket
=
\pi_*\operatorname{Exec}(\theta),
$$

where $\pi_*$ is distribution pushforward. Evaluation then samples a controlled restriction of this channel. A complete correctness argument has three parts:

1. **operational-denotational adequacy** of the interpreter;
2. **experiment provenance** tying samples to interpreter identity and controlled context;
3. **decision adequacy** tying promotion to certified evidence.

Category theory organizes the first and compositional aspects of the second. It does not erase statistical or systems assumptions.

\newpage

# Appendix C. Operational semantics of an optimization campaign

## C.1 Runtime configuration

A campaign configuration is

$$
C=(n,\Theta,W,B,X,D,A,L),
$$

where:

- $n$ is the next event sequence position;
- $\Theta$ maps candidate identity to immutable intervention manifests;
- $W$ is queued and in-flight work;
- $B$ maps candidate/build keys to verified build artifacts;
- $X$ maps experiment cell identities to execution state;
- $D$ maps candidates to decision artifacts;
- $A$ is the currently active release or candidate reference;
- $L$ is the durable append-only log.

The minimal sandbox reducer stores a projection of this configuration. Production state should retain native artifact references outside the reducer state and keep only immutable digests, status, and custody references inside it.

A command is a request such as `Propose`, `RecordBuild`, `StartEvaluation`, `CompleteEvaluation`, `Decide`, `Promote`, or `Reject`. A command handler verifies preconditions and emits one or more events. Only events enter the authoritative reducer.

## C.2 Proposal rule

A proposal is accepted only when the manifest is canonical, its baseline exists, its path verifies, its endpoint is valid, and its identity is unused:

$$
\frac{
\operatorname{verifyPath}(i)=\theta
\quad
\operatorname{id}(i)\notin\operatorname{dom}(\Theta)
}{
C\xrightarrow{\mathsf{propose}(i)}C[i\mapsto\mathsf{proposed}]
}.
$$

The transition records the effect grade, target support, required obligations, build-key projection, and claimed preservation relations. Impact closure is recomputed by the trusted dependency doctrine; a proposer-supplied closure is advisory only.

## C.3 Build rules

If $\operatorname{cl}(\operatorname{supp}(i))$ intersects build support, the candidate requires a build. Scheduling and completion are distinct:

$$
\frac{
\mathsf{status}(i)=\mathsf{proposed}
\quad
\mathsf{requiresBuild}(i)
}{
C\xrightarrow{\mathsf{scheduleBuild}(i,k)}C[W\cup\{k\mapsto\mathsf{queued}\}]
}
$$

and

$$
\frac{
W(k)=\mathsf{running}
\quad
\operatorname{verifyBuild}(a,k)
}{
C\xrightarrow{\mathsf{buildComplete}(i,a)}C[B(i):=a]}.
$$

A cache hit is modeled as a verified completion whose artifact already exists. It is not a skipped transition. The verifier checks build key, corpus barrier, derivation versions, manifest digest, and artifact integrity.

When no build is required, the release interpreter references the baseline build plus the candidate’s query-time specification. This distinction is necessary for joint indexing/query optimization.

## C.4 Evaluation start

An evaluation may start when the required build is present, the experiment manifest is valid, and no cell with the same identity is already terminal:

$$
\frac{
\mathsf{ready}(i,f,p)
\quad
p\notin\operatorname{terminal}(X)
}{
C\xrightarrow{\mathsf{evalStart}(i,f,p)}C[X(p):=\mathsf{running}] }.
$$

The cell identity $p$ includes candidate, baseline, suite, case, repeat, seed design, fidelity, evaluator, and policy versions. Retried attempts have separate attempt identities beneath the same semantic cell. Exactly one accepted result is selected by a deterministic completion rule; duplicates remain auditable.

## C.5 Evaluation completion and partial evidence

Completion records a native observation artifact and a verified summary reference:

$$
\frac{
X(p)=\mathsf{running}
\quad
\operatorname{verifyObs}(o,p)
}{
C\xrightarrow{\mathsf{evalComplete}(p,o)}C[X(p):=\mathsf{complete}(o)]}.
$$

Failure and cancellation are explicit terminal attempt outcomes. They do not silently remove a pairing cell. A protocol may reschedule a new attempt, mark the semantic cell censored with a reason, or leave it missing. The decision kernel sees the resulting completeness relation.

## C.6 Evidence certification

An obligation witness is certified when its verifier accepts an artifact under the candidate and policy identities:

$$
\frac{
q\in\mathsf{Req}(g(i))
\quad
\operatorname{verify}_q(a,i,p)=\mathsf{ok}
}{
C\xrightarrow{\mathsf{certify}(i,q,a)}C[\mathsf{evidence}(i,q):=a]}.
$$

A witness may discharge several obligations only when its verifier explicitly says so. For example, an exact-retrieval comparison may provide both an approximation oracle and retrieval evaluation evidence, but it does not constitute a security review.

## C.7 Decision rule

The decision command constructs a closed evidence bundle:

$$
\mathcal E_i=(i,\mathsf{Req}(g(i)),\mathsf{certs}(i),
\mathsf{pairs}(i),\mathsf{estimates}(i),\mathsf{policy}).
$$

The gate is a deterministic function

$$
\mathsf{Gate}:\mathcal E_i\to\mathbb V\times\mathsf{Checks}.
$$

A decision event includes the evidence-bundle digest, policy digest, verdict, and ordered checks. Recomputing the gate from the same bundle must produce the same artifact.

## C.8 Promotion and rejection

Promotion is permitted only after `pass`:

$$
\frac{D(i)=\mathsf{pass}\quad\neg\mathsf{rejected}(i)}
{C\xrightarrow{\mathsf{promote}(i)}C[A:=i,\mathsf{promoted}(i):=\mathsf{true}]}.
$$

Production activation may be a second state machine with staged, canary, active, draining, rolled-back, and retired states. The campaign’s `promote` event authorizes entry into that activation protocol; it need not perform the deployment itself. The activation result is fed back as a separate observation.

Rejection is terminal for the candidate path under the current campaign identity. A modified path or new evidence policy creates a new candidate or campaign rather than mutating history.

## C.9 Illegal transitions

The reducer rejects at least the following:

- duplicate proposal identity;
- build completion for an unknown or build-free candidate;
- evaluation before a required build;
- empty or inconsistent fidelity identity;
- duplicate start or duplicate semantic completion;
- completion before start;
- decision before any completed evaluation;
- invalid verdict value;
- promotion without pass;
- promotion after rejection;
- rejection after promotion;
- any event with a noncontiguous sequence number.

Rejection of an event is not the same as campaign rejection of a candidate. Invalid runtime input is logged as a command failure outside the authoritative event stream or as a distinct administrative event schema.

## C.10 Crash semantics

The durable log is authoritative. A safe command path is:

1. read current state and expected sequence;
2. validate the command against that state;
3. append the event atomically with compare-and-swap on sequence;
4. reduce or materialize the new state;
5. dispatch external work through an outbox tied to the event.

After a crash, the service reconstructs state by replaying the log and resumes undispatched outbox items. Workers use idempotency keys based on work identity and attempt identity. Completion is accepted only once per semantic cell, but all attempts remain in native logs.

## C.11 Concurrency semantics

Concurrent commands are serialized by sequence compare-and-swap or a transactional stream. This gives a total order for authority events without requiring all work to execute serially. Builds and evaluations may run concurrently when their resource and dependency plans permit.

Parallel candidate evaluation does not imply parallel intervention composition. The former is scheduler concurrency over independent immutable releases. The latter is a semantic claim that two updates commute. These must remain separate types.

## C.12 Fairness and liveness

Safety is reducer-local; liveness depends on the scheduler and environment. Useful fairness assumptions include:

- every queued, feasible work item is eventually attempted;
- retryable failures are retried within policy bounds;
- terminal worker results are eventually delivered;
- a candidate with complete required evidence is eventually decided;
- a passing promotion proposal is eventually either activated or explicitly failed.

No system can guarantee these under permanent provider failure or exhausted capacity. The campaign should therefore expose stalled states and deadlines as observations rather than claiming unconditional liveness.

## C.13 Online experiments

Online canaries live in a different experiment fiber from offline evaluation. Their context includes traffic allocation, user population, release epoch, interference, temporal window, and privacy policy. A promotion from offline to canary is an architecture or stage mapping with new evidence obligations, not merely a higher numeric fidelity.

The online controller must not mutate the active release in place. It proposes a new immutable release or routing policy, obtains authorization, and changes traffic through the activation protocol. This prevents feedback observations from losing the identity of the behavior that generated them.

\newpage

# Appendix D. Reference API blueprint

The following API is a design blueprint rather than a required public surface. It separates mathematical roles so implementations can evolve independently. The executable sandbox contains a smaller finite version.

## D.1 Stable identities

```go
type Digest string

type ArchitectureID string
type SpecID string
type InterventionID string
type PathID string
type BuildKey string
type ReleaseID string
type SuiteID string
type FidelityID string
type EvaluatorID string
type PolicyID string
type CampaignID string
```

Each identity is domain separated. A `SpecID` cannot be constructed by reusing raw `BuildKey` text. Canonical encodings include schema version and semantic namespace. Human names are metadata, not identity.

## D.2 Architecture and specification

```go
type Architecture[S any] interface {
    ID() ArchitectureID
    Validate(S) error
    Canonical(S) ([]byte, error)
    BehaviorID(S, ObservationFamily) (SpecID, error)
    DependencyGraph() DependencyGraph
}

type ObservationFamily struct {
    ID        string
    Version   string
    Outcomes  []string
    TraceAxes []string
}
```

An architecture owns validity and semantic dependency meaning. It does not own search strategy or campaign scheduling.

## D.3 Typed parameter references

```go
type ParamRef[S, A any] interface {
    ID() string
    Lens() Lens[S, A]
    EffectOf(before, after A) Effect
    PrimitiveSupport() NodeSet
    ValidateValue(A) error
}
```

A generated or hand-authored parameter reference combines focus, validation, effect classification, and support. The effect function can be value-sensitive: changing vector mode from exact to approximate has an approximation effect, while changing between two exact algorithms may be operational only under a certified equality relation.

A registry can existentially package typed references behind validated codecs, but the typed constructor should remain the source of truth.

## D.4 Atomic intervention

```go
type AtomicIntervention[S any] struct {
    ID          InterventionID
    Baseline    SpecID
    Result      SpecID
    Target      string
    Effect      Effect
    Hypothesis  string
    Preserves   []PreservationClaim
    Schema      string
    Apply       func(S) (S, error)
}

type PreservationClaim struct {
    Family    string
    Relation  string
    Tolerance *float64
    Scope     string
}
```

Construction applies the update, validates the result, computes identities, and rejects undeclared changes. Existing `ragopt` one-mutation manifests can instantiate this type.

## D.5 Path intervention

```go
type Path[S any] struct {
    ID       PathID
    Baseline SpecID
    Result   SpecID
    Steps    []AtomicIntervention[S]
    Targets  NodeSet
    Effect   Effect
}

func Compose[S any](steps ...AtomicIntervention[S]) (Path[S], error)
```

`Compose` verifies adjacent identities, concatenates causal path, unions targets, joins grades, and intersects preservation claims. Its canonical identity includes ordered step identities even if the endpoint equals another path’s endpoint.

## D.6 Dependency and work planning

```go
type DependencyGraph interface {
    Nodes() []Node
    Closure(NodeSet) (NodeSet, error)
    Explain(from NodeSet, to NodeSet) []DependencyPath
}

type ImpactPlan struct {
    Targets          NodeSet
    Closure          NodeSet
    BuildStages      []StageID
    Evaluators       []EvaluatorID
    ReusableArtifacts []ArtifactRef
    ReusableEvidence  []EvidenceRef
    Assumptions      []Assumption
}

type Planner[S any] interface {
    Plan(base S, path Path[S], external ExternalIdentity) (ImpactPlan, error)
}
```

The explanation paths are important operationally. A build request should say not only “rebuild vector index” but “embedding dimension changed, therefore embeddings and vector index are invalidated.”

## D.7 Reindexing

```go
type Reindex[A, B any] interface {
    MapSpec(A) (B, error)
    MapParam(string) (string, error)
    MapSupport(NodeSet) NodeSet
    MapEffect(Effect) Effect
    MapObservation(ObservationFamily) (ObservationFamily, error)
}
```

Composition and identity must satisfy functor laws. A migration adapter may be partial at the construction boundary, but accepted reindexing arrows should be total on their declared subcategory.

## D.8 RAG interpreter

```go
type ReleaseInterpreter[S any] interface {
    Build(ctx context.Context, spec S, source SourceSnapshot) (BuildArtifact, error)
    Open(ctx context.Context, spec S, build BuildArtifact) (Release, error)
}

type QueryInterpreter interface {
    Direct(ctx context.Context, release Release, req QueryRequest) (EvidenceResult, Trace, error)
    Answer(ctx context.Context, release Release, req AnswerRequest) (AnswerResult, Trace, error)
    Agent(ctx context.Context, release Release, req AgentRequest) (SessionResult, Trace, error)
}
```

Build and open are separated because many candidates share build artifacts while denoting different release behavior. The release is immutable and release-pinned for one request or session epoch.

## D.9 Experiment manifest

```go
type ExperimentManifest struct {
    ID             Digest
    Baseline       ReleaseID
    Candidate      ReleaseID
    Suite          SuiteID
    Fidelity       FidelityID
    Evaluator      EvaluatorID
    Policy         PolicyID
    SourceBarrier  Digest
    SeedDesign     SeedDesign
    Cases          []CaseID
    Repeats        int
    Supports       map[string]NodeSet
}

type CellKey struct {
    Experiment Digest
    Case       CaseID
    Repeat     int
    Arm        Arm
}
```

The manifest is immutable. A different case set, repeat count, provider, prompt, or censoring rule creates a different experiment identity.

## D.10 Evaluator and evidence

```go
type Evaluator[Obs any] interface {
    ID() EvaluatorID
    Support() NodeSet
    Evaluate(context.Context, Release, Case, RandomContext) (Obs, error)
    Extract(Obs) ([]MetricDatum, error)
}

type EvidenceCertificate struct {
    Obligation  string
    Candidate   PathID
    Experiment  Digest
    Artifact    ArtifactRef
    Verifier    Digest
    VerifiedAt  time.Time
    Outcome     string
}
```

The evaluator declares support; the planner decides whether evidence may be reused. The evaluator does not decide promotion.

## D.11 Mergeable metric

```go
type Reducer[Datum, Summary any] interface {
    Zero() Summary
    Add(Summary, Datum) Summary
    Merge(Summary, Summary) Summary
    Estimate(Summary) (Estimate, error)
}

type Estimate struct {
    Mean   float64
    Low    float64
    High   float64
    N      int
    Method string
}
```

Implementations should provide property tests for associativity, commutativity where claimed, identity, and equivalence between one-pass and partitioned reduction.

## D.12 Decision policy

```go
type Verdict string
const (
    Pass Verdict = "pass"
    Fail Verdict = "fail"
    NeedMore Verdict = "need-more"
)

type GatePolicy struct {
    ID              PolicyID
    RequiredEffects map[Effect]EvidenceRequirement
    Absolute        []AbsoluteConstraint
    Protected       []NonInferiorityConstraint
    Target          TargetConstraint
}

type DecisionArtifact struct {
    Candidate      PathID
    EvidenceDigest Digest
    Policy         PolicyID
    Verdict        Verdict
    Checks         []Check
}
```

`Evaluate` is pure and deterministic. It consumes a closed evidence bundle and returns a content-identified decision artifact.

## D.13 Campaign commands and events

```go
type Command interface{ isCommand() }
type Event interface {
    Sequence() uint64
    Campaign() CampaignID
    Digest() Digest
}

type Reducer interface {
    Apply(State, Event) (State, error)
    Check(State) error
}
```

The reducer accepts no search callbacks. Search runs in an outer shell that submits commands. This is the authority boundary.

## D.14 Search policy

```go
type SearchPolicy[S any] interface {
    Propose(context.Context, SearchView[S], Budget) ([]Path[S], error)
    Allocate(context.Context, AllocationView, Budget) ([]WorkRequest, error)
}
```

The view contains immutable summaries and identities, not raw mutation access to campaign state. Search may use random, Bayesian, evolutionary, gradient-like, bandit, or human-guided methods. All proposals are revalidated by the field adapter and all work flows through the campaign reducer.

## D.15 Package ownership

The recommended ownership boundary is:

- `evidencekit` or an equivalent small kernel: canonical identity, immutable references, reducer utilities, law-test helpers;
- `ragkit`: RAG specifications, interpreters, dependency nodes, observation families, release behavior;
- `ragopt`: generic campaign, experiment custody, metric reduction, gates, reports, search interfaces;
- `ragopt/ragspace`: typed RAG interventions, effect doctrine, impact planning, RAG fidelities;
- applications: suites, product metrics, security policy, provider behavior, user/session outcomes, final promotion ownership.

The sandbox combines some of these for legibility. Production packages should preserve the dependency direction even when deployed in one process.

\newpage

# Appendix E. Current-to-target mapping for `ragopt` and `ragkit`

This mapping is based on static inspection of the supplied repositories. The measurements are descriptive, not a substitute for runtime validation.

## E.1 Repository scale

The inspected `ragopt` snapshot contains 45 Go files, approximately 5,925 nonblank Go lines, 42 test functions, and 12 package directories. The inspected `ragkit` snapshot contains 173 Go files, approximately 17,743 nonblank Go lines, 273 test functions, and 23 package directories. The sandbox contains 42 Go files, approximately 3,743 nonblank Go lines, 29 test functions, and 15 package directories.

The important conclusion is qualitative: both existing packages already contain meaningful kernels. The target architecture should evolve them rather than replace them with a speculative universal framework.

## E.2 `ragopt` assets to preserve

The current optimizer’s strongest semantics are immutable custody and exact comparison discipline. These should remain stable:

1. **Immutable snapshots.** Reinterpret them as objects of a fiber and as endpoints of atomic generators.
2. **Exactly one declared mutation.** Preserve as the constructor rule for atomic interventions.
3. **Copied asset verification.** Incorporate artifact and external identities into evidence certificates.
4. **Exact paired cells.** Generalize the cell key with fidelity, evaluator, policy, and seed-design identities.
5. **Explicit missingness.** Retain missing pairs as first-class decision input.
6. **Ordered gates.** Extend with interval non-inferiority and effect-derived obligations; do not replace with scalar search score.
7. **Durable run directories and resume.** Place behind the event reducer and work/outbox protocol.
8. **Reports.** Extend with path, effect, closure, reuse explanation, evidence certificates, and feasible Pareto frontier.

## E.3 `ragopt` additions

The smallest coherent additions are:

- `intervention`: versioned atomic and path manifests;
- `effect`: generic grading interfaces, with RAG grades in an adapter;
- `experiment`: experiment/fidelity identity and randomization design;
- `campaign`: append-only authority reducer;
- `support`: generic support sets and cache-admission predicates;
- `pareto`: feasible frontier reporting;
- `ragspace`: RAG-specific parameter references, dependency doctrine, and obligations.

A generic `ragopt` package should not define chunkers, vector index settings, answer traces, or widget semantics. Those belong to imported adapters.

## E.4 `ragkit` assets to preserve

The existing package boundaries already expose core RAG meanings: chunking, representation, embedding, indexes, retrieval, reranking, answering/generation, and evaluation. They can become the semantic nodes and interpreters of the field.

Preserve:

- deterministic evidence and chunk identity rules;
- total ranking and tie-break laws;
- explicit retrieval stages rather than one opaque query function;
- native result and trace types;
- backend capabilities and approximate-search configuration;
- evaluation types that are genuinely common across products.

## E.5 `ragkit` additions

Add one behavior-complete optimization-facing specification assembled from existing domain types. It should bind:

- source and corpus identity;
- derivation/chunk/representation specifications;
- lexical and vector backend specifications;
- query rewrite, filtering, fusion, reranking, and context policies;
- answer/agent and provider identities where shared;
- serving, timeout, fallback, and projection policies where they affect common observations.

Then add:

- typed parameter references or generated lenses;
- a versioned dependency schema;
- build-key projections;
- observation-family declarations;
- exact-oracle hooks for approximation validation;
- interpreters that expose native traces and release identities.

The aggregate specification should not become a second implementation of every subsystem. It is a manifest of identities and references to native specifications.

## E.6 Overlap elimination

When GEC, RAG-TTC, or Garden contains a copied common substrate, migration should use differential fixtures:

1. capture inputs, release identities, and native outputs from the current implementation;
2. interpret the equivalent `ragkit` specification;
3. compare total ranking, evidence identity, trace projection, and errors;
4. characterize intentional differences as typed interventions;
5. cut over only after the declared observation relations pass.

This avoids calling a rewrite “semantics-preserving” based only on final answer text.

## E.7 Application ownership

GEC retains authorization, source scope, synonyms, provider disclosure policy, judges, and admin behavior. RAG-TTC retains product catalogs, connected retrieval, tool loops, provider integration, review, and tool evaluation. Garden retains multi-turn intent, choices, widget semantics, product facts, calibration, and frontend session behavior.

The shared field can express interventions into these domains, but it does not own their validity. Applications register additional effect grades, obligations, observation families, and gates through monotone extensions.

## E.8 Compatibility strategy

Version every semantic surface independently:

- architecture schema;
- specification schema;
- intervention schema;
- dependency graph;
- effect doctrine;
- experiment manifest;
- evaluator;
- metric reducer;
- decision policy;
- campaign reducer.

A candidate is valid only under a closed version vector. Compatibility code should translate old artifacts into new types explicitly rather than allowing implicit default fields to alter meaning.

\newpage

# Appendix F. Sandbox experiment protocol and interpretation

## F.1 Purpose

The sandbox is a self-contained executable model of the proposed architecture. It uses only the Go standard library, requires no model provider or database, and runs deterministically from a fixed seed design. Its role is to answer a concrete question: can the algebra support a joint indexing/query optimization campaign with lawful composition, dependency-aware reuse, multi-fidelity allocation, uncertainty-aware promotion, and runtime authority?

It is not a benchmark of modern embedding models or a production latency study.

## F.2 Toy corpus and queries

The corpus contains short documents with overlapping concepts and controlled lexical variation. The tokenizer applies deterministic normalization and a small semantic token map to emulate representational similarity without external embeddings. Query cases carry relevance judgments and answer-support terms.

The design intentionally creates tension among lexical retrieval, vector retrieval, chunk boundaries, candidate depth, reranking, context size, latency, and build cost. A trivial corpus where every candidate ties would not exercise the architecture.

## F.3 Behavior-complete candidate specification

The candidate specification includes:

- chunk word limit;
- chunk overlap;
- embedding dimension;
- vector mode (`exact` or modeled `approximate`);
- candidate depth;
- fusion weight;
- reranking flag;
- context size.

The build-key projection includes only chunking, overlap, dimension, and vector-mode inputs that affect build artifacts. The full behavior identity includes all eight fields.

Candidate enumeration uses finite typed and dependent spaces. Invalid combinations are filtered before evaluation. The baseline is excluded from the 575 non-baseline candidates.

## F.4 Dependency graph

Primitive parameters flow into these representative nodes:

- `artifact.chunks`;
- `artifact.lexical_index`;
- `artifact.embeddings`;
- `artifact.vector_index`;
- query lexical and vector channels;
- candidate generation;
- fusion;
- reranking;
- context admission;
- retrieval, answer, and operations evaluators.

A change to fusion weight reaches fusion, downstream ranking, context, and all dependent evaluators but not build artifacts. A change to chunk size reaches every build artifact and downstream observation. The recommended candidate changes query-time fields only, so its build key equals the baseline’s and the build is reused.

## F.5 Query interpreter

For each query, the interpreter:

1. tokenizes the query;
2. scores chunks lexically;
3. computes deterministic vector scores;
4. optionally applies approximate vector selection;
5. takes per-channel candidate prefixes;
6. fuses channels by a weighted score;
7. optionally reranks with a deterministic support feature;
8. admits the top context items;
9. produces retrieval and answer-support observations;
10. records modeled latency and build work.

All rankings use deterministic tie breaks. Approximation is compared to an exact-vector oracle metric.

## F.6 Metrics

The campaign records:

- mean reciprocal rank (`mrr`);
- recall at admitted context (`recall_at_context`);
- answer support (`answer_support`);
- exact-oracle agreement (`exact_oracle_agreement`);
- security compliance sentinel (`security_compliance`);
- modeled query latency (`latency_ms`);
- modeled build work (`build_units`).

Every paired metric retains baseline, candidate, delta, sample count, and interval. The security metric demonstrates gate plumbing only; it is not a security test.

## F.7 Fidelity chain

The chain is:

- `mini`: six cases, one repeat;
- `full`: twelve cases, three repeats;
- `final`: twelve cases, sixteen repeats.

The chain is validated by increasing rank and cost. It is used as a budget-allocation policy. The thesis does not assert a Blackwell relation among these three empirical fidelities. A separate exact finite example demonstrates the garbling checker.

## F.8 Allocation and promotion

All 575 candidates run at mini fidelity. A scalar heuristic allocates 56 candidates to full fidelity and 14 to final fidelity. The scalar combines quality and modeled cost only to spend the evaluation budget. It has no promotion authority.

The final policy requires:

- answer support lower bound at least $0.68$;
- latency upper bound at most $12.5$;
- oracle-agreement lower bound at least $0.70$;
- security compliance lower bound at least $1$;
- recall non-inferiority margin $0.04$;
- answer-support non-inferiority margin $0.03$;
- MRR improvement lower bound at least $0.005$.

Ordered gates return `need-more` when an interval crosses a threshold.

## F.9 Results

The campaign identifies six final candidates that both pass the gate and lie on the feasible Pareto frontier. The selected release is:

```text
chunk_words      18
chunk_overlap     0
embedding_dim    16
vector_mode       exact
candidate_depth   6
fusion_alpha      0.55
rerank             true
context_k          3
```

Relative to baseline at final fidelity:

- MRR increases from approximately $0.9036$ to $1.0000$;
- recall increases from approximately $0.9427$ to $1.0000$;
- answer support increases from approximately $0.4378$ to $0.7472$;
- exact-oracle agreement increases from approximately $0.8737$ to $1.0000$;
- modeled latency increases from approximately $5.8365$ to $12.1103$;
- modeled build work remains approximately $788.6$.

The candidate’s effect grade is approximation plus relevance plus interaction. It requires no rebuild because its indexing parameters equal baseline. Its final decision passes all obligations and gates. The event reducer records proposal, required work, completed evaluation, decision, and promotion.

## F.10 Cache evidence

The recorded build-cache hit rate is approximately $99.9\%$ because many candidate endpoints share one of a small number of build identities. The query/evaluation cache hit rate is approximately $54.0\%$ under support-aware reuse in the finite campaign.

These percentages are properties of the enumerated toy space, not forecasts for production. Their significance is structural: build sharing is determined by build-key projection, and evaluator reuse is determined by impact/support disjointness plus experiment identity.

## F.11 State-space exploration

The Go model checker explores reducer states to depth nine. The report contains 477 distinct sequence-sensitive states and 1,496 accepted transitions. It checks reducer invariants after every accepted transition and verifies that illegal actions are rejected.

Sequence number is included in the canonical state key, so states with identical candidate status but different event counts remain distinct. This makes the count unsuitable as a minimal quotient-state measure but appropriate for auditing the implemented reducer exploration.

## F.12 Reproduction

From the sandbox root:

```sh
./scripts/reproduce.sh
```

The script creates the demo report, JSONL event stream, candidate and frontier CSVs, law report, model-check report, dependency graph, and checksums. `campaign.json` is large because it retains full paired observations rather than only summaries.

## F.13 Interpretation boundary

The campaign establishes that:

- the finite category laws hold for tested examples;
- lenses satisfy their finite law suite;
- change closure drives build and evaluator reuse;
- paths retain effect and causal identity;
- exact pairing and interval gates execute end to end;
- search score cannot bypass the reducer;
- a joint indexing/query field can be enumerated and evaluated.

It does not establish external validity for real corpora, provider behavior, human answer quality, security, or production latency. Those require application-specific experiments and operational evidence.

\newpage

# Appendix G. Verification matrix and formal-method plan

## G.1 Evidence levels

The project uses four evidence levels:

1. **Mathematical proof:** a theorem follows from stated axioms.
2. **Mechanized finite proof or exhaustive exploration:** all states or values of a bounded finite model are checked.
3. **Property and differential testing:** many generated or fixture-backed cases are checked.
4. **Production observation:** behavior is measured under real workloads, providers, failures, and user populations.

These levels are complementary. A proved closure theorem is useless if the production graph omits an edge. A load test cannot prove promotion is unreachable without pass in every event order. The architecture assigns each claim to an appropriate level.

## G.2 Kernel verification matrix

**Canonical identity.** Test determinism, map-order independence, domain separation, schema-version sensitivity, and collision handling. Production uses cryptographic digests; proof assumes collision resistance.

**Finite kernels.** Property-test normalization, identity, associativity, tensor bifunctoriality, copy/discard laws on deterministic data, and total-variation symmetry. Extend with rational arithmetic for exact small proofs if numerical tolerance becomes material.

**Lenses.** Exhaustively check get-put, put-get, and put-put over finite enum fields. Generate lenses from schema metadata where possible. Mutation-test `Put` to ensure the suite catches unrelated-field drift.

**Change actions.** Check action identity and associativity, then derivative squares over finite models. For production build stages, use differential fixtures: incremental maintenance must equal clean rebuild at the same source barrier.

**Dependency graph.** Check acyclicity or explicitly model feedback SCCs; test closure laws; compare predicted invalidation with instrumented dataflow; use mutation testing to delete edges and verify differential tests fail.

**Effect doctrine.** Exhaustively check grade join laws and monotonicity of required evidence. Reject unknown effect bits. Product extensions must prove their forgetful map is monotone.

**Reindexing.** Check identity and composition laws, preservation of valid specifications, and support transport. Migration fixtures should compare denotations under declared observation families.

**Metric reducers.** Property-test identity, associativity, commutativity when claimed, partition independence, and numerical tolerance. Compare summaries against retained raw observations.

**Decision kernel.** Exhaustively test threshold boundaries, missing metrics, incomplete pairs, need-more intervals, policy versioning, and phase order. Mutation-test phase order to ensure target improvement cannot override safety.

## G.3 Campaign model checking

The included TLA+ module models proposal, build, evaluation, decision, promotion, and rejection. Its principal safety properties are:

- no promotion without pass;
- no candidate both promoted and rejected;
- no evaluation before a required build;
- no completion before start;
- active implies promoted.

A production model should add:

- multiple candidates and fidelities;
- retry attempts versus semantic cells;
- durable outbox delivery;
- activation and rollback;
- release leases;
- sequence compare-and-swap;
- cancellation races;
- policy upgrade and evidence invalidation.

The bundle states explicitly that TLC was not executed in the build environment. The Go bounded explorer was executed. Running TLC is a recommended next verification step, not retroactive evidence.

## G.4 Differential oracles

The strongest practical oracles for RAG optimization are:

- clean full rebuild versus incremental build;
- exact vector retrieval versus approximate backend;
- current product pipeline versus shared `ragkit` interpreter;
- direct one-pass reducer versus partitioned/merged reducer;
- online materialized campaign state versus log replay;
- frontend full replay versus snapshot-plus-suffix projection;
- baseline/candidate cells reconstructed from retained native artifacts versus stored summaries.

Every oracle comparison names an equality or tolerance relation. “Looks similar” is not a test relation.

## G.5 Fuzzing

Fuzz these boundaries:

- canonical encoding of nested specifications;
- malformed intervention paths and mismatched adjacent IDs;
- graph node/edge insertion and closure;
- event sequences including duplicates and reorderings;
- experiment cells with missing, duplicated, or inconsistent identities;
- metric NaN, infinity, zero count, and extreme values;
- policy thresholds and interval degeneracy;
- query cancellation and partial trace projection.

Fuzzers should preserve failed inputs as regression fixtures with semantic names.

## G.6 Fault injection

Inject failures at every durable boundary:

- after command validation but before event append;
- after event append but before materialization;
- after outbox append but before worker submission;
- during build staging;
- after artifact write but before verification;
- after one evaluation arm completes;
- during metric merge;
- after decision persistence but before promotion request;
- during activation and rollback.

The desired invariant is not “nothing fails.” It is that every failure yields an explicit, replayable state with no unauthorized promotion or stale artifact reuse.

## G.7 Statistical validation

The sandbox uses normal intervals for simplicity. Production should select methods per metric and design:

- paired bootstrap or permutation intervals for bounded ranking metrics;
- stratified resampling for heterogeneous case groups;
- cluster-robust methods for repeated conversation or user units;
- sequentially valid intervals for adaptive online stopping;
- multiplicity control or hierarchical policies when many candidates share one campaign;
- predeclared censoring and missingness treatment.

The statistical method identity belongs in the estimate and policy artifact. Recomputing with a different method produces a new evidence bundle.

## G.8 Security verification

Policy/security interventions require independent treatment. At minimum:

- authorization precedes hydration and remote disclosure;
- provider payloads are derived only from authorized evidence;
- traces record disclosure identities without leaking protected content;
- evaluator and optimizer principals have least authority;
- candidate manifests cannot smuggle provider or prompt changes through untyped extension fields;
- promotion and activation require distinct capabilities;
- native evidence artifacts have access controls and retention policy.

A security sentinel metric is never a substitute for these controls.

## G.9 Production acceptance criteria

A first production adoption should require:

1. every released candidate has an immutable path manifest and behavior identity;
2. impact plans explain every rebuild and reuse decision;
3. clean rebuild differential tests pass for indexing changes;
4. approximation changes pass an exact-oracle suite;
5. paired cells are complete or explicitly missing;
6. all required obligations have native artifact certificates;
7. the decision artifact is reproducible from retained evidence;
8. the reducer prevents promotion without pass under model checking and tests;
9. activation is release-pinned and rollbackable;
10. monitoring can attribute production observations to release and experiment identity.

\newpage

# Appendix H. Staged implementation and migration program

The migration is designed to create value before the full theory is implemented. Each stage has an exit criterion and preserves compatibility with existing campaigns.

## H.1 Stage 0: freeze semantic vocabulary

Document current candidate, snapshot, build, evaluation, gate, and run identities in `ragopt`; document chunk, representation, index, query, context, answer, and trace identities in `ragkit`. Mark which fields can change behavior and which are operational metadata.

**Exit criterion:** two maintainers can independently compute the same identity and say whether a field change requires a new release.

## H.2 Stage 1: typed atomic descriptors

Wrap current one-mutation candidates in a versioned descriptor containing target parameter, before/after identity, effect grade, hypothesis, and preservation claims. Do not add path search yet.

Recompute the descriptor from copied snapshots and reject mismatches. Add law tests for grade monotonicity and hidden mutation detection.

**Exit criterion:** every existing campaign can run through the descriptor adapter without changing its final report, and every candidate has a machine-readable semantic target.

## H.3 Stage 2: dependency graph and build keys

Define the first RAG dependency graph around stable stages: source, chunk, representations, lexical index, vector index, retrieval channels, fusion, reranking, context, answer, and evaluators. Add build-key projection and an explainable closure API.

Initially use conservative edges. Instrument actual stage inputs and compare predicted closure with clean rebuilds and current pipeline behavior.

**Exit criterion:** query-only candidates demonstrably reuse build artifacts, and every indexing candidate that requires rebuild is detected by differential tests.

## H.4 Stage 3: path candidates

Add ordered path manifests over atomic candidates. Verify adjacent snapshots and preserve path identity. Introduce generated finite spaces and dependent filters as search front ends, but keep existing grid/search implementations working.

Do not infer parallel independence automatically. Add a certificate interface and use it only for well-understood disjoint changes.

**Exit criterion:** a two- or three-factor coordinated experiment executes without opaque multi-mutation configuration files, and endpoint-equivalent paths remain distinguishable in reports.

## H.5 Stage 4: experiment identity and support-aware reuse

Version experiment manifests with suite, case set, repeats, seed design, fidelity, evaluator, source barrier, and policy. Require evaluators to declare support. Admit cached observations only when both semantic identity and support-disjointness pass.

Retain all native cells and explicit missingness. Introduce mergeable metric reducers with partition-law tests.

**Exit criterion:** an evaluator reuse report explains why each artifact was reused or recomputed, and replay from native cells reproduces every summary.

## H.6 Stage 5: evidence doctrine and interval gates

Map effect grades to evidence obligations. Attach native certificates. Extend gates with interval-valued absolute and non-inferiority checks. Preserve the existing ordered-gate behavior for legacy policies.

Add feasible Pareto reporting after gates. Keep the final selection explicit and product-owned.

**Exit criterion:** no candidate can pass with an unmet obligation, incomplete required pairing, or interval crossing a hard threshold.

## H.7 Stage 6: campaign reducer and job integration

Put campaign authority behind the append-only reducer. Connect builds and evaluations through an outbox and idempotent job identities. Treat search as an untrusted command producer.

Model-check the event protocol and run fault-injection tests. Separate campaign promotion authorization from release activation.

**Exit criterion:** crash/replay and duplicate-delivery tests preserve state; promotion without pass is unreachable in the checked model and rejected in implementation.

## H.8 Stage 7: product fibers

Implement adapters for at least two applied systems before generalizing further.

For GEC, focus first on authorization/disclosure ordering, synonyms, reranking, judges, and admin traces. For RAG-TTC, focus on complete builds, ANN certification, connected retrieval, tool trajectories, and review. For Garden, focus on session epochs, product facts, choices, widgets, and frontend convergence.

Promote only abstractions that retain the same laws and meanings in at least two fibers. Similar names are insufficient.

**Exit criterion:** shared campaigns can compare common RAG interventions while product-specific effects and gates remain native.

## H.9 Stage 8: online feedback

Add canary and production-observation fibers with traffic, temporal, user, and privacy identities. Use immutable releases and routing interventions. Introduce sequentially valid decisions where appropriate.

Keep online data from silently rewriting offline suites or active release parameters. Feedback creates new candidate hypotheses.

**Exit criterion:** every online observation is attributable to one release epoch and experiment protocol, and rollback does not mix evidence across releases.

## H.10 Governance

Create architectural decision records for:

- behavior-complete release identity;
- dependency graph ownership;
- effect taxonomy and extension;
- evidence certificate schemas;
- experiment and fidelity identity;
- gate policy authority;
- campaign event schemas;
- activation capability separation.

Schema evolution requires migration tests and explicit compatibility statements. Mathematical terminology should appear in design documents where it clarifies laws; production APIs should use domain language familiar to engineers.

## H.11 First three implementation projects

A practical first quarter can be organized as three self-contained projects.

**Project A: Closure and build reuse.** Implement typed parameter references, a RAG dependency graph, build-key projection, and differential clean-rebuild tests. Demonstrate reuse for fusion/reranking and rebuild for chunk/embedding changes.

**Project B: Paired evidence and gates.** Extend experiment identity, support declarations, interval estimates, non-inferiority, and obligation certificates. Reproduce one existing campaign through both old and new reports.

**Project C: Campaign authority.** Implement event schemas, reducer, replay, outbox integration, and model checking. Keep the existing search policy and workers unchanged behind adapters.

These projects can proceed partly in parallel once the shared identity schema is fixed.

\newpage

# Appendix I. Bibliography

Alvarez-Picallo, Mario, and C.-H. Luke Ong. 2019. “Change Actions: Models of Generalised Differentiation.” In *Foundations of Software Science and Computation Structures (FoSSaCS 2019)*, 45–61. Lecture Notes in Computer Science. Springer. DOI: 10.1007/978-3-030-17127-8_3.

Blackwell, David. 1953. “Equivalent Comparisons of Experiments.” *Annals of Mathematical Statistics* 24(2): 265–272.

Capucci, Matteo, Bruno Gavranović, Jules Hedges, and Eigil Fjeldgren Rischel. 2022. “Towards Foundations of Categorical Cybernetics.” *Electronic Proceedings in Theoretical Computer Science* 372: 235–248. DOI: 10.4204/EPTCS.372.17. arXiv:2105.06332.

Cruttwell, Geoffrey S. H., Bruno Gavranović, Neil Ghani, Paul Wilson, and Fabio Zanasi. 2022. “Categorical Foundations of Gradient-Based Learning.” In *Programming Languages and Systems: ESOP 2022*, 1–28. Lecture Notes in Computer Science 13240. Springer. DOI: 10.1007/978-3-030-99336-8_1.

Fong, Brendan, and David I. Spivak. 2019. *An Invitation to Applied Category Theory: Seven Sketches in Compositionality*. Cambridge University Press.

Fritz, Tobias. 2020. “A Synthetic Approach to Markov Kernels, Conditional Independence and theorems on Sufficient Statistics.” *Advances in Mathematics* 370: 107239. DOI: 10.1016/j.aim.2020.107239.

Fritz, Tobias, Tomáš Gonda, Paolo Perrone, and Eigil Fjeldgren Rischel. 2023. “Representable Markov Categories and Comparison of Statistical Experiments in Categorical Probability.” *Theoretical Computer Science* 961: 113896. DOI: 10.1016/j.tcs.2023.113896. arXiv:2010.07416.

Jacobs, Bart. 1999. *Categorical Logic and Type Theory*. Studies in Logic and the Foundations of Mathematics 141. Elsevier.

Kleisli, Heinrich. 1965. “Every Standard Construction Is Induced by a Pair of Adjoint Functors.” *Proceedings of the American Mathematical Society* 16(3): 544–546.

Libkind, Sophie, Andrew Baas, Evan Patterson, and James Fairbanks. 2022. “Operadic Modeling of Dynamical Systems: Mathematics and Computation.” *Electronic Proceedings in Theoretical Computer Science* 372: 192–206. DOI: 10.4204/EPTCS.372.14. arXiv:2105.12282.

Mac Lane, Saunders. 1998. *Categories for the Working Mathematician*. Second edition. Graduate Texts in Mathematics 5. Springer.

Marcolli, Matilde. 2022. “Pareto Optimization in Categories.” arXiv:2204.11931.

Riley, Mitchell. 2018. “Categories of Optics.” arXiv:1809.00738.

Spivak, David I. 2014. *Category Theory for the Sciences*. MIT Press.

Vagner, Dmitry, David I. Spivak, and Eugene Lerman. 2015. “Algebras of Open Dynamical Systems on the Operad of Wiring Diagrams.” *Theory and Applications of Categories* 30: 1793–1822.

## Repository and artifact sources

The empirical sections use the supplied August 2026 source snapshots of `ragkit`, `ragopt`, GEC, RAG-TTC, and TTC Garden, together with the preceding volume *The Semantics and Dynamics of Retrieval-Augmented Systems*. Repository measurements in this volume were computed by deterministic local scripts and describe only the inspected snapshots. The sandbox source, complete campaign artifacts, figures, checksums, and QA reports are included in the source bundle.

\newpage

# Appendix J. Glossary

**Absolute constraint.** A one-sided requirement on a candidate estimate, such as a latency upper bound or security lower bound. It is checked before target improvement.

**Architecture.** The typed component and wiring structure of a RAG system, including the semantic nodes over which dependency and observation doctrines are defined.

**Architecture mapping.** A restriction, embedding, migration, or translation between architectures that induces reindexing between optimization fibers.

**Artifact support.** The semantic node set through which an artifact’s denotation factors. It is stronger than a list of files accessed during execution.

**Atomic intervention.** One validated, typed change to a behavior-complete specification. It is a generator in the intervention category.

**Behavior-complete specification.** A release specification containing every identity capable of changing a selected family of observations.

**Blackwell order.** A preorder on statistical experiments. $H$ is at least as informative as $L$ when $L$ can be obtained by garbling $H$.

**Build key.** The projection of a full release specification onto parameters that determine build artifacts.

**Candidate.** A morphism from a baseline specification, including causal path, effect grade, targets, and endpoint. It is not merely an endpoint configuration.

**Campaign.** The runtime process that proposes, builds, evaluates, decides, and authorizes promotion of candidates under an immutable protocol.

**Campaign reducer.** The small partial state transition function that is authoritative for campaign status and promotion safety.

**Change action.** A monoid of changes acting on values, used to define generalized derivatives and incremental computation.

**Closure.** The least downstream-closed node set containing an intervention’s primitive targets.

**Commutativity certificate.** Evidence that two interventions may be reordered or composed in parallel under a declared observation relation.

**Coslice category.** For baseline $\theta_0$, the category whose objects are arrows out of $\theta_0$ and whose morphisms extend those arrows. It models progressive candidates.

**Decision artifact.** A content-identified record of policy, evidence digest, ordered checks, and pass/fail/need-more verdict.

**Denotational semantics.** The mathematical behavior assigned to a release or campaign, independent of one operational implementation but retaining selected outputs and traces.

**Dependency derivative.** A conservative abstraction of how a local change propagates to artifacts, runtime stages, and evaluators.

**Effect grade.** A join-semilattice element describing which semantic concerns an intervention may alter.

**Evidence certificate.** A verified reference showing that a specific obligation was discharged for a candidate under explicit identities.

**Evidence doctrine.** The monotone mapping from effect grades to required evidence, indexed by architecture and product policy.

**Experiment.** A stochastic observation channel generated from a release under controlled cases, randomization, evaluator, and fidelity.

**External identity.** A semantic input not represented as a dependency node, such as suite, seed design, provider version, source barrier, or policy.

**Feasible candidate.** A candidate that passes required evidence, completeness, absolute, and protected gates under the selected policy.

**Fidelity.** An experiment configuration with a particular information and cost profile. Numeric rank alone does not imply Blackwell comparability.

**Fiber.** The intervention category belonging to one architecture in the indexed optimization field.

**Garbling.** A stochastic post-processing channel that turns one experiment’s observations into another’s.

**Grade join.** Conservative combination of semantic effects under intervention composition; no concern is lost.

**Impact plan.** The trusted result of applying dependency closure and work/evidence rules to an intervention.

**Incremental rebuild.** Maintenance of derived artifacts by applying a change plan rather than performing a clean full build, subject to a differential equivalence oracle.

**Intervention.** A typed, validated, causal change from one valid specification to another.

**Intervention path.** An ordered composition of atomic interventions whose adjacent identities verify.

**Kleisli composition.** Sequential composition of effectful or stochastic functions by binding the output distribution of one into the next.

**Lens.** A lawful getter/putter pair that focuses and updates a local part of a whole specification.

**Markov category.** A symmetric monoidal category modeling stochastic maps with copy and discard structure on data objects.

**Metric reducer.** A mergeable algebra that converts native observations into estimates while supporting partitioned execution.

**Need-more.** The decision produced when evidence does not establish either side of a policy threshold, commonly because an interval overlaps it.

**Non-inferiority.** A protected-metric relation requiring the candidate not to be worse than baseline by more than a declared margin.

**Observation family.** The selected projection of behavior—answers, evidence, traces, disclosure, latency, frontend events, or sessions—used to state equivalence or refinement.

**Operational semantics.** The labeled transition rules describing how campaign or RAG runtime state evolves step by step.

**Optic.** A compositional abstraction for focusing through structured systems while retaining residual context and, in general, backward information.

**Optimization field.** The indexed family $\operatorname{Opt}:\mathcal A^{op}\to\mathbf{Cat}$ of intervention categories over architectures, together with effect, dependency, experiment, and decision structure.

**Oracle.** A reference interpreter or relation used to validate another implementation, such as exact retrieval for approximate search or clean rebuild for incremental maintenance.

**Paired cell.** Baseline and candidate observations sharing exactly the same controlled case, repeat, seed design, fidelity, evaluator, and policy identity.

**Parameterized morphism.** A system arrow $P\otimes X\to Y$ whose parameter object remains explicit under composition.

**Pareto frontier.** The feasible candidates not dominated across the selected multi-objective metric order.

**Path identity.** Content identity of the ordered atomic intervention history, not only its endpoint.

**Preservation claim.** A statement that an intervention retains a named observation relation over a declared scope and tolerance.

**Promotion.** Campaign authorization that a candidate has passed the declared evidence policy. Deployment or traffic activation may be a separate protocol.

**Reindexing.** Transport of specifications, interventions, support, and observations along an architecture mapping.

**Release.** An immutable, behavior-complete interpretation unit against which queries and experiments are pinned.

**Replay adequacy.** Equality between campaign state reconstructed from the durable event log and authoritative online reduction of the same prefix.

**Reuse.** Acceptance of an existing artifact or observation for a candidate after support-disjointness and external-identity checks.

**Search policy.** An untrusted strategy that proposes candidates and allocates budget. It has no promotion authority.

**Semantic node.** A parameter, derived artifact, runtime stage, observation, or evaluator in the architecture dependency doctrine.

**Stateful stochastic transducer.** A stochastic arrow that consumes state and input and returns new state, output, and trace.

**Statistical semantics.** The experiment and inference layer connecting a release’s behavior to finite evidence and decisions under uncertainty.

**Support-disjointness.** The condition that an intervention’s impact closure does not intersect an artifact or evaluator’s semantic support.

**Tensor.** Parallel composition in a monoidal category. In a stochastic setting it represents declared independence unless shared state is explicit.

**Trace.** Structured intensional events recording lineage, disclosure, fallbacks, latency, cost, tools, streaming, and other behavior not captured by final output alone.

**Trusted computing base.** The small set of identity, validation, closure, pairing, evidence, gate, and reducer code whose correctness is required for safe promotion.

**Work plan.** The concrete build, evaluation, and verification tasks derived from an impact plan and campaign protocol.

# Appendix K. Artifact inventory and integrity

The publication bundle is organized so that the theory can be inspected independently of the executable model and the executable model can be reproduced independently of the formatted thesis.

The top-level artifacts are:

- the Markdown manuscript;
- the editable DOCX publication;
- the rendered PDF publication;
- the complete `optfield-sandbox` source tree;
- all diagram sources and rendered figures;
- repository measurements and selected campaign projections;
- DOCX accessibility output, page-render metrics, PDF preflight, and checksums.

The sandbox `demo-output` directory contains the complete campaign evidence. Derived CSV and Markdown reports are conveniences. The JSON/JSONL artifacts and immutable source are the primary reproduction inputs.

Every bundle should be verified with its checksum manifest after transfer. A checksum establishes byte integrity, not semantic correctness. Semantic verification still requires running tests, law checks, the model checker, and the campaign under the documented toolchain.
EOF
cat /mnt/data/optfield_work/thesis/appendices.md >> /mnt/data/optfield_work/thesis/The_Algebra_of_Intervention_Fields.md
wc -w -l /mnt/data/optfield_work/thesis/The_Algebra_of_Intervention_Fields.md

```

<details><summary>💭 Thinking</summary>

**Appended formal notation and validated full reproduction checks**

</details>

```unknown
bash -lc sed -n '1,320p' /mnt/data/optfield_work/volume2_source/build_publication.sh && printf '\n--- available tools ---\n' && command -v pandoc && pandoc --version | head -n 4 && python /home/oai/skills/docx/render_docx.py --help | sed -n '1,220p' && printf '\n--- docx a11y help ---\n' && python /home/oai/skills/docx/ooxml_a11y_advisor.py --help | sed -n '1,220p' && printf '\n--- pdf preflight help ---\n' && python /home/oai/skills/pdfs/scripts/pdf_preflight.py --help | sed -n '1,220p'
```

The design has settled on an optimization doctrine linking indexed intervention categories to open stochastic behavior and validated traces. Crucially, candidate search remains separate from promotion authority and rebuild closure.

<details><summary>💭 Thinking</summary>

**Finalizing deliverables**

I’m completing the final rendered-document verification and packaging the thesis, sandbox, source materials, figures, and reproducibility records so the finished bundle is self-contained and usable.

</details>

```unknown
bash -lc ls -1 /mnt/data/optfield_work/publication/qa/contact_sheets_final | sed -n '1,40p' && echo COUNT=$(find /mnt/data/optfield_work/publication/qa/contact_sheets_final -type f | wc -l) && ls -lh /mnt/data/optfield_work/publication/The_Algebra_of_Intervention_Fields.docx /mnt/data/optfield_work/publication/qa/docx_render_final/The_Algebra_of_Intervention_Fields.pdf
```

<details><summary>💭 Thinking</summary>

**Created, audited, rendered, validated, and bundled the thesis publication deliverables**

</details>

```json
{"search_query":[{"q":"site:arxiv.org Markov categories Fritz 2020 synthetic approach conditional independence"},{"q":"site:arxiv.org categorical cybernetics parametrized morphisms optics Capucci Gavranovic Hedges Rischel"},{"q":"site:arxiv.org change actions models of generalised differentiation Alvarez-Picallo Ong"},{"q":"site:arxiv.org Pareto optimization in categories Marcolli 2022"}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Searched 2 websites**

</details>

# *The Algebra of Intervention Fields*

The thesis and executable reference sandbox are complete.

## Deliverables

- [Download the 126-page PDF](sandbox:/mnt/data/rag_output/The_Algebra_of_Intervention_Fields.pdf)
- [Download the editable DOCX](sandbox:/mnt/data/rag_output/The_Algebra_of_Intervention_Fields.docx)
- [Download the Markdown manuscript](sandbox:/mnt/data/rag_output/The_Algebra_of_Intervention_Fields.md)
- [Download the self-contained Go sandbox](sandbox:/mnt/data/rag_output/Optfield_Sandbox.zip)
- [Download the complete source and reproducibility bundle](sandbox:/mnt/data/rag_output/The_Algebra_of_Intervention_Fields_Source.zip)

The source bundle contains the manuscript, publications, thirteen figures and their sources, empirical projections, the complete sandbox, publication tooling, accessibility and style audits, PDF preflight results, Go test and vet results, law-check reports, model-check reports, and a SHA-256 integrity manifest.

## Scope of the thesis

The volume contains approximately **27,700 words, 52 numbered chapters, seven parts, and eleven appendices**. It takes the informal optimization-field proposal from Chapter 21 and replaces the usual flat configuration-space model with a compositional semantic architecture.

The central object is an **optimization field**

\[
\operatorname{Opt}:\mathcal A^{op}\longrightarrow \mathbf{Cat},
\]

where:

- \(\mathcal A\) is a category of RAG architectures and architecture mappings;
- each fiber \(\operatorname{Opt}(A)\) contains behavior-complete release specifications for architecture \(A\);
- morphisms are typed, validated intervention paths rather than arbitrary before-and-after configurations;
- reindexing transports specifications, intervention support, observations, and obligations between architectures.

For a fixed baseline \(\theta_0\), the candidate space is the coslice category

\[
(\theta_0\downarrow \operatorname{Opt}(A)).
\]

A candidate therefore retains both its endpoint and its causal path. Two candidates that produce the same final specification can remain distinct when they used different interventions, assumptions, builds, evidence, or audit histories.

## Mathematical backbone

The construction integrates several structures that play different roles rather than forcing all concerns into one category.

### Denotational semantics

A production RAG release is interpreted as an open, stateful, stochastic, parameterized transducer:

\[
T_\theta:
S\otimes X
\longrightarrow
\mathcal D(S\otimes Y\otimes \operatorname{Tr}),
\]

where \(S\) is runtime state, \(X\) contains requests and controlled context, \(Y\) contains outcomes, and \(\operatorname{Tr}\) preserves the operational observations relevant to the optimization claim.

Parameterized composition accumulates the local parameter objects of indexing, retrieval, ranking, context construction, generation, agents, validation, serving, and presentation. It does not flatten them into one untyped dictionary.

### Local intervention

Lawful lenses and optics focus a typed component parameter inside a behavior-complete release. An atomic intervention has:

- a target optic;
- a before and after value;
- a hypothesis;
- a semantic effect grade;
- primitive support;
- preservation claims;
- an application operation.

Sequential composition preserves the ordered intervention path. Certified parallel composition is permitted only when the required commutativity and independence conditions have been established.

### Change and dependency semantics

Change actions provide the discrete analogue of differentiation:

\[
f(a\oplus \delta a)
=
f(a)\oplus Df(a,\delta a).
\]

For RAG, \(Df\) need not be numerical. It may produce an artifact delta, a rebuild plan, an invalidation set, or a required evaluation set.

A dependency graph supplies a conservative support abstraction. The downstream closure

\[
\operatorname{cl}_A(\operatorname{supp}(i))
\]

determines which artifacts, runtime stages, observations, and evaluators may have changed. Artifact reuse is then justified by support disjointness and equality of external experiment identities, not merely by matching file bytes.

### Effect and evidence doctrine

Interventions are graded in a finite join-semilattice containing concerns such as:

\[
\{\text{operational},\text{approximation},\text{relevance},
\text{knowledge},\text{policy/security},
\text{interaction},\text{presentation}\}.
\]

Composition joins effect grades. A monotone doctrine

\[
\operatorname{Req}:E\longrightarrow O
\]

maps effects to minimum evidence obligations. Consequently, composing a more consequential intervention cannot reduce the evidence required for promotion.

### Statistical semantics

Evaluation is treated as a statistical experiment generated by a release under a declared suite, fidelity, randomization design, source barrier, evaluator policy, and observation family.

Pairing copies deterministic experimental context into both arms before stochastic execution. It does not copy a realized random output or merely reuse a nominal integer seed.

Multi-fidelity evaluation is modeled through comparison of experiments. A low-fidelity experiment \(L\) is genuinely a garbling of a higher-fidelity experiment \(H\) only when a channel \(G\) exists such that

\[
L=G\circ H.
\]

Where that witness is unavailable, the implementation records a weaker empirical calibration claim rather than asserting a Blackwell order.

### Decision semantics

Search allocation and promotion authority are separated.

A search controller may use scalar scores, Bayesian optimization, evolutionary methods, bandits, random search, or human proposals. None may write a promotion event.

Promotion instead evaluates:

1. evidence completeness;
2. pairing integrity;
3. absolute constraints;
4. protected non-inferiority constraints;
5. target improvement;
6. feasible Pareto order;
7. optional product review.

The trusted decision kernel returns `pass`, `fail`, or `need-more-evidence`. Interval overlap is therefore not silently converted into success.

The theoretical synthesis draws on Markov categories, parameterized maps and lenses, change-action models, categorical cybernetics, categorical comparison of statistical experiments, and categorical formulations of Pareto optimization. citeturn294183search0turn294183search21turn294183search2turn294183search1turn294183search8turn294183search3

## Runtime and operational semantics

Optimization is modeled as a cybernetic controller interacting with a RAG plant through observations and actions:

\[
\Gamma:C\otimes O\longrightarrow\mathcal D(C\otimes A).
\]

Campaign execution has a small-step transition semantics over immutable events such as:

- proposed;
- build required;
- build started and completed;
- evaluation started and completed;
- evidence certified;
- decision recorded;
- promoted;
- rejected.

An append-only reducer is the sole authority for campaign state. Search algorithms, workers, evaluators, and provider adapters submit commands or evidence; they cannot mutate promoted state directly.

The reducer enforces invariants including:

- no promotion without a passing decision;
- no candidate can be both promoted and rejected;
- build-dependent evaluation cannot begin before build completion;
- a completed evaluation must have started;
- evaluation identities cannot be silently mixed;
- event sequence numbers are contiguous;
- only the active passing candidate can be promoted.

Replay is the denotational fold of the event sequence. This makes checkpointing, crash recovery, audit, and reducer replacement precise.

## Package architecture proposed for `ragkit` and `ragopt`

The thesis derives a four-layer ownership structure:

- A foundational kernel owns canonical identity, immutable references, finite ordering, append-only events, reducers, and generic algebraic interfaces.
- `ragkit` owns behavior-complete RAG specifications, dependency meaning, observations, interpreters, release behavior, and RAG trace semantics.
- `ragopt` owns generic candidate custody, exact pairing, experiment identity, metric reduction, gates, campaign state, and promotion reports.
- `ragopt/ragspace` is the thin adapter that maps `ragkit` parameter references into intervention targets, effect grades, dependency closures, observation families, fidelities, and evidence obligations.

Applications continue to own native objectives, suites, security rules, agent behavior, presentation meaning, and product gates. The generic optimizer does not become another RAG framework.

## Executable sandbox

The sandbox is a standalone **Go 1.23**, standard-library-only implementation. It contains:

- 42 Go files;
- approximately 3,743 nonblank lines of Go;
- 15 packages;
- 29 test functions;
- no external Go modules;
- no network, database, vector service, or model-provider dependency.

Implemented kernels include:

- finite distributions and Markov-kernel composition;
- generic monoids;
- lawful cartesian lenses;
- change actions and derivatives;
- acyclic dependency graphs and impact closure;
- effect and obligation semilattices;
- typed finite and dependent intervention spaces;
- architecture reindexing;
- exact paired experiments;
- a finite Blackwell-garbling checker;
- mergeable estimates and intervals;
- ordered decision gates;
- Pareto frontiers;
- an event-sourced campaign reducer;
- bounded state-space exploration;
- a hybrid lexical/vector RAG system;
- a companion TLA+ model target.

The sandbox can be reproduced with:

```sh
cd optfield-sandbox
./scripts/reproduce.sh
```

## Executed RAG optimization campaign

The reference campaign jointly varies indexing and query behavior:

- chunk width;
- chunk overlap;
- representation dimension;
- exact versus modeled approximate vector retrieval;
- candidate depth;
- lexical/vector fusion weight;
- reranking;
- admitted context count.

It evaluates **575 non-baseline candidate specifications** at mini fidelity, advances **56** to full fidelity, and advances **14** to final fidelity. Six candidates pass all gates and lie on the selected feasible Pareto frontier.

The promoted finite-model candidate uses:

```text
chunk words       18
chunk overlap      0
embedding dimension 16
vector mode        exact
candidate depth    6
fusion weight      0.55
reranking          enabled
context count      3
```

Relative to the paired toy baseline, it changes the approximation, relevance, and interaction effects while reusing the build artifact. The reported finite-model changes include:

| Metric | Baseline | Candidate | Paired change |
|---|---:|---:|---:|
| Mean reciprocal rank | 0.9036 | 1.0000 | +0.0964 |
| Context recall | 0.9427 | 1.0000 | +0.0573 |
| Answer support | 0.4378 | 0.7472 | +0.3095 |
| Exact-oracle agreement | 0.8737 | 1.0000 | +0.1263 |
| Modeled latency | 5.8365 | 12.1103 | +6.2739 |
| Build units | 788.6 | 788.6 | 0 |

The latency increase remains beneath the declared hard gate and is exposed as a Pareto tradeoff rather than hidden inside a scalar objective. These results characterize the deterministic toy corpus and campaign, not production retrieval quality.

## Verification status

The final build passed:

- all Go tests;
- `go vet ./...`;
- eight executable algebraic law checks;
- bounded campaign-state exploration reaching **477 states and 1,496 legal transitions** through depth nine;
- DOCX accessibility audit with zero high-, medium-, or low-severity findings;
- visual inspection of all 126 rendered pages;
- PDF structural preflight with no warnings;
- ZIP integrity checks;
- source-bundle SHA-256 verification.

The bundle includes `formal/Campaign.tla`, but TLC was not available and was not executed. The Go state-space checker is executed evidence for the included finite reducer model; it is not a replacement for a general proof or a production model with multiple workers, fairness assumptions, failures, and temporal deployment behavior.

