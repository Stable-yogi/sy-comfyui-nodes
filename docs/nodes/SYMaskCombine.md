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
