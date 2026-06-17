---
title: RAG_SITE_SRC Guarded Vite Aliases
created: 2026-06-16
tags:
  - til
  - vite
  - frontend
  - pnpm
  - react
---

# TIL - RAG_SITE_SRC Guarded Vite Aliases

A `RAG_SITE_SRC`-guarded Vite alias is an opt-in local development switch: normally the app imports a package from `node_modules`, but when `RAG_SITE_SRC` is set, Vite rewrites selected package imports to the editable source checkout.

This is useful when a package's public `exports` point at built files, but I want Vite HMR against source CSS/TSX.

Example startup:

```bash
RAG_SITE_SRC=../../../2026-05-27--rag-evaluation-system/packages/rag-evaluation-site pnpm dev
```

Then `vite.config.ts` can do:

```ts
const ragSiteRoot = process.env.RAG_SITE_SRC;

resolve: {
  alias: ragSiteRoot
    ? [
        {
          find: "@go-go-golems/rag-evaluation-site/app",
          replacement: path.join(ragSiteRoot, "src/app/index.ts"),
        },
        {
          find: "@go-go-golems/rag-evaluation-site/styles.css",
          replacement: path.join(ragSiteRoot, "src/styles.css"),
        },
        {
          find: "@go-go-golems/rag-evaluation-site/theme.css",
          replacement: path.join(ragSiteRoot, "src/theme.css"),
        },
        {
          find: "@go-go-golems/rag-evaluation-site",
          replacement: path.join(ragSiteRoot, "src/index.ts"),
        },
      ]
    : [],
  dedupe: ["react", "react-dom"],
}
```

The key idea is that pnpm workspace links and package aliases are not the same thing. A workspace link may point at the local package root, but the package root still obeys the package's `exports`, which may reference built artifacts. Vite aliases can deliberately map public import names to source files during development.

"Guarded" means the rewrite only happens when the environment variable is present. Production builds, CI builds, and normal installs can keep using the published package shape.

In the ClubMed minitrace-viz case, this lets the Goja/xgoja backend keep serving Widget IR JSON on one port while Vite serves the React frontend on another port and hot-reloads CSS from the local `@go-go-golems/rag-evaluation-site` source tree.
