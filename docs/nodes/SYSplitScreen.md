# Split Screen SY (`SYSplitScreen`)

Source: `nodes/sy_split_screen.py`

**What it does:** Puts two pictures or clips together: side by side, stacked, or cut along a diagonal. Both are resized to the size of A first. A single picture can be mixed with a clip.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| images_a | IMAGE | yes | Shows on the left, top, or left of the diagonal. Sets the output size. | picture batch [B,H,W,3] |
| images_b | IMAGE | yes | Shows on the right, bottom, or right of the diagonal. | picture batch [B,H,W,3] |
| layout | COMBO | yes | How the two pictures are cut: left and right, top and bottom, or slanted. | one of: side by side, stacked, diagonal split |
| split | FLOAT | yes | Where the divider sits. 0.5 is the middle. | 0.05 to 0.95, step 0.01, default 0.5 |
| divider_width | INT | yes | Thickness of the divider line in pixels. 0 means no line. | 0 to 64, default 0 |
| divider_grey | FLOAT | yes | Brightness of the divider line. 0 is black, 1 is white. | 0.0 to 1.0, step 0.01, default 1.0 |
| fit | COMBO | yes | Crop to fill keeps the proportions. Stretch squeezes B to the size of A. | one of: crop to fill, stretch |
| when_uneven | COMBO | yes | If the clips differ in length: stop at the shorter or repeat the last frame. | one of: stop at shorter, repeat last |

Outputs: `IMAGE`

## How to use

1. Connect picture or clip A to **images_a** and B to **images_b**.
2. Pick the **layout** and move **split** to put the divider where you want it.
3. Set **divider_width** above 0 to draw a line, and **divider_grey** for its brightness.
4. Pick **fit**: crop to fill if B has other proportions than A.
5. A single picture on one side repeats over the whole clip on the other side.
