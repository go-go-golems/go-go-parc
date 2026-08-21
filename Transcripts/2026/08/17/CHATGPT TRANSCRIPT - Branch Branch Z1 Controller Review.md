# Branch · Branch · Z1 Controller Review

- URL: https://chatgpt.com/c/6a81f401-c93c-83ea-bb27-8ac7afb0c3aa
- Created: 2026-08-16T17:31:46.432Z

---

> Review this implementation of the Z1 controller. There are multiple axes to revie:
>
>
>
> - the machine control design
> - the algorithms and path design
> - the JS API + language design for the CAM design language
>
>
>
> Study it all, clone whatever git repos you need, be diligent.
>
>
>
> Write a markdown + pdf report.

```unknown
bash -lc cat /home/oai/skills/pdfs/SKILL.md && printf '\n---ZIP CONTENTS---\n' && unzip -l /mnt/data/dropcut-studio.zip | sed -n '1,220p'
```

I’ll map the project architecture, run available builds/tests, trace controller and CAM execution paths, and inspect linked upstream repositories. Then I’ll deliver a cited Markdown review and rendered PDF.

<details><summary>💭 Thinking</summary>

**Reviewing the repository**

I’m assessing the Z1 controller implementation across the CLI and studio components, starting with structure, tests, and module metadata. I’ll compare available upstream code where possible, then verify findings through focused checks.

**Reviewed the repository**

</details>

```unknown
bash -lc cd /mnt/data/dropcut-review/dropcut-studio && printf '%s\n' '--- README ---' && sed -n '1,260p' README.md && printf '%s\n' '--- JS API handbook ---' && sed -n '1,320p' docs/javascript-api-handbook.md && printf '%s\n' '--- Go CLI README ---' && sed -n '1,280p' makera-z1-cli/README.md && printf '%s\n' '--- Go module ---' && cat makera-z1-cli/go.mod
```

<details><summary>💭 Thinking</summary>

**Auditing the codebase**

I’m mapping the repository, measuring its scope, and checking available runtimes before running tests. I’ll inspect dependencies, the Go module relationship, and the frontend build so I can separate confirmed failures from design concerns.

**Audited the codebase**

**Inspected ZIP/PDF requirements, repository configuration, origins, and controller APIs**

</details>

```json
{"search_query":[{"q":"site:github.com/go-go-golems makera-z1-cli"},{"q":"site:github.com \"dropcut-studio\" CAM"},{"q":"site:github.com/MakeraInc CarveraController"},{"q":"Makera Z1 developer protocol native network"}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Searched 5 websites**

</details>

```unknown
bash -lc set -euo pipefail
cd /mnt/data/dropcut-review
for spec in \
  'https://github.com/go-go-golems/makera-z1-cli.git upstream-makera-z1-cli' \
  'https://github.com/go-go-golems/glazed.git glazed' \
  'https://github.com/MakeraInc/CarveraFirmware.git upstream-CarveraFirmware' \
  'https://github.com/MakeraInc/CarveraProfiles.git upstream-CarveraProfiles' \
  'https://github.com/MakeraInc/CarveraController.git upstream-CarveraController'; do
  url=${spec% *}; dir=${spec##* }
  if [ ! -d "$dir/.git" ]; then
    echo "CLONING $url -> $dir"
    git clone --depth=1 "$url" "$dir" || echo "FAILED $url"
  fi
done
printf '\n--- cloned commits ---\n'
for d in upstream-makera-z1-cli glazed upstream-CarveraFirmware upstream-CarveraProfiles upstream-CarveraController; do
  if [ -d "$d/.git" ]; then
    printf '%-32s ' "$d"
    git -C "$d" rev-parse HEAD
    git -C "$d" log -1 --format='%cI %s'
  fi
done
```

<details><summary>💭 Thinking</summary>

**Cloned CLI and reference repositories**

**Retrieved repository metadata and fetched the latest archive**

</details>

```unknown
bash -lc go version || true; node --version || true; pnpm --version || true; npm --version || true; printf '\nGOMODCACHE=%s\n' "$(go env GOMODCACHE 2>/dev/null || true)"; find "$(go env GOMODCACHE 2>/dev/null || echo /nonexistent)" -maxdepth 4 -type d -path '*go-go-golems*glazed*' 2>/dev/null | head -20; printf '\nPNPM STORE\n'; pnpm store path 2>/dev/null || true; find /root/.local/share/pnpm/store -maxdepth 2 -type d 2>/dev/null | head -20
```

<details><summary>💭 Thinking</summary>

**Inspecting implementation details**

I’m narrowing the review to controller behavior, safety handling, command coverage, and documentation accuracy. I’ll trace key packages and line-level evidence, then run focused tests and static checks to distinguish real defects from stale notes.

**Inspected implementation details**

</details>

The archive couples a TypeScript CAM/compiler workspace with a Go Z1 control CLI. I’m reviewing transport/safety, planning, postprocessing, scripting, and their integration as one safety boundary.

```unknown
bash -lc cd /mnt/data/dropcut-review/dropcut-studio && printf '%s\n' '--- TypeScript source inventory ---' && find packages apps -path '*/src/*' -type f \( -name '*.ts' -o -name '*.tsx' \) -printf '%p\n' | sort && printf '\n--- Go source inventory ---\n' && find makera-z1-cli -type f \( -name '*.go' -o -name '*.md' \) -printf '%p\n' | sort && printf '\n--- Go package tree ---\n' && find makera-z1-cli/pkg -maxdepth 3 -type f -name '*.go' -printf '%h\n' | sort -u
```

<details><summary>💭 Thinking</summary>

**Inspected Go and TypeScript projects, dependencies, tooling, and compiler errors**

**Planned machine analysis and inspected Carvera firmware repositories and commits**

</details>

```unknown
bash -lc cd /mnt/data/dropcut-review/dropcut-studio && sha256sum /mnt/data/dropcut-studio.zip > /mnt/data/dropcut-review/archive.sha256 && find packages apps makera-z1-cli -type f \( -name '*.ts' -o -name '*.tsx' -o -name '*.go' \) -print0 | sort -z | xargs -0 sha256sum > /mnt/data/dropcut-review/source-files.sha256 && python - <<'PY'
from pathlib import Path
from collections import defaultdict
root=Path('/mnt/data/dropcut-review/dropcut-studio')
groups=defaultdict(lambda:[0,0])
for p in root.rglob('*'):
    if p.suffix not in {'.ts','.tsx','.go','.md'} or not p.is_file(): continue
    rel=p.relative_to(root)
    top='/'.join(rel.parts[:2]) if rel.parts[0] in {'packages','apps'} else rel.parts[0]
    lines=p.read_text(errors='replace').splitlines()
    code=sum(1 for l in lines if l.strip() and not l.lstrip().startswith('//'))
    groups[top][0]+=len(lines); groups[top][1]+=code
for k in sorted(groups): print(f'{k:32s} total={groups[k][0]:6d} nonblank_non//={groups[k][1]:6d}')
PY
```

<details><summary>💭 Thinking</summary>

**Evaluating geometry validation**

I’m checking whether path construction actually guarantees continuity and valid arcs. Early concerns include weak frame checks, unvalidated radii and axes, and polyline sampling that may permit unintended jumps despite the continuity claim.

</details>

```unknown
bash -lc cd /mnt/data/dropcut-review/dropcut-studio && nl -ba packages/compiler/src/lower.ts | sed -n '1,420p' && printf '\n--- recertify ---\n' && nl -ba packages/compiler/src/recertify.ts | sed -n '1,360p' && printf '\n--- compiler index ---\n' && nl -ba packages/compiler/src/index.ts
```

<details><summary>💭 Thinking</summary>

**Assessing geometry validation**

I’m verifying whether path construction truly guarantees continuity and valid arcs. Current concerns include weak frame checks, unvalidated radii and axes, and polyline sampling that may allow unintended jumps despite continuity claims.

**Testing safety boundaries**

I’m examining command completion, decoder concurrency, simulation fidelity, and certificate construction. I’m also checking whether machine profiles and tool geometry reject invalid inputs or merely clamp them, since that can hide unsafe assumptions.

**Assessed geometry validation**

</details>

```unknown
bash -lc ls -la /mnt/data/dropcut-review && find /mnt/data/dropcut-review/dropcut-studio -maxdepth 3 -type f | sed 's#^#/##' | head -200
```

<details><summary>💭 Thinking</summary>

**Inspected codebase, validation, safety, motion, and control-flow implementations**

</details>

```unknown
bash -lc cd /mnt/data/dropcut-review/dropcut-studio/makera-z1-cli && nl -ba pkg/makera/report.go | sed -n '1,560p' && nl -ba pkg/makera/parse.go | sed -n '1,520p'
```

I’ve reproduced four stop-ship issues: unknown commands treated read-only, motion continuing after refusal, gouge certification without target checking, and exact-travel claims without resolving work-to-machine coordinates.

<details><summary>💭 Thinking</summary>

**Finalizing the review**

I’m consolidating the verified findings into a structured report, separating release-blocking safety issues from architectural and API concerns. I’ll include reproducible evidence, recommended fixes, test limitations, and clearly documented provenance.

</details>

```unknown
bash -lc find /mnt/data/dropcut-review/dropcut-studio/packages -maxdepth 3 -type f | sort | sed -n '1,240p'
```

<details><summary>💭 Thinking</summary>

**Inspected compiler, geometry, transport, documentation, and dependency code thoroughly**

</details>

```unknown
bash -lc cd /mnt/data/dropcut-review/dropcut-studio && printf '===== CL FIELD =====\n'; nl -ba packages/geometry/src/cl-field.ts; printf '\n===== CONTOURS 1-340 =====\n'; nl -ba packages/geometry/src/contours.ts
```

The HTTP layer is comparatively disciplined. Geometry is stronger for ball/flat cutters, but V-bit handling is non-conservative and bull-nose behavior falls short of its documented toroidal method.

```json
{"paths":["GitHub"],"query":"repository"}
```


---

> hello what's up?

<details><summary>💭 Thinking</summary>

**Checking in briefly**

Hello! I’m here and ready to help. I’m still organizing the repository review and identifying the relevant firmware pieces, but I haven’t completed the full analysis yet.

**Checked in briefly**

</details>

Hello. I’m here and continuing the Z1 review: tracing the controller and CAM layers, then producing the Markdown and PDF report.

The snapshot lacks usable Git history, and the Go CLI is not independently buildable as-is due to its Go 1.26.1 requirement and local `glazed` replacement.

I’ve confirmed critical controller flaws: command-gate bypasses and timeout sentinel reuse, plus canceled jogs sustaining motion. Separately, the JS “sandbox” uses same-realm evaluation without enforced timeouts.

Hello. I’m here. I had only begun the Z1 controller review; the code analysis and markdown/PDF report are not complete yet.

The CAM “verification” is also overstated: travel checks are sampled and simulation never compares cuts to the target surface. Emergency actions can block behind motion, while malformed status may appear safe.


---

> finish it.

I’ll inventory the source, trace control and toolpath pipelines end-to-end, inspect linked dependencies, validate findings against relevant references, then deliver prioritized Markdown and PDF reports.

```unknown
bash -lc cat /home/oai/skills/pdfs/SKILL.md && printf '\n---ZIP---\n' && unzip -l /mnt/data/dropcut-studio.zip | sed -n '1,220p'
```

<details><summary>💭 Thinking</summary>

**Inspecting repositories, documentation, and architecture**

</details>

```json
{"search_query":[{"q":"GitHub \"dropcut-studio\" CAM Z1"},{"q":"GitHub \"makera-z1-cli\""},{"q":"GitHub Makera Z1 firmware protocol"},{"q":"site:github.com Makera Z1 controller firmware"}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Searched 7 websites**

</details>

```unknown
bash -lc set -u
mkdir -p /mnt/data/z1-review-work/upstreams
for url in \
  https://github.com/go-go-golems/makera-z1-cli.git \
  https://github.com/wesen/dropcut-studio.git \
  https://github.com/go-go-golems/dropcut-studio.git \
  https://github.com/MakeraInc/CarveraFirmware.git \
  https://github.com/Carvera-Community/Carvera_Community_Firmware.git \
  https://github.com/Carvera-Community/Carvera_Controller.git
 do
  echo "=== $url ==="
  git ls-remote --symref "$url" HEAD 2>&1 | sed -n '1,3p' || true
 done
```

<details><summary>💭 Thinking</summary>

**Checked candidate repository URLs**

</details>

```json
{"open":[{"ref_id":"https://github.com/go-go-golems/makera-z1-cli"},{"ref_id":"https://github.com/wesen/dropcut-studio"},{"ref_id":"https://github.com/go-go-golems/dropcut-studio"}],"response_length":"medium"}
```

<details><summary>💭 Thinking</summary>

**Searched 1 website**

</details>

```unknown
bash -lc cd /mnt/data/z1-review-work/dropcut-studio
printf '%s\n' 'TypeScript files:' $(find packages apps -type f \( -name '*.ts' -o -name '*.tsx' \) | wc -l)
printf '%s\n' 'Go files:' $(find makera-z1-cli -type f -name '*.go' | wc -l)
printf '%s\n' 'TypeScript LOC:' $(find packages apps -type f \( -name '*.ts' -o -name '*.tsx' \) -print0 | xargs -0 cat | wc -l)
printf '%s\n' 'Go LOC:' $(find makera-z1-cli -type f -name '*.go' -print0 | xargs -0 cat | wc -l)
printf '%s\n' 'Tests:' $(find packages apps makera-z1-cli -type f \( -name '*.test.ts' -o -name '*_test.go' \) | wc -l)
printf '%s\n' 'TODO/FIXME markers:'
rg -n '(TODO|FIXME|HACK|XXX|not implemented|unsupported|panic\()' packages apps makera-z1-cli --glob '*.{ts,tsx,go}' | sed -n '1,260p'
```

<details><summary>💭 Thinking</summary>

**Preparing repository review**

I’m assessing whether the project can be inspected directly, compared with its public upstream state, and tested locally. I’ll first verify the available files and environment before deciding what checks are practical.

**Prepared repository review**

</details>

```unknown
bash -lc cat /home/oai/skills/pdfs/tasks/create.md; printf '\n---CONVERT---\n'; cat /home/oai/skills/pdfs/tasks/convert.md
```

<details><summary>💭 Thinking</summary>

**Inspected repository code, dependencies, tests, tooling, configurations, and source files**

</details>

```unknown
bash -lc cd /mnt/data/z1-review-work/dropcut-studio
for f in \
 ttmp/2026/08/11/MZ1-003--motion-and-job-control-with-a-manual-control-ui/analysis/01-implementation-review-the-client-the-cli-and-the-mz1-003-design.md \
 ttmp/2026/08/11/MZ1-003--motion-and-job-control-with-a-manual-control-ui/changelog.md \
 ttmp/2026/08/11/CAM-002--stock-aware-pocket-linking-and-consistent-cam-planning-architecture/design-doc/01-stock-aware-pocket-linking-architecture-and-implementation-guide.md \
 ttmp/2026/08/09/CAM-001--vite-react-redux-cam-application-with-embedded-js-scripting-ide/design-doc/01-dropcut-studio-architecture-analysis-and-implementation-guide.md; do
 echo "### $f"; rg -n '^#{1,4} ' "$f" | sed -n '1,260p'; echo; done
```

<details><summary>💭 Thinking</summary>

**Reviewing safety behavior**

I’m examining command classification, preflight enforcement, and reproducibility risks. A key concern is that direct cycle-start requests may resume motion without the same preflight checks enforced elsewhere, so I’m tracing those paths carefully.

**Reviewed safety behavior**

</details>

```unknown
bash -lc cd /mnt/data/z1-review-work/dropcut-studio/makera-z1-cli
printf '%s\n' '--- protocol encode ---'
nl -ba pkg/makera/protocol.go | sed -n '1,260p'
printf '%s\n' '--- exec CLI ---'
nl -ba cmd/z1ctl/cmds/exec.go | sed -n '1,260p'
printf '%s\n' '--- cycle-start references ---'
rg -n 'CycleStart|cycle-start|RealtimeResume' .
```

<details><summary>💭 Thinking</summary>

**Tracing command hazards**

I’m identifying two concrete risks: embedded newlines may allow multiple commands in one payload, and cycle-start appears to bypass preflight checks. I’m also separating API semantics, dry-run limitations, composite-motion behavior, and incomplete firmware-error handling.

**Traced command hazards**

</details>

The TypeScript core passes strict type-checking, but the Go side is not reproducibly buildable. I also confirmed two framing defects that can stall decoding or corrupt controller state.

```unknown
bash -lc cd /mnt/data/z1-review-work/dropcut-studio/makera-z1-cli
nl -ba pkg/makera/escape.go | sed -n '1,260p'
printf '\n--- motion CLI run ---\n'
nl -ba cmd/z1ctl/cmds/motionrun.go | sed -n '1,260p'
printf '\n--- positioning ---\n'
nl -ba cmd/z1ctl/cmds/positioning.go | sed -n '1,420p'
printf '\n--- outputs cycle start excerpt ---\n'
nl -ba cmd/z1ctl/cmds/outputs.go | sed -n '220,310p'
```

<details><summary>💭 Thinking</summary>

**Assessing remote security**

I’m checking token exposure, plaintext transport, unauthenticated telemetry, origin validation, and browser protections. The main concerns are replayable URL credentials, remote traffic without encryption, and publicly reachable status or camera endpoints.

**Assessed remote security**

</details>

```unknown
bash -lc cd /mnt/data/z1-review-work/dropcut-studio/makera-z1-cli
nl -ba pkg/makera/filexfer.go | sed -n '1,560p'
printf '\n--- filesystem ---\n'
nl -ba pkg/makera/filesystem.go | sed -n '1,320p'
```

<details><summary>💭 Thinking</summary>

**Prioritizing report findings**

I’m consolidating the implementation review into a Markdown report and PDF, emphasizing the confirmed command-injection risk, missing preflight on cycle start, testing limits, and the broader CAM architecture.

</details>

The safety boundary is bypassable and multi-step motions can interleave across callers. Separately, certification can label a program “verified” despite sampled crash errors because certificates lack failure state.

The report is complete with acceptance criteria for release blockers, including false gouge verification, same-realm script escape, and contour-chaining collisions. The 42-page PDF passed visual inspection; final integrity checks remain.

```unknown
bash -lc sed -n '1,240p' /home/oai/skills/pdfs/SKILL.md && printf '\n---FILES---\n' && find /mnt/data/z1-review-work/dropcut-studio/packages/script-host/src -maxdepth 2 -type f -print && printf '\n---STRATEGIES---\n' && find /mnt/data/z1-review-work/dropcut-studio/packages/strategies/src -maxdepth 2 -type f -print && printf '\n---PLANNER---\n' && find /mnt/data/z1-review-work/dropcut-studio/packages/planner/src -maxdepth 2 -type f -print
```

```json
{"paths":["GitHub"],"query":"contents"}
```

```json
{"paths":["GitHub"],"query":"tree"}
```

# Z1 Controller Review

Completed. The report covers the machine-control layer, CAM algorithms and path generation, JavaScript API/language semantics, postprocessing, certificate design, controller-to-CAM trust boundaries, build reproducibility, and a staged remediation plan.

**Disposition: NO-GO for production cutting, unattended jobs, or operation over an untrusted network.** The implementation remains suitable for development, simulation, controlled dry runs, and physically attended air-cut testing.

Four independently confirmed release blockers are:

1. **False gouge certification:** sampled stock-removal evidence is promoted into a gouge-verification result without comparing the cut against a target surface.
2. **Ineffective JavaScript isolation:** same-realm `new Function` execution can reach host globals, and the configured timeout is not enforced.
3. **Fail-open controller authorization:** the generic command classifier examines only the first token and treats unknown commands as read-only.
4. **Contour topology corruption:** endpoint keys repeat every **67.108864 mm**, allowing unrelated paths to merge within the Z1 work envelope.

The report contains 46 numbered findings, executable counterexamples, source-level evidence, prioritized P0/P1/P2 remediation, acceptance gates, and a minimum release checklist. Limitations such as the unavailable physical machine and blocked clean-room test-suite execution are documented explicitly.

- [Download the Markdown report](sandbox:/mnt/data/z1_review_deliverables/Z1_Controller_Implementation_Review.md)
- [Download the 42-page PDF report](sandbox:/mnt/data/z1_review_deliverables/Z1_Controller_Implementation_Review.pdf)


---

> research the theory behind building this kind of compiler and IR / compiler passes / semantics / operational research  and the creation of certificates and assertions and invariants and such.

<details><summary>💭 Thinking</summary>

**Researching compiler theory**

I’m identifying the project’s needs: intermediate representations, semantics, transformation passes, operational-research connections, and machine-checkable certificates. I’ll ground the explanation in established theory and tailor it to this compiler architecture.

**Researched compiler theory**

</details>

I’ll ground the theory in the reviewed Dropcut/Z1 architecture, mapping compiler stages to formal semantics, optimization theory, proof obligations, and certificate design.

```unknown
bash -lc ls -lah /mnt/data && find /mnt/data -maxdepth 3 -type f | sed -n '1,120p'
```

<details><summary>💭 Thinking</summary>

**Structuring the theory**

I’m connecting compiler pipelines, formal semantics, geometric reasoning, numerical guarantees, and certificate design. I’ll frame each pass as a contract-preserving refinement, with explicit invariants and checkable evidence.

**Structured the theory**

**Formalizing the compiler**

I’m modeling the pipeline with typed, state-aware intermediate representations, explicit units and frames, and semantics for motion, stock, tooling, and safety. I’m also defining conservative geometric certificates with numerical error bounds.

**Formalized the compiler**

**Gathering foundational sources**

I’m selecting primary references on semantics, verification, abstract interpretation, certified compilation, IR design, and planning. I’ll connect these foundations to CAM-specific scheduling, path linking, machine states, and evidence-producing transformations.

**Gathered foundational sources**

**Inspected project files, documentation, and compiler analysis sources**

</details>

```unknown
bash -lc cd /mnt/data/dropcut-studio-src/dropcut-studio && for f in packages/ir/src/path.ts packages/ir/src/provenance.ts packages/compiler/src/validate.ts packages/compiler/src/lower.ts packages/compiler/src/recertify.ts packages/analysis/src/pipeline-certificate.test.ts packages/planner/src/types.ts packages/planner/src/run.ts packages/planner/src/linker.ts packages/planner/src/refine.ts packages/script-host/src/api.ts packages/script-host/src/sandbox.ts packages/math/src/frames.ts packages/geometry/src/cl-field.ts packages/geometry/src/eikonal.ts packages/geometry/src/contours.ts packages/strategies/src/pocket.ts packages/strategies/src/constant-scallop.ts packages/post-makera/src/index.ts; do echo "===== $f ====="; nl -ba "$f" | sed -n '1,420p'; done
```

<details><summary>💭 Thinking</summary>

**Inspected source files with line numbers**

</details>

```json
{"search_query":[{"q":"site:nist.gov RS274 NGC interpreter canonical machining functions PDF Kramer Proctor Messina"},{"q":"CompCert verified compiler semantic preservation official paper PDF Leroy"},{"q":"translation validation Pnueli Siegel Singerman validating optimizing compiler PDF"},{"q":"proof-carrying code Necula 1997 PDF"}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Searched 12 websites**

</details>

```unknown
bash -lc cd /mnt/data/dropcut-studio-src/dropcut-studio && sed -n '1,340p' packages/compiler/src/validate.ts && echo '--- LOWER ---' && sed -n '1,300p' packages/compiler/src/lower.ts && echo '--- RECERTIFY ---' && sed -n '1,340p' packages/compiler/src/recertify.ts && echo '--- PROVENANCE ---' && sed -n '1,320p' packages/ir/src/provenance.ts && echo '--- PLANNER TYPES ---' && sed -n '1,360p' packages/planner/src/types.ts && echo '--- PLANNER RUN ---' && sed -n '1,420p' packages/planner/src/run.ts
```

I’ll distinguish operational semantics from operations research, and separate type/API-level evidence from genuine semantic proof, noting where current validation, provenance, and error-budget mechanisms remain nominal.

<details><summary>💭 Thinking</summary>

**Inspected compiler architecture, passes, planner, documentation, and APIs**

</details>

```json
{"search_query":[{"q":"site:arxiv.org \"MLIR: Scaling Compiler Infrastructure for Domain Specific Computation\""},{"q":"site:dl.acm.org MLIR scaling compiler infrastructure domain specific computation"},{"q":"site:llvm.org MLIR language reference dialect conversion official"},{"q":"site:mlir.llvm.org/docs DialectConversion official"}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Defining verified compilation**

I’m treating the system as a refinement pipeline, not merely a source-to-text compiler. I’m separating logical machine semantics, physical assumptions, numerical approximation, and certificates that preserve safety properties across passes.

**Defined verified compilation**

**Searched 1 website**

</details>

```json
{"search_query":[{"q":"site:nist.gov RS274NGC canonical machining functions interpreter PDF"},{"q":"site:compcert.org verified compiler semantic preservation translation validation"},{"q":"site:mlir.llvm.org rationale progressive lowering dialect conversion legality"},{"q":"proof carrying code Necula PDF Carnegie Mellon primary source"}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Searched 8 websites**

</details>

```unknown
bash -lc set -e
cd /mnt/data/dropcut-studio-src/dropcut-studio
printf '%s\n' '--- README pipeline ---'
grep -n -A14 -B3 'ManufacturingPlan' README.md | head -80 || true
printf '%s\n' '--- IR program types ---'
sed -n '1,260p' packages/ir/src/program.ts
printf '%s\n' '--- canonical commands ---'
sed -n '1,280p' packages/ir/src/commands.ts
printf '%s\n' '--- path ---'
sed -n '1,280p' packages/ir/src/path.ts
```

<details><summary>💭 Thinking</summary>

**Inspected IR pipeline paths, validation, certificates, sandbox, and analysis checks**

</details>

The emerging architecture is a certificate-carrying refinement pipeline: per-pass validation, conservative approximation bounds, separate feasibility and optimization, and runtime admission tied to the exact hashed job.

# Theory for a Certificate-Carrying CAM Compiler

I interpret “operational research” in both relevant senses:

1. **Operational semantics**: a mathematical account of how programs change machine, controller, geometry, and stock state.
2. **Operations research**: optimization of sequencing, linking, feeds, tool changes, and machining time under hard constraints.

The central conclusion is:

> Dropcut should be treated as a **certificate-carrying refinement compiler for a cyber-physical system**, not as a JavaScript-to-G-code translator.

Its target is not text. Its target is a set of possible physical executions of a particular machine, controller, tool, setup, and workpiece. The compiler is correct when every possible target execution refines the source manufacturing intent within declared error bounds and assumptions.

NIST’s canonical machining commands provide an established precedent for separating controller syntax from machining meaning: the NIST RS274 interpreter maps modal G-code into canonical machining operations. Dropcut is largely traversing the opposite direction—from manufacturing intent through canonical operations into a controller dialect—but the same “canonical semantic waist” is useful. citeturn662326search0turn662326search1

---

## 1. What kind of compiler is this?

A conventional compiler approximately has:

$$
\text{source program}
\longrightarrow
\text{machine program}
$$

and a semantic preservation theorem of the form:

$$
\operatorname{compile}(S)=T
\quad\Longrightarrow\quad
\operatorname{Beh}(T)\preceq\operatorname{Beh}(S)
$$

where $\operatorname{Beh}$ means observable behavior. CompCert proves such preservation by composing proofs for individual compiler passes. Importantly, a compiler is allowed to reject a source program rather than emit code it cannot compile correctly. citeturn662326search8turn662326search9turn662326search10

For CAM, the source and target semantics are richer:

$$
\text{manufacturing intent}
\rightarrow
\text{geometric construction}
\rightarrow
\text{toolpath}
\rightarrow
\text{machine trajectory}
\rightarrow
\text{controller commands}
\rightarrow
\text{physical material removal}
$$

The source often does not specify a unique execution. A pocket operation, for example, specifies an acceptable **result**, not one particular zigzag path. Therefore, the source meaning is best modeled as a set of permitted executions or outcomes:

$$
\operatorname{Allowed}(I)
=
\{\text{executions that satisfy manufacturing intent } I\}
$$

Compilation selects one implementation from that set:

$$
\operatorname{compile}(I)=P
$$

Correctness then means:

$$
\forall \tau\in\operatorname{Exec}(P,A):
\quad
\alpha(\tau)\in N_\varepsilon(\operatorname{Allowed}(I))
$$

where:

- $A$ is the set of assumptions about the machine and setup;
- $\tau$ is a possible physical execution trace;
- $\alpha$ abstracts a low-level physical trace back to manufacturing observations;
- $N_\varepsilon$ allows declared geometric and numerical error.

This is **refinement under assumptions and bounded approximation**.

The certificate’s ultimate theorem should resemble:

$$
\operatorname{verify}(B)=\text{true}
\land
\operatorname{AssumptionsHold}(A)
\quad\Longrightarrow\quad
\forall\tau\in\operatorname{Execute}(B,A):
\operatorname{Safe}(\tau)
\land
\operatorname{ConformsToIntent}_\varepsilon(\tau)
$$

Here $B$ is the exact deployed bundle, including emitted bytes, profile, tools, setup, configuration, and evidence.

---

## 2. The four semantics you need

No single semantic style is sufficient. This compiler needs at least four complementary views.

| Semantic view | Question answered | CAM application |
|---|---|---|
| Denotational | “What does this program mean?” | Manufacturing intent, path geometry, resulting stock |
| Operational | “How does execution proceed step by step?” | Modal G-code, controller state, probing, pause/resume |
| Axiomatic | “What must be true before and after this operation?” | Interlocks, travel limits, spindle/tool sequencing |
| Trace/temporal | “What is always or eventually true over time?” | Job lifecycle, stop behavior, connection loss, acknowledgements |

Hoare logic introduced reasoning with preconditions and postconditions, while abstract interpretation provides a framework for computing sound approximations of possible program behavior. citeturn409138search0turn409138search1

### 2.1 Denotational semantics

A machine state can be modeled as:

$$
\sigma =
(q,\dot q,F,W,T_{\text{active}},S_{\text{spindle}},
C,S_{\text{stock}},P_{\text{target}},O,M,t)
$$

where:

- $q,\dot q$: axis positions and velocities;
- $F$: frame graph and transforms;
- $W$: active work coordinate system;
- $T_{\text{active}}$: tool and holder;
- $S_{\text{spindle}}$: spindle state;
- $C$: coolant and other process state;
- $S_{\text{stock}}$: current stock solid;
- $P_{\text{target}}$: target part or protected material;
- $O$: fixtures and obstacles;
- $M$: controller mode and modal state;
- $t$: time.

A command should generally denote a relation rather than a deterministic function:

$$
\llbracket c\rrbracket :
\Sigma
\rightarrow
\mathcal P(\Sigma\times\operatorname{Trace}\times\operatorname{Outcome})
$$

The powerset accounts for:

- probe uncertainty;
- controller nondeterminism;
- measurement noise;
- communication failure;
- machine-following error;
- possible fault outcomes.

At higher levels, an operation such as `rectPocket` should not denote one polyline. It should denote a predicate on acceptable residual stock:

$$
\llbracket \operatorname{Pocket}(R,d,\delta)\rrbracket
=
\{S' \mid \operatorname{PocketSpecification}(S',R,d,\delta)\}
$$

A toolpath strategy then produces a **witness** that it believes satisfies this predicate.

That changes the conceptual type of a planner from:

```ts
Intent -> Toolpath
```

to:

```ts
Intent -> Result<{
  toolpath: Toolpath;
  witness: PlanningWitness;
}>
```

with an independent checker:

```ts
checkPlanningWitness(intent, toolpath, witness): CheckResult
```

### 2.2 Operational semantics

Operational semantics describes transitions:

$$
\langle c,\sigma\rangle
\rightarrow
\langle c',\sigma'\rangle
$$

or, for atomic canonical commands:

$$
\langle c,\sigma\rangle
\Downarrow
(\sigma',e)
$$

where $e$ is the emitted event or trace fragment.

A simplified cutting rule might be:

$$
\frac{
  \operatorname{Homed}(\sigma)
  \quad
  \operatorname{WCSKnown}(\sigma)
  \quad
  \operatorname{ToolLoaded}(\sigma,T)
  \quad
  \operatorname{SpindleValid}(\sigma)
  \quad
  f>0
}{
  \langle\operatorname{Cut}(\gamma,T,f),\sigma\rangle
  \Downarrow
  \left(
    \sigma[
      q:=\operatorname{end}(\gamma),
      S_{\text{stock}}:=S_{\text{stock}}\setminus
      \operatorname{Sweep}(T,\gamma)
    ],
    \operatorname{motionTrace}(\gamma,f)
  \right)
}
$$

This semantics belongs in a pure `@cam/semantics` package. It should be usable by:

- the verifier;
- the simulator;
- the time estimator;
- tests;
- the postprocessor validator;
- the controller protocol model.

The UI renderer can remain approximate, but it should not silently become the reference semantics.

### 2.3 Axiomatic semantics and weakest preconditions

For commands, use Hoare triples:

$$
\{P\}\ c\ \{Q\}
$$

For example:

$$
\{
\operatorname{Homed}
\land
\operatorname{WCSKnown}
\land
\operatorname{Tool}=T
\land
\operatorname{SpindleOn}
\land
\operatorname{PathSafe}(\gamma)
\}
$$

$$
\operatorname{cut}(\gamma,T,f)
$$

$$
\{
\operatorname{Pose}=\operatorname{end}(\gamma)
\land
S'=S\setminus\operatorname{Sweep}(T,\gamma)
\}
$$

A weakest-precondition function is especially useful:

$$
wp(c,Q)
$$

It computes the weakest condition required before $c$ so that $Q$ holds afterward. For a sequence:

$$
wp(c_1;c_2,Q)=wp(c_1,wp(c_2,Q))
$$

This gives the compiler a principled way to derive preflight requirements rather than maintaining ad hoc boolean checks.

For instance:

$$
wp(\operatorname{Cut}(\gamma,T,f),Q)
$$

would include:

- homed machine;
- known work transform;
- matching tool;
- valid spindle state;
- positive and supported feed;
- path inside the travel envelope;
- no forbidden swept-volume intersection;
- the postcondition $Q$ evaluated on the updated stock state.

### 2.4 Trace and temporal semantics

The controller is not merely a function from commands to responses. It is a concurrent state machine involving:

- host connection;
- upload;
- machine storage;
- acknowledgement;
- preparation;
- start;
- execution;
- pause;
- resume;
- abort;
- disconnect;
- alarm;
- recovery.

Temporal logic is appropriate here. TLA models systems as state-transition relations and supports reasoning about safety and liveness over traces. citeturn538704search0

Example properties:

$$
\Box(\operatorname{Motion}
\Rightarrow
\operatorname{Homed}\land\operatorname{Authorized})
$$

“Motion always implies that the machine is homed and the operation was authorized.”

$$
\Box(\operatorname{AbortRequested}
\Rightarrow
\Diamond(\operatorname{Stopped}\lor\operatorname{Faulted}))
$$

“An abort request eventually results in an explicit stopped or faulted state.”

$$
\Box(
\operatorname{ExecuteHash}=h
\Rightarrow
\operatorname{StoredHash}=h
)
$$

“The bytes executed are the bytes acknowledged after upload.”

These cannot be established by checking an array of canonical commands. They concern the entire host-controller protocol.

---

## 3. Separate path, trajectory, and process semantics

The current design correctly distinguishes a `Path` from G-code syntax, but a robust model needs three separate objects.

### Geometric path

$$
\gamma:[0,1]\rightarrow SE(3)
$$

For a fixed-orientation three-axis machine, this can be simplified to:

$$
\gamma:[0,1]\rightarrow\mathbb R^3
$$

It says where the tool is, but not when it is there.

### Time parameterization

$$
s:[0,T]\rightarrow[0,1]
$$

with $s$ monotone. The physical trajectory is:

$$
x(t)=\gamma(s(t))
$$

Velocity, acceleration, jerk, servo limitations, and contour-following error belong to $s(t)$ and the machine dynamics—not to the geometric curve alone.

### Process semantics

For a tool solid $B$, the swept volume is:

$$
\operatorname{Sweep}(B,x)
=
\bigcup_{t\in[0,T]}x(t)B
$$

Stock evolves as:

$$
S_{i+1}=S_i\setminus R_i
$$

where $R_i$ is the material provably removed by operation $i$.

Important properties can then be stated precisely.

Travel safety:

$$
\forall t,\quad q(t)\in Q_{\text{admissible}}
$$

Fixture and holder clearance:

$$
\operatorname{Sweep}(B_{\text{tool}}\cup B_{\text{holder}},x)
\cap O
=
\varnothing
$$

Rapid safety against current stock:

$$
\operatorname{Sweep}(B_{\text{tool}}\cup B_{\text{holder}},x_i)
\cap(S_i\cup O)
=
\varnothing
$$

No gouge, with tolerance $\delta$:

$$
\operatorname{Sweep}(B_{\text{tool}},x)
\cap
(P_{\text{target}}\ominus B_\delta)
=
\varnothing
$$

The erosion by $B_\delta$ expresses that penetration into a $\delta$-wide tolerance layer may be allowed, while penetration farther into target material is forbidden.

Required removal is a different property from no gouge. One concerns avoiding excessive removal; the other concerns removing enough material. They require different approximations and should be separate certificate claims.

---

## 4. The correct IR hierarchy

The current pipeline is:

```text
script
→ ManufacturingPlan
→ ToolpathProgram
→ CanonicalProgram
→ MachineProgram
→ ValidatedProgram
→ GCodeBlock[]
→ .nc
```

That direction is sound, but some stages need sharper semantic boundaries. MLIR’s central lesson is that domain-specific compilers benefit from representations at several abstraction levels, with explicit legality rules for each conversion target. citeturn628227search3turn628227search5

I would use these levels.

| IR | Meaning | Excludes |
|---|---|---|
| Authoring AST | User syntax, macros, source locations | Direct machine effects |
| Elaborated Plan IR | Units, frames, tools and references resolved | Unresolved names or implicit units |
| Manufacturing Intent IR | Features, operations, tolerances, precedence | Tool-center trajectories |
| Geometric Toolpath IR | Continuous cut curves and process parameters | Linking and machine-specific behavior |
| Scheduled Program IR | Ordered cuts, entries, retracts and traverses | Controller syntax |
| Machine IR | Machine frames, capabilities, limits and concrete trajectories | Modal G-code state |
| Controller IR | Explicit controller operations and dialect semantics | Text formatting ambiguity |
| Serialized Job Bundle | Exact bytes, metadata and certificate graph | Unbound assumptions |

### Validation is not really an IR level

`ValidatedProgram` is useful as a software engineering gate: it prevents accidental calls to the postprocessor before a validation function has run.

But semantically, “validated” should not be another language. It is evidence about an artifact.

Prefer:

```ts
interface Certified<T> {
  readonly artifact: T;
  readonly artifactHash: Hash;
  readonly claims: readonly Claim[];
  readonly evidence: readonly Evidence[];
}
```

rather than making certification part of the artifact’s structural identity.

This matters because different properties may be certified at different times:

```text
GeometricToolpath
  + path/target evidence

MachineProgram
  + travel/capability evidence

ControllerProgram
  + modal-equivalence evidence

Serialized bytes
  + parse-back and content-binding evidence

Execution setup
  + runtime assumption evidence
```

A single `ValidatedProgram` brand cannot express this proof graph.

---

## 5. Every compiler pass needs a semantic contract

A pass should not merely be:

```ts
I -> O
```

It should conceptually be:

```ts
interface CertifyingPass<I, O, W> {
  readonly id: string;
  readonly version: string;

  transform(
    input: I,
    config: PassConfig
  ): Result<{ output: O; witness: W }, Diagnostic[]>;

  check(
    input: I,
    output: O,
    witness: W,
    config: PassConfig
  ): CheckResult;
}
```

The checker should establish a relation:

$$
R_{I,O}(i,o)
$$

with a theorem:

$$
\operatorname{check}(i,o,w)=\text{true}
\Longrightarrow
R_{I,O}(i,o)
$$

The relation depends on the class of pass.

### Exact semantic preservation

Used for:

- harmless normalization;
- canonicalization;
- modal compression when interpreted semantics are identical;
- syntax serialization and parse-back.

$$
\operatorname{Sem}(o)=\operatorname{Sem}(i)
$$

### Trace refinement

Used when the target resolves choices left open by the source:

$$
\operatorname{Traces}(o)
\subseteq
\operatorname{Traces}(i)
$$

For example, a high-level `Traverse` allows any safe route. Lowering it to retract–XY–descend selects one allowed route.

### Bounded geometric refinement

Used for curve discretization and arc linearization:

$$
d_H(\gamma_i,\gamma_o)\le\varepsilon
$$

where $d_H$ is Hausdorff distance.

For swept-volume safety, centerline Hausdorff distance may be insufficient by itself. The pass must show how path deviation propagates through the tool shape and frame transforms.

### Witness selection

Used for CAM planning:

$$
o\in\llbracket i\rrbracket
$$

A pocket strategy is producing a witness satisfying a manufacturing specification.

### Optimization preservation

Used for path ordering or feed optimization:

$$
\operatorname{Feasible}(o)
\land
\operatorname{Sem}(o)\approx\operatorname{Sem}(i)
\land
J(o)\le J(i)
$$

The safety and semantic constraints are hard. The objective $J$ is secondary.

### Typical pass obligations

| Pass | Required proof or checker |
|---|---|
| Unit/frame elaboration | Dimensions valid; every coordinate has one known frame |
| Feature planning | Output path satisfies feature and allowance specification |
| Surface sampling | Surface approximation enclosed within declared bound |
| Curve refinement | Endpoint preservation and Hausdorff/chord bound |
| Path reordering | Dependency order preserved; process effects remain valid |
| Link generation | Every added move is inside certified free space |
| Machine lowering | Every operation is supported or soundly transformed |
| Feed clamping | Geometry unchanged; process assumptions revalidated |
| Arc lowering | Endpoints, orientation and sweep preserved within bound |
| Modal compression | Modal interpreter produces the same canonical trace |
| Serialization | Reparse yields equivalent controller IR |
| Upload | Stored and executed byte hash matches certified artifact |

This is essentially CompCert’s compositional strategy, but translation validation is probably more practical for this project initially: rather than proving the TypeScript implementation correct for all inputs, independently validate each actual input/output pair produced by a pass. Translation validation was introduced precisely as a way to validate individual compiler runs using a common semantic framework and refinement relation. citeturn840691search2turn840691search3

---

## 6. Paths as a category: useful, but be precise

The existing `Path<F>` design has a strong algebraic intuition:

- objects: poses or points;
- morphisms: paths between them;
- identity: `emptyPath(at)`;
- composition: `concat(a,b)` when `a.end = b.start`.

This is the free-category view of path construction.

There are, however, three qualifications.

### 6.1 Paths are generally equal only up to reparameterization

Two concatenated geometric paths can describe the same image with different parameterizations. Therefore, literal object equality is too strong. The appropriate equivalence is generally equality modulo monotone reparameterization.

### 6.2 Approximate equality is not equality

The current `JOIN_EPS` relation:

$$
d(p,q)<\varepsilon
$$

is not transitive:

$$
d(p,q)<\varepsilon,\quad d(q,r)<\varepsilon
$$

does not imply:

$$
d(p,r)<\varepsilon
$$

Consequently, endpoint matching by tolerance does not create an ordinary category with exact laws. Repeated composition may also accumulate error.

Better choices include:

- canonical snapping to exact point identities;
- symbolic endpoint identifiers;
- explicit join witnesses;
- exact rational or algebraic endpoints where practical;
- paths carrying accumulated endpoint uncertainty;
- a metric-enriched structure where error is part of the composition result.

For example:

```ts
interface JoinedPath<F> {
  readonly path: Path<F>;
  readonly joinErrors: readonly DistanceBound[];
}
```

### 6.3 Construction invariants are not semantic proofs

`PathBuilder` is valuable because it prevents an `end` field from disagreeing with the final segment. That is a **representation invariant**.

It does not establish:

- that an arc really starts at the prior endpoint;
- that arc radius is consistent at both ends;
- that a polysegment begins at the current cursor;
- that a path lies inside travel limits;
- that the path avoids the target and fixtures;
- that numerical evaluation respects its stated tolerance.

Keep the categorical API, but describe it as a compositional construction discipline rather than formal verification.

---

## 7. Commands as effects: monads, Kleisli composition, and typestate

Machine commands are effectful. They can:

- mutate machine state;
- fail;
- produce probe results;
- emit diagnostics;
- consume time;
- alter stock;
- interact with external controller state.

An ordinary state-and-error interpretation has a shape such as:

$$
M(A)=\Sigma\rightarrow\operatorname{Result}(\Sigma\times A,E)
$$

A command is:

$$
A\rightarrow M(B)
$$

and commands compose by Kleisli composition.

For CNC, a plain monad does not capture enough because the type of the machine state changes. A parameterized or indexed monad is a better model:

$$
\operatorname{Cmd}\langle S_{\text{before}},
S_{\text{after}},A\rangle
$$

with composition:

$$
\operatorname{bind}:
\operatorname{Cmd}\langle S_0,S_1,A\rangle
\rightarrow
(A\rightarrow\operatorname{Cmd}\langle S_1,S_2,B\rangle)
\rightarrow
\operatorname{Cmd}\langle S_0,S_2,B\rangle
$$

Parameterized monads were developed specifically to model effects whose pre-state and post-state types differ. Typestate similarly restricts which operations are permitted in a particular state and detects invalid operation sequences. citeturn409138search8turn628227search8

Conceptually:

```ts
type SelectTool<T, S> =
  Cmd<S, S & { tool: T }, void>;

type StartSpindle<R, S extends { tool: Tool }> =
  Cmd<S, S & { spindle: Running<R> }, void>;

type Cut<P, S extends {
  homed: true;
  wcs: KnownWcs;
  tool: Tool;
  spindle: RunningRpm;
}> =
  Cmd<S, S & { pose: EndOf<P> }, void>;
```

TypeScript cannot make the physical machine satisfy these states. It can only constrain program construction. Runtime preflight and controller-state checking remain mandatory.

### A practical SSA-style state token

A simpler IR encoding is:

```text
%s0 = machine.initial

%s1 = machine.require_homed %s0
%s2 = tool.select %s1 @T1
%s3 = spindle.start %s2 12000rpm
%s4 = motion.traverse %s3 to=(10,10,5)
%s5 = motion.cut %s4 path=@p1 feed=400
%s6 = spindle.stop %s5
```

Every state-changing operation consumes one state token and produces another. This:

- makes order explicit;
- prevents accidental reordering;
- supports dataflow analysis;
- gives probe results explicit dependencies;
- resembles the memory-token discipline used in compiler IRs.

It is usually easier to implement and inspect than advanced phantom-state types throughout a TypeScript API.

---

## 8. The JavaScript language should be a macro language over an inert AST

For assurance purposes, user JavaScript should not itself be the CAM semantic model. It should be a meta-language that constructs an immutable domain AST.

The important boundary is:

```text
arbitrary JavaScript computation
            ↓
       inert Plan AST
            ↓
    trusted semantic pipeline
```

After the AST is produced:

- no closures should remain;
- no arbitrary callbacks should be invoked by compiler passes;
- all values should be finite and validated;
- all frames and units should be explicit;
- every operation should have provenance;
- the AST should be serializable and content-addressable.

The current capability API already moves in this direction by allowing scripts to create plans rather than directly emit machine commands. The remaining problem is that `new Function` executes the macro language in the host realm. Isolation is a security requirement, but it is also a semantic requirement: deterministic, reproducible compilation is difficult if a program can read time, randomness, network state, storage, or host globals.

A good compilation record should capture:

```ts
interface ScriptEvaluationRecord {
  sourceHash: Hash;
  languageVersion: string;
  apiVersion: string;
  declaredInputs: readonly ArtifactRef[];
  resultAstHash: Hash;
  diagnostics: readonly Diagnostic[];
}
```

The resulting AST, not the live JavaScript environment, is what subsequent certificates should reference.

---

## 9. Assertions, invariants, assumptions, and proofs are different objects

These terms should not be conflated.

### Assertion

A proposition at a point in the program:

$$
x\in[0,100]
$$

### Precondition/postcondition

A proposition required before or promised after an operation:

$$
\{P\}\ c\ \{Q\}
$$

### Invariant

A property that holds initially and is preserved by every relevant transition:

$$
I(\sigma_0)
$$

$$
I(\sigma)\land\sigma\rightarrow\sigma'
\Longrightarrow I(\sigma')
$$

### Assumption

An external fact the software does not prove:

- tool diameter is 3.175 mm;
- fixture model matches reality;
- WCS was probed correctly;
- firmware implements the documented rapid semantics;
- spindle calibration is within a specified tolerance.

### Evidence

Data supporting a claim:

- interval bounds;
- a proof term;
- abstract states;
- a collision-separation witness;
- a parse-back comparison;
- an exhaustive transition table;
- a solver proof trace.

### Certificate

A machine-checkable package binding:

- one precise proposition;
- one artifact;
- assumptions;
- evidence;
- checker identity;
- result and quantitative bounds.

### Attestation or signature

Evidence about origin and integrity. A signature can establish that a certificate came from a particular compiler build. It does not prove that the certificate’s claim is mathematically valid.

### Important invariant classes for CAM

**Representation invariants**

- numbers are finite;
- lengths are nonnegative where required;
- frame identifiers exist;
- tool diameters are positive;
- arc endpoints and radii are coherent.

**Path invariants**

- segment continuity;
- endpoint consistency;
- valid parameter domains;
- bounded curvature where required;
- tolerance metadata corresponds to construction.

**Machine-state invariants**

- cutting implies a loaded tool;
- cutting implies a valid spindle state;
- motion implies homed axes and a known frame transform;
- tool change implies spindle stopped.

**Geometric invariants**

$$
S_{i+1}\subseteq S_i
$$

Stock only decreases.

$$
P_{\text{protected}}\subseteq S_i
$$

Protected target material remains.

$$
O_{i+1}=O_i
$$

Fixtures are not altered.

**Compiler invariants**

- provenance is total;
- every artifact has a stable hash;
- no unsupported operation survives a full lowering pass;
- every approximation has an attached bound;
- raw commands are absent from production-certifiable programs.

**Temporal invariants**

- an executing job is the acknowledged uploaded job;
- authorization is not separated from execution by an unchecked state change;
- abort does not return success before motion cessation is confirmed;
- disconnection cannot silently become continued host-controlled motion.

---

## 10. Abstract interpretation is the right foundation for many validators

Abstract interpretation executes a program over an abstract domain that conservatively represents many concrete states. Its purpose is not to simulate one likely execution, but to over-approximate all possible executions relevant to a property. citeturn409138search1

Possible abstract domains for this compiler include:

```text
Position     = exact point | axis-aligned box | unknown
Velocity     = interval
Tool         = exact tool | set of tools | unknown
Spindle      = off | on[rpm interval] | unknown
Homing       = homed | unhomed | maybe
WCS          = known transform interval | unknown
Modal motion = G0 | G1 | G2 | G3 | set thereof
Stock        = conservative occupancy/height bounds
Frames       = known graph | inconsistent | unknown
```

An abstract interpreter for final G-code would update modal state and machine state block by block.

For example:

$$
\widehat\sigma_{i+1}
=
\widehat{\operatorname{transfer}}
(\widehat\sigma_i,b_i)
$$

The analysis is sound when:

$$
\sigma_i\in\gamma(\widehat\sigma_i)
\Longrightarrow
\operatorname{step}(\sigma_i,b_i)
\in
\gamma(
\widehat{\operatorname{transfer}}
(\widehat\sigma_i,b_i)
)
$$

where $\gamma$ maps an abstract state to the concrete states it represents.

### Applications

- modal-state validation;
- definite tool/spindle state;
- machine travel bounds;
- unreachable controller modes;
- possibly active coordinate systems;
- feed and spindle ranges;
- state after pause or resume;
- raw command effect propagation;
- loop and subprogram analysis.

A `RawCmd` should generally map affected abstract components to **unknown**. Its self-declared `effects` list may be displayed as an assumption, but should not be trusted as a proof unless independently parsed and checked.

### Proof-carrying abstract interpretation

A compiler can attach the abstract state before every block:

```ts
interface BlockInvariant {
  block: number;
  before: AbstractMachineState;
  after: AbstractMachineState;
}
```

A small checker verifies:

1. the first invariant includes the initial state;
2. each block transfer is sound;
3. adjacent block states connect;
4. each claimed safety predicate follows from the abstract state.

The expensive analyzer is then untrusted. The checker is the trusted component.

---

## 11. Numerical soundness and robust computational geometry

This is the hardest part of a credible CAM certificate.

The implementation must distinguish:

1. ideal mathematical geometry;
2. finite-precision representation;
3. numerical algorithm output;
4. a conservative enclosure of the true result.

Floating-point predicates used for topology—orientation, sidedness, intersections, contour joining—can give incorrect signs near degeneracies. Adaptive or exact predicates are a standard approach to making these decisions robust. citeturn525981search8

Interval arithmetic provides values guaranteed to enclose the exact mathematical result when implemented with the required rounding behavior. IEEE 1788.1 specifies a simplified interval arithmetic standard over binary64 endpoints. citeturn525981search4

### 11.1 Inner and outer approximations

For a geometric solid $X$, maintain:

$$
X^-\subseteq X_{\text{true}}\subseteq X^+
$$

where:

- $X^-$ is a guaranteed inner approximation;
- $X^+$ is a guaranteed outer approximation.

For collision avoidance, use outer approximations:

$$
\operatorname{Sweep}^+
\cap
O^+
=
\varnothing
\quad\Longrightarrow\quad
\operatorname{Sweep}_{\text{true}}
\cap
O_{\text{true}}
=
\varnothing
$$

For guaranteed removal, use an inner approximation:

$$
R^-\subseteq R_{\text{true}}
$$

For conservative residual stock, if $S_{\text{true}}\subseteq S^+$, then:

$$
S'_{\text{true}}
=
S_{\text{true}}\setminus R_{\text{true}}
\subseteq
S^+\setminus R^-
$$

Therefore:

$$
S'^+=S^+\setminus R^-
$$

is a sound outer bound on remaining stock.

This asymmetry is important:

- **outer swept volume** proves absence of collision or gouge;
- **inner swept volume** proves guaranteed removal;
- using one sampled sweep for both claims is generally unsound.

### 11.2 A grid size is not a proof

A statement such as “verified to a 0.2 mm grid” is meaningful only if the checker proves that unsampled behavior is bounded by the cell representation.

A point-sampling algorithm can miss:

- a narrow fixture;
- a thin target feature;
- a rapid crossing between samples;
- a small gouge between grid cells;
- a topology change;
- an acute cusp.

A sound grid certificate needs, for example:

- conservative cell occupancy;
- interval bounds over each cell;
- a Lipschitz bound;
- adaptive subdivision until a separating condition is proved;
- a guaranteed enclosure of the tool sweep.

Otherwise, the honest status is:

```text
sampled simulation; no continuous-domain guarantee
```

not:

```text
verified to resolution
```

### 11.3 Error budgets must be typed by metric

The current scalar `totalGeometric` is a useful warning mechanism, but formal error composition needs more structure.

Different errors use different metrics:

- Hausdorff path deviation;
- normal-direction surface error;
- maximum gouge penetration;
- frame-transform uncertainty;
- axis-following error;
- time or velocity error;
- tool-radius uncertainty.

They cannot all be added indiscriminately.

For a pass $f$ with Lipschitz constant $L_f$:

$$
\varepsilon_{\text{out}}
\le
L_f\varepsilon_{\text{in}}
+
\varepsilon_f
$$

A plain sum is sound only when:

- every contribution is a proven upper bound;
- all contributions use a compatible metric and frame;
- each transformation has amplification factor at most one, or amplification is included;
- correlations do not introduce an unmodeled effect.

A better representation is:

```ts
type ErrorBound =
  | {
      metric: "hausdorff-position";
      frame: FrameId;
      value: Mm;
    }
  | {
      metric: "normal-surface";
      surface: ArtifactRef;
      value: Mm;
    }
  | {
      metric: "max-gouge-depth";
      target: ArtifactRef;
      value: Mm;
    }
  | {
      metric: "transform-translation";
      transform: ArtifactRef;
      value: Mm;
    }
  | {
      metric: "transform-rotation";
      transform: ArtifactRef;
      value: Radians;
    };
```

### 11.4 Configuration-space reasoning

Collision checking can be formulated in configuration space: the moving tool/holder becomes a point, while obstacles are expanded into forbidden configuration regions. This is a standard motion-planning formulation. citeturn525981search2turn525981search11

For a fixed-orientation three-axis mill:

$$
O_{\text{C-space}}
=
O\oplus(-B_{\text{tool+holder}})
$$

A tool-center path is safe when it avoids this expanded obstacle.

This gives a clean semantic distinction between:

- free-space linking;
- material-removing motion;
- machine-axis limits;
- target protection.

---

## 12. Certificate design

Proof-carrying code separates an untrusted producer from a relatively small consumer-side checker: the producer supplies code plus evidence that the code satisfies a defined policy, and the consumer validates that evidence. citeturn662326search4turn662326search11

That architecture maps directly to CAM:

```text
large, complex, heuristic CAM compiler
              ↓
       program + evidence
              ↓
small independent certificate checker
              ↓
       accept or reject
```

The strategy generator, optimizer, simulator, and even most compiler passes can remain untrusted if their outputs are checked independently.

### 12.1 Claim schema

A claim should name an actual proposition, not merely a category such as “gouge.”

```ts
interface Claim {
  readonly id: ClaimId;

  readonly subject: ArtifactRef;
  readonly proposition: StructuredPredicate;

  readonly result:
    | "proved-exact"
    | "proved-bounded"
    | "exhaustive-finite-check"
    | "translation-validated"
    | "simulation-only"
    | "assumed"
    | "unknown"
    | "refuted";

  readonly method: MethodRef;
  readonly assumptions: readonly AssumptionRef[];
  readonly evidence: readonly EvidenceRef[];
  readonly dependencies: readonly ClaimId[];

  readonly bound?: ErrorBound;

  readonly checker: {
    id: string;
    version: string;
    binaryHash: Hash;
  };
}
```

Example propositions:

```text
forall t:
  machinePose(job, t) ∈ profile.travelEnvelope
```

```text
maxPenetration(
  sweptTool(job),
  protectedTarget
) ≤ 0.020 mm
```

```text
forall rapid r at stock state S_r:
  sweptToolHolder(r) ∩ (S_r ∪ fixtures) = ∅
```

```text
interpretRS274(emittedBytes, initialModalState)
  = controllerProgramTrace
```

```text
storedJobHash = certifiedJobHash
```

### 12.2 Evidence methods

| Method | Appropriate claim |
|---|---|
| Symbolic proof | Modal equivalence, state-machine invariants |
| Interval enclosure | Numeric bounds, transforms, curve extrema |
| Exact geometric predicates | Topology and intersection decisions |
| Abstract interpretation | State and range properties over a program |
| Translation validation | Individual compiler-pass output |
| Exhaustive finite-state checking | Controller protocol and interlock FSM |
| Conservative spatial cover | Collision and gouge bounds |
| Simulation | Diagnostics and testing, not universal proof |
| Physical calibration record | External machine/tool assumption |

### 12.3 Certificate dependency graph

Claims should form a DAG:

```text
source hash
   ↓
elaborated-plan hash
   ↓  unit/frame evidence
intent hash
   ↓  planning witness
toolpath hash
   ↓  approximation and target evidence
machine-program hash
   ↓  capability/travel evidence
controller-IR hash
   ↓  modal-equivalence evidence
G-code byte hash
   ↓  parse-back evidence
uploaded byte hash
   ↓  controller acknowledgement
execution-state snapshot
```

Changing any of these must invalidate dependent claims:

- machine profile;
- firmware semantics;
- tool or holder geometry;
- stock;
- target;
- fixture model;
- WCS transform;
- postprocessor settings;
- coordinate precision;
- safe height;
- emitted bytes.

### 12.4 Trusted computing base

The trusted base should be deliberately small:

- formal definitions of claim predicates;
- independent certificate checker;
- exact or interval numerical kernel used by the checker;
- final G-code parser and controller semantics;
- canonical serialization and hashing;
- runtime identity/hash handshake;
- physical assumptions explicitly accepted by the operator.

The following should ideally not be trusted:

- toolpath strategy implementations;
- contour stitching;
- heuristic ordering;
- simulator rendering;
- editor;
- JavaScript runtime;
- optimizer;
- main compiler orchestration.

### 12.5 Current `CheckStatus` redesign

The existing four-way distinction—

- exact;
- to-resolution;
- not checked;
- unverifiable—

is better than `safe: true`.

But it combines three different dimensions:

1. **What proposition was checked?**
2. **What method was used?**
3. **What result was obtained?**

Those should be separate.

For example:

```ts
{
  proposition: {
    kind: "max-gouge-depth",
    targetHash,
    maxAllowed: mm(0.02)
  },
  method: {
    kind: "conservative-interval-sweep",
    spatialSubdivisionLimit: mm(0.01)
  },
  result: "proved-bounded",
  bound: {
    metric: "max-gouge-depth",
    value: mm(0.017)
  }
}
```

This is substantially harder to misinterpret than:

```ts
gouge: {
  kind: "verified-to-resolution",
  spatial: 0.1,
  numerical: 0.01
}
```

---

## 13. Operations research belongs after feasibility semantics

Optimization should be expressed as:

$$
\min_x J(x)
$$

subject to:

$$
x\in\mathcal F
$$

where $\mathcal F$ is the independently checkable feasible set.

Typical hard constraints include:

- feature precedence;
- tool compatibility;
- fixture clearance;
- target protection;
- axis limits;
- maximum feed, velocity, acceleration, and jerk;
- maximum contour error;
- probing dependencies;
- stock-state dependencies;
- entry and engagement constraints.

The objective may include:

$$
J(x)=
T_{\text{cycle}}
+\lambda_1N_{\text{tool changes}}
+\lambda_2D_{\text{rapid}}
+\lambda_3J_{\text{wear}}
$$

but safety should not be a weighted penalty. It belongs in $\mathcal F$.

### 13.1 Operation sequencing

Toolpath ordering with precedence constraints can be modeled using variants of the precedence-constrained traveling salesman problem. This has been applied directly to CNC toolpath optimization. citeturn538704search2turn538704search15

Nodes can represent:

- operations;
- possible path orientations;
- entry points;
- tool/setup alternatives.

Edges represent transition costs:

- retract;
- free-space link;
- tool change;
- spindle acceleration;
- probing;
- setup transition.

A precedence graph captures constraints such as:

```text
rough before finish
probe before dependent geometry
drill pilot before large drill
machine internal feature before releasing surrounding stock
```

### 13.2 Reordering is not generally semantics-preserving

Geometrically:

$$
(S\setminus R_1)\setminus R_2
=
(S\setminus R_2)\setminus R_1
$$

But machining operations may still not commute because intermediate stock affects:

- entry feasibility;
- tool engagement;
- remaining support;
- chip evacuation;
- thin-wall deflection;
- workholding;
- rapid safety;
- probe results.

Each operation therefore needs effect summaries:

```ts
interface OperationEffects {
  readsStock: RegionSet;
  removesStock: RegionSet;
  readsProbeValues: readonly BindingId[];
  writesProbeValues: readonly BindingId[];
  requiresTool: ToolId;
  requiresFrame: FrameId;
  precedenceTags: readonly string[];
}
```

Two operations can be freely reordered only if an independence checker proves their effects commute under the process model.

### 13.3 Free-space linking

Link generation is a shortest-path or optimal-motion problem in configuration space:

$$
\min_\gamma
\int_0^1 c(\gamma(s),\dot\gamma(s))\,ds
$$

subject to:

$$
\gamma(s)\notin O_{\text{C-space}}
$$

For a simple three-axis machine, this might be a visibility graph, A*, or a conservative retract policy. More advanced linkers can use distance fields or Eikonal solvers.

Fast marching is a numerical method for solving the Eikonal equation and monotonically advancing fronts; it is useful for distance fields and optimal-path extraction. It does not by itself prove that a generated constant-scallop path achieves a physical scallop bound. That requires a separate theorem connecting the field discretization, surface model, tool geometry, and extracted contours. citeturn525981search0turn525981search5

### 13.4 Feed scheduling

Given a geometric path, feed scheduling is an optimal-control problem:

$$
\min T
$$

subject to:

$$
|\dot q_i|\le v_i^{\max}
$$

$$
|\ddot q_i|\le a_i^{\max}
$$

$$
|\dddot q_i|\le j_i^{\max}
$$

plus:

- contour-error bounds;
- servo tracking limits;
- spindle and chip-load constraints;
- process-force limits.

CNC minimum-time trajectory research formulates this as constrained optimal control, often including velocity, acceleration, jerk, and tracking-error constraints. citeturn538704search1turn538704search7

The optimizer’s certificate should distinguish:

- **feasibility**: independently verified constraints;
- **objective value**: measured cycle-time estimate;
- **optimality**: proven only when a lower bound or solver certificate supports it;
- **optimality gap**:

$$
\frac{J_{\text{candidate}}-L}{L}
$$

where $L$ is a valid lower bound.

A greedy heuristic can still be useful. Its result should be called “verified feasible with estimated cost $J$,” not “optimal.”

---

## 14. Runtime assurance is part of the proof

A compile-time certificate proves a conditional statement:

```text
this program is safe if these assumptions hold
```

At execution time, the system must establish those assumptions.

A minimum execution protocol should bind:

- machine identity;
- firmware version or semantics profile;
- machine-profile hash;
- tool and holder identity;
- active WCS and transform;
- homing state;
- fixture/setup identity;
- stock/target version;
- uploaded byte hash;
- current alarm and interlock state.

Conceptually:

```text
host:       propose job hash H and assumptions A
controller: report machine state M and stored hash H'
host:       verify H = H' and M satisfies A
host:       authorize execution of H
controller: acknowledge exact execution instance
```

For additional protection, runtime assurance can place a small trusted monitor around a more complex controller or planner. Simplex architectures use a trusted safety component that takes control when an advanced component would violate a safety condition. Formal runtime-assurance frameworks extend this idea to cyber-physical and hybrid systems. citeturn840691search0turn840691search6

For the Z1, a realistic small monitor could enforce:

- allowed controller state transitions;
- no command execution before hash-bound authorization;
- axis and feed command envelopes;
- no spindle/tool-state contradictions;
- watchdog and communication-loss policy;
- explicit abort acknowledgement;
- safe-stop state.

The monitor must account for latency and stopping distance. “Stop requested” is not equivalent to “motion has stopped.”

---

## 15. Applying this directly to the current implementation

Several current decisions are theoretically sound foundations.

### Good foundations

**Non-modal canonical commands**

This makes local analysis possible and delays modal state to one controlled lowering step. It aligns well with canonical machine semantics.

**Manufacturing intent before G-code**

This correctly treats G-code as a backend rather than the source language.

**Explicit provenance**

Provenance is required for diagnostics, certificate dependencies, and assurance-case explanations.

**`RawCmd` as visibly unanalysable**

Explicitly marking an escape hatch is better than silently embedding unknown syntax.

**Distinct pipeline types**

The `MachineProgram`/`ValidatedProgram` distinction prevents an important class of accidental API misuse.

**Check statuses more detailed than a boolean**

This is the right direction toward honest assurance.

### Where the theory exposes gaps

**`ValidatedProgram` proves only that one function was called**

The source comment already acknowledges this. The brand should remain an API gate, but evidence needs independent semantics and checkers.

**Travel is marked exact after sampling paths**

Sampling a curve is not an exact travel proof. Analytic line and arc bounds can often be computed exactly or conservatively; polysegments can be checked segment by segment. Unknown transforms should make the result conditional or unknown.

**The sampled certificate has no target-part input**

`buildCertificate()` receives simulation depth information but not target geometry. Therefore it cannot establish a proposition such as “maximum target gouge is below $x$.”

**One sampled status is reused for two different claims**

Rapid-through-stock and target gouge have different semantics, inputs, and evidence requirements.

**The scalar error-budget sum lacks a formal metric**

It is useful as a warning but not yet a compositional geometric proof.

**Path endpoint tolerance is treated like equality**

That supports practical construction but not strict categorical laws or non-accumulating proof.

**Certification occurs before all lowering is complete**

Any postprocessor operation—traverse expansion, arc lowering, modal compression, rounding, inserted spindle stops—must itself preserve the claims. The exact final bytes need a final certificate.

**Self-declared raw effects are not trustworthy**

They can help explain intent, but an unparsed raw command must conservatively invalidate affected analyses.

---

## 16. Recommended target architecture

```text
┌───────────────────────────────────────────────────────────┐
│ JavaScript macro environment                              │
│ isolated, deterministic, capability-limited               │
└───────────────────────────┬───────────────────────────────┘
                            │ immutable AST + source map
┌───────────────────────────▼───────────────────────────────┐
│ Elaborator                                                 │
│ units, frames, tools, references, finite-value checks      │
└───────────────────────────┬───────────────────────────────┘
                            │ typed Plan IR + evidence
┌───────────────────────────▼───────────────────────────────┐
│ Manufacturing planner                                     │
│ heuristic/optimization allowed                            │
└───────────────────────────┬───────────────────────────────┘
                            │ toolpaths + planning witness
┌───────────────────────────▼───────────────────────────────┐
│ Independent geometric checker                             │
│ intent conformance, target, stock, robust predicates       │
└───────────────────────────┬───────────────────────────────┘
                            │ certified Geometric Toolpath
┌───────────────────────────▼───────────────────────────────┐
│ Scheduler/linker/feed planner                             │
│ precedence, C-space, optimal control                       │
└───────────────────────────┬───────────────────────────────┘
                            │ scheduled trajectory + witness
┌───────────────────────────▼───────────────────────────────┐
│ Machine lowering                                          │
│ capabilities, frames, travel, controller interpolation     │
└───────────────────────────┬───────────────────────────────┘
                            │ Machine IR
┌───────────────────────────▼───────────────────────────────┐
│ Postprocessor                                              │
│ controller dialect, modality, serialization                │
└───────────────────────────┬───────────────────────────────┘
                            │ exact bytes
┌───────────────────────────▼───────────────────────────────┐
│ Independent final validator                               │
│ reparse, interpret, compare, geometric/temporal claims      │
└───────────────────────────┬───────────────────────────────┘
                            │ certificate DAG + byte hash
┌───────────────────────────▼───────────────────────────────┐
│ Runtime preflight and assurance monitor                    │
│ machine state, setup assumptions, upload/execution binding │
└───────────────────────────────────────────────────────────┘
```

The most important package additions would be:

```text
@cam/semantics
@cam/certificate-schema
@cam/checker-core
@cam/gcode-semantics
@cam/robust-geometry
@cam/controller-model
```

---

## 17. Practical implementation sequence

### Stage 1: Make claims precise and honest

- Replace generic certificate fields with structured propositions.
- Downgrade sampled simulation to `simulation-only`.
- Bind every claim to artifact and configuration hashes.
- Forbid “exact” unless the method genuinely covers the continuous domain.
- Treat raw controller text as unknown.

### Stage 2: Create executable reference semantics

Implement pure interpreters for:

- Plan IR;
- canonical commands;
- Machine IR;
- controller IR;
- emitted G-code modal state.

Add trace comparison and structured state snapshots.

### Stage 3: Add translation validators

Begin with passes that are discrete and comparatively easy to validate:

- modal compression;
- coordinate rounding;
- serialization/parse-back;
- traverse expansion;
- arc linearization;
- feed clamping;
- inserted preamble and shutdown commands.

This provides substantial confidence without proving the complete compiler.

### Stage 4: Build the geometric assurance kernel

- robust predicates;
- interval bounds;
- tool and holder solids;
- target and fixture models;
- conservative swept-volume subdivision;
- separate inner and outer material approximations;
- typed error metrics.

Keep complex strategy generators outside the trusted base.

### Stage 5: Model the controller protocol

Specify upload/start/pause/resume/abort/disconnect as a state machine. Check safety and liveness properties with model checking or a TLA-style specification.

### Stage 6: Mechanize the small trusted core

Do not begin by formalizing all CAM geometry.

The highest-value mechanization targets are:

- canonical command semantics;
- controller modal semantics;
- modal compression;
- interlock state machine;
- certificate checker;
- proof composition;
- artifact/hash binding.

The complex planners can remain ordinary TypeScript so long as independently checked evidence accompanies their output.

---

## 18. Primary reading path

A focused theoretical curriculum for this compiler is:

1. **Canonical machine semantics:** the NIST canonical machining-command and RS274 interpreter reports. citeturn662326search0turn662326search1
2. **Program contracts and invariants:** Hoare’s axiomatic semantics. citeturn409138search0
3. **Sound static approximation:** Cousot and Cousot’s abstract interpretation. citeturn409138search1
4. **State-indexed APIs:** typestate and parameterized monads. citeturn628227search8turn409138search8
5. **Multi-level IR architecture:** MLIR’s design and dialect-conversion legality model. citeturn628227search3turn628227search5
6. **Whole-compiler proof:** CompCert’s pass-by-pass semantic preservation. citeturn662326search8turn662326search12
7. **Per-compilation proof:** translation validation. citeturn840691search2turn840691search3
8. **Producer/checker separation:** proof-carrying code. citeturn662326search4
9. **Robust geometry:** adaptive exact predicates and interval arithmetic. citeturn525981search8turn525981search4
10. **Motion and path planning:** configuration spaces and fast marching. citeturn525981search11turn525981search0
11. **Controller protocols:** TLA and runtime-assurance/Simplex architectures. citeturn538704search0turn840691search0
12. **Machining optimization:** precedence-constrained sequencing and constrained feedrate optimal control. citeturn538704search2turn538704search1

## Bottom line

The decisive design change is this:

> Every pass should produce both an artifact and independently checkable evidence relating that artifact to its input. The final certificate should compose those relations and bind them to the exact G-code bytes, machine profile, tools, setup, controller semantics, and live execution state.

That gives a coherent foundation for the IR, compiler passes, invariants, geometry algorithms, optimization passes, safety certificates, and Z1 controller protocol.


---

> make a full textbook as markdown and pdf

I’ll build a self-contained, source-grounded textbook around Dropcut/Z1, covering formal semantics, IRs, certifying passes, geometry, controller protocols, exercises, and implementation guidance, then validate Markdown and PDF editions.

<details><summary>💭 Thinking</summary>

**Planning textbook creation**

I’m preparing the requested Markdown and PDF by inspecting the existing project materials, researching the relevant theory, and organizing chapters with examples, exercises, diagrams, and technical explanations.

**Planned textbook creation**

</details>

```unknown
bash -lc cat /home/oai/skills/pdfs/SKILL.md && printf '\n---DOCX?---\n' && ls -la /home/oai/skills/pdfs
```

<details><summary>💭 Thinking</summary>

**Building the textbook framework**

I’m shaping a self-contained textbook around compiler theory, intermediate representations, certified geometry, optimization, invariants, and assurance. I’ll connect those ideas to the project case study and include references, exercises, and examples.

**Built the textbook framework**

**Reviewed PDF requirements and inspected project archive and existing review**

</details>

```unknown
bash -lc set -e
cd /mnt/data/z1_textbook_work
rm -rf dropcut-studio
unzip -q /mnt/data/dropcut-studio.zip
find dropcut-studio/packages -maxdepth 3 -type f | sort | sed -n '1,240p'
printf '\nTop-level docs:\n'
find dropcut-studio -maxdepth 3 -type f \( -name '*.md' -o -name '*.ts' -o -name '*.go' \) | sort | sed -n '1,220p'
```

<details><summary>💭 Thinking</summary>

**Organizing implementation details**

I’m organizing the material into theory, verified compilation, geometry, optimization, certification, runtime assurance, and a project-specific implementation section, while keeping the final textbook coherent and practical.

**Organized implementation details**

**Inspected Dropcut repository and key implementation files**

</details>

```json
{"search_query":[{"q":"site:acm.org Hoare 1969 axiomatic basis computer programming DOI"},{"q":"site:dl.acm.org Cousot Cousot abstract interpretation 1977 paper"},{"q":"site:compcert.org CompCert semantic preservation documentation"},{"q":"site:research.google/pubs MLIR scaling compiler infrastructure domain specific computation paper"}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Preparing final files**

I’m consolidating the case study, theory chapters, implementation guidance, exercises, and bibliography into the requested Markdown and PDF deliverables, then I’ll verify the rendered PDF before sharing links.

**Defining the textbook scope**

I’m covering semantics, layered IR, effectful machine state, compiler correctness, geometric certification, optimization, runtime assurance, and a Dropcut case study, supported by primary references and practical exercises.

**Prepared final files and defined textbook scope**

</details>

The implementation inventory is complete; I’ll structure the book as an eight-part course using actual pipeline boundaries and failure modes, with the canonical non-modal IR as a running case study.

<details><summary>💭 Thinking</summary>

**Searched 2 websites**

</details>

```unknown
bash -lc sed -n '1,240p' /home/oai/skills/pdfs/SKILL.md && printf '\n--- create ---\n' && sed -n '1,220p' /home/oai/skills/pdfs/tasks/create.md && printf '\n--- convert ---\n' && sed -n '1,220p' /home/oai/skills/pdfs/tasks/convert.md
```

<details><summary>💭 Thinking</summary>

**Created certificate-carrying CAM compiler textbook with verified PDF figures**

</details>

```unknown
bash -lc cat >> /mnt/data/z1_textbook_work/book/Certificate_Carrying_CAM_Compilers.md <<'EOF'

\part{Part II - Language and Intermediate Representation Design}

# JavaScript as a Staged Macro Language

> **Learning objectives.** The reader should be able to separate an authoring language from the stable CAM language, explain staging and elaboration, and design a deterministic capability-limited script boundary.

## 7.1 The convenience and danger of embedded JavaScript

JavaScript is attractive as a CAM authoring language. It has familiar control flow, functions, data structures, packages, editors, and a large ecosystem. Parametric geometry becomes concise:

```ts
for (let i = 0; i < holeCount; i++) {
  drill({
    at: p(origin.x + i * spacing, origin.y, topZ),
    diameter: mm(3),
    depth: mm(8),
  });
}
```

But unrestricted JavaScript is a poor stable semantic core. It can inspect time, randomness, environment variables, files, network state, prototypes, and host globals. It can loop forever, mutate shared objects, invoke asynchronous callbacks after lexical scopes have ended, or depend on implementation details of the runtime.

The solution is not to discard JavaScript. It is to give it a precise role: **JavaScript is a macro language that constructs an inert CAM abstract syntax tree.**

## 7.2 Two languages, not one

The authoring language includes JavaScript syntax and its computational power. The stable CAM language is a serializable AST with explicit constructors and no executable closures.

```text
JavaScript source
     |
     | evaluate in isolated staged environment
     v
Immutable authoring AST
     |
     | elaborate names, units, frames, tools
     v
Plan IR
```

After staging, no compiler pass should call user-provided functions. The AST should contain only finite data, identifiers, source spans, and references to declared artifacts.

This resembles multi-stage programming: one program executes now to construct another program that will be analyzed and compiled later [R37]. The staging boundary is a semantic boundary and a security boundary.

## 7.3 Capability design

The script should receive an explicit capability object:

```ts
interface CamAuthoringCapabilities {
  units: UnitConstructors;
  geometry: GeometryConstructors;
  tools: ToolRegistryBuilder;
  plan: PlanBuilder;
  diagnostics: DiagnosticSink;
}
```

Capabilities prevent accidental ambient access, but ordinary lexical shadowing is not a security sandbox. Same-realm evaluation with `new Function` still exposes standard constructors and prototype chains. A hostile or simply defective script can also block the event loop indefinitely.

A production design should execute scripts in a separately terminable worker, process, or isolate with:

- no ambient network or filesystem access unless explicitly granted;
- a wall-clock deadline enforced outside the script;
- a memory limit;
- deterministic time and randomness sources;
- a versioned API module;
- structured input and output serialization;
- process termination on cancellation;
- no shared mutable object graph with the compiler.

## 7.4 Determinism and declared inputs

A reproducible authoring run should be modeled as:

$$
\operatorname{eval}(	ext{source},\text{apiVersion},\text{inputs},\text{seed})
=\text{AST}.
$$

Every input must be declared and content-addressed. If a script reads a mesh, tool library, material table, or project parameter, the compilation record should include its hash.

```ts
interface ScriptEvaluationRecord {
  sourceHash: Hash;
  languageVersion: string;
  apiVersion: string;
  inputArtifacts: readonly ArtifactRef[];
  deterministicSeed?: bigint;
  resultAstHash: Hash;
  diagnostics: readonly Diagnostic[];
}
```

The same record should be sufficient to reproduce the AST in a clean environment.

## 7.5 Scope combinators

An authoring API may use scoped operations:

```ts
withTool(tool, () => {
  withFeed(mmPerMin(400), () => {
    pocket(feature);
  });
});
```

A synchronous implementation usually saves state, invokes the callback, and restores state in `finally`. If the callback returns a promise, restoration can happen before awaited work completes. The apparent lexical semantics are broken.

There are three sound choices:

1. Prohibit asynchronous callbacks and detect promises at runtime.
2. Make the combinator explicitly asynchronous and await the callback before restoration.
3. Avoid dynamic scopes in the AST builder and pass immutable context explicitly.

For a deterministic macro language, the third option is often simplest.

## 7.6 Mutability at the boundary

If a tool object is registered and then retained by reference, later user mutation can change the plan after validation:

```ts
const tool = { diameter: mm(3.175), fluteLength: mm(12) };
registerTool("T1", tool);
tool.diameter = mm(8); // changes meaning if reference was retained
```

The builder should deep-copy and freeze boundary objects, or convert them immediately into canonical immutable records. Hashing an object only helps if the object cannot change afterward.

## 7.7 Worked example: staged pocket program

A good authoring run produces data such as:

```ts
const ast: AuthoringProgram = {
  version: "cam-authoring/1",
  tools: [{
    id: "T1",
    geometry: { kind: "flatEndMill", diameter: 3.175, fluteLength: 12 },
    source: { file: "job.cam.js", line: 3, column: 14 },
  }],
  operations: [{
    kind: "rectPocket",
    featureId: "P1",
    frame: "work:G54",
    origin: [10, 10, 0],
    size: [30, 20],
    depth: 4,
    tool: "T1",
    radialAllowance: 0.2,
    axialAllowance: 0.2,
    source: { file: "job.cam.js", line: 8, column: 3 },
  }],
};
```

The AST contains no closure that can later inspect the host environment. It can be validated, displayed, serialized, hashed, diffed, and compiled by another implementation.

## 7.8 Design rules

\begin{designrule}
Use JavaScript to construct an inert, immutable, content-addressed AST. Do not make the JavaScript realm, closures, mutable objects, or ambient globals part of the CAM semantics.
\end{designrule}

## 7.9 Exercises

1. List five ambient JavaScript capabilities that damage reproducibility.
2. Design a JSON-serializable AST node for a probing operation.
3. Explain why a timeout checked after a script returns is not an enforced timeout.
4. Show how a synchronous scope combinator fails with an async callback.
5. Define an isolation protocol between a Studio UI and a worker process.
6. Specify which fields must be hashed to reproduce an authoring run.

# A Multi-Level IR Architecture

> **Learning objectives.** The reader should be able to assign concerns to IR levels, define legality at each stage, and avoid both a monolithic universal IR and premature lowering.

## 8.1 Why one IR is not enough

A universal node type such as:

```ts
interface Operation {
  kind: string;
  data: unknown;
}
```

appears flexible but erases the guarantees that make passes understandable. At the other extreme, lowering directly from authoring syntax to G-code forces every planner to know controller details and destroys manufacturing provenance.

A multi-level compiler retains the right information at each stage and defines explicit conversion points. MLIR demonstrates the value of multiple dialects and legality-controlled transformations for domain-specific compilation [R16]. A CAM compiler benefits even more because its abstraction levels correspond to distinct physical meanings.

![A ladder of CAM intermediate representations.](figures/ir_ladder.png){width=98%}

## 8.2 Authoring AST

The authoring AST preserves:

- source spans;
- names and declarations;
- macros already expanded into data;
- user-level concepts;
- unresolved references where diagnostics benefit.

It should exclude arbitrary executable values after the staging boundary.

## 8.3 Elaborated Plan IR

Elaboration resolves:

- units;
- frames;
- tool references;
- geometry artifact references;
- defaults;
- scope-derived settings;
- identifier uniqueness;
- finite values and domain constraints.

The elaborated IR is the first stable, language-independent project representation. It should be possible to save it and compile it without re-running JavaScript.

## 8.4 Manufacturing Intent IR

Intent IR represents features and operations:

- pockets, holes, slots, surfaces, profiles;
- roughing and finishing requirements;
- allowances and tolerances;
- protected and permitted regions;
- dependencies and setup requirements;
- process constraints.

It deliberately excludes exact tool-center paths.

## 8.5 Geometric Toolpath IR

Toolpath IR contains continuous or piecewise-continuous curves with process semantics:

```ts
interface CuttingPath<F extends FrameId> {
  geometry: Path<F>;
  tool: ToolRef;
  feedPolicy: FeedPolicy;
  operation: OperationRef;
  phase: "entry" | "rough" | "finish" | "leadOut";
  directionality: "reversible" | "forwardOnly";
}
```

It should still be independent of a controller's modal syntax.

## 8.6 Scheduled Program IR

Scheduling introduces:

- a total or partially ordered operation sequence;
- path orientation choices;
- entries, retracts, and links;
- tool changes;
- probe dependencies;
- feed schedules or time laws;
- evolving stock-state references.

This is where semantics become stateful. A link that was safe before roughing may be unnecessary afterward; a path that was safe after roughing may be unsafe before it.

## 8.7 Machine IR

Machine lowering resolves:

- axis and kinematic capabilities;
- supported interpolation primitives;
- machine and work frames;
- travel limits;
- spindle and feed limits;
- tool-change behavior;
- probe and accessory capabilities;
- safe expansion of abstract traverses.

Every remaining operation must be supported by the selected machine profile or rejected.

## 8.8 Controller IR

Controller IR makes the controller's semantics explicit without committing to final formatting. It may contain:

- set units;
- select plane;
- select work offset;
- set absolute mode;
- linear and arc motion;
- probe cycle;
- spindle and accessory actions;
- upload metadata;
- program end.

The controller IR should have an interpreter. Final G-code text is then a serialization of this IR plus an optional modal-compression optimization.

## 8.9 Serialized Job Bundle

The final bundle contains more than `.nc` bytes:

- exact controller program bytes;
- content hash;
- machine and firmware profile hash;
- tool and holder manifest;
- stock, target, fixture, and frame artifacts;
- certificate graph;
- declared runtime assumptions;
- optional preview data generated from the same artifact.

## 8.10 Legality

Each IR has a legality predicate. Examples:

```text
Authoring AST legal:
  no executable closures; all nodes schema-valid

Plan IR legal:
  all units/frames/references resolved; all values finite

Toolpath IR legal:
  all paths continuous; operation provenance total

Machine IR legal:
  every operation supported; all coordinates machine-resolved

Controller IR legal:
  initial modal state explicit; no unknown raw effects

Job bundle legal:
  hashes match; required claims present; assumptions well formed
```

A conversion should fail when it cannot produce legal output.

## 8.11 Validation is evidence, not a dialect

A type named `ValidatedProgram` is useful as an API guard, but validation does not create a new language. It creates evidence about an artifact.

```ts
interface Certified<T> {
  artifact: T;
  artifactHash: Hash;
  claims: readonly Claim[];
  evidence: readonly Evidence[];
}
```

Different claims attach at different stages. Path continuity evidence belongs to a toolpath artifact; modal equivalence belongs to controller bytes; runtime identity belongs to an execution instance. One global boolean brand cannot express this graph.

## 8.12 Exercises

1. Assign each concern to an IR level: source span, scallop tolerance, tool-center curve, G17 plane, decimal formatting, upload filename.
2. Write legality predicates for a probing node in Plan IR and Machine IR.
3. Explain why a preview mesh should reference an artifact hash.
4. Give an example of information that must survive planning for later diagnostics.
5. Design an IR conversion that is partial and returns structured diagnostics.
6. Compare a multi-level IR with a universal stringly typed operation list.

# Paths and Curves as Composable Objects

> **Learning objectives.** The reader should be able to model paths categorically, distinguish path image from parameterization, identify the failure of approximate equality, and define safe composition contracts.

## 9.1 Paths as arrows

A path has a start and end pose:

$$
p:A\to B.
$$

If $q:B\to C$, then composition is defined:

$$
q\circ p:A\to C.
$$

A stationary path $\mathrm{id}_A:A\to A$ acts as an identity, and composition is associative. This is the free-category intuition behind a path builder.

```ts
interface Path<F extends FrameId> {
  frame: F;
  start: Point3<F>;
  end: Point3<F>;
  segments: readonly Segment<F>[];
}
```

A builder that derives `end` from appended segments establishes a valuable representation invariant: the declared endpoint cannot disagree with the final segment.

## 9.2 Geometry versus parameterization

A curve is often written:

$$
\gamma:[0,1]\to\mathbb{R}^3.
$$

Two parameterizations can trace the same geometric image at different rates. For geometric path equivalence, curves are commonly considered modulo monotone reparameterization. Concatenating two curves changes parameterization even when the physical trace is unchanged.

This matters because a geometric path is not a trajectory. Time enters later through a monotone map:

$$
s:[0,T]\to[0,1],\qquad x(t)=\gamma(s(t)).
$$

Velocity, acceleration, jerk, and controller following error belong to $s(t)$ and machine dynamics, not to the curve alone.

## 9.3 Segment algebra

Useful primitive segments include:

- line segments;
- circular or helical arcs with geometric center, axis, and sweep;
- splines with declared basis and knot domain;
- polylines with explicit approximation provenance;
- stationary segments or dwells at a pose.

Controller-specific arc offsets such as `I`, `J`, and `K` do not belong in geometric path IR. They are one encoding of the same geometry under a selected plane and endpoint convention.

## 9.4 Exact joins and approximate joins

Suppose path composition accepts endpoints when:

$$
d(a.end,b.start)<\varepsilon.
$$

This relation is not transitive. It cannot serve as exact object identity in a category. Repeated approximate joins can drift, and topology construction can merge unrelated endpoints.

Safer designs include:

1. Canonical snapping to exact grid or symbolic point identities.
2. Explicit join witnesses recording the displacement.
3. A path result carrying accumulated endpoint uncertainty.
4. Exact rational or integer coordinates for topology decisions.
5. A metric-enriched algebra where composition returns a new error bound.

```ts
interface JoinWitness<F extends FrameId> {
  leftEnd: Point3<F>;
  rightStart: Point3<F>;
  displacement: Mm;
  repair: "none" | "snap-right-to-left" | "insert-link";
}
```

An inserted link is not merely a numerical repair. It is a new motion that needs cut or traverse semantics and clearance checking.

## 9.5 Reversal and orientation

A geometric path can often be reversed, but a machining action may not be reversible. Direction affects:

- climb versus conventional milling;
- lead-in and lead-out geometry;
- cutter compensation;
- helical entry;
- probe direction;
- one-way process constraints;
- stock engagement.

Directionality belongs in metadata or the action type. An optimizer must not reverse paths solely because the point list is reversible.

## 9.6 Path continuity is not enough

A syntactically continuous path may still be invalid:

- an arc's declared endpoint may not lie on its circle;
- a polyline segment may include a first point inconsistent with the cursor;
- a spline may have a singular or non-finite evaluation;
- curvature may exceed process or dynamics limits;
- the path may cross forbidden material;
- the frame may be inconsistent.

Distinguish representation invariants from semantic properties.

## 9.7 Worked example: arc witness

An arc segment can be represented as:

```ts
interface ArcSegment<F extends FrameId> {
  to: Point3<F>;
  center: Point3<F>;
  axis: UnitVec3;
  sweep: Radians;
}
```

A checker given the start point verifies:

1. the axis is unit length within a certified bound;
2. start and end radial distances agree within tolerance;
3. the declared sweep rotates the start radius to the end radius;
4. any axial displacement is consistent with a helical interpretation;
5. all values are finite;
6. the chosen linearization, if any, satisfies its sagitta bound.

## 9.8 Design rules

\begin{designrule}
Use path composition to enforce endpoint discipline, but do not confuse numerical proximity with equality or structural continuity with machining safety. Make every repair an explicit, semantically classified operation.
\end{designrule}

## 9.9 Exercises

1. Prove associativity of exact segment-list concatenation.
2. Explain why parameterized-curve equality is too strict for geometric paths.
3. Design a metric-aware result type for approximate concatenation.
4. Give three reasons a path reversal may be illegal.
5. Specify checks for a helical arc.
6. Construct three endpoints that demonstrate non-transitivity of tolerance joins.
7. Explain why automatically inserting a line between discontinuous cut paths can be dangerous.

# Actions, Effects, and Indexed Commands

> **Learning objectives.** The reader should be able to model commands as effectful computations, explain Kleisli composition, and use indexed state to encode legal command sequencing.

## 10.1 A path is not an action

The same curve can denote a rapid traverse, cutting feed, probe motion, inspection scan, or air move. The geometry alone does not determine effects. A machining command changes machine and stock state, can fail, emits a trace, and may produce a value.

A simple state-and-error command type is:

$$
M(A)=\Sigma\to\operatorname{Result}(A\times\Sigma,E).
$$

In TypeScript:

```ts
type Command<A> =
  (state: MachineState) =>
    Result<{ value: A; state: MachineState }, CommandError>;
```

A probe command returns a measurement; a cut commonly returns `void` but changes stock and pose.

## 10.2 Why ordinary composition fails

Let:

$$
f:A\to M(B),\qquad g:B\to M(C).
$$

Ordinary composition $g\circ f$ is ill typed because $f$ returns $M(B)$ while $g$ expects $B$. A monad supplies `bind`:

$$
\operatorname{bind}:M(B)\times(B\to M(C))\to M(C).
$$

For a result-and-state computation, `bind` propagates errors and threads the updated state into the next command.

```ts
function bind<A, B>(ma: Command<A>, f: (a: A) => Command<B>): Command<B> {
  return state0 => {
    const ra = ma(state0);
    if (!ra.ok) return ra;
    return f(ra.value.value)(ra.value.state);
  };
}
```

This is Kleisli composition. Monads provide a disciplined way to compose effectful computations [R10, R11].

## 10.3 CNC effects

A realistic command effect includes more than mutable state:

```ts
interface CommandResult<A> {
  value: A;
  state: MachineState;
  trace: readonly Event[];
  assumptionsUsed: readonly AssumptionRef[];
  claimsProduced: readonly Claim[];
}
```

Potential effects include:

- failure and alarms;
- machine-state mutation;
- stock removal;
- logging and provenance;
- nondeterministic measurement;
- asynchronous controller interaction;
- resource use and time;
- uncertainty propagation.

An effect system can record which operations read or modify which resources [R14].

## 10.4 Indexed commands

A plain state monad does not express that the type of legal state changes. A parameterized or indexed command type does:

$$
\operatorname{Cmd}\langle S_{before},S_{after},A\rangle.
$$

Composition requires the post-state index of one command to match the pre-state index of the next [R13]. Typestate uses the same idea to restrict operations by protocol state [R12].

```ts
type StartSpindle<S extends Homed & HasTool> =
  Cmd<S, S & SpindleRunning, void>;

type Cut<S extends Homed & HasTool & SpindleRunning & KnownWcs> =
  Cmd<S, S & AtPathEnd, void>;
```

The source API can make impossible sequences difficult to construct.

## 10.5 Limits of type-level safety

TypeScript types are erased. A forged value, unchecked deserialization, stale controller state, or physical mismatch can violate the index. Type-level typestate proves a property of the host program under its model; it does not prove the machine is physically in that state.

Runtime preflight must re-establish assumptions at the execution boundary.

## 10.6 Algebraic effects versus monolithic state

One large `MachineState` can become difficult to reason about. An alternative is to describe effects separately:

```ts
type Effect =
  | ReadPose
  | RequireHomed
  | SelectTool
  | SetSpindle
  | Move
  | RemoveStock
  | Probe
  | EmitDiagnostic;
```

Handlers interpret these effects for simulation, validation, preview, or controller execution. This can improve modularity, but it still requires a coherent ordering and state model. The key is not the syntax of monads versus effect handlers; it is the explicit representation of effects and their laws.

## 10.7 Worked example: probe then offset

A probe returns a measured coordinate:

```ts
type Probe = Cmd<ProbeReady, ProbeReady, Measurement>;
type SetWorkOrigin =
  (m: Measurement) => Cmd<ProbeReady, KnownWcs, void>;
```

Kleisli composition connects the returned value to the next operation:

```ts
const establishWcs = probeSurface(direction, maxTravel)
  .flatMap(measurement => setWorkOrigin(measurement));
```

The data dependency is explicit. A command list that merely places `probe` before `set offset` without binding the result is semantically incomplete.

## 10.8 Exercises

1. Implement `pure` and `bind` for a result-and-state command type.
2. State the three monad laws and explain their practical value for command sequencing.
3. Design indexed states for unhomed, homed, tool-selected, and spindle-running modes.
4. Explain one invariant that TypeScript typestate cannot establish about a physical machine.
5. Model a probe command that can return contact, no contact, or alarm.
6. Compare a state monad with an explicit effect algebra for CAM.

# State Tokens, SSA, and Ordering

> **Learning objectives.** The reader should be able to use an SSA-style state token to make effects explicit, construct def-use dependencies, and identify which transformations are legal around stateful commands.

## 11.1 The machine state as a linear resource

A practical IR need not encode every typestate distinction in TypeScript generics. It can make ordering explicit with a state token. Each effectful operation consumes one token and produces the next.

![An SSA-style machine state token threads through commands.](figures/state_token.png){width=98%}

```text
%s0 = machine.initial
%s1 = machine.require_homed %s0
%s2 = tool.select %s1 @T1
%s3 = spindle.start %s2 12000rpm
%s4 = motion.cut %s3 path=@p feed=400
%s5 = spindle.stop %s4
```

The token is not the full runtime state. It is an ordering and dependency witness.

## 11.2 Relation to SSA

Static single assignment form gives each value one definition and makes data dependencies explicit [R15]. A machine-state token applies the same discipline to side effects. Operations cannot be silently reordered across token dependencies.

Pure geometry computations need no token:

```text
%p1 = path.offset %feature by=1.2mm
%p2 = path.reverse %p1
```

Effectful program construction does:

```text
%s1 = motion.traverse %s0 to=%p1.start
%s2 = motion.cut %s1 path=%p1
```

## 11.3 Multiple resources

One global token is simple but can over-serialize independent work. A richer IR can use separate tokens for:

- controller state;
- stock state;
- tool library state;
- measurement environment;
- diagnostic/provenance stream.

However, splitting resources requires precise alias and commutativity rules. Two cuts that affect disjoint stock regions might commute geometrically but not mechanically if they change support or linking clearance.

For an initial implementation, a single machine/process token is usually safer.

## 11.4 Probe values and control flow

SSA makes measurements explicit values:

```text
%m, %s1 = probe.toward %s0 direction=-Z max=10mm
%t       = frame.from_probe %m datum=@top_surface
%s2      = frame.install %s1 %t as=G54
```

A failed probe can branch:

```text
switch %m.status:
  contact -> continue
  no_contact -> abort
  alarm -> quarantine_session
```

The IR can represent merge points with block arguments or phi-like values. A validator must ensure that state invariants hold along every incoming path.

## 11.5 Effect summaries

Optimization and scheduling require summaries:

```ts
interface EffectSummary {
  reads: readonly ResourceRegion[];
  writes: readonly ResourceRegion[];
  requires: readonly Predicate[];
  ensures: readonly Predicate[];
  mayFail: readonly FailureClass[];
}
```

A pass may commute two operations only if their effects are independent and the reordered preconditions remain valid.

## 11.6 Linear and affine use

A state token should usually be consumed exactly once. Duplicating it would fork the machine into two contradictory futures. Dropping it can omit required shutdown or recovery behavior.

A linear type system enforces exactly-once use; an affine system permits dropping but not duplication. Most mainstream TypeScript code cannot enforce this statically, but the IR verifier can check def-use counts.

## 11.7 Worked example: preventing an unsafe reorder

Suppose an optimizer sees:

```text
%s1 = spindle.start %s0 12000rpm
%s2 = motion.cut %s1 @p
%s3 = spindle.stop %s2
```

Moving `spindle.stop` before the cut would require consuming `%s1` and producing a new state passed to the cut. The cut's `SpindleRunning` requirement fails. The token graph exposes the invalid transformation.

## 11.8 Exercises

1. Convert a small imperative command list into state-token SSA.
2. Explain why duplicating a machine state token is unsound.
3. Design a verifier for single-definition and single-consumption token use.
4. Show a legal reordering of two pure geometry operations.
5. Give a case where two cuts in disjoint regions still should not commute.
6. Model a branch after probing and the merge of its safe paths.

# Provenance, Identity, and Reproducibility

> **Learning objectives.** The reader should be able to design total provenance, content-address artifacts, distinguish identity from display names, and bind diagnostics and certificates to exact inputs.

## 12.1 Provenance is semantic data

When a final move fails a check, the system should explain which source operation, feature, strategy, and compiler pass produced it. Provenance is therefore not an optional debug string. It supports:

- diagnostics;
- certificate dependency graphs;
- incremental recompilation;
- audit and review;
- visual selection in the UI;
- comparison between compiler versions;
- fault localization.

## 12.2 A provenance chain

```ts
interface Provenance {
  sourceSpan?: SourceSpan;
  authoringNode?: NodeId;
  operation?: OperationId;
  feature?: FeatureId;
  strategy?: { id: string; version: string };
  passHistory: readonly PassRecord[];
  parentArtifacts: readonly Hash[];
}
```

Every transformation either preserves provenance, refines it, or introduces a synthetic operation with an explicit reason such as `safety-retract` or `postprocessor-spindle-stop`.

## 12.3 Content addressing

An artifact hash should cover canonical serialization of:

- semantic content;
- schema version;
- relevant configuration;
- referenced artifact hashes.

A display filename is not identity. Two jobs named `part.nc` may differ; the same job may have several names.

Canonical serialization must define:

- map key order;
- number format;
- treatment of negative zero;
- Unicode normalization;
- omitted versus null fields;
- endianness for binary data;
- schema versioning.

## 12.4 Reproducible passes

A pass result should be a function of explicit inputs:

$$
O=F(I,C,V,S),
$$

where $C$ is configuration, $V$ identifies the pass implementation, and $S$ is any declared random seed. Hidden time, locale, thread interleaving, or unordered iteration can break reproducibility.

Reproducibility does not guarantee correctness, but it makes evidence, debugging, and regression analysis tractable.

## 12.5 Machine and firmware identity

A machine profile named `z1` is not sufficient if firmware revisions change protocol or motion semantics. The executable bundle should identify:

- machine model and configured limits;
- controller dialect and firmware compatibility range;
- relevant capability flags;
- postprocessor version;
- calibration profile version;
- known semantic deviations.

Runtime preflight compares live identity with the bundle assumptions.

## 12.6 Provenance through optimization

An optimizer may merge, split, or reorder paths. It should retain a many-to-many mapping:

```ts
interface OriginMap {
  outputRange: CommandRange;
  inputs: readonly {
    artifact: Hash;
    operation?: OperationId;
    pathRange?: ParameterInterval;
  }[];
  transformation: string;
}
```

This allows a gouge counterexample at final block 813 to highlight the source finishing operation and the arc-fitting pass that changed it.

## 12.7 Worked example: cache key

A toolpath-planning cache key should include more than the feature geometry:

```text
hash(
  intentIR,
  targetMeshHash,
  stockHash,
  toolAssemblyHash,
  strategyIdAndVersion,
  planningTolerance,
  machine-relevant constraints,
  deterministicSeed
)
```

Omitting the tool hash can reuse a path computed for a different cutter. Omitting the tolerance can attach an outdated witness to a stricter request.

## 12.8 Exercises

1. Design a canonical serialization rule for floating-point numbers.
2. Explain why a filename is not an artifact identity.
3. List the inputs to a deterministic contour-planning cache key.
4. Define provenance for an automatically inserted retract.
5. Describe how a certificate becomes stale after a machine-profile change.
6. Give one source of nondeterminism in JavaScript object iteration or parallel planning and show how to control it.

# Designing an Extensible CAM API

> **Learning objectives.** The reader should be able to design an API that is composable, explicit about context, extensible through strategies and kernels, and resistant to invalid states.

## 13.1 Separate stable concepts from plugins

The stable API should expose semantic concepts:

- frames and units;
- stock, target, fixtures, and tools;
- manufacturing features and operations;
- paths and motion classes;
- tolerances, assumptions, and diagnostics;
- compilation and certification stages.

Strategies should be plugins:

```ts
interface Strategy<I extends OperationIntent, W> {
  id: string;
  version: string;
  supports(intent: I, context: PlanningContext): SupportResult;
  plan(intent: I, context: PlanningContext): Result<{
    paths: readonly PlannedPath[];
    witness: W;
  }, Diagnostic[]>;
}
```

A strategy may propose output; it should not mint final safety claims.

## 13.2 Kernel independence

Geometry algorithms should depend on interfaces rather than one mesh library:

```ts
interface SurfaceOracle<F extends FrameId> {
  bounds(): Box3<F>;
  heightAtXY(x: Mm, y: Mm): Interval<Mm> | "outside";
  closestPoint(p: Point3<F>): ClosestPointBound<F>;
  raycast(ray: Ray3<F>): readonly HitBound<F>[];
}
```

Different kernels can implement exact B-rep queries, mesh acceleration structures, interval fields, or remote computation. The semantic contract says what bounds the result provides.

## 13.3 Explicit contexts

Avoid ambient mutable settings such as “current feed,” “current tool,” or “current frame” inside planners. Pass immutable contexts:

```ts
interface PlanningContext {
  machine: MachineProfileRef;
  setup: SetupRef;
  activeTool: ToolRef;
  frame: FrameId;
  toleranceBudget: ErrorBudget;
  stockState: StockStateRef;
  seed: bigint;
}
```

The authoring API may offer convenient scopes, but elaboration should convert them into explicit fields.

## 13.4 Result types and diagnostics

Exceptions are appropriate for programmer errors and violated internal invariants. User-level compilation failures should be values:

```ts
type CompileResult<T> =
  | { ok: true; value: T; diagnostics: readonly Diagnostic[] }
  | { ok: false; diagnostics: readonly Diagnostic[] };
```

A diagnostic should include severity, stable code, source provenance, artifact context, quantitative details, and suggested remediation.

## 13.5 Escape hatches

Advanced users may need raw controller operations. An escape hatch should be isolated:

```ts
interface RawControllerBlock {
  text: string;
  declaredDialect: DialectId;
  declaredEffects?: EffectSummary;
  provenance: Provenance;
}
```

Self-declared effects are assumptions, not proof. An independent parser may establish actual effects for a supported grammar. Otherwise, affected analyses become unknown and production certification should fail closed.

## 13.6 API layers

A pleasant system can offer three layers:

**Feature API** for most jobs:

```ts
roughPocket(feature, { tool: "T1", strategy: "adaptive" });
finishPocket(feature, { tool: "T2" });
```

**Path API** for custom machining geometry:

```ts
cut(path, { tool: "T1", feed: mmPerMin(350), intent: "finish" });
```

**Machine API** for exact canonical actions:

```ts
program.append(traverse(path, clearance));
program.append(dwell(seconds(1)));
```

Lower layers carry more responsibility and require stronger evidence.

## 13.7 Law-driven API testing

Algebraic laws become property tests:

- path identity and associativity under exact endpoints;
- frame-transform identity and inverse;
- serialization round trip;
- deterministic planning under fixed inputs;
- pass idempotence for canonicalization;
- effect-summary conservativeness;
- certificate invalidation under changed dependencies.

The API design should make laws visible enough to test.

## 13.8 Worked example: compiling explicitly

```ts
const authored = evaluateScript(source, scriptEnvironment);
const plan = elaborate(authored.ast, projectContext);
const intent = normalizeIntent(plan.value);
const proposed = strategyRegistry.plan(intent, planningContext);
const checkedPaths = checkPlanningWitness(intent, proposed);
const scheduled = schedule(checkedPaths, schedulingPolicy);
const machine = lowerToMachine(scheduled, z1Profile);
const controller = lowerToMakera(machine, makeraDialect);
const bytes = serialize(controller);
const final = validateFinalArtifact({
  intent,
  machine,
  controller,
  bytes,
  setup,
});
```

Each call has an explicit input and output. There is no hidden global “current job” whose meaning changes between preview and export.

## 13.9 Exercises

1. Design a strategy interface for constant-Z waterline finishing.
2. Define a geometry-kernel query with a sound outer bound.
3. Explain when to use an exception versus a diagnostic result.
4. Design three API layers for drilling.
5. Specify how a raw controller block affects certification.
6. Write five algebraic or metamorphic properties for the API.
7. Explain why plugin version identity belongs in provenance.
EOF
wc -l -w -c /mnt/data/z1_textbook_work/book/Certificate_Carrying_CAM_Compilers.md
```

The first ten chapters are drafted, including bounded refinement, stock semantics, path/effect modeling, modal lowering, and JavaScript staging. Numerical guarantees now explicitly distinguish inner from outer approximations.

<details><summary>💭 Thinking</summary>

**Appended language design chapters and wrote compiler passes**

</details>

```unknown
bash -lc cat >> /mnt/data/z1_textbook_work/book/Certificate_Carrying_CAM_Compilers.md <<'EOF'

\part{Part IV - Assertions, Invariants, and Certificates}

# Contracts, Hoare Logic, and Weakest Preconditions

> **Learning objectives.** The reader should be able to distinguish assertions, invariants, assumptions, and guarantees; derive weakest preconditions; and use contracts to structure compiler and controller checks.

## 22.1 Vocabulary matters

Safety discussions become confused when different logical objects share the word “check.” The following distinctions should appear in code and certificate schemas.

An **assertion** is a proposition about one program point or artifact.

A **precondition** must hold before an operation.

A **postcondition** is guaranteed after successful execution, subject to assumptions.

An **invariant** holds initially and is preserved by all relevant transitions.

An **assumption** is an external fact not established by the current checker.

A **guarantee** is a proposition established when the assumptions hold.

A **witness** is data chosen by a producer to help establish a proposition.

A **proof or evidence object** is checked by a specified procedure.

An **attestation** establishes origin or integrity; it does not establish semantic truth.

## 22.2 Hoare triples

A Hoare triple has the form [R4]:

$$
\{P\}\ c\ \{Q\}.
$$

It means that if command $c$ starts in a state satisfying $P$ and terminates normally, the resulting state satisfies $Q$. Total-correctness variants also establish termination.

A traverse contract might be:

$$
\{
\operatorname{Pose}=a\land
\operatorname{Homed}\land
\operatorname{Free}(\gamma,T,O,S)
\}
$$

$$
\operatorname{Traverse}(\gamma)
$$

$$
\{
\operatorname{Pose}=b\land
S'=S\land
\operatorname{ProcessState}'=\operatorname{ProcessState}
\}.
$$

The stock-equality postcondition distinguishes traverse from cut.

## 22.3 Sequential composition

If:

$$
\{P\}\ c_1\ \{R\}
$$

and:

$$
\{R\}\ c_2\ \{Q\},
$$

then:

$$
\{P\}\ c_1;c_2\ \{Q\}.
$$

The intermediate assertion $R$ is the interface between commands. Compiler IR design should expose enough state to state $R$.

## 22.4 Weakest preconditions

The weakest precondition $wp(c,Q)$ is the least restrictive condition that guarantees $Q$ after $c$.

For sequential commands:

$$
wp(c_1;c_2,Q)=wp(c_1,wp(c_2,Q)).
$$

For an assignment $x:=e$:

$$
wp(x:=e,Q)=Q[e/x].
$$

For a conditional:

$$
wp(\mathrm{if}\ b\ \mathrm{then}\ c_1\ \mathrm{else}\ c_2,Q)
=(b\Rightarrow wp(c_1,Q))\land(\neg b\Rightarrow wp(c_2,Q)).
$$

A preflight engine can derive requirements backward from the program rather than maintaining an unrelated checklist.

## 22.5 CNC weakest-precondition example

Suppose the desired final condition is:

$$
Q=\operatorname{SpindleOff}\land\operatorname{Pose}=p_{safe}.
$$

The program is:

```text
cut path P
retract to p_safe
stop spindle
```

Working backward:

1. `stop spindle` requires a valid controller session and guarantees `SpindleOff`.
2. `retract` requires a collision-free path from `end(P)` to $p_{safe}$.
3. `cut` requires homing, known WCS, selected tool, valid spindle state, safe cutting sweep, and feasible feed.

The derived precondition becomes the basis of compile-time claims and runtime preflight.

## 22.6 Invariant induction

To prove invariant $I$ over a transition system:

1. **Initialization:** $I(\sigma_0)$.
2. **Preservation:** $I(\sigma)\land T(\sigma,\sigma')\Rightarrow I(\sigma')$.

Examples:

- stock monotonically decreases under cut and remains unchanged under traverse;
- every motion command has a known frame;
- cutting implies a selected tool and active spindle;
- an executing job has one content hash;
- an alarm state cannot transition directly to running without explicit recovery.

## 22.7 Separation of resources

Separation logic reasons about disjoint mutable resources [R38]. Its central intuition is useful even without a full separation-logic implementation. An operation that removes stock in region $A$ should not affect a disjoint fixture region $B$. Effect summaries can state footprints, enabling local reasoning and safe parallel analysis.

## 22.8 Design by contract in APIs

Contracts should be executable where possible:

```ts
function cut<S extends ReadyToCut>(
  state: S,
  motion: CuttingMotion,
): Result<CutResult, Diagnostic[]> {
  requireFinitePath(motion.path);
  requirePositiveFeed(motion.feed);
  requireToolMatch(state.tool, motion.tool);
  // geometric and runtime obligations remain explicit claims
}
```

Do not pretend that a runtime assertion about metadata proves physical collision freedom. Contracts should state the boundary of what they establish.

## 22.9 Exercises

1. Write a Hoare triple for spindle start.
2. Derive $wp$ for `select tool; start spindle; cut` with final condition `stock conforms to roughing intent`.
3. State and prove a stock-monotonicity invariant for a simplified semantics.
4. Distinguish an assumption from a precondition in a live tool check.
5. Give an example of a local resource footprint for two independent operations.
6. Explain partial versus total correctness for an abort command.

# Abstract Interpretation for Machine Programs

> **Learning objectives.** The reader should be able to define concrete and abstract domains, implement sound transfer functions, compute invariants over control flow, and use unknown states conservatively.

## 23.1 Simulating one trace is not analyzing all traces

A simulator executes one concrete state through one control path. A validator often needs to cover many possible states: unknown initial modal settings, uncertain positions, branches after probing, controller faults, or values from macros. Abstract interpretation computes over-approximations of these possibilities [R7].

Let $C$ be a concrete domain and $A$ an abstract domain. A concretization function:

$$
\gamma:A\to\mathcal{P}(C)
$$

maps an abstract value to the concrete states it represents.

A sound abstract transfer function $\widehat{F}$ satisfies:

$$
F(\gamma(a))\subseteq\gamma(\widehat{F}(a)).
$$

## 23.2 Abstract machine state

```ts
interface AbstractMachineState {
  position: Box3 | "unknown";
  homing: "homed" | "unhomed" | "maybe";
  tool: ToolRef | Set<ToolRef> | "unknown";
  spindle: "off" | RpmInterval | "unknown";
  wcs: TransformInterval | "unknown";
  motionMode: Set<MotionMode>;
  feed: Interval<number> | "unknown";
  playing: "yes" | "no" | "maybe";
  alarm: "yes" | "no" | "maybe";
}
```

The domain should be just expressive enough for the claims it checks.

## 23.3 Interval transfer

For a linear absolute move to $X=x$, the abstract X interval becomes $[x,x]$ after accounting for rounding and transform uncertainty. In incremental mode, it becomes:

$$
X' = X + [x-\rho,x+\rho].
$$

If distance mode is `{absolute, incremental}`, the successor joins both possibilities. Precision drops, but soundness remains.

## 23.4 Modal-state analysis

An abstract G-code interpreter can prove:

- units definitely metric;
- distance mode definitely absolute;
- spindle definitely on before each cut;
- position remains inside travel bounds;
- no motion occurs with unknown WCS;
- raw commands do not leave required modal components unknown;
- final spindle state is definitely off.

Each block records an invariant before and after:

```ts
interface BlockInvariant {
  blockIndex: number;
  before: AbstractMachineState;
  after: AbstractMachineState;
}
```

A small proof checker replays abstract transfers and verifies safety predicates.

## 23.5 Joins and loss of precision

If one branch selects tool T1 and another selects T2, the merge state contains `{T1,T2}`. A later operation requiring exactly T1 cannot be proved safe without a guard.

Widening may be necessary for loops. For example, repeated incremental motion can make position unbounded unless the loop count is bounded. A production-certifiable dialect may reject unbounded macros rather than analyze them imprecisely.

## 23.6 Reduced products

Different abstract domains can cooperate. A position box and a linear relation domain may jointly prove tighter bounds. A modal-state domain and typestate domain can reduce each other: if an alarm is definite, playing is false; if spindle is off, RPM interval is zero.

Such combinations increase checker complexity. Begin with simple domains tied to explicit claims.

## 23.7 Unknown raw effects

A raw block that is not parsed should conservatively set affected state to unknown. Self-declared effects can be recorded as assumptions, but they do not justify a proved claim.

```ts
function transferRaw(state: AbstractState, raw: RawBlock): AbstractState {
  return {
    ...state,
    position: "unknown",
    motionMode: allMotionModes,
    feed: "unknown",
    spindle: "unknown",
    wcs: "unknown",
  };
}
```

A later explicit preamble can re-establish some components.

## 23.8 Worked example: final spindle state

A program branches around an optional finishing pass. Both branches eventually execute `M5`. At the merge, spindle is definitely off. If one branch omits `M5`, the merge state is `{off,on}` and the final safety epilogue claim fails.

## 23.9 Exercises

1. Define a concretization function for an interval.
2. Write abstract transfer rules for G90, G91, G20, and G21.
3. Explain why joining branches loses precision.
4. Design a sound state update for an unknown raw command.
5. Show how a loop of incremental X moves can require widening.
6. Propose a reduced product relevant to probing and frames.

# Robust Numerics and Computational Geometry

> **Learning objectives.** The reader should be able to distinguish topological predicates from metric constructions, use exact or adaptive predicates, apply interval enclosures, and identify failure modes of floating-point geometry.

## 24.1 Why geometric bugs are discontinuous

A small floating-point error in a distance often causes a small distance error. A small error in a sign predicate can change topology completely: two contours connect instead of remaining separate, a polygon changes orientation, or an intersection is missed.

Computational geometry therefore distinguishes:

- **predicates**, which decide discrete facts such as orientation or intersection;
- **constructions**, which compute coordinates.

Predicates deserve stronger numerical methods.

## 24.2 Orientation predicates

For points $a,b,c$ in 2D, orientation is the sign of:

$$
\operatorname{orient2d}(a,b,c)=
(b_x-a_x)(c_y-a_y)-(b_y-a_y)(c_x-a_x).
$$

Near collinearity, floating-point cancellation can return the wrong sign. Adaptive exact predicates evaluate cheaply in ordinary cases and increase precision only near degeneracy [R22].

Use robust predicates for:

- polygon orientation;
- segment intersection;
- point-in-polygon decisions;
- Delaunay or Voronoi topology;
- contour stitching;
- mesh adjacency and ray intersections.

## 24.3 Exact topology, approximate geometry

A practical architecture can keep topology exact while allowing bounded approximate coordinates. For grid-generated contours, use grid-edge identifiers rather than re-quantized endpoint coordinates. For polygon kernels, use integer-scaled coordinates within a proven range or exact rational predicates.

The endpoint-key failure discussed later is a violation of this principle: a lossy packed coordinate is used as topological identity.

## 24.4 Interval arithmetic

An interval $[a,b]$ represents every real number between its endpoints. Arithmetic operations use outward rounding so the exact result is enclosed. IEEE 1788.1 specifies interval arithmetic over binary floating-point endpoints [R23]; Moore, Kearfott, and Cloud provide a broad treatment of interval analysis [R24].

If:

$$
x\in[a,b],\quad y\in[c,d],
$$

then:

$$
x+y\in[a+c,b+d]
$$

with outward-rounded endpoints. Multiplication takes the min and max of all endpoint products.

Intervals can bound:

- curve coordinates over a parameter range;
- transform uncertainty;
- distance to a surface;
- polynomial extrema;
- swept-volume occupancy;
- numerical residuals.

## 24.5 The dependency problem

Interval arithmetic can overestimate when the same variable appears repeatedly. For $x\in[0,1]$:

$$
x-x=[-1,1]
$$

under naive interval evaluation, although the true result is zero. Subdivision, affine arithmetic, Taylor models, or symbolic simplification can improve tightness.

An inconclusive wide interval is not a false result. The checker can subdivide or reject.

## 24.6 Conservative meshing

A triangle mesh is often treated as exact geometry, but it approximates a design surface. A certificate should record:

- source artifact hash;
- tessellation tolerance;
- orientation and watertightness status;
- whether the mesh encloses or is enclosed by the intended solid;
- repairs performed;
- unresolved non-manifold or self-intersection issues.

Without an enclosure relation, mesh-based collision checks prove facts about the mesh, not necessarily the intended CAD solid.

## 24.7 Tolerance and topology

Using one epsilon everywhere is dangerous. Distinct tolerances are needed for:

- numeric comparison;
- geometric construction;
- topological snapping;
- machining allowance;
- certification bound.

A topological snap modifies geometry. Its displacement must be recorded and charged to an error budget.

## 24.8 Worked example: collision of two nearly touching paths

Suppose a line passes $2\,\mu$m from a fixture in nominal double precision, while tool-radius uncertainty is $5\,\mu$m and frame uncertainty is $10\,\mu$m. An exact floating-point distance does not make the move safe. The relevant outer enclosure intersects the obstacle. Numerical exactness and physical robustness are different dimensions.

## 24.9 Exercises

1. Compute `orient2d` for three nearly collinear points and explain cancellation risk.
2. Distinguish a predicate from a construction.
3. Give a use of interval subdivision in curve bounding.
4. Explain the interval dependency problem.
5. Design metadata for a mesh enclosure claim.
6. List four different tolerances in a CAM compiler and their roles.
7. Explain why exact arithmetic does not eliminate model uncertainty.

# Swept Volumes, Stock Models, and Collision Proofs

> **Learning objectives.** The reader should be able to define swept volume, choose conservative stock representations, distinguish cutting from holder collision, and formulate no-gouge and guaranteed-removal claims.

## 25.1 Swept volume

For a tool solid $T$ and pose trajectory $x(t)$, the swept volume is:

$$
\operatorname{Sweep}(T,x)=\bigcup_{t\in[0,T]}x(t)T.
$$

Swept-volume computation is central to collision detection, stock simulation, and manufacturing verification [R26]. Exact computation is difficult for general geometry and trajectories, so practical systems use conservative enclosures or discrete representations.

## 25.2 Stock evolution

For cutting command $i$ with removed volume $R_i$:

$$
S_{i+1}=S_i\setminus R_i.
$$

A simulator may approximate $R_i$ using the swept cutting geometry. The semantic distinction among commands remains important:

- cut updates stock;
- traverse must not update stock;
- probe ideally stops at first contact and may touch without intended removal;
- tool change and dwell preserve stock.

If a missing traverse is silently converted to a cut, the stock semantics change, not merely the visualization.

## 25.3 Tool versus holder

Let $T_c$ be cutting geometry and $T_a$ the full assembly. Then:

**No target gouge:**

$$
\operatorname{Sweep}(T_c,x)^+\cap P_{protected}=\varnothing.
$$

**No fixture collision:**

$$
\operatorname{Sweep}(T_a,x)^+\cap O^+=\varnothing.
$$

**Guaranteed removal:**

$$
R_{required}\subseteq \operatorname{Sweep}(T_c,x)^-.
$$

The superscripts indicate outer and inner enclosures.

## 25.4 Dexel and voxel models

A dexel model stores material intervals along parallel rays. A height field stores one surface value per XY cell and cannot represent undercuts or multiple layers. Triple-dexel models use three orthogonal directions and improve surface representation [R27, R28]. Voxels represent occupancy in three dimensions.

Tradeoffs include:

- memory;
- update speed;
- ability to represent overhangs and cavities;
- surface error;
- ease of conservative enclosure;
- suitability for cutter contact.

For a three-axis no-overhang part, a height field can be efficient, but its resolution must be connected to a continuous-domain bound.

## 25.5 A grid size is not a guarantee

Sampling motion at spacing $h$ and stock on a grid of cell size $g$ does not by itself prove “verified to $\max(h,g)$.” A narrow fixture or brief penetration can occur between samples.

A sound cell method needs one of:

- conservative occupancy of every cell touched by the continuous sweep;
- interval bounds over each cell and motion interval;
- a Lipschitz bound plus adaptive subdivision;
- exact primitive sweep tests;
- a certified distance-field enclosure.

Otherwise, label the result simulation-only.

## 25.6 Configuration-space collision

For fixed orientation, configuration-space obstacles reduce moving-solid collision to point-path collision [R25]:

$$
O_C=O\oplus(-T_a).
$$

A clearance checker can build an outer enclosure $O_C^+$ and prove that the tool-reference path is separated by a positive bound.

For rotating tools or multi-axis orientation, configuration space has more dimensions and the expansion varies with orientation.

## 25.7 Continuous path checking

Lines and arcs often admit analytic bounds. Splines and sampled paths can be recursively subdivided. A generic branch-and-bound checker operates on parameter intervals:

1. Bound path positions over interval $I$.
2. Expand by tool assembly and uncertainty.
3. If disjoint from obstacle enclosure, accept $I$.
4. If definitely intersecting, return a counterexample interval.
5. Otherwise subdivide until a limit.
6. If the limit is reached unresolved, return inconclusive.

This produces honest coverage of the continuous parameter domain.

## 25.8 Worked example: rapid through stock

A rapid from A to B at low Z is safe only if the entire outer swept assembly is disjoint from current stock and fixtures. Checking endpoints misses an obstacle between them. Checking sampled points can miss a thin wall. A segment-versus-expanded-obstacle test or conservative recursive enclosure addresses the whole move.

## 25.9 Exercises

1. Write set formulas for no-gouge, fixture collision, and guaranteed removal.
2. Compare height fields, dexels, triple dexels, and voxels.
3. Explain why one grid resolution cannot be attached blindly to all claims.
4. Design a recursive continuous collision checker.
5. Give a case where cutting geometry is clear but holder geometry collides.
6. Explain how stock state affects link verification.

# Error Budgets and Quantitative Refinement

> **Learning objectives.** The reader should be able to construct typed error budgets, compose bounds through passes, allocate tolerances, and distinguish numerical, model, calibration, and process uncertainty.

## 26.1 A budget is a proof structure

An error budget is not merely a UI sum. It records how a final bound follows from component bounds under explicit propagation rules.

Sources include:

- design-surface tessellation;
- tool geometry approximation;
- tool dimension tolerance and runout;
- path planning discretization;
- curve fitting and linearization;
- coordinate transform uncertainty;
- numeric rounding;
- controller interpolation;
- servo following error;
- probing and calibration;
- thermal and material effects.

Some are compiler-controlled; others are runtime assumptions.

## 26.2 Typed metrics

```ts
type ErrorBound =
  | { metric: "hausdorff-position"; frame: FrameId; value: Mm }
  | { metric: "normal-surface"; surface: Hash; value: Mm }
  | { metric: "max-gouge-depth"; target: Hash; value: Mm }
  | { metric: "transform-translation"; transform: Hash; value: Mm }
  | { metric: "transform-rotation"; transform: Hash; value: Radians }
  | { metric: "axis-following"; axis: AxisId; value: Mm };
```

Only compatible bounds can be combined directly. Rotational error becomes positional error only after multiplying by a radius or applying a more precise transform bound.

## 26.3 Budget allocation

Suppose a feature tolerance is $0.05$ mm. The compiler may allocate:

```text
CAD tessellation             0.010 mm
planning and refinement      0.012 mm
postprocessor rounding       0.003 mm
frame and probing            0.010 mm
machine following            0.010 mm
reserve                      0.005 mm
```

This allocation is meaningful only if each number is a valid bound in a compatible metric and the composition theorem supports addition. A planner that consumes more than its allocation must refine or fail.

## 26.4 Correlation and worst-case composition

Worst-case scalar addition is conservative when errors can align. Root-sum-square composition assumes statistical independence and a probabilistic interpretation; it is not a deterministic maximum bound. Certificates must identify whether a claim is worst-case, probabilistic, empirical, or nominal.

## 26.5 Pass amplification

A small angular error $\delta\theta$ at radius $r$ creates positional error approximately $r\delta\theta$. An offset operation can amplify boundary error near sharp corners or topology changes. A coordinate transform with scale should not exist in rigid machining frames, but a calibration map may have local condition numbers.

Each pass needs a sensitivity or Lipschitz bound when it propagates prior error.

## 26.6 Residual-driven refinement

An adaptive algorithm should report a residual related to the claimed metric. For a height field, comparing neighboring samples is not automatically a surface-error residual. A useful refinement loop is:

```text
propose approximation
compute certified local bound
if bound <= allocated budget: accept cell
else if subdivision limit not reached: subdivide
else: inconclusive
```

The residual, subdivision depth, and unresolved regions become evidence.

## 26.7 Runtime budgets

Some budget components are checked at runtime. A tool measurement may tighten diameter uncertainty; a probe sequence may establish a frame bound; a machine calibration record may establish following-error limits. If live bounds exceed the bundle allocation, execution is refused or the job is recompiled.

## 26.8 Worked example: final surface error

Suppose:

- target mesh outer deviation: $0.008$ mm;
- drop-cutter field bound: $0.012$ mm;
- arc fitting: $0.004$ mm;
- output rounding: $0.001$ mm;
- frame translation: $0.010$ mm;
- angular frame uncertainty: $0.0002$ rad at 50 mm radius, contributing $0.010$ mm.

A conservative additive position bound is $0.045$ mm if the metrics and directions align. If the requested bound is $0.04$ mm, the program is not certified merely because each individual pass met its local default.

## 26.9 Exercises

1. Classify six error sources as numerical, model, calibration, or process uncertainty.
2. Convert an angular bound to a positional bound at a given radius.
3. Explain when root-sum-square composition is inappropriate.
4. Design a typed budget for a planar pocket floor.
5. State a residual-driven refinement algorithm.
6. Explain how a runtime measurement can discharge a compile-time assumption.

# Certificate Schemas and Proof Graphs

> **Learning objectives.** The reader should be able to write precise claims, bind them to artifacts and assumptions, organize dependencies as a DAG, and avoid ambiguous status labels.

## 27.1 A certificate is a graph of propositions

A certificate should not be one boolean or one table of reassuring labels. It is a graph connecting artifacts, assumptions, claims, evidence, and checkers.

![A certificate dependency graph binds source, IRs, final bytes, setup, and runtime state.](figures/certificate_dag.png){width=86%}

A change to any dependency invalidates downstream claims.

## 27.2 Structured claims

```ts
interface Claim {
  id: ClaimId;
  subject: ArtifactRef;
  proposition: StructuredPredicate;
  result:
    | "proved-exact"
    | "proved-bounded"
    | "translation-validated"
    | "exhaustive-finite-check"
    | "simulation-only"
    | "assumed"
    | "unknown"
    | "refuted";
  method: MethodRef;
  assumptions: readonly AssumptionRef[];
  evidence: readonly EvidenceRef[];
  dependencies: readonly ClaimId[];
  bound?: ErrorBound;
  checker: CheckerIdentity;
}
```

The proposition is not a string such as `"gouge"`. It is structured:

```ts
{
  kind: "max-penetration",
  sweptArtifact: "sha256:...",
  protectedTarget: "sha256:...",
  maximum: mm(0.02),
  metric: "signed-normal-depth",
}
```

## 27.3 Results and methods are orthogonal

“Checked to resolution” combines method and conclusion. Separate:

- proposition;
- method;
- result;
- quantitative bound;
- coverage;
- assumptions.

A sampled simulation method may produce a counterexample and thus refute a claim. Failure to find a counterexample does not upgrade it to proof.

## 27.4 Assumption records

```ts
interface Assumption {
  id: AssumptionId;
  proposition: StructuredPredicate;
  source: "operator" | "calibration" | "machine-attestation" | "library";
  evidence?: ArtifactRef;
  validFrom?: Timestamp;
  validUntil?: Timestamp;
  runtimeCheck?: RuntimeCheckSpec;
}
```

Examples:

- tool T1 diameter lies in $[3.170,3.180]$ mm;
- fixture model hash matches setup QR code;
- machine firmware belongs to a compatible semantic profile;
- G54 transform lies inside an interval;
- stock dimensions meet a measured bound.

## 27.5 Evidence types

```ts
type Evidence =
  | AbstractInterpretationTrace
  | IntervalSubdivisionTree
  | CollisionSeparationWitness
  | CoverageWitness
  | ParseBackTraceComparison
  | SolverCertificate
  | ModelCheckingTrace
  | Counterexample
  | CalibrationRecord
  | SignatureAttestation;
```

Evidence schemas should be stable, versioned, and independently checkable.

## 27.6 Claim granularity

Separate claims by meaning:

- target no-gouge;
- fixture collision;
- holder collision;
- rapid-through-stock;
- required removal;
- machine travel;
- feed and dynamics;
- modal equivalence;
- final spindle stop;
- exact upload hash;
- controller start acknowledgement.

One generic evidence object should not be able to mint unrelated rows. Strong typing can enforce this:

```ts
function certifyGouge(
  claim: GougeClaim,
  evidence: GougeEvidence,
): CertifiedClaim;
```

## 27.7 Completeness policy

A bundle policy states which claims are required for a use class:

```text
Preview-only:
  schema, finite values, parse success

Attended air cut:
  travel, controller parse-back, exact bytes, runtime identity

Attended material cut:
  + target, fixture, holder, stock, tool and WCS assumptions

Unattended production:
  + protocol liveness, runtime monitor, calibrated dynamic bounds,
    recovery and interlock claims
```

A function such as `isFullyVerified` must derive from explicit policy, not from absence of severe diagnostics.

## 27.8 Worked example: false evidence reuse

Suppose a dexel simulation checks low rapids and spoilboard penetration but receives no target surface. It can support:

```text
rapid-through-current-stock sampled simulation
spoilboard penetration sampled simulation
```

It cannot support:

```text
maximum gouge into protected target <= 0.02 mm
```

because the proposition's target artifact is absent. A schema that requires `protectedTargetHash` and target-specific evidence prevents the incorrect promotion.

## 27.9 Exercises

1. Write a structured claim for machine travel.
2. Design separate evidence types for rapid collision and target gouge.
3. Explain why a digital signature is not a semantic proof.
4. Define a completeness policy for an attended air cut.
5. Draw a dependency graph for an arc-linearized final job.
6. Describe certificate invalidation after a tool change.

# Trusted Checkers and Proof-Carrying CAM

> **Learning objectives.** The reader should be able to minimize a trusted computing base, explain proof-carrying code, design producer-consumer separation, and evaluate checker independence.

## 28.1 The producer is complicated

CAM planners use spatial indices, heuristics, solvers, floating-point kernels, caches, parallelism, and UI state. Treating this entire implementation as trusted makes assurance fragile.

Proof-carrying code separates an untrusted producer from a consumer-side checker: code arrives with evidence that it satisfies a policy, and the consumer validates the evidence before execution [R20]. Foundational proof-carrying code reduces reliance on specialized verification-condition generators by grounding evidence in a smaller logic [R21].

The analogous CAM architecture is:

```text
complex planner / optimizer / postprocessor
                 |
                 v
        artifact + evidence
                 |
                 v
       small independent checker
                 |
           accept or reject
```

## 28.2 Trusted computing base

A realistic trusted base includes:

- definitions of claim predicates;
- canonical artifact hashing and serialization;
- independent parsers and semantic interpreters;
- robust numeric primitives used by checkers;
- certificate dependency validation;
- runtime identity and upload-hash handshake;
- a small execution monitor;
- explicitly accepted physical assumptions.

The UI, heuristic planners, optimizers, and preview renderer should not need to be trusted.

## 28.3 Independence

A checker that calls the same buggy helper as the producer is not strongly independent. Independence can be improved by:

- separate implementations;
- different algorithms or representations;
- reduced feature set;
- smaller codebase;
- strict schemas;
- deterministic behavior;
- extensive property and differential testing;
- optional mechanized proofs for critical kernels.

Independence is a spectrum, not a binary property.

## 28.4 Proof objects versus recomputation

A checker can:

1. recompute the property independently;
2. verify a compact witness;
3. check a formal proof term;
4. combine these methods.

For contour coverage, a cell decomposition witness may be cheaper than re-running planning. For modal equivalence, replaying both programs is simple. For a linear or mixed-integer optimizer, a solver certificate or dual bound may support optimality.

## 28.5 Checker resource bounds

Evidence can be adversarial or malformed. Checkers need:

- schema validation;
- size and recursion limits;
- deterministic resource bounds;
- integer overflow protection;
- denial-of-service resistance;
- explicit version compatibility;
- no execution of producer-supplied code.

## 28.6 Compositional certificates

If pass $P_1$ establishes $R_1(A,B)$ and $P_2$ establishes $R_2(B,C)$, a composition theorem establishes $R(A,C)$:

$$
R_1(A,B)\land R_2(B,C)\Longrightarrow R(A,C).
$$

The theorem may accumulate quantitative bounds. Certificate composition should be implemented by a checker, not inferred from matching stage names.

## 28.7 Mechanization strategy

Formalize the small semantic core first:

- canonical command semantics;
- controller modal semantics;
- pass-relation composition;
- certificate validity;
- state-machine authorization;
- numeric lemmas for common primitives.

Leave complex search algorithms unverified but validated. This yields more assurance per unit effort than attempting to prove an entire CAM application at once.

## 28.8 Worked example: validating a solver schedule

An untrusted optimizer returns operation order $\pi$, path orientations, total cost $J$, and a lower bound $L$. The checker verifies:

1. $\pi$ is a permutation of required operations;
2. all precedence edges are respected;
3. every selected orientation is legal;
4. each transition cost is recomputed;
5. total cost equals the sum;
6. the lower-bound certificate is valid;
7. the reported gap $(J-L)/L$ is correct.

The optimizer's internal search does not enter the trusted base.

## 28.9 Exercises

1. List the trusted components in a minimal CAM checker.
2. Give an example where a checker is insufficiently independent.
3. Compare recomputation with witness checking.
4. Design resource limits for a certificate checker.
5. State a composition theorem for two bounded geometric passes.
6. Choose three components suitable for formal mechanization and justify them.

# Temporal Semantics and Controller Protocols

> **Learning objectives.** The reader should be able to model the host-controller interaction as a state machine, state safety and liveness properties, and reason about ambiguous failures and authorization races.

## 29.1 The protocol is part of the compiler target

A final G-code file is useless unless the correct bytes are transferred, stored, selected, and executed. The controller interface is therefore part of the compilation and deployment semantics.

![A simplified controller and job lifecycle state machine.](figures/controller_fsm.png){width=96%}

## 29.2 States and transitions

A controller model should include states such as:

- disconnected;
- connected but unidentified;
- idle;
- uploading;
- ready with a specific stored hash;
- running a specific execution instance;
- held;
- stopped;
- alarmed;
- ambiguous or quarantined after timeout.

Transitions have guards and effects. `Resume` is not a read-only command; it enables motion. `FeedHold` is a stop-class action and should remain available even when ordinary command admission is blocked.

## 29.3 Safety properties

Examples:

$$
\Box(\operatorname{Running}(h)\Rightarrow
\operatorname{Authorized}(h)).
$$

$$
\Box(\operatorname{Start}(h)\Rightarrow
\operatorname{StoredHash}=h).
$$

$$
\Box(\operatorname{Motion}\Rightarrow
\neg\operatorname{Alarm}).
$$

$$
\Box(\operatorname{GenericReadPath}\Rightarrow
\neg\operatorname{MotionEffect}).
$$

The last property requires complete parsing, not prefix classification.

## 29.4 Liveness properties

$$
\Box(\operatorname{UploadStarted}\Rightarrow
\Diamond(\operatorname{Ready}\lor\operatorname{Failed}\lor\operatorname{Quarantined})).
$$

$$
\Box(\operatorname{AbortRequested}\Rightarrow
\Diamond(\operatorname{Stopped}\lor\operatorname{Alarm})).
$$

Liveness depends on assumptions about network delivery, controller scheduling, and machine responsiveness. Those assumptions must be stated.

## 29.5 Atomic admission and execution

A preflight that checks state, releases a lock, and later sends motion has a time-of-check/time-of-use gap. Another command can change the state between admission and execution.

A safer design serializes:

```text
acquire session authority
refresh live state
check preconditions
bind authorization to command/job hash and state epoch
send command
observe acknowledgement or quarantine
release authority
```

The state epoch invalidates admission if intervening events occur.

## 29.6 Ambiguous timeout

After sending a command, a timeout does not imply that the machine did nothing. The command may have executed while the reply was lost. The correct successor state is a set of possibilities. The session should enter an ambiguous/quarantined state until re-synchronized through a trusted status query and protocol boundary.

Blind retry is especially dangerous for motion or state-changing commands.

## 29.7 Message streams and loss

Safety-relevant events should not share a lossy queue designed for UI telemetry. A dropped alarm, completion marker, or protocol sentinel can make the host state inconsistent. Separate durable control events from best-effort display updates.

Partial writes must also be handled. A transport `Write` may write fewer bytes than requested without a fatal error; command framing must loop until complete or fail before execution can be assumed.

## 29.8 Model checking

A finite abstraction of the protocol can be exhaustively checked for invariants and deadlocks. TLA-style specifications are well suited to concurrency and temporal properties [R8, R34]. Hybrid automata extend state machines with continuous dynamics when stop distance and watchdog timing matter [R35].

## 29.9 Worked example: compound command classification

A classifier that examines only the first whitespace token may label:

```text
status\nG0 X100
```

as read-only because `status` is first. The semantic policy concerns every parsed command in the payload. A fail-closed grammar rejects embedded newlines or parses all blocks and proves that every effect belongs to the allowed class.

## 29.10 Exercises

1. Define states and transitions for upload, start, hold, resume, and abort.
2. State three safety and two liveness properties.
3. Explain the time-of-check/time-of-use race in preflight.
4. Model an ambiguous timeout as a set of successor states.
5. Explain why stop commands should bypass ordinary motion admission.
6. Design a fail-closed read-only command grammar.
7. Identify which messages require durable delivery.

# Runtime Assurance and Physical Assumptions

> **Learning objectives.** The reader should be able to bind compile-time evidence to live machine state, design a runtime assurance monitor, and distinguish logical proof from physical validation.

## 30.1 Conditional assurance

A compile-time certificate proves a conditional theorem:

```text
if assumptions A hold, artifact B satisfies claims C
```

Runtime preflight must establish as much of $A$ as possible. The remaining assumptions require operator acceptance, calibration records, or physical interlocks.

## 30.2 Hash-bound execution

![A runtime handshake binds authorization to exact bytes and live state.](figures/runtime_handshake.png){width=88%}

A robust protocol is:

1. Host proposes certified bundle hash $H$ and assumptions $A$.
2. Controller stores exact bytes and reports stored hash $H'$.
3. Controller reports identity, firmware, homing, WCS, tool state, alarm state, and job state $M$.
4. Host verifies $H'=H$ and $M\models A$.
5. Host authorizes one execution instance of $H$.
6. Controller acknowledges start of that exact instance.
7. Host monitors state until terminal completion, abort, or fault.

## 30.3 Runtime checks

Possible checks include:

- machine identity and firmware semantics profile;
- homed axes;
- active work coordinate system and measured transform;
- tool ID, length, and optional diameter measurement;
- fixture/setup identifier;
- stock presence and dimensions;
- door, probe, and accessory interlocks;
- no active alarm;
- exact stored job hash;
- controller idle or permitted paused state;
- calibration validity period.

## 30.4 Runtime assurance monitor

A runtime assurance architecture places a small trusted monitor around a more capable controller or host planner. Simplex-style systems switch to a trusted safety action when an advanced component approaches an unsafe region; modern runtime-assurance frameworks apply this to cyber-physical systems [R36].

For a Z1-class machine, a realistic monitor can enforce:

- authorized state transitions;
- command classes;
- job-hash binding;
- axis and feed envelopes;
- spindle/tool consistency;
- watchdog policy;
- communication-loss behavior;
- explicit confirmation of stop.

## 30.5 Stopping distance and latency

A stop request is not an instantaneous stop. If velocity is $v$ and guaranteed deceleration is $a$, a simple lower bound on stopping distance is:

$$
d_{stop}\ge\frac{v^2}{2a},
$$

plus command, communication, and controller latency. A safety envelope must reserve this distance. Feed hold may preserve the job and decelerate differently from emergency stop or reset.

## 30.6 Physical model validation

Even perfect software cannot prove that the CAD fixture model matches reality. Useful physical validation practices include:

- setup identifiers and photographs;
- measured stock and tool records;
- probing routines with uncertainty;
- air cuts and reduced-feed first runs;
- witness marks or sacrificial stock;
- calibration artifacts;
- independent inspection of critical dimensions;
- bounded validity periods for calibration.

These produce assumptions and attestations, not mathematical facts from the compiler.

## 30.7 Degradation policies

A runtime system should define what happens when an assumption cannot be established:

- refuse execution;
- downgrade to preview or air-cut mode;
- require explicit operator override with recorded rationale;
- reduce feed and restrict motion envelope;
- re-probe or re-measure;
- recompile with wider uncertainty;
- quarantine the session after ambiguity.

Silent continuation is not a policy.

## 30.8 Worked example: changed G54

A job was certified under work transform $T_0$ with uncertainty set $\Xi$. Before execution, the live controller reports $T_1$. The runtime checker computes whether $T_1$ lies inside the certified set. If not, the travel and collision claims are stale. The correct response is to revalidate or recompile, not to rely on the same file hash.

## 30.9 Design rules

\begin{warningbox}
A certificate is valid only for the exact artifact and assumption set named by its claims. Live machine identity, tools, frames, setup, and controller state are inputs to execution, not incidental operator details.
\end{warningbox}

## 30.10 Exercises

1. Design a runtime assumption manifest for a pocket job.
2. Explain why upload success is weaker than exact-byte execution.
3. Derive stopping distance for a given velocity and deceleration, then add latency distance.
4. List five monitor-enforceable properties and five physical assumptions it cannot prove.
5. Design a degradation policy for an unknown tool measurement.
6. Explain how a changed WCS invalidates geometric certificates.
EOF
wc -l -w -c /mnt/data/z1_textbook_work/book/Certificate_Carrying_CAM_Compilers.md
```

<details><summary>💭 Thinking</summary>

**Drafted contract, CAM, architecture, appendix, and implementation chapters**

</details>

```unknown
bash -lc cat >> /mnt/data/z1_textbook_work/book/Certificate_Carrying_CAM_Compilers.md <<'EOF'

\appendix

# Notation and Mathematical Reference

This appendix collects the notation used throughout the book. It is intended as a working reference rather than a substitute for a course in analysis, geometry, logic, or optimization.

## A.1 Sets and functions

| Symbol | Meaning |
|---|---|
| $x\in A$ | $x$ is an element of set $A$ |
| $A\subseteq B$ | every element of $A$ belongs to $B$ |
| $A\cup B$ | union |
| $A\cap B$ | intersection |
| $A\setminus B$ | set difference |
| $A\times B$ | Cartesian product |
| $\mathcal{P}(A)$ | powerset of $A$ |
| $f:A\to B$ | total function from $A$ to $B$ |
| $R\subseteq A\times B$ | relation between $A$ and $B$ |
| $R;S$ | relational composition |

A partial function can be modeled as a total function into an option or result type, or as a relation with no successor for some inputs.

## A.2 Logic

| Symbol | Meaning |
|---|---|
| $\neg P$ | not $P$ |
| $P\land Q$ | $P$ and $Q$ |
| $P\lor Q$ | $P$ or $Q$ |
| $P\Rightarrow Q$ | implication |
| $P\Leftrightarrow Q$ | equivalence |
| $\forall x.P(x)$ | for every $x$, $P(x)$ |
| $\exists x.P(x)$ | there exists an $x$ satisfying $P(x)$ |
| $\Box P$ | always $P$ in temporal logic |
| $\Diamond P$ | eventually $P$ in temporal logic |

A safety property states that a bad event never occurs. A liveness property states that a good event eventually occurs. Many controller requirements combine both.

## A.3 Orders and lattices

A preorder $\sqsubseteq$ is reflexive and transitive. A partial order is also antisymmetric. In compiler refinement, $Q\sqsubseteq P$ commonly means that $Q$ has no behaviors outside those allowed by $P$.

A lattice provides least upper bounds $a\sqcup b$ and greatest lower bounds $a\sqcap b$. Abstract interpretation uses joins to combine control-flow paths.

## A.4 Metric spaces

A metric $d$ satisfies:

1. $d(x,y)\ge0$;
2. $d(x,y)=0$ iff $x=y$;
3. $d(x,y)=d(y,x)$;
4. $d(x,z)\le d(x,y)+d(y,z)$.

The open ball of radius $\varepsilon$ is:

$$
B_{\varepsilon}(x)=\{y\mid d(x,y)<\varepsilon\}.
$$

The distance from point $x$ to set $A$ is:

$$
d(x,A)=\inf_{a\in A}d(x,a).
$$

The Hausdorff distance between compact sets is:

$$
d_H(A,B)=\max\left(
\sup_{a\in A}d(a,B),
\sup_{b\in B}d(b,A)
\right).
$$

## A.5 Geometry and morphology

| Symbol | Meaning |
|---|---|
| $\mathbb{R}^n$ | $n$-dimensional Euclidean space |
| $SO(3)$ | three-dimensional rotation group |
| $SE(3)$ | rigid motions in three dimensions |
| $A\oplus B$ | Minkowski sum |
| $A\ominus B$ | erosion / Minkowski difference in morphological usage |
| $\partial A$ | boundary of $A$ |
| $\operatorname{int}(A)$ | interior of $A$ |
| $A^-$ | guaranteed inner approximation |
| $A^+$ | guaranteed outer approximation |

For sets $A,B\subseteq\mathbb{R}^n$:

$$
A\oplus B=\{a+b\mid a\in A,b\in B\}.
$$

The configuration obstacle for a translating tool $T$ and obstacle $O$ is $O\oplus(-T)$.

## A.6 Paths and trajectories

A geometric path is:

$$
\gamma:[0,1]\to Q,
$$

where $Q$ is configuration space. A time law is a monotone function:

$$
s:[0,T]\to[0,1].
$$

The trajectory is $q(t)=\gamma(s(t))$.

For a tool solid $T$ and pose $X(t)$:

$$
\operatorname{Sweep}(T,X)=\bigcup_t X(t)T.
$$

## A.7 Error and uncertainty

A deterministic bound states:

$$
|x-\hat{x}|\le\varepsilon.
$$

An interval enclosure states:

$$
x\in[x^-,x^+].
$$

A probabilistic statement has the form:

$$
\Pr(|X-\hat{x}|\le\varepsilon)\ge1-\alpha.
$$

These are not interchangeable.

## A.8 Optimization

A constrained optimization problem is:

$$
\min_x J(x)\quad\text{subject to}\quad g_i(x)\le0,\ h_j(x)=0.
$$

A lower bound $L$ and feasible candidate cost $J$ satisfy:

$$
L\le J^*\le J.
$$

The gap quantifies the possible distance from global optimality.

# Reference IR and Certificate Schemas

The following schemas are intentionally explicit. They illustrate a coherent design; a production implementation may split fields or use generated codecs.

## B.1 Primitive identities and units

```ts
type Hash = string & { readonly __brand: "sha256" };
type SchemaId = string & { readonly __brand: "schema" };
type ArtifactId = string & { readonly __brand: "artifact-id" };
type FrameId = string & { readonly __brand: "frame" };
type ToolId = string & { readonly __brand: "tool-id" };
type FeatureId = string & { readonly __brand: "feature-id" };
type OperationId = string & { readonly __brand: "operation-id" };
type ClaimId = string & { readonly __brand: "claim-id" };
type AssumptionId = string & { readonly __brand: "assumption-id" };

type Mm = number & { readonly __unit: "mm" };
type MmPerMin = number & { readonly __unit: "mm/min" };
type Rpm = number & { readonly __unit: "rpm" };
type Radians = number & { readonly __unit: "rad" };
type Seconds = number & { readonly __unit: "s" };

interface ArtifactRef<T = unknown> {
  readonly id: ArtifactId;
  readonly hash: Hash;
  readonly schema: SchemaId;
  readonly mediaType: string;
  readonly byteLength: number;
  readonly _type?: T;
}
```

## B.2 Frames and transforms

```ts
interface Point3<F extends FrameId = FrameId> {
  readonly x: Mm;
  readonly y: Mm;
  readonly z: Mm;
  readonly frame: F;
}

interface Quaternion {
  readonly x: number;
  readonly y: number;
  readonly z: number;
  readonly w: number;
}

interface RigidTransform<From extends FrameId, To extends FrameId> {
  readonly from: From;
  readonly to: To;
  readonly translation: readonly [Mm, Mm, Mm];
  readonly rotation: Quaternion;
}

interface TransformUncertainty {
  readonly translationBox: readonly [
    readonly [Mm, Mm],
    readonly [Mm, Mm],
    readonly [Mm, Mm],
  ];
  readonly angularRadius: Radians;
  readonly confidence: "deterministic-bound" | "probabilistic";
}
```

## B.3 Geometry and setup

```ts
type GeometryRef = ArtifactRef<GeometryArtifact>;

interface GeometryArtifact {
  readonly kind:
    | "mesh"
    | "brep"
    | "implicit"
    | "voxel"
    | "dexel"
    | "height-field"
    | "primitive";
  readonly frame: FrameId;
  readonly enclosure?: {
    readonly direction: "inner" | "outer" | "two-sided" | "none";
    readonly metric: ErrorMetric;
    readonly bound?: ErrorBound;
  };
}

interface ToolAssembly {
  readonly id: ToolId;
  readonly cuttingGeometry: GeometryRef;
  readonly assemblyGeometry: GeometryRef;
  readonly fluteLength: Mm;
  readonly stickout: Mm;
  readonly measurementUncertainty: readonly ErrorBound[];
}

interface SetupManifest {
  readonly stock: GeometryRef;
  readonly target: GeometryRef;
  readonly fixtures: readonly GeometryRef[];
  readonly tools: readonly ArtifactRef<ToolAssembly>[];
  readonly frameGraph: ArtifactRef<FrameGraph>;
  readonly workSystem: string;
  readonly material?: ArtifactRef;
  readonly setupIdentity?: string;
}
```

## B.4 Paths

```ts
interface LineSegment<F extends FrameId> {
  readonly kind: "line";
  readonly to: Point3<F>;
}

interface ArcSegment<F extends FrameId> {
  readonly kind: "arc";
  readonly to: Point3<F>;
  readonly center: Point3<F>;
  readonly axis: readonly [number, number, number];
  readonly sweep: Radians;
}

interface SplineSegment<F extends FrameId> {
  readonly kind: "spline";
  readonly basis: "bezier" | "bspline" | "nurbs";
  readonly degree: number;
  readonly controlPoints: readonly Point3<F>[];
  readonly knots?: readonly number[];
  readonly weights?: readonly number[];
}

type Segment<F extends FrameId> =
  | LineSegment<F>
  | ArcSegment<F>
  | SplineSegment<F>;

interface Path<F extends FrameId = FrameId> {
  readonly frame: F;
  readonly start: Point3<F>;
  readonly end: Point3<F>;
  readonly segments: readonly Segment<F>[];
  readonly identityPolicy: "exact" | "snapped" | "witnessed-approximate";
  readonly approximation?: readonly ErrorBound[];
}
```

## B.5 Intent IR

```ts
interface RegionSpecification {
  readonly geometry: GeometryRef;
  readonly interpretation:
    | "required-removal"
    | "forbidden-removal"
    | "permitted-removal";
}

interface SurfaceRequirement {
  readonly surface: GeometryRef;
  readonly metric: "normal-deviation" | "hausdorff" | "scallop-height";
  readonly maximum: Mm;
}

interface OperationIntentBase {
  readonly id: OperationId;
  readonly feature: FeatureId;
  readonly frame: FrameId;
  readonly toolConstraints: readonly ToolConstraint[];
  readonly predecessors: readonly OperationId[];
  readonly regions: readonly RegionSpecification[];
  readonly surfaceRequirements: readonly SurfaceRequirement[];
  readonly provenance: Provenance;
}

interface PocketIntent extends OperationIntentBase {
  readonly kind: "pocket";
  readonly floor: GeometryRef;
  readonly boundary: GeometryRef;
  readonly roughingAllowance: {
    readonly radial: Mm;
    readonly axial: Mm;
  };
}

type OperationIntent = PocketIntent | HoleIntent | SurfaceIntent | CustomIntent;

interface IntentProgram {
  readonly schemaVersion: string;
  readonly setup: ArtifactRef<SetupManifest>;
  readonly operations: readonly OperationIntent[];
}
```

## B.6 Toolpath and schedule IR

```ts
interface PlannedPath {
  readonly id: string;
  readonly path: ArtifactRef<Path>;
  readonly operation: OperationId;
  readonly tool: ToolId;
  readonly phase: "entry" | "rough" | "semi-finish" | "finish" | "exit";
  readonly directionality:
    | { readonly kind: "reversible" }
    | { readonly kind: "fixed"; readonly reason: string };
  readonly feedPolicy: FeedPolicy;
  readonly provenance: Provenance;
}

interface ScheduledStep {
  readonly id: string;
  readonly beforeState: string;
  readonly afterState: string;
  readonly beforeStock: ArtifactRef;
  readonly afterStock: ArtifactRef;
  readonly command: CanonicalCommand;
  readonly dependencies: readonly string[];
}

interface ScheduledProgram {
  readonly setup: ArtifactRef<SetupManifest>;
  readonly steps: readonly ScheduledStep[];
  readonly finalState: string;
}
```

## B.7 Canonical commands

```ts
type CanonicalCommand =
  | {
      readonly kind: "selectTool";
      readonly tool: ToolId;
    }
  | {
      readonly kind: "startSpindle";
      readonly rpm: Rpm;
      readonly direction: "cw" | "ccw";
    }
  | {
      readonly kind: "stopSpindle";
    }
  | {
      readonly kind: "traverse";
      readonly path: ArtifactRef<Path>;
      readonly clearanceClaim?: ClaimId;
    }
  | {
      readonly kind: "cut";
      readonly path: ArtifactRef<Path>;
      readonly tool: ToolId;
      readonly feed: FeedPolicy;
      readonly operation: OperationId;
    }
  | {
      readonly kind: "probe";
      readonly path: ArtifactRef<Path>;
      readonly expectedContact: ContactModel;
      readonly outputBinding: string;
    }
  | {
      readonly kind: "dwell";
      readonly duration: Seconds;
    }
  | {
      readonly kind: "pause";
      readonly reason: string;
    };
```

## B.8 Machine and controller IR

```ts
interface MachineCommandBase {
  readonly beforeToken: string;
  readonly afterToken: string;
  readonly provenance: Provenance;
}

type MachineCommand =
  | (MachineCommandBase & {
      readonly kind: "axisMove";
      readonly interpolation: "rapid" | "linear" | "cwArc" | "ccwArc";
      readonly target: Point3<"machine">;
      readonly center?: Point3<"machine">;
      readonly feed?: MmPerMin;
    })
  | (MachineCommandBase & {
      readonly kind: "setSpindle";
      readonly rpm: Rpm;
      readonly direction: "cw" | "ccw" | "off";
    })
  | (MachineCommandBase & {
      readonly kind: "probeMove";
      readonly direction: readonly [number, number, number];
      readonly maximumTravel: Mm;
      readonly feed: MmPerMin;
      readonly outputBinding: string;
    });

interface ControllerBlock {
  readonly words: readonly ControllerWord[];
  readonly comments: readonly string[];
  readonly provenance: Provenance;
}

interface ControllerProgram {
  readonly dialect: string;
  readonly declaredInitialState: ModalState;
  readonly blocks: readonly ControllerBlock[];
}
```

## B.9 Diagnostics and provenance

```ts
interface SourceSpan {
  readonly artifact: Hash;
  readonly start: { readonly line: number; readonly column: number };
  readonly end: { readonly line: number; readonly column: number };
}

interface PassRecord {
  readonly passId: string;
  readonly passVersion: string;
  readonly relation: string;
  readonly inputHashes: readonly Hash[];
  readonly configurationHash: Hash;
}

interface Provenance {
  readonly source?: SourceSpan;
  readonly feature?: FeatureId;
  readonly operation?: OperationId;
  readonly parents: readonly Hash[];
  readonly passHistory: readonly PassRecord[];
}

interface Diagnostic {
  readonly code: string;
  readonly severity: "info" | "warning" | "error";
  readonly message: string;
  readonly provenance?: Provenance;
  readonly claim?: ClaimId;
  readonly counterexample?: ArtifactRef;
  readonly remediation?: string;
}
```

## B.10 Quantitative claims

```ts
type ErrorMetric =
  | "hausdorff-position"
  | "normal-surface"
  | "max-gouge-depth"
  | "minimum-clearance"
  | "transform-translation"
  | "transform-rotation"
  | "axis-following";

interface ErrorBound {
  readonly metric: ErrorMetric;
  readonly value: number;
  readonly unit: "mm" | "rad";
  readonly frame?: FrameId;
  readonly subject?: Hash;
  readonly interpretation: "deterministic" | "probabilistic" | "empirical";
  readonly confidence?: number;
}

type StructuredPredicate =
  | {
      readonly kind: "disjoint";
      readonly left: Hash;
      readonly right: Hash;
      readonly minimumSeparation?: Mm;
    }
  | {
      readonly kind: "max-penetration";
      readonly swept: Hash;
      readonly protectedTarget: Hash;
      readonly maximum: Mm;
      readonly metric: "signed-normal-depth" | "euclidean-depth";
    }
  | {
      readonly kind: "contains";
      readonly outer: Hash;
      readonly inner: Hash;
      readonly tolerance?: Mm;
    }
  | {
      readonly kind: "trace-refines";
      readonly source: Hash;
      readonly target: Hash;
      readonly relation: string;
    }
  | {
      readonly kind: "runtime-state-satisfies";
      readonly state: Hash;
      readonly assumptionSet: Hash;
    };
```

## B.11 Certificate graph

```ts
interface CheckerIdentity {
  readonly id: string;
  readonly version: string;
  readonly binaryHash: Hash;
  readonly relationVersion: string;
}

interface Claim {
  readonly id: ClaimId;
  readonly subject: ArtifactRef;
  readonly proposition: StructuredPredicate;
  readonly result:
    | "proved-exact"
    | "proved-bounded"
    | "translation-validated"
    | "exhaustive-finite-check"
    | "simulation-only"
    | "assumed"
    | "unknown"
    | "refuted";
  readonly method: string;
  readonly assumptions: readonly AssumptionId[];
  readonly evidence: readonly ArtifactRef[];
  readonly dependencies: readonly ClaimId[];
  readonly bound?: ErrorBound;
  readonly checker: CheckerIdentity;
}

interface Assumption {
  readonly id: AssumptionId;
  readonly proposition: StructuredPredicate;
  readonly source: "operator" | "calibration" | "machine" | "library";
  readonly evidence?: ArtifactRef;
  readonly runtimeCheck?: string;
  readonly validUntil?: string;
}

interface CertificateGraph {
  readonly schemaVersion: string;
  readonly rootSubject: ArtifactRef;
  readonly artifacts: readonly ArtifactRef[];
  readonly assumptions: readonly Assumption[];
  readonly claims: readonly Claim[];
  readonly policy: string;
}
```

# Checker Algorithms

This appendix gives reference algorithms. They emphasize the shape of soundness obligations rather than a particular implementation language.

## C.1 Certificate graph checker

```text
checkCertificate(graph, policy):
  validate schema and version compatibility
  verify every artifact hash against its bytes
  build maps for artifacts, assumptions, and claims

  for each claim:
    require unique claim id
    require subject exists and hash matches
    require all dependencies exist
    require all evidence artifacts exist
    require all assumptions exist
    require checker identity allowed by policy

  require claim dependency graph is acyclic
  process claims in topological order:
    require dependencies have acceptable results
    invoke claim-specific checker
    compare returned proposition, result, and bound
    reject if producer metadata overstates checker result

  require every policy-required proposition exists
  require no required claim is unknown, assumed-only, or simulation-only
  return accepted graph plus normalized summary
```

Soundness depends on claim-specific checkers and policy definitions. The graph checker prevents missing, stale, cyclic, or cross-applied evidence.

## C.2 Translation-validation skeleton

```text
validatePass(input I, output O, witness W, relation R):
  verify hash(I), hash(O), hash(W)
  verify schemas and pass versions
  switch R:
    ExactTraceEquality:
      ti = interpret(I)
      to = interpret(O)
      return compareExact(ti, to)

    TraceRefinement:
      return checkSimulationRelation(I, O, W)

    BoundedGeometry(metric, epsilon):
      return checkGeometricWitness(I, O, W, metric, epsilon)

    IntentSatisfaction:
      return checkIntentWitness(I, O, W)

    FeasibleOptimization:
      f = checkFeasibility(O, W.feasibility)
      j = recomputeObjective(O)
      l = checkLowerBound(W.lowerBound)
      return combine(f, j, l)
```

## C.3 Abstract-state proof checker

```text
checkAbstractTrace(program, proof):
  require proof has one entry per block
  state = abstractInitialState(program.initialAssumptions)

  for i in 0 .. program.blocks.length-1:
    require state is included in proof[i].before
    computed = abstractTransfer(program.blocks[i], proof[i].before)
    require computed is included in proof[i].after
    require localSafetyPredicates(proof[i].before, program.blocks[i])
    state = proof[i].after

  require finalPolicy(state)
  return success
```

“Included” uses the abstract-domain order. The producer may provide less precise states than the checker computes, but they must remain conservative.

## C.4 Continuous collision checker

```text
checkPath(path gamma, assembly T, obstacles O, interval I, budget):
  P = boundPath(gamma, I)             // outer pose enclosure
  W = sweepEnclosure(P, T, uncertainty)

  if disjoint(W, outer(O)) with separation delta > 0:
    return ProvedSafe(I, delta)

  if definitelyIntersects(inner(W), inner(O)):
    return Refuted(I, counterexampleRegion)

  if width(I) <= budget.parameterLimit
     or diameter(P) <= budget.spatialLimit
     or recursionDepth >= budget.maxDepth:
    return Inconclusive(I, W)

  split I into I1, I2
  r1 = checkPath(gamma, T, O, I1, budget)
  r2 = checkPath(gamma, T, O, I2, budget)
  return combine(r1, r2)
```

The `definitelyIntersects` branch requires inner enclosures. If these are unavailable, the checker may prove safety or return inconclusive but cannot always prove collision.

## C.5 Required-removal checker

```text
checkRequiredRemoval(required R, cutMotions M):
  guaranteed = empty set
  for motion in M:
    innerSweep = computeInnerSweep(motion.tool, motion.path)
    guaranteed = union(guaranteed, innerSweep)

  residual = difference(R, guaranteed)
  if residual is empty by exact/conservative test:
    return proved
  if a definitely nonempty inner subset of residual is found:
    return refuted with residual witness
  return inconclusive with unresolved cells
```

## C.6 Modal parse-back checker

```text
checkFinalBytes(controllerIR C, bytes B, dialect D, initialState M0):
  parsed = independentParse(B, D)
  if parse error: reject

  sourceTrace = interpretControllerIR(C, M0)
  byteTrace = interpretParsedBlocks(parsed, M0)

  compare:
    event kinds and ordering
    tool/spindle/accessory state
    path endpoints and interpolation semantics
    probe command/result bindings
    final modal state
    numeric deviation against formatting budget

  verify required preamble and epilogue predicates
  return trace-equivalence or bounded-refinement claim
```

## C.7 Schedule checker

```text
checkSchedule(intent, candidate, witness):
  require candidate contains each required operation exactly once
  require no unknown operations

  positions = map operation -> index
  for each precedence edge (a,b):
    require positions[a] < positions[b]

  state = initial process state
  cost = 0
  for each step:
    require step preconditions hold in state
    verify chosen orientation and entry
    verify link against referenced stock state
    state = apply certified effects(step, state)
    cost += recompute transition and operation cost

  require state satisfies final policy
  require cost == witness.objective within numeric bound
  optionally verify lower-bound certificate
```

## C.8 Error-budget composition

```text
composeBound(inputBound e, passLocal p, sensitivity L, metric m):
  require e.metric == m or verified metric conversion exists
  require p.metric == m
  require L is a valid upper Lipschitz/sensitivity bound
  return L * e.value + p.value
```

For vector or transform bounds, use a matrix or interval propagation rule rather than a scalar function.

## C.9 Runtime authorization checker

```text
authorize(bundle B, liveState M, storedHash H'):
  verify certificate graph of B under requested operating policy
  require H' == B.jobHash
  require live machine identity matches B.machineProfile
  require firmware semantics compatible
  require no alarm and permitted controller state
  require homing state satisfies assumptions
  require active WCS lies inside certified transform set
  require tool and setup identity satisfy assumptions
  require calibration records valid

  epoch = read controller state epoch
  token = sign(jobHash, epoch, assumptionSnapshotHash, expiry)
  return one-use authorization token
```

Execution consumes the token only if the state epoch remains unchanged.

# A Temporal Controller Model

The following TLA+-style pseudocode illustrates a model suitable for refinement and model checking. It is not tied to a specific syntax version.

## D.1 Variables

```text
VARIABLES
  conn,                 \* disconnected | connected
  identity,             \* unknown or machine/profile identity
  ctrlState,            \* idle | uploading | ready | running | held | alarm | quarantined
  storedHash,           \* hash or none
  executingHash,        \* hash or none
  authorizedHash,       \* hash or none
  stateEpoch,           \* monotonically increasing integer
  commandQueue,
  durableEvents,
  telemetry,
  homed,
  activeWcs,
  tool,
  alarm,
  lastOutcome
```

## D.2 Initial state

```text
Init ==
  /\ conn = "disconnected"
  /\ identity = "unknown"
  /\ ctrlState = "idle"
  /\ storedHash = None
  /\ executingHash = None
  /\ authorizedHash = None
  /\ stateEpoch = 0
  /\ commandQueue = << >>
  /\ durableEvents = << >>
  /\ telemetry = << >>
  /\ homed = FALSE
  /\ activeWcs = Unknown
  /\ tool = Unknown
  /\ alarm = FALSE
  /\ lastOutcome = None
```

## D.3 Connection and identification

```text
Connect ==
  /\ conn = "disconnected"
  /\ conn' = "connected"
  /\ identity' = "unknown"
  /\ UNCHANGED <<ctrlState, storedHash, executingHash, ...>>

Identify(id) ==
  /\ conn = "connected"
  /\ identity' = id
  /\ stateEpoch' = stateEpoch + 1
  /\ UNCHANGED <<conn, ctrlState, storedHash, ...>>
```

## D.4 Upload

```text
BeginUpload(h) ==
  /\ conn = "connected"
  /\ ctrlState = "idle"
  /\ ctrlState' = "uploading"
  /\ storedHash' = None
  /\ lastOutcome' = None
  /\ stateEpoch' = stateEpoch + 1

UploadSucceeded(h) ==
  /\ ctrlState = "uploading"
  /\ ctrlState' = "ready"
  /\ storedHash' = h
  /\ Append(durableEvents, [kind |-> "upload-ack", hash |-> h])
  /\ stateEpoch' = stateEpoch + 1

UploadAmbiguous ==
  /\ ctrlState = "uploading"
  /\ ctrlState' = "quarantined"
  /\ storedHash' = Unknown
  /\ lastOutcome' = "ambiguous-upload"
  /\ stateEpoch' = stateEpoch + 1
```

## D.5 Authorization and start

```text
Authorize(h, epoch) ==
  /\ ctrlState = "ready"
  /\ storedHash = h
  /\ epoch = stateEpoch
  /\ homed
  /\ ~alarm
  /\ RuntimeAssumptionsHold(identity, activeWcs, tool)
  /\ authorizedHash' = h
  /\ UNCHANGED <<ctrlState, executingHash, stateEpoch, ...>>

Start(h) ==
  /\ ctrlState = "ready"
  /\ storedHash = h
  /\ authorizedHash = h
  /\ ctrlState' = "running"
  /\ executingHash' = h
  /\ authorizedHash' = None        \* consume one-use authorization
  /\ stateEpoch' = stateEpoch + 1
```

## D.6 Hold, resume, abort, and alarm

```text
FeedHold ==
  /\ ctrlState = "running"
  /\ ctrlState' = "held"
  /\ stateEpoch' = stateEpoch + 1

Resume(h, epoch) ==
  /\ ctrlState = "held"
  /\ executingHash = h
  /\ authorizedHash = h
  /\ epoch = stateEpoch
  /\ ctrlState' = "running"
  /\ authorizedHash' = None
  /\ stateEpoch' = stateEpoch + 1

Abort ==
  /\ ctrlState \in {"running", "held", "uploading", "ready"}
  /\ ctrlState' = "idle"
  /\ executingHash' = None
  /\ authorizedHash' = None
  /\ Append(durableEvents, [kind |-> "aborted"])
  /\ stateEpoch' = stateEpoch + 1

Fault(reason) ==
  /\ ctrlState \in {"running", "held", "uploading", "ready"}
  /\ ctrlState' = "alarm"
  /\ alarm' = TRUE
  /\ lastOutcome' = reason
  /\ authorizedHash' = None
  /\ stateEpoch' = stateEpoch + 1
```

## D.7 Next-state relation

```text
Next ==
  \/ Connect
  \/ \E id : Identify(id)
  \/ \E h : BeginUpload(h)
  \/ \E h : UploadSucceeded(h)
  \/ UploadAmbiguous
  \/ \E h, epoch : Authorize(h, epoch)
  \/ \E h : Start(h)
  \/ FeedHold
  \/ \E h, epoch : Resume(h, epoch)
  \/ Abort
  \/ \E reason : Fault(reason)
  \/ StatusUpdate
  \/ Disconnect
```

## D.8 Invariants

```text
TypeInvariant ==
  ctrlState \in {"idle", "uploading", "ready", "running", "held", "alarm", "quarantined"}

RunningIsAuthorized ==
  ctrlState = "running" => executingHash # None

RunningMatchesStored ==
  ctrlState = "running" => executingHash = storedHash

NoMotionInAlarm ==
  alarm => ctrlState # "running"

UnknownUploadCannotRun ==
  storedHash = Unknown => ctrlState # "running"

OneUseAuthorization ==
  ctrlState = "running" => authorizedHash = None
```

## D.9 Temporal properties

```text
AbortEventuallyTerminal ==
  [](AbortRequested => <>(ctrlState \in {"idle", "alarm", "quarantined"}))

UploadEventuallyResolves ==
  [](ctrlState = "uploading" => <>(ctrlState \in {"ready", "alarm", "quarantined", "idle"}))

NoHashSubstitution ==
  [](ctrlState = "running" => executingHash = storedHash)
```

These liveness properties require fairness and environment assumptions. A model checker should search for deadlocks, unauthorized transitions, stale-epoch authorizations, and dropped durable events.
EOF
wc -l -w -c /mnt/data/z1_textbook_work/book/Certificate_Carrying_CAM_Compilers.md
```

<details><summary>💭 Thinking</summary>

**Appended appendices and selected exercise solutions to textbook**

</details>

```json
{"search_query":[{"q":"site:doi.org 10.2493/jjspe.76.361 triple dexel"},{"q":"site:doi.org 10.1115/1.3086034 triple dexel swept volume"},{"q":"site:doi.org 10.1155/2014/835098 CNC minimum time feedrate"},{"q":"site:ntrs.nasa.gov 20230017350 runtime assurance framework"}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Building the reference list**

I’m reconciling publication details, correcting uncertain entries, and assembling a reliable bibliography covering semantics, verification, geometry, optimization, runtime assurance, and the project’s implementation context.

**Searched 2 websites**

</details>

```unknown
bash -lc tail -n 120 /mnt/data/z1_textbook_work/book/Certificate_Carrying_CAM_Compilers.md && printf '\n---FILES---\n' && find /mnt/data/z1_textbook_work/book -maxdepth 2 -type f -printf '%P %s bytes\n' | sort | tail -n 30
```

<details><summary>💭 Thinking</summary>

**Inspected textbook files, headings, references, and citation numbers**

</details>

```json
{"search_query":[{"q":"site:nist.gov NISTIR 5970 Canonical Machining Commands Proctor Kramer Michaloski DOI"},{"q":"\"Precedence Constrained Traveling Salesman Problem in CNC Tool Path Optimization\" DOI authors"},{"q":"\"Conversion between Triple Dexel Model and Polygon Model\" DOI Inui Sakurai Umezu"},{"q":"\"STEPNC++ - An Effective Tool for Feature-based CAM/CNC\" NIST authors 2009"}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Searched 6 websites**

</details>

```unknown
bash -lc grep -n '^\\appendix\|^# Notation\|^# Reference IR\|^# Selected' /mnt/data/z1_textbook_work/book/Certificate_Carrying_CAM_Compilers.md | head -20
```

<details><summary>💭 Thinking</summary>

**Audited textbook appendix headings and citations for references R42 and R43**

</details>

```json
{"search_query":[{"q":"site:nist.gov/publications \"Testing STEP-NC Implementations\""},{"q":"\"Dijkstra Monads for All\" DOI authors"},{"q":"\"Efficient Representation and Validation of Proofs\" DOI Necula Lee"},{"q":"site:compcert.org \"Formal Verification of a Realistic Compiler\""}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Searched 16 websites**

</details>

```unknown
bash -lc cat >> /mnt/data/z1_textbook_work/book/Certificate_Carrying_CAM_Compilers.md <<'EOF'

# Glossary

This glossary uses the meanings intended throughout the book. Several terms have broader meanings in compilers, formal methods, computational geometry, or manufacturing; the definitions below identify the interpretation relevant to a certificate-carrying CAM system.

**Abstract domain.** A mathematical domain whose elements conservatively represent sets of concrete program or machine states. Examples include intervals, axis-aligned boxes, finite sets of modal states, and symbolic frame relations.

**Abstract interpretation.** A framework for computing sound approximations of program behavior by interpreting a program over an abstract domain rather than enumerating concrete executions.

**Abstraction function.** A mapping from detailed physical or controller traces to the observations relevant at a higher semantic level, such as final stock, protected-surface penetration, or feature dimensions.

**Acceptance gate.** A machine-enforced condition that an artifact must satisfy before it can advance to a later lifecycle stage, such as preview, air cut, attended cutting, or production execution.

**Acyclic dependency graph.** A directed graph with no cycles. Certificate dependencies should normally form such a graph so that artifacts and claims can be checked in a finite topological order.

**Admissible set.** The subset of states, configurations, paths, or schedules satisfying all hard constraints.

**Affine transform.** A transform consisting of a linear map and a translation. Rigid frame transforms are the special case preserving distances and orientation or reflection, depending on the determinant.

**Alarm state.** A controller or machine state in which ordinary execution is blocked or modified because a fault, interlock, or exceptional condition has been detected.

**Alias collision.** Two distinct semantic objects receiving the same identifier or lookup key. In geometry this can merge unrelated endpoints, contours, cells, or topology components.

**Artifact.** An immutable, content-addressed input or output of a compiler stage: source, AST, IR, mesh, tool model, machine profile, controller program, serialized bytes, evidence, or certificate.

**Artifact identity.** The stable identity of an artifact, normally a cryptographic content hash plus a schema or media type. A filename or in-memory object address is not sufficient.

**Assertion.** A proposition intended to hold at one program point, controller state, geometric stage, or runtime checkpoint.

**Assumption.** An external fact required by a proof but not established by that proof. Tool measurement, machine calibration, fixture identity, controller conformance, and work-coordinate registration are typical assumptions.

**Assumption discharge.** The act of replacing an assumption with evidence or a runtime check that establishes it for a specific execution.

**Attestation.** Signed evidence about provenance, identity, configuration, or execution. Attestation authenticates a statement; it does not by itself establish the statement's mathematical truth.

**Authorization epoch.** A monotonically changing identifier binding an authorization decision to the machine state on which it was based. It prevents stale preflight results from authorizing later, changed states.

**Backend.** The portion of a compiler that lowers machine-independent operations to a target machine, controller dialect, serialization, or transport protocol.

**Bounded refinement.** A refinement relation that permits a quantified deviation under a named metric, such as Hausdorff distance, normal-direction surface error, or timing error.

**Canonical command.** A machine-oriented action with explicit machining meaning but without target-controller syntax or accidental modal dependence.

**Certificate.** A machine-checkable package binding claims, artifact identities, assumptions, evidence, dependency claims, checker identities, and quantitative bounds.

**Certificate checker.** A comparatively small program that validates evidence and decides whether a certificate claim follows for the named artifact under the named assumptions.

**Certificate DAG.** The dependency graph connecting source artifacts, transformed artifacts, claims, evidence, runtime facts, and final execution authorization.

**Certified artifact.** An artifact accompanied by one or more successfully checked claims. Certification is property-specific; it does not mean that every desirable property has been proved.

**Checker independence.** The degree to which a checker avoids sharing the producer's algorithms, data normalizations, hidden state, and defect modes. Independent implementation is often more valuable than nominal modular separation.

**Claim.** A precise proposition about a precise subject artifact, such as a travel-envelope inclusion or a maximum target-penetration bound.

**Clearance.** A distance or separation condition between the tool assembly and stock, target, fixtures, machine structures, or forbidden configuration-space regions.

**Closed-world command language.** A command language in which every permitted operation is explicitly enumerated and unknown operations are rejected. This is preferred for machine-control authorization.

**Compiler pass.** A transformation or analysis from one IR stage to another, ideally accompanied by an explicit semantic relation and a checker or proof obligation.

**Concrete semantics.** The detailed semantics of actual states and transitions, as opposed to an abstract analysis that represents sets of them.

**Configuration space.** A space whose points represent complete machine configurations. Collision of a moving solid can be transformed into point avoidance in an expanded forbidden region of configuration space.

**Conformance.** Satisfaction of a specification, standard, target intent, controller dialect, or certificate proposition.

**Conservative approximation.** An approximation oriented so that a successful check implies the desired property. Collision checks use outer obstacle and sweep enclosures; guaranteed-removal checks use inner removal enclosures.

**Constraint.** A hard condition defining feasibility. A safety constraint must not be converted into a soft objective penalty unless the resulting violations are categorically rejected later.

**Content-addressing.** Naming an artifact by a digest of its exact bytes and relevant encoding metadata, making changes observable and dependency invalidation mechanical.

**Controller dialect.** The syntax and operational interpretation implemented by a particular controller and firmware profile, including modal groups, commands, extensions, numeric ranges, and protocol behavior.

**Controller IR.** A structured representation of controller-level operations after machine lowering but before textual serialization.

**Controller semantics profile.** A versioned, content-addressed description of how a target firmware interprets commands, modes, uploads, acknowledgements, and lifecycle operations.

**Counterexample.** A concrete input, state, trace, geometry, or schedule showing that a claimed invariant or transformation relation is false.

**Cutting sweep.** The swept volume of the material-removing portion of the tool along a trajectory.

**Cyber-physical compiler.** A compiler whose target semantics includes physical mechanisms, continuous dynamics, sensors, actuators, material state, faults, and communication rather than only abstract machine instructions.

**Denotation.** The mathematical meaning assigned to a syntax element or IR object. A manufacturing operation often denotes a set of acceptable outcomes rather than one path.

**Denotational semantics.** A compositional mapping from programs or operations to mathematical objects such as functions, relations, traces, or sets of acceptable workpiece states.

**Dexel.** A depth element representing intervals of material along a ray. A triple-dexel model uses three orthogonal ray families.

**Diagnostic.** A structured explanation of an error, warning, unproved obligation, assumption, or source-to-output provenance relationship.

**Dialect conversion.** A checked transformation from one IR dialect or abstraction level to another under explicit legality and semantic-preservation rules.

**Dimensional type.** A type carrying physical dimension, such as length, angle, speed, acceleration, or spindle rate, so dimensionally invalid operations are rejected.

**Dijkstra monad.** A specification-indexed computational abstraction that associates effectful computations with predicate transformers or Hoare-style contracts.

**Discretization.** Replacement of a continuous object by finite samples, cells, segments, time steps, or basis coefficients. A discretization parameter alone is not a proof of continuous-domain error.

**Effect summary.** A conservative description of the state, resources, stock regions, probe values, frames, or modalities read and written by an operation.

**Effect system.** A static system that records and constrains computational or machine effects in addition to ordinary value types.

**Elaboration.** The pass that resolves names, defaults, units, frames, tools, parameters, and syntactic sugar into an explicit, typed representation.

**Enclosure.** A set guaranteed to contain an exact but potentially unknown quantity or geometry. Intervals and conservative swept volumes are enclosures.

**End-to-end theorem.** A statement relating checked source intent and assumptions to all permitted final physical executions, composed across every compiler, controller, and runtime boundary.

**Evidence.** Data consumed by a checker to establish a claim: proof terms, interval bounds, abstract states, parse-back traces, separating axes, spatial covers, solver certificates, or exhaustive state tables.

**Exact claim.** A claim established without an approximation tolerance relative to the stated mathematical input model. It can still depend on assumptions connecting the model to reality.

**Execution instance.** One uniquely identified controller run of one stored job under one machine-state epoch. A filename does not uniquely identify an execution instance.

**Feasible set.** The set of candidates satisfying all hard constraints. Optimization should search within this set rather than trade safety against cost.

**Final-byte validation.** Re-parsing and interpreting the exact serialized bytes that will be uploaded, then checking equivalence or refinement against the certified controller IR.

**Frame.** A coordinate system with an identity and transform relationships. Coordinates without frames are incomplete semantic values.

**Frame graph.** A graph of named coordinate frames and transforms, possibly with interval-valued uncertainty and time-varying measurements.

**Free-space link.** A non-cutting connection between machining segments whose tool-and-holder sweep is certified to avoid current stock, fixtures, protected geometry, and forbidden machine regions.

**G-code block.** One controller input record containing words evaluated under modal and dialect-specific semantics. Textual order inside a block does not necessarily imply sequential execution.

**Gouge.** Material removal beyond the allowed target or allowance region. A gouge claim requires a target or protected-material model.

**Hash binding.** Inclusion of an artifact hash in a claim, protocol step, authorization, or signature so the statement cannot silently transfer to different bytes.

**Hausdorff distance.** A metric measuring the greatest nearest-point deviation between two sets. It is useful for path approximation but does not alone encode orientation, process, or topology preservation.

**Height field.** A surface representation with one height per planar location. It is efficient for three-axis material models but cannot represent arbitrary undercuts or multiple layers.

**Hoare triple.** A contract of the form $\{P\}\;c\;\{Q\}$ stating that command $c$, when started in a state satisfying $P$, establishes $Q$ if it terminates.

**Hybrid system.** A system combining discrete mode transitions with continuous state evolution, such as controller states plus machine position, velocity, and braking dynamics.

**Identity morphism.** In a path category, the zero-motion path at a pose. It acts as the neutral element for path composition under the chosen equality notion.

**Information order.** A partial order describing precision of abstract values, often written $a\sqsubseteq b$ when $b$ contains at least as much uncertainty or information according to the selected convention.

**Inner approximation.** A set guaranteed to lie inside the true set. Inner removal approximations support claims that material was definitely removed.

**Intent IR.** A representation of manufacturing features, working steps, allowances, tolerances, resources, and dependencies before a specific tool-center path is selected.

**Interlock.** A condition preventing or terminating an operation when required safety or process state is absent.

**Interval arithmetic.** Arithmetic on closed intervals with outward rounding so the exact real-valued result remains enclosed.

**Invariant.** A property true initially and preserved by every relevant transition or compiler step.

**IR legality.** The syntactic, typing, capability, and semantic conditions an artifact must satisfy at a given intermediate representation level.

**Job bundle.** The complete execution package: exact program bytes, machine and firmware profiles, tool/holder models, stock/target/fixture artifacts, frame data, assumptions, certificates, and metadata.

**Kleisli composition.** Composition of effectful functions through a monad or indexed effect abstraction rather than ordinary function composition.

**Language sandbox.** An execution environment intended to restrict a macro or scripting language. A same-realm wrapper that retains access to host globals is not a security boundary.

**Lattice.** A partially ordered set in which every pair has a least upper bound and greatest lower bound. Many abstract domains use lattices to merge control-flow information and compute fixed points.

**Legality checker.** A checker deciding whether an IR contains only operations, types, frames, units, and capabilities permitted at that level.

**Lipschitz bound.** A constant $L$ satisfying $d(f(x),f(y))\le Ld(x,y)$. It describes how input uncertainty or approximation can be amplified by a transformation.

**Liveness property.** A temporal property stating that some desired event eventually occurs, such as an abort eventually reaching a stopped or faulted state.

**Lowering.** Refinement from a higher-level IR to a more concrete IR by selecting machine, controller, geometry, or serialization details.

**Machine envelope.** The admissible set of axis configurations or tool poses under travel, soft-limit, fixture, and machine-structure constraints.

**Machine IR.** A representation after target-machine capabilities, frames, kinematics, limits, and trajectories have been made explicit but before controller syntax is serialized.

**Machine profile.** A versioned artifact describing kinematics, axis limits, rates, acceleration, jerk, spindle and tool capabilities, controller dialect, and other target constraints.

**Macro language.** A language executed at compile time to construct an inert AST or plan. It should not retain arbitrary executable closures inside trusted compiler passes.

**Material-removal semantics.** A semantics in which cutting commands transform stock solids, typically by set difference with a cutting sweep.

**Metric.** A distance function satisfying non-negativity, identity, symmetry, and triangle inequality. Approximation claims must name the metric under which their bounds hold.

**Modal state.** Controller state that persists across blocks until replaced, such as motion mode, units, plane, feed, spindle speed, or work offset.

**Modal compression.** Omission of redundant modal words during serialization. It is correct only if interpreted traces remain equivalent under the specified initial state and dialect.

**Model checking.** Exhaustive or symbolic exploration of a finite or finitely abstracted transition system to establish temporal properties or find counterexamples.

**Monad.** A compositional abstraction for computations with effects. For CAM, state, failure, nondeterminism, logging, and external interaction are relevant effects.

**Monotone analysis.** An analysis whose transfer functions preserve the abstract-domain order, enabling fixed-point computation and sound iteration.

**Nondeterminism.** Multiple possible successor states or traces arising from underspecified intent, sensor uncertainty, communication outcomes, faults, or environmental variation.

**Numerical kernel.** The small collection of arithmetic, predicates, interval operations, and geometric primitives trusted by certificate checkers.

**Objective.** A quantity minimized or maximized among feasible candidates, such as cycle time, rapid distance, tool changes, energy, or predicted wear.

**Operational semantics.** Rules describing how a configuration changes step by step as commands execute.

**Operations research.** Mathematical modeling and optimization of decisions such as operation sequencing, tool assignment, linking, and feed scheduling under constraints.

**Outer approximation.** A set guaranteed to contain the true set. Outer sweeps and obstacles support collision-absence and no-gouge claims.

**Parse-back validation.** Parsing emitted controller bytes back into structured IR and comparing their interpreted semantics with the pre-serialization artifact.

**Partial correctness.** A guarantee that the postcondition holds if execution terminates. It does not prove termination or eventual progress.

**Pass contract.** A specification of a pass's accepted input, produced output, semantic relation, error bound, assumptions, diagnostics, witness, and checker.

**Path.** A parameterized geometric curve through a frame. It does not by itself define timing, controller interpolation, or material-removal process.

**Path equivalence.** The chosen relation under which two path values are considered semantically equal, often equality modulo monotone reparameterization and a stated geometric tolerance.

**Path parameterization.** A monotone function mapping time to geometric path progress. It determines velocity, acceleration, jerk, and cycle time along a fixed path.

**Planner.** A generally complex and heuristic producer that chooses a toolpath, schedule, or process implementation satisfying an intent specification.

**Postcondition.** A proposition promised after an operation terminates from a state satisfying its precondition.

**Postprocessor.** A target-specific compiler backend lowering machine or canonical IR into a controller dialect and exact serialized job bytes.

**Precondition.** A proposition that must hold before an operation may execute or a theorem may be applied.

**Predicate transformer.** A function mapping desired postconditions backward to sufficient preconditions. Weakest-precondition semantics is a principal example.

**Process model.** A model of cutting, probing, spindle, stock, tool engagement, or machine dynamics used to interpret and check operations.

**Proof obligation.** A proposition that must be established before a pass result, job bundle, or runtime action can be accepted.

**Proof-producing analysis.** An analyzer that emits evidence allowing a smaller checker to validate its result rather than requiring the analyzer itself to be trusted.

**Protected material.** Target or fixture material that a claim forbids the cutting sweep from entering beyond a stated tolerance.

**Provenance.** Structured information linking output objects and diagnostics to source spans, compiler passes, parameters, input artifacts, and tool versions.

**Quantization.** Mapping continuous or high-precision values to discrete integer bins. Quantization can be useful, but a lossy packed key must not be mistaken for unique topology identity.

**Rapid safety.** A claim that a non-cutting motion's tool-and-holder sweep avoids current stock and obstacles under controller rapid semantics and machine uncertainty.

**Raw command.** An escape hatch containing target syntax whose effects have not been derived from a trusted parser. Conservative analyses must reject it or set affected abstract state to unknown.

**Reachability.** The set of states obtainable from an initial state under the transition relation and assumptions.

**Reference semantics.** A simple, explicit semantic implementation used as the standard against which optimized or target-specific implementations are compared.

**Refinement.** A relation in which a concrete implementation removes choices or adds detail without introducing behavior forbidden by the abstract specification.

**Refinement mapping.** A mapping from concrete states and traces to abstract states and traces used to demonstrate that one system implements another.

**Representation invariant.** A property ensuring an in-memory value is internally coherent, such as a path endpoint matching its last segment. It is narrower than a machining-safety claim.

**Residual stock.** Material remaining after the modeled removal operations. Conservative residual stock usually requires outer stock and inner removal approximations.

**Robust predicate.** A predicate whose result is correct for the mathematical input model despite floating-point degeneracy, normally through filtered, adaptive, exact, or interval methods.

**Runtime assurance.** A small trusted mechanism that monitors an advanced component or physical system and intervenes before a safety property can be violated.

**Safety property.** A temporal property stating that a bad event never occurs. A finite violation has a counterexample prefix.

**Semantic preservation.** Equality, refinement, or bounded correspondence between the meanings of a pass input and output.

**Semantic waist.** A compact intermediate language separating many high-level producers from many low-level targets while retaining the physical distinctions needed for correctness.

**Serialization.** Conversion of structured controller IR to exact bytes, including number formatting, line endings, comments, checksums, and encoding.

**Signature.** A cryptographic authentication of bytes or statements. A signature establishes origin and integrity under a key-management assumption, not semantic correctness.

**Simulation-only result.** Evidence from one or more concrete executions or samples without a theorem covering all relevant states or the continuous domain.

**Small-step semantics.** An operational semantics in which each rule performs one local transition, making interleavings, faults, and protocol states explicit.

**Soundness.** The property that every fact reported as established is true of all represented concrete behaviors under the stated assumptions. A sound analysis may conservatively reject safe programs.

**Source map.** A mapping from generated IR nodes, commands, and diagnostics back to source syntax and macro-expansion provenance.

**SSA state token.** A single-assignment value consumed and produced by state-changing IR operations, making effect order and data dependencies explicit.

**Staged programming.** Execution of one program phase to construct code or data for a later phase. The phase boundary should remove ambient authority and retain only inert, validated artifacts.

**Stock monotonicity.** The ideal subtractive-process invariant $S_{i+1}\subseteq S_i$. It excludes material addition but does not by itself establish correct removal.

**Swept volume.** The union of all poses of a solid along a trajectory. Different claims require the cutting tool sweep or the complete tool-and-holder assembly sweep.

**Target surface.** The desired final boundary or protected part geometry against which gouge, allowance, and residual-material claims are stated.

**Temporal logic.** A logic with operators over traces, such as always $\Box$, eventually $\Diamond$, and next, used for controller safety and liveness properties.

**Time-optimal path parameterization.** Selection of progress $s(t)$ along a fixed geometric path to minimize time while satisfying velocity, acceleration, torque, jerk, tracking, and process constraints.

**Total correctness.** Partial correctness plus termination or liveness under stated assumptions.

**Trace.** A finite or infinite sequence of states and observable events representing one system execution.

**Trace refinement.** Inclusion of concrete traces, after abstraction, in the set allowed by an abstract program.

**Trajectory.** A time-indexed pose or configuration function. A path becomes a trajectory only after time parameterization.

**Translation validation.** Independent checking that one actual pass output correctly refines its actual input, instead of proving the transformer correct for all inputs.

**Trusted computing base.** The code, semantics, numeric primitives, key material, and assumptions whose correctness must be trusted for the assurance argument to hold.

**Typestate.** Static representation of protocol state in types so only operations valid in the current state can be expressed.

**Uncertainty set.** A set of possible values for a physical or numerical quantity, such as a transform interval, tool-radius interval, or following-error bound.

**Validation.** Checking an artifact against a relation, policy, or specification. Validation should state exactly what was checked and by what method.

**Verification.** Establishment of a formal or mathematically justified claim. In this book the term is reserved for claims with explicit propositions, assumptions, and evidence rather than visual inspection alone.

**Weakest precondition.** The least restrictive precondition sufficient to ensure a desired postcondition after execution of a command.

**Witness.** Producer-supplied data demonstrating a construction or optimization choice, such as a path decomposition, correspondence, abstract invariant, separating plane, or schedule assignment.

**Work coordinate system.** A frame relating part-program coordinates to machine coordinates. Its identity and uncertainty are runtime-critical inputs to travel and collision claims.

# Guided Reading and Project Tracks

The chapters are intentionally cross-disciplinary. This appendix gives compact routes through the material for different implementation goals.

## G.1 Compiler and language track

Read Chapters 1, 2, 7-15, 18-20, 27, 28, 36, 37, and 40. Implement the inert plan AST, the multi-level IR ladder, pass contracts, content-addressed artifacts, and parse-back validation before adding advanced planning strategies. The central external readings are multi-stage programming [R37], MLIR [R16], SSA [R15], CompCert [R17], translation validation [R18, R19], and NIST's canonical machining interface [R1, R2].

## G.2 Static-analysis and formal-methods track

Read Chapters 3, 5, 6, 10, 11, 14, and 22-30. Begin with Hoare logic and weakest preconditions [R4, R5], structural operational semantics [R6], abstract interpretation [R7], refinement mappings [R9], temporal logic [R8, R34], and proof-carrying code [R20, R21]. Parameterized effects [R12-R14] and Dijkstra monads [R39] provide a route from API typing to machine-checkable contracts.

## G.3 Robust geometry and verification track

Read Chapters 3, 4, 9, 16, 24-28, 33, and 37. Build exact or adaptive topology predicates before accelerating constructions [R22]. Use interval enclosures [R23, R24], configuration-space reasoning [R25], conservative swept-volume techniques [R26], and representations such as triple dexels [R27, R28]. Keep target protection, fixture clearance, and guaranteed removal as separate propositions.

## G.4 Controller and runtime track

Read Chapters 1, 5, 18-20, 22, 23, 29, 30, 37, and 39. Implement a closed command grammar, explicit modal interpreter, protocol state machine, state epochs, hash-bound upload/start operations, and abort recovery. NIST's interpreters and canonical commands provide the machining semantics foundation [R1, R2]. TLA-style specification [R8, R34], hybrid systems [R35], and runtime assurance [R36] cover the protocol and physical-monitoring boundary.

## G.5 Planning and optimization track

Read Chapters 2-4, 6, 9, 16, 17, and Part V. Treat every optimizer as an untrusted producer of candidates inside a separately checked feasible set. Relevant foundations include configuration spaces [R25], fast marching and geodesics [R29, R30], precedence-constrained routing [R31], and constrained feed scheduling [R32, R33].

## G.6 Manufacturing-information track

Read Chapters 1, 2, 7, 8, 12, 13, 16, 18, 27, and 37. Compare the semantic-waist architecture with STEP-NC's feature and working-step model [R3, R42, R43]. Conformance testing is as important as schema design; Barnard Feeney and Frechette provide a manufacturing-specific testing perspective [R40].

## G.7 A twelve-week implementation course

| Week | Reading | Laboratory |
|---:|---|---|
| 1 | Chapters 1-2 | Define one pocket intent and three acceptable implementations. |
| 2 | Chapters 3-4 | Implement dimensional types and a checked frame graph. |
| 3 | Chapters 5-6 | Write denotational and small-step semantics for five canonical commands. |
| 4 | Chapters 7-9 | Build an isolated macro-to-AST boundary and path algebra. |
| 5 | Chapters 10-13 | Add effects, machine-state tokens, provenance, and extensible operation schemas. |
| 6 | Chapters 14-15 | Implement pass manifests and one translation validator. |
| 7 | Chapters 16-20 | Lower a pocket to controller IR and validate emitted bytes by parse-back. |
| 8 | Chapters 22-23 | Implement weakest-precondition rules and an interval/modal abstract interpreter. |
| 9 | Chapters 24-26 | Add robust predicates, interval transforms, and typed error budgets. |
| 10 | Chapters 27-30 | Build the certificate DAG, protocol model, and runtime preflight handshake. |
| 11 | Chapters 31-35 | Add precedence-aware sequencing and a checked free-space linker. |
| 12 | Chapters 36-40 | Integrate the headless compiler, checker process, CLI, and Z1 dry-run workflow. |

## G.8 Research directions

The architecture leaves several substantive research problems open:

1. A compositional specification language for machining features whose denotation covers tolerance zones, surface texture, process constraints, and intermediate stock support.
2. Efficient conservative swept-volume bounds for arbitrary tool assemblies and spline trajectories under uncertain transforms.
3. Proof-producing adaptive stock representations that combine dexel speed with local volumetric refinement.
4. Translation validators for geometry algorithms that emit compact correspondence or separation witnesses.
5. Robust scheduling with stock-dependent transition costs and structural-support constraints.
6. Controller semantics learned from traces but converted into explicit, reviewable, versioned profiles.
7. Small proof formats for geometric certificates; compact proof representation and checking remain important engineering concerns [R41].
8. Runtime monitors that combine discrete protocol assurance with bounded stopping dynamics and sensor uncertainty.

\backmatter

# References {-}

The bracketed identifiers in the text refer to the entries below. DOI links name the version of record when available; institutional pages are used for standards and technical reports.

**[R1]** Thomas R. Kramer, Frederick M. Proctor, and Elena R. Messina. *The NIST RS274/NGC Interpreter, Version 3*. NISTIR 6556, National Institute of Standards and Technology, 2000. <https://www.nist.gov/publications/nist-rs274ngc-interpreter-version-3>.

**[R2]** Frederick M. Proctor, Thomas R. Kramer, and John L. Michaloski. *Canonical Machining Commands*. NISTIR 5970, National Institute of Standards and Technology, 1997. <https://doi.org/10.6028/NIST.IR.5970>.

**[R3]** ISO 14649-1. *Industrial Automation Systems and Integration -- Physical Device Control -- Data Model for Computerized Numerical Controllers -- Part 1: Overview and Fundamental Principles*. International Organization for Standardization.

**[R4]** C. A. R. Hoare. “An Axiomatic Basis for Computer Programming.” *Communications of the ACM* 12, no. 10 (1969): 576-580, 583. <https://doi.org/10.1145/363235.363259>.

**[R5]** Edsger W. Dijkstra. “Guarded Commands, Nondeterminacy and Formal Derivation of Programs.” *Communications of the ACM* 18, no. 8 (1975): 453-457. <https://doi.org/10.1145/360933.360975>.

**[R6]** Gordon D. Plotkin. “A Structural Approach to Operational Semantics.” Originally DAIMI FN-19, Aarhus University, 1981; reprinted in *Journal of Logic and Algebraic Programming* 60-61 (2004): 17-139. <https://doi.org/10.1016/j.jlap.2004.03.009>.

**[R7]** Patrick Cousot and Radhia Cousot. “Abstract Interpretation: A Unified Lattice Model for Static Analysis of Programs by Construction or Approximation of Fixpoints.” In *Proceedings of POPL 1977*, 238-252. <https://doi.org/10.1145/512950.512973>.

**[R8]** Leslie Lamport. “The Temporal Logic of Actions.” *ACM Transactions on Programming Languages and Systems* 16, no. 3 (1994): 872-923. <https://doi.org/10.1145/177492.177726>.

**[R9]** Martín Abadi and Leslie Lamport. “The Existence of Refinement Mappings.” *Theoretical Computer Science* 82, no. 2 (1991): 253-284. <https://doi.org/10.1016/0304-3975(91)90224-P>.

**[R10]** Eugenio Moggi. “Notions of Computation and Monads.” *Information and Computation* 93, no. 1 (1991): 55-92. <https://doi.org/10.1016/0890-5401(91)90052-4>.

**[R11]** Philip Wadler. “The Essence of Functional Programming.” In *Proceedings of POPL 1992*, 1-14. <https://doi.org/10.1145/143165.143169>.

**[R12]** Robert E. Strom and Shaula Yemini. “Typestate: A Programming Language Concept for Enhancing Software Reliability.” *IEEE Transactions on Software Engineering* SE-12, no. 1 (1986): 157-171. <https://doi.org/10.1109/TSE.1986.6312929>.

**[R13]** Robert Atkey. “Parameterised Notions of Computation.” *Journal of Functional Programming* 19, nos. 3-4 (2009): 335-376. <https://doi.org/10.1017/S095679680900728X>.

**[R14]** John M. Lucassen and David K. Gifford. “Polymorphic Effect Systems.” In *Proceedings of POPL 1988*, 47-57. <https://doi.org/10.1145/73560.73564>.

**[R15]** Ron Cytron, Jeanne Ferrante, Barry K. Rosen, Mark N. Wegman, and F. Kenneth Zadeck. “Efficiently Computing Static Single Assignment Form and the Control Dependence Graph.” *ACM Transactions on Programming Languages and Systems* 13, no. 4 (1991): 451-490. <https://doi.org/10.1145/115372.115320>.

**[R16]** Chris Lattner, Mehdi Amini, Uday Bondhugula, Albert Cohen, Andy Davis, Jacques Pienaar, River Riddle, Tatiana Shpeisman, Nicolas Vasilache, and Oleksandr Zinenko. “MLIR: Scaling Compiler Infrastructure for Domain Specific Computation.” In *Proceedings of CGO 2021*, 2-14. <https://doi.org/10.1109/CGO51591.2021.9370308>.

**[R17]** Xavier Leroy. “Formal Verification of a Realistic Compiler.” *Communications of the ACM* 52, no. 7 (2009): 107-115. <https://doi.org/10.1145/1538788.1538814>.

**[R18]** Amir Pnueli, Michael Siegel, and Eli Singerman. “Translation Validation.” In *Tools and Algorithms for the Construction and Analysis of Systems, TACAS 1998*, 151-166. <https://doi.org/10.1007/BFb0054170>.

**[R19]** Nuno P. Lopes, Juneyoung Lee, Chung-Kil Hur, Zhengyang Liu, and John Regehr. “Alive2: Bounded Translation Validation for LLVM.” In *Proceedings of PLDI 2021*. <https://doi.org/10.1145/3453483.3454030>.

**[R20]** George C. Necula. “Proof-Carrying Code.” In *Proceedings of POPL 1997*, 106-119. <https://doi.org/10.1145/263699.263712>.

**[R21]** Andrew W. Appel. “Foundational Proof-Carrying Code.” In *Proceedings of the 16th Annual IEEE Symposium on Logic in Computer Science*, 247-256, 2001. <https://doi.org/10.1109/LICS.2001.932501>.

**[R22]** Jonathan Richard Shewchuk. “Adaptive Precision Floating-Point Arithmetic and Fast Robust Geometric Predicates.” *Discrete & Computational Geometry* 18 (1997): 305-363. <https://doi.org/10.1007/PL00009321>.

**[R23]** IEEE. *IEEE Standard for Interval Arithmetic (Simplified)*. IEEE Std 1788.1-2017. <https://standards.ieee.org/ieee/1788.1/6074/>.

**[R24]** Ramon E. Moore, R. Baker Kearfott, and Michael J. Cloud. *Introduction to Interval Analysis*. SIAM, 2009. <https://doi.org/10.1137/1.9780898717716>.

**[R25]** Tomás Lozano-Pérez. “Spatial Planning: A Configuration Space Approach.” *IEEE Transactions on Computers* C-32, no. 2 (1983): 108-120. <https://doi.org/10.1109/TC.1983.1676196>.

**[R26]** Silvia Sellán, Noam Aigerman, and Alec Jacobson. “Swept Volumes via Spacetime Numerical Continuation.” *ACM Transactions on Graphics* 40, no. 4 (2021). <https://doi.org/10.1145/3450626.3459780>.

**[R27]** Masatomo Inui, Takashi Sakurai, and Nobuyuki Umezu. “Data Conversion Technology between Triple Dexel Model and Polygonal Model.” *Journal of the Japan Society for Precision Engineering* 76, no. 2 (2010): 226-231. <https://doi.org/10.2493/jjspe.76.226>.

**[R28]** Weihan Zhang and Ming-Chuan Leu. “Surface Reconstruction Using Dexel Data from Three Sets of Orthogonal Rays.” *Journal of Computing and Information Science in Engineering* 9, no. 1 (2009): 011008. <https://doi.org/10.1115/1.3086034>.

**[R29]** J. A. Sethian. “A Fast Marching Level Set Method for Monotonically Advancing Fronts.” *Proceedings of the National Academy of Sciences* 93, no. 4 (1996): 1591-1595. <https://doi.org/10.1073/pnas.93.4.1591>.

**[R30]** Ron Kimmel and J. A. Sethian. “Computing Geodesic Paths on Manifolds.” *Proceedings of the National Academy of Sciences* 95, no. 15 (1998): 8431-8435. <https://doi.org/10.1073/pnas.95.15.8431>.

**[R31]** Ilker Kucukoglu, Tulin Gunduz, Fatma Balkancioglu, Emine Chousein Topal, and Oznur Sayim. “Application of Precedence Constrained Travelling Salesman Problem Model for Tool Path Optimization in CNC Milling Machines.” *An International Journal of Optimization and Control: Theories & Applications* 9, no. 3 (2019): 59-68. <https://doi.org/10.11121/ijocta.01.2019.00662>.

**[R32]** Qiang Zhang, Shurong Li, and Jianxin Guo. “Minimum Time Trajectory Optimization of CNC Machining with Tracking Error Constraints.” *Abstract and Applied Analysis* 2014, Article 835098. <https://doi.org/10.1155/2014/835098>.

**[R33]** Hung Pham and Quang-Cuong Pham. “A New Approach to Time-Optimal Path Parameterization Based on Reachability Analysis.” *IEEE Transactions on Robotics* 34, no. 3 (2018): 645-659. <https://doi.org/10.1109/TRO.2018.2819195>.

**[R34]** Leslie Lamport. *Specifying Systems: The TLA+ Language and Tools for Hardware and Software Engineers*. Addison-Wesley, 2002. <https://lamport.azurewebsites.net/tla/book.html>.

**[R35]** Rajeev Alur, Costas Courcoubetis, Thomas A. Henzinger, and Pei-Hsin Ho. “The Algorithmic Analysis of Hybrid Systems.” *Theoretical Computer Science* 138, no. 1 (1995): 3-34. <https://doi.org/10.1016/0304-3975(94)00202-T>.

**[R36]** J. Tanner Slagel, Lauren M. White, Aaron Dutle, César A. Muñoz, and Nicolas Crespo. “A Formal Verification Framework for Runtime Assurance.” In *NASA Formal Methods 2024*, 322-328. <https://doi.org/10.1007/978-3-031-60698-4_19>.

**[R37]** Walid Taha and Tim Sheard. “MetaML and Multi-Stage Programming with Explicit Annotations.” *Theoretical Computer Science* 248, nos. 1-2 (2000): 211-242. <https://doi.org/10.1016/S0304-3975(00)00053-0>.

**[R38]** John C. Reynolds. “Separation Logic: A Logic for Shared Mutable Data Structures.” In *Proceedings of the 17th Annual IEEE Symposium on Logic in Computer Science*, 55-74, 2002. <https://doi.org/10.1109/LICS.2002.1029817>.

**[R39]** Kenji Maillard, Danel Ahman, Robert Atkey, Guido Martínez, Cătălin Hriţcu, Exequiel Rivas, and Éric Tanter. “Dijkstra Monads for All.” *Proceedings of the ACM on Programming Languages* 3, ICFP, Article 104 (2019). <https://doi.org/10.1145/3341708>.

**[R40]** Allison Barnard Feeney and Simon P. Frechette. “Testing STEP-NC Implementations.” In *Proceedings of World Automation Congress 2002*. National Institute of Standards and Technology. <https://www.nist.gov/publications/testing-step-nc-implementations>.

**[R41]** George C. Necula and Peter Lee. “Efficient Representation and Validation of Proofs.” In *Proceedings of the 13th Annual IEEE Symposium on Logic in Computer Science*, 93-104, 1998. <https://doi.org/10.1109/LICS.1998.705646>.

**[R42]** Thomas R. Kramer and Frederick M. Proctor. *Feature-Based Control of a Machining Center*. NISTIR 5926, National Institute of Standards and Technology, 1996. <https://www.nist.gov/publications/feature-based-control-machining-center>.

**[R43]** John L. Michaloski, Thomas R. Kramer, Frederick M. Proctor, Xun Xu, Sid Venkatesh, and David Odendahl. “STEPNC++ -- An Effective Tool for Feature-Based CAM/CNC.” In *Advanced Design and Manufacturing Based on STEP*. Springer, 2009. <https://www.nist.gov/publications/stepnc-effective-tool-feature-based-camcnc>.

# Source Snapshot and Reproducibility Notes {-}

The implementation-specific case study is based on the supplied `dropcut-studio.zip` snapshot and the public repository branch `task/cnc-control-dropcut` near commit `e82bed1e5a00f38f4441e6ea13e1265edc775928`, inspected in August 2026. The case study is not a statement about later revisions. Where firmware behavior is discussed, the reviewed source evidence used the Makera stock Carvera firmware repository at commit `1683b6fb5c7ec1d341c476c6fdb2a22f7a26220e` and explicitly distinguished stock behavior from community-firmware changes.

The textbook's diagrams are generated from Graphviz or Matplotlib source stored with the Markdown edition. The PDF is rendered from the same Markdown source. Equations, algorithms, and TypeScript interfaces are pedagogical specifications; they must be implemented, tested, and connected to machine-specific assumptions before they can support a production certificate.

EOF

python - <<'PY'
from pathlib import Path
p=Path('/mnt/data/z1_textbook_work/book/Certificate_Carrying_CAM_Compilers.md')
s=p.read_text()
print('lines',s.count('\n')+1,'words',len(s.split()),'bytes',p.stat().st_size)
PY
```

<details><summary>💭 Thinking</summary>

**Appended glossary and reading paths**

</details>

```json
{"search_query":[{"q":"Robert Atkey Parameterised Notions of Computation DOI Journal Functional Programming"},{"q":"MetaML multi-stage programming explicit annotations DOI"},{"q":"Polymorphic effect systems Lucassen Gifford DOI"},{"q":"SSA control dependence graph DOI Cytron 1991"}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Searched 13 websites**

</details>

```unknown
bash -lc cat /home/oai/skills/pdfs/SKILL.md
```

<details><summary>💭 Thinking</summary>

**Read PDF skill instructions**

</details>

```unknown
bash -lc set -e
cd /mnt/data/z1_textbook_work/book
printf 'pandoc: '; pandoc --version | head -n 1
printf 'xelatex: '; xelatex --version | head -n 1
python - <<'PY'
from pathlib import Path
import re
p=Path('Certificate_Carrying_CAM_Compilers.md')
s=p.read_text()
# Fences
fences=[(i+1,l) for i,l in enumerate(s.splitlines()) if re.match(r'^```',l)]
print('code fences:',len(fences),'balanced',len(fences)%2==0)
# tcolor boxes
for env in ['designrule','warningbox','workedexample']:
    a=s.count(r'\begin{'+env+'}')
    b=s.count(r'\end{'+env+'}')
    print(env,a,b,'ok',a==b)
# Citation identifiers
used=set()
for m in re.finditer(r'\[([^\]]*R\d+[^\]]*)\]',s):
    used.update(map(int,re.findall(r'R(\d+)',m.group(1))))
defined=set(map(int,re.findall(r'^\*\*\[R(\d+)\]\*\*',s,re.M)))
print('references used',len(used),min(used),max(used))
print('references defined',len(defined),min(defined),max(defined))
print('missing defs',sorted(used-defined))
print('unused defs',sorted(defined-used))
# Figures
figs=re.findall(r'!\[[^]]*\]\(([^)]+)\)',s)
missing=[f for f in figs if not Path(f).exists()]
print('figures',len(figs),'missing',missing)
# headings with duplicate exact titles
from collections import Counter
hs=re.findall(r'^#{1,3} (.+)$',s,re.M)
dup=[(h,n) for h,n in Counter(hs).items() if n>1 and not h.startswith('Exercises')]
print('headings',len(hs),'duplicates sample',dup[:20])
PY
```

<details><summary>💭 Thinking</summary>

**Built and validated textbook PDF with font and figure adjustments**

</details>

```unknown
bash -lc rm -rf /mnt/data/z1_textbook_work/renders && mkdir -p /mnt/data/z1_textbook_work/renders
python /home/oai/skills/pdfs/scripts/render_pdf.py \
  /mnt/data/z1_textbook_work/book/Certificate_Carrying_CAM_Compilers.pdf \
  --out_dir /mnt/data/z1_textbook_work/renders \
  --dpi 150
printf '\nRendered pages: '
find /mnt/data/z1_textbook_work/renders -maxdepth 1 -name '*.png' | wc -l
ls -lh /mnt/data/z1_textbook_work/renders | sed -n '1,8p'
```

<details><summary>💭 Thinking</summary>

**Rebuilt and validated the textbook PDF with corrected headings and references**

</details>

```unknown
bash -lc set -e
OUT=/mnt/data/z1_textbook_deliverables
SRC=/mnt/data/z1_textbook_work/book
rm -rf "$OUT"
mkdir -p "$OUT"
cp "$SRC/Certificate_Carrying_CAM_Compilers.md" "$OUT/Certificate_Carrying_CAM_Compilers.md"
cp "$SRC/Certificate_Carrying_CAM_Compilers.pdf" "$OUT/Certificate_Carrying_CAM_Compilers.pdf"

BUNDLE=/mnt/data/z1_textbook_work/source_bundle/Certificate_Carrying_CAM_Compilers
rm -rf /mnt/data/z1_textbook_work/source_bundle
mkdir -p "$BUNDLE/figures"
cp "$SRC/Certificate_Carrying_CAM_Compilers.md" "$BUNDLE/"
cp "$SRC"/figures/*.png "$BUNDLE/figures/"
cp "$SRC"/figures/*.dot "$BUNDLE/figures/"
cp "$SRC/make_geometry_figure.py" "$BUNDLE/"
cat > "$BUNDLE/README.md" <<'EOF'
# Certificate-Carrying CAM Compilers - source bundle

This bundle contains the Markdown source and generated figures for the textbook.

## Render to PDF

Requirements: Pandoc, XeLaTeX, Linux Libertine O, Linux Biolinum O, DejaVu Sans Mono, and the LaTeX packages named in the Markdown YAML header.

Run from this directory:

```bash
pandoc Certificate_Carrying_CAM_Compilers.md \
  --from=markdown+raw_tex \
  --pdf-engine=xelatex \
  --top-level-division=chapter \
  --highlight-style=tango \
  --resource-path=. \
  -o Certificate_Carrying_CAM_Compilers.pdf
```

The `.dot` files are the Graphviz sources for most architecture diagrams. `make_geometry_figure.py` generates the inner/outer approximation figure.
EOF
cd /mnt/data/z1_textbook_work/source_bundle
zip -X -r "$OUT/Certificate_Carrying_CAM_Compilers_Source.zip" Certificate_Carrying_CAM_Compilers >/tmp/z1_zip.log
zip -T "$OUT/Certificate_Carrying_CAM_Compilers_Source.zip"
sha256sum "$OUT"/* > "$OUT/SHA256SUMS.txt"
ls -lh "$OUT"
cat "$OUT/SHA256SUMS.txt"
```

<details><summary>💭 Thinking</summary>

**Packaged final textbook deliverables and source bundle**

</details>

The manuscript is complete with 34 chapters, exercises, solutions, proof patterns, checklist, and bibliography. Final PDF verification and appendix reflow produced a clean 159-page edition.

# Certificate-Carrying CAM Compilers

Completed as a full textbook:

- **213 pages**
- **40 chapters in six parts**
- **Seven appendices**
- Formal semantics, refinement, IR design, compiler-pass contracts, translation validation, robust computational geometry, abstract interpretation, proof-carrying code, certificates, temporal controller models, runtime assurance, and operations research
- TypeScript-oriented implementation patterns and checker algorithms
- End-to-end certified-pocket example
- Detailed Dropcut Studio / Makera Z1 case study
- Exercises for every chapter with selected solutions
- Glossary, guided reading tracks, twelve-week course plan, research directions, and 43 primary references

Files:

- [Download the Markdown textbook](sandbox:/mnt/data/z1_textbook_deliverables/Certificate_Carrying_CAM_Compilers.md)
- [Download the 213-page PDF textbook](sandbox:/mnt/data/z1_textbook_deliverables/Certificate_Carrying_CAM_Compilers.pdf)
- [Download the complete source bundle](sandbox:/mnt/data/z1_textbook_deliverables/Certificate_Carrying_CAM_Compilers_Source.zip) — Markdown, PNG figures, Graphviz sources, figure-generation script, and build instructions
- [Download SHA-256 checksums](sandbox:/mnt/data/z1_textbook_deliverables/SHA256SUMS.txt)

The final PDF was rendered and visually inspected across the front matter, tables of contents, chapter pages, equations, code listings, diagrams, long tables, case study, solutions, glossary, and references.


---

> Use the material you gathered, but rewrite and restructure it so it actually turns into a real pedagogical textbook.
>
> Let’s try again, more structured and pedagogical: 4 big chapters, and after writing the first draft, go back and make sure each definition and term worth defining or introducing is properly motivated and defined and then applied in a few examples. Pretend you are a student reading the text and trying to make sense of it, and then rewrite it.
>
> Make sure to introduce concepts by motivation, definition, then concrete worked examples, then exercises, and potentially counterexample. Use full prose paragraphs and lists and pseudocode and maths and api signatures and diagrams. Use callouts for expanding on fundamentals or side topics.

<details><summary>💭 Thinking</summary>

**Planning the rewrite**

I’m going to inspect the available source material, identify the four major chapters, and reshape them into a coherent, pedagogical textbook. I’ll prepare both Markdown and PDF versions if the materials support that.

**Planned the rewrite**

</details>

```unknown
bash -lc cat /home/oai/skills/pdfs/SKILL.md && printf '\n--- files ---\n' && find /mnt/data -maxdepth 3 -type f | sed -n '1,240p'
```

I’m rebuilding the book around four coherent learning arcs, with each concept moving from motivation and definition through worked examples, counterexamples, implementation patterns, and exercises.

<details><summary>💭 Thinking</summary>

**Created a four-chapter pedagogical textbook PDF after inspecting source files and design instructions**

</details>

```unknown
bash -lc cd /mnt/data/z1_pedagogical_textbook_work/dropcut-studio
for f in \
 packages/units/src/index.ts \
 packages/math/src/frames.ts \
 packages/ir/src/path.ts \
 packages/ir/src/commands.ts \
 packages/ir/src/program.ts \
 packages/ir/src/provenance.ts \
 packages/compiler/src/index.ts \
 packages/compiler/src/validate.ts \
 packages/compiler/src/lower.ts \
 packages/compiler/src/recertify.ts; do
  echo "===== $f ====="
  sed -n '1,360p' "$f"
  echo
done
```

<details><summary>💭 Thinking</summary>

**Inspected compiler and geometry source files**

**Structuring the textbook**

I’m organizing the material into four substantial chapters, keeping the examples, formal definitions, compiler pipeline, geometry, planning, optimization, and verification themes connected through a coherent pedagogical progression.

**Structured the textbook**

**Designing the chapters**

I’m keeping exactly four numbered chapters, while using appendices for notation, a glossary, references, and selected solutions. I’ll connect formal semantics, geometry, planning, verification, and the end-to-end case study.

**Designed the chapters**

</details>

```unknown
bash -lc cd /mnt/data/z1_pedagogical_textbook_work/dropcut-studio
for f in \
 packages/ir/src/path.ts \
 packages/ir/src/commands.ts \
 packages/ir/src/program.ts \
 packages/ir/src/provenance.ts \
 packages/planner/src/types.ts \
 packages/planner/src/run.ts \
 packages/planner/src/linker.ts \
 packages/planner/src/refine.ts \
 packages/planner/src/entry.ts; do
  echo "===== $f ====="
  nl -ba "$f" | sed -n '1,420p'
  echo
done
```

The structure is now fixed: semantics, language/IR, verification/certificates, then planning, optimization, and controller execution. One pocket-machining example and the Z1 implementation will connect the chapters.

<details><summary>💭 Thinking</summary>

**Inspected project sources and drafted robotics book with diagrams**

**Building the manuscript**

I’m shaping the text as a polished textbook with four core chapters, practical callouts, diagrams, exercises, and appendices that support notation, terminology, references, and review.

**Built the manuscript**

</details>

```unknown
bash -lc cat > /mnt/data/z1_pedagogical_textbook_work/book/draft_v1.md <<'EOF'
---
title: "From Intent to Motion"
subtitle: "A Pedagogical Textbook on CAM Compilers, Geometry, Semantics, and Certificates"
author: "Dropcut / Makera Z1 project edition"
date: "August 2026"
lang: en-US
documentclass: book
classoption:
  - 11pt
  - oneside
  - openany
papersize: letter
geometry:
  - top=0.85in
  - bottom=0.9in
  - inner=0.95in
  - outer=0.85in
mainfont: "Linux Libertine O"
sansfont: "Linux Biolinum O"
monofont: "DejaVu Sans Mono"
fontsize: 11pt
linestretch: 1.08
colorlinks: true
linkcolor: "243447"
urlcolor: "2C658D"
toc: true
toc-depth: 2
numbersections: true
lof: true
highlight-style: tango
header-includes:
  - |
    \usepackage{amsmath,amssymb,mathtools}
    \usepackage{booktabs,longtable,array}
    \usepackage{microtype}
    \usepackage{fancyhdr}
    \usepackage{enumitem}
    \usepackage{caption}
    \usepackage{float}
    \usepackage{xcolor}
    \definecolor{Ink}{HTML}{243447}
    \definecolor{Accent}{HTML}{2C658D}
    \definecolor{Warm}{HTML}{9A6B1F}
    \definecolor{Pale}{HTML}{F4F7FA}
    \pagestyle{fancy}
    \fancyhf{}
    \fancyhead[LE,RO]{\small\thepage}
    \fancyhead[LO]{\small\nouppercase{\rightmark}}
    \fancyhead[RE]{\small\nouppercase{\leftmark}}
    \setlength{\headheight}{14pt}
    \setlist{nosep,leftmargin=*}
    \captionsetup{font=small,labelfont=bf}
    \setcounter{secnumdepth}{3}
    \setcounter{tocdepth}{2}
---

\frontmatter

# Preface {-}

A computer-aided manufacturing system can look deceptively simple from a distance. The user describes a pocket, the software draws some lines, and a postprocessor writes G-code. That description omits nearly everything that makes the problem intellectually interesting and physically dangerous. A real system must connect a human intention to an actual machine whose axes have limits, whose controller retains modal state, whose tool has a three-dimensional shape, whose setup is uncertain, and whose mistakes can break a cutter or damage a workpiece.

This book develops a way to reason about that entire chain. Its central proposal is that a CAM application should be built as a **refinement compiler for a cyber-physical process**. The source language describes acceptable manufacturing outcomes. Intermediate representations progressively choose geometry, order, timing, machine capabilities, and controller syntax. Every important transformation states what it preserves, what it approximates, and what evidence supports that statement. The final product is not merely a text file. It is an exact job bundle accompanied by explicit assumptions and checkable claims.

The running case study is a JavaScript-based CAM system for a Makera Z1-class desktop mill. The supplied Dropcut Studio implementation already contains many of the right ingredients: unit brands, frame-tagged points, path objects, high-level operations, cutter-location fields, contour extraction, planning strategies, a canonical command layer, machine profiles, G-code backends, simulation, and a controller client. It also contains instructive gaps. Some are ordinary software defects. Others are deeper category errors: treating a sampled simulation as a proof, treating approximate coordinates as topological identity, or treating a command prefix as the meaning of a compound payload. These examples let us study theory without detaching it from code.

The book has exactly four large chapters.

1. **Meaning before syntax** develops the physical and semantic model. It explains units, frames, paths, trajectories, swept volumes, denotational meaning, operational transitions, contracts, and temporal behavior.
2. **Languages, IRs, and passes** turns that model into a compiler architecture. It introduces staged JavaScript, multi-level IRs, categorical path composition, effectful commands, typestate, SSA-style state tokens, pass contracts, provenance, and translation validation.
3. **Geometry, planning, and optimization** develops the computational side of CAM: drop-cutter geometry, cutter-location fields, contours, offsets, entries, linking, stock models, robust numerics, scheduling, and feed planning.
4. **Certificates and runtime assurance** explains assertions, invariants, abstract interpretation, geometric evidence, proof-carrying artifacts, protocol state machines, hash-bound authorization, and a practical migration path for the Z1 controller and Dropcut compiler.

The goal is not to make every reader a specialist in formal semantics, computational geometry, operations research, and machine control at once. The goal is to build a connected mental model. Each technical idea is introduced because a concrete machining problem demands it. Definitions are followed by worked examples. Counterexamples show why tempting shortcuts fail. Exercises ask the reader to reconstruct the reasoning rather than merely repeat terminology.

## How to use this book {-}

A reader with software experience and basic algebra can begin at Chapter 1. Calculus and linear algebra are introduced only where needed. Familiarity with CNC terminology helps, but the relevant concepts are defined. Readers who already know CAM may move quickly through the physical preliminaries, but they should not skip the distinction among a geometric path, a timed trajectory, and a material-removal process; much of the later architecture depends on it.

Code examples use TypeScript-like notation because that matches the project. They are specifications first and implementation sketches second. Branded scalar types and phantom frame parameters are useful, but TypeScript erases them at runtime. Every static guarantee must therefore be paired with validation at serialization, deserialization, plugin, and execution boundaries.

Mathematical notation is used when it removes ambiguity. A formula is always explained in prose. When a model is idealized, the text states what has been omitted. A proof about a nominal mesh is not automatically a proof about the actual clamped part. A guarantee about controller bytes is not automatically a guarantee about the mechanics. The difference between a theorem and an assumption is one of the book's recurring themes.

## The running job {-}

We will repeatedly return to one small job. A rectangular stock blank measures 60 mm by 40 mm by 8 mm. The work coordinate origin is at the lower-left corner of the stock top. We want to machine a 30 mm by 20 mm pocket centered in the blank, 4 mm deep, leaving a finished wall and floor tolerance of 0.05 mm. A flat end mill roughs the pocket; a second pass finishes the boundary and floor. Two clamps lie near the upper and lower stock edges.

![The running pocket example.](figures/running_pocket.png){width=88%}

This job is deliberately ordinary. It still forces us to answer difficult questions:

- Does “make a pocket” denote one path or a set of acceptable outcomes?
- In which coordinate frame are the dimensions expressed?
- What tool geometry is assumed?
- How are entry and linking moves distinguished from cutting moves?
- What happens if the controller is still in incremental mode?
- How does the compiler know that a low traverse does not cross remaining stock?
- What does a claim such as “no gouge” actually quantify over?
- Which facts can be checked before execution, and which require live machine state?

By the end of Chapter 4, the job will have become a complete chain of artifacts, claims, and runtime checks.

## Conventions {-}

Lengths are expressed internally in millimetres. A point is written $p=(x,y,z)^F$ when the superscript names its coordinate frame. The symbol $S$ denotes current stock, $P$ the target or protected part, $O$ fixtures and other obstacles, and $T$ a tool or tool assembly. A geometric path is usually written $\gamma$, a timed trajectory $x(t)$, and a machine or process state $\sigma$.

A statement labeled **Definition** introduces terminology used later. A **Worked example** carries out a calculation or design step. A **Counterexample** demonstrates a failure of an appealing but invalid rule. A **Fundamental idea** callout expands a prerequisite that readers from another discipline may not know. A **Design consequence** turns theory into an engineering rule.

\mainmatter

# Meaning Before Syntax

## Chapter orientation

A novice CAM implementation often begins with a function named `generateGCode`. That starting point feels productive because G-code is visible and the machine accepts it. It is also a trap. The text `G1 X30 Y20 F400` has no safe, context-free meaning. Its interpretation depends on units, distance mode, active plane, work offset, feed mode, tool, machine state, firmware dialect, and prior blocks. More importantly, a list of controller blocks does not state what workpiece result the user requested.

This chapter therefore begins one level above code and one level below user interface. We will define what exists physically, what a manufacturing operation means, and how execution changes state. Only after those foundations are clear will later chapters design a language and compiler.

### Learning objectives

After this chapter, you should be able to:

- distinguish manufacturing intent from one implementation;
- model units, frames, tools, stock, target, fixtures, and controller state explicitly;
- distinguish a path from a trajectory and a trajectory from a material-removal action;
- explain denotational, operational, axiomatic, and temporal semantics;
- state safety properties as predicates over continuous executions;
- derive a simple preflight condition using weakest preconditions;
- identify assumptions that no compiler can establish from source code alone.

![The semantic stack from intent to physical execution.](figures/semantic_stack.png){width=72%}

## 1.1 Why a pocket is not a polyline

### Motivation

Suppose a user asks for the running pocket. One planner generates nested rectangular offsets. Another uses parallel raster lines. A third uses adaptive clearing and a final contour. These paths look different, take different times, and load the tool differently, yet all may produce an acceptable pocket.

If the source meaning were “execute this exact point list,” only one of them could be correct. That would make optimization and strategy choice impossible by definition. The user's intention is instead a constraint on the resulting material.

### Definition: manufacturing intent

A **manufacturing intent** is a specification of acceptable outcomes and process constraints, not a commitment to one sequence of axis motions. It may name:

- a region that must be removed;
- material that must remain;
- a target surface or tolerance zone;
- roughing allowance;
- required tools or prohibited tools;
- precedence constraints;
- surface finish or scallop limits;
- setup and inspection requirements.

Mathematically, an intent $I$ can be interpreted as a set of acceptable final states:

$$
\llbracket I\rrbracket \subseteq \Sigma,
$$

where $\Sigma$ is the set of possible complete machining states. For the pocket, $\llbracket I\rrbracket$ contains every final state whose stock has the required cavity within tolerance, whose protected material remains, and whose process constraints have been respected.

A toolpath is then a **witness candidate**: a proposed implementation that should lead to an element of $\llbracket I\rrbracket$.

### Worked example: two valid implementations

Let $R$ be the 30 mm by 20 mm rectangular pocket footprint and let the requested floor depth be $z=-4$ mm. Ignoring corner-radius details for the moment, an intent can say:

1. Material inside $R$ above $z=-4$ must be removed, except for at most 0.05 mm residual allowance.
2. Material below $z=-4.05$ is protected.
3. Material outside the wall tolerance band is protected.
4. The tool assembly must not intersect either clamp.

A raster planner may cut horizontal lines with a stepover of 1.5 mm. An offset planner may cut shrinking rectangles. If both satisfy the four conditions, both refine the same intent.

This distinction gives an optimizer room to choose. The planner can minimize cycle time, tool changes, or rapid distance while treating the intent as a hard constraint.

### Counterexample: using emitted G-code as the source meaning

Imagine that a user edits the operation tolerance from 0.10 mm to 0.03 mm, but the UI preview and certificate still reference an old cached `.nc` file. If the G-code text is treated as the semantic source, the system has no principled way to say that the file no longer implements the current intent. The missing relation is between the high-level operation and the emitted artifact.

A second failure is subtler. Suppose two G-code files trace the same nominal points, but one begins in `G90` absolute mode and the other inherits `G91` incremental mode from the controller. Textual similarity does not imply behavioral equality. Meaning belongs to an interpreter plus an initial state.

> **Design consequence — keep intent alive.** Preserve feature identity, target geometry, tolerances, tools, and operation provenance through the compiler. Do not reduce the program to anonymous points before the checks that require manufacturing meaning.

## 1.2 The physical state a command can change

### Motivation

A path alone cannot tell us whether a move is legal. A line through space may be a safe rapid when the stock is already cleared, a crash when stock remains, or a valid cut when the spindle is running with the correct tool. Legality depends on state.

### Definition: machine/process state

A **machine/process state** is the collection of information needed to interpret a command and predict its relevant effects. One useful model is:

$$
\sigma =
(q,\dot q,F,W,T_a,C,S,P,O,M,t,U).
$$

The components are:

- $q$: axis positions or machine configuration;
- $\dot q$: velocity, when dynamics matter;
- $F$: frame graph and transforms;
- $W$: active work coordinate system;
- $T_a$: active tool assembly, including holder;
- $C$: process state such as spindle, coolant, feed, and overrides;
- $S$: current stock;
- $P$: target and protected material;
- $O$: fixtures and machine obstacles;
- $M$: controller mode and modal state;
- $t$: time;
- $U$: uncertainty and assumptions associated with the other components.

![Components of a machine and process state.](figures/state_model.png){width=95%}

Not every pass needs every component. A unit checker does not need stock. A rapid-clearance checker does. An important architectural rule follows: a checker should receive every artifact needed to state its proposition. If a “gouge checker” receives no target geometry, it cannot establish a target-gouge claim.

### Worked example: one cutting move

Assume the machine is homed, tool T1 is selected, the spindle is running, and the current tool-tip pose is $(15,10,2)^{work}$. A helical entry follows a path $\gamma$ down to the first roughing level at $z=-1.5$ mm.

Before execution, the state includes the original stock $S_0$. After successful cutting, an idealized state update is:

$$
S_1 = S_0 \setminus \operatorname{Sweep}(T_c,\gamma),
$$

where $T_c$ is the cutting geometry of the tool. The pose becomes the endpoint of $\gamma$. The spindle remains on. The target $P$ and fixtures $O$ do not change.

This one command has several distinct postconditions:

- endpoint pose updated;
- stock decreased;
- target not excessively penetrated;
- fixtures unchanged;
- spindle state preserved;
- trace and provenance recorded.

A validator that checks only endpoint coordinates observes very little of this meaning.

### Fundamental idea: state does not mean one mutable object

The mathematical state $\sigma$ is a semantic model. An implementation does not need one giant mutable JavaScript object containing a mesh, controller socket, and every UI value. Different representations can project the state they need. The requirement is that the semantics make dependencies explicit enough to prevent unsound assumptions.

For example, a scheduler may use a symbolic stock-state identifier rather than storing a full voxel volume in every node. A certificate checker can resolve that identifier to the exact content-addressed stock artifact.

## 1.3 Units are part of meaning

### Motivation

Numbers such as `3`, `400`, and `12000` are meaningless without dimensions. A tool diameter of 3 mm, a feed of 400 mm/min, and a spindle speed of 12,000 rpm are all represented by JavaScript numbers. Accidentally exchanging them may still produce finite values and valid JSON.

### Definition: physical dimension and unit

A **physical dimension** identifies the kind of quantity: length, time, angle, speed, rotational rate, and so forth. A **unit** selects a scale within a dimension, such as millimetres or inches for length.

A useful core policy is to choose one internal unit for each dimension and convert at the boundary. For length:

```ts
type Mm = number & { readonly __brand: "mm" };
type MmPerMin = number & { readonly __brand: "mm/min" };
type Rpm = number & { readonly __brand: "rpm" };

const mm = (x: number): Mm => x as Mm;
const inch = (x: number): Mm => mm(25.4 * x);
```

The brand makes incompatible quantities distinct to TypeScript while erasing to a number at runtime.

### Worked example: a dimensionally correct pocket call

```ts
job.rectPocket({
  x: mm(15),
  y: mm(10),
  w: mm(30),
  h: mm(20),
  depth: mm(4),
  stepdown: mm(1.5),
  stepover: ratio(0.40),
  feed: mmPerMin(450),
});
```

The `depth` and `feed` fields cannot be interchanged without a type error in checked TypeScript. The `stepover` is deliberately a dimensionless ratio of tool diameter, not a bare length.

### Counterexample: branded values without runtime validation

A brand is a compile-time fiction. This code defeats it:

```ts
const feed = JSON.parse(input).feed as MmPerMin;
```

If the JSON contains `"fast"`, `NaN`, a negative number, or a value in inches, the cast proves nothing. Constructors and deserializers must validate finite values, ranges, and units. Plugins and script boundaries are runtime trust boundaries.

### Quantization is also a unit-level effect

When G-code emits coordinates with three decimal places, each coordinate is rounded with an error of at most:

$$
\varepsilon_{round}=\tfrac{1}{2}\,10^{-3}\ \mathrm{mm}=0.0005\ \mathrm{mm}.
$$

This contribution is small but real. It belongs in a quantitative error argument and must be associated with the metric it affects. We will return to typed error budgets in Chapter 3.

> **Design consequence — convert once, validate twice.** Convert external units into canonical units at the API boundary. Validate dimensions statically where possible and values dynamically at every untrusted boundary.

## 1.4 Coordinate frames prevent a high-cost class of errors

### Motivation

The running pocket is described in a work frame whose origin lies on the stock. The machine axes use a machine frame. A mesh may arrive centered around its own origin. A clamp model may be expressed in a fixture frame. The tuple `(15, 10, -4)` has no operational meaning until its frame is known.

### Definition: frame and rigid transform

A **coordinate frame** is a named coordinate system in which points and vectors are expressed. A **rigid transform** maps coordinates between frames using rotation and translation while preserving distances.

A three-dimensional rigid transform belongs to the group $SE(3)$. It can be represented by a rotation matrix $R$ and translation vector $t$:

$$
p^B = R_{A\to B}p^A+t_{A\to B}.
$$

In TypeScript:

```ts
interface Point3<F extends FrameId> {
  readonly x: Mm;
  readonly y: Mm;
  readonly z: Mm;
  readonly frame: F;
}

interface Transform<A extends FrameId, B extends FrameId> {
  readonly from: A;
  readonly to: B;
  readonly r: Matrix3;
  readonly t: Vec3;
}
```

Composition is defined only when frames meet:

$$
T_{A\to C}=T_{B\to C}\circ T_{A\to B}.
$$

Every rigid transform is invertible. Frames and invertible transforms therefore form a **groupoid**: a category in which every arrow has an inverse.

### Worked example: placing the part on the machine

Suppose the work origin is 80 mm to the right and 45 mm forward of the machine origin, with the stock top 12 mm below the machine's Z reference. A pure translation gives:

$$
T_{work\to machine}(x,y,z)=(x+80,y+45,z-12).
$$

The pocket-floor point $(15,10,-4)^{work}$ becomes:

$$
(95,55,-16)^{machine}.
$$

A travel checker must operate in a frame compatible with the machine envelope. A target-gouge checker may remain in the work or part frame if all compared geometry shares that frame.

### Counterexample: changing a label without applying a transform

This cast is not a transform:

```ts
const machinePoint = workPoint as Point3<"machine">;
```

It changes only the compiler's belief. The numeric coordinates remain in the work frame. A safe API permits such a cast only inside a boundary function whose caller explicitly assumes responsibility, and runtime frame identifiers should still be checked.

### Frame uncertainty

A probed work offset is not one exact transform. It is better modeled as a set or interval of possible transforms. A point at radius $r$ from the origin experiences positional uncertainty from an angular error $\delta\theta$ of approximately:

$$
\delta p \le r\,\delta\theta.
$$

Thus a small rotational uncertainty can dominate far from the probed datum. A certificate must either include this propagation or state that the frame is assumed exact.

## 1.5 Path, time law, trajectory, and swept volume

### Motivation

CAM discussions often use “toolpath” to mean several different objects. This ambiguity causes incorrect algorithms. A polyline says where to go but not how fast. A feed schedule says how progress changes over time. Material removal depends on the three-dimensional tool shape at every pose, not only on the centerline.

### Definition: geometric path

A **geometric path** is a continuous map from normalized progress to configuration or pose:

$$
\gamma:[0,1]\to Q.
$$

For a fixed-orientation three-axis mill, $Q$ may be approximated by $\mathbb R^3$. For multi-axis machining, $Q$ includes orientation and often axis configuration.

### Definition: time law and trajectory

A **time law** is a monotone map:

$$
s:[0,T]\to[0,1].
$$

The resulting **trajectory** is:

$$
x(t)=\gamma(s(t)).
$$

The same path may have several time laws. One respects only a feed limit; another also respects axis velocity, acceleration, jerk, and controller tracking constraints.

### Definition: swept volume

For a tool solid $T$ and pose trajectory $x(t)$, the **swept volume** is:

$$
\operatorname{Sweep}(T,x)=\bigcup_{t\in[0,T]}x(t)T.
$$

![A path and a time law combine to form a trajectory; the moving tool forms a swept volume.](figures/path_trajectory.png){width=90%}

### Worked example: a linear cut

Let a 6 mm diameter flat end mill move from $(15,10,-1.5)$ to $(45,10,-1.5)$ at 450 mm/min. The geometric path is:

$$
\gamma(s)=(15+30s,10,-1.5).
$$

At constant feed, the move length is 30 mm and the duration is:

$$
T=\frac{30\ \mathrm{mm}}{450\ \mathrm{mm/min}}=0.066\bar6\ \mathrm{min}=4\ \mathrm{s}.
$$

The time law is $s(t)=t/4$ for $0\le t\le4$ seconds. The cutting sweep is a horizontal capsule-like prism formed by translating the cutter disc along the segment and extending through the flute engagement depth.

### Counterexample: endpoint-only collision checking

Suppose both endpoints are clear of a narrow clamp that lies halfway between them. An endpoint checker reports success. The continuous swept volume intersects the clamp. Sampling at ten equally spaced times can still miss an obstacle thinner than the sample spacing or an event between samples.

The property to prove is quantified over all time:

$$
\forall t\in[0,T],\quad x(t)T_a\cap O=\varnothing,
$$

where $T_a$ is the complete tool assembly. A finite sampling method needs an additional theorem connecting samples to the continuous interval. Without that theorem it is simulation, not proof.

## 1.6 Motion classes carry different process meanings

### Motivation

The same geometric line may be used to cut, traverse, probe, or inspect. Treating these actions as one generic “move” loses the state changes and safety rules that distinguish them.

### Definition: canonical machining action

A **canonical machining action** is a controller-independent operation with explicit physical intent. A compact action algebra might contain:

```ts
type CanonicalCommand =
  | ToolChange
  | SpindleAction
  | CoolantAction
  | Traverse
  | Cut
  | Probe
  | Dwell
  | Pause;
```

A traverse promises no material removal. A cut updates stock. A probe produces a measurement and stops under a contact condition. A pause changes the controller lifecycle without prescribing a path.

### Worked example: safe traverse versus `G0`

The running job finishes one offset loop at low Z and must move to the start of the next loop. The manufacturing request is:

> Reach point B without cutting and without intersecting current stock, target, fixture, or holder constraints.

A conservative postprocessor may lower this one traverse into three motions:

```text
raise Z to a certified clearance plane
move X and Y to the next entry point
lower Z to the entry height
```

This is not equivalent to blindly emitting one three-axis `G0 X... Y... Z...` block if the controller can perform a dogleg rapid. The canonical action expresses the desired property; target lowering chooses an implementation compatible with the controller semantics.

### Counterexample: inserting a connector into two cut paths

Suppose path A ends at one side of a fixture and path B starts at the other. A generic path utility notices discontinuity and inserts a straight line. Geometry becomes continuous, but the new segment has no motion class. If interpreted as cut, it gouges stock. If interpreted as traverse, it collides with the fixture. Continuity repair is a semantic operation and must be checked as such.

## 1.7 Denotational semantics: what outcome does an operation permit?

### Motivation

We need a mathematical account of intent and process that does not depend on execution order or controller syntax. Denotational semantics supplies this view by assigning each construct a mathematical meaning.

### Definition: denotational semantics

A **denotational semantics** maps a language construct to a mathematical object in a compositional way. For a machining command, a relation is more realistic than a deterministic function:

$$
\llbracket c\rrbracket:
\Sigma\to\mathcal P(\Sigma\times Trace\times Outcome).
$$

The powerset $\mathcal P$ represents possible outcomes caused by measurement uncertainty, controller faults, following error, or deliberately underspecified choices.

For an ideal deterministic cut along trajectory $x$ with cutter $T_c$:

$$
\llbracket \operatorname{Cut}(x,T_c)\rrbracket(\sigma)
=
\sigma[S:=S\setminus\operatorname{Sweep}(T_c,x),\ q:=x(T)].
$$

For a traverse:

$$
S'=S.
$$

### Manufacturing intent as a predicate

A pocket intent can be defined as a predicate on final stock $S_f$. Let $V_{req}$ be material required to be absent and $P_{protected}$ material required to remain. Then an idealized specification is:

$$
V_{req}\cap S_f=\varnothing
$$

and:

$$
P_{protected}\subseteq S_f.
$$

Tolerance replaces exact emptiness and inclusion with metric bounds. Roughing allowance changes the required and protected regions.

### Worked example: roughing and finishing as refinement

A roughing operation leaves 0.2 mm radial and axial allowance. It is correct relative to a roughing intent whose protected region includes that allowance. A finishing operation then refines the residual stock toward the final intent.

The two operations compose at the stock level:

$$
S_2=(S_0\setminus R_{rough})\setminus R_{finish}.
$$

Set difference is associative in the useful sense:

$$
(S\setminus R_1)\setminus R_2=S\setminus(R_1\cup R_2).
$$

However, this algebraic equality does **not** imply the operations may be reordered physically. Intermediate stock affects entry, support, engagement, and safe linking. Chapter 3 will distinguish geometric commutativity from process independence.

### Fundamental idea: specification versus implementation

The denotation of a high-level operation is usually a set of acceptable outcomes. A planner chooses one implementation and should produce a witness showing why it belongs to that set. This is the key move that turns strategy code from a trusted oracle into an untrusted producer whose output can be checked.

## 1.8 Operational semantics: how execution proceeds

### Motivation

Denotational semantics tells us the allowed result, but controller faults, modal state, probing, pause, and resume require a step-by-step account. Operational semantics describes transitions between configurations.

### Definition: small-step operational semantics

A **small-step operational semantics** uses rules of the form:

$$
\langle c,\sigma\rangle\to\langle c',\sigma'\rangle.
$$

Each rule performs one conceptual transition. A completed atomic command may instead use:

$$
\langle c,\sigma\rangle\Downarrow(\sigma',e),
$$

where $e$ is an emitted event or trace fragment.

### Worked rule: cutting

A simplified rule is:

$$
\frac{
\operatorname{Homed}(\sigma)\quad
\operatorname{WCSKnown}(\sigma)\quad
\operatorname{Tool}(\sigma)=T\quad
\operatorname{SpindleValid}(\sigma)\quad
\operatorname{PathSafe}(\gamma,\sigma)
}{
\langle\operatorname{Cut}(\gamma,T,f),\sigma\rangle
\Downarrow
(\sigma',\operatorname{CutTrace}(\gamma,f))
}
$$

with:

$$
\sigma'.S=\sigma.S\setminus\operatorname{Sweep}(T_c,\gamma),
\qquad
\sigma'.q=\gamma(1).
$$

If a premise fails, a different rule produces a diagnostic or fault outcome. The rule makes the preconditions explicit instead of hiding them in an informal comment.

### Worked rule: probing

A probe move introduces nondeterminism because contact may occur at an uncertain point or not occur at all:

$$
\langle\operatorname{Probe}(\gamma),\sigma\rangle
\Downarrow
\begin{cases}
(\sigma_c,\operatorname{Contact}(p,U_p)),\\
(\sigma_n,\operatorname{NoContact}),\\
(\sigma_a,\operatorname{Alarm}).
\end{cases}
$$

The measured point and its uncertainty become a value used by later frame construction. A command sequence that executes `probe` and then `set offset` without binding the result is semantically incomplete.

### Why a reference interpreter matters

A pure interpreter for canonical commands provides one executable definition of meaning. It can drive:

- tests;
- abstract analysis;
- preview traces;
- time estimation;
- pass validation;
- comparison with parsed G-code.

The production simulator may use faster approximations. The reference interpreter should favor clarity and explicitness.

## 1.9 Axiomatic semantics: contracts around commands

### Motivation

When designing an API or validator, we often want to reason locally: what must be true before this command, and what can callers rely on afterward? Axiomatic semantics expresses this with logical contracts.

### Definition: Hoare triple

A **Hoare triple** has the form:

$$
\{P\}\ c\ \{Q\}.
$$

It means: if precondition $P$ holds and command $c$ terminates normally, then postcondition $Q$ holds.

For a traverse along $\gamma$ from $a$ to $b$:

$$
\{
q=a\land\operatorname{Homed}\land
\operatorname{Clear}(\gamma,T_a,S,O,P)
\}
$$

$$
\operatorname{Traverse}(\gamma)
$$

$$
\{
q=b\land S'=S\land T'=T\land C'=C
\}.
$$

The stock-equality postcondition is an important semantic distinction from a cut.

### Definition: weakest precondition

The **weakest precondition** $wp(c,Q)$ is the least restrictive condition that guarantees postcondition $Q$ after command $c$. For sequencing:

$$
wp(c_1;c_2,Q)=wp(c_1,wp(c_2,Q)).
$$

This lets us derive preflight requirements backward from the desired final condition.

### Worked example: deriving a pocket-job preflight

Consider the simplified program:

```text
select tool T1
start spindle at 12,000 rpm
traverse to entry
cut roughing paths
retract to safe pose
stop spindle
```

Desired final condition:

$$
Q=\operatorname{Pose}=p_{safe}\land\operatorname{SpindleOff}.
$$

Work backward.

1. `stop spindle` requires a live controller session and establishes `SpindleOff`.
2. `retract` requires a continuous collision-free path from the final cut pose to $p_{safe}$.
3. `cut roughing paths` requires homing, known WCS, selected tool, running spindle, valid feed, safe sweep, and target allowance.
4. `traverse to entry` requires free-space clearance under the current stock state.
5. `start spindle` requires a selected tool and supported RPM.
6. `select tool T1` requires that T1 is available and compatible with the setup.

The resulting $wp$ is a structured preflight specification. Some clauses can be checked at compile time, some at runtime, and some remain physical assumptions.

### Counterexample: a checklist detached from program semantics

A UI may display fixed checkboxes for “homed,” “cover closed,” and “tool loaded.” If the actual program contains no motion but writes a configuration file, homing is irrelevant. If it resumes a held job, current queued motion and job identity are crucial. A weakest-precondition approach derives requirements from the actual action class and program structure.

## 1.10 Invariants: properties that survive every step

### Motivation

A postcondition describes one operation. A long-running controller and a multi-pass compiler need properties that remain true across many transitions.

### Definition: invariant

An **invariant** is a predicate $I$ satisfying:

1. Initialization: $I(\sigma_0)$.
2. Preservation:

$$
I(\sigma)\land \sigma\to\sigma'
\Rightarrow I(\sigma').
$$

Typical CAM invariants include:

- stock monotonicity: $S_{i+1}\subseteq S_i$;
- every coordinate has one known frame;
- a cutting action has a selected tool and valid spindle state;
- a controller can execute only the content hash it has authorized;
- a stop-class command is never blocked by a failed motion preflight;
- no unsupported operation remains after machine lowering.

### Worked proof: stock monotonicity

Assume the command language contains cuts, traverses, spindle actions, tool changes, dwells, and probes. Define:

$$
I(\sigma)\equiv S\subseteq S_0.
$$

Initialization is immediate because $S=S_0$. For preservation:

- a cut updates $S'=S\setminus R$, so $S'\subseteq S\subseteq S_0$;
- every other command preserves $S$, so $S'=S\subseteq S_0$.

Therefore the invariant holds for every finite execution.

This proof does not establish **correct** removal. A broken cut may remove protected material while stock still decreases. Invariants must be chosen to match the desired property.

### Representation invariants versus physical invariants

A `PathBuilder` can guarantee that a path's declared `end` equals the terminal point derived from its segment list. This is a representation invariant. It does not prove that the arc radii are coherent, that a polysegment begins at the cursor, or that the path avoids fixtures. Clear naming prevents a local data-structure guarantee from being advertised as machining safety.

## 1.11 Temporal semantics: behavior over a whole controller trace

### Motivation

Upload, start, hold, resume, abort, disconnect, and alarm are not well modeled as isolated functions. They are concurrent protocol transitions. Safety may depend on what is always true; liveness may depend on what eventually happens.

### Definition: trace, safety, and liveness

A **trace** is a finite or infinite sequence of states and events:

$$
\tau=\sigma_0,e_0,\sigma_1,e_1,\ldots
$$

A **safety property** says that a bad event never happens. A finite prefix can demonstrate a violation. A **liveness property** says that a desired event eventually happens under stated fairness and environment assumptions.

Temporal logic uses operators such as:

- $\Box P$: always $P$;
- $\Diamond P$: eventually $P$.

Examples:

$$
\Box(\operatorname{Running}(h)\Rightarrow\operatorname{Authorized}(h))
$$

and:

$$
\Box(\operatorname{AbortRequested}\Rightarrow
\Diamond(\operatorname{Stopped}\lor\operatorname{Faulted})).
$$

### Worked example: resume is not read-only

A resume command may move no axis at the instant it is parsed. It nonetheless enables queued motion. Its effect class is therefore **state-enabling**, not read-only. A correct protocol requires fresh preflight and authorization at the transition from held to running.

This example illustrates why command classification should be based on operational effect rather than spelling. A bare `~` byte and a textual `resume` verb can share the same semantic class.

### Counterexample: timeout means failure

The host sends a start command and times out waiting for the reply. There are at least two possible states:

1. The controller never received the command.
2. The controller started the job and the acknowledgement was lost.

Blindly retrying can issue a second start or corrupt protocol state. The honest successor is an **ambiguous** set of states. The session should be quarantined until a trusted status query re-establishes the controller boundary.

## 1.12 The end-to-end correctness statement

We can now state what this compiler is trying to achieve.

Let $I$ be manufacturing intent, $B$ the exact deployed job bundle, and $A$ the set of assumptions about tool geometry, frames, fixtures, firmware, and physical machine behavior. Let $\operatorname{Exec}(B,A)$ be the possible physical traces when $B$ executes under assumptions $A$. Let $\alpha$ abstract a low-level trace to relevant manufacturing observations.

A bounded refinement statement is:

$$
\operatorname{verify}(B)=\text{true}
\land \operatorname{AssumptionsHold}(A)
$$

$$
\Longrightarrow
\forall\tau\in\operatorname{Exec}(B,A),\quad
\alpha(\tau)\in N_\varepsilon(\llbracket I\rrbracket).
$$

Here $N_\varepsilon$ is an allowed neighborhood under named metrics. The theorem says that every permitted execution produces an outcome within the declared tolerances of the intent.

This is stronger than “the preview looked right” and more honest than “safe: true.” It also makes incompleteness visible. If fixture geometry is absent, the fixture-clearance proposition cannot be proved. If the controller semantics are unknown, final-byte equivalence is conditional. If the actual tool is unmeasured, its diameter remains an assumption.

> **Fundamental idea — proofs are conditional.** Formal reasoning does not remove assumptions. It makes them explicit and prevents a claim from silently depending on facts the system never checked.

## 1.13 Chapter synthesis: specify the running pocket

We can now give the running job a semantic specification.

### Artifacts

- stock solid $S_0$;
- target/protected part $P$;
- clamp obstacles $O$;
- roughing tool assembly $T_1$;
- optional finishing tool assembly $T_2$;
- work-to-machine transform set $\mathcal T$;
- machine and controller profile $M$.

### Required outcome

Let $V_{pocket}$ be the ideal cavity and let $\delta=0.05$ mm. The final stock must satisfy a target-deviation predicate, for example:

$$
d_H(\partial S_f\cap R,\partial P\cap R)\le\delta,
$$

with additional directional conditions if normal error is the intended metric. Protected material outside the tolerance zone must remain.

### Process requirements

- all cutting paths use a compatible selected tool;
- spindle speed and feed remain within supported ranges;
- every traverse is disjoint from current stock and obstacles using the complete tool assembly;
- machine configurations remain inside the admissible envelope;
- the final spindle state is off;
- the controller executes exactly the certified bytes;
- runtime assumptions about machine identity, WCS, tool, setup, and interlocks hold.

This specification is not yet an algorithm. Chapter 2 designs the language and compiler that can carry it. Chapter 3 constructs candidate paths and schedules. Chapter 4 develops the evidence that lets a small checker accept or reject the final bundle.

## Exercises

### Concept checks

1. Give two geometrically different toolpaths that implement the same pocket intent. State which properties must be equal and which may differ.
2. Classify each object as intent, path, trajectory, or physical trace: a 0.4 tool-diameter stepover; a list of XYZ points; a velocity-versus-time curve; encoder samples.
3. Explain why a point requires a frame even when all current jobs use only G54.
4. Distinguish a representation invariant from a safety invariant using a path example.
5. Give one safety property and one liveness property for an upload protocol.

### Worked derivations

6. A 40 mm line is traversed at 1,200 mm/min. Compute the constant-feed duration. Then explain why this does not establish actual duration on a machine with acceleration limits.
7. A frame has angular uncertainty $0.0003$ rad. Bound the resulting positional uncertainty 80 mm from the datum.
8. Write a Hoare triple for `startSpindle(12000)` that mentions tool selection and maximum RPM.
9. Derive the weakest precondition of `traverse; cut; stopSpindle` for the postcondition “spindle off and stock conforms to roughing intent.”
10. Prove stock monotonicity for a language that also contains an additive-manufacturing command. What changes?

### Counterexample construction

11. Construct three points $a,b,c$ for which $d(a,b)<\varepsilon$ and $d(b,c)<\varepsilon$ but $d(a,c)\ge\varepsilon$.
12. Design a path whose endpoints are clear of an obstacle but whose swept volume collides.
13. Give a controller payload whose first token is read-only but whose later content can move the machine. What must a safe parser do?
14. Describe a state in which `resume` is more dangerous than a new single jog command.

### Design exercise

15. Write a structured semantic specification for drilling four holes. Include required removal, protected material, probe or setup assumptions, tool state, and terminal controller state. Do not write G-code.
EOF
python - <<'PY'
from pathlib import Path
p=Path('/mnt/data/z1_pedagogical_textbook_work/book/draft_v1.md')
print('chapter1 draft:',len(p.read_text().split()),'words',p.stat().st_size,'bytes')
PY
```

The semantic foundation and compiler architecture are drafted; I’m now deriving geometry algorithms only after defining their safety obligations, including clearance, coverage, scallop spacing, and numerical error.

<details><summary>💭 Thinking</summary>

**Drafted a pedagogical CAM compiler textbook**

</details>

```unknown
bash -lc cat >> /mnt/data/z1_pedagogical_textbook_work/book/draft_v1.md <<'EOF'

# Geometry, Planning, and Optimization

## Chapter orientation

The compiler architecture of Chapter 2 deliberately treats planning algorithms as producers rather than unquestioned authorities. This chapter studies what those producers must compute and what a checker must later verify.

CAM geometry is difficult because several problems are intertwined. A cutter has volume, not merely a center point. A mesh is an approximation to a design surface. A finishing tolerance is a statement about continuous geometry, while most algorithms operate on samples. Contour extraction makes discrete topological decisions. Linking depends on material removed by earlier operations. Scheduling and feed selection are constrained optimization problems rather than drawing operations.

We will separate these concerns. First we construct cutter-location geometry. Then we turn fields into paths, paths into safe connected programs, and programs into schedules and time laws. Throughout the chapter, we distinguish a useful numerical approximation from a sound enclosure.

### Learning objectives

After this chapter, you should be able to:

- formulate CAM planning as constrained witness search;
- explain cutter-location surfaces for flat and ball end mills;
- describe the role of triangle feature contact and spatial indices in a drop-cutter evaluator;
- explain why grid spacing and sample count are not automatically error bounds;
- implement and critique marching-squares contour extraction;
- derive 2.5D offset-pocket and ball-tool scallop formulas;
- compare raster, waterline, constant-scallop, and hybrid strategies;
- formulate safe linking in configuration space;
- compare height-field, dexel, and voxel stock models;
- use inner and outer approximations in the direction required by a claim;
- formulate operation ordering and feed planning as operations-research problems;
- compose typed numerical and physical error bounds.

![The major stages of geometric and process planning.](figures/planning_pipeline.png){width=98%}

## 3.1 Planning is constrained witness search

### Motivation

A strategy called `pocket`, `raster`, or `constantScallop` can easily be treated as a black box that returns points. That obscures the most important fact: a planner searches for one object satisfying a specification.

### Definition: planning problem

A **planning problem** consists of:

- an intent $I$;
- a context $C$ containing geometry, tools, machine constraints, stock state, and tolerances;
- a feasible set $\mathcal F(I,C)$;
- optionally, an objective $J$.

The planner seeks:

$$
x\in\mathcal F(I,C),
$$

or, for optimization:

$$
\min_{x\in\mathcal F(I,C)} J(x).
$$

The candidate $x$ may include paths, entries, links, orientation choices, operation order, feeds, and time laws.

### Hard constraints versus objectives

A target-gouge limit, fixture clearance, axis travel limit, or required precedence is a **hard constraint**. Cycle time, rapid distance, and number of tool changes are **objectives**. Safety must not be encoded merely as a large penalty:

$$
J(x)=time(x)+10^9\,collisionDepth(x).
$$

A sufficiently large time improvement could still make a colliding candidate numerically “better.” The correct model excludes colliding candidates from $\mathcal F$.

### Worked example: planning variables for the pocket

A pocket planner may choose:

- tool T1 or T2;
- stepdown levels $z_1,\ldots,z_k$;
- lateral stepover $s$;
- offset or raster pattern;
- direction of each loop;
- helical, ramp, or plunge entry;
- link paths;
- feed schedule.

Feasibility requires complete coverage within roughing allowance, no protected-material penetration, valid engagement, safe entry and links, and machine-supported motion. An objective may minimize estimated cycle time plus a penalty for retracts.

### Definition: witness

A **planning witness** is data that helps an independent checker establish feasibility. For an offset pocket it might contain:

- the inward-offset regions at each depth;
- the path-to-region coverage correspondence;
- selected entry-clearance regions;
- the stock-state version used for each link;
- the declared stepover and allowance;
- provenance from paths to the operation.

The witness is not trusted merely because the strategy produced it. It reduces checker work and improves diagnostics.

## 3.2 Cutter-location geometry

### Motivation

A target surface tells us where the finished material boundary should lie. The tool center or tip cannot simply follow that surface because the tool has a shape. A ball end mill touching a slope has its center displaced along the surface normal. A flat end mill must remain above the highest point under its circular bottom.

The planner therefore needs a surface of legal tool-reference positions.

### Definition: cutter-location surface

For a fixed tool orientation and planar XY placement, the **cutter-location surface** gives the lowest legal tool-reference height at every $(x,y)$ position without penetrating protected target geometry.

Write:

$$
CL_T(x,y)=\inf\{z\mid T+(x,y,z)\text{ does not penetrate }P\}.
$$

For common three-axis cutters and height-like target geometry, this becomes a maximum over possible contacts.

![A target surface and the corresponding ball-tool cutter-location surface.](figures/cl_surface.png){width=92%}

### Flat end mill

Let a flat end mill have radius $R$. Its cutting bottom is a horizontal disc. If the target can be described by height $h(u,v)$, the lowest safe tip height at axis position $(x,y)$ is:

$$
CL_{flat}(x,y)=
\max_{(u-x)^2+(v-y)^2\le R^2} h(u,v).
$$

The tool must clear the highest target point under its disc.

### Ball end mill

Let the spherical tip have radius $R$, and let the tool reference be the lowest point of the ball. A target point $(u,v,h(u,v))$ at horizontal distance:

$$
r=\sqrt{(u-x)^2+(v-y)^2}
$$

can contact the ball only when $r\le R$. The sphere center must lie at least:

$$
h(u,v)+\sqrt{R^2-r^2}.
$$

The tool-tip height is one radius lower, so:

$$
CL_{ball}(x,y)=
\max_{r\le R}
\left[h(u,v)+\sqrt{R^2-r^2}-R\right].
$$

This is a morphological dilation-like maximum. It explains why a ball tool cannot enter concave details smaller than its radius.

### Worked example: ball over a single point

A protected target point lies at height 2 mm, 1 mm horizontally from the tool axis. For a ball radius $R=3$ mm:

$$
CL=2+\sqrt{3^2-1^2}-3
=2+\sqrt8-3
\approx1.828\text{ mm}.
$$

The ball tip may lie below the target point because the side of the ball contacts it.

### Triangle meshes and feature contact

A mesh triangle can contact a spherical cutter at:

1. a vertex;
2. an edge interior;
3. a face interior.

A correct analytic drop-cutter evaluator computes the highest legal contact from all three feature classes and then takes the maximum across candidate triangles. Checking vertices alone misses a large face under the tool. Checking face planes alone misses edge and corner contacts near triangle boundaries.

For a ball tool over a triangle plane:

$$
z=Ax+By+C,
$$

the sphere center touching the infinite plane lies a normal distance $R$ away. Its center height at axis position $(x,y)$ is:

$$
z_c=Ax+By+C+R\sqrt{1+A^2+B^2}.
$$

The contact is valid only if the projected contact point lies inside the triangle. Edge and vertex formulas handle the remaining cases.

### Spatial acceleration

A mesh may contain millions of triangles, but only triangles within the tool's horizontal reach can contribute at one $(x,y)$. A **spatial index** partitions or bounds triangles so the evaluator queries a disc of radius $R$ rather than scanning the entire mesh.

The index can also store an upper height bound. If a node cannot exceed the current best contact height, it is pruned. This is branch-and-bound: a cheap conservative bound eliminates expensive exact feature tests.

### Counterexample: approximate V-bit as a flat disc

Treating a V-bit as a small flat disc may be useful for preview, but it changes the contact geometry. A cone's effective radius grows with depth. The approximation cannot support a claim about V-carved width or no-gouge on sloped walls unless a conservative relation to the true cone is proved. The honest result is “unsupported or approximated under these limitations,” not an exact cutter-location surface.

### Design consequence

Separate the fast evaluator from its evidence level. A specialized, allocation-free triangle loop may be appropriate in the planner. A certificate checker may use a slower independent enclosure, adaptive subdivision, or a different representation.

## 3.3 From an evaluator to a sampled field

### Motivation

Calling a drop-cutter evaluator everywhere is expensive. Many strategies therefore sample it on a regular grid and interpolate. A field enables contours, distance transforms, and fast preview. The cost is approximation.

### Definition: sampled cutter-location field

Choose grid spacing $g$, origin $(x_0,y_0)$, and dimensions $n_x,n_y$. Store:

$$
H_{ij}=CL(x_0+ig,y_0+jg).
$$

An interpolant $\widetilde{CL}(x,y)$ estimates values between samples. Bilinear interpolation is common.

### Worked example: memory and work

A 60 mm by 40 mm stock sampled every 0.1 mm uses approximately:

$$
(601)(401)\approx241{,}000
$$

samples. At eight bytes each, one scalar field uses about 1.9 MB. At 0.02 mm, the field exceeds six million samples and about 48 MB before auxiliary arrays. Resolution increases cost quadratically in the XY plane.

### Definition: discretization error

**Discretization error** is the difference between the continuous mathematical object and its finite representation. Grid spacing is an input to an error analysis, not the error itself.

If a function is known to be Lipschitz with constant $L$:

$$
|CL(p)-CL(q)|\le L\|p-q\|,
$$

then the distance to the nearest sample gives a conservative value bound. Without such regularity, a narrow spike between samples may be arbitrarily high.

### Counterexample: “verified at 0.1 mm resolution”

A target contains a 0.03 mm-wide ridge between grid lines. No sample sees it. A planner follows the interpolated field through the ridge. Stating “verified to 0.1 mm” is unsupported unless the geometry representation or derivative bounds prove that no feature can vary that rapidly.

A sound field can instead store conservative cell bounds:

$$
CL^-(cell)\le CL(p)\le CL^+(cell)
\quad\forall p\text{ in cell}.
$$

The planner may use nominal values; the checker uses the enclosures.

### Adaptive refinement

A practical refinement loop is:

```text
function certifyCell(cell, budget):
    bound = conservativeSurfaceBound(cell)
    approximation = localInterpolant(cell)
    error = boundDeviation(bound, approximation)

    if error <= budget:
        accept cell with evidence
    else if cell is still splittable:
        subdivide and recurse
    else:
        return inconclusive
```

A midpoint residual is useful only when a theorem relates it to the maximum interval error. For arbitrary geometry, comparing one midpoint with the endpoint interpolant is a heuristic. The certificate must say so.

## 3.4 Extracting contours without corrupting topology

### Motivation

Waterline finishing, Z-level roughing, and constant-scallop methods often extract level sets from a sampled field. The result should be a collection of closed loops and open curves. Small local topology errors can create self-intersections, missing loops, or connectors between unrelated regions.

### Definition: level set and contour

For scalar field $f(x,y)$ and level $c$, the **level set** is:

$$
L_c=\{(x,y)\mid f(x,y)=c\}.
$$

A contour algorithm approximates $L_c$ with line segments or curves.

### Marching squares

Marching squares examines the four signs of $f-c$ at each grid cell. The four bits select one of 16 cases. Crossing points are interpolated along cell edges. Most cases produce one segment.

### Saddle ambiguity

Cases with diagonally opposite corners on the same side of the level admit two connections.

![The ambiguous saddle case has two possible contour topologies.](figures/marching_squares_saddle.png){width=78%}

A cell-center test is a common pragmatic decider. A more principled **asymptotic decider** uses the bilinear interpolant to determine which branches connect. The chosen rule must be consistent across cells and documented, because it changes topology rather than merely position.

### Segment chaining

After local segments are emitted, their endpoints must be joined. A robust implementation distinguishes:

- topological identity: which two endpoints arise from the same grid edge;
- metric proximity: how close two independently constructed coordinates are.

For marching squares, endpoints on a shared grid edge can be assigned an exact symbolic identity such as `(gridEdgeId, levelId)`. This avoids guessing from floating-point coordinates.

### Counterexample: modulo-packed endpoint keys

Consider an implementation that quantizes coordinates at $10^{-6}$ mm and packs them after reducing each integer coordinate modulo $2^{26}=67{,}108{,}864$:

```ts
qx = round(x * 1_000_000) % 67_108_864;
qy = round(y * 1_000_000) % 67_108_864;
key = qx * 67_108_864 + qy;
```

Coordinates separated by:

$$
\frac{67{,}108{,}864}{1{,}000{,}000}
=67.108864\text{ mm}
$$

produce the same quantized residue. On a machine whose work envelope exceeds that distance, unrelated endpoints can enter the same bucket and contours can merge. The code may look numerically careful because the tolerance is tiny, yet the modulo operation destroys global uniqueness.

The fix is not simply a smaller tolerance. Use a collision-free pair key, nested maps, a string or bigint tuple, or—best for grid contours—exact edge identifiers. If hashing is used, equality must still compare the full coordinates or symbolic IDs.

### Counterexample: tolerant chaining as topology

Two separate contours pass within 0.5 micrometres. A tolerance join merges them. The resulting loop may look plausible in a preview but cross a protected island. Topology decisions need robust identities and predicates, not only nearest-neighbor thresholds.

> **Fundamental idea — topology is discontinuous.** A 1-nanometre coordinate error is small. A wrong “connected/not connected” decision can change an entire toolpath. Spend numerical rigor on predicates that control topology.

## 3.5 Planning a 2.5D pocket

### Motivation

A rectangular pocket is conceptually simple, which makes it an excellent place to see how tool geometry, stepdown, stepover, coverage, direction, entry, and linking interact.

### Definition: configuration-space offset for a pocket

Let $R$ be the pocket region and let $D_r$ be a disc of tool radius $r$. A tool center may remain inside the inward offset:

$$
R_c=R\ominus D_r.
$$

This is a morphological erosion: the set of center positions for which the cutter disc remains inside the pocket boundary.

For a 30 mm by 20 mm rectangle and a 6 mm diameter cutter, $r=3$ mm. The boundary centerline rectangle is 24 mm by 14 mm, offset 3 mm from each wall.

### Stepover

The **stepover** is lateral distance between adjacent cutting tracks. If specified as fraction $\rho$ of tool diameter $D$:

$$
s=\rho D.
$$

With $D=6$ mm and $\rho=0.4$:

$$
s=2.4\text{ mm}.
$$

Nested rectangular loops can be generated at inward offsets:

$$
3.0,\quad5.4,\quad7.8\text{ mm},\ldots
$$

A coverage checker must verify that the union of cutter sweeps covers the required region. Merely counting loops is insufficient near corners and the center.

### Stepdown

The **stepdown** is axial depth per roughing layer. For a 4 mm pocket and 1.5 mm stepdown, one possible level sequence is:

$$
z=-1.5,\quad -3.0,\quad -3.8
$$

when 0.2 mm axial allowance is left for finishing. The finish floor then cuts to $z=-4.0$.

A planner must define whether `depth` means positive magnitude or signed Z. The Elaborated Plan IR should normalize this convention so later passes do not guess.

### Climb and conventional direction

For a rotating cutter, reversing a loop can change climb milling to conventional milling. Therefore a geometric loop may be reversible while a machining action is direction-constrained. The toolpath IR should carry directionality and cutting convention explicitly.

### Entry planning

A vertical plunge is often undesirable because the center of many end mills has low surface speed and limited chip evacuation. Common preference order:

1. helical entry;
2. linear or zig-zag ramp;
3. plunge when no safer entry fits and the tool supports it.

For ramp angle $\alpha$ and desired vertical drop $d$, required horizontal length is:

$$
L=\frac{d}{\tan\alpha}.
$$

At $d=1.5$ mm and $\alpha=3^\circ$:

$$
L\approx\frac{1.5}{0.05241}\approx28.6\text{ mm}.
$$

This is longer than many compact pockets. A zig-zag can distribute the descent across repeated passes.

### Counterexample: twelve samples prove helix clearance

Checking a helical orbit at twelve angles can catch many obvious collisions. It does not prove continuous clearance. A narrow obstacle or concave boundary may intrude between samples. The result should be labeled a sampled feasibility heuristic unless a bound on boundary variation connects the angular spacing to continuous separation.

### Worked planning pseudocode

```text
function planPocket(intent, tool, context):
    centerRegion = erode(intent.region, tool.radius)
    levels = chooseDepthLevels(intent.depth, intent.axialAllowance,
                               intent.stepdown)
    paths = []

    for z in levels:
        loops = inwardOffsets(centerRegion, intent.stepover * tool.diameter)
        ordered = chooseLoopOrderAndDirection(loops, context.cutConvention)
        entry = chooseEntry(ordered.first.start, z, currentStock, tool)
        paths.append(entry)
        paths.extend(liftLoopsToZ(ordered, z))

    finish = planBoundaryAndFloorFinish(intent, tool)
    return paths + finish, coverageWitness(...)
```

Every helper has an obligation. `erode` must be topologically robust. `chooseDepthLevels` must respect allowance and maximum stepdown. `chooseEntry` must use current stock. `coverageWitness` must establish the required-removal relation.

## 3.6 Three-dimensional finishing strategies

### Motivation

A sculpted surface cannot generally be covered by one planar offset family. Different surface regions favor different path families. The strategy should be understood through the error metric it controls.

### Raster finishing

A **raster** strategy lays parallel XY lines and lifts them to the cutter-location surface. It is simple and predictable. Its disadvantages include many reversals, direction-dependent finish, and inefficient coverage of steep walls.

Important parameters are line direction, stepover, clipping region, direction reversal, and adaptive refinement along each lifted line.

### Waterline finishing

A **waterline** or constant-Z strategy extracts contours of the cutter-location field at several Z levels. It performs well on steep walls because vertical spacing controls the cusp left between contours. It performs poorly on nearly horizontal regions, where contours become sparse or degenerate.

### Ball-tool scallop height

On a locally planar surface machined by parallel passes with a ball radius $R$, the exact scallop height between two tracks separated by $s$ is:

$$
h=R-\sqrt{R^2-\left(\frac{s}{2}\right)^2}.
$$

Solving for spacing:

$$
s=2\sqrt{2Rh-h^2}.
$$

For small $h$:

$$
h\approx\frac{s^2}{8R}.
$$

### Worked example: choose stepover from scallop

A 6 mm ball mill has $R=3$ mm. Desired planar scallop is $h=0.01$ mm:

$$
s=2\sqrt{2(3)(0.01)-0.01^2}
\approx0.4895\text{ mm}.
$$

A fixed 40% diameter stepover would be 2.4 mm and would leave a much larger scallop. This demonstrates why finishing stepover should derive from the surface-error requirement and tool geometry, not a roughing default.

On a curved surface, effective spacing must account for surface curvature, tool contact geometry, and direction. The planar formula is a local approximation, not a universal certificate.

### Constant-scallop strategies

A **constant-scallop** strategy attempts to space neighboring paths by approximately equal surface distance under a metric connected to residual cusp height. One approach constructs a distance or arrival-time field and extracts iso-contours.

The Eikonal equation has the form:

$$
\|\nabla u(x)\|=\frac{1}{F(x)},
$$

where $u$ is arrival time or distance and $F$ is propagation speed. Fast marching computes a monotone numerical solution on a grid. By choosing $F$ from local tool and surface geometry, iso-values of $u$ can approximate desired spacing.

Fast marching proves neither exact scallop height nor topology by itself. A checker still needs to relate field discretization, surface model, tool shape, extracted contours, and path refinement to the final metric.

### Hybrid strategies

A **hybrid waterline/raster** strategy may use waterlines on steep regions and raster or constant-scallop paths on shallow regions. It requires:

- a robust slope classifier;
- overlap or blending near the boundary;
- trimming without fragmenting contours incorrectly;
- linking between path families;
- consistent error budgets.

### Counterexample: strategy name as a guarantee

A node labeled `constant-scallop` does not establish constant scallop. It records intent or method. The guarantee comes from a proposition, evidence, and checker that quantify the maximum residual surface deviation.

## 3.7 Linking and free-space motion

### Motivation

Cutting paths do not form a complete executable program. The tool must travel between entries, loops, levels, tools, and parking poses. Linking often causes more crashes than the cutting paths because a low move crosses material that a planner assumed was gone.

### Definition: free-space link

A **free-space link** is a non-cutting path whose complete tool-assembly sweep is disjoint from current stock and obstacles under the relevant uncertainty:

$$
\operatorname{Sweep}^+(T_a,\gamma_{link})
\cap(S_i^+\cup O^+\cup P_{forbidden}^+)=\varnothing.
$$

The subscript $i$ matters. Link safety is relative to a particular stock state.

### Configuration space

For fixed tool orientation and pure translation, expand obstacles by the reflected tool assembly:

$$
O_C=O\oplus(-T_a).
$$

The tool can then be represented by a point, and safe links avoid $O_C$.

![Configuration-space expansion turns a finite-radius tool into a point path.](figures/configuration_space.png){width=84%}

### Worked example: retract policy

A simple conservative linker uses a certified clearance plane $z_c$:

```text
from current pose:
    raise vertically to z_c
    move XY at z_c
    descend vertically to destination entry height
```

This is safe only if:

- both vertical columns are clear;
- the horizontal sweep at $z_c$ clears stock, fixtures, and holder constraints;
- $z_c$ lies within machine travel;
- controller rapid semantics implement or refine these segments.

A single “safe Z” scalar does not prove these conditions automatically.

### Shortest-path linking

More efficient linkers can search a graph or field in free configuration space:

- visibility graph around polygonal obstacles;
- A* on a conservative grid;
- navigation mesh;
- fast marching on a clearance-weighted cost field;
- stock-aware local retract and stay-down moves.

The objective might be path length or estimated time, but feasibility remains independently checked.

### Counterexample: link checked against final stock

A link between two early roughing paths is tested against the final cleared pocket. It passes. During actual execution, a central island of stock still exists and the low link crosses it. Every link must reference the stock state that precedes it, not a globally convenient final simulation.

## 3.8 Stock representations and swept-volume updates

### Motivation

Planning, simulation, and verification need a representation of remaining material. No single representation is best for all jobs.

### Height field

A **height field** stores one Z value per XY location. It is efficient for three-axis top-down machining without undercuts. It cannot represent multiple vertical intervals, caves, or arbitrary side entry.

### Dexel model

A **dexel** stores one or more material intervals along a ray. A vertical dexel grid can represent multiple layers. A triple-dexel model uses three orthogonal ray families to improve surface reconstruction and collision detail.

### Voxel model

A **voxel** model stores occupancy in three dimensions. It is general and simple to update but can be memory-intensive and produces staircase geometry unless refined.

### Boundary or exact solid model

A B-rep or exact constructive solid geometry model can represent boundaries precisely, but repeated swept-volume Boolean operations are computationally difficult and numerically delicate.

### Inner and outer approximations

Let $X$ be an unknown exact set. Maintain:

$$
X^-\subseteq X\subseteq X^+.
$$

The direction depends on the claim.

![Collision proofs use outer enclosures; guaranteed-removal proofs use inner enclosures.](figures/inner_outer.png){width=90%}

For collision absence:

$$
Sweep^+\cap O^+=\varnothing
\Rightarrow
Sweep\cap O=\varnothing.
$$

For guaranteed removal:

$$
R^-\subseteq R_{true}.
$$

For conservative remaining stock, if $S\subseteq S^+$ and $R^-\subseteq R$, then:

$$
S'=S\setminus R\subseteq S^+\setminus R^-.
$$

Thus $S'^+=S^+\setminus R^-$ is a sound outer bound on residual stock.

### Worked example: no-gouge and coverage need opposite sweeps

To prove no gouge, over-approximate the cutting sweep and show it avoids protected material. To prove required removal, under-approximate the sweep and show the required region lies inside it. One nominal sampled sweep cannot automatically support both claims.

### Counterexample: one dexel result promoted to two claims

A simulation sweeps a nominal tool through a dexel stock model and reports material removed. It receives no target part. It can detect sampled rapid-through-stock and spoilboard penetration. It cannot establish “maximum gouge into target” because the target proposition is not even defined in its inputs.

## 3.9 Robust computational geometry

### Motivation

Many geometry algorithms fail not because their distance estimates are slightly wrong, but because a floating-point sign changes a discrete decision. A segment is considered to intersect instead of miss; a polygon orientation flips; two contours connect.

### Definition: predicate and construction

A **geometric predicate** returns a discrete result: orientation, sidedness, intersection, containment, or ordering. A **geometric construction** computes coordinates or shapes.

Predicates deserve special numerical treatment because their errors change topology discontinuously.

### Orientation predicate

For 2D points $a,b,c$:

$$
orient2d(a,b,c)=
(b_x-a_x)(c_y-a_y)-(b_y-a_y)(c_x-a_x).
$$

Its sign tells whether $c$ lies left or right of directed line $ab$. Near collinearity, floating-point cancellation can produce the wrong sign. Adaptive exact predicates evaluate quickly in normal cases and increase precision near degeneracy.

### Interval arithmetic

An interval $[a,b]$ represents every real value between its endpoints. Arithmetic uses outward rounding so the exact result remains enclosed.

If:

$$
x\in[a,b],\quad y\in[c,d],
$$

then:

$$
x+y\in[a+c,b+d].
$$

Intervals can bound transforms, curve coordinates, distances, and residuals over a parameter region.

### Dependency problem

For $x\in[0,1]$, naive interval arithmetic gives:

$$
x-x\in[-1,1]
$$

although the exact value is zero. Subdivision, symbolic simplification, affine arithmetic, or Taylor models can tighten bounds. A wide interval is inconclusive, not incorrect.

### Continuous collision by branch and bound

```text
function checkInterval(path, parameterInterval I):
    P = outerBoundOfPath(path, I)
    W = outerSweep(P, toolAssembly, uncertainty)

    if W is provably disjoint from obstacles:
        return safe(I, separationBound)

    if an inner intersection is provable:
        return collision(I, counterexampleRegion)

    if I cannot be subdivided further:
        return inconclusive(I)

    split I and recurse
```

This algorithm covers the continuous domain because every parameter interval is either proved, refuted, or reported unresolved.

### Counterexample: exact arithmetic solves physical uncertainty

Exact predicates can determine the topology of the nominal mesh. They do not prove that the mesh matches the clamped workpiece, that the tool diameter is exact, or that the machine follows the commanded trajectory. Numerical robustness and model validity are separate obligations.

## 3.10 Operation ordering as operations research

### Motivation

After paths are generated, the compiler must choose an order. Nearest-neighbor ordering can reduce rapid distance but violate rough-before-finish, probe dependencies, support constraints, or tool grouping.

### Definition: precedence graph

A **precedence graph** is a directed acyclic graph $G=(V,E)$ whose vertices are operations and whose edge $(a,b)$ means $a$ must occur before $b$.

Examples:

- rough pocket before finish pocket;
- probe top surface before frame-dependent cuts;
- machine internal features before releasing surrounding stock;
- drill pilot before using a larger drill;
- finish a fragile wall only after bulk removal strategy is complete.

### State-dependent transition cost

Let $c(i,j,S)$ be the cost of moving from operation $i$ to $j$ under stock state $S$. The cost may include:

- retract and rapid time;
- tool change;
- spindle acceleration;
- probe or accessory transitions;
- risk or engagement constraints.

Because $S$ changes, this is not an ordinary static traveling-salesman problem.

### Path orientation

Each open path may have two candidate orientations. A scheduling node can be `(path, orientation, entryChoice)`. Directional process constraints may remove one orientation. The optimizer chooses among the legal states.

### Mixed-integer formulation sketch

Let binary variable $x_{ij}$ indicate that operation state $j$ follows $i$. Minimize:

$$
\sum_{i,j} c_{ij}x_{ij}
$$

subject to:

- one predecessor and successor per selected operation state;
- subtour elimination;
- one orientation per path;
- precedence constraints;
- tool and setup compatibility;
- stock-dependent feasibility.

For large jobs, exact mixed-integer optimization may be too expensive. Heuristics are acceptable if a checker verifies feasibility and recomputes objective cost.

### Counterexample: set subtraction commutes, operations commute

At the ideal stock level:

$$
(S\setminus R_1)\setminus R_2=(S\setminus R_2)\setminus R_1.
$$

It does not follow that physical operations commute. Removing $R_1$ may eliminate support needed during $R_2$, expose a safe entry, or change tool engagement. Effect summaries must include reads and dependencies, not only removed volume.

```ts
interface OperationEffects {
  readsStock: RegionSet;
  removesStock: RegionSet;
  readsMeasurements: readonly BindingId[];
  writesMeasurements: readonly BindingId[];
  requiresTool: ToolId;
  precedenceTags: readonly string[];
}
```

## 3.11 Feed scheduling and time parameterization

### Motivation

A geometric path with feed labels is not yet a physically feasible trajectory. Axis limits and curvature can require slowing down. Controller look-ahead and jerk limits affect following error and cycle time.

### Path parameterization

Given path $q(s)$ and progress $s(t)$:

$$
\dot q=q'(s)\dot s,
$$

$$
\ddot q=q''(s)\dot s^2+q'(s)\ddot s.
$$

Axis velocity limits impose:

$$
|q_i'(s)\dot s|\le v_i^{max}.
$$

Acceleration limits impose constraints on $\dot s$ and $\ddot s$.

### Curvature limit

For planar speed $v$ along curvature $\kappa$, normal acceleration is:

$$
a_n=v^2\kappa.
$$

If $a_n\le a_n^{max}$:

$$
v\le\sqrt{\frac{a_n^{max}}{\kappa}}.
$$

Sharp corners have very high or undefined curvature and require blending, stopping, or controller-specific corner handling.

### Worked example: speed on a small arc

A path contains an arc of radius 2 mm, so $\kappa=0.5\ \mathrm{mm}^{-1}$. If allowed normal acceleration is 500 mm/s²:

$$
v\le\sqrt{\frac{500}{0.5}}
=\sqrt{1000}
\approx31.6\text{ mm/s}
=1897\text{ mm/min}.
$$

A commanded feed of 2500 mm/min cannot be maintained through the arc under this simplified constraint.

### Time-optimal path parameterization

The optimization problem is:

$$
\min T
$$

subject to velocity, acceleration, jerk, torque, tracking-error, spindle, and process-force constraints. Reachability-based algorithms propagate feasible velocity intervals along the path. The planner may produce a candidate time law; an independent checker verifies all constraints on the represented intervals.

### Process constraints

Maximum machine feed is only one bound. Cutting feed also depends on:

- chip load per tooth;
- spindle RPM and flute count;
- radial and axial engagement;
- tool material and stickout;
- work material;
- machine rigidity;
- desired finish.

Many of these are empirical models or library assumptions. They should be named as such rather than presented as formal geometric guarantees.

## 3.12 Error budgets and quantitative refinement

### Motivation

The final surface differs from the nominal target for many reasons: mesh tessellation, field sampling, path approximation, coordinate rounding, frame uncertainty, tool runout, and servo following. A tolerance is meaningful only if these contributions are connected to a bound.

### Definition: error budget

An **error budget** records component bounds, metrics, frames, assumptions, and composition rules used to derive a final quantitative claim.

```ts
type ErrorBound =
  | { metric: "hausdorff-position"; frame: FrameId; value: Mm }
  | { metric: "normal-surface"; surface: Hash; value: Mm }
  | { metric: "max-gouge-depth"; target: Hash; value: Mm }
  | { metric: "transform-translation"; transform: Hash; value: Mm }
  | { metric: "transform-rotation"; transform: Hash; value: Radians }
  | { metric: "axis-following"; axis: AxisId; value: Mm };
```

Different metrics cannot be added without a conversion theorem.

### Pass sensitivity

If pass $f$ has Lipschitz or sensitivity bound $L_f$ and local approximation error $\varepsilon_f$:

$$
\varepsilon_{out}\le L_f\varepsilon_{in}+\varepsilon_f.
$$

A simple sum assumes compatible metrics and $L_f\le1$ or includes amplification separately.

### Worked example: surface budget

Suppose the pocket finish uses:

| Source | Bound |
|---|---:|
| target tessellation | 0.008 mm |
| cutter-location approximation | 0.012 mm |
| arc fitting | 0.004 mm |
| G-code rounding | 0.001 mm |
| work-frame translation | 0.010 mm |
| following error | 0.010 mm |

A conservative additive bound is:

$$
0.008+0.012+0.004+0.001+0.010+0.010=0.045\text{ mm}.
$$

![An example additive error budget.](figures/error_budget.png){width=84%}

If the feature tolerance is 0.05 mm, only 0.005 mm remains as reserve under this simplified compatible-metric model. If angular frame uncertainty contributes another 0.01 mm at the feature radius, the budget fails. Every local pass may meet its default while the composed program misses the feature tolerance.

### Worst-case versus statistical composition

Root-sum-square composition assumes an appropriate probabilistic model and independence. It is not a deterministic maximum. A certificate must identify whether a bound is:

- deterministic worst-case;
- probabilistic with a confidence level;
- empirical from calibration;
- nominal or heuristic.

### Counterexample: one scalar `totalGeometric`

Adding chord tolerance, simulation cell size, transform rotation, and scallop height into one number erases metrics and propagation. The sum may be useful as a warning dashboard but cannot support a precise theorem until conversions are justified.

## 3.13 Complete worked planning example

We now plan the running pocket with a 6 mm flat end mill for roughing and the same tool for finishing.

### Step 1: normalize intent

- Stock: 60 mm by 40 mm by 8 mm.
- Pocket footprint: $[15,45]\times[10,30]$ mm.
- Final floor: $z=-4$ mm.
- Roughing allowance: 0.2 mm radial and axial.
- Final tolerance: 0.05 mm.
- Roughing stepdown: 1.5 mm.
- Roughing stepover: 40% of diameter = 2.4 mm.

### Step 2: compute center regions

The roughing wall is left 0.2 mm heavy, so the cutter center stays at least:

$$
r+0.2=3.2\text{ mm}
$$

inside the final boundary. The first roughing loop uses a 23.6 mm by 13.6 mm centerline rectangle. Inward loops are spaced 2.4 mm.

### Step 3: choose depth levels

Leave 0.2 mm on the floor. Roughing depth is 3.8 mm:

$$
-1.5,\quad -3.0,\quad -3.8.
$$

### Step 4: choose entry

A 3-degree ramp requires about 28.6 mm per 1.5 mm drop, which is possible along the long dimension only with a carefully placed zig-zag. A helix of centerline radius 1.5 mm needs a clear circular region plus tool radius. The planner proposes a helix near the pocket center and supplies a continuous-clearance witness. If the checker cannot prove clearance, it tries a certified ramp or rejects the automatic entry.

### Step 5: generate roughing loops

At each depth, generate inward offsets until a coverage checker shows the remaining center region lies within the tool sweep. Preserve climb-milling orientation. Record which center-region band each loop covers.

### Step 6: plan links

Within one cleared layer, short stay-down links may be safe. Between depth levels, a descent is cutting motion and must stay inside already cleared XY space. Between roughing and finishing, link safety is checked against the roughing residual stock, not the final pocket.

### Step 7: finish

The wall finish follows the final centerline offset 3.0 mm from the pocket boundary at full depth. The floor finish covers the floor at $z=-4.0$ with a small stepover chosen from flat-tool coverage and finish requirements. The finish paths reference the final target and tolerance claims.

### Step 8: schedule

Precedence:

```text
rough level 1
  -> rough level 2
  -> rough level 3
  -> wall finish
  -> floor finish
  -> retract and spindle stop
```

Alternative wall/floor order can be considered if process effects prove independence. A nearest-neighbor heuristic cannot violate the graph.

### Step 9: parameterize

Start with material-library feed assumptions, then limit by machine feed, acceleration, curvature, and entry constraints. Attach empirical assumptions separately from machine-feasibility proofs.

### Step 10: emit witness bundle

The planner returns:

- path artifacts;
- offset and coverage correspondences;
- entry and link clearance evidence requests;
- depth and stepover records;
- precedence graph;
- stock-state sequence;
- error contributions;
- provenance.

Chapter 4 explains how these objects become checked claims rather than optimistic metadata.

## Exercises

### Cutter-location geometry

1. Derive the flat-tool cutter-location formula for a height field.
2. For a ball radius of 4 mm and target point 2 mm from the axis at height 5 mm, compute the legal tip height caused by that point.
3. Explain why vertex-only triangle contact is insufficient.
4. Design a spatial-index node bound for a flat end mill.
5. State what extra geometry is needed to model a bull-nose cutter.

### Sampling and topology

6. Compute the number and memory size of field samples for a 100 mm by 80 mm region at 0.2, 0.05, and 0.01 mm spacing.
7. Construct a narrow feature missed by a regular grid and explain what additional bound would make sampling sound.
8. Draw all 16 marching-squares sign cases and identify the two saddle cases.
9. Explain why exact grid-edge IDs are superior to coordinate quantization for chaining.
10. Find two X coordinates in a 150 mm work envelope that collide under a modulo period of 67.108864 mm.

### Pocket and finishing calculations

11. For a 4 mm cutter and 35% stepover, compute the lateral spacing.
12. Plan depth levels for a 7.2 mm pocket, 2 mm maximum stepdown, and 0.15 mm floor allowance.
13. Compute ramp length for 2 mm depth at 2.5 degrees.
14. Derive the exact ball-tool scallop-spacing formula from a circle cross-section.
15. Compute spacing for $R=2$ mm and $h=0.005$ mm.
16. Explain why a planar scallop formula is not sufficient on a sharply curved surface.

### Clearance and stock

17. State separate set predicates for tool gouge, holder collision, rapid-through-stock, and guaranteed removal.
18. Compare height fields, dexels, triple dexels, and voxels for a three-axis pocket and for an undercut part.
19. Design a stock-state identifier scheme for scheduled links.
20. Give a case where a final-stock link check passes but the execution-time link collides.
21. Write pseudocode for an adaptive continuous collision checker.

### Operations research and dynamics

22. Construct a precedence DAG for roughing, drilling, probing, and finishing a part.
23. Formulate a small path-orientation scheduling problem with binary variables.
24. Give two operations whose removed volumes are disjoint but whose physical order still matters.
25. Compute curvature-limited speed for radius 5 mm and normal acceleration 300 mm/s².
26. Explain the difference between a feasible schedule, an optimal schedule, and a schedule with a certified optimality gap.

### Error reasoning

27. Build a typed error budget for the pocket wall. Identify which bounds are compile-time, calibration-time, and runtime.
28. Give an example where a pass amplifies input error with $L>1$.
29. Explain why root-sum-square composition does not prove a worst-case tolerance.
30. Design an adaptive refinement policy that returns `inconclusive` rather than silently accepting an unresolved cell.
EOF
python - <<'PY'
from pathlib import Path
p=Path('/mnt/data/z1_pedagogical_textbook_work/book/draft_v1.md')
print('through chapter3:',len(p.read_text().split()),'words',p.stat().st_size,'bytes')
PY
```

<details><summary>💭 Thinking</summary>

**Drafted CAM geometry textbook and developed assurance architecture**

</details>

```unknown
bash -lc python - <<'PY'
from pathlib import Path
import re
p=Path('/mnt/data/z1_pedagogical_textbook_work/book/draft_v1.md')
s=p.read_text()
chapters=re.split(r'(?m)^# (?!Preface)(.+)$',s)
# pairs title/content after front parts; print pedagogical markers
for i in range(1,len(chapters),2):
    title=chapters[i].strip(); body=chapters[i+1]
    if title in {'References {-}','Glossary'}: continue
    print('\n',title)
    for marker in ['### Motivation','### Definition','### Worked example','### Counterexample','> **Fundamental idea','> **Design consequence','## Exercises']:
        print(f'{marker:28s}',body.count(marker))
# likely first-use terms/locations
terms=['refinement','Hausdorff','metric','topology','Minkowski','morphological','power set','relation','cyber-physical','abstraction','configuration space','Lipschitz','widening','fixed point','commutativity','conservative','proof-carrying','state epoch']
lines=s.splitlines()
print('\nFirst uses:')
for term in terms:
    for n,l in enumerate(lines,1):
        if term.lower() in l.lower():
            print(f'{term:20s} {n:5d}: {l[:100]}')
            break
PY
printf '\n--- headings ---\n'
rg -n '^#{1,4} ' /mnt/data/z1_pedagogical_textbook_work/book/draft_v1.md | sed -n '1,280p'
```

<details><summary>💭 Thinking</summary>

**Audited textbook pedagogy and reviewed CAM compiler revisions**

**Revising the textbook**

I’m revising the draft into four coherent chapters, strengthening motivation, definitions, worked examples, counterexamples, exercises, diagrams, mathematics, APIs, pseudocode, and appendices before producing Markdown and PDF deliverables.

**Expanding the revision**

I’m repairing the failed revision pipeline, adding missing prerequisite definitions, appendices, selected solutions, a glossary, references, and reproducibility notes, then I’ll inspect the finished Markdown and PDF for coherence.

**Revised and expanded the textbook content**

</details>

```unknown
bash -lc ls -lah /mnt/data/z1_pedagogical_textbook_work/book && sed -n '1,220p' /mnt/data/z1_pedagogical_textbook_work/book/revise_pedagogy.py && printf '\n--- draft head ---\n' && sed -n '1,180p' /mnt/data/z1_pedagogical_textbook_work/book/draft_v1.md
```

<details><summary>💭 Thinking</summary>

**Inspected and patched textbook revision scripts, headings, structure, and word counts**

</details>

```unknown
bash -lc cd /mnt/data/z1_pedagogical_textbook_work/book
rg -n 'multi-level|IR ladder|Abstract interpretation|Cousot|configuration space|proof-carrying|NIST|CompCert|Translation validation' draft_v2.md | sed -n '1,200p'
```

<details><summary>💭 Thinking</summary>

**Patched and audited textbook draft content, appendices, references, and definitions**

</details>

```unknown
bash -lc set -o pipefail
cd /mnt/data/z1_pedagogical_textbook_work/book
pandoc From_Intent_to_Motion.md \
  --from=markdown+raw_tex \
  --pdf-engine=xelatex \
  --top-level-division=chapter \
  --resource-path=. \
  --highlight-style=tango \
  -o From_Intent_to_Motion.pdf 2>&1 | tee /mnt/data/z1_pedagogical_textbook_work/pandoc.log
status=${PIPESTATUS[0]}
exit $status
```

<details><summary>💭 Thinking</summary>

**Rendered and inspected Pandoc PDF with corrected symbols and link colors**

</details>

```unknown
bash -lc rm -rf /mnt/data/z1_pedagogical_textbook_work/renders && mkdir -p /mnt/data/z1_pedagogical_textbook_work/renders
python /home/oai/skills/pdfs/scripts/render_pdf.py \
  /mnt/data/z1_pedagogical_textbook_work/book/From_Intent_to_Motion.pdf \
  --out_dir /mnt/data/z1_pedagogical_textbook_work/renders \
  --dpi 130
printf 'rendered: '; find /mnt/data/z1_pedagogical_textbook_work/renders -maxdepth 1 -name '*.png' | wc -l
ls -lh /mnt/data/z1_pedagogical_textbook_work/renders | sed -n '1,12p'
```

<details><summary>💭 Thinking</summary>

**Rendered, inspected, patched, and validated textbook PDF layout**

</details>

```unknown
bash -lc set -euo pipefail
WORK=/mnt/data/z1_pedagogical_textbook_work/book
OUT=/mnt/data/from_intent_to_motion_deliverables
BUNDLE=/mnt/data/z1_pedagogical_textbook_work/source_bundle/From_Intent_to_Motion
rm -rf "$OUT" /mnt/data/z1_pedagogical_textbook_work/source_bundle
mkdir -p "$OUT" "$BUNDLE/figures" "$BUNDLE/figure_sources"
cp "$WORK/From_Intent_to_Motion.md" "$OUT/From_Intent_to_Motion.md"
cp "$WORK/From_Intent_to_Motion.pdf" "$OUT/From_Intent_to_Motion.pdf"
cp "$WORK/From_Intent_to_Motion.md" "$BUNDLE/"
cp "$WORK"/figures/*.png "$BUNDLE/figures/"
cp "$WORK"/figure_sources/* "$BUNDLE/figure_sources/"
cat > "$BUNDLE/build.sh" <<'EOF'
#!/usr/bin/env bash
set -euo pipefail
pandoc From_Intent_to_Motion.md \
  --from=markdown+raw_tex \
  --pdf-engine=xelatex \
  --top-level-division=chapter \
  --resource-path=. \
  --highlight-style=tango \
  -o From_Intent_to_Motion.pdf
EOF
chmod +x "$BUNDLE/build.sh"
cat > "$BUNDLE/README.md" <<'EOF'
# From Intent to Motion — source bundle

This bundle contains the canonical Markdown source, rendered diagram assets, diagram source files, and the PDF build script.

## Build requirements

- Pandoc
- XeLaTeX / TeX Live
- Linux Libertine O
- Linux Biolinum O
- DejaVu Sans Mono
- LaTeX packages named in the Markdown YAML header

## Build

Run from this directory:

```bash
./build.sh
```

Most architecture diagrams are generated from the Graphviz `.dot` files under `figure_sources/`. The remaining figures are generated by the Python script in that directory.
EOF
cd /mnt/data/z1_pedagogical_textbook_work/source_bundle
zip -X -r "$OUT/From_Intent_to_Motion_Source.zip" From_Intent_to_Motion >/tmp/from_intent_zip.log
zip -T "$OUT/From_Intent_to_Motion_Source.zip"
cd "$OUT"
sha256sum From_Intent_to_Motion.md From_Intent_to_Motion.pdf From_Intent_to_Motion_Source.zip > SHA256SUMS.txt
ls -lh "$OUT"
cat SHA256SUMS.txt
```

<details><summary>💭 Thinking</summary>

**Packaged textbook deliverables and source bundle**

</details>

The four-chapter draft is now fully revised and audited, including missing first-use foundations and substantive exercise solutions. Final checks pass on the 149-page edition; I’m packaging reproducible sources.

# From Intent to Motion

The textbook has been rewritten from the ground up as a coherent **four-chapter pedagogical progression**, rather than a collection of loosely connected technical chapters.

The final edition is **149 pages** and approximately **32,600 words**. It uses one running pocket-machining example throughout, so each new abstraction is tied to a concrete manufacturing problem.

## Structure

1. **Meaning Before Syntax**  
   Develops manufacturing intent, machine and stock state, units, frames, paths, trajectories, swept volumes, canonical actions, denotational and operational semantics, Hoare logic, invariants, temporal behavior, and the end-to-end correctness statement.

2. **Languages, Intermediate Representations, and Compiler Passes**  
   Introduces staged JavaScript authoring, inert ASTs, elaboration, the complete IR ladder, categorical path composition, monads and Kleisli composition, typestate, SSA state tokens, compiler-pass contracts, provenance, translation validation, and API design.

3. **Geometry, Planning, and Optimization**  
   Covers cutter-location geometry, sampled fields, Lipschitz bounds, contour topology, pocket offsets, Minkowski operations, entries, three-dimensional finishing, configuration-space linking, stock representations, robust predicates, interval arithmetic, scheduling, feed parameterization, and quantitative error budgets.

4. **Certificates, Validation, and Runtime Assurance**  
   Distinguishes testing, simulation, verification, and attestation; develops assertions and invariants, abstract interpretation, proof-producing passes, geometric certificates, certificate DAGs, trusted checkers, final-byte validation, controller state machines, state-epoch authorization, runtime assurance, and a concrete Dropcut/Z1 migration plan.

The second pedagogical pass specifically repaired definitions that were previously assumed or introduced too late, including refinement, behaviors, predicates, relations, metrics, Hausdorff distance, categories and groupoids, topology, Minkowski sums and erosion, configuration spaces, conservative inner and outer approximations, fixed points, widening, state epochs, and operations research.

Each major concept now follows the sequence:

```text
motivation
→ definition
→ worked application
→ counterexample or limitation
→ exercises
```

The appendices provide a mathematical toolkit, consolidated TypeScript APIs, checker pseudocode, selected exercise solutions, a glossary, and 30 primary references.

## Files

- [Download the Markdown textbook](sandbox:/mnt/data/from_intent_to_motion_deliverables/From_Intent_to_Motion.md)
- [Download the 149-page PDF textbook](sandbox:/mnt/data/from_intent_to_motion_deliverables/From_Intent_to_Motion.pdf)
- [Download the complete source bundle](sandbox:/mnt/data/from_intent_to_motion_deliverables/From_Intent_to_Motion_Source.zip)
- [Download SHA-256 checksums](sandbox:/mnt/data/from_intent_to_motion_deliverables/SHA256SUMS.txt)

The source bundle includes the canonical Markdown, all rendered diagrams, Graphviz and Python figure sources, and a reproducible Pandoc/XeLaTeX build script.

