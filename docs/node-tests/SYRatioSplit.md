# RatioSplit SY (`SYRatioSplit`)

Source: `nodes/sy_ratio_split.py`

**What it does:** Shares a number out by a ratio. For example 100 split 1:3 gives 25 and 75. Up to four parts.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| total | FLOAT | yes | The number to share out. | -1000000000.0 to 1000000000.0, step 0.01, default 100.0 |
| ratios | STRING | yes | Up to four numbers split by colons, like 1:2:1. No negatives. | default '1:2:1' |

Outputs: `FLOAT`, `FLOAT`, `FLOAT`, `FLOAT`, `STRING`

## How it was tested

The harness builds a starting set of inputs from the default of every input (first entry for lists, a small gradient picture for IMAGE and a mask with a filled box for MASK). It runs the node once like that, then changes one input at a time: every entry of every list, the lowest, highest and a middle value of every number, both settings of every on/off switch, and an empty text for every text box. Each run must give the right number of outputs, and pictures and masks must have sane dimensions and no broken (NaN) values. A plain-words refusal to an out-of-range number or empty text counts as REJECTED (expected). Any other error counts as FAIL. The node was run in a temporary folder.

## Cases

| # | Input changed | Result | Output / message |
|---|---|---|---|
| 1 | baseline (all defaults) | PASS | FLOAT=float 25; FLOAT=float 50; FLOAT=float 25; FLOAT=float 0; STRING=str '25, 50, 25' |
| 2 | total = -1000000000.0 (min) | PASS | FLOAT=float -2.5e+08; FLOAT=float -5e+08; FLOAT=float -2.5e+08; FLOAT=float 0; STRING=str '-2.5e+08, -5e+08, -2.5e+08' |
| 3 | total = 1000000000.0 (max) | PASS | FLOAT=float 2.5e+08; FLOAT=float 5e+08; FLOAT=float 2.5e+08; FLOAT=float 0; STRING=str '2.5e+08, 5e+08, 2.5e+08' |
| 4 | total = 0.0 (mid) | PASS | FLOAT=float 0; FLOAT=float 0; FLOAT=float 0; FLOAT=float 0; STRING=str '0, 0, 0' |
| 5 | ratios = '' (empty) | REJECTED | ValueError: ratios must be numbers separated by colons like 1:2:1, got '' |

## Verdict

All 5 cases behaved as expected (4 passed, 1 rejected with a clear message).
