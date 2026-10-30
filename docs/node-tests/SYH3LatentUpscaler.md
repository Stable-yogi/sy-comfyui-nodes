# H3LatentUpscaler SY (`SYH3LatentUpscaler`)

Source: `nodes/sy_h3_latent_upscaler.py`

**What it does:** Makes a Minimax H3 video latent bigger with a trained 3D network, without decoding it first. Needs a model file in models/latent_upscale_models. Saves time, not VRAM. Feed it the VIDEO latent only (split the sound latent off first).

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| latent | LATENT | yes | The video latent (24 channels). Not the joined video+sound latent. |  |
| model_name | COMBO | yes | Upscaler file from models/latent_upscale_models. | one of: (none: put a model file in models/latent_upscale_models) |
| mode | COMBO | yes | How the new size is chosen. Only the matching number is used. | one of: scale by multiplier, target dimensions, megapixels |
| scale | FLOAT | yes | Used by 'scale by multiplier'. | 1.0 to 4.0, step 0.05, default 2.0 |
| width | INT | yes | Used by 'target dimensions': new width in pixels. | 64 to 8192, step 8, default 1280 |
| height | INT | yes | Used by 'target dimensions': new height in pixels. | 64 to 8192, step 8, default 704 |
| megapixels | FLOAT | yes | Used by 'megapixels': new picture size, aspect kept. | 0.1 to 16.0, step 0.1, default 1.0 |
| align | INT | yes | Round the pixel size to this grid. 32 is best. | 1 to 512, step 1, default 32 |
| enable_temporal_chunking | BOOLEAN | yes | Work on 32 frames at a time. Saves memory on long clips. | default True |
| force_unload | BOOLEAN | yes | Move the model to the CPU when done, to free VRAM for the next node. | default True |
| device | COMBO | yes | cuda is the normal choice for an NVIDIA card. | one of: cuda, rocm, cpu |
| precision | COMBO | yes | fp16 matches the model file. | one of: fp16, bf16, fp32 |

Outputs: `LATENT`

## How it was tested

This node was not run by the harness. Reason: Size planning, chunk ranges, blend weights and model-type detection have script tests. A torch run on the real upscaler model file gave the same output as the original node (checked side by side). A full H3 workflow run on a clean ComfyUI (864x480 up to 1280x704) succeeded. Not run here: it needs the 690 MB model file and a real H3 latent.


## Verdict

Not run. Size planning, chunk ranges, blend weights and model-type detection have script tests. A torch run on the real upscaler model file gave the same output as the original node (checked side by side). A full H3 workflow run on a clean ComfyUI (864x480 up to 1280x704) succeeded. Not run here: it needs the 690 MB model file and a real H3 latent.
