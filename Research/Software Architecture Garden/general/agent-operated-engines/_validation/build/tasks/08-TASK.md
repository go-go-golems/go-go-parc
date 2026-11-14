# Task: jailfs — file access for agent programs that cannot escape

Build `jailfs`, a Python 3 library (standard library only, no network, no pip installs) that an agent runtime uses for
all file access by agent-written programs. Each session gets one writable directory and some read-only directories
(datasets, helper libraries). The datasets are valuable; a single stray write would corrupt them. Agents probe
boundaries while doing ordinary work, and files in the writable directory may be links planted earlier. Apply the
pattern described in `CHAPTER.md`; this is the situation it is for.

Work only inside this directory. Write tests under `tests/` (use temporary directories, never real data) and run them
(`python3 -m unittest discover -s tests`). Keep `DIARY.md` as described in `DIARY-FORMAT.md`.

## Required public interface (other code will be tested against it)

Package `jailfs` (`jailfs/__init__.py` exports these names). All refusals raise `Refused` with attributes `code` (a
string) and `fix` (a string or None).

- `Workspace(root, reads=())`: `root` is the one writable directory; `reads` are read-only directories. Passing
  `root` as a list or tuple of several directories is refused at construction.
- `ws.read(path) -> bytes`: a relative path names a file in the writable root, then in each read directory in order;
  an absolute path must lie inside one of them.
- `ws.save(path, data: bytes)`: writes only inside the writable root (parent directories are created there).
- `ws.load(name) -> str`: the one way to load helper code: returns the text of a `.py` or `.js` file found like `read`.
- `ws.names() -> list`: relative names of files in the writable root.

Codes to use: `E_ACCESS` (outside the roots, through a link, a read-only root, or would replace a file this session
read), `E_NOT_FOUND`, `E_DUPLICATE` (the same path saved twice in one `ws.batch()` block), `E_SHADOW` (a save whose
relative name already exists in a read directory). `ws.batch()` is a context manager marking one agent program's run.

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
