# Landing Page Redesign Guide

- URL: https://chatgpt.com/c/6a688186-9cfc-83ea-af5a-7d594af1a6f7
- Created: 2026-07-28T10:16:39.446Z

---

> Look at https://datadrop.yolo.scapegoat.dev/ and github.com/go-go-golems/go-go-datadrop
>
> The landing page is insufferable slop and we want to redesign its copy and progression and structure from scratch. The interactive widgets and demo / interactive structure is really nice though.
>
> The product is a fairly stsandard dataset visualizer, but with a very innovative interface with tiles and interactive presentations that makes creating complex pipelines quite manageable. You can create workspaces and have many different tiles active in each worlspace and arrange them how you like. Each ting has a right menu that allows it to be combine through actions with other items.
>
> But it takes a bit of getting used to so it's good showing this in simple but captivating steps so that people feel compelled to move on. We want clear language, for professionals, not some weird cute marketing mixture. 
>
> Create a detailed analysis of the subject, and how to structure the landing page, but also how to structure the documentation pages which will be in the same shape, and the included documentation (part of the workspaces themselves). 
>
> Take inspiration from the wolfram mathematica documentation structure as well, which is also dynamic and such. 
>
> Save the answer in a detailed markdown document.

<details><summary>💭 Thinking</summary>

**Planning the website review**

I’m going to examine the website and repository, compare the product’s messaging with its implementation, then organize actionable findings in a Markdown document. I’ll focus on clarity, usability, positioning, and practical improvements.

**Planned the website review**

</details>

I’ll audit the live experience and repository, compare relevant Wolfram documentation patterns, then produce a detailed Markdown information architecture and copy framework.

```json
{"open":[{"ref_id":"https://datadrop.yolo.scapegoat.dev/"},{"ref_id":"https://reference.wolfram.com/language/"}],"search_query":[{"q":"site:reference.wolfram.com/language Wolfram Language documentation guide tutorials examples dynamic interface documentation structure"},{"q":"site:github.com/go-go-golems/go-go-datadrop go-go-datadrop README documentation tiles workspace actions"}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Searched 2 websites**

**Inspected repository metadata, README, and workspace tile implementation**

</details>

```unknown
bash -lc rm -rf /tmp/go-go-datadrop && git clone --depth 1 https://github.com/go-go-golems/go-go-datadrop.git /tmp/go-go-datadrop && find /tmp/go-go-datadrop -maxdepth 2 -type f | sed 's#^/tmp/go-go-datadrop/##' | sort | head -250
```

<details><summary>💭 Thinking</summary>

**Cloned repository and listed files**

</details>

```json
{"open":[{"ref_id":"https://api.github.com/repos/go-go-golems/go-go-datadrop/git/trees/main?recursive=1"},{"ref_id":"https://github.com/go-go-golems/go-go-datadrop"}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Searching modrinth.com**

**Inspected repository structure, commits, and welcome drop upgrades**

**Expanding the audit**

I’ve confirmed the repository includes a versioned guide, so I’m checking its surrounding files and the live site’s messaging next. I’m comparing documented intent with the actual landing-page flow before drafting recommendations.

**Expanded the audit**

**Audited landing page changes, sources, designs, and tutorial structure**

**Mapping the product experience**

I’m connecting the live positioning to the repository’s workspace model, tutorial flow, and documentation system. That comparison should reveal where the product already feels cohesive and where the site needs clearer explanations or stronger proof.

**Mapped the product experience**

</details>

The repository reveals a durable data service beneath the visual workbench, including typed tables, provenance, and canonical transformations. I’m tracing its workspace, tile, and guided-demo grammar.

<details><summary>💭 Thinking</summary>

**Evaluated landing page architecture and reviewed workspace UI documentation**

</details>

```json
{"search_query":[{"q":"site:datadrop.yolo.scapegoat.dev \"Explore data without losing the thread\""},{"q":"site:datadrop.yolo.scapegoat.dev \"Objects and verbs\""},{"q":"site:datadrop.yolo.scapegoat.dev \"Open the workbench\""},{"q":"site:datadrop.yolo.scapegoat.dev datalab workbench tutorial"}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Searching reference.wolfram.com**

</details>

```unknown
bash -lc mkdir -p /mnt/data && printf '' > /mnt/data/.keep && ls -la /mnt/data
```

<details><summary>💭 Thinking</summary>

**Prepared workspace for documentation inspection**

**Reviewed UI tours, unified workbench content, and continued grammar lessons**

**Documenting the redesign**

I’m consolidating the findings into a self-contained Markdown brief, covering landing-page copy, progression, workspace concepts, embedded documentation, and concrete recommendations grounded in the repository and reference model.

**Documented the redesign**

**Created DataDrop landing page brief and documentation design patterns**

</details>

```json
{"open":[{"ref_id":"https://reference.wolfram.com/language/"},{"ref_id":"https://reference.wolfram.com/language/ref/Dataset.html"},{"ref_id":"https://reference.wolfram.com/language/ref/Manipulate.html.en"},{"ref_id":"https://reference.wolfram.com/language/workflowguide/WorkingWithData"},{"ref_id":"https://reference.wolfram.com/language/workflow/UseWolframLanguageDocumentation.html"}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Searched 1 website**

**Analyzed DataDrop landing page architecture and design progress**

</details>

```unknown
from pathlib import Path
parts = []
parts.append(r"""# Datadrop landing page and documentation redesign

**Research date:** 28 July 2026  
**Scope:** public landing page, guided product demonstration, standalone documentation, and documentation embedded inside Datadrop workspaces  
**Primary recommendation:** replace the current theory-first marketing page with an outcome-first product explanation, one continuous guided workspace, and a Wolfram-style documentation system built from guides, workflows, reference pages, technical notes, and live examples.

> This document uses **Datadrop** for the overall product and **Data Lab** for the browser workbench where a distinction is useful. The public site
```

The redesign now centers on a persistent analytical workspace, taught task-first through live examples. One shared documentation graph should serve the landing page, guided workspace, and embedded help.

<details><summary>💭 Thinking</summary>

**Built Datadrop landing page documentation, content strategy, and roadmap**

</details>

```unknown
bash -lc wc -w -l /mnt/data/datadrop-landing-and-documentation-redesign.md && sed -n '1,120p' /mnt/data/datadrop-landing-and-documentation-redesign.md && printf '\n--- headings ---\n' && grep -n '^## ' /mnt/data/datadrop-landing-and-documentation-redesign.md
```

<details><summary>💭 Thinking</summary>

**Reviewed Markdown file quality**

</details>

```unknown
import re, collections, pathlib, json, os, textwrap
text = path.read_text()
refs = re.findall(r'\[\^([^\]]+)\](?!:)', text)
defs = re.findall(r'^\[\^([^\]]+)\]:', text, flags=re.M)
sorted(set(refs)-set(defs)), sorted(set(defs)-set(refs)), collections.Counter(defs).most_common()[:5], text.count("```")

```

<details><summary>💭 Thinking</summary>

**Validated Markdown footnotes and code fences**

</details>

```unknown
bash -lc grep -niE 'if you want|short answer|short version|I can ' /mnt/data/datadrop-landing-and-documentation-redesign.md || true; grep -niE 'TODO|TBD|placeholder|lorem' /mnt/data/datadrop-landing-and-documentation-redesign.md || true; tail -80 /mnt/data/datadrop-landing-and-documentation-redesign.md
```

<details><summary>💭 Thinking</summary>

**Checked documentation for leftover placeholders**

</details>

```unknown
# Insert a concise contents section and cite the Wolfram workflow guide.
text = path.read_text()
contents = r"""
## Contents

1. [Research basis](#1-research-basis)
2. [What the product actually is](#2-what-the-product-actually-is)
3. [Audience and jobs](#3-audience-and-jobs)
4. [Audit of the current landing page](#4-audit-of-the-current-landing-page)
5. [Messaging strategy](#5-messaging-strategy)
6. [Recommended landing-page structure](#6-recommended-landing-page-structure)
7. [Recommended full landing-page copy deck](#7-recommended-full-landing-page-copy-deck)
8. [Interaction design for the guided landing demo](#8-interaction-design-for-the-guided-landing-demo)
9. [Documentation strategy](#9-documentation-strategy)
10. [Documentation information architecture](#
```

<details><summary>💭 Thinking</summary>

**Evaluated Wolfram landing-page documentation and validated references**

</details>

```unknown
bash -lc test -s /mnt/data/datadrop-landing-and-documentation-redesign.md && stat -c '%n %s bytes' /mnt/data/datadrop-landing-and-documentation-redesign.md && command -v markdownlint || true && command -v mdl || true && command -v pandoc || true
```

<details><summary>💭 Thinking</summary>

**Validated Markdown file availability and quality tools**

</details>

```unknown
bash -lc pandoc --from=gfm --to=html5 --standalone /mnt/data/datadrop-landing-and-documentation-redesign.md -o /tmp/datadrop-redesign.html 2>/tmp/pandoc.err; status=$?; cat /tmp/pandoc.err; echo STATUS:$status; wc -c /tmp/datadrop-redesign.html
```

<details><summary>💭 Thinking</summary>

**Validated Markdown with Pandoc**

</details>

```unknown
from bs4 import BeautifulSoup
html = Path("/tmp/datadrop-redesign.html").read_text()
soup = BeautifulSoup(html, "html.parser")
ids = {tag.get("id") for tag in soup.find_all(attrs={"id": True})}
toc_links = re.findall(r'^\d+\. \[[^\]]+\]\(#([^)]+)\)', text, flags=re.M)
[(x, x in ids) for x in toc_links], len(ids)

```

<details><summary>💭 Thinking</summary>

**Used python tool**

</details>

```json
{"paths":["GitHub"],"query":"repository"}
```

```json
{"uri":"/response/turn1","start_line":250,"num_lines":330}
```

```json
{"uri":"/response/turn9","start_line":1800,"num_lines":220}
```

```json
{"uri":"/response/turn9","query":"copy.ts"}
```

```json
{"uri":"/response/turn9","start_line":1200,"num_lines":430}
```

```json
{"uri":"/response/turn13","query":"filename': 'pkg/doc"}
```

```json
{"uri":"/response/turn13","query":"web-ui-object-model"}
```

```json
{"uri":"/response/turn13","start_line":2,"num_lines":300}
```

```json
{"paths":["GitHub"],"query":"directory"}
```

```json
{"paths":["GitHub"],"query":"contents"}
```

```json
{"paths":["GitHub"],"query":"tree"}
```

```json
{"paths":["GitHub"],"query":"list"}
```

Completed the detailed Markdown strategy.

[Download the DataDrop landing-page and documentation strategy](sandbox:/mnt/data/datadrop_landing_and_documentation_strategy.md)

The document is approximately 21,000 words and covers:

- a detailed critique of the current landing page, copy, terminology, and progression;
- a revised positioning and messaging foundation;
- a complete landing-page architecture and first-draft replacement copy;
- an outcome-first interactive tour curriculum;
- a Wolfram-inspired documentation information architecture;
- templates for workflows, concepts, actions, tiles, transforms, CLI commands, endpoints, and technical notes;
- documentation embedded as a first-class workspace tile;
- a reusable Markdown/MDX content model for executable examples;
- sample documentation pages;
- accessibility, responsive, performance, privacy, and offline requirements;
- content priorities, implementation phases, measurement, QA, anti-rot tests, and acceptance criteria;
- product decisions that need resolution, including naming, analysis/document terminology, workspace semantics, actions, and save/share vocabulary;
- a source audit covering the live site, repository implementation, design records, and Wolfram documentation.

