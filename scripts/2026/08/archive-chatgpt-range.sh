#!/usr/bin/env bash
# archive-chatgpt-range.sh — Download and archive ChatGPT transcripts + files for a date range.
#
# Adapted from ttmp/2026/08/08/CHATGPT-ARCHIVE-2026-08-08/.../scripts/01-archive-chatgpt-range.sh
# (paginated bulk archive script proven on the 2026-07-26..2026-08-08 run).
#
# Usage: archive-chatgpt-range.sh [START] [END] [TAB_ID]
#   START   Inclusive start date YYYY-MM-DD (default: 2026-08-09)
#   END     Inclusive end date YYYY-MM-DD   (default: 2026-08-20)
#   TAB_ID  ChatGPT surf tab id as an INTEGER (default: 441404363)
#
# Env overrides: START / END / TAB
#
# Outputs:
#   - Transcripts:  $VAULT/Transcripts/YYYY/MM/DD/CHATGPT TRANSCRIPT - <title>.md
#   - Output files: $VAULT/Transcripts/YYYY/MM/DD/<title>/  (flattened, no manifest.json)
#   - Log:           /tmp/chatgpt-archive-range.log
#   - Failures:     /tmp/chatgpt-archive-range.failures
#
# Skip-by-URL: a conversation whose https://chatgpt.com/c/<id> URL is already
# present in that day's CHATGPT*.md files is skipped (idempotent re-runs).

set -euo pipefail

VAULT="${VAULT:-${HOME}/code/wesen/go-go-golems/go-go-parc}"
ROOT="${VAULT}/Transcripts"
START="${START:-${1:-2026-08-09}}"
END="${END:-${2:-2026-08-20}}"
TAB="${TAB:-${3:-441404363}}"

SURF_SOCKET_PATH="${SURF_SOCKET_PATH:-${HOME}/snap/chromium/common/surf-cli/surf.sock}"
export SURF_SOCKET_PATH

LIST=/tmp/chatgpt-archive-range.list
RAW=/tmp/chatgpt-archive-range.raw
LOG=/tmp/chatgpt-archive-range.log
FAIL=/tmp/chatgpt-archive-range.failures

: > "$LOG"
: > "$FAIL"

echo "=== ChatGPT range archive: ${START} .. ${END} (tab ${TAB}) ===" | tee -a "$LOG"

# --- Step 1: Paginated conversation discovery (stop when oldest item predates START) ---
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
" 2>&1 | tee -a "$LOG" | tee "$RAW"

sed "s/^content: '//; s/'$//" "$RAW" \
  | sed 's/^"//; s/"$//' \
  | sed 's/\\n/\n/g' \
  | grep -E '^[0-9]{4}-[0-9]{2}-[0-9]{2}\|[0-9a-f]{8}-' > "$LIST" || true

TOTAL=$(wc -l < "$LIST")
printf 'Conversations in range: %s\n' "$TOTAL" | tee -a "$LOG"

if [ "$TOTAL" -eq 0 ]; then
  echo "No conversations found for range ${START}..${END}. Done." | tee -a "$LOG"
  exit 0
fi

new=0; skipped=0; files=0; fail_t=0; fail_f=0
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
    printf 'SKIP %s %s\n' "$day" "$safe" | tee -a "$LOG"
  else
    printf 'TRANSCRIPT %s %s\n' "$day" "$safe" | tee -a "$LOG"
    if surf-go chatgpt transcript --from-api --conversation-id "$id" --tab-id "$TAB" --timeout-ms 120000 2>/dev/null > "$dest"; then
      new=$((new+1))
    else
      rm -f "$dest"
      printf 'FAILED transcript %s %s\n' "$day" "$id" | tee -a "$LOG"
      printf '%s\t%s\t%s\n' "$day" "$id" "transcript" >> "$FAIL"
      fail_t=$((fail_t+1))
    fi
  fi

  convdir="$dir/$safe"
  before=$(find "$convdir" -type f 2>/dev/null | wc -l || true)
  if ! surf-go chatgpt download --conversation-id "$id" --tab-id "$TAB" --output-dir "$convdir" --timeout-ms 120000 --skip-existing 2>/dev/null; then
    printf 'FAILED files %s %s\n' "$day" "$id" | tee -a "$LOG"
    printf '%s\t%s\t%s\n' "$day" "$id" "files" >> "$FAIL"
    fail_f=$((fail_f+1))
  fi
  nested="$convdir/$id"
  if [ -d "$nested" ]; then mv "$nested"/* "$convdir"/ 2>/dev/null || true; rmdir "$nested" 2>/dev/null || true; fi
  rm -f "$convdir/manifest.json"
  after=$(find "$convdir" -type f 2>/dev/null | wc -l || true)
  files=$((files + after - before))
  if [ "$after" -eq 0 ] && [ -d "$convdir" ]; then rmdir "$convdir" 2>/dev/null || true; fi
  sleep 0.4
done < "$LIST"

{
  printf '=== DONE range=%s..%s total=%s new_transcripts=%s skipped=%s files_new=%s failed_transcripts=%s failed_files=%s ===\n' \
    "$START" "$END" "$TOTAL" "$new" "$skipped" "$files" "$fail_t" "$fail_f"
  printf 'Failures manifest: %s\n' "$FAIL"
} | tee -a "$LOG"
