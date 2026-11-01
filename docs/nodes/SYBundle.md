# Bundle SY (`SYBundle`)

Source: `nodes/sy_bundle.py`

**What it does:** Packs model, clip, vae, prompts, latent, picture, mask, seed and sampler settings into one wire (a bundle). Plug in only what you have; an unplugged input is simply left out. Give it an earlier bundle and the new inputs are added to it or replace the same item. Open the bundle again with Unbundle SY.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| bundle | SY_BUNDLE | no | An earlier bundle to add to. Inputs below replace items with the same name. |  |
| model | MODEL | no | The model (checkpoint) to carry. |  |
| clip | CLIP | no | The text encoder (clip) to carry. |  |
| vae | VAE | no | The vae to carry. |  |
| positive | CONDITIONING | no | The positive prompt (conditioning). |  |
| negative | CONDITIONING | no | The negative prompt (conditioning). |  |
| latent | LATENT | no | A latent to carry. |  |
| image | IMAGE | no | A picture to carry. | picture batch [B,H,W,3] |
| mask | MASK | no | A mask to carry. | mask [B,H,W] |
| seed | INT | no | The seed number. Connect a wire to include it. |  |
| steps | INT | no | The number of steps. Connect a wire to include it. |  |
| cfg | FLOAT | no | The cfg (prompt strength). Connect a wire to include it. |  |
| denoise | FLOAT | no | The denoise amount. Connect a wire to include it. |  |
| width | INT | no | The picture width. Connect a wire to include it. |  |
| height | INT | no | The picture height. Connect a wire to include it. |  |
| sampler_name | STRING | no | The sampler name as text. Connect a wire to include it. | default '' |
| scheduler | STRING | no | The scheduler name as text. Connect a wire to include it. | default '' |
| text | STRING | no | A free text, for example the prompt. Connect a wire to include it. | default '' |
| text2 | STRING | no | A second free text. Connect a wire to include it. | default '' |
| extra_name | STRING | no | A name for the extra item below. Empty means the name 'extra'. | default '' |
| extra | * | no | One free item of any kind, stored under extra_name. |  |

Outputs: `SY_BUNDLE`, `STRING`

## How to use

1. Plug in only what you have: model, clip, vae, prompts, latent, picture, mask, seed, steps and so on. An unplugged input is left out.
2. Seed, steps, cfg, denoise, width, height and the text fields are included only when a wire is connected to them.
3. To add to an earlier bundle, connect it to bundle. Same-named items are replaced.
4. The bundle comes out as one wire, and keys lists what is inside. Open it again with Unbundle SY.
