# XY Pick SY (`SYXYPick`)

Source: `nodes/sy_xy_pick.py`

**What it does:** Picks one cell of an XY grid from a running index. Feed it a counter and auto-queue to render the whole grid.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| x_values | STRING | yes | The X list, one value per line. Empty means a single column. | default '', multiline |
| y_values | STRING | yes | The Y list, one value per line. Empty means a single row. | default '', multiline |
| index | INT | yes | Cell number from 0, going across each row first. | 0 to 2147483647, default 0 |
| wrap | BOOLEAN | yes | On: an index past the end starts again at 0. Off: it stops with an error. | default False |

Outputs: `STRING`, `STRING`, `INT`, `INT`, `INT`

## How it was tested

The harness builds a starting set of inputs from the default of every input (first entry for lists, a small gradient picture for IMAGE and a mask with a filled box for MASK). It runs the node once like that, then changes one input at a time: every entry of every list, the lowest, highest and a middle value of every number, both settings of every on/off switch, and an empty text for every text box. Each run must give the right number of outputs, and pictures and masks must have sane dimensions and no broken (NaN) values. A plain-words refusal to an out-of-range number or empty text counts as REJECTED (expected). Any other error counts as FAIL. The node was run in a temporary folder.

## Cases

| # | Input changed | Result | Output / message |
|---|---|---|---|
| 1 | baseline (all defaults) | PASS | STRING=str ''; STRING=str ''; INT=int 0; INT=int 0; INT=int 1 |
| 2 | x_values = '' (empty) | PASS | STRING=str ''; STRING=str ''; INT=int 0; INT=int 0; INT=int 1 |
| 3 | y_values = '' (empty) | PASS | STRING=str ''; STRING=str ''; INT=int 0; INT=int 0; INT=int 1 |
| 4 | index = 2147483647 (max) | REJECTED | ValueError: index 2147483647 is outside the grid: it has 1 x 1 = 1 cells, so use 0 to 0 (... |
| 5 | index = 1073741823 (mid) | REJECTED | ValueError: index 1073741823 is outside the grid: it has 1 x 1 = 1 cells, so use 0 to 0 (... |
| 6 | wrap = True | PASS | STRING=str ''; STRING=str ''; INT=int 0; INT=int 0; INT=int 1 |

## Verdict

All 6 cases behaved as expected (4 passed, 2 rejected with a clear message).
