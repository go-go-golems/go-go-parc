# Next change (jailfs)

Add `ws.remove(path)`: deletes a file in the writable root, under every existing guarantee (never through a link, never
in a read-only directory, never outside the roots), with a new code `E_IN_USE` when the file was read earlier in the
same `ws.batch()` block.
