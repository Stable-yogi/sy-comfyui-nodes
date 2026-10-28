# Int Value SY (`SYIntValue`)

Source: `nodes/sy_int_value.py`

**What it does:** A whole number. Type it once and plug it into as many nodes as you like. Also gives the same number as a decimal.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| value | INT | yes | The whole number to send out. | -9007199254740991 to 9007199254740991, default 0 |

Outputs: `INT`, `FLOAT`

## How it was tested

The harness builds a starting set of inputs from the default of every input (first entry for lists, a small gradient picture for IMAGE and a mask with a filled box for MASK). It runs the node once like that, then changes one input at a time: every entry of every list, the lowest, highest and a middle value of every number, both settings of every on/off switch, and an empty text for every text box. Each run must give the right number of outputs, and pictures and masks must have sane dimensions and no broken (NaN) values. A plain-words refusal to an out-of-range number or empty text counts as REJECTED (expected). Any other error counts as FAIL. The node was run in a temporary folder.

## Cases

| # | Input changed | Result | Output / message |
|---|---|---|---|
| 1 | baseline (all defaults) | PASS | INT=int 0; FLOAT=float 0 |
| 2 | value = -9007199254740991 (min) | PASS | INT=int -9007199254740991; FLOAT=float -9.0072e+15 |
| 3 | value = 9007199254740991 (max) | PASS | INT=int 9007199254740991; FLOAT=float 9.0072e+15 |

## Verdict

All 3 cases behaved as expected (3 passed, 0 rejected with a clear message).
