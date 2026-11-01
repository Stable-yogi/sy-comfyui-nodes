# DualCLIPLoaderGGUF SY (`SYDualCLIPLoaderGGUF`)

Source: `nodes/sy_gguf_loaders.py`

**What it does:** Loads two text encoder files together. Each can be a .gguf file or a normal one. Pick the model family. Adds two name_filter boxes, a plain info text, and a warning when both slots hold the same file or a file name does not fit the family. A .gguf file needs the gguf Python package (the node tells you how to add it).

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| clip_name1 | COMBO | yes | The first text encoder file (.gguf or normal). | one of: |
| clip_name2 | COMBO | yes | The second text encoder file (.gguf or normal). | one of: |
| type | COMBO | yes | The model family these two encoders are used with. | one of: stable_diffusion, stable_cascade, sd3, stable_audio, mochi, ltxv, pixart, cosmos, lumina2, wan, hidream, chroma ... |
| name_filter1 | STRING | no | Optional. Words for the first file, like 'clip_l'. Ignores the first list. | default '' |
| name_filter2 | STRING | no | Optional. Words for the second file, like 't5xxl Q8'. Ignores the second list. | default '' |

Outputs: `CLIP`, `STRING`

## How to use

1. Pick two files in clip_name1 and clip_name2 (each .gguf or normal), or use name_filter1 and name_filter2.
2. Set type to the model family.
3. A .gguf file needs the gguf Python package. The node tells you how to add it.
4. The model comes out with an info text and a warning if both slots hold the same file or a name does not fit the family.
