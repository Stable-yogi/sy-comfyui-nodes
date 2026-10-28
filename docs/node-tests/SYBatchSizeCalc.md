# Batch Size Calc SY (`SYBatchSizeCalc`)

Source: `nodes/sy_batch_size_calc.py`

**What it does:** Splits a total number of pictures into runs of at most a set size. Gives the number of runs, the size of the last run and what is left over.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| total | INT | yes | How many pictures you want in all. | 0 to 10000000, default 10 |
| max_per_pass | INT | yes | The most pictures one run can hold, such as what fits in memory. | 1 to 100000, default 4 |

Outputs: `INT`, `INT`, `INT`

## How it was tested

The harness builds a starting set of inputs from the default of every input (first entry for lists, a small gradient picture for IMAGE and a mask with a filled box for MASK). It runs the node once like that, then changes one input at a time: every entry of every list, the lowest, highest and a middle value of every number, both settings of every on/off switch, and an empty text for every text box. Each run must give the right number of outputs, and pictures and masks must have sane dimensions and no broken (NaN) values. A plain-words refusal to an out-of-range number or empty text counts as REJECTED (expected). Any other error counts as FAIL. The node was run in a temporary folder.

## Cases

| # | Input changed | Result | Output / message |
|---|---|---|---|
| 1 | baseline (all defaults) | PASS | INT=int 3; INT=int 2; INT=int 2 |
| 2 | total = 0 (min) | PASS | INT=int 0; INT=int 0; INT=int 0 |
| 3 | total = 10000000 (max) | PASS | INT=int 2500000; INT=int 4; INT=int 0 |
| 4 | total = 5000000 (mid) | PASS | INT=int 1250000; INT=int 4; INT=int 0 |
| 5 | max_per_pass = 1 (min) | PASS | INT=int 10; INT=int 1; INT=int 0 |
| 6 | max_per_pass = 100000 (max) | PASS | INT=int 1; INT=int 10; INT=int 10 |
| 7 | max_per_pass = 50000 (mid) | PASS | INT=int 1; INT=int 10; INT=int 10 |

## Verdict

All 7 cases behaved as expected (7 passed, 0 rejected with a clear message).
