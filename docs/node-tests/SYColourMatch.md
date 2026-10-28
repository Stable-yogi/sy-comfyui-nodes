# Colour Match SY (`SYColourMatch`)

Source: `nodes/sy_colour_match.py`

**What it does:** Makes a picture look like the colours of a reference picture. Good for keeping a series of pictures in one look.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| image | IMAGE | yes | The picture or batch of pictures to change. | picture batch [B,H,W,3] |
| reference | IMAGE | yes | The picture whose colours are copied. A batch is matched one to one, then repeats. | picture batch [B,H,W,3] |
| strength | FLOAT | yes | How far to move towards the reference. 0 changes nothing, 1 is a full match. | 0.0 to 1.0, step 0.01, default 1.0 |

Outputs: `IMAGE`

## How it was tested

The harness builds a starting set of inputs from the default of every input (first entry for lists, a small gradient picture for IMAGE and a mask with a filled box for MASK). It runs the node once like that, then changes one input at a time: every entry of every list, the lowest, highest and a middle value of every number, both settings of every on/off switch, and an empty text for every text box. Each run must give the right number of outputs, and pictures and masks must have sane dimensions and no broken (NaN) values. A plain-words refusal to an out-of-range number or empty text counts as REJECTED (expected). Any other error counts as FAIL. The node was run in a temporary folder.

## Cases

| # | Input changed | Result | Output / message |
|---|---|---|---|
| 1 | baseline (all defaults) | PASS | IMAGE=tensor[1, 64, 96, 3] |
| 2 | strength = 0.0 (min) | PASS | IMAGE=tensor[1, 64, 96, 3] |
| 3 | strength = 0.5 (mid) | PASS | IMAGE=tensor[1, 64, 96, 3] |

## Verdict

All 3 cases behaved as expected (3 passed, 0 rejected with a clear message).
