# XY Values List SY (`SYXYValuesList`)

Source: `nodes/sy_xy_values_list.py`

**What it does:** Builds the list of values for one side of an XY plot: a number range, a typed list, or a run of seeds.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| mode | COMBO | yes | numbers = a range, text list = values you type, seeds = a run of seed numbers. | one of: numbers, text list, seeds |
| start | FLOAT | yes | First number of the range (numbers mode). | -1000000.0 to 1000000.0, step 0.01, default 1.0 |
| stop | FLOAT | yes | Last number of the range (numbers mode). | -1000000.0 to 1000000.0, step 0.01, default 8.0 |
| steps | INT | yes | How many numbers in the range, including first and last. | 1 to 64, default 4 |
| text | STRING | yes | Values separated by commas or new lines (text list mode). | default 'euler, dpmpp_2m, ddim', multiline |
| seed_first | INT | yes | First seed (seeds mode). | 0 to 9223372036854775807, default 0 |
| seed_count | INT | yes | How many seeds to make (seeds mode). | 1 to 64, default 4 |
| seed_step | INT | yes | Added to each seed to get the next one (seeds mode). | -1000000 to 1000000, default 1 |

Outputs: `STRING`, `INT`

## How it was tested

The harness builds a starting set of inputs from the default of every input (first entry for lists, a small gradient picture for IMAGE and a mask with a filled box for MASK). It runs the node once like that, then changes one input at a time: every entry of every list, the lowest, highest and a middle value of every number, both settings of every on/off switch, and an empty text for every text box. Each run must give the right number of outputs, and pictures and masks must have sane dimensions and no broken (NaN) values. A plain-words refusal to an out-of-range number or empty text counts as REJECTED (expected). Any other error counts as FAIL. The node was run in a temporary folder.

## Cases

| # | Input changed | Result | Output / message |
|---|---|---|---|
| 1 | baseline (all defaults) | PASS | STRING=str '1 3.333333 5.666667 8'; INT=int 4 |
| 2 | mode = 'text list' | PASS | STRING=str 'euler dpmpp_2m ddim'; INT=int 3 |
| 3 | mode = 'seeds' | PASS | STRING=str '0 1 2 3'; INT=int 4 |
| 4 | start = -1000000.0 (min) | PASS | STRING=str '-1000000 -666664 -333328 8'; INT=int 4 |
| 5 | start = 1000000.0 (max) | PASS | STRING=str '1000000 666669.333333 333338.666667 8'; INT=int 4 |
| 6 | start = 0.0 (mid) | PASS | STRING=str '0 2.666667 5.333333 8'; INT=int 4 |
| 7 | stop = -1000000.0 (min) | PASS | STRING=str '1 -333332.666667 -666666.333333 -1000000'; INT=int 4 |
| 8 | stop = 1000000.0 (max) | PASS | STRING=str '1 333334 666667 1000000'; INT=int 4 |
| 9 | stop = 0.0 (mid) | PASS | STRING=str '1 0.666667 0.333333 0'; INT=int 4 |
| 10 | steps = 1 (min) | PASS | STRING=str '1'; INT=int 1 |
| 11 | steps = 64 (max) | PASS | STRING=str '1 1.111111 1.222222 1.333333 1.444444 1.555556 1.666667 1.777778 1.888889 2 2...'; INT=int 64 |
| 12 | steps = 32 (mid) | PASS | STRING=str '1 1.225806 1.451613 1.677419 1.903226 2.129032 2.354839 2.580645 2.806452 3.0...'; INT=int 32 |
| 13 | text = '' (empty) | PASS | STRING=str '1 3.333333 5.666667 8'; INT=int 4 |
| 14 | seed_first = 9223372036854775807 (max) | PASS | STRING=str '1 3.333333 5.666667 8'; INT=int 4 |
| 15 | seed_first = 4611686018427387903 (mid) | PASS | STRING=str '1 3.333333 5.666667 8'; INT=int 4 |
| 16 | seed_count = 1 (min) | PASS | STRING=str '1 3.333333 5.666667 8'; INT=int 4 |
| 17 | seed_count = 64 (max) | PASS | STRING=str '1 3.333333 5.666667 8'; INT=int 4 |
| 18 | seed_count = 32 (mid) | PASS | STRING=str '1 3.333333 5.666667 8'; INT=int 4 |
| 19 | seed_step = -1000000 (min) | PASS | STRING=str '1 3.333333 5.666667 8'; INT=int 4 |
| 20 | seed_step = 1000000 (max) | PASS | STRING=str '1 3.333333 5.666667 8'; INT=int 4 |
| 21 | seed_step = 0 (mid) | PASS | STRING=str '1 3.333333 5.666667 8'; INT=int 4 |

## Verdict

All 21 cases behaved as expected (21 passed, 0 rejected with a clear message).
