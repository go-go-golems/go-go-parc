# Branch · Branch · Branch · CLIM UI in React

- URL: https://chatgpt.com/c/6a731f66-9fe4-83ea-bed1-d62e7a6b365a
- Created: 2026-08-05T11:33:04.600Z

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

> I think it's time to take a step back and to reconsider how an API for a presentation based system could be implemented with all the modern research and design patterns that has happened in the last 30 years. 
>
> For example, we could find an API that makes it easy prove properties on it, on its components, using transfinite induction, fix point itereation, linking the colimits back to other categorical constructions that might be relevant
>
> Write a second document studying different possibilities for the architecture of this system that aren't necessarily so close to the common lisp approach / decomposition.

I’ll develop a standalone complementary study comparing mathematically tractable foundations, their proof obligations, and concrete TypeScript APIs that can coexist with the current React system.

```unknown
bash -lc set -euo pipefail
ls -lah /mnt/data
find /mnt/data -maxdepth 2 -type f | sed -n '1,200p'
```

<details><summary>💭 Thinking</summary>

**Assessing the document**

I’m identifying the requested companion document and checking which source materials are actually available. I’ll reconstruct the intended context, then ground the architecture discussion in authoritative technical sources without exposing internal implementation details.

**Assessed the document**

**Structuring the architecture**

I’m organizing the companion document around trace semantics, formal proofs, fixed points, colimits, incremental computation, bidirectional updates, effects, and compositional interfaces. I’ll distinguish genuinely useful transfinite reasoning from unnecessary complexity.

**Structured the architecture**

**Formalizing core semantics**

I’m modeling bindings as monotone rules, effects as command algebras, and runtimes as interpreters. Finite fact spaces usually converge without transfinite steps; colimits can model linking, merging, aliases, and reversible unlinking through retained provenance.

**Formalized core semantics**

**Qualifying fixed points**

I’m treating transfinite induction as a proof technique, not a runtime mechanism. I’ll connect accessible functors, initial algebras, coalgebras, cospans, and incremental calculus while keeping implementation finite and practical.

**Qualified fixed points**

</details>

```unknown
bash -lc set -euo pipefail
rm -rf /mnt/data/pbui_src
mkdir -p /mnt/data/pbui_src
unzip -q /mnt/data/pbui.zip -d /mnt/data/pbui_src
find /mnt/data/pbui_src -maxdepth 3 -type f | sed -n '1,240p'

```

<details><summary>💭 Thinking</summary>

**Inspected data files and archive contents for architecture context**

</details>

```json
{"search_query":[{"q":"Plotkin Pretnar handlers of algebraic effects paper PDF"},{"q":"Interaction Trees representing recursive and impure programs in Coq POPL 2020 PDF"},{"q":"Selective applicative functors paper static analysis effects PDF"},{"q":"algebraic effects handlers modular interpreters user interfaces research paper"}],"response_length":"long"}
```

I’ll also include a migration path from the existing codebase to the proposed architecture.

<details><summary>💭 Thinking</summary>

**Searched 25 websites**

</details>

```unknown
bash -lc set -euo pipefail
cd /mnt/data/pbui_src/pbui
printf '%s\n' '--- top-level ---'
find . -maxdepth 3 -type f | sort | sed -n '1,260p'
printf '%s\n' '--- presentation files ---'
find src/presentation packages/datalab-ui/src/pbui -maxdepth 3 -type f 2>/dev/null | sort
printf '%s\n' '--- current presentation API ---'
for f in src/presentation/types.ts src/presentation/registry.ts src/presentation/selectors.ts src/presentation/createPbui.tsx src/presentation/index.ts; do
  if [ -f "$f" ]; then echo "### $f"; sed -n '1,300p' "$f"; fi
done
```

<details><summary>💭 Thinking</summary>

**Inspected PBUI and Datalab presentation architectures, layout types, and runtime structure**

</details>

```json
{"search_query":[{"q":"site:arxiv.org propagators Radul Sussman revised report pdf"},{"q":"site:groups.csail.mit.edu propagators Radul Sussman pdf"},{"q":"semiring provenance databases Green Karvounarakis Tannen PODS 2007 pdf"},{"q":"Functorial Data Migration Spivak 2012 arxiv Kan extensions"}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Searched 17 websites**

</details>

```json
{"search_query":[{"q":"TLA temporal logic of actions Lamport paper Microsoft Research"},{"q":"Alloy lightweight object modelling notation paper MIT PDF"},{"q":"Incremental lambda calculus change structures paper arxiv"},{"q":"Adapton composable demand-driven incremental computation PLDI paper PDF"}],"response_length":"long"}
```

The emerging recommendation is a layered kernel: inspectable relational fixed points, algebraic interactions, typed composition ports, and lawful synchronization, with opaque callbacks confined to explicit escape hatches.

<details><summary>💭 Thinking</summary>

**Searched 26 websites**

</details>

```unknown
bash -lc cat > /mnt/data/PRESENTATION-SYSTEMS-BEYOND-CLIM.md <<'EOF'
# Beyond CLIM: Architectures for a Proof-Oriented Presentation System

## Reified queries, fixed points, algebraic effects, incremental computation, bidirectional transformations, and categorical wiring

**Status:** architectural study and companion volume  
**Audience:** engineers comfortable with TypeScript and React; no prior category theory or formal-methods background is assumed  
**Scope:** the semantic and runtime architecture of a presentation-based system, not its visual design system

---

## Abstract

A presentation-based interface associates rendered output with domain meaning. The first architecture in this project followed the broad CLIM pattern: presentation types, descriptors, input contexts, translators, actions, and a React provider coordinating them. That model is useful, but it is only one decomposition of the problem, and it inherits assumptions from an interactive Lisp environment whose center of gravity was dynamic dispatch and an imperative command loop.

This document asks a different question:

> What should a presentation-based system look like if its primary design goals include compositional semantics, incremental evaluation, inspectability, serialization, and the ability to state and prove nontrivial properties?

The answer is not “translate CLIM into more category theory.” It is to separate several mathematical structures that CLIM places behind one interaction protocol:

1. **Definitions are inductive syntax.** Queries, rules, component schemas, and effect programs should have a reified core that supports folds, interpreters, and structural induction.
2. **Derived interface knowledge is a fixed point.** Facts such as “this occurrence satisfies the current request” or “this action is applicable” can be defined as the least fixed point of monotone rules, with incremental maintenance and provenance.
3. **Ongoing interaction is coalgebraic.** A session is potentially unbounded behavior: events, effects, cancellation, asynchronous responses, and state transitions. It is better studied using traces, transition systems, coinduction, or interaction trees than as one recursive callback.
4. **Component connection is a wiring problem.** Typed ports and explicit link equations can be composed through coproducts, pushouts, and coequalizers. A colimit describes which interfaces have been identified; it does not, by itself, choose how conflicting values should be reconciled.
5. **Editable views are bidirectional transformations.** Lenses and related optics provide laws for reading and updating focused state. They solve a different problem from linking and should remain a separate layer.
6. **React is an interpreter, not the semantics.** Mounting JSX should register visual occurrences of already-defined semantic objects. It should not determine identity, action applicability, link topology, or workflow meaning.

The recommended architecture is therefore hybrid. It uses a small reified presentation calculus, a pure command/state kernel, an incremental relational runtime, effect handlers for workflows, lawful optics for state focus, and a typed open-component graph for links. Arbitrary JavaScript remains available through an explicit opaque boundary, but the system records exactly which guarantees are lost when that boundary is crossed.

This document studies several alternatives before presenting that recommendation. It also gives a worked chart–pipeline linking model, a proof plan, concrete TypeScript API sketches, and a staged migration path from the current codebase.

---

## 1. The design problem, restated

The current generic PBUI core is concise. Its semantic center is approximately:

```ts
interface PresentationReference<Values> {
  type: keyof Values;
  value: Values[keyof Values];
}

interface AcceptRequest<Values> {
  types: keyof Values | readonly (keyof Values)[];
  prompt: string;
  filter?: (reference: PresentationReference<Values>) => boolean;
}
```

A registry maps type names to labels, descriptions, tones, and actions. A provider tracks a pending acceptance request. A `Presentation` component asks whether its reference can satisfy that request and changes its pointer behavior accordingly. Product code supplies conversions and serializable verbs.

This is a reasonable first architecture. It offers a clean improvement over scattering click handlers throughout components. Its limitations arise when the interface becomes a substrate rather than a feature.

### 1.1 The callback ceiling

An arbitrary callback is maximally expressive:

```ts
filter: (reference) => arbitraryJavaScript(reference, ambientState)
```

It is also semantically opaque. From the outside, the runtime generally cannot determine:

- which state the callback reads;
- whether it is pure;
- whether equal domain objects receive equal answers;
- whether it is monotone as information grows;
- whether it is stable for the duration of an input operation;
- whether it can be serialized or sent to a worker;
- whether two callbacks are equivalent;
- how to index candidates before invoking it;
- how to update its result after a small state change;
- why it returned `true`;
- what theorem would justify replacing it with an optimized plan.

Memoization can hide some cost, but it cannot recover the missing semantics. TypeScript can ensure that a callback receives a value of the expected shape; it cannot prove arbitrary extensional properties of the callback.

This yields the first architectural principle:

> **Proof and optimization require reification. Host-language functions should be an escape hatch, not the only semantic representation.**

### 1.2 The registry ceiling

A mutable or centrally assembled registry is easy to understand, but it makes several relations look like object properties:

```text
presentation type -> descriptor -> actions
```

Many facts are actually contextual relations:

```text
(context, subject)                 -> acceptable?
(context, subject, capability)     -> action
(source sort, target sort, state)  -> translation
(component port, component port)   -> link
(command, state)                   -> next state and effects
```

Once these relations become recursive, derived, plugin-defined, or incrementally maintained, a descriptor map is no longer the most natural semantic center.

### 1.3 The component ceiling

A React component is a poor unit for proving domain properties. It mixes:

- semantic input;
- rendering;
- event wiring;
- accessibility behavior;
- local UI state;
- scheduling assumptions;
- effects;
- mounting lifetime.

A component test can establish useful behavioral facts, but it is not a stable mathematical object. Reconciliation, concurrent rendering, virtualization, and unmounting are implementation concerns that should not define domain identity or logical availability.

The more durable unit is an **open semantic component**: a typed interface, local state, transition semantics, derived observations, and a rendering interpretation.

### 1.4 What “proof-oriented” should mean

A proof-oriented API does not mean every application author writes theorem-prover scripts. It means the architecture exposes enough structure that different assurance levels are possible.

At minimum, the system should support executable laws and property-based tests. For critical structural protocols, it should admit bounded model checking. For the small semantic core, it should be possible to give a mechanized model in Lean, Coq, or Agda and relate that model to the TypeScript implementation.

The target properties fall into several classes:

| Class | Example |
|---|---|
| Algebraic law | semantic identity is reflexive, symmetric, and transitive |
| Structural invariant | each placement refers to an existing logical view |
| Fixed-point property | every derived action is justified by a rule whose premises hold |
| Incremental correctness | updating a result with a delta equals full recomputation |
| Bidirectional law | reading after writing yields the written focused value |
| Link coherence | all ports in one equality component observe one resolved value |
| Safety property | an unavailable capability never produces an executable privileged command |
| Liveness property | a pending selection eventually resolves, aborts, or remains explicitly blocked on an external event |
| Refinement property | the React adapter produces only traces allowed by the semantic kernel |

The architecture should make these statements natural rather than retrofitted.

### 1.5 Non-goals

This study does not propose:

- running transfinite ordinal loops in a browser;
- replacing every function with a category-theory abstraction;
- proving the DOM or React implementation from first principles;
- making UI action visibility a security boundary;
- requiring application authors to understand all the mathematics in this chapter;
- treating one universal abstraction as the solution to syntax, state, time, linking, and rendering.

The central discipline is the opposite: assign each concern to the weakest structure that adequately explains it.

---

# Part I — Mathematical tools with engineering consequences

## 2. Categories: a minimal working vocabulary

A **category** consists of objects and composable arrows. Every object has an identity arrow, and composition is associative. The terminology is abstract because the same laws appear in many settings:

- sets and functions;
- types and pure functions;
- schemas and schema mappings;
- state spaces and lawful transformations;
- interfaces and open components;
- contexts and restriction maps.

The practical value of category theory is not that arrows are more elegant than functions. It is that **universal properties specify constructions by how they compose with everything else**. This often gives exactly the modularity law an architecture needs.

A **functor** maps objects and arrows from one category to another while preserving identities and composition. An interpreter for a well-designed syntax is often functorial: interpreting a composed definition should equal composing the interpretations.

A **natural transformation** relates two functors coherently. In engineering language, it says that a conversion commutes with every supported structural operation rather than working only for hand-picked examples.

An **adjunction** relates a free construction to a forgetful one. Free syntax and its interpreters, free effect programs and handlers, and several data-migration operations obtain their laws from adjunctions.

The categorical vocabulary becomes useful only when it yields a concrete obligation. For example:

```text
interpret(compose(a, b)) = compose(interpret(a), interpret(b))
```

is an implementable law. Merely calling a registry a category is not.

## 3. Inductive definitions and initial algebras

Suppose a query language has constructors:

```ts
type Query<A> =
  | { tag: "all"; sort: Sort<A> }
  | { tag: "filter"; source: Query<A>; predicate: Predicate<A> }
  | { tag: "union"; left: Query<A>; right: Query<A> }
  | { tag: "join"; /* ... */ };
```

This syntax is inductive: every finite query is built by finitely many constructor applications. Categorically, such a datatype is commonly described as an **initial algebra** for a shape functor `F`. Informally, `F(X)` describes one layer of syntax whose recursive positions contain `X`; the complete syntax `μF` is a fixed point satisfying `F(μF) ≅ μF`.

Initiality gives two major benefits.

First, it gives a unique fold into any algebra that explains the constructors:

```text
fold : (F A -> A) -> (μF -> A)
```

An evaluator, pretty-printer, dependency analyzer, optimizer, serializer, monotonicity checker, and SQL compiler can all be folds over the same syntax.

Second, it gives structural induction. To prove a property for every query, prove it for each constructor assuming it holds for recursive children.

This is a better basis for proof than a callback because the finite syntax exposes the cases.

### 3.1 The extension problem

A closed algebraic datatype makes new interpreters easy and new syntax constructors invasive. A final or tagless-final encoding reverses part of that tradeoff. Modular sums of signatures, “data types à la carte,” plugin modules, and generated discriminated unions are different ways to manage the extension problem.

The important point is not to choose one encoding universally. It is to identify which language fragments must be serializable and inspectable. Those fragments benefit from an initial representation.

### 3.2 Transfinite initial-algebra chains

Some initial algebras can be constructed by repeatedly applying a functor beginning at an initial object:

```text
0 -> F 0 -> F² 0 -> F³ 0 -> ...
```

At a limit ordinal, the preceding chain is joined by a colimit. Under suitable preservation conditions, the process stabilizes at an initial algebra. Adámek’s construction may require transfinite stages for sufficiently general functors. Pitts and Steenkamp provide a constructive inflationary account, while Wißmann and Milius give a newer constructive construction based on a colimit of finite recursive coalgebras rather than an ordinal-indexed chain [Pitts & Steenkamp 2021; Wißmann & Milius 2024].

For an ordinary finite TypeScript AST built from finitary constructors, this metatheory does **not** imply a transfinite runtime. Structural recursion remains finite. The transfinite construction is relevant when proving existence at a general categorical level or reasoning about extensible infinitary signatures.

## 4. Least fixed points on lattices

A different fixed point appears when facts derive more facts.

Let `L` be a complete lattice of possible knowledge states, ordered by information content. A monotone operator `T : L -> L` derives one round of consequences. The intended semantics is often the least fixed point:

```text
μT = least X such that T(X) = X
```

For a fact system, `L` can be a powerset. Bottom is the empty fact set, order is inclusion, and join is union.

```text
X₀     = ∅
X₁     = T(X₀)
X₂     = T(X₁)
...
```

The Knaster–Tarski theorem gives existence of fixed points for monotone endofunctions on complete lattices. Abstract interpretation turns this style of fixed-point semantics and approximation into a general method for program analysis [Tarski 1955; Cousot & Cousot 1977]. Datalog and lattice-oriented languages such as Flix and Datafun make least fixed points a programming model rather than only a metatheory [Madsen, Yee & Lhoták 2016; Arntzenius & Krishnaswami 2016].

### 4.1 Presentation facts as a fixed point

A presentation runtime can use base facts such as:

```text
Presents(occurrence, subject, sort)
Wants(context, targetSort)
HasCapability(context, capability)
Translates(sourceSort, targetSort, translator)
Linked(portA, portB)
```

Rules derive:

```text
Candidate(context, occurrence, subject)
Acceptable(context, occurrence, acceptedSubject)
AvailableAction(context, subject, action)
BindingMember(binding, port)
```

Recursive translators, subtype closure, inherited action scopes, link connectivity, and rule-defined affordances are naturally fixed-point computations.

### 4.2 Finite, omega, and transfinite convergence

Three cases must be distinguished.

**Finite-height case.** If only finitely many facts can exist, monotone iteration reaches a fixed point in finitely many strict growth steps. This is the normal browser implementation target.

**Omega-continuous case.** If `T` preserves suprema of increasing countable chains, the least fixed point is reached at the join of the finite stages:

```text
μT = ⋁_{n < ω} Tⁿ(⊥)
```

**General monotone case.** A monotone operator may require transfinite iteration. Define approximants:

```text
X₀       = ⊥
X_{α+1}  = T(X_α)
X_λ      = ⋁_{β < λ} X_β       when λ is a limit ordinal
```

At some closure ordinal the chain stabilizes under ordinary set-sized assumptions.

The practical conclusion is strict:

> Use transfinite induction in the metatheory where it is justified. Engineer the production fact universe so each stratum has finite or otherwise tractable convergence.

### 4.3 A reusable transfinite proof pattern

Suppose an invariant `P(X)` should hold for every approximation and therefore for the least fixed point. A transfinite induction proof has three obligations:

1. **Base:** `P(⊥)`.
2. **Successor:** `P(X)` implies `P(T(X))`.
3. **Limit:** if `P(X_β)` holds for every `β < λ`, then `P(⋁_{β<λ} X_β)`.

For example, `P(X)` might state that every `AvailableAction` fact in `X` carries a provenance expression whose base leaves are valid capabilities and subject facts. The successor case checks each rule. The limit case observes that every fact in the union appeared at an earlier stage.

This style is useful even when the runtime terminates after twelve worklist steps. The ordinal formulation proves that the result does not depend on that implementation accident.

## 5. Coalgebras, traces, and coinduction

Inductive syntax describes finite definitions. Interactive behavior can continue indefinitely. A user may generate an unbounded sequence of events; a live data source may never finish; a workflow may recursively wait for input.

A coalgebra describes how a state can be observed or unfolded into one step of behavior. Final coalgebras support coinductive definitions and proofs. Two systems are often compared by **bisimulation**: each can match the other’s observable steps while preserving the relation.

Interaction Trees are a concrete proof-engineering example. They represent recursive impure programs as coinductive trees of uninterpreted events and continuations, support compositional interpreters built from event handlers, and come with an equational theory based on weak bisimulation [Xia et al. 2020].

For PBUI-like workflows, this suggests representing:

```text
select a document
then request confirmation
then dispatch a command
then wait for persistence
then report success or failure
```

as an effectful behavior interpreted by different handlers rather than as nested React callbacks.

## 6. Limits and colimits

A **diagram** is a shaped collection of objects and arrows. A **limit** is a universal way of observing a diagram consistently. A **colimit** is a universal way of assembling or identifying it.

Several familiar constructions are special cases.

| Construction | Engineering reading |
|---|---|
| Product | combine independent state with projections |
| Coproduct | combine alternatives or plugin signatures with case analysis |
| Equalizer | states on which two computations agree |
| Coequalizer | quotient by equations or aliases |
| Pullback | compatible pairs sharing a common image |
| Pushout | glue two systems along a common interface |
| General colimit | assemble a network while imposing its wiring identifications |

### 6.1 Links as a coequalizer

Let `P` be the set of ports and `E` the set of equality-link edges. Each edge has two endpoints:

```text
source, target : E -> P
```

The quotient of ports by the equivalence relation generated by those edges is the coequalizer:

```text
E ⇉ P -> P/~
```

In a finite implementation, `P/~` is computed by connected components or union–find. Each equivalence class is a logical binding group.

The universal property says that any function out of ports that treats linked endpoints equally factors uniquely through the quotient. This is exactly the coherence expected of a consumer that observes logical bindings rather than raw ports.

### 6.2 Pushouts and open composition

When two components expose a common interface, gluing them along that interface is a pushout. Cospans represent open systems with inputs and outputs; composing cospans uses pushouts. Decorated and structured cospans add internal system structure while retaining a principled composition law [Fong 2015; Baez & Courser 2020].

For UI architecture, a component can expose typed ports rather than DOM elements:

```text
Document input       Selection output
        \             /
          Chart core
        /             \
Filter command       Highlight input
```

Composition connects compatible interfaces. The same algebra can describe a chart, pipeline, inspector, or plugin without making any one component aware of all others.

### 6.3 What a colimit does not do

Suppose a chart port currently stores document `α` and a pipeline port stores `β`. Adding an equality link identifies the ports topologically. It does not decide whether the resulting value is `α`, `β`, an error, a conflict object, or a join.

Value reconciliation requires another algebra:

- reject unequal values;
- choose source or target by an explicit policy;
- use a last-writer-wins order;
- merge in a join-semilattice;
- retain a multi-value conflict;
- ask the user.

Conflating topology with value resolution produces categorical language without categorical correctness.

### 6.4 Unlinking is not an inverse colimit

A quotient forgets which sequence of edges generated an equivalence class. Destructive union–find is excellent for additions but does not make arbitrary deletion cheap or semantically unambiguous.

A linkable UI should retain the original diagram:

```ts
interface LinkEquation {
  id: LinkId;
  left: PortId;
  right: PortId;
  policy: ReconciliationPolicy;
}
```

The quotient is derived state. Removing one equation recomputes affected components or uses a dynamic-connectivity data structure. This preserves provenance and makes unlink behavior specifiable.

## 7. Lenses, optics, and bidirectional laws

A lens separates reading a view from updating through that view. In a common formulation:

```text
get : Source -> View
put : Source × View -> Source
```

Well-behaved lenses satisfy laws such as:

```text
GetPut:  put(s, get(s)) = s
PutGet:  get(put(s, v)) = v
PutPut:  put(put(s, v1), v2) = put(s, v2)
```

Foster and collaborators developed a combinator language for total, well-behaved bidirectional tree transformations [Foster et al. 2007]. Modern optics generalize composable access and update patterns, and profunctor representations provide a modular categorical account [Clarke et al. 2024].

Lenses are useful for:

- focusing a component on one part of application state;
- editing a projection while preserving hidden context;
- connecting a generic port to a nested store location;
- proving that a view update is reflected back coherently.

They are not a complete linking architecture. A lens relates one source and one view with an update policy. A link network can have many peers, cycles, conflicting writers, and topology changes. Use optics at the boundary between a port and state; use a link algebra for network composition.

## 8. Algebraic effects and handlers

An effect signature names operations without fixing their implementation:

```ts
type UiEffect<A> =
  | SelectEffect<A>
  | ReadCellEffect<A>
  | DispatchEffect<A>
  | ConfirmEffect<A>
  | FetchEffect<A>;
```

A free program built from these operations can be interpreted by handlers. Plotkin and Pretnar describe algebraic effects through equational theories; the free model induces the computation structure, and a handler supplies a model and corresponding homomorphism [Plotkin & Pretnar 2013].

This gives a strong architecture for workflows:

- production handler: DOM, network, persistence;
- test handler: deterministic scripted responses;
- logging handler: trace every operation;
- replay handler: reproduce a session;
- model-checking handler: explore alternatives;
- authorization handler: reject effects lacking authoritative capability.

Some UI constructs are scoped or higher-order: “run this computation under an input context,” “race these requests,” or “rollback this transaction.” These are not always ordinary first-order algebraic operations. They may require scoped or higher-order effect encodings, or a coinductive representation such as interaction trees.

## 9. Incremental computation

A presentation runtime repeatedly evaluates almost the same semantic questions over slightly changed state. Several research traditions offer different strategies.

**Dependency-graph approaches** record which computations read which inputs and invalidate affected nodes. Adapton combines demand-driven observation with a demanded computation graph so work is recomputed only when requested [Hammer et al. 2014].

**Program differentiation approaches** derive an update program from a base program. The incremental lambda calculus treats changes as first-class structure and generates derivatives satisfying a correctness equation [Cai et al. 2014; Giarrusso et al. 2019].

**Differential dataflow approaches** represent evolving collections as differences indexed by logical time and can maintain nested iterative computations under general updates [McSherry et al. 2013].

These techniques become available only when computation structure or dependencies are visible. An arbitrary closure can participate, but only as an opaque node with conservative invalidation.

---

# Part II — Architectural families

## 10. Family A: a pure state-transition kernel

### 10.1 Core idea

Represent the application as a deterministic transition function:

```ts
type Step<S, C, E> =
  (state: S, command: C) => Result<{
    state: S;
    effects: readonly E[];
  }, DomainError>;
```

The UI emits commands. The kernel validates and evolves state. Effects are data interpreted outside the kernel.

This is the architecture behind reducers, event-sourced aggregates, Elm-style update functions, and many state-machine systems. It is much less CLIM-like: the primary abstraction is not a presentation or input context but a transition system.

### 10.2 What it makes easy

The kernel is deterministic and replayable. Properties can be proved by induction over command traces. Safety and liveness can be modeled in temporal logic. Link operations become explicit commands rather than side effects hidden in components.

```ts
type Command =
  | { type: "StartSelection"; context: ContextSpec }
  | { type: "CommitSelection"; occurrence: OccurrenceId }
  | { type: "LinkPorts"; left: PortId; right: PortId; policy: Policy }
  | { type: "SetPort"; port: PortId; value: unknown }
  | { type: "Unlink"; link: LinkId };
```

Representative invariants are straightforward:

```text
all link endpoints exist
all occurrences refer to existing subjects
at most one modal input context owns a given interaction channel
commands never mutate state when their precondition fails
```

TLA+ is well suited to exploring temporal protocols, while Alloy is useful for bounded structural analysis. Alloy’s small relational kernel was explicitly designed to express structural constraints and support automatic semantic analysis [Lamport 1994; Jackson 2002].

### 10.3 What it does not solve

A reducer does not by itself provide:

- a query language;
- incremental derivation of applicable actions;
- a composition law for plugins;
- a mathematical account of rendering;
- structured interactive workflows;
- bidirectional focus into nested state.

The transition kernel is an excellent foundation but an incomplete presentation architecture.

### 10.4 Best use

Use this family as the authoritative operational core. Do not ask it to be the only authoring API.

## 11. Family B: a deeply embedded algebraic DSL

### 11.1 Core idea

Represent presentation-system definitions as data.

```ts
type Expr<A> =
  | All<A>
  | Where<A>
  | Join<A, B>
  | Translate<A, B>
  | Union<A>
  | Not<A>
  | Fix<A>
  | Opaque<A>;
```

A definition is an AST. Multiple interpreters give it meaning.

### 11.2 Interpreters

The same term can support:

```text
evaluate        -> current result
compile         -> indexed execution plan
incrementalize  -> delta plan
dependencies    -> state paths read
serialize       -> portable representation
prettyPrint     -> documentation
explain         -> provenance tree
abstractEval    -> conservative static properties
verify          -> proof obligations or certificates
```

This is the architecture with the clearest structural-induction story. The AST is an initial algebra; each interpreter is a fold or related recursion scheme.

### 11.3 API shape

```ts
const selectableProject = Query.from(Project)
  .where(Project.archived.eq(false))
  .where(Project.owner.eq(Context.currentUser))
  .map(Project.identity);
```

The syntax can be ergonomic if combinators are carefully designed. Type parameters can track the result type, dependencies, monotonicity class, effect class, or serializability.

```ts
type Query<
  A,
  Deps extends DependencySet,
  Mono extends Monotonicity,
  Portable extends boolean,
> = /* hidden AST */;
```

### 11.4 Proof story

One can prove, by structural induction:

- evaluator type soundness;
- dependency analysis soundness;
- optimizer preservation;
- compilation correctness;
- monotonicity of the certified fragment;
- serialization round trips;
- incremental derivative correctness constructor by constructor.

### 11.5 Costs

A deep embedding imposes a language boundary. Every desired operation must be represented in the AST. General higher-order host-language functions are difficult to inspect and serialize. Extending the syntax can require updating all interpreters.

A modular signature architecture can reduce that burden, but not erase it. There must remain a policy for unknown extension nodes.

### 11.6 Best use

Use a deep embedding for the **portable, optimizable, explainable core**: queries, rule premises, identities, dependencies, and effect programs whose structure matters.

## 12. Family C: tagless-final and algebra-parameterized APIs

### 12.1 Core idea

Instead of constructing an AST, write a definition polymorphic over an interpreter algebra.

```ts
interface QueryAlg<R> {
  all<A>(sort: Sort<A>): R;
  where<A>(source: R, predicate: Predicate<A>): R;
  union<A>(left: R, right: R): R;
}

type QueryProgram = <R>(alg: QueryAlg<R>) => R;
```

The definition cannot inspect `R`; it can only use the operations supplied by the algebra. Different algebras evaluate, print, optimize, or analyze it. Finally-tagless encodings use the host type system to preserve object-language typing across multiple interpretations [Carette, Kiselyov & Shan 2009].

### 12.2 Advantages

- new interpreters can be added without changing a central AST type;
- host-language typing often makes ill-typed terms unrepresentable;
- modular algebras can express extensions cleanly;
- interpretation can avoid repeated AST tagging and pattern matching;
- partial evaluation and staged compilation can be natural.

### 12.3 Disadvantages

- generic syntax inspection is less direct;
- serialization requires a dedicated reification interpreter and is not possible for every host-language term;
- sharing and source locations need explicit treatment;
- plugin compatibility across process or language boundaries is harder;
- proofs often reason about parametricity and algebra laws rather than a simple inductive datatype.

### 12.4 Best use

Tagless-final style is attractive for an internal TypeScript authoring layer when most consumers stay in one process. It is less attractive as the only persistent public interchange format.

A practical compromise is **final authoring, initial normalization**: authors use algebraic combinators, then a trusted interpreter reifies the supported fragment into a canonical plan.

## 13. Family D: algebraic effects and interaction trees

### 13.1 Core idea

Treat interaction as a program over an effect signature rather than as component-local callbacks.

```ts
const linkDocumentSelectors = Ui.gen(function* () {
  const source = yield* Ui.select(tileWithDocument);
  const target = yield* Ui.select(tileWithDocument.excluding(source));
  const policy = yield* Ui.choose(linkPolicies(source, target));
  yield* Ui.dispatch({
    type: "LinkPorts",
    left: source.documentPort,
    right: target.documentPort,
    policy,
  });
});
```

The syntax may be a free monad, freer structure, generator-backed instruction tree, or coinductive interaction tree.

### 13.2 Proof and tooling benefits

- handlers are explicit semantic boundaries;
- workflows can be replayed and simulated;
- effects can be reordered only when laws permit;
- a test interpreter can avoid DOM interaction;
- cancellation and failure become part of the program’s semantics;
- coinductive representations support nontermination and asynchronous streams;
- equivalence can be stated by trace equivalence or bisimulation.

### 13.3 Applicative, selective, or monadic?

A fully monadic workflow can choose future effects from previous values. That flexibility makes static dependency discovery difficult.

An applicative workflow declares all effects statically but cannot express value-dependent branching. Selective applicative functors occupy an intermediate point: effects remain statically discoverable while limited dynamic branching is allowed [Mokhov et al. 2019].

This distinction is useful for presentation systems:

- menu construction and prefetch plans often fit an applicative or selective fragment;
- open-ended input loops and asynchronous retries need monadic or coinductive power;
- the API can expose both and report which analyses remain available.

### 13.4 Costs

Effects solve interaction sequencing, not the entire semantic model. A free program can also become large, and TypeScript ergonomics around higher-kinded abstractions are imperfect. Scoped operations require care.

### 13.5 Best use

Use effect programs for cross-component workflows, command acquisition, asynchronous operations, and testable orchestration. Keep domain state transitions in the pure kernel.

## 14. Family E: a relational or Datalog-style fixed-point engine

### 14.1 Core idea

Represent semantic state as base relations and derive interface behavior through rules.

```text
Acceptable(ctx, occ, subject) :-
    Presents(occ, subject, sort),
    Wants(ctx, target),
    Compatible(sort, target),
    Satisfies(ctx.selector, subject).

AvailableAction(ctx, subject, action) :-
    HasCapability(ctx, cap),
    ActionRule(rule, subjectSort, cap, action),
    HasSort(subject, subjectSort),
    RulePredicate(rule, ctx, subject).
```

The program’s meaning is the least fixed point of its immediate-consequence operator.

### 14.2 Why this is compelling

Presentation systems are relation-heavy. The same domain object can have many occurrences; one occurrence can satisfy many contexts; actions depend on joins between subjects, capabilities, context, and state; links require transitive closure.

A relational runtime provides:

- declarative rules;
- indexes and joins;
- recursive closure;
- explanation through derivation trees;
- incremental view maintenance;
- a direct path to worker or server execution;
- a clean separation between base and derived state.

Datafun demonstrates that monotonicity can be tracked by a type discipline in a higher-order functional setting, while Flix extends Datalog-style least fixed points to lattices and monotone functions [Arntzenius & Krishnaswami 2016; Madsen, Yee & Lhoták 2016].

### 14.3 Provenance

A Boolean result says an action is available. A provenance expression says why.

Semiring provenance annotates query results so addition represents alternative derivations and multiplication represents joint use of premises. Green, Karvounarakis, and Tannen show a common semiring framework for several forms of relational annotation and extend it to Datalog with fixed points [Green, Karvounarakis & Tannen 2007].

For a UI, a simplified explanation might be:

```text
archive-project available because
  (subject-is-project)
  × (current-user-has-admin-capability)
  × (project-is-not-archived)
```

This is useful for debugging, disabled-action explanations, and audit logs. It is not an authorization proof unless the authoritative command handler validates the same premises.

### 14.4 The monotonicity boundary

Positive facts and recursive reachability are monotone. Retraction, negation, “only if no other candidate exists,” and priority-based choice are not straightforwardly monotone.

Options include:

- stratified negation;
- explicit epochs or transactions;
- support counts and differential maintenance;
- recomputation of a nonmonotone stratum;
- representing uncertainty or conflicts in a richer lattice;
- keeping authoritative nonmonotone decisions in the command kernel.

An API that accepts arbitrary lambdas and labels them “monotone” without evidence has not solved this problem.

### 14.5 Best use

Use a rule engine for applicability, subtype and translation closure, inherited action scopes, link connectivity, and other derived semantic facts. Keep ordering, visual layout, and effect sequencing in separate structures.

## 15. Family F: reactive and incremental dataflow

### 15.1 Core idea

Treat values as nodes in a dependency graph. Changes propagate to dependent computations.

```ts
const activeDocument = cell<DocumentId | null>(null);
const chartRows = computed(() => evaluatePipeline(activeDocument.get()));
const selectableFields = computed(() => schema(chartRows.get()));
```

Functional reactive programming gives time-varying values and events a compositional interface [Elliott & Hudak 1997; Elliott 2009]. Modern incremental systems add explicit change propagation, memoization, demand, or differential collections.

### 15.2 Strengths

- natural model for live UIs;
- fine-grained recomputation;
- direct subscription API for React;
- links can initially look like shared cells;
- derived labels, action counts, and acceptability update automatically;
- change propagation can be measured and optimized.

### 15.3 Recursive dataflow

Cycles require a semantics. Possibilities include:

- reject instantaneous cycles;
- require a delay, giving a causal stream network;
- interpret monotone cycles by least fixed point;
- interpret constraints by propagation to quiescence;
- use logical timestamps and iterative dataflow.

Differential dataflow is especially relevant when recursive queries must be updated after insertions and deletions. It maintains differences across partially ordered logical times and supports nested iteration [McSherry et al. 2013].

### 15.4 Risks

A generic signal graph can hide domain semantics just as thoroughly as callbacks. “This node depends on those nodes” is not the same as “this rule is monotone,” “this action is authorized,” or “this link is a lawful bidirectional relation.”

Glitches, cycles, disposal, dynamic dependencies, and identity reuse require precise runtime semantics. A dataflow graph should be compiled from a semantic plan where possible, not treated as the source language by default.

### 15.5 Best use

Use dataflow as an execution strategy and subscription layer. Do not make it the sole public meaning of a presentation system.

## 16. Family G: lenses, optics, and bidirectional view architecture

### 16.1 Core idea

Every displayed or editable view is derived from a source through a lawful bidirectional transformation.

```ts
const primaryDocument: Lens<AppView, DocumentId | null> = lens({
  get: view => view.documents.primary ?? null,
  put: (view, doc) => ({
    ...view,
    documents: doc
      ? { ...view.documents, primary: doc }
      : omit(view.documents, "primary"),
  }),
});
```

A chart and pipeline can each expose an optic to their document selector. Generic infrastructure reads and writes through those optics.

### 16.2 Strengths

- compositional focus into nested state;
- explicit update policy;
- algebraic laws suitable for property testing and proof;
- separation of view-specific representation from source state;
- good ergonomics for forms and editors;
- can support schema migration and reversible projections.

### 16.3 Limits

The classical lens laws assume a source/view relationship, not an arbitrary peer network. Two views may discard different information. Concurrent writes may conflict. Some transformations are partial, asymmetric, or require complements.

There are richer variants—partial lenses, symmetric lenses, relational lenses, delta lenses—but no single optic makes distributed synchronization trivial.

### 16.4 Best use

Use optics to connect semantic ports to component or store state and to specify editable projections. Combine them with explicit link topology and conflict policy.

## 17. Family H: open components and structured cospans

### 17.1 Core idea

A component is an open system with typed boundary ports and an internal implementation. Composition is wiring.

```ts
const Chart = component({
  name: "Chart",
  ports: {
    document: port(DocumentId, "read-write"),
    selection: port(RowSet, "output"),
    filter: port(FilterExpr, "input"),
  },
  state: ChartState,
  transition: chartStep,
  observe: chartObservations,
});
```

The component boundary is semantic. React rendering is one decoration or interpretation of the component.

### 17.2 Composition

Independent components combine by a coproduct-like operation. Connecting compatible ports adds identifications. A structured cospan can represent a component from an input interface to an output interface; pushout composition glues the shared boundary.

This provides a strong answer to plugin composition:

- a plugin declares its boundary;
- the host need not know its internals;
- composition is associative up to isomorphism;
- diagrams can be serialized;
- wiring can be visualized and analyzed;
- the same component can run under different renderers or effect handlers.

### 17.3 Proof story

Local component invariants can be paired with assume/guarantee contracts on ports. Composition theorems can state that compatible local guarantees imply a global invariant. The pushout or cospan laws justify reassociation of wiring without changing observable behavior.

### 17.4 Costs

Structured cospans describe composition elegantly but do not automatically provide:

- an efficient browser runtime;
- conflict resolution;
- workflow sequencing;
- query planning;
- rendering semantics.

The categorical layer must compile to ordinary graph and state machinery.

### 17.5 Best use

Use open components as the architectural unit for tiles, plugins, and cross-view binding. Treat structured cospans as the composition model, not as the everyday application-author syntax.

## 18. Family I: context-indexed semantics, presheaves, and fibrations

### 18.1 Core idea

Presentation meaning is always relative to a context:

```text
current user
current workspace
active capabilities
pending interaction
loaded data
selected stage
network authority
```

Rather than store one global registry that accepts a context argument, make context dependence part of the semantic structure.

Let contexts and refinements form a category `C`. A presheaf assigns data to each context with restriction maps along context morphisms. An indexed category or fibration assigns a category of valid subjects, actions, or proofs to each context and supports reindexing.

### 18.2 Engineering interpretation

```ts
interface Indexed<Context, A> {
  at(context: Context): A;
  restrict(from: Context, to: Context, proof: Refines<to, from>): A;
}
```

A capability-narrowing context should not invent actions. A workspace restriction should transport subjects and identities coherently. A naturality law states that interpreting and then restricting agrees with restricting and then interpreting.

### 18.3 Sheaf-style gluing

If multiple local contexts overlap, a sheaf condition asks whether compatible local data glue to a unique global value. This can model local-to-global consistency for collaborative or plugin-defined state.

Failure of unique gluing is also informative. It can expose a genuine conflict rather than forcing a last-writer-wins answer.

### 18.4 Strengths

- context is explicit in the semantics;
- reindexing laws constrain capability and scope changes;
- local plugin definitions can compose through restriction;
- dependent and proof-relevant relations fit naturally;
- the Grothendieck construction can assemble indexed fibers into one total category.

### 18.5 Costs

This is the most abstract option. A full presheaf or fibration API would be difficult for ordinary React authors and easy to misuse as decorative terminology. It is best kept in the formal model or library internals unless the application genuinely has rich context transport.

### 18.6 Best use

Use context indexing to design laws for capability narrowing, workspace scoping, and plugin reindexing. Do not expose categorical machinery directly unless it earns its complexity.

---
EOF
```

<details><summary>💭 Thinking</summary>

**Documented alternative architectures and checked document length**

</details>

```unknown
bash -lc cat >> /mnt/data/PRESENTATION-SYSTEMS-BEYOND-CLIM.md <<'EOF'
# Part III — Comparison and synthesis

## 19. Comparison matrix

No architecture dominates every axis. The following ratings are qualitative; they indicate the default shape of each family rather than a hard limit.

| Family | Reified semantics | Structural proof | Recursive derivation | Incremental execution | Workflow semantics | Linking/composition | Serialization | Host-language ergonomics |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Pure transition kernel | medium | trace induction | low | medium | medium | medium | high | high |
| Deep embedded DSL | high | high | medium | high after compilation | medium | medium | high | medium |
| Tagless-final API | medium–high | algebra/parametricity | medium | medium–high | medium | medium | low–medium | high |
| Algebraic effects / ITrees | high for operations | algebraic/coinductive | low | medium | very high | medium | high for initial encodings | medium |
| Relational fixed-point engine | high | fixed-point induction | very high | very high | low | medium | high | medium |
| Reactive dataflow | medium | graph/causality laws | high with explicit semantics | very high | medium | medium | medium | high |
| Lenses / optics | high for focus/update | equational laws | low | high | low | low–medium | medium | high |
| Structured cospans / open systems | high for boundaries | compositional laws | medium | implementation-dependent | low | very high | high | low–medium |
| Context-indexed semantics | very high | naturality/fibration laws | medium | implementation-dependent | medium | high | medium | low |

A few conclusions follow.

1. **The transition kernel should be authoritative but not authoring-complete.** It is the best place for state and command invariants.
2. **A reified query/rule core is the strongest route to explanation and incrementalization.** The callback-only model should not remain the semantic center.
3. **Effects and fixed points solve orthogonal problems.** Effects sequence requests and commands; fixed points derive stable knowledge.
4. **Lenses and colimits solve orthogonal problems.** Lenses focus and update state; colimits assemble and identify interfaces.
5. **Open components are the right unit of composition.** React components are one rendering of them.
6. **The public API should be stratified.** A certified/reified core can coexist with an opaque host-language boundary, but the guarantee downgrade must be visible.

## 20. A recommended hybrid: the Open Presentation Calculus

The term **Open Presentation Calculus** is used here as a design label, not as a claim that a complete formal calculus has already been constructed. The architecture has six semantic layers and one adapter layer.

```text
┌───────────────────────────────────────────────────────────────┐
│ React / DOM adapter                                           │
│ occurrences, accessibility, pointer and keyboard events      │
├───────────────────────────────────────────────────────────────┤
│ Interaction programs                                         │
│ select, confirm, dispatch, fetch, cancel; effect handlers     │
├───────────────────────────────────────────────────────────────┤
│ Incremental semantic runtime                                  │
│ queries, rules, provenance, least fixed points, subscriptions │
├───────────────────────────────────────────────────────────────┤
│ Open component and binding graph                              │
│ typed ports, link equations, colimit-derived binding groups   │
├───────────────────────────────────────────────────────────────┤
│ Pure command/state kernel                                     │
│ validation, transactions, authoritative state transitions     │
├───────────────────────────────────────────────────────────────┤
│ Semantic schema                                               │
│ sorts, identity, relations, codecs, changes, capabilities     │
└───────────────────────────────────────────────────────────────┘
```

The layers are deliberately not a single inheritance hierarchy. Each has its own laws and proof technique.

## 21. Layer 1: semantic schema

### 21.1 Sorts rather than presentation-type strings

A semantic sort is a named interface-level type with an explicit carrier, identity, codec, and change structure.

```ts
interface Sort<A, Key> {
  readonly name: string;
  readonly codec: Codec<A>;
  readonly identity: Identity<A, Key>;
  readonly change?: ChangeStructure<A>;
}

interface Identity<A, Key> {
  key(value: A): Key;
  equalsKey(left: Key, right: Key): boolean;
  encodeKey(key: Key): string;
}
```

Example:

```ts
const Document = sort<Document, DocumentId>({
  name: "Document",
  codec: documentCodec,
  identity: byKey(document => document.id),
});

const Field = sort<FieldRef, readonly [DocumentId | null, string]>({
  name: "Field",
  codec: fieldRefCodec,
  identity: byKey(field => [field.docId, field.name] as const),
});
```

The sort is not a renderer. It is not a descriptor. It is a semantic declaration shared by queries, ports, commands, persistence, and occurrences.

### 21.2 Identity as a setoid or groupoid boundary

At the simplest level, identity is an equivalence relation. The laws are:

```text
reflexive:  a ~ a
symmetric:  a ~ b  =>  b ~ a
transitive: a ~ b and b ~ c  =>  a ~ c
```

A canonical key makes these laws easy to implement, provided key extraction is stable and collision-free within its domain.

More complex systems may have multiple representations of one entity. Instead of forcing all equality through one key, a **groupoid-like** model can retain explicit invertible evidence that two representations denote the same object. In practice:

```ts
interface SameEntity<A, B> {
  readonly left: EntityRef<A>;
  readonly right: EntityRef<B>;
  readonly witnessKind: string;
}
```

The runtime can normalize this evidence to an identity class. The formal model can treat representations and equivalence witnesses as a groupoid. The public application API should still expose simple keys for the common case.

### 21.3 Subtyping and translation are not the same relation

A subtype relation should mean that a value can safely be used as the supertype representation. It forms a preorder or thin category when reflexive and transitive.

A translation changes representation or meaning. Total canonical translations can form ordinary arrows; partial translations can be modeled in the Kleisli category of `Option`; nondeterministic translations can be relations.

```ts
interface Translator<A, B> {
  readonly id: string;
  readonly from: Sort<A, unknown>;
  readonly to: Sort<B, unknown>;
  readonly cost: number;
  run(value: A, context: EvalContext): Option<B>;
  preservesIdentity?: IdentityPreservationWitness<A, B>;
}
```

A conversion graph with nonnegative costs can be understood as a category enriched over the tropical or Lawvere cost structure: path costs compose by addition, and alternatives are compared by minimum. That interpretation gives useful laws:

```text
cost(identity) = 0
cost(g ∘ f) = cost(f) + cost(g)
best path = minimum available total cost
```

It also exposes a coherence obligation. If two minimum-cost paths produce observably different target values, shortest-path selection is not a semantic proof. The system must choose a canonical path, retain the chosen path as evidence, or require a confluence property.

### 21.4 Relations and attributes

Schema attributes should be reified when they participate in queries or updates.

```ts
const ProjectArchived = attribute(Project, "archived", Bool, {
  get: project => project.archived,
});

const ProjectOwner = relation(Project, User, "owner", {
  get: project => project.ownerId,
});
```

This is not an object-relational mapper requirement. It is a way to give the query compiler stable names for dependencies and indexes.

### 21.5 Changes

Incremental execution needs more than equality. A change structure specifies how a value is updated and what a delta means.

```ts
interface ChangeStructure<A, Delta = unknown> {
  empty: Delta;
  apply(base: A, delta: Delta): A;
  compose(first: Delta, second: Delta): Delta;
  difference?(oldValue: A, newValue: A): Delta;
}
```

For sets, a delta may contain insertions and removals. For maps, it may contain key-local changes. For scalar document selection, it may simply be replacement. This layer lets a query compiler choose between invalidation, recomputation, and true differential maintenance.

### 21.6 Capabilities

Capabilities should be semantic values issued by an authoritative boundary, not booleans invented by rendering code.

```ts
const ArchiveProject = capability("ArchiveProject", Project);
```

The interface may derive that an action is visible from a capability fact. The command handler must still consume or validate authoritative evidence.

## 22. Layer 2: a typed query calculus

### 22.1 Queries denote collections, not callbacks

A query has a denotation relative to a database or semantic world:

```text
⟦q⟧_Γ ⊆ Carrier(A)
```

where `Γ` is the evaluation context.

A TypeScript façade might look like:

```ts
const activeOwnedProject = Query.from(Project)
  .where(ProjectArchived.eq(false))
  .where(ProjectOwner.eq(Context.currentUser))
  .distinctBy(Project.identity);
```

The internal representation is normalized syntax, not a closure chain.

### 22.2 Core constructors

A useful first-order fragment includes:

```text
source / singleton / literal
map / flatMap with restricted relational meaning
filter by reified predicate
join / semijoin / antijoin
union / intersection
distinct / group / aggregate
exists / forall in a bounded relation
translation
transitive closure or fix
stratified negation
parameter read
```

Do not begin with every SQL feature. Begin with the constructors required by presentation applicability and action rules.

### 22.3 Predicate syntax

```ts
const selectableField = Query.from(Occurrence)
  .where(Occurrence.sort.eq(Field))
  .join(Occurrence.subject, Field)
  .where(Field.docId.eq(Context.activeDocument))
  .where(Field.kind.in(["integer", "number"]))
  .select(Occurrence.id, Field.identity);
```

The compiler can inspect the predicate tree, extract dependencies, choose an index by sort and document, and produce an explanation plan.

### 22.4 Phantom classifications

The public type can track useful static classifications:

```ts
type Monotonicity = "monotone" | "stratified" | "nonmonotone" | "unknown";
type Portability = "portable" | "local";
type Purity = "pure" | "effectful";

type Query<A, D, M extends Monotonicity, P extends Portability> = {
  readonly _result?: A;
  readonly _dependencies?: D;
  readonly _monotonicity?: M;
  readonly _portability?: P;
};
```

These phantom parameters do not prove the classifications. They prevent accidental composition after a trusted compiler or constructor has assigned them.

### 22.5 Compile products

Compilation should return more than an evaluator:

```ts
interface CompiledQuery<A> {
  readonly plan: QueryPlan;
  readonly dependencies: DependencySet;
  readonly monotonicity: Monotonicity;
  readonly portability: Portability;
  evaluate(snapshot: Snapshot): readonly A[];
  subscribe(runtime: Runtime, sink: DeltaSink<A>): Subscription;
  explain(value: A): Explanation | null;
}
```

A compiler correctness theorem states:

```text
execute(compile(q), Γ) = ⟦q⟧_Γ
```

An incremental correctness theorem states, in change-action notation:

```text
evaluate(q, apply(Γ, δΓ))
  = apply(evaluate(q, Γ), derivative(q, Γ, δΓ))
```

### 22.6 The opaque constructor

Arbitrary JavaScript is still necessary. It should be explicit and information-bearing.

```ts
const domainSpecific = Query.opaque({
  name: "domain-specific-project-policy",
  input: Project,
  reads: [ProjectArchived, ProjectOwner, Context.currentUser],
  purity: "claimed-pure",
  monotonicity: "unknown",
  identityStable: true,
  estimateCost: "small",
  evaluate(project, context) {
    return legacyPolicy(project, context);
  },
});
```

The runtime treats claims as optimization contracts, not proofs. Development mode can attempt to falsify them with property tests or dependency instrumentation. A certified token should be issued only by a trusted checker or verified module.

The compiler’s report should be explicit:

```text
Query: active-owned-project
Portable: no — contains opaque JS node domain-specific-project-policy
Incremental plan: conservative invalidation on ProjectArchived,
                  ProjectOwner, Context.currentUser
Monotonicity proof: unavailable
Worker execution: unavailable
Explanation: stops at opaque node
```

This is preferable to pretending that every lambda participates in the same proof story.

## 23. Layer 3: rules, evidence, and fixed-point semantics

### 23.1 Applicability as a proof-relevant relation

Instead of an action descriptor returning a list, define a rule whose successful evaluation yields evidence.

```ts
interface Rule<Subject, Action, Evidence> {
  readonly id: RuleId;
  readonly subject: Sort<Subject, unknown>;
  readonly premise: Query<Evidence, unknown, Monotonicity, Portability>;
  build(subject: Subject, evidence: Evidence): Action;
}
```

Conceptually:

```text
Applicable(context, subject, action, evidence)
```

The evidence can contain safe explanatory data:

```ts
interface ArchiveEvidence {
  readonly capabilityId: CapabilityId;
  readonly projectId: ProjectId;
  readonly observedRevision: Revision;
  readonly reasons: readonly Reason[];
}
```

The evidence is not automatically an authorization credential. It can carry a revision so the command kernel detects stale applicability.

### 23.2 Immediate-consequence operator

Let `Base` be the current extensional facts and `Rules` the program. The runtime defines an operator:

```text
T_Base : DerivedFacts -> DerivedFacts
```

The semantic result is `μT_Base`.

This explains several operations uniformly:

- transitive subtype closure;
- translator reachability;
- action-table inheritance;
- occurrence acceptability;
- link connectedness;
- context-dependent capabilities;
- plugin-contributed affordances.

### 23.3 Stratification

A practical program is divided into strata.

```text
stratum 0: base identities, sorts, occurrences, capabilities
stratum 1: subtype and translator reachability
stratum 2: accepted candidates
stratum 3: action applicability
stratum 4: priority selection and presentation ordering
```

Positive recursive rules live within a monotone stratum. Negation only refers to completed lower strata. Priority and “best candidate” selection occur after the set of valid candidates is known.

This separation prevents an ordering rule from contaminating logical validity.

### 23.4 Provenance algebra

Each derived fact can carry an annotation. A small UI-focused provenance type might be:

```ts
type Why =
  | { tag: "fact"; fact: FactId }
  | { tag: "all"; reasons: readonly Why[] }
  | { tag: "any"; alternatives: readonly Why[] }
  | { tag: "rule"; rule: RuleId; reason: Why };
```

A semiring representation is more algebraically compact and supports different interpretations:

- Boolean: is there any derivation?
- natural numbers: how many supports?
- sets: which base facts participated?
- symbolic polynomials: exact alternative/joint provenance;
- costs: cheapest derivation.

The runtime need not expose formal power series to UI authors. It can use the algebra internally and render a human explanation.

### 23.5 Retractions

When base facts disappear, a naïve monotone cache is wrong. Options are chosen per stratum:

```text
small stratum        -> recompute from scratch
acyclic plan         -> reference counts
recursive plan       -> DRed-like support maintenance
delta collection     -> differential dataflow
opaque dependency    -> invalidate conservatively
```

Correctness is more important than maximal granularity. The query compiler should be allowed to choose full recomputation for a small relation.

## 24. Layer 4: open components and typed ports

### 24.1 Component definition

```ts
interface OpenComponent<State, Command, Observation> {
  readonly id: ComponentTypeId;
  readonly ports: PortSchema;
  readonly initial: State;
  step(state: State, command: Command): Transition<State>;
  observe(state: State): Observation;
}
```

A tile placement is not the component. A logical view can instantiate a component. A placement renders an occurrence of that instance.

```text
component type  -> chart semantics
component instance -> one chart view and its local state
placement       -> one rectangle rendering that instance
occurrence      -> one rendered semantic object inside a placement
```

### 24.2 Port modes

```ts
type PortMode =
  | "input"
  | "output"
  | "read"
  | "write"
  | "read-write";

interface Port<A, Mode extends PortMode> {
  readonly id: PortId;
  readonly sort: Sort<A, unknown>;
  readonly mode: Mode;
  readonly protocol: PortProtocol<A>;
}
```

Mode compatibility is checked before linking. A write-only command stream is not equated with a read-write state cell.

### 24.3 Protocols distinguish kinds of connection

Several things are casually called “linking” but have different semantics.

| Protocol | Meaning |
|---|---|
| Equality cell | all members share one current value |
| Event stream | outputs are routed to inputs; events are not state equality |
| Derived map | target observes a transformation of source |
| Constraint | peers must converge to compatible information |
| Selection relation | selected identities in one view influence highlighting in another |
| Command route | actions from one component target another |

The type system should prevent using one protocol as another.

```ts
type PortProtocol<A> =
  | EqualityCellProtocol<A>
  | EventProtocol<A>
  | MonotoneKnowledgeProtocol<A>
  | CommandProtocol<A>;
```

### 24.4 Link equations and topology

```ts
interface Link<A> {
  readonly id: LinkId;
  readonly left: PortId;
  readonly right: PortId;
  readonly protocol: ProtocolId<A>;
  readonly reconciliation: Reconciliation<A>;
  readonly createdBy: ActorId;
  readonly createdAt: LogicalTime;
}
```

The source of truth is the set of links. Binding groups are the colimit-derived connected components of compatible equality links.

### 24.5 Value reconciliation as an algebra

```ts
type Reconciliation<A> =
  | { type: "requireEqual" }
  | { type: "preferLeft" }
  | { type: "preferRight" }
  | { type: "join"; semilattice: JoinSemilattice<A> }
  | { type: "conflict"; build: (left: A, right: A) => Conflict<A> }
  | { type: "interactive"; workflow: WorkflowId };
```

For document selectors, `preferSource` may be a valid product decision. It must be named and testable. For collaborative filters, a set-union semilattice may be more appropriate. For edits, a conflict object may be necessary.

### 24.6 Optics attach ports to state

```ts
interface PortBinding<State, A> {
  readonly port: Port<A, "read-write">;
  readonly focus: Lens<State, A>;
}
```

The lens laws guarantee that the port’s local read and write semantics are coherent. The link runtime then coordinates multiple ports.

### 24.7 Composition and categorical semantics

At the formal level:

- component boundaries are typed objects;
- an open component is a structured cospan;
- parallel composition is monoidal product or coproduct, depending on the chosen category;
- sequential wiring composes cospans by pushout;
- equality links generate a coequalizer on ports;
- the complete workspace is a colimit of its component-and-link diagram.

At runtime, these become records, adjacency indexes, connected components, and transactional writes. The universal property justifies the implementation contract; it does not dictate the data structure.

## 25. Layer 5: the pure command/state kernel

### 25.1 Commands are data

```ts
type WorkspaceCommand =
  | LinkPortsCommand
  | UnlinkCommand
  | WritePortCommand
  | CreateViewCommand
  | PlaceViewCommand
  | ClosePlacementCommand
  | DispatchComponentCommand;
```

A command carries all identity needed to validate it. It does not capture React closures.

### 25.2 Transaction result

```ts
interface Transition<S, E = DomainEffect> {
  readonly state: S;
  readonly effects: readonly E[];
  readonly emittedFacts: readonly FactDelta[];
  readonly audit: AuditRecord;
}
```

The kernel performs link reconciliation and state updates atomically. The semantic runtime then consumes fact deltas.

### 25.3 Preconditions and postconditions

A command definition can pair executable code with reified specifications.

```ts
interface CommandSpec<S, C> {
  readonly pre: StatePredicate<S, C>;
  readonly post: TransitionPredicate<S, C>;
  run(state: S, command: C): Result<Transition<S>, DomainError>;
}
```

The TypeScript runtime checks preconditions. Property tests and a formal model check postconditions. A verified implementation could carry a theorem, but ordinary TypeScript should call these “specifications” or “contracts,” not proofs.

### 25.4 Stale evidence

An action selected from a menu may become invalid before execution. Commands should include the relevant revision or capability token.

```ts
interface ArchiveProjectCommand {
  type: "ArchiveProject";
  projectId: ProjectId;
  observedRevision: Revision;
  capability: CapabilityToken<"ArchiveProject">;
}
```

The kernel revalidates. UI applicability is advisory; command authorization is authoritative.

## 26. Layer 6: interaction programs and handlers

### 26.1 A small effect signature

```ts
type UiOp<A> =
  | { type: "Select"; query: Query<A, unknown, any, any>; prompt: Message }
  | { type: "Confirm"; message: Message }
  | { type: "Dispatch"; command: WorkspaceCommand }
  | { type: "Read"; query: Query<A, unknown, any, any> }
  | { type: "Await"; task: TaskId }
  | { type: "Notify"; notification: Notification };
```

A workflow is a program over these operations.

### 26.2 Handler stack

```text
workflow
  -> selection handler
  -> authorization handler
  -> transaction handler
  -> persistence handler
  -> telemetry handler
  -> platform handler
```

Handlers should be compositional and order-sensitive only where documented. A handler that interprets `Dispatch` into a state transition can be replaced by a simulation handler in tests.

### 26.3 Cancellation

Cancellation is a semantic event, not merely component unmounting. A pending selection should have an explicit owner, cancellation token, and terminal outcome.

```ts
type SelectionOutcome<A> =
  | { type: "selected"; value: A; evidence: AcceptanceEvidence }
  | { type: "cancelled"; reason: CancellationReason }
  | { type: "invalidated"; reason: InvalidationReason };
```

This makes race and stale-context behavior testable.

### 26.4 Selective static fragment

A workflow builder can expose a restricted fragment for predeclared effects:

```ts
const preparedMenu = Selective.mapN(
  read(projectQuery),
  read(capabilityQuery),
  (project, caps) => menuFor(project, caps),
);
```

The runtime can prefetch and analyze this fragment. A later `flatMap` or general generator marks the remainder dynamically dependent.

## 27. Adapter layer: React and the DOM

### 27.1 Occurrences are registrations

A React presentation occurrence should register and unregister a semantic fact:

```ts
function useOccurrence<A>(subject: Entity<A>, sort: Sort<A, unknown>) {
  const occurrenceId = useStableOccurrenceId();

  useLayoutEffect(() => runtime.mountOccurrence({
    id: occurrenceId,
    subject,
    sort,
    surface: currentSurface,
  }), [occurrenceId, subject.key, sort.name, currentSurface]);

  return runtime.observeOccurrence(occurrenceId);
}
```

The hook receives derived state:

```ts
interface OccurrenceObservation {
  readonly acceptableIn: readonly ContextId[];
  readonly actions: readonly ActionInstance[];
  readonly explanation?: Explanation;
  readonly tone?: Tone;
}
```

React renders it. React does not compute it by scanning every request callback.

### 27.2 Event translation

Pointer and keyboard events become semantic commands or effect inputs.

```text
DOM click on occurrence
  -> ActivateOccurrence(occurrenceId, modifiers)
  -> semantic runtime resolves active interaction mode
  -> selection outcome or default action
  -> command kernel
```

This preserves accessibility behavior while moving meaning out of the component.

### 27.3 Virtualization

Only mounted occurrences are directly selectable by pointer. The semantic query may know about unmounted subjects, but an occurrence-based selection operation should distinguish:

```text
candidate subject exists
candidate occurrence is mounted
candidate occurrence is visible
candidate occurrence is reachable by keyboard navigation
```

A separate searchable chooser can materialize subjects that have no current visual occurrence. This avoids pretending that the DOM is a complete output history.

### 27.4 React keys remain local

React keys preserve element identity during reconciliation. They should derive from occurrence or placement identity, not be reused as domain identity tokens. The semantic runtime owns domain identity independently.

---
EOF
```

<details><summary>💭 Thinking</summary>

**Designing alternative architectures**

I’m comparing modern proof-oriented designs for a presentation API: typed syntax, fixed-point facts, coalgebraic interaction traces, colimit-based linking, incremental maintenance, effects, lenses, and formal verification, rather than one monolithic abstraction.

**Extending the blueprint**

I’m carrying the architecture into a worked chart–pipeline example, concrete API sketches, proof obligations, verification layers, performance, migration from the existing system, and clear boundaries against overengineering.

**Designed alternative architectures and extended the blueprint**

</details>

```unknown
bash -lc wc -l -w -c /mnt/data/PRESENTATION-SYSTEMS-BEYOND-CLIM.md && tail -80 /mnt/data/PRESENTATION-SYSTEMS-BEYOND-CLIM.md && printf '\n--- headings ---\n' && rg -n '^#{1,4} ' /mnt/data/PRESENTATION-SYSTEMS-BEYOND-CLIM.md | tail -80
```

<details><summary>💭 Thinking</summary>

**Drafted hybrid comparison matrix after inspecting presentation systems and citations**

</details>

```json
{"search_query":[{"q":"site:arxiv.org interaction trees representing recursive and impure programs in Coq Xia Zakowski He Hurley Malecha Pierce Zdancewic"},{"q":"site:arxiv.org egg fast extensible equality saturation Willsey Nandi Wang Flatt Tatlock Panchekha"},{"q":"site:hal.science CRDT Shapiro Preguiça Baquero Zawirski comprehensive study convergent commutative replicated data types"},{"q":"site:dl.acm.org statecharts visual formalism complex systems Harel 1987"}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Searched 11 websites**

</details>

```unknown
bash -lc cat >> /mnt/data/PRESENTATION-SYSTEMS-BEYOND-CLIM.md <<'EOF'
# Part IV — A worked architecture for linked analytical views

## 28. The chart–pipeline problem as a semantic test case

Assume an analytical workspace contains:

- a chart view whose primary document determines the plotted data;
- a pipeline view whose primary document determines the transformation graph;
- possibly several placements of either logical view;
- document selectors in both views;
- a user operation that links the two selectors so changing either changes both.

This looks like a shared-state problem. That description is incomplete. The architecture must answer at least six independent questions:

1. Which logical views exist?
2. Which visual placements display those views?
3. Which document-selection ports do those views expose?
4. Which ports have been equated by links?
5. What value should a newly formed link component observe if its members disagree?
6. Which interaction and authorization facts permit the link command?

A single `linkedTo` property or callback does not answer all six. The open-component model does.

## 29. Semantic declarations

The domain begins with nominal sorts and stable identities:

```ts
const Document = schema.sort<Document>({
  name: "document",
  key: document => document.id,
});

const View = schema.sort<View>({
  name: "view",
  key: view => view.id,
});

const Placement = schema.sort<Placement>({
  name: "placement",
  key: placement => placement.id,
});
```

The schema also records relations:

```ts
const presentsView = schema.relation(Placement, View, {
  name: "presentsView",
  cardinality: "many-to-one",
});

const viewKind = schema.attribute(View, literal("chart", "pipeline", "table"), {
  name: "viewKind",
});
```

The identity functions are not display labels and are not React keys. They establish the semantic equality used by the runtime.

## 30. Components and document ports

A chart definition exposes a document-selection port:

```ts
const ChartComponent = component.define({
  kind: "chart",
  state: ChartState,
  ports: {
    primaryDocument: port.cell(Document, {
      protocol: "equality",
      mode: "read-write",
      focus: optic.path<ChartState>()("documentId"),
    }),
  },
  observations: chartObservations,
  commands: chartCommands,
});
```

The pipeline has a port with the same protocol and sort:

```ts
const PipelineComponent = component.define({
  kind: "pipeline",
  state: PipelineState,
  ports: {
    primaryDocument: port.cell(Document, {
      protocol: "equality",
      mode: "read-write",
      focus: optic.path<PipelineState>()("documentId"),
    }),
  },
  observations: pipelineObservations,
  commands: pipelineCommands,
});
```

The port declaration states four things that an ordinary setter does not:

- the semantic sort carried by the port;
- whether the component reads, writes, or does both;
- which connection protocol the port implements;
- how the port focuses the component's local state.

Port compatibility is a decidable schema-level judgment. A chart document port cannot accidentally link to a numeric chart-scale port merely because both happen to be represented by strings at runtime.

## 31. Link topology as a quotient

Let `P` be the finite set of document-port endpoints in one workspace. Let `E` be the set of explicit equality links. Each link has a source and target endpoint, giving two maps:

```text
s, t : E -> P
```

The equality-link topology is the coequalizer of those maps:

```text
E ⇉ P -> P / ~
```

where `~` is the least equivalence relation containing every pair `(s(e), t(e))`. Concretely, `P / ~` is the set of connected components in the undirected link graph.

This gives a precise meaning to “these selectors are linked”:

> Two ports share a logical binding exactly when the quotient map sends them to the same equivalence class.

For link additions, a union–find data structure is an efficient implementation of this quotient. The union–find structure is an implementation cache, not the durable definition. The durable state keeps the generating links because deletions require more information than an already-collapsed partition contains.

### 31.1 Why a binding ID is not the semantics

An implementation will normally assign each equivalence class an opaque `BindingId`:

```ts
interface BindingId extends Brand<string, "BindingId"> {}
```

That ID is useful for indexing. It should not be treated as the mathematical identity of the class. Recomputing the quotient, importing a workspace, or replaying an event log may allocate a different ID for an isomorphic topology.

Persistence should therefore be invariant under alpha-renaming of binding IDs. The observable structure is:

- which endpoints are equated;
- the protocol attached to the component;
- the resolved value and its provenance;
- not the particular generated string used as a cache key.

## 32. A colimit does not reconcile conflicting values

Suppose the chart currently selects document `A` and the pipeline selects document `B`. Adding an equality link determines that the two ports belong to one quotient class. It does not prove that `A = B`, and it does not select one value.

Value reconciliation is a separate algebra:

```ts
type Reconciliation<A> =
  | { tag: "requireEqual" }
  | { tag: "prefer"; endpoint: PortEndpointId }
  | { tag: "choose"; value: A; evidence: Evidence }
  | { tag: "join"; semilattice: JoinSemilattice<A> };
```

The link command must either supply a lawful strategy or return an explicit conflict:

```ts
type LinkResult<A> =
  | { tag: "linked"; binding: BindingId; value: A }
  | { tag: "conflict"; proposals: readonly PortProposal<A>[] }
  | { tag: "rejected"; reason: LinkRejection };
```

For ordinary document selectors, a source-preferred strategy is often appropriate because the gesture begins at a source selector. For collaborative sets, a semilattice join may be appropriate. For an exclusive resource or destructive setting, `requireEqual` or an explicit user choice is safer.

Making this policy explicit prevents an important category error:

```text
colimit of interfaces       = which boundaries are identified
reconciliation algebra      = which value the identified boundary observes
```

These constructions can be composed, but they are not interchangeable.

## 33. Link and unlink commands

Commands are immutable data checked by the pure kernel:

```ts
type WorkspaceCommand =
  | {
      tag: "LinkPorts";
      left: PortEndpointId;
      right: PortEndpointId;
      reconciliation: Reconciliation<DocumentId>;
      authorization: Evidence<"CanLinkPorts">;
    }
  | {
      tag: "UnlinkPorts";
      edge: LinkEdgeId;
      authorization: Evidence<"CanUnlinkPorts">;
    }
  | {
      tag: "SetPortValue";
      endpoint: PortEndpointId;
      value: DocumentId;
      expectedRevision: Revision;
    };
```

A successful `LinkPorts` transition performs a logically atomic operation:

1. verify that both endpoints exist;
2. verify sort and protocol compatibility;
3. verify the authorization evidence against the current revision;
4. add a generating edge;
5. recompute or incrementally merge the affected quotient classes;
6. reconcile the proposals;
7. write one resolved binding value;
8. emit topology and value deltas;
9. retain derivation evidence for explanations and undo.

An unsuccessful reconciliation must not leave a half-linked topology unless the product explicitly models a pending-conflict state.

### 33.1 Unlinking is not an inverse colimit

A quotient forgets which generating equations were responsible for an equivalence class. Therefore, “take the inverse of the colimit” is not a meaningful unlink algorithm.

The durable graph retains each explicit link edge. Unlinking removes one edge and recomputes connected components only for the previously affected class. If the removal splits the class, every new component initially receives the old resolved value:

```text
before: {chart, pipeline, table} -> document A
remove edge pipeline—table

after:  {chart, pipeline} -> document A
        {table}           -> document A
```

This gives a useful preservation law: unlinking changes topology but does not unexpectedly change a selector's current value.

If there are multiple paths between two ports, removing one edge does not unlink them. This is exactly what the graph semantics predicts and is difficult to express correctly with only a `linkedGroupId` field.

## 34. Derived facts for linking

The relational layer derives link-related interface facts:

```text
CompatiblePort(p, q)
  :- PortSort(p, s), PortSort(q, s),
     PortProtocol(p, k), PortProtocol(q, k),
     p != q.

SameBinding(p, q)
  :- QuotientClass(p, c), QuotientClass(q, c).

CanLink(ctx, p, q)
  :- CompatiblePort(p, q),
     HasCapability(ctx, LinkWorkspacePorts),
     not SameBinding(p, q).

Action(ctx, p, link(q))
  :- CanLink(ctx, p, q),
     MountedOccurrence(q, occurrence),
     Reachable(ctx, occurrence).
```

The final rule is intentionally occurrence-sensitive. A port can be a semantically valid link target while having no mounted occurrence. A pointer-driven workflow should show only reachable mounted targets; a searchable command palette can query all valid semantic targets.

Each derived action carries evidence:

```ts
interface CanLinkEvidence {
  readonly rule: "CanLink";
  readonly context: ContextId;
  readonly left: PortEndpointId;
  readonly right: PortEndpointId;
  readonly premises: readonly Evidence[];
  readonly revision: Revision;
}
```

The command kernel rechecks or validates this certificate. Action visibility remains a convenience, not an authorization boundary.

## 35. The interaction program

The linking gesture is an effect program rather than a component callback:

```ts
const linkDocumentSelector = workflow(function* (
  source: PortEndpoint<DocumentId>,
) {
  const target = yield* chooseOne(
    query.ports(Document)
      .where(expr.notEqual(field("id"), literal(source.id)))
      .where(rulePredicate("CanLink", source.id, field("id"))),
    {
      prompt: "Choose another document selector to link",
      surface: "mounted-occurrences",
      cancellation: "abort",
    },
  );

  const result = yield* issue({
    tag: "LinkPorts",
    left: source.id,
    right: target.id,
    reconciliation: { tag: "prefer", endpoint: source.id },
    authorization: target.evidence,
  });

  if (result.tag === "conflict") {
    const choice = yield* chooseConflictResolution(result.proposals);
    yield* issue(resolveLinkConflict(result, choice));
  }

  return result;
});
```

The React document bar starts this program. It does not own its continuation, global Escape behavior, candidate scanning, or command execution.

A handler stack determines what `chooseOne`, `issue`, and conflict resolution mean in a particular environment:

```text
workflow
  -> input-context handler
  -> capability/evidence handler
  -> command transaction handler
  -> persistence/event handler
  -> telemetry handler
  -> React occurrence handler
```

A test handler can provide a chosen target directly and compare the resulting command trace. A replay handler can supply recorded choices. A formal semantics can interpret the same effect signature as a labeled transition system.

## 36. Core theorems for the worked example

The architecture makes the desired properties small enough to state precisely.

### 36.1 Quotient coherence

For every reachable state `S` and compatible equality-linked ports `p` and `q`:

```text
p ~S q  =>  observe(S, p) = observe(S, q)
```

A proof factors `observe` through the quotient map. Every endpoint reads the value associated with its equivalence class, so equivalent endpoints necessarily observe the same value.

### 36.2 Order independence of topology

For a fixed endpoint set and a fixed set of equality edges, the generated equivalence relation is independent of insertion order:

```text
quotient(P, permutation(E)) ≅ quotient(P, E)
```

The runtime may allocate different opaque binding IDs, so the result is isomorphism rather than byte equality. Property tests should canonicalize components before comparison.

### 36.3 Incremental quotient correctness

Let `Q(S)` be the quotient recomputed from durable edges and `Q̂(S)` be the cached incremental representation. For every command trace:

```text
canonical(Q̂(S)) = canonical(Q(S))
```

This is the refinement theorem for union–find additions and the deletion algorithm. It can be tested by comparing the optimized runtime with a slow reference implementation after randomly generated command sequences.

### 36.4 Unlink locality

Removing an edge can change only the connected component that contained that edge's endpoints. Every other quotient class is unchanged.

This gives a precise invalidation frontier for the incremental engine.

### 36.5 Value preservation on unlink

If unlink succeeds without an explicit value-changing command, every endpoint observes the same value immediately before and after the transition:

```text
observe(S, p) = observe(unlink(S, e), p)
```

Topology may split; focused values do not.

### 36.6 Placement independence

Adding or removing a placement of a logical chart view does not change the chart view's document-port equivalence class. A placement presents a view; it does not own the view's semantic port.

This prevents a duplicated visual tile from accidentally duplicating or breaking the shared document selection.

### 36.7 Serialization up to renaming

Decoding an encoded workspace preserves endpoint incidence, link equations, and binding values up to fresh runtime identifiers:

```text
decode(encode(S)) ≅ S
```

The isomorphism may rename view, placement, edge, and binding IDs according to the portability policy. It must preserve the relations among them.

### 36.8 Authorization safety

Every successful `LinkPorts` transition has current evidence for the required capability:

```text
transition(S, LinkPorts(...)) = Success(S')
  => validAt(S, authorization, CanLinkPorts)
```

This property is enforced in the command kernel, independently of whether a UI action was visible.

---

# Part V — A concrete API surface

## 37. Design goals for the public API

The mathematical decomposition should not leak into every call site. Most application code should use a small fluent API with generated types. The implementation underneath should retain a first-order representation.

The public API should have these properties:

- **typed:** sort, relation, command, and port mismatches fail during development;
- **reified:** inspectable definitions have an AST or equivalent intermediate representation;
- **interpretable:** the same definition can run locally, in a worker, in tests, or in a formal model;
- **classifiable:** the runtime knows whether a definition is pure, monotone, incremental, serializable, or opaque;
- **explainable:** derived results can expose provenance;
- **extensible:** plugins contribute modules without mutating a process-global registry;
- **escape-friendly:** opaque JavaScript remains possible at a named boundary;
- **layered:** a user can adopt semantic identity and queries before adopting recursive rules or open components.

## 38. Modules instead of a global registry

A feature exports a semantic module:

```ts
export const projectsModule = defineModule({
  id: "projects",
  schema: [Project, ProjectId, ownsProject, projectStatus],
  queries: [activeProjects, projectsOwnedBy],
  rules: [projectActions, projectTranslations],
  commands: [OpenProject, ArchiveProject],
  components: [ProjectBrowser],
  workflows: [chooseProject, archiveFromOccurrence],
});
```

Modules combine through an explicit composition operation:

```ts
const application = composeModules(
  coreModule,
  documentsModule,
  chartsModule,
  pipelinesModule,
  projectsModule,
);
```

Composition performs checks:

- duplicate stable names;
- schema compatibility;
- rule stratification;
- unresolved imports;
- effect-handler coverage;
- port-protocol compatibility;
- command codec availability;
- opaque-definition policy.

The composition result is immutable. A provider receives one compiled application object rather than relying on registration order.

### 38.1 Plugin imports and exports

A module can declare a signature:

```ts
const comparisonPlugin = defineModule({
  id: "comparison",
  imports: {
    Document: importSort("core/Document"),
    OpenDocument: importCommand("documents/OpenDocument"),
  },
  exports: {
    ComparisonSet,
    AddToComparison,
  },
  // ...
});
```

This resembles ordinary module systems more than CLIM command-table mutation. It also provides a boundary for versioning and formal assumptions.

## 39. Sort and entity declarations

A sort declaration separates runtime representation, semantic identity, codecs, and optional laws:

```ts
const Project = sort.define<Project>({
  name: "projects/Project",
  key: project => project.id,
  codec: projectCodec,
  change: projectChangeStructure,
  laws: {
    keyStableAcross: ["rename", "status-change"],
  },
});
```

A first-class entity packages the sort and key with a current value or lookup reference:

```ts
type Entity<S extends Sort<any>> = {
  readonly sort: S;
  readonly key: KeyOf<S>;
};

const projectEntity = Project.entity(project.id);
```

Occurrences present entities, not arbitrary object references:

```tsx
<SemanticOccurrence subject={Project.entity(project.id)}>
  <ProjectCard project={project} />
</SemanticOccurrence>
```

The runtime can obtain current attributes through relations or a repository interpreter. This avoids retaining stale domain objects solely because they were captured by a rendered callback.

### 39.1 Value presentations remain possible

Not every presentation denotes a durable entity. A computed scalar, range, error, or transient suggestion may be a value presentation:

```ts
const Temperature = sort.value<number>({
  name: "measure/Temperature",
  equals: Object.is,
  codec: numberCodec,
});
```

The API distinguishes entity identity from value equality. It does not force every value into an artificial ID table.

## 40. Query construction

A typical selection query is first-order:

```ts
const activeOwnedProject = query
  .from(Project)
  .where(and(
    eq(Project.attr("archived"), literal(false)),
    eq(Project.attr("ownerId"), context.param(UserId, "currentUser")),
  ))
  .orderBy(Project.attr("title"), "ascending")
  .explain("active project owned by the current user");
```

A query over occurrences composes semantic and surface conditions:

```ts
const visibleActiveOwnedProject = query
  .occurrencesOf(activeOwnedProject)
  .where(eq(Occurrence.attr("mounted"), literal(true)))
  .where(eq(Occurrence.attr("reachable"), literal(true)));
```

The runtime may compile these into:

- hash indexes by sort and attribute;
- incremental relational operators;
- a worker-executable plan;
- a static dependency set;
- a human-readable explanation plan;
- a reference evaluator used for differential testing.

### 40.1 Opaque refinement

For an unusual local criterion:

```ts
const visuallyInteresting = activeOwnedProject.opaqueWhere({
  id: "projects/visually-interesting-v1",
  reads: [Project.attr("title"), Project.attr("summary")],
  stability: "per-revision",
  evaluate: project => bespokeHeuristic(project),
});
```

The declaration is honest about the boundary. The runtime can use the declared dependency set and revision stability but cannot derive a proof of the heuristic's extensional behavior from its body.

Policy can forbid opaque queries in specific contexts:

```ts
compile(application, {
  opaquePolicy: {
    authorization: "forbidden",
    persistence: "forbidden",
    localPresentationHint: "allowed",
  },
});
```

## 41. Rules and proof-relevant results

An action rule is not a callback attached to a descriptor:

```ts
const ArchiveProjectAction = rule.define({
  name: "projects/ArchiveProjectAction",
  variables: { ctx: Context, project: Project },
  when: all(
    fact(Project.exists("project")),
    fact(Project.attr("archived").is(false)),
    fact(Context.hasCapability("ctx", ArchiveProjects)),
    fact(Occurrence.presents("project")),
  ),
  derive: Action.available({
    id: "archive-project",
    subject: variable("project"),
    command: ArchiveProject.with({ project: variable("project") }),
  }),
});
```

The runtime derives an `ActionInstance` and a derivation:

```ts
interface ActionInstance<C extends Command<any>> {
  readonly id: ActionId;
  readonly command: C;
  readonly subject: Entity<any>;
  readonly evidence: Evidence<CanExecute<C>>;
  readonly explanation: DerivationTree;
}
```

The evidence is not automatically a proof object accepted by Lean or Coq. It is a checkable certificate in the runtime's small rule kernel. A mechanized model can prove that the certificate checker is sound with respect to the declarative semantics.

## 42. Commands and events

A command declaration contains its codec, precondition relation, and pure transition:

```ts
const ArchiveProject = command.define({
  name: "projects/ArchiveProject",
  input: struct({ project: Project.keyCodec }),
  requires: CanArchiveProject,
  decide(state, input, evidence) {
    const project = state.projects.get(input.project);
    if (!project || project.archived) {
      return reject("project-not-active");
    }

    return accept({
      state: state.updateProject(input.project, {
        archived: true,
        revision: project.revision + 1,
      }),
      events: [{ tag: "ProjectArchived", project: input.project }],
      effects: [],
    });
  },
});
```

Commands may be interpreted through event sourcing, direct state replacement, Redux actions, a server transaction, or a replicated protocol. The semantic contract is the pure decision relation.

### 42.1 Command evidence is revision-sensitive

The action runtime may derive permission at revision `r`. By the time the user activates it, the state can be at revision `r + 1`. Therefore evidence contains a revision or dependency version. The command interpreter either:

- validates that the relevant dependencies are unchanged;
- re-derives the precondition;
- or rejects the stale command.

This avoids time-of-check/time-of-use bugs while preserving responsive menus.

## 43. Effects and workflows

A workflow API can use generators as surface syntax while recording an interaction tree:

```ts
const chooseAndOpenProject = workflow.define("projects/ChooseAndOpen", function* () {
  const project = yield* effect.chooseOne(activeOwnedProject, {
    prompt: "Choose a project",
  });

  yield* effect.issue(OpenProject({ project: project.key }));
  yield* effect.focus(Project.entity(project.key));
});
```

A JavaScript generator by itself is opaque. The builder must capture operations as typed effect nodes rather than immediately executing them. General host-language branching still means the complete future effect set may depend on earlier results. That is acceptable in the monadic fragment.

For workflows that need static analyzability, a selective builder restricts branching:

```ts
const preflight = selective
  .read(activeOwnedProject)
  .and(readCapabilities)
  .map(buildAvailableOpenActions);
```

The API should expose the distinction rather than claim all workflows can be fully planned in advance.

## 44. Components and interpreters

A semantic component definition is independent of React:

```ts
const ProjectBrowser = component.define({
  name: "projects/ProjectBrowser",
  state: ProjectBrowserState,
  ports: {
    selectedProject: port.optional(Project, {
      protocol: "equality",
      mode: "read-write",
      focus: projectBrowserSelectedProject,
    }),
  },
  observations: {
    rows: activeOwnedProject,
    actions: actionsFor(Project),
  },
  transition: projectBrowserTransition,
});
```

React is one rendering interpreter:

```tsx
const ReactProjectBrowser = react.interpret(ProjectBrowser, view => (
  <div role="listbox">
    {view.rows.map(row => (
      <SemanticOccurrence key={row.key} subject={row.entity}>
        <ProjectRow row={row} actions={view.actions.for(row.entity)} />
      </SemanticOccurrence>
    ))}
  </div>
));
```

Other interpreters can produce:

- a textual command interface;
- a test model;
- a remote protocol description;
- an accessibility tree audit;
- a dependency visualization;
- a static documentation page.

The architecture does not require every component to be renderer-agnostic. Highly visual rendering can remain React-specific. It requires only that domain semantics and transitions are not *defined* by React lifecycle.

## 45. Runtime assembly

The application compiler produces a runtime plan:

```ts
const plan = compile(application, {
  queryBackend: "incremental",
  provenance: "minimal-derivation",
  workflowBackend: "interaction-tree",
  persistence: workspaceCodec,
});

const runtime = instantiate(plan, {
  repositories,
  effectHandlers,
  commandHandler,
  scheduler,
});
```

The React root receives the instance:

```tsx
<PresentationRuntimeProvider runtime={runtime}>
  <Workspace />
</PresentationRuntimeProvider>
```

The provider is now an adapter boundary. The compiled semantic application, not the provider component, is the primary unit of composition.

---
EOF
wc -l -w /mnt/data/PRESENTATION-SYSTEMS-BEYOND-CLIM.md
```

<details><summary>💭 Thinking</summary>

**Appended Part IV architecture text**

</details>

```json
{"search_query":[{"q":"site:arxiv.org \"A Theory of Changes for Higher-Order Languages\" incremental lambda calculus"},{"q":"site:arxiv.org \"Structured Cospans\" Baez Courser"},{"q":"site:arxiv.org \"Profunctor Optics\" Clarke Elkins Gibbons Loregian Milewski Pillmore Román"},{"q":"site:arxiv.org \"Functorial Data Migration\" Spivak"}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Searched 9 websites**

</details>

```unknown
bash -lc cat >> /mnt/data/PRESENTATION-SYSTEMS-BEYOND-CLIM.md <<'EOF'
# Part VI — Proof architecture

## 46. A compact formal model

A useful formalization should be substantially smaller than the implementation. One possible semantic state is:

```text
W = (B, D, G, V, C, O, r)
```

where:

- `B` is the set of base facts supplied by repositories and mounted occurrences;
- `D` is the set of derived facts;
- `G` is the open-component and link graph;
- `V` maps binding classes and local state cells to values;
- `C` is durable command/application state;
- `O` is occurrence and surface state;
- `r` is a logical revision.

For a fixed schema `Σ`, each query has a denotation:

```text
⟦q : Query A⟧W ⊆ A
```

Rules induce an immediate-consequence operator:

```text
TΣ,W : Facts -> Facts
```

and the derived database is:

```text
D = μX. TΣ,(B,X,G,V,C,O,r)(X)
```

A command is interpreted by a partial transition relation:

```text
(C, G, V, r) --command/events/effects--> (C', G', V', r + 1)
```

A workflow is a possibly infinite interaction tree over an effect signature. Handlers interpret that tree into command transitions, external requests, and observations. The React adapter contributes occurrence facts and translates DOM events into semantic input events.

This model intentionally does not include CSS layout, pixels, or React reconciliation. Those belong to the adapter refinement boundary.

## 47. The trusted computing base

A proof-oriented implementation should minimize the code whose correctness everything else assumes. The trusted semantic kernel consists of:

1. sort and key checking;
2. query AST constructors and the reference evaluator;
3. rule certificate checking;
4. command precondition checking and pure transition execution;
5. link-graph compatibility and quotient construction;
6. reconciliation algebra implementations;
7. codec validation;
8. effect-event constructors.

Optimized query plans, caches, indexes, union–find structures, worker protocols, and React hooks need not be trusted if they can be checked against or refined to this kernel.

### 47.1 Certificates rather than faith in the optimizer

An optimized layer can return a result plus a certificate:

```ts
interface DerivedResult<A> {
  readonly value: A;
  readonly evidence: Evidence;
}
```

The kernel checks the derivation against current base facts. The optimizer may miss results if completeness is not required for a particular hint, but it may not invent an action or authorization fact that the checker rejects.

For complete query results, differential testing compares optimized execution to the reference evaluator. A future verified compiler could prove the equality once and remove some runtime checking.

## 48. Structural induction obligations

The query and predicate languages support proofs by syntax.

### 48.1 Query type soundness

A representative theorem is:

```text
If Γ ⊢ q : Query A and a ∈ ⟦q⟧W, then Γ ⊢ a : A.
```

The proof proceeds by induction over `q`:

- `from(Sort A)` returns only entities of sort `A`;
- `where(q, p)` returns a subset of the induction hypothesis;
- `map(q, f)` uses the typing of `f`;
- `join(q1, q2, relation)` uses the relation's source and target sorts;
- union requires equal result sorts.

This theorem is modest, but it is the foundation for safe action and command construction.

### 48.2 Dependency-analysis soundness

Let `deps(q)` be the statically calculated set of base relations and context parameters read by query `q`. The desired property is:

```text
W and W' agree on deps(q)
  => ⟦q⟧W = ⟦q⟧W'.
```

This proves that the incremental runtime need not invalidate `q` after unrelated changes. The proof is again structural induction.

Opaque nodes require their declared dependency set to be treated as an assumption. The architecture should label the resulting theorem as conditional on that declaration.

### 48.3 Optimizer correctness

For every rewrite `q -> q'`:

```text
⟦q⟧W = ⟦q'⟧W
```

Examples include:

```text
filter(filter(q, p), r)
  = filter(q, p ∧ r)

filter(union(q, r), p)
  = union(filter(q, p), filter(r, p))
```

The second law requires set semantics or an appropriate bag-semantics qualification. Reification forces these hidden assumptions into the specification.

## 49. Fixed-point induction

If the rule operator `T` is monotone, its least fixed point supports the standard induction principle:

```text
T(P) ⊆ P
────────────
 μT ⊆ P
```

Here `P` is an invariant viewed as a set of allowed facts. To prove that every derived executable action has valid authority evidence, show that:

1. base facts satisfy the invariant;
2. every rule preserves it;
3. joins of approximants preserve it.

Then every fact in the least fixed point satisfies it.

### 49.1 A transfinite formulation

For an inflationary monotone operator `F` on a complete lattice, define an ordinal-indexed chain:

```text
X₀       = ⊥
Xα+1     = Xα ⊔ F(Xα)
Xλ       = ⨆β<λ Xβ       when λ is a limit ordinal
```

To prove an invariant `I` for every approximation:

- **base:** prove `I(X₀)`;
- **successor:** prove `I(Xα) => I(Xα+1)`;
- **limit:** prove that if `I(Xβ)` holds for every `β < λ`, then `I(⨆β<λ Xβ)`;
- apply transfinite induction;
- at a closure ordinal `κ` where `Xκ = Xκ+1`, conclude `I(μF)`.

This is where transfinite induction has a legitimate role in the architecture. It is a metatheoretic technique for general lattices and infinitary rule systems. It is not a recommendation to represent ordinals in production JavaScript.

### 49.2 When iteration stops earlier

Practical runtimes usually have stronger finiteness or continuity assumptions:

- over a finite active domain with no fresh-value generation, ascending chains stabilize after finitely many fact insertions;
- for an ω-continuous operator, the least fixed point is the join of the finite approximants at stage `ω`;
- stratified negation computes a sequence of monotone fixed points, one stratum at a time;
- widening can force convergence in abstract domains with infinite ascending chains, at the cost of approximation.

The compiler should record which case applies. “Monotone” alone guarantees existence on a complete lattice, not efficient finite convergence.

## 50. Provenance and proof relevance

A Boolean query result loses the reason why it holds. A provenance-aware runtime associates each result with an expression over source-fact tokens.

For positive relational rules, a commutative semiring interpretation is natural:

```text
alternative derivations  -> addition
joint premises           -> multiplication
base fact                -> variable token
```

For example:

```text
CanLink(chart, pipeline)
  = compatible(chart, pipeline)
  × capability(user, LinkPorts)
  × notAlreadyLinked(chart, pipeline)
```

If two rules derive the same action, provenance addition records alternatives. Different interpretations can answer different questions:

- Boolean: does any derivation exist?
- natural numbers: how many derivations exist?
- sets: which base facts contributed?
- security labels: what is the maximum sensitivity?
- costs: what is the cheapest derivation?
- symbolic expressions: what explanation tree should be shown?

Negation, aggregation, and retraction require richer provenance models than the simplest positive semiring. The implementation should not imply that one annotation algebra solves every rule fragment.

### 50.1 Evidence minimization

A full derivation DAG may be too large for menus. The runtime can retain:

- one minimal derivation for ordinary explanation;
- all derivations only in diagnostic mode;
- a compact dependency set for invalidation;
- a cryptographic or revision-stamped summary for remote execution.

The chosen compression must preserve whatever the checker needs.

## 51. Incremental correctness

Let `eval(q, W)` be full query evaluation and `update(q, W, ΔW)` be an incremental update returning a result delta. The key law is:

```text
eval(q, W ⊕ ΔW)
  = eval(q, W) ⊕ update(q, W, ΔW)
```

The change action `⊕` depends on the result domain. Sets use insertion and deletion deltas; counts use integer differences; maps use keyed patches; lattices may use joins.

An incremental compiler should prove or test this law constructor by constructor. Composition then follows from the query syntax.

### 51.1 Recursive incremental maintenance

Recursive rules require feedback. A semi-naive or differential implementation propagates only changes through the loop rather than recomputing the entire closure. The correctness statement remains observational equivalence with the reference least-fixed-point evaluator.

A useful testing strategy is:

1. generate a random small base world;
2. compute the reference fixed point;
3. generate a random valid delta;
4. update the optimized runtime;
5. recompute the reference result from scratch;
6. compare canonical facts and provenance obligations.

This catches errors in retractions, recursion, and invalidation that ordinary example tests miss.

## 52. Categorical proof obligations for components

### 52.1 Functorial interpretation

If component composition is represented by an operation `⊗` and a renderer is an interpreter `R`, a compositionality law is:

```text
R(A ⊗ B) ≅ R(A) ⊗R R(B)
```

The right-hand composition is renderer-specific. For a test interpreter it may be product composition; for React it may be a component tree and shared runtime scope. The law need not assert pixel equality. It asserts preservation of declared boundary and transition structure.

### 52.2 Colimit universality

For a wiring diagram `D`, let `colim D` be the composed interface. The universal property states that any compatible family of maps from the diagram into another interface factors uniquely through the colimit.

In the finite equality-link case, this specializes to the quotient fact:

> Any function on endpoints that gives equal results to explicitly linked endpoints factors uniquely through the set of binding classes.

This proves that the quotient is neither too coarse nor too fine for equality links.

### 52.3 Optic laws

A total lens focusing state `S` onto value `A` should satisfy:

```text
get(put(s, a))       = a              // Put–Get
put(s, get(s))       = s              // Get–Put
put(put(s, a), b)    = put(s, b)      // Put–Put
```

These laws justify treating a port update as a coherent update of component state. Partial optics and traversals need their own qualified laws. A path that may disappear cannot honestly be declared a total lens.

### 52.4 Protocol algebra laws

A semilattice reconciliation protocol requires:

```text
join(a, a) = a                 // idempotent
join(a, b) = join(b, a)        // commutative
join(join(a, b), c)
  = join(a, join(b, c))        // associative
```

These laws make merge order irrelevant and are central to replicated convergence. A source-preferred strategy does not satisfy commutativity and must remain an ordered command policy rather than being mislabeled a merge algebra.

## 53. Coalgebraic and temporal proof obligations

A workflow can be observed through traces of visible events:

```text
Prompt(query)
Choose(subject)
Issue(command)
CommandAccepted(events)
Focus(subject)
```

Two handlers are behaviorally equivalent when their observable traces are related by the chosen equivalence, commonly weak bisimulation that ignores internal scheduling steps.

### 53.1 Handler refinement

Let `Hspec` be a simple reference handler and `Hreact` the browser handler. The adapter correctness goal is:

```text
traces(Hreact(program)) ⊆ traces(Hspec(program))
```

The browser may add timing and rendering events, but every semantic choice, cancellation, and issued command must be permitted by the specification.

### 53.2 Safety and liveness

Temporal properties include:

```text
Safety:
  always(CommandAccepted(c) => preconditionHeld(c))

Cancellation:
  always(Abort(context) => eventually Resolved(context, null))

No double resolution:
  always(Resolved(context, x) => neverAgain Resolved(context, _))

Link propagation:
  always(SetPortValue(p, v) and Linked(p, q)
         => next Observe(q, v))
```

Liveness requires assumptions about fair scheduling and external responses. A workflow waiting for a network operation cannot be proven to finish without an environment assumption.

## 54. A layered verification strategy

No single tool should be forced to verify the entire TypeScript/React stack.

### 54.1 TypeScript

Use the type system for:

- nominal IDs and sorts;
- command input/result pairing;
- port protocol compatibility;
- effect signatures;
- query result types;
- opaque-definition classifications;
- exhaustiveness over closed syntax.

TypeScript does not establish runtime purity, totality, or algebraic laws. Branded evidence prevents accidental construction across ordinary module boundaries, not adversarial forging by arbitrary JavaScript.

### 54.2 Property-based testing

Use generated worlds and command traces for:

- identity laws;
- codec round trips;
- optic laws;
- reconciliation laws;
- query optimizer equivalence;
- full versus incremental evaluation;
- graph cache versus reference quotient;
- serialization up to renaming;
- undo and replay properties.

Property tests are especially valuable at the boundary where TypeScript's static guarantees end.

### 54.3 Alloy

A bounded relational model is suitable for structural questions:

- can a placement refer to two incompatible logical views?
- can an endpoint belong to two binding classes?
- can unlinking split an unrelated class?
- can a link survive after its endpoint is deleted?
- can module composition create a name collision or cyclic import?

Alloy does not prove the unbounded theorem, but counterexamples in small scopes often expose modeling mistakes rapidly.

### 54.4 TLA+

A temporal specification is suitable for workflows, concurrency, and distributed command handling:

- action evidence becomes stale during interaction;
- two users concurrently link and unlink ports;
- retries duplicate a command;
- a pending input context is cancelled during a remote response;
- local optimistic state is reconciled with server rejection.

The model can check safety and liveness under explicit fairness assumptions.

### 54.5 Lean, Coq, or Agda

Mechanize the small mathematical core:

- query syntax and reference semantics;
- rule closure and fixed-point induction;
- evidence-checker soundness;
- quotient/link coherence;
- command-kernel invariants;
- interaction-tree semantics and selected handlers.

The implementation relationship can begin as differential testing against extracted or separately implemented reference semantics. A later phase can generate TypeScript from a verified core or verify a lower-level implementation language. Full React verification is not a prerequisite for obtaining value.

## 55. The theorem catalogue

A project-level verification plan should name the theorems it intends to maintain. A practical initial catalogue is:

| ID | Statement | Primary technique |
|---|---|---|
| ID-1 | semantic equality is an equivalence relation | algebraic laws / property tests |
| Q-1 | query evaluation is type-sound | structural induction |
| Q-2 | dependency analysis is sound | structural induction |
| Q-3 | optimizer rewrites preserve denotation | equational proof + differential tests |
| R-1 | rule operator is monotone within each positive stratum | syntax classification |
| R-2 | every derived action has a valid derivation | fixed-point induction |
| R-3 | incremental closure equals full closure | refinement proof + differential tests |
| L-1 | equality-linked ports observe one value | quotient factorization |
| L-2 | link insertion order changes only generated IDs | equivalence closure / isomorphism |
| L-3 | unlink affects only the prior connected component | graph argument |
| O-1 | state ports satisfy their declared optic laws | property tests or proof |
| C-1 | accepted commands preserve workspace invariants | inductive transition invariant |
| C-2 | privileged commands require current authorization | kernel safety proof |
| W-1 | each input context resolves at most once | state-machine invariant |
| W-2 | browser traces refine workflow semantics | simulation or bisimulation |
| P-1 | encode/decode preserves semantic structure up to renaming | isomorphism proof + tests |

This catalogue is more useful than a general aspiration to “formally verify the UI.”

---
EOF
wc -l -w /mnt/data/PRESENTATION-SYSTEMS-BEYOND-CLIM.md
```

<details><summary>💭 Thinking</summary>

**Appended proof architecture Part VI section**

</details>

```unknown
bash -lc cat >> /mnt/data/PRESENTATION-SYSTEMS-BEYOND-CLIM.md <<'EOF'
# Part VII — Additional architectural directions

The recommended hybrid is not the only modern alternative. Several research traditions can replace or strengthen individual layers.

## 56. Equality saturation and e-graphs

An e-graph compactly represents a congruence relation over many expressions. Equality saturation repeatedly applies sound rewrites without committing to one sequence; an extraction phase later chooses a representative according to a cost model.

This can be useful for a presentation system when several **provably equivalent expressions** describe one semantic result:

```text
filter(filter(q, p), r)
  ≡ filter(q, p ∧ r)

project(join(a, b), fieldsFromA)
  ≡ a                 under a declared key constraint
```

It can also optimize conversion plans if rewrites express true equivalences and extraction costs encode latency, information loss, or user preference.

A modern possibility is to combine relational fixed-point reasoning with equality saturation. An equality-aware rule engine can maintain both facts and congruence classes, and certifying variants can emit equality proofs.

### 56.1 Where e-graphs do not fit

A presentation translator is not automatically an equality. Converting a detailed project to a project ID discards information; parsing a string may fail; opening a remote document has effects. Such arrows belong in a conversion or effect category, not an e-graph equivalence class.

Likewise, two domain objects should not be merged merely because one query currently cannot distinguish them. Semantic identity is an application contract, not an optimizer discovery.

The main risks are:

- rewrite explosion;
- unsound equations hidden in convenient rewrites;
- expensive extraction;
- difficulty explaining conditional equalities;
- mixing equivalence with directed translation.

E-graphs are therefore an optional optimizer and reasoning engine, not the primary identity store.

## 57. Statecharts, typestate, and session protocols

A selection operation has recognizable phases:

```text
Idle
  -> Selecting
      -> Resolving
          -> Completed
          -> Rejected
      -> Cancelled
```

A statechart makes these modes, nested states, and concurrent regions explicit. It is particularly useful for interaction policy:

- only one pointer-selection context owns global Escape;
- a remote lookup can run concurrently with visual highlighting;
- cancellation propagates to child activities;
- a conflict dialog suspends but does not discard the parent link workflow;
- completed contexts cannot resolve twice.

A typestate API can prevent invalid local calls:

```ts
const selecting: Selecting<Project> = context.start(query);
const resolving: Resolving<Project> = selecting.choose(project);
const complete: Completed<Project> = await resolving.commit();
```

Session types can extend the idea across a client/server boundary:

```text
client: ChooseRequest -> server
server: Candidates | Rejected -> client
client: Commit | Cancel -> server
server: Accepted | Stale -> client
```

The protocol can make omitted and out-of-order messages unrepresentable in generated clients.

### 57.1 Relationship to interaction trees

Statecharts provide a finite control structure and excellent visual inspection. Interaction trees provide compositional, recursively defined effectful programs and coinductive semantics. A practical system can compile a restricted workflow to a statechart or interpret statechart transitions as effects.

Statecharts become awkward when the control graph is highly data-dependent or built compositionally by plugins. Interaction trees become less immediately visual. Neither subsumes the other in every engineering dimension.

## 58. Event sourcing and materialized projections

A command kernel naturally supports event sourcing:

```text
Command + CurrentState -> Rejection | Events
CurrentState + Events  -> NextState
```

Durable events provide:

- replay;
- auditability;
- temporal queries;
- deterministic reconstruction;
- undo implemented through compensating commands or branch history;
- independently maintained projections for React, search, and analytics.

The presentation fact database can be a materialized projection of the event log. Incremental rules then update actions, candidates, and link classes as events arrive.

Event sourcing does not by itself prove correctness. Event schemas can be ambiguous, projections can diverge, and irreversible external effects need idempotency protocols. It is a persistence and integration architecture that fits the pure transition layer.

## 59. CRDTs and local-first collaboration

For a multi-user workspace, some state can use conflict-free replicated data types.

Examples include:

- an observed-remove set of explicit link edges;
- a grow-only set of provenance records;
- a semilattice of discovered capabilities or cached facts;
- a multi-value or last-writer-wins register for a document selection;
- a sequence CRDT for ordered placements.

A CRDT supplies convergence only when its algebraic conditions and network assumptions hold. It does not automatically preserve every application invariant.

### 59.1 Concurrent link and unlink

A plain set of pairs is insufficient. If one replica removes an edge while another concurrently re-adds it, the intended result depends on observed-remove, add-wins, or remove-wins semantics. The link protocol must choose and document one.

When an edge set converges, every replica can recompute the same quotient topology. Binding IDs should be derived canonically or treated as local alpha-renamed caches.

### 59.2 Values need their own replicated protocol

Topology convergence does not imply value convergence. A linked document cell may use:

- a last-writer-wins register, accepting clock assumptions and lost concurrent choices;
- a multi-value register, surfacing conflict;
- a causal register;
- a domain-specific join semilattice;
- a coordinated transaction when only one choice is valid.

Again, wiring and reconciliation remain separate.

### 59.3 The coordination boundary

Monotone accumulation often tolerates asynchronous replication. Operations involving negation, uniqueness, revocation, or exclusive ownership generally require coordination or a more carefully designed invariant-preserving protocol.

The fixed-point type classification can expose this boundary. A rule that only adds facts through joins is a better candidate for local-first execution than a rule saying “enable this action only if no conflicting lease exists.”

## 60. Schema categories and functorial migration

As semantic modules evolve, persistence requires more than JSON version switches. A categorical database model treats a schema as a category and an instance as a set-valued functor. A schema mapping can induce canonical migration operations corresponding broadly to restriction, data generation, and aggregation/join behavior.

For PBUI, this viewpoint could organize:

- renaming a sort while preserving entity references;
- splitting one relation into normalized relations;
- importing a plugin's schema into the application schema;
- projecting a complete workspace into a portable bundle schema;
- combining data from independently versioned modules;
- specifying round-trip expectations for lossy and lossless migrations.

A practical API might expose a simpler migration DSL while compiling it to a categorical model:

```ts
const v3ToV4 = migration.define({
  source: WorkspaceV3,
  target: WorkspaceV4,
  map: {
    View: preserveEntity(ViewV3, ViewV4),
    documentBinding: generateFrom(view => singleton(view.id)),
  },
});
```

The benefit is compositionality: migration from version 3 to 5 should agree with composing migrations 3 to 4 and 4 to 5, subject to explicitly declared information loss.

This machinery is powerful but should be introduced when schema evolution and plugin interoperability justify it. It is not needed to render the first presentation.

## 61. Attribute grammars

An attribute grammar computes information over a syntax or component tree using:

- synthesized attributes flowing upward;
- inherited attributes flowing downward;
- dependency equations among attributes.

This is an attractive alternative for semantics that follow the render or component tree:

- inherited interaction context;
- synthesized action summaries;
- accessibility metadata;
- layout constraints;
- local command scope;
- incremental recomputation after subtree changes.

The weakness is cross-cutting graph structure. A chart linked to a pipeline in another branch is no longer naturally tree-local. Reference attributes and circular attribute grammars can express such relationships, but a relational/link-graph runtime is often clearer.

A hybrid can use attribute-grammar techniques inside one component interpreter and relational rules across components.

## 62. Capability machines and object-capability design

An object-capability architecture represents authority through possession of unforgeable references rather than through globally queried role names. A command might require a capability object obtained from a trusted handler:

```ts
interface ArchiveCapability {
  archive(project: ProjectId): CommandToken;
}
```

This can strengthen plugin isolation:

- a plugin receives only capabilities it may exercise;
- effects are mediated by capability-bearing handlers;
- ambient authority is reduced;
- tests can supply limited mock capabilities.

The relational rule layer can still derive *availability* from capabilities. The command kernel should validate the actual authority token.

Object capabilities and proof-relevant authorization are complementary. The former constrains who can name an operation; the latter records why a particular operation is valid in the current state.

---

# Part VIII — Performance and operational design

## 63. Performance follows from semantic classification

The system should not promise one optimization strategy for every definition. It should compile according to classified structure.

| Definition class | Available optimizations |
|---|---|
| exact sort query | direct sort index |
| equality predicate on indexed attribute | hash lookup |
| positive relational query | join planning and incremental maintenance |
| monotone recursive rules | worklist or differential fixed point |
| stratified negation | per-stratum recomputation or supported incremental negation |
| lawful optic | focused state patch and local invalidation |
| equality-link addition | union–find merge |
| link deletion | affected-component dynamic connectivity or local recomputation |
| selective workflow | prefetch and static effect summary |
| opaque predicate with declared dependencies | candidate pruning plus callback evaluation |
| completely opaque callback | conservative invalidation and direct execution |

The architecture's value is not that all code becomes fast. It is that the compiler knows which optimization theorem is applicable.

## 64. Candidate indexing

Mounted occurrences should be indexed by:

```text
sort
semantic entity key
surface
component and port
visibility/reachability class
selected indexed attributes
```

An input context first narrows by sort and surface, then executes the compiled predicate. It should not invoke an arbitrary lambda against every presentation on every render.

For semantic candidates that are not mounted, repositories and relation indexes provide a separate source. This keeps pointer selection and command-palette search distinct while reusing the same underlying query.

## 65. Incremental rule evaluation

Base fact changes are deltas:

```ts
type FactDelta =
  | { tag: "insert"; fact: Fact }
  | { tag: "remove"; fact: Fact };
```

A worklist propagates only affected tuples. Positive recursive rules use semi-naive evaluation. Differential techniques can attach integer multiplicities or timestamped differences so additions and retractions flow through nested iteration.

The runtime should expose operational metrics:

```text
facts inserted/removed
rules activated
join tuples examined
fixed-point rounds
provenance nodes retained
queries invalidated
opaque predicates invoked
React subscribers notified
```

Without these measurements, a mathematically elegant engine can become an opaque performance problem.

## 66. Retractions and non-monotone features

User interfaces remove facts constantly:

- occurrences unmount;
- capabilities are revoked;
- documents close;
- links disappear;
- fields are deleted;
- remote responses supersede optimistic state.

A truth-maintenance or differential runtime must know whether a derived fact has another remaining derivation. Reference counts suffice only when derivations are appropriately represented. Recursive provenance can require dependency graphs or recomputation of an affected strongly connected region.

Negation is more expensive because inserting a fact can invalidate conclusions derived from its absence. The compiler should isolate negation in strata and report broad invalidation frontiers rather than silently degrading.

## 67. Link-graph algorithms

For predominantly additive local sessions:

- use union–find for equality-link additions;
- retain explicit edges durably;
- maintain class-to-value and endpoint-to-class indexes.

For occasional deletion, recomputing the affected component with breadth-first search is often simpler and sufficiently fast. Fully dynamic connectivity structures are justified only for very large, frequently edited link graphs.

The reference implementation should always be the obvious graph algorithm. Optimized caches are compared to it.

## 68. Provenance budgets

Full provenance can dominate memory. The runtime should support explicit modes:

```ts
type ProvenanceMode =
  | "none"
  | "dependency-set"
  | "one-derivation"
  | "all-derivations"
  | "certificate-only";
```

Authorization and command preconditions may require certificate-grade evidence. Decorative tones may need no provenance. A development inspector may request all derivations temporarily.

## 69. Scheduling and consistency

A semantic revision identifies a coherent snapshot. Queries and action derivations should not mix arbitrary repository revisions.

Possible policies include:

- synchronous local transactions;
- immutable snapshots with atomic publication;
- multi-version concurrency control;
- eventual observations with explicit staleness;
- suspense-like pending values in the React adapter.

The API should expose consistency rather than hiding it:

```ts
type Observation<A> =
  | { tag: "current"; revision: Revision; value: A }
  | { tag: "stale"; revision: Revision; value: A; refreshing: true }
  | { tag: "pending"; since: Revision }
  | { tag: "failed"; error: SemanticError };
```

A proof about one revision does not automatically hold after an asynchronous update.

## 70. Worker and server execution

Reified queries and codecs can cross process boundaries. The compiler can partition a plan:

```text
browser:
  mounted occurrence facts
  pointer reachability
  immediate visual state

worker:
  large relational joins
  recursive closure
  provenance compression

server:
  authoritative capabilities
  durable commands
  shared workspace state
```

Opaque host functions pin their containing subplan to the process that owns the code and environment. This is another reason to mark them explicitly.

## 71. React subscription discipline

A component should subscribe to the smallest observation key:

```text
occurrence observation by occurrence ID
action set by subject/context pair
binding value by binding class
query result by compiled query and parameter tuple
```

The semantic runtime publishes immutable snapshots or fine-grained signals. React's rendering frequency should not determine semantic recomputation frequency.

Concurrent rendering may call component functions speculatively. Therefore, registration and command effects belong in commit-safe hooks and idempotent runtime operations. Query construction should be pure.

---
EOF
wc -l -w /mnt/data/PRESENTATION-SYSTEMS-BEYOND-CLIM.md
```

<details><summary>💭 Thinking</summary>

**Appended architectural directions on e-graphs**

</details>

```json
{"search_query":[{"q":"site:arxiv.org \"Constructing Initial Algebras Using Inflationary Iteration\""},{"q":"site:arxiv.org \"Initial Algebras Unchained\" Wissmann Milius"},{"q":"site:arxiv.org Datafun Arntzenius Krishnaswami"},{"q":"site:arxiv.org \"A Theory of Changes for Higher-Order Languages\""}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Searched 8 websites**

</details>

```unknown
bash -lc cat >> /mnt/data/PRESENTATION-SYSTEMS-BEYOND-CLIM.md <<'EOF'
# Part IX — Migration from the current PBUI

## 72. Preserve the useful parts

The current implementation already contains several sound separations:

- semantic references are distinct from rendered children;
- verbs are serializable data rather than arbitrary side effects;
- a provider scopes transient input state;
- product code exposes a narrow environment rather than the complete store;
- logical views are distinct from workspace placements;
- acceptance is dynamically contextual rather than permanently attached to one widget.

A migration should preserve those gains. The goal is not a large rewrite from “CLIM-like” to “categorical.” It is to move semantic responsibility from opaque callbacks and component lifetime into compiled definitions and a small kernel.

## 73. Concept mapping

| Current concept | Proposed successor | Migration note |
|---|---|---|
| `PresentationReference<Values>` | `Entity<Sort>` or typed value subject | retain a compatibility wrapper |
| descriptor type-name key | nominal `Sort` declaration | generate old names from sort names |
| descriptor label/description | observation interpreter or display rule | simple descriptors can remain sugar |
| descriptor actions | contextual action rules | compile local actions as highest-priority rules |
| `AcceptRequest.types` | `query.from(sort)` | exact type query is a trivial plan |
| `AcceptRequest.filter` | predicate AST or `opaqueWhere` | wrap legacy callbacks explicitly |
| conversions | typed directed translation declarations | do not treat lossy conversions as equality |
| `createPresentationRegistry` | immutable compiled module/application | offer a registry façade during migration |
| PBUI provider | runtime/handler adapter | keep React context as dependency injection |
| `Presentation` component | semantic occurrence adapter | preserve visual API where possible |
| application verb | declared command input | existing serializable unions migrate well |
| `AppView.documents` | component state focused by typed document ports | initially derive ports from existing fields |
| view linking by shared ID | explicit link-edge graph and binding cells | distinguish linked view, linked placement, and linked port |

## 74. Phase 0: state the invariants first

Before replacing APIs, encode the current intended behavior as tests and models:

- selecting an acceptable occurrence resolves once;
- Escape aborts only the owning context;
- descriptor-local action order is stable;
- conversion selection is deterministic;
- duplicate placements preserve the intended view relationship;
- portable import freshens runtime IDs;
- document changes affect exactly the intended logical views.

These tests become the observational contract for compatibility interpreters.

## 75. Phase 1: introduce nominal sorts and identities

Add sort declarations behind the existing registry:

```ts
const Field = sort.define<FieldRef>({
  name: "datalab/Field",
  key: field => [field.docId, field.name],
});
```

`PresentationReference` can temporarily carry both the legacy type and the new sort token:

```ts
interface LegacyCompatibleReference<A> {
  readonly type: string;
  readonly sort: Sort<A>;
  readonly key: Key;
  readonly value: A;
}
```

This phase produces immediate value:

- consistent semantic identity;
- cross-occurrence matching;
- typed conversion endpoints;
- stable indexes;
- property tests for equality laws.

No fixed-point engine is required yet.

## 76. Phase 2: add the query AST beside filters

Translate simple acceptance requests automatically:

```ts
accept({ types: "field" })
```

becomes:

```ts
chooseOne(query.from(Field))
```

A legacy filter becomes:

```ts
query.from(Field).opaqueWhere({
  id: generatedStableId,
  reads: "unknown",
  stability: "call",
  evaluate: legacyFilter,
});
```

New features use expression predicates. The compiler can report the opaque percentage of each workflow and the optimization consequences.

## 77. Phase 3: make commands a pure kernel

Existing verbs are already close to command data. Add:

- codecs;
- explicit preconditions;
- pure decision functions;
- event/effect separation;
- revision checking.

Initially, the command handler may dispatch the old Redux action after validation. Later, the Redux reducer can become a projection or interpreter of the command result.

This phase should precede proof-relevant menus. It ensures that a forged or stale action still cannot bypass invariants.

## 78. Phase 4: compile immutable modules

Convert descriptor registration into module definitions. A compatibility compiler produces the old registry interface for components not yet migrated.

```text
module definitions
  -> composition checks
  -> compiled schema/query/rule tables
  -> legacy registry façade
  -> new runtime plan
```

This removes import-order dependence and creates one artifact that can be inspected, serialized in metadata, or compared across builds.

## 79. Phase 5: introduce ports and explicit link edges

Start with document selection because it has a concrete product requirement.

1. expose a typed `primaryDocument` port for chart and pipeline views;
2. derive its value from the existing `documents.primary` field through an optic;
3. store explicit link edges in workspace state;
4. compute binding classes from those edges;
5. route `setViewDocument` through `SetPortValue`;
6. preserve old workspaces by treating every unlinked port as a singleton class;
7. export topology without depending on runtime binding IDs.

This can coexist with the current layout model. It does not require the relational action engine.

## 80. Phase 6: move applicability into rules

Compile descriptor actions into facts and rules, then migrate cross-cutting actions:

```text
descriptor-local "inspect"
  -> generated direct rule

administrator archive action
  -> capability + state rule

link target highlighting
  -> port compatibility + occurrence reachability rule
```

Run the old and new applicability engines in shadow mode. Differences become diagnostics before the new engine controls visible behavior.

## 81. Phase 7: incrementalize

Only after reference semantics are stable should the system add:

- query indexes;
- semi-naive recursive evaluation;
- provenance compression;
- worker execution;
- union–find caches;
- fine-grained React subscriptions.

Every optimization ships with a differential test against the reference evaluator.

## 82. Phase 8: formalize the kernel

Formalize the smallest stable core, not the rapidly changing product surface:

- query and predicate syntax;
- fixed-point rules;
- evidence checker;
- command transitions;
- link quotient and reconciliation protocols;
- workflow event signature.

Export test vectors from the formal model or run both models over generated examples. The proof effort then protects the architectural substrate while normal product development continues in TypeScript.

## 83. Compatibility and deprecation policy

A multi-year migration needs visible classifications:

```ts
runtime.inspectDefinition(definition)
// {
//   representation: "reified" | "opaque",
//   serializable: boolean,
//   monotonicity: "proven" | "declared" | "unknown",
//   incremental: "compiled" | "coarse" | "none",
//   provenance: "complete" | "conditional" | "none"
// }
```

Deprecation should target guarantee gaps rather than syntax age. A well-contained opaque visual heuristic may remain acceptable indefinitely. An opaque authorization predicate should not.

---

# Part X — Recommendation

## 84. The recommended decomposition

The most defensible architecture is a **stratified semantic runtime** with six independent but composable structures:

1. **Initial syntax:** reified schemas, queries, predicates, rules, commands, and effect operations.
2. **Fixed-point knowledge:** a monotone or stratified relational closure with provenance.
3. **Pure transition kernel:** commands decide state changes, events, and effects under checked preconditions.
4. **Open wiring graph:** typed component ports, explicit link generators, quotient topology, and separate reconciliation algebras.
5. **Coalgebraic interaction:** potentially unbounded workflows interpreted by handlers and reasoned about through traces.
6. **Adapter interpreters:** React, persistence, workers, remote protocols, tests, and formal models.

Lenses attach ports to state. Incremental computation accelerates query, rule, and observation evaluation. Capabilities constrain effects. These are supporting structures, not additional universal layers.

## 85. Why not choose one family exclusively?

A purely relational system handles derived facts elegantly but is awkward for ordered asynchronous workflows. A pure effect system models workflows but does not automatically index thousands of mounted objects. A pure FRP graph handles changing values but does not explain command authorization. A pure lens architecture handles focus but not dynamic multi-party wiring. A cospan model composes boundaries but does not choose values. A state machine controls phases but does not provide a query optimizer.

The hybrid is not eclecticism for its own sake. Each layer has a different shape of reasoning:

| Concern | Structure | Proof method |
|---|---|---|
| finite definitions | initial algebra / AST | structural induction |
| recursive derived facts | complete lattice + monotone operator | fixed-point or transfinite induction |
| continuing behavior | coalgebra / transition system | coinduction, simulation, temporal logic |
| wiring | colimits and quotients | universal properties |
| focused update | lenses/optics | algebraic laws |
| effects | free syntax and handlers | homomorphism/equational reasoning |
| optimization | incremental change structures | refinement/equivalence |

Trying to force these concerns into one abstraction generally obscures the proof obligations.

## 86. What the application author should see

Most feature code should need four concepts:

```ts
sort.define(...)
query.from(...).where(...)
command.define(...)
workflow.define(...)
```

Component authors additionally use:

```ts
component.define(...)
port.cell(...)
<SemanticOccurrence ... />
```

Rule and categorical APIs are infrastructure or advanced-feature tools. Generated helpers and domain-specific builders should hide raw AST constructors.

The application author should not manipulate ordinals, lattice proofs, colimit cocones, or profunctor encodings. Those structures justify and organize the implementation; they are not ergonomic UI primitives.

## 87. Proof profiles as first-class metadata

Every compiled definition should expose a guarantee profile:

```ts
interface ProofProfile {
  readonly syntax: "reified" | "opaque";
  readonly purity: "pure" | "effectful" | "unknown";
  readonly monotonicity: "monotone" | "stratified" | "nonmonotone" | "unknown";
  readonly serialization: "portable" | "process-local";
  readonly incrementality: "derivable" | "declared-dependencies" | "none";
  readonly explanation: "proof-relevant" | "dependency-only" | "none";
  readonly authorityUse: "none" | "hint-only" | "security-critical";
}
```

The compiler checks combinations. For example:

- `security-critical` plus `opaque` is rejected;
- a process-local query cannot be persisted as a workflow definition;
- a recursive negative rule requires stratification or an explicit well-founded semantics;
- a replicated merge requires declared algebraic laws and tests;
- a worker plan cannot contain a browser-only callback.

This turns proof-friendliness into an enforceable API property.

## 88. A minimal first implementation

The smallest useful slice is not a Datalog engine or theorem prover. It is:

1. nominal sorts and entity keys;
2. a small query AST for sort, equality, conjunction, relation traversal, and mounted-occurrence conditions;
3. an explicit `opaqueWhere` escape hatch;
4. pure command declarations with precondition rechecking;
5. typed component ports and an equality-link graph;
6. a reference interpreter;
7. React occurrence registration;
8. property tests for identities, queries, link quotient, codecs, and commands.

Then add, in order:

- action rules without recursion;
- provenance;
- incremental indexes;
- recursive fixed-point rules;
- interaction-tree workflows;
- distributed and formal interpreters.

This order delivers the document-linking feature early while preserving a path to the more ambitious semantics.

## 89. Anti-patterns to avoid

### 89.1 Category-theory vocabulary without laws

Calling actions morphisms or providers monads creates no value unless composition and identity laws are stated and tested.

### 89.2 One giant universal graph

Entities, occurrences, effects, commands, ports, and React nodes can all be represented as graph data. That does not mean they should share one untyped edge relation. Typed relations and layer boundaries are essential.

### 89.3 Arbitrary callbacks disguised as proof objects

A branded TypeScript token saying `Monotone` does not prove that an arbitrary callback is monotone. Accept such properties as explicit trust assumptions or verify a reified syntax.

### 89.4 Transfinite runtime theater

Do not introduce ordinal counters into the browser because the metatheory mentions transfinite chains. Compile the active finite or continuous case and retain the general theorem in the model.

### 89.5 Destructive union as durable link state

Union–find forgets generating edges. It cannot correctly explain or delete links by itself. Persist the graph; cache the quotient.

### 89.6 Colimits as conflict-resolution magic

A pushout or coequalizer identifies interfaces. It does not decide which user's document selection wins.

### 89.7 Visibility as security

The absence of an action from a menu is not authorization. Commands recheck authority in the trusted kernel or server.

### 89.8 React as the database

Unmounting an occurrence should not delete the domain entity, command, or logical link. The DOM is one surface over semantic state.

### 89.9 Global completeness claims

An architecture with opaque plugins should say which properties are unconditional and which assume plugin contracts. Partial formal assurance is still valuable when its boundary is explicit.

## 90. Open research questions for this project

Several questions deserve prototypes rather than immediate standardization:

1. **Query equality:** should optimization use a hand-proved rewrite set, an e-graph, or a conventional relational planner?
2. **Rule language:** is stratified Datalog sufficient, or do lattice-valued aggregates and higher-order monotone functions justify a Datafun/Flix-like core?
3. **Context indexing:** should users, workspaces, permissions, and surfaces remain explicit query parameters, or should the type system index judgments by context?
4. **Bidirectional links:** which port protocols need lenses, symmetric lenses, multi-value cells, or explicit conflict states?
5. **Plugin composition:** how are rule-name, schema, and effect-signature conflicts diagnosed across independently versioned packages?
6. **Distributed topology:** what are the precise add/remove semantics for concurrent link edits?
7. **Evidence transport:** should a server accept compact client certificates, or only re-evaluate command preconditions?
8. **Identity migration:** how are semantic keys preserved when a document or schema is imported, forked, or merged?
9. **Incremental provenance:** which explanation mode provides enough diagnostics without dominating memory?
10. **Formal implementation path:** is extraction from a proof assistant practical, or is a verified reference model plus differential testing the better cost/benefit point?
11. **Accessibility semantics:** can occurrence reachability and command availability be modeled once and interpreted coherently for pointer, keyboard, screen reader, and voice surfaces?
12. **Undo:** should undo replay inverse commands, restore snapshots, manipulate event branches, or apply provenance-aware graph rewrites?

## 91. Final assessment

A modern presentation-based system should not be organized primarily around “an object has a presentation type and translators.” That remains a useful surface metaphor, but the deeper architecture is richer:

```text
semantic objects and relations
        ↓
reified queries and recursive rules
        ↓
proof-relevant, incrementally maintained observations
        ↓
typed open components connected by explicit wiring
        ↓
effectful workflows issuing checked state transitions
        ↓
React and other interpreters
```

This decomposition makes powerful dynamic behavior possible without making all semantics dynamic and opaque. It supports ordinary TypeScript development today, more aggressive indexing and distribution later, and meaningful formal claims where the product warrants them.

The most important design rule is simple:

> Reify what must be composed, optimized, serialized, explained, or proved. Keep unrestricted host-language code at a visible boundary. Use induction for finite definitions, fixed points for recursive knowledge, coinduction for ongoing behavior, colimits for wiring, and explicit algebras for value resolution.

---

# Appendix A — Glossary

**Action**  
A user-visible opportunity to issue a command, normally derived from subject, context, capability, and occurrence facts.

**Algebraic effect**  
An abstract operation represented in a program independently of the handler that interprets it.

**Binding class**  
An equivalence class of linked compatible ports.

**Coalgebra**  
A structure describing observable unfolding or transitions; useful for streams, machines, and ongoing interaction.

**Colimit**  
A universal construction that glues a diagram together. Coproducts, pushouts, and coequalizers are examples.

**Command**  
Serializable intent checked and interpreted by the pure transition kernel.

**Component**  
A semantic state machine with typed ports and observations, independent of a particular renderer.

**Context**  
An explicit parameter bundle such as current user, workspace, capabilities, surface, and active workflow.

**Derivation**  
A rule application tree or DAG that justifies a derived fact.

**Entity**  
A semantic subject identified by a nominal sort and stable key.

**Evidence**  
A checkable certificate that a judgment or command precondition holds at a specified revision.

**Fixed point**  
A value `X` satisfying `F(X) = X`. Least fixed points commonly define recursive positive rules.

**Interaction tree**  
A coinductive representation of recursive effectful behavior using abstract events and continuations.

**Lens**  
A lawful pair of read and update operations focusing a larger state onto a part.

**Occurrence**  
A mounted or otherwise addressable visual presentation of a semantic subject.

**Opaque definition**  
A host-language callback whose semantics cannot be fully inspected by the compiler.

**Optic**  
A composable abstraction for bidirectional access patterns, including lenses, prisms, and traversals.

**Placement**  
A visual location that presents a logical view.

**Port**  
A typed component boundary that can participate in a declared connection protocol.

**Presentation**  
A relationship between a semantic subject and a visual occurrence; not necessarily the primary organizing abstraction of the runtime.

**Provenance**  
Information recording which source facts and rule applications contributed to a result.

**Query**  
A reified, typed description of a collection or relation-valued computation.

**Reconciliation algebra**  
A policy or lawful operation that resolves multiple value proposals for a connected binding.

**Rule**  
A declarative implication deriving facts from facts.

**Sort**  
A nominal semantic type with identity, codec, and relation participation.

**Stratification**  
An ordering of rule groups that prevents problematic cycles through negation or non-monotone operators.

**Workflow**  
An effectful interaction program that can request selection, issue commands, wait, cancel, and handle conflict.

---

# Appendix B — Construction map

| Architectural object | Mathematical model | Engineering use |
|---|---|---|
| query/predicate syntax | initial algebra | folds, compilers, structural induction |
| extensible query interface | tagless-final algebra or modular signature | plugin interpreters and ergonomic builders |
| recursive action facts | least fixed point on fact lattice | applicability and capability closure |
| general closure construction | ordinal-indexed chain / inflationary iteration | metatheory for infinitary cases |
| workflow | free effect syntax / interaction tree | handler-independent interaction |
| runtime behavior | coalgebra or labeled transition system | traces, simulation, liveness |
| document-port links | coequalizer / quotient | binding classes |
| composition of open components | pushout / structured cospan | wiring modules through boundaries |
| focused component state | lens or optic | lawful local read/update |
| change propagation | change action / derivative / differential collection | incremental maintenance |
| query provenance | semiring or proof term | explanation, invalidation, trust |
| conversion costs | weighted category or enriched graph | deterministic plan selection |
| semantic equivalence rewrites | congruence / e-graph | equality saturation and extraction |
| schema version mapping | functor and Kan-extension-like migration | portable data evolution |
| replicated monotone state | join-semilattice / CRDT | local-first convergence |
| authorization | capability + proof-relevant judgment | least authority and checked commands |

---

# Appendix C — End-to-end sketch

The following condensed example shows how the proposed layers fit together. It is illustrative API design, not a claim that the current repository already exports these symbols.

```ts
// 1. Semantic schema
const Document = sort.define<Document>({
  name: "core/Document",
  key: document => document.id,
  codec: documentCodec,
});

const currentDocument = relation.attribute(Document, DocumentId, {
  name: "core/currentDocument",
});

// 2. Typed query
const availableDocument = query
  .from(Document)
  .where(eq(Document.attr("deleted"), literal(false)));

// 3. Command
const SetDocumentPort = command.define({
  name: "workspace/SetDocumentPort",
  input: struct({
    endpoint: PortEndpointId,
    document: Document.keyCodec,
    expectedRevision: Revision,
  }),
  requires: CanWritePort,
  decide: setDocumentPortTransition,
});

// 4. Components
const Chart = component.define({
  name: "charts/Chart",
  state: ChartState,
  ports: {
    document: port.cell(Document, {
      protocol: "equality",
      mode: "read-write",
      focus: chartDocumentLens,
    }),
  },
});

const Pipeline = component.define({
  name: "pipelines/Pipeline",
  state: PipelineState,
  ports: {
    document: port.cell(Document, {
      protocol: "equality",
      mode: "read-write",
      focus: pipelineDocumentLens,
    }),
  },
});

// 5. Rule
const LinkTarget = rule.define({
  name: "workspace/LinkTarget",
  when: all(
    Port.compatible(variable("source"), variable("target")),
    Context.hasCapability(variable("context"), LinkWorkspacePorts),
    Occurrence.mountedFor(variable("target")),
  ),
  derive: Candidate.linkTarget({
    source: variable("source"),
    target: variable("target"),
  }),
});

// 6. Workflow
const linkDocuments = workflow.define("workspace/LinkDocuments", function* (source) {
  const target = yield* effect.chooseOne(
    query.fromRule(LinkTarget).parameter("source", source),
    { prompt: "Choose a document selector" },
  );

  yield* effect.issue(LinkPorts({
    left: source,
    right: target.endpoint,
    reconciliation: { tag: "prefer", endpoint: source },
    authorization: target.evidence,
  }));
});

// 7. React adapter
function DocumentSelector({ endpoint }: { endpoint: PortEndpointId }) {
  const observation = usePort(endpoint);
  const start = useWorkflow(linkDocuments);

  return (
    <SemanticOccurrence subject={PortEndpoint.entity(endpoint)}>
      <select
        value={observation.value}
        onChange={event => observation.set(event.currentTarget.value)}
      >
        {/* options from an observed query */}
      </select>
      <button onClick={() => start(endpoint)}>Link</button>
    </SemanticOccurrence>
  );
}
```

---
EOF
wc -l -w /mnt/data/PRESENTATION-SYSTEMS-BEYOND-CLIM.md
```

<details><summary>💭 Thinking</summary>

**Documented PBUI migration recommendations with citation sources and context**

</details>

```json
{"search_query":[{"q":"site:arxiv.org \"Adapton: Composable, Demand-Driven Incremental Computation\""},{"q":"\"Incremental Lambda Calculus in Cache-Transfer Style\" Giarrusso arxiv"},{"q":"site:cidrdb.org CIDR 2013 Differential Dataflow McSherry Murray Isaacs Isard"},{"q":"site:arxiv.org \"Selective Applicative Functors\" Mokhov Lukyanov Marlow"}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Appending references**

I’m finishing the standalone study with a curated bibliography, then I’ll validate its structure and provide the completed Markdown document. The references will support the architectural comparisons without turning the design into a literature survey.

**Searched 11 websites**

</details>

```unknown
bash -lc set -euo pipefail
DOC=/mnt/data/PRESENTATION-SYSTEMS-BEYOND-CLIM.md
wc -l -w -c "$DOC"
tail -n 120 "$DOC"
```

<details><summary>💭 Thinking</summary>

**Inspected presentation systems document structure and headings**

</details>

```json
{"search_query":[{"q":"site:arxiv.org/abs/2105.03252 Constructing Initial Algebras Using Inflationary Iteration"},{"q":"site:arxiv.org/abs/2405.09504 Initial Algebras Unchained"},{"q":"site:projecteuclid.org Tarski lattice-theoretical fixpoint theorem 1955"},{"q":"site:di.ens.fr Cousot Cousot POPL 1977 abstract interpretation fixpoints"}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Searched 13 websites**

</details>

```unknown
bash -lc python - <<'PY'
import re
from pathlib import Path
p=Path('/mnt/data/PRESENTATION-SYSTEMS-BEYOND-CLIM.md')
text=p.read_text()
refs=[]
for m in re.finditer(r'\[([^\]\n]+(?:19|20)\d{2}[^\]\n]*)\]', text):
    s=m.group(1)
    if not s.startswith('^') and not s.startswith('['): refs.append(s)
for r in sorted(set(refs)):
    print(r)
PY
```

<details><summary>💭 Thinking</summary>

**Extracted citation labels and inspected bibliography coverage**

</details>

```json
{"search_query":[{"q":"site:dl.acm.org A Theory of Changes for Higher-Order Languages 2014 DOI"},{"q":"site:dl.acm.org Adapton Composable Demand-Driven Incremental Computation 2014 DOI"},{"q":"site:arxiv.org Incremental lambda calculus cache-transfer style 2019"},{"q":"site:cidrdb.org Differential Dataflow CIDR 2013 PDF"}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Searched 3 websites**

</details>

```unknown
bash -lc set -euo pipefail
DOC=/mnt/data/PRESENTATION-SYSTEMS-BEYOND-CLIM.md
python - <<'PY'
from pathlib import Path
p=Path('/mnt/data/PRESENTATION-SYSTEMS-BEYOND-CLIM.md')
text=p.read_text()
replacements={
"An e-graph compactly represents a congruence relation over many expressions. Equality saturation repeatedly applies sound rewrites without committing to one sequence; an extraction phase later chooses a representative according to a cost model.":
"An e-graph compactly represents a congruence relation over many expressions. Equality saturation repeatedly applies sound rewrites without committing to one sequence; an extraction phase later chooses a representative according to a cost model [Willsey et al. 2021; Zhang et al. 2023].",
"A statechart makes these modes, nested states, and concurrent regions explicit. It is particularly useful for interaction policy:":
"A statechart makes these modes, nested states, and concurrent regions explicit [Harel 1987]. It is particularly useful for interaction policy:",
"For a multi-user workspace, some state can use conflict-free replicated data types.":
"For a multi-user workspace, some state can use conflict-free replicated data types [Shapiro et al. 2011].",
"As semantic modules evolve, persistence requires more than JSON version switches. A categorical database model treats a schema as a category and an instance as a set-valued functor. A schema mapping can induce canonical migration operations corresponding broadly to restriction, data generation, and aggregation/join behavior.":
"As semantic modules evolve, persistence requires more than JSON version switches. A categorical database model treats a schema as a category and an instance as a set-valued functor. A schema mapping can induce canonical migration operations corresponding broadly to restriction, data generation, and aggregation/join behavior [Spivak 2012].",
"An attribute grammar computes information over a syntax or component tree using:":
"An attribute grammar computes information over a syntax or component tree using [Knuth 1968]:",
"An object-capability architecture represents authority through possession of unforgeable references rather than through globally queried role names. A command might require a capability object obtained from a trusted handler:":
"An object-capability architecture represents authority through possession of unforgeable references rather than through globally queried role names [Miller 2006]. A command might require a capability object obtained from a trusted handler:",
}
for old,new in replacements.items():
    if old not in text:
        raise SystemExit(f'missing replacement target: {old[:80]}')
    text=text.replace(old,new,1)
p.write_text(text)
PY
cat >> "$DOC" <<'EOF'

# Appendix D — Selected primary references

The references below are intentionally weighted toward primary research papers and formal source material. They are not a comprehensive survey of category theory, programming-language semantics, databases, distributed systems, or formal verification.

- **[Arntzenius & Krishnaswami 2016]** Michael Arntzenius and Neelakantan R. Krishnaswami. “Datafun: A Functional Datalog.” *Proceedings of the 21st ACM SIGPLAN International Conference on Functional Programming*, 2016, pp. 214–227. [DOI](https://doi.org/10.1145/2951913.2951948).
- **[Baez & Courser 2020]** John C. Baez and Kenny Courser. “Structured Cospans.” *Theory and Applications of Categories* 35, 2020, pp. 1771–1822. [arXiv](https://arxiv.org/abs/1911.04630).
- **[Cai et al. 2014]** Yufei Cai, Paolo G. Giarrusso, Tillmann Rendel, and Klaus Ostermann. “A Theory of Changes for Higher-Order Languages: Incrementalizing Lambda Calculi by Static Differentiation.” *Proceedings of PLDI 2014*, pp. 145–155. [arXiv](https://arxiv.org/abs/1312.0658).
- **[Carette, Kiselyov & Shan 2009]** Jacques Carette, Oleg Kiselyov, and Chung-chieh Shan. “Finally Tagless, Partially Evaluated: Tagless Staged Interpreters for Simpler Typed Languages.” *Journal of Functional Programming* 19(5), 2009, pp. 509–543. [DOI](https://doi.org/10.1017/S0956796809007205).
- **[Clarke et al. 2024]** Bryce Clarke, Derek Elkins, Jeremy Gibbons, Fosco Loregian, Bartosz Milewski, Emily Pillmore, and Mario Román. “Profunctor Optics, a Categorical Update.” *Compositionality* 6, 2024. [arXiv](https://arxiv.org/abs/2001.07488).
- **[Cousot & Cousot 1977]** Patrick Cousot and Radhia Cousot. “Abstract Interpretation: A Unified Lattice Model for Static Analysis of Programs by Construction or Approximation of Fixpoints.” *Proceedings of POPL 1977*, pp. 238–252. [Author-hosted publication page](https://www.di.ens.fr/~cousot/COUSOTpapers/POPL77.shtml).
- **[Elliott & Hudak 1997]** Conal Elliott and Paul Hudak. “Functional Reactive Animation.” *Proceedings of ICFP 1997*. [DOI](https://doi.org/10.1145/258948.258973).
- **[Elliott 2009]** Conal M. Elliott. “Push-Pull Functional Reactive Programming.” *Proceedings of the 2nd ACM SIGPLAN Symposium on Haskell*, 2009. [DOI](https://doi.org/10.1145/1596638.1596643).
- **[Fong 2015]** Brendan Fong. “Decorated Cospans.” *Theory and Applications of Categories* 30(33), 2015, pp. 1096–1120. [arXiv](https://arxiv.org/abs/1502.00872).
- **[Foster et al. 2007]** J. Nathan Foster, Michael B. Greenwald, Jonathan T. Moore, Benjamin C. Pierce, and Alan Schmitt. “Combinators for Bidirectional Tree Transformations: A Linguistic Approach to the View-Update Problem.” *ACM Transactions on Programming Languages and Systems* 29(3), 2007. [DOI](https://doi.org/10.1145/1232420.1232424).
- **[Giarrusso et al. 2019]** Paolo G. Giarrusso, Yann Régis-Gianas, and Philipp Schuster. “Incremental Lambda Calculus in Cache-Transfer Style: Static Memoization by Program Transformation.” *Programming Languages and Systems — ESOP 2019*, LNCS 11423, pp. 553–580. [DOI](https://doi.org/10.1007/978-3-030-17184-1_20).
- **[Green, Karvounarakis & Tannen 2007]** Todd J. Green, Grigoris Karvounarakis, and Val Tannen. “Provenance Semirings.” *Proceedings of PODS 2007*, pp. 31–40. [DOI](https://doi.org/10.1145/1265530.1265535).
- **[Hammer et al. 2014]** Matthew A. Hammer, Khoo Yit Phang, Michael Hicks, and Jeffrey S. Foster. “Adapton: Composable, Demand-Driven Incremental Computation.” *Proceedings of PLDI 2014*, pp. 156–166. [DOI](https://doi.org/10.1145/2594291.2594324).
- **[Harel 1987]** David Harel. “Statecharts: A Visual Formalism for Complex Systems.” *Science of Computer Programming* 8(3), 1987, pp. 231–274. [DOI](https://doi.org/10.1016/0167-6423(87)90035-9).
- **[Jackson 2002]** Daniel Jackson. “Alloy: A Lightweight Object Modelling Notation.” *ACM Transactions on Software Engineering and Methodology* 11(2), 2002, pp. 256–290. [DOI](https://doi.org/10.1145/505145.505149).
- **[Knuth 1968]** Donald E. Knuth. “Semantics of Context-Free Languages.” *Mathematical Systems Theory* 2, 1968, pp. 127–145. [DOI](https://doi.org/10.1007/BF01692511).
- **[Lamport 1994]** Leslie Lamport. “The Temporal Logic of Actions.” *ACM Transactions on Programming Languages and Systems* 16(3), 1994, pp. 872–923. [DOI](https://doi.org/10.1145/177492.177726).
- **[Madsen, Yee & Lhoták 2016]** Magnus Madsen, Ming-Ho Yee, and Ondřej Lhoták. “From Datalog to Flix: A Declarative Language for Fixed Points on Lattices.” *Proceedings of PLDI 2016*, pp. 194–208. [DOI](https://doi.org/10.1145/2908080.2908096).
- **[McSherry et al. 2013]** Frank McSherry, Derek G. Murray, Rebecca Isaacs, and Michael Isard. “Differential Dataflow.” *Proceedings of CIDR 2013*. [Conference paper](https://www.cidrdb.org/cidr2013/Papers/CIDR13_Paper111.pdf).
- **[Miller 2006]** Mark S. Miller. *Robust Composition: Towards a Unified Approach to Access Control and Concurrency Control*. PhD dissertation, Johns Hopkins University, 2006. [Author-hosted dissertation](http://www.erights.org/talks/thesis/markm-thesis.pdf).
- **[Mokhov et al. 2019]** Andrey Mokhov, Georgy Lukyanov, Simon Marlow, and Jerémie Dimino. “Selective Applicative Functors.” *Proceedings of the ACM on Programming Languages* 3(ICFP), Article 90, 2019. [DOI](https://doi.org/10.1145/3341694).
- **[Pitts & Steenkamp 2021]** Andrew M. Pitts and S. C. Steenkamp. “Constructing Initial Algebras Using Inflationary Iteration.” arXiv preprint, 2021; published in *EPTCS* 372, 2022, pp. 88–102. [DOI](https://doi.org/10.4204/EPTCS.372.7).
- **[Plotkin & Pretnar 2013]** Gordon D. Plotkin and Matija Pretnar. “Handling Algebraic Effects.” *Logical Methods in Computer Science* 9(4:23), 2013. [DOI](https://doi.org/10.2168/LMCS-9(4:23)2013).
- **[Shapiro et al. 2011]** Marc Shapiro, Nuno Preguiça, Carlos Baquero, and Marek Zawirski. “A Comprehensive Study of Convergent and Commutative Replicated Data Types.” INRIA Research Report RR-7506, 2011. [HAL](https://inria.hal.science/inria-00555588).
- **[Spivak 2012]** David I. Spivak. “Functorial Data Migration.” *Information and Computation* 217, 2012, pp. 31–51. [arXiv](https://arxiv.org/abs/1009.1166).
- **[Tarski 1955]** Alfred Tarski. “A Lattice-Theoretical Fixpoint Theorem and Its Applications.” *Pacific Journal of Mathematics* 5(2), 1955, pp. 285–309. [DOI](https://doi.org/10.2140/pjm.1955.5.285).
- **[Willsey et al. 2021]** Max Willsey, Chandrakana Nandi, Yisu Remy Wang, Oliver Flatt, Zachary Tatlock, and Pavel Panchekha. “egg: Fast and Extensible Equality Saturation.” *Proceedings of the ACM on Programming Languages* 5(POPL), Article 23, 2021. [arXiv](https://arxiv.org/abs/2004.03082).
- **[Wißmann & Milius 2024]** Thorsten Wißmann and Stefan Milius. “Initial Algebras Unchained: A Novel Initial Algebra Construction Formalized in Agda.” *Proceedings of the 39th Annual ACM/IEEE Symposium on Logic in Computer Science*, 2024. [DOI](https://doi.org/10.1145/3661814.3662105).
- **[Xia et al. 2020]** Li-yao Xia, Yannick Zakowski, Paul He, Chung-Kil Hur, Gregory Malecha, Benjamin C. Pierce, and Steve Zdancewic. “Interaction Trees: Representing Recursive and Impure Programs in Coq.” *Proceedings of the ACM on Programming Languages* 4(POPL), Article 51, 2020. [DOI](https://doi.org/10.1145/3371119).
- **[Zhang et al. 2023]** Yihong Zhang, Yisu Remy Wang, Oliver Flatt, David Cao, Philip Zucker, Eli Rosenthal, Zachary Tatlock, and Max Willsey. “Better Together: Unifying Datalog and Equality Saturation.” *Proceedings of the ACM on Programming Languages* 7(PLDI), 2023, pp. 468–492. [arXiv](https://arxiv.org/abs/2304.04332).

---

## Closing note

A proof-oriented presentation system should not begin by asking which abstract mathematical vocabulary can be placed over a React API. It should begin by deciding which semantic facts must remain inspectable, compositional, incrementally maintainable, and independently verifiable. Inductive syntax, fixed-point semantics, coalgebraic workflows, lawful optics, and categorical wiring then become separate tools with explicit contracts. Their value lies in the laws they expose and the optimizations and proofs those laws permit—not in the sophistication of the terminology.
EOF

wc -l -w -c "$DOC"
tail -n 120 "$DOC"
```

<details><summary>💭 Thinking</summary>

**Validating and Finalizing Mathematics Markdown Document**

</details>

The substantive draft is complete; I’m finalizing citations and structural checks while preserving distinct proof methods and evaluating alternatives such as CRDTs, statecharts, and equality saturation.

# Second architecture study

[Download **Presentation-Based UI Architectures Beyond CLIM**](sandbox:/mnt/data/PRESENTATION-BASED-UI-ARCHITECTURES-BEYOND-CLIM.md)

A copy is also placed in the project documentation tree:

[Open the repository copy](sandbox:/mnt/data/pbui_source/pbui/docs/presentation-based-ui-architectures-beyond-clim.md)

The document is approximately 20,000 words and is designed as a companion to the first CLIM-oriented chapter. It does not assume that presentations, input contexts, translators, and command tables must remain the system’s fundamental decomposition.

## Central conclusion

The recommended architecture is a **layered semantic kernel**, rather than a direct modernization of CLIM:

```text
domain schema and identities
        ↓
typed facts and derived relations
        ↓
selection/query language
        ↓
capabilities and operations
        ↓
open components with typed ports
        ↓
explicit interaction machines and effect programs
        ↓
incremental runtime
        ↓
React occurrence adapter
```

This separates several concerns that are easy to conflate:

- what is true about an application object;
- whether an object satisfies a request;
- what authority is available over it;
- how components expose and consume semantic ports;
- how linked components synchronize;
- how interaction evolves over time;
- how results are incrementally maintained;
- how semantic objects happen to be rendered in React.

## Architectures studied

The document develops and compares eleven possible foundations:

1. **Typed relational and Datalog-style semantics**  
   Presentations and selections become facts, relations, and monotone queries. Recursive relations receive least-fixed-point semantics.

2. **Algebraic syntax and interpreters**  
   Queries, actions, and interaction programs are represented as typed syntax trees rather than opaque callbacks. Structural induction, normalization, multiple interpreters, and proof-producing compilation become possible.

3. **Algebraic specifications and institutions**  
   Components are described through signatures, theories, models, and satisfaction. This gives a language-independent account of whether an implementation satisfies an interface contract.

4. **Structured cospans and open systems**  
   A UI component is treated as a system with a typed boundary. Components compose by connecting ports rather than by importing each other’s stores.

5. **Coalgebra and statecharts**  
   Long-running interaction is modeled through observable state and transitions. Bisimulation and invariant-preservation arguments become more natural than trying to represent all behavior as a finite command list.

6. **Lenses and bidirectional transformations**  
   Linked views with unequal representations are modeled through explicit `get` and `put` laws rather than informal shared-state callbacks.

7. **FRP and guarded recursion**  
   Time, causality, feedback, and dynamic occurrence lifetimes become explicit parts of the semantics.

8. **Incremental and differential computation**  
   The optimized runtime maintains changes to query results instead of repeatedly evaluating all predicates against all mounted presentations.

9. **Semilattices, LVars, and CRDTs**  
   Monotone and distributed state are separated from ordinary mutable application state. This is relevant for local-first collaboration and replicated links.

10. **Algebraic effects and handlers**  
    Interaction programs describe effects such as selecting an object, requesting authority, linking ports, and committing an operation without directly depending on React, Redux, or a server transport.

11. **Presheaf and contextual semantics**  
    Availability under changing environments is modeled as a context-indexed family rather than as a single global Boolean property.

These sections draw on distinct research traditions rather than treating all categorical language as interchangeable. In particular, the study separates initial-algebra induction, least-fixed-point and transfinite reasoning, coalgebraic coinduction, and open-system composition. citeturn109745view0turn109745view1turn109745view3turn967407view11turn109745view4

## Categorical treatment of linking

The document corrects the tempting but imprecise statement that “linked state is a colimit.”

Different parts of linking correspond to different constructions:

- **Merging two binding identities** is naturally a quotient or coequalizer.
- **Connecting open component boundaries** can be represented by a pushout or structured-cospan composition.
- **The space of mutually compatible component states** is normally a pullback or another limit.
- **Synchronizing unequal representations** generally needs a lens or another bidirectional transformation.
- **Reconciling replicated copies** belongs to semilattice or CRDT semantics rather than ordinary categorical wiring.

It also explains why a pushout of specifications does not automatically imply a pullback of implementation models. That relationship needs an appropriate contravariant model construction and exactness or amalgamation assumptions. Structured cospans, institution theory, and categorical exactness provide the relevant vocabulary. citeturn109745view4turn950747view3turn967407view2

## Fixed points and transfinite induction

The document distinguishes three recursion problems:

```text
recursive syntax
    → initial algebra
    → structural induction

recursive derived facts
    → least fixed point
    → fixed-point or transfinite induction

ongoing observable behavior
    → coalgebra
    → coinduction and bisimulation
```

For a monotone immediate-consequence operator \(F\) on a complete lattice, the semantic result is:

\[
\mu F
\]

For finitary or suitably continuous rule systems, ordinary iteration may converge at stage \(\omega\):

\[
\bot,\;F(\bot),\;F^2(\bot),\ldots
\]

For merely monotone operators, successor and limit stages may be required:

\[
X_0=\bot
\]

\[
X_{\alpha+1}=F(X_\alpha)
\]

\[
X_\lambda=\bigvee_{\beta<\lambda}X_\beta
\]

The chapter then shows how this affects selector recursion, inherited capabilities, graph reachability, recursive component composition, and proof obligations. The fixed-point discussion is grounded in Tarski-style lattice semantics, transfinite iteration in abstract interpretation, and typed enforcement of monotonicity. citeturn109745view0turn109745view1turn109745view2

## Opaque lambdas versus inspectable programs

One of the strongest conclusions is that unrestricted JavaScript callbacks cannot simultaneously provide:

- convenient extension;
- static dependency discovery;
- serialization;
- deterministic replay;
- worker execution;
- incremental maintenance;
- query optimization;
- capability auditing;
- proof by induction over program structure.

The proposed API therefore uses a **deep, typed query language** for the verifiable core:

```ts
const selectableProject = query<ProjectRef>()
  .where(eq(field("archived"), literal(false)))
  .where(eq(field("ownerId"), parameter("currentUserId")));
```

An opaque escape hatch remains available:

```ts
query<ProjectRef>().opaque({
  id: "legacy-project-filter",
  dependencies: ["project", "current-user"],
  evaluate: (project, environment) =>
    expensiveApplicationPredicate(project, environment),
});
```

But opaque nodes carry explicitly weaker guarantees. They can be marked as non-serializable, non-incremental, non-replayable, or outside the mechanized proof boundary.

## Concrete proposed API

The study includes a complete TypeScript-facing sketch for:

- branded semantic identities;
- schemas and typed references;
- extensional and intensional facts;
- query ASTs;
- recursive rule modules;
- proof-relevant selection candidates;
- operations and capabilities;
- component signatures;
- typed input and output ports;
- identity links;
- lenses;
- replicated links;
- explicit interaction machines;
- algebraic interaction programs;
- React occurrence registration;
- a reference evaluator;
- an indexed incremental evaluator;
- proof certificates and runtime checking.

An interaction can be described independently of React:

```ts
const linkDocumentViews = program(function* () {
  const source = yield* select(port("document-output"));
  const target = yield* select(port("document-input"));

  const authority = yield* requireCapability(
    capability("link-document-ports", source, target),
  );

  yield* connect({
    source,
    target,
    mode: identityLink(),
    authority,
  });

  yield* commit(operation("record-link-created", {
    source,
    target,
  }));
});
```

A React adapter then supplies mounted occurrences and renders current sensitivity:

```tsx
<Occurrence
  subject={documentRef(document.id)}
  forms={["document-card", "document-label"]}
  ports={[documentOutputPort(viewId)]}
>
  <DocumentCard document={document} />
</Occurrence>
```

React is consequently an interpreter and lifecycle adapter, not the source of semantic truth.

## Verification strategy

The document proposes a small trusted semantic kernel rather than claiming that TypeScript alone can prove the whole system.

The kernel would check:

- schema well-formedness;
- rule stratification and positivity;
- monotonicity certificates;
- query typing;
- operation preconditions and postconditions;
- component port compatibility;
- link-law declarations;
- machine transition totality where required;
- preservation of declared invariants;
- proof certificates emitted by optimized compilation.

The production runtime can then use indexes, differential maintenance, caches, workers, and specialization. Its outputs are compared against—or certified relative to—a slow reference evaluator. Incremental and differential computation research provides the implementation foundation for maintaining relational results without changing their denotational meaning. citeturn950747view6turn967407view6

## Migration path

The proposed system does not require replacing the current PBUI in one operation. The document provides a staged path:

```text
current PresentationReference
        ↓
introduce semantic SubjectRef and OccurrenceId
        ↓
compile existing selectors into a query IR
        ↓
separate operations from rendered actions
        ↓
introduce component ports and explicit link modes
        ↓
move interaction workflows into machines/programs
        ↓
add reference and incremental evaluators
        ↓
mechanize the small semantic kernel
```

Legacy `filter` callbacks and descriptor actions can remain as opaque compatibility nodes during migration. New features can use the structured representation first, allowing the proportion of the system inside the verifiable boundary to increase over time.

The Markdown was checked for balanced code fences and rendered successfully through a CommonMark/GFM parser.


---

> reneder to pdf especially so i can read the mathematical notation properly

I’ll typeset the Markdown into a PDF with proper mathematical rendering, then inspect the output for layout and equation issues.

```unknown
bash -lc cat /home/oai/skills/pdfs/SKILL.md
```

<details><summary>💭 Thinking</summary>

**Planning document formatting**

I’m preparing a temporary Markdown wrapper with YAML metadata, then configuring LaTeX for readable typography, mathematics, margins, headings, links, tables of contents, and wrapped code without altering the source document.

**Planned document formatting**

</details>

```unknown
bash -lc pandoc -D latex | rg -n 'unicode-math|mathfont|mainfont|microtype|xurl|url|fvextra|fancyvrb|geometry|toc' | sed -n '1,220p'
```

<details><summary>💭 Thinking</summary>

**Refining the PDF setup**

I’m refining the wrapper so the document gets a clean title page, consistent fonts, readable mathematics, wrapped code, sensible heading levels, a table of contents, and preserved source content without duplication.

</details>

```unknown
bash -lc pandoc -D latex | rg -n 'titlepage|maketitle|subtitle' | sed -n '1,100p'
```

<details><summary>💭 Thinking</summary>

**Generated and rebuilt technical PDF monograph with math and LaTeX fixes**

</details>

The PDF has been generated with a dedicated math font. I’m checking the title pages, equations, code blocks, tables, and references for clipping or missing glyphs.

```unknown
bash -lc set -euo pipefail
python /home/oai/skills/pdfs/scripts/pdf_inspect.py /mnt/data/PRESENTATION-BASED-UI-ARCHITECTURES-BEYOND-CLIM.pdf | sed -n '1,220p'
rm -rf /mnt/data/_pdf_renders
python /home/oai/skills/pdfs/scripts/render_pdf.py /mnt/data/PRESENTATION-BASED-UI-ARCHITECTURES-BEYOND-CLIM.pdf --out_dir /mnt/data/_pdf_renders --dpi 140
find /mnt/data/_pdf_renders -type f | wc -l
find /mnt/data/_pdf_renders -type f | sort | sed -n '1,30p'
```

<details><summary>💭 Thinking</summary>

**Inspected, modified, compiled, and verified architecture scorecard PDF deliverables**

</details>

[Download the typeset PDF](sandbox:/mnt/data/PRESENTATION-BASED-UI-ARCHITECTURES-BEYOND-CLIM.pdf)

It is a 105-page letter-sized document with:

- LaTeX-rendered mathematical notation
- Embedded text and math fonts
- Clickable table of contents and references
- Syntax-highlighted TypeScript examples
- Reformatted comparison tables for print readability


---

> So when you say open typed components with ports: quotients or coequalizers explain identification of ports, what does that mean?

<details><summary>💭 Thinking</summary>

**Clarifying the construction**

I’m interpreting “identification” as gluing compatible boundary ports into shared interfaces. The component’s internals remain hidden; only its typed ports and permitted connections are exposed, while wiring imposes equalities or matching constraints between ports.

**Clarified the construction**

</details>

I’ll unpack the categorical statement at three levels: the concrete UI operation, the quotient/coequalizer construction, and what it does—and does not—guarantee about runtime state.

```unknown
bash -lc rg -n -C 5 "quotient|coequalizer|identification of ports|open typed components" /mnt/data/PRESENTATION-BASED-UI-ARCHITECTURES-BEYOND-CLIM.md | sed -n '1,240p'
```

<details><summary>💭 Thinking</summary>

**Explained port identification via quotients**

</details>

```json
{"system1_search_query":[{"q":"site:arxiv.org structured cospans pushout open systems Baez Courser pdf"},{"q":"site:math.jhu.edu category theory coequalizer quotient universal property pdf Awodey"},{"q":"site:math.ucr.edu structured cospans pushout ports open systems pdf"}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Searched 8 websites**

</details>

It means that **wiring two component ports together can be modeled as declaring that two previously distinct interface names now denote one shared interface point**.

The phrase compresses several ideas, so it helps to separate them.

## 1. What is an open typed component?

An **open component** has:

- some private internal structure;
- a public boundary;
- named ports on that boundary through which it interacts with other components.

A **typed** port declares what may pass through it and often what interaction protocol it supports.

For example:

```ts
const chart = component({
  inputs: {
    document: inputPort<DocumentId>(),
  },
  outputs: {
    selection: outputPort<Selection<Row>>(),
  },
});

const pipeline = component({
  inputs: {
    document: inputPort<DocumentId>(),
  },
  outputs: {
    resultDocument: outputPort<DocumentId>(),
  },
});
```

The component is “open” because it has not yet been connected to a complete environment. Its ports are attachment points.

Before wiring, these are separate port occurrences:

```text
chart.document
pipeline.document
```

Even though both have type `DocumentId`, they are not yet the same port and need not contain the same document.

## 2. Identification means imposing an equation

Suppose the user links the chart’s document selector to the pipeline’s document selector.

At the structural level, the system declares:

\[
\texttt{chart.document}
\sim
\texttt{pipeline.document}
\]

The symbol \(\sim\) means “these port occurrences belong to the same binding-equivalence class.”

Before linking:

```text
chart.document       pipeline.document
      │                       │
   cell-12                  cell-91
```

After linking:

```text
chart.document ───┐
                  ├── binding-7
pipeline.document ┘
```

The two component-local names remain useful for addressing the ports, but both are interpreted through the same global binding.

In a runtime implementation, this could mean:

```ts
portBinding.get("chart.document")    === "binding-7";
portBinding.get("pipeline.document") === "binding-7";
```

and:

```ts
bindingValue.get("binding-7") === "doc-42";
```

The word **identification** therefore does not mean JavaScript object identity. It means that the composition process imposes an equation between two interface occurrences.

## 3. The quotient view

Start with the set of all port occurrences:

\[
P =
\{
  \texttt{chart.document},
  \texttt{pipeline.document},
  \texttt{chart.selection},
  \texttt{pipeline.result}
\}.
\]

The link generates an equivalence relation:

\[
\texttt{chart.document}
\sim
\texttt{pipeline.document}.
\]

We then form the quotient:

\[
P/{\sim}.
\]

Its elements are equivalence classes:

\[
\begin{aligned}
[
  \texttt{chart.document}
]
&=
\{
  \texttt{chart.document},
  \texttt{pipeline.document}
\},
\\
[
  \texttt{chart.selection}
]
&=
\{
  \texttt{chart.selection}
\},
\\
[
  \texttt{pipeline.result}
]
&=
\{
  \texttt{pipeline.result}
\}.
\end{aligned}
\]

So the quotient has three binding classes even though the original system had four port occurrences.

A union-find structure is a standard concrete way to compute this quotient:

```ts
bindings.union(
  port("chart", "document"),
  port("pipeline", "document"),
);
```

Later:

```ts
bindings.find(port("chart", "document"));
// binding-7

bindings.find(port("pipeline", "document"));
// binding-7
```

## 4. Why say “coequalizer” rather than only “quotient”?

A quotient describes the resulting equivalence classes. A **coequalizer** describes the construction through its universal property.

Let \(P\) be the set of ports. Let \(R\) be the set of requested identifications. For one link:

\[
R = \{w\}.
\]

Define two maps:

\[
s,t : R \rightrightarrows P
\]

by:

\[
s(w)=\texttt{chart.document},
\qquad
t(w)=\texttt{pipeline.document}.
\]

These maps select the two endpoints of every link.

The coequalizer is a map:

\[
q:P\longrightarrow Q
\]

such that:

\[
q\circ s=q\circ t.
\]

For our link, this says:

\[
q(\texttt{chart.document})
=
q(\texttt{pipeline.document}).
\]

Thus both port occurrences map to the same element of \(Q\), which can be understood as `binding-7`.

The important part is the **universal property**:

> Every interpretation of the original ports that already treats linked endpoints equally must factor uniquely through \(Q\).

Formally, suppose:

\[
f:P\to X
\]

is some interpretation satisfying:

\[
f\circ s=f\circ t.
\]

Then there is a unique:

\[
\bar f:Q\to X
\]

such that:

\[
f=\bar f\circ q.
\]

The diagram is:

```text
        s
    R ────→ P
    │       │
  t │       │ q
    ▼       ▼
    P ────→ Q
        q

and any compatible f : P → X factors as

P ──q──→ Q ──f̄──→ X
 \_______________/
          f
```

This is why the categorical language is useful. It says that after quotienting, downstream semantics no longer need to remember the individual equations. They can operate directly on the canonical binding classes.

Products, quotients, and related constructions are characterized categorically through such universal properties rather than through a particular data representation. citeturn177891search2

## 5. A TypeScript rendering

A minimal representation might be:

```ts
type ComponentId = string;
type PortName = string;
type BindingId = string;

interface PortRef<T> {
  componentId: ComponentId;
  name: PortName;
  type: PortType<T>;
}

interface IdentityLink<T> {
  left: PortRef<T>;
  right: PortRef<T>;
}

interface CompiledBindings {
  bindingOf(port: PortRef<unknown>): BindingId;
}
```

Compilation constructs the equivalence relation generated by the links:

```ts
function compileBindings(
  ports: readonly PortRef<unknown>[],
  links: readonly IdentityLink<unknown>[],
): CompiledBindings {
  const unionFind = new UnionFind(
    ports.map(portKey),
  );

  for (const link of links) {
    assertCompatible(link.left, link.right);

    unionFind.union(
      portKey(link.left),
      portKey(link.right),
    );
  }

  return {
    bindingOf(port) {
      return unionFind.find(portKey(port));
    },
  };
}
```

Conceptually:

```text
ports                     quotient bindings

chart.document    ───────┐
                         ├── document-binding-1
pipeline.document ───────┘

chart.selection   ────────── selection-binding-2
```

This is the finite-set implementation of the quotient/coequalizer idea.

## 6. How this relates to pushout composition

Suppose component \(C\) exposes an output boundary \(B\):

\[
A \longrightarrow C \longleftarrow B
\]

and component \(D\) accepts the same interface \(B\):

\[
B \longrightarrow D \longleftarrow E.
\]

These are cospan-shaped open systems. Their composition glues \(C\) and \(D\) along \(B\):

\[
C +_B D.
\]

This object is a **pushout**.

For sets, graphs, and many other concrete structures, a pushout can be understood as:

1. take a disjoint union of the two systems;
2. identify the two copies of every shared boundary element;
3. quotient by the equivalence relation generated by those identifications.

Schematically:

```text
Component C                  Component D

internal-C — port b₁        port b₂ — internal-D
                 \          /
                  shared B

Pushout:

internal-C — [b₁ = b₂] — internal-D
```

Structured-cospan models formalize open systems as systems with explicit input and output interfaces, and composition is performed by pushout over a compatible shared interface. citeturn177891search10turn177891search11

So the relationship is:

- **coequalizer/quotient:** explains the act of imposing port equations;
- **pushout:** explains composition of whole open components along a shared interface;
- in concrete categories, the pushout is often built using a coproduct followed by a quotient.

## 7. Typed identification is restricted

You cannot safely identify arbitrary ports merely because a user drew a line between them.

This is valid:

```text
chart.document       : DocumentId
pipeline.document    : DocumentId
```

This is generally invalid:

```text
chart.document       : DocumentId
pipeline.parameters  : PipelineParameters
```

The quotient must preserve typing. One possible judgment is:

\[
\Gamma\vdash p:T
\qquad
\Gamma\vdash q:T
\qquad
\therefore
\Gamma\vdash p\sim q.
\]

If the port types differ, the system needs an adapter:

```text
Document
    │
    ▼
documentToPipelineInput
    │
    ▼
PipelineInput
```

That is not an identity link. It is a morphism, translator, lens, codec, or process between ports.

A useful API should therefore distinguish:

```ts
identityLink(left, right);
```

from:

```ts
directedLink({
  from: documentPort,
  to: pipelineInputPort,
  map: documentToPipelineInput,
});
```

and from:

```ts
bidirectionalLink({
  left: chartDomainPort,
  right: pipelineFilterPort,
  lens: chartDomainPipelineFilterLens,
});
```

Only the first one says that the endpoints should be quotient-identified.

## 8. What the quotient does **not** tell you

This is the most important limitation.

Identifying ports tells us:

> These occurrences refer to one logical interface variable or binding.

It does **not** by itself tell us:

- whether the port is readable or writable;
- which component owns updates;
- whether updates are synchronous;
- what happens when two components write concurrently;
- whether values are copied or genuinely shared;
- how unequal representations are reconciled;
- whether changes travel in one direction or both;
- how authorization works;
- whether stale values are acceptable;
- whether a feedback loop is productive.

For example, after quotienting:

```text
chart.document ≡ pipeline.document
```

the runtime might implement the class as:

### One shared cell

```ts
const cell = signal<DocumentId>("doc-42");

chart.document = cell;
pipeline.document = cell;
```

### A store path

```ts
chart.document =
  store.bindingValues["binding-7"];

pipeline.document =
  store.bindingValues["binding-7"];
```

### A distributed register

```ts
binding7 = replicatedRegister<DocumentId>();
```

### A constraint

```text
chart.document must equal pipeline.document
```

with a separate repair algorithm when they disagree.

Those implementations have different operational behavior even though they satisfy the same structural identification.

## 9. Quotient versus compatible state space

There are two different mathematical questions.

### Structural question

Which port names have been identified?

\[
Q=P/{\sim}.
\]

This is quotient/coequalizer territory.

### State question

Which pairs of component states agree on their linked document?

Suppose:

\[
p_C:S_C\to D
\]

extracts the chart document, and:

\[
p_P:S_P\to D
\]

extracts the pipeline document.

The compatible combined states are:

\[
S_C\times_D S_P
=
\{
(c,p)\in S_C\times S_P
\mid
p_C(c)=p_P(p)
\}.
\]

That is a **pullback**.

So:

```text
coequalizer:
    makes the port names one binding

pullback:
    selects state pairs that agree on that binding
```

Neither automatically provides the transition algorithm that restores agreement after an edit. That requires additional operational semantics, such as:

- a shared mutable cell;
- a transaction;
- a state machine;
- a lens;
- a consistency-restoration procedure;
- a CRDT.

## 10. The practical meaning for PBUI

For the chart/pipeline example, a port-based PBUI architecture might represent:

```ts
const ChartSignature = {
  inputs: {
    document: port<DocumentId>({
      mode: "readWrite",
    }),
  },
};

const PipelineSignature = {
  inputs: {
    document: port<DocumentId>({
      mode: "readWrite",
    }),
  },
};
```

Before linking:

```ts
chart.document    -> binding-chart
pipeline.document -> binding-pipeline
```

After an identity link:

```ts
connect(
  chart.ports.document,
  pipeline.ports.document,
  identityLink(),
);
```

the graph compiler computes:

```ts
bindingOf(chart.ports.document)
  === bindingOf(pipeline.ports.document);
```

It then allocates one shared resource per quotient class:

```ts
const binding7 = createCell<DocumentId>("doc-42");
```

and gives each component a projection onto that resource:

```ts
mountChart({
  document: binding7,
});

mountPipeline({
  document: binding7,
});
```

The category-theoretic statement is not that the UI must literally implement category objects at runtime. It is that the compiler’s behavior can be specified independently of implementation details:

1. linked endpoints become equal under the quotient map;
2. unlinked endpoints remain distinct unless equality is forced transitively;
3. every interpretation respecting the link equations factors through the compiled binding graph;
4. link order does not change the resulting equivalence relation;
5. duplicate links are idempotent;
6. transitive linking works predictably.

For example:

\[
p\sim q,\quad q\sim r
\quad\Longrightarrow\quad
p\sim r.
\]

At the implementation level:

```ts
union(p, q);
union(q, r);

find(p) === find(r); // must hold
```

That gives a precise, testable interpretation of the sentence:

> **Quotients or coequalizers explain identification of ports.**

They explain how a collection of local component-boundary names is transformed into a canonical collection of global binding identities by imposing the equations introduced by wiring.


---

> What’s a coalgebraic machine?

A **coalgebraic machine** is a stateful system described by what you can **observe now** and how it can **evolve next**.

Formally, choose a functor \(F\) describing one step of behavior. A coalgebra is a pair

\[
(X,\gamma)
\]

where:

- \(X\) is the set or type of internal states;
- \(\gamma : X \to F(X)\) reveals the machine’s current observable behavior and its possible successor states.

The key direction is:

\[
\text{state} \longrightarrow \text{observable structure containing future states}.
\]

## A simple deterministic machine

Suppose a machine receives inputs of type \(I\), emits outputs of type \(O\), and moves to a new state.

Its coalgebra can be written as:

\[
\gamma : X \to O \times X^I.
\]

Given a state \(x\), the machine tells us:

1. its current output \(o \in O\);
2. for every possible input \(i \in I\), the next state.

In TypeScript:

```ts
interface MooreMachine<State, Input, Output> {
  observe(state: State): Output;
  transition(state: State, input: Input): State;
}
```

Equivalently:

```ts
type Coalgebra<State, Input, Output> =
  (state: State) => {
    output: Output;
    next: (input: Input) => State;
  };
```

For a document-linking interaction:

```ts
type LinkState =
  | { kind: "idle" }
  | { kind: "choosingSource" }
  | { kind: "choosingTarget"; source: PortRef }
  | { kind: "linked"; source: PortRef; target: PortRef }
  | { kind: "failed"; message: string };

type LinkInput =
  | { type: "start" }
  | { type: "selectPort"; port: PortRef }
  | { type: "cancel" }
  | { type: "unlink" };
```

The machine describes how every state reacts:

```ts
function transition(
  state: LinkState,
  input: LinkInput,
): LinkState {
  switch (state.kind) {
    case "idle":
      return input.type === "start"
        ? { kind: "choosingSource" }
        : state;

    case "choosingSource":
      if (input.type === "cancel") {
        return { kind: "idle" };
      }

      if (input.type === "selectPort") {
        return {
          kind: "choosingTarget",
          source: input.port,
        };
      }

      return state;

    case "choosingTarget":
      if (input.type === "cancel") {
        return { kind: "idle" };
      }

      if (input.type === "selectPort") {
        return compatible(state.source, input.port)
          ? {
              kind: "linked",
              source: state.source,
              target: input.port,
            }
          : {
              kind: "failed",
              message: "The selected ports are incompatible.",
            };
      }

      return state;

    case "linked":
      return input.type === "unlink"
        ? { kind: "idle" }
        : state;

    case "failed":
      return input.type === "start"
        ? { kind: "choosingSource" }
        : state;
  }
}
```

This is coalgebraic because the system is understood by repeatedly observing a state and following its transitions.

## Algebra versus coalgebra

The contrast is useful.

An algebra usually has the form:

\[
\alpha : F(X) \to X.
\]

It **constructs or reduces** a value from smaller pieces.

For example, an expression evaluator:

\[
\text{ExprF}(\mathbb{Z}) \to \mathbb{Z}
\]

combines evaluated child expressions into one result.

A coalgebra has the reverse shape:

\[
\gamma : X \to F(X).
\]

It **decomposes or unfolds** a state into current observations and future behavior.

A rough mnemonic is:

```text
algebra:
    combine finite structure

coalgebra:
    observe potentially unending behavior
```

An arithmetic expression is naturally algebraic because it is built from subexpressions.

A UI session, server, stream, editor, or interaction protocol is naturally coalgebraic because it can continue indefinitely.

## Why coalgebra fits interactive systems

An interactive UI is not usually a single finite result. At any moment it has:

- visible output;
- enabled interactions;
- pending requests;
- subscriptions;
- possible next states.

That is exactly coalgebraic structure.

For a presentation-based UI, a state might expose:

```ts
interface UiObservation {
  visibleOccurrences: readonly Occurrence[];
  acceptableOccurrences: ReadonlySet<OccurrenceId>;
  availableActions: ReadonlyMap<OccurrenceId, readonly Action[]>;
  prompt: string | null;
}
```

The full coalgebra might be:

```ts
interface UiStep<State, Event> {
  observe: UiObservation;
  next(event: Event): State;
}

type UiCoalgebra<State, Event> =
  (state: State) => UiStep<State, Event>;
```

The React layer can then render `observe`, while user and system events are fed into `next`.

```text
semantic state
      │
      ▼
 observation
      │
      ▼
    React
      │
 user event
      ▼
 next semantic state
```

React is not the machine itself. It is one interpreter of the machine’s observations.

## Moore and Mealy machines

Two common coalgebraic machines are Moore and Mealy machines.

A **Moore machine** associates output with the current state:

\[
X \to O \times X^I.
\]

```ts
observe(state): Output
transition(state, input): State
```

A **Mealy machine** associates output with transitions:

\[
X \to (O \times X)^I.
\]

```ts
step(state, input): {
  output: Output;
  state: State;
}
```

A UI often uses both views:

- the rendered interface is Moore-like: output depends on current state;
- commands and effects are Mealy-like: handling an event emits effects and a successor state.

```ts
interface StepResult<State, Effect> {
  state: State;
  effects: readonly Effect[];
}

function step(
  state: State,
  event: Event,
): StepResult<State, Effect> {
  // ...
}
```

## Behavior, not representation

Coalgebra encourages us to ask when two machines are behaviorally the same, rather than whether their internal states are structurally equal.

Suppose one linking implementation stores:

```ts
{
  phase: 2,
  selected: [sourcePort]
}
```

and another stores:

```ts
{
  mode: "waiting-for-target",
  source: sourcePort
}
```

Their state representations differ. But if they:

- render the same prompts;
- enable the same occurrences;
- react identically to every possible future event;

then they can be regarded as behaviorally equivalent.

This relation is called **bisimulation**.

## Bisimulation

A relation \(R \subseteq X \times Y\) is a bisimulation when related states:

1. have matching observations;
2. transition to related states under corresponding inputs.

For deterministic machines, if \(x\,R\,y\), then:

\[
\operatorname{observe}(x)
=
\operatorname{observe}(y)
\]

and for every input \(i\):

\[
\operatorname{next}_X(x,i)
\;R\;
\operatorname{next}_Y(y,i).
\]

This is valuable for refactoring. You can replace one implementation with another and prove that users cannot distinguish them through the public interaction protocol.

For PBUI, a bisimulation argument could establish that:

- the original Redux implementation;
- a new relational fixed-point runtime;

produce the same prompts, accepted objects, actions, and state transitions for every event trace.

## Final coalgebras

A **final coalgebra** is an abstract domain of complete observable behaviors.

For streams over \(A\), the coalgebra functor is:

\[
F(X)=A\times X.
\]

A stream reveals:

- its current head;
- its remaining tail.

The final coalgebra is the space of all infinite streams:

\[
A^\omega.
\]

A state machine can be mapped into its complete behavior: the potentially infinite tree or trace of everything it would do under all future inputs.

This mapping forgets irrelevant internal representation and preserves observable behavior.

For a deterministic input machine, the behavioral object can be thought of as a tree:

```text
current observation
├── event A → future behavior
├── event B → future behavior
└── event C → future behavior
```

Two internal states are equivalent when they map to the same behavior in the final coalgebra.

## Coalgebraic UI components

An open component can be modeled as a coalgebra whose observations include its port values and offered actions.

For component state \(S\), input events \(I\), visible output \(V\), and emitted port messages \(M\):

\[
S \to V \times (M \times S)^I.
\]

In TypeScript:

```ts
interface ComponentStep<State, Input, View, Message> {
  view: View;
  transition(
    input: Input,
  ): {
    messages: readonly Message[];
    state: State;
  };
}

type ComponentCoalgebra<State, Input, View, Message> =
  (state: State) => ComponentStep<
    State,
    Input,
    View,
    Message
  >;
```

A chart component might expose:

```ts
type ChartMessage =
  | {
      type: "documentChanged";
      documentId: DocumentId;
    }
  | {
      type: "selectionChanged";
      rows: readonly RowId[];
    };
```

Its behavior is not merely a React function from props to JSX. It includes how it evolves and communicates over time.

## Composition

Once components are coalgebraic, composition means more than placing their React nodes beside each other.

You must connect:

- outputs of one machine to inputs of another;
- shared ports or binding cells;
- feedback paths;
- effect handlers;
- scheduling rules.

For example:

```text
chart.documentChanged
          │
          ▼
 shared document binding
          │
          ▼
pipeline.externalDocumentChanged
```

The composed system has a product-like state:

\[
S_{\text{chart}}
\times
S_{\text{pipeline}}
\times
S_{\text{binding}}.
\]

Its transition function coordinates the constituent transitions.

If the link is synchronous, one event may cause several internal transitions before the composed system reaches a stable externally visible state. That can be described using fixed-point iteration:

\[
s_{n+1}=T(s_n)
\]

until:

\[
T(s_n)=s_n.
\]

So coalgebra describes the ongoing machine, while fixed-point machinery may be used inside one composite step to settle propagation.

## Coalgebra versus statecharts

A statechart is one concrete syntax for describing a coalgebraic machine.

Statecharts add useful structure:

- hierarchical states;
- parallel regions;
- guarded transitions;
- entry and exit effects;
- history states;
- event priorities.

The semantic core is still approximately:

```text
current configuration
    + incoming event
    → next configuration
    + effects
```

A statechart can therefore be compiled into a coalgebraic transition system.

The coalgebraic viewpoint is broader. It gives mathematical tools for:

- behavioral equivalence;
- composition;
- minimization;
- coinductive proofs;
- infinite behavior;
- refinement.

The statechart gives an ergonomic authoring notation.

## Why this matters for the proposed architecture

Calling an interaction a coalgebraic machine means that it should not be represented merely as an arbitrary callback like:

```ts
onClick={() => {
  // mutate several stores
  // open a selector
  // wait for another click
  // link two views
}}
```

Instead, the interaction has an explicit state space:

```ts
type InteractionState =
  | Idle
  | SelectingSource
  | SelectingTarget
  | Confirming
  | Completed
  | Failed;
```

an explicit observation function:

```ts
function observe(
  state: InteractionState,
): InteractionObservation;
```

and an explicit transition function:

```ts
function step(
  state: InteractionState,
  event: InteractionEvent,
): {
  state: InteractionState;
  effects: readonly InteractionEffect[];
};
```

That provides several benefits:

- every reachable phase can be inspected;
- missing event cases can be detected;
- invariants can be proved inductively over transitions;
- implementations can be compared using bisimulation;
- event traces can be replayed;
- the machine can run outside React;
- effects can be interpreted differently in tests, browsers, and servers.

In one sentence:

> A coalgebraic machine is a system defined by how its current state reveals observable behavior and determines its possible future states, making it a natural model for long-running interactive processes rather than finite constructed values.


---

> What about the use of coequalizers in the paper

I’ll trace every use of “coequalizer” in the document and distinguish the intended construction from places where the wording may be too strong or imprecise.

```unknown
bash -lc rg -n -i "coequalizer|quotient|pushout|identif|colimit" /mnt/data/PRESENTATION-BASED-UI-ARCHITECTURES-BEYOND-CLIM.md | sed -n '1,240p'
```

<details><summary>💭 Thinking</summary>

**Located coequalizer discussions and inspected relevant document sections**

**Clarifying coequalizers**

I’m explaining coequalizers as structural quotient constructions: they identify ports or states according to declared wiring. I’ll distinguish this compile-time identification from runtime value synchronization and note how pushouts can be represented using coproducts and coequalizers.

**Clarified coequalizers**

</details>

In the paper, **coequalizers are used only at the wiring/compiler layer**. They formalize the operation:

> “These distinct local port names shall represent one global binding.”

They do **not** directly define component behavior, state transitions, synchronization policy, or the coalgebraic machine.

## 1. The exact construction intended

Let \(P\) be the collection of port occurrences in a workspace:

\[
P =
\{
\texttt{chart.document},
\texttt{pipeline.document},
\texttt{table.document},
\texttt{chart.selection},
\ldots
\}.
\]

Let \(R\) be the collection of requested identity links. For example:

\[
R=\{r_1,r_2\}
\]

where:

\[
r_1:
\texttt{chart.document}
\equiv
\texttt{pipeline.document}
\]

and:

\[
r_2:
\texttt{pipeline.document}
\equiv
\texttt{table.document}.
\]

Define two endpoint maps:

\[
s,t:R\rightrightarrows P
\]

such that:

\[
s(r_1)=\texttt{chart.document},
\qquad
t(r_1)=\texttt{pipeline.document},
\]

and:

\[
s(r_2)=\texttt{pipeline.document},
\qquad
t(r_2)=\texttt{table.document}.
\]

The compiler computes the coequalizer:

\[
P
\xrightarrow{q}
Q
=
\operatorname{coeq}(s,t).
\]

It satisfies:

\[
q\circ s=q\circ t.
\]

Therefore:

\[
q(\texttt{chart.document})
=
q(\texttt{pipeline.document})
=
q(\texttt{table.document}).
\]

The resulting element of \(Q\) is one global binding identity, such as:

```text
binding-7
```

So the result might look like:

```text
chart.document    ─┐
pipeline.document ─┼── binding-7
table.document    ─┘

chart.selection   ─── binding-8
```

In the category of sets, this coequalizer is exactly the quotient:

\[
Q=P/{\sim}
\]

where \(\sim\) is the smallest equivalence relation containing all requested links.

## 2. Why the paper uses a coequalizer

The construction captures several desirable laws automatically.

### Transitivity

From:

\[
p\sim q
\qquad\text{and}\qquad
q\sim r
\]

the generated equivalence relation contains:

\[
p\sim r.
\]

### Idempotence

Adding the same link twice changes nothing:

\[
\operatorname{identify}(p,q);
\operatorname{identify}(p,q)
\]

produces the same quotient as adding it once.

### Order independence

These operations produce isomorphic results:

```ts
identify(chartDoc, pipelineDoc);
identify(pipelineDoc, tableDoc);
```

and:

```ts
identify(pipelineDoc, tableDoc);
identify(chartDoc, pipelineDoc);
```

### Canonical downstream interpretation

Suppose a later interpreter assigns runtime resources to ports:

\[
f:P\to X.
\]

If it respects all links:

\[
f\circ s=f\circ t,
\]

then it factors uniquely through the quotient:

\[
f=\bar f\circ q
\]

for a unique map:

\[
\bar f:Q\to X.
\]

This means the runtime does not need to allocate resources independently for every original port and then repeatedly enforce pairwise equalities. It can interpret the quotient classes directly:

```ts
for (const binding of quotientBindings) {
  runtime.allocateCell(binding);
}
```

## 3. What the compiler does with the quotient

The paper proposes a compilation sequence like this:

```text
typed component graph
        ↓
check identity-link compatibility
        ↓
collect port equations
        ↓
compute coequalizer / equivalence classes
        ↓
allocate one resource per class
        ↓
give each component a projection to that resource
```

In pseudocode:

```ts
const graph = workspace
  .add("chart", Chart)
  .add("pipeline", Pipeline)
  .identify(
    port("chart", "primaryDocument"),
    port("pipeline", "primaryDocument"),
  );

const quotient = computePortQuotient(graph);

for (const bindingClass of quotient.classes) {
  allocateSharedCell(bindingClass);
}
```

A union-find implementation computes the finite quotient efficiently:

```ts
unionFind.union(chartDocument, pipelineDocument);

const chartBinding =
  unionFind.find(chartDocument);

const pipelineBinding =
  unionFind.find(pipelineDocument);

assert(chartBinding === pipelineBinding);
```

Union-find is an implementation technique. The coequalizer is the semantic specification of what the result must mean.

## 4. The coequalizer is not the shared value

This distinction is easy to miss.

The quotient element:

```text
binding-7
```

is a **binding identity**. It is not itself the selected document.

The runtime may associate a value with it:

\[
v:Q\to D
\]

where \(D\) is the space of document references.

For example:

\[
v(\texttt{binding-7})=\texttt{doc-A}.
\]

Then a component reads its document through composition:

\[
P\xrightarrow{q}Q\xrightarrow{v}D.
\]

For the chart:

\[
v(q(\texttt{chart.document}))=\texttt{doc-A}.
\]

For the pipeline:

\[
v(q(\texttt{pipeline.document}))=\texttt{doc-A}.
\]

Equality follows because both local ports pass through the same quotient element.

This decomposition is useful:

```text
q : local port occurrence → global binding
v : global binding → current value
```

The quotient controls **aliasing**. The value map controls **state**.

## 5. Coequalizer versus pullback in the paper

The paper deliberately uses two different constructions.

### Coequalizer: structural identification

\[
P\to P/{\sim}
\]

answers:

> Which local port names represent the same global binding?

### Pullback: compatible component states

Suppose:

\[
p_c:C\to D
\]

extracts the chart’s current document, and:

\[
p_p:P\to D
\]

extracts the pipeline’s current document.

The compatible combined states are:

\[
C\times_D P
=
\{
(c,p)\mid p_c(c)=p_p(p)
\}.
\]

This answers:

> Which pairs of chart and pipeline states agree on their document?

These are related but not interchangeable:

```text
coequalizer:
local interface names → global binding identities

pullback:
local component states → compatible global states
```

The coequalizer lives primarily on the **syntax, topology, or interface graph** side. The pullback lives on the **semantic model or state** side.

## 6. Coequalizer versus pushout

The paper also says that whole open components can compose by pushout.

That is consistent with the coequalizer account. In many concrete categories, a pushout is constructed by:

1. taking a coproduct or disjoint union;
2. quotienting it by equations identifying the two copies of the shared interface.

For a span:

\[
X\xleftarrow{f}B\xrightarrow{g}Y,
\]

the pushout can often be presented as:

\[
X+_B Y
\cong
(X+Y)/{\sim}
\]

where:

\[
f(b)\sim g(b)
\qquad
\text{for every }b\in B.
\]

More formally, it can be constructed as the coequalizer of:

\[
B
\rightrightarrows
X+Y,
\]

using the two coproduct injections:

\[
\iota_X\circ f,
\qquad
\iota_Y\circ g.
\]

Thus the paper uses the constructions at different scales:

- **coequalizer:** identify specific port occurrences;
- **pushout:** compose entire open systems along a shared boundary;
- **pullback:** characterize compatible implementations or states.

## 7. Interaction with a coalgebraic machine

The coequalizer does not define the coalgebraic transition system. It helps construct the state space on which that machine runs.

Before linking, a simplified global state might be:

\[
S_{\mathrm{before}}
=
D_{\text{chart}}
\times
D_{\text{pipeline}}.
\]

The chart and pipeline documents may differ.

After compiling an identity link through one shared binding, the runtime state may instead contain:

\[
S_{\mathrm{after}}=D.
\]

Both components observe that same value through their port projections.

The workspace coalgebra could then be:

\[
\gamma:
S_{\mathrm{after}}
\to
O\times S_{\mathrm{after}}^I,
\]

or, with additional component state:

\[
\gamma:
(S_C\times S_P\times D)
\to
O\times
(S_C\times S_P\times D)^I.
\]

The roles are therefore:

```text
coequalizer:
determines which ports share a binding

coalgebra:
determines how the resulting linked system evolves
```

For an event:

```ts
{
  type: "chartSelectedDocument",
  documentId: "doc-B",
}
```

the coalgebraic transition updates the value attached to the quotient class:

```ts
bindingValues.set("binding-7", "doc-B");
```

Both components then observe `doc-B`.

## 8. A proof obligation enabled by the construction

Suppose:

\[
q:P\to Q
\]

is the compiled quotient, and:

\[
v_s:Q\to D
\]

gives the binding values in runtime state \(s\).

A component port \(p\) observes:

\[
\operatorname{observe}_s(p)=v_s(q(p)).
\]

If two ports were identified:

\[
q(p_1)=q(p_2),
\]

then immediately:

\[
\operatorname{observe}_s(p_1)
=
v_s(q(p_1))
=
v_s(q(p_2))
=
\operatorname{observe}_s(p_2).
\]

So the linked-value invariant follows by construction:

\[
\forall s\in\operatorname{Reachable},
\quad
\operatorname{chartDocument}(s)
=
\operatorname{pipelineDocument}(s).
\]

This proof still depends on an important runtime condition:

> Components must read and write through the generated binding interface rather than maintaining unsynchronized shadow copies.

The quotient proves that the generated port interpretation aliases the same binding. It cannot stop arbitrary component code from bypassing that interpretation.

## 9. A limitation: unlinking is not an inverse

Quotienting forgets distinctions.

After:

\[
p\sim q,
\]

the quotient contains one class:

\[
[p]=[q].
\]

There is no canonical inverse operation that recovers two independent values. When the user unlinks the components, the runtime needs an explicit policy:

```ts
unlink({
  port: pipelineDocument,
  initialize: "copy-current-value",
});
```

Possible policies include:

- copy the current shared value into both new bindings;
- preserve one side and reset the other;
- retrieve previously stored independent values;
- ask the user;
- reject unlinking while an operation is active.

Therefore the implementation must retain more than the bare quotient if reversible topology editing is required. It may preserve:

- original port occurrences;
- link declarations and provenance;
- previous binding values;
- an edit history;
- persistent binding IDs.

Usually the compiler recomputes the quotient from the remaining link declarations rather than trying to “subtract” an equivalence from union-find.

## 10. A limitation: not every connection is an identification

The paper restricts `.identify` to ports with genuinely identical semantics.

This is appropriate:

```ts
workspace.identify(
  chart.port("primaryDocument"),
  pipeline.port("primaryDocument"),
);
```

It is inappropriate when the relationship transforms information:

```ts
chart.selectedRows
    → pipeline.filterExpression
```

Those ports should not be made equal. They require a morphism, adapter, or lens:

```ts
workspace.connect(
  chart.port("selectedRows"),
  pipeline.port("filter"),
  {
    via: selectedRowsToFilter,
  },
);
```

Similarly, two ports carrying `DocumentId` are not necessarily identity-compatible:

```text
current document behavior
document-open event stream
last successfully processed document
proposed document
```

They share a TypeScript payload type but not a semantic contract.

The coequalizer should therefore be computed over a category or typed graph whose morphisms preserve more than raw payload types. Port contracts in the paper include temporal mode, authority, multiplicity, update algebra, and semantic tags for this reason.

## 11. Where the document uses the idea

The coequalizer appears in four connected roles:

- **Section 20.2:** formal explanation of port-name identification.
- **Section 25:** worked example from chart and pipeline ports to one binding class.
- **Section 32:** the `.identify(...)` API, contrasted with transformed `.connect(...)`.
- **Section 47:** compiler steps—add an equation, quotient the port graph, allocate one cell per class.
- **Section 56.8:** proposed verification target connecting graph quotienting to generated synchronization code.

The strongest intended theorem in that final research direction would resemble:

> Given a well-typed port graph \(G\), its identity-link coequalizer \(q:G\to Q\), and generated runtime \(R(Q)\), every pair of identified ports has equal observations in every reachable runtime state, provided all port effects are interpreted through the generated handlers.

## 12. One wording improvement I would make

The sentence:

> “quotients or coequalizers explain identification of ports”

is correct but compressed. A more exact formulation would be:

> Identity-link declarations generate an equivalence relation on typed port occurrences. The wiring compiler forms its universal quotient—equivalently, in a suitable category, the coequalizer of the two endpoint maps—and interprets each resulting equivalence class as one global binding.

That wording makes clear:

- what the objects are;
- what the parallel maps are;
- what is being quotiented;
- that typing matters;
- and that the runtime binding is an interpretation of the quotient, not the coequalizer itself.


---

> Generate a little self contained lean program and proof of ports and relationships and bindings and their projection to say , a f showing a widget

<details><summary>💭 Thinking</summary>

**Modeling widget bindings**

I’m interpreting this as a Lean model of widgets, ports, relationships, and bindings, with a proof that a binding projects to its destination port. I’ll keep it self-contained and use straightforward structures and propositions.

**Modeled widget bindings**

</details>

I’ll produce a Lean 4 file that models typed ports, link-generated binding classes, the quotient projection, and a well-defined widget renderer, with proofs that linked ports share both a binding and rendered widget.

```json
{"system1_search_query":[{"q":"site:lean-lang.org Lean 4 Quotient Setoid documentation"},{"q":"site:lean-lang.org theorem proving in Lean 4 quotient types setoid"},{"q":"site:lean-lang.org Lean 4 deriving DecidableEq Repr documentation"}],"response_length":"medium"}
```

<details><summary>💭 Thinking</summary>

**Searched 11 websites**

</details>

```unknown
bash -lc command -v lean || true; lean --version 2>/dev/null || true; ls -la /mnt/data | sed -n '1,80p'
```

<details><summary>💭 Thinking</summary>

**Checked Lean installation and toolchain availability**

</details>

```json
{"open":[{"ref_id":"turn213074search2"},{"ref_id":"turn213074search3"}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Searched 1 website**

</details>

```json
{"open":[{"ref_id":"https://github.com/leanprover/lean4/releases/download/v4.32.2/lean-4.32.2-linux.tar.zst"}],"response_length":"short"}
```

<details><summary>💭 Thinking</summary>

**Searching the web**

</details>

```unknown
bash -lc curl -L --fail --silent --show-error 'https://github.com/leanprover/lean4/releases/download/v4.32.2/lean-4.32.2-linux.tar.zst' -o /tmp/lean.tar.zst && ls -lh /tmp/lean.tar.zst
```

<details><summary>💭 Thinking</summary>

**Downloaded Lean release archive with curl**

**Formalizing the structure**

I’m refining the model by making relationships an explicit equivalence relation generated by links. Widgets can then project ports consistently across equivalent bindings, with Lean proving that linked ports produce identical projections.

**Formalized the structure**

</details>

```json
{"find":[{"ref_id":"turn635665view0","pattern":"Quotient.sound"},{"ref_id":"turn635665view0","pattern":"Quotient.lift"},{"ref_id":"turn635665view0","pattern":"Quotient.mk"}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Searched 1 website**

</details>

```unknown
bash -lc apt-cache policy elan lean4 2>/dev/null | sed -n '1,120p'
```

<details><summary>💭 Thinking</summary>

**Checked Lean quotient induction syntax**

</details>

The example will make the quotient’s universal property explicit: any port-level interpretation that respects links factors through `Binding`; the widget function is one such factor.

```unknown
bash -lc set -euo pipefail
out=/mnt/data/lean-port-bindings
rm -rf "$out"
mkdir -p "$out"
cat > "$out/Main.lean" <<'EOF'
import Init

/-!
A small, dependency-free Lean 4 model of typed UI ports, identity links,
bindings as quotient classes, and a widget interpretation that factors
through the quotient.

The intended picture is:

  local typed ports --project--> shared binding --f--> widget

The relation `Linked` is the equivalence closure generated by two declared
links. `Binding t` is the quotient of ports of type `t` by that relation.
-/

namespace PortBindings

/-- Semantic payload types carried by ports. -/
inductive PortType where
  | document
  | selection
  deriving Repr, DecidableEq

/--
Typed local port occurrences. The index prevents an identity link between,
for example, a document port and a selection port.
-/
inductive Port : PortType → Type where
  | chartDocument    : Port .document
  | pipelineDocument : Port .document
  | tableDocument    : Port .document
  | chartSelection   : Port .selection

/--
The equivalence relation generated by the declared identity links.

The primitive edges are:

  chartDocument    ~ pipelineDocument
  pipelineDocument ~ tableDocument

The remaining constructors close the relation under reflexivity, symmetry,
and transitivity.
-/
inductive Linked : {t : PortType} → Port t → Port t → Prop where
  | refl {t : PortType} (p : Port t) : Linked p p
  | chart_pipeline :
      Linked Port.chartDocument Port.pipelineDocument
  | pipeline_table :
      Linked Port.pipelineDocument Port.tableDocument
  | symm {t : PortType} {p q : Port t} :
      Linked p q → Linked q p
  | trans {t : PortType} {p q r : Port t} :
      Linked p q → Linked q r → Linked p r

/-- The generated link relation is a setoid for each semantic port type. -/
def portSetoid (t : PortType) : Setoid (Port t) where
  r := Linked
  iseqv := {
    refl := fun p => Linked.refl p
    symm := fun h => Linked.symm h
    trans := fun h₁ h₂ => Linked.trans h₁ h₂
  }

/--
A binding is an equivalence class of linked local ports. In `Type`, this is
the concrete quotient/coequalizer used by the wiring compiler.
-/
abbrev Binding (t : PortType) := Quotient (portSetoid t)

/-- The quotient projection from a local port occurrence to its binding. -/
def project {t : PortType} (p : Port t) : Binding t :=
  Quotient.mk (portSetoid t) p

/-- Linked ports are identified by the quotient projection. -/
theorem linked_ports_same_binding
    {t : PortType} {p q : Port t}
    (h : Linked p q) :
    project p = project q := by
  exact Quotient.sound h

/-- A tiny semantic widget language. -/
inductive Widget where
  | documentPicker (title : String)
  | selectionBadge (title : String)
  deriving Repr, DecidableEq

/--
A local interpretation of ports as widgets. Notice that all three linked
document ports receive the same widget value.
-/
def rawWidget {t : PortType} : Port t → Widget
  | .chartDocument    => .documentPicker "Shared document"
  | .pipelineDocument => .documentPicker "Shared document"
  | .tableDocument    => .documentPicker "Shared document"
  | .chartSelection   => .selectionBadge "Chart selection"

/-- The local widget interpretation respects every generated link. -/
theorem rawWidget_respects
    {t : PortType} {p q : Port t}
    (h : Linked p q) :
    rawWidget p = rawWidget q := by
  induction h with
  | refl p =>
      rfl
  | chart_pipeline =>
      rfl
  | pipeline_table =>
      rfl
  | symm h ih =>
      exact ih.symm
  | trans h₁ h₂ ih₁ ih₂ =>
      exact ih₁.trans ih₂

/--
Existence part of the quotient's universal property: every port-level map
that respects `Linked` factors through `Binding`.
-/
def factor
    {t : PortType} {α : Type}
    (g : Port t → α)
    (respects : ∀ p q, Linked p q → g p = g q) :
    Binding t → α :=
  Quotient.lift g respects

/-- The factorization commutes with the quotient projection. -/
theorem factor_commutes
    {t : PortType} {α : Type}
    (g : Port t → α)
    (respects : ∀ p q, Linked p q → g p = g q)
    (p : Port t) :
    factor g respects (project p) = g p := by
  rfl

/--
Uniqueness part of the universal property: a map out of `Binding` is uniquely
determined by how it acts after the projection from local ports.
-/
theorem factor_unique
    {t : PortType} {α : Type}
    (g : Port t → α)
    (respects : ∀ p q, Linked p q → g p = g q)
    (u : Binding t → α)
    (commutes : ∀ p, u (project p) = g p) :
    u = factor g respects := by
  funext b
  refine Quotient.ind (s := portSetoid t) ?_ b
  intro p
  simpa [factor, project] using commutes p

/-- The widget interpretation lifted from ports to shared bindings. -/
def widgetOfBinding {t : PortType} : Binding t → Widget :=
  factor rawWidget (fun _ _ h => rawWidget_respects h)

/-- A port shows a widget by projecting to its binding and interpreting it. -/
def showWidget {t : PortType} (p : Port t) : Widget :=
  widgetOfBinding (project p)

/-- The requested concrete function `f` for document bindings. -/
def f : Binding .document → Widget :=
  widgetOfBinding

/-- The triangle `Port -> Binding -> Widget` commutes. -/
theorem f_commutes (p : Port .document) :
    f (project p) = rawWidget p := by
  rfl

/-- The two primitive chart/pipeline endpoints have one binding. -/
theorem chart_pipeline_same_binding :
    project Port.chartDocument = project Port.pipelineDocument := by
  exact linked_ports_same_binding Linked.chart_pipeline

/-- Transitivity identifies chart, pipeline, and table document ports. -/
theorem chart_table_same_binding :
    project Port.chartDocument = project Port.tableDocument := by
  apply linked_ports_same_binding
  exact Linked.trans Linked.chart_pipeline Linked.pipeline_table

/-- Therefore the linked chart and pipeline project to the same widget. -/
theorem chart_pipeline_same_widget :
    f (project Port.chartDocument) =
      f (project Port.pipelineDocument) := by
  exact congrArg f chart_pipeline_same_binding

/-- And the concrete widget is the shared document picker. -/
theorem chart_widget_is_document_picker :
    f (project Port.chartDocument) =
      Widget.documentPicker "Shared document" := by
  rfl

/-- A tiny HTML-like renderer, outside the quotient proof itself. -/
def Widget.render : Widget → String
  | .documentPicker title =>
      "<select aria-label=\"" ++ title ++ "\">Document</select>"
  | .selectionBadge title =>
      "<span role=\"status\">" ++ title ++ "</span>"

end PortBindings

open PortBindings

/-- Run with `lean --run Main.lean`. -/
def main : IO Unit := do
  IO.println ("chart:    " ++ Widget.render (f (project Port.chartDocument)))
  IO.println ("pipeline: " ++ Widget.render (f (project Port.pipelineDocument)))
  IO.println ("table:    " ++ Widget.render (f (project Port.tableDocument)))
EOF

cat > "$out/lean-toolchain" <<'EOF'
leanprover/lean4:v4.32.2
EOF

cat > "$out/README.md" <<'EOF'
# Lean port-binding proof

This is a dependency-free Lean 4 example of:

- semantically typed local UI ports;
- identity-link declarations and their reflexive/symmetric/transitive closure;
- bindings as quotient classes of linked ports;
- the quotient projection `project : Port t -> Binding t`;
- the existence and uniqueness factorization property for maps out of a binding;
- a concrete `f : Binding .document -> Widget`;
- proofs that linked chart, pipeline, and table ports share a binding and widget;
- a tiny executable renderer.

## Run

With `elan` installed, enter this directory and run:

```sh
lean --run Main.lean
```

Expected output:

```text
chart:    <select aria-label="Shared document">Document</select>
pipeline: <select aria-label="Shared document">Document</select>
table:    <select aria-label="Shared document">Document</select>
```

The file uses only Lean's `Init` library and pins Lean 4.32.2 in
`lean-toolchain`.
EOF

cd /mnt/data
rm -f lean-port-bindings.zip
zip -qr lean-port-bindings.zip lean-port-bindings
ls -lah "$out" /mnt/data/lean-port-bindings.zip

```

<details><summary>💭 Thinking</summary>

**Modeled typed port bindings and searched for Lean tools**

</details>

Generated a self-contained Lean 4 mini-project:

- [Download the complete project](sandbox:/mnt/data/lean-port-bindings.zip)
- [Open `Main.lean`](sandbox:/mnt/data/lean-port-bindings/Main.lean)
- [Read the instructions](sandbox:/mnt/data/lean-port-bindings/README.md)

The core construction is:

\[
\operatorname{Port}(t)
\xrightarrow{\mathrm{project}}
\operatorname{Binding}(t)
\xrightarrow{f}
\operatorname{Widget}.
\]

It includes:

```lean
inductive Port : PortType → Type where
  | chartDocument    : Port .document
  | pipelineDocument : Port .document
  | tableDocument    : Port .document
  | chartSelection   : Port .selection
```

The indexed type prevents even stating an identity link between a document port and a selection port.

Identity links generate an equivalence relation:

```lean
inductive Linked : {t : PortType} → Port t → Port t → Prop where
  | refl ...
  | chart_pipeline :
      Linked Port.chartDocument Port.pipelineDocument
  | pipeline_table :
      Linked Port.pipelineDocument Port.tableDocument
  | symm ...
  | trans ...
```

Bindings are quotient classes:

```lean
abbrev Binding (t : PortType) :=
  Quotient (portSetoid t)

def project {t : PortType} (p : Port t) : Binding t :=
  Quotient.mk (portSetoid t) p
```

The first central proof states that linked ports have the same quotient projection:

```lean
theorem linked_ports_same_binding
    {t : PortType} {p q : Port t}
    (h : Linked p q) :
    project p = project q := by
  exact Quotient.sound h
```

Lean’s quotient construction is based on a setoid, while `Quotient.sound` states that related representatives become equal in the quotient. Functions out of a quotient are defined by proving that the underlying function respects the equivalence relation. citeturn371960view0turn371960view1

The program also proves the quotient’s factorization property:

```lean
def factor
    (g : Port t → α)
    (respects : ∀ p q, Linked p q → g p = g q) :
    Binding t → α :=
  Quotient.lift g respects
```

and its uniqueness:

```lean
theorem factor_unique
    (g : Port t → α)
    (respects : ∀ p q, Linked p q → g p = g q)
    (u : Binding t → α)
    (commutes : ∀ p, u (project p) = g p) :
    u = factor g respects
```

The concrete requested function is:

```lean
def f : Binding .document → Widget :=
  widgetOfBinding
```

with the theorem:

```lean
theorem chart_pipeline_same_widget :
    f (project Port.chartDocument) =
      f (project Port.pipelineDocument) := by
  exact congrArg f chart_pipeline_same_binding
```

Running:

```bash
lean --run Main.lean
```

is intended to print:

```text
chart:    <select aria-label="Shared document">Document</select>
pipeline: <select aria-label="Shared document">Document</select>
table:    <select aria-label="Shared document">Document</select>
```

The project pins Lean `v4.32.2` and uses only `Init`. I could not execute the Lean checker in this environment because no Lean toolchain is installed and external toolchain downloads are unavailable.


---

> [image: sediment://file_000000004e3481f787bbdddbc030330a]
> 1. (x: 82%, y: 69%) asked sol to go ham on mathematical foundations of its PortBindingResolverRegistry stuff

> forget the image. Create a list of small self contained projects to really figure out the details of this PBUI system, so that we can validate individual subsystems and then how they compose. The idea is to give each of these to a set of phd students to have them build it and assess and refine it, and then in a second pass (later on) put them together to see how they compose. Write a detailed set of project documents that conain the full framing of each subproject, as markdown + pdf. I will then hand them out to be worked on and then we can test them as users / explore the different scenarios and constellations and concerns and such.

```unknown
bash -lc cat /home/oai/skills/pdfs/SKILL.md
```

<details><summary>💭 Thinking</summary>

**Planning documentation**

I’m outlining a detailed, research-oriented documentation set from the provided project brief. I’ll preserve its architecture, formalize implementation guidance, and use established references without exposing internal research mechanics.

**Planned documentation**

</details>

```unknown
bash -lc grep -n '^#\|^##\|^###' /mnt/data/PRESENTATION-BASED-UI-ARCHITECTURES-BEYOND-CLIM.md | sed -n '1,260p'; printf '\n--- refs tail ---\n'; tail -n 260 /mnt/data/PRESENTATION-BASED-UI-ARCHITECTURES-BEYOND-CLIM.md | sed -n '1,260p'
```

<details><summary>💭 Thinking</summary>

**Structuring project briefs**

I’m organizing the first pass into focused, self-contained research projects covering semantics, querying, capabilities, ports, composition, linking, interaction, rules, runtime behavior, replication, and proof validation. I’ll also define explicit interfaces for later integration.

**Structured project briefs**

**Selecting research projects**

I’m settling on fourteen focused projects, spanning capabilities, typed composition, bidirectional links, interaction semantics, runtime behavior, replication, mechanized proofs, and evaluation. I’ll package individual briefs alongside an integrated omnibus and shared research index.

**Selected research projects**

**Defining project standards**

I’m setting shared expectations: each project will include a toy domain, formal model, executable prototype, tests, evaluation plan, and integration adapter. I’ll use common interchange artifacts so independent results can compose later without forcing early dependencies.

**Defined project standards**

</details>

```unknown
bash -lc which pandoc; which xelatex; which latexmk; pandoc --version | head -2; xelatex --version | head -2
```

<details><summary>💭 Thinking</summary>

**Preparing deliverables**

I’m completing the remaining project briefs, program charter, composition plan, shared index, omnibus document, and validation package. I’ll then render and inspect the Markdown and PDF outputs for consistency and usability.

**Prepared deliverables**

</details>

```unknown
bash -lc cat /home/oai/skills/pdfs/SKILL.md && printf '\n--- output tree ---\n' && find /mnt/data/pbui-research-projects -maxdepth 3 -type f | sort | sed -n '1,240p' && printf '\n--- helper tail ---\n' && sed -n '1,320p' /tmp/pbui_gen_common.py
```

<details><summary>💭 Thinking</summary>

**Created, rendered, validated, and packaged PBUI research documents and PDFs**

</details>

# PBUI subsystem research program

## Complete package

[Download the complete research package](sandbox:/mnt/data/pbui-research-projects.zip)

The archive contains:

- fifteen independently distributable project briefs in Markdown and PDF;
- fifteen self-contained handout ZIPs, one per student team;
- a 128-page combined compendium;
- the program handbook and project-assignment index;
- a shared JSONL interoperability contract;
- a common analytical-workbench fixture;
- six mandatory cross-project scenario traces;
- an evaluation rubric and evidence-labeling scheme;
- a controlled phase-two composition plan;
- capsule-manifest templates;
- document and PDF generation scripts.

## Combined documents

| Document | Markdown | PDF |
|---|---|---|
| Full 15-project compendium | [Markdown](sandbox:/mnt/data/PBUI-RESEARCH-PROJECTS-COMPENDIUM.md) | [128-page PDF](sandbox:/mnt/data/PBUI-RESEARCH-PROJECTS-COMPENDIUM.pdf) |
| Program handbook | [Markdown](sandbox:/mnt/data/PBUI-SUBSYSTEM-RESEARCH-PROGRAM-HANDBOOK.md) | [PDF](sandbox:/mnt/data/PBUI-SUBSYSTEM-RESEARCH-PROGRAM-HANDBOOK.pdf) |
| Assignment and project index | [Markdown](sandbox:/mnt/data/PBUI-RESEARCH-PROJECT-INDEX.md) | [PDF](sandbox:/mnt/data/PBUI-RESEARCH-PROJECT-INDEX.pdf) |

The PDF editions use LaTeX-rendered mathematical notation and embedded text and mathematics fonts.

## Individual project handouts

Each handout ZIP contains `PROJECT.md`, `PROJECT.pdf`, the shared contract, evaluation rubric, common fixtures, phase-two composition notes, metadata, and a project-specific capsule-manifest template.

| Project | Markdown | PDF | Self-contained handout |
|---|---|---|---|
| **P01 — Semantic Identity and the Subject Registry** | [MD](sandbox:/mnt/data/pbui-research-projects/projects/P01-semantic-identity-subject-registry.md) | [PDF](sandbox:/mnt/data/pbui-research-projects/pdf/P01-semantic-identity-subject-registry.pdf) | [ZIP](sandbox:/mnt/data/pbui-research-projects/handout-zips/P01-semantic-identity-subject-registry.zip) |
| **P02 — Occurrence Semantics and the Concurrent React Adapter** | [MD](sandbox:/mnt/data/pbui-research-projects/projects/P02-occurrence-lifecycle-react-adapter.md) | [PDF](sandbox:/mnt/data/pbui-research-projects/pdf/P02-occurrence-lifecycle-react-adapter.pdf) | [ZIP](sandbox:/mnt/data/pbui-research-projects/handout-zips/P02-occurrence-lifecycle-react-adapter.zip) |
| **P03 — Inspectable Typed Selectors and Selection Evidence** | [MD](sandbox:/mnt/data/pbui-research-projects/projects/P03-typed-selector-language-evidence.md) | [PDF](sandbox:/mnt/data/pbui-research-projects/pdf/P03-typed-selector-language-evidence.pdf) | [ZIP](sandbox:/mnt/data/pbui-research-projects/handout-zips/P03-typed-selector-language-evidence.zip) |
| **P04 — Recursive Rules, Fixed Points, and Provenance** | [MD](sandbox:/mnt/data/pbui-research-projects/projects/P04-recursive-rules-fixed-points-provenance.md) | [PDF](sandbox:/mnt/data/pbui-research-projects/pdf/P04-recursive-rules-fixed-points-provenance.pdf) | [ZIP](sandbox:/mnt/data/pbui-research-projects/handout-zips/P04-recursive-rules-fixed-points-provenance.zip) |
| **P05 — Operations, Capabilities, and Invariant-Preserving Affordances** | [MD](sandbox:/mnt/data/pbui-research-projects/projects/P05-operations-capabilities-invariants.md) | [PDF](sandbox:/mnt/data/pbui-research-projects/pdf/P05-operations-capabilities-invariants.pdf) | [ZIP](sandbox:/mnt/data/pbui-research-projects/handout-zips/P05-operations-capabilities-invariants.zip) |
| **P06 — Typed Ports and the Binding Quotient Compiler** | [MD](sandbox:/mnt/data/pbui-research-projects/projects/P06-typed-ports-binding-quotient-compiler.md) | [PDF](sandbox:/mnt/data/pbui-research-projects/pdf/P06-typed-ports-binding-quotient-compiler.pdf) | [ZIP](sandbox:/mnt/data/pbui-research-projects/handout-zips/P06-typed-ports-binding-quotient-compiler.zip) |
| **P07 — Open Components, Plugin Signatures, and Composition** | [MD](sandbox:/mnt/data/pbui-research-projects/projects/P07-open-components-plugin-composition.md) | [PDF](sandbox:/mnt/data/pbui-research-projects/pdf/P07-open-components-plugin-composition.pdf) | [ZIP](sandbox:/mnt/data/pbui-research-projects/handout-zips/P07-open-components-plugin-composition.zip) |
| **P08 — Bidirectional Links and Consistency Restoration** | [MD](sandbox:/mnt/data/pbui-research-projects/projects/P08-bidirectional-links-consistency-restoration.md) | [PDF](sandbox:/mnt/data/pbui-research-projects/pdf/P08-bidirectional-links-consistency-restoration.pdf) | [ZIP](sandbox:/mnt/data/pbui-research-projects/handout-zips/P08-bidirectional-links-consistency-restoration.zip) |
| **P09 — Coalgebraic Interaction Machines** | [MD](sandbox:/mnt/data/pbui-research-projects/projects/P09-coalgebraic-interaction-machines.md) | [PDF](sandbox:/mnt/data/pbui-research-projects/pdf/P09-coalgebraic-interaction-machines.pdf) | [ZIP](sandbox:/mnt/data/pbui-research-projects/handout-zips/P09-coalgebraic-interaction-machines.zip) |
| **P10 — Algebraic Interaction Programs and Effect Handlers** | [MD](sandbox:/mnt/data/pbui-research-projects/projects/P10-algebraic-effects-workflow-handlers.md) | [PDF](sandbox:/mnt/data/pbui-research-projects/pdf/P10-algebraic-effects-workflow-handlers.pdf) | [ZIP](sandbox:/mnt/data/pbui-research-projects/handout-zips/P10-algebraic-effects-workflow-handlers.zip) |
| **P11 — Incremental and Differential Evaluation** | [MD](sandbox:/mnt/data/pbui-research-projects/projects/P11-incremental-differential-evaluation.md) | [PDF](sandbox:/mnt/data/pbui-research-projects/pdf/P11-incremental-differential-evaluation.pdf) | [ZIP](sandbox:/mnt/data/pbui-research-projects/handout-zips/P11-incremental-differential-evaluation.zip) |
| **P12 — Local-First Replicated Bindings and Topology** | [MD](sandbox:/mnt/data/pbui-research-projects/projects/P12-local-first-replicated-bindings-topology.md) | [PDF](sandbox:/mnt/data/pbui-research-projects/pdf/P12-local-first-replicated-bindings-topology.pdf) | [ZIP](sandbox:/mnt/data/pbui-research-projects/handout-zips/P12-local-first-replicated-bindings-topology.zip) |
| **P13 — Explanation, Accessibility, and Proof-Relevant Interaction** | [MD](sandbox:/mnt/data/pbui-research-projects/projects/P13-explanation-accessibility-proof-relevant-interaction.md) | [PDF](sandbox:/mnt/data/pbui-research-projects/pdf/P13-explanation-accessibility-proof-relevant-interaction.pdf) | [ZIP](sandbox:/mnt/data/pbui-research-projects/handout-zips/P13-explanation-accessibility-proof-relevant-interaction.zip) |
| **P14 — Mechanized Semantic Kernel and Proof-Carrying Compilation** | [MD](sandbox:/mnt/data/pbui-research-projects/projects/P14-mechanized-semantic-kernel-proof-carrying-compilation.md) | [PDF](sandbox:/mnt/data/pbui-research-projects/pdf/P14-mechanized-semantic-kernel-proof-carrying-compilation.pdf) | [ZIP](sandbox:/mnt/data/pbui-research-projects/handout-zips/P14-mechanized-semantic-kernel-proof-carrying-compilation.zip) |
| **P15 — Conformance, Model-Based Testing, and Comparative Benchmarking** | [MD](sandbox:/mnt/data/pbui-research-projects/projects/P15-conformance-model-based-testing-benchmarking.md) | [PDF](sandbox:/mnt/data/pbui-research-projects/pdf/P15-conformance-model-based-testing-benchmarking.pdf) | [ZIP](sandbox:/mnt/data/pbui-research-projects/handout-zips/P15-conformance-model-based-testing-benchmarking.zip) |

## What each brief contains

Every project document includes:

- the problem framing and subsystem boundary;
- research questions and falsifiable hypotheses;
- explicit non-goals;
- a formal object of study;
- a minimum executable API;
- required work packages;
- mandatory experiments and competing-design comparisons;
- proof, validation, and counterexample obligations;
- performance or user-study measurements;
- a composition capsule and reliance statement;
- risk cases the team must actively attempt to produce;
- stretch directions;
- a week-by-week schedule;
- selected foundational readings;
- final handoff questions.

P06 is the focused investigation of the proposed `PortBindingResolverRegistry`: typed contracts, endpoint equations, generated equivalence relations, quotient/coequalizer semantics, shared-resource projection, persistent binding identity, dynamic unlinking, and a small mechanized theorem.

## Shared experimental structure

All projects use the same miniature analytical workbench: a source browser, chart, pipeline, and table. They share six required scenarios:

1. the same semantic subject through different rendered occurrences;
2. refined typed selection;
3. identity linking between document ports;
4. transformed row-selection-to-filter linking;
5. stale occurrence and revoked-authority handling;
6. concurrent link and unlink operations on offline replicas.

The first pass forbids teams from importing each other’s implementations. They compose only through fixtures, versioned schemas, and the `pbui-research/0.1` JSONL adapter. The later composition pass is divided into five controlled constellations rather than one immediate all-system integration.

The 21 generated PDFs passed structural preflight, use embedded fonts, and were visually sampled across title pages, mathematical sections, code listings, project boundaries, and appendices. The package archive and all fifteen handout archives passed CRC validation.


---

> Implement P06, here's a JSX foundation you can reuse parts off to make a selfcontained result.

<details><summary>💭 Thinking</summary>

**Reviewing the project**

I’m checking the attached P06 brief and JSX foundation first, then I’ll map requirements into the existing structure. I’m also looking for files that reveal expected routes, interactions, styling, and validation criteria.

**Reviewed the project**

</details>

I’m extracting P06’s specification and reusable JSX conventions, then building a standalone implementation with an executable demo, tests, and formal engineering notes.

<details><summary>💭 Thinking</summary>

**Searched Project P06 files by title**

</details>

```unknown
bash -lc set -euo pipefail
printf '%s\n' '--- P06 brief ---'
wc -l /mnt/data/pbui-research-projects/projects/P06-typed-ports-binding-quotient-compiler.md
sed -n '1,260p' /mnt/data/pbui-research-projects/projects/P06-typed-ports-binding-quotient-compiler.md
printf '%s\n' '--- remainder ---'
sed -n '261,620p' /mnt/data/pbui-research-projects/projects/P06-typed-ports-binding-quotient-compiler.md
printf '%s\n' '--- handout zip listing ---'
unzip -l /mnt/data/pbui-research-projects/handout-zips/P06-typed-ports-binding-quotient-compiler.zip | sed -n '1,240p'

```

<details><summary>💭 Thinking</summary>

**Planning the implementation**

I’m translating P06 into a standalone React prototype with the shared trace contract, editable bindings, runtime projection, compiler validation, and a small testable adapter so the result is usable rather than just visual.

**Planned the implementation**

</details>

```unknown
bash -lc cat /home/oai/skills/pdfs/SKILL.md
```

<details><summary>💭 Thinking</summary>

**Building the prototype**

I’m implementing the standalone P06 package now, combining the visual foundation with a dependency-light core, an interactive browser demo, validation tests, fixture data, documentation, and reproducible scripts.

**Designing the core**

I’m defining strict port compatibility, graph-based equivalence classes, deterministic union-find compilation, stable external binding IDs, runtime projections, diagnostics, and dependency-light browser execution so the prototype remains reproducible.

**Designed the core**

**Inspected P06 requirements and implemented the port-binding compiler runtime app**

</details>

```json
{"open":[{"ref_id":"https://unpkg.com/react@18.3.1/umd/react.production.min.js"},{"ref_id":"https://unpkg.com/react-dom@18.3.1/umd/react-dom.production.min.js"},{"ref_id":"https://unpkg.com/react@18.3.1/LICENSE"}],"response_length":"short"}
```

<details><summary>💭 Thinking</summary>

**Searched 1 website**

</details>

```unknown
bash -lc set -euo pipefail
curl -L --fail --silent --show-error 'https://unpkg.com/react@18.3.1/umd/react.production.min.js' -o /mnt/data/react.production.min.js
wc -c /mnt/data/react.production.min.js
head -c 120 /mnt/data/react.production.min.js | cat

```

<details><summary>💭 Thinking</summary>

**Downloaded the React production bundle**

</details>

```json
{"search_query":[{"q":"React 18.3.1 UMD production min js raw GitHub"},{"q":"ReactDOM 18.3.1 UMD production min js raw GitHub"}],"response_length":"short"}
```

<details><summary>💭 Thinking</summary>

**Searched 12 websites**

</details>

```json
{"open":[{"ref_id":"https://cdnjs.cloudflare.com/ajax/libs/react/18.3.1/umd/react.production.min.js"}],"response_length":"short"}
```

<details><summary>💭 Thinking</summary>

**Searching 1 website**

</details>

```json
{"search_query":[{"q":"site:raw.githubusercontent.com cdnjs react 18.3.1 umd react.production.min.js"},{"q":"site:github.com/cdnjs/cdnjs react 18.3.1 umd react.production.min.js"}],"response_length":"short"}
```

<details><summary>💭 Thinking</summary>

**Searched 4 websites**

</details>

```json
{"search_query":[{"q":"react.production.min.js 18.3.1 umd","domains":["cdnjs.cloudflare.com"]},{"q":"react-dom.production.min.js 18.3.1 umd","domains":["cdnjs.cloudflare.com"]}],"response_length":"short"}
```

<details><summary>💭 Thinking</summary>

**Searching react-dom.production.min.js 18.3.1 umd**

**Fetched React UMD and production bundle contents**

</details>

```unknown
bash -lc sed -n '1,320p' /mnt/data/lean-port-bindings/Main.lean 2>/dev/null || true
```

<details><summary>💭 Thinking</summary>

**Implementing the package**

I’m finishing the standalone P06 lab with its contract compiler, runtime projections, browser demo, tests, adapter, benchmark, counterexamples, and proof artifact. I’m also preserving the supplied JSX visual language while keeping the core dependency-light.

**Implemented the package**

</details>

# P06 implementation

[Download the complete P06 artifact](sandbox:/mnt/data/P06-typed-ports-binding-quotient-compiler.zip)

The archive is a self-contained project. It includes the TypeScript semantic kernel, compiled JavaScript, dependency-free browser laboratory, React adapter, tests, benchmarks, counterexamples, JSONL composition capsule, detailed report, and Lean proof development.

## Run it

```bash
unzip P06-typed-ports-binding-quotient-compiler.zip
cd p06-port-binding-lab

# Build, test, validate schemas, and replay shared traces
npm run verify

# Start the interactive laboratory
npm run demo
```

No package installation is required for the compiled artifact, tests, adapter, or browser demo. TypeScript is only needed when rebuilding `dist/` from `src/`.

## Interactive result

[View the laboratory screenshot](sandbox:/mnt/data/p06-port-binding-lab/docs/demo-screenshot.png)

The laboratory presents chart, pipeline, and table widgets alongside:

- typed input and output port cards;
- identity-link compatibility checking;
- explicit endpoint selection;
- quotient classes and projection maps;
- allocated resources and current values;
- active link declarations and provenance;
- merge-policy and unlink-policy controls;
- reference-versus-union-find differential experiments;
- finite factorization experiments;
- minimized counterexamples;
- topology and resource-churn traces.

The visual adapter retains the supplied foundation’s central idea that screen objects are typed, live presentations participating in a global interaction mode. fileciteturn0file0L7-L24 It also reuses the foundation’s presentation wrapper and shell-level interaction grammar, while replacing its type-only acceptance test with typed port selection, compatibility judgment, and link compilation. fileciteturn0file0L89-L120 The thick-bordered, independently addressable widget panels follow the supplied tile-oriented UI vocabulary. fileciteturn0file0L743-L783

## Principal implementation

The central API is `PortBindingResolverRegistry`:

```ts
const registry = new PortBindingResolverRegistry({
  engine: "optimized",
  verifyOptimizedAgainstReference: true,
});

registry
  .declare(chartDocument, {
    sort: "document",
    key: "doc-a",
  })
  .declare(pipelineDocument, {
    sort: "document",
    key: "doc-b",
  })
  .compile();

const judgment =
  registry.checkLink(chartDocument, pipelineDocument);

if (judgment.ok) {
  registry.identify(
    chartDocument,
    pipelineDocument,
    {
      linkId: "chart-pipeline-document",

      // Required because the two previous resources
      // contain different values.
      mergePolicy: {
        kind: "prefer-left",
        left: chartDocument,
      },
    },
  );
}
```

Once linked:

```ts
const chartProjection =
  registry.projection(chartDocument);

const pipelineProjection =
  registry.projection(pipelineDocument);

console.assert(
  chartProjection.bindingId ===
    pipelineProjection.bindingId,
);

console.assert(
  chartProjection.resourceId ===
    pipelineProjection.resourceId,
);

pipelineProjection.set({
  sort: "document",
  key: "doc-b",
});

console.assert(
  chartProjection.get().key === "doc-b",
);
```

The semantic path is:

\[
P_\tau
\xrightarrow{q_\tau}
Q_\tau
\xrightarrow{v_\tau}
\operatorname{Resource}(\tau)
\xrightarrow{\pi_p}
\text{widget}.
\]

Here:

- \(P_\tau\) contains local port occurrences in contract fiber \(\tau\);
- link declarations generate an equivalence relation on \(P_\tau\);
- \(Q_\tau\) is the quotient set of binding classes;
- \(q_\tau\) projects each local port onto its class;
- \(v_\tau\) allocates one resource for each class;
- the widget receives a typed projection onto that resource.

## Contract compatibility

Identity compatibility is deliberately stricter than payload-type equality. Each contract includes:

```ts
interface PortContractSpec {
  contractId: string;
  semanticTag: string;
  payloadSort: string;
  mode:
    | "read"
    | "write"
    | "read-write"
    | "event-source"
    | "event-sink";
  authorityDomain: string;
  multiplicity: "one" | "optional" | "many";
  updateAlgebra: string;
  lifetime:
    | "component"
    | "workspace"
    | "persistent"
    | "replicated";
}
```

Identity linking requires equality of:

- semantic tag;
- payload sort;
- temporal/read-write mode;
- authority domain;
- multiplicity;
- update algebra;
- lifetime.

For example, these are rejected even though both carry documents:

```text
chart.document
  semanticTag = primary-document
  mode        = read-write

pipeline.outputDocument
  semanticTag = derived-document
  mode        = read
```

That connection could be meaningful, but it is not equality. It belongs in a transformed-link or directed-process subsystem rather than in P06’s identity quotient.

## Reference and optimized compilers

Two independent connectivity algorithms are included:

```text
src/reference.ts
    graph traversal and transparent connected components

src/optimized.ts
    union-find with rank and path compression
```

Both produce the same normalized semantic plan:

```ts
interface SemanticBindingClass {
  classKey: string;
  contractFingerprint: string;
  contract: PortContractSpec;
  members: readonly string[];
  linkIds: readonly string[];
}
```

Union-find representatives never become public binding IDs. Representatives are implementation artifacts and can vary with insertion order, rank decisions, or recompilation.

The persistence layer assigns separate external identities:

```ts
interface PersistentBindingClass
  extends SemanticBindingClass {
  bindingId: string;
  anchor: string;
  birthOrdinal: number;
  lineage: BindingLineage;
}
```

This permits the optimized compiler to change internally without making widget resource identity depend on a union-find root.

## Dynamic topology

Linking, unlinking, port removal, and reload all compile a candidate plan before committing it.

### Merging

When a link combines classes whose resources disagree, the caller must choose a policy:

```ts
type MergePolicy =
  | { kind: "require-equal" }
  | { kind: "preserve-winner" }
  | {
      kind: "prefer-left";
      left: PortAddress;
    }
  | {
      kind: "prefer-right";
      right: PortAddress;
    }
  | {
      kind: "user-choice";
      value: unknown;
    };
```

Quotient semantics decides that there will be one class. It does not decide which preexisting value survives.

### Unlinking

Unlinking also requires an explicit policy:

```ts
registry.unlink("chart-pipeline-document", {
  policy: {
    kind: "copy-current",
  },
});
```

Available policies are:

```ts
type UnlinkPolicy =
  | { kind: "copy-current" }
  | { kind: "reset" }
  | { kind: "history-restore" }
  | {
      kind: "user-choice";
      values: Record<string, unknown>;
    };
```

This avoids claiming that quotienting has an inverse. Once two previous values have been collapsed into one binding, mathematics does not canonically recover the old independent values.

## Universal factorization

The runtime exposes a finite version of the quotient’s universal property:

```ts
const witness = registry.factor(
  port => interpretation.get(port),
  (left, right) =>
    semanticEqual(left, right),
);
```

A successful witness contains one value per binding class and verifies that the original port interpretation commutes with projection:

\[
g=\bar g\circ q.
\]

This provides a useful plugin boundary: a renderer, allocator, serializer, or instrumentation layer that respects declared links can operate over binding classes instead of repeatedly interpreting individual link equations.

## React adapter

[Open `P06PortBindingLab.jsx`](sandbox:/mnt/data/p06-port-binding-lab/react/P06PortBindingLab.jsx)

The React component is intentionally an adapter, not another semantic implementation:

```jsx
import P06PortBindingLab
  from "./react/P06PortBindingLab.jsx";

export default function App() {
  return <P06PortBindingLab />;
}
```

It imports `react/core.mjs`, which delegates to the canonical compiled TypeScript modules under `dist/`.

The React runtime itself is supplied by the host application. The dependency-free `web/` version is the no-install reproducible demonstration.

## Formal development

[Open the Lean development](sandbox:/mnt/data/p06-port-binding-lab/proofs/Main.lean)

The Lean model uses indexed port types:

```lean
inductive Contract where
  | primaryDocument
  | rowSelection
  | derivedDocument

inductive Port : Contract → Type where
  | chartDocument :
      Port .primaryDocument
  | pipelineDocument :
      Port .primaryDocument
  | tableDocument :
      Port .primaryDocument
  | chartSelection :
      Port .rowSelection
```

A document port and selection port cannot even be passed to the same identity-link relation without violating the index.

Bindings are quotients:

```lean
abbrev Binding (c : Contract) :=
  Quotient (portSetoid c)

def project {c : Contract}
    (p : Port c) : Binding c :=
  Quotient.mk (portSetoid c) p
```

The development supplies proof terms for:

```lean
theorem linked_ports_same_binding
theorem factor_commutes
theorem factor_unique
theorem chart_pipeline_same_binding
theorem chart_table_same_binding
theorem chart_pipeline_same_resource
theorem chart_pipeline_same_widget
```

Lean 4 was not installed in the assembly environment, so this file was not accepted by the checker here. The manifest therefore classifies it as unchecked proof source rather than verified evidence. The pinned toolchain is recorded under `proofs/lean-toolchain`.

## Validation completed

The final verification run completed:

```text
TypeScript build                          passed
React JSX syntax check                   passed
Node test suite                          20 passed, 0 failed
Generated typed graphs                   2,000
Reference/optimized differential check   passed
Capsule manifest validation              passed
JSON schema structural checks            passed
Identity-link trace replay               passed
Concurrent-topology trace                typed response
Transformed-link trace                   typed unsupported response
Browser server smoke                     passed
ZIP integrity test                       passed
Lean checker                             unavailable
```

The generated tests cover duplicates, cycles, disconnected components, randomized declaration order, incompatible contract fibers, persistence up to ID renaming, shared resource projection, explicit unlinking, unaffected-resource preservation, and finite factorization.

The benchmark includes graph sizes from 10 through 10,000 ports. It produced an important negative result: union-find alone does not substantially improve whole-plan compilation because contract validation, canonical sorting, hashing, persistent-ID matching, and plan normalization dominate much of the runtime.

## Documentation

- [Project README](sandbox:/mnt/data/p06-port-binding-lab/README.md)
- [Detailed framing and implementation report](sandbox:/mnt/data/p06-port-binding-lab/report/REPORT.md)
- [API reference](sandbox:/mnt/data/p06-port-binding-lab/docs/API.md)
- [Benchmark report](sandbox:/mnt/data/p06-port-binding-lab/docs/BENCHMARKS.md)
- [Evidence ledger](sandbox:/mnt/data/p06-port-binding-lab/docs/EVIDENCE.md)
- [Demonstration walkthrough](sandbox:/mnt/data/p06-port-binding-lab/report/DEMO-WALKTHROUGH.md)
- [Handoff note](sandbox:/mnt/data/p06-port-binding-lab/report/HANDOFF.md)
- [Composition capsule manifest](sandbox:/mnt/data/p06-port-binding-lab/capsule/manifest.json)

The archive SHA-256 is:

```text
cc752318d60d55df8b36ba0368f40a4defea0a1f2511e961badeb98b3d6eebae
```


---

> Make a pdf so I can read the maths. With toc

I’m assembling the P06 implementation notes, API, proof sketch, benchmarks, and formal model into one typeset PDF with a table of contents and properly rendered mathematics.

```unknown
bash -lc set -euo pipefail
find /mnt/data/p06-port-binding-lab -maxdepth 3 -type f | sort | sed -n '1,240p'

```

<details><summary>💭 Thinking</summary>

**Inspected P06 files and source archive contents for PDF creation**

**Creating the PDF report**

I’m preparing a standalone, readable PDF from the P06 implementation summary, including a table of contents, equations, reconciliations, and implementation notes. I’m keeping the mathematics organized so it can be read independently.

**Created the PDF report**

</details>

```unknown
bash -lc set -euo pipefail
which pandoc
which xelatex
fc-list | sed -n '1,40p'
```

<details><summary>💭 Thinking</summary>

**Checked PDF generation tools and available fonts**

</details>

I’m typesetting a focused P06 monograph rather than dumping the implementation README: the port model, compatibility judgments, generated equivalence relation, quotient/coequalizer, universal property, runtime projection, merge/unlink semantics, compiler correctness, API, tests, and Lean proof outline.

```unknown
bash -lc cat > /mnt/data/P06-TYPED-PORTS-BINDING-QUOTIENT-COMPILER.md <<'EOF'
---
title: "P06 — Typed Ports and the Binding Quotient Compiler"
subtitle: "Mathematical semantics, executable architecture, and verification plan"
author: "PBUI Subsystem Research Program"
date: "August 2026"
lang: en-US
toc: true
toc-depth: 3
numbersections: true
papersize: letter
geometry:
  - margin=0.86in
fontsize: 10.5pt
mainfont: "Noto Serif"
sansfont: "Inter"
monofont: "DejaVu Sans Mono"
mathfont: "Latin Modern Math"
colorlinks: true
linkcolor: "1F4E79"
urlcolor: "1F4E79"
header-includes:
  - |
    \usepackage{microtype}
    \usepackage{booktabs}
    \usepackage{longtable}
    \usepackage{array}
    \usepackage{mathtools}
    \usepackage{amssymb}
    \usepackage{stmaryrd}
    \usepackage{fvextra}
    \usepackage{xcolor}
    \usepackage{tcolorbox}
    \usepackage{enumitem}
    \usepackage{tikz-cd}
    \DefineVerbatimEnvironment{Highlighting}{Verbatim}{breaklines,breakanywhere,commandchars=\\\{\}}
    \setlist{nosep}
    \newtcolorbox{designbox}[1]{colback=blue!3!white,colframe=blue!45!black,title=#1,breakable}
    \newtcolorbox{warningbox}[1]{colback=orange!4!white,colframe=orange!55!black,title=#1,breakable}
    \newtcolorbox{theorembox}[1]{colback=green!3!white,colframe=green!40!black,title=#1,breakable}
    \newcommand{\Port}{\mathsf{Port}}
    \newcommand{\Binding}{\mathsf{Binding}}
    \newcommand{\Resource}{\mathsf{Resource}}
    \newcommand{\Widget}{\mathsf{Widget}}
    \newcommand{\Link}{\mathsf{Link}}
    \newcommand{\Contract}{\mathsf{Contract}}
    \newcommand{\Addr}{\mathsf{Addr}}
    \newcommand{\Reach}{\mathsf{Reach}}
---

# Executive summary

P06 studies one narrow but foundational problem in a presentation-based user-interface architecture:

> How should independently developed components expose typed ports, how should identity links between those ports be compiled, and what exactly is guaranteed when several local port occurrences are treated as one binding?

The implementation target is a `PortBindingResolverRegistry` that accepts component and port declarations, checks whether proposed identity links are semantically legal, constructs the equivalence relation generated by those links, forms the corresponding quotient of port occurrences, allocates one runtime resource for each quotient class, and gives widgets typed projections onto those resources.

The mathematical path is:

\[
P_{\tau}
\xrightarrow{q_{\tau}}
Q_{\tau}
\xrightarrow{v_{\tau}}
\Resource(\tau)
\xrightarrow{\pi_p}
\Widget.
\]

Here:

- \(P_{\tau}\) is the finite set of local port occurrences having contract \(\tau\);
- identity links generate an equivalence relation \(\sim_{\tau}\) on \(P_{\tau}\);
- \(Q_{\tau}=P_{\tau}/\!\sim_{\tau}\) is the quotient set of binding classes;
- \(q_{\tau}\) is the quotient projection;
- \(v_{\tau}\) assigns one live resource to every binding class;
- \(\pi_p\) is the component-facing projection through which a widget reads or writes that resource.

The quotient answers a structural question:

> Which local port names have been identified as one binding?

It does **not** answer all operational questions. In particular, it does not choose which value survives when two previously independent resources are merged, nor does it provide a canonical inverse when a binding is later split. Those choices require explicit reconciliation and unlink policies.

The P06 artifact therefore separates:

1. **typed port contracts**;
2. **compatibility judgments**;
3. **link declarations**;
4. **equivalence closure and quotient construction**;
5. **persistent binding identity**;
6. **runtime resource projection**;
7. **merge and unlink policy**;
8. **reference and optimized compilation**;
9. **proof obligations and differential tests**.

# Reading map

Readers primarily interested in the mathematics should read Sections 4–9 and 17. Readers implementing the registry should read Sections 10–16. Readers assessing the prototype should read Sections 18–21.

The central distinction to retain is:

\[
\boxed{\text{wiring topology}}
\quad\neq\quad
\boxed{\text{runtime value policy}}.
\]

The quotient establishes topology. A separate algebra establishes value behavior.

# 1. Problem framing

## 1.1 From live presentations to component ports

A presentation-based UI treats visible objects as semantically typed and live. A rendered occurrence is not merely pixels with an attached callback; it denotes a subject and can participate in operations selected elsewhere in the interface.

P06 extends that idea from presented **subjects** to component **interfaces**. A chart, pipeline, table, inspector, or plugin is not only a renderer. It is an open component exposing typed attachment points:

```ts
const Chart = component({
  ports: {
    document: port<DocumentId>({
      semanticTag: "primary-document",
      mode: "read-write",
    }),
    selection: port<RowSelection>({
      semanticTag: "row-selection",
      mode: "write",
    }),
  },
});
```

The chart's `document` port and the pipeline's `document` port are initially distinct occurrences. An identity link states that they shall henceforth be interpreted through one global binding.

## 1.2 Why a registry is necessary

A naïve implementation may store:

```ts
chart.document = pipeline.document;
```

or copy values in event handlers. This leaves several questions unanswered:

- Were the ports actually compatible?
- Does equality of JavaScript payload types imply semantic compatibility?
- Is the link persistent across serialization?
- What happens if a third component joins the binding?
- Are duplicate and transitive links idempotent?
- What happens when an edge is removed?
- Can optimized compilation change binding IDs?
- How can a plugin consume the compiled topology without understanding every original link?
- What proof establishes that linked widgets observe the same resource?

The registry is the boundary at which these questions receive explicit answers.

## 1.3 Scope

P06 is about **identity links**. It does not claim that every component connection is equality.

The following are different protocols:

| Connection | Meaning |
|---|---|
| Identity link | Both endpoints denote one logical binding. |
| Directed map | Values flow from source to target through a transformation. |
| Bidirectional lens | Two representations synchronize according to `get`/`put` laws. |
| Event route | Discrete events are forwarded; no shared state is implied. |
| Constraint link | Peers must satisfy a relation, possibly after repair. |
| Replicated register | Distributed copies converge according to a merge protocol. |

P06 implements and validates the first protocol. It rejects attempts to smuggle the others through an equality operator.

# 2. Core vocabulary

## 2.1 Component instance

A component instance is an independently stateful semantic object, such as one chart view or one pipeline view.

\[
C \in \mathcal{C}.
\]

A visual placement may render a component instance, but placement identity and component identity are separate.

## 2.2 Port occurrence

A port occurrence is addressed by a component and a local port name:

\[
p=(c,n)\in\Addr.
\]

In TypeScript:

```ts
interface PortAddress {
  componentId: string;
  portName: string;
}
```

Two components may each contain a port named `document`; their addresses remain distinct:

```text
chart-17/document
pipeline-42/document
```

## 2.3 Port contract

A contract records more than the carrier type.

```ts
interface PortContractSpec {
  contractId: string;
  semanticTag: string;
  payloadSort: string;
  mode:
    | "read"
    | "write"
    | "read-write"
    | "event-source"
    | "event-sink";
  authorityDomain: string;
  multiplicity: "one" | "optional" | "many";
  updateAlgebra: string;
  lifetime:
    | "component"
    | "workspace"
    | "persistent"
    | "replicated";
}
```

The contract belongs to a semantic fiber. Only ports in the same identity-compatible fiber may be quotient-identified.

## 2.4 Link declaration

A link declaration is a named edge between two port occurrences:

```ts
interface IdentityLink {
  linkId: string;
  left: PortAddress;
  right: PortAddress;
}
```

The durable source of truth is the set of declarations. Quotient classes are derived.

## 2.5 Binding

A binding is an equivalence class of identity-linked ports.

\[
[p]=\{q\in P_{\tau}\mid p\sim_{\tau}q\}.
\]

The binding is not a port occurrence and not the current payload value. It is the global interface identity induced by wiring.

## 2.6 Resource

A resource is the runtime carrier assigned to a binding. It may be a local signal, Redux location, transactionally updated cell, replicated register, or server-backed capability.

```ts
interface Resource<A> {
  get(): A;
  set(value: A): void;
  subscribe(listener: (value: A) => void): () => void;
}
```

# 3. Typed compatibility

## 3.1 The compatibility judgment

Identity linking requires a judgment of the form:

\[
\Gamma\vdash p\equiv_{\mathrm{id}}q : \tau.
\]

This means that, under schema environment \(\Gamma\), ports \(p\) and \(q\) may be interpreted as occurrences of one binding with contract \(\tau\).

A conservative rule is:

\[
\frac{
  \Gamma(p)=\tau
  \qquad
  \Gamma(q)=\tau
  \qquad
  \operatorname{IdentitySafe}(\tau)
}{
  \Gamma\vdash p\equiv_{\mathrm{id}}q:\tau
}.
\]

The prototype's `IdentitySafe` comparison requires equality of the contract fields that affect meaning and update behavior.

## 3.2 Payload equality is insufficient

Consider:

```text
chart.primaryDocument      : DocumentId
pipeline.derivedDocument   : DocumentId
```

The values share a TypeScript representation, but the semantic roles differ. Identifying them would claim that a pipeline output is the chart's freely writable primary document selector. That is usually false.

Similarly:

```text
currentDocument : DocumentId, read-write
openedDocument  : DocumentId, event-source
```

The first denotes state; the second denotes a stream of occurrences. Equality of payload type does not equate temporal protocol.

## 3.3 Compatibility diagnostics

The compiler should report structured reasons:

```ts
interface CompatibilityFailure {
  ok: false;
  code:
    | "missing-port"
    | "payload-sort-mismatch"
    | "semantic-tag-mismatch"
    | "mode-mismatch"
    | "authority-mismatch"
    | "multiplicity-mismatch"
    | "update-algebra-mismatch"
    | "lifetime-mismatch";
  left: PortContractSpec;
  right: PortContractSpec;
  explanation: string;
}
```

A diagnostic is preferable to a generic Boolean because later systems need to explain why a target cannot be selected.

# 4. Links generate an equivalence relation

Fix one contract fiber \(\tau\). Let \(P_{\tau}\) be the finite set of declared port occurrences with that contract. Let \(E_{\tau}\) be the finite set of valid identity-link declarations connecting endpoints in \(P_{\tau}\).

Each link has two endpoint maps:

\[
s,t:E_{\tau}\rightrightarrows P_{\tau}.
\]

For link \(e\):

\[
s(e)=\text{left endpoint},
\qquad
 t(e)=\text{right endpoint}.
\]

The declarations generate the least equivalence relation \(\sim_{\tau}\) containing every pair \((s(e),t(e))\).

## 4.1 Closure rules

The relation is generated by:

\[
\frac{}{p\sim p}
\quad\text{(reflexivity)}
\]

\[
\frac{e\in E_{\tau}}{s(e)\sim t(e)}
\quad\text{(declared edge)}
\]

\[
\frac{p\sim q}{q\sim p}
\quad\text{(symmetry)}
\]

\[
\frac{p\sim q\qquad q\sim r}{p\sim r}
\quad\text{(transitivity)}.
\]

## 4.2 Consequences

These closure rules yield important operational laws.

**Duplicate links are idempotent.** Adding the same equation twice does not change the generated relation.

**Insertion order is irrelevant.** The semantic partition depends only on the set of accepted edges, not their processing order.

**Linking is transitive.** If chart and pipeline are linked, and pipeline and table are linked, then chart and table belong to one binding class even without a direct edge.

**Self-links are harmless.** They add no new equality.

# 5. Quotient and coequalizer semantics

## 5.1 The quotient

The quotient set is:

\[
Q_{\tau}=P_{\tau}/\!\sim_{\tau}.
\]

Its elements are equivalence classes of linked port occurrences. The quotient projection is:

\[
q_{\tau}:P_{\tau}\to Q_{\tau},
\qquad
q_{\tau}(p)=[p].
\]

For every declared link \(e\):

\[
q_{\tau}(s(e))=q_{\tau}(t(e)).
\]

## 5.2 Coequalizer formulation

The quotient is the coequalizer of the endpoint maps:

\[
E_{\tau}
\mathrel{\substack{\xrightarrow{\;s\;}\\[-0.6ex]\xrightarrow[\;t\;]{}}}
P_{\tau}
\xrightarrow{q_{\tau}}
Q_{\tau}.
\]

The equation

\[
q_{\tau}\circ s=q_{\tau}\circ t
\]

states that each pair of linked endpoints receives the same binding identity.

## 5.3 Universal property

Suppose another system interprets port occurrences in a set \(X\):

\[
g:P_{\tau}\to X.
\]

Assume it respects links:

\[
g\circ s=g\circ t.
\]

Then there exists a unique function:

\[
\bar g:Q_{\tau}\to X
\]

such that:

\[
g=\bar g\circ q_{\tau}.
\]

The commuting diagram is:

\[
\begin{tikzcd}[column sep=large,row sep=large]
E_{\tau} \arrow[r,shift left=0.7ex,"s"] \arrow[r,shift right=0.7ex,"t"']
& P_{\tau} \arrow[r,"q_{\tau}"] \arrow[dr,"g"']
& Q_{\tau} \arrow[d,dashed,"\bar g"] \\
& & X
\end{tikzcd}
\]

This property is more useful than the phrase “connected components” alone. It establishes the canonical interface through which every link-respecting renderer, allocator, serializer, or instrumentation layer may operate.

\begin{theorembox}{Factorization theorem}
For a finite identity-link graph, any port-level interpretation constant on generated equivalence classes factors uniquely through the compiled binding quotient.
\end{theorembox}

## 5.4 A finite executable witness

The runtime can expose this property as an executable check:

```ts
const witness = registry.factor(
  port => interpretation.get(port),
  (left, right) => semanticEqual(left, right),
);
```

The witness records one value per quotient class and verifies:

\[
\forall p\in P_{\tau},
\qquad
\bar g(q_{\tau}(p))=g(p).
\]

# 6. Worked example: chart, pipeline, and table

Let:

\[
P_{\mathrm{doc}}
=
\{c,p,t\},
\]

where:

- \(c=\texttt{chart/document}\);
- \(p=\texttt{pipeline/document}\);
- \(t=\texttt{table/document}\).

Declare two edges:

\[
e_1:c\leftrightarrow p,
\qquad
 e_2:p\leftrightarrow t.
\]

The generated relation satisfies:

\[
c\sim p,
\qquad
p\sim t,
\qquad
c\sim t.
\]

Therefore:

\[
Q_{\mathrm{doc}}=\{\,[c,p,t] \,\}.
\]

The quotient projection is constant:

\[
q(c)=q(p)=q(t)=b_7.
\]

The allocator assigns a document resource:

\[
v(b_7)=r_7.
\]

Every widget projection reaches the same resource:

\[
\pi_c= v\circ q(c),
\qquad
\pi_p= v\circ q(p),
\qquad
\pi_t= v\circ q(t).
\]

Thus:

\[
\pi_c=\pi_p=\pi_t=r_7.
\]

If the pipeline writes document \(d_2\) through its projection:

\[
r_7\leftarrow d_2,
\]

then the chart and table read the same value:

\[
\operatorname{read}(\pi_c)
=
\operatorname{read}(\pi_p)
=
\operatorname{read}(\pi_t)
=d_2.
\]

# 7. Structural equality versus value semantics

The quotient guarantees:

\[
q(p)=q(q')
\quad\Longrightarrow\quad
\text{both endpoints name one binding}.
\]

It does not, by itself, determine the representation of the resource or the transition policy applied to it.

## 7.1 Shared-cell interpretation

A local runtime may allocate one signal per class:

```ts
const cell = createSignal<DocumentId>("doc-a");
```

Every endpoint receives the same object.

## 7.2 Store-location interpretation

The binding may correspond to a normalized store entry:

```ts
state.bindingValues[bindingId]
```

Port projections dispatch commands that update that location.

## 7.3 Replicated interpretation

A collaborative runtime may use a replicated register:

```ts
const register = replicatedRegister<DocumentId>();
```

The quotient still determines which local endpoints refer to the register, but the register's conflict semantics belong to a separate protocol.

## 7.4 Constraint interpretation

A solver may retain local variables and enforce:

\[
x_c=x_p=x_t.
\]

The quotient is then a compilation of equality constraints rather than literal pointer aliasing.

\begin{warningbox}{Do not overclaim}
The coequalizer explains the canonical identification of interface names. It does not prove that arbitrary component code cannot maintain unsynchronized shadow state. The runtime invariant depends on all reads and writes passing through the generated projection.
\end{warningbox}

# 8. Compatible global states and pullbacks

The quotient acts on interface occurrences. A separate construction characterizes component states that agree on a linked interface.

Let:

\[
d_C:S_C\to D
\]

extract the chart document, and:

\[
d_P:S_P\to D
\]

extract the pipeline document.

The compatible pairs are the pullback:

\[
S_C\times_D S_P
=
\{(c,p)\in S_C\times S_P\mid d_C(c)=d_P(p)\}.
\]

Thus:

| Question | Construction |
|---|---|
| Which port names are one binding? | Quotient/coequalizer |
| Which local states agree on that binding? | Pullback/equalizer-like constraint |
| How does an edit restore agreement? | Transition or synchronization policy |

The P06 compiler handles the first question and constructs a runtime that makes the second condition hold by shared projection. It requires policy for the third.

# 9. Persistent binding identity

## 9.1 Why the union-find representative is not a binding ID

An optimized compiler may choose any member as the representative of an equivalence class. Rank heuristics, path compression, insertion order, or implementation version can change that representative.

Therefore:

\[
\operatorname{root}_{UF}([p])
\neq
\operatorname{identity}_{\mathrm{binding}}([p]).
\]

Public identity must be independent of optimization artifacts.

## 9.2 Canonical class key

A semantic class can be represented canonically by sorted member addresses and a contract fingerprint:

```ts
interface SemanticBindingClass {
  classKey: string;
  contractFingerprint: string;
  members: readonly string[];
  linkIds: readonly string[];
}
```

For example:

```text
contract: primary-document/read-write/workspace
members:  chart-17/document | pipeline-42/document
```

The canonical key is useful for comparison and differential testing. It is not necessarily the durable user-facing identity because adding or removing a member changes the key.

## 9.3 Persistent class identity

A persistent binding record retains lineage:

```ts
interface PersistentBindingClass
  extends SemanticBindingClass {
  bindingId: string;
  anchor: string;
  birthOrdinal: number;
  lineage: BindingLineage;
}
```

A compiler can match old and new classes using stable anchors and overlap. The exact policy must be explicit because topology edits can merge or split classes.

## 9.4 Alpha-equivalence of plans

Two compiled plans may differ only in generated binding names. Their semantics should be compared up to bijective renaming:

\[
Q_1\cong Q_2.
\]

The isomorphism must preserve:

- class membership;
- contract;
- resource value;
- link provenance;
- projection incidence.

# 10. Runtime projection API

A component should not manipulate quotient classes directly. It receives a typed projection.

```ts
interface PortProjection<A> {
  readonly port: PortAddress;
  readonly bindingId: string;
  readonly resourceId: string;
  get(): A;
  set(value: A): void;
  subscribe(listener: (value: A) => void): () => void;
}
```

The registry API may resemble:

```ts
const registry = new PortBindingResolverRegistry({
  engine: "optimized",
  verifyOptimizedAgainstReference: true,
});

registry
  .declare(chartDocument, {
    sort: "document",
    key: "doc-a",
  })
  .declare(pipelineDocument, {
    sort: "document",
    key: "doc-b",
  })
  .compile();
```

A link is checked before it is committed:

```ts
const judgment =
  registry.checkLink(chartDocument, pipelineDocument);

if (judgment.ok) {
  registry.identify(
    chartDocument,
    pipelineDocument,
    {
      linkId: "chart-pipeline-document",
      mergePolicy: {
        kind: "prefer-left",
        left: chartDocument,
      },
    },
  );
}
```

After linking:

```ts
const chartProjection =
  registry.projection(chartDocument);

const pipelineProjection =
  registry.projection(pipelineDocument);

console.assert(
  chartProjection.bindingId ===
    pipelineProjection.bindingId,
);

console.assert(
  chartProjection.resourceId ===
    pipelineProjection.resourceId,
);
```

# 11. Merge semantics

Suppose two singleton classes currently contain values:

\[
V([p])=a,
\qquad
V([q])=b.
\]

Adding a link merges the classes:

\[
[p]\sqcup[q]=[p,q].
\]

The quotient says there is now one class. It does not determine a value:

\[
V([p,q])\;=?
\]

## 11.1 Explicit merge policies

```ts
type MergePolicy<A> =
  | { kind: "require-equal" }
  | { kind: "preserve-winner" }
  | { kind: "prefer-left"; left: PortAddress }
  | { kind: "prefer-right"; right: PortAddress }
  | { kind: "join"; algebra: JoinSemilattice<A> }
  | { kind: "user-choice"; value: A };
```

### Require equal

Accept only if:

\[
a=b.
\]

### Prefer one side

An ordered interaction identifies a designated source:

\[
V([p,q])=a.
\]

This policy is deterministic but not commutative.

### Join

If values form a join-semilattice:

\[
V([p,q])=a\sqcup b.
\]

The algebra must satisfy:

\[
a\sqcup a=a,
\]

\[
a\sqcup b=b\sqcup a,
\]

\[
(a\sqcup b)\sqcup c=a\sqcup(b\sqcup c).
\]

These laws make merge order irrelevant.

## 11.2 Transactionality

The link transition should be atomic:

1. validate endpoints and contracts;
2. compile the candidate quotient;
3. determine affected old classes;
4. reconcile their values;
5. allocate or select the surviving resource;
6. publish the new projection map;
7. emit one audit event.

If reconciliation fails, the old topology remains intact.

# 12. Unlinking and topology deletion

## 12.1 Why unlink is not an inverse quotient

A quotient forgets distinctions. If two independent values \(a\) and \(b\) were merged and policy selected \(a\), the quotient contains no canonical evidence from which to reconstruct \(b\).

Therefore there is no general inverse:

\[
P/\!\sim\;\not\to P
\]

that restores prior independent resources.

## 12.2 Durable edges

The runtime must retain the generating link graph:

```ts
interface LinkEdge {
  linkId: string;
  left: PortAddress;
  right: PortAddress;
  createdAt: number;
  provenance: unknown;
}
```

Removing an edge recomputes connectivity in the affected class. A bare union-find structure is insufficient for arbitrary deletion because it has discarded the edge provenance needed to split components.

## 12.3 Unlink policies

```ts
type UnlinkPolicy<A> =
  | { kind: "copy-current" }
  | { kind: "reset" }
  | { kind: "history-restore" }
  | { kind: "user-choice"; values: Record<string, A> };
```

### Copy current

If one class splits into \(k\) components, each new component receives the current shared value.

This supports the value-preservation law:

\[
\operatorname{read}_{S}(p)
=
\operatorname{read}_{\operatorname{unlink}(S,e)}(p)
\]

immediately after unlinking.

### History restore

Restore the most recent independent value for each new class, if the runtime retained sufficient lineage. This is convenient but introduces history-sensitive semantics.

## 12.4 Locality theorem

Removing an edge affects only its previous connected component. Every other quotient class and resource projection remains unchanged.

This theorem establishes a precise invalidation frontier for incremental recompilation.

# 13. Reference compiler

The reference implementation should be deliberately obvious.

## 13.1 Algorithm

For each contract fiber:

1. construct an undirected adjacency map from accepted link edges;
2. include isolated ports as singleton vertices;
3. traverse unvisited vertices using breadth-first or depth-first search;
4. sort each component's members;
5. sort the list of components canonically;
6. derive class provenance from incident link IDs.

## 13.2 Complexity

For \(n\) ports and \(m\) links:

\[
T_{\mathrm{ref}}(n,m)=O(n+m)
\]

for connectivity, plus sorting costs used to normalize output.

The reference compiler is suitable as the executable semantic oracle.

# 14. Optimized compiler

The optimized compiler uses disjoint-set union, or union-find.

## 14.1 Operations

```ts
makeSet(port)
find(port)
union(left, right)
```

With union by rank and path compression, a sequence of operations has near-constant amortized cost:

\[
O((n+m)\,\alpha(n)),
\]

where \(\alpha\) is the inverse Ackermann function.

## 14.2 Limits

Union-find handles additions well but does not support general edge deletion by itself. P06 therefore treats it as a compilation cache, not the durable semantic model.

## 14.3 Normalization

The optimized compiler must normalize classes to the same semantic representation as the reference compiler before comparison. Raw roots are not observable output.

## 14.4 Differential correctness condition

Let:

\[
\operatorname{Ref}(G)
\]

be the normalized reference plan and:

\[
\operatorname{Opt}(G)
\]

be the normalized optimized plan. The target property is:

\[
\forall G\in\operatorname{WellTypedGraphs},
\qquad
\operatorname{Ref}(G)=\operatorname{Opt}(G).
\]

Property-based tests generate graphs with duplicates, cycles, isolated ports, shuffled declarations, and multiple fibers.

# 15. Compiler phases

A robust compilation pipeline is:

```text
component and port declarations
        ↓
contract normalization
        ↓
identity-link validation
        ↓
partition by contract fiber
        ↓
connectivity compilation
        ↓
canonical semantic classes
        ↓
persistent identity reconciliation
        ↓
value merge/unlink planning
        ↓
resource allocation
        ↓
port projection table
        ↓
diagnostics and audit record
```

Each phase should have a typed input and output. This makes the compiler inspectable and allows a reference implementation to replace an optimized phase independently.

# 16. React integration

The React adapter should be thin. It obtains a projection and renders it.

```tsx
function DocumentSelector({
  endpoint,
}: {
  endpoint: PortAddress;
}) {
  const projection = usePortProjection<DocumentId>(endpoint);
  const documentId = useSyncExternalStore(
    projection.subscribe,
    projection.get,
    projection.get,
  );

  return (
    <select
      value={documentId}
      onChange={event =>
        projection.set(event.currentTarget.value)
      }
    >
      {/* options */}
    </select>
  );
}
```

The adapter does not calculate equivalence classes. It does not copy values to linked peers. It does not assign binding identity. Those responsibilities belong to the semantic runtime.

## 16.1 The widget projection theorem

Assume widgets read only through the generated projection:

\[
\operatorname{observe}_S(p)=V_S(q(p)).
\]

If:

\[
q(p)=q(q'),
\]

then:

\[
\operatorname{observe}_S(p)
=V_S(q(p))
=V_S(q(q'))
=\operatorname{observe}_S(q').
\]

Thus linked widgets observe equal binding values in every reachable state.

# 17. Lean proof model

A small Lean model can encode contract-indexed ports so ill-typed identity links are unrepresentable.

```lean
inductive Contract where
  | primaryDocument
  | rowSelection
  | derivedDocument

inductive Port : Contract → Type where
  | chartDocument :
      Port .primaryDocument
  | pipelineDocument :
      Port .primaryDocument
  | tableDocument :
      Port .primaryDocument
  | chartSelection :
      Port .rowSelection
```

The generated relation is indexed by contract:

```lean
inductive Linked :
    {c : Contract} → Port c → Port c → Prop where
  | refl (p : Port c) : Linked p p
  | chart_pipeline :
      Linked Port.chartDocument
             Port.pipelineDocument
  | pipeline_table :
      Linked Port.pipelineDocument
             Port.tableDocument
  | symm : Linked p q → Linked q p
  | trans : Linked p q → Linked q r → Linked p r
```

A setoid packages the equivalence laws:

```lean
def portSetoid (c : Contract) : Setoid (Port c) where
  r := Linked
  iseqv := {
    refl := Linked.refl
    symm := Linked.symm
    trans := Linked.trans
  }
```

Bindings are quotient classes:

```lean
abbrev Binding (c : Contract) :=
  Quotient (portSetoid c)

def project {c : Contract}
    (p : Port c) : Binding c :=
  Quotient.mk (portSetoid c) p
```

The primary theorem is immediate from quotient soundness:

```lean
theorem linked_ports_same_binding
    {c : Contract} {p q : Port c}
    (h : Linked p q) :
    project p = project q := by
  exact Quotient.sound h
```

A function out of the quotient is defined only after proving that it respects the relation:

```lean
def factor
    (g : Port c → α)
    (respects : ∀ p q,
      Linked p q → g p = g q) :
    Binding c → α :=
  Quotient.lift g respects
```

The commuting law is:

```lean
theorem factor_commutes
    (p : Port c) :
    factor g respects (project p) = g p := by
  rfl
```

The uniqueness theorem states that every other quotient-level map with the same commuting property equals `factor g respects`.

## 17.1 Widget interpretation

```lean
inductive Widget where
  | documentPicker (title : String)
  | selectionBadge (title : String)
```

If the raw widget interpretation is constant across links, it lifts to bindings:

```lean
def f : Binding .primaryDocument → Widget :=
  factor rawWidget rawWidget_respects
```

Then:

```lean
theorem chart_pipeline_same_widget :
    f (project Port.chartDocument) =
    f (project Port.pipelineDocument) := by
  exact congrArg f chart_pipeline_same_binding
```

This mechanizes the finite quotient factorization underlying the registry.

# 18. Required invariants

A production-quality implementation should maintain the following invariants.

## 18.1 Well-typed membership

Every class contains only ports with one compatible contract:

\[
\forall B\in Q,
\quad
\exists \tau,
\quad
\forall p\in B,
\Gamma(p)=\tau.
\]

## 18.2 Total projection

Every declared port has exactly one binding:

\[
\forall p\in P,
\quad
\exists! B\in Q,
\quad
p\in B.
\]

## 18.3 Edge soundness

Every accepted link has equal projection:

\[
\forall e\in E,
\quad
q(s(e))=q(t(e)).
\]

## 18.4 Minimality

Ports are identified only when forced by the equivalence closure of accepted links:

\[
q(p)=q(q')
\Longleftrightarrow
p\sim q'.
\]

## 18.5 Resource uniqueness

Each binding class receives exactly one resource:

\[
\forall B\in Q,
\quad
\exists! r,
\quad
v(B)=r.
\]

## 18.6 Projection coherence

Every member of a class resolves to that class's resource:

\[
q(p)=B
\Longrightarrow
\operatorname{resourceOf}(p)=v(B).
\]

## 18.7 Unaffected-class stability

A topology edit preserves the identity and resource of every class outside the affected region.

## 18.8 Serialization up to renaming

Encoding and decoding preserve the semantic graph and values up to fresh generated identifiers:

\[
\operatorname{decode}(\operatorname{encode}(S))\cong S.
\]

# 19. Test program

## 19.1 Unit tests

- exact compatible ports are accepted;
- semantic-tag mismatch is rejected;
- mode mismatch is rejected;
- authority mismatch is rejected;
- duplicate links are idempotent;
- self-links are harmless;
- transitive closure yields one class;
- isolated ports remain singleton classes;
- projections of linked ports share a resource;
- setting through one projection is visible through peers;
- merge conflict without policy is rejected;
- unlink with `copy-current` preserves observed values;
- deleting one redundant edge does not split a multiply connected class.

## 19.2 Property-based graph generation

Generate finite typed graphs with:

- 0–10,000 port occurrences;
- one or more contract fibers;
- duplicate and shuffled edges;
- cycles;
- disconnected components;
- random rejected cross-fiber edges;
- random topology edit traces.

Check reference and optimized equivalence after every accepted edit.

## 19.3 Metamorphic properties

**Permutation:** shuffling declaration and edge order preserves the normalized plan.

**Duplicate insertion:** adding an existing edge preserves the plan.

**Fresh isolated port:** adding an unlinked port adds exactly one singleton class.

**Component renaming:** consistently renaming opaque component IDs produces an isomorphic plan.

**Unrelated edit locality:** changing one disconnected component preserves every other class.

## 19.4 Counterexample tests

The project should actively seek failures for:

- using union-find roots as public IDs;
- treating payload-sort equality as identity compatibility;
- destructive union without edge provenance;
- merging unequal values without a policy;
- unlinking by arbitrary root splitting;
- preserving shadow component state outside projections;
- serializing runtime object pointers;
- silently converting a transformed link into identity.

# 20. Performance interpretation

Connectivity is rarely the only cost. Whole-plan compilation also performs:

- contract validation;
- hashing and sorting;
- canonical class construction;
- persistent-ID matching;
- resource reconciliation;
- provenance aggregation;
- projection-table construction;
- diagnostics.

Even though union-find improves the asymptotic connectivity primitive, it may not substantially improve total compile time at moderate graph sizes.

A benchmark should therefore report phase-level timings rather than only `union` and `find` throughput.

\[
T_{\mathrm{total}}
=
T_{\mathrm{validate}}
+T_{\mathrm{connect}}
+T_{\mathrm{normalize}}
+T_{\mathrm{reconcile}}
+T_{\mathrm{allocate}}
+T_{\mathrm{emit}}.
\]

For dynamic workspaces, incremental locality may matter more than the difference between two linear-time batch compilers.

# 21. Integration boundary

P06 should expose a composition capsule rather than leaking internal classes.

## 21.1 Inputs

- component-instance declarations;
- typed port declarations;
- initial resource proposals;
- identity-link declarations;
- merge and unlink policies;
- optional previous compiled state for identity continuity.

## 21.2 Outputs

- normalized binding classes;
- port-to-binding projections;
- binding-to-resource mappings;
- accepted and rejected links;
- diagnostics;
- provenance and lineage;
- topology/value deltas;
- an audit trace.

## 21.3 Other subsystem dependencies

P06 composes with:

- semantic identity, which names component and domain entities;
- operation/capability validation, which authorizes link edits;
- bidirectional-link research, which handles non-identity protocols;
- interaction machines, which drive target selection and cancellation;
- incremental evaluation, which consumes topology deltas;
- replication, which assigns concurrent semantics to durable edge sets;
- mechanized verification, which checks the quotient and compiler refinement theorems.

# 22. Design decisions and rejected alternatives

## 22.1 Rejected: shared group ID as the only source of truth

Storing only:

```ts
port.bindingGroupId = "group-7";
```

makes equality easy to query but loses the generating edges. It cannot explain why ports are linked, cannot correctly remove one redundant link, and provides poor provenance.

## 22.2 Rejected: union-find as durable state

Union-find is excellent for append-only connectivity but forgets edge structure and exposes unstable representatives.

## 22.3 Rejected: payload type alone

This admits semantically invalid equalities.

## 22.4 Rejected: callback-based propagation

Pairwise event handlers scale poorly, duplicate work in cycles, and do not define a canonical global binding identity.

## 22.5 Rejected: quotient decides merge values

This is mathematically false. Topological identification and value reconciliation are distinct.

## 22.6 Accepted: graph source, quotient cache, explicit policy

The chosen architecture retains declarations, derives the quotient, separates persistent binding identity from compiler representatives, and requires explicit value policy.

# 23. Research questions remaining

1. Which contract fields are necessary and sufficient for identity safety?
2. Can contract compatibility be expressed through subtyping or refinement rather than exact equality without losing soundness?
3. Which persistent-ID policy best balances user continuity with predictable topology semantics?
4. How should history-sensitive unlink policies be represented and explained?
5. When should the runtime use full recomputation, affected-component recomputation, or fully dynamic connectivity?
6. How should binding lineage behave under concurrent merge and split operations?
7. Can a certificate checker validate optimized plans without rerunning full connectivity?
8. What is the right observational equivalence for resources implemented by signals, stores, servers, and replicated registers?
9. How should transformed links compose with identity classes without conflating equality and direction?
10. Can plugin contracts evolve across versions while preserving binding identity and safety?

# 24. Conclusion

The typed-port binding compiler is a small subsystem with unusually broad architectural consequences. Its central result is simple:

\[
\text{valid identity links}
\Longrightarrow
\text{generated equivalence relation}
\Longrightarrow
\text{quotient binding classes}
\Longrightarrow
\text{one projected resource per class}.
\]

The coequalizer gives the correct universal characterization of port identification. The runtime projection turns that structural result into widget behavior. Explicit merge and unlink policies handle information that the quotient deliberately does not contain. A reference graph compiler provides transparent semantics; union-find provides an optimization that can be tested against it; a small Lean development captures the core factorization theorem.

The most important engineering rule is:

> Persist declarations and policies, derive quotient classes, allocate resources by class, and require components to interact through typed projections.

That rule makes linking deterministic, inspectable, testable, and suitable for later composition with interaction machines, incremental computation, replication, and formal verification.

# Appendix A. Compact API sketch

```ts
interface PortBindingResolverRegistry {
  declare<A>(
    address: PortAddress,
    declaration: PortDeclaration<A>,
  ): this;

  checkLink(
    left: PortAddress,
    right: PortAddress,
  ): CompatibilityJudgment;

  identify<A>(
    left: PortAddress,
    right: PortAddress,
    options: {
      linkId: string;
      mergePolicy: MergePolicy<A>;
    },
  ): CompileResult;

  unlink<A>(
    linkId: string,
    options: {
      policy: UnlinkPolicy<A>;
    },
  ): CompileResult;

  compile(): CompileResult;

  projection<A>(
    address: PortAddress,
  ): PortProjection<A>;

  factor<A>(
    interpretation: (port: PortAddress) => A,
    equal: (left: A, right: A) => boolean,
  ): FactorizationWitness<A>;
}
```

# Appendix B. Minimal JSON trace

```json
{"type":"port.declared","port":"chart-17/document","contract":"primary-document"}
{"type":"port.declared","port":"pipeline-42/document","contract":"primary-document"}
{"type":"link.requested","link":"link-1","left":"chart-17/document","right":"pipeline-42/document"}
{"type":"link.accepted","link":"link-1","contract":"primary-document"}
{"type":"binding.merged","old":["binding-2","binding-9"],"new":"binding-2","policy":"prefer-left"}
{"type":"projection.updated","port":"pipeline-42/document","binding":"binding-2","resource":"resource-2"}
```

# Appendix C. Proof checklist

- [ ] `Linked` is an equivalence relation in every contract fiber.
- [ ] `project` identifies every declared edge.
- [ ] `project` is minimal with respect to generated equality.
- [ ] Every link-respecting interpretation factors through `Binding`.
- [ ] The factor is unique.
- [ ] The optimized compiler refines the reference quotient.
- [ ] Linked projections resolve to one resource.
- [ ] Command transitions preserve contract homogeneity.
- [ ] Unlinking preserves unaffected classes.
- [ ] Serialization preserves the plan up to generated-ID renaming.

EOF

pandoc /mnt/data/P06-TYPED-PORTS-BINDING-QUOTIENT-COMPILER.md \
  --from markdown+raw_tex+tex_math_dollars \
  --pdf-engine=xelatex \
  --toc --toc-depth=3 --number-sections \
  --highlight-style=tango \
  --metadata title="P06 — Typed Ports and the Binding Quotient Compiler" \
  -o /mnt/data/P06-TYPED-PORTS-BINDING-QUOTIENT-COMPILER.pdf

ls -lh /mnt/data/P06-TYPED-PORTS-BINDING-QUOTIENT-COMPILER.*
```

<details><summary>💭 Thinking</summary>

**Built and refined a typed ports compiler report PDF with LaTeX fixes**

</details>

[Download the P06 typeset PDF](sandbox:/mnt/data/P06-TYPED-PORTS-BINDING-QUOTIENT-COMPILER.pdf)

[Download the Markdown source](sandbox:/mnt/data/P06-TYPED-PORTS-BINDING-QUOTIENT-COMPILER.md)

The 29-page PDF includes:

- a dedicated title page;
- a clickable, three-level table of contents;
- properly typeset quotient, coequalizer, pullback, factorization, and projection equations;
- a commuting-diagram treatment of the universal property;
- the chart–pipeline–table worked example;
- merge and unlink semantics;
- reference and union-find compiler models;
- correctness invariants and test obligations;
- TypeScript and Lean code excerpts;
- embedded text, code, and mathematics fonts.

It frames P06 as a port-level extension of the supplied UI foundation, in which visible objects are typed live presentations and compatible objects participate in a global acceptance mode. fileciteturn0file0L7-L17

