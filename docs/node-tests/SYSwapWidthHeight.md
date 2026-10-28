# Swap Width Height SY (`SYSwapWidthHeight`)

Source: `nodes/sy_swap_width_height.py`

**What it does:** Swaps width and height when the switch is on. Turns a landscape size into portrait and back.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| width | INT | yes | Width in pixels. | 0 to 65536, default 1024 |
| height | INT | yes | Height in pixels. | 0 to 65536, default 768 |
| swap | BOOLEAN | yes | On swaps the two sizes. Off passes them through unchanged. | default True |

Outputs: `INT`, `INT`

## How it was tested

The harness builds a starting set of inputs from the default of every input (first entry for lists, a small gradient picture for IMAGE and a mask with a filled box for MASK). It runs the node once like that, then changes one input at a time: every entry of every list, the lowest, highest and a middle value of every number, both settings of every on/off switch, and an empty text for every text box. Each run must give the right number of outputs, and pictures and masks must have sane dimensions and no broken (NaN) values. A plain-words refusal to an out-of-range number or empty text counts as REJECTED (expected). Any other error counts as FAIL. The node was run in a temporary folder.

## Cases

| # | Input changed | Result | Output / message |
|---|---|---|---|
| 1 | baseline (all defaults) | PASS | INT=int 768; INT=int 1024 |
| 2 | width = 0 (min) | PASS | INT=int 768; INT=int 0 |
| 3 | width = 65536 (max) | PASS | INT=int 768; INT=int 65536 |
| 4 | width = 32768 (mid) | PASS | INT=int 768; INT=int 32768 |
| 5 | height = 0 (min) | PASS | INT=int 0; INT=int 1024 |
| 6 | height = 65536 (max) | PASS | INT=int 65536; INT=int 1024 |
| 7 | height = 32768 (mid) | PASS | INT=int 32768; INT=int 1024 |
| 8 | swap = False | PASS | INT=int 1024; INT=int 768 |

## Verdict

All 8 cases behaved as expected (8 passed, 0 rejected with a clear message).
