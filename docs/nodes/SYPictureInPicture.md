# Picture In Picture SY (`SYPictureInPicture`)

Source: `nodes/sy_picture_in_picture.py`

**What it does:** Puts a small copy of one picture or clip inside another, with an optional border, rounded corners and see-through. The output has the size of the base. It refuses a placement that would hang outside the picture.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| images_base | IMAGE | yes | The big picture or clip that stays in the background. | picture batch [B,H,W,3] |
| images_inset | IMAGE | yes | The small picture or clip that is placed on top. | picture batch [B,H,W,3] |
| position | COMBO | yes | Which corner the small picture sits in, or the centre. | one of: top-left, top-right, bottom-left, bottom-right, centre |
| size | FLOAT | yes | Width of the small picture as a fraction of the base width. | 0.05 to 0.9, step 0.01, default 0.3 |
| margin | INT | yes | Gap in pixels between the small picture and the edge. | 0 to 500, default 24 |
| border | INT | yes | Thickness of the frame around the small picture, in pixels. | 0 to 64, default 4 |
| border_grey | FLOAT | yes | Brightness of the frame. 0 is black, 1 is white. | 0.0 to 1.0, step 0.01, default 1.0 |
| corner_radius | INT | yes | How round the corners are, in pixels. 0 is square. | 0 to 200, default 0 |
| opacity | FLOAT | yes | 1 hides the base behind the small picture, lower lets it show through. | 0.0 to 1.0, step 0.01, default 1.0 |
| when_uneven | COMBO | yes | If the clips differ in length: stop at the shorter or repeat the last frame. | one of: stop at shorter, repeat last |

Outputs: `IMAGE`

## How to use

1. Connect the big picture to **images_base** and the small one to **images_inset**.
2. Pick **position**, then set **size** and **margin**. If the small picture plus margin does not fit, the node tells you to lower them.
3. Add a frame with **border** and **border_grey**, and round the corners with **corner_radius**.
4. Lower **opacity** to let the base show through.
5. A single picture on one side repeats over the whole clip on the other side.
