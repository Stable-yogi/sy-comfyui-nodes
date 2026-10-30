# Film Grain SY (`SYFilmGrain`)

Source: `nodes/sy_film_grain.py`

**What it does:** Adds film grain. The same seed always gives the same grain. Choose grey or colour grain and how coarse it is.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| image | IMAGE | yes | The picture or batch of pictures to add grain to. | picture batch [B,H,W,3] |
| strength | FLOAT | yes | How visible the grain is. 0 changes nothing. | 0.0 to 1.0, step 0.01, default 0.1 |
| size | INT | yes | Grain size in pixels. 1 is fine grain, bigger is coarse. | 1 to 32, default 1 |
| seed | INT | yes | Number that fixes the grain pattern. Change it for a new pattern. | 0 to 4294967295, default 0 |
| color_grain | BOOLEAN | yes | On gives coloured grain, off gives grey grain. | default False |

Outputs: `IMAGE`
