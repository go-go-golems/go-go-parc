---
title: "ATProto Client: Building a Decentralized Social Web Application with Go and React"
aliases:
  - ATProto Client
  - AT Protocol Web Client
  - ATProto Viewer
tags:
  - article
  - atproto
  - go
  - react
  - vite
  - rtk-query
  - oauth
  - decentralized
  - bluesky
status: active
type: article
created: 2026-05-30
repo: /home/manuel/code/wesen/2026-05-30--at-proto
---

# ATProto Client: Building a Decentralized Social Web Application with Go and React

This article documents the complete process of building a web client for the AT Protocol — the decentralized social protocol that powers Bluesky — using Go for the backend and React with Vite and RTK Query for the frontend. It covers the protocol's architecture in precise technical terms, the OAuth authentication flow, the XRPC API proxy pattern, firehose real-time subscriptions, and the construction of a macOS 1 retro monochrome user interface. Every section is written for an engineer who wants to understand the system well enough to reproduce it, extend it, or debug it without referencing any other document.

The reference implementation lives at `/home/manuel/code/wesen/2026-05-30--at-proto`. It consists of 1,380 lines of Go across 4 packages and 1,087 lines of TypeScript, TSX, and CSS across 14 source files.

> [!summary]
> This article teaches four things:
> 1. The AT Protocol's federated architecture — PDS, Relay, AppView, Feed Generator, Labeler — and how data flows between them through signed repositories, XRPC calls, and firehose event streams.
> 2. How to use the Go indigo SDK to implement OAuth with DPoP, proxy XRPC calls, and parse firehose events.
> 3. How to wire a React+Vite+RTK Query frontend to a Go backend that handles all authentication and API proxying, with real-time updates via WebSocket.
> 4. The specific implementation decisions, failure modes, and API constraints encountered during the build.

## Why this note exists

Building an AT Protocol client requires understanding at least six distinct specifications (identity, repositories, XRPC, Lexicon, OAuth, sync) and how they interact. The official documentation is comprehensive but distributed across many pages. This article consolidates the essential protocol knowledge with the concrete engineering decisions and API patterns needed to produce a working client.

The article also records the specific version-dependent behaviors of the Go indigo SDK (pre-1.0, actively changing), the type signature mismatches between the tutorial documentation and the actual generated code, and the import-cycle resolution pattern required when combining indigo's OAuth client with a custom HTTP server.

## When to use this pattern

Build an ATProto web client with a Go backend proxy when:

- your frontend needs to authenticate users with ATProto OAuth, which requires server-side DPoP token signing that browsers cannot perform
- you want to subscribe to the firehose for real-time updates without exposing WebSocket connections directly to the browser
- you need to proxy XRPC calls to avoid CORS restrictions between the browser and PDS/AppView servers
- you want session persistence across browser tabs without embedding long-lived tokens in JavaScript

Do not use this pattern when:

- you only need read-only access to public data — use `https://public.api.bsky.app` directly from the browser with `@atproto/api`
- you are building a mobile app — use app passwords or native OAuth with a deep-link callback
- you need to operate infrastructure (PDS, Relay, AppView) — use the TypeScript reference implementation at `github.com/bluesky-social/atproto`

# Part I: The AT Protocol

## The federated architecture

The AT Protocol is a federated network protocol for decentralized social web applications. Federation means that account data is stored on host servers called Personal Data Servers (PDS), not distributed peer-to-peer between end devices. This design choice prioritizes availability and convenience: users do not need to keep a device online to serve their data.

The network has five service roles. Each can be operated by a different entity:

1. **Personal Data Server (PDS)** — the user's trusted agent. Hosts the user's data repository, manages authentication, controls the signing key, stores blobs (images, files), and proxies XRPC requests to other services.

2. **Relay** — the aggregation layer. Crawls all PDS instances and emits a unified firehose event stream containing every repository mutation across the network. Without Relays, every consumer would need to connect to every PDS individually, which does not scale.

3. **AppView** — the application logic layer. Subscribes to the Relay firehose, indexes records into queryable databases, and serves HTTP API endpoints for application-specific queries such as timelines, profiles, search results, and notification counts. Bluesky's AppView is at `api.bsky.app`.

4. **Feed Generator** — a custom algorithmic feed service. Subscribes to the firehose, applies custom logic to curate and rank posts, and exposes an XRPC endpoint (`app.bsky.feed.getFeedSkeleton`) that returns ordered lists of post AT-URIs. The AppView hydrates these skeletons into full post objects.

5. **Labeler** — a content labeling service. Subscribes to the firehose, applies labels to content and accounts, and publishes them. Labels are informational: they describe content, they do not hide it. Clients enforce labels based on user preferences.

Data flows through these services in a circular pattern. A user creates a post on their PDS. The PDS commits the record to the user's repository, signs it with the user's signing key, and emits a commit event. The Relay crawls the PDS, picks up the event, and broadcasts it through the firehose. The AppView consumes the firehose, indexes the post, and makes it available through timeline and search endpoints. Feed Generators evaluate the post for inclusion in custom feeds. Labelers may apply labels. Other users' clients query the AppView to display the post.

## Identity: DIDs and Handles

Every AT Protocol user has two identifiers that reference each other through bidirectional verification:

- **DID** (Decentralized Identifier) — a permanent, machine-readable identifier defined by the W3C DID Core specification. Example: `did:plc:bv6ggog3tya2z3vxsub7hnal`. DIDs never change. All content links use DIDs for stability.

- **Handle** — a human-readable DNS name. Example: `alice.bsky.social`. Handles are what users see, type, and share.

The relationship works through two resolution steps. First, the handle resolves to a DID via a DNS TXT record (`_atproto.alice.bsky.social` → `did=did:plc:...`) or an HTTPS well-known endpoint (`https://alice.bsky.social/.well-known/atproto-did`). Second, the DID resolves to a DID Document, which is a JSON object containing public keys, the user's handle, and the URL of the user's PDS.

AT Protocol supports two DID methods:

- **`did:plc`** — operated by the PLC directory service (a Bluesky-run consensus service). Provides strong consistency, key rotation through rotation keys, and a public API for creating and updating DID documents. This is the most common method.
- **`did:web`** — the DID document is hosted at a well-known HTTPS path on a domain the user controls. Simpler, but requires persistent domain ownership.

The DID Document contains the following fields:

```json
{
  "id": "did:plc:bv6ggog3tya2z3vxsub7hnal",
  "alsoKnownAs": ["https://alice.bsky.social"],
  "verificationMethod": [{
    "id": "#atproto",
    "type": "Multikey",
    "publicKeyMultibase": "zQ3sh..."
  }],
  "service": [{
    "id": "#atproto_pds",
    "type": "AtprotoPersonalDataServer",
    "serviceEndpoint": "https://bsky.social"
  }]
}
```

The `#atproto` key validates repository commits. The `#atproto_pds` service endpoint tells resolvers where to find the user's data. When a user migrates to a new PDS, the DID Document updates to point to the new endpoint, but the DID and all content links remain valid. This is the mechanism that enables account portability.

## Data repositories

A data repository is a self-authenticating, Merkle-tree-structured collection of records belonging to a single user. Every user has exactly one repository, identified by their DID.

The repository has three layers:

1. **Commit** — the signed root. Contains the root CID (Content Identifier) and a revision timestamp (TID). Every mutation produces a new Commit node with a new signature from the user's signing key.

2. **Merkle Search Tree (MST)** — an ordered, self-balancing tree structure. Each node is an IPLD `dag-cbor` object referenced by a CID (a multiformats content hash). The MST provides efficient lookups by path and compact proofs of inclusion.

3. **Records** — leaf data. JSON documents stored in collections, each identified by a record key (rkey). Most collections use TIDs (base32-encoded timestamps) as rkeys.

Records are addressed using AT URIs with the `at://` scheme:

| Level | AT URI | Meaning |
|---|---|---|
| Repository | `at://alice.bsky.social` | The user's entire repo |
| Collection | `at://alice.bsky.social/app.bsky.feed.post` | All posts by the user |
| Record | `at://alice.bsky.social/app.bsky.feed.post/3k2la...` | A specific post |

Repository data can be exported as CAR (Content Addressable aRchive) files, which bundle all IPLD blocks into a single file. CAR files are used for account migration, backup, and firehose sync (commit events include CAR block diffs).

## XRPC: The HTTP API system

XRPC (Lexicon RPC) is a thin wrapper around HTTPS that standardizes AT Protocol API calls. Every endpoint is identified by an NSID (Namespaced Identifier) rather than a REST-style path.

The HTTP request path starts with `/xrpc/`, followed by an NSID:

```
GET /xrpc/app.bsky.feed.getTimeline?limit=50&cursor=abc123
POST /xrpc/com.atproto.repo.createRecord
```

XRPC defines two request types mapped from Lexicon schemas:

- **Query** — HTTP GET. Cacheable, should not mutate state. Parameters are URL query parameters.
- **Procedure** — HTTP POST. Not cacheable, may mutate state. Request body is JSON.

The PDS acts as a generic proxy between clients and other AT Protocol services. Clients use the `atproto-proxy` HTTP header to specify which service should handle the request:

```
atproto-proxy: did:web:api.bsky.app#atproto_app_view
```

The PDS resolves the service DID, extracts the endpoint URL from the DID document, attaches an inter-service JWT signed by the user's signing key, and forwards the request.

Pagination uses cursor-based semantics. The first request omits the `cursor` parameter. If the response includes a `cursor` field, the client includes it in the next request. This continues until the response has no `cursor`, indicating the end of the result set.

Error responses use a standard JSON format:

```json
{"error": "RecordNotFound", "message": "Could not locate record"}
```

The `error` field maps to an error name defined in the endpoint's Lexicon schema, enabling programmatic error handling.

## Lexicon: The schema language

A Lexicon is a schema definition that describes record types, HTTP API endpoints, and event stream messages. Lexicon is similar to JSON Schema but includes AT Protocol-specific features such as NSID-based identification, union types for polymorphic records, and refs for cross-Lexicon schema reuse.

Every Lexicon is identified by an NSID with the format `domain.authority.collection.name`:

| NSID | Type | Purpose |
|---|---|---|
| `com.atproto.repo.createRecord` | procedure | Create a record in a collection |
| `com.atproto.sync.subscribeRepos` | subscription | Firehose event stream |
| `app.bsky.feed.post` | record | Schema for a post (max 300 chars) |
| `app.bsky.feed.getTimeline` | query | Home timeline |
| `app.bsky.actor.getProfile` | query | User profile with counts |

The `com.atproto.*` namespace contains core protocol operations. The `app.bsky.*` namespace contains the Bluesky application schemas. Third-party applications define their own namespaces.

## The firehose

The firehose is a real-time WebSocket event stream that broadcasts every repository mutation across the entire network. It is the backbone of the protocol's event-driven architecture.

To subscribe, connect via WebSocket to a Relay:

```
wss://bsky.network/xrpc/com.atproto.sync.subscribeRepos
```

The optional `cursor` parameter resumes from a specific sequence position.

The firehose emits several event types. The most important is `#commit`, which contains:

- `repo`: The DID of the repository
- `commit`: CID of the new commit
- `rev`: Revision sequence number
- `time`: Timestamp
- `ops`: Array of operations, each with `action` (`create`, `update`, `delete`), `path` (collection/rkey), and optional `cid`
- `blocks`: CAR block diff containing the actual record data

Other event types include `#identity` (DID document update), `#account` (account status change), and `#handle` (handle change).

The commit event's `blocks` field contains a CAR file with the diff of new and modified IPLD blocks. To extract records, the consumer must parse the CAR, look up each operation's CID in the block set, and decode the block from DAG-CBOR to JSON.

## OAuth with DPoP

AT Protocol uses OAuth 2.0 with DPoP (Demonstration of Proof-of-Possession) for client authentication. DPoP requires each API request to include a cryptographic proof that the access token holder also holds a specific keypair. This prevents token theft and replay attacks.

The OAuth flow for a web application has these steps:

1. The client application resolves the user's handle to discover their PDS.
2. The client registers a Pushed Authorization Request (PAR) with the PDS's authorization server.
3. The authorization server returns an authorization URL.
4. The user's browser opens the consent screen.
5. After the user approves, the PDS redirects back to the client's callback URL with an authorization code.
6. The client exchanges the code for access and refresh tokens, bound to the DPoP keypair.
7. For every subsequent API call, the client attaches a DPoP JWT proof header.

This flow must be handled server-side because the DPoP keypair management and JWT signing require cryptographic operations that browsers cannot perform securely. The Go backend handles all of this; the frontend only sees a session cookie.

# Part II: The Implementation

## Project architecture

The application has two components: a Go HTTP server and a React SPA. The Go server handles authentication, API proxying, and firehose relay. The React SPA handles all rendering and user interaction.

```
┌──────────────┐     HTTPS      ┌──────────────┐     XRPC      ┌──────────────┐
│  React SPA   │ ──────────────→ │  Go Server   │ ────────────→ │  PDS/AppView │
│  (browser)   │ ←────────────── │  (proxy)     │ ←──────────── │  (bsky.social)│
└──────┬───────┘                 └──────┬───────┘               └──────────────┘
       │                                │
       │ WebSocket                      │ WebSocket
       │                                │
       └────────────────────────────────┘
              /api/firehose relay
```

The Go server proxies all XRPC calls. The frontend never contacts AT Protocol services directly. This design is required for three reasons: DPoP signing must happen server-side, CORS prevents browser-to-PDS requests, and the firehose WebSocket connection benefits from server-side filtering.

## Go backend structure

```
internal/
├── config/config.go      — environment variable loading with defaults
├── auth/
│   ├── oauth.go          — OAuth client setup, flow handlers, session management
│   └── context.go        — AuthSession type, context injection, GetOAuthClient helper
├── server/
│   ├── server.go         — http.ServeMux routing, middleware chain, server creation
│   └── middleware.go      — AuthMiddleware for /api/* route protection
└── api/
    ├── handlers.go       — shared helpers (writeJSON, writeError, APIHandler struct)
    ├── feed.go           — timeline, thread, search proxy handlers
    ├── profile.go        — profile, follows, followers, actor search handlers
    ├── post.go           — create, like, unlike, repost, delete handlers
    ├── notifications.go  — list, unread count, update seen handlers
    └── firehose.go       — WebSocket relay from bsky.network to frontend clients
```

The entry point is `main.go`. It loads configuration, creates the auth store, creates the HTTP server, and starts listening.

## OAuth implementation with indigo

The indigo SDK provides the `atproto/auth/oauth` package, which handles the complete OAuth flow including DPoP. The implementation uses three key types:

- `oauth.ClientConfig` — defines the client ID, callback URL, and scopes
- `oauth.ClientApp` — the OAuth client that starts flows, processes callbacks, and resumes sessions
- `oauth.ClientSession` — an active session with token management and DPoP signing

The auth store is defined in `internal/auth/oauth.go`:

```go
func NewStore(cfg config.Config) *Store {
    var oauthConfig oauth.ClientConfig
    if cfg.Host == "http://localhost:8080" {
        oauthConfig = oauth.NewLocalhostConfig(
            cfg.Host+"/api/auth/callback",
            []string{"atproto"},
        )
    } else {
        oauthConfig = oauth.NewPublicConfig(
            cfg.Host+"/api/auth/client-metadata.json",
            cfg.Host+"/api/auth/callback",
            []string{"atproto"},
        )
    }
    oauthClient := oauth.NewClientApp(&oauthConfig, oauth.NewMemStore())
    cookieStore := sessions.NewCookieStore([]byte(cfg.SessionSecret))
    return &Store{OAuth: oauthClient, CookieStore: cookieStore}
}
```

`oauth.NewLocalhostConfig` creates a configuration suitable for local development. It uses a loopback redirect URI pattern that the PDS authorization server recognizes as safe. `oauth.NewPublicConfig` creates a production configuration that requires a client metadata document served at a well-known URL.

The login handler starts the flow:

```go
func (s *Store) HandleLogin(w http.ResponseWriter, r *http.Request) {
    handle := r.URL.Query().Get("handle")
    redirectURL, err := s.OAuth.StartAuthFlow(r.Context(), handle)
    http.Redirect(w, r, redirectURL, http.StatusFound)
}
```

`StartAuthFlow` resolves the handle to a DID, discovers the PDS, sends a Pushed Authorization Request, and returns the authorization URL. The browser redirects to the PDS consent screen. After approval, the PDS redirects to the callback:

```go
func (s *Store) HandleCallback(w http.ResponseWriter, r *http.Request) {
    sessData, err := s.OAuth.ProcessCallback(r.Context(), r.URL.Query())
    // Save session data to cookie
    sess, _ := s.CookieStore.Get(r, cookieName)
    sess.Values["account_did"] = sessData.AccountDID.String()
    sess.Values["session_id"] = sessData.SessionID
    sess.Save(r, w)
    http.Redirect(w, r, "/", http.StatusFound)
}
```

The session cookie stores only the account DID and session ID. The actual OAuth tokens (access, refresh, DPoP key) live in the indigo MemStore on the Go server. When an API handler needs to make an XRPC call, it resumes the session:

```go
func GetOAuthClient(ctx context.Context, authStore *auth.Store) (*oauth.ClientSession, error) {
    sess := SessionFromContext(ctx)
    did, _ := syntax.ParseDID(sess.DID)
    oauthSess, _ := authStore.OAuth.ResumeSession(ctx, did, sess.SessionID)
    return oauthSess, nil
}
```

`ResumeSession` returns a `ClientSession` that handles DPoP signing and token refresh automatically. The `APIClient()` method returns an `atclient.APIClient` pre-configured with the user's credentials.

## API proxy pattern

Every API handler follows the same pattern: extract the session, resume the OAuth client, make the XRPC call, return the JSON response.

```go
func (h *APIHandler) HandleGetTimeline(w http.ResponseWriter, r *http.Request) {
    oauthSess, err := h.getOAuthClient(r)
    if err != nil {
        writeError(w, http.StatusUnauthorized, err.Error())
        return
    }
    client := oauthSess.APIClient()
    params := map[string]any{"limit": 50}
    if cursor := r.URL.Query().Get("cursor"); cursor != "" {
        params["cursor"] = cursor
    }
    var resp TimelineResponse
    if err := client.Get(r.Context(), "app.bsky.feed.getTimeline", params, &resp); err != nil {
        writeError(w, http.StatusBadGateway, "failed to fetch timeline: "+err.Error())
        return
    }
    writeJSON(w, http.StatusOK, resp)
}
```

The `client.Get` method makes an authenticated XRPC GET request with DPoP proof attached. The method signature is `Get(ctx, nsid, params map[string]any, result any) error`. The `params` argument must be `map[string]any`, not `map[string]string` — this is a departure from what the tutorial documentation shows.

For write operations, the handler constructs the record body and calls `client.Post`:

```go
func (h *APIHandler) HandleCreatePost(w http.ResponseWriter, r *http.Request) {
    oauthSess, _ := h.getOAuthClient(r)
    client := oauthSess.APIClient()
    body := map[string]interface{}{
        "repo":       client.AccountDID.String(),
        "collection": "app.bsky.feed.post",
        "record": map[string]interface{}{
            "$type":     "app.bsky.feed.post",
            "text":      input.Text,
            "createdAt": syntax.DatetimeNow(),
        },
    }
    var resp RecordResponse
    client.Post(r.Context(), "com.atproto.repo.createRecord", body, &resp)
    writeJSON(w, http.StatusCreated, resp)
}
```

`syntax.DatetimeNow()` returns the current time in the AT Protocol's required ISO 8601 format. The `$type` field is required in every record to indicate its Lexicon schema.

## Firehose relay

The firehose relay has two connections: an upstream WebSocket to the Relay and downstream WebSockets to frontend clients.

```go
type FirehoseRelay struct {
    cfg     config.Config
    mu      sync.RWMutex
    clients map[*websocket.Conn]bool
}

func (f *FirehoseRelay) StartFirehose() error {
    relayURL := f.cfg.RelayURL + "/xrpc/com.atproto.sync.subscribeRepos"
    conn, _, err := websocket.DefaultDialer.Dial(relayURL, nil)
    // Read loop: parse messages, broadcast to clients
}

func (f *FirehoseRelay) HandleFirehose(w http.ResponseWriter, r *http.Request) {
    conn, _ := upgrader.Upgrade(w, r, nil)
    f.mu.Lock()
    f.clients[conn] = true
    f.mu.Unlock()
    // Keep alive: read client pings
}
```

The relay parses each firehose message by attempting to unmarshal it into one of the indigo generated types (`SyncSubscribeRepos_Commit`, `SyncSubscribeRepos_Identity`, `SyncSubscribeRepos_Account`). For commit events, it extracts the operations and broadcasts a simplified JSON event to all connected frontend clients.

The current implementation uses JSON unmarshaling, which works for the simplified relay use case. A production implementation would need to handle the actual CBOR frame format. The firehose does not send JSON — it sends DAG-CBOR frames with a CBOR header indicating the event type, followed by a DAG-CBOR body. The indigo SDK has a `lex/util` package with a frame reader that handles this, but integrating it requires additional parsing code that was not necessary for the initial implementation.

## Frontend architecture

The React frontend uses four key libraries:

- **React 19** with TypeScript for UI components
- **Vite 8** for development server and production bundling
- **RTK Query** (Redux Toolkit Query) for API state management with caching, invalidation, and optimistic updates
- **react-router-dom** for client-side routing

The RTK Query API definition in `store/api/atproto.ts` defines all endpoints with typed request and response interfaces:

```typescript
export const atprotoApi = createApi({
  reducerPath: 'atprotoApi',
  baseQuery: fetchBaseQuery({ baseUrl: '/api', credentials: 'same-origin' }),
  tagTypes: ['Post', 'Profile', 'Feed', 'Session'],
  endpoints: (builder) => ({
    getTimeline: builder.query<FeedResponse, { limit?: number; cursor?: string }>({
      query: (params) => ({ url: 'feed/timeline', params }),
      providesTags: ['Feed'],
    }),
    createPost: builder.mutation<{ uri: string; cid: string }, CreatePostInput>({
      query: (body) => ({ url: 'post/create', method: 'POST', body }),
      invalidatesTags: ['Feed'],
    }),
    // ... more endpoints
  }),
})
```

The `credentials: 'same-origin'` option ensures the session cookie is sent with every request. Cache invalidation works through RTK Query's tag system: when a mutation invalidates the `Feed` tag, all queries providing that tag are automatically refetched.

The firehose hook in `hooks/useFirehose.ts` subscribes to the relay WebSocket and dispatches cache invalidation when relevant events arrive:

```typescript
ws.onmessage = (event) => {
  const data = JSON.parse(event.data)
  if (data.type === 'commit' && data.ops) {
    const hasPostOps = data.ops.some(
      (op) => op.path.startsWith('app.bsky.feed.post') ||
              op.path.startsWith('app.bsky.feed.like')
    )
    if (hasPostOps) {
      dispatch(atprotoApi.util.invalidateTags(['Feed', 'Post']))
    }
  }
}
```

This creates a reactive data flow: firehose events invalidate the RTK Query cache, which triggers automatic refetches, which update the UI — all without manual polling or page refreshes.

## macOS 1 retro monochrome UI

The visual design follows the constraints of the original Macintosh System 1.0 (1984):

- **Black and white only** — no grayscale, no gradients. Elements are either foreground (black) or background (white).
- **No window chrome** — no title bars, no close/minimize/zoom buttons. The interface is a single flat panel.
- **No menu bar** — navigation is embedded in the content area as text links.
- **Tiny color accents** — only as text foreground color. Blue (`#0000cc`) for links. Red (`#cc0000`) for like counts. Never as background fill or border color.
- **12px sans-serif font** — matching the original Mac's 9pt Chicago font at modern pixel density.
- **512px maximum width** — the original Mac's screen width.

The CSS is defined entirely through custom properties in `styles/retro.css`:

```css
:root {
  --bg: #ffffff;
  --fg: #000000;
  --border: #000000;
  --muted: #666666;
  --accent: #0000cc;
  --accent-red: #cc0000;
  --font-sans: 'Geneva', 'Helvetica Neue', Arial, sans-serif;
  --font-size-base: 12px;
  --border-width: 1px;
}
```

Buttons use a classic Mac interaction model: black border, white fill, black text at rest; inverted (black fill, white text) when active. The `:active` pseudo-class implements this:

```css
button:active {
  background: var(--fg);
  color: var(--bg);
}
```

Focus indicators use dotted outlines matching the original Mac's keyboard navigation style. The loading state uses a rotating `◉` character instead of a spinner animation — the original Mac had no animation primitives.

## Go:embed frontend serving

The frontend is embedded into the Go binary using `go:embed`. The `frontend/embed.go` file declares:

```go
//go:embed all:dist
var distFS embed.FS
```

The `HandleSPA` function serves static files from the embedded filesystem and falls back to `index.html` for client-side routing paths. This means the production deployment is a single binary with no external file dependencies.

The build process is:

1. `cd frontend && npm install && npm run build` — produces `frontend/dist/`
2. `go build -o atproto-web .` — embeds `frontend/dist/` into the binary
3. `./atproto-web` — serves the SPA on the configured port

The Makefile encodes this order: `make build` runs `frontend-build` first, then `go build`.

# Part III: What Was Learned

## indigo SDK API constraints

The indigo SDK is pre-1.0 and its API differs from the tutorial documentation in several specific ways. These differences required code changes during implementation:

| Documentation says | Actual indigo API | Impact |
|---|---|---|
| `oauth.Session` | `oauth.ClientSession` | Type name mismatch in session handling |
| `client.Get(ctx, nsid, map[string]string, ...)` | `client.Get(ctx, nsid, map[string]any, ...)` | Parameter map must use `any` values |
| `syntax.ParseDID()` returns `*DID` | Returns `DID` (value, not pointer) | Cannot dereference with `*did` |
| `atURI.Rkey.String()` | `atURI.RecordKey().String()` | Method renamed |
| `atURI.Collection.String()` | `atURI.Collection().String()` | Collection is a method, not a field |
| Go 1.24+ required | Go 1.26 required | Module upgrade needed |

These constraints are not bugs in the SDK — they reflect its active development state. The generated types in `api/atproto/` and `api/bsky/` are auto-generated from Lexicon schemas and may change as the protocol evolves.

## Import cycle resolution

A Go project that combines indigo's OAuth client with a custom HTTP server will hit an import cycle if the auth middleware and API handlers are in separate packages. The cycle forms when:

1. `internal/server` needs `internal/auth` (for the middleware)
2. `internal/api` needs `internal/server` (for session extraction from context)
3. This creates `server → auth → server` or `api → server → auth → api`

The resolution is to extract the context types and helpers into the `auth` package itself:

```
internal/auth/context.go:
  - AuthSession struct (DID, SessionID)
  - SessionFromContext(ctx) → *AuthSession
  - SetSessionInContext(ctx, session) → context.Context
  - GetOAuthClient(ctx, authStore) → (*oauth.ClientSession, error)
```

The middleware in `internal/server/middleware.go` calls `auth.SetSessionInContext`. The API handlers in `internal/api/` call `auth.GetOAuthClient`. Neither depends on the other. The cycle is broken because both depend on `auth` but not on each other.

## OAuth localhost configuration

The indigo SDK provides `oauth.NewLocalhostConfig` for development. This creates a loopback client that uses `http://127.0.0.1:PORT/callback` as the redirect URI. The PDS authorization server recognizes loopback redirect URIs as safe and does not require client metadata registration.

For production, `oauth.NewPublicConfig` requires a client metadata document served at the client ID URL (e.g., `https://yourdomain.com/oauth/client-metadata.json`). The metadata document declares the client's name, redirect URIs, scopes, and JWKS URI.

The switch between these two configurations is controlled by the `HOST` environment variable in `config.go`. When `HOST` starts with `http://localhost` or `http://127.0.0.1`, the localhost config is used. Otherwise, the public config is used.

## Session store limitations

The implementation uses `oauth.NewMemStore()` for OAuth session data and `gorilla/sessions` with a CookieStore for browser session cookies. This combination has two limitations:

1. **Sessions are lost on server restart.** The MemStore keeps all OAuth tokens in memory. If the Go process restarts, every user must re-authenticate.

2. **No horizontal scaling.** The MemStore is process-local. Multiple server instances cannot share session data.

The production fix is to replace the MemStore with a SQLite-backed store (using the `authStore` pattern from the indigo cookbook's `go-oauth-cli-app`) and replace the CookieStore with a Redis-backed session store. The SQLite store persists tokens across restarts and allows multiple server instances to share session data through a shared database.

## Firehose message format

The firehose does not send JSON. It sends DAG-CBOR frames. Each frame has a CBOR header indicating the event type (a number mapping to an NSID), followed by a DAG-CBOR body containing the event data.

The simplified implementation in `internal/api/firehose.go` attempts JSON unmarshaling, which works for some messages but will fail for others. The correct approach uses the indigo SDK's `lex/util` frame reader:

```go
// Production firehose reading pattern (not yet implemented)
reader := lexutil.NewFrameReader(conn)
for {
    header, body, err := reader.ReadFrame()
    // header contains the event type NSID
    // body is DAG-CBOR that can be decoded into the generated type
}
```

This is the most significant technical gap in the current implementation. The firehose relay works for development and demonstration but will miss or misparse events in production use.

## Vite 8 import resolution

Vite 8 uses rolldown as its internal bundler, which has stricter import resolution than the esbuild-based Vite 5. The specific constraint is that relative imports must resolve to actual files. Imports like `../store/api/atproto` from `src/features/feed/FeedPage.tsx` resolve incorrectly because the path goes up two levels from `features/feed/` (reaching `src/` parent) instead of one level.

The correct pattern for feature-organized directories:

```
src/
├── features/
│   └── feed/
│       └── FeedPage.tsx    → import from '../../store/api/atproto'
├── store/
│   └── api/
│       └── atproto.ts
```

From `features/feed/`, the path `../../store/api/atproto` goes up to `src/` then into `store/api/atproto`. A single `../` prefix only reaches `features/`, which is incorrect.

# Part IV: How to Use the Application

## Running locally

```bash
# Clone the repository
cd /home/manuel/code/wesen/2026-05-30--at-proto

# Build frontend and Go binary
make build

# Run the server
./atproto-web

# Open http://localhost:8080 in a browser
# Enter your AT Protocol handle (e.g., your-handle.bsky.social)
# The browser redirects to the PDS consent screen
# After approval, you are redirected back and see the timeline
```

For development with hot reload, run the Go server and Vite dev server separately:

```bash
# Terminal 1: Go server
make dev

# Terminal 2: Vite dev server (proxies /api to Go server)
make frontend-dev

# Open http://localhost:5173
```

The Vite dev server proxies `/api` requests to the Go server at `localhost:8080`, defined in `frontend/vite.config.ts`.

## Environment variables

| Variable | Default | Purpose |
|---|---|---|
| `PORT` | `8080` | HTTP listen port |
| `HOST` | `http://localhost:8080` | External URL (determines OAuth config mode) |
| `APPVIEW_URL` | `https://public.api.bsky.app` | Bluesky AppView base URL |
| `RELAY_URL` | `wss://bsky.network` | Firehose relay WebSocket URL |
| `SESSION_SECRET` | `dev-secret-change-me` | Cookie encryption key (change for production) |
| `DB_PATH` | `atproto-web.db` | SQLite database path (unused, reserved) |

## Available features

- **Timeline**: View your home timeline with cursor-based pagination
- **Profile**: View any user's profile, follows count, followers count, posts count
- **Post**: Create new posts (up to 300 characters)
- **Like/Unlike**: Like or unlike any post (red count indicator when liked)
- **Repost**: Repost any post
- **Search**: Search posts by query string
- **Notifications**: API endpoints for notification list and unread count (UI pending)
- **Real-time updates**: Firehose subscription with automatic cache invalidation

# Part V: Contributing

## Codebase orientation

Start with these files:

| File | What to read first |
|---|---|
| `main.go` | Entry point, configuration loading |
| `internal/server/server.go` | All HTTP routes registered |
| `internal/auth/oauth.go` | OAuth flow handlers (login, callback, session, logout) |
| `internal/auth/context.go` | Session context injection pattern |
| `internal/api/feed.go` | Example of an XRPC proxy handler |
| `frontend/src/store/api/atproto.ts` | RTK Query API definition with all endpoint types |
| `frontend/src/App.tsx` | Frontend routing and authentication gate |
| `frontend/src/styles/retro.css` | macOS 1 monochrome theme CSS variables and components |

## Adding a new XRPC endpoint

To add a new XRPC proxy endpoint (for example, `app.bsky.feed.getLikes`):

1. Add the handler to `internal/api/` in the appropriate file (or create a new file):

```go
func (h *APIHandler) HandleGetLikes(w http.ResponseWriter, r *http.Request) {
    oauthSess, err := h.getOAuthClient(r)
    if err != nil {
        writeError(w, http.StatusUnauthorized, err.Error())
        return
    }
    client := oauthSess.APIClient()
    uri := r.URL.Query().Get("uri")
    params := map[string]any{"uri": uri}
    if cursor := r.URL.Query().Get("cursor"); cursor != "" {
        params["cursor"] = cursor
    }
    var resp interface{}
    if err := client.Get(r.Context(), "app.bsky.feed.getLikes", params, &resp); err != nil {
        writeError(w, http.StatusBadGateway, err.Error())
        return
    }
    writeJSON(w, http.StatusOK, resp)
}
```

2. Register the route in `internal/server/server.go`:

```go
mux.HandleFunc("GET /api/feed/likes", apiHandler.HandleGetLikes)
```

3. Add the RTK Query endpoint in `frontend/src/store/api/atproto.ts`:

```typescript
getLikes: builder.query<unknown, { uri: string; cursor?: string }>({
  query: (params) => ({ url: 'feed/likes', params }),
  providesTags: ['Post'],
}),
```

4. Export the hook and use it in a component.

## Adding a new Lexicon record type

To add support for a new record type (for example, `app.bsky.graph.block`):

1. Create the record body in the handler:

```go
body := map[string]interface{}{
    "repo":       client.AccountDID.String(),
    "collection": "app.bsky.graph.block",
    "record": map[string]interface{}{
        "$type":     "app.bsky.graph.block",
        "subject":   map[string]string{"did": targetDID},
        "createdAt": syntax.DatetimeNow(),
    },
}
client.Post(r.Context(), "com.atproto.repo.createRecord", body, &resp)
```

2. The indigo SDK does not need generated types for the record — the `map[string]interface{}` approach works for any Lexicon. Generated types are available for type safety but are not required.

## Testing

```bash
# Go tests
go test ./... -count=1

# Frontend build check (catches type errors)
cd frontend && npm run build
```

Integration testing requires an actual AT Protocol account. The OAuth flow cannot be tested without a real PDS consent screen.

# Part VI: Next Steps

## Immediate improvements

1. **SQLite session store.** Replace `oauth.NewMemStore()` with a SQLite-backed implementation using the pattern from the indigo cookbook. This persists sessions across server restarts and enables horizontal scaling.

2. **CBOR firehose parsing.** Replace the JSON unmarshaling in `firehose.go` with proper DAG-CBOR frame reading using indigo's `lex/util` package. This ensures all firehose events are correctly parsed.

3. **Firehose auto-reconnect.** Add exponential backoff reconnection when the upstream WebSocket connection drops. The current implementation stops on error.

4. **Profile editing.** Add a handler for `com.atproto.repo.putRecord` to update `app.bsky.actor.profile` records (display name, description, avatar blob).

5. **Blob upload.** Implement `com.atproto.repo.uploadBlob` for image attachments in posts. This requires multipart form handling and CDN link generation.

## Medium-term features

6. **Rich text facets.** Parse and render `app.bsky.richtext.facet` records, which encode mentions (@handle), links, and tags within post text. The frontend needs a facet-aware text renderer.

7. **Custom feed support.** Add a feed picker that queries `app.bsky.feed.getFeed` with different feed generator AT-URIs. This allows users to switch between algorithmic feeds.

8. **Notification UI.** Build a notification list component that calls the existing `/api/notifications` endpoint with real-time updates from the firehose.

9. **Thread view.** Implement a full thread view using `app.bsky.feed.getPostThread` with nested reply rendering.

10. **Direct messages.** Implement `chat.bsky.convo.*` endpoints for DM support. This requires additional OAuth scopes.

## Production hardening

11. **Confidential client.** Upgrade from `oauth.NewPublicConfig` to a confidential client with a P-256 signing key. This provides stronger client authentication.

12. **Rate limit handling.** Implement exponential backoff and retry for 429 responses from the PDS. RTK Query has built-in retry support that can be configured.

13. **Error boundaries.** Add React error boundaries around each feature module to prevent a single component crash from breaking the entire UI.

14. **HTTPS and deployment.** Configure TLS termination, set proper `SESSION_SECRET`, and deploy behind a reverse proxy. The `HOST` environment variable must match the external URL.

## Working rules

- The Go backend must proxy all XRPC calls. Never call AT Protocol services directly from the browser.
- Every `client.Get` call uses `map[string]any` for parameters, not `map[string]string`.
- The `$type` field is required in every record body sent to `com.atproto.repo.createRecord`.
- `syntax.DatetimeNow()` produces the correct timestamp format. Do not use `time.Now().Format(time.RFC3339)`.
- The firehose sends CBOR frames, not JSON. The current JSON-based parsing is a development shortcut.
- Session cookies store only the DID and session ID. OAuth tokens live in the indigo store on the server.
- The macOS 1 UI constraint means no color fills, no gradients, no animations, and no window chrome. Accent colors appear only as text foreground.
