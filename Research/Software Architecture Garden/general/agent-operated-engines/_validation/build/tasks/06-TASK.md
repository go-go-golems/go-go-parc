# Task: shopcli — an inventory command language whose errors repair themselves

Build `shopcli`, a Python 3 library (standard library only, no network, no pip installs). Agents manage a shop's
inventory by sending short scripts, one command per line. Each failed attempt costs the agent a round trip, so every
error must carry what the agent needs to fix its script without reading documentation. Apply the pattern described in
`CHAPTER.md`; this is the situation it is for.

Work only inside this directory. Write tests under `tests/` and run them (`python3 -m unittest discover -s tests`).
Keep `DIARY.md` as described in `DIARY-FORMAT.md`.

## The language

One command per line: `namespace.verb key=value key=value ...`. Values are numbers if they parse as numbers, otherwise
strings. A line `repeat N: <command>` runs the command N times. Blank lines are ignored. Commands:

| Command | Arguments | Result |
| --- | --- | --- |
| `item.add` | `name` (string), `qty` (integer ≥ 0; usual range 0–1000) | `{"name", "qty"}` (qty added to stock) |
| `item.remove` | `name`, `qty` (optional, default: all) | `{"name", "qty"}` remaining |
| `item.list` | none | list of `{"name", "qty"}` |
| `price.set` | `name`, `value` (number ≥ 0) | `{"name", "value"}` |
| `price.get` | `name` | `{"name", "value"}` |
| `report.stock` | none | `{"items", "units"}` |
| `report.margin` | `name`, `cost` (number) | `{"name", "margin"}` where margin = (value − cost) / value |

Agents demonstrably type these wrong names; treat them as known near-misses: `rm` and `delete` mean `item.remove`,
`ls` means `item.list`, `inventory` means `report.stock`.

## Required public interface (other code will be tested against it)

- `Shop()` holds the store; `shop.run(script: str) -> dict` runs a script and returns a reply:
  `{"ok": bool, "results": [one entry per command that ran], "warnings": [...], "error": {...} or None}`.
- Execution stops at the first error; results of earlier commands are still returned.
- `error` has: `code` (one of `shopcli.CODES`), `message`, `path` (a list; its last element starts with `✗`),
  `where` (`{"line": int, "source": str}`), `valid` (a list), `hint` (str or None), `fix` (str or None), and
  `host_name` (str or None).
- `shopcli.CODES` lists every code you use. Use at least: `E_UNKNOWN_COMMAND`, `E_NAMESPACE`, `E_UNKNOWN_OPTION`,
  `E_ARG_TYPE`, `E_ARG_RANGE`, `E_ARG_MISSING`, `E_NOT_FOUND`, `E_HOST` (an unexpected Python exception inside a
  command), `E_SYNTAX`.
- A warning has: `code` (`RANGE` for a value outside a usual range), `message`, `line`, `count`, `hint`.

When you are done, give a final message containing exactly one JSON object in a ```json fenced block:

```json
{
  "summary": "what you built, in three sentences",
  "files": ["paths you created"],
  "pattern_mapping": {"<participant from CHAPTER.md>": "where it is in your code"},
  "notes_applied": ["implementation notes from CHAPTER.md you applied, and how"],
  "tests": "how many tests you wrote, and the last result",
  "chapter_feedback": ["where the chapter helped, misled you or left you to guess"]
}
```
