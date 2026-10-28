# XY Grid Assemble SY (`SYXYGridAssemble`)

Source: `nodes/sy_xy_grid_assemble.py`

**What it does:** Builds one grid picture from a batch, with the X values across the top and the Y values down the side.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| images | IMAGE | yes | The pictures, row by row: X changes fastest. The count must be X count times Y count. | picture batch [B,H,W,3] |
| x_labels | STRING | yes | Labels across the top, one per line. Empty means one column and no header. | default '', multiline |
| y_labels | STRING | yes | Labels down the side, one per line. Empty means one row and no side labels. | default '', multiline |
| gap | INT | yes | Space in pixels between pictures. | 0 to 256, default 8 |
| padding | INT | yes | Space in pixels around the whole grid. | 0 to 256, default 12 |
| background | STRING | yes | Grid colour: black, white, gray, dark_gray, red, green, blue, gold or six hex digits. | default 'dark_gray' |
| label_size | INT | yes | Label text height in pixels. | 8 to 96, default 24 |

Outputs: `IMAGE`

## How it was tested

The harness builds a starting set of inputs from the default of every input (first entry for lists, a small gradient picture for IMAGE and a mask with a filled box for MASK). It runs the node once like that, then changes one input at a time: every entry of every list, the lowest, highest and a middle value of every number, both settings of every on/off switch, and an empty text for every text box. Each run must give the right number of outputs, and pictures and masks must have sane dimensions and no broken (NaN) values. A plain-words refusal to an out-of-range number or empty text counts as REJECTED (expected). Any other error counts as FAIL. The node was run in a temporary folder.

## Cases

| # | Input changed | Result | Output / message |
|---|---|---|---|
| 1 | baseline (all defaults) | PASS | IMAGE=tensor[1, 88, 120, 3] |
| 2 | x_labels = '' (empty) | PASS | IMAGE=tensor[1, 88, 120, 3] |
| 3 | y_labels = '' (empty) | PASS | IMAGE=tensor[1, 88, 120, 3] |
| 4 | gap = 0 (min) | PASS | IMAGE=tensor[1, 88, 120, 3] |
| 5 | gap = 256 (max) | PASS | IMAGE=tensor[1, 88, 120, 3] |
| 6 | gap = 128 (mid) | PASS | IMAGE=tensor[1, 88, 120, 3] |
| 7 | padding = 0 (min) | PASS | IMAGE=tensor[1, 64, 96, 3] |
| 8 | padding = 256 (max) | PASS | IMAGE=tensor[1, 576, 608, 3] |
| 9 | padding = 128 (mid) | PASS | IMAGE=tensor[1, 320, 352, 3] |
| 10 | background = '' (empty) | REJECTED | ValueError: background '' is not a colour: use a name (black, blue, dark_gray, gold, gray... |
| 11 | label_size = 8 (min) | PASS | IMAGE=tensor[1, 88, 120, 3] |
| 12 | label_size = 96 (max) | PASS | IMAGE=tensor[1, 88, 120, 3] |
| 13 | label_size = 52 (mid) | PASS | IMAGE=tensor[1, 88, 120, 3] |

## Verdict

All 13 cases behaved as expected (12 passed, 1 rejected with a clear message).
