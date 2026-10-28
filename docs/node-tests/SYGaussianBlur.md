# Gaussian Blur SY (`SYGaussianBlur`)

Source: `nodes/sy_gaussian_blur.py`

**What it does:** Blurs a picture softly. A bigger radius gives a stronger blur. Radius 0 leaves the picture as it is.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| image | IMAGE | yes | The picture or batch of pictures to blur. | picture batch [B,H,W,3] |
| radius | FLOAT | yes | How far the blur reaches, in pixels. 0 does nothing. | 0.0 to 64.0, step 0.1, default 4.0 |

Outputs: `IMAGE`

## How it was tested

The harness builds a starting set of inputs from the default of every input (first entry for lists, a small gradient picture for IMAGE and a mask with a filled box for MASK). It runs the node once like that, then changes one input at a time: every entry of every list, the lowest, highest and a middle value of every number, both settings of every on/off switch, and an empty text for every text box. Each run must give the right number of outputs, and pictures and masks must have sane dimensions and no broken (NaN) values. A plain-words refusal to an out-of-range number or empty text counts as REJECTED (expected). Any other error counts as FAIL. The node was run in a temporary folder.

## Cases

| # | Input changed | Result | Output / message |
|---|---|---|---|
| 1 | baseline (all defaults) | PASS | IMAGE=tensor[1, 64, 96, 3] |
| 2 | radius = 0.0 (min) | PASS | IMAGE=tensor[1, 64, 96, 3] |
| 3 | radius = 64.0 (max) | PASS | IMAGE=tensor[1, 64, 96, 3] |
| 4 | radius = 32.0 (mid) | PASS | IMAGE=tensor[1, 64, 96, 3] |

## Verdict

All 4 cases behaved as expected (4 passed, 0 rejected with a clear message).
