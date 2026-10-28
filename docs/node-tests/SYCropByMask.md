# CropByMask SY (`SYCropByMask`)

Source: `nodes/sy_crop_paste.py`

**What it does:** Cuts the picture and mask around the white part of the mask. Gives a crop info note for Paste Back SY.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| image | IMAGE | yes | The picture to cut. | picture batch [B,H,W,3] |
| mask | MASK | yes | Marks the area to keep. Must be the same size as the picture. | mask [B,H,W] |
| padding | INT | yes | Extra pixels kept around the white part for context. | 0 to 4096, step 1, default 32 |
| multiple_of | INT | yes | Crop width and height become a multiple of this. Models like 8 or 64. | 1 to 512, step 1, default 8 |
| threshold | FLOAT | yes | Mask values at or above this count as white. | 0.01 to 1.0, step 0.01, default 0.5 |
| on_empty | COMBO | yes | When nothing is white: crop the whole image, or stop with an error. | one of: whole_image, error |

Outputs: `IMAGE`, `MASK`, `STRING`

## How it was tested

The harness builds a starting set of inputs from the default of every input (first entry for lists, a small gradient picture for IMAGE and a mask with a filled box for MASK). It runs the node once like that, then changes one input at a time: every entry of every list, the lowest, highest and a middle value of every number, both settings of every on/off switch, and an empty text for every text box. Each run must give the right number of outputs, and pictures and masks must have sane dimensions and no broken (NaN) values. A plain-words refusal to an out-of-range number or empty text counts as REJECTED (expected). Any other error counts as FAIL. The node was run in a temporary folder.

## Cases

| # | Input changed | Result | Output / message |
|---|---|---|---|
| 1 | baseline (all defaults) | PASS | IMAGE=tensor[1, 64, 96, 3]; MASK=tensor[1, 64, 96]; STRING=str '{"h": 64, "image_h": 64, "image_w": 96, "version": 1, "w": 96, "x": 0, "y": 0}' |
| 2 | padding = 0 (min) | PASS | IMAGE=tensor[1, 32, 48, 3]; MASK=tensor[1, 32, 48]; STRING=str '{"h": 32, "image_h": 64, "image_w": 96, "version": 1, "w": 48, "x": 24, "y": 16}' |
| 3 | padding = 4096 (max) | PASS | IMAGE=tensor[1, 64, 96, 3]; MASK=tensor[1, 64, 96]; STRING=str '{"h": 64, "image_h": 64, "image_w": 96, "version": 1, "w": 96, "x": 0, "y": 0}' |
| 4 | padding = 2048 (mid) | PASS | IMAGE=tensor[1, 64, 96, 3]; MASK=tensor[1, 64, 96]; STRING=str '{"h": 64, "image_h": 64, "image_w": 96, "version": 1, "w": 96, "x": 0, "y": 0}' |
| 5 | multiple_of = 1 (min) | PASS | IMAGE=tensor[1, 64, 96, 3]; MASK=tensor[1, 64, 96]; STRING=str '{"h": 64, "image_h": 64, "image_w": 96, "version": 1, "w": 96, "x": 0, "y": 0}' |
| 6 | multiple_of = 512 (max) | PASS | IMAGE=tensor[1, 64, 96, 3]; MASK=tensor[1, 64, 96]; STRING=str '{"h": 64, "image_h": 64, "image_w": 96, "version": 1, "w": 96, "x": 0, "y": 0}' |
| 7 | multiple_of = 256 (mid) | PASS | IMAGE=tensor[1, 64, 96, 3]; MASK=tensor[1, 64, 96]; STRING=str '{"h": 64, "image_h": 64, "image_w": 96, "version": 1, "w": 96, "x": 0, "y": 0}' |
| 8 | threshold = 0.01 (min) | PASS | IMAGE=tensor[1, 64, 96, 3]; MASK=tensor[1, 64, 96]; STRING=str '{"h": 64, "image_h": 64, "image_w": 96, "version": 1, "w": 96, "x": 0, "y": 0}' |
| 9 | threshold = 1.0 (max) | PASS | IMAGE=tensor[1, 64, 96, 3]; MASK=tensor[1, 64, 96]; STRING=str '{"h": 64, "image_h": 64, "image_w": 96, "version": 1, "w": 96, "x": 0, "y": 0}' |
| 10 | threshold = 0.505 (mid) | PASS | IMAGE=tensor[1, 64, 96, 3]; MASK=tensor[1, 64, 96]; STRING=str '{"h": 64, "image_h": 64, "image_w": 96, "version": 1, "w": 96, "x": 0, "y": 0}' |
| 11 | on_empty = 'error' | PASS | IMAGE=tensor[1, 64, 96, 3]; MASK=tensor[1, 64, 96]; STRING=str '{"h": 64, "image_h": 64, "image_w": 96, "version": 1, "w": 96, "x": 0, "y": 0}' |

## Verdict

All 11 cases behaved as expected (11 passed, 0 rejected with a clear message).
