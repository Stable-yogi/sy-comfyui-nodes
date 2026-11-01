# Roll Image SY (`SYRollImage`)

Source: `nodes/sy_roll_image.py`

**What it does:** Slides a picture and wraps whatever leaves one edge back in on the opposite edge. Handy for checking seamless textures: switch on half_offset to push the seams into the middle. The info output tells the real move.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| image | IMAGE | yes | The picture or batch of pictures to slide. | picture batch [B,H,W,3] |
| shift_x | INT | yes | Sideways move. Positive moves the picture to the right. | -8192 to 8192, step 1, default 0 |
| shift_y | INT | yes | Up and down move. Positive moves the picture down. | -8192 to 8192, step 1, default 0 |
| unit | COMBO | yes | pixels moves by that many pixels; percent moves by a share of the width and height. | one of: pixels, percent |
| half_offset | BOOLEAN | no | On: also move by half the width and height, to show the seams of a tileable texture in the middle. | default False |

Outputs: `IMAGE`, `STRING`
