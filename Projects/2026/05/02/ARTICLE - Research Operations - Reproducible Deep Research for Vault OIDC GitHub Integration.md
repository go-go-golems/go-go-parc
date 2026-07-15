---
title: "Research Operations: Reproducible Deep Research for Vault OIDC GitHub Integration"
aliases:
  - Reproducible Vault OIDC Research
  - Deep Research Workflow for Vault OIDC GitHub Integration
  - Web Research Playbook for Infrastructure Design
  - HK3S-0028 Research Operations Report
tags:
  - article
  - research-operations
  - vault
  - github-actions
  - oidc
  - github-apps
  - ci-cd
  - docmgr
  - obsidian
status: active
type: article
created: 2026-05-02
repo: /home/manuel/code/wesen/2026-03-27--hetzner-k3s
related:
  - /home/manuel/code/wesen/2026-03-27--hetzner-k3s/ttmp/2026/05/02/HK3S-0028--enable-github-actions-oidc-access-to-vault
  - /home/manuel/code/wesen/obsidian-vault/Projects/2026/05/02/ARTICLE - Vault OIDC for GitHub Actions - Secretless CI GitOps.md
  - /home/manuel/code/wesen/obsidian-vault/Projects/2026/05/02/ARTICLE - Research - Vault OIDC and Short-Lived GitHub App Tokens for GitOps PR Automation.md
---

# Research Operations: Reproducible Deep Research for Vault OIDC GitHub Integration

This is the reproducible-research and ticket-evidence branch of the [[docmgr]] project map.

This report documents the research workflow used for the Vault OIDC GitHub Actions integration and the follow-up GitHub App installation-token design. It is not primarily about the final architecture. It is about how the research was performed, how sources were collected, how tool outputs were preserved, how conclusions were checked against implementation reality, and how future research projects can repeat the pattern.

> [!summary]
> - The research combined local code inspection, ticket-managed documentation, web search, source extraction, LLM synthesis, live infrastructure validation, and durable Obsidian reporting.
> - The important operational rule was to keep raw sources, prompts, scripts, and final synthesis together so the reasoning path could be retraced.
> - Web search was used for discovery, Defuddle was used for clean source capture, ChatGPT was used as a second-pass synthesis engine, and local implementation/testing was used as the final arbiter.
> - The resulting pattern is reusable for future infrastructure research: create a ticket, collect sources into `sources/`, store prompts and collection scripts in `scripts/`, write a diary, synthesize a report, validate against the live system, and commit the artifacts.

## Why this note exists

The Vault OIDC GitHub Actions work was both an implementation project and a research project. The implementation goal was clear: allow trusted GitHub Actions workflows to authenticate to Vault without long-lived GitHub repository secrets. The research goal evolved as the work progressed: understand how GitHub Actions OIDC, Vault JWT auth, reusable workflows, GitOps PR credentials, Terraform ownership, and GitHub App installation tokens should fit together.

A future research project should not have to rediscover the workflow. This note captures the method as a reusable playbook.

The key lesson is that good infrastructure research is not just reading documentation. It is a controlled loop:

```text
question
  -> local facts
  -> external sources
  -> clean source archive
  -> promptable source set
  -> synthesis
  -> implementation hypothesis
  -> live validation
  -> durable report
  -> committed artifact trail
```

Each step changes the quality of the next step. Local facts prevent generic advice. External sources prevent guessing. Clean source archives preserve evidence. LLM synthesis accelerates comparison. Live validation catches false confidence. Durable reports make the work reusable.

## The concrete project context

The project ticket was:

```text
HK3S-0028--enable-github-actions-oidc-access-to-vault
```

The main ticket workspace was:

```text
/home/manuel/code/wesen/2026-03-27--hetzner-k3s/ttmp/2026/05/02/HK3S-0028--enable-github-actions-oidc-access-to-vault
```

The final implementation connected these systems:

- GitHub Actions OIDC issuer: `https://token.actions.githubusercontent.com`
- Vault JWT auth mount: `auth/github-actions`
- Vault address: `https://vault.yolo.scapegoat.dev`
- Source repositories:
  - `wesen/2026-05-01--bot-signup`
  - `wesen/hair-booking`
- GitOps repository:
  - `wesen/2026-03-27--hetzner-k3s`
- Shared workflow repository:
  - `/home/manuel/code/wesen/corporate-headquarters/infra-tooling`
- Terraform owner:
  - `/home/manuel/code/wesen/terraform/vault/github-actions/envs/k3s`

The research did not stay abstract. Every major design claim had to survive contact with at least one of these repos or the live cluster.

## Research questions

The research was organized around progressively sharper questions.

### First question: Can GitHub Actions authenticate to Vault without repository secrets?

This required understanding:

- GitHub's OIDC token issuance model,
- required workflow permissions such as `id-token: write`,
- Vault JWT auth configuration,
- Vault role binding to GitHub OIDC claims,
- safe Vault token TTLs,
- minimum Vault policies for CI.

The output was a script-first bootstrap and validation path, then a Terraform-owned steady state.

### Second question: How should the pattern be reused across repositories?

Once `bot-signup` worked, the question became whether this was a one-off workflow edit or a reusable platform pattern. This drove the move into shared `infra-tooling`.

This required researching and validating:

- reusable GitHub Actions workflows,
- workflow inputs and token-source modes,
- claim binding when the source repository calls a shared workflow,
- how `job_workflow_ref` can be used to bind Vault access to the approved reusable workflow.

### Third question: What remains static after Vault OIDC is complete?

The implementation removed the GitHub repository secret, but the GitHub PR token was still a static value stored in Vault. The next research question was therefore:

```text
How do we replace the Vault-stored static GitHub PR token with a short-lived GitHub credential?
```

This led to the GitHub App installation-token research and the broker design comparison.

## Tools used

The research used different tools for different jobs. The important point is that each tool had a bounded role.

| Tool | Role in the research | Output preserved |
|---|---|---|
| `rg`, `find`, file reads | Inspect local repositories, workflows, scripts, Vault policies, docs, and ticket state. | Code references and report sections. |
| `docmgr` | Create and maintain the ticket workspace, diary, changelog, tasks, and validation. | `ttmp/.../HK3S-0028...` docs. |
| `surf kagi search` | Discover external sources and compare search result sets. | `sources/*.kagi.md`. |
| `defuddle parse --md` | Download clean Markdown versions of key web pages without navigation clutter. | `sources/*.defuddle.md`. |
| `surf chatgpt ask` | Produce a second-pass synthesis from the collected context and prompt. | `sources/chatgpt-*.md` and raw JSON. |
| `vault` CLI | Verify live Vault auth, policies, roles, and secret paths. | Diary evidence and validation commands. |
| `gh` CLI | Verify workflow runs and GitOps PRs. | Diary evidence and PR references. |
| `kubectl` | Validate Argo CD sync and application health. | Diary evidence and rollout proof. |
| `terraform` | Import and prove steady-state Vault resource ownership. | Terraform plan/apply evidence. |
| Obsidian vault | Store durable project reports and reusable playbooks. | `Projects/2026/05/02/*.md`. |
| Git | Preserve the research and implementation artifacts in commits. | K3s and Obsidian commits. |

This division of labor kept the research grounded. Search found sources. Defuddle preserved them. ChatGPT synthesized them. The local tools proved or disproved the synthesis.

## The ticket as the research container

The first operational decision was to put the work into a docmgr ticket. This gave the research a stable filesystem home and a standard structure.

The ticket held four kinds of records:

```text
index.md        high-level status and links
tasks.md        checklist and completion state
changelog.md    timestamped changes and related files
reference/      diary, reports, and long-lived reference documents
```

When the research deepened, two more directories became important:

```text
sources/        external source captures and model outputs
scripts/        collection scripts, prompts, and replay commands
```

This mattered because source collection otherwise becomes invisible. A final report can say that a design is based on GitHub documentation, Vault documentation, and a plugin README, but without local source captures a future reader cannot tell which exact documents were consulted or how they were interpreted.

The ticket structure made the research replayable:

```text
read scripts/
  -> see which searches and parses were run
read sources/
  -> inspect raw source material
read reference/01-investigation-diary.md
  -> see chronological decisions, commands, failures, and validations
read reference/03-*.md
  -> read the synthesized design
```

## Local-first research

The research started from the actual repository state rather than from general web advice. This avoided a common failure mode: designing a clean architecture that does not match the real workflows.

Local inspection answered questions such as:

- Which source repositories already publish images?
- Where is the GitOps PR token used?
- How does the GitOps repository organize manifests?
- What does `infra-tooling` already provide?
- Where should Vault bootstrap scripts live?
- What should Terraform eventually own?
- Which docs and playbooks need to be updated?

The local repositories were the specification. External sources were used to fill gaps and confirm platform behavior.

The most important local paths were:

```text
/home/manuel/code/wesen/2026-03-27--hetzner-k3s
/home/manuel/code/wesen/2026-05-01--bot-signup
/home/manuel/code/wesen/hair-booking
/home/manuel/code/wesen/corporate-headquarters/infra-tooling
/home/manuel/code/wesen/terraform
```

This local-first step also established implementation constraints:

- the K3s repo already owned Vault bootstrap scripts and platform runbooks,
- source repos needed minimal workflow changes,
- future repos should use shared `infra-tooling`,
- live Vault resources should not remain script-only forever,
- the final stable state should be represented in Terraform.

## Web search as discovery, not authority

`surf kagi search` was used to discover relevant source pages and alternative designs. Search output was not treated as authoritative by itself. It was a map of likely sources.

The search themes were:

```text
GitHub Actions OIDC Vault JWT auth
GitHub Actions OIDC reusable workflow job_workflow_ref
GitHub App installation token GitOps PR automation
Vault GitHub secrets engine GitHub App installation tokens
GitHub App token permissions contents pull requests
```

The useful search outputs were saved as Kagi Markdown files in the ticket:

```text
sources/kagi-oidc-vault.kagi.md
sources/kagi-github-app-token.kagi.md
sources/kagi-vault-github-plugin.kagi.md
sources/kagi-oidc-best-practices.kagi.md
sources/kagi-github-app-permissions.kagi.md
```

Saving these files served three purposes:

1. It captured what was discoverable at the time of research.
2. It recorded why certain pages were selected for deeper reading.
3. It made the research path auditable without rerunning search.

Search results were not the final evidence. They led to primary docs, source repositories, and focused articles that were then downloaded with Defuddle.

## Defuddle as source preservation

Web pages are noisy. They contain navigation, sidebars, repeated headers, cookie banners, and rendering-specific markup. For research, the useful unit is usually the clean article or documentation body. Defuddle was used to convert selected web pages into stable Markdown source files.

The pattern was:

```bash
defuddle parse <url> --md -o sources/<short-name>.defuddle.md
```

The important Defuddle captures included:

```text
sources/github-oidc-reference.defuddle.md
sources/github-oidc-vault.defuddle.md
sources/github-oidc-reusable-workflows.defuddle.md
sources/github-create-app-token-action.defuddle.md
sources/github-generate-installation-token-docs.defuddle.md
sources/vault-jwt-auth-docs.defuddle.md
sources/vault-retrieve-secrets-github-actions.defuddle.md
sources/vault-plugin-secrets-github-readme.defuddle.md
sources/ephemeral-github-tokens-via-vault.defuddle.md
```

The captured sources were then searchable with `rg`. This made it easy to extract evidence for specific design points:

```bash
rg -n "job_workflow_ref|workflow_ref|bound_claims|installation access token|expires" sources/
```

This is one of the most useful parts of the workflow. Once sources are local Markdown files, they become part of the same research workspace as code. They can be grepped, diffed, summarized, quoted, and committed.

## ChatGPT as a synthesis tool

`surf chatgpt` was used after the source set existed. That ordering is important. The model was not asked for a generic answer first. It was asked to reason over a prompt and the collected context.

The prompt was stored as:

```text
scripts/chatgpt-github-app-token-research.prompt.md
```

The runner script was stored as:

```text
scripts/run-chatgpt-github-app-token-research.sh
```

The outputs were stored as:

```text
sources/chatgpt-github-app-token-research.md
sources/chatgpt-github-app-token-research.raw.json
sources/chatgpt-github-app-token-research-clean.md
```

There was an early command failure:

```text
Error: query required unless --list-models is set
```

That failure was useful. It clarified that `surf chatgpt ask` requires an explicit prompt argument even when a prompt file is supplied. The final scripts preserve the corrected invocation so future research does not repeat the mistake.

The ChatGPT output was not copied blindly into the final design. It served four roles:

1. summarize the option space,
2. identify likely failure modes,
3. compare broker designs,
4. help structure the final report.

The final report still checked every important claim against local source captures and implementation constraints.

## Scripts as replayable research protocol

The user explicitly asked that prompts, scripts, and related artifacts be stored in `scripts/`. That requirement changed the research from a one-off session into a reproducible protocol.

The collection script encoded the source acquisition process:

```text
scripts/collect-github-app-token-research.sh
```

It performed the Kagi searches and Defuddle downloads. The ChatGPT script encoded the synthesis step:

```text
scripts/run-chatgpt-github-app-token-research.sh
```

A future reader can inspect these scripts and answer:

- Which queries were used?
- Which URLs were selected?
- Which files were generated?
- Which prompt was sent for model synthesis?
- Where did the outputs go?

This is better than only storing a final bibliography. The scripts show the process, not just the result.

## The diary as chronological memory

The implementation diary was one of the most important artifacts. It captured the order of events, including false starts and live validation steps.

The diary stored:

- what changed,
- why it changed,
- exact commands when useful,
- command output summaries,
- errors and fixes,
- decisions and reversals,
- GitHub Actions run IDs,
- GitOps PR numbers,
- Argo CD validation output,
- final conclusions.

For example, the diary preserved the rollout issue where `hair-booking` could not schedule a surge pod on the single-node cluster. That issue was not part of OIDC authentication, but it was part of proving the pipeline end to end. Without the diary, that operational context would be easy to lose.

A diary is different from a final report. The report should be clean and explanatory. The diary should be chronological and honest. Both are needed.

## Live validation as the final research check

The research design was repeatedly tested against the live system. This prevented the docs from becoming aspirational.

The validation loop included:

```text
bootstrap Vault auth mount and roles
  -> validate Vault JWT auth configuration
  -> seed or move Vault secrets
  -> run GitHub Actions workflow
  -> inspect workflow result
  -> inspect generated GitOps PR
  -> merge PR
  -> validate Argo CD sync and health
  -> record evidence
```

The research became more credible because the report could cite concrete proof:

- GitHub Actions runs succeeded.
- GitOps PRs were created and merged.
- Source repository secrets were deleted.
- Vault OIDC-only operation was proven.
- Shared `infra-tooling` was proven with `hair-booking`.
- Terraform imported and managed live Vault resources with no drift.
- Argo CD reported `Synced Healthy` after rollout.

This is the standard to aim for in future infrastructure research: a design is not complete until it has been validated against the real control plane or clearly marked as future work.

## From implementation research to next-stage design

The project had two levels of output.

The first level was an implemented architecture:

```text
GitHub Actions OIDC
  -> Vault JWT auth
  -> short-lived Vault token
  -> repo-specific Vault secret read
  -> GitOps PR token
  -> GitOps PR
  -> Argo CD rollout
```

The second level was a next-stage design:

```text
GitHub Actions OIDC
  -> Vault JWT auth
  -> short-lived Vault token
  -> GitHub App token broker
  -> short-lived GitHub installation token
  -> GitOps PR
```

The tooling workflow supported both levels. For the implemented architecture, the important tools were local code inspection, Vault CLI, GitHub CLI, Kubernetes CLI, Terraform, and docs. For the next-stage design, the important tools were Kagi, Defuddle, ChatGPT, and source-backed synthesis.

This separation is important. Not every researched idea should be implemented immediately. The final report clearly distinguished:

- current state,
- immediate migration path,
- stronger target architecture,
- follow-up ticket scope.

## Final synthesis pattern

The final synthesis was written in a textbook style, but it stayed tied to the concrete system.

The report structure was:

1. state the problem,
2. define the token types,
3. explain the credential broker concept,
4. compare implementation options,
5. identify minimum GitHub App permissions,
6. explain OIDC claim binding,
7. recommend a staged architecture,
8. list failure modes,
9. propose the next ticket.

This worked well because the report did not jump from source notes directly to recommendations. It built the model step by step.

A useful rule for future reports:

```text
If a reader cannot tell which component issues which token, which component consumes it, and what limits its scope, the report is not done.
```

For security-sensitive infrastructure, token lineage and authority boundaries must be explicit.

## Reusable workflow for future deep research projects

The following sequence should be reused.

### 1. Create a ticket workspace

Use `docmgr` to create or select a ticket. The ticket should have at least:

```text
index.md
tasks.md
changelog.md
reference/01-investigation-diary.md
sources/
scripts/
```

The ticket is the durable research workspace. Do not leave important prompts or source captures in `/tmp` only.

### 2. Write the initial research questions

Before collecting sources, write the questions in the diary or a prompt file. Good research questions are concrete:

```text
How can GitHub Actions authenticate to Vault without long-lived secrets?
Which OIDC claims can Vault bind for reusable workflows?
What credential still remains static after Vault OIDC is implemented?
Which component should mint short-lived GitHub installation tokens?
```

Bad research questions are too broad:

```text
How does OIDC work?
What is the best CI/CD security setup?
```

Start specific. Broaden only when the evidence requires it.

### 3. Inspect local reality first

Read the repos, workflows, scripts, Terraform, and docs before web research. Record the actual constraints.

Useful commands:

```bash
rg -n "GITOPS_PR_TOKEN|vault-action|id-token|workflow_call|permissions" . ../*/.github ../corporate-headquarters/infra-tooling
find ttmp -maxdepth 4 -type f | sort
```

The local system should shape the web search, not the other way around.

### 4. Run targeted web searches

Use `surf kagi search` for discovery. Save the outputs in `sources/`.

Example pattern:

```bash
surf kagi search "GitHub Actions OIDC Vault JWT auth bound claims" > sources/kagi-oidc-vault.kagi.md
surf kagi search "GitHub App installation access token permissions repositories expires" > sources/kagi-github-app-token.kagi.md
```

Search results are a research index, not final proof.

### 5. Capture primary sources with Defuddle

For each important source URL, store a clean Markdown copy.

```bash
defuddle parse "https://docs.github.com/actions/reference/openid-connect-reference" --md -o sources/github-oidc-reference.defuddle.md
defuddle parse "https://developer.hashicorp.com/vault/docs/auth/jwt" --md -o sources/vault-jwt-auth-docs.defuddle.md
```

Prefer primary docs and source repositories over blog posts. Use articles for design discussion and operational experience.

### 6. Grep the local source corpus

Once sources are local, use normal code tools on them.

```bash
rg -n "job_workflow_ref|workflow_ref|bound_claims|audience|installation access token|expires|permissions" sources/
```

This step turns web research into inspectable evidence.

### 7. Store prompts and run model synthesis

Write a prompt file under `scripts/`. Include:

- project context,
- source directory,
- specific questions,
- desired output shape,
- constraints,
- known current architecture.

Then run `surf chatgpt` with an explicit query and store the output in `sources/`.

A good model prompt asks for comparison and failure modes, not just a summary:

```text
Compare a Vault KV + actions/create-github-app-token design, a Vault GitHub secrets plugin design, and a custom broker design. For each, identify secrets exposed to CI, operational cost, blast radius, failure modes, and migration sequence.
```

### 8. Synthesize manually

The final report should not be a pasted model answer. Use the model output as one input alongside source captures and local facts.

Manual synthesis should answer:

- What is true in the current system?
- What did primary docs establish?
- Which recommendations fit the actual repos?
- Which options are immediate and which are target architecture?
- What are the failure modes?
- What should the next ticket implement?

### 9. Validate against reality

When implementation is in scope, validate with the real system. For infrastructure work, this may include:

```bash
vault auth list
vault read auth/github-actions/config
gh run list --repo <repo>
gh pr view <number> --repo <repo>
kubectl -n argocd get application <app>
terraform plan -detailed-exitcode
```

Never let a polished report substitute for a working control-plane test.

### 10. Commit the complete evidence trail

Commit the ticket docs, scripts, sources, and final report. Commit the Obsidian report separately if it lives in a separate repo.

The commit boundary should make review easy:

```text
implementation commit
validation docs commit
research sources/report commit
Obsidian report commit
```

This makes it possible to review code changes separately from research artifacts.

## Common failure modes in research projects

### Leaving source collection in scratch space

A `/tmp` directory is fine for early exploration, but the final sources must move into the ticket. If sources stay in `/tmp`, the final report becomes difficult to audit.

### Treating search summaries as evidence

Search results identify sources. They do not establish facts. For critical claims, capture and cite primary docs.

### Asking an LLM too early

If the model is asked before local constraints and sources are collected, it will produce a generic answer. For platform work, generic answers usually miss the important details.

### Not storing prompts

If prompts are not stored, the synthesis cannot be reproduced. Store prompts in `scripts/` next to the collection commands.

### Mixing chronology and final narrative

The diary should preserve the chronological mess. The final report should teach the clean model. Do not make one document do both jobs.

### Forgetting live validation

Infrastructure designs can look correct while failing because of permissions, branch rules, workload scheduling, Terraform provider behavior, or defaulted Kubernetes fields. The research is incomplete until the design is tested or the untested parts are explicitly marked as future work.

### Hiding uncertainty

A good report distinguishes facts, decisions, recommendations, and open questions. For the GitHub App token broker work, the report clearly marked the plugin and custom broker as follow-up architecture rather than completed implementation.

## What worked well in HK3S-0028

Several practices were especially valuable:

- Creating a docmgr ticket early kept the research organized.
- Maintaining a diary preserved commands, errors, run IDs, PR numbers, and rollout observations.
- Using Defuddle turned web pages into greppable local research sources.
- Storing Kagi output preserved the discovery trail.
- Storing ChatGPT prompts and outputs made the synthesis reproducible.
- Copying the Obsidian report back into the ticket kept project knowledge and ticket knowledge aligned.
- Importing live Vault resources into Terraform converted a successful proof into durable ownership.
- Running `docmgr doctor` caught missing frontmatter in generated research artifacts.
- Committing the complete artifact set made the research reviewable later.

## What should be improved next time

The workflow can be tightened further.

### Start with `sources/` and `scripts/` immediately

In this project, some early Kagi outputs were first written to `/tmp`. They were later copied into the ticket. Next time, create `sources/` and `scripts/` before the first search.

### Add frontmatter to generated Markdown artifacts at creation time

`docmgr doctor` flagged some generated Markdown files because they lacked frontmatter. The files were later fixed, but the collection script should write frontmatter headers directly or post-process generated artifacts.

### Prefix source files if they should be docmgr-clean

The remaining docmgr warnings are about missing numeric prefixes on source and prompt artifact filenames. For raw source archives, descriptive names are useful. For fully docmgr-clean tickets, prefer names such as:

```text
sources/01-kagi-oidc-vault.kagi.md
sources/02-github-oidc-reference.defuddle.md
scripts/01-collect-github-app-token-research.sh
scripts/02-chatgpt-github-app-token-research.prompt.md
```

### Record source URLs in a manifest

A future improvement would be a `sources/README.md` or `sources/manifest.yaml` that maps every captured file to:

- original URL,
- capture command,
- capture time,
- reason it was included,
- key claims extracted.

### Separate implementation and research tickets when the follow-up grows

HK3S-0028 became both the implementation ticket and the research container for the next credential-hardening stage. That was acceptable because the research was directly related, but the GitHub App implementation should likely become its own ticket.

## Template for future research collection scripts

A future project can start with this shape:

```bash
#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TICKET_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
SOURCES_DIR="$TICKET_DIR/sources"
mkdir -p "$SOURCES_DIR"

run_search() {
  local name="$1"
  local query="$2"
  {
    echo "---"
    echo "Title: Kagi: $name"
    echo "Ticket: HK3S-XXXX"
    echo "Status: reference"
    echo "DocType: reference"
    echo "Intent: preserve-research-artifact"
    echo "Topics: [research]"
    echo "Summary: Search capture for $query"
    echo "LastUpdated: $(date -Iseconds)"
    echo "WhatFor: Preserve discovery trail."
    echo "WhenToUse: Use when retracing research."
    echo "---"
    echo
    surf kagi search "$query"
  } > "$SOURCES_DIR/$name.kagi.md"
}

capture_page() {
  local name="$1"
  local url="$2"
  defuddle parse "$url" --md -o "$SOURCES_DIR/$name.defuddle.md"
}

run_search "01-kagi-topic" "specific search query"
capture_page "02-primary-doc" "https://example.com/docs"
```

This script starts with the right filesystem layout, writes frontmatter for search outputs, and keeps source capture repeatable.

## Template for future synthesis prompts

A good stored prompt should look like this:

```text
You are helping synthesize a design report for ticket HK3S-XXXX.

Context:
- Repo: <repo path>
- Ticket: <ticket path>
- Current architecture: <short description>
- Desired architecture: <short description>

Sources:
- <list captured source files or source directory>

Questions:
1. What facts do the primary docs establish?
2. What design options exist?
3. What are the security boundaries for each option?
4. What are the operational costs and failure modes?
5. What phased implementation sequence is safest?
6. What should be validated live before considering the work complete?

Constraints:
- Do not assume unmentioned cloud services.
- Distinguish implemented facts from recommendations.
- Prefer concrete steps and file/path references.
- Produce a structured report with a recommendation and open questions.
```

This kind of prompt asks the model to organize evidence, not invent architecture.

## Working rules for future infrastructure research

1. Start with the local system.
2. Use web search for discovery, not final authority.
3. Capture source pages as local Markdown.
4. Store prompts and scripts before running synthesis.
5. Keep a chronological diary separate from the final report.
6. Use the model as a synthesis partner, not as the source of truth.
7. Validate designs with live commands when implementation is in scope.
8. Preserve run IDs, PR numbers, revisions, and exact paths.
9. Commit research artifacts, not just implementation changes.
10. Write one durable Obsidian article that teaches the reusable method.

## Related notes

- [[ARTICLE - Vault OIDC for GitHub Actions - Secretless CI GitOps]]
- [[ARTICLE - Research - Vault OIDC and Short-Lived GitHub App Tokens for GitOps PR Automation]]
- `/home/manuel/code/wesen/2026-03-27--hetzner-k3s/ttmp/2026/05/02/HK3S-0028--enable-github-actions-oidc-access-to-vault/`
- `/home/manuel/code/wesen/2026-03-27--hetzner-k3s/docs/github-actions-vault-oidc-playbook.md`
