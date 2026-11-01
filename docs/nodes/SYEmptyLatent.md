# Empty Latent SY (`SYEmptyLatent`)

Source: `nodes/sy_empty_latent.py`

**What it does:** Makes a blank latent to start a render from. 'standard 4ch /8' has 4 channels (SD 1.5, SDXL). 'flux 16ch /8' has 16 channels (Flux, SD3 style). Both are 8 times smaller than the picture. Adds a snap_to option (round the size to 8, 16, 32 or 64 instead of silently cutting it), the real picture width and height as outputs, and an info text with warnings for sizes that are odd or very large.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| width | INT | yes | Picture width in pixels. | 8 to 16384, step 8, default 1024 |
| height | INT | yes | Picture height in pixels. | 8 to 16384, step 8, default 1024 |
| batch | INT | yes | How many blank latents to make at once. | 1 to 4096, default 1 |
| latent_type | COMBO | yes | 4 channels for SD 1.5 and SDXL. 16 channels for Flux style models. | one of: standard 4ch /8, flux 16ch /8 |
| snap_to | COMBO | no | off cuts the size to a multiple of 8. 16, 32 or 64 round it to that multiple. | one of: off, 8, 16, 32, 64 |
| snap_direction | COMBO | no | How snap_to rounds: to the nearest multiple, always down, or always up. | one of: nearest, down, up |

Outputs: `LATENT`, `INT`, `INT`, `STRING`

## How to use

1. Set width, height and batch.
2. Pick latent_type: standard 4ch /8 (SD 1.5, SDXL) or flux 16ch /8 (Flux, SD3 style).
3. Use snap_to (8, 16, 32 or 64) and snap_direction to round the size instead of silently cutting it.
4. Outputs: latent, the real width and height, and info with warnings for odd or very large sizes.
