# MaskFeather SY (`SYMaskFeather`)

Source: `nodes/sy_mask_feather.py`

**What it does:** Softens the edge of a mask with a smooth blur so it blends in. Radius 0 changes nothing.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| mask | MASK | yes | The mask to soften. | mask [B,H,W] |
| radius | INT | yes | How many pixels wide the soft edge is. 0 keeps the mask as it is. | 0 to 512, step 1, default 16 |

Outputs: `MASK`

## How it was tested

The harness builds a starting set of inputs from the default of every input (first entry for lists, a small gradient picture for IMAGE and a mask with a filled box for MASK). It runs the node once like that, then changes one input at a time: every entry of every list, the lowest, highest and a middle value of every number, both settings of every on/off switch, and an empty text for every text box. Each run must give the right number of outputs, and pictures and masks must have sane dimensions and no broken (NaN) values. A plain-words refusal to an out-of-range number or empty text counts as REJECTED (expected). Any other error counts as FAIL. The node was run in a temporary folder.

## Cases

| # | Input changed | Result | Output / message |
|---|---|---|---|
| 1 | baseline (all defaults) | PASS | MASK=tensor[1, 64, 96] |
| 2 | radius = 0 (min) | PASS | MASK=tensor[1, 64, 96] |
| 3 | radius = 512 (max) | PASS | MASK=tensor[1, 64, 96] |
| 4 | radius = 256 (mid) | PASS | MASK=tensor[1, 64, 96] |

## Verdict

All 4 cases behaved as expected (4 passed, 0 rejected with a clear message).
