# Seed SY (`SYSeed`)

Source: `nodes/sy_seed.py`

**What it does:** Gives one seed number. Fixed keeps it. Random picks a new one each run. Increment adds 1 each run.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| seed | INT | yes | The seed number. Same number gives the same picture. | 0 to 18446744073709551615, default 0 |
| mode | COMBO | yes | Fixed keeps the number. Random picks a new one each run. Increment adds 1 each run. | one of: fixed, random, increment |

Outputs: `INT`

## How it was tested

The harness builds a starting set of inputs from the default of every input (first entry for lists, a small gradient picture for IMAGE and a mask with a filled box for MASK). It runs the node once like that, then changes one input at a time: every entry of every list, the lowest, highest and a middle value of every number, both settings of every on/off switch, and an empty text for every text box. Each run must give the right number of outputs, and pictures and masks must have sane dimensions and no broken (NaN) values. A plain-words refusal to an out-of-range number or empty text counts as REJECTED (expected). Any other error counts as FAIL. The node was run in a temporary folder.

## Cases

| # | Input changed | Result | Output / message |
|---|---|---|---|
| 1 | baseline (all defaults) | PASS | INT=int 0 |
| 2 | seed = 18446744073709551615 (max) | PASS | INT=int 18446744073709551615 |
| 3 | seed = 9223372036854775807 (mid) | PASS | INT=int 9223372036854775807 |
| 4 | mode = 'random' | PASS | INT=int 8460841884322990393 |
| 5 | mode = 'increment' | PASS | INT=int 8460841884322990394 |

## Verdict

All 5 cases behaved as expected (5 passed, 0 rejected with a clear message).
