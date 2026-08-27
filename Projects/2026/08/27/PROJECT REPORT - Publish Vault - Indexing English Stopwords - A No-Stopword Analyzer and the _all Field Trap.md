---
title: "Publish Vault: Indexing English Stopwords — A No-Stopword Analyzer and the _all Field Trap"
aliases:
  - Publish Vault stopword fix
  - PV-SEARCH-STOPWORDS
  - publish-vault nostop analyzer
  - publish-vault what returns nothing
  - publish-vault search stopword bug
tags: [project-report, publish-vault, search, bleve, go, analyzer, stopwords, obsidian, regression]
status: active
type: project-report
created: 2026-08-27
repo: /home/manuel/code/wesen/go-go-golems/publish-vault
source_ticket: PV-SEARCH-STOPWORDS
source_pr: https://github.com/go-go-golems/publish-vault/commit/6f211ce
implementation_commits:
  - 6f211ce feat(search): index English stopwords via a no-stopword custom analyzer
  - 194c000 fix(search): set nostop as the index default analyzer + stopword index test
deployed_image: ghcr.io/go-go-golems/publish-vault:sha-1d9c02d
deployed_image_ssr: ghcr.io/go-go-golems/publish-vault-ssr:sha-1d9c02d
gitops_prs:
  - "325 (retro-obsidian-publish / parc.yolo)"
  - "326 (obsidian-vault-publish)"
ticket_path: ttmp/2026/08/27/PV-SEARCH-STOPWORDS--search-stopwords-index-english-stopwords-what-this-that-via-a-no-stopword-analyzer
related_vault_notes:
  - "[[PROJECT REPORT - Publish Vault - Date-Aware Advanced Search - A Technical Deep Dive]]"
  - "[[PROJ - Publish Vault - Bounded Persistent Search Indexing]]"
  - "[[ARTICLE - Publish Vault Memory Optimization - From OOM Incidents to Phase-Attributed Baselines]]"
---

# Publish Vault: Indexing English Stopwords — A No-Stopword Analyzer and the _all Field Trap

This report explains how publish-vault's full-text search came to return zero results for common English words such as `what`, `this`, `that`, `with`, `from`, `have`, `your`, `they`, and `them`, and how the fix was structured so the same change reaches both the index at build time and the query at search time. The work is ticket `PV-SEARCH-STOPWORDS`, deployed as image `ghcr.io/go-go-golems/publish-vault:sha-1d9c02d` (and the matching `-ssr` image) to the two publish-vault sites `parc.yolo.scapegoat.dev` and the sibling `obsidian-vault-publish` site, via GitOps PRs #325 and #326.

The bug was not a crash and not a missing feature. A user typing `what` into the search field on `parc.yolo.scapegoat.dev` got an empty result list, even though the word `what` appears in 1,737 of the vault's notes. The root cause is that publish-vault's Bleve index used the library's built-in `standard` analyzer on its text fields, and that analyzer's token filter chain is `lowercase → English stop filter`. The stop filter deletes a fixed list of common English words — the Snowball English stop list — from the token stream at indexing time, so those words never enter the index and can never be matched by any query. The fix is a custom analyzer named `nostop` that is the unicode tokenizer plus the lowercase filter and nothing else, registered in the Bleve registry and set as both the per-field analyzer and the index-wide default analyzer.

The decisive detail in the fix is the second of those two placements. Setting the analyzer on the four text fields (`title`, `body`, `tags`, `excerpt`) made indexing stop dropping stopwords, but queries still returned nothing for them, because a Bleve `MatchQuery` that does not name a field searches the index's `_all` composite field, and the `_all` field's analyzer is the `IndexMapping`'s `DefaultAnalyzer`, which Bleve defaults to `standard`. The query side was still dropping stopwords through `_all` even after the per-field analyzers were changed. Setting `im.DefaultAnalyzer = nostopAnalyzerName` closes that loop.

> [!summary]
> 1. publish-vault's text fields used Bleve's built-in `standard` analyzer, whose token filter chain is `lowercase → English stop filter`. The stop filter deletes the Snowball English stop words (`what`, `this`, `that`, `with`, `from`, …) from the token stream at indexing time, so they are never stored and never matchable.
> 2. The fix is a custom `nostop` analyzer (unicode tokenizer + lowercase filter, no stop filter, no stemmer) registered in the Bleve registry via `init()`, set on the four text fields and — critically — as the index-wide `DefaultAnalyzer`, because a field-less `MatchQuery` searches the `_all` composite field whose analyzer is the default, not the per-field analyzer.
> 3. A ≤3-character single-word query takes a `PrefixQuery` path that is not analyzed, which is why `the` (3 chars) returned 1,257 results while `what` (4 chars) returned zero: `the` matched raw indexed tokens starting with `the` (`theory`, `there`, `then`, …) without passing through the stop filter, while `what` went through the analyzed `MatchQuery` path and was dropped.
> 4. The production index rebuilds fresh on every pod startup (`NewPersistentWithOptions` removes the index directory and calls `bleve.New` with the new mapping), so the analyzer change takes effect on the next deploy with no manual reindex command. Live verification on `parc.yolo` confirmed `what`→1933, `this`→1919, `that`→1944, `with`→1948, `from`→1909 (all previously zero).

## The problem this work addresses

publish-vault serves an Obsidian vault as a single binary. Its search has two implementations that must agree on inclusion: a Go backend backed by a Bleve full-text index, and an in-browser static matcher that loads a JSON snapshot and does plain substring matching over title, excerpt, and tags. The production site `parc.yolo.scapegoat.dev` runs the Go backend. The static matcher has no stopword logic — it is `note.title.toLowerCase().includes(q)` — so in static mode every word, including `what`, matches if it appears. The Go backend, however, returned nothing for `what`.

The mismatch was reported as "you can't search for `what`". Investigation produced a table of live query totals that isolated the cause.

| Query | Live total | In the Snowball stop list? | Word length |
|-------|------------|----------------------------|-------------|
| `what` | 0 | yes | 4 |
| `this` | 0 | yes | 4 |
| `that` | 0 | yes | 4 |
| `with` | 0 | yes | 4 |
| `from` | 0 | yes | 4 |
| `have` | 0 | yes | 4 |
| `your` | 0 | yes | 4 |
| `they` | 0 | yes | 4 |
| `them` | 0 | yes | 4 |
| `the` | 1257 | yes | 3 |
| `and` | 120 | yes | 3 |
| `for` | 1651 | yes | 3 |
| `will` | 1385 | no | 4 |
| `work` | 1659 | no | 4 |
| `system` | 1594 | no | 6 |

Two facts in that table narrow the cause. Every four-or-more-letter stopword returned zero; every non-stopword of comparable length returned results. And every three-letter word — stopword or not — returned results. The first fact points at a stopword filter. The second fact is the one that initially looks like a contradiction: `the` is a stopword, so a stopword filter should drop it too, yet `the` returned 1,257 results. Resolving that contradiction required reading both the Bleve stop list and the query builder.

## How Bleve's standard analyzer drops stopwords

Bleve's `standard` analyzer is registered in `analysis/analyzer/standard/standard.go`. Its constructor builds an `analysis.DefaultAnalyzer` with three stages:

```go
tokenizer, err := cache.TokenizerNamed(unicode.Name)
toLowerFilter, err := cache.TokenFilterNamed(lowercase.Name)
stopEnFilter, err := cache.TokenFilterNamed(en.StopName)
rv := analysis.DefaultAnalyzer{
    Tokenizer: tokenizer,
    TokenFilters: []analysis.TokenFilter{
        toLowerFilter,
        stopEnFilter,
    },
}
```

The stop filter is `en.StopName`, the `stop_en` token filter, whose token map is `EnglishStopWords` in `analysis/lang/en/stop_words_en.go`. That file is the Snowball English stop list, a raw multi-line byte string, not a quoted list, which is why a naive grep for `"what"` finds nothing. Line 76 of that file is the bare token `what`. The list includes `i`, `me`, `my`, `we`, `you`, `your`, `he`, `she`, `it`, `they`, `them`, `their`, `what`, `which`, `who`, `this`, `that`, `with`, `from`, `have`, `the`, `and`, `for`, and roughly four hundred more.

publish-vault's `buildMapping` applied `standard.Name` to the three text fields that carry prose:

```go
titleField := bleve.NewTextFieldMapping()
titleField.Analyzer = standard.Name
// ... same for bodyField and tagsField
```

When the indexer processes a note whose body contains "This explains what bleve does", the standard analyzer tokenizes to `["this", "explains", "what", "bleve", "does"]`, then lowercases, then drops `this` and `what` (both on the stop list), leaving `["explains", "bleve", "does"]` in the index. The words `this` and `what` are gone. No query can find them, because the index never held them. This is index-time deletion, not query-time filtering: the tokens are removed before they reach the index's inverted lists.

The stop filter is a web-scale ranking optimization. At billions of documents, a word like `the` matches almost everything and carries no ranking signal; dropping it shrinks the index and improves precision for the words that remain. publish-vault is the opposite case: a personal note vault of roughly 2,000 documents, where every word can be a deliberate, intentional query — a note titled "What I learned about bleve", a code identifier, a filename. The index-size cost of keeping stopwords at this scale is negligible, and the precision cost of dropping them is high, because the user typed them on purpose. The stop filter is the wrong default for this domain.

## Why `the` returned results: the prefix-query special case

The query builder `textQueryClause` in `pkg/search/search.go` branches on word length:

```go
func textQueryClause(words []string) bq.Query {
    if len(words) == 1 && len(words[0]) <= 3 {
        return bleve.NewPrefixQuery(words[0])
    }
    var disjuncts []bq.Query
    for _, w := range words {
        mq := bleve.NewMatchQuery(w)
        mq.SetFuzziness(1)
        disjuncts = append(disjuncts, mq)
    }
    if len(disjuncts) == 1 {
        return disjuncts[0]
    }
    return bleve.NewConjunctionQuery(disjuncts...)
}
```

A single query word of three characters or fewer becomes a `PrefixQuery`. A `PrefixQuery` is not analyzed; it is matched against the raw terms already in the index. So a query for `the` never passes through the stop filter. It matches every indexed token that starts with the bytes `the`: `theory`, `there`, `then`, `these`, `theme`, `theorem`, `their`, `them`, and the bare `the` if any note indexed it through a field that did not apply the stop filter. That is why `the` returned 1,257 results — not because `the` escaped the stop filter, but because the prefix path bypassed analysis entirely and matched longer, non-stop tokens that share the prefix.

A single query word of four characters or more, and any multi-word query, takes the `MatchQuery` path. A `MatchQuery` is analyzed with the field's analyzer before matching. For a field-less `MatchQuery` the field is `_all`, and `_all`'s analyzer is the index default. So `what` (4 chars) went through the analyzed path, the stop filter dropped it, the query became empty, and Bleve returned zero.

The ≤3-character threshold is an existing UX choice, not part of the bug: it makes short queries like `go` or `js` work as prefixes (matching `golang`, `goja`, `json`). Once stopwords are indexed, the two paths stop being a source of inconsistency, because the analyzed path no longer drops the stopword. The threshold itself is left unchanged by this work.

## The fix: a no-stopword analyzer

The fix replaces the `standard` analyzer with a custom analyzer that omits the stop filter. The analyzer is defined in `pkg/search/analyzer_nostop.go`:

```go
const nostopAnalyzerName = "nostop"

func registerNostopAnalyzer() {
    _ = registry.RegisterAnalyzer(nostopAnalyzerName, func(config map[string]interface{}, cache *registry.Cache) (analysis.Analyzer, error) {
        tokenizer, err := cache.TokenizerNamed(unicode.Name)
        if err != nil {
            return nil, err
        }
        toLowerFilter, err := cache.TokenFilterNamed(lowercase.Name)
        if err != nil {
            return nil, err
        }
        return &analysis.DefaultAnalyzer{
            Tokenizer: tokenizer,
            TokenFilters: []analysis.TokenFilter{
                toLowerFilter,
            },
        }, nil
    })
}

func init() {
    registerNostopAnalyzer()
}
```

The analyzer is the same as `standard` with one stage removed: it keeps the unicode tokenizer and the lowercase filter, and omits the `stop_en` filter. No stemmer is applied, so exact token semantics are preserved — code identifiers and filenames are not reduced to stems, which would surprise a note searcher (`running` matching `run`). Typo tolerance is already provided by `SetFuzziness(1)` on `MatchQuery`, so stemming is not needed for recall.

`buildMapping` sets this analyzer on the four text fields and on the index default:

```go
func buildMapping() mapping.IndexMapping {
    im := bleve.NewIndexMapping()

    im.DefaultAnalyzer = nostopAnalyzerName

    dm := bleve.NewDocumentMapping()
    dm.DefaultAnalyzer = nostopAnalyzerName

    titleField := bleve.NewTextFieldMapping()
    titleField.Analyzer = nostopAnalyzerName
    titleField.Store = true
    dm.AddFieldMappingsAt("title", titleField)

    bodyField := bleve.NewTextFieldMapping()
    bodyField.Analyzer = nostopAnalyzerName
    bodyField.Store = false
    dm.AddFieldMappingsAt("body", bodyField)

    tagsField := bleve.NewTextFieldMapping()
    tagsField.Analyzer = nostopAnalyzerName
    tagsField.Store = true
    dm.AddFieldMappingsAt("tags", tagsField)

    tagsKwField := bleve.NewKeywordFieldMapping()
    tagsKwField.Store = false
    dm.AddFieldMappingsAt("tags_kw", tagsKwField)

    excerptField := bleve.NewTextFieldMapping()
    excerptField.Analyzer = nostopAnalyzerName
    excerptField.Store = true
    dm.AddFieldMappingsAt("excerpt", excerptField)
    // ... date and path fields unchanged ...
}
```

The keyword fields (`tags_kw`, `path`, `path_kw`, the date fields) are unchanged. They use Bleve's keyword analyzer, which does not tokenize at all; they exist for exact term and range queries, not free text, and the stopword problem never touched them.

## The `_all` field trap and why the first attempt failed

The first implementation set `nostopAnalyzerName` on the four text fields and built the index. All twelve existing search tests failed with the same error:

```
no analyzer with name or type 'nostop' registered
```

The cause was that the analyzer's constructor was not in the Bleve registry. `IndexMapping.AddCustomAnalyzer` stores the analyzer name on the mapping, but `bleve.New` and `bleve.NewMemOnly` validate the mapping against the global registry, and the registry did not know `nostop`. Bleve's own `standard` analyzer registers itself in an `init()` via `registry.RegisterAnalyzer`; a custom analyzer must do the same. Adding `init() { registerNostopAnalyzer() }` in `analyzer_nostop.go` fixed all twelve tests.

The second failure was subtler and is the central technical lesson of this work. After the registry fix, the index built and the existing tests passed, but a new test that searched for `what`, `this`, `that`, `with`, and `from` still returned zero for all of them. The per-field analyzers were `nostop`, so indexing no longer dropped stopwords. The query, however, still did.

A Bleve `MatchQuery` that does not call `SetField` searches the index's `_all` composite field. The `_all` field concatenates every field marked `IncludeInAll` and analyzes the result with the `IndexMapping`'s `DefaultAnalyzer`. Bleve's `NewIndexMapping` sets `DefaultAnalyzer` to `standard.Name`:

```go
// bleve mapping/index.go
const defaultAnalyzer = standard.Name
// ...
im.DefaultAnalyzer = defaultAnalyzer
```

Changing the per-field analyzers to `nostop` did not change `DefaultAnalyzer`, so the `_all` field still used `standard`, still applied the stop filter, and still dropped `what` from the query before matching. The index held `what`; the query never asked for it.

The fix is one line in `buildMapping`:

```go
im.DefaultAnalyzer = nostopAnalyzerName
```

The document mapping's `DefaultAnalyzer` is set to `nostop` as well, because `DocumentMapping.defaultAnalyzerName` walks the document mapping's `DefaultAnalyzer` as the fallback for any field without an explicit analyzer, and the `_all` field's analyzer is resolved through that path. With both set, indexing and querying use the same analyzer, and the round-trip is consistent.

This is the trap the report's title names. A field's analyzer and the index's default analyzer are two independent settings. Changing one without the other produces an index and a query that use different analyzers, and the failure is silent: the index builds, the existing tests pass (they never searched for stopwords), and only a search for a stopword reveals the divergence. Any future analyzer change in this codebase must set the index default, not only the per-field analyzers, or the `_all` field will keep the old behavior.

## The static matcher and why no-stopword is the consistent choice

The static matcher in `web/src/vault/staticVault.ts` has no stopword logic. Its free-text path is:

```ts
const titleScore = note.title.toLowerCase().includes(q) ? 2 : 0;
const contentScore = note.excerpt.toLowerCase().includes(q) ? 1 : 0;
```

A substring match. `what` matches any note whose title or excerpt contains `what`. There is no analyzer, no tokenizer, no stop list. So in static mode, `what` already matched. The Go backend's stopword dropping was a divergence between the two search implementations that the stopword report made visible.

Making the Go backend keep stopwords aligns the two implementations on inclusion: a note that the static matcher includes for `what` is now also included by the Bleve backend. The two still rank differently — Bleve scores by term frequency and field; the static matcher scores by a fixed title/excerpt/tag weight — but inclusion agreement is the contract the two modes must hold, and the stopword fix restores it. The earlier [[PROJECT REPORT - Publish Vault - Date-Aware Advanced Search - A Technical Deep Dive]] established that parity contract and fixed the static parser's date handling for the same reason; this work closes a second inclusion divergence.

## Decision records

### DR-1: remove the stop filter rather than stopword the prefix path

- **Context.** The bug had two symptoms: four-plus-letter stopwords returned zero, and `the` (three letters) returned 1,257. A consistent fix could either remove the stop filter (so stopwords are indexed and matchable everywhere) or apply the stop filter to the prefix path too (so `the` also returns zero).
- **Options.** (A) Remove the stop filter. (B) Apply the stop filter to the prefix path.
- **Decision.** **A**. The user's goal is that `what` returns results, not that `the` also returns nothing. Option B makes the bug uniform instead of fixing it. Option A makes both query paths consistent and aligns the Go backend with the static matcher.
- **Consequences.** Stopwords are indexed, so the index is slightly larger; at ~2,000 notes the cost is negligible. Multi-word queries now AND on stopwords, so `what is this` matches notes containing all three words, which is the correct behavior for an intentional query.

### DR-2: no stemmer

- **Context.** The `standard` analyzer applies a stop filter but no stemmer. A stemmer (e.g., the Porter stemmer in `analysis/lang/en/stemmer_en.go`) would reduce `running` to `run`, improving recall for inflected forms.
- **Options.** (A) Keep `nostop` without a stemmer. (B) Add a stemmer to `nostop`.
- **Decision.** **A**. A note vault is searched for exact tokens — code identifiers, filenames, proper nouns — where stemming surprises (`running` matching `run`, `university` matching `universe`) reduce precision. `SetFuzziness(1)` on `MatchQuery` already covers single-character typos, which is the recall the user actually wants. Stemming can be reconsidered if recall for inflected natural language becomes a real need.

### DR-3: set the index default analyzer, not only the per-field analyzers

- **Context.** The first fix set `nostop` on the text fields but not on `IndexMapping.DefaultAnalyzer`. The `_all` composite field kept `standard` and still dropped stopwords at query time.
- **Options.** (A) Set only per-field analyzers. (B) Set per-field analyzers and the index default.
- **Decision.** **B**. The `_all` field's analyzer is the index default, and a field-less `MatchQuery` searches `_all`. Without the default set, the query side and the index side use different analyzers and the failure is silent.
- **Consequences.** Both the document mapping's `DefaultAnalyzer` and the `IndexMapping`'s `DefaultAnalyzer` are set, so any field that falls back to the default also uses `nostop`. The `excerpt` field, which previously had no explicit analyzer and inherited `standard`, now explicitly uses `nostop`.

## Deployment and the no-manual-reindex property

publish-vault's production deployment runs with `--search-index-path /data/search`, a writable volume. The index is not opened and reused across restarts; it is rebuilt. The function `buildSearchIndex` in `pkg/server/runtime.go` builds the index into a revision-keyed snapshot directory:

```go
buildIndexDir := filepath.Join(buildDir, "index")
// ...
si, err := search.NewPersistentWithOptions(v, buildIndexDir, persistentSearchOptions(run))
```

`search.NewPersistentWithOptions` calls `os.RemoveAll(indexPath)` then `bleve.New(indexPath, buildMapping())`, so every index build starts from an empty directory and uses the current `buildMapping`. The pod restart on the new image therefore rebuilt the index with the `nostop` mapping. No manual reindex command, no migration step, no index-version flag was needed. The existing index directory for the previous revision remained on disk until the snapshot cleanup ran, but the new revision's index was built fresh and used immediately.

This is the operational property that made the fix a single PR. An analyzer change is a migration-by-rebuild — the existing index was built with the stop filter, so the tokens it holds do not include stopwords, and changing the analyzer only affects newly indexed documents. Because the production index is rebuilt on every startup, the deploy itself is the migration. A deployment that opened and reused a persistent index would have required a separate reindex step or a version flag; publish-vault does not, because of the snapshot-rebuild design documented in [[PROJ - Publish Vault - Bounded Persistent Search Indexing]].

The two-image deployment means each GitOps PR bumps two image lines: the `app` container (the Go server, which holds the Bleve index) and the `ssr` container (the server-side renderer). Both must update, because the fix lives in the `app` container's index. CI's `publish-image` workflow builds and pushes both from the same commit, and the GitOps PR automation bumps both lines in one PR. PR #325 (retro-obsidian-publish) and PR #326 (obsidian-vault-publish) each bumped both images to `sha-1d9c02d`.

## Verification

The regression test `TestStopwordsAreIndexed` in `pkg/search/search_test.go` indexes two notes — one containing `what`, `this`, `that`, `with`, `from` and one unrelated — and asserts each stopword is searchable. The words are four or more characters, so they exercise the `MatchQuery` path that exposed the bug, not the ≤3-character prefix path.

```go
func TestStopwordsAreIndexed(t *testing.T) {
    root := t.TempDir()
    writeTestNote(t, root, "what-note.md", "# What is bleve\n\nThis explains what bleve does with from and why that matters.")
    writeTestNote(t, root, "other-note.md", "# Other\n\nUnrelated note about golang.")
    // ...
    for _, w := range []string{"what", "this", "that", "with", "from"} {
        results, err := idx.Search(w, 20)
        if err != nil { t.Fatalf("Search(%q): %v", w, err) }
        if len(results) == 0 {
            t.Errorf("Search(%q): expected results (stopword should be indexed), got none", w)
        }
    }
    // ... and that "what" matches the what-note specifically ...
}
```

During development this test caught a content gap before it caught a code gap: the first version of the test note omitted `with` and `from`, and the test correctly reported zero for them, which looked like a code failure but was a test-data failure. Fixing the note text made the test pass. That the test distinguishes "the word isn't in the corpus" from "the analyzer dropped the word" is the property that makes it a useful regression test.

Live verification on `https://parc.yolo.scapegoat.dev` after the rollout to `sha-1d9c02d` confirmed the fix end to end.

| Query | Before | After |
|-------|--------|-------|
| `what` | 0 | 1933 |
| `this` | 0 | 1919 |
| `that` | 0 | 1944 |
| `with` | 0 | 1948 |
| `from` | 0 | 1909 |
| `have` | 0 | 1429 |
| `your` | 0 | 1489 |
| `they` | 0 | 2000 |
| `them` | 0 | 1999 |
| `the` | 1257 | 2000 |
| `knowledge` | 486 | 486 |
| `go` | 1759 | 1759 |
| `system` | 1594 | 1594 |

`the` went from 1,257 to 2,000: the prefix path previously matched only the longer tokens starting with `the`, while after the fix it also matches the bare stopword `the` that is now indexed. `knowledge`, `go`, and `system` are unchanged, confirming the fix is additive for non-stopwords. A multi-word query `what is this` returns 1,878, confirming that the conjunction now ANDs on all words including the stopwords.

## Failure modes and the decisions that avoid them

| Failure mode | Cause | Mitigation in place |
|---|---|---|
| Stopwords dropped at index time | `standard` analyzer's `stop_en` filter | `nostop` analyzer omits the stop filter |
| Stopwords dropped at query time via `_all` | `IndexMapping.DefaultAnalyzer` defaults to `standard` | `im.DefaultAnalyzer = nostopAnalyzerName` |
| Custom analyzer not found at index build | constructor not in the Bleve registry | `init() { registerNostopAnalyzer() }` via `registry.RegisterAnalyzer` |
| Existing index lacks stopwords after analyzer change | index built with the old mapping | production rebuilds the index fresh on every startup (`NewPersistentWithOptions`) |
| Static and dynamic search disagree on inclusion | static matcher has no stopword logic; backend dropped stopwords | both now keep stopwords; inclusion agreement restored |
| Stemmer surprises (`running` matching `run`) | adding a stemmer to `nostop` | no stemmer; `SetFuzziness(1)` covers typos |

## Current status

The fix is shipped, deployed, and verified live. Both `retro-obsidian-publish` (`parc.yolo.scapegoat.dev`) and `obsidian-vault-publish` run `sha-1d9c02d` (Argo `Synced`/`Healthy`). The full Go test suite passes, including the new `TestStopwordsAreIndexed`. The work is tracked in docmgr ticket `PV-SEARCH-STOPWORDS` with a four-phase investigation diary and a clean doctor report.

## Important project docs

- `/home/manuel/code/wesen/go-go-golems/publish-vault/pkg/search/analyzer_nostop.go` — the `nostop` analyzer and its `init()` registration.
- `/home/manuel/code/wesen/go-go-golems/publish-vault/pkg/search/search.go` — `buildMapping` (the `DefaultAnalyzer` and per-field analyzer assignments), `textQueryClause` (the ≤3 prefix special case).
- `/home/manuel/code/wesen/go-go-golems/publish-vault/pkg/search/search_test.go` — `TestStopwordsAreIndexed`.
- `/home/manuel/code/wesen/go-go-golems/publish-vault/pkg/server/runtime.go` — `buildSearchIndex` (the snapshot rebuild that makes the fix a no-manual-reindex deploy).
- `/home/manuel/code/wesen/go-go-golems/publish-vault/ttmp/2026/08/27/PV-SEARCH-STOPWORDS--search-stopwords-index-english-stopwords-what-this-that-via-a-no-stopword-analyzer/reference/01-investigation-diary.md` — the four-phase diary.
- `/home/manuel/code/wesen/2026-03-27--hetzner-k3s/gitops/kustomize/retro-obsidian-publish/deployment.yaml` — the image tag bumped to `sha-1d9c02d` via GitOps PR #325.

## Open questions

- The ≤3-character prefix special case in `textQueryClause` is now consistent (stopwords are indexed, so both paths agree), but the threshold itself is arbitrary. Should short queries use the analyzed `MatchQuery` path instead, so `go` matches only `go` and not `golang`? The prefix behavior is a useful UX for short identifiers; changing it is a separate decision.
- Should the analyzer be configurable, so a deployment that wants stopword removal for a very large vault can opt back into it? At the current scale the no-stopword default is correct; a config knob would be premature.
- The two-image deployment (app + ssr) requires both image lines to bump in lockstep. The GitOps automation already does this in one PR, but a deployment that bumped only one would silently serve a mismatched pair. A validation that the two tags match in the deployment manifest would catch that.

## Related vault notes

- [[PROJECT REPORT - Publish Vault - Date-Aware Advanced Search - A Technical Deep Dive]] — the advanced-search work that established the static/dynamic inclusion parity contract this fix upholds, and the shared `SearchRequest` contract.
- [[PROJ - Publish Vault - Bounded Persistent Search Indexing]] — the snapshot-rebuild index design that makes analyzer changes take effect on deploy without a manual reindex.
- [[ARTICLE - Publish Vault Memory Optimization - From OOM Incidents to Phase-Attributed Baselines]] — the memory-optimization work that produced the persistent, bounded index this fix builds on.

## Project working rule

> [!important]
> A Bleve analyzer change must set the `IndexMapping.DefaultAnalyzer`, not only the per-field analyzers. A field-less `MatchQuery` searches the `_all` composite field, whose analyzer is the index default, not the per-field analyzer; changing one without the other makes the index and the query use different analyzers, and the failure is silent until someone searches for a word the old analyzer dropped.
