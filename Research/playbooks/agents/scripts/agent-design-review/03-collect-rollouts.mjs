#!/usr/bin/env node
// Find each agent's native Codex rollout and the approval sidecars of a round; for a resumed round, cut out the
// resumed turn so it can be analysed on its own.
// Usage: node 03-collect-rollouts.mjs <out> <round> [--turn N]
//   Reads $out/<round>/logs/*.log ("session id: <uuid>") and $out/<round>/heads.json (worktree per item).
//   --turn N  analyse turn N (default 1): keep session_meta plus the records from the Nth task_started up to the next
//             one. `codex exec resume` appends its turn to the same rollout, so a baseline that was later resumed must
//             be cut to turn 1, and the first resume is turn 2. A single-turn rollout is used as it is.
// Writes: $out/<round>/rollouts/sessions.tsv (item, rollout path), sidecars.tsv (item, path), and for --turn the cut
//         files in $out/<round>/rollouts/. Never modifies ~/.codex.
import fs from 'node:fs';
import path from 'node:path';

const [out, round, ...rest] = process.argv.slice(2);
const turn = rest[0] === '--turn' ? Number(rest[1]) : 1;
const codexHome = process.env.CODEX_HOME ?? path.join(process.env.HOME, '.codex');
const dir = path.join(out, round);
const heads = JSON.parse(fs.readFileSync(path.join(dir, 'heads.json'), 'utf8'));
const rdir = path.join(dir, 'rollouts');
fs.mkdirSync(rdir, { recursive: true });

const all = [];
const walk = d => { for (const e of fs.readdirSync(d, { withFileTypes: true })) { const p = path.join(d, e.name); e.isDirectory() ? walk(p) : e.name.endsWith('.jsonl') && all.push(p); } };
walk(path.join(codexHome, 'sessions'));

const head = (f, n = 200000) => { const fd = fs.openSync(f, 'r'); const b = Buffer.alloc(n); const k = fs.readSync(fd, b, 0, n, 0); fs.closeSync(fd); return b.subarray(0, k).toString('utf8'); };
const isSidecar = f => head(f).includes('whose request action you are assessing');
const cwdOf = f => (head(f, 30000).match(/"cwd":"([^"]*)"/) || [])[1] ?? '';

const sessions = [], sidecars = [];
for (const item of Object.keys(heads)) {
  const log = path.join(dir, 'logs', `${item}.log`);
  const sid = (fs.readFileSync(log, 'utf8').match(/session id:\s*(\S+)/) || [])[1];
  const file = sid && all.find(f => f.includes(sid));
  if (!file) { console.error(`${item}: no rollout for session ${sid}`); continue; }
  let use = file;
  const lines = fs.readFileSync(file, 'utf8').trim().split('\n');
  const starts = lines.map((l, i) => [JSON.parse(l), i]).filter(([o]) => o.type === 'event_msg' && o.payload?.type === 'task_started').map(([, i]) => i);
  if (starts.length < turn) { console.error(`${item}: only ${starts.length} turns`); continue; }
  if (starts.length > 1) {
    const meta = turn > 1 ? lines.filter(l => JSON.parse(l).type === 'session_meta') : [];
    use = path.join(rdir, `${item}.turn${turn}.jsonl`);
    fs.writeFileSync(use, [...meta, ...lines.slice(turn > 1 ? starts[turn - 1] : 0, starts[turn] ?? lines.length)].join('\n') + '\n');
  }
  sessions.push([item, use]);
  // Sidecars share the worktree with every round run there, so keep only those that start inside this turn's window.
  const recs = fs.readFileSync(use, 'utf8').trim().split('\n').map(l => JSON.parse(l));
  const s0 = recs.find(o => o.type === 'event_msg' && o.payload?.type === 'task_started')?.timestamp;
  const s1 = recs.find(o => o.type === 'event_msg' && o.payload?.type === 'task_complete')?.timestamp ?? recs.at(-1).timestamp;
  const wt = heads[item].worktree;
  for (const f of all) {
    if (f === file || cwdOf(f) !== wt || !isSidecar(f)) continue;
    const t = (head(f, 20000).match(/"timestamp":"([^"]+)"/) || [])[1];
    if (t >= s0 && t <= s1) sidecars.push([item, f]);
  }
}
fs.writeFileSync(path.join(rdir, 'sessions.tsv'), sessions.map(r => r.join('\t')).join('\n') + '\n');
fs.writeFileSync(path.join(rdir, 'sidecars.tsv'), sidecars.map(r => r.join('\t')).join('\n') + '\n');
console.log(`${round}: ${sessions.length} sessions, ${sidecars.length} sidecars -> ${rdir}`);
