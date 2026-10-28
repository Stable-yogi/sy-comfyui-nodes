# Size Snap SY (`SYSizeSnap`)

Source: `nodes/sy_size_snap.py`

**What it does:** Snaps a width and height to a multiple, like 8 or 64, so a model accepts them. Pick nearest, round up or round down.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| width | INT | yes | Width in pixels to snap. | 1 to 65536, default 1000 |
| height | INT | yes | Height in pixels to snap. | 1 to 65536, default 1000 |
| multiple | INT | yes | Snap to a multiple of this number. | 1 to 1024, default 8 |
| mode | COMBO | yes | Nearest rounds either way. Up never shrinks. Down never grows. | one of: nearest, up, down |

Outputs: `INT`, `INT`

## How it was tested

The harness builds a starting set of inputs from the default of every input (first entry for lists, a small gradient picture for IMAGE and a mask with a filled box for MASK). It runs the node once like that, then changes one input at a time: every entry of every list, the lowest, highest and a middle value of every number, both settings of every on/off switch, and an empty text for every text box. Each run must give the right number of outputs, and pictures and masks must have sane dimensions and no broken (NaN) values. A plain-words refusal to an out-of-range number or empty text counts as REJECTED (expected). Any other error counts as FAIL. The node was run in a temporary folder.

## Cases

| # | Input changed | Result | Output / message |
|---|---|---|---|
| 1 | baseline (all defaults) | PASS | INT=int 1000; INT=int 1000 |
| 2 | width = 1 (min) | PASS | INT=int 8; INT=int 1000 |
| 3 | width = 65536 (max) | PASS | INT=int 65536; INT=int 1000 |
| 4 | width = 32768 (mid) | PASS | INT=int 32768; INT=int 1000 |
| 5 | height = 1 (min) | PASS | INT=int 1000; INT=int 8 |
| 6 | height = 65536 (max) | PASS | INT=int 1000; INT=int 65536 |
| 7 | height = 32768 (mid) | PASS | INT=int 1000; INT=int 32768 |
| 8 | multiple = 1 (min) | PASS | INT=int 1000; INT=int 1000 |
| 9 | multiple = 1024 (max) | PASS | INT=int 1024; INT=int 1024 |
| 10 | multiple = 512 (mid) | PASS | INT=int 1024; INT=int 1024 |
| 11 | mode = 'up' | PASS | INT=int 1000; INT=int 1000 |
| 12 | mode = 'down' | PASS | INT=int 1000; INT=int 1000 |

## Verdict

All 12 cases behaved as expected (12 passed, 0 rejected with a clear message).
