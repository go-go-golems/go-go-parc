---
title: Smailnail IMAP and Sieve Expansion Report
aliases:
  - Smailnail IMAP and Sieve Work
  - Smailnail IMAP/Sieve Today Report
tags:
  - project
  - smailnail
  - imap
  - javascript
  - sieve
  - email
  - mcp
  - report
status: active
type: project
created: 2026-03-19
repo: /home/manuel/workspaces/2026-03-08/update-imap-mcp/smailnail
ticket: SMN-20260319-IMAP-SIEVE
---

# Smailnail IMAP and Sieve Expansion Report

> [!summary]
> 1. Today’s work turned the research ticket into a shipped IMAP and Sieve runtime expansion for `smailnail`.
> 2. The code now includes a reusable mail runtime core, a richer JS service/module layer, and starter-friendly examples and docs.
> 3. The only intentionally open item is durable hosted-account Sieve schema support.

## What Was Built Today

The feature moved from analysis into implementation in three layers.

First, a reusable runtime core was added in `pkg/mailruntime` by porting the donor IMAP and ManageSieve logic from `remarquee/pkg/mail`. That gives `smailnail` a proper internal boundary for protocol handling instead of keeping the transport logic inside the JS wrapper.

Second, `pkg/services/smailnailjs` was expanded so JavaScript callers can work with a real mailbox/session API. The new service layer supports mailbox listing, status, searching, message fetches, flag mutation, move/copy/delete/expunge, append, and a separate Sieve connection path.

Third, `pkg/js/modules/smailnail` was expanded to expose those capabilities to goja scripts. The JS runtime now has a practical IMAP automation surface plus a Sieve builder and Sieve session methods.

## What New Contributors Can Use Immediately

### IMAP session

```javascript
const smailnail = require("smailnail")
const svc = smailnail.newService()
const session = svc.connect({
  accountId: "acc_123",
  mailbox: "INBOX"
})

try {
  const uids = session.search({ unseen: true, subject: "invoice" })
  const messages = session.fetch(uids, ["uid", "flags", "body.text"])
  session.addFlags(uids, ["\\Seen"])
  session.move(uids, "Processed/Invoices")
  return messages
} finally {
  session.close()
}
```

### Mailbox inspection

```javascript
const boxes = session.list()
const status = session.status("Archive")
const selected = session.selectMailbox("Archive", { readOnly: true })
```

### Append a raw message

```javascript
const uid = session.append([
  "From: user@example.com",
  "To: user@example.com",
  "Subject: Draft from smailnail",
  "",
  "Hello from append."
].join("\r\n"), {
  mailbox: "Drafts",
  flags: ["\\Draft"]
})
```

### Build and upload Sieve

```javascript
const script = svc.buildSieveScript((s) => {
  s.require(["fileinto"])
  s.if(s.headerContains("Subject", "invoice"), (a) => {
    a.fileInto("Invoices")
    a.stop()
  })
})

const sieve = svc.connectSieve({
  server: "sieve.example.com",
  username: "user@example.com",
  password: "secret"
})

try {
  sieve.check(script)
  sieve.putScript("main", script, { activate: true })
  return sieve.listScripts()
} finally {
  sieve.close()
}
```

## The Open Item

The remaining open item is hosted-account Sieve schema support.

What works now:

- inline Sieve connections work,
- `connectSieve({ accountId })` works,
- the current code defaults Sieve settings from the stored IMAP account when no dedicated Sieve settings exist.

Why it is still open:

- the hosted account model does not yet store Sieve-specific fields,
- some providers may use different Sieve host/port/credential settings than IMAP,
- the final schema decision should be made deliberately instead of rushed into the runtime.

In practice, that means today’s feature is usable, but the account-backed Sieve contract is still partially inferred from IMAP settings instead of being stored explicitly.

## What Changed In Code

- [pkg/mailruntime/imap_client.go](/home/manuel/workspaces/2026-03-08/update-imap-mcp/smailnail/pkg/mailruntime/imap_client.go)
- [pkg/mailruntime/sieve_client.go](/home/manuel/workspaces/2026-03-08/update-imap-mcp/smailnail/pkg/mailruntime/sieve_client.go)
- [pkg/services/smailnailjs/service.go](/home/manuel/workspaces/2026-03-08/update-imap-mcp/smailnail/pkg/services/smailnailjs/service.go)
- [pkg/js/modules/smailnail/module.go](/home/manuel/workspaces/2026-03-08/update-imap-mcp/smailnail/pkg/js/modules/smailnail/module.go)
- [pkg/js/modules/smailnail/docs/service.js](/home/manuel/workspaces/2026-03-08/update-imap-mcp/smailnail/pkg/js/modules/smailnail/docs/service.js)
- [pkg/js/modules/smailnail/docs/examples.js](/home/manuel/workspaces/2026-03-08/update-imap-mcp/smailnail/pkg/js/modules/smailnail/docs/examples.js)

## Validation

These checks passed during the work:

```bash
go test ./pkg/mailruntime ./pkg/services/smailnailjs ./pkg/js/modules/smailnail ./pkg/mcp/imapjs -count=1
docmgr doctor --root ttmp --ticket SMN-20260319-IMAP-SIEVE --stale-after 30
```

## Commit Trail

- `439258f` `Add shared IMAP and Sieve runtime core`
- `e66bd45` `Expand smailnail JS IMAP and Sieve APIs`
- `bc4baaa` `Record IMAP and Sieve implementation ticket progress`
- `c6fd9c6` `Expand starter documentation and examples`
- `886b6d5` `Record starter-doc expansion in ticket`
- `aff89b9` `Add project report for today's work`

## Related Notes

- [[PROJ - Smailnail Hosted Identity, Terraform, and Claude Fix]]
- [[PROJ - Smailnail OIDC Identity and Hosted Auth]]
- [[PROJ - Smailnail Hosted Backend and SPA]]
- [[Projects/2026/03/19/PROJ - Remarquee - reMarkable Toolkit]]
- SMN-20260319-IMAP-SIEVE ticket workspace in `smailnail/ttmp/2026/03/19/SMN-20260319-IMAP-SIEVE--expand-js-imap-with-remarquee-mail-package-and-add-sieve-scripting/`

## Why This Matters

This work closes a major gap between the hosted/backend side of Smailnail and the JavaScript runtime side. The runtime is no longer just a rule-builder wrapper. It is now a practical mailbox automation surface with a Sieve entrypoint, and the docs are finally broad enough for someone to start using it without reading the whole codebase first.
