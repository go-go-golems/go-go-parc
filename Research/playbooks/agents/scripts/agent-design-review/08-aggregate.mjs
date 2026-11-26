#!/usr/bin/env node
// Join judge scores with the blind key and summarize per round. Counts (R*) are summed; scales are averaged;
// yes/no items are counted as "yes".
// Usage: node 08-aggregate.mjs <scores.json> <blind-key.json> [--order r1,r2,r3] [--md out.md]
import fs from 'node:fs';
const [scoresPath, keyPath, ...rest] = process.argv.slice(2);
const opt = {}; for (let i = 0; i < rest.length; i += 2) opt[rest[i].replace(/^--/, '')] = rest[i + 1];
const scores = JSON.parse(fs.readFileSync(scoresPath, 'utf8'));
const key = Object.fromEntries(JSON.parse(fs.readFileSync(keyPath, 'utf8')).map(k => [k.name, k]));
const rows = scores.map(s => ({ ...s, item: key[s.doc]?.item ?? key[s.doc]?.id ?? s.item ?? s.program, round: key[s.doc]?.round, words: key[s.doc]?.words }));
const rounds = opt.order ? opt.order.split(',') : [...new Set(rows.map(r => r.round))];
const fields = Object.keys(scores[0]).filter(k => !/_quotes?$|^(doc|item|program|justification)$/.test(k));
const yes = v => /^(yes|true)$/i.test(String(v));
const isYesNo = f => rows.every(r => /^(yes|no|true|false)$/i.test(String(r[f])));
const summary = rounds.map(round => {
  const xs = rows.filter(r => r.round === round);
  const o = { round, n: xs.length, words: Math.round(xs.reduce((a, r) => a + (r.words ?? 0), 0) / xs.length) };
  for (const f of fields) {
    if (isYesNo(f)) o[f + ' (yes)'] = xs.filter(r => yes(r[f])).length;
    else if (/^R\d+$/.test(f)) o[f + ' (sum)'] = xs.reduce((a, r) => a + Number(r[f] ?? 0), 0);
    else o[f + ' (mean)'] = +(xs.reduce((a, r) => a + Number(r[f] ?? 0), 0) / xs.length).toFixed(2);
  }
  return o;
});
const cols = Object.keys(summary[0]);
const md = ['| ' + cols.join(' | ') + ' |', '|' + cols.map(() => '---').join('|') + '|', ...summary.map(s => '| ' + cols.map(c => s[c]).join(' | ') + ' |')].join('\n');
console.log(md);
const perItem = [...new Set(rows.map(r => r.item))].sort().map(item => Object.fromEntries([['item', item], ...rounds.map(rd => { const r = rows.find(x => x.item === item && x.round === rd); return [rd, r ? `${r.over_engineering}/${r.fitness}` : '-']; })]));
console.log('\nover_engineering/fitness per item:'); console.table(perItem);
if (opt.md) fs.writeFileSync(opt.md, md + '\n');
fs.writeFileSync(scoresPath.replace(/\.json$/, '') + '.summary.json', JSON.stringify({ summary, rows: rows.map(({ justification, ...r }) => Object.fromEntries(Object.entries(r).filter(([k]) => !/_quotes?$/.test(k)))) }, null, 1));
