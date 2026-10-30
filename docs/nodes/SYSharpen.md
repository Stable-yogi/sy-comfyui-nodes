# Sharpen SY (`SYSharpen`)

Source: `nodes/sy_sharpen.py`

**What it does:** Makes a picture crisper with an unsharp mask. Radius sets how wide the edges are, amount sets how strong.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| image | IMAGE | yes | The picture or batch of pictures to sharpen. | picture batch [B,H,W,3] |
| radius | FLOAT | yes | Width of the edges to sharpen, in pixels. Small is fine detail. | 0.1 to 32.0, step 0.1, default 1.0 |
| amount | FLOAT | yes | How strong the sharpening is. 0 changes nothing, above 2 is harsh. | 0.0 to 5.0, step 0.05, default 1.0 |

Outputs: `IMAGE`
