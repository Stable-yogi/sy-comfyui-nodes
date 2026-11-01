# InpaintStitch SY (`SYInpaintStitch`)

Source: `nodes/sy_inpaint_crop_stitch.py`

**What it does:** Scales the new crop back down and blends it into your picture through the soft mask. Every pixel outside the mask stays your own.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| stitch | SY_STITCH | yes | The 'stitch' output of Inpaint Crop. |  |
| inpainted | IMAGE | yes | The decoded crop from the sampler. | picture batch [B,H,W,3] |

Outputs: `IMAGE`

## How to use

1. Connect the stitch output of Inpaint Crop to stitch.
2. Connect the decoded crop from the sampler to inpainted.
3. The crop is scaled back down and blended into your picture through the soft mask. Every pixel outside the mask stays your own.
