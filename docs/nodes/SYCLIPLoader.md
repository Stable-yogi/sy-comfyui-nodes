# CLIP Loader SY (`SYCLIPLoader`)

Source: `nodes/sy_clip_loader.py`

**What it does:** Loads a single text encoder (CLIP) file. Adds over the plain loader: a name_filter box to find the file without scrolling, a plain info text (size, format, fp8 explained), a warning when the file name and the chosen family do not fit (for example a umt5 file with a non-Wan family), and a plain message for an empty file.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| clip_name | COMBO | yes | The text encoder file to load. | one of: |
| type | COMBO | yes | The model family this text encoder is used with. | one of: stable_diffusion, stable_cascade, sd3, stable_audio, mochi, ltxv, pixart, cosmos, lumina2, wan, hidream, chroma ... |
| device | COMBO | yes | default uses the GPU as usual. cpu keeps the encoder on the CPU. | one of: default, cpu |
| name_filter | STRING | no | Optional. Words like 'umt5 fp8': loads the first matching file and ignores the list. | default '' |

Outputs: `CLIP`, `STRING`
