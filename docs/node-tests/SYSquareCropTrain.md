# Crop Square Centre For Training SY (`SYSquareCropTrain`)

Source: `nodes/sy_square_crop_train.py`

**What it does:** Cuts the biggest square from the middle of each picture and resizes it to the size you give, ready for training.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| images | IMAGE | yes | The pictures to crop. Every picture in the batch is cropped the same way. | picture batch [B,H,W,3] |
| size | INT | yes | Width and height of the finished square in pixels. | 8 to 8192, step 8, default 1024 |
| method | COMBO | yes | How to resize. Area is best for shrinking, bicubic for enlarging. | one of: area, bicubic, bilinear, nearest |

Outputs: `IMAGE`

## How it was tested

The harness builds a starting set of inputs from the default of every input (first entry for lists, a small gradient picture for IMAGE and a mask with a filled box for MASK). It runs the node once like that, then changes one input at a time: every entry of every list, the lowest, highest and a middle value of every number, both settings of every on/off switch, and an empty text for every text box. Each run must give the right number of outputs, and pictures and masks must have sane dimensions and no broken (NaN) values. A plain-words refusal to an out-of-range number or empty text counts as REJECTED (expected). Any other error counts as FAIL. The node was run in a temporary folder.

## Cases

| # | Input changed | Result | Output / message |
|---|---|---|---|
| 1 | baseline (all defaults) | PASS | IMAGE=tensor[1, 1024, 1024, 3] |
| 2 | size = 8 (min) | PASS | IMAGE=tensor[1, 8, 8, 3] |
| 3 | size = 8192 (max) | PASS | IMAGE=tensor[1, 8192, 8192, 3] |
| 4 | size = 4096 (mid) | PASS | IMAGE=tensor[1, 4096, 4096, 3] |
| 5 | method = 'bicubic' | PASS | IMAGE=tensor[1, 1024, 1024, 3] |
| 6 | method = 'bilinear' | PASS | IMAGE=tensor[1, 1024, 1024, 3] |
| 7 | method = 'nearest' | PASS | IMAGE=tensor[1, 1024, 1024, 3] |

## Verdict

All 7 cases behaved as expected (7 passed, 0 rejected with a clear message).
