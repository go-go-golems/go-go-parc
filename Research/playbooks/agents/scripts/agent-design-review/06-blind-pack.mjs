#!/usr/bin/env node
// Pack every round's documents for a blind judge: one file per (item, round), shuffled, with frontmatter and any
// round-revealing trailing section removed. The key stays outside the judge's directory.
// Usage: node 06-blind-pack.mjs <out> <judge-dir> --rounds r1,r2,r3 --doc-regex '<regex on repo path>' [--strip '<regex>'] [--seed 18]
//   For each round, $out/<round>/heads.json gives {item: {worktree, rev}}; the document is the file at that revision
//   whose path matches --doc-regex and contains the item id (case-insensitive) when more than one matches.
//   A resumed round's earlier documents are read at the earlier round's recorded rev, so later commits do not leak in.
//   --strip: heading regex (whole line, without the #s); the LAST matching level-2/3 heading and everything after it is
//   removed. Default matches whole words cut/cuts/simplif*/self-review (a substring match once hit "Executive").
// Writes <judge-dir>/docs/doc-A.md ..., and $out/results/blind-key.json [{name, item, round, rev, path, words}].
import fs from 'node:fs';
import path from 'node:path';
import { execFileSync } from 'node:child_process';

const [out, judgeDir, ...rest] = process.argv.slice(2);
const opt = {};
for (let i = 0; i < rest.length; i += 2) opt[rest[i].replace(/^--/, '')] = rest[i + 1];
const rounds = opt.rounds.split(',');
const docRe = new RegExp(opt['doc-regex']);
const stripRe = new RegExp(`\\n#{2,3} [^\\n]*${opt.strip ?? '\\b(cuts?|simplif\\w*|self-review)\\b'}[^\\n]*\\n`, 'gi');
let seed = Number(opt.seed ?? 18);
const rnd = () => ((seed = (seed * 1103515245 + 12345) % 2147483648) / 2147483648);
const git = (cwd, ...a) => execFileSync('git', ['-C', cwd, ...a], { encoding: 'utf8', maxBuffer: 1 << 26 });

const items = [];
for (const round of rounds) {
  const heads = JSON.parse(fs.readFileSync(path.join(out, round, 'heads.json'), 'utf8'));
  for (const [item, h] of Object.entries(heads)) {
    const paths = git(h.worktree, 'ls-tree', '-r', '--name-only', h.rev).split('\n').filter(p => docRe.test(p));
    const p = paths.length > 1 ? paths.find(x => x.toLowerCase().includes(item.toLowerCase())) ?? paths[0] : paths[0];
    if (!p) { console.error(`${round}/${item}: no document matches at ${h.rev}`); continue; }
    items.push({ item, round, rev: h.rev, path: p, text: git(h.worktree, 'show', `${h.rev}:${p}`) });
  }
}
const strip = src => {
  src = src.replace(/^---\n[\s\S]*?\n---\n/, '');
  const m = [...src.matchAll(stripRe)].pop();
  return m ? src.slice(0, m.index) + '\n' : src;
};
const order = items.map(it => ({ it, k: rnd() })).sort((a, b) => a.k - b.k).map(x => x.it);
fs.mkdirSync(path.join(judgeDir, 'docs'), { recursive: true });
fs.mkdirSync(path.join(out, 'results'), { recursive: true });
const name = i => `doc-${i < 26 ? String.fromCharCode(65 + i) : String.fromCharCode(65 + Math.floor(i / 26) - 1) + String.fromCharCode(65 + (i % 26))}.md`;
const key = order.map((it, i) => {
  const body = strip(it.text);
  fs.writeFileSync(path.join(judgeDir, 'docs', name(i)), body);
  return { name: name(i), item: it.item, round: it.round, rev: it.rev, path: it.path, words: body.split(/\s+/).filter(Boolean).length, fullWords: it.text.split(/\s+/).filter(Boolean).length };
});
fs.writeFileSync(path.join(out, 'results', 'blind-key.json'), JSON.stringify(key, null, 1));
for (const k of key) console.log(`${k.name}\t${k.item}\t${k.words}w${k.words < 0.5 * k.fullWords ? '  <- stripped more than half: check --strip' : ''}`);
