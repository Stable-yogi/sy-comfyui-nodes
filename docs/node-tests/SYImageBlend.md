# Image Blend SY (`SYImageBlend`)

Source: `nodes/sy_image_blend.py`

**What it does:** Lays one picture over another. Pick a blend mode and how strong the top picture is. A smaller top picture is stretched to fit.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| base | IMAGE | yes | The bottom picture. The result has its size. | picture batch [B,H,W,3] |
| top | IMAGE | yes | The picture laid over the base. It is resized to the base size when needed. | picture batch [B,H,W,3] |
| mode | COMBO | yes | How the two pictures mix. Normal just shows the top picture. | one of: normal, multiply, screen, overlay, add, difference |
| opacity | FLOAT | yes | How strong the top picture is. 0 shows only the base, 1 the full mix. | 0.0 to 1.0, step 0.01, default 0.5 |

Outputs: `IMAGE`

## How it was tested

The harness builds a starting set of inputs from the default of every input (first entry for lists, a small gradient picture for IMAGE and a mask with a filled box for MASK). It runs the node once like that, then changes one input at a time: every entry of every list, the lowest, highest and a middle value of every number, both settings of every on/off switch, and an empty text for every text box. Each run must give the right number of outputs, and pictures and masks must have sane dimensions and no broken (NaN) values. A plain-words refusal to an out-of-range number or empty text counts as REJECTED (expected). Any other error counts as FAIL. The node was run in a temporary folder.

## Cases

| # | Input changed | Result | Output / message |
|---|---|---|---|
| 1 | baseline (all defaults) | PASS | IMAGE=tensor[1, 64, 96, 3] |
| 2 | mode = 'multiply' | PASS | IMAGE=tensor[1, 64, 96, 3] |
| 3 | mode = 'screen' | PASS | IMAGE=tensor[1, 64, 96, 3] |
| 4 | mode = 'overlay' | PASS | IMAGE=tensor[1, 64, 96, 3] |
| 5 | mode = 'add' | PASS | IMAGE=tensor[1, 64, 96, 3] |
| 6 | mode = 'difference' | PASS | IMAGE=tensor[1, 64, 96, 3] |
| 7 | opacity = 0.0 (min) | PASS | IMAGE=tensor[1, 64, 96, 3] |
| 8 | opacity = 1.0 (max) | PASS | IMAGE=tensor[1, 64, 96, 3] |

## Verdict

All 8 cases behaved as expected (8 passed, 0 rejected with a clear message).
