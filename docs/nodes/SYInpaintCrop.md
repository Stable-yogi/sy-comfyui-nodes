# InpaintCrop SY (`SYInpaintCrop`)

Source: `nodes/sy_inpaint_crop_stitch.py`

**What it does:** Cuts a box around the painted part and scales it up, so the model draws a small hand or face at full size. Send 'stitch' to Inpaint Stitch to put the result back.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| image | IMAGE | yes | Your whole picture. | picture batch [B,H,W,3] |
| mask | MASK | yes | The painted part (already grown and softened is best). | mask [B,H,W] |
| context | FLOAT | yes | Room around the painted part, as a factor of its size. More room matches the scene better. | 1.0 to 4.0, step 0.05, default 1.5 |
| size | INT | yes | Long side of the crop the model draws, in pixels. 1024 suits Krea 2. | 256 to 2048, step 16, default 1024 |
| min_box | INT | yes | Smallest crop box on the original picture, so a tiny mark still gets some scene around it. | 64 to 2048, step 16, default 256 |

Outputs: `SY_STITCH`, `IMAGE`, `MASK`
