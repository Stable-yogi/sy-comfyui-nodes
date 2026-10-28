# Round To Multiple SY (`SYRoundToMultiple`)

Source: `nodes/sy_round_to_multiple.py`

**What it does:** Rounds a number to a multiple of a step, like 64 for image sizes. Choose nearest, round up or round down.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| value | FLOAT | yes | The number to round. | -1000000000000000.0 to 1000000000000000.0, step 0.01, default 100.0 |
| multiple | FLOAT | yes | Round to a whole number of these steps. Must be above 0. | 1e-06 to 1000000000000000.0, step 0.01, default 64.0 |
| mode | COMBO | yes | nearest goes to the closest step. up goes higher. down goes lower. | one of: nearest, up, down |

Outputs: `FLOAT`, `INT`

## How it was tested

The harness builds a starting set of inputs from the default of every input (first entry for lists, a small gradient picture for IMAGE and a mask with a filled box for MASK). It runs the node once like that, then changes one input at a time: every entry of every list, the lowest, highest and a middle value of every number, both settings of every on/off switch, and an empty text for every text box. Each run must give the right number of outputs, and pictures and masks must have sane dimensions and no broken (NaN) values. A plain-words refusal to an out-of-range number or empty text counts as REJECTED (expected). Any other error counts as FAIL. The node was run in a temporary folder.

## Cases

| # | Input changed | Result | Output / message |
|---|---|---|---|
| 1 | baseline (all defaults) | PASS | FLOAT=float 128; INT=int 128 |
| 2 | value = -1000000000000000.0 (min) | PASS | FLOAT=float -1e+15; INT=int -1000000000000000 |
| 3 | value = 1000000000000000.0 (max) | PASS | FLOAT=float 1e+15; INT=int 1000000000000000 |
| 4 | value = 0.0 (mid) | PASS | FLOAT=float 0; INT=int 0 |
| 5 | multiple = 1e-06 (min) | PASS | FLOAT=float 100; INT=int 100 |
| 6 | multiple = 1000000000000000.0 (max) | PASS | FLOAT=float 0; INT=int 0 |
| 7 | multiple = 500000000000000.0 (mid) | PASS | FLOAT=float 0; INT=int 0 |
| 8 | mode = 'up' | PASS | FLOAT=float 128; INT=int 128 |
| 9 | mode = 'down' | PASS | FLOAT=float 64; INT=int 64 |

## Verdict

All 9 cases behaved as expected (9 passed, 0 rejected with a clear message).
