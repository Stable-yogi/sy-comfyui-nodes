# Remove Background SY (`SYRemoveBackground`)

Source: `nodes/sy_remove_background.py`

**What it does:** Cuts the subject out of its background in one step. Pick a background-removal model file, and you get the picture with a see-through or coloured background, the cut-out mask (1 = subject) and a flat-colour cut-out. Threshold, grow and feather clean up the edge. Works on whole batches.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| image | IMAGE | yes | The picture (or batch) to cut the subject out of. | picture batch [B,H,W,3] |
| model | COMBO | yes | Background removal model file from models/background_removal. | one of: (no model installed: use Model Downloader SY) |
| threshold | FLOAT | yes | 0 keeps the soft edge. Above 0 makes a hard cut at that level. | 0.0 to 1.0, step 0.01, default 0.0 |
| feather | INT | yes | Soft edge in pixels. 0 = off. | 0 to 64, default 0 |
| grow | INT | yes | Pixels to widen the subject. Negative numbers shrink it. | -64 to 64, default 0 |
| background | COMBO | yes | What goes behind the subject in the image output. | one of: transparent, white, black, grey, green screen |

Outputs: `IMAGE`, `MASK`, `IMAGE`

## How to use

1. Connect your picture (or batch) to image and pick a model file in model. If none is listed, get one with Model Downloader SY.
2. Choose background: transparent, white, black, grey or green screen.
3. Clean the edge with threshold (0 keeps the soft edge), feather and grow.
Outputs: the picture with the new background, the cut-out mask (1 = subject) and a flat-colour cut-out.
