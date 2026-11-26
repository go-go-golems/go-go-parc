#!/usr/bin/env node
// Snapshot a running (or finished) implementation round: what each agent has written so far, by category, and what
// it has been doing, from its live rollout. Meant for watching agents for over-testing and harness/framework building.
// Usage: node 11-snapshot-round.mjs <out> <round> [--categories categories.json] [--quiet]
//   Reads $out/<round>/heads.json if present (else derives worktrees from $WORKTREES/<round>-<item> and the base from
//   $BASE), the round's logs for session ids, and the rollouts under $CODEX_HOME/sessions (read only).
//   Lines are counted from `git diff --numstat <base>` (committed and uncommitted) plus untracked files.
//   categories.json: {"name": "regex on the path", ...}, first match wins, in order; the default order is
//   test, source, harness, docs, data, other.
// Appends one JSON line per call to $out/<round>/snapshots.jsonl and prints a table.
import fs from 'node:fs';
import path from 'node:path';
import { execFileSync } from 'node:child_process';

const [out, round, ...rest] = process.argv.slice(2);
const opt = {};
for (let i = 0; i < rest.length; i++) if (rest[i].startsWith('--')) opt[rest[i].slice(2)] = rest[i + 1]?.startsWith('--') || rest[i + 1] === undefined ? true : rest[++i];
const categories = Object.entries(opt.categories ? JSON.parse(fs.readFileSync(opt.categories, 'utf8')) : {
  test: '(^|/)tests?/|\\.test\\.|_test\\.|\\.spec\\.',
  source: '\\.typed$|(^|/)src/|\\.go$|\\.rs$|\\.c$|\\.h$',
  harness: '\\.(m?js|cjs|ts|py|sh)$',
  docs: '\\.md$',
  data: '\\.(json|ya?ml|csv|txt|toml)$',
}).map(([k, v]) => [k, new RegExp(v)]);
const cat = p => (categories.find(([, re]) => re.test(p)) ?? ['other'])[0];
const git = (cwd, ...a) => { try { return execFileSync('git', ['-C', cwd, ...a], { encoding: 'utf8', maxBuffer: 1 << 26 }); } catch { return ''; } };
const codexHome = process.env.CODEX_HOME ?? path.join(process.env.HOME, '.codex');
const dir = path.join(out, round);
const logs = path.join(dir, 'logs');
let heads = {};
if (fs.existsSync(path.join(dir, 'heads.json'))) heads = JSON.parse(fs.readFileSync(path.join(dir, 'heads.json'), 'utf8'));
else for (const f of fs.readdirSync(logs).filter(f => f.endsWith('.log'))) {
  const item = f.slice(0, -4);
  heads[item] = { worktree: path.join(process.env.WORKTREES, `${round}-${item.toLowerCase()}`), base: process.env.BASE };
}
const rollouts = [];
const walk = d => { if (!fs.existsSync(d)) return; for (const e of fs.readdirSync(d, { withFileTypes: true })) { const p = path.join(d, e.name); e.isDirectory() ? walk(p) : e.name.endsWith('.jsonl') && rollouts.push(p); } };
walk(path.join(codexHome, 'sessions'));

const rows = [];
for (const [item, h] of Object.entries(heads)) {
  const w = h.worktree, base = h.base;
  const lines = {}, files = {};
  const add = (p, n) => { const c = cat(p); lines[c] = (lines[c] ?? 0) + n; (files[c] ??= new Set()).add(p); };
  for (const l of git(w, 'diff', '--numstat', base).trim().split('\n').filter(Boolean)) {
    const [a, , p] = l.split('\t'); if (a !== '-') add(p, Number(a));
  }
  for (const p of git(w, 'ls-files', '--others', '--exclude-standard').trim().split('\n').filter(Boolean)) {
    try { add(p, fs.readFileSync(path.join(w, p), 'utf8').split('\n').length); } catch { /* binary or vanished */ }
  }
  const read = p => { try { return fs.readFileSync(path.join(w, p), 'utf8'); } catch { return ''; } };
  const testSrc = [...(files.test ?? [])].map(read).join('\n');
  const codeSrc = [...(files.test ?? []), ...(files.harness ?? [])].map(read).join('\n');
  const commits = git(w, 'rev-list', '--count', `${base}..HEAD`).trim();
  // Live rollout: session id from the log.
  let sid = null, live = {};
  try { sid = (fs.readFileSync(path.join(logs, `${item}.log`), 'utf8').match(/session id:\s*(\S+)/) || [])[1]; } catch { /* not started */ }
  const file = sid && rollouts.find(f => f.includes(sid));
  if (file) {
    const L = fs.readFileSync(file, 'utf8').trim().split('\n').map(l => { try { return JSON.parse(l); } catch { return {}; } });
    const starts = L.map((o, i) => [o, i]).filter(([o]) => o.type === 'event_msg' && o.payload?.type === 'task_started').map(([, i]) => i);
    const T = L.slice(starts.at(-1) ?? 0);
    const cmds = [];
    for (const o of T) if (o.type === 'response_item' && /tool_call$/.test(o.payload?.type ?? '')) {
      const src = o.payload.input ?? o.payload.arguments ?? '';
      for (const m of src.matchAll(/["']?cmd["']?\s*:\s*("(?:[^"\\]|\\.)*"|`(?:[^`\\]|\\.)*`)/g)) { try { cmds.push(m[1].startsWith('`') ? m[1].slice(1, -1) : JSON.parse(m[1])); } catch { cmds.push(m[1]); } }
    }
    // Prefer the authoritative per-command events (they include commands batched inside one code-mode script).
    const executed = T.filter(o => o.type === 'event_msg' && o.payload?.type === 'item_completed' && o.payload.item?.type === 'CommandExecution');
    if (executed.length) { cmds.length = 0; for (const o of executed) { const c = o.payload.item.command; cmds.push(Array.isArray(c) ? c.at(-1) : String(c)); } }
    const t0 = Date.parse(T.find(o => o.type === 'event_msg' && o.payload?.type === 'task_started')?.timestamp ?? NaN);
    const tLast = Date.parse(T.at(-1)?.timestamp ?? NaN);
    const done = T.some(o => o.type === 'event_msg' && o.payload?.type === 'task_complete');
    const commentary = T.filter(o => o.type === 'response_item' && o.payload?.type === 'message' && o.payload.role === 'assistant').map(o => (o.payload.content || []).map(p => p.text || '').join('')).at(-1) ?? '';
    live = {
      minutes: +((tLast - t0) / 60000).toFixed(1), done,
      toolCalls: T.filter(o => o.type === 'response_item' && /tool_call$/.test(o.payload?.type ?? '')).length,
      commands: cmds.length,
      testRuns: cmds.filter(c => /node --test|npm (run )?test|go test|pytest|vitest|jest/.test(c)).length,
      builds: cmds.filter(c => /npm run build|tsc\b|go build|cargo build/.test(c)).length,
      last: commentary.replace(/\s+/g, ' ').slice(0, 160),
    };
  }
  rows.push({
    item, commits: Number(commits || 0), lines,
    testCases: (testSrc.match(/^\s*(test|it)\s*\(/gm) || []).length,
    assertions: (testSrc.match(/\bassert(\.\w+)?\s*\(/g) || []).length,
    functionsInTestsAndHarness: (codeSrc.match(/\bfunction\s+\w+|\b(const|let)\s+\w+\s*=\s*(async\s*)?(\([^)]*\)|\w+)\s*=>/g) || []).length,
    outsideFiles: [...Object.values(files).flatMap(s => [...s])].filter(p => /^(src|tools)\//.test(p)),
    ...live,
  });
}
fs.appendFileSync(path.join(dir, 'snapshots.jsonl'), JSON.stringify({ at: new Date().toISOString(), rows }) + '\n');
if (!opt.quiet) {
  const cats = [...new Set(rows.flatMap(r => Object.keys(r.lines)))];
  const head = ['item', 'min', 'done', 'commits', ...cats.map(c => c + ' +'), 'tests', 'asserts', 'fns', 'testRuns', 'outside src/tools'];
  console.log(head.join('\t'));
  for (const r of rows) console.log([r.item, r.minutes ?? '-', r.done ? 'yes' : 'no', r.commits, ...cats.map(c => r.lines[c] ?? 0), r.testCases, r.assertions, r.functionsInTestsAndHarness, r.testRuns ?? '-', r.outsideFiles.length].join('\t'));
  for (const r of rows) if (r.last) console.log(`  ${r.item}: ${r.last}`);
}
