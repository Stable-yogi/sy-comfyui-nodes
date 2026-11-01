# Megapixel Scale SY (`SYMegapixelScale`)

Source: `nodes/sy_megapixel_scale.py`

**What it does:** Works out a new width and height that add up to a target number of megapixels. The shape (aspect) stays the same. Both sides are rounded to a multiple. Turn on no_upscale so small pictures are not blown up, and read the info line for the result.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| width | INT | yes | Current width in pixels. Only its shape against the height matters. | 1 to 65536, default 1024 |
| height | INT | yes | Current height in pixels. | 1 to 65536, default 1024 |
| megapixels | FLOAT | yes | Target size in millions of pixels. 1.0 is about 1024 by 1024. | 0.01 to 4096.0, step 0.05, default 1.0 |
| multiple | INT | yes | Width and height are rounded to a multiple of this. 16 suits most models. | 1 to 256, default 16 |
| no_upscale | BOOLEAN | no | On never gives more pixels than the picture has now. Small pictures are not blown up. | default False |

Outputs: `INT`, `INT`, `STRING`
