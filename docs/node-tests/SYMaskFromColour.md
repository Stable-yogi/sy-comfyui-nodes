# MaskFromColour SY (`SYMaskFromColour`)

Source: `nodes/sy_mask_from_colour.py`

**What it does:** Makes a mask from every pixel that is close to a chosen colour. Tolerance sets how close.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| image | IMAGE | yes | The picture to pick the colour from. | picture batch [B,H,W,3] |
| red | INT | yes | Red part of the wanted colour, 0 to 255. | 0 to 255, step 1, default 0 |
| green | INT | yes | Green part of the wanted colour, 0 to 255. | 0 to 255, step 1, default 255 |
| blue | INT | yes | Blue part of the wanted colour, 0 to 255. | 0 to 255, step 1, default 0 |
| tolerance | INT | yes | How far each colour part may differ and still count. 0 is an exact match. | 0 to 255, step 1, default 20 |

Outputs: `MASK`

## How it was tested

The harness builds a starting set of inputs from the default of every input (first entry for lists, a small gradient picture for IMAGE and a mask with a filled box for MASK). It runs the node once like that, then changes one input at a time: every entry of every list, the lowest, highest and a middle value of every number, both settings of every on/off switch, and an empty text for every text box. Each run must give the right number of outputs, and pictures and masks must have sane dimensions and no broken (NaN) values. A plain-words refusal to an out-of-range number or empty text counts as REJECTED (expected). Any other error counts as FAIL. The node was run in a temporary folder.

## Cases

| # | Input changed | Result | Output / message |
|---|---|---|---|
| 1 | baseline (all defaults) | PASS | MASK=tensor[1, 64, 96] |
| 2 | red = 255 (max) | PASS | MASK=tensor[1, 64, 96] |
| 3 | red = 127 (mid) | PASS | MASK=tensor[1, 64, 96] |
| 4 | green = 0 (min) | PASS | MASK=tensor[1, 64, 96] |
| 5 | green = 127 (mid) | PASS | MASK=tensor[1, 64, 96] |
| 6 | blue = 255 (max) | PASS | MASK=tensor[1, 64, 96] |
| 7 | blue = 127 (mid) | PASS | MASK=tensor[1, 64, 96] |
| 8 | tolerance = 0 (min) | PASS | MASK=tensor[1, 64, 96] |
| 9 | tolerance = 255 (max) | PASS | MASK=tensor[1, 64, 96] |
| 10 | tolerance = 127 (mid) | PASS | MASK=tensor[1, 64, 96] |

## Verdict

All 10 cases behaved as expected (10 passed, 0 rejected with a clear message).
