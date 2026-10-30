# Pixelate SY (`SYPixelate`)

Source: `nodes/sy_pixelate.py`

**What it does:** Makes a picture blocky, like big pixels. Each block becomes one colour.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| image | IMAGE | yes | The picture or batch of pictures to make blocky. | picture batch [B,H,W,3] |
| block_size | INT | yes | Width and height of each block in pixels. 1 changes nothing. | 1 to 512, default 8 |
| mode | COMBO | yes | Average uses the mean colour of the block. Nearest uses its top-left pixel. | one of: average, nearest |

Outputs: `IMAGE`
