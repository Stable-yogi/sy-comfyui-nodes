# Tile Split SY (`SYTileSplit`)

Source: `nodes/sy_tiles.py`

**What it does:** Cuts one big picture into equal tiles that overlap a little. Process the tiles, then join them with Tile Merge SY.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| image | IMAGE | yes | The picture to cut. If you give a batch, only the first picture is used. | picture batch [B,H,W,3] |
| tile_size | INT | yes | Width and height of one tile in pixels. | 64 to 8192, default 1024 |
| overlap | INT | yes | How many pixels neighbouring tiles share. Must be smaller than the tile size. | 0 to 2048, default 64 |

Outputs: `IMAGE`, `STRING`
