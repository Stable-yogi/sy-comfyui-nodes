# Flip Rotate SY (`SYFlipRotate`)

Source: `nodes/sy_flip_rotate.py`

**What it does:** Mirrors a picture and turns it in steps of 90 degrees. The mirror is done first, then the turn.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| image | IMAGE | yes | The picture or batch of pictures to flip or turn. | picture batch [B,H,W,3] |
| flip_horizontal | BOOLEAN | yes | Mirror left to right. | default False |
| flip_vertical | BOOLEAN | yes | Mirror top to bottom. | default False |
| rotate | COMBO | yes | Turn the picture clockwise by this much after any flip. | one of: none, 90 clockwise, 180, 270 clockwise |

Outputs: `IMAGE`
