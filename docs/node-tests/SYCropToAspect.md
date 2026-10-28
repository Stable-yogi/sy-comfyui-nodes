# Crop To Aspect SY (`SYCropToAspect`)

Source: `nodes/sy_crop_to_aspect.py`

**What it does:** Crops a picture to a shape such as 16:9 or 1:1. Takes the biggest area of that shape, centred or moved with the offsets.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| image | IMAGE | yes | The picture or batch of pictures to crop. | picture batch [B,H,W,3] |
| aspect_w | INT | yes | Width part of the shape, the 16 in 16:9. | 1 to 1000, default 16 |
| aspect_h | INT | yes | Height part of the shape, the 9 in 16:9. | 1 to 1000, default 9 |
| offset_x | FLOAT | yes | Moves the crop sideways. -1 is left, 0 is centre, 1 is right. | -1.0 to 1.0, step 0.01, default 0.0 |
| offset_y | FLOAT | yes | Moves the crop up or down. -1 is top, 0 is centre, 1 is bottom. | -1.0 to 1.0, step 0.01, default 0.0 |

Outputs: `IMAGE`, `INT`, `INT`

## How it was tested

The harness builds a starting set of inputs from the default of every input (first entry for lists, a small gradient picture for IMAGE and a mask with a filled box for MASK). It runs the node once like that, then changes one input at a time: every entry of every list, the lowest, highest and a middle value of every number, both settings of every on/off switch, and an empty text for every text box. Each run must give the right number of outputs, and pictures and masks must have sane dimensions and no broken (NaN) values. A plain-words refusal to an out-of-range number or empty text counts as REJECTED (expected). Any other error counts as FAIL. The node was run in a temporary folder.

## Cases

| # | Input changed | Result | Output / message |
|---|---|---|---|
| 1 | baseline (all defaults) | PASS | IMAGE=tensor[1, 54, 96, 3]; INT=int 96; INT=int 54 |
| 2 | aspect_w = 1 (min) | PASS | IMAGE=tensor[1, 64, 7, 3]; INT=int 7; INT=int 64 |
| 3 | aspect_w = 1000 (max) | PASS | IMAGE=tensor[1, 1, 96, 3]; INT=int 96; INT=int 1 |
| 4 | aspect_w = 500 (mid) | PASS | IMAGE=tensor[1, 2, 96, 3]; INT=int 96; INT=int 2 |
| 5 | aspect_h = 1 (min) | PASS | IMAGE=tensor[1, 6, 96, 3]; INT=int 96; INT=int 6 |
| 6 | aspect_h = 1000 (max) | PASS | IMAGE=tensor[1, 64, 1, 3]; INT=int 1; INT=int 64 |
| 7 | aspect_h = 500 (mid) | PASS | IMAGE=tensor[1, 64, 2, 3]; INT=int 2; INT=int 64 |
| 8 | offset_x = -1.0 (min) | PASS | IMAGE=tensor[1, 54, 96, 3]; INT=int 96; INT=int 54 |
| 9 | offset_x = 1.0 (max) | PASS | IMAGE=tensor[1, 54, 96, 3]; INT=int 96; INT=int 54 |
| 10 | offset_y = -1.0 (min) | PASS | IMAGE=tensor[1, 54, 96, 3]; INT=int 96; INT=int 54 |
| 11 | offset_y = 1.0 (max) | PASS | IMAGE=tensor[1, 54, 96, 3]; INT=int 96; INT=int 54 |

## Verdict

All 11 cases behaved as expected (11 passed, 0 rejected with a clear message).
