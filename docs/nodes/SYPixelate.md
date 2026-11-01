# Pixelate SY (`SYPixelate`)

Source: `nodes/sy_pixelate.py`

**What it does:** Makes a picture blocky, like big pixels. Each block becomes one colour. Set blocks_across to say how many blocks you want across the picture instead of a pixel size. The info output counts the blocks.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| image | IMAGE | yes | The picture or batch of pictures to make blocky. | picture batch [B,H,W,3] |
| block_size | INT | yes | Width and height of each block in pixels. 1 changes nothing. | 1 to 512, default 8 |
| mode | COMBO | yes | Average uses the mean colour of the block. Nearest uses its top-left pixel. | one of: average, nearest |
| blocks_across | INT | no | Wanted number of blocks across the width, for example 64. 0 uses block_size instead. | 0 to 4096, step 1, default 0 |

Outputs: `IMAGE`, `STRING`

## How to use

1. Connect your picture to image.
2. Set block_size (pixels per block, 1 changes nothing) or set blocks_across to say how many blocks you want across the picture. 0 uses block_size.
3. Choose mode: average uses the mean colour of a block, nearest uses its top-left pixel.
The info output counts the blocks.
