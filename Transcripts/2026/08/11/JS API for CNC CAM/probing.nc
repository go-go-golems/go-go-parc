%
(CAM-IR 0.1 - Two-pass Z probe)
G90 G21 G94 G17 G40 G49
G53 G0 Z-5.000
G54
T99 M6 (touch probe)
G0 Z5.000
G0 X0.000 Y0.000
G38.2 Z-20.000 F200.000
(capture stock.top.fast: read probe result from controller status/report)
G0 Z3.000
G38.2 Z-5.000 F40.000
(capture stock.top.slow: read probe result from controller status/report)
G0 Z5.000
G53 G0 Z-5.000
M30
%
