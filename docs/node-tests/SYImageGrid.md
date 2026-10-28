# Image Grid SY (`SYImageGrid`)

Source: `nodes/sy_image_grid.py`

**What it does:** Lays a batch of pictures out as one contact sheet. Optional captions, one per line, go under each picture.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| images | IMAGE | yes | The batch of pictures to put on the sheet. All are sized like the first one. | picture batch [B,H,W,3] |
| columns | INT | yes | How many pictures per row. Fewer pictures than columns gives a single row. | 1 to 64, default 4 |
| gap | INT | yes | Space in pixels between pictures and around the edge. | 0 to 256, default 8 |
| background | STRING | yes | Sheet colour: black, white, gray, dark_gray, red, green, blue, gold or six hex digits. | default 'black' |
| labels | STRING | no | One caption per line, in picture order. Leave empty for no captions. | default '', multiline |
| label_size | INT | no | Caption text height in pixels. | 8 to 96, default 20 |

Outputs: `IMAGE`

## How it was tested

The harness builds a starting set of inputs from the default of every input (first entry for lists, a small gradient picture for IMAGE and a mask with a filled box for MASK). It runs the node once like that, then changes one input at a time: every entry of every list, the lowest, highest and a middle value of every number, both settings of every on/off switch, and an empty text for every text box. Each run must give the right number of outputs, and pictures and masks must have sane dimensions and no broken (NaN) values. A plain-words refusal to an out-of-range number or empty text counts as REJECTED (expected). Any other error counts as FAIL. The node was run in a temporary folder.

## Cases

| # | Input changed | Result | Output / message |
|---|---|---|---|
| 1 | baseline (all defaults) | PASS | IMAGE=tensor[1, 80, 112, 3] |
| 2 | columns = 1 (min) | PASS | IMAGE=tensor[1, 80, 112, 3] |
| 3 | columns = 64 (max) | PASS | IMAGE=tensor[1, 80, 112, 3] |
| 4 | columns = 32 (mid) | PASS | IMAGE=tensor[1, 80, 112, 3] |
| 5 | gap = 0 (min) | PASS | IMAGE=tensor[1, 64, 96, 3] |
| 6 | gap = 256 (max) | PASS | IMAGE=tensor[1, 576, 608, 3] |
| 7 | gap = 128 (mid) | PASS | IMAGE=tensor[1, 320, 352, 3] |
| 8 | background = '' (empty) | REJECTED | ValueError: background '' is not a colour: use a name (black, blue, dark_gray, gold, gray... |
| 9 | labels = '' (empty) | PASS | IMAGE=tensor[1, 80, 112, 3] |
| 10 | label_size = 8 (min) | PASS | IMAGE=tensor[1, 80, 112, 3] |
| 11 | label_size = 96 (max) | PASS | IMAGE=tensor[1, 80, 112, 3] |
| 12 | label_size = 52 (mid) | PASS | IMAGE=tensor[1, 80, 112, 3] |

## Verdict

All 12 cases behaved as expected (11 passed, 1 rejected with a clear message).
