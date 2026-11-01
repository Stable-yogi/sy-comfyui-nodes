# Batch Info SY (`SYBatchInfo`)

Source: `nodes/sy_batch_info.py`

**What it does:** Reports the number of pictures in a batch and their width, height and channels. The pictures pass through unchanged. Also gives megapixels, landscape/portrait and a plain warning when the size is not a multiple of 8 or is very large.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| images | IMAGE | yes | The batch to measure. It is passed on unchanged. | picture batch [B,H,W,3] |

Outputs: `IMAGE`, `INT`, `INT`, `INT`, `INT`, `STRING`, `FLOAT`, `STRING`, `STRING`

## How to use

1. Connect a batch of pictures to images.
2. They pass through unchanged on the images output.
3. Read the count, width, height and channels, plus megapixels and orientation.
4. The warnings output tells you when the size is not a multiple of 8 or is very large.
