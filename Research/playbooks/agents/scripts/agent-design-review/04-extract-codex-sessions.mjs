#!/usr/bin/env node
// What each Codex agent was shown and what it did, from native rollouts.
// Usage: node 04-extract-codex-sessions.mjs <sessions.tsv> <out-dir>
//   sessions.tsv: "<item>\t<rollout path>" per line (from 03-collect-rollouts.mjs).
// Writes per item: commands.tsv (index, command; from CommandExecution events when the rollout has them), reads.tsv (paths passed to cat/sed/head/tail/nl),
//   messages.md (assistant commentary); once: system-prompt.md, skills-catalogue.md, agents-md.md, multi-agent.md
//   (identical across sessions up to paths; differences are reported); summary.json with, per item: model, effort,
//   minutes (first task_started to first task_complete), tool calls, commands, interpreter runs (commands invoking
//   node/python/deno/tsx/bun: probes, but also scripts that edit files, so read them before calling them probes),
//   skill files read, token totals (total includes cached input; output and reasoning are the generated part).
// Reasoning items are usually encrypted; the script counts them and any summaries but cannot read them.
import fs from 'node:fs';
import path from 'node:path';

const [tsv, outDir] = process.argv.slice(2);
const rows = fs.readFileSync(tsv, 'utf8').trim().split('\n').map(l => l.split('\t'));
fs.mkdirSync(outDir, { recursive: true });
const text = item => (item.payload.content || []).map(p => p.text || p.input_text || '').join('');
const shared = {}, differs = {}, summary = [];

for (const [id, file] of rows) {
  const L = fs.readFileSync(file, 'utf8').trim().split('\n').map(l => JSON.parse(l));
  const dir = path.join(outDir, id);
  fs.mkdirSync(dir, { recursive: true });
  const msgs = L.filter(l => l.type === 'response_item' && l.payload.type === 'message');
  const dev = msgs.filter(m => m.payload.role === 'developer').map(text);
  const user = msgs.filter(m => m.payload.role === 'user').map(text);
  const asst = msgs.filter(m => m.payload.role === 'assistant').map(text);
  // Context pieces as Codex sends them: developer[0] system prompt, developer[1] skills, the rest multi-agent blocks;
  // user[0] is AGENTS.md plus environment context when an AGENTS.md applies. A resumed turn has none of these.
  if (dev.length >= 2) {
    const ctx = { 'system-prompt': dev[0], 'skills-catalogue': dev[1], 'multi-agent': dev.slice(2).join('\n\n---\n\n'), 'agents-md': user[0]?.startsWith('# AGENTS.md') ? user[0] : '' };
    const norm = s => s.replace(/\/[^\s`"<>]*worktrees\/[^\s/`"<>]+/g, '<worktree>');
    for (const [k, v] of Object.entries(ctx)) {
      if (shared[k] === undefined) shared[k] = v;
      else if (norm(shared[k]) !== norm(v)) (differs[k] ??= []).push(id);
    }
  }
  const calls = L.filter(l => l.type === 'response_item' && /tool_call$/.test(l.payload.type));
  const commands = [], tools = {};
  calls.forEach((c, i) => {
    const src = c.payload.input ?? c.payload.arguments ?? '';
    for (const m of src.matchAll(/tools\.(\w+)\(/g)) tools[m[1]] = (tools[m[1]] || 0) + 1;
    if (!/tools\./.test(src)) tools[c.payload.name] = (tools[c.payload.name] || 0) + 1;
    // Code-mode exec: JS calling tools.exec_command({cmd:"..."}); classic function calls carry {"cmd": ...} JSON.
    for (const m of src.matchAll(/["']?cmd["']?\s*:\s*("(?:[^"\\]|\\.)*"|`(?:[^`\\]|\\.)*`|\[(?:[^\]\\]|\\.)*\])/g)) {
      let cmd = m[1];
      try { cmd = cmd.startsWith('`') ? cmd.slice(1, -1) : JSON.parse(cmd); } catch { /* keep raw */ }
      commands.push({ seq: i, cmd: Array.isArray(cmd) ? cmd.join(' ') : cmd });
    }
  });
  // Authoritative record when present: every command Codex actually ran is an item_completed event of type
  // CommandExecution (command, parsed_cmd with read paths, exit_code). It sees commands a model batches inside one
  // code-mode script (for example an array mapped over tools.exec_command), which the regex above misses.
  const executed = L.filter(l => l.type === 'event_msg' && l.payload?.type === 'item_completed' && l.payload.item?.type === 'CommandExecution').map(l => l.payload.item);
  const parsedReads = [];
  if (executed.length) {
    commands.length = 0;
    executed.forEach((x, i) => {
      const cmd = Array.isArray(x.command) ? (x.command.at(-1) ?? '') : String(x.command ?? '');
      commands.push({ seq: i, cmd, exit: x.exit_code });
      for (const pc of x.parsed_cmd ?? []) if (pc.type === 'read' && pc.path) parsedReads.push([pc.path, i]);
    });
  }
  fs.writeFileSync(path.join(dir, 'commands.tsv'), commands.map(c => `${c.seq}\t${c.cmd.replace(/\n/g, '\\n')}`).join('\n') + '\n');
  const reads = new Map(parsedReads.filter(([p]) => p).map(([p, s]) => [p, s]));
  for (const { seq, cmd } of commands)
    for (const m of cmd.matchAll(/(?:^|[;&|(]\s*|\s)(?:cat|sed -n '[^']*'|sed -n "[^"]*"|sed -n \S+|head(?: -n? ?\d+)?|tail(?: -n? ?\d+)?|nl -ba)\s+((?:[^\s;&|<>]+\s*)+)/g))
      for (const p of m[1].split(/\s+/)) if (/[./]/.test(p) && !p.startsWith('-') && !/^\d/.test(p) && !reads.has(p)) reads.set(p, seq);
  fs.writeFileSync(path.join(dir, 'reads.tsv'), [...reads].map(([p, s]) => `${s}\t${p}`).join('\n') + '\n');
  fs.writeFileSync(path.join(dir, 'messages.md'), asst.map((t, i) => `## ${i + 1}\n\n${t}\n`).join('\n'));
  const ev = t => L.find(l => l.type === 'event_msg' && l.payload?.type === t)?.timestamp;
  const t0 = ev('task_started'), t1 = ev('task_complete');
  const tokens = L.filter(l => l.type === 'event_msg' && l.payload?.type === 'token_count').map(l => l.payload.info?.total_token_usage).filter(Boolean).pop() ?? null;
  const reasoning = L.filter(l => l.type === 'response_item' && l.payload.type === 'reasoning');
  const turnCtx = L.find(l => l.type === 'turn_context')?.payload ?? {};
  summary.push({
    id, file, model: turnCtx.model ?? null, effort: turnCtx.effort ?? null,
    minutes: t0 && t1 ? +((Date.parse(t1) - Date.parse(t0)) / 60000).toFixed(1) : null,
    toolCalls: calls.length, commands: commands.length, commandSource: executed.length ? 'CommandExecution events' : 'tool-call text', failedCommands: commands.filter(c => c.exit && c.exit !== 0).length, tools,
    interpreterRuns: commands.filter(c => /(^|[\s;&|(])(node|python3?|deno|tsx|bun)\s/.test(c.cmd)).length,
    skillReads: [...reads.keys()].filter(p => /\/skills\//.test(p)),
    reasoningItems: reasoning.length, reasoningSummaries: reasoning.filter(r => (r.payload.summary || []).length).length,
    tokens,
  });
}
for (const [k, v] of Object.entries(shared)) fs.writeFileSync(path.join(outDir, `${k}.md`), v ?? '');
fs.writeFileSync(path.join(outDir, 'summary.json'), JSON.stringify({ sharedLengths: Object.fromEntries(Object.entries(shared).map(([k, v]) => [k, v?.length ?? 0])), differs, sessions: summary }, null, 2));
for (const s of summary) console.log(`${s.id.padEnd(10)} ${String(s.minutes).padStart(5)} min  calls ${String(s.toolCalls).padStart(3)}  cmds ${String(s.commands).padStart(3)}  interp ${String(s.interpreterRuns).padStart(2)}  skills: ${s.skillReads.map(p => p.replace(/.*\/skills\//, '')).join(', ') || '-'}`);
if (Object.keys(differs).length) console.log('context differs beyond worktree paths:', differs);
