# Branch · Branch · CLIM UI in React

- URL: https://chatgpt.com/c/6a714116-9374-83ea-8189-d9e85b40478c
- Created: 2026-08-04T01:32:47.621Z

---

> This is my attempt at a presentation based UI / common lisp CLIM system in react / JS. 
>
> But I feel there's quite a bit of flexibility around how to define action / action selectors / presentations / object identity|type that is present in Common Lisp and not in the Javascript, or other things in the UI setup that could be made more powerful to enable things like:
>
> linking a tile to presnt the same data object than another (for example, the pipeline view and the chart view to be linked, so that switching the document in one switches it in the other. 
>
> Or allowing arbitrary lambdas to be passed to refine what can be selected or not (and doing so with performance in mind), things like that.
>
> Make a deep analysis and write a detailed markdown document (that also goes into all the details of presentation based UIs, common lisp CLIM patterns, for a newcomer, in a textbook writing style). Also implement the ideas so I can have a first time experience with them.

<details><summary>💭 Thinking</summary>

**Inspecting project structure**

I’ll examine the archive, map the existing architecture, and identify extension points before changing anything. I’m also checking relevant Common Lisp IM conventions so the design fits the project rather than layering on unrelated abstractions.

**Inspected project structure**

</details>

I’ll inspect the project’s structure, runtime, and presentation/action data flow, then implement a coherent CLIM-inspired object-linking and selector layer with a runnable demo and textbook-style guide.

```unknown
bash -lc set -euo pipefail
ls -lah /mnt/data
file /mnt/data/pbui.zip
unzip -l /mnt/data/pbui.zip | sed -n '1,220p'
```

<details><summary>💭 Thinking</summary>

**Inspected project archives and compared PBUI source implementations**

</details>

```unknown
bash -lc cd /mnt/data/pbui_work/pbui
printf '%s\n' '--- README ---'
nl -ba README.md | sed -n '1,320p'
printf '%s\n' '--- datalab README ---'
nl -ba packages/datalab-ui/README.md | sed -n '1,320p'
printf '%s\n' '--- GUIDELINES headings ---'
rg -n '^#{1,4} ' packages/datalab-ui/GUIDELINES.md docs/playbooks/adding-editing-support-to-a-pbui-application.md
printf '%s\n' '--- layout and view symbol inventory ---'
rg -n --glob '*.{ts,tsx,proto,json,md}' '\b(View|view|Placement|placement|docId|activeDocId|linked|linkGroup|subject|selection|binding)\b' packages/datalab-ui/src/store packages/datalab-ui/src/layout packages/datalab-ui/src/components packages/datalab-ui/src/apps proto contracts/workbench/v1 | sed -n '1,560p'
```

<details><summary>💭 Thinking</summary>

**Checking pnpm and Corepack availability**

</details>

```json
{"search_query":[{"q":"Common Lisp Interface Manager II specification presentation types translators accept values official"},{"q":"McCLIM manual presentations presentation translators command tables official"},{"q":"CLIM 2 specification incremental redisplay output records official"},{"q":"Common Lisp Interface Manager paper presentation based user interfaces PDF"}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Reviewing implementation options**

I’m narrowing the design around presentation-type relationships, identity management, matching, translators, commands, cross-view links, and performance. I’ll verify the repository’s current abstractions before deciding which improvements fit cleanly.

**Reviewed implementation options**

**Modeling linked views**

I’m comparing synchronized document IDs with a centralized link-group source of truth. I’m leaning toward group bindings plus compatibility materialization, so existing app APIs keep working while coordinated updates avoid drift.

**Modeled linked views**

**Designing link actions**

I’m planning a discoverable linking flow: a document bar action selects another view, merges or creates a link group, and synchronizes the chosen document role without disrupting existing view data.

**Designed link actions**

</details>

The existing architecture cleanly separates domain-neutral PBUI, Datalab descriptors, logical views, and placements. I’m now isolating identity, eligibility, applicability, conversion, and shareable subject bindings as distinct protocols.

<details><summary>💭 Thinking</summary>

**Searched 22 websites**

</details>

```unknown
bash -lc cd /mnt/data/pbui_work/pbui
nl -ba proto/hyperslop/pbui/workbench/v1/workbench.proto | sed -n '1,420p'
printf '\n--- remote codec view lines ---\n'
nl -ba packages/datalab-ui/src/remote/codec.ts | sed -n '170,300p'
printf '\n--- persist view validation/serialization ---\n'
nl -ba packages/datalab-ui/src/store/persist.ts | sed -n '1,260p'
printf '\n--- protocol package tree ---\n'
find packages/workbench-protocol -maxdepth 4 -type f | sort | sed -n '1,220p'
```

<details><summary>💭 Thinking</summary>

**Implementing design direction**

I’m consolidating the practical path: preserve existing protocols, add centralized link-group utilities, expose linking through document-bar selection, and document the tradeoffs, performance boundaries, and future schema evolution.

**Executing the implementation**

I’m extending the generic layer with semantic identity, subtype-aware matching, typed translators, selectors, and action rules. Then I’m integrating document link groups, first-time linking UI, tests, and a detailed design document.

**Implemented design direction**

</details>

```unknown
bash -lc find /mnt/data/pbui_work/pbui -maxdepth 3 -type f | sed 's#^/mnt/data/pbui_work/pbui/##' | sort | head -200
```

<details><summary>💭 Thinking</summary>

**Checking Git repository status**

</details>

```unknown
bash -lc printf '%s\n' '--- pbui types ---'; sed -n '1,300p' packages/datalab-ui/src/pbui/types.ts; printf '%s\n' '--- pbui runtime ---'; sed -n '1,360p' packages/datalab-ui/src/pbui/runtime.tsx; printf '%s\n' '--- pbui registry ---'; sed -n '1,360p' packages/datalab-ui/src/pbui/registry.ts; printf '%s\n' '--- pbui index ---'; sed -n '1,260p' packages/datalab-ui/src/pbui/index.ts; printf '%s\n' '--- layout ---'; sed -n '1,460p' packages/datalab-ui/src/store/layout.ts
```

<details><summary>💭 Thinking</summary>

**Inspected Datalab UI layouts, components, reducers, tests, configuration, and documentation style**

</details>

```json
{"open":[{"ref_id":"turn272931search1"},{"ref_id":"turn272931search0"},{"ref_id":"turn272931search17"},{"ref_id":"turn272931search4"},{"ref_id":"turn272931search28"}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Searched 3 websites**

</details>

```unknown
bash -lc grep -R "message AppView" -n proto packages/workbench-protocol pkg | head -20; sed -n '1,240p' proto/hyperslop/pbui/workbench/v1/workbench.proto 2>/dev/null || true; find packages/workbench-protocol/src -type f -maxdepth 4 | head -20
```

The concrete design adds compiled predicates, revision-aware semantic identity, typed translators, and scoped action selectors. Selection becomes a linkable semantic object supporting heterogeneous views, unlinking, persistence, and selective subscriptions.

<details><summary>💭 Thinking</summary>

**Updating exports for presentationSelector and TileRef**

</details>

```unknown
bash -lc sed -n '1,420p' packages/datalab-ui/src/store/persist.ts; printf '\n--- bundles 1 ---\n'; sed -n '1,390p' packages/datalab-ui/src/store/bundles.ts; printf '\n--- portable model ---\n'; sed -n '1,220p' packages/datalab-ui/src/model/portable.ts; printf '\n--- remote codec views ---\n'; sed -n '120,260p' packages/datalab-ui/src/remote/codec.ts
```

<details><summary>💭 Thinking</summary>

**Finalizing changes**

I’m finishing the linked-view integration, validating modified TypeScript and documentation, then packaging the updated project while clearly separating verified checks from anything blocked by unavailable dependencies.

**Finalized changes**

</details>

```unknown
bash -lc pwd && ls -la /mnt/data/pbui_work/pbui && git -C /mnt/data/pbui_work/pbui status --short 2>/dev/null || true
```

<details><summary>💭 Thinking</summary>

**Implemented and inspected portable subject-link support across layouts and bundles**

</details>

```unknown
bash -lc cd /mnt/data/pbui_work/pbui && nl -ba packages/datalab-ui/src/store/bundles.ts | sed -n '1,520p' && nl -ba packages/datalab-ui/src/store/bundles.ts | sed -n '521,1040p'
```

<details><summary>💭 Thinking</summary>

**Inspecting Project Documentation and READMEs**

</details>

```json
{"search_query":[{"q":"McCLIM User Manual presentations input contexts presentation translators command tables official"},{"q":"Common Lisp Interface Manager CLIM II Specification presentation translators input contexts official"},{"q":"LispWorks CLIM User Guide presentation translators incremental redisplay"}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Searched 16 websites**

</details>

```unknown
bash -lc cd /mnt/data/pbui_work/pbui && rg -n "\.accept\(|accept\(\{|AcceptRequest|conversions|createPresentationRegistry|Presentation\s+reference|type: \"(field|cat|tile)\"" src packages/datalab-ui/src packages/datalab-ui/test | sed -n '1,320p'
```

<details><summary>💭 Thinking</summary>

**Checking npm cache packages**

</details>

```unknown
bash -lc corepack pnpm --version
```

<details><summary>💭 Thinking</summary>

**Wrapping up validation**

I’m correcting the remaining type-narrowing and generic-inference issues, then I’ll run the strongest available static checks and package the repository with documentation and implementation notes.

</details>

```unknown
bash -lc sed -n '1,240p' src/presentation/registry.ts && printf '\n--- selectors ---\n' && sed -n '1,240p' src/presentation/selectors.ts && printf '\n--- createPbui relevant ---\n' && sed -n '90,180p' src/presentation/createPbui.tsx
```

<details><summary>💭 Thinking</summary>

**Inspected configuration, registries, selectors, tests, documentation, and fixed type safety issues**

</details>

```unknown
bash -lc rm -rf /tmp/pbui-typecheck && mkdir -p /tmp/pbui-typecheck && cat > /tmp/pbui-typecheck/stubs.d.ts <<'EOF'
declare module "react" {
  export type ReactNode = unknown;
}
declare module "vitest" {
  export const describe: (name: string, fn: () => void) => void;
  export const test: (name: string, fn: () => void) => void;
  export const expect: (value: unknown) => {
    toBe(value: unknown): void;
    toEqual(value: unknown): void;
    toBeUndefined(): void;
    toBeNull(): void;
    toContain(value: unknown): void;
    toHaveLength(value: number): void;
    toThrow(value?: unknown): void;
    toMatchObject(value: unknown): void;
    not: { toBe(value: unknown): void };
  };
}
EOF
cat > /tmp/pbui-typecheck/tsconfig.json <<'EOF'
{
  "compilerOptions": {
    "target": "ES2022",
    "lib": ["ES2022", "DOM"],
    "module": "ESNext",
    "moduleResolution": "bundler",
    "strict": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "verbatimModuleSyntax": true,
    "skipLibCheck": true,
    "types": []
  },
  "files": [
    "/tmp/pbui-typecheck/stubs.d.ts",
    "/mnt/data/pbui_work/pbui/src/presentation/types.ts",
    "/mnt/data/pbui_work/pbui/src/presentation/registry.ts",
    "/mnt/data/pbui_work/pbui/src/presentation/selectors.ts",
    "/mnt/data/pbui_work/pbui/src/presentation/registry.test.ts",
    "/mnt/data/pbui_work/pbui/src/presentation/selectors.test.ts"
  ]
}
EOF
tsc -p /tmp/pbui-typecheck/tsconfig.json --noEmit --pretty false
```

Shared-document linking now works end-to-end, including deterministic merging, unlinking, duplication, and portable serialization. Strict typing and runtime assertions validate memoization, subtype matching, and cost-based conversions.

<details><summary>💭 Thinking</summary>

**Implemented semantic selectors, type checks, imports, caching, and safe supertype aliases**

</details>

```json
{"search_query":[{"q":"site:franz.com/support/documentation CLIM presentation types presentation translators command tables input context accept official"},{"q":"site:lispworks.com/documentation/HyperSpec Common Lisp generic functions method dispatch official"},{"q":"site:mcclim.common-lisp.dev manual presentation type parameters accept presentation translator command table"},{"q":"site:lispworks.com/documentation/lw80/clim presentation type inheritance parameters accept input context"}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Searched 3 websites**

</details>

```unknown
bash -lc python - <<'PY'
from pathlib import Path
p=Path('src/presentation/selectors.test.ts')
s=p.read_text()
needle='''  test("identity caching stays strict when a descriptor has no semantic identity", () => {'''
insert='''  test("identity caching re-materializes a translated candidate but reuses the tester decision", () => {\n    let translatorCalls = 0;\n    let testerCalls = 0;\n    const translatedRegistry = createPresentationRegistry<Values, Environment, Verb>(\n      {\n        projectId: {\n          label: (projectId) => projectId,\n          identity: (projectId) => ({ namespace: "project", key: projectId }),\n        },\n        project: {\n          label: (project) => project.title,\n        },\n      },\n      {\n        translators: [\n          {\n            id: "project-id-to-current-project",\n            from: "projectId",\n            to: "project",\n            translate: (projectId, env) => {\n              translatorCalls += 1;\n              return env.projects[projectId];\n            },\n          },\n        ],\n      },\n    );\n    const compiled = compilePresentationSelector(\n      createPresentationSelector<Values, Environment>("project", {\n        cache: "identity",\n        where: () => {\n          testerCalls += 1;\n          return true;\n        },\n      }),\n      translatedRegistry,\n      environment,\n    );\n\n    expect(compiled.accept({ type: "projectId", value: "project-1" })).toEqual({\n      type: "project",\n      value: environment.projects["project-1"],\n    });\n    expect(compiled.accept({ type: "projectId", value: "project-1" })).toEqual({\n      type: "project",\n      value: environment.projects["project-1"],\n    });\n    expect(translatorCalls).toBe(2);\n    expect(testerCalls).toBe(1);\n  });\n\n'''
if needle not in s: raise SystemExit('needle missing')
s=s.replace(needle, insert+needle)
p.write_text(s)
PY
tsc -p /tmp/pbui-typecheck/tsconfig.json --noEmit --pretty false
```

<details><summary>💭 Thinking</summary>

**Completing validation**

I’m adding focused tests for link normalization, remote conflict handling, and portable import behavior. Then I’ll rerun the available static checks and package the finished implementation with its design documentation.

**Completed validation**

</details>

```unknown
bash -lc pwd && find /mnt/data/pbui_work/pbui -maxdepth 3 -type f | sed 's#^/mnt/data/pbui_work/pbui/##' | sort | head -200
```

<details><summary>💭 Thinking</summary>

**Implemented and tested project selectors, layout normalization, and conflict handling**

</details>

```unknown
bash -lc cd /mnt/data/pbui_work/pbui && apply_patch <<'PATCH'
*** Begin Patch
*** Update File: src/presentation/Pbui.stories.tsx
@@
-import { useState, type CSSProperties } from "react";
+import { useMemo, useState, type CSSProperties } from "react";
 import { createPbui } from "./createPbui";
 import { createPresentationRegistry } from "./registry";
+import type { PresentationReference } from "./types";
@@
 export const TwoIsolatedProviders: Story = {
@@
   ),
 };
+
+/* ---------------------------------------------------------- concepts lab -- */
+
+interface LabEntity {
+  id: string;
+}
+
+interface LabProject extends LabEntity {
+  title: string;
+  owner: string;
+  archived: boolean;
+  revision: number;
+}
+
+interface LabValues {
+  entity: LabEntity;
+  project: LabProject;
+  projectId: string;
+}
+
+interface LabEnvironment {
+  projects: Record<string, LabProject | undefined>;
+  currentUserId: string;
+  canArchive: boolean;
+}
+
+type LabVerb =
+  | { type: "openProject"; projectId: string }
+  | { type: "inspectEntity"; entityId: string }
+  | { type: "archiveProject"; projectId: string }
+  | { type: "copyProjectId"; projectId: string };
+
+function projectFromReference(
+  reference: PresentationReference<LabValues>,
+  environment: LabEnvironment,
+): LabProject | undefined {
+  if (reference.type === "project") return reference.value;
+  if (reference.type === "projectId") return environment.projects[reference.value];
+  return environment.projects[reference.value.id];
+}
+
+function entityIdFromReference(reference: PresentationReference<LabValues>): string {
+  return reference.type === "projectId" ? reference.value : reference.value.id;
+}
+
+const labRegistry = createPresentationRegistry<LabValues, LabEnvironment, LabVerb>(
+  {
+    entity: {
+      label: (entity) => entity.id,
+      identity: (entity) => ({ namespace: "project", key: entity.id }),
+    },
+    project: {
+      label: (project) => project.title,
+      describe: (project) => ({
+        id: project.id,
+        owner: project.owner,
+        archived: project.archived,
+        revision: project.revision,
+      }),
+      identity: (project) => ({ namespace: "project", key: project.id }),
+      revision: (project) => project.revision,
+      tone: "positive",
+      actions: (project) => [
+        {
+          id: "open",
+          label: "Open project",
+          description: "A descriptor-local action; it is available in every action scope.",
+          verb: { type: "openProject", projectId: project.id },
+        },
+      ],
+    },
+    projectId: {
+      label: (projectId) => `#${projectId}`,
+      identity: (projectId) => ({ namespace: "project", key: projectId }),
+      revision: (projectId, environment) =>
+        environment.projects[projectId]?.revision ?? 0,
+      tone: "accent",
+      actions: (projectId) => [
+        {
+          id: "copy-id",
+          label: "Copy project id",
+          verb: { type: "copyProjectId", projectId },
+        },
+      ],
+    },
+  },
+  {
+    // A project can satisfy an input context asking for an entity without any
+    // conversion because its JavaScript representation is structurally safe.
+    supertypes: { project: "entity" },
+    translators: [
+      {
+        id: "project-id-to-project",
+        from: "projectId",
+        to: "project",
+        priority: 10,
+        tester: (projectId, environment) => environment.projects[projectId] !== undefined,
+        translate: (projectId, environment) => environment.projects[projectId],
+      },
+    ],
+    actionTables: [
+      { id: "workspace", parents: ["global"] },
+      { id: "admin", parents: ["workspace"] },
+    ],
+    actionSelectors: [
+      {
+        id: "inspect-entity",
+        from: "entity",
+        table: "workspace",
+        actions: (reference) => [
+          {
+            id: "inspect",
+            label: "Inspect semantic entity",
+            description: "Contributed by the inherited workspace action table.",
+            verb: {
+              type: "inspectEntity",
+              entityId: entityIdFromReference(reference),
+            },
+          },
+        ],
+      },
+      {
+        id: "archive-project",
+        from: "project",
+        table: "admin",
+        tester: (reference, environment) => {
+          const project = projectFromReference(reference, environment);
+          return environment.canArchive && project !== undefined && !project.archived;
+        },
+        actions: (reference, environment) => {
+          const project = projectFromReference(reference, environment);
+          return project
+            ? [
+                {
+                  id: "archive",
+                  label: "Archive project",
+                  description: "Contributed only when the admin action table is active.",
+                  danger: true,
+                  verb: { type: "archiveProject", projectId: project.id },
+                },
+              ]
+            : [];
+        },
+      },
+    ],
+  },
+);
+
+const labPbui = createPbui({
+  registry: labRegistry,
+  defaultEnvironment: {
+    projects: {},
+    currentUserId: "person-1",
+    canArchive: false,
+  },
+  defaultActionTables: ["workspace"],
+});
+
+const INITIAL_LAB_PROJECTS: LabProject[] = [
+  {
+    id: "compiler",
+    title: "Incremental compiler",
+    owner: "person-1",
+    archived: false,
+    revision: 1,
+  },
+  {
+    id: "renderer",
+    title: "Presentation renderer",
+    owner: "person-2",
+    archived: false,
+    revision: 3,
+  },
+  {
+    id: "archive",
+    title: "Archived prototype",
+    owner: "person-1",
+    archived: true,
+    revision: 8,
+  },
+];
+
+function LabSurface({ projects }: { projects: readonly LabProject[] }) {
+  const pbui = labPbui.usePbui();
+  const [accepted, setAccepted] = useState<PresentationReference<LabValues> | null>(null);
+
+  const acceptActiveOwnedProject = async () => {
+    const result = await pbui.accept({
+      selector: labPbui.selector("project", {
+        id: "active-owned-project",
+        description: "a non-archived project owned by the current user",
+        cache: "identity",
+        where: (reference, context) =>
+          reference.type === "project" &&
+          !reference.value.archived &&
+          reference.value.owner === context.environment.currentUserId,
+      }),
+      prompt:
+        "Choose a non-archived project owned by person-1. Either its card or its id token can satisfy this request.",
+    });
+    setAccepted(result);
+  };
+
+  const first = projects[0];
+  const sameObject = first
+    ? labRegistry.sameObject(
+        { type: "project", value: first },
+        { type: "projectId", value: first.id },
+        pbui.environment,
+      )
+    : false;
+
+  return (
+    <div
+      style={{
+        display: "grid",
+        gap: "1rem",
+        padding: "1.5rem",
+        maxWidth: "1100px",
+        margin: "0 auto",
+      }}
+    >
+      <header style={{ display: "grid", gap: "0.35rem" }}>
+        <h2 style={{ margin: 0 }}>CLIM concepts lab</h2>
+        <p style={{ margin: 0 }}>
+          Start the input context, then select a highlighted presentation. Right-click any
+          presentation to inspect its action table.
+        </p>
+      </header>
+
+      <section
+        style={{
+          display: "grid",
+          gap: "0.75rem",
+          padding: "1rem",
+          border: "1px solid currentColor",
+          borderRadius: "0.5rem",
+        }}
+      >
+        <div style={{ display: "flex", gap: "0.5rem", flexWrap: "wrap" }}>
+          <button type="button" disabled={pbui.accepting !== null} onClick={acceptActiveOwnedProject}>
+            Accept an active owned project
+          </button>
+          {pbui.accepting && (
+            <button type="button" onClick={pbui.abortAccept}>
+              Abort input context
+            </button>
+          )}
+        </div>
+        <output>
+          {pbui.accepting
+            ? `INPUT CONTEXT — ${pbui.accepting.prompt}`
+            : accepted
+              ? `ACCEPTED — <${accepted.type}> ${labRegistry.labelFor(accepted, pbui.environment)}`
+              : "No input context is active."}
+        </output>
+      </section>
+
+      <section style={{ display: "grid", gap: "0.75rem" }}>
+        {projects.map((project) => {
+          const projectReference = { type: "project", value: project } as const;
+          const idReference = { type: "projectId", value: project.id } as const;
+          return (
+            <article
+              key={project.id}
+              style={{
+                display: "grid",
+                gridTemplateColumns: "minmax(18rem, 1fr) minmax(12rem, auto)",
+                gap: "0.75rem",
+                alignItems: "stretch",
+              }}
+            >
+              <labPbui.Presentation
+                block
+                reference={projectReference}
+                doc={`<project> ${project.title}`}
+              >
+                <div
+                  style={{
+                    display: "grid",
+                    gap: "0.25rem",
+                    padding: "0.9rem",
+                    border: "1px solid currentColor",
+                    borderRadius: "0.5rem",
+                  }}
+                >
+                  <strong>{project.title}</strong>
+                  <span>owner: {project.owner}</span>
+                  <span>
+                    revision {project.revision} · {project.archived ? "archived" : "active"}
+                  </span>
+                </div>
+              </labPbui.Presentation>
+
+              <labPbui.Presentation
+                block
+                reference={idReference}
+                doc={`<projectId> ${project.id}; translates to <project> during acceptance`}
+              >
+                <code
+                  style={{
+                    display: "grid",
+                    placeItems: "center",
+                    height: "100%",
+                    padding: "0.9rem",
+                    border: "1px dashed currentColor",
+                    borderRadius: "0.5rem",
+                  }}
+                >
+                  #{project.id}
+                </code>
+              </labPbui.Presentation>
+            </article>
+          );
+        })}
+      </section>
+
+      <section
+        style={{
+          display: "grid",
+          gap: "0.35rem",
+          padding: "1rem",
+          border: "1px solid currentColor",
+          borderRadius: "0.5rem",
+        }}
+      >
+        <strong>Semantic identity check</strong>
+        <span>
+          The first project card and its id token use different presentation types, but
+          registry.sameObject(...) is <code>{String(sameObject)}</code>.
+        </span>
+        <span>
+          The archived card and token remain unhighlighted during acceptance because the arbitrary
+          selector tester rejects the translated project.
+        </span>
+      </section>
+
+      <labPbui.ObjectMenu />
+    </div>
+  );
+}
+
+function ClimConceptsExample() {
+  const [projects, setProjects] = useState(INITIAL_LAB_PROJECTS);
+  const [scope, setScope] = useState<"workspace" | "admin">("workspace");
+  const [lastVerb, setLastVerb] = useState<LabVerb | null>(null);
+  const environment = useMemo<LabEnvironment>(
+    () => ({
+      projects: Object.fromEntries(projects.map((project) => [project.id, project])),
+      currentUserId: "person-1",
+      canArchive: scope === "admin",
+    }),
+    [projects, scope],
+  );
+
+  const perform = (verb: LabVerb) => {
+    setLastVerb(verb);
+    if (verb.type !== "archiveProject") return;
+    setProjects((current) =>
+      current.map((project) =>
+        project.id === verb.projectId
+          ? { ...project, archived: true, revision: project.revision + 1 }
+          : project,
+      ),
+    );
+  };
+
+  return (
+    <labPbui.Provider
+      environment={environment}
+      actionTables={[scope]}
+      onPerform={perform}
+    >
+      <div style={{ minHeight: "100vh" }}>
+        <div
+          style={{
+            display: "flex",
+            gap: "0.75rem",
+            alignItems: "center",
+            justifyContent: "space-between",
+            flexWrap: "wrap",
+            padding: "0.75rem 1.5rem",
+            borderBottom: "1px solid currentColor",
+          }}
+        >
+          <label>
+            Action scope{" "}
+            <select
+              value={scope}
+              onChange={(event) => setScope(event.currentTarget.value as typeof scope)}
+            >
+              <option value="workspace">workspace</option>
+              <option value="admin">admin (inherits workspace)</option>
+            </select>
+          </label>
+          <button type="button" onClick={() => setProjects(INITIAL_LAB_PROJECTS)}>
+            Reset project state
+          </button>
+          <output>{lastVerb ? `last verb: ${JSON.stringify(lastVerb)}` : "No verb performed"}</output>
+        </div>
+        <LabSurface projects={projects} />
+      </div>
+    </labPbui.Provider>
+  );
+}
+
+export const ClimConceptsLab: Story = {
+  render: () => <ClimConceptsExample />,
+};
*** End Patch
PATCH
```

<details><summary>💭 Thinking</summary>

**Added concept lab registry and created a React TypeScript typechecking stub**

</details>

```json
{"open":[{"ref_id":"turn635943search2"},{"ref_id":"turn748092search7"},{"ref_id":"turn635943search3"},{"ref_id":"turn748092search6"},{"ref_id":"turn748092search3"}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Searched 2 websites**

</details>

```unknown
bash -lc cd /mnt/data/pbui_work/pbui && sed -n '1,420p' /tmp/pbui.diff > /tmp/diff-head.txt && wc -l /tmp/pbui.diff && sed -n '1,220p' packages/datalab-ui/src/pbui/types.ts && sed -n '1,260p' packages/datalab-ui/src/pbui/registry.ts && sed -n '1,200p' packages/datalab-ui/src/pbui/runtime.tsx && sed -n '1,220p' packages/datalab-ui/src/pbui/descriptors/tile.ts && sed -n '1,180p' packages/datalab-ui/src/pbui/descriptors/doc.ts && sed -n '1,180p' packages/datalab-ui/src/pbui/descriptors/field.ts
```

<details><summary>💭 Thinking</summary>

**Analyzed PBUI changes and updated README with CLIM quickstart**

</details>

```unknown
bash -lc cd /mnt/data/pbui_work/pbui && mkdir -p docs && cat > docs/presentation-based-ui-clim-guide.md <<'EOF'
# Presentation-Based User Interfaces in React

## A CLIM-inspired architecture, implementation guide, and Datalab case study

This chapter explains presentation-based user interfaces from first principles, relates them to the Common Lisp Interface Manager (CLIM), analyzes the original PBUI architecture in this repository, and documents the implementation added in this revision.

The intended reader may know React and TypeScript but not Common Lisp or CLIM. The goal is not to reproduce every feature of CLIM. The goal is to recover the parts of CLIM's interaction model that are especially valuable in a modern object-rich application:

- rendered output retains a semantic connection to a domain object;
- the interface can dynamically ask for an object of a semantic type;
- already-rendered objects can satisfy that request;
- one presented type can translate into another accepted type;
- arbitrary predicates can refine applicability without making every component understand every workflow;
- actions can be contributed by context rather than being permanently attached to one component;
- semantic object identity is separate from JavaScript reference identity, React element identity, and screen occurrence identity;
- independent views can share a selected subject through an explicit binding relation.

The implementation is deliberately incremental. Existing descriptors, verbs, `Presentation` components, and the legacy `types`/`filter` acceptance form continue to work. New code can adopt semantic identity, subtyping, translators, compiled selectors, action tables, and subject-link cells independently.

---

## 1. Why a presentation-based interface is different

A conventional component-oriented interface usually begins with widgets:

```text
button -> callback
select -> setter
row -> click handler
menu item -> command
```

Each component knows what a click means in its local context. This model is direct and works well for ordinary forms. It becomes less satisfactory when the same domain object appears in many visual forms and many workflows.

Consider one analytical field named `temperature`:

- a chip in a source browser;
- a table header;
- an encoding channel assignment;
- a node in a pipeline;
- a legend title;
- a field mentioned in an inspector;
- a token in command history.

A widget-oriented implementation tends to give each occurrence a separate handler. The source-browser chip may know how to map the field to a chart. The table header may know how to sort. The encoding panel may know how to accept a field. The pipeline may have another drag-and-drop protocol. These handlers often drift even though all occurrences mean the same thing.

A presentation-based interface starts with a different statement:

> This output is a presentation of domain object *x* as semantic type *T*.

The output may be text, SVG, a card, a table cell, or a complete tile. The important property is that the interface remembers what object and semantic type the output represents. Interaction can then be derived from the object, its type, the current input context, and the active command scope.

### 1.1 Four identities that must not be confused

Most bugs in object-rich interfaces come from treating several distinct notions of identity as though they were one.

| Identity | Question answered | Example |
|---|---|---|
| Domain identity | Which real application object is this? | document `doc-17` |
| Presentation identity | In what semantic role is it offered? | `<doc>`, `<projectId>`, `<field>` |
| Occurrence identity | Which rendered occurrence is under the pointer? | the field chip in the left pane |
| React identity | Which mounted element should React preserve? | a `key` in a list |

Two screen occurrences may present the same domain object. Two presentation types may also denote the same domain object. For example, a project card and a project-ID token can have different presentation types while identifying the same project. Conversely, two objects that happen to be structurally equal are not necessarily the same domain object.

React's `key` is not a domain identity protocol. It is a reconciliation hint local to a sibling list. JavaScript reference equality is not a domain identity protocol either: normalized stores, network decoding, immutable updates, and selectors routinely produce multiple object instances for one domain entity.

### 1.2 A dynamic input context

Suppose a command needs “an active quantitative field from document α.” In a conventional UI, the command often opens a dedicated picker. In a presentation-based UI, the application establishes an **input context** and existing presentations become selectable if they can satisfy it.

The request has several layers:

```text
semantic type: field
refinement: field belongs to document α
refinement: field is quantitative
possibly accepted through translation: category -> field
```

The rendered interface does not need to be rebuilt as a picker. Any existing table header, source-browser chip, pipeline output, or legend title can satisfy the request if its presentation is applicable.

### 1.3 Actions are relationships, not only properties

Some actions are intrinsic enough to live with a presentation descriptor. A document can expose “Inspect” or “Duplicate document.” Other actions exist only in a particular command scope:

- “Archive” is available in an administrator context;
- “Add to comparison” exists only inside a comparison workflow;
- “Use as command argument” depends on the command currently being read;
- “Link this selector to that tile” applies only while a link-target input context is active.

A robust model therefore needs both descriptor-local actions and context-contributed action selectors.

---

# Part I — CLIM foundations

## 2. What CLIM contributes conceptually

CLIM is a Common Lisp interface architecture rather than merely a widget set. Its manuals describe a model in which an application frame combines state, visual organization, and interaction; presentations connect displayed output to objects; command tables contain commands, menus, and presentation translators; and input contexts state what kinds of objects the system is currently asking the user to provide.[^mcclim-terminology]

A useful simplified loop is:

```text
read a command or command argument
        ↓
establish an input context
        ↓
make applicable presentations sensitive
        ↓
translate pointer input into an object or command
        ↓
execute the command against frame state
        ↓
redisplay
```

React applications do not normally run one explicit `read-execute-display` loop. State updates and rendering are event-driven. Nevertheless, the semantic decomposition remains valuable.

## 3. Application frames

A CLIM application frame is the object that ties together application state, panes, layouts, commands, and interaction policy. It is broader than a React component and narrower than an entire process.

A reasonable React correspondence is:

```text
CLIM application frame
    ≈ Provider instance
      + application/store instance
      + environment
      + active command/action tables
      + transient input context
      + rendering subtree
```

The correspondence is not exact. In this repository:

- `pbui.Provider` owns transient acceptance and menu state;
- the Redux store owns durable Datalab state;
- `PbuiEnvironment` exposes a controlled read interface;
- descriptor registries and action tables define interaction policy;
- the React subtree provides visual occurrences.

The important design lesson is **instance scope**. A presentation system should not depend on one ambient global store or one process-wide current environment. Two PBUI providers on one page must be independent, except for genuinely document-global mechanisms such as Escape ownership.

## 4. Presentations

CLIM presentations extend output recording with semantics. A presentation remembers displayed output, the associated Lisp object, and a semantic presentation type. That semantic tagging lets existing output satisfy later input requests.[^clim-what-is][^clim-output-recording]

A presentation therefore has at least four conceptual fields:

```ts
type ConceptualPresentation<T> = {
  object: T;
  presentationType: string;
  occurrence: renderedOutput;
  interactionMetadata: ...;
};
```

PBUI represents the semantic core as a discriminated reference:

```ts
interface Values {
  project: Project;
  projectId: string;
}

type ProjectRef =
  | { type: "project"; value: Project }
  | { type: "projectId"; value: string };
```

The `Presentation` React component supplies the occurrence. The descriptor supplies labeling, description, tone, actions, identity, and revision semantics. The provider supplies the current input and action context.

### 4.1 Presentation type is not JavaScript type

JavaScript and TypeScript answer representation questions:

```text
string
number
object
array
{ id: string; name: string }
```

A presentation type answers an interface-semantic question:

```text
<doc>
<field>
<tile>
<workspace>
<projectId>
<project>
```

Two values with the same TypeScript shape can require different menus and different acceptance behavior. A `string` can be a document ID, project ID, field name, stage ID, source name, or opaque token. Treating all strings as one interface type discards the information the interaction system needs.

### 4.2 One object, several presentations

CLIM presentation methods can specialize on a view, so one semantic type can have multiple visual representations.[^clim-presentation-types] PBUI currently places visual rendering in ordinary React components rather than in descriptor methods. This is intentional: descriptors stay free of component dependencies and remain easy to test.

The same object can still appear in many views:

```tsx
<Presentation reference={{ type: "project", value: project }}>
  <ProjectCard project={project} />
</Presentation>

<Presentation reference={{ type: "project", value: project }}>
  <CompactProjectRow project={project} />
</Presentation>
```

The occurrence changes; the semantic object and type do not.

## 5. Presentation types, inheritance, and parameters

CLIM presentation types form a semantic type lattice. Types can inherit presentation behavior, and parameterized presentation types can refine membership. The CLIM manuals require parameterized types to define type-membership and subtype behavior where inherited defaults are insufficient.[^clim-presentation-types]

Examples of parameterized type ideas are:

```lisp
(integer 0 100)
(sequence pathname)
((member alpha beta gamma) :description "document")
```

A TypeScript implementation has several possible levels of fidelity:

1. exact string type matching only;
2. nominal type inheritance;
3. parameterized type specifiers;
4. arbitrary type membership and subtype methods;
5. intersection, union, negation, and compound acceptance.

This revision implements level 2: named presentation types plus a transitive supertype graph. It intentionally does not pretend to implement CLIM's full parameterized type system.

### 5.1 Representation-safe subtyping

A critical difference between Common Lisp and TypeScript is the call boundary. If a translator or action selector is declared for a supertype and is invoked on a subtype, its callback must be able to consume the subtype's JavaScript value representation.

PBUI's `PresentationSupertypeMap` enforces:

```ts
Values[Subtype] extends Values[Supertype]
```

For example:

```ts
interface Values {
  entity: { id: string };
  project: { id: string; title: string };
}

const supertypes = {
  project: "entity",
} satisfies PresentationSupertypeMap<Values>;
```

This is safe because a project value can be passed to code expecting `{ id: string }`.

This would be rejected:

```ts
interface Values {
  entityId: string;
  project: { id: string; title: string };
}

// Unsafe: a project object is not a string.
const supertypes = { project: "entityId" };
```

That relationship is a **translation**, not subtyping.

## 6. Input contexts and `accept`

CLIM establishes an input context when it expects an object of a semantic type. Presentations that can satisfy that context become sensitive. The command processor establishes argument-specific input contexts, and presentation translators allow pointer input to supply command names or arguments.[^clim-command-processor]

PBUI's public operation is asynchronous:

```ts
const result = await pbui.accept({
  selector: pbui.selector("project", {
    where: (reference) =>
      reference.type === "project" && !reference.value.archived,
  }),
  prompt: "Choose an active project",
});
```

During the request:

1. the provider stores the request;
2. it compiles a selector for the current environment;
3. each rendered presentation asks whether it is acceptable;
4. acceptable occurrences receive the sensitive visual state;
5. activating an acceptable occurrence returns the accepted or translated reference;
6. Escape or an explicit abort resolves the request with `null`.

The request is dynamic. The same project card can be inert in one moment, acceptable as `<project>` in another, and acceptable as `<entity>` in a third.

### 6.1 Acceptance is not action execution

Acceptance supplies an object to a pending operation. It is not itself the final business effect.

```text
click acceptable field
    -> returns FieldRef to caller
    -> caller constructs a serializable verb
    -> application dispatches or performs verb
```

Keeping these stages separate avoids embedding workflow-specific mutations in every presentation occurrence.

## 7. Presentation translators

A CLIM presentation translator connects a source presentation type to a type required by the current input context. Applicability includes source type, target/context type, gesture, type parameters, and an optional tester. When several translators apply, CLIM orders them using priority and type specificity rules.[^clim-translator-applicability][^clim-translator-advanced]

PBUI implements direct, typed, one-step translators:

```ts
const translator: PresentationTranslator<Values, Environment> = {
  id: "project-id-to-project",
  from: "projectId",
  to: "project",
  priority: 10,
  tester: (projectId, environment) =>
    environment.projects[projectId] !== undefined,
  translate: (projectId, environment) =>
    environment.projects[projectId],
};
```

A displayed `projectId` token can now satisfy an input context asking for a `project`. The selection predicate receives the translated candidate and also receives the original source in its context.

### 7.1 Why translation is one-step

It is tempting to search an arbitrary conversion graph:

```text
A -> B -> C -> D
```

That creates hard questions:

- Which path wins?
- Can a translator have side effects or expensive lookups?
- Is repeated translation stable?
- How are cycles handled?
- How does a menu explain the chosen path?
- Can an intermediate conversion lose identity or authority?

The current registry permits one direct translation after checking direct subtype compatibility. This is predictable, easy to index, and close to the normal CLIM idea that a translator directly connects a presented source type to an input-context target type. Applications that need a chain should define an explicit translator for the intended semantic operation.

### 7.2 Testers

A translator tester is a predicate that narrows applicability based on the object and environment. CLIM separates broad type applicability from tester execution, and its APIs expose fast applicability paths for finding whether translators exist.[^clim-translator-advanced]

PBUI follows the same performance principle:

```text
source type index
    ↓
subtype check
    ↓
target type check
    ↓
translator tester
    ↓
translator body
    ↓
selector `where` predicate
```

An arbitrary predicate is not run for every unrelated presentation on the screen.

## 8. Commands, actions, and command tables

CLIM command tables determine which commands are available in a context and store menus and presentation translators. Tables can participate in inheritance. CLIM also distinguishes commands, which progress the command loop, from presentation actions used for side effects while input is pending.[^mcclim-terminology][^clim-command-processor]

PBUI does not implement a full CLIM command parser or command loop. It uses serializable application verbs:

```ts
type Verb =
  | { type: "archiveProject"; projectId: string }
  | { type: "inspectEntity"; entityId: string };
```

These verbs are command data. An application-level `onPerform` handler or Redux dispatcher interprets them.

There are two action sources:

1. **descriptor-local actions**, attached to the presented type;
2. **action selectors**, contributed by an active named action table.

```ts
const actionTables = [
  { id: "workspace", parents: ["global"] },
  { id: "admin", parents: ["workspace"] },
];

const archiveSelector = {
  id: "archive-project",
  from: "project",
  table: "admin",
  tester: (reference, environment) =>
    reference.type === "project" &&
    environment.canArchive &&
    !reference.value.archived,
  actions: (reference) =>
    reference.type === "project"
      ? [{
          id: "archive",
          label: "Archive project",
          danger: true,
          verb: { type: "archiveProject", projectId: reference.value.id },
        }]
      : [],
};
```

The provider selects active scopes:

```tsx
<pbui.Provider actionTables={["admin"]}>
  ...
</pbui.Provider>
```

`admin` inherits `workspace`, and `global` is always present. Descriptor-local action IDs win over contributed actions with the same ID, allowing a type-specific override.

## 9. Output recording and React

CLIM output recording captures displayed output in an output-record tree. It supports scrolling, structured formatting, semantic presentations, and incremental redisplay.[^clim-output-recording]

React's virtual tree is not a CLIM output history:

- React does not generally retain semantic records for output that has unmounted;
- hit testing is delegated to the DOM and event system;
- replay and scrolling are browser/layout concerns;
- React reconciliation uses component and element identity, not domain semantics;
- an off-screen virtualized object may have no mounted presentation occurrence.

Nevertheless, a React presentation wrapper is a useful analogue for **mounted semantic output**. PBUI records semantics in DOM attributes and event handlers for the lifetime of the occurrence:

```html
<span
  data-pbui="presentation"
  data-ptype="field"
  data-state="acceptable"
  role="button"
  tabindex="0"
>temperature</span>
```

A future output-record layer could maintain a semantic index beyond mounted DOM nodes, but that is not required for the interaction model implemented here.

---
EOF
```

<details><summary>💭 Thinking</summary>

**Drafted and documented CLIM-inspired PBUI architecture and testing guides**

</details>

```unknown
bash -lc set -e
cd /mnt/data/pbui_work/pbui
tsc -p /tmp/pbui-typecheck/tsconfig.json --noEmit --pretty false
tsc -p /tmp/pbui-typecheck/tsconfig-story.json --noEmit --pretty false
printf 'generic typechecks: ok\n'
node - <<'NODE'
const ts = require('/opt/nvm/versions/node/v22.16.0/lib/node_modules/typescript');
const fs = require('fs');
const cp = require('child_process');
const changed = cp.execFileSync('bash', ['-lc', "grep '^diff -ruN' /tmp/pbui.diff | sed 's#diff -ruN /mnt/data/pbui_orig/pbui/[^ ]* /mnt/data/pbui_work/pbui/##'"], {encoding:'utf8'}).trim().split('\n').filter(Boolean);
const currentExtra = [
  'packages/datalab-ui/test/subjectLinks.test.ts',
  'docs/presentation-based-ui-clim-guide.md',
];
let failed = false;
for (const rel of [...changed, ...currentExtra]) {
  if (!/\.(ts|tsx)$/.test(rel)) continue;
  const text = fs.readFileSync(rel, 'utf8');
  const result = ts.transpileModule(text, {
    compilerOptions: {
      target: ts.ScriptTarget.ES2022,
      module: ts.ModuleKind.ESNext,
      jsx: ts.JsxEmit.ReactJSX,
      isolatedModules: true,
      verbatimModuleSyntax: true,
    },
    fileName: rel,
    reportDiagnostics: true,
  });
  const diagnostics = result.diagnostics ?? [];
  if (diagnostics.length) {
    failed = true;
    console.error(`Diagnostics in ${rel}:`);
    for (const d of diagnostics) console.error(ts.flattenDiagnosticMessageText(d.messageText, '\n'));
  }
}
if (failed) process.exit(1);
console.log('changed-file syntax transpilation: ok');
NODE
```

<details><summary>💭 Thinking</summary>

**Inspected, fixed, compiled, and smoke-tested registry and subjectLinks changes**

</details>

```unknown
bash -lc set -e
npm root -g
node -e 'console.log(require.resolve("typescript", {paths:[require("child_process").execSync("npm root -g").toString().trim()]}))'
printf '\nStale portable versions:\n'
grep -RIn --exclude-dir=node_modules --exclude='pnpm-lock.yaml' -E 'version:[[:space:]]*3|BUNDLE_VERSION[[:space:]]*=[[:space:]]*3' /mnt/data/pbui_work/pbui || true
printf '\nBundle version declarations:\n'
grep -RIn --exclude-dir=node_modules -E 'BUNDLE_VERSION|version:[[:space:]]*4' /mnt/data/pbui_work/pbui/packages/datalab-ui/src /mnt/data/pbui_work/pbui/packages/datalab-ui/test | sed -n '1,160p'
```

<details><summary>💭 Thinking</summary>

**Checked TypeScript configuration, syntax, versions, and strict typechecks**

</details>

```unknown
bash -lc sed -n '240,520p' /mnt/data/pbui_work/pbui/src/presentation/registry.test.ts
```

<details><summary>💭 Thinking</summary>

**Inspected, updated, and typechecked PBUI registry, documentation, and persistence changes**

</details>

```unknown
bash -lc grep -n "linkViewDocument\|subjectLinks\|linked" -A35 -B20 /mnt/data/pbui_work/pbui/packages/datalab-ui/test/store.test.ts | sed -n '1,520p'
grep -n "subjectLinks\|bundle-local\|fresh" -A35 -B20 /mnt/data/pbui_work/pbui/packages/datalab-ui/test/portable.test.ts | sed -n '1,520p'
grep -n "subjectLinks\|conflict" -A40 -B20 /mnt/data/pbui_work/pbui/packages/datalab-ui/test/remote-load.test.ts | sed -n '1,320p'
```

<details><summary>💭 Thinking</summary>

**Reviewed Datalab link typecheck tests and persistence schema version**

</details>

# Completed deliverables

- [Enhanced PBUI project archive](sandbox:/mnt/data/pbui-enhanced.zip)
- [Detailed Markdown textbook and design analysis](sandbox:/mnt/data/PRESENTATION-BASED-UI-CLIM-DESIGN-AND-IMPLEMENTATION.md)
- [Repository-relative Git patch](sandbox:/mnt/data/pbui-enhancement.patch)

The patch applies cleanly to the supplied `pbui` directory with:

```bash
git apply pbui-enhancement.patch
```

The archive contains the complete enhanced `pbui/` tree and the supplied companion `datalab/` directory.

## Core architectural result

The implementation now distinguishes four identities that the original model partially conflated:

1. **Application-object identity** — for example, two separately allocated field references that both denote field `temperature` in document `α`.
2. **Logical view identity** — one open chart, pipeline, table, or other application configuration.
3. **Placement identity** — one rectangle presenting a logical view in the workspace.
4. **Subject or binding identity** — the selected document state that one or more otherwise independent views observe.

That fourth identity is what permits a chart and a pipeline to remain distinct applications while following the same selected document.

```text
chart placement ──┐
                  ├── chart view ─────┐
                  │                   │
pipeline placement┴── pipeline view ──┴── shared document binding ── document α
```

A linked duplicate still means multiple placements of one logical view. An ordinary duplicate creates an independent logical view and an independent document selector. The new document-link operation creates a third relationship: distinct views sharing only the document-selection subject.

## Generic PBUI extensions

### Semantic identity

Descriptors can now define a stable identity key and an identity domain:

```ts
field: {
  label: (field) => field.name,
  identityDomain: "field",
  identity: (field) => JSON.stringify([field.docId, field.name]),
}
```

PBUI exposes:

```ts
registry.identityFor(reference, environment);
registry.sameObject(left, right, environment);
```

The domain prevents accidental equality between unrelated IDs—for example, document `"1"` and user `"1"`. Different presentation types may intentionally share a domain when they are alternate presentations of the same application object.

Fallback behavior remains safe:

- primitives use primitive identity;
- objects use JavaScript object identity;
- no structural deep equality is guessed.

### Prepared selectors and arbitrary lambdas

Accept operations now support reusable `PresentationSelector` objects:

```ts
const selectableField = presentationSelectors.type("field", {
  cache: "identity",

  prepare: () => {
    const allowedNames = new Set(["station", "yield", "temperature"]);

    return (field) => allowedNames.has(field.name);
  },
});

const result = await pbui.accept({
  prompt: "Choose a field",
  selector: selectableField,
});
```

The selector protocol separates:

- `types`: the semantic type requirement;
- `includeSubtypes`: runtime subtype behavior;
- `where`: a direct arbitrary predicate;
- `prepare`: work performed once when the input context starts;
- `cache`: optional operation-scoped semantic memoization.

This addresses the performance problem with arbitrary lambdas. Instead of repeatedly scanning an array for every visible presentation and every React render, `prepare` can compile a regular expression, construct a `Set`, build an index, or capture a coherent snapshot once.

Identity caching is deliberately limited to one accept operation. It is not a global cache and cannot survive state changes indefinitely. PBUI also re-evaluates the selected occurrence when the user commits it. Consequently, memoization may establish that two occurrences are equally acceptable without returning the payload of the wrong occurrence.

The existing inline API remains supported:

```ts
pbui.accept({
  prompt: "Choose a field",
  types: "field",
  filter: (reference) => reference.value.name !== "internal_id",
});
```

### Runtime presentation subtypes

The registry now accepts a runtime type hierarchy:

```ts
createPresentationRegistry(descriptors, {
  supertypes: {
    employee: ["person"],
    administrator: ["employee"],
  },
});
```

Subtype checks are transitive and cached. Cycles are rejected at registry construction rather than being discovered during pointer interaction.

Raw selectors include subtypes by default, matching the expected input-context behavior. The typed Datalab selector factory produces exact-type selectors by default because its value-level lambda is statically typed for the selected concrete type.

### Selector-driven action rules

Actions no longer have to be repeated in every exact descriptor. The registry supports command-table-style rules:

```ts
{
  id: "inspect-visible-object",
  selector: { types: inspectableTypes },
  priority: 10,
  actions: (reference) => ({
    id: "inspect",
    label: "Inspect",
    verb: {
      kind: "inspect",
      ptype: reference.type,
      value: reference.value,
    },
  }),
}
```

Rules are selected by presentation selectors and ordered by priority. Descriptor-local actions are still listed first and shadow inherited rules by stable action ID. This allows a type to override a common `inspect` or `watch` command without duplicating the whole command system.

### Weighted conversion graph

Conversions are now named and typed:

```ts
{
  id: "category-to-field",
  from: "cat",
  to: "field",
  cost: 1,
  convert: (reference) => ({
    type: "field",
    value: {
      docId: reference.value.docId,
      name: reference.value.field,
    },
  }),
}
```

PBUI searches conversions as a bounded weighted graph:

- lower total cost wins;
- priority resolves equal-cost alternatives;
- edges are indexed by source type;
- semantic visited-state tracking prevents cycles;
- maximum path depth is configurable;
- legacy conversion functions remain supported as cost-one edges.

This makes conversion selection deterministic and auditable. A cheap two-edge interpretation can correctly beat an expensive direct conversion.

CLIM itself associates application objects, presentation types, and visual output; input contexts determine which visible presentations are acceptable; presentation types can participate in inheritance; and translators and command tables mediate between visible objects and commands. The implementation adopts those separations without attempting to reproduce CLIM’s Lisp APIs literally. citeturn250762search0turn250762search1turn884950search1turn164999search0

CLIM’s output history, output records, gesture system, textual parsing, partial commands, and incremental redisplay are broader facilities than this patch implements. They are analyzed separately in the guide rather than being conflated with the new selector and identity protocols. citeturn164999search1turn250762search2

## Chart and pipeline document linking

`AppView` now has an optional subject identity:

```ts
interface AppView {
  id: ViewId;
  appId: AppId;
  documents: Record<string, DocId>;
  documentBindingId?: string;
  title?: string;
}
```

A missing binding ID remains backward-compatible: the view’s own ID acts as its private binding.

Three reducers implement the lifecycle:

```ts
layoutActions.linkViewDocuments({
  sourceViewId,
  targetViewId,
});

layoutActions.setViewDocument({
  viewId,
  role: "primary",
  docId,
});

layoutActions.unlinkViewDocuments(viewId);
```

Linking merges the source and target binding groups. The source group’s document-role map wins at link time. Subsequent changes to any role propagate atomically to every logical view in the group. Unlinking detaches one logical view while preserving its current selection.

The interaction is itself implemented through PBUI rather than through a special tile-picker modal:

1. Press the chain button in a chart or pipeline DocBar.
2. PBUI enters an input context accepting another document-bound `<tile>` presentation.
3. Click or keyboard-activate the other tile title.
4. The views retain different `viewId` and `appId` values but receive one shared `documentBindingId`.
5. Either DocBar’s document dropdown now updates both views.
6. The unlink control detaches one view.

This is exercised by the Storybook story:

```text
Component Library
  → Organisms
    → Tile
      → Linked Document Selectors
```

After installing the repository dependencies, the first-time path is:

```bash
corepack enable
pnpm install
pnpm --filter @hyperslop-systems/datalab-ui storybook
```

## Product-level identity policies

The Datalab registry now explicitly identifies:

- fields by document and field name;
- documents by document ID;
- sources by their source coordinates;
- categories by document, field, and category value;
- datum rows by producer-supplied row key, falling back to row-object identity;
- pipeline steps, users, tokens, uploads, members, workspaces, stages, trace entries, and tile placements by their appropriate stable keys.

Chart marks and table rows now carry row keys where available. This allows semantic matching without unsafe structural equality that would collapse duplicate rows.

Common `Inspect` and `Add to watchlist` actions are contributed through action rules. Existing descriptor-local actions retain their intentional ordering by shadowing the common rule with the same stable action ID.

## Persistence and portability

Local persistence accepts the optional runtime binding ID while remaining compatible with older layouts.

Portable bundles do not export runtime binding IDs. Instead, they encode document-selection groups as dense equivalence indices:

```json
{
  "views": [
    {
      "app": "chart",
      "binding": 0,
      "documents": { "primary": 0 }
    },
    {
      "app": "pipeline",
      "binding": 0,
      "documents": { "primary": 0 }
    }
  ]
}
```

Import creates distinct fresh view IDs, reconstructs one fresh shared binding, and hydrates the shared document only once.

One boundary remains explicit: the current remote protobuf `AppView` has no document-binding field. Therefore:

- local persistence preserves linkage;
- tile, workspace, and stage bundles preserve linkage;
- current remote workbench snapshots do **not** preserve linkage.

Completing that transport requires an additive protocol field such as:

```proto
optional string document_binding_id = 5;
```

followed by regenerated TypeScript and Go protocol code and corresponding codec tests. The codec contains comments marking this boundary so remote behavior is not silently misrepresented.

## Validation

The delivered tree passed the checks that could run without the absent dependency installation:

- 31 changed TypeScript/TSX files: zero syntax diagnostics.
- Strict type checking of the generic identity, selector, registry, and conversion core.
- Runtime assertions for semantic identity, subtype traversal, action rules, selector preparation, memoization, clicked-occurrence commitment, conversion costs, and cycle rejection.
- Strict checking of the Datalab presentation registry.
- Strict checking of the portable model.
- Strict checking and runtime assertions for document linking, propagation, unlinking, and independent duplication.
- Strict checking and runtime round-trip assertions for portable linked workspaces.
- Markdown fence, link, and whitespace checks.
- ZIP integrity verification.
- Clean application of the patch followed by a byte-for-byte comparison with the enhanced repository.

The supplied archive had no `node_modules`. Full repository Vitest, Storybook, Vite, Biome, protobuf, and Go gates were not run because Corepack attempted to retrieve the pinned pnpm release and the execution environment had no network/DNS access. The guide distinguishes these targeted checks from the project’s normal complete CI suite.


---

> What would be elegant ways to implement the subtyping hierarchy, maybe in a mor emodern type theory way now since we have all this research and implementation and opensource approaches from the last 40 years. Are there maybe similar projects in javascript or in elixir or in other systems ?

<details><summary>💭 Thinking</summary>

**Researching related systems**

I’m comparing JavaScript, Elixir, UI, and type-theory precedents, then mapping them onto the proposed runtime. I’ll prioritize practical design lessons: protocols, multimethods, presentation types, refinement, row polymorphism, and semantic subtyping.

**Researched related systems**

</details>

I’ll compare several modern models—semantic subtyping, refinement types, open variants, type classes/protocols, and predicate dispatch—then map the strongest ideas onto your PBUI implementation and survey close systems in JavaScript, ClojureScript, Elixir, and other ecosystems.

```json
{"system1_search_query":[{"q":"site:mcclim.common-lisp.dev presentation types translators command tables McCLIM manual"},{"q":"semantic subtyping CDuce paper official PDF"},{"q":"algebraic subtyping MLsub paper official"},{"q":"occurrence typing Typed Racket paper official"}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Comparing implementation paths**

I’m separating practical runtime design from ambitious type-theory features. My likely recommendation is a structural type lattice with protocols, refinements, explicit conversions, compiled matching, and witnesses—rather than one global inheritance hierarchy.

**Compared implementation paths**

</details>

```json
{"system1_search_query":[{"q":"site:hexdocs.pm/elixir types patterns guards protocols official Elixir type system"},{"q":"site:elixir-lang.org/blog set-theoretic types Elixir official"},{"q":"site:clojure.org/reference multimethods protocols spec official"},{"q":"site:docs.julialang.org methods multiple dispatch type system official"}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Searched 34 websites**

</details>

## Main recommendation

Do **not** turn the presentation types into a deeper class-style inheritance hierarchy.

A more elegant model is:

> Presentation types denote sets of acceptable semantic references. Subtyping means set inclusion.

Then construct types using a small algebra:

- named atomic types;
- unions;
- intersections;
- differences or negation;
- parameterized types;
- predicate refinements;
- capabilities or roles.

Keep three other relations separate:

- **identity** — whether two references denote the same application object;
- **translation** — whether one representation can be converted into another;
- **behavior** — which actions, renderers, or commands apply.

This is close to **semantic subtyping** and set-theoretic type systems. Such systems model types through unions, intersections, and complements, with `A <: B` meaning that every value in `A` is also in `B`. CDuce is an established research implementation of this approach. Elixir has now adopted a gradual set-theoretic type system: Elixir 1.20, released June 3, 2026, performs gradual inference across the language using unions, intersections, and negations. citeturn424830search1turn569191search8turn851218academia76

For PBUI, I would use a **restricted, application-level semantic type algebra**, not attempt to implement a complete programming-language type checker.

---

# 1. A type algebra instead of a hierarchy

The current relation is approximately:

```ts
const supertypes = {
  project: "entity",
  employee: "person",
};
```

That is useful, but it treats every semantic relation as a nominal ancestry relation. It becomes awkward for concepts such as:

```text
active project
project owned by me
document-backed object
inspectable object
project or workspace
field in document α
visible object that is not archived
```

These are not naturally nodes in a single tree.

A more expressive representation would be:

```ts
type TypeExpr =
  | { readonly kind: "atom"; readonly id: TypeId }
  | { readonly kind: "union"; readonly members: readonly TypeExpr[] }
  | { readonly kind: "intersection"; readonly members: readonly TypeExpr[] }
  | { readonly kind: "not"; readonly operand: TypeExpr }
  | {
      readonly kind: "refinement";
      readonly base: TypeExpr;
      readonly predicate: PredicateId;
      readonly args?: unknown;
    }
  | {
      readonly kind: "parameterized";
      readonly constructor: TypeConstructorId;
      readonly args: readonly unknown[];
    };
```

With constructors:

```ts
const atom = (id: TypeId): TypeExpr => ({ kind: "atom", id });

const or = (...members: TypeExpr[]): TypeExpr => ({
  kind: "union",
  members,
});

const and = (...members: TypeExpr[]): TypeExpr => ({
  kind: "intersection",
  members,
});

const not = (operand: TypeExpr): TypeExpr => ({
  kind: "not",
  operand,
});

const refine = (
  base: TypeExpr,
  predicate: PredicateId,
  args?: unknown,
): TypeExpr => ({
  kind: "refinement",
  base,
  predicate,
  args,
});
```

Application types can then be expressed directly:

```ts
const Entity = atom("entity");
const Project = atom("project");
const Archived = atom("archived");
const Inspectable = atom("inspectable");
const DocumentBacked = atom("document-backed");

const InspectableProject = and(Project, Inspectable);

const ActiveProject = and(Project, not(Archived));

const SelectableSubject = or(
  and(Project, DocumentBacked),
  atom("workspace"),
);
```

The important change is that `inspectable`, `document-backed`, and `archived` need not be ancestors or subclasses. They are semantic properties.

## Why this is better

A tree forces every object into one privileged classification:

```text
entity
└── document-backed-entity
    └── project
        └── active-project
            └── active-project-owned-by-current-user
```

That explodes combinatorially. What happens when the project is also:

```text
searchable
shareable
archivable
editable
remote
cached
selected
```

With intersections, these remain independent dimensions:

```text
Project ∧ Editable ∧ DocumentBacked ∧ ¬Archived
```

This resembles set-theoretic typing more than object-oriented inheritance. Elixir’s new type system uses precisely the logical operations of union, intersection, and negation to describe narrowing produced by patterns and guards. citeturn569191search8turn569191search10

---

# 2. Atomic types, capabilities, and refinements

I would divide your type vocabulary into three categories.

## 2.1 Atomic domain types

These identify the fundamental semantic role in which a value is presented:

```text
project
document
field
category
pipeline-step
tile
workspace
user
```

They remain nominal and registry-owned.

```ts
registry.defineAtom<Project>({
  id: "project",
  identity: project => ({
    namespace: "project",
    key: project.id,
  }),
});
```

Atomic types should be relatively stable and few in number.

## 2.2 Capabilities

Capabilities describe operations or semantic affordances:

```text
inspectable
editable
deletable
document-backed
linkable-subject
tabular
selectable
```

They are essentially zero-argument propositions about a presentation.

```ts
registry.defineCapability({
  id: "document-backed",
});

registry.implementCapability({
  type: "project",
  capability: "document-backed",
});

registry.implementCapability({
  type: "chart",
  capability: "document-backed",
});
```

A capability is better than a parent type when its primary purpose is to determine available behavior.

For example:

```ts
actions.define({
  id: "change-document",
  subject: capability("document-backed"),
  action: reference => ({
    id: "change-document",
    label: "Change document",
    verb: {
      type: "changeDocument",
      target: reference,
    },
  }),
});
```

This is closer to a protocol, trait, or type class than inheritance. Clojure protocols define named sets of polymorphic operations independently of a concrete class hierarchy, while Elixir protocols vary behavior by data type. citeturn851218search0turn851218search5

## 2.3 Refinements

Refinements describe a subset selected by a predicate:

```text
active project
field belonging to document α
project owned by current user
tile currently visible
document for which the user has write permission
```

```ts
registry.defineRefinement<Project, { ownerId: string }>({
  id: "owned-by",
  base: atom("project"),

  test(project, args) {
    return project.ownerId === args.ownerId;
  },

  dependencies(project, args) {
    return [
      ["project", project.id, project.revision],
      ["owner", args.ownerId],
    ];
  },
});
```

Usage:

```ts
const MyProject = refine(
  atom("project"),
  "owned-by",
  { ownerId: currentUser.id },
);
```

This is related to refinement and occurrence typing: after a predicate succeeds, the system can treat that occurrence as belonging to a narrower type. Typed Racket’s occurrence typing explicitly refines variable types based on successful predicate checks. citeturn424830search3turn424830search7

---

# 3. Make matching produce evidence, not only a Boolean

The current selector model essentially asks:

```ts
accepts(reference): boolean
```

A more powerful protocol would return a **match witness**:

```ts
interface TypeEvidence {
  readonly expression: TypeExpr;
  readonly facts: readonly EvidenceFact[];
  readonly registryVersion: number;
  readonly environmentVersion: number;
}

interface Match<TReference> {
  readonly source: TReference;
  readonly accepted: TReference;
  readonly evidence: TypeEvidence;
  readonly conversionPath: readonly TranslatorId[];
  readonly specificity: Specificity;
}
```

Then:

```ts
const result = typeSystem.match(reference, ActiveProject, environment);

if (result.ok) {
  executeAction(result.match);
}
```

This has several benefits.

### Better explanation

A menu or developer inspector can say:

```text
Accepted as ActiveProject because:
  project <: entity
  project implements inspectable
  project.archived = false
```

### Safer action execution

The action receives not merely an untrusted project but evidence that the project satisfied the action’s requirements.

```ts
actions.define({
  id: "archive-project",
  subject: and(
    atom("project"),
    capability("archivable"),
    not(atom("archived")),
  ),

  run(match) {
    // match contains the evidence and accepted representation.
  },
});
```

### Correct caching

Evidence can record the revisions and environmental epochs against which the predicate was evaluated. Before executing an action, PBUI can cheaply check whether the evidence is still current.

This is important because an arbitrary predicate such as:

```ts
project => !project.archived
```

does not remain true forever.

---

# 4. Keep translation out of subtyping

This distinction should remain strict:

```text
Project <: Entity
```

means a `Project` value can be used directly wherever an `Entity` value is expected.

But:

```text
ProjectId -> Project
```

is not subtyping. It may involve:

- lookup;
- authorization;
- failure;
- asynchronous loading;
- a change of representation;
- a different lifetime;
- network access.

It is a translation or coercion.

```ts
registry.defineTranslator({
  id: "project-id/to-project",
  from: atom("project-id"),
  to: atom("project"),

  applicable(id, environment) {
    return environment.projects.has(id);
  },

  translate(id, environment) {
    return environment.projects.get(id);
  },
});
```

Julia makes a similar conceptual distinction: method dispatch is based on types, while conversion and promotion are separate operations; function arguments are not automatically converted merely to make a method applicable. citeturn569191search2turn569191search13

Your weighted translator graph is a reasonable model, but I would tighten it in two ways:

1. A translator should explicitly declare whether it is:
   - total;
   - partial;
   - pure;
   - asynchronous;
   - identity-preserving.

2. The matching result should retain the conversion path.

```ts
interface TranslatorMetadata {
  readonly total: boolean;
  readonly pure: boolean;
  readonly asynchronous: boolean;
  readonly preservesIdentity: boolean;
  readonly cost: number;
}
```

An identity-preserving translator such as `ProjectId -> Project` lets PBUI know that the accepted object still denotes the same semantic entity.

---

# 5. Use multiple dispatch for action selection

Actions are not really methods belonging to an object. They are relationships among:

```text
subject presentation
requested operation
input context
command table
current user capabilities
possibly a second object
```

That suggests **multiple dispatch** rather than descriptor inheritance.

Conceptually:

```ts
actions.define({
  subject: and(atom("project"), not(atom("archived"))),
  context: capability("administrative-context"),
  gesture: atom("context-menu"),
  method: archiveProject,
});
```

Or for linking:

```ts
actions.define({
  subject: capability("document-backed"),
  argument: capability("document-backed"),
  context: atom("linking-context"),

  method(source, target) {
    return linkDocumentBindings(source, target);
  },
});
```

This is much closer to Julia or Clojure multimethods than conventional JavaScript methods.

Julia chooses a method using the types of all arguments, not merely a privileged receiver. citeturn569191search2

Clojure multimethods are particularly relevant to PBUI. They support:

- arbitrary dispatch values;
- an ad hoc derivation hierarchy;
- tuple dispatch;
- method preference for ambiguities;
- hierarchy queries through `isa?`, `ancestors`, and `descendants`. citeturn630153search0

A PBUI action dispatcher could use:

```ts
type DispatchSignature = readonly [
  subjectType: TypeExpr,
  contextType: TypeExpr,
  gestureType: TypeExpr,
];
```

## Specificity ordering

Do not make numeric priority the principal resolution mechanism.

Derive ordering from semantic specificity:

```text
A is more specific than B when A <: B and not B <: A
```

For compound action signatures:

```text
(A1, A2, A3) is more specific than (B1, B2, B3)
when every Ai <: Bi
and at least one Ai is strictly narrower than Bi
```

Only use explicit priorities or preference declarations when two methods are genuinely incomparable.

For example:

```text
Project ∧ Editable
Project ∧ OwnedByCurrentUser
```

Neither necessarily contains the other. If both match, PBUI should either:

- combine their actions;
- report an ambiguity;
- use a declared preference;
- use a business-specific tie-break.

Silently resolving everything with a registration-order integer will eventually become difficult to reason about.

---

# 6. Parameterized presentation types

CLIM presentation types can carry parameters. Your model should support the same idea without generating new global type names.

Instead of:

```text
field-in-document-a
field-in-document-b
field-in-document-c
```

use:

```ts
const FieldIn = (documentId: string): TypeExpr =>
  parameterized("field-in-document", documentId);
```

Definition:

```ts
registry.defineTypeConstructor({
  id: "field-in-document",
  base: atom("field"),

  test(field: Field, [documentId]: readonly [string]) {
    return field.documentId === documentId;
  },

  subtype(leftArgs, rightArgs) {
    return leftArgs[0] === rightArgs[0];
  },
});
```

Then:

```ts
await pbui.accept({
  type: FieldIn(activeDocumentId),
});
```

Other useful constructors might include:

```ts
FieldOf(documentId)
ColumnOf(tableId)
OwnedBy(userId)
StageOf(pipelineId)
Permission("write")
RowOf(documentId, tableName)
```

Parameterized types should be serializable where possible. This makes them usable in:

- command history;
- persisted UI state;
- remote workbench protocols;
- debugging tools;
- explanations.

---

# 7. Arbitrary lambdas: separate stable refinements from ephemeral selectors

Allowing arbitrary lambdas is useful, but arbitrary lambdas are opaque:

```ts
project => project.score > expensiveThreshold()
```

The system cannot automatically determine:

- whether it is pure;
- what state invalidates its answer;
- whether it is safe to serialize;
- whether it can run remotely;
- how expensive it is;
- whether two lambdas are equivalent.

I would support two levels.

## Stable named refinement

```ts
registry.defineRefinement({
  id: "active-owned-project",
  base: atom("project"),
  purity: "pure",
  cost: "cheap",

  dependencies(project, args, environment) {
    return [
      project.revision,
      environment.authorizationEpoch,
      args.ownerId,
    ];
  },

  test(project, args, environment) {
    return (
      !project.archived &&
      project.ownerId === args.ownerId &&
      environment.canView(project.id)
    );
  },
});
```

This can be cached, inspected, explained, and serialized.

## Ephemeral lambda refinement

```ts
const selector = pbui.refine(atom("project"), {
  cache: "operation",
  where(project) {
    return temporarySet.has(project.id);
  },
});
```

This is valid only inside the current process and input context.

Elixir’s guard system offers a useful lesson here. Guards intentionally permit only a restricted set of predictable, side-effect-free operations so they can be efficiently analyzed and executed. Custom guards must expand into this restricted language. citeturn851218search2

PBUI does not need to restrict all predicates that severely, but it can classify them:

```ts
type PredicateClass =
  | "structural"
  | "pure"
  | "environment-dependent"
  | "volatile"
  | "effectful";
```

Recommended policy:

| Class | Cache | Serializable | Valid for subtype reasoning |
|---|---:|---:|---:|
| Structural | persistent | yes | yes |
| Pure named refinement | revision-based | yes | usually |
| Environment-dependent | environment epoch | with arguments | only within environment |
| Volatile lambda | operation only | no | no |
| Effectful | never | no | no |

An effectful function should generally be a translator or command, not a type predicate.

---

# 8. Open-world versus closed-world typing

Negation introduces a subtle issue.

Suppose:

```ts
not(atom("archived"))
```

What is its universe?

In a closed type system, it means every value in the universe except archived values. But PBUI registries may be extensible through application modules or plugins. A new type registered later changes the complement.

There are three reasonable choices.

## Registry-snapshot semantics

A compiled expression is interpreted against one registry version:

```ts
interface CompiledType {
  readonly registryVersion: number;
}
```

Adding a plugin invalidates and recompiles affected expressions.

This is the most general option.

## Restricted difference

Only permit subtraction from a known base:

```ts
difference(atom("project"), atom("archived-project"))
```

rather than global negation:

```ts
not(atom("archived-project"))
```

This is easier to explain and safer in an extensible system.

## Capabilities with negative refinements

Use explicit positive or negative facts:

```text
active
archived
visible
hidden
```

rather than arbitrary universal complements.

My recommendation is:

- expose `difference(base, excluded)` in the ordinary PBUI API;
- keep unrestricted `not` internal or advanced;
- version compiled expressions by registry snapshot.

---

# 9. Performance architecture

A semantic type algebra sounds expensive, but most PBUI matching can be compiled into a few fast stages.

## 9.1 Assign atomic types bit positions

```text
project          bit 0
entity           bit 1
inspectable      bit 2
document-backed  bit 3
archived         bit 4
```

A presentation obtains an atomic fact mask:

```ts
type AtomMask = bigint;
```

For example:

```text
Project A:
  project          1
  entity           1
  inspectable      1
  document-backed  1
  archived         0
```

Intersections and simple differences then become bit operations.

```ts
const hasRequiredAtoms =
  (facts & requiredMask) === requiredMask;

const hasExcludedAtoms =
  (facts & excludedMask) !== 0n;
```

## 9.2 Index rules by positive atoms

Before running predicates, find a selective required atom:

```text
Archive action requires Project ∧ Archivable ∧ ¬Archived
                          ↑
                  index under Project
```

Only rules indexed under atoms possessed by the presentation become candidates.

## 9.3 Normalize expressions

Normalize:

```text
Project ∧ (Inspectable ∨ Editable)
```

into an internal canonical representation.

For a modest application, disjunctive clauses are sufficient:

```ts
interface Clause {
  readonly requiredAtoms: AtomMask;
  readonly excludedAtoms: AtomMask;
  readonly refinements: readonly CompiledRefinement[];
}
```

```ts
interface CompiledType {
  readonly clauses: readonly Clause[];
}
```

## 9.4 Introduce BDDs only if expressions become large

Elixir’s type-system team initially used disjunctive normal forms but encountered exponential growth once intersections, unions, and negations became common. They subsequently moved toward binary decision diagrams and documented lazy BDD optimizations. citeturn569191search10

That is directly relevant, but PBUI probably does not need BDDs initially.

Use this progression:

```text
nominal DAG
    ↓
bitset facts + normalized clauses
    ↓
shared expression DAG
    ↓
BDD only after profiling demonstrates expression blow-up
```

Do not implement a BDD package merely because the theory is elegant.

## 9.5 Cache using identity, revision, and environment epoch

A safe cache key is approximately:

```ts
interface MatchCacheKey {
  readonly expressionHash: string;
  readonly identityNamespace: string;
  readonly identityKey: string;
  readonly objectRevision: string | number;
  readonly environmentEpoch: string | number;
  readonly registryVersion: number;
}
```

For refinement-specific dependencies, use narrower epochs:

```ts
predicate.dependencies(reference, environment);
```

That is better than invalidating every cached match whenever any environment value changes.

## 9.6 Revalidate on commitment

Hover highlighting can use cached applicability.

When the user activates the object, PBUI should perform a final applicability check against the current revision. This avoids accepting stale evidence after state changed between render and click.

---

# 10. A proposed PBUI API

A possible public API would look like this:

```ts
const types = createPresentationTypeSystem<Values, Environment>();

const Entity = types.atom("entity");

const Project = types.atom("project", {
  representation: isProject,
  identity: project => ({
    namespace: "project",
    key: project.id,
  }),
});

const Inspectable = types.capability("inspectable");
const DocumentBacked = types.capability("document-backed");
const Archived = types.capability("archived");

types.declareSubtype(Project, Entity);
types.implement(Project, Inspectable);
types.implement(Project, DocumentBacked);

const ActiveProject = types.difference(Project, Archived);

const ProjectOwnedBy = types.refinement(
  "project-owned-by",
  Project,
  {
    test(project, ownerId: string) {
      return project.ownerId === ownerId;
    },
  },
);

const MyActiveProject = types.and(
  ActiveProject,
  ProjectOwnedBy(currentUserId),
);
```

Acceptance:

```ts
const result = await pbui.accept({
  type: MyActiveProject,
  prompt: "Choose one of your active projects",
});
```

Action dispatch:

```ts
pbui.actions.define({
  id: "inspect-project",
  subject: types.and(Project, Inspectable),

  action(match) {
    return {
      id: "inspect",
      label: "Inspect project",
      verb: {
        type: "inspectProject",
        projectId: match.accepted.value.id,
      },
    };
  },
});
```

Context-sensitive action:

```ts
pbui.actions.define({
  id: "archive-project",
  subject: MyActiveProject,
  context: types.atom("administrative-context"),

  action(match) {
    return {
      id: "archive",
      label: "Archive",
      danger: true,
      verb: {
        type: "archiveProject",
        projectId: match.accepted.value.id,
      },
    };
  },
});
```

Translator:

```ts
pbui.translators.define({
  id: "project-id/to-project",
  from: types.atom("project-id"),
  to: Project,
  cost: 1,
  preservesIdentity: true,

  translate(reference, environment) {
    return environment.projects.get(reference.value);
  },
});
```

---

# 11. Static TypeScript and runtime PBUI types

You should treat these as two coordinated systems.

## TypeScript layer

The TypeScript layer checks that:

- callbacks consume the correct representation;
- translators return the declared target representation;
- action verbs have valid shapes;
- atomic type names correspond to the `Values` map;
- refinement arguments are correctly typed.

## Runtime semantic layer

The runtime layer decides:

- whether a concrete presentation satisfies a compound expression;
- whether a translator is applicable;
- which action method is most specific;
- whether cached evidence is current;
- whether two references identify the same object.

TypeScript’s types are erased at runtime, and a plugin-defined or environment-dependent semantic relation cannot be inferred solely from a structural TypeScript interface. Therefore the runtime registry must remain authoritative.

You can still produce good inference:

```ts
const ActiveProject = types.refine(
  Project,
  "active",
  (project): project is Project & ActiveProjectBrand =>
    !project.archived,
);
```

But I would avoid pretending that every dynamic refinement can become a permanently trustworthy TypeScript subtype. An object can become archived after the test succeeds.

Evidence with revision information is more honest than an unrestricted phantom brand.

---

# 12. Similar projects and systems

There is no mainstream JavaScript project that appears to reproduce CLIM’s complete combination of presentations, input contexts, command tables, translators, and output recording. There are, however, several systems that independently implement important parts of it.

## ArkType — closest TypeScript type-algebra precedent

ArkType is probably the most directly relevant JavaScript library for the type-expression layer. It describes itself as using set theory to expose runtime relationships between TypeScript-oriented types and supports runtime introspection such as checking whether one type extends another. It also supports custom narrowing expressions. citeturn769266search1turn769266search29

Useful lessons for PBUI:

- types can be runtime values;
- runtime types can expose `extends`;
- type expressions can be parsed and normalized;
- validators can be compiled;
- structural validation can coexist with TypeScript inference.

I would consider using ArkType to implement **structural leaf schemas**, but not use it as the complete PBUI semantic registry. ArkType does not own PBUI concepts such as:

- semantic object identity;
- presentation occurrence;
- command context;
- link groups;
- action tables;
- translators between application meanings.

A useful integration might be:

```ts
types.atom("project", {
  schema: ProjectArkType,
  identity: project => ["project", project.id],
});
```

## Elixir — closest modern language-theory precedent

Elixir’s type system is now perhaps the strongest practical precedent for your proposed semantic hierarchy. It is gradual, set-theoretic, and designed to model existing dynamic-language idioms using unions, intersections, negations, pattern matching, and guards. Elixir 1.20 completed the first milestone of type-inferencing and gradually checking all Elixir programs without requiring annotations. citeturn569191search8turn569191search4

Elixir also provides two useful operational patterns:

- pattern matching plus deliberately restricted guards for predictable refinement;
- protocols for behavior selected by data type. citeturn851218search2turn851218search5

PBUI could adopt Elixir’s conceptual split:

```text
pattern / atomic facts
    +
guard / refinement
    +
protocol / supported behavior
```

That maps well to:

```text
presentation atom
    +
selector refinement
    +
capability/action implementation
```

## Clojure multimethods — closest dispatch precedent

Clojure’s multimethod and hierarchy system is exceptionally relevant.

It allows independent ad hoc hierarchies over names rather than requiring class inheritance. Multimethod dispatch can use arbitrary values, including vectors, and ambiguities can be resolved with explicit preferences. citeturn630153search0

A PBUI action system modeled on Clojure could dispatch on:

```clojure
[subject-type input-context gesture]
```

For example:

```text
[project admin-context context-menu]
[field chart-encoding-context primary-click]
[tile link-target-context primary-click]
```

This may be a stronger conceptual basis for actions than attaching arrays of actions to descriptors.

## Clojure spec and Malli — predicates and schemas as data

Clojure spec treats predicates as specifications and supports conjunctions, alternatives, conforming, explanation, and generation. citeturn851218search1turn851218search6

Malli is a high-performance, data-driven schema system for Clojure and ClojureScript. It supports registries, transformations, multi-schemas, validation, and schema definitions represented as ordinary data. citeturn769266search3turn769266search19turn769266search23

Malli is a good precedent for making PBUI type expressions:

- immutable data;
- inspectable;
- serializable;
- registrable;
- compilable to validators;
- extensible without classes.

## Portal — closest presentation-oriented UI precedent

Portal is a Clojure data-inspection interface whose values can have multiple viewers. Viewer applicability is determined by predicates ranging from ordinary type checks to `clojure.spec` validation. Commands navigate from selected values to derived values. citeturn167864search0turn167864search8

That is very close to parts of PBUI:

```text
Portal value         ≈ PBUI semantic object
Portal viewer        ≈ presentation renderer/view
viewer predicate     ≈ presentation applicability
selected value       ≈ active presentation
Portal command       ≈ PBUI action/translator
history navigation   ≈ object traversal through commands
```

Portal is worth studying closely for interaction design, especially:

- selecting nested values;
- switching among valid viewers;
- command discovery;
- navigation history;
- keyboard-oriented object interaction.

## Glamorous Toolkit — closest object-centric environment

Glamorous Toolkit associates contextual views, actions, searches, and other tools with domain objects. Its moldable-development approach is based on making objects explorable through context-specific tools rather than forcing every domain into a fixed generic debugger. citeturn167864search2turn167864search6turn167864search22

This is highly aligned with the broader PBUI goal:

```text
object
  → several contextual presentations
  → applicable actions
  → navigable related objects
  → domain-specific explanation
```

GT is not a React library, but it is one of the strongest examples of where presentation-based object interfaces can lead.

## Fulcro — closest shared-identity precedent

Fulcro normalizes application entities so that multiple UI views of the same entity resolve to one normalized node. Different components can use the same ident while querying and rendering different subsets of the entity. citeturn167864search7turn167864search11

This is relevant to the object-identity side of PBUI:

```text
same entity
different components
different visual projections
shared normalized identity
```

Your subject-link mechanism goes beyond Fulcro’s entity normalization because it also models views intentionally sharing one selected subject, but Fulcro is a strong precedent for keeping UI occurrence identity separate from entity identity.

## Julia — action-method specificity

Julia is useful as a model for dispatch rather than runtime validation. Its methods are selected using the types of all arguments, and its type system is nominal and parametric. Concrete Julia types are final, with abstraction generally expressed through abstract supertypes. citeturn569191search2turn569191search5

Useful PBUI lessons:

- do not assign behavior to one privileged receiver;
- derive method specificity from type relationships;
- distinguish conversion from dispatch;
- avoid encoding arbitrary changing values into types purely to obtain dispatch. Julia’s own performance guide warns against overusing values as type parameters. citeturn569191search9

## Lively.next — JavaScript object environment

Lively.next is a browser-based JavaScript programming environment centered on inspecting live object state and modifying behavior at runtime. It is closer to Smalltalk’s Morphic tradition than to CLIM, but its object inspectors and live tooling are relevant to the development experience around PBUI. citeturn473031search10

## Observable Inspector

Observable’s open-source Inspector can render arbitrary JavaScript values into DOM output and is integrated with Observable’s reactive runtime. It is not a semantic presentation/action system, but it is a useful reference for generic value rendering and reactive recomputation. citeturn473031search11turn473031search15

---

# 13. What I would actually implement next

I would avoid jumping directly from the current nominal graph to a complete Boolean type engine. A four-stage migration would be safer.

## Stage 1 — capabilities and parameterized refinements

Keep the current atomic subtype DAG, then add:

```ts
types.capability(...)
types.implement(...)
types.refinement(...)
types.parameterized(...)
```

Extend selectors to accept:

```ts
type: TypeExpr
```

Internally, simple atoms can continue using the current implementation.

## Stage 2 — evidence-producing matching

Change:

```ts
accept(reference): PresentationReference | null
```

to an internal operation like:

```ts
match(reference, expression): MatchResult
```

Keep the public acceptance return value compatible, but expose evidence through an advanced API and developer tools.

## Stage 3 — multimethod action dispatcher

Replace or supplement action-selector arrays with:

```ts
actions.define({
  subject: TypeExpr,
  context?: TypeExpr,
  gesture?: GestureExpr,
  method: ...
});
```

Calculate specificity from subtype relations. Retain `priority` only as an explicit ambiguity resolution mechanism.

## Stage 4 — union, intersection, and difference compiler

Add:

```ts
types.or(...)
types.and(...)
types.difference(...)
```

Compile expressions into:

- atomic bit masks;
- positive rule indices;
- refinement predicates;
- revision-aware caches.

Only introduce BDDs if real application expressions show normalization blow-up.

---

# 14. Recommended conceptual model

The resulting architecture would have six independent protocols:

```text
1. Representation
   What JavaScript value is carried?

2. Semantic type
   What set of acceptable presentations does this belong to?

3. Identity
   Which application object does it denote?

4. Refinement evidence
   Which environment-dependent propositions currently hold?

5. Translation
   How can it become another representation or semantic role?

6. Behavior dispatch
   Which actions, views, or commands apply in this context?
```

That gives you a cleaner answer to common questions:

```text
Is Project a kind of Entity?
    → subtype relation

Can a ProjectId be used where a Project is requested?
    → translator

Do two references denote the same project?
    → semantic identity

May this user archive this project now?
    → refinement predicate

Does this object support inspection?
    → capability

Which archive implementation wins here?
    → multimethod specificity

Should two views follow the same document?
    → subject-binding identity
```

The central principle is:

> Use subtyping only for substitutability. Use capabilities for behavior, refinements for propositions, translations for representation changes, and identities for sameness.

That would preserve the best part of CLIM’s presentation-type model while incorporating ideas from semantic subtyping, refinement typing, protocols, multimethods, normalized entity systems, and modern object-centric development environments.


---

> Write a whole textbook building up to this API, so that I can follow it from base principles, and see what can be left out or what can be added or modified. ALso cite and reference other textbooks and resources ande xisting implementations and such. Add exercises as well. A real textbook.

<details><summary>💭 Thinking</summary>

**Planning the textbook**

I’m treating this as a substantial technical writing project: I’ll inspect the existing project context, research authoritative references and implementations, then organize a rigorous textbook with explanations, examples, exercises, and citations.

**Planned the textbook**

</details>

```unknown
bash -lc ls -lah /mnt/data && find /mnt/data -maxdepth 2 -type f | sed -n '1,240p'
```

I’ll create a standalone Markdown textbook grounded in the repository, progressing from foundations to the API through implementation, alternatives, exercises, projects, verified references, and an annotated bibliography.


---

> the whole type theory / mathematical foudnations / proof component of it is very interesting to me

<details><summary>💭 Thinking</summary>

The user is especially interested in the type theory, mathematical foundations, and proof-oriented aspects of the textbook and UI/API design.

**Developing the textbook**

I’m narrowing the scope to a coherent, publishable guide: establish the concepts, compare design choices, build incrementally toward the proposed API, and include exercises, implementation notes, and carefully selected references.

**Developed the textbook**

**Inspected source files and PDF creation guidelines for textbook drafting**

</details>

```unknown
bash -lc ls -lah /mnt/data && find /mnt/data -maxdepth 2 -type f | sed -n '1,200p'
```

Mathematics will be a primary strand: sets, relations, lattices, propositions-as-types, subtyping judgments, refinement evidence, coercions, ambiguity proofs, and executable registry laws.

<details><summary>💭 Thinking</summary>

**Selecting references**

I’m assembling sources spanning type theory, runtimes, pattern matching, refinement systems, dispatch, testing, and practical JavaScript libraries. I’ll use them to justify the API while identifying simplifications and worthwhile extensions.

**Selected references**

**Inspected project files, Git status, and textbook presentation code**

</details>

```json
{"search_query":[{"q":"CLIM II specification presentations presentation types input contexts translators command tables PDF"},{"q":"McCLIM manual presentations presentation translators command tables output recording"},{"q":"Common Lisp Interface Manager paper presentation based user interfaces CLIM PDF"},{"q":"CLIM presentation based user interfaces application frames output records specification"}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Structuring the book**

I’m shaping a full progression from mathematical foundations and semantic typing to runtime architecture, React integration, testing, design tradeoffs, case studies, appendices, and a curated bibliography.

**Structured the book**

</details>

Inference rules, soundness statements, proof sketches, and property tests will connect the formal model directly to concrete API decisions.

<details><summary>💭 Thinking</summary>

**Searched 33 websites**

</details>

```unknown
bash -lc cd /mnt/data/pbui_book_work/pbui && cat package.json && cat tsconfig.json && sed -n '1,240p' README.md
```

<details><summary>💭 Thinking</summary>

**Used container tool**

</details>

```json
{"search_query":[{"q":"QuickCheck lightweight tool for random testing Haskell paper PDF"},{"q":"fast-check official TypeScript property based testing documentation"},{"q":"algebraic laws property based testing software design official paper"},{"q":"TLA+ book Specifying Systems official PDF"}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Building the foundations**

I’m turning the project into a mathematically grounded textbook, moving from sets, orders, lattices, judgments, and proofs toward semantic types, refinement evidence, dispatch, and the final presentation API.

**Built the foundations**

**Searched 31 websites**

</details>

```unknown
bash -lc set -euo pipefail
printf '%s\n' '--- work tree ---'
find /mnt/data/pbui_book_work -maxdepth 3 -type f | sed 's#^/mnt/data/pbui_book_work/##' | sort | head -220
printf '\n--- PBUI package ---\n'
cd /mnt/data/pbui_book_work/pbui
pwd
ls -la
printf '\n--- presentation sources ---\n'
find src/presentation -maxdepth 2 -type f -print | sort
printf '\n--- docs ---\n'
find docs -maxdepth 3 -type f -print | sort 2>/dev/null || true

```

<details><summary>💭 Thinking</summary>

**Inspected textbook workspace, source files, and baseline documentation**

</details>

```json
{"open":[{"ref_id":"turn665971search32"},{"ref_id":"turn240609search12"},{"ref_id":"turn864788search0"},{"ref_id":"turn864788search2"},{"ref_id":"turn679815search0"},{"ref_id":"turn751875search0"}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Searched 3 websites**

</details>

```unknown
bash -lc set -euo pipefail
cd /mnt/data/pbui_book_work/pbui
mkdir -p docs/textbook/code docs/textbook/figures
cat > docs/textbook/README.md <<'EOF'
# Semantic Presentations

## Type Theory and Architecture for Object-Centric User Interfaces

**A textbook companion to PBUI**

This book develops a presentation-based user-interface architecture from first principles. It begins with ordinary React components, reconstructs the semantic ideas behind the Common Lisp Interface Manager (CLIM), develops the required mathematics and type theory, and derives an implementable TypeScript API for semantic presentation types, refinements, evidence-producing matching, translators, multimethod actions, identity, and linked views.

The mathematical chapters are not optional decoration. They state the semantic contracts that the implementation is intended to satisfy and identify exactly where JavaScript callbacks must be trusted.

## Reading paths

- **Application engineer:** Chapters 1–3, 8–10, 15–19, 21, and 23.
- **Type-theory path:** Chapters 4–14, 16–17, 20, and 24.
- **CLIM and interaction-design path:** Chapters 1–3, 12–14, 18–19, and 22.
- **Implementer:** Read in order and work through the companion code in [`code/`](code/).

## Parts and chapters

### Part I — From widgets to semantic interaction

1. [Objects, occurrences, and interaction meaning](01-objects-and-presentations.md)
2. [CLIM as an interaction architecture](02-clim.md)
3. [The baseline PBUI and its pressure points](03-baseline-pbui.md)

### Part II — Mathematical foundations

4. [Sets, predicates, functions, and relations](04-sets-relations.md)
5. [Preorders, partial orders, lattices, and Boolean structure](05-orders-lattices.md)
6. [Judgments, inference rules, induction, and metatheory](06-judgments-proofs.md)
7. [Propositions as types and evidence as data](07-curry-howard-evidence.md)

### Part III — A type theory for presentations

8. [Nominal, structural, and semantic subtyping](08-subtyping.md)
9. [Union, intersection, difference, and negation](09-set-theoretic-types.md)
10. [Refinements, occurrence typing, and gradual knowledge](10-refinements.md)
11. [Parameterized and dependent presentation types](11-parameterized-types.md)
12. [Capabilities, protocols, and type classes](12-capabilities.md)
13. [Translations, coercions, effects, and identity preservation](13-translations.md)
14. [Multiple dispatch and action-method specificity](14-multiple-dispatch.md)

### Part IV — Deriving and implementing the API

15. [The `TypeExpr` language and registry](15-type-expr-api.md)
16. [Evidence-producing matching](16-evidence-matching.md)
17. [Compilation, indexing, caching, and invalidation](17-performance.md)
18. [Semantic identity, view identity, and subject bindings](18-identity-bindings.md)
19. [React input contexts, presentations, actions, and accessibility](19-react-integration.md)
20. [Executable laws, property tests, models, and proofs](20-testing-and-formal-methods.md)

### Part V — Choosing a design

21. [Minimal, intermediate, and maximal profiles](21-design-profiles.md)
22. [Related systems and reusable ideas](22-related-systems.md)
23. [Datalab case study: linked analytical views](23-datalab-case-study.md)
24. [Limits, extensions, and research directions](24-future-directions.md)

### Appendices

- [A. Complete proposed API](appendix-a-api.md)
- [B. Selected exercise solutions](appendix-b-solutions.md)
- [C. Notation and laws](appendix-c-notation.md)
- [Bibliography and annotated resources](bibliography.md)

## Exercise notation

Exercises are marked by purpose:

- **[R]** reasoning or reading comprehension;
- **[C]** coding;
- **[P]** proof;
- **[D]** architecture or design;
- **[X]** extended project.

A diamond, **◆**, indicates an exercise with a selected solution in Appendix B.

## Companion implementation

The [`code/`](code/) directory contains a dependency-free reference implementation of the core calculus. It is deliberately smaller than a production package. Its purpose is to make definitions executable, expose proof obligations as laws, and show where a production PBUI can add indexing, React integration, remote protocols, and application-specific effects.
EOF

cat > docs/textbook/00-front-matter.md <<'EOF'
# Semantic Presentations

## Type Theory and Architecture for Object-Centric User Interfaces

### A textbook companion to PBUI

**Edition:** August 2026  
**Implementation language:** TypeScript and React  
**Primary historical reference:** the Common Lisp Interface Manager  
**Primary formal theme:** semantic subtyping with evidence-producing runtime matching

---

## Preface

A graphical interface displays rectangles, text, paths, tables, and controls. A user, however, rarely thinks in those terms. The user sees a project, a document, a pipeline stage, a chart mark, a person, or a field named `temperature`. The difference between pixels and objects is the central subject of this book.

A conventional component architecture normally assigns behavior where output is rendered:

```tsx
<button onClick={() => archive(project.id)}>Archive</button>
```

That code is clear, local, and often correct. It becomes less satisfactory when the same object appears in ten places, when an operation must accept any currently visible occurrence of a suitable object, or when the available operation depends jointly on the object, the current command, the user’s authority, and a second selected object. The architecture begins to duplicate semantic knowledge across components.

Presentation-based user interfaces reverse the dependency. Rendered output is explicitly associated with an application object and a semantic presentation type. A temporary input context can then ask for an object satisfying a type expression. Existing output becomes sensitive when it can provide such an object. Actions can be selected from the object and context rather than permanently wired into each visual occurrence.

The Common Lisp Interface Manager developed a mature version of this architecture. CLIM presentations associate output with application objects and presentation types; input contexts state what type of object is being requested; presentation translators connect displayed objects to command arguments; and command tables organize commands, menus, and translators. The architecture is broader than the subset implemented by PBUI, but its separations remain unusually useful.

Forty years of programming-language research also gives us better formal tools than a simple inheritance tree. Set-theoretic and semantic-subtyping systems interpret a type as a set of values. Refinement types describe subsets using propositions. Occurrence typing records knowledge established by predicates. Protocols and type classes separate supported behavior from nominal ancestry. Multiple dispatch selects behavior from several arguments. Proof-relevant judgments return evidence rather than a bare Boolean.

This book combines those lines of work into a practical architecture for a React application.

## What this book proves—and what it does not

The formal development defines a small core system, **SP**, for semantic presentations. Its central judgment has the form

\[
R; E \vdash r \Downarrow \tau \Rightarrow w
\]

and is read:

> Under registry \(R\) and environment \(E\), reference \(r\) matches presentation type expression \(\tau\), producing witness \(w\).

For the pure fragment, the book establishes a relative soundness result:

\[
R;E \vdash r \Downarrow \tau \Rightarrow w
\quad\Longrightarrow\quad
r \in \llbracket \tau \rrbracket_{R,E}.
\]

The result is *relative* because a JavaScript application supplies atomic classifiers, refinement predicates, identity functions, and translators. A proof about the registry cannot establish that an arbitrary callback tells the truth. It can establish that, assuming those trusted primitives satisfy their declared contracts, the composition machinery preserves the meaning of the type language.

The book also proves or sketches:

- reflexivity and transitivity of semantic subtyping;
- lattice laws for union and intersection;
- soundness of match witnesses by induction on derivations;
- termination of matching for finite type expressions and bounded translation search;
- conditions under which action dispatch has a unique most-specific method;
- conditions for sound memoization using dependency fingerprints;
- equivalence-relation laws required of semantic identity.

It does **not** claim that TypeScript is a proof assistant, that runtime application state is immutable, or that opaque predicates can be decided symbolically. Several chapters identify the exact boundary between proved infrastructure and trusted application code.

## Prerequisites

The programming chapters assume familiarity with:

- JavaScript or TypeScript;
- React components, context, and state;
- elementary functional-programming notation.

The mathematics starts with sets and relations. Prior exposure to discrete mathematics helps but is not required. Proofs are introduced as structured engineering arguments rather than as a prerequisite.

## Conventions

TypeScript code uses `readonly` aggressively because immutable descriptions are easier to normalize, hash, cache, and reason about. This is a design convention, not a claim that all application objects are immutable.

The notation \(\mathcal P(X)\) denotes the power set of \(X\). The symbol \(\subseteq\) denotes subset inclusion. The symbol \(\sqsubseteq\) is occasionally used for an implementation order or information order. The symbol \(<:\) denotes subtyping. Appendix C collects the notation and laws.

## A running example

The main examples use analytical projects and documents:

```ts
interface Project {
  id: string;
  title: string;
  ownerId: string;
  archived: boolean;
  revision: number;
}

interface Document {
  id: string;
  title: string;
  revision: number;
}

interface Values {
  entity: { id: string };
  project: Project;
  projectId: string;
  document: Document;
  tile: { placementId: string; viewId: string };
}
```

A project card and a project-ID token may present different representations while denoting the same project. A chart tile and a pipeline tile may be distinct views while sharing a document-selection binding. An administrator may see an archive action that an ordinary workspace does not contribute. These cases are simple enough to explain and rich enough to expose the important distinctions.

## Recommended companion reading

This book is not a substitute for general programming-language texts. Benjamin Pierce’s *Types and Programming Languages* is a standard route into operational semantics, subtyping, and type safety. Robert Harper’s *Practical Foundations for Programming Languages* emphasizes judgments and language structure. *Software Foundations* and *Programming Language Foundations in Agda* teach machine-checked proofs. Girard, Lafont, and Taylor’s *Proofs and Types* develops the Curry–Howard correspondence. Davey and Priestley’s *Introduction to Lattices and Order* provides the order-theoretic background. The bibliography gives annotated paths through these and implementation-oriented resources.
EOF

```

The calculus separates decidable instance matching from potentially unknown universal subtyping, using proved/refuted/unknown outcomes. It favors relative difference over unstable global negation in extensible registries.

<details><summary>💭 Thinking</summary>

**Checking Textbook Word Counts**

</details>

```json
{"open":[{"ref_id":"turn240609search7"},{"ref_id":"turn240609search1"},{"ref_id":"turn552726search2"},{"ref_id":"turn552726search16"},{"ref_id":"turn864788search1"},{"ref_id":"turn103017search0"},{"ref_id":"turn103017search2"}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Searched 6 websites**

</details>

```unknown
bash -lc set -euo pipefail
cd /mnt/data/pbui_book_work/pbui
cat > docs/textbook/08-subtyping.md <<'EOF'
# Chapter 8 — Nominal, Structural, and Semantic Subtyping

## 8.1 One word, several relations

“Subtyping” is used for several distinct ideas. A careful PBUI design must state which relation it means.

### Nominal subtyping

A declaration establishes the relation:

```ts
types.declareSubtype(Project, Entity);
```

The names and registry declaration matter. Two atoms with identical representations are not related unless declared.

### Structural subtyping

A value of one static type can be used where another is expected because it has the required members:

```ts
interface Entity {
  id: string;
}

interface Project {
  id: string;
  title: string;
}
```

TypeScript considers `Project` assignable to `Entity`. This is a compile-time representation relation. TypeScript’s official documentation describes its compatibility relation as structural, reflecting common JavaScript patterns.

### Semantic subtyping

A type is a set of references, and

\[
\tau <: \sigma
\]

means denotational inclusion. Union, intersection, and difference participate directly in the relation.

These views can cooperate, but they are not interchangeable.

## 8.2 Representation safety

Suppose an action method registered for `Entity` receives a reference tagged `Project` through nominal subtyping. The callback may access `reference.value.id`. This is safe only if the project representation can be passed to code expecting the entity representation.

A TypeScript declaration can enforce a sufficient condition:

```ts
type SafeSupertypeMap<Values extends object> = Partial<{
  [Sub in keyof Values]: {
    [Sup in keyof Values]:
      Values[Sub] extends Values[Sup] ? Sup : never
  }[keyof Values]
}>;
```

The exact implementation can be improved, but the contract is:

\[
V_{sub} \subseteq_{repr} V_{super}.
\]

This is a static representation check, not the semantic subtype definition itself.

### Unsafe declaration

```ts
interface Values {
  project: Project;
  projectId: string;
}

// Semantically related, but representation-unsafe.
types.declareSubtype(types.atom("projectId"), types.atom("project"));
```

A string cannot be passed directly to a project callback. The relation needs a translator.

## 8.3 The subsumption rule

Subtyping becomes useful through **subsumption**:

\[
\frac{
  R;E \vdash r \Downarrow \tau \Rightarrow w
  \qquad
  R \vdash \tau <: \sigma
}{
  R;E \vdash r \Downarrow \sigma
  \Rightarrow \mathsf{subsume}(w,\tau<:\sigma)
}
\;\textsc{M-Sub}
\]

If a project matches `Project` and `Project <: Entity`, it also matches `Entity`. Evidence records the subtype path or proof.

In a nominal DAG, the proof can be a path:

```ts
{
  kind: "subtype",
  path: ["specialProject", "project", "entity"],
  evidence: atomEvidence,
}
```

In a set-theoretic compiler, subtyping may be proved by normalization and emptiness rather than an explicit nominal path. Evidence can record a theorem ID or normalized inclusion certificate.

## 8.4 Variance

Parameterized presentation types introduce variance. Suppose `Collection<T>` denotes collections whose elements satisfy `T`.

A constructor is **covariant** when

\[
A <: B \Rightarrow C(A) <: C(B).
\]

Read-only collections are naturally covariant: a collection of projects can be viewed as a collection of entities.

A constructor is **contravariant** when

\[
A <: B \Rightarrow C(B) <: C(A).
\]

Input consumers are contravariant. A function that accepts any entity can be used where a function accepting projects is required.

A constructor is **invariant** when neither relation is generally safe. Mutable containers are often invariant because they both produce and consume elements.

PBUI type constructors should declare variance only when their semantic and representation behavior justifies it:

```ts
types.constructor("sequence-of", {
  parameters: [{ variance: "covariant" }],
  ...
});
```

For application-specific refinements such as `FieldOf(documentId)`, the parameter is a value index rather than a type parameter; variance may not apply.

## 8.5 Function types and action handlers

A function type obeys:

\[
A_2 <: A_1
\qquad
B_1 <: B_2
\]

implies

\[
(A_1 \to B_1) <: (A_2 \to B_2).
\]

Inputs are contravariant; outputs are covariant.

This matters when typing action rules. A method registered for broad references can safely handle a narrower dispatch result, but a method requiring `Project` cannot be installed where the dispatcher may pass any `Entity`.

TypeScript contains deliberate unsoundness and historical variance compromises. PBUI should not infer runtime semantic safety solely from TypeScript assignability. The runtime registry and its declarations remain authoritative.

## 8.6 Semantic equivalence

Define:

\[
\tau \simeq \sigma
\quad\text{iff}\quad
\tau <: \sigma \land \sigma <: \tau.
\]

This is an equivalence relation over expressions. It identifies expressions with equal denotations when subtyping is complete.

Examples:

\[
A \land A \simeq A
\]

\[
A \lor \bot \simeq A
\]

\[
A \land (B \lor C)
\simeq
(A \land B) \lor (A \land C).
\]

Opaque refinements make algorithmic equivalence incomplete. Two named predicates may happen to return the same result for every reference, but PBUI cannot prove that from function identity. Therefore:

```text
semantic truth       may exceed
registry-provable truth
```

The API should distinguish `isSubtypeProvable` from a misleading absolute `isSubtype` when unknown results are possible.

```ts
type Decision =
  | { kind: "yes"; proof: SubtypeProof }
  | { kind: "no"; counterexample?: Reference }
  | { kind: "unknown"; reason: string };
```

For fully structural expressions over decidable atoms, the result can be complete.

## 8.7 Width and depth subtyping are not presentation inheritance

Structural record subtyping includes notions such as:

- **width:** a record with more fields can satisfy a record requiring fewer;
- **depth:** field types can vary covariantly when safe;
- **permutation:** field order is irrelevant.

These are useful for TypeScript callback safety. They should not automatically create semantic presentation relations.

Two records may both contain `{ id: string }` but denote unrelated domains. Structural similarity does not imply that a document should appear in a command asking for a user.

A reliable policy is:

> Static structure may reject an unsafe declared semantic relation, but it should not silently invent a semantic relation.

## 8.8 Nominal atoms inside a semantic algebra

The recommended architecture combines nominal leaves with set-theoretic composition:

```text
nominal atoms:
  Project, Entity, Document, Archived

declared nominal relation:
  Project <: Entity

semantic expressions:
  Project ∧ Inspectable
  Project \ Archived
  Project ∨ Workspace
```

This gives stable application vocabulary without forcing every combination into the nominal graph.

Capabilities may also be nominal atoms whose membership is declared or computed. The distinction is organizational:

- a domain atom primarily names what an object is;
- a capability atom primarily names behavior it supports;
- the semantic engine treats both as sets.

## 8.9 Coherence of declarations

A registry should validate declarations at construction time.

### Acyclic nominal graph

Reject `A <: B`, `B <: C`, `C <: A` unless the system explicitly supports type aliases or equivalence classes.

### Representation compatibility

When subtype callbacks are shared across atom tags, verify a TypeScript-level sufficient condition or require an explicit unsafe declaration.

### Duplicate identifiers

Reject conflicting definitions of one atom or refinement ID.

### Stable declarations

Do not let the meaning of a declared nominal subtype depend on the current user or mutable environment. Contextual subsets belong in refinements.

### Open-world versioning

If plugins may extend the registry, assign a registry version. Compiled expressions and negative evidence are valid only against the version in which they were constructed.

## 8.10 Exercises

1. **[R]** Distinguish nominal, structural, and semantic subtyping using one example of each.
2. **[P]** Derive `SpecialProject <: Entity` from two nominal edges.
3. **[C]** Define a TypeScript helper that allows `Sub -> Super` only when `Values[Sub] extends Values[Super]`.
4. **[D]** Give a semantic subtype relation that TypeScript structure cannot discover automatically.
5. **[D]** Give a TypeScript structural assignment that should not create a presentation subtype.
6. **[P] ◆** Prove that mutual semantic subtyping is an equivalence relation.
7. **[R]** Explain why mutable `Collection<T>` is generally not covariant.
8. **[C]** Return `yes | no | unknown` from a subtype checker containing opaque refinements.
9. **[X]** Design a plugin registration protocol that permits new subtypes while preserving versioned compiled expressions.
EOF

cat > docs/textbook/09-set-theoretic-types.md <<'EOF'
# Chapter 9 — Union, Intersection, Difference, and Negation

## 9.1 Semantic subtyping

In semantic subtyping, types are interpreted as sets and type connectives use set operations. This approach has been developed extensively in research on set-theoretic types and implemented in systems such as CDuce. More recently, Elixir has adopted a gradual set-theoretic type system whose public documentation presents unions, intersections, negations, top, bottom, and a distinct `dynamic` notion.

For PBUI, the attraction is direct: input contexts already describe sets of acceptable references. Giving those sets an algebra makes selectors compositional and inspectable.

## 9.2 Grammar

A practical core grammar is:

\[
\tau ::= \top
\mid \bot
\mid a
\mid \tau \lor \tau
\mid \tau \land \tau
\mid \tau \setminus \tau
\mid \operatorname{refine}(\tau,p,\vec v).
\]

A richer internal grammar may include complement:

\[
\neg \tau.
\]

Difference can be defined from complement:

\[
\tau \setminus \sigma = \tau \land \neg\sigma.
\]

For an open UI registry, exposing restricted difference is usually safer than exposing unrestricted complement.

## 9.3 Union

A union expresses alternatives:

```ts
const SelectableContainer = types.or(Project, Workspace, Folder);
```

Matching succeeds if at least one branch succeeds. Union is useful for:

- commands accepting several domain categories;
- compatibility layers during migration;
- heterogeneous palettes;
- action rules that apply to a finite family of atoms.

A union should be normalized:

```text
or(A, or(B, A), bottom)
    ↦ or(A, B)
```

The order of members should be canonical for hashing, but UI explanation may preserve source order separately.

## 9.4 Intersection

An intersection composes independent properties:

```ts
const EditableProject = types.and(Project, Editable);
```

This avoids nominal combinatorial explosion. Without intersection, one might invent:

```text
EditableProject
InspectableProject
EditableInspectableProject
ArchivedInspectableProject
```

Intersections also provide a uniform dispatch language:

```ts
subject: types.and(DocumentBacked, Linkable)
```

A successful match must carry evidence for every member.

## 9.5 Difference

Difference expresses a positive base and an exclusion:

```ts
const ActiveProject = types.difference(Project, Archived);
```

Compared with a refinement named `active-project`, difference exposes more structure:

- it can participate in Boolean simplification;
- it explains failure as excluded membership;
- it may permit subtype proofs;
- it can reuse existing `Archived` classification.

Difference is especially natural for state-machine exclusions:

```text
EditableDocument = Document \ Locked
VisibleTile      = Tile \ Hidden
AvailableCommand = Command \ Disabled
```

It is only correct when the excluded type is meaningful over the base. The expression remains mathematically defined otherwise, but may be surprising.

## 9.6 Global negation and the universe problem

The complement of `Archived` requires a universe:

```text
all references that are not archived
```

Does that include users, documents, gestures, action contexts, and values registered by future plugins? A global complement can become larger after registry extension.

Three policies are available.

### Closed registry

Freeze the registry before compilation. Complement is relative to the frozen reference universe.

```ts
const compiled = types.compile(expression, {
  registryVersion: registry.version,
});
```

Adding atoms creates a new version and invalidates compiled complements.

### Base-relative difference

Expose only:

```ts
types.difference(base, excluded)
```

Then `Project \ Archived` remains stable even when unrelated atoms are added, assuming `Project` itself is stable.

### Typed negation

Require a universe argument:

```ts
types.notWithin(Project, Archived)
```

This is syntactic sugar for difference and makes the boundary explicit.

The recommended public API uses difference. An advanced compiler may retain complement internally.

## 9.7 Top, bottom, and dynamic

Top and bottom have precise meanings:

\[
\llbracket\top\rrbracket = \mathrm{Ref}
\]

\[
\llbracket\bot\rrbracket = \varnothing.
\]

`top` means every valid semantic reference. It is not an unchecked escape hatch.

A gradual system may also need **dynamic**, meaning that static knowledge is incomplete and runtime checks remain. Elixir’s documentation distinguishes `dynamic()` from its all-values type. PBUI can make a similar distinction:

```ts
type StaticDecision =
  | { kind: "proved"; type: TypeExpr }
  | { kind: "dynamic"; upperBound: TypeExpr };
```

For the runtime PBUI registry, every match is already dynamic in the ordinary sense of happening at runtime. A separate `dynamic` type becomes useful only if the type-expression compiler also performs static reasoning or crosses typed and untyped plugin boundaries.

Do not use `top` to mean “unknown.” Unknown information and universal membership are different concepts.

## 9.8 Subtyping by emptiness

In a Boolean algebra:

\[
\tau <: \sigma
\quad\text{iff}\quad
\tau \land \neg\sigma \simeq \bot.
\]

With difference:

\[
\tau <: \sigma
\quad\text{iff}\quad
\tau \setminus \sigma \simeq \bot.
\]

This turns subtype checking into an emptiness problem. For finite nominal atoms represented by Boolean decision structures, emptiness can be decided efficiently.

Opaque refinements break completeness. The compiler may know:

```text
OwnedBy(alice) <: Project
```

because the refinement declares `Project` as its base. It generally cannot prove:

```text
OwnedBy(alice) <: VisibleTo(alice)
```

unless a trusted implication is declared.

A refinement registry can optionally expose logical relationships:

```ts
registry.declareImplication({
  from: OwnedBy(userId),
  to: VisibleTo(userId),
  proof: "owners-can-view",
});
```

Such declarations should be rare and domain-reviewed.

## 9.9 Normal forms

One implementation strategy converts formulas to disjunctive normal form:

```text
(A ∧ B) ∨ (C ∧ ¬D)
```

represented as clauses:

```ts
interface Clause {
  positive: readonly Atom[];
  negative: readonly Atom[];
  refinements: readonly Refinement[];
}
```

DNF is simple and excellent for small expressions. Distribution can cause exponential growth:

```text
(A₁ ∨ A₂) ∧ (B₁ ∨ B₂) ∧ (C₁ ∨ C₂)
```

produces eight clauses. The Elixir implementation team publicly documented moving beyond naive DNF toward binary decision diagrams as negation-heavy inference made blow-ups operationally significant.

For PBUI:

1. begin with a shared expression DAG and modest normalization;
2. use bitsets and candidate indexes;
3. measure expression sizes in real applications;
4. introduce BDDs only if profiling justifies the complexity.

## 9.10 Binary decision diagrams

A reduced ordered binary decision diagram represents a Boolean function as a canonical directed acyclic graph relative to a variable order. Shared nodes avoid repeated subformulas. Union, intersection, and negation become graph operations with memoization.

Advantages:

- canonical equality under a fixed atom order;
- compact sharing for many formulas;
- efficient Boolean operations;
- direct emptiness and implication checks.

Costs:

- performance depends strongly on variable ordering;
- refinements and parameterized atoms complicate the variable universe;
- implementation and debugging are nontrivial;
- canonicality is relative to the chosen atomic decomposition;
- dynamic registry extension may require reordering or versioned diagrams.

A PBUI BDD should treat opaque refinements as indivisible propositions. It cannot reason inside their JavaScript bodies.

## 9.11 Set-theoretic types and user-interface meaning

A semantic type algebra is valuable only if the atoms are meaningful. The expression

```text
Project ∧ Inspectable ∧ ¬Archived
```

is understandable because each atom has a domain interpretation. An algebra over arbitrary component names would merely formalize implementation accidents.

The registry should document each atom as a proposition:

```ts
{
  id: "archived",
  proposition: "the referenced domain object is archived",
  stability: "revision-dependent",
  universe: Project,
}
```

This metadata supports explainers, audits, and correct caching.

## 9.12 Exercises

1. **[C]** Build `or`, `and`, and `difference` constructors with flattening and identity simplifications.
2. **[P]** Prove De Morgan’s laws relative to a fixed universe.
3. **[R]** Why is `top` not the same as an unknown or dynamic type?
4. **[D] ◆** Choose a negation policy for a plugin-extensible PBUI and justify it.
5. **[P]** Prove the subtyping-by-emptiness equivalence.
6. **[C]** Convert `(A or B) and (C or D)` to DNF and represent it as clauses.
7. **[R]** Explain the source of DNF’s exponential blow-up.
8. **[D]** Identify the smallest conditions under which a BDD would be justified in your application.
9. **[X]** Implement a reduced ordered BDD for atomic capabilities and compare it with clause normalization on randomly generated expressions.
EOF

cat > docs/textbook/10-refinements.md <<'EOF'
# Chapter 10 — Refinements, Occurrence Typing, and Gradual Knowledge

## 10.1 Types refined by propositions

A refinement type has the form

\[
\{x : \tau \mid \varphi(x)\}.
\]

It denotes members of base type \(\tau\) satisfying proposition \(\varphi\):

\[
\llbracket \{x : \tau \mid \varphi(x)\} \rrbracket_{R,E}
=
\{r \in \llbracket\tau\rrbracket_{R,E} \mid \varphi(r,E)\}.
\]

Examples:

```text
{ p : Project | not p.archived }
{ p : Project | p.ownerId = currentUser.id }
{ f : Field   | f.documentId = activeDocument.id }
{ t : Tile    | t is currently mounted }
```

Refinement types connect the type algebra to application state. They are also the point at which full automatic reasoning usually stops.

## 10.2 Named refinements

An arbitrary lambda is useful but opaque:

```ts
types.refine(Project, project => !project.archived)
```

A named refinement exposes operational metadata:

```ts
const OwnedBy = types.refinement(
  "owned-by",
  Project,
  {
    check(project, ownerId: string, environment) {
      return project.ownerId === ownerId;
    },
    dependencies(project, ownerId, environment) {
      return [
        project.revision,
        ownerId,
        environment.authorizationEpoch,
      ];
    },
    cost: "cheap",
    purity: "environment-dependent",
  },
);
```

The constructor returns a function from refinement arguments to a type expression:

```ts
const Mine = OwnedBy(currentUser.id);
```

Named refinements can be:

- serialized by ID and arguments;
- indexed by base type;
- shown in explanations;
- assigned dependency policies;
- related to other refinements by trusted implications;
- tested independently.

## 10.3 Occurrence typing

Occurrence typing refines what is known about a value after a predicate test. Typed Racket is a prominent implementation: predicate types carry propositions learned on success and failure, allowing a union-typed variable to be narrowed differently in each branch.

PBUI has an analogous dynamic flow:

```text
unclassified presentation reference
        ↓ match Project
reference accompanied by Project evidence
        ↓ check OwnedBy(alice)
reference accompanied by Project ∧ OwnedBy(alice) evidence
```

The occurrence—not the object for all time—has been classified under a particular environment snapshot.

A React component can expose the narrowing through a callback:

```ts
const result = pbui.match(reference, MyActiveProject);

if (result.ok) {
  renderArchiveAffordance(result.match);
}
```

Static TypeScript narrowing may also be available for exact atomic references, but contextual propositions should be represented by evidence rather than permanent object brands.

## 10.4 Positive and negative propositions

A predicate can establish knowledge in both branches:

```text
if archived?(p):
  then p ∈ Archived
  else p ∈ Project \ Archived
```

This is safe only when:

- the predicate is total for the base type;
- the result is stable during the branch or protected by a revision;
- `Archived` is exactly characterized by the predicate.

Many application predicates establish only one-sided knowledge. For example, a permission service failure may mean “unknown” rather than “not permitted.” The API should support:

```ts
type CheckResult<W> =
  | { kind: "yes"; witness: W }
  | { kind: "no"; reason: Failure }
  | { kind: "unknown"; reason: Failure };
```

A two-valued Boolean silently conflates rejection with incomplete information.

## 10.5 Pure, contextual, volatile, and effectful checks

Refinement checks differ operationally.

### Structural

Depends only on immutable value shape:

```ts
project => project.kind === "analysis"
```

Can be cached by semantic identity and object revision.

### Pure contextual

Depends on explicit environment values but has no effects:

```ts
(project, env) => env.visibleProjectIds.has(project.id)
```

Cache using a relevant environment epoch.

### Volatile

Depends on current time, pointer state, viewport state, or mutable external data:

```ts
(tile, env) => env.now < tile.lockExpiresAt
```

Use operation-scoped caching or none.

### Asynchronous

Requires a permission lookup or loading:

```ts
(project, env) => env.permissions.canEdit(project.id)
```

Needs pending status, cancellation, and stale-result rejection.

### Effectful

Mutates state or asks the user a question. This should generally not be a refinement. It belongs in an action or translator phase.

The registry can classify checks:

```ts
type PredicateClass =
  | "structural"
  | "pure"
  | "contextual"
  | "volatile"
  | "async";
```

The class constrains caching and use in subtype proofs.

## 10.6 Refinement inference and decidable fragments

General refinement logic is undecidable. Liquid Types regain decidable inference by restricting refinements to conjunctions drawn from a finite set of logical qualifiers and solving generated subtyping constraints with predicate abstraction.

PBUI does not need whole-program refinement inference. It can still borrow the principle:

> Define a small analyzable fragment for common predicates, and retain arbitrary functions as opaque checks.

Example analyzable predicate AST:

```ts
type Proposition =
  | { kind: "eq"; path: readonly string[]; value: JsonValue }
  | { kind: "in"; path: readonly string[]; values: readonly JsonValue[] }
  | { kind: "has-capability"; id: string }
  | { kind: "and"; members: readonly Proposition[] }
  | { kind: "or"; members: readonly Proposition[] }
  | { kind: "not"; proposition: Proposition };
```

The compiler can serialize, index, and partially reason about this fragment. A `custom` node can call an arbitrary function when necessary.

## 10.7 Gradual knowledge

Gradual typing mixes statically known and dynamically checked information. PBUI’s analogous problem is mixing:

- registry-proved structural facts;
- runtime-refined facts;
- unknown plugin facts;
- asynchronously pending facts.

A useful status lattice is:

```ts
type Applicability =
  | { kind: "impossible"; reason: Failure }
  | { kind: "possible"; remaining: readonly Check[] }
  | { kind: "pending"; promise: Promise<Decision> }
  | { kind: "proven"; match: Match };
```

The UI can decide its policy:

- highlight only `proven` occurrences;
- show `possible` occurrences with a weaker cue;
- resolve asynchronous checks on hover or activation;
- prefetch checks for visible objects.

This is more faithful than pretending every classification is instantaneous.

## 10.8 Mutation and invalidation

Typed Racket’s occurrence-typing documentation warns about mutation because a fact learned about a location may become invalid after assignment. PBUI has the same issue in application state.

Suppose a match proves:

```text
project p is not archived at revision 7
```

An asynchronous operation archives the project and increments the revision to 8. The old evidence cannot authorize an archive affordance.

A witness should include a dependency fingerprint:

```ts
interface Fingerprint {
  registryVersion: number;
  objectRevision: string | number;
  environmentEpochs: readonly [string, string | number][];
}
```

Before commitment:

```ts
if (!registry.isCurrent(match.fingerprint, reference, environment)) {
  const fresh = registry.match(reference, expression, environment);
  if (!fresh.ok) return staleSelectionFailure;
}
```

## 10.9 Refinements versus capabilities

Both can denote subsets. Use a capability when the property primarily declares supported behavior and is relatively stable:

```text
Inspectable
DocumentBacked
Linkable
```

Use a refinement when the property is parameterized, contextual, or state-dependent:

```text
OwnedBy(userId)
FieldOf(documentId)
VisibleTo(userId)
NotArchivedAt(revision)
```

This is an architectural distinction, not a different set-theoretic foundation. Both can compile to atomic facts or predicates.

## 10.10 Exercises

1. **[R]** Write three application types in refinement notation `{x : T | φ(x)}`.
2. **[C]** Implement a named `OwnedBy(userId)` refinement with structured evidence and a dependency fingerprint.
3. **[D]** Classify five predicates as structural, contextual, volatile, asynchronous, or improperly effectful.
4. **[R]** Explain the connection between occurrence typing and a PBUI match object.
5. **[P] ◆** State conditions under which a failed total predicate establishes membership in `Base \ Refinement`.
6. **[D]** Decide whether “currently hovered” should be a refinement type, an occurrence property, or a gesture-context fact.
7. **[C]** Define a small serializable proposition AST and an evaluator for it.
8. **[R]** Why does a finite qualifier set help make Liquid Type inference decidable?
9. **[X]** Add asynchronous applicability to a presentation list without allowing stale permission results to highlight a newly changed object.
EOF

cat > docs/textbook/11-parameterized-types.md <<'EOF'
# Chapter 11 — Parameterized and Dependent Presentation Types

## 11.1 Avoiding nominal explosion

A system with only atomic names is tempted to create one atom for every contextual subset:

```text
FieldOfDocumentA
FieldOfDocumentB
FieldOfDocumentC
ProjectOwnedByAlice
ProjectOwnedByBob
```

These names are not stable vocabulary. They are applications of type constructors to values.

A parameterized presentation type has the form:

\[
F(v_1,\ldots,v_n).
\]

Examples:

```text
FieldOf(documentId)
OwnedBy(userId)
StageOf(pipelineId)
Permission(write)
RowOf(documentId, relationName)
```

## 11.2 Type constructors

A type constructor maps arguments to a type expression:

```ts
const FieldOf = types.parameterized(
  "field-of",
  Field,
  {
    check(field, documentId: string) {
      return field.documentId === documentId;
    },
  },
);

const FieldOfActiveDocument = FieldOf(activeDocument.id);
```

Semantically:

\[
\llbracket \mathrm{FieldOf}(d) \rrbracket
=
\{f \in \llbracket\mathrm{Field}\rrbracket
\mid \mathrm{documentId}(f)=d\}.
\]

The constructor ID and arguments form an inspectable, serializable type term.

## 11.3 Indexed families

A family of types indexed by values is a simple form of dependent typing. The type varies with a value:

\[
d : \mathrm{DocumentId}
\vdash
\mathrm{FieldOf}(d)\;\mathsf{type}.
\]

PBUI does not need a full dependent programming language. It needs runtime-indexed semantic sets.

The dependency appears in three places:

- matching compares object fields with the index;
- explanation displays the index;
- caching includes the index and relevant document revision.

```ts
await pbui.accept({
  type: FieldOf(document.id),
  prompt: `Choose a field from ${document.title}`,
});
```

## 11.4 Singleton types

A singleton type contains exactly one semantic object:

\[
\{r\}.
\]

An identity-based constructor can express it:

```ts
const SameObjectAs = types.singleton(reference);
```

This is useful for linked presentations:

```text
select another occurrence of the same project
find every mounted presentation of document d
link a view to the subject selected by this controller
```

The denotation should use semantic identity rather than JavaScript reference equality:

\[
\llbracket \mathrm{SameObjectAs}(r) \rrbracket_E
=
\{s \mid s \approx_E r\}.
\]

Because identity may depend on environment and registry version, singleton evidence needs the same snapshot discipline as refinements.

## 11.5 Existential types

Sometimes a command needs a value with some hidden index:

```text
there exists a document d such that this is a FieldOf(d)
```

Written:

\[
\exists d:\mathrm{DocumentId}.\;\mathrm{FieldOf}(d).
\]

The witness contains both the index and field evidence:

```ts
interface SomeField {
  documentId: string;
  field: Field;
  evidence: Evidence;
}
```

Ordinary `Field` may already be sufficient if the field value stores `documentId`. Existentials become more useful when the index is abstract or when actions must retain which constructor instance matched.

## 11.6 Universal types and polymorphic actions

A polymorphic action works for every index:

\[
\forall d.\; \mathrm{FieldOf}(d) \to \mathrm{Action}.
\]

In TypeScript, a generic function approximates this:

```ts
function inspectFieldOf<DocumentId extends string>(
  match: Match<FieldOf<DocumentId>>,
): Action {
  ...
}
```

At runtime, the registry dispatches on the constructor and passes the actual arguments in evidence.

A simpler API avoids exposing higher-rank generics:

```ts
actions.defineParameterized({
  constructor: FieldOf,
  action(match, [documentId]) {
    ...
  },
});
```

## 11.7 Variance of constructors

Type-indexed constructors may have type arguments rather than value arguments. Consider:

```text
SequenceOf(Project)
SequenceOf(Entity)
```

If sequences are read-only, then

\[
\mathrm{Project}<:\mathrm{Entity}
\Rightarrow
\mathrm{SequenceOf(Project)}<:\mathrm{SequenceOf(Entity)}.
\]

The constructor is covariant.

For a command-argument consumer:

```text
ConsumerOf(Entity) <: ConsumerOf(Project)
```

because something able to consume every entity can consume projects. The constructor is contravariant.

PBUI’s first implementation can omit higher-kinded constructors and support only value-indexed refinements. The design should reserve a place for declared variance rather than encoding it accidentally.

## 11.8 Equality of parameters

A constructor must define argument equality or canonicalization:

```ts
FieldOf("doc-1")
FieldOf(new String("doc-1"))
```

For serializable primitive arguments, canonical JSON or a stable tuple encoding is sufficient. For object arguments, prefer semantic IDs:

```ts
FieldOfDocument({ id: "doc-1", ... })
```

should normalize to:

```ts
FieldOf("doc-1")
```

Do not use arbitrary object serialization as an identity protocol.

## 11.9 Subtyping between instances

For equality-indexed families:

\[
\mathrm{FieldOf}(d_1) <: \mathrm{FieldOf}(d_2)
\]

only when \(d_1=d_2\). Every instance is a subtype of its base:

\[
\mathrm{FieldOf}(d) <: \mathrm{Field}.
\]

Other constructors may define richer index orders. If access levels form

```text
read <: write <: administer
```

one must decide whether `Permission(write)` is a subtype or supertype of `Permission(read)` based on the proposition being denoted:

- “has at least permission level L” is contravariant in the threshold;
- “has exactly level L” is invariant.

The constructor’s semantics determines variance; names alone do not.

## 11.10 Serialization and remote use

Parameterized expressions are attractive for protocols because they can be data:

```json
{
  "kind": "parameterized",
  "constructor": "field-of",
  "args": ["doc-17"]
}
```

Only registered constructors may be interpreted. Arbitrary JavaScript predicates cannot cross a process boundary.

A safe decoder validates:

- constructor ID exists;
- argument schema is correct;
- expression depth and size are bounded;
- the caller is allowed to request the type;
- refinements do not trigger unauthorized data exposure.

A remote type expression is a query. Treat it with the same resource and authorization controls as any other query language.

## 11.11 Exercises

1. **[R]** Replace three dynamically generated nominal type names with one parameterized constructor.
2. **[C]** Implement `FieldOf(documentId)` as a named refinement constructor.
3. **[P]** Prove `FieldOf(d) <: Field` from its denotation.
4. **[P] ◆** Characterize when `FieldOf(d₁) <: FieldOf(d₂)` under equality indexing.
5. **[D]** Decide whether `Permission(level)` means exact level or at least level; derive the resulting variance.
6. **[C]** Implement a singleton semantic type using registry identity.
7. **[R]** Explain the evidence carried by an existential `∃d. FieldOf(d)`.
8. **[D]** Define a JSON schema and resource limits for remotely supplied type expressions.
9. **[X]** Add a covariant read-only `CollectionOf(T)` constructor to the companion type system and prove its subtype rule sound.
EOF

```

<details><summary>💭 Thinking</summary>

**Drafted and documented Chapters 8–14, then counted textbook words**

</details>

```unknown
bash -lc set -euo pipefail
cd /mnt/data/pbui_book_work/pbui
cat > docs/textbook/code/semantic-types.ts <<'EOF'
/**
 * Dependency-free reference implementation for the textbook.
 *
 * It intentionally implements a small, pure, synchronous core:
 * - nominal atoms with representation-safe subtype declarations;
 * - capabilities;
 * - union, intersection, and difference;
 * - named, parameterized refinements;
 * - evidence-producing direct matching;
 * - semantic identity;
 * - bounded, weighted, pure translator search;
 * - a conservative subtype prover.
 *
 * Production concerns such as asynchronous checks, React integration,
 * authorization, persistence, BDDs, and localization are discussed in the
 * chapters but kept outside this executable semantic kernel.
 */

export type PresentationValues = object;
export type PresentationType<Values extends PresentationValues> = Extract<keyof Values, string>;

export type PresentationReference<
  Values extends PresentationValues,
  Type extends PresentationType<Values> = PresentationType<Values>,
> = {
  [Key in Type]: Readonly<{
    type: Key;
    value: Values[Key];
  }>;
}[Type];

export interface SemanticIdentity {
  readonly namespace: string;
  readonly key: string | number;
}

export interface Fingerprint {
  readonly registryVersion: number;
  readonly objectRevision?: string | number;
  readonly dependencies: readonly (string | number | boolean)[];
}

export interface Atom<Type extends string = string> {
  readonly kind: "atom";
  readonly id: Type;
}

export interface Capability<Id extends string = string> {
  readonly kind: "capability";
  readonly id: Id;
}

export type TypeExpr<Type extends string = string> =
  | Readonly<{ kind: "top" }>
  | Readonly<{ kind: "bottom" }>
  | Atom<Type>
  | Capability
  | Readonly<{ kind: "union"; members: readonly TypeExpr<Type>[] }>
  | Readonly<{ kind: "intersection"; members: readonly TypeExpr<Type>[] }>
  | Readonly<{ kind: "difference"; base: TypeExpr<Type>; excluded: TypeExpr<Type> }>
  | Readonly<{
      kind: "refinement";
      id: string;
      base: TypeExpr<Type>;
      args: unknown;
    }>;

export type MatchFailure = Readonly<{
  code:
    | "bottom"
    | "atom-mismatch"
    | "capability-missing"
    | "union-failed"
    | "intersection-failed"
    | "excluded"
    | "refinement-failed"
    | "refinement-unknown"
    | "translation-exhausted";
  message: string;
  expression: TypeExpr;
  causes?: readonly MatchFailure[];
  details?: unknown;
}>;

export type Evidence =
  | Readonly<{ kind: "top" }>
  | Readonly<{
      kind: "atom";
      requested: string;
      actual: string;
      subtypePath: readonly string[];
    }>
  | Readonly<{
      kind: "capability";
      capability: string;
      implementedBy: string;
      inheritancePath: readonly string[];
    }>
  | Readonly<{
      kind: "union";
      branch: number;
      evidence: Evidence;
    }>
  | Readonly<{
      kind: "intersection";
      members: readonly Evidence[];
    }>
  | Readonly<{
      kind: "difference";
      base: Evidence;
      excludedFailure: MatchFailure;
    }>
  | Readonly<{
      kind: "refinement";
      id: string;
      base: Evidence;
      witness: unknown;
      fingerprint: Fingerprint;
    }>
  | Readonly<{
      kind: "translation";
      steps: readonly TranslationStep[];
      target: Evidence;
    }>;

export type DirectMatchResult<Values extends PresentationValues> =
  | Readonly<{
      ok: true;
      reference: PresentationReference<Values>;
      evidence: Evidence;
      fingerprint: Fingerprint;
    }>
  | Readonly<{
      ok: false;
      failure: MatchFailure;
    }>;

export type MatchResult<Values extends PresentationValues> =
  | Readonly<{
      ok: true;
      source: PresentationReference<Values>;
      accepted: PresentationReference<Values>;
      evidence: Evidence;
      fingerprint: Fingerprint;
      cost: number;
    }>
  | Readonly<{
      ok: false;
      failure: MatchFailure;
    }>;

export type RefinementDecision<Witness> =
  | Readonly<{ kind: "yes"; witness: Witness }>
  | Readonly<{ kind: "no"; reason: unknown }>
  | Readonly<{ kind: "unknown"; reason: unknown }>;

export interface AtomDefinition<Value, Environment> {
  readonly identity?: (value: Value, environment: Environment) => SemanticIdentity;
  readonly revision?: (value: Value, environment: Environment) => string | number;
}

type SafeSupertype<
  Values extends PresentationValues,
  Sub extends PresentationType<Values>,
> = {
  [Super in PresentationType<Values>]: Values[Sub] extends Values[Super] ? Super : never;
}[PresentationType<Values>];

interface ErasedRefinement<Values extends PresentationValues, Environment> {
  readonly id: string;
  readonly baseType: PresentationType<Values>;
  readonly check: (
    value: Values[PresentationType<Values>],
    args: unknown,
    environment: Environment,
  ) => RefinementDecision<unknown>;
  readonly dependencies: (
    value: Values[PresentationType<Values>],
    args: unknown,
    environment: Environment,
  ) => readonly (string | number | boolean)[];
}

export interface TranslationStep {
  readonly translatorId: string;
  readonly from: string;
  readonly to: string;
  readonly cost: number;
  readonly preservesIdentity: boolean;
}

interface ErasedTranslator<Values extends PresentationValues, Environment> {
  readonly id: string;
  readonly from: PresentationType<Values>;
  readonly to: PresentationType<Values>;
  readonly cost: number;
  readonly priority: number;
  readonly preservesIdentity: boolean;
  readonly applicable: (
    value: Values[PresentationType<Values>],
    environment: Environment,
  ) => boolean;
  readonly translate: (
    value: Values[PresentationType<Values>],
    environment: Environment,
  ) => Values[PresentationType<Values>] | undefined;
}

export interface TranslationBudget {
  readonly maxDepth: number;
  readonly maxVisitedStates: number;
}

export type SubtypeDecision =
  | Readonly<{ kind: "yes"; reason: string }>
  | Readonly<{ kind: "no"; reason: string }>
  | Readonly<{ kind: "unknown"; reason: string }>;

const TOP: TypeExpr = Object.freeze({ kind: "top" });
const BOTTOM: TypeExpr = Object.freeze({ kind: "bottom" });

function uniqueSorted<Type extends string>(members: readonly TypeExpr<Type>[]): TypeExpr<Type>[] {
  const byKey = new Map<string, TypeExpr<Type>>();
  for (const member of members) byKey.set(expressionKey(member), member);
  return [...byKey.values()].sort((left, right) =>
    expressionKey(left).localeCompare(expressionKey(right)),
  );
}

export function expressionKey(expression: TypeExpr): string {
  switch (expression.kind) {
    case "top":
      return "⊤";
    case "bottom":
      return "⊥";
    case "atom":
      return `a:${expression.id}`;
    case "capability":
      return `c:${expression.id}`;
    case "union":
      return `or(${expression.members.map(expressionKey).join(",")})`;
    case "intersection":
      return `and(${expression.members.map(expressionKey).join(",")})`;
    case "difference":
      return `diff(${expressionKey(expression.base)},${expressionKey(expression.excluded)})`;
    case "refinement":
      return `ref(${expression.id},${expressionKey(expression.base)},${stableEncode(expression.args)})`;
  }
}

function stableEncode(value: unknown): string {
  if (value === undefined) return "undefined";
  if (value === null || typeof value !== "object") return JSON.stringify(value);
  if (Array.isArray(value)) return `[${value.map(stableEncode).join(",")}]`;
  const record = value as Record<string, unknown>;
  return `{${Object.keys(record)
    .sort()
    .map((key) => `${JSON.stringify(key)}:${stableEncode(record[key])}`)
    .join(",")}}`;
}

export class PresentationTypeSystem<
  Values extends PresentationValues,
  Environment,
> {
  readonly #atoms = new Map<
    PresentationType<Values>,
    AtomDefinition<Values[PresentationType<Values>], Environment>
  >();
  readonly #parents = new Map<PresentationType<Values>, Set<PresentationType<Values>>>();
  readonly #capabilities = new Map<PresentationType<Values>, Set<string>>();
  readonly #refinements = new Map<string, ErasedRefinement<Values, Environment>>();
  readonly #translators = new Map<PresentationType<Values>, ErasedTranslator<Values, Environment>[]>();
  readonly #objectTokens = new WeakMap<object, number>();
  #nextObjectToken = 1;
  #version = 1;

  get version(): number {
    return this.#version;
  }

  readonly top = TOP as TypeExpr<PresentationType<Values>>;
  readonly bottom = BOTTOM as TypeExpr<PresentationType<Values>>;

  atom<Type extends PresentationType<Values>>(
    id: Type,
    definition: AtomDefinition<Values[Type], Environment> = {},
  ): Atom<Type> {
    if (this.#atoms.has(id)) {
      throw new Error(`Presentation atom ${id} is already defined`);
    }
    this.#atoms.set(
      id,
      definition as AtomDefinition<Values[PresentationType<Values>], Environment>,
    );
    this.#parents.set(id, new Set());
    this.#version += 1;
    return Object.freeze({ kind: "atom", id });
  }

  capability<Id extends string>(id: Id): Capability<Id> {
    return Object.freeze({ kind: "capability", id });
  }

  implement<Type extends PresentationType<Values>>(
    atom: Atom<Type>,
    capability: Capability,
  ): void {
    const set = this.#capabilities.get(atom.id) ?? new Set<string>();
    set.add(capability.id);
    this.#capabilities.set(atom.id, set);
    this.#version += 1;
  }

  declareSubtype<
    Sub extends PresentationType<Values>,
    Super extends SafeSupertype<Values, Sub>,
  >(sub: Atom<Sub>, supertype: Atom<Super>): void {
    if (!this.#atoms.has(sub.id) || !this.#atoms.has(supertype.id)) {
      throw new Error("Both atoms must be defined before declaring a subtype");
    }
    const parents = this.#parents.get(sub.id) ?? new Set<PresentationType<Values>>();
    parents.add(supertype.id);
    this.#parents.set(sub.id, parents);
    if (this.#findSubtypePath(supertype.id, sub.id)) {
      parents.delete(supertype.id);
      throw new Error(`Subtype declaration ${sub.id} <: ${supertype.id} creates a cycle`);
    }
    this.#version += 1;
  }

  or(...input: readonly TypeExpr<PresentationType<Values>>[]): TypeExpr<PresentationType<Values>> {
    const flat: TypeExpr<PresentationType<Values>>[] = [];
    for (const member of input) {
      if (member.kind === "top") return this.top;
      if (member.kind === "bottom") continue;
      if (member.kind === "union") flat.push(...member.members);
      else flat.push(member);
    }
    const members = uniqueSorted(flat);
    if (members.length === 0) return this.bottom;
    if (members.length === 1) return members[0]!;
    return Object.freeze({ kind: "union", members: Object.freeze(members) });
  }

  and(...input: readonly TypeExpr<PresentationType<Values>>[]): TypeExpr<PresentationType<Values>> {
    const flat: TypeExpr<PresentationType<Values>>[] = [];
    for (const member of input) {
      if (member.kind === "bottom") return this.bottom;
      if (member.kind === "top") continue;
      if (member.kind === "intersection") flat.push(...member.members);
      else flat.push(member);
    }
    const members = uniqueSorted(flat);
    if (members.length === 0) return this.top;
    if (members.length === 1) return members[0]!;
    return Object.freeze({ kind: "intersection", members: Object.freeze(members) });
  }

  difference(
    base: TypeExpr<PresentationType<Values>>,
    excluded: TypeExpr<PresentationType<Values>>,
  ): TypeExpr<PresentationType<Values>> {
    if (base.kind === "bottom" || excluded.kind === "top") return this.bottom;
    if (excluded.kind === "bottom") return base;
    if (expressionKey(base) === expressionKey(excluded)) return this.bottom;
    return Object.freeze({ kind: "difference", base, excluded });
  }

  refinement<
    Id extends string,
    Base extends PresentationType<Values>,
    Args,
    Witness,
  >(
    id: Id,
    base: Atom<Base>,
    definition: Readonly<{
      check(
        value: Values[Base],
        args: Args,
        environment: Environment,
      ): RefinementDecision<Witness>;
      dependencies?(
        value: Values[Base],
        args: Args,
        environment: Environment,
      ): readonly (string | number | boolean)[];
    }>,
  ): (args: Args) => TypeExpr<PresentationType<Values>> {
    if (this.#refinements.has(id)) {
      throw new Error(`Refinement ${id} is already defined`);
    }
    this.#refinements.set(id, {
      id,
      baseType: base.id,
      check: definition.check as ErasedRefinement<Values, Environment>["check"],
      dependencies:
        (definition.dependencies as ErasedRefinement<Values, Environment>["dependencies"] | undefined) ??
        (() => []),
    });
    this.#version += 1;
    return (args: Args) =>
      Object.freeze({
        kind: "refinement",
        id,
        base,
        args,
      });
  }

  translator<
    From extends PresentationType<Values>,
    To extends PresentationType<Values>,
  >(definition: Readonly<{
    id: string;
    from: Atom<From>;
    to: Atom<To>;
    cost?: number;
    priority?: number;
    preservesIdentity?: boolean;
    applicable?(value: Values[From], environment: Environment): boolean;
    translate(value: Values[From], environment: Environment): Values[To] | undefined;
  }>): void {
    const cost = definition.cost ?? 1;
    if (!Number.isFinite(cost) || cost < 0) {
      throw new Error(`Translator ${definition.id} must have a finite non-negative cost`);
    }
    const erased: ErasedTranslator<Values, Environment> = {
      id: definition.id,
      from: definition.from.id,
      to: definition.to.id,
      cost,
      priority: definition.priority ?? 0,
      preservesIdentity: definition.preservesIdentity ?? false,
      applicable:
        (definition.applicable as ErasedTranslator<Values, Environment>["applicable"] | undefined) ??
        (() => true),
      translate: definition.translate as ErasedTranslator<Values, Environment>["translate"],
    };
    const outgoing = this.#translators.get(erased.from) ?? [];
    if (outgoing.some((translator) => translator.id === erased.id)) {
      throw new Error(`Translator ${erased.id} is already defined for ${erased.from}`);
    }
    outgoing.push(erased);
    outgoing.sort(
      (left, right) =>
        left.cost - right.cost || right.priority - left.priority || left.id.localeCompare(right.id),
    );
    this.#translators.set(erased.from, outgoing);
    this.#version += 1;
  }

  identityFor(
    reference: PresentationReference<Values>,
    environment: Environment,
  ): SemanticIdentity {
    const definition = this.#atoms.get(reference.type);
    const explicit = definition?.identity?.(reference.value, environment);
    if (explicit) return explicit;
    const value = reference.value;
    if ((typeof value === "object" && value !== null) || typeof value === "function") {
      const object = value as object;
      let token = this.#objectTokens.get(object);
      if (token === undefined) {
        token = this.#nextObjectToken;
        this.#nextObjectToken += 1;
        this.#objectTokens.set(object, token);
      }
      return { namespace: `object:${reference.type}`, key: token };
    }
    return { namespace: `primitive:${reference.type}`, key: String(value) };
  }

  sameObject(
    left: PresentationReference<Values>,
    right: PresentationReference<Values>,
    environment: Environment,
  ): boolean {
    const leftIdentity = this.identityFor(left, environment);
    const rightIdentity = this.identityFor(right, environment);
    return (
      leftIdentity.namespace === rightIdentity.namespace &&
      leftIdentity.key === rightIdentity.key
    );
  }

  fingerprintFor(
    reference: PresentationReference<Values>,
    environment: Environment,
    dependencies: readonly (string | number | boolean)[] = [],
  ): Fingerprint {
    const revision = this.#atoms.get(reference.type)?.revision?.(reference.value, environment);
    return {
      registryVersion: this.version,
      objectRevision: revision,
      dependencies,
    };
  }

  matchDirect(
    reference: PresentationReference<Values>,
    expression: TypeExpr<PresentationType<Values>>,
    environment: Environment,
  ): DirectMatchResult<Values> {
    return this.#matchDirect(reference, expression, environment);
  }

  match(
    source: PresentationReference<Values>,
    expression: TypeExpr<PresentationType<Values>>,
    environment: Environment,
    budget: TranslationBudget = { maxDepth: 4, maxVisitedStates: 64 },
  ): MatchResult<Values> {
    const direct = this.matchDirect(source, expression, environment);
    if (direct.ok) {
      return {
        ok: true,
        source,
        accepted: source,
        evidence: direct.evidence,
        fingerprint: direct.fingerprint,
        cost: 0,
      };
    }

    interface QueueEntry {
      readonly reference: PresentationReference<Values>;
      readonly cost: number;
      readonly path: readonly TranslationStep[];
    }

    const queue: QueueEntry[] = [{ reference: source, cost: 0, path: [] }];
    const visited = new Set<string>();
    let visitedCount = 0;

    while (queue.length > 0 && visitedCount < budget.maxVisitedStates) {
      queue.sort(
        (left, right) =>
          left.cost - right.cost ||
          left.path.length - right.path.length ||
          left.path.map((step) => step.translatorId).join("/").localeCompare(
            right.path.map((step) => step.translatorId).join("/"),
          ),
      );
      const current = queue.shift();
      if (!current) break;

      const identity = this.identityFor(current.reference, environment);
      const stateKey = `${current.reference.type}|${identity.namespace}|${String(identity.key)}`;
      if (visited.has(stateKey)) continue;
      visited.add(stateKey);
      visitedCount += 1;

      if (current.path.length >= budget.maxDepth) continue;

      for (const translator of this.#translators.get(current.reference.type) ?? []) {
        if (!translator.applicable(current.reference.value, environment)) continue;
        const translatedValue = translator.translate(current.reference.value, environment);
        if (translatedValue === undefined) continue;
        const target = {
          type: translator.to,
          value: translatedValue,
        } as PresentationReference<Values>;

        if (
          translator.preservesIdentity &&
          !this.sameObject(current.reference, target, environment)
        ) {
          throw new Error(
            `Translator ${translator.id} declared identity preservation but changed semantic identity`,
          );
        }

        const step: TranslationStep = {
          translatorId: translator.id,
          from: translator.from,
          to: translator.to,
          cost: translator.cost,
          preservesIdentity: translator.preservesIdentity,
        };
        const path = [...current.path, step];
        const cost = current.cost + translator.cost;
        const targetMatch = this.matchDirect(target, expression, environment);
        if (targetMatch.ok) {
          return {
            ok: true,
            source,
            accepted: target,
            evidence: {
              kind: "translation",
              steps: path,
              target: targetMatch.evidence,
            },
            fingerprint: targetMatch.fingerprint,
            cost,
          };
        }
        queue.push({ reference: target, cost, path });
      }
    }

    return {
      ok: false,
      failure: {
        code: "translation-exhausted",
        message: `No direct or translated match for ${expressionKey(expression)}`,
        expression,
        causes: [direct.failure],
        details: { budget, visitedCount },
      },
    };
  }

  subtype(
    left: TypeExpr<PresentationType<Values>>,
    right: TypeExpr<PresentationType<Values>>,
  ): SubtypeDecision {
    if (expressionKey(left) === expressionKey(right)) {
      return { kind: "yes", reason: "normalized expressions are identical" };
    }
    if (left.kind === "bottom" || right.kind === "top") {
      return { kind: "yes", reason: "bottom is below every type and every type is below top" };
    }
    if (left.kind === "top" || right.kind === "bottom") {
      return { kind: "no", reason: "top is not below a proper type and a proper type is not below bottom" };
    }
    if (left.kind === "atom" && right.kind === "atom") {
      return this.#findSubtypePath(left.id, right.id)
        ? { kind: "yes", reason: `${left.id} has a nominal subtype path to ${right.id}` }
        : { kind: "no", reason: `${left.id} has no nominal subtype path to ${right.id}` };
    }
    if (left.kind === "union") {
      const decisions = left.members.map((member) => this.subtype(member, right));
      if (decisions.every((decision) => decision.kind === "yes")) {
        return { kind: "yes", reason: "every union member is a subtype of the target" };
      }
      if (decisions.some((decision) => decision.kind === "no")) {
        return { kind: "no", reason: "at least one union member is not a subtype of the target" };
      }
      return { kind: "unknown", reason: "at least one union member is opaque" };
    }
    if (right.kind === "intersection") {
      const decisions = right.members.map((member) => this.subtype(left, member));
      if (decisions.every((decision) => decision.kind === "yes")) {
        return { kind: "yes", reason: "the source is a subtype of every intersection member" };
      }
      if (decisions.some((decision) => decision.kind === "no")) {
        return { kind: "no", reason: "the source is not a subtype of an intersection member" };
      }
      return { kind: "unknown", reason: "an intersection member is opaque" };
    }
    if (left.kind === "intersection") {
      const decisions = left.members.map((member) => this.subtype(member, right));
      if (decisions.some((decision) => decision.kind === "yes")) {
        return { kind: "yes", reason: "one intersection member is already below the target" };
      }
    }
    if (right.kind === "union") {
      const decisions = right.members.map((member) => this.subtype(left, member));
      if (decisions.some((decision) => decision.kind === "yes")) {
        return { kind: "yes", reason: "the source is below one union member" };
      }
    }
    if (left.kind === "difference") return this.subtype(left.base, right);
    if (left.kind === "refinement") return this.subtype(left.base, right);
    return {
      kind: "unknown",
      reason: "the conservative prover does not decide this expression shape",
    };
  }

  #matchDirect(
    reference: PresentationReference<Values>,
    expression: TypeExpr<PresentationType<Values>>,
    environment: Environment,
  ): DirectMatchResult<Values> {
    switch (expression.kind) {
      case "top":
        return {
          ok: true,
          reference,
          evidence: { kind: "top" },
          fingerprint: this.fingerprintFor(reference, environment),
        };
      case "bottom":
        return {
          ok: false,
          failure: {
            code: "bottom",
            message: "No reference belongs to bottom",
            expression,
          },
        };
      case "atom": {
        const path = this.#findSubtypePath(reference.type, expression.id);
        if (!path) {
          return {
            ok: false,
            failure: {
              code: "atom-mismatch",
              message: `Expected ${expression.id}, received ${reference.type}`,
              expression,
              details: { expected: expression.id, actual: reference.type },
            },
          };
        }
        return {
          ok: true,
          reference,
          evidence: {
            kind: "atom",
            requested: expression.id,
            actual: reference.type,
            subtypePath: path,
          },
          fingerprint: this.fingerprintFor(reference, environment),
        };
      }
      case "capability": {
        const implementation = this.#findCapability(reference.type, expression.id);
        if (!implementation) {
          return {
            ok: false,
            failure: {
              code: "capability-missing",
              message: `${reference.type} does not implement ${expression.id}`,
              expression,
            },
          };
        }
        return {
          ok: true,
          reference,
          evidence: {
            kind: "capability",
            capability: expression.id,
            implementedBy: implementation.implementedBy,
            inheritancePath: implementation.path,
          },
          fingerprint: this.fingerprintFor(reference, environment),
        };
      }
      case "union": {
        const failures: MatchFailure[] = [];
        for (const [branch, member] of expression.members.entries()) {
          const result = this.#matchDirect(reference, member, environment);
          if (result.ok) {
            return {
              ok: true,
              reference,
              evidence: {
                kind: "union",
                branch,
                evidence: result.evidence,
              },
              fingerprint: result.fingerprint,
            };
          }
          failures.push(result.failure);
        }
        return {
          ok: false,
          failure: {
            code: "union-failed",
            message: "Every union branch failed",
            expression,
            causes: failures,
          },
        };
      }
      case "intersection": {
        const evidence: Evidence[] = [];
        const dependencies: (string | number | boolean)[] = [];
        for (const member of expression.members) {
          const result = this.#matchDirect(reference, member, environment);
          if (!result.ok) {
            return {
              ok: false,
              failure: {
                code: "intersection-failed",
                message: "An intersection member failed",
                expression,
                causes: [result.failure],
              },
            };
          }
          evidence.push(result.evidence);
          dependencies.push(...result.fingerprint.dependencies);
        }
        return {
          ok: true,
          reference,
          evidence: { kind: "intersection", members: evidence },
          fingerprint: this.fingerprintFor(reference, environment, dependencies),
        };
      }
      case "difference": {
        const base = this.#matchDirect(reference, expression.base, environment);
        if (!base.ok) return base;
        const excluded = this.#matchDirect(reference, expression.excluded, environment);
        if (excluded.ok) {
          return {
            ok: false,
            failure: {
              code: "excluded",
              message: "The reference belongs to the excluded type",
              expression,
              details: excluded.evidence,
            },
          };
        }
        return {
          ok: true,
          reference,
          evidence: {
            kind: "difference",
            base: base.evidence,
            excludedFailure: excluded.failure,
          },
          fingerprint: base.fingerprint,
        };
      }
      case "refinement": {
        const base = this.#matchDirect(reference, expression.base, environment);
        if (!base.ok) return base;
        const definition = this.#refinements.get(expression.id);
        if (!definition) {
          return {
            ok: false,
            failure: {
              code: "refinement-unknown",
              message: `Refinement ${expression.id} is not registered`,
              expression,
            },
          };
        }
        const decision = definition.check(reference.value, expression.args, environment);
        if (decision.kind !== "yes") {
          return {
            ok: false,
            failure: {
              code: "refinement-failed",
              message: `Refinement ${expression.id} returned ${decision.kind}`,
              expression,
              details: decision.reason,
            },
          };
        }
        const dependencies = definition.dependencies(
          reference.value,
          expression.args,
          environment,
        );
        const fingerprint = this.fingerprintFor(reference, environment, dependencies);
        return {
          ok: true,
          reference,
          evidence: {
            kind: "refinement",
            id: expression.id,
            base: base.evidence,
            witness: decision.witness,
            fingerprint,
          },
          fingerprint,
        };
      }
    }
  }

  #findSubtypePath(
    from: PresentationType<Values>,
    to: PresentationType<Values>,
  ): readonly string[] | null {
    if (from === to) return [from];
    const queue: Array<{ current: PresentationType<Values>; path: PresentationType<Values>[] }> = [
      { current: from, path: [from] },
    ];
    const visited = new Set<PresentationType<Values>>();
    while (queue.length > 0) {
      const next = queue.shift();
      if (!next || visited.has(next.current)) continue;
      visited.add(next.current);
      for (const parent of this.#parents.get(next.current) ?? []) {
        const path = [...next.path, parent];
        if (parent === to) return path;
        queue.push({ current: parent, path });
      }
    }
    return null;
  }

  #findCapability(
    from: PresentationType<Values>,
    capability: string,
  ): { implementedBy: string; path: readonly string[] } | null {
    const queue: Array<{ current: PresentationType<Values>; path: PresentationType<Values>[] }> = [
      { current: from, path: [from] },
    ];
    const visited = new Set<PresentationType<Values>>();
    while (queue.length > 0) {
      const next = queue.shift();
      if (!next || visited.has(next.current)) continue;
      visited.add(next.current);
      if (this.#capabilities.get(next.current)?.has(capability)) {
        return { implementedBy: next.current, path: next.path };
      }
      for (const parent of this.#parents.get(next.current) ?? []) {
        queue.push({ current: parent, path: [...next.path, parent] });
      }
    }
    return null;
  }
}

export function createPresentationTypeSystem<
  Values extends PresentationValues,
  Environment,
>(): PresentationTypeSystem<Values, Environment> {
  return new PresentationTypeSystem<Values, Environment>();
}
EOF

cat > docs/textbook/code/demo.ts <<'EOF'
import {
  createPresentationTypeSystem,
  expressionKey,
  type PresentationReference,
} from "./semantic-types.js";

interface Entity {
  id: string;
}

interface Project extends Entity {
  title: string;
  ownerId: string;
  archived: boolean;
  revision: number;
}

interface Document extends Entity {
  title: string;
  revision: number;
}

interface Values {
  entity: Entity;
  project: Project;
  projectId: string;
  document: Document;
}

interface Environment {
  projects: ReadonlyMap<string, Project>;
  authorizationEpoch: number;
}

const types = createPresentationTypeSystem<Values, Environment>();

const Entity = types.atom("entity", {
  identity: (entity) => ({ namespace: "entity", key: entity.id }),
});

const Project = types.atom("project", {
  identity: (project) => ({ namespace: "project", key: project.id }),
  revision: (project) => project.revision,
});

const ProjectId = types.atom("projectId", {
  identity: (projectId) => ({ namespace: "project", key: projectId }),
});

const Document = types.atom("document", {
  identity: (document) => ({ namespace: "document", key: document.id }),
  revision: (document) => document.revision,
});

// The TypeScript compiler permits this declaration because Project extends
// Entity at the representation level.
types.declareSubtype(Project, Entity);

const Inspectable = types.capability("inspectable");
const DocumentBacked = types.capability("document-backed");
types.implement(Project, Inspectable);
types.implement(Document, Inspectable);
types.implement(Project, DocumentBacked);

const OwnedBy = types.refinement(
  "owned-by",
  Project,
  {
    check(project, ownerId: string) {
      return project.ownerId === ownerId
        ? {
            kind: "yes" as const,
            witness: {
              projectId: project.id,
              ownerId,
              revision: project.revision,
            },
          }
        : {
            kind: "no" as const,
            reason: {
              expectedOwner: ownerId,
              actualOwner: project.ownerId,
            },
          };
    },
    dependencies(project, ownerId, environment) {
      return [project.revision, ownerId, environment.authorizationEpoch];
    },
  },
);

const Archived = types.refinement(
  "archived",
  Project,
  {
    check(project) {
      return project.archived
        ? { kind: "yes" as const, witness: { revision: project.revision } }
        : { kind: "no" as const, reason: "project is active" };
    },
    dependencies(project) {
      return [project.revision];
    },
  },
);

const ActiveProject = types.difference(Project, Archived(undefined));
const MyActiveProject = types.and(
  ActiveProject,
  OwnedBy("person-1"),
  Inspectable,
);

types.translator({
  id: "project-id/to-project",
  from: ProjectId,
  to: Project,
  cost: 1,
  preservesIdentity: true,
  applicable: (projectId, environment) => environment.projects.has(projectId),
  translate: (projectId, environment) => environment.projects.get(projectId),
});

const project: Project = {
  id: "project-1",
  title: "Semantic UI",
  ownerId: "person-1",
  archived: false,
  revision: 3,
};

const environment: Environment = {
  projects: new Map([[project.id, project]]),
  authorizationEpoch: 12,
};

const cardReference: PresentationReference<Values, "project"> = {
  type: "project",
  value: project,
};

const tokenReference: PresentationReference<Values, "projectId"> = {
  type: "projectId",
  value: project.id,
};

console.log("Requested expression:", expressionKey(MyActiveProject));
console.log("Direct card match:", types.match(cardReference, MyActiveProject, environment));
console.log("Translated token match:", types.match(tokenReference, MyActiveProject, environment));
console.log(
  "Card and token denote the same object:",
  types.sameObject(cardReference, tokenReference, environment),
);
EOF

cat > docs/textbook/code/laws.ts <<'EOF'
import assert from "node:assert/strict";
import {
  createPresentationTypeSystem,
  expressionKey,
  type PresentationReference,
  type TypeExpr,
} from "./semantic-types.js";

interface Entity {
  id: string;
}
interface Project extends Entity {
  archived: boolean;
  revision: number;
}
interface Values {
  entity: Entity;
  project: Project;
  projectId: string;
}
interface Environment {
  projects: ReadonlyMap<string, Project>;
}

const types = createPresentationTypeSystem<Values, Environment>();
const Entity = types.atom("entity", {
  identity: (value) => ({ namespace: "entity", key: value.id }),
});
const Project = types.atom("project", {
  identity: (value) => ({ namespace: "project", key: value.id }),
  revision: (value) => value.revision,
});
const ProjectId = types.atom("projectId", {
  identity: (value) => ({ namespace: "project", key: value }),
});
types.declareSubtype(Project, Entity);
const Inspectable = types.capability("inspectable");
types.implement(Project, Inspectable);

const Archived = types.refinement("archived", Project, {
  check(project) {
    return project.archived
      ? { kind: "yes" as const, witness: project.revision }
      : { kind: "no" as const, reason: "active" };
  },
});

const project: Project = { id: "p", archived: false, revision: 1 };
const projectRef: PresentationReference<Values, "project"> = {
  type: "project",
  value: project,
};
const projectIdRef: PresentationReference<Values, "projectId"> = {
  type: "projectId",
  value: project.id,
};
const environment: Environment = { projects: new Map([[project.id, project]]) };

types.translator({
  id: "id/to-project",
  from: ProjectId,
  to: Project,
  preservesIdentity: true,
  translate: (id, env) => env.projects.get(id),
});

function equivalent(left: TypeExpr<keyof Values & string>, right: TypeExpr<keyof Values & string>): void {
  assert.equal(expressionKey(left), expressionKey(right));
}

// Constructor-level lattice normalization laws.
equivalent(types.or(Project, Project), Project);
equivalent(types.and(Project, Project), Project);
equivalent(types.or(Project, types.bottom), Project);
equivalent(types.and(Project, types.top), Project);
equivalent(types.or(Project, Entity), types.or(Entity, Project));
equivalent(types.and(Project, Entity), types.and(Entity, Project));

// Subtyping is reflexive and transitive for the nominal graph.
assert.equal(types.subtype(Project, Project).kind, "yes");
assert.equal(types.subtype(Project, Entity).kind, "yes");

// Matching a subtype as its supertype produces evidence.
const entityMatch = types.matchDirect(projectRef, Entity, environment);
assert.equal(entityMatch.ok, true);
if (entityMatch.ok) {
  assert.deepEqual(entityMatch.evidence, {
    kind: "atom",
    requested: "entity",
    actual: "project",
    subtypePath: ["project", "entity"],
  });
}

// Intersection requires both propositions.
assert.equal(types.matchDirect(projectRef, types.and(Project, Inspectable), environment).ok, true);

// Difference accepts active projects and rejects archived projects.
const ActiveProject = types.difference(Project, Archived(undefined));
assert.equal(types.matchDirect(projectRef, ActiveProject, environment).ok, true);
assert.equal(
  types.matchDirect(
    { type: "project", value: { ...project, archived: true, revision: 2 } },
    ActiveProject,
    environment,
  ).ok,
  false,
);

// Semantic identity is reflexive, symmetric, and transitive for these samples.
const projectRef2: PresentationReference<Values, "project"> = {
  type: "project",
  value: { ...project },
};
assert.equal(types.sameObject(projectRef, projectRef, environment), true);
assert.equal(
  types.sameObject(projectRef, projectIdRef, environment),
  types.sameObject(projectIdRef, projectRef, environment),
);
assert.equal(types.sameObject(projectRef, projectIdRef, environment), true);
assert.equal(types.sameObject(projectIdRef, projectRef2, environment), true);
assert.equal(types.sameObject(projectRef, projectRef2, environment), true);

// Weighted translator search accepts the alternate representation.
const translated = types.match(projectIdRef, ActiveProject, environment);
assert.equal(translated.ok, true);
if (translated.ok) {
  assert.equal(translated.accepted.type, "project");
  assert.equal(translated.cost, 1);
  assert.equal(translated.evidence.kind, "translation");
}

console.log("All executable textbook laws passed.");
EOF

cat > docs/textbook/code/tsconfig.json <<'EOF'
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "NodeNext",
    "moduleResolution": "NodeNext",
    "strict": true,
    "noUncheckedIndexedAccess": true,
    "exactOptionalPropertyTypes": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "outDir": "dist",
    "rootDir": ".",
    "skipLibCheck": true
  },
  "include": ["*.ts"]
}
EOF

cat > docs/textbook/code/README.md <<'EOF'
# Executable semantic kernel

Compile and run from this directory:

```bash
tsc -p tsconfig.json
node dist/demo.js
node dist/laws.js
```

The implementation is deliberately dependency-free. It is a didactic semantic kernel, not a drop-in replacement for the production PBUI package.
EOF

```

<details><summary>💭 Thinking</summary>

**Counting Textbook Words and Code Lines**

</details>

```json
{"open":[{"ref_id":"turn504928search4"},{"ref_id":"turn504928search1"},{"ref_id":"turn958255search0"},{"ref_id":"turn958255search1"},{"ref_id":"turn866544search1"},{"ref_id":"turn958255search3"},{"ref_id":"turn913521search0"},{"ref_id":"turn866544search16"}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Searched 6 websites**

</details>

```unknown
bash -lc set -euo pipefail
cd /mnt/data/pbui_book_work/pbui
cat > docs/textbook/21-design-profiles.md <<'EOF'
# Chapter 21 — Minimal, Intermediate, and Maximal Profiles

## 21.1 There is no obligation to implement the whole theory

The mathematical model gives a vocabulary for reasoning. It does not require every application to ship a BDD compiler, proof objects, asynchronous refinements, multiple dispatch, and remote type expressions.

A good architecture makes sophisticated features additive. This chapter defines three practical profiles and a set of omission tests.

## 21.2 Profile A: typed presentations

The minimal useful profile contains:

- discriminated presentation references;
- descriptors for labels, descriptions, and local actions;
- semantic identity and revision;
- exact-type input contexts;
- optional one-step typed translators;
- one provider and object menu.

```ts
const registry = createPresentationRegistry({
  project: {
    label: project => project.title,
    identity: project => ({
      namespace: "project",
      key: project.id,
    }),
    revision: project => project.revision,
  },
});
```

Use this profile when:

- the domain vocabulary is small;
- actions mostly belong to exact types;
- input contexts ask for one or a few exact tags;
- there is little plugin extension;
- predicates are cheap and rare.

Leave out:

- set-theoretic expressions;
- capabilities;
- symbolic subtype reasoning;
- translator graph search;
- full evidence trees;
- dispatch specificity.

Still test identity laws and request lifecycle.

## 21.3 Profile B: semantic selectors

The intermediate profile adds:

- nominal subtype DAG;
- union and intersection;
- named capabilities;
- named parameterized refinements;
- prepared ephemeral predicates;
- evidence summaries;
- action rules selected by type expressions;
- operation-local caching;
- direct identity-preserving translators.

This profile covers most object-rich applications. It permits:

```ts
const Selectable = types.and(
  Project,
  Inspectable,
  OwnedBy(currentUser.id),
);
```

without requiring global complement, BDDs, async matching, or a full multimethod calculus.

Recommended simplifications:

- expose `difference(base, excluded)` but not unrestricted `not`;
- permit only direct translators, not arbitrary paths;
- combine action contributors by stable action ID and explicit priority;
- retain evidence summaries rather than complete proof trees;
- freeze the registry at application startup.

## 21.4 Profile C: extensible semantic runtime

The maximal profile adds features justified by plugins, large vocabularies, or complex workflows:

- full union/intersection/difference algebra;
- versioned open registries;
- capability dictionaries;
- evidence-producing refinements;
- weighted translator search;
- asynchronous applicability;
- multiple dispatch over subject, context, gesture, and argument;
- explicit ambiguity and preferences;
- compiled clauses or BDDs;
- remote serializable type expressions;
- semantic output indexes;
- formal model and property suite.

This profile is a small language runtime. It requires corresponding tooling:

- registry browser;
- expression pretty-printer;
- match explainer;
- dispatch ambiguity report;
- cache and callback metrics;
- protocol versioning;
- plugin isolation;
- security review.

Do not adopt Profile C merely because the API is intellectually attractive.

## 21.5 Feature-by-feature omission tests

### Omit nominal subtyping when

Every accepted category is already represented by an exact tag or explicit union.

### Omit capabilities when

Common behavior applies to at most one or two exact atoms and is unlikely to be extended by independent modules.

### Omit difference or negation when

State exclusions are clearer as named refinements and no symbolic subtype reasoning needs them.

### Omit proof evidence when

A Boolean plus a concise failure reason is sufficient and no downstream action consumes classification facts. Retain a development-only evidence option if debugging is difficult.

### Omit translator paths when

All valid conversions are direct. Direct edges are easier to predict and explain.

### Omit asynchronous matching when

Permission and loading can be resolved before entering the input context. This often produces a better interface.

### Omit multiple dispatch when

Action lookup depends only on subject type and one provider scope. A priority-sorted action-rule list is simpler.

### Omit BDDs when

Normalized expression sizes remain small. Measure before deciding.

### Omit remote expressions when

The client alone owns interaction semantics. Sending a stable command or query may be safer than sending a general type expression.

## 21.6 Migration sequence

A low-risk migration from the supplied PBUI is:

1. add descriptor identity and revision;
2. replace untyped conversion functions with named direct translators;
3. introduce a selector object that compiles legacy `types` and `filter`;
4. add a nominal subtype graph;
5. add capabilities for duplicated cross-type actions;
6. add named refinements for frequently reused predicates;
7. add operation-local evidence and caching;
8. move contextual actions into action rules;
9. add difference and compound expressions only where they simplify actual code;
10. add translator paths or multimethod dispatch only after direct forms become insufficient.

At every step, preserve the legacy API as a compilation target until application code has migrated.

## 21.7 API layering

Expose three layers rather than one overwhelming namespace.

### Basic

```ts
pbui.present(reference)
pbui.accept({ types, filter, prompt })
```

### Semantic

```ts
pbui.types.and(...)
pbui.acceptMatch({ type, prompt })
pbui.actions.define(...)
```

### Advanced

```ts
registry.compile(...)
registry.explainMatch(...)
registry.subtype(...)
registry.translationSearch(...)
registry.diagnostics()
```

The textbook’s final API is a design vocabulary. Production ergonomics should make the common path short.

## 21.8 Decision record template

For each advanced feature, record:

```text
Problem:
Observed duplication or failure mode:
Simpler alternatives considered:
Chosen semantic relation:
Static guarantees:
Runtime trusted assumptions:
Caching/invalidation policy:
Diagnostic tooling:
Exit or rollback strategy:
```

This keeps type-theoretic machinery tied to a concrete product need.

## 21.9 Exercises

1. **[D]** Classify your application as Profile A, B, or C and justify every included feature.
2. **[R]** Why is Profile C better described as a language runtime than a utility library?
3. **[D] ◆** Remove three features from the final API while preserving your most important use case.
4. **[C]** Implement a compatibility compiler from Profile A requests to Profile B expressions.
5. **[D]** Write a decision record for adding capabilities or keeping duplicated descriptor actions.
6. **[X]** Produce a staged migration plan for the supplied repository, including tests and rollback points for each stage.
EOF

cat > docs/textbook/22-related-systems.md <<'EOF'
# Chapter 22 — Related Systems and Reusable Ideas

## 22.1 How to compare systems

No single mainstream JavaScript library duplicates CLIM’s full combination of semantic output, input contexts, presentation types, translators, command tables, and output recording. Useful precedents are distributed across programming languages, schema libraries, inspector environments, state architectures, and formal-method tools.

The correct question is not “which project already is PBUI?” It is:

> Which mature system has solved this particular subproblem, and which assumptions differ?

## 22.2 CLIM and McCLIM

CLIM is the closest architectural ancestor. The CLIM 2 specification, vendor manuals, and McCLIM manual cover:

- presentations and presentation types;
- presentation type inheritance and parameters;
- `accept` and input contexts;
- presentation translators and testers;
- command tables;
- application frames;
- output recording and incremental redisplay.

PBUI borrows semantic association, dynamic acceptance, translators, contextual command organization, and application-frame-like provider scoping.

PBUI differs in important ways:

- React and browser events replace CLIM drawing and input protocols;
- mounted DOM output replaces the full output-history tree;
- serializable verbs replace a Lisp command loop;
- TypeScript generics provide representation checks;
- the proposed type algebra uses explicit set-theoretic composition;
- application stores and remote APIs are external.

McCLIM is open source and remains the best implementation to inspect for the interactions among presentations, translators, command tables, and input contexts.

## 22.3 CDuce and semantic subtyping

CDuce is an open-source functional language designed around powerful types for XML-oriented data. Its research lineage develops semantic subtyping: types denote sets, and subtype checking is set inclusion. Union, intersection, and negation are first-class components of the type algebra.

Reusable ideas:

- interpret types denotationally;
- reduce subtyping to emptiness of a difference;
- use Boolean decision structures for efficient representation;
- distinguish syntactic types from semantic equivalence;
- make pattern-based narrowing interact with set operations.

Difference from PBUI:

- CDuce types classify language values statically and dynamically;
- PBUI types classify tagged application references under a mutable environment;
- arbitrary contextual refinements and semantic identity are central to PBUI;
- PBUI action dispatch and view bindings are outside CDuce’s purpose.

## 22.4 Elixir’s gradual set-theoretic types

Elixir’s current type-system work is particularly relevant because it brings unions, intersections, and negations to a widely used dynamic language while respecting existing idioms such as pattern matching and guards. Its documentation distinguishes bottom, top, and dynamic knowledge. The implementation team has also published detailed accounts of moving from DNF representations to BDD variants as expression growth became a real compiler-performance problem.

Reusable ideas:

- set-theoretic types can be introduced gradually;
- patterns and guards naturally produce positive and negative knowledge;
- `dynamic` should not be conflated with top;
- implementation representations should evolve from measurements;
- public diagnostics are part of the type-system design.

Difference from PBUI:

- Elixir’s compiler analyzes programs; PBUI classifies runtime presentation references;
- Elixir guards use a restricted language; PBUI allows opaque callbacks but should classify and constrain them;
- PBUI evidence is temporal and environment-indexed.

## 22.5 Typed Racket and occurrence typing

Typed Racket narrows variable types based on predicate results. Predicate types carry propositions about what success and failure imply. The original Typed Scheme work formalized occurrence typing and proved its core sound.

Reusable ideas:

- predicates can carry logical information, not merely return Booleans;
- positive and negative branches may learn different facts;
- mutation can invalidate occurrence knowledge;
- union types become practical when ordinary predicates refine them.

PBUI applies these ideas to presentation occurrences. A successful match produces evidence valid under an environment fingerprint. The evidence should not be turned into an eternal brand on a mutable domain object.

## 22.6 Liquid Types, F*, and refinement systems

Liquid Types restrict refinement inference to a finite set of logical qualifiers, yielding decidable constraint solving for useful properties. F* exposes refinement and dependent types in a verification-oriented language and can prove program properties with SMT assistance.

Reusable ideas:

- arbitrary propositions are too broad for complete inference;
- a restricted proposition language can be analyzable and serializable;
- refinement dependencies and logical qualifiers can be explicit;
- a small verified core can coexist with an escape hatch.

PBUI can offer a proposition AST for common equality, membership, and capability checks while retaining custom JavaScript callbacks as opaque refinements.

## 22.7 TypeScript

TypeScript uses a fully erasable structural type system and deliberately prioritizes compatibility with JavaScript over provable soundness. Its design goals explicitly avoid runtime type metadata and do not claim a sound or provably correct type system.

Reusable ideas:

- structural assignability is excellent for checking callback representations;
- discriminated unions model tagged references well;
- generics can connect atom names to value representations;
- declaration files provide strong package ergonomics.

Limits for PBUI:

- semantic tags and subtype declarations need runtime data;
- contextual refinement facts disappear at runtime;
- TypeScript structure cannot infer domain identity;
- static assignability should not invent presentation semantics;
- evidence validity across mutation requires runtime revisions.

The PBUI registry complements TypeScript rather than competing with it.

## 22.8 ArkType

ArkType is a TypeScript-oriented runtime validator whose documentation emphasizes set-theoretic understanding, runtime type relationships, introspection, and normalized optimized schemas.

Reusable ideas:

- schemas can be runtime values with static inference;
- runtime `extends` relations can be exposed;
- normalized internal representations improve validation and introspection;
- expressive syntax can compile to efficient checks.

Potential integration:

```ts
types.atom("project", {
  representationSchema: ProjectSchema,
  identity: project => ({ namespace: "project", key: project.id }),
});
```

ArkType could validate structural leaf representations. PBUI still needs semantic identity, contextual refinements, occurrence handling, command contexts, translators, and view bindings.

## 22.9 Effect Schema, TypeBox, Zod, and schema ecosystems

Effect Schema models decoding, encoding, assertion, transformations, arbitrary generation, JSON Schema, equivalence, and pretty-printing. TypeBox builds JSON-Schema-oriented TypeScript types. Zod provides ergonomic runtime validation with static inference.

These systems are relevant to:

- validating refinement arguments;
- defining remote type-expression schemas;
- decoding domain data before presentation;
- deriving arbitrary generators for tests;
- obtaining structural equivalence or pretty printers.

They are not presentation-type systems. A successful schema decode says the value has a shape; it does not establish which application object the occurrence denotes or which action table applies.

## 22.10 Clojure hierarchies and multimethods

Clojure supports ad hoc derivation hierarchies over names and multimethod dispatch on arbitrary values, attributes, metadata, or tuples. Its `prefer-method` facility resolves otherwise ambiguous methods.

This is one of the closest precedents for PBUI action dispatch.

Reusable ideas:

- hierarchy need not be tied to classes;
- dispatch can use a tuple of semantic dimensions;
- method preference should be explicit;
- runtime polymorphism can be open and data-driven;
- `isa?` is a semantic hierarchy query distinct from `instance?`.

PBUI extends the idea by allowing dispatch dimensions to be compound type expressions and by returning evidence for applicability.

## 22.11 Clojure protocols and Elixir protocols

Clojure protocols define named method sets and permit independent extension over types. Elixir protocols dispatch behavior by data type and support consolidation for runtime efficiency.

Reusable ideas:

- behavior contracts belong outside a class tree;
- capabilities can have method dictionaries;
- extension conflicts and consolidation need explicit lifecycle rules;
- protocols solve a large single-dispatch subset more simply than general multimethods.

PBUI capabilities can use this model, while contextual actions remain multiple-dispatch relations.

## 22.12 Malli and Clojure spec

Malli is a high-performance, data-driven schema library for Clojure and ClojureScript. Clojure spec uses predicates and combinators for validation, conformation, explanation, and generation.

Reusable ideas:

- schemas/specifications as immutable data;
- registries of named definitions;
- rich explanations;
- transformations and conforming;
- generation from specifications;
- extensible custom nodes.

The final PBUI `TypeExpr` should feel more like a data-driven schema AST than a JavaScript class hierarchy.

## 22.13 Portal

Portal is an open-source Clojure data inspector designed for navigating values. It supports multiple viewers and commands over selected data. Viewer applicability can be based on value shape and predicates.

Reusable interaction ideas:

- selected nested values as first-class objects;
- switching among applicable viewers;
- command discovery over the focused value;
- navigation history through derived objects;
- keyboard-oriented inspection.

Portal is closer to an inspector than an application command framework, but it demonstrates how rich object selection and contextual viewing can feel in practice.

## 22.14 Glamorous Toolkit

Glamorous Toolkit is an open-source moldable development environment centered on contextual tools, views, searches, and actions associated with domain objects. Its philosophy is that generic tools are broad but context-specific tools communicate more domain value; tools should become available where their context is relevant.

This strongly aligns with PBUI’s intended direction:

```text
object
  → several contextual presentations
  → applicable tools and actions
  → related objects and navigation
  → executable explanations
```

GT also shows the importance of authoring tools that inspect the semantic system itself. A PBUI registry browser and match explainer should be product features for developers, not afterthoughts.

## 22.15 Julia

Julia’s multiple dispatch chooses the most specific applicable method based on the types of all arguments. It is an important model for action-method organization and specificity.

Reusable ideas:

- behavior need not belong to one privileged receiver;
- method signatures form a specificity order;
- ambiguity is a real design condition;
- conversion and dispatch are distinct;
- generic behavior can emerge from a coherent patchwork of methods.

Julia’s types are nominal and its compiler setting differs significantly, so PBUI should borrow dispatch principles rather than emulate the language.

## 22.16 Fulcro and normalized identity

Fulcro is a ClojureScript application framework built around normalized application data and component queries. Multiple components can render different projections of one entity identified by a stable ident.

Reusable ideas:

- entity identity is independent of component occurrence;
- normalized state makes shared updates explicit;
- UI joins can project one entity into many contexts;
- graph-oriented state supports targeted refresh.

PBUI’s semantic identity serves a similar cross-occurrence purpose. Subject bindings add another relation: distinct views intentionally share one changing selector cell.

## 22.17 Lively.next, Smalltalk, and live object environments

Lively.next is a browser-based JavaScript development environment with live object inspection and modification. Smalltalk systems and Morphic environments similarly emphasize direct manipulation of live objects and reflective tools.

Reusable ideas:

- inspecting live object state in context;
- modifying behavior while the system runs;
- tools as ordinary objects;
- direct manipulation of visual object graphs.

CLIM’s semantic presentation protocol is more type-and-command oriented; live object environments are more reflective. A strong PBUI development experience can combine both.

## 22.18 Abstract interpretation, BDD packages, and incremental systems

Abstract interpretation supplies the theory of sound approximation and ordered abstract domains. BDD literature supplies compact Boolean representations. Incremental computation systems supply dependency graphs and invalidation strategies.

PBUI need not reproduce these fields. It can apply their results:

- bitset facts are a sound prefilter;
- compiled matchers are abstract classifiers;
- dependency fingerprints approximate change impact;
- BDDs become an implementation option for large Boolean structure;
- stale evidence is invalidated like an incremental computation node.

## 22.19 A comparison matrix

| System | Semantic set algebra | Runtime predicates | Evidence/explanation | Contextual dispatch | Semantic output | Identity normalization |
|---|---:|---:|---:|---:|---:|---:|
| CLIM/McCLIM | presentation types, inheritance | testers | partial | command tables/translators | yes | application-defined |
| CDuce | strong | language predicates/patterns | type errors | functions/patterns | no | no UI identity protocol |
| Elixir types | strong, gradual | guards/patterns | compiler diagnostics | protocols/functions | no | data semantics |
| Typed Racket | unions/refinement propositions | predicates | type diagnostics | functions/generics | no | no UI identity protocol |
| ArkType | runtime structural set relations | narrowing | validation errors | no | no | schema equivalence only |
| Clojure multimethods | ad hoc hierarchy | arbitrary dispatch | ambiguity errors | strong | no | application-defined |
| Portal | predicate-driven viewers | yes | UI-oriented | commands | selected values | value-oriented |
| Glamorous Toolkit | contextual applicability | yes | contextual tools | actions/views/searches | object-centric | object identity |
| Fulcro | no type algebra | selectors | query tools | mutations | component output | strong normalized entity identity |
| Proposed PBUI | restricted set algebra | named and opaque refinements | proof-relevant matches | multi-dimensional actions | mounted semantic output | explicit cross-type identity and bindings |

The matrix is intentionally qualitative. Each system solves a different problem.

## 22.20 Exercises

1. **[R]** Select three systems and identify one idea PBUI should borrow and one assumption it should not.
2. **[D]** Decide whether ArkType or Effect Schema should validate structural leaf values in your registry.
3. **[D]** Compare Clojure multimethod preferences with numeric action priorities.
4. **[R]** Explain how Portal and Glamorous Toolkit differ from a conventional form-oriented UI library.
5. **[C]** Prototype a capability dictionary using an Elixir/Clojure-protocol style registry.
6. **[D] ◆** Produce a comparison matrix for PBUI and two systems not listed here.
7. **[X]** Install and study one open-source system from this chapter. Reimplement one interaction pattern in the PBUI Storybook and document the semantic mapping.
EOF

cat > docs/textbook/23-datalab-case-study.md <<'EOF'
# Chapter 23 — Datalab Case Study: Linked Analytical Views

## 23.1 The scenario

Datalab presents documents through several applications:

- chart views;
- pipeline views;
- table views;
- field and source browsers;
- inspectors and trace views.

A chart and pipeline may both operate on a primary document. The user wants changing the document in one view to change it in the other, while preserving independent chart and pipeline configuration.

This requirement exposes the difference among:

- domain object identity;
- logical view identity;
- placement identity;
- shared subject-binding identity.

## 23.2 Incorrect models

### Merge the views

Using one `viewId` would imply that chart and pipeline are one application configuration. This loses independent state and app identity.

### Duplicate document IDs and synchronize by callbacks

Each DocBar could set its own view document and then imperatively update linked peers. This duplicates source-of-truth state and permits drift after import, remote updates, or missed events.

### Link placements

Placements are rectangles. A view may move or have several placements. Document linkage belongs to logical views, not one occurrence.

### Infer linkage from equal document values

Two independent views may happen to show the same document. Equality of current values does not mean future selections should be coupled.

## 23.3 Binding model

Introduce a binding entity:

```ts
interface DocumentBinding {
  id: BindingId;
  documents: Record<DocumentRole, DocumentId>;
  revision: number;
}

interface AppView {
  id: ViewId;
  appId: AppId;
  documentBindingId: BindingId;
  configuration: unknown;
}
```

A newly created view gets a private binding. Linking changes the target view to the source binding, subject to a merge policy. Unlinking copies current values into a new binding.

Selectors resolve:

```ts
function selectViewDocument(state, viewId, role) {
  const view = state.views[viewId];
  return state.bindings[view.documentBindingId].documents[role];
}
```

The UI no longer needs to synchronize peer values because peers read one state cell.

## 23.4 Presentation vocabulary

Datalab can define:

```ts
interface Values {
  tile: TileReference;
  view: AppViewReference;
  chartView: ChartViewReference;
  pipelineView: PipelineViewReference;
  document: DocumentReference;
}
```

Nominal relation:

```text
ChartView <: View
PipelineView <: View
```

Capabilities:

```text
DocumentBacked
LinkableSubject
```

Both chart and pipeline implement them.

The link-target request is:

```ts
const targetType = types.and(
  View,
  DocumentBacked,
  LinkableSubject,
);
```

An ephemeral exclusion removes the source view itself.

## 23.5 First-time interaction

A discoverable workflow can be:

1. each document-backed tile header shows a chain control;
2. activating it enters an input context;
3. the prompt states “Choose another view whose document selection should follow this view”;
4. applicable tile title presentations are highlighted;
5. choosing one displays a confirmation summary when role values conflict;
6. the link action dispatches on source and target capabilities;
7. both DocBars display a shared-link indicator;
8. an unlink control detaches the current view.

Because tile titles are presentations, keyboard and pointer selection share one semantic request.

## 23.6 Action dispatch

The final operation relates two objects:

```ts
actions.define({
  id: "link-document-bindings",
  subject: types.and(View, DocumentBacked),
  argument: types.and(View, DocumentBacked),
  context: LinkViewsContext,
  method(source, context, gesture, target) {
    return {
      id: "link",
      label: "Link document selection",
      verb: {
        type: "linkViewDocuments",
        sourceViewId: source.accepted.value.viewId,
        targetViewId: target.accepted.value.viewId,
      },
    };
  },
});
```

A specialized method can reject or adapt incompatible role sets:

```text
(ChartView, PipelineView)
```

may map chart `primary` to pipeline `input`, while a general `(DocumentBacked, DocumentBacked)` method uses equal role names.

## 23.7 Conflict semantics

Suppose source and target currently select different primary documents. Linking needs a policy.

### Source wins

Predictable when the user initiated from the source control.

### Target wins

Useful when the prompt means “follow that view.”

### New binding with explicit choice

A dialog lists conflicting roles and asks which value to retain.

### Role-wise merge

Non-conflicting roles are combined; conflicting roles use source or explicit resolution.

The verb should record the decision so remote replay is deterministic:

```ts
{
  type: "linkViewDocuments",
  sourceViewId,
  targetViewId,
  resolution: {
    primary: { take: "source" },
  },
}
```

## 23.8 Portable bundles

Portable state should preserve equivalence, not runtime IDs.

Export:

1. collect bindings referenced by exported views;
2. assign dense local binding indices;
3. export each binding once;
4. store each view’s local index.

Import:

1. allocate one fresh binding per exported binding;
2. import role values through document-ID remapping;
3. allocate fresh view IDs;
4. attach each view to its reconstructed binding.

Property:

```text
shareBefore(v₁,v₂) iff shareAfter(import(v₁),import(v₂))
```

## 23.9 Remote protocol evolution

If the existing protobuf `AppView` lacks a binding field, local behavior and portable bundles can support linkage before the remote workbench protocol does. This boundary must be explicit.

An additive protocol design might introduce normalized bindings:

```proto
message DocumentBinding {
  string id = 1;
  map<string, string> documents = 2;
  uint64 revision = 3;
}

message AppView {
  string id = 1;
  string app_id = 2;
  string document_binding_id = 3;
  // legacy materialized documents may remain during migration
}
```

Compatibility strategy:

- old snapshots without binding IDs create private bindings;
- new writers may materialize legacy document maps while old readers remain supported;
- conflict validation rejects mismatched materialized and normalized values;
- protocol tests cover round trips in both versions.

## 23.10 Proof obligations

The case study has concrete invariants:

1. `view.documentBindingId` always refers to an existing binding;
2. a binding role points to an existing document or an explicitly permitted unresolved ID;
3. link and unlink preserve every unaffected view;
4. set-document changes exactly one binding;
5. independent duplicate allocates a fresh binding;
6. linked placement reuses the same view and therefore the same binding;
7. portable round trip preserves the view-sharing equivalence relation;
8. remote fallback behavior is documented and deterministic.

These are stronger and more testable than “the two dropdowns stay in sync.”

## 23.11 Exercises

1. **[D]** Choose a normalized or materialized binding model for the supplied Datalab store.
2. **[P]** Prove that setting one normalized binding role propagates to every member view.
3. **[C]** Implement source-wins linking and unlink-copy semantics.
4. **[D] ◆** Design the UI for a conflict between source and target document roles.
5. **[C]** Build the PBUI link-target input context using capabilities rather than exact app IDs.
6. **[P]** State a portable round-trip theorem using equivalence relations rather than ID equality.
7. **[X]** Extend the protobuf schema and codecs for normalized bindings, including backward-compatibility tests.
EOF

cat > docs/textbook/24-future-directions.md <<'EOF'
# Chapter 24 — Limits, Extensions, and Research Directions

## 24.1 The trusted boundary remains real

The semantic core can prove composition laws relative to trusted primitives. JavaScript callbacks remain able to:

- lie;
- diverge;
- read untracked mutable state;
- throw;
- perform effects;
- return stale data;
- violate identity declarations.

A mature implementation should make trust visible:

```text
verified structural core
registry declarations checked by types and runtime assertions
named predicates covered by contract tests
opaque predicates explicitly marked
server authorization independent
```

The goal is not to eliminate trust. It is to reduce and localize it.

## 24.2 A serializable proposition language

The most valuable near-term extension is a small proposition AST:

```ts
type Proposition =
  | Eq<Path, JsonValue>
  | In<Path, readonly JsonValue[]>
  | HasCapability<CapabilityId>
  | SameIdentity<ReferenceLocator>
  | And<readonly Proposition[]>
  | Or<readonly Proposition[]>
  | Not<Proposition>;
```

Benefits:

- remote selectors;
- deterministic caching;
- safer plugin declarations;
- explanation generation;
- static implication rules;
- query planning;
- test-data generation.

A custom predicate remains as an explicitly local node.

## 24.3 Proof-assistant reference semantics

The pure direct matcher can be formalized in Lean, Agda, Coq, or F*. A small mechanized development could produce:

- syntax and denotation;
- normalized expression representation;
- a decidable matcher for finite atoms;
- soundness and completeness proofs;
- extracted reference implementation;
- proof certificates checked by JavaScript.

One promising architecture is **proof-producing compilation**:

```text
TypeScript registry builder
  → normalized expression and certificate
  → small verified checker validates certificate
  → optimized matcher executes with differential tests
```

This may be excessive for application code but valuable if PBUI evolves into infrastructure used by many plugins or remote clients.

## 24.4 Incremental and reactive logic

A refinement result depends on facts. Rather than storing opaque fingerprints, a future registry can expose a dependency graph:

```text
OwnedBy(p, user)
  depends on project[p].ownerId
  depends on principal.id

CanEdit(p, user)
  depends on OwnedBy(p,user)
  depends on permission[p,user]
```

This resembles incremental computation and dataflow logic. When a fact changes, only affected evidence is invalidated.

A Datalog-style rule engine is another possible substrate:

```text
inspectable(project(P)).
can_archive(U,P) :- owns(U,P), active(P), admin(U).
```

Datalog offers declarative relations, indexing, provenance, and incremental variants. It also changes the programming model substantially. Introduce it only if the application has many shared logical rules, not for a handful of selectors.

## 24.5 Provenance

Evidence answers “why did this match?” Provenance generalizes the question:

```text
which registry declaration?
which source data revision?
which translator path?
which permission fact?
which plugin?
which user-selected parameter?
```

Provenance is useful for:

- explainable interfaces;
- audit trails;
- invalidation;
- debugging plugin conflicts;
- reproducible command histories.

A compact provenance DAG can share common proof nodes across many matches.

## 24.6 Distributed and collaborative semantics

In a collaborative workspace, semantic identity and evidence cross process boundaries. New questions arise:

- Are identity namespaces globally unique?
- Which registry version interpreted a remote type expression?
- Can two clients have different plugin vocabularies?
- How are subject-binding updates merged?
- Does evidence refer to an authoritative snapshot?
- Can a client request a type that reveals hidden objects?

A robust protocol should include:

```ts
interface SemanticProtocolEnvelope {
  registrySchemaId: string;
  registryVersion: string;
  expression: SerializedTypeExpr;
  principalContextId?: string;
  snapshotId?: string;
}
```

Remote evidence should be treated as provenance, not authority.

## 24.7 Temporal types

Many UI propositions are temporal:

```text
active now
loaded before timeout
selected since command began
unchanged since confirmation
```

One can index evidence by time or snapshot:

\[
\mathrm{ActiveAt}(p,t)
\]

or use temporal logic for workflows. Most applications should encode snapshot IDs and revisions rather than expose a temporal type language. Formal temporal models become worthwhile for concurrent workflows, leases, and optimistic operations.

## 24.8 Linear and affine resources

Some accepted objects should be consumed at most once:

```text
one-time token
drag payload
transaction capability
exclusive lock lease
```

Linear or affine type ideas can model consumption. In JavaScript, an opaque stateful witness can enforce one-shot use:

```ts
interface OneShotMatch {
  consume(): Match;
}
```

After consumption, further calls fail. This is an operational approximation, not static linear typing. It can nevertheless prevent double submission in command workflows.

## 24.9 Modal contexts

A match may be valid only under a mode:

```text
known from cache
verified by server
available after loading
permitted in administrative context
```

Modal type theory distinguishes propositions under modalities such as necessity, possibility, time, or location. A pragmatic PBUI can represent modalities as evidence status and context types:

```text
LocallyKnown(Project)
ServerVerified(Project)
PossiblyAvailable(Project)
```

Use explicit names and operational semantics. Do not add modal notation without a concrete workflow need.

## 24.10 Bidirectional typing and API ergonomics

A complex generic API can overwhelm TypeScript inference. Bidirectional typing suggests a practical ergonomic split:

- constructors synthesize expression metadata;
- registration sites check callbacks against explicitly known atoms;
- use sites infer accepted reference types when expressions remain statically tractable;
- advanced dynamic expressions return a broad reference plus runtime evidence.

For example:

```ts
const Project = types.atom("project");
const Mine = OwnedBy(userId); // synthesizes base Project

const result = await pbui.acceptTyped(Mine);
// statically ProjectRef, dynamically accompanied by ownership evidence
```

Intersections of unrelated representation atoms may not have a useful TypeScript value type. The API should degrade honestly rather than create impossible conditional types.

## 24.11 Generative and adaptive interfaces

A semantic registry gives an AI or adaptive UI structured information:

- available object kinds;
- identity relations;
- type expressions accepted by commands;
- applicable actions;
- explanation and provenance;
- safe serializable verbs.

This can support generated menus or workflow suggestions. The deterministic registry should remain the execution boundary. A generated interface proposes type expressions and commands; the matcher and domain layer validate them.

This is closely aligned with object-centric environments that emphasize deterministic contextual tools. Generative presentation should augment, not bypass, those tools.

## 24.12 Research program

A serious PBUI research program could investigate:

1. a mechanized core calculus with proof-producing match compilation;
2. efficient mixed Boolean/refinement representations;
3. incremental provenance-aware evidence;
4. multimethod coherence under open plugin extension;
5. accessible interaction over very large semantic output spaces;
6. distributed registry versioning and remote expression safety;
7. empirical comparison of widget-local and presentation-based development;
8. user studies of dynamic input contexts and semantic linking;
9. integration with normalized graph stores and query languages;
10. developer tooling for explaining UI applicability.

The core practical hypothesis is testable:

> Explicit semantic relations reduce duplicated interaction logic and make cross-view operations more compositional, provided the registry remains explainable and the common path remains small.

## 24.13 Final perspective

The final API is not primarily an inheritance system. It is a small logic of application references:

```text
atoms name stable semantic categories
subtyping states substitutability
union and intersection compose sets
refinements state contextual propositions
capabilities provide behavior dictionaries
translations change representation
identity states sameness
bindings state shared changing subjects
action methods relate several classified arguments
evidence records why a decision holds
```

That separation is the enduring result. Features can be omitted, alternative algorithms can be substituted, and the syntax can change without losing the conceptual model.

## 24.14 Exercises

1. **[D]** Identify the trusted computing base of a remote PBUI deployment.
2. **[D]** Choose one predicate that should move from an opaque lambda to a proposition AST.
3. **[P]** State a provenance-preservation property for translated matches.
4. **[C]** Implement a one-shot match wrapper and test that it cannot be consumed twice.
5. **[R]** Explain why remote evidence is not authorization.
6. **[D] ◆** Select one research direction and define a six-week prototype with measurable success criteria.
7. **[X]** Write a mechanized or executable formal model for one advanced extension: asynchronous evidence, multimethod coherence, or linked-binding convergence.
EOF

```

<details><summary>💭 Thinking</summary>

**Drafted Chapters 21–24 and related systems**

</details>

```json
{"search_query":[{"q":"CLIM 2 specification authors Common Lisp Interface Manager Release 2"},{"q":"A presentation manager based on application semantics McKay 1988 bibliographic citation"},{"q":"Semantic subtyping Frisch Castagna Benzaken JACM citation DOI"},{"q":"QuickCheck lightweight tool for random testing of Haskell programs citation"}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Searched 25 websites**

</details>

```unknown
bash -lc set -euo pipefail
cd /mnt/data/pbui_book_work/pbui
cat > docs/textbook/appendix-a-api.md <<'EOF'
# Appendix A — Complete Proposed API

This appendix consolidates the API developed across the book. It is a design specification, not a claim that every declaration should be shipped in the first release. Chapter 21 defines smaller profiles.

## A.1 Core references

```ts
export type PresentationValues = object;

export type PresentationType<
  Values extends PresentationValues,
> = Extract<keyof Values, string>;

export type PresentationReference<
  Values extends PresentationValues,
  Type extends PresentationType<Values> = PresentationType<Values>,
> = {
  [Key in Type]: Readonly<{
    type: Key;
    value: Values[Key];
  }>;
}[Type];
```

## A.2 Semantic identity and revisions

```ts
export interface SemanticIdentity {
  readonly namespace: string;
  readonly key: string | number;
}

export interface AtomDefinition<Value, Environment> {
  readonly label?: (
    value: Value,
    environment: Environment,
  ) => React.ReactNode;

  readonly describe?: (
    value: Value,
    environment: Environment,
  ) => unknown;

  readonly identity?: (
    value: Value,
    environment: Environment,
  ) => SemanticIdentity;

  readonly revision?: (
    value: Value,
    environment: Environment,
  ) => string | number;

  readonly tone?: PresentationTone;
}
```

Identity functions should satisfy equivalence laws. Revisions need not be globally monotone, but equality must imply that every state component relevant to cached classifiers is unchanged or separately included in a dependency fingerprint.

## A.3 Type expressions

```ts
export interface Atom<Type extends string = string> {
  readonly kind: "atom";
  readonly id: Type;
}

export interface Capability<
  Id extends string = string,
  Methods = unknown,
> {
  readonly kind: "capability";
  readonly id: Id;
  readonly __methods?: Methods;
}

export type TypeExpr<Type extends string = string> =
  | Readonly<{ kind: "top" }>
  | Readonly<{ kind: "bottom" }>
  | Atom<Type>
  | Capability
  | Readonly<{
      kind: "union";
      members: readonly TypeExpr<Type>[];
    }>
  | Readonly<{
      kind: "intersection";
      members: readonly TypeExpr<Type>[];
    }>
  | Readonly<{
      kind: "difference";
      base: TypeExpr<Type>;
      excluded: TypeExpr<Type>;
    }>
  | Readonly<{
      kind: "refinement";
      id: string;
      base: TypeExpr<Type>;
      args: JsonValue;
    }>
  | Readonly<{
      kind: "parameterized";
      constructor: string;
      args: readonly JsonValue[];
    }>;
```

The public API should prefer `difference(base, excluded)` over unrestricted global complement. An internal compiler may use complement relative to a frozen registry universe.

## A.4 Type-system builder

```ts
export interface PresentationTypeSystemBuilder<
  Values extends PresentationValues,
  Environment,
> {
  readonly top: TypeExpr<PresentationType<Values>>;
  readonly bottom: TypeExpr<PresentationType<Values>>;

  atom<Type extends PresentationType<Values>>(
    id: Type,
    definition?: AtomDefinition<Values[Type], Environment>,
  ): Atom<Type>;

  capability<Id extends string, Methods = unknown>(
    id: Id,
  ): Capability<Id, Methods>;

  declareSubtype<
    Sub extends PresentationType<Values>,
    Super extends RepresentationSafeSupertype<Values, Sub>,
  >(
    sub: Atom<Sub>,
    supertype: Atom<Super>,
  ): void;

  implement<
    Type extends PresentationType<Values>,
    Id extends string,
    Methods,
  >(
    type: Atom<Type>,
    capability: Capability<Id, Methods>,
    methods: Methods,
    metadata?: ImplementationMetadata,
  ): void;

  or(
    ...members: readonly TypeExpr<PresentationType<Values>>[]
  ): TypeExpr<PresentationType<Values>>;

  and(
    ...members: readonly TypeExpr<PresentationType<Values>>[]
  ): TypeExpr<PresentationType<Values>>;

  difference(
    base: TypeExpr<PresentationType<Values>>,
    excluded: TypeExpr<PresentationType<Values>>,
  ): TypeExpr<PresentationType<Values>>;

  refinement<Id extends string, Base extends PresentationType<Values>, Args, Witness>(
    id: Id,
    base: Atom<Base>,
    definition: RefinementDefinition<Values[Base], Args, Witness, Environment>,
  ): RefinementConstructor<Args, PresentationType<Values>>;

  translator<From extends PresentationType<Values>, To extends PresentationType<Values>>(
    definition: TranslatorDefinition<Values, Environment, From, To>,
  ): void;

  freeze(): PresentationRegistry<Values, Environment>;
}
```

## A.5 Refinements

```ts
export type RefinementDecision<Witness> =
  | Readonly<{
      kind: "yes";
      witness: Witness;
    }>
  | Readonly<{
      kind: "no";
      reason: Diagnostic;
    }>
  | Readonly<{
      kind: "unknown";
      reason: Diagnostic;
    }>;

export type RefinementPurity =
  | "structural"
  | "pure"
  | "contextual"
  | "volatile"
  | "async";

export interface RefinementDefinition<
  Value,
  Args,
  Witness,
  Environment,
> {
  readonly purity?: RefinementPurity;
  readonly cost?: "constant" | "cheap" | "moderate" | "expensive";
  readonly serializable?: boolean;

  check(
    value: Value,
    args: Args,
    environment: Environment,
    signal?: AbortSignal,
  ):
    | RefinementDecision<Witness>
    | Promise<RefinementDecision<Witness>>;

  dependencies?(
    value: Value,
    args: Args,
    environment: Environment,
  ): readonly DependencyToken[];

  explainSuccess?(witness: Witness, level: DiagnosticLevel): Diagnostic;
  explainFailure?(reason: Diagnostic, level: DiagnosticLevel): Diagnostic;
}
```

Synchronous and asynchronous definitions may be split into distinct interfaces to preserve stronger static return types.

## A.6 Translators

```ts
export type TranslationEffect =
  | "pure-total"
  | "pure-partial"
  | "async-partial";

export interface TranslatorDefinition<
  Values extends PresentationValues,
  Environment,
  From extends PresentationType<Values>,
  To extends PresentationType<Values>,
> {
  readonly id: string;
  readonly from: Atom<From>;
  readonly to: Atom<To>;
  readonly effect: TranslationEffect;
  readonly cost: number;
  readonly priority?: number;
  readonly preservesIdentity?: boolean;
  readonly serializable?: boolean;

  applicable?(
    value: Values[From],
    environment: Environment,
    signal?: AbortSignal,
  ): boolean | Promise<boolean>;

  translate(
    value: Values[From],
    environment: Environment,
    signal?: AbortSignal,
  ):
    | Values[To]
    | undefined
    | Promise<Values[To] | undefined>;
}

export type TranslationPolicy =
  | "none"
  | "identity-preserving-only"
  | "pure-only"
  | "allow-async"
  | Readonly<{
      allow: readonly string[];
      maxDepth?: number;
      maxVisitedStates?: number;
      timeoutMs?: number;
    }>;
```

## A.7 Evidence, failure, and fingerprints

```ts
export interface Fingerprint {
  readonly registryVersion: string | number;
  readonly objectRevision?: string | number;
  readonly dependencies: readonly DependencyToken[];
}

export type Evidence =
  | TopEvidence
  | AtomEvidence
  | CapabilityEvidence
  | UnionEvidence
  | IntersectionEvidence
  | DifferenceEvidence
  | RefinementEvidence
  | TranslationEvidence;

export interface Match<Values extends PresentationValues> {
  readonly source: PresentationReference<Values>;
  readonly accepted: PresentationReference<Values>;
  readonly evidence: Evidence;
  readonly fingerprint: Fingerprint;
  readonly translationCost: number;

  capability<Methods>(capability: Capability<string, Methods>): Methods;
}

export type MatchResult<Values extends PresentationValues> =
  | Readonly<{ ok: true; match: Match<Values> }>
  | Readonly<{ ok: false; failure: MatchFailure }>;
```

Evidence constructors should be package-private or branded. A public evidence union is useful for inspection but should not allow users to forge a valid `Match` object.

## A.8 Registry queries

```ts
export interface PresentationRegistry<
  Values extends PresentationValues,
  Environment,
> {
  readonly version: string | number;

  identityFor(
    reference: PresentationReference<Values>,
    environment: Environment,
  ): SemanticIdentity;

  sameObject(
    left: PresentationReference<Values>,
    right: PresentationReference<Values>,
    environment: Environment,
  ): boolean;

  matchDirect(
    reference: PresentationReference<Values>,
    expression: TypeExpr<PresentationType<Values>>,
    environment: Environment,
  ): MatchResult<Values>;

  match(
    reference: PresentationReference<Values>,
    expression: TypeExpr<PresentationType<Values>>,
    environment: Environment,
    policy?: TranslationPolicy,
  ): MatchResult<Values> | Promise<MatchResult<Values>>;

  compile(
    expression: TypeExpr<PresentationType<Values>>,
    options?: CompileOptions,
  ): CompiledType<Values, Environment>;

  subtype(
    left: TypeExpr<PresentationType<Values>>,
    right: TypeExpr<PresentationType<Values>>,
  ): SubtypeDecision;

  explainMatch(match: Match<Values>, level?: DiagnosticLevel): Diagnostic;
  explainFailure(failure: MatchFailure, level?: DiagnosticLevel): Diagnostic;
  diagnostics(): readonly RegistryDiagnostic[];
}
```

## A.9 Acceptance and ephemeral predicates

```ts
export interface PreparedPredicate<Values extends PresentationValues, Environment> {
  test(
    match: Match<Values>,
    environment: Environment,
  ): boolean | RefinementDecision<unknown>;
}

export interface AcceptRequest<Values extends PresentationValues, Environment> {
  readonly type: TypeExpr<PresentationType<Values>>;
  readonly prompt: string;
  readonly translation?: TranslationPolicy;
  readonly environmentPolicy?: "snapshot" | "live";
  readonly where?: Readonly<{
    cache?: "none" | "identity" | "operation";
    prepare?(
      environment: Environment,
      signal: AbortSignal,
    ): PreparedPredicate<Values, Environment>;
    test?: PreparedPredicate<Values, Environment>["test"];
  }>;
}
```

The provider can expose both evidence-preserving and compatibility methods:

```ts
acceptMatch(request): Promise<Match<Values> | null>;
accept(request): Promise<PresentationReference<Values> | null>;
```

## A.10 Action methods

```ts
export interface ActionSignature<Type extends string = string> {
  readonly subject: TypeExpr<Type>;
  readonly context?: TypeExpr<Type>;
  readonly gesture?: TypeExpr<Type>;
  readonly argument?: TypeExpr<Type>;
}

export interface ActionMethod<
  Values extends PresentationValues,
  Environment,
  Verb,
> {
  readonly id: string;
  readonly signature: ActionSignature<PresentationType<Values>>;
  readonly mode?: "contribute" | "singular";

  applicable?(
    matches: ActionMatchTuple<Values>,
    environment: Environment,
  ): RefinementDecision<unknown>;

  actions(
    matches: ActionMatchTuple<Values>,
    environment: Environment,
  ): readonly PresentationAction<Verb>[];
}

export interface ActionRegistry<Values, Environment, Verb> {
  define(method: ActionMethod<Values, Environment, Verb>): void;
  prefer(preferredMethodId: string, overMethodId: string): void;
  resolve(input: ActionDispatchInput<Values, Environment>): ActionResolution<Verb>;
}
```

Contributing methods can combine actions. Singular methods require a unique maximal method or explicit preference.

## A.11 React factory

```ts
export interface CreatePbuiOptions<Values, Environment, Verb> {
  readonly registry: PresentationRegistry<Values, Environment>;
  readonly actions: ActionRegistry<Values, Environment, Verb>;
  readonly defaultEnvironment: Environment;
  readonly defaultActionContext?: PresentationReference<Values>;
  readonly renderMenuHeader?: MenuHeaderRenderer<Values, Environment>;
}

export interface PbuiContextValue<Values, Environment, Verb> {
  readonly environment: Environment;
  readonly accepting: ActiveInputContext<Values, Environment> | null;

  acceptMatch(
    request: AcceptRequest<Values, Environment>,
  ): Promise<Match<Values> | null>;

  accept(
    request: AcceptRequest<Values, Environment>,
  ): Promise<PresentationReference<Values> | null>;

  abortAccept(): void;
  classify(reference: PresentationReference<Values>): Applicability;
  satisfyAccept(reference: PresentationReference<Values>): Promise<void>;
  perform(verb: Verb): void | Promise<void>;
}
```

## A.12 What the companion code implements

`code/semantic-types.ts` implements the synchronous semantic kernel:

- atoms;
- representation-safe nominal subtyping;
- marker capabilities;
- normalized union, intersection, and difference;
- named refinements with witnesses and dependency tokens;
- semantic identity and revisions;
- evidence-producing direct matching;
- pure partial weighted translators;
- bounded translation search;
- a conservative symbolic subtype prover.

It intentionally omits React, asynchronous checks, capability dictionaries, action dispatch, remote expressions, and BDDs. Those omissions demonstrate how the API can be layered.
EOF

cat > docs/textbook/appendix-c-notation.md <<'EOF'
# Appendix C — Notation and Laws

## C.1 Universes

| Notation | Meaning |
|---|---|
| \(K\) | set of atomic presentation tags |
| \(V_k\) | value carrier associated with tag \(k\) |
| \(\mathrm{Ref}=\sum_{k\in K}V_k\) | tagged reference universe |
| \(R\) | frozen semantic registry |
| \(E\) | environment or state snapshot |
| \(\tau,\sigma,\rho\) | presentation type expressions |
| \(r,s\) | presentation references |
| \(w\) | positive match evidence |
| \(q\) | failure or negative evidence |

## C.2 Denotation

\[
\llbracket \tau \rrbracket_{R,E}
\subseteq \mathrm{Ref}
\]

is the set of references denoted by \(\tau\) under registry \(R\) and environment \(E\).

## C.3 Judgments

| Judgment | Reading |
|---|---|
| \(R\vdash\tau\;\mathsf{type}\) | \(\tau\) is well formed |
| \(R\vdash\tau<:\sigma\) | \(\tau\) is a subtype of \(\sigma\) |
| \(R;E\vdash r\Downarrow\tau\Rightarrow w\) | \(r\) matches \(\tau\), producing \(w\) |
| \(R;E\vdash r\not\Downarrow\tau\Rightarrow q\) | \(r\) fails to match \(\tau\), explained by \(q\) |
| \(r\approx_E s\) | \(r\) and \(s\) denote the same semantic object |

## C.4 Type grammar

\[
\tau ::= \top
\mid \bot
\mid \operatorname{atom}(k)
\mid \operatorname{cap}(c)
\mid \tau\lor\tau
\mid \tau\land\tau
\mid \tau\setminus\tau
\mid \operatorname{refine}(\tau,p,a).
\]

## C.5 Denotational equations

\[
\llbracket\top\rrbracket=\mathrm{Ref}
\]

\[
\llbracket\bot\rrbracket=\varnothing
\]

\[
\llbracket\tau\lor\sigma\rrbracket
=\llbracket\tau\rrbracket\cup\llbracket\sigma\rrbracket
\]

\[
\llbracket\tau\land\sigma\rrbracket
=\llbracket\tau\rrbracket\cap\llbracket\sigma\rrbracket
\]

\[
\llbracket\tau\setminus\sigma\rrbracket
=\llbracket\tau\rrbracket\setminus\llbracket\sigma\rrbracket
\]

\[
\llbracket\operatorname{refine}(\tau,p,a)\rrbracket_{R,E}
=
\{r\in\llbracket\tau\rrbracket_{R,E}\mid p_R(r,a,E)\}.
\]

## C.6 Lattice and Boolean laws

For semantic equivalence \(\simeq\):

### Identity

\[
A\lor\bot\simeq A,
\qquad
A\land\top\simeq A.
\]

### Domination

\[
A\lor\top\simeq\top,
\qquad
A\land\bot\simeq\bot.
\]

### Idempotence

\[
A\lor A\simeq A,
\qquad
A\land A\simeq A.
\]

### Commutativity

\[
A\lor B\simeq B\lor A,
\qquad
A\land B\simeq B\land A.
\]

### Associativity

\[
(A\lor B)\lor C\simeq A\lor(B\lor C),
\]

\[
(A\land B)\land C\simeq A\land(B\land C).
\]

### Absorption

\[
A\lor(A\land B)\simeq A,
\qquad
A\land(A\lor B)\simeq A.
\]

### Distribution

\[
A\land(B\lor C)
\simeq
(A\land B)\lor(A\land C).
\]

### Difference

\[
A\setminus\bot\simeq A,
\qquad
A\setminus A\simeq\bot,
\qquad
\bot\setminus A\simeq\bot.
\]

### Subtyping by emptiness

\[
A<:B
\quad\Longleftrightarrow\quad
A\setminus B\simeq\bot.
\]

## C.7 Identity laws

Within one coherent environment snapshot:

\[
r\approx r
\]

\[
r\approx s\Rightarrow s\approx r
\]

\[
r\approx s\land s\approx t\Rightarrow r\approx t.
\]

For an identity-preserving translator \(f\):

\[
f(r)=s\Rightarrow r\approx s.
\]

## C.8 Matching laws

### Direct soundness

\[
R;E\vdash r\Downarrow\tau\Rightarrow w
\Rightarrow
r\in\llbracket\tau\rrbracket_{R,E}.
\]

### Translation soundness

If translation-aware matching accepts target \(s\) as \(\tau\), then

\[
s\in\llbracket\tau\rrbracket_{R,E}.
\]

If every path edge preserves identity, then

\[
r\approx s.
\]

### Normalization preservation

\[
\llbracket\operatorname{normalize}(\tau)\rrbracket
=
\llbracket\tau\rrbracket.
\]

## C.9 Cache law

For predicate \(p\) and dependency function \(d\), sound reuse requires:

\[
d(r,E_1)=d(r,E_2)
\Rightarrow
p(r,E_1)=p(r,E_2).
\]

## C.10 Dispatch order

For method signatures

\[
M=(\tau_1,\ldots,\tau_n),
\]

define

\[
M_1\preceq M_2
\]

when every component of \(M_1\) is a subtype of the corresponding component of \(M_2\). Singular dispatch is coherent when the applicable set has a unique maximal semantic-equivalence class and duplicate representatives are resolved explicitly.

## C.11 Binding laws

Let \(b(v)\) be the subject binding of view \(v\).

### Sharing

\[
v_1\sim v_2
\quad\Longleftrightarrow\quad
b(v_1)=b(v_2).
\]

### Propagation

\[
b(v_1)=b(v_2)
\Rightarrow
\operatorname{subject}(v_1,r)=\operatorname{subject}(v_2,r).
\]

### Unlink copy

Immediately after unlinking \(v\) into fresh binding \(b'\):

\[
b'\ne b(v_{old})
\]

and

\[
\operatorname{subject}(b',r)
=
\operatorname{subject}(b(v_{old}),r).
\]
EOF

```

The formal core and strict TypeScript kernel now pass executable laws, including translation, dispatch, cache revalidation, and linked-subject coherence. Modular profiles let readers stop at increasing sophistication levels.

<details><summary>💭 Thinking</summary>

**Completing the textbook**

I’m filling the remaining appendices with selected solutions and an annotated bibliography, then I’ll assemble the chapters, validate the companion examples, and package the finished textbook with its source files.

**Completed the textbook**

</details>

```unknown
bash -lc set -euo pipefail
cd /mnt/data/pbui_book_work/pbui
find docs/textbook -maxdepth 2 -type f | sort
printf '\nWord counts:\n'
wc -w docs/textbook/*.md docs/textbook/code/*.ts | tail -n 8
printf '\nREADME tail:\n'
tail -n 80 README.md
printf '\nBook README:\n'
sed -n '1,260p' docs/textbook/README.md
```

<details><summary>💭 Thinking</summary>

**Inspected textbook files and drafted appendices and bibliography**

</details>

```unknown
bash -lc set -euo pipefail
cd /mnt/data/pbui_book_work/pbui
cat > docs/textbook/appendix-b-solutions.md <<'EOF'
# Appendix B — Selected Exercise Solutions

These are model solutions to the exercises marked **◆**. They are not the only acceptable answers. For design exercises, the important criteria are explicit assumptions, separation of concerns, and a defensible account of failure modes. For proof exercises, the important criteria are a stated universe, correctly used definitions, and no hidden appeal to implementation behavior.

## B.1 Chapter 1, Exercise 5 — Identically represented strings

Consider these values:

```ts
const documentId = "42";
const userId = "42";
const fieldName = "42";
```

All three have the JavaScript representation `string`, yet they should have distinct presentation types:

```text
DocumentId
UserId
FieldName
```

The distinction is semantic rather than structural. A document ID might support “open document,” “link document selection,” or translation to a loaded document. A user ID might support “open profile” or translation to an account. A field name may be meaningful only relative to a document or table. Treating all three as one presentation type would make unrelated actions and translators applicable.

The identity domains must normally differ as well:

```ts
{ namespace: "document", key: "42" }
{ namespace: "user", key: "42" }
{ namespace: "field", key: [documentId, "42"] }
```

The example establishes a general rule: runtime representation is not a sufficient definition of interface meaning. A presentation type names the role under which a value is offered to the interaction system.

## B.2 Chapter 2, Exercise 6 — Classifying four relations

1. **An employee used as a person:** subtyping, provided the employee representation can be consumed directly by operations expecting a person and the domain contract states that every employee is a person.

   \[
   \mathsf{Employee} <: \mathsf{Person}.
   \]

2. **A document ID looked up as a document:** translation. The operation changes representation, may consult an environment, and may fail.

   \[
   \mathsf{DocumentId} \rightharpoonup \mathsf{Document}.
   \]

3. **An active project:** refinement. It denotes the subset of projects satisfying a contextual predicate such as `archived === false`.

   \[
   \{p\in\mathsf{Project}\mid \neg p.\mathit{archived}\}.
   \]

4. **A chart used as a document-backed view:** either direct acceptance through a capability or nominal subtyping under a representation-safe interface. The cleaner design is usually capability membership:

   \[
   \mathsf{Chart} \subseteq \mathsf{DocumentBacked}.
   \]

   If `DocumentBacked` supplies operations such as `getDocumentBinding`, the match should also return the capability dictionary. Calling this relation translation would be misleading because no new chart value need be created.

## B.3 Chapter 3, Exercise 5 — Exact lists as finite unions

Let the legacy request contain the exact type names

\[
L=[k_1,\ldots,k_n].
\]

Its acceptance rule is:

\[
\operatorname{accepts}_L(r)
\quad\text{iff}\quad
\operatorname{tag}(r)=k_i\text{ for some }i.
\]

Associate each name with an atomic semantic type whose denotation is exactly the references carrying that tag:

\[
\llbracket k_i\rrbracket
=
\{r\in\mathsf{Ref}\mid \operatorname{tag}(r)=k_i\}.
\]

The denotation of the finite union is

\[
\llbracket k_1\lor\cdots\lor k_n\rrbracket
=
\bigcup_{i=1}^{n}\llbracket k_i\rrbracket.
\]

Therefore

\[
r\in\llbracket k_1\lor\cdots\lor k_n\rrbracket
\]

holds exactly when `tag(r)` equals at least one list member, which is the legacy rule. Duplicate names do not change the union because union is idempotent. An empty list denotes the empty union, hence `bottom`, if the legacy API interprets it as accepting nothing.

This equivalence justifies compiling a backward-compatible request into a structured type expression. It does not yet account for subtypes or translators; exact atomic denotations must be used to preserve legacy behavior.

## B.4 Chapter 4, Exercise 5 — Identity pairs form an equivalence

Define semantic identity on references by

\[
r\approx s
\quad\text{iff}\quad
N(r)=N(s)\land K(r)=K(s),
\]

where `N` returns an identity namespace and `K` returns a key. Assume equality on namespaces and equality on keys are equivalence relations.

**Reflexivity.** For every reference `r`, namespace equality gives `N(r)=N(r)` and key equality gives `K(r)=K(r)`. Hence `r≈r`.

**Symmetry.** Suppose `r≈s`. Then `N(r)=N(s)` and `K(r)=K(s)`. By symmetry of both equalities, `N(s)=N(r)` and `K(s)=K(r)`. Hence `s≈r`.

**Transitivity.** Suppose `r≈s` and `s≈t`. Then

\[
N(r)=N(s),\quad N(s)=N(t)
\]

and

\[
K(r)=K(s),\quad K(s)=K(t).
\]

By transitivity, `N(r)=N(t)` and `K(r)=K(t)`, so `r≈t`.

Thus `≈` is an equivalence relation. The proof also shows why the namespace cannot usually be omitted: equal keys from different entity domains would create false cross-domain equivalence classes.

## B.5 Chapter 5, Exercise 5 — Subtyping as emptiness of difference

By definition,

\[
A <: B
\quad\text{iff}\quad
A\subseteq B.
\]

We prove

\[
A\subseteq B
\quad\text{iff}\quad
A\setminus B=\varnothing.
\]

**Forward direction.** Assume `A⊆B`. Suppose for contradiction that some `x` belongs to `A\B`. By difference membership, `x∈A` and `x∉B`. But `A⊆B` and `x∈A` imply `x∈B`, a contradiction. Therefore `A\B` is empty.

**Reverse direction.** Assume `A\B=∅`. To show `A⊆B`, choose arbitrary `x∈A`. If `x∉B`, then by definition `x∈A\B`, contradicting emptiness. Therefore `x∈B`. Since `x` was arbitrary, `A⊆B`.

This equivalence is operationally important. A semantic subtype checker may reduce `A <: B` to an emptiness question for `A\B`. The mathematical equivalence is exact; an implementation may nevertheless answer `unknown` because emptiness is undecidable or intentionally incomplete when opaque refinements are present.

## B.6 Chapter 6, Exercise 6 — Intersection soundness

We prove the intersection case of direct-match soundness. The final inference rule is

\[
\frac{
R;E\vdash r\Downarrow\tau\Rightarrow w_1
\qquad
R;E\vdash r\Downarrow\sigma\Rightarrow w_2
}{
R;E\vdash r\Downarrow\tau\land\sigma
\Rightarrow \operatorname{and}(w_1,w_2)
}.
\]

Assume the derivation ends with this rule. Its premises give two strictly smaller matching derivations. By the induction hypothesis applied to the first premise,

\[
r\in\llbracket\tau\rrbracket_{R,E}.
\]

By the induction hypothesis applied to the second premise,

\[
r\in\llbracket\sigma\rrbracket_{R,E}.
\]

The denotation of intersection is set intersection:

\[
\llbracket\tau\land\sigma\rrbracket_{R,E}
=
\llbracket\tau\rrbracket_{R,E}
\cap
\llbracket\sigma\rrbracket_{R,E}.
\]

An element belongs to an intersection exactly when it belongs to both operands. The two induction-hypothesis conclusions therefore imply

\[
r\in\llbracket\tau\land\sigma\rrbracket_{R,E}.
\]

This proves the case. Notice what was not required: the evidence values `w₁` and `w₂` did not need to be inspected. Their existence records that the premises were derived. A proof-relevant implementation retains them because later behavior may need refinement witnesses or capability dictionaries.

## B.7 Chapter 7, Exercise 4 — Curry–Howard and intersection

Under the propositions-as-types interpretation, the proposition

\[
P\land Q
\]

is inhabited by a pair containing evidence for `P` and evidence for `Q`. The introduction rule is

\[
\frac{p:P\qquad q:Q}{(p,q):P\land Q}.
\]

The PBUI intersection matching rule has exactly this shape. If the matcher can construct `w₁` witnessing that reference `r` belongs to `τ`, and `w₂` witnessing that the same `r` belongs to `σ`, it constructs

```ts
{
  kind: "intersection",
  left: w1,
  right: w2,
}
```

as evidence for `τ ∧ σ`.

The elimination operations are projections: code that receives intersection evidence may recover either constituent witness. This matters when the witnesses contain operational dictionaries. A match for

```text
Project ∧ Editable
```

may carry both nominal project evidence and an `Editable` dictionary with methods such as `updateTitle`.

The correspondence is not automatically a proof of arbitrary JavaScript facts. If `w₂` was created by calling an opaque predicate, the logical interpretation depends on the registry contract that the predicate returns a witness only when the stated proposition is true. Curry–Howard explains the shape and composition of evidence; it does not validate an untrusted callback by itself.

## B.8 Chapter 8, Exercise 6 — Mutual subtyping equivalence

Define semantic equivalence of type expressions by

\[
A\equiv B
\quad\text{iff}\quad
A<:B\land B<:A.
\]

Because semantic subtyping is set inclusion, we prove that `≡` is an equivalence relation.

**Reflexivity.** Set inclusion is reflexive, so `A⊆A` in both directions. Therefore `A≡A`.

**Symmetry.** If `A≡B`, then `A⊆B` and `B⊆A`. Reordering the conjunction gives `B⊆A` and `A⊆B`, hence `B≡A`.

**Transitivity.** If `A≡B` and `B≡C`, then `A⊆B⊆C`, so `A⊆C`. Likewise, `C⊆B⊆A`, so `C⊆A`. Hence `A≡C`.

By extensionality, mutual inclusion also implies that the denotations are equal. Syntactically different expressions can therefore occupy the same equivalence class, for example `A ∨ A` and `A`. A subtype implementation can quotient expressions by semantic equivalence conceptually, while retaining source syntax separately for diagnostics.

## B.9 Chapter 9, Exercise 4 — Negation in an extensible registry

A defensible policy is **base-relative difference plus registry-snapshot semantics**.

The ordinary public API exposes:

```ts
types.difference(Project, Archived)
```

rather than an unrestricted global complement `not(Archived)`. Its denotation is stable relative to the explicit base:

\[
\llbracket\mathsf{Project}\setminus\mathsf{Archived}\rrbracket
=
\{r\in\llbracket\mathsf{Project}\rrbracket
\mid r\notin\llbracket\mathsf{Archived}\rrbracket\}.
\]

Adding a new unrelated plugin atom does not change that set. A newly registered project subtype may change it, which is appropriate, but compiled expressions carry a registry version and are recompiled after registry extension.

An advanced API may expose unrestricted complement, but its universe must be explicit:

```ts
types.complement(types.registryUniverse(version), Archived)
```

The compiled matcher records the universe/version. A plugin installation increments the registry version and invalidates complement-dependent caches.

This policy is more verbose than a global `not`, but it avoids suggesting that complement has a timeless meaning in an open world. It also produces clearer action declarations: “project but not archived” is normally the intended proposition, not “every possible reference except archived references.”

## B.10 Chapter 10, Exercise 5 — Negative information from a failed refinement

Let a named refinement be

\[
S=\{r\in B\mid p(r,E)=\mathsf{true}\}.
\]

A failed evaluation establishes membership in `B\S` only under the following conditions:

1. the reference has already been shown to belong to the base `B`;
2. `p` is total for all members of `B` in the relevant environment;
3. evaluation terminates normally rather than returning “unknown,” throwing, timing out, or being cancelled;
4. `p` is two-valued and its false result means logical falsity, not lack of information;
5. the environment and object revision used by the conclusion are the same as, or dependency-equivalent to, those used by the evaluation;
6. the predicate implementation satisfies its declared semantic contract.

Under these assumptions, suppose `r∈B` and `p(r,E)=false`. By definition, `r∉S`. Therefore `r∈B` and `r∉S`, which is exactly `r∈B\S`.

Without totality, failure may mean “not proved.” Without revision stability, a project can become active immediately after the check. Without a two-valued contract, an authorization service returning “indeterminate” cannot justify negated permission. This is why a production matcher should distinguish `false`, `unknown`, and operational failure when negative evidence matters.

## B.11 Chapter 11, Exercise 4 — Indexed field subtyping

Define

\[
\mathsf{FieldOf}(d)
=
\{f\in\mathsf{Field}\mid \operatorname{document}(f)=d\}.
\]

Assume document indexing uses ordinary equality. We characterize

\[
\mathsf{FieldOf}(d_1)<:\mathsf{FieldOf}(d_2).
\]

If `d₁=d₂`, the two denotations are equal, so inclusion holds.

If `d₁≠d₂`, then a field cannot satisfy both equalities when `document(f)` is single-valued. If `FieldOf(d₁)` is inhabited, choose `f` with `document(f)=d₁`. It cannot also have `document(f)=d₂`; hence it is not in `FieldOf(d₂)`, and inclusion fails.

Therefore, under the additional assumption that every index denotes at least one field,

\[
\mathsf{FieldOf}(d_1)<:\mathsf{FieldOf}(d_2)
\quad\text{iff}\quad d_1=d_2.
\]

Without the non-emptiness assumption, an empty source type is a subtype of every type. The exact characterization is therefore:

\[
\mathsf{FieldOf}(d_1)<:\mathsf{FieldOf}(d_2)
\quad\text{iff}\quad
 d_1=d_2
\ \lor\ 
\mathsf{FieldOf}(d_1)=\varnothing.
\]

The subtle empty-set case is a useful reminder that semantic subtyping concerns denotations, not only constructor arguments.

## B.12 Chapter 12, Exercise 5 — Capability coherence

Use an **explicit ownership and qualification policy**:

1. Every capability has a globally stable ID such as `core/document-backed`.
2. A capability implementation is keyed by `(capabilityId, atomId)`.
3. The registry rejects a second unqualified implementation for the same pair.
4. A plugin that intentionally supplies an alternative must register a qualified implementation ID and cannot silently replace the default.
5. Selection among alternatives requires an explicit provider configuration or preference declaration.
6. Registry freeze validates that each required pair has one selected coherent implementation.

Example:

```ts
registry.implement(DocumentBacked, Chart, {
  id: "core/chart-document-binding",
  dictionary: coreChartBinding,
});

registry.implementAlternative(DocumentBacked, Chart, {
  id: "plugin-x/remote-chart-binding",
  dictionary: remoteChartBinding,
});
```

The application must then choose:

```ts
registry.prefer(
  [DocumentBacked, Chart],
  "plugin-x/remote-chart-binding",
);
```

This is stricter than last-registration-wins and easier to debug than numeric priority. It makes incoherence a startup error rather than a pointer-event surprise. For open plugin ecosystems, the registry should report both module origins and the exact conflicting semantic pair.

## B.13 Chapter 13, Exercise 4 — Equal-cost translation paths

Use a lexicographic ordering over explicit path metadata:

1. lower total cost;
2. fewer effectful edges;
3. fewer asynchronous edges;
4. fewer total edges;
5. higher minimum edge priority, then higher summed priority;
6. lexicographically smaller stable translator-ID sequence.

The first four criteria encode semantic preferences: cheap, pure, synchronous, short paths are generally easier to explain and less failure-prone. The final ID ordering is not semantically meaningful; it merely guarantees deterministic output when the registry declares otherwise equivalent alternatives.

A stronger policy rejects an unresolved tie rather than selecting by ID when the resulting targets may differ semantically. Translators can declare a coherence group and a target-equivalence contract. If two equal-ranked paths are not known coherent, the result should be:

```ts
{
  ok: false,
  reason: "ambiguous-translation",
  paths: [pathA, pathB],
}
```

For PBUI, the recommended default is deterministic selection only among pure paths whose final targets are either semantically identical or declared coherent. Any ambiguous effectful path should require an explicit preference. The evidence records the selected path and the alternatives considered.

## B.14 Chapter 14, Exercise 4 — Incomparable action methods

Suppose these methods are both applicable:

```text
M₁ = (Project ∧ Editable, WorkspaceContext)
M₂ = (Project, AdministrativeContext)
```

The current subject is an editable project, and the current context is both a workspace context and an administrative context. `M₁` is narrower in the subject coordinate, while `M₂` is narrower in the context coordinate. Neither signature is componentwise below the other, so they are incomparable and both maximal.

Choose the **combine-by-action-ID** policy because these methods contribute menu entries rather than competing implementations:

- collect actions from every maximal applicable method;
- group by stable action ID;
- retain both when IDs differ;
- treat duplicate IDs as an explicit override/coherence problem;
- order the visible actions by menu group and presentation metadata, not by pretending one method is more specific.

For example, `M₁` may contribute “Edit project,” while `M₂` contributes “Archive project.” Both should appear. If both contribute `save`, the registry should require a preference or reject the ambiguity. This preserves the partial-order semantics instead of hiding incomparability behind registration order.

## B.15 Chapter 15, Exercise 5 — Union normalization preservation

Assume normalization recursively normalizes members, flattens nested unions, removes duplicate members, removes `bottom`, and returns `top` if a `top` member is present.

We show that each rewrite preserves denotation.

- **Flattening:** `(A∨B)∨C` and `A∨B∨C` both denote `⟦A⟧∪⟦B⟧∪⟦C⟧` by associativity of union.
- **Deduplication:** `A∨A` denotes `⟦A⟧∪⟦A⟧=⟦A⟧` by idempotence.
- **Bottom removal:** `A∨⊥` denotes `⟦A⟧∪∅=⟦A⟧`.
- **Top absorption:** `A∨⊤` denotes `⟦A⟧∪Ref=Ref=⟦⊤⟧`.
- **Recursive normalization:** by the induction hypothesis, replacing each member with its normalized form preserves that member’s denotation; union is congruent under equality of operands.

A finite sequence of denotation-preserving rewrites preserves denotation by transitivity of equality. Therefore

\[
\llbracket\operatorname{normalize}(\tau_1\lor\cdots\lor\tau_n)\rrbracket
=
\bigcup_i\llbracket\tau_i\rrbracket.
\]

Sorting members by stable expression ID may establish a canonical representation but has no semantic effect because union is commutative.

## B.16 Chapter 16, Exercise 3 — Two identity-preserving translation edges

Let

\[
r_0\xrightarrow{t_1}r_1\xrightarrow{t_2}r_2
\]

be a successful path. Assume both translators are sound and identity-preserving:

\[
r_0\approx r_1
\qquad\text{and}\qquad
r_1\approx r_2.
\]

Assume direct matching constructs evidence

\[
R;E\vdash r_2\Downarrow\tau\Rightarrow w.
\]

By direct-match soundness,

\[
r_2\in\llbracket\tau\rrbracket_{R,E}.
\]

This establishes that the accepted target satisfies the requested semantic type.

For identity, semantic identity is assumed transitive. From `r₀≈r₁` and `r₁≈r₂`, transitivity gives

\[
r_0\approx r_2.
\]

The complete evidence may be represented as:

```ts
{
  kind: "translation",
  source: r0,
  target: r2,
  steps: [
    { translatorId: t1.id, source: r0, target: r1 },
    { translatorId: t2.id, source: r1, target: r2 },
  ],
  targetEvidence: w,
  preservesIdentity: true,
}
```

The proof does not imply `r₀∈⟦τ⟧`: `r₀` may have a project-ID representation while `τ` requires a project representation. It proves membership of the translated target and sameness of denotation under the explicit identity contracts.

## B.17 Chapter 17, Exercise 4 — Sound memoization

Let a deterministic predicate be `p(r,E)` and let `d(r,E)` be its dependency fingerprint. Assume dependency stability:

\[
d(r,E_1)=d(r,E_2)
\Rightarrow
p(r,E_1)=p(r,E_2).
\]

Suppose the cache stores

\[
(d(r,E_1),\ p(r,E_1)).
\]

At a later evaluation under `E₂`, the cache computes `d(r,E₂)` and finds it equal to the stored fingerprint. The value returned by the cache is `p(r,E₁)`. By the stability assumption,

\[
p(r,E_1)=p(r,E_2).
\]

Therefore the cached value equals the value a fresh evaluation would return under `E₂`, so reuse is sound.

For witness-producing predicates, equality must be strengthened. If later code consumes only the truth value, equal decisions suffice. If later code consumes a permission token or capability dictionary, equal fingerprints must imply observationally equivalent witnesses for those operations. A safe implementation may cache the decision but rematerialize occurrence-specific output, or it may include witness version/provenance in the fingerprint.

The proof is conditional: it does not prove that a declared dependency function is complete. Omitting `authorizationEpoch` from a permission predicate’s fingerprint violates the premise and makes the cache unsound.

## B.18 Chapter 18, Exercise 3 — Unlink independence

Use the normalized model:

```text
views[v].bindingId = b
bindings[b].roles = S
```

Suppose view `v` shares binding `b` with other views. Unlinking allocates a fresh binding `b'`, copies the role map, and changes only `v`:

```text
bindings[b'].roles := copy(bindings[b].roles)
views[v].bindingId := b'
```

All other views and binding `b` are unchanged.

Immediately after unlinking,

\[
\operatorname{roles}(b')=\operatorname{roles}(b),
\]

so `v` preserves its visible subject selection.

Now perform a later update on `b'`, producing state `S'`. Only views whose `bindingId` is `b'` observe that update. By construction, `v` is one such view and every previously linked other view still points to `b`. Therefore their effective role maps remain `S`, while `v` observes `S'`.

Conversely, a later update to `b` changes the other views and not `v`. Thus after unlinking, updates to either binding are independent. The proof relies on fresh allocation and on reducers updating binding entities by ID rather than mutating a shared role-map object through an alias.

## B.19 Chapter 19, Exercise 5 — Keyboard interaction for 5,000 marks

Do not put 5,000 SVG marks in the tab order. Use a composite interaction model:

1. The chart itself is one tab stop with an accessible label and instructions.
2. Entering semantic-navigation mode activates an `aria-activedescendant` or equivalent managed-focus model.
3. Arrow keys navigate an indexed logical neighborhood: next time point, previous series, nearest spatial mark, or next filtered result.
4. A search command opens a virtualized list backed by the same compiled `TypeExpr`; it can find off-screen and unmounted marks.
5. Enter commits the active semantic mark to the input context; Escape exits or aborts.
6. A compact live region announces the active mark’s series, coordinates, value, and applicability.
7. A data-table alternative exposes the same marks through rows and columns.
8. Pointer hover may update the active mark, but keyboard state is not made dependent on hover.

The semantic index should be separate from the DOM occurrence registry. Each mark has a stable identity and searchable attributes. Only the active visual occurrence needs an accessibility focus proxy. This design keeps tab traversal bounded, supports virtualization, and lets dynamic PBUI acceptance work over the domain index rather than only mounted nodes.

## B.20 Chapter 20, Exercise 3 — Union normalization case

Assume the normalization theorem holds recursively for `τ` and `σ`:

\[
\llbracket N(\tau)\rrbracket=\llbracket\tau\rrbracket,
\qquad
\llbracket N(\sigma)\rrbracket=\llbracket\sigma\rrbracket.
\]

For a union, the normalizer first normalizes operands and then applies flattening, deduplication, and identity/absorption rewrites. Before those rewrites,

\[
\llbracket N(\tau)\lor N(\sigma)\rrbracket
=
\llbracket N(\tau)\rrbracket
\cup
\llbracket N(\sigma)\rrbracket.
\]

By the induction hypotheses, this equals

\[
\llbracket\tau\rrbracket\cup\llbracket\sigma\rrbracket
=
\llbracket\tau\lor\sigma\rrbracket.
\]

Each subsequent canonicalization rewrite preserves union denotation by associativity, commutativity, idempotence, the empty-set identity, and universal-set absorption. Therefore the final normalized union has the same denotation as the original union.

If the implementation interns normalized nodes, pointer equality of the resulting expression is an optimization consequence, not part of the semantic proof. The proof concerns denotational equality.

## B.21 Chapter 21, Exercise 3 — Removing three features

Assume the primary use case is: “Any visible field can satisfy a chart-encoding request, including a contextual restriction to the active document.” Retain atoms, named refinements, direct matching, semantic identity, and React input contexts.

Remove:

1. **General negation/difference.** The use case can express positive refinements such as `FieldOf(activeDocument)` without complements. This avoids open-world complement semantics and a Boolean normalizer.
2. **Multi-edge translator search.** Require one explicit direct translator per accepted alternate representation. This removes path ambiguity, budgets, and path coherence while preserving `FieldName → Field` if needed.
3. **Multiple-dispatch actions.** Keep descriptor-local actions and one contextual action-rule list. The use case is acceptance-oriented and does not yet require dispatch over subject, context, gesture, and argument tuples.

This yields an intermediate profile:

```text
atoms + nominal subtyping
named refinements
identity and revisions
evidence-producing direct matching
one-step translators
provider-scoped input contexts
```

The omitted features can later be added behind stable interfaces. The key is that the semantic model does not require the maximum implementation profile on day one.

## B.22 Chapter 22, Exercise 6 — A comparison with Datalog and ProseMirror

| Dimension | Proposed PBUI | Datalog engine | ProseMirror |
|---|---|---|---|
| Primary unit | semantic reference/presentation | fact and relation tuple | document node/mark and transaction |
| Classification | type expressions and refinements | derived predicates from rules | schema node and mark types |
| Inference | matching, subtype closure, translation | fixed-point rule evaluation | transaction and plugin-state application |
| Contextual behavior | action multimethods and input contexts | query/rule parameters | commands, plugins, keymaps |
| Evidence | explicit match/provenance tree | proof/provenance can be derived from rule firing | transaction steps and plugin metadata |
| Identity | registry-defined semantic identity | tuple/value identity | positions, node structure, plugin keys |
| Incrementality | revision/dependency caches | semi-naive/incremental evaluation | mapped positions and incremental transactions |
| Main lesson for PBUI | — | use indexed declarative facts for applicability and explanation | separate immutable semantic state changes from view/plugin behavior |
| Assumption not to borrow | — | closed-world negation as failure is unsafe for every plugin/refinement context | tree-position identity is not general domain-object identity |

Datalog suggests a future alternative for large rule sets: compile stable capabilities, subtype facts, and action applicability into an indexed relation engine. ProseMirror suggests treating interactions as explicit transactions over a normalized model rather than component-local mutations. Neither system is a drop-in presentation manager: Datalog lacks visual occurrences and gestures, while ProseMirror specializes in structured document editing.

## B.23 Chapter 23, Exercise 4 — Link conflict UI

Assume the source chart selects document `A` and the target pipeline selects document `B`. Activating “Link document selection” should not silently discard one selection.

Use a small conflict step anchored to the two tiles:

```text
These views currently use different documents.

Chart:    Sales 2025 (A)
Pipeline: Forecast inputs (B)

[Use chart document] [Use pipeline document] [Cancel]
```

The initial link gesture establishes the two candidate views but does not mutate state. The conflict step produces one explicit verb:

```ts
{
  type: "linkDocumentBindings",
  sourceBindingId,
  targetBindingId,
  resolution: "source" | "target",
  expectedSourceRevision,
  expectedTargetRevision,
}
```

The reducer checks revisions atomically. If either changed, the conflict is recomputed rather than applying stale intent. Keyboard focus starts on the explanatory heading or the first safe choice; Escape cancels. The labels name actual views and documents rather than abstract “source” and “target.”

For matching role maps with several differing roles, show a compact table and support either one whole-binding winner or per-role resolution. Start with a whole-binding policy unless users genuinely need mixed results.

## B.24 Chapter 24, Exercise 6 — Six-week research prototype

**Direction:** provenance-aware evidence and invalidation.

**Question:** Can explicit dependency provenance reduce predicate recomputation while preserving commitment-time correctness in a 10,000-presentation workspace?

**Week 1 — Model and baseline.** Define evidence, dependency tokens, environment epochs, and three predicate classes. Build a naïve matcher that re-evaluates every candidate. Establish benchmark fixtures and correctness oracles.

**Week 2 — Instrumentation.** Add callback counts, cache hit rates, evidence sizes, invalidation causes, and commitment revalidation logs. Build a trace viewer.

**Week 3 — Dependency cache.** Implement `(expression, identity, revision, dependencyFingerprint)` caching. Add property tests that compare cached and uncached decisions under generated valid state changes.

**Week 4 — Provenance.** Record which atom, capability, refinement, and translator facts contributed to each match. Implement targeted invalidation from changed dependency tokens.

**Week 5 — React integration.** Test mounted and virtualized presentations, superseded input contexts, and stale asynchronous results. Conduct accessibility checks for explanation views.

**Week 6 — Evaluation.** Compare naïve and provenance-aware systems over representative interaction traces.

**Success criteria:**

- zero decision mismatches against the uncached oracle in generated tests;
- zero stale commits in adversarial revision-change tests;
- at least 80% fewer refinement evaluations in a stable 10,000-object trace;
- median match-inspection latency below 16 ms for already indexed candidates;
- evidence explanation identifies every trusted callback and invalidating dependency;
- a written account of cases where provenance overhead outweighs savings.

A negative performance result still succeeds scientifically if correctness and overhead are measured clearly.
EOF
wc -w docs/textbook/appendix-b-solutions.md
```

<details><summary>💭 Thinking</summary>

**Wrote Appendix B solutions content**

</details>

```json
{"search_query":[{"q":"site:mcclim.common-lisp.dev McCLIM manual presentations input contexts translators command tables"},{"q":"site:lispworks.com/documentation clim presentation types translators command tables CLIM 2"},{"q":"ACM A presentation manager based on application semantics McKay 1989"},{"q":"CLIM Common Lisp Interface Manager paper 1991 ACM"}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Searched 18 websites**

</details>

```unknown
bash -lc set -euo pipefail
cd /mnt/data/pbui_book_work/pbui
cat > docs/textbook/bibliography.md <<'EOF'
# Bibliography and Annotated Resources

The citations in this book use short keys such as **[TAPL]** and **[CLIM2]**. URLs point to publisher pages, official manuals, project sites, or primary papers where practical. Access dates are omitted because the source package records no claim that a web page is immutable; version-sensitive resources identify the version or date discussed in the text.

## A. Presentation-based interfaces and CLIM

### [McKay1989]

Scott McKay, William York, and Michael McMahon. “A Presentation Manager Based on Application Semantics.” In *Proceedings of the 2nd Annual ACM SIGGRAPH Symposium on User Interface Software and Technology (UIST ’89)*, pp. 141–148, 1989. DOI: [10.1145/73660.73678](https://doi.org/10.1145/73660.73678).

This is the central historical paper for the idea that displayed interface entities should be associated with their semantic application objects and classified in a type lattice. It is the most direct ancestor of the architecture developed here. Its implementation setting predates React, normalized client stores, and TypeScript, so this book reconstructs its separations rather than copying its mechanisms.

### [McKay1991]

Scott McKay. “CLIM: The Common Lisp Interface Manager.” *Communications of the ACM* 34, no. 9 (September 1991), pp. 58–59. DOI: [10.1145/114669.114675](https://doi.org/10.1145/114669.114675).

A concise account of CLIM’s object-and-operation-centered view of interface construction. It is useful as a statement of intent; the full protocols are documented in the specification and manuals below.

### [CLIM2]

*Common Lisp Interface Manager (CLIM), Release 2.0 Specification*. 1990s specification, preserved in several distributions and archives. A scanned release is available at [the Bitsavers mirror](https://archive.decromancer.ca/bitsavers.org/pdf/symbolics/software/genera_8/Common_Lisp_Interface_Manager__CLIM__Release_2.0.pdf).

The normative reference for presentation types, presentations, input contexts, translators, command tables, application frames, output recording, and incremental redisplay. It is broad and protocol-oriented. Readers should resist reducing CLIM to the subset implemented in the companion TypeScript kernel.

### [McCLIM]

The McCLIM Project. *McCLIM User’s Manual*. [https://mcclim.common-lisp.dev/static/manual/mcclim.html](https://mcclim.common-lisp.dev/static/manual/mcclim.html). Project site: [https://mcclim.common-lisp.dev/](https://mcclim.common-lisp.dev/).

McCLIM is the active free-software implementation of CLIM. The manual is a practical way to study application frames, presentations, input contexts, commands, command tables, and translators in an executable system. Its examples also make clear that a presentation manager is integrated with a larger interaction architecture.

### [LispWorksCLIM]

LispWorks. *CLIM 2.0 User Guide*. [PDF](https://www.lispworks.com/documentation/pdf/lw80/clim-8-0.pdf) and [HTML contents](https://www.lispworks.com/documentation/lw80/clim/).

A concept-organized guide based on the CLIM II specification. The chapters on defining presentation types, translator applicability, input contexts, application frames, and the command processor are especially relevant. The examples of translators show that applicability depends on source and target presentation types, context, gesture, and optional testers—not merely on an unconstrained conversion function.

### [GuidedTourCLIM]

N. I. A. “A Guided Tour of the Common Lisp Interface Manager,” originally published in *Lisp Pointers* in 1991; later updated examples for McCLIM by Clemens Fruhwirth. [Updated PDF](https://dept-info.labri.fr/~strandh/guided-tour.pdf). DOI for the original ACM item: [10.1145/121994.121996](https://doi.org/10.1145/121994.121996).

A more tutorial introduction than the specification. It is useful for seeing the interaction of CLIM facilities in complete examples. Historical variants exist, so exact APIs should be checked against the target CLIM implementation.

### [CLIMPerspective]

Ralf Möller. “User Interface Management Systems: The CLIM Perspective.” [https://www.chai.uni-hamburg.de/~moeller/uims-clim/clim-intro.html](https://www.chai.uni-hamburg.de/~moeller/uims-clim/clim-intro.html).

An overview of CLIM concepts in the broader context of user-interface management systems. It is useful for comparing CLIM’s abstractions with Smalltalk and other object-oriented UI traditions.

### [FranzCLIM2]

Franz Inc. *clim2* source repository. [https://github.com/franzinc/clim2](https://github.com/franzinc/clim2).

An open source codebase for studying a production CLIM implementation. Its value is architectural and historical. It should not be treated as a modern JavaScript API template.

## B. General type theory, logic, and proof

### [TAPL]

Benjamin C. Pierce. *Types and Programming Languages*. MIT Press, 2002. [Publisher page](https://mitpress.mit.edu/9780262303828/types-and-programming-languages/). ISBN 978-0-262-16209-8.

The standard pragmatic introduction to operational semantics, typed lambda calculi, subtyping, recursive types, polymorphism, and type-system metatheory. Chapters 4–8 of this book borrow its discipline of defining syntax, judgments, and proofs separately from an implementation. TAPL primarily studies static languages; PBUI uses related mathematics for a runtime interaction protocol.

### [ATTAPL]

Benjamin C. Pierce, editor. *Advanced Topics in Types and Programming Languages*. MIT Press, 2005. [Publisher page](https://mitpress.mit.edu/9780262552677/advanced-topics-in-types-and-programming-languages/).

A collection on advanced type analyses, low-level typing, modules, proof, and related topics. It is a bridge from TAPL to the research literature. No single chapter directly specifies a presentation manager, but many techniques inform extensions discussed in Chapter 24.

### [PFPL]

Robert Harper. *Practical Foundations for Programming Languages*, 2nd edition. Cambridge University Press, 2016. Author’s materials: [https://www.cs.cmu.edu/~rwh/pfpl/](https://www.cs.cmu.edu/~rwh/pfpl/).

A systematic account of programming-language concepts using judgments and structural operational semantics. It is especially valuable for understanding hypothetical judgments, inductive definitions, dynamics/statics separation, and the design of small calculi. The phrase “practical foundations” is apt for PBUI: formal structure should organize an implementation rather than decorate it after the fact.

### [ProofsAndTypes]

Jean-Yves Girard, translated and with appendices by Paul Taylor and Yves Lafont. *Proofs and Types*. Cambridge University Press, 1989; corrected web edition, 2003. [Open PDF](https://www.paultaylor.eu/stable/prot.pdf).

A classic introduction to typed lambda calculus and the propositions-as-types correspondence. Chapter 7 uses its perspective to motivate evidence-producing matches. The companion kernel applies only a small fragment of these ideas; it is not a proof assistant or a dependently typed language.

### [SoftwareFoundations]

Benjamin C. Pierce and many contributors. *Software Foundations* series. [https://softwarefoundations.cis.upenn.edu/](https://softwarefoundations.cis.upenn.edu/).

A freely available, machine-checked development in Rocq/Coq. Volume 1 covers logic, induction, and proof assistants; Volume 2 covers programming-language semantics and static type systems; the QuickChick volume connects property-based testing with formal specifications. It is the recommended route for readers who want to mechanize the calculus developed here.

### [PLFA]

Philip Wadler, Wen Kokke, and Jeremy G. Siek. *Programming Language Foundations in Agda*. [https://plfa.github.io/](https://plfa.github.io/).

An open textbook in which prose, programs, and proofs are Agda code. It provides an alternative to Software Foundations for learning intrinsically typed syntax, semantics, progress, preservation, and the Curry–Howard correspondence.

### [DaveyPriestley]

B. A. Davey and H. A. Priestley. *Introduction to Lattices and Order*, 2nd edition. Cambridge University Press, 2002. [Publisher page](https://www.cambridge.org/core/books/introduction-to-lattices-and-order/946458CB6638AF86D85BA00F5787F4F4).

A thorough introduction to partially ordered sets, lattices, distributive lattices, Boolean algebras, Galois connections, and fixed points. It supplies the mathematical background for subtype order, type constructors as lattice operations, action-signature product orders, and abstract domains.

### [Cousot1977]

Patrick Cousot and Radhia Cousot. “Abstract Interpretation: A Unified Lattice Model for Static Analysis of Programs by Construction or Approximation of Fixpoints.” In *POPL ’77*, pp. 238–252, 1977. DOI: [10.1145/512950.512973](https://doi.org/10.1145/512950.512973).

The foundational abstract-interpretation paper. PBUI’s bit masks, clause indices, and compiled prefilters can be understood as sound abstractions of concrete semantic membership. The infrastructure should permit false positives at an early filter stage but never false negatives that skip a genuine candidate.

### [PierceBCP]

Benjamin C. Pierce. *Basic Category Theory for Computer Scientists*. MIT Press, 1991.

A compact introduction to categories, functors, natural transformations, adjunctions, and related constructions. Category theory is not required for the core PBUI API, but it helps formalize translation composition and distinguish structure-preserving maps from arbitrary conversions.

## C. Semantic, set-theoretic, gradual, and refinement types

### [Frisch2008]

Alain Frisch, Giuseppe Castagna, and Véronique Benzaken. “Semantic Subtyping: Dealing Set-Theoretically with Function, Union, Intersection, and Negation Types.” *Journal of the ACM* 55, no. 4, Article 19, 2008. DOI: [10.1145/1391289.1391293](https://doi.org/10.1145/1391289.1391293).

The primary technical reference for interpreting types as sets and defining subtyping as inclusion in the presence of Boolean connectives and function types. PBUI adopts the denotational intuition and a restricted algebra over semantic references. It does not implement the paper’s full language or decision procedure.

### [GentleSemantic]

Giuseppe Castagna and Alain Frisch. “A Gentle Introduction to Semantic Subtyping.” In *PPDP ’05*, 2005. DOI: [10.1145/1069774.1069793](https://doi.org/10.1145/1069774.1069793).

A shorter entry point to semantic subtyping. It is recommended before the JACM article for readers who want intuition about union, intersection, negation, and subtyping by set inclusion.

### [CDuce]

Véronique Benzaken, Giuseppe Castagna, and Alain Frisch. “CDuce: An XML-Centric General-Purpose Language.” In *ICFP ’03*, 2003. DOI: [10.1145/944705.944711](https://doi.org/10.1145/944705.944711). Project: [https://www.cduce.org/](https://www.cduce.org/).

CDuce is a mature implementation of semantic subtyping, rich regular types, pattern matching, and XML-oriented programming. It demonstrates that set-theoretic typing can be executable rather than merely notational. PBUI’s universe and effects are different, but CDuce is an important implementation precedent.

### [CastagnaProgramming]

Giuseppe Castagna. “Programming with Union, Intersection, and Negation Types.” 2024 revision. [arXiv:2111.03354](https://arxiv.org/abs/2111.03354).

A modern tutorial and research synthesis on semantic subtyping and programming with Boolean type connectives, including polymorphism. Useful after the introductory chapters for understanding the larger design space.

### [ElixirDesign]

Giuseppe Castagna, Guillaume Duboc, and José Valim. “The Design Principles of the Elixir Type System.” [arXiv:2306.06391](https://arxiv.org/abs/2306.06391), 2023 and subsequent revisions.

Explains the gradual set-theoretic approach chosen for Elixir, including how an existing dynamic language’s guards, patterns, maps, functions, and gradual boundaries influence the design. The work is an unusually relevant modern precedent because it integrates semantic subtyping into an established dynamic ecosystem.

### [ElixirTypes]

Elixir Project. “Gradual Set-Theoretic Types.” Current development documentation. [https://elixir.hexdocs.pm/main/gradual-set-theoretic-types.html](https://elixir.hexdocs.pm/main/gradual-set-theoretic-types.html).

The official implementation-status and user-facing explanation. As of the version documented in this book, the compiler describes types using unions, intersections, and negation and is progressively integrating inference and checking. Because it is version-sensitive, consult the current page rather than relying on a frozen summary.

### [ElixirBDD]

Elixir Project. “Lazier BDDs for Set-Theoretic Types.” 2 December 2025. [https://elixir-lang.org/blog/2025/12/02/lazier-bdds-for-set-theoretic-types/](https://elixir-lang.org/blog/2025/12/02/lazier-bdds-for-set-theoretic-types/).

An implementation report on controlling complexity in a practical set-theoretic type checker using binary decision diagrams and laziness. It motivates Chapter 17’s advice to begin with bitsets and clauses, measure expression growth, and introduce BDD machinery only when warranted.

### [TypedScheme2008]

Sam Tobin-Hochstadt and Matthias Felleisen. “The Design and Implementation of Typed Scheme.” In *POPL ’08*, pp. 395–406, 2008. DOI: [10.1145/1328438.1328486](https://doi.org/10.1145/1328438.1328486). [Author PDF](https://www2.ccs.neu.edu/racket/pubs/popl08-thf.pdf).

Introduces occurrence typing, where predicate tests refine the types of variables along control-flow paths, and reports a mechanically proved core. It is the main precedent for treating successful runtime tests as propositions that justify narrower knowledge.

### [TypedRacketOccurrence]

Typed Racket documentation. “Occurrence Typing.” [https://docs.racket-lang.org/ts-guide/occurrence-typing.html](https://docs.racket-lang.org/ts-guide/occurrence-typing.html).

A practical explanation of how predicates and control flow refine types in Typed Racket. PBUI match evidence is analogous in spirit, although it classifies domain references in an interaction context rather than statically typing every program expression.

### [LiquidTypes2008]

Patrick M. Rondon, Ming Kawaguchi, and Ranjit Jhala. “Liquid Types.” In *PLDI ’08*, 2008. DOI: [10.1145/1375581.1375602](https://doi.org/10.1145/1375581.1375602). [Author PDF](https://goto.ucsd.edu/~rjhala/liquid/liquid_types.pdf).

Combines Hindley–Milner inference with predicate abstraction to infer useful dependent refinements. The paper is relevant to named refinements, decidable predicate languages, and automated reasoning. PBUI deliberately permits opaque runtime predicates as an escape hatch and must therefore expose a larger trusted boundary.

### [LiquidUsability2025]

Catarina Gamboa, Abigail Reese, Alcides Fonseca, and Jonathan Aldrich. “Usability Barriers for Liquid Types.” *Proceedings of the ACM on Programming Languages* 9, PLDI, Article 224, 2025. DOI: [10.1145/3729327](https://doi.org/10.1145/3729327).

An empirical study of barriers faced by developers using liquid types. It is valuable as a warning against assuming that more expressive proof obligations automatically produce a usable developer experience. PBUI’s explanations and profiles should be evaluated as interface features, not only as formal machinery.

### [FStar]

F* Project. *Proof-Oriented Programming in F\\** and online tutorial. [https://fstar-lang.org/tutorial/](https://fstar-lang.org/tutorial/).

A proof-oriented functional language with dependent and refinement types, effects, and automated verification. It is a candidate platform for a mechanized or extracted PBUI matcher whose trusted callbacks are represented as explicit assumptions.

## D. Dispatch, protocols, object systems, and language precedents

### [CLOS]

Sonya E. Keene. *Object-Oriented Programming in Common Lisp: A Programmer’s Guide to CLOS*. Addison-Wesley, 1989.

A clear account of generic functions, methods, multiple dispatch, method combination, and the Common Lisp Object System. It supplies background for CLIM’s object model and for Chapter 14’s separation of action methods from a privileged receiver object.

### [AMOP]

Gregor Kiczales, Jim des Rivières, and Daniel G. Bobrow. *The Art of the Metaobject Protocol*. MIT Press, 1991.

The classic treatment of making an object system’s implementation protocol explicit and extensible. It is relevant to registry freezing, plugin extension, method selection, and reflective debugging. A PBUI registry should expose a controlled protocol, not casually reproduce an unrestricted metaobject system.

### [ClojureMultimethods]

Clojure Project. “Multimethods and Hierarchies.” [https://clojure.org/reference/multimethods](https://clojure.org/reference/multimethods).

Clojure multimethods dispatch on arbitrary values and use an independent ad hoc hierarchy, with explicit preferences for ambiguity. This is one of the closest practical models for action selection over subject, context, gesture, and argument dimensions.

### [ClojureProtocols]

Clojure Project. “Protocols.” [https://clojure.org/reference/protocols](https://clojure.org/reference/protocols). See also [Runtime Polymorphism](https://clojure.org/about/runtime_polymorphism).

Protocols define named sets of operations independently of an inheritance-heavy object model. They motivate PBUI capabilities that return dictionaries of behavior. Clojure protocols dispatch primarily through JVM type machinery; PBUI capabilities may be contextual and proof-relevant.

### [ElixirProtocols]

Elixir Project. “Protocols.” [https://hexdocs.pm/elixir/protocols.html](https://hexdocs.pm/elixir/protocols.html).

Elixir protocols define polymorphic behavior over data types and support consolidation. They are a useful implementation precedent for capability dictionaries and registry freeze, but they do not by themselves model contextual refinements or multi-argument dispatch.

### [JuliaMethods]

Julia Project. “Methods.” *Julia Manual*. [https://docs.julialang.org/en/v1/manual/methods/](https://docs.julialang.org/en/v1/manual/methods/).

Julia’s multiple dispatch chooses methods using all argument types and derives specificity from the type relation. It supports Chapter 14’s product-order account of action signatures. Julia also keeps method dispatch conceptually distinct from conversion and promotion, reinforcing the separation between subtyping and PBUI translators.

## E. JavaScript and TypeScript runtime type systems

### [TypeScriptCompatibility]

Microsoft. “Type Compatibility.” *TypeScript Handbook*. [https://www.typescriptlang.org/docs/handbook/type-compatibility.html](https://www.typescriptlang.org/docs/handbook/type-compatibility.html).

The official explanation of TypeScript’s structural compatibility model. It is crucial for understanding why representation-safe callbacks can be checked statically while semantic subtype declarations still require runtime registry meaning.

### [TypeScriptGoals]

Microsoft. “TypeScript Design Goals.” [https://github.com/microsoft/TypeScript/wiki/TypeScript-Design-Goals](https://github.com/microsoft/TypeScript/wiki/TypeScript-Design-Goals).

Records TypeScript’s goals and non-goals, including structural typing and fully erasable type information rather than a runtime type system. PBUI’s runtime semantic types are therefore intentionally separate from TypeScript annotations.

### [ArkType]

ArkType Project. [https://arktype.io/](https://arktype.io/) and [GitHub repository](https://github.com/arktypeio/arktype).

A TypeScript runtime validator that explicitly uses set-theoretic relationships and exposes runtime introspection such as type extension checks. It is the closest JavaScript precedent for a runtime `TypeExpr` algebra. ArkType validates structural value sets; PBUI additionally needs semantic identity, occurrences, input contexts, translations, and actions.

### [EffectSchema]

Effect Project. “Introduction to Effect Schema.” [https://effect.website/docs/schema/introduction/](https://effect.website/docs/schema/introduction/) or the versioned documentation at [https://effect.website/docs/v3/schema/introduction](https://effect.website/docs/v3/schema/introduction).

Effect Schema describes encoded and decoded forms, validation, transformation, and environmental requirements. It is a strong candidate for validating registry declarations, refinement arguments, and wire formats. Its transformations should not automatically be treated as PBUI semantic translators without identity and applicability contracts.

### [Zod]

Zod Project. [https://zod.dev/](https://zod.dev/).

A widely used TypeScript-first schema validation library. It is appropriate for structural boundaries and serializable refinement arguments. It does not supply semantic subtyping or presentation interaction protocols.

### [TypeBox]

TypeBox Project. [https://github.com/sinclairzx81/typebox](https://github.com/sinclairzx81/typebox).

A JSON-Schema-oriented runtime type builder with TypeScript inference. It is relevant when PBUI type or command declarations must cross a network boundary and remain compatible with standard schema tooling.

## F. Object-centric and data-centric interface systems

### [Portal]

Portal Project. [https://github.com/djblue/portal](https://github.com/djblue/portal).

A Clojure/ClojureScript data inspector with selectable nested values, multiple predicate-driven viewers, commands, and navigation. It is one of the closest contemporary examples of value-oriented presentation and command discovery. Portal is principally an inspector; PBUI targets reusable application interaction protocols.

### [GlamorousToolkit]

Glamorous Toolkit. [https://gtoolkit.com/](https://gtoolkit.com/).

An object-centric programming environment built around contextual views, actions, searches, and explainable tools. Its “moldable development” philosophy strongly supports the idea that domain objects should acquire several purpose-specific presentations rather than one universal inspector.

### [Malli]

Malli Project. [https://github.com/metosin/malli](https://github.com/metosin/malli).

A high-performance, data-driven schema library for Clojure and ClojureScript. Its schemas are ordinary immutable data, registrable, transformable, and inspectable. It is a useful precedent for representing PBUI type expressions as data rather than class instances with hidden behavior.

### [Fulcro]

Tony Kay. *Fulcro Developer’s Guide*. [https://book.fulcrologic.com/](https://book.fulcrologic.com/).

Fulcro normalizes entities using stable idents and lets many components query different projections of the same entity. It is a strong precedent for separating domain entity identity from visual occurrence identity. PBUI subject bindings add a distinct relation: independent views can share one changing selection cell.

### [LivelyNext]

Lively.next Project. [https://lively-next.org/](https://lively-next.org/) and [GitHub](https://github.com/LivelyKernel/lively.next).

A browser-based live programming environment with object inspection, direct manipulation, and runtime modification. It represents the Smalltalk/Morphic line of reflective object environments. Its lessons are primarily about tooling and liveness rather than a set-theoretic presentation-type calculus.

### [ObservableInspector]

Observable. *Inspector* source repository. [https://github.com/observablehq/inspector](https://github.com/observablehq/inspector).

A small, open implementation for rendering arbitrary JavaScript values into reactive DOM output. It is useful for generic rendering and value display, but it does not retain the full semantic type, identity, action, and input-context relations required by PBUI.

### [ProseMirror]

Marijn Haverbeke and contributors. *ProseMirror Guide and Reference*. [https://prosemirror.net/docs/](https://prosemirror.net/docs/).

A mature architecture for schema-constrained document trees, immutable editor state, transactions, commands, plugins, and incremental view updates. It is instructive for explicit state transitions and plugin composition, though its node schema and positional identity are specialized to document editing.

### [Datalog]

Stefano Ceri, Georg Gottlob, and Letizia Tanca. *Logic Programming and Databases*. Springer, 1990; and contemporary Datalog resources such as the Soufflé project at [https://souffle-lang.github.io/](https://souffle-lang.github.io/).

Datalog provides a declarative model of facts, rules, indexed joins, fixed-point evaluation, and, in some systems, provenance. It is a plausible future compilation target for stable subtype, capability, and action-applicability facts. Opaque JavaScript refinements and UI occurrences remain outside ordinary Datalog’s pure relational core.

## G. Identity, accessibility, testing, and formal methods

### [WAIAPG]

W3C Web Accessibility Initiative. *ARIA Authoring Practices Guide*. [https://www.w3.org/WAI/ARIA/apg/](https://www.w3.org/WAI/ARIA/apg/).

Patterns and guidance for keyboard interfaces, composite widgets, focus management, and accessible semantics. Dynamic presentation sensitivity does not exempt PBUI from ordinary accessible interaction design; Chapter 19 treats semantic matching and keyboard navigation as separate responsibilities.

### [QuickCheck2000]

Koen Claessen and John Hughes. “QuickCheck: A Lightweight Tool for Random Testing of Haskell Programs.” In *ICFP ’00*, 2000. DOI: [10.1145/351240.351266](https://doi.org/10.1145/351240.351266).

The foundational paper for property-based testing. Algebraic laws, generated subtype DAGs, translation graphs, and state-machine interaction models are natural QuickCheck-style targets.

### [fast-check]

fast-check Project. [https://fast-check.dev/](https://fast-check.dev/).

A property-based testing framework for TypeScript and JavaScript, including model-based testing facilities. It is the practical recommendation for exercising the laws in Chapter 20 against the production implementation.

### [SpecifyingSystems]

Leslie Lamport. *Specifying Systems: The TLA+ Language and Tools for Hardware and Software Engineers*. Addison-Wesley, 2002. [Official PDF and resources](https://lamport.azurewebsites.net/tla/book.html).

A practical introduction to specifying state machines, invariants, refinement, and temporal properties. The link/unlink/set-subject lifecycle and asynchronous accept-operation ownership are small enough to model in TLA+ and rich enough to benefit from exhaustive state exploration.

### [Quickstrom]

Oskar Wickström and contributors. Quickstrom project and papers. [https://quickstrom.io/](https://quickstrom.io/).

A specification-based testing approach for web applications, using temporal properties to generate and check browser interactions. It is relevant to verifying that visual interaction remains consistent with PBUI’s input-context state machine.

### [PBUI-Source]

The supplied PBUI repository, especially [`src/presentation/`](../../src/presentation/) and the Datalab package under `packages/datalab-ui`.

This is the concrete baseline analyzed in Chapters 3 and 23. Repository claims in the textbook refer to the supplied snapshot, not to every future version or similarly named project.

## Suggested study sequences

### Mathematics-first

1. [DaveyPriestley] for orders, lattices, Boolean algebra, and Galois connections.
2. [TAPL] or [PFPL] for judgments, induction, subtyping, and metatheory.
3. [ProofsAndTypes] for proof terms and Curry–Howard.
4. [GentleSemantic], then [Frisch2008], for set-theoretic types.
5. [TypedScheme2008] and [LiquidTypes2008] for refinements and evidence from predicates.
6. [SoftwareFoundations] or [PLFA] to mechanize a small matcher.

### Interaction-architecture-first

1. [McKay1989] and [McKay1991].
2. [McCLIM] or [LispWorksCLIM], focusing on presentations, input contexts, translators, and command tables.
3. [Portal] and [GlamorousToolkit] for current object-centric interaction examples.
4. [Fulcro] for normalized entity identity.
5. Chapters 15–19 of this book and the companion kernel.

### JavaScript implementation-first

1. [TypeScriptCompatibility] and [TypeScriptGoals].
2. [ArkType], [EffectSchema], [Malli], and [ClojureMultimethods] as focused implementation precedents.
3. [fast-check] for executable laws.
4. [ElixirTypes] and [ElixirBDD] for a modern report on set-theoretic type-system engineering.
5. Return to [Frisch2008] once the implementation questions are concrete.
EOF
wc -w docs/textbook/bibliography.md
```

<details><summary>💭 Thinking</summary>

**Drafted PBUI textbook annotated bibliography with chapter references**

</details>

```unknown
bash -lc set -euo pipefail
cd /mnt/data/pbui_book_work/pbui
cat > docs/textbook/references.bib <<'EOF'
@inproceedings{McKay1989,
  author    = {McKay, Scott and York, William and McMahon, Michael},
  title     = {A Presentation Manager Based on Application Semantics},
  booktitle = {Proceedings of the 2nd Annual ACM SIGGRAPH Symposium on User Interface Software and Technology},
  pages     = {141--148},
  year      = {1989},
  doi       = {10.1145/73660.73678}
}

@article{McKay1991,
  author  = {McKay, Scott},
  title   = {{CLIM}: The Common Lisp Interface Manager},
  journal = {Communications of the ACM},
  volume  = {34},
  number  = {9},
  pages   = {58--59},
  year    = {1991},
  doi     = {10.1145/114669.114675}
}

@manual{CLIM2,
  title        = {Common Lisp Interface Manager (CLIM), Release 2.0 Specification},
  organization = {CLIM consortium},
  year         = {1993},
  url          = {https://archive.decromancer.ca/bitsavers.org/pdf/symbolics/software/genera_8/Common_Lisp_Interface_Manager__CLIM__Release_2.0.pdf}
}

@manual{McCLIM,
  title        = {McCLIM User's Manual},
  organization = {The McCLIM Project},
  url          = {https://mcclim.common-lisp.dev/static/manual/mcclim.html}
}

@book{Pierce2002,
  author    = {Pierce, Benjamin C.},
  title     = {Types and Programming Languages},
  publisher = {MIT Press},
  year      = {2002},
  isbn      = {9780262162098}
}

@book{Harper2016,
  author    = {Harper, Robert},
  title     = {Practical Foundations for Programming Languages},
  edition   = {2},
  publisher = {Cambridge University Press},
  year      = {2016},
  url       = {https://www.cs.cmu.edu/~rwh/pfpl/}
}

@book{Girard1989,
  author     = {Girard, Jean-Yves},
  translator = {Taylor, Paul and Lafont, Yves},
  title      = {Proofs and Types},
  publisher  = {Cambridge University Press},
  year       = {1989},
  url        = {https://www.paultaylor.eu/stable/prot.pdf}
}

@book{DaveyPriestley2002,
  author    = {Davey, B. A. and Priestley, H. A.},
  title     = {Introduction to Lattices and Order},
  edition   = {2},
  publisher = {Cambridge University Press},
  year      = {2002},
  isbn      = {9780521784511}
}

@article{FrischCastagnaBenzaken2008,
  author  = {Frisch, Alain and Castagna, Giuseppe and Benzaken, V{\'e}ronique},
  title   = {Semantic Subtyping: Dealing Set-Theoretically with Function, Union, Intersection, and Negation Types},
  journal = {Journal of the ACM},
  volume  = {55},
  number  = {4},
  pages   = {19:1--19:64},
  year    = {2008},
  doi     = {10.1145/1391289.1391293}
}

@inproceedings{CastagnaFrisch2005,
  author    = {Castagna, Giuseppe and Frisch, Alain},
  title     = {A Gentle Introduction to Semantic Subtyping},
  booktitle = {Proceedings of the 7th ACM SIGPLAN International Conference on Principles and Practice of Declarative Programming},
  year      = {2005},
  doi       = {10.1145/1069774.1069793}
}

@inproceedings{BenzakenCastagnaFrisch2003,
  author    = {Benzaken, V{\'e}ronique and Castagna, Giuseppe and Frisch, Alain},
  title     = {{CDuce}: An XML-Centric General-Purpose Language},
  booktitle = {Proceedings of the Eighth ACM SIGPLAN International Conference on Functional Programming},
  year      = {2003},
  doi       = {10.1145/944705.944711}
}

@misc{CastagnaDubocValim2023,
  author       = {Castagna, Giuseppe and Duboc, Guillaume and Valim, Jos{\'e}},
  title        = {The Design Principles of the Elixir Type System},
  year         = {2023},
  eprint       = {2306.06391},
  archivePrefix= {arXiv},
  url          = {https://arxiv.org/abs/2306.06391}
}

@inproceedings{TobinHochstadtFelleisen2008,
  author    = {Tobin-Hochstadt, Sam and Felleisen, Matthias},
  title     = {The Design and Implementation of Typed Scheme},
  booktitle = {Proceedings of the 35th Annual ACM SIGPLAN-SIGACT Symposium on Principles of Programming Languages},
  pages     = {395--406},
  year      = {2008},
  doi       = {10.1145/1328438.1328486}
}

@inproceedings{RondonKawaguchiJhala2008,
  author    = {Rondon, Patrick M. and Kawaguchi, Ming and Jhala, Ranjit},
  title     = {Liquid Types},
  booktitle = {Proceedings of the 29th ACM SIGPLAN Conference on Programming Language Design and Implementation},
  year      = {2008},
  doi       = {10.1145/1375581.1375602}
}

@inproceedings{CousotCousot1977,
  author    = {Cousot, Patrick and Cousot, Radhia},
  title     = {Abstract Interpretation: A Unified Lattice Model for Static Analysis of Programs by Construction or Approximation of Fixpoints},
  booktitle = {Proceedings of the 4th ACM SIGACT-SIGPLAN Symposium on Principles of Programming Languages},
  pages     = {238--252},
  year      = {1977},
  doi       = {10.1145/512950.512973}
}

@book{Keene1989,
  author    = {Keene, Sonya E.},
  title     = {Object-Oriented Programming in Common Lisp: A Programmer's Guide to CLOS},
  publisher = {Addison-Wesley},
  year      = {1989}
}

@book{Kiczales1991,
  author    = {Kiczales, Gregor and des Rivi{\`e}res, Jim and Bobrow, Daniel G.},
  title     = {The Art of the Metaobject Protocol},
  publisher = {MIT Press},
  year      = {1991}
}

@inproceedings{ClaessenHughes2000,
  author    = {Claessen, Koen and Hughes, John},
  title     = {{QuickCheck}: A Lightweight Tool for Random Testing of Haskell Programs},
  booktitle = {Proceedings of the Fifth ACM SIGPLAN International Conference on Functional Programming},
  year      = {2000},
  doi       = {10.1145/351240.351266}
}

@book{Lamport2002,
  author    = {Lamport, Leslie},
  title     = {Specifying Systems: The TLA+ Language and Tools for Hardware and Software Engineers},
  publisher = {Addison-Wesley},
  year      = {2002},
  url       = {https://lamport.azurewebsites.net/tla/book.html}
}
EOF
python - <<'PY'
from pathlib import Path
p = Path('docs/textbook/README.md')
s = p.read_text()
old = '- [Bibliography and annotated resources](bibliography.md)'
new = old + '\n- [BibTeX database](references.bib)'
if new not in s:
    s = s.replace(old, new)
p.write_text(s)
PY
wc -l docs/textbook/references.bib

```

<details><summary>💭 Thinking</summary>

**Updating Textbook Documentation and References**

</details>

```unknown
bash -lc set -euo pipefail
cd /mnt/data/pbui_book_work/pbui
python - <<'PY'
from pathlib import Path
import re, sys
root=Path('docs/textbook')
files=sorted(root.glob('*.md'))
errors=[]
# bibliography keys
bib=(root/'bibliography.md').read_text()
bib_keys=set(re.findall(r'^### \[([^\]]+)\]$', bib, flags=re.M))
# all bracket citation-like keys beginning upper; avoid normal links
used=set()
for p in files:
    text=p.read_text()
    if text.count('```') % 2:
        errors.append(f'unbalanced fenced blocks: {p}')
    # local links
    for label,target in re.findall(r'\[([^\]]*)\]\(([^)]+)\)', text):
        if target.startswith(('http://','https://','mailto:','#')):
            continue
        pathpart=target.split('#',1)[0]
        if not pathpart:
            continue
        resolved=(p.parent/pathpart).resolve()
        if not resolved.exists():
            errors.append(f'broken local link in {p}: {target}')
    # explicit citation keys, excluding markdown links by looking for [Key] not followed by (
    for m in re.finditer(r'\[([A-Z][A-Za-z0-9-]+)\](?!\()', text):
        used.add(m.group(1))
for key in sorted(used-bib_keys):
    errors.append(f'citation key missing from bibliography: {key}')
# chapters
for n in range(1,25):
    ps=list(root.glob(f'{n:02d}-*.md'))
    if len(ps)!=1:
        errors.append(f'chapter {n}: expected one file, got {ps}')
        continue
    text=ps[0].read_text()
    if f'# Chapter {n}' not in text:
        errors.append(f'chapter title mismatch: {ps[0]}')
    if '## References and further reading' not in text:
        errors.append(f'no references block: {ps[0]}')
    if 'Exercises' not in text:
        errors.append(f'no exercises: {ps[0]}')
# appendices and bib linked from readme
for required in ['appendix-a-api.md','appendix-b-solutions.md','appendix-c-notation.md','bibliography.md','references.bib']:
    if not (root/required).exists(): errors.append(f'missing {required}')
if errors:
    print('\n'.join(errors)); sys.exit(1)
print(f'Markdown graph: OK ({len(files)} Markdown files, {len(bib_keys)} bibliography keys, {len(used)} in-text citation keys)')
print(f'Diamond exercises: {sum(p.read_text().count("◆") for p in files)}')
print(f'Exercise items: {sum(len(re.findall(r"^\d+\. \*\*\[[RCPDX]\]", p.read_text(), flags=re.M)) for p in files)}')
print(f'Theorem/proposition labels: {sum(len(re.findall(r"\*\*(?:Theorem|Lemma|Proposition|Corollary)", p.read_text())) for p in files)}')
PY

rm -rf docs/textbook/code/dist
tsc -p docs/textbook/code/tsconfig.json
node docs/textbook/code/dist/laws.js
node docs/textbook/code/dist/demo.js

```

<details><summary>💭 Thinking</summary>

**Validated textbook references, formatting, notation, and proof assistant tools**

</details>

```unknown
bash -lc set -euo pipefail
cd /mnt/data/pbui_book_work/pbui
cat > docs/textbook/appendix-d-glossary.md <<'EOF'
# Appendix D — Glossary

## Acceptance

The act of supplying a semantic reference to a currently active input context. Acceptance is not the same as executing the final business action. See Chapters 1, 2, 16, and 19.

## Action

A contextually available operation presented to the user, usually represented in PBUI as data that produces a serializable verb. Descriptor-local actions are convenient; action methods selected from subject and context are more compositional. See Chapters 12 and 14.

## Action table

A named scope that contributes commands or actions and may inherit from other scopes. The term comes from CLIM command tables, though PBUI’s proposed facility is deliberately smaller. See Chapters 2 and 14.

## Applicability

The proposition that a presentation, translator, action method, or capability implementation may be used in the current environment and context. Applicability can have a cheap structural phase and a more expensive predicate phase. See Chapters 10, 13, 14, and 17.

## Atom

A named primitive presentation type such as `project`, `field`, or `tile`. Atomic presentation types are registry-owned semantic categories, not JavaScript primitive types. See Chapters 8 and 15.

## Binding

An explicit mutable cell or entity containing a selected semantic subject, such as a document ID. Several distinct views may point to the same binding. See Chapters 18 and 23.

## Boolean type algebra

A type language with operations corresponding to union, intersection, and complement or difference. Under semantic subtyping, these operations are interpreted as set operations. See Chapters 5 and 9.

## Capability

A proposition that a reference supports some semantic role or behavior, such as `Inspectable` or `DocumentBacked`. A marker capability supplies classification only; an operational capability also supplies a dictionary of methods. See Chapter 12.

## Classifier

A trusted registry function or declaration that establishes membership in an atomic type, capability, or refinement. A classifier is part of the trusted boundary unless its behavior is independently verified. See Chapters 6, 10, and 20.

## Coercion

A representation-changing operation sometimes inserted implicitly by a language or framework. This book generally uses the more explicit word **translation** and avoids treating translations as subtype proofs. See Chapter 13.

## Coherence

The property that extension and dispatch do not produce contradictory or ambiguous implementations. Capability dictionaries, action methods, and translation paths all need coherence policies. See Chapters 12–14.

## Command

A named operation, often with typed arguments. CLIM has a command processor and command tables. PBUI ordinarily represents an executable request as a serializable verb and leaves effects to an application boundary. See Chapter 2.

## Completeness

A matcher or subtype prover is complete relative to a language when it can derive every semantically valid result in that language. Concrete runtime matching may be complete even when symbolic subtype reasoning returns `unknown` for opaque refinements. See Chapters 8, 16, and 20.

## Concrete match

A decision about one actual reference under one registry and environment. Concrete membership can often be decided by running predicates even when symbolic subtype inclusion cannot be decided. See Chapter 16.

## Context

Additional semantic input to interaction or dispatch, such as an administrative scope, active command, gesture, current user, or first selected object. Context should not be silently encoded into a subject’s nominal ancestry. See Chapters 10 and 14.

## Denotation

The mathematical meaning of a type expression: the set of references it contains under a registry and environment, written \(\llbracket\tau\rrbracket_{R,E}\). See Chapters 4–6.

## Dependency fingerprint

A stable representation of the object revisions and environmental facts on which a predicate decision or witness depends. Equal fingerprints may justify cache reuse only under an explicit stability contract. See Chapters 10 and 17.

## Dependent sum

A family-indexed sum written \(\sum_{k\in K}V_k\). The PBUI reference universe is a dependent sum because each presentation tag chooses a possibly different JavaScript value carrier. See Chapter 4.

## Direct acceptance

Acceptance without representation-changing translation. It may use exact atomic membership, nominal subtyping, capabilities, Boolean type composition, and refinements. See Chapters 2, 8–12, and 16.

## Dispatch

Selection of behavior from one or more classified arguments. Multiple dispatch considers several dimensions rather than privileging one receiver. See Chapter 14.

## Domain identity

The relation answering whether two references denote the same application entity. It is independent of React keys, screen occurrence, and presentation role. See Chapters 1 and 18.

## Environment

The coherent state snapshot against which contextual predicates, translations, and identity or revision functions are evaluated. It is written \(E\) in formal judgments. See Chapters 6 and 10.

## Evidence

Structured data explaining a successful derivation, such as atomic membership, a union branch, both parts of an intersection, a refinement witness, or a translation path. Evidence is stronger than a bare Boolean but is only as trustworthy as its primitive constructors. See Chapters 7 and 16.

## Expression interning

Reusing one canonical runtime node for semantically or syntactically normalized type expressions. Interning supports fast equality, caches, and compact evidence, but pointer equality is an implementation fact rather than semantic equality. See Chapters 15 and 17.

## Failure evidence

Structured data explaining why matching failed. A failure tree can improve diagnostics but may be expensive or reveal sensitive details. See Chapters 6 and 16.

## Gesture

A named interaction input such as selection, context-menu activation, keyboard command, or drag. CLIM integrates gestures with translator applicability; PBUI can model gesture as a dispatch coordinate. See Chapters 2, 14, and 19.

## Identity preservation

A translator property stating that its source and successful target denote the same semantic object. It is stronger than merely producing a value of the target type. See Chapters 13 and 16.

## Input context

A transient request for a reference satisfying a semantic type expression. Mounted presentations and domain-search results can participate in the same context. See Chapters 1, 2, and 19.

## Intersection type

A type whose denotation contains references belonging to every operand. A witness contains evidence for all required components. See Chapters 5, 7, and 9.

## Invalidation

The act of discarding compiled matchers, caches, or evidence after relevant registry, object, or environment dependencies change. See Chapters 10 and 17.

## Judgment

A formal assertion derived by inference rules, such as \(R;E\vdash r\Downarrow\tau\Rightarrow w\). A judgment defines the relation being implemented and proved. See Chapter 6.

## Lattice

A partially ordered set in which pairs have a meet and join. Semantic types ordered by inclusion form a lattice under intersection and union, with bottom and top. See Chapter 5.

## Match

A successful result containing at least the source reference, accepted reference, evidence, and freshness information. A translated match may have distinct source and target representations. See Chapter 16.

## Match soundness

The theorem that every reference accepted with evidence belongs to the denotation of the requested expression, relative to trusted primitive contracts. See Chapters 6, 16, and 20.

## Method specificity

The partial order used to choose among applicable action implementations. One signature is more specific when each coordinate denotes a subset of the corresponding coordinate in the other. See Chapter 14.

## Nominal subtyping

A declared relation among named semantic types. It is useful for stable domain taxonomies but should not absorb contextual propositions, capabilities, or translations. See Chapter 8.

## Normalization

Rewriting a type expression to a canonical or simpler form while preserving denotation. Typical laws flatten nested unions/intersections, remove identities, deduplicate operands, and apply absorption. See Chapters 9, 15, and 20.

## Occurrence

One mounted or recorded visual manifestation of a semantic reference. Several occurrences can denote the same object, and one occurrence can disappear while the object remains in the domain model. See Chapters 1 and 19.

## Occurrence typing

A static typing technique in which successful predicates refine knowledge about a variable at a program occurrence. PBUI’s runtime match evidence plays an analogous role for semantic references. See Chapter 10.

## Open world

A registry model in which new atoms, capabilities, or methods may be added by modules or plugins. Global negation and method coherence become version-sensitive under open extension. See Chapters 9, 12, and 15.

## Parameterized type

A type constructor applied to semantic arguments, such as `FieldOf(documentId)`. Parameters avoid manufacturing a global atom for every contextual subset. See Chapter 11.

## Partial order

A reflexive, transitive, and antisymmetric relation. Semantic subtyping is a partial order after quotienting expressions by mutual inclusion. Method signatures use a product partial order. See Chapters 5, 8, and 14.

## Predicate refinement

A subset of a base type selected by a predicate, written conceptually as \(\{r\in B\mid p(r,E)\}\). Named refinements can expose dependencies and witnesses; opaque lambdas remain an escape hatch. See Chapter 10.

## Presentation

Rendered output associated with an application object and semantic presentation type. In React, a wrapper can maintain this association for a mounted occurrence. In CLIM, presentations participate in the output-recording and input-context architecture. See Chapters 1, 2, and 19.

## Presentation reference

A discriminated runtime pair of semantic tag and carried value, such as `{ type: "project", value: project }`. The total reference universe is the sum of all such carriers. See Chapters 3 and 4.

## Presentation type

An interface-semantic set of references. It is not identical to a TypeScript structural type or JavaScript runtime class. See Chapters 1, 3, and 8.

## Proof relevance

The property that the particular evidence for a proposition matters computationally. A capability witness may contain a dictionary, and a translated match records the path used. See Chapter 7.

## Provenance

Information about where a witness, declaration, or decision came from: registry module, refinement ID, translator path, dependency set, or remote authority. See Chapters 16, 20, and 24.

## Refinement

See **Predicate refinement**.

## Registry

The runtime authority that names atoms, records subtype and capability relations, stores refinements and translators, assigns stable IDs, and compiles type expressions. A frozen registry has a stable version and validated coherence constraints. See Chapter 15.

## Registry version

A monotonically changing identifier for the declaration snapshot against which expressions and evidence were compiled. It is needed when plugins or late registrations can change subtype closure or complement. See Chapters 9, 15, and 17.

## Representation

The JavaScript value shape carried by a presentation tag. Representation compatibility is not the same as semantic subtyping, though TypeScript can help ensure that direct subtype callbacks are safe. See Chapters 3 and 8.

## Revision

An application-provided version for a semantic object or binding. Revisions help invalidate stale evidence and prevent commitment based on an earlier state. See Chapters 10, 17, and 18.

## Semantic equivalence

Mutual semantic subtyping: \(A<:B\) and \(B<:A\). Equivalent expressions denote the same set even when their syntax differs. See Chapters 5, 8, and 15.

## Semantic identity

See **Domain identity**.

## Semantic subtyping

The definition \(A<:B\) iff \(\llbracket A\rrbracket\subseteq\llbracket B\rrbracket\). It supports set-theoretic reasoning and separates mathematical meaning from a particular inference algorithm. See Chapters 5, 8, and 9.

## Singleton type

A semantic type containing exactly one identity class or value. It can express “the same object as this reference” or a literal semantic value. See Chapter 11.

## Sound approximation

A cheaper classifier that never excludes a genuine match but may admit candidates that a later exact check rejects. Bit masks and source-type indices are examples. See Chapters 5 and 17.

## Structural typing

Compatibility determined by value shape rather than declared name. TypeScript is predominantly structural. PBUI may use structural typing for callback safety while retaining nominal and semantic runtime relations. See Chapters 3 and 8.

## Subject

The semantic object selected or observed by a view, often stored in a role within a binding. A subject is not the same as the logical view that observes it. See Chapters 18 and 23.

## Subtyping

A substitutability or set-inclusion relation. In this book, the unqualified formal relation is semantic inclusion, while nominal declarations and structural checks are mechanisms that may justify particular inclusions. See Chapter 8.

## Top and bottom

`top` denotes the complete reference universe; `bottom` denotes the empty set. `top` is not an “unknown” type: membership in top is definitely true. See Chapters 5 and 9.

## Translation

A partial, possibly effectful mapping from one presented representation to another accepted representation. Translation is distinct from subtyping and may carry cost, authority, identity-preservation, and freshness metadata. See Chapter 13.

## Trusted computing base

The declarations and implementation components whose correctness is assumed by a soundness theorem. In PBUI this includes primitive classifiers, identity functions, refinement callbacks, translators, effect handlers, and the small matcher core unless some are mechanized. See Chapter 20.

## Type expression

An immutable runtime syntax tree denoting a semantic set, constructed from atoms, capabilities, unions, intersections, differences, and refinements. See Chapters 9 and 15.

## Union type

A type whose denotation contains references belonging to at least one operand. Evidence identifies a successful branch or set of branches, depending on policy. See Chapters 5, 7, and 9.

## Verb

Serializable data describing an application operation, interpreted outside the generic presentation package. A verb supports testing, logging, undo, remote transport, and effect separation. See Chapters 2 and 14.

## View identity

The identity of one logical application configuration, such as a chart or pipeline instance. It is separate from placement identity and shared-subject identity. See Chapters 18 and 23.

## Witness

A value that records evidence for a successful proposition or match. See **Evidence**.
EOF

cat > docs/textbook/index.md <<'EOF'
# Subject Index

This index is intentionally conceptual rather than page-based. Links point to the chapter where a topic is introduced or treated most fully.

- **accept / acceptance:** [1](01-objects-and-presentations.md), [2](02-clim.md), [16](16-evidence-matching.md), [19](19-react-integration.md)
- **abstract interpretation:** [5](05-orders-lattices.md), [17](17-performance.md), [22](22-related-systems.md)
- **accessibility:** [19](19-react-integration.md)
- **action methods:** [12](12-capabilities.md), [14](14-multiple-dispatch.md)
- **action tables:** [2](02-clim.md), [14](14-multiple-dispatch.md)
- **ambiguity:** [13](13-translations.md), [14](14-multiple-dispatch.md)
- **ArkType:** [22](22-related-systems.md)
- **atomic presentation types:** [8](08-subtyping.md), [15](15-type-expr-api.md)
- **BDD:** [9](09-set-theoretic-types.md), [17](17-performance.md)
- **bindings:** [18](18-identity-bindings.md), [23](23-datalab-case-study.md)
- **bitsets:** [17](17-performance.md)
- **Boolean algebra:** [5](05-orders-lattices.md), [9](09-set-theoretic-types.md)
- **cache soundness:** [10](10-refinements.md), [17](17-performance.md)
- **capabilities:** [12](12-capabilities.md)
- **category-theoretic view of translators:** [13](13-translations.md)
- **CDuce:** [9](09-set-theoretic-types.md), [22](22-related-systems.md)
- **CLIM:** [2](02-clim.md), [22](22-related-systems.md)
- **Clojure multimethods:** [14](14-multiple-dispatch.md), [22](22-related-systems.md)
- **coercions:** [13](13-translations.md)
- **coherence:** [12](12-capabilities.md), [14](14-multiple-dispatch.md), [24](24-future-directions.md)
- **commands and verbs:** [2](02-clim.md), [14](14-multiple-dispatch.md)
- **completeness:** [8](08-subtyping.md), [16](16-evidence-matching.md), [20](20-testing-and-formal-methods.md)
- **Curry–Howard:** [7](07-curry-howard-evidence.md)
- **Datalab:** [3](03-baseline-pbui.md), [23](23-datalab-case-study.md)
- **decision procedures:** [8](08-subtyping.md), [9](09-set-theoretic-types.md), [17](17-performance.md)
- **denotational semantics:** [4](04-sets-relations.md), [6](06-judgments-proofs.md)
- **dependent sums:** [4](04-sets-relations.md)
- **dependent types:** [11](11-parameterized-types.md), [24](24-future-directions.md)
- **difference types:** [5](05-orders-lattices.md), [9](09-set-theoretic-types.md)
- **dispatch specificity:** [14](14-multiple-dispatch.md)
- **domain identity:** [1](01-objects-and-presentations.md), [18](18-identity-bindings.md)
- **Effect Schema:** [22](22-related-systems.md)
- **Elixir set-theoretic types:** [9](09-set-theoretic-types.md), [22](22-related-systems.md)
- **environment snapshots:** [6](06-judgments-proofs.md), [10](10-refinements.md), [16](16-evidence-matching.md)
- **equivalence relations:** [4](04-sets-relations.md), [8](08-subtyping.md), [18](18-identity-bindings.md)
- **evidence:** [7](07-curry-howard-evidence.md), [16](16-evidence-matching.md)
- **exercises and projects:** every chapter; [selected solutions](appendix-b-solutions.md)
- **failure evidence:** [6](06-judgments-proofs.md), [16](16-evidence-matching.md)
- **formal mechanization:** [20](20-testing-and-formal-methods.md), [24](24-future-directions.md)
- **Fulcro:** [18](18-identity-bindings.md), [22](22-related-systems.md)
- **Glamorous Toolkit:** [22](22-related-systems.md)
- **gradual typing:** [10](10-refinements.md), [22](22-related-systems.md)
- **guards:** [10](10-refinements.md), [22](22-related-systems.md)
- **identity-preserving translation:** [13](13-translations.md), [16](16-evidence-matching.md)
- **incremental redisplay/computation:** [2](02-clim.md), [17](17-performance.md)
- **inference rules:** [6](06-judgments-proofs.md)
- **input contexts:** [1](01-objects-and-presentations.md), [2](02-clim.md), [19](19-react-integration.md)
- **intersections:** [5](05-orders-lattices.md), [7](07-curry-howard-evidence.md), [9](09-set-theoretic-types.md)
- **invalidation:** [10](10-refinements.md), [17](17-performance.md)
- **judgments:** [6](06-judgments-proofs.md)
- **Julia multiple dispatch:** [14](14-multiple-dispatch.md), [22](22-related-systems.md)
- **lattices:** [5](05-orders-lattices.md)
- **linked analytical views:** [18](18-identity-bindings.md), [23](23-datalab-case-study.md)
- **liquid types:** [10](10-refinements.md), [22](22-related-systems.md)
- **matching:** [6](06-judgments-proofs.md), [16](16-evidence-matching.md)
- **McCLIM:** [2](02-clim.md), [22](22-related-systems.md)
- **memoization:** [17](17-performance.md)
- **method combination:** [14](14-multiple-dispatch.md)
- **multiple dispatch:** [14](14-multiple-dispatch.md)
- **negation:** [9](09-set-theoretic-types.md)
- **nominal subtyping:** [8](08-subtyping.md)
- **normalization:** [9](09-set-theoretic-types.md), [15](15-type-expr-api.md), [20](20-testing-and-formal-methods.md)
- **object occurrence:** [1](01-objects-and-presentations.md), [19](19-react-integration.md)
- **occurrence typing:** [10](10-refinements.md)
- **open-world registries:** [9](09-set-theoretic-types.md), [15](15-type-expr-api.md)
- **output recording:** [2](02-clim.md), [19](19-react-integration.md)
- **parameterized types:** [11](11-parameterized-types.md)
- **partial orders:** [5](05-orders-lattices.md), [14](14-multiple-dispatch.md)
- **performance:** [17](17-performance.md)
- **placement identity:** [1](01-objects-and-presentations.md), [18](18-identity-bindings.md)
- **Portal:** [22](22-related-systems.md)
- **predicates:** [4](04-sets-relations.md), [10](10-refinements.md)
- **presentation manager:** [1](01-objects-and-presentations.md), [2](02-clim.md)
- **presentation references:** [3](03-baseline-pbui.md), [4](04-sets-relations.md)
- **presentation translators:** [2](02-clim.md), [13](13-translations.md)
- **proof by induction:** [6](06-judgments-proofs.md), [20](20-testing-and-formal-methods.md)
- **proof relevance:** [7](07-curry-howard-evidence.md)
- **property-based testing:** [20](20-testing-and-formal-methods.md)
- **protocols/type classes:** [12](12-capabilities.md)
- **provenance:** [16](16-evidence-matching.md), [24](24-future-directions.md)
- **React integration:** [19](19-react-integration.md)
- **refinement types:** [10](10-refinements.md)
- **registry:** [15](15-type-expr-api.md)
- **representation safety:** [3](03-baseline-pbui.md), [8](08-subtyping.md)
- **revision/freshness:** [10](10-refinements.md), [16](16-evidence-matching.md), [17](17-performance.md)
- **semantic equivalence:** [5](05-orders-lattices.md), [8](08-subtyping.md)
- **semantic subtyping:** [8](08-subtyping.md), [9](09-set-theoretic-types.md)
- **singleton types:** [11](11-parameterized-types.md)
- **soundness:** [6](06-judgments-proofs.md), [16](16-evidence-matching.md), [20](20-testing-and-formal-methods.md)
- **structural typing:** [3](03-baseline-pbui.md), [8](08-subtyping.md)
- **subject identity:** [18](18-identity-bindings.md)
- **subtyping by emptiness:** [5](05-orders-lattices.md), [9](09-set-theoretic-types.md)
- **testing state machines:** [20](20-testing-and-formal-methods.md)
- **top and bottom:** [5](05-orders-lattices.md), [9](09-set-theoretic-types.md)
- **translation graph:** [13](13-translations.md), [16](16-evidence-matching.md)
- **trusted computing base:** [6](06-judgments-proofs.md), [20](20-testing-and-formal-methods.md), [24](24-future-directions.md)
- **TypeExpr API:** [15](15-type-expr-api.md), [Appendix A](appendix-a-api.md)
- **TypeScript erasure:** [3](03-baseline-pbui.md), [8](08-subtyping.md)
- **unions:** [5](05-orders-lattices.md), [7](07-curry-howard-evidence.md), [9](09-set-theoretic-types.md)
- **view identity:** [18](18-identity-bindings.md), [23](23-datalab-case-study.md)
- **virtualization:** [19](19-react-integration.md)
- **witnesses:** [7](07-curry-howard-evidence.md), [16](16-evidence-matching.md)
EOF

python - <<'PY'
from pathlib import Path
p=Path('docs/textbook/README.md')
s=p.read_text()
old='- [C. Notation and laws](appendix-c-notation.md)\n- [Bibliography and annotated resources](bibliography.md)'
new='- [C. Notation and laws](appendix-c-notation.md)\n- [D. Glossary](appendix-d-glossary.md)\n- [Subject index](index.md)\n- [Bibliography and annotated resources](bibliography.md)'
if old not in s: raise SystemExit('README appendix marker missing')
s=s.replace(old,new)
p.write_text(s)
PY
wc -w docs/textbook/appendix-d-glossary.md docs/textbook/index.md
```

<details><summary>💭 Thinking</summary>

**Added glossary to PBUI textbook**

</details>

```unknown
bash -lc set -euo pipefail
cd /mnt/data/pbui_book_work/pbui
cat > docs/textbook/build-book.py <<'PY'
#!/usr/bin/env python3
"""Validate and build the single-volume Semantic Presentations textbook."""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUTPUT = ROOT / "Semantic-Presentations-Textbook.md"


@dataclass(frozen=True)
class Section:
    path: str
    anchor: str
    toc_label: str
    toc_indent: int = 0


SECTIONS: tuple[Section, ...] = (
    Section("00-front-matter.md", "front-matter", "Front matter"),
    *tuple(
        Section(
            next(ROOT.glob(f"{number:02d}-*.md")).name,
            f"chapter-{number}",
            next(ROOT.glob(f"{number:02d}-*.md")).read_text().splitlines()[0]
            .removeprefix("# ")
            .strip(),
        )
        for number in range(1, 25)
    ),
    Section("appendix-a-api.md", "appendix-a", "Appendix A — Complete proposed API"),
    Section(
        "appendix-b-solutions.md",
        "appendix-b",
        "Appendix B — Selected exercise solutions",
    ),
    Section("appendix-c-notation.md", "appendix-c", "Appendix C — Notation and laws"),
    Section("appendix-d-glossary.md", "appendix-d", "Appendix D — Glossary"),
    Section("index.md", "subject-index", "Subject index"),
    Section("bibliography.md", "bibliography", "Bibliography and annotated resources"),
)

FILE_ANCHORS = {section.path: section.anchor for section in SECTIONS}

LINK_RE = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")
BIB_HEADING_RE = re.compile(r"^### \[([^\]]+)\]$", re.MULTILINE)


def bibliography_keys() -> set[str]:
    return set(BIB_HEADING_RE.findall((ROOT / "bibliography.md").read_text()))


def rewrite_links(text: str) -> str:
    """Rewrite source-edition Markdown links to stable single-volume anchors."""

    bib_keys = bibliography_keys()

    def replace(match: re.Match[str]) -> str:
        label, target = match.groups()
        if target.startswith(("http://", "https://", "mailto:", "#")):
            return match.group(0)

        path, separator, fragment = target.partition("#")
        if path == "bibliography.md" and fragment:
            if fragment not in {key.lower() for key in bib_keys}:
                return match.group(0)
            return f"[{label}](#ref-{fragment})"
        if path in FILE_ANCHORS:
            anchor = FILE_ANCHORS[path]
            return f"[{label}](#{anchor})"
        return match.group(0)

    return LINK_RE.sub(replace, text)


def add_bibliography_anchors(text: str) -> str:
    return BIB_HEADING_RE.sub(
        lambda match: f'<a id="ref-{match.group(1).lower()}"></a>\n\n{match.group(0)}',
        text,
    )


def contents() -> str:
    lines = [
        "<a id=\"contents\"></a>",
        "",
        "# Contents",
        "",
        "## Reading paths",
        "",
        "- **Application engineer:** Chapters 1–3, 8–10, 15–19, 21, and 23.",
        "- **Type-theory path:** Chapters 4–14, 16–17, 20, and 24.",
        "- **CLIM and interaction-design path:** Chapters 1–3, 12–14, 18–19, and 22.",
        "- **Implementer:** Read in order and run the companion kernel in `code/`.",
        "",
        "## Chapters and appendices",
        "",
    ]
    for section in SECTIONS[1:]:
        lines.append(f"- [{section.toc_label}](#{section.anchor})")
    lines.extend(
        [
            "- [BibTeX database](references.bib)",
            "",
            "Exercise labels: **[R]** reasoning, **[C]** coding, **[P]** proof, "
            "**[D]** design, and **[X]** extended project. A **◆** marks an "
            "exercise with a selected solution in Appendix B.",
        ]
    )
    return "\n".join(lines)


def render() -> str:
    pieces: list[str] = []
    for index, section in enumerate(SECTIONS):
        text = (ROOT / section.path).read_text().rstrip()
        text = rewrite_links(text)
        if section.path == "bibliography.md":
            text = add_bibliography_anchors(text)
        pieces.append(f'<a id="{section.anchor}"></a>\n\n{text}')
        if index == 0:
            pieces.append(contents())
    header = (
        "<!-- Generated by docs/textbook/build-book.py. Edit the chapter sources, "
        "not this file. -->\n\n"
    )
    return header + "\n\n---\n\n".join(pieces) + "\n"


def validate() -> list[str]:
    errors: list[str] = []
    source_paths = [ROOT / section.path for section in SECTIONS]
    keys = bibliography_keys()
    key_anchors = {key.lower() for key in keys}

    if len(keys) < 30:
        errors.append(f"bibliography unexpectedly small: {len(keys)} keys")

    for path in source_paths:
        if not path.exists():
            errors.append(f"missing source: {path.name}")
            continue
        text = path.read_text()
        if text.count("```") % 2:
            errors.append(f"unbalanced fenced code blocks: {path.name}")

        for _label, target in LINK_RE.findall(text):
            if target.startswith(("http://", "https://", "mailto:", "#")):
                continue
            local_path, _separator, fragment = target.partition("#")
            if local_path:
                resolved = (path.parent / local_path).resolve()
                if not resolved.exists():
                    errors.append(f"broken local link in {path.name}: {target}")
            if local_path == "bibliography.md" and fragment not in key_anchors:
                errors.append(
                    f"unknown bibliography anchor in {path.name}: {fragment}"
                )

    chapter_paths = [ROOT / section.path for section in SECTIONS[1:25]]
    for number, path in enumerate(chapter_paths, start=1):
        text = path.read_text()
        if not re.search(rf"^# Chapter {number}\b", text, re.MULTILINE):
            errors.append(f"chapter heading mismatch: {path.name}")
        if "Exercises" not in text:
            errors.append(f"chapter has no exercises: {path.name}")
        if "## References and further reading" not in text:
            errors.append(f"chapter has no reading references: {path.name}")

    marked = sum(path.read_text().count("◆") for path in chapter_paths)
    solutions = len(
        re.findall(
            r"^## B\.\d+ Chapter \d+, Exercise \d+",
            (ROOT / "appendix-b-solutions.md").read_text(),
            re.MULTILINE,
        )
    )
    if marked != solutions:
        errors.append(
            f"selected-solution coverage mismatch: {marked} marked, {solutions} solved"
        )

    if not (ROOT / "references.bib").exists():
        errors.append("missing references.bib")
    if not (ROOT / "code" / "semantic-types.ts").exists():
        errors.append("missing executable semantic kernel")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--check",
        action="store_true",
        help="validate and fail if the generated single-volume file is stale",
    )
    args = parser.parse_args()

    errors = validate()
    if errors:
        for error in errors:
            print(f"error: {error}", file=sys.stderr)
        return 1

    generated = render()
    if args.check:
        if not OUTPUT.exists():
            print(f"error: missing generated book: {OUTPUT}", file=sys.stderr)
            return 1
        if OUTPUT.read_text() != generated:
            print(
                "error: generated book is stale; run python3 docs/textbook/build-book.py",
                file=sys.stderr,
            )
            return 1
        print("Textbook sources and generated volume are valid.")
        return 0

    OUTPUT.write_text(generated)
    print(f"Wrote {OUTPUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
PY
chmod +x docs/textbook/build-book.py

cat > docs/textbook/Makefile <<'EOF'
.PHONY: all check code clean

all:
	python3 build-book.py

check:
	python3 build-book.py --check
	rm -rf code/dist
	tsc -p code/tsconfig.json
	node code/dist/laws.js
	node code/dist/demo.js

code:
	rm -rf code/dist
	tsc -p code/tsconfig.json
	node code/dist/laws.js
	node code/dist/demo.js

clean:
	rm -rf code/dist Semantic-Presentations-Textbook.md
EOF

python3 docs/textbook/build-book.py
python3 docs/textbook/build-book.py --check
wc -w docs/textbook/Semantic-Presentations-Textbook.md
head -n 85 docs/textbook/Semantic-Presentations-Textbook.md
```

<details><summary>💭 Thinking</summary>

**Built textbook Markdown, fixed bibliography links, and inspected README appendix**

</details>

```unknown
bash -lc set -euo pipefail
cd /mnt/data/pbui_book_work/pbui
cat > docs/textbook/appendix-e-proof-status.md <<'EOF'
# Appendix E — Proof Status and Mechanization Map

This appendix records the epistemic status of the book’s claims. It is meant to prevent a common failure mode in “formally inspired” software: mathematical notation is presented beside code, and the reader is left to infer that the code has somehow been proved correct.

The companion TypeScript kernel has executable laws and strict type checks. The manuscript contains paper proofs and proof sketches. Neither fact makes the implementation machine-verified. A complete verified system would require a mechanized core and a correspondence argument between that core and the production runtime.

## E.1 Status vocabulary

### Definition

A stipulation that fixes meaning, such as

\[
A<:B\quad\text{iff}\quad
\llbracket A\rrbracket\subseteq\llbracket B\rrbracket.
\]

A definition is not an empirical hypothesis. An implementation may fail to decide it completely or may implement a different relation by mistake.

### Mathematical theorem

A proposition proved from definitions and stated assumptions. A hand proof can be rigorous, but it is still vulnerable to omitted cases and transcription errors.

### Proof sketch

An argument that identifies the induction, cases, or key lemmas without spelling out every formal step. It should be sufficient for a trained reader to complete the proof.

### Executable law

A test asserting that a finite implementation behavior agrees with an algebraic or semantic law over chosen examples or generated cases. Passing tests increase confidence but do not quantify over all possible values unless the tested domain is actually exhaustive.

### Type-level guarantee

A property enforced by TypeScript’s static checker, such as a translator returning the value carrier associated with its declared target tag. TypeScript guarantees concern the checked source program under its own unsound and erasable type system; they do not establish runtime semantic truth.

### Trusted contract

An assumption supplied by application or plugin code. Examples include “this identity function is stable,” “this predicate witnesses ownership,” and “this translator preserves identity.” The infrastructure can preserve such facts compositionally but cannot derive their truth from an arbitrary JavaScript function body.

### Mechanized theorem

A theorem checked by a proof assistant against a formal definition. No theorem in the delivered TypeScript source has this status. Chapter 20 and this appendix describe how to obtain it.

## E.2 Core claim inventory

| Claim | Location | Status in this edition | Executable analogue | Principal assumptions |
|---|---|---|---|---|
| Namespace/key identity is an equivalence relation | Chapters 4, 18; Appendix B | hand proof | identity laws in `laws.ts` | key equality and identity extraction are coherent |
| Union/intersection lattice laws | Chapters 5, 9; Appendix C | set-theoretic proofs or standard laws | normalization and matching laws | fixed reference universe and ordinary set operations |
| `A <: B` iff `A \ B` is empty | Chapters 5, 9; Appendix B | full hand proof | conservative subtype checks | denotational definition of subtype and difference |
| Direct-match soundness | Chapters 6, 16 | structural-induction proof sketch, one full case | match results checked against examples | atom, capability, and refinement constructors are sound |
| Evidence introduction for union/intersection | Chapter 7 | Curry–Howard interpretation and rules | evidence discriminants in the kernel | evidence constructors are controlled |
| Mutual subtyping is an equivalence | Chapter 8; Appendix B | full hand proof | subtype closure laws | subtyping means inclusion |
| Normalization preserves denotation | Chapters 15, 20; Appendix B | rewrite-by-rewrite proof sketch | normalizer laws | each rewrite implements the stated set law |
| Bounded direct matching terminates | Chapters 6, 16 | measure argument | all law runs terminate | finite acyclic expression syntax; refinements themselves terminate |
| Bounded translation search terminates | Chapters 13, 16 | finite-search argument | budget and cycle tests | finite registry, positive/controlled costs, explicit budget |
| Identity-preserving path preserves identity | Chapters 13, 16; Appendix B | induction on path length | path evidence and same-object checks | every edge contract is true; identity is transitive |
| Unique maximal method under total specificity order | Chapter 14 | short full proof | finite maximal-method algorithm can be tested | applicable set is finite and nonempty |
| Sound memoization under dependency stability | Chapter 17; Appendix B | full conditional proof | cached/uncached differential tests | fingerprint equality implies observationally equivalent predicate results |
| Binding sharing is an equivalence relation | Chapter 18 | elementary proof | reducer/model tests | binding IDs have equality |
| Unlink creates future independence | Chapter 18; Appendix B | state-transition proof | reducer/model tests | fresh binding allocation and non-aliasing update semantics |
| Portable round trip preserves sharing classes | Chapter 23 | theorem statement and proof plan | bundle round-trip properties | import/export preserve dense binding equivalence indices |

## E.3 The trusted computing base

For the pure core, the trusted computing base contains at least the following elements.

### The JavaScript runtime

The implementation assumes ordinary behavior for object property access, arrays, maps, strings, numbers used as costs, and function invocation. Host mutation or prototype interference can violate seemingly pure assumptions.

### Registry construction

The registry must:

- assign stable IDs without collision;
- reject malformed or cyclic nominal declarations where required;
- control evidence constructors;
- freeze a coherent declaration snapshot;
- invalidate compiled artifacts when the registry version changes.

A bug in transitive closure or expression normalization can invalidate the infrastructure theorems even when every domain callback is honest.

### Atomic classifiers

For each atom `k`, the runtime classifier must agree with the intended denotation of `atom(k)`. In the simplest discriminated-reference model, the classifier is tag equality plus nominal ancestry. If an atom also performs structural validation, that validator joins the trusted base.

### Refinement predicates

A refinement declaration claims that successful execution establishes a proposition. The infrastructure can record the callback’s ID, arguments, environment version, and witness. It cannot prove that `project.ownerId === userId` corresponds to the business meaning of ownership or that an authorization cache is current.

### Identity and revision functions

Identity extraction must be stable enough to define an equivalence relation. Revision/dependency extraction must change whenever a fact consumed by cached evidence can change. These are application-level proof obligations.

### Translators

A translator’s declaration includes source type, target type, partiality, effects, and possibly identity preservation. The matcher can verify that the returned reference has the declared target tag and can subsequently match it. It cannot prove that the translation did not fabricate the wrong project or that a claimed identity-preserving lookup used the correct key.

### Effect and command boundary

Match evidence is not authorization. A command handler must recheck security-sensitive authority at the authoritative domain boundary. Remote evidence is input provenance, not a capability to mutate protected state.

## E.4 A minimal mechanized calculus

A first mechanization should omit most production features. The objective is a small theorem whose definitions correspond closely to a test oracle.

### Step 1 — Finite tags and references

Define a finite tag type and a dependent carrier family:

```text
Tag : Type
Value : Tag -> Type
Ref := Σ k : Tag, Value k
```

For a first development, use a finite enumerated `Tag` and simple carriers. General plugin extension is a meta-level concern, not part of the core theorem.

### Step 2 — Primitive membership oracle

Represent atomic membership as a relation supplied by the registry:

```text
AtomMember : Registry -> Ref -> AtomId -> Prop
```

State its decidability separately:

```text
atomMemberDec : Decidable (AtomMember R r a)
```

This keeps semantic truth distinct from the decision procedure.

### Step 3 — Type-expression syntax

Define an inductive syntax:

```text
TypeExpr :=
| top
| bottom
| atom AtomId
| union TypeExpr TypeExpr
| inter TypeExpr TypeExpr
| diff TypeExpr TypeExpr
| refine TypeExpr PredicateId Args
```

The first mechanized soundness theorem can omit `diff`, because positive evidence for difference requires negative membership evidence. Add it after the positive fragment is stable.

### Step 4 — Denotation

Define denotation recursively as a proposition on references:

```text
Denotes R E top r := True
Denotes R E bottom r := False
Denotes R E (atom a) r := AtomMember R r a
Denotes R E (union x y) r := Denotes R E x r ∨ Denotes R E y r
Denotes R E (inter x y) r := Denotes R E x r ∧ Denotes R E y r
```

A refinement predicate is represented as a proposition plus a trusted decider. The proof assistant makes the boundary explicit in the types.

### Step 5 — Evidence and matching relation

Define evidence indexed by the expression it proves, or define an unindexed syntax plus a well-formedness relation. The indexed version makes impossible evidence constructors unrepresentable:

```text
Evidence R E r : TypeExpr -> Type
```

For example, intersection evidence contains evidence for both operands.

Then define a computable matcher returning an option or decision:

```text
match : (R E r τ) -> Decidable (Denotes R E τ r)
```

Alternatively, define an inductive matching judgment and later prove an algorithm complete for the supported fragment.

### Step 6 — Soundness and completeness

Prove:

```text
match_sound:
  Match R E r τ w -> Denotes R E τ r
```

For the decidable positive fragment, also prove:

```text
match_complete:
  Denotes R E τ r -> ∃ w, Match R E r τ w
```

The production system may intentionally lose symbolic completeness while retaining concrete matching completeness.

### Step 7 — Normalization

Define a simple normalizer for top, bottom, flattened union, and flattened intersection. Prove denotational preservation before implementing aggressive distributive rewrites. Extraction or a hand translation can then serve as a differential oracle for TypeScript.

## E.5 Adding translations to the mechanization

Translations introduce a second reference and a path relation.

```text
TranslateStep R E : Ref -> TranslatorId -> Ref -> Prop
```

A sound edge declaration requires:

```text
TranslateStep R E r t s -> Denotes R E (targetType t) s
```

An identity-preserving edge additionally requires:

```text
preservesIdentity t -> TranslateStep R E r t s -> SameObject E r s
```

Define the reflexive transitive closure of translation steps, then prove path target soundness and identity preservation by induction on the closure derivation. Search optimality is a different theorem: it concerns the graph algorithm and cost order, not semantic acceptance.

Effects should initially be modeled as an explicit relation, not executed inside the proof assistant. A later F* or monadic development can track failure, state, asynchronous cancellation, and authority.

## E.6 Mechanizing action dispatch

For a finite method registry, define:

- a signature as a vector of type expressions;
- applicability as membership of each actual argument in the corresponding expression;
- specificity as componentwise semantic subtyping;
- maximality in the finite applicable set.

Prove that a finite nonempty total order has one maximal equivalence class. For partial orders, the algorithm should return the entire maximal set. A separate coherence predicate decides whether that set can be combined, preferred, or must be reported as ambiguous.

Open plugin extension complicates the theorem. Freezing the registry before dispatch converts an open-world construction process into a closed finite snapshot on which the proof applies.

## E.7 Model checking linked bindings

The binding subsystem is a state machine rather than a type calculus. It is well suited to TLA+, Alloy, or an exhaustive small-state model.

State variables might include:

```text
views      : ViewId -> BindingId
bindings   : BindingId -> Role -> Subject
nextId     : Nat
```

Actions:

```text
SetSubject(view, role, subject)
Link(sourceView, targetView, resolution)
Unlink(view)
DuplicateIndependent(view)
DuplicatePlacement(view)
```

Invariants:

1. every view refers to an existing binding;
2. unlink allocates a fresh binding and preserves the current role map;
3. independent duplicate does not share a binding;
4. duplicate placement preserves logical view and binding identity;
5. link resolution is atomic with respect to expected revisions;
6. an update affects exactly the views in one binding equivalence class.

A model checker can explore action sequences and produce counterexamples to reducer designs that look locally reasonable.

## E.8 Correspondence with TypeScript

Even a complete proof of the abstract calculus does not automatically verify `semantic-types.ts`. Four integration strategies are available.

### Extraction

Implement the matcher in Rocq, Agda, Lean, or F* and extract/compile it to JavaScript or WebAssembly. This minimizes hand-translation risk but may complicate integration and debugging.

### Generated reference interpreter

Generate a deliberately slow verified interpreter and test the optimized TypeScript implementation against it over generated registries, expressions, references, and environments.

### Refinement mapping

Document a line-by-line correspondence between formal constructors and TypeScript discriminants, then use property tests and mutation testing to find divergence. This is weaker than extraction but often easier to maintain.

### Proof-carrying compilation artifacts

Have the compiler emit a compact certificate for normalized expressions, subtype decisions, or translator paths. A smaller checker validates the certificate at runtime. This shifts trust from a complex optimizer to a small verifier.

## E.9 Recommended first mechanization project

A realistic first project is deliberately narrow:

1. atoms, top, bottom, union, and intersection;
2. finite references and an abstract atom-membership relation;
3. evidence-producing direct matching;
4. direct soundness and completeness;
5. normalization preservation for flattening, identities, absorption, and deduplication;
6. extraction or differential testing against the TypeScript kernel.

Do not begin with asynchronous translators, open-world negation, React, or authorization. Those features are important, but they obscure the foundational correspondence one wants to establish first.

## E.10 Criteria for stronger claims

The project may accurately describe its core as **machine-verified** only when:

- the syntax, denotation, matcher, and relevant theorem are checked by a proof assistant;
- the artifact being executed is extracted from or rigorously connected to that development;
- trusted primitives and effects are enumerated;
- generated code and proof-assistant versions are reproducible;
- the claim identifies the verified fragment rather than implying that the entire React application is proved correct.

Until then, the accurate description is:

> The design is formally specified, supported by hand proofs and executable law tests, with explicit trusted contracts.
EOF

python - <<'PY'
from pathlib import Path
p=Path('docs/textbook/README.md')
s=p.read_text()
old='- [D. Glossary](appendix-d-glossary.md)\n- [Subject index](index.md)'
new='- [D. Glossary](appendix-d-glossary.md)\n- [E. Proof status and mechanization map](appendix-e-proof-status.md)\n- [Subject index](index.md)'
if old not in s: raise SystemExit('README marker missing')
s=s.replace(old,new)
p.write_text(s)

p=Path('docs/textbook/build-book.py')
s=p.read_text()
old='    Section("appendix-d-glossary.md", "appendix-d", "Appendix D — Glossary"),\n    Section("index.md", "subject-index", "Subject index"),'
new='    Section("appendix-d-glossary.md", "appendix-d", "Appendix D — Glossary"),\n    Section(\n        "appendix-e-proof-status.md",\n        "appendix-e",\n        "Appendix E — Proof status and mechanization map",\n    ),\n    Section("index.md", "subject-index", "Subject index"),'
if old not in s: raise SystemExit('builder marker missing')
s=s.replace(old,new)
p.write_text(s)
PY
wc -w docs/textbook/appendix-e-proof-status.md
```

<details><summary>💭 Thinking</summary>

**Finalizing materials**

I’m validating the assembled volume, checking links and executable examples, then I’ll provide the textbook, editable source, companion implementation, and project-integrated archive as finished artifacts.

</details>

```unknown
bash -lc set -euo pipefail
cd /mnt/data/pbui_book_work/pbui
rg -n "LICENSE|License" docs/textbook/00-front-matter.md docs/textbook/Semantic-Presentations-Textbook.md | head -20
sed -n '1,120p' docs/textbook/00-front-matter.md
```

<details><summary>💭 Thinking</summary>

**Updated and validated textbook content, build anchors, licensing, and bibliography links**

</details>

```unknown
bash -lc set -euo pipefail
cd /mnt/data/pbui_book_work/pbui
python3 - <<'PY'
from pathlib import Path
import re
root = Path('docs/textbook')
chapters = sorted(root.glob('[0-9][0-9]-*.md'))
prose_files = chapters + sorted(root.glob('appendix-*.md')) + [root/'bibliography.md', root/'index.md']
words = sum(len(re.findall(r"\b[\w’'-]+\b", p.read_text())) for p in prose_files)
exercises = sum(len(re.findall(r'^### Exercise\b', p.read_text(), flags=re.M)) for p in prose_files)
marked = sum(len(re.findall(r'^### Exercise.*◆', p.read_text(), flags=re.M)) for p in prose_files)
solutions = len(re.findall(r'^## Solution\b', (root/'appendix-b-solutions.md').read_text(), flags=re.M))
bib_entries = len(re.findall(r'^## \[', (root/'bibliography.md').read_text(), flags=re.M))
ts_lines = sum(len(p.read_text().splitlines()) for p in (root/'code').glob('*.ts'))
generated_words = len(re.findall(r"\b[\w’'-]+\b", (root/'Semantic-Presentations-Textbook.md').read_text()))
print({
    'chapters': len(chapters),
    'source_prose_words': words,
    'single_volume_words': generated_words,
    'exercises': exercises,
    'marked_exercises': marked,
    'selected_solutions': solutions,
    'bibliography_entries': bib_entries,
    'typescript_source_lines': ts_lines,
})
PY

du -sh docs/textbook /mnt/data/pbui_book_work/pbui /mnt/data/pbui_book_work/datalab
find docs/textbook -maxdepth 2 -type f | sort | sed -n '1,120p'
```

<details><summary>💭 Thinking</summary>

**Inspected, rebuilt, patched, and packaged textbook source artifacts and statistics**

</details>

# Semantic Interfaces

## Presentation Types, Mathematical Foundations, and Proof-Oriented UI Architecture

The textbook and its complete companion package are finished.

### Primary artifacts

- [Read the complete textbook](sandbox:/mnt/data/Semantic-Interfaces-Textbook.md)
- [Download the complete textbook package](sandbox:/mnt/data/semantic-interfaces-textbook.zip)
- [Formal results and proof-status index](sandbox:/mnt/data/semantic-interfaces-textbook/FORMAL_RESULTS_INDEX.md)
- [Fourteen-week study guide](sandbox:/mnt/data/semantic-interfaces-textbook/STUDY_GUIDE.md)
- [PBUI repository integration map](sandbox:/mnt/data/semantic-interfaces-textbook/PBUI_INTEGRATION_MAP.md)
- [Validation report](sandbox:/mnt/data/semantic-interfaces-textbook/VALIDATION.md)

### Executable companion

- [TypeScript presentation-type kernel](sandbox:/mnt/data/semantic-interfaces-textbook/companion/presentation-type-kernel.ts)
- [Executable law suite](sandbox:/mnt/data/semantic-interfaces-textbook/companion/presentation-type-kernel.test.ts)
- [Companion instructions](sandbox:/mnt/data/semantic-interfaces-textbook/companion/README.md)
- [BibTeX bibliography](sandbox:/mnt/data/semantic-interfaces-textbook/references.bib)

## Scope of the textbook

The book contains:

- **30 chapters**
- **five appendices**
- approximately **40,600 words**
- **187 exercises**
- **41 cited books, papers, specifications, and implementations**
- a dependency-free TypeScript reference implementation
- a strict compiler configuration and executable law suite
- a staged path from a minimal PBUI to a research-oriented semantic interface system

The mathematical material is not confined to a late appendix. It provides the main progression of the book.

## Mathematical progression

The formal development begins with:

- sets and characteristic predicates;
- extensional equality;
- binary relations;
- equivalence relations and quotient sets;
- preorders and partial orders;
- lattices and Boolean operations;
- closure operators;
- partial functions;
- logical judgments and inference rules;
- proof relevance;
- structural induction;
- denotational and operational semantics;
- soundness, completeness, and decidability.

It then defines a presentation-type calculus:

\[
\tau ::= \top
\mid \bot
\mid a
\mid \operatorname{cap}(c)
\mid \tau\lor\tau
\mid \tau\land\tau
\mid \tau\setminus\tau
\mid \operatorname{refine}(p,\theta,\tau).
\]

Types are interpreted as sets of tagged presentation references:

\[
\llbracket\tau\rrbracket^R_e\subseteq\Omega_R,
\]

and semantic subtyping is defined by inclusion:

\[
R,e\models\tau_1\leq\tau_2
\quad\Longleftrightarrow\quad
\llbracket\tau_1\rrbracket^R_e
\subseteq
\llbracket\tau_2\rrbracket^R_e.
\]

This follows the central semantic-subtyping idea that types denote sets and subtyping denotes set inclusion. The book relates the calculus to the established semantic-subtyping literature, including union, intersection, and negation types. citeturn599927search2turn905623view4

## Formal results

The book states and develops, among others:

- semantic-key equality as an equivalence relation;
- ancestor closure as a closure operator;
- the Boolean laws of the type algebra;
- direct-matcher soundness;
- translated-acceptance soundness;
- minimum-cost translator-path selection under explicit assumptions;
- unique-maximal multimethod determinism;
- at-most-once input-context resolution;
- acceptance safety at commitment time;
- linked-subject coherence;
- preservation of visible state under unlinking;
- revision- and dependency-aware cache soundness.

The [formal-results index](sandbox:/mnt/data/semantic-interfaces-textbook/FORMAL_RESULTS_INDEX.md) records the status of each result as one of:

- definition;
- complete paper proof;
- proof sketch;
- executable law;
- registry or host-language assumption;
- proof-assistant mechanization target.

The proofs are conventional mathematical arguments, not machine-checked proofs. Appendix C develops a concrete Lean-, Coq-, Agda-, or Isabelle-oriented mechanization sequence rather than presenting executable tests as proof.

## From CLIM to React

The CLIM chapters introduce:

- presentations;
- presentation types;
- input contexts;
- presentation translators;
- commands and command tables;
- output records;
- application frames;
- parameterized presentation types;
- contextual interaction.

The McCLIM documentation describes the same central dynamic: an input context declares the requested type, applicable presentations become sensitive, and presentation translators can turn gestures on displayed objects into values or commands. citeturn905623view3

The book then separates the CLIM-inspired React architecture into six independent protocols:

1. **Representation** — the JavaScript value being carried.
2. **Semantic type** — the set of requests the reference can satisfy directly.
3. **Identity** — the application object the reference denotes.
4. **Refinement evidence** — propositions currently established about it.
5. **Translation** — ways to obtain another representation or semantic role.
6. **Behavior dispatch** — applicable actions, commands, or renderers.

A seventh relation, **subject binding**, handles coordinated view state without confusing shared selection with object identity or logical-view identity.

## API construction

The implementation chapters build toward APIs such as:

```ts
const Entity = types.atom("entity");

const Project = types.atom("project", {
  identity: project => ({
    namespace: "project",
    key: project.id,
  }),
});

const Inspectable = types.capability("inspectable");
const DocumentBacked = types.capability("document-backed");
const Archived = types.capability("archived");

types.declareSubtype(Project, Entity);
types.implement(Project, Inspectable);
types.implement(Project, DocumentBacked);

const ActiveProject = types.difference(Project, Archived);

const ProjectOwnedBy = types.refinement(
  "project-owned-by",
  Project,
  {
    test(project, ownerId: string) {
      return project.ownerId === ownerId;
    },
  },
);

const MyActiveProject = types.and(
  ActiveProject,
  ProjectOwnedBy(currentUserId),
);
```

Acceptance becomes:

```ts
const result = await pbui.accept({
  type: MyActiveProject,
  prompt: "Choose one of your active projects",
});
```

Actions are developed as multimethods:

```ts
pbui.actions.define({
  id: "archive-project",

  subject: types.and(
    Project,
    types.capability("archivable"),
    types.difference(Project, Archived),
  ),

  context: types.atom("administrative-context"),

  action(match) {
    return {
      id: "archive",
      label: "Archive project",
      verb: {
        type: "archiveProject",
        projectId: match.accepted.value.id,
      },
    };
  },
});
```

Translations remain separate from subtype declarations:

```ts
pbui.translators.define({
  id: "project-id/to-project",
  from: ProjectId,
  to: Project,
  cost: 1,
  preservesIdentity: true,

  translate(reference, environment) {
    return environment.projects.get(reference.value);
  },
});
```

Matching produces evidence rather than only a Boolean:

```ts
interface Match<Reference> {
  readonly source: Reference;
  readonly accepted: Reference;
  readonly requestedType: TypeExpr;
  readonly evidence: MembershipEvidence;
  readonly translationPath: readonly TranslatorStep[];
  readonly validity: ValidityToken;
}
```

## Performance treatment

The implementation chapters cover:

- registry snapshots;
- precomputed nominal transitive closure;
- bitsets for atomic and capability facts;
- expression hash-consing;
- normalized expression DAGs;
- candidate indexing by positive atoms;
- prepared refinement predicates;
- operation-local selector caching;
- semantic-identity and revision cache keys;
- environment dependency fingerprints;
- commit-time revalidation;
- bounded weighted translator search;
- ambiguity diagnostics;
- when clause normalization is sufficient;
- when BDDs might become justified.

The book uses Elixir as a current production precedent for set-theoretic typing. Elixir 1.20, released on June 3, 2026, completed its initial gradual-typing milestone using unions, intersections, and negations; the Elixir team has also documented the practical transition from eager normal forms toward lazier BDD representations. citeturn905623view2

The text does not recommend implementing BDDs initially. It presents a progression from a nominal DAG, through bitsets and normalized clauses, to shared expression graphs, introducing BDDs only when profiling shows expression expansion to be a real problem.

## Existing systems examined

The comparative chapters cover:

- Common Lisp CLIM and McCLIM;
- CDuce and semantic subtyping;
- Elixir’s gradual set-theoretic type work;
- ArkType;
- Typed Racket and occurrence typing;
- Liquid Types and LiquidHaskell;
- Clojure multimethods, protocols, and spec;
- Malli;
- Julia multiple dispatch and conversion;
- Portal;
- Glamorous Toolkit;
- Fulcro;
- Lively.next;
- Observable Inspector.

The comparisons identify which concepts can be borrowed without claiming that any one project implements the entire PBUI model.

## Choosing what to leave out

The final part defines four coherent stopping points.

### Profile A — Nominal presentation system

Includes tagged references, descriptors, exact or nominal subtype matching, direct actions, and an input context.

Leaves out refinements, translations, Boolean type expressions, evidence, and multimethods.

### Profile B — Practical semantic PBUI

Adds semantic identity, revisions, prepared selectors, direct translators, action rules, commit revalidation, and linked subject cells.

This is the recommended first target for the supplied application.

### Profile C — Algebraic PBUI

Adds capabilities, union, intersection, base-relative difference, named refinements, evidence-producing matching, and semantic specificity.

This is the recommended long-term architecture when the application’s semantic vocabulary has stabilized.

### Profile D — Research-oriented system

Adds complete decision procedures for a fixed fragment, BDD or SAT-based representations, recursive types, plugin-theory composition, richer proof objects, and mechanized metatheory.

This profile is explicitly optional.

## Validation

The companion passes:

```text
semantic-interfaces reference kernel: all executable laws passed
```

The final checks also verified:

- strict TypeScript compilation;
- compiled JavaScript syntax;
- archive integrity;
- balanced code and mathematical delimiters;
- the complete chapter and appendix sequence;
- 30 exercise sections containing 187 exercises;
- all 41 bibliography entries cited;
- no unresolved citation keys;
- no unfinished-work markers;
- valid internal table-of-contents anchors.

The archive includes SHA-256 checksums for its contents.


---

> Make a pdf

I’ll typeset the textbook into a polished PDF with bookmarks, equations, code blocks, citations, and a navigable table of contents.

```unknown
bash -lc cat /home/oai/skills/pdfs/SKILL.md && printf '\n--- FILE CHECK ---\n' && ls -lh /mnt/data/Semantic-Interfaces-Textbook.md && wc -l -w -c /mnt/data/Semantic-Interfaces-Textbook.md
```

<details><summary>💭 Thinking</summary>

**Inspected PDF skills, Markdown sources, and generation options**

**Structuring the PDF**

I’m planning a temporary preprocessed Markdown file with metadata, an automatic table of contents, title-page details, and cleaner book-level structure. I’ll avoid duplicating the manual contents and preserve chapter bookmarks.

**Structured the PDF**

</details>

```unknown
bash -lc python - <<'PY'
from pathlib import Path
p=Path('/mnt/data/Semantic-Interfaces-Textbook.md')
for i,line in enumerate(p.read_text().splitlines(),1):
    if line.startswith('# '): print(f'{i}: {line}')
PY
```

<details><summary>💭 Thinking</summary>

**Inspected textbook Markdown, Pandoc templates, fonts, and rendered PDF layout**

</details>

The source has a full five-part structure plus appendices. I’m converting it as a true book rather than a printout: front matter, generated contents, numbered chapters, appendix lettering, running heads, and wrapped source listings.

```unknown
bash -lc set -euo pipefail
WORK=/mnt/data/_semantic_interfaces_pdf
rm -rf "$WORK"
mkdir -p "$WORK"
python - <<'PY'
from pathlib import Path
import re
src = Path('/mnt/data/Semantic-Interfaces-Textbook.md').read_text()
lines = src.splitlines()
out=[]
# Metadata for a book-quality PDF.
out.extend([
'---',
'title: "Semantic Interfaces"',
'subtitle: |',
'  Presentation Types, Mathematical Foundations, and Proof-Oriented UI Architecture',
'',
'  From Common Lisp CLIM to a Set-Theoretic PBUI in TypeScript and React',
'date: "First working edition - August 2026"',
'lang: en-US',
'documentclass: scrbook',
'classoption:',
'  - oneside',
'  - open=any',
'  - headings=normal',
'papersize: letter',
'fontsize: 10pt',
'geometry:',
'  - top=0.85in',
'  - bottom=0.9in',
'  - inner=0.95in',
'  - outer=0.95in',
'mainfont: "Noto Serif"',
'sansfont: "Inter"',
'monofont: "DejaVu Sans Mono"',
'mathfont: "STIX Math"',
'colorlinks: true',
'linkcolor: MidnightBlue',
'urlcolor: Teal',
'citecolor: MidnightBlue',
'toc: true',
'toc-title: "Contents"',
'toc-depth: 2',
'numbersections: true',
'secnumdepth: 3',
'has-frontmatter: true',
'---',
''
])
started=False
skip_contents=False
for line in lines:
    if not started:
        if line.strip() == '## About this book':
            started=True
            out.append('# About this book {.unnumbered}')
        continue
    if line.strip() == '# Contents':
        skip_contents=True
        continue
    if skip_contents:
        if line.startswith('# Part I '):
            skip_contents=False
        else:
            continue
    if line.startswith('# Part '):
        title=line[2:].strip()
        # Escape only characters that can be meaningful in LaTeX headings.
        title=title.replace('&', r'\&').replace('%', r'\%').replace('#', r'\#')
        out.extend(['', rf'\part{{{title}}}', ''])
        continue
    m=re.match(r'^#\s+(\d+)\.\s+(.+)$', line)
    if m:
        out.append('# '+m.group(2))
        continue
    m=re.match(r'^#\s+Appendix\s+([A-E])\s+—\s+(.+)$', line)
    if m:
        if m.group(1)=='A':
            out.extend(['', r'\appendix', ''])
        out.append('# '+m.group(2))
        continue
    out.append(line)
Path('/mnt/data/_semantic_interfaces_pdf/book.md').write_text('\n'.join(out)+'\n')
PY
cat > "$WORK/header.tex" <<'EOF'
% Book typography and navigation.
\usepackage{xurl}
\usepackage{bookmark}
\usepackage{scrlayer-scrpage}
\usepackage{enumitem}
\usepackage{fvextra}
\usepackage{ragged2e}
\usepackage{needspace}

\definecolor{PBInk}{HTML}{172033}
\definecolor{PBAccent}{HTML}{255A78}
\definecolor{PBMuted}{HTML}{5F6B7A}
\definecolor{PBRule}{HTML}{D5DCE5}
\definecolor{shadecolor}{HTML}{F3F6F8}

\KOMAoptions{headsepline=0.35pt}
\clearpairofpagestyles
\ihead{\footnotesize\sffamily\headmark}
\ohead{\footnotesize\sffamily Semantic Interfaces}
\cfoot{\footnotesize\sffamily\pagemark}
\automark[section]{chapter}

\setkomafont{part}{\sffamily\bfseries\color{PBInk}}
\setkomafont{partnumber}{\sffamily\bfseries\color{PBAccent}}
\setkomafont{chapter}{\sffamily\bfseries\color{PBInk}}
\setkomafont{chapterprefix}{\sffamily\bfseries\color{PBAccent}}
\setkomafont{section}{\sffamily\bfseries\color{PBInk}}
\setkomafont{subsection}{\sffamily\bfseries\color{PBInk}}
\setkomafont{subsubsection}{\sffamily\bfseries\color{PBMuted}}
\setkomafont{descriptionlabel}{\sffamily\bfseries\color{PBInk}}

\RedeclareSectionCommand[beforeskip=0pt,afterskip=1.8\baselineskip]{chapter}
\RedeclareSectionCommand[beforeskip=1.8\baselineskip,afterskip=0.55\baselineskip]{section}
\RedeclareSectionCommand[beforeskip=1.35\baselineskip,afterskip=0.4\baselineskip]{subsection}
\RedeclareSectionCommand[beforeskip=1.1\baselineskip,afterskip=0.3\baselineskip]{subsubsection}

\setlist[itemize]{leftmargin=1.55em,itemsep=0.25em,topsep=0.35em}
\setlist[enumerate]{leftmargin=1.8em,itemsep=0.25em,topsep=0.35em}
\setlist[description]{leftmargin=0pt,itemsep=0.35em,topsep=0.4em}
\renewcommand{\arraystretch}{1.14}
\setlength{\emergencystretch}{2.5em}
\clubpenalty=7000
\widowpenalty=7000
\displaywidowpenalty=7000

% Keep code readable, including long TypeScript signatures and URLs.
\RecustomVerbatimEnvironment{Highlighting}{Verbatim}{
  commandchars=\\\{\},
  breaklines=true,
  breakanywhere=true,
  fontsize=\small,
  tabsize=2
}

% A restrained textbook block-quote style.
\renewenvironment{quote}
  {\begin{addmargin}[1.4em]{1.4em}\itshape\color{PBMuted}}
  {\end{addmargin}}

% Avoid orphaned low-level headings.
\pretocmd{\subsection}{\Needspace{4\baselineskip}}{}{}
\pretocmd{\subsubsection}{\Needspace{3\baselineskip}}{}{}

% Custom title page. Pandoc appends the subtitle to \@title.
\makeatletter
\renewcommand{\maketitle}{%
  \begin{titlepage}
    \centering
    \vspace*{0.13\textheight}
    {\sffamily\bfseries\color{PBInk}\fontsize{34}{40}\selectfont\@title\par}
    \vspace{1.8cm}
    {\color{PBAccent}\rule{0.28\textwidth}{1.8pt}\par}
    \vfill
    \begin{minipage}{0.72\textwidth}
      \centering
      {\sffamily\large\color{PBMuted}
       A rendered object should not lose its meaning merely because it has become pixels.\par}
    \end{minipage}
    \vfill
    {\sffamily\large\color{PBInk}\@date\par}
    \vspace*{0.06\textheight}
  \end{titlepage}
}
\makeatother
EOF
cd "$WORK"
pandoc book.md \
  --from=markdown+tex_math_dollars+raw_tex \
  --to=pdf \
  --pdf-engine=xelatex \
  --top-level-division=chapter \
  --highlight-style=tango \
  --include-in-header=header.tex \
  --output=/mnt/data/Semantic-Interfaces-Textbook.pdf \
  --verbose > "$WORK/pandoc.log" 2>&1
ls -lh /mnt/data/Semantic-Interfaces-Textbook.pdf

```

<details><summary>💭 Thinking</summary>

**Compiled and validated a book-quality semantic interfaces textbook PDF**

</details>

```unknown
from PIL import Image, ImageOps, ImageDraw, ImageFont
from pathlib import Path
rend=Path('/mnt/data/_semantic_interfaces_pdf/renders')
groups = [
    [1,2,3,4,5,15,16,17,18],
    [38,39,40,67,68,69,70,95,96],
    [97,98,99,100,124,125,126,127,128],
    [164,165,166,167,168,189,190,191,192],
    [193,209,210,211,212,220,221,222,223]
]
outpaths=[]
for gi, pages in enumerate(groups,1):
    thumbs=[]
    for p in pages:
        img=Image.open(rend/f'page-{p:03d}.png').convert('RGB')
        target_w=330
        h=int(img.height*target_w/img.width)
        img=img.resize((target_w,h))
        canvas=Image.new('RGB',(target_w,h+28
```

<details><summary>💭 Thinking</summary>

**Inspected PDF pages via contact sheets**

</details>

```unknown
bash -lc python - <<'PY'
from PIL import Image, ImageDraw
from pathlib import Path
rend=Path('/mnt/data/_semantic_interfaces_pdf/renders')
groups = [
    [1,2,3,4,5,15,16,17,18],
    [38,39,40,67,68,69,70,95,96],
    [97,98,99,100,124,125,126,127,128],
    [164,165,166,167,168,189,190,191,192],
    [193,209,210,211,212,220,221,222,223]
]
for gi, pages in enumerate(groups,1):
    thumbs=[]
    for p in pages:
        img=Image.open(rend/f'page-{p:03d}.png').convert('RGB')
        target_w=330
        h=int(img.height*target_w/img.width)
        img=img.resize((target_w,h))
        canvas=Image.new('RGB',(target_w,h+28),'white')
        canvas.paste(img,(0,28))
        d=ImageDraw.Draw(canvas)
        d.text((8,6), f'Page {p}', fill='black')
        thumbs.append(canvas)
    cols=3
    rows=(len(thumbs)+cols-1)//cols
    cell_w=max(i.width for i in thumbs)
    cell_h=max(i.height for i in thumbs)
    sheet=Image.new('RGB',(cols*cell_w,rows*cell_h),(220,220,220))
    for idx,img in enumerate(thumbs):
        x=(idx%cols)*cell_w
        y=(idx//cols)*cell_h
        sheet.paste(img,(x,y))
    out=Path(f'/mnt/data/_semantic_interfaces_pdf/contact-{gi}.jpg')
    sheet.save(out,quality=90)
    print(out)
PY
```

<details><summary>💭 Thinking</summary>

**Validated PDF title generation, pagination layout, and final semantic interfaces output**

</details>

[Download the 223-page PDF textbook](sandbox:/mnt/data/Semantic-Interfaces-Textbook.pdf)

It includes a generated table of contents, PDF bookmarks, numbered chapters, lettered appendices, typeset mathematics, wrapped code listings, exercises, and bibliography.

