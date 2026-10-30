# ApplyMaskToImage SY (`SYApplyMaskToImage`)

Source: `nodes/sy_apply_mask_to_image.py`

**What it does:** Hides the part of a picture outside the mask. The hidden part becomes see-through (alpha), black or gray.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| image | IMAGE | yes | The picture to cut out. | picture batch [B,H,W,3] |
| mask | MASK | yes | The mask. It is stretched to the picture size if needed. | mask [B,H,W] |
| fill | COMBO | yes | What the hidden part becomes: see-through (adds an alpha channel), black or gray. | one of: alpha, black, gray |
| keep | COMBO | yes | masked keeps the white part of the mask, outside keeps the black part. | one of: masked, outside |

Outputs: `IMAGE`
