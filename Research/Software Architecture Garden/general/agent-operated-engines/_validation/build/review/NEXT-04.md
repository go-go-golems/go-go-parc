# Next change (stencilpipe)

Add `dy()` (a vertical difference that reads only along y, the mirror of `dx()`) and `up2()` (a 2x nearest-neighbour
upsample: the output is twice the input's size and `out[y][x] = in[y//2][x//2]`). Windows of both must still compute
only what they need.
