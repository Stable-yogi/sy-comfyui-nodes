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

## How to use

1. Pick the text encoder file in clip_name, or type words such as umt5 fp8 in name_filter. A filter match is loaded and the list is ignored.
2. Set type to the model family it is used with.
3. Set device: default uses the GPU, cpu keeps the encoder on the CPU.
4. The loaded clip comes out with an info text (size, format) and a warning if the file name and family do not fit.
