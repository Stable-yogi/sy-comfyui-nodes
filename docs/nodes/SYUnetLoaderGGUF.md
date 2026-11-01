# UnetLoaderGGUF SY (`SYUnetLoaderGGUF`)

Source: `nodes/sy_gguf_loaders.py`

**What it does:** Loads a GGUF diffusion model (unet). Smaller than the full file and LoRA files still work on it. Adds a name_filter box (type part of a name instead of scrolling), a plain info text (size and what the Q4/Q8 part of the name means), a warning for a text encoder picked by mistake, and a plain message for an empty file. Needs the gguf Python package (the node tells you how to add it).

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| unet_name | COMBO | yes | The .gguf diffusion model file to load. | one of: |
| name_filter | STRING | no | Optional. Words like 'flux Q4': loads the first matching .gguf and ignores the list. | default '' |

Outputs: `MODEL`, `STRING`

## How to use

1. Pick the .gguf file in unet_name, or type part of a name such as "flux Q4" in name_filter. A filled name_filter loads the first matching file and ignores the list.
2. Connect model to your sampler. LoRA files still work on it.
3. The info output describes what was loaded.
