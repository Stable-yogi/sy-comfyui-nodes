# Layout Boxes Merge SY (`SYLayoutBoxesMerge`)

Source: `nodes/sy_layout_boxes_merge.py`

**What it does:** Joins up to four box lists into one list, keeping the order. Empty inputs are skipped.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| boxes_1 | STRING | no | Box text from a Layout Box node or another merge. Leave empty to skip. | default '' |
| boxes_2 | STRING | no | Box text from a Layout Box node or another merge. Leave empty to skip. | default '' |
| boxes_3 | STRING | no | Box text from a Layout Box node or another merge. Leave empty to skip. | default '' |
| boxes_4 | STRING | no | Box text from a Layout Box node or another merge. Leave empty to skip. | default '' |

Outputs: `STRING`

## How it was tested

The harness builds a starting set of inputs from the default of every input (first entry for lists, a small gradient picture for IMAGE and a mask with a filled box for MASK). It runs the node once like that, then changes one input at a time: every entry of every list, the lowest, highest and a middle value of every number, both settings of every on/off switch, and an empty text for every text box. Each run must give the right number of outputs, and pictures and masks must have sane dimensions and no broken (NaN) values. A plain-words refusal to an out-of-range number or empty text counts as REJECTED (expected). Any other error counts as FAIL. The node was run in a temporary folder.

## Cases

| # | Input changed | Result | Output / message |
|---|---|---|---|
| 1 | baseline (all defaults) | REJECTED | ValueError: all four inputs are empty; connect at least one Layout Box node |
| 2 | boxes_1 = '' (empty) | REJECTED | ValueError: all four inputs are empty; connect at least one Layout Box node |
| 3 | boxes_2 = '' (empty) | REJECTED | ValueError: all four inputs are empty; connect at least one Layout Box node |
| 4 | boxes_3 = '' (empty) | REJECTED | ValueError: all four inputs are empty; connect at least one Layout Box node |
| 5 | boxes_4 = '' (empty) | REJECTED | ValueError: all four inputs are empty; connect at least one Layout Box node |

## Verdict

All 5 cases behaved as expected (0 passed, 5 rejected with a clear message).
