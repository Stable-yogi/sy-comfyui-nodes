# Tile Split SY (`SYTileSplit`)

Source: `nodes/sy_tiles.py`

**What it does:** Cuts one big picture into equal tiles that overlap a little. Process the tiles, then join them with Tile Merge SY. Also gives the tile count and a plain info sentence (grid size, tile size, and a warning when the picture is smaller than one tile).

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| image | IMAGE | yes | The picture to cut. A batch: only the first picture is used, unless batch_mode says all. | picture batch [B,H,W,3] |
| tile_size | INT | yes | Width and height of one tile in pixels. | 64 to 8192, default 1024 |
| overlap | INT | yes | How many pixels neighbouring tiles share. Must be smaller than the tile size. | 0 to 2048, default 64 |
| batch_mode | COMBO | no | first picture only keeps the old behaviour. all pictures cuts every picture of a batch, one after the other. | one of: first picture only, all pictures |

Outputs: `IMAGE`, `STRING`, `INT`, `STRING`

## How to use

1. Connect the big picture to image and set tile_size and overlap (smaller than the tile size).
2. Pick batch_mode: first picture only, or all pictures to cut every picture of a batch.
3. Process the tiles, then send tiles and tile_info to Tile Merge SY.
4. Outputs: the tiles, tile_info, the tile count and an info sentence.
