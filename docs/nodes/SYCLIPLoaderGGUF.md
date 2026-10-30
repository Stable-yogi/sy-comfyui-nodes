# CLIPLoaderGGUF SY (`SYCLIPLoaderGGUF`)

Source: `nodes/sy_gguf_loaders.py`

**What it does:** Loads one text encoder (CLIP) file. It can be a .gguf file or a normal one. Pick the model family. A .gguf file needs the gguf Python package (the node tells you how to add it).

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| clip_name | COMBO | yes | The text encoder file to load (.gguf or normal). | one of: |
| type | COMBO | yes | The model family this text encoder is used with. | one of: stable_diffusion, stable_cascade, sd3, stable_audio, mochi, ltxv, pixart, cosmos, lumina2, wan, hidream, chroma ... |

Outputs: `CLIP`
