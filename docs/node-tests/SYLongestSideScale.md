# Longest Side Scale SY (`SYLongestSideScale`)

Source: `nodes/sy_longest_side_scale.py`

**What it does:** Works out a new width and height so the longer side equals the number you give. The shape (aspect) stays the same. Both sides are rounded to a multiple.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| width | INT | yes | Current width in pixels. | 1 to 65536, default 1024 |
| height | INT | yes | Current height in pixels. | 1 to 65536, default 768 |
| longest_side | INT | yes | Size in pixels you want for the longer side. | 1 to 65536, default 1024 |
| multiple | INT | yes | Both sides are rounded to a multiple of this. Use 1 for exact. | 1 to 256, default 8 |

Outputs: `INT`, `INT`

## How it was tested

The harness builds a starting set of inputs from the default of every input (first entry for lists, a small gradient picture for IMAGE and a mask with a filled box for MASK). It runs the node once like that, then changes one input at a time: every entry of every list, the lowest, highest and a middle value of every number, both settings of every on/off switch, and an empty text for every text box. Each run must give the right number of outputs, and pictures and masks must have sane dimensions and no broken (NaN) values. A plain-words refusal to an out-of-range number or empty text counts as REJECTED (expected). Any other error counts as FAIL. The node was run in a temporary folder.

## Cases

| # | Input changed | Result | Output / message |
|---|---|---|---|
| 1 | baseline (all defaults) | PASS | INT=int 1024; INT=int 768 |
| 2 | width = 1 (min) | PASS | INT=int 8; INT=int 1024 |
| 3 | width = 65536 (max) | PASS | INT=int 1024; INT=int 16 |
| 4 | width = 32768 (mid) | PASS | INT=int 1024; INT=int 24 |
| 5 | height = 1 (min) | PASS | INT=int 1024; INT=int 8 |
| 6 | height = 65536 (max) | PASS | INT=int 16; INT=int 1024 |
| 7 | height = 32768 (mid) | PASS | INT=int 32; INT=int 1024 |
| 8 | longest_side = 1 (min) | PASS | INT=int 8; INT=int 8 |
| 9 | longest_side = 65536 (max) | PASS | INT=int 65536; INT=int 49152 |
| 10 | longest_side = 32768 (mid) | PASS | INT=int 32768; INT=int 24576 |
| 11 | multiple = 1 (min) | PASS | INT=int 1024; INT=int 768 |
| 12 | multiple = 256 (max) | PASS | INT=int 1024; INT=int 768 |
| 13 | multiple = 128 (mid) | PASS | INT=int 1024; INT=int 768 |

## Verdict

All 13 cases behaved as expected (13 passed, 0 rejected with a clear message).
