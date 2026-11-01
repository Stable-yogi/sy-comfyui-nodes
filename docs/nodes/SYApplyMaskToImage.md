# ApplyMaskToImage SY (`SYApplyMaskToImage`)

Source: `nodes/sy_apply_mask_to_image.py`

**What it does:** Hides the part of a picture outside the mask. The hidden part becomes see-through (alpha), black or gray. A soft edge (feather) avoids hard cut-out lines. A mask of another size or batch is fitted for you.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| image | IMAGE | yes | The picture to cut out. | picture batch [B,H,W,3] |
| mask | MASK | yes | The mask. It is stretched to the picture size if needed. | mask [B,H,W] |
| fill | COMBO | yes | What the hidden part becomes: see-through (adds an alpha channel), black or gray. | one of: alpha, black, gray |
| keep | COMBO | yes | masked keeps the white part of the mask, outside keeps the black part. | one of: masked, outside |
| feather | INT | no | Softens the mask edge by this many pixels so the cut-out has no hard line. 0 = off. | 0 to 512, step 1, default 0 |

Outputs: `IMAGE`, `STRING`

## How to use

1. Connect the picture to image and the mask to mask.
2. Choose keep: masked keeps the white part, outside keeps the black part.
3. Choose fill: alpha makes the rest see-through, black or gray paints it.
4. Raise feather to soften the cut-out edge. The cut-out picture comes out as image, with an info line.
