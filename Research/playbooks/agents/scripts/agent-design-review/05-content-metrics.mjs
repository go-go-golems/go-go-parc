#!/usr/bin/env node
// Crude, reproducible content metrics for design documents (candidate selection, not proof).
// Usage: node 05-content-metrics.mjs [--families families.json] label=path ...
//   Prose = lines outside frontmatter, fenced code, tables and headings; sentences split on [.!?] + space + capital.
//   families.json: {"name": "regex source", ...}, matched case-insensitively per sentence; a sentence can count in several.
//   Default families suit "spec-heavy design" questions; replace them for other questions.
// Prints a JSON array: words, sentences, words per sentence, code blocks, tables, guarantee phrases, contrast markers,
// semicolons and "simpler/easier" phrases per 1,000 prose words, "would ... but" weighings per 1,000, and the share of
// sentences per family.
import fs from 'node:fs';

let args = process.argv.slice(2);
let families = {
  errorContract: '\\b(status|statuses|error|errors|invalid|reject|rejects|malformed|trap|traps|sentinel|unchanged|overflow|underflow|fuel|capacity|guard|guards|mismatch|-1|-2|wrong-length)\\b',
  testing: '\\b(fixture|fixtures|test|tests|case|cases|seed|seeds|oracle|vector|vectors|golden|directed|profile|profiles)\\b',
  measurement: '\\b(measure|measurement|report|median|record|heat|spill|spills|instructions per|image bytes|ratio)\\b',
  futureFeature: '\\b(future|later|once|when .{0,40}available|becomes available|router|dispatcher|would need|will need|pending)\\b',
};
if (args[0] === '--families') { families = JSON.parse(fs.readFileSync(args[1], 'utf8')); args = args.slice(2); }
const fam = Object.fromEntries(Object.entries(families).map(([k, v]) => [k, new RegExp(v, 'i')]));
const guarantee = /before any (output )?(write|store|writes|stores)|no writes|leave[s]? all .{0,20}bytes alone|unchanged (guest )?memory|defined memory|before the first store/gi;
const contrast = /\b(rather than|instead of|instead,|not only|, not |whereas|unlike|as opposed to)\b/gi;
const simpler = /\b(simpler|simplest|easier|cheaper)\b/gi;
const wouldBut = /\bwould\b[^.]{0,120}\bbut\b/gi;

const rows = [];
for (const arg of args) {
  const i = arg.indexOf('=');
  const label = arg.slice(0, i), file = arg.slice(i + 1);
  const src = fs.readFileSync(file, 'utf8').replace(/^---\n[\s\S]*?\n---\n/, '');
  let inCode = false, codeBlocks = 0, tables = 0, prevTable = false;
  const prose = [];
  for (const line of src.split('\n')) {
    if (/^```/.test(line)) { if (!inCode) codeBlocks++; inCode = !inCode; continue; }
    if (inCode) continue;
    const isTable = /^\s*\|/.test(line);
    if (isTable && !prevTable) tables++;
    prevTable = isTable;
    if (isTable || /^#/.test(line) || !line.trim()) continue;
    prose.push(line.replace(/^\s*([-*]|\d+\.)\s+/, ''));
  }
  const text = prose.join(' ').replace(/\s+/g, ' ');
  const words = src.split(/\s+/).filter(Boolean).length;
  const proseWords = Math.max(text.split(/\s+/).filter(Boolean).length, 1);
  const sentences = text.split(/(?<=[.!?])\s+(?=[A-Z`*\[(])/).filter(s => s.split(' ').length > 2);
  const per1k = re => +(1000 * (text.match(re) || []).length / proseWords).toFixed(2);
  rows.push({
    label, words, proseWords, sentences: sentences.length, wordsPerSentence: +(proseWords / Math.max(sentences.length, 1)).toFixed(1),
    codeBlocks, tables, guaranteePhrases: (src.match(guarantee) || []).length,
    contrastPer1k: per1k(contrast), semicolonsPer1k: per1k(/;/g), simplerPer1k: per1k(simpler), wouldButPer1k: per1k(wouldBut),
    ...Object.fromEntries(Object.entries(fam).map(([k, re]) => [k + '%', +(100 * sentences.filter(s => re.test(s)).length / Math.max(sentences.length, 1)).toFixed(1)])),
  });
}
console.log(JSON.stringify(rows, null, 1));
