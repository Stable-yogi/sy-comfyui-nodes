# MaskGrowShrink SY (`SYMaskGrowShrink`)

Source: `nodes/sy_mask_grow_shrink.py`

**What it does:** Makes the white area of a mask bigger (positive pixels) or smaller (negative pixels).

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| mask | MASK | yes | The mask to change. | mask [B,H,W] |
| pixels | INT | yes | Positive grows the white area, negative shrinks it. | -512 to 512, step 1, default 8 |
| shape | COMBO | yes | Round keeps corners smooth. Square grows corners out. | one of: round, square |

Outputs: `MASK`

## How it was tested

The harness builds a starting set of inputs from the default of every input (first entry for lists, a small gradient picture for IMAGE and a mask with a filled box for MASK). It runs the node once like that, then changes one input at a time: every entry of every list, the lowest, highest and a middle value of every number, both settings of every on/off switch, and an empty text for every text box. Each run must give the right number of outputs, and pictures and masks must have sane dimensions and no broken (NaN) values. A plain-words refusal to an out-of-range number or empty text counts as REJECTED (expected). Any other error counts as FAIL. The node was run in a temporary folder.

## Cases

| # | Input changed | Result | Output / message |
|---|---|---|---|
| 1 | baseline (all defaults) | PASS | MASK=tensor[1, 64, 96] |
| 2 | pixels = -512 (min) | PASS | MASK=tensor[1, 64, 96] |
| 3 | pixels = 512 (max) | PASS | MASK=tensor[1, 64, 96] |
| 4 | pixels = 0 (mid) | PASS | MASK=tensor[1, 64, 96] |
| 5 | shape = 'square' | PASS | MASK=tensor[1, 64, 96] |

## Verdict

All 5 cases behaved as expected (5 passed, 0 rejected with a clear message).
