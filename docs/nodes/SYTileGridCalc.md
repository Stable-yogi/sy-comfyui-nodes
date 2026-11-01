# Tile Grid Calc SY (`SYTileGridCalc`)

Source: `nodes/sy_tile_grid_calc.py`

**What it does:** Counts the tiles needed to cover a picture for a tile size and overlap. Gives columns, rows, the total and a text line, plus the step between tiles, the top left corner of every tile, and plain warnings (tiny overlap, tile size not a multiple of 8, too many tiles). Can stop the run if there would be too many tiles.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| width | INT | yes | Picture width in pixels. | 1 to 1000000, default 2048 |
| height | INT | yes | Picture height in pixels. | 1 to 1000000, default 2048 |
| tile_size | INT | yes | Width and height of one square tile in pixels. | 1 to 1000000, default 1024 |
| overlap | INT | yes | Pixels shared by neighbour tiles. Must be less than the tile size. | 0 to 1000000, default 64 |
| max_tiles | INT | no | Stop with a message if more tiles than this are needed, for example 16. 0 turns the limit off. | 0 to 100000, default 0 |

Outputs: `INT`, `INT`, `INT`, `STRING`, `INT`, `STRING`, `STRING`
