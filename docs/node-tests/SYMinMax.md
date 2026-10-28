# Min Max SY (`SYMinMax`)

Source: `nodes/sy_min_max.py`

**What it does:** Takes two numbers and gives the smaller one and the bigger one.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| a | FLOAT | yes | The first number. | -1000000000000000.0 to 1000000000000000.0, step 0.01, default 0.0 |
| b | FLOAT | yes | The second number. | -1000000000000000.0 to 1000000000000000.0, step 0.01, default 0.0 |

Outputs: `FLOAT`, `FLOAT`

## How it was tested

The harness builds a starting set of inputs from the default of every input (first entry for lists, a small gradient picture for IMAGE and a mask with a filled box for MASK). It runs the node once like that, then changes one input at a time: every entry of every list, the lowest, highest and a middle value of every number, both settings of every on/off switch, and an empty text for every text box. Each run must give the right number of outputs, and pictures and masks must have sane dimensions and no broken (NaN) values. A plain-words refusal to an out-of-range number or empty text counts as REJECTED (expected). Any other error counts as FAIL. The node was run in a temporary folder.

## Cases

| # | Input changed | Result | Output / message |
|---|---|---|---|
| 1 | baseline (all defaults) | PASS | FLOAT=float 0; FLOAT=float 0 |
| 2 | a = -1000000000000000.0 (min) | PASS | FLOAT=float -1e+15; FLOAT=float 0 |
| 3 | a = 1000000000000000.0 (max) | PASS | FLOAT=float 0; FLOAT=float 1e+15 |
| 4 | b = -1000000000000000.0 (min) | PASS | FLOAT=float -1e+15; FLOAT=float 0 |
| 5 | b = 1000000000000000.0 (max) | PASS | FLOAT=float 0; FLOAT=float 1e+15 |

## Verdict

All 5 cases behaved as expected (5 passed, 0 rejected with a clear message).
