# DualCLIPLoaderGGUF SY (`SYDualCLIPLoaderGGUF`)

Source: `nodes/sy_gguf_loaders.py`

**What it does:** Loads two text encoder files together. Each can be a .gguf file or a normal one. Pick the model family. A .gguf file needs the gguf Python package (the node tells you how to add it).

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| clip_name1 | COMBO | yes | The first text encoder file (.gguf or normal). | one of: |
| clip_name2 | COMBO | yes | The second text encoder file (.gguf or normal). | one of: |
| type | COMBO | yes | The model family these two encoders are used with. | one of: stable_diffusion, stable_cascade, sd3, stable_audio, mochi, ltxv, pixart, cosmos, lumina2, wan, hidream, chroma ... |

Outputs: `CLIP`
