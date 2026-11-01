# Compare Metrics SY (`SYCompareMetrics`)

Source: `nodes/sy_compare_metrics.py`

**What it does:** Compares two images of the same size. diff_score is the mean absolute difference (0 = identical, 1 = opposite). diff_image shows the difference, brightened by gain. Can compare only inside a mask, can resize image_b to fit, and also gives the biggest difference, a PSNR score and a plain verdict.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| image_a | IMAGE | yes | The first picture to compare, for example the original. | picture batch [B,H,W,3] |
| image_b | IMAGE | yes | The second picture to compare. It must be the same size as the first. | picture batch [B,H,W,3] |
| gain | FLOAT | yes | Makes small differences easier to see in the output. 1 = true size, 4 = four times brighter. | 0.0 to 1000.0, step 0.1, default 4.0 |
| mask | MASK | no | Optional. Compare only where the mask is white. A different size is stretched to fit. | mask [B,H,W] |
| resize_b | BOOLEAN | no | On: resize image_b to image_a's size first. Off: stop with a message when the sizes differ. | default False |

Outputs: `FLOAT`, `IMAGE`, `FLOAT`, `FLOAT`, `STRING`
