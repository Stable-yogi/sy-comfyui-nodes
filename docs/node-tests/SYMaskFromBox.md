# MaskFromBox SY (`SYMaskFromBox`)

Source: `nodes/sy_mask_from_box.py`

**What it does:** Makes a mask that is white inside a rectangle and black elsewhere. Parts outside the canvas are cut off.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| x | INT | yes | Left edge of the box in pixels. | -16384 to 16384, step 1, default 0 |
| y | INT | yes | Top edge of the box in pixels. | -16384 to 16384, step 1, default 0 |
| box_width | INT | yes | Width of the box in pixels. | 0 to 16384, step 1, default 256 |
| box_height | INT | yes | Height of the box in pixels. | 0 to 16384, step 1, default 256 |
| canvas_width | INT | yes | Width of the mask in pixels. | 1 to 16384, step 1, default 1024 |
| canvas_height | INT | yes | Height of the mask in pixels. | 1 to 16384, step 1, default 1024 |

Outputs: `MASK`

## How it was tested

The harness builds a starting set of inputs from the default of every input (first entry for lists, a small gradient picture for IMAGE and a mask with a filled box for MASK). It runs the node once like that, then changes one input at a time: every entry of every list, the lowest, highest and a middle value of every number, both settings of every on/off switch, and an empty text for every text box. Each run must give the right number of outputs, and pictures and masks must have sane dimensions and no broken (NaN) values. A plain-words refusal to an out-of-range number or empty text counts as REJECTED (expected). Any other error counts as FAIL. The node was run in a temporary folder.

## Cases

| # | Input changed | Result | Output / message |
|---|---|---|---|
| 1 | baseline (all defaults) | PASS | MASK=tensor[1, 1024, 1024] |
| 2 | x = -16384 (min) | PASS | MASK=tensor[1, 1024, 1024] |
| 3 | x = 16384 (max) | PASS | MASK=tensor[1, 1024, 1024] |
| 4 | y = -16384 (min) | PASS | MASK=tensor[1, 1024, 1024] |
| 5 | y = 16384 (max) | PASS | MASK=tensor[1, 1024, 1024] |
| 6 | box_width = 0 (min) | PASS | MASK=tensor[1, 1024, 1024] |
| 7 | box_width = 16384 (max) | PASS | MASK=tensor[1, 1024, 1024] |
| 8 | box_width = 8192 (mid) | PASS | MASK=tensor[1, 1024, 1024] |
| 9 | box_height = 0 (min) | PASS | MASK=tensor[1, 1024, 1024] |
| 10 | box_height = 16384 (max) | PASS | MASK=tensor[1, 1024, 1024] |
| 11 | box_height = 8192 (mid) | PASS | MASK=tensor[1, 1024, 1024] |
| 12 | canvas_width = 1 (min) | PASS | MASK=tensor[1, 1024, 1] |
| 13 | canvas_width = 16384 (max) | PASS | MASK=tensor[1, 1024, 16384] |
| 14 | canvas_width = 8192 (mid) | PASS | MASK=tensor[1, 1024, 8192] |
| 15 | canvas_height = 1 (min) | PASS | MASK=tensor[1, 1, 1024] |
| 16 | canvas_height = 16384 (max) | PASS | MASK=tensor[1, 16384, 1024] |
| 17 | canvas_height = 8192 (mid) | PASS | MASK=tensor[1, 8192, 1024] |

## Verdict

All 17 cases behaved as expected (17 passed, 0 rejected with a clear message).
