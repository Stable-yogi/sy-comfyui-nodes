# VRAM Estimate SY (`SYVramEstimate`)

Source: `nodes/sy_vram_estimate.py`

**What it does:** Rough estimate of the VRAM a model needs: file size times an overhead factor. Only a guide, not a measurement. Add the size of other models loaded together and your card memory to get a plain fits or does not fit answer with tips.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| file_size_gb | FLOAT | yes | Size of the model file in gigabytes. | 0.01 to 1000.0, step 0.1, default 6.0 |
| overhead_factor | FLOAT | yes | Extra room for work memory. 1.2 to 1.5 is common. | 1.0 to 5.0, step 0.05, default 1.3 |
| extra_models_gb | FLOAT | no | Size of other models in memory at the same time, such as the text encoder and VAE. For example 9. | 0.0 to 1000.0, step 0.1, default 0.0 |
| card_vram_gb | FLOAT | no | Your graphics card memory in GB, for example 24. 0 turns the fit check off. | 0.0 to 1000.0, step 1.0, default 0.0 |

Outputs: `STRING`, `FLOAT`, `BOOLEAN`, `STRING`
