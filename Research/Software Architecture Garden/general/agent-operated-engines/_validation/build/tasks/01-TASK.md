# Task: hubreg — the action registry of a home-automation hub

Build `hubreg`, a Python 3 library and command-line tool (standard library only, no network, no pip installs) for a
home-automation hub. Device plug-ins register actions. Three consumers use the same actions: a language-model
assistant (needs a JSON tool description per action), a mobile app (needs one control description per argument),
and the hub itself (must validate every command from both before running it). Apply the pattern described in
`CHAPTER.md`; this is exactly the situation it is for.

Work only inside this directory. Write tests under `tests/` and run them (`python3 -m unittest discover -s tests`).

## Required public interface (other code will be tested against it)

Package `hubreg` (`hubreg/__init__.py` must export these names):

- `Registry(confirm_required=())` — `confirm_required` is the host's set of action names that need confirmation.
- `reg.register(record: dict) -> None`; raises `RecordError` (attribute `.code`, a string) when a record is
  malformed or inconsistent.
- A record is a dict:
  `{"name": str, "on": str (device kind), "doc": str, "args": [ArgSpec], "fields": [str] (keys of the result),
    "samples": [dict] (argument dicts for testing), "run": callable(args: dict) -> dict,
    "flags": {"confirm": bool} (optional), "redirects": {wrong_action_name: right_action_name} (optional)}`
  where an ArgSpec is
  `{"name": str, "type": "number" | "string" | "enum" | "bool", "unit": str or None, "doc": str,
    "default": any (optional), "optional": bool (optional), "min": number (optional), "max": number (optional),
    "usual": [low, high] (optional), "usual_hint": str (optional), "values": [str] (enum only),
    "redirects": {wrong_option_name: right_option_name} (optional)}`.
- `reg.bind(on: str, name: str, args: dict) -> Call` where `Call` has `.record_name`, `.on`, `.args` (a dict with
  defaults filled) and `.warnings` (a list of objects with `.code` and `.message`; a value outside an argument's usual range gives code `RANGE`). On failure it raises `Refusal`
  with attributes `.code`, `.message`, `.valid` (list, may be empty), `.nearest` (str or None) and `.fix` (str or
  None). Use these codes: `E_UNKNOWN_ACTION`, `E_UNKNOWN_OPTION`, `E_ARG_TYPE`, `E_ARG_RANGE`, `E_ARG_MISSING`.
- `reg.run(call, confirmed=False) -> dict`; raises `Refusal` with code `E_CONFIRM` when the action needs
  confirmation and `confirmed` is false.
- `reg.tool_schemas() -> list` of JSON-serialisable tool descriptions (name, description, input schema with types,
  units and ranges) for the assistant.
- `reg.controls(on, name) -> list` of dicts, one per argument, for the app (name, type, unit, min, max, default,
  values).
- `reg.help(on, name) -> str`.
- `reg.walk() -> list` of problems (dicts with at least `"action"` and `"problem"` keys) found by exercising every
  registered action; an empty list means no problems.
- Command line: `python3 -m hubreg describe` prints the tool descriptions of the demo plug-ins as JSON;
  `python3 -m hubreg call <kind> <action> key=value ...` binds and runs one call and prints the result or the refusal.

## Demo plug-ins to include (registered by `hubreg.demo_registry()`)

- `thermostat.set_temperature`: `target` in °C, hard limits 5–35, usual 16–24; result fields `target`, `mode`.
- `light.dim`: `level` in percent, 0–100, default 50; result field `level`.
- `door.lock_door`: no arguments; a security action the host requires confirmation for; result field `locked`.
- `scene.run_scene`: `scene`, one of `morning`, `evening`, `away`; result field `scene`.

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
