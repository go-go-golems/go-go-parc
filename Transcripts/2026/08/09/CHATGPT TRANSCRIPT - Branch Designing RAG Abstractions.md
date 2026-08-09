# Branch · Designing RAG Abstractions

- URL: https://chatgpt.com/c/6a7800b4-2720-83ea-913a-716e2738a8b6
- Created: 2026-08-09T04:23:17.054Z

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
>
> Think about where plugin interfaces / interfaces can come in handy to have a backbone that the actual cases can be grafted onto, keeping the core simple but providing strong semantics.

<details><summary>💭 Thinking</summary>

**Planning the thesis**

I’m locating the existing Chapter 21 materials, reviewing the relevant project context, and identifying the needed research and artifact formats. I’ll then build a self-contained thesis and executable sandbox around its mathematical architecture.

**Planned the thesis**

</details>

```unknown
bash -lc cat /home/oai/skills/pdfs/SKILL.md && printf '\n---DOCX---\n' && cat /home/oai/skills/docx/SKILL.md
```

I’ll develop Chapter 21 into a standalone categorical/probabilistic optimization theory, paired with a minimal plugin kernel, concrete RAG grafts, laws, tests, runnable Go examples, and thesis publications.

<details><summary>💭 Thinking</summary>

**Sharpening the framework**

I’m surveying categorical semantics for optimization, lenses, reverse differentiation, monoidal composition, open systems, and algebraic effects. I’ll distill these ideas into a minimal core supporting typed plugins, interventions, evaluation, and compositional workflows.

**Sharpened the framework**

**Formalizing composition**

I’m modeling campaigns as coalgebraic propose–evaluate–decide–update loops, with parameterized systems, lenses for interventions, effectful evaluation, typed capabilities, provenance, and compositional plugin interpreters.

**Formalized composition**

**Refining typed interfaces**

I’m keeping the core practical: parameterized stages compose through paired parameters, lenses express lawful interventions, and finite kernels model stochastic evaluation. I’ll place iterative feedback outside the minimal algebra and validate plugin laws through tests.

**Refined typed interfaces**

</details>

```unknown
bash -lc rm -rf /mnt/data/opfield_work && mkdir -p /mnt/data/opfield_work/repos /mnt/data/opfield_output && python - <<'PY'
from pathlib import Path
from zipfile import ZipFile
src=Path('/mnt/data/rag-ttc(2).zip')
out=Path('/mnt/data/opfield_work/repos')
with ZipFile(src) as z:
    for info in z.infolist():
        p=Path(info.filename)
        if p.is_absolute() or '..' in p.parts:
            raise SystemExit(f'unsafe path {info.filename}')
        t=out/p
        if info.is_dir():
            t.mkdir(parents=True, exist_ok=True)
        else:
            t.parent.mkdir(parents=True, exist_ok=True)
            with z.open(info) as r, open(t,'wb') as w:
                while b:=r.read(1024*1024): w.write(b)
print('done')
PY
find /mnt/data/opfield_work/repos -maxdepth 2 -type d | sort | sed -n '1,100p'
```

<details><summary>💭 Thinking</summary>

**Inspected thesis files and safely extracted Chapter 21 project content**

</details>

```json
{"search_query":[{"q":"site:arxiv.org \"Backprop as Functor\" Fong Spivak Tuyeras"},{"q":"site:arxiv.org category theory parameterized maps Para construction machine learning Gavranovic"},{"q":"site:arxiv.org \"Categories of Optics\" Riley"},{"q":"site:arxiv.org \"Markov categories\" Fritz"}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Searched 1 website**

</details>

```unknown
bash -lc cd /mnt/data/opfield_work/repos && for f in ragopt/pkg/candidate/*.go ragopt/pkg/eval/*.go ragopt/pkg/compare/*.go ragopt/pkg/gate/*.go ragopt/pkg/runstore/*.go; do echo "===== $f ====="; rg -n '^type |^func |^const \(' "$f" | head -120; done
```

The backbone is converging on free compositional plans, typed intervention optics, stochastic kernels and couplings, monoidal measurements, and evidence-driven campaign coalgebras. Plugins interpret declared generators rather than arbitrary callbacks.

<details><summary>💭 Thinking</summary>

**Inspected ragopt APIs, types, tools, and implemented static analysis demo and plugin registry plan**

</details>

```unknown
bash -lc set -euo pipefail
ROOT=/mnt/data/opfield_work/opfield
cat > "$ROOT/engine/executor.go" <<'EOF'
package engine

import (
    "context"
    "fmt"
    "time"

    "github.com/go-go-golems/opfield/core"
    "github.com/go-go-golems/opfield/plan"
    "github.com/go-go-golems/opfield/plugin"
)

type Executor struct{ Registry *plugin.Registry }

func (e Executor) Run(ctx context.Context,p *plan.Plan,inputs []core.Envelope) core.Execution{
    start:=time.Now()
    if e.Registry==nil{return done(core.Failed(core.StatusInfrastructureFailure,"registry","nil registry",false),start)}
    if err:=plan.Validate(p,e.Registry);err!=nil{return done(core.Failed(core.StatusInfrastructureFailure,"invalid_plan",err.Error(),false),start)}
    if err:=validateFrame(inputs,p.In);err!=nil{return done(core.Failed(core.StatusInfrastructureFailure,"input",err.Error(),false),start)}
    result:=e.run(ctx,p,inputs)
    if result.OK(){if err:=validateFrame(result.Outputs,p.Out);err!=nil{return done(core.Failed(core.StatusInfrastructureFailure,"output",err.Error(),false),start)}}
    result.Duration=time.Since(start)
    return result
}

func (e Executor) run(ctx context.Context,p *plan.Plan,inputs []core.Envelope) core.Execution{
    if err:=ctx.Err();err!=nil{return core.Failed(core.StatusCancelled,"context",err.Error(),false)}
    switch p.Kind{
    case plan.KindIdentity:return core.Success(cloneFrame(inputs)...)
    case plan.KindPrimitive:
        op,_:=e.Registry.Operation(p.Operation)
        result:=op.Execute(ctx,cloneFrame(inputs))
        for i:=range result.Observations{if result.Observations[i].Operation==""{result.Observations[i].Operation=p.Operation}}
        return result
    case plan.KindSequence:
        current:=cloneFrame(inputs);var obs []core.Observation;var arts []core.ArtifactRef
        for _,child:=range p.Children{r:=e.run(ctx,child,current);obs=append(obs,r.Observations...);arts=append(arts,r.Artifacts...);if !r.OK(){r.Observations=obs;r.Artifacts=arts;return r};current=r.Outputs}
        r:=core.Success(current...);r.Observations=obs;r.Artifacts=arts;return r
    case plan.KindTensor:
        offset:=0;var outputs []core.Envelope;var obs []core.Observation;var arts []core.ArtifactRef
        for _,child:=range p.Children{n:=len(child.In);r:=e.run(ctx,child,inputs[offset:offset+n]);offset+=n;obs=append(obs,r.Observations...);arts=append(arts,r.Artifacts...);if !r.OK(){r.Observations=obs;r.Artifacts=arts;return r};outputs=append(outputs,r.Outputs...)}
        r:=core.Success(outputs...);r.Observations=obs;r.Artifacts=arts;return r
    case plan.KindPermute:
        out:=make([]core.Envelope,len(inputs));for i,j:=range p.Permutation{out[i]=inputs[j]};return core.Success(out...)
    case plan.KindCopy:return core.Success(inputs[0],inputs[0])
    case plan.KindDrop:return core.Success()
    default:return core.Failed(core.StatusInfrastructureFailure,"plan_kind",fmt.Sprintf("unknown kind %s",p.Kind),false)
    }
}
func validateFrame(values []core.Envelope,port core.Port)error{if len(values)!=len(port){return fmt.Errorf("arity mismatch: got %d want %d",len(values),len(port))};for i,v:=range values{if v.Schema!=port[i]{return fmt.Errorf("wire %d schema got %s want %s",i,v.Schema,port[i])};if err:=v.Validate();err!=nil{return fmt.Errorf("wire %d: %w",i,err)}};return nil}
func cloneFrame(values []core.Envelope)[]core.Envelope{return append([]core.Envelope(nil),values...)}
func done(r core.Execution,start time.Time)core.Execution{r.Duration=time.Since(start);return r}
EOF
cat > "$ROOT/artifact/store.go" <<'EOF'
package artifact

import (
    "context"
    "encoding/json"
    "fmt"
    "os"
    "path/filepath"

    "github.com/go-go-golems/opfield/core"
)

type Ref struct { Digest core.Digest `json:"digest"`; MediaType string `json:"media_type"`; Size int64 `json:"size"` }
type Store interface{Put(context.Context,string,[]byte)(Ref,error);Get(context.Context,Ref)([]byte,error);Has(context.Context,core.Digest)(bool,error)}

type FileStore struct{Root string}
func NewFileStore(root string)(*FileStore,error){if root==""{return nil,fmt.Errorf("empty artifact root")};if err:=os.MkdirAll(root,0o755);err!=nil{return nil,err};return &FileStore{Root:root},nil}
func (s *FileStore) path(d core.Digest)string{return filepath.Join(s.Root,string(d)[7:]+".blob")}
func (s *FileStore) Put(ctx context.Context,media string,data []byte)(Ref,error){if err:=ctx.Err();err!=nil{return Ref{},err};d:=core.Sum("opfield/artifact/v1",[]byte(media),data);p:=s.path(d);if _,err:=os.Stat(p);err==nil{return Ref{Digest:d,MediaType:media,Size:int64(len(data))},nil};tmp,err:=os.CreateTemp(s.Root,".tmp-");if err!=nil{return Ref{},err};name:=tmp.Name();defer os.Remove(name);if _,err=tmp.Write(data);err==nil{err=tmp.Sync()};if closeErr:=tmp.Close();err==nil{err=closeErr};if err!=nil{return Ref{},err};if err=os.Rename(name,p);err!=nil{if _,stat:=os.Stat(p);stat!=nil{return Ref{},err}};return Ref{Digest:d,MediaType:media,Size:int64(len(data))},nil}
func (s *FileStore) Get(ctx context.Context,ref Ref)([]byte,error){if err:=ctx.Err();err!=nil{return nil,err};data,err:=os.ReadFile(s.path(ref.Digest));if err!=nil{return nil,err};d:=core.Sum("opfield/artifact/v1",[]byte(ref.MediaType),data);if d!=ref.Digest{return nil,fmt.Errorf("artifact digest mismatch")};return data,nil}
func (s *FileStore) Has(ctx context.Context,d core.Digest)(bool,error){if err:=ctx.Err();err!=nil{return false,err};_,err:=os.Stat(s.path(d));if err==nil{return true,nil};if os.IsNotExist(err){return false,nil};return false,err}
func PutJSON(ctx context.Context,s Store,media string,v any)(Ref,error){b,err:=core.CanonicalJSON(v);if err!=nil{return Ref{},err};return s.Put(ctx,media,b)}
func GetJSON[T any](ctx context.Context,s Store,ref Ref)(T,error){var z T;b,err:=s.Get(ctx,ref);if err!=nil{return z,err};if err=json.Unmarshal(b,&z);err!=nil{return z,err};return z,nil}
EOF
cat > "$ROOT/optic/lens.go" <<'EOF'
package optic

import "fmt"

type Lens[S, A any] struct{
    ID string
    Get func(S)A
    Put func(S,A)(S,error)
    EqualS func(S,S)bool
    EqualA func(A,A)bool
}
func Compose[S,A,B any](outer Lens[S,A],inner Lens[A,B],id string)Lens[S,B]{return Lens[S,B]{ID:id,Get:func(s S)B{return inner.Get(outer.Get(s))},Put:func(s S,b B)(S,error){a:=outer.Get(s);a2,err:=inner.Put(a,b);if err!=nil{return s,err};return outer.Put(s,a2)},EqualS:outer.EqualS,EqualA:inner.EqualA}}
func CheckLaws[S,A any](l Lens[S,A],states []S,values []A)error{
    if l.ID==""||l.Get==nil||l.Put==nil||l.EqualS==nil||l.EqualA==nil{return fmt.Errorf("incomplete lens")}
    for _,s:=range states{
        s2,err:=l.Put(s,l.Get(s));if err!=nil{return fmt.Errorf("get-put: %w",err)};if !l.EqualS(s,s2){return fmt.Errorf("get-put law failed")}
        for _,a:=range values{
            s3,err:=l.Put(s,a);if err!=nil{continue};if !l.EqualA(l.Get(s3),a){return fmt.Errorf("put-get law failed")}
            for _,b:=range values{s4,err:=l.Put(s3,b);if err!=nil{continue};s5,err:=l.Put(s,b);if err!=nil{continue};if !l.EqualS(s4,s5){return fmt.Errorf("put-put law failed")}}
        }
    }
    return nil
}
EOF
cat > "$ROOT/para/para.go" <<'EOF'
// Package para implements the Para construction for ordinary Go functions.
package para

type Pair[A,B any] struct{First A;Second B}
type Map[A,B any] func(A)(B,error)
type Parametric[P,A,B any] struct{Run func(P,A)(B,error)}
func Compose[P,Q,A,B,C any](f Parametric[P,A,B],g Parametric[Q,B,C])Parametric[Pair[P,Q],A,C]{return Parametric[Pair[P,Q],A,C]{Run:func(p Pair[P,Q],a A)(C,error){var z C;b,err:=f.Run(p.First,a);if err!=nil{return z,err};return g.Run(p.Second,b)}}}
func Reparameterize[R,P,A,B any](r Map[R,P],f Parametric[P,A,B])Parametric[R,A,B]{return Parametric[R,A,B]{Run:func(x R,a A)(B,error){var z B;p,err:=r(x);if err!=nil{return z,err};return f.Run(p,a)}}}
func Tensor[P,Q,A,B,C,D any](f Parametric[P,A,B],g Parametric[Q,C,D])Parametric[Pair[P,Q],Pair[A,C],Pair[B,D]]{return Parametric[Pair[P,Q],Pair[A,C],Pair[B,D]]{Run:func(p Pair[P,Q],x Pair[A,C])(Pair[B,D],error){var z Pair[B,D];b,err:=f.Run(p.First,x.First);if err!=nil{return z,err};d,err:=g.Run(p.Second,x.Second);if err!=nil{return z,err};return Pair[B,D]{b,d},nil}}}
EOF
cat > "$ROOT/prob/seed.go" <<'EOF'
package prob

import (
    "crypto/sha256"
    "encoding/binary"
    "math/rand"
)

type Seed [32]byte
func SeedFromString(value string)Seed{return sha256.Sum256([]byte("opfield/seed/v1\x00"+value))}
func (s Seed) Split(label string)Seed{h:=sha256.New();h.Write([]byte("opfield/seed/split/v1"));h.Write(s[:]);h.Write([]byte{0});h.Write([]byte(label));var out Seed;copy(out[:],h.Sum(nil));return out}
func (s Seed) Uint64()uint64{return binary.BigEndian.Uint64(s[:8])}
func (s Seed) Rand()*rand.Rand{return rand.New(rand.NewSource(int64(s.Uint64())))}
EOF
cat > "$ROOT/prob/finite.go" <<'EOF'
package prob

import (
    "fmt"
    "math"
)

type Dist[T comparable] map[T]float64
func NewDist[T comparable](weights map[T]float64)(Dist[T],error){sum:=0.0;for _,w:=range weights{if math.IsNaN(w)||math.IsInf(w,0)||w<0{return nil,fmt.Errorf("invalid weight")};sum+=w};if sum<=0{return nil,fmt.Errorf("zero mass")};out:=Dist[T]{};for x,w:=range weights{if w>0{out[x]=w/sum}};return out,nil}
func Pure[T comparable](x T)Dist[T]{return Dist[T]{x:1}}
func Bind[A,B comparable](d Dist[A],k func(A)Dist[B])Dist[B]{out:=Dist[B]{};for a,p:=range d{for b,q:=range k(a){out[b]+=p*q}};return out}
func Map[A,B comparable](d Dist[A],f func(A)B)Dist[B]{return Bind(d,func(a A)Dist[B]{return Pure(f(a))})}
func Product[A,B comparable](a Dist[A],b Dist[B])Dist[Pair[A,B]]{out:=Dist[Pair[A,B]]{};for x,p:=range a{for y,q:=range b{out[Pair[A,B]{x,y}]+=p*q}};return out}
type Pair[A,B comparable] struct{First A;Second B}
type Kernel[A,B comparable] func(A)Dist[B]
func Compose[A,B,C comparable](f Kernel[A,B],g Kernel[B,C])Kernel[A,C]{return func(a A)Dist[C]{return Bind(f(a),g)}}
func Tensor[A,B,C,D comparable](f Kernel[A,B],g Kernel[C,D])Kernel[Pair[A,C],Pair[B,D]]{return func(x Pair[A,C])Dist[Pair[B,D]]{return Product(f(x.First),g(x.Second))}}
func Equal[T comparable](a,b Dist[T],eps float64)bool{keys:=map[T]struct{}{};for k:=range a{keys[k]=struct{}{}};for k:=range b{keys[k]=struct{}{}};for k:=range keys{if math.Abs(a[k]-b[k])>eps{return false}};return true}
EOF

```

<details><summary>💭 Thinking</summary>

**Implemented game engines, policy selection, and campaign event resumption**

</details>

```unknown
bash -lc set -euo pipefail
ROOT=/mnt/data/opfield_work/opfield
cat > "$ROOT/domain/ragtoy/types.go" <<'EOF'
package ragtoy

import "github.com/go-go-golems/opfield/core"

const(
    SchemaSpec core.SchemaID="ragtoy.spec/v1"
    SchemaCorpus core.SchemaID="ragtoy.corpus/v1"
    SchemaChunks core.SchemaID="ragtoy.chunks/v1"
    SchemaIndex core.SchemaID="ragtoy.index/v1"
    SchemaCase core.SchemaID="ragtoy.case/v1"
    SchemaRetrieval core.SchemaID="ragtoy.retrieval/v1"
    SchemaTrial core.SchemaID="ragtoy.trial/v1"
    SchemaParameter core.SchemaID="ragtoy.parameter/v1"
)
const(
    OpChunk core.OperationID="ragtoy.chunk/v1"
    OpIndex core.OperationID="ragtoy.index/v1"
    OpRetrieve core.OperationID="ragtoy.retrieve/v1"
    OpMeasure core.OperationID="ragtoy.measure/v1"
)

type Spec struct{ChunkWords int `json:"chunk_words"`;OverlapWords int `json:"overlap_words"`;LexicalWeight float64 `json:"lexical_weight"`;VectorWeight float64 `json:"vector_weight"`;TopK int `json:"top_k"`}
type ParameterValue struct{Kind string `json:"kind"`;IntValue int `json:"int_value,omitempty"`;FloatValue float64 `json:"float_value,omitempty"`}
type Document struct{ID string `json:"id"`;Title string `json:"title"`;Text string `json:"text"`}
type Corpus struct{Documents []Document `json:"documents"`}
type Chunk struct{ID string `json:"id"`;DocumentID string `json:"document_id"`;Ordinal int `json:"ordinal"`;Text string `json:"text"`;Tokens []string `json:"tokens"`}
type ChunkSet struct{Chunks []Chunk `json:"chunks"`;ChunkWords int `json:"chunk_words"`;OverlapWords int `json:"overlap_words"`}
type IndexedChunk struct{Chunk Chunk `json:"chunk"`;TermFrequency map[string]float64 `json:"term_frequency"`;Vector []float64 `json:"vector"`}
type Index struct{Chunks []IndexedChunk `json:"chunks"`;DocumentFrequency map[string]int `json:"document_frequency"`;VectorDimension int `json:"vector_dimension"`}
type CaseInput struct{Query string `json:"query"`;RelevantDocuments []string `json:"relevant_documents"`}
type RankedDocument struct{DocumentID string `json:"document_id"`;Score float64 `json:"score"`;Lexical float64 `json:"lexical"`;Vector float64 `json:"vector"`;BestChunkID string `json:"best_chunk_id"`;Words int `json:"words"`}
type RetrievalResult struct{Query string `json:"query"`;RelevantDocuments []string `json:"relevant_documents"`;Ranked []RankedDocument `json:"ranked"`;ScoredChunks int `json:"scored_chunks"`}
type TrialOutput struct{Recall float64 `json:"recall"`;MRR float64 `json:"mrr"`;HitRate float64 `json:"hit_rate"`;ScoredChunks float64 `json:"scored_chunks"`;ContextWords float64 `json:"context_words"`;Ranked []RankedDocument `json:"ranked"`}
EOF
cat > "$ROOT/domain/ragtoy/algorithms.go" <<'EOF'
package ragtoy

import (
    "fmt"
    "hash/fnv"
    "math"
    "sort"
    "strings"
    "unicode"
)

const vectorDim=48
func validateSpec(s Spec)error{if s.ChunkWords<4||s.ChunkWords>200{return fmt.Errorf("chunk_words out of range")};if s.OverlapWords<0||s.OverlapWords>=s.ChunkWords{return fmt.Errorf("overlap_words out of range")};if !finiteNonnegative(s.LexicalWeight)||!finiteNonnegative(s.VectorWeight)||s.LexicalWeight+s.VectorWeight==0{return fmt.Errorf("invalid weights")};if s.TopK<1||s.TopK>20{return fmt.Errorf("top_k out of range")};return nil}
func finiteNonnegative(x float64)bool{return !math.IsNaN(x)&&!math.IsInf(x,0)&&x>=0}
func tokenize(text string)[]string{var out []string;var b strings.Builder;flush:=func(){if b.Len()>0{out=append(out,b.String());b.Reset()}};for _,r:=range strings.ToLower(text){if unicode.IsLetter(r)||unicode.IsDigit(r){b.WriteRune(r)}else{flush()}};flush();return out}
func chunkCorpus(spec Spec,corpus Corpus)(ChunkSet,error){if err:=validateSpec(spec);err!=nil{return ChunkSet{},err};var chunks []Chunk;step:=spec.ChunkWords-spec.OverlapWords;for _,doc:=range corpus.Documents{tokens:=tokenize(doc.Title+" "+doc.Text);for start,ord:=0,0;start<len(tokens);start,ord=start+step,ord+1{end:=start+spec.ChunkWords;if end>len(tokens){end=len(tokens)};part:=append([]string(nil),tokens[start:end]...);id:=fmt.Sprintf("%s:%04d:%04d",doc.ID,start,end);chunks=append(chunks,Chunk{ID:id,DocumentID:doc.ID,Ordinal:ord,Text:strings.Join(part," "),Tokens:part});if end==len(tokens){break}}};return ChunkSet{Chunks:chunks,ChunkWords:spec.ChunkWords,OverlapWords:spec.OverlapWords},nil}
func buildIndex(chunks ChunkSet)Index{df:=map[string]int{};indexed:=make([]IndexedChunk,0,len(chunks.Chunks));for _,c:=range chunks.Chunks{counts:=map[string]int{};for _,t:=range c.Tokens{counts[t]++};tf:=map[string]float64{};for t,n:=range counts{tf[t]=float64(n)/float64(len(c.Tokens));df[t]++};indexed=append(indexed,IndexedChunk{Chunk:c,TermFrequency:tf,Vector:vectorize(c.Tokens)})};return Index{Chunks:indexed,DocumentFrequency:df,VectorDimension:vectorDim}}
var concepts=map[string]string{"prune":"prune","pruning":"prune","trim":"prune","cut":"prune","acid":"acid","acidic":"acid","ericaceous":"acid","shade":"shade","shady":"shade","shadow":"shade","hedge":"hedge","hedging":"hedge","screen":"hedge","crimson":"red","scarlet":"red","red":"red","bee":"pollinator","bees":"pollinator","pollinator":"pollinator","pollinators":"pollinator","fragrant":"scent","scented":"scent","perfume":"scent","drought":"dry","dry":"dry","xeric":"dry"}
func semanticToken(t string)string{if c,ok:=concepts[t];ok{return c};return t}
func vectorize(tokens []string)[]float64{v:=make([]float64,vectorDim);for _,raw:=range tokens{t:=semanticToken(raw);addFeature(v,"tok:"+t,1);r:=[]rune(t);for i:=0;i+2<len(r);i++{addFeature(v,"tri:"+string(r[i:i+3]),0.25)}};norm:=0.0;for _,x:=range v{norm+=x*x};if norm>0{norm=math.Sqrt(norm);for i:=range v{v[i]/=norm}};return v}
func addFeature(v []float64,s string,weight float64){h:=fnv.New64a();_,_=h.Write([]byte(s));x:=h.Sum64();idx:=int(x%uint64(len(v)));sign:=1.0;if x&(1<<63)!=0{sign=-1};v[idx]+=sign*weight}
func dot(a,b []float64)float64{n:=len(a);if len(b)<n{n=len(b)};s:=0.0;for i:=0;i<n;i++{s+=a[i]*b[i]};return s}
func retrieve(index Index,spec Spec,c CaseInput)(RetrievalResult,error){if err:=validateSpec(spec);err!=nil{return RetrievalResult{},err};q:=tokenize(c.Query);qv:=vectorize(q);n:=float64(len(index.Chunks));type cs struct{doc,id string;lex,vec float64;words int};scores:=make([]cs,0,len(index.Chunks));maxLex,maxVec:=0.0,0.0;for _,ic:=range index.Chunks{lex:=0.0;for _,t:=range q{tf:=ic.TermFrequency[t];if tf==0{continue};idf:=math.Log(1+(n+1)/(float64(index.DocumentFrequency[t])+1));lex+=tf*idf};vec:=dot(qv,ic.Vector);if vec<0{vec=0};if lex>maxLex{maxLex=lex};if vec>maxVec{maxVec=vec};scores=append(scores,cs{doc:ic.Chunk.DocumentID,id:ic.Chunk.ID,lex:lex,vec:vec,words:len(ic.Chunk.Tokens)})};byDoc:=map[string]RankedDocument{};for _,x:=range scores{lex,vec:=x.lex,x.vec;if maxLex>0{lex/=maxLex};if maxVec>0{vec/=maxVec};score:=spec.LexicalWeight*lex+spec.VectorWeight*vec;prev,ok:=byDoc[x.doc];if !ok||score>prev.Score||(score==prev.Score&&x.id<prev.BestChunkID){byDoc[x.doc]=RankedDocument{DocumentID:x.doc,Score:score,Lexical:lex,Vector:vec,BestChunkID:x.id,Words:x.words}}};ranked:=make([]RankedDocument,0,len(byDoc));for _,x:=range byDoc{ranked=append(ranked,x)};sort.Slice(ranked,func(i,j int)bool{if ranked[i].Score!=ranked[j].Score{return ranked[i].Score>ranked[j].Score};return ranked[i].DocumentID<ranked[j].DocumentID});if len(ranked)>spec.TopK{ranked=ranked[:spec.TopK]};return RetrievalResult{Query:c.Query,RelevantDocuments:append([]string(nil),c.RelevantDocuments...),Ranked:ranked,ScoredChunks:len(index.Chunks)},nil}
func measure(r RetrievalResult)TrialOutput{rel:=map[string]struct{}{};for _,id:=range r.RelevantDocuments{rel[id]=struct{}{}};hits:=0;rr:=0.0;words:=0;for i,x:=range r.Ranked{words+=x.Words;if _,ok:=rel[x.DocumentID];ok{hits++;if rr==0{rr=1/float64(i+1)}}};recall:=0.0;if len(rel)>0{recall=float64(hits)/float64(len(rel))};hit:=0.0;if hits>0{hit=1};return TrialOutput{Recall:recall,MRR:rr,HitRate:hit,ScoredChunks:float64(r.ScoredChunks),ContextWords:float64(words),Ranked:r.Ranked}}
EOF
cat > "$ROOT/domain/ragtoy/plugin.go" <<'EOF'
package ragtoy

import (
    "context"

    "github.com/go-go-golems/opfield/core"
    "github.com/go-go-golems/opfield/optic"
    "github.com/go-go-golems/opfield/plugin"
)

type Plugin struct{}
func(Plugin)Manifest()plugin.Manifest{return plugin.Manifest{ID:"ragtoy",Version:"1.0.0",Description:"Deterministic miniature RAG domain"}}
func(Plugin)Install(b *plugin.Builder)error{
    schemas:=[]core.Schema{{SchemaSpec,"1","RAG build and query specification"},{SchemaCorpus,"1","document corpus"},{SchemaChunks,"1","derived chunks"},{SchemaIndex,"1","lexical and hashed-vector index"},{SchemaCase,"1","query and relevance labels"},{SchemaRetrieval,"1","ranked retrieval result"},{SchemaTrial,"1","trial metrics and ranked evidence"},{SchemaParameter,"1","typed intervention value"}}
    for _,s:=range schemas{if err:=b.RegisterSchema(s);err!=nil{return err}}
    spec:=plugin.JSONCodec[Spec]{ID:SchemaSpec};corpus:=plugin.JSONCodec[Corpus]{ID:SchemaCorpus};chunks:=plugin.JSONCodec[ChunkSet]{ID:SchemaChunks};index:=plugin.JSONCodec[Index]{ID:SchemaIndex};caseCodec:=plugin.JSONCodec[CaseInput]{ID:SchemaCase};retrieval:=plugin.JSONCodec[RetrievalResult]{ID:SchemaRetrieval};trial:=plugin.JSONCodec[TrialOutput]{ID:SchemaTrial}
    if err:=b.RegisterOperation(plugin.Binary[Spec,Corpus,ChunkSet]{Desc:core.OperationDescriptor{ID:OpChunk,Version:"1",Plugin:"ragtoy",Inputs:core.Port{SchemaSpec,SchemaCorpus},Outputs:core.Port{SchemaChunks},Effects:[]core.Effect{core.EffectCPU},Deterministic:true,Cacheable:true,Dependencies:[]string{"corpus.normalize","index.chunk"},Cost:core.CostHint{Work:2,CriticalPath:2}},A:spec,B:corpus,Out:chunks,Run:func(_ context.Context,s Spec,c Corpus)(ChunkSet,[]core.Observation,error){x,err:=chunkCorpus(s,c);return x,[]core.Observation{{Kind:"ragtoy.chunked",Attributes:map[string]string{"documents":itoa(len(c.Documents))}}},err}});err!=nil{return err}
    if err:=b.RegisterOperation(plugin.Unary[ChunkSet,Index]{Desc:core.OperationDescriptor{ID:OpIndex,Version:"1",Plugin:"ragtoy",Inputs:core.Port{SchemaChunks},Outputs:core.Port{SchemaIndex},Effects:[]core.Effect{core.EffectCPU,core.EffectArtifactWrite},Deterministic:true,Cacheable:true,Dependencies:[]string{"index.lexical","index.vector"},Cost:core.CostHint{Work:4,CriticalPath:4,MemoryBytes:1<<20}},In:chunks,Out:index,Run:func(_ context.Context,c ChunkSet)(Index,[]core.Observation,error){x:=buildIndex(c);return x,[]core.Observation{{Kind:"ragtoy.indexed",Attributes:map[string]string{"chunks":itoa(len(c.Chunks))}}},nil}});err!=nil{return err}
    if err:=b.RegisterOperation(plugin.Ternary[Index,Spec,CaseInput,RetrievalResult]{Desc:core.OperationDescriptor{ID:OpRetrieve,Version:"1",Plugin:"ragtoy",Inputs:core.Port{SchemaIndex,SchemaSpec,SchemaCase},Outputs:core.Port{SchemaRetrieval},Effects:[]core.Effect{core.EffectCPU,core.EffectArtifactRead},Deterministic:true,Cacheable:true,Dependencies:[]string{"query.channels","query.fusion","query.topk"},Cost:core.CostHint{Work:3,CriticalPath:3}},A:index,B:spec,C:caseCodec,Out:retrieval,Run:func(_ context.Context,i Index,s Spec,c CaseInput)(RetrievalResult,[]core.Observation,error){x,err:=retrieve(i,s,c);return x,[]core.Observation{{Kind:"ragtoy.retrieved",Attributes:map[string]string{"query":c.Query}}},err}});err!=nil{return err}
    if err:=b.RegisterOperation(plugin.Unary[RetrievalResult,TrialOutput]{Desc:core.OperationDescriptor{ID:OpMeasure,Version:"1",Plugin:"ragtoy",Inputs:core.Port{SchemaRetrieval},Outputs:core.Port{SchemaTrial},Effects:[]core.Effect{core.EffectCPU},Deterministic:true,Cacheable:true,Dependencies:[]string{"eval.retrieval"},Cost:core.CostHint{Work:1,CriticalPath:1}},In:retrieval,Out:trial,Run:func(_ context.Context,r RetrievalResult)(TrialOutput,[]core.Observation,error){return measure(r),[]core.Observation{{Kind:"ragtoy.measured"}},nil}});err!=nil{return err}
    return nil
}
func(Plugin)Laws()[]plugin.Law{return []plugin.Law{{Name:"specification lenses",Check:checkLensLaws}}}
func checkLensLaws()error{base:=DefaultSpec();states:=[]Spec{base,{ChunkWords:12,OverlapWords:2,LexicalWeight:.5,VectorWeight:1.5,TopK:4}};ints:=[]int{8,16,32};floats:=[]float64{.25,1,2};if err:=optic.CheckLaws(chunkLens(),states,ints);err!=nil{return err};if err:=optic.CheckLaws(overlapLens(),states,[]int{0,2,6});err!=nil{return err};if err:=optic.CheckLaws(lexicalLens(),states,floats);err!=nil{return err};if err:=optic.CheckLaws(vectorLens(),states,floats);err!=nil{return err};return optic.CheckLaws(topKLens(),states,[]int{1,3,5})}
func itoa(x int)string{if x==0{return "0"};b:=make([]byte,0,12);for x>0{b=append(b,byte('0'+x%10));x/=10};for i,j:=0,len(b)-1;i<j;i,j=i+1,j-1{b[i],b[j]=b[j],b[i]};return string(b)}
EOF

```

<details><summary>💭 Thinking</summary>

**Built and tested RAG plugin operations in Go**

</details>

```unknown
bash -lc set -euo pipefail
ROOT=/mnt/data/opfield_work/opfield
cat > "$ROOT/domain/quadratic/quadratic.go" <<'EOF'
package quadratic

import (
    "context"
    "fmt"
    "math"
    "time"

    "github.com/go-go-golems/opfield/core"
    "github.com/go-go-golems/opfield/decision"
    "github.com/go-go-golems/opfield/experiment"
    "github.com/go-go-golems/opfield/metric"
    "github.com/go-go-golems/opfield/plugin"
)
const(SchemaSpec core.SchemaID="quadratic.spec/v1";SchemaParameter core.SchemaID="quadratic.parameter/v1";SchemaCase core.SchemaID="quadratic.case/v1";SchemaOutput core.SchemaID="quadratic.output/v1")
type Spec struct{X float64 `json:"x"`;Noise float64 `json:"noise"`}
type Parameter struct{X float64 `json:"x"`}
type CaseInput struct{Target float64 `json:"target"`}
type Output struct{Loss float64 `json:"loss"`;X float64 `json:"x"`;Target float64 `json:"target"`}
type Space struct{}
func(Space)ID()string{return "quadratic.space/v1"};func(Space)Schema()core.SchemaID{return SchemaSpec}
func(Space)Baseline(context.Context)(core.Envelope,error){return plugin.JSONCodec[Spec]{ID:SchemaSpec}.Encode(Spec{X:0,Noise:.02})}
func(Space)Patches(_ context.Context,_ core.Envelope)([]experiment.Patch,error){codec:=plugin.JSONCodec[Parameter]{ID:SchemaParameter};var out []experiment.Patch;for _,x:=range []float64{1,2,3,4}{e,_:=codec.Encode(Parameter{X:x});out=append(out,experiment.Patch{ID:fmt.Sprintf("x-%.0f",x),Optic:"quadratic.spec.x",Value:e,Classes:[]experiment.SemanticClass{experiment.ClassRelevance},Targets:[]string{"model.parameter"},Closure:[]string{"model.parameter","eval.loss"},Hypothesis:"move x toward the target"})};return out,nil}
func(Space)Apply(_ context.Context,b core.Envelope,p experiment.Patch)(core.Envelope,error){s,err:=plugin.JSONCodec[Spec]{ID:SchemaSpec}.Decode(b);if err!=nil{return core.Envelope{},err};v,err:=plugin.JSONCodec[Parameter]{ID:SchemaParameter}.Decode(p.Value);if err!=nil{return core.Envelope{},err};if p.Optic!="quadratic.spec.x"||math.IsNaN(v.X)||math.IsInf(v.X,0){return core.Envelope{},fmt.Errorf("invalid patch")};s.X=v.X;return plugin.JSONCodec[Spec]{ID:SchemaSpec}.Encode(s)}
func Suite()(experiment.Suite,error){codec:=plugin.JSONCodec[CaseInput]{ID:SchemaCase};var cases []experiment.Case;for i,t:=range []float64{2.8,3.0,3.2}{e,_:=codec.Encode(CaseInput{Target:t});cases=append(cases,experiment.Case{ID:fmt.Sprintf("target-%d",i),Input:e})};return experiment.NewSuite("quadratic",cases)}
type Runner struct{}
func(Runner)ID()string{return "quadratic.runner/v1"};func(Runner)MetricDefinitions()[]metric.Definition{return []metric.Definition{{ID:"loss",Direction:metric.Minimize},{ID:"distance",Direction:metric.Minimize}}}
func(Runner)Run(_ context.Context,req experiment.TrialRequest)experiment.TrialResult{start:=time.Now().UTC();r:=experiment.TrialResult{Coordinate:req.Coordinate,StartedAt:start};s,err:=plugin.JSONCodec[Spec]{ID:SchemaSpec}.Decode(req.Spec);if err!=nil{return qfail(r,err)};c,err:=plugin.JSONCodec[CaseInput]{ID:SchemaCase}.Decode(req.Case.Input);if err!=nil{return qfail(r,err)};noise:=(req.Seed.Rand().Float64()*2-1)*s.Noise;distance:=math.Abs(s.X-c.Target);loss:=(s.X-c.Target)*(s.X-c.Target)+noise;out:=Output{Loss:loss,X:s.X,Target:c.Target};env,_:=plugin.JSONCodec[Output]{ID:SchemaOutput}.Encode(out);r.Output=&env;r.Metrics=metric.Vector{"loss":loss,"distance":distance};r.Status=core.StatusSuccess;r.FinishedAt=time.Now().UTC();return r}
func qfail(r experiment.TrialResult,err error)experiment.TrialResult{r.Status=core.StatusInfrastructureFailure;r.Failure=&core.Failure{Class:"decode",Message:err.Error()};r.FinishedAt=time.Now().UTC();return r}
func Policy()decision.Sequence{return decision.Sequence{PolicyID:"quadratic.policy/v1",Target:"loss",Gates:[]decision.Gate{decision.CoverageGate{RequireSuccess:true},decision.MeanDeltaGate{Metric:"loss",Minimum:0},decision.MeanDeltaGate{Metric:"distance",Minimum:0}}}}
EOF
cat > "$ROOT/cmd/opfield-demo/main.go" <<'EOF'
package main

import (
    "context"
    "encoding/json"
    "flag"
    "fmt"
    "log"
    "os"
    "path/filepath"

    "github.com/go-go-golems/opfield/artifact"
    "github.com/go-go-golems/opfield/campaign"
    "github.com/go-go-golems/opfield/core"
    "github.com/go-go-golems/opfield/domain/quadratic"
    "github.com/go-go-golems/opfield/domain/ragtoy"
    "github.com/go-go-golems/opfield/experiment"
    "github.com/go-go-golems/opfield/plan"
    "github.com/go-go-golems/opfield/plugin"
)
func main(){domain:=flag.String("domain","rag","rag or quadratic");out:=flag.String("out","./demo-out","output directory");reset:=flag.Bool("reset",false,"remove output before running");repeats:=flag.Int("repeats",2,"paired repeats");flag.Parse();if *reset{_ = os.RemoveAll(*out)};if err:=os.MkdirAll(*out,0o755);err!=nil{log.Fatal(err)};ctx:=context.Background();var result campaign.Result;var err error;switch *domain{case "rag":result,err=runRAG(ctx,*out,*repeats);case "quadratic":result,err=runQuadratic(ctx,*out,*repeats);default:log.Fatalf("unknown domain %q",*domain)};if err!=nil{log.Fatal(err)};raw,_:=json.MarshalIndent(result,"","  ");if err=os.WriteFile(filepath.Join(*out,"result.json"),raw,0o644);err!=nil{log.Fatal(err)};fmt.Println(string(raw))}
func runRAG(ctx context.Context,out string,repeats int)(campaign.Result,error){reg:=plugin.NewRegistry();if err:=reg.Register(ragtoy.Plugin{});err!=nil{return campaign.Result{},err};store,err:=artifact.NewFileStore(filepath.Join(out,"artifacts"));if err!=nil{return campaign.Result{},err};runner,err:=ragtoy.NewRunner(reg,store,ragtoy.SampleCorpus());if err!=nil{return campaign.Result{},err};suite,err:=ragtoy.SampleSuite();if err!=nil{return campaign.Result{},err};events,err:=campaign.NewJSONLStore(filepath.Join(out,"events.jsonl"));if err!=nil{return campaign.Result{},err};bp,qp:=runner.Plans();for name,p:=range map[string]*plan.Plan{"build":bp,"query":qp}{id,_:=plan.ID(p);analysis,_:=plan.Analyze(p,reg);raw,_:=core.CanonicalJSON(struct{ID core.Digest `json:"id"`;Analysis plan.Analysis `json:"analysis"`;Plan *plan.Plan `json:"plan"`}{id,analysis,p});_ = os.WriteFile(filepath.Join(out,name+"-plan.json"),raw,0o644)};engine:=campaign.Engine{Config:campaign.Config{Name:"ragtoy-composable-optimization",Repeats:repeats},Space:ragtoy.Space{},Proposer:experiment.AllPatches{},Workload:suite,Runner:runner,Policy:ragtoy.DefaultPolicy(),Store:events};return engine.Run(ctx)}
func runQuadratic(ctx context.Context,out string,repeats int)(campaign.Result,error){suite,err:=quadratic.Suite();if err!=nil{return campaign.Result{},err};events,err:=campaign.NewJSONLStore(filepath.Join(out,"events.jsonl"));if err!=nil{return campaign.Result{},err};engine:=campaign.Engine{Config:campaign.Config{Name:"quadratic-composable-optimization",Repeats:repeats},Space:quadratic.Space{},Proposer:experiment.AllPatches{},Workload:suite,Runner:quadratic.Runner{},Policy:quadratic.Policy(),Store:events};return engine.Run(ctx)}
EOF
cat > "$ROOT/Makefile" <<'EOF'
.PHONY: test demo-rag demo-quadratic clean

test:
	go test ./...

demo-rag:
	go run ./cmd/opfield-demo -domain rag -out ./demo-out/rag -reset

demo-quadratic:
	go run ./cmd/opfield-demo -domain quadratic -out ./demo-out/quadratic -reset

clean:
	rm -rf demo-out
EOF
cd "$ROOT"
gofmt -w .
go test ./...

```

The kernel now preserves static typing while controlling composition, effects, cost, and dependencies. A compiling RAG graft adds immutable-release realization, dependency-aware build reuse, deterministic paired trials, resumable campaigns, and promotion gates.

<details><summary>💭 Thinking</summary>

**Implemented and tested quadratic, RAG, plugin, and workflow integrations**

</details>

```unknown
bash -lc set -euo pipefail
ROOT=/mnt/data/opfield_work/opfield
cat > "$ROOT/plan/fold.go" <<'EOF'
package plan

import "github.com/go-go-golems/opfield/core"

// Algebra interprets the free typed wiring syntax into a semantic carrier R.
// Implementations must supply meanings for the categorical constructors and
// primitive generators. Fold is the unique structural recursion induced by
// those choices.
type Algebra[R any] interface {
    Identity(core.Port) (R, error)
    Primitive(core.OperationDescriptor) (R, error)
    Sequence(core.Port, core.Port, []R) (R, error)
    Tensor(core.Port, core.Port, []R) (R, error)
    Permute(core.Port, core.Port, []int) (R, error)
    Copy(core.SchemaID) (R, error)
    Drop(core.SchemaID) (R, error)
}

func Fold[R any](p *Plan, lookup DescriptorLookup, algebra Algebra[R]) (R, error) {
    var zero R
    if err := Validate(p, lookup); err != nil { return zero, err }
    var goFold func(*Plan) (R, error)
    goFold = func(n *Plan) (R, error) {
        switch n.Kind {
        case KindIdentity:
            return algebra.Identity(n.In)
        case KindPrimitive:
            d, _ := lookup.Descriptor(n.Operation)
            return algebra.Primitive(d)
        case KindSequence:
            children := make([]R, 0, len(n.Children))
            for _, child := range n.Children { x, err := goFold(child); if err != nil { return zero, err }; children = append(children, x) }
            return algebra.Sequence(n.In, n.Out, children)
        case KindTensor:
            children := make([]R, 0, len(n.Children))
            for _, child := range n.Children { x, err := goFold(child); if err != nil { return zero, err }; children = append(children, x) }
            return algebra.Tensor(n.In, n.Out, children)
        case KindPermute:
            return algebra.Permute(n.In, n.Out, n.Permutation)
        case KindCopy:
            return algebra.Copy(n.In[0])
        case KindDrop:
            return algebra.Drop(n.In[0])
        default:
            return zero, nil
        }
    }
    return goFold(p)
}
EOF
cat > "$ROOT/plan/analyze.go" <<'EOF'
package plan

import (
    "sort"

    "github.com/go-go-golems/opfield/core"
)

type Analysis struct {
    Operations    []core.OperationID `json:"operations"`
    Effects       []core.Effect      `json:"effects"`
    Dependencies  []string           `json:"dependencies"`
    Deterministic bool               `json:"deterministic"`
    Cacheable     bool               `json:"cacheable"`
    Cost          core.CostHint      `json:"cost"`
}

type analysisAlgebra struct{}
func (analysisAlgebra) Identity(core.Port)(Analysis,error){return Analysis{Deterministic:true,Cacheable:true},nil}
func (analysisAlgebra) Primitive(d core.OperationDescriptor)(Analysis,error){return Analysis{Operations:[]core.OperationID{d.ID},Effects:append([]core.Effect(nil),d.Effects...),Dependencies:append([]string(nil),d.Dependencies...),Deterministic:d.Deterministic,Cacheable:d.Cacheable,Cost:d.Cost},nil}
func (analysisAlgebra) Sequence(_ core.Port,_ core.Port,children []Analysis)(Analysis,error){return combine(children,false),nil}
func (analysisAlgebra) Tensor(_ core.Port,_ core.Port,children []Analysis)(Analysis,error){return combine(children,true),nil}
func (analysisAlgebra) Permute(core.Port,core.Port,[]int)(Analysis,error){return Analysis{Deterministic:true,Cacheable:true},nil}
func (analysisAlgebra) Copy(core.SchemaID)(Analysis,error){return Analysis{Deterministic:true,Cacheable:true},nil}
func (analysisAlgebra) Drop(core.SchemaID)(Analysis,error){return Analysis{Deterministic:true,Cacheable:true},nil}

func Analyze(p *Plan,lookup DescriptorLookup)(Analysis,error){return Fold(p,lookup,analysisAlgebra{})}
func combine(children []Analysis,parallel bool)Analysis{a:=Analysis{Deterministic:true,Cacheable:true};ops:=map[core.OperationID]struct{}{};effects:=map[core.Effect]struct{}{};deps:=map[string]struct{}{};for _,c:=range children{for _,x:=range c.Operations{ops[x]=struct{}{}};for _,x:=range c.Effects{effects[x]=struct{}{}};for _,x:=range c.Dependencies{deps[x]=struct{}{}};a.Deterministic=a.Deterministic&&c.Deterministic;a.Cacheable=a.Cacheable&&c.Cacheable;a.Cost.Work+=c.Cost.Work;a.Cost.Dollars+=c.Cost.Dollars;if parallel{a.Cost.CriticalPath=maxf(a.Cost.CriticalPath,c.Cost.CriticalPath);a.Cost.MemoryBytes+=c.Cost.MemoryBytes}else{a.Cost.CriticalPath+=c.Cost.CriticalPath;a.Cost.MemoryBytes=max64(a.Cost.MemoryBytes,c.Cost.MemoryBytes)}};for x:=range ops{a.Operations=append(a.Operations,x)};sort.Slice(a.Operations,func(i,j int)bool{return a.Operations[i]<a.Operations[j]});for x:=range effects{a.Effects=append(a.Effects,x)};sort.Slice(a.Effects,func(i,j int)bool{return a.Effects[i]<a.Effects[j]});for x:=range deps{a.Dependencies=append(a.Dependencies,x)};sort.Strings(a.Dependencies);return a}
func max64(a,b int64)int64{if a>b{return a};return b}
func maxf(a,b float64)float64{if a>b{return a};return b}
EOF
cat > "$ROOT/engine/executor.go" <<'EOF'
package engine

import (
    "context"
    "fmt"
    "time"

    "github.com/go-go-golems/opfield/core"
    "github.com/go-go-golems/opfield/plan"
    "github.com/go-go-golems/opfield/plugin"
)

type Arrow func(context.Context, []core.Envelope) core.Execution
type Compiled struct{In core.Port;Out core.Port;Run Arrow}
type executionAlgebra struct{registry *plugin.Registry}
func(executionAlgebra)Identity(p core.Port)(Compiled,error){return Compiled{In:p.Clone(),Out:p.Clone(),Run:func(_ context.Context,in []core.Envelope)core.Execution{return core.Success(cloneFrame(in)...)}},nil}
func(a executionAlgebra)Primitive(d core.OperationDescriptor)(Compiled,error){op,ok:=a.registry.Operation(d.ID);if !ok{return Compiled{},fmt.Errorf("unknown operation %s",d.ID)};return Compiled{In:d.Inputs.Clone(),Out:d.Outputs.Clone(),Run:func(ctx context.Context,in []core.Envelope)core.Execution{r:=op.Execute(ctx,cloneFrame(in));for i:=range r.Observations{if r.Observations[i].Operation==""{r.Observations[i].Operation=d.ID}};return r}},nil}
func(executionAlgebra)Sequence(in,out core.Port,children []Compiled)(Compiled,error){return Compiled{In:in.Clone(),Out:out.Clone(),Run:func(ctx context.Context,values []core.Envelope)core.Execution{current:=cloneFrame(values);var obs []core.Observation;var arts []core.ArtifactRef;for _,child:=range children{r:=child.Run(ctx,current);obs=append(obs,r.Observations...);arts=append(arts,r.Artifacts...);if !r.OK(){r.Observations=obs;r.Artifacts=arts;return r};current=r.Outputs};r:=core.Success(current...);r.Observations=obs;r.Artifacts=arts;return r}},nil}
func(executionAlgebra)Tensor(in,out core.Port,children []Compiled)(Compiled,error){return Compiled{In:in.Clone(),Out:out.Clone(),Run:func(ctx context.Context,values []core.Envelope)core.Execution{offset:=0;var outputs []core.Envelope;var obs []core.Observation;var arts []core.ArtifactRef;for _,child:=range children{n:=len(child.In);r:=child.Run(ctx,values[offset:offset+n]);offset+=n;obs=append(obs,r.Observations...);arts=append(arts,r.Artifacts...);if !r.OK(){r.Observations=obs;r.Artifacts=arts;return r};outputs=append(outputs,r.Outputs...)};r:=core.Success(outputs...);r.Observations=obs;r.Artifacts=arts;return r}},nil}
func(executionAlgebra)Permute(in,out core.Port,perm []int)(Compiled,error){return Compiled{In:in.Clone(),Out:out.Clone(),Run:func(_ context.Context,values []core.Envelope)core.Execution{x:=make([]core.Envelope,len(values));for i,j:=range perm{x[i]=values[j]};return core.Success(x...)}},nil}
func(executionAlgebra)Copy(schema core.SchemaID)(Compiled,error){return Compiled{In:core.Port{schema},Out:core.Port{schema,schema},Run:func(_ context.Context,in []core.Envelope)core.Execution{return core.Success(in[0],in[0])}},nil}
func(executionAlgebra)Drop(schema core.SchemaID)(Compiled,error){return Compiled{In:core.Port{schema},Out:nil,Run:func(_ context.Context,_ []core.Envelope)core.Execution{return core.Success()}},nil}

type Executor struct{Registry *plugin.Registry}
func(e Executor)Compile(p *plan.Plan)(Compiled,error){if e.Registry==nil{return Compiled{},fmt.Errorf("nil registry")};return plan.Fold(p,e.Registry,executionAlgebra{registry:e.Registry})}
func(e Executor)Run(ctx context.Context,p *plan.Plan,inputs []core.Envelope)core.Execution{start:=time.Now();compiled,err:=e.Compile(p);if err!=nil{return done(core.Failed(core.StatusInfrastructureFailure,"invalid_plan",err.Error(),false),start)};if err=validateFrame(inputs,compiled.In);err!=nil{return done(core.Failed(core.StatusInfrastructureFailure,"input",err.Error(),false),start)};if err=ctx.Err();err!=nil{return done(core.Failed(core.StatusCancelled,"context",err.Error(),false),start)};result:=compiled.Run(ctx,inputs);if result.OK(){if err=validateFrame(result.Outputs,compiled.Out);err!=nil{return done(core.Failed(core.StatusInfrastructureFailure,"output",err.Error(),false),start)}};result.Duration=time.Since(start);return result}
func validateFrame(values []core.Envelope,port core.Port)error{if len(values)!=len(port){return fmt.Errorf("arity mismatch: got %d want %d",len(values),len(port))};for i,v:=range values{if v.Schema!=port[i]{return fmt.Errorf("wire %d schema got %s want %s",i,v.Schema,port[i])};if err:=v.Validate();err!=nil{return fmt.Errorf("wire %d: %w",i,err)}};return nil}
func cloneFrame(values []core.Envelope)[]core.Envelope{return append([]core.Envelope(nil),values...)}
func done(r core.Execution,start time.Time)core.Execution{r.Duration=time.Since(start);return r}
EOF
# fix Seq constructor type checking before identity elimination
python - <<'PY'
from pathlib import Path
p=Path('/mnt/data/opfield_work/opfield/plan/plan.go')
s=p.read_text()
old='''\tcompact := flat[:0]\n\tfor _, p := range flat {\n\t\tif p.Kind == KindIdentity {\n\t\t\tcontinue\n\t\t}\n\t\tcompact = append(compact, p)\n\t}\n\tflat = compact\n'''
new='''\tfor i := 1; i < len(flat); i++ {\n\t\tif !flat[i-1].Out.Equal(flat[i].In) {\n\t\t\treturn nil, fmt.Errorf("sequence type mismatch %s -> %s", flat[i-1].Out, flat[i].In)\n\t\t}\n\t}\n\tcompact := flat[:0]\n\tfor _, p := range flat {\n\t\tif p.Kind == KindIdentity {\n\t\t\tcontinue\n\t\t}\n\t\tcompact = append(compact, p)\n\t}\n\tflat = compact\n'''
if old not in s: raise SystemExit('seq block not found')
s=s.replace(old,new)
# remove duplicate later compatibility loop
old2='''\tfor i := 1; i < len(flat); i++ {\n\t\tif !flat[i-1].Out.Equal(flat[i].In) {\n\t\t\treturn nil, fmt.Errorf("sequence type mismatch %s -> %s", flat[i-1].Out, flat[i].In)\n\t\t}\n\t}\n'''
# remove only second occurrence
idx=s.find(old2, s.find(new)+len(new))
if idx!=-1:s=s[:idx]+s[idx+len(old2):]
p.write_text(s)
PY
cd "$ROOT" && gofmt -w . && go test ./...
```

<details><summary>💭 Thinking</summary>

**Integrating the architecture**

I’m assembling the thesis around a small typed composition core, then attaching RAG and quadratic optimization domains through shared interfaces. The implementation emphasizes lawful composition, stochastic evaluation, provenance, comparison, and resumable campaigns.

**Finishing quality checks**

I’m moving from construction to verification: running tests, race checks, static analysis, and coverage; correcting canonicalization or fold edge cases; then documenting, rendering, and packaging the thesis and sandbox reproducibly.

**Integrated the architecture and finished quality checks**

</details>

```unknown
bash -lc set -euo pipefail
cd /mnt/data/opfield_work/opfield
printf '%s
' '--- tree ---'
find . -maxdepth 3 -type f | sort | sed -n '1,260p'
printf '%s
' '--- canonical ---'
sed -n '1,240p' core/canonical.go
printf '%s
' '--- go test ---'
go test ./...
```

<details><summary>💭 Thinking</summary>

**Implemented typed plan folding, JSON validation, and keyed schema fixes**

</details>

```unknown
bash -lc cd /mnt/data/opfield_work/opfield
for f in \
 core/effect.go core/envelope.go core/outcome.go \
 plugin/plugin.go plugin/typed.go \
 plan/plan.go plan/fold.go plan/analyze.go plan/validate.go \
 engine/executor.go \
 optic/lens.go para/para.go prob/finite.go \
 experiment/types.go decision/decision.go \
 campaign/engine.go campaign/event.go campaign/state.go campaign/store.go \
 domain/ragtoy/types.go domain/ragtoy/space.go domain/ragtoy/runner.go domain/ragtoy/policy.go \
 domain/quadratic/quadratic.go cmd/opfield-demo/main.go; do
  echo "===== $f ====="
  sed -n '1,320p' "$f"
  echo
done
```

<details><summary>💭 Thinking</summary>

**Inspected, tested, documented, and ran optimization field campaign architecture**

</details>

```json
{"search_query":[{"q":"site:arxiv.org \"Backprop as Functor\" Fong Spivak Tuyeras"},{"q":"site:arxiv.org \"Categorical Foundations of Gradient-Based Learning\""},{"q":"site:arxiv.org \"Categories of Optics\" Mitchell Riley"},{"q":"site:arxiv.org \"Free gs-monoidal categories and free Markov categories\""}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Searched 8 websites**

</details>

```unknown
bash -lc set -euo pipefail
mkdir -p /mnt/data/opfield_work/thesis/figures /mnt/data/opfield_work/thesis/data /mnt/data/opfield_work/thesis/qa
cat > /mnt/data/opfield_work/thesis/make_figures.py <<'PY'
from pathlib import Path
import subprocess, csv, os
import matplotlib.pyplot as plt
import numpy as np

OUT=Path('/mnt/data/opfield_work/thesis/figures')
OUT.mkdir(parents=True,exist_ok=True)
NAVY='#17324d'; BLUE='#2d5f87'; TEAL='#2e7d77'; LIGHT='#edf3f6'; MID='#c7d6df'; ORANGE='#c06b2c'; RED='#9f3a38'; GREEN='#3f7d4a'; GRAY='#5f6b73'; WHITE='#ffffff'; DARK='#1f2933'; PURPLE='#66558c'; YELLOW='#f4e8bd'

def dot(name, body, rankdir='TB'):
    src=f'''digraph G {{
      graph [fontname="Lato", bgcolor="transparent", pad="0.22", nodesep="0.45", ranksep="0.60", splines=ortho, rankdir={rankdir}];
      node [fontname="Lato", fontsize=10.5, shape=box, style="rounded,filled", color="{BLUE}", fontcolor="{DARK}", fillcolor="{LIGHT}", penwidth=1.2, margin="0.13,0.09"];
      edge [fontname="Lato", fontsize=9, color="{GRAY}", fontcolor="{GRAY}", arrowsize=0.7, penwidth=1.2];
      {body}
    }}'''
    p=OUT/f'{name}.dot'; p.write_text(src)
    subprocess.run(['dot','-Tpng','-Gdpi=220',str(p),'-o',str(OUT/f'{name}.png')],check=True)
    subprocess.run(['dot','-Tsvg',str(p),'-o',str(OUT/f'{name}.svg')],check=True)

# 1 doctrine stack
dot('01_optimization_doctrine', f'''
subgraph cluster_math {{ label="Mathematical doctrine"; color="{MID}"; style="rounded,dashed";
  wiring [label="Free typed wiring\nsequence ; tensor ⊗ ; copy ; discard", fillcolor="#e9f1f8", color="{BLUE}", penwidth=2];
  para [label="Para(C)\nparameterized systems"];
  optics [label="Lawful optics\nlocal interventions", fillcolor="#f4eef8", color="{PURPLE}"];
  stoch [label="Markov kernels\nstochastic trials", fillcolor="#eef6f5", color="{TEAL}"];
  order [label="Preorders / resource monoids\nconstraints, Pareto, cost", fillcolor="#f8f5ec", color="{ORANGE}"];
  coalgebra [label="Coalgebra / transition system\ncampaign dynamics", fillcolor="#eef6eb", color="{GREEN}"];
}}
subgraph cluster_software {{ label="Executable architecture"; color="{MID}"; style="rounded,dashed";
  signatures [label="schemas + operation descriptors"];
  plans [label="plans + folds"];
  plugins [label="plugin registry + laws"];
  experiments [label="spaces + runners + workloads"];
  campaign [label="paired cells + event store + gates"];
}}
wiring -> para; wiring -> stoch; para -> optics; stoch -> order; optics -> order; order -> coalgebra;
wiring -> plans [style=dashed]; signatures -> plans; plugins -> signatures; para -> experiments [style=dashed]; optics -> experiments [style=dashed]; stoch -> experiments [style=dashed]; coalgebra -> campaign [style=dashed]; order -> campaign [style=dashed]; experiments -> campaign;
''')

# 2 free plan interpreters
dot('02_free_plan_interpreters', f'''
plugins [label="Plugin signature Σ\ntyped primitive generators", fillcolor="#fff3e8", color="{ORANGE}"];
free [label="Free wiring category W(Σ)\nserializable Plan AST", fillcolor="#e9f1f8", color="{BLUE}", penwidth=2.2];
fold [label="Fold / universal extension", fillcolor="#f4eef8", color="{PURPLE}"];
exec [label="Execution\neffectful arrows"];
analysis [label="Static analysis\neffects + dependencies + resources"];
identity [label="Identity\ncanonical plan digest"];
graph [label="Visualization / deployment\nadditional interpreters"];
plugins -> free; free -> fold; fold -> exec; fold -> analysis; fold -> identity; fold -> graph;
''', 'LR')

# 3 plugin surfaces
dot('03_plugin_surfaces', f'''
core [label="Minimal kernel\ncomposition • identity • custody • pairing • order", fillcolor="#e8f2f0", color="{TEAL}", penwidth=2.2];
low [label="Low-level operation plugin\nschemas • generators • codecs • laws", fillcolor="#edf3f8", color="{BLUE}"];
high [label="High-level domain graft\nSpace • Proposer • Workload • Runner • Policy", fillcolor="#f4eef8", color="{PURPLE}"];
app [label="Existing application / RAG engine\nproduct semantics and native artifacts", fillcolor="#fff8e8", color="{ORANGE}"];
interpreters [label="Kernel interpreters\nexecute • analyze • identify • visualize"];
campaign [label="Campaign machine\nexact cells • resume • gates"];
low -> core [label="extends signature"];
high -> core [label="implements ports"];
app -> high [label="anti-corruption adapter"];
core -> interpreters; core -> campaign;
low -> interpreters [style=dashed]; high -> campaign [style=dashed];
''', 'LR')

# 4 Para
dot('04_para_composition', f'''
subgraph cluster_f {{ label="f"; color="{MID}"; style=rounded; p [label="P\nparameters", fillcolor="#f4eef8", color="{PURPLE}"]; a [label="A\ninput"]; f [label="f : P ⊗ A → B", fillcolor="#e9f1f8", color="{BLUE}"]; b [label="B"]; p->f; a->f; f->b; }}
subgraph cluster_g {{ label="g"; color="{MID}"; style=rounded; q [label="Q\nparameters", fillcolor="#f4eef8", color="{PURPLE}"]; g [label="g : Q ⊗ B → C", fillcolor="#eef6f5", color="{TEAL}"]; c [label="C"]; q->g; b->g; g->c; }}
composite [label="g ∘ f has parameter object P ⊗ Q\nparameters follow wiring", fillcolor="#eef6eb", color="{GREEN}", penwidth=2];
p -> composite [style=dashed]; q -> composite [style=dashed]; composite -> c [style=dashed];
''', 'LR')

# 5 optics and dependency closure
dot('05_optic_dependency_closure', f'''
release [label="Global release specification Θ", fillcolor="#e9f1f8", color="{BLUE}"];
optic [label="Lawful optic / lens\nfocus: vector_weight", fillcolor="#f4eef8", color="{PURPLE}", penwidth=2];
value [label="typed value 1.75"];
patched [label="Candidate Θ′"];
target [label="direct target\nquery.fusion", fillcolor="#fff8e8", color="{ORANGE}"];
closure [label="dependency closure\nquery.topk → eval.retrieval → answer/session", fillcolor="#eef6f5", color="{TEAL}"];
reuse [label="unaffected build artifacts reused", fillcolor="#eef6eb", color="{GREEN}"];
release -> optic; value -> optic; optic -> patched; optic -> target; target -> closure; patched -> reuse [style=dashed];
''', 'LR')

# 6 stochastic paired coupling
dot('06_paired_markov_coupling', f'''
case [label="case xᵢ"];
seed [label="shared seed / coupling ωᵢᵣ", fillcolor="#f4eef8", color="{PURPLE}"];
base [label="K_θ(xᵢ, ωᵢᵣ)\nbaseline outcome", fillcolor="#edf3f8", color="{BLUE}"];
cand [label="K_θ′(xᵢ, ωᵢᵣ)\ncandidate outcome", fillcolor="#eef6f5", color="{TEAL}"];
delta [label="oriented paired difference Δᵢᵣ", fillcolor="#eef6eb", color="{GREEN}", penwidth=2];
case -> base; case -> cand; seed -> base; seed -> cand; base -> delta; cand -> delta;
independent [label="independent draws increase variance\nand weaken attribution", fillcolor="#fbeeee", color="{RED}"];
independent -> delta [style=dotted, arrowhead=tee, color="{RED}"];
''', 'LR')

# 7 decision order
dot('07_constraint_pareto_decision', f'''
candidates [label="candidate evidence"];
security [label="1. security / integrity", fillcolor="#fbeeee", color="{RED}"];
coverage [label="2. complete paired coverage"];
quality [label="3. protected quality noninferiority"];
resources [label="4. latency / cost / capacity envelope", fillcolor="#fff8e8", color="{ORANGE}"];
pareto [label="5. Pareto frontier", fillcolor="#eef6f5", color="{TEAL}"];
preference [label="6. target or human preference", fillcolor="#eef6eb", color="{GREEN}", penwidth=2];
reject [label="reject / indeterminate", fillcolor="#fbeeee", color="{RED}"];
candidates -> security -> coverage -> quality -> resources -> pareto -> preference;
security -> reject [label="fail", style=dashed]; coverage -> reject [label="fail", style=dashed]; quality -> reject [label="fail", style=dashed]; resources -> reject [label="fail", style=dashed];
''', 'LR')

# 8 campaign state machine
dot('08_campaign_state_machine', f'''
start [label="not started"];
started [label="started"];
registered [label="candidates registered"];
trials [label="paired trials in progress"];
compared [label="reports recorded"];
decided [label="gate decisions recorded"];
terminal [label="terminal / immutable", fillcolor="#eef6eb", color="{GREEN}", penwidth=2];
interrupted [label="process interruption", fillcolor="#fff8e8", color="{ORANGE}"];
start -> started [label="campaign.started"];
started -> registered [label="candidate.registered*"];
registered -> trials [label="trial.completed*"];
trials -> compared [label="comparison.recorded*"];
compared -> decided [label="decision.recorded*"];
decided -> terminal [label="campaign.completed"];
trials -> interrupted [style=dashed]; compared -> interrupted [style=dashed]; interrupted -> trials [label="replay + continue", style=dashed];
terminal -> terminal [label="rerun is read-only"];
''', 'LR')

# 9 event sourcing
dot('09_event_sourced_resume', f'''
commands [label="campaign commands\nnext missing semantic action"];
append [label="conditional append\nimmutable event"];
log [label="events.jsonl / durable ledger", shape=cylinder, fillcolor="#edf3f8", color="{BLUE}"];
reduce [label="pure reducer", fillcolor="#eef6f5", color="{TEAL}"];
state [label="campaign state\nmissing cells • reports • decisions"];
crash [label="crash / restart", fillcolor="#fbeeee", color="{RED}"];
commands -> append -> log -> reduce -> state -> commands;
crash -> log [style=dashed]; log -> state [label="replay", style=dashed];
''', 'LR')

# 10 package architecture
dot('10_package_architecture', f'''
subgraph cluster_kernel {{ label="kernel"; color="{MID}"; style="rounded,dashed";
 core [label="core"];
 plugin [label="plugin"];
 plan [label="plan"];
 engine [label="engine"];
 artifact [label="artifact"];
}}
subgraph cluster_math {{ label="mathematical adapters"; color="{MID}"; style="rounded,dashed";
 para [label="para"];
 optic [label="optic"];
 prob [label="prob"];
 metric [label="metric"];
}}
subgraph cluster_campaign {{ label="optimization protocol"; color="{MID}"; style="rounded,dashed";
 experiment [label="experiment"];
 decision [label="decision"];
 campaign [label="campaign", fillcolor="#eef6eb", color="{GREEN}"];
}}
subgraph cluster_domains {{ label="grafts"; color="{MID}"; style="rounded,dashed";
 rag [label="domain/ragtoy", fillcolor="#edf3f8", color="{BLUE}"];
 quad [label="domain/quadratic", fillcolor="#f4eef8", color="{PURPLE}"];
}}
core -> plugin; core -> plan; plugin -> engine; plan -> engine; core -> artifact;
core -> experiment; prob -> experiment; metric -> experiment; experiment -> decision; experiment -> campaign; decision -> campaign;
para -> rag [style=dashed]; optic -> rag; plan -> rag; engine -> rag; artifact -> rag; campaign -> rag [dir=back];
experiment -> quad; decision -> quad; campaign -> quad [dir=back];
''')

# 11 RAG dependency graft
dot('11_rag_dependency_graft', f'''
corpus [label="Corpus", fillcolor="#edf3f8", color="{BLUE}"];
chunk [label="chunk(spec, corpus)"];
index [label="index(chunks)"];
retrieve [label="retrieve(index, query spec, case)"];
measure [label="measure(retrieval)"];
metrics [label="trial metrics + native artifact", fillcolor="#eef6eb", color="{GREEN}"];
corpus -> chunk -> index -> retrieve -> measure -> metrics;
chunkparam [label="chunk / overlap patch", fillcolor="#fff8e8", color="{ORANGE}"];
queryparam [label="fusion / top-k patch", fillcolor="#f4eef8", color="{PURPLE}"];
chunkparam -> chunk; queryparam -> retrieve;
cache [label="content-addressed build cache\nkey excludes query-only parameters", fillcolor="#eef6f5", color="{TEAL}"];
index -> cache [dir=both];
''', 'LR')

# 12 two domains
dot('12_two_domain_grafts', f'''
core [label="same campaign kernel\nSpace • Workload • Runner • Policy • Store", fillcolor="#e8f2f0", color="{TEAL}", penwidth=2.2];
rag [label="RAG graft\n7 interventions × 9 cases × 3 repeats\nselected: larger chunks", fillcolor="#edf3f8", color="{BLUE}"];
quad [label="Quadratic graft\n4 interventions × 3 targets × 4 repeats\nselected: x = 3", fillcolor="#f4eef8", color="{PURPLE}"];
plans [label="uses typed operation plans\nand content-addressed artifacts"];
plain [label="uses direct domain runner\nno plan/plugin dependency"];
rag -> core; quad -> core; rag -> plans; quad -> plain;
''', 'LR')

# 13 assurance ladder
dot('13_assurance_ladder', f'''
unit [label="unit tests"];
property [label="property / law tests"];
differential [label="differential domain fixtures"];
state [label="state-machine / model checking"];
statistical [label="paired statistical evidence"];
shadow [label="shadow / canary"];
proof [label="selective formal proof", fillcolor="#eef6eb", color="{GREEN}"];
unit -> property -> differential -> state -> statistical -> shadow;
property -> proof [style=dashed]; state -> proof [style=dashed];
caption [label="Different claims require different evidence;\nformal structure does not replace empirical evaluation.", shape=note, fillcolor="#fff8e8", color="{ORANGE}"];
caption -> statistical [style=dotted, arrowhead=none];
''', 'LR')

# 14 mapping current to target
dot('14_ragopt_ragkit_mapping', f'''
ragkit [label="ragkit\nRAG domain operations and releases", fillcolor="#edf3f8", color="{BLUE}"];
ragopt [label="ragopt\nrun custody, pairing, gates", fillcolor="#eef6eb", color="{GREEN}"];
current [label="Current overlap\nad hoc candidate spaces and adapters", fillcolor="#fff0e6", color="{ORANGE}"];
opfield [label="Optimization-field backbone\nfree plans + Para + optics + kernels + campaign", fillcolor="#e8f2f0", color="{TEAL}", penwidth=2.2];
ragspace [label="ragopt/ragspace adapter\ntyped interventions + dependency closure"];
products [label="GEC / TTC / Garden\nproduct-native runners and artifacts", fillcolor="#f4eef8", color="{PURPLE}"];
current -> opfield [label="formalize"];
opfield -> ragspace; ragkit -> ragspace; ragopt -> ragspace; products -> ragspace [label="graft"];
''', 'LR')

# 15 empirical implementation metrics
root=Path('/mnt/data/opfield_work/opfield')
packages=[]
for d in sorted([p for p in root.iterdir() if p.is_dir() and p.name not in {'.git','demo-out','examples','docs','scripts','cmd','domain'}]):
    files=list(d.glob('*.go'))
    if not files: continue
    loc=sum(sum(1 for line in f.read_text().splitlines() if line.strip()) for f in files)
    tests=sum(f.read_text().count('func Test') for f in files)
    packages.append((d.name,loc,tests))
# add domains and command
for name,path in [('ragtoy',root/'domain/ragtoy'),('quadratic',root/'domain/quadratic')]:
    files=list(path.glob('*.go')); loc=sum(sum(1 for line in f.read_text().splitlines() if line.strip()) for f in files); tests=sum(f.read_text().count('func Test') for f in files); packages.append((name,loc,tests))
packages.sort(key=lambda x:x[1], reverse=True)
with open('/mnt/data/opfield_work/thesis/data/implementation_metrics.csv','w',newline='') as f:
    w=csv.writer(f); w.writerow(['package','nonblank_go_lines','tests']); w.writerows(packages)
names=[x[0] for x in packages]; loc=[x[1] for x in packages]; tests=[x[2] for x in packages]
y=np.arange(len(names))
fig,ax=plt.subplots(figsize=(10.5,6.5))
ax.barh(y,loc,color=BLUE,label='nonblank Go lines')
ax.set_yticks(y,names); ax.invert_yaxis(); ax.set_xlabel('Nonblank Go lines'); ax.set_title('Reference implementation by package')
for i,v in enumerate(loc): ax.text(v+5,i,str(v),va='center',fontsize=8)
ax.grid(axis='x',alpha=.25)
ax2=ax.twiny(); ax2.scatter(tests,y,color=ORANGE,s=24,label='test functions'); ax2.set_xlabel('Test functions')
fig.tight_layout(); fig.savefig(OUT/'15_implementation_metrics.png',dpi=220,bbox_inches='tight'); fig.savefig(OUT/'15_implementation_metrics.svg',bbox_inches='tight'); plt.close(fig)
print('generated',len(list(OUT.glob('*.png'))),'PNG figures')
PY
python /mnt/data/opfield_work/thesis/make_figures.py
ls -lh /mnt/data/opfield_work/thesis/figures/*.png
cat /mnt/data/opfield_work/thesis/data/implementation_metrics.csv
```

<details><summary>💭 Thinking</summary>

**Generated thesis figures, analyzed images, and calculated repository metrics**

</details>

```unknown
bash -lc cat > /mnt/data/opfield_work/thesis/A_Categorical_Backbone_for_Composable_Optimization.md <<'EOF'
---
title: "A Categorical Backbone for Composable Optimization"
subtitle: "Parameterized Systems, Lawful Interventions, Stochastic Experiments, and Plugin Interpreters"
author: "A doctoral-style architecture study and executable reference implementation"
date: "August 2026"
lang: en-US
---

# Abstract {-}

Optimization software is usually organized around loops: propose a configuration, run an evaluation, compare measurements, and retain a winner. This description is operationally recognizable but mathematically weak. It says little about how optimized systems compose, how parameters follow composition, how a local intervention changes a global configuration, how stochastic trials should be paired, how effects and resources propagate, how a plugin can extend the field without redefining its laws, or how an interrupted campaign resumes without changing its meaning. In retrieval-augmented generation, these omissions become acute. A candidate can alter corpus admission, chunking, representations, embeddings, index structure, query rewriting, filtering, fusion, reranking, context selection, generation, agent policy, deadlines, caches, or frontend presentation. Each intervention invalidates a different portion of the system and requires a different level of evidence. A flat parameter dictionary and a generic callback loop cannot express this causal structure reliably.

This thesis develops a categorical and probabilistic backbone for a composable optimization field. The construction is deliberately layered. A typed signature describes domain objects and primitive operations. Its free wiring syntax provides sequential composition, monoidal product, permutation, explicit copying, and explicit discarding. Plugins contribute generators and laws, not new composition rules. Every interpretation of a plan—execution, static effect analysis, dependency analysis, resource estimation, identity, provenance, visualization, or deployment—is induced by a structure-preserving fold. Parameterized systems are modeled through the Para construction: a system from $A$ to $B$ with parameter object $P$ is represented by a morphism $P \otimes A \to B$, and composition tensors parameter objects rather than collecting unrelated strings in a global map. Lawful lenses and more general optics identify local views of a release specification; patches become typed interventions with direct targets, transitive dependency closure, semantic class, and hypothesis.

Stochastic evaluation is modeled with Markov kernels. For parameter $\theta$, a trial is a kernel $K_\theta : X \rightsquigarrow O$ from cases and environment to distributions over outcomes. Paired comparison is therefore a coupling problem, not merely two independent samples. The executable reference uses deterministic, domain-separated seed splitting to provide a common-random-number coupling and exact case/repeat coordinates; a production realization can strengthen this with retained provider responses or explicit coupling kernels. Metrics define oriented preorders rather than a universal scalar field. Hard constraints determine eligibility, Pareto dominance determines partial preference, and lexicographic gates encode policy without pretending that recall, dollars, latency, disclosure, and reliability share a natural additive unit.

An optimization campaign is modeled as an open state-transition system and, equivalently at a high level, a coalgebra whose observations are immutable events. The event reducer is the operational semantics of campaign custody. Candidate registration, exact paired cells, comparisons, decisions, and terminal selection have explicit causal order. Resume is continued transition from a reduced event prefix. The campaign kernel owns identity, pairing, missingness, failure accounting, gate order, and terminal immutability. Domain grafts own the meaning of parameters, cases, execution, measurements, and native artifacts.

The thesis accompanies a self-contained Go implementation, `opfield`, using only the standard library. The implementation contains a canonical envelope and artifact kernel; a transactional plugin registry; a typed plan language; generic structural folds; execution and static-analysis interpreters; Para, lens, finite-probability, metric-order, experiment, decision, and event-sourced campaign packages; and two independent domain grafts. The first is a miniature RAG optimizer with chunking, lexical and hashed-semantic retrieval, dependency-aware build reuse, seven typed interventions, nine evaluation cases, exact pairing, and promotion gates. The second optimizes a noisy quadratic objective without using the plan or RAG layers, demonstrating that the campaign protocol is domain-neutral. The module passes unit tests, `go vet`, and the Go race detector.

The resulting architecture is not a universal optimizer and does not claim that category theory replaces statistics, application semantics, or operational engineering. Its purpose is narrower and stronger: to identify the small algebraic structures that a core must own so that independently developed plugins and applied systems can be grafted onto one optimization field without losing type boundaries, causal identity, reproducibility, or decision semantics.

# Preface {-}

This volume develops the mathematical backbone implicit in Chapter 21 of the preceding RAG semantics study. That chapter treated optimization as a typed intervention over the dependency graph of an evolving RAG release. The present work asks what must exist beneath that domain model if indexing optimization, query optimization, answer evaluation, session calibration, backend certification, and production canaries are to share one compositional architecture.

The answer is not “more interfaces” in the ordinary sense. Interfaces are useful only when their laws and composition are controlled. A core made entirely of extension points has no semantics of its own. Conversely, a closed framework that hard-codes every stage cannot accommodate GEC authorization, TTC connected retrieval, Garden widgets, a new ANN backend, or a non-RAG optimization problem without central modification. The design problem is to locate the boundary at which variability becomes a model of stable structure rather than a bypass around it.

The implementation is intentionally a sandbox. It is small enough to inspect end to end and concrete enough to run. It does not include distributed workers, a production artifact service, generalized Bayesian optimization, release activation, or a full statistical library. Those facilities are discussed as interpreters, stores, policies, or domain grafts. The core remains limited to mechanisms whose semantics are sufficiently stable to justify shared ownership.

The mathematical presentation is constructive. Definitions are followed by their software consequences; abstract structures are retained only when they explain a composition rule, a plugin boundary, a law, an identity, a test, or an operational invariant. Formal claims are separated into proven-by-construction properties, executable law checks, proof sketches, and empirical obligations. Natural-language model quality and production performance remain empirical regardless of the elegance of the wiring category.

# Principal thesis claims {-}

1. **Optimization requires a domain of composable systems before it requires a search algorithm.** A proposer cannot act meaningfully until system structure, parameterization, intervention, stochastic evaluation, resources, and decisions have explicit semantics.
2. **The correct low-level plugin boundary is a typed signature.** Plugins add objects, primitive generators, codecs, annotations, and laws. The kernel retains sequence, tensor, structural maps, validation, and interpretation.
3. **A free wiring syntax is the simplest stable backbone.** It separates intensional plans from their meanings and gives each interpreter a unique structural extension from plugin generators.
4. **Parameters should compose with systems.** The Para construction models a component as $P \otimes A \to B$ and makes composite parameter spaces arise from wiring rather than a global namespace.
5. **Candidate patches are optics plus causal declarations.** Lawful focus/update behavior is necessary but not sufficient; every intervention must also name semantic class, direct targets, dependency closure, and evaluation fidelity.
6. **Stochastic comparison is about couplings.** Exact paired coordinates and shared randomness are structural requirements, not reporting conveniences.
7. **Optimization is ordered rather than scalar by default.** Security, integrity, coverage, quality, latency, cost, and user outcome generally form constraints and partial orders; scalar preference is a final policy layer.
8. **A campaign is a dynamic system with durable semantics.** Event-sourced custody makes interruption and resume part of the same transition system rather than an implementation-specific recovery path.
9. **Two plugin surfaces are required.** Fine-grained operation plugins support multiple interpreters; coarse domain grafts wrap existing applications without forcing their internals into the kernel.
10. **The core should be small because its laws are strong, not because it is vague.** Composition, identity, effect declaration, pairing, missingness, gate order, and event validity belong in the kernel. Product meaning and native measurement do not.

# Notation and conventions {-}

A symmetric monoidal category is written $(\mathcal C, \otimes, I)$. Objects such as $A,B,X,Y$ denote typed interfaces or data schemas. A morphism $f:A\to B$ denotes a computation or system component. Sequential composition is written $g\circ f$ or $f;g$. Parallel composition is $f\otimes g$.

A typed signature is $\Sigma=(\mathsf{Ob},\mathsf{Gen},\mathsf{dom},\mathsf{cod},\mathsf{ann})$. Its free wiring category is written $\mathsf W(\Sigma)$. A parameterized morphism is represented by a pair $(P,f)$ with $f:P\otimes A\to B$ and written $A\xrightarrow[P]{f}B$. A release or complete configuration is $\theta\in\Theta$. A local parameter view is $\ell:\Theta\rightsquigarrow P$. A candidate intervention is $i:\theta\leadsto\theta'$.

A Markov kernel from $X$ to $Y$ is written $K:X\rightsquigarrow Y$. $\mathcal D(Y)$ denotes a distribution over $Y$. A paired coupling of baseline and candidate kernels is $\Gamma_x\in\mathcal D(O_b\times O_c)$ with the correct marginals. A metric vector is $m:O\to\mathbb R^d$, with each coordinate carrying a direction. The oriented candidate difference is $\Delta_j=s_j(m_j^c-m_j^b)$, where $s_j=1$ for maximization and $s_j=-1$ for minimization.

A campaign state is $s\in S$, an event is $e\in E$, and the pure reducer is $\rho:S\times E\rightharpoonup S$. A partial arrow indicates that invalid events are rejected. An event prefix is $e_{1:n}$ and its reduced state is $\rho^*(s_0,e_{1:n})$.

The Go implementation uses schema IDs and canonical envelopes at runtime because Go cannot directly encode a heterogeneous typed syntax tree with all type equalities checked statically. Typed generic adapters establish the plugin boundary; plan validation establishes the heterogeneous wiring boundary.

![The proposed optimization doctrine and its executable realization.](figures/01_optimization_doctrine.png){width=92%}

# Part I. Reframing the optimization field

# 1. From an optimization loop to an optimization doctrine

## 1.1 The usual loop is extensionally under-specified

The standard optimization loop can be expressed in a few lines:

```text
while budget remains:
    candidate = propose(history)
    outcome = evaluate(candidate)
    history = update(history, candidate, outcome)
return select(history)
```

This form is useful for explaining search strategy. It is not a sufficient architecture. `candidate` may be a scalar, a prompt file, a whole index, a deployment release, or a policy mutation. `evaluate` may be a pure function, a stochastic provider call, a multi-hour build, or a production canary. `outcome` may be one number, a partial metric vector, a failure, an interaction trace, or an artifact graph. `history` may be in memory, a filesystem, a database, or a durable event stream. `select` may be argmax, a feasibility test, a Pareto policy, or human authorization.

When all of these distinctions are left to callbacks, the loop has almost no denotational content. It cannot tell whether two candidates are comparable, whether an index can be reused, whether a failure remains in the denominator, whether a plugin duplicated an effect, or whether a resumed run is the same experiment.

A doctrine is a small collection of structures that make those questions meaningful across domains. It does not prescribe the search algorithm. It specifies what a system, parameter, intervention, trial, comparison, decision, and campaign are, and how each composes.

## 1.2 Why RAG exposes the weakness

RAG optimization spans a dependency graph rather than one parameter vector. A chunk-size change modifies knowledge projection, chunk identities, generated representations, embeddings, indexes, retrieval labels, and downstream answers. A fusion-weight change reuses the index but changes ranking and every downstream context. A reranker change alters disclosure, latency, failure behavior, and ranking. A deadline change may be operational under one workload and answer-changing under another. An agent-tool description changes the distribution over search trajectories. A widget projection can change user outcome with no retrieval change.

These interventions have different codomains of evidence. Static laws can reject an invalid chunker or authorization order. Exact-oracle tests can certify an ANN approximation. Retrieval labels can compare ranking. Repeated answer cells can compare grounding. Multi-turn sessions are required for agent policy. Shadow and canary trials are required for production latency and fallback. A generic optimizer must not flatten these levels.

## 1.3 What the doctrine must own

The doctrine must own precisely the decisions that make evidence composable:

- typed system boundaries;
- sequential and parallel composition;
- explicit duplication and discarding;
- semantic identity;
- parameter composition and reparameterization;
- lawful local update;
- declared effects and dependencies;
- stochastic trial coordinates and couplings;
- metric direction and missingness;
- ordered gate evaluation;
- durable state transition and terminality.

It must not own the meaning of a GEC source role, a TTC product fact, a Garden widget, or an ANN recall threshold. Those remain domain semantics.

## 1.4 Search algorithms become plugins of the doctrine

Grid search, random search, Bayesian optimization, evolutionary search, gradient descent, LLM proposal, and human curation can all implement a proposer interface once the candidate space and evidence protocol exist. Gradient-based optimization may exploit extra differential structure; Bayesian methods may exploit probabilistic surrogate structure. Neither should be required by the base field.

This inversion is central: the optimizer is no longer the core into which a system is embedded. The compositional system and experiment doctrine is the core; a search algorithm is one controller over it.

# 2. Empirical starting point: `ragopt`, `ragkit`, and applied RAG

## 2.1 Existing strengths

The reviewed `ragopt` package already establishes several strong semantic choices. A candidate is an immutable baseline snapshot plus exactly one mutable asset. Evaluation pairs incumbent and challenger at identical case and repeat coordinates. Outcomes distinguish contract validity, abstention, metrics, usage, errors, and native artifacts. The run store copies inputs, appends cells, resumes incomplete runs, and prevents a report from silently ignoring missing cells. Gate policy is ordered rather than one weighted objective.

`ragkit` provides deterministic RAG domain types and functions: documents, chunks, representations, embedders, lexical and vector searchers, retrieval and fusion, reranking contracts, context construction, grounded answer validation, caches, execution controls, and immutable index bundles. RAG-TTC, GEC, and Garden graft product-specific behavior onto those mechanisms.

The supplied snapshot contains 173 Go files and 273 test functions in `ragkit`, 45 Go files and 42 tests in `ragopt`, 515 Go files and 906 tests in RAG-TTC, 200 Go files and 252 tests in GEC, and 70 Go files and 108 tests in the Garden backend scope. The numbers establish that the design problem is not hypothetical. Several mature subsystems already need a shared semantic boundary.

## 2.2 The remaining gap

The current optimization kernel begins after a product has materialized a candidate and implemented an `Arm`. It does not know the candidate's internal parameter structure, the system plan it modifies, the dependency closure it invalidates, the effects it changes, or the evaluation fidelity required by its semantic class. This is a sound boundary for a generic run harness, but it leaves each application to reinvent the optimization *field* around it.

The current RAG library begins with RAG domain operations. It does not provide a domain-neutral compositional language for systems and parameterization, nor should it. Consequently, a direct attempt to put all optimization composition into `ragkit` would over-specialize the foundation.

The missing layer is between the semantic kernel and the domain packages: a small, typed, compositional doctrine that can describe the shape of an optimized system and the legal way external domains extend it.

## 2.3 Requirements derived from the codebase

The applied systems imply concrete requirements:

1. A build plan and a query plan must share types and identities but admit different interpreters and resource policies.
2. Query-only candidates must reuse build artifacts without relying on handwritten lists of irrelevant fields.
3. A product runner must retain a native artifact richer than generic metrics.
4. A search tool or full conversation must be usable as one trial without rewriting the application into primitive nodes.
5. A new backend or evaluation stage should be pluggable at a fine-grained level when static analysis is valuable.
6. Authorization and remote disclosure must be visible as effects that a plan policy can reject.
7. Failures and missing metrics must be represented rather than coerced into zero or dropped.
8. A campaign must resume from exact semantic coordinates.
9. The core cannot depend on any one RAG provider, UI framework, judge, or artifact backend.

These requirements motivate two plugin surfaces rather than one.

# 3. Design criteria and non-goals

## 3.1 Criteria

**Compositionality.** The meaning of a composite plan must be determined by meanings of its parts and the composition constructors.

**Typed openness.** Plugins can add schemas and primitive operations without adding new plan node kinds or changing kernel composition.

**Multiple interpretations.** One plan can be executed, analyzed, identified, visualized, or compiled to a remote graph.

**Parameter locality.** Component parameters compose with component wiring and can be addressed through lawful local views.

**Stochastic honesty.** Randomness, sampling, coupling, failure, and retained material are explicit.

**Causal invalidation.** An intervention determines downstream artifacts and evaluations through a dependency relation.

**Custody.** Every candidate, case, repeat, arm, metric, artifact, comparison, and decision has stable identity and durable state.

**Policy separation.** Eligibility and preference are explicit policy values, not hidden in an optimizer's scoring callback.

**Small trusted core.** The kernel should be inspectable and stable; product-specific meaning belongs in grafts.

## 3.2 Non-goals

The doctrine is not intended to prove semantic equivalence of arbitrary application code automatically. It cannot infer whether a prompt change is safe, whether a model answer is true, or whether a corpus label is correct. It provides places to state and test these claims.

It is not a replacement for workflow orchestration. A distributed scheduler can interpret plans or execute trial requests, but queue placement and cluster management need not be part of the categorical kernel.

It is not a requirement that every application operation become a primitive generator. Fine-grained representation is useful only when structural analysis, reuse, or alternate interpretation justifies it.

It is not a universal scalar optimizer. The default decision structure is constraint and partial order.

# 4. Two plugin surfaces

## 4.1 Low-level operation plugins

A low-level plugin extends a typed signature. It declares schemas, primitive operation signatures, effects, dependency labels, resource hints, codecs, implementations, and laws. It is appropriate when a component should be visible to several interpreters.

Examples include:

- normalize one source revision;
- chunk a document;
- generate one representation;
- embed a batch;
- build or query one index;
- fuse rankings;
- rerank an authorized pool;
- assemble context;
- validate an answer contract.

The plugin does not define sequence or parallel composition. It cannot define a special identity node. It cannot alter how plan IDs are computed. Those remain kernel laws.

## 4.2 High-level domain grafts

A high-level graft implements the optimization protocol around an existing system. It supplies a `Space`, `Proposer`, `Workload`, `Runner`, `Policy`, and `Store`. The runner may call an application service, run a CLI, submit a job, or execute a low-level plan.

Examples include:

- one complete GEC retrieval-and-answer case;
- one Garden multi-turn calibration conversation;
- one ANN build/query benchmark;
- one production shadow request;
- one noisy mathematical objective.

This surface prevents the architecture from requiring an invasive rewrite before an application can gain exact pairing and durable campaign semantics.

## 4.3 Why one interface cannot serve both

If every domain is forced into primitive operations, the core becomes a workflow DSL and application semantics leak into shared packages. If every domain is only an opaque runner, the core cannot analyze plans, dependencies, effects, or artifact reuse. The two surfaces occupy different abstraction levels and can coexist.

![Low-level plugins extend typed syntax; high-level grafts connect complete domains to campaign custody.](figures/03_plugin_surfaces.png){width=92%}

# Part II. The categorical and probabilistic backbone

# 5. Typed signatures

## 5.1 Definition

A typed operation signature is

$$
\Sigma=(O,G,d,c,a),
$$

where $O$ is a set of object or schema symbols; $G$ is a set of primitive generators; $d(g)$ and $c(g)$ are finite ordered lists of objects giving the domain and codomain ports of generator $g$; and $a(g)$ is a set of annotations.

A port $[A_1,\ldots,A_n]$ denotes the tensor $A_1\otimes\cdots\otimes A_n$. The empty port denotes the monoidal unit $I$.

Annotations are not part of ordinary category theory but are necessary for software interpretation. In this doctrine they include:

- semantic operation and plugin version;
- effect set;
- determinism and cacheability claims;
- dependency labels;
- resource hints;
- data-class or disclosure metadata;
- human description.

## 5.2 Schemas are semantic objects

A schema is not merely a serialization shape. It identifies the interpretation of a value on a wire. Two JSON records with the same fields but different authority, temporal scope, or units require different schemas. A source chunk and a generated summary may both contain text, but one is evidence and one is a search representation. Treating them as the same object would make an invalid plan type-correct.

Versioned schema IDs provide nominal type safety across plugin boundaries. A codec interprets a schema symbol as a concrete representation and establishes an encode/decode relation. In the sandbox, canonical JSON envelopes combine schema ID, payload, and domain-separated digest.

## 5.3 Signature union and plugin registration

A registry combines plugin signatures only when object and generator names do not conflict and every operation port resolves. This is a disjoint-union discipline with explicit sharing through previously registered schema IDs. Transactional registration ensures that failed laws or collisions do not leave a partial signature.

The registry is best treated as immutable after release construction. Hot replacement of a generator implementation changes the model of the signature and therefore creates a new registry or release identity.

## 5.4 Why annotations remain declarative

Effect and dependency declarations cannot be trusted merely because they are fields. Their purpose is to support inspection, policy, and testing. A production plugin may be isolated in a capability sandbox so that declarations can also be enforced. The mathematical architecture does not confuse a declared effect system with OS security; it supplies the vocabulary and plan position required for enforcement.

# 6. The free wiring category

## 6.1 Syntax

From $\Sigma$ we construct a free typed wiring language $\mathsf W(\Sigma)$. Its morphisms are generated by:

- each primitive $g:d(g)\to c(g)$;
- identity $\mathrm{id}_A:A\to A$;
- sequential composition;
- tensor product;
- symmetry or permutation maps;
- explicit copying $\Delta_A:A\to A\otimes A$;
- explicit discarding $!_A:A\to I$.

The sandbox represents this syntax as `plan.Plan` nodes: `primitive`, `identity`, `sequence`, `tensor`, `permute`, `copy`, and `drop`.

## 6.2 Why free syntax is the backbone

Free syntax separates a plan from every particular meaning. The same term can be interpreted as executable code, a dependency graph, a cost expression, a provenance query, a disclosure proof obligation, or a diagram. This is the source of composability: all meanings follow the same wiring.

The free construction also gives plugins a disciplined extension point. A plugin adds generators to $\Sigma$; it does not add an eighth composition constructor. This prevents a plugin from creating a node that static analysis cannot see or that identity hashing treats inconsistently.

## 6.3 Explicit copy and discard

In an ordinary cartesian category, values can be copied and discarded naturally. Effectful computations generally cannot. Duplicating the output value of a completed deterministic computation is different from executing the computation twice. Discarding a value is different from removing the computation that produced it, especially when the computation writes an artifact or discloses data remotely.

The plan syntax therefore makes structural copy and discard explicit. It resembles a free gs-monoidal or CD-style wiring category rather than assuming all morphisms are cartesian. This aligns with categorical work that treats free gs-monoidal categories as combinatorial term graphs and notes their relevance to computer implementation.

## 6.4 Equations and normalization

The kernel enforces associative sequence and tensor and removes identities after checking boundary compatibility. Thus

$$
(f;g);h = f;(g;h)
$$

and

$$
(f\otimes g)\otimes h = f\otimes(g\otimes h)
$$

receive the same normalized plan representation and digest. Permutation is explicit, so the order of a port remains semantic.

The sandbox does not quotient by every possible gs-monoidal equation. In particular, it does not automatically rewrite copy through arbitrary generators. This conservative syntax preserves intensional structure needed for effects and provenance.

## 6.5 Universal interpretation

Let $\mathcal D$ be a semantic domain with meanings for the structural constructors. An assignment $F_0$ of every object and generator in $\Sigma$ to $\mathcal D$ extends uniquely by structural recursion to an interpretation

$$
\llbracket-\rrbracket_F:\mathsf W(\Sigma)\to\mathcal D.
$$

In the implementation, `plan.Algebra[R]` supplies meanings for the seven constructors and `plan.Fold` performs the extension. This is the practical universal property.

![A plugin signature generates one plan syntax; folds induce multiple whole-plan interpretations.](figures/02_free_plan_interpreters.png){width=92%}

# 7. Interpreters, effects, and abstract semantics

## 7.1 Execution as an effectful interpretation

A pure generator would denote a function. Real operations can fail, observe time, read and write artifacts, call networks, use state, sample randomness, or disclose content. A useful denotation has the shape

$$
\llbracket f\rrbracket : X \to T(Y),
$$

where $T$ captures effects. One conceptual carrier is

$$
T(Y)=\mathsf{Context}\to\mathsf{Outcome}(Y\times\mathsf{Trace}\times\mathsf{Artifacts}\times\mathsf{Duration}).
$$

This can be organized as a Kleisli category when the chosen effect combination forms a monad. Algebraic-effects theory offers another view: primitive effects generate a free theory and handlers interpret them. The sandbox does not encode a monad or handler calculus directly; it uses an explicit `core.Execution` value and an execution algebra. The categorical model explains why sequence and alternate handlers can share syntax.

## 7.2 Failure has semantic classes

At least four statuses are necessary:

- success;
- domain failure;
- infrastructure failure;
- cancellation.

A query returning a valid abstention can be a success. An answer contract violation can be a domain failure. A corrupt artifact is infrastructure failure. Context cancellation is not evidence that the candidate is low quality. These distinctions determine retry, denominator, and gate behavior.

A plugin implementation error is returned as an attributable execution result. An outer campaign error is reserved for inability to maintain campaign semantics, such as an event-store write failure.

## 7.3 Static abstract interpretation

The same plan can be folded into a static summary. The sandbox computes operation set, effect set, dependency set, determinism, cacheability, and a resource hint. Sequential and tensor composition use different resource operations:

$$
\begin{aligned}
\mathsf{work}(f;g)&=\mathsf{work}(f)+\mathsf{work}(g),\\
\mathsf{critical}(f;g)&=\mathsf{critical}(f)+\mathsf{critical}(g),\\
\mathsf{memory}(f;g)&=\max(\mathsf{memory}(f),\mathsf{memory}(g)),\\[4pt]
\mathsf{work}(f\otimes g)&=\mathsf{work}(f)+\mathsf{work}(g),\\
\mathsf{critical}(f\otimes g)&=\max(\mathsf{critical}(f),\mathsf{critical}(g)),\\
\mathsf{memory}(f\otimes g)&=\mathsf{memory}(f)+\mathsf{memory}(g).
\end{aligned}
$$

These are estimates, not performance guarantees. Their value is compositional preflight and comparison.

## 7.4 Effect policy as an interpreter or predicate

A policy can reject a plan whose static interpretation contains forbidden effects or an invalid ordering. A data-class analysis can require every `remote.disclosure` operation to be dominated by an authorization certificate stage. A deterministic-replay policy can reject `clock` and undeclared `random` effects. A local-test policy can replace network generators with artifact replay handlers.

This is a direct benefit of retaining plans as data. A callback-only architecture can log effects after execution; it cannot reliably reject a composition before execution.

## 7.5 Interpreter coherence

Different interpreters need not produce identical traces, but they must share protected structure. A concurrent execution interpreter may schedule tensor branches differently from the serial reference interpreter. Its observational equivalence may ignore branch interleaving while preserving outputs, failure class, per-operation observations, disclosure set, artifacts, and resource bounds.

Every production interpreter should state its refinement relation to the reference semantics. This is more precise than saying two engines “run the same DAG.”

# 8. Parameterized morphisms and the Para construction

## 8.1 Parameter objects

A configurable component is not merely $f:A\to B$. It is a family indexed by a parameter object $P$:

$$
f:P\otimes A\to B.
$$

Equivalently, each $p\in P$ selects a behavior $f_p:A\to B$. The object $P$ can be a scalar, a structured record, a prompt artifact, an index backend specification, or a complete release submanifest.

This formulation gives parameters a type and a position in the system.

## 8.2 Composition

Suppose

$$
f:P\otimes A\to B
$$

and

$$
g:Q\otimes B\to C.
$$

Their parameterized composite has parameter object $P\otimes Q$:

$$
(P\otimes Q)\otimes A
\cong Q\otimes(P\otimes A)
\xrightarrow{\mathrm{id}_Q\otimes f}
Q\otimes B
\xrightarrow{g}
C.
$$

The crucial consequence is that parameters compose according to system wiring. There is no need for a global untyped map whose keys happen to be understood by distant code.

![Composition in Para tensors component parameter objects.](figures/04_para_composition.png){width=88%}

## 8.3 Reparameterization

An optimizer may use coordinates $R$ that differ from implementation parameters $P$. A map $r:R\to P$ induces

$$
r^*f = f\circ(r\otimes\mathrm{id}_A):R\otimes A\to B.
$$

Examples include:

- log-space to a positive rate;
- logits to simplex weights;
- a single policy knob tied to several lower-level values;
- a model alias resolved to an immutable provider version;
- a candidate artifact bundle materialized into legacy files.

Reparameterization should be explicit and identified. Otherwise an optimizer's coordinates can change meaning without a release identity change.

## 8.4 Para as a category of open models

Under standard conditions, parameterized maps form a category `Para(C)` whose morphisms are parameterized maps modulo suitable reparameterization. Work on compositional learning has used this construction to explain how models and learning algorithms compose, including backpropagation as a monoidal functor and gradient-based learning through parametric lenses.

The present doctrine generalizes the architectural lesson beyond gradients. The parameter object can be discrete and mixed, and the proposer need not be differentiable. Composition still benefits from Para.

## 8.5 Implementation correspondence

The sandbox's `para.Parametric[P,A,B]` contains a `Run(P,A)` function. `Compose` pairs parameter objects, `Tensor` pairs independent systems, and `Reparameterize` maps coordinates. Go's ordinary product structs stand in for monoidal products.

The implementation is intentionally small: it does not quotient reparameterizations or encode associator isomorphisms as first-class values. The thesis-level architecture can use a bicategory or double category when those witnesses must be retained.

# 9. Reparameterizations, transformations, and double structure

## 9.1 Why ordinary categories are not the whole story

Optimization involves two kinds of movement:

1. composing systems along their data interfaces;
2. changing how one parameter space represents or controls another.

It is useful to distinguish horizontal system wiring from vertical parameter transformations. A square can express compatibility:

$$
\begin{array}{ccc}
P\otimes A & \xrightarrow{f} & B\\
\downarrow r\otimes u && \downarrow v\\
Q\otimes A' & \xrightarrow{g} & B'.
\end{array}
$$

Such squares can represent schema migration, materialization, adapter correctness, or a candidate implementation refining an abstract specification.

## 9.2 Double categories and open systems

Double-category treatments of open dynamical systems distinguish interface wiring from maps between dynamics. This is relevant because an optimization campaign is itself an open dynamical system: it receives proposals and trial completions, changes internal state, and emits decisions and artifacts. Product runners can be grafted through interfaces without exposing all internal state.

The reference implementation does not implement a generic double-category library. It retains the distinction in ordinary interfaces:

- plans compose system operations;
- optics and `Space.Apply` transform specifications;
- runners interpret a spec on a case;
- campaign events transform durable state.

A future formalization can promote compatibility evidence between these layers to explicit 2-cells.

## 9.3 Refinement squares

A useful production notion is a refinement square between an abstract operation and a concrete plugin implementation. It can state that concrete execution followed by output projection equals abstract execution after input embedding, perhaps up to an observation relation. Such squares would support backend substitution and differential certification.

For example, an ANN backend refines an exact vector-search operation not by equality but by a tolerance relation over ranked outputs and resource improvement. The square's relation becomes part of its certification artifact.

# 10. Optics and lawful intervention

## 10.1 The local-update problem

A release specification $\Theta$ is large. An optimizer usually changes one focus $P$: chunk size, vector weight, reranker model, timeout, or prompt. A raw function `set(path,value)` is too weak. It does not state how to read the current focus, whether writes are stable, or whether two updates interfere.

A lens consists of

$$
\mathsf{get}:\Theta\to P
$$

and

$$
\mathsf{put}:\Theta\times P\to\Theta,
$$

subject to laws.

## 10.2 Lens laws

For admissible $p,q$:

$$
\mathsf{put}(\theta,\mathsf{get}(\theta))=\theta
$$

(get-put),

$$
\mathsf{get}(\mathsf{put}(\theta,p))=p
$$

(put-get), and

$$
\mathsf{put}(\mathsf{put}(\theta,p),q)=\mathsf{put}(\theta,q)
$$

(put-put).

These laws give a local patch stable meaning. Put-put is particularly important for event histories and adaptive proposers: the current focus depends on the last value, not accidental update history.

## 10.3 Partial validity

Real configurations impose constraints. Overlap must be less than chunk length; weights must be finite and nonnegative; a model must support the required dimension. `put` may therefore be partial. The laws apply over admissible values. A `Space` must not advertise a patch that its optic rejects.

The sandbox checks lens laws at plugin registration over representative states and values. This is executable evidence, not a universal proof. Property testing can strengthen coverage.

## 10.4 General optics

Lenses cover product-like configuration. Prisms can represent optional routes or backend variants; traversals can update homogeneous collections; affine optics can focus on at most one target. Riley's categorical treatment unifies these accessors and provides a general account of lawfulness. The architecture should expose an optic identity and law certificate rather than freeze the core to string paths.

## 10.5 Patch plus causal declaration

A lawful optic answers “how is the configuration changed?” It does not answer “what does the change invalidate?” A complete patch therefore includes:

$$
i=(\ell,p',\mathsf{class},\mathsf{targets},\mathsf{closure},\mathsf{hypothesis}).
$$

Semantic classes include operational, approximation, relevance, knowledge, policy, interaction, and presentation. Direct targets identify changed dependency nodes; closure is the transitive downstream invalidation set.

![A lawful local patch induces a causal dependency closure and reuse boundary.](figures/05_optic_dependency_closure.png){width=92%}

## 10.6 Composition of interventions

The initial `ragopt` discipline of exactly one mutation is valuable because it improves attribution. The mathematical backbone can nevertheless compose compatible interventions. Two lenses on independent focuses can tensor; nested lenses can compose. A multi-change candidate then has a structured intervention tree rather than an unordered patch set.

Campaign policy can still require atomic interventions during exploration and allow composed candidates only after individual effects are understood.

# 11. Categorical probability and stochastic trial semantics

## 11.1 A trial is a kernel

A deterministic trial is a function. A model-mediated or production trial is more accurately a Markov kernel

$$
K_\theta:X\rightsquigarrow O,
$$

assigning each case $x$ a distribution $K_\theta(-\mid x)$ over outcomes. Randomness may arise from model decoding, provider load, approximate search, timing, data arrival, or agent choices.

Markov categories provide a compositional setting in which stochastic maps, copying, discarding, conditional independence, and statistical notions can be treated abstractly. The doctrine uses this structure to define trial composition without choosing one probability representation.

## 11.2 Composition

For kernels $K:X\rightsquigarrow Y$ and $L:Y\rightsquigarrow Z$:

$$
(L\circ K)(z\mid x)=\int_Y L(z\mid y)K(dy\mid x).
$$

For finite distributions the integral is a sum. The sandbox implements `prob.Bind` and `prob.Compose` directly.

Independent parallel composition uses product kernels. Correlated stages require a joint kernel rather than tensor.

## 11.3 Deterministic maps inside stochastic semantics

A deterministic function $f:X\to Y$ embeds as a Dirac kernel $\delta_f:X\rightsquigarrow Y$. This lets deterministic preprocessing, stochastic generation, and deterministic validation compose in one semantic target.

Deterministic structure is also necessary for lawful copying. A sampled outcome can be copied after sampling; copying a stochastic generator and running two samples is a different plan. Explicit copy in the wiring syntax preserves this distinction.

## 11.4 Partiality and failure

A probability distribution over only successful values loses failure probability. One option is an outcome object

$$
O = Y + \mathsf{DomainFailure}+\mathsf{InfrastructureFailure}+\mathsf{Cancelled}.
$$

The kernel then distributes mass across terminal classes. Another option uses partial Markov categories or subprobability. The sandbox uses explicit terminal statuses in samples. This is sufficient for exact denominator custody and avoids treating a failed trial as absent probability mass.

## 11.5 Retained material versus abstract distribution

A production system rarely knows the full kernel. It obtains samples. Reproducibility is material: inputs, seed, provider identity, response, trace, and artifacts are retained. The categorical kernel is the denotational model; the campaign ledger is sampled evidence.

# 12. Couplings and exact paired experiments

## 12.1 Independent samples are not the default comparison

To compare baseline $K_b$ and candidate $K_c$, one could sample independently. This adds avoidable variance and weakens causal attribution. A paired experiment chooses a coupling

$$
\Gamma_x\in\mathcal D(O_b\times O_c)
$$

whose marginals are $K_b(-\mid x)$ and $K_c(-\mid x)$.

The paired difference is measured on joint samples $(o_b,o_c)\sim\Gamma_x$.

## 12.2 Common random numbers

A practical coupling uses one seed $\omega_{i,r}$ for case $i$ and repeat $r$:

$$
o_b=F(\theta_b,x_i,\omega_{i,r}),\qquad
o_c=F(\theta_c,x_i,\omega_{i,r}).
$$

This is valid only where the runner interprets the seed consistently. Remote providers may not expose deterministic seeding. Stronger coupling can replay identical retrieval candidates, provider responses, or traffic conditions where doing so does not invalidate the intervention.

The campaign identity domain-separates seeds by campaign, case, and repeat. Baseline and candidate use the same seed coordinate.

![Paired comparison is an explicit coupling of baseline and candidate kernels.](figures/06_paired_markov_coupling.png){width=92%}

## 12.3 Exact coordinates

A trial coordinate includes case ID, repeat, arm, and candidate identity. Comparison projects baseline and candidate onto common case/repeat keys and requires exactly one terminal result from each arm. Missing and duplicate cells are errors.

This is more than bookkeeping. The matrix of exact coordinates is the empirical object being compared. Dropping difficult failures changes the estimand.

## 12.4 Coupling validity under interventions

Not every shared artifact is a valid coupling. Replaying baseline retrieval candidates when testing a new chunker would erase the candidate's intended effect. Replaying provider generation while testing only fusion weights may be useful for retrieval diagnosis but cannot measure answer-distribution change. The intervention's dependency closure determines what can be shared.

This gives a categorical interpretation to evaluation reuse: reuse is permitted only outside the causal downstream cone of the intervention.

# 13. Metrics as orders and resources

## 13.1 Directional metric spaces

A metric definition is $(j,s_j,u_j)$: identity, direction, and unit. Direction orients all differences so positive means better:

$$
\Delta_j=s_j(m_j^c-m_j^b).
$$

This operation is valid without making units commensurate.

## 13.2 Product preorder and Pareto dominance

Given complete metric vectors, candidate $a$ weakly dominates $b$ when it is no worse in every oriented coordinate. It strictly dominates when at least one coordinate is better. This defines a partial order after quotienting observational equality.

The Pareto front is the set of undominated eligible candidates. It preserves trade-offs rather than hiding them in arbitrary weights.

## 13.3 Constraints first

Security, contract validity, missingness, and hard capacity are not preferences. They define the feasible subset:

$$
\mathcal F=\{\theta\in\Theta\mid c_k(\theta)\le 0\ \forall k\}.
$$

Preference operates only on $\mathcal F$. A candidate cannot compensate for unauthorized disclosure with higher recall.

## 13.4 Resources as ordered commutative monoids

Resources combine and admit convertibility or feasibility orders. Work, dollars, token budget, storage, and provider calls can often be modeled as commutative monoids under addition with an order. Parallel critical path and peak memory require richer algebra.

The architecture should permit resource interpretations that are monotone under composition. Fritz's resource-theory account of ordered commutative monoids supplies a general language for combination and convertibility. The software consequence is to keep resource vectors structured and allow policy to apply monotones, rather than forcing one cost scalar into every operation descriptor.

## 13.5 Lawvere-style quantitative enrichment

Some properties can be treated as enriched distances or costs. Latency bounds compose additively in sequence and by maximum in ideal parallel execution. Approximation error may compose under domain-specific bounds. This suggests enrichment of the wiring category in a quantale or ordered algebra.

The sandbox's `CostHint` is a first approximation, not a general enrichment. The thesis leaves the richer carrier pluggable through interpreters.

# 14. Selection, gates, and open decision systems

## 14.1 Decision is not objective evaluation

An evaluator maps outcomes to measurements. A decision policy maps a comparison report to `pass`, `fail`, or `indeterminate`, plus checks and optional preference score. Keeping these separate prevents the runner from deciding its own promotion.

## 14.2 Lexicographic gate program

A gate sequence is evaluated in order:

1. security and integrity;
2. complete paired coverage;
3. protected-stratum noninferiority;
4. target improvement;
5. resource envelope;
6. Pareto or product preference.

The first failed or indeterminate gate terminates evaluation. This order is part of policy identity.

![Eligibility is constraint-first; Pareto and preference apply only to surviving candidates.](figures/07_constraint_pareto_decision.png){width=94%}

## 14.3 Three-valued logic

`Indeterminate` is distinct from failure. Missing metrics, insufficient samples, or an unavailable required stratum mean the policy cannot decide. Treating indeterminate as pass is unsafe; treating it as an intrinsic candidate failure may also be misleading. Operationally it blocks promotion and requests more or corrected evidence.

## 14.4 Selection functions and open games

A selection function maps a context or payoff continuation to preferred choices. Compositional game theory treats open games as systems whose local behavior depends on an environment and whose equilibria compose. Optimization components have a related open character: a local candidate is valuable only relative to downstream metrics, constraints, and environment.

The present architecture does not model every optimizer as an open game. It adopts the narrower lesson that decision behavior should be an explicit composable object with inputs, outputs, and continuation context, not hidden inside a scalar callback.

## 14.5 Human decision as a policy interpreter

Human review can be represented as a terminal gate that consumes the complete promotion report and emits a signed decision event. This preserves the distinction between evidence generation and organizational authority. Human judgment is not made “automatic” by placing it in the same event model; it becomes auditable.

# 15. Campaigns as coalgebras and open dynamical systems

## 15.1 State and transition

A campaign has state

$$
s=(\mathsf{id},\mathsf{candidates},\mathsf{trials},\mathsf{reports},\mathsf{decisions},\mathsf{terminal}).
$$

Its next action depends on missing semantic work: register a candidate, execute a missing coordinate, compare complete pairs, decide a report, or terminate.

This can be viewed as a coalgebra

$$
\gamma:S\to\mathcal F(S)
$$

for a functor describing commands, observations, and next state, or as a labelled transition system. The implementation exposes the transition trace as events and the state update as a pure reducer.

## 15.2 Event-sourced operational semantics

Each event has a sequence number, campaign identity, type, timestamp, and typed payload. The reducer rejects:

- a non-start event first;
- sequence gaps;
- campaign identity mismatch;
- duplicate candidates or cells;
- report before candidate;
- decision before report;
- nonterminal trial result;
- any event after completion.

This event language is the small-step operational semantics of the campaign.

![The event-sourced campaign state machine.](figures/08_campaign_state_machine.png){width=96%}

## 15.3 Resume as semantic continuation

Let $E=P\cdot U$ be an event history split at interruption. Replaying $P$ yields state $s_P$. Continuing from $s_P$ emits only missing events $U$. Correct resume requires

$$
\rho^*(s_0,P\cdot U)=\rho^*(\rho^*(s_0,P),U).
$$

This is reducer associativity. The engine's command selection must also be idempotent with respect to completed semantic coordinates.

The sandbox injects an event-store interruption, resumes, verifies no duplicate cells, and verifies that rerunning a terminal campaign appends nothing.

![Commands, durable append, pure reduction, and replay form the resume loop.](figures/09_event_sourced_resume.png){width=90%}

## 15.4 Open interfaces

A campaign is open to proposers, runners, workloads, policies, and stores. Each component can be replaced through a narrow interface. The campaign identity binds their IDs and the material baseline/candidates, so replacement does not silently continue an old campaign.

This is the high-level plugin architecture. Its compositionality is operational rather than fine-grained categorical wiring, but the same design rule applies: the kernel owns the transition laws; grafts supply behavior at ports.

# 16. The unified optimization doctrine

## 16.1 Definition

An optimization doctrine $\mathfrak O$ consists of:

1. a typed monoidal base $\mathcal C$ or free wiring presentation $\mathsf W(\Sigma)$;
2. a category of parameterized systems $\mathsf{Para}(\mathcal C)$;
3. a class of lawful optics over parameter/release objects;
4. a stochastic semantic category $\mathcal K$ for trials;
5. an ordered resource and metric semantics $\mathcal V$;
6. an artifact and identity theory $\mathcal A$;
7. a campaign transition system $\mathcal S$;
8. a family of structure-preserving interpretations linking these layers.

A domain graft supplies a model of the relevant signatures and interfaces plus law evidence.

## 16.2 Optimization problem in the doctrine

A problem instance includes:

- baseline parameter/release $\theta_0$;
- legal intervention family $I(\theta_0)$;
- workload distribution or finite suite $W$;
- trial kernel family $K_\theta$;
- metric map $m$;
- feasibility/gate policy $G$;
- proposal controller $P$;
- budget/resource policy $B$.

The optimizer seeks evidence for an eligible preferred candidate, not merely

$$
\arg\max_\theta J(\theta).
$$

A more faithful expression is

$$
\operatorname{Select}_G\left(
\operatorname{Pareto}
\left\{
(\theta,\widehat{K_\theta},m,\mathsf{trace})
\mid \theta\in I(\theta_0),\ \mathsf{evidence\ complete}
\right\}
\right).
$$

## 16.3 Plugin theorem, informally

Given a plugin signature extension $\Sigma\hookrightarrow\Sigma'$ and a valid model of its generators in each required interpreter, every existing plan remains valid with unchanged meaning, and every new plan receives a meaning by the same fold. No existing interpreter requires a new plan-node case.

This is the core extensibility result. In software terms, the syntax is closed under constructors and open under generators and interpreters.

## 16.4 Scope of proof

The free-syntax extension property is structural. The claim that a plugin operation correctly implements its declared generator is a separate refinement obligation. The claim that a candidate is better is statistical and policy-relative. The doctrine does not conflate these proof levels.

EOF
wc -l -w -c /mnt/data/opfield_work/thesis/A_Categorical_Backbone_for_Composable_Optimization.md
```

<details><summary>💭 Thinking</summary>

**Packaging the deliverables**

I’m consolidating the verified implementation, mathematical correspondence, reproducibility scripts, examples, and thesis materials. I’ll package the source and executable sandbox together, with validation results and clear artifact boundaries.

**Packaged the deliverables**

</details>

```unknown
bash -lc tail -n 220 /mnt/data/opfield_work/thesis/A_Categorical_Backbone_for_Composable_Optimization.md && printf '\n---HEADINGS---\n' && rg -n '^#' /mnt/data/opfield_work/thesis/A_Categorical_Backbone_for_Composable_Optimization.md | tail -n 120
```

<details><summary>💭 Thinking</summary>

**Constructed and verified a categorical optimization thesis with RAG chapters**

</details>

```unknown
bash -lc cat >> /mnt/data/opfield_work/thesis/A_Categorical_Backbone_for_Composable_Optimization.md <<'EOF'

# Part VI. Assurance, extensions, and research program

# 46. Structural results and proof obligations

## 46.1 Free-extension result

Let $\Sigma$ be a typed signature and $\mathsf W(\Sigma)$ the free strict symmetric monoidal category with explicit copy and discard maps admitted by the chosen wiring doctrine. Let $\mathcal D$ be a target category carrying the corresponding structure. A generator interpretation $J$ assigns every object of $\Sigma$ to an object of $\mathcal D$ and every primitive generator to a morphism with matching domain and codomain.

By freeness, there is a unique structure-preserving functor

$$
\widehat J:\mathsf W(\Sigma)\to\mathcal D
$$

extending $J$. This is the mathematical basis of `plan.Fold`: once an interpreter supplies meanings for primitives and structural constructors, every valid plan has one induced meaning.

Now extend the signature to $\Sigma'=\Sigma+\Delta$. Any interpretation $J'$ that agrees with $J$ on $\Sigma$ induces $\widehat J'$. For every old plan $p\in\mathsf W(\Sigma)$,

$$
\widehat J'(p)=\widehat J(p).
$$

This is the noninterference property desired from operation plugins. New generators do not change old meanings. The software proof depends on stable canonical descriptors and the absence of mutable global registry behavior during a campaign.

## 46.2 Normalization and identity

The sandbox normalizes nested sequence and tensor nodes before hashing. Desired laws are:

$$
(f;g);h \equiv f;(g;h),
$$

$$
(f\otimes g)\otimes h \equiv f\otimes(g\otimes h),
$$

$$
\mathrm{id};f\equiv f\equiv f;\mathrm{id},
$$

and corresponding unit laws for tensor. In a strict presentation, associators and unitors are erased by normalization. Permutations retain explicit identity because port order is semantically visible.

The proof obligation is that normalization is terminating, idempotent, and sound with respect to every interpreter:

$$
N(N(p))=N(p)
$$

and

$$
\widehat J(N(p))=\widehat J(p).
$$

The sandbox tests representative laws. A production kernel should use property tests over generated well-typed plans and a small mechanized proof or exhaustive finite model for the normalization rewrite system.

## 46.3 Type preservation

Let $p:A\to B$ be a validated plan and let an execution environment provide an envelope matching $A$. If every primitive implementation satisfies its declared input/output codecs, then execution either returns an attributable failure outcome or an envelope matching $B$.

This is a progress-and-preservation style property. It is conditional on plugin refinement. The kernel checks structural port compatibility and envelope schema/digest validity. Typed adapters discharge ordinary decode/encode boundaries. A malicious or defective plugin can still lie about its output; post-execution validation turns that lie into infrastructure failure rather than allowing it to contaminate downstream operations.

## 46.4 Tensor independence

For pure deterministic operations $f:A\to B$ and $g:C\to D$, the tensor execution should be observationally equivalent to independent execution:

$$
\llbracket f\otimes g\rrbracket(a,c)
=
(\llbracket f\rrbracket(a),\llbracket g\rrbracket(c)).
$$

With effects, equality is weakened. A concurrent interpreter may interleave observations and resource use. It must preserve branch-local inputs, outputs, artifacts, and protected effects. If two branches contend for a shared provider quota, their joint latency distribution may not factor. Resource analysis and interpreter refinement must state this explicitly.

The core therefore distinguishes syntactic independence from operational independence. Tensor permits parallel interpretation; it does not promise absence of shared external resources.

## 46.5 Para associativity

Given parameterized maps

$$
f:P\otimes A\to B,
\quad
g:Q\otimes B\to C,
\quad h:R\otimes C\to D,
$$

the two ways of composing produce parameter objects isomorphic to $P\otimes Q\otimes R$ and equal behavior up to associators and symmetries. In the sandbox, nested Go product structs expose associativity at the representation level; helper functions construct a canonical pairing convention.

A production schema should canonicalize parameter products or name component fields so that associator choices do not create accidental candidate identities. The mathematical category treats them as coherent isomorphisms; serialized software must choose one normal form.

## 46.6 Optic law and patch determinacy

For a lawful total lens $L:S\rightsquigarrow A$, the three lens laws imply that applying a patch to focus $A$ has history-independent last-write semantics. If `Patch(L,a)` denotes the endomorphism $s\mapsto\mathsf{put}(s,a)$, then:

$$
\mathsf{Patch}(L,a);\mathsf{Patch}(L,b)
=
\mathsf{Patch}(L,b).
$$

For two disjoint commuting lenses $L_A$ and $L_B$:

$$
\mathsf{Patch}(L_A,a);\mathsf{Patch}(L_B,b)
=
\mathsf{Patch}(L_B,b);\mathsf{Patch}(L_A,a).
$$

Commutativity is not automatic for overlapping or constrained optics. A multi-patch candidate should carry either an order or a commutation witness. The sandbox restricts candidates to one patch, matching the supplied `ragopt` discipline and making causal interpretation clearer.

## 46.7 Dependency-closure soundness

Let $G=(V,E)$ be the dependency graph and $T\subseteq V$ direct targets. Let $C=\mathsf{reach}_G(T)$. An artifact labeled by node $v\notin C$ is eligible for reuse only if its semantic key excludes every changed value and every transitive output of changed nodes.

The desired soundness theorem is:

> If plugin dependency declarations are complete and semantic keys are compositional, then reusing artifacts outside $C$ does not change the candidate denotation.

The theorem is conditional because dependency completeness is domain knowledge. Conformance can test it through mutation analysis: change each advertised parameter, execute both fresh and reuse paths, and compare outputs. Provenance traces can also detect undeclared reads by instrumenting configuration access in development builds.

## 46.8 Coupling unbiasedness

Suppose baseline and candidate outcomes have marginals $K_b(x)$ and $K_c(x)$. Any coupling $\Gamma_x$ with these marginals gives an unbiased paired estimator of mean difference:

$$
\mathbb E_{(Y_b,Y_c)\sim\Gamma_x}[m(Y_c)-m(Y_b)]
=
\mathbb E_{K_c(x)}[m]-\mathbb E_{K_b(x)}[m].
$$

The coupling changes variance, not expectation. Common random numbers can reduce variance when responses are positively correlated. They can increase variance otherwise. Pairing is therefore a structural requirement for exact coordinates, while the choice of coupling is a statistical design decision that must be retained in campaign identity.

Provider APIs may not expose stable seeds. A material replay coupling can hold upstream provider output fixed to isolate downstream changes, but it answers a conditional causal question rather than the full live-distribution question. Campaign reports must state which coupling was used.

## 46.9 Failure-preserving comparison

Let each coordinate produce a total trial result in a sum type:

$$
R = \mathsf{Success}(M,A) + \mathsf{DomainFail}(F) + \mathsf{InfraFail}(F) + \mathsf{Cancelled}(F).
$$

Comparison is a total function over pairs of $R$. It never projects only successful metric maps before checking coverage. A hard coverage gate can require all intended coordinates, and a success gate can separately bound failure classes.

This design prevents survivorship bias where a candidate appears strong because hard cases failed and disappeared. It also prevents infrastructure outages from being silently interpreted as low metric values.

## 46.10 Gate monotonicity

A lexicographic gate sequence evaluates $g_1,0,0,g_n$ and returns on first fail or indeterminate. If a new hard gate is prepended, a previously ineligible candidate cannot become eligible. If a stricter version of an earlier predicate replaces it, later favorable metrics cannot compensate.

This monotonicity is desirable for security and integrity policy. It differs from weighted scoring, where adding a penalty can be offset by unrelated gains.

## 46.11 Event-reducer safety

The campaign reducer should satisfy:

1. deterministic reduction;
2. prefix validity;
3. terminal immutability;
4. coordinate uniqueness;
5. causal order of report and decision;
6. campaign identity consistency.

For valid histories $P$ and $U$:

$$
\rho^*(s_0,P\cdot U)=\rho^*(\rho^*(s_0,P),U).
$$

The store and command engine add operational obligations: append atomicity, expected sequence, fencing in distributed execution, and idempotent command selection. The sandbox proves the reducer laws through tests and demonstrates resume under an injected append failure. It does not prove distributed linearizability.

## 46.12 Plugin extension theorem in software form

A practical theorem schema for each plugin version is:

- registration is atomic;
- all schema and operation IDs are unique;
- every operation's port schemas exist;
- codecs round-trip a conformance corpus;
- static descriptor is canonical and immutable;
- implementation outputs validate against the descriptor;
- declared laws pass their certificate suite;
- existing plans retain IDs and interpreter outputs after registration.

The last property can be tested by snapshotting old registry descriptors and running old golden plans before and after plugin addition. This is the executable counterpart of signature-extension conservativity.

# 47. Verification strategy

## 47.1 Assurance ladder

Different claims require different methods:

| Claim | Appropriate evidence |
|---|---|
| schema and port compatibility | compile/validation tests |
| canonical identity | golden vectors and property tests |
| sequence/tensor normalization | property tests and proof of rewrite system |
| plugin implementation refinement | differential and conformance tests |
| dependency closure | mutation tests and provenance instrumentation |
| incremental/full equivalence | generated change-sequence tests |
| campaign reducer safety | state-machine tests and model checking |
| stochastic quality | paired statistical evaluation |
| distributed store semantics | linearizability/fault-injection tests |
| production utility | shadow/canary evidence and human review |

No single formalism establishes all rows. The backbone is valuable because it localizes the claim boundaries.

## 47.2 Property-based plan generation

Generate schemas and well-typed primitive descriptors, then recursively generate plans using identity, sequence, tensor, permutation, copy, and drop. Check:

- validation succeeds for generated plans;
- normalized IDs are invariant under reassociation and units;
- every interpreter fold terminates;
- execution reference and an alternate interpreter agree under the stated observation relation;
- malformed permutations and port mismatches fail;
- unknown node kinds and operation IDs fail closed.

Shrinking should preserve type correctness so counterexamples remain intelligible.

## 47.3 Plugin conformance harness

A plugin package should export a manifest and a test factory. The host supplies generic tests:

- descriptor canonicalization;
- codec round-trip and invalid-payload rejection;
- operation determinism where declared;
- cache-key sensitivity to semantic inputs;
- no undeclared effect under an instrumented environment;
- law checks over generated fixtures;
- cancellation and deadline behavior;
- output schema validation;
- panic containment or process isolation.

Domain-specific tests augment the generic harness. An ANN plugin receives an exact oracle suite; an authorization plugin receives adversarial scope cases; a Garden projection plugin receives provenance fixtures.

## 47.4 Metamorphic optimization tests

Optimization software has useful metamorphic properties:

- adding an irrelevant metric must not change earlier hard-gate results;
- permuting candidate enumeration must not change reports or deterministic selection;
- permuting case execution order must not change terminal state;
- increasing repeats adds coordinates without changing existing coordinate identity;
- resuming after any event prefix yields the same terminal state as uninterrupted execution;
- adding a plugin unused by the campaign must not change campaign identity;
- changing a runner, workload, coupling, metric definition, or policy must change campaign identity.

These tests catch hidden dependence on map order, wall clock, or mutable registries.

## 47.5 Statistical conformance

A stochastic runner can be tested against known kernels. Generate Bernoulli, Gaussian-like finite, or quadratic objectives where expected differences are known. Verify:

- seed splitting produces stable distinct substreams;
- paired reports match hand calculations;
- missing cells and failures remain visible;
- confidence intervals have approximate coverage under simulation;
- sequential policies control the intended error rate under their assumptions;
- Pareto front and metric orientation are correct.

The sandbox includes finite distributions and paired deterministic noise but not a statistical inference package. That should be an extension module rather than part of the identity/custody kernel.

## 47.6 Model checking campaign protocols

A bounded TLA+ or explicit-state model can include:

```text
candidates, cells, reports, decisions, terminal,
commands, events, workerLeases, appendPosition
```

Actions register, schedule, complete, compare, decide, cancel, fail append, resume, and complete. Safety invariants include uniqueness and causal order. Liveness can state that under fair scheduling and a functioning store, every finite campaign eventually terminates.

A distributed refinement adds worker claims and fencing. The model should explore duplicate completions, stale workers, coordinator failover, and concurrent compare commands.

## 47.7 RAG-specific differential tests

For each candidate class:

- execute the legacy application path;
- execute the plan/graft path with identical release and retained provider material;
- compare ranked evidence, contribution traces, authorization decisions, context, answer contract, native artifact, and frontend projection under an explicit normalization;
- classify intended changes.

Security corrections should deliberately change disclosure traces. Deterministic tie-order improvements may change ranks only for equal scores. Identity-epoch changes should not be hidden as compatibility failures.

## 47.8 Race, load, and failure testing

The reference module passes Go's race detector, but production assurance also needs:

- concurrent registry reads after freeze;
- campaign workers completing the same coordinate;
- event append conflicts and coordinator failover;
- artifact write interruption and verification;
- provider timeout and retry storms;
- build/query resource contention;
- canary stop while trials are in flight;
- plugin process crash or malformed response;
- release revocation during a shadow trial.

The semantic outcome for each failure must be specified before injecting it.

## 47.9 Reproducibility levels

A campaign can declare one of several reproducibility classes:

1. **Structural:** same plans, candidates, coordinates, and policies.
2. **Material:** all provider and derived outputs retained; exact replay is possible.
3. **Seeded:** deterministic software and providers under recorded seeds/environment.
4. **Distributional:** only the stochastic kernel/model version is identified; repeated statistics should agree.
5. **Observational:** production environment cannot be replayed; retained trace supports audit only.

Reports should not claim exact reproducibility when only distributional identity exists.

# 48. Plugin security and isolation

## 48.1 Plugins are executable supply-chain inputs

A plugin can read data, invoke networks, consume resources, forge metrics, or corrupt process state. Type descriptors do not make code safe. The architecture separates semantic extensibility from execution trust.

A production manifest should contain:

- plugin ID, semantic version, build/source digest;
- publisher/signature and review status;
- supported kernel/schema versions;
- generators and codecs;
- declared effects, data classes, endpoints, and resource bounds;
- law/conformance certificate references;
- required secrets and capabilities;
- process/runtime isolation profile.

Campaign and release identities bind the exact plugin digest, not merely a friendly name.

## 48.2 Registry freeze

Registration occurs through a builder transaction. Once committed, a registry snapshot is immutable. A campaign captures its registry identity. Dynamic registration during execution would make plan resolution time-dependent and could change old plan meanings.

Hot plugin upgrades therefore create a new registry/release generation. In-flight campaigns continue under the old snapshot or stop with an explicit incompatibility event.

## 48.3 Capability-based execution

Rather than handing a plugin a general context with filesystem, network, secrets, and clocks, the host supplies narrow capabilities:

```go
type Capabilities struct {
    Artifacts artifact.Client
    Clock     clock.Reader
    Random    prob.Source
    Network   network.PolicyClient
    Secrets   secret.ScopedReader
    Observe   trace.Sink
}
```

The manifest determines which fields are populated. Network clients enforce endpoint and data-policy constraints. Artifact clients constrain namespaces. A deterministic test interpreter supplies virtual clock and seeded randomness.

In-process Go cannot reliably sandbox malicious code. Untrusted or high-risk plugins should run in a separate process, container, WebAssembly runtime, or remote service with authenticated typed RPC.

## 48.4 Typed RPC boundary

A process-isolated operation protocol contains:

- registry/plugin/operation identity;
- request/campaign/trial coordinate;
- input envelope references;
- deadline and idempotency key;
- granted capability tokens;
- output envelope and artifact references;
- declared observations and usage;
- terminal status and attributable failure.

The host validates all output as if the process were untrusted. Large artifacts move through content-addressed storage, not arbitrary paths. The RPC protocol is an interpreter of the same primitive signature, so process isolation does not change plan semantics.

## 48.5 Metric and artifact fraud

A domain runner controls native measurement and can lie. The kernel cannot infer truth from a metric map. Trust can be strengthened by:

- evaluator separation from candidate implementation;
- immutable raw/native artifacts;
- independent recomputation of generic metrics;
- hidden cases and policy tests;
- signed provider/request logs;
- deterministic reference implementations;
- human inspection for promotion.

The campaign records who produced each artifact and metric. It does not elevate plugin output to unquestioned fact.

## 48.6 Data minimization

Plans and traces should carry artifact references and digests by default, not duplicate corpus/query text. Effect analysis can calculate disclosure sets. Product policy determines retention and redaction.

A plugin manifest declares whether it needs raw source, normalized text, metadata only, vectors, or aggregate metrics. The host can reject an unnecessarily broad requirement or insert a projection operation before the plugin.

## 48.7 Denial-of-service and quotas

Static resource hints are advisory. Runtime enforcement uses deadlines, memory/process limits, provider quotas, artifact size limits, and output cardinality bounds. A plugin that exceeds its contract yields an infrastructure failure and may be quarantined.

A proposer also requires limits. It cannot emit an unbounded candidate stream or recursively create campaigns without a budget. Candidate-count and materialization budgets are campaign policy.

## 48.8 Schema evolution attacks

A plugin should not reinterpret an existing schema ID with different meaning. Schema IDs are immutable and content/domain separated. Evolution creates a new ID and an explicit migration operation. The registry rejects duplicate IDs with unequal descriptors.

Unknown fields and forward compatibility must be specified per schema. Silent field dropping can invalidate candidate identity or security policy.

# 49. Distributed refinement

## 49.1 Separation of semantic and physical graphs

The plan is a semantic graph. A scheduler may split, batch, fuse, place, retry, or parallelize its operations. These transformations form a physical execution plan that must refine the semantic plan.

Examples:

- batching many `embed` morphisms into one provider request;
- fusing decode/encode boundaries inside one process;
- executing tensor branches concurrently;
- scheduling build stages on remote workers;
- replaying a cached artifact instead of invoking the operation.

Each optimization needs a refinement witness or conformance test preserving protected observations.

## 49.2 Command protocol

Workers should receive idempotent commands keyed by semantic coordinate:

```go
type TrialCommand struct {
    CampaignID  core.Digest
    CandidateID core.Digest
    CaseID      core.Digest
    Repeat      int
    Arm         experiment.Arm
    Seed        uint64
    RunnerID    string
    Deadline    time.Time
    Fence       uint64
}
```

A completion event is accepted only once for the key and current fence. Duplicate attempts can write identical content-addressed artifacts, but only one terminal cell enters campaign state.

## 49.3 Store linearizability

The campaign event stream requires an append operation with expected next sequence or an equivalent compare-and-swap. In a partition, two coordinators may propose the same next event. At most one succeeds. The loser reloads and recomputes commands.

Snapshots are derived caches and never authority. An invalid or stale snapshot is discarded and events replayed.

## 49.4 Exactly-once effect is local, not global

It is unnecessary and usually impossible to guarantee exactly-once execution of every trial. The protocol guarantees at-most-one accepted terminal result per semantic coordinate. Provider calls and work may repeat. Side-effecting domain operations must be idempotent, simulated, or excluded from trials.

Promotion/activation is a separate compare-and-swap effect with an idempotency key. This is the only exactly-once semantic effect required at the release head.

## 49.5 Deterministic scheduling identity

Execution order is normally operational identity, not campaign semantic identity, because exact coordinates make reports order-independent. It becomes semantic when time/environment drift can affect outcomes. A paired interleaving schedule can then be part of the coupling policy:

```text
case 1 repeat 1: baseline, candidate
case 1 repeat 2: candidate, baseline
...
```

The report records schedule and wall-clock strata. This is useful for remote provider drift.

## 49.6 Distributed tensor and cancellation

A tensor node can launch branches concurrently. If one fails, policy decides whether to cancel the other, retain partial artifacts, or wait for complete observations. This policy is part of the execution interpreter, not the abstract tensor.

Campaign cancellation stops scheduling new commands, requests cancellation of active work, accepts or rejects late completions under policy, and appends one terminal cancellation event. Resume after cancellation creates a new campaign unless the cancellation event is explicitly reversible, which the reference doctrine avoids.

## 49.7 Federated or privacy-preserving evaluation

Some workloads cannot leave a product or tenant boundary. A remote evaluator can execute trial commands and return signed aggregate/native artifact references. Exact coordinate identity and metric schema remain shared. The central campaign need not receive raw evidence.

Secure aggregation or differential privacy can be modeled as an evaluation plugin whose noise/privacy budget is part of the metric semantics and campaign identity. Privacy accounting is an ordered resource, not an annotation.

# 50. Limits of the doctrine

## 50.1 Category theory does not supply domain truth

The construction can prove that a plan is well typed, an interpreter is structurally compositional, or a campaign retains exact pairs. It cannot prove that retrieved text is relevant, a judge is calibrated, a source is authoritative, or a user is helped. Those are domain and empirical claims.

Formal structure prevents several classes of category error. It does not eliminate measurement error.

## 50.2 Freeness can expose too much syntax

A fully reified plan for every internal function can become verbose, brittle, and expensive to version. The correct granularity is guided by interpretation value. An operation should be a primitive when it needs independent identity, policy, reuse, observation, replacement, or alternate execution. Ordinary local code can remain inside a plugin implementation.

## 50.3 Effects are difficult to combine universally

Network, state, nondeterminism, exceptions, cancellation, streaming, and resource constraints do not have one trivial monad in production software. Algebraic effects and handlers provide a conceptual model, but a practical Go implementation may use explicit outcomes and capability interfaces. The doctrine requires declared composition and interpreters, not one universal effect stack.

## 50.4 Markov kernels idealize providers

A remote language model is not necessarily a stationary kernel identified by model name and seed. Providers change infrastructure, hidden prompts, batching, moderation, and model weights. Distributional identity is therefore an operational claim with uncertainty. Retained material and temporal strata remain necessary.

## 50.5 Optic laws can conflict with global constraints

A local lens is most natural for independent product fields. Configuration validity can couple distant fields. Partial optics, validated reparameterizations, or dependent spaces are required. The system should reject invalid candidates rather than weaken laws to make every path writable.

## 50.6 Dependency graphs are declarations

The core can compute closure exactly from the graph, but it cannot know the graph is complete. Undeclared ambient reads—environment variables, current time, mutable files, provider aliases—are common sources of unsound reuse. Capability restriction, provenance instrumentation, and mutation tests are essential.

## 50.7 Decision policies remain political and product-relative

Lexicographic gates make policy explicit; they do not make it neutral. Choosing a noninferiority margin, cost budget, safety threshold, or human reviewer is an organizational decision. The artifact should identify and expose that policy rather than presenting it as mathematical inevitability.

## 50.8 Distributed production adds failure modes

The sandbox is local and sequential. A distributed implementation must establish store consistency, fencing, artifact durability, worker identity, secret policy, and operational SLOs. The semantics guide refinement but do not supply infrastructure automatically.

## 50.9 Adaptive optimization complicates inference

A fixed paired campaign is statistically simpler than adaptive candidate generation, early stopping, and repeated holdout use. A generalized engine must treat proposal history, selection bias, multiplicity, and confirmation evidence explicitly. Search sophistication should not arrive before experiment custody.

# 51. Research program

## 51.1 Mechanized free-plan kernel

Formalize the wiring syntax, normalization, typing, and folds in Lean, Coq, or Agda. Extract golden normal forms and test vectors for the Go implementation. Prove conservativity under signature extension and soundness of the static effect algebra.

A modest target is preferable to proving the entire system: schemas, ports, sequence, tensor, permutation, copy, discard, and finite effect summaries.

## 51.2 General optics and dependent spaces

Replace the lens-only sandbox with a serializable optic language supporting products, sums, optional branches, traversals, and validated reparameterizations. Study composition with dependency declarations so that focusing a parameter can automatically derive semantic targets.

A useful result would be an optic whose residual/context object directly generates an invalidation witness.

## 51.3 Provenance-semiring interpretation

Interpret plans and incremental builds into provenance polynomials or semimodules. This can provide item-level explanations of which source revisions, parameters, and operations contributed to an artifact or metric. It can also compute precise invalidation and common-prefix sharing.

The challenge is keeping provenance compact for large corpora. Factorized or Merkle-linked representations are likely necessary.

## 51.4 Categorical stochastic campaigns

Develop an explicit Markov-category semantics for trial plans, couplings, repeated measures, missingness, and adaptive proposals. Distinguish random-variable coupling from shared material replay. Connect statistical estimators to the categorical construction without burying assumptions in implementation code.

## 51.5 Resource-enriched optimization

Model latency, dollars, tokens, memory, energy, privacy, and disclosure as ordered commutative monoids or enriched hom-values. Investigate when sequential/tensor resource summaries are exact, upper bounds, or empirical distributions. This can support static budget rejection and compositional capacity planning.

## 51.6 Open campaign composition

Treat campaigns, build coordinators, release managers, and canary controllers as open dynamical systems with compatible interfaces. Study composition of their safety properties and how event traces implement categorical wiring at runtime.

A practical question is whether an offline campaign, shadow campaign, and canary can be composed as one higher-level protocol while retaining each subsystem's durable state.

## 51.7 Certified plugin refinement

Define machine-readable refinement contracts between abstract generators and concrete implementations. Examples include exact/ANN retrieval relations, local/remote reranker equivalence, legacy/new query path compatibility, and simulator/production runner correspondence.

Certificates can combine proof, exhaustive finite checking, property tests, benchmark distributions, and signed human review.

## 51.8 Learning proposers as ordinary plugins

Implement grid, random, Bayesian, evolutionary, gradient, and language-model proposers over the same observation interface. Compare their sample efficiency only after preserving candidate identity, selection history, and confirmation holdout. This separates optimizer research from experiment-engine correctness.

## 51.9 Cross-language SDK

Specify canonical schemas and RPC for plugins in Go, Python, Rust, and TypeScript. Use a language-neutral canonical encoding and golden vectors. Preserve typed operation descriptors and campaign coordinates while allowing domain-native implementation.

The kernel should remain language-agnostic at the protocol level even if one trusted implementation is in Go.

## 51.10 RAG field benchmark

Construct a benchmark that evaluates optimization architectures rather than only retrievers. It should include:

- indexing and query interventions with known invalidation closure;
- stochastic provider stubs;
- authorization constraints;
- incremental corpus changes;
- answer and agent outcomes;
- frontend projections;
- interrupted/distributed campaign execution;
- promotion and rollback decisions.

Success would measure whether a system produces correct, reproducible evidence under changes and failures, not merely whether it finds a high score.

# 52. Conclusion

Optimization needs a semantics of systems before it needs a more sophisticated search loop. The central construction of this thesis is a small but strong doctrine:

- a typed signature names domain objects and primitive operations;
- a free wiring syntax owns sequence, tensor, and structural composition;
- plugins extend generators and models without extending composition rules;
- structural folds induce execution, effects, dependencies, resources, identity, and provenance;
- parameterized morphisms make configuration compose with systems;
- optics make local interventions lawful and explicit;
- Markov kernels and couplings make stochastic comparison honest;
- ordered metrics and gates preserve constraints and partial preference;
- event-sourced campaigns give optimization a durable operational semantics.

The plugin boundary follows from the mathematics. Fine-grained plugins are models of a signature and are valuable when multiple interpretations matter. Coarse domain grafts implement stable campaign ports and let existing systems participate without invasive decomposition. The core remains simple not by omitting semantics, but by owning only semantics that must be universal: composition, identity, pairing, missingness, gate order, and event validity.

The executable `opfield` sandbox demonstrates the construction in ordinary Go. It composes typed plans, interprets them in more than one way, checks lawful interventions, couples exact paired trials, resumes an interrupted campaign, and optimizes both a miniature RAG system and an unrelated stochastic quadratic objective. Its limitations are explicit: it is a reference kernel, not a production scheduler, statistical package, or proof assistant.

Applied to RAG, the doctrine turns indexing and querying into one compositional field without collapsing their distinctions. A chunking intervention changes a build prefix and invalidates downstream artifacts. A fusion intervention changes only a query suffix. An agent-policy intervention requires trajectory evaluation. A serving-policy intervention may be operational or outcome-changing depending on deadlines and fallback. Every candidate carries its causal claim, and every promotion is backed by exact release, workload, trace, and decision identities.

This architecture makes room for future methods—Bayesian search, differentiable learning, language-model proposers, incremental indexing, distributed workers, shadow traffic, and canary control—without making any one of them the definition of optimization. They become plugins and interpreters grafted onto a field whose basic laws remain stable.

The resulting research program is both formal and practical. The free-plan and reducer kernels are small enough to prove or model-check. Plugin refinement and quality remain testable and empirical. Product-specific semantics remain in the products. That division of labor is the principal result: a composable optimization architecture can be open to new domains and methods while preserving a small, reviewable semantic backbone.
EOF
wc -l -w -c /mnt/data/opfield_work/thesis/A_Categorical_Backbone_for_Composable_Optimization.md
```

<details><summary>💭 Thinking</summary>

**Appended formal appendices and fixed manuscript Markdown and LaTeX issues**

</details>

```unknown
bash -lc cat /home/oai/skills/docx/SKILL.md && printf '\n---PDF---\n' && cat /home/oai/skills/pdfs/SKILL.md
```

The formal core now separates exact probability semantics from seeded execution, with whole-system meanings induced by kernel folds over typed plugin signatures. The 138-page manuscript is undergoing publication QA.

<details><summary>💭 Thinking</summary>

**Created and rendered a styled doctoral-style DOCX with TOC and branding**

</details>

```unknown
bash -lc cat /home/oai/skills/docx/tasks/toc_workflow.md | sed -n '1,320p'; printf '\n---insert help---\n'; python /home/oai/skills/docx/scripts/insert_toc.py --help | sed -n '1,240p'
```

<details><summary>💭 Thinking</summary>

**Rendering remaining PDF pages and comparing outputs**

</details>

```unknown
bash -lc python /home/oai/skills/pdfs/scripts/pdf_preflight.py --help | sed -n '1,240p'; echo '--- a11y'; python /home/oai/skills/docx/scripts/a11y_audit.py --help | sed -n '1,200p'; echo '--- images'; python /home/oai/skills/docx/scripts/images_audit.py --help | sed -n '1,200p'
```

<details><summary>💭 Thinking</summary>

**Inspected, verified, and packaged project deliverables and documentation**

</details>


---

> continue

# *A Categorical Backbone for Composable Optimization*

The standalone thesis and executable sandbox are complete.

## Publications and implementation

- [Download the 142-page PDF](sandbox:/mnt/data/opfield_output/A_Categorical_Backbone_for_Composable_Optimization.pdf)
- [Download the editable DOCX](sandbox:/mnt/data/opfield_output/A_Categorical_Backbone_for_Composable_Optimization.docx)
- [Download the Markdown manuscript](sandbox:/mnt/data/opfield_output/A_Categorical_Backbone_for_Composable_Optimization.md)
- [Download the self-contained `opfield` Go sandbox](sandbox:/mnt/data/opfield_output/opfield-sandbox.zip)
- [Download the complete source bundle](sandbox:/mnt/data/opfield_output/A_Categorical_Backbone_for_Composable_Optimization_Source.zip)
- [Download SHA-256 checksums](sandbox:/mnt/data/opfield_output/SHA256SUMS.txt)

The thesis is approximately **31,000 words**, with **52 chapters and eight appendices**. The source bundle contains the manuscript, figure sources, rendered figures, implementation, retained experiment artifacts, document-build scripts, and QA reports.

## Principal architectural result

The proposed backbone is not an optimizer and not a RAG framework. It is a small semantic substrate on which optimizers and optimized domains can be composed.

Its central construction has seven parts.

### 1. A typed signature

A domain plugin contributes a signature

\[
\Sigma =
(\mathsf{Ob},
\mathsf{Gen},
\mathsf{dom},
\mathsf{cod},
\mathsf{ann}),
\]

where:

- \(\mathsf{Ob}\) contains versioned domain schemas;
- \(\mathsf{Gen}\) contains primitive operation symbols;
- \(\mathsf{dom}\) and \(\mathsf{cod}\) assign typed ports;
- \(\mathsf{ann}\) declares effects, dependencies, determinism, cacheability, resources, disclosure, and applicable laws.

Plugins extend the vocabulary. They do **not** add new notions of sequencing, parallel composition, identity, copying, discarding, trial pairing, or campaign completion.

### 2. A free typed wiring language

From \(\Sigma\), the kernel constructs a free symmetric monoidal, gs-monoidal-style wiring category \(\mathsf W(\Sigma)\). Plans are composed from:

- primitive generators;
- identity;
- sequential composition;
- tensor or parallel composition;
- permutations;
- explicit copy;
- explicit discard.

This produces the main plugin-safety result:

> A plugin can introduce new primitive meanings without changing the composition laws or invalidating existing plans.

Every whole-plan interpretation is induced by a structural fold. Execution, static effect analysis, dependency closure, cost estimation, provenance, visualization, deployment compilation, and replay therefore consume the same plan rather than reconstructing incompatible graphs.

This use of free compositional syntax is related to categorical treatments of parameterized learning, free gs-monoidal categories, and compositional models of computation. citeturn149553search0turn518698search0turn149553search3

### 3. Parameterized morphisms

An optimizable component is represented by

\[
f:P\otimes A\longrightarrow B,
\]

rather than by a function plus an unrelated dictionary of parameter names.

Composition tensors the parameter objects:

\[
(P,f):A\to B,\qquad
(Q,g):B\to C
\]

compose to

\[
(P\otimes Q,\;
(P\otimes Q)\otimes A
\longrightarrow C).
\]

This is the role of the `Para` construction. Parameter structure follows system structure. Optimizer-facing coordinates are introduced separately through reparameterization:

\[
r:R\longrightarrow P.
\]

A grid optimizer, Bayesian proposer, gradient method, or language-model proposer can therefore use convenient coordinates without changing the implementation parameter object or system identity. The construction is informed by categorical accounts of backpropagation and compositional learning, but the thesis generalizes it to discrete, stochastic, constrained, and non-differentiable optimization. citeturn149553search0turn518698search0

### 4. Lawful interventions as optics

A candidate does not replace arbitrary fields in a string map. It applies a lawful optic to a release or system specification.

For a simple lens:

\[
\mathsf{get}:\Theta\to P,
\qquad
\mathsf{put}:\Theta\times P\to\Theta,
\]

the kernel checks the familiar laws:

\[
\mathsf{put}(\theta,\mathsf{get}(\theta))=\theta,
\]

\[
\mathsf{get}(\mathsf{put}(\theta,p))=p,
\]

\[
\mathsf{put}(\mathsf{put}(\theta,p),q)
=
\mathsf{put}(\theta,q).
\]

A complete intervention also contains:

- semantic class;
- direct dependency targets;
- transitive invalidation closure;
- typed replacement value;
- causal hypothesis;
- minimum evaluation fidelity.

The optic answers *how* a local value changes. The causal declaration answers *what that change invalidates*. General optics provide the larger mathematical setting for products, sums, optional branches, traversals, and parameterized transformations. citeturn149553search2

### 5. Stochastic trials as Markov kernels

For candidate parameter \(\theta\), a trial is modeled as a Markov kernel

\[
K_\theta:X\rightsquigarrow O,
\]

not merely a deterministic callback.

Comparing an incumbent and candidate requires a coupling

\[
\Gamma_x\in
\mathcal D(O_b\times O_c)
\]

with the correct marginals. Independent samples are only one possible coupling and are often statistically inefficient.

The executable kernel implements exact coordinates and domain-separated deterministic seeds:

\[
(\mathsf{campaign},
\mathsf{case},
\mathsf{repeat},
\mathsf{arm})
\longmapsto
\omega.
\]

This makes common-random-number pairing structural rather than conventional. A production runner may strengthen it through retained provider responses, traffic pairing, or an explicitly supplied coupling kernel.

Markov categories provide the abstract setting for stochastic composition, copying, discarding, and conditional-independence structure. citeturn518698search1turn149553search3

### 6. Ordered decisions rather than universal scalar scores

Metrics carry identity, direction, unit, missingness, and uncertainty. Candidate-minus-baseline differences are oriented so that positive means improvement:

\[
\Delta_j
=
s_j(m_j^c-m_j^b),
\qquad
s_j\in\{-1,+1\}.
\]

Hard constraints first determine the feasible subset:

\[
F=
\{\theta\mid g_i(\theta)\le 0
\text{ for every hard gate }i\}.
\]

Preference then operates through product preorders, Pareto dominance, lexicographic policies, or an explicitly authorized scalarization.

The default decision program is:

1. security;
2. integrity and contract validity;
3. exact paired coverage;
4. protected-stratum noninferiority;
5. target improvement;
6. resource envelope;
7. Pareto or product preference;
8. human or deployment authorization.

This preserves the distinction between eligibility and preference. Recall, dollars, latency, disclosure, failure rate, and user outcome do not acquire a natural additive unit merely because software can multiply them by weights. Ordered resource structures and compositional resource theories motivate this treatment. citeturn443270search2

### 7. Campaigns as event-sourced open dynamical systems

A campaign is modeled as a state-transition system or coalgebra:

\[
\gamma:S\longrightarrow F(S),
\]

with an append-only event vocabulary and a pure partial reducer:

\[
\rho:S\times E\rightharpoonup S.
\]

The kernel owns transitions for:

- campaign creation;
- candidate registration;
- baseline and candidate trial completion;
- paired-report construction;
- decision recording;
- terminal selection;
- cancellation;
- interruption and resume.

Resume is not a special recovery branch. Given an event prefix \(P\),

\[
s_P=\rho^\ast(s_0,P),
\]

continuation emits only events missing from \(s_P\). Re-running a terminal campaign appends nothing.

This gives campaigns the character of open dynamical systems: proposers, runners, stores, policies, deployment authorities, and environments attach through explicit interfaces while transition validity remains kernel-owned. citeturn443270search0turn443270search1

## The two plugin surfaces

A principal conclusion is that one generic “plugin interface” is insufficient.

### Low-level operation plugins

These are appropriate when alternate interpretation is valuable. A low-level plugin registers:

- versioned schemas and codecs;
- typed primitive operations;
- effects and resource annotations;
- dependency labels;
- deterministic and cacheability claims;
- implementations;
- executable laws or certification references.

Examples include:

```text
normalize source revision
chunk document
generate representation
embed batch
build lexical index
build vector index
retrieve one channel
collapse representations
fuse rankings
authorize candidates
rerank
assemble context
validate answer contract
```

The registry is transactional. A plugin becomes visible only after all schemas, operations, codecs, collisions, and required laws validate. Existing plan syntax and existing interpreters remain unchanged.

The design is analogous to algebraic-effect signatures and handlers: plugins declare operations while interpreters or handlers determine their execution meaning. citeturn518698search2

### High-level domain grafts

These are appropriate for existing products that should not be rewritten into primitive operations.

A domain graft supplies six narrow ports:

```go
type Space interface { ... }
type Proposer interface { ... }
type Workload interface { ... }
type Runner interface { ... }
type Policy interface { ... }
type Store interface { ... }
```

A `Runner` may:

- call a complete GEC retrieval and answer service;
- run a Garden multi-turn calibration conversation;
- launch an ANN certification job;
- execute an RAG-TTC tool loop;
- invoke an unrelated numerical optimizer;
- submit work to an external scheduler.

The campaign kernel still controls candidate identity, exact coordinates, seed custody, metric validation, missingness, failures, comparison, ordered gates, resume, and terminality.

This permits progressive adoption:

- coarse product runners can participate immediately;
- high-value internal stages can later become typed primitive operations;
- products retain authorization, prompts, structured facts, UI schemas, and native evaluators.

## The `opfield` implementation

The sandbox is a standard-library-only Go module targeting Go 1.23 or later.

Its packages include:

| Package | Role |
|---|---|
| `core` | canonical envelopes, domain-separated digests, schemas, effects, outcomes |
| `plugin` | transactional registry, codecs, typed operation adapters, laws |
| `plan` | free typed plan syntax, validation, identity, generic folds |
| `engine` | executable reference interpretation |
| `artifact` | verified content-addressed local artifact storage |
| `para` | parameterized maps, composition, tensor, reparameterization |
| `optic` | lawful lenses and executable law checking |
| `prob` | finite distributions, kernels, composition, deterministic seed splitting |
| `metric` | oriented differences, dominance, Pareto fronts |
| `experiment` | spaces, patches, candidates, workloads, coordinates, reports |
| `decision` | pass/fail/indeterminate gates and ordered policies |
| `campaign` | append-only events, reducer, paired engine, resume |
| `domain/ragtoy` | fine- and coarse-grained RAG graft |
| `domain/quadratic` | unrelated stochastic optimization graft |

## Executable demonstrations

### RAG graft

The miniature RAG implementation includes:

- deterministic corpus and chunking;
- lexical retrieval;
- hashed semantic vectors;
- weighted fusion;
- stable ranking and tie-breaking;
- content-addressed index artifacts;
- typed build and query plans;
- lawful configuration lenses;
- dependency-aware build reuse;
- nine relevance cases;
- seven one-parameter interventions;
- three paired repeats;
- constraint-first promotion policy.

The resulting campaign contains **239 immutable events**. Query-only interventions reuse the baseline index; chunking interventions receive distinct build artifacts. The selected candidate is `chunk-34` for this deliberately small workload.

### Quadratic graft

The second example optimizes a noisy quadratic objective without using the plan, plugin-operation, artifact, or RAG layers. It uses only the high-level campaign ports.

It produces **74 events** and selects \(x=3\). This demonstrates that the campaign protocol is not a disguised retrieval engine.

## Verification performed

The module was extracted from its final ZIP into a clean directory and successfully ran:

```text
go test ./...
go vet ./...
go test -race ./...
```

Both demonstrations were then regenerated from the extracted archive:

```text
make demo-rag
make demo-quadratic
```

The regenerated campaigns produced 239 and 74 events respectively.

Document verification included:

- visual inspection of all 142 pages;
- correction and reinspection of the one clipped equation found during QA;
- validation of all 70 static table-of-contents page references;
- DOCX accessibility audit: zero high-, medium-, or low-severity findings;
- PDF preflight: opens correctly, not encrypted, not image-only, no XFA, no warnings;
- tagged Letter-size PDF with no structural suspects.

## Scope of the formal claims

The thesis separates four levels of assurance:

- properties established by construction in the small kernel;
- executable algebraic and state-machine laws;
- proof sketches and explicit proof obligations;
- empirical obligations belonging to plugins and product domains.

It does **not** claim a machine-checked proof that arbitrary plugins are semantically correct, that model-generated answers are true, or that every distributed implementation refines the reference interpreter. Those remain certification, testing, statistical, and operational obligations. The contribution is to make their boundaries explicit and composable rather than hiding them inside callbacks.

# A Categorical Backbone for Composable Optimization

The thesis and executable sandbox are complete.

## Deliverables

- [Thesis — PDF](sandbox:/mnt/data/opfield_output/A_Categorical_Backbone_for_Composable_Optimization.pdf)
- [Thesis — editable DOCX](sandbox:/mnt/data/opfield_output/A_Categorical_Backbone_for_Composable_Optimization.docx)
- [Thesis — Markdown source](sandbox:/mnt/data/opfield_output/A_Categorical_Backbone_for_Composable_Optimization.md)
- [Self-contained `opfield` Go sandbox](sandbox:/mnt/data/opfield_output/opfield-sandbox.zip)
- [Complete study source bundle](sandbox:/mnt/data/opfield_output/A_Categorical_Backbone_for_Composable_Optimization_Source.zip)
- [SHA-256 checksums](sandbox:/mnt/data/opfield_output/SHA256SUMS.txt)

The thesis is **142 pages**, approximately **31,600 words**, with **52 numbered chapters, eight appendices, and sixteen figures**.

## Mathematical result

The proposed optimization field is built from six interacting structures.

### 1. A typed signature and free wiring category

A plugin contributes a typed signature

\[
\Sigma =
(\mathsf{Ob},\mathsf{Gen},\mathsf{dom},\mathsf{cod},\mathsf{ann}),
\]

consisting of schemas, primitive operations, signatures, and semantic annotations.

The kernel generates a free wiring language over that signature. It owns:

\[
\mathsf{id},
\qquad
g\circ f,
\qquad
f\otimes g,
\qquad
\mathsf{copy},
\qquad
\mathsf{drop},
\qquad
\mathsf{permute}.
\]

Plugins can add primitive generators, but they cannot redefine composition, identity, copying, discarding, plan normalization, or structural identity.

A plan is therefore an intensional object. Its execution, effect analysis, dependency analysis, cost model, identity, visualization, provenance query, or deployment graph are separate interpretations induced by structural folds.

### 2. The Para construction for optimized systems

A parameterized component is modeled as

\[
(P,f) : A \rightsquigarrow B,
\qquad
f:P\otimes A\to B.
\]

Composition tensors parameter objects:

\[
(P,f);(Q,g)
=
\left(
P\otimes Q,\;
(P\otimes Q)\otimes A
\to
Q\otimes B
\to
C
\right).
\]

This replaces the usual global dictionary of unrelated parameter names. Parameter structure follows system structure.

Reparameterization is explicit. An optimizer may work in coordinates \(P'\) while the system consumes \(P\), provided there is a declared map

\[
r:P'\to P.
\]

This permits grids, constrained coordinates, learned embeddings, hierarchical spaces, and optimizer-specific parameterizations without changing the system definition.

### 3. Optics for lawful local interventions

A candidate patch is not an arbitrary mutation callback. A lens or more general optic focuses on one lawful part of the complete configuration:

\[
\mathsf{get}:S\to A,
\qquad
\mathsf{put}:S\times A\to S.
\]

The implementation checks the lens laws:

\[
\mathsf{put}(s,\mathsf{get}(s))=s,
\]

\[
\mathsf{get}(\mathsf{put}(s,a))=a,
\]

\[
\mathsf{put}(\mathsf{put}(s,a_1),a_2)
=
\mathsf{put}(s,a_2).
\]

A complete intervention also records its semantic class, direct targets, transitive dependency closure, hypothesis, and required evaluation fidelity. The optic establishes lawful update behavior; the dependency graph establishes causal invalidation.

### 4. Markov kernels and experimental coupling

A stochastic trial is modeled as a Markov kernel

\[
K_\theta:X\rightsquigarrow O.
\]

Baseline and candidate comparison is not merely two independent samples. It is a coupling

\[
\Gamma_x
\in
\mathcal D(O_b\times O_c)
\]

whose marginals are the baseline and candidate outcome distributions.

The executable sandbox realizes a common-random-number coupling through exact case/repeat coordinates and domain-separated seed splitting. A production integration can strengthen this using retained model responses, replay artifacts, or application-specific coupling kernels.

### 5. Ordered decision semantics

Metrics define oriented preorders rather than one universal scalar. The framework supports:

- hard eligibility constraints;
- three-valued decisions: pass, fail, and indeterminate;
- Pareto dominance;
- ordered gate sequences;
- final lexicographic or product-owned preference.

This prevents recall, latency, cost, disclosure, failure, and user outcome from being silently treated as naturally commensurable.

### 6. Event-sourced campaign dynamics

An optimization campaign is an open transition system whose observable behavior is an immutable event history.

Candidate registration, paired trial completion, comparison, decision, selection, cancellation, and terminal completion have explicit transition order. Resume is semantic continuation from the reduced event prefix, not reconstruction from miscellaneous temporary files.

The campaign kernel owns:

- campaign and candidate identity;
- exact case/repeat/arm coordinates;
- pairing;
- failure and missingness preservation;
- metric validation;
- gate order;
- append-only event custody;
- terminal immutability.

## Plugin architecture

The thesis concludes that one plugin interface is insufficient. The sandbox implements two extension levels.

### Low-level operation plugins

These are used when operations should be visible to several interpreters.

A plugin transaction registers:

- versioned schemas;
- typed operation signatures;
- codecs;
- implementations;
- determinism and cacheability declarations;
- effects and remote-disclosure properties;
- dependency labels;
- resource and cost estimates;
- executable laws.

Registration is transactional. A collision or failed law leaves the registry unchanged.

Operations exchange canonical schema-bearing envelopes rather than `map[string]any`. The plan kernel remains closed over its structural constructors, while operation generators and interpreters remain open.

### High-level domain grafts

These wrap a complete existing application without requiring it to be rewritten as primitive plan nodes.

A graft supplies six interfaces:

```go
type Space interface {
    Baseline(context.Context) (Snapshot, error)
    Patches(context.Context, Snapshot) ([]Patch, error)
    Apply(context.Context, Snapshot, Patch) (Candidate, error)
}

type Proposer interface {
    Propose(context.Context, Space, History) ([]Patch, error)
}

type Workload interface {
    ID() Digest
    Cases(context.Context) ([]Case, error)
}

type Runner interface {
    Run(context.Context, TrialRequest) TrialResult
}

type Policy interface {
    Decide(context.Context, Candidate, PairedReport) Decision
}

type Store interface {
    Append(context.Context, ExpectedPosition, Event) error
    Load(context.Context) ([]Event, error)
}
```

A `Runner` can execute a typed plan, call a GEC service, run a Garden conversation, invoke an existing CLI, submit a remote build, or replay an artifact. The campaign protocol remains unchanged.

This creates the intended grafting boundary:

```text
domain-specific meaning
    Space / Workload / Runner / Policy
                    |
                    v
generic optimization custody
 identity / pairing / comparison / events / gates
                    |
                    v
optional fine-grained typed plans
 schemas / generators / effects / interpreters
```

## Sandbox implementation

The standalone `opfield` module uses only the Go standard library and includes:

| Package | Function |
|---|---|
| `core` | canonical envelopes, schemas, digests, effects, outcomes |
| `plugin` | transactional registry and typed operation adapters |
| `plan` | free typed plan syntax, validation, normalization, folds |
| `engine` | reference execution interpreter |
| `para` | parameterized morphisms and reparameterization |
| `optic` | lawful lenses and law checking |
| `prob` | finite distributions, Markov kernels, seed splitting |
| `metric` | metric orientation, dominance, Pareto fronts |
| `experiment` | spaces, candidates, workloads, coordinates, paired reports |
| `decision` | ordered gates and three-valued decisions |
| `campaign` | event reducer, durable store, resume, terminal state |
| `artifact` | content-addressed native artifacts |
| `domain/ragtoy` | complete miniature indexing/query optimization graft |
| `domain/quadratic` | unrelated stochastic optimization graft |

The RAG graft includes deterministic chunking, lexical and hashed-semantic retrieval, typed build and query plans, dependency-aware artifact reuse, seven lawful interventions, nine evaluation cases, exact pairing, and promotion gates.

The quadratic graft has no RAG, indexing, or plan dependency. It demonstrates that the high-level optimization protocol is genuinely domain-neutral rather than a disguised RAG framework.

## Verification

The implementation was rechecked with:

```text
go test ./...
go vet ./...
go test -race ./...
```

All passed. The extracted sandbox ZIP was tested independently.

The RAG demonstration selected the lawful `chunk-34` intervention and rejected candidates that regressed protected recall. The quadratic demonstration selected the optimum candidate at \(x=3\). Campaign histories are append-only and resumable, and the demos emit content-addressed artifacts plus serialized build/query plans.

The DOCX passed its accessibility audit with no findings. The final PDF has **142 pages**, opens correctly, is unencrypted and searchable, and passed structural preflight without warnings.


---

> what does port mean in the context of "open ports of a campaign machine'

In that phrase, **port means an explicitly typed interaction boundary between the campaign state machine and something outside it**.

Think of the campaign machine as having an internal state \(S\) and transition rules that the kernel owns. It cannot do everything itself: somebody must propose candidates, execute trials, persist events, decide gates, perhaps activate a winning release. Those capabilities attach at its *open ports*.

A useful abstract picture is:

\[
\boxed{\text{Proposer}}
\longrightarrow
\boxed{
\begin{array}{c}
\text{Campaign}\\
\text{machine}
\end{array}}
\longrightarrow
\boxed{\text{Runner}}
\]

with other ports for workload, store, policy, artifact resolution, deployment, etc. More formally, you can regard the campaign as an **open system**

\[
C : I \rightsquigarrow O
\]

whose boundary \(I,O\) describes the things its environment is allowed to supply or observe.

The important point is that a port is **not just a Go interface**. The interface is one implementation of the port. Semantically, the port specifies a protocol: the types of values exchanged, when exchanges are legal, what identities they carry, and which side owns which invariants.

For example, a runner port might have the conceptual signature

\[
\mathsf{Run} :
(\mathsf{Candidate},
 \mathsf{Case},
 \mathsf{Repeat},
 \mathsf{Seed})
\rightsquigarrow
\mathsf{TrialOutcome}.
\]

The campaign kernel controls the left-hand coordinates and requires the outcome to come back under exactly those coordinates. The plugin attached to that port controls *how* the experiment is actually run. It might run GEC, Garden, an ANN benchmark, a remote Kubernetes job, or a toy function.

That distinction is why the notion is useful architecturally:

```go
type Runner interface {
    Run(context.Context, TrialRequest) TrialResult
}
```

is the **software interface**, while

\[
\mathsf{TrialRequest}\rightsquigarrow\mathsf{TrialResult}
\]

together with its laws is the **semantic port**.

The campaign machine might have ports roughly like these:

| Port | Environment supplies | Kernel retains control of |
|---|---|---|
| **Candidate/proposer** | possible interventions | candidate identity and legality |
| **Workload** | cases to evaluate | exact case coordinates |
| **Runner** | execution of a trial | pairing, repeat and seed custody |
| **Artifact** | native outputs | artifact identity/reference |
| **Policy** | domain-specific gate interpretation | gate ordering and terminal semantics |
| **Store** | persistence mechanism | valid event transitions |
| **Activation** | actual production deployment | requirement that only an eligible candidate can be requested |

This matters because the campaign becomes **open without becoming semantically porous**. You can replace what is connected to a port without replacing the campaign laws.

For example:

```text
                     ┌── GEC runner
                     │
Candidate ──┐        │
Workload ───┼──▶ CAMPAIGN ◀── Runner port ─── Garden runner
Policy ─────┤        │
Store ──────┘        └── remote cluster runner
```

GEC and Garden can attach completely different operational worlds to the same runner port. The kernel still knows that:

\[
(b,i,r)
\]

must be compared with

\[
(c,i,r),
\]

not with some arbitrary candidate observation. It still knows missing trials cannot disappear. It still knows terminal campaigns cannot subsequently acquire unexplained events.

### Why call it a *port* rather than a plugin?

Because **plugin describes who is attached; port describes where and under what contract attachment is allowed**.

That distinction becomes important in the categorical treatment. An open system has a boundary. Composition happens by connecting compatible boundaries:

\[
A
\;\xrightarrow{\quad p \quad}\;
B
\]

or, for two open systems,

\[
F : X\otimes A \to Y\otimes B,
\qquad
G : Y\otimes B \to Z\otimes C,
\]

where the matching \(Y\otimes B\) boundary can be wired together.

So instead of saying:

> “The campaign has arbitrary callbacks.”

the design says:

> “The campaign exposes a small set of typed open ports, and external interpreters may inhabit those ports.”

That is considerably stronger.

It means the **closed semantic kernel** can remain tiny:

```text
candidate identity
trial coordinates
pairing
event reduction
metric validation
gate sequencing
terminality
```

while the **open boundary** contains everything likely to vary:

```text
candidate proposal
RAG building
query execution
LLM providers
evaluation suites
storage
distributed execution
deployment
```

This is also why the phrase **“open ports of the campaign machine”** is intentionally close to terminology from *open systems*, *open dynamical systems*, *operads/wiring diagrams*, and *structured/decorated cospans*. The boundary is first-class, and composition occurs by wiring boundaries together rather than by letting plugins reach arbitrarily into internal state.

A concrete RAG example makes the distinction sharper. Imagine this campaign:

```text
               Intervention
                    │
                    ▼
              ┌───────────┐
Corpus ──────▶│           │──────▶ Trial results
Workload ────▶│ Campaign  │
              │           │──────▶ Promotion evidence
              └───────────┘
                    │
                    ▼
                Activation
```

The campaign does **not** know how to build an HNSW index. Its build/runner port may be inhabited by:

```text
RAG-TTC implementation
    chunk
    embed
    build HNSW
    query
    measure recall/latency
```

Another inhabitant might be:

```text
GEC implementation
    open release
    hybrid search
    authorization
    reranking
    answer judging
```

They share the campaign semantics because they connect through the same port protocol, not because their internal systems look alike.

One terminological refinement I would make in the thesis is to distinguish **ports** from **operations**:

- **operation** = a primitive *inside* a typed plan, such as `Embed`, `Fuse`, `Rerank`;
- **port** = a boundary where the *whole machine* interacts with an external system;
- **plugin** = an implementation/module that can supply operations or inhabit ports;
- **adapter** = the concrete code translating an existing system to a port protocol.

So the conceptual hierarchy is:

\[
\boxed{\text{kernel}}
\quad
\overset{\text{ports}}{\longleftrightarrow}
\quad
\boxed{\text{plugins/adapters}}
\]

while inside the kernel-controlled plan language:

\[
\boxed{\text{plan}}
=
\text{composition of typed operations}.
\]

That distinction is one of the more important architectural ideas in the thesis: **make the mathematics closed where correctness depends on it, and open the system only at explicitly modeled ports.**


---

> give me code examples. also whats that squiggly arrow you use,

The squiggly arrow I used,

\[
A \rightsquigarrow B
\]

was informal notation for “an effectful / stochastic / externally interpreted computation from \(A\) to \(B\),” rather than an ordinary pure function

\[
A \to B.
\]

In the probabilistic part of the thesis, it is most naturally read as a **Markov kernel**:

\[
K : A \rightsquigarrow B
\]

meaning that each \(a\in A\) determines a probability distribution over \(B\):

\[
K(a) \in \mathcal D(B).
\]

So a trial runner is better modeled as

\[
\mathsf{Run} :
\mathsf{TrialRequest}
\rightsquigarrow
\mathsf{TrialOutcome}
\]

because the same request can yield different model outputs, latency, failures, etc.

In Go, though, the port still looks ordinary:

```go
type Runner interface {
	Run(ctx context.Context, req TrialRequest) TrialOutcome
}
```

The stochastic/effectful semantics are in the contract, not Go's arrow syntax.

## 1. Simplest possible campaign port

Here is the most basic version:

```go
package campaign

import "context"

type TrialRequest struct {
	CandidateID string
	CaseID      string
	Repeat      int
	Seed        uint64
}

type TrialOutcome struct {
	Score float64
	Err   error
}

type Runner interface {
	Run(context.Context, TrialRequest) TrialOutcome
}
```

The campaign owns the coordinates:

```go
func runCell(
	ctx context.Context,
	runner Runner,
	candidateID string,
	caseID string,
	repeat int,
) TrialOutcome {
	req := TrialRequest{
		CandidateID: candidateID,
		CaseID:      caseID,
		Repeat:      repeat,
		Seed:        deriveSeed(candidateID, caseID, repeat),
	}

	return runner.Run(ctx, req)
}
```

The important ownership distinction is:

```text
Campaign owns:
    CandidateID
    CaseID
    Repeat
    Seed

Runner owns:
    how the candidate is actually evaluated
```

The runner cannot silently decide, “I'll use repeat 7 instead,” because the coordinate is part of the request.

---

## 2. Two completely different plugins inhabiting the same port

A toy numerical plugin:

```go
type QuadraticRunner struct{}

func (QuadraticRunner) Run(
	ctx context.Context,
	req TrialRequest,
) TrialOutcome {
	x := candidateValue(req.CandidateID)

	noise := deterministicNoise(req.Seed)

	score := -(x-3)*(x-3) + noise

	return TrialOutcome{
		Score: score,
	}
}
```

And a RAG plugin:

```go
type RAGRunner struct {
	Releases ReleaseStore
	Cases    CaseStore
}

func (r *RAGRunner) Run(
	ctx context.Context,
	req TrialRequest,
) TrialOutcome {
	release, err := r.Releases.Open(req.CandidateID)
	if err != nil {
		return TrialOutcome{Err: err}
	}

	tc, err := r.Cases.Get(req.CaseID)
	if err != nil {
		return TrialOutcome{Err: err}
	}

	result, err := release.Query(ctx, QueryRequest{
		Text: tc.Query,
		Seed: req.Seed,
	})
	if err != nil {
		return TrialOutcome{Err: err}
	}

	return TrialOutcome{
		Score: recallAtK(result.Hits, tc.ExpectedDocs),
	}
}
```

The campaign machinery does not care that one runner evaluates a quadratic and the other runs a whole RAG release.

That is what I mean by a **port**.

---

# 3. A port with a stronger semantic protocol

Usually I would make the interface richer than just `Run`.

```go
type Runner interface {
	Describe() RunnerDescriptor

	Run(
		ctx context.Context,
		req TrialRequest,
		sink ObservationSink,
	) TrialResult
}

type RunnerDescriptor struct {
	ID            string
	Version       string
	Determinism   Determinism
	Effects       []Effect
	Capabilities  []Capability
}

type Determinism int

const (
	Deterministic Determinism = iota
	SeedDeterministic
	Stochastic
)

type Effect string

const (
	EffectNetwork       Effect = "network"
	EffectModelProvider Effect = "model-provider"
	EffectFilesystem    Effect = "filesystem"
)
```

Now the interface represents more of the semantic port.

For example, a campaign can reject an incompatible runner before execution:

```go
func ValidateRunner(
	spec CampaignSpec,
	runner Runner,
) error {
	d := runner.Describe()

	if spec.RequireSeedControl &&
		d.Determinism == Stochastic {
		return fmt.Errorf(
			"campaign requires seed-controlled runner",
		)
	}

	return nil
}
```

So the plugin isn't merely “something with the right method.”

It has to satisfy the protocol associated with the port.

---

# 4. Workload as another port

The workload can also be external.

```go
type Case struct {
	ID    string
	Input []byte
}

type Workload interface {
	ID() string
	Cases(context.Context) ([]Case, error)
}
```

A static benchmark:

```go
type StaticWorkload struct {
	cases []Case
}

func (w StaticWorkload) ID() string {
	return "gec-retrieval-v3"
}

func (w StaticWorkload) Cases(
	ctx context.Context,
) ([]Case, error) {
	return append([]Case(nil), w.cases...), nil
}
```

A production-shadow workload could implement the exact same port:

```go
type ShadowTrafficWorkload struct {
	Store TraceStore
}

func (w ShadowTrafficWorkload) ID() string {
	return "production-shadow-2026-08-09"
}

func (w ShadowTrafficWorkload) Cases(
	ctx context.Context,
) ([]Case, error) {
	traces, err := w.Store.Sample(ctx, 500)
	if err != nil {
		return nil, err
	}

	out := make([]Case, 0, len(traces))

	for _, t := range traces {
		out = append(out, Case{
			ID:    t.RequestID,
			Input: t.CanonicalInput,
		})
	}

	return out, nil
}
```

Again:

```text
campaign
   |
   +--- Workload port ---> static benchmark plugin
   |
   +--- Workload port ---> shadow traffic plugin
```

Same boundary, different inhabitant.

---

# 5. Candidate proposal as a port

The optimizer itself should also be replaceable.

```go
type Candidate struct {
	ID     string
	Config Config
}

type History struct {
	Completed []Evaluation
}

type Proposer interface {
	Propose(
		ctx context.Context,
		baseline Candidate,
		history History,
	) ([]Candidate, error)
}
```

A grid proposer:

```go
type GridProposer struct {
	Weights []float64
}

func (g GridProposer) Propose(
	ctx context.Context,
	baseline Candidate,
	history History,
) ([]Candidate, error) {
	var out []Candidate

	for _, w := range g.Weights {
		cfg := baseline.Config
		cfg.VectorWeight = w

		out = append(out, Candidate{
			ID:     fmt.Sprintf("vector-weight-%.2f", w),
			Config: cfg,
		})
	}

	return out, nil
}
```

A Bayesian optimizer could inhabit exactly the same port:

```go
type BayesianProposer struct {
	Model SurrogateModel
}

func (p *BayesianProposer) Propose(
	ctx context.Context,
	baseline Candidate,
	history History,
) ([]Candidate, error) {
	xs := encodeObservations(history)

	next := p.Model.Next(xs)

	return []Candidate{
		decodeCandidate(baseline, next),
	}, nil
}
```

Or even an LLM-backed proposer.

The campaign does not need to know how proposals are generated.

---

# 6. Why the campaign state itself should *not* be exposed

A bad interface would look like:

```go
type Plugin interface {
	Run(c *Campaign)
}
```

Then a plugin could do:

```go
func (p EvilPlugin) Run(c *Campaign) {
	c.Completed = true
	c.Winner = "my-candidate"
	c.Results = nil
}
```

You've lost the semantics.

A better interface only exposes legal interaction points:

```go
type Proposer interface {
	Propose(context.Context, ProposalRequest) ProposalResult
}

type Runner interface {
	Run(context.Context, TrialRequest) TrialResult
}

type Policy interface {
	Decide(context.Context, DecisionRequest) Decision
}
```

The kernel alone performs state transitions:

```go
func (m *Machine) Apply(e Event) error {
	next, err := Reduce(m.state, e)
	if err != nil {
		return err
	}

	m.state = next
	return nil
}
```

For example:

```go
func Reduce(s State, e Event) (State, error) {
	switch e := e.(type) {

	case TrialCompleted:
		if s.Status != Running {
			return State{}, ErrIllegalTransition
		}

		if !s.HasCandidate(e.CandidateID) {
			return State{}, ErrUnknownCandidate
		}

		key := CellKey{
			CandidateID: e.CandidateID,
			CaseID:      e.CaseID,
			Repeat:      e.Repeat,
		}

		if s.Results.Contains(key) {
			return State{}, ErrDuplicateCell
		}

		s.Results = s.Results.Put(key, e.Result)
		return s, nil

	default:
		return State{}, ErrUnknownEvent
	}
}
```

The plugin can *request or produce something through a port*.

It cannot mutate campaign truth.

That is the architectural payoff.

---

# 7. Ports can themselves be typed by input/output objects

This is where the categorical language becomes useful.

Suppose we have:

```go
type Port[A, B any] interface {
	Invoke(context.Context, A) (B, error)
}
```

Then:

```go
type TrialPort = Port[TrialRequest, TrialOutcome]
type ProposalPort = Port[ProposalRequest, ProposalResult]
type DecisionPort = Port[DecisionRequest, Decision]
```

You can write adapters:

```go
type FuncPort[A, B any] struct {
	F func(context.Context, A) (B, error)
}

func (p FuncPort[A, B]) Invoke(
	ctx context.Context,
	a A,
) (B, error) {
	return p.F(ctx, a)
}
```

Composition looks like ordinary typed function composition:

```go
func Compose[A, B, C any](
	f Port[A, B],
	g Port[B, C],
) Port[A, C] {
	return FuncPort[A, C]{
		F: func(ctx context.Context, a A) (C, error) {
			b, err := f.Invoke(ctx, a)
			if err != nil {
				var zero C
				return zero, err
			}

			return g.Invoke(ctx, b)
		},
	}
}
```

This corresponds roughly to:

\[
A \to B,\qquad
B \to C
\]

giving

\[
A \to C.
\]

Once those operations can be stochastic/effectful, I might write:

\[
A \rightsquigarrow B,
\qquad
B \rightsquigarrow C
\]

and compose them as effectful arrows.

---

# 8. What the squiggly arrow means mathematically

There isn't one universal meaning for `\rightsquigarrow`. Authors use it differently.

In **this thesis**, I used it mostly as a visual distinction for a computation that isn't being treated as an ordinary deterministic function.

Three cases matter.

### Ordinary deterministic function

\[
f:A\to B
\]

Every \(a\) determines exactly one \(b\).

In Go:

```go
func F(a A) B
```

### Partial/effectful computation

\[
f:A\rightsquigarrow B
\]

Informally:

> give me an \(A\), and executing something may eventually yield a \(B\), perhaps with effects or failure.

For instance:

```go
func F(ctx context.Context, a A) (B, error)
```

The squiggle is only suggestive here.

### Markov kernel

The precise probabilistic interpretation is:

\[
K:A\rightsquigarrow B
\]

with

\[
K:A\to\mathcal D(B).
\]

So instead of:

\[
a \mapsto b
\]

you have:

\[
a \mapsto P(B\mid a).
\]

For a finite example:

```go
type Weighted[B any] struct {
	Value B
	Prob  float64
}

type Distribution[B any] []Weighted[B]

type Kernel[A, B any] interface {
	Apply(A) Distribution[B]
}
```

Example:

```go
type CoinKernel struct{}

func (CoinKernel) Apply(x string) Distribution[string] {
	return Distribution[string]{
		{Value: x + "-success", Prob: 0.8},
		{Value: x + "-failure", Prob: 0.2},
	}
}
```

Mathematically:

\[
K(x)
=
0.8\,\delta_{\text{success}}
+
0.2\,\delta_{\text{failure}}.
\]

---

# 9. Composition of probabilistic squiggly arrows

Suppose:

\[
K:A\rightsquigarrow B
\]

and

\[
L:B\rightsquigarrow C.
\]

Their composite is:

\[
L\circ K:A\rightsquigarrow C
\]

defined by

\[
(L\circ K)(c\mid a)
=
\sum_b
L(c\mid b)K(b\mid a)
\]

in the finite case.

In Go:

```go
func ComposeKernel[A comparable, B comparable, C comparable](
	k Kernel[A, B],
	l Kernel[B, C],
) Kernel[A, C] {
	return KernelFunc[A, C](
		func(a A) Distribution[C] {
			acc := map[C]float64{}

			for _, wb := range k.Apply(a) {
				for _, wc := range l.Apply(wb.Value) {
					acc[wc.Value] += wb.Prob * wc.Prob
				}
			}

			out := make(Distribution[C], 0, len(acc))
			for c, p := range acc {
				out = append(out, Weighted[C]{
					Value: c,
					Prob:  p,
				})
			}

			return out
		},
	)
}

type KernelFunc[A, B any] func(A) Distribution[B]

func (f KernelFunc[A, B]) Apply(a A) Distribution[B] {
	return f(a)
}
```

That is one of the reasons Markov categories are attractive for optimization: **stochastic computations still compose categorically**.

---

# 10. A RAG trial as a kernel

Suppose the input is:

```go
type RAGTrial struct {
	ReleaseID string
	Query     string
	Seed      uint64
}
```

And the observable result is:

```go
type RAGObservation struct {
	Recall     float64
	Grounded   bool
	LatencyMS  float64
	Tokens     int
	AnswerHash string
}
```

Conceptually:

\[
K :
\mathsf{RAGTrial}
\rightsquigarrow
\mathsf{RAGObservation}.
\]

Why not simply:

\[
\mathsf{RAGTrial}
\to
\mathsf{RAGObservation}?
\]

Because even with the same release and query:

- the generator may sample differently;
- a remote reranker may vary;
- latency varies;
- retry/fallback paths vary;
- connected data may change;
- failures are stochastic.

In actual Go, we'd sample one realization:

```go
type RAGTrialRunner interface {
	Run(
		ctx context.Context,
		req RAGTrial,
	) (RAGObservation, error)
}
```

The mathematical kernel describes the distribution that repeated executions are sampling from.

---

# 11. A paired-trial port is actually even more interesting

For optimization, I don't ideally want:

```go
Run(baseline)
Run(candidate)
```

independently.

I want a **coupling port**.

```go
type PairRequest struct {
	Baseline  Candidate
	Candidate Candidate
	Case      Case
	Repeat    int
	PairSeed  uint64
}

type PairResult struct {
	Baseline  TrialResult
	Candidate TrialResult
}

type PairRunner interface {
	RunPair(
		context.Context,
		PairRequest,
	) PairResult
}
```

Mathematically, instead of merely:

\[
K_b:X\rightsquigarrow O
\]

and

\[
K_c:X\rightsquigarrow O,
\]

we introduce

\[
\Gamma_x:
X\rightsquigarrow O_b\times O_c
\]

such that its marginals are \(K_b\) and \(K_c\).

That lets a domain plugin say:

> I know how to couple these trials better than simply running them independently.

For an LLM evaluation it might reuse:

- the same case;
- same random seed;
- same source snapshot;
- same captured remote response where appropriate;
- same time bucket;
- same production request.

That generally reduces comparison variance.

---

# 12. Code for such a coupled port

```go
type PairRunner interface {
	RunPair(
		ctx context.Context,
		req PairRequest,
	) PairResult
}
```

A simple common-random-number implementation:

```go
type CommonSeedPairRunner struct {
	Runner Runner
}

func (p CommonSeedPairRunner) RunPair(
	ctx context.Context,
	req PairRequest,
) PairResult {
	baseReq := TrialRequest{
		CandidateID: req.Baseline.ID,
		CaseID:      req.Case.ID,
		Repeat:      req.Repeat,
		Seed:        req.PairSeed,
	}

	candReq := TrialRequest{
		CandidateID: req.Candidate.ID,
		CaseID:      req.Case.ID,
		Repeat:      req.Repeat,
		Seed:        req.PairSeed,
	}

	return PairResult{
		Baseline:  p.Runner.Run(ctx, baseReq),
		Candidate: p.Runner.Run(ctx, candReq),
	}
}
```

A more sophisticated provider-replay plugin might implement the same port differently.

The campaign doesn't care.

---

# 13. An example of the campaign machine with all its ports

You might end up with:

```go
type Ports struct {
	Proposer Proposer
	Workload Workload
	Runner   PairRunner
	Policy   Policy
	Store    EventStore
	Artifact ArtifactStore
}

type Machine struct {
	ports Ports
	state State
}
```

Then the machine itself owns the protocol:

```go
func (m *Machine) Step(ctx context.Context) error {
	switch m.state.Phase {

	case PhaseNeedCandidates:
		return m.propose(ctx)

	case PhaseNeedTrials:
		return m.runNextPair(ctx)

	case PhaseNeedDecision:
		return m.decide(ctx)

	case PhaseComplete:
		return nil

	default:
		return ErrInvalidPhase
	}
}
```

The plugin is invoked *only when the internal machine reaches a state at which that port is legal*.

That's an important part of “port.”

For example:

```go
func (m *Machine) runNextPair(ctx context.Context) error {
	cell, ok := m.state.NextMissingPair()
	if !ok {
		return m.append(EventEvaluationComplete{})
	}

	req := PairRequest{
		Baseline:  m.state.Baseline,
		Candidate: cell.Candidate,
		Case:      cell.Case,
		Repeat:    cell.Repeat,
		PairSeed:  cell.Seed,
	}

	result := m.ports.Runner.RunPair(ctx, req)

	return m.append(EventPairCompleted{
		Coordinate: cell.Coordinate,
		Result:     result,
	})
}
```

Notice what isn't given to the runner:

```go
*m.state
*m
event store internals
winner selection
promotion status
```

That is deliberate.

---

# 14. “Open port” is really a controlled hole

A fairly intuitive mental model is:

```text
             INTERNAL SEMANTICS
        ┌─────────────────────────┐
        │                         │
        │   campaign reducer      │
        │   pairing laws          │
        │   event custody         │
        │   terminality           │
        │                         │
        │         ○ runner port ────── external runner
        │                         │
        │         ○ policy port ────── domain policy
        │                         │
        │         ○ store port  ────── SQLite/S3/etc.
        │                         │
        └─────────────────────────┘
```

The circle is a **controlled hole in an otherwise closed machine**.

What can pass through the hole is specified.

The external component cannot reach through the hole and rearrange the machine.

That is the sense in which I was using **open port**.

