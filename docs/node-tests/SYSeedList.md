# Seed List SY (`SYSeedList`)

Source: `nodes/sy_seed_list.py`

**What it does:** Makes a comma list of seeds. Sequential counts up. Random fixed looks random but is the same every run.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| base_seed | INT | yes | Start number. Same start gives the same list. | 0 to 18446744073709551615, default 0 |
| count | INT | yes | How many seeds to make (1 to 64). | 1 to 64, default 4 |
| mode | COMBO | yes | Sequential: base, base+1... Random fixed: scattered numbers, repeatable. | one of: sequential, random_fixed |

Outputs: `STRING`, `INT`

## How it was tested

The harness builds a starting set of inputs from the default of every input (first entry for lists, a small gradient picture for IMAGE and a mask with a filled box for MASK). It runs the node once like that, then changes one input at a time: every entry of every list, the lowest, highest and a middle value of every number, both settings of every on/off switch, and an empty text for every text box. Each run must give the right number of outputs, and pictures and masks must have sane dimensions and no broken (NaN) values. A plain-words refusal to an out-of-range number or empty text counts as REJECTED (expected). Any other error counts as FAIL. The node was run in a temporary folder.

## Cases

| # | Input changed | Result | Output / message |
|---|---|---|---|
| 1 | baseline (all defaults) | PASS | STRING=str '0, 1, 2, 3'; INT=int 0 |
| 2 | base_seed = 18446744073709551615 (max) | PASS | STRING=str '18446744073709551615, 0, 1, 2'; INT=int 18446744073709551615 |
| 3 | base_seed = 9223372036854775807 (mid) | PASS | STRING=str '9223372036854775807, 9223372036854775808, 9223372036854775809, 92233720368547...'; INT=int 9223372036854775807 |
| 4 | count = 1 (min) | PASS | STRING=str '0'; INT=int 0 |
| 5 | count = 64 (max) | PASS | STRING=str '0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21,...'; INT=int 0 |
| 6 | count = 32 (mid) | PASS | STRING=str '0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21,...'; INT=int 0 |
| 7 | mode = 'random_fixed' | PASS | STRING=str '7758176404715800194, 15308084094301570617, 8791662011684601223, 9309829342914...'; INT=int 7758176404715800194 |

## Verdict

All 7 cases behaved as expected (7 passed, 0 rejected with a clear message).
