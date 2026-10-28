# Random In Range SY (`SYRandomInRange`)

Source: `nodes/sy_random_in_range.py`

**What it does:** Makes a random whole number and a random decimal between two limits. The same seed always gives the same answer.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| seed | INT | yes | Same seed, same numbers. Change it for new numbers. | 0 to 18446744073709551615, default 0 |
| min_value | FLOAT | yes | Lowest number that can come out. | -1000000000000000.0 to 1000000000000000.0, step 0.01, default 0.0 |
| max_value | FLOAT | yes | Highest number that can come out. Not below min_value. | -1000000000000000.0 to 1000000000000000.0, step 0.01, default 100.0 |

Outputs: `INT`, `FLOAT`

## How it was tested

The harness builds a starting set of inputs from the default of every input (first entry for lists, a small gradient picture for IMAGE and a mask with a filled box for MASK). It runs the node once like that, then changes one input at a time: every entry of every list, the lowest, highest and a middle value of every number, both settings of every on/off switch, and an empty text for every text box. Each run must give the right number of outputs, and pictures and masks must have sane dimensions and no broken (NaN) values. A plain-words refusal to an out-of-range number or empty text counts as REJECTED (expected). Any other error counts as FAIL. The node was run in a temporary folder.

## Cases

| # | Input changed | Result | Output / message |
|---|---|---|---|
| 1 | baseline (all defaults) | PASS | INT=int 97; FLOAT=float 84.4422 |
| 2 | seed = 18446744073709551615 (max) | PASS | INT=int 43; FLOAT=float 2.18257 |
| 3 | seed = 9223372036854775807 (mid) | PASS | INT=int 80; FLOAT=float 31.6645 |
| 4 | min_value = -1000000000000000.0 (min) | PASS | INT=int -954420000713643; FLOAT=float -1.55578e+14 |
| 5 | min_value = 1000000000000000.0 (max) | REJECTED | ValueError: min_value (1e+15) is bigger than max_value (100). Swap them. |
| 6 | max_value = -1000000000000000.0 (min) | REJECTED | ValueError: min_value (0) is bigger than max_value (-1e+15). Swap them. |
| 7 | max_value = 1000000000000000.0 (max) | PASS | INT=int 45579999286357; FLOAT=float 8.44422e+14 |
| 8 | max_value = 0.0 (mid) | PASS | INT=int 0; FLOAT=float 0 |

## Verdict

All 8 cases behaved as expected (6 passed, 2 rejected with a clear message).
