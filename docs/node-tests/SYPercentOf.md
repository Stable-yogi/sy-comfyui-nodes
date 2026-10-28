# PercentOf SY (`SYPercentOf`)

Source: `nodes/sy_percent_of.py`

**What it does:** Does percentage sums. Find a percent of a number, find what percent one number is of another, or raise or lower a number by a percent.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| mode | COMBO | yes | percent_of: a% of b. what_percent: a is what % of b. change_by_percent: a changed by b%. | one of: percent_of, what_percent, change_by_percent |
| a | FLOAT | yes | The first number. See the mode for how it is used. | -1000000000.0 to 1000000000.0, step 0.01, default 10.0 |
| b | FLOAT | yes | The second number. See the mode for how it is used. | -1000000000.0 to 1000000000.0, step 0.01, default 200.0 |

Outputs: `FLOAT`, `STRING`

## How it was tested

The harness builds a starting set of inputs from the default of every input (first entry for lists, a small gradient picture for IMAGE and a mask with a filled box for MASK). It runs the node once like that, then changes one input at a time: every entry of every list, the lowest, highest and a middle value of every number, both settings of every on/off switch, and an empty text for every text box. Each run must give the right number of outputs, and pictures and masks must have sane dimensions and no broken (NaN) values. A plain-words refusal to an out-of-range number or empty text counts as REJECTED (expected). Any other error counts as FAIL. The node was run in a temporary folder.

## Cases

| # | Input changed | Result | Output / message |
|---|---|---|---|
| 1 | baseline (all defaults) | PASS | FLOAT=float 20; STRING=str '10.0% of 200.0 = 20.0' |
| 2 | mode = 'what_percent' | PASS | FLOAT=float 5; STRING=str '10.0 is 5.0% of 200.0' |
| 3 | mode = 'change_by_percent' | PASS | FLOAT=float 30; STRING=str '10.0 changed by 200.0% = 30.0' |
| 4 | a = -1000000000.0 (min) | PASS | FLOAT=float -2e+09; STRING=str '-1000000000.0% of 200.0 = -2000000000.0' |
| 5 | a = 1000000000.0 (max) | PASS | FLOAT=float 2e+09; STRING=str '1000000000.0% of 200.0 = 2000000000.0' |
| 6 | a = 0.0 (mid) | PASS | FLOAT=float 0; STRING=str '0.0% of 200.0 = 0.0' |
| 7 | b = -1000000000.0 (min) | PASS | FLOAT=float -1e+08; STRING=str '10.0% of -1000000000.0 = -100000000.0' |
| 8 | b = 1000000000.0 (max) | PASS | FLOAT=float 1e+08; STRING=str '10.0% of 1000000000.0 = 100000000.0' |
| 9 | b = 0.0 (mid) | PASS | FLOAT=float 0; STRING=str '10.0% of 0.0 = 0.0' |

## Verdict

All 9 cases behaved as expected (9 passed, 0 rejected with a clear message).
