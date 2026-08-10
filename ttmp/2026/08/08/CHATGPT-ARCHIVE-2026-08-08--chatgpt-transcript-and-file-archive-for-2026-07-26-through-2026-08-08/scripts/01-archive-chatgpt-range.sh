#!/usr/bin/env bash
set -euo pipefail
TAB=441403940
START=2026-07-26
END=2026-08-08
VAULT=/home/manuel/code/wesen/go-go-golems/go-go-parc
ROOT="$VAULT/Transcripts"
LIST=/tmp/chatgpt-archive-range.list
RAW=/tmp/chatgpt-archive-range.raw
surf-go js --tab-id "$TAB" --timeout-ms 120000 "
const s = await fetch('/api/auth/session', {credentials:'include'});
const token = (await s.json()).accessToken;
if (!token) throw new Error('ChatGPT login required');
const out = [];
for (let offset = 0; ; offset += 100) {
  const r = await fetch('/backend-api/conversations?offset=' + offset + '&limit=100&order=updated', {credentials:'include', headers:{Authorization:'Bearer ' + token}});
  const j = await r.json();
  const items = j.items || [];
  if (!items.length) break;
  for (const it of items) {
    const day = (it.update_time || '').slice(0, 10);
    if (day >= '${START}' && day <= '${END}') out.push(day + '|' + it.id + '|' + (it.title || 'Untitled'));
  }
  const oldest = (items[items.length - 1].update_time || '').slice(0, 10);
  if (oldest < '${START}') break;
}
return out.join('\\n');
" 2>&1 | tee "$RAW"
sed "s/^content: '//; s/'$//" "$RAW" | sed 's/^"//; s/"$//' | sed 's/\\n/\n/g' | grep -E '^[0-9]{4}-[0-9]{2}-[0-9]{2}\|[0-9a-f]{8}-' > "$LIST" || true
printf 'Conversations in range: %s\n' "$(wc -l < "$LIST")"
new=0; skipped=0; files=0
while IFS='|' read -r day id title; do
  [ -z "$id" ] && continue
  year=${day%%-*}; rest=${day#*-}; month=${rest%%-*}; date_day=${rest#*-}
  dir="$ROOT/$year/$month/$date_day"
  mkdir -p "$dir"
  safe=$(printf '%s' "$title" | tr '/' '_' | tr -cd 'A-Za-z0-9 _.-' | sed 's/  */ /g; s/^ *//; s/ *$//' | cut -c1-70)
  [ -n "$safe" ] || safe=Untitled
  dest="$dir/CHATGPT TRANSCRIPT - $safe.md"
  url="https://chatgpt.com/c/$id"
  if grep -rlF "$url" "$dir"/CHATGPT*.md 2>/dev/null | head -1 | grep -q .; then
    skipped=$((skipped+1))
  else
    printf 'TRANSCRIPT %s %s\n' "$day" "$safe"
    if surf-go chatgpt transcript --from-api --conversation-id "$id" --tab-id "$TAB" --timeout-ms 120000 2>/dev/null > "$dest"; then new=$((new+1)); else rm -f "$dest"; echo "FAILED transcript $id" >&2; fi
  fi
  convdir="$dir/$safe"
  before=$(find "$convdir" -type f 2>/dev/null | wc -l || true)
  surf-go chatgpt download --conversation-id "$id" --tab-id "$TAB" --output-dir "$convdir" --timeout-ms 120000 --skip-existing 2>/dev/null || echo "FAILED files $id" >&2
  nested="$convdir/$id"
  if [ -d "$nested" ]; then mv "$nested"/* "$convdir"/ 2>/dev/null || true; rmdir "$nested" 2>/dev/null || true; fi
  rm -f "$convdir/manifest.json"
  after=$(find "$convdir" -type f 2>/dev/null | wc -l || true)
  files=$((files + after - before))
  if [ "$after" -eq 0 ] && [ -d "$convdir" ]; then rmdir "$convdir" 2>/dev/null || true; fi
  sleep 0.4
done < "$LIST"
printf 'DONE new_transcripts=%s skipped=%s files_new=%s\n' "$new" "$skipped" "$files"
