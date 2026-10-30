# Image Blend SY (`SYImageBlend`)

Source: `nodes/sy_image_blend.py`

**What it does:** Lays one picture over another. Pick a blend mode and how strong the top picture is. A smaller top picture is stretched to fit.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| base | IMAGE | yes | The bottom picture. The result has its size. | picture batch [B,H,W,3] |
| top | IMAGE | yes | The picture laid over the base. It is resized to the base size when needed. | picture batch [B,H,W,3] |
| mode | COMBO | yes | How the two pictures mix. Normal just shows the top picture. | one of: normal, multiply, screen, overlay, add, difference |
| opacity | FLOAT | yes | How strong the top picture is. 0 shows only the base, 1 the full mix. | 0.0 to 1.0, step 0.01, default 0.5 |

Outputs: `IMAGE`
