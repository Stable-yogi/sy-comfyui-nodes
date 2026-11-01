# Decode SY (`SYDecode`)

Source: `nodes/sy_decode.py`

**What it does:** Turns a latent into a picture, video frames or sound. If the graphics card runs out of memory it retries by itself in smaller and smaller tiles instead of stopping, and tells you what it used.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| samples | LATENT | yes | The latent to turn into a picture, video or sound. |  |
| vae | VAE | yes | The VAE that matches the model (for sound: the audio VAE). |  |
| mode | COMBO | yes | Picture or video frames come out on image. Sound comes out on audio. | one of: Picture or video, Sound |
| tiles | COMBO | yes | Auto: one piece first, tiles if memory runs out. Always: tiles from the start. Never: one piece only. | one of: Auto (retry in tiles), Always tiles, Never tiles |
| tile_size | INT | yes | First tile size in pixels. Each retry halves it. | 64 to 4096, step 32, default 512 |
| overlap | INT | yes | How much neighbouring tiles share, so no seams show. | 0 to 1024, step 8, default 64 |

Outputs: `IMAGE`, `AUDIO`, `STRING`

## How to use

1. Connect the latent to samples and the vae to vae.
2. Set mode: Picture or video, or Sound.
3. tiles: Auto retries in smaller tiles if the graphics card runs out of memory. Always tiles and Never tiles force it. Set tile_size and overlap.
4. Outputs: image, audio and info, which says what was used.
