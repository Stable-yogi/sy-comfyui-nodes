# Number Compare SY (`SYNumberCompare`)

Source: `nodes/sy_number_compare.py`

**What it does:** Compares number a with number b and gives yes or no. Use it to drive a switch.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| a | FLOAT | yes | The number on the left. | -1000000000000000.0 to 1000000000000000.0, step 0.01, default 0.0 |
| operator | COMBO | yes | How to compare: equal, not equal, smaller, bigger and so on. | one of: ==, !=, <, <=, >, >= |
| b | FLOAT | yes | The number on the right. | -1000000000000000.0 to 1000000000000000.0, step 0.01, default 0.0 |

Outputs: `BOOLEAN`

## How it was tested

The harness builds a starting set of inputs from the default of every input (first entry for lists, a small gradient picture for IMAGE and a mask with a filled box for MASK). It runs the node once like that, then changes one input at a time: every entry of every list, the lowest, highest and a middle value of every number, both settings of every on/off switch, and an empty text for every text box. Each run must give the right number of outputs, and pictures and masks must have sane dimensions and no broken (NaN) values. A plain-words refusal to an out-of-range number or empty text counts as REJECTED (expected). Any other error counts as FAIL. The node was run in a temporary folder.

## Cases

| # | Input changed | Result | Output / message |
|---|---|---|---|
| 1 | baseline (all defaults) | PASS | BOOLEAN=bool True |
| 2 | a = -1000000000000000.0 (min) | PASS | BOOLEAN=bool False |
| 3 | a = 1000000000000000.0 (max) | PASS | BOOLEAN=bool False |
| 4 | operator = '!=' | PASS | BOOLEAN=bool False |
| 5 | operator = '<' | PASS | BOOLEAN=bool False |
| 6 | operator = '<=' | PASS | BOOLEAN=bool True |
| 7 | operator = '>' | PASS | BOOLEAN=bool False |
| 8 | operator = '>=' | PASS | BOOLEAN=bool True |
| 9 | b = -1000000000000000.0 (min) | PASS | BOOLEAN=bool False |
| 10 | b = 1000000000000000.0 (max) | PASS | BOOLEAN=bool False |

## Verdict

All 10 cases behaved as expected (10 passed, 0 rejected with a clear message).
