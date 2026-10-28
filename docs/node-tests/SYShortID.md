# Short ID SY (`SYShortID`)

Source: `nodes/sy_short_id.py`

**What it does:** Makes a short code such as a1b2c3d4. The same seed gives the same code. Add a prefix if you like.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| length | INT | yes | How many characters the code has (not counting the prefix). | 4 to 16, default 8 |
| charset | COMBO | yes | Which characters may appear: hex, letters, digits or mixed. | one of: hex, letters, digits, mixed |
| seed | INT | yes | Same seed gives the same code. Change it for a new code. | 0 to 18446744073709551615, default 0 |
| prefix | STRING | yes | Text put in front of the code, for example run_. | default '' |

Outputs: `STRING`

## How it was tested

The harness builds a starting set of inputs from the default of every input (first entry for lists, a small gradient picture for IMAGE and a mask with a filled box for MASK). It runs the node once like that, then changes one input at a time: every entry of every list, the lowest, highest and a middle value of every number, both settings of every on/off switch, and an empty text for every text box. Each run must give the right number of outputs, and pictures and masks must have sane dimensions and no broken (NaN) values. A plain-words refusal to an out-of-range number or empty text counts as REJECTED (expected). Any other error counts as FAIL. The node was run in a temporary folder.

## Cases

| # | Input changed | Result | Output / message |
|---|---|---|---|
| 1 | baseline (all defaults) | PASS | STRING=str 'cd18fc9f' |
| 2 | length = 4 (min) | PASS | STRING=str 'cd18' |
| 3 | length = 16 (max) | PASS | STRING=str 'cd18fc9fb6494384' |
| 4 | length = 10 (mid) | PASS | STRING=str 'cd18fc9fb6' |
| 5 | charset = 'letters' | PASS | STRING=str 'mynbiqpm' |
| 6 | charset = 'digits' | PASS | STRING=str '66048764' |
| 7 | charset = 'mixed' | PASS | STRING=str 'y0cq65zt' |
| 8 | seed = 18446744073709551615 (max) | PASS | STRING=str '07a6e3b1' |
| 9 | seed = 9223372036854775807 (mid) | PASS | STRING=str 'a4fe3f85' |
| 10 | prefix = '' (empty) | PASS | STRING=str 'cd18fc9f' |

## Verdict

All 10 cases behaved as expected (10 passed, 0 rejected with a clear message).
