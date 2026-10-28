# Seed Stepper SY (`SYSeedStepper`)

Source: `nodes/sy_seed_stepper.py`

**What it does:** Builds a list of seeds (base, base+step, base+2*step...) and gives the seed at one index, plus the whole list.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| base_seed | INT | yes | The first seed of the list. | 0 to 18446744073709551615, default 0 |
| step | INT | yes | What is added to the seed for each next place. | -1000000 to 1000000, default 1 |
| count | INT | yes | How many seeds are in the list. | 1 to 256, default 4 |
| index | INT | yes | Which place of the list to give out. 0 is the first. | 0 to 100000, default 0 |
| wrap | BOOLEAN | yes | On: an index past the end starts over at the front. Off: that is an error. | default True |

Outputs: `INT`, `STRING`

## How it was tested

The harness builds a starting set of inputs from the default of every input (first entry for lists, a small gradient picture for IMAGE and a mask with a filled box for MASK). It runs the node once like that, then changes one input at a time: every entry of every list, the lowest, highest and a middle value of every number, both settings of every on/off switch, and an empty text for every text box. Each run must give the right number of outputs, and pictures and masks must have sane dimensions and no broken (NaN) values. A plain-words refusal to an out-of-range number or empty text counts as REJECTED (expected). Any other error counts as FAIL. The node was run in a temporary folder.

## Cases

| # | Input changed | Result | Output / message |
|---|---|---|---|
| 1 | baseline (all defaults) | PASS | INT=int 0; STRING=str '0, 1, 2, 3' |
| 2 | base_seed = 18446744073709551615 (max) | PASS | INT=int 18446744073709551615; STRING=str '18446744073709551615, 0, 1, 2' |
| 3 | base_seed = 9223372036854775807 (mid) | PASS | INT=int 9223372036854775807; STRING=str '9223372036854775807, 9223372036854775808, 9223372036854775809, 92233720368547...' |
| 4 | step = -1000000 (min) | PASS | INT=int 0; STRING=str '0, 18446744073708551616, 18446744073707551616, 18446744073706551616' |
| 5 | step = 1000000 (max) | PASS | INT=int 0; STRING=str '0, 1000000, 2000000, 3000000' |
| 6 | step = 0 (mid) | PASS | INT=int 0; STRING=str '0, 0, 0, 0' |
| 7 | count = 1 (min) | PASS | INT=int 0; STRING=str '0' |
| 8 | count = 256 (max) | PASS | INT=int 0; STRING=str '0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21,...' |
| 9 | count = 128 (mid) | PASS | INT=int 0; STRING=str '0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21,...' |
| 10 | index = 100000 (max) | PASS | INT=int 0; STRING=str '0, 1, 2, 3' |
| 11 | index = 50000 (mid) | PASS | INT=int 0; STRING=str '0, 1, 2, 3' |
| 12 | wrap = False | PASS | INT=int 0; STRING=str '0, 1, 2, 3' |

## Verdict

All 12 cases behaved as expected (12 passed, 0 rejected with a clear message).
