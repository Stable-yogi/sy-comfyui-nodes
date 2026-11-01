# Before After SY (`SYBeforeAfter`)

Source: `nodes/sy_before_after.py`

**What it does:** Makes one comparison picture from a before and an after picture: split (line you place), side by side, top and bottom, difference, checkerboard or blend. Small before/after labels. The info line gives the mean difference.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| before | IMAGE | yes | The picture before the change. | picture batch [B,H,W,3] |
| after | IMAGE | yes | The picture after the change. | picture batch [B,H,W,3] |
| mode | COMBO | no | How the two pictures are put together. | one of: split vertical, split horizontal, side by side, top and bottom, difference, checkerboard, blend |
| position | FLOAT | no | Where the split is (0 to 1). In blend: how much of after is mixed in. | 0.0 to 1.0, step 0.01, default 0.5 |
| line_width | INT | no | Width of the dividing line in pixels. 0 means no line. | 0 to 20, default 2 |
| line_colour | COMBO | no | Colour of the dividing line. | one of: white, black, red, green, blue, yellow |
| labels | BOOLEAN | no | Draw small before / after text. Only in the split, side by side and top and bottom modes. | default True |
| match_size | COMBO | no | What to do when the two pictures differ in size. | one of: resize after to before, resize both to the smaller, refuse on mismatch |
| difference_gain | FLOAT | no | Makes small differences brighter in difference mode. | 1.0 to 20.0, step 0.5, default 4.0 |
| batch_mode | COMBO | no | Use only the first picture of each batch, or compare every picture. | one of: first picture only, all pictures |

Outputs: `IMAGE`, `STRING`
