#!/usr/bin/env python3
"""Render the Agent-Operated Engines pattern language (vault markdown) into one HTML page for an Artifact."""
import html, json, pathlib, re, sys
import markdown

SRC = pathlib.Path.home() / "code/wesen/go-go-golems/go-go-parc/Research/Software Architecture Garden/general/agent-operated-engines"
VAL = SRC / "_validation"
OUT = pathlib.Path(sys.argv[1])

GROUPS = [("The engine", range(1, 5)), ("The agent surface", range(5, 9)),
          ("Agents at work", range(9, 12)), ("Keeping it true", range(12, 14))]


def split_frontmatter(text):
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if not m:
        return {}, text
    fm = {}
    for line in m.group(1).splitlines():
        mm = re.match(r"^(\w+):\s*(.*)$", line)
        if mm:
            fm[mm.group(1)] = mm.group(2).strip()
    return fm, text[m.end():]


def fix_links(md):
    md = re.sub(r"\[\[00-overview(?:\|([^\]]+))?\]\]", lambda m: f"[{m.group(1) or 'Overview'}](#overview)", md)
    md = re.sub(r"\[\[[^\]|]*\|([^\]]+)\]\]", r"*\1*", md)
    md = re.sub(r"\[\[([^\]]+)\]\]", lambda m: f"*{m.group(1).split('/')[-1]}*", md)
    md = re.sub(r"\]\((\d\d)-[a-z0-9-]+\.md(?:#[^)]*)?\)", lambda m: f"](#{'overview' if m.group(1) == '00' else 'ch-' + m.group(1)})", md)
    return md


def render(md, prefix):
    h = markdown.markdown(md, extensions=["tables", "fenced_code", "sane_lists"], output_format="html")
    h = re.sub(r'<pre><code class="language-mermaid">(.*?)</code></pre>',
               lambda m: f'<div class="diagram"><pre class="mermaid">{m.group(1)}</pre></div>', h, flags=re.S)
    h = re.sub(r"<pre><code(?: class=\"language-[\w-]+\")?>", '<div class="code"><pre><code>', h)
    h = h.replace("</code></pre>", "</code></pre></div>").replace("</pre></div></div>", "</pre></div>")
    h = re.sub(r"<table>", '<div class="table-wrap"><table>', h).replace("</table>", "</table></div>")

    def hid(m):
        slug = re.sub(r"[^a-z0-9]+", "-", re.sub(r"<[^>]+>", "", m.group(2)).lower()).strip("-")
        return f'<h{m.group(1)} id="{prefix}-{slug}">{m.group(2)}</h{m.group(1)}>'
    h = re.sub(r"<h([23])>(.*?)</h\1>", hid, h)
    # Alexander's form: the Problem sentence and the "Therefore:" paragraph stand out
    h = re.sub(r'(<h2 id="[^"]+-solution">Solution</h2>\s*)<p>', r'\1<p class="therefore">', h)
    h = re.sub(r'(<h2 id="[^"]+-problem">Problem</h2>\s*)<p>', r'\1<p class="problem">', h)
    h = re.sub(r'(<h2 id="[^"]+-solution">)', r'<div class="diamonds" aria-hidden="true">❖ ❖ ❖</div>\1', h)
    return h


def quiz_stats(n):
    keyf = VAL / "keys" / f"{n}.json"
    if not keyf.exists():
        return None
    key = json.loads(keyf.read_text())
    runs = qp = qt = fr = ft = 0
    tags = set()
    for f in sorted(VAL.glob(f"answers/{n}-*.json")):
        m = re.match(rf"{n}-(\w+?)-(v\d+)\.json$", f.name)
        if not m:
            continue
        sc, tag = m.groups()
        try:
            a = json.loads(f.read_text())
        except Exception:
            continue
        runs += 1
        tags.add(tag)
        qk, fk = key["quiz"].get(sc, {}), key["fits"].get(sc, {})
        quiz = {q["id"]: q.get("answer", "") for q in a.get("quiz", [])}
        qp += sum(1 for qid, groups in qk.items()
                  if all(any(w.lower() in str(quiz.get(qid, "")).lower() for w in g) for g in groups))
        qt += len(qk)
        fits = {t["id"]: t.get("fits") for t in a.get("transfer", [])}
        fr += sum(1 for tid, want in fk.items() if fits.get(tid) is want)
        ft += len(fk)
    return {"runs": runs, "versions": len(tags), "quiz": (qp, qt), "fits": (fr, ft)}


def build_stats(n):
    out = []
    for f in sorted((VAL / "builds").glob(f"{n}-*-*-*.txt")):
        m = re.match(rf"{n}-(\w+)-(v\d+)-(\w+)\.txt$", f.name)
        if not m:
            continue
        agent, tag, kind = m.groups()
        t = f.read_text()
        ran = re.findall(r"Ran (\d+) tests", t)
        status = re.findall(r"^(OK|FAILED \(([^)]*)\))", t, re.M)
        if not ran or not status:
            continue
        total = int(ran[0])
        bad = sum(int(x) for x in re.findall(r"\d+", status[0][1])) if status[0][0] != "OK" else 0
        own = int(ran[-1]) if len(ran) > 1 else None
        rec = {"agent": agent, "kind": kind, "passed": total - bad, "total": total, "own": own}
        if kind != "build" and len(ran) >= 3 and len(status) >= 2:
            xbad = sum(int(x) for x in re.findall(r"\d+", status[1][1])) if status[1][0] != "OK" else 0
            rec["extra"] = (int(ran[1]) - xbad, int(ran[1]))
        out.append(rec)
    return out


def esc(s):
    return html.escape(s, quote=True)


chapters = []
for f in sorted(SRC.glob("[01][0-9]-*.md")):
    n = f.name[:2]
    fm, body = split_frontmatter(f.read_text())
    body = fix_links(body)
    if n == "00":
        body = re.sub(r"^# .*\n", "", body, count=1, flags=re.M)
        chapters.append({"n": n, "html": render(body, "overview"), "fm": fm})
        continue
    m = re.search(r"^# Chapter (\d+) · (.+)$", body, re.M)
    num, name = int(m.group(1)), m.group(2).strip()
    body = body[m.end():]
    sub = re.search(r"^\*(.+)\*\s*$", body, re.M)
    subtitle = sub.group(1) if sub else ""
    if sub:
        body = body[:sub.start()] + body[sub.end():]
    rating = re.search(r"^Rating: (★+) \(([^)]*)\)\.?\s*$", body, re.M)
    stars = rating.group(1) if rating else ""
    if rating:
        body = body[:rating.start()] + body[rating.end():]
    chapters.append({"n": n, "num": num, "name": name, "subtitle": subtitle, "stars": stars,
                     "status": fm.get("status", ""), "html": render(body, f"ch-{n}"),
                     "quiz": quiz_stats(n), "builds": build_stats(n)})

ov = chapters[0]
chs = {c["num"]: c for c in chapters[1:]}

total_runs = sum((c["quiz"] or {}).get("runs", 0) for c in chapters[1:])
total_builds = sum(1 for c in chapters[1:] for b in c["builds"] if b["kind"] == "build")


def validation_block(c):
    q = c["quiz"]
    parts = []
    if q and q["runs"]:
        parts.append(
            f'<div><dt>Read and apply</dt><dd>{q["runs"]} agent runs on {q["versions"]} '
            f'version{"s" if q["versions"] != 1 else ""} · quiz {q["quiz"][0]}/{q["quiz"][1]} · '
            f'fit verdicts {q["fits"][0]}/{q["fits"][1]}</dd></div>')
    builds = [b for b in c["builds"] if b["kind"] == "build"]
    ext = [b for b in c["builds"] if b["kind"] != "build"]
    if builds:
        s = ", ".join(f'{b["passed"]}/{b["total"]}' for b in builds)
        parts.append(f'<div><dt>Built by agents</dt><dd>{len(builds)} project{"s" if len(builds) != 1 else ""} · '
                     f'hidden tests {s}</dd></div>')
    if ext:
        s = ", ".join(f'{b["extra"][0]}/{b["extra"][1]}' for b in ext if "extra" in b)
        r = ", ".join(f'{b["passed"]}/{b["total"]}' for b in ext)
        parts.append(f'<div><dt>Change request</dt><dd>new hidden tests {s} · original tests still {r}</dd></div>')
    if not builds:
        parts.append('<div><dt>Built by agents</dt><dd class="pending">builds running</dd></div>'
                     if c["num"] in (3, 4, 6, 8) else
                     '<div><dt>Built by agents</dt><dd class="pending">not yet</dd></div>')
    return '<dl class="validation">' + "".join(parts) + "</dl>"


STATUS_HINT = {"established": "seen working in several of the source projects",
               "candidate": "one strong instance, others partial",
               "emergent": "visible in the projects, not yet fully built"}

nav = ['<a class="nav-ov" href="#overview">Overview</a>']
for g, rng in GROUPS:
    nav.append(f'<p class="nav-group">{esc(g)}</p><ol class="nav-list" start="{rng[0]}">')
    for i in rng:
        c = chs[i]
        nav.append(f'<li><a href="#ch-{c["n"]}" data-ch="ch-{c["n"]}"><span class="nav-num">{i}</span>'
                   f'<span class="nav-name">{esc(c["name"])}</span><span class="nav-stars" '
                   f'aria-label="{len(c["stars"])} star">{c["stars"]}</span></a></li>')
    nav.append("</ol>")
nav.append('<a class="nav-ov" href="#method">How they were checked</a>')

sections = []
for g, rng in GROUPS:
    for i in rng:
        c = chs[i]
        first = i == rng[0]
        sections.append(f'''
<section class="chapter" id="ch-{c["n"]}" aria-labelledby="ch-{c["n"]}-title">
  <header class="ch-head">
    <p class="eyebrow">{"<span>" + esc(g) + "</span> · " if first else ""}Chapter {i}</p>
    <h1 id="ch-{c["n"]}-title">{esc(c["name"])} <span class="stars" title="{"close to invariant" if len(c["stars"]) == 2 else "a good form among several"}">{c["stars"]}</span></h1>
    <p class="subtitle">{esc(c["subtitle"])}</p>
    <div class="ch-meta">
      <p class="status"><span class="chip chip-{esc(c["status"])}">{esc(c["status"])}</span> {esc(STATUS_HINT.get(c["status"], ""))}</p>
      {validation_block(c)}
    </div>
  </header>
  <div class="prose">{c["html"]}</div>
</section>''')

method = f'''
<section class="chapter method" id="method" aria-labelledby="method-title">
  <header class="ch-head">
    <p class="eyebrow">Appendix</p>
    <h1 id="method-title">How they were checked</h1>
    <p class="subtitle">Agents read each chapter, applied it to unfamiliar problems, and built software with it.</p>
  </header>
  <div class="prose">
    <p>Every chapter went through isolated agent runs (DeepSeek 4.1 Flash, no tools, no files, the chapter and a task
    in one saved prompt). So far that is {total_runs} runs across the thirteen chapters.</p>
    <ul>
      <li><strong>Quiz.</strong> Four questions per scenario with a hidden key, to check the chapter is read the way
      it was meant.</li>
      <li><strong>Transfer.</strong> The agent maps the pattern onto a domain the chapter never mentions, sketches it,
      and names the implementation note that matters most there.</li>
      <li><strong>Control.</strong> One scenario per run where the pattern should <em>not</em> be used. Every run so
      far rejected the control, with reasons.</li>
      <li><strong>Review.</strong> Each run lists what is unclear, wrong, missing or too long. A section is revised
      when at least two runs flag the same defect; isolated complaints are noted and left alone.</li>
    </ul>
    <p>Then agents built small, standard-library-only projects that need the pattern, each in its own directory, with
    a diary and their own tests ({total_builds} builds scored so far, more running). Hidden acceptance tests were written against the
    task and checked against a reference implementation before any agent saw them. A later change request (adding a new
    kind of operation to the chapter 1 build) measured whether the structure grows in one place.</p>
    <p>Pass rates show whether the code works, not whether the pattern helped. The next round adds builds without
    the chapter as controls and a blind design review in the spirit of Alexander, Gabriel and Fowler: which forces
    the code resolved, whether the structure fits its task or copies the sketch, whether similar seams emerged across
    agents, whether a newcomer could live in the code and add the next operation locally, where it smells, and whether
    a simpler control did as well with less.</p>
  </div>
</section>'''

page = f'''<title>Agent-Operated Engines</title>
<meta name="claude:viewport-fit-sides" content="cover">
<meta name="description" content="A pattern language for engines that language-model agents operate by writing code.">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,500;12..96,700&family=Literata:ital,opsz,wght@0,7..72,400;0,7..72,600;0,7..72,700;1,7..72,400&family=JetBrains+Mono:wght@400;600&display=swap">
<style>
/* Layout: a bound book: sticky chapter index on the left, one ~66ch reading column, chapters stacked as sections */
:root {{
  --paper: #f4f6f4;
  --page: #fbfcfb;
  --ink: #18211d;
  --muted: #56635c;
  --rule: #d3dbd6;
  --accent: #1b6a55;
  --accent-ink: #12503f;
  --tint: #e4eee9;
  --code-bg: #edf1ee;
  --chip-est: #1b6a55;
  --chip-cand: #8a5a12;
  --chip-emer: #5a4a8a;
  --font-display: "Bricolage Grotesque", "Avenir Next", "Segoe UI", system-ui, sans-serif;
  --font-body: "Literata", "Iowan Old Style", Georgia, "Times New Roman", serif;
  --font-mono: "JetBrains Mono", ui-monospace, "SF Mono", Menlo, Consolas, monospace;
  --measure: 66ch;
}}
@media (prefers-color-scheme: dark) {{
  :root:not([data-theme="light"]) {{
    --paper: #101513; --page: #141a17; --ink: #dfe6e2; --muted: #9aa8a0; --rule: #2a3530;
    --accent: #6cc5a8; --accent-ink: #8fd6bd; --tint: #1b2722; --code-bg: #18201c;
    --chip-est: #6cc5a8; --chip-cand: #e0b061; --chip-emer: #b4a4ea;
    color-scheme: dark;
  }}
}}
:root[data-theme="dark"] {{
  --paper: #101513; --page: #141a17; --ink: #dfe6e2; --muted: #9aa8a0; --rule: #2a3530;
  --accent: #6cc5a8; --accent-ink: #8fd6bd; --tint: #1b2722; --code-bg: #18201c;
  --chip-est: #6cc5a8; --chip-cand: #e0b061; --chip-emer: #b4a4ea;
  color-scheme: dark;
}}
html {{ scroll-padding-top: calc(env(safe-area-inset-top, 0px) + 16px); }}
body {{
  background: var(--paper); color: var(--ink);
  font-family: var(--font-body); font-size: 1.0625rem; line-height: 1.62;
  -webkit-font-smoothing: antialiased; text-rendering: optimizeLegibility;
}}
.shell {{
  display: grid; grid-template-columns: minmax(0, 1fr); gap: 0;
  max-width: 1240px; margin: 0 auto;
  padding-left: max(16px, env(safe-area-inset-left, 0px));
  padding-right: max(16px, env(safe-area-inset-right, 0px));
}}
@media (min-width: 980px) {{
  .shell {{ grid-template-columns: 260px minmax(0, 1fr); gap: 56px; }}
}}
a {{ color: var(--accent-ink); text-decoration-thickness: 1px; text-underline-offset: 2px; }}
a:hover {{ color: var(--accent); }}
:focus-visible {{ outline: 2px solid var(--accent); outline-offset: 2px; border-radius: 2px; }}

/* index */
.index {{ padding-block: 20px 8px; min-width: 0; }}
.index details > summary {{
  font-family: var(--font-display); font-weight: 700; font-size: 0.95rem; cursor: pointer;
  padding: 10px 0; border-bottom: 1px solid var(--rule); list-style: none;
}}
.index details > summary::-webkit-details-marker {{ display: none; }}
.index details > summary::after {{ content: " ▾"; color: var(--muted); }}
.index details[open] > summary::after {{ content: " ▴"; }}
@media (min-width: 980px) {{
  .index {{ position: sticky; top: env(safe-area-inset-top, 0px); align-self: start;
           max-height: 100vh; overflow-y: auto; padding-block: 36px 24px; }}
  .index details > summary {{ display: none; }}
}}
.nav-ov {{ display: block; font-family: var(--font-display); font-weight: 500; font-size: 0.92rem;
          padding: 8px 0 2px; text-decoration: none; color: var(--ink); }}
.nav-group {{ margin: 18px 0 4px; font-family: var(--font-display); font-size: 0.7rem; font-weight: 700;
             letter-spacing: 0.09em; text-transform: uppercase; color: var(--muted); }}
.nav-list {{ list-style: none; margin: 0; padding: 0; }}
.nav-list a {{
  display: grid; grid-template-columns: 1.7em minmax(0, 1fr) auto; gap: 6px; align-items: baseline;
  padding: 4px 6px; margin-inline: -6px; border-radius: 4px;
  font-family: var(--font-display); font-size: 0.88rem; line-height: 1.3; text-decoration: none; color: var(--ink);
}}
.nav-list a:hover {{ background: var(--tint); color: var(--ink); }}
.nav-list a.current {{ background: var(--tint); color: var(--accent-ink); font-weight: 700; }}
.nav-num {{ color: var(--muted); font-variant-numeric: tabular-nums; text-align: right; }}
.nav-stars {{ color: var(--accent); font-size: 0.7rem; letter-spacing: 0.05em; }}

/* main column */
main {{ min-width: 0; padding-block: 8px 64px; }}
.title-block {{ padding-block: 40px 28px; border-bottom: 1px solid var(--rule); max-width: var(--measure); }}
.title-block .eyebrow {{ margin: 0 0 10px; }}
.title-block h1 {{
  font-family: var(--font-display); font-weight: 700; font-size: clamp(2.2rem, 6vw, 3.6rem);
  line-height: 1.02; letter-spacing: -0.02em; margin: 0; text-wrap: balance;
}}
.title-block .lede {{ font-size: 1.15rem; color: var(--muted); margin: 16px 0 0; max-width: 56ch; }}
.title-block .facts {{ margin: 18px 0 0; font-family: var(--font-display); font-size: 0.85rem; color: var(--muted);
                      display: flex; flex-wrap: wrap; gap: 6px 18px; padding: 0; list-style: none; }}
.title-block .facts b {{ color: var(--ink); font-weight: 700; }}

.eyebrow {{ font-family: var(--font-display); font-size: 0.74rem; font-weight: 700; letter-spacing: 0.1em;
           text-transform: uppercase; color: var(--muted); }}
.eyebrow span {{ color: var(--accent-ink); }}

.chapter {{ padding-block: 56px 8px; border-bottom: 1px solid var(--rule); }}
.ch-head {{ max-width: var(--measure); margin-bottom: 8px; }}
.ch-head .eyebrow {{ margin: 0 0 8px; }}
.ch-head h1 {{
  font-family: var(--font-display); font-weight: 700; font-size: clamp(1.7rem, 4.2vw, 2.45rem);
  line-height: 1.08; letter-spacing: -0.015em; margin: 0; text-wrap: balance;
}}
.stars {{ color: var(--accent); font-size: 0.55em; vertical-align: 0.35em; letter-spacing: 0.04em; white-space: nowrap; }}
.subtitle {{ font-style: italic; font-size: 1.12rem; color: var(--muted); margin: 10px 0 0; }}
.ch-meta {{ display: grid; gap: 8px; margin-top: 18px; padding: 12px 14px; background: var(--page);
           border: 1px solid var(--rule); border-radius: 6px; font-family: var(--font-display); font-size: 0.84rem; }}
.status {{ margin: 0; color: var(--muted); }}
.chip {{ display: inline-block; padding: 1px 8px; border-radius: 999px; border: 1px solid currentColor;
        font-size: 0.72rem; font-weight: 700; letter-spacing: 0.06em; text-transform: uppercase; margin-right: 6px; }}
.chip-established {{ color: var(--chip-est); }}
.chip-candidate {{ color: var(--chip-cand); }}
.chip-emergent {{ color: var(--chip-emer); }}
.validation {{ display: grid; gap: 2px; margin: 0; }}
.validation > div {{ display: grid; grid-template-columns: 9.5em minmax(0, 1fr); gap: 10px; }}
.validation dt {{ color: var(--muted); }}
.validation dd {{ margin: 0; font-variant-numeric: tabular-nums; }}
.validation dd.pending {{ color: var(--muted); font-style: italic; }}
@media (max-width: 480px) {{ .validation > div {{ grid-template-columns: minmax(0, 1fr); gap: 0; }} .validation > div + div {{ margin-top: 6px; }} }}

/* prose */
.prose {{ max-width: var(--measure); }}
.prose h2 {{
  font-family: var(--font-display); font-weight: 700; font-size: 1.2rem; letter-spacing: -0.005em;
  margin: 2.1em 0 0.5em; text-wrap: balance;
}}
.prose h3 {{ font-family: var(--font-display); font-weight: 700; font-size: 1.02rem; margin: 1.6em 0 0.4em; }}
.prose p, .prose ul, .prose ol {{ margin: 0 0 0.95em; }}
.prose ul, .prose ol {{ padding-left: 1.4em; }}
.prose li {{ margin-bottom: 0.45em; }}
.prose li > p {{ margin-bottom: 0.4em; }}
.prose strong {{ font-weight: 700; }}
.prose blockquote {{ margin: 1em 0; padding: 0.1em 0 0.1em 1em; border-left: 2px solid var(--rule); color: var(--muted); }}
.prose code {{ font-family: var(--font-mono); font-size: 0.84em; background: var(--code-bg); padding: 0.08em 0.3em;
              border-radius: 3px; overflow-wrap: anywhere; }}
.prose .problem {{ font-size: 1.12rem; line-height: 1.5; }}
.prose .therefore {{ font-size: 1.1rem; line-height: 1.55; padding-block: 0.2em 0.9em;
                    border-bottom: 1px solid var(--rule); }}
.diamonds {{ margin: 2.4em 0 -0.8em; color: var(--accent); letter-spacing: 0.4em; font-size: 0.9rem; text-align: left; }}
.code, .table-wrap, .diagram {{ overflow-x: auto; margin: 1.1em 0 1.3em; max-width: 100%; }}
.code pre {{ margin: 0; padding: 14px 16px; background: var(--code-bg); border-radius: 6px; width: max-content; min-width: 100%;
            box-sizing: border-box; }}
.code code {{ font-family: var(--font-mono); font-size: 0.8rem; line-height: 1.55; background: none; padding: 0;
             overflow-wrap: normal; color: var(--ink); }}
.diagram {{ background: var(--page); border: 1px solid var(--rule); border-radius: 6px; padding: 12px; }}
.diagram pre {{ margin: 0; font-family: var(--font-mono); font-size: 0.8rem; }}
@media (min-width: 1240px) {{ .prose .code, .prose .table-wrap, .prose .diagram {{ max-width: calc(var(--measure) + 14ch); }} }}
table {{ border-collapse: collapse; font-size: 0.88rem; line-height: 1.45; min-width: 100%; }}
th, td {{ text-align: left; vertical-align: top; padding: 7px 12px 7px 0; border-bottom: 1px solid var(--rule); }}
th {{ font-family: var(--font-display); font-weight: 700; font-size: 0.82rem; color: var(--muted);
     border-bottom-color: var(--ink); }}
td code {{ white-space: nowrap; }}
.method .prose {{ padding-bottom: 32px; }}
footer.colophon {{ max-width: var(--measure); padding-block: 28px 8px; font-family: var(--font-display); font-size: 0.82rem;
                  color: var(--muted); }}
</style>

<div class="shell">
  <nav class="index" aria-label="Chapters">
    <details id="index-details">
      <summary>Contents · 13 patterns</summary>
      {"".join(nav)}
    </details>
  </nav>
  <main>
    <header class="title-block" id="overview">
      <p class="eyebrow">A pattern language · 13 chapters</p>
      <h1>Agent-Operated Engines</h1>
      <p class="lede">How to build a domain engine that language-model agents operate by writing code, and how to run,
      check and record the work those agents do.</p>
      <ul class="facts">
        <li>Distilled from <b>goja-cv</b>, <b>go-go-goja</b>, <b>the Editor lab</b> and <b>the DUST pipelines</b></li>
        <li><b>{total_runs}</b> agent validation runs</li>
        <li>14 November 2026</li>
      </ul>
    </header>
    <div class="prose overview">{ov["html"]}</div>
    {"".join(sections)}
    {method}
    <footer class="colophon">Source: the Software Architecture Garden, <code>general/agent-operated-engines/</code>, chapters 00–13 and <code>_validation/</code>.</footer>
  </main>
</div>
<script>
(function () {{
  var details = document.getElementById("index-details");
  var wide = window.matchMedia("(min-width: 980px)");
  function syncOpen() {{ if (wide.matches) details.open = true; }}
  syncOpen();
  if (wide.addEventListener) wide.addEventListener("change", syncOpen);
  details.addEventListener("click", function (e) {{
    if (!wide.matches && e.target.closest("a")) details.open = false;
  }});
  var links = {{}};
  document.querySelectorAll(".nav-list a[data-ch]").forEach(function (a) {{ links[a.dataset.ch] = a; }});
  if (!("IntersectionObserver" in window)) return;
  var current = null;
  var obs = new IntersectionObserver(function (entries) {{
    entries.forEach(function (en) {{
      if (en.isIntersecting && links[en.target.id]) {{
        if (current) current.classList.remove("current");
        current = links[en.target.id];
        current.classList.add("current");
      }}
    }});
  }}, {{ rootMargin: "-20% 0px -70% 0px" }});
  document.querySelectorAll("section.chapter[id^='ch-']").forEach(function (s) {{ obs.observe(s); }});
}})();
</script>
'''
OUT.write_text(page)
print(OUT, len(page), "bytes;", total_runs, "runs;", total_builds, "builds")
for c in chapters[1:]:
    print(c["num"], c["name"], c["stars"], c["status"], c["quiz"], [(b["agent"], b["kind"], b["passed"], b["total"]) for b in c["builds"]])
