# Tile Merge SY (`SYTileMerge`)

Source: `nodes/sy_tiles.py`

**What it does:** Joins tiles from Tile Split SY back into one picture. Works after an upscale of a whole-number factor. Tiles from a batch cut with batch_mode all pictures give a batch back. The info output says the new size and the enlarge factor.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| tiles | IMAGE | yes | The processed tiles, in the same count and order as Tile Split SY gave them. | picture batch [B,H,W,3] |
| tile_info | STRING | yes | The tile_info text from Tile Split SY. | default '' |
| blend | COMBO | yes | linear fades the shared edges softly. none lets later tiles cover earlier ones. | one of: linear, none |

Outputs: `IMAGE`, `STRING`

## How to use

1. Connect the processed tiles to tiles, in the same count and order as Tile Split SY gave them.
2. Connect tile_info from Tile Split SY.
3. Pick blend: linear fades shared edges softly, none lets later tiles cover earlier ones.
4. It works after an upscale by a whole-number factor. A batch cut with all pictures gives a batch back.
