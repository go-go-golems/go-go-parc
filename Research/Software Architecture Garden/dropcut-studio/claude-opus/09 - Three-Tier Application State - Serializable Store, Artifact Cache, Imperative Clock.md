---
title: Three-Tier Application State — Serializable Store, Artifact Cache, Imperative Clock
aliases:
  - Redux holds ids, a cache holds artifacts
  - Identity-keyed artifact cache with live-set GC
  - Versioned project document with a migration seam
  - Load generation counter for externally owned editors
status: established
type: architecture-garden-design
created: 2026-10-25
analyzed: 2026-10-25
analysis_author: claude-opus-5-5
repository: /home/manuel/code/wesen/dropcut-studio
repository_remote: git@github.com:wesen/dropcut-studio.git
repository_commit: f3ebac2d5291b4a371bde25ae3a44d6f752cff41
tags:
  - architecture-garden
  - dropcut-studio
  - react
  - redux
  - state-management
  - persistence
  - file-formats
related_files:
  - apps/studio/src/state/store.ts
  - apps/studio/src/state/slices.ts
  - apps/studio/src/state/artifactCache.ts
  - apps/studio/src/state/compileThunk.ts
  - apps/studio/src/state/projectFile.ts
  - apps/studio/src/state/projectStore.ts
  - apps/studio/src/ui/viewportHandle.ts
  - apps/studio/src/ui/Editor.tsx
  - packages/viewer-three/src/playback.ts
  - packages/ir/src/program.ts
related_notes:
  - "[[Research/Software Architecture Garden/upwork-tracker/06 - Keyboard First Workspace and URL State]]"
  - "[[Research/Software Architecture Garden/upwork-tracker/08 - Source State Separation XDG and WAL Safe Backup]]"
---

# Three-Tier Application State — Serializable Store, Artifact Cache, Imperative Clock

A CAM application's state spans six orders of magnitude in size and four in update rate. The script is a few kilobytes and changes on keystrokes; the toolpath buffers are tens of megabytes and change per compile; the playback clock changes sixty times a second. Putting all of it in one Redux store breaks serialisability checks, makes DevTools unusable and forces a choice between correctness middleware and performance. This chapter describes how the studio app assigns each kind of state to a tier with its own rules, and how the saved project document is kept separate from all three.

> [!summary]
> - **Tier 1, Redux:** small, serialisable, undoable-in-principle state. `serializableCheck` and `immutableCheck` stay **on** as the enforcement mechanism.
> - **Tier 2, artifact cache:** large compile outputs in a module-level `Map`, keyed by a monotonic id. Redux stores only the id; a live-set GC drops the rest.
> - **Tier 3, imperative handle:** the viewport's 60 Hz clock and `play/seek` calls, reached through one module-level handle. Redux receives a throttled `tick`.
> - Render data uses a separate **transport representation** of flat typed arrays.
> - The saved **project document is not the store state**. It carries a format version from v1, a migration seam that exists before it is needed, and type checks that run *before* defaults are applied.
> - Two small state techniques are worth copying: dirty tracking by snapshot comparison, and a **load generation counter** for an editor that owns its own document.

## 1. Why one store is the wrong shape

Redux's development middleware checks that every action and state value is serialisable and that state is never mutated. Those checks are what keep a store honest. A compiled program violates both: it contains `Float32Array`s of millions of points, a `Map` of tools, branded values, and — once rendered — Three.js objects with cycles. The usual reaction is to disable the checks "to make the warning go away". `store.ts` states the consequence of that reaction directly: *disabling them … is exactly how a store ends up holding a 24 MB typed array.*

The alternative is to assign state by its properties.

| Tier | Holds | Size | Update rate | Rules |
|---|---|---|---|---|
| 1. Redux | script, machine id, settings, diagnostics, certificate rows, stats, playback time, UI selection | KB | keystrokes, compiles, throttled ticks | serialisable, immutable, checked in dev |
| 2. Artifact cache | `ValidatedProgram`, `GCodeDocument`, `RenderBuffers`, mesh, stock box | MB | once per compile | immutable after insert, keyed by id, GC to live set |
| 3. Imperative handle | Three.js scene, animation clock, `play/seek/pause` | — | 60 Hz | one owner, explicit subscription, never in Redux |

## 2. Tier 2: the artifact cache

`apps/studio/src/state/artifactCache.ts` is about forty lines of code:

```ts
const store = new Map<ArtifactId, CompileArtifact>();
let sequence = 0;

export function putArtifact(artifact: CompileArtifact): ArtifactId {
  const id = `artifact:${++sequence}`;
  store.set(id, artifact);
  return id;
}

export function collectGarbage(live: ReadonlySet<ArtifactId>): number {
  let removed = 0;
  for (const id of store.keys()) if (!live.has(id)) { store.delete(id); removed++; }
  return removed;
}
```

Three decisions in it carry the design.

**The id is a counter, not a content hash.** Hashing megabytes of floats on every compile costs more than it saves. The id only has to answer *is this the artifact I already rendered?*, and a monotonic counter answers that exactly: a new compile is a new id even if its output is byte-identical, which is the right behaviour for a viewer that should reset playback on recompile.

**The store holds the id, and components re-read on id change.** Redux's `compileSucceeded` payload contains `artifactId` plus small summaries: line and motion counts, cut and rapid lengths, time and its model, certificate rows, the error budget total. A viewport component selects `artifactId`, calls `getArtifact(id)` when it changes, and does nothing when unrelated state changes.

**Garbage collection is relative to a live set.** After each compile the thunk calls `collectGarbage(new Set([artifactId]))`. Without it, *every keystroke-triggered recompile leaks a toolpath buffer.* The live set is currently one id; the function's signature already supports keeping several, which a future compare-two-compiles view would need.

Before handing the certificate to Redux, the thunk flattens it into rows (`certificateRows`) of `{ label, status, detail }` strings. The comment explains the choice: the branded `Mm` values are numbers at runtime, but *keeping the store's shape flat and obvious is worth more than reusing the type.*

## 3. A transport representation for render data

`Path` objects with `Point3` members are the right representation for authoring and checking toolpaths. They are the wrong representation for a renderer or a `postMessage` to a worker. `packages/ir/src/program.ts` defines a separate artifact:

```ts
export interface RenderBuffers {
  readonly positions: Float32Array;   // xyz-interleaved, length 3·count
  readonly kinds: Uint8Array;         // MoveKind per point
  readonly times: Float64Array;       // cumulative seconds at each point
  readonly gcodeLines: Int32Array;    // emitted line for each point, or −1
  readonly count: number;
  readonly totalSeconds: number;
  readonly minZ: number;
  readonly maxZ: number;
}
```

Typed arrays are transferable, so a worker can post them with zero copy; the trail can be drawn by advancing one draw-range integer; and `gcodeLines` makes click-to-seek and play-time line highlighting a lookup.

Playback position is a binary search over `times`. The module comment notes that *all three prototypes independently implemented a binary search over cumulative motion times, each slightly differently.* `sampleAt` in `packages/viewer-three/src/playback.ts` is that function written once, with the edge cases tested in `playback.test.ts`: time before the first motion, after the last, zero-duration motions (division by zero becomes "fully complete"), and an empty program.

## 4. Tier 3: the imperative clock

The transport bar has to call `play()`, `seek()` and `setSpeed()` on the live viewport. Routing those through Redux would put a 60 Hz clock into the store. `apps/studio/src/ui/viewportHandle.ts` is a module-level handle with a subscription:

```ts
let current: ViewportApi | null = null;
export function setViewport(api: ViewportApi | null): void { current = api; for (const l of listeners) l(api); }
export const getViewport = (): ViewportApi | null => current;
export function onViewportChange(cb: (api: ViewportApi | null) => void): () => void { ... }
```

Its comment defends the singleton precisely: *a singleton is honest about there being one viewport, and keeps the imperative escape hatch in one visible place rather than threading refs through the component tree.* The viewport dispatches a **throttled** `tick({ time, duration, playing, gcodeLine })` to Redux so the G-code panel can highlight the active line; the reducer's comment says *dispatched by the viewport's throttled tick, NOT per animation frame.*

The viewer package itself (`packages/viewer-three`) is framework-free Three.js. React mounts it and registers its API; nothing in the viewer imports React.

## 5. The project document is not the store

`apps/studio/src/state/projectFile.ts` opens with the premise that drives it: *a saved project outlives the code that wrote it.* Four rules follow.

### 5.1 The document and the store are different types

`ProjectDocument` carries `formatVersion`, a generated `id`, `name`, `createdAt`, `modifiedAt`, and the settings. `ProjectState` in Redux carries the settings plus transient fields — `documentId`, `savedSettings`, `diskFileName`, `saving`, `lastError`, `loadGeneration`. The two share a `ProjectSettings` subset with explicit converters (`settingsOf`, `documentFor`). The comment gives the reason: *keeping them separate means a store refactor does not silently change the file format.*

### 5.2 The migration seam exists from version 1

```ts
export const PROJECT_FORMAT_VERSION = 1;
```

`parseDocument` refuses files newer than the build (`file format version 2 is newer than this build understands (1) — update the application`), then calls `migrate(o, version)`. With one version, `migrate` is nearly a no-op. *That is the point: the seam exists before it is needed, so version 2 is a case in a switch rather than an archaeology exercise.* Version-less files (`version 0`) are accepted only if they carry a `script` string.

### 5.3 Reject wrong types before filling in absent fields

This is the subtle rule, and the most broadly useful one in the module:

```ts
// Reject WRONG-TYPED fields before migrating. Migration fills in fields that
// are ABSENT, which is the right response to an older format; applying the
// same defaults to a field that is present but malformed would silently
// discard the user's data — opening the file would show an empty script.
const wrongType = checkFieldTypes(o);
if (wrongType) return { ok: false, error: wrongType };
return migrate(o, version);
```

The distinction is between *absent* and *malformed*. An absent field means the file predates the field, and a default is the correct reading. A present field of the wrong type means corruption or a hand-edit error, and a default would replace the user's data with nothing and then let them save over the original. `projectFile.test.ts` pins both behaviours.

### 5.4 The file is meant to live in version control

`serialise` writes two-space-indented JSON with a trailing newline *so a saved file diffs cleanly in git.* Ids are generated (`crypto.randomUUID()`), not derived from the name, so renaming does not orphan a project and two projects may share a name. `projectStore.ts` offers three storage routes and explains each: IndexedDB as the default library (structured clones, no practical size limit, ready for binary meshes); the File System Access API for real files the user can commit next to the part they cut; download and upload everywhere else. It also records a rejected option, the Origin Private File System, with the reason: OPFS is origin-private and invisible to the user, so it gives nothing IndexedDB does not.

## 6. Two small techniques

**Dirty tracking compares against a snapshot.** `ProjectState.savedSettings` holds the settings as last saved; `isDirty` compares current settings with it via `settingsEqual`. A boolean `dirty` flag would stay true after the user types a character and deletes it again. Comparison reports clean, which is correct.

**A load generation counter for an editor that owns its document.** CodeMirror owns its own document and undo history. The editor cannot simply re-render from the store, because it must distinguish "the user typed and the store is echoing it back" from "something replaced the whole program". Comparing text cannot make that distinction: loading a document whose text equals the current text would look like a no-op, and reopening the same document should still reset undo history. `ProjectState.loadGeneration` is incremented by every external replacement (open, new, import), and the editor resets its state when the counter changes:

```ts
useEffect(() => {
  if (loadGeneration === 0) return;          // nothing loaded yet; mount handled it
  view.setState(makeState(scriptRef.current, dispatch));
}, [loadGeneration, dispatch]);
```

`store.test.ts` asserts that typing does not bump the counter, that opening a document does, and that starting a new project bumps it even when the resulting text is identical. The test comment records that the counter was added to fix a real bug, *the editor silently keeps showing the previous project*, and commit `cc4db3b` (":bug: Editor did not update when switching projects") is that fix.

## 7. Where the implementation is ahead of, or behind, its comments

- **The in-flight abandonment is vacuous today.** The auto-compile middleware debounces for 600 ms and calls `inFlight?.abort()` before dispatching a new compile, with the comment *an in-flight compile is abandoned rather than awaited — its result would be stale.* But the compile thunk contains no `await` and never reads its abort signal: the whole pipeline runs synchronously on the main thread before `dispatch` returns. By the time `abort()` is called the previous compile has already finished and dispatched. Nothing is stale yet. When compilation moves to a worker, the thunk will need a real fence — for example, a compile generation recorded in `compileStarted` and checked in `compileSucceeded` — or an older compile that finishes late will overwrite a newer one.
- **GC is called from the thunk, not middleware.** The cache comment says *called from middleware after each compile*; the call is in `compileThunk.ts`. Behaviour is the same; the comment is stale.
- **The thunk duplicates the CLI pipeline.** Its header says it runs *the same pipeline the CLI runs — literally the same function*. It does not call `compileScript`; it re-implements the eight steps. See [[Research/Software Architecture Garden/dropcut-studio/claude-opus/10 - Architecture Debt and Patterns Not to Repeat|chapter 10]].

## 8. Applicability

The three-tier split fits any front end that renders large computed artifacts: data-visualisation tools, map editors, audio and video editors, IDEs with build outputs, notebook UIs. The test for tier 2 is simple: if a value is large, derived, and replaced wholesale, it belongs in an id-keyed cache rather than in the store. The test for tier 3 is update rate: anything per-frame belongs to its owner, with throttled summaries in the store.

The document rules fit any application file format: version from the start, migrate absent fields, reject malformed ones, refuse newer versions with a message, and keep the document type independent of in-memory state.

## 9. Candidate ecosystem guidance

1. Keep serialisability and immutability checks on in development; treat them as the enforcement of the tier rule.
2. Put large derived artifacts in an id-keyed cache, store only the id, and garbage-collect to a live set after each replacement.
3. Use monotonic ids when identity means "same production", and content hashes only when it means "same bytes".
4. Give per-frame state one imperative owner and publish throttled summaries.
5. Define a transport representation of flat typed arrays for anything that crosses a worker boundary or feeds a renderer.
6. Version saved documents from the first release and ship a migration function that already exists.
7. Reject present-but-malformed fields before defaulting absent ones.
8. Use snapshot comparison for dirty state and generation counters for "externally replaced".
9. When computation becomes asynchronous, fence results by generation; an abort call that nothing observes is not a fence.

## 10. Evidence and references

- `apps/studio/src/state/store.ts` — checks on; `autoCompile` middleware, 600 ms debounce, `inFlight.abort()`.
- `apps/studio/src/state/artifactCache.ts:49`, `:65` — `putArtifact`, `collectGarbage`.
- `apps/studio/src/state/compileThunk.ts:56`, `:193` — pipeline re-implementation, artifact split, `certificateRows`.
- `apps/studio/src/ui/viewportHandle.ts` — imperative handle.
- `apps/studio/src/state/slices.ts` — `loadGeneration`, `savedSettings`, `isDirty`, throttled `tick`.
- `apps/studio/src/ui/Editor.tsx` — generation-guarded editor reset.
- `apps/studio/src/state/projectFile.ts:21`, `:122`, `:156`, `:177` — version, `parseDocument`, `checkFieldTypes`, `migrate`.
- `apps/studio/src/state/projectStore.ts` — IndexedDB, File System Access, download/upload; OPFS rationale.
- `packages/ir/src/program.ts` — `RenderBuffers`; `packages/viewer-three/src/playback.ts` — `buildRenderBuffers`, `sampleAt`.
- Tests: `projectFile.test.ts`, `store.test.ts`, `playback.test.ts`.
