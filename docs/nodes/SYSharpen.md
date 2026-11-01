# Sharpen SY (`SYSharpen`)

Source: `nodes/sy_sharpen.py`

**What it does:** Makes a picture crisper with an unsharp mask. Radius sets how wide the edges are, amount sets how strong, and the optional threshold keeps smooth areas and noise from being sharpened. The info output says what was done.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| image | IMAGE | yes | The picture or batch of pictures to sharpen. | picture batch [B,H,W,3] |
| radius | FLOAT | yes | Width of the edges to sharpen, in pixels. Small is fine detail. | 0.1 to 32.0, step 0.1, default 1.0 |
| amount | FLOAT | yes | How strong the sharpening is. 0 changes nothing, above 2 is harsh. | 0.0 to 5.0, step 0.05, default 1.0 |
| threshold | FLOAT | no | Ignore brightness changes smaller than this, so noise is not sharpened. 0 sharpens everything; try 0.02. | 0.0 to 1.0, step 0.005, default 0.0 |

Outputs: `IMAGE`, `STRING`

## How to use

1. Connect a picture or a batch to image.
2. Set radius (width of the edges to sharpen, small for fine detail) and amount (strength, above 2 is harsh).
3. Optional: set threshold, for example 0.02, so smooth areas and noise are not sharpened.
4. The sharpened picture comes out on image with an info line.
