# Model Preset Bundle SY (`SYModelPresetBundle`)

Source: `nodes/sy_model_preset_bundle.py`

**What it does:** Pick a model family and get its usual steps, cfg, sampler, scheduler, size and a short note. These are starting points.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| preset | COMBO | yes | The model family whose usual settings you want. | one of: Krea 2, Qwen Image 2.1, Flux, SDXL (old), Z-Image, Wan 2.2 video, LTX video, H3, MiniMax image, MiniMax video, HunyuanVideo, Qwen edit ... |

Outputs: `INT`, `FLOAT`, `STRING`, `STRING`, `INT`, `INT`, `STRING`
