# Pad Image SY (`SYPadImage`)

Source: `nodes/sy_pad_image.py`

**What it does:** Adds space around a picture. Also gives a mask that is white on the new space, ready for outpainting. Can round the new size up to a multiple of 8 or 64, and the info output tells the old and new size.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| image | IMAGE | yes | The picture or batch of pictures to add space around. | picture batch [B,H,W,3] |
| left | INT | yes | Pixels to add on the left. | 0 to 8192, default 0 |
| right | INT | yes | Pixels to add on the right. | 0 to 8192, default 0 |
| top | INT | yes | Pixels to add on the top. | 0 to 8192, default 0 |
| bottom | INT | yes | Pixels to add at the bottom. | 0 to 8192, default 0 |
| color | COMBO | yes | Colour that fills the new space. | one of: black, white, grey, red, green, blue |
| custom_color | STRING | no | Optional own colour as red,green,blue numbers 0 to 255, for example 200,120,40. Empty uses the list. | default '' |
| multiple_of | INT | no | Round the new width and height up to a multiple of this, for example 8. Extra goes right and bottom. | 1 to 512, step 1, default 1 |

Outputs: `IMAGE`, `MASK`, `INT`, `INT`, `STRING`

## How to use

1. Connect your picture to image.
2. Set left, right, top and bottom in pixels and pick the fill color (or type your own as red,green,blue in custom_color).
3. Optional: multiple_of rounds the new size up (extra goes right and bottom).
Outputs: the padded picture, a mask that is white on the new space (ready for outpainting), width, height and an info line with the old and new size.
