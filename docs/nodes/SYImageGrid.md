# Image Grid SY (`SYImageGrid`)

Source: `nodes/sy_image_grid.py`

**What it does:** Lays a batch of pictures out as one contact sheet. Optional captions, one per line, go under each picture, or number them automatically. Pictures of other sizes can keep their shape. The info line gives the sheet size.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| images | IMAGE | yes | The batch of pictures to put on the sheet. All are sized like the first one. | picture batch [B,H,W,3] |
| columns | INT | yes | How many pictures per row. Fewer pictures than columns gives a single row. | 1 to 64, default 4 |
| gap | INT | yes | Space in pixels between pictures and around the edge. | 0 to 256, default 8 |
| background | STRING | yes | Sheet colour: black, white, gray, dark_gray, red, green, blue, gold or six hex digits. | default 'black' |
| labels | STRING | no | One caption per line, in picture order. Leave empty for no captions. | default '', multiline |
| label_size | INT | no | Caption text height in pixels. | 8 to 96, default 20 |
| fit | COMBO | no | If a picture has another size than the first: stretch it, or keep its shape inside the cell. | one of: stretch, keep shape |
| auto_number | BOOLEAN | no | On: when the labels box is empty, caption the pictures 1, 2, 3 ... | default False |

Outputs: `IMAGE`, `STRING`
