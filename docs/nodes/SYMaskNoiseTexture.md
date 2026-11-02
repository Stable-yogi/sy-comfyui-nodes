# Mask Noise Texture SY (`SYMaskNoiseTexture`)

Source: `nodes/sy_mask_noise_texture.py`

**What it does:** Draws a cloudy mask from seeded noise, for dirt, mist or random cut-outs. The same seed always gives the same mask. Leave threshold at -1 for soft clouds, or set a level to cut them into hard black and white shapes.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| width | INT | yes | Width of the mask in pixels. | 8 to 8192, step 1, default 1024 |
| height | INT | yes | Height of the mask in pixels. | 8 to 8192, step 1, default 1024 |
| scale | FLOAT | yes | Size of the biggest clouds in pixels. | 2.0 to 512.0, step 1.0, default 64.0 |
| octaves | INT | yes | How many layers of finer detail are added on top of the big clouds. | 1 to 6, step 1, default 3 |
| contrast | FLOAT | yes | Higher gives darker darks and brighter brights. Lower gives a flat grey haze. | 0.1 to 8.0, step 0.1, default 1.5 |
| seed | INT | yes | Same seed gives the same clouds. Change it for a new pattern. | 0 to 9007199254740992, step 1, default 0 |
| threshold | FLOAT | yes | -1 keeps soft clouds. Any other level cuts them into hard black and white shapes. | -1.0 to 1.0, step 0.01, default -1.0 |

Outputs: `MASK`

## How to use

1. Set **width** and **height** to the size you need.
2. Set **scale** to the size of the clouds and **octaves** for finer detail on top.
3. Adjust **contrast** until the clouds look right.
4. Change **seed** for a different pattern; the same seed repeats the same mask.
5. Leave **threshold** at -1 for soft clouds, or pick a level for hard cut-outs. The output **MASK** is one picture [1,H,W].
