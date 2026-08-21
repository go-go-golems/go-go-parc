---
title: GEC Ads Attribution - Google Ads Importer (Phase 3)
aliases:
  - GEC Ads Attribution Phase 3
  - GEC Google Ads Importer
  - importGoogleAds.php
tags:
  - project
  - gec
  - php
  - google-ads
  - api-integration
  - attribution
  - phpunit
status: active
type: project
created: 2026-08-21
publish: false
repo: /home/manuel/workspaces/2026-08-19/add-ad-tracking-gec/goldeneaglecoin.com
ticket: GEC-ADS-ATTRIBUTION-001
---

# GEC Ads Attribution - Google Ads Importer (Phase 3)

Phase 3 of GEC-ADS-ATTRIBUTION-001 connects goldeneaglecoin.com to the Google Ads API: campaign spend and performance flow into `google_ads_campaign_daily`, captured gclids resolve to campaigns through `google_ads_click_lookups`, and the nightly attribution job (phase 4) fills `campaign_id` on order attributions from those lookups. This report covers the credential model, a deliberate departure from the design document on the client library, the import pipeline's idempotency and retention guarantees, the inverted query model that `click_view` forces, and an operational incident: discovering mid-build that a concurrent review session had left the worktree on the pull-request branch.

> [!summary]
> - The Google Ads API requires three credentials with distinct roles: a developer token (the application may call), an OAuth refresh token (as this user), and a customer id (about this account). Two of three are in SSM; the importer is deployable now and activates when the refresh token arrives.
> - The official `googleads/google-ads-php` library was rejected in favor of a ~200-line REST client: three read-only GAQL queries do not justify a generated protobuf tree, and the REST surface is plain JSON.
> - `click_view` cannot be filtered by gclid and answers only single days within a 90-day window, so the resolver inverts the query: fetch whole days, match in memory, and track three terminal states (resolved / not_found / expired) so the pending set always shrinks.
> - Concurrent sessions share worktrees: a review session left the checkout on the PR branch and the first phase 3 commits landed there. Nothing was pushed; the work moved to `task/google-ads-importer`.

## The credential model

Google Ads API authentication decomposes into three independent credentials, and understanding their separation explains both the provisioning design and what "we have a developer token" does and does not unlock.

The **developer token** authorizes the *application*: it is issued per manager (MCC) account through the API Center and says that requests bearing it may use the API at all. It grants access to no account's data. Fresh tokens start at "test account" access level — usable only against Google's test accounts — and reach production data through a reviewed Basic-access application.

The **OAuth refresh token** authorizes the *user*: API requests execute with the permissions of the Google login that granted consent. A refresh token is generated once (an OAuth consent flow against the client id/secret of a Google Cloud OAuth client) and then exchanged for short-lived access tokens on every run. Because the token dies with the account that granted it, it should belong to a role account, not a person.

The **customer id** selects the *account*: which Ads account a query reads. When access is routed through a manager account, the manager's id travels as a `login-customer-id` header alongside.

The provisioning path mirrors the codebase's existing secret handling: parameters live in AWS SSM (`/googleads/developer_token`, `/googleads/client_secret` as SecureString, `/googleads/client_id` as String), and provisioning renders them into the gitignored `config.ini [googleads]` section, the same pattern `step-install-postfix.sh` uses for the SMTP password. At the time of writing the developer token and OAuth client are stored; the refresh token, MCC id and customer ids are outstanding. The code is structured so this is not blocking: `importGoogleAds.php` exits 0 silently while `googleads.enabled` is unset, so the crontab entries can deploy before the credentials are complete.

## The library decision

The design document specifies `composer require googleads/google-ads-php`. The implementation deviates, and the reasoning deserves a full statement because the deviation is the kind that looks like corner-cutting until the alternative is examined.

The official library is built around gRPC: it ships the generated protobuf classes for every resource and service in the API surface — thousands of files — plus a transport layer that prefers the `grpc` PHP extension (not installed on the GEC servers) and falls back to REST. The importer needs exactly three read-only GAQL queries. Over the API's documented REST surface, a GAQL query is one JSON POST to `customers/{cid}/googleAds:searchStream` with three headers; the OAuth exchange is one form POST. The complete client — token refresh with expiry caching, `searchStream` with batch flattening, `listAccessibleCustomers`, error extraction from both single-object and batch-array error shapes — is about two hundred lines (`src/lib/GoogleAds/Client.php`).

The cost of owning this client is version maintenance: Google sunsets API versions roughly yearly, and with the official library a version bump is a composer update, while here it is a config value (`googleads.api_version`, default `v21`) because the version only appears in URLs. The benefit is no dependency with a footprint two orders of magnitude larger than the code using it, no grpc concerns, and a transport that tests can stub by overriding one method. The trade was taken knowingly and is recorded as a design delta; if the project ever needs mutations (phase 7's conversion uploads) the decision should be revisited, since write paths deserve the official library's request validation.

Network I/O is isolated behind three protected methods (`postJson`, `getJson`, `postForm`). The test suite's `StubGoogleAdsClient` overrides `searchStream` wholesale and records the GAQL it was asked, which lets integration tests assert not just results but query behavior — for example, that a second `click_view` run issues zero API queries.

## The data model

Five tables (design doc §11.3), each with a distinct retention role:

| Table | Role | Key property |
|---|---|---|
| `google_ads_campaign_daily` | The fact table: one row per customer × campaign × date × device segment | `UNIQUE uq_gacd` makes import an idempotent upsert |
| `google_ads_campaigns` | Slowly changing dimension of campaign name/settings | `valid_to IS NULL` marks the current row; renames close-and-open |
| `google_ads_import_runs` | Audit: every importer execution with counters and status | Mirrors `attribution_runs`; feeds the phase 5B status page |
| `google_ads_raw_reports` | What the API actually returned, per chunk (gz + base64 JSON) | Mapper bugs are recoverable without re-fetching |
| `google_ads_click_lookups` | gclid → campaign resolution results | Three-state `resolution_status`; unique per gclid |

Two conventions carried over from the earlier phases: money never stays in micros (`cost_micros / 1e6` at mapping time, rounded to cents), and every table gets `created_at`/`updated_at` which php-activerecord maintains — except that the multi-row upsert writes them itself with `UTC_TIMESTAMP()` because it bypasses the model layer for throughput.

One ActiveRecord detail cost a model attribute: the class `GoogleAdsCampaignDaily` would pluralize to `google_ads_campaign_dailies`, so the model pins `static $table_name = 'google_ads_campaign_daily'`.

## The import pipeline

`Importer::campaignDaily()` walks the requested range in calendar-month chunks. Chunking serves two goals: a failure loses one chunk rather than a decade of backfill, and response payloads stay bounded. Per chunk the sequence is fixed — fetch, map, retain raw, upsert, track dimension:

```php
foreach (self::monthChunks($from, $to) as [$a, $b]) {
    $apiRows = $this->client->searchStream($customerId, Queries::campaignDaily($a, $b));
    $rows = array_map(fn ($r) => RowMapper::campaignDaily($r, $customerId), $apiRows);
    // raw retention first: if the upsert fails, the evidence survives
    GoogleAdsRawReport::create([... GoogleAdsRawReport::pack($rows) ...]);
    $upserted += $this->upsertDaily($rows, $run->id);
    $this->trackDimension($rows);
}
```

The upsert is a single multi-row `INSERT … ON DUPLICATE KEY UPDATE` against the `uq_gacd` unique key. Idempotency here is not merely a convenience: Google restates conversion metrics for up to the conversion window (30–90 days) after the click, so the nightly import always re-imports a trailing window (`googleads.restate_days`, default 60) and *must* overwrite rows it has written before. The same mechanism makes re-running a failed backfill safe. Rows outside the restate window are never touched except by explicit backfill — which, together with the raw table, satisfies the spec's "store original values" requirement.

`trackDimension()` maintains the campaign dimension: for each campaign's newest report row in the batch, compare six fields (name, type, status, bid strategy, targets) against the current dimension row; on any difference, stamp `valid_to` on the old row and open a new one. The dimension exists because campaign *names* are how humans read reports, names change, and a fact table that stores only ids forces every report through a join that can only ever show the current name. With validity intervals, phase 5B reports can label historical spend with the name the campaign had at the time.

## click_view and the inverted query

Resolving a gclid to a campaign would naturally be a keyed lookup: given this click id, which campaign produced it? The `click_view` resource does not support that shape. It answers only queries filtered to exactly one `segments.date`, returns every click of that day, and holds only the last 90 days.

The resolver therefore inverts the problem. `pendingGclidsByDate()` collects our own unresolved gclids — captured in `visitor_touches`, absent from `google_ads_click_lookups` — grouped by click date. For each distinct date, the whole day is fetched once and matched in memory against the pending set. The cost model follows: one API query per distinct pending date, regardless of how many gclids that day holds, and zero queries when nothing is pending.

Every pending gclid ends in one of three terminal states, and the distinction keeps the pending set monotonically shrinking:

- **resolved** — found in the day's clicks; campaign, ad group and ad id stored (the ad id is parsed from the `adGroupAd` resource name, `customers/N/adGroupAds/{group}~{ad}`).
- **not_found** — the day was queried but the gclid was absent. The row is written but *retried on later runs* (upsert refreshes non-resolved rows), because Google's click data can lag capture by hours.
- **expired** — the touch is older than the 90-day window and was never resolved; it can never be resolved, and the explicit row prevents it from being re-queried forever.

The integration test pins the operational consequence: after one run resolves, marks not-found and expires the fixture gclids, a second run issues zero API queries.

The design document's recommendation stands unchanged and is worth restating: the account-level tracking template (`utm_campaign={campaignid}`) removes the click_view dependency entirely for future clicks, because the campaign id then arrives in the UTMs our capture pipeline already stores. click_view resolution is the fallback for clicks without it — including all clicks from before the template is set.

## Wiring into the nightly job

The phase 4 attribution job resolves campaign ids in two steps now (design doc §14 rule 5): `Rules::resolveCampaignId` handles the no-API case (numeric `utm_campaign` from the tracking template); when that yields nothing and the credited touch carries a gclid, `GoogleAdsClickLookup::resolvedFor()` supplies campaign, ad group and customer ids, and `GoogleAdsCampaign::currentFor()` supplies the display name.

Three invariants had to hold simultaneously, and each guards against a distinct failure:

1. The four enrichment fields (`campaign_id`, `campaign_name`, `ad_group_id`, `google_customer_id`) are always present in the recomputed attribute array — otherwise the change detector reads undefined keys.
2. They are members of the change-detection field list — otherwise a lookup arriving *after* an order's first v1 attribution would compute new values that the "unchanged, skip" branch throws away, and enrichment would never persist.
3. They are preserved from the stored row when the recomputation resolves nothing — otherwise any re-run after touch data drifted would erase enrichment the importer had provided.

Scheduling encodes the data dependency: the crontab now imports at 06:30 (campaign_daily) and 06:45 (click_view) — after Google's "yesterday" stabilizes — and the attribution job moved from 01:30 to 07:00 so each night's attribution sees that night's lookups.

## The concurrent-session incident

Mid-build, two anomalies appeared in sequence: the phase 5A test file was "not found", and the phase 4 job test count had grown from 9 to 13. The explanation was environmental, not code: a PR-review session had run in the same worktree a day earlier, checked out the pull-request branch `task/add-ad-tracking-gec`, committed review fixes there (including a refactor of the attribution job into `Window`/`CustomerIdentity` helpers and expanded tests), and left the worktree on that branch. The phase 3 schema commits — and the previous day's SSM diary commit — had therefore landed on the PR branch, which this project's workflow explicitly keeps one-PR-per-phase.

Recovery was mechanical because nothing had been pushed: create `task/google-ads-importer` at HEAD (the phase 3 commits stacked on the *reviewed* PR branch — the right base anyway), and reset `task/add-ad-tracking-gec` to its origin state. The phase 5A branch was untouched throughout; its "missing" test file simply lives on that branch.

Two durable lessons entered the diary. Verify the current branch before committing, not after — a worktree shared across sessions is mutable state. And the fact that the day's patches applied cleanly onto a concurrently-refactored `Job.php` was anchor luck, not process: the string-replacement anchors happened to survive the refactor.

## Testing

`tests/std/googleAdsImporterTest.php` (10 tests, 72 assertions) runs against REST-shaped fixture JSON — the camelCase, string-numbered format the real API emits, including `costMicros: "12345670000"` and resource names to parse. Coverage maps to the failure modes discussed above: micros and target conversions, ad-id parsing, month chunking including partial edge months, the GAQL date-injection guard, two-run upsert idempotency with run-id restamping, raw payload round-trip, dimension rename close-and-open plus the no-change case, dry-run write-freedom, click_view three-state resolution with the zero-queries-on-rerun assertion, and the attribution job picking up lookup + dimension data end to end.

The branch's full suite stands at 62 tests / 510 assertions (one pre-existing skip). The credential smoke test `scripts/helpers/testGoogleAdsAccess.php` verifies the live path step by step — config presence (secrets masked), OAuth exchange, `listAccessibleCustomers`, a one-row GAQL query per customer — and currently fails, correctly and informatively, at the missing refresh token.

## Current status

- Branch `task/google-ads-importer` (stacked on the reviewed PR branch): commits `3285bc831` (schema + models), `73e266fb2` (client/queries/mapper), `a19a43241` (importer, cron, smoke, job wiring), `86eef9268` (tests), `f0037e81a` (ticket docs). Not pushed.
- In SSM: developer token, OAuth client id/secret. Outstanding: refresh token (one OAuth consent by an Ads-account login), MCC id, customer ids, and the developer token's access-level confirmation (Test vs Basic).
- Activation sequence when they arrive: fill `/googleads/*` + config, `enabled=1`, `testGoogleAdsAccess.php`, one-off backfill (`--from 2016-01-01`, month-chunked), then the crontab takes over.
- Phase 5B unblocks the moment `google_ads_campaign_daily` has data; the 5A reports were shaped to extend with spend columns rather than be replaced.

## Important project docs

- Ticket: `ttmp/2026/08/18/GEC-ADS-ATTRIBUTION-001--google-ads-campaign-to-order-attribution-cac-and-ltv-analysis/` (design doc §13 = this phase; diary Step 27; this report as `report/04-…`).
- Companion notes: [[PROJ - GEC Ads Attribution - Cohort LTV Report and Marketing Touch Capture (Phase 1-2)]], [[PROJ - GEC Ads Attribution - Nightly Attribution Job and Order-Side Campaign Reports (Phase 4-5A)]].

## Open questions

- Whether phase 7 (conversion upload — a write path) should adopt the official client library after all; this report's library argument is explicitly scoped to read-only reporting.
- Whether `Client::request` needs 429/quota backoff once real volume exists; currently any failure fails the customer's run and the next nightly re-import covers the gap.

## Near-term next steps

- Obtain the refresh token and account ids; confirm the developer token's access level.
- Set the account-level tracking template (O3) — it reduces the click_view fallback surface from the moment it is set.
- Open the phase 3 PR once the PR-base question (stacked vs. post-merge rebase) is decided for the queued branches.
