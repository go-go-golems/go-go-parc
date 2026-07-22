# Hosting Platform Analysis

- URL: https://chatgpt.com/c/6a5d8d57-ba2c-83ea-9c0e-c990108f325e
- Created: 2026-07-20T02:52:08.565Z

## Turn 0 - user

- Message ID: `263eab1d-6331-4782-8605-898a8c1ddb6e`

study github.com/go-go-golems/go-go-goja and github.com/go-go-golems/go-go-host and then also https://parc.yolo.scapegoat.dev/note/research/kb/projects/go-go-goja and https://parc.yolo.scapegoat.dev/note/research/kb/projects/widget-dsl

I want to build a hosting platform that is hosting javascript goja programs (see in particular the xgoja feature and the way different modules can be linked). The idea is that you can pay for a subscription for these different modules (like sqlite), and then upload programs that will use that runtime to run, a bit like AWS lambda, but also with web UIs and things like stripe payments and all. The idea is that people will use coding agents, so that the whole release version stuff (like in go-go-host) would be safe and versioned and rollbackable and secure. I plan to use something like github.com/go-go-golems/tiny-idp which is still WIP (we're turning it into something scriptable too: https://github.com/go-go-golems/tiny-idp/tree/task/prod-tiny-idp) for both managing my customers (the hosting users that upload js), and then maybe instances or some way for customers to manage their users.

Anyway, figure it out, and analyze all the code here and see what is worth saving, what should be changed, what is bad, what is missing, and all that.

## Turn 1 - assistant

- Message ID: `c6d86867-e40d-42a4-956f-447ecb9e075f`
- Model: `gpt-5-6-pro`

I’ll inspect the repositories, design notes, and Tiny IDP branch, then trace runtime, module, release, and auth flows into a security review, retention matrix, architecture, and migration plan.

## Turn 2 - assistant (thinking)

- Message ID: `2391834f-3fc3-49b1-bc0e-8379dee71712`

<details><summary>Thinking</summary>

**Evaluated GitHub repos and retrieved repository metadata**


</details>

## Turn 3 - assistant (thinking)

- Message ID: `ad7fb26d-7063-4297-b743-6f46b8800a35`

<details><summary>Thinking</summary>

**Inspected and retrieved GitHub repository metadata**


</details>

## Turn 4 - assistant (tool call)

- Message ID: `8d6e9baa-f1d6-475b-aec3-1c681a69f914`
- Model: `gpt-5-6-pro`

```unknown
bash -lc set -euo pipefail
mkdir -p /mnt/data/repo-review
cd /mnt/data/repo-review
for r in go-go-goja go-go-host tiny-idp; do
  if [ -d "$r/.git" ]; then
    git -C "$r" fetch --all --tags --prune >/dev/null 2>&1 || true
  else
    git clone --filter=blob:none --no-checkout "https://github.com/go-go-golems/$r.git" "$r"
  fi
done
printf '\nCLONED\n'
for r in go-go-goja go-go-host tiny-idp; do git -C "$r" remote -v | head -1; done
```

## Turn 5 - assistant (thinking)

- Message ID: `f6869164-7cb3-4cec-915d-9cb52beef6b5`

<details><summary>Thinking</summary>

**Cloned repositories for analysis**


</details>

## Turn 6 - assistant (tool call)

- Message ID: `6fd18c98-5f44-4b8c-8fe8-38af5526b4f5`
- Model: `gpt-5-6-pro`

```json
{"open":[{"ref_id":"https://github.com/go-go-golems/go-go-goja"},{"ref_id":"https://github.com/go-go-golems/go-go-host"},{"ref_id":"https://github.com/go-go-golems/tiny-idp/tree/task/prod-tiny-idp"},{"ref_id":"https://parc.yolo.scapegoat.dev/note/research/kb/projects/go-go-goja"},{"ref_id":"https://parc.yolo.scapegoat.dev/note/research/kb/projects/widget-dsl"}],"response_length":"long"}
```

## Turn 7 - assistant (thinking)

- Message ID: `1a8cb005-12a4-400f-b17b-9d9702e61a22`

<details><summary>Thinking</summary>

**Searched the web, GitHub, and various resources for projects**


</details>

## Turn 8 - assistant (thinking)

- Message ID: `199e64df-190c-4da0-913c-f350ad0b62a3`

<details><summary>Thinking</summary>

**Searched and fetched files, documentation, and migration content**


</details>

## Turn 9 - assistant (tool call)

- Message ID: `e447da88-26c6-4f6f-ab3a-fc7746d6c933`
- Model: `gpt-5-6-pro`

```json
{"open":[{"ref_id":"turn147769view1","lineno":150},{"ref_id":"turn147769view1","lineno":180},{"ref_id":"turn147769view1","lineno":300},{"ref_id":"turn147769view1","lineno":340}],"response_length":"long"}
```

## Turn 10 - assistant (thinking)

- Message ID: `b4605ac0-c0be-498d-8b4c-0a159fd7d839`

<details><summary>Thinking</summary>

**Searched the web and GitHub**


</details>

## Turn 11 - assistant (thinking)

- Message ID: `4dc4dacc-4639-47e7-9a7b-e8989a84d566`

<details><summary>Thinking</summary>

**Searched GitHub repository for deployment files and keywords**


</details>

## Turn 12 - assistant (tool call)

- Message ID: `4ccffebe-b0df-40df-af24-945461ebb36a`
- Model: `gpt-5-6-pro`

```json
{"click":[{"ref_id":"turn147769view1","id":80},{"ref_id":"turn147769view1","id":78},{"ref_id":"turn147769view1","id":81},{"ref_id":"turn147769view1","id":96}],"response_length":"long"}
```

## Turn 13 - assistant

- Message ID: `15f8dcbe-8e65-4535-84a3-c511beb798a4`
- Model: `gpt-5-6-pro`

A key boundary is emerging: preserve xgoja’s compile-time capability composition separately from go-go-host’s deployment control plane, while testing that split against paid modules and hostile tenants.

## Turn 14 - assistant (thinking)

- Message ID: `c3a902dd-34b6-4632-b905-fa83e042e177`

<details><summary>Thinking</summary>

**Searched multiple websites for GitHub API URLs and resources**


</details>

## Turn 15 - assistant (thinking)

- Message ID: `e1b05bc7-3022-4037-8988-ab010f46d8c6`

<details><summary>Thinking</summary>

**Fetched repository files, documentation, and runtime guidelines for analysis**


</details>

## Turn 16 - assistant (thinking)

- Message ID: `45fb1c87-a997-4774-93e4-c9258136df15`

<details><summary>Thinking</summary>

**Investigated runtime issues and inspected session security**


</details>

## Turn 17 - assistant (tool call)

- Message ID: `b8ab0d54-0b02-453c-9738-467bf8c8d180`
- Model: `gpt-5-6-pro`

```json
{"open":[{"ref_id":"https://github.com/go-go-golems/go-go-host/tree/main/internal/sitejs/web"},{"ref_id":"https://github.com/go-go-golems/go-go-host/tree/main/internal/runtime"},{"ref_id":"https://github.com/go-go-golems/go-go-host/tree/main/internal/control"},{"ref_id":"https://github.com/go-go-golems/go-go-host/tree/main/internal/store/migrations"}],"response_length":"long"}
```

## Turn 18 - assistant (thinking)

- Message ID: `f849bbc2-445a-4144-9da7-b0d4d6785880`

<details><summary>Thinking</summary>

**Searched the web**


</details>

## Turn 19 - assistant (thinking)

- Message ID: `5dc80825-5fe2-467b-bbee-34fa700ede6a`

<details><summary>Thinking</summary>

**Inspected code quality, searched files, and fetched GitHub content**


</details>

## Turn 20 - assistant (thinking)

- Message ID: `9f2a00ad-b6e0-4c62-b9f7-c896a5d5baa4`

<details><summary>Thinking</summary>

**Implemented VM interrupt policy, evaluated middleware defaults, and fetched files**


</details>

## Turn 21 - assistant (thinking)

- Message ID: `6f87a37c-d0f8-4abf-93f3-0c0af7243893`
- Model: `gpt-5-6-pro`

<details><summary>Thinking</summary>

**Reviewing code access method**

I'm thinking about how to access the code repository. The GitHub API might help explore the files, but I’ll need to check if it can list all contents recursively. Let’s try that!

**Reviewed code access method**


</details>

## Turn 22 - assistant (tool call)

- Message ID: `97c083d0-d854-4d65-bf21-75336785d904`
- Model: `gpt-5-6-pro`

```json
{"open":[{"ref_id":"https://api.github.com/repos/go-go-golems/go-go-goja/git/trees/main?recursive=1"},{"ref_id":"https://api.github.com/repos/go-go-golems/go-go-host/git/trees/main?recursive=1"},{"ref_id":"https://api.github.com/repos/go-go-golems/tiny-idp/git/trees/task/prod-tiny-idp?recursive=1"},{"ref_id":"https://api.github.com/repos/go-go-golems/tiny-idp/git/trees/main?recursive=1"}],"response_length":"long"}
```

## Turn 23 - assistant (thinking)

- Message ID: `85b53522-c495-468e-a7c1-35e1f716775a`

<details><summary>Thinking</summary>

**Searched the web and GitHub repositories for tree data**


</details>

## Turn 24 - assistant (thinking)

- Message ID: `54521750-58c3-4721-af97-e04224ce5bf1`

<details><summary>Thinking</summary>

**Searched branches and fetched README content from GitHub repository**


</details>

## Turn 25 - assistant (tool call)

- Message ID: `da1f1007-9ed3-4667-8e9e-65609858b0c6`
- Model: `gpt-5-6-pro`

```json
{"open":[{"ref_id":"https://github.com/go-go-golems/tiny-idp/tree/task/prod-tiny-idp"},{"ref_id":"https://github.com/go-go-golems/tiny-idp/tree/main"},{"ref_id":"https://github.com/go-go-golems/go-go-host"},{"ref_id":"https://github.com/go-go-golems/go-go-goja"}],"response_length":"long"}
```

## Turn 26 - assistant (thinking)

- Message ID: `fd6ea2d4-4ea6-4375-996c-1e80452ed554`

<details><summary>Thinking</summary>

**Searched the web and GitHub**


</details>

## Turn 27 - assistant (thinking)

- Message ID: `dbf53a76-1198-4e8a-bf3e-e5288b2ed407`

<details><summary>Thinking</summary>

**Fetched relevant README, security, and embedding documentation**


</details>

## Turn 28 - assistant (tool call)

- Message ID: `67d2c5ff-226a-4fcb-af80-e6660a1caa9b`
- Model: `gpt-5-6-pro`

```json
{"search_query":[{"q":"site:github.com/go-go-golems/tiny-idp \"task/prod-tiny-idp\""},{"q":"github go-go-golems tiny-idp prod-tiny-idp"},{"q":"site:github.com/go-go-golems/tiny-idp \"serve-production\""}],"response_length":"long"}
```

## Turn 29 - assistant (thinking)

- Message ID: `5c617c23-85bd-4a94-ad68-b0b024eb7fbe`

<details><summary>Thinking</summary>

**Searched GitHub, arxiv, zenn, and other sites for code references**


</details>

## Turn 30 - assistant (thinking)

- Message ID: `6c448e7d-fab2-475e-83e5-5508096c9ef9`

<details><summary>Thinking</summary>

**Compared commits for file changes and metadata**


</details>

## Turn 31 - assistant (tool call)

- Message ID: `0b36184a-1afe-44eb-a1c4-addb7f519c80`
- Model: `gpt-5-6-pro`

```json
{"search_query":[{"q":"site:parc.yolo.scapegoat.dev/note/research/kb/projects/go-go-goja"},{"q":"site:parc.yolo.scapegoat.dev/note/research/kb/projects/widget-dsl"},{"q":"site:parc.yolo.scapegoat.dev \"widget-dsl\""},{"q":"site:parc.yolo.scapegoat.dev \"go-go-goja\""}],"response_length":"long"}
```

## Turn 32 - assistant (thinking)

- Message ID: `8e4d16cc-e250-4961-8040-1706c39fa971`

<details><summary>Thinking</summary>

**Inspected key files and searched web and parc.yolo.scapegoat.dev**


</details>

## Turn 33 - assistant (tool call)

- Message ID: `d7a2d656-aecb-45c8-aefe-c1bf6e891915`
- Model: `gpt-5-6-pro`

```unknown
bash -lc curl -fsSL --max-time 30 'https://parc.yolo.scapegoat.dev/note/research/kb/projects/go-go-goja' -o /tmp/parc-go-go-goja.html && wc -c /tmp/parc-go-go-goja.html && head -c 500 /tmp/parc-go-go-goja.html
```

## Turn 34 - assistant (thinking)

- Message ID: `bf593d49-09df-495f-b236-42b5f4e597bc`

<details><summary>Thinking</summary>

**Downloaded content with curl**


</details>

## Turn 35 - assistant (tool call)

- Message ID: `7e878b40-7bae-478f-ba61-5d2134d88bba`
- Model: `gpt-5-6-pro`

```json
{"search_query":[{"q":"dns.google resolve parc.yolo.scapegoat.dev A"}],"response_length":"short"}
```

## Turn 36 - assistant (thinking)

- Message ID: `bf92c354-0a58-483e-acbd-1d65843c96a0`

<details><summary>Thinking</summary>

**Searched DNS queries and multiple websites for domain resolution**


</details>

## Turn 37 - assistant (tool call)

- Message ID: `52b49baa-a496-4879-8de9-27fe53a1363a`
- Model: `gpt-5-6-pro`

```unknown
bash -lc curl -kfsSL --max-time 20 -H 'accept: application/dns-json' 'https://1.1.1.1/dns-query?name=parc.yolo.scapegoat.dev&type=A'
```

## Turn 38 - assistant (thinking)

- Message ID: `8cf95aea-3d69-448d-86a2-667dc72b4036`

<details><summary>Thinking</summary>

**Queried DNS using DoH with curl**


</details>

## Turn 39 - assistant (tool call)

- Message ID: `dafa2551-bc9f-49a4-81b6-c19f57e0ea79`
- Model: `gpt-5-6-pro`

```json
{"search_query":[{"q":"\"Retro Obsidian Publish\" GitHub"},{"q":"\"Retro Obsidian Publish\" API note"},{"q":"\"Retro Obsidian Publish\" source code"},{"q":"Obsidian Publish clone \"Retro\" GitHub"}],"response_length":"long"}
```

## Turn 40 - assistant (thinking)

- Message ID: `674e9b22-7c72-4965-b246-df6772ee4d65`

<details><summary>Thinking</summary>

**Searched multiple websites and platforms for relevant information**


</details>

## Turn 41 - assistant (tool call)

- Message ID: `2ce01afb-f4e3-4fa9-9c2c-9ef106afda4f`
- Model: `gpt-5-6-pro`

```json
{"open":[{"ref_id":"turn797149search1"}],"response_length":"long"}
```

## Turn 42 - assistant (thinking)

- Message ID: `9338a3a7-4c94-4300-8add-effc3901340d`

<details><summary>Thinking</summary>

**Searched the web and aiseckit.com**


</details>

## Turn 43 - assistant (tool call)

- Message ID: `84cff8d3-bfe9-455a-b482-9e9ee85e9133`
- Model: `gpt-5-6-pro`

```json
{"search_query":[{"q":"site:jina.ai reader API query parameter url r.jina.ai target URL"},{"q":"site:github.com/jina-ai/reader r.jina.ai URL encoding API"},{"q":"Jina Reader API POST URL endpoint documentation"}],"response_length":"long"}
```

## Turn 44 - assistant

- Message ID: `ec8fc8bd-714a-4b12-a606-0bb97001f4ec`
- Model: `gpt-5-6-pro`

Concrete blockers: activation discards validated capabilities, timer/database restrictions leak, and manifests ignore entrypoints. Context cancellation cannot stop running JavaScript, so hard deadlines require isolated workers.

## Turn 45 - assistant (thinking)

- Message ID: `41a59255-ae42-4605-8427-640cb6e07259`

<details><summary>Thinking</summary>

**Searched Jina Reader API, GitHub, and web content**


</details>

## Turn 46 - assistant (thinking)

- Message ID: `429abe06-e0fa-4c75-9a67-06073716ce34`

<details><summary>Thinking</summary>

**Searched GitHub for widget-dsl and related terms**


</details>

## Turn 47 - assistant (tool call)

- Message ID: `200b3484-99f2-4e96-b490-9553926bb16f`
- Model: `gpt-5-6-pro`

```json
{"search_query":[{"q":"github \"widget-dsl\" \"go-go-golems\""},{"q":"github \"research/kb/projects/widget-dsl\""},{"q":"github \"research/kb/projects/go-go-goja\""},{"q":"\"widget DSL\" \"go-go-golems\""}],"response_length":"long"}
```

## Turn 48 - assistant (thinking)

- Message ID: `d8bcddfd-9caf-4766-9147-9b4637464430`

<details><summary>Thinking</summary>

**Searched multiple sites for widget DSL and more**


</details>

## Turn 49 - assistant (thinking)

- Message ID: `42428b36-c47b-42ef-b0e8-4729131347e3`

<details><summary>Thinking</summary>

**Fetched and inspected code, analyzed trust model and gaps**


</details>

## Turn 50 - assistant (thinking)

- Message ID: `f195d1d7-aa76-4e68-a1c2-44ae8691748c`

<details><summary>Thinking</summary>

**Inspected issues in capability management and repository functionality**


</details>

## Turn 51 - assistant (thinking)

- Message ID: `810beeac-be61-42cb-ae93-ab937cf175a9`
- Model: `gpt-5-6-pro`

<details><summary>Thinking</summary>

**Considering pool and load behavior**

Analyzing potential issues with worker pools and synchronization. The pool might face deadlock or race conditions during worker acquisition and closure, especially with failure handling and indefinite loading if source code introduces randomness.

**Considered pool and load behavior**


</details>

## Turn 52 - assistant (thinking)

- Message ID: `220c5d47-1854-49b0-8485-d9b84a1dd962`

<details><summary>Thinking</summary>

**Inspected capability binding for invocation and cleanup**


</details>

## Turn 53 - assistant (thinking)

- Message ID: `4d56e8a8-d05b-4995-b283-630b139cbca1`
- Model: `gpt-5-6-pro`

<details><summary>Thinking</summary>

**Analyzing potential bugs**

I'm thinking through how various bugs could affect call handling, context management, and object binding. There might be memory leaks or unexpected issues with prototype pollution, and I’ll need safeguards for concurrency limits and validation.

**Analyzed potential bugs**


</details>

## Turn 54 - assistant (thinking)

- Message ID: `5bfc785d-df47-4ce4-8ca2-345b73ae805c`

<details><summary>Thinking</summary>

**Evaluated bug behavior and inspected code for potential issues**


</details>

## Turn 55 - assistant (thinking)

- Message ID: `6e9cbcd8-01d5-4fd1-848e-36b10b5b2f64`
- Model: `gpt-5-6-pro`

<details><summary>Thinking</summary>

**Reviewing user request**

I’m analyzing the user's deep architecture and code review request. The goal is to review the platforms’ structure, security, release management, and integration points for JS hosting. I’ll focus on key areas and gaps but won't cover all files unless needed.

**Exploring code and repo status**

I’m analyzing the Goja and Go-Host repos, focusing on architecture, capabilities, deployment, and security. I’ll also consider potential issues like resource limits, manifest validation, and the management of global state.

**Reviewing system issues and improvements**

I’m analyzing several issues with activation, cleanup, runtime, and security, such as unaddressed rollback and resource management, while also looking at the IdP code for platform scalability and key functionality gaps.

**Reviewed user request and explored code and system issues**


</details>

## Turn 56 - assistant (thinking)

- Message ID: `0947be9e-df0e-414b-b50a-715b51a7c2c7`

<details><summary>Thinking</summary>

**Searched repositories for parc/widget and inspected repo content**


</details>

## Turn 57 - assistant (tool call)

- Message ID: `68cff04f-2cd3-40d6-82d4-2a5608904bbe`
- Model: `gpt-5-6-pro`

```unknown
bash -lc git ls-remote https://github.com/go-go-golems/go-go-parc.git HEAD
```

## Turn 58 - assistant (thinking)

- Message ID: `b1e6e3d2-29ca-4934-a020-15ae3629b935`

<details><summary>Thinking</summary>

**Fetched remote Git repository data**


</details>

## Turn 59 - assistant (thinking)

- Message ID: `c26c1c76-62d9-4b78-ae0b-17c9f3c1ea13`

<details><summary>Thinking</summary>

**Searched files in GitHub repository**


</details>

## Turn 60 - assistant (tool call)

- Message ID: `26428e6b-231f-4e46-8263-a84523f7c356`
- Model: `gpt-5-6-pro`

```json
{"open":[{"ref_id":"https://api.github.com/repos/go-go-golems/go-go-parc/git/trees/main?recursive=1"}],"response_length":"long"}
```

## Turn 61 - assistant (thinking)

- Message ID: `a3af364c-04a8-4b59-b900-c24df521b249`

<details><summary>Thinking</summary>

**Searched multiple sites for go-go-parc API and repos**


</details>

## Turn 62 - assistant (thinking)

- Message ID: `47aca8a5-0ef9-495d-9a05-02d7976eb483`

<details><summary>Thinking</summary>

**Fetched repo metadata and file content from GitHub**


</details>

## Turn 63 - assistant (thinking)

- Message ID: `5eaab428-95eb-49ad-b309-9b687d40b07f`

<details><summary>Thinking</summary>

**Inspected repository homepage, searched commits, and fetched diffs**


</details>

## Turn 64 - assistant (thinking)

- Message ID: `36759dfd-356e-4427-8a86-678641a5553d`

<details><summary>Thinking</summary>

**Searched and fetched commit details for widget-dsl and go-go-goja**


</details>

## Turn 65 - assistant (thinking)

- Message ID: `2954bd66-e66e-4a2c-a086-37e03071448b`

<details><summary>Thinking</summary>

**Inspected runtime plan and searched for authentication details**


</details>

## Turn 66 - assistant (thinking)

- Message ID: `b9f56eb0-0667-4cec-885f-5099c2ded618`

<details><summary>Thinking</summary>

**Fetched README sections, commit details, and analyzed code structure**


</details>

## Turn 67 - assistant (thinking)

- Message ID: `60331ad3-5a59-4b22-8065-4b60407cbb2e`

<details><summary>Thinking</summary>

**Fetched and inspected database migration, documentation, and files**


</details>

## Turn 68 - assistant (thinking)

- Message ID: `375ec607-5884-41dc-aefd-390033f43a3f`

<details><summary>Thinking</summary>

**Identified security issues and searched commits in repository**


</details>

## Turn 69 - assistant (thinking)

- Message ID: `59e276d7-c971-435b-bb01-1963a277f662`

<details><summary>Thinking</summary>

**Searched repository for lambda, inspected commits, and fetched files**


</details>

## Turn 70 - assistant (thinking)

- Message ID: `6f9e1ffb-f3f7-4c81-9cbd-c8dd35115981`

<details><summary>Thinking</summary>

**Searched and fetched commit data for go-go-goja project**


</details>

## Turn 71 - assistant (tool call)

- Message ID: `4015aaad-e169-49b8-a471-3e4813d18faa`
- Model: `gpt-5-6-pro`

```json
{"search_query":[{"q":"site:github.com/dop251/goja README interrupt runtime not goroutine safe"},{"q":"site:github.com/google/gvisor docs sandbox containers security isolation"},{"q":"site:firecracker-microvm.github.io security process isolation microVM"}],"response_length":"long"}
```

## Turn 72 - assistant (thinking)

- Message ID: `6f282482-abc3-4c19-965e-d57a218aefd0`

<details><summary>Thinking</summary>

**Searched GitHub for Goja security and isolation details**


</details>

## Turn 73 - assistant (thinking)

- Message ID: `f4d725af-9275-48f1-ab5e-3ac772bbb719`

<details><summary>Thinking</summary>

**Fetched README from GitHub repository**


</details>

## Turn 74 - assistant (tool call)

- Message ID: `eabd05b6-f510-4dc0-aecf-29dc7b81b691`
- Model: `gpt-5-6-pro`

```json
{"search_query":[{"q":"site:docs.stripe.com billing entitlements feature access subscriptions webhook official"},{"q":"site:docs.stripe.com webhooks signature idempotency official"},{"q":"site:docs.stripe.com billing subscriptions lifecycle entitlements active entitlement summary"}],"response_length":"long"}
```

## Turn 75 - assistant (thinking)

- Message ID: `1d266ca6-93ff-4070-9c1a-2e69e9e859b2`

<details><summary>Thinking</summary>

**Searched official Stripe documentation on billing and webhooks**


</details>

## Turn 76 - assistant (thinking)

- Message ID: `643eb760-77cc-44a5-adb2-91d330d01e49`

<details><summary>Thinking</summary>

**Evaluated signature standards and fetched code for inspection**


</details>

## Turn 77 - assistant (thinking)

- Message ID: `aa95c04c-a55e-48d6-964c-51ce2f698f60`
- Model: `gpt-5-6-pro`

<details><summary>Thinking</summary>

**Reviewing system architecture**

I’m assessing the user’s platform approach, including how modules, runtime plans, and security gaps are connected. The xgoja setup, lifecycle, and billing system are under review for improvements.

**Reviewing runtime and module specs**

I’m diving into the xgoja and go-go-host specifics, inspecting module registration, lifecycle, and runtime composition. The primary focus is integrity in execution, isolation, and security for deployment readiness.

**Reviewed system architecture, runtime, and module specs**


</details>

## Turn 78 - assistant (thinking)

- Message ID: `9634392d-fbeb-4fc1-bdad-d90d33bc2157`

<details><summary>Thinking</summary>

**Fetched and cited GitHub file contents and runtime information**


</details>

## Turn 79 - assistant (thinking)

- Message ID: `dd2a92f9-8eb5-4dc1-82ef-3448f88c8b3e`

<details><summary>Thinking</summary>

**Inspected code and fetched relevant files for Lambda API details**


</details>

## Turn 80 - assistant (tool call)

- Message ID: `cd75c439-b721-4f81-92e6-a8f0769af273`
- Model: `gpt-5-6-pro`

```json
{"search_query":[{"q":"site:gvisor.dev docs production security model untrusted code runsc OCI runtime"},{"q":"site:docs.stripe.com billing entitlements active entitlement summary updated webhook idempotency subscriptions"}],"response_length":"long"}
```

## Turn 81 - assistant (thinking)

- Message ID: `ddbd46ef-8c4e-416e-be21-a45f5bac102c`

<details><summary>Thinking</summary>

**Searched gVisor and Stripe documentation for webhooks and signatures**


</details>

## Turn 82 - assistant (thinking)

- Message ID: `f686694e-9dc3-41c6-9fe4-a257218acc3f`

<details><summary>Thinking</summary>

**Searched files in GitHub repository**


</details>

## Turn 83 - assistant (tool call)

- Message ID: `69faad8c-4d43-4d21-88cf-6b50193e91bd`
- Model: `gpt-5-6-pro`

```json
{"search_query":[{"q":"site:parc.yolo.scapegoat.dev/note/research/kb/projects/widget-dsl \"Widget DSL v3\""},{"q":"site:parc.yolo.scapegoat.dev/note/research/kb/projects/go-go-goja \"go-go-goja Runtime System\""}],"response_length":"medium"}
```

## Turn 84 - assistant (thinking)

- Message ID: `8dfd6ab2-f4e8-4e09-aba0-a813a76d17d3`

<details><summary>Thinking</summary>

**Reviewed repository commits, branches, and source documentation**


</details>

## Turn 85 - assistant (thinking)

- Message ID: `c384abe6-154e-4498-a473-7be11c612087`

<details><summary>Thinking</summary>

**Evaluated code audit scope, security, and designed data models**


</details>

## Turn 86 - assistant (tool call)

- Message ID: `281e6748-cdbc-47ee-839e-8b346c32f192`
- Model: `gpt-5-6-pro`

```json
{"open":[{"ref_id":"https://r.jina.ai/https://parc.yolo.scapegoat.dev/note/research/kb/projects/widget-dsl"},{"ref_id":"https://r.jina.ai/https://parc.yolo.scapegoat.dev/note/research/kb/projects/go-go-goja"}],"response_length":"long"}
```

## Turn 87 - assistant (thinking)

- Message ID: `bf773146-d78d-4cce-805f-557e5a3f18a0`

<details><summary>Thinking</summary>

**Searched multiple websites including Jina.ai and arxiv.org**


</details>

## Turn 88 - assistant (tool call)

- Message ID: `af9c9d40-d57d-4055-871c-f7681c269a3e`
- Model: `gpt-5-6-pro`

```unknown
bash -lc git ls-remote https://github.com/go-go-golems/go-go-host.git HEAD
```

## Turn 89 - assistant (thinking)

- Message ID: `183efde3-fc71-41df-abc0-93409dcfa484`

<details><summary>Thinking</summary>

**Tested git ls-remote in container**


</details>

## Turn 90 - assistant (thinking)

- Message ID: `aa07b05e-453e-454e-9e63-b1349ca09757`

<details><summary>Thinking</summary>

**Fetched directory listing from repository**


</details>

## Turn 91 - assistant

- Message ID: `7641d8ab-47c5-4b82-9876-0d24d05f4622`
- Model: `gpt-5-6-pro`

The architecture now converges on TinyIDP-style typed effect plans, host-owned security operations, and signed content-addressed runtime profiles. The MVP should separate pooled functions from isolated long-lived services.

## Turn 92 - assistant (thinking)

- Message ID: `fc9af521-9c1b-4162-aa2e-6cdfa7868308`

<details><summary>Thinking</summary>

**Fetched runtime plan, documentation, and file content from repositories**


</details>

## Turn 93 - assistant (thinking)

- Message ID: `645131d6-f18a-46f2-b7c1-5113ec715822`

<details><summary>Thinking</summary>

**Evaluated architecture and citations for PARC review**


</details>

## Turn 94 - assistant (tool call)

- Message ID: `b929a760-3188-49a5-bbfe-e56c2746065f`
- Model: `gpt-5-6-pro`

```json
{"paths":["GitHub"],"query":"get_file_contents"}
```

## Turn 95 - assistant (tool call)

- Message ID: `96b6f7ba-ddcc-4708-b149-d4566affbbf3`
- Model: `gpt-5-6-pro`

```json
{"paths":["GitHub"],"query":"tree"}
```

## Turn 96 - assistant (tool call)

- Message ID: `9f8826ab-f1b3-4f71-b21e-9901a633908c`
- Model: `gpt-5-6-pro`

```json
{"paths":["GitHub"],"query":"branch"}
```

## Turn 97 - assistant (tool call)

- Message ID: `f9359395-4180-4dc9-af11-c523963f2da3`
- Model: `gpt-5-6-pro`

```json
{"paths":["GitHub"],"query":"search_repositories"}
```

## Turn 98 - assistant (tool call)

- Message ID: `0dd04089-7f5a-44dc-b9b4-415f6377b6ef`
- Model: `gpt-5-6-pro`

```json
{"uri":"/response/turn56","query":"research/kb/projects/widget-dsl"}
```

## Turn 99 - assistant (tool call)

- Message ID: `4ff33741-ecf5-45d7-8f65-77c4b457b226`
- Model: `gpt-5-6-pro`

```json
{"uri":"/response/turn56","start_line":1,"num_lines":80}
```

## Turn 100 - assistant (tool call)

- Message ID: `8aa67dfb-efc2-45c2-aa2e-6dc9b00dab4c`
- Model: `gpt-5-6-pro`

```json
{"uri":"/response/turn65","query":"X-Go-Go"}
```

## Turn 101 - assistant (tool call)

- Message ID: `4e026d74-57ac-4c58-ad52-252e7e5a6c7e`
- Model: `gpt-5-6-pro`

```json
{"uri":"/response/turn74","query":"internal/control"}
```

## Turn 102 - assistant (tool call)

- Message ID: `df5330a3-1c26-4212-85fd-5deb0077e9d3`
- Model: `gpt-5-6-pro`

```json
{"uri":"/response/turn57","query":"filename"}
```

## Turn 103 - assistant (tool call)

- Message ID: `fb006de2-a3fd-49cf-a836-e03e2c92f851`
- Model: `gpt-5-6-pro`

```json
{"paths":["GitHub"],"query":"search"}
```

## Turn 104 - assistant (tool call)

- Message ID: `13e74833-cd91-4bde-b450-a6c9ee365c0f`
- Model: `gpt-5-6-pro`

```json
{"paths":["GitHub"],"query":"fetch_file"}
```

## Turn 105 - assistant (recap)

- Message ID: `366a1146-f621-54b0-8a0b-25dfec50e8e0`

> _Worked for 50m 21s_

## Turn 106 - assistant

- Message ID: `c351bc50-a3e7-4324-93cc-b10f0f185e04`
- Model: `gpt-5-6-pro`

# Architectural verdict

The platform is viable, but it should **not** be implemented by continuing to expand the current in-process `go-go-host` runtime.

The correct decomposition is:

- **`go-go-goja` / `xgoja`** becomes the trusted runtime SDK, native-module linker, TypeScript surface generator, and build planner.
- A new **generic application-program contract**, extracted from the `tiny-idp` scripting work, becomes the static description of routes, functions, pages, actions, effects, capabilities, schemas, and budgets.
- **`go-go-host`** contributes the control-plane concepts—organizations, projects, domains, releases, agents, grants, audit, quotas—but its current `Supervisor` and `SiteRuntime` should be replaced as the production execution plane.
- A new **isolated worker plane** runs one tenant/release per sandbox or process group.
- **Tiny-IDP** remains a separate identity kernel and managed identity service. Untrusted customer JavaScript must not execute inside the IdP process.
- The **Widget DSL** becomes a versioned server-driven UI protocol. The current `ui.dsl` HTML builder should not be the default managed UI API.

I traced the primary production paths: xgoja planning and generation, provider registration, engine/runtime ownership, deployment ingestion and activation, routing, sessions, UI rendering, agent/audit behavior, the `task/prod-tiny-idp` branch, and the source commits behind the two PARC notes. This is not a line-by-line audit of every test, generated dashboard asset, or dependency.

One scope caveat: the PARC material describes a `WarmPoolSupervisor` Lambda layer, but I could not verify that implementation on the current public `go-go-host` main. I therefore treat that material as a design source, not as deployed code already available. fileciteturn75file12L82-L93

---

# Release blockers in the current code

## 1. Capability enforcement is currently bypassed

Bundle validation computes and records requested and effective capabilities. fileciteturn81file0L121-L163

However:

- The dry-run runtime is built with `hostruntime.DefaultCapabilities()`.
- The activated runtime is also built with `DefaultCapabilities()`.
- `NewSiteRuntime` always opens SQLite and always registers `database` and `db`, regardless of `CapabilitySet.Database`.

That means the policy decision made during validation is not the policy actually used at execution time. fileciteturn78file0L28-L47 fileciteturn78file0L150-L180 fileciteturn79file0L43-L91

This is the first issue to fix. A paid-module platform cannot use a best-effort capability list. The resolved module set and permission set must be:

1. Canonicalized.
2. Persisted as part of the immutable release.
3. Signed or covered by the release digest.
4. Used directly to construct the worker.
5. Rechecked by the worker before running code.

There should be no `DefaultCapabilities()` on a hosted production path. The default should be no authority.

## 2. HTTP timeouts do not stop JavaScript execution

`runtimeowner.Call` schedules work on the VM owner. When the caller context expires, `Call` returns an error, but there is no interrupt in that path; already-running JavaScript can continue. fileciteturn82file0L33-L56

`go-go-host` applies `http.TimeoutHandler`, which limits how long the HTTP response waits. It does not terminate the JavaScript callback. fileciteturn80file0L127-L140

Goja itself is deliberately single-owner and exposes an explicit `Runtime.Interrupt` mechanism. fileciteturn77file0L71-L83 fileciteturn77file0L279-L301

The `tiny-idp` branch demonstrates the better pattern:

- Invocation-specific deadline.
- `VM.Interrupt` when the deadline expires.
- Mark the worker unsafe.
- Clear the interrupt only during cleanup.
- Discard the worker instead of returning it to the pool. fileciteturn96file0L22-L49

For hostile or agent-generated programs, even that is not enough by itself. The final sequence should be:

1. Cancel invocation capabilities.
2. Interrupt the Goja VM.
3. Allow a very short cleanup interval.
4. Discard the VM unconditionally after interruption.
5. Kill the worker process if native code or a broken module does not return.
6. Let cgroups enforce memory, CPU, and process limits.

One active invocation per VM is the simplest safe ownership model. A single site-wide VM means one infinite loop can block every request for that site.

## 3. Activation is not transactionally consistent

The current supervisor creates and health-checks a candidate, swaps the in-memory routing maps, then asynchronously closes the previous runtime. fileciteturn80file0L9-L50

Only after that does the control service call `MarkDeploymentActive`. If the database operation fails, live traffic and persisted control-plane state disagree. fileciteturn78file0L175-L181

There is also no graceful drain before closing the old runtime. Closing with the activation request’s context can interrupt or partially close a runtime still handling requests. The host map assignment also has no visible collision check against another site already owning the same hostname. fileciteturn80file0L28-L49

Replace this with a desired-state deployment model:

1. Build the candidate.
2. Start it under a new immutable release ID.
3. Record worker readiness.
4. Perform one database compare-and-swap of the environment’s traffic generation.
5. Emit an outbox event in the same transaction.
6. Routers observe the new generation.
7. Drain the previous generation.
8. Retire it after in-flight requests reach zero or a hard drain deadline expires.

The database should be the source of truth. An in-memory supervisor should be a reconciler of that state, never a competing source of truth.

## 4. Bundle ingestion is vulnerable to memory exhaustion

The validator reads the entire archive into memory, then reads every compressed entry using `io.ReadAll`. Uncompressed-byte limits are checked only after all entries have already been materialized. fileciteturn81file0L86-L116 fileciteturn81file0L218-L279

It also canonicalizes names before validation and does not reject duplicate canonical paths. Multiple entries can therefore collapse onto the same destination, with the later write winning. fileciteturn81file0L282-L306 fileciteturn81file0L331-L352

Keep the current good ideas—symlink rejection, path confinement, manifest validation, SHA-256—but rewrite ingestion to:

- Stream data rather than buffering the full archive.
- Enforce compressed and uncompressed totals during reading.
- Enforce a per-file maximum.
- Reject declared sizes that exceed policy before reading.
- Limit compression ratio.
- Reject duplicate raw and canonical names.
- Reject multiple manifests.
- Use strict JSON decoding with unknown-field rejection.
- Stage extraction into a temporary directory and atomically rename it.
- Clean up failed deployment placeholders and dry-run data.
- Store source bundles in content-addressed object storage.

## 5. The current `ui.dsl` is not safe as a managed UI contract

The module exposes:

- `script` and `style` elements.
- A `raw()` primitive.
- Arbitrary attribute maps.
- Normalization failures converted into visible text rather than deployment errors. fileciteturn100file0L23-L38 fileciteturn100file0L76-L93

The renderer emits `RawHTML` without escaping and writes arbitrary attribute names and values. Attribute value escaping does not make event attributes, `javascript:` URLs, CSS values, or arbitrary form actions safe. fileciteturn101file0L18-L47 fileciteturn101file0L51-L123

This API can remain as an explicitly privileged compatibility module, such as `unsafe.html`, behind a high-risk permission and a restrictive Content Security Policy. It should not be part of the safe hosted profile.

## 6. Production activation enables development error behavior

Activation currently sets `Dev: true`. fileciteturn78file0L162-L174

The web host returns the full JavaScript handler error when `Dev` is enabled. fileciteturn92file0L97-L103

That can expose stack traces, paths, SQL errors, module details, and user data. Production releases must force development errors off. Preview environments can expose sanitized diagnostics only to authenticated project members.

The current session mechanism is also not authentication. It is a long-lived opaque anonymous ID; the default duration is one year, and `Secure` is false unless explicitly set. fileciteturn91file0L47-L86

It can be retained as an anonymous cart or browser-correlation ID after tightening defaults, but it must not represent a logged-in user.

## 7. The database module needs hosting-specific hardening

The generic database module:

- Can log a data source name on configuration failure.
- Logs raw SQL statements.
- Materializes complete query results in memory.
- Has no module-level row or result-byte limit. fileciteturn93file0L242-L259 fileciteturn93file0L275-L315

The hosted wrapper should add:

- Query and transaction deadlines.
- Maximum rows and maximum encoded result bytes.
- Maximum statements and transactions per invocation.
- Automatic rollback when an invocation ends.
- SQL/DSN redaction.
- SQLite authorizer restrictions where practical.
- Disabled extension loading and controlled `ATTACH` behavior.
- Migration-specific authority separate from ordinary request-time SQL.

## 8. The `tiny-idp` worker pool has a shutdown defect

`Pool.Close` sets `closed = true`, waits for active workers, and can return on context cancellation before invoking `p.cancel()` or closing the workers. A later `Close` returns immediately because `closed` is already true. As written, that can make the leak permanent. fileciteturn83file0L136-L182

Separate “no longer accepting work” from “resources fully closed,” and make cleanup retryable. Also repair pool capacity asynchronously when replacement creation fails; currently a failed replacement can shrink the pool indefinitely. fileciteturn83file0L80-L104

---

# What is worth preserving

## `go-go-goja` and xgoja

Preserve:

- The distinction between planning/building and creating individual runtimes.
- Explicit provider registration.
- Runtime module selection by provider, name, alias, and validated configuration.
- TypeScript declaration generation.
- Closed static source-graph validation.
- Runtime ownership, closer registration, lifecycle context, and owner scheduling.
- Generated runtime packages with embedded plans.

The xgoja v2 plan already treats selected providers and native modules as the authoritative runtime surface, while browser bundles remain separate assets. fileciteturn87file0L11-L24 Native modules are selected by provider and can have aliases and typed configuration. fileciteturn87file0L149-L199 Static imports are validated against a closed graph, and nonliteral dynamic imports are rejected. fileciteturn87file0L259-L278

That is almost exactly the build foundation a coding-agent-oriented platform needs.

Change:

- Add a hosted module security descriptor.
- Add runtime ABI and provider/module version identity.
- Freeze registries after construction.
- Remove implicit/default modules on all hosted paths.
- Add an invocation-level interrupt-and-discard API to the owner layer.
- Restrict host mutation of embedded runtime plans.
- Separate build provenance from runtime configuration.

The current `RuntimePlan` intentionally omits provider import paths, module versions, replacements, and other build-only inputs. Its runtime module entries contain only provider, name, alias, and configuration. fileciteturn97file0L3-L10 fileciteturn97file0L52-L66 That is insufficient to identify a paid, reproducible hosted runtime.

Generated bundles also allow a host callback to modify the decoded plan before constructing providers and the host. That is useful for deployment bindings, but a signed release must constrain this to approved binding substitutions; it must not allow module or permission mutation. fileciteturn98file0L46-L54 fileciteturn98file0L82-L110

## `go-go-host`

Preserve:

- Organizations, memberships, sites/projects, domains, quotas, agents, keys, grants, nonces, deployment records, and audit concepts.
- Immutable deployment IDs and separate upload/activation operations.
- Validation reports and smoke checks.
- Machine identities distinct from human credentials.
- Agent grants scoped to sites, paths, channels, and activation.
- Postgres/sqlc layering and explicit store boundaries.

The existing data model is a good control-plane skeleton. fileciteturn99file0L22-L40

Change or replace:

- Replace `SiteRuntime` and the in-process `Supervisor` with remote or local isolated workers.
- Split deployment into source revision, build, artifact, release, rollout, and traffic-generation records.
- Make audit writes transactionally reliable instead of ignoring errors. Several agent and deployment mutations currently discard audit failures. fileciteturn102file0L18-L30 fileciteturn102file0L79-L119
- Move bundles and generated artifacts from local mutable paths to object storage.
- Add workers, leases, invocations, usage, entitlements, module versions, bindings, secrets, and outbox records.
- Replace direct “swap runtime then update database” behavior with reconciliation.

Retire from the primary platform path:

- Recursive execution of every `.js` file in lexical order. The manifest has an `entrypoint`, but the current loader walks the entire scripts directory and executes all JavaScript files. fileciteturn79file0L138-L184
- `http.TimeoutHandler` as the execution limiter.
- One shared VM per site.
- Always-on per-site SQLite in the web daemon.
- Mutable boolean capability sets.
- The current `ui.dsl` as the safe renderer.
- Anonymous cookie identity as application authentication.

## `tiny-idp`

Preserve:

- The strict OAuth/OIDC kernel.
- The explicit boundary where Go owns protocol validation, cookies, secrets, cryptographic operations, replay-sensitive state, effects, and artifact issuance.
- The serializable `Program` contract that contains no Goja values.
- Handler schemas, allowed outcomes, required capabilities, allowed effects, and budgets.
- Compile-time validation and fingerprints.
- Opaque secret handles and native-verified evidence.
- Explicit browser continuations.
- Exclusive VM workers and discard-after-interrupt behavior.

The `Program` type deliberately separates the serializable program description from VM-owned callback functions. fileciteturn89file0L3-L20 Each lambda has schemas, outcomes, capabilities, effects, and invocation budgets. fileciteturn90file0L20-L39

That model should be generalized into a repository-neutral package, rather than remaining specific to identity.

Keep the trust warning. The design explicitly says that the in-process sandbox is not containment for hostile code and that untrusted tenant-authored JavaScript must not run in the IdP process. fileciteturn84file0L241-L269

## Widget DSL

Preserve the PARC design direction:

- JavaScript composes a serializable page IR.
- Go owns data access and execution.
- React owns browser rendering.
- Actions and bindings are data, not serialized callbacks.
- The wire protocol is versioned.
- Validation includes IR goldens and real browser rendering tests.

That is a much stronger interface for coding agents than arbitrary HTML or arbitrary React components. fileciteturn56file0L1-L1

Change:

- Extract the generic wire protocol from Vault-specific components.
- Pin the renderer/component-registry version into each release.
- Put strict limits on nodes, depth, text, properties, and total encoded size.
- Validate all actions and URLs.
- Make server actions refer to named handlers in the application program contract.
- Keep unsafe HTML out of the normal protocol.
- Fail deployment validation on malformed nodes; never render validation errors into the page.

---

# Recommended platform architecture

```text
                          TRUSTED CONTROL PLANE

  Dashboard / API / CLI / Coding Agents
                    |
              Auth + RBAC
                    |
       Projects / Environments / Domains
       Releases / Policies / Approvals
       Modules / Entitlements / Billing
       Identity Realms / Secrets / Audit
                    |
          PostgreSQL + transactional outbox
                    |
          signed desired release records
                    v

                          TRUSTED BUILD PLANE

  Source bundle or Git revision
        -> strict archive scanner
        -> JS/TS static graph
        -> application contract compiler
        -> policy and entitlement resolver
        -> xgoja runtime-profile resolver
        -> tests / SBOM / provenance
        -> signed content-addressed artifact or OCI image
                    |
                    v

                         EXECUTION PLANE

        Edge/router -> release traffic generation
                           |
              one tenant/release per sandbox
                           |
                   bounded VM worker pool
                           |
               capability/resource brokers
                           |
        database / object store / payments / auth / queues
```

## Control plane

The control plane should never execute tenant JavaScript. It manages:

- Organizations and members.
- Projects and environments.
- Domains and certificates.
- Module catalog and versions.
- Commercial entitlements.
- Resource bindings.
- Secrets metadata.
- Source revisions and builds.
- Releases and traffic generations.
- Agent keys, grants, signatures, and approvals.
- Audit and policy decisions.
- Usage aggregation and billing exports.

Use PostgreSQL as the authoritative state store. Every security-relevant state transition should write its audit/outbox event in the same transaction.

## Build plane

The build service should generate the xgoja specification itself. Customers upload JavaScript/TypeScript and an application manifest; they do not supply arbitrary Go provider imports, build tags, `replace` directives, or workspace settings.

This matters because xgoja supports local `go.work` discovery and a resolution precedence that can prefer replacements or workspace modules. That is appropriate for development but inappropriate for a hosted build supplied by a tenant or coding agent. fileciteturn87file0L123-L147

For production builds:

- Force workspace mode off.
- Resolve provider modules from an operator-controlled catalog.
- Pin exact Go module versions and checksums.
- Use a fixed Go toolchain and dependency mirror.
- Disallow arbitrary extra Go imports.
- Generate an SBOM and provenance record.
- Sign the output.
- Cache by the complete runtime-profile digest.

Do not dynamically download Go plugins into a long-lived universal worker. Prefer profile-specific binaries or images containing only the selected native modules.

At launch, use a small curated profile matrix, for example:

- Core HTTP/functions.
- Core plus SQLite.
- Core plus Widget UI.
- Core plus SQLite and Widget UI.
- Core plus managed payments.
- Core plus managed app authentication.

Later, build arbitrary allowlisted combinations on demand and cache them by profile digest.

## Execution plane

Each release should execute in a distinct OS process and, for different customers, a distinct sandbox. Goja is an interpreter boundary, not an operating-system security boundary.

A reasonable first production isolation layer is gVisor `runsc`. It implements an OCI runtime and a user-space application kernel, and its security guidance recommends putting different customers in different sandboxes. citeturn567569search3turn567569search6

Each worker should have:

- Read-only root filesystem.
- No host filesystem mounts.
- Dedicated unprivileged UID.
- Memory, CPU, PID, and file-size limits.
- No network by default.
- Egress only through a policy-enforcing proxy.
- Ephemeral writable storage except for explicit resource mounts.
- Short-lived workload identity.
- No control-plane database credentials.
- A signed release manifest and exact runtime lock.
- Bounded log output.
- Hard process termination as the final timeout mechanism.

A warm pool should be per release, not a shared pool of mixed tenants. A worker that is interrupted, panics in native code, violates a protocol, or exceeds a budget is discarded.

---

# Generalize the Tiny-IDP scripting model into an application compiler

The strongest idea in the reviewed code is not Express-style startup registration. It is the `tiny-idp` separation between:

1. A serializable, statically validated program contract.
2. VM-owned callback functions indexed by stable handler IDs.
3. Native capabilities supplied only for one invocation.
4. Structured outcomes and effects.

Create a new package, perhaps `go-go-program`, independent of both hosting and identity.

A generic program could contain:

```go
type Program struct {
    APIVersion   string
    Name         string
    Routes       map[string]RouteSpec
    Functions    map[string]HandlerSpec
    Pages        map[string]PageSpec
    Actions      map[string]HandlerSpec
    Schedules    map[string]ScheduleSpec
    Schemas      map[string]Schema
    Capabilities map[string]CapabilityRequirement
    Resources    map[string]ResourceRequirement
    Tests        []ProgramTest
}
```

A handler contract should include:

```go
type HandlerSpec struct {
    ID                   string
    Kind                 HandlerKind
    InputSchema          string
    OutputSchema         string
    RequiredCapabilities []CapabilityRequirement
    AllowedEffects       []EffectKind
    AuthPolicy           AuthPolicy
    Idempotency          IdempotencyPolicy
    Budget               InvocationBudget
    SourceLocation       SourceLocation
}
```

Budgets should cover more than timeout:

- Wall-clock time.
- CPU time where measurable.
- Maximum capability calls.
- Maximum concurrent capability calls.
- Maximum input and output bytes.
- Maximum log bytes.
- Maximum database rows.
- Maximum response body.
- Maximum continuation payload.
- Maximum total effects.
- Maximum network requests and bytes.

The compiler runs the source in a collector-only runtime. The DSL records routes, functions, pages, schemas, requirements, tests, and callback IDs. It then:

1. Produces canonical serializable JSON.
2. Validates the program graph.
3. Runs declarative tests using fake capabilities.
4. Calculates source, contract, and callback-registry fingerprints.
5. Emits a release contract.
6. Re-executes and verifies those fingerprints when a worker loads the artifact.

This is already the pattern in the Tiny-IDP branch: static analysis treats lambda code as opaque but constrained by declared schemas, capabilities, outcomes, effects, and continuation edges. fileciteturn84file0L108-L138

Make this the primary application API. Keep Express as a compatibility runtime for trusted or migrated applications, not as the long-term agent-facing interface.

A platform DSL might look like:

```javascript
const A = require("@gogo/app").v1;

module.exports = A.program("shop", app => {
  app.http("home", {
    method: "GET",
    path: "/",
    output: "widget.page/v3",
    capabilities: ["catalog.read"],
    budget: {
      timeoutMs: 100,
      maxCapabilityCalls: 10,
      maxOutputBytes: 262144,
    },
  }, async ctx => {
    const products = await ctx.cap.catalog.list({});
    return ctx.page.shop({ products });
  });

  app.action("start-checkout", {
    input: "checkout.request/v1",
    output: "checkout.result/v1",
    capabilities: ["payments.checkout.create"],
    effects: ["payment_session_create"],
  }, async ctx => {
    return ctx.cap.payments.createCheckout(ctx.input);
  });
});
```

JavaScript supplies business logic. Go supplies authority.

---

# Paid native modules and subscriptions

## Separate six concepts that are currently conflated

The platform needs distinct types for:

| Concept | Meaning |
|---|---|
| **Provider extension** | Compile-time Go contribution to xgoja. |
| **Runtime module** | A selected JS-visible CommonJS API. |
| **Permission** | Authority granted to executing code. |
| **Entitlement** | Commercial right held by an account. |
| **Quota** | Amount of a resource or operation allowed. |
| **Binding** | A concrete environment resource or credential connection. |

The current xgoja `PackageCapability` means an extension hook such as configuration sections, host-service contributions, or runtime initializers. It is not a security permission. Rename that concept to `ProviderExtension` or `ProviderContribution` before introducing commercial/runtime capabilities. fileciteturn94file0L26-L39 fileciteturn94file0L72-L117

## Extend the native module descriptor

The existing provider module has a good base: name, alias, description, configuration schema, TypeScript declaration, and factory. fileciteturn88file0L43-L53

A hosted module version additionally needs:

- Stable canonical module ID.
- Semantic version.
- Runtime ABI compatibility.
- Provider Go module, version, and checksum.
- Factory/source digest.
- Aliases.
- Risk or isolation class.
- Required permissions.
- Configuration schema.
- Binding schema.
- Secret types.
- Resource dependencies.
- Module dependencies and conflicts.
- Network policy.
- Lifecycle: build, runtime, or invocation.
- Concurrency model.
- State ownership.
- Migration contract.
- Metering dimensions.
- Pricing feature/SKU mapping.
- TypeScript declaration digest.
- Documentation digest.
- Deprecation and end-of-support state.

Aliases such as `database`, `db`, and `sqlite` must resolve to one canonical module/version and one entitlement. An alias must never become a policy bypass.

## Resolve subscriptions when creating a release

The release pipeline should:

1. Parse requested native modules.
2. Resolve exact catalog versions.
3. Check account entitlements.
4. Evaluate environment policy.
5. Resolve resource bindings.
6. Calculate effective permissions.
7. Generate the xgoja profile.
8. Build or retrieve the cached runtime artifact.
9. Emit an exact module lock.
10. Sign the release.

A release lock should contain at least:

```json
{
  "runtimeABI": "gogo-host/v1",
  "gojaVersion": "...",
  "goGoGojaVersion": "...",
  "toolchain": "...",
  "sourceDigest": "...",
  "programDigest": "...",
  "runtimeProfileDigest": "...",
  "policyDigest": "...",
  "entitlementSnapshot": "...",
  "modules": [
    {
      "id": "sqlite",
      "version": "1.3.2",
      "providerModule": "...",
      "providerSum": "...",
      "factoryDigest": "...",
      "alias": "db",
      "configDigest": "...",
      "binding": "primary"
    }
  ]
}
```

Do not mutate a running VM when a subscription changes. A changed module set produces a new release.

## Stripe should feed an internal entitlement ledger

Stripe should not be queried on every invocation. Stripe subscription activity is asynchronous, and Stripe exposes active entitlements and an `entitlements.active_entitlement_summary.updated` webhook for provisioning changes. citeturn567569search0turn567569search1

The flow should be:

```text
Stripe webhook
    -> verify signature
    -> deduplicate event
    -> append billing event
    -> update internal entitlement projection
    -> emit entitlement-changed outbox event
```

Stripe’s own guidance uses idempotency keys or durable deduplication records when the same logical event may be received more than once. citeturn963604search0

The entitlement snapshot used by a release should be immutable. A downgrade policy can:

- Immediately block new releases requiring the removed module.
- Allow an existing release to run for a defined grace period.
- Suspend it after grace.
- Permit immediate revocation for abuse or a security emergency.

That policy is a platform decision, not a Stripe status lookup buried inside a worker.

## SQLite is both a module and a resource

Treat these separately:

- The **SQLite module** is the JS API and native code.
- The **SQLite resource** is a persistent database instance, storage allocation, backup policy, migration state, and worker-placement constraint.
- The **binding** connects a release environment to that resource.

The current Tiny-IDP documentation correctly describes its SQLite implementation as single-active-node. fileciteturn86file0L27-L34 Use the same honesty for hosted SQLite:

- Pin the active worker or worker group to one volume.
- Use a distributed lease to prevent two writers being scheduled on separate nodes.
- Provide backup, verification, and restore.
- Separate schema migration from request execution.
- Do not promise arbitrary horizontal scale with a local SQLite file.

For scalable profiles, offer managed Postgres or a remote SQLite-compatible service as separate resource types.

---

# Release, agent, rollback, and audit model

## Split the current deployment record into distinct objects

Use these semantics:

- **Source revision**: exact uploaded archive or Git commit.
- **Build**: one attempt to compile a source revision under a runtime profile.
- **Artifact**: immutable signed executable/image plus SBOM and provenance.
- **Release**: artifact plus environment configuration, bindings, policy, and entitlement snapshot.
- **Deployment**: one attempt to make a release available.
- **Traffic generation**: immutable routing decision pointing traffic percentages to releases.
- **Worker revision**: concrete running instance or pool.
- **Rollback**: a new traffic generation targeting an explicitly selected previous release.

Do not overload one mutable deployment status with all of those meanings.

## Agent-generated releases

The existing machine-identity direction is good: agents, public keys, site-scoped grants, nonces, upload authorization, and separate human versus machine credentials. fileciteturn99file0L34-L40

An agent’s signed promotion request should cover a canonical payload containing:

- Organization, project, environment.
- Source revision digest.
- Build/artifact digest.
- Release digest.
- Expected current traffic generation.
- Exact module lock.
- Permission and policy digest.
- Binding/configuration digest.
- Migration plan digest.
- Idempotency key.
- Timestamp and nonce.
- Requested rollout policy.

The control plane should still recompute every policy decision. An agent signature proves who requested the change; it does not make the change safe.

Generate a machine-readable authority diff:

```text
+ module payments@1.2.0
+ permission network.egress: payments-provider
+ secret binding stripe-production
+ effect payment_session_create
~ database schema 12 -> 13
- module old-mailer@0.8.1
```

Require additional approval for changes involving:

- New native module.
- New network destination.
- New secret.
- Identity or payment authority.
- Destructive database migration.
- Custom domain or certificate.
- Unsafe HTML.
- Increased memory, timeout, or concurrency.
- Module major-version upgrade.

## Promotion and rollback

Promotion should use compare-and-swap against the expected traffic generation. Two agents must not be able to race and silently overwrite each other.

A safe sequence is:

```text
build candidate
    -> validate contract and tests
    -> start preview worker
    -> smoke and synthetic tests
    -> optionally canary
    -> candidate marked ready
    -> transactionally CAS traffic generation + audit + outbox
    -> routers adopt generation
    -> drain previous release
```

Rollback must name an exact release. “Previous validated deployment” is not sufficient because validation order is not necessarily traffic order, and a previous code release may not be compatible with the current database. The current rollback implementation chooses a previous validated deployment and activates it. fileciteturn78file0L185-L202

Code rollback and database rollback are different operations. Require:

- Expand/contract migrations.
- Compatibility windows.
- A backup before destructive migrations.
- Explicit declaration of whether a release can run against both old and new schema generations.
- A separate privileged restore workflow rather than automatically reversing arbitrary migrations.

## Audit

Audit must be evidence-grade:

- Append-only.
- Transactionally coupled to state mutation or emitted through a transactional outbox.
- Stable event names and schemas.
- Actor identity and key ID.
- Request and idempotency ID.
- Source, release, and policy digests.
- Before/after generation.
- Approval decision.
- Worker rollout result.

Security-relevant code should never use `_, _ = InsertAuditEvent(...)`.

---

# Identity architecture

There are two separate identity populations.

## Platform identity

These are your customers and their team members:

- Organization owners.
- Developers.
- Billing administrators.
- Release approvers.
- Coding agents.
- Platform operators.

Tiny-IDP strict mode can support this for an initial deployment, or the control plane can accept external OIDC. Its strict profile already has a good baseline: Authorization Code plus PKCE, exact redirect matching, server-side sessions, CSRF controls, secure-cookie production validation, restrictive security headers, persistent keys, and auditing. fileciteturn85file0L7-L26

## Hosted-application identity

These are the end users of a customer’s application. Do not put them into the same issuer, key set, subject namespace, or administrative domain as platform users.

Offer three application auth modes:

1. **Managed shared realm**  
   A logically isolated app/environment tenant in a separate identity service.

2. **Dedicated managed issuer**  
   Separate Tiny-IDP instance, database, keys, domain, backups, and lifecycle.

3. **External OIDC**  
   The customer supplies an existing issuer and client configuration.

Application JavaScript should receive verified claims such as:

```json
{
  "authenticated": true,
  "issuer": "...",
  "subject": "...",
  "tenant": "...",
  "scopes": ["..."],
  "roles": ["..."]
}
```

It should not receive passwords, signing keys, raw refresh tokens, session cookies, or the IdP database.

For customer-managed users, expose a narrow `users.v1` capability:

- Invite.
- Disable.
- Assign application role.
- Read a bounded public profile.
- Request password-reset or login links.
- List with pagination and quotas.

Do not expose the raw identity store.

## Scriptable identity workflows

The Tiny-IDP design explicitly keeps OAuth validation, cookies, credentials, cryptography, replay state, effects, and token issuance in Go. JavaScript receives bounded values and narrow capabilities. fileciteturn84file0L26-L52

Keep that invariant.

For tenant-authored identity workflows, execute the workflow in the isolated worker plane and communicate with Tiny-IDP over a typed internal protocol:

```text
Tiny-IDP validates protocol request
    -> invokes workflow release with bounded input
    -> receives structured outcome
    -> applies native effects
    -> stores continuation
    -> issues protocol artifact
```

Tiny-IDP must fail closed when the workflow service is unavailable or returns an invalid result.

Browser-spanning flows should use durable, versioned continuations. A Promise is not a durable representation of a form submission that may resume after a restart or on another node. fileciteturn84file0L45-L52

Continuation records must pin:

- Workflow release digest.
- Handler ID.
- Input and carry schema versions.
- Issuer/client binding.
- Browser/session binding.
- Expiry and one-time-use state.
- Migration policy when the application is upgraded before continuation resume.

---

# Web UI model

Support two primary paths.

## 1. Static browser applications

Customers build React, Vue, Svelte, or plain browser assets using standard frontend tooling. xgoja already makes the correct distinction: browser applications are built separately and included as assets rather than executed inside Goja. fileciteturn87file0L21-L24

The platform serves immutable, content-hashed assets from object storage or a CDN.

## 2. Widget IR pages

For agent-generated applications, the Widget DSL approach is more controllable:

```text
JavaScript handler
    -> returns versioned serializable page IR
    -> Go validates size, schema, actions, and policy
    -> browser renderer displays approved components
```

A production widget protocol needs:

- `schemaVersion`.
- Pinned renderer version.
- Component registry digest.
- Explicit component allowlist.
- Node, depth, collection, text, and total-byte limits.
- Typed properties.
- No arbitrary React component names.
- No serialized functions.
- No raw HTML by default.
- Strict URL and interpolation validation.
- Accessible component semantics.
- Localization boundaries.
- Cache keys that include release, user/tenant, locale, and data dependencies.

Actions should be data:

```json
{
  "type": "server",
  "handler": "start-checkout",
  "input": {
    "productId": {"from": "row.id"}
  }
}
```

The host maps that to a named handler in the program contract and applies:

- Authentication and authorization.
- CSRF protection.
- Input schema validation.
- Idempotency.
- Rate limits.
- Effect policy.
- Audit.

Go should own authoritative headers, cookies, redirects, CSRF tokens, and form action URLs. Tiny-IDP’s UI boundary already follows this principle: rendering models contain no protocol secrets, and renderers do not receive an `http.ResponseWriter`. fileciteturn84file0L181-L193

---

# Payments module design

Do not give ordinary scripts `STRIPE_SECRET_KEY` plus unrestricted `fetch`.

Provide a narrow native `payments.v1` capability:

- Create checkout session.
- Create customer portal session.
- Read a bounded subscription summary.
- Cancel or schedule cancellation under configured policy.
- Create refund requests with explicit authority.
- Retrieve configured products/prices.
- Accept verified webhook events.

The host should:

- Keep the API secret in a resource binding.
- Restrict permitted products, prices, currencies, and redirect domains.
- Generate or enforce idempotency keys.
- Verify webhook signatures using the exact raw request body.
- Deduplicate webhook events.
- Convert the event into native-verified evidence.
- Pass only that evidence to JavaScript.
- Apply sensitive effects through an effect plan.

This is the same security pattern as the Tiny-IDP design: JavaScript chooses business behavior; native code owns protocol verification, secrets, replay protection, and irreversible effects.

---

# Data-model additions

The existing control-plane entities should be extended with:

| Area | New entities |
|---|---|
| Source/build | `source_revisions`, `builds`, `build_checks`, `artifacts`, `artifact_attestations` |
| Runtime | `runtime_profiles`, `runtime_profile_modules`, `worker_revisions`, `worker_leases` |
| Release | `releases`, `release_bindings`, `release_permissions`, `release_entitlement_snapshots` |
| Traffic | `traffic_generations`, `traffic_allocations`, `rollout_events` |
| Modules | `module_catalog`, `module_versions`, `module_dependencies`, `module_pricing_features` |
| Billing | `billing_customers`, `subscriptions`, `entitlements`, `billing_events` |
| Resources | `resource_instances`, `resource_bindings`, `resource_backups`, `resource_migrations` |
| Identity | `identity_realms`, `identity_clients`, `external_issuers` |
| Invocation | `invocations`, `usage_events`, `runtime_logs`, `runtime_metrics` |
| Security | `policy_decisions`, `approvals`, `secret_refs`, `secret_access_events` |
| Reliability | `outbox_events`, `idempotency_keys`, `reconciliation_failures` |

Keep “deployment” as an operation, not as the only object representing source, artifact, release, and live traffic.

---

# Repository-specific change plan

## `go-go-goja`

1. Add a hosted runtime lock containing exact provider versions, module versions, checksums, ABI, and build provenance.
2. Extend `providerapi.Module` with a hosted security/resource descriptor.
3. Rename `PackageCapability` to avoid collision with runtime security capabilities.
4. Add a constrained binding-substitution layer rather than arbitrary runtime-plan mutation.
5. Add owner-level `CallInterruptible` or an invocation wrapper that owns deadline, interrupt, clear, and poison state.
6. Make hosted builders disable all implicit modules.
7. Freeze provider and module registries after build.
8. Replace opaque string-key host services with namespaced typed service keys.
9. Add result-size, query, and logging controls to the database module.
10. Generate exact TypeScript declarations and agent documentation from the resolved module lock.

## `go-go-host`

1. Persist and enforce effective module/permission sets.
2. Stop using `DefaultCapabilities()` in hosted deployment construction.
3. Set production `Dev` false.
4. Replace recursive script loading with the compiled application contract.
5. Move execution into a separate worker binary.
6. Replace `Supervisor` activation with desired-state reconciliation and draining.
7. Add CAS traffic generations and explicit rollback targets.
8. Rewrite bundle scanning as a bounded streaming operation.
9. Store artifacts in content-addressed object storage.
10. Make audit/outbox writes transactional.
11. Add module catalog, entitlements, resources, releases, workers, and invocations.
12. Treat anonymous sessions separately from authenticated users.
13. Remove `ui.dsl` from the default safe profile.
14. Add domain ownership collision checks and certificate lifecycle.
15. Add bounded logs, traces, metrics, and usage records.

## `tiny-idp`

1. Extract `Program`, `LambdaSpec`, schemas, diagnostics, budgets, artifact fingerprints, and generic worker interfaces into neutral packages.
2. Keep identity-specific outcomes, effects, evidence, and continuations in Tiny-IDP.
3. Fix pool shutdown and replacement-capacity defects.
4. Never run untrusted hosted-app code in the IdP process.
5. Add a remote workflow executor interface for tenant-authored identity workflows.
6. Add a horizontally scalable store implementation before claiming shared high availability; the current SQLite store is explicitly single-active-node. fileciteturn86file0L31-L34
7. Keep the production validation contract and release gate.
8. Add managed realm provisioning, issuer/key lifecycle, client lifecycle, export, suspension, and deletion APIs.

## Widget DSL

1. Publish a standalone versioned wire-format package.
2. Extract generic components and intent-oriented namespaces from Vault-specific functionality.
3. Build a Go validator independent of React.
4. Pin renderer and component-registry digests per release.
5. Convert all actions to references to program handlers.
6. Add golden IR, accessibility, Storybook, and real-browser tests.
7. Treat raw HTML as a privileged separate capability.
8. Enforce CSP and URL/action policies in the host, not in user JavaScript.

---

# Recommended implementation order

## Stage 0: make the current prototype honest

1. Fix effective capability persistence and construction.
2. Make database registration conditional.
3. Force production errors off.
4. Add hard Goja interruption and worker poisoning.
5. Fix archive streaming and duplicate-path handling.
6. Disable `ui.dsl.raw`, script/style, and unsafe attributes in the safe profile.
7. Fix activation ordering, host collisions, and graceful draining.
8. Make audit failures visible and transactional.
9. Fix the Tiny-IDP pool shutdown defect.

Do not accept unrelated customers’ programs on the same daemon before these are complete.

## Stage 1: single-node hosted alpha

Build:

- Control plane in Postgres.
- Content-addressed source and artifact store.
- Separate builder process.
- Separate worker process.
- Generic application program contract.
- HTTP handlers, Lambda handlers, server actions, and pages.
- Core, SQLite, and Widget runtime profiles.
- Exact release locks and signed artifacts.
- Platform identity.
- Explicit release promotion and rollback.
- Invocation records and bounded logs.

Even on one physical node, retain the process and data-plane boundaries.

## Stage 2: subscriptions, payments, and app-user identity

Add:

- Module catalog and internal entitlement ledger.
- Stripe webhook ingestion and reconciliation.
- Managed payments capability.
- Resource provisioning and bindings.
- Managed app-user realms and external OIDC.
- Remote identity workflow execution.
- Usage aggregation.
- Entitlement-aware release creation.

## Stage 3: distributed execution

Add:

- Multiple router and worker nodes.
- gVisor sandbox scheduling.
- Worker leases.
- Canary and percentage traffic.
- Egress gateway.
- Central logs and traces.
- Postgres/remote database profiles.
- Dedicated SQLite placement and backup.
- Quota enforcement across nodes.
- Automated reconciliation and dead-worker recovery.

---

# Bottom line

Most of the **concepts** are worth keeping, but the current execution topology is not.

The strongest product foundation is:

- xgoja’s explicit native-module composition and static source planning.
- Tiny-IDP’s serializable program contract, bounded capabilities, typed outcomes, effects, and durable continuations.
- go-go-host’s organizations, agents, deployment records, domains, quotas, and audit model.
- Widget DSL’s serializable UI IR and data-driven actions.

The parts to replace are:

- In-process multi-tenant execution.
- Boolean/default capability enforcement.
- Recursive script startup.
- Response-only timeouts.
- Local in-memory activation as the source of truth.
- The current raw HTML UI DSL.
- Direct secret/network access for payments or identity.
- Per-request billing lookups.
- Conflation of a native module, commercial entitlement, permission, quota, and resource.

The initial product should be deliberately narrow: JavaScript/TypeScript only, operator-curated native modules, no ambient filesystem/process/network access, isolated per-release workers, static assets plus Widget IR, SQLite with explicit singleton semantics, managed payments, and separate platform versus application identity. That scope aligns well with coding agents while preserving a security model that can actually be explained, versioned, audited, rolled back, and enforced.

## Turn 107 - user

- Message ID: `8295ccf9-a464-493c-8f10-40a09b26a633`
- Attachment: SKILL(4).md

write a textbook style document that walks an intern through the systema dn its principles and concepts and implementations and how the decisions were made and all. Also, go-go-goja has an extensive HTTP framework to build secure web applications.

## Turn 108 - assistant

- Message ID: `9d761618-a49d-4f21-b68f-9dbf533a4eec`
- Model: `gpt-5-6-pro`

I’ll produce an intern-facing textbook with diagrams, code-path walkthroughs, design rationale, security boundaries, and roadmap, treating go-go-goja’s HTTP, routing, authentication, host services, and guarded outbound access as first-class subsystems.

## Turn 109 - assistant (tool call)

- Message ID: `53c82136-04bc-4e35-9580-4f376dda47ab`
- Model: `gpt-5-6-pro`

```unknown
bash -lc cat /home/oai/skills/docx/SKILL.md
```

## Turn 110 - assistant

- Message ID: `4a702bec-2a72-4651-873c-1367c3a16f9d`
- Model: `gpt-5-6-pro`

I’ll develop a self-contained intern textbook separating current code, gaps, and proposed architecture, while tracing go-go-goja’s HTTP stack, authentication, routing, sessions, and guarded capabilities.

## Turn 111 - assistant (thinking)

- Message ID: `fe1ac879-bf33-41ef-ad77-82f8f0cd2a5e`

<details><summary>Thinking</summary>

**Read and verified DOCX tasks**


</details>

## Turn 112 - assistant (thinking)

- Message ID: `f75482ef-532c-4ed0-b8d1-fa6f70a48bd8`

<details><summary>Thinking</summary>

**Read docx skill documentation and tasks**


</details>

## Turn 113 - assistant (thinking)

- Message ID: `6d7ab1df-88ec-4fc0-919d-b78491d8ac6d`

<details><summary>Thinking</summary>

**Fetched GitHub files and searched auth documentation**


</details>

## Turn 114 - assistant (thinking)

- Message ID: `f20fc79a-b859-4e9a-ac5a-c5282adae0aa`

<details><summary>Thinking</summary>

**Fetched hostauth details, inspected code, and searched for documentation**


</details>

## Turn 115 - assistant (thinking)

- Message ID: `ec307719-8a4e-4914-9baa-38f0433e3094`
- Model: `gpt-5-6-pro`

<details><summary>Thinking</summary>

**Planning the textbook structure**

The textbook could cover 20 chapters, focusing on designing a Go-ja application platform. The HTTP framework and secure implementation will be central. I’ll reference current code and branches, with GitHub details for accuracy.

**Planned the textbook structure**


</details>

## Turn 116 - assistant (thinking)

- Message ID: `c29902b8-3f33-49e4-9516-b7146ae32387`
- Model: `gpt-5-6-pro`

<details><summary>Thinking</summary>

**Designing document structure**

I’ll build a document with detailed chapters, incorporating the system context, platform, and Go-ja framework. I’ll outline core concepts, including runtime environments, building, security, and hosting, with citations from prior sources.

**Designed document structure**


</details>

## Turn 117 - assistant

- Message ID: `e766f9c0-0346-4343-91b0-caff64c096b3`
- Model: `gpt-5-6-pro`

The HTTP treatment will emphasize its shared JavaScript/Go route-plan contract, staged builders, host-owned CSRF/resource/authorization/audit services, and adapters for custom routing and `net/http`.

## Turn 118 - assistant (thinking)

- Message ID: `8dea2844-4f54-443a-bb00-4ba1311bc150`

<details><summary>Thinking</summary>

**Searched GitHub repository and fetched related documentation**


</details>

## Turn 119 - assistant

- Message ID: `60efe168-9f66-458e-8377-a405908085d2`
- Model: `gpt-5-6-pro`

The teaching spine will follow the exact Go-owned request pipeline, then cover guarded outbound fetch, static assets, native handlers, lifecycle, and the resulting hosted architecture.

## Turn 120 - assistant (tool call)

- Message ID: `ec83c753-61e6-4008-99a1-ce2685a1ec88`
- Model: `gpt-5-6-pro`

```unknown
bash -lc fc-list | grep -i -E 'Liberation Serif|DejaVu Serif|Carlito|Aptos|Noto Serif' | head -20
```

## Turn 121 - assistant (thinking)

- Message ID: `cbf433d5-5d68-477b-a8db-82992400e61f`

<details><summary>Thinking</summary>

**Searched, fetched, and evaluated implementation files and code details**


</details>

## Turn 122 - assistant (thinking)

- Message ID: `024c70b4-7ecc-4b9b-b39c-0ec4c81e42b6`

<details><summary>Thinking</summary>

**Fetched files and searched for documentation from GitHub repository**


</details>

## Turn 123 - assistant (thinking)

- Message ID: `40eef67b-7271-4997-b670-88e47dcc8aeb`
- Model: `gpt-5-6-pro`

<details><summary>Thinking</summary>

**Planning content structure**

I’m thinking the user may want a concise document, aiming for about 20k words spread across roughly 14 chapters, with 4-6 diagrams in ASCII or PNG format. Since they didn’t specifically request images, Python-generated diagrams could be a good fit.

**Planned content structure**


</details>

## Turn 124 - assistant (tool call)

- Message ID: `0a0c156e-fd92-433a-bb70-f40492a38668`
- Model: `gpt-5-6-pro`

```unknown
bash -lc command -v dot || true; command -v pandoc || true; python - <<'PY'
import docx
print('python-docx ok')
PY
```

## Turn 125 - assistant (thinking)

- Message ID: `c8663fb5-6406-4757-8593-aa1fb23612f4`

<details><summary>Thinking</summary>

**Checked dependencies for diagram generation and DOCX creation**


</details>

## Turn 126 - assistant (thinking)

- Message ID: `5b5ac715-ec3a-4679-bd28-7ffa0606b9df`
- Model: `gpt-5-6-pro`

<details><summary>Thinking</summary>

**Planning document setup**

I’m considering using a local clone for thorough code analysis. We can use existing sources and inspect up-to-date README files, but I’ll mention certain aspects are still in progress, such as the Tiny-ID P scripting branch.

**Planned document setup**


</details>

## Turn 127 - assistant (thinking)

- Message ID: `181ffc38-179e-465c-a301-7f9240280974`
- Model: `gpt-5-6-pro`

<details><summary>Thinking</summary>

**Planning document structure**

I’m considering adding decision-making sections like "Problem", "Alternatives", and "Consequences". For exercises, we could guide an intern through tasks, using snippets and examples. I’ll focus on Markdown and DOC X, avoiding PDF for now since the user didn’t ask for it.

**Planned document structure**


</details>

## Turn 128 - assistant (thinking)

- Message ID: `c22aee7e-ecbe-4e17-a69f-fb0397c0d759`
- Model: `gpt-5-6-pro`

<details><summary>Thinking</summary>

**Planning content structure and diagrams**

I’m considering five diagrams for key system concepts, and I’ll use Mermaid in Markdown for simplicity, but include Graphviz-generated images in the DOC X. The document will focus on guiding interns through the secure JavaScript hosting platform.

**Planned content structure and diagrams**


</details>

## Turn 129 - assistant (tool call)

- Message ID: `6981493e-8d42-4b87-b5b4-67566cb9677f`
- Model: `gpt-5-6-pro`

```unknown
bash -lc set -e
WORK=/mnt/data/textbook_work
rm -rf "$WORK"
mkdir -p "$WORK/diagrams" "$WORK/render"
cat > "$WORK/diagrams/system_overview.dot" <<'DOT'
digraph G {
  graph [rankdir=TB, bgcolor="white", pad="0.25", nodesep="0.45", ranksep="0.6", fontname="DejaVu Sans"];
  node [shape=box, style="rounded,filled", fillcolor="#f7f9fc", color="#4b5d73", fontname="DejaVu Sans", fontsize=11, margin="0.12,0.08"];
  edge [color="#4b5d73", arrowsize=0.8, fontname="DejaVu Sans", fontsize=9];

  subgraph cluster_control {
    label="Trusted control plane"; color="#8fa3b8"; style="rounded";
    users [label="Dashboard, CLI, coding agents"];
    api [label="API, authentication, RBAC"];
    state [label="Projects, releases, policies,\nmodules, entitlements, audit"];
    db [label="PostgreSQL + transactional outbox"];
    users -> api -> state -> db;
  }

  subgraph cluster_build {
    label="Trusted build plane"; color="#8fa3b8"; style="rounded";
    source [label="Source bundle or Git revision"];
    scan [label="Bounded archive scan + source graph"];
    compile [label="Program compiler + policy resolver"];
    xgoja [label="xgoja runtime profile build"];
    artifact [label="Signed content-addressed artifact\nSBOM + provenance + runtime lock"];
    source -> scan -> compile -> xgoja -> artifact;
  }

  subgraph cluster_exec {
    label="Execution plane"; color="#8fa3b8"; style="rounded";
    router [label="Edge/router"];
    worker [label="Per-tenant release sandbox\nGoja worker pool + gojahttp host"];
    broker [label="Capability and resource brokers"];
    resources [label="Database, object store, identity,\npayments, queues, guarded egress"];
    router -> worker -> broker -> resources;
  }

  db -> compile [label="desired release"];
  artifact -> worker [label="verified artifact"];
  db -> router [label="traffic generation"];
  worker -> db [label="status, usage, audit", style=dashed];
}
DOT

cat > "$WORK/diagrams/runtime_ownership.dot" <<'DOT'
digraph G {
  graph [rankdir=LR, bgcolor="white", pad="0.25", nodesep="0.45", ranksep="0.6", fontname="DejaVu Sans"];
  node [shape=box, style="rounded,filled", fillcolor="#f7f9fc", color="#4b5d73", fontname="DejaVu Sans", fontsize=10.5];
  edge [color="#4b5d73", arrowsize=0.8, fontname="DejaVu Sans", fontsize=9];
  plan [label="RuntimeFactory\nimmutable module plan"];
  runtime [label="engine.Runtime"];
  vm [label="goja.Runtime\n(single-owner VM)"];
  loop [label="event loop"];
  owner [label="runtimeowner\nCall / Post / WaitIdle"];
  require [label="require registry"];
  bridge [label="runtimebridge\nlifecycle + current call context"];
  modules [label="native modules\nloaders + closers + values"];
  caller [label="HTTP request, command,\nworker invocation"];
  async [label="bounded Go work"];

  plan -> runtime;
  runtime -> vm;
  runtime -> loop;
  runtime -> owner;
  runtime -> require;
  runtime -> bridge;
  require -> modules;
  caller -> owner [label="Call(ctx)"];
  owner -> vm [label="serialized"];
  modules -> async [label="start off-VM"];
  async -> owner [label="Post settlement"];
  bridge -> modules [label="current context"];
}
DOT

cat > "$WORK/diagrams/http_pipeline.dot" <<'DOT'
digraph G {
  graph [rankdir=TB, bgcolor="white", pad="0.25", nodesep="0.35", ranksep="0.45", fontname="DejaVu Sans"];
  node [shape=box, style="rounded,filled", fillcolor="#f7f9fc", color="#4b5d73", fontname="DejaVu Sans", fontsize=10];
  edge [color="#4b5d73", arrowsize=0.75, fontname="DejaVu Sans", fontsize=8.5];
  req [label="HTTP request"];
  ident [label="Trusted proxy identity normalization"];
  match [label="Mount or route match\nReject raw routes when configured"];
  dto [label="Session + bounded body parsing\nRequestDTO"];
  pre [label="Pre-auth rate limits"];
  auth [label="Authenticate credential\nSession / API token / access token"];
  csrf [label="CSRF verification\nwhen required and applicable"];
  resource [label="Resolve declared resources"];
  grants [label="Check token grants"];
  authorize [label="Host authorizer decision"];
  post [label="Post-auth rate limits"];
  ctx [label="SecureContext projected to JavaScript"];
  handler [label="Planned JS or Go handler"];
  response [label="Response helpers / renderer"];
  audit [label="Allowed, denied, failed, completed audit"];

  req -> ident -> match -> dto -> pre -> auth -> csrf -> resource -> grants -> authorize -> post -> ctx -> handler -> response;
  pre -> audit [style=dashed]; auth -> audit [style=dashed]; authorize -> audit [style=dashed]; handler -> audit [style=dashed];
}
DOT

cat > "$WORK/diagrams/release_lifecycle.dot" <<'DOT'
digraph G {
  graph [rankdir=LR, bgcolor="white", pad="0.25", nodesep="0.45", ranksep="0.6", fontname="DejaVu Sans"];
  node [shape=box, style="rounded,filled", fillcolor="#f7f9fc", color="#4b5d73", fontname="DejaVu Sans", fontsize=10];
  edge [color="#4b5d73", arrowsize=0.8, fontname="DejaVu Sans", fontsize=8.5];
  source [label="Source revision"];
  build [label="Build attempt"];
  artifact [label="Immutable artifact"];
  release [label="Release\nartifact + config + bindings + policy"];
  candidate [label="Candidate workers"];
  smoke [label="Smoke / synthetic / canary checks"];
  cas [label="CAS traffic generation\n+ audit + outbox"];
  live [label="Live generation"];
  drain [label="Drain retired generation"];
  rollback [label="Rollback creates a new\ntraffic generation"];

  source -> build -> artifact -> release -> candidate -> smoke -> cas -> live -> drain;
  live -> rollback [style=dashed];
  rollback -> cas [label="explicit target release"];
}
DOT

cat > "$WORK/diagrams/identity_flow.dot" <<'DOT'
digraph G {
  graph [rankdir=TB, bgcolor="white", pad="0.25", nodesep="0.4", ranksep="0.5", fontname="DejaVu Sans"];
  node [shape=box, style="rounded,filled", fillcolor="#f7f9fc", color="#4b5d73", fontname="DejaVu Sans", fontsize=10];
  edge [color="#4b5d73", arrowsize=0.8, fontname="DejaVu Sans", fontsize=8.5];
  browser [label="Browser user"];
  oidc [label="Tiny-IDP or external OIDC\nAuthorization Code + PKCE"];
  native [label="Go-owned login/callback/logout handlers"];
  session [label="Server-side application session\nopaque secure cookie"];
  route [label="gojahttp planned route"];
  js [label="JavaScript handler sees\nActor + AuthResult + ResourceRef"];
  agent [label="Coding agent / service"];
  token [label="Programauth API/access token\nhashed durable credential"];
  fetch [label="Guarded fetch client"];

  browser -> oidc -> native -> session -> route -> js;
  agent -> token -> route;
  agent -> fetch -> route;
}
DOT

cat > "$WORK/diagrams/widget_pipeline.dot" <<'DOT'
digraph G {
  graph [rankdir=LR, bgcolor="white", pad="0.25", nodesep="0.45", ranksep="0.6", fontname="DejaVu Sans"];
  node [shape=box, style="rounded,filled", fillcolor="#f7f9fc", color="#4b5d73", fontname="DejaVu Sans", fontsize=10];
  edge [color="#4b5d73", arrowsize=0.8, fontname="DejaVu Sans", fontsize=8.5];
  author [label="JavaScript / Go intent DSL"];
  normalize [label="Normalize + validate"];
  ir [label="Versioned Widget IR\ncomponents, slots, actions, data"];
  preset [label="Recipes + design-system policy"];
  renderer [label="Pinned React renderer registry"];
  browser [label="Browser UI"];
  action [label="Serialized action"];
  planned [label="Planned server action route"];

  author -> normalize -> ir -> preset -> renderer -> browser;
  browser -> action -> planned;
}
DOT

cat > "$WORK/diagrams/module_resolution.dot" <<'DOT'
digraph G {
  graph [rankdir=TB, bgcolor="white", pad="0.25", nodesep="0.4", ranksep="0.5", fontname="DejaVu Sans"];
  node [shape=box, style="rounded,filled", fillcolor="#f7f9fc", color="#4b5d73", fontname="DejaVu Sans", fontsize=10];
  edge [color="#4b5d73", arrowsize=0.8, fontname="DejaVu Sans", fontsize=8.5];
  requested [label="Application requests modules"];
  catalog [label="Operator module catalog\nversions, ABI, risk, permissions"];
  entitlement [label="Account entitlements + quotas"];
  policy [label="Environment policy"];
  binding [label="Resource and secret bindings"];
  resolver [label="Deterministic resolver"];
  lock [label="Exact runtime lock"];
  build [label="xgoja profile build or cache lookup"];
  release [label="Signed release"];

  requested -> resolver;
  catalog -> resolver;
  entitlement -> resolver;
  policy -> resolver;
  binding -> resolver;
  resolver -> lock -> build -> release;
}
DOT

for f in "$WORK"/diagrams/*.dot; do
  base=${f%.dot}
  dot -Tpng -Gdpi=180 "$f" -o "$base.png"
done
ls -lh "$WORK/diagrams"/*.png

```

## Turn 130 - assistant (thinking)

- Message ID: `05ed6351-3ded-4e03-9df7-90442fcbe4e0`

<details><summary>Thinking</summary>

**Generated diagrams and files in specified directories**


</details>

## Turn 131 - assistant (thinking)

- Message ID: `80d43857-dc84-4cb3-8ce7-87d39d419859`
- Model: `gpt-5-6-pro`

<details><summary>Thinking</summary>

**Creating textbook-style document**

I’ll produce an intern-focused textbook, blending practical examples, diagrams, and foundational explanations. The plan includes detailing the go-go-goja HTTP architecture and secure web application framework with a focus on decision-making processes, modularity, and capabilities.

**Created a textbook-style document**


</details>

## Turn 132 - assistant (tool call)

- Message ID: `c98c99c6-f109-401e-b2b6-4d50245483d9`
- Model: `gpt-5-6-pro`

```unknown
bash -lc sed -n '1,240p' /home/oai/skills/docx/SKILL.md && printf '\n---CREATE_EDIT---\n' && sed -n '1,220p' /home/oai/skills/docx/tasks/create_edit.md && printf '\n---VERIFY---\n' && sed -n '1,220p' /home/oai/skills/docx/tasks/verify_render.md
```

## Turn 133 - assistant

- Message ID: `19381edf-49ad-41ab-aad0-454d40f1941a`
- Model: `gpt-5-6-pro`

I’ll clearly separate existing repository behavior, reusable implemented principles, and proposed multi-tenant architecture. Next, I’ll generalize Tiny-IDP’s bounded lambdas and connect them to Widget IR and static frontends.

## Turn 134 - assistant

- Message ID: `2945eaf2-a217-44bd-8f23-2a2a976da5e9`
- Model: `gpt-5-6-pro`

The foundation section now covers repository roles, runtime ownership, xgoja composition, and authority terminology. A running multi-tenant example will connect later chapters and expose each decision’s alternatives and invariants.

## Turn 135 - assistant (thinking)

- Message ID: `11ce8a88-4c52-4b01-b4a7-941b8e445544`

<details><summary>Thinking</summary>

**Checked available fonts for docx styling**


</details>

## Turn 136 - assistant (tool call)

- Message ID: `c56bfabc-5c72-4031-ad19-8c32a5a1992a`
- Model: `gpt-5-6-pro`

```unknown
bash -lc cat > /mnt/data/hosted_goja_platform_textbook.md <<'EOF'
# Building a Hosted Goja Application Platform

## A textbook guide to go-go-goja, xgoja, go-go-host, Tiny-IDP, secure HTTP applications, module subscriptions, and agent-driven releases

**Architecture and implementation guide**  
**Research snapshot:** July 20, 2026

---

## Preface

This book explains a specific engineering problem: how to turn the Goja-based tools in the Go Go Golems ecosystem into a hosted platform where customers upload JavaScript or TypeScript programs, select native Go-backed modules, publish secure web applications and functions, manage their own users, and release changes through coding agents without losing auditability or rollback safety.

The repositories already contain many of the required pieces. `go-go-goja` provides an owned JavaScript runtime, an event loop, explicit native-module composition, TypeScript declaration generation, an extensive HTTP framework, planned authorization, server-side sessions, programmatic agent authentication, guarded outbound HTTP, and generated xgoja hosts. `go-go-host` provides an early control plane for organizations, sites, deployments, agents, domains, quotas, capabilities, audit, and runtime activation. The `task/prod-tiny-idp` branch of Tiny-IDP develops a particularly strong model for constrained JavaScript programs: serializable contracts, named lambdas, schemas, outcomes, capabilities, effects, budgets, fingerprints, worker pools, and durable browser continuations. The Widget DSL research demonstrates how server-side JavaScript can produce a versioned user-interface intermediate representation that a generic browser renderer can display. [S1][S4][S10][S17][S21]

The book has two obligations. First, it must describe the current implementations accurately. Second, it must explain the target architecture without pretending that recommendations already exist in production code. Sections therefore use three labels:

- **Current implementation** describes code or documented behavior found in the reviewed repositories.
- **Design principle** explains the reasoning that should survive refactoring.
- **Target platform** describes the recommended hosted system.

The central correction to the earlier architectural review is that the HTTP subsystem is not a small route bridge. `go-go-goja` already contains a substantial web application framework. JavaScript uses an Express-style declaration API, but Go owns the listener, router, request parsing, session state, authentication, CSRF checks, resource resolution, authorization, rate limits, audit, static mounts, generic handler mounts, asynchronous handler completion, OIDC lifecycle routes, and graceful shutdown. The hosted platform should build on that framework rather than replacing it with a second, narrower HTTP stack. [S4][S5][S6][S7][S8][S9]

### How to read this book

Parts I and II establish the runtime and HTTP foundations. Part III turns those foundations into a control plane, build plane, and execution plane. Part IV generalizes the Tiny-IDP and Widget DSL work into an agent-friendly application model. Part V evaluates the current code, assigns repository responsibilities, and provides an implementation sequence.

A new intern should read the chapters in order. An experienced engineer may begin with Chapter 4 for the HTTP framework, Chapter 10 for releases, or Chapter 17 for the gap analysis.

### Source notation

References such as `[S7]` point to the source map in Appendix C. Sources are repository files, design documents, and the two PARC project notes requested for this review. The codebase is active; line numbers and package details may change after the stated research snapshot.

---

# Part I — Foundations

# 1. The System We Are Building

The proposed product is a managed application platform for JavaScript programs executed by Goja. A customer uploads source code, chooses a set of native modules, connects resources such as a database or identity realm, and promotes an immutable release. The platform runs that release as an HTTP application, a request-driven function, a scheduled job, or an automation agent. The customer pays for modules and resources rather than operating the Go runtime or compiling a custom binary by hand.

That description contains several different kinds of software. Separating them early prevents most architectural confusion.

| Kind of code | Author | Trust level | Examples |
| --- | --- | --- | --- |
| Tenant application code | Customer or coding agent | Untrusted or partially trusted | Route handlers, workflows, page composition, business rules |
| Native runtime module | Platform or reviewed provider author | Trusted | SQLite API, planned HTTP framework, payments adapter, auth client, Widget DSL |
| Browser asset | Customer build pipeline | Untrusted content served under policy | React bundle, CSS, images, static HTML |
| Control-plane service | Platform | Highly trusted | Release API, entitlements, policy, audit, domains, worker scheduler |
| Identity kernel | Platform or dedicated customer service | Highly trusted | OIDC validation, credentials, sessions, signing keys, continuation state |

The platform must not treat these categories as interchangeable. JavaScript is allowed to express application behavior. It is not allowed to choose its own operating-system privileges, inject arbitrary Go packages, read the platform process environment, obtain raw database handles, or define how tokens are verified. Native modules expose selected authority through typed APIs. The control plane decides whether the customer is entitled to use that authority. The worker enforces the decision.

## 1.1 Four planes

A useful first decomposition has four planes.

```text
Authoring and build plane
    source -> static analysis -> runtime profile -> artifact

Control plane
    organizations -> projects -> releases -> policy -> traffic

Execution plane
    routers -> isolated workers -> capability brokers -> resources

Identity plane
    platform users -> application users -> sessions -> tokens -> keys
```

The planes communicate through immutable records and narrow protocols. They should not share a large mutable process merely because all services are written in Go.

## 1.2 The product promise

A credible product promise is stronger than “we execute JavaScript.” It is:

- A release names the exact source, native modules, policies, bindings, renderer, and runtime ABI that executed.
- The platform can explain why a request was allowed or denied before JavaScript ran.
- A coding agent can propose a release, but cannot silently enlarge its own authority.
- A failed release does not replace a healthy release.
- A rollback selects an exact earlier release and records the new traffic decision.
- Subscription changes affect release eligibility through an internal entitlement model, not through a billing API call on every request.
- Customer code is isolated from the control plane and from other customers.

These promises determine the architecture. They require immutable releases, explicit capabilities, host-owned HTTP security, reproducible builds, transactional state transitions, and an execution boundary stronger than a Go interface.

## 1.3 Why Goja is appropriate

Goja is useful when JavaScript drives an engine written in Go and frequently crosses the Go/JavaScript boundary. It is pure Go and gives the host precise control over available modules and concurrency. A `goja.Runtime` is not goroutine-safe; only one goroutine may use a runtime at a time. The host must therefore own scheduling rather than allowing arbitrary request goroutines to call the VM. [S2][S3]

Goja is not a complete Node.js runtime and should not become one accidentally. The platform chooses which Node-like facilities exist. That constraint is an advantage for a managed product: it makes the runtime surface reviewable.

## 1.4 The first design decision

**Decision:** JavaScript expresses behavior; Go owns authority.

If JavaScript owned listeners, cookies, token verification, filesystem access, network sockets, or database credentials directly, each application would construct a different security boundary. The platform could no longer reason about releases uniformly. By keeping authority in Go-backed services, the platform can validate a static plan, enforce it before callbacks, meter it, audit it, and revoke it.

### Key points

- The product is a managed authority system, not only a script runner.
- Tenant code, native modules, browser assets, control-plane code, and identity code have different trust levels.
- The target architecture has separate build, control, execution, and identity planes.
- JavaScript should receive narrow capabilities rather than ambient process authority.

---

# 2. Runtime Ownership, Scheduling, and Lifecycle

A Goja runtime is a mutable interpreter state. It contains global variables, loaded modules, JavaScript objects, pending promises, and references to Go values. The most important runtime rule is therefore ownership: at any moment, one serialized execution path owns the VM.

## 2.1 The owned runtime

`go-go-goja` wraps the raw VM in an `engine.Runtime`. The runtime contains the VM, the CommonJS `require` implementation, a Node-style event loop, a runtime owner, runtime-scoped values, a lifetime context, and registered cleanup functions. The factory constructs these pieces in a deliberate order. [S2]

```text
RuntimeFactory
    -> new goja.Runtime
    -> new event loop
    -> new RuntimeOwner
    -> lifetime context
    -> runtime bridge bindings
    -> require registry
    -> native module registration
    -> enable require and standard globals
    -> runtime initializers
    -> owned Runtime
```

This order solves concrete problems. Native modules need the event loop and owner before they can create asynchronous APIs. Modules must register loaders before `require` is enabled. Runtime initializers may import modules, so they run afterward. Cleanup hooks are registered during construction and run in reverse order during shutdown.

## 2.2 RuntimeFactory versus Runtime

The factory is an immutable composition plan. A runtime is one mutable execution instance created from that plan.

| Object | Lifetime | Mutable state | Responsibility |
| --- | --- | --- | --- |
| `RuntimeFactoryBuilder` | Build/configuration | Yes, until `Build` | Collect modules, middleware, initializers, and require options |
| `RuntimeFactory` | Process or release generation | No | Create equivalent runtime instances |
| `Runtime` | Worker or invocation pool slot | Yes | Own one VM, event loop, values, and resources |

This separation is essential for pooling. A platform can validate and freeze one release profile, then create several equivalent workers without rebuilding policy on every request.

## 2.3 RuntimeOwner

`runtimeowner.RuntimeOwner` exposes `Call`, `Post`, `WaitIdle`, `Shutdown`, and `IsClosed`. `Call` schedules work on the owner context and waits for a result. `Post` schedules work without a return value. Both associate the caller's context with the VM operation through the runtime bridge. [S3]

```go
result, err := runtime.Owner.Call(ctx, "load-program", func(ctx context.Context, vm *goja.Runtime) (any, error) {
    return vm.RunProgram(compiled)
})
```

The owner also handles reentrant calls. If native module code is already running on the owner path and calls another owner operation using the marked context, the owner executes it directly rather than deadlocking by scheduling onto itself.

## 2.4 Contexts are not execution limits by themselves

A context can stop waiting without stopping JavaScript. If a caller's deadline expires while JavaScript is in an infinite loop, `Call` may return cancellation while the scheduled callback continues to occupy the VM. The HTTP response can time out while the worker remains blocked.

The Tiny-IDP scripting branch demonstrates a stronger pattern. An invocation creates a deadline, installs a callback that invokes `VM.Interrupt`, marks the worker unsafe, clears the interrupt during bounded cleanup, and discards the worker instead of returning it to the pool. [S19][S20]

The hosted runtime should formalize this sequence:

```text
invocation deadline
    -> cancel native capabilities
    -> interrupt VM
    -> mark worker poisoned
    -> attempt bounded cleanup
    -> discard VM
    -> kill worker process if it does not stop
```

The process boundary is the final enforcement mechanism. Goja interruption protects the pool. Operating-system limits protect the node.

## 2.5 Promise settlement

Asynchronous native modules must not resolve a promise from a background goroutine by touching the VM directly. The correct pattern is:

1. Create the promise on the owner path.
2. Run blocking work outside the VM.
3. Post settlement back to the owner.
4. Resolve or reject while the VM is owned.

The HTTP host and Tiny-IDP worker both account for promises. The HTTP host accepts a promise returned by a route handler and polls its state through owner calls until it is fulfilled or rejected. Tiny-IDP capability bindings perform native work asynchronously and post the result back through the owner. [S5][S20]

## 2.6 Runtime lifecycle

A runtime must close all resources it created: database connections, HTTP clients, file watchers, timers, plugin processes, and background goroutines. Native modules receive an `AddCloser` hook during registration. The runtime cancels its lifetime context, waits briefly for owner activity, interrupts if required, executes closers, removes bridge state, shuts down the owner, and stops the event loop. [S2]

**Decision:** Every native module must be runtime-scoped unless its state is demonstrably immutable and process-safe.

A global module registry may describe available module types, but mutable connections and services belong to a runtime or a release worker. This prevents one tenant's state from leaking into another tenant's VM.

### Key points

- A raw `goja.Runtime` is not the platform execution unit; the owned runtime is.
- Factories freeze policy, while runtimes hold mutable execution state.
- All VM calls and promise settlements must pass through the owner.
- Context cancellation must be paired with VM interruption and worker disposal.
- Native resources must register cleanup with the runtime lifecycle.

---

# 3. xgoja as the Build and Composition System

`xgoja` is the bridge between application intent and a concrete Go binary. It selects provider packages, native runtime modules, JavaScript or TypeScript sources, command surfaces, generated artifacts, and workspace behavior. The v2 schema makes these concepts explicit and produces an embedded runtime plan. [S1]

## 3.1 Providers and runtime modules

A provider is a trusted Go package that contributes one or more capabilities to xgoja. A provider may register runtime modules, command sets, source sets, TypeScript declarations, help text, assets, host services, and runtime initializers. A runtime module is one selected JavaScript-visible API supplied by a provider. [S1]

```yaml
providers:
  - id: http
    import: github.com/go-go-golems/go-go-goja/pkg/xgoja/providers/http

runtime:
  modules:
    - provider: http
      name: express
      as: express
```

The alias is part of the source contract. A TypeScript or JavaScript file may import `express`, and the planner preserves that bare import so the Goja runtime resolves it through the native registry.

The distinction between provider and module matters for subscriptions. A provider is a build-time package. A module is a selected API. An entitlement is the customer's commercial right to select it. A permission is the authority the module may exercise. A binding is the concrete resource attached to it. These concepts must remain separate.

## 3.2 Sources and the closed graph

Executable source sets have a declared origin, language, include/exclude patterns, and compile intent. xgoja parses static imports and validates local helpers and bare module names. Nonliteral dynamic imports are rejected because a generated application requires a closed source graph. [S1]

```text
source set
    -> parse imports
    -> resolve local files
    -> verify native module aliases
    -> bundle TypeScript if requested
    -> emit executable source artifact
```

A closed graph provides several benefits:

- The release can name every source file and native dependency.
- Missing imports fail during planning rather than on a production request.
- Agents can generate TypeScript against exact declarations.
- The platform can calculate a stable source digest.
- Runtime module entitlements can be checked before building.

## 3.3 Commands are explicit surfaces

Runtime modules and command sets are different provider outputs. The Express module lets JavaScript register routes. The HTTP provider's `serve` command owns the listener and keeps the runtime alive. A command chooses which source sets it can execute. [S1][S12]

This design should be preserved in the hosted platform, even if the public product hides the generated CLI. A release still needs an explicit execution surface:

- HTTP application.
- Request-driven function.
- Scheduled job.
- Queue consumer.
- One-shot migration.
- Agent command.

The platform should not infer every possible surface from arbitrary top-level JavaScript effects.

## 3.4 Generated runtime packages

xgoja can generate a runtime package containing an embedded plan, provider registration code, embedded source files, TypeScript declarations, and APIs for creating runtimes. The embedding host may configure host services or apply controlled runtime configuration before constructing the bundle. [S1]

For local tools, this flexibility is useful. For hosted releases, it must be narrowed. A customer must not be able to alter provider imports, use local `go.work` replacements, or inject arbitrary Go dependencies. The platform should generate the xgoja specification from an operator-controlled module catalog.

## 3.5 Reproducible runtime profiles

The current runtime plan intentionally omits build-only information such as provider import paths, module versions, and replacements. That is suitable for a generated binary that already contains its code, but it is insufficient as the sole hosted release identity. [S1]

The target release lock should record:

```json
{
  "runtimeAbi": "gogo-host/v1",
  "toolchain": "go1.x.y",
  "gojaVersion": "...",
  "goGoGojaVersion": "...",
  "sourceDigest": "sha256:...",
  "programDigest": "sha256:...",
  "profileDigest": "sha256:...",
  "modules": [
    {
      "id": "sqlite",
      "version": "1.3.2",
      "providerModule": "github.com/example/provider",
      "providerSum": "h1:...",
      "alias": "db",
      "configDigest": "sha256:..."
    }
  ]
}
```

**Decision:** Hosted builds use exact module versions from a curated catalog and disable workspace discovery and arbitrary replacements.

The alternative—building from the customer's xgoja provider list—would let uploaded source expand the trusted computing base. That is not a safe subscription model.

### Key points

- xgoja is already a build planner and module linker, not merely a CLI wrapper.
- Providers are trusted Go packages; runtime modules are selected JavaScript APIs.
- Closed import graphs enable reproducible releases and early failures.
- Command surfaces should remain explicit even when the hosted product hides the CLI.
- A hosted release needs a complete runtime lock in addition to the embedded runtime plan.

---

# Part II — The Secure HTTP Application Framework

# 4. Go Owns the Server; JavaScript Declares the Application

The HTTP architecture begins with a strict separation. JavaScript declares routes and handlers. Go owns the network listener, top-level mux, request lifecycle, route registry, security services, and VM scheduling. The API is Express-style because the fluent route syntax is familiar, but it is not an attempt to reproduce the full npm Express ecosystem. [S4]

## 4.1 The main components

| Component | Responsibility |
| --- | --- |
| `gojahttp.Host` | Route matching, mounts, request DTOs, sessions, planned enforcement, dispatch, response handling |
| `modules/express` | JavaScript route and mount declaration API |
| HTTP provider `serve` command | Listener, `http.Server`, top-level mux, native handlers, runtime construction, signal handling, graceful shutdown |
| `Enforcer` | Router-independent authentication, CSRF, resource resolution, authorization, rate limits, and audit |
| `hostauth` | Optional session, OIDC, app authorization, capability, and programmatic-auth services |
| `RuntimeOwner` | Serialized callbacks into the Goja VM |

A request path in a generated application looks like this:

```text
client
  -> http.Server
  -> top-level ServeMux
       -> native Go auth/readiness routes, when configured
       -> hot-reload helper routes, when configured
       -> gojahttp.Host
            -> static or generic mounted handler
            -> planned Go route
            -> planned JavaScript route
            -> raw JavaScript route, only when allowed
```

The `serve` command mounts native auth handlers before the JavaScript fallback, then constructs a runtime with per-runtime host services, executes the selected route-registration source, starts the listener, and performs graceful shutdown on cancellation or signals. JavaScript does not call `app.listen()`. [S12]

## 4.2 Express is a declaration layer

A normal public route is explicit:

```javascript
const express = require("express");
const app = express.app();

app.get("/healthz")
  .public()
  .handle((_ctx, res) => res.json({ ok: true }));
```

An authenticated mutation declares its security intent before supplying a handler:

```javascript
app.patch("/orgs/:orgId/projects/:projectId")
  .auth(express.sessionUser())
  .resource(
    express.resource("project")
      .idFromParam("projectId")
      .tenantFromParam("orgId")
      .mustExist()
  )
  .csrf()
  .rateLimit(
    express.rateLimit("project-update")
      .perMinute(30)
      .byActor()
      .byResource("project")
  )
  .allow("project.update")
  .audit("project.update")
  .handle((ctx, res) => {
    res.json({ id: ctx.resource("project").id, updated: true });
  });
```

The route file does not load a session row, parse a bearer token, query a membership table, or decide whether the actor may update the project. It names the requirements. Go enforces them.

## 4.3 Why the server is not started from JavaScript

Allowing scripts to create listeners would create several problems:

- Multiple scripts could bind conflicting addresses.
- The platform could not mount native OIDC or readiness handlers consistently.
- Signal handling and graceful shutdown would vary by application.
- Hot reload would have to replace listeners rather than route snapshots.
- The platform could not guarantee one routing and observability boundary.

The HTTP provider therefore owns `net.Listen`, `http.Server.Serve`, and shutdown. Express is route registration only. [S12]

## 4.4 Static mounts and generic Go handlers

The host supports three forms of non-route dispatch:

1. Static filesystem directories.
2. Static content from an embedded asset module.
3. Generic Go `http.Handler` mounts exposed by trusted native modules.

```javascript
app.staticFromAssetsModule("/static", require("fs:assets"), "/app/public");
app.mount("/ws", sessionstream.webSocket.server(hub));
```

Generic mounts preserve the original path by default. Static helpers strip the prefix. Exclusion prefixes allow a broad mount to leave selected paths for later routes. This makes the host usable for WebSockets and other Go-owned transports without constructing a second JavaScript routing system. [S4][S5]

## 4.5 Raw routes

The host still supports low-level raw JavaScript handlers for compatibility. `RejectRawRoutes: true` makes matched raw routes fail rather than bypass planned policy. Planned routes and approved mounts continue to work. [S5][S9]

**Decision:** Production generated hosts should reject raw routes by default.

The important property is reviewability. Every ordinary route should visibly declare public or authenticated access. An accidental `app.get(path, handler)` overload must not create an unplanned security path.

## 4.6 Request and response objects

`gojahttp` parses the method, URL, path, query values, path params, headers, cookies, session, client IP, body, and raw body into a request DTO. JSON, URL-encoded, and multipart forms are parsed automatically; other bodies remain strings. The current parser caps request bodies at 64 MiB and multipart in-memory use at 32 MiB. [S5]

The response API provides status, headers, JSON, send, HTML rendering, redirects, and end. It ensures that a response is only sent once. A handler may return a promise; the host waits for fulfillment through owner-scheduled checks. [S4][S5]

The hosting platform should make body and response limits configurable per route profile and usually much smaller than the generic framework maximum.

### Key points

- The Go HTTP host is the server; Express is the application declaration language.
- The `serve` command owns listener lifecycle, native handlers, runtime startup, and shutdown.
- Planned routes, planned Go handlers, static mounts, generic mounts, and compatibility raw routes share one host.
- Production should reject raw routes.
- Request parsing and promise completion are already integrated with runtime ownership.

---

# 5. Planned Routes: Security Intent as Data

A planned route is a `RoutePlan` produced when the application registers a route. The plan is validated before traffic is accepted. It contains the method, pattern, security mode, acceptable credential requirements, resources, action, CSRF requirement, audit event, and rate-limit policies. [S6]

## 5.1 The route plan

```go
type RoutePlan struct {
    Name       string
    Method     string
    Pattern    string
    Security   SecuritySpec
    Resources  []ResourceSpec
    Action     string
    CSRF       CSRFSpec
    Audit      AuditSpec
    RateLimits []RateLimitSpec
}
```

This is the central HTTP design. Security is no longer hidden in middleware order or handler branches. It is a value that can be validated, listed, documented, diffed, tested, and audited.

## 5.2 Staged builders

The Go API uses distinct builder stages:

```text
RouteNeedsSecurity
    -> Public()
        -> RouteNeedsHandler

RouteNeedsSecurity
    -> Auth(spec)
        -> RouteNeedsPolicy
            -> Resource / CSRF / Audit / RateLimit
            -> Allow(action)
                -> RouteNeedsHandler
```

The JavaScript API uses Go-backed builder objects with the same conceptual stages. A handler cannot be registered until the route has called `.public()` or completed `.auth(...).allow(...)`. [S4][S8]

This is stronger than documentation. It makes omitted security declarations a registration error.

## 5.3 Registration-time validation

`ValidateRoutePlan` normalizes and checks the plan. Important invariants include: [S6]

- The method and pattern are required.
- A route must choose public or authenticated security.
- Public routes cannot declare authenticated principal requirements.
- Authenticated routes require an action.
- OAuth routes require audit.
- Resource value sources must reference real path params.
- Authentication requirements are normalized and deduplicated.
- Rate-limit specs are normalized before registration.

A typo such as `idFromParam("id")` on `/projects/:projectId` fails at startup rather than producing an authorization gap on a live request.

## 5.4 Security requirements

The framework distinguishes credential method from principal kind.

| Dimension | Examples |
| --- | --- |
| Authentication method | Session, API token, access token |
| Principal kind | User, agent, service |

A browser route can require `sessionUser()`. An automation endpoint can require `agent()`. A deliberately shared endpoint can use `anyOf(sessionUser(), agent())`. [S15]

This prevents a common mistake: an API token with a matching action should not automatically enter a browser-only route. The principal requirement is checked before the handler.

## 5.5 Resources and authorization

A resource declaration describes where the resource identity comes from. It does not load the resource itself.

```javascript
express.resource("project")
  .idFromParam("projectId")
  .tenantFromParam("orgId")
  .mustExist()
```

The host calls a `ResourceResolver`, receives a minimal `ResourceRef`, then passes the actor, action, primary resource, and all resolved resources to the `Authorizer`. The handler receives the resolved references only after authorization succeeds. [S6][S7]

This division keeps domain policy in Go while keeping route intent near the application behavior.

## 5.6 CSRF

A route may call `.csrf()`. On unsafe methods, the enforcer invokes the host `CSRFProtector` when the authentication result requires CSRF. Browser session authentication normally requires it. API-token authentication does not rely on ambient cookies, but a route can reject API tokens through `sessionUser()` before this distinction matters. [S7][S15]

CSRF is therefore not a JavaScript convention. It is a host service enforced before the callback.

## 5.7 Rate limits

Rate limits are route policy. The builder can construct keys from IP, route, actor, params, tenant params, headers, body fields, or resolved resources. Some limits run before authentication; limits that require actor or resource data run afterward. Denied callers do not consume shared post-authorization resource buckets. [S7][S8][S15]

```text
pre-auth limit
  -> authentication
  -> principal requirement
  -> CSRF
  -> resource resolution
  -> grant/action check
  -> authorizer
  -> post-auth limit
  -> handler
```

A hosted platform should attach plan metadata to metrics so that operators can answer which policy rejected a request without logging secrets or high-cardinality payloads.

## 5.8 Audit

If a route declares an audit event, the enforcer records denied, allowed, failed, and completed outcomes. Audit records include route identity, action, actor, resources, status, reason, and redacted authentication attributes. [S7]

The present code ignores errors returned by `AuditSink.RecordAudit`. For a general library this may avoid breaking user traffic when audit storage is unavailable. For the hosted control plane, security-relevant mutations need a stricter durability contract. The platform can use a transactional outbox or fail closed for selected actions.

## 5.9 SecureContext

After enforcement, handlers receive a `SecureContext` containing:

- The validated route plan.
- Parsed request data.
- Params and body.
- Redacted authentication information.
- The actor.
- Resolved resources.
- The action.

The context is not a raw store or token container. Raw bearer values, password material, and refresh-token identifiers do not enter it. [S6]

### Key points

- Planned routes compile security intent into a validated value.
- Builder stages prevent handler registration before access policy is declared.
- Principal kind and credential method are separate constraints.
- Resource identity is declared in JavaScript, but resource loading and authorization remain in Go.
- Rate limits and audit are first-class route-plan fields.

---

# 6. The Enforcer Pipeline

The `Enforcer` is the router-independent implementation behind planned routes. `gojahttp.Host`, standard `net/http` middleware, generated hosts, and custom adapters can all use the same pipeline. [S7][S8]

## 6.1 Ordered enforcement

The order is deliberate:

```text
1. Validate route plan
2. Construct initial SecureContext
3. Apply pre-auth rate limits
4. Authenticate when required
5. Check route credential/principal requirements
6. Verify CSRF for applicable unsafe requests
7. Resolve declared resources
8. Intersect credential grants with the action
9. Call the authorizer
10. Apply post-auth rate limits
11. Record allowed audit state
12. Invoke handler
13. Record completed or failed audit state
```

Changing this order changes security semantics. For example, post-auth rate limits must not run before authorization if a denied caller could exhaust another tenant's resource bucket. CSRF must run before the mutation callback. Resource resolution must happen before resource-based authorization and post-auth limits.

## 6.2 Authentication adapters

The basic `Authenticator` returns an actor. The richer `ResultAuthenticator` returns an `AuthResult` with method, principal kind, credential metadata, grants, scopes, CSRF behavior, and optional verified OAuth context. Older authenticators are adapted to browser-session user results. [S6][S7]

This supports several credential families without making handlers parse headers:

- Server-side browser sessions.
- Application API tokens.
- OAuth-style access tokens.
- Future service credentials.

## 6.3 Grant checks and authorizer checks

A credential may carry grants. The enforcer first checks whether those grants allow the route action on the resource. It then calls the host authorizer for application policy. [S7]

Both checks matter:

- A token cannot exceed the permissions encoded into it.
- A token grant does not override current application policy, membership, suspension, or resource state.

This is especially useful for coding agents. An agent token can be narrowly scoped, while the authorizer still checks current project ownership and environment policy.

## 6.4 Error mapping

Typical status behavior is:

| Condition | Status |
| --- | --- |
| Required credential missing or invalid | 401 |
| Authenticated principal does not satisfy route requirement | 403 |
| CSRF invalid | 403 |
| Resource absent | 404 |
| Action or authorizer denied | 403 |
| Rate limit exceeded | 429 |
| Missing host service or invalid route plan | 500 |

Development mode may expose internal 500 details. Production mode should return generic errors and record detailed diagnostics in structured logs and audit. [S5][S7][S15]

## 6.5 Using the framework without JavaScript

The same route-plan system is available to Go applications:

- `gojahttp.NewApp(host)` for a fluent Go route builder.
- `RegisterPlannedHTTP` for generated or low-level plans.
- `PlannedMiddleware` for an existing router.
- `NewEnforcer` for custom adapters. [S8]

This is important for platform architecture. Native control or management endpoints can share the same security model as JavaScript routes. The system does not need one authorization framework for Go and another for tenant applications.

## 6.6 Why not use middleware order as policy

Traditional middleware stacks can be secure, but their effective policy is procedural. Reviewers must trace the exact nesting order and determine whether a handler is mounted inside or outside each wrapper. A `RoutePlan` is declarative and serializable.

**Decision:** Treat route policy as data and the enforcer as the only interpreter of that data.

This allows the platform to produce a release-time route inventory:

```text
PATCH /orgs/:orgId/projects/:projectId
  principal: session user
  resource: project from projectId, tenant from orgId
  csrf: required
  action: project.update
  rate limits: project-update
  audit: project.update
```

A coding agent can generate this inventory, a policy engine can reject it, and a reviewer can approve it before deployment.

### Key points

- The enforcer is reusable independently of a particular router or JavaScript runtime.
- Enforcement order is part of the security contract.
- Token grants and current application authorization are separate checks.
- Go and JavaScript routes can share one planned-auth system.
- Route inventories should become release artifacts and authority diffs.

---

# 7. Host Authentication, OIDC, Capabilities, and Automation Agents

The HTTP framework separates route policy from authentication infrastructure. Route files declare requirements. `hostauth` constructs sessions, stores, OIDC handlers, application authorization services, capability services, programmatic credentials, and native endpoints. [S9][S10]

## 7.1 Browser OIDC flow

In OIDC mode, native Go handlers own:

```text
GET  /auth/login
GET  /auth/callback
GET  /auth/logout
POST /auth/logout
GET  /auth/session
```

The callback exchanges the authorization code, validates the provider response, maps issuer and subject to a local application user, and creates a server-side application session. The browser receives an opaque app-session cookie. Provider tokens remain server-side. [S9][S10]

This is the correct boundary. JavaScript sees the authenticated actor and redacted claims. It does not receive the OIDC client secret, refresh token, or signing keys.

## 7.2 Public URL versus listen address

The process may listen on `:8080` while users access `https://app.example.test`. OIDC callback URLs and secure-cookie policy must use the browser-visible origin, not the bind address. The configuration therefore separates public base URL, redirect URL, and listen address. [S9][S10]

This distinction should become a standard hosted environment field:

- Internal listen address belongs to the worker.
- Public origin belongs to the environment/domain binding.
- Redirect URIs are derived from the public origin under policy.

## 7.3 Five store families

Hostauth uses separate store interfaces for separate security concepts. They may share one Postgres connection pool, but they must not collapse into one generic key/value API. [S11]

| Store | Responsibility |
| --- | --- |
| Session | Opaque app sessions, CSRF state, metadata |
| Audit | Security-relevant route outcomes |
| AppAuth | App users, tenants, memberships, resources |
| Capability | Limited bearer-like grants, validation, and single-use consumption |
| ProgramAuth | Agents, API tokens, access/refresh families, device codes |

This is a strong model for the hosting platform. Persistence can be physically consolidated while interfaces preserve semantics.

## 7.4 App identity is local identity

An OIDC subject identifies a person at an issuer. Application authorization needs local state: tenants, memberships, resources, suspension, and roles. The appauth store maps external identity into the application's domain model. [S11]

The hosted platform has two identity populations:

1. Platform users who manage organizations, billing, and releases.
2. End users of each hosted application.

They should not share one issuer namespace, key set, or administration boundary merely because Tiny-IDP can serve both.

## 7.5 Capability tokens

The high-level `auth` module lets JavaScript issue and consume constrained capability tokens without direct database access. A token can name its type, resource, tenant, claims, expiry, creator, and single-use policy. The raw token is returned once; the store keeps a hash. [S13]

The issue route is authenticated and authorized. The consume route may be public because possession of the token is the capability, but it validates expected type and resource and atomically marks single-use tokens as consumed.

This pattern is useful beyond invitations:

- Email verification.
- One-time deployment approval.
- Passwordless action links.
- Limited webhook callbacks.
- Delegated file upload.

## 7.6 Programmatic agents

Programmatic authentication separates the durable agent principal, the bearer credential, and the grants. JavaScript can provision agents and issue API tokens through Go-owned builders. Raw token values appear only in issuance results; list and revoke APIs return redacted metadata. [S14]

A route intended for automation declares `express.agent()` and an action. The enforcer parses the token and checks the principal kind and grant before JavaScript runs.

```javascript
app.get("/agent/reports/:reportId")
  .auth(express.agent())
  .allow("report.read")
  .audit("agent.report.read")
  .handle((ctx, res) => {
    res.json({ reportId: ctx.params.reportId, agent: ctx.actor.id });
  });
```

This is directly relevant to coding agents that upload and release applications. Agent identity should remain distinct from human sessions.

## 7.7 Device authorization

Hostauth includes an application-owned device flow for coding agents. A browser user approves a device request, after which the application creates an agent and issues application-owned access and refresh credentials. These are not Tiny-IDP tokens even if the user authenticated through Tiny-IDP. [S17]

The latest production-hardening design identifies remaining single-node work:

- Derive a trustworthy client address behind a configured proxy.
- Apply rate limits and action policy to native device endpoints before durable work.
- Use a server-owned verification URI.
- Allow owners to inspect, deny, list, disable, and revoke their own agents.
- Make readiness probe actual SQL dependencies rather than configuration shape. [S17]

The document also distinguishes a later OAuth resource-server slice. The route contract already models exact issuer, resource, and scope requirements, but the first production verifier profile and end-to-end Tiny-IDP access-token flow remain a separate delivery. [S6][S17]

## 7.8 Single-node versus high availability

The current strict hostauth profile is intentionally single-node. It rejects in-memory persistent stores for critical state, requires secure sessions, and expects schema migration outside the serving process, but it does not claim distributed limiting or multi-replica OIDC transaction behavior. [S17]

The hosted platform should preserve this honesty. A profile must state whether it supports:

- One process.
- Multiple workers on one node.
- Multiple replicas with shared state.
- Cross-region failover.

### Key points

- OIDC login is Go-owned infrastructure; route authorization remains application policy.
- Provider tokens stay server-side and become a local opaque app session.
- Session, audit, app authorization, capability, and programmatic-auth stores are separate concepts.
- Agents, tokens, and grants are distinct objects.
- The current production hardening plan is a measured single-node profile, not an HA claim.

---

# 8. Guarded Outbound HTTP and Native Capabilities

Inbound HTTP is only half of a hosted application. Applications call payment APIs, email providers, storage services, model endpoints, and other internal services. Arbitrary outbound network access would undermine the module and entitlement model, so `go-go-goja` exposes a guarded `fetch` module. [S16]

## 8.1 Outbound HTTP is authority

The fetch module requires an explicit `allow: true`. It can restrict origins, set a default timeout, cap buffered response size, and limit credential sources. [S16]

```yaml
runtime:
  modules:
    - provider: host
      name: fetch
      config:
        allow: true
        allowedOrigins:
          - https://api.example.test
        timeout: 5s
        maxResponseBytes: 1048576
        credentials:
          allowFiles: true
          allowedFiles:
            - /run/secrets/example-token.json
```

This is the correct general rule for hosted modules: selecting the module is not enough. The module has a policy and a binding.

## 8.2 Go-owned credential sources

The API provides Go-owned bearer credential builders for literals, environment variables, and files. The client rejects arbitrary JavaScript auth maps for sensitive input so that policy checks and redaction remain in Go. [S16]

For the hosted platform, raw environment and filesystem sources should usually be replaced with a secret-reference capability:

```javascript
fetch.client()
  .baseUrl("https://api.example.test")
  .auth(fetch.auth.bearer().fromBinding("example-api"))
```

The worker would resolve `example-api` through its release bindings and inject the credential only into the outbound request.

## 8.3 Origin policy is not full egress policy

An origin allowlist at the module layer is useful but not sufficient for hostile tenants. The execution environment should also enforce network policy through a proxy or sandbox. The proxy can handle DNS rebinding resistance, private-address restrictions, TLS policy, request/response metering, and central audit.

```text
JavaScript fetch
  -> Go module validation
  -> release binding and origin policy
  -> egress proxy
  -> destination
```

## 8.4 Payments as a narrow module

A payments module should not expose a provider secret and generic fetch. It should expose reviewed operations:

- Create checkout session.
- Create customer portal session.
- Read bounded subscription state.
- Request a refund under policy.
- Verify and decode webhook events.

The module owns credentials, idempotency, allowed products, redirect domains, webhook signatures, and replay protection. JavaScript supplies business choices through typed inputs.

## 8.5 Capability descriptor

Every hosted native module version should declare:

| Field | Purpose |
| --- | --- |
| Canonical ID and version | Release identity and upgrades |
| Runtime ABI | Compatibility with worker binary |
| Permissions | Network, storage, secrets, effects |
| Configuration schema | Static non-secret module options |
| Binding schema | Required resources and secret references |
| Egress policy | Allowed service classes or origins |
| Limits | Calls, bytes, rows, concurrency |
| Metering dimensions | Billable usage |
| Type declarations | Agent and developer experience |
| Lifecycle | Build-time, runtime, or invocation-scoped |
| Risk class | Required isolation and approval |

**Decision:** Commercial entitlement, runtime selection, permission, quota, and resource binding are separate checks.

A customer may be entitled to use SQLite but have no database bound in a specific environment. A token may be entitled to call a payment module but lack the action grant for refunds. These distinctions should be visible in the data model.

### Key points

- Outbound HTTP is an explicit host capability.
- Origin limits, timeouts, body limits, and credential-source policy belong in Go.
- Secrets should be referenced through release bindings rather than copied into JavaScript variables.
- Sensitive integrations should expose narrow domain operations, not generic network plus a secret.
- Module metadata must support policy, metering, documentation, and reproducibility.

---

# 9. Browser Assets, Widget IR, and Server-Driven UI

A hosted platform needs a browser strategy. xgoja already establishes one boundary: browser bundles are built by browser tooling and included as assets; xgoja compiles JavaScript that runs inside Goja, not frontend code. [S1]

The platform should support two primary UI modes.

## 9.1 Static browser applications

Customers may build React, Vue, Svelte, or plain browser assets. The build plane runs standard frontend tooling in a separate sandbox, stores content-hashed artifacts, and serves them through a CDN or read-only asset module.

The Goja application supplies APIs and server actions. The browser application remains an ordinary browser program subject to a Content Security Policy and origin policy.

## 9.2 Widget IR pages

The Widget DSL research uses JavaScript to construct a serializable page intermediate representation. Go owns data access and execution. React owns rendering through a component registry. Actions and bindings are data rather than callbacks on the wire. [S21]

```text
Goja page handler
    -> versioned WidgetPage JSON
    -> Go validation
    -> browser WidgetRenderer
    -> approved component registry
```

A minimal node protocol has text, element, and component nodes. A production protocol should additionally define:

- Schema version.
- Renderer and component-registry digest.
- Component allowlist.
- Maximum depth, node count, text size, collection size, and total bytes.
- Typed properties.
- Action schema.
- Binding and interpolation rules.
- Accessibility requirements.
- Cache variation rules.

## 9.3 Actions refer to program handlers

A server action should be a reference to a named application handler, not a serialized function:

```json
{
  "type": "server",
  "handler": "checkout.start",
  "input": {
    "productId": { "from": "row.id" }
  }
}
```

The host resolves the handler in the release's application contract, validates input, applies route/action policy, enforces idempotency, invokes JavaScript, and records effects.

## 9.4 The current HTML UI DSL

`ui.dsl` constructs HTML nodes and includes a raw HTML primitive. It is useful for trusted applications and simple server-side pages. It should not be the default safe UI protocol for arbitrary tenants because raw HTML, scripts, styles, arbitrary attributes, and direct redirects require a much broader browser trust model. [S4]

A hosted product can expose two profiles:

- `widget.ui` as the normal constrained, versioned interface.
- `unsafe.html` as a privileged module requiring explicit approval and a restrictive CSP.

## 9.5 Why UI needs a versioned protocol

A coding agent can generate Widget IR against TypeScript declarations and component documentation. If the renderer is pinned in the release, the same source produces the same intended component contract. Without a pinned renderer and registry, a frontend deployment could silently reinterpret an old release.

**Decision:** The renderer version and registry digest are part of the release lock.

### Key points

- Browser bundles and Goja programs are different build products.
- Widget IR provides a constrained server-driven UI path for coding agents.
- Actions should reference named server handlers rather than serialize functions.
- Raw HTML should be privileged, not the default managed UI capability.
- Renderer identity belongs in the immutable release.

---

# Part III — From Repositories to a Hosting Platform

# 10. What go-go-host Contributes

`go-go-host` is an early hosting control plane. It already models users, organizations, memberships, sites, domains, quotas, capabilities, deployments, agents, keys, grants, nonces, deploy runs, audit events, and runtime status. It separates HTTP transport, control services, persistence, deployment validation, runtime lifecycle, and JavaScript-facing modules. [S18]

These concepts are worth preserving. The current in-process execution implementation is not the final production plane.

## 10.1 Valuable control-plane structure

The repository's layering rule is sound:

```text
HTTP handler / CLI adapter
    -> control service
        -> store / deploy / runtime subsystem
            -> database / filesystem / runtime
```

Authorization and product invariants belong in control services. HTTP handlers and dashboards are adapters, not enforcement points. Postgres migrations and sqlc provide a disciplined persistence path. [S18]

## 10.2 Immutable deployment records

A deployment record is reserved before validation so artifact paths and version identity are stable. Upload and activation are separate. A candidate is unpacked, loaded in a dry-run runtime, smoke-tested, then marked validated or rejected. Activation creates a new runtime and checks health before swapping traffic. [S18]

The principles are correct:

- Candidate identity exists before validation.
- Validation does not immediately affect traffic.
- Live traffic changes only after a health check.
- Previous versions remain available for rollback.

## 10.3 Agent identity and grants

Agents have separate machine identities and keys. Grants scope them to organizations and sites, allowed channels and paths, and activation rights. Nonces provide replay protection. This is the correct foundation for coding-agent release workflows. [S18]

## 10.4 The current execution subsystem

The current `SiteRuntime` opens a per-site SQLite database, builds a Goja runtime, registers a small set of modules, loads every `.js` file in lexical order, and serves routes through a site-specific web host. The `Supervisor` maps hosts and sites to active runtimes and swaps the map after health checking a candidate. [S18]

This implementation was useful for proving the product loop. It should now be replaced by the richer `gojahttp` and xgoja framework rather than extended in parallel.

The duplication is important:

| Current go-go-host subsystem | Existing go-go-goja capability |
| --- | --- |
| `internal/sitejs/web` route host | `pkg/gojahttp.Host` |
| Local Express registrar | `modules/express` plus HTTP provider |
| Anonymous session DTO | `gojahttp` hostauth session system |
| HTML `ui.dsl` | Existing module plus Widget DSL direction |
| Manual module selection | xgoja providers and runtime plans |
| Manual script directory walk | xgoja source graph and generated application loading |

**Decision:** go-go-host should consume generated runtime profiles and `gojahttp`; it should not maintain a second HTTP framework.

## 10.5 Control plane versus worker plane

The daemon currently contains both the control plane and active customer VMs. A hostile loop, native module defect, or memory exhaustion can therefore affect the API that manages all customers.

The target split is:

```text
Control-plane API and database
    -> desired release and worker records
    -> worker scheduler / reconciler
    -> isolated worker processes or pods
    -> router sends traffic to ready release workers
```

The control plane should not import customer application packages or open customer SQLite files.

### Key points

- go-go-host already has valuable product entities and service layering.
- Upload, validation, and activation are correctly separated in concept.
- Agent keys and grants are a strong foundation for coding-agent workflows.
- The current JavaScript host duplicates a narrower version of go-go-goja's HTTP framework.
- The control plane and tenant execution must become separate processes.

---

# 11. Releases, Deployments, and Traffic Generations

A single “deployment” object is often asked to represent source code, a build attempt, an artifact, environment configuration, live traffic, and running processes. That overload makes rollback and audit ambiguous. The hosted platform should separate these objects.

## 11.1 The release vocabulary

| Object | Meaning |
| --- | --- |
| Source revision | Exact uploaded archive or Git commit |
| Build | One attempt to compile a source revision under a runtime profile |
| Artifact | Immutable signed executable/image plus source bundle, SBOM, and provenance |
| Release | Artifact plus environment configuration, module lock, bindings, policy, and entitlement snapshot |
| Deployment | One attempt to make a release available in an environment |
| Traffic generation | Immutable routing decision assigning percentages to releases |
| Worker revision | Concrete running instance or pool for one release |

A release is the unit that should be reproducible and rollbackable. A deployment is an operation that may fail. A traffic generation is the live decision.

## 11.2 Candidate lifecycle

```text
source revision created
    -> build queued
    -> build succeeded
    -> artifact signed
    -> release assembled
    -> policy approved
    -> preview workers started
    -> smoke checks passed
    -> release ready
    -> traffic generation committed
    -> previous release draining
    -> previous release retired
```

Each transition records actor, inputs, expected prior state, output digests, and audit event.

## 11.3 Database as source of truth

The current supervisor swaps in-memory maps and then updates the database. If the database update fails, traffic and persisted state can disagree. The target platform uses a database compare-and-swap for the traffic generation, writes an outbox event in the same transaction, and lets routers reconcile. [S18]

```text
transaction:
  verify expected current generation
  insert new traffic generation
  update environment current generation
  insert audit event
  insert outbox event
commit
```

The router may briefly lag the database, but it is reconciling toward one authoritative state.

## 11.4 Draining

A replaced worker should stop receiving new requests and continue serving in-flight requests until completion or a drain deadline. Only then should its runtime close.

```text
ready candidate
    -> publish new generation
    -> router stops new traffic to old release
    -> wait for in-flight count = 0
    -> cancel background work
    -> close runtime
    -> kill after hard deadline
```

## 11.5 Rollback

Rollback creates a new traffic generation pointing to a named earlier release. It does not mutate history and does not choose “previous validated” implicitly.

Database compatibility must be explicit. A code rollback may be unsafe after a destructive migration. Releases should declare schema compatibility ranges and use expand/contract migrations. Backup restore is a separate privileged operation.

## 11.6 Artifact contents

A release artifact should include:

- Exact source archive.
- Compiled JavaScript/TypeScript bundle.
- Serializable application contract.
- Callback-registry fingerprint.
- Runtime profile and module lock.
- TypeScript declarations used by the build.
- Static assets or asset digest.
- Renderer/Widget registry identity.
- Tests and build-check results.
- SBOM and provenance.
- Signature.

### Key points

- Source, build, artifact, release, deployment, traffic, and worker are different objects.
- The database should own the live traffic decision.
- Routers and workers reconcile desired state rather than invent it.
- Rollback creates a new immutable traffic generation.
- Database compatibility and code rollback must be designed together.

---

# 12. Module Catalogs, Subscriptions, Entitlements, Quotas, and Bindings

A commercial module system introduces vocabulary that technical registries do not currently provide. `xgoja` calls optional provider extension interfaces “capabilities,” while go-go-host uses site capabilities as module allow flags. The platform needs more precise terms.

## 12.1 Six separate concepts

| Concept | Definition |
| --- | --- |
| Provider extension | Trusted Go hook contributed to xgoja composition |
| Runtime module | JavaScript-visible API selected into a profile |
| Permission | Authority granted to executing code |
| Entitlement | Commercial right held by an account |
| Quota | Allowed amount of resource or operation |
| Binding | Concrete resource or secret connected to an environment |

Rename xgoja's generic `PackageCapability` concept to `ProviderExtension` or `ProviderContribution` before adding hosted permissions. The current name is technically valid but will collide with product security language. [S1]

## 12.2 Module version record

A catalog entry should contain:

```text
module identity
  id, version, aliases, provider package, checksum, ABI

security contract
  permissions, risk class, egress, secret types, effects

resource contract
  required bindings, state ownership, migration behavior

execution contract
  lifecycle, concurrency, timeouts, max payloads

commercial contract
  feature/SKU, metering dimensions, quota classes

user contract
  TypeScript declarations, docs, examples, deprecation status
```

Aliases such as `database`, `db`, and `sqlite` resolve to one canonical module version and one entitlement. An alias must never bypass policy.

## 12.3 Entitlement resolution

Release creation performs entitlement checks:

```text
requested modules
    -> canonical catalog resolution
    -> exact versions
    -> account entitlement check
    -> environment policy check
    -> resource binding resolution
    -> effective permission calculation
    -> build profile
    -> immutable entitlement snapshot in release
```

Workers do not call the billing provider. They verify that the signed release contains an approved entitlement snapshot and that the control plane has not suspended it.

## 12.4 Subscription changes

A downgrade policy should be explicit:

- New releases requiring the removed module are blocked immediately.
- Existing releases may continue for a configured grace period.
- A security or abuse suspension may stop them immediately.
- Re-enabling service produces a new control-plane decision, not a mutated artifact.

This prevents a billing webhook from unpredictably changing a running VM's module set.

## 12.5 Quotas and metering

Quotas can apply at several levels:

| Level | Examples |
| --- | --- |
| Build | Source bytes, build minutes, artifact bytes |
| Release | Module count, domains, bound resources |
| Worker | Memory, CPU, process count, pool size |
| Invocation | Timeout, output bytes, capability calls, DB rows |
| Monthly usage | Requests, compute milliseconds, egress bytes, storage |

Metering events should be append-only and idempotent. Billing aggregation is downstream of enforcement. A failed billing export must not erase usage evidence.

## 12.6 SQLite as module and resource

SQLite is not only a JavaScript API. It is also a persistent file, backup policy, schema state, and placement constraint.

- The **module** exposes query and transaction operations.
- The **resource instance** owns the database file and backups.
- The **binding** attaches an environment to the resource.
- The **worker policy** ensures a single active writer when local storage is used.

A product should not imply arbitrary horizontal scale for a local SQLite file. It can provide a well-defined single-active-worker profile and separate scalable database products.

### Key points

- Provider hooks, modules, permissions, entitlements, quotas, and bindings must not share one field.
- Module versions need security, resource, execution, commercial, and user-facing metadata.
- Entitlements are resolved when a release is created and captured immutably.
- Subscription changes do not mutate a running runtime profile.
- Stateful modules require explicit resource and placement semantics.

---

# 13. Agent-Driven Releases, Approval, and Audit

Coding agents are expected users of the platform. The release system should assume that an agent can generate valid code quickly and can also make an incorrect authority request quickly. The safety model cannot depend on a human reading every line.

## 13.1 Agent identity

An agent has:

- Durable principal ID.
- Public keys and key lifecycle.
- Organization/project/environment grants.
- Allowed source paths and channels.
- Permission to build, propose, promote, or rollback.
- Optional expiry.
- Nonce and replay-protection state.

Human credentials are not reused for automated deployment.

## 13.2 Signed proposal payload

A release proposal signature should cover a canonical payload:

```json
{
  "organization": "o1",
  "project": "p1",
  "environment": "production",
  "sourceDigest": "sha256:...",
  "artifactDigest": "sha256:...",
  "releaseDigest": "sha256:...",
  "expectedTrafficGeneration": 41,
  "runtimeProfileDigest": "sha256:...",
  "policyDigest": "sha256:...",
  "bindingsDigest": "sha256:...",
  "migrationDigest": "sha256:...",
  "idempotencyKey": "...",
  "timestamp": "...",
  "nonce": "..."
}
```

The signature proves who submitted the proposal and what bytes were proposed. It does not prove that the proposal is safe. The server recomputes policy and entitlement decisions.

## 13.3 Authority diff

A release review should show authority changes before code changes:

```text
+ module payments@1.2.0
+ permission network.egress: payment-provider
+ binding stripe-production
+ effect payment_session_create
~ database schema 12 -> 13
- module legacy-mailer@0.8.1
```

Require explicit approval for:

- New native modules.
- New secrets or bindings.
- New egress destinations.
- Identity and payment authority.
- Unsafe HTML.
- Destructive migrations.
- Increased time, memory, concurrency, or body limits.
- Major module upgrades.

## 13.4 Compare-and-swap promotion

A promotion request includes the traffic generation the agent expects. If another actor has promoted a release since the agent prepared its proposal, the operation fails rather than silently overwriting the newer state.

## 13.5 Audit durability

Audit events should be append-only and transactionally coupled to state mutations. At minimum they record:

- Actor type, principal, key ID.
- Organization, project, environment.
- Request and idempotency IDs.
- Source, artifact, release, profile, and policy digests.
- Before and after traffic generation.
- Approval result.
- Worker rollout result.
- Failure reason.

The current repositories often ignore audit sink errors. The hosted product should classify operations:

- **Best-effort request audit** may continue when the sink is degraded, with a security event.
- **Control-plane mutation audit** must commit with the mutation through an outbox or fail.

## 13.6 Release evidence

A coding agent should be able to attach machine-readable evidence:

- Static route inventory.
- Program contract validation.
- Unit tests using fake capabilities.
- Preview smoke results.
- Browser screenshots or accessibility results for Widget pages.
- Database migration checks.
- Dependency and vulnerability reports.
- Authority diff.

This evidence is part of the release record and can be re-evaluated by policy.

### Key points

- Agents are first-class machine principals, not disguised users.
- Signatures authenticate proposals; server policy still decides.
- Authority diffs make risky changes visible before line-level review.
- Promotion uses compare-and-swap against the expected traffic generation.
- Control-plane mutation audit must be transactionally durable.

---

# 14. The Execution Plane and Isolation

Goja constrains the JavaScript language environment, but it is not an operating-system sandbox. A native module is Go code in the worker process. A defect or excessive allocation can affect the process even when JavaScript has no `fs` or `exec` module.

## 14.1 Worker boundary

The target execution unit is one tenant release in an isolated worker process or sandbox.

```text
router
  -> release worker group
       -> bounded pool of exclusive Goja runtimes
       -> capability/resource brokers
       -> external resources
```

A worker contains only the native modules selected by the runtime profile. It receives no control-plane database credentials.

## 14.2 One invocation per VM

A VM worker is acquired exclusively. One request or job invokes one named handler. The worker is released only if the invocation completed within policy and cleanup succeeded. Any interrupt, panic, protocol violation, or uncertain state poisons the worker.

This follows the Tiny-IDP pool design, which creates equivalent runtime images from an immutable artifact and replaces unsafe workers. [S20]

## 14.3 Warm pools

A warm pool belongs to one release generation. Do not mix tenants or releases in one VM pool.

Benefits:

- Source and module state are loaded once per worker.
- Callback registry fingerprint is verified on load.
- Invocation-scoped capabilities can be installed and removed.
- A poisoned worker can be replaced from the same artifact.

Pool saturation should return a controlled overload response or queue according to the surface. It should not start unbounded goroutines or VMs.

## 14.4 Operating-system limits

Each worker should have:

- Read-only root filesystem.
- Dedicated unprivileged UID.
- CPU, memory, PID, file, and log limits.
- No host filesystem mounts.
- No network by default.
- Egress through a policy proxy.
- Ephemeral writable space except explicit resource mounts.
- Short-lived workload identity.
- Hard process termination after deadline.

A sandbox runtime such as gVisor can strengthen tenant separation. The exact mechanism is an infrastructure choice; the architectural requirement is that hostile tenant code cannot share the control-plane process.

## 14.5 Stateful placement

A local SQLite resource requires placement and lease rules. A worker scheduler should acquire a lease before mounting the resource. A second worker cannot become active on another node until the first lease expires or is revoked safely.

```text
release requests sqlite binding
    -> scheduler obtains resource lease
    -> worker mounts volume
    -> readiness verifies DB
    -> router enables traffic
```

## 14.6 Worker protocol

The control plane should communicate desired state, not execute callbacks directly. A worker protocol may include:

- Load release.
- Report readiness.
- Invoke handler.
- Begin drain.
- Report in-flight count.
- Stop release.
- Export metrics and structured logs.

The signed release manifest is verified by the worker before loading source.

### Key points

- Goja is a language/runtime boundary, not the final tenant isolation boundary.
- One tenant release belongs in a separate worker process or sandbox.
- VM workers are exclusive and discarded after uncertain execution.
- Warm pools are release-specific.
- Stateful resources require leases and explicit placement semantics.

---

# Part IV — A General Application Program Model

# 15. What Tiny-IDP Teaches About Safe JavaScript Programs

The Tiny-IDP scripting branch addresses a different product, but it solves the hardest general problem: how to let JavaScript implement real behavior while Go retains protocol authority.

## 15.1 Serializable program, separate callbacks

`idpprogram.Program` contains workflows, providers, lambda specifications, schemas, capabilities, and declarative tests. It contains no Goja dependency and no JavaScript function values. Callbacks are stored separately in the runtime by stable lambda ID. [S19][S20]

This separation produces two artifacts:

1. A serializable contract that tools can validate and inspect.
2. A runtime callback registry that only a VM owner can invoke.

## 15.2 Lambda contract

Each lambda declares:

- ID and kind.
- Input and output schema.
- Allowed outcome kinds.
- Required capability versions.
- Allowed native effects.
- Timeout.
- Maximum capability calls.
- Maximum output bytes.
- Source location. [S19]

The metadata is enforcement data. A lambda cannot call an undeclared capability. A result outside the allowed outcomes or output schema invalidates the invocation.

## 15.3 Compiler runtime

The compiler executes source in an isolated runtime that exposes only the Tiny-IDP builder module. Ambient file loaders and default modules are disabled. It applies source and time limits, materializes the program, validates it, computes fingerprints, and creates an immutable artifact. [S20]

At worker load, the same source must reproduce the same program and callback registry. A mismatch fails activation.

## 15.4 Invocation-scoped capabilities

A worker receives capability bindings for one invocation. Each binding has an ID/version, input and output byte limits, and a Go function. Capability calls create promises, perform native work, and settle back on the runtime owner. The binding counts calls and becomes inactive when the invocation ends. [S20]

This prevents a callback from retaining a capability object and using it later under a different request.

## 15.5 Secrets and evidence

Secret values are represented by opaque handles. Native-verified evidence, such as a verified email, is injected by the executor and cannot be forged by returning a similar JavaScript object. [S19][S20]

The general platform can apply the same distinction:

- **Input data** can come from the request.
- **Secret handles** refer to host-owned values.
- **Evidence** proves a native verification step occurred.
- **Effects** request native state changes.

## 15.6 Structured outcomes

Tiny-IDP handlers return outcome families such as continue, present, challenge, commit, complete, deny, skip, and error. Exceptions are infrastructure errors, not policy denials. [S19]

This explicit result model is more auditable than arbitrary side effects. It also supports durable workflows.

## 15.7 General lesson

**Decision:** The agent-facing application API should compile JavaScript into a serializable program contract plus named callbacks.

Express remains valuable, especially for existing applications, but a general hosted platform benefits from a higher-level program description for functions, pages, actions, schedules, and workflows.

### Key points

- Safe scripting separates a serializable program contract from VM-owned callbacks.
- Lambda metadata is enforced, not merely documented.
- Compilation runs in an isolated collector runtime.
- Capabilities, secrets, evidence, and effects are distinct boundary types.
- Worker load verifies fingerprints before activation.

---

# 16. A Generic Hosted Application Contract

The Tiny-IDP contract can be generalized into a repository-neutral application model.

## 16.1 Program shape

```go
type Program struct {
    APIVersion   string
    Name         string
    Routes       map[string]RouteSpec
    Functions    map[string]HandlerSpec
    Pages        map[string]PageSpec
    Actions      map[string]HandlerSpec
    Schedules    map[string]ScheduleSpec
    Workflows    map[string]WorkflowSpec
    Schemas      map[string]Schema
    Capabilities map[string]CapabilityRequirement
    Resources    map[string]ResourceRequirement
    Tests        []ProgramTest
}
```

The contract is not required to replace `RoutePlan`. A route specification can contain or compile to the existing `gojahttp.RoutePlan`. This preserves the mature enforcer while adding release-wide static analysis.

## 16.2 Handler contract

```go
type HandlerSpec struct {
    ID                   string
    Kind                 HandlerKind
    InputSchema          string
    OutputSchema         string
    RequiredCapabilities []CapabilityRequirement
    AllowedEffects       []EffectKind
    AuthPlan             *gojahttp.RoutePlan
    Idempotency          IdempotencyPolicy
    Budget               InvocationBudget
    SourceLocation       SourceLocation
}
```

Budgets should cover:

- Wall-clock and CPU time.
- Input, output, and log bytes.
- Capability calls and concurrency.
- Database rows and result bytes.
- Network requests and bytes.
- Effects and continuation payload size.

## 16.3 JavaScript API

```javascript
const A = require("@gogo/app").v1;

module.exports = A.program("shop", app => {
  app.http("catalog.home", {
    method: "GET",
    path: "/",
    public: true,
    output: "widget.page/v3",
    capabilities: ["catalog.read@1"],
    budget: {
      timeoutMs: 100,
      maxCapabilityCalls: 10,
      maxOutputBytes: 262144
    }
  }, async ctx => {
    const products = await ctx.cap.catalog.read({ limit: 20 });
    return ctx.page.shop({ products });
  });

  app.action("checkout.start", {
    input: "checkout.request/v1",
    output: "checkout.result/v1",
    capabilities: ["payments.checkout.create@1"],
    effects: ["payment_session_create"]
  }, async ctx => {
    return ctx.cap.payments.createCheckout(ctx.input);
  });
});
```

The compiler registers callback IDs, validates declarations, emits the route inventory and module requirements, and runs declarative tests with fake capabilities.

## 16.4 Integration with gojahttp

At activation:

```text
Program.RouteSpec
    -> compile/validate RoutePlan
    -> register planned route in gojahttp.Host
    -> route handler invokes named application lambda
    -> lambda result converted to response or Widget page
```

The enforcer remains the sole interpreter of HTTP security policy. The generic application executor owns handler schemas, budgets, capabilities, and effects.

## 16.5 Compatibility Express profile

Existing Express applications can remain supported:

- The route script registers planned routes directly.
- xgoja static analysis inventories native imports.
- Runtime budgets apply around each HTTP callback.
- Raw routes are disabled.
- A route-descriptor export becomes part of the release.

The new program API is the preferred agent-facing profile, not an immediate requirement for all existing code.

## 16.6 Declarative tests

A program test names a handler, input, fake capability outputs, expected outcome, and optional effect assertions. It contains no arbitrary host authority.

```javascript
app.test("catalog empty state", {
  handler: "catalog.home",
  input: {},
  fakes: {
    "catalog.read": []
  },
  expect: {
    outcome: "complete",
    outputSchema: "widget.page/v3"
  }
});
```

These tests give coding agents a fast release gate before a worker is started.

### Key points

- The generic program contract should compile to existing route plans rather than replace the enforcer.
- Handler schemas, budgets, capabilities, effects, and idempotency are release metadata.
- A compatibility Express profile can coexist with a higher-level agent-facing API.
- Declarative tests are bounded artifacts that the platform can run with fake capabilities.

---

# 17. Durable Workflows and Explicit Continuations

An HTTP request can await a bounded database or network call. It cannot keep a JavaScript promise alive across a browser form, process restart, release rollout, or worker relocation. Durable workflows require explicit continuation state.

## 17.1 In-request await

This is safe when bounded:

```javascript
async function submitted(ctx) {
  const member = await ctx.cap.community.lookup({ email: ctx.input.email });
  return member ? ctx.complete(member) : ctx.deny("not_a_member");
}
```

The request remains open. The capability has a deadline and call budget. Promise settlement occurs through the runtime owner.

## 17.2 Browser boundary

A form presentation returns normally:

```javascript
return ctx.present.form({
  schema: "signup.form/v1",
  resume: "signup.submitted"
});
```

Go validates the presentation, stores a continuation, renders the form, and releases the VM worker. The later POST loads the continuation and invokes `signup.submitted` as a fresh call.

## 17.3 Continuation record

A continuation should pin:

- Program/release digest.
- Workflow and resume handler.
- Input and carry schema versions.
- Authenticated actor and tenant binding where applicable.
- Browser/session/CSRF binding.
- Original validated request digest.
- Evidence and secret references.
- Creation, expiry, consumption, and terminal outcome.

It must not serialize a Goja heap, closure, promise resolver, raw password, cookie, or database transaction.

## 17.4 Release changes during a workflow

When a new release is promoted before a continuation resumes, the system needs an explicit policy:

- Resume under the pinned old release while it remains retained.
- Migrate the continuation through a declared schema adapter.
- Expire the continuation and restart the workflow.

Implicitly invoking the new handler with old carry data is unsafe.

## 17.5 Identity workflows

Tiny-IDP should remain the identity kernel. Tenant-authored identity workflows can run in the isolated worker plane through a typed remote protocol:

```text
Tiny-IDP validates OAuth/browser request
    -> calls pinned workflow release with bounded event
    -> receives structured outcome
    -> applies native challenge/effect
    -> stores continuation
    -> issues protocol artifacts
```

JavaScript never validates redirect URIs, PKCE, JWTs, cookies, codes, or signing keys. [S19]

### Key points

- An in-request promise is not a durable workflow state.
- Browser and external waits use explicit versioned continuations.
- Continuations pin release and schema identity.
- Go owns replay protection, secrets, evidence, and irreversible effects.
- Identity protocol authority stays in Tiny-IDP even when workflow behavior is scripted.

---

# Part V — Evaluation and Implementation Plan

# 18. What to Preserve, Change, Retire, and Add

This chapter converts the architectural reasoning into repository-level decisions.

## 18.1 Preserve

### go-go-goja and xgoja

Preserve:

- Owned runtime, event loop, runtime owner, call context, closers.
- Explicit provider and runtime-module composition.
- xgoja v2 sources, commands, artifacts, and static import graph.
- TypeScript declaration generation.
- `gojahttp.Host`, planned routes, staged builders, `Enforcer`, mounts, and HTTP provider.
- Hostauth separation of sessions, audit, appauth, capabilities, and programauth.
- Guarded fetch and Go-owned credential builders.
- Generated runtime packages and host-service injection.

### go-go-host

Preserve:

- Organizations, memberships, projects/sites, environments, domains.
- Agents, keys, grants, nonces, deploy runs.
- Quotas, audit vocabulary, Postgres/sqlc layering.
- Separate upload, validation, activation, and rollback concepts.
- Candidate smoke checks and immutable deployment history.

### Tiny-IDP

Preserve:

- Strict OAuth/OIDC kernel.
- Public embedding boundaries and production validation.
- Serializable program and lambda contracts.
- Isolated compiler runtime and fingerprints.
- Exclusive worker pools and poisoned-worker disposal.
- Opaque secrets, native evidence, structured outcomes and effects.
- Explicit browser continuations.

### Widget DSL

Preserve:

- Versioned serializable UI IR.
- JavaScript composition, Go data/execution, React rendering.
- Data-driven actions and bindings.
- Component registry and browser validation.

## 18.2 Change

### go-go-goja

- Add hosted module descriptors and exact module locks.
- Rename provider extension “capabilities.”
- Formalize interruptible invocation and poison state in the runtime owner layer.
- Freeze registries after build.
- Replace opaque host-service string keys with namespaced typed keys where possible.
- Make body, response, DB, and log limits profile-configurable.
- Define stricter audit durability options.

### go-go-host

- Replace `internal/sitejs/web` and local Express/UI copies with `gojahttp` and xgoja providers.
- Replace recursive script loading with compiled source/program artifacts.
- Persist and enforce the exact effective module and permission set.
- Move tenant execution into isolated workers.
- Replace in-memory traffic swaps with transactional traffic generations and reconciliation.
- Move artifacts from mutable local paths to content-addressed object storage.
- Split deployment records into source, build, artifact, release, rollout, and worker entities.

### Tiny-IDP

- Extract generic program, schema, budget, artifact, and worker abstractions into neutral packages.
- Keep identity-specific effects, evidence, and continuations in Tiny-IDP.
- Add a remote workflow executor for tenant-authored identity behavior.
- Fix pool close semantics so a timeout does not leave resources permanently uncloseable.

### Widget DSL

- Publish a standalone wire-format and validator.
- Pin renderer and registry versions in releases.
- Link server actions to named program handlers.
- Put strict limits on nodes, depth, data, and output bytes.
- Keep raw HTML outside the normal safe profile.

## 18.3 Retire from the primary platform path

- Control plane and tenant VMs in one process.
- `DefaultCapabilities()` on hosted runtime creation.
- One shared site VM serving unbounded concurrent requests.
- Recursive execution of every `.js` file.
- Response timeout without VM interruption.
- Raw routes in production.
- Generic network plus provider secret for payments.
- Anonymous opaque cookie IDs presented as authentication.
- Local mutable filesystem paths as release identity.

## 18.4 Add

- Module catalog, versions, dependencies, entitlements, and pricing features.
- Resource instances and bindings.
- Source revisions, builds, artifacts, attestations, and release locks.
- Traffic generations, allocations, and rollout events.
- Worker revisions, leases, invocations, logs, and usage events.
- Policy decisions, approvals, idempotency records, and transactional outbox.
- Platform identity and separate application identity realms.
- Egress proxy and secret broker.

### Key points

- The target is a refactoring and integration of strong existing components, not a rewrite from zero.
- The most important reuse decision is adopting `gojahttp` throughout go-go-host.
- The largest new subsystem is the isolated worker and release-control model.
- Tiny-IDP's generic scripting mechanisms should be extracted without weakening the identity kernel.

---

# 19. Current Risks and Missing Invariants

The current repositories are active implementation projects, not a finished multi-tenant service. The following risks should be treated as release blockers for unrelated customer code.

## 19.1 Effective capabilities in go-go-host

Bundle validation calculates requested and effective capabilities, but runtime creation currently uses default capabilities rather than the persisted effective set. Database modules are registered regardless of the database boolean. This breaks the connection between policy and execution. [S18]

**Required invariant:** The signed release lock is the only source of runtime modules and permissions, and the worker verifies it before constructing the runtime.

## 19.2 Execution timeout

HTTP timeout wrappers can stop response waiting without interrupting the VM. [S3][S5][S18]

**Required invariant:** Every invocation has an interrupt path, poison state, process-level deadline, and hard kill.

## 19.3 Activation consistency

The current supervisor can swap in-memory routing before persisting the active deployment. [S18]

**Required invariant:** Traffic changes are committed transactionally and routers reconcile the committed generation.

## 19.4 Archive ingestion

The current deployment validator buffers the archive and entries in memory before fully enforcing uncompressed quotas, and canonical path collisions need stronger handling. [S18]

**Required invariant:** Archive scanning is streaming, size-bounded, duplicate-safe, path-safe, and staged atomically.

## 19.5 Audit errors

Several code paths ignore audit write failures. [S7][S18]

**Required invariant:** Control-plane mutation audit is transactionally durable; request audit has an explicit degradation policy.

## 19.6 Trusted proxy identity and readiness

The July 18 hostauth hardening analysis found inconsistent client-IP interpretation between audit and rate limiting, native device endpoints outside the planned enforcer, and readiness that reported configuration rather than SQL reachability. [S17]

**Required invariant:** One canonical request identity is derived once, native routes have their own bounded policy perimeter, and readiness probes actual dependencies.

## 19.7 Pool shutdown

The Tiny-IDP pool can set itself closed, return on a close timeout before canceling/closing workers, and then reject later cleanup attempts. [S20]

**Required invariant:** “not accepting work” and “resources fully closed” are separate states; cleanup is retryable and idempotent.

## 19.8 UI authority

The generic HTML DSL can emit raw HTML and broad attributes. [S4]

**Required invariant:** Arbitrary tenant UI uses a validated Widget protocol or a separately approved unsafe HTML profile.

### Key points

- Current gaps are primarily broken links between declared policy and actual execution.
- Timeouts, activation, archive parsing, audit, proxy identity, and cleanup require explicit invariants.
- The HTTP framework itself is a major asset; the target should harden and integrate it rather than discard it.

---

# 20. Implementation Sequence for an Intern Team

The implementation should advance through coherent vertical slices. Each phase proves one invariant and leaves the system runnable.

## Phase 0 — Baseline and terminology

Deliverables:

- Architecture decision records for the four planes.
- Glossary adopted in code and docs.
- Current route, module, and entity inventory.
- Integration test proving go-go-host can run a `gojahttp` planned public route.

Exit evidence:

- No new use of ambiguous “capability” for both provider extensions and permissions.
- One documented source of truth for route policy and runtime module selection.

## Phase 1 — Replace the duplicate HTTP host

Deliverables:

- go-go-host worker prototype using xgoja/gojahttp HTTP provider.
- Planned public and authenticated routes.
- Raw routes rejected.
- Existing static assets and SQLite binding wired through host services.
- Request timeout paired with VM interruption and worker disposal.

Exit evidence:

- Route inventory lists public/auth/resource/action/CSRF/audit/rate-limit policy.
- A blocked infinite loop does not block the control plane.

## Phase 2 — Artifact and release model

Deliverables:

- Source revision, build, artifact, release, traffic generation tables.
- Content-addressed object storage.
- Runtime lock with exact module versions.
- Signed artifact verification in worker.
- Transactional outbox.

Exit evidence:

- The same release can be loaded on a clean worker and reproduces the same program/profile fingerprints.
- Traffic promotion is compare-and-swap and auditable.

## Phase 3 — Isolated workers

Deliverables:

- Separate worker binary/process.
- Release-specific runtime pool.
- Resource and secret bindings.
- CPU, memory, PID, filesystem, network, log, and invocation limits.
- Drain and hard-stop protocol.

Exit evidence:

- A worker crash or OOM does not interrupt the control-plane API.
- One tenant cannot address another tenant's worker or resource.

## Phase 4 — Generic application contract

Deliverables:

- Neutral program, schema, handler, budget, test, artifact, and worker packages extracted from Tiny-IDP patterns.
- Compiler collector module.
- HTTP route specs compiled to `RoutePlan`.
- Named actions and Widget page handlers.
- Declarative test runner.

Exit evidence:

- Agent-authored source produces a deterministic contract and callback registry.
- Invalid schemas, undeclared capabilities, or illegal outcomes fail before activation.

## Phase 5 — Module catalog and subscriptions

Deliverables:

- Module/version catalog.
- Entitlement and quota model.
- Release-time entitlement snapshot.
- SQLite module/resource/binding split.
- Usage event pipeline.

Exit evidence:

- A user without an entitlement cannot create a release containing the module.
- Removing an entitlement follows the documented grace/suspension policy without mutating artifacts.

## Phase 6 — Platform and application identity

Deliverables:

- Platform OIDC for customer teams.
- Managed application realm and external OIDC modes.
- Programmatic agent lifecycle.
- Trusted proxy identity and SQL readiness.
- Remote Tiny-IDP workflow executor for selected scripted flows.

Exit evidence:

- Platform users and application users have separate issuer and authorization boundaries.
- Agent and browser routes reject the wrong principal types.

## Phase 7 — Widget UI and payments

Deliverables:

- Versioned Widget wire protocol and validator.
- Renderer/registry lock.
- Named server actions.
- Narrow payments module and verified webhook evidence.

Exit evidence:

- Widget pages pass schema, size, accessibility, and browser tests.
- Payment secrets never enter JavaScript or logs.

## Phase 8 — Distributed execution

Deliverables:

- Multi-node scheduler and worker leases.
- Canary and percentage traffic.
- Distributed-safe resources and rate-limit profiles.
- Central metrics, logs, traces, and usage aggregation.

Exit evidence:

- Node loss triggers reconciliation without double-activating single-writer resources.
- Rollout and rollback work through traffic generations across nodes.

### Key points

- Each phase proves a complete invariant rather than adding broad scaffolding.
- The first vertical slice is reuse of `gojahttp` in an isolated worker.
- Reproducible releases and traffic generations precede commercial module complexity.
- Generic scripting extraction follows, rather than blocking, the first hosted HTTP slice.

---

# 21. Worked Trace: From Source to an Authenticated Response

This chapter connects the major components in one concrete sequence.

## 21.1 Build

A coding agent uploads:

```text
app.ts
web/dist/*
app.manifest.json
```

The manifest requests:

```json
{
  "runtime": "web",
  "modules": ["express@1", "sqlite@1", "widget.ui@3"],
  "entrypoint": "app.ts"
}
```

The build plane:

1. Stores the exact source archive and digest.
2. Resolves module versions through the catalog.
3. Checks entitlements and environment policy.
4. Generates an xgoja v2 specification using curated providers.
5. Validates the static source graph.
6. Compiles TypeScript.
7. Runs the program collector and declarative tests.
8. Emits route inventory, program contract, static assets, runtime lock, SBOM, and provenance.
9. Signs the artifact.

## 21.2 Release

The control plane binds:

- `sqlite.primary` to database resource `db_17`.
- `identity.default` to managed realm `realm_9`.
- Public domain `shop.example.test`.
- Widget renderer `renderer_3.4.1`.

It creates release `rel_42` with an immutable entitlement and policy snapshot.

## 21.3 Activation

The worker scheduler:

1. Acquires the SQLite lease.
2. Starts a sandboxed worker with the profile-specific binary.
3. Verifies the release signature and module lock.
4. Creates a runtime factory.
5. Loads a bounded pool of runtime images.
6. Registers planned routes into `gojahttp.Host`.
7. Mounts native OIDC and readiness handlers.
8. Runs smoke requests.
9. Reports ready.

The control plane commits traffic generation 42 pointing 100% to `rel_42`.

## 21.4 Browser login

The browser requests `/account` without a session.

```text
GET /account
  -> route match
  -> pre-auth rate limit
  -> session authenticator
  -> no actor
  -> 401
```

The frontend sends the user to `/auth/login`. The native OIDC handler redirects to the issuer. After callback validation, the host creates a local session and returns an opaque cookie.

## 21.5 Authenticated route

The browser sends:

```http
PATCH /orgs/o1/projects/p7
Cookie: sid=opaque
X-CSRF-Token: ...
Content-Type: application/json

{"name":"New name"}
```

The host executes:

```text
body limit and JSON parsing
  -> request DTO
  -> planned route lookup
  -> pre-auth rate limit by IP and route
  -> session lookup
  -> session-user requirement
  -> CSRF verification
  -> resolve project p7 in tenant o1
  -> token/session grant intersection
  -> authorizer checks project.update
  -> post-auth rate limit by actor and project
  -> audit allowed
  -> acquire release VM worker
  -> inject invocation capabilities
  -> invoke named handler through RuntimeOwner
  -> validate output/effects
  -> send response
  -> audit completed
  -> release worker
```

At no point does JavaScript parse the cookie, load the membership table, verify CSRF, or receive the database filename.

## 21.6 Failure cases

| Failure | Result |
| --- | --- |
| Missing session | 401 before JavaScript |
| Agent API token on session-only route | 403 before JavaScript |
| Stale CSRF token | 403 before resource mutation |
| Project belongs to another tenant | 404 or 403 according to resolver policy |
| Missing `project.update` grant | 403 before authorizer callback or handler |
| Rate limit exceeded | 429 with policy metadata in audit |
| JavaScript exceeds deadline | VM interrupted, worker discarded, 500/504 according to surface |
| Candidate worker unhealthy | No traffic-generation change |

### Key points

- The release lock connects build-time selection to runtime enforcement.
- Authentication and authorization complete before the JavaScript callback.
- The handler runs in an exclusive, bounded worker with only release capabilities.
- Failure paths preserve the active release and produce structured evidence.

---

# 22. Intern Exercises

These exercises are designed to make the architecture concrete. Each exercise should produce code, tests, and a short written explanation of the invariant being proved.

## Exercise 1 — Trace a planned route

Choose one route in an example xgoja host. Record:

- Route registration source.
- Generated or runtime `RoutePlan`.
- Required host services.
- Enforcer order.
- Handler context fields.
- Audit outcomes.
- Expected status for missing auth, wrong principal, missing CSRF, denied action, and success.

Do not begin by changing code. The exercise is complete when another engineer can review the route policy from your trace.

## Exercise 2 — Add a route rate limit

Add a pre-auth IP/route limit and a post-auth actor/resource limit. Write tests proving:

- Anonymous callers share only the intended bucket.
- Two authenticated actors do not share the actor bucket.
- A denied actor does not consume the allowed actor's resource bucket.
- `Retry-After` is returned on 429.

Explain why each limit belongs before or after authorization.

## Exercise 3 — Replace a raw route

Find a raw Express route and migrate it to a planned route. Enable `RejectRawRoutes`. Prove startup or request failure for the old route and success for the planned route.

## Exercise 4 — Define a hosted module descriptor

Write a catalog descriptor for `sqlite@1` containing:

- Permissions.
- Resource binding schema.
- Query and result limits.
- Migration lifecycle.
- Metering dimensions.
- TypeScript declarations.
- Entitlement feature.
- Single-writer placement requirements.

Then show the generated release-lock entry.

## Exercise 5 — Poison a worker

Create a handler that exceeds its execution deadline. Verify:

- The VM is interrupted.
- The invocation returns an error.
- The worker is not returned to the idle pool.
- A replacement worker loads successfully.
- A second request succeeds.

## Exercise 6 — Implement a traffic-generation CAS

Create two concurrent promotion requests with the same expected generation. Exactly one must commit. The other must receive a conflict and must not change traffic.

## Exercise 7 — Build a Widget action

Define a Widget page with a server action. Verify:

- The action names an existing handler.
- Input binding paths validate.
- Unauthorized users cannot invoke it.
- Oversized output is rejected.
- Renderer and registry versions are pinned in the release.

## Exercise 8 — Model a continuation upgrade

Create workflow version 1 with a pending continuation. Promote version 2 with an incompatible carry schema. Implement one explicit policy: pinned old release, migration adapter, or expiry/restart. Prove that the system never passes old carry data to the new handler implicitly.

---

# Appendix A — Reference Architecture

```text
                           CONTROL PLANE

 Dashboard / API / CLI / Coding Agents
                 |
          Platform OIDC + RBAC
                 |
 Organizations / Projects / Environments / Domains
 Releases / Policies / Approvals / Entitlements
 Agents / Keys / Grants / Audit / Usage
                 |
       PostgreSQL + transactional outbox
                 |
          desired traffic generations
                 v

                            BUILD PLANE

 Source archive or Git revision
       -> bounded scanner
       -> JS/TS static graph
       -> program compiler
       -> module and entitlement resolver
       -> xgoja profile generator
       -> tests / SBOM / provenance
       -> signed content-addressed artifact
                 |
                 v

                         EXECUTION PLANE

 Edge/router -> traffic generation -> release worker group
                                      |
                          isolated process/sandbox
                                      |
                           exclusive Goja VM pool
                                      |
                    gojahttp Host + Enforcer + handlers
                                      |
                      capabilities / secrets / resources
                                      |
                    DB / object store / payments / egress

                          IDENTITY PLANE

 Platform issuer ---------------------> control-plane sessions
 Managed app realm / external OIDC ---> app-local sessions
 Tiny-IDP kernel ---------------------> credentials, tokens, keys,
                                        continuations, protocol effects
```

---

# Appendix B — Glossary

**Actor** — A host-owned authenticated principal exposed to a planned route after authentication.

**Agent** — A durable automation principal, distinct from its API tokens and grants.

**Application contract** — Serializable description of routes, handlers, schemas, capabilities, effects, budgets, pages, and tests.

**Artifact** — Signed immutable build output and its provenance.

**Binding** — Connection between an environment/release and a resource or secret reference.

**Capability binding** — Invocation-scoped Go implementation of one declared application capability.

**Continuation** — Durable record that allows a workflow to resume in a fresh invocation after an external boundary.

**Deployment** — Attempt to make a release available.

**Effect** — Native state change requested by a handler and applied under host policy.

**Entitlement** — Commercial right for an account to use a product feature or module.

**Enforcer** — Router-independent interpreter of `RoutePlan` security policy.

**Evidence** — Native-verified fact injected into a handler and not forgeable as ordinary input data.

**Native module** — Trusted Go-backed JavaScript API installed into a Goja runtime.

**Permission** — Authority that a module or handler may exercise.

**Planned route** — HTTP route with a validated host-owned security contract.

**Provider** — Trusted Go package that contributes xgoja modules, commands, sources, declarations, or host services.

**Quota** — Enforced limit on resource or operation amount.

**Release** — Artifact plus exact environment configuration, modules, bindings, policy, entitlements, and renderer identity.

**Resource instance** — Persistent or external service owned by the platform, such as a database or identity realm.

**Runtime lock** — Exact, signed identity of toolchain, source, native modules, ABI, configuration, and renderer.

**Runtime owner** — Serialized scheduler through which all Goja VM access occurs.

**Source revision** — Exact source input to a build.

**Traffic generation** — Immutable routing decision assigning traffic to releases.

**Widget IR** — Versioned serializable page and action protocol rendered by an approved browser component registry.

**Worker revision** — Running process or pool loaded from one release.

---

# Appendix C — Source Map

The following sources were used for the current-implementation descriptions. Repository paths are more stable than prose summaries and should be consulted before changing a subsystem.

[S1] `go-go-golems/go-go-goja`, xgoja v2 planning and generated runtimes:  
- `cmd/xgoja/doc/17-xgoja-v2-reference.md`  
- `pkg/xgoja/app/types.go`  
- `pkg/xgoja/providerapi/module.go`  
- `pkg/xgoja/providerapi/provider_registry.go`  
- `cmd/xgoja/internal/generate/templates/runtime_package.go.tmpl`  
https://github.com/go-go-golems/go-go-goja

[S2] `go-go-golems/go-go-goja`, owned runtime construction and lifecycle:  
- `pkg/engine/factory.go`  
- `pkg/engine/runtime.go`  
- `pkg/engine/module_specs.go`

[S3] `go-go-golems/go-go-goja`, serialized VM ownership:  
- `pkg/runtimeowner/types.go`  
- `pkg/runtimeowner/runner.go`

[S4] `go-go-golems/go-go-goja`, Express-style HTTP module:  
- `pkg/doc/18-express-module.md`

[S5] `go-go-golems/go-go-goja`, HTTP host implementation:  
- `pkg/gojahttp/host.go`  
- `pkg/gojahttp/request_response.go`  
- `pkg/gojahttp/body.go`

[S6] `go-go-golems/go-go-goja`, route-plan types and validation:  
- `pkg/gojahttp/auth_plan.go`

[S7] `go-go-golems/go-go-goja`, planned-route enforcement:  
- `pkg/gojahttp/enforcer.go`

[S8] `go-go-golems/go-go-goja`, Go-native planned-auth API:  
- `pkg/gojahttp/app.go`  
- `cmd/xgoja/doc/18-go-planned-auth-api.md`

[S9] `go-go-golems/go-go-goja`, host composition for Express and OIDC:  
- `cmd/xgoja/doc/19-express-auth-host-integration-guide.md`

[S10] `go-go-golems/go-go-goja`, generated hostauth configuration:  
- `cmd/xgoja/doc/20-hostauth-config-reference.md`

[S11] `go-go-golems/go-go-goja`, auth stores:  
- `cmd/xgoja/doc/21-auth-stores-reference.md`

[S12] `go-go-golems/go-go-goja`, HTTP serve command and hot reload:  
- `cmd/xgoja/doc/22-http-serve-command-reference.md`

[S13] `go-go-golems/go-go-goja`, high-level audit and capability JavaScript APIs:  
- `cmd/xgoja/doc/24-generated-auth-javascript-apis.md`

[S14] `go-go-golems/go-go-goja`, agents and API tokens:  
- `cmd/xgoja/doc/25-programmatic-auth-javascript-apis.md`

[S15] `go-go-golems/go-go-goja`, route credential requirements and rate limits:  
- `cmd/xgoja/doc/26-express-route-auth-requirements.md`

[S16] `go-go-golems/go-go-goja`, guarded outbound HTTP:  
- `cmd/xgoja/doc/27-guarded-fetch-client-api.md`

[S17] `go-go-golems/go-go-goja`, current production hardening plan:  
- `ttmp/2026/07/18/XGOJA-HOSTAUTH-PROD-HARDENING-001--single-node-hostauth-production-hardening/design-doc/01-intern-implementation-guide-for-single-node-hostauth-hardening.md`

[S18] `go-go-golems/go-go-host`, control plane, deployment, runtime, and data model:  
- `README.md`  
- `docs/architecture/data-model.md`  
- `docs/contributing/runtime-and-deployment-guidelines.md`  
- `internal/deploy/bundle.go`  
- `internal/control/deployments.go`  
- `internal/runtime/runtime.go`  
- `internal/runtime/supervisor.go`  
https://github.com/go-go-golems/go-go-host

[S19] `go-go-golems/tiny-idp`, lambda-first identity scripting design on `task/prod-tiny-idp`:  
- `ttmp/2026/07/10/TINYIDP-GOJA-001--go-go-goja-identity-microkernel-scripting-layer/design-doc/03-lambda-first-tiny-idp-javascript-api-with-explicit-browser-continuations.md`  
https://github.com/go-go-golems/tiny-idp/tree/task/prod-tiny-idp

[S20] `go-go-golems/tiny-idp`, program and runtime implementation on `task/prod-tiny-idp`:  
- `pkg/idpprogram/program.go`  
- `pkg/idpprogram/lambda.go`  
- `pkg/idpprogram/validate.go`  
- `pkg/idpscript/compiler.go`  
- `pkg/idpscript/runtime_factory.go`  
- `pkg/idpscript/invoke.go`  
- `pkg/idpscript/pool.go`

[S21] PARC Widget DSL project note and related Widget DSL v3 report:  
- `https://parc.yolo.scapegoat.dev/note/research/kb/projects/widget-dsl`  
- `go-go-golems/go-go-parc`, Widget DSL v3 and Publish Vault project reports

[S22] PARC go-go-goja project note and runtime-system reports:  
- `https://parc.yolo.scapegoat.dev/note/research/kb/projects/go-go-goja`  
- `go-go-golems/go-go-parc`, go-go-goja runtime and HTTP/auth reports

---

# Closing

The reviewed system is not missing a web framework. It already has one of the strongest foundations in the project: Go-owned HTTP lifecycle, planned routes, reusable enforcement, explicit principal requirements, resource-aware authorization, CSRF, rate limits, audit, OIDC sessions, agent tokens, native mounts, guarded outbound access, and generated-host integration.

The hosting platform should make that framework the application boundary. xgoja should define the trusted runtime profile. go-go-host should become the control plane and reconciler. Isolated workers should execute immutable releases. Tiny-IDP should remain the identity kernel while contributing a general model for serializable JavaScript programs, bounded capabilities, effects, evidence, and continuations. Widget IR should provide the normal agent-friendly UI protocol.

The final architecture is coherent because each layer has one responsibility. JavaScript describes behavior. Route plans describe HTTP security. Native modules expose reviewed authority. Releases freeze source and dependencies. The control plane records policy and traffic. Workers enforce limits. Identity services own credentials and protocol state. These boundaries are the platform.
EOF
wc -w /mnt/data/hosted_goja_platform_textbook.md

```

## Turn 137 - assistant (thinking)

- Message ID: `df745a7a-4038-4dac-9f44-8c1e80d81b35`

<details><summary>Thinking</summary>

**Wrote markdown, processed into Word, rendered PDF, and generated images**


</details>

## Turn 138 - assistant (thinking)

- Message ID: `f7849dae-f134-48f1-bb4a-41dca37a86a0`

<details><summary>Thinking</summary>

**Read skill and task documents, listed textbooks, and analyzed images**


</details>

## Turn 139 - assistant (tool call)

- Message ID: `da3f6003-0712-47b9-840c-e57995e1d6b0`
- Model: `gpt-5-6-pro`

```unknown
bash -lc cat > /mnt/data/textbook_work/master.md <<'EOF'
# Building a Secure JavaScript Hosting Platform with Goja

## An intern's guide to go-go-goja, xgoja, gojahttp, go-go-host, Tiny-IDP, Widget DSL, releases, paid modules, and isolated execution

**Status:** Architecture textbook and implementation guide  
**Audience:** Engineers joining the project, including interns and coding-agent operators  
**Scope:** The existing repositories, the design principles already embodied in them, the gaps between the current components, and the proposed production hosting architecture

---

## Preface

The system described in this book has one central purpose: let a customer upload a JavaScript or TypeScript program, select a controlled set of Go-backed modules, and run the result as a secure hosted application. The application may expose HTTP routes, render web interfaces, use a database, authenticate users, call approved external services, accept payments, and be deployed repeatedly by coding agents. A release must be inspectable, versioned, reproducible, auditable, and reversible.

The interesting problem is not JavaScript evaluation. `goja` already evaluates JavaScript in Go. The engineering problem is deciding which authority JavaScript receives, how Go owns the runtime around it, how HTTP security is declared and enforced, how native modules are selected and paid for, how application code becomes an immutable release, and how a failed release is prevented from becoming live.

This book explains those decisions in their dependency order. It begins with trust boundaries and runtime ownership, then moves through modules and xgoja, the secure HTTP framework, UI rendering, the control plane, identity, billing, releases, and isolated execution. Each chapter distinguishes three things:

1. **What exists now.** This is grounded in the reviewed repositories.
2. **What principle the implementation expresses.** This is the reusable reasoning behind the code.
3. **What the hosting platform should do next.** This is the proposed production architecture.

The codebase is active. Names and package boundaries will continue to evolve. The invariants should change much more slowly.

### How to read the diagrams

The diagrams show authority and lifecycle, not package imports alone. A solid arrow usually means data or control moves in that direction. A boundary labeled *trusted* means code inside that boundary is operated by the platform and is not supplied by a tenant. A tenant program is always treated as less trusted than the process that validates its release.

### Running example: Project Desk

The chapters use a small application called **Project Desk**. It has:

- a public health route;
- authenticated project pages;
- a resource-bound project update route;
- a SQLite database;
- Widget IR pages rendered by a browser application;
- a CI agent with an API token;
- a payment action that creates a checkout session;
- releases deployed by an automated agent.

Project Desk is not a special product. It is a compact example that exercises the system's main boundaries.

---

# Part I. The Product and Its Boundaries

## 1. The product is a controlled application host

A hosted program is not merely a file executed by an interpreter. It is a unit of source, native-module selection, permissions, resource bindings, configuration, tests, assets, and operational policy. The platform must preserve that complete unit across build, release, activation, rollback, and audit.

A useful first model is:

```text
source + program contract + module lock + bindings + policy = release
release + traffic decision + worker state = running application
```

This model prevents a common failure: treating source code as the only versioned input. A program compiled with one SQLite module version, one Widget renderer, and one authorization policy is not the same release when any of those components changes.

<!-- DIAGRAM:system_overview -->

### 1.1 Three planes

The target architecture separates three planes.

| Plane | Owns | Must not do |
|---|---|---|
| Control plane | Accounts, projects, environments, policies, entitlements, releases, domains, audit, desired state | Execute tenant JavaScript |
| Build plane | Source scanning, compilation, static validation, module resolution, tests, provenance, artifact signing | Serve public application traffic |
| Execution plane | Route requests to an immutable release and run bounded tenant invocations | Decide billing entitlements or mutate release history |

The separation is not organizational ceremony. It controls the impact of a compromise. A worker that runs a malicious program should not possess control-plane database credentials. A build service that processes an adversarial archive should not also terminate customer traffic. A dashboard should not be able to bypass server-side release policy.

> **Decision: separate control, build, and execution.**  
> **Problem:** One process that accepts uploads, compiles code, manages tenants, and serves applications accumulates every privilege.  
> **Selected rule:** Each plane gets only the data and credentials needed for its role.  
> **Rejected alternative:** A universal daemon with in-process runtimes and direct access to all platform stores.  
> **Resulting invariant:** No tenant program can reach the control-plane store through an ambient process credential.

### 1.2 Current repositories and their roles

The existing repositories already contain most of the required concepts, but they are distributed across projects.

| Repository or subsystem | Existing strength | Intended platform role |
|---|---|---|
| `go-go-goja` | Owned Goja runtimes, module APIs, async boundaries, HTTP framework, authentication helpers | Runtime SDK and secure application host foundation |
| `xgoja` | Provider composition, source graphs, generated binaries, declarations, command surfaces | Trusted build planner and runtime-profile compiler |
| `go-go-host` | Organizations, sites, deployments, agents, grants, audit, quotas, routing | Control-plane seed and release orchestrator |
| `tiny-idp` | Strict OAuth/OIDC kernel and a bounded JavaScript program model | Platform/app identity service and source of generic program-contract patterns |
| Widget DSL | Intent-level UI grammar, typed IR, React target | Safe server-driven web UI protocol |

The platform should not copy each implementation wholesale. It should preserve the strongest boundary from each project and remove duplicated weaker paths.

### 1.3 A vocabulary that prevents category errors

Several words are easy to conflate. The distinction matters because each word is checked at a different time.

| Term | Definition | Checked when |
|---|---|---|
| Provider | A Go package that contributes xgoja modules, sources, command sets, declarations, or host extensions | Build planning |
| Runtime module | A selected JavaScript-visible API such as `express`, `database`, `auth`, or `fetch` | Build and worker startup |
| Permission | An authority granted to a running program, such as outbound access to one origin | Release resolution and invocation |
| Entitlement | A commercial right held by an account, such as use of the SQLite module | Release creation and reconciliation |
| Quota | A numerical limit, such as database bytes or requests per minute | Build, control, and execution |
| Binding | A connection from a release to a concrete resource, secret, issuer, or database | Release creation and worker startup |
| Artifact | A content-addressed built output plus metadata and provenance | Build completion |
| Release | An immutable artifact combined with environment bindings, policy, and entitlement snapshot | Promotion |
| Traffic generation | An immutable routing decision that assigns traffic to releases | Activation and rollback |

A subscription for SQLite is an entitlement. The JavaScript name `db` is a module alias. The database file or managed database is a resource. The right to execute SQL is a permission. The maximum database size is a quota. The connection between the release and that database is a binding. One boolean called `sqliteEnabled` cannot represent all six concepts safely.

### 1.4 Key points

- The product hosts immutable releases, not loose source files.
- Control, build, and execution are separate trust domains.
- Existing repositories should converge around their strongest boundaries rather than retain parallel runtimes.
- Module, permission, entitlement, quota, binding, artifact, and release are separate domain concepts.

---

## 2. Trust is expressed as capabilities and data flow

The platform makes JavaScript useful by giving it carefully selected capabilities. A capability is not a promise that the code will behave. It is the exact authority the host makes available through a typed interface.

Examples include:

- execute a prepared SQLite query against the application's database;
- resolve the current authenticated actor;
- create a payment checkout session for configured products;
- read an object from one application-owned bucket;
- call one allow-listed HTTP origin;
- return a Widget IR page;
- publish a bounded job to one queue.

The unsafe alternative is ambient authority: unrestricted filesystem access, process execution, environment variables, host networking, raw database handles, or control-plane credentials. Ambient authority makes code review incomplete because behavior depends on what happens to be available in the process.

### 2.1 Capability flow

A capability has four layers:

```text
catalog declaration
    -> release requirement
        -> host binding
            -> invocation-scoped JavaScript object
```

The catalog declaration identifies the module version and its security contract. The release requirement records what the application asks for. The host binding supplies the concrete implementation, such as one database. The invocation object exposes only the methods available during one request.

The Tiny-IDP scripting work demonstrates a particularly strong version of this model. Lambdas declare required capabilities and effect classes. At invocation time, the host supplies exactly those bindings, applies call and byte budgets, and discards a worker after an unsafe interruption. The general hosting platform should extract this model into a neutral application-program package.

### 2.2 Authority must be host-owned

JavaScript may declare intent, but it should not manufacture security objects. This rule appears repeatedly in the codebase:

- Express authentication specs are Go-backed objects returned by `express.user()`, `express.agent()`, or `express.oauth()`.
- Resource specs are Go-backed objects returned by `express.resource(type)`.
- Rate-limit specs are Go-backed objects returned by `express.rateLimit(policy)`.
- Guarded fetch credentials are Go-backed builders rather than arbitrary JavaScript maps.
- Tiny-IDP evidence and secret handles originate in Go and cannot be forged from plain objects.

The pattern protects more than type safety. It gives the host an unambiguous identity for security-sensitive declarations and prevents a plain object from bypassing validation.

> **Decision: JavaScript declares intent using host-issued builder objects.**  
> **Problem:** Plain JavaScript objects are easy to forge, omit required fields, or reinterpret inconsistently.  
> **Selected rule:** Security-sensitive builders carry hidden Go identity and are normalized into immutable plans.  
> **Rejected alternative:** Let handlers pass arbitrary policy maps that are interpreted at request time.  
> **Resulting invariant:** A route cannot become protected, resource-bound, rate-limited, or credential-bearing without passing through Go validation.

### 2.3 The sandbox is not the whole boundary

`goja` is an interpreter, not a complete multi-tenant operating-system sandbox. A Go native module can read files, open sockets, allocate memory, or block a goroutine if the host gives it those powers. The execution plane therefore needs two layers:

1. **Language and capability isolation.** The runtime exposes only approved modules, validates inputs and outputs, applies deadlines, and owns the event loop.
2. **Process and operating-system isolation.** A worker runs with memory, CPU, PID, filesystem, and network constraints, and can be killed if native code does not return.

The first layer prevents normal code from obtaining authority. The second limits damage when a runtime, module, or tenant program is defective or hostile.

### 2.4 Key points

- Capabilities are explicit, typed authority supplied by the host.
- Security-sensitive JavaScript values should carry host-issued identity.
- An interpreter boundary does not replace process isolation.
- The safest default module and permission set is empty.

---

# Part II. The go-go-goja Runtime

## 3. A runtime is an owned execution environment

A `goja.Runtime` is not goroutine-safe. Only one goroutine may use a VM at a time, and values from one runtime cannot be passed directly into another. The repository therefore wraps the VM in an owned execution environment containing an event loop, a scheduler, a CommonJS registry, lifecycle context, runtime values, and cleanup hooks.

<!-- DIAGRAM:runtime_ownership -->

### 3.1 Construction sequence

The runtime factory follows a deliberate order:

```text
validate immutable factory plan
    -> create goja VM
    -> create and start event loop
    -> create runtime owner
    -> create lifetime context and closer registry
    -> create require registry
    -> register selected native modules
    -> enable require and common globals
    -> run runtime initializers
    -> return owned Runtime
```

Each step depends on the previous one. Native modules that create asynchronous work need the event loop and owner before they are registered. Initializers that call `require()` must run after the registry is enabled. Partial construction must close resources in reverse order.

The factory is immutable after `Build()`. That gives every runtime created from the factory the same module composition. Per-runtime state is still fresh: each runtime receives a new VM, event loop, module loaders, and value map.

### 3.2 The runtime owner

The runtime owner exposes two essential operations:

```go
Call(ctx, operation, func(ctx, vm) (value, error))
Post(ctx, operation, func(ctx, vm))
```

`Call` schedules work onto the owning event-loop path and waits for a result. `Post` schedules fire-and-forget work. Both associate the current Go context with the VM call so native modules can inherit cancellation, deadlines, and request metadata.

A native asynchronous function follows this pattern:

```text
on VM owner:
    create JavaScript Promise
    validate input
    start bounded Go work

on worker goroutine:
    perform I/O using invocation context

back on VM owner:
    resolve or reject Promise
```

The Promise must be settled on the owner path. Calling Goja objects from a random goroutine violates the runtime's ownership rule even when the code appears to work in a small test.

### 3.3 Runtime context versus invocation context

Two contexts coexist:

- The **runtime lifetime context** exists for the lifetime of the VM. It is canceled during runtime close and stops runtime-owned background work.
- The **invocation context** belongs to one request, function invocation, or command. It carries a shorter deadline and cancellation signal.

A native module should normally use the current invocation context when one exists, then fall back to the lifetime context for runtime-owned background work. It should not replace both with `context.Background()`.

### 3.4 Closing a runtime

Closing is a protocol, not just `loop.Stop()`:

1. Mark the runtime as closing so no new closers are added.
2. Cancel the lifetime context.
3. Wait briefly for owner work to become idle.
4. Interrupt active JavaScript if it does not become idle.
5. Run module closers in reverse order.
6. remove runtime bridge state;
7. shut down the owner;
8. stop the event loop.

A runtime that was interrupted during an untrusted invocation should be treated as poisoned. Clearing an interrupt does not prove that all JavaScript and module state returned to a valid application boundary. A pool should discard the worker and create a fresh one.

> **Decision: one active invocation per VM worker.**  
> **Problem:** A Goja VM is single-owner, and one long-running handler can block all work scheduled to that VM.  
> **Selected rule:** A worker is acquired exclusively for one invocation; timeouts poison and discard it.  
> **Rejected alternative:** Share one site-wide VM across arbitrary concurrent HTTP requests.  
> **Resulting invariant:** Request concurrency is controlled by pool size, and a stuck invocation cannot permanently monopolize the entire release.

### 3.5 What the platform should add

The runtime layer should expose an explicit invocation primitive that owns the complete timeout protocol:

```go
type InvocationResult struct {
    Value      json.RawMessage
    SafeToReuse bool
    Usage      Usage
}

Invoke(ctx, handlerID, input, capabilityBindings, budget) (InvocationResult, error)
```

The primitive should:

- validate input before acquiring a worker where possible;
- acquire one worker exclusively;
- install invocation-scoped capabilities and secret handles;
- interrupt on timeout;
- bound output and log bytes;
- wait for capability settlement;
- validate the structured result;
- erase invocation state;
- release only a safe worker;
- kill the process if the VM cannot be reclaimed.

### 3.6 Key points

- A runtime is a VM plus ownership, scheduling, context, modules, and cleanup.
- All VM mutation and Promise settlement happens on the owner path.
- Runtime lifetime and request lifetime are separate.
- Interrupted workers should be discarded, not casually reused.

---

## 4. Native modules convert Go authority into JavaScript APIs

A native module defines a JavaScript-visible name and a loader that populates CommonJS exports. Simple modules can be registered by name and loader. Runtime-scoped modules receive richer context: the VM, owner, event loop, host services, configuration, values, and closer registration.

The important design question for a module is not “what functions should JavaScript see?” It is “what authority does this module grant, what state does it own, and how is that authority bounded?”

### 4.1 Module categories

| Category | Examples | Typical lifetime | Security concern |
|---|---|---|---|
| Data-only | path manipulation, YAML encoding, pure builders | Runtime | CPU and output size |
| Bound resource | database, object store, application auth | Runtime or invocation | Tenant/resource isolation |
| Network | guarded fetch, payment client, webhook sender | Invocation | Egress and credentials |
| HTTP host | Express/gojahttp registrar | Runtime | Route ownership and request security |
| Native transport | WebSocket or protocol handler mounted as `http.Handler` | Runtime | Path handoff and lifecycle |
| UI grammar | Widget DSL, safe HTML builder | Runtime | Output validation and injection |
| Unsafe compatibility | unrestricted filesystem, process execution, raw HTML | Runtime | Broad host authority |

A paid module may span more than one category. SQLite includes a JavaScript API, a persistent resource, migration policy, backup policy, and placement constraint. The module descriptor must not hide those operational requirements.

### 4.2 Provider packages

xgoja provider packages can contribute:

- runtime modules;
- command sets;
- JavaScript verb sources;
- help and assets;
- TypeScript declarations;
- host services;
- runtime initializers;
- public configuration sections.

This is a good extension mechanism, but the current name `PackageCapability` describes provider extension hooks rather than application security authority. The hosting platform should rename it to `ProviderExtension` or `ProviderContribution` before adding a commercial permission system.

### 4.3 A hosted module descriptor

The existing module descriptor has a name, default alias, description, configuration schema, TypeScript declarations, and a per-runtime factory. A managed platform needs additional fields:

```go
type HostedModuleVersion struct {
    ID                   string
    Version              string
    RuntimeABI           string
    ProviderModule       string
    ProviderVersion      string
    ProviderChecksum     string
    FactoryDigest        string
    Aliases              []string
    RiskClass            string
    RequiredPermissions  []Permission
    ConfigSchema         json.RawMessage
    BindingSchema        json.RawMessage
    Dependencies         []ModuleRequirement
    Conflicts            []ModuleRequirement
    NetworkPolicy        NetworkPolicy
    MeteringDimensions   []Meter
    PricingFeature       string
    TypeScriptDigest     string
    DocumentationDigest  string
}
```

Aliases such as `database`, `db`, and `sqlite` must resolve to one canonical module identity. Otherwise an alias can become an entitlement or policy bypass.

### 4.4 Module configuration and resource bindings

Static module configuration belongs in the release. Secrets and concrete resource locations belong in bindings. For example:

```yaml
modules:
  sqlite:
    version: 1.3.2
    config:
      maxRowsPerQuery: 1000
      maxResultBytes: 1048576
    binding: primary-database
```

The release can include the digest of the configuration without exposing the database path or encryption key. At worker startup, the platform resolves `primary-database` to a scoped handle.

### 4.5 Key points

- A native module is an authority boundary, not just an import name.
- Provider extensions and runtime security permissions are different concepts.
- Hosted module versions need ABI, provenance, permission, resource, and billing metadata.
- Aliases resolve to canonical identities before policy and entitlement checks.

---

## 5. xgoja is the trusted composition compiler

xgoja turns a declarative plan into a focused Go application containing selected providers, runtime modules, sources, commands, declarations, and assets. This is the correct direction for a hosting platform because it avoids one ambient mega-runtime that exposes every native module.

<!-- DIAGRAM:module_resolution -->

### 5.1 The v2 plan

A v2 specification distinguishes:

- provider packages imported into the generated Go program;
- selected Go-backed runtime modules;
- source sets executed inside Goja;
- command surfaces;
- generated artifacts;
- browser assets built outside Goja.

Runtime modules and command sets are intentionally separate. The `express` module is imported by JavaScript; the HTTP `serve` command set owns a long-running command that creates a runtime, loads a JavaScript verb, and serves its registered routes.

### 5.2 Closed source graphs

xgoja validates static imports before generation. Bare imports must match selected module names or aliases. Nonliteral dynamic imports are rejected because they prevent the build from proving the dependency graph.

This principle is important for agent-generated code. A coding agent should receive immediate build diagnostics when it references a module that is not selected. The platform should not defer that failure to the first production request.

### 5.3 Browser code is a different artifact

Browser applications, web workers, CSS processing, and frontend package installation do not belong in the Goja runtime compiler. They are built by frontend tooling and included as assets. This prevents the server runtime profile from growing Node-compatible behavior solely to build a browser bundle.

The hosting platform can support two frontend modes:

1. a conventional static browser application built separately;
2. server-driven Widget IR rendered by a generic browser client.

### 5.4 Development workspace resolution is not production resolution

xgoja supports local workspace discovery and replacement precedence. This is useful for repository development. A managed build must disable ambient workspace resolution and accept provider packages only from the platform catalog.

A production build should pin:

- Go toolchain;
- `go-go-goja` version;
- provider Go module versions and checksums;
- exact module versions and aliases;
- compiler settings;
- source digest;
- program-contract digest;
- renderer version;
- policy and entitlement snapshot digests.

### 5.5 Runtime plan versus runtime lock

The current runtime plan intentionally omits build-only provider imports and versions. That is sufficient for a generated binary to construct its runtime, but insufficient to identify a commercial reproducible release. The platform needs a **runtime lock** alongside the plan.

```json
{
  "runtimeAbi": "gogo-host/v1",
  "toolchain": "go1.26.x",
  "goGoGoja": "...",
  "sourceDigest": "sha256:...",
  "programDigest": "sha256:...",
  "profileDigest": "sha256:...",
  "policyDigest": "sha256:...",
  "modules": [
    {
      "id": "go-go-goja-http/express",
      "version": "...",
      "alias": "express",
      "providerSum": "h1:...",
      "configDigest": "sha256:..."
    }
  ]
}
```

The lock is included in artifact signing and release audit. Host-owned configuration may substitute approved bindings, but it must not mutate the module set after signing.

> **Decision: the platform generates xgoja specifications.**  
> **Problem:** Allowing tenant-supplied provider imports, Go replacements, build tags, or workspace paths would turn a JavaScript hosting product into arbitrary Go build execution.  
> **Selected rule:** Tenants request catalog modules; the trusted build service generates the provider plan and pins dependencies.  
> **Rejected alternative:** Accept arbitrary `xgoja.yaml` as the production build instruction.  
> **Resulting invariant:** Every native module in an artifact was selected from an operator-controlled catalog.

### 5.6 Key points

- xgoja is a build-time composition system, not merely a CLI wrapper.
- Static graph validation moves dependency failures into build time.
- Browser bundles remain separate assets.
- Production builds use catalog-pinned dependencies and an exact runtime lock.

---

# Part III. The Secure HTTP Application Framework

## 6. gojahttp is the primary web-application substrate

The secure HTTP framework in `go-go-goja` is much broader than a simple Express bridge. `pkg/gojahttp` owns route matching, request identity, body parsing, sessions, static and native handler mounts, response helpers, request logging, planned security enforcement, authorization, resource resolution, CSRF, rate limiting, audit, Promise completion, and both JavaScript and native Go handlers.

The `express` module is the JavaScript authoring surface over that host. It is intentionally Express-style rather than fully Express-compatible. It does not implement arbitrary middleware stacks, `next()`, template engines, npm Express plugins, or every Node API. This is a product decision: a smaller language can compile route intent into a Go-owned security plan.

### 6.1 The layers

```text
JavaScript route declaration
    -> Go-backed staged builder
        -> validated RoutePlan
            -> gojahttp route registry
                -> reusable Enforcer
                    -> JavaScript or native Go handler
```

`gojahttp.Enforcer` can also wrap ordinary `net/http` routes through `PlannedMiddleware`, so the security model is not coupled to JavaScript routing. Native authentication endpoints, OAuth callbacks, WebSocket handlers, and generated routes can share the same plan contract.

### 6.2 Raw routes and planned routes

A raw route registers a callable and receives a request DTO. A planned route registers both a handler and a Go-owned `RoutePlan`.

The production option `RejectRawRoutes` rejects matched raw routes. Static mounts and planned routes remain available. This makes “all application routes are planned” an enforceable host policy rather than a documentation convention.

### 6.3 The route plan

A route plan contains:

```go
type RoutePlan struct {
    Name       string
    Method     string
    Pattern    string
    Security   SecuritySpec
    Resources  []ResourceSpec
    Action     string
    CSRF       CSRFSpec
    Audit      AuditSpec
    RateLimits []RateLimitSpec
}
```

It is data. It can be validated, listed, reviewed, compared between releases, included in a release contract, and used by both JavaScript and native handlers.

### 6.4 A public route is still explicit

```javascript
const express = require("express");
const app = express.app();

app.get("/healthz")
  .name("health")
  .public()
  .rateLimit(express.rateLimit("health.read").perMinute(120).byIP())
  .handle((_ctx, res) => res.json({ ok: true }));
```

Calling `.public()` records an intentional exposure. It is not equivalent to omitting authentication configuration.

### 6.5 A protected resource route

Project Desk updates a project with the following plan:

```javascript
app.patch("/orgs/:orgId/projects/:projectId")
  .name("project.update")
  .auth(express.sessionUser().mfaFresh("10m"))
  .resource(
    express.resource("project")
      .idFromParam("projectId")
      .tenantFromParam("orgId")
      .mustExist()
  )
  .csrf()
  .rateLimit(
    express.rateLimit("project.write")
      .perMinute(30)
      .byActor()
      .byResource("project")
  )
  .allow("project.update")
  .audit("project.updated")
  .handle(async (ctx, res) => {
    const project = ctx.resource("project");
    const updated = await projects.update(project.id, ctx.body);
    res.json({ project: updated });
  });
```

The handler does not parse the session cookie, load the project row for authorization, decide whether the user owns the resource, verify CSRF, or construct a rate-limit key. Those operations run before the handler.

> **Decision: security is a compiled route plan, not handwritten handler middleware.**  
> **Problem:** A handler that manually reads cookies, loads a resource, checks ownership, and verifies CSRF can forget or reorder a check.  
> **Selected rule:** JavaScript declares route intent; Go validates and enforces the plan before invoking JavaScript.  
> **Rejected alternative:** Unrestricted Express middleware and convention-based security helpers.  
> **Resulting invariant:** A protected handler cannot register until the route declares an authentication mode and required action.

### 6.6 Key points

- gojahttp is the core secure HTTP host; Express is its JavaScript grammar.
- Planned routes are data contracts compiled at script load time.
- Production hosts can reject raw routes.
- The same enforcer can protect JavaScript and native Go handlers.

---

## 7. Staged builders make invalid routes unrepresentable

The Express route builder does not expose every method at every stage. Each call returns a new JavaScript object representing the next legal stage.

| Stage | Methods | Meaning |
|---|---|---|
| Needs security | `.name()`, `.public()`, `.auth()` | Method and path exist, but exposure is undecided |
| Needs policy | `.resource()`, `.csrf()`, `.rateLimit()`, `.audit()`, `.allow()` | An actor is required; resource and action policy are being declared |
| Needs handler | `.csrf()`, `.rateLimit()`, `.audit()`, `.handle()` | The route has enough metadata to register |

The builder objects are backed by Go state. The `.auth()` method accepts only objects issued by the Express module. `.resource()` and `.rateLimit()` follow the same rule. When `.handle()` is called, the host validates the complete plan and registers it.

### 7.1 Why registration-time failure matters

Consider an error in which the route path is `/projects/:projectId`, but the resource plan asks for `idFromParam("id")`. The host can detect that mismatch while loading the script. The deployment fails before traffic is switched.

If validation waited until request time, the first real user would discover the error. Worse, behavior might differ between path variants.

### 7.2 Authentication specifications

The framework supports host-issued specifications for several principal and credential shapes:

```javascript
express.user().required()
express.sessionUser().mfaFresh("10m")
express.agent()
express.oauth()
  .issuer("https://issuer.example")
  .resource("project-api")
  .scopes("project.read", "project.write")
express.anyOf(express.sessionUser(), express.agent())
```

The Go plan distinguishes authentication method from principal kind. A user may authenticate through a server-side session. An agent may authenticate with an API token. An OAuth access token is checked against issuer, resource, and scopes. The route can require the exact shape it needs.

OAuth requirements are deliberately strict. The plan requires issuer, resource, scopes, and an audit event. This makes bearer-token endpoints visible during route review.

### 7.3 Resource specifications

A resource plan describes where identifiers come from:

- route parameter;
- query parameter;
- body field;
- literal value.

The JavaScript route does not receive a raw store handle to perform authorization. A host `ResourceResolver` converts the declared identifier into a minimal `ResourceRef`. The `Authorizer` then receives the actor, action, first resource, and all resolved resources.

This supports multi-resource decisions without leaking database records into generic security code.

### 7.4 Rate-limit specifications

Rate-limit plans can combine key parts:

- client IP;
- route;
- actor;
- route or tenant parameter;
- header;
- body field;
- resolved resource.

Policies that depend only on transport values run before authentication. Policies that require actor or resource identity run after authorization. Denied callers do not consume a shared resource bucket.

The host may provide an in-memory limiter for tests or a distributed limiter for production. The route declaration does not change.

### 7.5 Route descriptors and release review

Because the host can list route descriptors, a build can generate a route manifest:

```text
PATCH /orgs/:orgId/projects/:projectId
  name: project.update
  auth: session user, MFA <= 10m
  resource: project from projectId in tenant orgId
  action: project.update
  csrf: required
  rate limit: project.write / actor + project
  audit: project.updated
```

A coding agent's pull request or release proposal should include a diff of this manifest. New public routes, new OAuth scopes, weaker MFA, removed CSRF, or broader rate-limit keys become reviewable authority changes.

### 7.6 Key points

- Builder stages encode the required declaration order.
- Host-issued builder identity prevents forged policy objects.
- Route/resource mismatches fail during application load.
- Route manifests turn HTTP authority into reviewable release data.

---

## 8. The enforcement pipeline runs before JavaScript

The route plan is valuable because one reusable pipeline enforces it. Understanding the order is essential; changing the order can change security semantics.

<!-- DIAGRAM:http_pipeline -->

### 8.1 Step-by-step request trace

For the Project Desk update route, one request follows this sequence.

#### Step 1: normalize network identity

The outer host determines the direct peer and trusted client IP. Forwarding headers are ignored unless the direct peer belongs to a configured trusted proxy range. Malformed forwarded chains from trusted peers fail rather than being partially trusted.

#### Step 2: request logging and request ID

The host ensures a request ID, creates an access-log response writer, and records request completion metadata. This happens outside JavaScript so a handler cannot suppress the basic access record.

#### Step 3: static/native mount dispatch

Static or mounted Go handlers are checked first. Mounts can preserve the original path or strip the prefix. Exclusion prefixes allow a broad mount to defer selected paths to later routes.

#### Step 4: route match and raw-route guard

The registry matches method and path parameters. `HEAD` may fall back to `GET`. When `RejectRawRoutes` is enabled, an unplanned JavaScript route is rejected before its handler runs.

#### Step 5: build the request DTO

The host creates or loads the lightweight request session identifier and parses the body. JSON, URL-encoded forms, multipart forms, and raw bodies are normalized into a request DTO. The current implementation caps the body at 64 MiB and multipart in-memory parsing at 32 MiB; a hosted product should allow smaller per-route or per-plan limits.

#### Step 6: validate the route plan

The plan is normalized again at enforcement. Invalid modes, empty actions, missing parameters, malformed OAuth requirements, and invalid rate-limit keys fail closed.

#### Step 7: pre-authentication rate limits

Policies keyed only by route, IP, header, body field, or route parameters run before expensive authentication. This protects login and token endpoints from unauthenticated floods.

#### Step 8: authenticate

The host `Authenticator` converts a session, API token, access token, or other approved credential into an `AuthResult`. The result contains non-secret metadata: actor, method, principal kind and ID, credential hint, grants, scopes, and verified OAuth assertions. Raw bearer tokens are not projected into handler context.

#### Step 9: check route authentication requirements

The actual authentication method and principal kind must match one of the plan requirements. A valid agent token therefore fails a browser-session-only route even if both credentials belong to authorized identities.

#### Step 10: verify CSRF where required

For unsafe methods, a route with `.csrf()` invokes the host `CSRFProtector`. Session authentication normally requires CSRF; bearer credentials may not, depending on the normalized `AuthResult`. A missing CSRF service is a host misconfiguration and fails closed.

#### Step 11: resolve resources

The host extracts resource and tenant identifiers from the validated request DTO and calls `ResourceResolver`. Missing required resources can become a 404 without exposing whether an unauthorized resource exists.

#### Step 12: check embedded grants

If the credential carries normalized grants, the enforcer checks whether they permit the route action against the resolved resource. This provides a fast credential-scope boundary before the application authorizer.

#### Step 13: authorize

The host `Authorizer` receives the actor, action, first resource, and resource map. It returns an explicit decision. Denial becomes 403; resource lookup can remain 404.

#### Step 14: post-authentication rate limits

Policies keyed by actor or resource run only after authorization succeeds. An unauthorized caller cannot exhaust a shared project budget.

#### Step 15: audit the allowed outcome

When the plan declares an audit event, the host records the allowed security envelope before handler execution.

#### Step 16: invoke JavaScript through the owner

The host constructs `SecureContext`, projects a bounded JavaScript `ctx`, and calls the handler through the runtime owner. The handler receives authenticated facts, not raw policy services.

#### Step 17: finish synchronous or Promise output

A synchronous return is converted through response helpers. If a Promise is returned, the host checks its state on the owner path until fulfilled, rejected, or the request context ends.

#### Step 18: audit completion or failure

The host records completed or failed outcomes with status and reason. In production, client error bodies remain generic.

### 8.2 Status semantics

| Condition | Status |
|---|---:|
| Missing or invalid credentials | 401 |
| Valid actor but denied action or CSRF | 403 |
| Resource hidden or absent | 404 |
| Rate limit exceeded | 429 with `Retry-After` when available |
| Required host service missing | 500 or service-unavailable, depending on failure |
| Handler failure | 500 with generic production body |

This status mapping is part of the application contract. A platform should test it as black-box behavior, not only unit-test individual interfaces.

### 8.3 Audit reliability

The current MVP treats audit sink errors as best-effort in several paths. That is acceptable for local examples but not for evidence-grade release, identity, payment, or administrative actions. The managed platform should write security mutations and their audit/outbox record in one database transaction, or fail the mutation.

Route request audit has a different availability tradeoff. A high-volume read route may not be allowed to fail solely because an external analytics sink is down. The platform should classify audit events:

- **transactional security events:** account, permission, release, secret, token, payment, and destructive data changes;
- **request evidence:** allowed/denied/completed/failed route observations delivered through a durable buffer;
- **metrics:** bounded aggregates that may tolerate sampling.

### 8.4 Key points

- Enforcement order is part of the security design.
- JavaScript runs only after identity, CSRF, resources, grants, authorization, and relevant budgets pass.
- Authentication metadata is non-secret and credential-type aware.
- Audit durability requirements depend on event class, but ignored errors are not sufficient for critical mutations.

---

## 9. Host-owned identity supports browsers, agents, and OAuth resources

The HTTP framework deliberately separates identity proof from application authorization. An identity provider proves who authenticated. The application decides what that principal may do to a project, document, report, or tenant.

### 9.1 Server-side browser sessions

`sessionauth.Manager` stores opaque sessions on the server. The browser receives only a cookie identifier. A session includes:

- application user ID;
- external identity subject and selected claims;
- tenant memberships;
- CSRF token;
- MFA timestamp;
- idle and absolute expiry;
- revocation state.

The secure default cookie uses the `__Host-` prefix, `HttpOnly`, `Secure`, path `/`, and `SameSite=Lax`. Insecure HTTP must be enabled explicitly for local demonstrations. The manager validates expiry and revocation, refreshes idle expiry, projects an application actor, verifies CSRF with constant-time comparison, and enforces route-declared MFA freshness.

The lightweight request session ID in the base `gojahttp` host is not authentication. It is useful for anonymous correlation or application state keys. Authenticated browser routes should use the server-side session manager.

### 9.2 OIDC and Keycloak

The Keycloak adapter uses standard OIDC Authorization Code with PKCE:

```text
browser -> Go login endpoint
    -> identity provider
    -> Go callback verifies state, code, ID token, nonce
    -> normalize external subject into application user
    -> create server-side application session
    -> browser receives only application session cookie
```

Provider access and refresh tokens remain server-side. The application stores its own users, memberships, resource ownership, and fine-grained policy. Identity-provider groups can inform policy, but they should not replace application domain state.

### 9.3 Agents and API tokens

Programmatic identities are separate durable principals. An agent has an ID, kind, tenant, and grants. API-token issuance returns the raw token once; later list and revoke operations return only redacted metadata such as token ID, prefix, credential hint, scopes, expiry, and revocation state.

An agent route declares its requirement:

```javascript
app.get("/agent/reports/:reportId")
  .auth(express.agent())
  .allow("report.read")
  .audit("agent.report.read")
  .handle((ctx, res) => {
    res.json({
      reportId: ctx.params.reportId,
      principal: ctx.auth.principalId,
      credential: ctx.auth.credentialHint
    });
  });
```

The handler never parses the bearer token. The authenticator validates it, resolves its agent, normalizes grants, and provides non-secret context.

### 9.4 OAuth resource-server routes

A route can require an external access token with exact issuer, resource, and scopes. This is useful when Project Desk exposes an API to another service using Tiny-IDP or an external issuer.

```javascript
app.get("/api/projects/:projectId")
  .auth(
    express.oauth()
      .issuer("https://id.example")
      .resource("project-desk-api")
      .scopes("project.read")
  )
  .resource(express.resource("project").idFromParam("projectId").mustExist())
  .allow("project.read")
  .audit("project.api.read")
  .handle((ctx, res) => res.json({ project: ctx.resource("project") }));
```

The route plan requires audit for OAuth requirements. This is a deliberate review signal for externally accessible bearer-token APIs.

### 9.5 Trusted proxies

Client IP is security data because rate limits and audits use it. The host trusts `X-Forwarded-For` only when the direct TCP peer is in a configured proxy CIDR. It bounds the header length and hop count, parses every address, and chooses the first untrusted address from the right side of the chain.

A platform deployment must configure this once at the outer server boundary. Individual JavaScript handlers should never interpret forwarding headers.

### 9.6 Tiny-IDP in the platform

There are two populations:

- **platform users:** customers, team members, billing administrators, approvers, and coding agents;
- **application users:** end users of a hosted customer application.

They should not share administrative authority, issuer keys, or subject namespaces by accident. The platform can offer:

1. a managed shared application realm with strict logical isolation;
2. a dedicated managed issuer;
3. an external OIDC issuer supplied by the customer.

<!-- DIAGRAM:identity_flow -->

### 9.7 Key points

- Identity proof and application authorization are separate.
- Browser tokens stay server-side; the browser receives an opaque app session.
- Agents are durable principals with separately managed credentials and grants.
- Forwarded client identity is trusted only through explicit proxy policy.
- Platform identity and hosted-application identity are separate populations.

---

## 10. The HTTP framework includes operations, not just routing

A secure application host also needs bounded transport, outbound calls, native integrations, reload behavior, and operational state.

### 10.1 Request and response DTOs

Planned handlers receive a context with:

```typescript
type PlannedContext = {
  request: Request;
  auth: AuthMetadata;
  actor: Actor | null;
  body: unknown;
  params: Record<string, string>;
  resources: Record<string, ResourceRef>;
  resource(name: string): ResourceRef | null;
  action: string;
  routeName: string;
};
```

Response helpers include status, headers, content type, JSON, text, HTML rendering, redirects, and end. The host owns whether development errors are exposed.

A managed platform should add per-route limits for request bytes, response bytes, header count, multipart files, and execution time. The current global body limits are useful defaults but too broad for all applications.

### 10.2 Static and mounted handlers

`app.static` serves a host directory, while `app.staticFromAssetsModule` serves from a read-only embedded filesystem module. The hosted safe profile should prefer embedded or object-store-backed assets; arbitrary host directories should be privileged.

`app.mount` accepts a Go-backed object carrying a hidden `http.Handler`. The mount uses prefix matching and preserves the original path unless `stripPrefix` is requested. This allows native modules to own WebSocket, streaming, OAuth, or protocol-specific handlers without reimplementing them in JavaScript.

The route ownership must remain explicit. A paid module that mounts `/payments/webhook` should declare that mount in its module descriptor and release manifest so collisions are caught before activation.

### 10.3 Native planned handlers and middleware

`Host.RegisterPlannedHTTP` and `PlannedMiddleware` apply the same route-plan enforcer to native Go handlers. This means a host-owned endpoint can use the same actor, resource, action, CSRF, rate-limit, and audit contract as a JavaScript handler.

That is valuable for:

- OAuth login and callback routes;
- binary downloads;
- WebSocket upgrades;
- payment webhooks;
- health and readiness endpoints;
- high-throughput endpoints that should not enter Goja.

### 10.4 Guarded outbound fetch

Outbound HTTP is a native capability. The xgoja host provider offers a guarded `fetch` module with:

- an explicit `allow: true` gate;
- origin allow-lists;
- default and per-request timeouts;
- maximum buffered response size;
- policy over environment and file credential sources;
- Go-owned bearer credential builders;
- a small low-level API and a fluent client.

A hosted platform should make the allowed origins part of the release permission diff. Direct arbitrary egress remains disabled. Payment and identity integrations should usually receive narrower domain-specific modules rather than generic fetch.

### 10.5 Blue/green hot reload

The xgoja HTTP serve path includes a hot-reload manager. It:

1. creates a fresh candidate host;
2. creates and loads a fresh runtime;
3. invokes the selected JavaScript verb to register routes;
4. optionally performs an HTTP smoke request;
5. atomically swaps the active snapshot;
6. closes the retired runtime after a grace period;
7. exposes bounded status.

This local mechanism expresses the right release principle: construct and validate a candidate before changing traffic. The managed platform should generalize it from an in-memory snapshot pointer to an immutable database traffic generation and distributed router reconciliation.

### 10.6 HTTP server lifecycle

The generated serve command owns a real `net/http.Server`, sets `ReadHeaderTimeout`, reacts to process signals or context cancellation, and performs graceful shutdown with a bounded timeout. It can also mount native authentication handlers before the JavaScript application fallback and wrap the entire mux in trusted request-identity middleware.

### 10.7 How go-go-host should converge

The reviewed `go-go-host` main branch contains a smaller `internal/sitejs/web` host. It has useful route registration, response helpers, sessions, and supervisor integration, but it does not contain the full planned route, auth, rate-limit, proxy, programmatic credential, guarded fetch, and hot-reload framework described above.

The target platform should migrate `go-go-host` execution to `gojahttp` rather than maintain a parallel HTTP implementation. `go-go-host` should own projects, releases, routing, quotas, and orchestration; `gojahttp` should own the application HTTP security contract.

### 10.8 Key points

- Secure web hosting includes request limits, response semantics, egress, native mounts, and lifecycle.
- Native and JavaScript routes can share one plan enforcer.
- Guarded fetch turns network access into reviewable host policy.
- Hot reload provides a local candidate-then-swap model for production release design.
- go-go-host should converge on gojahttp instead of extending its smaller web fork.

---

# Part IV. Application Programs and User Interfaces

## 11. A serializable program contract makes agent output reviewable

Traditional startup scripts register callbacks directly into a VM. That is flexible, but it gives the control plane little structured information about the application. The Tiny-IDP scripting branch introduces a stronger pattern: JavaScript produces a serializable `Program` contract while callbacks remain indexed by stable IDs inside each runtime.

The generic platform should extract that pattern into a neutral package.

### 11.1 Program shape

```go
type Program struct {
    APIVersion   string
    Name         string
    Routes       map[string]RouteSpec
    Functions    map[string]HandlerSpec
    Pages        map[string]PageSpec
    Actions      map[string]HandlerSpec
    Schedules    map[string]ScheduleSpec
    Schemas      map[string]Schema
    Capabilities map[string]CapabilityRequirement
    Resources    map[string]ResourceRequirement
    Tests        []ProgramTest
}
```

Callbacks are not serialized. A handler specification records the stable callback ID and its contract:

```go
type HandlerSpec struct {
    ID                   string
    Kind                 HandlerKind
    InputSchema          string
    OutputSchema         string
    AllowedOutcomes      []OutcomeKind
    RequiredCapabilities []CapabilityRequirement
    AllowedEffects       []EffectKind
    AuthPolicy           AuthPolicy
    Idempotency          IdempotencyPolicy
    Budget               InvocationBudget
    SourceLocation       SourceLocation
}
```

### 11.2 Compilation

The program compiler runs source in an isolated collector runtime that exposes only the application DSL. It rejects ambient module loading, applies source and time limits, captures callback IDs, copies the serializable contract, validates it in Go, runs declared tests with fake capabilities, and calculates fingerprints.

```text
source
  -> goja compile
  -> isolated collector runtime
  -> serializable Program + callback registry
  -> deterministic validation
  -> declarative tests
  -> source/program/callback/schema fingerprints
  -> immutable application artifact
```

At worker startup, the source is loaded again into a fresh runtime. The worker verifies that the callback registry and contract fingerprints match the artifact. A source file that registers different callbacks based on ambient state fails activation.

### 11.3 Budgets

A useful invocation budget includes:

- wall-clock timeout;
- maximum capability calls;
- maximum concurrent capability calls;
- input and output bytes;
- log bytes;
- database rows and result bytes;
- network requests and bytes;
- response body size;
- maximum effects;
- continuation payload size.

The budget is part of the handler contract and release review. A coding agent that raises a route timeout from 100 ms to 30 seconds is changing resource authority.

### 11.4 Outcomes and effects

Handlers should return structured outcomes rather than use exceptions for expected policy results. A generic vocabulary may include:

- `complete`: successful terminal value;
- `respond`: HTTP or function response;
- `page`: validated Widget page;
- `continue`: immediate transition to another handler;
- `present`: durable browser continuation;
- `challenge`: start or continue a native proof;
- `commit`: request a validated native effect plan;
- `deny`: valid negative decision;
- `error`: infrastructure or invalid program behavior.

Native effects are separate from the decision to request them. JavaScript can propose `payment_session_create`; Go validates product, amount, idempotency, entitlement, and credential policy before calling the provider.

### 11.5 Express compatibility and the contract compiler

The existing planned Express DSL already compiles route security into Go data. The program compiler should absorb those route descriptors rather than replace the HTTP framework. A practical migration path is:

1. load an Express-style application in a collector runtime;
2. capture planned route descriptors and callback IDs;
3. reject raw routes in the managed profile;
4. merge route plans with schemas, budgets, module requirements, pages, actions, and tests;
5. emit one application `Program`.

This preserves the extensive gojahttp framework while making a release statically inspectable.

### 11.6 Key points

- A program contract separates VM callbacks from serializable release metadata.
- Compilation verifies stable callback and schema fingerprints.
- Budgets and effects are reviewable handler authority.
- The generic compiler should incorporate planned Express routes rather than invent a second HTTP framework.

---

## 12. Widget DSL makes web UI a typed protocol

Widget DSL separates author intent from renderer implementation. JavaScript or Go constructs semantic widgets, the host normalizes them into a typed intermediate representation, and a React application renders that IR through a versioned component registry.

<!-- DIAGRAM:widget_pipeline -->

### 12.1 Why IR instead of arbitrary HTML

Arbitrary HTML gives server code control over tags, attributes, script injection, form actions, and styling. A typed Widget IR gives the platform a stable boundary that can be:

- serialized and content-limited;
- validated independently of React;
- diffed between releases;
- rendered by multiple clients;
- tested with golden IR;
- reviewed in Storybook and browser automation;
- constrained to approved components and actions.

A page may have this conceptual wire shape:

```typescript
type WidgetPage = {
  schemaVersion: string;
  rendererVersion: string;
  id: string;
  title: string;
  shell?: ShellSpec;
  root: WidgetNode;
};

type WidgetNode =
  | { kind: "text"; text: string }
  | { kind: "element"; tag: SafeTag; attrs?: SafeAttrs; children?: WidgetNode[] }
  | { kind: "component"; type: ComponentID; props?: object; children?: WidgetNode[] };
```

The managed profile should prefer components and a very small safe element set. Raw HTML, arbitrary script/style tags, event attributes, and `javascript:` URLs should require an explicitly privileged compatibility module, if they are offered at all.

### 12.2 Actions are data

A server-driven interface cannot serialize JavaScript closures into the browser. Actions are defunctionalized into data:

```json
{
  "type": "server",
  "handler": "start-checkout",
  "input": {
    "productId": { "from": "row.id" }
  }
}
```

The browser dispatches the action to a named application handler. The host then applies authentication, CSRF, input validation, idempotency, rate limits, effect policy, and audit using the same program contract.

### 12.3 Static browser applications remain supported

Widget IR is not a requirement for every application. A customer may build a conventional React, Vue, Svelte, or plain browser application. That bundle is a separate immutable artifact and calls planned HTTP APIs.

The two modes can coexist:

- static assets for complex client-side interaction;
- Widget pages for rapid agent-generated dashboards, forms, tables, and administrative surfaces.

### 12.4 Renderer compatibility

Each release should pin:

- Widget schema version;
- renderer package version;
- component-registry digest;
- design-system or preset version.

A component registry change can alter behavior without changing application source. It is therefore part of the release identity.

### 12.5 Validation layers

Widget UI requires three different test classes:

1. **Semantic tests:** the application returns the expected widget intent and action contracts.
2. **IR tests:** canonical serialized output matches a golden or schema predicate.
3. **Visual/browser tests:** the target renderer displays the page and interactions correctly.

The Widget DSL project found that IR goldens alone do not detect every integration mismatch. Browser tests are part of the contract.

> **Decision: Widget IR is the default agent-generated UI surface.**  
> **Problem:** Arbitrary HTML or arbitrary React generation expands the security and compatibility surface of every release.  
> **Selected rule:** Agents author semantic UI and actions; the platform owns normalization, component policy, styling, and browser dispatch.  
> **Rejected alternative:** Expose unrestricted raw HTML as the standard server-rendered UI API.  
> **Resulting invariant:** Every interactive server-driven action resolves to a named, policy-enforced application handler.

### 12.6 Key points

- Widget DSL is an intent language over a typed UI protocol.
- Renderer and registry versions are release inputs.
- Actions are data that call named program handlers.
- Semantic, IR, and visual tests cover different failure classes.

---

# Part V. The Control Plane and Release System

## 13. go-go-host supplies the control-plane skeleton

The current go-go-host repository already models users, organizations, memberships, sites, domains, quotas, site capabilities, deployments, agents, keys, grants, nonces, deploy runs, audit, and runtime status. Its layering—HTTP adapters, control services, store wrappers, deployment validation, and runtime supervision—is a useful starting point.

The production platform should retain these concepts while replacing the in-process execution path and refining the release model.

### 13.1 What is worth preserving

- Authorization and product invariants belong in control services, not only handlers or dashboards.
- Store wrappers hide SQL implementation details.
- Upload and activation are separate operations.
- Deployment records and artifact paths are immutable.
- A candidate runtime is built and smoke-tested before a traffic swap.
- Machine agents use separate credentials and grants from human users.
- Path, channel, and activation permissions can be scoped per agent.
- Operational mutations emit audit events.

### 13.2 Where the current execution path diverges

As reviewed, go-go-host currently:

- builds one in-process runtime per site;
- always opens a per-site SQLite database;
- registers database aliases independently of the effective requested capability set;
- loads every `.js` file in lexical traversal order rather than one compiled program contract;
- uses an in-memory supervisor map as live routing state;
- applies an HTTP response timeout that does not itself guarantee JavaScript interruption;
- contains a smaller HTTP host rather than the full gojahttp planned framework;
- performs some audit writes best-effort.

These are reasonable beta implementation choices. They are not the final multi-tenant boundary.

### 13.3 Capability enforcement must be end-to-end

The bundle validator currently computes requested and effective capabilities. The runtime constructor must receive exactly that resolved set. No later code may replace it with broad defaults.

The platform sequence should be:

```text
manifest requirements
  ∩ account entitlement
  ∩ environment policy
  ∩ operator module policy
  = effective release permissions
```

The effective set is canonicalized, persisted, included in the release digest, and used directly by worker construction.

### 13.4 Control-plane source of truth

The database should hold desired state. Routers and workers reconcile it. In-memory maps are caches, not authorities.

For example, environment `production` may point to traffic generation 42:

```json
{
  "generation": 42,
  "allocations": [
    { "release": "rel_new", "weight": 100 }
  ],
  "previousGeneration": 41
}
```

A router observes generation 42 and updates its cache. If it restarts, it reconstructs state from the database or a durable stream.

### 13.5 Key points

- go-go-host is a useful control-plane seed.
- Its current in-process runtime is a beta execution mechanism, not the final tenant boundary.
- Effective capabilities must survive unchanged from validation to worker construction.
- Persistent desired state, not an in-memory supervisor, is the authority for traffic.

---

## 14. A release is more precise than a deployment

One mutable deployment record cannot accurately represent source, build, artifact, environment configuration, rollout, and live traffic. The platform should model them separately.

<!-- DIAGRAM:release_lifecycle -->

### 14.1 Domain objects

| Object | Meaning |
|---|---|
| Source revision | Exact uploaded archive or Git commit and source digest |
| Build | One attempt to compile and validate a source revision under a runtime profile |
| Artifact | Signed content-addressed output, runtime lock, SBOM, provenance, and test evidence |
| Release | Artifact plus environment bindings, effective permissions, policy, and entitlement snapshot |
| Deployment | One attempt to start or promote a release |
| Worker revision | A concrete process, sandbox, or pool serving one release |
| Traffic generation | Immutable allocation of traffic to releases |
| Rollback | A new traffic generation pointing to an explicitly selected prior release |

### 14.2 Candidate-to-live sequence

```text
create release
    -> start candidate worker revision
    -> wait for readiness
    -> run smoke and synthetic checks
    -> optional canary traffic
    -> compare-and-swap expected traffic generation
    -> write new generation + audit + outbox transactionally
    -> routers adopt generation
    -> drain previous worker revision
    -> retire after in-flight count reaches zero or deadline
```

The compare-and-swap prevents two coding agents from silently promoting different releases over each other.

### 14.3 Blue/green and canary

The local xgoja hot-reload manager proves the core blue/green rule: build and smoke a candidate before swapping an atomic pointer. The distributed platform adds persistent generations and weighted allocations.

A canary generation may be:

```json
{
  "generation": 43,
  "allocations": [
    { "release": "rel_old", "weight": 95 },
    { "release": "rel_new", "weight": 5 }
  ]
}
```

Sticky allocation may be based on a stable request key so one user does not alternate between incompatible releases during a session.

### 14.4 Rollback and databases

Code rollback and database rollback are different operations. A prior release may no longer run against the current schema. The release contract should declare schema compatibility and migration phases.

Prefer expand/contract migrations:

1. expand schema so old and new releases can run;
2. deploy new release;
3. backfill data;
4. move traffic;
5. remove old code;
6. contract schema in a later release.

A destructive restore is a privileged resource operation, not an automatic side effect of switching code.

### 14.5 Artifact evidence

An artifact should contain or reference:

- source digest;
- program contract and callback fingerprint;
- runtime lock;
- module and provider checksums;
- SBOM;
- compiler and toolchain identity;
- static graph diagnostics;
- unit and declared program-test results;
- route manifest;
- authority diff;
- Widget IR schema/renderer pins;
- signature and provenance.

### 14.6 Key points

- Source, build, artifact, release, deployment, worker, and traffic are separate objects.
- Promotion is a persistent compare-and-swap, not an in-memory side effect.
- Rollback selects an exact release and must respect database compatibility.
- Build evidence travels with the artifact.

---

## 15. Coding agents are principals, not trusted administrators

Coding agents will create most source revisions and release proposals. Their automation is a product feature, but an agent signature does not make a release safe. It identifies the requester and protects the request from tampering.

### 15.1 Agent identity

An agent has:

- durable principal ID;
- organization and optional project/environment scope;
- active public keys or API tokens;
- allowed actions;
- allowed source paths or channels;
- expiry and revocation state;
- separate authority to build, propose, canary, or promote.

Human credentials must not be reused by machines.

### 15.2 Canonical signed release request

A promotion request should cover:

```text
organization, project, environment
source revision digest
build/artifact digest
release digest
expected current traffic generation
module lock digest
permission and policy digest
binding/config digest
migration plan digest
rollout policy
idempotency key
timestamp and nonce
```

The control plane recomputes every policy decision. The signature proves who asked for the operation.

### 15.3 Authority diff

Every release proposal should include a machine-generated diff such as:

```text
+ route POST /checkout/start: public -> session user
+ module payments@1.2.0
+ permission egress api.stripe.com:443
+ secret binding stripe-production
+ effect payment_session_create
~ project.update MFA freshness 30m -> 10m
~ database schema 12 -> 13
- module legacy-mailer@0.8.1
```

Some changes can be auto-approved under policy. Others require human review.

Require review for:

- a new native module or major version;
- new network origin;
- new secret or production resource binding;
- identity, payment, or destructive data effects;
- removal of CSRF, audit, MFA, or authorization requirements;
- new public route;
- unsafe HTML or filesystem/process access;
- increased memory, timeout, body, output, or concurrency limits;
- destructive schema migration;
- domain or certificate changes.

### 15.4 Idempotency and replay

Agent requests use nonce and timestamp replay protection, but operational APIs also need idempotency keys. Repeating a request after a network timeout should return the original build or release result rather than create a second release.

### 15.5 Key points

- Agents are durable machine principals with limited grants.
- Signed requests are authenticated proposals, not policy overrides.
- Authority diffs make generated changes reviewable.
- Nonces prevent replay; idempotency keys prevent duplicate operations.

---

# Part VI. Identity Workflows and Native Effects

## 16. Tiny-IDP remains the identity kernel

Tiny-IDP's strict engine demonstrates a valuable division of responsibility. Go owns OAuth/OIDC validation, HTTP and browser security, cookies, password processing, cryptography, signing keys, replay-sensitive state, atomic effects, sessions, token issuance, and audit. JavaScript receives bounded typed values and returns structured decisions.

This boundary should be preserved even when identity workflows become scriptable.

### 16.1 Why identity JavaScript is different

An ordinary application handler may return a page or update a project. An identity handler participates in credential establishment and token issuance. It must not receive:

- raw passwords or password hashes;
- signing keys;
- refresh tokens;
- authorization codes;
- cookies;
- Fosite objects;
- SQL transactions;
- unconstrained networking.

JavaScript may decide how signup branches, how a virtual identity is mapped, or whether an invitation is acceptable. Go validates evidence and applies the effects.

### 16.2 Explicit browser continuations

A browser form or email challenge spans multiple HTTP requests. A pending Promise inside one Goja heap is not durable across process restart, worker replacement, source upgrade, or another node.

The identity workflow therefore returns a presentation or challenge with a named resume handler. Go stores a continuation containing:

- workflow and handler IDs;
- program and schema version;
- original validated protocol request digest;
- client and redirect binding;
- browser and session binding;
- bounded carry data;
- opaque secret/evidence references;
- expiry and one-time consumption state.

The next request is validated by Go and invokes the resume handler as a fresh bounded call.

### 16.3 Remote workflow execution for tenant code

The Tiny-IDP design explicitly warns that its in-process scripting sandbox is not containment for hostile tenant code. The hosting platform should therefore execute customer-authored identity workflows in the isolated worker plane.

```text
Tiny-IDP validates protocol request
    -> sends bounded workflow event to pinned release
    -> receives structured outcome
    -> validates outcome and evidence references
    -> applies native identity effects transactionally
    -> stores continuation or issues protocol artifact
```

If the workflow service is unavailable or returns invalid output, Tiny-IDP fails closed.

### 16.4 Managed application identity modes

A hosted project can choose:

- managed shared realm with tenant isolation;
- dedicated managed Tiny-IDP instance and keys;
- external OIDC issuer.

Application code receives verified claims and a stable application actor. It does not receive the identity store.

A narrow `users.v1` capability may support invitation, disable, role assignment, public profile lookup, and reset/login-link requests. Those operations remain host-authorized and audited.

### 16.5 Key points

- Go remains the identity and cryptographic authority.
- JavaScript decides bounded workflow behavior and requests effects.
- Browser-spanning waits use durable continuations, not suspended VM heaps.
- Untrusted identity workflow code runs outside the IdP process.

---

# Part VII. Paid Modules, Resources, and Billing

## 17. Subscriptions authorize release construction

A customer may subscribe to native modules such as SQLite, payments, advanced identity, queues, or premium UI components. Billing state should determine which releases may be created or continue after a defined grace policy. It should not be queried from Stripe during every request.

### 17.1 Internal entitlement ledger

Stripe or another billing provider emits asynchronous events. The control plane verifies, deduplicates, stores, and projects them into an internal entitlement table.

```text
verified billing webhook
  -> durable billing event
  -> entitlement projection
  -> entitlement-changed outbox event
  -> release/reconciliation policy
```

A release captures an immutable entitlement snapshot. This answers the historical question: why was this module allowed when the release was created?

### 17.2 Release resolution

For each requested module, the build/control plane:

1. resolves a canonical catalog version;
2. checks account entitlement;
3. checks project/environment policy;
4. validates dependencies and conflicts;
5. resolves resource bindings;
6. derives effective permissions;
7. calculates quotas and metering dimensions;
8. generates the xgoja profile and runtime lock;
9. signs the artifact and release.

A downgrade policy can immediately block new releases, allow an existing release through a grace period, then suspend it. Security revocation may bypass grace.

### 17.3 SQLite is a module and a resource

The SQLite JavaScript API is one concern. The persistent database file, storage allocation, migration state, backup schedule, encryption, and worker placement are another.

A SQLite resource should define:

- one active writer placement or lease policy;
- filesystem/volume ownership;
- soft and hard byte limits;
- connection and statement budgets;
- backup, verify, and restore operations;
- migration generation;
- compatible release range;
- observability and corruption checks.

Do not promise arbitrary horizontal scale over one local SQLite file. For scalable profiles, offer managed Postgres or a remote database service as a different resource product.

### 17.4 Payments as a narrow module

Project Desk should not receive a Stripe secret and unrestricted fetch. A `payments.v1` capability can expose:

- create checkout session;
- create customer portal session;
- read a bounded subscription summary;
- cancel or schedule cancellation under policy;
- create a refund request with explicit authority;
- retrieve configured products and prices;
- consume host-verified webhook evidence.

The host owns:

- provider credentials;
- product/price/currency allow-lists;
- redirect-domain policy;
- idempotency keys;
- webhook signature verification using raw body;
- event deduplication;
- conversion to native evidence;
- irreversible effect execution and audit.

JavaScript owns product behavior: which approved checkout to start, what page to show, and how the application responds to verified subscription events.

### 17.5 Metering

Module subscription and usage metering are separate. A module descriptor may declare dimensions such as:

- invocation count;
- database bytes;
- query CPU or rows;
- egress requests and bytes;
- payment operations;
- identity active users;
- object storage bytes;
- queue messages.

Workers emit bounded usage events identified by release, project, environment, module, and invocation. The control plane aggregates them. A worker never edits the billing ledger directly.

### 17.6 Key points

- Billing events feed an internal entitlement ledger.
- Entitlements are checked during release resolution, not every request.
- A release records the entitlement snapshot used to authorize it.
- SQLite and payments combine a JS module with host-owned resources and effects.

---

# Part VIII. The Production Execution Plane

## 18. Each tenant release runs in an isolated worker boundary

The final execution plane should not run unrelated customer programs inside the control-plane daemon. Each release runs in a dedicated process or sandbox group with a bounded worker pool.

### 18.1 Worker contents

A worker receives:

- signed artifact and runtime lock;
- exact selected module binary or image;
- release program contract;
- non-secret configuration;
- short-lived resource binding credentials or broker handles;
- network policy;
- quotas and handler budgets;
- workload identity;
- log and usage destinations.

It does not receive:

- control-plane database credentials;
- billing-provider administrative credentials;
- secrets for modules not selected;
- host filesystem paths outside declared mounts;
- unrestricted egress;
- other tenant data.

### 18.2 Process controls

A first production sandbox should provide:

- read-only root filesystem;
- unprivileged UID;
- separate process namespace;
- memory and CPU limits;
- PID and file-size limits;
- no host socket mounts;
- no network by default;
- egress through a policy gateway;
- ephemeral writable storage;
- explicit persistent resource mounts;
- hard process kill as final timeout enforcement.

Language-level interruption remains useful for fast recovery and diagnostics. Process-level kill is the final safety mechanism when native code fails to cooperate.

### 18.3 Worker pools

A pool belongs to one release. It never mixes runtimes from different tenants or release digests.

```text
request
  -> route to release
  -> acquire exclusive VM worker
  -> install invocation bindings
  -> invoke handler with budget
  -> validate result and usage
  -> release safe worker or discard unsafe worker
```

Cold starts can be hidden by maintaining a minimum warm pool. Pool size is a release quota and concurrency limit.

### 18.4 Resource brokers

A worker should call narrow brokers rather than hold broad credentials:

- database broker or scoped connection;
- object-store client restricted to a prefix;
- payment broker restricted to an account/product set;
- identity workflow interface;
- queue publisher restricted to a topic;
- guarded egress proxy.

The broker receives workload identity and release metadata, checks policy again, applies quotas, emits audit/usage, and performs the operation.

### 18.5 Router behavior

The edge/router:

- maps host and path to project environment;
- reads the active traffic generation;
- selects a release allocation;
- attaches request and trace IDs;
- forwards to a ready worker revision;
- enforces coarse body/header/time limits;
- retries only idempotent operations under explicit policy;
- records routing status and latency.

Application authorization remains inside the gojahttp host because it depends on route plans and resources. The router does not duplicate application policy.

> **Decision: process isolation surrounds the Goja capability boundary.**  
> **Problem:** A native module or interpreter defect can escape language-level assumptions and block or access process resources.  
> **Selected rule:** Tenant releases run in resource-constrained worker processes or sandboxes with no ambient control-plane authority.  
> **Rejected alternative:** One long-lived daemon hosting every customer VM in one address space.  
> **Resulting invariant:** The platform can terminate one release without terminating or exposing another customer's release or the control plane.

### 18.6 Key points

- One release pool is one isolation and policy unit.
- Workers receive signed artifacts and scoped bindings, not control-plane authority.
- Capability brokers centralize secrets, quotas, audit, and usage.
- Process kill backs up VM interruption.

---

# Part IX. End-to-End Example

## 19. Project Desk from source to request

This chapter assembles the pieces into one concrete flow.

### 19.1 Application request

The customer selects:

- secure HTTP/Express;
- server-side application authentication;
- SQLite;
- Widget DSL;
- payments;
- guarded fetch to one internal API.

An illustrative application manifest is:

```yaml
schema: gogo/app/v1
name: project-desk
runtime:
  modules:
    - id: http/express
    - id: auth/application
    - id: data/sqlite
      binding: primary-db
    - id: ui/widget-dsl
      version: "3"
    - id: payments/checkout
      binding: stripe-production
    - id: host/fetch
      config:
        allowedOrigins:
          - https://reports.internal.example
sources:
  server: ./server
  webAssets: ./web/dist
entrypoint: ./server/app.ts
checks:
  smokePath: /healthz
```

The customer does not provide Go imports or workspace replacements. The platform translates catalog IDs into xgoja providers and exact module versions.

### 19.2 Program source

A simplified application declares routes and actions:

```javascript
const express = require("express");
const widget = require("widget.dsl");
const db = require("db");
const payments = require("payments");

const app = express.app();

app.get("/healthz")
  .public()
  .handle((_ctx, res) => res.json({ ok: true }));

app.get("/orgs/:orgId/projects/:projectId")
  .auth(express.sessionUser())
  .resource(
    express.resource("project")
      .idFromParam("projectId")
      .tenantFromParam("orgId")
      .mustExist()
  )
  .allow("project.read")
  .audit("project.read")
  .handle((ctx, res) => {
    const project = ctx.resource("project");
    const rows = db.query(
      "select id, title, status from tasks where project_id = ? limit 100",
      project.id
    );
    return widget.page(project.claims.title, p =>
      p.section("Tasks", s => s.view(widget.data.table(rows)))
    );
  });

app.post("/checkout/start")
  .auth(express.sessionUser().mfaFresh("10m"))
  .csrf()
  .rateLimit(express.rateLimit("checkout.start").perMinute(5).byActor())
  .allow("billing.checkout.create")
  .audit("billing.checkout.created")
  .handle(async (ctx, res) => {
    const session = await payments.createCheckout({
      product: "project-desk-pro",
      customer: ctx.actor.id,
      idempotencyKey: ctx.request.headers["idempotency-key"]
    });
    res.json({ redirect: session.url });
  });
```

In the managed compiler, these route descriptors are combined with handler schemas, budgets, effects, module requirements, and declared tests into the program contract.

### 19.3 Build

The build service performs:

```text
scan archive with compressed/uncompressed/file limits
verify paths and duplicate canonical names
compile TypeScript
validate static imports against selected modules
execute collector runtime
validate program, routes, schemas, budgets, effects
run declared tests with fake capabilities
build or retrieve runtime-profile image
build static browser assets separately
produce runtime lock, route manifest, SBOM, provenance
sign content-addressed artifact
```

### 19.4 Release resolution

The control plane verifies:

- the account is entitled to SQLite, Widget DSL, and payments;
- the environment allows payment effects;
- `primary-db` belongs to the project environment;
- `stripe-production` is an approved production binding;
- the fetch origin is allowed by platform policy;
- quotas fit the subscription;
- the agent may propose this release;
- any authority changes have required approval.

The resulting release is immutable.

### 19.5 Promotion

A candidate worker starts in an isolated sandbox, verifies the signature and lock, opens scoped resources, loads a fresh pool, checks callback fingerprints, registers planned routes, and serves an internal smoke request.

The control plane then compare-and-swaps the production traffic generation. Routers adopt the new generation. The previous pool drains.

### 19.6 One authenticated request

A browser requests the project page:

```text
edge selects release
  -> worker gojahttp host matches route
  -> server-side session authenticates user
  -> project resource resolves in tenant
  -> grants and authorizer permit project.read
  -> audit allowed
  -> exclusive VM worker invokes handler
  -> bounded SQLite query returns rows
  -> Widget DSL returns validated page IR
  -> response sent
  -> audit completed + usage event
```

### 19.7 One automated request

A CI agent calls a report route with its API token. The route requires `express.agent()`, so a browser session cannot accidentally satisfy it. The guarded fetch client reads its credential from an allowed secret source, calls the exact origin, and receives a bounded response.

### 19.8 Failure cases

| Failure | Detection point | Result |
|---|---|---|
| Source imports unselected module | Static graph validation | Build rejected |
| Public route omits `.public()` | Staged builder / plan validation | Runtime load rejected |
| Resource references missing path param | Plan validation | Build or candidate rejected |
| Account lacks payments entitlement | Release resolution | Release not created |
| Candidate health returns 500 | Smoke check | Current traffic unchanged |
| Handler exceeds timeout | Invocation manager | VM interrupted, worker discarded; process killed if necessary |
| Audit/outbox transaction fails during promotion | Control-plane transaction | Traffic generation unchanged |
| Payment webhook signature invalid | Native payment endpoint | Request rejected before JavaScript |
| Prior release incompatible with DB schema | Rollback policy | Rollback blocked or requires restore plan |

### 19.9 Key points

- Every stage checks a different class of invariant.
- JavaScript remains the business-logic language, while Go owns authority and lifecycle.
- The release contains enough evidence to reproduce and review what runs.
- Candidate failure never requires disturbing the active release.

---

# Part X. Implementation Plan and Intern Guide

## 20. Repository changes in dependency order

### 20.1 go-go-goja

1. Add a neutral application-program package extracted from Tiny-IDP patterns.
2. Add an invocation manager with interrupt, poison, output, log, and capability budgets.
3. Add hosted security/resource descriptors to provider modules.
4. Rename provider `PackageCapability` to avoid collision with runtime permissions.
5. Freeze provider and module registries after build.
6. Produce a canonical route manifest from gojahttp planned routes.
7. Add per-route request/response limits to `RoutePlan`.
8. Make critical audit behavior configurable by durability class.
9. Harden database result, transaction, SQL logging, and migration authority.
10. Keep guarded fetch disabled unless explicit policy is supplied.

### 20.2 xgoja

1. Add runtime-lock generation with exact provider and module provenance.
2. Add a hosted build mode that disables workspace auto-resolution and arbitrary imports.
3. Let the platform generate specs from catalog requirements.
4. Include program, route, renderer, and policy digests in artifacts.
5. Emit agent-facing TypeScript declarations and module documentation from the resolved lock.
6. Keep browser builds separate and content-addressed.

### 20.3 go-go-host

1. Persist the effective permission/module set and pass it unchanged to workers.
2. Replace `DefaultCapabilities()` on hosted paths with deny-by-default resolution.
3. Migrate application HTTP execution to gojahttp.
4. Split source revisions, builds, artifacts, releases, traffic generations, and workers.
5. Move bundles and artifacts to content-addressed object storage.
6. Replace in-process site runtimes with an execution-plane worker API.
7. Make promotion a database compare-and-swap with transactional outbox and audit.
8. Add graceful drain and exact rollback target selection.
9. Add module catalog, entitlements, resources, bindings, secrets, usage, and policy decisions.
10. Rewrite archive ingestion as bounded streaming validation with duplicate-path rejection.

### 20.4 tiny-idp

1. Keep strict protocol validation and native effects in Tiny-IDP.
2. Extract generic program, schema, budget, artifact, pool, and capability patterns.
3. Repair pool shutdown and failed-replacement capacity behavior.
4. Add a remote workflow executor for untrusted hosted application workflows.
5. Add managed realm lifecycle, export, suspension, key rotation, and deletion APIs.
6. Add a horizontally scalable store before advertising shared multi-node availability.

### 20.5 Widget DSL

1. Publish a standalone versioned IR and Go validator.
2. Pin renderer and registry digests in releases.
3. Map server actions to named program handlers.
4. Enforce node, depth, text, property, collection, and total-byte limits.
5. Separate privileged raw HTML from the safe profile.
6. Maintain semantic, golden IR, Storybook, accessibility, and browser test suites.

### 20.6 Key points

- Changes start at runtime contracts and build identity before distributed orchestration.
- gojahttp is reused, not reimplemented.
- Control-plane schema changes follow the release model.
- Identity and UI retain separate native security boundaries.

---

## 21. Delivery stages

### Stage 0: make the current prototype honest

Before serving unrelated customers:

- enforce the effective capability set end-to-end;
- conditionally register SQLite and all other native modules;
- force development errors off in production;
- add hard invocation interruption and worker discard;
- bound archive extraction and reject duplicates;
- disable unsafe HTML primitives in the safe profile;
- use gojahttp planned routes with raw-route rejection;
- make activation, host ownership, drain, and audit consistent;
- repair Tiny-IDP pool close behavior.

### Stage 1: single-node hosted alpha

Build the target boundaries even on one machine:

- Postgres control plane;
- content-addressed source and artifact store;
- separate build process;
- separate worker process;
- generic application compiler;
- planned HTTP routes, functions, actions, and Widget pages;
- core, SQLite, auth, and Widget profiles;
- signed artifacts and exact release locks;
- explicit promotion and rollback;
- invocation records, logs, metrics, and usage.

### Stage 2: subscriptions, payments, and application identity

Add:

- module catalog and entitlement ledger;
- billing webhook ingestion and reconciliation;
- payments resource and effects;
- managed application-user realms and external OIDC;
- remote identity workflow execution;
- resource provisioning and backup;
- subscription-aware release resolution.

### Stage 3: distributed execution

Add:

- multiple routers and worker nodes;
- sandbox scheduling and worker leases;
- weighted canary traffic;
- distributed rate limits;
- guarded egress gateway;
- central logs and traces;
- scalable database profiles;
- automated reconciliation and dead-worker recovery.

### Stage 4: ecosystem

Add:

- third-party provider certification;
- signed module publishing;
- compatibility and deprecation policies;
- reproducible module-profile cache;
- enterprise identity and policy adapters;
- richer Widget component packs;
- regional placement and data-residency controls.

---

## 22. An intern's code-reading path

Read in this order. The sequence follows runtime authority from the inside out.

### 22.1 Runtime ownership

1. `go-go-goja/pkg/engine/factory.go`
2. `go-go-goja/pkg/engine/runtime.go`
3. `go-go-goja/pkg/runtimeowner/types.go`
4. `go-go-goja/pkg/runtimeowner/runner.go`
5. `go-go-goja/pkg/runtimebridge/runtimebridge.go`

Questions to answer:

- Which goroutine owns the VM?
- Where is current call context installed?
- What happens when runtime construction fails halfway?
- What resources can a module register for cleanup?

### 22.2 Modules and xgoja

1. `go-go-goja/modules/common.go`
2. `go-go-goja/pkg/engine/module_specs.go`
3. `go-go-goja/pkg/xgoja/providerapi/`
4. `go-go-goja/pkg/xgoja/app/`
5. `go-go-goja/cmd/xgoja/doc/17-xgoja-v2-reference.md`

Questions:

- Which module decisions happen at build time and which at runtime?
- What information is absent from `RuntimePlan`?
- How does a provider contribute declarations and host services?

### 22.3 Secure HTTP

1. `go-go-goja/pkg/gojahttp/auth_plan.go`
2. `go-go-goja/modules/express/auth_builders.go`
3. `go-go-goja/pkg/gojahttp/enforcer.go`
4. `go-go-goja/pkg/gojahttp/planned_dispatch.go`
5. `go-go-goja/pkg/gojahttp/host.go`
6. `go-go-goja/pkg/gojahttp/ratelimit.go`
7. `go-go-goja/pkg/gojahttp/auth/sessionauth/`
8. `go-go-goja/pkg/xgoja/hostauth/`

Questions:

- Which checks happen before JavaScript?
- Why are pre-auth and post-auth rate limits separate?
- What values are intentionally omitted from `AuthResult`?
- Why can `RejectRawRoutes` be enforced by the host?

### 22.4 Serving and reload

1. `go-go-goja/pkg/xgoja/providers/http/http.go`
2. `go-go-goja/pkg/xgoja/providers/http/serve.go`
3. `go-go-goja/pkg/xgoja/hotreload/manager.go`

Questions:

- Who owns the listener?
- How are native auth handlers mounted before the app fallback?
- When is the active runtime swapped?
- What happens to a candidate that fails smoke?

### 22.5 Control plane

1. `go-go-host/docs/architecture/data-model.md`
2. `go-go-host/internal/control/deployments.go`
3. `go-go-host/internal/deploy/bundle.go`
4. `go-go-host/internal/runtime/runtime.go`
5. `go-go-host/internal/runtime/supervisor.go`
6. agent, grant, nonce, and audit services

Questions:

- Which records are immutable?
- Where can in-memory and persistent state diverge?
- Does the effective capability set reach runtime construction unchanged?
- What happens when audit persistence fails?

### 22.6 Program contracts and identity

1. `tiny-idp/pkg/idpprogram/`
2. `tiny-idp/pkg/idpscript/`
3. Tiny-IDP lambda-first workflow design
4. `tiny-idp/pkg/embeddedidp/`
5. strict engine security profile

Questions:

- Which values cross the Go/JavaScript boundary as JSON?
- How are callback registries fingerprinted?
- When is a worker considered unsafe to reuse?
- Why are browser continuations durable records?

### 22.7 UI

1. Widget DSL knowledge-base note
2. Widget IR types and validators
3. Widget DSL fluent builders
4. React registry and adapters
5. Storybook and browser fixtures

Questions:

- Which layer owns styling?
- Which actions are serializable?
- How is renderer compatibility pinned?
- What can golden IR tests miss?

---

## 23. Practical exercises

### Exercise 1: trace a protected request

Choose one planned route. Write down:

1. route plan fields;
2. authentication requirement;
3. CSRF decision;
4. resource value sources;
5. authorizer input;
6. pre- and post-auth rate-limit keys;
7. JavaScript context fields;
8. audit outcomes.

Then write a test for 401, 403, 404, 429, success, and handler failure.

### Exercise 2: make a route invalid on purpose

Create a route whose resource references a path parameter that does not exist. Confirm that the application fails during load. Explain why registration-time failure is safer than request-time failure.

### Exercise 3: add an invocation budget

Add a handler that loops forever. Implement a deadline that interrupts the VM, marks the worker unsafe, and replaces it. Verify that the next invocation uses a fresh runtime.

### Exercise 4: produce a route authority diff

Compare two route manifests. Detect:

- newly public route;
- removed CSRF;
- broader OAuth scopes;
- changed action;
- changed MFA freshness;
- increased rate limit.

Classify which changes require review.

### Exercise 5: model SQLite correctly

Draw separate records for module version, entitlement, permission, quota, resource, and binding. Show how a release refers to each. Do not use one `enabled` field.

### Exercise 6: test a Widget page at three layers

For one page:

1. assert semantic intent;
2. compare canonical IR;
3. render it in a browser fixture and exercise an action.

Record one failure that only the browser test detects.

### Exercise 7: analyze a release race

Two agents both read traffic generation 41 and propose different releases. Show how compare-and-swap permits one generation 42 and rejects the other proposal for reconciliation.

### Exercise 8: design a payment effect

Define the JavaScript request shape, Go validation, idempotency key, product allow-list, secret binding, provider call, audit event, and returned non-secret result for `payment_session_create`.

---

# Part XI. Review Checklists

## 24. Runtime review checklist

- Every VM is accessed through its owner.
- Promise resolution returns to the owner path.
- Runtime and invocation contexts are not confused.
- Timeouts interrupt JavaScript and poison unsafe workers.
- Native work observes cancellation.
- Output, logs, and capability calls are bounded.
- Runtime close is idempotent and retry-safe.
- A partial startup closes every acquired resource.

## 25. Module review checklist

- The module has a canonical ID and version.
- Required permissions are explicit.
- Resource bindings are typed.
- Secrets never enter serializable release metadata.
- Aliases cannot bypass policy or entitlement.
- Configuration rejects unknown fields.
- TypeScript declarations match runtime behavior.
- Network and filesystem authority are deny-by-default.
- Metering and quota dimensions are defined.
- Closers are registered for runtime-owned resources.

## 26. HTTP review checklist

- Production enables `RejectRawRoutes`.
- Every route declares `.public()` or an exact auth requirement.
- Protected routes declare an action.
- Resource identifiers and tenant boundaries are host-resolved.
- Unsafe browser/session routes declare CSRF.
- OAuth routes declare exact issuer, resource, scopes, and audit.
- Pre-auth limits protect expensive authentication.
- Post-auth limits use actor/resource keys where needed.
- Proxy forwarding headers are trusted only from configured peers.
- Body, response, and execution limits fit the route.
- Handler context contains no raw credentials.
- Native handlers use planned middleware where policy applies.
- Production errors are generic.

## 27. Release review checklist

- Source revision is immutable and content-addressed.
- Archive extraction is streaming and bounded.
- Static imports match selected modules.
- Program and callback fingerprints match.
- Route and authority diffs are attached.
- Module versions and provider checksums are locked.
- Entitlement and policy snapshots are recorded.
- Secrets appear only as binding references.
- Candidate worker passes readiness and smoke.
- Promotion uses expected-generation compare-and-swap.
- Audit and outbox are transactional.
- Previous workers drain before close.
- Rollback target and schema compatibility are explicit.

## 28. Identity and payment review checklist

- Protocol verification remains in native Go.
- JavaScript receives no password, token, cookie, key, or raw store handle.
- Browser tokens remain server-side.
- Sessions have idle, absolute, revocation, CSRF, and MFA semantics.
- Application authorization is separate from identity-provider groups.
- Webhook signatures are checked over the exact raw body.
- Events are deduplicated.
- Effects use idempotency keys.
- Payment products, prices, currencies, and redirects are allow-listed.
- Sensitive mutations produce transactional audit evidence.

---

# Part XII. Glossary

## 29. Terms

**Actor**  
A non-secret application representation of an authenticated principal.

**Agent**  
A durable machine principal such as a coding agent, CI bot, or integration.

**Artifact**  
A content-addressed built output plus lock, provenance, test evidence, and signature.

**AuthResult**  
The host-normalized authentication result containing actor, method, principal identity, grants, scopes, and verified OAuth assertions without raw credentials.

**Binding**  
A release-time connection to a concrete resource or secret-backed service.

**Capability**  
A narrow host-supplied operation made available to JavaScript.

**Collector runtime**  
An isolated runtime used during compilation to capture a serializable program contract and callback IDs.

**Control plane**  
The trusted service that owns accounts, projects, policy, releases, entitlements, audit, and desired state.

**Effect**  
A host-applied operation with externally visible or durable consequences.

**Entitlement**  
A commercial right to use a product feature or module.

**Execution plane**  
The workers, routers, brokers, and sandboxes that serve immutable releases.

**Grant**  
A normalized permission attached to a principal or credential, often scoped to a tenant or resource.

**Handler budget**  
Limits on time, calls, bytes, logs, effects, and other invocation resources.

**Host service**  
A Go-owned service object provided to runtime modules during setup.

**Invocation**  
One exclusive bounded execution of a named handler.

**Module alias**  
The JavaScript import name for a canonical runtime module.

**Planned route**  
An HTTP route with a validated Go-owned `RoutePlan` describing exposure, identity, resources, action, CSRF, rate limits, and audit.

**Program contract**  
A serializable description of handlers, routes, pages, schemas, capabilities, effects, budgets, tests, and continuation edges.

**Provider**  
A Go package that contributes xgoja modules, commands, sources, declarations, or host extensions.

**Quota**  
A numerical limit applied by control, build, or execution services.

**Release**  
An immutable artifact combined with environment bindings, effective policy, and entitlement snapshot.

**ResourceRef**  
A minimal host-resolved resource identity projected into authorization and handler context.

**RoutePlan**  
The validated data contract enforced before a JavaScript or native handler runs.

**Runtime lock**  
The exact reproducibility and provenance record for a runtime profile.

**Traffic generation**  
An immutable routing decision assigning traffic to one or more releases.

**Widget IR**  
A typed serializable user-interface representation rendered by a versioned target.

**Worker revision**  
A concrete process, sandbox, or pool serving one immutable release.

---

# Appendix A. Source and Evidence Map

This book is derived from the following reviewed code and documentation. Paths are relative to their repositories. The map is intended to help an intern verify statements against working code.

## A.1 go-go-goja runtime and xgoja

- `pkg/engine/factory.go`
- `pkg/engine/runtime.go`
- `pkg/runtimeowner/types.go`
- `pkg/runtimeowner/runner.go`
- `pkg/runtimebridge/runtimebridge.go`
- `modules/common.go`
- `pkg/engine/module_specs.go`
- `pkg/xgoja/providerapi/`
- `pkg/xgoja/app/`
- `cmd/xgoja/doc/17-xgoja-v2-reference.md`
- `cmd/xgoja/internal/generate/templates/runtime_package.go.tmpl`
- `Research/KB/Projects/go-go-goja.md` in go-go-parc

## A.2 HTTP and authentication

- `pkg/gojahttp/host.go`
- `pkg/gojahttp/auth_plan.go`
- `pkg/gojahttp/enforcer.go`
- `pkg/gojahttp/planned_dispatch.go`
- `pkg/gojahttp/middleware.go`
- `pkg/gojahttp/ratelimit.go`
- `pkg/gojahttp/request_identity.go`
- `pkg/gojahttp/body.go`
- `pkg/gojahttp/session.go`
- `modules/express/auth_builders.go`
- `pkg/doc/18-express-module.md`
- `pkg/doc/29-express-auth-user-guide.md`
- `pkg/doc/33-auth-module-guide.md`
- `pkg/gojahttp/auth/sessionauth/`
- `pkg/gojahttp/auth/keycloakauth/`
- `pkg/gojahttp/auth/programauth/`
- `pkg/xgoja/hostauth/`
- `pkg/xgoja/providers/http/http.go`
- `pkg/xgoja/providers/http/serve.go`
- `pkg/xgoja/hotreload/manager.go`
- `cmd/xgoja/doc/25-programmatic-auth-javascript-apis.md`
- `cmd/xgoja/doc/27-guarded-fetch-client-api.md`

## A.3 go-go-host

- `README.md`
- `docs/contributing/runtime-and-deployment-guidelines.md`
- `docs/architecture/data-model.md`
- `internal/deploy/bundle.go`
- `internal/control/deployments.go`
- `internal/control/agents.go`
- `internal/runtime/runtime.go`
- `internal/runtime/supervisor.go`
- `internal/sitejs/web/`

## A.4 Tiny-IDP

Reviewed primarily on `task/prod-tiny-idp`:

- `pkg/idpprogram/`
- `pkg/idpscript/`
- `internal/gojamodules/tinyidp/`
- `pkg/idpworkflow/`
- `pkg/idpcontinuation/`
- `pkg/embeddedidp/`
- `docs/security-profile.md`
- `docs/embedding-foundations.md`
- `ttmp/2026/07/10/TINYIDP-GOJA-001--go-go-goja-identity-microkernel-scripting-layer/design-doc/03-lambda-first-tiny-idp-javascript-api-with-explicit-browser-continuations.md`

## A.5 Widget DSL

- `Research/KB/Projects/widget-dsl.md` in go-go-parc
- `Projects/2026/07/08/ARTICLE - Widget DSL v3 - From Split Modules to a Real Host Migration.md`
- Widget DSL/IR packages and React renderer registries in the associated frontend repositories
- Storybook, golden IR, and browser fixtures associated with the Widget DSL project

---

# Appendix B. Final Design Principles

1. **Go owns authority; JavaScript owns bounded application behavior.**
2. **A runtime is owned, single-threaded, contextual, and disposable.**
3. **Native modules are selected explicitly and carry security, resource, and billing metadata.**
4. **xgoja compiles focused runtime profiles from an operator-controlled catalog.**
5. **gojahttp planned routes are the standard secure web surface.**
6. **Authentication, resource resolution, authorization, CSRF, rate limits, and audit run before JavaScript.**
7. **The application program is serializable, fingerprinted, schema-validated, budgeted, and tested.**
8. **Widget IR is the default server-driven UI protocol; raw HTML is privileged.**
9. **A release includes source, program, module lock, renderer, bindings, policy, entitlement snapshot, and evidence.**
10. **Traffic changes through immutable generations and compare-and-swap.**
11. **Agents propose signed changes but do not bypass policy.**
12. **Identity and payment protocols remain native effects with narrow scriptable decisions.**
13. **Entitlements authorize releases; workers emit usage but do not control billing.**
14. **Tenant releases run in isolated processes or sandboxes with no ambient control-plane authority.**
15. **Candidate construction and smoke precede every live swap.**

The system is coherent when these principles reinforce one another. A planned route is useful because the program compiler can inspect it. The program compiler is useful because xgoja can build an exact runtime profile. The runtime profile is trustworthy because modules come from a catalog. The release is reproducible because it has a lock and provenance. Promotion is safe because a candidate is tested before an immutable traffic generation changes. Runtime failure is contained because the worker is bounded and disposable. Identity, payments, and storage remain host-owned because the program receives only narrow capabilities.

That is the architecture an intern should preserve when changing the code. Package names may move. These boundaries should remain visible.
EOF
wc -w /mnt/data/textbook_work/master.md
wc -l /mnt/data/textbook_work/master.md
```

## Turn 140 - assistant (thinking)

- Message ID: `a4c68d7c-57e5-435e-bb6b-72416a69edec`

<details><summary>Thinking</summary>

**Wrote guide and processed documents for textbook formatting**


</details>

## Turn 141 - assistant (tool call)

- Message ID: `93b1fac2-f52b-4fd7-9b7f-a4a9423adb82`
- Model: `gpt-5-6-pro`

```unknown
bash -lc rm -rf /mnt/data/textbook_work/render1 && mkdir -p /mnt/data/textbook_work/render1
python /home/oai/skills/docx/render_docx.py /mnt/data/secure_goja_hosting_platform_textbook.docx --output_dir /mnt/data/textbook_work/render1 --emit_pdf --verbose
```

## Turn 142 - assistant (tool call)

- Message ID: `1ffd0b62-2402-47fe-b916-8796a9346b66`
- Model: `gpt-5-6-pro`

```unknown
bash -lc grep -n "List Number\|ordered\|re.match.*\\d" -n /mnt/data/build_hosted_goja_textbook.py | head -40 && sed -n '1,260p' /mnt/data/build_hosted_goja_textbook.py | tail -120
```

## Turn 143 - assistant (thinking)

- Message ID: `ce7f9f43-3753-4e15-9519-59d1392c2019`

<details><summary>Thinking</summary>

**Inspected and patched ordered list parser and text formatting**


</details>

## Turn 144 - assistant (tool call)

- Message ID: `9f2882ed-d057-4d94-92d3-151c8c068060`
- Model: `gpt-5-6-pro`

```unknown
bash -lc rm -rf /mnt/data/hosted_goja_render_v2 /mnt/data/hosted_goja_pairs_v2 && mkdir -p /mnt/data/hosted_goja_render_v2 && python /home/oai/skills/docx/render_docx.py /mnt/data/hosted_goja_platform_textbook.docx --output_dir /mnt/data/hosted_goja_render_v2 --emit_pdf --verbose
```

## Turn 145 - assistant (thinking)

- Message ID: `dff11fe1-9155-4257-a784-0ca34d6e36c8`

<details><summary>Thinking</summary>

**Cleaned directories, analyzed images, and inspected document audits**


</details>

## Turn 146 - assistant

- Message ID: `f5f3597b-2609-429f-b18c-d918918cc64c`
- Model: `gpt-5-6-pro`

The full manuscript is assembled with 34 chapters, exercises, glossary, decision records, and source map; I’m rebuilding the DOCX and verifying its rendered layout after workspace loss.

## Turn 147 - assistant (tool call)

- Message ID: `9e6033d0-de56-4f08-8ca8-8e1c76f9433a`
- Model: `gpt-5-6-pro`

```json
{"paths":["GitHub"],"query":"fetch_file"}
```

## Turn 148 - assistant (recap)

- Message ID: `8b3b6016-045a-5ef4-aebb-8446e038b959`

> _Worked for 47m 19s_

## Turn 149 - assistant

- Message ID: `984acad5-a04c-4751-9c3c-c3b2b4c7b7b8`
- Model: `gpt-5-6-pro`

# Hosted Goja Platform Textbook

The completed document is a 69-page, approximately 14,900-word intern-facing textbook. It starts with the execution model and builds toward the secure HTTP framework, release architecture, module subscriptions, identity, isolated workers, durable workflows, current implementation risks, and an incremental engineering plan. The structure develops the reasons behind each boundary before presenting implementation details, with concrete code, pseudocode, tables, traces, decision records, and exercises. fileciteturn105file0L10-L15

The HTTP framework is treated as a central existing capability, not as something the platform still needs to invent. The relevant chapters cover:

- Go-owned listener, server, mux, startup, native-handler mounting, signal handling, graceful shutdown, and hot reload.
- The Express-style JavaScript declaration API.
- Staged planned-route builders and the compiled `RoutePlan`.
- The ordered `Enforcer` pipeline for pre-auth rate limits, authentication, principal requirements, CSRF, resource resolution, grant checks, authorization, post-auth limits, audit, and handler invocation.
- Browser OIDC sessions, app-local authorization, capability tokens, programmatic agents, mounts, static assets, and guarded outbound HTTP. fileciteturn113file0L20-L43 fileciteturn113file0L62-L83 fileciteturn120file0L63-L178 fileciteturn110file0L28-L65

The Word edition was rendered and inspected across all 69 pages. The accessibility audit found no high- or medium-severity issues.

[Download the Word textbook](sandbox:/mnt/data/hosted_goja_platform_textbook.docx)

[Download the Markdown source](sandbox:/mnt/data/hosted_goja_platform_textbook.md)

## Turn 150 - assistant (thinking)

- Message ID: `0cb16848-9338-435d-9118-c56ce1ea8ce6`

<details><summary>Thinking</summary>

**Rendered document, analyzed images, and inspected diagrams and metadata**


</details>

## Turn 151 - assistant (tool call)

- Message ID: `1cb86909-9374-44cf-bd6d-d01a56b353d9`
- Model: `gpt-5-6-pro`

```json
{"paths":["GitHub"],"query":"search"}
```

## Turn 152 - assistant (tool call)

- Message ID: `146782ee-3a9c-4295-9bff-4cb27ec83e63`
- Model: `gpt-5-6-pro`

```json
{"paths":["GitHub"],"query":"fetch_file"}
```

## Turn 153 - assistant (recap)

- Message ID: `9e5fb9ed-412a-545f-934d-6d2768f178e3`

> _Worked for 65m 25s_

## Turn 154 - assistant

- Message ID: `ae9967c8-4e75-4a06-9158-2c7e219e9da6`
- Model: `gpt-5-6-pro`

## Completed

The final manuscript is a **69-page, approximately 15,600-word textbook** for an intern joining the project. It develops the architecture from first principles, explains why each boundary exists, grounds the discussion in concrete code and request traces, records rejected alternatives, and includes diagrams, exercises, review checklists, a glossary, and a source/evidence map. This follows the supplied foundation-first authoring method: explain the reason for a design before its implementation, use concrete examples, and prefer precise diagrams over analogies. fileciteturn105file0L10-L30

The document gives the HTTP framework a complete treatment rather than presenting it as a small Express adapter. Part III covers `gojahttp` as the Go-owned application host; Express as the JavaScript declaration grammar; planned `RoutePlan` objects; staged route builders; authentication; server-side sessions and OIDC; resource resolution; credential grants; authorization; CSRF; pre- and post-authentication rate limits; audit; native planned handlers; guarded outbound HTTP; trusted proxies; server lifecycle; and blue/green reload. This matches the repository’s design in which JavaScript receives narrow access to host-owned services only after the planned route pipeline has authenticated and authorized the request. fileciteturn138file0L23-L68 Native Go handlers can also use the same planned enforcement pipeline through `PlannedMiddleware`, so the security model is not limited to JavaScript callbacks. fileciteturn129file0L10-L50

All 69 DOCX pages were rendered and visually inspected. The accessibility audit returned no findings.

- [Download the formatted Word textbook](sandbox:/mnt/data/secure_goja_hosting_platform_textbook.docx)
- [Download the Markdown source](sandbox:/mnt/data/secure_goja_hosting_platform_textbook.md)

## Turn 155 - user

- Message ID: `c93ace6b-9684-46a9-82ee-2492fef7adba`

I want this to basically allow js app to be generated and deployed in a. Professional manner, while being very efficient for an llm to be created, which really allows just in time app creation, from both personal apps (my own email client / todo list / etc…) to friends share app (doodle for the next barbecue, etc…) to full professional crm and logistic backends and booking website and ecommerce stores to be built , by providing say big modules like product search behind an elegant and simple js api. Because we can hide complex operational semantics behind simple denotatiknal semantics, llms have a tremendously easier job generating real apps. 

I want to pitch this business idea to raise some seed capital, explore different business models and pitch ideas and make a big ass document that also explains / helps me tackle this, I’m squarely a technical founder and would also need to find a business person. I have a tremendously innovative and effective designer founder who has really impressive demos (and I have a very solid technical first version of th system, tackling a lot of the really complex parts)

## Turn 156 - assistant (thinking)

- Message ID: `d4ea396b-c091-49a6-8465-b7d5352486f5`
- Model: `gpt-5-6-pro`

<details><summary>Thinking</summary>

**Creating business pitch document**

The user seems to want a comprehensive document, like a business plan or model, possibly also involving a technical or designer co-founder. This requires market research and structuring into formats such as DOCX or Markdown.

**Created business pitch document**


</details>

## Turn 157 - assistant

- Message ID: `18775ca3-949d-49c7-b4b6-a126f87b0e1e`
- Model: `gpt-5-6-pro`

I’ll develop an investor-grade founder dossier covering the product thesis, market, business models, GTM, fundraising, risks, milestones, pitch variants, cofounder search, and proven-versus-unproven claims.

## Turn 158 - assistant (tool call)

- Message ID: `4e1ae1bd-5454-4042-9f7b-59a124d49571`
- Model: `gpt-5-6-pro`

```unknown
bash -lc cat /home/oai/skills/docx/SKILL.md && printf '\n---USER SKILL---\n' && sed -n '1,220p' /mnt/data/SKILL\(4\).md
```

## Turn 159 - assistant (thinking)

- Message ID: `392ecc21-efb3-4fe2-9210-3f97da957b07`

<details><summary>Thinking</summary>

**Inspected SKILL files for business document creation**


</details>

## Turn 160 - assistant (thinking)

- Message ID: `b2c2b7d5-ac75-49a2-bc94-9722c620a9a4`
- Model: `gpt-5-6-pro`

<details><summary>Thinking</summary>

**Planning business document**

The user wants a comprehensive business exploration document to pitch a seed idea. I'll research market trends, business models, competitors, and gather current data to create an 80+ page document.

**Planned a business document**


</details>

## Turn 161 - assistant (thinking)

- Message ID: `615590e0-7a2a-4278-b022-343e079a1572`
- Model: `gpt-5-6-pro`

<details><summary>Thinking</summary>

**Planning business document**

I'll focus on creating a comprehensive business document, incorporating aspects like founder roles, product vision, user stories, business models, and typical equity splits. I'll be careful with details like hiring specs and narrow the scope.

**Planned business document**


</details>

## Turn 162 - assistant (thinking)

- Message ID: `173bec74-c51c-4368-8bec-c7478f3d0929`
- Model: `gpt-5-6-pro`

<details><summary>Thinking</summary>

**Evaluating funding strategies**

I’m weighing the company’s funding options and considering market benchmarks for seed rounds and valuations. I’ll suggest a raise plan based on team needs and growth rather than over-prescribing specific amounts.

**Evaluated funding strategies**


</details>

## Turn 163 - assistant (tool call)

- Message ID: `8dd3428b-3150-4717-b5b4-942ef9f6e7d0`
- Model: `gpt-5-6-pro`

```json
{"search_query":[{"q":"2026 AI app builder market Replit Agent Lovable Bolt v0 funding ARR latest July 2026"},{"q":"site:replit.com Agent build deploy apps official"},{"q":"site:lovable.dev official product build full stack apps AI"},{"q":"site:v0.dev official v0 full stack apps"}],"response_length":"long"}
```

## Turn 164 - assistant (thinking)

- Message ID: `45605dac-542c-47e9-af58-dcc99b508da1`

<details><summary>Thinking</summary>

**Searched for AI app builders, docs, and related sites**


</details>

## Turn 165 - assistant (tool call)

- Message ID: `72a66013-7d30-4c92-9552-5e983045ed10`
- Model: `gpt-5-6-pro`

```json
{"search_query":[{"q":"site:carta.com data seed round size valuation 2025 2026 startup fundraising"},{"q":"site:carta.com SAFE seed dilution 2025 startup fundraising data"},{"q":"site:ycombinator.com safe financing documents official post-money SAFE"},{"q":"site:openvc.app startup seed round 2026 benchmarks"}],"response_length":"long"}
```

## Turn 166 - assistant (thinking)

- Message ID: `c2e1a4da-bb5c-42c5-ada4-0b5d464f7eb6`

<details><summary>Thinking</summary>

**Searched seed funding benchmarks, pricing models, and resources**


</details>

## Turn 167 - assistant (tool call)

- Message ID: `e87a0ccb-361f-47bd-b481-8e3030909510`
- Model: `gpt-5-6-pro`

```unknown
bash -lc ls -lh /mnt/data/secure_goja_hosting_platform_textbook.* /mnt/data/hosted_goja_platform_textbook.* 2>/dev/null || true && wc -l -w /mnt/data/secure_goja_hosting_platform_textbook.md 2>/dev/null || true && sed -n '1,180p' /mnt/data/secure_goja_hosting_platform_textbook.md 2>/dev/null
```

## Turn 168 - assistant (thinking)

- Message ID: `a37a4de2-067e-486d-8a50-4285b5f846b8`

<details><summary>Thinking</summary>

**Read existing technical document**


</details>

## Turn 169 - assistant (tool call)

- Message ID: `2f40b2af-61ae-4b3f-be1b-5bad0f4f328b`
- Model: `gpt-5-6-pro`

```json
{"search_query":[{"q":"site:replit.com pricing Replit Core Pro 2026 official"},{"q":"site:lovable.dev pricing official 2026"},{"q":"site:vercel.com v0 pricing official 2026"},{"q":"site:base44.com pricing official"}],"response_length":"long"}
```

## Turn 170 - assistant

- Message ID: `111f61e3-8606-4c13-8221-d489f9ac5753`
- Model: `gpt-5-6-pro`

The positioning is sharpening beyond prompt-to-code: a production application substrate whose high-level modules compress operational complexity, enabling agents to compose reliable, safely released applications.

## Turn 171 - assistant (thinking)

- Message ID: `916709eb-6b3d-4284-b50c-0e11d95d14fe`

<details><summary>Thinking</summary>

**Searched for pricing, competitive analysis, and entrepreneurship resources**


</details>

## Turn 172 - assistant (tool call)

- Message ID: `a6b2164a-fb89-4565-b4bf-db96a86c5edc`
- Model: `gpt-5-6-pro`

```unknown
bash -lc sed -n '1,260p' /home/oai/skills/docx/tasks/create_edit.md && printf '\n---VERIFY---\n' && sed -n '1,220p' /home/oai/skills/docx/tasks/verify_render.md
```

## Turn 173 - assistant (thinking)

- Message ID: `9032de0c-8fce-4073-bb37-4ac8ebd22fb1`

<details><summary>Thinking</summary>

**Inspected create_edit and verify_render instructions and checked libraries**


</details>

## Turn 174 - assistant (tool call)

- Message ID: `4516a9b4-7225-40a1-a6a6-084dd6e1fa47`
- Model: `gpt-5-6-pro`

```unknown
bash -lc mkdir -p /mnt/data/_founder_assets && cat > /mnt/data/_founder_assets/make_diagrams.py <<'PY'
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
from pathlib import Path

OUT = Path('/mnt/data/_founder_assets')

def box(ax, x, y, w, h, text, fontsize=10, lw=1.4):
    p = FancyBboxPatch((x,y), w,h, boxstyle='round,pad=0.02,rounding_size=0.02', fill=False, linewidth=lw)
    ax.add_patch(p)
    ax.text(x+w/2, y+h/2, text, ha='center', va='center', fontsize=fontsize, wrap=True)
    return p

def arrow(ax, x1,y1,x2,y2):
    ax.add_patch(FancyArrowPatch((x1,y1),(x2,y2),arrowstyle='->',mutation_scale=14,linewidth=1.2))

# Thesis stack
fig, ax = plt.subplots(figsize=(10,6))
ax.set_xlim(0,10); ax.set_ylim(0,6); ax.axis('off')
labels = [
    (0.5,4.8,2.0,0.7,'Human or business\nintent'),
    (3.0,4.8,2.0,0.7,'Coding agent / LLM'),
    (5.5,4.8,2.0,0.7,'Small JavaScript\napplication program'),
    (7.9,4.8,1.6,0.7,'Reviewable\nrelease plan'),
]
for args in labels: box(ax,*args)
arrow(ax,2.5,5.15,3.0,5.15); arrow(ax,5.0,5.15,5.5,5.15); arrow(ax,7.5,5.15,7.9,5.15)
box(ax,1.0,2.8,2.2,0.85,'Elegant denotational APIs\nbooking · search · CRM · payments')
box(ax,3.9,2.8,2.2,0.85,'Versioned module catalog\npermissions · quotas · bindings')
box(ax,6.8,2.8,2.2,0.85,'Professional runtime\nauth · audit · rollback · isolation')
arrow(ax,6.3,4.8,2.1,3.65); arrow(ax,6.5,4.8,5.0,3.65); arrow(ax,7.0,4.8,7.9,3.65)
box(ax,2.1,0.8,5.8,0.9,'Durable custom software created just in time\nPersonal apps → shared micro-apps → professional systems')
arrow(ax,2.1,2.8,3.4,1.7); arrow(ax,5.0,2.8,5.0,1.7); arrow(ax,7.9,2.8,6.6,1.7)
ax.set_title('The product thesis: agents specify intent; the platform owns production semantics', fontsize=14, pad=14)
fig.tight_layout(); fig.savefig(OUT/'thesis_stack.png', dpi=180, bbox_inches='tight'); plt.close(fig)

# Segment ladder
fig, ax = plt.subplots(figsize=(10,5.5))
ax.set_xlim(0,10); ax.set_ylim(0,5.5); ax.axis('off')
steps = [
    (0.6,0.6,2.0,0.8,'Personal\nemail client · todo · dashboard'),
    (2.5,1.5,2.0,0.8,'Friends & community\nbarbecue poll · club app'),
    (4.4,2.4,2.0,0.8,'Small business\nbooking · CRM · quoting'),
    (6.3,3.3,2.0,0.8,'Professional operations\nlogistics · inventory · portals'),
    (8.2,4.2,1.2,0.8,'Enterprise\nprivate apps'),
]
for s in steps: box(ax,*s, fontsize=9)
for i in range(len(steps)-1):
    x,y,w,h,_=steps[i]; x2,y2,w2,h2,_=steps[i+1]
    arrow(ax,x+w,y+h/2,x2,y2+h2/2)
ax.text(0.7,4.7,'Same runtime and module semantics',fontsize=12)
ax.text(0.7,4.25,'Different distribution, support, compliance, and willingness to pay',fontsize=10)
ax.set_title('The product can span a wide application ladder; go-to-market cannot start everywhere', fontsize=14, pad=14)
fig.tight_layout(); fig.savefig(OUT/'segment_ladder.png', dpi=180, bbox_inches='tight'); plt.close(fig)

# Business model stack
fig, ax = plt.subplots(figsize=(10,6))
ax.set_xlim(0,10); ax.set_ylim(0,6); ax.axis('off')
box(ax,1.0,4.6,8.0,0.8,'Builder subscription\ncreation credits · collaboration · environments · support', fontsize=11)
box(ax,1.0,3.4,8.0,0.8,'Application runtime\nbase fee per production app + metered compute, storage, bandwidth, users', fontsize=11)
box(ax,1.0,2.2,8.0,0.8,'Premium modules and resources\nsearch · booking · commerce · identity · messaging · databases', fontsize=11)
box(ax,1.0,1.0,3.7,0.8,'Marketplace take rate\nthird-party modules, templates, experts', fontsize=10)
box(ax,5.3,1.0,3.7,0.8,'Enterprise contracts\nSSO · private cloud · support · governance', fontsize=10)
for y in [4.6,3.4,2.2]:
    if y>2.2: arrow(ax,5.0,y,5.0,y-0.4)
arrow(ax,3.1,2.2,2.85,1.8); arrow(ax,6.9,2.2,7.15,1.8)
ax.set_title('Recommended revenue architecture: separate creation, runtime, modules, and enterprise value', fontsize=14, pad=14)
fig.tight_layout(); fig.savefig(OUT/'business_model_stack.png', dpi=180, bbox_inches='tight'); plt.close(fig)

# GTM sequence
fig, ax = plt.subplots(figsize=(11,4.6))
ax.set_xlim(0,11); ax.set_ylim(0,4.6); ax.axis('off')
xs=[0.3,2.45,4.6,6.75,8.9]
texts=[
    '1. Design partners\npaid app builds',
    '2. Repeatable\nvertical packs',
    '3. Studio / agency\nchannel product',
    '4. Self-serve\nagent builder',
    '5. Module marketplace\nenterprise platform',
]
for x,t in zip(xs,texts): box(ax,x,1.7,1.8,1.0,t,fontsize=10)
for i in range(4): arrow(ax,xs[i]+1.8,2.2,xs[i+1],2.2)
ax.text(0.4,3.5,'Revenue and customer learning first',fontsize=11)
ax.text(7.0,3.5,'Scalable distribution and ecosystem later',fontsize=11)
ax.set_title('Recommended commercialization sequence', fontsize=14, pad=14)
fig.tight_layout(); fig.savefig(OUT/'gtm_sequence.png', dpi=180, bbox_inches='tight'); plt.close(fig)

# Proof ladder
fig, ax = plt.subplots(figsize=(10,6))
ax.set_xlim(0,10); ax.set_ylim(0,6); ax.axis('off')
items=[
    (0.8,0.6,8.4,0.65,'Technical proof: secure runtime, modules, release, rollback, HTTP and identity'),
    (1.3,1.55,7.4,0.65,'Product proof: impressive end-to-end demos and repeatable app quality'),
    (1.8,2.5,6.4,0.65,'Customer proof: paid design partners and active production apps'),
    (2.3,3.45,5.4,0.65,'Economic proof: module attach rate, retention, and gross margin'),
    (2.8,4.4,4.4,0.65,'Scale proof: repeatable acquisition and expanding app count per customer'),
]
for i in items: box(ax,*i,fontsize=9.5)
for j in range(len(items)-1):
    x,y,w,h,_=items[j]; x2,y2,w2,h2,_=items[j+1]
    arrow(ax,5.0,y+h,5.0,y2)
ax.set_title('The seed story becomes stronger as proof moves from technology to customer economics', fontsize=14, pad=14)
fig.tight_layout(); fig.savefig(OUT/'proof_ladder.png', dpi=180, bbox_inches='tight'); plt.close(fig)
PY
python /mnt/data/_founder_assets/make_diagrams.py
ls -lh /mnt/data/_founder_assets/*.png
```

## Turn 175 - assistant

- Message ID: `901ce5c3-8a25-495d-995d-c75a9658be3f`
- Model: `gpt-5-6-pro`

Personal and friend-shared apps can drive viral discovery, while studios and small-business operators form the initial revenue wedge through subscriptions, active-app pricing, capability packs, and enterprise controls.

## Turn 176 - assistant (recap)

- Message ID: `c22b81a7-c812-40d0-a4a9-f44fab3bc191`

> _Stopped thinking_

## Turn 177 - assistant (thinking)

- Message ID: `3efa2c86-6dca-4821-b052-191a71637d6b`

<details><summary>Thinking</summary>

**Created diagrams, wrote founder dossier, and appended document sections**


</details>

## Turn 178 - user

- Message ID: `9adff765-63b0-4d53-8ac6-591e668656df`

Continue yo

## Turn 179 - assistant

- Message ID: `0fc2a938-ba6b-4481-89cc-7ebe892e1142`
- Model: `gpt-5-6-pro`

I’ll turn the technical thesis into an investor-facing strategy: market narrative, wedges, business models, seed pitch, hiring, risks, milestones, and fundraising materials.

## Turn 180 - assistant (thinking)

- Message ID: `60f8b777-91f6-4bba-99c9-f18d7babf113`
- Model: `gpt-5-6-pro`

<details><summary>Thinking</summary>

**Planning business pitch**

I’m considering how to continue the business pitch. It looks like I should create a comprehensive doc, using market research, competitors, funding details, and possibly prior documents, but no image generation for now.

**Planning document creation**

I’m thinking about how to create a large doc for the business pitch—likely both DOCX and Markdown. I might use a previous textbook as a foundation and conduct some web research on current platforms and market trends.


</details>

## Turn 181 - assistant (tool call)

- Message ID: `6110eec7-7164-466f-a257-a490c2af1073`
- Model: `gpt-5-6-pro`

```unknown
bash -lc cat /home/oai/skills/docx/SKILL.md && printf '\n---TEXTBOOK SKILL---\n' && cat '/mnt/data/SKILL(4).md' | sed -n '1,220p' && printf '\n---FILES---\n' && ls -lh /mnt/data | sed -n '1,120p'
```

## Turn 182 - assistant (thinking)

- Message ID: `ade54d9d-9117-4db9-b170-e7c69b8a929d`

<details><summary>Thinking</summary>

**Read and inspected docx documentation for content analysis**


</details>

## Turn 183 - assistant (thinking)

- Message ID: `c8b9254e-e92f-4cb1-8b4f-a461c9b63adc`
- Model: `gpt-5-6-pro`

<details><summary>Thinking</summary>

**Drafting business document**

I’m planning a big document for the user’s business pitch—120 pages, including research, sections on equity, and possibly a pitch deck. I’ll include footnotes and URLs but no full citations in the final.

**Drafted a business document**


</details>

## Turn 184 - assistant (thinking)

- Message ID: `f9cc95c7-76bb-4866-84ce-718aed375458`
- Model: `gpt-5-6-pro`

<details><summary>Thinking</summary>

**Researching current sources**

I need to gather updated information on various platforms like Replit, Lovable, Vercel, and others. I'll check official blogs and financial reports for financing, pricing models, and acquisitions, while focusing on business roles, founder matching, and seed fundraising.

**Researched current sources**


</details>

## Turn 185 - assistant (tool call)

- Message ID: `9b80012b-f2a6-4d17-8855-43f2dd4648da`
- Model: `gpt-5-6-pro`

```json
{"search_query":[{"q":"site:blog.replit.com March 2026 $400 million $9 billion 50 million users 85% Fortune 500 Replit"},{"q":"site:lovable.dev blog December 2025 $330 million $6.6 billion funding"},{"q":"site:vercel.com/blog v0 February 2026 4 million users production security shadow IT"},{"q":"site:wix.com press release Base44 acquisition 80 million 2025"}],"response_length":"long"}
```

## Turn 186 - assistant (thinking)

- Message ID: `09bba11b-0ba9-42d5-953c-0af357c50522`

<details><summary>Thinking</summary>

**Searched 20 webpages**


</details>

## Turn 187 - assistant (tool call)

- Message ID: `c3711b5f-eec2-4ea5-9c8e-8db07d6c6632`
- Model: `gpt-5-6-pro`

```json
{"search_query":[{"q":"site:blog.replit.com 2026 funding 400 million 9 billion 50 million users"},{"q":"site:replit.com/news 400 million 9 billion March 2026 Replit"},{"q":"site:replit.com 85% Fortune 500 50 million users 2026 funding"},{"q":"Replit March 2026 $400 million $9 billion official"}],"response_length":"long"}
```

## Turn 188 - assistant (thinking)

- Message ID: `59793d7e-8cec-4b7f-ab46-039e9a56639a`

<details><summary>Thinking</summary>

**Searched multiple sources for funding, user, and investment details**


</details>

## Turn 189 - assistant (tool call)

- Message ID: `8bb9647e-eee1-4f50-9818-2d390b3dbb2a`
- Model: `gpt-5-6-pro`

```unknown
bash -lc grep -n '!\[' /mnt/data/agent_native_app_platform_founder_dossier.md | sed -n '1,120p'; grep -n '_founder_assets' /mnt/data/agent_native_app_platform_founder_dossier.md | sed -n '1,120p'
```

## Turn 190 - assistant

- Message ID: `19558850-f9f1-489b-9e62-3913a49782f3`
- Model: `gpt-5-6-pro`

The key framing is an AI-native application operating system monetizing operationally complete capabilities, with the initial wedge proving safer, better generation than ordinary cloud stacks.

## Turn 191 - assistant (thinking)

- Message ID: `036386da-ff47-41ae-996e-b0f6980dd3d8`

<details><summary>Thinking</summary>

**Extracted image references and inserted claims into dossier file**


</details>

## Turn 192 - assistant (tool call)

- Message ID: `6f92e53e-946e-445d-8d9d-8b995e6ebf09`
- Model: `gpt-5-6-pro`

```unknown
bash -lc cat >> /mnt/data/agent_native_app_platform_founder_dossier.md <<'EOF'

# Part VII. The Founding Team

## 43. The current team story

The company already has the two capabilities that are hardest to manufacture after incorporation: a founder who has built the difficult technical substrate and a founder who can make the result feel like a product rather than an infrastructure demonstration.

That combination is unusually relevant to this market. Agent-generated software fails in two different ways. It can be operationally unsound, and it can be visually or behaviorally incoherent. The technical founder addresses the first class of failure through a controlled runtime, explicit modules, secure HTTP semantics, identity boundaries, versioned releases, rollback, and isolation. The design founder addresses the second through product direction, interface systems, application demonstrations, interaction quality, and a coherent visual language.

The missing capability is not “business” in the abstract. The missing capability is ownership of the market-facing company system:

- Choosing an initial customer and refusing distracting segments.
- Converting technical differentiation into a category narrative.
- Running customer discovery without turning every request into a feature commitment.
- Closing paid design partners and turning them into repeatable products.
- Designing pricing, packaging, and channel economics.
- Building the investor process and recruiting the first commercial team.
- Establishing a company cadence in which product, customer, and capital decisions reinforce one another.

![Founding team operating system](./_founder_assets/founding_team_system.png)

### 43.1 The technical founder's durable contribution

The technical founder should be described as more than the person who wrote the runtime. The founder has developed a point of view about how agents should create software:

1. Application code should express business intent through compact JavaScript or TypeScript.
2. Difficult operational semantics should live behind versioned native modules.
3. The host should enforce authentication, authorization, release policy, resource access, and runtime ownership.
4. Generated software should be inspectable, reproducible, rollbackable, and supportable.
5. The module system should be commercially meaningful, not merely a package registry.

This is the intellectual foundation of the company. Investors need to see that the technical work is not a collection of clever components. It is one architecture built around a specific market insight.

The technical founder's near-term job is therefore not to finish every subsystem. It is to make the architecture legible through a small number of undeniable applications, to close the remaining production gaps that block external use, and to create a module boundary that other engineers can extend.

### 43.2 The design founder's durable contribution

The design founder is not a downstream service provider who makes technical demos presentable. Design is part of the product architecture.

A platform that lets agents create professional applications needs a theory of interface generation. Without one, every application becomes a pile of generated components, inconsistent interaction patterns, and one-off responsive behavior. A typed widget protocol, semantic recipes, renderer targets, and application-level design constraints let the system create products that feel intentional while remaining easy for an agent to author.

The design founder should own or co-own:

- Product experience and interaction principles.
- The visual and semantic design system.
- The demo portfolio and customer-facing application quality.
- Design-partner discovery around end-user workflows.
- Template, recipe, and vertical-pack quality.
- The editor and review experience for generated applications.
- Brand and category expression.

The investor narrative should make this founder advantage concrete. Show several applications that share the same platform but do not look like the same template. Show how a design rule becomes a reusable system capability. Show the difference between generated code and generated product quality.

### 43.3 The commercial founder's required contribution

The third founder, if one joins, must complete the system rather than duplicate it. The person should be able to turn a broad technical platform into a sequence of narrow commercial proofs.

The required behavior is closer to an early-stage CEO and company builder than to a later-stage sales executive. A strong candidate can spend the morning interviewing an operations manager, the afternoon restructuring the product narrative with the other founders, and the evening building a seed investor map. The candidate must be comfortable selling something that still changes every week while protecting the long-term architecture from bespoke customer demands.

The person should not need to implement the runtime, but must be able to understand and explain why the runtime matters. A commercial founder who treats the product as a generic AI app builder will erase the differentiation. A commercial founder who can explain semantic modules, production guarantees, and the studio wedge in customer language can make the differentiation valuable.

### 43.4 The founding-team narrative

The external story should be concise:

> **We are a technical founder who built the agent-native runtime, a design founder who built an unusually strong application experience and demo system, and a commercial founder or founding executive who turns that technology into a repeatable market. Together we cover infrastructure, product quality, and company creation.**

Do not exaggerate team completeness before the commercial role is filled. Investors will discover the gap quickly. State it as an active and disciplined search, and demonstrate that the existing founders are already doing customer work rather than waiting for someone else to begin it.

### 43.5 Internal ownership before the third founder arrives

Until the role is filled, the existing founders need explicit temporary ownership:

| Company function | Temporary owner | Weekly output |
|---|---|---|
| Product and technical roadmap | Technical founder | One prioritized roadmap and release review |
| Design system and application quality | Design founder | Demo/application review and design-system decisions |
| Customer discovery | Shared, with one meeting owner | Interview notes, problem ranking, follow-ups |
| Sales pipeline | One named founder | Updated pipeline, next actions, pricing evidence |
| Company narrative and fundraising prep | One named founder | Deck revisions, investor map, proof gaps |
| Finance and administration | Technical founder or fractional operator | Cash report, contracts, legal checklist |

Shared responsibility without a named owner usually means no responsibility. Temporary ownership can change, but it must remain explicit.

## 44. Do you need a business co-founder?

A co-founder is not a job opening with a larger equity grant. A co-founder is a person who accepts company-level risk, takes durable authority over a major part of the system, and remains responsible when the original plan fails.

The correct question is therefore not “Would a business person help?” The answer to that question is always yes. The correct question is:

> **Does the company need another person with founder-level authority and commitment to own the market, capital, and organization for the next decade?**

### 44.1 Reasons to add a commercial co-founder

The case is strong when several conditions are true:

- The technical founder wants to remain deeply involved in architecture and product rather than spend most weeks selling, fundraising, recruiting, and managing.
- The design founder wants to own product and design rather than the entire commercial organization.
- The market requires category creation and founder-led enterprise or channel sales.
- A candidate brings exceptional founder-market fit, not merely general management experience.
- The candidate is willing to join before certainty, compensation, and organizational support exist.
- The candidate changes the rate at which the company learns, closes customers, and recruits.

Technical founders frequently seek complementary commercial skills. YC's co-founder matching data found that 74% of engineering founders preferred a co-founder with sales and marketing skills, while 53% preferred operations skills.[^S15] That preference does not prove a specific candidate is right. It confirms that the gap is common and strategically meaningful.

### 44.2 Reasons not to add one yet

Do not add a co-founder because fundraising feels uncomfortable, because investors ask who sells, or because the founders want someone to “handle business.” Those motivations create a vague role with impossible expectations.

Delay or reject the co-founder decision when:

- The candidate wants a mature product, salary, and team before committing.
- The candidate's primary value is investor introductions.
- The person cannot personally sell the first ten customers.
- The person does not develop a credible understanding of the product's architecture.
- The person proposes broad partnerships instead of direct customer work.
- The candidate treats design as marketing polish or technical work as an implementation detail.
- The existing founders have not decided who wants to be CEO.
- The company has not defined the decisions the new founder would own.

A strong founding commercial executive can be better than a weak co-founder. Titles should follow demonstrated company-level ownership.

### 44.3 Four viable leadership structures

| Structure | When it works | Main risk |
|---|---|---|
| Technical founder remains CEO; commercial co-founder becomes President or Chief Business Officer | Technical founder wants company leadership and can fundraise, while the commercial founder owns GTM and operations | Ambiguous final authority if decision rights are not explicit |
| Commercial co-founder becomes CEO; technical founder becomes CTO or Chief Product/Technology Officer | Technical founder wants to build product and the candidate has exceptional company-building capacity | Technical thesis may be diluted if CEO lacks product depth |
| Existing founders remain the founding team; hire a founding GTM executive | Founders can lead fundraising and strategy but need commercial execution | Executive may lack founder-level commitment or authority |
| Run without a dedicated commercial leader through design-partner phase | Existing founders can sell the first ten customers and want more evidence before recruiting | Market learning and fundraising preparation may move too slowly |

The company does not need to decide based on convention. It needs to decide based on the work each founder wants to perform repeatedly.

### 44.4 The CEO question

The CEO's core job at this stage is to maintain company coherence. That means choosing the market, allocating scarce attention, recruiting, financing the company, resolving founder disagreements, and ensuring that customers receive value.

The technical founder should remain or become CEO if that work is energizing and if the founder is willing to become excellent at it. Technical depth does not disqualify someone from CEO leadership. Refusing market and organizational work does.

A commercial co-founder should become CEO when the person has the strongest combined ability to:

- Hold the product and market thesis.
- Recruit exceptional people.
- Sell before the sales process exists.
- Raise capital without distorting the company.
- Make hard priority decisions.
- Represent the company with credibility to technical and nontechnical audiences.
- Preserve trust among the founders under pressure.

Do not decide the CEO role as an equity prize or status concession. Decide it as an operating responsibility.

### 44.5 Recommended decision

The recommended path is:

1. The existing founders begin customer discovery and paid design-partner work immediately.
2. They publish a precise co-founder brief rather than a generic search.
3. Promising candidates complete a six-week working trial.
4. The team makes the co-founder and CEO decisions after observing real customer, product, and conflict behavior.
5. A candidate who is strong but not yet founder-level can join as a founding executive with milestone-based equity.

This sequence preserves speed while protecting the cap table and founding relationship.

## 45. Role definition for a commercial co-founder

A useful role description begins with outcomes, not traits.

### 45.1 Mission

> **Turn an agent-native application platform with strong technology and design into a focused company with paid customers, repeatable distribution, a credible seed narrative, and an operating system capable of scaling.**

### 45.2 Twelve-month outcomes

The commercial co-founder should be accountable for producing, with the other founders:

1. A clearly defined beachhead and category narrative.
2. Ten to twenty paid design partners or equivalent recurring customers.
3. A repeatable studio, agency, or vertical-pack acquisition motion.
4. Pricing evidence across builder, runtime, and premium-module revenue.
5. Customer case studies showing time-to-value and production durability.
6. A qualified pipeline that does not depend entirely on personal friends.
7. A completed seed financing on terms appropriate to the evidence.
8. The first commercial and customer-engineering hires.
9. A company operating cadence, budget, and board reporting system.
10. A founder relationship that becomes stronger after disagreements and missed targets.

### 45.3 Weekly responsibilities

The role initially includes direct work that later becomes separate functions:

- Conduct customer discovery and sales calls.
- Build and advance the design-partner pipeline.
- Write proposals and negotiate pilot agreements.
- Review application delivery and customer outcomes.
- Translate customer patterns into product priorities with the technical and design founders.
- Test packaging, pricing, and module economics.
- Build channel relationships with studios and agencies.
- Maintain the investor narrative and fundraising data room.
- Recruit early employees and advisors.
- Own budget, runway, and basic business operations.
- Lead the weekly company review.

A candidate who only wants strategy, partnerships, or fundraising is not suited to the stage.

### 45.4 Ideal experience profile

No candidate will match every line. The strongest profiles include some combination of:

- Founder or first ten employee at a developer-tools, infrastructure, vertical SaaS, automation, or application-platform company.
- Successful founder-led sales to small businesses, agencies, studios, or enterprise teams.
- Experience packaging technical infrastructure into a simple commercial product.
- Evidence of building a category narrative rather than merely executing an established playbook.
- Ability to negotiate partnerships without substituting partnerships for customer acquisition.
- Product judgment sufficient to distinguish a repeated pattern from a bespoke request.
- Fundraising experience or the ability to learn it rapidly.
- Comfort with open source, developer communities, and technical buyers.
- Respect for design as a product capability.
- Experience operating with very little staff and incomplete data.

The candidate does not need to be a former venture-backed CEO. A high-agency product, GTM, or operations leader who has repeatedly created new motions can be stronger than a polished executive from a mature company.

### 45.5 Required product understanding

By the end of a trial, the candidate should be able to explain, without scripts:

- Why high-level modules make agents more reliable.
- Why this is not simply Replit, Lovable, or v0 on Goja.
- How the runtime and release model reduce operational risk.
- Why the first customer segment is narrower than the product vision.
- How builder, runtime, module, and marketplace revenue differ.
- Why design is part of the platform architecture.
- Which security claims the system can and cannot make today.
- What proof is still missing.

Commercial clarity requires technical honesty.

### 45.6 Authority and decision rights

The role should come with actual authority. A possible initial division is:

| Decision area | Primary owner | Required consultation |
|---|---|---|
| Company strategy and financing | CEO | All founders |
| Runtime architecture and security | Technical founder | CEO and design founder for product impact |
| Product experience and design system | Design founder | Technical founder and CEO |
| Beachhead, pricing, and GTM | Commercial founder | All founders |
| Customer commitments | Commercial founder | Technical and design founders before roadmap commitments |
| Hiring | Functional owner | CEO and at least one other founder |
| Budget | CEO | Board and functional owners |
| Major module roadmap | Product trio | Customer evidence and technical feasibility |

The point is not rigid bureaucracy. It is to prevent every disagreement from becoming a referendum on the founding relationship.

## 46. Candidate scorecard

Founders often choose co-founders through chemistry and narrative. Chemistry matters, but it is difficult to distinguish early rapport from durable compatibility. A scorecard forces the team to collect evidence.

### 46.1 Weighted scorecard

| Dimension | Weight | Evidence to collect |
|---|---:|---|
| Founder motivation and risk tolerance | 15% | Full-time commitment, financial expectations, persistence under ambiguity |
| Customer discovery | 15% | Quality of interviews, synthesis, ability to find non-obvious pain |
| Founder-led sales | 15% | Ability to create urgency, ask for money, negotiate, and close |
| Strategic judgment | 12% | Beachhead selection, prioritization, rejection of distractions |
| Product and technical fluency | 10% | Accurate explanation of architecture and customer consequences |
| Narrative and communication | 10% | Customer pitch, investor pitch, writing, listening, precision |
| Operating ability | 8% | Cadence, follow-through, financial discipline, recruiting |
| Fundraising and network creation | 5% | Investor understanding, warm path creation, reference quality |
| Working style and conflict behavior | 10% | Candor, accountability, speed, ability to disagree productively |

A candidate does not pass because the weighted score exceeds a number. The score identifies where enthusiasm lacks evidence.

### 46.2 Work samples

Use real work rather than hypothetical interviews:

1. **Customer interview.** The candidate leads a discovery call with a potential design partner, then writes a synthesis separating facts, interpretations, and product implications.
2. **Paid pilot proposal.** The candidate produces a one-page proposal with scope, price, timeline, success criteria, and exclusions.
3. **Positioning exercise.** The candidate explains the product to a studio owner, a seed investor, and a small-business operator without using the same pitch.
4. **Pricing review.** The candidate critiques the proposed pricing model and designs two tests.
5. **Founder disagreement.** The team debates a real request that would create short-term revenue but distort the platform.
6. **Investor meeting.** The candidate participates in or simulates a partner meeting and handles objections.
7. **Operating review.** The candidate runs a weekly meeting using actual pipeline, product, and cash data.

### 46.3 Reference questions

References should answer behavioral questions:

- What did the candidate personally create from nothing?
- Did the candidate sell, or manage people who sold?
- How did the person behave when a major plan failed?
- Did colleagues trust the candidate with bad news?
- Which kinds of people performed poorly under the candidate?
- Did the candidate make product promises that engineering could not keep?
- How did the person handle credit and blame?
- Would the reference found another company with this person?
- What should the existing founders know before sharing control?

Seek references supplied by the candidate and back-channel references where appropriate and ethical.

### 46.4 Red flags

Treat these as evidence, not personality quirks:

- Uses “we” for achievements but cannot describe personal contribution.
- Talks primarily about brand, partnerships, or investors rather than customers.
- Wants to delegate outbound sales before closing it personally.
- Cannot state what should not be built.
- Treats technical complexity as something engineering should hide from leadership.
- Confuses confidence with certainty.
- Produces many introductions but few advanced commitments.
- Avoids written commitments and measurable outcomes.
- Changes the company story to match every audience.
- Negotiates founder economics before doing meaningful work together.
- Is dismissive of support, implementation, or operational details.
- Blames prior teams without describing personal mistakes.

## 47. Search channels

A co-founder search should be run like a high-priority company process. Waiting for a perfect introduction creates no learning and gives the search no deadline.

### 47.1 Start with the co-founder brief

Publish or privately circulate a concise brief containing:

- The company thesis.
- What has already been built.
- The design proof and demonstrations.
- The commercial hypothesis and initial wedge.
- The exact role and twelve-month outcomes.
- The current founder roles.
- What remains uncertain.
- Expected commitment, location, and timing.
- The working-trial process.
- The founder's honest reason for seeking a partner.

The brief should attract people who want the actual work, not merely the category.

### 47.2 Warm network

Ask for introductions from:

- Founders of developer-tool, infrastructure, no-code, vertical SaaS, and agency-platform companies.
- Seed investors and angel investors who know zero-to-one operators.
- Customers and potential design partners.
- Senior product, partnerships, and GTM leaders from adjacent platforms.
- Designers and engineering leaders who have worked with unusually commercial operators.
- Former colleagues, open-source collaborators, and founder communities.

The request should describe the person, not ask whether someone knows “a business co-founder.”

### 47.3 Structured founder communities

Use founder communities as talent-density tools rather than endorsements. YC operates a dedicated co-founder matching platform, and its published examples include teams that worked on trial projects before committing.[^S22] South Park Commons supports founders from exploration through funded company creation, with current funding described as ranging from $1 million to $10 million.[^S20] Entrepreneurs First explicitly accepts individuals with an early idea or a co-founder under test and runs a matching process.[^S21]

Other relevant sources include:

- Founder residencies and accelerators.
- Developer-tools and AI-infrastructure communities.
- Design-technology communities.
- Industry-specific operator networks in booking, commerce, logistics, and SMB software.
- Local founder groups where repeated in-person work is possible.

Do not join a program solely to outsource the search. Join when the community, location, capital, and schedule improve the company's odds.

### 47.4 Targeted outbound

Build a list of fifty to one hundred people with evidence of relevant behavior. Good target profiles include:

- Former founders whose companies did not work but who demonstrated strong sales and company judgment.
- Early GTM or product leaders at Retool, Airtable, Replit, Lovable, Vercel, Supabase, Shopify, Wix, automation platforms, or vertical SaaS companies.
- Agency or studio founders who productized custom software delivery.
- Operators who launched a new business line inside a platform company.
- Investors or community leaders who want to return to operating.

A short outbound message should state why this particular person fits the problem. Generic mass outreach is weak evidence of how the candidate search will be run.

### 47.5 Candidate funnel

Track the search:

| Stage | Target |
|---|---:|
| Identified profiles | 100 |
| Warm or tailored outreach | 50 |
| First conversations | 20 |
| Deep founder conversations | 8 |
| Working sessions | 4 |
| Six-week trials | 1–2 |
| Founder decision | 0 or 1 |

“No hire” is a valid outcome. A forced co-founder is more expensive than a longer search.

## 48. The working-trial process

The trial should expose the real work of founding the company. Social dinners and pitch conversations reveal compatibility, but they do not reveal execution under pressure.

### 48.1 Trial structure

A six-week trial can be run while legal founder status remains undecided.

#### Week 0: explicit expectations

Agree in writing on:

- Time commitment.
- Confidentiality and intellectual-property assignment for trial work.
- Whether the trial is paid consulting work.
- Which decisions remain with the existing founders.
- Expected artifacts and customer access.
- Evaluation criteria.
- What happens if either side stops early.

#### Week 1: understand and restate the thesis

The candidate reviews the product, technical companion document, demos, market analysis, and current pipeline. The output is a written company thesis in the candidate's own words, including the strongest objection to the business.

#### Week 2: customer discovery

The candidate sources or joins at least five interviews. The output is a problem map, buyer map, repeated-language analysis, and recommendation about the initial wedge.

#### Week 3: commercial offer

The candidate creates the design-partner offer, pricing, scope, agreement outline, and outreach sequence. The team sends it to real prospects.

#### Week 4: sell and negotiate

The candidate leads sales conversations and asks for a paid commitment. The output is not necessarily a closed contract; it is evidence of how the person creates urgency, handles objections, and updates strategy.

#### Week 5: investor and partner narrative

The candidate revises the one-pager and pitch, runs several practice meetings, and builds a targeted investor or partner map.

#### Week 6: operating review and founder decision

The candidate runs a company review covering product, customers, pipeline, cash, risks, and next-month priorities. The founders then discuss role, authority, economics, and unresolved concerns.

### 48.2 Trial scorecard

At the end, answer:

- Did the candidate increase the rate of customer learning?
- Did the candidate ask for money directly?
- Did prospects understand the product more clearly?
- Did the candidate protect the long-term architecture from one-off demands?
- Did written work become more precise?
- Did the candidate reliably complete commitments?
- Did disagreement improve decisions?
- Did the existing founders want to share difficult information with this person?
- Did everyone become more ambitious and more realistic?
- Would the team still choose this person after a failed fundraise or lost customer?

### 48.3 Trial compensation

There are three reasonable structures:

1. **Unpaid mutual exploration** for a limited number of hours, before the candidate performs material company work.
2. **Paid consulting agreement** for a part-time trial, with all work assigned to the company.
3. **Short employment arrangement** when the candidate works full-time and local law requires employment treatment.

Use counsel. Do not rely on informal promises about future equity in exchange for substantial work.

### 48.4 Why the trial matters

Carta reports that two-founder teams remain the most common among venture-funded startups, and YC matching data shows that technical and nontechnical pairings are common.[^S16][^S15] Those population patterns do not reduce the importance of individual compatibility. Founder failure is often a governance and trust failure. A trial is a low-cost way to observe the future company before making it irreversible.

## 49. Equity, vesting, and governance

Founder equity should reflect future company-building risk and commitment, while acknowledging the substantial technology and design value already created. It should not be calculated as an hourly invoice for past work or divided automatically by title.

### 49.1 Principles

1. **Equity pays for the future.** Past contributions matter because they de-risk the company, but most founder equity compensates years of future work and opportunity cost.
2. **Vesting protects every founder.** A founder who leaves early should not retain the same ownership as founders who continue building.
3. **Authority and equity are related but not identical.** The CEO can have final operating authority without owning a majority.
4. **Near-equal splits can be rational.** Carta reported that 44.6% of two-founder teams formed in 2025 divided equity equally, and the median two-founder split was 51–49.[^S23] That is evidence of a trend, not a rule for this company.
5. **The process matters.** A transparent model and explicit assumptions are more important than pretending there is one objectively correct percentage.

### 49.2 Contribution model

Evaluate each founder across:

- Pre-existing intellectual property and product proof.
- Full-time start date.
- Cash invested or salary deferred.
- Future role breadth and company-level risk.
- Replacement difficulty.
- Customer, distribution, or fundraising leverage.
- Expected duration of contribution.
- Personal guarantees or unusual liabilities.

Do not assign precise percentage points to each category as if the result were scientific. Use the model to reveal disagreement.

### 49.3 Illustrative structures

These are discussion examples, not recommendations:

| Situation | Illustrative founder allocation before employee pool and financing |
|---|---|
| Technical and design founders have both worked full-time for a substantial period; commercial founder joins before revenue and takes CEO-level risk | 38% technical / 32% design / 30% commercial |
| Technical founder created most existing IP; design founder recently joined; commercial founder joins after first customers | 48% technical / 27% design / 25% commercial |
| All three have worked together through a meaningful trial and commit at the same early stage | Approximately one-third each, adjusted for prior IP and cash |
| Candidate joins after seed financing with market salary and narrower GTM role | Founding-executive option grant rather than co-founder common stock |

The correct number depends on facts not provided here. The important distinction is whether the new person is accepting founder-level uncertainty before the commercial proof exists.

### 49.4 Vesting

A common founder structure is four-year vesting with a one-year cliff, usually implemented through company repurchase rights over unvested founder stock. For founders who have already spent material time building the company, the board can recognize a portion of elapsed service while preserving meaningful future vesting.

Questions to decide with counsel:

- Vesting commencement date for each founder.
- Credit for prior full-time service.
- Treatment of existing intellectual property.
- Single-trigger or double-trigger acceleration, if any.
- Repurchase price for unvested shares.
- Treatment of voluntary departure, termination, disability, and death.
- Whether founders receive restricted stock or options based on tax and company timing.
- Timely 83(b) elections where applicable.

Do not promise acceleration casually. Broad single-trigger acceleration can make an acquisition harder and create divergent incentives.

### 49.5 Governance

The founders should sign a written founder agreement or equivalent set of corporate documents covering:

- Roles and decision rights.
- CEO authority.
- Board composition.
- Reserved decisions requiring board or founder approval.
- Equity and vesting.
- Intellectual-property assignment.
- Confidentiality.
- Founder departure.
- Outside activities.
- Expense and salary policy.
- Conflict resolution.
- Sale of the company.
- Deadlock process.

A simple initial board might contain the CEO and one other founder, expanding when an institutional financing occurs. Another structure gives all three founders board seats before financing. The choice should account for local law, investor expectations, and the need to avoid operational deadlock.

### 49.6 Reserved decisions

Examples that should not be made unilaterally by one functional founder:

- Issuing equity or debt.
- Selling the company or material intellectual property.
- Changing founder compensation materially.
- Hiring or firing a founder-level executive.
- Entering an exclusive strategic partnership.
- Changing the primary business or abandoning the platform thesis.
- Taking on material debt or long-term obligations.
- Committing to a customer requirement that changes the security model.

### 49.7 Founder conflict protocol

Write the protocol before conflict:

1. The decision owner writes the decision, alternatives, evidence, and deadline.
2. Each founder states objections and the evidence that would change their view.
3. The team distinguishes reversible from irreversible decisions.
4. Reversible decisions go to the functional owner after consultation.
5. Irreversible company decisions go to the CEO or board under agreed authority.
6. Relationship conflicts are discussed separately from the product decision.
7. Persistent deadlock can use a mutually selected advisor or board member, but not as a substitute for founder responsibility.

The founders do not need to agree on every decision. They need to trust the decision system.

---
EOF

```

## Turn 193 - assistant

- Message ID: `a147aad2-50e5-45d0-9e72-9b8ff95a80c7`
- Model: `gpt-5-6-pro`

The entry strategy pairs viral personal/shareable apps with revenue-bearing small-business deployments through studios, while pricing attaches to live apps and managed capabilities. Next come reusable pitch assets.

## Turn 194 - assistant (thinking)

- Message ID: `5ffeabc4-7c1d-4b3c-8ea2-67f59e184d36`

<details><summary>Thinking</summary>

**Wrote Part VII and Part VIII sections 43-55**


</details>

## Turn 195 - assistant (tool call)

- Message ID: `02a1d30b-5992-45f3-8ce0-1aed328702fe`
- Model: `gpt-5-6-pro`

```unknown
bash -lc cat >> /mnt/data/agent_native_app_platform_founder_dossier.md <<'EOF'

# Part IX. Pitch Assets

## 56. One-sentence pitches

One sentence cannot explain the entire company. Its job is to create the correct next question.

### 56.1 Primary investor pitch

> **We are building an agent-native application cloud where coding agents create compact JavaScript applications over secure, high-level modules, so custom software can be generated quickly and still be production-ready, governable, and maintainable.**

### 56.2 Outcome-oriented investor pitch

> **We let AI agents turn business intent into professional software by replacing thousands of lines of fragile operational glue with versioned modules for identity, payments, search, booking, data, UI, and deployment.**

### 56.3 Studio and agency pitch

> **Deliver custom client applications in days instead of months, using an agent-native platform that handles the hard production work and lets your team focus on workflow and design.**

### 56.4 Small-business customer pitch

> **We create software around the way your business actually works, then keep it hosted, secure, backed up, and easy to change as the business evolves.**

### 56.5 Enterprise pitch

> **Give employees and coding agents a governed way to create internal applications, with approved modules, identity, permissions, audit, release review, and a complete application inventory.**

### 56.6 Developer pitch

> **Write the business logic in JavaScript; import high-level modules; let the host own authentication, concurrency, secrets, infrastructure, deployment, and rollback.**

### 56.7 Module-provider pitch

> **Package your service as an agent-friendly application primitive, and we provide runtime integration, policy, metering, billing, documentation, and distribution into generated apps.**

### 56.8 General-audience pitch

> **You describe the software you need, an AI builds it from reliable building blocks, and the platform keeps it working like a professionally engineered product.**

### 56.9 Pitches to avoid

Avoid leading with:

- “AWS Lambda for Goja.” This describes an implementation layer and understates the product.
- “A better Replit.” It invites a feature comparison with a much larger company.
- “No-code for LLMs.” It is clever but unclear to buyers.
- “An app store for modules.” The marketplace is a later business model, not the initial value.
- “Build anything instantly.” The claim is broad, unprovable, and associated with prototype tools.
- “Secure by default” without specifying the structural controls and current scope.

## 57. Thirty-second pitch

### 57.1 Investor version

> Coding agents can generate a lot of code, but real applications still depend on difficult operational details: authentication, permissions, database semantics, payments, search, booking, deployment, rollback, and security. Today agents reproduce that glue differently in every project, which makes generated apps fragile. We built an application cloud where the agent writes a small JavaScript program against high-level, versioned modules, while the platform guarantees the operational behavior. We already have the secure runtime, HTTP framework, release system, identity work, and strong design demos. We are now using it with studios and design partners to build professional custom apps in days and turn the repeated capabilities into a module business.

### 57.2 Customer version

> Most businesses end up adapting their work to generic software or paying a large amount for custom development. Our platform lets us create an application around your real workflow in days. The application is not a throwaway prototype: it has users, permissions, persistent data, backups, release history, and support. When you need to change it, we create a reviewed release and can roll back safely.

### 57.3 Cofounder-candidate version

> We have a technically deep, working agent-native application platform and a design founder producing excellent product demos. The missing founder role is to choose the first market, close paid design partners, build the channel and pricing model, and lead the company and seed process with us. This is not a finished product looking for a salesperson. It is a company formation problem with unusually strong technical and design proof.

## 58. Two-minute pitch

> Software creation is moving from writing every implementation detail to describing what should exist. The current generation of coding agents proves that millions of people want to build applications, but the way those tools work creates a new problem: the agent generates a conventional stack and the user inherits every operational decision. Authentication, authorization, database migrations, payments, webhooks, search, deployment, and rollback are regenerated in slightly different ways for every app.
>
> Our core insight is that an agent should not have to reproduce those semantics. It should write a compact application program against high-level modules. A booking API should mean reserve a valid slot, not generate locks, retries, time-zone rules, reminders, and cancellation logic. A product-search API should mean search the authorized catalog, not configure indexing, ranking, typo tolerance, tenant filters, and metering. The platform owns that complexity in versioned modules.
>
> We built the technical foundation for this model: a Go-hosted JavaScript runtime with explicit module composition, a secure HTTP framework where authentication and authorization run before JavaScript, professional release and rollback semantics, identity integration, application workers, and a typed UI system. Our design co-founder has built applications that demonstrate the product quality this architecture can produce.
>
> We are entering through AI-native studios, agencies, and operational small-business applications such as booking, lightweight CRM, catalogs, quotes, and logistics. They need to deliver custom software repeatedly, which gives us revenue and shows us which modules recur. We charge for the builder, each production application, premium modules, and eventually enterprise governance and a marketplace.
>
> The long-term opportunity is a cloud where people and agents create software just in time—from a personal tool or a barbecue scheduling app to a professional CRM or commerce operation—without requiring the agent to reinvent production engineering every time.

## 59. Ten-minute investor narrative

The ten-minute pitch should be treated as one argument with a live product proof, not twelve disconnected slide descriptions.

### 59.1 Minute 0–1: the change in software creation

Open with the behavior, not the technology.

> More people can now create software by describing it. That is already a mass-market behavior. The limiting problem has moved. The question is no longer only whether an agent can generate an interface and some code. The question is whether the resulting application can safely run a business, evolve over time, and be operated by someone who did not hand-engineer the stack.

Show one strong generated application immediately. Do not spend the first minute on a market chart.

### 59.2 Minute 1–2: the production gap

Show a conventional generated application architecture:

```text
prompt
  -> generated frontend
  -> generated API routes
  -> generated schema
  -> auth integration
  -> payment integration
  -> deployment config
  -> monitoring and recovery
```

Explain that the agent is asked to reproduce operational decisions that have failure modes far outside the visible interface.

Use a concrete example:

> “Reserve this booking slot” appears simple. In production it means concurrency control, idempotency, time zones, cancellation rules, reminders, authorization, and payment state. If every app regenerates those rules, every app becomes a new reliability problem.

### 59.3 Minute 2–3: the insight

Introduce the semantic split.

> We move the operational semantics into versioned modules. The agent specifies what the application means. The platform implements how that meaning is safely produced.

Show two code samples side by side: one conventional integration and one compact module call. The module sample should be real and executable.

### 59.4 Minute 3–5: live demo

The live demo should follow a fixed sequence:

1. Start from a plain-language application request.
2. Show the agent selecting or being constrained to approved modules.
3. Show the generated compact application source.
4. Open a working preview with high design quality.
5. Show the data and user workflow.
6. Request a meaningful change.
7. Show the source and authority diff.
8. Create a release candidate and run validation.
9. Activate the release.
10. Demonstrate rollback or a denied unsafe change.

A good demo request might be:

> “Create a barbecue planning app for twenty friends. Let people propose dates, vote, claim food items, and pay their share. The organizer can see attendance and send reminders.”

Then connect it to a professional version:

> “The same module semantics support a catering booking system, a membership event platform, or a field-service scheduling workflow. The surface changes; the production capabilities remain governed and reusable.”

### 59.5 Minute 5–6: what is built

Show the system as a set of completed foundations and explicit gaps:

**Built or technically proven:**

- Goja runtime ownership and asynchronous execution.
- xgoja provider and native-module composition.
- Secure planned HTTP routes.
- Authentication, sessions, programmatic agents, CSRF, resources, authorization, audit, rate limits, and guarded fetch.
- Deployment validation, immutable releases, activation, rollback, and agent identities.
- Tiny-IDP production and scriptable identity foundations.
- Widget DSL and high-quality application demos.

**Being productized:**

- Isolated multi-tenant worker plane.
- Commercial module catalog and entitlement enforcement.
- Builder workspace and application planning.
- Design-partner delivery and studio workflow.
- Billing, usage, support, and customer operations.

This honesty improves credibility. The company has solved hard problems, but has not yet solved every business problem.

### 59.6 Minute 6–7: beachhead

State one first market:

> We are starting with AI-native studios, agencies, and automation consultants that repeatedly deliver operational software. They already have customers, they understand custom workflows, and they feel the cost of rebuilding authentication, data, payments, search, deployment, and maintenance for every project.

Show the first solution packs:

- Booking and customer portal.
- Lightweight CRM and quoting.
- Catalog, product search, and ordering.
- Internal logistics and status workflows.

Explain that direct small-business customers are a secondary channel and personal/shared apps are a product-led surface, not the initial revenue model.

### 59.7 Minute 7–8: business model

Show the four revenue layers:

1. Builder subscription.
2. Production application runtime.
3. Premium modules and resources.
4. Enterprise, marketplace, and partner revenue.

Use one invoice example:

```text
Studio plan                         $499 / month
8 active client applications       $392 / month
Booking module on 3 apps            $147 / month
Product search usage                 $86 / month
Storage and runtime overage           $41 / month
-------------------------------------------------
Monthly platform revenue           $1,165
```

State that the numbers are hypotheses being tested, not published pricing.

### 59.8 Minute 8–9: defensibility

Defensibility is not “we use Goja.” It is the combination of:

- High-level module semantics and operational edge cases.
- Application and release outcome data.
- A growing corpus of successful compact programs.
- Design recipes and renderer systems.
- Studio and module-provider distribution.
- Trust, governance, and application inventory.
- Module economics that persist after generation.

Explain that better models improve the platform because they become better clients of the same semantic APIs.

### 59.9 Minute 9–10: team, proof, and ask

> The technical founder built the core runtime and security architecture. The design founder built an unusually strong application and interface system. We are adding the commercial founder or founding GTM leader who will own the first market and company-building motion. Over the next eighteen to twenty-four months, the capital turns the technical proof into paid design partners, a repeatable studio product, the first premium module catalog, and a self-service application cloud.

State the exact round, milestones, and current customer proof. End on the application, not the financing slide.

## 60. Investor one-pager

### From intent to production software

**Company:** Working name to be determined  
**Category:** Agent-native application cloud  
**Stage:** Technical product built; design-partner commercialization  
**Round:** Targeting a $3.5 million seed, adjusted to customer proof

#### Problem

Coding agents can generate application code, but professional software depends on operational semantics that agents currently reproduce in every project: authentication, permissions, data consistency, payments, search, booking, secrets, integrations, deployment, observability, migration, and rollback. The generated application may look complete while carrying hidden security and maintenance risk.

#### Insight

LLMs perform better when they operate against small, typed, goal-oriented APIs. The application should state what a business operation means; the platform should own how it runs safely. A search module should expose product search, not search-cluster administration. A booking module should expose reservation semantics, not locks and reminder queues.

#### Product

The platform lets coding agents generate compact JavaScript or TypeScript applications over a catalog of secure, versioned modules. It provides:

- Agent planning and generation.
- High-level modules for data, identity, payments, search, booking, messaging, UI, and workflows.
- A Go-owned secure HTTP pipeline.
- Isolated execution with explicit permissions and resources.
- Preview, validation, immutable releases, deployment, audit, and rollback.
- A typed UI protocol and professional design system.
- APIs and MCP tools for external coding agents.

#### Why now

Prompt-to-app platforms have validated mass demand and attracted major usage and capital. At the same time, leading platforms now describe production security, governance, built-in primitives, and agent-driven deployment as central product problems. The competitive frontier is moving from code generation toward reliable application semantics.

#### Beachhead

Start with AI-native studios, agencies, automation consultants, and operational small-business applications. These customers create repeated custom software and expose recurring module patterns. Initial packs include booking, lightweight CRM, catalog/search, quoting/orders, and internal logistics.

#### Business model

- Builder and studio subscriptions.
- Base fee and metered usage per production application.
- Premium modules and managed resources.
- Enterprise governance and private deployment.
- Marketplace take rate on modules, templates, and experts.

#### Defensibility

The moat compounds through module operational history, application and release outcome data, a corpus of successful agent-authored programs, design recipes, provider economics, partner distribution, and a trusted governance layer. Model improvements increase the value of the platform rather than eliminating it.

#### Team

- Technical founder with a substantial first version of the runtime, module system, HTTP security framework, release control plane, and identity architecture.
- Design founder with strong product craft, renderer and DSL work, and impressive working demonstrations.
- Active search for a commercial co-founder or founding GTM leader to own market selection, customers, partnerships, fundraising, and company operations.

#### Eighteen- to twenty-four-month milestones

- Ten to twenty paid design partners and repeated production use.
- Two to three proven vertical solution packs.
- Studio workspace and external-agent API.
- First premium module catalog with measured margins.
- Self-service application creation and runtime billing.
- Production worker isolation, governance, support, and reliability evidence.

#### Ask

Capital, design partners, studio relationships, module-provider partners, and introductions to an exceptional commercial co-founder.

## 61. Outreach messages

Outreach should be brief enough to answer and specific enough to demonstrate fit.

### 61.1 Warm investor introduction request

**Subject:** Introduction to [Partner] — agent-native application platform

> I am building a platform that lets coding agents create compact JavaScript applications over secure, high-level modules for identity, data, payments, search, booking, UI, and deployment. The technical runtime and several strong product demos are working; we are now starting a focused design-partner motion with studios and operational software use cases.
>
> [Partner] appears relevant because of their work in [developer tools / application infrastructure / design software / vertical SaaS]. Would you be comfortable introducing us? I can send a one-page summary and a short demo first.

### 61.2 Direct investor message

**Subject:** Agents can generate code; we are building the production semantics

> [Name] — I am the technical founder of an agent-native application cloud. Instead of asking an LLM to regenerate authentication, database behavior, payments, search, deployment, and rollback for every app, the agent writes a small JavaScript program against versioned high-level modules and the host guarantees the operational behavior.
>
> We have built a substantial secure runtime and release foundation, and my design co-founder has working demos that show the product quality. We are entering through studios and repeated operational applications. Your investment in / writing about [specific company or thesis] suggests this may fit. May I send a five-minute demo and one-page memo?

### 61.3 Design-partner message

**Subject:** Build one of your recurring workflows as a professional custom app

> We are working with a small group of teams that currently coordinate important work through spreadsheets, forms, email, and several disconnected tools. We can turn one of those workflows into a custom application in days, including users, permissions, data, notifications, and a controlled release process.
>
> We are looking for workflows that are repeated, painful, and likely to change over time. The design partnership is paid but discounted, and you receive a working production application plus direct influence over the platform. Would a 30-minute workflow review be useful?

### 61.4 Studio or agency partner message

**Subject:** A production platform for AI-native custom app delivery

> Your team already knows how to discover workflows and design client experiences. We are building the runtime that removes the repeated production work: auth, permissions, data, payments, search, booking, deployment, rollback, and managed modules behind a compact JavaScript API.
>
> We are selecting a few studios to test whether the platform can reduce delivery time and create recurring runtime revenue without taking away the client relationship. I would like to show you the current demos and compare them with the kinds of projects you repeatedly build.

### 61.5 Commercial co-founder message

**Subject:** Cofounder role: turn a working agent-native app cloud into a company

> I have built a technically substantial first version of an application platform designed for coding agents: compact JavaScript programs, native high-level modules, secure HTTP semantics, release/version/rollback, identity, and isolated hosting. A design founder has built an unusually strong product and demo layer.
>
> We are looking for the person who wants founder-level ownership of market selection, design partners, pricing, studio channels, company operations, recruiting, and seed fundraising. The role starts with a working trial on real customer and pitch work; it is not a generic “business co-founder” search. Your experience with [specific evidence] looks unusually relevant. Are you open to a direct conversation?

### 61.6 Advisor request

> We are not looking for a ceremonial advisor list. We need help with [specific issue: studio channel economics, developer-platform pricing, enterprise app governance, module marketplace, or seed positioning]. Could we schedule one focused session? I will send a short memo with the decision, evidence, and alternatives in advance.

### 61.7 Customer reference request

> We are preparing a financing and broader design-partner launch. Would you be comfortable speaking with a small number of investors or prospects about the problem you had, the application we delivered, the time to value, and what still needs improvement? We will coordinate each request and never share confidential information without approval.

### 61.8 Follow-up after a first investor meeting

> Thank you for the discussion. The two questions I heard were [question one] and [question two]. We are addressing them through [specific customer test or product proof]. I have attached the short technical note we discussed and a link to the demo. I will send an update when [explicit milestone] is complete.

## 62. Founder FAQ

This section provides direct answers to questions that investors, candidates, partners, and the founders themselves are likely to ask.

### 62.1 Why JavaScript and Goja?

JavaScript is widely understood by models, developers, and frontend ecosystems. Goja embeds JavaScript inside a Go-owned runtime without requiring a separate V8 service or Node process for every application. More importantly, go-go-goja already provides explicit runtime ownership, native modules, generated xgoja profiles, asynchronous boundaries, and a secure HTTP framework. The company is not betting that Goja is the fastest general JavaScript engine. It is using Goja as a controllable language layer over high-value native capabilities.

CPU-heavy work should not run as arbitrary JavaScript. It should run in bounded native modules, external services, queues, or specialized infrastructure.

### 62.2 Why not just build on Node.js?

Node has a vast ecosystem but also a vast ambient dependency and authority surface. The product thesis requires a closed, reviewable module set, runtime-owned context, and application profiles constructed from selected native capabilities. Node can be used elsewhere in the system, but a general npm environment is not the safest default for untrusted agent-generated applications.

The semantic module architecture could eventually support other runtime targets. Goja is the first controlled execution substrate, not necessarily the only one forever.

### 62.3 Why will agents be better at this than ordinary app generation?

The platform reduces the number of operational choices and represents business operations directly. The claim should be tested quantitatively. Expected improvements include fewer generation iterations, smaller programs, fewer security defects, better static validation, easier tests, and more reliable upgrades. If those improvements do not appear, the product needs to change.

### 62.4 Is this simply an AI app builder?

It includes an app-building experience, but the differentiated product is the application substrate. Current builders generally generate conventional stacks and integrate lower-level services. This platform makes versioned semantic modules, permissions, resources, and professional release behavior the primary programming model.

### 62.5 Why cannot Replit, Lovable, v0, Wix, or a cloud provider copy this?

They can and will add high-level primitives. The company must build more than a feature. The durable system includes deep module semantics, operational edge cases, module economics, a compact program model, application and release outcome data, design recipes, studio distribution, provider relationships, and trust.

The company should assume competitors improve rapidly. It wins by focusing earlier, learning faster in selected workflows, and building a coherent ecosystem around the semantic runtime.

### 62.6 What is the initial customer?

The recommended first customer is an AI-native studio, agency, automation consultant, or technically ambitious operator that repeatedly needs custom operational applications. The first end-user workflows are booking, lightweight CRM, catalogs/search, quotes/orders, internal logistics, customer portals, and coordination.

### 62.7 Why not start with personal applications?

Personal apps are strategically important because they demonstrate just-in-time software and create sharing loops. They are a difficult first business due to low willingness to pay, privacy integrations, broad support needs, and consumer acquisition. They should be a bounded free or viral surface until their economics are proven.

### 62.8 Can the platform really support both a barbecue poll and a CRM?

The runtime and module principles can support both. The products have different support, compliance, pricing, and distribution requirements. The architecture can remain broad while the commercial message and launch segment remain narrow.

### 62.9 What is a premium module?

A premium module exposes a small application API over difficult, ongoing operational behavior. Examples include product search, booking, commerce, managed identity, messaging, document workflows, maps/routing, or logistics. Premium status is justified by recurring customer value, provider cost, operational responsibility, or specialized domain depth.

### 62.10 Why is product search a good example?

A simple `products.search()` API can hide indexing, ranking, typo tolerance, facets, tenant isolation, merchandising, analytics, cache invalidation, provider selection, quotas, and cost control. It is easy for an agent to use, valuable to many applications, and operationally substantial enough to support recurring revenue.

### 62.11 Are modules just API wrappers?

No. A useful module owns lifecycle and policy as well as transport. It may provision resources, maintain state, validate schemas, enforce permissions, manage retries and idempotency, emit usage, expose observability, and support version upgrades. A thin wrapper can be included, but it is not the primary moat.

### 62.12 Who builds the modules?

The company builds the first-party core and first premium catalog. Later, infrastructure providers, vertical experts, and third-party developers can build reviewed modules through a provider SDK. The marketplace should not launch until module lifecycle, billing, support, and security review are stable.

### 62.13 What happens when a module has a security bug?

Releases pin exact module versions. The platform can block new releases, notify affected customers, test a patched version, canary it, and promote controlled upgrades. Emergency policy can suspend a vulnerable module or application. Centralizing operational behavior makes a patch more scalable, but also increases correlated risk, which requires module-specific incident processes.

### 62.14 How does rollback work when data changes?

Code rollback and data rollback are separate. Releases should declare schema compatibility. Migrations should use expand/contract patterns, backups, and explicit approvals for destructive changes. The platform can route traffic back to an earlier compatible release, but it should not pretend that every database migration is automatically reversible.

### 62.15 Is customer JavaScript trusted?

No. The production model should treat tenant-authored code as untrusted and isolate it at the operating-system or sandbox boundary. Goja's controlled module surface reduces authority but is not a complete security boundary. Timeouts require interrupt and process termination, and workers that encounter unsafe states should be discarded.

### 62.16 Does the system expose arbitrary network access?

Not by default. Outbound HTTP is a capability with explicit origin policy, timeout, response limits, credential-source controls, metering, and audit. High-value integrations should use typed modules rather than arbitrary fetch whenever practical.

### 62.17 How are secrets handled?

Secrets remain in host-managed stores or provider bindings. JavaScript receives opaque handles or narrow operations, not raw long-lived credentials. Logs, prompts, request contexts, and audit records should be redacted and bounded.

### 62.18 How does application authentication work?

Platform users and hosted-application users are separate populations. The control plane authenticates customers and collaborators. Hosted apps can use managed identity realms, dedicated identity deployments, or external OIDC. The application receives verified, non-secret identity claims and declares route policy; Go owns credential validation, sessions, CSRF, and protocol operations.

### 62.19 Why is the HTTP framework differentiated?

The Express-style JavaScript API compiles route intent into a Go-owned plan. Before JavaScript executes, the host can apply authentication, principal requirements, CSRF, resource resolution, grant checks, authorization, rate limits, and audit. The same plan can protect Go handlers. This turns security policy into a reviewable application artifact rather than scattered handler code.

### 62.20 What is the UI strategy?

The platform supports static frontend assets and a versioned Widget DSL. In the Widget model, application code returns semantic, serializable UI intent. A renderer owns components, styling, state wiring, accessibility, and target behavior. This gives agents a smaller grammar and lets design improvements propagate across applications.

Unsafe arbitrary HTML can exist as a privileged capability, not the default safe UI contract.

### 62.21 Will customers be locked in?

Managed high-level modules create platform dependence, as every cloud platform does. Reduce harmful lock-in through source export, data export, release manifests, module locks, documented APIs, and clear ownership terms. Some managed semantics will require the platform runtime. That boundary should be explicit during sales.

### 62.22 Can customers self-host?

Not necessarily at launch. Self-hosting expands support, security, upgrade, and module-provider complexity. Enterprise dedicated deployments or a controlled runtime package can be offered when demand and economics justify them. The first product should optimize for a reliable managed service.

### 62.23 What is open source?

A possible strategy is to keep the runtime, module SDK, local development tools, and selected core modules open, while the managed control plane, premium modules, governance, billing, and marketplace are commercial. The exact boundary should maximize adoption and trust without giving away the entire managed economic layer.

Open source should have a product reason: developer trust, provider ecosystem, local development, or distribution. It should not be used as a substitute for go-to-market.

### 62.24 How does pricing work?

Internally, maintain separate ledgers for creation, runtime, modules, and contract entitlements. Externally, present simple packages. A studio might pay a builder subscription, a fee per active client application, and module usage. An enterprise might pay an annual platform contract with included application and usage capacity.

### 62.25 Why will gross margins be attractive?

Application programs are small, and Goja is efficient for orchestration workloads. Expensive behavior can be centralized, metered, and priced through modules. Margins depend on model generation cost, worker utilization, provider pass-through cost, support, and application traffic. The company must instrument them from the first pilots rather than assume infrastructure margins.

### 62.26 Is this a services business?

The launch uses paid services to discover repeated product patterns. The company remains a software business only if module reuse rises, delivery hours decline, recurring platform revenue grows, and partners can ship without founder intervention. Those metrics should be reviewed explicitly.

### 62.27 What is the marketplace opportunity?

Once there is application demand and a stable module contract, third parties can sell modules, templates, design systems, vertical packs, and expert services. The platform can provide installation, permissions, metering, billing, compatibility, review, and distribution. The marketplace is an expansion mechanism, not the day-one wedge.

### 62.28 What is the largest possible company?

The largest vision is a new application cloud in which software is created when needed rather than purchased from a fixed catalog. Individuals create personal tools; communities create temporary shared applications; businesses create systems around their exact operations; enterprises govern portfolios of employee- and agent-created software; providers distribute capabilities as modules.

The company captures value from creation, operation, modules, transactions, enterprise governance, and the ecosystem.

### 62.29 Why raise venture capital?

The platform requires simultaneous investment in runtime security, product experience, modules, application delivery, and distribution. A credible winner can become a large ecosystem company, but the market is moving quickly and competitors are well financed. Venture capital is appropriate if the founders want to pursue the broad platform outcome and can demonstrate a path to venture-scale distribution.

A narrower profitable studio or vertical software factory could be built with less capital. The financing choice should match the intended company.

### 62.30 What should the seed round prove?

The seed should prove that the architecture becomes a repeatable business:

- Paid customers use production applications.
- Agents create them faster and more reliably through semantic modules.
- Repeated workflows become modules and packs.
- Studios or direct customers provide a repeatable acquisition path.
- Application count and module revenue expand per customer.
- The worker and control plane meet a truthful production standard.
- The company can move toward self-service without services cost growing linearly.

### 62.31 Why this team?

The technical founder has already tackled runtime ownership, module composition, HTTP security, release control, identity, and isolation problems that most app-builder teams encounter later. The design founder has an effective product system and impressive demos. The team is adding commercial founder-level ownership deliberately rather than pretending technology alone creates a company.

### 62.32 What is the biggest unresolved question?

The largest unresolved question is distribution: which customer repeatedly pays for custom applications on this substrate, and which channel can acquire them efficiently? The design-partner and studio program exists to answer that question before the company scales the team.

---
EOF

```

## Turn 196 - assistant (thinking)

- Message ID: `70396740-d717-4de8-8f88-75a34e934662`

<details><summary>Thinking</summary>

**Drafted Part IX of the dossier and validated structure**


</details>

## Turn 197 - assistant (thinking)

- Message ID: `0bfc2892-d963-48ba-beaa-bd7ce77ddee8`
- Model: `gpt-5-6-pro`

<details><summary>Thinking</summary>

**Converting to DOCX**

I’m converting the detailed Markdown draft into a professional DOCX, ensuring all the sections and references are intact. The final goal is to deliver a polished document with proper styling and footnotes.

**Converted to DOCX**


</details>

## Turn 198 - assistant (tool call)

- Message ID: `1da69ec0-8db6-4a29-84c9-6dba84eb0cfa`
- Model: `gpt-5-6-pro`

```unknown
bash -lc ls -lh /mnt/data/agent_native_app_platform_founder_dossier.md /mnt/data/secure_goja_hosting_platform_textbook.docx /mnt/data/_founder_assets && wc -w -l /mnt/data/agent_native_app_platform_founder_dossier.md && sed -n '1,120p' /home/oai/skills/docx/SKILL.md
```

## Turn 199 - assistant (thinking)

- Message ID: `73a38e0f-178b-4528-8005-d07d0782e695`

<details><summary>Thinking</summary>

**Inspected and converted markdown to DOCX, generating footnotes report**


</details>

## Turn 200 - assistant (tool call)

- Message ID: `ef1f3b34-5320-40ea-94ea-927f7a305f94`
- Model: `gpt-5-6-pro`

```unknown
bash -lc cat > /mnt/data/postprocess_founder_dossier.py <<'PY'
from __future__ import annotations

from copy import deepcopy
from pathlib import Path

from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.table import WD_CELL_VERTICAL_ALIGNMENT, WD_ROW_HEIGHT_RULE
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK, WD_LINE_SPACING
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, RGBColor

SRC = Path('/mnt/data/agent_native_application_cloud_founder_dossier.raw.docx')
DST = Path('/mnt/data/agent_native_application_cloud_founder_dossier.docx')

doc = Document(SRC)

# --- Palette ---
NAVY = '17365D'
BLUE = '1F4E79'
MID_BLUE = '5B9BD5'
PALE_BLUE = 'EAF2F8'
VERY_PALE_BLUE = 'F5F9FC'
PALE_GRAY = 'F2F4F7'
MID_GRAY = 'D9E1F2'
DARK_GRAY = '404040'
WHITE = 'FFFFFF'
BORDER = 'B4C7E7'


def set_cell_shading(cell, fill: str) -> None:
    tcPr = cell._tc.get_or_add_tcPr()
    shd = tcPr.find(qn('w:shd'))
    if shd is None:
        shd = OxmlElement('w:shd')
        tcPr.append(shd)
    shd.set(qn('w:fill'), fill)
    shd.set(qn('w:val'), 'clear')


def set_cell_borders(cell, color: str = BORDER, size: str = '4') -> None:
    tcPr = cell._tc.get_or_add_tcPr()
    borders = tcPr.find(qn('w:tcBorders'))
    if borders is None:
        borders = OxmlElement('w:tcBorders')
        tcPr.append(borders)
    for edge in ('top', 'left', 'bottom', 'right', 'insideH', 'insideV'):
        tag = qn(f'w:{edge}')
        el = borders.find(tag)
        if el is None:
            el = OxmlElement(f'w:{edge}')
            borders.append(el)
        el.set(qn('w:val'), 'single')
        el.set(qn('w:sz'), size)
        el.set(qn('w:space'), '0')
        el.set(qn('w:color'), color)


def set_cell_margins(cell, top=70, start=90, bottom=70, end=90) -> None:
    tc = cell._tc
    tcPr = tc.get_or_add_tcPr()
    tcMar = tcPr.find(qn('w:tcMar'))
    if tcMar is None:
        tcMar = OxmlElement('w:tcMar')
        tcPr.append(tcMar)
    for m, v in [('top', top), ('start', start), ('bottom', bottom), ('end', end)]:
        node = tcMar.find(qn(f'w:{m}'))
        if node is None:
            node = OxmlElement(f'w:{m}')
            tcMar.append(node)
        node.set(qn('w:w'), str(v))
        node.set(qn('w:type'), 'dxa')


def set_repeat_table_header(row) -> None:
    trPr = row._tr.get_or_add_trPr()
    tblHeader = trPr.find(qn('w:tblHeader'))
    if tblHeader is None:
        tblHeader = OxmlElement('w:tblHeader')
        trPr.append(tblHeader)
    tblHeader.set(qn('w:val'), 'true')


def prevent_row_split(row) -> None:
    trPr = row._tr.get_or_add_trPr()
    cantSplit = trPr.find(qn('w:cantSplit'))
    if cantSplit is None:
        cantSplit = OxmlElement('w:cantSplit')
        trPr.append(cantSplit)


def add_paragraph_border_and_shading(paragraph, fill=VERY_PALE_BLUE, border=BLUE) -> None:
    pPr = paragraph._p.get_or_add_pPr()
    shd = pPr.find(qn('w:shd'))
    if shd is None:
        shd = OxmlElement('w:shd')
        pPr.append(shd)
    shd.set(qn('w:fill'), fill)
    shd.set(qn('w:val'), 'clear')

    pBdr = pPr.find(qn('w:pBdr'))
    if pBdr is None:
        pBdr = OxmlElement('w:pBdr')
        pPr.append(pBdr)
    left = pBdr.find(qn('w:left'))
    if left is None:
        left = OxmlElement('w:left')
        pBdr.append(left)
    left.set(qn('w:val'), 'single')
    left.set(qn('w:sz'), '18')
    left.set(qn('w:space'), '8')
    left.set(qn('w:color'), border)


def add_field(run, instruction: str) -> None:
    fldChar1 = OxmlElement('w:fldChar')
    fldChar1.set(qn('w:fldCharType'), 'begin')
    instrText = OxmlElement('w:instrText')
    instrText.set(qn('xml:space'), 'preserve')
    instrText.text = instruction
    fldChar2 = OxmlElement('w:fldChar')
    fldChar2.set(qn('w:fldCharType'), 'end')
    run._r.append(fldChar1)
    run._r.append(instrText)
    run._r.append(fldChar2)


def set_run_font(run, name=None, size=None, bold=None, italic=None, color=None) -> None:
    if name:
        run.font.name = name
        rPr = run._r.get_or_add_rPr()
        rFonts = rPr.rFonts
        if rFonts is None:
            rFonts = OxmlElement('w:rFonts')
            rPr.insert(0, rFonts)
        for attr in ('ascii', 'hAnsi', 'eastAsia', 'cs'):
            rFonts.set(qn(f'w:{attr}'), name)
    if size:
        run.font.size = Pt(size)
    if bold is not None:
        run.bold = bold
    if italic is not None:
        run.italic = italic
    if color:
        run.font.color.rgb = RGBColor.from_string(color)


# --- Page geometry and section behavior ---
for section in doc.sections:
    section.page_width = Inches(8.5)
    section.page_height = Inches(11)
    section.top_margin = Inches(0.72)
    section.bottom_margin = Inches(0.72)
    section.left_margin = Inches(0.82)
    section.right_margin = Inches(0.82)
    section.header_distance = Inches(0.30)
    section.footer_distance = Inches(0.32)
    section.different_first_page_header_footer = True

# --- Document properties ---
props = doc.core_properties
props.title = 'From Intent to Production Software'
props.subject = 'Founder strategy, business model, go-to-market, and seed fundraising playbook for an agent-native application cloud'
props.author = 'Founding team'
props.keywords = 'agent-native application cloud, JavaScript, LLM application generation, seed fundraising, founder strategy'
props.comments = 'Confidential working founder dossier prepared July 20, 2026.'

# --- Base styles ---
styles = doc.styles

if 'Normal' in styles:
    normal = styles['Normal']
    normal.font.name = 'Aptos'
    normal.font.size = Pt(10)
    normal.font.color.rgb = RGBColor.from_string(DARK_GRAY)
    normal.paragraph_format.space_after = Pt(5)
    normal.paragraph_format.line_spacing = 1.12
    normal.paragraph_format.widow_control = True

for style_name in ('Body Text', 'First Paragraph'):
    if style_name in styles:
        style = styles[style_name]
        style.font.name = 'Aptos'
        style.font.size = Pt(10)
        style.font.color.rgb = RGBColor.from_string(DARK_GRAY)
        style.paragraph_format.space_after = Pt(5)
        style.paragraph_format.line_spacing = 1.12
        style.paragraph_format.widow_control = True

if 'Compact' in styles:
    style = styles['Compact']
    style.font.name = 'Aptos'
    style.font.size = Pt(9.6)
    style.font.color.rgb = RGBColor.from_string(DARK_GRAY)
    style.paragraph_format.space_after = Pt(1.5)
    style.paragraph_format.line_spacing = 1.05
    style.paragraph_format.widow_control = True

if 'Title' in styles:
    style = styles['Title']
    style.font.name = 'Aptos Display'
    style.font.size = Pt(30)
    style.font.bold = True
    style.font.color.rgb = RGBColor.from_string(NAVY)
    style.paragraph_format.space_before = Pt(112)
    style.paragraph_format.space_after = Pt(14)
    style.paragraph_format.keep_with_next = True

if 'Subtitle' in styles:
    style = styles['Subtitle']
    style.font.name = 'Aptos'
    style.font.size = Pt(15)
    style.font.color.rgb = RGBColor.from_string(BLUE)
    style.paragraph_format.space_after = Pt(24)
    style.paragraph_format.keep_with_next = True

heading_specs = {
    'Heading 1': (21, NAVY, 0, 11),
    'Heading 2': (15.5, BLUE, 11, 5),
    'Heading 3': (12.2, NAVY, 8, 3),
    'Heading 4': (10.6, BLUE, 6, 2),
}
for name, (size, color, before, after) in heading_specs.items():
    if name in styles:
        style = styles[name]
        style.font.name = 'Aptos Display' if name in ('Heading 1', 'Heading 2') else 'Aptos'
        style.font.size = Pt(size)
        style.font.bold = True
        style.font.color.rgb = RGBColor.from_string(color)
        style.paragraph_format.space_before = Pt(before)
        style.paragraph_format.space_after = Pt(after)
        style.paragraph_format.keep_with_next = True
        style.paragraph_format.keep_together = True
        style.paragraph_format.widow_control = True
        if name == 'Heading 1':
            style.paragraph_format.page_break_before = True

if 'Block Text' in styles:
    style = styles['Block Text']
    style.font.name = 'Aptos'
    style.font.size = Pt(10)
    style.font.color.rgb = RGBColor.from_string(NAVY)
    style.paragraph_format.left_indent = Inches(0.22)
    style.paragraph_format.right_indent = Inches(0.08)
    style.paragraph_format.space_before = Pt(5)
    style.paragraph_format.space_after = Pt(6)
    style.paragraph_format.line_spacing = 1.08
    style.paragraph_format.widow_control = True

if 'Source Code' in styles:
    style = styles['Source Code']
    style.font.name = 'Consolas'
    style.font.size = Pt(8.2)
    style.font.color.rgb = RGBColor.from_string('202020')
    style.paragraph_format.space_before = Pt(3)
    style.paragraph_format.space_after = Pt(5)
    style.paragraph_format.line_spacing_rule = WD_LINE_SPACING.SINGLE
    style.paragraph_format.left_indent = Inches(0.12)
    style.paragraph_format.right_indent = Inches(0.08)
    style.paragraph_format.widow_control = False

for foot_name in ('Footnote Text', 'Footnote Reference'):
    if foot_name in styles:
        styles[foot_name].font.name = 'Aptos'
        styles[foot_name].font.size = Pt(8)
        styles[foot_name].font.color.rgb = RGBColor.from_string(DARK_GRAY)

for cap_name in ('Caption', 'Image Caption'):
    if cap_name in styles:
        style = styles[cap_name]
        style.font.name = 'Aptos'
        style.font.size = Pt(8.8)
        style.font.italic = True
        style.font.color.rgb = RGBColor.from_string(DARK_GRAY)
        style.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
        style.paragraph_format.space_before = Pt(2)
        style.paragraph_format.space_after = Pt(8)
        style.paragraph_format.keep_with_next = False
        style.paragraph_format.keep_together = True

# --- Cover page ---
paras = doc.paragraphs
if len(paras) >= 3:
    paras[0].style = styles['Title']
    paras[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
    paras[1].style = styles['Subtitle']
    paras[1].alignment = WD_ALIGN_PARAGRAPH.CENTER

    cover_meta = paras[2]
    cover_meta.alignment = WD_ALIGN_PARAGRAPH.CENTER
    cover_meta.paragraph_format.space_before = Pt(8)
    cover_meta.paragraph_format.space_after = Pt(0)
    cover_meta.paragraph_format.line_spacing = 1.35
    for run in cover_meta.runs:
        set_run_font(run, name='Aptos', size=9.5, color=DARK_GRAY)
    # Add a restrained confidentiality line above the metadata.
    p = OxmlElement('w:p')
    paras[2]._p.addprevious(p)
    from docx.text.paragraph import Paragraph
    conf = Paragraph(p, paras[2]._parent)
    conf.alignment = WD_ALIGN_PARAGRAPH.CENTER
    conf.paragraph_format.space_after = Pt(9)
    run = conf.add_run('CONFIDENTIAL · WORKING FOUNDER DOSSIER')
    set_run_font(run, name='Aptos', size=9, bold=True, color=BLUE)
    # Page break after cover metadata.
    cover_meta.add_run().add_break(WD_BREAK.PAGE)

# --- Paragraph-level refinement ---
for para in doc.paragraphs:
    sname = para.style.name if para.style else ''
    if sname == 'Block Text':
        add_paragraph_border_and_shading(para)
    elif sname == 'Source Code':
        pPr = para._p.get_or_add_pPr()
        shd = pPr.find(qn('w:shd'))
        if shd is None:
            shd = OxmlElement('w:shd')
            pPr.append(shd)
        shd.set(qn('w:fill'), PALE_GRAY)
        shd.set(qn('w:val'), 'clear')
        pBdr = pPr.find(qn('w:pBdr'))
        if pBdr is None:
            pBdr = OxmlElement('w:pBdr')
            pPr.append(pBdr)
        for edge in ('top', 'left', 'bottom', 'right'):
            el = OxmlElement(f'w:{edge}')
            el.set(qn('w:val'), 'single')
            el.set(qn('w:sz'), '3')
            el.set(qn('w:space'), '3')
            el.set(qn('w:color'), 'D9D9D9')
            pBdr.append(el)
    elif sname in ('Captioned Figure',):
        para.alignment = WD_ALIGN_PARAGRAPH.CENTER
        para.paragraph_format.space_before = Pt(5)
        para.paragraph_format.space_after = Pt(1)
        para.paragraph_format.keep_with_next = True
        para.paragraph_format.keep_together = True
    elif sname == 'Image Caption':
        para.style = styles['Caption'] if 'Caption' in styles else para.style
        para.alignment = WD_ALIGN_PARAGRAPH.CENTER

# Keep headings with following content and avoid lonely list labels.
for para in doc.paragraphs:
    if para.style and para.style.name.startswith('Heading'):
        para.paragraph_format.keep_with_next = True
        para.paragraph_format.keep_together = True
    if para.text.strip() in {'The key points to internalize:', 'Founder decision:', 'Investor implication:', 'Operating rule:'}:
        para.paragraph_format.keep_with_next = True

# --- Images: fit, center, and add alt descriptions from captions ---
max_width = Inches(6.45)
for shape in doc.inline_shapes:
    if shape.width > max_width:
        ratio = max_width / shape.width
        shape.width = max_width
        shape.height = int(shape.height * ratio)

# Add title/description to drawing docPr using adjacent caption when available.
for i, para in enumerate(doc.paragraphs):
    drawings = para._p.xpath('.//wp:docPr')
    if not drawings:
        continue
    caption = ''
    if i + 1 < len(doc.paragraphs):
        caption = doc.paragraphs[i + 1].text.strip()
    if not caption:
        caption = 'Founder strategy diagram'
    for docPr in drawings:
        docPr.set('title', caption)
        docPr.set('descr', caption)

# --- Tables: readable, investor-grade formatting ---
for table in doc.tables:
    table.autofit = True
    if table.rows:
        set_repeat_table_header(table.rows[0])
    for r_idx, row in enumerate(table.rows):
        prevent_row_split(row)
        row.height_rule = WD_ROW_HEIGHT_RULE.AT_LEAST
        for cell in row.cells:
            cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.TOP
            set_cell_margins(cell)
            set_cell_borders(cell)
            if r_idx == 0:
                set_cell_shading(cell, BLUE)
            elif r_idx % 2 == 0:
                set_cell_shading(cell, VERY_PALE_BLUE)
            else:
                set_cell_shading(cell, WHITE)
            for p in cell.paragraphs:
                p.paragraph_format.space_before = Pt(0)
                p.paragraph_format.space_after = Pt(2.5)
                p.paragraph_format.line_spacing = 1.02
                p.paragraph_format.widow_control = False
                for run in p.runs:
                    set_run_font(
                        run,
                        name='Aptos',
                        size=8.7,
                        bold=True if r_idx == 0 else None,
                        color=WHITE if r_idx == 0 else DARK_GRAY,
                    )

# --- Header/footer and page numbers ---
for section in doc.sections:
    header = section.header
    hp = header.paragraphs[0]
    hp.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    hp.paragraph_format.space_after = Pt(0)
    hr = hp.add_run('FROM INTENT TO PRODUCTION SOFTWARE')
    set_run_font(hr, name='Aptos', size=7.5, bold=True, color=BLUE)

    footer = section.footer
    fp = footer.paragraphs[0]
    fp.alignment = WD_ALIGN_PARAGRAPH.CENTER
    fp.paragraph_format.space_before = Pt(0)
    fp.paragraph_format.space_after = Pt(0)
    fr = fp.add_run('Confidential founder dossier  ·  July 2026  ·  ')
    set_run_font(fr, name='Aptos', size=7.5, color='666666')
    pr = fp.add_run()
    set_run_font(pr, name='Aptos', size=7.5, color='666666')
    add_field(pr, 'PAGE')

# Ensure first-page header/footer are empty.
for section in doc.sections:
    fh = section.first_page_header
    if fh.paragraphs:
        fh.paragraphs[0].text = ''
    ff = section.first_page_footer
    if ff.paragraphs:
        ff.paragraphs[0].text = ''

# Update fields when opened in Word.
settings = doc.settings._element
update = settings.find(qn('w:updateFields'))
if update is None:
    update = OxmlElement('w:updateFields')
    settings.append(update)
update.set(qn('w:val'), 'true')

# Avoid title page headings inheriting page-break-before from former Heading styles.
doc.paragraphs[0].paragraph_format.page_break_before = False
doc.paragraphs[1].paragraph_format.page_break_before = False

# Save.
doc.save(DST)
print(DST)
PY
python /mnt/data/postprocess_founder_dossier.py
ls -lh /mnt/data/agent_native_application_cloud_founder_dossier.docx
```

## Turn 201 - assistant (thinking)

- Message ID: `b4332dad-ae32-4780-87b7-d03f91b35e8d`

<details><summary>Thinking</summary>

**Processed and formatted founder dossier document, audited and inspected file integrity, checked markdown, parsed headers, edited contents, and generated PDF**


</details>

## Turn 202 - assistant (tool call)

- Message ID: `5e735e89-53aa-43c7-bfa3-3c929b61852b`
- Model: `gpt-5-6-pro`

```unknown
bash -lc set -e
python /home/oai/skills/docx/scripts/a11y_audit.py /mnt/data/agent_native_application_cloud_founder_dossier.docx
printf '\n--- HEADING AUDIT ---\n'
python /home/oai/skills/docx/scripts/heading_audit.py /mnt/data/agent_native_application_cloud_founder_dossier.docx
printf '\n--- IMAGES AUDIT ---\n'
python /home/oai/skills/docx/scripts/images_audit.py /mnt/data/agent_native_application_cloud_founder_dossier.docx
printf '\n--- FILE STATS ---\n'
stat -c '%n %s bytes' /mnt/data/agent_native_application_cloud_founder_dossier.docx /mnt/data/agent_native_application_cloud_founder_dossier.md
wc -w /mnt/data/agent_native_application_cloud_founder_dossier.md
pdfinfo /mnt/data/founder_dossier_render/agent_native_application_cloud_founder_dossier.pdf | grep -E 'Pages|Page size|File size'
```

## Turn 203 - assistant

- Message ID: `ea69ab51-a2b5-4781-b156-dc07591c2239`
- Model: `gpt-5-6-pro`

The founder dossier is complete, including seed deck, financing, cofounder process, falsifiable milestones, objections, and diligence materials. Formatting issues are fixed; final source and accessibility audits remain.

## Turn 204 - assistant (thinking)

- Message ID: `1dd54348-48b0-4ab8-a133-a14906f7e2c2`

<details><summary>Thinking</summary>

**Used container tool**


</details>

## Turn 205 - assistant (recap)

- Message ID: `67b7f515-bbb0-5bc2-87ff-81bf7ea4755d`

> _Worked for 49m 39s_

## Turn 206 - assistant

- Message ID: `d3863e91-bd86-4038-9510-f798f6bc92d1`
- Model: `gpt-5-6-pro`

# Founder and Seed Strategy Dossier

Completed. This is now a **122-page, 33,824-word founder dossier** built to support company formation, commercial validation, cofounder recruitment, and seed fundraising—not merely a longer technical pitch.

The manuscript follows a foundation-first structure: it establishes why the company should exist, explains the economic and operational problem it solves, and then develops product, market, business-model, execution, and fundraising decisions through concrete examples, models, diagrams, and decision records. fileciteturn148file0L10-L16

## Central business thesis

The document sharpens the company around this claim:

> **Coding agents can already generate substantial amounts of code. The missing product is an application substrate whose semantics are compact enough for agents to use reliably and operationally complete enough for real businesses to trust.**

Instead of making an LLM repeatedly generate authentication, permissions, payment flows, indexing, retries, tenancy, deployment, migrations, rollback, monitoring, and infrastructure glue, the platform exposes those systems through small, versioned JavaScript APIs.

A generated application therefore becomes mostly a description of business behavior:

```javascript
const app = require("app");
const products = require("products");
const payments = require("payments");

app.get("/search")
  .public()
  .handle(async (ctx, res) => {
    const results = await products.search({
      query: ctx.request.query.q,
      filters: ctx.request.query.filters,
    });

    res.json(results);
  });

app.post("/checkout")
  .auth(app.sessionUser())
  .csrf()
  .allow("checkout.create")
  .audit("checkout.created")
  .handle(async (ctx, res) => {
    const checkout = await payments.checkout.create({
      customer: ctx.actor.id,
      items: ctx.body.items,
    });

    res.json(checkout);
  });
```

The small program denotes a large amount of host-owned operational behavior. That translation layer is the product.

## Main conclusions developed in the dossier

The recommended initial commercial wedge is **AI-native studios, agencies, automation consultants, and technically ambitious operators that repeatedly deliver custom operational applications**. They provide recurring workflows, shorter sales cycles, direct evidence of delivery-time reduction, and a natural path from paid design work to reusable product modules.

The proposed revenue architecture separates four ledgers:

1. **Builder revenue** for generation, collaboration, testing, previews, and release tooling.
2. **Application runtime revenue** for each active production application and its resource consumption.
3. **Premium-module revenue** for capabilities such as product search, managed identity, booking, commerce, messaging, logistics, and document workflows.
4. **Enterprise and ecosystem revenue** for governance, private deployments, support, provider modules, vertical packs, and marketplace transactions.

This is deliberately not positioned as unlimited generation for one flat fee. The company creates value when applications are created, when they remain active, and when they consume managed operational semantics.

The financing recommendation is to **prepare a credible case for approximately a $3.5 million seed round while allowing the evidence to determine whether the first financing is labeled pre-seed or seed**. The strongest fundraising trigger is not another technical milestone. It is a combination of:

- Paid design partners.
- Real production applications.
- Measured reductions in delivery time and repair cycles.
- Repeated use of the same semantic modules.
- Early recurring runtime or module revenue.
- Evidence that studios can deliver applications without continuous founder intervention.

The commercial-founder recommendation is also specific: do not recruit a generic “business person.” Recruit either a **CEO/GTM cofounder** or a genuinely founder-level commercial executive capable of owning market selection, customer development, design partnerships, pricing, company narrative, recruiting, and fundraising. The document proposes a six-week working trial with actual customers, pipeline work, pricing decisions, and pitch meetings before making a permanent founder commitment.

## What the document contains

The dossier is organized into nine parts and three appendices:

- **Company thesis:** the category, long-term vision, core customer promise, and reasons the timing may be favorable.
- **Product as a business:** semantic modules, application profiles, release semantics, UI strategy, identity, payments, product search, and the existing secure HTTP framework.
- **Market and competition:** customer segmentation, initial wedge, competitor map, alternative categories, differentiation, and defensibility.
- **Business models and pricing:** builder plans, application fees, metering, premium modules, enterprise contracts, marketplace economics, services boundaries, and illustrative cohort models.
- **Go-to-market:** design partners, studios and agencies, direct customers, personal and friend-shared applications, vertical packs, channel strategy, sales process, onboarding, retention, and expansion.
- **Seed fundraising:** financing readiness, round sizing, use of funds, milestone design, investor selection, diligence, narrative construction, and common objections.
- **Founding team:** role architecture, the commercial-founder search, working trials, equity, vesting, authority, governance, advisors, and conflict management.
- **Execution plan:** the first 90 days, 12- and 24-month roadmap, hiring sequence, experiments, proof gates, metrics, risks, incident response, and pivot criteria.
- **Reusable pitch assets:** one-sentence, 30-second, two-minute, and ten-minute pitches; an investor one-pager; outreach messages; design-partner messages; cofounder outreach; and a 32-question founder FAQ.
- **Appendices:** market source register, financial and pricing assumptions, metrics definitions, dilution examples, and 100 structured cofounder discussion questions.

The Word edition was rendered and inspected across all 122 pages. The final accessibility audit found no high-, medium-, or low-severity issues. Market, financing, competitor, and pricing evidence is dated **July 20, 2026** and is clearly separated from internal hypotheses so it can be refreshed before external circulation.

## Files

[Download the formatted founder and seed dossier](sandbox:/mnt/data/agent_native_application_cloud_founder_dossier.docx)

[Download the editable Markdown source](sandbox:/mnt/data/agent_native_application_cloud_founder_dossier.md)

## Turn 207 - user

- Message ID: `daa01dea-0831-4bd2-82d8-7ffa459ef33f`
- Attachment: SKILL(4).md

write a textbook style document that walks an intern through the systema dn its principles and concepts and implementations and how the decisions were made and all. Also, go-go-goja has an extensive HTTP framework to build secure web applications.

## Turn 208 - assistant (thinking)

- Message ID: `9a3215a5-ddfc-490a-8363-d5a4c2f07f5e`
- Model: `gpt-5-6-pro`

<details><summary>Thinking</summary>

**Clarifying document format**

It seems the user is asking for a formal textbook-style document, but the format isn't clear. I’ll likely create a substantial markdown document based on the uploaded file and include citations accordingly.

**Planning document format**

I’m thinking of creating both a markdown and a document file. I’ll incorporate the HTTP framework details the user mentioned and use the uploaded guide for authorship. This will be a detailed textbook-style doc.

**Planned and clarified document format**


</details>

## Turn 209 - assistant (tool call)

- Message ID: `36427598-43eb-4dd9-ba94-94d3ec8363d2`
- Model: `gpt-5-6-pro`

```unknown
bash -lc cat /home/oai/skills/docx/SKILL.md
```

