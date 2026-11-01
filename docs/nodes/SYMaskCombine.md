# MaskCombine SY (`SYMaskCombine`)

Source: `nodes/sy_mask_combine.py`

**What it does:** Joins two masks: union (either), intersect (both), subtract (A without B) or xor (only one). B is resized to A. Can also grow or shrink, then feather, then invert the result in the right order. The info line warns about empty masks and size mismatches.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| mask_a | MASK | yes | The first mask. Its size sets the result size. | mask [B,H,W] |
| mask_b | MASK | yes | The second mask. It is stretched to the size of mask A if needed. | mask [B,H,W] |
| operation | COMBO | yes | union = A or B, intersect = A and B, subtract = A minus B, xor = in one only. | one of: union, intersect, subtract, xor |
| grow | INT | no | After combining: grow the white area by this many pixels (negative shrinks). 0 is off. | -512 to 512, step 1, default 0 |
| feather | INT | no | After growing: soften the edge by this many pixels. 0 is off. | 0 to 512, step 1, default 0 |
| invert_result | BOOLEAN | no | Swap white and black in the finished mask. | default False |

Outputs: `MASK`, `STRING`

## How to use

1. Connect two masks to mask_a and mask_b. Mask B is stretched to the size of mask A.
2. Choose the operation: union (either), intersect (both), subtract (A without B) or xor (only one of them).
3. Optional: grow the result (negative shrinks), then feather it, then turn invert_result on. They run in that order.
The info output warns about empty masks and size differences.
