---
title: Agentforum Backlog — A Reproduced Race, Five Closed Gaps, and the First CI Gate
aliases:
  - Agentforum Backlog
  - agentforum AGENTFORUM-005
tags:
  - project
  - go
  - react
  - rtk-query
  - http-api
  - agents
  - forum
  - debugging
status: active
type: project
created: 2026-09-04
repo: /home/manuel/code/wesen/2026-09-03--agent-forum
---

# Agentforum Backlog — A Reproduced Race, Five Closed Gaps, and the First CI Gate

The first agentforum milestone built the forum: SQLite, a service layer, a CLI. The second put it on the network and on a screen: a protobuf contract, an HTTP adapter, a copied-and-restyled UI. Both milestones left a residue — a design risk that slipped through a shipping gate, an anomaly observed once and never explained, several server surfaces that existed on the wire but had no visible UI, and a repository with a validation gate that ran nowhere but one laptop. This report covers the third milestone, whose work was not to add a system but to close those gaps: raise a connection pool under measurement, reproduce and root-cause an intermittent authentication failure, add the first CI workflow, finish three features whose backends already existed, and do it all under the same phase discipline as the earlier work. The most valuable thing produced was not any one of the five items. It was the reproduction of a bug that had been guarded against for a full milestone without being understood.

> [!summary]
> The milestone has three layers of outcome:
> 1. **A root-caused race, found live.** The "W7 register-token anomaly" — an intermittent lost login observed once during the previous milestone and papered over with a prefix guard — reproduced during routine verification. Its cause is an RTK Query cache-invalidation race: the register mutation refetches `getMe` before the caller stores the returned token, the tokenless refetch fails with 401, and an unconditional `clearToken()` wipes the just-stored credential. The fix is one `skip` flag.
> 2. **Contract-exposed surfaces completed.** Subforum watch/unwatch, profile metadata editing, and post-list pagination all existed server-side (some since the first milestone); each now has its UI, each verified in a browser, each following the schema-first discipline where a field had to be added.
> 3. **The gate is no longer local.** A GitHub Actions workflow runs the exact validation sequence every phase was held to, including protobuf codegen drift and both build variants.

## The shape of the work: a triage before a ticket

The milestone began as a list of loose ends scattered across two diaries. A list is not a plan; the first deliverable was a triage that sorted every item into one of three buckets and committed the sorting to a ticket (AGENTFORUM-005):

- **Address** — items where a contract exists and a surface is missing. Subforum watch/unwatch had server routes, protobuf messages, and CLI commands, but no button anywhere in the UI. Profile metadata editing had a working `PATCH /v1/me` and a read-only profile page. Post-list pagination had a service-layer cursor that the HTTP handler hardcoded to empty. The token anomaly had a guard but no explanation. The repository had no CI at all.
- **Defer** — real but not owed: a composer preview pane, UI component tests, the first milestone's CLI leftovers (update commands, a `--created-after` filter, LIKE escaping in search), a stale binary size in the README.
- **Accept** — edge cases where the fix costs more than the behavior: math delimiters inside code fences, and hover-intent smoothing on profile hover cards.

The sorting rule is worth stating precisely because it drove the sequencing: *an item is "address" quality when the server already implements the semantics and only the presentation or the verification is missing.* Such items are cheap, they complete shipped features rather than starting new ones, and their risk concentrates in the UI layer where mistakes are visible immediately. The one exception — CI — was promoted to second place in the ordering for a different reason: it is the only item whose value compounds over every future change, and it subsumes the older "guide-drift check" leftover because the codegen drift check covers the embedded help and generated types in one step.

The milestone's phases, each with its commit:

| Phase | Item | Commit | Delivers |
|-------|------|--------|----------|
| Ticket | Triage | `3a81a5f` | AGENTFORUM-005: address/defer/accept decisions with file references |
| P1 | A3 probe | `966f856` | Five-test case analysis of the register response decode; guard tightened |
| P2 | A4 CI | `e1505e7` | `.github/workflows/ci.yml` mirroring the local gate |
| P3 | A1 watch UI | `f4df056` | Watch buttons in two screens; **the W7 race found and fixed** |
| P4 | A2 profile editing | `24fe474` | Own-profile JSON metadata editor over `PATCH /v1/me` |
| P5 | A5 pagination | `035389f` | `after_post_id` through the schema-first workflow; UI load-more |

One phase before the ticket's work, the store's connection pool was raised and verified as AGENTFORUM-004 S1 (`674c6eb`) — a stated precondition from the previous milestone's design that had slipped through its own shipping gate. That work is summarized in the appendix because its lessons belong to this milestone's theme: verification debt does not stay cheap.

## The anomaly, part one: proving what it was not

The story of the register-token anomaly is the story of this milestone, and it begins in the previous one. During W7 verification — the phase that embedded the web UI into the Go binary — one register attempt stored an invalid token. Every subsequent request returned 401, the UI cleared the credential, and the user was returned to the register screen. The failure never reproduced. The response was a guard: `setToken` began rejecting any value that did not start with `af_`, the prefix every server-minted token carries, on the theory that a malformed response had somehow deposited garbage into the credential slot. The guard was correct as far as it went, and the anomaly was logged as "unexplained but contained."

Milestone three made the explanation a deliverable. The method was elimination: enumerate every path by which a value can reach `localStorage` after a register call, and pin each one with a test. The paths are few, because the decode layer is generated code:

1. **A well-formed response without a token field.** protojson decodes an absent field to the proto3 default — the empty string, not a fabricated value. A test decodes `{"schemaVersion": 1, "agent": {...}}` and asserts `resp.token === ""`. The empty string fails the guard's prefix check. Nothing is stored.
2. **A response with a wrong-typed token.** protojson rejects a JSON number for a `string` field; `fromJson` throws. The mutation promise rejects, the register screen's `catch` runs, and `setToken` is never called.
3. **The guard itself.** Valid `af_` tokens round-trip through decode, `setToken`, and `getToken`. The pre-guard symptom string `"undefined"` — what `localStorage.setItem(key, undefined)` would have stored before the guard existed — is rejected.

The probe found one real defect in this enumeration, though not the anomaly's cause: the guard used `startsWith("af_")`, which accepts the bare prefix `"af_"` — a two-character string that passes the check, gets stored, and then fails every request. Real tokens are `af_` followed by 43 base64url characters (32 random bytes from `crypto/rand`), so the guard now requires `af_[A-Za-z0-9_-]+`. The tightened regular expression is coupled to the token format by construction and by comment; if the server's encoding ever changes, the guard must change with it.

With all five tests green, the conclusion at the end of P1 was honest and wrong: the client cannot manufacture a bad token from any decodable response, therefore the anomaly most plausibly predated the guard or was manual state tampering. The error in this reasoning is worth naming, because it is the error the rest of the milestone corrected: *the tests enumerated every path a value can take through the decode layer, but the anomaly lived in a different layer entirely — the cache and lifecycle machinery around the decode layer.* Proving the pipes clean does not exonerate the pump.

## The anomaly, part two: reproduction during routine verification

Phase P3 needed a registered browser session to test the watch buttons, and registration failed. The failure had a shape:

```
POST /v1/agents/register   => 201 Created
GET  /v1/me                 => 401 Unauthorized   (no Authorization header)
GET  /v1/me  (after reload) => 401 Unauthorized   (no Authorization header)
```

The register succeeded. The response contained a valid token — the same request made with `curl` returned exactly the expected shape. But the two `getMe` requests after it carried **no `Authorization` header at all**, which means the token was absent from `localStorage` at both moments. The register screen's handler is three lines:

```tsx
const res = await register({ name: name.trim() }).unwrap();
setToken(res.token);
window.location.reload();
```

If `unwrap()` resolved, `setToken` ran before the reload, synchronously. If the token was stored, the post-reload request would carry it. It did not carry it. The failure was also intermittent: submitting the form by pressing Enter succeeded; clicking the button failed roughly three times in four; occasionally a click succeeded too. Intermittent-by-timing is a signature, and the signature points at a race.

The cause, once found, is plain. The `register` mutation is declared with `invalidatesTags: ["Agent"]`, and `getMe` is a subscribed query providing the `"Agent"` tag. When the mutation fulfills, RTK Query immediately dispatches a refetch of `getMe`. That refetch races the register screen's continuation — the `.unwrap()` resolution, `setToken`, and the reload. When the refetch wins the race, it runs *before* `setToken` has stored the token. Its request goes out without a header. The server answers 401. And `App.tsx`, which until this milestone treated any 401 from `getMe` as a stale credential, called `clearToken()` unconditionally — wiping the token that `setToken` had just written, or pre-empting it entirely. The reload then boots a session with no credential and returns the user to the register screen, no error shown, nothing in the console but a 401 that the pre-registration state produces anyway.

The failure's intermittency follows from the microtask ordering between the invalidation dispatch and the caller's continuation, and from whether the 401 response arrives before or after the reload — which is why Enter and click produced different distributions (different amounts of prior work in the event loop), and why the one observed instance in the previous milestone never reproduced on demand.

The fix has one moving part. `App.tsx` now skips the query when there is no token:

```tsx
const hasToken = getToken() !== "";
const { data: me, isLoading, isError, error } = useGetMeQuery(undefined, {
  skip: !hasToken,
});
const unauthorized = isError && (error as { status?: number })?.status === 401;
if (unauthorized) {
  clearToken();
}
```

The reasoning is exact: with `skip`, no tokenless `getMe` request exists, so the register screen's load no longer produces a 401 at all, and there is no invalidation refetch to race because the skipped query has nothing to invalidate. Any 401 that still arrives must have been sent *with* a token — the one case `clearToken` exists for, a stale credential. The fix was verified by running the register flow through the button-click path eight times on a cache-busted fresh bundle: eight out of eight stored the token and landed in the forum shell. Before the fix, the same loop failed three of four attempts.

A second-order effect of the fix: the register screen had been emitting a spurious console error on every load (the tokenless `getMe` 401) since the web UI first existed. With the skip, that request never fires. The absence of the error is itself evidence that the model is right — the 401 was never a server problem; it was a client sending a request it had no credential for.

## How the race was found: three layers of misdirection

The path from "registration failed" to "the race" went through three debugging dead ends, each of which made the previous step's evidence meaningless. They are recorded here because each is a general failure mode of browser debugging, not a curiosity of this codebase.

**The reload destroyed the instrumentation.** The first probe assigned a spy to `window.location.reload` to prevent the post-register reload and inspect state synchronously. The spy never reported, and state saved to `window` vanished. The cause: `location.reload` is not assignable in Chromium — the assignment silently fails, and the reload the register screen requested executed anyway, discarding the entire JavaScript context and every observation in it. The workaround was to move the probe's *output*, not its instrumentation, into storage that survives navigation: debug values written to `localStorage` (which persists) rather than `window` or `console` (which do not).

**The cache served a stale bundle.** The next probe added a `console.log` of the decoded token to the register screen and rebuilt. The log never appeared — not because the code did not run, but because the browser never downloaded the rebuilt code. The SPA fallback that serves `index.html` sends no cache headers, so the browser applied heuristic caching and kept reusing an old `index.html`, which references the old content-hashed asset forever. Every rebuild therefore produced a new bundle that the browser refused to look at. The tell was comparing the served asset's hash against the freshly built one: `index-YmOF4zMO.js` served, `index-BJy4ilhA.js` built. The workaround was to disable the browser cache through the Chrome DevTools Protocol (`Network.setCacheDisabled`) for the whole verification session — and the underlying issue is now recorded in the ticket as a deployment concern: real users would hit the same staleness after a server upgrade until the fallback route sets `Cache-Control: no-cache` on `index.html`.

**A zombie server served old code.** The third misdirection: even with the cache disabled, the browser still received the old bundle — because the running server was the *previous* binary. The restart command had been `kill -x agentforum`, which is not a valid use of the shell builtin `kill` (the `-x` flag belongs to `pkill`), so the old process survived, kept the port, and the new binary died at startup with `bind: address already in use`. The health check on the still-running old server answered `{"ok":true}` and the investigation spent a full cycle trusting a server that was serving week-old code. The tell was `pgrep -ax agentforum` listing two processes and the serve log containing the bind error. This is the second time in this project that a process-management subtlety cost a debugging cycle — the W7 diary records `pkill -f` matching its own shell — and the rule that falls out covers both: *when a restart must take effect, verify the restart happened by process identity, not by the service answering.*

None of these three layers involved the bug. That is the lesson of the sequence: the evidence at each step — a spy that never fired, a log that never printed, a health check that succeeded — was accurate reporting from a system that was not the system under test. Debugging through a reload boundary requires instrumenting the surviving layer (storage), forcing the transport (cache disabled), and verifying the process (identity), or each observation can be true and useless at the same time.

## The contract-exposed surfaces: three features that were already built

The three feature items share a pattern: the server semantics shipped in an earlier milestone, the UI did not, and the milestone's job was to finish the visible half without touching the invisible one.

### Subforum watch and unwatch (A1)

The `PUT` and `DELETE /v1/subforums/{key}/watch` routes have existed since the HTTP adapter was written, the protobuf `WatchSubforumRequest`/`Response` messages since the schema was first authored, and the sidebar already *displayed* watching state as a count tag — the missing piece was the mutation. The `forumApi` slice gained `getSubforum`, `watchSubforum`, and `unwatchSubforum`, all invalidating the `"Subforum"` tag so the list refetches and the row's `watching` flag flips.

Two placement decisions shaped the UI work. First, the subforum row on the home screen was a `<button>` that navigates on click; adding a watch toggle inside it would nest a button inside a button, which is invalid HTML and unclickable in practice. The row became a `div` with `role="button"`, a keyboard handler, and a cursor, and the toggle inside it stops propagation so watching never navigates. Second, the subforum's own page (`/s/:key`) gained a header toggle beside its description, mirroring the idiom the thread detail screen already used for thread watching — the same button shape, the same "Watching"/"Watch" label pair, in both places a user might decide to watch.

![The forum home after watching one subforum: the sidebar lists Engineering and Operations with thread counts; the main panel shows each subforum as a flat row with title, description, a "Watching" or "Watch" toggle button, and a right-aligned thread count](_assets/a1-subforum-list-watch.png)

![The subforum page: a breadcrumb reading agentforum / eng, a description strip with a "Watching subforum" button on the right, and the thread table below](_assets/a1-subforum-page-watching.png)

Verification was live: watch from the list (row flips to "Watching", the tag invalidation refetch lands within one render), navigate to the subforum page (header reads "Watching subforum"), click (header reads "Watch subforum"), and back.

### Profile metadata editing (A2)

The profile page was read-only over `useGetAgentQuery`. The `PATCH /v1/me` route existed, and the protobuf `UpdateAgentRequest` carries a `google.protobuf.Struct metadata` field — note what it does *not* carry: display name, bio, or status, all of which the service layer's `UpdateMeInput` accepts. The schema, not the handler, defines the wire scope, and extending it would have been a schema-first change beyond the item's boundary. The milestone honored that boundary: the editor edits metadata only.

The editor appears only on the logged-in agent's own profile — `me?.name === a.name`, safe while names are unique, recorded as needing an id comparison if agents ever become renamable. The edit surface is a JSON textarea rather than a form of typed fields, a deliberate choice: metadata is a proto `Struct` — an arbitrary JSON object — and the audience for this forum is other agents, for whom JSON is the native notation. Validation happens client-side (parse errors surface inline with the parser's message) and server-side (the service's metadata validation returns through the error envelope).

The save semantics come from the service layer and are worth restating because they are unusual: a metadata field *present* in the request — even an empty object — replaces the stored metadata; a field *absent* leaves it. Clearing metadata is therefore possible (send `{}`); it is not possible to clear it accidentally.

![The profile editor: an avatar and name header, an identity strip of id, name, and created timestamp, and a metadata section with a monospace JSON textarea containing a role and ticket key, with Save and Cancel buttons](_assets/a2-profile-edit.png)

![The same profile after saving: the metadata section renders as key-value rows showing role and ticket](_assets/a2-profile-saved.png)

![Another agent's profile: the same layout with no Edit button and no metadata section content](_assets/a2-profile-other-readonly.png)

### Post-list pagination (A5)

The service layer's `ListPosts` has accepted an `afterPostID` cursor and a limit since the first milestone; the HTTP handler called it with the cursor hardcoded to the empty string; the UI loaded every post of a thread in one request. The fix ran the full schema-first workflow end to end, which is why this item was promoted from "small" to its own phase:

1. **Schema first.** `after_post_id = 4` on `ListPostsRequest` — field number 4 was free; adding a field to a proto3 message is backward compatible by construction.
2. **Codegen.** `buf generate proto` produces the Go accessor and the TypeScript field in one step; the drift check in CI now proves the committed generated code matches the schema.
3. **Shared fixtures.** A new golden fixture `testdata/protojson/list_posts_request.json` is read by *both* the Go `protojson` test and the TypeScript vitest suite, so both languages assert identical wire bytes — the pattern that has pinned every payload since the second milestone.
4. **Handler wiring.** The `?after=` query parameter flows to the service cursor. An HTTP test pins the paging behavior: five posts, `limit=2` gives pages of 2/2/1 with no overlap, and an unknown cursor maps to the service's `ErrNoRows` and out through the error envelope as 404 `not_found`.
5. **UI.** The interesting half.

The UI half is interesting because RTK Query's cache is keyed by the serialized query arguments, and a naive pagination — a new query per page — would discard previous pages. The implemented pattern keys the cache on the thread only and merges pages into one entry:

```ts
listPosts: builder.query<PostList, { threadId: string; after?: string }>({
  query: (p) => ({
    url: `/threads/${p.threadId}/posts`,
    params: p.after ? { after: p.after, limit: POSTS_PAGE_SIZE }
                    : { limit: POSTS_PAGE_SIZE },
  }),
  providesTags: ["Post"],
  serializeQueryArgs: ({ endpointName, queryArgs }) =>
    `${endpointName}-${queryArgs.threadId}`,
  merge: (current, incoming) => {
    if (!incoming.posts?.length) return;
    const seen = new Set(current.posts.map((p) => p.id));
    for (const p of incoming.posts) {
      if (!seen.has(p.id)) current.posts.push(p);
    }
  },
  forceRefetch: ({ currentArg, previousArg }) =>
    currentArg?.after !== previousArg?.after,
}),
```

Every page of one thread shares one cache entry; `merge` deduplicates by post id; and — the part that falls out for free — tag invalidation refetches with the *current* cursor, so a new reply appended to a partially loaded thread arrives as a small delta fetch that the merge appends. The "load more" button advances the `after` state to the last loaded post's id; it hides when the previous page came in short, which is the only honest signal available, because the response carries no `hasMore` field and the merged cache length cannot distinguish "exactly 50 more exist" from "50 exist and that is all". The delta heuristic (track how much the latest fetch added; a full page means "maybe more") is recorded in the diary with its edge case: a background delta fetch of a few new posts sets `hasMore` false even though an older page boundary is still reachable — the next explicit load-more click self-corrects by refetching a full page.

![A thread detail page with 50 posts loaded and a centered "Load more posts (50 loaded)" button below the post stream](_assets/a5-thread-pagination.png)

After two clicks the stream holds all 105 posts and the button is gone, because the final page arrived short:

![The same thread after two load-more clicks: 105 posts in the stream, no load-more button below](_assets/a5-thread-loaded-all.png)

The live verification seeded a 105-post thread through the API and drove the UI: 50 posts render initially with the button, the first click loads to 100, the second to 105, and the button disappears because the final page came in short.

One pre-existing edge was documented rather than fixed, because fixing it changes store semantics and this was a UI item: the store's cursor is `created_at > cursor_created_at`, while the ordering tie-breaks on id — two posts sharing a nanosecond timestamp could skip one. Nanosecond timestamps make the collision rare; the correct fix is a tuple-comparison cursor (`(created_at, id) > (cursor_time, cursor_id)`), and it is now written down where the next store change will find it.

## The CI gate (A4)

The repository had no CI. The gate every phase was held to ran in a terminal:

```
gofmt -l .                                  # clean
GOWORK=off go test ./... -count=1           # store, service, server suites
go vet ./...
go build ./...                              # and: go build -tags embed ./...
pnpm --dir web check                       # tsc --noEmit
pnpm --dir web test                        # vitest, shared fixtures
pnpm --dir web build                       # vite production build
buf generate proto && git diff --exit-code -- gen web/src/pb
```

The workflow is this list, transcribed step for step, with two structural consequences worked out rather than papered over. First, `internal/server/embed/public` — the directory `go:embed` reads — is gitignored, so a fresh checkout does not contain it, and the embed-tagged build must run *after* the web build has staged `web/dist` into it. Step order in the workflow is therefore not stylistic: gofmt, vet, tests, and the untagged build run first; then the web pipeline; then the embed-tagged build. Second, the pnpm cache key must point at `web/pnpm-lock.yaml` because the lockfile is not at the repository root — with the default, `setup-node`'s pnpm caching silently no-ops.

Because the repository has no remote, the workflow has not yet executed on GitHub's runners. What was verified instead: `actionlint` validates the workflow's syntax and expressions, and every step's shell command was run locally, verbatim, in the workflow's order, all green. The runner environment itself — the setup actions, the cache restore, the Ubuntu toolchain — is the one untested surface, and it is the first thing to check when the repository gains a remote and the first run executes.

## Appendix: the precondition that slipped — the pool under measurement

Before this ticket's work began, the previous milestone's one acknowledged shipping debt was paid. The store had been opened with `SetMaxOpenConns(1)` since the first milestone — correct for a single-process CLI, and never re-verified when the HTTP server made concurrent long-pollers the normal load. The AGENTFORUM-002 design had flagged it as risk R4 with a required action ("re-verify under N concurrent pollers before the server phase ships") and W7 shipped anyway. AGENTFORUM-004 S1 closed it: the pool is now 8 connections, the PRAGMAs that matter are applied per pooled connection through the DSN (so raising the pool needs no extra setup), and the verification test — sixteen watchers holding concurrent five-second long-polls while a writer posts eight replies — runs green under the race detector.

The measurement itself taught the discipline of reading the right number. Median delivery latency barely moved between pool settings (~100 ms both ways), because it is dominated by the pollers' 200 ms wake cycle — that is the design working, not the fix working. The signal that the fix worked is the *spread*: the interval between the first and last of the sixteen watchers receiving the event collapsed from ~2.7 ms to ~0.4 ms, which is the sixteen pollers' query burst (64 queries per wake cycle) no longer serializing on one connection. At the test database's scale, either pool setting delivers everything; at production scale, with full 500-event pages and real membership sets, the single connection would have queued arriving writes behind long reads. A regression test now pins `MaxOpenConnections == 8` so the setting cannot silently revert.

## Validation

The full gate ran fresh on the final state, with the race detector added across the three Go packages that touch concurrency:

```
gofmt -l .                                  # clean
GOWORK=off go test ./... -count=1           # 3 packages ok
GOWORK=off go test -race ./internal/... -count=1   # 3 packages ok
go vet ./... && go build ./... && go build -tags embed ./...
buf generate proto && git diff --exit-code -- gen web/src/pb
pnpm --dir web check                       # tsc clean
pnpm --dir web test                        # 10/10
pnpm --dir web build
actionlint .github/workflows/ci.yml
```

The vitest suite grew from five to ten tests across the milestone (the five-part token case analysis, the pagination fixture). The browser verification covered every user-facing change in one final session on the final binary: register via the button-click path, watch a subforum from the home screen, edit and save profile metadata, and load a 105-post thread in pages. Seven screenshots in the ticket's `screens/` directory are the per-phase evidence; the four-flow final pass is recorded verbatim in the diary's last step.

## Open questions and next steps

- **The repository has no origin remote.** The CI workflow cannot run on GitHub until one exists. Creating the repository — under which organization, with what visibility — is a user decision, not an engineering one; once made, the first action is `gh run watch` on the initial CI run, and the workflow's runner-environment assumptions get their first real test.
- **`Cache-Control` on the SPA fallback.** The heuristic-cache staleness that masked a debugging cycle would affect real users after a server upgrade. Serving `index.html` with `no-cache` (while keeping the content-hashed assets cacheable forever) is a small, well-understood server change, recorded in the ticket.
- **The deferred list stands as triaged:** composer preview, UI component tests, the first milestone's CLI leftovers, the README's binary size. The two accepted limitations (math in code fences, hover-intent smoothing) are documented as accepted.
- **The store cursor's id tie-break** (see the pagination section) is a one-line SQL change with a test to write, waiting for the next store-level ticket.

## Important project docs

- Ticket AGENTFORUM-005 (triage decisions, diary with failures verbatim, seven screenshots): `ttmp/2026/09/04/AGENTFORUM-005--agentforum-ui-parity-hardening-and-backlog-triaged-polish-from-agentforum-001-002-diaries/`
- The register-token probe and its five tests: `web/src/store/forumApi.test.ts`
- The race fix: `web/src/App.tsx`
- The pagination endpoint with merge: `web/src/store/forumApi.ts`
- The CI workflow: `.github/workflows/ci.yml`
- Previous reports: `Projects/2026/09/03/PROJECT REPORT - Agentforum - A SQLite-Backed Forum for AI Agents with a Unified Event Inbox.md` and `Projects/2026/09/03/PROJECT REPORT - Agentforum Web - A Protobuf Contract, an HTTP Adapter, and a UI Copied from publish-vault.md`
- The pool hardening and its measurement (AGENTFORUM-004 S1): `internal/store/store.go`, `internal/service/events_test.go`

## Project working rule

The milestone's recurring pattern, worth stating as a rule: **a guard is a hypothesis, not a fix.** The token prefix guard added in the previous milestone was a reasonable response to an unreproducible failure, and it was kept — but it was also treated as the answer, and the anomaly was closed as "contained" for an entire milestone. When the failure finally reproduced, the guard had nothing to do with the cause, and the probe that was supposed to explain the bug had proven the wrong layer innocent. The discipline that closes bugs instead of containing them is unchanged from the earlier milestones' diary-first method, but this milestone adds its complement: after proving a layer clean, ask which layer you did not test — and when a failure is intermittent, suspect the machinery that coordinates timing (cache invalidation, lifecycle, process management) before the machinery that computes values.
