# PasteBack SY (`SYPasteBack`)

Source: `nodes/sy_crop_paste.py`

**What it does:** Pastes a processed crop back into the original picture with a soft edge, using the crop info from Crop By Mask SY.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| image | IMAGE | yes | The original picture, the same one that was cropped. | picture batch [B,H,W,3] |
| crop | IMAGE | yes | The processed crop. It is resized to the crop box if its size differs. | picture batch [B,H,W,3] |
| crop_info | STRING | yes | The crop_info output of Crop By Mask SY. | default '' |
| feather | INT | yes | Width in pixels of the soft seam. 0 gives a hard edge. | 0 to 512, step 1, default 16 |
| crop_mask | MASK | no | Only paste where this mask is white. Leave empty to paste the whole crop. | mask [B,H,W] |

Outputs: `IMAGE`

## How it was tested

The harness builds a starting set of inputs from the default of every input (first entry for lists, a small gradient picture for IMAGE and a mask with a filled box for MASK). It runs the node once like that, then changes one input at a time: every entry of every list, the lowest, highest and a middle value of every number, both settings of every on/off switch, and an empty text for every text box. Each run must give the right number of outputs, and pictures and masks must have sane dimensions and no broken (NaN) values. A plain-words refusal to an out-of-range number or empty text counts as REJECTED (expected). Any other error counts as FAIL. The node was run in a temporary folder.

## Cases

| # | Input changed | Result | Output / message |
|---|---|---|---|
| 1 | baseline (all defaults) | PASS | IMAGE=tensor[1, 64, 96, 3] |
| 2 | crop_info = '' (empty) | REJECTED | ValueError: crop_info is not valid: connect the crop_info output of Crop By Mask SY |
| 3 | feather = 0 (min) | PASS | IMAGE=tensor[1, 64, 96, 3] |
| 4 | feather = 512 (max) | PASS | IMAGE=tensor[1, 64, 96, 3] |
| 5 | feather = 256 (mid) | PASS | IMAGE=tensor[1, 64, 96, 3] |

## Verdict

All 5 cases behaved as expected (4 passed, 1 rejected with a clear message).
