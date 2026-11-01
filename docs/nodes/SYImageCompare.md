# Image Compare SY (`SYImageCompare`)

Source: `nodes/sy_image_compare.py`

**What it does:** Compares two pictures: side by side, difference, blend, checker or wipe. B is resized to match A. The info line says if the pictures are identical, or how much they differ, and warns if B had to be reshaped.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| image_a | IMAGE | yes | The first picture. Its size sets the result size. | picture batch [B,H,W,3] |
| image_b | IMAGE | yes | The second picture. It is resized to fit the first if needed. | picture batch [B,H,W,3] |
| mode | COMBO | yes | How to put the two pictures together. | one of: side_by_side, difference, blend, checker, wipe |
| amount | FLOAT | yes | Blend mix, or wipe position. 0 shows A, 1 shows B. | 0.0 to 1.0, step 0.01, default 0.5 |
| resize_b | COMBO | no | How B is resized when its size differs: nearest keeps hard pixels, smooth looks cleaner. | one of: nearest, smooth |

Outputs: `IMAGE`, `STRING`
