# UnetLoaderGGUF SY (`SYUnetLoaderGGUF`)

Source: `nodes/sy_gguf_loaders.py`

**What it does:** Loads a GGUF diffusion model (unet). Smaller than the full file and LoRA files still work on it. Needs the gguf Python package (the node tells you how to add it).

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| unet_name | COMBO | yes | The .gguf diffusion model file to load. | one of: |

Outputs: `MODEL`
