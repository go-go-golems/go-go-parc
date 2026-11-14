# Next change (hubreg)

A third-party plug-in adds `light.set_color` with one required argument `color` of a new argument type `rgb`: a string
`#rrggbb` (hex digits, either case); `"red"` or `"#ff00"` must be refused with `E_ARG_TYPE`. Tool schemas and controls
must describe the argument with type `rgb`. A fourth consumer, `reg.voice_phrases()`, returns example phrases per
action generated from the records alone.
