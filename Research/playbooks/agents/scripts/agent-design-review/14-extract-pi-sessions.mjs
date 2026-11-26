#!/usr/bin/env node
// Extract what Pi agents saw and did from their sessions (the Pi counterpart of 04-extract-codex-sessions.mjs).
// Usage: node 14-extract-pi-sessions.mjs <out> <round> [--turn N]
//   Reads $out/<round>/sessions/<item>/*.jsonl. Writes $out/<round>/extract/<item>/{commands.tsv,reads.tsv,messages.md},
//   $out/<round>/extract/system-sections.json (section sizes of the first item's system message) and summary.json,
//   and prints one line per item. --turn N keeps only the Nth user turn and what follows it, up to the next user
//   message (a resumed session appends turns to the same file); default: all turns.
import fs from 'node:fs';
import path from 'node:path';

const [out, round, ...rest] = process.argv.slice(2);
const turn = rest.includes('--turn') ? Number(rest[rest.indexOf('--turn') + 1]) : null;
const dir = path.join(out, round, 'sessions');
const X = path.join(out, round, 'extract');
fs.mkdirSync(X, { recursive: true });
const summary = {};
let sections = null;
for (const item of fs.readdirSync(dir).sort()) {
  const file = fs.readdirSync(path.join(dir, item)).find(f => f.endsWith('.jsonl'));
  if (!file) continue;
  let L = fs.readFileSync(path.join(dir, item, file), 'utf8').trim().split('\n').map(l => JSON.parse(l));
  const sys = L.find(o => o.type === 'message' && o.message?.role === 'system');
  if (sys && !sections) sections = Object.fromEntries(Object.entries(sys.message.sections ?? {}).map(([k, v]) => [k, v.length]));
  if (turn) {
    const users = L.map((o, i) => [o, i]).filter(([o]) => o.type === 'message' && o.message?.role === 'user').map(([, i]) => i);
    L = L.slice(users[turn - 1], users[turn] ?? L.length);
  }
  const msgs = L.filter(o => o.type === 'message').map(o => o.message);
  const calls = [], reads = [], texts = [];
  let input = 0, output = 0, cacheRead = 0;
  for (const m of msgs) {
    if (m.role !== 'assistant') continue;
    const u = m.usage ?? {};
    input += u.input ?? 0; output += u.output ?? 0; cacheRead += u.cacheRead ?? 0;
    for (const c of m.content ?? []) {
      if (c.type === 'text' && c.text?.trim()) texts.push(c.text.trim());
      if (c.type === 'toolCall') {
        calls.push(c);
        if (c.name === 'read') reads.push(c.arguments?.path ?? c.arguments?.file_path ?? '');
      }
    }
  }
  const cmds = calls.filter(c => c.name === 'bash').map(c => String(c.arguments?.command ?? ''));
  for (const c of cmds) for (const m of c.matchAll(/(?:cat|sed -n [^ ]+|head(?: -n ?\d+)?|less)\s+([^\s|;&>]+\.(?:md|ts|mjs|js|json|tix|typed))/g)) reads.push(m[1]);
  const skills = [...new Set(reads.filter(p => /skills\/[^/]+\/(SKILL\.md|references\/)/.test(p)).map(p => p.replace(/.*skills\//, '')))];
  const ts = L.map(o => Date.parse(o.timestamp)).filter(Number.isFinite);
  const minutes = +((Math.max(...ts) - Math.min(...ts)) / 60000).toFixed(1);
  const byTool = {};
  for (const c of calls) byTool[c.name] = (byTool[c.name] ?? 0) + 1;
  const xi = path.join(X, item);
  fs.mkdirSync(xi, { recursive: true });
  fs.writeFileSync(path.join(xi, 'commands.tsv'), 'n\tcmd\n' + cmds.map((c, i) => `${i}\t${c.replace(/\s+/g, ' ')}`).join('\n') + '\n');
  fs.writeFileSync(path.join(xi, 'reads.tsv'), 'path\n' + reads.join('\n') + '\n');
  fs.writeFileSync(path.join(xi, 'messages.md'), texts.map((t, i) => `## ${i}\n\n${t}\n`).join('\n'));
  const interpreterRuns = cmds.filter(c => /\bnode\s+(-e|--input-type|-\s|<<)|python3?\s+(-c|-\s|<<)/.test(c)).length;
  summary[item] = { minutes, toolCalls: calls.length, byTool, commands: cmds.length, interpreterRuns, skills, tokens: { input, output, cacheRead } };
  console.log(`${item.padEnd(12)} ${String(minutes).padStart(5)} min  calls ${String(calls.length).padStart(3)}  cmds ${String(cmds.length).padStart(3)}  interp ${String(interpreterRuns).padStart(2)}  tools ${JSON.stringify(byTool)}  skills: ${skills.join(', ') || '-'}`);
}
fs.writeFileSync(path.join(X, 'summary.json'), JSON.stringify(summary, null, 1));
if (sections) fs.writeFileSync(path.join(X, 'system-sections.json'), JSON.stringify(sections, null, 1));
