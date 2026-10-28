# Clamp Remap SY (`SYClampRemap`)

Source: `nodes/sy_clamp_remap.py`

**What it does:** Keeps a number inside a range, and moves it from one range to another. Example: 0 to 1 becomes 0 to 255.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| value | FLOAT | yes | The number to change. | -1000000000000000.0 to 1000000000000000.0, step 0.01, default 0.5 |
| in_min | FLOAT | yes | Start of the range the number comes from. | -1000000000000000.0 to 1000000000000000.0, step 0.01, default 0.0 |
| in_max | FLOAT | yes | End of the range the number comes from. Must differ from in_min. | -1000000000000000.0 to 1000000000000000.0, step 0.01, default 1.0 |
| out_min | FLOAT | yes | Start of the range the number goes to. | -1000000000000000.0 to 1000000000000000.0, step 0.01, default 0.0 |
| out_max | FLOAT | yes | End of the range the number goes to. | -1000000000000000.0 to 1000000000000000.0, step 0.01, default 100.0 |
| clamp | BOOLEAN | yes | On keeps the result inside the output range. Off lets it run past. | default True |

Outputs: `FLOAT`, `FLOAT`

## How it was tested

The harness builds a starting set of inputs from the default of every input (first entry for lists, a small gradient picture for IMAGE and a mask with a filled box for MASK). It runs the node once like that, then changes one input at a time: every entry of every list, the lowest, highest and a middle value of every number, both settings of every on/off switch, and an empty text for every text box. Each run must give the right number of outputs, and pictures and masks must have sane dimensions and no broken (NaN) values. A plain-words refusal to an out-of-range number or empty text counts as REJECTED (expected). Any other error counts as FAIL. The node was run in a temporary folder.

## Cases

| # | Input changed | Result | Output / message |
|---|---|---|---|
| 1 | baseline (all defaults) | PASS | FLOAT=float 50; FLOAT=float 0.5 |
| 2 | value = -1000000000000000.0 (min) | PASS | FLOAT=float 0; FLOAT=float 0 |
| 3 | value = 1000000000000000.0 (max) | PASS | FLOAT=float 100; FLOAT=float 1 |
| 4 | value = 0.0 (mid) | PASS | FLOAT=float 0; FLOAT=float 0 |
| 5 | in_min = -1000000000000000.0 (min) | PASS | FLOAT=float 100; FLOAT=float 0.5 |
| 6 | in_min = 1000000000000000.0 (max) | PASS | FLOAT=float 100; FLOAT=float 1 |
| 7 | in_max = -1000000000000000.0 (min) | PASS | FLOAT=float 0; FLOAT=float 0 |
| 8 | in_max = 1000000000000000.0 (max) | PASS | FLOAT=float 5e-14; FLOAT=float 0.5 |
| 9 | in_max = 0.0 (mid) | REJECTED | ValueError: in_min and in_max are both 0. Make them different so the range has a size. |
| 10 | out_min = -1000000000000000.0 (min) | PASS | FLOAT=float -5e+14; FLOAT=float 0.5 |
| 11 | out_min = 1000000000000000.0 (max) | PASS | FLOAT=float 5e+14; FLOAT=float 0.5 |
| 12 | out_max = -1000000000000000.0 (min) | PASS | FLOAT=float -5e+14; FLOAT=float 0.5 |
| 13 | out_max = 1000000000000000.0 (max) | PASS | FLOAT=float 5e+14; FLOAT=float 0.5 |
| 14 | out_max = 0.0 (mid) | PASS | FLOAT=float 0; FLOAT=float 0.5 |
| 15 | clamp = False | PASS | FLOAT=float 50; FLOAT=float 0.5 |

## Verdict

All 15 cases behaved as expected (14 passed, 1 rejected with a clear message).
