New requirements arrived for hubreg. Implement them in the same directory, keep all existing tests passing, and add
tests for the new behaviour.

1. A third-party plug-in adds `light.set_color` with one required argument `color` of a new argument type `rgb`: a
   string of the form `#rrggbb` (hex digits, either case). `"red"` or `"#ff00"` must be refused with `E_ARG_TYPE`.
   Tool schemas and controls must describe the argument with type `rgb`. Add the type and the plug-in WITHOUT editing
   the binder or the registry core: the point of the design is that a new type and a new action are local additions.
   Register it in `demo_registry()`. If you find you cannot avoid editing the core, do the smallest change that makes
   types pluggable, and say so.
2. A fourth consumer: `reg.voice_phrases()` returns a dict mapping each action's full name (`"kind.action"`) to a
   non-empty list of example phrases a voice assistant can say, generated from the records alone (names, argument
   docs, units, defaults); no per-action phrase lists written by hand.
3. Rename the thermostat argument `target` to `temperature`. Old callers still send `target=21`; such a call must be
   refused with `E_UNKNOWN_OPTION` and a `fix` naming `temperature`. `temperature=21` must bind.

When you are done, give a final message containing exactly one JSON object in a ```json fenced block:

```json
{
  "changed_files": {"path": "why it changed"},
  "core_untouched": true,
  "new_tests": "how many, and the last result",
  "design_notes": ["what in your design made each requirement easy or hard"],
  "chapter_feedback": ["where CHAPTER.md helped or failed you on these changes"]
}
```
