#!/usr/bin/env node
// Check that every quote a judge gave (any field ending in "_quotes" or "_quote") occurs verbatim in its document,
// ignoring whitespace and typographic-quote differences, and dropping bracketed judge annotations such as
// "[6 items]" or "[but proposes ...]" (a bracketed span is dropped only when the document does not contain it, so
// brackets that belong to the text, like a regex class "[c-a]", are kept).
// Usage: node 07-verify-quotes.mjs <judge-dir>      (reads scores.json and docs/)
import fs from 'node:fs';
import path from 'node:path';
const dir = process.argv[2];
const scores = JSON.parse(fs.readFileSync(path.join(dir, 'scores.json'), 'utf8'));
const norm = s => s.replace(/[\u2018\u2019]/g, "'").replace(/[\u201c\u201d]/g, '"').replace(/\s+/g, ' ').trim();
const dropAnnotations = (q, doc) => q.replace(/\[[^\]]*\]/g, m => (doc.includes(m) ? m : ' '));
let total = 0, missing = 0;
for (const s of scores) {
  const doc = norm(fs.readFileSync(path.join(dir, 'docs', s.doc), 'utf8'));
  for (const [k, v] of Object.entries(s)) {
    if (!/_quotes?$/.test(k)) continue;
    for (const q of [].concat(v ?? [])) {
      // A quote may elide with "..." or "…": every fragment must occur, in order.
      const parts = norm(dropAnnotations(String(q), doc)).split(/\s*(?:\.\.\.|…)\s*/).filter(p => p.length > 3);
      if (!parts.length) continue;
      total++;
      let at = 0, ok = true;
      for (const p of parts) { const i = doc.indexOf(p, at); if (i < 0) { ok = false; break; } at = i + p.length; }
      if (!ok) { missing++; console.log(`${s.doc} ${k}: not found: ${String(q).slice(0, 120)}`); }
    }
  }
}
console.log(`${total - missing}/${total} quotes found verbatim`);
process.exit(missing ? 1 : 0);
