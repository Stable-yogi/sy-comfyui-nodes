# CyclePick SY (`SYCyclePick`)

Source: `nodes/sy_cycle_pick.py`

**What it does:** Picks one line from a list using a counter. When the counter passes the end it starts again from the first line.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| items | STRING | yes | One item per line. Blank lines are skipped. | default '', multiline |
| counter | INT | yes | Which item to take, counting from 0. It goes round when too big. | -2147483648 to 2147483647, default 0 |

Outputs: `STRING`, `INT`, `INT`

## How it was tested

The harness builds a starting set of inputs from the default of every input (first entry for lists, a small gradient picture for IMAGE and a mask with a filled box for MASK). It runs the node once like that, then changes one input at a time: every entry of every list, the lowest, highest and a middle value of every number, both settings of every on/off switch, and an empty text for every text box. Each run must give the right number of outputs, and pictures and masks must have sane dimensions and no broken (NaN) values. A plain-words refusal to an out-of-range number or empty text counts as REJECTED (expected). Any other error counts as FAIL. The node was run in a temporary folder.

## Cases

| # | Input changed | Result | Output / message |
|---|---|---|---|
| 1 | baseline (all defaults) | REJECTED | ValueError: items is empty: type at least one line of text |
| 2 | items = '' (empty) | REJECTED | ValueError: items is empty: type at least one line of text |
| 3 | counter = -2147483648 (min) | REJECTED | ValueError: items is empty: type at least one line of text |
| 4 | counter = 2147483647 (max) | REJECTED | ValueError: items is empty: type at least one line of text |
| 5 | counter = -1 (mid) | REJECTED | ValueError: items is empty: type at least one line of text |

## Verdict

All 5 cases behaved as expected (0 passed, 5 rejected with a clear message).
