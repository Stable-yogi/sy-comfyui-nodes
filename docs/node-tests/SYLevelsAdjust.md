# Levels Adjust SY (`SYLevelsAdjust`)

Source: `nodes/sy_levels_adjust.py`

**What it does:** Brightness, contrast, saturation and gamma in one node. Default values change nothing.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| image | IMAGE | yes | The picture or batch of pictures to adjust. | picture batch [B,H,W,3] |
| brightness | FLOAT | yes | Adds light. Below 0 darkens, above 0 brightens. | -1.0 to 1.0, step 0.01, default 0.0 |
| contrast | FLOAT | yes | Spread between dark and light. 1 is unchanged, 0 is flat grey. | 0.0 to 3.0, step 0.01, default 1.0 |
| saturation | FLOAT | yes | Colour strength. 1 is unchanged, 0 is black and white. | 0.0 to 3.0, step 0.01, default 1.0 |
| gamma | FLOAT | yes | Middle tones. Above 1 brightens the shadows, below 1 darkens them. | 0.1 to 5.0, step 0.01, default 1.0 |

Outputs: `IMAGE`

## How it was tested

The harness builds a starting set of inputs from the default of every input (first entry for lists, a small gradient picture for IMAGE and a mask with a filled box for MASK). It runs the node once like that, then changes one input at a time: every entry of every list, the lowest, highest and a middle value of every number, both settings of every on/off switch, and an empty text for every text box. Each run must give the right number of outputs, and pictures and masks must have sane dimensions and no broken (NaN) values. A plain-words refusal to an out-of-range number or empty text counts as REJECTED (expected). Any other error counts as FAIL. The node was run in a temporary folder.

## Cases

| # | Input changed | Result | Output / message |
|---|---|---|---|
| 1 | baseline (all defaults) | PASS | IMAGE=tensor[1, 64, 96, 3] |
| 2 | brightness = -1.0 (min) | PASS | IMAGE=tensor[1, 64, 96, 3] |
| 3 | brightness = 1.0 (max) | PASS | IMAGE=tensor[1, 64, 96, 3] |
| 4 | contrast = 0.0 (min) | PASS | IMAGE=tensor[1, 64, 96, 3] |
| 5 | contrast = 3.0 (max) | PASS | IMAGE=tensor[1, 64, 96, 3] |
| 6 | contrast = 1.5 (mid) | PASS | IMAGE=tensor[1, 64, 96, 3] |
| 7 | saturation = 0.0 (min) | PASS | IMAGE=tensor[1, 64, 96, 3] |
| 8 | saturation = 3.0 (max) | PASS | IMAGE=tensor[1, 64, 96, 3] |
| 9 | saturation = 1.5 (mid) | PASS | IMAGE=tensor[1, 64, 96, 3] |
| 10 | gamma = 0.1 (min) | PASS | IMAGE=tensor[1, 64, 96, 3] |
| 11 | gamma = 5.0 (max) | PASS | IMAGE=tensor[1, 64, 96, 3] |
| 12 | gamma = 2.55 (mid) | PASS | IMAGE=tensor[1, 64, 96, 3] |

## Verdict

All 12 cases behaved as expected (12 passed, 0 rejected with a clear message).
