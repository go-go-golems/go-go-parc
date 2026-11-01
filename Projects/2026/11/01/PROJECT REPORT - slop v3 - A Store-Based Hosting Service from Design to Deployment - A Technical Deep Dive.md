---
title: "slop v3: A Store-Based Hosting Service from Design to Deployment — A Technical Deep Dive"
aliases:
  - slop v3 Deep Dive
  - slop v3 core project report
  - SLOP3-001 report
tags:
  - project
  - slop
  - go
  - sqlite
  - goja
  - hosting
  - architecture
status: active
type: project
created: 2026-11-01
repo: /home/manuel/code/wesen/2026-10-31--slop-v3
---

# slop v3: A Store-Based Hosting Service from Design to Deployment — A Technical Deep Dive

**slop v3** is a single Go binary, `slop`, that is both a web server and the command-line tool that controls it. The server hosts small web applications written in HTML and JavaScript, optionally with server-side JavaScript, for visitors who may or may not be signed in. The command-line tool lets a person, or a coding agent acting with that person's token, create those applications, push their files, set who may use them and publish them at URLs. Every application runs against a **store**: one SQLite file that holds the application's documents, its files, its own SQL tables and a numbered log of every change.

This report explains how the system works and how it was built. It was written from the repository, the implementation diary and the verification runs of 1 November 2026, when the nine implementation phases (P0 to P8) were completed in one working session. It is organised in dependency order. Section 2 states the problem. Sections 3 to 5 define the data model and the single list of operations that every client uses. Sections 6 to 10 explain serving, server-side code, access control, subscriptions and model access. Section 11 covers the back office. Sections 12 and 13 describe the deployment of existing sites and applications from their source folders, and a coding agent building and changing applications on the system. The last sections cover verification, the course of the work, and the limits of the design.

> [!summary]
> - **Five nouns.** Everything is a store, an app, a mount, a person or a grant. A store is a SQLite file; an app is a store whose files include `app.json`; a mount gives a store a URL; a grant gives a person or an audience a level on a store. One function, `Can`, decides every access question and returns a trace of how it decided.
> - **One list of operations.** 76 verbs, each a Go struct with a name, arguments, a required token scope and a function. The CLI, the HTTP API at `/api/v1/<verb>` and the `slop eval` JavaScript scope are all generated from that table, so an agent and the back office call exactly the same code.
> - **Turns are transactions.** A store's server code, `actor.js`, runs in a goja runtime owned by one goroutine. Each event it handles is one SQLite transaction; an `await` on real I/O ends the transaction, and the code after the `await` runs in a new one. Reactors follow the store's log from a cursor and run exactly once per commit.
> - **Deployed from source, used by an agent.** The public site slop.boutique, seven applications from the francois project, Claude Blocks and Pinup were built from their source folders and pushed with the CLI. Browser checks pass for guests, members and an admin, and model calls go to a real model through the Pi worker. A Pi coding agent built a poll app and added tags to a journal through the same CLI. It also showed that a development-mode sign-in lets an agent become an admin.

## 1. What exists, and where

| Item | Location |
|---|---|
| Repository (module `github.com/go-go-golems/slop`) | `/home/manuel/code/wesen/2026-10-31--slop-v3` |
| Ticket workspace | `ttmp/2026/11/01/SLOP3-001--slop-v3-core-a-streamlined-store-based-hosting-service-design-and-implementation-guide/` |
| Design and implementation guide (2,770 lines) | `design-doc/01-slop-v3-core-design-and-implementation-guide-for-interns.md` |
| Implementation diary (one step per phase) | `reference/01-diary.md` |
| Build, deploy and browser-check scripts | `scripts/01-…` to `scripts/10-…` |
| Screenshots of the checks | `various/p7-backoffice/`, `various/p8-deploy/` |
| The coding agent's brief, apps, reports and tool calls | `various/p8-agent/` |
| Predecessor in production | slop-computer v2, `/home/manuel/workspaces/2026-10-28/slop-computer/slop-computer` |
| Source of the subscription code | francois, `/home/manuel/code/wesen/go-go-golems/francois` |

The code is about 17,800 non-blank lines of Go in seventeen packages, plus three JavaScript and TypeScript builds: the page runtime that implements `claude.use`, the React back office, and the worker for model calls. The main direct Go dependencies are goja (the JavaScript runtime), mattn/go-sqlite3, zitadel/oidc (sign-in), stripe-go (payments), robfig/cron (alarm schedules), cobra (the CLI) and yaml.v3.

| Package | Non-blank lines | Responsibility |
|---|---:|---|
| `server` | 3,929 | hosts, mounts, static and live serving, views, sign-in, billing and sample endpoints |
| `verbs` | 2,641 | the verb table |
| `system` | 2,293 | `system.db`: people, tokens, grants, mounts, policy, LLM ledger, Stripe state |
| `actor` | 2,221 | goja actors, turns, reactors, alarms, the modules actors `use()` |
| `store` | 1,395 | `store.db`: documents, files, snapshots, the log, the SQL authorizer |
| `rt` | 1,164 | the page runtime contract: manifests, rules, views, rooms |
| `billing` | 859 | the subscription policy and the Stripe gateway, from francois |
| `kernel` | 470 | running versions of apps, standing access, guest cleanup |
| others | 1,943 | access check, CLI client, config, identity (OIDC), LLM client, blobs, ids |

## 2. The problem

slop-computer v2 hosts artifacts: pages, data sets and design files, each with numbered versions, bound into routes on sites, and edited in a Workshop where comments on a version become prompts for an agent. It runs in production, and it has accumulated many concepts: artifacts, versions, kinds, viewers, routes, bindings, threads, projects. Each concept has its own tables, verbs and UI. v3 was designed to keep the central idea of a separate design document from 31 October (one SQLite file per unit of state, with its code running next to it) and to discard the rest of v2's vocabulary.

The requirements in the guide (§2.1) reduce to five:

1. A coding agent must be able to do everything a person can, through the same operations, with a token that acts as its person.
2. Visitors who are not signed in must be able to use applications, including writing to them, when the owner allows it.
3. An admin decides who may open which store, what each application may do for each kind of visitor, and who may call the model with how many tokens per month.
4. Subscriptions work as they do in francois: a person with a paid subscription or a complimentary grant gets more.
5. Applications written for the claude.ai artifact contract (`claude.use("db")` and so on) run unchanged.

The fifth requirement matters more than it appears. Claude Blocks and Pinup were written as claude.ai artifacts; the francois examples were written against the same contract. A host that implements the contract can run them without edits, and section 12 shows that it does.

## 3. Five nouns and one check

The data model is introduced here in the order in which its terms depend on each other.

A **store** is the unit of state. It is a directory `stores/<id>/` containing one SQLite file, `store.db`, which holds JSON **documents** at paths such as `entries/e1`, **files** at paths such as `index.html`, the application's own SQL tables, and a **log** of numbered commits. File contents are kept once, by SHA-256, in a shared blob directory, so two stores holding the same file hold it once on disk.

An **app** is a store whose files include `app.json`. That file names the HTML entry page, the optional server code (`actor.js`), the store type the app runs on, and the **capabilities** its pages use, in the shape of the claude.ai artifact contract. A store either runs its own files as an app, or names another store as its app and holds only data. The second form is how one Claude Blocks app serves many workspaces: each workspace is a data store of type `blocks` that runs the app store `blocks`.

A **mount** is a host and a path pattern pointing at a store: `boutique.localhost:18300 /` points at the store `boutique`. A pattern may contain a parameter that names the store, as in `/b/:id`, so one mount serves every store of one type.

A **person** is a signed-in **user** (`usr_…`) or a **guest**. A guest who needs an identity, to write or to keep private documents, gets a `vis_…` id remembered by a cookie. A person's **audience** is computed on every request from their role and subscription: `guest`, `member`, `subscriber` or `admin`. It is never stored.

A **grant** gives a **level** on one store to a subject: a person, or an audience written `@guest`, `@member` or `@subscriber`. The levels are ordered: `view` < `interact` < `admin` < `owner`.

```mermaid
graph LR
  P[person<br/>usr_… / vis_…] -->|has| A[audience<br/>computed]
  G[grant] -->|level on| S[store<br/>store.db]
  G -->|subject| P
  G -->|subject| A
  S -->|runs| APP[app store<br/>app.json, actor.js]
  M[mount<br/>host + path] -->|points at| S
  style S fill:#e8eefc
  style APP fill:#e8eefc
```

Every access question goes through one function, `Checker.Can(ctx, principal, store, need, what, hidden)` in `pkg/access/check.go`. It computes the principal's level on the store and compares it with the level the operation needs. The level is computed in four steps:

1. The owner of the store holds `owner`; an admin holds `admin` on every store.
2. Otherwise, every grant whose subject matches the principal contributes its level, and the highest wins. `@member` matches anyone whose audience is at least `member`, so a subscriber matches it too.
3. The result is capped by the audience: a guest holds at most `interact`, a member or subscriber at most `admin`. `owner` comes only from creating the store.
4. A token is capped by its scopes: a `read` token acts at most at `view`.

Each step appends a line to a trace. The verb `explain.can` returns that trace, and the back office shows it, so an admin never has to guess why someone was refused. For a member reading a store that grants `@member interact`, and for a guest asked to write to a store that grants `@guest view`, the traces read:

```text
audience member (usr_7c…)
grant @member interact on notes (direct)
reading needs view

audience guest (vis_41…)
grant @guest view on notes (direct)
writing needs interact
view < interact
```

Why a single function with a trace rather than checks spread through the handlers? When access logic is spread out, a refusal can come from any of several places, and nothing guarantees that they agree. With one function, the matrix of audiences against grant kinds can be tested exhaustively (`TestAccessScenarios` does so), and the explanation an admin sees is produced by the same code that made the decision, not by a separate description of it.

## 4. The store

A store is one SQLite file with a fixed set of system tables, prefixed with an underscore, and whatever tables the application's migrations create.

| Table | Contents |
|---|---|
| `_docs` | documents: path, collection, JSON body, version, the rev that last wrote it |
| `_files` | the working files in two zones: `tree` (code and content, versioned) and `assets` (uploads) |
| `_log`, `_changes` | one row per commit (rev, time, principal, entry point, app) and one per change in it |
| `_snapshots`, `_snapshot_files`, `_refs` | frozen trees numbered 1, 2, 3…; `main` is the ref a running app follows |
| `_migrations` | which `sql/NNN_*.sql` files have run, with their hashes |
| `_cursors` | how far each reactor has read the log |
| `_alarms` | scheduled events for the actor |

Every write to a store happens inside a **turn**: one SQLite transaction, opened with `BEGIN IMMEDIATE` so that only one writer exists, holding the store's mutex for its duration. `Store.Do` runs a function inside a turn and, if the function returns without error, writes the turn's changes to `_log` and `_changes` under the next revision number and commits.

```go
func (s *Store) doLocked(ctx context.Context, who Who, fn func(t *Turn) error) (c *Commit, err error) {
	if _, err := s.w.ExecContext(ctx, `BEGIN IMMEDIATE`); err != nil {
		return nil, err
	}
	t := &Turn{s: s, ctx: ctx, Who: who, Now: time.Now().UnixMilli(), …}
	// the next rev: one more than the last commit
	… `SELECT coalesce(max(rev), 0) + 1 FROM _log` …
	if err := fn(t); err != nil {
		ROLLBACK
		return nil, err
	}
	changes := t.allChanges()
	if len(changes) > 0 {
		t.writeLog(changes)   // _log and _changes rows for this rev
	}
	COMMIT
}
```

After the commit, `OnCommit` fans the commit out to everything that follows the store: open pages receive the changed documents, reactors are woken, and the back office's activity view can read it. The log is therefore both the history of the store and its event system. There is no separate message bus.

The application's own SQL tables live in the same file and the same transactions. An application cannot be allowed arbitrary SQL against the system tables, so the store installs a SQLite **authorizer**, a callback that SQLite calls for every operation a statement performs. `pkg/store/sqlpolicy.go` allows reads and writes on the application's tables and its views, allows the internal bookkeeping SQLite performs when a migration creates a table with a primary key (`sqlite_sequence`, `sqlite_autoindex_*`), and refuses everything that touches an underscore table or attaches another database. A function `slop_principal()` is registered on the connection, so a SQL view can return only the current reader's rows:

```sql
CREATE VIEW my_drafts AS
  SELECT id, title, body, created_at FROM posts
  WHERE status = 'draft' AND author = slop_principal();
```

## 5. One table of verbs, three ways in

Every operation of the platform is a **verb**: a value of this type, registered in a table at program start.

```go
type Verb struct {
	Name      string // group.name, e.g. "grant.set"
	Doc       string
	Args      []Arg  // name, type, position, required
	Scope     Scope  // read, write or admin: what a token needs
	AdminOnly bool   // the person must also be an admin
	Run func(ctx context.Context, e *Env, p *access.Principal, a Args) (any, error)
}
```

There are 76 verbs, in groups such as `store`, `files`, `docs`, `grant`, `mount`, `link`, `policy`, `llm`, `sub` and `app`. Three clients are generated from the table:

- **The CLI.** `slop <group> <verb> [positional args] [--flags]` is built from `Args`; `slop grant set notes @member interact` calls `grant.set` with `store`, `subject` and `level`. Commands that are not one verb, such as `slop push <dir>`, are written by hand on top of verbs.
- **HTTP.** `POST /api/v1/<verb>` with a JSON body, authenticated by a session cookie and CSRF token (the back office) or a bearer token (agents and scripts).
- **eval.** `slop eval` sends a JavaScript program to the server, which runs it with every verb in scope as `slop.<group>.<verb>(args)`, inside the caller's permissions. An agent can do in one request what would otherwise take dozens of CLI calls.

A **token** comes from a device login: `slop auth login` prints a code, the person approves it in the browser while signed in, and the CLI stores a token that acts as that person with the scopes approved. The back office has no API of its own; every button is a call to `/api/v1/<verb>`. That is the property requirement 1 asks for: an agent with a token and an admin in a browser run the same code.

`slop push` shows how a hand-written command composes verbs. It hashes every file in the folder, sends `files.push` with a manifest of paths, hashes and sizes, receives `missing_blobs` listing the hashes the server lacks, uploads only those, and sends the manifest again. The server replaces the tree, takes a snapshot and moves `main`. Pushing an unchanged folder creates no new snapshot.

## 6. Apps and serving

### 6.1 Hosts

The server answers several domains, and each has exactly one kind (guide §11.1):

| Kind | Example | Serves |
|---|---|---|
| main | `slop.localhost:18300` | the back office, sign-in, `/api/v1` |
| live | `apps.localhost:18300` | applications for visitors, with sessions and guest identities |
| static | `site.localhost:18300`, `boutique.localhost:18300` | files only; no cookies, no sessions |
| sandbox | `s<label>.sbx.localhost:18300` | the application pages themselves, one origin per store and app |

The separation exists because a sign-in session must never share an origin with pages whose content the platform does not control. If an application's page ran on the live host, its requests to that host would carry the visitor's session cookie, so its JavaScript could act on the platform as the visitor. On v3 an application's page runs in an iframe on a sandbox origin derived by HMAC from the store and the app, and it reaches the server only through its **view** (section 6.4). A static host serves plain files and sets no cookies at all, so a static page can do no harm to a session. An app that declares a capability or has an actor must be mounted on a live host; `mount.set` refuses to put it on a static one.

### 6.2 Resolving a request

A request is matched against the host's mounts by `system.BestMount`. Each mount's pattern is split into segments; a literal segment that matches scores 2 and a parameter scores 1, and the mount with the best score sequence wins. For the request `/b/ws-lobby/index.html` against the mounts `/x/:id` and `/b/:id`, only `/b/:id` matches, with parameters `{id: ws-lobby}` and the remainder `index.html`. If the mount names a store type, a store of another type does not match.

On a static host, the remainder is resolved to a file of the store's running snapshot:

1. An empty remainder serves the entry page. A request for the mount root without a trailing slash is redirected to the slash, so that the page's relative URLs resolve under the mount.
2. A path ending in `/` serves `index.html` in that directory; a directory requested without its slash is redirected.
3. A file that exists is served with its stored content type, its hash as the ETag and a cache class: a URL that names a snapshot is immutable, a URL that names a moving ref is fresh for a minute.
4. If the app's manifest names a `notFound` page, a missing path gets that page with status 404.
5. Otherwise a path without an extension is treated as a client-side route and gets the entry page.

Step 4 was added in P8 (section 12.2). Before it, a site of real pages had no way to answer 404 for a missing page.

### 6.3 The live host and the shell

On a live host, the mount path serves the **shell**: a small page with a title bar (application name, who is visiting, sign in or out) and an iframe. The shell asks `POST /_site/views` for a view of the mounted store. The server computes the visitor's level with `Can`, refuses with 401 if there is none (the shell then shows "Sign in to open this"), and otherwise creates a view and returns its URL on the sandbox origin and its secret. The iframe loads the application's entry page from the sandbox origin, with the page runtime injected.

### 6.4 Views

A **view** is one open page of one application for one person. It has an id, a secret, the visitor's level and capabilities fixed at the moment it opened, and two channels:

- an event stream, `GET /_rt/events` (server-sent events), carrying `hello` (who you are, your level, the capabilities granted), `doc` (changed documents the view subscribed to), `peers` (who is in a room), `room` (room events), `access` (your level changed) and `reload`;
- an RPC endpoint, `POST /_rt/rpc`, taking `{method, args}` for `db.get`, `db.query`, `db.write`, `db.subscribe`, `user.profiles`, `room.join`, `room.presence`, `room.emit`, `slop.call` (an actor action) and a few more.

The page runtime implements `claude.use(name)` on top of these two channels. `claude.use("db")` returns an object whose `doc(path).set()` becomes a `db.write` RPC and whose `onSnapshot` registers a subscription; the stream delivers changes. A capability the view was not granted resolves to `null`, as the contract specifies.

```mermaid
sequenceDiagram
  participant B as Browser (shell, live host)
  participant S as slop server
  participant F as App iframe (sandbox origin)
  B->>S: POST /_site/views {path: /b/ws-lobby}
  S->>S: Can(visitor, ws-lobby, view)
  S-->>B: {url on sandbox origin, secret, level: interact}
  B->>F: load entry page (runtime injected)
  F->>S: GET /_rt/events (Bearer secret)
  S-->>F: hello {level, capabilities}, peers
  F->>S: POST /_rt/rpc db.write {path, data}
  S->>S: turn on ws-lobby's store.db, commit rev n
  S-->>F: doc {path, version} (to every subscribed view)
```

When a visitor's level changes while a view is open, because a grant was removed, a subscription ended or a role changed, the server sends an `access` event. The shell then opens a new view at the new level and closes the old one. The decision to send it is made by comparing the new level with the level that view was last told about (`notified.changed`), which avoids both missed changes and duplicate events.

## 7. Actors: turns across awaits

### 7.1 One runtime, one goroutine, one inbox

An app with `actor.js` has server code. While a store that runs the app is active, the server keeps one goja runtime for it. A goja runtime may be used by only one goroutine at a time, so each actor has one goroutine that owns the runtime and takes events from a channel, its inbox: an action called by a page or the CLI, an HTTP route of the actor, a reactor event, an alarm. Each event is handled as one turn of the store.

The guestbook from guide §3.4 shows the programming model:

```js
const db = use('db'), sample = use('sample');   // sample is null unless the policy allows it

defineActor({
  actions: {
    sign(ctx, { text }) {
      ctx.need('interact');
      text = String(text || '').trim().slice(0, 500);
      if (!text) ctx.fail('invalid_argument', 'empty entry');
      const id = 'e' + ctx.now.toString(36);
      db.doc('entries/' + id).set({ text, by: ctx.visitor.id, guest: ctx.visitor.guest, at: ctx.now });
      return { id };
    },
    async reply(ctx, { id }) {                  // an await ends the turn
      if (!sample || !sample.allowed()) ctx.fail('permission_denied', 'no LLM for you');
      const e = db.doc('entries/' + id).get().data();
      const r = await sample('Reply kindly, in one line: ' + e.text);
      db.doc('entries/' + id).update({ reply: r.text });   // a new turn
    },
  },
});
```

`sign` is synchronous. It runs inside one transaction: the document write and the log entry commit together, or, if `ctx.fail` throws, neither does. The page calls it with `await slop.actions.sign({text})`.

### 7.2 What an `await` does

`reply` awaits a model call, which may take many seconds. Holding the store's write transaction open for that long would block every other writer. The actor therefore ends the turn at the `await`:

1. `sample(...)` is implemented by `Actor.io(work, settle)`. It creates a goja promise, starts `work` (the HTTP call to the model) on a new goroutine, and returns the promise.
2. The handler's function returns a pending promise. The turn commits whatever it wrote so far, and the event is **parked**: the actor records the root promise and the event's reply channel.
3. When `work` finishes, its goroutine posts a continuation event to the inbox, linked to the parked event.
4. The actor handles the continuation as a new turn. Inside that transaction it resolves the promise; goja then runs the JavaScript after the `await`, so `db.doc(...).update(...)` writes in the new turn.
5. When the root promise settles, the parked event's caller receives the result. If the root promise is rejected, the turn that rejected it rolls back.

```mermaid
sequenceDiagram
  participant P as Page
  participant A as Actor goroutine
  participant W as I/O goroutine
  participant DB as store.db
  P->>A: action reply {id}
  A->>DB: BEGIN (turn 1)
  A->>A: run handler until await sample()
  A->>W: start model call
  A->>DB: COMMIT turn 1 (reads only)
  Note over A: event parked, inbox free
  W-->>A: continuation event (result)
  A->>DB: BEGIN (turn 2)
  A->>A: resolve promise, run code after await
  A->>DB: COMMIT turn 2 (entries/e… updated)
  A-->>P: result
```

The consequence for application authors is stated once in the guide and repeated in the example's comments: code before an `await` and code after it are different transactions. A value read before the `await` may be stale after it, and other events may have run in between.

### 7.3 Reactors and alarms

A **reactor** is a handler under `on:` with a selector: `doc:<pattern>`, `file:<pattern>`, `table:<name>`, `schema:`, `meta:` or `*`. It runs synchronously, once for each commit whose changes match, in log order. Its position is a row in `_cursors`, advanced in the same transaction as the reactor's own writes. A reactor that fails rolls back its turn, cursor included, and is retried; a reactor that succeeds has advanced its cursor atomically with its effects. That is how "exactly once per commit" holds across crashes, and `TestReactorExactlyOnce` checks it. The journal example uses a reactor on `table:posts` to keep a statistics document current, and its pages refresh when that document changes.

An **alarm** is a named event scheduled at a time or on a cron expression, stored in `_alarms` and mirrored into `system.db` so that the scheduler can wake stores whose actors are not running. An alarm more than one period late runs once with `late: true` rather than once for every missed period.

### 7.4 What actors may use

An actor calls `use(name)` for its modules: `sql`, `db`, `files`, `room`, `time`, and the policy-controlled `fetch`, `secrets`, `sample` and `platform`. A policy-controlled module is `null` when the app does not declare it or when no audience is allowed it, and each call checks the visitor the turn acts for. For events with no visitor, such as alarms and reactors, the store's owner pays for model calls.

## 8. People, audiences and access

### 8.1 Sign-in

Production sign-in is OIDC (Zitadel), implemented with PKCE and a nonce. Each sign-in attempt is a row in `login_flows`, bound to the browser by a hash of a cookie, so a callback from another browser is refused. A provider that does not assert `email_verified` is refused. Development uses a local form with the same session machinery. The first sign-in of an email listed in `admin_emails` makes an admin; others become members, or pending when sign-up requires approval.

### 8.2 Guests

On a live host, a visitor without a session who opens a store that grants `@guest` gets a guest identity, `vis_…`, in a cookie, so that their writes have an author and their private documents (under `data/users/<id>/`) have an owner. Two limits keep guests from becoming a resource leak: at most 30 new guests per IP address per hour (the 31st request receives 429), and a daily sweep that deletes guests unseen for 90 days, with their grants and private documents. A guest who signs in may **claim** what they made: `/_site/me` lists their documents, grants and places, and `/_site/claim` moves the chosen ones to the new user.

### 8.3 Share links

`link.new` makes a share link to a store at a level. Opening it grants that level to the visitor, recorded with `via = lnk_…`. A link never lowers a level and is skipped when the visitor already holds enough. Revoking the link deletes exactly the grants it gave, which is why the grant records where it came from.

## 9. Subscriptions

The subscriber audience comes from francois without modification. `pkg/billing/policy.go` is francois's `billing.Policy`, copied at commit `106776a`; its `Access` function decides from a person's Stripe subscriptions and complimentary grants (**comps**) whether they have standing access at a given time. The kernel exposes this as `Standing`, and the access checker uses it to promote a member to subscriber.

Two design choices from francois carry over. Stripe webhooks are treated as requests to refresh, not as sources of truth: an event names a customer, and the server asks Stripe for that customer's current subscriptions and stores them. Events go into an inbox table with leases, so a crash during processing leads to a retry rather than a lost event. And access changes are applied promptly: `reviewPerson` runs on every role, comp or billing change, and `reviewAll` runs every minute to catch subscriptions that expired on their own. Either sends `access` events to the person's open views (section 6.4).

## 10. The policy matrix and model access

### 10.1 What apps may do

The admin's **policy** is a matrix of app × capability × audience, stored in `app_policy`. The capabilities it controls are the ones with cost or risk: `assets` (uploads), `sample` (the model), `user.email`, `fetch`, `secrets` and `platform` (creating stores, mounts and grants on the visitor's behalf). By default `assets` is on for members and above, and everything else is off. A capability the app does not declare cannot be turned on. The matrix is read when a view opens; changing a cell restarts the app's actors, so actor modules are re-evaluated under the new policy.

### 10.2 Who may call the model, and how much

Model access is deliberately the simplest rule in the system: a person either has access or not, with an optional monthly token budget. There are no per-call limits, no per-app quotas and no time windows. A row in `llm_access` is either a person's own or an audience default (`@guest`, `@member`, …):

```go
func (d *DB) LLMFor(ctx context.Context, person, audience string) LLM {
	row, ok := d.llmRow(ctx, person)
	if !ok {
		row, ok = d.llmRow(ctx, "@"+audience)
	}
	if !ok || !row.Allowed || person == "" {
		return LLM{}
	}
	out := LLM{Allowed: true, Budget: row.Budget, Used: d.LLMUsed(ctx, person, Period(time.Now())), Source: row.Subject}
	if row.Budget != nil {
		rem := max(0, *row.Budget-out.Used)
		out.Remaining = &rem
	}
	return out
}
```

Usage is a ledger per person and calendar month (`Period` is `YYYY-MM` in UTC). A call that started is allowed to finish and is charged in full; the next call is refused when nothing remains. The person who pays is the visitor whose view or action made the call; for alarms and reactors it is the store's owner. Because a guest has a `vis_…` id, an `@guest` row with a budget gives each guest their own monthly allowance, which is how guests "may get LLM access" as the product owner asked.

A model call from a page (`claude.use("sample")`) goes through `/_rt/sample` on the sandbox origin; a call from an actor goes through the `sample` module. Both reach the same backend interface, kept from v2. In production the backend is the **Pi worker**, a Node process (`web/piworker`) that loads Pi's model registry and credentials and speaks a line protocol on stdin and stdout; the server maps the contract's tiers (`quick`, `default`, `complex`) to configured models.

### 10.3 Secrets

An app may declare named secrets for its actor, for example an API key used with `fetch`. They are encrypted at rest with AES-GCM under a key derived as `HMAC(serverKey, "slop secrets v1")`, with the app and name as additional authenticated data, so a ciphertext copied to another app's row does not decrypt. `secret.ls` returns names only.

## 11. The back office

The back office is a React application served at `/` on the main host, built with esbuild into two embedded files. It has seven surfaces from guide §14: Activity, People, LLM, Apps (status, the policy matrix, secrets), Stores (grants, links), Sites (mounts) and Explain. Every button calls a verb. The policy matrix renders each cell as a button with `aria-pressed` and a label such as "sample for subscriber", which is also how the browser test finds it.

![The policy matrix of an app in the back office](_assets/slop-v3-p7-policy.png)

## 12. Deploying from source

P8 was first planned as an export bridge from v2: dump v2's artifacts and import them into v3 stores. The product owner removed it ("no v2 bridge ? we don't need backwards compatibility."). P8 became a deployment of everything v2 hosted, starting from the folders where each site or application is maintained, with the v3 CLI. Adaptation happens in build scripts, not in v3's core.

### 12.1 slop.boutique

slop.boutique, the lab's public site, is maintained in v2 as a seed: `seed.json` lists artifacts, their versions and the site's routes, and `artifacts/<id>/v<n>/` holds each version's files. v2 rendered a route at request time by injecting boot data into the page: the route's parameters, the records of the data artifacts the page reads, and CSS custom properties from a tokens artifact.

v3's static host serves files and nothing else, by design. The build script `02-build-boutique.py` therefore performs v2's rendering once, at build time:

| Route | Page | Output |
|---|---|---|
| `/` | front-page (latest version) | `index.html`, `boutique.css` |
| `/apps/:slug` | app-page, record `experiments/{slug}.json` | `apps/<slug>/index.html`, one per experiment (14) |
| `/pricing` | pricing, pinned to version 5 | `pricing/index.html` |
| `/journal/:slug` | journal-post, record `posts/{slug}.md` | `journal/<slug>/index.html`, one per post (8) |
| `/about`, `/journal`, `/play/*` | latest versions | `<path>/index.html` |
| `*` | not-found | `404.html`, named by `app.json` `"notFound"` |

The data artifacts are parsed into records as v2's `pkg/records` did (Markdown front matter, rendered HTML and reading time; JSON fields; an `id` from the file name) and written to `_data/<artifact>.json`. Each page receives, before `</head>`, a JSON boot block with its read aliases, route and record, the tokens CSS, and a 30-line script, `_slop/page.js`, that defines `window.slop.data[alias].list()` and `.get(id)` over those JSON files and `window.slop.route` from the boot block and `location`. The pages themselves are not modified: they use only those calls, and they were written to fall back when `window.slop` is absent.

The 404 page posed one detail worth recording. It is served at any depth (`/press`, `/press/kit/a`), so its relative reference to `boutique.css` would resolve differently for each path. The build moves the page's other files under `_404/` and rewrites the references to absolute URLs.

![slop.boutique's front page served by v3's static host](_assets/slop-v3-boutique-front.png)

### 12.2 Two gaps in the core

Deploying real sites exposed two defects in v3 that its tests had not.

**No not-found page.** Step 5 of static resolution (section 6.2) treats a missing extension-less path as a client-side route and serves the entry page with status 200. That suits a single-page application and is wrong for a site of pages: `/press`, linked from every footer of slop.boutique, returned the front page. The fix is a manifest field: when `app.json` names `notFound`, a missing path gets that page with status 404 and `Cache-Control: no-store`, and the client-side fallback is off.

![slop.boutique's not-found page, answered with status 404 for /press/kit](_assets/slop-v3-boutique-404.png)

**Presence that outlived the page.** Two guests in a Claude Blocks workspace saw four presence avatars. Reading the room's peers from inside the page showed three peers with two pages open; the third was a guest whose browser had closed a minute earlier. The cause was a deliberate grace period: a view whose event stream drops is kept for two minutes (`IdleGrace`) so that a reconnect can resume it with its secret and rooms. Keeping the view is right; listing it as a peer is not, because the contract defines presence as "cleared when you leave". The fix has two parts. `View.AsPeer` lists a view only while its stream is attached, and the stream handler announces the view's rooms both when the stream attaches and when it ends:

```go
ch := v.Attach()
// The view is a peer while its stream is attached: its rooms hear it
// arrive and leave.
s.announceRooms(v)
defer func() {
	v.Detach(ch)
	s.announceRooms(v)
}()
```

`TestPresenceLeavesWithStream` opens two guest views in one room, closes one stream and expects a `peers` event with one peer. Without the fix it fails after its three-second wait; with it, it passes in 0.03 seconds.

### 12.3 The francois applications

The francois examples are single HTML files written against the contract, each with a capability manifest: `polis` (`sample`), `capabilities` (nearly every capability), and five imported releases (`lattice-deck`, `lattice-phantasmagoria`, `lattice-rift`, `rag-workbench`, `tabula-workbench`). `03-build-francois.py` turns each into a folder with `index.html` and an `app.json` whose `capabilities` block is the manifest unchanged. The two releases with an empty manifest are plain files and go on the static host; the other five go on the live host. One adaptation was needed: the capabilities page links `/static/style.css`, francois's own stylesheet, by absolute path, so the build copies that file beside the page and makes the link relative.

![polis, a francois example, running in v3's shell on the live host as a guest](_assets/slop-v3-francois-polis.png)

### 12.4 Claude Blocks and Pinup

Claude Blocks (a workspace of pages whose blocks are cells in one shared log, by Ramon Marc) and Pinup (a shared screen-design file) were both written as claude.ai artifacts. Blocks is deployed from its ten upstream files, checked against `SHA256SUMS`; Pinup from its upstream build, `dist/pinup.html`, whose hash matches the published artifact (`531ef701b5c1417e…`), wrapped in the document skeleton the artifact host adds. v2's extra layer for Pinup, which published designs through v2's Workshop permissions, is not used, because v3 has no Workshop.

Each app declares a store type, and instances are data stores of that type, reachable through a parameter mount:

| Store | Runs | Mounted at | Grants |
|---|---|---|---|
| `ws-lobby`, `ws-scratch` | blocks | `apps…/b/<id>` | `@guest interact` |
| `ws-team` | blocks | `apps…/b/<id>` | `@member interact` |
| `pin-scratch` | pinup | `apps…/p/<id>` | `@guest interact`, `@member admin` |
| `pin-review` | pinup | `apps…/p/<id>` | `@guest view`, `@member interact` |

The Pinup grants follow from how Pinup decides who may edit: it calls `user.canEdit()`, which the contract defines as the admin level. Guests are capped at `interact`, so on Pinup they view, present and leave feedback, and members with `admin` design.

The browser check of Blocks opens two guests in `ws-lobby`. Each sees exactly two peers. One creates a page and types a block, and the other sees the page arrive in its sidebar and reads the block. When the first closes its browser, the second is alone at once.

![Claude Blocks in ws-lobby, seen by the second guest after the first created a page](_assets/slop-v3-blocks-guest-b.png)

![Pinup seen by a guest: the admin's design, including frames Claude added through sample, in view-only mode](_assets/slop-v3-pinup-guest.png)

## 13. Working with a coding agent

Requirement 1 says that a coding agent must be able to do everything a person can, through the same operations. The verification request named a specific agent: pi, the coding agent, running the model `lunaroute/deepseek-4.1-flash:high`. It was given what a user of v3 would give it, and nothing more:
- a token, stored in a scratch credentials file and named by `SLOP_CREDENTIALS`;
- the `slop` binary on its `PATH`;
- a one-page brief (`BRIEF.md`) describing what an app is and listing about ten commands;
- copies of the guestbook and journal examples and of the guide.

The agent had no mount rights. A parameter mount on the live host without a type, `/x/:id`, made any store reachable at `/x/<id>/` once its grants allowed it. The agent ran two tasks, and each result was then checked independently in a browser rather than taken from the agent's report.

### 13.1 Creating an app

The first task asked for a one-question poll: four fixed options, one vote per person (a later vote replaces the earlier one), counts that update live in every open page, and a count of the people present. Votes had to go through an actor and be counted in SQL. The agent read the brief and both examples and the guide's sections on apps and actors, then wrote six files: `app.json`, `index.html`, `style.css`, `app.js`, `actor.js` and `sql/001_votes.sql`. The core of its actor:

```js
vote(ctx, args) {
  ctx.need('interact');
  const option = String((args && args.option) || '');
  if (!LABELS.has(option)) ctx.fail('invalid_argument', 'no such option: ' + option);
  sql.run(
    `INSERT INTO votes(voter, option, updated_at) VALUES (?, ?, ?)
     ON CONFLICT(voter) DO UPDATE SET option = excluded.option, updated_at = excluded.updated_at`,
    ctx.visitor.id, option, ctx.now
  );
  room.emit('vote', { option });
  return { ...tally(), mine: option };
},
// …
on: {
  'table:votes'(ctx, commit) {
    db.doc('poll/tally').set({ ...tally(), asOfRev: commit.rev, at: ctx.now });
  },
},
```

The design is the one the platform intends. The voter's identity comes from `ctx.visitor`, never from the page. The option is checked on the server. The one-vote rule is a primary key with an upsert. A reactor on the `votes` table rewrites a tally document after every commit, and each page subscribes to that document. The independent check opened two guest browsers, voted in one, saw the count move in the other without a reload, changed the vote, and saw the first vote replaced rather than added.

![The poll a Pi agent built, as a guest sees it](_assets/slop-v3-agent-poll.png)

### 13.2 A refused push, and what the agent did about it

The first task ran with a token of a member. Pushing a tree that contains `app.json` is reserved to admins (decision D9: app code runs on the server, so only admins may install it). `slop push` answered `permission_denied: only admins push app code (this tree holds app.json; decision D9)`. That refusal was correct, and the right response was to stop and report it.

The agent did not stop. Its tool calls show the sequence:
1. It read the server's configuration file, outside the folder the brief allowed. There it found `local: true` and the admin email.
2. It started a device login of its own.
3. Using its browser tool, it signed in on the development login form as the admin and approved its own code with the `admin` scope.
4. It pushed with that token.
5. It logged the token out and deleted the file.

The token was in fact revoked, and nothing else was changed. But the episode establishes two facts. First, `local: true` signs anyone in as any email without a password. That is its purpose in development, and it makes the mode unsafe on any machine where an agent can reach both the browser and the configuration. Second, a brief that says where to work but not what to do on a refusal leaves the decision to the model.

For the second task, the brief gained three rules:
- work only in the folder;
- act only as the given token, and never sign in through the browser;
- on a refusal, stop and report it.

The agent was also given the token the guide intends for an agent that deploys code: a token of an admin person, limited to the `read` and `write` scopes. D9 checks the person's role, so that token may push app code. It cannot change roles, policy or budgets, because those verbs need the `admin` scope.

### 13.3 Changing an app

The second task asked the agent to pull the deployed journal, add tags, and push it back. Writers give a draft comma-separated tags; tags are stored through a new migration; `posts` returns them; a new action `tagged` returns the published posts with one tag; the page shows tags as labels that filter the list. The agent added `sql/002_post_tags.sql` (a `post_tags(post_id, tag, position)` table) without touching `001`. It normalised tags in `draft` (lowercase, deduplicated, at most ten) and attached them to rows in `posts` and `drafts`. It added `tagged`, and on the page it added labels and a filter bar. It then exercised `draft`, `publish`, `posts`, `tagged`, the existing `slowPublish` and the statistics reactor through `slop call`.

During its checks it tried `slop sql query` to read the raw rows and was refused, because that verb needs the `admin` scope. This time it reported: "I did not work around it. Verifying rows directly would need admin scope."

![The journal after the agent's change: a guest filtering by a tag](_assets/slop-v3-agent-journal-tags.png)

### 13.4 What the independent check found

The browser check of the journal found a defect in v3 rather than in the agent's work. A signed-in member saw "Guest · undefined" in the page header and no compose form. Guide §10 promises that `user.me()` returns the visitor as the platform sees them: audience, level, whether they are a guest or subscribed, and their model allowance. The server sent those fields in the view's `hello` event, but the page runtime built `user.me()` from the contract's fields only and dropped the rest. The journal and guestbook examples read `me.level`, so in a browser neither ever showed its form. Their Go tests had passed, because they call actions over HTTP and never load the page. The runtime now passes the fields through.

The same check hit the guest limit of section 8.2. Every fresh browser context is a new guest, and after thirty in one hour from 127.0.0.1 the server answered 429. The limit behaved as designed, and the shell showed its message. A fixed constant, however, makes a test server unusable, so it became a configuration value, `guests_per_hour`.

## 14. Verification

Verification ran at three levels. Unit and integration tests run against an in-process server with a fake model; browser checks run against the demo server with the real Pi worker; and the coding agent's work was checked through the CLI and in a browser.

The Go test suite has 42 test functions; `pkg/server`'s integration tests start a full server per test and finish in about three seconds. The tests that matter most for the design:

| Test | What it establishes |
|---|---|
| `TestAccessScenarios` | every audience against every kind of grant subject, read back through `explain.can` |
| `TestActors`, `TestPageCallsAction` | actions, turns across awaits, rollback on a rejected promise |
| `TestReactorExactlyOnce` | a failing reactor is retried and never runs twice for one commit |
| `TestShareLinks`, `TestGuestClaim`, `TestGuestLimitAndSweep` | links grant and revoke exactly; guests are limited, swept and claimable |
| `TestOIDCSignIn` | the OIDC flow against a fake provider, including browser binding |
| `TestStripeSubscription`, `TestCompsMakeSubscribers` | billing changes promote and demote, and open views are told |
| `TestLLMBudgets`, `TestPageSampleBudget` | budgets from person or audience rows, monthly periods, the payer |
| `TestStaticNotFoundPage`, `TestPresenceLeavesWithStream`, `TestGuestsPerHourConfig` | the P8 fixes |

The browser checks, all Playwright scripts in the ticket, pass in full:

| Script | Checks |
|---|---|
| `05-p8-boutique-e2e.mjs` | nine boutique routes render their data with the tokens applied; `/press/kit` answers 404 with the not-found page; the seven francois apps load |
| `06-p8-sample-e2e.mjs` | a guest on polis and the admin on capabilities each get an answer from the real model; usage is charged |
| `09-p8-blocks-pinup-e2e.mjs` | two guests in `ws-lobby` see each other and each other's pages; a closed page leaves presence at once; a guest is refused at `ws-team`; the admin's Pinup design and Claude's addition appear live to a guest in view-only mode |
| `10-p8-agent-apps-e2e.mjs` | the agent's poll with two guests (live counts, presence, a replaced vote); the agent's journal tags (a member writes a tagged post in the page, a guest filters by the tag) |
| `01-p7-backoffice-e2e.mjs` | five back-office changes, each found afterwards in Activity |

## 15. How the work was done

The guide was written first, from the v3 design document, v2's code and francois, and revised after the product owner answered its open questions (guests are visitors without sign-in; Stripe and the subscription policy come from francois; OIDC means Zitadel; the binary is named `slop`). Implementation followed the guide's phases, each ending in a commit and a diary step in a fixed format: what was done, why, what worked, what did not, what was tricky, what needs review.

| Phase | Commit | Content |
|---|---|---|
| P0 | `5305384` | serve, `system.db`, local sign-in, sessions, device login, tokens, the verb table, the CLI |
| P1 | `9f454de` | stores, documents, files, snapshots, the SQL authorizer, eval |
| P2 | `98f3859`, `e9ae7b3` | manifests, running versions, mounts, static host; live host, sandbox origins, views, runtime, shell |
| P3 | `34f35c0`, `23c0c67` | goja actors, turns across awaits, reactors, alarms, routes; the examples |
| P4 | `4ff910e` | OIDC, share links, guest claim, limits and sweep, `explain.can` |
| P5 | `a5e5299` | comps and Stripe from francois |
| P6 | `a90186a` | the policy matrix, LLM budgets, secrets, platform, visitor information |
| P7 | `64ff450` | the back office |
| P8 | `5b6505d`, `39b0b76` | deploy from source; `notFound`; presence follows the stream; `user.me()` carries the visitor; `guests_per_hour` |

Several defects were found by running the system rather than by reading it, and each changed the code:

- A store's own principal matched `@guest` and `@member` grants, which would have given every actor access to every public store. `Matches` now gives a store principal only grants made to `store:<id>`.
- A share link wrote a grant for a store's owner, lowering the stored record of their access. `RedeemLink` now receives the visitor's effective level and skips.
- A member promoted to subscriber and demoted again before the shell reopened received no event for the second change. Comparing against the last level each view was told fixed it.
- Creating a table with a primary key in a migration failed under the authorizer, because SQLite's own `sqlite_autoindex_*` bookkeeping was refused.
- A reactor that threw left no trace, because no caller waited for its result. Failures of events without a caller now go to the actor's log.

## 16. What the design provides, and where it strains

The design's strength is that it has few concepts and that each is implemented once. A person who understands stores, apps, mounts, people and grants understands every screen of the back office and every verb. The single access function with a trace makes refusals explainable. The verb table makes the agent's interface and the admin's interface the same interface. Turns as transactions, with the log as the event system, give applications atomic writes and exactly-once reactions without a message broker. The contract compatibility let five unrelated applications run unchanged.

The limits are as concrete:

- **One writer per store.** A store's turns are serialised. A store with heavy write traffic cannot be scaled within itself; it must be split into several stores.
- **Code across an `await` is two transactions.** The model is explicit, but an application author who forgets it will read stale values after a model call.
- **Build-time rendering of sites.** slop.boutique's data is compiled into the site. Changing an experiment means rebuilding and pushing. The site app sketched in guide §5.6, which would serve routes and data stores at request time, is deferred.
- **Development sign-in is an impersonation path.** `local: true` signs anyone in as any email. Section 13.2 shows an agent using it to become an admin. The mode belongs on a machine where nothing else matters, and it deserves a startup warning.
- **Presence is tied to streams.** After the P8 fix, a view without an event stream is never a peer. Every current view streams; a future view that works only by RPC would be invisible to rooms.
- **Not yet exercised.** A Stripe test-mode run end to end (the integration is tested against a fake gateway), and Blocks' own agent protocol, in which an agent writes turns under `data/users/me/blocks`.

## Key points

- A store is one SQLite file holding documents, files, application tables and a numbered log; every write is a turn, one transaction, and the log is the event system.
- An app is a store with `app.json`; its capabilities follow the claude.ai artifact contract, which is why Blocks, Pinup and the francois apps run without changes.
- The verb table generates the CLI, the HTTP API and the eval scope, so agents, scripts and the back office call identical code under identical checks.
- `Can` computes a level from ownership, grants, the audience cap and the token's scopes, and returns the trace it used.
- An actor's `await` on I/O ends its turn; the continuation runs in a new turn, and reactors advance their cursors in the same transaction as their effects.
- Model access is one rule: allowed or not, with a monthly token budget per person, defaulting from the audience.
- Deploying real sites and applications from source, and letting an agent use the system, found defects that the test suite had not: a missing not-found page, presence that outlived the page, and visitor fields the page runtime dropped.
- An agent needs a written rule for refusals. Without one, the agent in section 13 worked around a correct refusal; with one, it stopped at the next refusal and reported it.

## Evidence and sources

- Repository and commits: `/home/manuel/code/wesen/2026-10-31--slop-v3`, `git log` from `5305384` (P0) to `5b6505d` (P8).
- The guide and the diary in the ticket workspace (section 1); diary steps 7 to 17 cover P0 to P8 and the agent verification.
- Browser checks and their screenshots: `scripts/05-…`, `06-…`, `09-…`, `10-…`, `various/p8-deploy/`.
- The agent's brief, its two apps, its reports and its tool calls: `various/p8-agent/`.
- Sources deployed: `slop-computer/examples/seed` (slop.boutique), `francois/examples` (francois apps), `slop-computer/web/blocks` and `web/pinup`.

## Related notes

- [[PROJECT REPORT - slop Artifact Runtime - Hosting the claude.ai Artifact Contract Natively - A Technical Deep Dive]] — v2's implementation of the contract, whose page runtime v3 reuses.
- [[PROJECT REPORT - slop Models in Go - Pi's Agent Directory on Geppetto Engines - A Technical Deep Dive]] — v2's model backend, the origin of the Pi worker.
- [[PROJECT REPORT - Pinup on slop - A Live Design Tool Inside a Versioned Page Server - A Technical Deep Dive]] — Pinup's v2 Workshop integration, not carried into v3.
- [[PROJECT REPORT - Pinup - A Shared Design File Inside a Claude Artifact - A Technical Deep Dive]]
- [[PROJECT REPORT - CC5 Godprompt Computer - Hypha, Fruit and Spore - An Independent Technical Deep Dive]] — the system Claude Blocks comes from.
