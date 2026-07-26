---
title: go-go-datadrop — The Store as an Instance Boundary
aliases:
  - redux store factory no singleton
  - per instance capability injection
  - multi instance embedded application
tags:
  - architecture-garden
  - go-go-datadrop
  - redux
  - dependency-injection
  - embedding
status: active
type: architecture-pattern-study
pattern_maturity: established
created: 2026-07-26
analyzed: 2026-07-26
repository: /home/manuel/code/wesen/go-go-golems/go-go-datadrop
repository_commit: ef996430f8a3a63e6812d961eb2bae5d631272a0
analysis_commit: 69b82257f75a4ca236d985629dc298844128409f
source_tickets:
  - DATADROP-7
related_files:
  - ui/src/store/index.ts
  - ui/src/store/persist.ts
  - ui/src/appkit/usePersistence.ts
  - ui/src/api/fixtureBaseQuery.ts
  - ui/src/components/pages/WorkbenchInstance/WorkbenchInstance.tsx
  - ui/test/instances.test.ts
---

# The Store as an Instance Boundary

**Maturity: Established.**

The cleanest single runtime pattern in the repository, and the one whose failure modes were most thoroughly written down before they were fixed.

## 1. What problem is being solved

The application was a single-page workbench: one Redux store, one set of documents, one tile layout, one persistence key. A requirement arrived to embed **six complete, independent instances of it** into one scrolling tutorial page, each with its own documents, its own layout, and data that arrives without a server.

The naive reading is that this needs a rewrite. It did not. It needed the removal of seven assumptions that only became wrong when there was more than one of the thing.

## 2. The concrete shape

The whole pattern is one exported function and one absence.

```ts
// ui/src/store/index.ts
export function makeStore(options: MakeStoreOptions = {}) {
  const { preloaded, seed = true, fixtures, clipboard } = options;

  const preloadedState = {
    world:  { ...initialWorld, ...preloaded?.world },
    layout: preloaded?.layout ?? defaultSpaces(),
  };

  const store = configureStore({
    reducer: { [api.reducerPath]: api.reducer, world: worldSlice.reducer, layout: layoutSlice.reducer },
    middleware: (getDefault) =>
      getDefault({ thunk: { extraArgument: { fixtures, clipboard } } }).concat(api.middleware),
    preloadedState,
  });

  if (seed && store.getState().world.docOrder.length === 0) {
    store.dispatch(worldSlice.actions.newDoc(null));
  }

  setupListeners(store.dispatch);
  return store;
}
```

**The module exports no constructed store**, and the absence is the pattern. It used to export one, restored from `localStorage` at module load, imported by exactly one file. That was harmless until it was not.

The definition that makes the boundary checkable:

> An **instance** is one store and the React tree beneath its `Provider`. Everything an instance owns is either in that store or in React context below it. Nothing instance-scoped may live in a module-level variable.

Anything reachable without going through the `Provider` is shared, and shared is usually wrong.

## 3. How it is woven into the rest of the application

Three things had to move for the boundary to hold, and each is instructive.

**Application concerns left the shell.** The signed-out gate, a one-time URL parameter read, the session query and the persistence effect were all in the shell component. All four are routing, session or authentication concerns that ended up there because there was only ever one shell. With six instances they become: six identical session requests; six panels forcing themselves to a sign-in screen for a visitor who is anonymous by definition; and six instances racing to consume one URL parameter, of which exactly one wins.

Separating the shell from the application was therefore not a new abstraction. It was the separation those four lines had always implied.

**Persistence became a parameter, defaulting to nothing.**

```ts
export function usePersistence(key: string | null): void {
  …
  useEffect(() => {
    if (key === null) return;              // before the timer, not inside it
    const timer = setTimeout(() => {
      const state = store.getState();      // what is true now, not at schedule time
      save(key, state.world, state.layout);
    }, 500);
    return () => clearTimeout(timer);
  }, [key, world, layout, store]);
}
```

Two details carry weight. The early return happens **before** the timer is created, so a memory-only instance does not merely skip the write — it never schedules anything, and six panels do not run six debounce timers each time the reader touches one. And `null` is the **default**, so an embedded panel that forgets to opt out is inert rather than destructive. The application opts in, in one place, in a file whose job is to know that it is the application.

The failure this prevents is the worst in the list, because it is silent: six instances writing to one key means the reader's real layout is overwritten by whichever tutorial section they last scrolled past, with no error and no symptom until the next reload.

**Capabilities travel on the thunk extra argument.**

Some code cannot take a prop. An RTK Query `baseQuery` is constructed once when the API slice is defined and runs inside middleware; there is no call site above it to thread configuration through. But it must still differ per store — one instance answering from committed fixtures, another going to the network.

```ts
getDefault({ thunk: { extraArgument: { fixtures, clipboard } } })
```

This is the only per-store channel such code can read. `fixtureBaseQuery` wraps the real transport, reads the fixture map off that argument, and answers from memory when one is present. A store built with fixtures **never touches the network at all** — not "prefers not to", never — which is what lets a marketing page render real charts with the API absent, returning 500, or demanding an account.

The same channel later carried a clipboard port, which made an export path testable with no DOM. That reuse is evidence the channel was the right one.

## 4. Why it works

The value is not "you can have two stores". It is that **the wrong thing became unavailable rather than discouraged.**

Deleting the module's store export means `import { store }` fails to compile. A lint rule, a comment or a code-review convention would each have been a request; deletion is a fact. The source states the principle directly:

> Removing the export makes the wrong import *unavailable* rather than merely discouraged, which is the only kind of discouragement that survives contact with a hurry.

Three subtler consequences fell out of the factory and each had been a bug first.

**Both slices are always supplied to `preloadedState`, never conditionally spread.** A preloaded object whose `layout` key is sometimes absent makes `configureStore` infer that the layout reducer must accept `undefined`, and the resulting store type stops matching its own reducer.

**`preloadedState` is supplied even with no preload at all.** Falling through to the slices' own initial state has two problems visible only with more than one store: the layout slice's `initialState: initialLayout()` is evaluated **once**, at module load, so every store built without a preload began life with the same workspace *id*; and the fallback layout was a single empty tile rather than the real default workspaces, so a Storybook story rendering the shell was demonstrating the fallback rather than the product.

**Seeding a document belongs in the factory.** It is a property of *a* store, not of *the* store. As three lines beside a module-level store, every other store — a story's, an embedded panel's — silently got a workbench with nothing in it.

## 5. What goes wrong

**Building the store in a render body.** The correct form is a ref with a null check, not `useState`'s lazy initialiser:

```ts
const storeRef = useRef<AppStore | null>(null);
if (!storeRef.current) storeRef.current = makeStore({ … });
```

Both are available on the first render, but StrictMode double-invokes the initialiser and would construct two stores, discarding one *after* its middleware had already started. An effect is worse still, because the first render must already have a store to hand to `Provider`.

**Reset is remount, and there is no `reset()`.** Give the instance a React `key` and change it; React discards the subtree and the store goes with it. A reset that walks state back can leave a fragment behind, and the fragment is always in the thing nobody thought to walk back.

**The guard is a test, not a convention.** `ui/test/instances.test.ts` asserts that the store module exports no constructed instance, that nothing outside the application entry point imports a store *value*, and that two stores share nothing — a document added to one does not appear in the other, and document ids do not collide.

## 6. When should another project reuse it

Whenever an application might ever need to exist twice on one page: an embedded demo, a tutorial, a side-by-side comparison, a Storybook story of a whole page, a plugin host.

The cost is close to zero if paid at the start and moderate if paid later — in this project it was seven one-line changes plus the shell split, which is small only because a single `grep` established that exactly one file imported the singleton. The census is the part to copy: **before assuming a rewrite, count the actual references.**

The capability-injection half generalises further than the multi-instance half. Any framework that provides a per-instance channel to code that cannot take a prop — a thunk extra argument, a context value, a constructor parameter — should carry injected capabilities there rather than through module imports, because that is what makes the capability substitutable in a test.

## 7. What should become ecosystem guidance

Three candidates, developed in [[Research/Software Architecture Garden/go-go-datadrop/09 - Candidate Ecosystem Guidelines|document 09]]:

1. **Make the wrong thing unavailable, not discouraged.** Deleting an export beats documenting a rule.
2. **Injected capabilities travel on the one per-instance channel the framework already provides.**
3. **A destructive default is a defect even when every current caller overrides it.** Persistence defaults to off precisely so that forgetting is inert.

## Related notes

- [[Research/Software Architecture Garden/go-go-datadrop/01 - Project Architecture Overview]]
- [[Research/Software Architecture Garden/go-go-datadrop/05 - Structural Guard Tests as a Genre]]
- [[Research/Software Architecture Garden/go-go-datadrop/09 - Candidate Ecosystem Guidelines]]
- [[PROJECT REPORT - go-go-datadrop v0.6 - Six Workbenches on One Page, and a Tutorial That Cannot Rot]]
