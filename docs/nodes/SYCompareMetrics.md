# Compare Metrics SY (`SYCompareMetrics`)

Source: `nodes/sy_compare_metrics.py`

**What it does:** Compares two images of the same size. diff_score is the mean absolute difference (0 = identical, 1 = opposite). diff_image shows the difference, brightened by gain.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| image_a | IMAGE | yes | The first picture to compare, for example the original. | picture batch [B,H,W,3] |
| image_b | IMAGE | yes | The second picture to compare. It must be the same size as the first. | picture batch [B,H,W,3] |
| gain | FLOAT | yes | Makes small differences easier to see in the output. 1 = true size, 4 = four times brighter. | 0.0 to 1000.0, step 0.1, default 4.0 |

Outputs: `FLOAT`, `IMAGE`
