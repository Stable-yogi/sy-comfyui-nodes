# Perspective Warp SY (`SYPerspectiveWarp`)

Source: `nodes/sy_perspective_warp.py`

**What it does:** Pulls the four corners of the picture to new places. Use it to straighten a slanted photo or to tilt a card. Corners must keep their order: top-left, top-right, bottom-right, bottom-left.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| image | IMAGE | yes | The picture or pictures to warp. | picture batch [B,H,W,3] |
| tl_x | FLOAT | yes | top-left x, 0 is the left edge, 1 the right edge. | -0.5 to 1.5, step 0.005, default 0.0 |
| tl_y | FLOAT | yes | top-left y, 0 is the top edge, 1 the bottom edge. | -0.5 to 1.5, step 0.005, default 0.0 |
| tr_x | FLOAT | yes | top-right x, 0 is the left edge, 1 the right edge. | -0.5 to 1.5, step 0.005, default 1.0 |
| tr_y | FLOAT | yes | top-right y, 0 is the top edge, 1 the bottom edge. | -0.5 to 1.5, step 0.005, default 0.0 |
| br_x | FLOAT | yes | bottom-right x, 0 is the left edge, 1 the right edge. | -0.5 to 1.5, step 0.005, default 1.0 |
| br_y | FLOAT | yes | bottom-right y, 0 is the top edge, 1 the bottom edge. | -0.5 to 1.5, step 0.005, default 1.0 |
| bl_x | FLOAT | yes | bottom-left x, 0 is the left edge, 1 the right edge. | -0.5 to 1.5, step 0.005, default 0.0 |
| bl_y | FLOAT | yes | bottom-left y, 0 is the top edge, 1 the bottom edge. | -0.5 to 1.5, step 0.005, default 1.0 |
| edge | COMBO | yes | What fills the places the warped picture does not cover. | one of: black, stretch, mirror |
| keep_size | BOOLEAN | yes | On: result has the original size. Off: result is cropped to the new shape. | default True |

Outputs: `IMAGE`

## How to use

1. Connect a picture or batch to **image**.
2. Move each corner to where it should end up. The plain corners (0,0 / 1,0 / 1,1 / 0,1) return the picture unchanged.
3. Keep the corners in order and keep the shape four-sided; a flipped or flat shape is refused with a message.
4. Choose **edge** for the empty areas, and turn **keep_size** off to crop the result to the new shape.
