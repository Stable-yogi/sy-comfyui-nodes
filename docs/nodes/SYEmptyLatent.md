# Empty Latent SY (`SYEmptyLatent`)

Source: `nodes/sy_empty_latent.py`

**What it does:** Makes a blank latent to start a render from. 'standard 4ch /8' has 4 channels (SD 1.5, SDXL). 'flux 16ch /8' has 16 channels (Flux, SD3 style). Both are 8 times smaller than the picture.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| width | INT | yes | Picture width in pixels. | 8 to 16384, step 8, default 1024 |
| height | INT | yes | Picture height in pixels. | 8 to 16384, step 8, default 1024 |
| batch | INT | yes | How many blank latents to make at once. | 1 to 4096, default 1 |
| latent_type | COMBO | yes | 4 channels for SD 1.5 and SDXL. 16 channels for Flux style models. | one of: standard 4ch /8, flux 16ch /8 |

Outputs: `LATENT`
