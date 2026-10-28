# Sharpen SY (`SYSharpen`)

Source: `nodes/sy_sharpen.py`

**What it does:** Makes a picture crisper with an unsharp mask. Radius sets how wide the edges are, amount sets how strong.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| image | IMAGE | yes | The picture or batch of pictures to sharpen. | picture batch [B,H,W,3] |
| radius | FLOAT | yes | Width of the edges to sharpen, in pixels. Small is fine detail. | 0.1 to 32.0, step 0.1, default 1.0 |
| amount | FLOAT | yes | How strong the sharpening is. 0 changes nothing, above 2 is harsh. | 0.0 to 5.0, step 0.05, default 1.0 |

Outputs: `IMAGE`

## How it was tested

The harness builds a starting set of inputs from the default of every input (first entry for lists, a small gradient picture for IMAGE and a mask with a filled box for MASK). It runs the node once like that, then changes one input at a time: every entry of every list, the lowest, highest and a middle value of every number, both settings of every on/off switch, and an empty text for every text box. Each run must give the right number of outputs, and pictures and masks must have sane dimensions and no broken (NaN) values. A plain-words refusal to an out-of-range number or empty text counts as REJECTED (expected). Any other error counts as FAIL. The node was run in a temporary folder.

## Cases

| # | Input changed | Result | Output / message |
|---|---|---|---|
| 1 | baseline (all defaults) | PASS | IMAGE=tensor[1, 64, 96, 3] |
| 2 | radius = 0.1 (min) | PASS | IMAGE=tensor[1, 64, 96, 3] |
| 3 | radius = 32.0 (max) | PASS | IMAGE=tensor[1, 64, 96, 3] |
| 4 | radius = 16.05 (mid) | PASS | IMAGE=tensor[1, 64, 96, 3] |
| 5 | amount = 0.0 (min) | PASS | IMAGE=tensor[1, 64, 96, 3] |
| 6 | amount = 5.0 (max) | PASS | IMAGE=tensor[1, 64, 96, 3] |
| 7 | amount = 2.5 (mid) | PASS | IMAGE=tensor[1, 64, 96, 3] |

## Verdict

All 7 cases behaved as expected (7 passed, 0 rejected with a clear message).
