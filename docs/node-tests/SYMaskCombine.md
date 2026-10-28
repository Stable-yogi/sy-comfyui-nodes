# MaskCombine SY (`SYMaskCombine`)

Source: `nodes/sy_mask_combine.py`

**What it does:** Joins two masks: union (either), intersect (both), subtract (A without B) or xor (only one). B is resized to A.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| mask_a | MASK | yes | The first mask. Its size sets the result size. | mask [B,H,W] |
| mask_b | MASK | yes | The second mask. It is stretched to the size of mask A if needed. | mask [B,H,W] |
| operation | COMBO | yes | union = A or B, intersect = A and B, subtract = A minus B, xor = in one only. | one of: union, intersect, subtract, xor |

Outputs: `MASK`

## How it was tested

The harness builds a starting set of inputs from the default of every input (first entry for lists, a small gradient picture for IMAGE and a mask with a filled box for MASK). It runs the node once like that, then changes one input at a time: every entry of every list, the lowest, highest and a middle value of every number, both settings of every on/off switch, and an empty text for every text box. Each run must give the right number of outputs, and pictures and masks must have sane dimensions and no broken (NaN) values. A plain-words refusal to an out-of-range number or empty text counts as REJECTED (expected). Any other error counts as FAIL. The node was run in a temporary folder.

## Cases

| # | Input changed | Result | Output / message |
|---|---|---|---|
| 1 | baseline (all defaults) | PASS | MASK=tensor[1, 64, 96] |
| 2 | operation = 'intersect' | PASS | MASK=tensor[1, 64, 96] |
| 3 | operation = 'subtract' | PASS | MASK=tensor[1, 64, 96] |
| 4 | operation = 'xor' | PASS | MASK=tensor[1, 64, 96] |

## Verdict

All 4 cases behaved as expected (4 passed, 0 rejected with a clear message).
