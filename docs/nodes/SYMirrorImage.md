# Mirror Image SY (`SYMirrorImage`)

Source: `nodes/sy_mirror_image.py`

**What it does:** Copies one half of a picture, flipped, onto the other half so it becomes symmetric. Four way mirrors one quarter.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| image | IMAGE | yes | The picture or batch of pictures to mirror. | picture batch [B,H,W,3] |
| mode | COMBO | yes | Which side is kept and copied over the other. four_way copies the top-left quarter. | one of: left_to_right, right_to_left, top_to_bottom, bottom_to_top, four_way |

Outputs: `IMAGE`
