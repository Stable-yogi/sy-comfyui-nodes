# XY Label Strip SY (`SYXYLabelStrip`)

Source: `nodes/sy_xy_label_strip.py`

**What it does:** Writes the XY grid as a Markdown table. Each cell shows its picture number, so you can match it to the batch.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| x_values | STRING | yes | The X list, one value per line. | default '', multiline |
| y_values | STRING | yes | The Y list, one value per line. Empty means a single row. | default '', multiline |
| x_name | STRING | yes | Name of the X axis, shown in the table corner. | default 'X' |
| y_name | STRING | yes | Name of the Y axis, shown in the table corner. | default 'Y' |

Outputs: `STRING`

## How it was tested

The harness builds a starting set of inputs from the default of every input (first entry for lists, a small gradient picture for IMAGE and a mask with a filled box for MASK). It runs the node once like that, then changes one input at a time: every entry of every list, the lowest, highest and a middle value of every number, both settings of every on/off switch, and an empty text for every text box. Each run must give the right number of outputs, and pictures and masks must have sane dimensions and no broken (NaN) values. A plain-words refusal to an out-of-range number or empty text counts as REJECTED (expected). Any other error counts as FAIL. The node was run in a temporary folder.

## Cases

| # | Input changed | Result | Output / message |
|---|---|---|---|
| 1 | baseline (all defaults) | REJECTED | ValueError: both lists are empty: give at least one X or Y value |
| 2 | x_values = '' (empty) | REJECTED | ValueError: both lists are empty: give at least one X or Y value |
| 3 | y_values = '' (empty) | REJECTED | ValueError: both lists are empty: give at least one X or Y value |
| 4 | x_name = '' (empty) | REJECTED | ValueError: both lists are empty: give at least one X or Y value |
| 5 | y_name = '' (empty) | REJECTED | ValueError: both lists are empty: give at least one X or Y value |

## Verdict

All 5 cases behaved as expected (0 passed, 5 rejected with a clear message).
