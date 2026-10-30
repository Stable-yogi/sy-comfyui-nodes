# VRAM Estimate SY (`SYVramEstimate`)

Source: `nodes/sy_vram_estimate.py`

**What it does:** Rough estimate of the VRAM a model needs: file size times an overhead factor. Only a guide, not a measurement.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| file_size_gb | FLOAT | yes | Size of the model file in gigabytes. | 0.01 to 1000.0, step 0.1, default 6.0 |
| overhead_factor | FLOAT | yes | Extra room for work memory. 1.2 to 1.5 is common. | 1.0 to 5.0, step 0.05, default 1.3 |

Outputs: `STRING`, `FLOAT`
