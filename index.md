---
title: go-go-parc
created: "2026-05-21"
---

# go-go-parc

A personal knowledge base for projects, research, and technical learning. Everything here is written by or for Manuel, using AI-assisted workflows.

## How the vault is organized

### `Projects/` — Project reports and articles

Dated project reports, technical deep dives, playbooks, and textbooks. Organized by year/month/day.

- **`PROJ —`** Project reports: what was built, how it works, what was learned
- **`ARTICLE —`** Standalone technical articles and playbooks
- **`GUIDE —`** Step-by-step implementation guides
- **`RESEARCH —`** Open research questions and investigations

The bulk of the vault lives here. Browsing by date shows the chronological arc of work.

### `Research/` — Structured knowledge and long-form research

- **`Research/KB/`** — The knowledge base: reusable concept entries organized by tier
  - `Fundamentals/` — Universal CS/engineering concepts (encoding, access control, rendering pipelines)
  - `On-Ramp/`** — Concepts you need before working on a project (ESC/POS printing, OAuth flows, Tree-sitter)
  - `Tribal/`** — Patterns specific to this body of work (goja embedding, IIFE cell rewrite, reduction-ladder debugging)
- **`Research/Institute/`** — Research institute: long-form investigations
  - `Articles/`, `Books/`, `Guidelines/`, `Magazine/`, `Proposals/`, `Technical Reports/`, `Wiki/`
  - `Research/` — Deep research projects with source material
  - `Projects/` — Ongoing institute-level projects
- **`Research/playbooks/`** — Operational playbooks (KB authoring, git history cleanup, vault sync)

### `Logs/` — Campaign and batch logs

Batch analysis logs from the knowledge base campaign, intern reports, and handoff documents.

### `Attachments/` — Images and embedded files

Auto-generated attachment storage for images referenced in notes.

## Navigation tips

- Start with the **graph view** or **search** to find topics across folders
- Use `PROJ` / `ARTICLE` / `GUIDE` prefixes to filter by document type
- The `Research/KB/Tribal/` entries are the distilled, reusable patterns — good entry points for understanding recurring design decisions
- Dates in `Projects/` track when the report was written, not necessarily when the project started
