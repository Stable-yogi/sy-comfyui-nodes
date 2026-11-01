# Mirror Image SY (`SYMirrorImage`)

Source: `nodes/sy_mirror_image.py`

**What it does:** Copies one half of a picture, flipped, onto the other half so it becomes symmetric. Four way mirrors one quarter. The info output says which side was copied and what happens with an odd-sized picture.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| image | IMAGE | yes | The picture or batch of pictures to mirror. | picture batch [B,H,W,3] |
| mode | COMBO | yes | Which side is kept and copied over the other. four_way copies the top-left quarter. | one of: left_to_right, right_to_left, top_to_bottom, bottom_to_top, four_way |

Outputs: `IMAGE`, `STRING`

## How to use

1. Connect your picture to image.
2. Choose mode. It names the side that is kept and copied, flipped, onto the other side: left_to_right, right_to_left, top_to_bottom, bottom_to_top or four_way.
3. four_way copies the top-left quarter to all four corners.
The info output says which side was copied and what happens with an odd-sized picture.
