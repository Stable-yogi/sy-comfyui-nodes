# Labelled AB Grid SY (`SYLabelledABGrid`)

Source: `nodes/sy_image_grid.py`

**What it does:** Puts two to four pictures in a strip with a caption under each. Good for comparing checkpoints on the same prompt. Pictures of other sizes can keep their shape instead of being stretched. The info line gives the strip size.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| image_a | IMAGE | yes | First picture. Its size sets the size of every cell. | picture batch [B,H,W,3] |
| image_b | IMAGE | yes | Second picture. It is resized to match the first. | picture batch [B,H,W,3] |
| label_a | STRING | yes | Caption under the first picture. Leave empty for none. | default 'A' |
| label_b | STRING | yes | Caption under the second picture. Leave empty for none. | default 'B' |
| direction | COMBO | yes | row puts pictures side by side, column stacks them. | one of: row, column |
| gap | INT | yes | Space in pixels between pictures and around the edge. | 0 to 256, default 8 |
| background | STRING | yes | Strip colour: a name like black or white, or six hex digits. | default 'black' |
| label_size | INT | yes | Caption text height in pixels. | 8 to 96, default 24 |
| image_c | IMAGE | no | Optional third picture. | picture batch [B,H,W,3] |
| image_d | IMAGE | no | Optional fourth picture. | picture batch [B,H,W,3] |
| label_c | STRING | no | Caption under the third picture. | default 'C' |
| label_d | STRING | no | Caption under the fourth picture. | default 'D' |
| fit | COMBO | no | If a picture has another size than the first: stretch it, or keep its shape inside the cell. | one of: stretch, keep shape |

Outputs: `IMAGE`, `STRING`

## How to use

1. Connect two to four pictures to image_a, image_b and optionally image_c and image_d. The first picture sets the cell size.
2. Type the captions in label_a to label_d. Leave one empty for no caption.
3. direction row puts the pictures side by side; column stacks them. Set gap, background and label_size. fit keeps the shape of pictures of other sizes.
4. One strip comes out, plus an info line with its size. It suits comparing checkpoints on the same prompt.
