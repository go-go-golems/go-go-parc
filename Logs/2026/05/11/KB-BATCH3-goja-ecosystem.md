---
title: "KB Playbook Batch 3: goja/JS Runtime Ecosystem (6 Projects)"
doc-type: reference
topics: parc, knowledge-base, goja, js-runtime, batch-analysis
owners: manuel
created: "2026-05-11"
---

# KB Playbook Batch 3: goja/JS Runtime Ecosystem

Analysis of 6 projects from the go-go-goja / JavaScript runtime ecosystem. Follows the updated playbook (with classification edge cases, domain seeds, variation-vs-candidate rules).

## Projects analyzed

1. go-go-goja REPL API (45 KB)
2. go-go-goja Node-like Primitives (27 KB)
3. go-go-goja Plugins (23 KB)
4. Goja vs Sobek Deep Analysis (12 KB)
5. JS Discord Bot Framework (11 KB)
6. go-go-goja jsverbs (10 KB)

---

## Project 1: go-go-goja REPL API

### Step 1: Concept Extraction

| Concept | Category | Role | Tribal? |
|---------|----------|------|---------|
| goja JS runtime embedding | Technology | Core interpreter | Covered by existing [[Tribal/goja-embedding-in-go]] |
| REPL session semantics | Pattern | What counts as a session, what metadata persists, how restore works | Yes — our specific session model |
| IIFE cell rewrite | Pattern | Wrapping cells in async IIFEs for lexical capture + last-expression semantics | Yes — our specific rewrite strategy |
| Profile-based execution (raw/interactive/persistent) | Pattern | Configurable session behavior instead of one-size-fits-all | Yes — our design |
| Replay-based restore | Pattern | Re-executing persisted source into a fresh runtime instead of VM serialization | Yes — our approach |
| Static analysis (AST/CST) for cell planning | Pattern | jsparse + Tree-sitter to compute declarations, unresolved refs, final expression | Yes — our specific analysis pipeline |
| SQLite-backed session persistence | Pattern | Sessions, evaluations, bindings, console events, binding docs in SQLite | Partially — [[Tribal/sqlite-as-application-database]] covers general SQLite usage |
| Console capture for REPL output | Pattern | Structured ConsoleEvent entries instead of stdout printing | Yes — our approach |
| JSDoc sentinels for inline docs | Pattern | No-op helpers (__doc__, __package__) that allow doc markup in REPL source | Yes — our convention |
| Promise handling in evaluation | Pattern | Detecting promise-like results and awaiting them before building cell response | Yes — our specific pattern |
| Runtime owner thread discipline | Pattern | Serializing VM access through a runtime owner; goroutines post closures back | Yes — our concurrency model |

### Step 2: Classification

| Concept | Decision | Reason |
|---------|----------|--------|
| REPL session semantics | Tribal candidate (3/3) → **READY** | Seen in REPL API, Geppetto/Pinocchio sessions, Loupedeck JS REPL. Three projects share the "session = live runtime + execution policy + durable history" model. |
| IIFE cell rewrite | Tribal candidate (2/3) | Seen in REPL API, Goja REPL Hardening. Needs 1 more. |
| Profile-based execution | Variation of existing goja-embedding entry | Per the playbook's edge-case rule: this follows the goja-embedding structure and only differs in the session-policy surface. Add as a variation to [[Tribal/goja-embedding-in-go]]. |
| Replay-based restore | Tribal candidate (1/3) | Only REPL API uses this. |
| Static analysis for cell planning | Tribal candidate (1/3) | Only REPL API. The jsparse + Tree-sitter combo is ours but only used here. |
| Runtime owner thread discipline | Tribal candidate (3/3) → **READY** | Seen in REPL API, Node-like Primitives (async fs), JS Discord Bot. All three share the "goroutines do OS work, post closures back to owner thread" pattern. |
| Console capture / JSDoc sentinels | Tribal candidate (1/3) | Only REPL API. |
| Promise handling in evaluation | Tribal candidate (2/3) | REPL API + Node-like Primitives. |

### Step 3: Entries Ready to Create

**REPL session semantics** (3/3 tribal): The "session = live runtime + policy + history" pattern appears in REPL API (the canonical instance), Geppetto/Pinocchio (chat sessions), and Loupedeck (JS REPL sessions). Core insight: a JavaScript REPL session is not just a live VM — it's a product concept with explicit binding capture, execution policy, and optional durable history. Draft skeleton, needs implementer review.

**Runtime owner thread discipline** (3/3 tribal): The "goroutines do blocking work, post closures back to the VM-owning thread" pattern appears in REPL API, Node-like Primitives (fs async), and JS Discord Bot (dispatch). Core insight: the goja VM is single-threaded; all mutations must go through the owner. This is our concurrency model for goja.

### Key question: Does the goja-embedding tribal entry cover these?

The existing entry documents the generic embedding pattern. Both new tribal entries are extensions of that pattern into specific architectural concerns (session semantics and thread safety). They follow the goja-embedding structure but add structurally different code and gotchas. Per the playbook's edge-case rule, these are new candidates, not variations, because the code structure and failure modes are different.

---

## Project 2: go-go-goja Node-like Primitives

### Step 1: Concept Extraction

| Concept | Category | Role | Tribal? |
|---------|----------|------|---------|
| goja runtime factory composition | Pattern | Building a VM with explicit capability selection via engine.NewBuilder() | Yes — our composition model |
| Data-only vs host-access module split | Pattern | Safe defaults (crypto, path, timer) vs opt-in host modules (fs, os, exec) | Yes — our trust model |
| Module specs and runtime initializers | Pattern | Two distinct composition APIs: require registry vs live VM mutation | Yes — our design |
| Async native module pattern (goroutine → Promise) | Pattern | Blocking OS work in goroutine, Promise settlement on owner thread | Yes — same as "runtime owner thread discipline" |
| fs module (Buffer-aware, async-first) | Technology | Node-like filesystem access from embedded JS | No — Node docs exist, but our async-in-Go implementation is ours |
| Granular module selection | Pattern | DefaultRegistryModule("fs") vs DefaultRegistryModules() | Yes — our API design |
| process global opt-in | Pattern | Module is require-able but global is opt-in | Yes — our specific decision |
| Smoke tests as architecture validation | Pattern | Testing through Owner.Call instead of just Go helpers | Yes — our testing approach |

### Step 2: Classification

| Concept | Decision | Reason |
|---------|----------|--------|
| goja runtime factory composition | Variation of goja-embedding | Follows the same embedding structure, extends it with the builder pattern. Add as variation. |
| Data-only vs host-access module split | Tribal candidate (2/3) | Seen in Node-like Primitives and (implicitly) Capsule Lab (permission-locked API). One more project with explicit module trust policy triggers it. |
| Module specs vs runtime initializers | Tribal candidate (1/3) | Only Node-like Primitives has this split. |
| Async native module pattern | Same as "runtime owner thread discipline" (3/3 above) | Already counted. |
| Granular module selection | Tribal candidate (1/3) | Only Node-like Primitives. |
| process global opt-in | Tribal candidate (1/3) | Only Node-like Primitives. |

### Key observation

This project is a major contributor to the goja-embedding entry's project list and to the "runtime owner thread discipline" tribal candidate. It also adds a new tribal candidate: "data-only vs host-access module split" at 2/3 (with Capsule Lab).

---

## Project 3: go-go-goja Plugins

### Step 1: Concept Extraction

| Concept | Category | Role | Tribal? |
|---------|----------|------|---------|
| HashiCorp go-plugin for JS modules | Pattern | External subprocess providing JS modules via RPC | Yes — our plugin architecture |
| Plugin discovery and manifest validation | Pattern | Discover binaries, request manifest, validate, register in require | Yes — our discovery model |
| Plugin authoring SDK | Pattern | MustModule/Function/Object/Method/Call/Serve DSL | Yes — our SDK design |
| Runtime-scoped module registrars | Pattern | Per-runtime module registration and cleanup hooks | Yes — our lifecycle model |
| Runtime-scoped docs hub | Pattern | docaccess.Hub with providers (Glazed, jsdoc, plugin manifest) | Yes — our docs architecture |
| Result normalization before structpb encoding | Pattern | Rewriting Go values into structpb-friendly shapes | Yes — our workaround |
| Docs-aware REPL autocomplete | Pattern | Plugin docs feeding completion candidates and help drawers | Yes — our integration |

### Step 2: Classification

| Concept | Decision | Reason |
|---------|----------|--------|
| HashiCorp go-plugin for JS modules | Tribal candidate (1/3) | Only go-go-goja Plugins. Significant architectural investment but single instance. |
| Plugin discovery + manifest validation | Tribal candidate (1/3) | Only go-go-goja Plugins. |
| Plugin authoring SDK | Tribal candidate (1/3) | Only go-go-goja Plugins. |
| Runtime-scoped module registrars | Tribal candidate (2/3) | Seen in Plugins and Node-like Primitives (factory.NewRuntime). |
| Runtime-scoped docs hub | Tribal candidate (1/3) | Only go-go-goja Plugins. |
| Docs-aware REPL autocomplete | Tribal candidate (1/3) | Only go-go-goja Plugins (js-repl). |
| Result normalization before structpb | Tribal candidate (1/3) | Only go-go-goja Plugins. |

### Key observation

This project introduces many tribal candidates but all at 1/3. The HashiCorp plugin architecture is a significant investment — but it only has one implementation. If a second project adopted the same plugin pattern (e.g., a plugin system for a different Go JS host), several of these would move to 2/3 quickly.

---

## Project 4: Goja vs Sobek Deep Analysis

### Step 1: Concept Extraction

| Concept | Category | Role | Tribal? |
|---------|----------|------|---------|
| ES Modules (ESM) support in Go JS engines | Technology | import/export, dynamic imports, top-level await | No — spec is public |
| Goja vs Sobek fork tracking | Pattern | Sobek tracks Goja with near-zero lag, adds only ESM | Yes — our specific finding about this ecosystem |
| ESM architectural cost | Pattern | +4.6% code size, +5 files, significant conceptual overhead | Yes — our analysis |
| When to choose Sobek over Goja | Pattern | Only when you need ESM or k6 integration | Yes — our decision framework |

### Step 2: Classification

| Concept | Decision | Reason |
|---------|----------|--------|
| ESM support in Go JS engines | On-Ramp candidate (1/5) 🌐 Domain seed | Lookupable (ECMAScript spec), but our angle (Go engine integration, migration cost) is missing from public docs. Opens a new domain. |
| Goja vs Sobek decision framework | Tribal candidate (1/3) | Our specific analysis. Only one analysis exists. |

### Key observation

This project opens a potential "Go JS engine selection" on-ramp domain. The decision between Goja and Sobek is a question that many Go projects will face. But with only 1 project touching this, it's firmly at 1/5 with a domain seed flag.

---

## Project 5: JS Discord Bot Framework

### Step 1: Concept Extraction

| Concept | Category | Role | Tribal? |
|---------|----------|------|---------|
| goja-based Discord bot host | Pattern | Go process runs JS bot scripts via goja with require("discord") | Yes — our framework design |
| defineBot DSL | Pattern | Clean JS API for command/component/modal/event registration | Yes — our DSL |
| Single-bot per process | Pattern | One Discord session per process, no multi-bot composition | Yes — our architectural decision |
| Two-stage Glazed parsing for runtime config | Pattern | Pre-parse static flags, then dynamically build Glazed schema from bot metadata | Yes — our pattern |
| Runtime owner thread discipline | Pattern | Same as identified above — goroutines post closures back to VM owner | Already counted (3/3) |
| Discord interaction dispatch | Technology | Routing slash commands, components, modals, events to JS handlers | No — Discord API is documented |
| UI DSL for Discord | Pattern | message()/embed()/button()/select()/form()/card()/confirm() builders | Yes — our UI DSL |

### Step 2: Classification

| Concept | Decision | Reason |
|---------|----------|--------|
| goja-based Discord bot host | Tribal candidate (1/3) | Only JS Discord Bot Framework. |
| defineBot DSL | Tribal candidate (1/3) | Only JS Discord Bot Framework. |
| Single-bot per process | Tribal candidate (1/3) | Only JS Discord Bot Framework. |
| Two-stage Glazed parsing for runtime config | Tribal candidate (2/3) | Seen in JS Discord Bot and (potentially) other Glazed apps with dynamic schemas. |
| UI DSL for Discord | Tribal candidate (1/3) | Only JS Discord Bot. |

### Key observation

This project contributes to the "runtime owner thread discipline" candidate (now at 3/3 from REPL API + Node-like Primitives + JS Discord Bot). It also contributes "two-stage Glazed parsing" at 2/3.

---

## Project 6: go-go-goja jsverbs

### Step 1: Concept Extraction

| Concept | Category | Role | Tribal? |
|---------|----------|------|---------|
| JS-defined Glazed commands | Pattern | .js files scanned as command definitions, exposed as Glazed verbs | Yes — our pattern |
| Static metadata extraction via AST | Pattern | Parsing literal AST nodes for command metadata, not runtime evaluation | Yes — our approach |
| Source overlay runtime | Pattern | In-memory loader preserving relative require() for scanned scripts | Yes — our design |
| Shared binding plan | Pattern | One contract between schema generation and runtime invocation | Yes — our pattern |
| Multi-source scanning (dir, fs.FS, in-memory) | Pattern | ScanDir/ScanFS/ScanSource/ScanSources | Yes — our API |

### Step 2: Classification

| Concept | Decision | Reason |
|---------|----------|--------|
| JS-defined Glazed commands | Tribal candidate (2/3) | Seen in jsverbs and (potentially) the Glazed help system. The ZK Tool's `zk obsidian run-script` is a different pattern. |
| Static metadata extraction via AST | Tribal candidate (1/3) | Only jsverbs. |
| Source overlay runtime | Tribal candidate (1/3) | Only jsverbs. |
| Shared binding plan | Tribal candidate (1/3) | Only jsverbs. |
| Multi-source scanning | Tribal candidate (1/3) | Only jsverbs. |

### Key observation

jsverbs connects two KB domains: the goja ecosystem (how JS runs) and the Glazed ecosystem (how commands are structured). The "JS-defined Glazed commands" candidate is interesting because it bridges both.

---

## Updated Candidate Tracking

### Tribal candidates at 3/3 → READY

| Concept | Seen in | Status |
|---------|---------|--------|
| **REPL session semantics** | REPL API, Geppetto/Pinocchio, Loupedeck JS REPL | 3/3 → **READY**: session = live runtime + policy + durable history |
| **Runtime owner thread discipline** | REPL API, Node-like Primitives (fs async), JS Discord Bot | 3/3 → **READY**: goroutines do OS work, post closures back to VM-owning thread |

### Tribal candidates updated (from this batch)

| Concept | Seen in | Status |
|---------|---------|--------|
| IIFE cell rewrite | REPL API, Goja REPL Hardening | 2/3 |
| Data-only vs host-access module split | Node-like Primitives, Capsule Lab | 2/3 |
| Runtime-scoped module registrars | Plugins, Node-like Primitives | 2/3 |
| Two-stage Glazed parsing for runtime config | JS Discord Bot, (other Glazed apps?) | 2/3 |
| JS-defined Glazed commands | jsverbs, (Glazed help?) | 2/3 |
| HashiCorp go-plugin for JS modules | Plugins | 1/3 |
| Plugin authoring SDK | Plugins | 1/3 |
| Replay-based restore | REPL API | 1/3 |
| Static analysis for cell planning | REPL API | 1/3 |
| Console capture / JSDoc sentinels | REPL API | 1/3 |
| Promise handling in evaluation | REPL API, Node-like Primitives | 2/3 |
| Granular module selection | Node-like Primitives | 1/3 |
| process global opt-in | Node-like Primitives | 1/3 |
| Module specs vs runtime initializers | Node-like Primitives | 1/3 |
| Plugin discovery + manifest validation | Plugins | 1/3 |
| Runtime-scoped docs hub | Plugins | 1/3 |
| Docs-aware REPL autocomplete | Plugins | 1/3 |
| Result normalization before structpb | Plugins | 1/3 |
| Goja vs Sobek decision framework | Goja vs Sobek | 1/3 |
| goja-based Discord bot host | JS Discord Bot | 1/3 |
| defineBot DSL | JS Discord Bot | 1/3 |
| Single-bot per process | JS Discord Bot | 1/3 |
| UI DSL for Discord | JS Discord Bot | 1/3 |
| Static metadata extraction via AST | jsverbs | 1/3 |
| Source overlay runtime | jsverbs | 1/3 |
| Shared binding plan | jsverbs | 1/3 |
| Multi-source scanning | jsverbs | 1/3 |

### On-Ramp candidates updated

| Concept | Seen in | Status |
|---------|---------|--------|
| ESM support in Go JS engines | Goja vs Sobek | 1/5 🌐 Domain seed |

---

## Playbook feedback (Batch 3)

1. **The variation-vs-candidate rule worked.** Profile-based execution in the REPL API clearly follows the goja-embedding structure. I classified it as a variation, not a new candidate. This saved me from inflating the candidate list.

2. **The "count projects that share core insight" rule worked.** "Runtime owner thread discipline" appeared in three projects with different surface APIs (REPL eval, async fs, Discord dispatch) but the same core pattern. Counting it as one tribal entry at 3/3 feels right.

3. **Domain seed flag is useful.** Goja vs Sobek opens an "ESM in Go engines" question that doesn't fit any existing KB section. The 🌐 flag signals "this needs a judgment call" without prematurely creating an entry.

4. **Batching by domain is efficient.** Reading 6 goja projects in sequence built cumulative context. Each project reinforced concepts from the previous ones, making classification faster. The goja-embedding entry now has 8+ projects feeding it.

5. **Large projects (45 KB) take disproportionate time.** The REPL API report alone took as long as the other 5 combined. For future batches, I'd recommend capping at 25 KB or giving a time budget per project.
