# Outpaint Pad SY (`SYOutpaintPad`)

Source: `nodes/sy_outpaint_pad.py`

**What it does:** One box for outpainting. Adds margins to a picture (or pads it to a shape like 16:9), fills the new area so the model has something to continue from (edge stretch, mirror, blur, grey, black), and makes the matching mask with a soft seam that reaches into the picture. Gives the box of the original so you can paste it back. Replaces chaining pad, fill, mask grow and feather nodes. Pad Image SY only pads with one colour.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| image | IMAGE | yes | The picture or batch of pictures to extend. | picture batch [B,H,W,3] |
| left | INT | yes | Pixels to add on the left. Example: 256 | 0 to 8192, default 0 |
| top | INT | yes | Pixels to add on the top. Example: 0 | 0 to 8192, default 0 |
| right | INT | yes | Pixels to add on the right. Example: 256 | 0 to 8192, default 0 |
| bottom | INT | yes | Pixels to add at the bottom. Example: 0 | 0 to 8192, default 0 |
| to_aspect | COMBO | no | Pad to this shape, picture centred. Replaces the four numbers. Example: 16:9 | one of: off, 1:1, 4:3, 3:2, 16:9, 9:16, 21:9 |
| multiple | INT | no | Round the new size up to a multiple of this (added right and bottom). Example: 8 | 1 to 512, default 8 |
| fill | COMBO | no | What the new area holds before painting. Example: blur of picture | one of: edge stretch, mirror, blur of picture, grey, black |
| seam_feather | INT | no | Soft mask edge, this many pixels INTO the picture. Example: 32 | 0 to 256, default 0 |
| mask_grow | INT | no | Hard mask pixels into the picture before the soft part. Example: 8 | 0 to 256, default 0 |

Outputs: `IMAGE`, `MASK`, `STRING`, `STRING`
