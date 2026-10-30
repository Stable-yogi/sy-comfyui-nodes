# Pad Image SY (`SYPadImage`)

Source: `nodes/sy_pad_image.py`

**What it does:** Adds space around a picture. Also gives a mask that is white on the new space, ready for outpainting.

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

Outputs: `IMAGE`, `MASK`, `INT`, `INT`
