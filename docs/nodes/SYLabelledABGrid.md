# Labelled AB Grid SY (`SYLabelledABGrid`)

Source: `nodes/sy_image_grid.py`

**What it does:** Puts two to four pictures in a strip with a caption under each. Good for comparing checkpoints on the same prompt.

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

Outputs: `IMAGE`
