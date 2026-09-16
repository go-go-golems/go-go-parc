---
title: "Slack Support for discord-bot — Complete Branch Deep Dive"
aliases:
  - Slack Bot Branch Deep Dive
  - discord-bot Slack Port Full Analysis
tags:
  - project
  - article
  - go
  - javascript
  - slack
  - socket-mode
  - goja
  - block-kit
  - sqlite
  - ci
status: active
type: project
created: 2026-09-16
repo: /home/manuel/workspaces/2026-09-10/add-slack-support/discord-bot
code_revision: 1bda64f
branch: task/add-slack-support
tickets:
  - DISCORD-SLACK-001
  - SLACK-CREDENTIALS-001
  - SLACK-UI-001
  - SLACK-PORT-001
---

# Slack Support for discord-bot: The Complete Branch

The branch `task/add-slack-support` adds a second platform to a repository that previously spoke only Discord. It contains 53 commits over `main`, changes 676 files, and inserts roughly 110,000 lines including archived documentation and ticket artifacts. The result is not a translation layer. It is an independent Slack runtime — Go owns the process, the credentials, the network, and the databases; JavaScript owns the bot definitions and their handler behavior, exposed through a typed, capability-scoped module named `slack`.

This report is the fourth and final deep dive in a series. It covers the branch as a whole at revision `1bda64f`. Three earlier reports documented the runtime and credential installation work ([[PROJECT REPORT - Discord Bot Slack Support - Deep Dive Technical Analysis]]), the offline runtime's ownership and admission model ([[PROJ - Slack Bot - Runtime Ownership Admission and Local Verification]]), and the native UI DSL with interaction acknowledgments and manifest synchronization ([[PROJ - Slack Bot - Native UI ACKs and Manifest Synchronization]]). This report adds what those documents could not yet describe: the port of all thirteen example bots, the operational service surface, live installation switching, the credential redaction of Git history, and the reproducible validation pipeline that now gates every push.

> [!summary]
> - The branch delivers a complete Go+Goja Slack runtime: discovery, manifest generation, app creation, developer installation, Socket Mode ingress, a Block Kit UI DSL, an allowlisted Web API service surface, and lifecycle-owned SQLite persistence.
> - All thirteen Discord example bots were ported to native Slack workflows; 167 literal source-handler mappings and 181 native registration expectations are machine-checked.
> - Live operation was validated by installing and switching between the Poker and Hater bots in a real workspace, after the manifest synchronization gate correctly blocked startup on permission changes.
> - Documentation token examples were removed from outgoing Git history with `git-filter-repo`, and the ancestry was rebased back onto upstream `main` to eliminate artificial merge conflicts.
> - Local validation is now blocking and reproducible: pinned golangci-lint, GoSec, govulncheck, a module-matched glazed-lint, lefthook hooks, and CI that runs the same Makefile checks.

## 1. What the branch contains

The work was organized into four docmgr tickets, each with an archived design document, a chronological diary, Defuddle-captured official Slack documentation, and evidence artifacts:

| Ticket | Scope | Key deliverables |
| --- | --- | --- |
| `DISCORD-SLACK-001` | Architecture research, offline runtime, SDK probe, `bots run-local` | Intern guide, `pkg/slackbot`, `internal/jsslack`, `pkg/slackhost`, `pkg/slackcli`, `internal/slacktransport`, mock-based SDK interop proof |
| `SLACK-CREDENTIALS-001` | Local credentials, app creation, developer installation, live `bots run` | `internal/slackconfig` store, `create_app`, `install_app`, `profiles`, `run_remote`, live ping app installation |
| `SLACK-UI-001` | Slack surfaces research, Block Kit DSL, interaction ACKs, manifest sync | `internal/jsslack/ui_elements.go`, `ui_module.go`, single-use modal ACK, `update_manifest`, wire-level showcase regression |
| `SLACK-PORT-001` | Port of all thirteen example bots | Persistence, named operational services, user-token boundaries, acceptance matrix, operations handoff, cursor-cycle rejection |

The package layout separates three concerns that the earlier reports introduced one at a time. Domain contracts and admission live in `pkg/slackbot` (values, validation, ingress, the named operation allowlist). VM integration lives in `internal/jsslack` (module registration, UI builders, dispatch, database ownership, local verbs). Transport and operational side effects live in `internal/slacktransport` (Socket Mode client, Web API operations, external file upload). Public composition lives in `pkg/slackhost`, the CLI in `pkg/slackcli`, and user-facing documentation in `pkg/slackdoc`. No package imports the Discord runtime.

## 2. The runtime model, restated precisely

A Slack bot process is one Goja virtual machine per bot, loaded from one JavaScript entry file under `examples/slack-bots/`. The file calls `defineBot` and receives registration functions:

```javascript
const { defineBot } = require("slack"),
  ui = require("slack/ui");

module.exports = defineBot(
  ({ configure, command, event, action, view, options, shortcut }) => {
    configure({
      name: "ping",
      description: "Commands, native controls, modals, search and generated files",
      scopes: ["files:write"],
      run: { fields: { greeting: { type: "string", default: "pong" } } },
    });
    command("/golem-ping", { description: "Check the development bot" },
      async (ctx) => ui.message(ctx.config.greeting)
        .block(ui.header("Pong"))
        .block(ui.section(ui.plain("JavaScript handled this slash command.")))
        .build());
  });
```

Three facts about this model carry most of the design weight:

- **One bot per process.** Discovery can enumerate all bots offline, but `bots run` loads exactly one. This keeps identity, credential selection, and manifest synchronization unambiguous: the running process is the installed app for one bot's configuration.
- **Configuration is declared, not discovered.** `configure.run.fields` declares which JSON keys `--bot-config-file` may project into `ctx.config`. Host credentials never come from that file. Inspection (`bots inspect`) lists the declared fields without requiring their values; running requires them.
- **The VM owner is single-threaded and Go keeps it.** JavaScript runs only on the owner goroutine. Outbound Web API calls decode their parameters on the owner, execute in a bounded errgroup, and return to the owner for promise settlement. A cancellation watcher interrupts the VM between entries; a CPU-bound handler loop is therefore terminable, while a single VM entry is never preempted mid-instruction.

Ingress admission is bounded and typed. The queue capacity is 32 envelopes; deduplication retains 4096 business-event identities for five minutes; the ACK context is two seconds; the HTTP client timeout is ten seconds. Admission is keyed on business-event identity, not connection delivery identity, because Socket Mode may redeliver an event under a new envelope. Queue insertion precedes the acknowledgment call, so a worker may begin before the ACK is observed on the wire — the guarantee is ACK independence from handler progress, not strict ACK-before-handler ordering. When the queue is full, ingress emits an explicit overload receipt rather than silently dropping work.

## 3. The interaction acknowledgment protocol

Slack requires nearly every interaction to be acknowledged within seconds. The branch implements a single-use acknowledgment capability for interactions that produce payload responses (modal submissions, external select suggestions, view updates), while ordinary commands and actions keep immediate ACK behavior.

```text
interaction arrives
  → decoder produces slackbot.Interaction
  → host invokes the registered JS handler on the owner
  → handler receives an `ack` capability: exactly one of
      ack()            → empty semantic ACK
      ack.response(view) → ACK payload opens/updates a modal
      ack.options([...]) → ACK payload answers a suggestion query
  → deadline elapses or handler returns → unreceived ACK is sent as empty
```

The decision is one-shot: a second `ack` call is an error, and a handler that never calls `ack` receives an empty ACK at the deadline. Suggestions must enter this explicit path because the automatic ingress acknowledgment would otherwise discard their response payload — this was the failure mode the routing implementation fixed. Modal duplicate handling deliberately preserves the original semantic ACK, because an empty duplicate ACK can accept an invalid form.

Response-URL delivery has its own wire subtlety discovered during the port: replacing an original message must omit `response_type`, or the replacement inherits ephemeral visibility from ordinary replies. A regression test (`TestShowcaseWireDoesNotReplyPong` and its successors in `internal/slacktransport`) verifies this at the byte level on a real local WebSocket fixture.

## 4. The service surface: named operations, not raw HTTP

JavaScript handlers reach Slack through `ctx.slack.*` — a finite, allowlisted set of named operations defined in `pkg/slackbot/operations.go` and implemented in `internal/slacktransport/operations.go`. A script cannot construct an arbitrary Web API call, cannot see a token, and cannot attach the bot Authorization header to third-party URLs.

The surface covers messages (post, post ephemeral, update, delete), conversations (history with pagination cursors, info, list, members, join, leave, kick, setTopic, archive), users (lookup, list, change events), user groups (list, read-modify-write membership), pins, reactions, workspace info, permalinks, and generated-file upload. External file upload uses the two-step `files.getUploadURLExternal`/`files.completeUploadExternal` sequence with a token-free content transfer whose destination is checked; generated files are UTF-8 and limited to 8 MiB.

Two identity boundaries are explicit. First, Slack user groups are membership lists, not Discord permission roles: membership updates read the current members and send the complete replacement list, because Slack's API replaces membership rather than appending. Concurrent external group changes can race this operation, and the guide says so. Second, user-token operations (`useUserToken: true`, `deleteAsUser`, `setMembersAsUser`) are deliberately selected, never silently substituted. Workspace removal (`/mod-remove-workspace-user`) requires a third gate: `enableWorkspaceRemoval: true` plus a separately imported Enterprise user token with `admin.users:write`. The normal developer installation produces bot and Socket Mode tokens only, so that operation is structurally unreachable in a default setup.

SQLite persistence reuses the existing go-go-goja database module, registered once per host, restricted to `sqlite3` and handler-time access. The host opens no database during inspection, and closes owned connections after runtime shutdown. Every persistent table in the ported examples carries a workspace key, so one database file can serve multiple workspaces without cross-contamination.

## 5. The thirteen ports

The port inventory (`SLACK-PORT-001`) started from 156 source handler registrations across the Discord examples and produced 167 literal source-to-Slack mappings, machine-checked against 181 native registration expectations in `pkg/slackcli/port_inventory_test.go`. Each example was re-expressed with Slack-native controls rather than approximated:

| Bot | What the port demonstrates |
| --- | --- |
| ping | commands, buttons, static selects, modals, external-select search, generated report files |
| hater | humor controls, apology modal form, verdict flow (live-tested) |
| interaction-types | text-parsed command arguments, message shortcuts, avatar display |
| announcements | Block Kit announcement preview |
| unified-demo | local verbs (`bots invoke`), run-metadata, redacted API key values |
| poker | pure card/ranking algorithm reuse, workspace/channel/user-scoped rounds (live-tested) |
| support | channel/thread operations, drafts, private follow-ups |
| custom-kb | SQLite link store, workspace-scoped uniqueness, selection and refresh |
| knowledge-base | capture, review, editing, pagination, export, reaction promotion with reviewer authorization |
| show-space | manager authorization, announcement publication with exact pin references, cancellation |
| archive-helper | cursor pagination, attachment links, external file upload, cycle rejection |
| moderation | message/channel/member/group operations, explicit token boundaries, conditional workspace removal |
| ui-showcase | cards, pagers, forms, selects, aliases, review flows |

Three porting decisions deserve explanation because they record platform differences rather than implementation shortcuts:

**Discord slash options became text parsing plus forms.** Slack delivers command arguments as a text string. Where Discord offered structured options and autocomplete, the ports either parse text explicitly or open a suggestion form; search commands accept text for direct results or open the form when text is omitted. Slack has no native equivalent of slash-option autocomplete, so the acceptance matrix records its absence instead of emulating it incorrectly.

**Moderation semantics diverged where the platforms diverge.** Discord timeouts, bans, channel slowmode, and role hierarchies have no same-semantics Slack operations. The matrix records what exists: message deletion, group membership replacement, and — behind separate gates — workspace removal. Thread membership differs too: Slack threads are replies to messages, not independently joinable channels, so the Support bot names its channel join/leave operations explicitly.

**Pagination is explicit and fail-closed.** Archive Helper fetches history page by page with `next_cursor`. Message deduplication alone does not prove progress, so the implementation tracks every returned cursor per export and rejects any repeat. The follow-up fix (Step 9 of the port diary) closed the case where consecutive-duplicate detection missed an A/B/A cycle: because duplicates were already excluded, such a cycle could fetch until the invocation timeout. Now any repeated cursor fails the export before permalink generation or upload, and tests cover consecutive repetition, A/B/A cycles, and mid-page rate-limit errors, each asserting that no partial file is ever published.

## 6. Live operation: install, switch, and verify

The live story began with the `ping` app (`A0C1UJMCPGA` installed in workspace `T0C1UJMCPGA`, profile `go-go-golems`) and progressed through the UI showcase. During the port phase, live operation switched twice, each time through the same gate:

1. `bots run poker --profile go-go-golems` — manifest synchronization updates the app, detects `permissions_updated: true`, and stops with reinstall instructions.
2. `bots install poker --profile go-go-golems --team-id T0C1UJMCPGA` — completes and stores the installation without printing tokens.
3. Restart — manifest reports `permissions_updated: false`, `auth.test` succeeds, Socket Mode connects, hello arrives.

The same sequence switched the installation to Hater. The important property is that the gate is active: the runner will not connect with a stale manifest, and a changed permission set always forces a deliberate reinstall before the process reaches Slack.

A live debugging episode from `SLACK-UI-001` remains instructive. The user observed an unexpected `pong` reply whose generating code path was never identified. The investigation added a wire-level regression that loads discovery, runs the showcase, and replays both `/golem-ping` and `/ui-showcase` over a real local WebSocket, capturing both ACK payloads and response-URL HTTP messages with SHA-256 text fingerprints (no message bodies or credentials in logs). The test proved the showcase does not reply pong in that sequence, and the manifest export showed `/golem-ping` absent from the installed app — but the diary explicitly records the root cause as unresolved rather than claiming the observation was disproved. Reproducing the exact wire payload required one non-obvious fix: the pinned slack-go `SlashCommand.UnmarshalJSON` demands `is_enterprise_install` even when false, so a fixture matching only the framework's normalized shape never reaches the decoder.

## 7. History redaction and ancestry repair

Pushing the branch triggered GitHub's secret protection: archived documentation copies contained Slack token and webhook examples. The cleanup had two stages, and the second stage exists because the first was incomplete.

First, every reachable historical blob was scanned without printing credential values. Three distinct documentation values were replaced with `SLACK_REDACTED_EXAMPLE` using `git-filter-repo` exact-value replacement, confined to seven archived reference files. The synthetic transport-test URLs were retained deliberately — they validate host behavior and are not credentials.

Second, the filter had also rewritten shared ancestry: the rewritten upstream tip had a tree identical to upstream `main` but a different commit identity, which produced artificial merge conflicts in `README.md`, `go.mod`, `.gitignore`, and the ticket vocabulary. The repair replayed all 50 feature commits onto the real upstream base:

```sh
git rebase --onto upstream/main 4e8cfcc task/add-slack-support
```

The rebased tip's tree was verified identical to the prior sanitized tip, the merge base became the actual `ff70844`, and a rescan confirmed only the synthetic test URL remained. The lesson is recorded in the diary: limit history replacement to feature ancestry, or restore the unchanged upstream base before publishing a filtered branch. Historical hashes in earlier diary entries describe pre-redaction checkpoints and no longer identify the rewritten commits.

## 8. Reproducible validation

The final phase (PR 19 review plus hook/CI alignment) fixed two operator-facing defects and made every local gate blocking and pinned:

- A failed `create-app` call left an empty reserved credential file, so a corrected retry failed on the exclusive-create check. Cleanup is now armed until write and close both succeed; a later stdout/profile error preserves saved credentials.
- The guide advertised a nonexistent `profiles list` subcommand; the actual root command is `slack-bot profiles`, now tested as shipped.
- `golangci-lint` v2.11.2, GoSec v2.29.0, and `govulncheck` v1.8.0 are pinned. The single GoSec suppression (`G703` on the CLI's repository-root stat) is documented at the call site as an operator-selected local path, not a remotely supplied one.
- `glazed-lint` is built from the exact `go.mod` version (Glazed v1.3.6) rather than a shared binary, and it no longer silently falls back to an older version when the build fails. The earlier workspace-checkout drift — a newer Glazed API causing `undefined: settings.NewGlazedSchema` failures under `go.work` — is the failure mode this prevents.
- `make check` runs the full module-isolated pipeline (`GOWORK=off`, `GOFLAGS=-buildvcs=false` for linked worktrees); lefthook makes pre-commit run lint/logger checks and matching tests, and pre-push run blocking `make check`. Generation and release steps are explicit commands, never implicit hook side effects — an earlier release hook mutated `go.mod`/`go.sum` and generated files concurrently with tests.
- CI runs the same Makefile checks, verifies generated logcopter loggers are current, and includes an offline Slack discovery smoke test. Go moved to 1.26.6 and the vulnerable transitive modules were upgraded; `make govulncheck` now reports zero reachable vulnerabilities, with the remaining advisories confined to imported-but-uncalled packages.

The day-to-day verification commands remain the ones the earlier reports established:

```sh
go run ./cmd/slack-bot bots list
go run ./cmd/slack-bot bots inspect knowledge-base
go run ./cmd/slack-bot bots manifest knowledge-base
go run ./cmd/slack-bot bots simulate ui-showcase \
  --event-file examples/slack-bots/fixtures/ui-view.json
go run ./cmd/slack-bot bots invoke unified-demo status
go run ./cmd/slack-bot bots run poker --profile go-go-golems --log-level debug
```

## 9. What the evidence does and does not establish

The branch is disciplined about evidence levels, and a reader of the tickets should preserve that discipline. Offline tests prove registration, payload construction, dispatch, admission, persistence, and failure semantics against fixtures and a pinned stateful mock. Wire-level regressions prove exact ACK behavior and response encoding over a real local WebSocket. The acceptance matrix proves registration parity for 167 source handlers; it does not certify live platform behavior. Live installation and switching of Poker and Hater proves manifest synchronization, installation, authentication, and Socket Mode connectivity; full workflow qualification of every port still requires deliberate user interaction in the workspace, and the moderation/administrative operations depend on actual plan, token scopes, and actor rights that no mock can establish.

Known open boundaries at revision `1bda64f`:

- The unexpected live `pong` remains without an identified root cause; the reproduction is in place for the next occurrence.
- Nine golangci-lint findings and seven glazed-lint raw-flag declarations in preexisting credential commands were recorded as existing debt, alongside module-level advisories in uncalled packages.
- Rate limits fail operations rather than retrying; there is no method-scoped pacing, durable admission, or reconnect-recovery catalog. Reconnection is inherited from the SDK without an acceptance test of its failure modes.
- Public-channel message subscriptions cover edit/delete subtypes, but broader event coverage beyond the ported examples is not claimed.

## 10. How to resume this work

The four tickets carry resumable state in their diaries and acceptance matrices. The next concrete steps, in the order the evidence supports:

1. Exercise the remaining untested ports live, one bot per process, through the existing manifest-sync/reinstall gate.
2. Complete the source-handler acceptance review for any workflow whose live behavior has not been observed, and record results in `SLACK-PORT-001/reference/02-source-handler-acceptance-matrix.md`.
3. Capture the next live occurrence of the unexplained pong with the fingerprinting already in place.
4. Address the recorded lint and dependency debt in a separate change, keeping the validation pipeline blocking.
5. Treat rate-limit policy, reconnect acceptance, and durable admission as design questions, not defaults; the current fail-closed behavior is a deliberate contract, and any relaxation should be as explicit as the cursor-cycle rejection was.

The branch demonstrates a repeatable method: research with archived sources before design, offline implementation with fakes before transport, a real SDK probe before transport code, wire fixtures before live operation, machine-checked inventories before parity claims, and blocking local checks that CI can reproduce exactly. Each layer of that method is documented well enough for an intern to extend it — which was the first requirement the project set for itself.

## Related

- [[PROJECT REPORT - Discord Bot Slack Support - Deep Dive Technical Analysis]] — runtime and credential installation
- [[PROJ - Slack Bot - Runtime Ownership Admission and Local Verification]] — offline runtime, ownership, admission
- [[PROJ - Slack Bot - Native UI ACKs and Manifest Synchronization]] — UI DSL and interaction ACKs
- Repository: `/home/manuel/workspaces/2026-09-10/add-slack-support/discord-bot`
- Tickets: `ttmp/2026/09/{10,14,15}/` — `DISCORD-SLACK-001`, `SLACK-CREDENTIALS-001`, `SLACK-UI-001`, `SLACK-PORT-001`
