# Go-Go-Datadrop React/PBUI Architecture Review

**Revised against the real repository, not only the prototype**

- **Repository:** `go-go-golems/go-go-datadrop`
- **Branch:** `task/datadrop-mcp`
- **Analyzed revision:** `08f814b685d0c2fa3d968fe7835079a323883971`
- **Primary frontend:** `ui/`
- **Companion reference artifact:** `pbui-landing.jsx`
- **Review date:** 2026-07-26

## Scope and correction

The first version of this review was based only on the supplied single-file PBUI artifacts. That was the wrong scope once the repository was available. The branch already contains most of the architectural decomposition that the prototype-only review proposed:

- a React-free table, pipeline, chart, time, and plot model;
- Redux Toolkit slices for durable world and layout state;
- RTK Query for server state;
- a presentation protocol with typed values, descriptors, serializable verbs, object menus, and accept-by-pointing;
- a generic application registry;
- a split-tree window manager with structural sharing and tests;
- a layered component system, Storybook, design tokens, and import-boundary tests;
- local persistence, snapshots, chart permalinks, CSV export, and PNG export;
- thin application containers plus an ongoing extraction into presentational panels.

This revised document therefore does **not** recommend rebuilding the application around abstractions it already has. It reviews the abstractions in the branch, identifies where they still have application-global or implicit scope, and proposes the smallest coherent route to reusable packages.

Important implementation-status note: the branch head is a design/documentation commit. It records the measured `FieldChip` render-path defect and proposes `fieldsFor`, but the checked-in source at this revision still resolves fields through `tableFor`. This report distinguishes that planned fix from code already shipped.

The central conclusion is:

> The codebase is already a credible reference implementation of a PBUI workbench. The next architectural step is to make runtime scope, workspace scope, registration, command routing, and serialization explicit. It is not to replace Redux, duplicate the model layer, or rewrite the UI.

---

# 1. Executive assessment

## 1.1 What is already strong

The branch has several unusually good foundations.

1. **The computational model is genuinely headless.** `ui/src/model/` contains no React, Redux, DOM, or network code. `Table`, `ChartSpec`, the transformation pipeline, and the plot compiler can be tested as ordinary functions.
2. **Server state and user decisions are separated.** RTK Query owns fetched tables and account data. Redux `world` owns documents, specifications, snapshots, the watchlist, and the trace. Redux `layout` owns workspaces and split trees.
3. **Commands are data.** Presentation descriptors return serializable `Verb` values rather than closures over `dispatch`. This gives the codebase a real seam between interaction semantics and execution.
4. **Tiles are views, not owners.** A tile stores an application ID and document binding. Documents live in `world`, so closing or moving a tile does not destroy the document.
5. **The window manager core is already pure.** `updateNode`, `removeLeaf`, `cloneTree`, `findLeaf`, and `snapRatio` are independent of React and tested.
6. **The presentation model preserves provenance and ownership.** Field, datum, category, and channel references carry a `docId` where appropriate, avoiding the prototype’s ambiguity about which chart an action targets.
7. **Architecture is enforced.** The import graph, component stories, control usage, token relationships, and several security properties are tests rather than conventions written only in prose.
8. **The repository is honest about bounded data.** Table truncation, mark caps, facet caps, type provenance, and invalid chart specifications are reported visibly rather than hidden.

These should remain the load-bearing choices.

## 1.2 What still prevents clean reuse

The remaining problems are concentrated around scope and composition rather than basic design.

| Priority | Finding | Why it matters |
|---|---|---|
| P0 | Field presentation resolution can evaluate a full pipeline during render | The branch head documents a measured 158 ms table-header render at the 50,000-row budget. |
| P0 | Layout actions implicitly mutate `currentSpaceId` | Two workspaces cannot be rendered and edited concurrently in one store without ambiguity. |
| P0 | Tile drag state and DOM registration are module-global | Two workbench roots or two workspace surfaces can see and affect each other. |
| P1 | `PbuiProvider` combines high-frequency mouse documentation with all presentation interactions | Hovering a mark can invalidate every presentation consuming the context, including thousands of SVG marks. |
| P1 | The public presentation vocabulary is larger than the descriptor and command implementation | `channel`, `chart`, `tile`, and `workspace` are declared but have no registered descriptors; some promised menus cannot exist. |
| P1 | Pipeline step IDs use a module counter | Restore, import, multiple stores, and exported setups can produce duplicate step IDs. |
| P1 | Plot derivation can evaluate the same pipeline twice | `useDocPipeline` computes a result and `buildPlot` computes it again. |
| P1 | Persistence is one local, unnamed version-1 payload | It is autosave, not yet a portable workspace/project/data bundle system. |
| P2 | Application and conversion registries are module singletons populated by side effects | Tests, HMR, package consumers, and multiple independent runtimes cannot choose isolated registries. |
| P2 | `docBound: boolean` and `{app, docId}` are too narrow as a reusable widget contract | Future resource-bound or instance-stateful widgets have no declared binding or serialization policy. |
| P2 | `SourceRef` and plot colors are embedded in otherwise generic model modules | The data and graphics cores still know Datadrop-specific resource identity and the default visual theme. |
| P2 | Every SVG datum presentation is focusable | Large charts can create thousands of tab stops. |

## 1.3 Recommended direction

Preserve the current architecture and extract it in layers:

```text
@go-go-golems/pbui-core
    presentation definitions, commands, conversions, codecs; no React

@go-go-golems/pbui-react
    Presentation, accept/menu/doc-line providers and hooks

@go-go-golems/workspace-core
    generic split trees, workspace operations, validation, migrations

@go-go-golems/workspace-react
    WorkspaceSurface, TileFrame, SplitView, scoped drag runtime

@go-go-golems/table-core
    Table, Field, pipeline, schema calculation

@go-go-golems/graphics-core
    visualization specs and plot geometry compiler

@go-go-golems/datalab-widgets
    chart, table, pipeline, encoding, gallery, inspector, and related panels

apps/datadrop-ui
    RTK Query adapters, auth, uploads, account widgets, presets, shell
```

These do not need to become eight published npm packages immediately. The first safe step is to create internal package-style boundaries and public entry points in the same repository. Publish only after the dependency graph and API have stabilized.

---

# 2. New-developer guide to the repository

## 2.1 What the product is

Go-Go-Datadrop is a self-hostable research data inbox. The server stores two main source kinds:

- **streams:** unbounded, append-only event logs;
- **datasets:** finite, immutable, versioned file collections.

The UI projects either source into one typed tabular representation. The browser then applies a small data pipeline and a grammar-of-graphics specification. This is the critical seam:

```text
Datadrop stream or dataset
            │
            │ HTTP projection performed by the Go server
            ▼
          Table
            │
            ├── pipeline: filter / derive / summarize / sort / limit
            │
            └── visualization: mapping / geom / scale / facet
                              │
                              ▼
                         plot geometry
                              │
                              ▼
                         React + SVG
```

The browser does not parse arbitrary source files or infer a second competing schema. It receives rows, fields, field types, provenance, row-count information, and truncation information from the server.

## 2.2 Toolchain and common commands

The frontend uses React, TypeScript, Redux Toolkit, React Redux, RTK Query, Vite, Bun, and Storybook. The repository deliberately keeps JavaScript tooling out of ordinary Go builds; built UI assets are committed and embedded by the Go binary.

From the repository root:

```bash
# Typecheck and run the Bun tests.
make ui-test

# Build the production UI.
make ui

# Start Vite on :5173, proxying /v1 to a server on :8080.
make ui-dev

# Start Storybook on :6006.
make storybook

# Run Go tests.
make test

# Run the full local Datadrop + Zitadel stack.
make compose-up
```

Direct frontend commands are also available:

```bash
bun install --cwd ui --frozen-lockfile
bun run --cwd=ui typecheck
bun test --cwd ui
bun run --cwd=ui dev
bun run --cwd=ui storybook
```

Read `ui/GUIDELINES.md` before modifying the component tree. It is an operational specification, not optional style advice.

## 2.3 Frontend directory map

```text
ui/src/
├── api/                 RTK Query API and Datadrop wire DTOs
├── appkit/              application descriptor and registry contract
├── apps/                tile application containers and registration
├── components/
│   ├── foundation/      Text, Kbd, visually-hidden, section labels
│   ├── layout/          Stack, Toolbar, Surface, app body layout
│   ├── atoms/           controls, chips, badges, primitive live objects
│   ├── molecules/       DocBar, legend, rows, composed controls
│   ├── organisms/       feature panels with DTO/callback interfaces
│   └── pages/           Workbench composition root
├── export/              browser CSV and PNG helpers
├── fixtures/            story/test data; not production sources
├── model/               pure table, pipeline, chart, time, plot, permalink
├── pbui/                presentation protocol, descriptors, verbs, provider
├── store/               Redux slices, command application, persistence, presets
├── styles/              design tokens and global visual contract
└── main.tsx              browser mount and top-level Redux Provider
```

### `model/`

This is the computational core.

- `table.ts` defines `Field`, `FieldType`, `Row`, `Table`, and currently the Datadrop-shaped `SourceRef`.
- `pipeline.ts` defines pipeline steps, `schemaAfter`, and `evaluate`.
- `chart.ts` defines `ChartSpec`, channels, geoms, channel type constraints, and the default chart heuristic.
- `plot.ts` turns a table plus chart specification plus size into plain drawable geometry.
- `time.ts` handles temporal parsing and tick construction.
- `permalink.ts` encodes and decodes a chart specification in the URL fragment.

No file in this directory should import React, Redux, browser APIs, or the network.

### `api/`

`api/client.ts` is the RTK Query boundary. It knows Datadrop routes, authentication mode, streams, datasets, tables, users, tokens, members, sessions, and uploads. This is server state, not project state.

### `store/`

- `world.ts` contains live chart documents, snapshots, compare pins, watch entries, inspected value, and trace.
- `layout.ts` contains workspaces and split trees.
- `spaces.ts` defines code-owned workspace presets such as `welcome`, `account`, `build`, `explore`, and tutorials.
- `persist.ts` stores selected world and layout state in `localStorage`.
- `applyVerb.ts` maps PBUI verbs to Redux actions.
- `index.ts` creates a store, restores persisted state, and registers the RTK Query reducer and middleware.

### `pbui/`

This implements the Genera/CLIM-inspired interaction model.

- `types.ts` defines presentation types and the value shape each type carries.
- `registry.ts` maps a presentation type to its label, description, menu actions, and tone.
- `descriptors/` contains one object-type implementation per registered type.
- `verbs.ts` defines serializable commands.
- `PbuiProvider.tsx` manages accept requests, object-menu state, mouse documentation, and command dispatch.
- `Presentation.tsx` wraps HTML or SVG output as a typed, live object.
- `ObjectMenu.tsx`, `AcceptBanner.tsx`, and `MouseDocLine.tsx` provide the shell UI.
- `conversions.ts` contains declared presentation conversions.

### `appkit/` and `apps/`

`appkit/registry.ts` is the contract between tiles and applications. An app descriptor currently contains an ID, title, tone, `docBound` flag, and React component. Files under `apps/` register themselves, and `apps/all.ts` imports them for side effects.

The intended component pattern is:

```text
App container
  owns hooks, RTK Query, Redux dispatch, browser effects
        │
        ▼
Organism panel
  receives DTOs and callbacks; renderable in Storybook
        │
        ▼
Molecules / atoms / layout / foundation
```

Some applications already follow this closely, while the branch head explicitly records additional applications still needing panel extraction.

## 2.4 Runtime startup

The browser starts approximately as follows:

```text
main.tsx
  └── <ReduxProvider store={store}>
        └── <Workbench>
              ├── imports apps/all, populating the global app registry
              ├── selects world and current workspace
              ├── builds a PBUI environment
              ├── maps PBUI verbs to Redux actions
              └── <PbuiProvider>
                    ├── AcceptBanner
                    ├── WorkspaceStrip
                    ├── NodeView(currentWorkspace.tree)
                    │     ├── SplitView
                    │     └── Tile
                    │           └── registered application component
                    ├── MouseDocLine
                    └── ObjectMenu
```

`Workbench` is already small and is correctly acting as the composition root. It should remain the place where Datadrop-specific services are assembled, but reusable implementations should be passed into it rather than imported through process-global singletons.

## 2.5 The core state model

### Server state: RTK Query

Fetched drops, tables, users, tokens, memberships, and other API data belong to RTK Query. Multiple documents with identical query arguments share a cache entry.

Do not persist the RTK Query cache as part of a workspace bundle. A persisted cache is stale server data, can be large, and can accidentally retain sensitive response material.

### Project state: `world`

A live document has this effective structure:

```ts
interface Doc {
  id: string;
  name: string;
  limit: number;
  spec: ChartSpec;
}

interface ChartSpec {
  source: SourceRef;
  steps: Step[];
  geom: "point" | "line" | "bar" | "area";
  mapping: Record<"x" | "y" | "color" | "size" | "facet", string | null>;
  yScale: "linear" | "log";
  typeOverrides?: Record<string, "q" | "n" | "t">;
}
```

Several tiles can bind to the same `Doc`. That is why a chart, table, pipeline editor, and encoding editor remain synchronized without direct wiring between those components.

A snapshot stores a deep copy of `spec` and the document’s row budget. It is immutable with respect to later document edits.

### Layout state: `layout`

A workspace is a name plus a binary split tree:

```ts
type Node =
  | {
      id: string;
      type: "leaf";
      app: string;
      docId: string | null;
    }
  | {
      id: string;
      type: "split";
      dir: "row" | "col";
      a: Node;
      b: Node;
      ratio: number;
    };

interface Workspace {
  id: string;
  name: string;
  tree: Node;
  pinned?: boolean;
}
```

The split tree is a good model because it is:

- serializable;
- deterministic;
- easy to validate;
- easy to clone;
- structurally shareable;
- sufficient for nested row and column layouts.

### Transient interaction state: `PbuiProvider` and drag runtime

Accept requests, the current object menu, mouse-documentation text, the pending promise resolver, DOM element references, and pointer drag geometry are not project data. They should not be persisted.

The current code correctly keeps the accept resolver outside Redux. It does not yet scope all transient state cleanly enough for several independent runtime roots.

## 2.6 Data flow through a document

A document-bound tile follows this path:

1. `useDocTable(docId)` selects the document.
2. The document’s `SourceRef` and row budget become RTK Query arguments.
3. The server returns a typed `Table`.
4. If the document has no mapping yet, an effect applies `defaultChart(table)`.
5. `evaluate(table, steps, overrides)` calculates pipeline rows and output fields.
6. Table and pipeline applications render the pipeline result.
7. `buildPlot(table, spec, width, height)` validates the spec and emits panels, ticks, legends, and marks.
8. `ChartPanel` renders that geometry as SVG.
9. Individual row-backed marks become `<datum>` presentations; legend entries become `<cat>` presentations.

The distinction between source table and pipeline output is essential. A derived or summarized field exists in the output even though it is absent from the source.

## 2.7 Presentation and command flow

### Right-click menu flow

For a field chip:

```text
<FieldChip field={FieldRef}>
  └── <Presentation ptype="field" value={FieldRef}>

right-click
  └── PbuiProvider.openMenu("field", value, x, y)
        └── ObjectMenu
              └── descriptorFor("field").actions(value, environment)
                    └── Action { label, verb, disabledBecause? }

select action
  └── PbuiProvider.perform(verb)
        └── Workbench.perform
              └── actionsForVerb(verb, world, environment)
                    └── Redux actions
                          └── reducers
```

This is one of the strongest parts of the code. The menu logic is pure and testable, and the execution boundary is explicit.

### Accept-by-pointing flow

A command can request an argument:

```ts
const result = await pbui.accept({
  ptype: "field",
  prompt: "Choose the field to map to y",
  filter: (_ptype, value) => isQuantitative(value),
});
```

While the request is active:

- matching presentations render as acceptable;
- clicking one satisfies the request instead of running its ordinary left-click action;
- Escape resolves the request with `null`;
- a declared conversion may allow another presentation type to satisfy it.

This is already a useful subset of CLIM presentation acceptance. It needs extension points and better context isolation, not replacement.

## 2.8 Window-manager flow

`NodeView` recursively renders the current workspace tree. A split node renders two panes and a divider. A leaf renders `Tile`, which resolves the app descriptor and mounts the app component.

Operations are reducer actions over the current tree:

- split a leaf;
- close a leaf and promote its sibling;
- change a leaf’s app;
- bind a leaf to a document;
- exchange two leaves’ app/document fields;
- remove a source leaf and dock it on an edge of another;
- resize a split;
- add, clone, rename, remove, or switch workspaces.

The pure tree functions are already suitable for reuse. The Redux actions and React runtime still assume one current workspace.

## 2.9 Design-system and component rules

The component architecture is stricter than most prototypes and should be retained.

- No CSS framework.
- Tokens are the source of visual constants.
- Component stories are mandatory.
- Raw form controls are generally prohibited outside atoms.
- The import graph is checked by a Bun test.
- Presentational panels take data and callbacks.
- Components below organisms do not fetch.
- Meaning cannot depend on color alone.
- Secrets cannot appear in presentation values.

The rules are practical because they identify the test that enforces them and the exceptions that exist.

## 2.10 Existing persistence and export

The branch already has four distinct mechanisms:

1. **Autosave:** `store/persist.ts` writes selected `world` and complete `layout` state to one localStorage key after a debounce.
2. **Chart snapshots:** deep copies of one live chart document’s specification and row budget.
3. **Chart permalink:** base64url-encoded `ChartSpec` in a URL fragment.
4. **Output export:** pipeline rows to RFC 4180 CSV and an on-screen SVG to PNG.

These are useful building blocks, but they solve different problems. Autosave is not a portable project file. A snapshot is not a workspace. A chart permalink does not include layout, document identity, or compare state. CSV and PNG are data/product exports, not editable setup exports.

## 2.11 Current tests worth understanding

Before changing the architecture, read these test families:

- model tests for pipeline, plot, time, and export;
- `store.test.ts` for tree invariants, document and snapshot isolation, command application, and persistence rejection;
- `layers.test.ts` for the dependency graph;
- Storybook coverage tests;
- token and contrast tests;
- raw-control and component-folder tests;
- account/API-surface security tests.

The codebase has good tests for invariants it has named. The next work should name and test the currently implicit runtime-scope invariants.

---

# 3. Detailed architectural review

## 3.1 Keep Redux Toolkit and RTK Query

Replacing Redux would be a regression.

Redux Toolkit currently provides:

- immutable identity changes that make memoization correct;
- serializable world and layout state;
- replayable reducers;
- selector subscriptions instead of a whole-world mutation notification;
- a natural import/export boundary;
- easy creation of isolated stores for Storybook and future embedded workbenches.

RTK Query provides:

- request deduplication;
- cache identity;
- loading and error state;
- invalidation for account and upload operations;
- a clean separation between fetched server data and editable project state.

The reuse problem is not Redux. The problem is that some modules import a singleton store assumption or dispatch actions whose target workspace is implicit. The fix is store factories, typed hooks, explicit scope, and runtime injection.

## 3.2 The current split tree is package-worthy

`layout.ts` has the correct conceptual core:

- a discriminated union;
- structural sharing in `updateNode`;
- sibling promotion in `removeLeaf`;
- deep ID regeneration in `cloneTree`;
- pure snapping logic;
- reducer operations that preserve one leaf minimum.

For reuse, make the tree generic rather than hard-code app and document fields:

```ts
export type SplitTree<L> = SplitNode<L> | LeafNode<L>;

export interface LeafNode<L> {
  id: string;
  type: "leaf";
  value: L;
}

export interface SplitNode<L> {
  id: string;
  type: "split";
  dir: "row" | "col";
  ratio: number;
  a: SplitTree<L>;
  b: SplitTree<L>;
}

export interface AppTileBinding {
  appId: string;
  resource?: ResourceBinding;
  viewState?: JsonObject;
}
```

The current shape can be supported through adapters during migration:

```ts
const currentLeafToBinding = (node: CurrentLeaf): AppTileBinding => ({
  appId: node.app,
  resource: node.docId ? { kind: "document", id: node.docId } : undefined,
});
```

A generic tree can also power an outer board whose leaves contain workspace IDs.

## 3.3 Workspace mutation is currently ambient

This is the largest blocker to “multiple workspaces on the same page.”

Every tree reducer calls a helper equivalent to:

```ts
const space = state.spaces.find(s => s.id === state.currentSpaceId);
space.tree = operation(space.tree);
```

That is correct when only the current workspace is mounted. It becomes wrong when two workspace trees are visible:

- a divider in workspace B dispatches `setRatio({nodeId, ratio})`;
- the reducer searches workspace A because A is current;
- it either changes a coincidentally matching node, does nothing, or changes the wrong surface after an ID/import defect;
- a tile in B computes `canClose` from A;
- a drag from B docks into whichever workspace the reducer considers current.

All layout operations need an explicit workspace target:

```ts
interface WorkspaceTarget {
  workspaceId: string;
}

type SetRatio = WorkspaceTarget & {
  nodeId: string;
  ratio: number;
};

type DockTile = WorkspaceTarget & {
  from: string;
  to: string;
  zone: "left" | "right" | "top" | "bottom";
};
```

Then replace `mutateTree(state, fn)` with:

```ts
function mutateWorkspaceTree(
  state: LayoutState,
  workspaceId: string,
  fn: (tree: Node) => Node,
): void {
  const workspace = state.spaces.find(s => s.id === workspaceId);
  if (workspace) workspace.tree = fn(workspace.tree);
}
```

The ordinary single-workspace shell can continue dispatching against `currentSpaceId`. The difference is that `WorkspaceSurface` resolves that ID once and passes it into every child operation.

## 3.4 The drag runtime must not be global

`components/organisms/Tile/useDrag.ts` currently has module-level values for:

- the map of tile IDs to DOM elements;
- the current drag;
- all drag listeners.

This creates several problems:

1. Two independent workbench roots share one hit-test registry.
2. Two concurrently rendered workspaces share targets whether or not cross-workspace docking is intended.
3. Every tile subscribes to every drag-state update.
4. HMR and tests can retain or observe global state unexpectedly.
5. A source store may dispatch a target ID owned by another store.

Create a scoped runtime object:

```ts
export interface WorkspaceDragRuntime {
  readonly runtimeId: string;
  register(target: DragTarget): () => void;
  begin(input: DragStart): void;
  move(point: Point): void;
  end(): DragResult | null;
  cancel(): void;
  subscribe(listener: () => void): () => void;
  getSnapshot(): DragSnapshot;
}
```

Provide it at one of two scopes:

- **workspace scope:** dragging is confined to one workspace;
- **board scope:** explicit cross-workspace operations are allowed.

Do not let module location accidentally decide the behavior.

Use Pointer Events with pointer capture where possible, restore `userSelect` in effect cleanup as well as pointer-up cleanup, and batch move updates through `requestAnimationFrame`.

## 3.5 `PbuiProvider` has the right responsibilities but the wrong update topology

The provider currently exposes one context object containing:

- the environment;
- accept state and accept methods;
- menu state and methods;
- mouse documentation and setter;
- the command performer.

Every `Presentation` calls `usePbui()`. Therefore a change to mouse documentation or menu state changes the context value observed by every field chip and every row-backed chart mark.

With up to 5,000 marks per panel, this is a material rendering risk.

Split by update frequency and readership:

```text
PresentationRegistryContext   stable service
CommandDispatcherContext      stable service
EnvironmentContext            stable resolver facade or external-store access
AcceptStore                    presentations subscribe only to accept matching
MenuStore                      only ObjectMenu subscribes to menu state
MouseDocWriterContext          stable set/clear callbacks
MouseDocStore                  only MouseDocLine subscribes to current text
```

Recommended hooks:

```ts
usePresentationRegistry()
useCommandDispatcher()
usePresentationEnvironment()
useAcceptController()
useAcceptMatch(ptype, value)
useObjectMenuController()
useObjectMenuState()
useMouseDocWriter()
useMouseDocText()
```

`Presentation` should use only stable controllers plus `useAcceptMatch`. Hovering one mark should update the documentation line without rerendering the other marks.

An external store implemented with `useSyncExternalStore` is appropriate for accept, menu, mouse documentation, and drag state. Redux is also possible, but pending accept resolvers must remain out of serializable state.

## 3.6 Presentation typing is only partially type-safe

`PresentationValues` correctly maps presentation type names to value shapes. The React component and descriptor lookup then frequently collapse the value to `unknown` or `never`.

Make the public API generic:

```ts
export interface PresentationProps<T extends PresentationType> {
  ptype: T;
  value: PresentationValues[T];
  // ...
}

export interface PresentationDescriptor<T extends PresentationType> {
  ptype: T;
  label(value: PresentationValues[T], env: PbuiEnvironment): string;
  describe(value: PresentationValues[T], env: PbuiEnvironment): JsonValue;
  actions(value: PresentationValues[T], env: PbuiEnvironment): Action[];
  codec?: PresentationCodec<PresentationValues[T]>;
}
```

This catches a datum value accidentally passed as a field and makes registry extension safer.

## 3.7 The descriptor registry is incomplete

The type union currently declares:

```text
field, source, doc, step, geom, channel, datum, cat, chart,
tile, workspace, user, token, member, upload
```

The registry registers only:

```text
field, source, doc, cat, datum, geom, step,
user, token, member, upload
```

The missing public types are:

```text
channel, chart, tile, workspace
```

This is visible behavior, not only a typing nicety:

- `WorkspaceStrip` tells the user that right-click duplicates or deletes a workspace.
- A workspace is wrapped in `Presentation ptype="workspace"`.
- `ObjectMenu` asks the registry for actions.
- The registry returns no descriptor and therefore no actions.

Similarly, tile titles are live presentations but have no tile descriptor. Frozen chart snapshots have a public type but no chart descriptor. Channels have a public value shape but no channel descriptor.

Fix this in two parts.

First, register explicit descriptors for every public type, even where the action list is intentionally empty.

Second, make completeness testable:

```ts
const descriptors = {
  field: fieldDescriptor,
  // ...every key...
} satisfies {
  [K in PresentationType]: PresentationDescriptor<K>;
};
```

If host packages add types through module augmentation, validate the assembled registry at runtime and in a package-level contract test.

## 3.8 Command routing is not complete

The `Verb` union includes world operations plus account and upload operations. `actionsForVerb` handles the world/chart subset and stops after snapshot operations.

A concrete example is `TokensApp`:

1. it performs the actual RTK Query mutation;
2. it calls `pbui.perform({kind: "createToken", ...})` to record a trace without carrying the secret;
3. `Workbench.perform` passes that verb to `actionsForVerb`;
4. there is no `createToken` case, so no action is returned and no trace is written.

This means the code’s claimed single command seam is incomplete.

Replace the one monolithic switch with an extensible command registry:

```ts
export interface CommandContext {
  getState(): RuntimeState;
  dispatch(action: UnknownAction): void;
  services: RuntimeServices;
  trace(event: CommandTrace): void;
}

export interface CommandDefinition<C extends Command = Command> {
  type: C["type"];
  execute(command: C, context: CommandContext): void | Promise<void>;
  describe(command: C): string;
}
```

Packages register their handlers:

```text
pbui-core           inspect, watch
workspace package   split, dock, close, clone workspace
analysis package    set mapping, add step, snapshot
account package     sign in/out, token and member commands
upload package      retry/cancel upload
```

The executor can always append a safe trace description after successful execution. Secret-bearing results never become commands.

## 3.9 Conversions need environment and registration

The conversion table has a working `cat -> field` conversion and a declared `doc -> source` entry that always returns `undefined`, with a comment that the shell will fill it. The shell cannot fill a closed exported object through the current interface in a principled way, and document-to-source conversion requires access to world state.

Use definitions that receive the environment:

```ts
export interface PresentationConversion<F extends PresentationType, T extends PresentationType> {
  from: F;
  to: T;
  convert(
    value: PresentationValues[F],
    env: PbuiEnvironment,
  ): PresentationValues[T] | undefined;
}
```

Make conversions injectable through the runtime registry. Keep them few and explicit. A fully general implicit translator graph is unnecessary unless real use cases justify it.

## 3.10 The field render path has a measured performance defect

The current path is:

```text
FieldChip render
  -> resolveField(ref, environment)
       -> environment.tableFor(docId)
            -> useTableFor resolver
                 -> evaluate(all rows, all steps)
```

A table header renders one field chip per output field. The branch head documents a measured 158.5 ms for thirteen field chips at a 50,000-row budget.

`resolveField` only needs the post-pipeline field list. `schemaAfter` already computes it without touching rows.

Split the environment:

```ts
interface PbuiEnvironment {
  fieldsFor(docId: DocId | null): Field[];  // safe during render
  tableFor(docId: DocId | null): Table | null; // rows; menu/inspection only
  activeDocId: DocId | null;
  nameOf(docId: DocId | null): string;
  overridesFor(docId: DocId | null): Record<string, FieldType> | undefined;
}
```

Then:

```ts
export function resolveField(ref: FieldRef, env: PbuiEnvironment) {
  const field = env.fieldsFor(ref.docId).find(f => f.name === ref.name) ?? null;
  // no evaluate()
}
```

Memoization is useful behind both resolvers, but it is not the primary fix. The render path should not request rows at all.

## 3.11 Pipeline evaluation is duplicated for plots

`useDocPlot` calls `useDocPipeline`, which computes a memoized pipeline result. It then calls `buildPlot(table, spec, width, height)`, and `buildPlot` calls `evaluate` again.

Use a two-stage compiler:

```ts
interface EvaluatedData {
  rows: Row[];
  fields: Field[];
  err: string | null;
  dropped: Record<string, number>;
}

function compilePlot(
  data: EvaluatedData,
  visual: VisualizationSpec,
  size: Size,
  options?: PlotOptions,
): Plot;
```

Then:

```ts
const data = useDocumentData(docId);
const plot = useMemo(
  () => data ? compilePlot(data, visual, size) : null,
  [data, visual, size],
);
```

The public convenience `buildPlot(table, spec, size)` can remain and call both stages for tests or simple consumers.

## 3.12 Exact source identity must include dataset version

The cache resolver in `useTableFor` manually compares source properties but does not include dataset `version`. Two documents pointing at the same drop, dataset, and path but different versions can be associated with the wrong cached table.

Use the existing `sameSource` helper or exact serialized RTK Query arguments. Do not maintain a second incomplete equality implementation.

## 3.13 Step IDs are not safe for persistence or multiple runtimes

Documents and layout nodes use UUIDs, but `newStep` uses a module-level counter:

```ts
let stepCounter = 0;
const id = `s${++stepCounter}`;
```

After reload, import, HMR, or mounting several stores in one page, a newly created step can duplicate an existing persisted step ID.

Split identity from defaults:

```ts
export function createStepDraft<K extends StepKind>(
  kind: K,
  fields: Field[],
): Omit<StepOf<K>, "id">;

export function createStep<K extends StepKind>(
  kind: K,
  fields: Field[],
  id: string = crypto.randomUUID(),
): StepOf<K>;
```

For a React-free package, inject an `IdFactory` rather than call `crypto` directly in model code.

Import must also remap IDs to avoid collisions between the current project and the imported bundle.

## 3.14 App registration needs runtime scope

The current app registry is a module-global `Map`, and `apps/all.ts` populates it through side-effect imports. This is acceptable for one closed application bundle but weak for reuse:

- duplicate app IDs silently overwrite;
- tests cannot easily create a minimal registry;
- HMR may leave registration order or stale descriptors implicit;
- two embedded workbenches cannot expose different app sets;
- package consumers must import a magic side-effect module;
- import compatibility cannot be checked against a declared registry version.

Use an explicit registry object:

```ts
export interface AppRegistry {
  register(descriptor: AppDescriptor): void;
  get(id: string): AppDescriptor | undefined;
  list(): readonly AppDescriptor[];
  has(id: string): boolean;
}

export function createAppRegistry(
  descriptors: readonly AppDescriptor[],
): AppRegistry;
```

Duplicate IDs should throw in development and tests. The host assembles the registry:

```ts
const apps = createAppRegistry([
  ...datalabApps,
  ...datadropAccountApps,
  ...tutorialApps,
]);
```

A side-effect compatibility entry point may remain for the existing app, but it should not be the package API.

## 3.15 `docBound` should become a resource-binding contract

A boolean says only whether an app shows a DocBar. It does not describe:

- whether a binding is required;
- what resource type is accepted;
- how a missing or deleted binding is repaired;
- how an imported binding is decoded;
- whether the app has serializable view-local state;
- which default resource should be created or selected.

Use a descriptor such as:

```ts
export interface AppDescriptor<P = unknown> {
  id: string;
  version: number;
  title: string;
  tone: string;
  binding:
    | { kind: "none" }
    | { kind: "document"; required: boolean }
    | { kind: "resource"; resourceType: string; required: boolean };
  createViewState?(): P;
  viewStateCodec?: Codec<P>;
  Component: ComponentType<AppRuntimeProps<P>>;
}
```

When a leaf changes to a document-bound app, normalize its binding immediately. The current UI can display an app that falls back to the active document while the leaf itself still has `docId: null`; the title and serialized layout then do not record what the user is actually viewing.

## 3.16 Separate durable project state, durable layout state, and session state

`WorldState` currently combines:

- durable documents and snapshots;
- active document selection;
- compare pins;
- watchlist;
- inspected object;
- trace.

This is workable, but export requirements expose the distinctions.

Recommended categories:

```text
Project data
  documents, named data setups, snapshots

Workspace/layout data
  workspaces, split trees, tile bindings, view state

Session data
  active workspace, active document, compare selection, last inspector value

Ephemeral runtime data
  menu, accept continuation, hover text, drag DOM refs, request state

History/telemetry
  trace, optionally exportable but not part of the canonical project
```

They may remain in two Redux slices initially. The important change is to define explicit codecs and selectors for each category instead of serializing a hand-picked object inline.

## 3.17 Presentation values need codecs, not only `unknown`

The watchlist persists presentation type plus `unknown` value. This works for current small JSON-shaped references, but a reusable PBUI package needs per-type rules:

```ts
export interface PresentationCodec<V> {
  encode(value: V, env: PbuiEnvironment): JsonValue;
  decode(value: JsonValue, env: PbuiEnvironment): DecodeResult<V>;
  rebind?(value: V, idMap: ImportIdMap): V;
}
```

This provides:

- validation on import;
- ID remapping;
- stale-reference reporting;
- secret-field whitelisting;
- version migration;
- explicit refusal for nonportable presentation values.

The current global key-name secret scan should remain as a defense-in-depth check, not the primary serialization contract.

## 3.18 Chart-mark keyboard behavior needs a policy

`Presentation` assigns `tabIndex=0` to SVG and HTML presentations alike. A chart may render thousands of row-backed marks, making keyboard traversal unusable.

Recommended options, in increasing sophistication:

1. SVG marks are not individually tab-focusable; the chart is one focusable region and exposes a summary plus keyboard exploration mode.
2. Roving tabindex: only the selected or nearest mark has `tabIndex=0`.
3. A virtual accessibility table mirrors visible marks and supports row navigation.

The prototype’s choice to exclude marks from ordinary tab order is closer to a usable default. Keep right-click/pointer interactions, but do not create thousands of tab stops.

## 3.19 The model is mostly generic but still carries host concerns

### Datadrop-specific `SourceRef`

`Table`, fields, pipeline steps, and plot geometry are generic. `SourceRef` is not; it contains `drop`, `stream`, `dataset`, `version`, and `path`.

For package extraction, either:

```ts
interface Table<M = unknown> {
  source: M;
  fields: Field[];
  rows: Row[];
  // ...
}
```

or move source identity out of the table and into a document/resource binding.

A practical staged design is:

```ts
// generic package
interface Table {
  fields: Field[];
  rows: Row[];
  rowCount: number;
  truncated: boolean;
  metadata?: JsonObject;
}

// Datadrop adapter
interface DatadropSourceRef {
  kind: "stream" | "dataset";
  drop: string;
  // ...
}
```

### Theme values in the plot compiler

The geometry compiler currently owns concrete palette colors. This makes plot output easy to render but couples the pure model to the default theme.

Pass a theme/palette in `PlotOptions`, with existing colors as defaults:

```ts
interface PlotTheme {
  categories: readonly string[];
  rampLow: string;
  rampHigh: string;
  neutral: string;
}
```

If truly renderer-neutral geometry is desired later, marks can carry semantic color keys rather than final CSS colors. That is a larger change and is not required for the first package extraction.

---

# 4. Reusable package architecture

## 4.1 Package dependency graph

A practical target is:

```text
                 ┌──────────────────────┐
                 │   pbui-core          │
                 │ commands, types,     │
                 │ descriptors, codecs  │
                 └──────────┬───────────┘
                            │
                 ┌──────────▼───────────┐
                 │   pbui-react         │
                 │ providers + hooks +  │
                 │ Presentation/menu    │
                 └──────────┬───────────┘
                            │
┌─────────────────┐  ┌──────▼──────────┐  ┌────────────────────┐
│ workspace-core  │  │ table-core      │  │ graphics-core      │
│ generic trees   │  │ fields/pipeline │  │ visual spec/plot   │
└────────┬────────┘  └──────┬──────────┘  └─────────┬──────────┘
         │                  │                       │
┌────────▼────────┐         └──────────┬────────────┘
│ workspace-react │                    │
│ surfaces/tiles  │          ┌─────────▼───────────┐
└────────┬────────┘          │ datalab-widgets     │
         │                   │ panels + adapters   │
         └────────────┬──────┴─────────┬───────────┘
                      │                │
              ┌───────▼────────────────▼──────┐
              │        datadrop-ui host       │
              │ RTK Query, auth, upload,      │
              │ presets, shell, persistence   │
              └───────────────────────────────┘
```

## 4.2 Mapping current files to the target

| Current area | First target |
|---|---|
| `model/table.ts`, most of `pipeline.ts` | `table-core` |
| visual portion of `chart.ts`, `plot.ts`, `time.ts` | `graphics-core` |
| `pbui/types.ts`, descriptors, verbs, conversions | `pbui-core` |
| `Presentation`, provider, menu, accept banner, doc line | `pbui-react` |
| pure functions and types in `store/layout.ts` | `workspace-core` |
| `SplitView`, `Tile`, drag logic | `workspace-react` |
| chart/table/pipeline/encoding panels and generic chips | `datalab-widgets` |
| RTK Query, Datadrop source adapters, auth/upload/profile | host application |
| workspace presets and pinned-space merge policy | host application |
| Redux slices | initially host; later optional adapters per package |

Do not move files only to make the tree look like a package plan. Move a unit when its imports and public API already prove the boundary.

## 4.3 Runtime object

The top-level reusable concept should be a stable runtime assembled by the host:

```ts
export interface WorkbenchRuntime {
  id: string;
  store: Store;
  apps: AppRegistry;
  presentations: PresentationRegistry;
  commands: CommandRegistry;
  conversions: ConversionRegistry;
  sources: DataSourceRegistry;
  persistence: PersistenceAdapter;
  ids: IdFactory;
  clock: Clock;
}
```

Then:

```tsx
<WorkbenchRuntimeProvider runtime={runtime}>
  <ProjectProvider projectId="project-1">
    <PbuiRoot scope="project">
      <WorkbenchShell />
    </PbuiRoot>
  </ProjectProvider>
</WorkbenchRuntimeProvider>
```

The runtime object is stable configuration. Stateful slices remain in their dedicated stores and are accessed through selector hooks.

This supports:

- one normal application root;
- several isolated demos on one page;
- tests with tiny registries and fake data adapters;
- a host that exposes only a subset of widgets;
- future non-Redux storage adapters if needed.

## 4.4 Window-manager API

A controlled reusable surface can look like:

```tsx
<WorkspaceSurface
  workspaceId={workspace.id}
  tree={workspace.tree}
  registry={runtime.apps}
  onCommand={workspaceController.execute}
  dragScope={boardDragRuntime}
/>
```

Or, through a provider:

```tsx
<WorkspaceProvider controller={controller} workspaceId={workspace.id}>
  <WorkspaceSurface />
</WorkspaceProvider>
```

Recommended hooks:

```ts
useWorkspace(workspaceId)
useWorkspaceController(workspaceId)
useWorkspaceCanClose(workspaceId)
useWorkspaceNode(workspaceId, nodeId)
useTileBinding(workspaceId, nodeId)
useWorkspaceDragState(workspaceId, nodeId)
```

The core package should expose operations, not Redux action creators:

```ts
splitLeaf(tree, nodeId, dir, createLeaf): Tree
closeLeaf(tree, nodeId): Tree
setLeafValue(tree, nodeId, value): Tree
dockLeaf(tree, from, to, zone): Tree
swapLeafValues(tree, a, b): Tree
validateTree(input, leafCodec): Result<Tree>
remapTreeIds(tree, idFactory): Tree
```

A Redux adapter can call these functions inside reducers.

## 4.5 PBUI registry API

Use instance registries rather than closed module objects:

```ts
const registry = createPresentationRegistry()
  .register(fieldPresentation)
  .register(sourcePresentation)
  .register(documentPresentation)
  .register(workspacePresentation);
```

A descriptor should include more than display and menu behavior when persistence is required:

```ts
interface PresentationDefinition<T extends PresentationType> {
  type: T;
  tone: string;
  label(value: ValueOf<T>, env: Environment): string;
  describe(value: ValueOf<T>, env: Environment): JsonValue;
  actions(value: ValueOf<T>, env: Environment): readonly Action[];
  codec: PresentationCodec<ValueOf<T>>;
  defaultAction?(value: ValueOf<T>, env: Environment): Command | null;
}
```

Give actions stable IDs:

```ts
interface Action {
  id: string;
  label: string;
  command: Command;
  group?: string;
  order?: number;
  disabledBecause?: string;
}
```

A label is not a safe React key or command identity.

## 4.6 Provider and hook layout

Recommended React composition:

```tsx
<RuntimeServicesProvider value={runtimeServices}>
  <PresentationRegistryProvider registry={presentations}>
    <CommandProvider registry={commands}>
      <AcceptProvider store={acceptStore}>
        <MenuProvider store={menuStore}>
          <MouseDocumentationProvider store={mouseDocStore}>
            {children}
          </MouseDocumentationProvider>
        </MenuProvider>
      </AcceptProvider>
    </CommandProvider>
  </PresentationRegistryProvider>
</RuntimeServicesProvider>
```

This looks more verbose than one provider, but consumers should use a composed `<PbuiRoot>` wrapper. The separation is about update propagation and independent tests, not forcing every application to write the nesting.

A `Presentation` should conceptually do this:

```ts
const registry = usePresentationRegistry();           // stable
const commands = useCommandDispatcher();              // stable
const menu = useObjectMenuController();                // stable
const mouseDoc = useMouseDocWriter();                  // stable
const acceptable = useAcceptMatch(ptype, value);       // changes only on accept
```

Only `MouseDocLine` calls `useMouseDocText()`. Only `ObjectMenu` calls `useObjectMenuState()`.

## 4.7 Data-source adapter API

The reusable table and graphics packages should not import RTK Query or Datadrop DTOs.

```ts
export interface DataSourceAdapter<R extends JsonValue = JsonValue> {
  kind: string;
  canHandle(ref: JsonValue): ref is R;
  describe(ref: R): string;
  load(ref: R, options: LoadOptions): Promise<Table>;
  subscribe?(ref: R, options: LiveOptions): LiveTableSubscription;
  codec: Codec<R>;
}
```

The Datadrop host can still implement loading through RTK Query hooks. A runtime adapter used from React may expose hooks rather than direct promises:

```ts
interface ReactDataSourceAdapter<R> extends DataSourceAdapter<R> {
  useTable(ref: R, options: LoadOptions): QueryResult<Table>;
}
```

Keep one canonical source-equality implementation per adapter.

## 4.8 Widget API

Separate three levels:

1. **Panel:** pure presentation with DTOs and callbacks.
2. **App adapter:** obtains store/query data and translates callbacks to commands.
3. **App descriptor:** registration metadata, binding policy, state codec.

Example:

```ts
export interface PipelinePanelProps {
  fields: Field[];
  steps: Step[];
  rowCount: number;
  dropped: Record<string, number>;
  onAddStep(kind: StepKind): void;
  onUpdateStep(step: Step): void;
  onMoveStep(id: string, by: -1 | 1): void;
  onRemoveStep(id: string): void;
}
```

```tsx
function PipelineApp({ binding }: AppRuntimeProps) {
  const doc = useDocument(binding.documentId);
  const data = useDocumentData(binding.documentId);
  const commands = useCommandDispatcher();

  return (
    <PipelinePanel
      fields={data.fields}
      steps={doc.steps}
      rowCount={data.rows.length}
      onAddStep={(kind) => commands.execute({type: "analysis.addStep", ...})}
      // ...
    />
  );
}
```

Generic widgets belong in `datalab-widgets`. Datadrop account, token, member, and upload apps remain host packages because they depend on Datadrop API semantics.

---

# 5. Saving, exporting, and importing setups

## 5.1 Name the distinct export products

The user-facing model should distinguish these objects:

### Workspace layout

A layout only:

- workspace name and metadata;
- split tree;
- app IDs and versions;
- resource bindings;
- serializable view-local state.

It does not contain the documents themselves unless the user chooses a combined export.

### Data setup

A reusable data preparation recipe:

- source binding;
- row/window budget;
- pipeline steps;
- field type overrides;
- optional parameters or unresolved-source placeholders.

It deliberately excludes geometry and visual mappings.

### Visualization setup

A visual recipe:

- geom;
- mappings;
- scales;
- facet and future guide options.

It can be applied to a compatible data setup.

### Analysis document

The current live composition:

- identity and name;
- data setup;
- visualization setup;
- optional provenance and timestamps.

### Project

A collection of:

- documents;
- named data setups;
- snapshots;
- optional watch entries;
- project metadata.

### Workbench bundle

A project plus workspace collection and selected session state.

### Workspace board

An outer composition that renders several workspace surfaces together.

### Portable data bundle

An explicit opt-in export that embeds fields and rows. This is separate because it can be large and can copy sensitive data.

## 5.2 Versioned envelope

Use one envelope for every portable artifact:

```ts
interface BundleEnvelope<K extends BundleKind, P> {
  format: "go-go-datalab";
  version: number;
  kind: K;
  id: string;
  name: string;
  createdAt: string;
  createdBy?: {
    app: string;
    appVersion?: string;
  };
  requires: {
    apps?: Array<{ id: string; version?: number }>;
    presentationTypes?: string[];
    sourceKinds?: string[];
    features?: string[];
  };
  payload: P;
}

type BundleKind =
  | "workspace"
  | "data-setup"
  | "visualization"
  | "document"
  | "project"
  | "workbench"
  | "workspace-board"
  | "portable-data";
```

Use JSON as the canonical initial format. A zip container can later include JSON plus embedded data, thumbnails, or attachments without changing the logical schema.

## 5.3 Suggested payloads

```ts
interface WorkspaceBundlePayload {
  workspaces: SerializedWorkspace[];
  selectedWorkspaceId?: string;
}

interface DataSetupPayload {
  id: string;
  name: string;
  source: SerializedSourceBinding;
  budget: number;
  steps: Step[];
  typeOverrides?: Record<string, FieldType>;
}

interface VisualizationPayload {
  geom: Geom;
  mapping: Record<Channel, string | null>;
  yScale: "linear" | "log";
}

interface ProjectBundlePayload {
  project: ProjectMetadata;
  dataSetups: Record<string, DataSetupPayload>;
  documents: Record<string, SerializedDocument>;
  snapshots: Record<string, SerializedSnapshot>;
  watch?: SerializedPresentationRef[];
}

interface WorkbenchBundlePayload {
  project: ProjectBundlePayload;
  layout: WorkspaceBundlePayload;
  session?: {
    activeDocumentId?: string;
    comparePins?: [string | null, string | null];
  };
}

interface WorkspaceBoardPayload {
  boardTree: SplitTree<{
    surfaceId: string;
    workspaceId: string;
    projectId?: string;
  }>;
}
```

## 5.4 Minimal implementation over the current model

Do not normalize the entire state model before shipping export.

The first implementation can derive a data setup from the existing document:

```ts
function dataSetupFromDoc(doc: Doc): DataSetupPayload {
  return {
    id: crypto.randomUUID(),
    name: `${doc.name} data`,
    source: encodeSource(doc.spec.source),
    budget: doc.limit,
    steps: structuredClone(doc.spec.steps),
    typeOverrides: structuredClone(doc.spec.typeOverrides),
  };
}
```

A visualization setup comes from the remaining `ChartSpec` fields.

This immediately enables:

- export data recipe;
- import data recipe into a new or existing document;
- export visualization separately;
- export full document;

Longer term, if users regularly share one transformed dataset across several visualizations, normalize `DataSetup` into first-class project state and let documents reference it by ID. Do this because the usage exists, not only because normalization looks elegant.

## 5.5 Pure codecs and storage adapters

Split the current persistence module into two layers.

### Pure layer

```ts
encodeWorkspace(state): BundleEnvelope
encodeProject(state): BundleEnvelope
encodeWorkbench(state): BundleEnvelope
validateBundle(value): Result<BundleEnvelope>
migrateBundle(value): Result<CurrentBundle>
importBundle(current, bundle, policy): ImportPlan
applyImportPlan(state, plan): State
```

### Storage/browser layer

```ts
interface PersistenceAdapter {
  load(slot: string): Promise<BundleEnvelope | null>;
  save(slot: string, bundle: BundleEnvelope): Promise<void>;
  remove(slot: string): Promise<void>;
  list?(): Promise<SavedBundleSummary[]>;
}
```

Implementations:

- namespaced localStorage for small autosaves;
- IndexedDB for named local projects or embedded data;
- browser download/upload for files;
- optional Datadrop server storage later;
- in-memory adapter for tests and demos.

The Workbench component should not own a debounce effect over whole world objects. Use Redux listener middleware or a persistence controller subscribing to the store:

```ts
listenerMiddleware.startListening({
  matcher: isPersistentAction,
  effect: debounceSaveCurrentProject,
});
```

This centralizes persistence, makes it testable, and avoids tying save semantics to a particular page component.

## 5.6 Migrations

The current validator rejects any version other than 1. Portable files need migrations:

```ts
const migrations: Record<number, (input: unknown) => unknown> = {
  1: migrateV1ToV2,
  2: migrateV2ToV3,
};

function migrateToCurrent(input: unknown): Result<BundleVCurrent> {
  const header = parseHeader(input);
  let value = input;
  for (let v = header.version; v < CURRENT_VERSION; v++) {
    value = migrations[v](value);
  }
  return validateCurrent(value);
}
```

Migration rules should be deterministic and pure. Keep golden fixtures for every historical version.

## 5.7 Import ID remapping

Importing into an existing project must not trust incoming IDs.

Build an import plan:

```ts
interface ImportIdMap {
  workspaces: Map<string, string>;
  nodes: Map<string, string>;
  documents: Map<string, string>;
  dataSetups: Map<string, string>;
  steps: Map<string, string>;
  snapshots: Map<string, string>;
  viewInstances: Map<string, string>;
}
```

Then rewrite every reference through that map before committing one atomic state change.

Offer explicit conflict policies:

- **replace:** replace current project/workspaces;
- **merge:** import as additional objects with new IDs;
- **duplicate:** always create renamed copies;
- **apply:** apply a setup to a selected existing document;
- **open separately:** create a new project runtime.

Never silently overwrite by matching display names.

## 5.8 Missing apps and sources

An imported workspace can reference an app not installed in the current host. An imported project can reference a source the current user cannot read.

Represent both explicitly:

```ts
interface UnresolvedAppBinding {
  kind: "unresolved-app";
  appId: string;
  encodedState?: JsonValue;
}

interface UnresolvedSourceBinding {
  kind: "unresolved-source";
  sourceKind: string;
  encodedRef: JsonValue;
  reason: "adapter-missing" | "not-found" | "forbidden" | "invalid";
}
```

The UI should render a repair panel, not fall back to another app or the active document without telling the user.

## 5.9 Security and privacy

Continue the current structural rule that secrets cannot enter presentation values or persisted state.

For portable bundles:

- use per-type and per-source whitelisting;
- run the current secret-key scanner as defense in depth;
- never include bearer tokens, cookies, RTK Query cache, token creation responses, or browser session details;
- warn before embedding table rows;
- include source identifiers but not credentials;
- keep link-style exports in the URL fragment rather than query parameters;
- allow hosts to mark fields or source kinds nonexportable.

## 5.10 Canonical serialization

For stable diffs and reproducible sharing:

- sort object-map keys where order is not semantic;
- preserve explicit arrays where order is semantic;
- normalize empty optional objects to `undefined` or omit them consistently;
- store ISO timestamps;
- do not store locale-formatted times;
- do not store derived plot geometry or fetched table caches;
- include app and source requirements.

---

# 6. Multiple workspaces and multiple workbenches

The phrase “multiple workspaces on the same page” describes three different products. The architecture should support all three deliberately.

## 6.1 Mode A: switchable workspaces over one project

This is the current behavior:

```text
one Redux world
one layout collection
one currentSpaceId
one rendered WorkspaceSurface
```

Documents and snapshots are shared. Switching workspace changes only the layout camera.

Keep this mode as the default shell.

## 6.2 Mode B: several visible workspace surfaces over one project

Example:

```tsx
<ProjectProvider projectId="analysis-1">
  <WorkspaceBoard>
    <WorkspaceSurface workspaceId="build" />
    <WorkspaceSurface workspaceId="explore" />
    <WorkspaceSurface workspaceId="compare" />
  </WorkspaceBoard>
</ProjectProvider>
```

All surfaces share documents. A filter applied from a mark in one surface updates every view of the same document in the other surfaces.

Requirements:

- every layout operation includes `workspaceId`;
- each tile knows its workspace scope;
- close/split capability is computed for that workspace;
- drag targets are scoped by board policy;
- PBUI accept scope is explicit;
- menus identify both document target and workspace where relevant;
- focus management distinguishes surfaces.

Recommended default policies:

```text
Accept scope      project-wide
Menu scope        one active menu per PBUI root
Drag scope        workspace-local
Cross-workspace   explicit “move/copy tile to workspace…” command
Active document   project-wide, visibly named
```

Project-wide accept preserves the CLIM value proposition: a command in one workspace can accept an object displayed in another. Cross-workspace drag is more dangerous and should not happen accidentally through one global DOM registry.

## 6.3 Mode C: several independent workbenches on one page

This is what the attached landing demo demonstrates conceptually: several embedded workbench instances, each with its own world, workspaces, and accept plumbing.

The reusable API should make isolation explicit:

```tsx
const runtimeA = createWorkbenchRuntime({
  id: "demo-a",
  store: createWorkbenchStore(initialA),
  persistence: memoryPersistence(),
});

const runtimeB = createWorkbenchRuntime({
  id: "demo-b",
  store: createWorkbenchStore(initialB),
  persistence: memoryPersistence(),
});

<div className="examples">
  <WorkbenchRoot runtime={runtimeA} />
  <WorkbenchRoot runtime={runtimeB} />
</div>
```

Isolation tests must prove:

- accept in A does not light presentations in B;
- drag in A cannot target a tile in B;
- menus and mouse documentation do not cross;
- app registries can differ;
- active document changes do not cross;
- autosave keys do not collide;
- one root can unmount during a drag without leaking listeners.

## 6.4 Workspace board as an outer split tree

A workspace board can reuse the generic tree core:

```ts
type WorkspaceBoardTree = SplitTree<{
  workspaceId: string;
  projectId?: string;
  surfaceOptions?: {
    showWorkspaceStrip?: boolean;
    showStatusLine?: boolean;
  };
}>;
```

This supports nested side-by-side and stacked workspaces without inventing another layout algorithm.

The inner tree manages app tiles. The outer tree manages workspace surfaces. Keep their drag runtimes and command types distinct even if they share pure tree utilities.

## 6.5 Workspace templates versus instances

Current pinned workspaces are rebuilt from code and replace stored versions. That policy is valid for account and welcome screens, but a reusable package should express it as templates:

```ts
interface WorkspaceTemplate {
  id: string;
  version: number;
  name: string;
  create(context: TemplateContext): Workspace;
  updatePolicy: "replace" | "merge" | "detach-on-edit";
}
```

User-created workspaces are instances. Exporting a template-backed workspace should offer:

- export the template reference;
- detach and export a concrete copy;
- export only user overrides if the template supports merging.

---

# 7. Data setups and reusable manipulation

## 7.1 What “data setup” should mean

A data setup is the reusable relationship between a source and a pipeline, independent of a chart picture:

```ts
interface DataSetup {
  id: string;
  name: string;
  source: SourceBinding;
  budget: number;
  steps: Step[];
  typeOverrides?: Record<string, FieldType>;
}
```

This can feed:

- a table;
- one or several charts;
- a statistics panel;
- a data-quality panel;
- an export command;
- a future model or notebook widget.

## 7.2 Current model versus normalized model

The current document owns both data and visualization state. That is simple and useful:

```text
Doc
  └── ChartSpec
        ├── source
        ├── steps
        ├── mapping
        ├── geom
        └── scale
```

A normalized future model would be:

```text
DataSetup
  ├── source
  ├── budget
  ├── steps
  └── type overrides

VisualizationDocument
  ├── dataSetupId
  ├── mapping
  ├── geom
  └── scale
```

Do not normalize only to satisfy architectural aesthetics. Use this decision rule:

- If users mostly want one pipeline per chart, keep the current document as the editing unit and provide data-setup import/export projections.
- If users repeatedly need several independent visualizations over one shared transformed relation, promote `DataSetup` to first-class project state.

The export schema can support both without forcing the internal migration immediately.

## 7.3 Pipeline extension model

The five fixed step kinds are a coherent v1 package API. Avoid a generic plugin framework until another operation is genuinely needed.

When extension becomes necessary, use registered operation definitions:

```ts
interface PipelineOperationDefinition<S extends Step> {
  kind: S["kind"];
  validate(step: unknown): Result<S>;
  schema(fields: Field[], step: S): Field[];
  evaluate(rows: Row[], fields: Field[], step: S): OperationResult;
  label(step: S): string;
  codec: Codec<S>;
}
```

Keep schema and row evaluation as separate methods so render paths can remain row-free.

## 7.4 Derived-data cache

With several workspaces showing the same document, derived pipeline data should be computed once per document revision, not once per tile.

A cache key needs:

```text
source identity + table revision + row budget + steps identity/hash + type overrides
```

Expose selectors/hooks:

```ts
useDocumentFields(docId)   // schemaAfter; cheap
useDocumentData(docId)     // evaluated rows; memoized
useDocumentPlot(docId, view, size)
```

A project runtime can own this derived cache. It is not persisted.

## 7.5 Exporting processed data

Keep current CSV semantics: export pipeline output, not source input.

Add setup-level export commands:

```text
Export data setup JSON
Export visualization JSON
Export document JSON
Export pipeline output CSV
Export chart PNG
Copy chart permalink
Export project/workbench bundle
```

These are different verbs and should be named distinctly in menus.

---

# 8. UI and widget packaging

## 8.1 Preserve the panel/container split

The branch is already moving in the correct direction. Continue until all generic feature UIs have presentational panels and stories.

Good package candidates:

- `ChartPanel` and SVG renderer;
- `TablePanel`;
- `PipelinePanel`;
- `EncodingPanel`;
- document manager panel;
- snapshot gallery panel;
- comparison panel;
- inspector panel;
- watchlist panel;
- trace panel;
- source browser panel, with source DTOs abstracted;
- window-manager chrome;
- presentation chips and badges.

Host-specific candidates that should remain outside generic packages:

- sign-in;
- profile and sessions;
- API token management;
- member management;
- Datadrop upload workflow;
- hardwired welcome/account/tutorial workspaces.

## 8.2 Avoid a universal widget prop API

Do not turn the design system into a generic `Box`/style-prop system. The existing guidelines are correct: widgets should expose bounded semantic props grounded in real call sites.

The reusable boundary is behavior and data shape, not arbitrary styling.

## 8.3 Theme API

The package should expose:

- semantic CSS custom properties;
- stable `data-part` names only where external theming needs them;
- an optional default stylesheet;
- plot palette options aligned with CSS tokens.

Do not export internal font files or hard-code host page furniture into widgets.

## 8.4 Widget state classification

For each app, document where every state lives:

| State kind | Example | Location |
|---|---|---|
| project | pipeline steps | project/world store |
| resource binding | document shown by tile | workspace leaf |
| persistent view state | table column widths | workspace view-state object |
| session view state | currently open gallery filter | session slice or local state |
| ephemeral DOM state | active pointer drag | scoped runtime only |
| server cache | fetched table | RTK Query |

This prevents both extremes: putting everything in Redux and losing meaningful state whenever a tile remounts.

---

# 9. Concrete provider and hook proposal

## 9.1 Host composition

```tsx
export function DatadropWorkbench({ runtime }: { runtime: DatadropRuntime }) {
  return (
    <WorkbenchRuntimeProvider runtime={runtime.core}>
      <Provider store={runtime.store}>
        <DataSourceProvider registry={runtime.sources}>
          <PresentationRegistryProvider registry={runtime.presentations}>
            <CommandProvider registry={runtime.commands}>
              <PbuiRoot scopeId={runtime.id}>
                <WorkbenchPage />
              </PbuiRoot>
            </CommandProvider>
          </PresentationRegistryProvider>
        </DataSourceProvider>
      </Provider>
    </WorkbenchRuntimeProvider>
  );
}
```

`PbuiRoot` internally composes accept, menu, and mouse-documentation stores.

## 9.2 Typed Redux hooks

Create once:

```ts
export const useAppDispatch = useDispatch.withTypes<AppDispatch>();
export const useAppSelector = useSelector.withTypes<RootState>();
export const useAppStore = useStore.withTypes<AppStore>();
```

This removes repeated generic assertions and makes a store factory easier to expose.

## 9.3 Project and document hooks

```ts
useProject(projectId)
useDocument(docId)
useActiveDocumentId(projectId)
useSetActiveDocument(projectId)
useDocumentFields(docId)
useDocumentData(docId)
useDocumentVisualization(docId)
useDocumentPlot(docId, size)
useSnapshots(projectId)
```

## 9.4 Workspace hooks

```ts
useWorkspace(workspaceId)
useCurrentWorkspaceId()
useWorkspaceController(workspaceId)
useWorkspaceApps(workspaceId)
useWorkspaceResourceBindings(workspaceId)
useWorkspaceBoard(boardId)
```

## 9.5 Presentation hooks

```ts
usePresentationDefinition(ptype)
usePresentationInteraction(ptype, value)
useAccept(request)
useAcceptController()
useAcceptMatch(ptype, value)
useObjectMenuState()
useObjectMenuController()
useMouseDocumentationText()
useMouseDocumentationWriter()
useCommandDispatcher()
```

## 9.6 Persistence hooks

```ts
useAutosave(projectId)
useSavedProjects()
useExportBundle(kind, options)
useImportBundle()
useImportPreview(file)
useUnresolvedBindings(projectId)
```

The actual encode/decode logic remains outside React.

---

# 10. Migration plan

## Phase 0 — lock the baseline

Before moving files:

- record the analyzed branch revision;
- run `make ui-test`, `make storybook`, and the relevant Go tests;
- add a Storybook page with two isolated workbench stores;
- add a fixture with two dataset versions sharing the same path;
- add render-count instrumentation for a chart with many marks;
- add a bundle fixture representing the current persisted v1 payload.

## Phase 1 — fix correctness and measured performance

1. Add `fieldsFor` to `PbuiEnvironment`.
2. Make `FieldChip` and field actions resolve schema without evaluating rows.
3. Keep `tableFor` for inspection/statistics only and memoize it.
4. Use exact source equality including dataset version.
5. Split plot compilation so `useDocPlot` does not evaluate twice.
6. Replace pipeline step counters with injected/UUID IDs.
7. Add performance and ID-collision regression tests.

This phase should land before package extraction.

## Phase 2 — complete the PBUI contract

1. Implement explicit descriptors for `channel`, `chart`, `tile`, and `workspace`.
2. Add compile-time/runtime descriptor completeness checks.
3. Implement or remove the placeholder document-to-source conversion.
4. Split the command executor into registrable command handlers.
5. Route account/upload trace commands through actual handlers.
6. Give menu actions stable IDs.
7. Add per-presentation codecs.
8. Make `Presentation` generic over its type.

## Phase 3 — make workspace scope explicit

1. Add `workspaceId` to every tree command.
2. Pass workspace scope through `NodeView`, `SplitView`, `Tile`, `DocBar`, and drag logic.
3. Replace selectors that inspect `currentSpaceId` inside each tile.
4. Add `<WorkspaceSurface workspaceId>`.
5. Create a scoped drag runtime and remove module globals.
6. Test two concurrently rendered workspaces sharing one world.

Keep `currentSpaceId` as shell navigation state, not mutation target state.

## Phase 4 — separate PBUI update channels

1. Split stable services from accept/menu/mouse state.
2. Use external-store selectors for high-frequency state.
3. Ensure mouse-documentation updates rerender only the status line.
4. Define chart-mark focus policy.
5. Test render counts and keyboard behavior.

## Phase 5 — portable bundles

1. Extract pure codecs from `persist.ts`.
2. Define the bundle envelope and current schema version.
3. Add workspace, data-setup, visualization, document, project, and workbench codecs.
4. Add import preview and ID-remapping plan.
5. Add migration fixtures.
6. Add unresolved app/source handling.
7. Add file download/upload UI.
8. Move autosave to listener middleware or a persistence controller.
9. Namespace storage by runtime/project.

## Phase 6 — multi-root and workspace board

1. Introduce `createWorkbenchRuntime`.
2. Make app, presentation, command, source, and conversion registries instance-owned.
3. Add independent `<WorkbenchRoot runtime>` instances.
4. Add `WorkspaceBoard` using the generic split tree.
5. Define project-wide accept and workspace-local drag defaults.
6. Add isolation tests.

## Phase 7 — internal package extraction

Move only boundaries already proven by imports:

1. `workspace-core`;
2. `table-core`;
3. `graphics-core`;
4. `pbui-core`;
5. React packages;
6. widget package;
7. host adapters.

Use Bun workspaces or TypeScript project references internally. Keep the packages private until APIs have at least one second consumer: the Datadrop app plus the landing/demo page is enough.

## Phase 8 — optional first-class data setups

After observing real use:

- promote named data setups into project state;
- let several documents reference one setup;
- define copy-on-write or shared-edit semantics;
- add data-setup presentations and commands;
- add dependency/impact UI when changing a setup used by several documents.

Do not silently change current document semantics during the earlier infrastructure work.

---

# 11. Required regression tests

## Architecture contracts

- Every `PresentationType` has exactly one assembled descriptor.
- Every command type has a handler or is explicitly declared observational.
- Duplicate app, presentation, command, and conversion IDs fail.
- Generic packages do not import the Datadrop API or host store.
- App registration order does not change persisted identity.

## Multiple-root isolation

- Two roots can use different stores and registries.
- Accept, menu, mouse documentation, drag, active document, and autosave do not cross roots.
- Unmounting one root does not break the other.
- Storage keys are namespaced.

## Concurrent workspaces

- Split workspace B while workspace A remains current.
- Resize a divider in B and verify only B changes.
- Close a tile in B and compute close capability from B.
- Project-wide accept can be satisfied from either visible workspace.
- Workspace-local drag cannot target the other workspace.
- Explicit move/copy commands can transfer a tile if enabled.

## Persistence and bundles

- Every bundle kind round-trips.
- Every historical schema migrates to current.
- Import remaps every ID and reference.
- Unknown app/source bindings survive as unresolved objects.
- No credentials or secret-shaped fields can be exported.
- A portable-data export requires explicit opt-in.
- Pinned/template workspaces obey their declared update policy.
- Malformed ratios, duplicate node IDs, dangling document IDs, invalid step IDs, and invalid mappings are rejected or repaired visibly.

## Performance

- Rendering field chips never calls the row-evaluating resolver.
- One document pipeline is evaluated at most once per revision per derived-data cache.
- Plot compilation does not reevaluate an already evaluated pipeline.
- Hovering a datum does not rerender sibling datum presentations.
- Divider drag is frame-bounded and commits persistence after settling.

## Accessibility

- Large charts do not create one tab stop per mark.
- Dividers remain keyboard adjustable.
- Object menus restore focus to their invoker.
- Multiple workspace surfaces have named regions and navigable headings.
- Accept mode has a programmatic announcement and a reliable cancel path.

---

# 12. What not to do

1. **Do not replace Redux with one mutable class and a notify callback.** The branch already fixed the prototype’s main correctness and rendering weakness.
2. **Do not create another data pipeline beside `model/pipeline.ts`.** Extend or package the existing one.
3. **Do not persist RTK Query state.** Persist references and user decisions, then refetch.
4. **Do not treat localStorage autosave as the portable file format.** Separate codecs from storage.
5. **Do not add one larger provider containing every runtime state.** Stable services and high-frequency state need different subscription boundaries.
6. **Do not make cross-workspace drag happen merely because two DOM nodes share a module-global map.** Define the policy.
7. **Do not hide unavailable commands.** Keep the existing `disabledBecause` teaching model.
8. **Do not generalize pipeline operations, geoms, or widget styling before a real second use case exists.** Package the proven core first.
9. **Do not move host-specific auth and upload semantics into generic PBUI packages.** PBUI provides command and presentation machinery; the host defines those objects.
10. **Do not export secrets, caches, transient continuations, derived geometry, or DOM state.**

---

# 13. Suggested first-week reading path for a new developer

1. Read `README.md` through the stream/dataset distinction and quick start.
2. Read `ui/GUIDELINES.md` completely.
3. Read `ui/src/model/table.ts`, `pipeline.ts`, `chart.ts`, and the beginning of `plot.ts`.
4. Read `ui/src/store/world.ts`, then `layout.ts`, then `persist.ts`.
5. Trace one field right-click through:
   - `FieldChip`;
   - `Presentation`;
   - `ObjectMenu`;
   - `fieldDescriptor`;
   - `Verb`;
   - `actionsForVerb`;
   - `world` reducer.
6. Trace one document-bound tile through:
   - `Workbench`;
   - `NodeView`;
   - `Tile`;
   - `appkit/registry`;
   - `ChartApp` or `TableApp`;
   - `useDocTable` and `useDocPipeline`.
7. Open Storybook and inspect the awkward/error states, not only the default states.
8. Run `make ui-test` before and after any change.
9. Read the DATADROP-3, DATADROP-4, and DATADROP-6 design documents when touching the model, PBUI, or component layers.

A useful first contribution would be one of:

- descriptor completeness and workspace/tile commands;
- the `fieldsFor` render-path fix;
- UUID/injected step IDs;
- exact source matching with dataset version;
- a two-runtime isolation story and test.

These are bounded changes that teach the architecture and close real gaps.

---

# 14. Final recommendation

The branch should be treated as the implementation base for a reusable workbench platform. It already demonstrates the difficult ideas:

- one typed table seam;
- a pure pipeline and graphics compiler;
- live documents with cheap views;
- a serializable split-tree layout;
- presentation-driven menus and cross-window argument acceptance;
- command values separated from reducers;
- storyable panels and enforced architecture.

The package effort should focus on five explicit boundaries:

1. **runtime ownership:** no module-global registries or drag state;
2. **workspace ownership:** every layout mutation names its workspace;
3. **subscription ownership:** presentations subscribe only to state they use;
4. **resource ownership:** apps declare bindings and codecs rather than a boolean;
5. **serialization ownership:** portable, versioned bundles are separate from autosave adapters.

Once those are in place, the same core can support:

- the existing Datadrop workbench;
- several independent tutorial/demo workbenches on one page;
- several simultaneous workspace views over one project;
- saved and shareable window arrangements;
- named data preparation setups;
- reusable visualization setups;
- complete project/workbench exports;
- host-specific widget sets built on one PBUI interaction model.

That is an incremental extraction from a sound codebase, not a rewrite.

---

# Appendix A — Proposed public types

```ts
export type JsonPrimitive = string | number | boolean | null;
export type JsonValue = JsonPrimitive | JsonValue[] | { [key: string]: JsonValue };
export type JsonObject = { [key: string]: JsonValue };

export interface IdFactory {
  next(namespace: string): string;
}

export interface Codec<T> {
  encode(value: T): JsonValue;
  decode(value: JsonValue): Result<T>;
}

export interface ResourceBinding {
  kind: string;
  id: string;
  encoded?: JsonValue;
}

export interface AppTileValue<V extends JsonValue = JsonValue> {
  appId: string;
  appVersion?: number;
  binding?: ResourceBinding;
  viewState?: V;
}

export interface Workspace<V extends JsonValue = JsonValue> {
  id: string;
  name: string;
  tree: SplitTree<AppTileValue<V>>;
  origin?:
    | { kind: "user" }
    | { kind: "template"; templateId: string; templateVersion: number };
}
```

# Appendix B — Proposed project model, normalized form

```ts
export interface ProjectState {
  id: string;
  name: string;
  dataSetups: Record<string, DataSetup>;
  dataSetupOrder: string[];
  documents: Record<string, VisualizationDocument>;
  documentOrder: string[];
  snapshots: Record<string, DocumentSnapshot>;
}

export interface DataSetup {
  id: string;
  name: string;
  source: ResourceBinding;
  budget: number;
  steps: Step[];
  typeOverrides?: Record<string, FieldType>;
}

export interface VisualizationDocument {
  id: string;
  name: string;
  dataSetupId: string;
  visual: VisualizationSpec;
}

export interface VisualizationSpec {
  geom: Geom;
  mapping: Record<Channel, string | null>;
  yScale: "linear" | "log";
}
```

This normalized form is a possible later state. The current `Doc + ChartSpec` model remains a valid implementation until shared data setups become a real editing requirement.

# Appendix C — Acceptance criteria for the first reusable release

A first reusable release is ready when all of the following are true:

- two independent runtimes mount on one page with no shared state;
- two workspaces from one project render and remain editable simultaneously;
- app and presentation registries are runtime-owned and validate duplicate IDs;
- every public presentation type has a descriptor;
- every command has an executor;
- field rendering is row-free;
- pipeline output is not recomputed redundantly for each field or plot stage;
- step IDs remain unique after reload and import;
- workspace, data setup, document, project, workbench, and board bundles round-trip;
- bundle import remaps IDs and reports unresolved apps/sources;
- no credentials are serializable through any bundle codec;
- chart marks have a bounded keyboard-navigation strategy;
- the existing layer, Storybook, model, store, security, and browser tests remain green.

# Appendix D — Source index at the analyzed revision

The review was performed against commit `08f814b685d0c2fa3d968fe7835079a323883971`. The following files are the shortest path back to each major claim.

## Product and development workflow

- [`README.md`](https://github.com/go-go-golems/go-go-datadrop/blob/08f814b685d0c2fa3d968fe7835079a323883971/README.md) — product model, streams versus datasets, server modes, commands, and API overview.
- [`Makefile`](https://github.com/go-go-golems/go-go-datadrop/blob/08f814b685d0c2fa3d968fe7835079a323883971/Makefile) — authoritative UI build, test, development, and Storybook commands.
- [`ui/package.json`](https://github.com/go-go-golems/go-go-datadrop/blob/08f814b685d0c2fa3d968fe7835079a323883971/ui/package.json) — frontend dependencies and scripts.
- [`ui/GUIDELINES.md`](https://github.com/go-go-golems/go-go-datadrop/blob/08f814b685d0c2fa3d968fe7835079a323883971/ui/GUIDELINES.md) — component rules, layer graph, stories, tokens, presentation rules, and authoring procedure.

## Runtime and state

- [`ui/src/main.tsx`](https://github.com/go-go-golems/go-go-datadrop/blob/08f814b685d0c2fa3d968fe7835079a323883971/ui/src/main.tsx) — browser mount and top-level Redux Provider.
- [`ui/src/components/pages/Workbench/Workbench.tsx`](https://github.com/go-go-golems/go-go-datadrop/blob/08f814b685d0c2fa3d968fe7835079a323883971/ui/src/components/pages/Workbench/Workbench.tsx) — composition root, current workspace rendering, PBUI environment, command application, and autosave effect.
- [`ui/src/store/index.ts`](https://github.com/go-go-golems/go-go-datadrop/blob/08f814b685d0c2fa3d968fe7835079a323883971/ui/src/store/index.ts) — store factory and state-domain separation.
- [`ui/src/store/world.ts`](https://github.com/go-go-golems/go-go-datadrop/blob/08f814b685d0c2fa3d968fe7835079a323883971/ui/src/store/world.ts) — live documents, snapshots, watchlist, inspection, pins, and trace.
- [`ui/src/store/layout.ts`](https://github.com/go-go-golems/go-go-datadrop/blob/08f814b685d0c2fa3d968fe7835079a323883971/ui/src/store/layout.ts) — split tree, workspaces, pure operations, and current-workspace reducers.
- [`ui/src/store/spaces.ts`](https://github.com/go-go-golems/go-go-datadrop/blob/08f814b685d0c2fa3d968fe7835079a323883971/ui/src/store/spaces.ts) — code-owned workspace presets and pinned-space policy.
- [`ui/src/store/persist.ts`](https://github.com/go-go-golems/go-go-datadrop/blob/08f814b685d0c2fa3d968fe7835079a323883971/ui/src/store/persist.ts) — version-1 localStorage payload, defensive validation, pinned-space merge, and secret scan.
- [`ui/src/store/applyVerb.ts`](https://github.com/go-go-golems/go-go-datadrop/blob/08f814b685d0c2fa3d968fe7835079a323883971/ui/src/store/applyVerb.ts) — current command-to-Redux seam and PBUI environment builder.

## Pure data and graphics model

- [`ui/src/model/table.ts`](https://github.com/go-go-golems/go-go-datadrop/blob/08f814b685d0c2fa3d968fe7835079a323883971/ui/src/model/table.ts) — `Table`, fields, types, provenance, and Datadrop-shaped `SourceRef`.
- [`ui/src/model/pipeline.ts`](https://github.com/go-go-golems/go-go-datadrop/blob/08f814b685d0c2fa3d968fe7835079a323883971/ui/src/model/pipeline.ts) — pipeline steps, module-level step counter, `schemaAfter`, and `evaluate`.
- [`ui/src/model/chart.ts`](https://github.com/go-go-golems/go-go-datadrop/blob/08f814b685d0c2fa3d968fe7835079a323883971/ui/src/model/chart.ts) — chart specification, channel constraints, defaults, and exact source equality helper.
- [`ui/src/model/plot.ts`](https://github.com/go-go-golems/go-go-datadrop/blob/08f814b685d0c2fa3d968fe7835079a323883971/ui/src/model/plot.ts) — pure plot geometry compiler, caps, palette, and its internal pipeline evaluation.
- [`ui/src/model/permalink.ts`](https://github.com/go-go-golems/go-go-datadrop/blob/08f814b685d0c2fa3d968fe7835079a323883971/ui/src/model/permalink.ts) — chart-spec URL-fragment codec.
- [`ui/src/export/csv.ts`](https://github.com/go-go-golems/go-go-datadrop/blob/08f814b685d0c2fa3d968fe7835079a323883971/ui/src/export/csv.ts) — pipeline-output CSV encoding and browser download.
- [`ui/src/export/png.ts`](https://github.com/go-go-golems/go-go-datadrop/blob/08f814b685d0c2fa3d968fe7835079a323883971/ui/src/export/png.ts) — SVG-to-PNG browser conversion.
- [`ui/src/apps/useTable.ts`](https://github.com/go-go-golems/go-go-datadrop/blob/08f814b685d0c2fa3d968fe7835079a323883971/ui/src/apps/useTable.ts) — RTK Query table hooks, default-chart seeding, field/table resolver, pipeline derivation, and plot derivation.

## PBUI protocol

- [`ui/src/pbui/types.ts`](https://github.com/go-go-golems/go-go-datadrop/blob/08f814b685d0c2fa3d968fe7835079a323883971/ui/src/pbui/types.ts) — public presentation vocabulary and environment interface.
- [`ui/src/pbui/registry.ts`](https://github.com/go-go-golems/go-go-datadrop/blob/08f814b685d0c2fa3d968fe7835079a323883971/ui/src/pbui/registry.ts) — assembled descriptor registry and its current missing public types.
- [`ui/src/pbui/verbs.ts`](https://github.com/go-go-golems/go-go-datadrop/blob/08f814b685d0c2fa3d968fe7835079a323883971/ui/src/pbui/verbs.ts) — serializable command union.
- [`ui/src/pbui/PbuiProvider.tsx`](https://github.com/go-go-golems/go-go-datadrop/blob/08f814b685d0c2fa3d968fe7835079a323883971/ui/src/pbui/PbuiProvider.tsx) — accept, menu, mouse documentation, conversions, and command context in one provider.
- [`ui/src/pbui/Presentation.tsx`](https://github.com/go-go-golems/go-go-datadrop/blob/08f814b685d0c2fa3d968fe7835079a323883971/ui/src/pbui/Presentation.tsx) — HTML/SVG presentation wrapper and current focus behavior.
- [`ui/src/pbui/ObjectMenu.tsx`](https://github.com/go-go-golems/go-go-datadrop/blob/08f814b685d0c2fa3d968fe7835079a323883971/ui/src/pbui/ObjectMenu.tsx) — descriptor-driven object menu.
- [`ui/src/pbui/conversions.ts`](https://github.com/go-go-golems/go-go-datadrop/blob/08f814b685d0c2fa3d968fe7835079a323883971/ui/src/pbui/conversions.ts) — current conversion table and document-to-source placeholder.
- [`ui/src/pbui/descriptors/field.ts`](https://github.com/go-go-golems/go-go-datadrop/blob/08f814b685d0c2fa3d968fe7835079a323883971/ui/src/pbui/descriptors/field.ts) — field resolution, statistics, and type-aware commands.
- [`ui/src/pbui/descriptors/doc.ts`](https://github.com/go-go-golems/go-go-datadrop/blob/08f814b685d0c2fa3d968fe7835079a323883971/ui/src/pbui/descriptors/doc.ts) — document presentation semantics.

## Applications, components, and window manager

- [`ui/src/appkit/registry.ts`](https://github.com/go-go-golems/go-go-datadrop/blob/08f814b685d0c2fa3d968fe7835079a323883971/ui/src/appkit/registry.ts) — process-global app registry and `docBound` contract.
- [`ui/src/apps/all.ts`](https://github.com/go-go-golems/go-go-datadrop/blob/08f814b685d0c2fa3d968fe7835079a323883971/ui/src/apps/all.ts) — side-effect registration entry point.
- [`ui/src/components/organisms/Tile/Tile.tsx`](https://github.com/go-go-golems/go-go-datadrop/blob/08f814b685d0c2fa3d968fe7835079a323883971/ui/src/components/organisms/Tile/Tile.tsx) — tile chrome, app resolution, current-workspace close selector, and app switching.
- [`ui/src/components/organisms/Tile/useDrag.ts`](https://github.com/go-go-golems/go-go-datadrop/blob/08f814b685d0c2fa3d968fe7835079a323883971/ui/src/components/organisms/Tile/useDrag.ts) — module-global tile registry and drag state.
- [`ui/src/components/organisms/SplitView/SplitView.tsx`](https://github.com/go-go-golems/go-go-datadrop/blob/08f814b685d0c2fa3d968fe7835079a323883971/ui/src/components/organisms/SplitView/SplitView.tsx) — recursive workspace rendering and divider interaction.
- [`ui/src/components/organisms/WorkspaceStrip/WorkspaceStrip.tsx`](https://github.com/go-go-golems/go-go-datadrop/blob/08f814b685d0c2fa3d968fe7835079a323883971/ui/src/components/organisms/WorkspaceStrip/WorkspaceStrip.tsx) — current workspace navigation and promised presentation menus.
- [`ui/src/components/molecules/DocBar/DocBar.tsx`](https://github.com/go-go-golems/go-go-datadrop/blob/08f814b685d0c2fa3d968fe7835079a323883971/ui/src/components/molecules/DocBar/DocBar.tsx) — document binding and fallback to the active document.
- [`ui/src/components/atoms/FieldChip/FieldChip.tsx`](https://github.com/go-go-golems/go-go-datadrop/blob/08f814b685d0c2fa3d968fe7835079a323883971/ui/src/components/atoms/FieldChip/FieldChip.tsx) — render-time field resolution.
- [`ui/src/apps/ChartApp/ChartApp.tsx`](https://github.com/go-go-golems/go-go-datadrop/blob/08f814b685d0c2fa3d968fe7835079a323883971/ui/src/apps/ChartApp/ChartApp.tsx) — container/panel split and debounced plot sizing.
- [`ui/src/components/organisms/ChartPanel/ChartPanel.tsx`](https://github.com/go-go-golems/go-go-datadrop/blob/08f814b685d0c2fa3d968fe7835079a323883971/ui/src/components/organisms/ChartPanel/ChartPanel.tsx) — row-backed SVG presentations and visual honesty around caps.
- [`ui/src/apps/TokensApp/TokensApp.tsx`](https://github.com/go-go-golems/go-go-datadrop/blob/08f814b685d0c2fa3d968fe7835079a323883971/ui/src/apps/TokensApp/TokensApp.tsx) — concrete example of a host mutation followed by a PBUI trace verb that the current executor does not handle.

## Tests and design records

- [`ui/test/store.test.ts`](https://github.com/go-go-golems/go-go-datadrop/blob/08f814b685d0c2fa3d968fe7835079a323883971/ui/test/store.test.ts) — tree, world, command, persistence, and security invariants.
- [`ui/test/layers.test.ts`](https://github.com/go-go-golems/go-go-datadrop/blob/08f814b685d0c2fa3d968fe7835079a323883971/ui/test/layers.test.ts) — one-way import graph.
- [`ui/test/export.test.ts`](https://github.com/go-go-golems/go-go-datadrop/blob/08f814b685d0c2fa3d968fe7835079a323883971/ui/test/export.test.ts) — CSV and chart-permalink contracts.
- [`DATADROP-3 visualization workbench guide`](https://github.com/go-go-golems/go-go-datadrop/blob/08f814b685d0c2fa3d968fe7835079a323883971/ttmp/2026/07/24/DATADROP-3--web-ui-grammar-of-graphics-visualization-workbench-for-datasets-and-streams/design/01-web-ui-visualization-workbench-intern-implementation-guide.md) — table seam, browser grammar, export, live data, and original implementation plan.
- [`DATADROP-4 PBUI shell guide`](https://github.com/go-go-golems/go-go-datadrop/blob/08f814b685d0c2fa3d968fe7835079a323883971/ttmp/2026/07/24/DATADROP-4--pbui-shell-presentation-based-workbench-and-atomic-design-system-with-storybook/design/01-pbui-shell-analysis-design-and-implementation-guide.md) — presentation interaction model, workspaces, atomic system, and shell decomposition.
- [`DATADROP-6 design-system guide`](https://github.com/go-go-golems/go-go-datadrop/blob/08f814b685d0c2fa3d968fe7835079a323883971/ttmp/2026/07/25/DATADROP-6--design-system-coverage-story-every-primitive-and-split-pbui-and-apps-into-reusable-atoms-molecules-and-organisms/design/01-design-system-coverage-and-decomposition-analysis-design-and-implementation-guide.md) — enforced layer graph, panel extraction, Storybook coverage, and design-system decisions.
- [`DATADROP-6 render-path follow-up`](https://github.com/go-go-golems/go-go-datadrop/blob/08f814b685d0c2fa3d968fe7835079a323883971/ttmp/2026/07/25/DATADROP-6--design-system-coverage-story-every-primitive-and-split-pbui-and-apps-into-reusable-atoms-molecules-and-organisms/design/02-the-render-path-the-row-budget-and-the-nine-applications-still-inline.md) — measured `FieldChip` performance defect and remaining application extraction work.
