# Tile Merge SY (`SYTileMerge`)

Source: `nodes/sy_tiles.py`

**What it does:** Joins tiles from Tile Split SY back into one picture. Works after an upscale of a whole-number factor.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| tiles | IMAGE | yes | The processed tiles, in the same count and order as Tile Split SY gave them. | picture batch [B,H,W,3] |
| tile_info | STRING | yes | The tile_info text from Tile Split SY. | default '' |
| blend | COMBO | yes | linear fades the shared edges softly. none lets later tiles cover earlier ones. | one of: linear, none |

Outputs: `IMAGE`
