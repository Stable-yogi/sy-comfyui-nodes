# InpaintStitch SY (`SYInpaintStitch`)

Source: `nodes/sy_inpaint_crop_stitch.py`

**What it does:** Scales the new crop back down and blends it into your picture through the soft mask. Every pixel outside the mask stays your own.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| stitch | SY_STITCH | yes | The 'stitch' output of Inpaint Crop. |  |
| inpainted | IMAGE | yes | The decoded crop from the sampler. | picture batch [B,H,W,3] |

Outputs: `IMAGE`

## How it was tested

This node was not run by the harness. Reason: needs real model, covered by loader test (inputs: stitch (SY_STITCH)).


## Verdict

Not run. needs real model, covered by loader test (inputs: stitch (SY_STITCH)).
