# MaskOverlayPreview SY (`SYMaskOverlayPreview`)

Source: `nodes/sy_mask_overlay_preview.py`

**What it does:** Shows a mask on top of a picture as a coloured tint, so you can check what it covers.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| image | IMAGE | yes | The picture to show the mask on. | picture batch [B,H,W,3] |
| mask | MASK | yes | The mask to show. It is stretched to the picture size if needed. | mask [B,H,W] |
| red | INT | yes | Red part of the tint colour, 0 to 255. | 0 to 255, step 1, default 255 |
| green | INT | yes | Green part of the tint colour, 0 to 255. | 0 to 255, step 1, default 0 |
| blue | INT | yes | Blue part of the tint colour, 0 to 255. | 0 to 255, step 1, default 0 |
| opacity | FLOAT | yes | How strong the tint is. 0 shows no tint, 1 covers the picture. | 0.0 to 1.0, step 0.01, default 0.5 |

Outputs: `IMAGE`

## How it was tested

The harness builds a starting set of inputs from the default of every input (first entry for lists, a small gradient picture for IMAGE and a mask with a filled box for MASK). It runs the node once like that, then changes one input at a time: every entry of every list, the lowest, highest and a middle value of every number, both settings of every on/off switch, and an empty text for every text box. Each run must give the right number of outputs, and pictures and masks must have sane dimensions and no broken (NaN) values. A plain-words refusal to an out-of-range number or empty text counts as REJECTED (expected). Any other error counts as FAIL. The node was run in a temporary folder.

## Cases

| # | Input changed | Result | Output / message |
|---|---|---|---|
| 1 | baseline (all defaults) | PASS | IMAGE=tensor[1, 64, 96, 3] |
| 2 | red = 0 (min) | PASS | IMAGE=tensor[1, 64, 96, 3] |
| 3 | red = 127 (mid) | PASS | IMAGE=tensor[1, 64, 96, 3] |
| 4 | green = 255 (max) | PASS | IMAGE=tensor[1, 64, 96, 3] |
| 5 | green = 127 (mid) | PASS | IMAGE=tensor[1, 64, 96, 3] |
| 6 | blue = 255 (max) | PASS | IMAGE=tensor[1, 64, 96, 3] |
| 7 | blue = 127 (mid) | PASS | IMAGE=tensor[1, 64, 96, 3] |
| 8 | opacity = 0.0 (min) | PASS | IMAGE=tensor[1, 64, 96, 3] |
| 9 | opacity = 1.0 (max) | PASS | IMAGE=tensor[1, 64, 96, 3] |

## Verdict

All 9 cases behaved as expected (9 passed, 0 rejected with a clear message).
