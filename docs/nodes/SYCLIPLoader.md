# CLIP Loader SY (`SYCLIPLoader`)

Source: `nodes/sy_clip_loader.py`

**What it does:** Loads a single text encoder (CLIP) file. Pick the model family it belongs to.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| clip_name | COMBO | yes | The text encoder file to load. | one of: |
| type | COMBO | yes | The model family this text encoder is used with. | one of: stable_diffusion, stable_cascade, sd3, stable_audio, mochi, ltxv, pixart, cosmos, lumina2, wan, hidream, chroma ... |
| device | COMBO | yes | default uses the GPU as usual. cpu keeps the encoder on the CPU. | one of: default, cpu |

Outputs: `CLIP`
