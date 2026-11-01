# Model Preset Bundle SY (`SYModelPresetBundle`)

Source: `nodes/sy_model_preset_bundle.py`

**What it does:** Pick a model family and get its usual steps, cfg, sampler, scheduler, size and a short note. These are starting points. Adds an aspect choice (the preset's pixel budget in another shape, such as 16:9 or 9:16, snapped to a size the model likes) and a one-line info text.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| preset | COMBO | yes | The model family whose usual settings you want. | one of: Krea 2, Qwen Image 2.1, Flux, SDXL (old), Z-Image, Wan 2.2 video, LTX video, H3, MiniMax image, MiniMax video, HunyuanVideo, Qwen edit ... |
| aspect | COMBO | no | preset = the preset's own size. Or a shape like 16:9: same pixel budget, new shape. | one of: preset, 1:1, 5:4, 4:3, 3:2, 16:9, 21:9, 4:5, 3:4, 2:3, 9:16 |

Outputs: `INT`, `FLOAT`, `STRING`, `STRING`, `INT`, `INT`, `STRING`, `FLOAT`, `STRING`

## How to use

1. Pick a preset in preset. These are starting points.
2. Optional: set aspect to a shape such as 16:9 or 9:16. The preset's pixel budget is kept and the size is snapped to one the model likes. preset keeps the preset's own size.
3. Connect the outputs to your sampler: steps, cfg, sampler_name, scheduler, width, height.
note, megapixels and info give extra text and numbers.
