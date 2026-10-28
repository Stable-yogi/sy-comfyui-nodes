# Vignette SY (`SYVignette`)

Source: `nodes/sy_vignette.py`

**What it does:** Darkens the edges and corners of a picture. Strength sets how dark, softness sets how far in the fade reaches.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| image | IMAGE | yes | The picture or batch of pictures to darken at the edges. | picture batch [B,H,W,3] |
| strength | FLOAT | yes | How dark the corners get. 0 changes nothing, 1 is black. | 0.0 to 1.0, step 0.01, default 0.5 |
| softness | FLOAT | yes | How wide the fade is. Small is a tight dark rim, 1 fades from the centre. | 0.05 to 1.0, step 0.01, default 0.5 |

Outputs: `IMAGE`

## How it was tested

The harness builds a starting set of inputs from the default of every input (first entry for lists, a small gradient picture for IMAGE and a mask with a filled box for MASK). It runs the node once like that, then changes one input at a time: every entry of every list, the lowest, highest and a middle value of every number, both settings of every on/off switch, and an empty text for every text box. Each run must give the right number of outputs, and pictures and masks must have sane dimensions and no broken (NaN) values. A plain-words refusal to an out-of-range number or empty text counts as REJECTED (expected). Any other error counts as FAIL. The node was run in a temporary folder.

## Cases

| # | Input changed | Result | Output / message |
|---|---|---|---|
| 1 | baseline (all defaults) | PASS | IMAGE=tensor[1, 64, 96, 3] |
| 2 | strength = 0.0 (min) | PASS | IMAGE=tensor[1, 64, 96, 3] |
| 3 | strength = 1.0 (max) | PASS | IMAGE=tensor[1, 64, 96, 3] |
| 4 | softness = 0.05 (min) | PASS | IMAGE=tensor[1, 64, 96, 3] |
| 5 | softness = 1.0 (max) | PASS | IMAGE=tensor[1, 64, 96, 3] |
| 6 | softness = 0.525 (mid) | PASS | IMAGE=tensor[1, 64, 96, 3] |

## Verdict

All 6 cases behaved as expected (6 passed, 0 rejected with a clear message).
