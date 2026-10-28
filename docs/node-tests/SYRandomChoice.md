# Random Choice SY (`SYRandomChoice`)

Source: `nodes/sy_random_choice.py`

**What it does:** Picks one line out of your list of lines. The same seed always picks the same line.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| lines | STRING | yes | One choice per line. Empty lines are skipped. | default '', multiline |
| seed | INT | yes | Decides the pick. Change it to get another line. | 0 to 18446744073709551615, default 0 |

Outputs: `STRING`, `INT`

## How it was tested

The harness builds a starting set of inputs from the default of every input (first entry for lists, a small gradient picture for IMAGE and a mask with a filled box for MASK). It runs the node once like that, then changes one input at a time: every entry of every list, the lowest, highest and a middle value of every number, both settings of every on/off switch, and an empty text for every text box. Each run must give the right number of outputs, and pictures and masks must have sane dimensions and no broken (NaN) values. A plain-words refusal to an out-of-range number or empty text counts as REJECTED (expected). Any other error counts as FAIL. The node was run in a temporary folder.

## Cases

| # | Input changed | Result | Output / message |
|---|---|---|---|
| 1 | baseline (all defaults) | REJECTED | ValueError: lines is empty - type at least one line of text |
| 2 | lines = '' (empty) | REJECTED | ValueError: lines is empty - type at least one line of text |
| 3 | seed = 18446744073709551615 (max) | REJECTED | ValueError: lines is empty - type at least one line of text |
| 4 | seed = 9223372036854775807 (mid) | REJECTED | ValueError: lines is empty - type at least one line of text |

## Verdict

All 4 cases behaved as expected (0 passed, 4 rejected with a clear message).
