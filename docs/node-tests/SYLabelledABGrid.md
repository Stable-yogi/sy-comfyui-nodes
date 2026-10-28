# Labelled AB Grid SY (`SYLabelledABGrid`)

Source: `nodes/sy_image_grid.py`

**What it does:** Puts two to four pictures in a strip with a caption under each. Good for comparing checkpoints on the same prompt.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| image_a | IMAGE | yes | First picture. Its size sets the size of every cell. | picture batch [B,H,W,3] |
| image_b | IMAGE | yes | Second picture. It is resized to match the first. | picture batch [B,H,W,3] |
| label_a | STRING | yes | Caption under the first picture. Leave empty for none. | default 'A' |
| label_b | STRING | yes | Caption under the second picture. Leave empty for none. | default 'B' |
| direction | COMBO | yes | row puts pictures side by side, column stacks them. | one of: row, column |
| gap | INT | yes | Space in pixels between pictures and around the edge. | 0 to 256, default 8 |
| background | STRING | yes | Strip colour: a name like black or white, or six hex digits. | default 'black' |
| label_size | INT | yes | Caption text height in pixels. | 8 to 96, default 24 |
| image_c | IMAGE | no | Optional third picture. | picture batch [B,H,W,3] |
| image_d | IMAGE | no | Optional fourth picture. | picture batch [B,H,W,3] |
| label_c | STRING | no | Caption under the third picture. | default 'C' |
| label_d | STRING | no | Caption under the fourth picture. | default 'D' |

Outputs: `IMAGE`

## How it was tested

The harness builds a starting set of inputs from the default of every input (first entry for lists, a small gradient picture for IMAGE and a mask with a filled box for MASK). It runs the node once like that, then changes one input at a time: every entry of every list, the lowest, highest and a middle value of every number, both settings of every on/off switch, and an empty text for every text box. Each run must give the right number of outputs, and pictures and masks must have sane dimensions and no broken (NaN) values. A plain-words refusal to an out-of-range number or empty text counts as REJECTED (expected). Any other error counts as FAIL. The node was run in a temporary folder.

## Cases

| # | Input changed | Result | Output / message |
|---|---|---|---|
| 1 | baseline (all defaults) | PASS | IMAGE=tensor[1, 112, 424, 3] |
| 2 | label_a = '' (empty) | PASS | IMAGE=tensor[1, 112, 424, 3] |
| 3 | label_b = '' (empty) | PASS | IMAGE=tensor[1, 112, 424, 3] |
| 4 | direction = 'column' | PASS | IMAGE=tensor[1, 424, 112, 3] |
| 5 | gap = 0 (min) | PASS | IMAGE=tensor[1, 96, 384, 3] |
| 6 | gap = 256 (max) | PASS | IMAGE=tensor[1, 608, 1664, 3] |
| 7 | gap = 128 (mid) | PASS | IMAGE=tensor[1, 352, 1024, 3] |
| 8 | background = '' (empty) | REJECTED | ValueError: background '' is not a colour: use a name (black, blue, dark_gray, gold, gray... |
| 9 | label_size = 8 (min) | PASS | IMAGE=tensor[1, 96, 424, 3] |
| 10 | label_size = 96 (max) | PASS | IMAGE=tensor[1, 184, 424, 3] |
| 11 | label_size = 52 (mid) | PASS | IMAGE=tensor[1, 140, 424, 3] |
| 12 | label_c = '' (empty) | PASS | IMAGE=tensor[1, 112, 424, 3] |
| 13 | label_d = '' (empty) | PASS | IMAGE=tensor[1, 112, 424, 3] |

## Verdict

All 13 cases behaved as expected (12 passed, 1 rejected with a clear message).
