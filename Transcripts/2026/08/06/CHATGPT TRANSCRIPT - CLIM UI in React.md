# CLIM UI in React

- URL: https://chatgpt.com/c/6a6cee0b-ba84-83ea-afb0-2c0cd079dac8
- Created: 2026-07-31T18:48:44.326Z

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

> Now analyze the following, using datalab and pbui.
>
> I want to be able to "link" views, where like, I have a table / dataset / pipeline / encoding open, say census dataset, with a pipeline that plots a barchart, based on the aggregation of population by city.
>
> I want to have the plot linked to the 3 things that go into it, so that if I load a different dataset, the plot, the encoding, the table view all update to have the new setup, or if I switch to a new pipeline defined on another dataset, all other views also switch accordingly. Maybe there's a little link icon active and I can interact with, maybe it's even a presentation thing + actions (especially if possible with the additions we discussed before).
>
> Anyway, the goal is to make it easy for users to create workspaces that are dedicated to a certain type of work without having to switch every view individually. Or duplicate the same workspace but use different datasets for it. etc...
>
> Write a similar study up in markdown.

<details><summary>💭 Thinking</summary>

**Inspecting project files**

I’m going to examine the uploaded project materials, identify the existing data and interface structure, and then write a Markdown study grounded in the actual implementation rather than assumptions.

**Inspected project files**

</details>

I’ll inspect the enhanced PBUI/Datalab implementation, then develop a multi-view linkage model covering APIs, reducers, interactions, persistence, and migration.

```unknown
bash -lc ls -lah /mnt/data && rm -rf /mnt/data/pbui_linked_views_study && mkdir -p /mnt/data/pbui_linked_views_study && unzip -q /mnt/data/pbui-enhanced.zip -d /mnt/data/pbui_linked_views_study && find /mnt/data/pbui_linked_views_study -maxdepth 3 -type f | sed 's#^#/##' | head -200
```

<details><summary>💭 Thinking</summary>

**Clarifying workspace linking**

I’m checking whether the current document model already links datasets, pipelines, encodings, and views, then I’ll identify what’s missing for coordinated workspace switching and presentation-oriented actions.

**Clarified workspace linking**

**Inspecting World Model and Actions**

</details>

```unknown
bash -lc cd /mnt/data/pbui_linked_views_study/pbui && for f in packages/datalab-ui/src/components/molecules/DocBar/DocBar.tsx packages/datalab-ui/src/components/organisms/Tile/Tile.tsx packages/datalab-ui/src/pbui/descriptors/tile.ts packages/datalab-ui/src/pbui/types.ts packages/datalab-ui/src/pbui/verbs.ts packages/datalab-ui/src/pbui/registry.ts packages/datalab-ui/src/appkit/registry.ts; do echo; echo '###' $f; nl -ba "$f" | sed -n '1,420p'; done
```

<details><summary>💭 Thinking</summary>

**Modeling workspace behavior**

I’m distinguishing whole-composition linking from reusable workspace templates. The existing binding handles coordinated views, while first-class workspace slots, rebind actions, and fork semantics may be needed for switching datasets or pipelines without manually changing every view.

**Modeled workspace behavior**

</details>

```unknown
bash -lc cd /mnt/data/pbui_linked_views_study/pbui && rg -n "replaceDocumentSource|createGraphicDocument|cloneGraphicDocument|rootSource|rootView|orderedTransformIds|appendTransform" packages/datalab-ui/src/model/graphicAuthoring.ts && nl -ba packages/datalab-ui/src/model/graphicAuthoring.ts | sed -n '1,520p'
```

<details><summary>💭 Thinking</summary>

**Designing reusable links**

I’m shaping the study around a composition-level binding first, then a future port-based model. This preserves the current architecture while enabling reusable workspace templates, compatible dataset rebinding, and independent workspace forks.

**Designed reusable links**

</details>

The key distinction is switching an entire graphic document versus rebinding an analytic recipe; broader links may coordinate dataset, pipeline, relation, encoding, and plot selectively with directional dependencies.

```unknown
bash -lc cd /mnt/data/pbui_linked_views_study/pbui && rg -n "use.*Schema|schema|Dataset.*Query|datasetTable|SourceRef" packages/datalab-ui/src/api packages/datalab-ui/src/apps packages/datalab-ui/src/model datalab/pkg/server datalab/pkg/store | sed -n '1,1200p'
```

<details><summary>💭 Thinking</summary>

**Inspected document, workspace cloning, schema, dataset, and UI architectures**

</details>

```json
{"search_query":[{"q":"site:lispworks.com documentation CLIM presentation types input contexts presentation translators command tables"},{"q":"site:lispworks.com documentation CLIM presentations input context accept present"},{"q":"site:lispworks.com documentation CLIM command tables translators output records"}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Creating the study**

I’m grounding the Markdown report in the enhanced PBUI/Datalab implementation, separating existing document-level linking from the broader workspace model, then documenting architecture, interactions, persistence, migration, and testing.

**Designing the study**

I’m focusing the report on three concrete gaps: source replacement currently resets analysis state, source views aren’t linked participants, and workspace duplication mirrors rather than creates an independent analytical copy.

**Created and designed the study**

**Searched 2 websites**

</details>

```unknown
bash -lc find /mnt/data/pbui_linked_views_study/pbui/packages/datalab-ui/src -maxdepth 4 -type f | sed 's#^#/##' | head -200
```

<details><summary>💭 Thinking</summary>

**Inspected datalab UI, presentation APIs, layout state, graphics, and app components**

</details>

```unknown
bash -lc nl -ba /mnt/data/pbui_linked_views_study/pbui/packages/datalab-ui/src/model/portable.ts | sed -n '1,760p'
printf '\n===== bundles =====\n'
nl -ba /mnt/data/pbui_linked_views_study/pbui/packages/datalab-ui/src/store/bundles.ts | sed -n '1,920p'
```

Because these views already project one `GraphicDocument`, I’ll preserve that boundary with typed link ports; workspace duplication must also clone logical views and bindings instead of mirroring them.

<details><summary>💭 Thinking</summary>

**Inspecting Portable Bundles and View Bindings**

</details>

```unknown
bash -lc ROOT=/mnt/data/pbui_linked_views_study/pbui/packages/datalab-ui/src
printf '%s\n' '--- chart/table/pipeline/encoding primary document usage ---'
for f in "$ROOT/apps/ChartApp/ChartApp.tsx" "$ROOT/apps/TableApp/TableApp.tsx" "$ROOT/apps/PipelineApp/PipelineApp.tsx" "$ROOT/apps/EncodingApp/EncodingApp.tsx" "$ROOT/apps/SourceApp/SourceApp.tsx"; do
  echo "### $f"; [ -f "$f" ] && rg -n "primary|useDoc|DocBar|docBound|source|view\.documents|activeDoc" "$f" | head -100 || true
done
printf '%s\n' '--- app registration locations ---'
rg -n "registerApp\(|id: \"(chart|table|pipeline|encode|source)\"|docBound" "$ROOT/apps" | head -220
printf '%s\n' '--- analysis coordinator/hooks ---'
rg -n "AnalysisCoordinator|useDocAnalysisResult|useDocAnalysis|useDocPlot|semantic|inFlight|cache" "$ROOT/appkit" | head -260
printf '%s\n' '--- census fixture fields ---'
python - <<'PY'
import json, pathlib
paths=list(pathlib.Path('/mnt/data/pbui_linked_views_study').rglob('census.json'))
print(paths)
for p in paths[:5]:
    try:
        obj=json.loads(p.read_text())
        print('\n',p)
        print(str(obj)[:4000])
    except Exception as e: print(e)
PY
printf '%s\n' '--- aggregate output naming ---'
rg -n "sum_population|\$\{fn\}_\$\{field\}|measure.*name|aggregate" "$ROOT" | head -220
```

<details><summary>💭 Thinking</summary>

**Inspected document analysis infrastructure and pipeline presentation**

</details>

```unknown
from pathlib import Path
import textwrap, os, re, json, datetime

out = Path("/mnt/data/LINKED-ANALYSIS-WORKSPACES-PBUI-DATALAB-STUDY.md")

doc = r'''
# Linked Analysis Workspaces in Datalab

## A PBUI- and CLIM-inspired design for coordinating dataset, pipeline, table, encoding, and chart views

**Status:** Architecture and interaction study  
**Analyzed codebase:** the enhanced `pbui` repository and its `packages/datalab-ui` application supplied with this conversation  
**Date:** 2026-08-02  
**Scope:** data-model design, presentation semantics, interaction design, persistence, workspace duplication, source retargeting, performance, migration, and testing  
**Implementation status:** the
```

<details><summary>💭 Thinking</summary>

**Designed linked analysis workspace architecture**

</details>

```unknown
bash -lc ls -l /mnt/data/LINKED-ANALYSIS-WORKSPACES-PBUI-DATALAB-STUDY.md 2>/dev/null || true
```

<details><summary>💭 Thinking</summary>

**Created study workspace design and appended analysis sections 14 through 32**

</details>

```unknown
bash -lc cat >> /mnt/data/LINKED-ANALYSIS-WORKSPACES-PBUI-DATALAB-STUDY.md <<'EOF'

---

# 21. Transactions, undo, and concurrency

## 21.1 One conceptual operation, one transaction

These should each be atomic:

- merge link groups;
- detach a port;
- rebind a group;
- fork an analysis;
- adapt an analysis onto a source;
- fork a workspace;
- instantiate a template.

A user should never see half the group updated.

## 21.2 High-level trace records

Examples:

```text
analysis_group_linked
    sourceBinding
    targetBinding
    mergedBinding
    winnerDocument
    memberCount

analysis_group_rebound
    binding
    oldDocument
    newDocument

analysis_forked_to_source
    binding
    sourceDocument
    newDocument
    targetSource
    mappings

workspace_forked
    sourceWorkspace
    newWorkspace
    viewCount
    bindingCount
    documentCount
```

Do not log one low-level entry per port rewrite.

## 21.3 Undo

Useful inverse operations:

### Rebind

Store the old document ID and expected current revision.

### Detach

Store the old binding ID and fresh binding ID. Undo reattaches the port if neither has changed incompatibly.

### Merge

Undo is more complex because members from two groups were combined. The command must record the original partition and values.

### Fork analysis onto source

Undo rebinds to the old document. The new document can be retained as an orphaned recent analysis or garbage-collected when unreferenced, according to product policy.

### Fork workspace

Undo removes the newly created workspace and any documents, bindings, and views reachable only from it.

A toast with **Undo** is a practical first UI.

## 21.4 Async preflight races

A source schema request and compile can take long enough for state to change.

Capture:

```text
binding ID
binding revision
source document ID
source document semantic revision
target source version/fingerprint
```

Before commit, verify all still match. If not:

```text
“The analysis changed while compatibility was being checked. Review the updated setup and try again.”
```

Do not commit a plan computed for stale transforms.

## 21.5 Concurrent group merges

Two clients may concurrently merge or rebind the same groups.

Expected-revision checks make the conflict visible. Server-side command application should be idempotent by command ID.

A merge command should reference the source and target binding revisions. If either is stale, reject rather than silently merging a different membership set.

## 21.6 Immutable snapshots for selectors

PBUI `prepare` should capture IDs and scalar metadata, not mutable object references that Immer may later replace.

The final command resolves current records by ID.

---

# 22. Accessibility and discoverability

## 22.1 Chain icon semantics

The glyph alone is insufficient. Use accessible labels:

- `Analysis link: private`
- `Analysis link: Regional population, 5 views`
- `Link this analysis port`
- `Unlink this view from Regional population`

The linked state needs text or count, not only color.

## 22.2 Keyboard flow

A complete keyboard interaction:

1. Focus the analysis-link button.
2. Press Enter.
3. The command prompt announces: `Choose another analysis port. Five eligible targets.`
4. Tab or arrow navigation moves among eligible presentations.
5. Enter selects.
6. Escape cancels and returns focus to the initiating control.
7. A status region announces the result.

## 22.3 Screen-reader relationship descriptions

An analysis port can expose:

```text
Chart analysis. Population by region.
Linked with Dataset, Pipeline, Table, and Encoding.
```

The manage-group panel should use a real list with buttons, not a visually arranged set of spans.

## 22.4 Conflict dialogs

A conflict preview should identify:

- source group;
- target group;
- current analyses;
- number of affected views;
- winner choice.

Buttons must name the outcome, not `OK` and `Cancel` only.

## 22.5 Empty and invalid states

Unbound:

```text
No analysis selected.
[Choose visible analysis] [Create analysis]
```

Schema-invalid after drift:

```text
Analysis needs repair.
2 source fields no longer resolve.
[Review mappings]
```

The chain remains intact in both states. Errors should not silently detach views.

## 22.6 Tutorial affordances

A newcomer tutorial can use presentations:

```text
1. Activate the chain icon in the chart.
2. Click the Analysis chip in the pipeline.
3. Change the analysis in either toolbar.
4. Observe all linked views update.
5. Duplicate the workspace and choose a new source.
```

Because the targets are semantic presentations, tutorial steps need not depend on brittle DOM selectors alone.

---

# 23. Worked census example

This walkthrough uses the repository's actual fixture and welcome-document conventions.

## 23.1 Build the analysis

Source:

```text
kind: dataset
drop: lab
dataset: census
version: 2
path: rows.csv
```

Relevant fields:

```text
region       nominal
population   quantitative
area_km2     quantitative
station_id   nominal
```

Transform:

```text
aggregate-population
    groupBy: region
    measure:
        name: population_total
        function: sum
        field: population
```

Root view:

```text
mark: bar
x: region
y: population_total
color: region
```

This is the repository-equivalent of “population by city.”

## 23.2 Create the workspace

Open:

- Dataset;
- Pipeline;
- Table;
- Encoding;
- Chart.

Each receives a private `primary` analysis binding selecting the same document initially.

This initial state is not yet linked:

```text
binding D → doc census-bars
binding P → doc census-bars
binding T → doc census-bars
binding E → doc census-bars
binding C → doc census-bars
```

The selected values happen to be equal, but changing one selector would not change the others.

## 23.3 Link all compatible views

From the chart's chain menu, choose:

```text
Add all compatible views here
```

The command collects the five `primary` analysis ports and attaches them to one new binding:

```text
binding A “Regional population” → doc census-bars
```

The bar shows:

```text
[⛓ Regional population · 5]
```

## 23.4 Switch to another existing analysis

The user opens the pipeline selector and chooses `Population and land area`, another existing document.

The binding becomes:

```text
binding A → doc census-scatter
```

All five views switch:

- Dataset remains census because that document uses the same source.
- Pipeline becomes empty or shows that document's transforms.
- Table shows row-level census output.
- Encoding shows point mark with `area_km2` and `population`.
- Chart becomes a scatter plot.

No peer events are sent.

## 23.5 Switch by clicking another pipeline

A pipeline tile elsewhere presents:

```ts
{
  type: "pipeline",
  value: {
    docId: "climate-temperature",
    terminal: ...
  }
}
```

Its action menu offers:

```text
Use owning analysis in “Regional population”
```

PBUI converts the pipeline to its owning `doc`. The binding changes to the climate document. All five views now show the climate analysis.

## 23.6 Duplicate the workspace independently

The user chooses **Duplicate workspace**.

The full fork produces:

```text
original:
    workspace W1
    views V1..V5
    binding A
    doc D1

copy:
    workspace W2
    views V6..V10
    binding B
    doc D2
```

`D2` is a cloned census analysis. Editing it or rebinding B does not affect W1.

## 23.7 Retarget the copy to a same-schema version

The user chooses census version 3 with the same field names and types.

Preflight classifies it as exact. The preserving source replacement succeeds without a mapping dialog.

The copied document keeps:

- aggregate transform;
- `population_total` alias;
- bar mark;
- x/y/color encodings.

Binding B continues to identify the copied linked group and now selects the adapted document.

## 23.8 Retarget to different field names

Target fields:

```text
city          nominal
residents     quantitative
land_area     quantitative
```

The contract requires:

```text
region       nominal       dimension
population   quantitative  measure
```

The mapping dialog suggests:

```text
region → city
population → residents
```

The adapted transform becomes:

```text
groupBy: city
sum residents as population_total
```

The encoding becomes:

```text
x: city
y: population_total
color: city
```

The derived alias remains stable.

Compilation succeeds, so the transaction:

1. inserts the new document;
2. rebinds B;
3. records the mapping;
4. emits one trace entry.

The original workspace remains on census version 2.

## 23.9 Save as a template

The user saves W2 as:

```text
Template: Population aggregation workspace
Slot: Main analysis
Blueprint: adapted population bar document
Contract:
    category dimension, nominal, required
    population measure, quantitative, required
```

A future instance asks for one source or existing analysis and reconstructs the five linked ports automatically.

---

# 24. Implementation roadmap

The work can be staged so that each phase provides product value.

## Phase 1 — Complete the current document-binding experience

Goals:

- use product label `Analysis`;
- add group label and count;
- add `Add all compatible views`;
- use a dedicated analysis-port presentation target;
- owner-qualify pipeline steps;
- add PBUI conversions from analysis-owned objects to `doc`;
- add conflict preview for differently selected groups.

This phase can still use the existing denormalized `documentBindingId` reducer internally.

## Phase 2 — Fix workspace copy semantics

Goals:

- rename current `cloneSpace` user action to `Mirror workspace`;
- implement full **Duplicate workspace** by reusing bundle graph-copy logic;
- add tests for alias preservation and independence;
- warn when a group crosses the workspace boundary;
- provide one-step undo.

This directly enables the user's “duplicate the same workspace but use different datasets” workflow, even before preserving source retarget exists.

## Phase 3 — Add linked dataset view

Goals:

- add `DatasetApp`;
- make it analysis-bound;
- show root source and input requirements;
- add owner-qualified `analysisSource` presentations;
- add source-browser commands that explicitly choose a target binding.

At the end of this phase, all five desired view types can join one group.

## Phase 4 — Normalize subject bindings and app ports

Goals:

- add `bindings` store;
- replace `docBound` with port descriptors;
- migrate `AppView.documents`;
- change selectors and `AnalysisBar` to resolve through bindings;
- add garbage collection and deletion invariants;
- update portable format;
- maintain old-import compatibility.

Do this before adding a second subject kind.

## Phase 5 — Exact-schema analysis fork

Goals:

- create pure preserving source-replacement helper;
- add schema-only candidate query;
- clone a document;
- preserve transforms and encodings only when every required field matches exactly;
- compile before commit;
- atomically insert and rebind;
- add revision guard and undo.

This delivers a safe first version without a mapping UI.

## Phase 6 — Mapping contracts

Goals:

- derive source-origin requirements and use sites;
- classify compatibility;
- implement mapping UI;
- rewrite typed field references;
- preserve derived aliases;
- cache compatibility;
- record mapping metadata;
- handle schema drift.

## Phase 7 — Parameterized templates

Goals:

- introduce binding table and template slots in portable format;
- expose one slot per linked group;
- save blueprints and contracts;
- instantiate from existing analysis or source;
- support optional slots;
- migrate existing templates as fixed snapshots.

## Phase 8 — Remote protocol and collaboration

Goals:

- add subject-binding records and port references to protobuf;
- add atomic domain mutations;
- implement expected-revision conflict handling;
- preserve links in remote round trips;
- support collaborative group management and source fork.

## Phase 9 — Generalized linked subjects

Only after analysis linking is stable, consider:

- filter sets;
- time ranges;
- row selections;
- cursors;
- color scales.

Each should be a separate subject kind with explicit app ports and conversion semantics.

---

# 25. Codebase change map

The following map identifies likely modification points. It is not a patch specification; exact filenames may be adjusted to preserve the repository's layering rules.

## 25.1 Generic PBUI

### `src/presentation/types.ts`

Potential additions:

- optional command-start/partial-command verb conventions;
- no change required for the basic selector and conversion model.

### `src/presentation/createPbui.tsx`

Potential additions:

- public API for beginning a serializable partial command;
- input-context metadata for source presentation and missing argument.

### `src/presentation/registry.ts`

Existing action rules and conversions are sufficient for most link behavior.

Potential additions:

- diagnostics for ambiguous equal-cost conversions when desired;
- optional conversion explanation for command previews.

### New or product-level `PbuiCommandHost`

Prefer this in Datalab unless the missing-argument protocol becomes generic enough for PBUI core.

Responsibilities:

- receive a begin-command verb;
- establish accept context;
- resolve conversion;
- dispatch completed verb;
- manage cancellation/focus.

## 25.2 Presentation product layer

### `packages/datalab-ui/src/pbui/types.ts`

Change:

- `step: string` → `step: StepRef`;
- add analysis binding/port, pipeline, encoding, owner-source, and relation refs;
- narrow ambient fallbacks.

### `packages/datalab-ui/src/pbui/registry.ts`

Add:

- descriptors;
- identities;
- conversions to `doc`;
- action rules for link, rebind, inspect, fork.

### `packages/datalab-ui/src/pbui/descriptors/step.ts`

Use `ref.docId`, not `env.activeDocId`.

### `packages/datalab-ui/src/pbui/descriptors/source.ts`

Separate catalog-source actions from owner-qualified analysis-source actions. Remove or de-emphasize implicit active-document targeting.

### `packages/datalab-ui/src/pbui/verbs.ts` and verb application

Add serializable link/rebind/fork command verbs.

## 25.3 Layout and binding state

### `packages/datalab-ui/src/store/layout.ts`

Near-term:

- group names;
- explicit merge winner;
- add-all command;
- mirror naming.

Normalized phase:

- `SubjectBinding` records;
- view port references;
- reducers for attach/detach/merge/rebind;
- binding GC;
- membership selectors.

A separate `store/subjects.ts` may reduce file size, provided imports do not create a cycle.

### `packages/datalab-ui/src/appkit/registry.ts`

Replace `docBound` with declared ports. Provide compatibility helpers during migration.

### `packages/datalab-ui/src/components/molecules/DocBar`

Rename/evolve to `AnalysisBar`.

Present:

- analysis document;
- analysis port;
- binding chip.

Keep tile-title presentation separate.

## 25.4 Applications

### Chart, table, pipeline, encoding apps

Resolve the selected document through:

```text
view.bindings.primary → binding → documentId
```

Pass port metadata to `AnalysisBar`.

### Pipeline panel

Present owner-qualified step and pipeline references.

### Encoding app/panel

Present the owner-qualified encoding object.

### Table app/panel

Present the output relation with owner document.

### New `DatasetApp`

Read and present root source, schema contract, and retarget commands.

### `SourceApp`

Remain a catalog. Add explicit commands targeting an analysis binding.

## 25.5 Analysis model

### `model/graphicAuthoring.ts`

Keep current destructive `replaceDocumentSource`.

Add a preserving pure helper with a distinct name, for example:

```ts
adaptDocumentToSource(...)
```

Do not overload one function with `reset: boolean`.

### New `model/analysisContract.ts`

Responsibilities:

- derive field requirements;
- classify source compatibility;
- rank mappings;
- rewrite owner-context field references;
- serialize portable contracts.

### Compiler integration

Expose enough resolved provenance to distinguish source-origin and derived references.

## 25.6 Analysis resources

### `appkit/AnalysisProvider.tsx`

Centralize per-document compiled state and default initialization.

### `appkit/analysisCoordinator.ts`

Retain execution coalescing. Add compatibility/resource integration only where it preserves its focused responsibility.

### API client

Add schema-only source query or formalize an existing endpoint suitable for candidate checks.

## 25.7 Workspace copying and templates

### `store/bundles.ts`

Extract or reuse graph collection/hydration for in-memory workspace fork.

### `model/portable.ts`

Add explicit portable bindings and slots in a version bump.

### `store/templates.ts`

Store template mode and slots. Preserve old bundles as fixed snapshots.

### Workspace menu verbs

Add:

- mirror;
- duplicate/fork;
- duplicate for another source;
- save parameterized template.

## 25.8 Persistence and remote

### `store/persist.ts`

Add migration and normalized validation.

### `remote/codec.ts`

Encode/decode bindings and ports. Remove the explicit link-loss limitation after protocol generation.

### Protobuf and generated code

Extend `AppView` and workbench state with typed subject bindings. Add mutation messages and regenerate TypeScript and Go outputs.

---

# 26. Testing strategy

The feature crosses graph identity, UI selection, compilation, and persistence. Tests should emphasize invariants and alias relationships.

## 26.1 Binding reducer tests

Test:

- private binding creation;
- merge with same document;
- merge with different documents and explicit winner;
- attach port;
- detach preserves current value;
- rebind changes all consumers by reference;
- unreferenced binding GC;
- invalid subject-kind rejection;
- stale revision rejection;
- document deletion repair.

## 26.2 Property-based binding graph tests

Generate random:

- views;
- app port declarations;
- bindings;
- document selections;
- link/detach/rebind operations.

Assert after every operation:

- references resolve;
- kinds match;
- one value per binding;
- detach preserves value;
- no unreferenced records after GC;
- equivalent ports remain equivalent.

## 26.3 PBUI tests

Test:

- analysis-port identity;
- prepared selector called once per accept operation;
- repeated occurrences use semantic memoization;
- exact clicked occurrence is returned;
- ineligible current-group ports are rejected;
- target removed before commit is rejected;
- pipeline/encoding/relation/step conversions resolve to owner doc;
- plain catalog source does not convert to doc;
- action-rule shadowing by stable ID.

## 26.4 Owner qualification regression tests

Render two pipeline panels for documents α and β with identical step IDs.

Open the step menu in β and verify every verb carries `docId: β`.

This test should fail under the current bare-string design.

## 26.5 App integration tests

Mount linked chart, table, pipeline, encoding, and dataset views.

Rebind once and assert each reads the same new document.

Test that view-local state such as table sorting and chart size does not become shared merely because the analysis is shared.

## 26.6 Source adaptation unit tests

### Exact schema

Preserve transforms and encodings.

### Renamed fields

Apply explicit mapping and preserve derived output alias.

### Missing required field

Return `mapping-required` or `incompatible`, with use-site diagnostics.

### Ambiguous candidate

Do not guess.

### Derived field

Do not rewrite `population_total` when source `population` changes.

### Nested field references

Exercise every transform and view location.

### Compile failure

Return failure with no mutated input document.

### Revision race

Reject stale plan at commit.

### Stream policy

Enforce supported source-kind rules.

## 26.7 Workspace graph-copy tests

Construct a workspace with:

- two placements of one logical view;
- five views sharing one binding;
- two bindings selecting one document;
- a group with one member outside the workspace.

Fork and assert:

- all runtime IDs are new;
- duplicate placements still share one cloned view;
- linked members share one cloned binding;
- shared source document aliases become one cloned document;
- no cloned identity points back to original;
- external group member remains on original;
- copied members form an independent group.

Property-based graph cloning is particularly valuable here.

## 26.8 Portable round-trip tests

Test:

- current format;
- migration from v3 binding indices;
- normalized ports;
- template slots;
- optional slots;
- fixed documents;
- malformed indices;
- dangling references;
- unsupported subject kinds;
- credential audit.

## 26.9 Remote codec tests

Test:

- bindings survive encode/decode;
- old remote workbench decodes to private bindings;
- expected revisions;
- atomic fork mutation;
- dangling document rejection;
- unknown subject kind handling;
- Go and TypeScript generated schema compatibility.

## 26.10 Performance tests

Measure:

- one prepared port-set build per accept;
- no row evaluation during link hover/select;
- one compile per document revision across linked views;
- in-flight execution coalescing;
- compatibility cache hit;
- no million-row fetch for schema checks;
- bounded member-manager rendering.

## 26.11 Accessibility tests

Test:

- chain state accessible names;
- keyboard accept/cancel;
- focus restoration;
- status announcements;
- conflict dialog labels;
- group member list semantics;
- no color-only distinction.

## 26.12 Storybook scenarios

Add stories:

1. Private analysis port.
2. Five linked views.
3. Link target highlighting.
4. Conflict merge preview.
5. Unlink without visual change.
6. Dataset app exact compatibility.
7. Mapping-required state.
8. Invalid schema drift.
9. Mirror versus fork workspace.
10. Template slot instantiation.

---

# 27. Rejected alternatives

## 27.1 Peer-to-peer view links

Rejected because they create event graphs, ordering problems, and partial updates.

Use one shared subject.

## 27.2 Global active analysis

Rejected because it prevents independent groups and makes visible-object actions depend on focus.

Use owner-qualified presentations and explicit bindings.

## 27.3 Copy pipeline and encoding into each tile

Rejected because each tile would own a divergent copy of one composition.

Keep the analysis document as the source of truth.

## 27.4 Treat pipeline, table, encoding, and chart as one subtype hierarchy

Rejected because they are not substitutable instances of one object type. They are different objects or projections owned by one analysis.

Use conversions to the owning analysis, not false subtyping.

## 27.5 Convert any catalog source to an analysis

Rejected because a source has no unique owning analysis.

Use a two-argument fork/retarget command.

## 27.6 Store member lists inside bindings and binding IDs inside views

Rejected because it creates two mutable sources of membership truth.

Persist port references; derive reverse membership.

## 27.7 One shared-group ID for all future interaction state

Rejected because analysis selection, filters, cursor, row selection, and zoom need independent coupling.

Use typed subjects and named ports.

## 27.8 Silent best-effort field mapping

Rejected because an incorrect chart can look plausible.

Require explicit choice for ambiguous mappings and compile before commit.

## 27.9 Destructive source reset under the label “switch dataset”

Rejected because it discards work unexpectedly.

Keep reset as a clearly named operation and add fork/adapt.

## 27.10 Call geometry-only cloning “Duplicate workspace”

Rejected because the copy changes with the original.

Call it Mirror. Make Duplicate a graph fork or present explicit choices.

## 27.11 Split pipeline and encoding into first-class reusable artifacts immediately

Rejected as the first step because the current `GraphicDocument` already gives coherent ownership and the main requested workflow does not require independent artifact versioning.

Reconsider only when users need to share one pipeline across many documents while independently changing it, compose pipelines as libraries, or version encodings separately.

---

# 28. Open design choices

Several decisions require product judgment. None blocks the core architecture.

## 28.1 Merge winner default

Options:

- initiating/source group wins;
- target wins;
- larger group wins;
- ask only when values differ.

Recommendation: source wins for same-value/no-conflict cases; ask when values differ.

## 28.2 User-facing term

Candidates:

- Analysis;
- Composition;
- Document;
- Graphic;
- Work item.

Recommendation: **Analysis**. It communicates that source, pipeline, table result, and visualization belong together. Keep internal names until a broader refactor is justified.

## 28.3 Default duplicate semantics

Recommendation:

- primary menu item: **Duplicate workspace** → full fork;
- secondary: **Mirror workspace**;
- advanced: **Duplicate layout with shared analyses**.

This aligns the default with user expectations and preserves the useful current behavior under a precise name.

## 28.4 Forked document naming

Examples:

```text
Population by region — copy
Population by region · census v3
Population by region · city demographics
```

Recommendation: derive a provisional name from source and let the user edit it in the preflight.

## 28.5 Orphan document policy

After undo or workspace deletion, a cloned document may have no bindings.

Options:

- immediate garbage collection;
- retain in recent analyses;
- prompt;
- TTL cleanup.

Recommendation: retain as a recent analysis for the session, with explicit cleanup, unless storage scale demands eager GC. Bindings themselves can be eagerly garbage-collected.

## 28.6 In-place retarget permissions

In-place retarget changes every binding that selects the same document.

Recommendation: make it advanced and show all affected groups. Default to fork.

## 28.7 Cross-workspace linking

The data model can support it. The interaction should default to visible/current workspace targets because cross-workspace links are harder to understand.

A group manager can expose external members explicitly.

## 28.8 Empty bindings

Allowing `documentId: null` is useful for optional template slots and deleted-document repair.

Required app ports should render a clear empty state rather than fail.

## 28.9 Multiple sources in one document

The current authoring helpers often assume a root/first source. Future joins require several source-bound ports or one analysis binding plus source-node-specific presentations.

The normalized subject architecture does not require each source to be a top-level UI binding. The analysis remains the selected composition; a join editor can expose source-node presentations within it.

## 28.10 Whether a pipeline becomes a standalone object later

A standalone pipeline artifact becomes useful when users need:

- library reuse across analyses;
- pipeline versioning independent of charts;
- parameterized pipelines;
- several root views over one transform graph;
- explicit pipeline ownership and permissions.

Until then, “pipeline presentation converts to owner document” is simpler and coherent.

---

# 29. Acceptance criteria

A first complete release should satisfy the following observable criteria.

## 29.1 Linking

- A chart, table, pipeline, encoding, and dataset view can be placed in one linked group.
- The group has a visible chain indicator and member count.
- Changing the analysis from any member updates every member.
- Unlinking one member leaves it showing the same analysis.
- Linking groups with different analyses shows an explicit winner preview.
- Link selection uses PBUI presentation input, keyboard operation, and semantic identity.

## 29.2 Object correctness

- Pipeline steps and other owned objects target their actual document.
- Clicking a pipeline, encoding, relation, source-in-analysis, or step can select its owning analysis through PBUI conversion.
- A catalog source is never mistaken for an existing analysis.

## 29.3 Source reuse

- A user can fork a linked analysis onto a same-schema source without losing pipeline or encoding.
- A renamed-field source opens a mapping flow.
- Ambiguous mappings are not silently applied.
- Compilation failure commits nothing.
- The original analysis remains intact.
- Undo returns the group to the original analysis.

## 29.4 Workspace reuse

- Mirror workspace preserves shared logical views.
- Duplicate workspace produces independent views, bindings, and documents.
- Editing or rebinding the duplicate does not affect the original.
- Internal linked-group topology survives duplication.
- Multiple placements of one view remain multiple placements of one cloned view.

## 29.5 Templates

- A linked group can be exposed as one named template slot.
- Instantiation asks once for the slot.
- The slot may bind an existing analysis or adapt a blueprint to a source.
- Portable import/export preserves slots and group topology.
- Old snapshot templates remain readable.

## 29.6 Persistence and collaboration

- Local reload preserves links.
- Portable round trip preserves links.
- Remote workbench round trip preserves links.
- Stale concurrent updates are detected.
- Document deletion cannot leave silent dangling bindings.

## 29.7 Performance

- Link target hit testing performs no row evaluation.
- Same-document linked views share in-flight analysis execution.
- Source compatibility uses schema-only access.
- A group rebind updates one normalized subject record.
- Large workspaces remain responsive.

---

# 30. Glossary

**Analysis**  
The product-facing name recommended for a `GraphicDocument`: source, transforms, relation, visual specification, and parameters as one coherent composition.

**Analysis binding**  
A stable subject record whose value is the selected analysis document.

**Analysis port**  
A named connection point on an application view that refers to an analysis binding.

**Application object**  
A semantic domain object represented in the UI.

**Binding group**  
The derived set of ports that reference one binding.

**Conversion**  
A typed interpretation from one presentation object to another, such as pipeline to owning analysis.

**Detach**  
Give a port a private binding initialized from its current shared binding.

**Fork**  
Clone identities and content while preserving internal graph relationships and independence from the original.

**Input context**  
A temporary state in which PBUI accepts presentations satisfying a selector or convertible target type.

**Logical view**  
One open application instance, independent of workspace placement.

**Mirror**  
A second layout tree that presents the same logical views and therefore shares their bindings and documents.

**Owner-qualified reference**  
A presentation value that carries both local object identity and its owning analysis, such as `{ docId, stepId }`.

**Placement**  
A workspace rectangle that presents a logical view.

**Presentation**  
A visible occurrence associated with an application object and presentation type.

**Retarget**  
Change an analysis source while attempting to preserve and adapt downstream setup.

**Schema contract**  
The source-field and capability requirements implied by an analysis or declared by a template.

**Subject**  
A typed shared selection or interaction value observed by application ports.

**Template slot**  
A named subject input in a parameterized workspace template.

---

# 31. References

## Repository paths analyzed

- `src/presentation/types.ts`
- `src/presentation/selectors.ts`
- `src/presentation/registry.ts`
- `src/presentation/conversions.ts`
- `src/presentation/createPbui.tsx`
- `packages/datalab-ui/src/store/layout.ts`
- `packages/datalab-ui/src/store/layoutTree.ts`
- `packages/datalab-ui/src/store/world.ts`
- `packages/datalab-ui/src/store/bundles.ts`
- `packages/datalab-ui/src/store/templates.ts`
- `packages/datalab-ui/src/store/persist.ts`
- `packages/datalab-ui/src/model/graphic.ts`
- `packages/datalab-ui/src/model/graphicAuthoring.ts`
- `packages/datalab-ui/src/model/portable.ts`
- `packages/datalab-ui/src/model/transformEditor.ts`
- `packages/datalab-ui/src/appkit/registry.ts`
- `packages/datalab-ui/src/appkit/AnalysisProvider.tsx`
- `packages/datalab-ui/src/appkit/analysisCoordinator.ts`
- `packages/datalab-ui/src/apps/ChartApp/ChartApp.tsx`
- `packages/datalab-ui/src/apps/TableApp/TableApp.tsx`
- `packages/datalab-ui/src/apps/PipelineApp/PipelineApp.tsx`
- `packages/datalab-ui/src/apps/EncodingApp/EncodingApp.tsx`
- `packages/datalab-ui/src/apps/SourceApp/SourceApp.tsx`
- `packages/datalab-ui/src/components/molecules/DocBar/DocBar.tsx`
- `packages/datalab-ui/src/components/organisms/PipelinePanel/PipelinePanel.tsx`
- `packages/datalab-ui/src/pbui/types.ts`
- `packages/datalab-ui/src/pbui/registry.ts`
- `packages/datalab-ui/src/pbui/descriptors/step.ts`
- `packages/datalab-ui/src/pbui/descriptors/source.ts`
- `packages/datalab-ui/src/remote/codec.ts`
- `proto/hyperslop/pbui/workbench/v1/workbench.proto`
- `packages/datalab-ui/src/fixtures/census.json`
- `packages/datalab-ui/src/demo/welcome.ts`

## CLIM background

The following official LispWorks CLIM documentation is useful background for the presentation/input-context/translator/command model:

- [CLIM presentation concepts](https://www.lispworks.com/documentation/lw81/clim/clim-ch6-1.htm)
- [Presentation types](https://www.lispworks.com/documentation/lw81/clim/clim-ch7-2.htm)
- [Presentation translators](https://www.lispworks.com/documentation/lw80/clim/clim-ch8-5.htm)
- [Defining presentation translators](https://www.lispworks.com/documentation/lw80/clim/clim-ch8-6.htm)
- [Commands](https://www.lispworks.com/documentation/lw81/clim/clim-ch11-1.htm)
- [Command processing](https://www.lispworks.com/documentation/lw80/clim/clim-ch11-9.htm)
- [CLIM glossary](https://www.lispworks.com/documentation/lw81/clim/clim-glossary.htm)

The preceding design borrows the separation of application object, presentation type, input context, conversion/translator, and command. It does not claim API compatibility with CLIM.

---

# 32. Final recommendation

The enhanced codebase has already crossed the most important conceptual boundary: a chart and a pipeline can remain distinct logical applications while sharing a document-selection subject.

The next step should not be a larger collection of tile-to-tile synchronization handlers. It should be a disciplined generalization of that subject.

The recommended sequence is:

1. Treat `GraphicDocument` as the selected **Analysis**.
2. Present a named analysis port in every dataset, pipeline, table, encoding, and chart tile.
3. Use PBUI selectors, semantic identity, conversions, and action rules to link ports and rebind groups.
4. Fix ownerless analysis-owned presentations, beginning with pipeline steps.
5. Rename the current geometry-only copy to **Mirror workspace** and make ordinary duplication a full graph fork using the existing portable bundle machinery.
6. Add a document-bound dataset application while retaining the singleton source catalog.
7. Add a preflighted **Fork analysis onto source** operation that preserves transforms and encodings, uses schema contracts, requests mappings, compiles before commit, and is undoable.
8. Normalize bindings and app ports before adding other linked state kinds.
9. Extend templates with one slot per linked analysis group.
10. Extend the remote protocol so that bindings are first-class collaborative state.

This architecture gives users the desired experience:

```text
Build one workspace for a type of work.
Link its analytical views once.
Switch the whole workspace by choosing an analysis anywhere.
Duplicate it without hidden aliases.
Apply the setup to another source without discarding the pipeline.
Save the linked topology as a reusable template with one meaningful input.
```

It also preserves the main strengths of the current PBUI and Datalab design: semantic presentations, serializable actions, explicit identity, pure graph transformations, deterministic state transitions, and a single coherent analytical composition.
EOF
wc -c -l /mnt/data/LINKED-ANALYSIS-WORKSPACES-PBUI-DATALAB-STUDY.md
```

The study now specifies schema-aware rebinding because source loading currently erases transforms and encodings, alongside distinct mirror, independent-copy, fork, and template-instantiation semantics.

<details><summary>💭 Thinking</summary>

**Validated appended sections, references, paths, archives, and linked workspace study**

</details>

# Linked-workspace study

[Download the detailed Markdown study](sandbox:/mnt/data/LINKED-ANALYSIS-WORKSPACES-PBUI-DATALAB-STUDY.md)

The document is approximately 18,000 words across 32 sections. It includes:

- A code-specific audit of the enhanced PBUI and Datalab implementation.
- A newcomer-oriented explanation of presentation-based UI and the relevant CLIM model.
- A distinction between the analytical dependency graph and the UI binding graph.
- A proposed normalized `SubjectBinding` and named application-port architecture.
- PBUI presentation types, identities, selectors, conversions, action rules, and partial-command flows.
- Interaction designs for the chain indicator, linking, unlinking, group management, and analysis rebinding.
- A preserving **Fork analysis onto source** design with schema preflight, field contracts, mapping, compilation, transactions, revision guards, and undo.
- A proposed document-bound dataset application, while retaining `SourceApp` as a global source catalog.
- Explicit **Mirror**, **Duplicate layout**, **Fork workspace**, and **Template instance** semantics.
- Parameterized workspace templates with one named slot per linked analysis group.
- Local, portable, and remote persistence designs.
- Performance, concurrency, accessibility, testing, migration, and implementation roadmaps.
- A worked example using the repository’s actual census fixture: aggregate `population` by `region` as `population_total`.

The central conclusion is that the chart, table, pipeline, encoding, and dataset views should not synchronize with one another directly. They should expose named analysis ports connected to one first-class binding whose subject is a `GraphicDocument`.

The repository already contains the beginning of that architecture through `documentBindingId`. The main repo-specific gaps identified are:

1. `SourceApp` is a singleton catalog rather than a linked view of an analysis source.
2. `setDocSource` currently resets transforms, views, encodings, and parameters.
3. Pipeline-step presentations contain only a step ID and can target the ambient active document rather than their actual owner.
4. `cloneSpace` clones geometry while retaining the same logical views, bindings, and documents; it is a workspace mirror rather than an independent duplicate.
5. Portable bundle hydration already provides most of the graph-copy algorithm needed for a true workspace fork.
6. The remote protobuf representation does not preserve binding equivalence.

This turn contains the architectural study rather than source-code modifications.


---

> make a pdf

> make it a pdf

I’ll convert the completed Markdown study into a formatted PDF and verify the rendered pages.

```unknown
bash -lc cat /home/oai/skills/pdfs/SKILL.md && printf '
---FILES---
' && ls -l /mnt/data/LINKED-ANALYSIS-WORKSPACES-PBUI-DATALAB-STUDY.md
```

<details><summary>💭 Thinking</summary>

**Formatting the document**

I’m refining the Markdown-to-PDF workflow by removing the manual contents section, relying on generated navigation, and avoiding automatic numbering because the source already includes numbered headings.

**Formatted the document**

</details>

```unknown
bash -lc sed -n '1,260p' /home/oai/skills/pdfs/scripts/html_to_pdf.py
```

<details><summary>💭 Thinking</summary>

**Designing the PDF workflow**

I’m favoring a polished HTML-to-PDF route with custom styling, linked navigation, page numbers, and stronger code wrapping. I’ll validate layout through text extraction, page inspection, and rendered contact sheets.

**Designed the PDF workflow**

**Created a structured PDF with TOC after reviewing Markdown and conversion instructions**

</details>

The source is long and code-heavy, so I’m using a print-optimized HTML pipeline rather than a basic Markdown export. This preserves internal links and wraps wide TypeScript examples cleanly.

```unknown
bash -lc cat > /mnt/data/_pdf_work/build_pdf.py <<'PY'
from pathlib import Path
import re, subprocess

src = Path('/mnt/data/LINKED-ANALYSIS-WORKSPACES-PBUI-DATALAB-STUDY.md')
work = Path('/mnt/data/_pdf_work')
work.mkdir(parents=True, exist_ok=True)
text = src.read_text(encoding='utf-8')
lines = text.splitlines()

# Convert the first title/subtitle headings to metadata for a proper title page.
assert lines[0].startswith('# ')
title = lines[0][2:].strip()
assert lines[2].startswith('## ')
subtitle = lines[2][3:].strip()
body = '\n'.join(lines[4:]) + '\n'

# Promote the executive summary so it appears alongside numbered chapters in the TOC.
body = body.replace('## Executive summary', '# Executive summary', 1)
# Its five immediate subsections were H3 in the original title hierarchy.
first_chapter = body.index('# 1. The concrete problem')
front = body[:first_chapter].replace('\n### ', '\n## ')
body = front + body[first_chapter:]

# Remove the hand-authored Markdown contents list; Pandoc will create a linked TOC.
body = re.sub(
    r'\n---\n\n## Contents\n.*?\n---\n\n(?=# 1\. The concrete problem)',
    '\n\n',
    body,
    flags=re.S,
)

md = work / 'study-print.md'
md.write_text(
    '---\n'
    f'title: "{title}"\n'
    f'subtitle: "{subtitle}"\n'
    'date: "August 2, 2026"\n'
    'lang: en-US\n'
    '---\n\n' + body,
    encoding='utf-8',
)

css = work / 'study.css'
css.write_text(r'''
@page {
  size: Letter;
  margin: 0.70in 0.68in 0.78in 0.68in;
}

:root {
  --ink: #172033;
  --muted: #5f6878;
  --rule: #d7dce5;
  --soft: #f4f6f9;
  --accent: #274c77;
  --accent-soft: #eaf0f7;
}

* { box-sizing: border-box; }
html { font-size: 10pt; }
body {
  margin: 0;
  color: var(--ink);
  font-family: "Noto Serif", "DejaVu Serif", Georgia, serif;
  line-height: 1.47;
  text-rendering: optimizeLegibility;
  overflow-wrap: anywhere;
}

#title-block-header {
  min-height: 8.2in;
  display: flex;
  flex-direction: column;
  justify-content: center;
  padding: 0.35in 0.22in 0.55in;
  border-top: 7px solid var(--accent);
  border-bottom: 1px solid var(--rule);
  break-after: page;
}
#title-block-header .title {
  margin: 0 0 0.2in;
  color: var(--ink);
  font-family: "Noto Sans", "DejaVu Sans", Arial, sans-serif;
  font-size: 30pt;
  line-height: 1.06;
  font-weight: 760;
  letter-spacing: -0.02em;
}
#title-block-header .subtitle {
  max-width: 6.5in;
  margin: 0 0 0.65in;
  color: var(--accent);
  font-family: "Noto Sans", "DejaVu Sans", Arial, sans-serif;
  font-size: 15pt;
  line-height: 1.35;
  font-weight: 500;
}
#title-block-header .date {
  margin: 0;
  color: var(--muted);
  font-family: "Noto Sans", "DejaVu Sans", Arial, sans-serif;
  font-size: 10pt;
}

#TOC {
  break-after: page;
  padding: 0.04in 0 0.12in;
}
#TOC::before {
  content: "Contents";
  display: block;
  margin: 0 0 0.22in;
  padding-bottom: 0.09in;
  border-bottom: 2px solid var(--accent);
  font-family: "Noto Sans", "DejaVu Sans", Arial, sans-serif;
  font-size: 22pt;
  font-weight: 730;
}
#TOC > ul { columns: 2; column-gap: 0.42in; }
#TOC ul { margin: 0; padding-left: 1.15em; }
#TOC li { margin: 0 0 0.075in; break-inside: avoid; }
#TOC a { color: var(--ink); text-decoration: none; }

h1, h2, h3, h4, h5, h6 {
  font-family: "Noto Sans", "DejaVu Sans", Arial, sans-serif;
  color: var(--ink);
  line-height: 1.18;
  break-after: avoid-page;
}
h1 {
  margin: 0 0 0.22in;
  padding: 0.02in 0 0.10in;
  border-bottom: 2px solid var(--accent);
  font-size: 20pt;
  font-weight: 760;
  break-before: page;
}
#TOC + h1 { break-before: auto; }
h2 {
  margin: 0.28in 0 0.11in;
  color: var(--accent);
  font-size: 14pt;
  font-weight: 700;
}
h3 {
  margin: 0.22in 0 0.08in;
  font-size: 11.5pt;
  font-weight: 700;
}
h4 { margin: 0.18in 0 0.06in; font-size: 10.5pt; }

p { margin: 0 0 0.12in; orphans: 3; widows: 3; }
ul, ol { margin: 0.06in 0 0.14in; padding-left: 0.27in; }
li { margin: 0 0 0.045in; }
li > p { margin-bottom: 0.05in; }

strong { font-weight: 700; }
a { color: var(--accent); text-decoration-thickness: 0.5px; text-underline-offset: 1.5px; }
hr { border: 0; border-top: 1px solid var(--rule); margin: 0.25in 0; }

blockquote {
  margin: 0.15in 0 0.18in;
  padding: 0.13in 0.18in;
  border-left: 4px solid var(--accent);
  background: var(--accent-soft);
  color: #25344a;
  break-inside: avoid-page;
}
blockquote > :last-child { margin-bottom: 0; }

code {
  font-family: "Noto Sans Mono", "DejaVu Sans Mono", Consolas, monospace;
  font-size: 0.88em;
}
p code, li code, td code {
  padding: 0.02em 0.22em;
  border: 1px solid #dde2ea;
  border-radius: 3px;
  background: var(--soft);
  white-space: normal;
}
pre {
  margin: 0.13in 0 0.18in;
  padding: 0.12in 0.14in;
  border: 1px solid #d8dee8;
  border-radius: 5px;
  background: #f6f8fa;
  white-space: pre-wrap;
  overflow-wrap: anywhere;
  word-break: break-word;
  line-height: 1.37;
  break-inside: auto;
}
pre code {
  padding: 0;
  border: 0;
  background: transparent;
  font-size: 7.6pt;
  white-space: pre-wrap;
}

table {
  width: 100%;
  margin: 0.14in 0 0.2in;
  border-collapse: collapse;
  table-layout: fixed;
  font-size: 8.2pt;
  line-height: 1.32;
}
thead { display: table-header-group; }
tr { break-inside: avoid-page; }
th, td {
  padding: 0.065in 0.075in;
  border: 1px solid #cfd6e1;
  vertical-align: top;
  overflow-wrap: anywhere;
}
th {
  background: #e9eef5;
  font-family: "Noto Sans", "DejaVu Sans", Arial, sans-serif;
  text-align: left;
  font-weight: 700;
}

figure { margin: 0.18in 0; break-inside: avoid-page; }
img { max-width: 100%; height: auto; }

/* Keep short semantic diagrams and compact lists together where possible. */
pre:has(code.language-text) { break-inside: avoid-page; }

@media print {
  a { color: var(--accent); }
}
''', encoding='utf-8')

html = work / 'study.html'
cmd = [
    'pandoc', str(md), '-o', str(html),
    '--standalone', '--toc', '--toc-depth=1',
    '--section-divs', '--embed-resources',
    '--highlight-style=tango',
    '--css', str(css),
    '--metadata', 'pagetitle=Linked Analysis Workspaces in Datalab',
]
subprocess.run(cmd, check=True)
print(html)
PY
python /mnt/data/_pdf_work/build_pdf.py
```

<details><summary>💭 Thinking</summary>

**Created and validated a 120-page PDF with rendered visual inspection**

</details>

[Download the PDF](sandbox:/mnt/data/linked-analysis-workspaces-pbui-datalab-study.pdf)

