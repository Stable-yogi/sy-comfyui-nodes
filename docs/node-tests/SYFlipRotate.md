# Flip Rotate SY (`SYFlipRotate`)

Source: `nodes/sy_flip_rotate.py`

**What it does:** Mirrors a picture and turns it in steps of 90 degrees. The mirror is done first, then the turn.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| image | IMAGE | yes | The picture or batch of pictures to flip or turn. | picture batch [B,H,W,3] |
| flip_horizontal | BOOLEAN | yes | Mirror left to right. | default False |
| flip_vertical | BOOLEAN | yes | Mirror top to bottom. | default False |
| rotate | COMBO | yes | Turn the picture clockwise by this much after any flip. | one of: none, 90 clockwise, 180, 270 clockwise |

Outputs: `IMAGE`

## How it was tested

The harness builds a starting set of inputs from the default of every input (first entry for lists, a small gradient picture for IMAGE and a mask with a filled box for MASK). It runs the node once like that, then changes one input at a time: every entry of every list, the lowest, highest and a middle value of every number, both settings of every on/off switch, and an empty text for every text box. Each run must give the right number of outputs, and pictures and masks must have sane dimensions and no broken (NaN) values. A plain-words refusal to an out-of-range number or empty text counts as REJECTED (expected). Any other error counts as FAIL. The node was run in a temporary folder.

## Cases

| # | Input changed | Result | Output / message |
|---|---|---|---|
| 1 | baseline (all defaults) | PASS | IMAGE=tensor[1, 64, 96, 3] |
| 2 | flip_horizontal = True | PASS | IMAGE=tensor[1, 64, 96, 3] |
| 3 | flip_vertical = True | PASS | IMAGE=tensor[1, 64, 96, 3] |
| 4 | rotate = '90 clockwise' | PASS | IMAGE=tensor[1, 96, 64, 3] |
| 5 | rotate = '180' | PASS | IMAGE=tensor[1, 64, 96, 3] |
| 6 | rotate = '270 clockwise' | PASS | IMAGE=tensor[1, 96, 64, 3] |

## Verdict

All 6 cases behaved as expected (6 passed, 0 rejected with a clear message).
