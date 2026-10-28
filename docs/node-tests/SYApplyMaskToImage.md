# ApplyMaskToImage SY (`SYApplyMaskToImage`)

Source: `nodes/sy_apply_mask_to_image.py`

**What it does:** Hides the part of a picture outside the mask. The hidden part becomes see-through (alpha), black or gray.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| image | IMAGE | yes | The picture to cut out. | picture batch [B,H,W,3] |
| mask | MASK | yes | The mask. It is stretched to the picture size if needed. | mask [B,H,W] |
| fill | COMBO | yes | What the hidden part becomes: see-through (adds an alpha channel), black or gray. | one of: alpha, black, gray |
| keep | COMBO | yes | masked keeps the white part of the mask, outside keeps the black part. | one of: masked, outside |

Outputs: `IMAGE`

## How it was tested

The harness builds a starting set of inputs from the default of every input (first entry for lists, a small gradient picture for IMAGE and a mask with a filled box for MASK). It runs the node once like that, then changes one input at a time: every entry of every list, the lowest, highest and a middle value of every number, both settings of every on/off switch, and an empty text for every text box. Each run must give the right number of outputs, and pictures and masks must have sane dimensions and no broken (NaN) values. A plain-words refusal to an out-of-range number or empty text counts as REJECTED (expected). Any other error counts as FAIL. The node was run in a temporary folder.

## Cases

| # | Input changed | Result | Output / message |
|---|---|---|---|
| 1 | baseline (all defaults) | PASS | IMAGE=tensor[1, 64, 96, 4] |
| 2 | fill = 'black' | PASS | IMAGE=tensor[1, 64, 96, 3] |
| 3 | fill = 'gray' | PASS | IMAGE=tensor[1, 64, 96, 3] |
| 4 | keep = 'outside' | PASS | IMAGE=tensor[1, 64, 96, 4] |

## Verdict

All 4 cases behaved as expected (4 passed, 0 rejected with a clear message).
