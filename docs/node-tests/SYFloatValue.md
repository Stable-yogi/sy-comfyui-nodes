# Float Value SY (`SYFloatValue`)

Source: `nodes/sy_float_value.py`

**What it does:** A decimal number. Type it once and plug it into as many nodes as you like. Also gives the nearest whole number.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| value | FLOAT | yes | The decimal number to send out. | -1000000000000000.0 to 1000000000000000.0, step 0.01, default 0.0 |

Outputs: `FLOAT`, `INT`

## How it was tested

The harness builds a starting set of inputs from the default of every input (first entry for lists, a small gradient picture for IMAGE and a mask with a filled box for MASK). It runs the node once like that, then changes one input at a time: every entry of every list, the lowest, highest and a middle value of every number, both settings of every on/off switch, and an empty text for every text box. Each run must give the right number of outputs, and pictures and masks must have sane dimensions and no broken (NaN) values. A plain-words refusal to an out-of-range number or empty text counts as REJECTED (expected). Any other error counts as FAIL. The node was run in a temporary folder.

## Cases

| # | Input changed | Result | Output / message |
|---|---|---|---|
| 1 | baseline (all defaults) | PASS | FLOAT=float 0; INT=int 0 |
| 2 | value = -1000000000000000.0 (min) | PASS | FLOAT=float -1e+15; INT=int -1000000000000000 |
| 3 | value = 1000000000000000.0 (max) | PASS | FLOAT=float 1e+15; INT=int 1000000000000000 |

## Verdict

All 3 cases behaved as expected (3 passed, 0 rejected with a clear message).
